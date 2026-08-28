"""yodaed check — the open-questions queue.

Every dangling reference and every rule the game would only reveal at launch
becomes a question here. BLOCKING questions stop a build; WARN questions are
dead ends and loose threads worth knowing about.

The semantic rules are lifted straight from the EV Bible's Override Mïsn
topic (vendor/ev-bible-extracted/EVO/Mïsn.txt) and specs/misn-evo.yaml.
"""
import re

from . import campaign as camp

BLOCK, WARN = "BLOCK", "WARN"


class Question:
    def __init__(self, level, slug, field, text, hint=None):
        self.level, self.slug, self.field = level, slug, field
        self.text, self.hint = text, hint

    def render(self):
        mark = "!" if self.level == BLOCK else "?"
        lines = [f"  {mark} {self.field}: {self.text}"]
        if self.hint:
            lines.append(f"      → {self.hint}")
        return "\n".join(lines)


def _q(out, level, m, field, text, hint=None):
    out.append(Question(level, m.slug if m else "(campaign)", field, text, hint))


def check_mission(m, world, cpg, out):
    doc = m.doc
    avail = doc.get("available") or {}
    obj = doc.get("objective") or {}
    cargo = doc.get("cargo") or {}
    ships = doc.get("ships") or {}
    reward = doc.get("reward") or {}

    # --- availability ------------------------------------------------------
    at = avail.get("at")
    if at is None:
        _q(out, BLOCK, m, "available.at", "no offering stellar named")
    elif at != ":any_inhabited" and at not in world.stellars:
        _q(out, BLOCK, m, "available.at", f'"{at}" — no stellar by that name',
           "check data/gazetteer.yaml, or create the stellar first")
    loc = avail.get("from", "computer")
    if loc not in camp.AVAIL_LOCS:
        _q(out, BLOCK, m, "available.from",
           f'"{loc}" — must be one of {sorted(camp.AVAIL_LOCS)}')
    elif loc == "ship":
        _q(out, WARN, m, "available.from",
           "offered from ship — needs a matching përs resource",
           "përs authoring is not implemented yet; track it by hand")
    chance = avail.get("chance", 100)
    if not isinstance(chance, int) or not 1 <= chance <= 100:
        _q(out, BLOCK, m, "available.chance",
           f"{chance!r} — AvailRandom is a percentage, 1-100")
    when = avail.get("when") or {}
    for key in when:
        if key not in ("set", "clear"):
            _q(out, BLOCK, m, f"available.when.{key}",
               "Override tests exactly one set-bit and one clear-bit",
               "misn has only AvailBitSet + AvailBitClr; no boolean algebra")

    # --- objective ---------------------------------------------------------
    for field, specials in (("travel_to", camp.TRAVEL_SPECIALS),
                            ("return_to", camp.RETURN_SPECIALS)):
        dest = obj.get(field)
        if dest is None:
            continue
        if str(dest).startswith(":"):
            if dest not in specials:
                _q(out, BLOCK, m, f"objective.{field}",
                   f'"{dest}" — unknown special; use {sorted(specials)}')
        elif dest not in world.stellars:
            _q(out, BLOCK, m, f"objective.{field}",
               f'"{dest}" — no stellar by that name')

    # --- cargo -------------------------------------------------------------
    if cargo:
        ctype = cargo.get("type")
        if ctype is None:
            _q(out, BLOCK, m, "cargo.type", "cargo block without a type")
        elif ctype != ":random" and ctype not in camp.CARGO:
            _q(out, BLOCK, m, "cargo.type",
               f'"{ctype}" — not a standard cargo type',
               "standard types: " + ", ".join(camp.CARGO[:6]) + ", …")
        qty = cargo.get("qty")
        if not isinstance(qty, int) or qty == 0:
            _q(out, BLOCK, m, "cargo.qty",
               f"{qty!r} — tons required (negative means ±50% of magnitude)")
        pickup, dropoff = cargo.get("pickup"), cargo.get("dropoff")
        if pickup is not None and pickup not in camp.PICKUPS:
            _q(out, BLOCK, m, "cargo.pickup",
               f'"{pickup}" — use {sorted(camp.PICKUPS)}')
        if dropoff is not None and dropoff not in camp.DROPOFFS:
            _q(out, BLOCK, m, "cargo.dropoff",
               f'"{dropoff}" — use {sorted(camp.DROPOFFS)}')
        if pickup == "at_travel" and dropoff == "at_travel":
            _q(out, BLOCK, m, "cargo",
               "picked up and dropped off at the same place",
               "the Bible warns Override behaves strangely; move one end")

    # --- special ships -----------------------------------------------------
    if ships:
        count = ships.get("count", 0)
        if not isinstance(count, int) or not 1 <= count <= 31:
            _q(out, BLOCK, m, "ships.count", f"{count!r} — 1-31 special ships")
        goal = ships.get("goal")
        if goal is not None and goal not in camp.SHIP_GOALS:
            _q(out, BLOCK, m, "ships.goal",
               f'"{goal}" — use {sorted(camp.SHIP_GOALS)}')
        dude = ships.get("dude")
        if dude is None:
            _q(out, BLOCK, m, "ships.dude", "special ships without a dude class")
        elif dude not in world.dudes:
            _q(out, WARN, m, "ships.dude",
               f'"{dude}" — no dude by that name in the 1997 plugin',
               "a new düde resource will be needed at build time")
        system = ships.get("system", ":initial")
        if str(system).startswith(":"):
            if system not in camp.SHIP_SYSTEM_SPECIALS:
                _q(out, BLOCK, m, "ships.system",
                   f'"{system}" — use {sorted(camp.SHIP_SYSTEM_SPECIALS)}')
        elif system not in world.systems:
            _q(out, BLOCK, m, "ships.system",
               f'"{system}" — no system by that name')
    elif (doc.get("ships") or {}).get("goal"):
        _q(out, BLOCK, m, "ships.goal", "a goal needs ships to apply to")

    # --- reward ------------------------------------------------------------
    if reward.get("record") is not None and not reward.get("govt"):
        _q(out, BLOCK, m, "reward.record",
           "a record change without a government is meaningless",
           "name the CompGovt whose ledger moves")
    govt = reward.get("govt")
    if govt and govt not in world.govts:
        _q(out, BLOCK, m, "reward.govt", f'"{govt}" — no such government')

    # --- hooks -------------------------------------------------------------
    for hook, cap in camp.HOOK_CAPACITY.items():
        writes = m.hook_bits(hook)
        if len(writes) > cap:
            _q(out, BLOCK, m, f"on.{hook}",
               f"writes {len(writes)} bits; the misn struct holds {cap}")
        for verb, bit in writes:
            if verb not in ("set", "clear") or not bit:
                _q(out, BLOCK, m, f"on.{hook}",
                   f'"{verb} {bit}" — write bits as "set <name>" or "clear <name>"')

    # --- time --------------------------------------------------------------
    tl = doc.get("time_limit")
    if tl is not None and (not isinstance(tl, int) or tl < 1):
        _q(out, BLOCK, m, "time_limit", f"{tl!r} — days, 1 and up (omit for none)")

    # --- text --------------------------------------------------------------
    for role, rel in (doc.get("text") or {}).items():
        path = m.path.parent.parent / rel
        if not path.exists():
            _q(out, BLOCK, m, f"text.{role}", f"{rel} — not written",
               f"write the prose at campaign/{rel}")
            continue
        prose = path.read_text(encoding="utf-8")
        for wc in re.findall(r"<([A-Z]{2,3})>", prose):
            if wc not in camp.WILDCARDS:
                _q(out, BLOCK, m, f"text.{role}",
                   f"<{wc}> — not a wildcard Override expands",
                   "known: " + " ".join(f"<{w}>" for w in sorted(camp.WILDCARDS)))


def check_chain(cpg, out):
    writers, testers = cpg.bit_writers(), cpg.bit_testers()
    external = {name for name, entry in cpg.bits.items()
                if isinstance(entry, dict) and entry.get("external")}

    for bit in sorted(set(writers) | set(testers)):
        if bit not in cpg.bits:
            _q(out, WARN, None, f"bit {bit}",
               "undocumented — add it to bits.yaml with a doc line")
    for bit, users in sorted(testers.items()):
        if bit not in writers and bit not in external:
            _q(out, BLOCK, None, f"bit {bit}",
               f"tested by {', '.join(users)} but never set by any mission",
               "the gate can never open; write the setter, or mark the bit "
               "external: true in bits.yaml if the 1997 chain owns it")
    for bit, users in sorted(writers.items()):
        if bit not in testers:
            _q(out, WARN, None, f"bit {bit}",
               f"set by {', '.join(users)} but never tested",
               "dead end — intended follow-up mission not written?")

    if len(set(writers) | set(testers) | set(cpg.bits)) > camp.MISSION_BIT_CEILING:
        _q(out, BLOCK, None, "bits",
           f"more than {camp.MISSION_BIT_CEILING} named bits — Override's hard ceiling")

    # Reachability: a mission is reachable when its set-gate is written by a
    # reachable mission (or is external). Fixpoint over the chain graph.
    reachable = set()
    changed = True
    while changed:
        changed = False
        for m in cpg.missions:
            if m.slug in reachable:
                continue
            gate = m.gate_bits().get("set")
            ok = (gate is None or gate in external or
                  any(w in reachable for w in writers.get(gate, [])))
            if ok:
                reachable.add(m.slug)
                changed = True
    for m in cpg.missions:
        if m.slug not in reachable:
            _q(out, WARN, m, "chain",
               "no path from a game start reaches this mission's gate")


def run(root, world=None):
    cpg = camp.Campaign(root)
    world = world or camp.load_world()
    out = []
    for m in cpg.missions:
        check_mission(m, world, cpg, out)
    check_chain(cpg, out)
    return cpg, out


def render(cpg, questions):
    lines = []
    by_slug = {}
    for q in questions:
        by_slug.setdefault(q.slug, []).append(q)
    for m in cpg.missions:
        qs = by_slug.get(m.slug, [])
        n = len(qs)
        tag = f"[{n} open question{'s' if n != 1 else ''}]" if n else "[clean]"
        lines.append(f"  MISSION  {m.name:<40}{tag}")
        lines.extend(q.render() for q in qs)
        lines.append("")
    if by_slug.get("(campaign)"):
        lines.append("  CHAIN")
        lines.extend(q.render() for q in by_slug["(campaign)"])
        lines.append("")
    blocking = sum(1 for q in questions if q.level == BLOCK)
    warns = len(questions) - blocking
    verdict = "Not buildable." if blocking else "Buildable."
    lines.append(f"  {warns} warning{'s' if warns != 1 else ''}, "
                 f"{blocking} blocking. {verdict}")
    return "\n".join(lines)
