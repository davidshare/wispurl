# Local implementation issues

The [Local DevOps, DevSecOps, and SRE Epic](EPIC.md) is the canonical end-to-end implementation order and issue tracker. Issue IDs and `depends_on` references are stable; filenames are grouped by tool or engineering area.

## Issue directories

- [`app/`](./app/) — Application foundations and service behavior (6 issues)
- [`docker/`](./docker/) — Docker Compose and local environment (2 issues)
- [`containers/`](./containers/) — Container image build and hardening (2 issues)
- [`security/`](./security/) — Security engineering and policy (9 issues)
- [`cicd/`](./cicd/) — Continuous integration and delivery (2 issues)
- [`kubernetes/`](./kubernetes/) — Kind, Helm, ArgoCD, and Kubernetes workloads (5 issues)
- [`observability/`](./observability/) — Metrics, logs, traces, and alerting (6 issues)
- [`sre/`](./sre/) — Reliability, recovery, and operations (7 issues)

Issue-level status and acceptance evidence remain in each issue file. The checkboxes in the epic represent whole-issue completion, not individual subtask completion.
