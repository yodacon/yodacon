# Flight recordings — version history

Every recording is one unedited take from the build it names, captured
with the in-game recorder (`GONEX_REC`, frames every 6 at 60 fps → 10 fps
GIF). Since rc3, the caption bar is burned into the frames by the game
itself (`GONEX_REC_CAPTION`): version, build date, gonex commit, take.
Old takes are never overwritten — the filename is the version.

| file | build date | gonex | mode | outcome |
| --- | --- | --- | --- | --- |
| `landing-a1.gif` | 2026-08-27 | pre-RC1 | autoland | first full landing, ConEx station |
| `landing-a2.gif` | 2026-08-28 | RC1 | autoland | one take orbit→parked, 12× time |
| `landing-a3-manual.gif` | 2026-08-28 | `235d2a3` | **manual, hands off** | the bad landing: hull burning, TOO STEEP cue, emergency override, guardian dumping seed, 8 km off the line — every error and every new guidance element on display |
| `landing-a3-auto.gif` | 2026-08-28 | `235d2a3` | **autoland** | the clean landing: corridor flown, 0.0 km off the pad line, debrief grade A 82/100 "PROVEN COURIER" |
| `reentry-a3.gif` | 2026-08-31 | RC3 `95205bd` | **autoland** | the release build's fire: the solar-prominence fan and the ion flow streaming off the horizon, corridor flown, 0.0 km off the pad line, grade A 82/100 "PROVEN COURIER" |
| `takeoff-a3.gif` | 2026-08-31 | RC3 `95205bd` | **takeoff (scripted)** | first takeoff on tape: the runway roll down the spaceport road, rotate over the town, the ascent sheath punching through the upper air, sky going to black, orbital insertion |

The RC3-build pair (`reentry-a3.gif`, `takeoff-a3.gif`) is the sales
gallery on the front page: the full round trip — down through the fire to
the pad, then back up through it to orbit — on the tagged v0.1a3 build,
with the prominence layer and the ion flow both ways.

The earlier rc3 pair demonstrates the current UI: the expected-profile h–V
monitor, the dotted pipe projected to the pad, the flight-director bug
with STEER LEFT/RIGHT chevrons, burn warnings with steering cues, the
damage-control reflex, per-ship dials with the LOAD gauge, the split
interface through the ILS final, and the runway debrief with the landing
grade.
