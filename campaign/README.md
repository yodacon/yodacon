# campaign/ — mission-chain source

This is the plain-text source of truth for new Yodacon missions, per
[docs/mission-editor-plan.md](../docs/mission-editor-plan.md). The resource
fork (and the gonex export) are build artifacts; this tree is what you edit.

    missions/*.yaml     one mission per file — the filename stem is the slug
    texts/<slug>/*.md   the prose, diffable and reviewable as writing
    bits.yaml           control-bit registry; docs hand-written, cross-refs generated
    ids.lock            name -> resource ID ledger, allocated at build time

Work the queue, not the fields:

    python3 -m yodaed check campaign     # the open-questions queue
    python3 -m yodaed graph campaign     # the chain as Mermaid
    python3 -m yodaed bits campaign --write   # refresh bits.yaml cross-refs

(or `make check` from the repo root).

## The source format, by example

```yaml
mission: Lithium Run to Exeon
available:
  at: ConEx              # stellar name from data/gazetteer.yaml, or :any_inhabited
  from: bar              # computer | bar | ship (ship needs a përs)
  when:                  # named bits — Override tests one set + one clear, max
    set: pellet_contract_signed
    clear: pellet_route_proven
  chance: 80             # AvailRandom, 1-100
objective:
  travel_to: Exeon       # name, or :none :random_inhabited :random_uninhabited
  return_to: :accepted   # also :accepted (ReturnStel -4)
cargo: {type: Equipment, qty: 40, pickup: at_start, dropoff: at_travel}
ships:                   # optional special ships
  count: 3               # 1-31
  dude: ConEx Shipping   # a düde name from the 1997 plugin (or a new one)
  goal: escort           # destroy disable board escort observe rescue chase_off
  system: :travel        # :initial :any :travel :return :adjacent :player, or a name
reward: {credits: 25000, govt: Consolidated Express, record: 5}
time_limit: 12           # days; omit for none
text:                    # paths relative to campaign/
  brief: texts/pellet-run/brief.md
  complete: texts/pellet-run/complete.md
  fail: texts/pellet-run/fail.md
on:                      # bits written per outcome; "set <bit>" or "clear <bit>"
  success: set pellet_route_proven    # up to 2 (CompBitSet + CompBitSet2)
  failure: set pellet_route_burned    # up to 2; accept/refuse take 1 each
```

Prose may use Override's wildcards (`<DST>` `<DSY>` `<RST>` `<RSY>` `<CT>`
`<CQ>` `<DL>` `<PN>` `<PSN>` `<OSN>` `<SN>`); an unknown wildcard is a build
error. Field semantics come from the EV Bible's Override edition
(`vendor/ev-bible-extracted/EVO/Mïsn.txt`) via `specs/misn-evo.yaml`.

## The starter chain

`pellet-contract` → `pellet-run` → `exeon-standing-freight`: a handshake
haul, the lithium run that proves (or burns) the Exeon lane, and the
standing freight it unlocks. The final bit `exeon_lane_open` is a deliberate
loose thread — `yodaed check` flags it as the next chapter's gate.
