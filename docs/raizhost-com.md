# How raizhost.com works

[System overview](../README.md) · [Request flow](request-flow.md) · [Deployment flow](deploy-flow.md)

The marketing website presents RaizHost's services, work, pricing, and blog. It also contains
the public quote form and browser interfaces for quote administration and the sales CRM.
Public pages are built with Astro; server operations live in separate Lambda APIs.

## Reading a page

Astro builds HTML, styles, scripts, and media into `dist/`. Deployment copies those files
to S3. Cloudflare DNS resolves the hostname to CloudFront, which serves cached output and
fetches missing objects from the private S3 origin through Origin Access Control (OAC).

Blog and service pages are built content. Browser interactions enhance them without turning
each page view into an application-server or database request. The `/demos/` mount and
`demos.raizhost.com` use the demo delivery bucket and follow the demo noindex contract.

## Submitting a quote

The form's browser code calls the configured **API Gateway URL directly**. Its request
does not travel through the marketing S3 bucket or the owner portal.

| Step | Responsibility |
| :-- | :-- |
| Browser → quote HTTP API | Submit the form payload to the configured API origin |
| API Gateway → quote Lambda | Route the request and apply stage throttling |
| Quote Lambda | Validate fields, apply anti-abuse checks, enforce administrative authorization |
| Lambda → quotes DynamoDB table | Store the accepted submission |
| Lambda → Resend | Attempt transactional mail and record its outcome |

Email failure does not erase an accepted inquiry. DynamoDB remains the source for quote
administration. A response also needs interpretation: an intentional honeypot response may
report success without creating a record.

## Quote administration and CRM

The administration pages are static browser interfaces; privileged reads and writes are
authorized by their APIs. Quote administration and the CRM have separate endpoints, tokens,
and DynamoDB tables. Browser-visible API URLs are configuration, not credentials. CORS
constrains browser origins but is not authentication.

Promoting a quote into the CRM is an explicit browser-side operation using CRM authorization.
It is not an automatic Postgres sync or an owner-portal transaction. Internal tools are
noindexed and excluded from the public sitemap; API authorization provides the access boundary.

## Shipping a website change

The current production workflow is manually dispatched with an exact reviewed commit SHA
and explicit production approval. It checks the revision, runs the site's validation, builds
Astro, and assumes the scoped AWS deployment role through GitHub OIDC.

Uploads distinguish hashed bundles, stable-name media, and HTML/metadata. Assets upload
before HTML, followed by a CloudFront invalidation and a cleanup pass. This reduces
missing-asset risk but is not an atomic release: requesting invalidation does not prove all
edge locations have finished invalidating. The repository workflow defines cache headers
and deletion policy.

Quote and CRM functions have separate deployment commands. Shipping `dist/` does not update
their Lambda code. A portal release does not deploy the marketing website either.

The [CI/CD guide](ci-cd.md) shows which checks run before release selection.
[Authorization](authorization.md) distinguishes the dispatch approval input from GitHub
environment protections; [release verification](release-verification.md) records what the
workflow checks after upload.

**Source basis:** `raizhost`'s deployment workflow, browser API clients, and
`functions/quotes/` / `functions/sales-crm/`, at the revision in [current state](current-state.md).
