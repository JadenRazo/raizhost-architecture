# Design decisions

[System overview](../README.md) · [Request flow](request-flow.md) · [Current evidence](current-state.md)

These decisions explain the platform's shape and the tradeoffs it accepts. Historical
cost motivations are not current price quotes; billing needs its own dated measurement.

## Static output for public websites

Marketing pages, demos, and client websites publish built HTML and assets to S3/CloudFront.
Most visits need no application compute or relational database. This keeps delivery simple
and separates an owner's editing session from the website visitors receive.

The tradeoff is a build/publication step for content changes. Git history makes earlier
content recoverable, but S3 upload plus CDN invalidation is not an atomic switch.

## An owner editor over each site's source

The connected client website defines a content map, and the portal validates edits against
it. The owner controls routine content while RaizHost manages layout and structural changes.
Publication creates a content commit and uses the site's own build.

This adds a GitHub dependency to editing and publication. The portal must distinguish
saved, committed, building, live, failed, and unconfirmed outcomes.

## One anchor for the portal and relational services

The always-on EC2 anchor hosts the Next.js owner portal and Postgres services. This
consolidates the workload without a separate database fleet. PgBouncer absorbs connection
pressure from tracker Lambdas; the portal and tracker keep separate databases.

The cost is shared failure exposure and operational responsibility for patching, capacity,
backups, and restoration. A configured backup job is not proof of recoverability. Separate
databases also do not prove independently scoped database credentials.

## Lambda for tracker requests and scheduled collection

The tracker web application renders stored data on demand through HTTP API Gateway and
Lambda Web Adapter. Pollers run as separate scheduled ZIP Lambdas. Browser visits and
upstream collection therefore have independent lifecycles.

The web function's local cron is disabled. Database-backed pages render dynamically at
request time, with explicit CDN windows, so a database-free image build cannot freeze an
empty dashboard into production.

## Cloudflare DNS and CloudFront delivery

Cloudflare provides hostname resolution. CloudFront terminates viewer TLS and chooses the
origin/cache behavior. Private S3 origins use OAC. Route 53 health checks integrate with
CloudWatch monitoring rather than providing authoritative DNS in this design.

DNS-only records must not be drawn as an extra HTTP proxy. Cache and authorization policy
belong to the relevant distribution and application, not to a generic DNS box.

## An HTTPS load balancer without an application failover claim

The portal now uses a managed HTTPS origin with restricted network ingress and
an origin credential. Its ALB spans two zones, but forwards over private HTTP to
one anchor. This adds a managed transport boundary and a future target attachment
point; it does not supply another application or database. The cost allowance and
remaining recovery gates belong to [cloud operations](cloud-operations.md), and
[portal ingress](portal-ingress.md) shows the actual hops.

## DynamoDB for inquiries and CRM

Quote capture and CRM operations have separate HTTP APIs, Lambda functions, and DynamoDB
tables. They do not require the anchor's Postgres service. Administrative handlers check
authorization; CORS and noindex serve different purposes.

Resend attempts transactional email after an accepted quote is stored. Email delivery and
successful storage are separate outcomes.

## Anchor NAT for private-subnet egress

The documented network routes private Lambda egress through the anchor, avoiding a dedicated
NAT Gateway. Pollers use that outbound path to reach upstream sources.

This adds routing availability and configuration persistence to the anchor's responsibilities.
Reverify the live route and firewall configuration when diagnosing ingestion failures.

## Scoped OIDC roles and repository-owned releases

GitHub Actions exchanges OIDC identity for the relevant AWS role. The portal uses ephemeral
CodeBuild runners; marketing and tracker use their inspected GitHub-hosted workflow paths.
Runner identity and deploy permission are separate.

Triggers differ by repository. The [deployment guide](deploy-flow.md) records those
differences rather than describing every release as a push to main.

## Infrastructure declarations require reconciliation

Terraform records the original core, CloudFormation owns the runner factory, and client
provisioning scripts produce import maps. Recorded out-of-band changes mean source is not
proof of a drift-free account.

Legacy-root Terraform automation remains held in the inspected workflow. Current inventory,
a reviewed no-op reconciliation, and tested recovery are prerequisites to changing that
operational posture. The October foundation stack uses its own state boundary and
was applied only after ownership checks and a reviewed non-destructive plan; its
post-apply plan showed no changes. This does not reconcile the legacy root.

## Cost reporting follows evidence

The older public headline combined a modeled serving core with an expected operations-box
saving. It did not establish the current whole-account bill. This guide avoids a fixed
monthly-cost claim and stale resource totals.

Measure billing over a stated period, separate serving and operations/CI costs, and include
storage, networking, and retained resources. A budget alert is a notification, not a hard
spending cap.

The [October cloud operations record](cloud-operations.md) contains the measured
September gross cost, current budget and conditional migration target. The first
batch prioritizes auditability, reliable backups and demonstrated logical recovery
without adding a new compute fleet. A two-zone ALB now fronts the existing anchor. Multi-AZ application and database
capacity still come after application
state, database compatibility, dependency retirement and cost gates pass.
