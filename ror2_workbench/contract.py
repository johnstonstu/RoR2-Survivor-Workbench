"""Strict v1 project contract and source metadata validation."""

import re
from .core import Invalid, keys, require, relative, string, local, read_json, forbidden
from .csharp import literal_versions

VERSION = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
DEPENDENCY = re.compile(r"[A-Za-z0-9_]+-[A-Za-z0-9_]+-" + VERSION)


def version(value):
    require(isinstance(value, str) and re.fullmatch(VERSION, value), "version must be plain major.minor.patch")
    require(all(int(n) <= 2147483647 for n in value.split(".")), "version part exceeds System.Version bounds")


def load(root):
    doc = read_json(local(root, "workbench.json"))
    keys(doc, ("schema", "mode", "identity", "plugin", "package", "files", "coordination", "inputs"))
    require(type(doc["schema"]) is int and doc["schema"] == 1, "unsupported contract schema")
    require(doc["mode"] in ("scaffold", "fixture", "mod"), "mode must be scaffold, fixture, or mod")
    identity = doc["identity"]
    keys(identity, ("name", "version"))
    require(isinstance(identity["name"], str) and re.fullmatch(r"[A-Za-z0-9_]{1,128}", identity["name"]), "invalid package name")
    version(identity["version"])
    plugin = doc["plugin"]
    keys(plugin, ("source", "version_constant"))
    relative(plugin["source"])
    require(isinstance(plugin["version_constant"], str) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", plugin["version_constant"]), "invalid version constant")
    require(isinstance(doc["inputs"], list) and plugin["source"] in doc["inputs"], "inputs must include plugin source")
    require(len(doc["inputs"]) == len(set(doc["inputs"])), "duplicate evidence input")
    for path in doc["inputs"]:
        relative(path)
        forbidden(path)
    package = doc["package"]
    keys(package, ("manifest", "readme", "icon", "changelog", "license"))
    for path in package.values():
        relative(path)
    require(isinstance(doc["files"], list) and 5 <= len(doc["files"]) <= 128, "files must list 5-128 exact entries")
    names = set()
    for item in doc["files"]:
        keys(item, ("source", "destination", "sha256", "license", "provenance"))
        relative(item["source"])
        forbidden(item["source"])
        relative(item["destination"])
        forbidden(item["destination"])
        name = item["destination"].casefold()
        require(name not in names, "duplicate/case-colliding package destination")
        require(not any(name.startswith(n + "/") or n.startswith(name + "/") for n in names), "file/directory destination collision")
        names.add(name)
        require(item["sha256"] is None or (isinstance(item["sha256"], str) and re.fullmatch(r"[0-9a-f]{64}", item["sha256"])), "invalid SHA256 pin")
        string(item["license"], "license")
        string(item["provenance"], "provenance")
    for key, destination in {"manifest":"manifest.json", "readme":"README.md", "icon":"icon.png", "changelog":"CHANGELOG.md", "license":"LICENSE"}.items():
        require(any(f["source"] == package[key] and f["destination"] == destination for f in doc["files"]), "missing exact package mapping: " + destination)
    keys(doc["coordination"], ("task", "runtime_policy"))
    for path in doc["coordination"].values():
        relative(path)
    return doc


def metadata(root, doc):
    manifest = read_json(local(root, doc["package"]["manifest"]))
    keys(manifest, ("name", "version_number", "website_url", "description", "dependencies"))
    require(manifest["name"] == doc["identity"]["name"], "contract/Thunderstore name mismatch")
    version(manifest["version_number"])
    require(manifest["version_number"] == doc["identity"]["version"], "contract/Thunderstore version mismatch")
    require(isinstance(manifest["description"], str) and 0 < len(manifest["description"]) <= 250, "description must contain 1-250 characters")
    require(isinstance(manifest["website_url"], str) and (not manifest["website_url"] or re.fullmatch(r"https://[^\s]+", manifest["website_url"])), "website_url must be empty or HTTPS")
    deps = manifest["dependencies"]
    require(isinstance(deps, list) and all(isinstance(d, str) and DEPENDENCY.fullmatch(d) for d in deps), "dependencies must be exact Author-Package-x.y.z identifiers")
    require(len(set(deps)) == len(deps), "duplicate dependency")
    if doc["mode"] == "mod":
        require(bool(deps), "mod must declare reviewed runtime dependencies")
        require(any(f["destination"].startswith("plugins/") and f["destination"].lower().endswith(".dll") for f in doc["files"]), "mod requires an owned plugin DLL under plugins/")
    source = local(root, doc["plugin"]["source"]).read_text(encoding="utf-8-sig")
    # Literal constant only; no guessing through arbitrary C# expressions.
    found = literal_versions(source, doc["plugin"]["version_constant"])
    require(found == [doc["identity"]["version"]], "exactly one literal source version constant must match contract")
    return manifest


def task(root, doc):
    value = read_json(local(root, doc["coordination"]["task"]))
    keys(value, ("schema", "id", "goal", "base", "status", "integrator", "owned_paths", "acceptance", "next_action"))
    require(type(value["schema"]) is int and value["schema"] == 1, "unsupported task schema")
    for name in ("id", "goal", "integrator", "next_action"):
        string(value[name], name)
    require(value["base"] is None or (isinstance(value["base"], str) and re.fullmatch(r"[0-9a-f]{40,64}", value["base"])), "base must be a full Git SHA or null")
    require(value["status"] in ("planned", "active", "review", "done", "blocked"), "invalid task status")
    require(isinstance(value["owned_paths"], list) and bool(value["owned_paths"]), "owned_paths must be a nonempty list")
    for path in value["owned_paths"]:
        relative(path)
    require(isinstance(value["acceptance"], list) and bool(value["acceptance"]), "acceptance must be a nonempty list")
    acceptance_ids = set()
    for item in value["acceptance"]:
        keys(item, ("id", "level", "status", "evidence"))
        string(item["id"], "acceptance id")
        require(item["id"] not in acceptance_ids, "duplicate acceptance id")
        acceptance_ids.add(item["id"])
        require(item["level"] in ("static", "offline", "build", "solo", "controller", "multiplayer", "visual", "media"), "invalid evidence level")
        require(item["status"] in ("pending", "passed", "failed", "blocked"), "invalid acceptance status")
        require(item["evidence"] is None or isinstance(item["evidence"], str), "evidence must be a relative path or null")
        if item["evidence"] is not None:
            local(root, item["evidence"])
        require(item["status"] != "passed" or item["evidence"] is not None, "passed acceptance requires an evidence file")
    if value["status"] == "done":
        require(all(a["status"] == "passed" for a in value["acceptance"]), "done task has unresolved acceptance")
    local(root, doc["coordination"]["runtime_policy"])
    return value
