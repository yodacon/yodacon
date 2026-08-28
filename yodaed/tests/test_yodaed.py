"""yodaed suite: the yamlite subset, the question queue, chain lints, and
the shipped starter campaign staying buildable."""
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from yodaed import bits, campaign, check, graph, yamlite  # noqa: E402

WORLD = campaign.load_world(REPO)


class TestYamlite(unittest.TestCase):
    def test_scalars_and_nesting(self):
        doc = yamlite.loads(
            'a: 1\n'
            'b: "two # not a comment"\n'
            'c:  # trailing comment\n'
            '  d: [1, -2, "x"]\n'
            '  e: {k: v, n: 3}\n'
            'f: true\n'
            'lst:\n'
            '  - one\n'
            '  - 2\n')
        self.assertEqual(doc["a"], 1)
        self.assertEqual(doc["b"], "two # not a comment")
        self.assertEqual(doc["c"]["d"], [1, -2, "x"])
        self.assertEqual(doc["c"]["e"], {"k": "v", "n": 3})
        self.assertIs(doc["f"], True)
        self.assertEqual(doc["lst"], ["one", 2])

    def test_duplicate_key_rejected(self):
        with self.assertRaises(yamlite.YamliteError):
            yamlite.loads("a: 1\na: 2\n")

    def test_reads_the_real_gazetteer(self):
        gaz = yamlite.load(REPO / "data" / "gazetteer.yaml")
        self.assertEqual(gaz["systems"][129]["name"], "Sol")
        self.assertIn(128, gaz["stellars"])  # Earth


def _tmp_campaign(missions, texts=None):
    root = Path(tempfile.mkdtemp())
    (root / "missions").mkdir()
    for slug, body in missions.items():
        (root / "missions" / f"{slug}.yaml").write_text(body, encoding="utf-8")
    for rel, body in (texts or {}).items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body, encoding="utf-8")
    return root


def _questions(root):
    _, qs = check.run(root, WORLD)
    return qs


def _blocking(qs):
    return [q for q in qs if q.level == check.BLOCK]


class TestCheck(unittest.TestCase):
    def test_unknown_stellar_blocks(self):
        qs = _questions(_tmp_campaign({"m": "mission: M\navailable:\n  at: Nowhere\n"}))
        self.assertTrue(any("no stellar by that name" in q.text
                            for q in _blocking(qs)))

    def test_gate_bit_never_set_blocks(self):
        qs = _questions(_tmp_campaign({
            "m": "mission: M\navailable:\n  at: Earth\n  when:\n    set: ghost\n"}))
        self.assertTrue(any("never set" in q.text for q in _blocking(qs)))

    def test_external_bit_is_the_escape_hatch(self):
        root = _tmp_campaign({
            "m": "mission: M\navailable:\n  at: Earth\n  when:\n    set: legacy\n"})
        (root / "bits.yaml").write_text(
            'legacy:\n  external: true\n  doc: "owned by the 1997 chain"\n',
            encoding="utf-8")
        self.assertFalse(_blocking(_questions(root)))

    def test_same_place_cargo_blocks(self):
        qs = _questions(_tmp_campaign({
            "m": "mission: M\navailable:\n  at: Earth\n"
                 "cargo: {type: Metal, qty: 5, pickup: at_travel, dropoff: at_travel}\n"}))
        self.assertTrue(any("same place" in q.text for q in _blocking(qs)))

    def test_success_holds_two_bits_at_most(self):
        qs = _questions(_tmp_campaign({
            "m": "mission: M\navailable:\n  at: Earth\n"
                 "on:\n  success: [set a, set b, set c]\n"}))
        self.assertTrue(any("holds 2" in q.text for q in _blocking(qs)))

    def test_unknown_wildcard_blocks(self):
        qs = _questions(_tmp_campaign(
            {"m": "mission: M\navailable:\n  at: Earth\n"
                  "text:\n  brief: texts/m/brief.md\n"},
            {"texts/m/brief.md": "Deliver to <DST> for <PAY>.\n"}))
        self.assertTrue(any("<PAY>" in q.text for q in _blocking(qs)))

    def test_missing_prose_blocks(self):
        qs = _questions(_tmp_campaign(
            {"m": "mission: M\navailable:\n  at: Earth\n"
                  "text:\n  brief: texts/m/brief.md\n"}))
        self.assertTrue(any("not written" in q.text for q in _blocking(qs)))

    def test_unreachable_chain_warns(self):
        qs = _questions(_tmp_campaign({
            "a": "mission: A\navailable:\n  at: Earth\n  when:\n    set: x\n"
                 "on:\n  success: set y\n",
            "b": "mission: B\navailable:\n  at: Earth\n  when:\n    set: y\n"
                 "on:\n  success: set x\n"}))
        self.assertTrue(any("no path from a game start" in q.text for q in qs))


class TestStarterCampaign(unittest.TestCase):
    def test_buildable_with_one_loose_thread(self):
        cpg, qs = check.run(REPO / "campaign", WORLD)
        self.assertEqual(len(cpg.missions), 3)
        self.assertFalse(_blocking(qs))
        warns = [q for q in qs if q.level == check.WARN]
        self.assertEqual(len(warns), 1)
        self.assertIn("exeon_lane_open", warns[0].field)

    def test_bits_registry_is_current(self):
        cpg = campaign.Campaign(REPO / "campaign")
        on_disk = (REPO / "campaign" / "bits.yaml").read_text(encoding="utf-8")
        self.assertEqual(bits.render(cpg), on_disk)

    def test_graph_names_the_chain(self):
        text = graph.run(REPO / "campaign")
        self.assertIn("pellet_contract -- pellet_contract_signed --> pellet_run",
                      text)
        self.assertIn(":::deadend", text)


if __name__ == "__main__":
    unittest.main()
