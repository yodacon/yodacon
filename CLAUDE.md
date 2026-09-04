# Working in this repo

## The root is established — do not add to it

The repository root is settled. Its contents are:

    .gitignore  .gitmodules  .nojekyll  CNAME  LICENSE  Makefile
    README.md  backlog.md  index.html  setup-development.md

**New files go in an appropriate subdirectory, never at the root.** If nothing
existing fits, create a properly named directory and put the file inside it. The only
exception is a file that is only meaningful at the root — a tool's config that must
live there (`CLAUDE.md` itself), or a GitHub Pages control file.

Where things belong:

| Directory | Contents |
| --- | --- |
| `gonex/` | Submodule — the game (`yodacon/gonex`). The only checkout; there is no second one |
| `evutils/` | Byte-identical resource-fork dump/build tooling |
| `data/` | Gazetteer, universe map, and the exporters that feed `gonex/` |
| `docs/` | Project documentation |
| `docs/lab-reports/` | Dated engineering write-ups, `YYYY-MM-DD-<slug>.md` |
| `vendor/paulricheson/` | The 1997 ConEx plugin: `release/`, `extracted/`, `tools/` |
| `vendor/docs/` | Third-party reference material, mirrored |
| `vendor/konex/` | Submodule — the konex engine fork |
| `vendorignored/` | Large local archives, git-ignored in full |

## Building

The root `Makefile` is the center that compiles it all: `make all` round-trips
the 1997 fork (`verify`), runs every suite (`test`), and builds the game
(`gonex`). `make export` regenerates the game data from the extraction.

## Submodules: work in `gonex/` takes two commits

`gonex/` and `vendor/konex/` are separate repositories. A submodule records
**one commit**, not a branch, so changing the game means committing twice and
pushing twice:

    cd gonex && git commit && git push        # the game's own history
    cd .. && git add gonex && git commit      # move this repo's pointer
    git push

Do the second half or the work is pushed but a fresh clone still builds the
old game. `git submodule status` from the root prints what yodacon believes
the game is; a leading `+` means the pointer is stale.

Never work on the game anywhere but `gonex/`. A loose second clone of the same
repo used to sit at `~/code/gonex` and was deleted on 3 Sep 2026 — two
checkouts of one repository drift apart silently, and commits land in the tree
nobody builds.

## Never `git add -A`

This working tree carries a lot of untracked material that must not be committed,
including multi-gigabyte archives. Stage explicit paths:

    git add index.html docs/whatever.md      # yes
    git add -A                               # no

## Commit identity

Run a bare `git commit`. The global config is correct; do not pass `-c user.name` or
`-c user.email`.
