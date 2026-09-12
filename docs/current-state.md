# Current state and evidence

[System overview](../README.md) · [Design decisions](decisions.md)

**Documentation check: 2026-09-12 UTC.** This is a scoped record for RaizHost's website,
owner portal, tracker, and client delivery. Recheck the affected rows after a release or
topology change; review this snapshot by **2026-10-12**.

Three evidence levels matter: source describes implementation, a successful workflow
records a release, and a live response reports what an endpoint observed at a particular
time. None alone is a full AWS inventory or a recovery test.

## Application revisions inspected

| Repository | Selected revision | Source used |
| :-- | :-- | :-- |
| `JadenRazo/raizhost` | `03c8bcc407f8b7a1a7b9bbcb1767e42fda7d88ca` | Production workflow; quote/CRM clients and function code |
| `JadenRazo/raizhost-app` | `f3a405f7ddf07463f5436e699cdf2293225cba18` | Content contract and source adapter; draft/publish services; auth; anchor/CI/deploy files |
| [JadenRazo/llm-tracker](https://github.com/JadenRazo/llm-tracker/tree/457f1f14544f4de3ebdfa6115a3b8537b37baea2) | `457f1f14544f4de3ebdfa6115a3b8537b37baea2` | Registry, pollers, schema, page/cache configuration, health and deploy workflow |
| `JadenRazo/aws-infra` | `f19c4b2f9c703e4a9125cf605b48aca31f062826` | Tracker edge/VPC declarations, shared networking, Terraform CI hold |

Tracker source is public. Other evidence includes private repositories; this page publishes
the relevant behavior and revisions without exposing their resource identifiers or credentials.

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
| Backup recovery | Recent dump/snapshot evidence and an isolated restore exercise with recorded results | Backup configuration does not establish a recovery objective |
| Portal GitHub credential migration and owner onboarding | Runtime configuration and completed handoff evidence | Adapter capability is documented without declaring rollout complete |
| Client hosting details | Each site's source workflow, resource registry, and live preview/public checks | No universal cache, rollback, or preview-access guarantee |

Use the [application guides](../README.md#follow-a-path) for behavior, and this page for
verification scope. Avoid copying changing inventory or billing numbers into every diagram.
