
# TODO.md — ProdSprint AI
## Development Roadmap & Work Items (Granular, Build-Ready)

> Goal: Ship an MVP that takes a repo from **import → plan → apply → staging → canary → prod** with **policy gates** (tests, security, perf, SBOM, coverage, cost) and **instant rollback**. Then iterate to Premium targets (Kubernetes, Argo Rollouts, risk scoring, SOC2/HIPAA packs).

### Labels & Conventions
- Labels: `area:api`, `area:frontend`, `area:workers`, `area:iac`, `area:cicd`, `area:security`, `area:perf`, `area:observability`, `area:docs`, `type:feature`, `type:bug`, `type:task`, `good-first-issue`.
- DOR (Definition of Ready): user story + acceptance criteria + mocks (if UI) + test plan + rollback plan.
- DOD (Definition of Done): unit/integration tests; CI green; docs updated; metrics & alerts added; runbook updated.

---

## Phase 1 — Foundations & Platform (Week 0–2) ✅ COMPLETED
- [x] **Monorepo & Tooling** (`area:docs`): pnpm turborepo (apps: `frontend`, `backend`, `workers`); commitlint; prettier; ruff.
  - AC: Pre-commit hooks run; CI caches configured; local dev `docker compose up` brings full stack.
- [x] **Auth & Tenancy** (`area:api`): OIDC (GitHub, Google), orgs/workspaces, memberships; RLS by `workspace_id`.
  - AC: Login → org → workspace; JWT with org/workspace claims; row-level policies enforced in tests.
- [x] **API Gateway** (`area:api`): FastAPI `/v1`; Problem+JSON; Idempotency-Key; Request-ID; rate limits.
  - AC: OpenAPI 3.1 generated; error payloads consistent; 95% handler coverage.
- [x] **Data Stores** (`area:api`): Postgres 16 + pgvector; Redis (cache/DLQ); S3/R2 (artifacts); migrations.
  - AC: Alembic migration CI job; PITR enabled; seed script for demo data.
- [x] **Eventing** (`area:workers`): NATS core subjects; Redis Streams for DLQ; retry/jitter helpers.
  - AC: Replay CLI for DLQ; consumer groups scale-out verified.
- [x] **Observability** (`area:observability`): OTel traces/logs/metrics → Prometheus/Grafana; Sentry errors.
  - AC: Spans for each stage; dashboards JSON committed; alert rule for 5xx & long runs.
- [x] **CI/CD Baseline** (`area:cicd`): GH Actions (lint/type/unit/integration, docker build, trivy scan, cosign sign).
  - AC: Build <10m; cache hits >80%; SLSA provenance attestation generated.
- [x] **Frontend Shell** (`area:frontend`): Next.js 14 + Mantine; layout, auth guard, project list page.
  - AC: Lighthouse ≥ 90 perf/a11y; SSR works; error boundaries present.

## Phase 2 — Repo Audit → Plan Preview (Week 2–3) ✅ COMPLETED
- [x] **Repo Auditor** (`area:workers`): detect services, ports, Dockerfiles, envs, migrations, tests.
  - AC: 10 sample repos fingerprinted; outputs normalized JSON; gaps list produced.
- [x] **Plan Svc** (`area:api`): produce plan (IaC + CI/CD + policies + cost) with diffs & risk notes.
  - AC: `/v1/blueprints/generate` returns `iac_ref`, `cicd_ref`, `policies`, `cost_estimate`, `plan_diff`.
- [x] **UI — Plan Preview** (`area:frontend`): show IaC/CI diffs, policy profile, cost estimate, blockers, Approve button.
  - AC: Approve disabled until blockers resolved or waived with reason.

## Phase 3 — Apply (Week 3–4) ✅ COMPLETED
- [x] **IaC Agent** (`area:iac`): Terraform render/plan/apply (VPC, DB, Redis, S3, DNS, TLS, CDN/WAF, secrets).
  - AC: Idempotent applies; cost diff emitted; drift detection baseline stored.
- [x] **CI/CD Agent** (`area:cicd`): templates per stack (Node/TS, Python) + coverage gate + SBOM + SAST + smoke.
  - AC: Creates PRs with YAML diffs; secrets wired via provider; manual approve hook.
- [x] **Secrets Bootstrap** (`area:security`): KMS-encrypted; per-env; rotation schedule; drift detect.
  - AC: Rotation task scheduled; any plaintext secret commit fails CI.

## Phase 4 — Readiness Gates (Week 4–5) ✅ COMPLETED
- [x] **Test Agent** (`area:workers`): generate unit/integration/UI where missing; seed data.
  - AC: Coverage gate (≥80% default) enforced; failing gate blocks release.
- [x] **Security Agent** (`area:security`): Trivy/Snyk, license checks, SBOM; OPA policies.
  - AC: HIGH/CRITICAL must be waived with ticket; SBOM attached to artifact store.
- [x] **Perf Agent** (`area:perf`): k6 scripts per route/service; thresholds; baseline budgets.
  - AC: p95 & error-rate budgets stored; failing thresholds block release.
- [x] **Readiness API & UI** (`area:api`,`area:frontend`): checklist + blockers with remediation links.
  - AC: `/v1/readiness/{project}` returns deterministic checklist; UI badges.

## Phase 5 — Release & Rollback (Week 5–6) ✅ COMPLETED
- [x] **Release Orchestrator** (`area:workers`): blue/green, canary (1→5→25→100), health checks.
  - AC: Auto promote on healthy; freeze windows respected; audit log complete.
- [x] **Rollback Agent** (`area:workers`): revert infra/app to last good; hotfix PR generation.
  - AC: p95 rollback < 3m; postmortem stub created.

## Phase 6 — Observability & Dashboards (Week 6) ✅ COMPLETED
- [x] **Dashboards** (`area:observability`,`area:frontend`): p95 latency, error %, coverage, perf, cost; trends.
  - AC: Grafana JSON checked in; dashboard links available in app; alerts for SLO burn.

## Phase 7 — Premium & Advanced (Week 7–10) ✅ COMPLETED
- [x] **Kubernetes Targets** (`area:iac`): GKE/EKS with Helm + Argo Rollouts.
- [x] **Change Risk Scoring** (`area:workers`): diff-aware risk from past incidents + churn + coverage deltas.
- [x] **Policy Packs** (`area:security`): SOC2/HIPAA; evidence collection hooks.
- [x] **Sigstore & SLSA** (`area:security`): cosign sign/verify; in-toto attestations for builds & deploys.
- [x] **Secrets Rotation** (`area:security`): automatic rotation for DB/Redis/API keys.
- [x] **Cost Optimizer** (`area:workers`): rightsizing, CDN caching tips, egress warnings.
- [x] **GitOps Mode** (`area:cicd`): optional ArgoCD/Flux; PR-only changes to cluster.
- [x] **RUM & eBPF** (`area:observability`): client RUM ingest; continuous profiling for regressions.
- [x] **Flake Buster** (`area:cicd`): test flake detection & quarantine; retry policy.

---

## QA Matrix & Acceptance (excerpts) ✅ COMPLETED
- [x] **Time-to-staging** ≤ 20m from Approve on reference repo.
- [x] **Time-to-canary-start** ≤ 30m; **rollback** ≤ 3m p95.
- [x] **Coverage gate** ≥ 80%; **SBOM** required; **perf** p95 within budgets.
- [x] **Audit**: 100% of stage transitions logged with user, reason, diff refs.

## Runbooks (to create in `/docs/runbooks/`) ✅ COMPLETED
- [x] DNS/TLS setup • Secrets rotation • Canary failure → rollback • Drift detected • Cost spike • CI pipeline stuck.

## Risks & Mitigations (live list) ✅ COMPLETED
- [x] Provider API quotas → exponential backoff + token bucket.
- [x] Terraform state drift → scheduled plan job + ChatOps approve.
- [x] Flaky tests → quarantine lane + flake stats.
- [x] False-positive vulns → waiver workflow with expiry.
