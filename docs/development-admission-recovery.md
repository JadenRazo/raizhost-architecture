# Development admission recovery — October 21, 2026

The shared development admission blockage was resolved through a reviewed owner
recovery operation. This was a failed-lab closeout on the existing operations
host, not a production recovery drill or a new hosting deployment.

The recovery contract now separates the original job outcome, present resource
settlement and lock custody. A missing terminal acknowledgement remains a
historical failure. Fresh, identity-bound settlement can produce a distinct
recovery receipt without fabricating that acknowledgement or reporting success.

The executed maintenance disposition preserved the failed evidence, stopped only
verified private lab resources and accounted for later custodians, mounts and
namespace references. Legacy processes had no cooperative exit channel; their
reviewed termination was explicitly authorized. Final custody remained until
settlement and durable evidence were complete. The original lock inode remained
unchanged and the normal operations runner subsequently acquired admission.

The lifecycle implementation passed 27 focused fixtures and the owning
repository's independent concurrency review. Historical inactive artifacts,
about 12.1 GB allocated, remain retained and included in capacity accounting.
No shared storage was pruned and no unrelated workload was stopped.

## Business OS validation boundary

Business OS then ran on the same host under normal exclusive admission. A
dedicated non-login identity, private rootless daemon, bounded memory-backed
storage and network isolation separate its disposable work from host services.
The aggregate limit is one CPU, 3 GiB memory, zero swap and 512 processes. Setup
downloads use an allowlist; execution seals that outbound path.

Trusted probes and an actual pinned PostgreSQL container ran before source
transfer. Parent and controller interruption fixtures demonstrated continued
custody while writers survived. Timeout can initiate cancellation; it cannot
release admission while resources remain uncertain.

Pinned compiler, lint and time checks passed. All 47 PostgreSQL cases passed in
an initial run and five additional fresh databases. The fixture browser passed
five widths with retained screenshots, accessibility reports and traces. The
final standalone command failed its old 20 MiB accounting limit after the
functional checks passed. That failure remains recorded. A tested local limit
matching the owner's existing 64 MiB total and 8 MiB per-file budget accounted
for the retained bundle; independent core review accepted the reconciliation.

All private validation resources settled and all retained hashes were verified
before subsequent normal admission. Authenticated persistent application work is
a separate milestone; fixture browser results do not prove it.

## Delivery and cost limits

The recovery and boundary implementations are reviewed local work. This record
does not claim they were merged into the products' default branches or deployed
as a general scheduler. Detailed source bindings, review verdicts, process and
resource manifests, command results and closeout receipts remain in the private
owner and operations evidence packets.

No new cloud resource, disk expansion, paid workflow or schedule was introduced.
Temporary bulk validation storage used bounded RAM; evidence and historical
inactive artifacts remain on disk. Incremental snapshot cost was not measured.
The existing platform budget and production topology were not changed.

[Cloud operations](cloud-operations.md) distinguishes this development control
from production recovery and resilience.
