"""ci-2b's A/B over the pinned command corpus (DRI 2026-10-28 item 2(a); plan section 9).

    uv run python docs/commands-imperatives/ci-2b/evidence/ab.py pin RAW.jsonl   # writes corpus.json.gz
    uv run python docs/commands-imperatives/ci-2b/evidence/ab.py run             # writes ab.json
    uv run python docs/commands-imperatives/ci-2b/evidence/ab.py check           # exit 1 on a forbidden row

The corpus: every command wording the speech-acts tests read (`record_plugin.py`, on the frozen pre-switch side and
on Lean's), every wording of no question form of the Q1.4 A/B corpus (docs/question-answering/q1-4b/evidence), and
ci-1's review F3 rows. Base: the pre-switch parser (`tests/frozen_speech/speech_english.py`) with the pre-switch
query selection (`ve/speech_document.py` at the base: the one record whose target is the sentence's `_sentence`).
Head: Lean's `english.command` answer through `read_command`'s binding (`command_answer`). Each row is classed:
`same`; `R1` (both refused, the base's code (its class when it has none) and quoted names kept, or a `RULED` code); `b2` (read by the base, refused, `many` or `limit`
in the head); `many` (refused by the base, `many` in the head: item 2(a)); and the forbidden `read` (refused, now read),
`changed` (read differently) and `code` (refused with another code or without a quoted name).
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "tests")]
CORPUS, RESULT = HERE / "corpus.json.gz", HERE / "ab.json"
PROVE, PREMISES = "Prove that ", " using these premises."
FORBIDDEN = ("read", "changed", "code")
# A base code the head replaces by a ruled one: a proof task with no record whose target is its sentence was
# `InvalidInput: query required` (the deleted selection found none) and is `QueryMismatch: <unit>` (spec P2, O1:
# reviews/dri-decisions-20261102-ci-0.md item 2).
RULED = {("InvalidInput", "QueryMismatch")}


def _key(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()[:16]


def pin(raw: Path) -> None:
    from ve.speech_acts import wording_text
    from ve.errors import VEError
    environments, rows = {}, {}

    def add(env, wording, queries=None, query=None, source="tests"):
        name = _key(env)
        environments.setdefault(name, env)
        rows.setdefault((name, wording, json.dumps(queries, sort_keys=True), query),
                        {"env": name, "wording": wording, "queries": queries, "query": query, "source": source})
    for line in raw.read_text().splitlines():
        r = json.loads(line)
        add(r["environment"], r["wording"], r.get("queries"), r.get("query"))
    sys.path.insert(0, str(ROOT / "docs/question-answering/q1-4b/evidence"))
    import speech_ab_f2 as q14
    for r in q14.recordings(str(ROOT / "docs/question-answering/q1-4b/evidence"))[1]:
        try:
            text = wording_text(r["wording"])
        except VEError:
            continue
        if text and not text.startswith(("Is ", "Must ", "Can ", "Which ", "Does it follow")):
            add(q14._environment(r["env"]).to_dict(), r["wording"], [], None, "q1-4")
    from test_speech_source_lean import base_env
    for wording in ("Click check, if .", "Click check, if atlas is reviewed and beacon is reviewed or tom is a cat."):
        add(base_env(), wording, [], None, "ci-1 F3")
    CORPUS.write_bytes(gzip.compress(json.dumps({"environments": environments, "rows": list(rows.values())},
                                                sort_keys=True).encode(), mtime=0))


def _base(env, row):
    from ve.ast import _to_data
    from ve.errors import VEError
    from ve.speech_english import _sentence
    from tests.frozen_speech.speech_english import parse_speech
    query = row["query"]
    try:
        text = row["wording"].strip()
        if row["queries"] is not None and text.startswith(PROVE) and text.endswith(PREMISES):
            target = _to_data(_sentence(env, text[len(PROVE):-len(PREMISES)] + "."))
            matches = [q["id"] for q in row["queries"] if q["target"]["ast"] == target]
            query = matches[0] if len(matches) == 1 else None
        return {"outcome": "one", "command": parse_speech(env, row["wording"], env.speech_acts, query=query)[0]}
    except VEError as exc:
        return {"outcome": "refused", "class": type(exc).__name__, "text": exc.message}


def _records(env, row):
    """The head's query records: the row's, or, for a proof task the frozen side read with a selected query, the one
    record the base's selection implies (that query, with the sentence's target)."""
    from ve.ast import _to_data
    from ve.errors import VEError
    from ve.speech_english import _sentence
    if row["queries"] is not None:
        return row["queries"]
    text = row["wording"].strip()
    if row["query"] is None or not (text.startswith(PROVE) and text.endswith(PREMISES)):
        return []
    try:
        target = _to_data(_sentence(env, text[len(PROVE):-len(PREMISES)] + "."))
    except VEError:
        return []
    return [{"id": row["query"], "premises": [], "target": {"ast": target}}]


def _head(env, row):
    from ve.backends import english_lean, relay
    from ve.english import EnglishVocabulary
    from ve.errors import VEError
    from ve.speech_acts import wording_text
    try:
        wording = wording_text(row["wording"])
    except VEError as exc:
        return {"outcome": "refused", "class": type(exc).__name__, "text": exc.message}
    case = english_lean.command_request(env, wording, EnglishVocabulary(env, _defer_overlay_refusals=True), {},
                                        unit="u", queries=_records(env, row))
    result = english_lean.command_answer(relay.decide_once(english_lean.COMMAND_MODE, case), case)
    if result["outcome"] == "one":
        return {"outcome": "one", "command": result["reading"]["command"]}
    if result["outcome"] == "refused":
        return {"outcome": "refused", "class": result["class"], "text": f"{result['code']}: {result['text']}"}
    return {"outcome": result["outcome"], "readings": len(result.get("readings", []))}


def classify(base, head) -> str:
    if base == head:
        return "same"
    if base["outcome"] == "one":
        return "changed" if head["outcome"] == "one" else "b2"
    if head["outcome"] == "many":
        return "many"
    if head["outcome"] != "refused":
        return "read" if head["outcome"] == "one" else "b2"
    quoted = set(re.findall(r"'[^']*'", base["text"])) - set(re.findall(r"'[^']*'", head["text"]))
    coded = re.match(r"([A-Z][A-Za-z]+): ", base["text"])
    kept = (coded[1], head["text"].split(":", 1)[0]) in RULED or head["text"].startswith(coded[0]) if coded \
        else base["class"] == head["class"]
    return "R1" if kept and not quoted else "code"


def run() -> dict:
    from ve.environment import Environment
    corpus = json.loads(gzip.decompress(CORPUS.read_bytes()))
    rows, counts = [], {}
    for row in corpus["rows"]:
        env = Environment(corpus["environments"][row["env"]])
        base, head = _base(env, row), _head(env, row)
        cls = classify(base, head)
        counts[cls] = counts.get(cls, 0) + 1
        if cls != "same":
            rows.append({"class": cls, "env": row["env"], "wording": row["wording"], "source": row["source"],
                         "base": base, "head": head})
    result = {"corpus_sha256": hashlib.sha256(CORPUS.read_bytes()).hexdigest(), "rows": len(corpus["rows"]),
              "counts": dict(sorted(counts.items())), "changed": rows}
    RESULT.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    return result


def problems(result: dict) -> list[str]:
    """The saved A/B's forbidden rows and its inconsistencies: what item 2(a) and R1 do not allow."""
    out = [f"{r['class']}: {r['wording']!r}" for r in result["changed"] if r["class"] in FORBIDDEN]
    out += [f"misclassed: {r['wording']!r}" for r in result["changed"] if classify(r["base"], r["head"]) != r["class"]]
    if sum(result["counts"].values()) != result["rows"]:
        out.append("the counts do not total the rows")
    return out


if __name__ == "__main__":
    command = sys.argv[1]
    if command == "pin":
        pin(Path(sys.argv[2]))
    elif command == "run":
        print(json.dumps(run()["counts"]))
    found = problems(json.loads(RESULT.read_text()))
    print("\n".join(found) or "A/B: no forbidden row")
    sys.exit(1 if found else 0)
