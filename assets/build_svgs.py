#!/usr/bin/env python3
"""
Generates the animated SVGs used by the profile README.

    python assets/build_svgs.py

Emits light + dark variants of:
  * system-{theme}.svg  -- service topology with live packets
  * trace-{theme}.svg   -- request waterfall built from real measured numbers

Everything is self-contained: no external fonts, no scripts, no network calls,
so GitHub renders it straight from the repo.
"""

from pathlib import Path

OUT = Path(__file__).parent

THEMES = {
    "dark": {
        "bg": "#0b0f14",
        "panel": "#11161d",
        "panel2": "#0e131a",
        "grid": "#161c24",
        "line": "#2b333d",
        "text": "#e6edf3",
        "muted": "#7d8590",
        "faint": "#4d5866",
        "accent": "#ff6b4a",
        "teal": "#39d3bb",
    },
    "light": {
        "bg": "#ffffff",
        "panel": "#f7f9fb",
        "panel2": "#fbfcfd",
        "grid": "#f0f3f6",
        "line": "#d5dce4",
        "text": "#161b22",
        "muted": "#5b6672",
        "faint": "#98a3b0",
        "accent": "#c0392b",
        "teal": "#0f766e",
    },
}

MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def paint(template: str, c: dict) -> str:
    for key, val in c.items():
        template = template.replace(f"__{key.upper()}__", val)
    return template.replace("__MONO__", MONO)


# ---------------------------------------------------------------- topology ---

# columns
COL = {
    "ingress": (48, 150),
    "edge": (258, 176),
    "svc": (494, 256),
    "state": (886, 266),
}
ROW_Y = [125, 201, 277]          # box top edge, per row
BOX_H = 54
ROW_MID = [y + BOX_H / 2 for y in ROW_Y]   # 152, 228, 304

SERVICES = [
    ("svc/url-shortener", "redirects + analytics · fastapi"),
    ("svc/readr", "rag over pdfs · langgraph"),
    ("svc/codity", "distributed job scheduler"),
]
STATE = [
    ("redis", "cache-aside · sliding-window limits"),
    ("postgres:16", "the queue itself · 13 tables"),
    ("pgvector", "embeddings · cosine top-k"),
]

# (path id, d, kind) -- kind picks the colour
EDGES = [
    ("p1", "M198,228 H252", "req"),
    ("p2", "M434,228 C462,228 466,152 488,152", "req"),
    ("p3", "M434,228 H488", "req"),
    ("p4", "M434,228 C462,228 466,304 488,304", "req"),
    ("p5", "M750,152 H880", "data"),
    ("p6", "M750,152 C812,152 824,228 880,228", "data"),
    ("p7", "M750,228 C812,228 824,304 880,304", "data"),
    ("p8", "M750,304 C812,304 824,228 880,228", "data"),
]

# (path, begin, dur)
PACKETS = [
    ("p1", 0.0, 1.1), ("p1", 0.55, 1.1),
    ("p2", 1.1, 1.5), ("p3", 1.35, 1.3), ("p4", 1.6, 1.5),
    ("p5", 2.4, 1.2), ("p6", 2.7, 1.4), ("p7", 2.9, 1.4), ("p8", 3.1, 1.4),
]

LOG = [
    ("codity", "worker claims batch — FOR UPDATE SKIP LOCKED · fencing token issued"),
    ("url-shortener", "cache-aside HIT 6.7ms · cold path was 40.0ms"),
    ("readr", "pgvector cosine top-k → groq stream over SSE"),
]

TOPO_CSS = """
  .mono { font-family: __MONO__; }
  .t-title  { font-size: 29px; font-weight: 700; letter-spacing: -0.4px; }
  .t-sub    { font-size: 12px; fill: __MUTED__; }
  .col      { font-size: 9.5px; letter-spacing: 1.6px; fill: __FAINT__; }
  .n-name   { font-size: 13px; fill: __TEXT__; }
  .n-sub    { font-size: 10.5px; fill: __MUTED__; }
  .pill     { font-size: 10.5px; fill: __TEAL__; letter-spacing: 0.3px; }
  .log      { font-size: 11.5px; }
  .wire     { fill: none; stroke: __FAINT__; stroke-width: 1.25; stroke-dasharray: 3 7; }
"""


def node(x, y, w, name, sub, bar_color, name_color=None):
    return f"""  <g>
    <rect x="{x}" y="{y}" width="{w}" height="{BOX_H}" rx="9" fill="__PANEL__" stroke="__LINE__"/>
    <rect x="{x}" y="{y + 12}" width="3" height="{BOX_H - 24}" rx="1.5" fill="{bar_color}"/>
    <text class="mono n-name" x="{x + 17}" y="{y + 23}" fill="{name_color or '__TEXT__'}">{esc(name)}</text>
    <text class="mono n-sub" x="{x + 17}" y="{y + 40}">{esc(sub)}</text>
  </g>"""


def build_topology(theme: str) -> str:
    c = THEMES[theme]
    parts = []

    parts.append(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 450" '
        'width="1200" height="450" role="img" '
        'aria-label="shardul.sys service topology">'
    )
    parts.append("  <title>shardul.sys — service topology</title>")
    parts.append(f"  <style>{TOPO_CSS}</style>")
    parts.append("""  <defs>
    <filter id="glow" x="-300%" y="-300%" width="700%" height="700%">
      <feGaussianBlur stdDeviation="2.6" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <pattern id="grid" width="26" height="26" patternUnits="userSpaceOnUse">
      <path d="M26 0H0V26" fill="none" stroke="__GRID__" stroke-width="1"/>
    </pattern>
  </defs>""")

    # frame
    parts.append('  <rect width="1200" height="450" rx="14" fill="__BG__"/>')
    parts.append('  <rect x="0" y="88" width="1200" height="256" fill="url(#grid)" opacity="0.75"/>')
    parts.append('  <rect x="0.5" y="0.5" width="1199" height="449" rx="14" fill="none" stroke="__LINE__"/>')

    # header
    parts.append('  <text class="mono t-title" x="48" y="46" fill="__TEXT__">shardul'
                 '<tspan fill="__ACCENT__">.sys</tspan></text>')
    parts.append('  <text class="mono t-sub" x="48" y="68">'
                 'backend &amp; ai systems engineer · region in-nanded-1 · SGGS ’27 · uptime: 2024→</text>')
    parts.append('  <g><rect x="962" y="30" width="190" height="26" rx="13" fill="__PANEL2__" stroke="__LINE__"/>'
                 '<circle cx="980" cy="43" r="4" fill="__TEAL__">'
                 '<animate attributeName="opacity" values="0.35;1;0.35" dur="2.4s" repeatCount="indefinite"/>'
                 '</circle>'
                 '<text class="mono pill" x="993" y="47">all systems shipping</text></g>')
    parts.append('  <path d="M48,86 H1152" stroke="__LINE__" stroke-width="1"/>')

    # column captions
    for label, key in (("INGRESS", "ingress"), ("EDGE", "edge"), ("SERVICES", "svc"), ("STATE", "state")):
        parts.append(f'  <text class="mono col" x="{COL[key][0]}" y="112">{label}</text>')

    # wires first so nodes sit on top
    for pid, d, kind in EDGES:
        parts.append(f'  <path id="{pid}" class="wire" d="{d}">'
                     '<animate attributeName="stroke-dashoffset" values="0;-10" dur="1.4s" '
                     'repeatCount="indefinite"/></path>')

    # nodes
    ix, iw = COL["ingress"]
    parts.append(node(ix, ROW_Y[1], iw, "client", "browser · curl · sdk", "__FAINT__", "__MUTED__"))
    ex, ew = COL["edge"]
    parts.append(node(ex, ROW_Y[1], ew, "edge/gateway", "jwt · rbac · rate limit", "__ACCENT__"))
    sx, sw = COL["svc"]
    for i, (name, sub) in enumerate(SERVICES):
        parts.append(node(sx, ROW_Y[i], sw, name, sub, "__ACCENT__"))
    tx, tw = COL["state"]
    for i, (name, sub) in enumerate(STATE):
        parts.append(node(tx, ROW_Y[i], tw, name, sub, "__TEAL__"))

    # packets in flight
    for pid, begin, dur in PACKETS:
        kind = next(k for p, _, k in EDGES if p == pid)
        fill = "__TEAL__" if kind == "data" else "__ACCENT__"
        parts.append(f"""  <circle r="3.2" fill="{fill}" filter="url(#glow)">
    <animateMotion dur="{dur}s" begin="{begin}s" repeatCount="indefinite" rotate="auto">
      <mpath href="#{pid}"/>
    </animateMotion>
    <animate attributeName="opacity" dur="{dur}s" begin="{begin}s"
             values="0;1;1;0" keyTimes="0;0.12;0.85;1" repeatCount="indefinite"/>
  </circle>""")

    # log tail
    parts.append('  <path d="M48,352 H1152" stroke="__LINE__" stroke-width="1"/>')
    for i, (svc, msg) in enumerate(LOG):
        y = 378 + i * 24
        on = 0.10 + i * 0.06          # fraction of the 6s cycle this line appears at
        parts.append(f"""  <text class="mono log" x="48" y="{y}" opacity="0">
    <tspan fill="__TEAL__">[ok]</tspan>
    <tspan fill="__ACCENT__" dx="10">{esc(svc)}</tspan>
    <tspan fill="__MUTED__" dx="10">{esc(msg)}</tspan>
    <animate attributeName="opacity" dur="6s" repeatCount="indefinite"
             values="0;0;1;1;0" keyTimes="0;{on:.3f};{on + 0.03:.3f};0.92;1"/>
  </text>""")

    parts.append("</svg>")
    return paint("\n".join(parts), c)


# ------------------------------------------------------------------ traces ---

BAR_X0, BAR_X1 = 300, 1140
BAR_W = BAR_X1 - BAR_X0

# (label, hint, offset_ms, dur_ms, colour_key, open_ended)
PANEL_A = {
    "title": "GET /{slug}",
    "hint": "url-shortener · redirect hot path",
    "scale": 45.0,
    "ticks": [0, 10, 20, 30, 40],
    "unit": "ms",
    "y": 128,
    "rows": [
        ("postgres lookup", "cold", 0, 40.0, "muted", False),
        ("redis cache-aside", "hit", 0, 6.7, "teal", False),
    ],
}
PANEL_B = {
    "title": "POST /ingest → POST /chat",
    "hint": "readr · pdf becomes an answer",
    "scale": 2600.0,
    "ticks": [0, 500, 1000, 1500, 2000, 2500],
    "unit": "ms",
    "y": 274,
    "rows": [
        ("parse.pdf", "", 0, 200, "accent", False),
        ("embed.gemini", "1536-d", 200, 1300, "accent", False),
        ("vector.search", "pgvector", 1500, 500, "teal", False),
        ("llm.groq.stream", "", 2000, 200, "teal", True),
    ],
}

# (grow start seconds, grow duration seconds) per bar, over a 7s cycle
TIMING = [(0.25, 0.50), (0.55, 0.50), (1.15, 0.35), (1.50, 0.55), (2.05, 0.40), (2.45, 0.35)]
CYCLE = 7.0

TRACE_CSS_HEAD = """
  .mono { font-family: __MONO__; }
  .t-title { font-size: 29px; font-weight: 700; letter-spacing: -0.4px; }
  .t-sub   { font-size: 12px; fill: __MUTED__; }
  .p-name  { font-size: 13px; fill: __ACCENT__; }
  .p-hint  { font-size: 10.5px; fill: __MUTED__; }
  .s-name  { font-size: 11.5px; fill: __TEXT__; }
  .s-hint  { font-size: 10px; fill: __FAINT__; }
  .tick    { font-size: 9.5px; fill: __FAINT__; }
  .dur     { font-size: 11px; fill: __TEXT__; }
  .note    { font-size: 11px; fill: __ACCENT__; }
"""


def cycle_anim(attr: str, hold_val, start: float, end: float, zero="0") -> str:
    """SMIL keyframes over one shared CYCLE: stay at `zero`, ramp to `hold_val`
    between `start` and `end` seconds, hold, then collapse at the end of the loop."""
    k0, k1 = start / CYCLE, end / CYCLE
    return (f'<animate attributeName="{attr}" dur="{CYCLE}s" repeatCount="indefinite" '
            f'calcMode="spline" keySplines="0 0 1 1;.22 1 .36 1;0 0 1 1;.6 0 1 1" '
            f'values="{zero};{zero};{hold_val};{hold_val};{zero}" '
            f'keyTimes="0;{k0:.4f};{k1:.4f};0.93;1"/>')


def build_trace(theme: str) -> str:
    c = THEMES[theme]
    css = [TRACE_CSS_HEAD]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 440" '
        'width="1200" height="440" role="img" '
        'aria-label="Request traces through two production paths">',
        "  <title>trace — measured production paths</title>",
    ]
    body = []

    body.append('  <rect width="1200" height="440" rx="14" fill="__BG__"/>')
    body.append('  <rect x="0.5" y="0.5" width="1199" height="439" rx="14" fill="none" stroke="__LINE__"/>')
    body.append('  <text class="mono t-title" x="48" y="46" fill="__TEXT__">trace'
                '<tspan fill="__ACCENT__">.</tspan></text>')
    body.append('  <text class="mono t-sub" x="48" y="68">'
                'two paths I actually measured — not estimates, not vibes</text>')
    body.append('  <path d="M48,86 H1152" stroke="__LINE__" stroke-width="1"/>')

    bar_index = 0
    for panel in (PANEL_A, PANEL_B):
        py = panel["y"]
        scale = BAR_W / panel["scale"]
        body.append(f'  <text class="mono p-name" x="48" y="{py - 26}">{esc(panel["title"])}</text>')
        body.append(f'  <text class="mono p-hint" x="48" y="{py - 10}">{esc(panel["hint"])}</text>')

        # gridlines
        axis_y = py + len(panel["rows"]) * 32 + 6
        for t in panel["ticks"]:
            gx = BAR_X0 + t * scale
            body.append(f'  <path d="M{gx:.1f},{py - 22} V{axis_y}" stroke="__GRID__" stroke-width="1"/>')
            body.append(f'  <text class="mono tick" x="{gx:.1f}" y="{axis_y + 15}" text-anchor="middle">'
                        f'{t}{panel["unit"] if t == panel["ticks"][-1] else ""}</text>')

        for row_i, (name, hint, off, dur, ckey, open_end) in enumerate(panel["rows"]):
            y = py + row_i * 32
            x = BAR_X0 + off * scale
            w = max(dur * scale, 3)
            start, grow = TIMING[bar_index]
            end = start + grow
            # the cold path is deliberately drab -- it is the path we engineered away
            fill = {"teal": "__TEAL__", "accent": "__ACCENT__", "muted": "__MUTED__"}[ckey]
            alpha = 0.55 if ckey == "muted" else 0.92

            body.append(f'  <text class="mono s-name" x="48" y="{y + 15}">{esc(name)}</text>')
            if hint:
                body.append(f'  <text class="mono s-hint" x="{48 + len(name) * 7.1 + 9:.0f}" y="{y + 15}">'
                            f'{esc(hint)}</text>')
            body.append(f'  <rect x="{BAR_X0}" y="{y}" width="{BAR_W}" height="21" rx="5" '
                        f'fill="__PANEL__" opacity="0.55"/>')
            # the bar grows by animating its own width -- SMIL, no CSS transforms
            body.append(f'  <rect x="{x:.1f}" y="{y}" width="0" height="21" rx="5" '
                        f'fill="{fill}" opacity="{alpha}">'
                        f'{cycle_anim("width", f"{w:.1f}", start, end)}</rect>')
            # the duration label lands the moment the bar finishes
            if open_end:
                lbl, lcol = "→ first token · SSE", ' fill="__MUTED__"'
            else:
                lbl, lcol = f"{dur:g}{panel['unit']}", ""
            body.append(f'  <text class="mono dur" x="{x + w + 12:.1f}" y="{y + 15}"{lcol} opacity="0">'
                        f'{esc(lbl)}'
                        f'<animate attributeName="opacity" dur="{CYCLE}s" repeatCount="indefinite" '
                        f'values="0;0;1;1;0" '
                        f'keyTimes="0;{end / CYCLE:.4f};{(end + 0.15) / CYCLE:.4f};0.93;1"/></text>')
            bar_index += 1

        body.append(f'  <path d="M{BAR_X0},{axis_y} H{BAR_X1}" stroke="__LINE__" stroke-width="1"/>')

    # the punchline, landing just after the redis bar settles
    note_end = TIMING[1][0] + TIMING[1][1]
    body.append(f'  <text class="mono note" x="510" y="175" opacity="0">'
                f'← 6× faster — and the cache is never the source of truth'
                f'<animate attributeName="opacity" dur="{CYCLE}s" repeatCount="indefinite" '
                f'values="0;0;1;1;0" '
                f'keyTimes="0;{note_end / CYCLE:.4f};{(note_end + 0.2) / CYCLE:.4f};0.93;1"/></text>')

    parts.append(f"  <style>{''.join(css)}\n  </style>")
    parts.extend(body)
    parts.append("</svg>")
    return paint("\n".join(parts), c)


if __name__ == "__main__":
    for theme in THEMES:
        (OUT / f"system-{theme}.svg").write_text(build_topology(theme), encoding="utf-8")
        (OUT / f"trace-{theme}.svg").write_text(build_trace(theme), encoding="utf-8")
        print(f"wrote system-{theme}.svg, trace-{theme}.svg")
