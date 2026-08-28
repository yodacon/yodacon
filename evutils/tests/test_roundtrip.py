"""The Phase 2 gate: unmodified ConEx 1.2 must round-trip byte-identically.

Uses the locally expanded forks in vendor/expanded/ when present; otherwise
expands vendor/paulricheson/release/ConEx 1.2.sit with unar (as CI does).
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from evutils import cli, rfork  # noqa: E402

FORK_NAMES = ["ConEx1.2.rsrc", "ConEx Readme 1.2.rsrc"]


def locate_forks():
    expanded = REPO / "vendor" / "expanded" / "ConEx 1.2"
    if all((expanded / n).exists() for n in FORK_NAMES):
        return expanded
    if shutil.which("unar") is None:
        raise unittest.SkipTest("no expanded forks and no unar to expand the .sit")
    tmp = Path(tempfile.mkdtemp(prefix="evutils-test-"))
    subprocess.run(
        ["unar", "-k", "visible", "-o", str(tmp),
         str(REPO / "vendor" / "paulricheson" / "release" / "ConEx 1.2.sit")],
        check=True, capture_output=True,
    )
    return tmp / "ConEx 1.2"


class RoundTrip(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        fork_dir = locate_forks()
        cls.forks = {n: rfork.unwrap_appledouble((fork_dir / n).read_bytes()) for n in FORK_NAMES}

    def test_parse_serialize_identity(self):
        for name, original in self.forks.items():
            with self.subTest(fork=name):
                self.assertEqual(rfork.serialize(rfork.parse(original)), original)

    def test_dump_build_identity(self):
        for name, original in self.forks.items():
            with self.subTest(fork=name):
                with tempfile.TemporaryDirectory() as td:
                    cli.dump(rfork.parse(original), Path(td))
                    self.assertEqual(cli.build(Path(td)), original)

    def test_dump_is_mostly_json(self):
        # The plugin's game data must come out as labeled JSON, not opaque bins.
        with tempfile.TemporaryDirectory() as td:
            counts = cli.dump(rfork.parse(self.forks["ConEx1.2.rsrc"]), Path(td))
        self.assertGreater(counts["json"], 300)


if __name__ == "__main__":
    unittest.main()
