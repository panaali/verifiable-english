"""ME-0: fetch the target texts with a plain HTTP client (no model) and pin them.

First run (no `fetch-log.json` for a target): writes the raw bytes fetched and `fetch-log.json` (URL, retrieval time,
HTTP status, SHA-256, size) into `docs/research/evidence/math-evidence/<target>/raw/`. Licence evidence is fetched
the same way.

Later runs (the pin exists, as on a clone): never rewrite `fetch-log.json`. A file present on disk is checked against
its logged SHA-256; a file absent (the gitignored third-party pages) is fetched again and written only if its bytes
match the logged SHA-256. A mismatch is reported with the new digest and nothing is written; the exit status is 1.

    python3 -I research/math-evidence/fetch_sources.py
"""
from __future__ import annotations

import datetime
import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "docs/research/evidence/math-evidence"
AGENT = "VE-ME0-pilot/1.0 (research measurement; plain HTTP, no model)"

WS = "https://en.wikisource.org/w/index.php?action=raw&title="
MM_INDEX = "On_the_Relative_Motion_of_the_Earth_and_the_Luminiferous_Ether"
MM_PAGE = "Page:On_the_Relative_Motion_of_the_Earth_and_the_Luminiferous_Ether.djvu/{}"
RAM_ITEM = "g.-h.-hardy-p.-v.-seshu-aiyan-b.-m.-wilson-ed.-collected-papers-of-srinivasa-ram"
RAM_TXT = ("https://archive.org/download/" + RAM_ITEM + "/G.%20H.%20Hardy%2C%20P.%20V.%20Seshu%20Aiyan%2C%20B.%20M."
           "%20Wilson%2C%20ed.%20-%20Collected%20Papers%20of%20Srinivasa%20Ramanujan-Cambridge%20University%20Press"
           "%20%281927%29_djvu.txt")
RAM_ALT = "https://archive.org/download/pli.kerala.rare.28155/pli.kerala.rare.28155_djvu.txt"

TARGETS = {
    "physics-michelson-morley": (
        [("index.wiki", WS + MM_INDEX)]
        + [(f"page-{n:02d}.wiki", WS + MM_PAGE.format(n)) for n in range(1, 14)]
    ),
    "math-ramanujan-bertrand": [
        ("collected-papers-1927-hardy-item_djvu.txt", RAM_TXT),
        ("collected-papers-1927-kerala-item_djvu.txt", RAM_ALT),
        ("hardy-item-metadata.json", "https://archive.org/metadata/" + RAM_ITEM),
    ],
    "dl-alphafold": [
        ("nature-article.html", "https://www.nature.com/articles/s41586-021-03819-2"),
        ("europepmc-fulltext.xml",
         "https://www.ebi.ac.uk/europepmc/webservices/rest/PMC8371605/fullTextXML"),
    ],
    "dl-licence-check": [
        ("arxiv-2106.09685-abs.html", "https://arxiv.org/abs/2106.09685"),
        ("arxiv-2309.16588-abs.html", "https://arxiv.org/abs/2309.16588"),
    ],
}


def fetch(url: str) -> tuple[int, bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        return response.status, response.read()


def pin(target: str, items: list[tuple[str, str]]) -> None:
    raw = EVIDENCE / target / "raw"
    raw.mkdir(parents=True)
    log = []
    for name, url in items:
        when = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
        status, body = fetch(url)
        (raw / name).write_bytes(body)
        log.append({"file": name, "url": url, "retrieved": when, "http_status": status,
                    "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()})
        print(target, name, status, len(body))
    (raw / "fetch-log.json").write_text(json.dumps(log, indent=1) + "\n")


def verify(target: str) -> list[str]:
    raw = EVIDENCE / target / "raw"
    failures = []
    for entry in json.loads((raw / "fetch-log.json").read_text()):
        path = raw / entry["file"]
        if path.exists():
            body, how = path.read_bytes(), "on disk"
        else:
            status, body = fetch(entry["url"])
            how = f"fetched again (HTTP {status})"
        digest = hashlib.sha256(body).hexdigest()
        if digest != entry["sha256"]:
            failures.append(f"{target}/{entry['file']}: {how}, sha256 {digest} != pinned {entry['sha256']}")
            print(target, entry["file"], how, "MISMATCH")
            continue
        if not path.exists():
            path.write_bytes(body)
        print(target, entry["file"], how, "matches the pin")
    return failures


def main() -> int:
    failures = []
    for target, items in TARGETS.items():
        if (EVIDENCE / target / "raw/fetch-log.json").exists():
            failures += verify(target)
        else:
            pin(target, items)
    for line in failures:
        print(line, file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
