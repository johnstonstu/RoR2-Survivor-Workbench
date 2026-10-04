"""A receipt records a reviewed result, without elevating its evidence level."""

import subprocess
from . import __version__
from datetime import datetime, timezone
from .core import keys, require, string, local, parse_json, digest, file_bytes, snapshot, scan
from .contract import load, task


def git_identity(root):
    # Git observation must not refresh the index or execute a configured monitor.
    prefix = ["git", "--no-optional-locks", "-c", "core.fsmonitor=false", "-c", "core.untrackedCache=false"]
    try:
        top = subprocess.run([*prefix, "rev-parse", "--show-toplevel"], cwd=root, capture_output=True, text=True, timeout=10)
        from pathlib import Path
        if top.returncode or Path(top.stdout.strip()).resolve() != Path(root).resolve():
            return {"commit": None, "dirty": None, "status": "unavailable"}
        sha = subprocess.run([*prefix, "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, timeout=10)
        dirty = subprocess.run([*prefix, "status", "--porcelain"], cwd=root, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return {"commit": None, "dirty": None, "status": "unavailable"}
    if sha.returncode or dirty.returncode:
        return {"commit": None, "dirty": None, "status": "unavailable"}
    return {"commit": sha.stdout.strip(), "dirty": bool(dirty.stdout.strip()), "status": "observed"}


def identity(root, doc):
    names = ["workbench.json", *doc["inputs"], *doc["package"].values(), *doc["coordination"].values(),
             *(f["source"] for f in doc["files"])]
    for instruction in ("AGENTS.md", "CLAUDE.md"):
        if (root / instruction).exists():
            names.append(instruction)
    return snapshot(root, names)


def base_receipt(root, operation, doc):
    return {"schema": 1, "tool": "ror2-agent-workbench", "tool_version": __version__,
            "operation": operation, "created_utc": datetime.now(timezone.utc).isoformat(),
            "mode": doc["mode"], "project": doc["identity"], "git": git_identity(root),
            "input_hashes": identity(root, doc),
            "runtime_compatibility": "unverified", "uploaded": False}


def acceptance_coverage(current_task, checks):
    """Compare one validated result with named gates; never merge or approve them."""
    reported = {check["id"]: check for check in checks}
    required = {gate["id"]: gate for gate in current_task["acceptance"]}
    missing, mismatches, not_passed, matched = [], [], [], []
    for name, gate in required.items():
        check = reported.get(name)
        if check is None:
            missing.append(name)
        elif check["level"] != gate["level"]:
            mismatches.append({"id": name, "expected": gate["level"], "reported": check["level"]})
        elif check["status"] != "passed":
            not_passed.append(name)
        else:
            matched.append(name)
    return {"required_ids": list(required), "matched_passed": matched,
            "missing": missing, "level_mismatches": mismatches, "not_passed": not_passed,
            "unrelated_ids": [name for name in reported if name not in required],
            "all_required_reported_passed": len(matched) == len(required),
            "scope": "this result only; operator attestations; no task update or merged evidence"}


def record(root, input_name):
    doc = load(root)
    current_task = task(root, doc)
    raw = file_bytes(local(root, input_name))
    scan(raw, input_name)
    result = parse_json(raw)
    keys(result, ("schema", "task_id", "input_hashes", "tool_versions", "checks", "limitations"))
    require(type(result["schema"]) is int and result["schema"] == 1, "unsupported result schema")
    require(result["task_id"] == current_task["id"], "result belongs to a different current task")
    require(result["input_hashes"] == identity(root, doc), "result input identity is stale/incomplete; capture identity before running checks")
    require(isinstance(result["tool_versions"], dict) and bool(result["tool_versions"]), "record actual tool versions")
    for name, version in result["tool_versions"].items():
        string(name, "tool name")
        string(version, "tool version")
    require(isinstance(result["limitations"], list) and all(isinstance(x, str) for x in result["limitations"]), "limitations must be a string list")
    require(isinstance(result["checks"], list) and bool(result["checks"]), "checks must be nonempty")
    ids = set()
    for check in result["checks"]:
        keys(check, ("id", "level", "status", "terminal", "exit_code", "assertions", "full_log_review", "log", "observations"))
        string(check["id"], "check id")
        require(check["id"] not in ids, "duplicate check id")
        ids.add(check["id"])
        require(check["level"] in ("static", "offline", "build", "solo", "controller", "multiplayer", "visual", "media"), "unknown evidence level")
        require(check["status"] in ("passed", "failed", "not_run", "blocked"), "unknown outcome; waivers are not passes")
        require(type(check["terminal"]) is bool, "terminal must be boolean")
        require(check["exit_code"] is None or type(check["exit_code"]) is int, "exit_code must be integer or null")
        require(type(check["assertions"]) is int and check["assertions"] >= 0, "invalid assertion count")
        require(check["full_log_review"] in ("passed", "failed", "not_run"), "invalid full-log review status")
        string(check["observations"], "observations")
        if check["status"] == "passed":
            require(check["terminal"] and check["assertions"] > 0 and check["full_log_review"] == "passed", "pass requires terminal result, current assertions, and full-log review")
            require(check["exit_code"] in (0, None), "nonzero exit cannot be passed")
            require(check["log"] is not None, "passed result requires evidence log")
        require(check["log"] is None or isinstance(check["log"], str), "log must be a relative path or null")
        if check["log"] is not None:
            log = file_bytes(local(root, check["log"]))
            scan(log, check["log"])
            # Preserve the full local log separately; receipt includes only its hash.
            check["log_sha256"] = digest(log)
    receipt = base_receipt(root, "record", doc)
    require(receipt["input_hashes"] == result["input_hashes"], "inputs changed during result validation")
    receipt.update(result)
    receipt["acceptance_coverage"] = acceptance_coverage(current_task, result["checks"])
    receipt["result_sha256"] = digest(raw)
    receipt["attestation"] = "operator-supplied observations; not independently replayed by workbench"
    return receipt
