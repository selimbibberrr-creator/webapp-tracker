#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "index.html", "manifest.webmanifest", "sw.js", "offline.html", "404.html",
    "version.json", ".nojekyll", "icons/icon.svg", "payload/metadata.json"
]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    for path in REQUIRED:
        if not (ROOT / path).is_file():
            fail(f"Missing required file: {path}")

    manifest = json.loads((ROOT / "manifest.webmanifest").read_text(encoding="utf-8"))
    for field in ["name", "short_name", "start_url", "scope", "display", "icons"]:
        if not manifest.get(field):
            fail(f"Manifest field missing: {field}")
    if manifest["start_url"].startswith("/") or manifest["scope"].startswith("/"):
        fail("Manifest paths must remain relative for GitHub project pages")

    metadata = json.loads((ROOT / "payload/metadata.json").read_text(encoding="utf-8"))
    for index in range(metadata["chunkCount"]):
        chunk = ROOT / "payload" / f"chunk-{index:02d}.txt"
        if not chunk.is_file() or not chunk.read_text(encoding="ascii").strip():
            fail(f"Payload chunk invalid: {chunk.name}")

    subprocess.run([sys.executable, str(ROOT / "tools/build_dist.py")], check=True)
    app = (ROOT / "dist/index.html").read_text(encoding="utf-8")
    for marker in ["FORGETRACKER", "manifest.webmanifest", "serviceWorker", "void init()"]:
        if marker not in app:
            fail(f"Built app marker missing: {marker}")
    print("ForgeTracker PWA validation passed")


if __name__ == "__main__":
    main()
