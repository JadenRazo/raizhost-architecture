"""Render readable journey SVGs and matching Mermaid sketches from journeys.json.

Connectors occupy the gap between stages, never the text column. Desktop and
narrow variants share content, with line wrapping measured in their embedded font.
"""

from __future__ import annotations

import argparse
import base64
import copy
import html
import io
import json
from pathlib import Path
import re

from fontTools.ttLib import TTFont


ROOT = Path(__file__).resolve().parent
SPECS = json.loads((ROOT / "journeys.json").read_text())
FONT_CSS = (ROOT / "fonts.css").read_text()
FONTS = {}
for weight, data in re.findall(
    r"font-weight:(\d+);src:url\(data:font/woff2;base64,([A-Za-z0-9+/=]+)\)", FONT_CSS
):
    FONTS[int(weight)] = TTFont(io.BytesIO(base64.b64decode(data)))


def measure(value, size, weight=400):
    font = FONTS[weight]
    cmap = font.getBestCmap()
    advances = font["hmtx"]
    return sum(advances[cmap.get(ord(c), cmap[ord("x")])][0] for c in value) * size / font["head"].unitsPerEm


def wrap(value, width, size, weight=400):
    lines = []
    line = ""
    for word in value.split():
        candidate = f"{line} {word}".strip()
        if line and measure(candidate, size, weight) > width:
            lines.append(line)
            line = word
        else:
            line = candidate
        if measure(line, size, weight) > width:
            raise ValueError(f"unbreakable label is too wide: {line}")
    if line:
        lines.append(line)
    return lines


def intersects(segment, box, padding=2):
    """Axis-aligned connector versus padded text rectangle."""
    x1, y1, x2, y2 = segment
    left, top, right, bottom = box
    left, top, right, bottom = left-padding, top-padding, right+padding, bottom+padding
    if x1 == x2:
        return left <= x1 <= right and max(min(y1, y2), top) <= min(max(y1, y2), bottom)
    if y1 == y2:
        return top <= y1 <= bottom and max(min(x1, x2), left) <= min(max(x1, x2), right)
    raise ValueError("Journey connectors must remain horizontal or vertical")


def check_geometry(geometry):
    issues = []
    for label in geometry["texts"]:
        x0, y0, x1, y1 = label["box"]
        bx0, by0, bx1, by1 = label["container"]
        # Baseline subtraction can differ from the original top by ~1e-13.
        epsilon = 0.001
        if x0 < bx0-epsilon or y0 < by0-epsilon or x1 > bx1+epsilon or y1 > by1+epsilon:
            issues.append(f"text outside its reserved space: {label['value']}")
        for line in geometry["lines"]:
            if intersects(line, label["box"]):
                issues.append(f"connector crosses text: {label['value']}")
    for i, first in enumerate(geometry["texts"]):
        a, b, c, d = first["box"]
        for second in geometry["texts"][i+1:]:
            e, f, g, h = second["box"]
            if max(a, e) < min(c, g) and max(b, f) < min(d, h):
                issues.append(f"text overlap: {first['value']} / {second['value']}")
    return issues


class Canvas:
    def __init__(self, width):
        self.width = width
        self.parts = []
        self.geometry = {"texts": [], "lines": []}

    def rect(self, x, y, width, height, fill, stroke="none", radius=8):
        self.parts.append(f'<rect x="{x:g}" y="{y:g}" width="{width:g}" height="{height:g}" rx="{radius}" fill="{fill}" stroke="{stroke}"/>')

    def text(self, x, top, value, width, size=20, weight=400, color="#1e293b", line_height=None):
        line_height = line_height or size * 1.4
        # Leave breathing room for browser rasterization and fallback symbols.
        lines = wrap(value, width-12, size, weight)
        for i, line in enumerate(lines):
            baseline = top + size + i * line_height
            box = [x, baseline-size, x+measure(line, size, weight), baseline+size*.25]
            self.geometry["texts"].append({"value": line, "box": box,
                "container": [x, top, x+width, top+len(lines)*line_height]})
            self.parts.append(f'<text x="{x:g}" y="{baseline:g}" font-size="{size:g}" font-weight="{weight}" fill="{color}">{html.escape(line)}</text>')
        return top + len(lines) * line_height

    def arrow(self, top, bottom):
        x = self.width / 2
        self.geometry["lines"].append([x, top, x, bottom])
        self.parts.append(f'<path class="connector" d="M{x:g} {top:g} V{bottom:g}" fill="none" stroke="#64748b" stroke-width="2" marker-end="url(#arrow)"/>')


def draw_stage(canvas, stage, number, top, narrow, ordered):
    margin = 16 if narrow else 24
    padding = 18 if narrow else 24
    x = margin + padding
    content_width = canvas.width - 2*x
    start = len(canvas.parts)
    y = top + padding
    y = canvas.text(x, y, stage["actor"], content_width, 13 if narrow else 14, 600, "#334155") + 5
    heading = f"{number}. {stage['title']}" if ordered else stage["title"]
    y = canvas.text(x, y, heading, content_width, 20 if narrow else 24, 600, "#0f172a") + 8
    if stage.get("detail"):
        y = canvas.text(x, y, stage["detail"], content_width, 18 if narrow else 20)
    branches = stage.get("branches", [])
    if branches:
        # These panels are coequal. Their meaning (concurrent or alternative)
        # is explicit in the stage heading and note, never inferred from order.
        branch_gap = 18
        column_width = content_width if narrow else (content_width-branch_gap)/2
        branch_top = y + 4
        branch_bottom = branch_top
        for index, branch in enumerate(branches):
            bx = x if narrow else x + index*(column_width+branch_gap)
            by = branch_bottom + 12 if narrow and index else branch_top
            content_x = bx + 14
            inner_width = column_width-28
            panel_start = len(canvas.parts)
            by = canvas.text(content_x, by+12, branch["actor"], inner_width, 13, 600) + 4
            by = canvas.text(content_x, by, branch["title"], inner_width, 19 if narrow else 20, 600) + 6
            by = canvas.text(content_x, by, branch["detail"], inner_width, 18) + 14
            panel_y = branch_bottom+12 if narrow and index else branch_top
            panel = f'<rect x="{bx:g}" y="{panel_y:g}" width="{column_width:g}" height="{by-panel_y:g}" rx="6" fill="#f1f5f9"/>'
            canvas.parts.insert(panel_start, panel)
            branch_bottom = max(branch_bottom, by)
        y = branch_bottom
    for field, label, color, fill in [
        ("stop", "STOP — ", "#9a3412", "#fff7ed"),
        ("note", "", "#334155", "#f8fafc"),
    ]:
        if not stage.get(field):
            continue
        y += 12
        note_start = len(canvas.parts)
        note_y = y
        y = canvas.text(x+12, y+10, label+stage[field], content_width-24, 17, 400, color) + 10
        canvas.parts.insert(note_start, f'<rect x="{x:g}" y="{note_y:g}" width="{content_width:g}" height="{y-note_y:g}" rx="6" fill="{fill}"/>')
    bottom = y + padding
    canvas.parts.insert(start, f'<rect class="stage" x="{margin}" y="{top:g}" width="{canvas.width-2*margin}" height="{bottom-top:g}" rx="8" fill="#ffffff" stroke="#cbd5e1"/>')
    return bottom


def render(spec, narrow=False):
    canvas = Canvas(400 if narrow else 840)
    margin = 20 if narrow else 28
    y = canvas.text(margin, 20, spec["title"], canvas.width-2*margin, 27 if narrow else 32, 600, "#0f172a") + 8
    y = canvas.text(margin, y, spec["subtitle"], canvas.width-2*margin, 18) + 24
    ordered = spec.get("flow", True)
    for number, stage in enumerate(spec["stages"], 1):
        bottom = draw_stage(canvas, stage, number, y, narrow, ordered)
        if number < len(spec["stages"]):
            if ordered:
                canvas.arrow(bottom+8, bottom+27)
            y = bottom + 36
    y = canvas.text(margin, bottom+22, spec["footer"], canvas.width-2*margin, 17) + 24
    issues = check_geometry(canvas.geometry)
    if issues:
        raise ValueError("\n".join(issues))
    content = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {canvas.width} {y:g}" role="img" aria-labelledby="title description">',
        f'<title id="title">{html.escape(spec["title"])}</title>',
        f'<desc id="description">{html.escape(spec["subtitle"])} The companion guide explains each stage and exception.</desc>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="#64748b"/></marker></defs>',
        '<style>'+FONT_CSS+'\ntext{font-family:Inter,sans-serif;font-kerning:none;font-variant-ligatures:none}</style>',
        '<rect width="100%" height="100%" fill="#ffffff"/>', *canvas.parts, '</svg>\n']
    return "\n".join(content), canvas.geometry


def mermaid(spec):
    lines = ["%% Generated by journeys.py from journeys.json; do not edit this sketch.",
             "%% The companion SVG uses staged layouts for human reading.",
             "%% " + spec["footer"], "flowchart TB"]
    stages = spec["stages"]
    ids = [stage.get("id", f"s{i}") for i, stage in enumerate(stages, 1)]
    for index, (ident, stage) in enumerate(zip(ids, stages)):
        label = f"{stage['actor']}<br/>{stage['title']}"
        if stage.get("detail"):
            label += "<br/>" + html.escape(stage["detail"], quote=True)
        lines.append(f'  {ident}["{label}"]')
        if stage.get("stop"):
            lines.append(f'  {ident} -->|"rejected / paused"| {ident}_stop["{html.escape(stage["stop"], quote=True)}"]')
        if stage.get("note"):
            lines.append(f'  {ident} -.-> {ident}_note["{html.escape(stage["note"], quote=True)}"]')
        branches = stage.get("branches", [])
        for n, branch in enumerate(branches):
            child = f"{ident}_{n}"
            label = html.escape(branch["actor"]+": "+branch["title"]+". "+branch["detail"], quote=True)
            lines.append(f'  {ident} --> {child}["{label}"]')
            if index < len(ids)-1 and spec.get("flow", True):
                if branch.get("observe"):
                    lines.append(f'  {child} -.->|"observed while running or complete"| {ids[index+1]}')
                else:
                    lines.append(f'  {child} --> {ids[index+1]}')
        if not branches and index < len(ids)-1 and spec.get("flow", True):
            lines.append(f'  {ident} -->|"continue if accepted"| {ids[index+1]}')
    for source, target in spec.get("edges", []):
        lines.append(f"  {source} --> {target}")
    return "\n".join(lines) + "\n"


def self_test():
    _, geometry = render(SPECS["owner-publishing"])
    assert not check_geometry(geometry)
    label = geometry["texts"][0]
    x0, y0, x1, y1 = label["box"]
    broken = copy.deepcopy(geometry)
    broken["lines"].append([x0-10, (y0+y1)/2, x1+10, (y0+y1)/2])
    assert any("connector crosses" in item for item in check_geometry(broken)), "missed injected crossing"
    broken = copy.deepcopy(geometry)
    broken["texts"][0]["box"][2] = broken["texts"][0]["container"][2] + 20
    assert any("outside" in item for item in check_geometry(broken)), "missed injected overflow"
    broken = copy.deepcopy(geometry)
    broken["texts"].append(copy.deepcopy(label))
    assert any("text overlap" in item for item in check_geometry(broken)), "missed injected text overlap"
    print("Journey geometry rejects injected connector crossings, overflow and overlapping labels")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    for name, spec in SPECS.items():
        if not re.fullmatch(r"[a-z0-9-]+", name):
            raise ValueError("invalid journey filename")
        outputs = {f"{name}.mmd": mermaid(spec)}
        for narrow in [False, True]:
            suffix = "-mobile" if narrow else ""
            outputs[f"{name}{suffix}.svg"] = render(spec, narrow)[0]
        for filename, content in outputs.items():
            path = ROOT / filename
            if args.check:
                if not path.exists() or path.read_text() != content:
                    raise SystemExit(f"{filename} is stale; run python3 diagrams/journeys.py")
            else:
                path.write_text(content)
    print(f"{'Checked' if args.check else 'Rendered'} {len(SPECS)} journeys, desktop and narrow; no geometry collisions")


if __name__ == "__main__":
    main()
