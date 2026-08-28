#!/usr/bin/env python3
"""Export the joined universe and the 36 ConEx missions as Gonex game data.

Writes into ~/code/Gonex/assets/data/conex/:
- galaxy.json   — systems (coords, links, govt) and stellars (parent system,
  govt, tech, and a derived landing profile for the reentry simulator)
- missions.json — the recovered mïsn records with their 1997 brief texts,
  plus the one restoration fix: mission 285's impossible AvailBitClr 161 is
  lifted so the Marks Logging finale is reachable (flagged "restoration").

Rerun after any ConEx restoration edit; the game inherits the repair.
"""
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
from evutils import rfork, tmpl  # noqa: E402
from data.build_gazetteer import BASE, PLUGIN, load, overlay  # noqa: E402

def gonex_dir():
    """The export target: $GONEX_DIR, else the gonex/ submodule, else the
    development checkout at ~/code/Gonex."""
    if env := os.environ.get("GONEX_DIR"):
        return Path(env)
    if (REPO / "gonex").is_dir():
        return REPO / "gonex"
    return Path.home() / "code" / "Gonex"


OUT = gonex_dir() / "assets" / "data" / "conex"

CARGO = ["Food", "Industrial", "Medical", "Luxury Goods", "Metal", "Equipment",
         "Passengers", "Criminal", "Drugs", "Ore Samples", "Munitions", "Ore",
         "Data", "Lumber", "Commandos", "Orders", "Documents", "Parcels",
         "Uridium", "Rebel Operative", "Confed Operative", "Garbage",
         "Prototype", "Kestrel Subassemblies"]


def cargo_name(t):
    if t is None or t < 0:
        return ""
    if 0 <= t < len(CARGO):
        return CARGO[t]
    if t >= 1000:
        return "Mixed Freight"  # random-type special
    return f"Cargo {t}"


def landing_profile(rid, name, tech):
    """Deterministic per-stellar reentry difficulty. Higher tech pads sit on
    denser, better-tracked worlds with narrower corridors and bigger bonuses;
    Earth is the checkride."""
    tech = max(0, tech or 0)
    width = max(0.25, 0.58 - 0.012 * tech)     # corridor half-width, deg
    atmos = 0.8 + ((rid * 7) % 5) / 10.0       # density scale 0.8-1.2
    grav = 0.85 + ((rid * 11) % 4) / 10.0      # gravity scale 0.85-1.15
    if name == "Earth":                        # the canonical checkride
        width, atmos, grav = 0.22, 1.0, 1.0
    return {
        "corridorHalfWidthDeg": round(width, 3),
        "atmosScale": round(atmos, 2),
        "gravityScale": round(grav, 2),
        "padBonus": 2000 * tech,
    }


def main():
    base, plugin = load(BASE), load(PLUGIN)
    systems = overlay(base, plugin, "sÿst")
    spobs = overlay(base, plugin, "spöb")
    govts = overlay(base, plugin, "gövt")

    def gname(gid):
        return govts[gid][0] if gid in govts else ""

    gal = {"systems": {}, "stellars": {}}
    for rid in sorted(systems):
        name, f, src = systems[rid]
        if f is None:
            continue
        links = sorted({f[k] for k in f if k.startswith("Con")
                        and f[k] != -1 and f[k] != rid and f[k] in systems})
        navs = [f[f"Nav{i}"] for i in range(1, 5)
                if f.get(f"Nav{i}", -1) >= 128 and f.get(f"Nav{i}") in spobs]
        gal["systems"][str(rid)] = {
            "name": name or f"#{rid}", "x": f["xPos"], "y": f["yPos"],
            "links": links, "stellars": navs,
            "govt": gname(f.get("Govt")), "source": src,
        }
    for rid in sorted(spobs):
        name, f, src = spobs[rid]
        if f is None:
            continue
        holders = [sid for sid, entry in gal["systems"].items()
                   if rid in entry["stellars"]]
        entry = {
            "name": name or f"#{rid}",
            "system": int(holders[0]) if holders else f.get("System", -1),
            "govt": gname(f.get("Govt")), "tech": f.get("TechLevel", 0),
            "sprite": 1 + (rid % 18),
            "landing": landing_profile(rid, name, f.get("TechLevel", 0)),
            "source": src,
        }
        if f.get("CustPicID", -1) > 0:
            entry["landPic"] = f["CustPicID"]
        gal["stellars"][str(rid)] = entry

    # missions, with prose
    plug = rfork.parse(rfork.unwrap_appledouble(PLUGIN.read_bytes()))
    tm = tmpl.templates_in(plug)
    descs = {r.rid: r.data.split(b"\x00")[0].decode("mac_roman")
             for r in plug.resources if r.rtype == "dësc"}
    missions = []
    for r in sorted((r for r in plug.resources if r.rtype == "mïsn"),
                    key=lambda r: r.rid):
        d = {l: v for l, v in tmpl.decode(tm["mïsn"], r.data)}
        m = {
            "id": r.rid,
            "name": (r.name or "").replace("\r", "").strip(),
            "availStel": d["AvailStel"], "availBitSet": d["AvailBitSet"],
            "availBitClr": d["AvailBitClr"], "availRandom": d["AvailRandom"],
            "travelStel": d["TravelStel"], "returnStel": d["ReturnStel"],
            "cargoType": d["CargoType"], "cargoName": cargo_name(d["CargoType"]),
            "cargoQty": d["CargoQty"], "pay": d["PayVal"],
            "shipCount": d["ShipCount"], "compBitSet": d["CompBitSet"],
            "timeLimit": d["TimeLimit"],
            "brief": descs.get(d["BriefText"], ""),
            "quickBrief": descs.get(d["QuickBrief"], ""),
            "compText": descs.get(d["CompText"], ""),
        }
        if r.rid == 285:
            # 1997 chain bug: AvailBitClr 161 can never be satisfied once the
            # chain sets bit 161. Restoration lifts it (see LR-2026-02 / the
            # Flight Manual dossier).
            m["availBitClr"] = -1
            m["restoration"] = "stock AvailBitClr=161 made this unreachable"
        missions.append(m)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "galaxy.json").write_text(
        json.dumps(gal, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (OUT / "missions.json").write_text(
        json.dumps(missions, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"wrote {OUT}/galaxy.json: {len(gal['systems'])} systems, "
          f"{len(gal['stellars'])} stellars")
    print(f"wrote {OUT}/missions.json: {len(missions)} missions")


if __name__ == "__main__":
    main()
