#!/usr/bin/env python3
"""Render data/universe-map.svg: the base-EV + ConEx galaxy, HUD-styled.

Systems are plotted at their sÿst coordinates, hyperspace links drawn
between them. Colors follow the Phase 6 style tokens from backlog.md.
Sources as in build_gazetteer.py; run after it, or standalone.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "data"))
from build_gazetteer import BASE, PLUGIN, load, overlay  # noqa: E402

VOID, CRT, CRT_LIT = "#05070a", "#0d3d12", "#1d7a24"
PHOSPHOR, CHROME, ACCENT = "#5cff5c", "#dfe4e6", "#c26bd8"

W, H, MARGIN = 1200, 900, 70


def main():
    base, plugin = load(BASE), load(PLUGIN)
    systems = {
        rid: v for rid, v in overlay(base, plugin, "sÿst").items() if v[1] is not None
    }

    xs = [f["xPos"] for _, f, _ in systems.values()]
    ys = [f["yPos"] for _, f, _ in systems.values()]
    span_x, span_y = max(xs) - min(xs) or 1, max(ys) - min(ys) or 1
    scale = min((W - 2 * MARGIN) / span_x, (H - 2 * MARGIN) / span_y)

    def at(f):
        # EV map coordinates: +y is south, same as SVG
        return (
            round(MARGIN + (f["xPos"] - min(xs)) * scale, 1),
            round(MARGIN + (f["yPos"] - min(ys)) * scale, 1),
        )

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'font-family="Courier, monospace">',
        f'<rect width="{W}" height="{H}" fill="{VOID}"/>',
        f'<rect x="8" y="8" width="{W-16}" height="{H-16}" fill="none" '
        f'stroke="{CRT}" stroke-width="2"/>',
        f'<text x="24" y="36" fill="{PHOSPHOR}" font-size="18" '
        f'letter-spacing="3">CONEX UNIVERSE — NAV CHART</text>',
        f'<text x="24" y="56" fill="{ACCENT}" font-size="11">'
        f'{len(systems)} SYSTEMS · BASE EV 1.0.4 + CONEX 1.2 OVERLAY</text>',
    ]

    # hyperspace links (each drawn once)
    drawn = set()
    for rid, (name, f, src) in systems.items():
        for k, v in f.items():
            if not k.startswith("Con") or v == -1 or v == rid:
                continue
            if v in systems and (v, rid) not in drawn:
                x1, y1 = at(f)
                x2, y2 = at(systems[v][1])
                svg.append(
                    f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                    f'stroke="{CRT_LIT}" stroke-width="1" opacity="0.55"/>'
                )
                drawn.add((rid, v))

    # systems over the links; ConEx's own territory in accent
    for rid, (name, f, src) in sorted(systems.items(), key=lambda kv: kv[1][2]):
        x, y = at(f)
        conex = src != "base"
        color = ACCENT if conex else PHOSPHOR
        r = 5 if conex else 3
        svg.append(
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{VOID}" '
            f'stroke="{color}" stroke-width="{1.6 if conex else 1}"/>'
        )
        anchor = "start" if x < W - 120 else "end"
        dx = 9 if anchor == "start" else -9
        weight = ' font-weight="bold"' if conex else ""
        svg.append(
            f'<text x="{x+dx}" y="{y+4}" fill="{color}" font-size="10" '
            f'text-anchor="{anchor}" opacity="{0.95 if conex else 0.7}"{weight}>'
            f"{(name or f'#{rid}')}</text>"
        )

    # legend, chrome-framed
    lx, ly = 24, H - 92
    svg += [
        f'<rect x="{lx-10}" y="{ly-18}" width="270" height="76" fill="{VOID}" '
        f'stroke="{CHROME}" stroke-width="1" opacity="0.9"/>',
        f'<circle cx="{lx+6}" cy="{ly}" r="3" fill="{VOID}" stroke="{PHOSPHOR}"/>',
        f'<text x="{lx+18}" y="{ly+4}" fill="{PHOSPHOR}" font-size="11">base EV system</text>',
        f'<circle cx="{lx+6}" cy="{ly+22}" r="5" fill="{VOID}" stroke="{ACCENT}" stroke-width="1.6"/>',
        f'<text x="{lx+18}" y="{ly+26}" fill="{ACCENT}" font-size="11">ConEx addition / override</text>',
        f'<line x1="{lx}" y1="{ly+44}" x2="{lx+12}" y2="{ly+44}" stroke="{CRT_LIT}"/>',
        f'<text x="{lx+18}" y="{ly+48}" fill="{PHOSPHOR}" font-size="11" opacity="0.7">hyperspace link</text>',
        "</svg>",
    ]

    out = REPO / "data" / "universe-map.svg"
    out.write_text("\n".join(svg) + "\n", encoding="utf-8")
    print(f"wrote {out}: {len(systems)} systems, {len(drawn)} link segments")


if __name__ == "__main__":
    main()
