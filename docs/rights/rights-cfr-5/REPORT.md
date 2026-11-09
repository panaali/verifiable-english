# rights-cfr-5 report: single right lines round-trip with their header options

**Status:** built and waiting for the chain's gate. The DRI does not need to sign anything: DELTA row 1 is
pre-signed (reviews/dri-decisions-20261109-lp0801.md item 1), and row 2 cites R1 and R2.
**What changed:** `render_line` and `parse_line` (ve/surface/rights.py) now carry the switch header that norm_english
renders (`Claim of right r (user may turn off). …`) and no other header. No verdict changes.
**Open:** 126 of 506 generated lines still fail. Every one has two carve-outs, and the cause is a double space in
norm_english's soft parser, not this item (section 3). That is follow-up rights-cfr-5b. Trust +0. Pilot bytes: 0.
**HEAD:** the last commit on feature/rights-cfr-5. Base: `49f1682dc` (`git merge-base HEAD main`).

## 1. Task deliverables

The task is regrade #6 (reviews/l1-c-regrade-rights-20261109.md), item rights-cfr-5. The plan is
docs/spec/rights.md :228 (header options) and :436 (round-trip).

| # | Deliverable | Delivered by |
|---|---|---|
| 1 | `render_line` and `parse_line` accept exactly the header forms norm_english renders, read from the renderer and not retyped. | `render_line` keeps the renderer's own header text: the source must match norm_english's `_SOFT_HEADER` as block 1, and `source[len("Rule 1"):]` is kept. `parse_line` splits the line with the same `_SOFT_HEADER`. `_rendered_header` decodes the options with `softnorms.parse_header_options` and accepts the header only if it equals `render_header_options((), parties)`, the renderer's spelling for one rule; a single line never renders a precedence option. Any other header is refused with main's text before parsing. ve/norm_english.py is unchanged. Tests: `test_rights_incident_roundtrip_with_switch` and `test_rights_incident_header_the_renderer_never_writes_is_refused`. |
| 2 | `test_rights_incident_roundtrip_with_switch`, failing on main first. | tests/test_rights.py. It covers a strict line, a default line and a line with two parties. On the base's ve/surface/rights.py it fails with `InvalidInput: rights incident must have one rule`. new-tests-on-base.log ends `4 failed`: the switch, negative, R1-delta and generated tests. The file was restored afterwards (`HEAD-RESTORED`). |
| 3 | A generated round-trip over the rights generator's lines, with the failure count before and after. | `line_roundtrip.py 200` covers every claim, liberty and immunity line with a predicate, in the 159 documents (seeds 0-199 of conformance/rights_differential.py) that correlate: 506 lines. **Before: 180 failed** (71 `InvalidInput: rights incident must have one rule`, the header; 109 `Expected a complete rule sentence`) (line-roundtrip-before.json). **After: 126 failed**, all `Expected a complete rule sentence`, all `unless=2`. Each failing line is listed by seed as `<right>/<line name>` in line-roundtrip-after.json under `failing`. Permanent tests: `test_generated_rights_lines_round_trip_one_by_one` (seeds 0-39, every line with at most one carve-out; it asserts at least 50 lines and at least 5 with a switch) and `test_generated_rights_lines_with_two_carve_outs_round_trip`, a strict xfail tied to rights-cfr-5b that turns red when that fix lands. |
| 4 | A negative test: a header variant that norm_english never renders is still refused. | `test_rights_incident_header_the_renderer_never_writes_is_refused` uses 20 variants: empty parentheses, precedence options (`rule`/`rules`, either order with the switch), a trailing `;`, doubled spaces, case, other wording, a comma list, brackets, NBSP, tab, CR, full-width parentheses and a duplicate party. Each is refused with main's exact text (`\ASyntaxError: expected Claim, Liberty or Immunity of right\Z`). Unsorted and undeclared parties, which are in the rendered spelling, are refused by the soft checker (DELTA row 2). |

The 572-line set of the rights3 builder was not saved, so I could not reproduce it. Its current equivalent is the
506-line set above. The regrade (line 92) did not reproduce it either.

## 2. Seeded bugs (Python; ve/surface/rights.py, the only product file changed)

`bash docs/rights/rights-cfr-5/seeded_bugs.sh` plants each bug, runs the one test named, and restores the file with
`git checkout`. It also restores the file on exit and refuses to run on a dirty file. Output: seeded-bugs.log, which
ends `RESTORED`.

| Bug | Mutation (ve/surface/rights.py) | Failing test (tests/test_rights.py) |
|---|---|---|
| S1 switch dropped on parse | `raw.pop("alterable", None)` in `parse_line` | `test_rights_incident_roundtrip_with_switch` (dict mismatch) |
| S2 non-rendered header accepted | `_rendered_header` returns `True` | `test_rights_incident_header_the_renderer_never_writes_is_refused` (DID NOT RAISE) |
| S3 precedence option let through | the comparison uses `render_header_options(_refs, parties)` | the negative test (`DependencyCycle: rule-1`, not main's text) |
| S6 unparsed header passed on | `except VEError: return True` | the negative test (`Unknown rule header option …`) |
| S4 header dropped on render | `render_line` returns `. ` + body | `test_rights_incident_roundtrip_with_switch` (startswith) |
| S5 switch dropped on default lines | pop `alterable` when `mode == "default"` | `test_generated_rights_lines_round_trip_one_by_one` |

The task's two required bugs are S1 (the condition test fails) and S2 (the negative test fails). DRI adv0838 item
3(b) asks for the negative test to fail on a seeded break: S2, S3 and S6 show it does. No Lean or Rust product code
changed.

## 3. Lines still failing (126 of 506): cause

Every remaining failure is a line with two carve-outs. norm_english renders them as separate sentences:
`Rule 1. Every state must not …, if that person is adult. Except when … . Except when … .` Its own soft parser
(`_parse_soft_english`) does not read that back. At ve/norm_english.py:528, `carveouts = first[sentence_end + 1:]`
keeps the leading space. Line 540 adds another `" "`, so the W1 parser gets `.  Except when` with two spaces and
raises `Expected a complete rule sentence`.

Evidence: `line_roundtrip.py 200 --carveout-probe` applies `carveouts.lstrip()` at :540 in memory only. With it, 0 of
the 506 lines fail (line-roundtrip-carveout-probe.json), so this one cause explains all 126. The task allows
ve/norm_english.py to be edited only to expose the header grammar, and the fix changes what `parse_english` accepts
for whole soft documents. So it is not made here.

FOLLOW-UP: rights-cfr-5b soft norm English: rules with two or more carve-outs do not parse back (double space at ve/norm_english.py:540)

## 4. DELTA, trust, size, pilot bytes, checks

- **DELTA.md:** two rows, no verdict changes.
  - Row 1 is SIGNED by the DRI 2026-11-09 (lp0801 item 1), with its condition test and its negative test in the
    Ruling cell.
  - Row 2 cites R1 and R2. Its fault order is one sentence in the row. Its test is
    `test_rights_incident_header_delta_keeps_base_names_r1`, over header-delta.json.
- **Trust:** `uv run python tools/trust_map.py --check` gives `K +0, S +0, D +0, G +0, tied +0, unclassified +0,
  trusted +0` and `PASS`. No allowance or FOLLOW-UPS.md row was needed.
- **Size:** `git diff --numstat 49f1682dc` gives +752 -5 before this report's final edit.
  - Script output is 344 of those lines: header-delta.json, the three line-roundtrip JSONs, new-tests-on-base.log
    and seeded-bugs.log.
  - Hand-written: ve/surface/rights.py +27/-5, tests +125, and about 260 lines of docs and scripts. That is under
    the ~600 cap.
- **Pilot bytes expected to move:** 0. `render_line` and `parse_line` have no caller in `ve/`; I checked with
  `grep -rn "render_line\|parse_line" ve/`. Document rendering goes through `render_unit`.
- **Overlap check (common rules):** I ran `git diff --name-only main...<b>` for every lean-first, feature, infra and
  foundation branch. None touches ve/surface/rights.py, ve/norm_english.py or tests/test_rights.py. The self-reviewer
  found the same.
- **Spec re-read:**
  - The header options, against docs/spec/rights.md:228-230. That text names `(users may turn off)` as an example
    and gives no grammar of its own, so the renderer's `render_header_options` spelling is the form.
  - The round-trip, against :436 (`print(parse(s)) = s` on canonical text).
  - The spec's `(exception to claim 3 of right 12)` header (:229) is a W1 precedence form on a right line. Neither
    norm_english nor `render_line` renders it, so it stays refused, as the task asks.
- **Evaluators and runners:** no evaluator, runner or mode is added, so the rule does not apply.
- **Not run by me:**
  - the full release gate (the chain runs it);
  - trust_mutants (no Lean changed);
  - lean/audit.py (no Lean changed; `lake build` ran, to build the checkers the tests use);
  - the Rust build (no Rust changed).

## 5. Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relayed answer, schema or relay changed. `parse_line` passes text to the
   existing soft route.
2. Deliverables: PASS. Section 1 gives each deliverable with its test. Rule-break grep: no new Python copy of a Lean
   decision (the header grammar is read from norm_english/softnorms), no report test, no file shared with an
   in-flight branch.
3. Tests can fail: PASS. S1-S6 in seeded-bugs.log, and new-tests-on-base.log (4 failed on base code). The xfail is
   strict.
4. Valid inputs still pass, base against head: PASS. The header-delta.json script runs base against head: 46 equal,
   4 differ, all in DELTA. `test_incident_english_has_one_soft_rule_reading` and
   `test_every_rights_incident_shape_round_trips_with_one_reading` (tests/test_english_unambiguity.py) still pass.
5. R8 binding: N.A. There is no relayed answer field. Undeclared party input:
   `test_rights_incident_header_the_renderer_never_writes_is_refused` (`guest`).
6. Gate evidence on final HEAD: PASS for this item's evidence. It is saved and regenerated by its scripts on the
   committed code: line-roundtrip-*.json, header-delta.json. The chain runs the gate.
7. No unsigned item: PASS. DELTA row 1 is pre-signed with its condition and negative tests; row 2 is R1/R2 with
   `test_rights_incident_header_delta_keeps_base_names_r1`.
8. Every user-visible change in DELTA: PASS. header-delta.json gives the base/head diff over the header variants,
   and line-roundtrip-before/after give the render-side availability (71 lines).
9. Test selection: PASS. tests/test_rights.py is selected for ve/surface/rights.py (the self-reviewer checked with
   select_tests).
10. Lean statements: N.A. No Lean changed.
11. Budgets, limits and deadlines: N.A. No budget path changed.
12. CPU and memory: N.A. Two regex matches and one string comparison per line; there is no document-path caller.
13. Test-removed trailers: N.A. No test was removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. The accept direction is
    `test_rights_incident_roundtrip_with_switch`, the refuse direction is the negative test, and section 4 has the
    spec re-read.
15. No overclaim, no silent cut, checks can fail, limits: PASS.
    - Deliverable 3's "target 0" is not reached. The 126 lines are listed with their cause, as the task allows.
    - The fix is named as rights-cfr-5b; the task's norm_english constraint keeps it out of this item.
    - S1-S6 show the checks can fail.
    - Limits: N.A.

## 6. Next item

None (task: "Next item: none"), apart from the follow-up rights-cfr-5b above.
