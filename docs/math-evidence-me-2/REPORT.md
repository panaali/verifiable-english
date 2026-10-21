# me-2 report: the `ve-calc@0` wire and the `calc` runner (math-evidence ME-2, first part)

No DRI signature is reserved: the one DELTA row cites R16. The item is cut as the task suggested: the wire and the
runner with the route cases; the service mode, its shape and encoder, and the row fields beyond the outcome are the
next item **me-2b**. Size is over the ~600-line guide (below, "Size").

## Statement gate

ME-S passed its bounded re-checks (manage-agents `math-evidence-p3ver1.final.md`, then `math-evidence-p3ver2.final.md`:
PASS). Plan and spec are main's (`docs/spec/math-evidence-PLAN.md` and `docs/spec/math-evidence.md`, identical to
c5197da78). Spec 3.4 gives the elaborated forms of 3.2's statements (the plan says so under 3.2), so they are the
ones built. Each statement proved here equals the reviewed text after whitespace normalisation (checked by a script
over the spec section and the Lean files): `Wire.decodeCase_wellFormed`, `Check.run_claim`, `Check.run_sound`,
`Run.rows_outcome`, `Run.outcome_sound`, `Run.row_sound`, `Run.verdict_sound`, `Run.unknown_named`. `Check`,
`Check.UnknownCause` and `Check.OutcomeMeans` are the reviewed text with the `claim` constructor and its clauses only,
as spec 3.4 says ("each batch adds its constructor, its clauses and its case of `Check.run_sound`"); `Case`, `Row`,
`Run.row` and `Run.rows` are as written. `runMode_calc` and `runCaseReported_fits` are me-2b's (the mode). No
statement changed.

## Plan rows (ME-2 at main; plan 3.2, spec 2.1 and 3.1-3.4, J1)

| Row | Delivered | Where, checked by (`lean/VE/Calc/RunExamples.lean` guard line) |
|---|---|---|
| `lean/VE/Calc/Wire.lean`: `Case`, `Wire.decodeCase` | yes: format, values (stated or defined), claims (`eq`, `lt`, `le`, `gt`, `ge`, `within`, `rounds` with an optional rule, `rounds-down`, `rounds-up`), `rounding`, `software`, `support`, `span` | 91, 153, 188, 242, 268 |
| Limits of 3.2 in order: 10,000 JSON values, depth 64, 512 values, 512 claims, exponents 64, literals 40 digits (W6's `parseDecimal`), names and claim ids 64 bytes; checked before anything else | yes, each on both sides, and their order (exponent before digits before names; a limit before a field error) | 153 |
| Decoder refusals of 13.1 owned by ME-2: `InvalidInput` (with the JSON path), `ResourceLimit`, `UnknownName`, `DuplicateName`, `DuplicateClaimId`, `NoClaims` | yes | 188, 242, 268 |
| `VerbalisationCollision`, `ValueWordsForm`, `ReservedWord` | **me-2b**, with the `line` field they serve; until then `words` is any string | 268 states it |
| Identity 3.3 with J1: `meaning_id` through `VE.Route.Wire.meaningId ["calc@0"]`, the frozen encoder unchanged; `words` removed; values in shortest plain decimal (no `sci` left); printed numbers as `[digits, places]` canonical decimal strings; each `rounds` claim with its rule; claim ids by `ve-calc-claim-v0.2:calc@0` | yes; I-1 pinned (`b3798e85…`, and `c7cd36a4…` for the `"20000000"` spelling), R-1 and R-2 claim ids pinned | 54-55, 132-145 |
| `Wire.decodeCase_wellFormed` | yes | proof; `lean/VE/Audit.lean` |
| Spec 3.4: `Check` (claim), `Check.UnknownCause`, `Check.OutcomeMeans`, `Check.run`, `Check.run_sound`, `Row`, `Run.row`, `Run.rows`, `Run.rows_outcome`, `Run.runCaseReported`, `Run.outcomeAt`, `Run.outcome_sound`, `Run.row_sound`, `Run.verdict_sound`, `Run.unknown_named` | yes, all proved; the decided-row meaning is also decidable for route cases | 54-60, 123 |
| Route cases V-1, V-2, V-5 (20 claims in one case), V-11, V-9, I-1, R-1, R-2 | yes, as `#guard`s with every expected result of spec 13.3 and 13.6 (R-1 and R-2 pinned whole, every field) | 54-55, 91 |
| Hostile set: unknown name, a name defined after its use, `pow` above the limit, a literal of 41 digits, a printed spelling with a sign error, a forged `meaning_id` | yes (a forged `meaning_id` in the request is an unknown field: the identity is Lean's) | 153, 188 |
| Plan's seeded bug: claim i + 1's verdict reported for claim i | yes: `mutants.json` `plan-seeded-bug` fails the R-1 and R-2 guards (54, 55) | `mutants.json` |
| `calc` constructor, name, list entry, dispatch, `runMode_calc`; `MODES` (generated from the handshake) | **me-2b**: registering the mode needs `ResponseShape.Encoders.runMode_fits`' case, so the shape and encoder come with it | |
| `lean/ResponseShape/{Schemas,Encoders}/Calc.lean`, `calc.json`, `DEADLINES` | **me-2b** | |
| `calc@0` row of AR-10's profile table | **not built; to ME-10**: no case of the `calc` mode lists profiles (spec 3.1), and admitting `calc@0` in a document environment before any route checks calculation content would widen what is accepted, which no standing ruling covers. ME-10 (calculation content in documents) adds the row with its composition proof | FOLLOW-UPS "## me-2" |
| `ve/assurance-manifest.json` decoder pins | yes: `Wire.lean` and `Run.lean` pinned whole, `Units.lean` re-pinned, `RunExamples.lean` under `other_json` | `tests/test_assurance_manifest.py` |
| `ROADMAP.md` trust-cost line | yes | |
| Generated files via regen | `regen_generated.py --write` (inventories, `docs/spec/assurance-manifest.md`); `calc.json`, `ResponseShape.lean` and `route-cases.json` are unchanged until me-2b | `regen_generated.py --check` |

One owner: `VE.Calc.Units` now takes `checkFields` and `invalid` from `VE.Calc.Wire` (moved, with an optional-field
list) and spells a factor with `Wire.plain` (the shortest plain decimal), so `ve-units@2`'s factors and `ve-calc@0`'s
values share one canonical spelling. Every `UnitsExamples` guard is unchanged. me-6c (factors written
`["sci", d, e]`) can now read them with `Wire.literal`.

Fault order (no base exists, so none of it is a delta; recorded for me-2b's relay): the limits in 3.2's order;
then the case's fields (unknown before missing), the format, the rule, the software convention, the lists and
`NoClaims`; then each value record and each claim entry in order (fields, name, words, source, support, span); then
`DuplicateName`, `UnknownName` (definitions in order, then claims) and `DuplicateClaimId`.

## Trust (R16)

K +0, S +14, untied V +134, trusted +148 (`trust_map.py --check`: PASS; allowance recorded; FOLLOW-UPS "## me-2"
has the ties-pass row). Per declaration in DELTA row 1. The limits, refusals and name checks are D[R]; canonical forms
and digests D[I]; `decodeCase`, `Row`, `Run.row`, `Run.rows`, `Run.words`, `Run.outcomes`, `Run.outcomeAt` and
`Run.runCaseReported` are tied to the theorems that fix what they answer. To stay within 150 the first draft (+165)
was reshaped: reject-only and identity code split into their own declarations, `runCase` folded into the tied
`runCaseReported`, and `Run.row` tied by `Run.row_outcome`.

## Seeded bugs and mutants

- [`trust-mutants.json`](trust-mutants.json): `uv run python tools/trust_mutants.py --max-mutants 1000 --json
  docs/math-evidence-me-2/trust-mutants.json --allow docs/math-evidence-me-2/trust-mutants-allow.json` on the final
  Lean change: 125 KILLED, 0 SURVIVOR, 0 UNKNOWN, 10 INVALID, 21 ALLOWED, 0 NOT RUN; exit 0. The first runs (150
  killed, 45 survivors, 81 unknown; then 122/0/7) were answered with fixtures (every argument's path, asymmetric
  comparisons, claim ids, one-character values) and with code every mutant can reach (cons patterns, the parser's
  fuel from `VE.Limits.maxDepth`, no singleton list wrappers). The allowed: equivalent mutants (`eq` swapped; `take 1`
  of a list of at most one element), mutants that are no program (an Option or a lookup table emptied), and
  `Check.UnknownCause` with the unknown arm of `Check.OutcomeMeans`: a Prop over `Claim.Overflows` and
  `Claim.ReadsExhausted`, which quantify over the rationals, so no evaluated check can read it (FOLLOW-UPS: a
  decidable restatement through `Expr.eval_iff` would). `OutcomeMeans`' `=`→`≠` mutant is killed by the guard at
  123, run by hand with the proofs stubbed (the tool marks a check that decides through the instance as unknown).
- [`mutants.json`](mutants.json): 23 hand mutants, each alone, with every theorem of `Wire.lean` and `Run.lean`
  stubbed so only `#guard`s can catch it (the control build passes); all killed. Lean, one per claimed behaviour and
  per trusted definition: `plan-seeded-bug` (`Run.runCaseReported`, guards 54-55), `literal-sci-sign`,
  `operations-sub`, `comparisons-gt`, `rules-half-even`, `expr-pow`, `claim-within`, `claim-rule`, `value-stated`,
  `entry-id`, `decl-defined`, `decode-software`, `decode-rounding`, `outcome-means` (123), `rowjson-reason`,
  `rowjson-reproduction`, `words-undefined`, `limit-nodes` and `limit-order` (153), `admit-unknown` (188),
  `identify-domain`, and `units-factor-spelling` (`lean/VE/Calc/Units.lean`, `UnitsExamples.lean` 107 and 229).
  Python (`tools/layer_policy.py`, a tool): the route cases taken out of the runner layer fails
  `tools/check_lean_imports.py` ("new outward Lean import: VE.Calc.RunExamples -> VE.Calc.Run"). No Rust changed.

## Tests and checks run

- `lake build` (whole library), `python3 lean/audit.py` (PASS, 604 files), `regen_generated.py --write` then
  `--check`, `trust_map.py --check`, `repo_map.py --check`, `check_lean_imports.py`,
  `tests/test_assurance_manifest.py -k "pinned or classified or json_use"` (5 passed).
- Selected tests: "Final selected run" below. Synced with main 6454946a5 (et-3cb) before it, and again with
  768a935fc (df-1ac, only the shared registries overlap): `lake build`, `regen_generated.py --write`,
  `trust_map.py --check` (+148, PASS), `check_lean_imports.py`, and the two fixed test files (141 passed) after it.
- Not run: the full gate (the chain's). No test in `main-known-red.txt` is touched.

## Size

Hand-written lines over the merge base: Lean product 558 (`Wire.lean` 380, `Run.lean` 162, `Units.lean` 13,
`VE.lean` 3), route cases 286 (`RunExamples.lean`), side tables about 200 (`tools/trust-classes.json` 142, assurance
manifest 56), tool 5, evidence and docs about 190 (DELTA, REPORT, `mutants.json`, the allow file, ROADMAP);
`trust-mutants.json` and the inventories are generated. About 1,240 in all, twice the ~600 guide. The cut the task
named was taken (no mode, shape, encoder, words checks or row fields beyond the outcome); a further cut would split
the decoder (380 lines, of which the limit scan is 75 and the refusals and identity most of the rest) from the runner
whose route cases and seeded bug ME-2 asks for, and the decoder alone would still be about 800.

## Pilot bytes and next item

0 expected (plan: "Bytes: 0"); nothing claimed. Next: **me-2b** (the `calc` mode: `Mode.calc` in
`lean/VE/Service/Registry.lean`, the dispatch line and `runMode_calc` in `Protocol.lean`, `Schemas/Calc.lean`,
`Encoders/Calc.lean` with `runCaseReported_fits`, `calc.json`, `DEADLINES`, service-level route cases in
`tests/data/route-cases.jsonl`; the row fields `line`, `display`, `sides`, `tie`, `finding` and `rests_on` with the
words checks), then qt-a3 (protocol queue), me-4 and me-12.

## Final selected run

`mac-pytest.sh --select -- --base 6454946a5f54 --run` on 6035a2de (the synced HEAD): the Mac runner's setup failed
("lake build failed twice (runner problem)"), so it ran on the VM: 81 of 460 units, the lake build (every route case)
and every Lean and layer check passed; 4 tests in 2 files failed, both mine:
`tests/test_assurance_manifest.py::test_decoder_files_are_pinned_whole` and `::test_trusted_decoder_line_ranges_are_pinned`
(`Wire.lean` and `Run.lean` changed after their pins), and
`tests/test_lean_limits.py::test_no_non_frozen_lean_check_hard_codes_a_limit` and `::test_the_reviewers_probe` (the
node, depth and name limits written as numbers). Fixed in cfee74b09: the limits are `VE.Limits.maxNodes`, `maxDepth`
and `maxIdentifierBytes`, the files re-pinned. Then: both files rerun, 141 passed; `lake build VE.Calc.RunExamples
VE.Calc.UnitsExamples` (every guard); `regen_generated.py --check` (33 entries); `trust_map.py --check` PASS (+148);
`trust_mutants.py` again on cfee74b09, the same 125 killed, 21 allowed, exit 0; `gate_collection.py --check
--prebuilt`: 0 added, 0 refused, 0 stale, 0 malformed. The `limit-nodes` hand mutant was rerun on the new text:
killed (guard 153).

## Self-review against BUILDER-CHECKLIST

1. PASS (decoder side): every field of a case, a value record and a claim entry replaced by 7, true, null, [], {},
   1.5, "" and a nested list is refused and answers no row (guard 268); deep input is the depth limit (153). No Python
   reads a `calc` answer yet (me-2b/ME-3), so the relay half is N.A.
2. PASS: plan rows table above; me-2b and ME-10 named with reasons; no Python copy of a Lean decision, no permanent
   report test; overlap: no in-flight branch edits `Wire.lean`, `Run.lean`, `Units.lean` or `layer_policy.py`; the
   shared registries (`lean/VE.lean`, `tools/trust-classes.json`, `ve/assurance-manifest.json`) are append-only.
3. PASS: `mutants.json` 23 of 23 killed with proofs stubbed; `trust-mutants.json` exit 0.
4. PASS: reordered keys and renamed words keep the `meaning_id`, spellings "0.30"/"0.3" as values do and as printed
   numbers do not (132-145); `UnitsExamples` unchanged after the shared spelling. No Python or Rust implementation.
5. N.A.: no relayed field yet; inputs: undeclared names refused (`unknown-name`, `defined-after-use`,
   `unknown-claim-name`, 188).
6. PASS: synced with main 768a935fc; selected run on the earlier sync, fixes rerun after; the full gate is the chain's.
7. PASS: DELTA row 1 cites R16 with per-declaration lines; `trust_map.py --check` PASS; FOLLOW-UPS row.
8. PASS: no public output (no mode or route); DELTA says so.
9. PASS: `select_tests.py` selects 81 of 460 units, `lake build` among them, which evaluates every route case; it
   also selected and caught `tests/test_lean_limits.py` and the manifest pins (above).
10. PASS: the eight statements equal the reviewed text; mutants break the proofs before they are stubbed (for
    example `outcome-means` breaks `Check.run_sound` and `Run.verdict_sound`). No `check_*_statements.py` covers
    math-evidence.
11. PASS: each limit tested at and past its value (153); a digit-limit hit is UNKNOWN for the claim (R-2's v1), never
    a verdict. No budget field until ME-4 (refused as unknown).
12. N.A.: no runtime path changes; the route cases evaluate in about a second of the Lean build.
13. PASS: no test removed; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
