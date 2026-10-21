"""Write units.json and metrics.json for the 2026-10-17T1800Z run (language at ve-green-fu-ar2-decoders). Nothing here calls a model.

    uv run --frozen python usecases/udhr-pilot/run-20261017T1800Z/finish21.py

The run carries the previous run's translation (run-20261017T0600Z, kept in previous-20261017T0600Z/) and repairs what its audit
found: u037 was UNFAITHFUL (a reading missing: the scope of "arbitrary" over "arrest, detention or exile") and the audit named u027
as having the same structure (repair15_specs.py). No feature upgrade (no product file changed since the previous tag) and no plan
repair (the carried u097, u085, u091, u106 repairs stand). Inputs: this run's saved check results.
"""
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
import repair15_specs as R  # noqa: E402

PREV = HERE / "previous-20261017T0600Z"
m = json.loads((PREV / "metrics.json").read_text())
ud = json.loads((PREV / "units.json").read_text())
pc = json.loads((HERE / "parts-check.json").read_text())
parts = json.loads((HERE / "parts.json").read_text())
wit = json.loads((HERE / "witnesses.json").read_text())["norm_defaults_status"]
comp = json.loads((HERE / "companions-check.json").read_text())
refusal = json.loads((HERE / "refusal-test.json").read_text())
whole = json.loads((HERE / "experiment-whole" / "whole-check.json").read_text())
legacy_cov = json.loads((HERE / "coverage.json").read_text())["coverage"]
legacy_ver = json.loads((HERE / "verdict.json").read_text())["report"]
iso = json.loads((HERE / "qt0p-isolated.json").read_text())
compare = json.loads((HERE / "unit-compare.json").read_text())
w15 = json.loads((HERE / "witnesses_repaired15.json").read_text())
OLD, TAG = "ve-green-rights-licence-relay", "ve-green-fu-ar2-decoders"
CHANGED = sorted(R.ORDER)                                  # u027, u037
assert not compare["unexpected"] and sorted(d["unit"] for d in compare["differences"]) == CHANGED
for n, v in pc.items():
    assert "error" not in v and v["premises"]["status"] == "model" and v["conflict"] in (None, "CONFLICT-FREE"), (n, v)   # part03 holds no reading set
assert whole["load"]["coverage_percent"] == 100 and whole["check"]["premises"] == "model"

# ---------------------------------------------------------------- units.json
units = {u["id"]: u for u in ud["units"]}
FORMAL = ("2 candidates ({cands}), each stated in the part document translation-part01.ve.md as content (norm-defaults@0, completion "
          "'unspecified'; a rule over a plain property is stated as the assertion that the property holds of every case its guard picks "
          "out), in one reading set whose separating situations Lean admitted; each candidate also stands as a one-unit companion "
          "document with Lean status witnesses (a case inside the rule is SETTLED, a case outside it UNDECIDED, never 'not required' and "
          "never permitted). No candidate names a bearer the words do not name.")
for uid in CHANGED:
    u = units[uid]
    order = R.ORDER[uid]
    u["status"] = "READINGS"
    u["reading_set"] = f"rs_{uid}"
    u["candidates"] = list(order)
    u["companions"] = [f"readings/{uid}.{c}.ve.md" for c in order]
    u["norm_defaults_companions"] = list(u["companions"])
    u["formal_depth"] = FORMAL.format(cands=", ".join(order))
    u["words_only_single_reading"] = False
    u.pop("single_reading", None)
    u["status_in_previous_run"] = "OPEN"
    u["previous_status_in_run_20261017T0600Z"] = "OPEN"
    u["ledger_repair_20261017T1800Z"] = R.REASON[uid]
    u["audit_repair_20261017T1800Z"] = ("repaired 2026-10-17T1800Z (repair15.py): " + R.REASON[uid] +
                                        "; the old single candidate `prohibited` is replaced by the two candidates, no trace of it is left; "
                                        "pending a fresh independent audit")
    u["audit_20261017T0600Z"] = ("UNFAITHFUL (repaired in this run)" if uid in R.AUDIT_REJECTED else
                                 "not sampled; named by the audit as having u037's structure; re-expressed in this run, waits for an audit")
ud["audit_note_20261017T1800Z"] = ("this run repairs u037 (rejected by the 20261017T0600Z audit: the scope of 'arbitrary' over 'arrest, detention or exile' "
                                   "had one reading) and u027 (named by the same audit: the scope of 'cruel, inhuman or degrading' over 'treatment or "
                                   "punishment'); both are now reading sets of two norm candidates and wait for a fresh audit")
(HERE / "units.json").write_text(json.dumps(ud, indent=1, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------- numbers from the ledger
rows = ud["units"]
span = lambda u: u["span"][1] - u["span"][0]
COVERED = ("CHECKED", "LABELLED", "OPEN", "READINGS")
counts = Counter(u["status"] for u in rows)
bytes_by = Counter()
for u in rows:
    bytes_by[u["status"]] += span(u)
assert sum(bytes_by.values()) == 10916 and len(rows) == 130
claimed = sum(span(u) for u in rows if u["status"] in COVERED and u.get("claimed", True))
verified_prev = set(m["audit_verified_units"])
verified = (verified_prev - set(CHANGED)) | {"u098"}
byid = {u["id"]: u for u in rows}
assert all(byid[i]["status"] in COVERED and byid[i].get("claimed", True) for i in verified)
verified_bytes = sum(span(byid[i]) for i in verified)
pending = ["u110", *CHANGED]
pending_bytes = sum(span(byid[i]) for i in pending)
print("counts", dict(counts), "bytes", dict(bytes_by), "claimed", claimed, "verified", verified_bytes, "pending", pending_bytes)

# ---------------------------------------------------------------- metrics.json
def swap(x):
    if isinstance(x, str):
        return x.replace(OLD, TAG)
    if isinstance(x, list):
        return [swap(i) for i in x]
    if isinstance(x, dict):
        return {k: swap(v) for k, v in x.items()}
    return x

old_m = m
m = swap(m)
m["run"] = "run-20261017T1800Z"
m["previous_run"] = ("run-20261017T0600Z (ve-green-rights-licence-relay); its parts, units, readings and metrics are in previous-20261017T0600Z/ "
                     "(earlier runs' copies: previous-20261013T0600Z/)")
m["previous_baseline"] = OLD
m["baseline"] = TAG
m["features_merged_since_previous_baseline"] = [
    "none a translator can write. The merges since ve-green-rights-licence-relay are fu-premise-f9 (a test: a timeout in the lifted choices' searches alone "
    "is CheckerUnavailable) and fu-ar2-decoders (a DECODERS completeness test and the widest-trusted-line rule of tools/trust_changes.py). "
    "`git diff ve-green-rights-licence-relay HEAD -- ve lean rust` is empty: no product file changed, so no construct, profile or sentence form is new."]
m["feature_upgrades"] = {"bytes": 0, "count": 0, "note": "no newly merged feature lets any UNFORMALISED unit move", "units": []}
m["plan_repairs"] = []
m["plan_repairs_note"] = ("none this run; the earlier plan repairs (u097 QT-0p, u085, u091, u106 AP-0 item 1; u039 not landed) are carried in the parts, "
                          "unchanged (plan_repairs_in_carried_state); QT-0p's preconditions hold (u097's span is 8857-8933, part03 is byte-identical to the previous run's)")
m["changed_units"] = CHANGED
m["units_changed_this_run"] = CHANGED
m["repaired_units"] = CHANGED
m["repaired_unit_reasons"] = {u: R.REASON[u] for u in CHANGED}
m["audit_repairs"] = [{"audit": "20261017T0600Z", "unit": u, "reason": R.REASON[u]} for u in CHANGED]
m["audit_repairs_previous_run"] = old_m["audit_repairs"]
m["units_rejected_by_audit_and_repaired"] = list(R.AUDIT_REJECTED)
m["units_repaired_same_defect_not_rejected"] = list(R.NAMED_BY_AUDIT)
m["unit_counts_by_status"] = dict(sorted(counts.items()))
m["previous_run_unit_counts_by_status"] = old_m["unit_counts_by_status"]
m["bytes_by_status"] = dict(sorted(bytes_by.items()))
m["unit_counts_by_status_change"] = {"audit_repairs": {"bytes": sum(span(byid[u]) for u in CHANGED), "units": len(CHANGED),
                                                       "moves": "u027 and u037: OPEN -> READINGS (one reading -> two)"},
                                     "feature_upgrades": {"bytes": 0, "units": 0}, "plan_repairs": {"bytes": 0, "units": 0}}
m["claimed_covered_bytes_previous_run"] = old_m["claimed_covered_bytes"]
m["claimed_covered_bytes_previous_run_under_x5"] = old_m["claimed_covered_bytes"]
m["claimed_covered_bytes"] = claimed
m["claimed_covered_percent"] = round(100 * claimed / 10916, 2)
m["claimed_change_vs_previous_run_bytes"] = claimed - old_m["claimed_covered_bytes"]
m["claimed_change_vs_previous_run_bytes_under_x5"] = claimed - old_m["claimed_covered_bytes"]
m["audit_verified_units"] = sorted(verified, key=lambda i: [u["id"] for u in rows].index(i))
m["audit_verified_units_form_unchanged"] = [i for i in m["audit_verified_units"]]
m["audit_verified_units_reexpressed_this_run"] = []
m["audit_verified_units_withdrawn_this_run"] = {"u037": "rejected by the 20261017T0600Z audit; repaired this run, waits for a fresh audit",
                                                 "u027": "judged FAITHFUL before, but re-expressed this run (two readings), so it is not verified until re-audited"}
m["previous_run_audit_verified_covered_bytes"] = old_m["audit_verified_covered_bytes"]
m["audit_verified_covered_bytes"] = verified_bytes
m["audit_verified_covered_percent"] = round(100 * verified_bytes / 10916, 2)
m["audit_verified_note"] = ("verified = judged FAITHFUL by an audit and not changed since, and not marked claimed:false. The 20261017T0600Z audit "
                            "judged u098 FAITHFUL (first audit since its repair), so it joins the verified set (+42 B); u037 (rejected, 68 B) and u027 "
                            "(97 B, re-expressed) leave it, so the net is " + f"{verified_bytes - old_m['audit_verified_covered_bytes']:+d} B" +
                            f" ({old_m['audit_verified_covered_bytes']:,} -> {verified_bytes:,} B). Under X5, u035 and u111 never count.")
m["audit_pending_units"] = pending
m["audit_pending_bytes"] = pending_bytes
m["audit_newly_verified_units"] = ["u098"]
m["audit_newly_verified_units_note"] = "u098 was judged FAITHFUL by the 20261017T0600Z audit and is unchanged since"
m["audit_20261017T0600Z"] = {"file": "AUDIT.md (the 20261017T0600Z audit, carried as written; its preface says the auditor could not write the file)",
                             "sampled": 20, "faithful": 19, "changed_units_checked": 2, "changed_units_faithful": ["u052", "u114"],
                             "unfaithful": ["u037"],
                             "u037": "a reading is missing: 'arbitrary' can cover arrest, detention and exile, or 'arrest' alone; the run gave only the wide one. "
                                     "Repaired this run (repair15.py): two candidates arbitrary_over_all and arbitrary_arrest_only",
                             "u027": "not sampled; the audit says it has u037's structure ('cruel, inhuman or degrading' over 'treatment or punishment'); "
                                     "given the same repair (adjectives_over_both, adjectives_treatment_only)",
                             "note": "audit text read from previous-20261017T0600Z/AUDIT.md; the covered status of u037 is not claimed as verified until a fresh audit"}
m["audit_20261017T0600Z_units_faithful"] = ["u002", "u011", "u021", "u022c", "u028", "u038", "u048", "u050", "u072", "u074", "u075", "u083", "u085",
                                            "u088", "u090", "u098", "u099a", "u105c", "u113", "u052", "u114"]
m["audit_20261017T0600Z_units_unfaithful"] = ["u037"]
m["audit_20261017T0600Z_top_missing_features"] = [
    "the checker finds the scope of a modifier over a list itself ('arbitrary', 'peaceful', 'freely', 'within the borders of each state'); the translator decides today",
    "checked references and scoped limitations ('this right', the ellipses, 'rights and freedoms set forth herein'; 9 of 10 substantive units audited are limited by u019, u108, u111, u112, u114 and none of those links is checked)",
    "plain-English rendering of norms (9 of 10 substantive units audited render only as 'The passage is recorded as a rule')"]
m["language_change_for_udhr"] = ("none for what a translator can write: no construct was added (no ve/, lean/ or rust/ file changed). The two repaired units use constructs the "
                                 "language already had (a reading set of two norm candidates over one regulated act, as u055's). The other 128 units load with the same status and row.")
m["language_findings"] = [
    f"NO NEW TRANSLATION CAPABILITY for the UDHR at {TAG}: the merges since the last run are two tests and a trust-tool rule. The 42 UNFORMALISED units keep the blockers they had.",
    "audit repair: the scope of a modifier over a list is a reading the English admits, and VE can state it only because the translator writes both candidates; the audit's top missing feature "
    "(the checker finds the scope readings itself) is why u037 and u027 were uneven in earlier runs. The separating situation of u037 is a detention that is not arbitrary (the wide reading leaves it UNDECIDED, "
    "the narrow one forbids it); of u027 a punishment that is not cruel, inhuman or degrading (same). Lean admitted both situations at load time.",
    "the four parts load and check at the new tag (premises 'model', CONFLICT-FREE under every reading; part01 now has 8 choices and checks in "
    f"{pc['translation-part01.ve.md']['seconds']} s, was 6 s with 2 choices; parts 02-04 are byte-identical to the previous run's)",
    f"the whole declaration as ONE document (experiment-whole/translation-whole.ve.md; u027 and u037 join u025, u055, u073, u111 as RD-4b components, six components) LOADS in {whole['load']['seconds']} s "
    f"at {whole['load']['coverage_percent']}% coverage and CHECKS in {whole['check']['seconds']} s with readings {whole['check']['readings_status']} and premises '{whole['check']['premises']}' "
    "(previous run: 668.1 s and 732.0 s; two more components cost 95 s to load and 431 s to check). Default Rust limit kept; no prlimit run, so no raised limit and no peak resident-set record.",
    "the whole declaration with every candidate in the main document (integrate.py u001 u114) was not re-run this run (earlier result: Python's one-element search finds no separating situation for u111's pair)",
    "the natural view still shows a norm as 'The passage is recorded as a rule' (the legacy rendered.md gains one 'Another reading is: ...' line for each of the two new reading sets)"]
m["not_done_this_run"] = ["no blind audit of this run (the orchestrator audits); no seeded bug in product code (no product file under ve/, lean/ or rust/ was changed; see seeded-bugs.md)"]
m["reading_set_count"] = sum(1 for u in rows if u["status"] == "READINGS")
m["reading_set_candidates"] = sum(len(u["candidates"]) for u in rows if u["status"] == "READINGS")
m["previous_run_reading_set_count"] = old_m["reading_set_count"]
m["previous_run_reading_set_candidates"] = old_m["reading_set_candidates"]
m["reading_sets_multi_candidate"] = sorted(set(old_m["reading_sets_multi_candidate"]) | set(CHANGED))
m["reading_sets_changed_this_run"] = {u: {"before": ["prohibited"], "after": list(R.ORDER[u])} for u in CHANGED}
m["single_reading_units"] = [u for u in old_m["single_reading_units"] if u not in CHANGED]
m["single_reading_unit_count"] = len(m["single_reading_units"])
m["old_boundary_aggregation"] = dict(old_m["old_boundary_aggregation"], OPEN=old_m["old_boundary_aggregation"]["OPEN"] - 2,
                                     READINGS=old_m["old_boundary_aggregation"]["READINGS"] + 2)
m["previous_run_old_boundary_aggregation"] = old_m["old_boundary_aggregation"]
assert all(old_m["old_to_new_units"][u] == [u] for u in CHANGED)
m["words_only"] = {"rule": old_m["words_only"]["rule"], "readings_added_this_run": {u: list(R.ORDER[u]) for u in CHANGED},
                   "readings_removed_this_run": {u: ["prohibited"] for u in CHANGED}, "readings_changed_this_run": {},
                   "open_questions_listed_that_the_text_does_not_raise": 0,
                   "note": ("both new readings per unit are readings of the word order only: the modifier ('arbitrary'; 'cruel, inhuman or degrading') stands before all the "
                            "listed nouns or before the first noun alone. No reading comes from outside knowledge (no treaty practice, no legal convention); the explicitly "
                            "listed items (arrest, detention, exile; treatment, punishment) stay as checked structure; the open terms `arbitrary` and `ill_treatment` are the "
                            "ones the units already had. In the narrow readings a detention, an exile or a punishment is barred whether or not the modifier applies, which "
                            "is what the words, read that way, say")}
m["presupposition_check"] = m["presupposition_check"].replace("no unit changed this run, so the labelled units are the audited previous run's",
                                                              "no heading or label changed this run (the two changed units, u027 and u037, are norms), so the labelled units are the audited previous run's")
m["part_checks"] = {n: {"seconds": v["seconds"], "premises": v["premises"], "readings_status": v["readings_status"], "conflict": v["conflict"],
                        "coverage_bytes_by_status": v["coverage"]["bytes_by_status"], "residual": v["coverage"]["residual"],
                        "document_id": v["document_id"]} for n, v in pc.items()}
m["document_ids"] = {n: v["document_id"] for n, v in pc.items()}
m["parts"] = parts
m["whole_document_legacy"]["coverage"] = legacy_cov
m["whole_document_legacy"]["premises"] = legacy_ver["premises"]
m["whole_document_legacy"]["reading_plan_route"] = legacy_ver["reading_plan"]["route"]
m["companion_documents"] = len(comp)
m["status_witnesses"] = wit
m["status_witness_rows"] = sum(len(v) for v in wit.values())
m["no_invented_permissions"]["status_rows"] = f"{m['status_witness_rows']} Lean status rows over {len(comp)} companions, all as expected"
m["qt0p_u097"]["isolated_measurement"] = iso
m["qt0p_u097"]["in_this_run"]["note"] = (f"carried unchanged; the isolated measurement (qt0p_isolated.py) and the probe rows were re-run at {TAG} and give the same result "
                                         "(part03 OPEN +76 B, premises `model`); part03 is byte-identical to the previous run's")
m["rendering_change"] = {"what": "the legacy rendered.md gains one 'Another reading is: The passage is recorded as a rule.' line for each of the two new sets; rendered-parts/ for parts 02-04 are unchanged; "
                                 "readings-rendered.md and witnesses.json have the new companions", "verdict": "no change in how norms are worded"}
m["vocabulary_change_check"]["result"] = {k: compare[k] for k in ("differences", "environment_changed_in", "unexpected", "units")}
m["vocabulary_change_check"]["result"]["note"] = ("no vocabulary change: the two new candidates per unit reuse the existing sorts, predicates and open terms (only the guard differs); "
                                                  "the situation step (integrate.py all), witnesses_all.py and compare_units.py were re-run, parts 02-04 are byte-identical, "
                                                  "and every unit of part 01 other than u027 and u037 parses unchanged")
m["vocabulary_change_check"]["rust_time_limit"] = "default VE_RUST_TIMEOUT kept (5 s); no prlimit run, so no raised limit and no peak resident-set record"
m["whole_document_experiment"]["components"] = {"load": whole["load"], "check": whole["check"]}
m["whole_document_experiment"]["component_sets"] = ["u025", "u027", "u037", "u055", "u073", "u111"]
m["whole_document_experiment"]["result"] = "loads and checks at " + TAG
ch = m["checks"]
ch["companions"] = f"PASS: {len(comp)} companions check (premises model) and {m['status_witness_rows']} Lean status rows as expected (re-run at {TAG})"
ch["legacy_document"] = {"check_seconds": 0.2, "coverage": "PASS (100%)", "premises": legacy_ver["premises"]}
ch["parts"] = (f"PASS: ve document check on all 4 parts at {TAG}: premises 'model' for every choice, CONFLICT-FREE under every reading; parts 02-04 are byte-identical to the previous run's, "
               "part 01 differs only in the two new reading sets (u027, u037)")
ch["unchanged_units"] = ("PASS: 128 of 130 units have the same status and the same row in the part files; the two that differ are exactly the repaired units u027 and u037 "
                         "(loader status OPEN before and after: a unit with a reading set shows OPEN; the ledger status is READINGS)")
ch["wrong_separating_situation"] = {"result": refusal["result"], "set": refusal["set"]}
ch["whole_document"] = {"check_seconds": whole["check"]["seconds"], "coverage_percent": whole["load"]["coverage_percent"], "load_seconds": whole["load"]["seconds"],
                        "premises": whole["check"]["premises"], "readings_status": whole["check"]["readings_status"], "tag": TAG}
ch["repaired_units"] = {"companions_written": {k: [o["lean_point_status"] for o in v] for k, v in w15.items()},
                        "separating_situations": "found by integrate.py's search over Lean's filled document and admitted by Lean at load (part01: no missing, no limit)"}
lim = ch["limits_met"]
lim[1] = (f"the whole declaration as ONE document (experiment-whole/): six two-reading sets with their own vocabulary as RD-4b components (u025, u027, u037, u055, u073, u111) and the rest in the "
          f"main component, built by whole.py; at {TAG} load_document succeeds after {whole['load']['seconds']} s (coverage {whole['load']['coverage_percent']}%) and check_document answers "
          f"{whole['check']['readings_status']}, premises '{whole['check']['premises']}' after {whole['check']['seconds']} s (experiment-whole/whole-check.json)")
(HERE / "metrics.json").write_text(json.dumps(m, indent=1, ensure_ascii=False, sort_keys=True) + "\n")
print("ok", {k: v["seconds"] for k, v in pc.items()}, whole)
