# ap-4b report: `Source`, `sourceCheck`, `sourceCheck_exact` and `atomSituation`

- **Status:** built, Lean only; no DRI signature reserved; DELTA's one row (trust S +68, V +15, K +0) cites R16.
- **HEAD:** branch tip of `feature/ap-4b`; base `09fca5013` (main).
- **Changed:** `lean/VE/Acts/Sources.lean` and `lean/VE/Acts/Situation.lean` (new), the fixtures in
  `lean/VE/Acts/ReadingsExamples.lean`, registration and generated lists, the trust side tables, one assurance-manifest
  reason.
- **Open:** nothing reaches a route (by design: ap-4 adds the `act-readings` mode and the admission hook);
  `sourceCheck_complete` is not built (below). Next: AP-7 on `phraseReadings`, then ap-4.
- **Evidence:** 31 seeded bugs, all killed; trust mutants 0 survivors, 0 unknown; selected tests: one failure, fixed,
  its rerun passes; full gate is the chain's.

## Scope and what reaches users

Plan (`docs/spec/act-phrases-PLAN.md` at `80f056f9e`), AP-4 and section 3's `Source`, `sourceCheck`,
`sourceCheck_exact` and `atomSituation`; spec `docs/spec/act-phrases.md` 1.8 and 7 on main. The plan's section 3
gives `sourceCheck_exact` with `(D fs fx N b)`; the task's statement gate names spec 7's text, and spec 7 is the
reviewed statement (draft 2's SR3 and SR14 added `unspec` and the comparison up to order), so this item builds
spec 7's text. Nothing in this item reaches a route, relay or answer: only `VE.lean`, the generated `VE/Audit.lean` and
the fixtures import the two modules; no file under `lean/VE/Readings/`, `lean/VE/Service/`, `ve/` or `rust/` changes.
ap-4b implements no synthesis round 2 edit: round 2 (`f2b1d4634`, `80f056f9e`) changed AP-0 to AP-8's estimates and
AP-3's u0123 text only (as ap-4a's report records).

Statement gate: the plan's statement review accepted AP-4's statements (spec 7; plan change log item 11). Probe
`python3 docs/act-phrases/ap-4b/check_statements.py` cuts each declaration from spec section 7 and from the Lean file
and compares the whitespace-normalised text; output: 13 lines, all `EQUAL` (`theorem sourceCheck_exact`,
`def SourceExact`, `structure Source`, `abbrev View`, `def expected`, `def choicesOn`, `def choiceViews`,
`def readingViews`, and the signatures of `ruleView`, `choiceRules`, `opOfSource`, `sourceCheck`, `atomSituation`).

## Plan rows delivered

Fixture lines are `lean/VE/Acts/ReadingsExamples.lean`'s.

| Task deliverable | Where | Evidence |
|---|---|---|
| (1) `Source` and `sourceCheck`: a bijection between readings and choices, complete against the grammar; each choice's rules keep the template's modal (role and sign), guard, carve-outs, precedence and completion; the completion three-valued, read from the original metadata (`unspec`), not the frame's placeholder; rules compared up to order | `Sources.lean`: `Source`, `View`, `ruleView` (completion by `VE.NormDefaults.completionOf` with `unspec`), `expected`, `choicesOn`, `choiceRules`, `choiceViews`, `readingViews`, `opOfSource` (`opOf`'s table, one owner), `compareViews`, `sourceCheck` | 163 (S1), 164 (S8), 167 (projection), 169 (S2), 173 (S3), 176-177, 179 (template's guard, carve-outs, precedence, completion `allow` and `unspecified`, role), 184 (a rule's guard), 198-208 (S4 to S7, other modals), 214 (largest sizes), 222 (budget 0), 244-248 (D-29's other texts) |
| (2) `sourceCheck_exact` | `Sources.lean`, with `compareViews_ok` and `pick_forall₂` | proved; statement EQUAL (above); `lean/audit.py` PASS |
| (3) `atomSituation`, checked by `separates` | `Situation.lean` | 255 (u105 and u055 candidates separated both ways), 258 (the probe), 263 (two-argument acts), 265 (constants), 270 (one act: `holds`, not separated) |
| (4) rs_u055 and rs_u105b/rs_u105c with their coupling pass; refused: skipped middle, missing reading, permission to prohibition, `unspecified` to `deny` (S7); passing: another order (S8) | fixtures | 198 (S4), 163 (S1); 173 (S3), 169 (S2), 199 (S5), 205 (S7); 164 (S8) |
| F11: a reading that is a whole join has no candidate; u076 the residual | fixtures | 229 (u076's set refused: the one-act reading has no choice), 236 (the readings frame refuses the one-act reading as the source words it, D-33, and as `expected` renders it, D-1) |
| Seeded bug: rs_u105b/c refused when the "all" reading is dropped | `e1x-all-dropped` (Grammar.lean, upstream guards off) | killed by 163 (S1), 164 (S8), 167, 169 and others ([mutants.json](mutants.json)) |
| Computed once, size charged against a stated limit (feature rule) | `sourceCheck` lexes, lists the readings (`phraseReadings`, at most 64: `phraseReadings_length`) and the choices (`VE.Readings.choices`, cut at 65) once each; each comparison step makes at most 65 × 64 permutation tests | 214: L6's 64 readings against 7 uncoupled sets of two (128 choices, cut at 65) refused within the module's build (`lake build VE.Acts.ReadingsExamples`, 86 s including its imports' rebuild) |

u076 (A11) is the residual named by spec F11: its one-act reading is a whole join, which the readings route's frame
refuses (D-33), so its reading set cannot pass `sourceCheck` until the readings elaboration is specified and reviewed.

Not delivered: `sourceCheck_complete` (spec 7 states it; the task's deliverables do not list it; the check is written
so that it should hold, each refusal meant as one of `SourceExact`'s conjuncts failing, which is not proved here); the `act-readings` mode, relay,
admission hook, Python fuzz and AR1 to AR5 (ap-4).

## Deviations from the spec text (no statement changes)

1. **`List.Forall₂` is defined in `Sources.lean`.** Spec 7's `SourceExact` names Mathlib's `List.Forall₂`; this project
   has no Mathlib, so the file defines it with Mathlib's two constructors. The statement's text is unchanged.
2. **Diagnostics outside D-29.** A lexing error is the lexer's; no op (a plain act with sign false) is
   `InvalidInput: the source has no modal word for its act`; the limit is `ResourceLimit: the source phrase has too
   many readings to list; split the sentence` (D-17's wording with the source phrase as subject). D-29's four texts are
   the spec's, in this order: a choice that is no reading (so S5 and S7 name the changed modal or completion), two
   choices that are one reading, a reading with no choice (S2, named by its paraphrase), the counts. No route shows
   them yet; ap-4 relays them.
3. **S3 is the plan's skipped middle.** Spec 11.4 writes "a candidate putting *freely* on `enjoy` only", but u105a
   (*freely* on `participate`) is fixed in every reading, so no choice can leave `participate` without *freely*; the
   fixture adds the plan's "skipped-middle candidate" (*freely* on `participate` and `share`, not on `enjoy`).
4. **The pilot sets re-written (finding F3).** One candidate holds one rule, so a reading of two or three simple acts
   is the shared fixed units (`Source.units`) plus one candidate per set: rs_u105b and rs_u105c coupled on `freely`
   with u105a fixed; rs_u055 as u055a (the arbitrary deprivation, fixed) and one set (`deprivation_only`,
   `both_acts`) reading the denial. Frames are decoded by the readings route's own decoder; `unspec` by
   `VE.Readings.Wire.unspecOf`.
5. **`choiceRules` reads the projected choice.** A set the choice does not name contributes no rule, and
   `choicesOn` names the listed sets only, so `choiceRules` tests `Source.units` for fixed units and nothing for sets
   (a test of `Source.sets` there was an equivalent mutant, removed). A listed unit or chosen candidate whose content
   is not a rule contributes no rule, so its choice cannot equal a reading.
6. **`atomSituation`'s probe** is `selects "norm" p` for the act `p` of witness `i`'s rule that `j`'s rule does not
   regulate (a rule on `p` selects in `i`'s document and none exists in `j`'s); the base has one element `0` in every
   sort, every constant names it, every relation and generated table is empty, and the value is `true`. A template
   guard that fails on the empty base makes `separates` refuse, which is the check's own answer.
7. `View`'s decidable equality is declared once with `synthInstance.maxSize 1024` (a seven-field product exceeds the
   default instance size).

## Overlap with branches in flight

At the start (`git diff --name-only main...<branch>` over `lean-first/*`, `feature/*`, `infra/*`, `foundation/*`):
no hand-written file of this item is touched elsewhere; `lean/VE.lean` (one import line each, cmp-s2b, pc-3, sc-5rd,
sn-b6, me-1) and `tools/trust-classes.json` (several) are shared registration files whose additions sit in separate
hunks.

## Seeded bugs (Lean; no Python or Rust product code changed)

`python3 docs/act-phrases/ap-4b/seed_bugs.py` plants each, builds `VE.Acts.ReadingsExamples`, restores; results in
[mutants.json](mutants.json): 31 plants, 31 KILLED, `restored_build_returncode` 0. At least one plant per new trusted
definition (`tools/trust_map.py`'s S and V lists) and per claimed behaviour.

| Plant | File | Definition | Killed by |
|---|---|---|---|
| e1x-all-dropped (the plan's) | Grammar.lean | globalRules | ReadingsExamples 163 (S1), 164 (S8), 167, 169, and A8's 38, 40, 49, 86 |
| forall2-unrelated | Sources.lean | List.Forall₂ | `pick_forall₂` (Sources.lean 139) |
| source-no-units | Sources.lean | Source | Sources.lean 64 (`choiceRules` reads it) |
| view-no-completion | Sources.lean | View | Sources.lean 49, 55 |
| ruleView-placeholder | Sources.lean | ruleView | 202 (S6), 203 |
| ruleView-sign | Sources.lean | ruleView | 198 (S4), 202 |
| ruleView-guard | Sources.lean | ruleView | 184 |
| expected-guard, expected-over | Sources.lean | expected | 179 |
| choicesOn-no-dedup, choicesOn-no-projection | Sources.lean | choicesOn | 167 |
| choiceRules-no-units, choiceRules-all-units, choiceRules-no-sets | Sources.lean | choiceRules | 163-169, 198, 202; 177; 163-169, 198, 202 |
| choiceViews-unspec | Sources.lean | choiceViews | 202, 203 |
| readingViews-first | Sources.lean | readingViews | 163, 164, 167, 169, 198, 202, 222 |
| opOfSource-sign | Sources.lean | opOfSource | 163 and eleven others |
| sourceExact-ordered (σ in the readings' order) | Sources.lean | SourceExact | `sourceCheck_exact` (176) |
| sourceCheck-no-compare, sourceCheck-no-paraphrases | Sources.lean | sourceCheck | `sourceCheck_exact` (175; 162, 174, 176) |
| compare-no-reading-check | Sources.lean | compareViews | 173 (S3), 176, 177, 179, 199 (S5), 203, 205 (S7), 207 |
| compare-no-pairwise, compare-no-bijection | Sources.lean | compareViews | `compareViews_ok` (155) |
| pick-any | Sources.lean | pick | `pick_forall₂` (138) |
| d29-no-code | Sources.lean | d29 | 169 and eleven others |
| atom-value-false, atom-probe-other, atom-shared-act, atom-tuple-one, atom-constant-outside | Situation.lean | atomSituation | 255, 263; 255, 258, 263; 270; 263; 265 |
| rulePred-none | Situation.lean | rulePred | 255, 258, 263 |

## Trust

`uv run python tools/trust_map.py --check` on the final code: K +0, S +68, D +0, G +52 (tied +35), unclassified +0,
trusted +83 against `09fca5013`: Sources.lean +68 (S), Situation.lean +15 (untied G[V]); "PASS: K, S and untied [V]
within 09fca50130a0 and the allowances introduced since". Recorded with `trust_map.py --allow` ("SIGNED by standing
ruling R16 (DRI-RULINGS.md), ap-4b, 2026-10-18"); FOLLOW-UPS.md "## ap-4b" asks for the ties pass
(`sourceCheck_complete`, and a theorem tying `atomSituation` to `separates_separated`).

`tools/trust_mutants.py` (checklist 13a, `mac-pytest.sh --trustmut`; ran on the VM, Mac slots busy), final evidence
[trust-mutants.json](trust-mutants.json) at head `c17a28414`, base `09fca5013`: 161 mutants of the 10 trusted
definitions, KILLED 111, SURVIVOR 0, UNKNOWN 0, INVALID 12, ALLOWED 38, exit 0 (log summary: "111 KILLED, 0 SURVIVOR,
0 UNKNOWN, 12 INVALID, 38 ALLOWED, 0 NOT RUN in 6321 s"). Allowed, with one-line reasons in
[trust-mutants-allow.json](trust-mutants-allow.json): cuts of the Props `SourceExact` and `List.Forall₂`, which no check
evaluates and whose cuts break `sourceCheck_exact` or `pick_forall₂` (R16: a Prop is exercised by its proofs);
ill-typed cuts; and `opOfSource`'s placeholder `allowByDefault` flag, which `opOf` does not read. History: the first
run (`193b1c542`) left 37 survivors and 12 unknown; besides those classes, `rulePreds`' one-element list (now
`rulePred`, an option), `atomSituation`'s tuple arity and its constants were unchecked: fixtures 263 and 265 added.

## Tests

- While iterating: `lake build` of the edited modules and their fixtures only.
- `cd lean && lake build`: 1189 jobs, exit 0; `python3 lean/audit.py`: "PASS: 691 source files; 7755 named theorem
  declarations audited".
- `uv run python tools/regen_generated.py --write --skip route-cases`: "wrote 33 entries". `route-cases` is skipped
  because it needs the Rust release binary (`rust/target/release/ve`, absent here) and this item changes no route.
- Selected tests, once, on `c000f61c5`: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`: 87 of 511
  units, ve-mac-1, "1 failed, 137 passed" in `tests/test_assurance_manifest.py`
  (`test_every_json_handling_lean_file_is_classified`: ReadingsExamples.lean now builds JSON); fixed by its
  `other_json` reason in `ve/assurance-manifest.json` (6e14faf80); the failed id rerun on ve-mac-1: "1 passed", exit 0.
  One file was deferred to the chain gate by the selector (`tests/test_safety_framework.py`, weak reason).
- `uv run python tools/gate_collection.py --check --prebuilt`: "31006 collected, 31006 at 09fca50130a0; 0 added,
  0 removed by a trailer, 0 refused, 0 stale and 0 malformed trailers" (no test removed).
- Pre-existing failures on main (`main-known-red.txt`): none selected or touched here.
- Not run: the full release gate (the chain runs it on the final HEAD); Python or Rust tests of a changed path (none).

## Size

Hand-written lines against the merge base (`git diff --numstat`): Lean product 209 (Sources.lean 179, Situation.lean
30), fixtures 174, `VE.lean` 2; evidence scripts and allow file 202 (`seed_bugs.py` 127, `check_statements.py` 55,
`trust-mutants-allow.json` 20); trust side table 85 (`tools/trust-classes.json`), assurance manifest 1; this report and
DELTA. Measured at 359 when deliverables (1) to (4) and their fixtures were done; the evidence the rules require
(seeded bugs per trusted definition, trust mutants, statement probe) and the fixtures they asked for took it past
600. No deliverable was added beyond the task's; the cut candidate would have been `atomSituation` (about 75 lines with
its fixtures and plants).

## Pilot bytes

0 by itself (an estimate; nothing is claimed before a pilot audit). u092's 163 B (M1) and M2 (u055 checked exact) need
ap-4's admission hook; u076's 125 B also waits for the readings elaboration (spec F11).

## Next item

AP-7 on `phraseReadings`, then ap-4 (the `act-readings` mode, relay and the admission hook in
`lean/VE/Readings/Run.lean`, which calls `sourceCheck` with `UnspecifiedWire.unspecOf re D` and writes
`atomSituation`'s situations). `sourceCheck_complete` goes with the ties pass (FOLLOW-UPS "## ap-4b").

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer is fully typed and contained: N.A., no route, relay or answer reads anything this item adds
   (DELTA "Public output: none").
2. Every required deliverable is built: PASS, "Plan rows delivered" (each with its file and guard lines); no Python or
   Rust file, no Python copy of a Lean decision (`opOfSource` reads `opOf`, `ruleView` reads `completionOf`).
3. Tests and gates can fail: PASS, [mutants.json](mutants.json) (31 plants, 31 KILLED, one per trusted definition and
   per behaviour) and [trust-mutants.json](trust-mutants.json) (0 SURVIVOR, 0 UNKNOWN, exit 0).
4. Python, Lean and Rust agree; valid inputs still pass: N.A. for the comparison (Lean only); PASS for valid inputs:
   S1, S4, S6, S8 and the projection fixture pass (ReadingsExamples 163, 164, 167, 198, 202), and every existing
   ReadingsExamples guard passes (`lake build`, 1189 jobs).
5. R8 binding: N.A., no relay (ap-4 binds `act-readings`).
6. Gate evidence matches the final HEAD: PASS for the saved evidence (trust mutants at `c17a28414`, the last Lean
   change; later commits change the evidence, this report, DELTA and the assurance manifest only); the full gate
   is the chain's, on the final HEAD.
7. No unsigned item: PASS, DELTA row 1 cites R16 with `trust_map.py --check`, the plants and the trust mutants; no
   signature reserved.
8. Every user-visible change in DELTA: PASS, no public output changes, so the only row is the trust growth.
9. Test selection finds the tests: PASS, `select_tests` picked 87 of 511 units, including
   `tests/test_assurance_manifest.py`, which found the unclassified JSON fixture file.
10. Lean statements say what is claimed: PASS, the statement probe (13 EQUAL); plants that break each theorem
    (`sourceExact-ordered`, `compare-no-pairwise`, `compare-no-bijection`, `pick-any`, `forall2-unrelated`);
    `sourceCheck_exact` is about `sourceCheck`'s own result.
11. Budgets and limits fail closed: PASS, budget 0 is a `ResourceLimit` refusal (222), the 64-reading listing against
    65 choices is refused (214), and `phraseReadings`' `limit` is never success (`sourceCheck`'s `.limit` arm).
12. No CPU or memory regression: PASS, no route or pilot reaches the new code; `sourceCheck` evaluates each value once
    and its comparison is bounded by 64 readings and 65 choices (214).
13. Removed tests have a trailer: PASS, `gate_collection.py --check --prebuilt`: 0 added, 0 removed, 0 stale.
14. Both directions, cited evidence, spec re-read: PASS. Both directions: S1/S8 pass and S2/S3/S5/S7 refused; the
    completion `unspecified` passes and `deny` refused (202, 203, 205); the projection keeps and drops (167, 176);
    separation true both ways and false on one act (255, 263, 270); D-29 accepts and refuses on views (244-248).
    Spec re-read: `Source`, `View`, `ruleView`, `expected`, `choicesOn`, `choiceViews`, `readingViews`, `SourceExact`,
    `sourceCheck_exact` and `atomSituation` against docs/spec/act-phrases.md section 7 (the probe), D-29's texts
    against section 10, S1 to S8 against 11.4, F11 against 14.2, 1.8, and plan AP-4 (lines 936-993 at `80f056f9e`).
