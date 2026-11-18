#!/usr/bin/env python3
"""Compare ZIP payloads without extracting or executing archive members."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import struct
import sys
import zipfile
import zlib


class ArchiveError(ValueError):
    """Expected unsupported, invalid, unsafe or oversized archive."""


DEFAULT_LIMITS = {
    "archive_bytes": 64 * 1024 * 1024,
    "members": 2000,
    "member_bytes": 32 * 1024 * 1024,
    "total_bytes": 128 * 1024 * 1024,
}
CHUNK = 64 * 1024


def preflight(stream, size, limits):
    """Bound central-directory entry count before ZipFile allocates objects."""
    if size > limits["archive_bytes"]:
        raise ArchiveError("archive byte limit exceeded")
    stream.seek(max(0, size - 65557))
    tail = stream.read(65557)
    start = len(tail)
    end = None
    while start:
        start = tail.rfind(b"PK\x05\x06", 0, start)
        if start < 0:
            break
        if start + 22 <= len(tail):
            record = struct.unpack_from("<4s4H2LH", tail, start)
            if start + 22 + record[-1] == len(tail):
                end = record
                break
    if end is None:
        raise ArchiveError("missing or invalid ZIP end record")
    _, disk, cd_disk, disk_count, count, cd_size, cd_offset, _ = end
    if disk or cd_disk or disk_count != count:
        raise ArchiveError("multipart ZIP archives are unsupported")
    if count == 65535 or 0xFFFFFFFF in (cd_size, cd_offset):
        raise ArchiveError("ZIP64 archives are unsupported")
    if count > limits["members"]:
        raise ArchiveError("member count limit exceeded")
    end_offset = size - len(tail) + start
    if cd_offset + cd_size != end_offset:
        raise ArchiveError("invalid or unsupported central-directory layout")
    stream.seek(cd_offset)
    actual = 0
    while stream.tell() < end_offset:
        header = stream.read(46)
        if len(header) != 46 or header[:4] != b"PK\x01\x02":
            raise ArchiveError("invalid central-directory member")
        fields = struct.unpack("<4s6H3L5H2L", header)
        actual += 1
        if actual > limits["members"]:
            raise ArchiveError("member count limit exceeded")
        if fields[13] or 0xFFFFFFFF in (fields[8], fields[9], fields[16]):
            raise ArchiveError("multipart or ZIP64 member is unsupported")
        next_offset = stream.tell() + sum(fields[10:13])
        if next_offset > end_offset:
            raise ArchiveError("central-directory member exceeds its bounds")
        stream.seek(next_offset)
    if actual != count:
        raise ArchiveError("central-directory member count mismatch")


def checked_name(info):
    name = info.orig_filename
    if not name or "\x00" in name or "\\" in name or name.startswith("/"):
        raise ArchiveError("unsafe member path")
    if re.match(r"^[A-Za-z]:", name):
        raise ArchiveError("unsafe drive-qualified member path")
    canonical = name[:-1] if name.endswith("/") else name
    if not canonical or any(p in ("", ".", "..") for p in canonical.split("/")):
        raise ArchiveError("unsafe member path component")
    kind = stat.S_IFMT(info.external_attr >> 16)
    if kind == stat.S_IFLNK:
        raise ArchiveError("symlink member rejected")
    if kind not in (0, stat.S_IFREG, stat.S_IFDIR):
        raise ArchiveError("special-file member rejected")
    if kind == stat.S_IFDIR and not info.is_dir():
        raise ArchiveError("inconsistent directory member")
    return canonical


def inventory(path, limits):
    """Return payload hashes and a separate metadata inventory."""
    try:
        if not stat.S_ISREG(os.stat(path).st_mode):
            raise ArchiveError("input must be a regular file")
        with open(path, "rb") as stream:
            before = os.fstat(stream.fileno())
            if not stat.S_ISREG(before.st_mode):
                raise ArchiveError("input must be a regular file")
            preflight(stream, before.st_size, limits)
            stream.seek(0)
            digest = hashlib.sha256()
            hashed_bytes = 0
            while chunk := stream.read(min(CHUNK, limits["archive_bytes"] - hashed_bytes + 1)):
                hashed_bytes += len(chunk)
                if hashed_bytes > limits["archive_bytes"]:
                    raise ArchiveError("archive byte limit exceeded while reading")
                digest.update(chunk)
            current = os.fstat(stream.fileno())
            if hashed_bytes != before.st_size or current.st_mtime_ns != before.st_mtime_ns:
                raise ArchiveError("input changed during inspection")
            payloads, metadata, directories, seen = {}, {}, [], set()
            total = 0
            with zipfile.ZipFile(stream) as archive:
                order = []
                comment = archive.comment.hex()
                for info in archive.infolist():
                    name = checked_name(info)
                    if name in seen:
                        raise ArchiveError("duplicate member path rejected")
                    seen.add(name)
                    order.append(name)
                    if info.flag_bits & 1:
                        raise ArchiveError("encrypted member unsupported")
                    if info.compress_type not in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
                        raise ArchiveError("only stored and deflated members are supported")
                    total += info.file_size
                    if info.file_size > limits["member_bytes"]:
                        raise ArchiveError("per-member uncompressed byte limit exceeded")
                    if total > limits["total_bytes"]:
                        raise ArchiveError("total uncompressed byte limit exceeded")
                    metadata[name] = {
                        "timestamp": list(info.date_time), "compression": info.compress_type,
                        "compressed_bytes": info.compress_size, "external_attr": info.external_attr,
                        "internal_attr": info.internal_attr, "flags": info.flag_bits,
                        "extra_hex": info.extra.hex(), "comment_hex": info.comment.hex(),
                        "create_system": info.create_system,
                    }
                    if info.is_dir():
                        if info.file_size:
                            raise ArchiveError("directory contains nonempty payload")
                        directories.append(name)
                    count, member_hash = 0, hashlib.sha256()
                    with archive.open(info) as member:
                        while True:
                            chunk = member.read(min(CHUNK, limits["member_bytes"] - count + 1))
                            if not chunk:
                                break
                            count += len(chunk)
                            if count > limits["member_bytes"]:
                                raise ArchiveError("per-member uncompressed byte limit exceeded")
                            member_hash.update(chunk)
                    if count != info.file_size:
                        raise ArchiveError("member uncompressed length mismatch")
                    if not info.is_dir():
                        payloads[name] = {"bytes": count, "sha256": member_hash.hexdigest()}
            after = os.fstat(stream.fileno())
            if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
                raise ArchiveError("input changed during inspection")
            return {"sha256": digest.hexdigest(), "bytes": before.st_size,
                    "payloads": payloads, "metadata": metadata, "directories": sorted(directories),
                    "member_order": order, "archive_comment_hex": comment}
    except (OSError, zipfile.BadZipFile, RuntimeError, NotImplementedError, EOFError,
            UnicodeError, zlib.error) as exc:
        raise ArchiveError(f"cannot inspect archive: {exc}") from None


def exact_bytes_equal(left, right, size):
    try:
        with open(left, "rb") as a, open(right, "rb") as b:
            remaining = size
            while remaining:
                wanted = min(CHUNK, remaining)
                x, y = a.read(wanted), b.read(wanted)
                if x != y or len(x) != wanted:
                    return False
                remaining -= wanted
            return a.read(1) == b.read(1) == b""
    except OSError as exc:
        raise ArchiveError(f"cannot compare archive bytes: {exc}") from None


def compare_archives(left, right, limits=None):
    limits = dict(DEFAULT_LIMITS if limits is None else limits)
    if set(limits) != set(DEFAULT_LIMITS) or any(type(v) is not int or v < 1 for v in limits.values()):
        raise ArchiveError("limits must contain four positive integer values")
    a, b = inventory(left, limits), inventory(right, limits)
    ap, bp = a["payloads"], b["payloads"]
    common = ap.keys() & bp.keys()
    added, removed = sorted(bp.keys() - ap.keys()), sorted(ap.keys() - bp.keys())
    changed = sorted(name for name in common if ap[name] != bp[name])
    metadata_changed = sorted(name for name in a["metadata"].keys() & b["metadata"].keys()
                              if a["metadata"][name] != b["metadata"][name])
    return {
        "schema": "zip-payload-diff-v1", "limits": limits,
        "archive_bytes_equal": a["sha256"] == b["sha256"] and a["bytes"] == b["bytes"]
                               and exact_bytes_equal(left, right, a["bytes"]),
        "payloads_equal": not (added or removed or changed),
        "added": added, "removed": removed, "changed": changed,
        "metadata": {"changed_members": metadata_changed,
                     "member_order_changed": a["member_order"] != b["member_order"],
                     "archive_comment_changed": a["archive_comment_hex"] != b["archive_comment_hex"],
                     "directories_added": sorted(set(b["directories"]) - set(a["directories"])),
                     "directories_removed": sorted(set(a["directories"]) - set(b["directories"]))},
        "left": {k: a[k] for k in ("sha256", "bytes", "payloads")},
        "right": {k: b[k] for k in ("sha256", "bytes", "payloads")},
        "scope": "Payload comparison only; not build reproducibility or trust verification.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    for name, default in DEFAULT_LIMITS.items():
        parser.add_argument("--max-" + name.replace("_", "-"), type=int, default=default)
    args = parser.parse_args(argv)
    limits = {name: getattr(args, "max_" + name) for name in DEFAULT_LIMITS}
    try:
        report = compare_archives(args.left, args.right, limits)
    except ArchiveError as exc:
        print(json.dumps({"error": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
