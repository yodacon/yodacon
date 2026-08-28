# ConEx — Paul Richeson, 1997–1999

Everything of mine that survived from the original *Escape Velocity* plugin, kept
together: the shipped release, and the resources recovered from it.

The Yodacon was published into this archive. That is the reason the rest of this
project exists.

## `release/`

The plugin as it shipped, byte-for-byte, in the two forms it was mirrored in.
Nothing in this directory is ever edited.

| File | Format |
| --- | --- |
| `ConEx 1.2.sit` | StuffIt 5, "Arsenic" arithmetic coder |
| `792_ConEx12.sit.hqx` | BinHex 4.0 wrapping the same `.sit` |

Both mirrored 2026-08-27 from the Cythera Guides EV add-on archive. SHA-256 digests
for both are recorded in `PROVENANCE.md`.

## `extracted/`

The readable, diffable, version-controlled form of the same data — the resource fork
split into individual files, art decoded to PNG, prose decoded to UTF-8.

| Directory | Contents |
| --- | --- |
| `ConEx1.2/` | Resource fork of the plugin, `<type>/<id>[_<name>].bin` |
| `ConEx-Readme-1.2/` | Resource fork of the readme document |
| `png/` | Decoded PICT images |
| `sprites/` | Decoded spïn sheets, RGBA with the mask applied |
| `text/` | Decoded text resources, UTF-8 |

## `tools/`

The extraction and decoding scripts, kept beside the data they operate on. Each takes
its paths as arguments and derives output locations from the input's parent, so they
work from anywhere:

| Script | Purpose |
| --- | --- |
| `rsrc_extract.py` | Split a resource fork into `<type>/<id>[_<name>].bin` |
| `convert_all.py` | Batch-decode PICTs to PNG, spïn sheets to RGBA, text to UTF-8 |
| `pict_decode.py` | Decode a single PICT to an image |
| `tmpl_dump.py` | Dump a resource against its `TMPL` definition |

Regenerating `extracted/` from `release/`:

```sh
cd vendor/paulricheson
python3 tools/rsrc_extract.py <resource-fork> extracted/ConEx1.2
python3 tools/convert_all.py extracted/ConEx1.2 extracted/ConEx-Readme-1.2
```

## `PROVENANCE.md`

Every date and hash the archive still carries, recorded before anything else touched
it — source digests, member timestamps inside the `.sit`, and the HFS creation dates
preserved through extraction. The plugin's files date to **9 November 1997**.

Extraction method and findings are written up in
[`docs/lab-reports/2026-08-27-conex-resource-extraction.md`](../../docs/lab-reports/2026-08-27-conex-resource-extraction.md).
