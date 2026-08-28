"""yodaed new — scaffold the file that answers a question.

`yodaed new mission <slug>` writes a mission source with every field
present and annotated, plus the brief stub it references, so the next
`yodaed check` run picks up exactly where the scaffold leaves off.
`yodaed new text <relpath>` writes a missing prose file on its own.
"""
from pathlib import Path

MISSION_TEMPLATE = """\
mission: {title}
available:
  at: ConEx                # stellar name from data/gazetteer.yaml, or :any_inhabited
  from: computer           # computer | bar | ship
  # when:                  # gate on named bits (one set + one clear, max)
  #   set: some_bit
  #   clear: other_bit
  chance: 100
objective:
  travel_to: Exeon         # name, or :none :random_inhabited :random_uninhabited
  return_to: :accepted     # or a name, :none, ...
# cargo: {{type: Parcels, qty: 10, pickup: at_start, dropoff: at_travel}}
# ships:
#   count: 3               # 1-31
#   dude: ConEx Shipping   # a düde from the 1997 plugin, or a new name
#   goal: escort           # destroy disable board escort observe rescue chase_off
#   system: :travel
reward:
  credits: 5000
# time_limit: 12           # days
text:
  brief: texts/{slug}/brief.md
on:
  success: set {slug_bit}_done
"""

BRIEF_TEMPLATE = """\
TODO — the offer, in the courier voice. Wildcards expand in-game:
<DST> destination stellar · <RST> return stellar · <CT> cargo type ·
<CQ> tons · <DL> deadline · <PN> the player's name.
"""


def new_mission(root, slug):
    root = Path(root)
    path = root / "missions" / f"{slug}.yaml"
    if path.exists():
        return f"yodaed: {path} already exists", 1
    title = slug.replace("-", " ").title()
    path.write_text(MISSION_TEMPLATE.format(
        title=title, slug=slug, slug_bit=slug.replace("-", "_")),
        encoding="utf-8")
    brief = root / "texts" / slug / "brief.md"
    brief.parent.mkdir(parents=True, exist_ok=True)
    brief.write_text(BRIEF_TEMPLATE, encoding="utf-8")
    return (f"scaffolded missions/{slug}.yaml and texts/{slug}/brief.md\n"
            f"now: edit both, then run `yodaed check` for the next question"), 0


def new_text(root, rel):
    path = Path(root) / rel
    if path.exists():
        return f"yodaed: {path} already exists", 1
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(BRIEF_TEMPLATE, encoding="utf-8")
    return f"scaffolded {rel}", 0
