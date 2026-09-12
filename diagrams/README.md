# Diagram workflow

Public documents embed committed SVGs with text alternatives. Each diagram is also linked
at full size, so its detail remains available when GitHub scales it down on a phone.

## Choose the source

| Diagram | Edit here | What it explains |
| :-- | :-- | :-- |
| System overview | [overview.py](overview.py) | Serving lanes, data boundaries, and owner publication |
| Request routing | [request-flow.mmd](request-flow.mmd) | DNS versus HTTPS, origins, and direct browser APIs |
| Code deployment | [deploy-flow.mmd](deploy-flow.mmd) | The distinct release trigger and artifact path for each repository |
| Client delivery | [client-provisioning.mmd](client-provisioning.mmd) | Hosting authorization, resource creation, and site integration |
| Owner publication | [owner-publishing.mmd](owner-publishing.mmd) | Draft, preview, live publication, and confirmation |
| Tracker data | [llm-data-flow.mmd](llm-data-flow.mmd) | Scheduled collection versus reader requests |

The overview generator produces **both** `architecture.svg` and `architecture.mmd` from
one set of nodes and edges. Its explicit layout keeps the main map readable while the
Mermaid sketch remains useful for inspecting topology. Do not edit either generated output
by hand. `fonts.css` preserves the Inter subsets already embedded in the original diagram.

## Render and check

With Docker, Python 3, and the geometry check's font dependencies installed:

```bash
python3 -m pip install fonttools brotli
diagrams/render.sh
```

The renderer uses Mermaid CLI `11.4.2`, matching CI. For a local CLI installation of that
same version, set `MMDC_BIN` to its executable. An optional `PUPPETEER_CONFIG` file lets
the CLI reuse an installed browser. Browser/download prerequisites belong to the local
environment; they are not production application dependencies.

The script renders flows, adds descriptive titles and a white canvas, strips external
stylesheet imports, and refreshes the source/SVG checksums. The SVG canvas keeps diagram
text readable in GitHub's light and dark themes.

Run the lightweight checks without rerendering:

```bash
python3 diagrams/overview.py --check
python3 diagrams/check_docs.py
python3 diagrams/check.py
```

CI additionally lints Markdown, renders **all six** Mermaid files to validate syntax, and
checks public documentation for private identifiers. The checks cover:

- Overview source/output agreement.
- Every Mermaid source and SVG in the render manifest.
- Local documentation links, SVG embeds, and image text alternatives.
- Portable SVG structure, responsive viewBox, and opaque background.
- Overview labels fitting their boxes, label collisions, and lines crossing text, measured
  with the actual embedded font metrics.

These checks cannot establish that an arrow matches production. Review diagram semantics
against the owning application source and dated deployment/live evidence. Inspect generated
flows visually, including desktop and 375/412/430px document widths; each guide's prose and
tables must explain the path without relying on tiny diagram labels.

The overview's 16px headings and 14px node descriptions are checked by matching metrics in
`check.py`. Update those metrics if the typography changes. Keep a meaningful geometry
failure check when changing the generator or checker.
