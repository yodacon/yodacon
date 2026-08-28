"""evutils command line: dump a resource fork to an editable tree, build it back.

    python3 -m evutils dump  <fork-or-appledouble> <out-dir>
    python3 -m evutils build <dump-dir> <out-fork>
    python3 -m evutils verify <fork-or-appledouble>

Game resources whose type has a TMPL in the fork (shïp, mïsn, sÿst, ...)
are dumped as labeled JSON; everything else as raw .bin. Every JSON dump
is verified to re-encode byte-identically before it is written, so a
clean `dump` + unedited `build` reproduces the fork exactly.
"""
import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from struct import error as struct_error

from . import rfork, tmpl


def sanitize(text: str) -> str:
    keep = [ch if ch.isalnum() or ch in " ._-#'" else "_" for ch in text]
    return "".join(keep).strip().rstrip(".") or "_"


def load_fork(path: Path) -> rfork.Fork:
    return rfork.parse(rfork.unwrap_appledouble(path.read_bytes()))


def dump(fork: rfork.Fork, out_dir: Path) -> dict:
    templates = tmpl.templates_in(fork)
    manifest = {
        "format": "evutils-dump-1",
        "reserved": fork.reserved.hex(),
        "map_header": fork.map_header.hex(),
        "type_order": fork.type_order,
        "resources": [],
    }
    counts = {"json": 0, "bin": 0}
    for res in fork.resources:
        stem = f"{res.rid}" + (f"_{sanitize(res.name)}" if res.name else "")
        entry = {
            "type": res.rtype,
            "id": res.rid,
            "name": res.name,
            "attrs": res.attrs,
            "handle": res.handle.hex(),
            "data_order": res.data_order,
            "name_order": res.name_order if res.name is not None else None,
        }
        fields = None
        if res.rtype in templates:
            try:
                decoded = tmpl.decode(templates[res.rtype], res.data)
                if tmpl.encode(templates[res.rtype], decoded) == res.data:
                    fields = decoded
            except (ValueError, IndexError, struct_error):
                fields = None
        tdir = out_dir / sanitize(res.rtype)
        tdir.mkdir(parents=True, exist_ok=True)
        if fields is not None:
            entry["file"] = f"{sanitize(res.rtype)}/{stem}.json"
            (tdir / f"{stem}.json").write_text(
                json.dumps({"fields": fields}, ensure_ascii=False, indent=1) + "\n",
                encoding="utf-8",
            )
            counts["json"] += 1
        else:
            entry["file"] = f"{sanitize(res.rtype)}/{stem}.bin"
            (tdir / f"{stem}.bin").write_bytes(res.data)
            counts["bin"] += 1
        manifest["resources"].append(entry)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
    )
    return counts


def build(dump_dir: Path) -> bytes:
    manifest = json.loads((dump_dir / "manifest.json").read_text(encoding="utf-8"))
    if manifest.get("format") != "evutils-dump-1":
        raise SystemExit(f"{dump_dir}: not an evutils dump")
    fork = rfork.Fork(
        reserved=bytes.fromhex(manifest["reserved"]),
        map_header=bytes.fromhex(manifest["map_header"]),
        type_order=manifest["type_order"],
    )
    # TMPLs load first: JSON resources re-encode through them.
    templates = {}
    for entry in manifest["resources"]:
        if entry["type"] == "TMPL" and entry["name"]:
            templates[entry["name"]] = tmpl.parse_tmpl(
                (dump_dir / entry["file"]).read_bytes()
            )
    for entry in manifest["resources"]:
        path = dump_dir / entry["file"]
        if entry["file"].endswith(".json"):
            decoded = json.loads(path.read_text(encoding="utf-8"))["fields"]
            data = tmpl.encode(templates[entry["type"]], decoded)
        else:
            data = path.read_bytes()
        fork.resources.append(
            rfork.Resource(
                rtype=entry["type"],
                rid=entry["id"],
                name=entry["name"],
                attrs=entry["attrs"],
                handle=bytes.fromhex(entry["handle"]),
                data=data,
                data_order=entry["data_order"],
                name_order=entry["name_order"] or 0,
            )
        )
    return rfork.serialize(fork)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="evutils", description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("dump", help="resource fork -> editable JSON/bin tree")
    p.add_argument("fork", type=Path)
    p.add_argument("out_dir", type=Path)
    p = sub.add_parser("build", help="dump tree -> resource fork")
    p.add_argument("dump_dir", type=Path)
    p.add_argument("out_fork", type=Path)
    p = sub.add_parser("verify", help="prove dump+build round-trips a fork byte-identically")
    p.add_argument("fork", type=Path)
    args = parser.parse_args(argv)

    if args.cmd == "dump":
        counts = dump(load_fork(args.fork), args.out_dir)
        print(f"dumped {counts['json']} resources as JSON, {counts['bin']} as raw bin")
    elif args.cmd == "build":
        data = build(args.dump_dir)
        args.out_fork.write_bytes(data)
        print(f"wrote {len(data)} bytes, sha256 {hashlib.sha256(data).hexdigest()}")
    elif args.cmd == "verify":
        original = rfork.unwrap_appledouble(args.fork.read_bytes())
        if rfork.serialize(rfork.parse(original)) != original:
            sys.exit("FAIL: parse+serialize does not reproduce the fork")
        with tempfile.TemporaryDirectory() as td:
            dump(rfork.parse(original), Path(td))
            rebuilt = build(Path(td))
        if rebuilt != original:
            sys.exit("FAIL: dump+build does not reproduce the fork")
        print(
            f"OK: {args.fork.name} round-trips byte-identically "
            f"({len(original)} bytes, sha256 {hashlib.sha256(original).hexdigest()})"
        )


if __name__ == "__main__":
    main()
