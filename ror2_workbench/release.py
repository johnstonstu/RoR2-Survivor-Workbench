"""Allowlisted, pinned package bytes; ZIP parity without extracting anything."""

import io
import re
import struct
import zipfile
import zlib
from .core import require, local, digest, file_bytes, scan, relative, forbidden
from .contract import load, metadata, task

MAX_TOTAL = 256 * 1024 * 1024


def icon(data):
    require(data.startswith(b"\x89PNG\r\n\x1a\n"), "icon must be PNG")
    offset, kinds, image_data = 8, [], bytearray()
    width = height = channels = None
    while offset < len(data):
        require(offset + 12 <= len(data), "truncated PNG chunk")
        size, kind = struct.unpack(">I4s", data[offset:offset+8])
        require(size <= 8_000_000 and offset + size + 12 <= len(data), "invalid PNG chunk length")
        body = data[offset+8:offset+8+size]
        crc = struct.unpack(">I", data[offset+8+size:offset+12+size])[0]
        require(zlib.crc32(kind + body) == crc, "PNG CRC mismatch")
        if not kinds:
            require(kind == b"IHDR" and size == 13, "PNG must start with IHDR")
            width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", body)
            require((width, height) == (256, 256), "icon must be exactly 256x256")
            require(depth == 8 and color in (2, 6) and (compression, filtering, interlace) == (0, 0, 0), "v0.1 accepts noninterlaced 8-bit RGB/RGBA icons; re-export icon")
            channels = 3 if color == 2 else 4
        elif kind == b"IHDR":
            require(False, "duplicate PNG IHDR")
        if kind == b"IDAT":
            image_data.extend(body)
        kinds.append(kind)
        offset += size + 12
        if kind == b"IEND":
            require(size == 0 and offset == len(data), "invalid PNG end")
            break
    require(kinds[-1:] == [b"IEND"] and image_data, "incomplete PNG")
    decoder = zlib.decompressobj()
    expected = 256 * (1 + 256 * channels)
    pixels = decoder.decompress(image_data, expected + 1)
    require(decoder.eof and not decoder.unused_data and len(pixels) == expected, "invalid PNG pixel payload")
    require(all(pixels[i] <= 4 for i in range(0, expected, 1 + 256 * channels)), "invalid PNG row filter")


def collect(root, doc, pinned=True):
    files = {}
    total = 0
    for item in doc["files"]:
        data = file_bytes(local(root, item["source"]))
        total += len(data)
        require(total <= MAX_TOTAL, "package exceeds v0.1 256 MiB limit")
        scan(data, item["destination"])
        if pinned:
            require(item["sha256"] == digest(data), "missing/stale SHA256 pin: " + item["destination"])
            require(item["license"].strip().casefold() not in ("todo", "unknown", "unreviewed"), "unreviewed license: " + item["destination"])
            require(item["provenance"].strip().casefold() not in ("todo", "unknown", "unreviewed"), "unreviewed provenance: " + item["destination"])
        files[item["destination"]] = data
    icon(files["icon.png"])
    for name in ("README.md", "CHANGELOG.md", "LICENSE", "manifest.json"):
        require(bool(files[name].decode("utf-8-sig").strip()), "empty UTF-8 package metadata: " + name)
    version = re.escape(doc["identity"]["version"])
    require(re.search(r"(?m)^##\s+" + version + r"(?:\s|$)", files["CHANGELOG.md"].decode("utf-8-sig")), "changelog lacks current version heading")
    return files


def candidate(root):
    doc = load(root)
    metadata(root, doc)
    task(root, doc)
    require(doc["mode"] != "scaffold", "scaffold has no release binaries; adopt a reviewed project and set mode to mod")
    return doc, collect(root, doc)


def archive_bytes(files):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name, data in sorted(files.items()):
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, data)
    return stream.getvalue()


def verify_bytes(data, files):
    require(len(data) <= MAX_TOTAL, "ZIP exceeds v0.1 size limit")
    with zipfile.ZipFile(io.BytesIO(data), "r") as archive:
        entries = archive.infolist()
        require(len(entries) == len(files), "ZIP entry count differs from allowlist")
        for entry in entries:
            # ZipInfo silently replaces os.sep on Windows and truncates at NUL.
            # Reject the stored name before that normalization can hide defects.
            relative(entry.orig_filename)
            require(entry.orig_filename == entry.filename, "ZIP stored filename was normalized")
        require(len({e.filename.casefold() for e in entries}) == len(entries), "ZIP duplicate/case collision")
        require({e.filename for e in entries} == set(files), "ZIP entry names differ from exact allowlist")
        total = 0
        for entry in entries:
            relative(entry.filename)
            forbidden(entry.filename)
            require(not entry.is_dir() and not entry.flag_bits & 1, "ZIP directories/encryption forbidden")
            require(entry.compress_type in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED), "ZIP compression method unsupported")
            require((entry.external_attr >> 16) & 0o170000 != 0o120000, "ZIP symlink forbidden")
            require(entry.file_size == len(files[entry.filename]), "ZIP byte length mismatch: " + entry.filename)
            total += entry.file_size
            require(total <= MAX_TOTAL, "ZIP expanded size exceeds limit")
            # Reads check CRC too. No extraction or execution of supplied bytes.
            actual = archive.read(entry)
            require(actual == files[entry.filename], "ZIP hash parity mismatch: " + entry.filename)
    require(data == archive_bytes(files), "ZIP container differs from canonical workbench bytes; comments, extra metadata, prefixes and trailers are forbidden")
    return {name: {"bytes": len(value), "sha256": digest(value)} for name, value in sorted(files.items())}
