# RaizHost cost-disciplined platform audit

**Audit date:** September 6, 2026. **Scope:** repository evidence, not a live AWS or billing audit.
**Owner-reported baseline:** approximately $160/month. **Goal:** $180-220/month or lower;
$250 is a soft review boundary, not a target or an enforced spending cap.

## Executive decision

Do not migrate production to EKS now. Preserve economical static/serverless workloads and the
existing container deployment while closing recovery and Terraform-state risks. Propose a separate,
ephemeral EKS learning platform once scope, teardown, and its incremental budget are approved.
The [workbench](../platform/README.md) contains runnable cost and plan-triage tools plus the proposed
operating sequence. No cloud resources were created by this audit.

## Evidence boundaries

Code inspection establishes what is declared and what workflows are intended to do. Operational
records establish what was previously observed. Neither proves today's cloud inventory, current
invoice, successful backups, enabled alerts, GitHub environment rules, or actual IAM permissions.
No fresh AWS inventory, Cost Explorer result, Terraform state, DNS answer, database content,
cloud metric, or recovery test was obtained during this pass. No AWS mutation was performed.

Repositories examined included `raizhost-architecture`, `aws-infra`, `raizhost-operations`,
`raizhost-app`, `raizhost`, `raizhost-infra`, `raizhost-demos`, and adjacent website/deployment
repositories. This is a focused first-pass discovery, not a claim that every file and resource
in the ecosystem was inspected. Source pointers below preserve the distinction between public
reports and private implementation evidence without publishing account identifiers or secrets.

| Evidence | Observed fact | Confidence boundary |
| :-- | :-- | :-- |
| [Current state](current-state.md), reconciled August 30 | S3/CloudFront static delivery; serverless paths; app/Postgres/PgBouncer/Redis/NAT on shared anchor | Recent operator report; not a fresh cloud inventory |
| `aws-infra/main.tf` | Reusable budget, network, anchor, security, backup, OIDC and observability modules; private default route uses anchor | Code verified; deployed configuration and drift unverified |
| `aws-infra/.github/workflows/terraform-ci.yml` | Static-only CI, backend-disabled init, validation and scans; explicit H8 hold | Workflow code verified; no live plan run |
| `aws-infra/modules/budget-guardrail/main.tf` | Budget alerts and optional anomaly monitoring already defined | Delivery/confirmation and deployed settings unverified |
| `raizhost-app/.github/workflows/deploy.yml` | Successful same-repo push CI gates exact-SHA deployment; CodeBuild runner, OIDC, SSM, migrations, health-gated deploy script and ops drift check | Workflow inspected; current execution and branch/environment settings unverified |
| `raizhost-infra/README.md` and current-state record | k3s/Argo CD/observability history exists; Hetzner is reported as a rollback shadow, not active editor runtime | Do not infer currently running EKS or a required live VPS dependency |

Public architecture base revision: `7460e95b665e4d1f1f85fd8bc240d3429bb56baa`.
Inspected file blob fingerprints for repeatability:

- Current-state document: `ca3772912a1e2ad25ad57dc353fa9211ff8fa1fb`.
- Infrastructure root: `3d656cc69d5a414092df2412ebdf6703938c40e4`.
- Infrastructure CI: `f01591180f3d6f7bd7fd28ec6aba55a5a6b6835a`.
- Budget module: `009f963eeff958f1da895d6cceb248a39f62836e`.
- App deployment workflow: `761961bf78afdd02dd978c7611d15d985f55d430`.

There is already useful engineering here. Do not describe containerization, OIDC, reusable modules,
alerts, deployment health gates, or GitOps history as entirely missing just to create work.
Existing topology-correction PRs and the app's pending authentication work should remain separate
from this portfolio initiative; no auth rollout or historical-resource retirement is authorized here.

## Cost baseline: unresolved, not fabricated

The public current-state document reports a previous approximately $106 measured run rate with
continuous ops-box usage and a projected $90-95 after scheduling. It also reports a separate
$10 runner alert budget. **A budget is not usage, and a projection is not an invoice.** Those
figures do not reconcile the owner's current $160 report. Differences in month, account scope,
runner activity, retained resources, external services, credits, or tax need evidence.

| Cost driver to reconcile | Current evidence | Next measurement |
| :-- | :-- | :-- |
| Anchor compute and EBS | Shared always-on host and attached stateful storage declared | Instance type/hours, all volumes, utilization and backup footprint |
| Ops/development compute | Scheduled operator machine reported; may serve other projects | Actual daily run hours, CPU/memory, job ownership, retained EBS/IPs |
| CodeBuild and other runners | Ephemeral app runner factory reported | Build minutes/type, retries, cache/image transfer and log retention |
| Networking and edge | NAT-instance route, CloudFront, DNS and endpoints across records | IPv4 hours, endpoint-AZ hours, transfer, request and cache metrics |
| Storage, images and backups | S3, EBS snapshots, ECR, contract/data retention | GB-months, lifecycle, orphaned volumes and restore requirements |
| Observability and security | Alarms, logs and security modules exist | Ingestion, retention, custom metric count and optional service usage |
| Other accounts and VPS | Legacy/rollback surfaces documented | Current invoice, dependency owner, retirement approval |

**Verified savings: $0.** Do not spend an assumed savings figure before it is realized and
measured. No instance size reduction, volume deletion, snapshot purge, endpoint removal, or
VPS cancellation is recommended without ownership/dependency validation and rollback.

For the next read-only billing pass, collect June, July and August full-month actuals, then
September-to-date separately. Reconcile service, usage type, region and linked-account totals
against invoices, including refunds/credits/tax consistently. Separate AWS from other providers
and RaizHost production from personal/operator projects. Record query time, period, metric and
billing scope; redact identifiers before publication. Cost Explorer/API calls may have small fees.

Inventory must cover all relevant accounts and enabled regions, with pagination. An empty result
in one region is not proof a resource is absent. Collect compute, volumes, snapshots, public IPs,
NAT/LB/endpoints, databases, log retention, runner activity, S3/ECR usage, tags and schedules.
Read-only discovery must not retrieve secret values or enable cost-incurring security products.

## Highest-value risks and improvements

| Priority | Finding | First safe improvement | Acceptance evidence |
| :-- | :-- | :-- | :-- |
| P0 | Last recorded Terraform plan included destructive DNS drift; backend/tfvars completeness is also flagged | Preserve static-only CI; reconcile resource ownership, config and state under explicit approval | Reviewed full-scope plan after reconciliation; no DNS loss |
| P0 | Backup job exists but freshness/restore proof remains open | Inspect backup metadata; schedule an isolated restore with data-handling approval | Recoverable database, app-level checks, measured RPO and RTO |
| P1 | Anchor co-locates app, databases, cache/pooler and private egress | Map dependency failure domains; document restore and traffic isolation | A tested recovery procedure, not a claim of multi-AZ HA |
| P1 | Current costs do not match historical estimate | Build measured cost ledger before resizing/retiring | Same-scope before/after bill and usage evidence |
| P1 | Infrastructure scans are configured as advisory | Triage findings and ratchet reviewed rules; do not blindly make all findings fatal | New unsafe changes blocked without disabling legitimate CI |
| P2 | Production deployment already has substantial safeguards | Verify live protections, OIDC trust, migration compatibility and rollback drill | Successful staged bad-rollout recovery and audit trail |
| P2 | Kubernetes depth is a learning gap, not a requirement for static hosting | Isolated stateless lab, explicit exercises, controlled EKS sessions | Recorded diagnoses, fixes, node/Pod failures and cost receipts |

A backup's existence is not proof of recovery. A failed anchor can affect the editor and private
serverless egress while independently hosted static assets continue to serve, subject to their
own dependencies. Multi-AZ subnet declarations do not remove that shared-host failure domain.

## Recommended target and cost envelope

**Tier A: customer production.** Keep static delivery on S3/CloudFront and appropriate APIs/jobs
serverless. Keep the current container path while proving backups, rollback, alert delivery,
resource ownership and cost attribution. Do not change DNS, auth, publishing, or customer data
for portfolio value. Measure user-facing availability/errors and latency before setting SLOs.

**Tier B: disposable platform environment.** Independently scoped Terraform state and deployment
identity; synthetic stateless workload; private workers across two AZs; explicit ALB ingress,
probes, resources, HPA, PDB, workload identity and small telemetry footprint. Practice a manual
inspection/deployment path before adding GitOps. Require teardown verification before declaring
this cost-efficient. The full proposed choices and limitations are in the workbench.

Use the workbench's conservative two-worker allowance and no savings assumption:

| Scenario | Additional monthly planning estimate | Combined with owner baseline |
| :-- | --: | --: |
| Offline tools only | $0 new AWS infrastructure | Approximately $160, before unrelated usage changes |
| EKS resources provisioned 48 hours | Approximately $29 | Approximately $189 |
| EKS resources provisioned 80 hours | Approximately $38 | Approximately $198 |
| Same EKS design left on 730 hours | Approximately $224 | Approximately $384 |

These estimates exclude taxes, discounts and third-party bills and do not enforce a spending cap.
Choose an initial **$30-40 incremental lab envelope**, with the number of provisioned hours,
cleanup policy and independent alerting approved first. There is no need to aim for $250.
Do not enable EKS Auto Mode, provisioned control-plane tiers, or paid managed capabilities by default.

## HA and database decision record

| Design choice | Failure/impact | Enterprise alternative | Adoption trigger and incremental cost |
| :-- | :-- | :-- | :-- |
| Shared production anchor retained temporarily | Host/AZ loss interrupts stateful app and private egress | Independent application replicas, managed database, resilient egress | Recovery/SLO or maintenance requirement exceeded; price complete design after utilization data |
| Single temporary lab NAT | NAT-AZ loss can impair egress from both worker AZs | AZ-local NAT paths | Deliberate HA egress exercise; second NAT/IP about $2.40 per 48-hour session-month before bytes |
| Two lab workers and replicas | Insufficient surviving capacity can still cause outages | Additional headroom and tested AZ placement | Measured scheduling/load requirement; one additional worker at model allowance is $2.40 per 48 hours plus disk |
| Small retained telemetry allowance | Limited history after lab destruction | Longer retention or managed observability | Incident-analysis/compliance need exceeds short retention; quote ingestion/storage first |

RDS is a decision to evaluate, not an automatic migration. Compare single-AZ managed PostgreSQL
and Multi-AZ against database size, extensions, connections, backup quality and operator time.
Moving PostgreSQL alone will not remove the anchor's app/cache/NAT roles, so "RDS is cheaper"
is not established. Define RPO/RTO with the owner; test restore and migration rollback before any
change. Never store production database dumps or sensitive Terraform plans in this public repo.

## Implementation sequence and truthful completion

This change implements the audit, offline cost model, conservative plan triage, synthetic tests,
and non-deploying test workflow. It does not close H8, fix backup freshness, deploy EKS, execute
failure drills, improve measured uptime, or save verified dollars.

Next: collect billing/inventory evidence; address recovery and state safety; verify existing
security/deployment controls; run local Kubernetes exercises; obtain sandbox account/budget
approval; provision a bounded EKS session; record operational drills; tear down and reconcile
cost; then decide whether GitOps or additional HA provides enough benefit to justify its burden.

Each completed stage should publish sanitized evidence and upgrade its status from proposed to
implemented or verified. Interview claims must track that evidence rather than tool names.
