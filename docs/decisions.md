# Decision log

Short ADR-style entries. Each is the *why* behind a box on the diagram.

## 1. Re-imagine for scale-to-zero instead of lifting the VPS

A container-for-container port of the ~27-service Hetzner box priced at $200–700/mo. The
$100 ceiling forced a redesign: everything request-driven became serverless, and one small
Graviton instance absorbed only what cannot idle. Result: a roughly $50/month serving core.
The separately scheduled operations box brings the expected business-account total to roughly
$90-95/month; the distinction is intentional and public.

## 2. One Postgres on an EC2 anchor, not RDS

Seven Postgres containers became one instance with many databases (~12 GB total). RDS +
ElastiCache for the same shape starts around $60/mo before storage; Aurora Serverless v2 was
evaluated and rejected because an always-on daemon defeats its scale-down. Anchor compute is
about $25/month before EBS and IPv4. Nightly S3 dumps and daily EBS snapshots are configured;
backup freshness and restore verification remain open checks.

## 3. Cloudflare for DNS, Route 53 only for health checks

Cloudflare provides DNSSEC and email routing at no cost, and cutover between providers is a single
CNAME swap with TTL-limited rollback. Private S3 origins are protected by CloudFront Origin Access
Control, not by the DNS provider. No Route 53 hosted zones exist; Route 53 health checks are used
because they integrate with CloudWatch alarms directly.

## 4. HTTP API Gateway instead of an ALB or Lambda Function URLs

An ALB is ~$18/mo idle. HTTP APIs are pay-per-request, give CORS and stage throttling for
free, and replaced Function URLs after those returned 403 on every request despite a correct
public policy.

## 5. No NAT Gateway

~$32/mo idle. The anchor sits in the public subnet and masquerades for the private Lambda
subnets. (Lesson: the MASQUERADE rule must be persisted as a systemd unit, or pollers silently
fail after the next reboot.)

## 6. arm64 everywhere

Both EC2 instances and every Lambda are Graviton. Production container images are built
`--platform linux/arm64` in CI. The one x86 Lambda that remained was migrated with Lambda Web
Adapter and got ~50 ms edge-cached HTML as part of the same change. Browser-heavy CI can still
choose a disposable x86 runner image without changing production architecture.

## 7. The client editor runs on the anchor, not on Lambda

`app.raizhost.com` holds authenticated drafts, uploads, preview state, and publish history. It ran
on a container-image Lambda for a while, but a stateful app on ephemeral compute kept breaking in
quiet ways. It now runs as a Docker container on the anchor behind CloudFront, deployed through SSM
with health-gated auto-rollback. The Lambda rollback path was retired.

The product architecture changed again on 2026-08-17: the hand-built client site remains the
product, and the editor changes only fields exposed by the site's content contract. Publish creates
a source commit; the client site's own workflow builds and deploys it. The legacy page-builder path
is not the client delivery model.

## 8. CloudWatch over self-hosted observability

Prometheus, Grafana, Loki and Tempo cost more to keep warm than the workloads they watched.
Lambda, API Gateway and CloudFront emit metrics natively; a handful of alarms and Route 53
health checks feed one SNS topic. Custom dashboards were the price.

## 9. Resend for email after SES stayed sandboxed

A new AWS account starts SES in sandbox; the production-access request was denied. Client
contact forms are load-bearing, so transactional mail moved to Resend. SES identities remain
but carry nothing.

## 10. Declared infrastructure, gated scripts for the daily path

The original core has roughly 330 Terraform declarations with per-account backends and an
`allowed_account_ids` guard. That is not the same as claiming the current live account is fully
reconciled: the last known plan included destructive DNS drift. Terraform CI is therefore
static-only until H8 closes. The ephemeral runner factory is intentionally CloudFormation-managed.

Per-client go-lives are repetitive and time-sensitive, so they run through idempotent Node scripts
that plan by default and require `--execute` (which the operations guard intercepts for approval).
Each run emits a `terraformImport` map for later adoption after state is reconciled.

## 11. Budget alarms before anything that can spend

Two AWS Budgets at the $100 ceiling were the first resources created. The one time the bill
doubled (an ops box hand-launched outside Terraform, running 24/7), the alarm is what caught it.
The CodeBuild runner layer adds a separate $10/month alert budget; it is alerting, not a kill switch.

## 12. Static sites are the product

Clients get a hand-built static site, not a CMS. It is faster, has no plugin surface to
exploit, and is cheaper to host: a client site is an S3 bucket, a distribution, a certificate,
a health check and an alarm. The client editor commits bounded content changes to the site's
repository; its workflow deploys to S3 and CloudFront. Git history is the version history.

## 13. Ephemeral CodeBuild runners for the client editor repository

GitHub-hosted runner billing blocked app releases on 2026-08-27/28. Three alternatives were
evaluated: an always-on EC2 runner, a custom EC2/JIT autoscaler, and CodeBuild-hosted GitHub Actions
runners. CodeBuild won because every job gets a fresh environment that terminates immediately,
with no idle fleet or autoscaler to operate.

Each repository gets its own project, actor/workflow allowlists, a concurrency ceiling, and 14-day
logs. The runner role can fetch only the selected GitHub App connection and write its own logs. It
cannot deploy; production access still requires the existing repository/ref-scoped OIDC role.
`raizhost-app` moved first and produced step-bearing CI and deploy runs on 2026-08-30. Other trust
domains move separately.

## 14. Terraform CI is static-only until production drift is reconciled

The infrastructure repository used to plan with live credentials and auto-apply on merges to
`main`, despite placeholder business configuration and a known plan containing live DNS destroys.
Moving that job to a more reliable runner would have increased risk. On 2026-08-30 the workflow was
changed to formatting, backend-free validation, scanners, and runner-factory tests only. It has no
AWS identity, live plan, or apply path, and a repository assertion prevents those from silently
returning while H8 is open.

## 15. Retain Straindex data, disable the workload

Straindex was consuming database connections without current product value. Its two Lambda
functions are retained with reserved concurrency zero, and its database refuses new connections.
No data or AWS resource was deleted. That makes the rollback explicit while keeping the disabled
workload out of the serving architecture; inventory counts still include its retained functions.
