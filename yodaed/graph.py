"""yodaed graph — the mission chain as Mermaid, readable at a glance.

Nodes are missions; an edge runs from the mission that writes a bit to each
mission gated on it, labeled with the bit. Dead-end bits and external gates
show as standalone bit nodes so loose threads are visible on the chart.
"""
from . import campaign as camp


def _nid(slug):
    return slug.replace("-", "_")


def render(cpg):
    writers, testers = cpg.bit_writers(), cpg.bit_testers()
    external = {name for name, entry in cpg.bits.items()
                if isinstance(entry, dict) and entry.get("external")}
    lines = ["flowchart LR"]
    for m in cpg.missions:
        lines.append(f'    {_nid(m.slug)}["{m.name}"]')
    for bit, users in sorted(testers.items()):
        srcs = writers.get(bit)
        if srcs:
            for src in srcs:
                for user in users:
                    lines.append(f"    {_nid(src)} -- {bit} --> {_nid(user)}")
        else:
            style = ":::external" if bit in external else ":::missing"
            for user in users:
                lines.append(f"    bit_{_nid(bit)}([{bit}]){style} --> {_nid(user)}")
    for bit, srcs in sorted(writers.items()):
        if bit not in testers:
            for src in srcs:
                lines.append(f"    {_nid(src)} -. {bit} .-> "
                             f"bit_{_nid(bit)}([{bit}]):::deadend")
    lines.append("    classDef external stroke-dasharray: 4 3")
    lines.append("    classDef missing stroke:#f66")
    lines.append("    classDef deadend stroke-dasharray: 2 2")
    return "\n".join(lines)


def run(root):
    return render(camp.Campaign(root))
