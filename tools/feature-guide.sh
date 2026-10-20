#!/bin/sh
# feature-guide.sh — assemble the pictures for docs/FEATURE_GUIDE.md.
#
# Nothing here is captured live. Gonex needs a real window (Ebitengine has no
# headless renderer), so every picture is one the repo already holds, taken
# from the running build with GONEX_SHOT / GONEX_REC:
#
#   docs/game/img/*.png          the flight manual's screens, 22 Sep 2026, seed 20260922
#   assets/gpis-instruments/*    the six-stage cockpit, 1 Sep 2026
#   assets/governor-desk/*       the Governor's Desk, day 120
#   assets/landing-a3-*.gif      flight recordings (one frame each, scaled 2x)
#
# The script copies each one into docs/features/NN-name.png and burns in
# numbered markers that the guide's captions refer to. Re-run it after the
# source pictures change; the marker positions are in 1024x768 pixels.
#
#   sh tools/feature-guide.sh
#
# Needs ImageMagick 7 (`magick`) and nothing else.

set -eu

ROOT=$(cd "$(dirname "$0")/.." && pwd)
OUT="$ROOT/docs/features"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT INT TERM
mkdir -p "$OUT"

command -v magick >/dev/null 2>&1 || { echo "needs ImageMagick 7 (magick)" >&2; exit 1; }

# frame <gif> <index> <png>: one frame of a recording, coalesced, scaled 2x
# (pixel-doubled, so the GIF's own palette survives and the file stays small)
frame() {
	rm -f "$TMP"/f*.png
	magick "$ROOT/$1" -coalesce "$TMP/f%03d.png"
	magick "$TMP/f$(printf %03d "$2").png" -filter Point -resize 200% "$3"
}

# shot <src> <out-name> x,y ... : copy with numbered markers, 1 upward
shot() {
	src=$1 name=$2
	shift 2
	n=0 draw=""
	for xy in "$@"; do
		n=$((n + 1))
		x=${xy%,*} y=${xy#*,}
		tx=$((x - 5)) ty=$((y + 6))
		[ "$n" -ge 10 ] && tx=$((x - 10))
		draw="$draw circle $x,$y $((x + 13)),$y"
		draw="$draw text $tx,$ty '$n'"
	done
	case $src in /*) ;; *) src="$ROOT/$src" ;; esac
	magick "$src" -strip \
		-fill '#ffd23f' -stroke '#111111' -strokewidth 3 \
		-font DejaVu-Sans-Bold -pointsize 17 \
		-draw "$(echo "$draw" | sed 's/ text [^ ]* [^ ]*//g')" \
		-stroke none -fill '#111111' -draw "$(echo "$draw" | sed 's/ circle [^ ]* [^ ]*//g')" \
		-define png:compression-level=9 "$OUT/$name.png"
	echo "  $name.png  ($(wc -c <"$OUT/$name.png") bytes)"
}

# the two recording stills
frame assets/landing-a3-manual.gif 143 "$TMP/burning.png"
frame assets/landing-a3-auto.gif   340 "$TMP/debrief.png"

G=docs/game/img
shot $G/menu.png                                 01-menu        285,241 285,341
shot $G/flight.png                               02-flight      222,14 440,345 812,22 200,645
shot $G/deorbit.png                              03-deorbit     18,80 160,316 836,88 248,597
shot $G/entry_auto.png                           04-entry       180,30 450,430 240,520 248,640 840,640 14,250
shot assets/gpis-instruments/sky-tab5.png        05-advisor     428,160 330,242 626,600 240,520
shot "$TMP/burning.png"                          06-burning     340,214 150,316 840,620 626,720 245,632
shot assets/gpis-instruments/entry-final.png     07-final       18,58 470,342 560,470 80,300
shot "$TMP/debrief.png"                          08-debrief     188,184 188,262 696,190 188,410
shot $G/concourse.png                            09-concourse   45,195 45,315 45,421 45,451 45,481 680,362
shot $G/trade.png                                10-trade       45,186 45,238 45,368 45,412 45,462
shot $G/missions.png                             11-missions    45,166 45,197 608,200
shot $G/bar.png                                  12-bar         45,193 45,230 45,278
shot $G/outfit.png                               13-outfit      45,190 45,286 45,370 45,455
shot $G/yard.png                                 14-yard        45,256 45,466 676,440
shot $G/journal.png                              15-journal     45,195 45,312 466,312 45,468 45,606
shot assets/governor-desk/desk-conex-day120.png  16-governor    45,166 45,250 45,345 350,200 45,620 555,742
shot $G/takeoff.png                              17-takeoff     455,440 80,480 952,150 335,98
