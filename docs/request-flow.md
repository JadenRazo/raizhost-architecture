# Request flow

How a browser request reaches each kind of surface. Every public hostname resolves through
Cloudflare DNS (DNS-only CNAME) to its own CloudFront distribution; AWS hosts only origins.

```mermaid
flowchart TB
  B(["Browser"]) --> DNS["Cloudflare DNS<br/>DNS-only CNAME → CloudFront"]
  DNS --> CF["CloudFront distribution<br/>ACM cert · PriceClass_100"]
  CF --> FN["CloudFront Function (viewer-request)<br/>301 slash-less folders → /path/<br/>rewrite /path/ → /path/index.html<br/>block known-bad user agents"]
  FN -->|"static site"| S3["S3 origin via OAC<br/>hashed assets: immutable 1y<br/>HTML: max-age=0, s-maxage=1d"]
  FN -->|"/api/* on a site"| GW["HTTP API Gateway<br/>CORS locked to the site<br/>stage throttling"]
  GW --> L["Lambda (arm64)"]
  FN -->|"app.raizhost.com"| ANCHOR["anchor EC2 :8083<br/>portal container<br/>SG allows CloudFront prefix list only"]
  L -->|"in-VPC apps"| PG["Postgres via PgBouncer<br/>(on the anchor)"]
  L -->|"key-value apps"| DDB[("DynamoDB")]
  L --> SM["Secrets Manager"]
  L -->|"outbound"| NAT["anchor as NAT<br/>(no NAT Gateway)"]
```

## Three origin types

| Surface | Origin | Cold path | Notes |
|:--|:--|:--|:--|
| Static sites (marketing, demos, client sites, status) | S3 via Origin Access Control | S3 GET | Bucket policies allow only the owning distribution(s). The demo factory is mounted on **two** hosts (`demos.raizhost.com` and `raizhost.com/demos/`) from one bucket, which is what surfaced the shared-cache-key lesson. |
| Serverless apps (`llm.raizhost.com`, tenant apps, quote/CRM APIs) | HTTP API Gateway → Lambda | Lambda cold start (arm64 Next.js containers ~1 s; Go/Rust zip ~50 ms) | Next.js apps emit `s-maxage` so CloudFront serves HTML for most requests; Lambda sees only revalidations. |
| Client portal (`app.raizhost.com`) | Custom origin: the anchor's portal container | none (always on) | Origin request policy forwards all viewer headers; `X-Forwarded-Proto=https` is injected as an origin custom header. Auth pages are `no-store`; static chunks are immutable. |

## Why the edge does so much

CloudFront Functions run on every viewer request for microdollars and let the origins stay
dumb: canonical URLs are enforced before S3 sees the request, obvious bot traffic is dropped
before it becomes a Lambda invocation, and per-behavior cache policies decide what is shared.
The only time an origin is touched for a static site is a cache miss or an invalidation.
