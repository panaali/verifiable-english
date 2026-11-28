"""Write tour/MANIFEST.md, the tour's manifest of record: which commit each stop and each scene of the demo video
comes from, in one place.

Its inputs are files of this repository only (so the page is the same at every commit until one of them changes):
  tour/VE_MAIN_COMMIT.txt   the commit of record on main: the tour's timings were measured at it (tour/README.md,
                            "How long it takes"), and each stop's recorded output is compared with the one at it;
  tour/AFTER_RELEASE_COMMIT the commit of branch after-release that stops 4, 5, 7, 9 and 10 run from;
  tour/video-sources.tsv    every line of a stop's output that the demo video shows, with the commit it was taken
                            from (the header's commit, or the one after "@" in the file column); its "#" lines say
                            which copy of the video build's own list it was taken from;
  tour/expected/            the stops' recorded outputs (tour/make_expected.py), and git's copies of them at the
                            commit of record.

Run from anywhere:  python3 tour/make_manifest.py          (writes the page)
                    python3 tour/make_manifest.py --check  (exit 1 if the page is not what this would write)
tour/make_expected.py runs it after every recording; tests/test_tour.py fails when the page drifts.
"""
from __future__ import annotations

import csv
import hashlib
import importlib.util
from pathlib import Path
import re
import subprocess
import sys

TOUR = Path(__file__).resolve().parent
ROOT = TOUR.parent
PAGE = TOUR / "MANIFEST.md"
SOURCES = TOUR / "video-sources.tsv"
# The measured run's line on the tour page, inside its timings block: "... from a clean copy (commit <main>;
# after-release at <side>)"
TIMINGS = re.compile(r"from\s+a\s+clean\s+copy\s+\(commit\s+([0-9a-f]{10});\s+after-release\s+at\s+([0-9a-f]{10})\)")
TIMINGS_BLOCK = re.compile(r"<!-- timings -->\n(.*?)<!-- /timings -->", re.S)


def _make_expected():
    spec = importlib.util.spec_from_file_location("tour_make_expected_for_manifest", TOUR / "make_expected.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def commit_of_record() -> str:
    return (TOUR / "VE_MAIN_COMMIT.txt").read_text(encoding="utf-8").strip()


def after_release_commit() -> str:
    return (TOUR / "AFTER_RELEASE_COMMIT").read_text(encoding="utf-8").strip()


def measured() -> tuple[str, str]:
    """The (main, after-release) commits the page's timings name, 10 characters each."""
    blocks = TIMINGS_BLOCK.findall((TOUR / "README.md").read_text(encoding="utf-8"))
    found = TIMINGS.findall(blocks[0]) if len(blocks) == 1 else []
    if len(found) != 1:
        raise SystemExit(f"tour/README.md must name the measured commits once, as {TIMINGS.pattern}; found {found}")
    return found[0]


def _git_show(commit: str, path: str) -> bytes | None:
    done = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=ROOT, capture_output=True)
    if done.returncode == 0:
        return done.stdout
    present = subprocess.run(["git", "cat-file", "-e", f"{commit}^{{commit}}"], cwd=ROOT, capture_output=True)
    if present.returncode != 0:
        raise SystemExit(f"commit {commit} is not in this checkout: the manifest needs it (git fetch it)")
    return None


def video_origin() -> list[str]:
    """The file's "#" lines: where the copy was taken from."""
    with open(SOURCES, encoding="utf-8-sig") as f:
        return [line[1:].strip() for line in f if line.startswith("#")]


def video_lines() -> tuple[str, list[dict]]:
    """The header's commit and one dict per quoted line: scene, file, commit, line number, text."""
    with open(SOURCES, encoding="utf-8-sig", newline="") as f:
        rows = [(n, row) for n, row in enumerate(csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE), 1)
                if row and not row[0].startswith("#")]
    bad = [n for n, row in rows if len(row) != 4]
    if bad:
        raise SystemExit(f"{SOURCES.name}: line {bad[0]} has not exactly 4 tab-separated fields")
    head = rows[0][1]
    if head[0] != "scene" or not head[1].startswith("file@") or head[2:] != ["line", "text"]:
        raise SystemExit(f"{SOURCES.name}: unexpected header {head}")
    default = head[1].split("@", 1)[1]
    lines = []
    for _, (scene, file, number, text) in rows[1:]:
        path, _, commit = file.partition("@")
        lines.append({"scene": scene, "file": path, "commit": commit or default, "line": int(number), "text": text})
    return default, lines


def _short(commit: str) -> str:
    return commit[:10]


def render() -> str:
    stops_module = _make_expected()
    main, side = commit_of_record(), after_release_commit()
    m_main, m_side = measured()
    if m_main != _short(main):
        raise SystemExit(f"tour/README.md's timings name main {m_main}, tour/VE_MAIN_COMMIT.txt {main}: the commit of"
                         " record is the commit the timings were measured at; measure again or fix one of them")
    out = [
        "# The tour's manifest of record",
        "",
        "<!-- Written by tour/make_manifest.py; do not edit by hand. tests/test_tour.py fails when it drifts. -->",
        "",
        "Which commit each part of the tour and of the demo video comes from. Every stop's script, and the small",
        "program it runs, come from the checkout it is run in. The stops marked after-release run that program",
        "with VE's code from the pinned after-release commit; the others use the checkout's own VE. What each stop",
        "printed is recorded in tour/expected/. The demo video shows lines of those recorded outputs, each taken",
        "at a commit named below.",
        "",
        f"- **Commit of record (main):** `{main}`.",
        "  The tour's timings were measured at it; each stop's recorded output below is compared with the one",
        "  recorded at it.",
        f"- **After-release commit (pinned in tour/AFTER_RELEASE_COMMIT):** `{side}`.",
        f"- **Timings** (tour/README.md, \"How long it takes\"): measured at main `{m_main}`, after-release "
        f"`{m_side}`" + ("." if m_side == _short(side) else
                         f"; the after-release pin has moved since (to `{_short(side)}`), so those stops' times"
                         " are of the earlier commit."),
        "",
        "## Stops",
        "",
        "| stop | runs from | recorded output (sha256, first 12) | same output at the commit of record |",
        "|---|---|---|---|",
    ]
    for stop in stops_module.STOPS:
        rel = f"tour/expected/{stop}.txt"
        now = (ROOT / rel).read_bytes()
        then = _git_show(main, rel)
        runs = (f"this checkout, with VE from after-release `{_short(side)}`" if stop in stops_module.AFTER_RELEASE
                else "this checkout")
        same = ("not recorded at that commit" if then is None else "same" if then == now else
                "DIFFERS: recorded again after the commit of record")
        out.append(f"| {stop} | {runs} | `{hashlib.sha256(now).hexdigest()[:12]}` | {same} |")
    default, lines = video_lines()
    out += [
        "",
        "## Video scenes",
        "",
        f"From tour/video-sources.tsv (the lines of the stops' outputs that the video shows; its default commit"
        f" `{default}`), " + "; ".join(video_origin()) + ".",
        "\"Same at the commit of record\" and \"same today\" compare each shown line with the same line of the",
        "recorded output at the commit of record and in this checkout. \"After-release pin then\" is the pin in",
        "force at the scene's commit, for the stops that use it.",
        "",
        "| scene | output it shows | taken at commit | after-release pin then | lines shown | same at the commit of"
        " record | same today |",
        "|---|---|---|---|---|---|---|",
    ]
    scenes: dict[tuple, list[dict]] = {}
    for line in lines:
        scenes.setdefault((line["scene"], line["file"], line["commit"]), []).append(line)
    def compare(shown, content, missing, then=""):
        if content is None:
            return missing
        current = content.splitlines()
        differ = [str(x["line"]) for x in shown if x["line"] > len(current) or current[x["line"] - 1] != x["text"]]
        return "yes" if not differ else f"NO: line {', '.join(differ)} differs{then}"

    after_release_files = {f"tour/expected/{s}.txt" for s in stops_module.AFTER_RELEASE}
    for (scene, file, commit), shown in scenes.items():
        then_record = _git_show(main, file)
        at_record = compare(shown, None if then_record is None else then_record.decode("utf-8"),
                            "no: not recorded at that commit")
        today = compare(shown, (ROOT / file).read_text(encoding="utf-8") if (ROOT / file).is_file() else None,
                        "no: not recorded in this checkout", " (re-cut the scene)")
        pin = "-"
        if file in after_release_files:
            pinned = _git_show(commit, "tour/AFTER_RELEASE_COMMIT")
            pin = "none" if pinned is None else f"`{_short(pinned.decode('utf-8').strip())}`"
        numbers = ", ".join(str(x["line"]) for x in shown)
        out.append(f"| {scene} | {file} | `{_short(commit)}` | {pin} | {numbers} | {at_record} | {today} |")
    unshown = [s for s in stops_module.STOPS if not any(f == f"tour/expected/{s}.txt" for _, f, _ in scenes)]
    out += ["", "Stops the video does not show: " + (", ".join(unshown) if unshown else "none") + "."]
    return "\n".join(out) + "\n"


def main(argv) -> int:
    page = render()
    if argv == ["--check"]:
        if not PAGE.is_file() or PAGE.read_text(encoding="utf-8") != page:
            print("tour/MANIFEST.md is not what tour/make_manifest.py writes: run python3 tour/make_manifest.py",
                  file=sys.stderr)
            return 1
        return 0
    if argv:
        print("usage: python3 tour/make_manifest.py [--check]", file=sys.stderr)
        return 2
    PAGE.write_text(page, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
