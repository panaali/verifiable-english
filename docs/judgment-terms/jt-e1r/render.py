"""Frozen JT-E1r display generator. No answer key is read while rendering."""
from __future__ import annotations

import csv
import json
from pathlib import Path
import subprocess
import sys

from conformance.p0 import LANGUAGE, SPEC_REVISION
from ve.environment import Environment
from ve.english import EnglishVocabulary

HERE = Path(__file__).resolve().parent
PIN = "8868ce212"  # main when the frame was frozen, before reader calls
CAPTURES = HERE / "captures"


def rows():
    with (HERE / "items.tsv").open(newline="") as stream:
        return list(csv.DictReader(stream, delimiter="|"))


def environment(row, *, template=False):
    predicate = {"arguments": ["thing"], "description": "judgment term"}
    if template and row["template"]:
        predicate["verbalisation"] = row["template"]
    return {"language": LANGUAGE, "spec_revision": SPEC_REVISION,
            "profiles": ["relational-fol@0"],
            "vocabulary": {"sorts": {"thing": {"description": "thing"}},
                           "predicates": {row["predicate"]: predicate},
                           "constants": {"focus": {"sort": "thing", "description": "focus"}}}}


def lint(row):
    if not row["template"]:
        return "absent"
    words = EnglishVocabulary(Environment(environment(row, template=True)))
    codes = sorted({issue.code for issue in words.issues})
    return "accepted" if not codes else "rejected:" + ",".join(codes)


def statement(row):
    return f'@focus is {row["predicate"]}.\n'


def command(env_path, ve_path):
    return [sys.executable, "-m", "ve", "render", "--env", str(env_path),
            "--view", "ve_english", str(ve_path)]


def control(row, *, capture=False):
    name = row["id"]
    env_path = CAPTURES / f"{name}.env.json"
    ve_path = CAPTURES / f"{name}.ve"
    output_path = CAPTURES / f"{name}-identifier.txt"
    if capture:
        CAPTURES.mkdir(exist_ok=True)
        env_path.write_text(json.dumps(environment(row), sort_keys=True, ensure_ascii=False) + "\n")
        ve_path.write_text(statement(row))
    else:
        assert json.loads(env_path.read_text()) == environment(row)
        assert ve_path.read_text() == statement(row)
    result = subprocess.run(command(env_path, ve_path), capture_output=True, check=True)
    if capture:
        output_path.write_bytes(result.stdout)
        (CAPTURES / f"{name}.command.json").write_text(json.dumps({
            "commit": PIN, "command": command(env_path, ve_path),
            "environment": env_path.name, "document": ve_path.name,
            "output": output_path.name}, indent=2) + "\n")
    else:
        assert output_path.read_bytes() == result.stdout
    return result.stdout


def english(row, fallback):
    if row["lint"] != "accepted":
        return fallback
    atom = row["atom"]
    decider = row["decider"]
    line = (f"Whether {atom} is a judgment; the text does not say who makes it."
            if decider == "unstated" else f"Whether {atom} is a judgment for {decider}.")
    return (line + "\n").encode()


def displays(row):
    old = (CAPTURES / f"{row['id']}-identifier.txt").read_bytes()
    new = (CAPTURES / f"{row['id']}-english.txt").read_bytes()
    return old, new


def audit(*, capture=False):
    frame = rows()
    assert len(frame) == 40 and len({r["id"] for r in frame}) == 40
    assert sum(r["id"].startswith("U") for r in frame) == 20
    assert sum(r["id"].startswith("C") for r in frame) == 20
    rejected = []
    for row in frame:
        assert row["lint"] == lint(row), row["id"]
        assert row["answer"] in {"settled", "turns", "conditional"}
        old = control(row, capture=capture)
        new = english(row, old)
        if capture:
            (CAPTURES / f"{row['id']}-english.txt").write_bytes(new)
        else:
            assert displays(row) == (old, new), row["id"]
        common = common_text(row)
        for value in (row["source"], row["conclusion"], row["predicate"], row["atom"], row["decider"]):
            assert value in common, (row["id"], value)
        assert old.strip() and new.strip()
        if row["lint"] != "accepted":
            assert old == new, row["id"]
            rejected.append(row["id"])
    return rejected


def common_text(row):
    return (f"SOURCE: {row['source']}\nCONCLUSION: {row['conclusion']}\n"
            f"JUDGMENT: {row['predicate']} means whether {row['atom']}; decider: {row['decider']}.\n")


if __name__ == "__main__":
    print("fallback rows:", ", ".join(audit(capture="--capture" in sys.argv)))
