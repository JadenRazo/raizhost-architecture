# Client provisioning

Going live for a new client used to be ~12 console steps. It is now one command that plans by
default and mutates only on `--execute`, which trips the operations guard's approval prompt.

```
node infra/new-client-site.mjs --slug <slug> --domain <domain> [--no-www] [--no-dns] [--execute]
```

```mermaid
sequenceDiagram
  autonumber
  participant Op as Operator
  participant S as new-client-site
  participant G as Guard hook
  participant AWS
  participant CFl as Cloudflare

  Op->>S: run (plan mode)
  S->>AWS: describe existing resources (read-only)
  S-->>Op: mutation manifest (what would be created, what already exists)
  Op->>S: run again with --execute
  S->>G: gated action
  G-->>Op: approve?
  Op-->>G: yes
  S->>AWS: S3 bucket (versioning on) + scoped policy
  S->>AWS: ACM certificate (DNS-validated, us-east-1)
  S->>CFl: validation CNAME (create-only; never overwrites)
  Note over S,AWS: run stops at the ACM wait — re-run when ISSUED
  Op->>S: run again with --execute
  S->>AWS: CloudFront Function (canonical URLs) + OAC
  S->>AWS: CloudFront distribution from template
  S->>CFl: site CNAME(s) → CloudFront (DNS-only)
  S->>AWS: Route 53 health check (HTTPS, 30s)
  S->>AWS: CloudWatch uptime alarm → SNS
  S-->>Op: clients/<slug>.json registry + terraformImport map + paste-ready docs
```

## Properties that matter

- **Idempotent.** Live AWS is the state; every step is check-then-create and safe to re-run.
  Existing resources are reported, not touched.
- **Re-entrant across the certificate wait.** The same command twice is the normal path.
- **DNS is create-only.** An existing record with different content is reported and left
  alone — so an MX record can never be clobbered by a site launch.
- **Drift alarm.** The checked-in CloudFront Function source is byte-compared against the live
  reference function on every run; divergence aborts before anything is created.
- **Registry out, not just resources.** Each client gets a JSON registry of every ID plus a
  `terraformImport` map, so adoption into Terraform is a mechanical import loop later.
- **Monitoring is part of go-live**, not a follow-up: health check + alarm are created in the
  same run. (The first alarm evaluation fires one ALARM→OK pair before real data arrives — that
  pair is the delivery test.)

## After launch: content updates

```
node infra/site-update.mjs <slug> [--execute] [--allow-delete]
```

Runs the site's own link/rendering checks, bumps a site-wide `?v=N` cache-bust, does the
two-pass `s3 sync` with the proven cache-control split, invalidates `/*`, polls until complete,
then verifies live 200s and headers. Deleted files are listed and the run aborts unless
`--allow-delete` — the guard against syncing the wrong directory into a production bucket.
