#!/usr/bin/env bash
set -Eeuo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
image="minlag/mermaid-cli@sha256:99c983b3ab4e14033f2880bc1b9de17e5090b4515dabd63fe9cf8c0ae6130956"
names=(request-flow deploy-flow client-provisioning owner-publishing llm-data-flow
  ci-cd-flow deployment-identity portal-authorization portal-rollout
  preview-and-live client-site-cicd publish-status)

python3 "${repo_root}/diagrams/overview.py"
for name in "${names[@]}"; do
  if [[ -n "${MMDC_BIN:-}" ]]; then
    extra=()
    [[ -z "${PUPPETEER_CONFIG:-}" ]] || extra+=(-p "${PUPPETEER_CONFIG}")
    "${MMDC_BIN}" -i "${repo_root}/diagrams/${name}.mmd" \
      -o "${repo_root}/diagrams/${name}.svg" \
      -c "${repo_root}/diagrams/mermaid-config.json" -b white "${extra[@]}"
  else
    docker run --rm \
      --user "$(id -u):$(id -g)" \
      --volume "${repo_root}:/data" \
      "${image}" \
      -i "/data/diagrams/${name}.mmd" \
      -o "/data/diagrams/${name}.svg" \
      -c "/data/diagrams/mermaid-config.json" -b white
  fi
done

python3 - "${repo_root}" <<'PY'
from pathlib import Path
import hashlib
import re
import sys

root = Path(sys.argv[1])
titles = {
    "request-flow": "RaizHost request routing",
    "deploy-flow": "RaizHost repository deployment paths",
    "client-provisioning": "Client hosting and site integration",
    "owner-publishing": "Owner draft, preview, and publication",
    "llm-data-flow": "LLM Tracker collection and reader paths",
    "ci-cd-flow": "RaizHost CI checks and release selection",
    "deployment-identity": "RaizHost deployment identity and AWS permission gates",
    "portal-authorization": "Portal content authorization gates",
    "portal-rollout": "Portal container rollout and recovery gates",
    "preview-and-live": "Showers preview and live publication branches",
    "client-site-cicd": "Showers client website CI/CD pipeline",
    "publish-status": "Owner publication status and confirmation",
}
for name, title in titles.items():
    path = root / "diagrams" / f"{name}.svg"
    svg = path.read_text()
    svg = re.sub(r'<style[^>]*>@import url\([^<]+</style>', "", svg)
    # Put the canvas after the root, before any diagram geometry.
    svg = re.sub(r'(<svg\b[^>]*>)', lambda m: m[1] +
        f'<title>{title}</title><desc>The embedding guide provides a complete text walkthrough of this flow.</desc>'
        '<rect width="100%" height="100%" fill="#ffffff"/>', svg, count=1)
    path.write_text(svg)

paths = sorted((root / "diagrams").glob("*.mmd"))
lines = []
for source in paths:
    for path in [source, source.with_suffix(".svg")]:
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.relative_to(root)}")
(root / "diagrams" / "rendered.sha256").write_text("\n".join(lines) + "\n")
PY

python3 "${repo_root}/diagrams/overview.py" --check
python3 "${repo_root}/diagrams/check_docs.py"
python3 "${repo_root}/diagrams/check.py"
