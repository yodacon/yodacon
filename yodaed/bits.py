"""yodaed bits — regenerate the control-bit registry's cross-references.

bits.yaml is hand-edited only for the doc line (and `external: true` on bits
the 1997 chain owns). `set_by` and `tested_by` are generated here, which is
exactly what makes the dead-end and never-set lints in `check` trustworthy.
"""
import json

from . import campaign as camp


def render(cpg):
    writers, testers = cpg.bit_writers(), cpg.bit_testers()
    names = sorted(set(writers) | set(testers) | set(cpg.bits))
    lines = [
        "# Control-bit registry. Hand-edit only `doc` (and `external: true`",
        "# for bits owned by the 1997 chain). `set_by`/`tested_by` are",
        "# generated — refresh with: python3 -m yodaed bits campaign",
        "",
    ]
    for name in names:
        entry = cpg.bits.get(name)
        entry = entry if isinstance(entry, dict) else {}
        lines.append(f"{name}:")
        if entry.get("external"):
            lines.append("  external: true")
        doc = entry.get("doc", "TODO — say what this bit means")
        lines.append(f"  doc: {json.dumps(doc, ensure_ascii=False)}")
        lines.append(f"  set_by: {json.dumps(sorted(set(writers.get(name, []))))}")
        lines.append(f"  tested_by: {json.dumps(sorted(set(testers.get(name, []))))}")
    return "\n".join(lines) + "\n"


def run(root, write=False):
    cpg = camp.Campaign(root)
    text = render(cpg)
    if write:
        (cpg.root / "bits.yaml").write_text(text, encoding="utf-8")
    return text
