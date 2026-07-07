#!/usr/bin/env python3
"""Build the direct GitHub Pages artifact from the compressed ForgeTracker payload."""
from __future__ import annotations

import base64
import gzip
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = ROOT / "payload"
DIST = ROOT / "dist"


def main() -> None:
    metadata = json.loads((PAYLOAD / "metadata.json").read_text(encoding="utf-8"))
    chunks = [
        (PAYLOAD / f"chunk-{index:02d}.txt").read_text(encoding="ascii").strip()
        for index in range(metadata["chunkCount"])
    ]
    app_bytes = gzip.decompress(base64.b64decode("".join(chunks), validate=True))
    digest = hashlib.sha256(app_bytes).hexdigest()
    if digest != metadata["sha256"]:
        raise SystemExit(f"Payload checksum mismatch: {digest} != {metadata['sha256']}")
    if b"FORGETRACKER" not in app_bytes or b"void init()" not in app_bytes:
        raise SystemExit("Decoded app failed the sanity check")

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    (DIST / "index.html").write_bytes(app_bytes)

    for filename in ["manifest.webmanifest", "sw.js", "offline.html", "404.html", "version.json", ".nojekyll"]:
        shutil.copy2(ROOT / filename, DIST / filename)
    shutil.copytree(ROOT / "icons", DIST / "icons")
    shutil.copytree(ROOT / "payload", DIST / "payload")

    print(f"Built {DIST / 'index.html'} ({len(app_bytes):,} bytes, sha256={digest})")


if __name__ == "__main__":
    main()
