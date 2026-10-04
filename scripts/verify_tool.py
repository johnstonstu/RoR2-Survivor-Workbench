"""Run bounded local checks and save a new private verification receipt."""

import hashlib
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from ror2_workbench import __version__
from ror2_workbench.core import json_bytes, scan, write_new


def verify():
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    evidence = root / "local" / ("verification-" + stamp)
    evidence.mkdir(parents=True, exist_ok=False)
    checks = []
    for name, args in (("unit", ["-m", "unittest", "discover", "-s", "tests", "-v"]), ("demo", ["scripts/demo.py"])):
        started = time.monotonic()
        result = subprocess.run([sys.executable, *args], cwd=root, capture_output=True, timeout=60)
        elapsed = time.monotonic() - started
        log = result.stdout + result.stderr
        write_new(evidence / (name + ".log"), log)
        checks.append({"id":name, "level":"offline", "exit_code":result.returncode,
                       "elapsed_seconds":round(elapsed, 3),
                       "status":"passed" if result.returncode == 0 else "failed",
                       "log":name + ".log", "log_sha256":hashlib.sha256(log).hexdigest()})
    inputs = {}
    directories = {"ror2_workbench", "docs", "scripts", "tests", ".github", "examples"}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in ("__pycache__", "local", "bin", "obj") for part in path.relative_to(root).parts):
            continue
        relative = path.relative_to(root)
        if len(relative.parts) > 1 and relative.parts[0] not in directories:
            continue
        data = path.read_bytes()
        scan(data, relative.as_posix())
        inputs[relative.as_posix()] = hashlib.sha256(data).hexdigest()
    receipt = {"schema":1, "tool":"ror2-agent-workbench", "tool_version":__version__,
               "operation":"tool-verification", "created_utc":datetime.now(timezone.utc).isoformat(),
               "tool_versions":{"python":platform.python_version()}, "platform":platform.system(),
               "input_hashes":inputs, "checks":checks,
               "limitations":["See full unit log for skipped host-dependent cases.", "Synthetic offline checks only; no game/Unity/Wwise/controller/multiplayer/media acceptance.", "No external CI execution or publication occurred."]}
    write_new(evidence / "receipt.json", json_bytes(receipt))
    print(json.dumps({"all_checks_passed":all(c["exit_code"] == 0 for c in checks), "receipt":(evidence / "receipt.json").relative_to(root).as_posix()}, indent=2))
    return 0 if all(c["exit_code"] == 0 for c in checks) else 1


if __name__ == "__main__":
    sys.exit(verify())
