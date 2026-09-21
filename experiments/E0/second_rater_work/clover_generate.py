#!/usr/bin/env python3
"""Generate the blinded E0 second-rating record for CloverBench."""
import json
import sys
from pathlib import Path

sys.path.insert(0, "/private/tmp/ve-e0-integration")
from ve import Environment, check

ROOT = Path(__file__).resolve().parents[1]
DRAW = ROOT / "survey_samples" / "_drawn" / "clover.json"
OUT = Path(__file__).with_name("clover.jsonl")


def env(sorts, predicates, constants):
    return {
        "language": "ve.core@0",
        "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20",
        "vocabulary": {
            "sorts": {k: {"description": v} for k, v in sorts.items()},
            "predicates": {k: {"arguments": a, "description": d} for k, (a, d) in predicates.items()},
            "constants": {k: {"sort": s, "description": d} for k, (s, d) in constants.items()},
        },
    }


def checked(label, needed, rationale, source, environment, reification=None, statement_roles=None):
    result = dict(label=label, construct_needed=needed, rationale=rationale,
                formalization=source, environment=environment,
                parse_result=check(Environment(environment), source), reification=reification)
    if statement_roles is not None:
        result["statement_roles"] = statement_roles
    return result


def excluded(label, needed, rationale):
    return dict(label=label, construct_needed=needed, rationale=rationale,
                formalization=None, environment=None,
                parse_result={"status": "not_checked", "reason": "No faithful v0 formalization claimed."},
                reification=None)

def F(sort, var, body): return f"for every {sort} {var}, ({body})"
def E(sort, var, body): return f"there exists {sort} {var}, ({body})"
def I(left, right): return f"if ({left}), then ({right})"
def A(left, right): return f"({left}) and ({right})"
def O(left, right): return f"({left}) or ({right})"
def N(body): return f"not ({body})"


swap_env = env(
    {"value": "A value in one invocation."}, {},
    {"input_x": ("value", "The invocation's first input value."),
     "input_y": ("value", "The invocation's second input value."),
     "output_x": ("value", "The invocation's first returned value."),
     "output_y": ("value", "The invocation's second returned value.")})
swap_source = "@output_x equals @input_y.\n@output_y equals @input_x.\n"

convert_env = env(
    {"natural": "A natural number in the contract's value domain.",
     "boolean": "A Boolean value in the contract's value domain."},
    {"mapped": (["natural", "natural"], "The graph of the supplied function f."),
     "input_value": (["natural", "boolean"], "The graph of the input map."),
     "result_value": (["natural", "boolean"], "The graph of the returned map.")}, {})
convert_support = (
    "for every natural k, (there exists natural v, (k mapped v)).\n"
    "for every natural k, (for every natural v1, (for every natural v2, (if ((k mapped v1) and (k mapped v2)), then (v1 equals v2)))).\n"
    "for every natural k, (for every boolean b1, (for every boolean b2, (if ((k input_value b1) and (k input_value b2)), then (b1 equals b2)))).\n"
    "for every natural k, (for every boolean b1, (for every boolean b2, (if ((k result_value b1) and (k result_value b2)), then (b1 equals b2)))).\n")
convert_pre = "for every natural k1, (for every natural k2, (for every natural v, (if ((k1 mapped v) and (k2 mapped v)), then (k1 equals k2))))"
convert_domain_forward = "for every natural k, (if (there exists boolean b, (k input_value b)), then (there exists natural fk, ((k mapped fk) and (there exists boolean rb, (fk result_value rb)))))"
convert_domain_reverse = "for every natural k, (for every natural fk, (if ((k mapped fk) and (there exists boolean rb, (fk result_value rb))), then (there exists boolean ib, (k input_value ib))))"
convert_values = "for every natural k, (for every natural fk, (for every boolean b, (if ((k input_value b) and (k mapped fk)), then (fk result_value b))))"
convert_post = f"(({convert_domain_forward}) and ({convert_domain_reverse})) and ({convert_values})"
convert_source = convert_support + f"if ({convert_pre}), then ({convert_post}).\n"

seq_env = env(
    {"position": "An index position in either finite collection.",
     "value": "A value of the generic element type.",
     "object": "A heap object identity."},
    {"input_value": (["position", "value"], "The input sequence value at a position."),
     "output_value": (["position", "value"], "The returned array value at a position."),
     "allocated_before": (["object"], "An object allocated before this method invocation.")},
    {"output_array": ("object", "The returned array object's identity.")})
seq_source = (
    "not (@output_array is allocated_before).\n"
    "for every position p, (if (there exists value v, (p input_value v)), then (there exists value v, (p output_value v))).\n"
    "for every position p, (if (there exists value v, (p output_value v)), then (there exists value v, (p input_value v))).\n"
    "for every position p, (for every value v, (if (p input_value v), then (p output_value v))).\n"
    "for every position p, (for every value v1, (for every value v2, (if ((p input_value v1) and (p input_value v2)), then (v1 equals v2)))).\n"
    "for every position p, (for every value v1, (for every value v2, (if ((p output_value v1) and (p output_value v2)), then (v1 equals v2)))).\n")

swap_array_env = env(
    {"position": "An array index location.", "value": "An integer value, used only through equality."},
    {"before_value": (["position", "value"], "The pre-state array graph."),
     "after_value": (["position", "value"], "The post-state array graph.")},
    {"left_index": ("position", "The parameter i."), "right_index": ("position", "The parameter j.")})
swap_array_support = (
    "for every position p, (for every value v1, (for every value v2, (if ((p before_value v1) and (p before_value v2)), then (v1 equals v2)))).\n"
    "for every position p, (for every value v1, (for every value v2, (if ((p after_value v1) and (p after_value v2)), then (v1 equals v2)))).\n")
swap_array_pre = "(there exists value v, (@left_index before_value v)) and (there exists value v, (@right_index before_value v))"
swap_array_domains = "(for every position p, (if (there exists value v, (p before_value v)), then (there exists value v, (p after_value v)))) and (for every position p, (if (there exists value v, (p after_value v)), then (there exists value v, (p before_value v))))"
swap_left = "for every value v, (if (@right_index before_value v), then (@left_index after_value v))"
swap_right = "for every value v, (if (@left_index before_value v), then (@right_index after_value v))"
swap_frame = F("position", "p", F("value", "v", I(A(A("p before_value v", N("p equals @left_index")), N("p equals @right_index")), "p after_value v")))
swap_array_post = f"(({swap_array_domains}) and (({swap_left}) and ({swap_right}))) and ({swap_frame})"
swap_array_source = swap_array_support + f"if ({swap_array_pre}), then ({swap_array_post}).\n"

copy_env = env(
    {"position": "An index or the one-past-end boundary.", "value": "An array element value.",
     "snapshot": "A loop-head state represented by the invariant.", "cell": "A reified cell observation in a loop snapshot."},
    {"before": (["position", "position"], "Strict index order."),
     "input_value": (["position", "value"], "The source array graph."),
     "output_value": (["position", "value"], "The returned array graph."),
     "cursor": (["snapshot", "position"], "The loop cursor at a loop-head snapshot."),
     "in_snapshot": (["cell", "snapshot"], "The snapshot owning a cell observation."),
     "cell_position": (["cell", "position"], "The position observed by a cell record."),
     "cell_value": (["cell", "value"], "The value observed by a cell record.")},
    {"start": ("position", "Index zero."), "end": ("position", "The one-past-end length boundary.")})
copy_cell_condition = A(A(A(A(A("c1 in_snapshot s", "c2 in_snapshot s"), "c1 cell_position p"), "c2 cell_position p"), "c1 cell_value v1"), "c2 cell_value v2")
copy_cell_functional = F("snapshot", "s", F("position", "p", F("cell", "c1", F("cell", "c2", F("value", "v1", F("value", "v2", I(copy_cell_condition, "v1 equals v2")))))))
copy_support = (
    "for every position p, (not (p before p)).\n"
    "for every position p, (for every position q, (for every position r, (if ((p before q) and (q before r)), then (p before r)))).\n"
    "for every position p, (for every position q, (((p equals q) or (p before q)) or (q before p))).\n"
    "(@start equals @end) or (@start before @end).\n"
    "for every position p, (if (there exists value v, (p input_value v)), then (((p equals @start) or (@start before p)) and (p before @end))).\n"
    "for every position p, (if (((p equals @start) or (@start before p)) and (p before @end)), then (there exists value v, (p input_value v))).\n"
    "for every position p, (for every value v1, (for every value v2, (if ((p input_value v1) and (p input_value v2)), then (v1 equals v2)))).\n"
    "for every position p, (for every value v1, (for every value v2, (if ((p output_value v1) and (p output_value v2)), then (v1 equals v2)))).\n"
    "for every cell c, (there exists snapshot s, (c in_snapshot s)).\n"
    "for every cell c, (there exists position p, (c cell_position p)).\n"
    "for every cell c, (there exists value v, (c cell_value v)).\n"
    + copy_cell_functional + ".\n"
    "there exists snapshot s, (true).\n"
    "for every snapshot s, (there exists position i, (s cursor i)).\n"
    "for every snapshot s, (for every position i1, (for every position i2, (if ((s cursor i1) and (s cursor i2)), then (i1 equals i2)))).\n")
copy_contract = seq_source.split("not (@output_array is allocated_before).\n", 1)[1]
copy_prefix = F("snapshot", "s", F("position", "i", I("s cursor i", F("position", "p", F("value", "v", I(A("p before i", "p input_value v"), E("cell", "c", A(A("c in_snapshot s", "c cell_position p"), "c cell_value v"))))))))
copy_invariant = (
    "for every snapshot s, (for every position i, (if (s cursor i), then ((i equals @end) or (there exists value v, (i input_value v))))).\n"
    + copy_prefix + ".\n")
copy_source = copy_support + copy_contract + copy_invariant

digits = [f"digit_{i}" for i in range(10)]
digit_env = env(
    {"position": "A string index or one-past-end boundary.", "character": "A character value.",
     "boolean": "A Boolean result value.", "snapshot": "A loop-head state represented by the invariant."},
    {"before": (["position", "position"], "Strict index order."),
     "input_character": (["position", "character"], "The input string's character graph."),
     "cursor": (["snapshot", "position"], "The loop cursor at a loop-head snapshot."),
     "state_true": (["snapshot"], "The intermediate result is true at this snapshot.")},
    {"start": ("position", "Index zero."), "end": ("position", "The string-length boundary."),
     "result": ("boolean", "The returned Boolean."), "boolean_true": ("boolean", "Boolean true."),
     "boolean_false": ("boolean", "Boolean false."),
     **{d: ("character", f"The character {i}.") for i, d in enumerate(digits)}})

def disjoin(forms):
    out = forms[0]
    for form in forms[1:]:
        out = f"({out}) or ({form})"
    return out

digit_test = lambda c: disjoin([f"{c} equals @{d}" for d in digits])
digit_distinct = "".join(f"not (@{a} equals @{b}).\n" for i, a in enumerate(digits) for b in digits[i + 1:])
all_input_digits = f"for every position p, (for every character c, (if (p input_character c), then ({digit_test('c')})))"
prefix_digits = lambda i: f"for every position p, (for every character c, (if ((p before {i}) and (p input_character c)), then ({digit_test('c')})))"
digits_source = (
    digit_distinct + "not (@boolean_true equals @boolean_false).\n"
    "for every boolean b, ((b equals @boolean_true) or (b equals @boolean_false)).\n"
    "for every position p, (not (p before p)).\n"
    "for every position p, (for every position q, (for every position r, (if ((p before q) and (q before r)), then (p before r)))).\n"
    "for every position p, (for every position q, (((p equals q) or (p before q)) or (q before p))).\n"
    "(@start equals @end) or (@start before @end).\n"
    "for every position p, (if (there exists character c, (p input_character c)), then (((p equals @start) or (@start before p)) and (p before @end))).\n"
    "for every position p, (if (((p equals @start) or (@start before p)) and (p before @end)), then (there exists character c, (p input_character c))).\n"
    "for every position p, (for every character c1, (for every character c2, (if ((p input_character c1) and (p input_character c2)), then (c1 equals c2)))).\n"
    f"(if (@result equals @boolean_true), then ({all_input_digits})) and (if ({all_input_digits}), then (@result equals @boolean_true)).\n"
    "there exists snapshot s, (true).\n"
    "for every snapshot s, (there exists position i, (s cursor i)).\n"
    "for every snapshot s, (for every position i1, (for every position i2, (if ((s cursor i1) and (s cursor i2)), then (i1 equals i2)))).\n"
    "for every snapshot s, (for every position i, (if (s cursor i), then ((i equals @end) or (there exists character c, (i input_character c))))).\n"
    f"for every snapshot s, (for every position i, (if (s cursor i), then ((if (s is state_true), then ({prefix_digits('i')})) and (if ({prefix_digits('i')}), then (s is state_true))))).\n")

modify_env = env(
    {"outer_index": "An outer-array index.", "inner_index": "An inner-array index.",
     "array_ref": "An inner-array reference.", "cell": "A stable inner-cell location.",
     "value": "A natural-number cell value, used only through equality."},
    {"before_outer": (["outer_index", "array_ref"], "Outer-array references before the call."),
     "after_outer": (["outer_index", "array_ref"], "Outer-array references after the call."),
     "cell_array": (["cell", "array_ref"], "The inner array owning a cell location."),
     "cell_index": (["cell", "inner_index"], "The index of a cell location."),
     "before_cell": (["cell", "value"], "Cell values before the call."),
     "after_cell": (["cell", "value"], "Cell values after the call.")},
    {"selected_outer": ("outer_index", "The parameter index1."),
     "selected_inner": ("inner_index", "The parameter index2."),
     "new_value": ("value", "The parameter val.")})
modify_support = (
    "for every outer_index i, (for every array_ref a1, (for every array_ref a2, (if ((i before_outer a1) and (i before_outer a2)), then (a1 equals a2)))).\n"
    "for every outer_index i, (for every array_ref a1, (for every array_ref a2, (if ((i after_outer a1) and (i after_outer a2)), then (a1 equals a2)))).\n"
    "for every cell c, (for every value v1, (for every value v2, (if ((c before_cell v1) and (c before_cell v2)), then (v1 equals v2)))).\n"
    "for every cell c, (for every value v1, (for every value v2, (if ((c after_cell v1) and (c after_cell v2)), then (v1 equals v2)))).\n"
    "for every cell c, (there exists array_ref a, (c cell_array a)).\n"
    "for every cell c, (there exists inner_index j, (c cell_index j)).\n"
    "for every cell c, (there exists value v, (c before_cell v)).\n"
    "for every cell c, (for every array_ref a1, (for every array_ref a2, (if ((c cell_array a1) and (c cell_array a2)), then (a1 equals a2)))).\n"
    "for every cell c, (for every inner_index j1, (for every inner_index j2, (if ((c cell_index j1) and (c cell_index j2)), then (j1 equals j2)))).\n"
    "for every cell c1, (for every cell c2, (for every array_ref a, (for every inner_index j, (if ((((c1 cell_array a) and (c2 cell_array a)) and (c1 cell_index j)) and (c2 cell_index j)), then (c1 equals c2))))).\n")
modify_distinct = F("outer_index", "i", F("outer_index", "j", F("array_ref", "ai", F("array_ref", "aj", I(A(A("i before_outer ai", "j before_outer aj"), N("i equals j")), N("ai equals aj"))))))
modify_pre = f"(({modify_distinct}) and (there exists array_ref a, (@selected_outer before_outer a))) and (there exists cell c, ((c cell_index @selected_inner) and (there exists array_ref a, ((c cell_array a) and (@selected_outer before_outer a)))))"
modify_outer = "(for every outer_index i, (for every array_ref a, (if (i before_outer a), then (i after_outer a)))) and (for every outer_index i, (for every array_ref a, (if (i after_outer a), then (i before_outer a))))"
modify_update = F("array_ref", "a", F("cell", "c", I(A(A("@selected_outer before_outer a", "c cell_array a"), "c cell_index @selected_inner"), "c after_cell @new_value")))
modify_frame_condition = A(A(A("@selected_outer before_outer selected", "c cell_array a"), "c cell_index j"), "c before_cell v")
modify_frame_condition = A(modify_frame_condition, O(N("a equals selected"), N("j equals @selected_inner")))
modify_frame = F("array_ref", "selected", F("array_ref", "a", F("cell", "c", F("inner_index", "j", F("value", "v", I(modify_frame_condition, "c after_cell v"))))))
modify_no_new_cells = F("cell", "c", I(E("value", "v", "c after_cell v"), E("value", "v", "c before_cell v")))
modify_source = modify_support + f"if ({modify_pre}), then (((({modify_outer}) and ({modify_update})) and ({modify_frame})) and ({modify_no_new_cells})).\n"

def ordered_array_support(value_pred="input_value"):
    return (
        "for every position p, (not (p before p)).\n"
        "for every position p, (for every position q, (for every position r, (if ((p before q) and (q before r)), then (p before r)))).\n"
        "for every position p, (for every position q, (((p equals q) or (p before q)) or (q before p))).\n"
        "(@start equals @end) or (@start before @end).\n"
        f"for every position p, (if (there exists value v, (p {value_pred} v)), then (((p equals @start) or (@start before p)) and (p before @end))).\n"
        f"for every position p, (if (((p equals @start) or (@start before p)) and (p before @end)), then (there exists value v, (p {value_pred} v))).\n"
        f"for every position p, (for every value v1, (for every value v2, (if ((p {value_pred} v1) and (p {value_pred} v2)), then (v1 equals v2)))).\n")

append_env = env(
    {"position": "An input/output index or one-past-end boundary.", "value": "An array element value.",
     "snapshot": "A loop-head state represented by the invariant.", "cell": "A reified cell observation."},
    {"before": (["position", "position"], "Strict index order."),
     "input_value": (["position", "value"], "The input array graph."),
     "output_value": (["position", "value"], "The returned array graph."),
     "cursor": (["snapshot", "position"], "The loop cursor."),
     "in_snapshot": (["cell", "snapshot"], "The snapshot owning a cell observation."),
     "cell_position": (["cell", "position"], "The observed position."),
     "cell_value": (["cell", "value"], "The observed value.")},
    {"start": ("position", "Index zero."), "end": ("position", "The input length boundary and new last index."),
     "new_end": ("position", "The output length boundary."), "appended": ("value", "The appended parameter b.")})
append_support = ordered_array_support() + (
    "@end before @new_end.\n"
    "for every position p, (if ((@end before p) and (p before @new_end)), then (false)).\n"
    "for every position p, (for every value v1, (for every value v2, (if ((p output_value v1) and (p output_value v2)), then (v1 equals v2)))).\n"
    "there exists snapshot s, (true).\n"
    "for every snapshot s, (there exists position i, (s cursor i)).\n"
    "for every snapshot s, (for every position i1, (for every position i2, (if ((s cursor i1) and (s cursor i2)), then (i1 equals i2)))).\n"
    "for every cell c, (there exists snapshot s, (c in_snapshot s)).\n"
    "for every cell c, (there exists position p, (c cell_position p)).\n"
    "for every cell c, (there exists value v, (c cell_value v)).\n"
    + copy_cell_functional + ".\n")
append_post = A(
    A(F("position", "p", I(E("value", "v", "p input_value v"), E("value", "v", "p output_value v"))),
      F("position", "p", I(E("value", "v", "p output_value v"), O(E("value", "v", "p input_value v"), "p equals @end")))),
    A(F("position", "p", F("value", "v", I("p input_value v", "p output_value v"))), "@end output_value @appended"))
append_source = append_support + append_post + ".\n" + copy_invariant

find_env = env(
    {"position": "An array index, end boundary, or distinguished not-found sentinel.", "value": "An integer value used through equality.",
     "snapshot": "A loop-head state represented by the invariant."},
    {"before": (["position", "position"], "Strict index order."),
     "input_value": (["position", "value"], "The input array graph."),
     "cursor": (["snapshot", "position"], "The loop cursor.")},
    {"start": ("position", "Index zero."), "end": ("position", "The array length boundary."),
     "sentinel": ("position", "The -1 not-found result."), "result": ("position", "The returned index."),
     "key": ("value", "The searched key.")})
find_support = ordered_array_support() + (
    "not (@sentinel equals @end).\n"
    "not (there exists value v, (@sentinel input_value v)).\n"
    "there exists snapshot s, (true).\n"
    "for every snapshot s, (there exists position i, (s cursor i)).\n"
    "for every snapshot s, (for every position i1, (for every position i2, (if ((s cursor i1) and (s cursor i2)), then (i1 equals i2)))).\n")
prior_not_key = lambda i: F("position", "p", F("value", "v", I(A(f"p before {i}", "p input_value v"), N("v equals @key"))))
find_found = A(E("value", "v", A("@result input_value v", "v equals @key")), prior_not_key("@result"))
find_absent = F("position", "p", F("value", "v", I("p input_value v", N("v equals @key"))))
find_contract = A(O("@result equals @sentinel", E("value", "v", "@result input_value v")), A(I(N("@result equals @sentinel"), find_found), I("@result equals @sentinel", find_absent)))
find_invariant = F("snapshot", "s", F("position", "i", I("s cursor i", A(O("i equals @end", E("value", "v", "i input_value v")), prior_not_key("i")))))
find_source = find_support + find_contract + ".\n" + find_invariant + ".\n"

linear1_env = env(
    {"position": "An array index or length boundary.", "value": "An integer value used through equality.",
     "snapshot": "A loop-head state represented by the invariant."},
    {"before": (["position", "position"], "Strict index order."), "input_value": (["position", "value"], "The input array graph."),
     "cursor": (["snapshot", "position"], "The loop cursor.")},
    {"start": ("position", "Index zero."), "end": ("position", "The length boundary."),
     "result": ("position", "The returned position or end boundary."), "key": ("value", "The searched value e.")})
linear1_support = ordered_array_support() + (
    "there exists snapshot s, (true).\nfor every snapshot s, (there exists position i, (s cursor i)).\n"
    "for every snapshot s, (for every position i1, (for every position i2, (if ((s cursor i1) and (s cursor i2)), then (i1 equals i2)))).\n")
linear1_contract = A(O("@result equals @end", E("value", "v", "@result input_value v")), A(O("@result equals @end", "@result input_value @key"), prior_not_key("@result")))
linear1_invariant = F("snapshot", "s", F("position", "i", I("s cursor i", A(O("i equals @end", E("value", "v", "i input_value v")), prior_not_key("i")))))
linear1_source = linear1_support + linear1_contract + ".\n" + linear1_invariant + ".\n"

linear3_env = env(
    {"position": "An array index or length boundary.", "value": "A generic array element.", "snapshot": "A loop-head state."},
    {"before": (["position", "position"], "Strict index order."), "input_value": (["position", "value"], "The input array graph."),
     "matches": (["value"], "The supplied predicate P holds of this value."), "cursor": (["snapshot", "position"], "The loop cursor.")},
    {"start": ("position", "Index zero."), "end": ("position", "The length boundary."), "result": ("position", "The returned index.")})
linear3_support = ordered_array_support() + (
    "there exists snapshot s, (true).\nfor every snapshot s, (there exists position i, (s cursor i)).\n"
    "for every snapshot s, (for every position i1, (for every position i2, (if ((s cursor i1) and (s cursor i2)), then (i1 equals i2)))).\n")
matching_at = lambda p: E("value", "v", A(f"{p} input_value v", "v is matches"))
not_matching_before = lambda p: F("position", "k", F("value", "v", I(A(f"k before {p}", "k input_value v"), N("v is matches"))))
linear3_pre = E("position", "p", matching_at("p"))
linear3_post = A(matching_at("@result"), not_matching_before("@result"))
remaining_match = lambda i: E("position", "p", A(O(f"p equals {i}", f"{i} before p"), matching_at("p")))
linear3_invariant = F("snapshot", "s", F("position", "i", I("s cursor i", A(A(E("value", "v", "i input_value v"), remaining_match("i")), not_matching_before("i")))))
linear3_source = linear3_support + I(linear3_pre, A(linear3_post, linear3_invariant)) + ".\n"

remove_env = env(
    {"input_position": "An input-array index or end boundary.", "output_position": "An output-array index.", "value": "An element value.",
     "snapshot": "A loop-head state represented by the invariant.", "cell": "A reified output-cell observation."},
    {"input_before": (["input_position", "input_position"], "Strict input index order."),
     "output_before": (["output_position", "output_position"], "Strict output index order."),
     "input_value": (["input_position", "value"], "The input array graph."),
     "output_value": (["output_position", "value"], "The returned array graph."),
     "shifted_to": (["input_position", "output_position"], "The order-isomorphic tail-position mapping after deleting the first input position."),
     "cursor": (["snapshot", "input_position"], "The loop cursor."),
     "in_snapshot": (["cell", "snapshot"], "The snapshot owning an observation."),
     "cell_position": (["cell", "output_position"], "The observed output position."),
     "cell_value": (["cell", "value"], "The observed value.")},
    {"first": ("input_position", "The first input position."), "end": ("input_position", "The input length boundary.")})
remove_obs = E("cell", "c", A(A("c in_snapshot s", "c cell_position q"), "c cell_value v"))
remove_support = (
    "for every input_position p, (not (p input_before p)).\n"
    "for every input_position p, (for every input_position q, (for every input_position r, (if ((p input_before q) and (q input_before r)), then (p input_before r)))).\n"
    "for every input_position p, (for every input_position q, (((p equals q) or (p input_before q)) or (q input_before p))).\n"
    "(@first equals @end) or (@first input_before @end).\n"
    "for every input_position p, (if (there exists value v, (p input_value v)), then (((p equals @first) or (@first input_before p)) and (p input_before @end))).\n"
    "for every input_position p, (if (((p equals @first) or (@first input_before p)) and (p input_before @end)), then (there exists value v, (p input_value v))).\n"
    "for every output_position p, (not (p output_before p)).\n"
    "for every output_position p, (for every output_position q, (for every output_position r, (if ((p output_before q) and (q output_before r)), then (p output_before r)))).\n"
    "for every output_position p, (for every output_position q, (((p equals q) or (p output_before q)) or (q output_before p))).\n"
    "for every input_position p, (for every value v1, (for every value v2, (if ((p input_value v1) and (p input_value v2)), then (v1 equals v2)))).\n"
    "for every output_position p, (for every value v1, (for every value v2, (if ((p output_value v1) and (p output_value v2)), then (v1 equals v2)))).\n"
    "for every input_position p, (for every output_position q1, (for every output_position q2, (if ((p shifted_to q1) and (p shifted_to q2)), then (q1 equals q2)))).\n"
    "for every input_position p1, (for every input_position p2, (for every output_position q, (if ((p1 shifted_to q) and (p2 shifted_to q)), then (p1 equals p2)))).\n")
remove_pre = E("value", "v", "@first input_value v")
remove_mapping = A(
    A(F("input_position", "p", I(N("p equals @first"), E("output_position", "q", "p shifted_to q"))),
      F("output_position", "q", E("input_position", "p", "p shifted_to q"))),
    A(F("input_position", "p", F("output_position", "q", F("value", "v", I(A("p shifted_to q", "p input_value v"), "q output_value v")))),
      F("input_position", "p1", F("input_position", "p2", F("output_position", "q1", F("output_position", "q2", I(A(A("p1 shifted_to q1", "p2 shifted_to q2"), "p1 input_before p2"), "q1 output_before q2")))))))
remove_mapping = A(remove_mapping, F("output_position", "q", N("@first shifted_to q")))
remove_obs_condition = A(A(A(A("c1 in_snapshot s", "c2 in_snapshot s"), "c1 cell_position q"), "c2 cell_position q"), A("c1 cell_value v1", "c2 cell_value v2"))
remove_obs_functional = F("snapshot", "s", F("output_position", "q", F("cell", "c1", F("cell", "c2", F("value", "v1", F("value", "v2", I(remove_obs_condition, "v1 equals v2")))))))
remove_prefix = F("input_position", "p",
                  F("output_position", "q",
                    F("value", "v",
                      I(A(A("p input_before i", "p shifted_to q"), "p input_value v"), remove_obs))))
remove_inv_body = F("snapshot", "s",
                    F("input_position", "i",
                      I("s cursor i", A(O("i equals @end", E("value", "v", "i input_value v")), remove_prefix))))
remove_invariants = A(E("snapshot", "s", "true"), A(remove_obs_functional, A(F("snapshot", "s", E("input_position", "i", "s cursor i")), A(F("snapshot", "s", F("input_position", "i1", F("input_position", "i2", I(A("s cursor i1", "s cursor i2"), "i1 equals i2")))), remove_inv_body))))
remove_source = remove_support + I(remove_pre, A(remove_mapping, remove_invariants)) + ".\n"


ratings = {
"CloverBench/textbook_algo/triple": excluded("NO", ["integer arithmetic", "multiplication"], "The sole postcondition defines the result as 3*x; v0 has no arithmetic, and replacing it by a named relation would merely hide the whole claim."),
"CloverBench/textbook_algo/convert_map_key": checked("REIFIED", ["function graph", "finite-map graph"], "The injective function and both maps can be expanded as single-valued binary graphs; the requires clause implies the two postconditions rather than being asserted as an unconditional fact.", convert_source, convert_env, "Function application is replaced by mapped(k,v), and map lookup/membership by partial single-valued input_value/result_value graphs. Totality and single-valuedness of f and map single-valuedness are supporting type semantics. Injectivity is the contract antecedent; key-domain equivalence and value preservation are its consequent.", ["function totality", "function single-valuedness", "input map single-valuedness", "result map single-valuedness", "requires injectivity implies both ensures clauses"]),
"CloverBench/textbook_algo/array_append": checked("REIFIED", ["ordered position graph", "singleton append", "loop snapshots"], "The contract appends one distinguished value and the invariant copies an ordered prefix; neither performs arithmetic on element values, so both admit an explicit position/cell encoding.", append_source, append_env, "The input end boundary becomes the one new output position, with a fresh adjacent output boundary. Functional cell graphs preserve the input prefix and loop snapshots carry the prefix-copy invariant."),
"CloverBench/textbook_algo/cal_sum": excluded("NO", ["integer arithmetic", "multiplication", "division"], "The postcondition and invariant are the closed-form arithmetic sum; no independent relational content remains after removing arithmetic."),
"CloverBench/textbook_algo/array_copy": checked("REIFIED", ["array cell graph", "ordered positions", "loop snapshots"], "The equal-length copy contract and prefix invariant use only equality and ordered index domains, so positions, cells, and loop-head snapshots can be expanded mechanically.", copy_source, copy_env, "Input/output arrays are functional position-value graphs. before is the explicit strict position order. Snapshot/cursor and reified cell observations represent the invariant's loop-head valuation; no arithmetic on element values is hidden."),
"CloverBench/textbook_algo/swap_in_array": checked("REIFIED", ["before/after array graphs"], "Bounds are exactly membership in the pre-state array domain; with functional before/after graphs the swap, unchanged domain, and frame condition are first-order relational constraints.", swap_array_source, swap_array_env, "Array lookup is expanded as functional position-value graphs. The requires clause is the implication antecedent; swapped cells, identical domains, and preservation of all other cells form the consequent."),
"CloverBench/textbook_algo/two_sum": excluded("OPAQUE", ["integer addition", "array indexing", "integer order"], "The search-order and witness skeleton is useful, but pair matching depends on integer addition and the invariants quantify ordered index ranges, which v0 cannot interpret directly."),
"CloverBench/textbook_algo/selectionsort": excluded("OPAQUE", ["integer order", "array indexing", "multiset cardinality", "mutable state"], "Sortedness can be sketched relationally, but the permutation contract requires unbounded multiplicity counting and the invariants also depend on indexed mutable state."),
"CloverBench/textbook_algo/bubble_sort": excluded("OPAQUE", ["integer order", "array indexing", "multiset cardinality", "mutable state"], "The sortedness skeleton is relational, while the general multiset equality and index arithmetic in the nested-loop invariants are outside v0."),
"CloverBench/textbook_algo/integer_square_root": excluded("NO", ["natural-number arithmetic", "multiplication", "successor"], "Both the result specification and invariant are arithmetic inequalities involving multiplication; a square-root predicate would hide the essential claim."),
"CloverBench/textbook_algo/has_close_elements": excluded("OPAQUE", ["real arithmetic", "absolute difference", "sequence indexing", "integer order"], "Existence/nonexistence of a close pair is a useful quantifier skeleton, but closeness is defined by real subtraction, comparison, and indexed sequence access."),
"CloverBench/textbook_algo/triple4": excluded("NO", ["integer arithmetic", "multiplication"], "The only functional claim is r=3*x, which cannot be expressed without arithmetic or an opaque predicate naming the result."),
"CloverBench/textbook_algo/seq_to_array": checked("REIFIED", ["sequence-to-array cell graph", "heap freshness"], "With no loop invariants, the contract can be expanded into equal position domains, equal values at each position, functional cell graphs, and freshness of the returned object.", seq_source, seq_env, "Sequence and array lookup are represented by separate partial single-valued position-to-value graphs. Equality of their position domains expresses equal length, pointwise inclusion plus functionality expresses equal contents, and freshness is explicit against allocated_before."),
"CloverBench/textbook_algo/find": checked("REIFIED", ["ordered position graph", "not-found sentinel", "loop snapshots"], "The search uses only value equality, a strict position order, and a distinguished -1 sentinel; these are expanded directly along with the prefix invariant.", find_source, find_env, "Valid indices are the input graph's ordered domain, sentinel is explicitly outside it, and loop-head snapshots carry a cursor whose strict prefix contains no key."),
"CloverBench/textbook_algo/even_list": excluded("OPAQUE", ["integer modulo", "sequence membership", "array indexing", "cardinality/order"], "Membership and order-preserving filtering have relational content, but evenness uses modulo and the invariants require general indexed sequence lengths and correspondence."),
"CloverBench/textbook_algo/triple3": excluded("NO", ["integer arithmetic", "multiplication"], "The only contract is arithmetic tripling; the branch in the excluded algorithm body adds no independent specification content."),
"CloverBench/textbook_algo/swap_bitvector": checked("DIRECT", [], "The complete functional specification is two equalities between same-sort input and output values; bitvector operations occur only in the excluded body.", swap_source, swap_env),
"CloverBench/textbook_algo/double_array_elements": excluded("OPAQUE", ["integer multiplication", "array indexing", "mutable old state"], "The before/after array skeleton is useful, but every changed-cell obligation depends on multiplication by two and the loop invariants require index intervals."),
"CloverBench/textbook_algo/swap": checked("DIRECT", [], "The complete contract consists solely of two same-sort equalities swapping returned and input values; arithmetic does not occur in the specification.", swap_source, swap_env),
"CloverBench/textbook_algo/is_even": excluded("NO", ["integer modulo", "Boolean equivalence"], "The sole postcondition defines the Boolean result by x mod 2; a named even predicate would hide the essential computation."),
"CloverBench/textbook_algo/multi_return": excluded("NO", ["integer addition", "integer subtraction"], "Both returned values are specified only by arithmetic expressions, leaving no independent relational claim."),
"CloverBench/textbook_algo/swap_arith": checked("DIRECT", [], "Although the excluded implementation uses arithmetic, the complete functional contract is only the two cross equalities.", swap_source, swap_env),
"CloverBench/textbook_algo/all_digits": checked("REIFIED", ["string character graph", "ordered positions", "loop snapshots", "fixed finite alphabet"], "The ten accepted characters are explicitly enumerated with distinct constants; the result equivalence and prefix invariant then use only relational character lookup and strict index order.", digits_source, digit_env, "String access is a functional position-character graph, the digit set is an equality disjunction over ten pairwise-distinct constants, and each loop-head snapshot explicitly carries its cursor and intermediate Boolean."),
"CloverBench/textbook_algo/modify_2d_array": checked("REIFIED", ["two-state heap graph", "reified nested cells"], "Outer references, stable inner-cell locations, pre/post values, bounds, the non-aliasing precondition, update, and frame condition can all be represented explicitly as relations.", modify_source, modify_env, "Outer arrays are functional index-reference graphs; cells separately identify their owning inner array and inner index. The requires clauses form the implication antecedent. The consequent preserves outer references, writes the selected cell, and preserves every other cell."),
"CloverBench/textbook_algo/max_array": excluded("OPAQUE", ["integer order", "array indexing", "length"], "Being an attained upper bound has a useful relational-order skeleton, but the contract and invariants require the standard integer order and bounded array indices."),
"CloverBench/textbook_algo/remove_front": checked("REIFIED", ["tail position isomorphism", "ordered positions", "loop snapshots"], "Deleting the first position and shifting the remaining positions is an explicit order-preserving bijection; the slice equality and prefix invariant require no element arithmetic.", remove_source, remove_env, "shifted_to is constrained as a bijection from every non-first input position onto output positions, preserves order and values, and is reused by the loop-prefix snapshot invariant. The nonempty requires clause is the contract antecedent."),
"CloverBench/textbook_algo/linear_search1": checked("REIFIED", ["ordered position graph", "end sentinel", "loop snapshots"], "The contract and invariant use only equality lookup, strict prefix order, and the end boundary as the no-match result.", linear1_source, linear1_env, "The input cell graph defines valid positions; result/cursor may be a valid position or the explicit end boundary, and every earlier input value is constrained unequal to the key."),
"CloverBench/textbook_algo/rotate": excluded("OPAQUE", ["integer addition", "modulo", "array indexing"], "The pointwise correspondence skeleton is useful, but the defining source index is (i+offset) mod length, so an unexplained rotation relation would hide the essential semantics."),
"CloverBench/textbook_algo/linear_search3": checked("REIFIED", ["reified predicate input", "ordered position graph", "loop snapshots"], "The supplied predicate is a unary relation on values, while first-match and the invariants are explicit constraints over the ordered position graph.", linear3_source, linear3_env, "matches(v) represents P(v). The existence precondition implies the first-match postcondition; loop snapshots state valid cursors, a remaining match, and no earlier match."),
"CloverBench/textbook_algo/online_max": excluded("OPAQUE", ["integer order", "array indexing", "length arithmetic"], "Maximum and first-later-greater conditions have a relational-order skeleton, but the contract and both invariants rely on bounded indices, length-1, and the standard order on integer values."),
}


def main():
    sample = json.loads(DRAW.read_text())["sample"]
    assert len(sample) == 30
    assert set(ratings) == {x["id"] for x in sample}
    with OUT.open("w") as f:
        for item in sample:
            record = {"dataset": "clover", "id": item["id"], **ratings[item["id"]]}
            f.write(json.dumps(record, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
