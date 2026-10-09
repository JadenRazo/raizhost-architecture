# Working on RaizHost architecture

Explain the platform so an operator or public reader can trace a user action
through services, data and recovery paths. This is a documentation repository;
changing a diagram does not implement or authorize the depicted infrastructure.

## Authority and evidence

Start with the README's action map and the affected `docs/` walkthrough.
Use `docs/current-state.md` for dated revisions, observations and unresolved
verification, `docs/cloud-operations.md` for operating versus target design,
and `docs/decisions.md` for decisions. Trace changed claims to the owning
application/infrastructure source and its revision before updating them.

Keep source implementation, workflow completion, live configuration, endpoint
observations and demonstrated recovery distinct. Record date, scope and limits
beside evidence; an old audit's heading date is not a fresh inventory. A healthy
endpoint is not a recovery drill, and a backup rehearsal is not automatic
failover. Budget/usage figures need their dated authority and gross-cost scope.
Do not infer current production from proposed Terraform or an historical receipt.

Consolidate a verified change batch into the relevant guides and one evidence
record after its outcome is established. Preserve earlier observations and their
scope; keep incomplete work visibly pending. Link detailed receipts instead of
turning the reader's walkthrough into a running incident log or duplicating
changing inventory everywhere. Never expose private account/resource identifiers,
credentials, client data or private release metadata in this public repository.

## Diagrams and checks

Read `diagrams/README.md` before visual changes. `diagrams/overview.py` owns
the overview SVG and Mermaid sketch; `diagrams/journeys.json` and
`diagrams/journeys.py` own journey desktop/mobile SVGs and sketches. Other flows use their `.mmd`
source. Do not hand-edit generated outputs. Keep prose and arrows consistent,
include text alternatives, and review desktop and narrow reading widths.

With the documented dependencies already available, the local checks are:

```sh
python3 diagrams/overview.py --check
python3 diagrams/journeys.py --check
python3 diagrams/journeys.py --self-test
python3 diagrams/check_docs.py
python3 diagrams/check.py
```

`diagrams/render.sh` regenerates assets and checksums; it requires the rendering
toolchain described in the diagram guide. Render only when source assets change.
`.github/workflows/ci.yml` owns Markdown lint, every-Mermaid syntax rendering,
geometry and private-identifier checks on PRs and main pushes. Geometry checks
need font dependencies; passing them does not establish production accuracy.
A prose edit needs relevant link/source/privacy checks, not a cloud operation
or a new application release. Report unavailable checks without calling them passes.

## Writing and delivery

Lead with what a user does and what happens next. Use familiar words, one idea
per paragraph, and descriptive evidence links. Explain decisions and material
limits without inflated reliability claims or repeated summaries. A PR states
the documentation problem, resulting explanation and checks actually run.
Use focused commits following repository history, otherwise
`docs: concrete change` (preferably under 72 characters). Report edits, review,
push/PR and default-branch adoption separately. Docs CI does not deploy the
platform or verify live GitHub/AWS settings.
