# Request flow

How a browser request reaches each kind of surface. Every public hostname resolves through
Cloudflare DNS (DNS-only CNAME) to its own CloudFront distribution; AWS hosts only origins.

<p align="center">
  <img src="../diagrams/request-flow.svg" alt="A browser resolves through Cloudflare DNS to CloudFront. CloudFront routes static surfaces to S3, serverless routes through HTTP API Gateway to Lambda, and app.raizhost.com to the anchor-hosted client editor. Lambda reaches DynamoDB, Secrets Manager, and Postgres through PgBouncer, using the anchor for private-subnet egress." width="100%">
</p>

<sub>Editable source: [`diagrams/request-flow.mmd`](../diagrams/request-flow.mmd). A committed SVG is embedded so the flow remains visible in GitHub's mobile clients.</sub>

## Three origin types

| Surface | Origin | Cold path | Notes |
|:--|:--|:--|:--|
| Static sites (marketing, demos, client sites, status) | S3 via Origin Access Control | S3 GET | Bucket policies allow only the owning distribution(s). The demo factory is mounted on **two** hosts (`demos.raizhost.com` and `raizhost.com/demos/`) from one bucket, which is what surfaced the shared-cache-key lesson. |
| Serverless apps (`llm.raizhost.com`, tenant apps, quote/CRM APIs) | HTTP API Gateway → Lambda | Lambda cold start (arm64 Next.js containers ~1 s; Go/Rust zip ~50 ms) | Next.js apps emit `s-maxage` so CloudFront serves HTML for most requests; Lambda sees only revalidations. |
| Client editor (`app.raizhost.com`) | Custom origin: the anchor's editor container | none (always on) | Origin request policy forwards the required viewer headers; `X-Forwarded-Proto=https` is injected as an origin custom header. Auth pages are `no-store`; static chunks are immutable. Publishing content leaves the request path and enters the repository deploy flow. |

## Why the edge does so much

CloudFront Functions run on every viewer request for microdollars and let the origins stay
dumb: canonical URLs are enforced before S3 sees the request, obvious bot traffic is dropped
before it becomes a Lambda invocation, and per-behavior cache policies decide what is shared.
The only time an origin is touched for a static site is a cache miss or an invalidation.
