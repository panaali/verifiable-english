"""fsf-r2: the translation re-measured on main after jt-2/jt-2b, df-1b/df-1bb and sc-5r/sc-5rb, with one probe per
merged item on a part document.

    python usecases/safety-framework/measure_r2.py [--source PATH] [--check]

The translation's rules and readings are fsf-r1's, unchanged (a re-expression needs an independent second-model
fidelity check, and this item makes no model calls). `units.json` and `gaps.json` are measure_r1's measurement of the
saved spans and results, with each unit's Oct 18 status beside its status today and each feature's family (JT, DF,
SC, QT, ET, AP, WG, AT, external reference, readings, no claim to check). `probes.json` is VE's answer on each probe:
admitted or refused, with Lean's diagnostic, and the status each probed unit gets. The probes are cut from the pinned
source, which is not committed, so they are rerun only where it is stored; `--check` without it checks the measurement
alone. All files go to `docs/usecases/safety-framework/fsf-r2/`; fsf-r1's evidence is not touched.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import io
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_document as B  # noqa: E402
import measure_r1 as M  # noqa: E402
import readings_r1 as R1  # noqa: E402

EVIDENCE = HERE.parents[1] / "docs" / "usecases" / "safety-framework" / "fsf-r2"
R1_EVIDENCE = M.EVIDENCE

# Each fsf-r1 feature, its family, and the merged items (since Oct 18) that bear on it, with the probes that test them.
FAMILIES = {
    "judgment terms": ("JT", ["jt-2", "jt-2b"], ["JT-a", "JT-b", "JT-c", "JT-d"]),
    "modality (may, could)": ("AT", [], []),
    "process and deadline wording": ("ET", [], []),
    "readings: a reading with no rule or several rules": ("readings", ["sc-5r", "sc-5rb"], ["SC-a", "SC-b", "SC-c", "SC-d"]),
    "external references": ("external reference", [], []),
    "attitudes (beliefs, expectations)": ("AT", [], []),
    "two readings kept: VE decides each (fsf-r1)": ("readings", ["df-1b", "df-1bb"], ["DF-a", "DF-b", "DF-c"]),
    "causation": ("WG", [], []),
    "defeasible (stated adjustments)": ("DF", ["df-1b", "df-1bb"], []),
    "attitudes (aims)": ("AT", [], []),
    "addressee (a recommendation to the field)": ("SC", [], []),
    M.NO_CLAIM: ("no claim to check", [], []),
}


def measure():
    """measure_r1's units and gaps, with the Oct 18 status of each unit and each feature's family."""
    units, rest = M.measure()
    oct18 = {u["id"]: u["status"] for u in M.load(R1_EVIDENCE / "units.json")["units"]}
    for u in units:
        u["status_oct18"] = oct18[u["id"]]
    gaps = M.gaps(units, rest)
    gaps["master_bytes_by_status"]["oct18"] = M.load(R1_EVIDENCE / "gaps.json")["master_bytes_by_status"]["today"]
    gaps["units_changed_status_since_oct18"] = [u["id"] for u in units if u["status"] != u["status_oct18"]]
    for name, entry in gaps["features"].items():
        family, merged, probes = FAMILIES[name]
        entry.update({"family": family, "merged_since_oct18": merged, "probes": probes})
    return {"units": units}, gaps


# --- probes ---------------------------------------------------------------------------------------------------------

def unit_bytes(source, *uids):
    spans = dict(zip((u for _, u, _ in B.UNITS), B.spans(source)))
    return [(uid, source[spans[uid][0]:spans[uid][1]]) for uid in uids]


def front_text(front, parts):
    """A ve-document@1 text: the front matter, then the units' source bytes in order, each unit's span its own."""
    body, cursor = b"", 0
    for unit, (_, data) in zip(front["units"], parts):
        unit["span"] = [cursor, cursor + len(data)]
        body += data
        cursor += len(data)
    return b"---\n" + json.dumps(front, indent=1, ensure_ascii=False).encode() + b"\n---\n" + body


def lean_document(text):
    """Lean's document mode on `text`, through the one relay entry: admitted with each unit's status and the
    judgments usage map, or refused with Lean's diagnostic."""
    from ve.backends.relay import answer
    row, error = answer("document", {"id": "d", "document": text.decode(), "admit": True})
    if error is not None:
        return {"admitted": False, "diagnostic": str(error)}
    return {"admitted": True, "units": {u["id"]: u["status"] for u in row["units"]},
            **({"judgments": row["judgments"]} if "judgments" in row else {}),
            "bytes_by_status": row["coverage"]["bytes_by_status"]}


def ve_document(path):
    """`ve document check` on the file (Python's loader and relays): its unit statuses, or its refusal."""
    from ve.document import check_document, load_document
    from ve.errors import VEError
    try:
        units = load_document(path)["units"]
        check_document(path)
    except VEError as exc:
        return {"admitted": False, "diagnostic": f"{type(exc).__name__}: {exc}"}
    return {"admitted": True, "units": {u["id"]: u["status"] for u in units}}


def rule_unit(uid, rule_id, terms):
    return {"id": uid, "kind": "norm", "meaning": {"open": terms} if terms else "specified", "support": "testimony",
            "content": {"norm": json.loads(B.T.parsed_rule(rule_id))}}


def judgments_probes(source):
    """JT: f7-rra's unit (s134-rra, open term OT1) under `judgments@0`."""
    parts = unit_bytes(source, "s134-rra")
    out = {}
    # JT-a: D1's own environment (soft-norms@0, readings@1) with judgments@0 and the documents@1 it requires.
    env = B.environment()
    env["profiles"] = sorted({*env["profiles"], "documents@1", "judgments@0"})
    front = {"format": "ve-document@1", "environment": env, "units": [rule_unit("s134-rra", "f7-rra",
                                                                                 ["ot1_level_reached"])],
             "open_terms": B.open_term_declarations(["ot1_level_reached"])}
    out["JT-a"] = {"what": "s134-rra in D1's environment with judgments@0", **lean_document(front_text(front, parts))}
    # JT-b: the profiles judgments@0 composes with in the document mode (no soft-norms@0, no readings@1), the open
    # term declared as D1 declares it (a token no formula reads).
    env = B.environment()
    env["profiles"] = ["documents@1", "judgments@0", "norms@0", "relational-fol@0"]
    front = {"format": "ve-document@1", "environment": env, "units": [rule_unit("s134-rra", "f7-rra",
                                                                                 ["ot1_level_reached"])],
             "open_terms": B.open_term_declarations(["ot1_level_reached"])}
    out["JT-b"] = {"what": "s134-rra without soft-norms@0, OT1 declared as in D1", **lean_document(front_text(
        copy.deepcopy(front), parts))}
    # JT-c: a re-expression (fsf-r3's, not made here): OT1 declared on the open predicate the rule reads, `reached`.
    [record] = B.open_term_declarations(["ot1_level_reached"])
    record.update(name="reached", arguments=list(env["vocabulary"]["predicates"]["reached"]["arguments"]))
    front.update(units=[rule_unit("s134-rra", "f7-rra", ["reached"])], open_terms=[record])
    out["JT-c"] = {"what": "s134-rra without soft-norms@0, OT1 declared on `reached` (a re-expression)",
                   **lean_document(front_text(front, parts))}
    # JT-d: every unit with a rule of its own and an open term, each listing the open predicates its rule reads
    # (each a judgments@0 record, decided by the vocabulary's decider), in one part document.
    predicates = env["vocabulary"]["predicates"]
    open_predicates = {p for p, d in predicates.items() if "decided by " in d["description"].lower()}
    records = {r["id"]: r for r in M.load(HERE / "spans.json")["units"]}
    units, uids = [], []
    for uid, record in records.items():
        if "rule" in record and record.get("open_terms"):
            norm = json.loads(B.T.parsed_rule(record["rule"]))
            read = sorted(open_predicates & names_in(norm["guard"]))
            units.append(rule_unit(uid, record["rule"], read))
            uids.append(uid)
    used = sorted({p for u in units if type(u["meaning"]) is dict for p in u["meaning"]["open"]})
    declarations = [{"name": p, "arguments": list(predicates[p]["arguments"]),
                     "decided_by": decider(predicates[p]["description"]),
                     "necessary": [], "sufficient": [], "factors": [], "precedents": [], "jurisdiction": "fsf_v3_1",
                     "version": 1} for p in used]
    front = {"format": "ve-document@1", "environment": env, "units": units, "open_terms": declarations}
    out["JT-d"] = {"what": "every unit with its own rule and an open term, each listing the open predicates its rule "
                           "reads (a re-expression)", "open_predicates": used,
                   **lean_document(front_text(front, unit_bytes(source, *uids)))}
    return out


def decider(description):
    """The decider vocabulary.py's `_open` names at the end of an open predicate's description."""
    return description[description.lower().rindex("decided by ") + len("decided by "):].split()[0].strip(".,;")


def names_in(node):
    """The predicate names a formula's JSON reads."""
    if type(node) is list and node and node[0] in ("unary", "binary", "ternary", "pred") and type(node[1]) is str:
        return {node[1]}.union(*(names_in(n) for n in node[2:]))
    if type(node) is list:
        return set().union(*(names_in(n) for n in node))
    return set()


def defaults_probes(source, scratch):
    """DF: the defaults flag (`ve document readings --assume-no-exception`) on RS4holistic's part document (a force
    set: strict or default), and on the same unit with only its default reading as content (a collapse, which a
    translation of someone else's text never makes: a probe of what the flag would answer, not a re-expression)."""
    from ve.document import main
    from ve.errors import VEError
    text, front = R1.part_document(source, "rs4_holistic")
    question = scratch / "holistic.json"
    question.write_text(json.dumps(["forall", "proposal", ["unary", "holistic", ["var", 0]]]))
    out = {}
    for probe, what, document in (
            ("DF-a", "RS4holistic's part document (s135-holistic, the set as D1 writes it)", front),
            ("DF-b", "s135-holistic with RS4holistic = default as its content, no set (a collapse: probe only)",
             {**front, "reading_sets": [], "units": [{**rule_unit("s135-holistic", "f20-holistic-default", []),
                                                      "span": front["units"][0]["span"]}]}),
            ("DF-c", "DF-b with norm-defaults@0 and documents@1 listed, as the df-1bb probe documents are",
             {**front, "reading_sets": [], "units": [{**rule_unit("s135-holistic", "f20-holistic-default", []),
                                                      "span": front["units"][0]["span"]}],
              "environment": {**front["environment"], "profiles": sorted(
                  {*front["environment"]["profiles"], "norm-defaults@0", "documents@1"} - {"readings@1"})}})):
        path = scratch / f"{probe}.ve.md"
        R1.write(path, text, document)
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                code = main(["readings", str(path), "--conclusion", str(question), "--assume-no-exception"])
            answer = json.loads(stdout.getvalue())
            result = {"admitted": code == 0, "question": answer["question"], "answer": answer["answer"]}
        except VEError as exc:
            result = {"admitted": False, "diagnostic": f"{type(exc).__name__}: {exc}"}
        out[probe] = {"what": what, **result, "status": ve_document(path)}
    return out


def scope_probes(source):
    """SC: RS8 on 1.3.5 bullet 2 under `scope@0`. "This is required only for external deployment, not internal
    deployment or further development" (s135-bullet2-only) narrows the DM rule of the sub-bullet before it
    (s135-bullet2-dm, rule f9-dm): as written in scope@0 it is a governor whose effect re-guards f9-dm. Its readings
    (RS8: scope, no rule / rel, a release) are readings of the governing words. Each probe runs on D1's chain (the
    soft chain with readings@1) and on the plain norms chain, which f9-dm needs alone."""
    parts = unit_bytes(source, "s135-bullet2-dm", "s135-bullet2-only")
    governor = {"id": "g1", "unit": "s135-bullet2-only", "reach": {"rules": ["f9-dm"]}, "units": ["s135-bullet2-dm"],
                "effect": {"reguard": ["and", "own", ["unary", "external", ["var", 0]]]}}
    out = {}
    for chain, profiles, names in (("D1", B.environment()["profiles"], ("SC-a", "SC-b")),
                                   ("norms", ["norms@0", "readings@1", "relational-fol@0"], ("SC-c", "SC-d"))):
        raw = {**B.environment(), "profiles": sorted(profiles)}
        env = {**raw, "profiles": sorted({*profiles, "scope@0"})}
        # The distinguishing model is over the environment without scope@0 (scope adds no symbol).
        model = B.situation_model(_soft(raw) if "soft-norms@0" in profiles else _plain(raw), B.DISTINGUISHING["RS8"])
        rs8 = {"id": "rs8_bullet2", "unit": "s135-bullet2-only", "version": 1, "status": "open",
               "readings": [{"id": choice, "kind": "norm", "meaning_id": "pending", "content": None,
                             "admission": {"who": "translator", "why": f"RS8 = {choice}",
                                           "distinguishing_models": {o: model.model_id for o in ("scope", "rel")
                                                                     if o != choice}}}
                            for choice in ("scope", "rel")],
               "models": {model.model_id: model.to_dict()}}
        for probe, with_set in zip(names, (True, False)):
            units = [rule_unit("s135-bullet2-dm", "f9-dm", ["ot2_residual_risk_acceptable"]),
                     {"id": "s135-bullet2-only", "kind": "norm", "meaning": "specified", "support": "testimony"}]
            front = {"format": "ve-document@1", "environment": copy.deepcopy(env), "units": units,
                     "open_terms": B.open_term_declarations(["ot2_residual_risk_acceptable"]),
                     "scope": {"version": "scope@0", "governors": [copy.deepcopy(governor)]},
                     **({"reading_sets": [copy.deepcopy(rs8)]} if with_set else {})}
            if not with_set:
                front["environment"]["profiles"].remove("readings@1")
            out[probe] = {"what": f"{chain} chain: s135-bullet2-only as a governor re-guarding f9-dm, "
                                  + ("with RS8's set on it" if with_set else "without RS8's set"),
                          **lean_document(front_text(front, parts))}
    return out


def _soft(raw):
    from ve.softnorms import SoftEnvironment
    return SoftEnvironment(raw)


def _plain(raw):
    from ve.environment import Environment
    return Environment.from_dict(raw)


def probes(source):
    with tempfile.TemporaryDirectory() as scratch:
        return {**judgments_probes(source), **defaults_probes(source, Path(scratch)), **scope_probes(source)}


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=B.DEFAULT_SOURCE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    units, gaps = measure()
    out = {"units.json": units, "gaps.json": gaps}
    if args.source.exists():
        source = args.source.read_bytes()
        if hashlib.sha256(source).hexdigest() != B.TEXT_SHA256 or len(source) != B.TEXT_BYTES:
            raise SystemExit("the source is not the pinned FSF 3.1 text")
        out["probes.json"] = probes(source)
    elif not args.check:
        raise SystemExit(f"the pinned source is not at {args.source}")
    for name, data in out.items():
        text = json.dumps(data, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
        if args.check:
            if (EVIDENCE / name).read_text() != text:
                raise SystemExit(f"{name} is out of date")
        else:
            EVIDENCE.mkdir(parents=True, exist_ok=True)
            (EVIDENCE / name).write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
