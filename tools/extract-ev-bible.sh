#!/bin/sh
# Extract the EV Bible from its Cocoa app bundle into plain text.
#
# "EV Bible.app" is a PPC-era Mac application, but it does not need to RUN:
# the 44KB executable is only a document viewer, and every topic is stored as
# an ordinary RTF file inside Contents/Resources. This script converts those
# to UTF-8 text so the reference is greppable, diffable, and usable on any
# machine — no PowerPC, no Rosetta, no emulator.
#
# Regenerates vendor/ev-bible-extracted/ from vendor/EV Bible.app.
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd)
APP="$ROOT/vendor/EV Bible.app/Contents/Resources"
OUT="$ROOT/vendor/ev-bible-extracted"

[ -d "$APP" ] || { echo "missing: $APP" >&2; exit 1; }
command -v textutil >/dev/null || { echo "needs macOS textutil" >&2; exit 1; }

for SET in EVO EVN; do
  [ -d "$APP/$SET Topics" ] || continue
  mkdir -p "$OUT/$SET"
  for f in "$APP/$SET Topics"/*.rtf; do
    textutil -convert txt -stdout "$f" > "$OUT/$SET/$(basename "$f" .rtf).txt"
  done
  # single concatenated edition file
  { echo "EV Bible — $SET edition"
    echo "Extracted from 'EV Bible.app' by tools/extract-ev-bible.sh"
    echo
    for t in "$OUT/$SET"/*.txt; do
      echo; echo "================================================================"
      echo "  $(basename "$t" .txt)"
      echo "================================================================"; echo
      cat "$t"
    done
  } > "$OUT/EV-Bible-$SET.txt"
  echo "$SET: $(ls "$OUT/$SET" | wc -l | tr -d ' ') topics -> $OUT/EV-Bible-$SET.txt"
done
