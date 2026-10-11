# Cloud operations and staged resilience

[System overview](../README.md) · [Dated evidence](current-state.md) · [Decisions](decisions.md)

**Verified controls: October 11, 2026.** The gross budget is **$250/month across
all AWS workloads**, with $225 planned usage and a $25 reserve. Logging, monitoring,
origin protection and storage controls are live. Operations-host database/configuration recovery and the portal real-backup
restore passed; the daily operations backup timer is enabled.
[The consolidated evidence record](current-state.md#cloud-control-reconciliation--october-11-2026)
records accepted controls, remaining checks and earlier recovery history.

## What runs today

Static sites retain the CloudFront/private-S3 serving path shown in the overview.
Dynamic workloads use API Gateway/Lambda where suitable. The owner portal runs
on a shared EC2 anchor with PostgreSQL, PgBouncer and Redis; private Lambda egress
also depends on that host. An anchor failure can therefore affect editing,
database consumers and external collection together.

The anchor is a Graviton `t4g.medium`; the operations host is `t4g.large` with a
180 GiB encrypted root volume. Both are in one Availability Zone. The operations host still
runs production workloads, so it cannot be scheduled off as a cost optimization
until those dependencies have been moved and verified. Current EC2 topology does
not provide automatic application or database failover across AZs. The anchor's
root still holds its data; its attached 60 GiB volume is unformatted and unused.

Portal requests use CloudFront → authenticated HTTPS ALB origin → anchor container,
with trusted viewer-IP handling. This was accepted before the October 11 batch;
[infrastructure PR 12](https://github.com/JadenRazo/aws-infra/pull/12) records the
origin change. Production endpoint health is verified, separately from recovery.

Portfolio messaging was retired with explicit approval: its page, navigation,
WebSocket origin/behavior, port 8082 ingress and dedicated inline ECR policy were
removed. Shared data and ECR images remain retained.

## Measured cost and the budget gate

| Measurement | USD | Meaning |
| :-- | --: | :-- |
| September gross AWS usage | 127.32 | Historical Cost Explorer read, excluding credits/refunds |
| October 1–10 gross usage | 39.59 | Last read October 11; not a completed monthly bill |
| October forecast | 129.86 | October 11 read; point-in-time forecast |
| Program ceiling | 250.00 | Gross spend across all workloads, including temporary overlap |
| Planned usage target | 225.00 | Leaves a reserve within the ceiling |
| Reserve | 25.00 | Buffer, not an extra allowance |

The program budget alerts at **$200, $225 and $250 actual**, plus **$225 forecast**.
The older $100 budget is now also $250 gross. The $10 CodeBuild budget now filters
the CodeBuild service on a gross basis. Subscribers were preserved. Notifications
are delayed signals, not spending caps.

The current planning allowance is **$211.80**: $165 base, $4.80 root expansion from
other work, $7 monitoring, $3 retention, $5 drill and a conservative $27 for three
full 180 GiB snapshots. Including the $25 reserve gives **$236.80**, below $250.
These are planning allowances, not measured spend or enforceable caps. Recheck
actual billing as logs, snapshots, retention and CI usage appear.

## Deployed controls

| Control | Live verification | Boundary |
| :-- | :-- | :-- |
| Multi-region account CloudTrail | Existing trail now also delivers to CloudWatch with 14-day retention and root-use, privileged-IAM and trail-change alerts | Account trail; no organization trail, paid data events or immutable retention |
| ALB access logs | Enabled; delivery observed in private SSE-S3 storage with seven-day retention | Delivery does not establish application recovery |
| Audit storage | Private, owner-enforced, encrypted and versioned S3; TLS-only client access; 365-day current/noncurrent retention | An administrator can still change AWS controls |
| Terraform state transport | Existing private/versioned state bucket now denies insecure client transport | Root normal plan returned exit 0 with no actions on October 11; CI remains static only, with no automatic apply |
| EBS encryption default | Enabled and read back in the primary region | Applies to newly created regional volumes |
| External-access analyzer | Free account analyzer ACTIVE; 12 initial non-public IAM trust findings inspected against actual role policies | Findings remain active for intended-access and recovery review; no broad archive rules |
| CRM and quote deletion protection | Both tables ACTIVE and protected; existing 35-day PITR retained | Does not prevent authorized item deletion or prove restoration |
| Backup completion | New scripts require valid source coverage, successful archive upload and a final checksum receipt; unique keys separate concurrent runs | Media and logical database copies are not a coordinated application snapshot |
| Independent backup monitoring | Lambda checks database, media and operations backups; all three streams healthy and alarms OK with actions enabled; dedicated Terraform plan has no changes | Receipt/metadata checks do not prove restored data or notification delivery |

The isolated foundation stack applied eleven resource/setting additions, with no
replacements or deletions, and then produced a no-change Terraform plan. These
controls use a separate state boundary. The table bootstrap sources now preserve
deletion protection for both new and existing tables.

The October 8 audit validation window was **18:24:33–19:24:33 UTC**. This is verification of
delivered files for that completed interval, not a claim about all future logs.

## Independent backup monitoring

EventBridge invokes a small ARM Lambda every **15 minutes**, outside the VPC and
independent of the anchor and its NAT function. It reads the newest completion
receipt for each database, media and operations stream and checks schema, coverage, timestamps,
S3 versions, size and checksum metadata. A completed copy older than **26 hours**,
an invalid receipt or a failed check emits unhealthy status; it never falls back
to an older valid receipt to hide a newer broken one. It does not connect to the
database, download archives, or write backup objects. Its IAM read grant is
limited to the three backup prefixes and also permits archive reads.

CloudWatch evaluates all three health streams and treats missing metrics as breaching,
covering a stopped scheduler or monitor as well as stale backups. AWS evaluation
windows and service delays mean this is not an exact 30-minute detection promise.
Logs retain 14 days. The account has ten unreserved concurrent Lambda executions;
the monitor shares that pool and has no dedicated concurrency guarantee.

Acceptance on October 9 verified the deployed code hash, actual healthy results,
two scheduled invocations, both production alarms OK with notifications enabled,
and a no-change plan in the dedicated Terraform state. A separate actionless
alarm demonstrated missing-data failure, healthy recovery, explicit failure,
recovery and missing-data failure again, then was deleted. Production backup
data and thresholds were preserved. No synthetic emails were sent, no inbox
delivery was claimed, and this exercise did not repeat the October 8 restore.

Source and procedure are in [infrastructure PR 10](https://github.com/JadenRazo/aws-infra/pull/10)
and its [quota correction](https://github.com/JadenRazo/aws-infra/pull/11).
These links may require private-repository access. Investigate the alarm's
stream, newest receipt, monitor logs and nightly job before changing thresholds;
re-establish a valid backup and healthy independent checks after repairing the cause.

## Host monitoring and notification acceptance

Disk, memory and heartbeat telemetry and Lambda-error alarms are deployed. There
are **11 operational and three security alarms with actions enabled**. They notify
through SNS; the existing EC2 auto-recover/reboot actions are the
exception and remain preserved. New alarms do not provide application failover.

A real operations-host heartbeat pause exercised `FILL(heartbeat, 0)` with three
of three periods below one. It entered ALARM after **210.6 seconds** and returned
to OK after reporting resumed; applications were untouched. A separate CloudWatch
SNS provider test reported successful action status. **Human inbox receipt is not
confirmed.** Inspect telemetry and the affected service when notified; an OK
heartbeat alone does not prove application health.

## Backup coverage and demonstrated recovery

| Stream | Installed control | Acceptance boundary |
| :-- | :-- | :-- |
| Operations root | Encrypted 180 GiB; DLM daily at 08:00 UTC, retain three | First scheduled snapshot pending October 12; no snapshot restore demonstrated |
| Operations logical backup | Consistent AIO SQLite and ZeroDay dump plus required configs; scoped versioned S3 access; daily 10:30 UTC timer enabled after acceptance | Exact-version archive passed checksums, config identity, SQLite integrity, PostgreSQL restore and `pg_amcheck`; temporary resources removed. Application startup was not tested |
| Anchor database and actual media archives | Current versions retained 365 days, Glacier transition after 30 days; noncurrent versions 30 days | Retention is not a restore result; archive/permanent data preserved |
| Operations backup objects | Current versions 30 days; noncurrent versions seven days | Database/configuration restore accepted; independent protection remains separate |
| Legacy portal S3 uploads | Versioning enabled; current objects retained indefinitely, noncurrent versions 365 days | Separate from actual portal media in the Docker-local uploads archive |

The October 11 portal drill restored the latest real backups, all ten connectable
databases and their extension contract into PostgreSQL 17.11, plus actual media
(verified empty). Login, draft save and publication to an isolated fixture Git
repository passed in **8m43s**. Total duration including cleanup was **8m46s**.
The database receipt was **9h56m** old and the media receipt **7h56m** old at start;
these observed ages are not a guaranteed recovery point.

The drill used the pinned production image with test-only Git tooling, no network,
fresh credentials and owned disposable resources. Versioned receipt/archive
identities and checksums were checked; all temporary containers and volumes were
removed. Production was not a restore target. This is application API and local
publish acceptance, not customer publication, PITR, snapshot restoration or
host/AZ/regional failover. Daily backups imply up to roughly a day of data loss
when successful; this measured rehearsal is not a recovery-time commitment.

## Historical recovery evidence — October 8

The October 8 rehearsal established database-only recovery. Nightly logical dumps
imply roughly a 24-hour data-loss window when every run succeeds; missed or unusable backups make that worse. The first new-format run
completed in 3 minutes 40 seconds. Its roughly 1.11 GB compressed database archive
and the media archive were downloaded by exact S3 version and verified against
their receipts, SHA-256, lengths and compressed contents.

An isolated rehearsal then restored **all 10 connectable databases** into a
disposable PostgreSQL 17.11 server. Database loading took **6m04s**; download,
initialization, validation and cleanup took **7m11s total**. Database coverage and
extension versions matched the source inventory; restored tables were counted,
indexes were valid, and the editor database passed `pg_amcheck`. Row counts describe
the restored target; no source row-count baseline was captured for equivalence.

The rehearsal had no network, production connection or application consumers.
Its container and volume were removed, and host capacity was checked afterward.
The measured duration is for this logical restore under its resource limits; it
is **not an application recovery-time commitment or an AZ failover result**.

The small upload archives were traced against the running app. Its active upload
directory matched the mounted backup volume and contained zero files at that read;
no ephemeral fallback directory existed. Empty archives alone were not evidence
of data loss. The deployed script verifies coverage, contents, counts and checksums
before reporting backup completion; the first new archive passed an independent
download and content check with zero files and zero source bytes.

The October 8 source read reported PostgreSQL 17.10, about 6.39 GiB in connectable
databases and 6.11 GiB deliberately retained but disabled. Logical dumps skip databases that disallow
connections. Keep that data retained and prove a separate snapshot or approved
archive recovery before retiring its storage. Version availability, disk size
and an existing snapshot do not prove RDS compatibility or restoration.

## Milestones and remaining work

| Milestone | Work | Evidence required for completion |
| :-- | :-- | :-- |
| Week 1 | Foundation controls, verified archives, measured logical restore and independent backup monitoring are complete | Continue checking delivery, freshness and coverage; preserve the stated recovery scope |
| Weeks 2–3 | Origin HTTPS and trusted viewer IP accepted; permissions and complete recovery remain open | Allowed/denied access tests, recoverable deployments and accepted whole-application restore |
| Weeks 4–5 | Shared media, distributed limits and retry-safe job ownership | Two-instance consistency, tenant isolation, forged-header and duplicate-job regressions |
| Weeks 5–10 | Conditional RDS Multi-AZ, two-AZ ECS and load balancing; resolve shared-host dependencies | Compatible trial restore, single-writer cutover, measured recovery and a cost fit |
| Weeks 10–12 | SLOs, cost reviews, restore/incident drills and operating evidence | Measured outcomes, actual cost trends, owned follow-ups and reconciled architecture |

These are milestones, not a reason to delay preparation or deploy out of order.
Later-phase designs, recovery procedures and acceptance gates are prepared now.
The root normal Terraform plan returned exit 0 with no actions at **15:53:35 UTC
on October 11**, after reviewed state-only refresh and sensitivity metadata updates.
All three Cloudflare zones are now readable; ownership is unchanged. Infrastructure
CI remains static only, without automatic apply. CodeBuild remains CloudFormation
owned, with source ownership preserved and a stack policy denying replacement or
deletion. The final budget update preserved its original dates, settings and subscribers.
The infrastructure change link is recorded in the dated evidence.

The approved scope covered batches 4–8. **Explicitly excluded and unresolved** are
operations-host AdministratorAccess removal, failing portfolio Lambdas, and
independently protected backups (batches 1–3). The IAM Access Analyzer findings
remain open. Scoped backup permissions do not remove AdministratorAccess, and
versioning/retention do not establish independent or immutable backup protection.

## Conditional target design

Retain the static/serverless paths. Move the critical owner-app path to two ARM
Fargate tasks across two AZs, behind an HTTPS load balancer, with private RDS
PostgreSQL Multi-AZ primary/standby and shared media. Separate operations from
production and establish independent log/backup ownership.

Shared-state and retry tests come first. Database extensions, working set, IOPS
and connections must fit the chosen RDS class; every anchor/NAT/job dependency
needs a replacement; temporary coexistence must fit the same $250 ceiling. Do
not count retirement or scheduling savings while a host still serves production.
Auxiliary workload capacity remains an open sizing decision. If these gates fail,
retain and harden the existing platform.

Database failover is only part of app recovery. Measure reconnects, connection
pools, retries and correctness. A cutover has one writer; after the new database
accepts writes, reverting to the old one requires data reconciliation. Regional
recovery and immutable retention are separate capabilities, not implied by Multi-AZ.

## Operating evidence

The 15-minute backup monitor is an installed schedule. Additional proposed cadence:
daily external health and backup coverage review; weekly gross spend,
access findings and capacity; monthly isolated restoration and dependency review;
quarterly scoped AZ/regional exercises. Those additional processes are not new schedules.

Each exercise records scope, impact, detection, last recoverable write, elapsed
recovery, correctness, cost and follow-up ownership. Career evidence should show
the actual decision, implementation contribution and measured outcome across
architecture, DevOps, SRE, security and cost management. A plan or passing build
alone does not establish a resilience or cost-saving claim.

After each complete batch is deployed and verified, update the diagram, operating
facts, costs and evidence here together in one consolidated change. Keep future
targets distinct from what actually runs.
