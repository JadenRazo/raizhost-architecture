# Diagram evidence and refresh contract

[System overview](../README.md) · [Dated history](current-state.md) · [Diagram sources](../diagrams/README.md)

**Checked October 11, 2026, 00:55–01:07 UTC.** The refresh compared selected repository
revisions, workflow source, scoped AWS configuration and public health responses.
The same-day cloud audit supplied the billing receipts used by the cloud guide.
This refresh made no infrastructure, deployment, customer-content or billing changes.
Earlier measurements keep their original dates; this is not an all-account audit.

## What changed in the explanation

- The portal route now includes the deployed HTTPS ALB and its private HTTP hop
  to one anchor. Two ALB zones do not mean two application or database replicas.
- Marketing deploys on `live` pushes, with an optional approved exact-SHA dispatch
  on that branch. It checks that the selected commit belongs to `live` history.
- Backup observation uses an EventBridge **scheduled rule**, distinct from the
  Scheduler service used by tracker pollers. Its healthy alarms do not prove restoration.
- The operations observation policy exists, but AdministratorAccess remains attached.
- The overview has a narrow layout generated from the same application nodes and
  edges. New origin, failure-domain and backup diagrams have desktop/phone variants.

## Diagram-to-source map

| Diagram | Owning implementation or observation | Evidence boundary |
| :-- | :-- | :-- |
| System overview / request routing | CloudFront origins and behaviors; ALB target/transport; application workflows | October 11 source and scoped AWS reads; no full network failure exercise |
| Portal ingress | Infrastructure origin stack/runbook; live listener shape, security groups and target health | One healthy target; function on four behaviors; no fresh forged-header or host-environment test |
| Failure domains | EC2 placement, target registration, route tables, schedules and IAM attachments | Observed configuration plus documented dependencies; no new outage test |
| Code deployment / CI/CD | Marketing `live`, portal `main`, tracker `main` workflow files | Current trigger and SHA-selection logic; no deployment performed by this audit |
| Deployment identity | Workflow OIDC declarations; prior runner/IAM source audit | Role responsibilities; deploy-role trust policies and CodeConnections installation scope not re-audited |
| Owner publication / portal authorization / publication status | Portal content service, GitHub adapter and content route authorization | Current source; no owner mutation or customer publication invoked |
| Preview versus live / client CI/CD | Showers Deploy workflow and portal branch adapter | Concrete Showers `main`/`preview` example; marketing and portfolio use their configured `live` branches |
| Portal rollout | Portal Deploy workflow and anchor rollout script | Current image/health/rollback conditions; no fresh rollback drill |
| Tracker data | Current registry, collector, database-access and workflow source; live edge routes and all three schedule intervals | Topology and 10-minute / 30-minute / 2-hour schedules verified; no independent provider-freshness or parser-output audit |
| Client provisioning | Current operations provisioning script; prior handoff audit | Plan/certificate/resource sequence inspected; no provisioning or tenant setup performed |
| Backup monitoring | Recovery-monitoring stack, enabled scheduled rule and live alarm configuration | Both alarms OK with actions enabled and missing data breaching; no new restore or inbox test |

Selected source revisions are preserved in the private audit with file hashes.
The publication includes only non-secret behavior. Source was read from marketing
and portfolio `live`, and portal, tracker, Showers and infrastructure `main`.
Portal health reported database up and matched its inspected source revision;
the latest successful portal Deploy run matched it too. Tracker health reported
database up; that endpoint does not identify an exact deployed source revision.

The four main-branch protection and ruleset reads still match the
[CI/CD table](ci-cd.md#2-apply-the-actual-merge-gates). Marketing's `production`
environment still has no configured reviewer, timer or branch protection.
Marketing `live` branch protection was not inspected: the workflow's release-ref
and ancestry checks do not establish whether a particular actor may push there.

## Keep the diagrams accurate

Use layered views: the overview locates the application, a journey explains one
action, and origin/recovery diagrams expose shared dependencies. A single
inventory poster would obscure these differences; application journeys alone
would omit the operating and recovery boundaries.

After changing a route, workflow, publication contract or recovery control:

1. Read the owning source at a fixed revision and inspect affected live settings.
2. Update the diagram source and companion explanation together. Preserve dated
   historical evidence and label anything proposed or unverified.
3. Regenerate changed assets; run source/output, link, privacy, geometry and
   Markdown checks. Inspect the actual document at desktop and phone widths.
4. Record what passed, what was not exercised, and the delivery state. A green
   documentation check validates artifacts, not deployed infrastructure.

Review volatile observations by **November 11, 2026**, or immediately after an
affected change. Refresh the relevant row; do not relabel the entire repository
as freshly verified after a narrow check.
