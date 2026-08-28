#!/usr/bin/env python3
"""Export the remaining 1997 ConEx ships and landing art into Gonex.

For every recovered ship bank (shïp/spïn 166-175, except 174 which already
ships hand-tuned as yodacon97): slice the composited sprite sheet into the
36 per-frame PNGs Gonex's loader wants, write specs.xml converted from the
1997 shïp record (same mapping the yodacon97 port used: MaxVelocity=2x
Speed, TurnSpeed=30x Maneuver, Acceleration and Mass direct), and copy the
target / shipyard / comm PICTs (3000/5000/5300 + id-128).

Also copies the spöb CustPicID landing backgrounds — PICTs 13514/13515/
13516, the ConEx / Exeon / Cenron views the 1999 release said "will amaze
you" — into Gonex for the dock screen.

Usage: python3 data/export_ships.py
"""
import glob
import sys
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from evutils import rfork, tmpl  # noqa: E402

PLUGIN = REPO / "vendor/expanded/ConEx 1.2/ConEx1.2.rsrc"
SPRITES = REPO / "vendor/paulricheson/extracted/sprites"
PNGS = REPO / "vendor/paulricheson/extracted/png/ConEx1.2"
from data.export_gonex import gonex_dir  # noqa: E402

GONEX = gonex_dir() / "assets" / "data"

SPECS_XML = """<Ship>
    <ShipName Value="{name} '97" />
    <MaxVelocity Value="{maxv}" />
    <TurnSpeed Value="{turn}" />
    <Acceleration Value="{accel}" />
    <Mass Value="{mass}" />
    <CollisionRadius Value="{radius}" />
    <Damage Value="100" />
</Ship>
"""


def pict(pid):
    hits = glob.glob(str(PNGS / f"{pid}.png")) + glob.glob(str(PNGS / f"{pid}_*.png"))
    return Path(hits[0]) if hits else None


def main():
    plug = rfork.parse(rfork.unwrap_appledouble(PLUGIN.read_bytes()))
    tm = tmpl.templates_in(plug)
    ships = {r.rid: (r.name, dict(tmpl.decode(tm["shïp"], r.data)))
             for r in plug.resources if r.rtype == "shïp"}
    spins = {r.rid: dict(tmpl.decode(tm["spïn"], r.data))
             for r in plug.resources if r.rtype == "spïn"}

    exported = []
    for rid in range(166, 176):
        if rid == 174 or rid not in ships or rid not in spins:
            continue  # 174 = yodacon97, already in the tree
        name, d = ships[rid]
        sp = spins[rid]
        sheet_hits = glob.glob(str(SPRITES / f"{rid}_*.png"))
        if not sheet_hits:
            print(f"skip {rid} {name}: no composited sheet")
            continue
        folder = GONEX / "ships" / (name.lower().replace(" ", "-") + "97")
        folder.mkdir(parents=True, exist_ok=True)

        sheet = Image.open(sheet_hits[0]).convert("RGBA")
        w, h = sp["xSize"], sp["ySize"]
        for i in range(36):
            col, row = i % 6, i // 6
            frame = sheet.crop((col * w, row * h, (col + 1) * w, (row + 1) * h))
            frame.save(folder / f"{i:02d}.png")

        (folder / "specs.xml").write_text(SPECS_XML.format(
            name=name, maxv=2 * d["Speed"], turn=30 * max(d["Maneuver"], 1),
            accel=max(d["Accel"], 50), mass=max(d["Mass"], 10),
            radius=w // 2), encoding="utf-8")

        idx = rid - 128
        for kind, base in (("target", 3000), ("yard", 5000), ("comm", 5300)):
            src = pict(base + idx)
            if src:
                Image.open(src).save(folder / f"{kind}.png")
            else:
                # a ship without its own picture flies its sprite frame
                sheet.crop((0, 0, w, h)).save(folder / f"{kind}.png")
        exported.append((rid, folder.name, f"{w}x{h}"))

    land = GONEX / "conex" / "land"
    land.mkdir(parents=True, exist_ok=True)
    for pid in (13514, 13515, 13516):
        src = pict(pid)
        if src:
            Image.open(src).save(land / f"{pid}.png")

    for rid, folder, dims in exported:
        print(f"shïp {rid} → {folder} ({dims} x36)")
    print(f"landing backgrounds → {land}: 13514 ConEx, 13515 Exeon, 13516 Cenron")


if __name__ == "__main__":
    main()
