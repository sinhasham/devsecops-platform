# 🚀 Production-Grade DevSecOps Platform

A full production-grade DevSecOps + GitOps platform built on Kubernetes.

## 🛠️ Tech Stack

| Category | Tools |
|----------|-------|
| Container Orchestration | Kubernetes (kind) |
| Package Management | Helm |
| Infrastructure as Code | Terraform |
| CI/CD | GitHub Actions |
| GitOps | ArgoCD |
| Security Scanning | Trivy, Checkov, Gitleaks |
| Metrics | Prometheus + Grafana |
| Logging | Loki + Promtail |
| Tracing | OpenTelemetry |
| App | FastAPI (Python) |

## 📦 Project Structure

    devsecops-platform/
    ├── app/                    # FastAPI application
    ├── docker/                 # Dockerfile (multi-stage, non-root)
    ├── helm/devsecops-api/     # Helm chart
    ├── k8s/base/               # Raw Kubernetes manifests
    ├── terraform/kind-cluster/ # Infrastructure as Code
    ├── gitops/                 # ArgoCD application manifests
    └── .github/workflows/      # CI/CD pipelines

## 🔐 Security Pipeline

Every push triggers:
1. Gitleaks — secret scanning
2. Checkov — IaC misconfiguration scanning
3. Docker build + push to DockerHub
4. Trivy — container vulnerability scanning

## 📊 Observability Stack

- Prometheus — metrics collection (18 scrape targets)
- Grafana — dashboards at localhost:3000
- Loki + Promtail — log aggregation
- OpenTelemetry — distributed tracing

## 📝 Modules Completed

- [x] Module 0-4: Environment, K8s, Networking, Storage, Docker
- [x] Module 5: Helm
- [x] Module 6: Terraform
- [x] Module 7: GitHub Actions CI
- [x] Module 8: DevSecOps Tools
- [x] Module 9: ArgoCD & GitOps
- [x] Module 10-11: Prometheus + Grafana
- [x] Module 12: Loki
- [x] Module 13: OpenTelemetry
- [x] Module 14: Production Architecture
