"""CLI: python3 -m yodaed <check|graph|bits|new> [campaign-dir] [args]

check                 print the open-questions queue; exit 1 if anything blocks
graph                 print the mission chain as Mermaid
bits                  print bits.yaml with regenerated cross-refs (--write saves)
new mission <slug>    scaffold a mission + its brief in the campaign dir
new text <relpath>    scaffold a missing prose file

`new` takes the campaign dir first when it is not ./campaign:
    python3 -m yodaed new campaign mission pellet-return
"""
import sys
from pathlib import Path

from . import bits, check, graph, new


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    flags = {a for a in argv if a.startswith("--")}
    if not args:
        print(__doc__.strip())
        return 2
    cmd = args[0]
    if cmd == "new":
        rest = list(args[1:])
        root = Path("campaign")
        if rest and rest[0] not in ("mission", "text"):
            root = Path(rest.pop(0))
        if len(rest) < 2:
            print(__doc__.strip())
            return 2
        if not (root / "missions").is_dir():
            print(f"yodaed: {root}/missions/ not found", file=sys.stderr)
            return 2
        kind, name = rest[0], rest[1]
        msg, code = (new.new_mission(root, name) if kind == "mission"
                     else new.new_text(root, name))
        print(msg)
        return code
    root = Path(args[1] if len(args) > 1 else "campaign")
    if not (root / "missions").is_dir():
        print(f"yodaed: {root}/missions/ not found", file=sys.stderr)
        return 2
    if cmd == "check":
        cpg, questions = check.run(root)
        print(check.render(cpg, questions))
        return 1 if any(q.level == check.BLOCK for q in questions) else 0
    if cmd == "graph":
        print(graph.run(root))
        return 0
    if cmd == "bits":
        text = bits.run(root, write="--write" in flags)
        if "--write" in flags:
            print(f"wrote {root}/bits.yaml")
        else:
            print(text, end="")
        return 0
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
