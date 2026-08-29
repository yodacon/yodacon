# Flight recordings — version history

Every recording is one unedited take from the build it names, captured
with the in-game recorder (`GONEX_REC`, frames every 6 at 60 fps → 10 fps
GIF). Since rc3, the caption bar is burned into the frames by the game
itself (`GONEX_REC_CAPTION`): version, build date, gonex commit, take.
Old takes are never overwritten — the filename is the version.

| file | build date | gonex | mode | outcome |
| --- | --- | --- | --- | --- |
| `landing-rc1.gif` | 2026-08-27 | pre-RC1 | autoland | first full landing, ConEx station |
| `landing-rc2.gif` | 2026-08-28 | RC1 | autoland | one take orbit→parked, 12× time |
| `landing-rc3-manual.gif` | 2026-08-28 | `235d2a3` | **manual, hands off** | the bad landing: hull burning, TOO STEEP cue, emergency override, guardian dumping seed, 8 km off the line — every error and every new guidance element on display |
| `landing-rc3-auto.gif` | 2026-08-28 | `235d2a3` | **autoland** | the clean landing: corridor flown, 0.0 km off the pad line, debrief grade A 82/100 "PROVEN COURIER" |

The rc3 pair demonstrates the current UI: the expected-profile h–V
monitor, the dotted pipe projected to the pad, the flight-director bug
with STEER LEFT/RIGHT chevrons, burn warnings with steering cues, the
damage-control reflex, per-ship dials with the LOAD gauge, the split
interface through the ILS final, and the runway debrief with the landing
grade.
