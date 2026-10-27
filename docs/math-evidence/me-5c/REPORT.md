No DRI signature is reserved: DELTA rows 2-4 cite R2, R1 and R16. Row 1 (the `follows` check, `premises` and free
values are now accepted, which the base refused) cites SYNTHESIS 4.1 and the plan's ME-5 as the DRI decision that
schedules them, as ap-1b's and me-2b's DELTA cite SYNTHESIS for their plan rows; this task names no item-specific
exception for that citation, so if the DRI does not accept it, row 1 is the one that needs a signature. Size: about
860 hand-written lines, over the ~600 guide (below, "Size"); the follow row fields are cut to **me-5d**.

# me-5c report: the `follows` check of the `calc` mode (math-evidence ME-5)

Base `110b3bf3a` (`git merge-base HEAD main`; me-2, me-2b and me-5b on main); commits `git log --oneline --no-merges
main..HEAD`. Read first: me-5b's REPORT ("Next item", "Delivered", "Sibling lessons") and me-2's REPORT
(`docs/math-evidence-me-2/REPORT.md`).

## Statement gate

ME-S passed (manage-agents `math-evidence-p3ver2.final.md`: PASS). After collapsing whitespace, a script finds each of
these in both spec 3.4 / 5 (main) and the Lean files: the `follows` constructor of `Check`; `Check.exprs`'s follows arm;
`Check.keep`'s wildcard arm; both arms of `Check.reasons` this item has; `Check.UnknownCause` whole; `Check.OutcomeMeans`
with its claim, follows (holds, fails), undefined and unknown clauses (J3) in the spec's order; `Check.run_sound` and
`Check.run_claim` unchanged; `follows_of_check`. J3's statement fits me-2's `Check` with no change: the consistent and
identity constructors and arms are ME-8's and ME-9's ("each batch adds its constructor, its clauses and its case of
`Check.run_sound`"). `Follows`, `HasCounterexample`, `follows_of_check`, `counterexample_of_check` and
`Claim.facts_sound` are untouched (`Lower.lean`'s diff is `Expr.linear`'s body and three new lemmas).

## Delivered (task order)

| Row | Delivered | Where, checked by |
|---|---|---|
| (1) `follows` in me-2's `Check` and wire, the case's `premises`, `NonlinearPremise` | yes: `Check.follows P links C` with premise ids resolved; `free` values; `premises` (`eq`, `lt`, `le`, `gt`, `ge`, `within`; `support` required); conclusions `lt`, `le`, `gt`, `ge`; `UnknownPremise`, `UnknownLink` (a link names two free values), `NonlinearPremise: <path>` (the innermost part not linear once inlined, by its JSON path), limit 8 (512 premises); premises and free values hashed (3.3) | `lean/VE/Calc/Wire.lean`; RunExamples: the derivations table (every refusal and both sides of each limit), the identity families `premises`, `derivation`, `free`, the malformed-value guard |
| (2) the runner over `Claim.facts` and `Derive.search`, J3's clauses, `Check.run_sound` | yes: `Check.run` for a derivation: the first inlining fault (undefined, budget), the `maxPolyTerms` node bound on each inlined expression, then `Derive.search` over the lowered facts, `holds` only when `Derivation.check` replays the certificate (`follows_of_check`), `fails` only when `counterexampleCheck` holds (`counterexample_of_check`); `Check.run_sound` proved for both kinds, `Run.row_sound`, `Run.unknown_named` and `Run.verdict_sound` unchanged in statement; rows carry `kind` (`"follows"` / `"claim"`), bound to the request entry in `calc.json` | `lean/VE/Calc/Run.lean`; R-3 and R-4 pinned whole; `ResponseShape.Encoders.Calc.runCaseReported_fits` |
| (3) J10's rendering | `VE.Calc.English.renderFollows`: the premises numbered, each link `(s, r)` as "S equals the square of R." and "R is at least 0.", then "From these, it follows that …"; R-3's line of spec 13.6 word for word, from R-3's decoded case. **The `line` and `rests_on` row fields are me-2c's** (not on main): the rendering is not on the wire yet, and `rests_on`'s premise and link lines (J10's residual line) go with them (me-5d) | RunExamples J10 guards (one and two links) |
| (4) R-3, R-4 as JSON cases and `tests/test_calc_derive.py` | yes: spec 13.6's requests in `tests/data/route-cases.jsonl` and `tests/data/relay-gate-cases.jsonl`; `test_calc_derive.py`: H-6 (R-3), H-6p, H-6n (R-4), H-6a without the link, `le`; the refusals; `kind` bound. The forged negative-weight certificate and H-6a's s = 0, r = 1 are refused at the level of facts by `DeriveExamples.lean`'s guards (lines 31, 44-50, 62-68): the service never takes a certificate or an assignment from a request, so at the service level H-6a is the derivation without the link (`fails`) against R-3 (`holds`) | `tests/test_calc_derive.py`, `tests/test_calc_service.py`; the binding census re-recorded (`--answers`) |
| R-10a | waits for ME-4 (task) | — |
| a follows row's `certificate` and `counterexample` (spec 3.4's table) | **me-5d** (size rule; with me-2c's row fields) | FOLLOW-UPS "## me-5c" |

Cost (me-5b checklist 12, me-2b's F1): one inlining table per derivation (`Claim.inline` is now `Claim.subst` over
`inlineTable`, `Claim.factsIn_eq`), the node bound before lowering, and `Expr.linear` normalises each sum
(`QLin.norm`, proved by `QLin.eval_norm`). Before the normalisation one derivation over a 400-step definition chain
with 60 premises took 114 s; after it, 0.08 s (a /tmp script through `ve_service`, not in the suite). The guard
"a chain of definitions lowers to one coefficient per unknown" pins it without timing; the 12- and 13-step doubling
chains pin the node bound on both sides.

## Deviations

- `NonlinearPremise` names the part by its JSON path (`premises.0.claim.2`), not by a rendering: the decoder has no
  words for values (me-2c), and a path has no symbol (13.1's rule).
- A division by a part that inlines to the constant 0 is `NonlinearPremise` (me-5b's `Expr.linear`), where C26's
  reading would admit it as undefined: the refusing side; FOLLOW-UPS.
- Past `maxPolyTerms` nodes an inlined expression is `unknown (limit .derivationSteps)`: spec 5's limits have no node
  count, and this is the derivation's own limit reason (1.5).

## Trust (R16)

`trust_map.py --check` on the final code: K +0, S +22, untied V +58, trusted +80, PASS with the allowance recorded
(`docs/trust-baseline.json`); per file in DELTA row 4. FOLLOW-UPS "## me-5c" asks for the ties pass.
[`trust-mutants.json`](trust-mutants.json) (`mac-pytest.sh --trustmut -- --max-mutants 1000`, ve-mac-1, the last run
rescored on the final Lean change): 133 killed, 0 survivors, 0 unknown, 28 invalid, 35 allowed, exit 0. The first run
had 26 survivors and 18 unknown; the survivors that a check can reach got fixtures (two links, two premises in order,
a fault in the conclusion's first operand, each kind's reasons read from the runner's unknown rows, two rendered
links). Allowed ([`trust-mutants-allow.json`](trust-mutants-allow.json)): `OutcomeMeans`'s follows and undefined
clauses and `UnknownCause`'s general arm, propositions over every assignment that no evaluated check reads (each breaks
`Check.run_sound`: `mutants.json` outcome-means-*, unknown-cause-*); type-error mutants of patterns and lists; and two
equivalent mutants of `decode` (`take 1` of a list of at most one element, and of `cprems` inside `isEmpty`).

## Seeded bugs ([`mutants.json`](mutants.json), 38, Lean; each applied alone and restored)

- The plan's: `Farkas.check` accepts a negative weight. It breaks `Farkas.check_sound`; with that proof stubbed, the
  forged-certificate regression (`DeriveExamples.lean` 67-68) fails.
- One per new clause of `OutcomeMeans`: holds, fails and undefined swapped or weakened, and the general unknown arm
  (`u ∉ k.reasons`, `∀` for `∃`): each breaks `Check.run_sound`.
- Runner: replay skipped, counterexample unchecked, the step limit read as inconclusive, the node bound at 8,000, a
  premise dropped, two conclusion facts accepted, each fault mapped to the other outcome, faults read in reverse, free
  values not kept, `factsIn` reordering facts (proofs or the R-3, chain-12/13 and declaration guards).
- Wire: conclusion `eq` admitted, an unknown premise resolved to the first, links swapped, a `rounds` premise admitted,
  `UnknownLink` admitting a stated value, the outermost nonlinear part named, the nonlinear bound at 8,000, conclusions
  not judged, limit 8 at 513, `free: false` admitted, premises not hashed, premise names not checked, premise ids out
  of the claim namespace (RunExamples guards, each named).
- Rendering: the root's line "at most", links before the premises (J10 guard). `Expr.linear` without `norm`,
  `Claim.subst` reading `a` twice (proofs and guards).
- Shape: the claim branch of `kind` without its `x-case` fails `tests/test_calc_derive.py::test_a_rows_kind_is_its_requests`.
- Python and Rust product code are unchanged, so no seeded bug there.

## Tests and checks run

- `lake build` (whole library, in the selection), `python3 lean/audit.py` (PASS, 618 files), `regen_generated.py
  --check` (33 entries), `repo_map.py --check`, `check_lean_imports.py`, `trust_map.py --check`,
  `gate_collection.py --check --prebuilt` (12 added, 0 removed, 0 refused, 0 stale, 0 malformed).
- Selected: `mac-pytest.sh --select -- --base 110b3bf3a --run` on 3f27820e6 (ve-mac-1): 379 of 463 units, 0 failed,
  exit 0 (`test_calc_derive`, `test_calc_service`, `test_route_row_schemas`, `test_relay_mutation_gate`,
  `test_shape_binding_mutants`, `test_assurance_manifest`, `test_trust_mutants` among them). The commits after it
  change only `RunExamples.lean` guards (built: `lake build VE.Calc.RunExamples`), evidence and docs.
- Not run: the full gate (the chain's). No test in `main-known-red.txt` is touched.

## Size

Hand-written lines over the merge base (`git diff --numstat`, generated files and the tool's evidence excluded): Lean
product 347 (`Wire.lean` 128, `Run.lean` 120, `Lower.lean` 52, `Inline.lean` 14, `Render.lean` 10, the shape and
encoder 23), fixtures 230 (`RunExamples.lean`), Python tests and cases 71, side tables 46 (`trust-classes.json`, the
assurance manifest), evidence and docs about 190 (`mutants.json`, the allow file, DELTA, this report): about 860. The
size check before the second half (`d905039e6`, 398 lines) left room for (2)-(4); the cost fix (`Lower.lean` 52,
`Inline.lean` 14) and the fixtures the trust mutants asked for came after. The follow row fields are cut to me-5d.

**Bytes:** 0 expected (plan ME-5); nothing is claimed before a pilot audit.

Shared files: `lean/ResponseShape/Schemas/Calc.lean`, `Encoders/Calc.lean` (me-2b's, merged), `tests/data/*`
(append-only), `tools/trust-classes.json`, `ve/assurance-manifest.json` (registries). No branch in flight edits the
Calc files: `lean-first/b14b-evidence` (Oct 12) and `foundation/me-1` (Oct 15) list them only against old bases.

## Next item

- **me-5d**: a follows row's `certificate` and `counterexample` (names bound to the request's free values) and
  `rests_on`'s premise and link lines, with the follows `line` from `renderFollows`, after me-2c's row fields.
- R-10a after ME-4; me-9's follow-ups (R-10c after ME-4); then ME-7.

## Sibling lessons (me-2b review)

- F1, a value recomputed on every read (time doubling per step): the class here is the lowering of a derivation. One
  inlining table per derivation, normalised sums, the node bound; the 12/13-step doubling chains and the one-coefficient
  guard pin it, and the slowest whole case found (54 s, under the deadline) is a FOLLOW-UPS row.
- F2, a check tested on its refusing side only: every limit and refusal has its accepted neighbour (512/513 premises,
  63/64 facts, chain 12/13 for the search and for the linearity check, `le` and `gt` conclusions beside `eq`, a
  `within` premise beside `rounds`).

## Self-review against BUILDER-CHECKLIST

1. PASS: genuine R-3 and R-4 answers are in the calc corpus that `tests/test_route_row_schemas.py` and
   `tests/test_shape_binding_mutants.py` mutate field by field, and in the relay mutation gate; the decoder refuses
   every malformed value of each new field (RunExamples malformed guard).
2. PASS: the table above, each row with its check; me-5d named for the cut row fields, R-10a for ME-4; no Python copy of
   a Lean decision, no report test, no in-flight overlap.
3. PASS: `mutants.json` 38 of 38 killed; `trust-mutants.json` exit 0 with the allow file.
4. PASS: the base corpus answers unchanged (`test_route_cases_answer_their_rows`, R-1, R-2, I-1 pinned); key order and
   words do not change a derivation's identity (identity families); no Python or Rust implementation exists.
5. PASS: `kind` bound (`test_a_rows_kind_is_its_requests`, me-2b's `kind retyped` mutant); undeclared premise ids,
   link names and premise names refused (`test_refusals`; RunExamples `unknown-premise`, `unknown-link-*`,
   `premise-name`).
6. PASS: base from `git merge-base`; commits from `main..HEAD --no-merges`; the full gate is the chain's.
7. PASS: DELTA rows cite R2, R1, R16 and row 1 the DRI decision file (first lines above); `trust_map.py --check` PASS;
   FOLLOW-UPS "## me-5c".
8. PASS: DELTA lists the accepted fields, rows, refusals, fault order, rewording and CPU; no base answer changed.
9. PASS: the selection ran 379 units with `test_calc_derive.py` and `lake build`; the shape seeded bug fails a selected
   test.
10. PASS: statements equal the spec (script above); the clause mutants break `Check.run_sound`; `Run.row_sound` is
    about `runCaseReported`'s own rows.
11. PASS: every limit is UNKNOWN, never a verdict (`chain-13`, `facts-64`, the budget row); no budget field before ME-4.
12. PASS: the one-coefficient guard and the doubling-chain fixtures (no timing in the suite); 114 s to 0.08 s measured.
13. PASS: no test removed; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
