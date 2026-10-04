"""Original asset-free planning scaffold. No downloads or hidden code execution."""

import re
import struct
import zlib
from pathlib import Path
from .core import require, json_bytes


def png():
    def chunk(kind, body):
        return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))
    # Original, deliberately plain placeholder icon: no game artwork.
    rows = b"".join(b"\0" + bytes((20, 42, 58)) * 256 for _ in range(256))
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 256, 256, 8, 2, 0, 0, 0)) + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b"")


def create(destination, name):
    require(isinstance(name, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", name), "starter name must be a portable identifier beginning with a letter")
    target = Path(destination).absolute()
    require(not target.exists(), "starter destination already exists; never overwrite")
    for parent in target.parents:
        require(not parent.is_symlink(), "starter parent may not be linked")
        if parent.exists():
            require(not getattr(parent.stat(follow_symlinks=False), "st_file_attributes", 0) & 0x400, "starter parent may not be a junction")
    manifest = {"name": name, "version_number": "0.1.0", "website_url": "", "description": "Draft custom survivor; replace before release.", "dependencies": []}
    package = {"manifest":"package/manifest.json", "readme":"package/README.md", "icon":"package/icon.png", "changelog":"package/CHANGELOG.md", "license":"LICENSE"}
    destinations = {"manifest":"manifest.json", "readme":"README.md", "icon":"icon.png", "changelog":"CHANGELOG.md", "license":"LICENSE"}
    files = [{"source":source, "destination":destinations[key], "sha256":None, "license":"MIT", "provenance":"Original starter placeholder; review before shipping"} for key, source in package.items()]
    contract = {"schema":1, "mode":"scaffold", "identity":{"name":name, "version":"0.1.0"},
                "plugin":{"source":"mod/PluginIdentity.cs", "version_constant":"Version"},
                "inputs":["mod/PluginIdentity.cs", "AGENTS.md", "CLAUDE.md", "local/dependencies.lock.json"], "package":package, "files":files,
                "coordination":{"task":"local/task.json", "runtime_policy":"docs/runtime-policy.md"}}
    task = {"schema":1, "id":"first-skill", "goal":"Implement one native-input skill with explicit lifecycle and authority acceptance.", "base":None, "status":"planned", "integrator":"project-maintainer",
            "owned_paths":["mod"], "acceptance":[{"id":"build", "level":"build", "status":"pending", "evidence":None}, {"id":"native-held-repress", "level":"solo", "status":"pending", "evidence":None}, {"id":"controller", "level":"controller", "status":"pending", "evidence":None}, {"id":"client-host", "level":"multiplayer", "status":"pending", "evidence":None}],
            "next_action":"Choose a licensed survivor framework; implement one native-input skill before custom art."}
    license_text = (Path(__file__).parent.parent / "LICENSE").read_text(encoding="utf-8")
    payloads = {
        "workbench.json":json_bytes(contract), "package/manifest.json":json_bytes(manifest),
        "local/dependencies.lock.json":json_bytes({"schema":1, "reviewed":False, "runtime_packages":[], "build_lock":None}),
        "package/icon.png":png(), "local/task.json":json_bytes(task), "LICENSE":license_text.encode(),
        "mod/PluginIdentity.cs":('namespace ' + name + '\n{\n    // Identity only: this is not a loadable BepInEx plugin or survivor.\n    internal static class PluginIdentity\n    {\n        public const string Version = "0.1.0";\n    }\n}\n').encode(),
        "README.md":b"# Survivor development workspace\n\nRead AGENTS.md and local/task.json. The scaffold has no playable survivor.\nKeep contributor setup here and player documentation in package/README.md.\nSee the workbench docs for adopting a licensed framework and artifact checks.\n",
        "package/README.md":b"# Draft survivor\n\nPlayer-facing documentation placeholder. No playable survivor is included yet.\nReplace this with controls, skills, dependencies, compatibility, credits and known limits.\nPublish versioned media before a release and verify it in a live browser.\n",
        "package/CHANGELOG.md":b"# Changelog\n\n## 0.1.0\n\n- Draft development scaffold; no game integration yet.\n",
        "AGENTS.md":b"# Agent contract\n\nRead workbench.json and local/task.json, then inspect HEAD and the diff.\nUse one integrator for shared registrations, versions, config and generated assets.\nOwn only declared paths; task declarations do not grant deployment or publication approval.\nKeep native input, one animation transform owner, and server-owned projectile damage.\nRun build-only feedback when the maintainer owns playtesting. Record exact evidence levels.\nNever deploy, launch, publish, upload, call providers, pay, or change saves/bindings by default.\nWorktrees share profiles, Unity and Wwise. Read docs/runtime-policy.md before runtime work.\nKeep secrets, game binaries, extracted assets, raw logs and personal paths out of Git.\n",
        "CLAUDE.md":b"@AGENTS.md\n",
        ".gitignore":b".env\n.env.*\n.mcp.json\nlocal/\nevidence/\nartifacts/\ndist/\n**/bin/\n**/obj/\n**/Library/\n**/Temp/\n__pycache__/\n",
        "docs/runtime-policy.md":b"# Runtime policy\n\nNo profile changes are implemented by workbench v0.1.\nAn authorized future staging tool must target one explicitly marked disposable profile,\nrefuse a running game and linked targets, take an atomic lease at one canonical shared\ncoordination path, validate every input before any write, back up touched files, and record\nprevious/new hashes and restore instructions. Never sweep profiles or delete a fixed clean\nprofile. No age-based lease takeover. Release only after owned processes stop.\nUnity/Wwise projects and generated artifacts need the same serial owner.\nPhysical controller, real multiplayer and live media acceptance remain separate.\n",
    }
    target.mkdir(parents=True, exist_ok=False)
    for name, data in payloads.items():
        path = target / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return {"operation":"init", "mode":"scaffold", "created_files":len(payloads), "playable_survivor":False}
