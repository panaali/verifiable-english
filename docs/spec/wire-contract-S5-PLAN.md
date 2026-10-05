# Wire contract stage S5: `norms@0` and `norm-defaults@0` (PLAN)

**Status:** plan only, draft 3, 2026-10-03, branch `design/wire-s5` from `main` at `b2ce446e`. No code or proofs
change with this document. Draft 1 (`b2ce446e`) was a pointer of one paragraph: item 1 of this plan is stage S5 of
[wire-contract-PLAN.md](wire-contract-PLAN.md) (the **base plan**), "`norms@0` and `norm-defaults@0` switched
from shadow to the contract's diagnostics, accept/reject and identities unchanged, only diagnostics may become
uniform (listed per profile), the corpus-completeness test kept. Honest open questions." Draft 2 applied the
converged position of `manage-agents/debates/design-wire-s5/{fable,astra}.md` and wrote the plan out. The
item-1 statement spec is [wire-contract-s5.md](wire-contract-s5.md) (the **statement spec**); its statement
review comes before any build step. That review was held on draft 2 of this plan and draft 1 of the statement
spec (`manage-agents/debates/wire-s5-spec/{fable,astra}.md`): three rounds, both reviewers on FIX in each, and
then the DRI's ruling, which makes Fable's round-3 position the joint one. Draft 3 applies its edits to this
plan (section 10) and makes no other change. [wire-contract.md](wire-contract.md), the statement spec of S0 to
S3 with its build responses, is the **base spec**; [wire-contract-s4.md](wire-contract-s4.md) and
[wire-contract-S4-PLAN.md](wire-contract-S4-PLAN.md) are the **S4 spec** and the **S4 plan**, whose shape this
plan follows.

**What the debate files are.** As for S4, `debates/design-wire-s5/` holds the three files of
`debates/design-wire/`, word for word: the debate on the base plan (CONVERGED after round 3; Sol at xhigh stood
in for Astra, as `astra.md` records), and `TOPIC.md` still asks about the base plan. No reviewer had read this
plan before the statement review. The converged edits a to h are already in the base plan (its section 11) and
were restated for S4 (S4 plan, section 3). "Applying them exactly" therefore means here: each edit is restated
as it binds stage S5 (section 3), and no design choice of the debate is reopened or added to. Everything in
this plan that the debate did not decide is marked as a choice of this draft and listed in section 8 for the
statement review.

The plan was written from reading the sources at `b2ce446e`; nothing was built or run, and every `file:line`
reference must be re-read at each step.

## 0. Decision in brief

1. **Stage S5 is one item with two units, in order.** Item 1 is the base plan's rows 6 and 7 of 5.3: the
   contract `norms@0` (W1 norm documents), then the contract `norm-defaults@0` (the `unspecified` completion),
   each taken through every step of base plan 5.1: author, hooks, generate, shadow, delta report, DRI review,
   switch. Neither contract exists today, so "switched from shadow" in the pointer is read as "after a shadow
   period of its own", as the pilot had in S3 and S4.
2. **The machinery is generalised first (S5.0).** Everything after the lint in the pilot's tooling is wired to
   `soft-norms@0` by name: the generated Lean module, the English table, the examples, the fault catalogue, the
   gate, the delta, the golden file, the recorder, the test-inputs file, the pre-commit hook and the Lean unit
   registry (section 1). S5.0 makes each take a unit, with the pilot's outputs byte-identical afterwards.
3. **Each switch changes one thing in public.** At one call site per unit, when Python rejects a submitted norm
   source, the error carries the contract's record. When a check of the table fails, the record names the first
   one that fails and the message is that check's text; otherwise the message is the validator's. No verdict, no
   identity, no code and no Lean row changes. The complete list of changed messages is measured on each unit's
   corpus and signed by the DRI before its switch commit.
4. **The contract still decides no verdict.** The engine runs only after the legacy validator has rejected,
   inside the handler of that rejection, and hands back the same error (edit f, section 3).
5. **The order of each table is Python's**, the authority of `admission` (`ve/assurance-manifest.json:670`), as
   base plan 5.1 step 1 and rows 6 and 7 require. The Lean routes check the same facts in a different order in a
   few places (section 1), so on an input with two faults the Lean route's text can differ from the record. Lean's
   rows never switch; that difference is reported, not enforced, and is not a claim of the plan. One order
   inside the table is not Python's: within one formula, the syntax checks name the first node refused in
   pre-order (statement spec 2.5), which on a formula with a non-first-order tag is not the node at which
   Python's decoder raises.
6. **Rust has no column.** Rust decodes no norm document and no `norm-defaults@0` environment (section 1), so
   neither unit needs the Rust engine of S4 item 2, which stays undone.
7. **Base plan rows 2 to 5 are still not contracted** (S4 items 3 to 6 are not started), so the environment, the
   formula decoder and typing stay inherited checks with language-specific text, as in the pilot. The base plan
   put rows 2 to 5 first for this reason; the pointer orders S5 before them, and this draft follows the pointer
   and records the cost (section 8, question 2).

## 1. Where the work stands (read at `b2ce446e`, not run)

| Fact | Source |
|---|---|
| One contract exists, `soft-norms@0`, public at revision 4; `limits.json` has four names and `names.json` four classes | `ve/wire_contract/soft-norms@0.json:3–5`, `limits.json`, `names.json`, `contracts.lock` |
| S4 item 1 is done: the pilot's switch, its measurement (8,796 cases, 498 text changes in seven signed checks, zero mismatches), the review fixes and the DRI's countersignature. S4 items 2 to 6 are not started | S4 spec sections 14 to 16; `conformance/wire-contract/s4-integration.md` |
| The Python engine supports `include` with `at`, `view`, `as` and `says`; the included contract is loaded by name and must be in `uses` and the lock. The Lean generator inlines an included contract's entries into the including table, so a revision of the included contract changes the including module too | `ve/wire_contract/engine.py:57–68, 419–432`; `tools/wire_contract_lean.py:140–147` |
| The pilot's tooling is hard-wired to `soft-norms@0` after the lint: the registry import, the examples, the English table path, the Lean table module, the catalogue, the gate's unit, report and binaries, the delta's and golden file's inputs, the recorder's wrappers, the corpus test and the pre-commit hook | `tools/wire_contract.py:70–73, 501–510, 583–639`; `conformance/wire_contract_gate.py:47–54, 279, 415–427, 484, 494–495, 757`; `conformance/wire_contract_delta.py:11–17`; `conformance/wire_contract_golden.py:35–38`; `conformance/wire_contract_faults.py:23, 428`; `tests/contract_input_recorder.py:35–112`; `tests/test_wire_gate_corpus.py:43`; `tools/hooks/precommit.py:448–462` |
| `ve_diagnose` looks a unit up in a hard-coded list in a hand-written, hash-listed module; the executable root is not hash-listed | `lean/VE/WireContract/Diagnose.lean:32–38, 59`; `VE/Route/frozen-sources.sha256:260`; `lean/DiagnoseMain.lean` |
| The `admission` operation's authority is Python. A `norms@0` document with a norm construct and no soft, defaults, alternatives or quantity profile goes to `_admit_norm_document_python`, which decodes the environment, checks the profile, validates the document's units and then builds `NormDocument(env, active)`; a `norm-defaults@0` document goes to `admit_norm_defaults_document`, which builds `UnspecifiedDocument(env, [NormDocument._decode(c) …])` | `ve/assurance-manifest.json:667–674`; `ve/backends/dispatch.py:61`; `ve/admission.py:499–526`; `ve/norm_admission.py:51–98`; `ve/norm_defaults_route.py:136–190` |
| Python's legacy validators: `NormDocument.__init__` (profile, rule count, decode every unit, then per rule: name, duplicate, reserved name under the profile, regulated predicate, sign and carve-outs, typing; then `over` references, the precedence DAG, depth, the layer DAG) and `UnspecifiedDocument.__init__` with `_build` (profile, no soft or alternatives, W1, the three limits, typing over the filled environment with the node budget and height 15, the fill premises' budget) | `ve/norms.py:202–275`; `ve/norm_defaults.py:198–265, 222–227` |
| Python's texts in this unit are often without the class prefix (`rules`, `precedence depth`, `rule x`, `AST exceeds 10,000 nodes`), and three rejections are raised as `VEError` with a text that names another class (`UnsupportedProfile: norms@0 is required`, `UnknownSymbol: regulated predicate …`, `UnsupportedProfile: regulated closure edge …`). The stage-0 baseline has 56 `norms_elaborate` cells with the second text and code `InvalidInput` | `ve/norms.py:204, 206, 215, 217, 223, 232, 252`; `ve/ast.py:212`; `conformance/baseline-2026-09/python.json` |
| Lean's legacy validators: `ve_norms_route` decodes a source by `Norms.Wire.decodeSource` (envelope, gate, vocabulary, the regulated extension, document gates, every norm decoded in order, then `Tree.check`); `ve_norm_defaults_route` rewrites `unspecified` to `deny`, strips the profile, runs the same decoder, then `checkAuthor` (reserved names, the three limits, the node budget with the fill guards, height 15). Neither route reports a `code`; rows carry a bare `error` string, whose leading word Python maps to a class | `lean/VE/Norms/Wire.lean:231–255, 274–289`; `lean/VE/Norms/Tree.lean:302–368`; `lean/VE/NormDefaults/Wire.lean:51–59, 73–101`; `lean/VE/Norms/Run.lean:191–192`; `lean/VE/NormDefaults/Run.lean:194–195`; `ve/backends/diagnostics.py:31–52` |
| Where the two legacy orders differ inside the unit, from reading: Lean checks that `name` is a string and `sign` a Boolean while decoding each rule, Python in the per-rule loop after decoding every rule; Lean checks reserved `unsaid--` names after every W1 check, Python inside the per-rule loop; Lean refuses data flags under `norm-defaults@0`, Python has no such check. Inside a formula: Lean's decoder refuses a non-first-order tag and a name that is not a string at the node, Python's decoder reads both and typing refuses them; Lean's `check` types a whole formula before it adds its nodes to the running total, Python counts each node before it checks it | `lean/VE/Norms/Wire.lean:237, 241`; `ve/norms.py:214, 218–220, 224`; `lean/VE/NormDefaults/Wire.lean:77, 89`; `lean/VE/Norms/Wire.lean:279`; `lean/VE/Norms/Wire.lean:191–223`; `ve/ast.py:466–529`; `lean/VE/Norms/Tree.lean:343–346`; `ve/ast.py:209–215, 245–246` |
| Rust decodes no norm document, has no `norms-*` or `norm-defaults-*` case kind, and refuses any environment that lists `norm-defaults@0`; the specs say so by design | `rust/ve/src/main.rs:97–295`; `rust/ve-core/src/environment.rs:178–193, 404–407`; norms.md 11.6; norm-defaults.md 8 |
| The three-way norms tests compare texts by substring (`AST exceeds`, `invalid act phrase`) or status only; the norm-defaults three-way scripts compare only accepted inputs and count any Lean error row as a mismatch; the admission-tampering test compares Python's text with Lean's exactly | `tests/test_norms_three_way.py:112–118, 168–170, 202–205, 223, 320, 409–411`; `conformance/norm_defaults_three_way.py:237–238`; `tests/test_norm_defaults_three_way.py:205–208` |
| norms.md 11.1 calls its diagnostics "shared text in Python and Lean"; neither norms.md nor norm-defaults.md has a known-limitation paragraph on diagnostics | `docs/spec/norms.md:1045–1056`; `docs/spec/norm-defaults.md:715–718` |

## 2. Item 1: the two units become public

The statement spec fixes every detail; this section is the plan-level summary.

- **S5.0, the generalisation.** `tools/wire_contract.py`, the gate, the delta, the golden and catalogue files, the
  recorder, the corpus test, the pre-commit hook and the Lean unit registry take a unit. The generated module and
  the English table are named from the contract (`norms@0` gives `Tables/Norms.lean` and
  `docs/spec/norms-wire-table.md`, as `soft-norms@0` gives `Tables/SoftNorms.lean` and
  `soft-norms-wire-table.md`). The pilot's generated files, reports and gate numbers are byte-identical after it.
  Nothing in `ve/` changes except a registry table in the tooling's own module.
- **Before each switch, S5-pre (blocks the switch).** The shadow gate of each unit lists every corpus case on which
  Python's legacy validator and the Lean route disagree on the verdict (`legacy_verdict_differences`). A verdict
  difference is outside this plan's licence and is fixed separately, as S3-pre and S4-pre were, with its record
  `conformance/wire-contract/s5-pre.md`. Candidates from reading: data flags under `norm-defaults@0` (Lean
  rejects, Python does not); a Lean rejection by `norms-elaborate` after the decoder has accepted; the fill
  premises over their shared node budget (Python rejects, Lean has no check known from reading; the statement
  spec's fixture D11 is such a source). Class differences between the two (Python's `InvalidInput` against
  Lean's `UnsupportedProfile` on `norms@0 is required`) are recorded and not fixed: the contract's classes are
  Python's (section 8, question 5).
- **The measured delta, per unit.** The gate computes, for every corpus case that Python's legacy validator
  rejects, the record the overlay would report, and lists every case whose message or class would change,
  grouped by check. The public delta is the part of that list on the cases that reach the switched statement
  (the statement spec's handler-reaching cases, 2.11). A source that fails earlier, on the environment or on
  the route's profile check, makes the call raise today's error without a record; the gate checks that too.
  The DRI signs the list check by check (`conformance/wire-contract/<unit>-switch.json`), with the release
  note. This is step 5 of base plan 5.1, done as S4 did it: the measurement is a commit of its own, before the
  switch and in shadow.
- **The domains.** Each unit is measured on the sources that Python's dispatch hands to its validator. An
  environment that lists `norm-defaults@0` is outside `norms@0`'s domain: its sources are `norm-defaults@0`'s,
  whose table includes the first, and `norms@0`'s Lean legacy validator is `ve_norms_route` alone. The
  reserved-name check of `norms@0` can then fail only through the include, and is an allowed coverage gap of
  `norms@0` (statement spec 2.2 and 8.4).
- **The switch commit, per unit** (step 6): the contract's `status` becomes `public` and its revision rises; one
  function, `public_rejection`, in the unit's contract module and one call site are added; generated files, the
  lock and the reports are regenerated. The legacy validators are not edited. At the call site the error carries
  the contract's record. When a check of the table fails, the record names the first one that fails and the
  message is that check's text; otherwise the message is the validator's.
- **What may change, for `norms@0`** (base plan 5.3, row 6): Python's message on the checks of the signed list.
  From reading, those are the rule count, the two unit-shape checks, the duplicate rule name and the precedence
  depth, which gain the class prefix or lose Python's field lists; the rule-name check on a name that is not
  a string, or that is a string containing `'`, `\` or a character that Python's `repr` escapes; and the
  formula-syntax check at a node with a non-first-order tag, whose message becomes `invalid indexed formula`
  (statement spec section 6). Lean's route rows do not change; Rust has no column.
- **What may change, for `norm-defaults@0`** (row 7): the three limits, the node budget, the height and the fill
  premise, which gain the prefix, and the included `norms@0` checks as above. Rejections of this unit are compared
  between Python and Lean for the first time, as row 7 says.
- **What rows 6 and 7 ask to delete.** Step 6 deletes "the unit's test tolerance" and "the spec's
  known-limitation paragraph". Row 6 names the substring matches of `tests/test_norms_three_way.py`. Of those,
  only the `AST exceeds` match (lines 168 to 170) is about this unit, and it reaches `NormDocument` directly, not
  the switched call site, so the switch does not change its input's message; the gate replaces the tolerance by
  comparing every text of the unit at zero tolerance, and the test keeps its substring (statement spec 2.9). The
  `invalid act phrase` matches are environment texts, row 4's. Row 7 names no tolerance. Neither spec has a
  known-limitation paragraph; both gain the paragraph of the statement spec's 3.5. The deletions are empty for
  these units; that is recorded here rather than invented.

## 3. The converged edits, as they bind stage S5

Each row restates one edit of the joint position (Fable's round 3, which Astra's round 3 restates) for S5. The
base plan's text for each edit is unchanged.

| Edit | What it requires of S5 |
|---|---|
| a. "By construction" is limited to table expansion, and to position, code, path and text conditional on equal predicate results; T3 order is test-enforced; raw JSON scanner order is open | "Uniform" after a switch has this meaning only. For each unit: Python's public text is the contract's template text; that it equals the Lean engine's record is constructed only where every predicate reached returns the same result in both, and is tested on every corpus case that Lean reads. The order inside the three classifier sets of `norms@0` (3.8, 3.9, 4.7) is the formula order of the validators, and inside a formula the first node refused in pre-order: for 3.8 and 3.9 by a diagnostic walk, the budget before the shape at each node and a non-first-order tag refused at its node, which is not always Python's decoder's order; for 4.7 by `_Checker`'s order, the node count before the node's own check. It is test-enforced. The Lean route's own first fault on a multi-fault input is a third thing: the table's order is Python's, so it can differ, and no claim is made about it. The scanner order belongs to S4 item 3 and stays open there |
| b. C1 covers identity serialisation; `VEError.to_dict()` may gain `diagnostic` | The member exists since S1a and is set at one call site since S4. Item 1 sets it at two more; nothing in `to_dict()` changes, and `code` is never written by either switch |
| c. C4 allows additions, generated rehashes, and a reviewed append-only `VE/Audit.lean` diff with its rehash in S1b; the lemmas stay optional | `VE/Audit.lean` is not touched. In S5 the inventory diff of a commit is additions (two hooks modules, two tables) and generated rehashes (`Limits.lean`, `Names.lean`, and the pilot's table, whose header names their hashes), plus one reviewed append-only diff that the debate did not foresee: `VE/WireContract/Diagnose.lean`'s unit registry gains two imports and two entries, no existing line changing. That exception is recorded in the statement spec (5.3) and in section 8, question 4, in the words of the S1b one |
| d. C2 and the tolerance removals apply where an implementation supports the unit and completes diagnosis; a deferred outcome carries the contract, revision, deferred check id and legacy text, has no `check`, `code` or `path`, and is never a residual | Python's registries for both units are complete, so Python is compared at zero tolerance and its deferred count is 0. The call sites consult no Lean process; if an engine ever defers there, the deferred record is reported with the legacy text. Rust does not support either unit and is not run on it; there is no Rust column and no Rust tolerance to remove |
| e. Run the inherited `norm-defaults@0` difference to ground before S3; fix a reachable verdict difference outside the plan | Closed (`s3-pre.md`, `s4-pre.md`). S5-pre of this plan handles the two units' legacy verdict differences the same way: run to ground in shadow, fixed outside the plan, before the switch |
| f. Strike `Engine.run` as a route's validation; "contract first" covers diagnostics only | Each switch puts a call of the engine inside the handler of a rejection that the legacy validator already raised, at `ve/norm_admission.py:96` and `ve/norm_defaults_route.py:174`; it hands back the same error object, and on an accepted input the diagnostic modules are not imported. `Environment`, `NormDocument` and `UnspecifiedDocument` keep deciding the verdict and are not edited |
| g. Under a `view`, `path` is the include site; the generator imports `FORBIDDEN`; one switch commit per unit | Neither contract has a view. `norm-defaults@0` includes `norms@0` at the root without a view, so every `path` is the plain pointer into the submitted root and `check` carries the include id (`w1/4.2`); no record has an `inner_path`. The generator is unchanged. Item 1 is two of the per-unit switch commits: one commit, one revert, its own delta report and release note, each |
| h. After S3 the DRI reviews the gate; if it fails, stop; S4 onward needs a separate decision | The gate is met (S4 spec section 1). The separate decision for S5 is the pointer (`b2ce446e`, 2026-10-03) and covers stage S5 only. S6 onward needs another |
| Scope: S1c moved to S4 | The Rust engine is S4 item 2 and is not started. Neither unit of S5 has a Rust part, so S5 does not need it |

## 4. What S5 does not include

| Not included | Why |
|---|---|
| S4 items 2 to 6 (the Rust engine, `json@0`, `envelope@0.2`, `vocabulary@0.2`, `formula@0.2` and `model@0.2`) | separate statement specs; the pointer covers S5 only. Until item 5 exists, the environment is one inherited hook in both contracts, and until item 6, the formula decoder and typing are inherited classifier members; their texts stay language-specific (base spec D8) |
| the other entry points that build a `NormDocument` or an `UnspecifiedDocument` (`ve.document`, quoted norms, the readings, alternatives, risk, soft and rights routes, the English front ends, the completions audit) | each keeps today's message; listed in the statement spec 2.9, as the S4 spec listed the soft ones |
| the Lean-authority path of `admission` (`VE_AUTHORITY=lean`) | its rejection is a Lean row read by `checker_error`; no Python validator runs; not switched |
| any change of a Python class or text in a legacy validator | the contract's classes and the residual texts are Python's; a changed class is a product decision this plan does not make (section 8, question 5) |

## 5. Gates for every commit of S5

The four conservativity gates of base plan 5.2, as the debate amended them:

- **C1.** No diff in a decoder, canonical serialiser, identity serialisation or digest function. The diff-scope
  list of each commit is in the statement spec (7.2); `ve/norms.py`, `ve/norm_defaults.py`, `ve/environment.py`,
  `ve/errors.py`, `ve/wire_contract/engine.py` and every Lean module except the generated tables and the unit
  registry are outside it.
- **C2.** Legacy verdicts equal their snapshot; each engine reports a fault exactly when its legacy validator
  rejects, at zero tolerance, where the language completes diagnosis (Python and Lean; no Rust).
- **C3.** Public diagnostics change only as the signed delta of the unit lists; the gate fails on a change outside
  it.
- **C4.** `lake build`, `lean/audit.py`, `frozen.py` and the manifest test pass; the inventory diff is additions
  and generated rehashes, plus the one append-only registry diff of edit c.

And two that the pointer names:

- **The corpus-completeness test is kept.** `tests/test_wire_gate_corpus.py` keeps its three tests for the pilot,
  unweakened, and gains the same three for each new unit; an input that item 1's new tests submit must be in the
  unit's corpus like any other.
- **`tools/wire_contract.py --check`** passes in the gate and the hook, for every contract.

## 6. Steps and effort

| Step | Content | Effort |
|---|---|---|
| S5.0 | the generalisation: tooling, gate, reports, recorder, corpus test, hook and Lean registry take a unit; the pilot's outputs byte-identical | 1.5 d |
| S5.1a | `norms@0`: contract, examples, Python hooks and registry (`ve/norms_contract.py`), Lean hooks (`Hooks/Norms.lean`), generated table and English table, catalogue, shadow gate | 2.5 d |
| S5.1b | the measurement commit for `norms@0`, in shadow: the stored reports over the whole corpus; the gate enforces S5-pre and the class rule from here | 0.5 d |
| S5.1c | DRI review of the delta: the signing file and the release note | review |
| S5.1d | the switch commit for `norms@0`: status, revision, `public_rejection`, the call site, tests, the paragraph in norms.md | 0.5 d |
| S5.2a | `norm-defaults@0`: contract (including `norms@0`), examples, hooks in both languages, generated files, catalogue, shadow gate | 1.5 d |
| S5.2b, c, d | measurement, DRI review, switch, as for `norms@0`; the paragraph in norm-defaults.md | 0.5 d + review + 0.5 d |
| S5-pre | the legacy verdict differences of each unit run to ground; a fix outside the wire work; `s5-pre.md` | 0.5–1 d |

About 8 to 8.5 engineer-days, against the base plan's 5 for the S5 row, which did not count the generalisation,
the measurements or the switches. Order: S5.0 first; S5.1a to S5.1d, then S5.2a to S5.2d (the second contract
includes the first and needs its revision fixed); S5-pre runs during each shadow and blocks that unit's switch.
The statement review read the statement spec and this plan before S5.0 and returned FIX. By its joint position
the verdict is PASS, and S5.0 may start, once its edits are in both documents (section 10).

## 7. Risks

| Risk | Mitigation |
|---|---|
| The diagnostic layer changes a verdict | the call is inside the rejection's handler and returns the same error object; a test scans each call site's shape; the gate asserts the raised object's type and code against the legacy validator on every rejected case |
| The engine raises on some input and turns a rejection into a crash | `public_rejection` returns the error unchanged on any exception; the gate requires zero such cases |
| A message changes that nobody signed | C3: the gate fails on a measured change whose check has no signature, and on a signature with no measured change |
| The two legacy validators disagree on a verdict | found by the shadow gate (C2 in both languages on every case), fixed outside the plan (S5-pre), before the switch |
| A Lean hook calls a coarse frozen decoder and fails for a reason that belongs to a later check | the hooks of `norms@0` work per formula and per graph: the syntax decoder and the typing walk that the hooks module holds (statement spec 2.5), and `dependencyOrder`; none calls `decodeSource`, and `typeDiagnostic` is not run on a whole formula; a coarser failure shows as an engine mismatch in tier 0 |
| The include is new: a defect in scopes shows only now | the engine corpus already covers includes (`mid@0`, `forms@0`); `norm-defaults@0`'s fixtures D3 to D5 and D12 exercise included checks at every phase |
| The generalisation breaks the pilot | S5.0 is its own commit; the pilot's reports, gate numbers and generated files are compared byte for byte |
| The corpus misses an input class, so the signed list is incomplete in the field | the corpus-completeness test is kept per unit; the claim is "complete on the corpus", stated as such |

## 8. Open questions

1. **No debate was held on S5.** The debate files are the base plan's. The statement review was the first review
   of anything specific to S5; it read this plan with the statement spec, and its edits are in section 10.
2. **S5 before S4 items 3 to 6.** The base plan put rows 2 to 5 first because the later profiles inherit them.
   This draft follows the pointer: the environment, the formula decoder and typing are inherited checks with
   language-specific text in both contracts, and turning them into includes after items 5 and 6 is a second delta
   for each unit. If the DRI prefers the base plan's order, item 1 waits for S4 items 5 and 6 unchanged.
3. **What "stage S5" covers.** The pointer says both units are "switched from shadow"; no contract exists. This
   draft reads it as the whole of base plan 5.1 for each, with its own shadow and measurement. If the DRI meant
   one shadow period for both, the two measurements merge and the switches stay separate commits.
4. **The unit registry.** `ve_diagnose` keeps its contracts in a hard-coded list in a hash-listed module, so every
   new unit edits `Diagnose.lean`. This draft records the append-only exception for S5 (edit c). The alternative
   is to move the list to the executable root `DiagnoseMain.lean`, which is not hash-listed, so that later units
   add a hooks module and one line there; that is one edit of `Diagnose.lean` now and none later. The DRI's call.
5. **Classes.** The contract's classes are Python's, because the authority is Python and base plan 5.1 keeps the
   authority's rejected cells unchanged. Lean's leading words map to other classes on two checks (`UnsupportedProfile`
   and `UnknownSymbol` against Python's `InvalidInput`), so the record's class and a Lean-authority deployment's
   code would differ there. Aligning Python to Lean would change 56 cells of the frozen stage-0 baseline. Not
   proposed; recorded.
6. **The environment's class.** The inherited environment hook has one code of class `InvalidInput`, while the
   environment decoder raises several classes. On an environment fault the record's class and the error's code can
   differ; the statement spec exempts that check from the class rule and lists it as a limit until S4 item 5.
7. **One entry point per unit.** Only admission is switched. The document path (`ve.document`), quoted norms and
   the direct constructors keep today's messages, so the same fault can read differently through two entry points
   until their own rows.
8. **The unit's domain.** Python's `NormDocument` accepts closure and order environments (the family-norms mode)
   and `UnspecifiedDocument` accepts a listed `soft-norms@0`; the routes dispatch those elsewhere before either
   validator runs, and the Lean routes refuse them. The statement spec puts them outside the unit's domain (the
   adapter refuses the case; the catalogue never builds it) rather than listing them as verdict differences.
   The statement review added one exclusion, for the same reason: an environment that lists `norm-defaults@0`
   is outside `norms@0`'s domain, because the dispatch hands it to the defaults route, whose Lean validator
   runs checks that `NormDocument` does not.
9. **Non-first-order formulas.** Python's formula decoder reads a `reach` node and typing refuses it later; Lean's
   FOL decoder refuses it at once. The statement spec makes the syntax classifier refuse it at its node, in
   both languages, with the message `invalid indexed formula`: the classifier names the first node refused in
   pre-order, the budget before the shape, which is the order of Lean's decoder and not always that of
   Python's. On such an input the record's class (`SyntaxError`) stands against Python's legacy class
   (`UnsupportedProfile` at typing, or a `ResourceLimit` that the decoder raises at a later node), and the
   message changes. Exempted from the class rule, listed, and part of the signed delta; the shadow measures
   whether any corpus input reaches it. A name that is not a string is not a syntax fault: it fails typing in
   both languages, as it does in Python today.
10. **Effort figures** are this draft's; the base plan's 5 days covered authoring only.

## 9. Debate response table (draft 2)

Source: `manage-agents/debates/design-wire-s5/{fable,astra}.md`, a copy of the base plan's debate. Verdict there:
**BUILD (exact edits): S0 to S3 only, S1c moved to S4**; S4 onward by a separate decision.

| Debate edit | Change in this draft |
|---|---|
| a | section 0, item 5; section 3, row a; statement spec 2.13 |
| b | section 3, row b; section 5, C1; statement spec 2.7 and 4.2 |
| c | section 3, row c; section 5, C4; section 8, question 4; statement spec 5.3 and 7.3 (C4) |
| d | section 0, item 6; section 3, row d; section 5, C2; statement spec 2.7 (the deferred record at the call site) and 2.2 (no Rust column) |
| e | section 2 and section 6, step S5-pre; section 3, row e; statement spec 2.12 |
| f | section 0, item 4; section 3, row f; statement spec 2.8 |
| g | section 3, row g; section 2 (one commit, one revert, delta report, release note, per unit); statement spec 2.4 (the include without a view) |
| h | section 3, row h; section 1 (the gate's numbers) |
| Scope: S1c moved to S4 | section 0, item 6; section 4 |

## 10. Statement review response (draft 3)

Source: `manage-agents/debates/wire-s5-spec/{fable,astra}.md` and `result.txt`, the statement review of this
plan (draft 2) and of the statement spec (draft 1). Verdict: **FIX**, in each of three rounds; the DRI's ruling
of 2026-10-03 makes the proposed joint position of Fable's round 3 the converged one. The statement spec's
section 13 lists every edit, by the names the review gave them; the rows below are the edits that change this
plan. Nothing was run.

| Edit of the review | Change in this draft |
|---|---|
| J1. `norms@0`'s domain excludes an environment that lists `norm-defaults@0`; the reserved-name check is a coverage gap of `norms@0` | section 2 (the domains); section 8, question 8 |
| J2′, with the names. Inside a formula the syntax checks name the first node refused in pre-order, the budget before the shape; a name that is not a string fails typing, not syntax; the class exemption is wider | section 0, item 5; section 1 (the row on the two orders); section 3, row a; section 7 (the row on Lean hooks); section 8, question 9 |
| J3. Lean's typing hook counts each node before it checks it | section 1 (the row on the two orders); section 3, row a; section 7 (the row on Lean hooks) |
| J5 and J6. D11 is a concrete source; the fill premises share one node count | section 2 (S5-pre) |
| J7. The public delta and the call's record cover the handler-reaching cases; earlier errors are today's, and that is checked | section 2 (the measured delta) |
| J9. The rule-name message also changes on strings that `repr` escapes | section 2 (what may change, for `norms@0`) |
| J10. At a non-first-order tag Python's message becomes `invalid indexed formula` | section 2 (what may change, for `norms@0`); section 8, question 9 |
| Order of the work | the status paragraph; section 6 (the paragraph under the table); section 8, question 1 |

J4 (the Lean environment hook), J8 (the boundary of `fill_wellFormed`) and the D3 correction change the
statement spec only.
