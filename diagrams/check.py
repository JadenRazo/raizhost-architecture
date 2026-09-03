"""Geometry checker for diagrams/architecture.svg.

Uses the Inter subsets embedded in the SVG to measure every <text> run with the
exact metrics browsers will use, then fails if any text overflows its box, any
line segment crosses any text, or two text runs overlap.

The target is intentionally fixed to the adjacent architecture.svg file. This
checker accepts no file-path arguments.

    pip install fonttools brotli && python3 diagrams/check.py
"""

import base64
import html
import io
import math
import re
import sys
from pathlib import Path

from fontTools.ttLib import TTFont


SVG_FILENAME = "architecture.svg"
DIAGRAMS_DIRECTORY = Path(__file__).resolve().parent


def read_architecture_svg():
    """Read the one repository-controlled SVG this checker is designed for."""
    if len(sys.argv) != 1:
        raise SystemExit(
            "usage: python3 diagrams/check.py\n"
            "file-path arguments are rejected; the checker only reads "
            "diagrams/architecture.svg"
        )

    unresolved_path = DIAGRAMS_DIRECTORY / SVG_FILENAME
    if unresolved_path.is_symlink():
        raise SystemExit("refusing to read architecture.svg through a symbolic link")

    try:
        svg_path = unresolved_path.resolve(strict=True)
    except OSError as error:
        raise SystemExit(f"cannot resolve {unresolved_path}: {error}") from error

    try:
        svg_path.relative_to(DIAGRAMS_DIRECTORY)
    except ValueError as error:
        raise SystemExit(
            "refusing to read architecture.svg outside the diagrams directory"
        ) from error

    if svg_path.name != SVG_FILENAME or not svg_path.is_file():
        raise SystemExit("diagrams/architecture.svg is not a regular SVG file")

    return svg_path.read_text(encoding="utf-8")


_svg = read_architecture_svg()
fonts = {}
for match in re.finditer(
    r"font-weight:(\d+);src:url\(data:font/woff2;base64,([A-Za-z0-9+/=]+)\)",
    _svg,
):
    fonts[int(match.group(1))] = TTFont(
        io.BytesIO(base64.b64decode(match.group(2)))
    )
assert 400 in fonts and 600 in fonts, "embedded Inter 400/600 not found"


def width(text, size, weight, letter_spacing=0):
    """Return the rendered advance width for one SVG text run."""
    font = fonts[weight]
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]
    units_per_em = font["head"].unitsPerEm
    advance = 0
    for character in text:
        glyph = cmap.get(ord(character)) or cmap.get(ord("x"))
        advance += hmtx[glyph][0]
    return advance * size / units_per_em + letter_spacing * len(text)


def rotate_bbox(box, transform):
    """Apply one SVG rotate(angle [cx cy]) transform to a bounding box."""
    match = re.fullmatch(
        r"\s*rotate\(\s*([-+\d.]+)(?:[ ,]+([-+\d.]+)[ ,]+([-+\d.]+))?\s*\)\s*",
        transform,
    )
    if not match:
        raise ValueError(f"unsupported text transform: {transform!r}")

    angle = math.radians(float(match.group(1)))
    center_x = float(match.group(2) or 0)
    center_y = float(match.group(3) or 0)
    cosine = math.cos(angle)
    sine = math.sin(angle)
    x0, y0, x1, y1 = box
    points = []
    for x, y in ((x0, y0), (x0, y1), (x1, y0), (x1, y1)):
        dx = x - center_x
        dy = y - center_y
        points.append(
            (
                center_x + dx * cosine - dy * sine,
                center_y + dx * sine + dy * cosine,
            )
        )
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return min(xs), min(ys), max(xs), max(ys)


classes = {
    "bandt": (13, 600, 0.4, True),
    "h": (14, 600, 0, False),
    "s": (12, 400, 0, False),
    "m": (11, 400, 0, False),
    "lbl": (11, 400, 0, False),
}
texts = []
parse_errors = []
for match in re.finditer(r"<text([^>]*)>(.*?)</text>", _svg):
    attributes, text = match.group(1), html.unescape(match.group(2))
    x = float(re.search(r'x="([-+\d.]+)"', attributes).group(1))
    y = float(re.search(r'y="([-+\d.]+)"', attributes).group(1))
    class_match = re.search(r'class="(\w+)"', attributes)
    if class_match:
        size, weight, letter_spacing, uppercase = classes[class_match.group(1)]
    else:
        size_match = re.search(r'font-size="([\d.]+)"', attributes)
        size = float(size_match.group(1)) if size_match else 11
        weight = 600 if 'font-weight="600"' in attributes else 400
        letter_spacing = 0
        uppercase = False
    if uppercase:
        text = text.upper()

    anchor_match = re.search(r'text-anchor="(\w+)"', attributes)
    anchor = anchor_match.group(1) if anchor_match else "start"
    text_width = width(text, size, weight, letter_spacing)
    x0 = x - text_width / 2 if anchor == "middle" else (x - text_width if anchor == "end" else x)
    box = (x0, y - size * 0.75, x0 + text_width, y + size * 0.25)

    transform_match = re.search(r'transform="([^"]+)"', attributes)
    if transform_match:
        try:
            box = rotate_bbox(box, transform_match.group(1))
        except ValueError as error:
            parse_errors.append(str(error))

    x0, y0, x1, y1 = box
    texts.append(
        {
            "t": text,
            "x0": x0,
            "x1": x1,
            "y0": y0,
            "y1": y1,
            "cls": class_match.group(1) if class_match else "raw",
        }
    )

rects = []
for match in re.finditer(
    r'<rect class="box[^"]*" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"',
    _svg,
):
    x, y, box_width, box_height = map(float, match.groups())
    rects.append((x, y, x + box_width, y + box_height))
# Cylinder + pill approximations.
rects.append((252, 580, 372, 670))
rects.append((120, 24, 380, 64))

PAD = 8
issues = list(parse_errors)
for text in texts:
    if text["cls"] in ("lbl", "bandt", "raw"):
        continue
    center_x = (text["x0"] + text["x1"]) / 2
    center_y = (text["y0"] + text["y1"]) / 2
    containing = [
        rect
        for rect in rects
        if rect[0] <= center_x <= rect[2] and rect[1] <= center_y <= rect[3]
    ]
    if not containing:
        issues.append(f"NOBOX  {text['t']!r}")
        continue
    rect = containing[0]
    if text["x0"] < rect[0] + PAD or text["x1"] > rect[2] - PAD:
        required = max(
            rect[0] + PAD - text["x0"],
            text["x1"] - rect[2] + PAD,
        )
        issues.append(
            f"OVERFLOW {text['t']!r}: text {text['x0']:.0f}-{text['x1']:.0f} "
            f"vs box {rect[0]:.0f}-{rect[2]:.0f} (need +{required:.0f}px)"
        )

# Orthogonal line segments versus text bounding boxes.
segments = []
for match in re.finditer(r'<path class="l[d]?" d="([^"]+)"', _svg):
    points = re.findall(r"([ML])\s*([-+\d.]+)\s+([-+\d.]+)", match.group(1))
    points = [(float(x), float(y)) for _, x, y in points]
    for start, end in zip(points, points[1:]):
        segments.append((start, end, match.group(1)))


def hits_text(segment, text, pad=2):
    """Return whether an orthogonal segment enters a text bounding box."""
    (x1, y1), (x2, y2), _ = segment
    x0 = text["x0"] - pad
    x3 = text["x1"] + pad
    y0 = text["y0"] - pad
    y3 = text["y1"] + pad
    if x1 == x2:
        return x0 <= x1 <= x3 and min(y1, y2) < y3 and max(y1, y2) > y0
    if y1 == y2:
        return y0 <= y1 <= y3 and min(x1, x2) < x3 and max(x1, x2) > x0
    return False


for segment in segments:
    for text in texts:
        if hits_text(segment, text):
            issues.append(
                f"LINE-THROUGH-TEXT {text['t']!r} by seg {segment[0]}->{segment[1]}"
            )

# Text-versus-text overlap, including transformed labels.
for index, first in enumerate(texts):
    for second in texts[index + 1 :]:
        if (
            first["x0"] < second["x1"]
            and second["x0"] < first["x1"]
            and first["y0"] < second["y1"]
            and second["y0"] < first["y1"]
        ):
            issues.append(f"TEXT-OVERLAP {first['t']!r} / {second['t']!r}")

for issue in issues:
    print(issue)
print("issues:", len(issues))
sys.exit(1 if issues else 0)
