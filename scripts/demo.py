"""Synthetic, disposable end-to-end example. No game assets or runnable mod."""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ror2_workbench.__main__ import main
from ror2_workbench.core import json_bytes


def demo():
    with tempfile.TemporaryDirectory(prefix="ror2-workbench-demo-") as temporary:
        root = Path(temporary) / "fixture"
        commands = [["init", str(root), "--name", "WorkbenchFixture"]]
        for command in commands:
            assert main(command) == 0
        doc = json.loads((root / "workbench.json").read_text())
        doc["mode"] = "fixture"
        payload = root / "artifacts" / "fixture.txt"
        payload.parent.mkdir()
        payload.write_text("Synthetic package payload; not a BepInEx plugin.\n", encoding="utf-8")
        doc["files"].append({"source":"artifacts/fixture.txt", "destination":"plugins/WorkbenchFixture/fixture.txt", "sha256":None, "license":"MIT", "provenance":"Original synthetic test data"})
        (root / "workbench.json").write_bytes(json_bytes(doc))
        assert main(["pin", "--root", str(root)]) == 0
        (root / "workbench.json").write_bytes((root / "local/workbench.pinned.json").read_bytes())
        assert main(["check", "--root", str(root), "--release"]) == 0
        assert main(["package", "--root", str(root), "--output", "dist/fixture.zip", "--receipt", "evidence/package.json"]) == 0
        assert main(["verify", "--root", str(root), "dist/fixture.zip", "--receipt", "evidence/verify.json"]) == 0
        print("DEMO PASSED: exact pinned ZIP bytes verified; synthetic fixture deleted on exit.")


if __name__ == "__main__":
    demo()
