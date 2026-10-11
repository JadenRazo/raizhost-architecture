# Current state and evidence

[System overview](../README.md) · [Design decisions](decisions.md)

## Diagram and origin refresh — October 11, 2026

[The scoped evidence record](diagram-evidence.md) supersedes the older HTTP-origin
and release-trigger descriptions. CloudFront now uses an HTTPS ALB origin; the
ALB has one healthy anchor target and forwards to it over private HTTP. All four
portal behaviors have the viewer function. Both EC2 hosts remain in one zone.

The portal's public health and latest successful Deploy matched the inspected
source revision with database up. Marketing source on `live` releases branch
pushes or an approved dispatch with release-history validation. The operations
role still has AdministratorAccess alongside its observation and SSM policies.
The backup scheduled rule is enabled; both alarms report OK with actions enabled.
The same-day billing read reports $39.59 estimated gross usage for October 1–10
and a $130.94 forecast, updated October 10 at 22:28 UTC; the gross budget remains
$250. These supersede the October 9 amounts only for the corresponding cost view.

These are configuration, source and endpoint observations. No new restore,
rollback, owner publication, notification delivery or origin attack test ran.
The entries below preserve what was known at their stated times; their
then-pending TLS work is no longer the current origin topology.

## Backup-monitoring follow-up — October 9, 2026

The second accepted increment adds independent backup monitoring. This section
updates that control and the budget; the October 8 and September records below
retain their original scope and dates. Serving and deployment diagrams still
describe the same application paths.

| Observation | What it establishes |
| :-- | :-- |
| Deployed monitor code matches the reviewed package; both database/media checks healthy | Completion receipts and archive metadata are consistent and fresh at the read, not proof of newly restored data |
| Two actual EventBridge invocations observed; both health alarms OK with actions enabled | The installed 15-minute schedule reports outside the anchor/VPC and is connected to the existing operator topic |
| Separate alarm exercised missing, healthy and explicit-failure data with no actions, then was removed | Failure/recovery and missing-reporting detection were observed without synthetic notifications or backup changes |
| Dedicated monitoring Terraform state returns no changes | Deployed resources and source agree; legacy root remains held |
| Gross budget forecast $124.34; estimated month-to-date $29.10 | October 9 read of budget data updated October 8 at 23:40 UTC; the $250 ceiling and $25 design reserve remain |
| Portal health at 01:08 UTC reports database up and `9f614b8549d76d9163dc95fc953c52001079278d` | The previously accepted release remains healthy; no app release occurred in this increment |
| HTTPS origin/client-identity and machine-IAM changes have passing preparation checks and CI, but no independent review verdict | Prepared only: current HTTP origin and operations AdministratorAccess remain, with explicit follow-up ownership |

[Cloud operations](cloud-operations.md) records the monitoring path, $3/month
allowance, shared-concurrency limit, recovery boundaries and source PRs. No new
application, AZ or regional failover capability is claimed.

## Cloud follow-up — October 8, 2026

AWS CLI and bounded host/SQL inspection established the baseline, followed by
reviewed, authorized infrastructure changes. [Cloud operations](cloud-operations.md) is the current authority
for the facts in this table; the September application and release evidence below
remains a dated record, not a new check of every application workflow.

| Observation | What it establishes |
| :-- | :-- |
| September gross AWS cost excluding credits/refunds: $127.32 | A measured monthly baseline, not the credit-adjusted bill or a per-client allocation |
| October forecast $120.78 and estimated month-to-date $25.22 | Point-in-time budget/billing signals; not the completed October bill |
| Anchor and operations host share one Availability Zone | Current EC2 topology does not provide AZ failover |
| Operations host still carries production dependencies | Scheduling it off is not yet an accepted cost saving |
| New backup scripts are installed; exact S3 versions passed checksum/content checks | Archive completion and media coverage verified; active media is empty |
| Ten connectable databases restored into isolated PostgreSQL 17.11 | Loading 6m04s; full rehearsal 7m11s; extension/index checks and editor integrity pass; no application failover claim |
| PostgreSQL 17.10; retained inactive data is outside logical-dump coverage | Migration and recovery must account for retained data separately |
| Owner portal runs `9f614b8549d76d9163dc95fc953c52001079278d` | CI and Deploy passed; public/host health report exact SHA and DB up; Node 22.23.3, Next 15.5.27, Sharp 0.35.5 and native JPEG/WebP/AVIF checks verified |
| Isolated foundation stack: 11 additions applied, zero replacements/deletions; subsequent no-change plan | Code and live controls agree within this stack; legacy root remains held |
| CloudTrail delivered logs; 2/2 digests and 26/26 log files validated | Completed first-hour window, with private/versioned audit storage; not immutable or organization-wide logging |
| Regional EBS encryption default and external-access analysis enabled | Default protects new regional volumes; 12 initial non-public trust findings inspected and left active for review |
| Gross budget $250; 80/90/100% actual and 90% forecast alerts | Preserved recipients and Credit/Refund exclusions; notifications do not enforce a hard cap |
| CRM and quotes tables deletion-protected, 35-day PITR retained | Live protection and owning bootstrap sources reconciled; item deletion and restores remain separate concerns |

Foundation, backup and table-source changes passed independent review and relevant
tests. The live database was not a restoration target: the drill used an isolated,
disposable copy, which was removed after verification. Application image-processing
patches and a pinned ECR Public build image passed deployment and final live checks.
DNS, serving topology and production database placement were not
changed. Future failover work follows the gates in the cloud-operations guide.

The final application [CI run](https://github.com/JadenRazo/raizhost-app/actions/runs/37841355709)
and [Deploy run](https://github.com/JadenRazo/raizhost-app/actions/runs/37843300310)
completed successfully; deployment finished at 20:59:15 UTC. Public health was
checked at 21:44 UTC, followed by host/native-library and backup-preservation checks.
Those workflow links may require private-repository access. The earlier Docker Hub
rate-limit failure stopped before image publication; the pinned ECR Public source
resolved it through a new tested release.

## September application audit

**Documentation check: 2026-09-12 UTC.** This is a scoped record for RaizHost's website,
owner portal, tracker, and client delivery. Recheck the affected rows after a release or
topology change; review this snapshot by **2026-10-12**.

Source describes implementation, a successful workflow records a release, live GitHub
settings establish configured gates, and a live response reports what an endpoint observed
at a particular time. None alone is a full AWS inventory or a recovery test.

## Application revisions inspected

| Repository | Selected revision | Source used |
| :-- | :-- | :-- |
| `JadenRazo/raizhost` | `03c8bcc407f8b7a1a7b9bbcb1767e42fda7d88ca` | Production workflow; quote/CRM clients and function code |
| `JadenRazo/raizhost-app` | `f3a405f7ddf07463f5436e699cdf2293225cba18` | Content contract and source adapter; draft/publish services; auth; anchor/CI/deploy files |
| [JadenRazo/llm-tracker](https://github.com/JadenRazo/llm-tracker/tree/457f1f14544f4de3ebdfa6115a3b8537b37baea2) | `457f1f14544f4de3ebdfa6115a3b8537b37baea2` | Registry, pollers, schema, page/cache configuration, health and deploy workflow |
| `JadenRazo/aws-infra` | `f19c4b2f9c703e4a9125cf605b48aca31f062826` | Tracker edge/VPC declarations, shared networking, Terraform CI hold |
| `JadenRazo/showersautodetail` | `74c8dcacb5cd4f783dd44a39c34af126e2a8624c` | Client Deploy workflow, package commands, content import, preview base and indexing |

Tracker source is public. Other evidence includes private repositories; this page publishes
the relevant behavior and revisions without exposing their resource identifiers or credentials.

## GitHub gate settings

Read on **2026-09-12 UTC** through the authenticated GitHub REST API:

| Read | Result used in the diagrams and guides |
| :-- | :-- |
| `repos/JadenRazo/{repo}/branches/main/protection` for marketing, portal, tracker and infrastructure | Portal requires `build` and `e2e`; tracker requires `Typecheck, lint, build`; both require an up-to-date branch. Marketing and infrastructure have no required status checks configured |
| Approving-review count in those protections | 0 for all four; conversation resolution and administrator enforcement enabled |
| `repos/JadenRazo/{repo}/rules/branches/main` | Empty for all four: no additional active ruleset rules returned |
| `repos/JadenRazo/raizhost/environments/production` | No protection rules; no deployment branch policy |

These settings can change independently of a commit. Recheck them when modifying release
gates. [CI/CD](ci-cd.md) explains the consequences; [authorization](authorization.md)
separates configured checks from operator approval. Workflow source establishes that the
portal and tracker deploy jobs do not declare an environment gate. No GitHub protection
setting or application workflow was changed for this documentation expansion.

## Deployment and live observations

| Surface | Evidence observed | What it establishes |
| :-- | :-- | :-- |
| Marketing | Deploy run `34053315341`, success on 2026-09-06, matching the selected SHA; public homepage fetched on 2026-09-12 | Recorded release and reachable public content; no live build-SHA endpoint was used |
| Owner portal | Deploy run `33999861046`, success on 2026-09-05; health at 2026-09-12 04:06 UTC reported `ok: true`, `db: up`, and the selected SHA | Exact app revision and database reachability at that check |
| Tracker | [Deploy run 34652750204](https://github.com/JadenRazo/llm-tracker/actions/runs/34652750204), success on 2026-09-11, matching the selected SHA | Recorded deployment of the web image and tier bundles |
| Tracker health | At 2026-09-12 04:06 UTC: `ok: true`, `db: up`, 26 sources, no failing or never-run sources; last poll at 04:02:45 UTC | Reported ingestion health at that moment; not an independent per-source cadence audit |

Health evidence came from read-only GETs to [the portal health endpoint](https://app.raizhost.com/api/health)
and [the tracker health endpoint](https://llm.raizhost.com/api/health). These links now return
current responses, which may differ from the dated observations above. No manual poll,
customer content write, or application deployment was performed for this documentation change.

## Owner publication evidence

The [owner walkthrough](owner-publishing.md), [client CI/CD](client-site-cicd.md), and
[status guide](publish-status.md) were traced through portal source and Showers' client
workflow, rather than inferred from the portal's own code-release pipeline.

| Observation | What it establishes |
| :-- | :-- |
| [Preview content commit](https://github.com/JadenRazo/showersautodetail/commit/1fa7201513f5026fc982cf8aac51411d167ef1a4), successful [preview run 33938275730](https://github.com/JadenRazo/showersautodetail/actions/runs/33938275730), 2026-09-05 | A content-only push to `preview` completed all workflow steps, including S3 sync, invalidation request and HTTP smoke |
| [Live content commit](https://github.com/JadenRazo/showersautodetail/commit/74c8dcacb5cd4f783dd44a39c34af126e2a8624c), successful [main run 33942877942](https://github.com/JadenRazo/showersautodetail/actions/runs/33942877942), 2026-09-05 | A separate content-only push to `main` completed the same workflow's live target |
| Both commits modified only `raizhost/content.json` and have parent `d9e78eba9f7d79a0fe6c93aec8906dfb510671ae` | The observed live update was a separate commit, not a merge of the preview commit |
| Showers branch protections read 2026-09-12: main has a PR policy, 0 required approvals, no required status checks and `enforce_admins: false`; preview returns “Branch not protected”. Branch-rules API returns `[]` for both | Direct publication still depends on the source credential's permitted write/bypass scope. This read does not prove that any GitHub App installation can push main |
| Anonymous GETs at approximately 2026-09-12 07:44 UTC: [public root](https://showersautodetail.com/) and [preview root](https://showersautodetail.com/_preview/) both returned 200 | Public output was reachable without a portal session. Preview HTML had `noindex, nofollow`, a production canonical and preview-prefixed URLs; the public root had an indexing directive |

The observed workflow titles identify admin-created content updates. They do not establish
a fresh non-admin owner journey or completed customer onboarding. This documentation audit
did not press Preview/Publish, upload a file, read tenant credentials or change content.
It also did not assert that the served HTML matches every field in either commit. Source
links may require repository access; private resource identifiers remain omitted.

Branch-policy evidence came from `repos/JadenRazo/showersautodetail/branches/{branch}/protection`
and `repos/JadenRazo/showersautodetail/rules/branches/{branch}` for main and preview. No policy
was changed. GitHub documents [PR requirements and administrator exemptions](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches);
a required approval count of zero is not proof of unrestricted direct writes.

Two implementation limits are material: Showers' post-deploy check is an HTTP HEAD request,
not an assertion of the changed page body; and uploads create separate live-branch commits
eligible for its push workflow. The latter is inferred from the adapter and trigger, not
from a newly performed photo upload. These distinctions are explicit in the walkthrough.

## Infrastructure and operations evidence

The operations AWS map contains a mixture of older full inventory reads and later
application-specific corrections. Its latest heading date is not a fresh inventory. In that September
session, the AWS CLI had no active credentials, so a live distribution/routing inventory
could not be completed. Infrastructure diagrams therefore reflect inspected application
source, infrastructure declarations, and recorded corrections; they are not a claim that
every AWS property was freshly read.

The code and records support these paths:

- Static websites use CloudFront and private S3 origins.
- The owner portal runs in Docker on the anchor; its earlier Lambda path was retired.
- Tracker pages use API Gateway/web Lambda, with a separate S3 static-bundle path.
- Scheduled tracker pollers write to Postgres through PgBouncer on the anchor.
- Quote and CRM browser requests call their separate API Gateways and DynamoDB-backed functions.
- Client owner publication commits source; the client repository's workflow publishes files.

Operations use Codex for implementation and fresh Astra medium contexts for independent
review. Applicable runtime permissions and explicit effect authorization govern production
actions. A legacy hook file is not proof that a hook executed in a Codex session.

## Open verification work

| Item | Owning evidence to obtain | Documentation consequence |
| :-- | :-- | :-- |
| Broader routing and account inventory | Extend the October scoped AWS inspection to other-region, learning-account and client details as needed | October host/topology facts above have a stated scope; no universal fleet or schedule guarantee |
| Ongoing cost | Recheck whole-account gross billing after the new controls and CI usage appear | September usage and October forecast above are dated observations; validate the later steady-state target before migration |
| Terraform drift | Current state reconciliation and reviewed plan under the infrastructure runbook | Keep the documented live-automation hold until its owner resolves it |
| Live deployment trust and grants | Read deployed IAM trust/resource policies and CodeConnections installation scope against the inspected OIDC/runner declarations | The identity diagram describes the mechanism and source configuration, not a fresh least-privilege audit |
| Remaining recovery work | Retained disabled-data snapshot restoration, application correctness, PITR and failure drills | The completed logical rehearsal does not establish complete application, AZ or regional recovery |
| Portal GitHub credential migration and owner onboarding | Runtime configuration and completed handoff evidence | Adapter capability is documented without declaring rollout complete |
| Client hosting details beyond the Showers example | Each site's source workflow, resource registry, tenant mapping and live preview/public checks | The concrete Showers pipeline is documented; no universal cache, rollback, preview-access or completed-onboarding guarantee |

Use the [application guides](../README.md#follow-a-path) for behavior, and this page for
verification scope. Avoid copying changing inventory or billing numbers into every diagram.
