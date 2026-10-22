# RaizHost platform engineering workbench

**Status: offline tooling implemented; EKS and the two-tier target are proposed, not deployed.**

Start with the [September discovery audit](../docs/platform-audit-2026-09-06.md).
The production reference remains [current state](../docs/current-state.md). This directory
contains no AWS credentials, Terraform resources, deploy actions, or customer data.

## Run the tools

Python 3.10 or newer and the standard library are sufficient. From the repository root:

```bash
python3 -m unittest discover -s platform -p 'test_*.py' -v
python3 platform/cost_model.py
python3 platform/cost_model.py --cluster-hours 80 --worker-hours 80 --network-hours 80 --volume-hours 80
```

The model defaults to the owner's approximately $160 monthly baseline, not a verified invoice.
It makes **no savings assumption**. Default worker pricing is an explicit $0.05 per node-hour
allowance, not a quoted EC2 instance price. Replace it with a current region/type quote before
approving a deployment. Two nodes do not necessarily have capacity for an entire monitoring stack;
measure requests, daemon overhead, memory pressure, and CPU credits before choosing instance sizes.

### Cost assumptions and results

Rates were reviewed on September 6, 2026. The scenario uses a 730-hour comparison window,
standard-support EKS, two private workers, one zonal NAT Gateway, an internet-facing ALB,
three baseline public IPv4 addresses, and two 20 GB gp3 root volumes. S3 gateway endpoint is the
preferred free path for S3 access; extra interface endpoints are not included.

| Component | Assumption | 48 provisioned hours | 730 provisioned hours |
| :-- | :-- | --: | --: |
| EKS control plane | $0.10 per hour | $4.80 | $73.00 |
| Two workers | $0.05 per node-hour allowance | $4.80 | $73.00 |
| One NAT Gateway | $0.045 per hour before bytes | $2.16 | $32.85 |
| One ALB | $0.0225 per hour before capacity usage | $1.08 | $16.43 |
| Public IPv4 | Three at $0.005 per hour | $0.72 | $10.95 |
| Root EBS | 40 GB at $0.08 per GB-month, prorated | $0.21 | $3.20 |
| Retained-resource allowance | State, images, retained storage/logs | $5.00 | $5.00 |
| Variable-usage reserve | Traffic, telemetry, build/API usage | $10.00 | $10.00 |
| **Incremental estimate** | Sum before rounding | **$28.77** | **$224.43** |
| **Ecosystem estimate** | Owner baseline plus increment | **$188.77** | **$384.43** |

At 80 hours, the same model estimates **$37.95 incremental / $197.95 total**. These are
planning estimates, not caps or promised bills. The reserve is not an upper bound. Taxes,
credits, support plans, external subscriptions, extra storage, ALB growth, CPU surplus credits,
paid EKS capabilities, and usage above the reserve can change the result. Small sessions also
have service-specific minimum/rounded billing. EBS month proration here is approximate.

Use the lifetimes for which resources **exist**, including provisioning, troubleshooting,
and teardown. Separate hour inputs deliberately expose forgotten control planes and networks:

```bash
# Workers stopped, but the cluster, NAT/ALB/IPs and disks remain all month:
python3 platform/cost_model.py --cluster-hours 730 --worker-hours 0 --network-hours 730 --volume-hours 730

# Extended-support control plane alone is $438 over the comparison window:
python3 platform/cost_model.py --cluster-hours 730 --extended-support
```

A second NAT and its IPv4 address add about $2.40 for 48 hours or $36.50 for 730 hours,
before data transfer. One NAT is a deliberate sandbox compromise, not an HA egress claim.
The same cost profile does not apply to an internet-isolated design: price the complete
ECR, S3, identity, load-balancer, logging, and other required endpoint set first.

Pricing sources: [EKS](https://aws.amazon.com/eks/pricing/),
[VPC and IPv4](https://aws.amazon.com/vpc/pricing/),
[ALB](https://aws.amazon.com/elasticloadbalancing/pricing/),
and [EBS](https://aws.amazon.com/ebs/pricing/).

## Offline Terraform plan triage

`plan_review.py` reads an **already authorized, privately stored** JSON plan export. It never
invokes Terraform, obtains credentials, reads cloud state, changes state, or authorizes apply.
Do not generate a fresh production plan to exercise this tool while the H8 hold remains open.
The tests use entirely synthetic plans, including a DNS-deletion regression.

```bash
python3 platform/plan_review.py /private/approved-plan.json
```

Exit zero means only **no flags in supported fields**, never "safe to apply". Exit one requires
human review; exit two means invalid or unsupported input. Every supported mutation needs review,
with extra reasons for DNS, database/storage/key changes, delete/replacement/forget, imports,
moves, drift, incomplete plans, deferred changes, output changes, and checks that did not pass.

The parser intentionally rejects state JSON, missing status metadata, unknown actions/major
formats, duplicate keys, non-finite numbers, and files over 50 MiB. Some otherwise valid Terraform
exports, including older exports or omitted empty arrays, may be rejected conservatively.
It is a review aid, **not a comprehensive Terraform policy engine**. An export cannot prove
correct credentials, a non-targeted full plan, current state, review approval, or that H8 is fixed.
Future schema features require review and tests. Do not wire an exit-zero result to an apply.

Output contains only fixed reason codes and counts, never addresses or values. Nevertheless,
**raw JSON plans and state may contain secrets**: keep them outside this public repository,
PR comments, and public CI artifacts. See the [Terraform JSON format](https://developer.hashicorp.com/terraform/internals/json-format).

## Proposed ADR: separate production from the learning platform

**Decision status: proposed; provisioning requires approval.** Keep economical production
request paths and improve their recovery evidence. Build EKS separately to learn operations
without moving customer authentication, billing, databases, or publishing onto a lab cluster.

Production benefits from a small failure surface. The lab benefits from reproducibility,
failure injection, teardown, and realistic networking. A permanent EKS cluster buys idle hours;
a disposable cluster buys practice. Existing k3s/GitOps history is useful context, not evidence
that the proposed EKS environment exists.

Start with a stateless, synthetic status/preview demonstration. Use no production credentials,
customer data, shared database, DNS cutover, or dependency on the production anchor. Build an
ARM-compatible image and test it before selecting Graviton; use x86 when dependencies require it.
The real editor is already containerized and need not be rewritten to learn Deployments.

### Proposed build gates

| Gate | Work | Evidence required before progressing |
| :-- | :-- | :-- |
| 0 | Cost and account inventory | Full-month billing scope, dependencies, owners, measured idle candidates |
| 1 | Production recovery | Fresh backup, isolated restore, measured RPO/RTO, rollback ownership |
| 2 | State safety | H8 DNS ownership reconciled and reviewed; no automatic apply restoration |
| 3 | Local Kubernetes | Probe, selector, rollout, and resource-failure exercises with synthetic data |
| 4 | Sandbox foundation | Explicit account/region, isolated state and IAM, version pins, cost approval |
| 5 | Ephemeral EKS | Two-AZ private workers, ingress, workload identity, tested teardown |
| 6 | Operations | SLO evidence, HPA/PDB and node drill, postmortem, cost receipt |
| 7 | GitOps | One reconciler, demonstrated drift correction and Git-revert rollback |

Gate 2 blocks production Terraform; it need not prevent an independently approved and
strictly isolated sandbox implementation. Never attach the sandbox to the unreconciled
production state just to reuse modules.

For the new sandbox, prefer an encrypted, versioned S3 state backend with explicit
`use_lockfile = true`, compatible Terraform version pins, least-privilege state/lock permissions,
and a committed provider lockfile. Existing production locking is not changed by this work.
[DynamoDB locking is deprecated](https://developer.hashicorp.com/terraform/language/backend/s3);
a migration must be separately planned so older clients cannot bypass coordination.

### Networking and availability choices

Use two public subnets for the ALB and two private worker subnets. Two zonal managed node groups
with one initial worker each make initial placement explicit; confirm placement before any HA
claim. Two replicas, topology constraints, readiness, and spare capacity must also be tested.
A multi-AZ control plane or subnet list alone does not prove the application survives an AZ loss.

For the first small lab, prefer one temporary zonal NAT plus the S3 gateway endpoint over
an always-on per-AZ NAT fleet or a large interface endpoint bundle. A NAT-AZ outage can break
private egress in both worker AZs. Enterprise evolution is AZ-local egress and sufficient
surviving workload capacity when availability requirements justify the additional cost.

Enable private Kubernetes API access. Restrict any public API endpoint to approved operator
and runner egress, or use a runner with a deliberate private network path. OIDC authentication
alone does not provide connectivity to a private endpoint. Do not expose the API broadly
because a hosted runner has changing addresses. For no-internet workers, Pod Identity requires
EKS Auth access; IRSA requires STS access. See [private EKS requirements](https://docs.aws.amazon.com/eks/latest/userguide/private-clusters.html).

Initially use managed node groups and on-demand baseline capacity. Add bounded Spot experiments
only after reliable creation/recovery. Postpone Karpenter, managed Prometheus/Grafana, paid EKS
capabilities, and a service mesh unless an observed constraint justifies them. Start GitOps with
one self-hosted Argo CD instance during lab sessions after the manual deployment path is understood;
validate its memory overhead rather than assuming small nodes fit every controller.

## Operator exercises: proposed, not yet executed

Before every exercise, verify the AWS account, kubeconfig context, namespace, target resource,
blast radius, baseline health, stop condition, and rollback. Namespace isolation alone does not
make a shared production cluster a safe chaos environment. Mutations belong only in the lab.

Use explicit context and namespace on **every** Kubernetes command, for example:

```bash
kubectl --context "$LAB_CONTEXT" -n "$LAB_NAMESPACE" get deploy,rs,pods,svc,ingress -o wide
kubectl --context "$LAB_CONTEXT" -n "$LAB_NAMESPACE" get endpointslices -l kubernetes.io/service-name=demo
kubectl --context "$LAB_CONTEXT" -n "$LAB_NAMESPACE" describe pod "$POD"
kubectl --context "$LAB_CONTEXT" -n "$LAB_NAMESPACE" get events --sort-by=.metadata.creationTimestamp
kubectl --context "$LAB_CONTEXT" -n "$LAB_NAMESPACE" logs "$POD" -c demo --tail=100
kubectl --context "$LAB_CONTEXT" -n "$LAB_NAMESPACE" logs "$POD" -c demo --previous --tail=100
kubectl --context "$LAB_CONTEXT" -n "$LAB_NAMESPACE" rollout status deployment/demo --timeout=90s
```

| Exercise | Distinguishing evidence | Recovery and proof |
| :-- | :-- | :-- |
| Wrong Service selector | Ready Pods but no matching ready EndpointSlices | Restore selector; confirm endpoints and external request |
| Bad image or startup crash | Pod events versus current/previous container logs | Revert approved image; rollout and request succeed |
| Failed readiness | Running container excluded from service traffic | Correct probe/dependency; confirm ready endpoints |
| OOMKilled | Termination reason, limits, observed memory; not just restart count | Correct leak/request/limit; repeat bounded load |
| Failed liveness | Restart timing and probe logs, despite potentially healthy app | Correct probe; verify stable restarts and traffic |
| ALB unhealthy target | Target reason, target port/path, security groups, Pod readiness | Correct the failing layer; target and request healthy |
| IAM or dependency denial | Workload identity and sanitized SDK error; network versus authorization | Restore minimum allowed access; retry exact operation |
| Drain or node loss | Placement, available replicas, eviction budget, pending resources | Recover capacity; measure observed failed requests |
| Drift or replacement | Code, stored mapping, real resource ownership, proposed actions | Approved reconciliation; never blind state removal |

A PDB governs voluntary eviction; it is not protection against node crashes or a substitute for
Deployment rollout settings. HPA scales Pods and needs functioning metrics and resource requests;
node capacity is a separate control loop. See [PDB guidance](https://kubernetes.io/docs/tasks/run-application/configure-pdb/)
and [Service debugging](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/).

For each drill, retain a sanitized incident record: injected fault, hypothesis, command evidence,
impact, mitigation, recovery measurement, cause, prevention, and actual lab cost. A screenshot of
healthy Pods alone is not evidence of incident-handling competence.

## Teardown is an acceptance test

Expiry tags and a CI `always()` block are useful but are **not** spending caps. A failed runner,
lost permission, or stuck controller can leave charges running. Before approving EKS, require
an independent bounded cleanup/alert path restricted to the exact sandbox account, environment,
state, and resource allowlist; it must not have production-delete authority.

Stop GitOps reconciliation before intentionally removing lab workloads. While controllers still
run, remove lab Ingress and load-balancer Services and wait for their AWS resources to disappear.
Then remove lab node groups/cluster, NAT, addresses and disposable volumes in the reviewed order.
Do not delete the remote state bucket, audit records, or intentional retention foundations.

Verify absence through read-only AWS inventory, not only a green Terraform exit. Record retained
ECR images, logs, snapshots, state and any orphaned volumes separately. Recheck delayed billing.
EKS deletion without ingress cleanup can leave ALBs behind; see [AWS teardown guidance](https://docs.aws.amazon.com/eks/latest/userguide/delete-cluster.html).

## Truthful portfolio evidence

Implemented here: offline cost modelling, conservative plan triage, synthetic regression tests,
and an evidence-labelled roadmap. These do not establish deployed EKS, cost savings, tested
production recovery, production HA, or GitOps operations. Promote each claim only after its
corresponding deployment, drill, or billing evidence exists.
