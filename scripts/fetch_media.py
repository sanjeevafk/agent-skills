#!/usr/bin/env python3
"""Restore binary media (images, audio, video) that is kept out of git history.

The files are published as zip assets on a GitHub release and listed, with
SHA-256 checksums, in media.lock. Run this once after cloning:

    python3 scripts/fetch_media.py            # download from the release
    python3 scripts/fetch_media.py --from-dir DIR   # use zips already on disk
    python3 scripts/fetch_media.py --check    # verify only, exit 1 if anything is missing

Restored files are added to .git/info/exclude so they are never committed by accident.
"""
import argparse
import hashlib
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPO = "sanjeevafk/agent-skills"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def missing(lock):
    return [p for p, digest in lock["files"].items()
            if not (ROOT / p).is_file() or sha256(ROOT / p) != digest]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--from-dir", type=Path, help="directory that already holds the media-*.zip assets")
    ap.add_argument("--check", action="store_true", help="verify only; do not download")
    args = ap.parse_args()

    lock = json.loads((ROOT / "media.lock").read_text())
    todo = missing(lock)
    if args.check:
        print(f"{len(todo)} of {len(lock['files'])} media files missing or modified")
        return 1 if todo else 0
    if not todo:
        print(f"All {len(lock['files'])} media files present.")
        return 0

    cache = args.from_dir or ROOT / ".cache" / "media"
    cache.mkdir(parents=True, exist_ok=True)
    for name, meta in lock["assets"].items():
        zpath = cache / name
        if not zpath.is_file() or sha256(zpath) != meta["sha256"]:
            if args.from_dir:
                print(f"error: {zpath} missing or checksum mismatch", file=sys.stderr)
                return 1
            url = f"https://github.com/{REPO}/releases/download/{lock['tag']}/{name}"
            print(f"Downloading {url}")
            urllib.request.urlretrieve(url, zpath)
            if sha256(zpath) != meta["sha256"]:
                print(f"error: checksum mismatch for {name}", file=sys.stderr)
                return 1
        with zipfile.ZipFile(zpath) as z:
            for member in z.namelist():
                if member not in lock["files"]:
                    continue
                target = (ROOT / member).resolve()
                if ROOT not in target.parents:
                    print(f"error: unsafe path {member}", file=sys.stderr)
                    return 1
                z.extract(member, ROOT)

    still = missing(lock)
    if still:
        print(f"error: {len(still)} files failed verification, e.g. {still[0]}", file=sys.stderr)
        return 1

    exclude = ROOT / ".git" / "info" / "exclude"
    if exclude.parent.is_dir():
        have = set(exclude.read_text().splitlines()) if exclude.exists() else set()
        add = ["/" + p for p in lock["files"] if "/" + p not in have]
        if add:
            with open(exclude, "a") as fh:
                fh.write("\n".join(add) + "\n")
    print(f"Restored and verified {len(lock['files'])} media files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
