"""Rebuild the UDHR ve-green-flaky4 measurement from the pinned prior run, without model calls.

Starts from base/ (the 2026-09-29T0600Z translation, unchanged bytes) and changes only the four units the
2026-09-29 audit rejected (u017, u052, u112, u114). Run from the repository root's environment with
PATH=~/.elan/bin:$PATH so the soft-norms Lean route is found.
"""
from __future__ import annotations

from collections import Counter
import copy
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
sys.path.insert(0, str(HERE))
import candidates as C
from ve.ast import Binary, Forall, Implies, Not, Or, Unary, Var, formula_to_data
from ve.document import check_document, coverage, load_document, render_document
from ve.entailment import check_entailment_certificate, prove_entailment
from ve.english import lint_english_vocabulary
from ve.environment import Environment
from ve.identity import meaning_id
from ve.model import FiniteModel
from ve.norms import NormDocument

SOURCE = HERE.parent / "source" / "udhr.md"
BASE = HERE / "base"
READINGS = HERE / "readings"
PIN = "d6495201e9f6229603d2b13427ac68bd8febf5ad80f1cec329bbc3d04d9c7d3a"
raw = SOURCE.read_bytes()
assert hashlib.sha256(raw).hexdigest() == PIN

prior = (BASE / "translation.ve.md").read_bytes()
front, body = prior[4:].split(b"\n---\n", 1)
assert body == raw
meta = json.loads(front)
rows = json.loads((BASE / "units.json").read_text())["units"]
old_metrics = json.loads((BASE / "metrics.json").read_text())
assert len(meta["units"]) == len(rows) == 129
by_id = {r["id"]: r for r in rows}
unit_by_id = {u["id"]: u for u in meta["units"]}
REPAIRED = ["u017", "u052", "u112", "u114"]

# ---------------------------------------------------------------- environment additions (base predicates only)
# Regulated predicates for pending candidates are NOT declared here: a regulated predicate brings its completion
# into every premise check of this document, and no source unit states one.
vocab = meta["environment"]["vocabulary"]
vocab["sorts"]["right"] = C.sort("right", "rights",
                                 "a right or freedom set forth in this Declaration")
vocab["sorts"]["bearer"] = C.sort("bearer", "bearers", "a State, group or person")


def base_predicate(arguments, description):
    # No verbalisation: the English vocabulary lint accepts only one-word unary complements and article-free
    # binary verbs, which cannot say these conditions; the renderer falls back to the identifier (see metrics).
    return {"arguments": arguments, "description": description}


vocab["predicates"].update({
    "genuinely_prosecuted_for_non_political_crime": base_predicate(
        ["person"], "The person faces a prosecution that genuinely arises from a non-political crime"),
    "genuinely_prosecuted_for_acts_contrary_to_un": base_predicate(
        ["person"], "The person faces a prosecution that genuinely arises from acts contrary to the purposes "
                    "and principles of the United Nations"),
    "entitled_to_asylum": base_predicate(
        ["person"], "The person holds the entitlement to seek and to enjoy asylum from persecution (Article 14, paragraph 1)"),
    "exercises_contrary_to_un": base_predicate(
        ["person", "right"], "The person exercises the right or freedom contrary to the purposes and principles "
                             "of the United Nations"),
    "right_protects_exercise": base_predicate(
        ["person", "right"], "The right or freedom protects the person's exercise of it"),
    "declaration_implies_destructive_right": base_predicate(
        ["bearer"], "This Declaration implies for the bearer a right to engage in any activity or to perform any act "
                    "aimed at the destruction of any of the rights and freedoms set forth in it"),
})
meta["open_terms"].extend(C.NEW_OPEN_TERMS)
env = Environment(meta["environment"])
env_json = meta["environment"]


def data(formula):
    return formula_to_data(env, formula)


# Assertion readings (formulas, checked in this document).
V0, V1 = Var(0), Var(1)
u052_b = Forall("person", Implies(Or(Unary("genuinely_prosecuted_for_non_political_crime", V0),
                                     Unary("genuinely_prosecuted_for_acts_contrary_to_un", V0)),
                                  Not(Unary("entitled_to_asylum", V0))))
u112_b = Forall("person", Forall("right", Implies(Binary("exercises_contrary_to_un", V1, V0),
                                                   Not(Binary("right_protects_exercise", V1, V0)))))
u114_b = Forall("bearer", Not(Unary("declaration_implies_destructive_right", V0)))
ASSERTIONS = {"u052": ("entitlement_withheld", u052_b), "u112": ("scope_limited", u112_b),
              "u114": ("no_implied_right", u114_b)}

# Finite models over the main environment. A reading set needs a model id per other reading; for pairs whose
# other reading is a norm without formula content the tool cannot compare, so the model falsifies the assertion.
def model_data(domains, relations):
    full = {name: [] for name in env.predicates}
    full.update(relations)
    return {"complete": True, "constants": {}, "domains": domains, "relations": full}


DOMAINS = {"actor": ["a"], "person": ["p"], "right": ["r"], "bearer": ["b"]}
MODELS = {
    "empty": model_data(DOMAINS, {}),
    "u052": model_data(DOMAINS, {"genuinely_prosecuted_for_non_political_crime": [["p"]],
                                 "entitled_to_asylum": [["p"]]}),
    "u112": model_data(DOMAINS, {"exercises_contrary_to_un": [["p", "r"]],
                                 "right_protects_exercise": [["p", "r"]]}),
    "u114": model_data(DOMAINS, {"declaration_implies_destructive_right": [["b"]]}),
}
model_ids = {k: FiniteModel.from_dict(env, v).model_id for k, v in MODELS.items()}

# ---------------------------------------------------------------- companion documents (norm-kind candidates)
READINGS.mkdir(exist_ok=True)
all_terms = meta["open_terms"]
companion = {}
for uid, cands in C.COMPANIONS.items():
    a, b = by_id[uid]["span"]
    for cid in cands:
        path = C.write_companion(READINGS, uid, cid, raw[a:b], all_terms)
        verdict = check_document(path)
        loaded = load_document(path)
        companion[(uid, cid)] = {
            "path": str(path.relative_to(HERE)), "meaning_id": loaded["units"][0]["meaning_id"],
            "document_id": verdict["document_id"], "premises": verdict["premises"]["status"],
            "coverage_bytes": verdict["coverage"]["bytes_by_status"], "residual": verdict["coverage"]["residual"],
            "soft": verdict.get("soft"), "loaded": loaded,
        }
        assert verdict["coverage"]["accounted_bytes"] == b - a
        assert verdict["premises"]["status"] == "model"

WHY = {
    ("u017", "strict"): "Article 1 'should' read as a strict obligation on every human being to act towards each other "
                        "human being in a spirit of brotherhood. Elaborated and checked as readings/u017.strict.ve.md "
                        "(W1 rule, obligation-role predicate, deny-completion means 'not required'; no permission "
                        "predicate is declared). The reciprocal 'each other human being' is in the act phrase only.",
    ("u017", "default"): "Article 1 'should' read as a defeasible rule (soft-norms@0): the same obligation holds unless "
                         "the rule's exception applies, and the source names no decider ('unstated'). Elaborated and "
                         "checked as readings/u017.default.ve.md; the exception stays an open decision.",
    ("u052", "invocation_barred"): "Article 14(2) read as a strict prohibition on invoking the asylum right of paragraph 1 "
                                   "in the described prosecutions (conditions carried by the sort prosecuted_person, so no "
                                   "completion is invented for other people). Elaborated and checked as "
                                   "readings/u052.invocation_barred.ve.md.",
    ("u052", "entitlement_withheld"): "Article 14(2) read as withholding the entitlement: whoever faces a prosecution "
                                      "genuinely arising from a non-political crime or from acts contrary to UN purposes and "
                                      "principles is not entitled to asylum. A formula in this document; 'genuinely', "
                                      "'non-political' and 'contrary to UN purposes and principles' are named open terms.",
    ("u112", "exercise_prohibited"): "Article 29(3) read as an unconditional prohibition ('in no case': no carve-out, no "
                                     "precedence) on exercising a declared right or freedom contrary to UN purposes and "
                                     "principles. Elaborated and checked as readings/u112.exercise_prohibited.ve.md.",
    ("u112", "scope_limited"): "Article 29(3) read as limiting the scope of the rights: no right or freedom protects an "
                               "exercise that is contrary to UN purposes and principles. A formula in this document.",
    ("u114", "interpretive_ban"): "Article 30 read as a prohibition on interpreting the Declaration as implying, for any "
                                  "State, group or person, a right to destroy declared rights. Elaborated and checked as "
                                  "readings/u114.interpretive_ban.ve.md.",
    ("u114", "no_implied_right"): "Article 30 read as a statement of the Declaration's content: it implies for no State, "
                                  "group or person a right to engage in any activity or act aimed at destroying any declared "
                                  "right. A formula in this document.",
}

previous_sets = {rs["unit"]: rs for rs in meta["reading_sets"]}  # version 1: null-content candidates, audit-rejected
reading_sets = []
for uid in REPAIRED:
    candidates = []
    ids = list(C.COMPANIONS[uid]) + ([ASSERTIONS[uid][0]] if uid in ASSERTIONS else [])
    for cid in ids:
        if (uid, cid) in companion:
            kind, content, mid = "norm", None, companion[(uid, cid)]["meaning_id"]
        else:
            formula = ASSERTIONS[uid][1]
            kind, content, mid = "asserted", data(formula), meaning_id(env, formula)
        model_key = uid if uid in ASSERTIONS else "empty"
        candidates.append({"id": cid, "kind": kind, "meaning_id": mid, "content": content,
                           "admission": {"who": "translator", "why": WHY[(uid, cid)],
                                         "distinguishing_models": {o: model_ids[model_key] for o in ids if o != cid}}})
    model_key = uid if uid in ASSERTIONS else "empty"
    reading_sets.append({"id": f"rs_{uid}", "unit": uid, "version": 2, "status": "open",
                         "rejected_history": [{"version": 1, "readings": [r["id"] for r in previous_sets[uid]["readings"]],
                                               "reason": "null-content candidates rejected by the 2026-09-29 audit"}],
                         "models": {model_ids[model_key]: MODELS[model_key]},
                         "readings": candidates})
meta["reading_sets"] = reading_sets

UNIT_OPEN = {"u017": ["spirit_of_brotherhood"],
             "u052": ["genuine", "non_political_crime", "contrary_to_un_purposes_and_principles"],
             "u112": ["rights_and_freedoms_set_forth", "contrary_to_un_purposes_and_principles"],
             "u114": ["rights_and_freedoms_set_forth", "aimed_at_destruction_of_rights"]}
for uid in REPAIRED:
    unit = unit_by_id[uid]
    unit["kind"] = "norm"
    unit["meaning"] = {"open": UNIT_OPEN[uid]}

base_units = {u["id"]: u for u in json.loads(front)["units"]}
assert all(unit_by_id[uid] == base_units[uid] for uid in unit_by_id if uid not in REPAIRED), "an unrepaired unit changed"
assert all(by_id[uid]["status"] == old for uid, old in [(u, r["status"]) for u, r in by_id.items() if u not in REPAIRED])

# ---------------------------------------------------------------- write the document and check it
document = HERE / "translation.ve.md"
document.write_bytes(b"---\n" + json.dumps(meta, ensure_ascii=False, sort_keys=True, indent=2).encode()
                     + b"\n---\n" + raw)
doc = load_document(document)
verdict = check_document(document)
cov = coverage(doc)
rendered = render_document(document)
assert doc["source"] == raw
assert cov["source_bytes"] == cov["accounted_bytes"] == len(raw)
assert sum(u["span"][1] - u["span"][0] for u in meta["units"]) == len(raw)
assert [u["span"] for u in meta["units"]] == [r["span"] for r in rows]
assert "must not compel each person to belong to an association" in rendered
(HERE / "rendered.md").write_text(rendered)
(HERE / "readings-rendered.md").write_text("\n\n".join(
    f"## {u}.{c}\n\n" + render_document(HERE / item["path"]) for (u, c), item in sorted(companion.items())) + "\n")

# ---------------------------------------------------------------- witnesses
witnesses = {}


def replayed(env_, premises, conclusion):
    result = prove_entailment(env_, premises, conclusion)
    ok = (result.status == "Found"
          and check_entailment_certificate(env_, premises, conclusion, result.certificate).valid)
    return {"status": result.status, "certificate_replayed": bool(ok)}


# u017: the two candidates give different answers exactly where the exception applies.
strict_doc = companion[("u017", "strict")]["loaded"]["norms"]
soft = companion[("u017", "default")]["loaded"]["soft_document"]
R = "act_in_brotherhood_required"
X = "soft__excepted__brotherhood_default"
required_for_all = Forall("human_being", Unary(R, V0))
witnesses["u017"] = {
    "strict_entails_required_for_every_human_being": replayed(
        strict_doc.env, tuple(f for _, f in strict_doc.premises()), required_for_all),
    "default_entails_required_unless_excepted": replayed(
        soft.elaborated.env, tuple(f for _, f in soft.elaborated.premises()),
        Forall("human_being", Implies(Not(Unary(X, V0)), Unary(R, V0)))),
    "default_entails_not_required_when_excepted": replayed(
        soft.elaborated.env, tuple(f for _, f in soft.elaborated.premises()),
        Forall("human_being", Implies(Unary(X, V0), Not(Unary(R, V0))))),
    "default_does_not_entail_required_for_every_human_being": replayed(
        soft.elaborated.env, tuple(f for _, f in soft.elaborated.premises()), required_for_all),
    "separating_condition": "a human being for whom the exception applies: strict says required, default says not required",
}
assert witnesses["u017"]["strict_entails_required_for_every_human_being"]["certificate_replayed"]
assert witnesses["u017"]["default_entails_required_unless_excepted"]["certificate_replayed"]
assert witnesses["u017"]["default_entails_not_required_when_excepted"]["certificate_replayed"]
assert witnesses["u017"]["default_does_not_entail_required_for_every_human_being"]["status"] != "Found"

# Completion independence: each prohibition is unconditional over its sort, so its declared completion is never
# consulted. Flip the completion and the rule alone still decides; drop the rule and the completion shows.
def variant(source_env_json, rule, default, keep_rule=True):
    e = copy.deepcopy(source_env_json)
    for predicate in e["vocabulary"]["predicates"].values():
        if "regulated" in predicate:
            predicate["regulated"]["default"] = default
    return NormDocument(Environment(e), [NormDocument._decode(rule)] if keep_rule else [])


def completion_report(source_env_json, rule, predicate, sort_names):
    """Same three checks for a unary prohibition (sort_names has one sort) or a binary one (two sorts)."""
    sorts_ = list(sort_names)
    if len(sorts_) == 1:
        concl = Forall(sorts_[0], Not(Unary(predicate, V0)))
    else:
        concl = Forall(sorts_[0], Forall(sorts_[1], Not(Binary(predicate, V1, V0))))
    out = {}
    for default in ("allow", "deny"):
        d = variant(source_env_json, rule, default)
        out[f"rule_kept_completion_{default}"] = replayed(d.env, tuple(f for _, f in d.premises()), concl)
        assert out[f"rule_kept_completion_{default}"]["certificate_replayed"]
    dropped = variant(source_env_json, rule, "allow", keep_rule=False)
    out["rule_dropped_completion_allow"] = replayed(dropped.env, tuple(f for _, f in dropped.premises()), concl)
    assert out["rule_dropped_completion_allow"]["status"] != "Found"
    return out


u074 = unit_by_id["u074"]["content"]
witnesses["u074"] = completion_report(meta["environment"], u074, "compel_association_membership_permitted", ["actor", "person"])
for uid, cid, predicate, sort_name in [("u052", "invocation_barred", "invoke_asylum_right_permitted", "prosecuted_person"),
                                       ("u112", "exercise_prohibited", "contrary_exercise_permitted", "contrary_exercise"),
                                       ("u114", "interpretive_ban", "destructive_interpretation_permitted",
                                        "destructive_interpretation")]:
    profiles, sorts, predicates, rule, _ = C.COMPANIONS[uid][cid]
    companion_env = C.environment(profiles, sorts, predicates)
    witnesses[f"{uid}.{cid}"] = completion_report(companion_env, rule, predicate, [sort_name])
witnesses["u052.entitlement_withheld_is_not_forced_by_the_ban"] = (
    "separated from invocation_barred by vocabulary only: the two readings share no predicate, and relating "
    "'invoke' to 'entitled' needs rights semantics that are not merged")
(HERE / "witnesses.json").write_text(json.dumps(witnesses, ensure_ascii=False, indent=2, sort_keys=True) + "\n")

# ---------------------------------------------------------------- manifest
NOTES = {
    "u017": {"new_feature": "soft-norms@0 (should as a default rule with an open exception)",
             "residual_missing": ["other:norm_reading_candidates_hold_no_content_in_ve-document@1",
                                  "other:pairwise_relation_only_in_act_phrase"]},
    "u052": {"new_feature": None, "residual_missing": ["other:norm_reading_candidates_hold_no_content_in_ve-document@1",
                                                      "norms", "defaults"]},
    "u112": {"new_feature": None, "residual_missing": ["other:norm_reading_candidates_hold_no_content_in_ve-document@1",
                                                      "norms", "defaults"]},
    "u114": {"new_feature": None, "residual_missing": ["other:norm_reading_candidates_hold_no_content_in_ve-document@1",
                                                      "norms", "defaults"]},
}
PROSE = ("The norm candidate is an unconditional prohibition over a sort whose description (prose, not checked structure) "
         "carries the source's conditions; the source states no completion for anyone else, so none is invented. ")
DEPTH = {
    "u017": "Both candidates are formal: an obligation on every human being, strict or with an open exception. 'Each other "
            "human being' sits in the act phrase and 'spirit of brotherhood' is a named open term.",
    "u052": PROSE + "The assertion candidate is fully formal: both grounds, and the negated entitlement.",
    "u112": PROSE + "The assertion candidate is fully formal: no right protects an exercise contrary to UN purposes and principles.",
    "u114": PROSE + "The assertion candidate is fully formal: no bearer has an implied destructive right.",
}
for uid in REPAIRED:
    row = by_id[uid]
    row.pop("audit_gap", None)
    row.pop("audit_disposition", None)
    row["previous_status"] = row["status"]
    row["status"] = "READINGS"
    row["candidates"] = [c["id"] for c in next(rs for rs in reversed(meta["reading_sets"])
                                              if rs["unit"] == uid)["readings"]]
    row["open_terms"] = UNIT_OPEN[uid]
    row["companions"] = [companion[(uid, cid)]["path"] for cid in C.COMPANIONS[uid]]
    row["audit_repair"] = ("Every candidate now has checked content: norm candidates as companion documents, assertion "
                           "candidates as formulas in this document. Pending a fresh independent audit.")
    row["formal_depth"] = DEPTH[uid]
    row["new_feature"] = NOTES[uid]["new_feature"]
    row["residual_missing_features"] = NOTES[uid]["residual_missing"]
assert by_id["u074"]["status"] == "CHECKED"
(HERE / "units.json").write_text(json.dumps({
    "source_sha256": PIN, "units": rows,
    "note": "READINGS units hold an open reading set whose candidates all have checked content (companion documents for "
            "norm-kind candidates, since ve-document@1 reading candidates cannot hold norm content)."},
    ensure_ascii=False, indent=2) + "\n")

counts = Counter(r["status"] for r in rows)
bytes_by_status = Counter()
missing = Counter()
for row in rows:
    bytes_by_status[row["status"]] += row["span"][1] - row["span"][0]
    if row["status"] == "UNFORMALISED":
        missing[row["missing_feature"]] += 1
old_aggregation = Counter()
for children in old_metrics["old_to_new_units"].values():
    statuses = {by_id[uid]["status"] for uid in children}
    old_aggregation[next(iter(statuses)) if len(statuses) == 1 else "MIXED"] += 1

audit_passes = set("u001 u002 u021 u030 u034 u053 u056 u062 u065 u069 u072 u095 u104 u109 u113 u074".split())
audit_bytes = sum(r["span"][1] - r["span"][0] for r in rows if r["id"] in audit_passes)
assert audit_bytes == 303
COVERED = ("CHECKED", "LABELLED", "OPEN", "READINGS")
claimed = sum(bytes_by_status[s] for s in COVERED)
repaired_bytes = sum(by_id[u]["span"][1] - by_id[u]["span"][0] for u in REPAIRED)
metrics = {
    "source": {"path": "source/udhr.md", "sha256": PIN, "bytes": len(raw), "fetch_date_utc": "2026-09-27"},
    "baseline": "ve-green-flaky4",
    "previous_run": "run-20260929T0600Z (ve-green-w6a); copied unchanged into base/",
    "features_merged_since_previous_baseline": ["soft-norms@0", "speech-acts@0 (commands and questions; not applicable)",
                                                "gates and use cases (no language change)"],
    "old_unit_count": old_metrics["old_unit_count"],
    "old_boundary_aggregation": dict(sorted(old_aggregation.items())),
    "old_to_new_units": old_metrics["old_to_new_units"],
    "unit_scale": "sentence or clause; coordinated regulated acts split; headings separate (unchanged from the previous run)",
    "bytes_accounted": cov["accounted_bytes"], "bytes_accounted_percent": cov["coverage_percent"],
    "unit_count": len(rows),
    "unit_counts_by_status": dict(sorted(counts.items())),
    "bytes_by_status": dict(sorted(bytes_by_status.items())),
    "claimed_covered_bytes": claimed, "claimed_covered_percent": round(100 * claimed / len(raw), 2),
    "claimed_covered_bytes_previous_run": 592,
    "claimed_covered_bytes_excluding_prose_scoped_norm_candidates": claimed - sum(by_id[u]["span"][1] - by_id[u]["span"][0] for u in ("u052", "u112", "u114")),
    "prose_scoped_units": ["u052", "u112", "u114"],
    "tool_status_bytes": cov["bytes_by_status"],
    "audit_verified_covered_bytes": audit_bytes,
    "audit_verified_covered_percent": round(100 * audit_bytes / len(raw), 2),
    "audit_verified_substantive_bytes": 57,
    "audit_pending_bytes": repaired_bytes,
    "audit_rejected_units_repaired": REPAIRED,
    "newly_covered_by_merged_features": ["u017"],
    "repaired_with_features_already_present_at_w6a": ["u052", "u112", "u114"],
    "open_terms": [{k: item[k] for k in ("name", "decided_by", "necessary", "sufficient", "factors")}
                   for item in meta["open_terms"]],
    "reading_sets": [{"id": rs["id"], "unit": rs["unit"], "version": rs["version"],
                      "candidates": [{"id": r["id"], "kind": r["kind"], "formula_in_document": r["content"] is not None,
                                      "companion": next((v["path"] for (u, c), v in companion.items()
                                                        if u == rs["unit"] and c == r["id"]), None)}
                                     for r in rs["readings"]]}
                     for rs in meta["reading_sets"] if rs["version"] == 2],
    "missing_feature_tally": dict(sorted(missing.items())),
    "residual_missing_feature_tally_for_readings_units": dict(sorted(Counter(
        f for r in rows if r["status"] == "READINGS" for f in r["residual_missing_features"]).items())),
    "no_invented_permissions": {
        "u074": "unconditional prohibition over every actor and person; its declared completion 'allow' is never consulted "
                "(witnesses.json: the same conclusion under 'deny'; dropping the rule loses it)",
        "u017": "obligation-role predicates only; 'deny' completion means 'not required'; no permission predicate is declared, "
                "so nothing is permitted or forbidden for anyone",
        "u052/u112/u114": "each prohibition is scoped by a sort that names exactly the people or acts the source names, "
                          "so the completion is never consulted (witnesses.json); the cost is that the conditions sit in the "
                          "sort description as prose",
        "language_gap": "defaults: a conditional prohibition cannot leave the complement unspecified, because every "
                        "regulated predicate needs a completion; scoping by sort is the only workaround"},
    "presupposition_check": "No heading, speaker marker or transition presupposes a substantive claim (title, Preamble, "
                            "Article headings, 'The General Assembly,', 'Now, therefore,'); the labelled units are unchanged.",
    "english_vocabulary_lint": [f"{i.path}: {i.code}" for i in lint_english_vocabulary(env)],
    "english_rendering_note": "The three assertion readings render with predicate identifiers ('classified as ...'): the wordings tried "
                              "were rejected by the English vocabulary lint, which allows only a one-word unary complement or an article-free binary verb, and "
                              "rejects 'the', 'for', 'and' and 'or' inside a predicate wording.",
    "companions": {f"{u}.{c}": {k: v for k, v in item.items() if k != "loaded"} for (u, c), item in companion.items()},
    "check_verdicts": {
        "document_load": "PASS", "byte_partition": "PASS", "document_check": "PASS",
        "premises": verdict["premises"], "reading_plan_route": verdict["reading_plan"]["route"],
        "formal_norm_units": sum(type(u["content"]) is dict and "norm" in u["content"] for u in doc["units"]),
        "companion_documents": {f"{u}.{c}": "PASS (premises: model)" for (u, c) in companion},
        "u017_reading_separation": "PASS (certificates replayed)",
        "completion_independence": "PASS for u074 and the three prohibition companions",
        "render": "PASS",
        "ve_natural": "document norm renderer used; full natural view does not round-trip W1 norm blocks",
    },
    "document_id": verdict["document_id"], "source_id": verdict["source_id"],
    "coverage_tool": cov,
}
(HERE / "metrics.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({"units": len(rows), "statuses": dict(counts), "old_aggregation": dict(old_aggregation),
                  "claimed": claimed, "premises": verdict["premises"], "plan": verdict["reading_plan"]["route"],
                  "tool_status_bytes": cov["bytes_by_status"]}, ensure_ascii=False))
