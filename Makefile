# Yodacon — the center that compiles it all.
#
# The 1997 plugin is the source of truth; everything downstream is derived:
#
#   vendor/paulricheson/release/*.sit          (byte-exact 1997 releases)
#     └─ vendor/expanded/                      (unar working copies, ignored)
#         └─ vendor/paulricheson/extracted/    (committed resource tree)
#             ├─ data/gazetteer.yaml + universe-map.svg
#             └─ gonex/assets/data/…           (galaxy, missions, ships, land art)
#                 └─ the game
#
# `make all` proves the chain: round-trips the fork, regenerates the data,
# and builds + tests the game in the gonex/ submodule.

PY      ?= python3
GONEX   ?= $(firstword $(wildcard gonex) $(HOME)/code/Gonex)
EXPAND   = vendor/expanded
FORK     = $(EXPAND)/ConEx 1.2/ConEx1.2.rsrc

.PHONY: all test check verify expand extract gazetteer export gonex run clean-derived

all: verify test gonex

## expand: unpack the 1997 release archives into vendor/expanded (local only)
expand:
	@test -f "$(FORK)" || unar -q -k visible -o "$(EXPAND)/" "vendor/paulricheson/release/ConEx 1.2.sit"
	@test -f "$(FORK)" && echo "expanded: $(FORK)"

## verify: prove the resource fork round-trips byte-identically (evutils)
verify: expand
	$(PY) -m evutils verify "$(FORK)"

## test: evutils + yodaed suites + the full gonex suite (reentry gates included)
test:
	$(PY) -m unittest discover -q -s evutils/tests
	$(PY) -m unittest discover -q -s yodaed/tests
	cd "$(GONEX)" && go test ./...

## check: the mission editor's open-questions queue over campaign/
check:
	$(PY) -m yodaed check campaign

## extract: regenerate the committed resource tree from the release
extract: expand
	cd vendor/paulricheson && $(PY) tools/rsrc_extract.py "../../$(FORK)" extracted/ConEx1.2

## gazetteer: rebuild data/gazetteer.yaml and the SVG chart
gazetteer: expand
	$(PY) data/build_gazetteer.py
	$(PY) data/build_map.py

## export: push the joined universe, missions, ships and landing art into gonex
export: expand
	GONEX_DIR="$(GONEX)" $(PY) data/export_gonex.py
	GONEX_DIR="$(GONEX)" $(PY) data/export_ships.py

## gonex: build the game from the submodule (or ~/code/Gonex checkout)
gonex:
	cd "$(GONEX)" && go build -o gonex-bin ./cmd/gonex
	@echo "built: $(GONEX)/gonex-bin"

## run: fly it
run: gonex
	cd "$(GONEX)" && ./gonex-bin

clean-derived:
	rm -f "$(GONEX)/gonex-bin"
