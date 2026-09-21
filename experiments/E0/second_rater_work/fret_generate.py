#!/usr/bin/env python3
"""Generate the blind E0 second-rater record for the FRET sample."""
import json
import sys
from pathlib import Path

sys.path.insert(0, "/private/tmp/ve-e0-integration")
import ve

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "survey_samples" / "_drawn" / "fret.json"
OUT = Path(__file__).with_name("fret.jsonl")
FRET_SOURCE = Path("/Users/seyran/code/ve-claude/data/fret")


def authoritative_semantics():
    result = {}
    for filename in ("LM_requirements.json", "LM_reqts_and_vars.json",
                     "LPC_full_reqts_and_vars.json", "fsm_reqts_and_vars.json"):
        data = json.loads((FRET_SOURCE / filename).read_text())
        for req in data["requirements"]:
            sem = req["semantics"]
            result[(filename, req["reqid"])] = {
                "description": sem["description"], "ft": sem["ft"], "pt": sem["pt"]}
    return result


def env(sorts, predicates):
    return {
        "language": "ve.core@0", "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20",
        "vocabulary": {
            "sorts": {s: {"description": d} for s, d in sorts.items()},
            "predicates": {p: {"arguments": a, "description": d}
                           for p, (a, d) in predicates.items()},
            "constants": {},
        },
    }


TIME = {"timepoint": "A snapshot in the requirement trace."}
NONEMPTY_TRACE = "there exists timepoint t, (true).\n"


def always_imp(ante, cons):
    return f"for every timepoint t, (if ({ante}), then ({cons})).\n"


def unary_fit(preds, source, reification):
    e = env(TIME, {p: (["timepoint"], d) for p, d in preds.items()})
    return e, NONEMPTY_TRACE + source, reification


def onset_immediate_fit(component):
    e = env(TIME, {
        "initial": (["timepoint"], "The unique first snapshot of the execution interval."),
        "previous": (["timepoint", "timepoint"], "The first snapshot is the immediate predecessor of the second."),
        "emergency_button": (["timepoint"], "emergency_button is true at this snapshot."),
        component: (["timepoint"], f"{component} is on at this snapshot."),
    })
    axioms = (
        "there exists timepoint i, (i is initial).\n"
        "for every timepoint i, (for every timepoint j, (if ((i is initial) and (j is initial)), then (i equals j))).\n"
        "for every timepoint p, (for every timepoint t, (for every timepoint q, (if ((p previous t) and (q previous t)), then (p equals q)))).\n"
        "for every timepoint p, (for every timepoint t, (for every timepoint u, (if ((p previous t) and (p previous u)), then (t equals u)))).\n"
        "for every timepoint i, (if (i is initial), then (not (there exists timepoint p, (p previous i)))).\n"
        "for every timepoint t, (if (not (t is initial)), then (there exists timepoint p, (p previous t))).\n"
    )
    trigger = "((t is initial) and (t is emergency_button)) or ((t is emergency_button) and (there exists timepoint p, ((p previous t) and (not (p is emergency_button)))))"
    source = axioms + always_imp(trigger, f"not (t is {component})")
    reif = "Trace-adapter semantics: initial is the unique first snapshot and previous is the immediate-predecessor relation. The trigger is emergency_button true initially or a false-to-true onset; 'immediately' requires the response at that same snapshot. The adapter must supply the complete finite or infinite execution interval; a finite VE model represents only a finite execution."
    return e, source, reif


fits = {}
fits["LM_requirements.json:LM_requirements:FSM-006:c829eaa4"] = unary_fit(
    {"state_ap_maneuver": "FSM_Autopilot state equals ap_maneuver_state at this snapshot.",
     "standby": "standby is true at this snapshot.", "good": "good is true at this snapshot.",
     "state_ap_standby": "FSM_Autopilot STATE equals ap_standby_state at this snapshot."},
    always_imp("((t is state_ap_maneuver) and (t is standby)) and (t is good)", "t is state_ap_standby"),
    "Trace-adapter semantics: sort timepoint is exactly the snapshots of one trace; each unary predicate records the named Boolean or enum equality at that snapshot. 'Always' quantifies over every snapshot." )

for ident, component in [
    ("LM_reqts_and_vars.json:Liquid_mixer:LM-010:e9f62fc0", "valve_1"),
    ("LM_reqts_and_vars.json:Liquid_mixer:LM-012:e9f4f740", "stirring_motor"),
    ("LM_reqts_and_vars.json:Liquid_mixer:LM-009:e9f8a0c1", "valve_0"),
]:
    fits[ident] = onset_immediate_fit(component)

fits["fsm_reqts_and_vars.json:FSM:FSM-011:973568c0"] = unary_fit(
    {"sen_nominal": "senstate equals sen_nominal_state at this snapshot.",
     "request": "request is true at this snapshot.",
     "sen_transition": "SENSTATE equals sen_transition_state at this snapshot."},
    always_imp("(t is sen_nominal) and (not (t is request))", "t is sen_transition"),
    "Trace-adapter semantics: timepoint is exactly the trace snapshots and predicates reify the stated Boolean/enum observations; 'always' ranges over them all.")

fits["LPC_full_reqts_and_vars.json:LPC:LPC_REARPROP:79b85960"] = unary_fit(
    {"rearprop": "rearprop is true at this snapshot.",
     "hover_control_mode": "hover_control_mode is true at this snapshot."},
    "for every timepoint t, (((t is rearprop) or (t is hover_control_mode)) and (not ((t is rearprop) and (t is hover_control_mode)))).\n",
    "Trace-adapter semantics: timepoint enumerates every trace snapshot; the formula expands xor as exactly one of the two Boolean observations at each snapshot.")


def until_fit():
    e = env(TIME, {
        "before": (["timepoint", "timepoint"], "Strict temporal order of snapshots in one discrete linear trace."),
        "previous": (["timepoint", "timepoint"], "The first snapshot is the immediate predecessor of the second."),
        "initial": (["timepoint"], "The unique first snapshot of the execution interval."),
        "start": (["timepoint"], "timer_60sec_expire is true at this snapshot."),
        "stop": (["timepoint"], "timer_120sec_expire or emergency_button occurs at this snapshot."),
        "valve_2": (["timepoint"], "valve_2 is on at this snapshot."),
    })
    axioms = (
      "there exists timepoint i, (i is initial).\n"
      "for every timepoint i, (for every timepoint j, (if ((i is initial) and (j is initial)), then (i equals j))).\n"
      "for every timepoint p, (for every timepoint t, (for every timepoint q, (if ((p previous t) and (q previous t)), then (p equals q)))).\n"
      "for every timepoint p, (for every timepoint t, (for every timepoint u, (if ((p previous t) and (p previous u)), then (t equals u)))).\n"
      "for every timepoint i, (if (i is initial), then (not (there exists timepoint p, (p previous i)))).\n"
      "for every timepoint t, (if (not (t is initial)), then (there exists timepoint p, (p previous t))).\n"
      "for every timepoint p, (for every timepoint t, (if (p previous t), then (p before t))).\n"
      "for every timepoint a, (not (a before a)).\n"
      "for every timepoint a, (for every timepoint b, (if (not (a equals b)), then ((a before b) or (b before a)))).\n"
      "for every timepoint a, (for every timepoint b, (for every timepoint c, (if ((a before b) and (b before c)), then (a before c)))).\n"
    )
    trigger = "((s is initial) and (s is start)) or ((s is start) and (there exists timepoint p, ((p previous s) and (not (p is start)))))"
    req = f"for every timepoint s, (if ({trigger}), then (for every timepoint t, (if (((s equals t) or (s before t)) and (not (there exists timepoint u, (((s equals u) or (s before u)) and (((u equals t) or (u before t)) and (u is stop)))))), then (t is valve_2)))).\n"
    return e, axioms + req, "Trace-adapter semantics: initial/previous detect the first true point and false-to-true onsets of timer_60sec_expire. before is constrained as a strict total order. valve_2 holds from each trigger until, but not at, the first stopping snapshot; if no stop occurs it holds through the complete remaining execution interval, so this is FRET's weak-until behavior. The adapter must supply the complete finite or infinite interval."

fits["LM_reqts_and_vars.json:Liquid_mixer:LM-008:e9f8a0c0"] = until_fit()


def within_fit(n):
    e = env(TIME, {
        "initial": (["timepoint"], "The initial snapshot at which this unscoped requirement begins."),
        "next_tick": (["timepoint", "timepoint"], "The second snapshot is exactly one tick after the first."),
        "thrust_borne": (["timepoint"], "lift_mode equals thrust_borne at this snapshot."),
        "terminal": (["timepoint"], "The last snapshot of a finite execution interval."),
    })
    # A path of length k witnesses satisfaction k ticks after the initial snapshot.
    choices = ["s is thrust_borne"]
    for k in range(1, n + 1):
        body = f"t{k} is thrust_borne"
        for j in range(k, 0, -1):
            left = "s" if j == 1 else f"t{j-1}"
            body = f"({left} next_tick t{j}) and ({body})"
            body = f"there exists timepoint t{j}, ({body})"
        choices.append(body)
    # FRET permits an interval ending before the deadline without a response.
    terminal_choices = ["s is terminal"]
    for k in range(1, n):
        body = f"e{k} is terminal"
        for j in range(k, 0, -1):
            left = "s" if j == 1 else f"e{j-1}"
            body = f"({left} next_tick e{j}) and ({body})"
            body = f"there exists timepoint e{j}, ({body})"
        terminal_choices.append(body)
    choices.extend(terminal_choices)
    def balanced_or(parts):
        if len(parts) == 1:
            return parts[0]
        mid = len(parts) // 2
        return f"({balanced_or(parts[:mid])}) or ({balanced_or(parts[mid:])})"
    disj = balanced_or(choices)
    axioms = (
        "there exists timepoint i, (i is initial).\n"
        "for every timepoint i, (for every timepoint j, (if ((i is initial) and (j is initial)), then (i equals j))).\n"
        "for every timepoint a, (for every timepoint b, (for every timepoint c, (if ((a next_tick b) and (a next_tick c)), then (b equals c)))).\n"
        "for every timepoint a, (for every timepoint b, (for every timepoint c, (if ((a next_tick c) and (b next_tick c)), then (a equals b)))).\n"
        "for every timepoint i, (if (i is initial), then (not (there exists timepoint p, (p next_tick i)))).\n"
        "for every timepoint t, (if (t is terminal), then (not (there exists timepoint u, (t next_tick u)))).\n"
        "for every timepoint t, (if (not (t is terminal)), then (there exists timepoint u, (t next_tick u))).\n"
    )
    source = axioms + f"for every timepoint s, (if (s is initial), then ({disj})).\n"
    return e, source, f"Trace-adapter semantics: initial is the unique first point and functional next_tick means exactly one discrete tick. The formula mechanically unrolls response paths of length 0 through {n}, plus FRET's finite-interval escape when terminal occurs in fewer than {n} ticks. The adapter must supply the complete trace interval; finite VE models cover finite executions, while v0 denotation also permits an infinite timepoint domain."

fits["LPC_full_reqts_and_vars.json:LPC:LPC_REACH_HOVER_16:79ba0711"] = within_fit(16)
fits["LPC_full_reqts_and_vars.json:LPC:LPC_REACH_HOVER_13:79b76f00"] = within_fit(13)


def fixed_signal_fit(expected):
    """Reify exact equality of named numeric signals to literal 0.0/1.0."""
    predicates = {name.lower(): (["timepoint", "numeric_value"],
                  f"The exact value of source signal {name} at this snapshot.")
                  for name in expected}
    e = env({"timepoint": "A snapshot in the complete execution interval.",
             "numeric_value": "An exact numeric signal value; no arithmetic operations are assumed."}, predicates)
    e["vocabulary"]["constants"] = {
        "zero": {"sort": "numeric_value", "description": "The numeric literal 0.0."},
        "one": {"sort": "numeric_value", "description": "The numeric literal 1.0."},
    }
    clauses = []
    axioms = [NONEMPTY_TRACE, "not (@zero equals @one).\n"]
    for source_name, value in expected.items():
        name = source_name.lower()
        axioms.append(f"for every timepoint t, (for every numeric_value v, (for every numeric_value w, (if ((t {name} v) and (t {name} w)), then (v equals w)))).\n")
        clauses.append(f"t {name} @{'one' if value == 1 else 'zero'}")
    formula = clauses[-1]
    for clause in reversed(clauses[:-1]):
        formula = f"({clause}) and ({formula})"
    source = "".join(axioms) + f"for every timepoint t, ({formula}).\n"
    return e, source, "Trace-adapter semantics: each binary relation records the exact value of the already-declared FRET signal; per-signal functionality is stated. zero and one denote distinct literal values. The source requirement compares these signals to constants and does not itself recompute their upstream assignments. The complete execution interval must be supplied; finite VE models cover finite traces."


fits["LM_requirements.json:LM_requirements:EUL-006C:3b33fb60"] = fixed_signal_fit({
    "c1xc1Transpose": 1, "c2xc2Transpose": 1, "c3xc3Transpose": 1})
fits["LM_requirements.json:LM_requirements:EUL-007:89d04ff0"] = fixed_signal_fit({
    "DCMxDCMTranspose_11": 1, "DCMxDCMTranspose_12": 0, "DCMxDCMTranspose_13": 0,
    "DCMxDCMTranspose_21": 0, "DCMxDCMTranspose_22": 1, "DCMxDCMTranspose_23": 0,
    "DCMxDCMTranspose_31": 0, "DCMxDCMTranspose_32": 0, "DCMxDCMTranspose_33": 1})

fits["LPC_full_reqts_and_vars.json:LPC:LPC_KIAS_KGS:79b96ad1"] = (
    env({"timepoint": "A snapshot in the requirement trace.", "numeric_value": "An exact numeric signal value supplied by the trace adapter."}, {
        "kias_value": (["timepoint", "numeric_value"], "The exact kias value at the snapshot."),
        "kgs_value": (["timepoint", "numeric_value"], "The exact kgs value at the snapshot."),
    }),
    NONEMPTY_TRACE +
    "for every timepoint t, (for every numeric_value v, (for every numeric_value w, (if ((t kias_value v) and (t kias_value w)), then (v equals w)))).\n" +
    "for every timepoint t, (for every numeric_value v, (for every numeric_value w, (if ((t kgs_value v) and (t kgs_value w)), then (v equals w)))).\n" +
    "for every timepoint t, (there exists numeric_value v, ((t kias_value v) and (t kgs_value v))).\n",
    "Trace-adapter semantics: each signal-value relation records its exact numeric value and functionality is explicit. Reusing one quantified value expresses equality only; it assumes no ordering or arithmetic. The formula requires both readings at every snapshot of the complete execution interval; finite VE models cover finite traces."
)

labels = {
"LM_requirements.json:LM_requirements:EUL-006C:3b33fb60": ("NO", ["real_arithmetic", "matrix_computation"], "The requirement consists entirely of computed real-valued products and equality to 1.0; v0 has neither functions nor arithmetic, and no independent relational claim remains."),
"LM_requirements.json:LM_requirements:AP-004a:c829ea75": ("OPAQUE", ["real_arithmetic", "absolute_value", "previous_value", "numeric_comparison"], "The trigger and response depend on subtraction, absolute value, numeric thresholds, and preReal/preBool history. An implication skeleton is relational, but both decisive checks would be opaque predicates."),
"LM_requirements.json:LM_requirements:EUL-001d:c829ea6d": ("NO", ["real_arithmetic", "trigonometric_functions"], "The entire claim is a real-valued trigonometric equation; naming its truth as a predicate would hide the essential computation."),
"LM_requirements.json:LM_requirements:SWIM-002:c829ea60": ("OPAQUE", ["real_arithmetic", "numeric_comparison"], "The implication and enum-valued response have a useful relational skeleton, but its pressure-threshold antecedent requires an interpreted numeric comparison unavailable in v0."),
"LM_requirements.json:LM_requirements:REG-005:c829ea73": ("OPAQUE", ["metric_time", "real_arithmetic", "numeric_comparison", "persistence_operator"], "The prohibition skeleton is relational, but persisted(100, hcvdt_cmd_fcs_fps2 > 32.0) needs both a metric-duration interpretation and a numeric comparison."),
"LM_requirements.json:LM_requirements:NN-004:c829ea51": ("OPAQUE", ["metric_time", "real_arithmetic", "absolute_value", "numeric_comparison"], "A bounded-duration implication skeleton is visible, but 200 seconds and the absolute-error comparison cannot be implemented by v0 relations without an external numeric/time interpretation."),
"LM_requirements.json:LM_requirements:NN-003B:c829ea64": ("NO", ["metric_time", "real_arithmetic", "numeric_comparison"], "The substantive requirement is a numeric interval maintained for 200 seconds. No qualitative relational claim remains after removing metric time and comparisons."),
"LM_requirements.json:LM_requirements:AP-003D:c829ea50": ("OPAQUE", ["real_arithmetic", "numeric_comparison"], "The conditional assignment skeleton is relational, but the TurnKnob threshold/range tests require numeric ordering unavailable in v0."),
"LM_requirements.json:LM_requirements:REG-007:c829ea78": ("NO", ["real_arithmetic", "numeric_comparison"], "This is solely a real-valued upper-bound claim; an atomic predicate would merely conceal the comparison."),
"LM_requirements.json:LM_requirements:NLG-001:c829ea59": ("NO", ["real_arithmetic", "multiplication", "numeric_comparison"], "This is solely a multiplication-and-positivity claim, which v0 cannot compute."),
"LM_requirements.json:LM_requirements:AP-003C:c829eaa1": ("OPAQUE", ["real_arithmetic", "numeric_comparison", "sign_function"], "Mode qualification and implication form a relational skeleton, but both the angle guard and computed reference require numeric comparison, multiplication, and sign."),
"LM_requirements.json:LM_requirements:TSM-004:c829ea54": ("OPAQUE", ["real_arithmetic", "absolute_value", "numeric_comparison", "previous_value"], "The guarded assignment/previous-value skeleton is relational, but its three absolute differences, thresholds, counter comparisons, and preReal/preInt operations are unavailable."),
"LM_requirements.json:LM_requirements:EUL-007:89d04ff0": ("NO", ["real_arithmetic", "matrix_computation"], "All nine conjuncts assert computed matrix-product entries equal numeric constants; v0 cannot express those computations."),
"LPC_full_reqts_and_vars.json:LPC:LPC_KIAS_0:79ba7c42": ("NO", ["real_arithmetic", "numeric_comparison"], "The whole claim is a real-valued nonnegativity constraint; there is no independent qualitative content."),
"LPC_full_reqts_and_vars.json:LPC:LPC_WB_STAY_ON_until:79b96ad0": ("OPAQUE", ["real_arithmetic", "numeric_comparison", "temporal_until"], "The mode-stability until pattern is relationally useful, but both trigger and termination depend essentially on comparisons of kias with 90.0."),
"LM_requirements.json:LM_requirements:TUI-003v3:0b8c7620": ("OPAQUE", ["real_arithmetic"], "The normalv3 guard is relational, but the response is a computed integration equation using multiplication and addition unavailable in v0."),
"LPC_full_reqts_and_vars.json:LPC:LPC_WIND_SPEED_DERIV_assumption:79ba7c41": ("OPAQUE", ["real_arithmetic", "absolute_value", "previous_value", "numeric_comparison"], "The FTP disjunction is a useful Boolean skeleton, but the other branch requires previous-value subtraction, absolute value, and a threshold comparison."),
"LPC_full_reqts_and_vars.json:LPC:LPC_FCS_STAY_ON:79ba5531": ("OPAQUE", ["previous_value", "real_arithmetic", "numeric_comparison"], "The previous-snapshot implication skeleton is relational, but its preBool condition includes kias >= 30.0, an unavailable numeric comparison."),
"LPC_full_reqts_and_vars.json:LPC:LPC_STB_STAY_ON_until:79b8a781": ("OPAQUE", ["real_arithmetic", "numeric_comparison", "temporal_until"], "The qualitative mode/until skeleton is useful, but the trigger and stopping condition essentially use kias and kgs threshold comparisons."),
"LM_requirements.json:LM_requirements:EUL-001A:c829ea5c": ("NO", ["real_arithmetic", "trigonometric_functions"], "The entire requirement is a trigonometric multiplication equation; v0 has no functions or numeric arithmetic."),
}


def main():
    sampled = json.loads(SAMPLE.read_text())["sample"]
    source_semantics = authoritative_semantics()
    records = []
    for item in sampled:
        ident = item["id"]
        if ident in fits:
            e, source, reif = fits[ident]
            result = ve.check(ve.Environment(e), source)
            rec = {"dataset": "fret", "id": ident, "label": "REIFIED",
                   "construct_needed": ["trace_timepoints"] + (["temporal_order"] if "until" in reif.lower() else []) + (["tick_successor"] if "tick" in reif.lower() else []) + (["exact_value_reification"] if "exact value" in reif.lower() else []),
                   "rationale": "The requirement is mechanically expressible using explicit snapshots and ordinary unary/binary relations; the adapter semantics are stated rather than hidden in an interpreted predicate.",
                   "formalization": source, "environment": e, "parse_result": result,
                   "reification": reif}
        else:
            label, constructs, rationale = labels[ident]
            rec = {"dataset": "fret", "id": ident, "label": label,
                   "construct_needed": constructs, "rationale": rationale,
                   "formalization": None, "environment": None,
                   "parse_result": {"status": "not_checked", "reason": f"{label} item has no faithful v0 witness."},
                   "reification": None}
        filename, _, reqid, _ = ident.split(":")
        rec["source_semantics"] = source_semantics[(filename, reqid)]
        records.append(rec)
    assert len(records) == 30
    OUT.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in records))
    print(json.dumps({"records": len(records), "counts": {k: sum(r["label"] == k for r in records) for k in ("DIRECT", "REIFIED", "OPAQUE", "NO")}, "checked": sum(r["parse_result"].get("language") == "accepted" for r in records)}))


if __name__ == "__main__":
    main()
