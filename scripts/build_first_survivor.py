"""Fixed opt-in .NET recipe: locked restore/build, no profile or game access."""

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
from ror2_workbench import __version__
from ror2_workbench.core import Invalid, digest, json_bytes, local, require, scan, snapshot, write_new

project = root / "examples/first-survivor"
source_names = ["Mod/Identity.cs", "Mod/Plugin.cs", "Mod/RecruitContent.cs", "Mod/FirstSurvivor.csproj", "Mod/packages.lock.json", "nuget.config", "AGENTS.md", "CLAUDE.md", "workbench.json"]


def build(offline_feed=None):
    dotnet = shutil.which("dotnet")
    require(dotnet is not None, "existing dotnet SDK is required; no tool installation is performed")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    output = project / "local" / ("build-" + stamp)
    output.mkdir(parents=True, exist_ok=False)
    task = project / "local/task.json"
    if not task.exists():
        write_new(task, local(project, "task.template.json").read_bytes())
    before = snapshot(project, source_names)
    env = os.environ.copy()
    isolated = root / "local" / "first-survivor-sdk"
    locations = {"DOTNET_CLI_HOME":"home", "NUGET_PACKAGES":"packages", "NUGET_HTTP_CACHE_PATH":"http-cache", "NUGET_PLUGINS_CACHE_PATH":"plugin-cache", "NUGET_SCRATCH":"scratch", "APPDATA":"appdata", "LOCALAPPDATA":"localappdata"}
    for variable, directory in locations.items():
        path = isolated / directory
        path.mkdir(parents=True, exist_ok=True)
        env[variable] = str(path)
    env.update(DOTNET_GENERATE_ASPNET_CERTIFICATE="false", DOTNET_CLI_TELEMETRY_OPTOUT="1", DOTNET_SKIP_FIRST_TIME_EXPERIENCE="1", DOTNET_ADD_GLOBAL_TOOLS_TO_PATH="false", DOTNET_CLI_UI_LANGUAGE="en-US", MSBUILDDISABLENODEREUSE="1")
    restore = ["restore", "Mod/FirstSurvivor.csproj", "--configfile", "nuget.config", "--locked-mode", "--disable-parallel", "-p:NuGetAudit=false"]
    if offline_feed:
        require(Path(offline_feed).is_dir(), "offline feed must be an existing package directory")
        restore.extend(["--source", str(Path(offline_feed).absolute())])
    commands = [("sdk", ["--version"]), ("restore", restore), ("build", ["build", "Mod/FirstSurvivor.csproj", "-c", "Release", "--no-restore", "--disable-build-servers", "-p:UseSharedCompilation=false", "-nodeReuse:false"])]
    results = []
    for name, arguments in commands:
        started = time.monotonic()
        completed = subprocess.run([dotnet, *arguments], cwd=project, env=env, capture_output=True, timeout=60)
        raw = completed.stdout + completed.stderr
        write_new(output / (name + ".raw.log"), raw)
        text = raw.decode("utf-8", errors="replace")
        # Full logs retained privately; only known workspace/feed paths are redacted.
        for path in (str(root), root.as_posix(), str(Path(offline_feed).absolute()) if offline_feed else ""):
            if path:
                text = text.replace(path, "<local-workspace>")
        clean = text.encode("utf-8")
        scan(clean, name + ".log")
        write_new(output / (name + ".log"), clean)
        results.append({"id":name, "exit_code":completed.returncode, "elapsed_seconds":round(time.monotonic() - started, 3), "log":name + ".log", "log_sha256":digest(clean)})
        if completed.returncode:
            break
    success = len(results) == 3 and all(item["exit_code"] == 0 for item in results)
    artifact = {}
    if success:
        require(snapshot(project, source_names) == before, "source/lock changed during build")
        name = "Mod/bin/Release/netstandard2.1/WorkbenchRecruit.dll"
        data = local(project, name).read_bytes()
        require(data.startswith(b"MZ") and len(data) > 1000, "build did not produce a plugin PE artifact")
        scan(data, "WorkbenchRecruit.dll")
        artifact = {"path":name, "bytes":len(data), "sha256":digest(data)}
    build_log = (output / "build.log").read_text() if (output / "build.log").exists() else ""
    warnings = re.findall(r"(\d+) Warning\(s\)", build_log)
    errors = re.findall(r"(\d+) Error\(s\)", build_log)
    receipt = {"schema":1, "operation":"first-survivor-build", "tool_version":__version__, "created_utc":datetime.now(timezone.utc).isoformat(), "platform":platform.system(), "status":"passed" if success else "failed", "scope":"compile-only", "restore_mode":"offline-existing-feed" if offline_feed else "official-configured-registries", "nuget_audit":"not_run", "input_hashes":before, "commands":results, "artifact":artifact, "compiler_warnings":int(warnings[-1]) if warnings else None, "compiler_errors":int(errors[-1]) if errors else None, "full_log_review":"operator review required; sanitized full logs retained", "runtime_acceptance":"not_run", "limitations":["Publicized reference compilation is not native API/runtime access proof.", "No game/profile/editor/controller/multiplayer/media test or publication occurred.", "No game/framework assemblies or source assets are part of the package allowlist."]}
    write_new(output / "receipt.json", json_bytes(receipt))
    print(json.dumps({"status":receipt["status"], "scope":receipt["scope"], "receipt":(output / "receipt.json").relative_to(root).as_posix(), "artifact":artifact}, indent=2))
    return 0 if success else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--offline-feed", help="read an existing hierarchical NuGet feed/cache; no network restore")
    args = parser.parse_args()
    try:
        sys.exit(build(args.offline_feed))
    except (Invalid, OSError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"status":"failed", "scope":"compile-only", "error":str(error) if isinstance(error, Invalid) else type(error).__name__}))
        sys.exit(2)
