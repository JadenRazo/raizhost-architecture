"""Generate the overview SVG and Mermaid sketch from the same nodes and edges.

No renderer or network is needed. The existing embedded Inter subsets live in
fonts.css. check.py measures those exact fonts against the generated geometry.
"""

from html import escape
from pathlib import Path
import argparse


ROOT = Path(__file__).resolve().parent
WIDTH, HEIGHT = 1120, 1190
COLORS = {
    "source": ("#f8fafc", "#64748b"),
    "edge": ("#fff7ed", "#c2410c"),
    "runtime": ("#eff6ff", "#2563eb"),
    "data": ("#ecfdf5", "#047857"),
}
# id, x, y, width, height, kind, text lines. Coordinates are SVG pixels.
NODES = [
    ("sites", 28, 234, 236, 80, "source", ["raizhost.com", "Client sites and demos"]),
    ("site_cf", 304, 234, 188, 80, "edge", ["CloudFront", "Website distribution"]),
    ("site_s3", 532, 234, 240, 80, "data", ["Private S3 origin", "Built HTML and assets"]),
    ("forms", 28, 374, 236, 80, "source", ["Marketing browser code", "Quote form / admin / CRM"]),
    ("quote_api", 304, 374, 188, 80, "runtime", ["HTTP API Gateway", "Separate API origins"]),
    ("quote_fn", 532, 374, 240, 80, "runtime", ["Quote / CRM Lambdas", "Validate and authorize"]),
    ("ddb", 812, 374, 280, 80, "data", ["DynamoDB", "Separate quote and CRM tables"]),
    ("owner", 28, 514, 236, 80, "source", ["app.raizhost.com", "Owner signs in and edits"]),
    ("app_cf", 304, 514, 188, 80, "edge", ["CloudFront", "HTTPS → ALB"]),
    ("portal", 532, 514, 240, 80, "runtime", ["Next.js owner portal", "Docker on the EC2 anchor"]),
    ("editor_db", 812, 514, 280, 80, "data", ["Portal Postgres database", "Accounts, drafts, publish records"]),
    ("reader", 28, 654, 236, 80, "source", ["llm.raizhost.com", "Reader opens dashboard / RSS"]),
    ("llm_cf", 304, 654, 188, 80, "edge", ["CloudFront", "Tracker distribution"]),
    ("web", 532, 654, 240, 80, "runtime", ["HTTP API → web Lambda", "Next.js + Lambda Web Adapter"]),
    ("tracker_db", 812, 654, 280, 80, "data", ["PgBouncer → Postgres", "Tracker database on anchor"]),
    ("bundles", 304, 792, 188, 80, "data", ["Private S3 assets", "/_next/static/*"]),
    ("pollers", 812, 792, 280, 80, "runtime", ["Scheduled poller Lambdas", "EventBridge invokes three tiers", "Fetch sources; normalize records"]),
    ("publish", 28, 1004, 236, 90, "source", ["Preview or Publish", "Save + authorize + validate"]),
    ("repo", 304, 1004, 188, 90, "source", ["Client repository", "Content JSON commit", "Selected branch push"]),
    ("build", 532, 1004, 240, 90, "runtime", ["Client site workflow", "Checks + build + AWS writes"]),
    ("output", 812, 1004, 280, 90, "data", ["S3 + CloudFront", "Preview prefix or public site"]),
]
# source, destination, async, SVG path, optional text and its coordinates.
EDGES = []
for row in [("sites", "site_cf", "site_s3"), ("forms", "quote_api", "quote_fn", "ddb"),
            ("owner", "app_cf", "portal", "editor_db"),
            ("reader", "llm_cf", "web", "tracker_db"),
            ("publish", "repo", "build", "output")]:
    for source, target in zip(row, row[1:]):
        a = next(n for n in NODES if n[0] == source)
        b = next(n for n in NODES if n[0] == target)
        y = a[2] + a[4] / 2
        EDGES.append((source, target, row[0] == "publish",
                      f"M{a[1] + a[3]} {y:g} L{b[1]} {y:g}", None))
EDGES.extend([
    ("llm_cf", "bundles", False, "M398 734 L398 792", ("hashed bundles", 410, 769)),
    ("pollers", "tracker_db", True, "M952 792 L952 734", ("writes", 964, 769)),
])


def render_svg():
    font_css = (ROOT / "fonts.css").read_text()
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title description">',
             '<title id="title">RaizHost: serving paths and owner publication</title>',
             '<desc id="description">Read each horizontal lane from browser to origin and data. Cloudflare provides DNS only. Static websites use S3 through CloudFront; quote and CRM APIs are called directly. The portal uses an HTTPS ALB origin and private HTTP to a single anchor target. LLM Tracker uses a web Lambda and separate scheduled pollers. Portal and tracker databases share the anchor. Owner publication commits to a client repository whose workflow builds the public site.</desc>',
             '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10z" fill="#64748b"/></marker></defs>',
             '<style>' + font_css + '\n' +
             'text{font-family:Inter,sans-serif;fill:#172b35}.h{font-size:16px;font-weight:600}.s{font-size:14px;font-weight:400}.m,.lbl{font-size:12px;font-weight:400}.bandt{font-size:14px;font-weight:600;letter-spacing:.4px;text-transform:uppercase}.l,.ld{fill:none;stroke:#64748b;stroke-width:1.7;marker-end:url(#arrow)}.ld{stroke-dasharray:5 4}</style>',
             '<rect width="100%" height="100%" fill="#ffffff"/>']

    def text(x, y, value, attributes='font-size="14"'):
        parts.append(f'<text x="{x}" y="{y}" {attributes}>{escape(value)}</text>')

    text(28, 44, "RaizHost system", 'font-size="28" font-weight="600"')
    text(28, 74, "Application paths · source and scoped AWS routing checked 11 October 2026", 'font-size="16"')
    parts.append('<rect x="28" y="102" width="1064" height="74" rx="8" fill="#f8fafc" stroke="#cbd5e1"/>')
    text(48, 131, "DNS: Cloudflare resolves the hostname. HTTPS: the browser connects to CloudFront.", 'font-size="16" font-weight="600"')
    text(48, 155, "CloudFront boxes below are separate distributions. Origin arrows apply on a cache miss or revalidation.")
    for y, label in [(218, "01  Read a website"), (358, "02  Submit or manage an inquiry"),
                     (498, "03  Use the owner portal"), (638, "04  Read LLM updates"),
                     (988, "05  Build a preview or publish an owner's update")]:
        text(28, y, label, 'class="bandt"')
    for ident, x, y, w, h, kind, lines in NODES:
        fill, stroke = COLORS[kind]
        parts.append(f'<rect class="box {kind}" x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}"/>')
        baseline = y + (h - len(lines) * 21) / 2 + 16
        for index, value in enumerate(lines):
            text(x + w / 2, baseline + index * 21, value,
                 f'class="{"h" if index == 0 else "s"}" text-anchor="middle"')
    for source, target, asynchronous, path, label in EDGES:
        parts.append(f'<path class="{"ld" if asynchronous else "l"}" d="{path}"/>')
        if label:
            value, x, y = label
            text(x, y, value, 'class="lbl"')
    text(812, 268, "Visitors read built files.")
    text(812, 291, "The portal is outside this request path.")
    text(532, 815, "Web requests read stored data.")
    text(532, 840, "Scheduled workers collect updates.")
    text(28, 924, "ALB → portal uses private HTTP. Two ALB zones still lead to one anchor, its databases and local media.")
    text(28, 948, "Tracker workers also use anchor NAT. An anchor outage affects editing, database reads and collection.")
    parts.append('<path class="l" d="M28 1136 L64 1136"/>')
    text(76, 1140, "Request / data access", 'class="lbl"')
    parts.append('<path class="ld" d="M264 1136 L300 1136"/>')
    text(312, 1140, "Scheduled work / publication", 'class="lbl"')
    text(28, 1170, "Publication status: portal polls the exact client workflow run. Full path: docs/owner-publishing.md", 'font-size="12"')
    parts.append('</svg>\n')
    return '\n'.join(parts)


def render_mermaid():
    parts = ['%% Generated by overview.py; edit its shared nodes and edges.',
             '%% Cloudflare supplies DNS answers; HTTPS goes directly to CloudFront.', 'flowchart LR']
    for kind, (fill, stroke) in COLORS.items():
        parts.append(f'  classDef {kind} fill:{fill},stroke:{stroke},color:#172b35')
    for ident, x, y, w, h, kind, lines in NODES:
        label = '<br/>'.join(lines)
        parts.append(f'  {ident}["{label}"]:::{kind}')
    for source, target, asynchronous, path, label in EDGES:
        arrow = '-.->' if asynchronous else '-->'
        parts.append(f'  {source} {arrow} {target}')
    return '\n'.join(parts) + '\n'


def mobile_lane(canvas, title, ids, note, top, nodes, edges):
    """Draw one lane, using only its existing shared-graph connectors."""
    y = canvas.text(22, top, title, 356, 23, 600) + 12
    for i, ident in enumerate(ids):
        _, _, _, _, _, kind, lines = nodes[ident]
        start, box_top = len(canvas.parts), y
        y = canvas.text(36, y+16, lines[0], 328, 20, 600)
        y = canvas.text(36, y+5, ". ".join(lines[1:]), 328, 18) + 16
        fill, stroke = COLORS[kind]
        canvas.parts.insert(start, f'<rect x="20" y="{box_top:g}" width="360" height="{y-box_top:g}" rx="8" fill="{fill}" stroke="{stroke}"/>')
        if i+1 >= len(ids):
            continue
        edge = (ident, ids[i+1])
        if edge in edges:
            canvas.arrow(y+7, y+25)
            if edges[edge]:
                canvas.parts[-1] = canvas.parts[-1].replace('stroke-width="2"', 'stroke-width="2" stroke-dasharray="5 4"')
        y += 34
    return canvas.text(22, y+12, note, 356, 17) + 30


def render_mobile():
    """Read the same graph by lane at phone width; no second topology source."""
    from journeys import Canvas, FONT_CSS, check_geometry
    canvas = Canvas(400)
    y = canvas.text(22, 20, "RaizHost system", 356, 27, 600) + 10
    y = canvas.text(22, y, "Application paths checked 11 October 2026. Cloudflare answers DNS; HTTPS goes to CloudFront or the configured API.", 356, 17) + 24
    rows = [
        ("Read a website", ["sites", "site_cf", "site_s3"], "Visitors read built files; the portal is outside this request path."),
        ("Submit or manage an inquiry", ["forms", "quote_api", "quote_fn", "ddb"], "Quote and CRM browser calls go directly to their API origins."),
        ("Use the owner portal", ["owner", "app_cf", "portal", "editor_db"], "ALB to anchor is private HTTP. Two ALB zones lead to one host; they do not provide app or database failover."),
        ("Read LLM updates", ["reader", "llm_cf", "web", "tracker_db"], "The web Lambda reads collected records. The database shares the anchor with the portal."),
        ("Tracker assets and collection", ["bundles", "pollers"], "Separate paths: CloudFront reads bundles from S3. EventBridge invokes pollers, which use anchor NAT and write the tracker database."),
        ("Preview or Publish", ["publish", "repo", "build", "output"], "The portal polls the exact client workflow. A commit is not yet a deployed website."),
    ]
    nodes = {n[0]: n for n in NODES}
    edges = {(e[0], e[1]): e[2] for e in EDGES}
    covered = [ident for _, ids, _ in rows for ident in ids]
    if len(covered) != len(set(covered)) or set(covered) != set(nodes):
        raise ValueError("Mobile lanes must cover every shared node exactly once")
    for title, ids, note in rows:
        y = mobile_lane(canvas, title, ids, note, y, nodes, edges)
    y = canvas.text(22, y, "Solid arrows: request or data access. Dashed arrows: publication. Read the companion guides for recovery and verification limits.", 356, 17) + 22
    issues = check_geometry(canvas.geometry)
    if issues:
        raise ValueError('\n'.join(issues))
    return '\n'.join([
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 {y:g}" role="img" aria-labelledby="title description">',
        '<title id="title">RaizHost application paths, narrow layout</title>',
        '<desc id="description">The same nodes and paths as the desktop system overview, grouped vertically by application.</desc>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0 L10 5 L0 10z" fill="#64748b"/></marker></defs>',
        '<style>'+FONT_CSS+'text{font-family:Inter,sans-serif;font-kerning:none;font-variant-ligatures:none}</style>',
        '<rect width="100%" height="100%" fill="#ffffff"/>', *canvas.parts, '</svg>\n'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Fail if generated overview assets are stale')
    args = parser.parse_args()
    for name, content in [('architecture.svg', render_svg()), ('architecture-mobile.svg', render_mobile()), ('architecture.mmd', render_mermaid())]:
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_text() != content:
                raise SystemExit(f'{name} is stale; run python3 diagrams/overview.py')
        else:
            path.write_text(content)
    print('Overview SVG and Mermaid sketch match shared graph' if args.check else 'Generated overview SVG and Mermaid sketch')


if __name__ == '__main__':
    main()
