# Current state and evidence

[System overview](../README.md) · [Design decisions](decisions.md)

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
application-specific corrections. Its latest heading date is not a fresh inventory. In this
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
| Current routing, instance sizing, schedules, and resource totals | Read-only AWS/Cloudflare inventory against application origins and the operations AWS map | No fresh fleet counts, instance-size claims, or schedule-health guarantees here |
| Current cost | Whole-account billing over a stated period, separating serving, operations, CI, and retained resources | Earlier serving-core and scheduled-total estimates are historical; no current monthly bill is asserted |
| Terraform drift | Current state reconciliation and reviewed plan under the infrastructure runbook | Keep the documented live-automation hold until its owner resolves it |
| Live deployment trust and grants | Read deployed IAM trust/resource policies and CodeConnections installation scope against the inspected OIDC/runner declarations | The identity diagram describes the mechanism and source configuration, not a fresh least-privilege audit |
| Backup recovery | Recent dump/snapshot evidence and an isolated restore exercise with recorded results | Backup configuration does not establish a recovery objective |
| Portal GitHub credential migration and owner onboarding | Runtime configuration and completed handoff evidence | Adapter capability is documented without declaring rollout complete |
| Client hosting details beyond the Showers example | Each site's source workflow, resource registry, tenant mapping and live preview/public checks | The concrete Showers pipeline is documented; no universal cache, rollback, preview-access or completed-onboarding guarantee |

Use the [application guides](../README.md#follow-a-path) for behavior, and this page for
verification scope. Avoid copying changing inventory or billing numbers into every diagram.
