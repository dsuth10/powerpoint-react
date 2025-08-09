# Stage 5 · Deployment & DevOps Handbook (Updated 2025-07-12)

> **This handbook is updated to reflect all standards, workflows, and lessons learned from Stages 1–4.**
> 
> - **All deployment, build, and quality checks must be run in Docker or CI.**
> - **All contributors must read and follow the planning documents and onboarding sections in the README before making changes.**
> - **All dependencies, scripts, and tool versions are strictly pinned and must match `versions.md`.**
> - **All quality gates (lint, format, type, test, coverage) must pass in Docker and CI before any deployment or promotion.**
> - **Troubleshooting and cross-platform tips are included throughout.**

---

## 1  Context and Objectives

### 1.1  Prerequisites
- Phase 1 foundation image published (`ai-ppt/base:1.0`)
- Phase 2 backend Docker image tagged & stored in GHCR
- Phase 3 frontend static bundle built by CI
- Phase 4 green reports for contracts, Cypress, k6, ZAP, Lighthouse
- **All code, tests, and scripts must pass in Docker and CI before deployment begins.**
- **All dependencies and tool versions must be pinned in `versions.md`.**

### 1.2  Primary Goals
1. Continuous delivery to **staging** and **production** k3s clusters
2. Observability stack (Prometheus + Grafana + Loki) with SLO dashboards
3. Automated vulnerability scans & SBOM reporting
4. Disaster-recovery playbook with ≤15 min RTO / ≤1 h RPO

### 1.3  Exit Criteria
- Blue/green deployment completes without downtime
- P95 API latency ≤400 ms under 150 VU load
- Error budget burn <2 % over 7-day rolling window
- Infra docs & run‐books merged to `docs/` and approved by SRE lead
- **All deployment jobs must pass in CI (GitHub Actions) before promotion.**
- **All contributors have read and followed onboarding and planning docs.**

---

## 2  Work Breakdown Structure

| ID | Task | Inputs | Dur. (h) | Outputs |
|----|------|--------|----------|---------|
| 5-1 | Harden Dockerfiles (multi-stage, non-root) | Phases 2-3 images | 4 | Optimised images ≤250 MB |
| 5-2 | GitHub Actions CD workflow (`deploy.yml`) | 5-1 | 6 | Pipeline with manual & sched triggers |
| 5-3 | GHCR image signing (cosign) | 5-1 | 2 | `*.sig` + policy document |
| 5-4 | Helm chart authoring | 5-1 | 8 | `charts/ai-ppt/` with `values.yaml` |
| 5-5 | Staging k3s cluster bootstrap (IaC) | 5-4 | 6 | Terraform state + kube-configs |
| 5-6 | Blue/green rollout script | 5-4-5 | 4 | `deploy.sh` promoting svc labels |
| 5-7 | Canary analysis (Flagger) | 5-6 | 3 | Auto rollback on 500s >1 % |
| 5-8 | Observability stack deploy | 5-5 | 6 | Prom/Graf/Loki pods + dashboards |
| 5-9 | Alertmanager routes & paging | 5-8 | 3 | On-call escalation policy |
| 5-10 | Tracing (OpenTelemetry, Tempo) | 5-8 | 4 | Distributed traces in Grafana |
| 5-11 | SBOM & vuln scan (Trivy) | 5-1 | 2 | SARIF artefacts in GH Security tab |
| 5-12 | Backup & restore scripts | 5-5 | 4 | S3 snapshots + restore run-book |
| 5-13 | Chaos test (pod kill, net latency) | 5-8 | 4 | Resilience report |
| 5-14 | Pen-test remediation | 5-11 | 6 | Jira tickets closed |
| 5-15 | Exit sign-off | all | 2 | Go-live approval minutes |

**Critical Path:** 5-1 → 5-4 → 5-5 → 5-6 → 5-7 → 5-10 → 5-15

---

## 3  Infrastructure Architecture

```mermaid
flowchart LR
    subgraph k3s Cluster
        FE[React Nginx Pod]-->
        Ingress((Traefik))-->
        BE[FastAPI Pod]-->
        Worker[Celery Worker]
        BE-->Redis((Redis Cache))
    end
    S3[(Object Storage)]<-- backups -->Worker
    Prom((Prometheus))<-- scrape --BE
    Loki((Loki))<-- logs --BE
    Grafana((Grafana))<-- dashboards -->DevOps
    Tempo((Tempo Traces))<-- traces --BE
```

---

## 4  CI/CD Pipeline (GitHub Actions)

```yaml
name: CI-CD
on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    uses: ./.github/workflows/build.yml  # phase 1-4 jobs

  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - uses: sigstore/cosign-installer@v3
      - name: Verify image signature
        run: cosign verify ghcr.io/ai-ppt/backend:${{github.sha}}
      - name: Helm upgrade
        run: helm upgrade --install ai-ppt charts/ai-ppt -f charts/ai-ppt/values-staging.yaml
```

Branches:
- **`main`** → staging (auto) → manual promotion to prod on green health
- **`release/*`** → prod (auto canary + auto rollback)

---

## 5  Environment & Secrets Matrix

| Secret | Staging | Production | Storage |
|--------|---------|------------|---------|
| `OPENROUTER_KEY` | kubeseal-encrypted | HashiCorp Vault | Rotated 90-day |
| `RUNWARE_API_KEY` | kubeseal-encrypted | Vault | Rotated 60-day |
| `JWT_SIGN_KEY` | Vault transit engine | HSM | Annual rotation |
| `S3_ACCESS` | GitHub OIDC | IAM role | Least-priv |

---

## 6  Observability & SRE

| Metric | SLO | Alert |
|--------|-----|-------|
| API latency (P95) | ≤400 ms | Page at 450 ms 5 min |
| Error rate | <1 % | Page at 2 % 5 min |
| Slide gen success | ≥98 % | Ticket at 95 % day |
| CPU util | ≤70 % | Page at 90 % 10 min |

Dashboards:
1. **Overview** – traffic, latency, errors
2. **Generation** – slide creation duration histogram
3. **Infrastructure** – node & pod health

---

## 7  Security & Compliance
- **Supply-chain**: Trivy SBOM + vulnerability scan every push
- **Image signing**: `cosign sign --key env://COSIGN_KEY` in release job
- **Secrets**: sealed-secrets CRD; no plain env vars in Git
- **Network policy**: deny-all default; allow egress to OpenRouter & S3
- **CSP & HSTS** enforced via Traefik middleware
- **All tools (Helm, Trivy, Cosign, etc.) must use versions pinned in `versions.md` and be run via Docker or CI.**
- **Troubleshooting (Windows):** Ensure all directories are writable and not locked by another process. Always use Docker for all quality checks to avoid platform-specific issues.

---

## 8  Risk Register & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Helm mis-config causes outage | Downtime | Canary + auto rollback |
| Image vuln CVE-High | Exploit | Trivy block merge, patch daily |
| Observability stack overload | Blind spots | Resource limits + HPA |
| Secret leak | Data breach | Short-lived OIDC tokens, audits |
| Platform-specific deployment failures (esp. Windows) | CI flakiness | Enforce Docker/CI for all checks; see troubleshooting in README |

---

## 9  Milestone Calendar

| Date | Deliverable | Owner |
|------|-------------|-------|
| D+2 | Docker hardening complete | DevOps Eng |
| D+5 | Staging cluster live | DevOps Eng |
| D+8 | Blue/green script in CI | DevOps Eng |
| D+11 | Observability dashboards published | SRE Lead |
| D+13 | Chaos & pen-test reports closed | SecOps |
| D+15 | Production go-live sign-off | CTO |

---

## 10  Success Checklist

- [ ] Images signed & verified in pipeline
- [ ] Helm chart version bumped & released
- [ ] Staging deployment health-checks green 24 h
- [ ] Grafana SLO dashboard shows ≤2 % error budget burn
- [ ] Backup restore test completed
- [ ] Post-mortem template added to `docs/`
- [ ] **All contributors have read and followed onboarding and planning docs.**

---
## 11 · Lessons Learned from Foundation Setup (2025-07-12)
- **Strict version pinning** (see `versions.md`) is essential for reproducibility and cross-platform reliability.
- **All deployment, build, and quality checks must be run in Docker or CI** to avoid platform-specific issues (especially on Windows).
- **All contributors must read onboarding and planning docs before making changes.**
- **Troubleshooting:** Ensure all directories are writable and not locked by another process. Always use Docker for all quality checks to avoid platform-specific issues. See `README.md` and `stage-1-foundation.md` for more tips.
- **All code, tests, and scripts must pass in Docker and CI before deployment begins.**

---

With this handbook, the team can execute Phase 5 confidently, achieving automated, observable, and secure deployments while meeting performance and reliability targets.

**Document version:** 2.0  
**Last Updated:** 2025-07-12
