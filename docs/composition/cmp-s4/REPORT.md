# cmp-s4: documents and cases, the composed admission, the identity cases (discourse 14.4 to 14.6)

- **Status:** done as cut below; no DRI signature needed (DELTA has no row: reviews/dri-decisions-20261102-cmp-s4.md item 1).
- **What changed:** `lean/VE/Discourse/Compose.lean` (new) holds 14.4, 14.5 and 14.6's identity theorems, all proved
  (no `sorry`, no new axiom). `lean/VE/Discourse/Run.lean` gains `encodeComposed`, `ComposedAdmissionAnswer` and the
  restated `discourse_wire_acceptance`; `fuelBudget` moved unchanged to `Admission.lean` as `VE.Discourse.fuelBudget`.
  `lean/VE/Discourse/ComposeExamples.lean` (new) holds the 14.8 fixtures this item can run, as `#guard`s.
- **Cut to cmp-s4c (FOLLOW-UP):** the route entry (`runCase` on the composed path, the three `NotImplemented: <kind> on
  the chain` kinds), its relay, schema and fuzz tests, the route cases, the chain decoders that let the soft, rights
  and norm-defaults lists through step 1, and the fixtures that need them (S4-1 on the constitution part, S4-16 and
  S4-17 through the route, S4-18, S4-27, S4-28's route test, the saved byte-identity comparison). Reason: size (below).
- **Depends on cmp-s4ab (not merged):** 14.3 steps 1 and 3 to 7 and the fence slots. Until it merges, the composed path
  refuses a fenced unit and a prose unit with a recorded formula-producing mention by name (below). S4-4, S4-5, S4-22
  with its fence, S4-24 as a route case wait for it.
- **Trust:** S +125, V +19, K +0 (trusted +143 of R16's 150). SIGNED by standing ruling R16.
- **DELTA:** no row (docs/composition/cmp-s4/DELTA.md). No route, wire, Python or English answer changes.

## Deliverables (task cmp-s4)

| Task row | Delivered | Evidence |
|---|---|---|
| (1) 14.4 `resolveDocument`, `caseManifest`, `resolveCase`, `contentFree`, `caseShape`; `resolveDocument_keeps`, `resolveCase_keeps`, `resolveCase_off` | yes, statements verbatim | `Compose.lean:84-190`; statement check below |
| (1) 14.5 `dispatchAdmission`, `chainDocument`, `ChainAdmitted`, `Composed`, `admitComposed`, `conditionalOnOf`, `composedJson`; `composed_admission`, `composed_path`, `conditions_retained` | yes, statements verbatim | `Compose.lean:195-386` |
| (2) 14.6 `composed_unchanged`, `composed_base_unchanged`, `composed_unchanged_error` (DRI condition: the `"ve.discourse@1" ∉ profiles ∨` disjunct) | yes, verbatim, in `lean/statements.txt` | `Compose.lean:389-411` |
| (2) `encodeComposed`, `ComposedAdmissionAnswer`, restated `discourse_wire_acceptance` (namespace `VE.Discourse.Run`) | yes, verbatim | `Run.lean:177-202`; `runCase` unchanged, so the proof takes the left disjunct |
| (2) `fuelBudget` moved to `Admission.lean` | yes | `Admission.lean:715` |
| (3) route entry and relay | **cut to cmp-s4c** | widening row pre-signed there (DRI decision item 2) |
| (4) fixtures as `#guard`s | S4-2 (α), S4-3, S4-20, S4-21, S4-22 and S4-23 (without a fence), S4-25, S4-28, S4-16 and S4-17 at `dispatchAdmission`; a synthetic S4-1 on the norms route | `ComposeExamples.lean` |
| (4) S4-1 on the constitution part, S4-14, S4-18, S4-27, route cases, saved byte-identity comparison | **cut to cmp-s4c** (S4-14 keeps today's answer: no code path changed) | |
| (5) seeded bugs: the four the task names, plus one per new trusted definition | yes, 29 of 29 killed | `mutants.json`, table below |
| evaluate once, charge against a stated limit, a large fixture | yes | "Evaluation cost" |
| `lean/statements.txt`, generated tables | regenerated | `tools/regen_generated.py --write` |

Plan rows (composition-PLAN.md S4 at `docs/spec/composition-PLAN.md:824`): "the discourse loader's three abstentions
become implementations" is cmp-s4c's (route) after cmp-s4ab (fences); "`ve/profiles.py` and the Lean gate admit
`ve.discourse@1` beside the chain" is cmp-s4c's (three-way agreement, 14.6); question 7 stays OPEN 1 (DRI 2026-10-31
item 2).

## The composed path in this item (14.5 steps 1 to 7)

`admitComposed` takes the composed path iff `"norms@0" ∈ profiles ∧ "ve.discourse@1" ∈ profiles ∧ chainConstructs
environment j = true`; otherwise it is `.today` of `admitDiscourse … (baseVocabulary environment) … fuelBudget`, or
`baseVocabulary`'s error. On the path, `admitChain` runs, in the spec's order:

1. `wrapperOk` (today's texts and today's frozen FOL-family gate on `baseEnvironment`), then `chainAbstentions`:
   non-empty `groups`, `constraints`, `validity` or `reading_sets` are `NotImplemented: <groups | constraints | validity
   claims | reading sets> on the chain`;
2. `integrityOk` (document table and integrity, as today);
3. `chainBase`: the norms decoder's environment of the base pair, the chain route's environment id
   (`environmentId` of `Norms.Wire.canonicalEnvironmentJson`, the id the norms route's certificates bind) and the
   manifest; `definitions_version` must equal that id (`StaleTarget: definitions@<v>`);
4. and 5. `resolveWith` (= `resolveDocument`): 14.3 step 6 (`MentionNotSlot: <m>` for a recorded formula-producing
   mention on a JSON content) and two named abstentions while cmp-s4ab is out: `NotImplemented: fenced content on the
   chain`, `NotImplemented: a bound prose unit on the chain`. Every other content's `resolveContent` answer is the
   content as written (`resolve_identity`: no slot), so the answer is the payload itself;
6. `dispatch (baseProfiles profiles)`, `chainDocument` (units and `MIXED` parts with id, span, kind and content in the
   chain route's wire form: an `ast` content its formula, any other content as written, the form `Norms.Admission`
   `splitUnit` reads; graph, lemmas, open term names; no graph is today's `NotImplemented: a document without a claim
   graph`), the byte charge, `dispatchAdmission`;
7. `Loader.documentId`, the reference lines (7.1, `referencesJson`; refused if one carries a `conditional_on` list),
   `wrapperReportId` over `inner`'s `report_id`.

Readings (each a point the spec leaves to the implementation):
- **The FOL-family check of step 1** is today's gate (`Gate.decodeEnvelope` on `baseEnvironment`), which knows only
  the frozen profiles: `soft-norms@0`, `rights@0`, `norm-defaults@0`, `readings@1` and `speech-acts@0` lists stop
  there with today's text, the same answer as off the path (`#guard`s at `ComposeExamples.lean:101-108`). So only the
  norms route is reached in this item; the chain decoders are cmp-s4c's. `dispatchAdmission`'s own refusals are
  pinned directly (`ComposeExamples.lean:109-113`).
- **`composedJson`** has the keys `document_id`, `inner`, `inner_report_id`, `references`, `report_id`;
  `encodeComposed` adds `id` and `status: ok`, as `Route.Wire.ok` does for today's answer.
- **`caseShape`** is `{"id": <id>, "document": [<source>, <the front matter's shape as canonical text>]}`; `resolveCase`
  checks its own result against it (regenerated, never trusted) and `resolveCase_keeps` follows from that check.
  Lean's `Json` has no decidable equality, so the check compares strings (as `VE.Ask.Same` does).
- **Layer:** `Compose` and its fixtures are layer 4 in `tools/layer_policy.py` (it states theorems on
  `Service.Document.profilesOf` and runs the chain routes), as `VE.Compose.Contract` is.
- **cmp-s4a review F1** (a definite's sort by `restrictionSort`) concerns resolution of slots, which no input reaches
  before cmp-s4ab; it stays with cmp-s4ab's route wiring.

Statement check: every declaration and docstring of 14.4 to 14.6's Lean blocks (`docs/spec/discourse.md:2313-2513`)
compared with `Compose.lean`, `Run.lean` and `Admission.lean`, whitespace-normalised (a one-off script, not
committed): "42 spec declarations and docstrings (discourse.md lines 2313-2513); 0 not verbatim".

## Size

`git diff --numstat $(git merge-base HEAD main)`, hand-written: `Compose.lean` 412, `ComposeExamples.lean` 233,
`Run.lean` +14/-7, `Admission.lean` 3, `lean/VE.lean` 2, `tools/layer_policy.py` 3, `tools/trust-classes.json`
+101/-3, this report and DELTA.md. About 780 lines before the report, above the ~600 guide. The spec-verbatim
declarations with their docstrings and the proofs of the nine theorems take about 230 of `Compose.lean`'s lines and
cannot leave without leaving the statement gate's theorems unproved; I cut at the route entry (task row (3)), the
fallback the task names.

## Seeded bugs (Lean only; no Python or Rust product code changed)

Each was planted alone, built with `lake build VE.Discourse.ComposeExamples`, and restored. All 29 are in
`docs/composition/cmp-s4/mutants.json` with the first failing check.

| Behaviour | Mutant | Fails |
|---|---|---|
| the composed path needs `ve.discourse@1` (S4-28) | `admitComposed`: `"ve.discourse@1" ∈ profiles ∧` dropped | `composed_path` (`Compose.lean:311`, via `admitChain_of`) |
| `readings@1` beside `norms@0` is refused (S4-16) | `dispatchAdmission`: `.readings` runs the norms route | `ComposeExamples.lean:110` |
| no coherence premise dropped from `conditional_on` (S4-18) | `composedJson`: `inner` with its `conditional_on` emptied | `conditions_retained` (`Compose.lean:370`) |
| `resolveCase` removes the `discourse` key (S4-22) | `writtenText`: `discourse` kept | `ComposeExamples.lean:204` |
| `definitions_version` is checked (step 3) | `admitChain`: `req (true || …)` | `ComposeExamples.lean:136` |
| the payload is kept (`resolveDocument_keeps`) | `resolveWith`: the source rewritten | `resolveDocument_keeps` (`Compose.lean:169`) |
| a case without `ve.discourse@1` is unchanged | `resolveCase`: always `resolveOn` | `resolveCase_keeps` (`Compose.lean:173`) |

The other 22 (one per remaining new definition: `chainKeys`, `contentKey`, `unitsAndParts`, `chainConstructs`,
`contentOk`, `chainAbstentions`, `editObj`, `editArr`, `unitFree`, `frontShape`, `textShape`, `caseParts`,
`contentFree`, `caseShape`, `chainUnit`, `conditionalOnOf`, `conditionalOnTree`, `conditionalOnList`, `chainBase`,
`caseManifest`, `chainDocument`, `encodeComposed`) each fail a named `#guard` (`mutants.json`).

## Trust (R16)

`uv run python tools/trust_map.py --check`: "PASS: K, S and untied [V] within 3b4e471f8c29 and the allowances
introduced since"; against the merge base: K +0, S +125 (`Compose.lean`), V +19 (`Compose.lean` +18: `chainBase`,
`caseManifest`; `Run.lean` +1: `encodeComposed`). Recorded with `--signed "SIGNED by standing ruling R16
(DRI-RULINGS.md), cmp-s4, 2026-10-18"` (`docs/trust-baseline.json`). No line replaces a deleted Python path (no R6).

Classes (`tools/trust-classes.json`): S for the meaning the theorems are stated over or that decides acceptance
(`chainConstructs` and its helpers, `contentOk`, `chainAbstentions`, `contentFree`, `caseShape` and their helpers,
`chainUnit`, `conditionalOnOf`/`Tree`/`List`, `ChainAdmitted`, `Composed`), as cmp-s4a's review F2 asks; C for the
checked executables (`resolveWith`, `resolveDocument`, `resolveOn`, `resolveCase`, `writtenText`, `admitChain`,
`admitComposed`); tied: `composedJson` (`conditions_retained`), `chainDocument` and `dispatchAdmission`
(`composed_admission`), `fuelBudget` (`composed_unchanged`), `ComposedAdmissionAnswer` (`discourse_wire_acceptance`);
`chainReferences` G[R]; fixtures T.

R16's conditions: 143 ≤ 150, K +0; every new trusted definition has a check that can fail (the 29 hand mutants;
trust mutants below); the FOLLOW-UPS row is under "## cmp-s4" in `manage-agents/FOLLOW-UPS.md` (ties pass).

TRUST-MUTANTS-RESULT

## Evaluation cost (feature feed, evaluators and runners)

`admitComposed` evaluates each value it reads once: `chainConstructs` once (the path test); on the path the payload's
manifest and environment once (`chainBase`, shared by steps 3 to 5: `resolveDocument` is `resolveWith` of the same
manifest), `resolveWith` once, `chainDocument` once, the chain route once, the reference lines once. The chain
document is charged against `Loader.maxDocumentBytes` (4,000,000 bytes, the loader's limit on a document text) before
the chain route reads it: `ResourceLimit: chain document bytes`. No slot is resolved in this item, so nothing fans out;
the norms route keeps its own limit of 256 rules. Fixture: a 200-norm-unit document ends within both
(`ComposeExamples.lean:90-96`, `large`).

## Tests

- `lake build VE.Discourse.ComposeExamples`: every `#guard` passes. `cd lean && lake build`: "Build completed
  successfully (1234 jobs)". `python3 lean/audit.py`: "PASS: 725 source files; 8029 named theorem declarations
  audited … only the declared standard axiom allowlist".
- `uv run python tools/regen_generated.py --check --skip route-cases`: "checked 34 entries" (route-cases needs the Rust
  release binary; its inputs did not change: `runCase` is as on main).
- SELECTED-RESULT
- No test in `main-known-red.txt` was hit. Not run: the full gate (the chain runs it on the final HEAD).

## Pilot bytes

0 (*estimate*): no route reaches the composed path before cmp-s4c.

## Commits (`git log --oneline --no-merges main..HEAD`, saved)

COMMITS

## Next items

- FOLLOW-UP: cmp-s4c, the discourse route entry on the composed path, its relay, schema, fuzz tests and route cases,
  the chain decoders in step 1, and S4-1, S4-14, S4-16, S4-17, S4-18, S4-27, S4-28 as route fixtures with the saved
  byte-identity comparison (DRI decision 2026-11-02 item 2 signs its widening row and lists its conditions).
- cmp-s4ab (14.3 steps 1, 3 to 7; fences), cmp-s4b (OPEN 4), pc-s4-positions, then pc-7b.

## Self-review against BUILDER-CHECKLIST

SELF-REVIEW
