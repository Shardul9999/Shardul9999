#!/usr/bin/env python3
"""
Generates the animated SVGs used by the profile README.

    python assets/build_svgs.py

Emits light + dark variants of six panels: system, trace, fleet, decisions,
stack, health.

Everything is self-contained: no external fonts, no scripts, no network calls,
so GitHub renders it straight from the repo.

On sizing -- GitHub renders a profile README into an ~831px column, so a wider
viewBox is scaled DOWN before anyone sees it and the type shrinks with it. W is
therefore set just above that column width: the panels render at roughly 1:1,
and a font size here is very nearly the size it lands at on screen. Nothing
below 10.5px, and body text sits at 12-14px. If you widen W, scale the type
with it or it becomes unreadable again.
"""

from pathlib import Path

OUT = Path(__file__).parent

W = 860          # canvas width for every panel; ~1:1 against GitHub's column
M = 32           # outer margin
INNER = W - 2 * M

THEMES = {
    "dark": {
        "bg": "#0b0f14",
        "panel": "#11161d",
        "panel2": "#0e131a",
        "grid": "#161c24",
        "line": "#2b333d",
        "text": "#e6edf3",
        "muted": "#8b949e",
        "faint": "#5a6675",
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
        "muted": "#54606d",
        "faint": "#8894a3",
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


def tw(text: str, size: float) -> float:
    """Monospace advance width -- good enough to lay out chips and clip masks."""
    return len(text) * size * 0.6


def open_svg(h: int, label: str, title: str) -> list:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" '
        f'width="{W}" height="{h}" role="img" aria-label="{esc(label)}">',
        f"  <title>{esc(title)}</title>",
    ]


def frame(h: int) -> list:
    return [
        f'  <rect width="{W}" height="{h}" rx="14" fill="__BG__"/>',
        f'  <rect x="0.5" y="0.5" width="{W - 1}" height="{h - 1}" rx="14" '
        'fill="none" stroke="__LINE__"/>',
    ]


def panel_head(title: str, tail: str, sub: str) -> list:
    return [
        f'  <text class="mono h-title" x="{M}" y="44" fill="__TEXT__">{esc(title)}'
        f'<tspan fill="__ACCENT__">{esc(tail)}</tspan></text>',
        f'  <text class="mono h-sub" x="{M}" y="66">{esc(sub)}</text>',
        f'  <path d="M{M},84 H{W - M}" stroke="__LINE__" stroke-width="1"/>',
    ]


HEAD_CSS = """
  .mono { font-family: __MONO__; }
  .h-title { font-size: 26px; font-weight: 700; letter-spacing: -0.3px; }
  .h-sub   { font-size: 13px; fill: __MUTED__; }
"""


def pulse(dur: float, lo=0.3, hi=1.0, begin=0.0) -> str:
    return (f'<animate attributeName="opacity" values="{lo};{hi};{lo}" dur="{dur}s" '
            f'begin="{begin}s" repeatCount="indefinite"/>')


GLOW = """  <defs><filter id="glow" x="-300%" y="-300%" width="700%" height="700%">
    <feGaussianBlur stdDeviation="2.4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter></defs>"""


# ---------------------------------------------------------------- topology ---

# three columns: the client column was dropped when the canvas narrowed -- the
# gateway is the ingress, and the packets still enter from the left.
EDGE_X, EDGE_W = M, 196
SVC_X, SVC_W = 282, 286
STATE_X, STATE_W = 622, 206

BOX_H = 62
SVC_Y = [108, 188, 268, 348]
STATE_Y = [148, 228, 308]
MID_Y = 259

SERVICES = [
    ("svc/url-shortener", "redirects + analytics · fastapi", False),
    ("svc/health-assistant", "grounded rag · vercel + render", True),
    ("svc/readr", "rag over pdfs · langgraph", False),
    ("svc/codity", "distributed job scheduler", False),
]
STATE = [
    ("redis", "cache-aside · limits"),
    ("postgres:16", "the queue itself · neon"),
    ("pgvector", "hnsw · cosine top-5"),
]

SVC_MID = [y + BOX_H // 2 for y in SVC_Y]        # 139, 219, 299, 379
STATE_MID = [y + BOX_H // 2 for y in STATE_Y]    # 179, 259, 339

EDGES = (
    [(f"p{i}", f"M{EDGE_X + EDGE_W},{MID_Y} C{EDGE_X + EDGE_W + 24},{MID_Y} "
      f"{SVC_X - 24},{m} {SVC_X},{m}", "req")
     for i, m in enumerate(SVC_MID)]
    + [("d0", f"M{SVC_X + SVC_W},{SVC_MID[0]} C{SVC_X + SVC_W + 28},{SVC_MID[0]} "
        f"{STATE_X - 22},{STATE_MID[0]} {STATE_X},{STATE_MID[0]}", "data"),
       ("d1", f"M{SVC_X + SVC_W},{SVC_MID[0]} C{SVC_X + SVC_W + 28},{SVC_MID[0]} "
        f"{STATE_X - 22},{STATE_MID[1]} {STATE_X},{STATE_MID[1]}", "data"),
       ("d2", f"M{SVC_X + SVC_W},{SVC_MID[1]} C{SVC_X + SVC_W + 28},{SVC_MID[1]} "
        f"{STATE_X - 22},{STATE_MID[2]} {STATE_X},{STATE_MID[2]}", "data"),
       ("d3", f"M{SVC_X + SVC_W},{SVC_MID[2]} C{SVC_X + SVC_W + 28},{SVC_MID[2]} "
        f"{STATE_X - 22},{STATE_MID[2]} {STATE_X},{STATE_MID[2]}", "data"),
       ("d4", f"M{SVC_X + SVC_W},{SVC_MID[3]} C{SVC_X + SVC_W + 28},{SVC_MID[3]} "
        f"{STATE_X - 22},{STATE_MID[1]} {STATE_X},{STATE_MID[1]}", "data")]
)

PACKETS = [("p0", 0.0, 1.4), ("p1", 0.25, 1.3), ("p2", 0.5, 1.4), ("p3", 0.75, 1.5),
           ("d0", 1.9, 1.2), ("d1", 2.1, 1.3), ("d2", 2.3, 1.3),
           ("d3", 2.5, 1.2), ("d4", 2.7, 1.4)]

LOG = [
    ("health-assistant", "red-flag short-circuit in 0.1ms — no retrieval, no model call"),
    ("health-assistant", "27/27 answers cited · 129/129 citations valid · 0% false hits"),
    ("codity", "claims batch — FOR UPDATE SKIP LOCKED · fencing token issued"),
]

TOPO_H = 534

TOPO_CSS = """
  .col    { font-size: 11px; letter-spacing: 1.6px; fill: __FAINT__; }
  .n-name { font-size: 14px; fill: __TEXT__; }
  .n-sub  { font-size: 12px; fill: __MUTED__; }
  .pill   { font-size: 11px; fill: __TEAL__; letter-spacing: 0.3px; }
  .live   { font-size: 10.5px; fill: __TEAL__; letter-spacing: 1.1px; }
  .log    { font-size: 12.5px; }
  .wire   { fill: none; stroke: __FAINT__; stroke-width: 1.4; stroke-dasharray: 3 7; }
"""


def node(x, y, w, name, sub, bar, name_fill=None, live=False):
    border = "__TEAL__" if live else "__LINE__"
    extra = ""
    if live:
        extra = (f'\n    <circle cx="{x + w - 18}" cy="{y + 21}" r="4.5" fill="__TEAL__">'
                 '<animate attributeName="opacity" values="0.3;1;0.3" dur="1.8s" '
                 'repeatCount="indefinite"/></circle>'
                 f'\n    <text class="mono live" x="{x + w - 29}" y="{y + 25}" '
                 'text-anchor="end">LIVE</text>')
    return f"""  <g>
    <rect x="{x}" y="{y}" width="{w}" height="{BOX_H}" rx="10" fill="__PANEL__" stroke="{border}"/>
    <rect x="{x}" y="{y + 14}" width="3.5" height="{BOX_H - 28}" rx="1.75" fill="{bar}"/>
    <text class="mono n-name" x="{x + 17}" y="{y + 26}" fill="{name_fill or '__TEXT__'}">{esc(name)}</text>
    <text class="mono n-sub" x="{x + 17}" y="{y + 47}">{esc(sub)}</text>{extra}
  </g>"""


def build_topology(theme):
    p = open_svg(TOPO_H, "shardul.sys service topology: gateway into four services "
                         "into redis, postgres and pgvector",
                 "shardul.sys — service topology")
    p.append(f"  <style>{HEAD_CSS}{TOPO_CSS}</style>")
    p.append(GLOW.replace("</defs>", """
    <pattern id="grid" width="26" height="26" patternUnits="userSpaceOnUse">
      <path d="M26 0H0V26" fill="none" stroke="__GRID__" stroke-width="1"/>
    </pattern></defs>"""))
    p += frame(TOPO_H)
    p.append(f'  <rect x="0" y="86" width="{W}" height="344" fill="url(#grid)" opacity="0.7"/>')

    p.append(f'  <text class="mono h-title" x="{M}" y="44" fill="__TEXT__">shardul'
             '<tspan fill="__ACCENT__">.sys</tspan></text>')
    p.append(f'  <text class="mono h-sub" x="{M}" y="66">'
             'backend &amp; ai systems engineer · in-nanded-1 · SGGS ’27</text>')
    p.append(f'  <g><rect x="{W - M - 190}" y="28" width="190" height="28" rx="14" '
             'fill="__PANEL2__" stroke="__LINE__"/>'
             f'<circle cx="{W - M - 170}" cy="42" r="4.5" fill="__TEAL__">'
             '<animate attributeName="opacity" values="0.35;1;0.35" dur="2.4s" '
             'repeatCount="indefinite"/></circle>'
             f'<text class="mono pill" x="{W - M - 156}" y="47">all systems shipping</text></g>')
    p.append(f'  <path d="M{M},84 H{W - M}" stroke="__LINE__" stroke-width="1"/>')

    for label, x in (("INGRESS", EDGE_X), ("SERVICES", SVC_X), ("STATE", STATE_X)):
        p.append(f'  <text class="mono col" x="{x}" y="100">{label}</text>')

    for pid, d, _ in EDGES:
        p.append(f'  <path id="{pid}" class="wire" d="{d}">'
                 '<animate attributeName="stroke-dashoffset" values="0;-10" dur="1.4s" '
                 'repeatCount="indefinite"/></path>')

    p.append(node(EDGE_X, MID_Y - BOX_H // 2, EDGE_W, "edge/gateway",
                  "clerk jwt · rbac", "__ACCENT__"))
    for i, (name, sub, live) in enumerate(SERVICES):
        p.append(node(SVC_X, SVC_Y[i], SVC_W, name, sub, "__ACCENT__", live=live))
    for i, (name, sub) in enumerate(STATE):
        p.append(node(STATE_X, STATE_Y[i], STATE_W, name, sub, "__TEAL__"))

    for pid, begin, dur in PACKETS:
        kind = next(k for q, _, k in EDGES if q == pid)
        fill = "__TEAL__" if kind == "data" else "__ACCENT__"
        p.append(f"""  <circle r="3.6" fill="{fill}" filter="url(#glow)">
    <animateMotion dur="{dur}s" begin="{begin}s" repeatCount="indefinite">
      <mpath href="#{pid}"/></animateMotion>
    <animate attributeName="opacity" dur="{dur}s" begin="{begin}s"
             values="0;1;1;0" keyTimes="0;0.12;0.85;1" repeatCount="indefinite"/>
  </circle>""")

    p.append(f'  <path d="M{M},436 H{W - M}" stroke="__LINE__" stroke-width="1"/>')
    for i, (svc, msg) in enumerate(LOG):
        on = 0.10 + i * 0.06
        p.append(f"""  <text class="mono log" x="{M}" y="{464 + i * 26}" opacity="0">
    <tspan fill="__TEAL__">[ok]</tspan>
    <tspan fill="__ACCENT__" dx="10">{esc(svc)}</tspan>
    <tspan fill="__MUTED__" dx="10">{esc(msg)}</tspan>
    <animate attributeName="opacity" dur="6s" repeatCount="indefinite"
             values="0;0;1;1;0" keyTimes="0;{on:.3f};{on + 0.03:.3f};0.92;1"/>
  </text>""")
    p.append("</svg>")
    return paint("\n".join(p), THEMES[theme])


# ------------------------------------------------------------------ traces ---

BAR_X0, BAR_X1 = 250, W - M
BAR_W = BAR_X1 - BAR_X0
ROW_PITCH, BAR_H = 34, 24
TRACE_H = 506
CYCLE = 7.0

PANEL_A = {
    "title": "POST /api/chat",
    "hint": "health-assistant · p50, measured · 50 docs / 168 chunks",
    "scale": 2700.0, "ticks": [0, 500, 1000, 1500, 2000, 2500], "unit": "ms", "y": 132,
    "rows": [
        ("embed.gemini", "768-d", 0, 714.7, "accent", None),
        ("retrieve.pgvector", "top-5", 714.7, 46.2, "teal", None),
        ("llm.first_token", "groq → gemini", 760.9, 368.4, "accent", "@1129.3ms"),
        ("answer.complete", "4.8 citations", 1129.3, 1382.9, "accent", "@2512.2ms"),
        ("red_flag.short_circuit", "", 0, 0.1, "teal", "0.1ms"),
    ],
}
PANEL_B = {
    "title": "GET /{slug}",
    "hint": "url-shortener · redirect hot path",
    "scale": 45.0, "ticks": [0, 10, 20, 30, 40], "unit": "ms", "y": 392,
    "rows": [
        ("postgres lookup", "cold", 0, 40.0, "muted", None),
        ("redis cache-aside", "hit", 0, 6.7, "teal", None),
    ],
}

TIMING = [(0.30, 0.55), (0.85, 0.30), (1.15, 0.40), (1.55, 0.55), (2.35, 0.25),
          (2.90, 0.50), (3.20, 0.45)]

TRACE_CSS = """
  .p-name { font-size: 14px; fill: __ACCENT__; }
  .p-hint { font-size: 11.5px; fill: __MUTED__; }
  .s-name { font-size: 13px; fill: __TEXT__; }
  .s-hint { font-size: 11px; fill: __FAINT__; }
  .tick   { font-size: 11px; fill: __FAINT__; }
  .dur    { font-size: 12.5px; fill: __TEXT__; }
  .note   { font-size: 12px; fill: __ACCENT__; }
"""


def cycle_anim(attr, hold, start, end, zero="0"):
    return (f'<animate attributeName="{attr}" dur="{CYCLE}s" repeatCount="indefinite" '
            'calcMode="spline" keySplines="0 0 1 1;.22 1 .36 1;0 0 1 1;.6 0 1 1" '
            f'values="{zero};{zero};{hold};{hold};{zero}" '
            f'keyTimes="0;{start / CYCLE:.4f};{end / CYCLE:.4f};0.93;1"/>')


def fade_in(at):
    return ('<animate attributeName="opacity" dur="%ss" repeatCount="indefinite" '
            'values="0;0;1;1;0" keyTimes="0;%.4f;%.4f;0.93;1"/>'
            % (CYCLE, at / CYCLE, (at + 0.15) / CYCLE))


def build_trace(theme):
    p = open_svg(TRACE_H, "Request traces: the health-assistant chat path and the "
                          "url-shortener redirect path", "trace — measured production paths")
    p.append(f"  <style>{HEAD_CSS}{TRACE_CSS}</style>")
    p += frame(TRACE_H)
    p += panel_head("trace", ".", "two paths I measured rather than guessed at")

    i = 0
    for panel in (PANEL_A, PANEL_B):
        py, scale = panel["y"], BAR_W / panel["scale"]
        p.append(f'  <text class="mono p-name" x="{M}" y="{py - 28}">{esc(panel["title"])}</text>')
        p.append(f'  <text class="mono p-hint" x="{M}" y="{py - 12}">{esc(panel["hint"])}</text>')

        axis_y = py + len(panel["rows"]) * ROW_PITCH + 8
        for t in panel["ticks"]:
            gx = BAR_X0 + t * scale
            p.append(f'  <path d="M{gx:.1f},{py - 24} V{axis_y}" stroke="__GRID__"/>')
            unit = panel["unit"] if t == panel["ticks"][-1] else ""
            p.append(f'  <text class="mono tick" x="{gx:.1f}" y="{axis_y + 18}" '
                     f'text-anchor="middle">{t}{unit}</text>')

        for r, (name, hint, off, dur, ckey, override) in enumerate(panel["rows"]):
            y = py + r * ROW_PITCH
            x = BAR_X0 + off * scale
            bw = max(dur * scale, 3)
            start, grow = TIMING[i]
            end = start + grow
            fill = {"teal": "__TEAL__", "accent": "__ACCENT__", "muted": "__MUTED__"}[ckey]
            alpha = 0.55 if ckey == "muted" else 0.92

            p.append(f'  <text class="mono s-name" x="{M}" y="{y + 17}">{esc(name)}</text>')
            if hint:
                p.append(f'  <text class="mono s-hint" x="{M + tw(name, 13) + 9:.0f}" '
                         f'y="{y + 17}">{esc(hint)}</text>')
            p.append(f'  <rect x="{BAR_X0}" y="{y}" width="{BAR_W}" height="{BAR_H}" rx="6" '
                     'fill="__PANEL__" opacity="0.55"/>')
            p.append(f'  <rect x="{x:.1f}" y="{y}" width="0" height="{BAR_H}" rx="6" '
                     f'fill="{fill}" opacity="{alpha}">'
                     f'{cycle_anim("width", f"{bw:.1f}", start, end)}</rect>')

            label = override or f"{dur:g}{panel['unit']}"
            # a bar that reaches the right edge carries its label inside instead
            if x + bw + 12 + tw(label, 12.5) > BAR_X1:
                lx, anchor, lfill = x + bw - 10, ' text-anchor="end"', ' fill="__BG__"'
            else:
                lx, anchor, lfill = x + bw + 12, "", ""
            p.append(f'  <text class="mono dur" x="{lx:.1f}" y="{y + 17}"{anchor}{lfill} '
                     f'opacity="0">{esc(label)}{fade_in(end)}</text>')
            i += 1

        p.append(f'  <path d="M{BAR_X0},{axis_y} H{BAR_X1}" stroke="__LINE__"/>')

    for bar_i, x, y, text in (
        (4, 320, 285, "← the safety path never reaches the model"),
        (6, 400, 443, "← 6× faster · the cache is never the source of truth"),
    ):
        at = TIMING[bar_i][0] + TIMING[bar_i][1]
        p.append(f'  <text class="mono note" x="{x}" y="{y}" opacity="0">{esc(text)}'
                 f'{fade_in(at)}</text>')
    p.append("</svg>")
    return paint("\n".join(p), THEMES[theme])


# ------------------------------------------------------------- fleet board ---

TILE_W, TILE_H, TILE_GAP = (INNER - 20) // 2, 100, 16
FLEET_H = 100 + 4 * (TILE_H + TILE_GAP) + 12

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
KIND = {"live": ("__TEAL__", "LIVE", 1.6),
        "prod": ("__ACCENT__", "SHIPPED", 3.4),
        "lab": ("__FAINT__", "LAB", 0.0)}

FLEET_CSS = """
  .f-name { font-size: 15px; fill: __TEXT__; }
  .f-l1   { font-size: 12.5px; fill: __MUTED__; }
  .f-l2   { font-size: 11.5px; fill: __FAINT__; }
  .f-tag  { font-size: 10.5px; letter-spacing: 1.1px; }
"""


def build_fleet(theme):
    p = open_svg(FLEET_H, "Fleet status board: eight service tiles with status lamps",
                 "fleet — service status")
    p.append(f"  <style>{HEAD_CSS}{FLEET_CSS}</style>")
    p.append("""  <defs><linearGradient id="sweep" x1="0" x2="1">
    <stop offset="0" stop-color="__TEAL__" stop-opacity="0"/>
    <stop offset="0.5" stop-color="__TEAL__" stop-opacity="0.08"/>
    <stop offset="1" stop-color="__TEAL__" stop-opacity="0"/>
  </linearGradient></defs>""")
    p += frame(FLEET_H)
    p += panel_head("fleet", ".status", "eight services · one of them is answering "
                                        "requests right now")

    for i, (name, kind, l1, l2) in enumerate(FLEET):
        x = M + (i % 2) * (TILE_W + 20)
        y = 100 + (i // 2) * (TILE_H + TILE_GAP)
        colour, tag, rate = KIND[kind]
        border = "__TEAL__" if kind == "live" else "__LINE__"
        lamp = f'<circle cx="{x + 22}" cy="{y + 28}" r="5" fill="{colour}">'
        lamp += (pulse(rate, 0.25, 1.0, begin=i * 0.25) if rate else "") + "</circle>"
        p.append(f"""  <g>
    <rect x="{x}" y="{y}" width="{TILE_W}" height="{TILE_H}" rx="11"
          fill="__PANEL__" stroke="{border}"/>
    {lamp}
    <text class="mono f-name" x="{x + 40}" y="{y + 33}">{esc(name)}</text>
    <text class="mono f-tag" x="{x + TILE_W - 16}" y="{y + 32}" text-anchor="end"
          fill="{colour}">{tag}</text>
    <text class="mono f-l1" x="{x + 22}" y="{y + 63}">{esc(l1)}</text>
    <text class="mono f-l2" x="{x + 22}" y="{y + 85}">{esc(l2)}</text>
  </g>""")

    p.append(f"""  <rect x="0" y="94" width="200" height="{FLEET_H - 106}" fill="url(#sweep)">
    <animate attributeName="x" values="-200;{W}" dur="6s" repeatCount="indefinite"/>
  </rect>""")
    p.append("</svg>")
    return paint("\n".join(p), THEMES[theme])


# ---------------------------------------------------------- decision spine ---

DEC_CYCLE = 5.0
DECISIONS = [
    ("ADR-001", "refuse rather than guess", "0% false hits"),
    ("ADR-002", "postgres is the queue", "one less system to run"),
    ("ADR-003", "cache-aside, never write-through", "6× faster reads"),
    ("ADR-004", "fail over, don't retry harder", "44% failover, held"),
    ("ADR-005", "read the plan before the query", "up to 20,000×"),
]
DEC_X, DEC_Y0, DEC_PITCH = 60, 118, 72
DEC_H = DEC_Y0 + (len(DECISIONS) - 1) * DEC_PITCH + 44

DEC_CSS = """
  .d-id    { font-size: 11px; letter-spacing: 1.4px; fill: __FAINT__; }
  .d-title { font-size: 14px; fill: __TEXT__; }
  .d-out   { font-size: 12px; fill: __TEAL__; }
"""


def build_decisions(theme):
    p = open_svg(DEC_H, "Decision log: five architecture decision records with the "
                        "outcome each one produced", "decisions — the calls and what they cost")
    p.append(f"  <style>{HEAD_CSS}{DEC_CSS}</style>")
    p.append(GLOW)
    p += frame(DEC_H)
    p += panel_head("decisions", ".log", "five calls, and the bill each one came with")

    y0, y1 = DEC_Y0 - 18, DEC_Y0 + (len(DECISIONS) - 1) * DEC_PITCH + 18
    p.append(f'  <path id="spine" d="M{DEC_X},{y0} V{y1}" stroke="__LINE__" '
             'stroke-width="1.5" fill="none"/>')

    for i, (adr, title, out) in enumerate(DECISIONS):
        y = DEC_Y0 + i * DEC_PITCH
        at = (y - y0) / (y1 - y0) * DEC_CYCLE
        p.append(f"""  <g>
    <circle cx="{DEC_X}" cy="{y}" r="16" fill="none" stroke="__TEAL__" opacity="0">
      <animate attributeName="r" values="9;22" dur="0.8s" begin="{at:.2f}s"
               repeatCount="indefinite"/>
      <animate attributeName="opacity" values="0.7;0" dur="0.8s" begin="{at:.2f}s"
               repeatCount="indefinite"/>
    </circle>
    <circle cx="{DEC_X}" cy="{y}" r="8" fill="__BG__" stroke="__ACCENT__" stroke-width="2.2"/>
    <text class="mono d-id" x="{DEC_X + 32}" y="{y + 5}">{adr}</text>
    <text class="mono d-title" x="{DEC_X + 122}" y="{y + 5}">{esc(title)}</text>
    <text class="mono d-out" x="{W - M}" y="{y + 5}" text-anchor="end">{esc(out)}</text>
  </g>""")

    p.append(f"""  <circle r="4.5" fill="__TEAL__" filter="url(#glow)">
    <animateMotion dur="{DEC_CYCLE}s" repeatCount="indefinite">
      <mpath href="#spine"/></animateMotion>
  </circle>""")
    p.append("</svg>")
    return paint("\n".join(p), THEMES[theme])


# ------------------------------------------------------------ runtime stack ---

LAYERS = [
    ("CLIENT", ["react 18", "typescript", "vite", "next.js", "clerk"]),
    ("EDGE", ["fastapi", "jwt + rbac", "sliding-window limits", "cors"]),
    ("SERVICE", ["sqlalchemy", "alembic", "asyncio", "asyncpg", "pydantic"]),
    ("DATA", ["postgresql", "pgvector", "redis", "neon", "upstash", "supabase"]),
    ("MODEL", ["groq", "gemini", "langgraph", "langchain", "hnsw + cosine"]),
    ("SHIP", ["docker", "github actions", "render", "vercel", "gcp", "pytest"]),
]
BAND_H, BAND_GAP, CHIP_X = 52, 10, 152
STACK_CYCLE = 7.0
STACK_H = 100 + len(LAYERS) * (BAND_H + BAND_GAP) + 14

STACK_CSS = """
  .s-layer { font-size: 11.5px; letter-spacing: 1.5px; fill: __MUTED__; }
  .s-chip  { font-size: 12.5px; fill: __TEXT__; }
"""


def build_stack(theme):
    p = open_svg(STACK_H, "The runtime stack in six layers, each a row of named tools",
                 "runtime — what I actually reach for")
    p.append(f"  <style>{HEAD_CSS}{STACK_CSS}</style>")
    p += frame(STACK_H)
    p += panel_head("runtime", ".stack", "top to bottom, the layers I actually reach for")

    for i, (label, chips) in enumerate(LAYERS):
        y = 100 + i * (BAND_H + BAND_GAP)
        at = i * (STACK_CYCLE / len(LAYERS))
        p.append(f'  <rect x="{M}" y="{y}" width="{INNER}" height="{BAND_H}" rx="10" '
                 'fill="__PANEL2__" stroke="__LINE__"/>')
        p.append(f'  <rect x="{M}" y="{y}" width="4" height="{BAND_H}" rx="2" '
                 f'fill="__ACCENT__" opacity="0.25">{pulse(STACK_CYCLE, 0.25, 1, at)}</rect>')
        p.append(f'  <text class="mono s-layer" x="{M + 20}" y="{y + 31}">{label}</text>')
        cx = CHIP_X
        for chip in chips:
            cw = tw(chip, 12.5) + 24
            p.append(f"""  <g>
    <rect x="{cx:.0f}" y="{y + 12}" width="{cw:.0f}" height="28" rx="14"
          fill="__PANEL__" stroke="__LINE__"/>
    <text class="mono s-chip" x="{cx + cw / 2:.0f}" y="{y + 31}" text-anchor="middle">{esc(chip)}</text>
  </g>""")
            cx += cw + 8
    p.append("</svg>")
    return paint("\n".join(p), THEMES[theme])


# ---------------------------------------------------------- health terminal ---

TERM_CYCLE = 9.0
CMD = "curl -s https://shardul.sys/health | jq"
RESPONSE = [
    [("{", "t-punc")],
    [('  "status":  ', "t-key"), ('"up"', "t-str"), (",", "t-punc")],
    [('  "region":  ', "t-key"), ('"in-nanded-1"', "t-str"), (",", "t-punc")],
    [('  "live":    ', "t-key"), ('["health-assistant"]', "t-str"), (",", "t-punc")],
    [('  "open_to": ', "t-key"), ('"backend · infra · ai-systems work"', "t-str"), (",", "t-punc")],
    [('  "reach":   ', "t-key"), ('"portfolio · linkedin · leetcode · email"', "t-str")],
    [("}", "t-punc")],
]
LINE_PITCH = 26
TERM_H = 134 + len(RESPONSE) * LINE_PITCH + 44

TERM_CSS = """
  .t-bar  { font-size: 12px; fill: __MUTED__; }
  .t-cmd  { font-size: 14px; fill: __TEXT__; }
  .t-key  { font-size: 14px; fill: __ACCENT__; }
  .t-str  { font-size: 14px; fill: __TEAL__; }
  .t-punc { font-size: 14px; fill: __MUTED__; }
"""


def build_health(theme):
    p = open_svg(TERM_H, "A terminal running a health check against shardul.sys",
                 "health — still up")
    p.append(f"  <style>{HEAD_CSS}{TERM_CSS}</style>")
    p += frame(TERM_H)
    p.append(f'  <path d="M0,38 H{W}" stroke="__LINE__"/>')
    for i, col in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        p.append(f'  <circle cx="{28 + i * 20}" cy="19" r="6" fill="{col}" opacity="0.85"/>')
    p.append(f'  <text class="mono t-bar" x="{W // 2}" y="24" text-anchor="middle">'
             'shardul.sys — health check</text>')

    y, type_dur = 86, 1.6
    px, cw = tw("$ ", 14), tw(CMD, 14)
    typed = 0.02 + type_dur / TERM_CYCLE

    p.append(f'  <text class="mono t-str" x="{M}" y="{y}">$</text>')
    p.append(f"""  <defs><clipPath id="typing">
    <rect x="{M + px:.0f}" y="{y - 15}" width="0" height="22">
      <animate attributeName="width" dur="{TERM_CYCLE}s" repeatCount="indefinite"
               values="0;0;{cw:.0f};{cw:.0f};0" keyTimes="0;0.02;{typed:.3f};0.95;1"/>
    </rect></clipPath></defs>""")
    p.append(f'  <g clip-path="url(#typing)"><text class="mono t-cmd" x="{M + px:.0f}" '
             f'y="{y}">{esc(CMD)}</text></g>')
    p.append(f"""  <rect y="{y - 13}" width="9" height="18" fill="__TEAL__" opacity="0.85">
    <animate attributeName="x" dur="{TERM_CYCLE}s" repeatCount="indefinite"
             values="{M + px:.0f};{M + px:.0f};{M + px + cw:.0f};{M + px + cw:.0f}"
             keyTimes="0;0.02;{typed:.3f};1"/>
    <animate attributeName="opacity" values="0.85;0.85;0;0" dur="{TERM_CYCLE}s"
             keyTimes="0;{typed + 0.04:.3f};{typed + 0.06:.3f};1" repeatCount="indefinite"/>
  </rect>""")

    first = 0.02 + (type_dur + 0.35) / TERM_CYCLE
    for i, segs in enumerate(RESPONSE):
        at = first + i * 0.035
        spans = "".join(f'<tspan class="{cls}" xml:space="preserve">{esc(t)}</tspan>'
                        for t, cls in segs)
        p.append(f'  <text class="mono" x="{M}" y="{134 + i * LINE_PITCH}" opacity="0">{spans}'
                 f'<animate attributeName="opacity" dur="{TERM_CYCLE}s" repeatCount="indefinite" '
                 f'values="0;0;1;1;0" keyTimes="0;{at:.3f};{at + 0.02:.3f};0.95;1"/></text>')

    done = first + len(RESPONSE) * 0.035 + 0.05
    blink = ";".join(f"{done + n * 0.03:.3f}" for n in range(7))
    p.append(f"""  <rect x="{M}" y="{134 + len(RESPONSE) * LINE_PITCH - 14}" width="9" height="18"
        fill="__TEAL__" opacity="0">
    <animate attributeName="opacity" dur="{TERM_CYCLE}s" repeatCount="indefinite"
             values="0;0;0.9;0;0.9;0;0.9;0" keyTimes="0;{blink};1"/>
  </rect>""")
    p.append("</svg>")
    return paint("\n".join(p), THEMES[theme])


BUILDERS = {"system": build_topology, "trace": build_trace, "fleet": build_fleet,
            "decisions": build_decisions, "stack": build_stack, "health": build_health}

if __name__ == "__main__":
    for theme in THEMES:
        for name, fn in BUILDERS.items():
            (OUT / f"{name}-{theme}.svg").write_text(fn(theme), encoding="utf-8")
        print(f"wrote {len(BUILDERS)} svgs for {theme}")
