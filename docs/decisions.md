# Decision log

Short ADR-style entries. Each is the *why* behind a box on the diagram.

## 1. Re-imagine for scale-to-zero instead of lifting the VPS

A container-for-container port of the ~27-service Hetzner box priced at $200–700/mo. The
$100 ceiling forced a redesign: everything request-driven became serverless, and one small
Graviton instance absorbed only what cannot idle. Result: ~$50/mo core platform.

## 2. One Postgres on an EC2 anchor, not RDS

Seven Postgres containers became one instance with many databases (~12 GB total). RDS +
ElastiCache for the same shape starts around $60/mo before storage; Aurora Serverless v2 was
evaluated and rejected because an always-on daemon defeats its scale-down. The anchor with
PgBouncer is ~$25 all-in and is backed up nightly to S3 plus daily EBS snapshots.

## 3. Cloudflare for DNS, Route 53 only for health checks

Cloudflare provides DNSSEC, email routing, and origin hiding at no cost, and cutover between
providers is a single CNAME swap with instant rollback. No Route 53 hosted zones exist; Route
53 health checks are used because they integrate with CloudWatch alarms directly.

## 4. HTTP API Gateway instead of an ALB or Lambda Function URLs

An ALB is ~$18/mo idle. HTTP APIs are pay-per-request, give CORS and stage throttling for
free, and replaced Function URLs after those returned 403 on every request despite a correct
public policy.

## 5. No NAT Gateway

~$32/mo idle. The anchor sits in the public subnet and masquerades for the private Lambda
subnets. (Lesson: the MASQUERADE rule must be persisted as a systemd unit, or pollers silently
fail after the next reboot.)

## 6. arm64 everywhere

Both EC2 instances and every Lambda are Graviton. Container images are built `--platform
linux/arm64` in CI. The one x86 Lambda that remained was migrated with Lambda Web Adapter and
got ~50 ms edge-cached HTML as part of the same change.

## 7. The portal runs on the anchor, not on Lambda

`app.raizhost.com` uploads files, runs background site builds, and publishes to S3. It ran on
a container-image Lambda for a while, but a stateful app on ephemeral compute kept breaking in
quiet ways. It now runs as a Docker container on the anchor behind the same CloudFront
distribution, deployed via SSM with health-gated auto-rollback. The Lambda stayed as a
one-flip rollback for a week, then was retired.

## 8. CloudWatch over self-hosted observability

Prometheus, Grafana, Loki and Tempo cost more to keep warm than the workloads they watched.
Lambda, API Gateway and CloudFront emit metrics natively; a handful of alarms and Route 53
health checks feed one SNS topic. Custom dashboards were the price.

## 9. Resend for email after SES stayed sandboxed

A new AWS account starts SES in sandbox; the production-access request was denied. Client
contact forms are load-bearing, so transactional mail moved to Resend. SES identities remain
but carry nothing.

## 10. Terraform for the platform, gated scripts for the daily path

~330 resources live in Terraform with per-account backends and an `allowed_account_ids` guard.
Per-client go-lives are repetitive and time-sensitive, so they run through idempotent Node
scripts that plan by default and require `--execute` (which the operations guard intercepts
for approval). Each run emits a `terraformImport` map so nothing stays permanently outside
state.

## 11. Budget alarms before anything that can spend

Two AWS Budgets at the $100 ceiling were the first resources created. The one time the bill
doubled (an ops box hand-launched outside Terraform, running 24/7), the alarm is what caught it.

## 12. Static sites are the product

Clients get a hand-built static site, not a CMS. It is faster, has no plugin surface to
exploit, and is cheaper to host — a client site is an S3 bucket, a distribution, a
certificate, a health check and an alarm. The client edits content through the portal, which
publishes to S3; git history is the version history.
