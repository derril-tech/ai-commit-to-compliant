
# PLAN.md — ProdSprint AI
## Vision
Ship an **autonomous release orchestrator** that gets apps from repo to **compliant production in hours**, not weeks—baking in **tests, security, performance, observability, and reversibility** by default.

## Goals & Outcomes
- **One‑click environments** (staging → prod) with IaC, DNS, TLS, secrets.
- **Policy‑gated CI/CD** (coverage, SBOM, SAST/DAST, perf budgets, cost caps).
- **Safe releases** (blue/green, canary) with **instant rollback**.
- **Dashboards** (p95, errors, coverage, perf, cost) + **readiness checklist**.
- **Org golden paths** & templates for consistent delivery across teams.

## Target Users
Founders/Indie devs • Platform teams • Security/Compliance • Agencies.

## Strategy (How we’ll win)
1. **Opinionated defaults** (reliable templates) + **generated specifics** per repo.
2. **Policy before promote**: everything is gated and auditable.
3. **Fast feedback loops**: canary by default, automated rollbacks.
4. **Extensible adapters** for cloud/CDN/DNS/CI providers.

## Deliverables (V1)
- Backend API & workers (agents) with evented orchestration and SSE progress.
- UI Wizard, Readiness checklist, Release console, Dashboards.
- Terraform templates (VPC, Postgres, Redis, S3, DNS, TLS, CDN/WAF, secrets).
- CI templates for Node/TS & Python; Trivy/SBOM; k6 perf.
- Render (BE) + Vercel (FE) deployment paths.

## Milestones & Timeline
- **M1 Foundations (W0–2)** ✅: auth/tenancy, stores, CI/CD baseline, observability, shell UI.
- **M2 Plan (W2–3)** ✅: repo audit → plan preview with diffs & cost.
- **M3 Apply (W3–4)** ✅: Terraform apply + CI templates PRs + secrets bootstrap.
- **M4 Readiness (W4–5)** ✅: tests/security/perf agents + readiness API/UI.
- **M5 Release (W5–6)** ✅: canary + rollback + freeze windows + audit.
- **M6 Dashboards (W6)** ✅: SLO cards & trends; alerts.
- **M7 Premium (W7–10)** ✅: Kubernetes + Argo, risk scoring, SOC2/HIPAA packs, Sigstore/SLSA, GitOps mode, cost optimizer.

## Success Metrics
- Median repo→staging ≤ **20m**; repo→canary start ≤ **30m**; rollback ≤ **3m** p95.
- ≥ **80%** projects pass readiness without manual intervention.
- ≥ **70%** policy gates enabled post‑week 1.
- **NPS ≥ 45**, weekly active workspaces ↑.

## Risks & Responses
- **Drift & hidden state** → scheduled plan+drift alerts, GitOps option.
- **Provider outages** → multi-target failover, backoff, DLQ replay.
- **False blocks** (security/perf) → waive-with-expiry + audit.
- **Secret sprawl** → KMS, rotation, scanning on PR.

## Pricing & Packaging (draft)
- **Free**: 1 project, Vercel/Render, basic gates.
- **Pro**: 10 projects, custom policy packs, rollout strategies, dashboards, alerts.
- **Enterprise**: SSO/SAML, on‑prem runners, SOC2/HIPAA packs, GitOps, audit export.

## Rollout
Pilot with 3–5 teams → collect baselines → refine policies → open self‑serve with quotas & metering → add Kubernetes/Argo in Premium.

## Appendix — Policy Gates (defaults)
- **Coverage ≥ 80%** (line) or **70%** (branch) AND no critical untested areas.
- **SBOM required**; no **CRITICAL/HIGH** vulns unless waived w/ expiry.
- **Perf**: p95 latency within budget; error rate < 1%.
- **Cost**: projected month cost within ceiling; % change explained.
- **Compliance**: TLS, HSTS, CSP; secrets encrypted; audit complete.
