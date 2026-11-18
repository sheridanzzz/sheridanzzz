#!/usr/bin/env python3
"""Builds the profile README and its SVG cards.

    python3 scripts/build.py

Needs Pillow. Reads screenshots from the portfolio repo and the Geist fonts
that ship with Next.js (override with SHOTS=... FONTS=...).
"""
import base64
import hashlib
import io
import math
import os
import pathlib
from html import escape

from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
HOME = pathlib.Path.home()
SHOTS = pathlib.Path(os.environ.get("SHOTS", HOME / "GitHub/sheridan-portfolio/src/assets/shots"))
FONTS = pathlib.Path(os.environ.get("FONTS", HOME / "GitHub/visamate/node_modules/next/dist/next-devtools/server/font"))

W = 880
BG, BAR, LINE = "#05070a", "#0a0f14", "#1b232c"
P, S, M = "#e9eef2", "#8b98a4", "#4f5b66"
AMB, BLU, GRN, PUR, SHA = "#f5a524", "#79c0ff", "#7ee787", "#d2a8ff", "#d29922"
MONO = "GM,'Geist Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
SANS = "G,Geist,-apple-system,'Segoe UI',Helvetica,Arial,sans-serif"

LIVE = (GRN, "#0f2a17")
ROWS = [
    dict(sha="a1r7a1", lane=0, head=True, refs=[("HEAD -> main", AMB, "#2b1d05"), ("live beta", *LIVE)],
         title="airtail: spending, sorted from your inbox", url="airtail.org",
         stack="Next.js · MongoDB · Gemini · SwiftUI", shot="airtail"),
    dict(sha="1edg42", lane=0, refs=[("live alpha", *LIVE)],
         title="ledgr: a year of receipts, ready for tax time", url="ledgrtax.com",
         stack="Next.js · Postgres · Expo", shot="ledgr"),
    dict(sha="5ca1e0", lane=1, refs=[("work", BLU, "#0c2140")],
         title="scalene: price + forecast planners from first commit",
         stack="C#/.NET · gRPC · Azure · Angular · since 2024"),
    dict(sha="0rb17e", lane=0, refs=[("mac app store soon", PUR, "#2a1230")],
         title="orbit: hold ⌥⌘, your apps gather at the pointer", url="orbitmac.app",
         stack="Swift · SwiftUI · AppKit", shot="orbit"),
    dict(sha="v15a01", lane=0, refs=[("live", *LIVE)],
         title="visamate: partner visa evidence, ready to lodge", url="visamateapp.com",
         stack="Next.js · Supabase · pdf-lib", shot="visamate"),
    dict(sha="je7c23", lane=1, small=True, title="jet charge: software engineer", year="2023"),
    dict(sha="0pe921", lane=1, small=True, title="openpay: initial commit", year="2021"),
]
STATS = [("2", "greenfield services"), ("550+", "unit tests shipped"), ("35+", "enterprise tenants"), ("3", "side products live")]
PROJECT_CHIPS = [("airtail.org", "https://airtail.org"), ("ledgrtax.com", "https://ledgrtax.com"),
                 ("visamateapp.com", "https://visamateapp.com"), ("orbitmac.app", "https://orbitmac.app")]
PERSONAL_CHIPS = [("sheridangomes.com", "https://sheridangomes.com", "globe"),
                  ("in/sheridangomes", "https://www.linkedin.com/in/sheridangomes", "in"),
                  ("me@sheridangomes.com", "mailto:me@sheridangomes.com", "at")]


def b64(data):
    return base64.b64encode(data).decode()


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def font_css(sans=True):
    # ponytail: whole Latin woff2 (~30 KB each) embedded, subset with fontTools if size ever matters
    faces = [("GM", "geist-mono-latin.woff2")] + ([("G", "geist-latin.woff2")] if sans else [])
    return "".join(
        f"@font-face{{font-family:{n};font-weight:100 900;"
        f"src:url(data:font/woff2;base64,{b64((FONTS / f).read_bytes())}) format('woff2')}}"
        for n, f in faces)


def svg(w, h, title, body, css="", sans=True):
    style = (font_css(sans) + f"text{{font-family:{MONO};white-space:pre}}.s{{font-family:{SANS}}}" + css +
             "@media (prefers-reduced-motion:reduce){*{animation:none!important}}")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
            f"<title>{escape(title)}</title><style>{style}</style>{''.join(body)}"
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" fill="none" stroke="{LINE}"/></svg>')


def t(x, y, s, size=12, fill=S, extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" {extra}>{escape(s)}</text>'


def line(x1, y1, x2, y2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{LINE}"/>'


def wave_png(cols=220, rows=30, k=4):
    """Dithered amber signal, periodic in x so two copies scroll seamlessly."""
    bayer = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
    tau, bg, dot = 2 * math.pi / cols, rgb(BG), rgb(LINE)
    im = Image.new("RGB", (cols, rows), bg)
    px = im.load()
    for i in range(cols):
        y0 = rows * .55 + 4 * math.sin(3 * tau * i) + 2.5 * math.sin(9 * tau * i + 1) + 5 * math.sin(tau * i + .5)
        width = 7 + 3 * math.sin(5 * tau * i)
        amp = .55 + .45 * math.sin(2 * tau * i + 2)
        for j in range(rows):
            v = max(0.0, 1 - abs(j - y0) / width) * amp
            if v * 16 > bayer[j & 3][i & 3]:
                a = min(1.0, v * 1.4)
                alpha, c = .25 + .75 * a, (245, 120 + round(a * 60), 36)
                px[i, j] = tuple(round(b * (1 - alpha) + cc * alpha) for b, cc in zip(bg, c))
            elif (i * 7 + j * 13) % 97 == 0:
                px[i, j] = dot
    strip = Image.new("RGB", (cols * 2, rows))
    strip.paste(im, (0, 0))
    strip.paste(im, (cols, 0))
    buf = io.BytesIO()
    strip.resize((cols * 2 * k, rows * k), Image.NEAREST).save(buf, "PNG", optimize=True)
    return buf.getvalue()


def thumb(name, w=312, h=160):
    im = Image.open(SHOTS / f"{name}.jpg").convert("RGB")
    im = im.crop((0, 0, im.width, round(im.width * h / w))).resize((w, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=82, optimize=True)
    return b64(buf.getvalue())


def header():
    H, g, split = 426, 150, 384
    b = [f'<rect width="{W}" height="{H}" fill="{BG}"/>', f'<rect width="{W}" height="30" fill="{BAR}"/>',
         t(12, 19, "sheridan", 12, P, 'font-weight="500"'),
         f'<rect class="pulse" x="82" y="11.5" width="7" height="7" fill="{AMB}"/>',
         t(98, 19, "SHIPPING", 12, AMB), t(W - 12, 19, "sheridangomes.com", 12, M, 'text-anchor="end"'),
         f'<clipPath id="bn"><rect y="30" width="{W}" height="120"/></clipPath>',
         f'<g clip-path="url(#bn)"><image class="scroll" x="0" y="30" width="{2 * W}" height="120" '
         f'href="data:image/png;base64,{b64(wave_png())}"/></g>',
         line(0, 30.5, W, 30.5), line(0, g + .5, W, g + .5),
         line(split + .5, g, split + .5, H), line(632.5, g, 632.5, H), line(split, 288.5, W, 288.5),
         t(24, 214, "Sheridan", 44, P, 'class="s" font-weight="500" letter-spacing="-1.3"'),
         t(24, 260, "Gomes", 44, P, 'class="s" font-weight="500" letter-spacing="-1.3"'),
         t(24, 292, "Senior software engineer.", 13, P), t(24, 310, "Enterprise platforms and practical AI.", 13, P)]
    for y, (k, v) in zip((346, 368, 390), [("NOW", "shipping Airtail and Ledgr"), ("BASED", "Melbourne, AU"),
                                           ("HANDLE", "@sheridanzzz")]):
        b += [t(24, y, k, 12, M), t(104, y, v, 12, P)]
    cells = [("WORKING AT", "Scalene Group"), ("FOCUS", ".NET platforms"), ("STACK", "C# · TS · Swift"),
             ("ALSO", "Mac apps + AI")]
    for (x, y), (k, v) in zip([(split, g), (632, g), (split, 288), (632, 288)], cells):
        b += [t(x + 16, y + 28, k, 11, M), t(x + 16, y + 52, v, 13, P, 'font-weight="500"')]
    css = (".pulse{animation:p 1.6s ease-in-out infinite}@keyframes p{50%{opacity:.3}}"
           ".scroll{animation:s 18s steps(220) infinite}@keyframes s{to{transform:translateX(-880px)}}")
    title = ("Sheridan Gomes (sheridanzzz): senior software engineer in Melbourne, Australia. "
             "Enterprise platforms and practical AI. Working at Scalene Group.")
    return svg(W, H, title, b, css)


def log():
    top, y, centers = 38, 46, []
    b = [f'<rect width="{W}" height="2000" fill="#07090c"/>', f'<rect width="{W}" height="{top}" fill="{BAR}"/>',
         line(0, top - .5, W, top - .5),
         f'<text x="14" y="24" font-size="12.5"><tspan fill="{AMB}">sheridan@melbourne</tspan> '
         f'<tspan fill="{BLU}">~</tspan><tspan fill="{P}"> % git log --graph --all</tspan></text>',
         f'<rect class="cur" x="{14 + 7.5 * 45}" y="13" width="8" height="15" fill="{P}"/>',
         f'<rect x="{W - 312}" y="18" width="10" height="2" fill="{AMB}"/>', t(W - 296, 23, "main · side projects", 11, M),
         f'<rect x="{W - 132}" y="18" width="10" height="2" fill="{BLU}"/>', t(W - 116, 23, "work · day job", 11, M)]
    rows = []
    for r in ROWS:
        h = 58 if r.get("small") else 92
        c = y + h / 2
        centers.append((r["lane"], c, r.get("head")))
        rows.append(t(76, c + 4, r["sha"], 12, SHA))
        if r.get("small"):
            rows.append(f'<text x="140" y="{c + 4}" font-size="13"><tspan fill="{S}">{escape(r["title"])}</tspan>'
                        f'<tspan fill="{M}"> · {r["year"]}</tspan></text>')
        else:
            x = 140
            for label, fg, bg in r["refs"]:
                w = len(label) * 6.6 + 12
                rows += [f'<rect x="{x}" y="{c - 17}" width="{w:.1f}" height="17" rx="3" fill="{bg}"/>',
                         t(x + 6, c - 4.5, label, 11, fg, 'font-weight="500"')]
                x += w + 6
            rows.append(t(round(x, 1), c - 4, r["title"], 13, P))
            url = f'<tspan fill="{BLU}">{r["url"]}</tspan><tspan> · </tspan>' if r.get("url") else ""
            rows.append(f'<text x="140" y="{c + 17}" font-size="11.5" fill="#6e7a85">{url}{escape(r["stack"])}</text>')
            if r.get("shot"):
                tx, ty = W - 14 - 156, c - 40
                rows += [f'<clipPath id="c{r["sha"]}"><rect x="{tx}" y="{ty}" width="156" height="80" rx="3"/></clipPath>',
                         f'<image x="{tx}" y="{ty}" width="156" height="80" clip-path="url(#c{r["sha"]})" '
                         f'preserveAspectRatio="xMidYMin slice" href="data:image/jpeg;base64,{thumb(r["shot"])}"/>',
                         f'<rect x="{tx + .5}" y="{ty + .5}" width="155" height="79" rx="3" fill="none" stroke="{LINE}"/>']
        y += h
    lane_x = (24, 50)
    main = [c for lane, c, _ in centers if lane == 0]
    merge = next(c for lane, c, _ in centers if lane == 1 and c > main[-1])
    b += [f'<path d="M24 {main[0]} V{main[-1] + 10} C24 {main[-1] + 40} 50 {main[-1] + 40} 50 {merge - 8}" '
          f'stroke="{AMB}" stroke-width="2" fill="none"/>',
          f'<path d="M50 {top} V{centers[-1][1]}" stroke="{BLU}" stroke-width="2" fill="none"/>']
    for lane, c, head in centers:
        col = AMB if lane == 0 else BLU
        b.append(f'<circle cx="{lane_x[lane]}" cy="{c}" r="{6 if head else 5}" fill="{col if head else "#07090c"}" '
                 f'stroke="{col}" stroke-width="2"/>')
    b += rows
    st = y + 8
    b.append(line(0, st + .5, W, st + .5))
    for i, (n, label) in enumerate(STATS):
        x = i * W / len(STATS)
        if i:
            b.append(line(x + .5, st, x + .5, st + 64))
        b += [t(x + 16, st + 30, n, 20, P, 'class="s" font-weight="500"'), t(x + 16, st + 50, label, 11, S)]
    css = ".cur{animation:b 1s steps(1) infinite}@keyframes b{50%{opacity:0}}"
    title = ("git log of Sheridan's work. Side projects on main: Airtail (airtail.org, live beta), "
             "Ledgr (ledgrtax.com, live alpha), Orbit (orbitmac.app, coming to the Mac App Store), "
             "VisaMate (visamateapp.com, live). Day job on work: Scalene Group since 2024, JET Charge 2023, "
             "Openpay 2021.")
    return svg(W, st + 64, title, b, css)


def chip(label, icon):
    w = round(14 + 12 + 10 + len(label) * 7.2 + 12 + 8 + 14)
    icons = {
        "sq": f'<rect x="16" y="14" width="8" height="8" fill="{AMB}"/>',
        "globe": f'<g fill="none" stroke="{M}" stroke-width="1.2"><circle cx="20" cy="18" r="6"/>'
                 f'<ellipse cx="20" cy="18" rx="2.6" ry="6"/><path d="M14 18h12"/></g>',
        "in": t(14, 22, "in", 12, M, 'font-weight="600"'),
        "at": t(15, 22, "@", 12, M),
    }
    ax = w - 24
    body = [f'<rect width="{w}" height="36" fill="{BG}"/>', icons[icon], t(36, 22, label, 12, P),
            f'<path d="M{ax} {22} l7 -7 M{ax + 2} {15} h5 v5" fill="none" stroke="{M}" stroke-width="1.3"/>']
    return svg(w, 36, label, body, sans=False)


def save(name, text):
    (ASSETS / name).write_text(text)
    return f"./assets/{name}?v={hashlib.sha1(text.encode()).hexdigest()[:8]}"


def main():
    ASSETS.mkdir(exist_ok=True)
    h, lg = save("header.svg", header()), save("log.svg", log())

    def chips(items):
        out = []
        for label, href, *icon in items:
            src = save(f"chip-{label.split('.')[0].replace('/', '-').replace('@', '-')}.svg", chip(label, (icon or ["sq"])[0]))
            out.append(f'  <a href="{href}"><img src="{src}" height="36" alt="{label}"></a>')
        return "\n".join(out)

    readme = f"""<!-- Generated by scripts/build.py. Edit the script, then run: python3 scripts/build.py -->
<a href="https://sheridangomes.com"><img src="{h}" width="100%" alt="Sheridan Gomes, senior software engineer in Melbourne. Enterprise platforms and practical AI. Working at Scalene Group."></a>

<a href="https://sheridangomes.com"><img src="{lg}" width="100%" alt="git log of my work: Airtail, Ledgr, Orbit and VisaMate on main; Scalene Group, JET Charge and Openpay on work."></a>

<p align="center">
{chips(PROJECT_CHIPS)}
</p>
<p align="center">
{chips(PERSONAL_CHIPS)}
</p>
"""
    (ROOT / "README.md").write_text(readme)
    for f in sorted(ASSETS.iterdir()):
        print(f"{f.name:28} {f.stat().st_size / 1024:7.1f} KB")


if __name__ == "__main__":
    main()
