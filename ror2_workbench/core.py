"""Small filesystem and reporting primitives. Never print rejected file content."""

import hashlib
import json
import re
from pathlib import Path, PurePosixPath


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def keys(value, required, optional=()):
    require(isinstance(value, dict), "expected an object")
    require(set(required) <= value.keys(), "missing required contract field(s)")
    require(value.keys() <= set(required) | set(optional), "unknown contract field(s)")


def string(value, label):
    require(isinstance(value, str) and bool(value.strip()), label + " must be a nonempty string")
    return value


def relative(value):
    string(value, "path")
    require("\\" not in value and ":" not in value and "\x00" not in value, "use portable forward-slash relative paths")
    parts = value.split("/")
    require(all(p and p not in (".", "..") and not p.endswith((" ", ".")) for p in parts), "unsafe path component")
    require(not PurePosixPath(value).is_absolute(), "absolute paths are forbidden")
    require(all(not any(c in p for c in '<>"|?*') for p in parts), "nonportable path")
    require(all(not re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", p) for p in parts), "reserved Windows path")
    return value


def local(root, name, exists=True):
    relative(name)
    root = Path(root).absolute()
    # Reject links/junctions in every existing ancestor, including the root.
    target = root.joinpath(*name.split("/"))
    for part in (target, *target.parents):
        require(not part.is_symlink(), "linked path forbidden")
        if part.exists():
            attrs = getattr(part.stat(follow_symlinks=False), "st_file_attributes", 0)
            require(not attrs & 0x400, "reparse point forbidden")
    require(all(not part.exists() or part.is_dir() for part in target.parents), "existing path parent is not a directory")
    require(target.resolve().is_relative_to(root.resolve()), "path escaped project")
    if exists:
        require(target.is_file(), "missing file: " + name)
    return target


def parse_json(data):
    def unique(pairs):
        result = {}
        for key, val in pairs:
            require(key not in result, "duplicate JSON key")
            result[key] = val
        return result
    require(len(data) <= 2_000_000, "JSON input too large")
    try:
        return json.loads(data.decode("utf-8-sig"), object_pairs_hook=unique)
    except RecursionError:
        raise Invalid("JSON nesting exceeds parser limit") from None


def read_json(path):
    with Path(path).open("rb") as stream:
        return parse_json(stream.read(2_000_001))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_bytes(path):
    require(path.stat().st_size <= 128 * 1024 * 1024, "input exceeds v0.1 128 MiB per-file limit")
    with path.open("rb") as stream:
        data = stream.read(128 * 1024 * 1024 + 1)
    require(len(data) <= 128 * 1024 * 1024, "input exceeds v0.1 128 MiB per-file limit")
    require(bool(data), "empty package input")
    return data


def write_new(path, data):
    """Exclusive creation; never overwrite a receipt or release candidate."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as stream:
        stream.write(data)


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def scan(data, label):
    # A guardrail, not proof of secret absence. Do not echo matches.
    for text in (data.decode("utf-8", errors="ignore"), data.decode("utf-16-le", errors="ignore")):
        patterns = [
            r"(?i)[a-z]:[\\/]Users[\\/]", r"/" + r"Users/[^/\s]+/", r"/" + r"home/[^/\s]+/",
            r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
            r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16})\b",
            r"(?i)(?<![A-Za-z0-9_])(?:api[_-]?key|password|secret|token)\s*[=:]\s*[\"']?[A-Za-z0-9_/-]{16,}",
        ]
        require(not any(re.search(p, text) for p in patterns), "privacy/secret pattern detected in " + label)
    # Escapes in JSON must not hide a path/credential from the byte scan.
    strict_json = label.lower().endswith(".json")
    if strict_json or data.lstrip()[:1] in (b"{", b"["):
        try:
            parsed = parse_json(data)
        except (ValueError, UnicodeError):
            require(not strict_json, "malformed UTF-8 JSON in " + label)
            return
        pending, visited = [parsed], 0
        while pending:
            value = pending.pop()
            visited += 1
            require(visited <= 100_000, "JSON scan exceeds bounded node limit")
            if isinstance(value, str):
                # A leaf is already decoded; scan it as text, not as another JSON document.
                for pattern in patterns:
                    require(not re.search(pattern, value), "privacy/secret pattern detected in " + label)
            elif isinstance(value, dict):
                for key, item in value.items():
                    credential = key.casefold().replace("_", "").replace("-", "") in ("apikey", "password", "secret", "token")
                    require(not (credential and isinstance(item, str) and re.fullmatch(r"[A-Za-z0-9_/-]{16,}", item)), "credential-like JSON value detected in " + label)
                pending.extend(value.keys())
                pending.extend(value.values())
            elif isinstance(value, list):
                pending.extend(value)


def forbidden(name):
    parts = name.lower().split("/")
    base = parts[-1]
    require(not any(p in (".git", ".aws", ".codex", "library", "packages", "obj") or p.startswith(".env") for p in parts), "private/tool-cache path forbidden")
    require(base != "init.bnk" and not base.endswith((".unitypackage", ".pdb", ".key", ".pem")), "prohibited release file")
    require(not (base.endswith(".dll") and re.match(r"(ror2|assembly-csharp|unity|system|mscorlib|netstandard|ak\.|wwise|bepinex|r2api|mmhook)", base)), "game/framework assembly must remain an external dependency")


def snapshot(root, names):
    return {name: digest(file_bytes(local(root, name))) for name in sorted(set(names))}
