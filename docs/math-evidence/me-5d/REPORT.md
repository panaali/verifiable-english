STOP before the wire (DRI choice, no DELTA signature reserved): a follows row's `certificate` and `counterexample`
are computed by Lean and pinned to spec 13.6, but are **not on the wire**. The names inside them cannot be bound to the
request's free values with the response dialect, and a binding relation needs `ve/backends/service_schema.py`, which
this item may not edit (protocol queue). Shipping them unbound would be an R8 B finding. The DRI chooses (a) a dialect
relation through the protocol queue, or (b) ME-3's relay (`ve/calc.py`) binds them (below, "Stop"); the rest is
**me-5e**. Part (2) is already on main (me-2c). Part (3) stops on me-2c's `rests_on` spec gap. DELTA has one row
(R16).

# me-5d report: what a decided derivation shows (math-evidence ME-5, last part)

Base `ab010c3f0` (`git merge-base HEAD main`; me-2c and me-5c on main). Commits: `git log --oneline --no-merges
main..HEAD`. Read first: me-5c's REPORT ("Next item", "Sibling lessons") and me-2c's REPORT (row fields delivered;
`rests_on` stopped on a spec gap).

## Statement gate

ME-S passed its bounded re-checks (manage-agents `math-evidence-p3ver2.final.md`: PASS). This item changes no statement.
`tools/lean_statements.py --check` reports 0 changed (6,625 statements; `lean/statements.txt` is untouched).

- Not edited: the `follows` clauses of `Check.OutcomeMeans`, `follows_of_check` and `counterexample_of_check`
  (`Lower.lean`), `runMode_calc` (`Protocol.lean`) and `runCaseReported_fits` (`Encoders/Calc.lean`).
- `Check.run_sound` keeps its statement. Two `simpa` calls in its claim case now unfold `Check.runShown`, and its follows
  case unfolds `Derive.shown` where it unfolded `Derive.outcome`.
- `Check.run` is spec-opaque. Its body is now `(Check.runShown ds k).1`, and `Check.run_claim` is still `rfl`.

## Plan rows (task order)

| Row | Delivered | Where, checked by |
|---|---|---|
| (1) a follows row's `certificate` and `counterexample` (spec 3.4's table) | **In Lean, not on the wire** (Stop). `Check.runShown` gives the outcome with what it shows (`Shown`: the replayed steps of a holds row, the checked point of a fails row, nothing otherwise) from one search. `Check.run` is its first component, so no derivation is searched twice. `Run.shownJson` writes spec 3.4's form: each step `{"farkas": {"goal": fact, "weights": […]}}` or `{"square": {"square", "root", "a", "b"}}`; a fact `{"const", "coeffs", "strict"}`; one `[name, "n/d"]` per free value read, in declaration order (`Run.reads`: the names of the inlined expressions and of the links, as ME-9's point reads its sides') | `lean/VE/Calc/Run.lean`. `RunExamples.lean` certificate and counterexample table (`:885`): R-3's certificate word for word as spec 13.6 writes it; R-4's counterexample `[["r","1/5"],["s","1/25"],["d","2/125"]]`; H-6p, H-6a, a linear refutation, one premise, stated values only (an empty coefficient list, and a counterexample reading no free value), reads through a definition and two links (an unread free value left out, a name read only by the last expression), a cancelling term, a goal over two unknowns; and `null`/`null` for an inconclusive derivation, the step limit and a claim row; the `runShown` guard for undefined and budget derivations |
| (1) typed in `Schemas/Calc.lean`, encoded with `runCaseReported_fits`, schema regenerated | **no: me-5e** (Stop) | — |
| (2) the follows `line` from `renderFollows` in me-2c's `line` field | **already on main** (me-2c): `Run.line` renders a follows check by `English.renderFollows`. R-3's line is spec 13.6's sentence (`tests/test_calc_service.py::test_rows_carry_leans_sides_display_tie_and_line`, the `line-follows` guard) | nothing to add |
| (3) `rests_on`'s premise and link lines | **no: me-2c recorded the spec gap** (me-2c REPORT "Not delivered"; FOLLOW-UPS "## me-2c", "me-2c spec gap"). As the task directs, no field is added to the case | — |
| Every answer main gives keeps its verdict (base against head on the calc route cases) | yes: no answer changes | the 7 recorded `calc` answers of `tests/data/binding-answers.jsonl.gz` (recorded on main) are byte-identical from the head's `ve_service`; R-1 to R-4 whole-answer goldens and `test_route_cases_answer_their_rows` unchanged and passing |
| Do not edit `Protocol.lean` or `service_schema.py` | kept | `git diff main --stat` |
| Each new check on both sides of each boundary | yes: a certificate only on holds rows and a counterexample only on fails rows, each beside rows of the other outcomes; read and unread free values; first and last links; first and last expressions; one and two coefficients | the table above |

## Stop: binding the names (for the DRI)

R8 makes a missing binding a B finding, and spec 3.4 asks that "every name in a `counterexample` … is a free value of the
request". The dialect cannot express that for these fields:

- **No context.** Within a row, the schema's context is the request's claim entry (`x-zip "/claims"`), which holds
  neither the case's `values` nor the premises' claims.
- **No keyword.** At the answer level, `x-references` reads only arrays of objects (`{field: name}`), while spec 3.4's
  counterexample and coefficients are pairs `[name, "n/d"]`. A path with `*` fails on any row whose field is `null`.
  `_resolve` has no list index, so `x-equals` cannot name `/values/i/name`.
- **Unbound today.** A rebound name (the relay gate's `rebind`) would be accepted, and so would a square step whose
  (square, root) is not one of the derivation's links.

Two ways to close it, both outside this item:

- **(a) A dialect relation.** For example, "this string, or a pair's first element, is the `name` of a request `values`
  entry with `free: true`", and "this pair is one of the claim entry's links". It goes in `lean/ResponseShape.lean`,
  `ve_response_decode` and `ve/backends/service_schema.py`: the protocol queue.
- **(b) ME-3's relay.** The plan (ME-3) already has `ve/calc.py` bind "every claim id, value name and data handle in
  the answer to the request, and each row's kind and kind fields as spec 3.4 lists them". The fields would go on the
  wire once ME-3 lands.

I did not ship the fields with relay-gate allow entries, because that would leave an R8 B finding open. **me-5e** (with
(a) or after (b)):

- `rowJson`'s follows members from `Check.runShown` (one search per row, as now).
- The shape, typed per outcome: a certificate only on holds and a counterexample only on fails.
- `runCaseReported_fits` re-proved.
- R3 tests (each member equals Lean's text, R-3 and R-4 as in 13.6), the R8 fuzz tests, and the relay gate.

FOLLOW-UPS "## me-5d" records this.

## Deviations

- "Read" is the free values that the inlined expressions name, plus the links' names. ME-9's identity point (`Identity.lean:181`) reads its sides
  the same way. A value whose terms cancel is still read (guard `reads-cancel`); one that is declared free but not read
  is left out (guard `reads`, `u`).
- A derivation over stated values alone has a goal with no coefficients and a counterexample `[]` (no free value read):
  spec 3.4's form, with nothing in it.

## Trust (R16)

`tools/trust_map.py --check` on the final code gives K +0, S +0, untied V +41, and PASS with the allowance in
`docs/trust-baseline.json`. All 41 lines are in `lean/VE/Calc/Run.lean`: D[V] `Shown`, `Run.factJson`, `Run.stepJson`,
`Run.reads` and `Run.shownJson`. `Derive.shown` and `Check.runShown` are C (`tools/trust-classes.json`); `Derive.outcome`
is gone. The ties pass is in FOLLOW-UPS "## me-5d". `ve/assurance-manifest.json` pins `Run.lean` whole (365 lines,
`shownJson` added to its declarations), and the decoder total goes from 38,587 to 38,635.

[`trust-mutants.json`](trust-mutants.json) comes from `mac-pytest.sh --trustmut -- --max-mutants 1000` on the final Lean
change (ve-mac-1, a full run): 91 killed, 0 survivors, 0 unknown, 24 invalid, 8 allowed, exit 0.

- **First run** (a83d734a): 6 survivors and 20 unknown.
  - The survivors are now killed by two fixtures: a goal over two unknowns (a coefficient list cut to its first or last
    entry), and the reads case with a second link and a name read only by the last expression.
  - The unknown mutants failed to elaborate away from the mutated text, because lambda types were inferred late. With
    typed lambdas, 12 of the 20 became ordinary mutants.
- **Allowed** ([`trust-mutants-allow.json`](trust-mutants-allow.json)): the 8 mutants Lean refuses at their own line.
  They are `list-empty` on a list whose `map`/`flatMap`/`filterMap` keeps its function argument, and `append-right`
  leaving `flatMap` with no function. The same lists cut by `list-first`, `list-last` and `list-drop-last` are killed.

## Seeded bugs ([`mutants.json`](mutants.json), 12, all Lean, each applied alone and restored)

All are in `lean/VE/Calc/Run.lean`. Every one fails a named `#guard` or proof:

- **`Derive.shown`:**
  - A holds row shows nothing: the guard at `RunExamples.lean:885`.
  - A fails row is reported as holds: `Check.run_sound` no longer closes (`Run.lean:142`).
- **`Check.runShown`:** the step limit is read as inconclusive: the derivations table, `:637`.
- **`reads`:** unfiltered, first-appearance order, and links dropped: `:885`, `reads`.
- **`factJson`:** strict flipped, and the constant negated: `:885`, `r3`.
- **`stepJson`:** weights reversed, and square and root swapped: `:885`, `r3`.
- **`shownJson`:** the point's values zeroed (`r4`), and only the first step kept (`r3`).

No Python or Rust product code changed (`ve/assurance-manifest.json` is a manifest, and the rest is generated), so
there is no seeded bug there.

## Tests and checks run

- **Builds and checks:** all pass.
  - `lake build` (whole library, 1,118 jobs).
  - `python3 lean/audit.py`: PASS, 638 files.
  - `tools/lean_statements.py --check`: 0 changed.
  - `regen_generated.py --check`: 33 entries.
  - `repo_map.py --check`, `assurance_manifest.py --check` and `trust_map.py --check`: PASS.
  - `gate_collection.py --check --prebuilt`: 0 added, 0 removed, 0 refused, 0 stale, 0 malformed.
- **Selected tests:** `mac-pytest.sh --select -- --base ab010c3f0 --run` on c2de14d98 (ve-mac-1), exit 0.
  - 369 of 466 units ran, with 0 failed.
  - They include `lake build`, `test_calc_service`, `test_calc_derive`, `test_route_row_schemas`,
    `test_assurance_manifest`, `test_relay_mutation_gate`, `test_trust_mutants` and `test_enum_domains`.
  - The commits after it add only this report, DELTA and `mutants.json`.
- **Base against head:** the 7 recorded `calc` answers are identical (above).
- **Not run:** the full gate (the chain's). No test in `main-known-red.txt` is touched.

## Size

Hand-written lines over the merge base (`git diff --numstat`), about 360 in all:

- **Lean product:** 90 (`Run.lean`).
- **Fixtures:** 64 (`RunExamples.lean`).
- **Side tables:** 32 (`trust-classes.json`, the allowance and the manifest).
- **Evidence and docs:** about 175 (the allow file, `mutants.json`, DELTA and this report).

Generated files: `declarations.txt`, `checkers.lock`, `trust-mutants.json` and `assurance-manifest.md`.

**Bytes:** 0 expected (plan ME-5); nothing is claimed before a pilot audit.

Shared files: `tools/trust-classes.json`, `ve/assurance-manifest.json` and `docs/trust-baseline.json` (registries). No
branch in flight edits `Run.lean`, `RunExamples.lean`, the calc shape or encoder, or the calc tests (checked against every
`lean-first/*`, `feature/*`, `infra/*` and `foundation/*` branch; `feature/qt-a3b` edits only
`lean/VE/Cardinality/RunExamples.lean`).

## Next item

- **me-5e**: the certificate and counterexample on the wire, after the DRI's choice above.
- R-10a after ME-4; me-9's follow-ups (R-10c after ME-4); then ME-7.

## Sibling lessons (me-2c review)

- **F1, re-evaluation per field.** One search gives both the outcome and what it shows (`Check.runShown`;
  `Check.run` is its first component). The rendering evaluates nothing, and `reads` inlines only for a fails row.
- **F2, a `null` field recorded but not named in the next item.** What does not fit is named: me-5e, with its parts
  listed under "Stop".
- **Checks on one side only.** Each outcome has its own rows beside the others' (above).

## Self-review against BUILDER-CHECKLIST

1. **N.A.:** no answer member changes, so no relayed field is new. The calc corpus's existing mutation tests still pass
   (`test_route_row_schemas`, `test_relay_mutation_gate` in the selection).
2. **PASS:**
   - The plan-row table above names each row's commit and check. (1) stops before the wire for a DRI choice (Stop),
     (2) is on main and (3) is a spec gap; me-5e is named.
   - There is no Python copy and no report test, and no branch in flight overlaps.
3. **PASS:** `mutants.json` (12 of 12 caught) and `trust-mutants.json` (exit 0, allow file).
4. **PASS:** base against head, the 7 recorded calc answers are identical; the R-1 to R-4 goldens are unchanged. No
   Python or Rust implementation exists.
5. **N.A.:** nothing new is relayed. Binding the new names is the stop reason, with me-5e.
6. **PASS:** the base is from `git merge-base`, the commits from `main..HEAD --no-merges`, and the full gate is the
   chain's.
7. **PASS:** the DELTA row cites R16 and no row is reserved. The DRI choice is in the first line, and there is a
   FOLLOW-UPS "## me-5d" row.
8. **PASS:** DELTA says no answer changes, with the evidence: `test_route_cases_answer_their_rows` and the RunExamples
   goldens.
9. **PASS:** the selection ran 369 units with `lake build`. Every seeded bug fails `lake build VE.Calc.RunExamples`,
   which the selection's `lake build` covers.
10. **PASS:** statements unchanged (`lean_statements --check`: 0). `seed-fails-as-holds` breaks `Check.run_sound`.
    `Check.run` is the first component of the same `runShown` whose second component is shown.
11. **PASS:** no limit changes. A derivation at the step limit or the budget, or one that is inconclusive or
    undefined, shows nothing (guards `chain-13`, `inconclusive`, the `runShown` guard); its outcome stays unknown or
    undefined.
12. **PASS:** one search per derivation (`Check.run := (runShown ds k).1`), and no new evaluation on any path a row
    takes. `reads` runs only when rendering a fails row, which is not on the wire yet.
13. **PASS:** no test removed (`gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed).
