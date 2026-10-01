"""Check source-linked readings on feature routes that cannot share one profile.

This is an authoring record, not a claim that proposed work happened.  Every
entry names an unchanged source unit and is checked by the merged parser or
statement layer in the foreground when this script runs.
"""
from __future__ import annotations

import json
import subprocess
from hashlib import sha256
from pathlib import Path

from ve.environment import Environment
from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.speech_acts import SpeechDocument
from ve.reports import ReportsDocument
from ve.english import parse_english_with_metadata, render_english
from ve.units import elaborate_quantity
from ve.risk import run_case

HERE = Path(__file__).resolve().parent
SOURCE_HASH = "a9fa225acce6a684af7519c9c6fa82a20fc3a7e685a04b7e1a4bac88a0d6ed22"

COMMANDS = {
    "u018": "compare at matched cost", "u019": "focus the benchmark",
    "u020": "test forged findings", "u021": "include real artefacts",
    "u067": "paste one unlabelled candidate", "u079": "compare at matched cost",
    "u080": "focus the benchmark", "u081": "test forged findings",
    "u082": "include real artefacts",
}
RISK_WORDINGS = {
    "u029": "label might lead to confidence",
    "u035": "label might lead to confidence",
    "u037": "formalisation might lead to misstatement",
    "u086": "label might lead to confidence",
    "u088": "formalisation might lead to misstatement",
}
DATED_PLANS = {"u012": "2026-10-25", "u017": "2026-10-25", "u078": "2026-10-25"}
REPORTS = {"u003": ("old_text", "says", "tests_checker"),
           "u007": ("applicant", "intends", "tests_mandatory_proofs"),
           "u060": ("supplied_update", "says", "judges_reach_ceiling"),
           "u074": ("applicant", "intends", "tests_mandatory_proofs")}


def _lean_route(executable: str, case: dict) -> dict:
    binary = HERE.parents[1] / "lean" / ".lake" / "build" / "bin" / executable
    process = subprocess.run([str(binary), "-"], input=json.dumps([case]), text=True,
                             capture_output=True, check=False, timeout=180)
    if process.returncode not in (0, 1):
        raise RuntimeError(process.stderr)
    [result] = json.loads(process.stdout)
    assert result["status"] == "ok", result
    return result


def _base(profiles, sorts, predicates, constants, **extra):
    return {"language": LANGUAGE, "profiles": profiles, "spec_revision": SPEC_REVISION,
            "vocabulary": {"sorts": {s: {"description": s} for s in sorts},
                           "predicates": predicates, "constants": constants, **extra.pop("vocabulary", {})},
            **extra}


def check_commands():
    tasks = {f"task_{uid}": {"sort": "task", "description": description}
             for uid, description in COMMANDS.items()}
    env = Environment(_base(
        ["norms@0", "relational-fol@0", "speech-acts@0"], ("author", "task"),
        {"perform_required": {"arguments": ["author", "task"], "description": "perform",
                              "regulated": {"role": "obligation", "default": "deny",
                                            "act": "{0} perform {1}", "permission": "perform_permitted"}},
         "perform_permitted": {"arguments": ["author", "task"], "description": "perform",
                               "regulated": {"role": "permission", "default": "allow",
                                             "act": "{0} perform {1}"}}},
        {"applicant": {"sort": "author", "description": "the applicant"}, **tasks},
        speech_acts={"task": "grant_edit", "addressee": {"sort": "author", "constant": "applicant"}}))
    units = [{"id": uid, "span": [i, i + 1], "kind": "instruction", "meaning": "specified", "support": "none",
              "content": {"command": {"force": "require", "act": "perform_required",
                                      "args": [f"task_{uid}"], "guard": ["top"]}}}
             for i, uid in enumerate(COMMANDS)]
    speech = SpeechDocument(env, units)
    assert len(speech.policy.rules) == len(COMMANDS)
    _lean_route("ve_speech_acts_route", {"id": "bluedot-commands", "kind": "speech-elaborate",
                                         "environment": env.to_dict(), "document": {"units": units}})
    return {uid: {"command": description, "force": "require", "active": True}
            for uid, description in COMMANDS.items()}


def check_reports():
    predicates = {name: {"arguments": ["text"], "description": name.replace("_", " ")}
                  for _, _, name in REPORTS.values()}
    env = Environment(_base(
        ["documents@1", "relational-fol@0", "reports@0"], ("text", "evidence"), predicates,
        {name: {"sort": "text", "description": name}
         for name in ("old_text", "applicant", "supplied_update")},
        vocabulary={"reports": {"holders": ["text"], "evidence": "evidence"}}))
    units = []
    for index, (uid, (holder, act, predicate)) in enumerate(REPORTS.items()):
        units.append({"id": uid, "span": [index, index + 1],
                      "kind": ["attributed", holder, act, "asserted"],
                      "meaning": "specified", "support": "none",
                      "content": {"report": {"holder": holder, "act": act, "context": "draft",
                                             "content": {"ast": ["unary", predicate,
                                                                                    ["const", holder]]}}}})
    reports = ReportsDocument(env, [{"id": "draft", "tense": "present",
                                     "description": "grant draft wording"}], [], units)
    assert len(reports.premises) == len(REPORTS)
    _lean_route("ve_reports_route", {"id": "bluedot-reports", "kind": "reports-elaborate",
                                     "environment": env.to_dict(),
                                     "document": {"units": units, "contexts": [
                                         {"id": "draft", "tense": "present",
                                          "description": "grant draft wording"}], "assessments": []}})
    return {uid: {"holder": holder, "act": act, "content_predicate": predicate,
                  "promoted_to_truth": False} for uid, (holder, act, predicate) in REPORTS.items()}


def check_risk():
    pred = lambda args, wording: {"arguments": args, "description": wording, "verbalisation": wording}
    env = Environment(_base(
        ["alternatives@0", "norms@0", "relational-fol@0", "risk@0"],
        ("action", "chooser", "harm"),
        {"available": pred(["action", "chooser"], "{0} is available to {1}"),
         "leads_to": pred(["action", "harm"], "{0} leads to {1}")},
        {"label": {"sort": "action", "description": "proof label"},
         "formalisation": {"sort": "action", "description": "formalisation"},
         "confidence": {"sort": "harm", "description": "false confidence"},
         "misstatement": {"sort": "harm", "description": "misstatement of the task"}},
        alternatives={"chooser": "chooser", "action": "action", "harm": "harm",
                      "available": "available", "leads_to": "leads_to", "outcomes": "signed"},
        risk={"severity": {"sort": "severity", "classes": ["unassessed"],
                            "more_severe": [], "unranked": [],
                            "decided_by": "grant-author"},
              "harm_classes": [["confidence", "unassessed"], ["misstatement", "unassessed"]],
              "unexamined": "possible"}))
    assert run_case({"id": "bluedot-risk", "kind": "risk-elaborate",
                     "environment": env.to_dict(), "document": {"norms": []}})["status"] == "ok"
    result = {}
    for uid, wording in RISK_WORDINGS.items():
        parsed = parse_english_with_metadata(env, wording + ".",
                                             accept_suggested_vocabulary=True).document.formulas[0]
        assert render_english(parsed, env, accept_suggested_vocabulary=True).lower() == wording
        result[uid] = {"wording": wording, "ast": str(parsed),
                       "status": "possible_under_unexamined_policy"}
    return result


def check_dates():
    env = Environment(_base(
        ["order@0", "relational-fol@0", "time@0"], (), {},
        {"milestone_deadline": {"sort": "$int", "unit": "day",
                                 "description": "milestone deadline"}},
        unit_schema="ve-units@1",
        units={"day": {"scale": "1", "display": {"kind": "iso_date"}}}))
    result = {}
    for uid, date in DATED_PLANS.items():
        payload = {"format": "ve-quantity@1",
                   "formula": ["date_on", ["const", "day", "milestone_deadline"], ["date", date]]}
        canonical, _ = elaborate_quantity(env, payload)
        _lean_route("ve_quantity", {"id": uid, "environment": env.to_dict(), "quantity": canonical})
        result[uid] = {"date": date, "quantity": canonical, "force": "intended_release_deadline"}
    return result


def main():
    from .build_document import build
    assert sha256((HERE / "source.md").read_bytes()).hexdigest() == SOURCE_HASH
    document = build()
    checked = {u["id"] for u in document["units"] if u["status"] == "CHECKED"}
    readings = {"speech_acts": check_commands(), "reports": check_reports(),
                "risk_possibility": check_risk(), "time": check_dates()}
    assert set().union(*(set(r) for r in readings.values())) <= checked
    (HERE / "feature-readings.json").write_text(json.dumps(
        {"source_sha256": SOURCE_HASH, "signature": "grant-author",
         "why": "Separate profile routes preserve the source unit's force without asserting completion or observed harm.",
         "readings": readings}, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
