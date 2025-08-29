
# ARCH.md — ProdSprint AI
## System Architecture (Multi‑tenant, Event‑Driven, Policy‑Gated)

### Overview
ProdSprint AI is a **multi‑tenant release orchestrator** that analyzes a repo, proposes a **plan** (IaC + CI/CD + policies + cost), provisions **staging**, runs **readiness gates** (tests, security, performance), and executes **safe releases** (blue/green/canary) with **automatic rollback**. It emits **dashboards**, **SLOs**, and a complete **audit trail**.

### Diagram
```
Next.js 14 (Mantine) ── REST/SSE ─► FastAPI /v1 (OIDC, RBAC, RLS, Problem+JSON)
                                     │
                                     ├─► NATS (events) / Redis Streams (DLQ)
                                     │
                                     └─► Workers (Python 3.11, CrewAI+LangGraph-friendly):
                                          • repo_auditor       • iac_agent         • cicd_agent
                                          • test_agent         • security_agent    • perf_agent
                                          • release_orchestrator• rollback_agent   • observability_agent
                                          • cost_optimizer
Data Plane:
  • Postgres 16 + pgvector — orgs, workspaces, projects, runs, blueprints, artifacts, releases, alerts, audit, policies, integrations
  • S3/R2 — artifacts (iac/cicd/tests/sbom/perf/obs), logs, exports
  • Redis — cache, rate limits, DLQ replay cursors
Observability:
  • OpenTelemetry → Prometheus/Grafana; Sentry for errors; Logfmt/JSON logs
Security:
  • KMS per org/workspace; Sigstore (cosign); SLSA provenance; OPA/Conftest gates; CSP/TLS/HSTS
Providers:
  • Vercel/Render (MVP) → Kubernetes targets (GKE/EKS) + Argo Rollouts (Premium)
```

### Orchestration Model
- **DAG** of stages with **idempotency keys** per `(project_id, stage, attempt)`; retries with exponential backoff & jitter.
- **Events**: `project.imported`, `plan.ready`, `iac.applied`, `cicd.emitted`, `tests.generated`, `security.passed`, `perf.baselined`, `readiness.ready`, `release.progress`, `release.rolledback`, `error.*`.
- **State**: table `runs` captures status, stage, logs_ref, metrics, policy_result; SSE at `/v1/runs/{id}/stream`.

### Data Model (DDL excerpt)
```sql
CREATE TYPE run_kind AS ENUM ('import','blueprint','apply','readiness','release','rollback');
CREATE TYPE run_status AS ENUM ('pending','running','done','error');

CREATE TABLE orgs(id UUID PRIMARY KEY, name TEXT, plan TEXT, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE users(id UUID PRIMARY KEY, org_id UUID REFERENCES orgs(id), email CITEXT UNIQUE, name TEXT, role TEXT, tz TEXT, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE workspaces(id UUID PRIMARY KEY, org_id UUID REFERENCES orgs(id), name TEXT, created_by UUID REFERENCES users(id), created_at TIMESTAMPTZ DEFAULT now());

CREATE TABLE projects(
  id UUID PRIMARY KEY, workspace_id UUID REFERENCES workspaces(id),
  repo_url TEXT NOT NULL, branch TEXT DEFAULT 'main', target TEXT, region TEXT,
  state TEXT, created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE integrations(project_id UUID REFERENCES projects(id), type TEXT, creds_ref TEXT, scopes TEXT[], PRIMARY KEY(project_id, type));

CREATE TABLE runs(
  id UUID PRIMARY KEY, project_id UUID REFERENCES projects(id),
  kind run_kind, status run_status DEFAULT 'pending', stage TEXT, attempt INT DEFAULT 0,
  logs_ref TEXT, metrics JSONB, policy_result JSONB, created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE blueprints(project_id UUID PRIMARY KEY REFERENCES projects(id),
  iac_ref TEXT, cicd_ref TEXT, policies JSONB, cost_estimate JSONB, plan_diff JSONB);

CREATE TYPE artifact_type AS ENUM ('iac','cicd','tests','sbom','perf','observability','release','runbook');
CREATE TABLE artifacts(id UUID PRIMARY KEY, project_id UUID REFERENCES projects(id),
  run_id UUID REFERENCES runs(id), t artifact_type, path TEXT, meta JSONB, created_at TIMESTAMPTZ DEFAULT now());

CREATE TABLE releases(id UUID PRIMARY KEY, project_id UUID REFERENCES projects(id),
  sha TEXT, env TEXT, strategy TEXT, status TEXT, risk_score NUMERIC, created_at TIMESTAMPTZ DEFAULT now(), updated_at TIMESTAMPTZ DEFAULT now());

CREATE TABLE alerts(id UUID PRIMARY KEY, project_id UUID REFERENCES projects(id), type TEXT, severity TEXT, action TEXT, meta JSONB, created_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE audit_log(id BIGSERIAL PRIMARY KEY, org_id UUID, user_id UUID, action TEXT, target TEXT, meta JSONB, created_at TIMESTAMPTZ DEFAULT now());
```

### API Surface (REST /v1)
- `POST /projects/import` — analyze repo → run_id
- `POST /blueprints/generate` — return IaC/CI refs + policies + cost
- `GET  /blueprints/{project_id}` — read latest plan
- `POST /pipelines/apply` — provision infra + emit CI PRs
- `GET  /readiness/{project_id}` — checklist & blockers
- `POST /releases/create` — start rollout (strategy, percent)
- `POST /releases/rollback` — revert release
- `GET  /dashboards/{project_id}` — SLOs, coverage, perf, cost
- `GET  /runs/{id}/stream` — SSE progress

### Pipeline Stages (deterministic order + parallel windows)
1. **Audit**: detect stack/services/ports/tests/env/migrations.
2. **Plan**: render Terraform/Helm; generate CI templates; compute cost; draft policies.
3. **Apply**: create VPC/DB/Redis/S3/DNS/TLS/CDN/secrets; commit artifacts.
4. **Readiness** (parallelizable): Test → Security → Perf; gates must pass or be waived.
5. **Release**: blue/green or canary; health gates; promote or rollback.
6. **Observe**: OTel exporters, dashboards, alerts; baselines and cost trend set.

### Security & Compliance
- **Secrets**: KMS-backed; rotation schedules; secret drift detection; PR scanners for plaintext leaks.
- **Supply Chain**: Trivy scan, SBOM via Syft, **cosign** signed images, **SLSA** attestations, OPA/Conftest policy gates.
- **Compliance Packs** (Premium): SOC2/HIPAA defaults; evidence collection hooks; audit export endpoints.

### Performance & Scaling
- Target p95s: **repo→staging ≤ 20m**, **rollback ≤ 3m**. Parallel workers, template caches, Terraform plugin cache. Rate limiting with token buckets. Backpressure via NATS consumer groups.

### Deployment & Ops
- **Frontend**: Vercel; CSP/HSTS; ISR for dashboards.
- **Backend/Workers**: Render (MVP) or Fly.io; Premium: GKE/EKS with autoscaling pools.
- **IaC**: Terraform workspaces per env; blue/green infra applies; state in remote backend; drift job scheduled.
- **Backups/DR**: Postgres PITR; artifacts versioned in S3; restore runbooks; periodic game days.

### Advanced Feature Modules
- **Change Risk Scoring**: per-release risk using code churn, ownership, test gaps, incident history.
- **GitOps Mode**: ArgoCD/Flux reconciliation; PR-only changes; drift = red status.
- **Cost Optimizer**: rightsizing, egress/CDN tips; budget alerts with justifications.
- **RUM + eBPF Profiling**: client performance & server profiles to catch regressions.
