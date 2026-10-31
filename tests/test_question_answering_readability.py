"""Plan Q2.6: the sealed reading and writing evaluation of `ve ask` (docs/question-answering/q2-6/readability/) is
the builder's from saved answers only, its manifest verifies, every key and gold is Lean's saved answer, and no
context carries a key, a lead name, a spec excerpt or a DELTA text. No model is called."""
from __future__ import annotations

import json
from pathlib import Path
import re
import shutil

from conformance import question_answering_readability as QR

ROOT = Path(__file__).resolve().parents[1]
SAVED = {e["id"]: e for e in (json.loads(p.read_text()) for p in (ROOT / "tests/fixtures/ask").glob("[AGU]*.json"))}
ANSWERED = {ident: entry["result"] for ident, entry in SAVED.items() if "result" in entry}
# The key of each lead, written here apart from the builder's table.
KEYS = {"yes": "YES", "no": "RULES-OUT", "notNecessarily": "ALLOWS-FAIL", "by_reading": "BY-READING",
        "notSettled": "OPEN", "unknown": "OPEN"}


def _built():
    texts = QR.files()
    return texts, json.loads(texts["items.json"])["items"], json.loads(texts["writing.json"])["tasks"]


def test_the_builder_is_deterministic_and_the_manifest_verifies(tmp_path):
    QR.build(tmp_path / "built")
    built = {str(p.relative_to(tmp_path / "built")): p.read_bytes() for p in (tmp_path / "built").rglob("*")
             if p.is_file()}
    sealed = {str(p.relative_to(QR.SEALED)): p.read_bytes() for p in QR.SEALED.rglob("*") if p.is_file()}
    assert built == sealed and "MANIFEST.sha256" in sealed
    assert QR.problems() == []
    # The opposite direction: a sealed file edited after the manifest, or an extra file, is found.
    copy = tmp_path / "copy"
    shutil.copytree(QR.SEALED, copy)
    with (copy / "contexts/R-G1.txt").open("a") as stream:
        stream.write("\n")
    (copy / "contexts/extra.txt").write_text("x")
    assert set(QR.problems(copy)) == {"manifest does not verify: contexts/R-G1.txt", "not built: contexts/extra.txt",
                                      "differs from the build: contexts/R-G1.txt"}


def test_every_reading_key_is_the_saved_lean_lead():
    texts, items, _ = _built()
    replayed = {f["id"]: f for f in json.loads((ROOT / "docs/spec/question-answering-q2/evidence/fixtures.json")
                                                .read_text())["fixtures"]}
    assert sorted(i["fixture"] for i in items if i["variant"] == "shown") == sorted(ANSWERED) and len(ANSWERED) == 17
    for item in items:
        lead = ANSWERED[item["fixture"]]["lead"]
        assert item["lead"] == lead == replayed[item["fixture"]]["lead"]
        [option] = [o for o in item["options"] if o["letter"] == item["key"]]
        assert option["label"] == item["key_label"] == KEYS[lead], item["id"]
        assert [o["label"] for o in item["options"]][-1] == "OPEN"
        assert sorted(o["label"] for o in item["options"]) == sorted(set(KEYS.values()))
        assert all(f"{o['letter']}. {o['text']}" in texts[item["context"]] for o in item["options"])


def test_a_context_is_what_a_human_gets_and_leaks_nothing():
    texts, items, tasks = _built()
    contexts = {path: text for path, text in texts.items() if path.startswith("contexts/")}
    banned = {"notNecessarily", "notSettled", "by_reading", "key_label", *KEYS.values()}
    for path, text in contexts.items():
        assert not banned & set(re.findall(r"[A-Za-z_-]+", text)), path
    pieces = set()
    for source in ("docs/spec/question-answering.md", "docs/spec/question-answering-q2/DELTA.md"):
        for line in (ROOT / source).read_text().splitlines():
            pieces |= {cell.strip() for cell in [line, *line.split("|")] if len(cell.strip()) >= 40}
    assert not [(path, piece) for path, text in contexts.items() for piece in pieces if piece in text]
    for item in items:
        answer = ANSWERED[item["fixture"]]["text"]
        if item["variant"] == "shown":
            assert "\n=== VE'S ANSWER ===\n" + "\n".join(answer) + "\n\n=== QUESTION ===\n" in texts[item["context"]]
        assert QR.render_path(item["document"]).read_text() in texts[item["context"]]
    for task in tasks:  # a writing context never shows a question of its own task
        assert not [f for f in task["fixtures"] if SAVED[f]["question"] in texts[task["context"]]]


def test_each_no_variant_differs_from_its_source_in_the_lead_line_only():
    texts, items, _ = _built()
    variants = [i for i in items if i["variant"] == "no"]
    assert sorted(v["fixture"] for v in variants) == sorted(
        ident for ident, result in ANSWERED.items() if result["lead"] == "notNecessarily") == ["A3", "G3"]
    for variant in variants:
        [source] = [i for i in items if i["fixture"] == variant["fixture"] and i["variant"] == "shown"]
        before, after = texts[source["context"]].splitlines(), texts[variant["context"]].splitlines()
        assert len(before) == len(after)
        assert [(a, b) for a, b in zip(before, after) if a != b] == [("Not necessarily.", "No.")]
        assert {k: v for k, v in variant.items() if k not in {"id", "variant", "context"}} == \
            {k: v for k, v in source.items() if k not in {"id", "variant", "context"}}


def test_each_writing_gold_is_the_saved_reading():
    texts, _, tasks = _built()
    assert sorted(f for task in tasks for f in task["fixtures"]) == sorted(ANSWERED)
    for task in tasks:
        for ident in task["fixtures"]:
            assert task["gold"] == ANSWERED[ident]["ast"] and task["gold_sentence"] == ANSWERED[ident]["sentence"]
            assert task["document"] == SAVED[ident]["path"]
        assert 0 < len(task["examples"]) <= 5
        for example in task["examples"]:
            assert SAVED[example]["path"] != task["document"] and example[0] != task["id"][2]
            assert SAVED[example]["question"] in texts[task["context"]] and example in ANSWERED
        assert f"You want to ask {task['intention']}." in texts[task["context"]]
    assert "{ve_message}" in texts["contexts/retry.txt"] and "{attempt} of 3" in texts["contexts/retry.txt"]
