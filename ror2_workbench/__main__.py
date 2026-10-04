"""python -m ror2_workbench: local checks only; no execution from manifests."""

import argparse
import json
import sys
import zipfile
import zlib
from pathlib import Path
from . import __version__
from .core import Invalid, local, require, write_new, json_bytes, digest, scan
from .contract import load, metadata, task
from .release import candidate, collect, archive_bytes, verify_bytes
from .evidence import record, identity, base_receipt, git_identity
from .starter import create


def parser():
    result = argparse.ArgumentParser(description="Provider-neutral RoR2 project contracts and exact release checks. No deployment or AI calls.")
    result.add_argument("--version", action="version", version=__version__)
    sub = result.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init", help="create a new asset-free planning scaffold; never overwrite")
    init.add_argument("destination")
    init.add_argument("--name", default="MySurvivor")
    for name in ("check", "pin", "package", "verify", "identity", "status", "record", "packet"):
        command = sub.add_parser(name)
        command.add_argument("--root", default=".", help="project containing workbench.json")
        if name == "packet":
            command.add_argument("--max-bytes", type=int, default=12000, help="bounded context packet size; actual UTF-8 bytes, not an estimated token count")
        if name == "check":
            command.add_argument("--release", action="store_true", help="require all pinned release inputs")
        if name == "pin":
            command.add_argument("--output", default="local/workbench.pinned.json", help="write reviewed candidate contract to a NEW relative file")
        if name == "package":
            command.add_argument("--output", required=True, help="NEW relative ZIP path inside project")
        if name == "verify":
            command.add_argument("archive", help="relative existing ZIP path inside project")
        if name == "record":
            command.add_argument("input", help="relative operator result JSON")
        if name in ("package", "verify", "record"):
            command.add_argument("--receipt", required=True, help="NEW relative JSON receipt path")
    return result


def run(args):
    if args.command == "init":
        return create(args.destination, args.name), 0
    root = Path(args.root).absolute()
    doc = load(root)
    scan(json_bytes(doc), "workbench.json")
    if args.command in ("check", "pin", "identity", "status", "packet"):
        metadata(root, doc)
        active = task(root, doc)
        scan(json_bytes(active), "current task")
        if args.command == "packet":
            require(1000 <= args.max_bytes <= 64000, "packet byte budget must be between 1000 and 64000")
            hashes = identity(root, doc)
            context = {"tool_version":__version__, "input_hashes":hashes, "task":active, "git":git_identity(root)}
            result = {"operation":"packet", "context":context, "context_fingerprint":digest(json_bytes(context)),
                      "routing":"Choose bounded, standard or deep effort using docs/model-routing.md; no automatic model calls.",
                      "stop_rule":"One owned change and its named checks; hand off or escalate with concrete failure evidence.",
                      "limitations":"Declared file identity only; inspect the actual diff and relevant source. No source text or raw logs included."}
            require(len(json_bytes(result)) <= args.max_bytes, "context packet exceeds byte budget; narrow the task/declared inputs or deliberately choose a larger bounded budget")
            return result, 0
        if args.command == "status":
            return {"task":active, "acceptance_is":"declared; inspect evidence before relying on it", "mode":doc["mode"]}, 0
        if args.command == "identity":
            return {"input_hashes":identity(root, doc)}, 0
        if args.command == "check":
            if args.release:
                candidate(root)
            return {"operation":"check", "passed":True, "scope":"release-byte-checks" if args.release else "metadata-and-task-only", "mode":doc["mode"], "runtime_compatibility":"unverified"}, 0
        files = collect(root, doc, pinned=False)
        for entry in doc["files"]:
            entry["sha256"] = digest(files[entry["destination"]])
        output = local(root, args.output, exists=False)
        require(output.suffix == ".json", "pin output must be JSON")
        write_new(output, json_bytes(doc))
        return {"operation":"pin", "output":args.output, "next":"Review candidate pins/licensing; replace workbench.json manually. Pinning is not asset approval."}, 0
    receipt_path = local(root, args.receipt, exists=False)
    require(receipt_path.suffix == ".json" and not receipt_path.exists(), "receipt must be a NEW JSON file")
    if args.command == "record":
        receipt = record(root, args.input)
        write_new(receipt_path, json_bytes(receipt))
        code = 0 if all(c["status"] == "passed" for c in receipt["checks"]) else 1
        return {"operation":"record", "receipt":args.receipt, "all_reported_checks_passed":code == 0,
                "acceptance_coverage":receipt["acceptance_coverage"]}, code
    starting_identity = identity(root, doc)
    doc, files = candidate(root)
    if args.command == "package":
        archive_path = local(root, args.output, exists=False)
        require(archive_path.suffix == ".zip" and not archive_path.exists(), "package output must be a NEW .zip file")
        require(archive_path not in receipt_path.parents and receipt_path not in archive_path.parents, "archive and receipt paths may not contain each other")
        data = archive_bytes(files)
    else:
        archive_path = local(root, args.archive)
        require(archive_path.stat().st_size <= 256 * 1024 * 1024, "ZIP exceeds v0.1 size limit")
        with archive_path.open("rb") as stream:
            data = stream.read(256 * 1024 * 1024 + 1)
    entries = verify_bytes(data, files)
    receipt = base_receipt(root, args.command, doc)
    require(receipt["input_hashes"] == starting_identity, "inputs changed during package/verification; no output written")
    receipt.update({"archive":args.output if args.command == "package" else args.archive, "archive_sha256":digest(data), "entries":entries,
                    "limitations":["Source constant parity does not inspect compiled DLL metadata or prove build provenance.", "Hashes do not establish asset rights or generated bundle freshness.", "No game, controller, network or media acceptance was performed."]})
    if args.command == "package":
        write_new(archive_path, data)
    write_new(receipt_path, json_bytes(receipt))
    return receipt, 0


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        result, code = run(args)
    except (Invalid, OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile, zlib.error) as error:
        # Privacy-safe diagnostics: never echo untrusted JSON values, archive members,
        # matched secrets or native filesystem exception strings.
        if isinstance(error, Invalid):
            result = {"passed":False, "error":str(error)}
        else:
            result = {"passed":False, "error":"input/IO error: " + type(error).__name__}
        print(json.dumps(result, indent=2))
        return 2
    print(json.dumps(result, indent=2))
    return code


if __name__ == "__main__":
    sys.exit(main())
