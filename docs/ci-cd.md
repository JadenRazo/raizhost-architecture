# From an application code change to a release

[System overview](../README.md) · [Client content CI/CD](client-site-cicd.md) · [Deployment identity](authorization.md) · [Release verification](release-verification.md)

**An owner pressing Preview or Publish follows the [client website pipeline](client-site-cicd.md).**
The [owner walkthrough](owner-publishing.md) explains how that push is created. This page
covers changes to the marketing, portal and tracker applications themselves.

CI checks proposed code. CD releases a selected revision. RaizHost's three main applications
connect those stages differently: marketing releases pushes to `live` or an approved
dispatch on that branch, the
portal publishes and deploys after successful push CI on main, and the tracker accepts
either successful CI on main or a manual deployment dispatch.

<p align="center">
  <a href="../diagrams/ci-cd-flow.svg"><img src="../diagrams/ci-cd-flow.svg" alt="Three CI/CD lanes. Marketing CI supplies evidence for reviewed promotion to live; live pushes or an approved dispatch on live start deployment. The job binds the selected SHA to live history and runs checks before S3. Portal build and end-to-end checks precede image publication on a push to main, and a same-repository successful push CI gates SSM deployment of its head SHA. Tracker successful CI on main or an independent manual dispatch selects the revision for its web image, assets, and three pollers." width="100%"></a>
</p>

Read each lane downward. Solid arrows are workflow dependencies or triggers. The marketing
dashed arrow is an **operator code-promotion step**: its Deploy workflow does not query
a prior CI conclusion. Owner content commits also push the configured `live` branch. [Open the diagram at full size](../diagrams/ci-cd-flow.svg).

## 1. Check the proposed change

| Repository | CI runs for | Checks that matter to this architecture |
| :-- | :-- | :-- |
| `raizhost` | PRs and pushes targeting main or staging | Workflow pins, theme/CRM contracts, Astro checks/build, blog and pricing output, browser interactions, contrast, links and Lighthouse |
| `raizhost-app` | Main PRs, main pushes, manual CI runs; fork PR jobs are skipped | `build`: workflow policy, types, lint, tests, build. `e2e`: real local Postgres, migration compatibility, owner editing/publication and published output |
| `llm-tracker` | Main PRs and main pushes | Types, lint, read/UI regressions, build, no database-backed prerendering, loadable poller bundle |

The portal's two check jobs run independently; image publication needs **both**. Its PR
checks use disposable CodeBuild runners. Marketing and tracker CI use GitHub-hosted runners.
The tracker build intentionally has no production database connection: the prerender guard
prevents that empty build environment from becoming a permanently empty public page.

A failed required job stops its dependent jobs. A green PR run is evidence about that run's
revision; a main push may test a different merge revision.

## 2. Apply the actual merge gates

These GitHub settings were re-read on **2026-10-11 UTC**, alongside the workflow source.
Required checks are configured separately from checks that merely run.

| Main branch | Required status checks | Required approving reviews |
| :-- | :-- | :-- |
| `raizhost` | None configured | 0 |
| `raizhost-app` | `build`, `e2e`; branch must be up to date | 0 |
| `llm-tracker` | `Typecheck, lint, build`; branch must be up to date | 0 |
| `aws-infra` | None configured | 0 |

All four inspected branch protections enforce their rules for administrators and require
conversation resolution. Their branch-rules API returned no additional active ruleset
rules. A zero review count does not encode RaizHost's operational review and release
authorization procedure. [Authorization](authorization.md) distinguishes that procedure
from automated enforcement; [diagram evidence](diagram-evidence.md) records
how these settings were checked.

## 3. Select the release and its exact revision

| Target | What permits the deploy job | Revision used |
| :-- | :-- | :-- |
| Marketing | Push to `live`, or dispatch on `live` with `approve_production == true`; checkout must equal the selected SHA and be its release-branch ancestor | Push SHA or requested `commit_sha`; deployment checks rerun before AWS credentials |
| Portal | CI conclusion is success, original event is push, head branch is main, and head repository matches | `workflow_run.head_sha`, whose image CI already pushed |
| Tracker | Successful CI on main **or** manual Deploy dispatch | CI `head_sha`, or the dispatch's `github.sha` |

Marketing merging to main does not deploy production. Approved code must be promoted to
`live`; owner content publication also writes that configured branch. Dispatch requires
the `live` ref and a requested commit in its history. Neither path queries a prior CI
conclusion, so the operator must assess the relevant evidence before code promotion.

A portal main push can release production automatically, so authorize that effect before
merging. Manually dispatching **portal CI** does not satisfy its push-only image/deploy
gates. Tracker's manual Deploy path has no CI-success prerequisite; its automatic condition
also lacks the portal's explicit push-event and same-repository comparisons. Keep those
distinctions when reviewing workflow changes.

## 4. Ship, then establish the result

The [deployment flow](deploy-flow.md) maps images, ZIPs and static output to their destinations.
The [identity diagram](authorization.md#deployment-identity) shows how a job obtains permission
to write. The [verification guide](release-verification.md) explains which checks run after
those writes and how a failed rollout is handled.

Client content follows the [owner publication flow](owner-publishing.md), then
[client CI/CD](client-site-cicd.md): the client repository owns its build and live/preview
deployment checks. Do not infer those checks from portal CI.
Quote/CRM functions have separate deployment commands. Infrastructure CI performs static
validation without AWS identity; live Terraform plan/apply remains held pending drift
reconciliation. Passing this architecture repository's documentation CI only validates docs.

**Source basis:** each application's `.github/workflows/ci.yml` and `deploy.yml`, infrastructure
Terraform CI, and the dated GitHub settings in [current state](current-state.md).
