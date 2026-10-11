"""Validate diagram sources, responsive embeds, local links and rendered assets."""

from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys
from urllib.parse import unquote, urlsplit


ROOT = pathlib.Path(__file__).resolve().parents[1]
DIAGRAMS = ROOT / "diagrams"
PAIRS = {path.name: path.with_suffix(".svg").name
         for path in sorted(DIAGRAMS.glob("*.mmd"))}
JOURNEYS = json.loads((DIAGRAMS / "journeys.json").read_text())
RESPONSIVE = set(JOURNEYS) | {"architecture"}
MOBILE = {f"{name}-mobile.svg" for name in RESPONSIVE}
OUTPUTS = set(PAIRS.values()) | MOBILE
MANIFEST = DIAGRAMS / "rendered.sha256"
issues: list[str] = []

markdown = {path: path.read_text(encoding="utf-8") for path in sorted(ROOT.rglob("*.md"))
            if not any(part in {".git", "node_modules"} for part in path.parts)}
for path, text in markdown.items():
    if re.search(r"^```mermaid\s*$", text, flags=re.MULTILINE):
        issues.append(f"{path.relative_to(ROOT)}: embed a rendered SVG instead of inline Mermaid")
    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    links += re.findall(r'(?:src|href)="([^"]+)"', text)
    for srcset in re.findall(r'srcset="([^"]+)"', text):
        links += [candidate.strip().split()[0] for candidate in srcset.split(",")]
    for link in links:
        parsed = urlsplit(link.strip("<>"))
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        target = (path.parent / unquote(parsed.path)).resolve()
        if not target.is_relative_to(ROOT):
            issues.append(f"{path.relative_to(ROOT)}: local link escapes repository: {link}")
        elif not target.exists():
            issues.append(f"{path.relative_to(ROOT)}: missing local link target: {link}")

manifest: dict[str, str] = {}
if not MANIFEST.exists():
    issues.append("diagrams/rendered.sha256 is missing")
else:
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (diagrams/[a-z0-9-]+\.(?:mmd|svg))", line)
        if not match:
            issues.append(f"invalid manifest line: {line!r}")
        elif match[2] in manifest:
            issues.append(f"duplicate manifest entry: {match[2]}")
        else:
            manifest[match[2]] = match[1]

expected_paths = {f"diagrams/{name}" for name in set(PAIRS) | OUTPUTS}
actual_paths = {f"diagrams/{p.name}" for p in DIAGRAMS.iterdir() if p.suffix in {".mmd", ".svg"}}
for unexpected in (actual_paths | set(manifest)) - expected_paths:
    issues.append(f"unexpected source/output: {unexpected}")
for key in sorted(expected_paths):
    path = ROOT / key
    if not path.exists():
        issues.append(f"{key} is missing")
    elif key not in manifest:
        issues.append(f"{key} is missing from the render manifest")
    elif hashlib.sha256(path.read_bytes()).hexdigest() != manifest[key]:
        issues.append(f"{key} changed without refreshing diagrams/rendered.sha256")

for name in sorted(OUTPUTS):
    path = DIAGRAMS / name
    if not path.exists():
        continue
    svg = path.read_text(encoding="utf-8")
    if "<svg" not in svg or "viewBox=" not in svg:
        issues.append(f"{name}: responsive SVG viewBox is missing")
    if "<title" not in svg or "<desc" not in svg:
        issues.append(f"{name}: accessible title/description is missing")
    if '<rect width="100%" height="100%" fill="#ffffff"/>' not in svg:
        issues.append(f"{name}: opaque light/dark-mode canvas is missing")
    if "@import url(" in svg:
        issues.append(f"{name}: external stylesheet import is not portable")
    if 'class="edgeLabel"' in svg and not re.search(
        r"\.edgeLabel rect\s*\{\s*opacity:\s*1\s*!important;\s*fill:\s*(?:#ffffff|rgb\(255,\s*255,\s*255\))\s*!important;?\s*\}", svg
    ):
        issues.append(f"{name}: connector labels need an opaque white background")

for name in PAIRS.values():
    found = False
    for path, text in markdown.items():
        for tag in re.findall(r"<img\b[^>]*>", text, flags=re.IGNORECASE):
            src = re.search(r'src="([^"]+)"', tag)
            if not src or pathlib.PurePosixPath(src[1]).name != name:
                continue
            found = True
            if not re.search(r'alt="[^\"]+"', tag) or 'width="100%"' not in tag:
                issues.append(f"{path.relative_to(ROOT)}: {name} needs alt text and width=\"100%\"")
            if pathlib.Path(name).stem in RESPONSIVE:
                pictures = re.findall(r"<picture\b[^>]*>.*?</picture>", text, re.DOTALL)
                mobile_name = pathlib.Path(name).stem + "-mobile.svg"
                if not any(tag in picture and f'/{mobile_name}"' in picture
                           and 'media="(max-width: 600px)"' in picture for picture in pictures):
                    issues.append(f"{path.relative_to(ROOT)}: {name} needs its narrow-screen picture source")
    if not found:
        issues.append(f"{name}: rendered asset is not embedded anywhere")

if issues:
    print("diagram documentation check failed:")
    for issue in issues:
        print(f"- {issue}")
    sys.exit(1)

print(f"Documentation check passed: {len(PAIRS)} diagrams, {len(MOBILE)} narrow variants, links and manifest")
