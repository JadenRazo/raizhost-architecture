# From an owner's edit to a live website

[System overview](../README.md) · [Portal runtime](app-raizhost-com.md) · [Client CI/CD](client-site-cicd.md) · [Publication status](publish-status.md)

**An owner publishes through the client's Git repository.** The portal saves and validates
the draft, commits `raizhost/content.json` to the selected branch, and tracks that commit's
deployment. The client workflow builds the website and writes S3 output; CloudFront serves
it. Releasing the portal's own container is a [different pipeline](ci-cd.md).

This walkthrough covers the connected-site content editor at `app.raizhost.com`. Showers
Auto Detail supplies the concrete client workflow. Branch names and destinations below are
verified for that site; another site's connection and workflow must be inspected separately.

## What does each owner action actually do?

| Action | Immediate effect | Does it deploy the website? |
| :-- | :-- | :-- |
| Type in the editor / working preview | Change browser state; the editor bridge updates marked elements in its iframe | No. This is visual feedback using the site's proxied page |
| Save / autosave | Write the validated draft and revision to portal Postgres | No. Visitors read the previously built site |
| Upload a photo | Process a WebP and commit it to the site's configured upload directory on the live branch | Can trigger the site's push workflow; see [photos](#when-do-photos-become-public) |
| Build private preview | Flush the latest draft, then create a preview-branch content commit | Yes, to the preview destination; the public root is unchanged by this content build |
| Publish | Flush the latest draft, then create a live-branch content commit | Yes, through the client workflow; the HTTP response acknowledges submission |
| Restore from History | Load earlier content into a draft | No. Review and publish separately |

The built-preview button is labelled **Build private preview** in the UI. Showers' preview
URL returned HTML to an anonymous request on 2026-09-12. Its `noindex, nofollow` tag requests
exclusion from search; the preview is **not authenticated**. Do not put confidential content
there on the assumption that the button's label provides access control.

## Follow the handoff

<p align="center">
  <a href="../diagrams/owner-publishing.svg"><img src="../diagrams/owner-publishing.svg" alt="After the owner confirms Preview or Publish, the editor saves the latest draft and posts an explicit target and revision tokens. The portal checks authorization and content, resets the preview branch when needed, and commits content.json through GitHub. The branch push starts the client workflow independently of the portal recording a queued publication and returning HTTP 202. The workflow builds and deploys S3 and CloudFront output. The browser later asks the portal for the exact commit's workflow status." width="100%"></a>
</p>

The two parallel sections matter: deployment can proceed while the portal is completing its
database bookkeeping. The response and the deployment result are separate events.
[Open the sequence diagram](../diagrams/owner-publishing.svg).

### 1. Load the site's editing contract

The tenant's `content_sources` record selects its repository, live branch, optional preview
branch, workflow filename, content/upload paths, and public/preview URLs. The portal reads
`content-map.json` and `content.json` at one immutable source revision, plus the saved draft.
The map defines the editable fields; the client site's source defines layout and rendering.

### 2. Confirm the action and finish saving

The owner sees a change summary and confirms Preview or Publish. The editor's mutation
queue serializes draft operations and flushes the latest document before submitting the
publication. This includes an edit still waiting for the normal 1.2-second autosave debounce.
Validation problems or a revision conflict stop submission.

The browser sends `POST /api/sites/{tenantId}/content/publish` with three required values:
`kind` (`preview` or `live`), `expectedRevision`, and `expectedSourceHeadSha`. Omitting the
target never defaults to publishing live.

### 3. Pass the server's authorization and consistency gates

The server requires a valid session, an accessible tenant with a content source, and write
access: a platform admin or a tenant editor/owner. When billing is enabled, non-admin writes
also need editing access. Per-tenant/user publishing limits apply after authentication.

The service checks the draft revision, repository head, draft's base content, and the map's
field permissions and limits. It validates against the same source snapshot used for the
commit. A stale tab or concurrent source change cannot silently overwrite newer content.
The [authorization guide](authorization.md#portal-content-authorization) gives the exact
gates and rejection codes.

Routine self-service publication has the owner's confirmation and these application checks.
The inspected client workflow does **not** add a RaizHost staff approval or PR-merge step to
each button click. GitHub's branch policy must still permit the server credential's direct
write; a rejected push does not turn into a PR automatically. Managed design requests and
operator code releases have separate procedures.

### 4. Write the selected Git branch

For **preview**, the service resets or creates the preview branch at the validated live head,
then commits the cleaned draft to that branch. It checks that the live head is still current
before and after that commit. For **live**, it commits the cleaned draft directly to the
configured live branch. Each content commit updates only `content.json`.

The GitHub adapter creates blobs, a tree and a commit through the Git API, then advances the
branch without forcing the content commit over a changed head. Its write allowlist covers
the configured content and upload directories. The intentional preview reset is a separate
ref operation; the live branch is never reset by Preview.

GitHub independently checks the source credential and branch policy. In the 2026-09-12
read, Showers' main branch had a PR policy with zero required approvals and administrator
enforcement disabled; preview was unprotected. That is **not** unrestricted push permission
for every credential. The observed admin-created updates succeeded, but current installation
bypass scope was not audited. A policy-rejected write is reported as a source-write error.

### 5. Record the submission while GitHub starts the site workflow

Advancing the branch triggers the client's `on: push` workflow. Ordinary publication does
not call `workflow_dispatch`. The portal stores a publication row with an ID, content commit
SHA, kind, URL and `queued` status, then returns **HTTP 202** with that tracking information.

A live commit clears the active draft; the persistent revision still advances. A preview
keeps a draft when its content differs from the live source; a no-change preview clears the
active draft. None of those database states proves the public deployment has finished.

GitHub and Postgres cannot commit atomically. If the Git write succeeds but database
confirmation fails, the API reports `publish_confirmation_conflict`: the update may already
be deploying. Preview has another post-commit case: if its final check finds a moved live
head, it returns `content_source_conflict` even though an earlier-source preview may exist.
That preview did not change the live branch, and the tab retains the owner's edits. In
either case, reload and inspect the existing commit/run before another publication.

### 6. Run the client website's CI/CD

Showers checks immutable Action references, installs dependencies, runs unit tests, chooses
the branch's target, and builds Astro. Only then does the job obtain AWS credentials, upload
assets and HTML to the chosen S3 destination, request CloudFront invalidation, and check the
target URL. [Client CI/CD](client-site-cicd.md) diagrams each gate and the four upload passes.

The client build imports `raizhost/content.json` into its pages. The portal does not compile
those pages or send a new portal image through ECR/SSM for an owner's content update.

### 7. Reconcile the workflow result

While the editor is open and a publication is pending, the browser asks the portal for its
status. The portal looks up the configured workflow using the **content SHA and branch**,
or its recorded run identity, then persists the confirmed result. It does not accept an
unrelated latest green run. GitHub runs keep executing if the owner closes the tab; status
can be reconciled when they return. [Status and recovery](publish-status.md) explains polling,
unavailable lookups, retries, and failed deployments.

### 8. Confirm the changed page

The portal calls a successful live-kind workflow `live`; a successful preview-kind workflow
means **preview ready**. Showers' workflow checks that the target responds to an HTTP HEAD
request. It does not read the edited hours or wait for invalidation completion. For content
acceptance, open the intended live or preview page and check the actual change. A green
workflow and verified new content are different levels of evidence.

## Does Publish promote the preview?

**No. Publish makes a fresh commit from the current draft to the live branch and rebuilds.**
It does not merge the preview branch or copy the preview's built files into production.
An owner can edit again after reviewing a preview, so the later live build may contain
different values. Preview is optional; its success is not a required publication gate.

<p align="center">
  <a href="../diagrams/preview-and-live.svg"><img src="../diagrams/preview-and-live.svg" alt="A validated saved draft can take two separate paths. Preview resets the preview branch to the validated live source, adds a preview content commit, and builds with PREVIEW=1 into /_preview/. Publish adds a fresh content commit to main and rebuilds with PREVIEW=0 into the public root. There is no branch merge or artifact promotion between the paths." width="100%"></a>
</p>

For Showers, `main` builds the public root and `preview` builds `/_preview/`. Preview builds
use that base path for internal links and uploads, emit noindex, and retain a production
canonical URL. The preview prefix is shared and replaced by later previews, not a permanent
URL unique to a publication. Its reset can also create a workflow run for the base revision;
the portal must track the subsequent **content commit's** run.

This is visible in the [dated evidence](current-state.md#owner-publication-evidence): the
successful preview and live content commits were separate commits with the same parent.

## When do photos become public?

Photo upload is a separate repository mutation. The server processes the file, commits it
under the configured uploads directory on the live branch, and returns a data URL for the
editor's immediate display. Publishing later writes the content reference to that file.

Showers' push trigger has no path filter, and the upload commit has no skip-CI marker.
**An upload commit can therefore deploy the asset before the owner presses Publish.** The
new image need not be referenced by the public page yet, but its asset URL can be reachable.
The service's older comment saying uploads wait for the next publish is not a reliable
description of this workflow. This is a source-derived consequence, not a new upload test.

## Which credentials cross the handoff?

| Boundary | Identity used | What it permits |
| :-- | :-- | :-- |
| Browser → portal | Better Auth session and tenant role | Access to the selected site's content operations |
| Portal → GitHub | Server-side GitHub App installation token, or configured interim PAT | Repository operations allowed by its grants and branch policy; enabled retries also need rerun permission |
| Client workflow → AWS | GitHub OIDC exchanged for a site deploy-role session | Permitted S3 and CloudFront operations |

The adapter's environment variable named `GITHUB_TOKEN` is an interim server credential,
not the Actions job's automatic token. Runtime credential migration and deployed IAM grants
were not re-audited. The [identity guide](authorization.md#deployment-identity) explains AWS
trust and operation-level permission checks.

## Source map

These links pin behavior to the inspected portal revision. Private source links require
repository access; the walkthrough above is self-contained.

| Question | Implementation authority |
| :-- | :-- |
| What does a button call? | [Editor confirmation and submission](https://github.com/JadenRazo/raizhost-app/blob/f3a405f7ddf07463f5436e699cdf2293225cba18/src/components/content-editor/site-editor.tsx), [serialized draft operations](https://github.com/JadenRazo/raizhost-app/blob/f3a405f7ddf07463f5436e699cdf2293225cba18/src/components/content-editor/draft-mutation-lane.ts) |
| What can the owner change? | [Content contract](https://github.com/JadenRazo/raizhost-app/blob/f3a405f7ddf07463f5436e699cdf2293225cba18/docs/content-contract.md), [server route gates](https://github.com/JadenRazo/raizhost-app/blob/f3a405f7ddf07463f5436e699cdf2293225cba18/src/app/api/sites/%5BtenantId%5D/content/_shared.ts) |
| Which repo, paths, branches and workflow? | [Content-source resolution](https://github.com/JadenRazo/raizhost-app/blob/f3a405f7ddf07463f5436e699cdf2293225cba18/src/lib/content/source/index.ts) |
| What is saved, committed or tracked? | [Content service: addImage, publishDraft, refreshPublish and restore](https://github.com/JadenRazo/raizhost-app/blob/f3a405f7ddf07463f5436e699cdf2293225cba18/src/lib/content/service.ts) |
| What triggers CI and identifies the run? | [GitHub source adapter](https://github.com/JadenRazo/raizhost-app/blob/f3a405f7ddf07463f5436e699cdf2293225cba18/src/lib/content/source/github.ts), [client workflow](client-site-cicd.md#source-map) |

The older Puck page-builder uses a separate direct-publication implementation. This page
describes `/content/publish`; do not apply it to the legacy `/api/sites/{tenantId}/publish`
route or the operations repository's site-update command.
