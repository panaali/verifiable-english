"""E2.6: compare the saved readability replay with the saved base, from the files alone (no checkout, no git).

    .venv/bin/python -m conformance.english_lean_e2_readability_report --write

The base is E2.5's recording at `9aaf918d` (`docs/lean-first/e2/evidence/readability-base.jsonl` and
`readability-reading-base.jsonl`); the head is `english_lean_e2_readability`'s (`evidence/e2.6/`). A writing message
that changed is preserved when it keeps the scorer's outcome and, by the lf-12 DRI rule:

* every name the base quoted: quoted again in the head message, or, for a fragment of the sentence at the base
  location (the hand parser's `'t'` of `that`), a quoted word of the sentence that contains that fragment there;
* the base location: the span of Python's hand parser, which reproduces the base message at this checkout, lies
  inside the head span;
* every sentence of the base message that quotes nothing (its suggestions), verbatim.

A reading item is preserved when its verdict and message equal the base's. The report fails on any regression.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/lean-first/e2/evidence"
HEAD = EVIDENCE / "e2.6"
BASE_COMMIT = "9aaf918d538a35e63d64a7c5abc86bbcfbb87472"
QUOTED = re.compile(r"'([^']*)'")


def read(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()]


def sentences(message: str) -> list[str]:
    return [s for s in re.split(r"(?<=\.) (?=[A-Z])", message) if s]


def names_kept(base: dict, head: dict) -> list[str]:
    """The base's quoted names that the head message does not keep."""
    shown = QUOTED.findall(head["ve_message"])
    sentence, location = base["sentence"], (base.get("python") or {}).get("span")
    lost = []
    for name in QUOTED.findall(base["ve_message"]):
        if name in shown:
            continue
        if location is not None and sentence[location[0]:location[0] + len(name)] == name and any(
                name in word and 0 <= (at := sentence.find(word)) <= location[0] < at + len(word) for word in shown):
            continue  # a fragment at the base location, quoted whole by the head
        lost.append(name)
    return lost


def preservation(base: dict, head: dict) -> dict:
    python = head.get("python") or {}
    reproduced = python.get("message") == base["ve_message"]
    span, at = head.get("span"), python.get("span")
    located = bool(reproduced and span and at and span[0] <= at[0] and at[1] <= span[1])
    lost = names_kept({**base, "python": python}, head)
    suggestions = [s for s in sentences(base["ve_message"]) if not QUOTED.search(s) and s not in head["ve_message"]]
    return {"outcome_kept": base["outcome"] == head["outcome"], "base_reproduced": reproduced,
            "location_kept": located, "names_lost": lost, "suggestions_lost": suggestions,
            "preserved": base["outcome"] == head["outcome"] and located and not lost and not suggestions}


def compare(base_writing, head_writing, base_reading, head_reading) -> tuple[dict, list[dict], list[dict]]:
    if len(base_writing) != len(head_writing) or len(base_reading) != len(head_reading):
        raise ValueError("the head replay does not have the base's attempts and items")
    changed = []
    for base, head in zip(base_writing, head_writing, strict=True):
        key = ("task", "session", "attempt", "sentence")
        if any(base[k] != head[k] for k in key):
            raise ValueError(f"attempt {[base[k] for k in key]} is not the base's")
        if (base["outcome"], base["ve_message"]) != (head["outcome"], head["ve_message"]):
            changed.append({"base": base, "head": head, "check": preservation({**base, "python": head.get("python")},
                                                                              head)})
    reading_changes = []
    for base, head in zip(base_reading, head_reading, strict=True):
        if base["item"] != head["item"]:
            raise ValueError(f"item {head['item']} is not the base's {base['item']}")
        if (base["verdict"], base.get("message") or "") != (head["verdict"], head.get("message") or ""):
            reading_changes.append({"item": base["item"], "base": [base["verdict"], base.get("message") or ""],
                                    "head": [head["verdict"], head.get("message") or ""]})
    summary = {
        "format": "ve-e2.6-readability-comparison@1", "base_commit": BASE_COMMIT,
        "writing_attempts": len(head_writing),
        "writing_outcome_changes": sum(c["base"]["outcome"] != c["head"]["outcome"] for c in changed),
        "writing_message_changes": len(changed),
        "writing_preserved_changes": sum(c["check"]["preserved"] for c in changed),
        "writing_regressions": [f"{c['base']['task']} {c['base']['session']} attempt {c['base']['attempt']}"
                                for c in changed if not c["check"]["preserved"]],
        "reading_items": len(head_reading),
        "reading_unavailable": [r["item"] for r in head_reading if r["verdict"] == "unavailable"],
        "reading_differences": [r["item"] for r in reading_changes],
        "lean_reading_items": [r["item"] for r in head_reading if r.get("route") == "lean"],
    }
    summary["regression"] = bool(summary["writing_regressions"] or summary["writing_outcome_changes"]
                                 or summary["reading_unavailable"] or summary["reading_differences"])
    return summary, changed, reading_changes


def escaped(value) -> str:
    return (value or "").replace("|", "\\|").replace("\n", "<br>")


def markdown(summary: dict, changed: list[dict], reading_changes: list[dict]) -> str:
    lines = ["# E2.6 readability replay", "",
             f"Generated by `python -m conformance.english_lean_e2_readability_report --write` from the saved base "
             f"(`{BASE_COMMIT[:8]}`, E2.5's recording) and the head replay in this directory. No model was called.", "",
             f"Writing: {summary['writing_attempts']} attempts; {summary['writing_outcome_changes']} changed outcomes; "
             f"{summary['writing_message_changes']} changed messages, of which {summary['writing_preserved_changes']} "
             f"keep every base name, location and suggestion. Regressions: "
             f"**{len(summary['writing_regressions'])}**.", "",
             f"Reading: {summary['reading_items']} items; unavailable **{len(summary['reading_unavailable'])}**; "
             f"verdict or message differences from the base **{len(summary['reading_differences'])}**. Answered by "
             f"Lean directly (no product path at this checkout): {', '.join(summary['lean_reading_items'])}.", "",
             "## Changed writing messages", "",
             "| Attempt | Base message | Head message | Base span | Head span | Names lost | Suggestions lost |",
             "|---|---|---|---|---|---|---|"]
    for c in changed:
        b, h, k = c["base"], c["head"], c["check"]
        lines.append(f"| {b['task']} {b['session']} attempt {b['attempt']} | {escaped(b['ve_message'])} | "
                     f"{escaped(h['ve_message'])} | {(h.get('python') or {}).get('span')} | {h.get('span')} | "
                     f"{', '.join(k['names_lost']) or 'none'} | {', '.join(k['suggestions_lost']) or 'none'} |")
    lines += ["", "## Reading items that differ from the base", ""]
    lines += [f"- {r['item']}: base {r['base']}, head {r['head']}" for r in reading_changes] or ["None."]
    return "\n".join(lines) + "\n"


def render() -> tuple[dict, str]:
    summary, changed, reading_changes = compare(
        read(EVIDENCE / "readability-base.jsonl"), read(HEAD / "readability-writing.jsonl"),
        read(EVIDENCE / "readability-reading-base.jsonl"), read(HEAD / "readability-reading.jsonl"))
    return summary, markdown(summary, changed, reading_changes)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    summary, text = render()
    if args.write:
        (HEAD / "readability-comparison.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        (HEAD / "readability-changes.md").write_text(text)
    print(json.dumps(summary, indent=2))
    return 1 if summary["regression"] else 0


if __name__ == "__main__":
    sys.exit(main())
