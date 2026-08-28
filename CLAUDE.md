# Working in this repo

## The root is established — do not add to it

The repository root is settled. Its contents are:

    .gitignore  .gitmodules  .nojekyll  CNAME  LICENSE
    README.md  backlog.md  index.html  setup-development.md

**New files go in an appropriate subdirectory, never at the root.** If nothing
existing fits, create a properly named directory and put the file inside it. The only
exception is a file that is only meaningful at the root — a tool's config that must
live there (`CLAUDE.md` itself), or a GitHub Pages control file.

Where things belong:

| Directory | Contents |
| --- | --- |
| `docs/` | Project documentation |
| `docs/lab-reports/` | Dated engineering write-ups, `YYYY-MM-DD-<slug>.md` |
| `vendor/paulricheson/` | The 1997 ConEx plugin: `release/`, `extracted/`, `tools/` |
| `vendor/docs/` | Third-party reference material, mirrored |
| `vendor/konex/` | Submodule — the konex engine fork |
| `vendorignored/` | Large local archives, git-ignored in full |

## Never `git add -A`

This working tree carries a lot of untracked material that must not be committed,
including multi-gigabyte archives. Stage explicit paths:

    git add index.html docs/whatever.md      # yes
    git add -A                               # no

## Commit identity

Run a bare `git commit`. The global config is correct; do not pass `-c user.name` or
`-c user.email`.
