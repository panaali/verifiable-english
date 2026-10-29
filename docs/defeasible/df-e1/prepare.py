"""Build DF-E1 reader items from checked Lean answers; make no model calls."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from tests.test_defaults_lean import DOCS, UNLESS_URGENT, X_ALL
from ve import defaults
from ve.backends import relay
from ve.defaults_english import sentences
from ve.norm_english import render_english
from ve.softnorms import SoftEnvironment, SoftNormDocument

HERE = Path(__file__).resolve().parent


def checked(name: str, act: str, conclusion: list) -> dict:
    environment, norms = copy.deepcopy(DOCS[name])
    for predicate in ("x_required", "x_permitted"):
        environment["vocabulary"]["predicates"][predicate]["regulated"]["act"] = "{0} " + act
    sent = []
    original = relay.decide

    def capture(mode, cases, **options):
        rows = original(mode, cases, **options)
        sent.extend((copy.deepcopy(case), copy.deepcopy(row)) for case, row in zip(cases, rows))
        return rows

    relay.decide = capture
    try:
        answer = defaults.ask(environment, norms, [], conclusion)
    finally:
        relay.decide = original
    matches = [(case, row) for case, row in sent if case.get("kind") == "defaults-certificate"]
    assert len(matches) == 1, (name, answer)
    case, row = matches[0]
    assert answer["answer"]["basis"] == row["basis"] == "needs", (name, answer)
    assert "strict_model" in case and row["verdict"] == "FOLLOWS", name
    # The plan compares the same checked answer under the two candidate markers.
    forms = {form: sentences(case, {**row, "form": form}) for form in ("long", "short")}
    assert forms[row["form"]] == answer["english"], name
    rule_text = render_english(SoftNormDocument(SoftEnvironment(environment), norms))[0]
    return {"source": name, "rule_text": rule_text, "lean_form": row["form"],
            "lean_answer": answer["answer"], "strict_countermodel": case["strict_model"],
            "rendered": forms, "expected": "yes"}


def needs_items() -> list[dict]:
    specs = [
        ("alpha", "review content", X_ALL),
        ("alpha", "flag risk", X_ALL),
        ("alpha", "explain decisions", X_ALL),
        ("alpha", "seek consent", X_ALL),
        ("alpha", "record outcomes", X_ALL),
        ("alpha", "report misuse", X_ALL),
        ("beta", "review content", UNLESS_URGENT),
        ("beta", "flag risk", UNLESS_URGENT),
        ("epsilon", "seek consent", X_ALL),
        ("epsilon", "record outcomes", X_ALL),
        ("delta", "explain decisions", X_ALL),
        ("delta", "report misuse", X_ALL),
    ]
    items = []
    for index, (name, act, conclusion) in enumerate(specs, 1):
        item = checked(name, act, conclusion)
        item["id"] = f"N{index:02d}"
        item["class"] = "short-eligible" if index <= 6 else name
        assert (item["lean_form"] == "short") == (index <= 6), item["id"]
        items.append(item)
    return items


if __name__ == "__main__":
    items = needs_items()
    (HERE / "needs.json").write_text("[\n" + ",\n".join(json.dumps(item, ensure_ascii=False)
                                                            for item in items) + "\n]\n")
    print("generated", len(items), "checked needs answers")
