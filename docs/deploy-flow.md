# Deploy flow

Deployments are GitHub Actions workflows using **OIDC role assumption**: a per-repository IAM role
binds deployment permission to the expected repository/ref or protected environment. There are no
stored AWS keys in CI. Runner identity and deploy identity are separate: the `raizhost-app` runner
is an ephemeral CodeBuild environment with only source-connection and log permissions; the workflow
must still assume its narrower deploy role.

<p align="center">
  <img src="../diagrams/deploy-flow.svg" alt="Reviewed changes enter GitHub Actions. The app uses one-job CodeBuild runners while other repositories use their onboarded runner path. Jobs assume separate OIDC deploy roles, then deploy static sites to S3 and CloudFront, Lambda artifacts to Lambda, or the client editor through ECR and SSM with health-gated rollback. Client editor publishes first create a content commit in the client's repository." width="100%">
</p>

<sub>Editable source: [`diagrams/deploy-flow.mmd`](../diagrams/deploy-flow.mmd). A committed SVG is embedded so the flow remains visible in GitHub's mobile clients.</sub>

## Why three shapes

| Target | Mechanism | Why |
|:--|:--|:--|
| **Static sites** | `aws s3 sync` in ordered passes + one invalidation | The order matters: HTML goes last so it never references an asset that isn't uploaded yet, and a final `--delete` pass runs *after* invalidation so cached HTML can still find the old hashed assets it points to. `--size-only` is banned because sync only stamps cache-control on objects it uploads. |
| **Lambda apps** | Image push + `update-function-code` | Immutable images, instant rollback by pointing at the previous tag. Images are built arm64 in CI so Graviton Lambdas never run under emulation. |
| **Client editor** | SSM RunCommand executing an on-box `deploy.sh` | The editor is stateful and lives on the anchor. SSM gives an audited, IAM-scoped way to run the deploy without opening SSH. The script is health-gated with automatic rollback, and the on-box files are tracked in the app repo with a read-only drift check that runs after every deploy. |

## Runner path

`raizhost-app` moved to CodeBuild-hosted GitHub Actions runners on 2026-08-30. Each job gets a
fresh environment and then terminates; ordinary checks use small ARM compute, browser checks use a
disposable Ubuntu x86 image, and production image builds use ARM. The runner service role has no
application permissions. Other repositories remain on their existing runner path until they are
onboarded through a separately reviewed trust domain.

This migration followed a GitHub-hosted runner billing incident that blocked the app and Showers
workflows on 2026-08-27/28. It is a targeted resilience change, not a claim that every repository
has already moved.

## Terraform

Infrastructure CI is intentionally **static-only while the H8 drift reconciliation is open**. It
runs formatting, backend-free validation, security scanners, and runner-factory tests, but has no
AWS identity and cannot run a live plan or apply. The old scheduled drift job is unscheduled and
retained as a sentinel. The last known live plan included destructive production DNS drift, so
making that path automatic would be unsafe.

Platform applies remain targeted and human-run. Day-to-day client provisioning uses the gated
scripts described in [client-provisioning.md](client-provisioning.md), which emit a
`terraformImport` map so the resources they create can be adopted after state is reconciled.

## One gotcha worth writing down

After a push, match workflow runs to the exact `head_sha` before trusting them. During a GitHub
Actions incident, a push created *zero* runs and the previous run's green check was easy to
mistake for the new one. A small verify script now does that match and prints the
`gh workflow run` fallback if the event was dropped.
