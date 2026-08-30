# Diagram workflow

GitHub's Mermaid rendering is inconsistent across mobile clients, so public documents embed
committed SVGs. The adjacent `.mmd` files remain the editable sources.

Run the renderer after changing `request-flow.mmd`, `deploy-flow.mmd`, or
`client-provisioning.mmd`:

```bash
diagrams/render.sh
```

The script uses the same pinned Mermaid CLI image and config as CI, removes an unused external
Font Awesome import, adds an accessible title/description and opaque white canvas for dark-mode
readability, and refreshes `rendered.sha256`. CI then:

1. renders every Mermaid source to prove the syntax;
2. rejects inline Mermaid fences in public Markdown;
3. rejects a changed source or rendered SVG whose manifest was not refreshed; and
4. runs the custom geometry checker against the hand-drawn overview SVG.

`architecture.svg` is deliberately hand-drawn and checked by `check.py`; `architecture.mmd` is an
editable structural sketch, not its byte-generating source.
