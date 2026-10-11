# Current state and evidence

[System overview](../README.md) · [Design decisions](decisions.md)

## Cloud-control reconciliation — October 11, 2026

The October 11 batch reconciled Terraform with live resources, added bounded
logging and alerts, extended backups, and retired unused portfolio messaging.
Earlier dated observations below retain their original scope.
[Cloud operations](cloud-operations.md) explains the current controls and limits.

Implementation merged after passing static CI: [infrastructure PR 15](https://github.com/JadenRazo/aws-infra/pull/15),
[portfolio retirement](https://github.com/JadenRazo/Project-Website/pull/80) and
[retirement merge](https://github.com/JadenRazo/Project-Website/pull/81).
The earlier accepted HTTPS origin is in
[infrastructure PR 12](https://github.com/JadenRazo/aws-infra/pull/12), with trusted
viewer-IP handling in [portal PR 108](https://github.com/JadenRazo/raizhost-app/pull/108).
Private repository links may require access. Detailed CLI, plan, review and restore
receipts remain in the operations cloud-controls audit; private resource and
release identifiers are not reproduced here.

| Verified observation | Scope and limit |
| :-- | :-- |
| Root normal Terraform plan at 15:53:35 UTC: exit 0, no actions, after reviewed state-only refresh and sensitivity metadata | State/configuration reconciliation verified; CI remains static only, no automatic apply |
| Read access to all three Cloudflare zones available | DNS records and state ownership unchanged |
| Portfolio messaging retirement deployed | Page/navigation, WebSocket origin/behavior, 8082 ingress and dedicated inline ECR policy removed; shared data and image archives retained |
| Existing multi-region CloudTrail adds 14-day CloudWatch logs and root-use, privileged-IAM and trail-change alerts | Existing S3 audit archive retained; no immutable or independent archive |
| ALB access logs enabled and delivered to private encrypted storage, seven-day retention | Actual delivery observed; production endpoint healthy |
| Host disk/memory/heartbeat telemetry, Lambda-error alarms, 11 operational and three security alarm actions enabled | SNS notifications added; existing EC2 reboot/recover actions preserved |
| Real telemetry-only pause entered ALARM in 210.6 seconds and returned to OK after resume | Applications untouched; separate CloudWatch-to-SNS action succeeded, human inbox receipt unconfirmed |
| Both broad budgets now use $250 gross; $10 CodeBuild filter corrected | Original CodeBuild dates and all settings/subscribers verified after protected CloudFormation update; notifications are not spending caps |
| October 1–10 gross usage $39.59; October forecast $129.86, read October 11 | Estimated billing signals, not the final monthly bill |
| Planning allowance $211.80 plus $25 reserve = $236.80 | Conservative allowance under the $250 ceiling, not measured spend or a hard cap |
| Operations root encrypted, 180 GiB; daily 08:00 UTC DLM retaining three installed | First scheduled snapshot expected October 12; snapshot restoration not demonstrated |
| Operations logical backup completed; exact-version archive passed two-database restore and config checks at 18:25 UTC | SQLite integrity, PostgreSQL restore/`pg_amcheck`, config identity and cleanup passed before enabling daily 10:30 UTC timer; AIOStreams/ZeroDay application startup not tested |
| Independent backup monitor extended to database, media and operations streams; all three healthy | All three alarms are OK with actions enabled; a fresh dedicated Terraform plan has no changes |
| Retention installed: operations current 30/noncurrent seven days; anchor database and actual media current 365, Glacier transition at 30, noncurrent 30 days | Permanent archive preserved; retention alone is not recovery |
| Legacy portal S3 uploads versioned; current objects indefinite/noncurrent 365 days | Actual portal media remains Docker-local and is archived separately |
| Real portal backup restore passed in 8m43s; cleanup finished in 8m46s | Ten connectable databases/extensions and empty media verified; login, draft save and local Git publication passed in isolated resources |
| Database and media receipts were 9h56m and 7h56m old at drill start | Observed recovery points, not guarantees; daily backups can lose roughly a day when successful |
| Both hosts remain in one AZ; anchor data remains on root, attached 60 GiB unused | No host, AZ or regional failover added |

### Remaining scope

First scheduled operations-root snapshot and human notification inbox receipt
remain unverified. The restore tests do not establish customer-site deployment,
PITR, disabled retained-database recovery, snapshot restoration or infrastructure
failover. The October 8 **7m11s database-only restore** below remains historical
evidence; it is distinct from the October 11 application rehearsal.

The owner selected recommendations 4–8. Operations AdministratorAccess removal,
failing portfolio Lambda repairs and independently protected backups (1–3) remain
excluded and unresolved. IAM Access Analyzer findings remain open. Scoped backup
permissions do not reduce an attached administrator policy.

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
| Portal health at 01:08 UTC reports database up and the recorded private release revision | The previously accepted release remains healthy; no app release occurred in this increment |
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
| Owner portal runs the recorded private release revision | CI and Deploy passed; public/host health report exact SHA and DB up; Node 22.23.3, Next 15.5.27, Sharp 0.35.5 and native JPEG/WebP/AVIF checks verified |
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

The final application CI and Deploy runs completed successfully; deployment finished at 20:59:15 UTC. Public health was
checked at 21:44 UTC, followed by host/native-library and backup-preservation checks.
Detailed workflow identifiers remain in the private operations record. The earlier Docker Hub
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
| `JadenRazo/raizhost` | Recorded in private source evidence | Production workflow; quote/CRM clients and function code |
| `JadenRazo/raizhost-app` | Recorded in private source evidence | Content contract and source adapter; draft/publish services; auth; anchor/CI/deploy files |
| [JadenRazo/llm-tracker](https://github.com/JadenRazo/llm-tracker/tree/457f1f14544f4de3ebdfa6115a3b8537b37baea2) | `457f1f14544f4de3ebdfa6115a3b8537b37baea2` | Registry, pollers, schema, page/cache configuration, health and deploy workflow |
| `JadenRazo/aws-infra` | Recorded in private source evidence | Tracker edge/VPC declarations, shared networking, Terraform CI hold |
| `JadenRazo/showersautodetail` | Recorded in private source evidence | Client Deploy workflow, package commands, content import, preview base and indexing |

Tracker source is public. Other evidence includes private repositories; this page publishes
the relevant behavior and public tracker revision without exposing private release metadata, resource identifiers or credentials.

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
| Marketing | Recorded private deploy run, success on 2026-09-06, matching the selected SHA; public homepage fetched on 2026-09-12 | Recorded release and reachable public content; no live build-SHA endpoint was used |
| Owner portal | Recorded private deploy run, success on 2026-09-05; health at 2026-09-12 04:06 UTC reported `ok: true`, `db: up`, and the selected SHA | Exact app revision and database reachability at that check |
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
| Recorded preview content commit and successful workflow, 2026-09-05 | A content-only push to `preview` completed all workflow steps, including S3 sync, invalidation request and HTTP smoke |
| Recorded live content commit and successful workflow, 2026-09-05 | A separate content-only push to `main` completed the same workflow's live target |
| Both commits modified only `raizhost/content.json` and share the recorded parent revision | The observed live update was a separate commit, not a merge of the preview commit |
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
| Infrastructure maintenance | Review future live changes against a fresh plan and the owning state | October 11 root reconciliation and budget date/subscriber verification are complete; CI remains static only |
| Live deployment trust and grants | Read deployed IAM trust/resource policies and CodeConnections installation scope against the inspected OIDC/runner declarations | The identity diagram describes the mechanism and source configuration, not a fresh least-privilege audit |
| Remaining recovery work | Observe the first operations DLM snapshot; prove snapshot/PITR, retained disabled-data and host/AZ/region recovery separately | October 11 portal application and operations database/configuration restores passed within their stated scope |
| Portal GitHub credential migration and owner onboarding | Runtime configuration and completed handoff evidence | Adapter capability is documented without declaring rollout complete |
| Client hosting details beyond the Showers example | Each site's source workflow, resource registry, tenant mapping and live preview/public checks | The concrete Showers pipeline is documented; no universal cache, rollback, preview-access or completed-onboarding guarantee |

Use the [application guides](../README.md#follow-a-path) for behavior, and this page for
verification scope. Avoid copying changing inventory or billing numbers into every diagram.
