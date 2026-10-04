# Wire contract stage S7: `alternatives@0` and `risk@0` (PLAN)

**Status:** plan only, draft 2, 2026-10-04, branch `design/wire-s7` from `main` at `bb05a08d`. No code or proofs
change with this document. Draft 1 (`f72d830c`) was a pointer of one paragraph: item 1 of this plan is stage S7
of [wire-contract-PLAN.md](wire-contract-PLAN.md) (the **base plan**), "`alternatives@0` and `risk@0`. S0-S4
are merged on main; S5 (`norms@0`, `norm-defaults@0`, including the S5.0 generalisation of the generator) is
merging in parallel and is a PREREQUISITE: write the spec against S5's generalised generator as specified in the
S5 plan/spec on branch `design/wire-s5`. Apply the base plan's S7 section exactly: only diagnostics may become
uniform (listed per profile); accept/reject and identities unchanged; corpus completeness test kept; the
difffuzz baseline (`infra/difffuzz`, if merged) must not grow. Honest open questions." Draft 2 applies the
converged position of `manage-agents/debates/design-wire-s7/{fable,astra}.md` and writes the plan out. The
item-1 statement spec is [wire-contract-s7.md](wire-contract-s7.md) (the **statement spec**); its statement
review comes before any build step. [wire-contract.md](wire-contract.md), the statement spec of S0 to S3 with
its build responses, is the **base spec**; [wire-contract-s4.md](wire-contract-s4.md) and
[wire-contract-S4-PLAN.md](wire-contract-S4-PLAN.md) are the **S4 spec** and the **S4 plan**;
[wire-contract-S5-PLAN.md](wire-contract-S5-PLAN.md) and [wire-contract-s5.md](wire-contract-s5.md) on branch
`design/wire-s5` (plan draft 3, spec draft 2, statement review passed; the build is in progress) are the **S5
plan** and the **S5 spec**, whose shape this plan follows and whose S5.0 generalisation it requires.

**What the debate files are.** As for S4 and S5, `debates/design-wire-s7/` holds the three files of
`debates/design-wire/`, word for word: the debate on the base plan (CONVERGED after round 3; Sol at xhigh stood
in for Astra, as `astra.md` records), and `TOPIC.md` still asks about the base plan. No reviewer has read this
plan. The converged edits a to h are already in the base plan (its section 11) and were restated for S4 (S4
plan, section 3) and S5 (S5 plan, section 3). "Applying them exactly" therefore means here: each edit is
restated as it binds stage S7 (section 3), and no design choice of the debate is reopened or added to.
Everything in this plan that the debate did not decide is marked as a choice of this draft and listed in
section 8 for the statement review.

The plan was written from reading the sources at `bb05a08d`; nothing was built or run, and every `file:line`
reference must be re-read at each step. The Lean statements of the statement spec were written as a stub file
but could not be compiled in the session that wrote them (statement spec, status paragraph); compiling the
stub is the first task of the build.

## 0. Decision in brief

1. **Stage S7 is two items.** Item 1 is the base plan's row 9 of 5.3: the contract `alternatives@0` (the
   alternatives source: environment with its block, norm units, base assertion units), then the contract
   `risk@0` (the risk source, and the decision record of a `risk-decision` case), each taken through every step
   of base plan 5.1: author, hooks, generate, shadow, delta report, DRI review, switch. Neither contract exists
   today. Item 2 is the one Rust change the row names: `UnitPrecision` gets one encoding (section 2, item 2).
2. **The order of each table is Lean's**, the authority of both routes (`lean/VE/Alternatives/Wire.lean`,
   `lean/VE/Risk/Wire.lean`, `Record.lean` and `Run.lean` are pinned decoders in `ve/assurance-manifest.json`;
   base plan 5.1 step 1 and row 9: `checkAlt`, `checkRisk`, `checkView`). Python has no validator of either
   unit: `ve/alternatives.py` and `ve/risk.py` transport a case to the Lean route and return its row. So, under
   edit d, Python does not support either unit; its engine runs the table up to the first instance that needs
   Lean and then defers, and the record is Lean's, obtained from `ve_diagnose` through the manifest operation
   `wire.diagnose`. This is the first production use of the Lean consultation that base plan 2.5 designed; S4
   and S5 did not need it because their Python registries were complete.
3. **Each switch changes one thing in public.** `ve.alternatives.run_case` and `ve.risk.run_case` return the
   route's row; after the switch, an error row of a case in the unit's domain carries the contract's record in
   a member `diagnostic`, and its `error` text is the record's text when a check of the table fails, otherwise
   the route's text. No verdict, no identity, no `status`, no Lean row changes. The complete list of changed
   texts is measured on each unit's corpus and signed by the DRI before its switch commit.
4. **The contract still decides no verdict.** The engine runs only on a row the Lean route has already rejected,
   inside the function that returns that row, and hands back the same row object (edit f, section 3).
5. **The decision record is part of `risk@0`**, as phases that run only when the root has a `decision` member:
   base plan row 9 names `checkView` (V1 to V11) as an order source, and `UnitPrecision` (item 2) arises there.
   Admission (A1 to A3) and validation (V1 to V11) are two classifier sets with the route's texts; the order
   inside each set is the validator's and test-enforced (base plan 2.3, T3).
6. **Inherited checks stay inherited and Lean-only.** W1's environment decoder, W1's unit decoder, W6's unit
   checks and the typing of guards are inherited hooks whose text is the decoder's own. Python registers them
   as deferred, so that the public text of an inherited check is always the Lean engine's, which is the route's
   text today. Base plan rows 2 to 6 (S4 items 3 to 6, S5) are not merged or not built, so no include is used:
   the texts of W1's unit checks on these routes are the Lean route's, not `norms@0`'s (section 8, question 7).
7. **Rust has no column for the units.** Rust decodes neither source and no record. Item 2 changes one error
   encoding in `rust/ve-core/src/risk.rs`, the risk evaluator that the differential harness runs, and nothing
   else in Rust.
8. **The difffuzz baseline does not exist on `main`.** The branch `infra/difffuzz` is at `bb05a08d` with no
   commit of its own, and `main` has no difffuzz file. The pointer's condition is recorded and is vacuous until
   that work merges; if it merges before an S7 commit, the commit's gate adds the baseline comparison.

## 1. Where the work stands (read at `bb05a08d`, not run)

| Fact | Source |
|---|---|
| One contract exists, `soft-norms@0`, public at revision 4. S4 item 1 is merged; S4 items 2 to 6 are not started. S5 (plan draft 3, spec draft 2, statement review passed) is being built on `ve-wire-s5-int`; its S5.0 makes the tooling take a unit | `ve/wire_contract/`; `conformance/wire-contract/s4-integration.md`; S5 plan section 6; S5 spec 7.1 |
| The alternatives route in Python: `run_case` refuses a case that is not an object of a known kind, decodes the environment with Python's `Environment` (which checks the block with Python's own order and texts, and raises `UnsupportedProfile` without `alternatives@0`), then sends the raw case to `ve_alternatives_route` and returns its row. Admission goes through the same function with kind `admission` and raises `AdmissionError` with the row's text | `ve/alternatives.py:19–32`; `ve/environment.py:164–272, 550–555`; `ve/backends/lean.py:172–191`; `ve/admission.py:508–514` |
| The risk route in Python: `run_case` sends the raw case unchanged; Python decodes nothing first. Python's `Environment` mirrors the Lean block decoder and check for the English surface and for admission, in Lean's order and texts | `ve/risk.py:226–241, 70–215`; `ve/environment.py:510–517, 556–562` |
| The Lean alternatives source decoder: the profile gate, the block present, W1's environment decoder on the view without the block, no definitions and no data flags, the strict block decoder, the norm units (`decodeNorm`, at most 256), the base units, then `checkBlock`, the verbalisations, `avoids`, the base units typed, then `validateAlt`: `checkAlt` (the block again, the rules typed over the profile words and the inlining limit, W1's `validate` on the inlined tree, the fulfilments, `Γ`) and a Boolean fallback | `lean/VE/Alternatives/Wire.lean:25–36, 78–128, 132–159, 169–178, 193–223`; `lean/VE/Alternatives/Decl.lean:198–263`; `lean/VE/Norms/Tree.lean:302–368` |
| The Lean risk source decoder: the W6 pair, the profile gate, both blocks present, the envelope of the view and the FOL family, the W6 profile tuple, the unit records, the vocabulary annotations, W1's environment decoder on the view, the extension's rules, no definitions, flags or `$string` literals, the alternatives block with `excludes` expanded, the risk block, the norm units, the identity, `checkBlock`, the verbalisations, `avoids` and `excludes`, the base units typed, then `validateRisk`: `checkRiskBlock`, `checkRiskTyping`, `validateAlt (toAlt R)` and a Boolean fallback | `lean/VE/Risk/Wire.lean:24–31, 49–66, 86–149, 189–258, 268–277, 290–344`; `lean/VE/Risk/Decl.lean:210–280` |
| The Lean decision record: the decision entry and the supplied entries decode, admission (A1 to A3), validation (V1 to V11, with problems found while decoding cited contents reported at their step), the margin-candidate limit; `SufficientOutsideNecessary` and `RiskInconsistent` carry the witness case in the route's text | `lean/VE/Risk/Wire.lean:360–397`; `lean/VE/Risk/Record.lean:243–274, 384–462, 467–505, 817–990`; `lean/VE/Risk/Report.lean:122–124`; `lean/VE/Risk/Run.lean:281–288, 362–371` |
| Every route row with `status` `error` carries a bare `error` string; Python classifies its leading word (`UnknownSymbol`, `DuplicateDeclaration`, `ResourceLimit`, `UnsupportedProfile`, `InvalidModel(...)`) and reads every other text as `InvalidInput` | `ve/backends/diagnostics.py:15–52` |
| `UnitPrecision` has three encodings: Lean and Python print the message `UnitPrecision(<tag>, scale=<n>)` under the class `InvalidInput`, and so does Rust's unit decoder; Rust's risk evaluator prints the code `UnitPrecision` with the message `<tag>, scale`. The differential test compares `code: message` and never generates an off-grid literal, so the difference is untested | `lean/VE/Risk/Record.lean:282–283`; `lean/VE/Time/Wire.lean:362`; `ve/units.py:270`; `rust/ve-core/src/units.rs:154–158`; `rust/ve-core/src/risk.rs:110–112`; `tests/test_risk_differential.py:192–196` |
| The GENERIC cases of row 9: four faults of the vocabulary decoders that W1 and alt share, which both implementations reject, "each with its generic text"; the test asserts rejection only | `tests/test_risk_w6_extension.py:205–211, 255–258` |
| Diagnostics are tested text for text: every routable row of risk.md 6 on a hand-written input (84 cases); Python's environment check against Lean on 57 single faults and 309 pairs; the W6 extension (65 faults) | `tests/test_risk_every_diagnostic.py`; `tests/test_risk_diagnostics.py`; `tests/test_risk_w6_extension.py` |
| `ve_diagnose` looks a unit up in a hard-coded list in a hand-written, hash-listed module. The manifest operation `wire.diagnose` has one binding (mode `soft-norms@0`) and no call site; a Lean call from inside `ve/` must come from a declared call site | `lean/VE/WireContract/Diagnose.lean:32–38`; `ve/assurance-manifest.json:972–993`; `ve/assurance.py:97–124` |
| The Python engine defers at a hook, classifier or view whose name the registry maps to no function; the overlay consults a Lean outcome only when one is passed; the pilot's and S5's call sites pass none | `ve/wire_contract/engine.py:419–423, 453–463, 501–513` |
| `tools/wire_contract.py` refuses a hook the Python registry lacks (`WC08`), which base spec 2.5 rule 6 allows; the Python registry's `register` stores whatever value it is given | `tools/wire_contract.py:583–599`; `ve/wire_contract/engine.py:40–54` |
| The branch `infra/difffuzz` is at `bb05a08d`; no file of `main` names a difffuzz baseline | `git log infra/difffuzz`; `git diff --stat main infra/difffuzz` (empty) |

## 2. The two items

The statement spec fixes every detail; this section is the plan-level summary.

**Item 1, `alternatives@0` then `risk@0`.**

- **S7.0, what the generalisation must add.** S5.0 (S5 spec 7.1) makes the tooling take a unit. S7 needs four
  more things, each a generalisation of the tooling and not a change of `ve/`: the unit's Lean route and case
  kind come from a function of the root, not a constant, because a `risk@0` root with a `decision` is
  validated by `risk-decision` and one without by `risk-elaborate`; the gate measures the public delta on a
  row, not on a `VEError`, and counts the Lean consultation's outcome; the Python registry may name a hook
  without implementing it (the value `None`), which the engine reads as deferred and the lint as registered;
  and the recorder wraps `ve.alternatives.run_case`, `ve.risk.run_case`, both `public_rejection` functions and
  the two route binaries.
- **Before each switch, S7-pre (blocks the switch).** The shadow gate of each unit lists every corpus case on
  which the route's verdict and the verdict of Python's standalone `Environment` on the same environment
  disagree (`legacy_verdict_differences`), because on the alternatives route Python's `Environment` runs
  before the Lean route and decides the verdict of the environment part. Known from reading: Python rejects a
  predicate whose verbalisation reads like a profile word (`AlternativesReserved: wording for <p>`) and the
  Lean route does not. A verdict difference is outside this plan's licence and is fixed separately, as S3-pre,
  S4-pre and S5-pre were, with its record `conformance/wire-contract/s7-pre.md`.
- **The measured delta, per unit.** The gate computes, for every corpus case that the Lean route rejects, the
  record the overlay would report, and lists every case whose public text or class would change, grouped by
  check. The public delta is the part on the cases that reach the switched statement: for `alternatives@0`
  the error rows of `alt-elaborate` cases that pass Python's `Environment`; for `risk@0` the error rows of
  `risk-elaborate` and `risk-decision` cases. The DRI signs the list check by check
  (`conformance/wire-contract/<unit>-switch.json`), with the release note. This is step 5 of base plan 5.1,
  done as S4 and S5 did it: the measurement is a commit of its own, before the switch and in shadow.
- **The switch commit, per unit** (step 6): the contract's `status` becomes `public` and its revision rises;
  one function, `public_rejection`, in the unit's contract module and one call site in the route's
  `run_case` are added; the `wire.diagnose` binding gains the unit's mode and the call site; generated files,
  the lock and the reports are regenerated. The Lean routes are not edited. At the call site the error row
  carries the contract's record. When a check of the table fails, the record names the first one that fails
  and the row's `error` is that check's text; otherwise the `error` is the route's.
- **What may change, for `alternatives@0`** (base plan 5.3, row 9): the row's `error` on the checks of the
  signed list. From reading, nothing on a single fault: revision 1 takes every text from the route, so on a
  one-fault source the record's text is the route's text. The texts differ on a multi-fault source only where
  the table's order differs from the route's, which it does not by construction of the table, except inside
  a classifier set (test-enforced). The expected list is empty, and the measurement decides (statement spec
  section 6).
- **What may change, for `risk@0`:** the same; and the row's `error` on a `risk-decision` rejection names the
  same text, with the witness case where the route appends one. Expected list empty; the measurement decides.
- **What row 9 asks to delete.** Row 9's tolerance column is "those `GENERIC` cases". They are faults of the
  vocabulary decoders that W1 and alt share, reported by W1's environment decoder, which on these routes is an
  inherited hook with each language's own text until S4 item 5 (`vocabulary@0.2`). The tolerance cannot be
  removed by S7 and is kept; the row's "generic texts" change is delivered by S4 item 5, not here (section 8,
  question 8). Neither alternatives.md nor risk.md has a known-limitation paragraph on diagnostics; both gain
  the paragraph of the statement spec's 3.5.

**Item 2, `UnitPrecision` gets one encoding.** `rust/ve-core/src/risk.rs:111` prints the code `UnitPrecision`
with the message `<tag>, scale`; every other site prints the class `InvalidInput` with the message
`UnitPrecision(<tag>, scale=<n>)`. Item 2 changes that one line to the second encoding, with `<n>` the tag's
scale as the unit decoder prints it, and adds to `tests/test_risk_differential.py` an off-grid literal case
whose Lean and Rust texts must be equal, read as the differential reads them (statement spec 2.14). It is a
diagnostic of the Rust evaluator, not of a wire unit: no contract names it, no verdict changes (the literal
stays rejected), and it is one commit with its own release note. It lands before the `risk@0` switch.

## 3. The converged edits, as they bind stage S7

Each row restates one edit of the joint position (Fable's round 3, which Astra's round 3 restates) for S7. The
base plan's text for each edit is unchanged.

| Edit | What it requires of S7 |
|---|---|
| a. "By construction" is limited to table expansion, and to position, code, path and text conditional on equal predicate results; T3 order is test-enforced; raw JSON scanner order is open | "Uniform" after a switch has this meaning only. For each unit: the row's public text is the contract's template text; that it equals the Lean engine's record is constructed only where every predicate reached returns the same result in both, which for these units means: the Python engine's T1 fault before the first deferred instance, and otherwise Lean's own record. The order inside the five classifier sets of `alternatives@0` and the nine of `risk@0` (statement spec 2.3, 2.4) is the validator's and test-enforced. The route's own first fault on a multi-fault input is the table's by construction outside those sets, because the table is authored from the route's code in its order; inside them it is the route's by definition. The scanner order belongs to S4 item 3 and stays open there |
| b. C1 covers identity serialisation; `VEError.to_dict()` may gain `diagnostic` | `VEError.to_dict()` is not touched; the public object of these units is the route's row, which gains the member `diagnostic` and whose `error` text may change; `status` and `id` are never written. `AdmissionError` is not touched: admission is outside the domain (section 4) |
| c. C4 allows additions, generated rehashes, and a reviewed append-only `VE/Audit.lean` diff with its rehash in S1b; the lemmas stay optional | `VE/Audit.lean` is not touched unless the two optional engine lemmas of the statement spec (5.3) are added, in which case the S1b exception is used again for their `#print axioms` lines and recorded. The inventory diff of a commit is additions (two hooks modules, two tables) and generated rehashes (`Limits.lean`, `Names.lean`, every earlier table whose header names their hashes), plus the append-only registry diff of `Diagnose.lean` that S5 records as a C4 exception (S5 spec 5.3); the same exception is used for the two entries of S7 |
| d. C2 and the tolerance removals apply where an implementation supports the unit and completes diagnosis; a deferred outcome carries the contract, revision, deferred check id and legacy text, has no `check`, `code` or `path`, and is never a residual | Python does not support either unit. Its engine is compared at zero tolerance only on the cases where it completes diagnosis (a fault in the gate phase, before the first deferred instance); every other Python outcome is deferred and counted. Lean supports both and completes diagnosis on every case; it is compared at zero tolerance with the route (fault exactly when the route rejects). At the call site a deferred Python outcome is resolved by `ve_diagnose`; when that operation is unavailable the deferred record is reported with the route's text, as base spec 2.8 says. Rust is not run on either unit |
| e. Run the inherited `norm-defaults@0` difference to ground before S3; fix a reachable verdict difference outside the plan | Closed (`s3-pre.md`, `s4-pre.md`; S5-pre is S5's). S7-pre of this plan handles the alternatives route's two-validator verdict differences the same way: run to ground in shadow, fixed outside the plan, before the switch |
| f. Strike `Engine.run` as a route's validation; "contract first" covers diagnostics only | Each switch puts a call of the engine inside the branch of `run_case` that returns an error row of the Lean route, at `ve/alternatives.py:32` and `ve/risk.py:241`; it hands back the same row object, and on an accepted case the diagnostic modules are not imported. `decodeAltSource`, `decodeRiskSource`, `admitDecision` and `validateDecision` keep deciding the verdict and are not edited |
| g. Under a `view`, `path` is the include site; the generator imports `FORBIDDEN`; one switch commit per unit | Neither contract has an include or a view, so every `path` is the plain pointer into the root and no record has an `inner_path`. The views the routes apply (`normsView`, `riskNormsView`) are applied inside the inherited hooks, not by the engine. The generator is unchanged. Item 1 is two of the per-unit switch commits: one commit, one revert, its own delta report and release note, each |
| h. After S3 the DRI reviews the gate; if it fails, stop; S4 onward needs a separate decision | The gate is met (S4 spec section 1). The separate decision for S7 is the pointer (`f72d830c`, 2026-10-04) and covers stage S7 only. S8 onward needs another |
| Scope: S1c moved to S4 | The Rust engine is S4 item 2 and is not started. Neither unit of S7 has a Rust part; item 2 is one text in the Rust evaluator and uses no engine |

## 4. What S7 does not include

| Not included | Why |
|---|---|
| S4 items 2 to 6 and S5's two contracts | separate statement specs; S5's generalisation (S5.0) is a prerequisite of S7's tooling, not of its tables. Until S4 item 5 exists the environment is one inherited hook in both contracts; until S4 item 6 the formula syntax inside a unit and the typing are inherited; and since S5's `norms@0` is not merged, W1's unit checks are authored here from the Lean route and not included (section 8, question 7) |
| the `admission` kind of both routes (`ve/admission.py:508–514`) | the alternatives source inside a W2 document is reached through `splitDocument` and `decodeDoc`, and the W2 checks after it are row 13's; the adapters refuse an `admission` case, and the call site is not switched |
| the kinds whose rejections continue after the source: `alt-validate`, `alt-conflict`, `alt-followable`, `alt-certificate`, `risk-conflict`, `risk-followable`, `risk-audit`, `risk-certificate` | a scenario, package, witness or log rejection has no check in either table; such a row would always be a residual. `ve_diagnose` still accepts the kinds that carry the root's members; `public_rejection` is called for `alt-elaborate`, `risk-elaborate` and `risk-decision` only |
| Python's `Environment` as a validator of either unit, and the `Environment` statement of `ve/alternatives.py:24` | it validates the environment only, in its own order; it is the English surface's and admission's validator, and on the alternatives route an earlier statement than the switched one. It keeps its texts (section 8, question 5) |
| any change of a Lean text, a Python text in `ve/environment.py` or `ve/risk.py`, or a Rust text other than item 2 | the contract's classes and texts are the route's; a changed class is a product decision this plan does not make |
| the record's log (`risk-audit`) | a different wire unit (`ve-risk-log@0`), not in the base plan's table |

## 5. Gates for every commit of S7

The four conservativity gates of base plan 5.2, as the debate amended them:

- **C1.** No diff in a decoder, canonical serialiser, identity serialisation or digest function. The diff-scope
  list of each commit is in the statement spec (7.2); `ve/environment.py`, `ve/risk.py` (except the one call
  in `run_case`), `ve/alternatives.py` (the same), `ve/errors.py`, `ve/backends/diagnostics.py`,
  `ve/wire_contract/engine.py` and every Lean module except the generated tables and the unit registry are
  outside it.
- **C2.** Legacy verdicts equal their snapshot; the Lean engine reports a fault exactly when the route rejects,
  at zero tolerance; the Python engine, where it completes diagnosis, reports a fault only when the route
  rejects, and its deferred share is reported; Rust is not run.
- **C3.** Public diagnostics change only as the signed delta of the unit lists; the gate fails on a change
  outside it.
- **C4.** `lake build`, `lean/audit.py`, `frozen.py` and the manifest test pass; the inventory diff is additions
  and generated rehashes, plus the one append-only registry diff of edit c.

And three that the pointer names:

- **The corpus-completeness test is kept.** `tests/test_wire_gate_corpus.py` keeps its three tests for every
  earlier unit, unweakened, and gains the same three for each new unit; an input that item 1's new tests
  submit must be in the unit's corpus like any other.
- **`tools/wire_contract.py --check`** passes in the gate and the hook, for every contract.
- **The difffuzz baseline must not grow.** Vacuous while `infra/difffuzz` is unmerged (section 0, item 8); if
  it merges first, each S7 commit's gate compares the baseline before and after and fails on growth.

## 6. Steps and effort

| Step | Content | Effort |
|---|---|---|
| S7.0 | after S5.0 has merged: the root-to-case function per unit, the gate's row-based delta and consultation count, the `None` registry entries, the recorder's wrappers; the pilot's and S5's outputs byte-identical | 1 d |
| S7.1a | `alternatives@0`: contract, examples, `ve/alternatives_contract.py` (adapter, `legacy_validation`, the registry of deferred names), `lean/VE/WireContract/Hooks/Alternatives.lean`, generated table and English table, catalogue, shadow gate | 2.5 d |
| S7.1b | the measurement commit for `alternatives@0`, in shadow; the gate enforces S7-pre and the class rule from here | 0.5 d |
| S7.1c | DRI review of the delta: the signing file and the release note | review |
| S7.1d | the switch commit for `alternatives@0`: status, revision, `public_rejection` with the Lean consultation, the call site, the `wire.diagnose` mode and call site, tests, the paragraph in alternatives.md | 0.5 d |
| S7.2 | item 2: the one line of `risk.rs`, the differential case, the release note | 0.5 d |
| S7.3a | `risk@0`: contract (source and record), examples, hooks in both languages, generated files, catalogue, shadow gate | 4 d |
| S7.3b, c, d | measurement, DRI review, switch, as for `alternatives@0`; the paragraph in risk.md | 0.5 d + review + 0.5 d |
| S7-pre | the two-validator verdict differences of the alternatives route run to ground; a fix outside the wire work; `s7-pre.md` | 0.5–1 d |

About 10.5 to 11 engineer-days, against the base plan's 6 for the S7 row, which did not count the record, the
generalisation, the measurements or the switches. Order: S7.0 first, after S5.0 has merged; S7.1a to S7.1d;
S7.2 at any time before S7.3d; S7.3a to S7.3d; S7-pre runs during the first shadow and blocks the
`alternatives@0` switch. The statement review reads the statement spec and this plan before S7.0.

## 7. Risks

| Risk | Mitigation |
|---|---|
| The diagnostic layer changes a verdict | the call is inside the branch that returns an error row and returns the same row object; a test scans each call site's shape; the gate asserts the row's `status` and `id` against the route's row on every rejected case |
| The engine or the Lean consultation raises and turns a rejection into a crash | `public_rejection` returns the row unchanged on any exception, and `CheckerUnavailable` from `wire.diagnose` is the deferred record; the gate requires zero exceptions |
| A message changes that nobody signed | C3: the gate fails on a measured change whose check has no signature, and on a signature with no measured change |
| A Lean hook calls a coarse frozen function and fails for a reason that belongs to a later check | every hook of both units is one step of the route in the route's order, calling the frozen function of that step on the decoded value of the earlier steps; the classifier sets are the route's own multi-step functions, mapped by fixed leading texts; a coarser failure shows as an engine mismatch in tier 0 |
| The table misses a rejection of the route (a residual) | the route's fallback texts that no input reaches (`InvalidInput: alternatives block is not well-formed` and five more, statement spec 2.3 and 2.4) are not in the tables; the gate's residual count must be 0 on tiers 0, A, B and the replayed suites, which include every input of the 84-case diagnostics test |
| The first production Lean consultation is slow or flaky | it runs only on a rejection of a Lean-only route, where a Lean process has just run; a timeout is `CheckerUnavailable` and gives the deferred record; the gate counts consultations and their outcomes |
| The generalisation breaks the pilot or S5 | S7.0 is its own commit; every earlier unit's reports, gate numbers and generated files are compared byte for byte |
| The corpus misses an input class, so the signed list is incomplete in the field | the corpus-completeness test is kept per unit; the claim is "complete on the corpus", stated as such |

## 8. Open questions

1. **No debate was held on S7.** The debate files are the base plan's. The statement review is the first review
   of anything specific to S7; it reads this plan with the statement spec.
2. **The record inside `risk@0`.** This draft puts admission and validation of a decision record into `risk@0`
   as guarded phases with two classifier sets (section 0, item 5). The alternative is a separate unit
   `risk-decision@0` with its own root; it would separate the corpora and the deltas and need its own row of
   the base plan. The DRI's call.
3. **The Lean consultation in production.** This draft follows base plan 2.5: a deferred Python outcome is
   resolved by `ve_diagnose` at the call site, and the record is Lean's. The alternative is the S4 and S5
   practice (no consultation; the deferred record with the route's text), under which almost every rejection
   of these units would carry a deferred record and the public text would never change. The DRI's call; this
   draft recommends the consultation because it is what makes the switch mean something for Lean-only routes.
4. **The Python fast path is the gate phase only.** Python's engine completes diagnosis on the profile gate and
   the block's presence and defers at W1's environment decoder. That is honest and small; a larger Python
   registry would need Python hooks for checks that Python never reaches in production, because the engine
   stops at the first deferred instance.
5. **Two validators on one route.** `ve/alternatives.py:24` runs Python's `Environment` before the Lean route.
   This draft leaves that statement alone (its rejections keep Python's text and have no record) and switches
   the Lean-row branch only. The alternative is to switch both statements, so that a block fault's public
   text becomes the contract's (Lean's order) even when Python rejected it; that is a second delta on the same
   call site. Recorded for the DRI.
6. **The kinds switched.** `alt-elaborate`, `risk-elaborate` and `risk-decision` only (section 4). A caller of
   another kind gets the route's row as today.
7. **No include of `norms@0`.** The S5 contract is not merged, and its texts are Python's where Python and Lean
   differ (S5 spec D3), while these routes are Lean's. Including it would change the public text of W1 unit
   faults on these routes to Python's wording. This draft authors W1's unit checks on these routes with the
   Lean route's texts and no include; when S4 items 5 and 6 and S5 exist, making the shared checks includes is
   a later revision of each unit with its own delta.
8. **The GENERIC texts.** Row 9 lists them as diagnostics that may change and their test as the tolerance
   removed. They are W1 vocabulary texts inside the inherited environment hook; S7 cannot make them uniform
   without S4 item 5, and the test's tolerance is kept (section 2).
9. **The unit registry.** `Diagnose.lean` gains two entries by the append-only exception S5 records; the
   alternative S5 offers (moving the list to `DiagnoseMain.lean`) is still open there.
10. **The public row of `run_case`.** `tests/test_risk_diagnostics.py::test_route_answer_is_leans_through_python_dispatch`
    asserts byte-equality between `run_case`'s row and the route's. After the switch the rows differ in
    `diagnostic` and in the signed `error` texts; the test keeps its assertion for `status`, `id` and every
    other member and compares `error` under the signed list. Listed as a changed expectation of the switch
    commit.
11. **Effort figures** are this draft's; the base plan's 6 days covered authoring only.
12. **The stub was not compiled.** The session that wrote the statement spec could run no Lean (statement spec,
    status paragraph). The fixture numbers that the spec derives from the Lean definitions are marked as
    derived, with the `#eval` that confirms each in the stub; the first build task runs it.

## 9. Debate response table (draft 2)

Source: `manage-agents/debates/design-wire-s7/{fable,astra}.md`, a copy of the base plan's debate. Verdict there:
**BUILD (exact edits): S0 to S3 only, S1c moved to S4**; S4 onward by a separate decision.

| Debate edit | Change in this draft |
|---|---|
| a | section 0, item 2; section 3, row a; statement spec 2.13 |
| b | section 3, row b; section 5, C1; statement spec 2.7 and 4.2 |
| c | section 3, row c; section 5, C4; section 8, question 9; statement spec 5.3 and 7.3 (C4) |
| d | section 0, items 2 and 6; section 3, row d; section 5, C2; statement spec 2.7 (the consultation and the deferred record) and 2.2 (no Rust column) |
| e | section 2 and section 6, step S7-pre; section 3, row e; statement spec 2.12 |
| f | section 0, item 4; section 3, row f; statement spec 2.8 |
| g | section 3, row g; section 2 (one commit, one revert, delta report, release note, per unit); statement spec 2.4 (no include, no view) |
| h | section 3, row h; section 1 (the gate's state) |
| Scope: S1c moved to S4 | section 0, item 7; section 4 |
