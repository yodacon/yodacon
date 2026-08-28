"""Load a campaign source tree and the world it must resolve against.

A campaign directory holds:

    missions/*.yaml     one mission per file; the filename stem is the slug
    texts/<slug>/*.md   mission prose, referenced by relative path
    bits.yaml           the control-bit registry (docs; cross-refs generated)
    ids.lock            name -> resource ID ledger (allocated at build time)

The world it resolves against is already in the repo:

    data/gazetteer.yaml                        systems, stellars, governments
    vendor/paulricheson/extracted/ConEx1.2/düde/   ship-class (dude) names
"""
from pathlib import Path

from . import yamlite

REPO = Path(__file__).resolve().parents[1]

# Special destination keywords, mirroring the Bible's negative codes.
TRAVEL_SPECIALS = {":none": -1, ":random_inhabited": -2, ":random_uninhabited": -3}
RETURN_SPECIALS = {":none": -1, ":random_inhabited": -2, ":random_uninhabited": -3,
                   ":accepted": -4}
SHIP_SYSTEM_SPECIALS = {":initial": -1, ":any": -2, ":travel": -3, ":return": -4,
                        ":adjacent": -5, ":player": -6}

SHIP_GOALS = {"destroy": 0, "disable": 1, "board": 2, "escort": 3,
              "observe": 4, "rescue": 5, "chase_off": 6}
AVAIL_LOCS = {"computer": 0, "bar": 1, "ship": 2}
PICKUPS = {"at_start": 0, "at_travel": 1, "on_boarding": 2}
DROPOFFS = {"at_travel": 0, "at_return": 1}

# Standard cargo types, same table data/export_gonex.py ships to the game.
CARGO = ["Food", "Industrial", "Medical", "Luxury Goods", "Metal", "Equipment",
         "Passengers", "Criminal", "Drugs", "Ore Samples", "Munitions", "Ore",
         "Data", "Lumber", "Commandos", "Orders", "Documents", "Parcels",
         "Uridium", "Rebel Operative", "Confed Operative", "Garbage",
         "Prototype", "Kestrel Subassemblies"]

# Wildcards Override expands inside mission descs (EV Bible, Mïsn topic).
WILDCARDS = {"DSY", "DST", "RSY", "RST", "CT", "CQ", "DL", "PN", "PSN",
             "OSN", "SN"}

MISSION_BIT_CEILING = 256

# Hook -> how many bits the misn struct can write (CompBitSet+CompBitSet2 etc.)
HOOK_CAPACITY = {"accept": 1, "success": 2, "failure": 2, "refuse": 1}


class World:
    """Everything names resolve against."""

    def __init__(self, gazetteer, dude_names):
        self.systems = {}    # name -> id
        self.stellars = {}   # name -> id
        self.govts = set()
        for rid, entry in (gazetteer.get("systems") or {}).items():
            self.systems[entry["name"]] = rid
            if entry.get("govt"):
                self.govts.add(entry["govt"])
        for rid, entry in (gazetteer.get("stellars") or {}).items():
            self.stellars[entry["name"]] = rid
            if entry.get("govt"):
                self.govts.add(entry["govt"])
        self.dudes = set(dude_names)


def load_world(repo=REPO):
    gazetteer = yamlite.load(repo / "data" / "gazetteer.yaml")
    dude_dir = repo / "vendor" / "paulricheson" / "extracted" / "ConEx1.2" / "düde"
    dudes = []
    if dude_dir.is_dir():
        for f in sorted(dude_dir.glob("*.bin")):
            _, _, name = f.stem.partition("_")
            if name:
                dudes.append(name)
    return World(gazetteer, dudes)


class Mission:
    def __init__(self, slug, path, doc):
        self.slug = slug
        self.path = path
        self.doc = doc

    @property
    def name(self):
        return self.doc.get("mission") or self.slug

    def hook_bits(self, hook):
        """Bits written by an on: hook, as (verb, bit) pairs."""
        raw = (self.doc.get("on") or {}).get(hook)
        if raw is None:
            return []
        items = raw if isinstance(raw, list) else [raw]
        out = []
        for item in items:
            verb, _, bit = str(item).partition(" ")
            out.append((verb, bit.strip()))
        return out

    def gate_bits(self):
        """Bits tested for availability, as {'set': bit?, 'clear': bit?}."""
        when = (self.doc.get("available") or {}).get("when") or {}
        return {k: when[k] for k in ("set", "clear") if when.get(k)}


class Campaign:
    def __init__(self, root):
        self.root = Path(root)
        self.missions = []
        self.bits = {}       # name -> {doc, external?}
        self.ids_lock = {}
        for path in sorted((self.root / "missions").glob("*.yaml")):
            self.missions.append(Mission(path.stem, path, yamlite.load(path)))
        bits_file = self.root / "bits.yaml"
        if bits_file.exists():
            self.bits = yamlite.load(bits_file) or {}
        lock = self.root / "ids.lock"
        if lock.exists():
            self.ids_lock = yamlite.load(lock) or {}

    def bit_writers(self):
        """bit name -> [slug] of missions that write it (any hook)."""
        out = {}
        for m in self.missions:
            for hook in HOOK_CAPACITY:
                for _verb, bit in m.hook_bits(hook):
                    out.setdefault(bit, []).append(m.slug)
        return out

    def bit_testers(self):
        """bit name -> [slug] of missions that gate on it."""
        out = {}
        for m in self.missions:
            for bit in m.gate_bits().values():
                out.setdefault(bit, []).append(m.slug)
        return out
