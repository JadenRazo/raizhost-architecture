"""Validate mobile-safe diagram embeds and their source/output manifest."""

from __future__ import annotations

import hashlib
import pathlib
import re
import sys


ROOT = pathlib.Path(__file__).resolve().parents[1]
PAIRS = {
    "request-flow.mmd": "request-flow.svg",
    "deploy-flow.mmd": "deploy-flow.svg",
    "client-provisioning.mmd": "client-provisioning.svg",
}
MANIFEST = ROOT / "diagrams" / "rendered.sha256"


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


issues: list[str] = []
markdown_paths = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
for path in markdown_paths:
    text = path.read_text(encoding="utf-8")
    if re.search(r"^```mermaid\s*$", text, flags=re.MULTILINE):
        issues.append(f"{path.relative_to(ROOT)}: inline Mermaid is not mobile-safe; embed an SVG")

manifest: dict[str, str] = {}
if not MANIFEST.exists():
    issues.append("diagrams/rendered.sha256 is missing")
else:
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  (diagrams/[a-z0-9-]+\.(?:mmd|svg))", line)
        if not match:
            issues.append(f"invalid manifest line: {line!r}")
            continue
        manifest[match.group(2)] = match.group(1)

for source_name, output_name in PAIRS.items():
    for name in (source_name, output_name):
        path = ROOT / "diagrams" / name
        key = f"diagrams/{name}"
        if not path.exists():
            issues.append(f"{key} is missing")
            continue
        expected = manifest.get(key)
        if expected is None:
            issues.append(f"{key} is missing from the render manifest")
        elif digest(path) != expected:
            issues.append(f"{key} changed without refreshing diagrams/rendered.sha256")

    svg_path = ROOT / "diagrams" / output_name
    if svg_path.exists():
        svg = svg_path.read_text(encoding="utf-8")
        if "<svg" not in svg or "viewBox=" not in svg:
            issues.append(f"diagrams/{output_name}: responsive SVG viewBox is missing")
        if "<title" not in svg or "<desc" not in svg:
            issues.append(f"diagrams/{output_name}: accessible title/description is missing")
        if '<rect width="100%" height="100%" fill="#ffffff"/>' not in svg:
            issues.append(f"diagrams/{output_name}: opaque mobile/dark-mode canvas is missing")
        if "@import url(" in svg:
            issues.append(f"diagrams/{output_name}: external stylesheet import is not portable")

for output_name in PAIRS.values():
    tags: list[tuple[pathlib.Path, str]] = []
    for path in markdown_paths:
        text = path.read_text(encoding="utf-8")
        for tag in re.findall(r"<img\b[^>]*>", text, flags=re.IGNORECASE):
            if output_name in tag:
                tags.append((path, tag))
    if not tags:
        issues.append(f"diagrams/{output_name}: rendered asset is not embedded anywhere")
    for path, tag in tags:
        if 'width="100%"' not in tag:
            issues.append(
                f"{path.relative_to(ROOT)}: {output_name} embed must use width=\"100%\""
            )

if issues:
    print("diagram documentation check failed:")
    for issue in issues:
        print(f"- {issue}")
    sys.exit(1)

print(f"diagram documentation check passed ({len(PAIRS)} mobile-safe SVGs)")
