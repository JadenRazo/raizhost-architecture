# Current state

**Reconciled:** 2026-08-30 against the RaizHost operations canon, recent infrastructure and
application history, and step-bearing GitHub workflow runs. Re-check after any infrastructure
change or by 2026-09-30.

This page separates the platform that is serving traffic now from transition work. Counts below
include retained resources even when a workload is deliberately disabled. They do not imply ten
client websites: Showers Auto Detail is the first live client site; the other public surfaces are
RaizHost, demo, status, portfolio, and application infrastructure.

## Serving now

| Area | Current state |
|:--|:--|
| Edge | 10 CloudFront distributions behind Cloudflare DNS. Static origins use S3 with Origin Access Control. |
| Request compute | 17 arm64 Lambda functions and 9 HTTP APIs, plus one always-on `t4g.medium` anchor. Some functions are schedule-driven rather than HTTP-facing. |
| Stateful services | The anchor runs Postgres, PgBouncer, Redis, NAT for private Lambda subnets, and the `app.raizhost.com` container. |
| Data | 15 S3 buckets, 2 on-demand DynamoDB tables, Secrets Manager, versioned contract storage, and EBS snapshots. |
| Scheduling | 11 EventBridge schedules run pollers/jobs and the ops-box start/stop window. |
| Client editing | The live editor commits allowed content changes to the client's source repository; that site's workflow builds and deploys to S3. Showers is the first integrated tenant. |
| Mail | Resend carries transactional mail. SES remains non-production and is not load-bearing. |
| CI for the editor | `raizhost-app` jobs run in fresh CodeBuild-hosted GitHub Actions environments and then terminate. Deploy jobs separately assume the existing repository-scoped OIDC role. |

The inventory counts reconcile the last full map with two recorded retirements: the old
`raizhost-app` Lambda/API path was deleted on 2026-08-05, and the unused marketing API plus its empty
DynamoDB table were deleted on 2026-08-19. Straindex resources still exist but have concurrency and
database connections disabled, so they remain in the inventory without serving requests.

## Active transition work

- **Client editor rollout.** The editor is live and production-proven through Git commit, preview,
  workflow, S3, and CloudFront. Owner onboarding and replacing the editor's interim repository token
  with its own narrowly scoped GitHub App remain operational handoff work.
- **Runner migration.** A repository-scoped CodeBuild runner factory became live for
  `raizhost-app` on 2026-08-30 after GitHub-hosted runner billing blocked releases on 2026-08-27/28.
  Other repositories are onboarded deliberately by trust domain; this is not yet a blanket runner
  replacement.
- **Terraform reconciliation.** The core platform has roughly 330 Terraform declarations, but live
  state and configuration are not reconciled. The last known plan included destructive DNS drift.
  As of 2026-08-30, infrastructure CI is intentionally static-only: formatting, validation, security
  scans, and factory tests run with no AWS identity, live plan, or automatic apply.
- **IaC ownership.** Terraform owns the original core, CloudFormation owns the ephemeral runner
  factory, and gated provisioning scripts emit import maps for new client resources. A small set of
  recorded CLI-applied changes still waits for Terraform reconciliation.
- **Legacy retirement.** The Hetzner VPS remains a read-only rollback shadow. Straindex is retained
  but operationally disabled. Neither should be described as an active production dependency.

## Cost truth

The old **“about $50/month”** headline described only the serving core. The last billed run-rate
measurement was about $106/month with the ops box running continuously. Its 00:00-07:00 PT stop
window is expected to put the business-account total near $90-95/month: roughly $50 for the core
and roughly $40 for the scheduled ops box.

That post-schedule estimate has not yet been re-measured across a clean billing cycle, so it is a
planning figure, not an invoice claim. Two account budgets alert at the $100 ceiling; the new
CodeBuild runner layer has a separate $10/month alert budget and no idle runner fleet.

## Verification debt kept visible

- Re-run the full read-only AWS inventory and Cost Explorer sweep; the semantic reconciliation is
  current, but several base counts still originate in the older full inventory pass.
- Reconcile Terraform to a reviewed no-op before restoring live plan capability. Automatic apply on
  merge is intentionally retired.
- Verify nightly Postgres backup freshness and a restore path; the job is configured, but the older
  missing-dump check remains open.
- Finish the editor-specific GitHub App migration and the first owner handoff.

Stable rationale lives in [the decision log](decisions.md). Request, deployment, and client lifecycle
details live in the other documents in this directory.
