#!/usr/bin/env python3
"""Build steps for the BheemBhai skills catalog (ADR-032).

  python tools/build.py sync           copy shared/ notes into the skills listed in shared/shared-map.yaml
  python tools/build.py sync --check   fail if any copy differs from its source (CI)
  python tools/build.py pack --version 1.2.0 [--git-sha SHA] [--out dist]
                                       write dist/catalog.tgz, dist/catalog.tgz.sha256 and manifest.json
"""
import argparse
import gzip
import hashlib
import io
import json
import sys
import tarfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
SHARED = ROOT / "shared"
CONFIG = ROOT / "config"


def load_shared_map():
    data = yaml.safe_load((SHARED / "shared-map.yaml").read_text()) or {}
    return {note: (skills or []) for note, skills in data.items()}


def sync(check_only):
    problems = []
    for note, skills in load_shared_map().items():
        source = SHARED / note
        if not source.is_file():
            problems.append(f"shared-map.yaml names {note}, which is not in shared/")
            continue
        body = source.read_bytes()
        for skill in skills:
            if not (SKILLS / skill).is_dir():
                problems.append(f"shared-map.yaml names skill {skill}, which does not exist")
                continue
            target = SKILLS / skill / "references" / note
            if target.is_file() and target.read_bytes() == body:
                continue
            if check_only:
                problems.append(f"{target.relative_to(ROOT)} differs from shared/{note}; edit shared/ and run `python tools/build.py sync`")
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(body)
                print(f"synced {target.relative_to(ROOT)}")
    for p in problems:
        print(f"ERROR: {p}")
    return 1 if problems else 0


def content_sha256(folder):
    """sha256 over (relative path, bytes) of every file, sorted by path. Independent of tar metadata."""
    h = hashlib.sha256()
    for f in sorted(p for p in folder.rglob("*") if p.is_file()):
        rel = f.relative_to(folder).as_posix().encode()
        h.update(len(rel).to_bytes(4, "big") + rel)
        data = f.read_bytes()
        h.update(len(data).to_bytes(8, "big") + data)
    return h.hexdigest()


def file_sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add_bytes(tar, name, data):
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mtime = 0
    info.mode = 0o644
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    tar.addfile(info, io.BytesIO(data))


def pack(version, git_sha, out_dir):
    catalog = yaml.safe_load((ROOT / "catalog.yaml").read_text())
    if str(catalog.get("version")) != version:
        print(f"ERROR: catalog.yaml version {catalog.get('version')} does not match --version {version}")
        return 1
    manifest = {
        "catalog": version,
        "git_sha": git_sha,
        "requires_platform": catalog.get("requires_platform"),
        "requires_verify": catalog.get("requires_verify"),
        "skills": {d.name: content_sha256(d) for d in sorted(SKILLS.iterdir()) if d.is_dir()},
        "config": {f.name: file_sha256(f) for f in sorted(CONFIG.glob("*.yaml"))},
    }
    files = [ROOT / "catalog.yaml"]
    files += sorted(p for p in SKILLS.rglob("*") if p.is_file())
    files += sorted(CONFIG.glob("*.yaml"))

    out = ROOT / out_dir
    out.mkdir(parents=True, exist_ok=True)
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as tar:  # deterministic: fixed metadata, sorted entries
        add_bytes(tar, "manifest.json", json.dumps(manifest, indent=2, sort_keys=True).encode())
        for f in files:
            add_bytes(tar, f.relative_to(ROOT).as_posix(), f.read_bytes())
    archive = out / "catalog.tgz"
    with open(archive, "wb") as fh, gzip.GzipFile(fileobj=fh, mode="wb", mtime=0, filename="") as gz:
        gz.write(raw.getvalue())
    digest = file_sha256(archive)
    (out / "catalog.tgz.sha256").write_text(f"{digest}  catalog.tgz\n")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"packed {archive.relative_to(ROOT)} ({len(manifest['skills'])} skills, {len(manifest['config'])} config files) sha256 {digest}")
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sync")
    s.add_argument("--check", action="store_true")
    p = sub.add_parser("pack")
    p.add_argument("--version", required=True)
    p.add_argument("--git-sha", default="")
    p.add_argument("--out", default="dist")
    args = ap.parse_args()
    if args.cmd == "sync":
        return sync(args.check)
    return pack(args.version, args.git_sha, args.out)


if __name__ == "__main__":
    sys.exit(main())
