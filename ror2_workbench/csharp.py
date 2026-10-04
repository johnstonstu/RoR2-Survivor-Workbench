"""Bounded C# lexical guard, not a compiler or preprocessor evaluator."""

import re
from .core import require

INTERPOLATED = re.compile(r'(?:\$+@?|@\$+)"')
CONDITIONAL = re.compile(r"#\s*(?:if|elif|else|endif)\b")
WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def tokens(source):
    require(len(source) <= 2_000_000, "C# identity source exceeds size limit")
    result, i = [], 0
    while i < len(source):
        if source[i].isspace():
            i += 1
            continue
        if source.startswith("//", i):
            end = source.find("\n", i)
            i = len(source) if end < 0 else end + 1
            continue
        if source.startswith("/*", i):
            end = source.find("*/", i + 2)
            require(end >= 0, "unterminated C# comment")
            i = end + 2
            continue
        require(not INTERPOLATED.match(source, i), "interpolated identity source is unsupported; use a dedicated literal identity file")
        require(not CONDITIONAL.match(source, i), "conditional identity source is unsupported; use a dedicated identity file")
        verbatim = source.startswith('@"', i)
        if source[i] in ('"', "'") or verbatim:
            quote = '"' if verbatim else source[i]
            start = i + (2 if verbatim else 1)
            count = len(source[i:]) - len(source[i:].lstrip('"')) if quote == '"' and not verbatim else 0
            if count >= 3:
                end = source.find('"' * count, i + count)
                require(end >= 0, "unterminated C# raw string")
                result.append(("opaque", ""))
                i = end + count
                continue
            value, escaped, i = [], False, start
            while i < len(source):
                if source[i] == quote:
                    if verbatim and source.startswith('""', i):
                        value.append('"')
                        i += 2
                        continue
                    break
                if not verbatim and source[i] == "\\":
                    require(i + 1 < len(source), "unterminated C# escape")
                    escaped = True
                    i += 2
                    continue
                require(verbatim or source[i] not in "\r\n", "newline in regular C# literal")
                value.append(source[i])
                i += 1
            require(i < len(source), "unterminated C# literal")
            result.append(("string" if quote == '"' and not escaped else "opaque", "".join(value)))
            i += 1
            continue
        match = WORD.match(source, i)
        if match:
            result.append(("word", match.group()))
            i += len(match.group())
        else:
            result.append(("symbol", source[i]))
            i += 1
    return result


def literal_versions(source, constant):
    stream = tokens(source)
    head = [("word", "const"), ("word", "string"), ("word", constant), ("symbol", "=")]
    return [stream[i+4][1] for i in range(len(stream) - 5)
            if stream[i:i+4] == head and stream[i+4][0] == "string" and stream[i+5] == ("symbol", ";")]
