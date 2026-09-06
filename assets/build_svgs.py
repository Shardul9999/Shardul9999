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
BOX_H = 50
CANVAS_H = 510
CENTER_Y = 251                          # ingress + edge sit on this line
SVC_ROW_Y = [118, 190, 262, 334]        # 4 services
STATE_ROW_Y = [154, 226, 298]           # 3 backing stores, centred against them

# (name, sub, live)
SERVICES = [
    ("svc/url-shortener", "redirects + analytics · fastapi", False),
    ("svc/health-assistant", "grounded rag · vercel + render", True),
    ("svc/readr", "rag over pdfs · langgraph", False),
    ("svc/codity", "distributed job scheduler", False),
]
STATE = [
    ("redis", "cache-aside · sliding-window limits"),
    ("postgres:16", "the queue itself · neon · 13 tables"),
    ("pgvector", "hnsw · cosine top-5 · floor 0.65"),
]

# (path id, d, kind) -- kind picks the colour
EDGES = [
    ("p1", "M198,251 H252", "req"),
    ("p2", "M434,251 C462,251 466,143 488,143", "req"),
    ("p3", "M434,251 C462,251 466,215 488,215", "req"),
    ("p4", "M434,251 C462,251 466,287 488,287", "req"),
    ("p5", "M434,251 C462,251 466,359 488,359", "req"),
    ("d1", "M750,143 C812,143 824,179 880,179", "data"),
    ("d2", "M750,143 C812,143 824,251 880,251", "data"),
    ("d3", "M750,215 C812,215 824,323 880,323", "data"),
    ("d4", "M750,287 C812,287 824,323 880,323", "data"),
    ("d5", "M750,359 C812,359 824,251 880,251", "data"),
]

# (path, begin, dur)
PACKETS = [
    ("p1", 0.0, 1.1), ("p1", 0.55, 1.1),
    ("p2", 1.1, 1.5), ("p3", 1.3, 1.4), ("p4", 1.5, 1.5), ("p5", 1.7, 1.6),
    ("d1", 2.4, 1.2), ("d2", 2.6, 1.4), ("d3", 2.8, 1.4),
    ("d4", 3.0, 1.4), ("d5", 3.2, 1.5),
]

LOG = [
    ("health-assistant", "red-flag short-circuit in 0.1ms — no retrieval, no model call"),
    ("health-assistant", "27/27 answers cited · 129/129 citations valid · 0% false hits"),
    ("codity", "worker claims batch — FOR UPDATE SKIP LOCKED · fencing token issued"),
]

TOPO_CSS = """
  .mono { font-family: __MONO__; }
  .t-title  { font-size: 29px; font-weight: 700; letter-spacing: -0.4px; }
  .t-sub    { font-size: 12px; fill: __MUTED__; }
  .col      { font-size: 9.5px; letter-spacing: 1.6px; fill: __FAINT__; }
  .n-name   { font-size: 13px; fill: __TEXT__; }
  .n-sub    { font-size: 10.5px; fill: __MUTED__; }
  .pill     { font-size: 10.5px; fill: __TEAL__; letter-spacing: 0.3px; }
  .live     { font-size: 8.5px; fill: __TEAL__; letter-spacing: 1.2px; }
  .log      { font-size: 11.5px; }
  .wire     { fill: none; stroke: __FAINT__; stroke-width: 1.25; stroke-dasharray: 3 7; }
"""


def node(x, y, w, name, sub, bar_color, name_color=None, live=False):
    # a live service gets a brighter border and a pulsing beacon on its right edge
    border = "__TEAL__" if live else "__LINE__"
    beacon = ""
    if live:
        beacon = (f'\n    <circle cx="{x + w - 17}" cy="{y + 18}" r="4" fill="__TEAL__">'
                  '<animate attributeName="opacity" values="0.3;1;0.3" dur="1.8s" '
                  'repeatCount="indefinite"/></circle>'
                  f'\n    <text class="mono live" x="{x + w - 27}" y="{y + 21}" '
                  'text-anchor="end">LIVE</text>')
    return f"""  <g>
    <rect x="{x}" y="{y}" width="{w}" height="{BOX_H}" rx="9" fill="__PANEL__" stroke="{border}"/>
    <rect x="{x}" y="{y + 11}" width="3" height="{BOX_H - 22}" rx="1.5" fill="{bar_color}"/>
    <text class="mono n-name" x="{x + 17}" y="{y + 22}" fill="{name_color or '__TEXT__'}">{esc(name)}</text>
    <text class="mono n-sub" x="{x + 17}" y="{y + 38}">{esc(sub)}</text>{beacon}
  </g>"""


def build_topology(theme: str) -> str:
    c = THEMES[theme]
    parts = []

    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 {CANVAS_H}" '
        f'width="1200" height="{CANVAS_H}" role="img" '
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
    parts.append(f'  <rect width="1200" height="{CANVAS_H}" rx="14" fill="__BG__"/>')
    parts.append('  <rect x="0" y="88" width="1200" height="320" fill="url(#grid)" opacity="0.75"/>')
    parts.append(f'  <rect x="0.5" y="0.5" width="1199" height="{CANVAS_H - 1}" rx="14" '
                 'fill="none" stroke="__LINE__"/>')

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
        parts.append(f'  <text class="mono col" x="{COL[key][0]}" y="106">{label}</text>')

    # wires first so nodes sit on top
    for pid, d, kind in EDGES:
        parts.append(f'  <path id="{pid}" class="wire" d="{d}">'
                     '<animate attributeName="stroke-dashoffset" values="0;-10" dur="1.4s" '
                     'repeatCount="indefinite"/></path>')

    # nodes
    mid_top = CENTER_Y - BOX_H // 2
    ix, iw = COL["ingress"]
    parts.append(node(ix, mid_top, iw, "client", "browser · curl · sdk", "__FAINT__", "__MUTED__"))
    ex, ew = COL["edge"]
    parts.append(node(ex, mid_top, ew, "edge/gateway", "clerk jwt · rbac · rate limit", "__ACCENT__"))
    sx, sw = COL["svc"]
    for i, (name, sub, live) in enumerate(SERVICES):
        parts.append(node(sx, SVC_ROW_Y[i], sw, name, sub, "__ACCENT__", live=live))
    tx, tw = COL["state"]
    for i, (name, sub) in enumerate(STATE):
        parts.append(node(tx, STATE_ROW_Y[i], tw, name, sub, "__TEAL__"))

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
    parts.append('  <path d="M48,408 H1152" stroke="__LINE__" stroke-width="1"/>')
    for i, (svc, msg) in enumerate(LOG):
        y = 436 + i * 24
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

# (label, hint, offset_ms, dur_ms, colour_key, label_override)
# health-assistant p50s, straight from docs/BENCHMARKS.md. The last two bars carry
# cumulative "@" timestamps because those are what was measured -- the span widths
# between them are arithmetic, and labelling them as durations would overclaim.
PANEL_A = {
    "title": "POST /api/chat",
    "hint": "health-assistant · p50, measured · 50 docs / 168 chunks",
    "scale": 2700.0,
    "ticks": [0, 500, 1000, 1500, 2000, 2500],
    "unit": "ms",
    "y": 128,
    "rows": [
        ("embed.gemini", "768-d", 0, 714.7, "accent", None),
        ("retrieve.pgvector", "hnsw · top-5", 714.7, 46.2, "teal", None),
        ("llm.first_token", "groq → gemini", 760.9, 368.4, "accent", "@1129.3ms"),
        ("answer.complete", "4.8 citations", 1129.3, 1382.9, "accent", "@2512.2ms"),
        ("red_flag.short_circuit", "", 0, 0.1, "teal", "0.1ms"),
    ],
}
PANEL_B = {
    "title": "GET /{slug}",
    "hint": "url-shortener · redirect hot path",
    "scale": 45.0,
    "ticks": [0, 10, 20, 30, 40],
    "unit": "ms",
    "y": 374,
    "rows": [
        ("postgres lookup", "cold", 0, 40.0, "muted", None),
        ("redis cache-aside", "hit", 0, 6.7, "teal", None),
    ],
}

# (grow start seconds, grow duration seconds) per bar, over a 7s cycle
TIMING = [(0.30, 0.55), (0.85, 0.30), (1.15, 0.40), (1.55, 0.55), (2.35, 0.25),
          (2.90, 0.50), (3.20, 0.45)]
CYCLE = 7.0
TRACE_H = 480

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
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 {TRACE_H}" '
        f'width="1200" height="{TRACE_H}" role="img" '
        'aria-label="Request traces through two production paths">',
        "  <title>trace — measured production paths</title>",
    ]
    body = []

    body.append(f'  <rect width="1200" height="{TRACE_H}" rx="14" fill="__BG__"/>')
    body.append(f'  <rect x="0.5" y="0.5" width="1199" height="{TRACE_H - 1}" rx="14" '
                'fill="none" stroke="__LINE__"/>')
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

        for row_i, (name, hint, off, dur, ckey, label_override) in enumerate(panel["rows"]):
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
            lbl = label_override or f"{dur:g}{panel['unit']}"
            lcol = ""
            body.append(f'  <text class="mono dur" x="{x + w + 12:.1f}" y="{y + 15}"{lcol} opacity="0">'
                        f'{esc(lbl)}'
                        f'<animate attributeName="opacity" dur="{CYCLE}s" repeatCount="indefinite" '
                        f'values="0;0;1;1;0" '
                        f'keyTimes="0;{end / CYCLE:.4f};{(end + 0.15) / CYCLE:.4f};0.93;1"/></text>')
            bar_index += 1

        body.append(f'  <path d="M{BAR_X0},{axis_y} H{BAR_X1}" stroke="__LINE__" stroke-width="1"/>')

    # the two punchlines, each landing just after the bar it belongs to
    for bar_i, x, y, text in (
        (4, 365, 271, "← the safety path short-circuits before retrieval, before the model"),
        (6, 505, 421, "← 6× faster, and the cache is never the source of truth"),
    ):
        end = TIMING[bar_i][0] + TIMING[bar_i][1]
        body.append(f'  <text class="mono note" x="{x}" y="{y}" opacity="0">{esc(text)}'
                    f'<animate attributeName="opacity" dur="{CYCLE}s" repeatCount="indefinite" '
                    f'values="0;0;1;1;0" '
                    f'keyTimes="0;{end / CYCLE:.4f};{(end + 0.2) / CYCLE:.4f};0.93;1"/></text>')

    parts.append(f"  <style>{''.join(css)}\n  </style>")
    parts.extend(body)
    parts.append("</svg>")
    return paint("\n".join(parts), c)


# ------------------------------------------------------------ shared parts ---

def tw(text: str, size: float) -> float:
    """Monospace advance width. Close enough to lay out chips and clip masks."""
    return len(text) * size * 0.6


def open_svg(w: int, h: int, label: str, title: str) -> list:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="{esc(label)}">',
        f"  <title>{esc(title)}</title>",
    ]


def frame(w: int, h: int) -> list:
    return [
        f'  <rect width="{w}" height="{h}" rx="14" fill="__BG__"/>',
        f'  <rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" '
        'fill="none" stroke="__LINE__"/>',
    ]


def panel_head(title: str, tail: str, sub: str, w: int) -> list:
    """The `name.suffix` + subtitle + rule used by every panel."""
    return [
        f'  <text class="mono h-title" x="48" y="46" fill="__TEXT__">{esc(title)}'
        f'<tspan fill="__ACCENT__">{esc(tail)}</tspan></text>',
        f'  <text class="mono h-sub" x="48" y="68">{esc(sub)}</text>',
        f'  <path d="M48,86 H{w - 48}" stroke="__LINE__" stroke-width="1"/>',
    ]


HEAD_CSS = """
  .mono { font-family: __MONO__; }
  .h-title { font-size: 29px; font-weight: 700; letter-spacing: -0.4px; }
  .h-sub   { font-size: 12px; fill: __MUTED__; }
"""


def pulse(dur: float, lo=0.3, hi=1.0, begin=0.0) -> str:
    return (f'<animate attributeName="opacity" values="{lo};{hi};{lo}" dur="{dur}s" '
            f'begin="{begin}s" repeatCount="indefinite"/>')


# ------------------------------------------------------------- fleet board ---

FLEET_W, FLEET_H = 1200, 344
TILE_W, TILE_H, TILE_GAP = 268, 92, 16

# (name, kind, line1, line2)  kind: live | prod | lab
FLEET = [
    ("health-assistant", "live", "90% hit · 0% false hits", "p50 2512ms · 100% cited"),
    ("codity", "prod", "exactly-once · 10 workers", "58 endpoints · 48 CI tests"),
    ("readr", "prod", "pdf → grounded answer", "per-user + per-thread isolation"),
    ("url-shortener", "prod", "40ms → 6.7ms cached", "94% coverage · 22 tests"),
    ("support-copilot", "prod", "multi-tenant backend", "alembic migrations, versioned"),
    ("ai-gateway", "prod", "ordered provider chain", "dead provider ≠ dead request"),
    ("pg-tuning", "lab", "1M synthetic rows", "up to 20,000× via indexes"),
    ("cloudbeat", "lab", "spotify oauth + 3D", "60fps spline scene"),
]

KIND_STYLE = {
    "live": ("__TEAL__", "LIVE", 1.6),
    "prod": ("__ACCENT__", "SHIPPED", 3.4),
    "lab": ("__FAINT__", "LAB", 0.0),
}

FLEET_CSS = """
  .f-name  { font-size: 12.5px; fill: __TEXT__; }
  .f-l1    { font-size: 10.5px; fill: __MUTED__; }
  .f-l2    { font-size: 10px; fill: __FAINT__; }
  .f-tag   { font-size: 8.5px; letter-spacing: 1.2px; }
"""


def build_fleet(theme: str) -> str:
    c = THEMES[theme]
    p = open_svg(FLEET_W, FLEET_H, "Fleet status board for eight services",
                 "fleet — service status")
    p.append(f"  <style>{HEAD_CSS}{FLEET_CSS}</style>")
    p.append("""  <defs>
    <linearGradient id="sweep" x1="0" x2="1">
      <stop offset="0" stop-color="__TEAL__" stop-opacity="0"/>
      <stop offset="0.5" stop-color="__TEAL__" stop-opacity="0.07"/>
      <stop offset="1" stop-color="__TEAL__" stop-opacity="0"/>
    </linearGradient>
  </defs>""")
    p += frame(FLEET_W, FLEET_H)
    p += panel_head("fleet", ".status", "eight services · one of them is answering requests "
                                       "right now", FLEET_W)

    for i, (name, kind, l1, l2) in enumerate(FLEET):
        col, row = i % 4, i // 4
        x = 40 + col * (TILE_W + TILE_GAP)
        y = 104 + row * (TILE_H + TILE_GAP)
        colour, tag, rate = KIND_STYLE[kind]
        border = "__TEAL__" if kind == "live" else "__LINE__"
        lamp = f'<circle cx="{x + 20}" cy="{y + 25}" r="4.5" fill="{colour}">'
        lamp += (pulse(rate, 0.25, 1.0, begin=i * 0.25) if rate else "") + "</circle>"
        p.append(f"""  <g>
    <rect x="{x}" y="{y}" width="{TILE_W}" height="{TILE_H}" rx="10"
          fill="__PANEL__" stroke="{border}"/>
    {lamp}
    <text class="mono f-name" x="{x + 34}" y="{y + 29}">{esc(name)}</text>
    <text class="mono f-tag" x="{x + TILE_W - 14}" y="{y + 28}" text-anchor="end"
          fill="{colour}">{tag}</text>
    <text class="mono f-l1" x="{x + 20}" y="{y + 57}">{esc(l1)}</text>
    <text class="mono f-l2" x="{x + 20}" y="{y + 76}">{esc(l2)}</text>
  </g>""")

    # a scanline drifting across the board, the way a console polls its fleet
    p.append(f"""  <rect x="0" y="96" width="240" height="{FLEET_H - 120}" fill="url(#sweep)">
    <animate attributeName="x" values="-240;{FLEET_W}" dur="6s" repeatCount="indefinite"/>
  </rect>""")
    p.append("</svg>")
    return paint("\n".join(p), c)


# ---------------------------------------------------------- decision spine ---

DEC_W, DEC_H = 1200, 212
DEC_CYCLE = 5.0
DECISIONS = [
    ("ADR-001", "refuse, don't guess", "0% false hits"),
    ("ADR-002", "postgres is the queue", "one less system"),
    ("ADR-003", "cache-aside only", "6× faster reads"),
    ("ADR-004", "fail over, don't retry", "44% failover, held"),
    ("ADR-005", "read the plan first", "up to 20,000×"),
]

DEC_CSS = """
  .d-id    { font-size: 9.5px; letter-spacing: 1.4px; fill: __FAINT__; }
  .d-title { font-size: 12px; fill: __TEXT__; }
  .d-out   { font-size: 10px; fill: __TEAL__; }
  .spine   { stroke: __LINE__; stroke-width: 1.5; fill: none; }
"""


def build_decisions(theme: str) -> str:
    c = THEMES[theme]
    p = open_svg(DEC_W, DEC_H, "Five architecture decision records on a timeline",
                 "decisions — the calls and what they cost")
    p.append(f"  <style>{HEAD_CSS}{DEC_CSS}</style>")
    p += frame(DEC_W, DEC_H)
    p += panel_head("decisions", ".log", "five calls, and the bill each one came with", DEC_W)

    x0, x1, spine_y = 70, 1130, 132
    p.append(f'  <path id="spine" class="spine" d="M{x0},{spine_y} H{x1}"/>')

    xs = [130 + i * 235 for i in range(len(DECISIONS))]
    for i, ((adr, title, outcome), x) in enumerate(zip(DECISIONS, xs)):
        at = (x - x0) / (x1 - x0) * DEC_CYCLE      # when the pulse reaches this node
        p.append(f"""  <g>
    <text class="mono d-id" x="{x}" y="{spine_y - 26}" text-anchor="middle">{adr}</text>
    <circle cx="{x}" cy="{spine_y}" r="16" fill="none" stroke="__TEAL__" opacity="0">
      <animate attributeName="r" values="9;19" dur="0.7s" begin="{at:.2f}s"
               repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.7;0" dur="0.7s" begin="{at:.2f}s"
               repeatCount="indefinite"/>
    </circle>
    <circle cx="{x}" cy="{spine_y}" r="7" fill="__BG__" stroke="__ACCENT__" stroke-width="2"/>
    <text class="mono d-title" x="{x}" y="{spine_y + 34}" text-anchor="middle">{esc(title)}</text>
    <text class="mono d-out" x="{x}" y="{spine_y + 52}" text-anchor="middle">{esc(outcome)}</text>
  </g>""")

    # the pulse that walks the spine and sets each node off as it passes
    p.append(f"""  <circle r="4" fill="__TEAL__" filter="url(#dglow)">
    <animateMotion dur="{DEC_CYCLE}s" repeatCount="indefinite"><mpath href="#spine"/></animateMotion>
  </circle>""")
    p.insert(2, """  <defs><filter id="dglow" x="-300%" y="-300%" width="700%" height="700%">
    <feGaussianBlur stdDeviation="2.6" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter></defs>""")
    p.append("</svg>")
    return paint("\n".join(p), c)


# ----------------------------------------------------------------- runtime ---

STACK_W = 1200
BAND_H, BAND_GAP, BAND_X = 46, 8, 178

LAYERS = [
    ("CLIENT", ["react 18", "typescript", "vite", "next.js", "clerk"]),
    ("EDGE", ["fastapi", "jwt + rbac", "sliding-window limits", "cors"]),
    ("SERVICE", ["sqlalchemy", "alembic", "asyncio", "asyncpg", "pydantic"]),
    ("DATA", ["postgresql", "pgvector", "redis", "neon", "upstash", "supabase"]),
    ("MODEL", ["groq", "gemini", "langgraph", "langchain", "hnsw + cosine"]),
    ("SHIP", ["docker", "github actions", "render", "vercel", "gcp", "linux", "pytest"]),
]
STACK_CYCLE = 7.0
STACK_H = 92 + len(LAYERS) * (BAND_H + BAND_GAP) + 16

STACK_CSS = """
  .s-layer { font-size: 10px; letter-spacing: 1.6px; fill: __MUTED__; }
  .s-chip  { font-size: 11px; fill: __TEXT__; }
"""


def build_stack(theme: str) -> str:
    c = THEMES[theme]
    p = open_svg(STACK_W, STACK_H, "The runtime stack, layer by layer",
                 "runtime — what I actually reach for")
    p.append(f"  <style>{HEAD_CSS}{STACK_CSS}</style>")
    p += frame(STACK_W, STACK_H)
    p += panel_head("runtime", ".stack", "top to bottom, the layers I actually reach for",
                    STACK_W)

    for i, (label, chips) in enumerate(LAYERS):
        y = 100 + i * (BAND_H + BAND_GAP)
        at = i * (STACK_CYCLE / len(LAYERS))       # the cascade down the stack
        p.append(f'  <rect x="48" y="{y}" width="{STACK_W - 96}" height="{BAND_H}" rx="9" '
                 'fill="__PANEL2__" stroke="__LINE__"/>')
        p.append(f'  <rect x="48" y="{y}" width="3.5" height="{BAND_H}" rx="1.75" '
                 f'fill="__ACCENT__" opacity="0.25">{pulse(STACK_CYCLE, 0.25, 1, at)}</rect>')
        p.append(f'  <text class="mono s-layer" x="70" y="{y + BAND_H / 2 + 4:.0f}">{label}</text>')

        cx = BAND_X
        for chip in chips:
            w = tw(chip, 11) + 22
            p.append(f"""  <g>
    <rect x="{cx:.0f}" y="{y + 11}" width="{w:.0f}" height="24" rx="12"
          fill="__PANEL__" stroke="__LINE__" opacity="0.9"/>
    <text class="mono s-chip" x="{cx + w / 2:.0f}" y="{y + 27}" text-anchor="middle">{esc(chip)}</text>
  </g>""")
            cx += w + 8

    p.append("</svg>")
    return paint("\n".join(p), c)


# ---------------------------------------------------------------- terminal ---

TERM_W, TERM_H = 1200, 318
TERM_CYCLE = 9.0
CMD = "curl -s https://shardul.sys/health | jq"
# (indent, [(text, colour class)]) -- rendered as one line each
RESPONSE = [
    [("{", "t-punc")],
    [('  "status":  ', "t-key"), ('"up"', "t-str"), (",", "t-punc")],
    [('  "region":  ', "t-key"), ('"in-nanded-1"', "t-str"), (",", "t-punc")],
    [('  "live":    ', "t-key"), ('["health-assistant"]', "t-str"), (",", "t-punc")],
    [('  "open_to": ', "t-key"), ('"backend · infra · ai-systems work"', "t-str"), (",", "t-punc")],
    [('  "reach":   ', "t-key"), ('"portfolio · linkedin · leetcode · email"', "t-str")],
    [("}", "t-punc")],
]

TERM_CSS = """
  .t-bar   { font-size: 11px; fill: __MUTED__; }
  .t-cmd   { font-size: 13px; fill: __TEXT__; }
  .t-key   { font-size: 13px; fill: __ACCENT__; }
  .t-str   { font-size: 13px; fill: __TEAL__; }
  .t-punc  { font-size: 13px; fill: __MUTED__; }
"""


def build_health(theme: str) -> str:
    c = THEMES[theme]
    p = open_svg(TERM_W, TERM_H, "A terminal running a health check against shardul.sys",
                 "health — still up")
    p.append(f"  <style>{HEAD_CSS}{TERM_CSS}</style>")
    p += frame(TERM_W, TERM_H)

    # window chrome
    p.append('  <path d="M0,40 H1200" stroke="__LINE__" stroke-width="1"/>')
    for i, col in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        p.append(f'  <circle cx="{30 + i * 20}" cy="20" r="6" fill="{col}" opacity="0.85"/>')
    p.append('  <text class="mono t-bar" x="600" y="24" text-anchor="middle">'
             'shardul.sys — health check</text>')

    type_dur = 1.6
    x, y = 40, 82
    prompt_w = tw("$ ", 13)
    cmd_w = tw(CMD, 13)

    p.append(f'  <text class="mono t-str" x="{x}" y="{y}">$</text>')
    # typewriter: a clip rect widens across the command text
    p.append(f"""  <defs><clipPath id="typing">
    <rect x="{x + prompt_w}" y="{y - 14}" width="0" height="20">
      <animate attributeName="width" dur="{TERM_CYCLE}s" repeatCount="indefinite"
               values="0;0;{cmd_w:.0f};{cmd_w:.0f};0"
               keyTimes="0;0.02;{(0.02 + type_dur / TERM_CYCLE):.3f};0.95;1"/>
    </rect>
  </clipPath></defs>""")
    p.append(f'  <g clip-path="url(#typing)"><text class="mono t-cmd" x="{x + prompt_w:.0f}" '
             f'y="{y}">{esc(CMD)}</text></g>')
    # the caret rides the end of the typed text, then parks
    p.append(f"""  <rect y="{y - 12}" width="8" height="16" fill="__TEAL__" opacity="0.85">
    <animate attributeName="x" dur="{TERM_CYCLE}s" repeatCount="indefinite"
             values="{x + prompt_w:.0f};{x + prompt_w:.0f};{x + prompt_w + cmd_w:.0f};{x + prompt_w + cmd_w:.0f}"
             keyTimes="0;0.02;{(0.02 + type_dur / TERM_CYCLE):.3f};1"/>
    <animate attributeName="opacity" values="0.85;0.85;0;0" dur="{TERM_CYCLE}s"
             keyTimes="0;{(0.06 + type_dur / TERM_CYCLE):.3f};{(0.08 + type_dur / TERM_CYCLE):.3f};1"
             repeatCount="indefinite"/>
  </rect>""")

    # response lines land one after another, the way real output does
    first = 0.02 + (type_dur + 0.35) / TERM_CYCLE
    for i, segments in enumerate(RESPONSE):
        ly = 128 + i * 23
        at = first + i * 0.035
        spans = "".join(f'<tspan class="{cls}" xml:space="preserve">{esc(t)}</tspan>'
                        for t, cls in segments)
        p.append(f'  <text class="mono" x="{x}" y="{ly}" opacity="0">{spans}'
                 f'<animate attributeName="opacity" dur="{TERM_CYCLE}s" repeatCount="indefinite" '
                 f'values="0;0;1;1;0" keyTimes="0;{at:.3f};{at + 0.02:.3f};0.95;1"/></text>')

    # and a caret waiting for the next command
    done = first + len(RESPONSE) * 0.035 + 0.05
    p.append(f"""  <rect x="{x}" y="{128 + len(RESPONSE) * 23 - 12}" width="8" height="16"
        fill="__TEAL__" opacity="0">
    <animate attributeName="opacity" dur="{TERM_CYCLE}s" repeatCount="indefinite"
             values="0;0;0.9;0;0.9;0;0.9;0"
             keyTimes="0;{done:.3f};{done + 0.03:.3f};{done + 0.06:.3f};{done + 0.09:.3f};{done + 0.12:.3f};{done + 0.15:.3f};1"/>
  </rect>""")
    p.append("</svg>")
    return paint("\n".join(p), c)


BUILDERS = {
    "system": build_topology,
    "trace": build_trace,
    "fleet": build_fleet,
    "decisions": build_decisions,
    "stack": build_stack,
    "health": build_health,
}

if __name__ == "__main__":
    for theme in THEMES:
        for name, fn in BUILDERS.items():
            (OUT / f"{name}-{theme}.svg").write_text(fn(theme), encoding="utf-8")
        print(f"wrote {len(BUILDERS)} svgs for {theme}")
