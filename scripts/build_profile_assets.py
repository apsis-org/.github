#!/usr/bin/env python3
"""Generate the SVG assets used by profile/README.md.

GitHub strips CSS from README files, so every visual element of the
organization profile is drawn as a self-contained SVG with its own dark
background. That keeps the look identical in GitHub's light and dark themes.

The palette and typography follow apsis-dx.com (app/globals.css,
components/layout/siteStyles.ts, public/apsis-logo.svg).

Usage:
    python3 scripts/build_profile_assets.py
"""

from __future__ import annotations

import random
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "profile" / "assets"

# --- Brand tokens (apsis-dx.com) -------------------------------------------
BG_TOP = "#141327"
BG_BOTTOM = "#09090b"
NEBULA_INDIGO = "#312e81"
NEBULA_PURPLE = "#581c87"
STAR = "#f5f0dd"
ORBIT_FROM = "#7c72ed"
ORBIT_MID = "#6759db"
ORBIT_TO = "#5548c8"
FG = "#f4f4f5"
TEXT = "#e4e4e7"
LEAD = "#b0aabb"
MUTED = "#71717a"
DIM = "#52525b"
ACCENT = "#8b85d9"

SANS = "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"

# Symbol and wordmark paths from public/apsis-logo.svg (viewBox 0 0 1080 256).
LOGO_INNER = f"""
  <defs>
    <linearGradient id="lg-orbit" x1="374" y1="271" x2="533" y2="594" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{ORBIT_FROM}"/><stop offset="0.5" stop-color="{ORBIT_MID}"/><stop offset="1" stop-color="{ORBIT_TO}"/>
    </linearGradient>
    <linearGradient id="lg-dot" x1="405" y1="473" x2="458" y2="526" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#756ae8"/><stop offset="1" stop-color="#5a4fd1"/>
    </linearGradient>
  </defs>
  <g transform="translate(-68 -173.92) scale(.68)">
    <path fill="url(#lg-orbit)" d="M351 288C421 254 510 275 563 340C632 422 600 545 405 619C512 564 565 499 564 429C563 338 468 266 351 288Z"/>
    <path fill="{FG}" d="M370 328C268 351 200 408 200 477c0 74 71 125 181 125-95-12-149-57-149-124 0-62 50-116 138-150Z"/>
    <path fill="{FG}" d="m309 527 123-169 123 169-123-127-123 127Z"/>
    <circle cx="432" cy="500" r="30" fill="url(#lg-dot)"/>
    <g fill="none" stroke="{FG}" stroke-width="18" stroke-linecap="square" stroke-linejoin="round">
      <path d="m704 516 75-119 75 119"/>
      <path d="M948 516V397h79c50 0 50 66 0 66h-79"/>
      <path d="M1260 397h-83c-42 0-42 59 0 59h60c43 0 43 60 0 60h-91"/>
      <path d="M1362 397v119"/>
      <path d="M1580 397h-83c-42 0-42 59 0 59h60c43 0 43 60 0 60h-91"/>
    </g>
  </g>"""


def t(s: str) -> str:
    return escape(s, quote=False)


def style() -> str:
    return f"""<style>
    .sans {{ font-family: {SANS}; }}
    .mono {{ font-family: {MONO}; letter-spacing: .16em; }}
    .code {{ font-family: {MONO}; letter-spacing: 0; }}
    .tw {{ animation: tw 4.8s ease-in-out infinite; }}
    @keyframes tw {{ 0%, 100% {{ opacity: .2; }} 50% {{ opacity: 1; }} }}
    .pulse {{ animation: pulse 3.2s ease-in-out infinite; }}
    @keyframes pulse {{ 0%, 100% {{ opacity: .45; }} 50% {{ opacity: 1; }} }}
  </style>"""


def frame_defs(w: int, h: int, rx: int, uid: str) -> str:
    """Background, rim light and clip shared by every panel."""
    return f"""
    <linearGradient id="{uid}-bg" x1="0" y1="0" x2="{w}" y2="{h}" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{BG_TOP}"/><stop offset="1" stop-color="{BG_BOTTOM}"/>
    </linearGradient>
    <linearGradient id="{uid}-rim" x1="0" y1="0" x2="{w}" y2="{h}" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#fff" stop-opacity=".38"/>
      <stop offset=".25" stop-color="#fff" stop-opacity=".05"/>
      <stop offset=".75" stop-color="#fff" stop-opacity=".04"/>
      <stop offset="1" stop-color="#fff" stop-opacity=".26"/>
    </linearGradient>
    <linearGradient id="{uid}-orbit" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{ORBIT_FROM}"/><stop offset="1" stop-color="{ORBIT_TO}"/>
    </linearGradient>
    <radialGradient id="{uid}-glow">
      <stop offset="0" stop-color="{ORBIT_FROM}" stop-opacity=".75"/>
      <stop offset=".35" stop-color="{ORBIT_FROM}" stop-opacity=".18"/>
      <stop offset="1" stop-color="{ORBIT_FROM}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="{uid}-neb-i">
      <stop offset="0" stop-color="{NEBULA_INDIGO}" stop-opacity=".7"/>
      <stop offset="1" stop-color="{NEBULA_INDIGO}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="{uid}-neb-p">
      <stop offset="0" stop-color="{NEBULA_PURPLE}" stop-opacity=".55"/>
      <stop offset="1" stop-color="{NEBULA_PURPLE}" stop-opacity="0"/>
    </radialGradient>
    <clipPath id="{uid}-clip"><rect width="{w}" height="{h}" rx="{rx}"/></clipPath>"""


def stars(rng: random.Random, w: int, h: int, n: int, avoid=None) -> str:
    out = []
    for _ in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        if avoid and avoid(x, y):
            continue
        r = rng.choice([0.6, 0.8, 0.8, 1.0, 1.2, 1.6])
        op = rng.uniform(0.25, 0.85)
        if rng.random() < 0.3:
            delay = rng.uniform(0, 4.8)
            out.append(
                f'<circle class="tw" style="animation-delay:-{delay:.1f}s" cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{STAR}"/>'
            )
        else:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{STAR}" opacity="{op:.2f}"/>')
    return "\n    ".join(out)


def panel(w: int, h: int, uid: str, body: str, *, rx: int = 18, title: str, seed: int = 1,
          star_count: int = 0, nebulae: str = "", avoid=None) -> str:
    rng = random.Random(seed)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(title)}">
  <title>{t(title)}</title>
  {style()}
  <defs>{frame_defs(w, h, rx, uid)}
  </defs>
  <g clip-path="url(#{uid}-clip)">
    <rect width="{w}" height="{h}" fill="url(#{uid}-bg)"/>
    {nebulae}
    {stars(rng, w, h, star_count, avoid)}
    {body}
  </g>
  <rect x=".75" y=".75" width="{w - 1.5}" height="{h - 1.5}" rx="{rx}" fill="none" stroke="url(#{uid}-rim)" stroke-width="1.5"/>
</svg>
"""


def write(name: str, svg: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(svg, encoding="utf-8")
    print(f"wrote profile/assets/{name}")


# --- Banner -----------------------------------------------------------------
def banner() -> str:
    w, h = 1280, 420
    cx, cy = 985, 205
    uid = "bn"
    nebulae = f"""
    <ellipse cx="{cx}" cy="{cy - 20}" rx="460" ry="300" fill="url(#{uid}-neb-i)"/>
    <ellipse cx="760" cy="430" rx="420" ry="200" fill="url(#{uid}-neb-p)"/>
    <ellipse cx="80" cy="-40" rx="420" ry="220" fill="url(#{uid}-neb-i)" opacity=".6"/>"""
    orbit_outer = f"M{cx - 330},{cy} a330,124 0 1,0 660,0 a330,124 0 1,0 -660,0"
    orbit_main = f"M{cx - 250},{cy} a250,92 0 1,0 500,0 a250,92 0 1,0 -500,0"
    orbit_inner = f"M{cx - 160},{cy} a160,58 0 1,1 320,0 a160,58 0 1,1 -320,0"
    body = f"""
    <!-- Orbit system: the central point is Telos -->
    <g transform="rotate(-16 {cx} {cy})">
      <path d="{orbit_outer}" fill="none" stroke="{FG}" stroke-opacity=".10" stroke-width="1"/>
      <path d="{orbit_main}" fill="none" stroke="url(#{uid}-orbit)" stroke-opacity=".85" stroke-width="1.6"/>
      <circle r="4.5" fill="{STAR}">
        <animateMotion dur="38s" repeatCount="indefinite" path="{orbit_main}"/>
      </circle>
      <circle r="2.5" fill="{ACCENT}">
        <animateMotion dur="64s" repeatCount="indefinite" begin="-20s" path="{orbit_outer}"/>
      </circle>
    </g>
    <g transform="rotate(14 {cx} {cy})">
      <path d="{orbit_inner}" fill="none" stroke="{FG}" stroke-opacity=".22" stroke-width="1" stroke-dasharray="2 7"/>
      <circle r="3" fill="{ORBIT_FROM}">
        <animateMotion dur="24s" repeatCount="indefinite" path="{orbit_inner}"/>
      </circle>
    </g>
    <circle cx="{cx}" cy="{cy}" r="90" fill="url(#{uid}-glow)" class="pulse"/>
    <circle cx="{cx}" cy="{cy}" r="9" fill="{ORBIT_FROM}"/>
    <circle cx="{cx}" cy="{cy}" r="3.5" fill="{STAR}"/>
    <text x="{cx + 22}" y="{cy + 34}" class="mono" font-size="11" fill="{ACCENT}" opacity=".9">TELOS</text>

    <!-- Copy -->
    <circle cx="90" cy="92" r="3.5" fill="{ORBIT_FROM}" class="pulse"/>
    <text x="104" y="97" class="mono" font-size="13" fill="{ACCENT}">AI &amp; DX MEDIA · APSIS-DX.COM</text>
    <svg x="58" y="118" width="420" height="100" viewBox="0 0 1080 256">{LOGO_INNER}
    </svg>
    <defs>
      <linearGradient id="{uid}-head" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#a1a1aa"/>
      </linearGradient>
    </defs>
    <text x="82" y="300" class="sans" font-size="56" font-weight="500" letter-spacing="-1.1" fill="url(#{uid}-head)">Reach your Telos.</text>
    <text x="84" y="342" class="sans" font-size="18" fill="{LEAD}">Exploring the intersection of AI, DX, and business logic.</text>
    <line x1="84" y1="372" x2="1196" y2="372" stroke="{FG}" stroke-opacity=".08"/>
    <text x="84" y="398" class="mono" font-size="11" fill="{DIM}">BLOG / SIGNALS / WORKS / OPERATORS</text>
    <text x="1196" y="398" text-anchor="end" class="mono" font-size="11" fill="{DIM}">NAVIGATE TO YOUR TELOS →</text>"""
    title = "Apsis DX — Reach your Telos. Exploring the intersection of AI, DX, and business logic."
    return panel(w, h, uid, body, rx=22, title=title, seed=7, star_count=170, nebulae=nebulae,
                 avoid=lambda x, y: (60 < x < 640 and 70 < y < 410) or (y > 380))


# --- Section header ---------------------------------------------------------
def section(index: str, label: str, seed: int) -> str:
    w, h = 1280, 84
    uid = f"s{index}"
    label_x = 128
    line_x = label_x + int(len(label) * 21 * 0.76) + 36
    body = f"""
    <ellipse cx="1150" cy="42" rx="320" ry="90" fill="url(#{uid}-neb-i)" opacity=".8"/>
    <text x="44" y="50" class="mono" font-size="19" fill="{ORBIT_FROM}">{index}</text>
    <line x1="84" y1="43" x2="108" y2="43" stroke="{ACCENT}" stroke-opacity=".6"/>
    <text x="{label_x}" y="50" class="mono" font-size="21" fill="{TEXT}" >{t(label.upper())}</text>
    <defs>
      <linearGradient id="{uid}-line" x1="{line_x}" y1="0" x2="1200" y2="0" gradientUnits="userSpaceOnUse">
        <stop offset="0" stop-color="{ORBIT_FROM}" stop-opacity=".7"/><stop offset="1" stop-color="{ORBIT_FROM}" stop-opacity=".05"/>
      </linearGradient>
    </defs>
    <line x1="{line_x}" y1="43" x2="1200" y2="43" stroke="url(#{uid}-line)" stroke-width="1.2"/>
    <circle cx="1220" cy="43" r="16" fill="url(#{uid}-glow)" class="pulse"/>
    <circle cx="1220" cy="43" r="3.5" fill="{STAR}"/>"""
    return panel(w, h, uid, body, rx=16, title=f"{index} — {label}", seed=seed, star_count=34,
                 avoid=lambda x, y: x < line_x + 10 or (1190 < x < 1250))


# --- Cards ------------------------------------------------------------------
def card(uid: str, eyebrow: str, title: str, lines: list[str], footer: str | None,
         seed: int, nebula: str = "i", title_mono: bool = False) -> str:
    w, h = 480, 290
    neb_pos = {"i": (470, 10), "p": (440, 300)}[nebula]
    title_cls = 'class="code"' if title_mono else 'class="sans"'
    title_size = 26 if title_mono else 31
    body_lines = "\n    ".join(
        f'<text x="36" y="{150 + i * 30}" class="sans" font-size="19" fill="{LEAD}">{t(line)}</text>'
        for i, line in enumerate(lines)
    )
    foot = (
        f'<line x1="36" y1="238" x2="444" y2="238" stroke="{FG}" stroke-opacity=".08"/>'
        f'<text x="36" y="266" class="mono" font-size="13" fill="{MUTED}">{t(footer.upper())}</text>'
        if footer else ""
    )
    body = f"""
    <ellipse cx="{neb_pos[0]}" cy="{neb_pos[1]}" rx="300" ry="190" fill="url(#{uid}-neb-{nebula})"/>
    <g transform="rotate(-18 418 58)">
      <ellipse cx="418" cy="58" rx="34" ry="13" fill="none" stroke="url(#{uid}-orbit)" stroke-width="1.4"/>
    </g>
    <circle cx="418" cy="58" r="14" fill="url(#{uid}-glow)"/>
    <circle cx="418" cy="58" r="3.5" fill="{STAR}"/>
    <text x="36" y="62" class="mono" font-size="14" fill="{ACCENT}">{t(eyebrow.upper())}</text>
    <text x="36" y="110" {title_cls} font-size="{title_size}" font-weight="500" fill="{FG}">{t(title)}</text>
    {body_lines}
    {foot}"""
    alt = f"{title} — {' '.join(lines)}"
    return panel(w, h, uid, body, rx=18, title=alt, seed=seed, star_count=40,
                 avoid=lambda x, y: (20 < x < 460 and 36 < y < 284) or (380 < x < 460 and y < 90))


def operator(uid: str, name: str, role: str, handle: str, seed: int) -> str:
    w, h = 640, 200
    initial = name[0]
    body = f"""
    <ellipse cx="120" cy="100" rx="260" ry="170" fill="url(#{uid}-neb-i)"/>
    <g transform="rotate(-18 112 100)">
      <ellipse cx="112" cy="100" rx="72" ry="26" fill="none" stroke="url(#{uid}-orbit)" stroke-width="1.4"/>
      <circle r="3" fill="{STAR}">
        <animateMotion dur="14s" repeatCount="indefinite" path="M40,100 a72,26 0 1,0 144,0 a72,26 0 1,0 -144,0"/>
      </circle>
    </g>
    <circle cx="112" cy="100" r="40" fill="{BG_TOP}" stroke="{FG}" stroke-opacity=".18"/>
    <text x="112" y="114" text-anchor="middle" class="sans" font-size="38" font-weight="500" fill="{FG}">{initial}</text>
    <text x="222" y="70" class="mono" font-size="14" fill="{ACCENT}">CO-FOUNDER</text>
    <text x="222" y="114" class="sans" font-size="38" font-weight="500" fill="{FG}">{t(name)}</text>
    <text x="222" y="146" class="sans" font-size="19" fill="{LEAD}">{t(role)}</text>
    <text x="604" y="176" text-anchor="end" class="code" font-size="13" fill="{MUTED}">@{t(handle)} →</text>"""
    return panel(w, h, uid, body, rx=18, title=f"{name} — Co-Founder / {role}", seed=seed, star_count=34,
                 avoid=lambda x, y: (20 < x < 630 and 40 < y < 190))


# --- Tech stack -------------------------------------------------------------
STACK = [
    ("Language", ["TypeScript"]),
    ("Frontend", ["Next.js", "Astro"]),
    ("Platform", ["Cloudflare Workers", "Azure Functions", "Google Apps Script", "Slack Platform"]),
    ("Infra", ["Terraform"]),
    ("AI", ["Claude Code", "AI agents in every workflow"]),
]


def tech_stack() -> str:
    w = 1280
    row_h = 62
    top = 44
    h = top + row_h * len(STACK) + 22
    uid = "ts"
    rows = []
    for i, (label, items) in enumerate(STACK):
        y = top + i * row_h
        rows.append(
            f'<text x="56" y="{y + 26}" class="mono" font-size="15" fill="{ACCENT}">{t(label.upper())}</text>'
        )
        x = 260
        for item in items:
            cw = int(len(item) * 10.4) + 44
            rows.append(
                f'<rect x="{x}" y="{y}" width="{cw}" height="40" rx="20" fill="{NEBULA_INDIGO}" fill-opacity=".28" '
                f'stroke="{ORBIT_FROM}" stroke-opacity=".38"/>'
                f'<circle cx="{x + 20}" cy="{y + 20}" r="3" fill="{ORBIT_FROM}"/>'
                f'<text x="{x + 32}" y="{y + 26}" class="sans" font-size="18" fill="{TEXT}">{t(item)}</text>'
            )
            x += cw + 14
        if i < len(STACK) - 1:
            rows.append(
                f'<line x1="56" y1="{y + row_h - 11}" x2="1224" y2="{y + row_h - 11}" stroke="{FG}" stroke-opacity=".05"/>'
            )
    body = f"""
    <ellipse cx="1180" cy="40" rx="420" ry="220" fill="url(#{uid}-neb-i)"/>
    <ellipse cx="900" cy="{h + 40}" rx="380" ry="160" fill="url(#{uid}-neb-p)"/>
    {"".join(rows)}"""
    alt = "Tech stack — " + "; ".join(f"{k}: {', '.join(v)}" for k, v in STACK)
    row_end = top + row_h * len(STACK)
    return panel(w, h, uid, body, rx=18, title=alt, seed=31, star_count=120,
                 avoid=lambda x, y: (40 < x < 1180 and 30 < y < row_end))


# --- Footer -----------------------------------------------------------------
def footer() -> str:
    w, h = 1280, 150
    uid = "ft"
    arc = "M-40,190 Q640,-10 1320,190"
    body = f"""
    <ellipse cx="640" cy="170" rx="560" ry="140" fill="url(#{uid}-neb-i)"/>
    <path d="{arc}" fill="none" stroke="url(#{uid}-orbit)" stroke-opacity=".7" stroke-width="1.4"/>
    <circle r="3.5" fill="{STAR}">
      <animateMotion dur="30s" repeatCount="indefinite" path="{arc}"/>
    </circle>
    <circle cx="640" cy="90" r="34" fill="url(#{uid}-glow)" class="pulse"/>
    <circle cx="640" cy="90" r="4" fill="{STAR}"/>
    <text x="640" y="52" text-anchor="middle" class="mono" font-size="13" fill="{ACCENT}">APSIS DX · REACHING TELOS</text>"""
    return panel(w, h, uid, body, rx=18, title="Apsis DX — Reaching Telos", seed=99, star_count=80,
                 avoid=lambda x, y: (440 < x < 840 and 28 < y < 64))


def main() -> None:
    write("banner.svg", banner())

    write("section-what-we-do.svg", section("01", "What we do", 11))
    write("section-media.svg", section("02", "Media", 12))
    write("section-open-source.svg", section("03", "Open Source", 13))
    write("section-tech-stack.svg", section("04", "Tech Stack", 14))
    write("section-operators.svg", section("05", "Operators", 15))
    write("section-contact.svg", section("06", "Contact", 16))

    write("card-build.svg", card("cb", "01 · Build", "AI Implementation",
                                 ["Embedding AI into real business", "workflows and automating what", "slows teams down."], None, 21))
    write("card-grow.svg", card("cg", "02 · Grow", "DX Talent Development",
                                ["Helping your people master AI", "so they can drive DX on their", "own."], None, 22, "p"))
    write("card-advise.svg", card("ca", "03 · Advise", "Technical Advisory",
                                  ["Hands-on guidance on", "architecture design and", "technology choices."], None, 23))

    write("card-blog.svg", card("mb", "Insights", "Blog",
                                ["Autonomous systems, algorithmic", "strategy, and enterprise", "architecture."], "apsis-dx.com/blog →", 41))
    write("card-signals.svg", card("ms", "Daily · AI News", "Signals",
                                   ["New models, features, and major", "announcements from leading AI", "companies — every day."], "apsis-dx.com/signals →", 42, "p"))
    write("card-works.svg", card("mw", "Case Studies", "Works",
                                 ["Where business and technology,", "people and organizations", "meet."], "apsis-dx.com/works →", 43))

    write("card-template-gas.svg", card("rg", "Template · GAS", "template-gas-monorepo",
                                        ["Many Google Apps Script projects", "in one TypeScript monorepo,", "bundled with esbuild."], "TypeScript · clasp · esbuild", 51, title_mono=True))
    write("card-template-slack.svg", card("rs", "Template · Slack", "template-slack-monorepo",
                                          ["Slack CLI apps on Slack's", "managed infrastructure —", "no server of your own."], "Deno · Slack CLI", 52, "p", title_mono=True))
    write("card-template-teams.svg", card("rt", "Template · Teams", "template-teams-bot",
                                          ["A Microsoft Teams Bot on Azure", "Functions, provisioned with", "Terraform."], "TypeScript · Azure · Terraform", 53, title_mono=True))

    write("tech-stack.svg", tech_stack())

    write("operator-loki.svg", operator("ol", "Loki", "DX Engineer", "Cloud-Xero", 61))
    write("operator-takuma.svg", operator("ot", "Takuma", "DX Engineer", "takuma531zov", 62))

    write("footer.svg", footer())


if __name__ == "__main__":
    main()
