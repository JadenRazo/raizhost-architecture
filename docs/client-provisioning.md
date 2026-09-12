# Client delivery and provisioning

[System overview](../README.md) · [Owner portal](app-raizhost-com.md) · [Deployment flow](deploy-flow.md)

A client website has two connected pieces: a built static site that visitors receive from
S3/CloudFront, and an owner content contract that the portal can edit. Hosting provisions
the destination; the client repository and its workflow determine what is published there.

## Provision the hosting destination

The operations repository contains the planning command:

```text
node infra/new-client-site.mjs --slug <slug> --domain <domain> [--no-www] [--no-dns] [--execute]
```

The default run inspects existing state and prints proposed changes. Execution requires
authorization for the listed effects and an explicit `--execute` run. The flag is not
evidence of human approval, and an approval hook is not assumed to run in every agent runtime.

<p align="center">
  <a href="../diagrams/client-provisioning.svg"><img src="../diagrams/client-provisioning.svg" alt="Inspect existing hosting and DNS state, prepare the exact mutation plan, then obtain authorization. An execute run creates a versioned S3 bucket and certificate validation, waits for issuance, creates CloudFront with OAC, adds site DNS and monitoring, and records resource and Terraform import maps." width="100%"></a>
</p>

The script checks for existing resources before creating them, supports rerunning after
certificate validation, and records the resulting resource map. DNS creation reports
conflicting existing records rather than replacing them. Its CloudFront Function comparison
checks the expected routing implementation before creation.

The output includes a versioned S3 bucket, an ACM certificate, CloudFront/OAC, DNS records,
and Route 53/CloudWatch monitoring. Route 53 health checks are monitoring, not the site's
authoritative DNS. Monitoring configuration still needs delivery and recovery verification.

## Connect the site to the owner portal

1. Build the site in its own repository, with content read from `raizhost/content.json`.
2. Define the editing boundary in `raizhost/content-map.json`. Keep structural/design fields
   managed and routine owner fields editable.
3. Provide the site's build/deploy workflow and scope its OIDC permissions to its resources.
4. Configure the tenant's source repository, live branch, and optional preview branch/URL.
5. Verify authorization, draft saving, preview isolation, publication tracking, and the
   public result using the site's actual contract.

Preview deployment must stay beneath `/_preview/` and carry noindex. The production website
is indexable where appropriate. A preview is not access-controlled merely because it is
noindexed.

## Ongoing changes

Owner publication commits allowed content and uploaded images to the client repository.
The site's workflow builds and deploys them. The [portal guide](app-raizhost-com.md) explains
draft revisions, source conflicts, and when a publication may be called live.

Managed structural changes use the site's reviewed code/deploy path. Older operations-hosted
sites also have a separate update command:

```text
node infra/site-update.mjs <slug> [--execute] [--allow-delete]
```

That command owns its build/link checks, asset/HTML cache handling, invalidation, and
deletion guard. It is not the portal's content-source publisher.

**Source basis:** operations `infra/new-client-site.mjs`, `infra/site-update.mjs`, the client
launch runbook, and the portal content contract. Current client count and onboarding status
are outside this document's verification scope.
