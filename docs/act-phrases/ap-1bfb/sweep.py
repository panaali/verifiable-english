"""ap-1bfb A1: the 45-case engine sweep of ap-1bf's review (F1), rebuilt: kinds, domain, profile lists, multibyte
text, normalised spaces, more than 64 regulated predicates, `defined`, flags and admission. Each case goes through
Python's adapter and engine and through Lean's `diagnose acts@0`; a row records both and whether they differ in
status, outcome, check or text. Writes the JSON named on the command line (`before.json` on the pre-A1 hook,
`after.json` on this item's).

    uv run python docs/act-phrases/ap-1bfb/sweep.py docs/act-phrases/ap-1bfb/sweep-after.json
"""

from copy import deepcopy
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from conformance.acts_contract import REGISTRY, acts_source  # noqa: E402
from conformance.wire_contract_engine import Fault, load, run  # noqa: E402
from conformance.wire_contract_faults_acts import base  # noqa: E402
from tests import lean_routes  # noqa: E402
from ve.errors import UnsupportedProfile  # noqa: E402


def env(edit=None):
    raw, _ = base()
    if edit:
        edit(raw)
    return raw


def case(name, edit=None, kind="norms-elaborate", norms=None, **extra):
    raw, rules = base()
    if edit:
        edit(raw)
    value = {"id": name, "kind": kind, "environment": raw, "norms": rules if norms is None else norms, **extra}
    return value


def profiles(ps):
    def edit(raw):
        raw["profiles"] = ps
    return edit


def predicates(raw):
    return raw["vocabulary"]["predicates"]


def act(text, name="paid"):
    def edit(raw):
        predicates(raw)[name]["regulated"]["act"] = text
    return edit


def fixed(*phrases):
    def edit(raw):
        raw["vocabulary"]["acts"]["fixed"].extend(phrases)
    return edit


def regulated(n):
    def edit(raw):
        for i in range(n - sum("regulated" in d for d in predicates(raw).values())):
            predicates(raw)[f"r{i}"] = {"arguments": ["person"], "description": "r",
                                        "regulated": {"role": "permission", "default": "allow",
                                                      "act": "{0} seek aid " + chr(97 + i // 26) * 2 + chr(97 + i % 26)}}
    return edit


def entry(name, **fields):
    def edit(raw):
        predicates(raw)[name].update(fields)
    return edit


def both(*edits):
    def edit(raw):
        for e in edits:
            e(raw)
    return edit


def document(rules):
    return {"units": [{"id": f"u{i}", "span": [i, i + 1], "kind": "norm", "content": c} for i, c in enumerate(rules)],
            "graph": {"root": "r", "nodes": []}}


P = ["acts@0", "norms@0", "relational-fol@0"]
DEFINED = {"arguments": ["person"], "body": ["top"]}


def cases():
    _, rules = base()
    return [
        # kinds (6)
        case("kind-elaborate"), case("kind-conflict", kind="norms-conflict"),
        case("kind-certificate", kind="norms-certificate"), case("kind-defaults", kind="norm-defaults-elaborate"),
        case("kind-soft", kind="soft-elaborate"), {k: v for k, v in case("kind-missing").items() if k != "kind"},
        # domain (6)
        case("domain-plain-norms", profiles(["norms@0", "relational-fol@0"])),
        case("domain-norm-defaults", profiles(["acts@0", "norm-defaults@0", "norms@0", "relational-fol@0"])),
        case("domain-soft", profiles(["acts@0", "norms@0", "relational-fol@0", "soft-norms@0"])),
        case("domain-quantity", lambda raw: raw.update(unit_schema={})),
        case("domain-norms-string", norms="x"), case("domain-norms-member", norms=[7]),
        # profile lists (9)
        case("profiles-without-norms", profiles(["acts@0", "relational-fol@0"])),
        case("profiles-acts-only", profiles(["acts@0"])),
        case("profiles-unsorted", profiles(["norms@0", "acts@0", "relational-fol@0"])),
        case("profiles-repeated", profiles(["acts@0", "acts@0", "norms@0", "relational-fol@0"])),
        case("profiles-definitions", profiles(["acts@0", "definitions@0", "norms@0", "relational-fol@0"])),
        case("profiles-data", profiles(["acts@0", "data@0", "norms@0", "relational-fol@0"])),
        case("profiles-time", profiles(["acts@0", "norms@0", "relational-fol@0", "time@0"])),
        case("profiles-documents", profiles(["acts@0", "documents@1", "norms@0", "relational-fol@0"])),
        case("profiles-without-fol", profiles(["acts@0", "norms@0"])),
        # multibyte text (4)
        case("multibyte-act", act("{0} enjoy café")), case("multibyte-phrase", fixed("naïve rest")),
        case("multibyte-act-long", act("{0} enjoy " + "é" * 200)),
        case("multibyte-phrase-long", fixed("zeta " + "é" * 160)),
        # normalised spaces (5)
        case("spaces-act-double", act("{0}  enjoy  rest")), case("spaces-act-edges", act("  {0} enjoy rest ")),
        case("spaces-phrase-double", fixed("equal  pay")), case("spaces-phrase-edges", fixed(" equal pay ")),
        case("spaces-act-tab", act("{0}\tenjoy rest")),
        # regulated predicates (2)
        case("regulated-64", regulated(64)), case("regulated-65", regulated(65)),
        # defined (3)
        case("defined-without-definitions", entry("c", defined=DEFINED)),
        case("defined-with-definitions", both(entry("c", defined=DEFINED), profiles(
            ["acts@0", "definitions@0", "norms@0", "relational-fol@0"]))),
        case("defined-regulated", entry("paid", defined=DEFINED)),
        # flags (3)
        case("flag-functional", entry("paid", functional=True)), case("flag-total", entry("paid", total=True)),
        case("flag-plain-functional", entry("c", functional=True)),
        # admission (5)
        {**case("admission"), "kind": "admission", "document": document(rules)},
        {**case("admission-no-document"), "kind": "admission"},
        {**case("admission-units-string"), "kind": "admission", "document": {"units": "xy"}},
        {**case("admission-mixed"), "kind": "admission", "document": {"units": [7, {"kind": "norm",
                                                                                     "content": rules[0]}]}},
        {**case("admission-without-norms", profiles(["acts@0", "relational-fol@0"])), "kind": "admission",
         "document": document(rules)},
        # envelope (2)
        case("language", lambda raw: raw.update(language="ve.core@0.1")),
        case("spec-revision", lambda raw: raw.update(spec_revision="x")),
    ]


def python_row(value):
    try:
        root = acts_source(deepcopy(value))
    except UnsupportedProfile as error:
        return {"status": "error", "error": str(error)}
    outcome = run(load("acts@0"), root, registry=REGISTRY)
    if isinstance(outcome, Fault):
        return {"status": "ok", "outcome": "fault", "check": outcome.record["check"], "text": outcome.record["text"]}
    return {"status": "ok", "outcome": "clean"}


def lean_row(row):
    if row.get("status") != "ok":
        return {"status": row.get("status"), "error": row.get("error")}
    if row.get("outcome") == "fault":
        record = row["diagnostic"]
        return {"status": "ok", "outcome": "fault", "check": record["check"], "text": record["text"]}
    return {"status": "ok", "outcome": row.get("outcome")}


def main(output):
    values = cases()
    lean = lean_routes.diagnose("acts@0", deepcopy(values))
    rows = []
    for value, row in zip(values, lean):
        p, q = python_row(value), lean_row(row)
        rows.append({"case": value["id"], "python": p, "lean": q,
                     "differs": sorted(k for k in set(p) | set(q) if p.get(k) != q.get(k))})
    differing = [r["case"] for r in rows if r["differs"]]
    Path(output).write_text(json.dumps({"cases": len(rows), "differing": differing, "rows": rows}, indent=1,
                                       ensure_ascii=False) + "\n")
    print(len(rows), "cases;", len(differing), "differ:", differing)


if __name__ == "__main__":
    main(sys.argv[1])
