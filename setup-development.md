# Development Setup

Working notes for building **konex** on macOS and porting it to Go.
Started 27 Aug 2026.

## What konex is

[`jbussdieker/konex`](https://github.com/jbussdieker/konex) — Joshua B. Bussdieker's
2005 open-source Escape-Velocity-alike. ~10,100 lines of **C++** (not C, despite the
KDevelop project shape), fixed-function OpenGL 1.x, X11/GLX on Linux and Win32 on
Windows. Build system is 2005-era autotools (`configure.in`, `Makefile.am`) plus a
KDevelop project file and a Visual C++ 6 `.dsp`.

The repo also carries checked-in build droppings — `Release/*.obj`, `dist/konex.exe`,
`konex.ncb`, CVS directories — about 40 MB. Don't clean those up in the fork unless we
decide to; they're history.

### License — read this before writing any Go

konex is **GPL v2** (`COPYING`). The Yodacon site/repo is MIT. A fork is a derivative
work and stays GPL v2, and **a Go port that is a translation of this source is also a
derivative work** — it does not launder the license. Options, to decide before the port
goes far:

1. Keep the Go engine GPL v2 in its own repo, MIT only for our original assets/lore.
2. Ask Joshua Bussdieker for a relicense/dual-license.
3. Clean-room: write Go from the *design* without copying structure — expensive, and
   hard to prove.

Nothing here is blocked on this yet, but it decides what the Go repo's LICENSE says.

## Required software (macOS, Apple Silicon)

All present or installed on 27 Aug 2026:

| Tool | Version | How |
| --- | --- | --- |
| Xcode Command Line Tools | `/Library/Developer/CommandLineTools` | `xcode-select --install` |
| Homebrew | 6.0.19 | already installed |
| CMake | 4.4.3 | `brew install cmake` |
| SDL2 | via `sdl2-compat` 2.32.70 | `brew install sdl2` |
| Go | 1.27.0 | `brew install go` |

**Not needed:** X11/XQuartz, OpenAL, autotools. The sound system is already commented
out upstream (`snd_main.h` is `//#include`d in `defs.h` and `snd_main.cpp` is absent
from `Makefile.am`), so the OpenAL dependency is dead. OpenGL comes from the macOS
`OpenGL.framework` — deprecated by Apple but fully functional; we get a 2.1
compatibility context, which is what the fixed-function code needs.

## The macOS port

Autotools was abandoned in favour of a `CMakeLists.txt` that selects sources and
libraries per platform. Changes made to get it building and running:

- **`src/defs.h`** — the file hard-coded `#define LINUX` for anything that wasn't
  WIN32. Added a `MACOS` branch: SDL2 + `OpenGL/gl.h` + `OpenGL/glu.h` instead of
  `X11/Xlib.h`, `GL/glx.h`, and the `AL/*` headers.
- **`src/vid_sdl.cpp` / `.h`** — upstream had an SDL backend, but it was written for
  **SDL 1.2** and commented out of the build (`SDL_SetVideoMode`, `SDL_GetVideoInfo`,
  `SDL_ACTIVEEVENT`, `SDL_GL_SwapBuffers` — all removed in SDL2). Rewritten against
  SDL2: `SDL_CreateWindow` + `SDL_GL_CreateContext` with a compatibility profile,
  SDL2 event loop, plus `vidsdl_SetMode` and `vidsdl_CreateFont`, which the X11
  backend had but the SDL one never did.
- **`src/vid_main.cpp` / `.h`, `src/sys_main.cpp`** — route the `MACOS` build to the
  `vidsdl_*` entry points instead of `vidl_*`.
- **`src/view.cpp`** — `if (viewPlayer > 0)` on a pointer; clang rejects the ordered
  comparison. Now `!= NULL`.
- **`CMakeLists.txt`** — new. Also stages `dist/` next to the built binary, because
  the engine resolves asset paths relative to the executable.

26 of the 30 translation units compiled clean under clang with no changes at all,
which says good things about how portable the original actually is.

### Known gap

`vidsdl_CreateFont` is a **stub**. The X11 backend built its 256 glyph display lists
with `glXUseXFont`, which has no macOS equivalent. The port allocates the display
lists and leaves them empty with a correct raster advance, so the engine links and
runs — but all in-game text (console, HUD, menus) renders as nothing. First real task
after the build: upload a bitmap font and fill those lists.

Also: keyboard **text** input is Linux-only. `in_main.cpp` maps raw X11 keycodes in a
`#ifdef LINUX` switch; SDL2 gives scancodes, so that table is wrong for macOS and is
left disabled. Movement keys work via `sysKeys[]`; typing in the console does not.

Minor: the patched files were rewritten with LF endings, so a few diffs are larger
than the logical change.

## Build and run

A convenience `Makefile` wraps CMake, so the entry point is just `make`:

```sh
git submodule update --init vendor/konex && cd vendor/konex
make deps     # brew install cmake sdl2 (one time)
make check    # report what the build needs and whether it is present
make          # configure + compile
make run      # launch from the staged asset directory
```

Other targets: `make release` (optimized, into `build-release/`), `make rebuild`,
`make clean`, `make distclean`, `make help`.

The upstream Autotools files (`Makefile.cvs`, `Makefile.am`, `configure.in`) are
left in place for the historical record but are not used. Don't run `./configure`
in this tree — it would generate a root `Makefile` and clobber ours.

Underneath, it is a plain CMake build if you prefer to drive it directly:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build -j8
cd build/bin && ./konex
```

### Status — it runs

First successful macOS run, 27 Aug 2026:

```
* Welcome to Konex...
CONFIG: Configuration loaded sucessfully
TIMER: Time system is operational.
VID: Video system is operational.
 - Vendor (Apple)
 - Version (2.1 Metal - 90.5)
 - Renderer (Apple M1)
IN: Input system is operational.
* Engine initialization complete...
STARS: Created 1000 stars...
PLANETS: Loaded 18 planets...
EXPLOSIONS: Loaded 17 explosions...
SHIPS: Loaded 12 ships.
* Game initialization complete...
```

Five `VID: Error loading ./data/planets/1[3-7]/view.tga` messages are **upstream asset
gaps**, not a porting failure — those files aren't in the repo.

## Repository layout

Plan: fork `jbussdieker/konex`, then carry the fork in this repo as a git submodule so
the site repo and the engine version stay pinned together.

```sh
gh repo fork jbussdieker/konex --clone=false
git submodule add -b macos-port git@github.com:vonglurt/konex.git vendor/konex
```

**Decided 27 Aug 2026:** the fork lives under the personal account as
[`vonglurt/konex`](https://github.com/vonglurt/konex), on branch `macos-port`. There is
no GitHub organization yet; forming one is a good idea and the repo transfers in one
step when it exists. It is wired into this repo as a submodule:

```sh
git submodule update --init vendor/konex
cd vendor/konex && make
```

`vendor/` also holds unrelated, untracked reference material — `vendor/docs` alone is
about 2.4 GB. Do not run a bare `git add -A` in this repo.

## Go port

C++-first was the chosen path: get the original building and running on macOS (done),
then port module by module with a runnable reference to diff behaviour against.

Sensible order, smallest and least entangled first:

1. `xml.cpp` + tinyxml → `encoding/xml`. Pure data, no graphics. Good first slice.
2. `config.cpp`, `ships.cpp`, `planets.cpp`, `item.cpp` — data loading off the XML.
3. `vector.h`, `tm_*`, `entity.cpp` — math and the entity/timer core.
4. `ai.cpp`, `spawn.cpp`, `missile.cpp`, `explosion.cpp`, `player.cpp` — simulation.
5. Rendering last. This is the real rewrite: the engine is fixed-function GL with
   display lists, and none of that survives the move.

Rendering library, to decide at step 5:

- **[ebiten](https://github.com/hajimehoshi/ebiten)** — pure Go, no cgo, 2D sprite/
  texture model that matches what konex actually draws. Cross-compiles cleanly.
  Recommended.
- **[go-sdl2](https://github.com/veandco/go-sdl2)** — cgo bindings, closest 1:1 to the
  existing SDL2 backend, keeps the port mechanical. Costs cgo and a real SDL2 dependency.

Everything above the renderer is plain Go and testable without either.
