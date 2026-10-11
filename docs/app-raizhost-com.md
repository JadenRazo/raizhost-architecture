# How app.raizhost.com works

[System overview](../README.md) · [Owner-to-live walkthrough](owner-publishing.md) · [Client CI/CD](client-site-cicd.md)

The owner portal is the editing and management surface for a client's RaizHost website.
An owner can change the content exposed by that website's contract, save a draft, inspect
a preview, and publish. Design and structural changes go through tracked managed requests.

For the complete **Preview / Publish button path**, start with the
[owner-to-live walkthrough](owner-publishing.md). It follows the browser request through
server gates, GitHub, the client build and the publication result.

## The runtime

The browser resolves `app.raizhost.com` through Cloudflare DNS and connects to CloudFront.
CloudFront connects to an HTTPS ALB origin, which forwards over private HTTP to the
always-on Next.js container on the EC2 anchor. The ALB spans two zones but has one
application target. [Portal ingress](portal-ingress.md) diagrams transport and origin trust. Postgres stores accounts, tenant membership, drafts, and publication records.
Better Auth handles authentication; server-side checks enforce membership, role, subscription,
and permitted fields. An owner-facing control is only the interface to those checks.

The [portal authorization diagram](authorization.md#portal-content-authorization) shows
the session, tenant, write-role and conditional billing gates, including their rejection
paths. Read access and write access follow different checks.

Authenticated pages and APIs must not share personalized responses through a public cache.
Static bundles have a different caching policy. The historical portal Lambda was retired;
the current release workflow deploys a container through ECR and SSM.

## The website defines the editing boundary

Each connected client repository supplies these files:

| Path | Responsibility |
| :-- | :-- |
| `raizhost/content-map.json` | Controls, labels, types, validation limits, and owner/managed access |
| `raizhost/content.json` | Committed content values; the site build turns them into published HTML |
| `public/uploads/` | Owner images committed separately when uploaded |

The v2 map makes routine owner controls available across subscribed plans and preserves
managed design values on the server. Legacy v1 maps retain their older access rules until
deliberately migrated. The site consumes the content during its own build. Preview markers
such as `data-rh` let the editor's working preview update the corresponding visible elements.

## Save, preview, and publish

| Action | What it writes | What the visitor sees |
| :-- | :-- | :-- |
| Edit the working preview | Temporary browser state | The public website is unchanged |
| Save | Active draft and a monotonic revision in Postgres | The public website is unchanged |
| Upload a photo | Separate asset commit on the configured live branch | Its workflow can deploy the asset before Publish updates the page's reference |
| Build a preview | Content commit on the configured preview branch | Showers builds under `/_preview/`; its public root is unchanged by this content build |
| Publish | Content JSON commit on the configured live branch, then a site workflow run | S3 objects change during deployment; the portal confirms success from the matching workflow |
| Restore a prior revision | A draft based on earlier content | It must go through publication to become public again |

The inline working preview is immediate browser feedback. A built preview exercises the
real site's build and deployment. Noindex requests exclusion from search indexing; it does
not authenticate viewers. Showers' built preview was anonymously accessible in the dated read.

The GitHub source adapter commits through GitHub's API. It supports GitHub App installation
credentials and an interim token path; this guide does not claim that the production
credential migration has finished. The portal does not run the connected site's Astro build.

The detailed guides divide that work at its real boundaries:

- [Owner action and Git handoff](owner-publishing.md): confirmation, save flushing, tenant
  gates, source conflicts, branch writes, photos, and HTTP 202.
- [Client CI/CD](client-site-cicd.md): the actual Showers checks, preview/live build flags,
  AWS credentials, S3 passes, invalidation and HTTP smoke check.
- [Status and recovery](publish-status.md): run identity, polling, terminal states, partial
  writes, rechecks, eligible retries and restored content.

## Concurrency and failure boundaries

Draft saves use compare-and-swap revisions: a stale tab cannot silently replace newer work.
The revision survives draft deletion, so a delayed autosave cannot recreate a discarded or
published draft. Source changes and draft conflicts have different recovery paths.

GitHub lookups distinguish a matching run, confirmed absence, and an unavailable response.
An API outage leaves publication unconfirmed. A successful content commit alone does not
mean the site is live. The portal's `live` status means the matching workflow succeeded;
that workflow's checks determine how much has been verified about the served output.

Live S3 publication is not an atomic swap. A failing workflow may already have uploaded some
objects, so a failure cannot promise that the previous public version is intact. Preview
isolation is enforced by its branch/prefix contract. Git history supports recovery, but
restoring public output still requires a new successful deployment.

The older Puck page-builder renderer has a separate direct-publication implementation. The
flow above describes connected, hand-built client websites. Releasing portal code is also
separate from an owner pressing Publish.

For portal code, follow [CI/CD](ci-cd.md) into the [rollout and rollback gates](release-verification.md#portal-rollout-and-rollback).

**Source basis:** `raizhost-app`'s content contract, `src/lib/content/`, authentication checks,
and anchor deployment workflow at the revision in [current state](current-state.md).
