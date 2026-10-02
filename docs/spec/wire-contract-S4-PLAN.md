# Wire contract stage S4: the first public contract (PLAN)

**Status:** plan only, draft 2, 2026-10-02, branch `design/wire-s4` from `main` at `2ee50149`. No code or proofs
change with this document. Draft 1 (`de2a37ae`) was a pointer of one paragraph: item 1 of this plan is stage S4 of
[wire-contract-PLAN.md](wire-contract-PLAN.md) (the **base plan**), "the first profile switched from shadow to the
contract's diagnostics, accept/reject and identities unchanged, only diagnostics may become uniform (listed per
profile), the corpus-completeness test kept". Draft 2 applies the converged position of
`manage-agents/debates/design-wire-s4/{fable,astra}.md` and writes the plan out. The item-1 statement spec is
[wire-contract-s4.md](wire-contract-s4.md) (the **statement spec**); its statement review comes before any build
step. [wire-contract.md](wire-contract.md), the statement spec of S0 to S3 with its build responses, is the
**base spec**.

**What the debate files are.** `manage-agents/wire-next.sh` filled `debates/design-wire-s4/` by copying the three
files of `debates/design-wire/`. They are word for word the debate on the base plan (CONVERGED after round 3; Sol
at xhigh stood in for Astra, as `astra.md` records), and `TOPIC.md` still asks about the base plan. No reviewer
has read this plan. The converged edits a to h are already in the base plan (its section 11). "Applying them
exactly" therefore means here: each edit is restated as it binds stage S4 (section 3), and no design choice of the
debate is reopened or added to. Everything in this plan that the debate did not decide is marked as a choice of
this draft and listed in section 8 for the statement review.

The plan was written from reading the sources at `2ee50149`; nothing was built or run, and every `file:line`
reference must be re-read at each step.

## 0. Decision in brief

1. **Stage S4 is done as six items, in order.** Item 1 is the switch of `soft-norms@0` from `shadow` to `public`:
   the first profile whose public diagnostic is the contract's. Items 2 to 6 are the S4 row of the base plan
   (section 7 there): the Rust engine, then `json@0`, `envelope@0.2`, `vocabulary@0.2` with its layers, and
   `formula@0.2` with `model@0.2`.
2. **Item 1 is the base plan's step 6 of 5.1 for row 1 of 5.3**, which S3 left open on purpose (base spec D9:
   "S3 ends in shadow with the delta report; the switch is one separate commit"). It is one commit and one
   revert.
3. **The switch changes one thing in public.** At one call site, Python's rejection of a soft source carries the
   contract's record, and its message becomes the record's text. No verdict, no identity, no code and no Lean row
   changes. The complete list of changed messages is measured on the gate's corpus and signed by the DRI before
   the commit.
4. **The contract still decides no verdict.** The engine runs only after the legacy validator has rejected, inside
   the handler of that rejection, and can only hand back the same error (edit f, section 3).
5. **Items 2 to 6 are not started by this plan's statement review.** Each needs its own statement spec, because
   its table has to be authored from the authority's code (base plan 5.1, step 1), and each ends with its own
   switch commit.

## 1. Where the work stands (read at `2ee50149`, not run)

| Fact | Source |
|---|---|
| S0 to S3 are merged. The pilot contract `soft-norms@0` is at revision 3 with `"status": "shadow"` | `ve/wire_contract/soft-norms@0.json:3–5`, `contracts.lock` |
| The Python engine has `run` and `overlay`; the pilot's hooks, classifiers and adapter are in `ve/softnorms_contract.py`. No other module of `ve/` imports either | `ve/wire_contract/engine.py:383, 501`; `tests/test_softnorms_contract.py:228` |
| `VEError` has the attribute `diagnostic`, `None` by default, and `to_dict()` adds the member only when it is set. Nothing sets it | `ve/errors.py:16–30` |
| The Lean engine is `lean/VE/WireContract/`; `ve_diagnose` prints `fault` with the record, or `clean`. The optional theorems were added: eight `#print axioms` lines are in `VE/Audit.lean`, so the exception of C4 was used in S1b | `Engine.lean:453–534`; `VE/Audit.lean:123, 2974–2981` |
| The continuation gate is met: 8,576 cases (tier 0 165, tier A 4,280, tier B 200, replayed 3,917, legacy differences 14), no mismatch, residual 0 and deferred 0 in both languages, coverage met, feasibility 51 of 67, S3-pre closed | `conformance/wire-contract/soft-norms@0-gate.json`; base spec section 18; `manage-agents/wire3-loop.final.md` |
| The corpus-completeness test has three tests: every input of the contract and soft tests, every source of the soft conformance module and every soft fixture is in the gate's corpus | `tests/test_wire_gate_corpus.py` |
| The gate counts 303 cases whose contract text differs from Python's legacy text, on checks that are not inherited. The stored delta report was made from a sample of 2,000 cases and an earlier gate (it states 6,007 cases); it names 4.1c, 6.5a and 6.11 and lists no public change | `soft-norms@0-gate.json:97`; `soft-norms@0-delta.json` |
| The two legacy validators agree on every verdict of the corpus. On three of the 14 legacy-difference inputs their codes differ: `speech-acts@0` added to the profiles (two inputs), and the `unspecified` default under `norm-defaults@0` | `conformance/wire-contract/s3-pre.md`; `soft-norms@0-delta.json:38–72` |
| The pilot has no include, so no record of it has an `inner_path` | base spec R5 |

## 2. Item 1: `soft-norms@0` becomes public

The statement spec fixes every detail; this section is the plan-level summary.

- **Before the switch, S4-pre (blocks the switch).** The three inputs on which the legacy validators' codes differ
  are run to ground, as S3-pre was. A changed code is a recorded product decision, implemented in Python first
  (SEMANTICS-MIGRATION-PLAN 2.3) and outside this plan's licence: it is one separate commit in Python's soft
  table, with its own record `conformance/wire-contract/s4-pre.md`. The switch needs the gate's
  `legacy_code_differences` empty (statement spec 2.8).
- **The measured delta.** The gate computes, for every corpus case that Python's legacy validator rejects, the
  record the overlay would report, and lists every case whose message or code would change, grouped by check. The
  DRI signs the list check by check (`conformance/wire-contract/soft-norms@0-switch.json`), with the release note.
  This is step 5 of base plan 5.1.
- **The switch commit** (step 6): the contract's `status` becomes `public` and its revision 4; one function,
  `ve.softnorms_contract.public_rejection`, and one call site in `ve/soft_route.py` are added; generated files,
  the lock and the reports are regenerated. The legacy validators are not edited.
- **What may change, for this profile** (base plan 5.3, row 1): Python's message on the checks of the signed list.
  From reading, those are 4.1c, 6.5a, 6.6, 6.11, 2.7a and 2.8c on a name that is not a string, and 3.2 on a
  profile outside the Lean route's registry (statement spec section 6). Lean's route rows do not change; Rust has
  no soft validation and no column.
- **What row 1 asks to delete.** Step 6 also deletes "the unit's test tolerance" and "the spec's known-limitation
  paragraph". Row 1 names no tolerance (its last column is a check that S3 added), and soft-norms.md has no
  known-limitation paragraph on diagnostics. Both deletions are empty for this unit; that is recorded here rather
  than invented.

## 3. The converged edits, as they bind stage S4

Each row restates one edit of the joint position (Fable's round 3, which Astra's round 3 restates) for S4. The
base plan's text for each edit is unchanged.

| Edit | What it requires of S4 |
|---|---|
| a. "By construction" is limited to table expansion, and to position, code, path and text conditional on equal predicate results; T3 order is test-enforced; raw JSON scanner order is open | "Uniform" after a switch has this meaning only. For `soft-norms@0`: Python's public text is the contract's template text; that it equals Lean's record is constructed only where every predicate reached returns the same result in both, and is tested on the corpus. The order inside the sets 5.7–5.8 and 6.5–6.15 stays test-enforced, and inherited texts stay language-specific. The scanner order belongs to item 3 (`json@0`) and stays open there |
| b. C1 covers identity serialisation; `VEError.to_dict()` may gain `diagnostic` | The member exists since S1a. Item 1 is the first time it is set; nothing else in `to_dict()` changes, and `code` is never written by the switch. The Rust `error` object gains `diagnostic` in item 2 and not before |
| c. C4 allows additions, generated rehashes, and a reviewed append-only `VE/Audit.lean` diff with its rehash in S1b; the lemmas stay optional | The S1b exception was used. In S4 the inventory diff of a commit is additions and generated rehashes only; item 1 has one generated rehash (`WireContract/Tables/SoftNorms.lean`). The statement spec offers three optional Lean statements in a new module; adding them needs the same append-only audit lines. Edit c grants that for S1b only, so this plan applies the same rule to S4 **only if the statement review confirms it** (section 8, question 6); otherwise the statements are dropped and no existing inventory line changes |
| d. C2 and the tolerance removals apply where an implementation supports the unit and completes diagnosis; a deferred outcome carries the contract, revision, deferred check id and legacy text, has no `check`, `code` or `path`, and is never a residual | Python completes diagnosis of the pilot (deferred 0), so it is compared at zero tolerance. The call site consults no Lean process; if the engine ever defers there, the deferred record is reported with the legacy text. From item 2 the Rust engine defers on every soft-norms hook and is counted, not compared |
| e. Run the inherited `norm-defaults@0` difference to ground before S3; fix a reachable verdict difference outside the plan | Closed (`s3-pre.md`). The code differences it left are step S4-pre of this plan, handled the same way: run to ground, fixed outside the plan, before the switch |
| f. Strike `Engine.run` as a route's validation; "contract first" covers diagnostics only | Item 1 puts the first call of the engine into production. It is inside the handler of a rejection that the legacy validator already raised, it hands back the same error object, and on an accepted input the diagnostic modules are not even imported. Items 3 to 6 write contracts for decoders that keep deciding the verdict |
| g. Under a `view`, `path` is the include site; the generator imports `FORBIDDEN`; one switch commit per unit | The pilot has no include, so item 1 publishes no `inner_path`. The generator is unchanged. Item 1 is the first of the per-unit switch commits: one commit, one revert, its own delta report and release note |
| h. After S3 the DRI reviews the gate; if it fails, stop; S4 onward needs a separate decision | The gate is met (section 1). The separate decision is the first sentence of draft 1 (DRI gate met 2026-10-02) and covers stage S4 only. S5 onward needs another |
| Scope: S1c moved to S4 | The Rust engine is item 2. Item 1 has no Rust part |

## 4. Items 2 to 6 (the S4 row of the base plan)

| Item | Content | Effort (base plan) | Needs first |
|---|---|---|---|
| 2 | Rust engine `rust/ve-core/src/contract.rs`, generated `contract_tables.rs`, the engine corpus in three languages | 3 d | a statement spec for the Rust engine: the definitions of wire-contract.md sections 2 and 8.1 apply unchanged; the spec adds the generated module's grammar and the `error` object |
| 3 | `json@0` | 1.5 d | a statement spec; base plan question 7 (scanner order) stays open |
| 4 | `envelope@0.2` and the profile gate | 2 d | a statement spec with the table read from `ve/profiles.py` |
| 5 | `vocabulary@0.2` with `data@0`, `definitions@0`, `time@0`, `documents@1`, `norms@0` declarations | 4 d | a statement spec with the table read from `environment._decode` |
| 6 | `formula@0.2`, `model@0.2` | 3 d | a statement spec with the table read from `_Decoder` |

Each of items 3 to 6 follows base plan 5.1: author, hooks, generate, shadow, delta report, DRI review, switch.
After item 6 the pilot's inherited hooks (2.3, 4.2a, 4.13b, 4.13d, 5.7, 5.8a, 6.10b) can become includes; that is
a new revision of `soft-norms@0` with its own delta report.

## 5. Gates for every commit of S4

The four conservativity gates of base plan 5.2, as the debate amended them:

- **C1.** No diff in a decoder, canonical serialiser, identity serialisation or digest function. For item 1 the
  diff-scope list is in the statement spec (7.1); `ve/softnorms.py`, `ve/errors.py` and every Lean module except
  the generated pilot table are outside it.
- **C2.** Legacy verdicts equal their snapshot; the engine reports a fault exactly when the legacy validator
  rejects, at zero tolerance, where the language completes diagnosis.
- **C3.** Public diagnostics change only as the signed delta lists; the gate fails on a change outside it.
- **C4.** `lake build`, `lean/audit.py`, `frozen.py` and the manifest test pass; the inventory diff is additions
  and generated rehashes (and, only under row c of section 3, the append-only audit lines with their rehash).

And two that the pointer names:

- **The corpus-completeness test is kept.** `tests/test_wire_gate_corpus.py` stays, with its three tests
  unweakened; an input that item 1's new tests submit must be in the gate's corpus like any other.
- **`tools/wire_contract.py --check`** passes in the gate and the hook.

## 6. Steps and effort

| Step | Content | Effort |
|---|---|---|
| S4-pre | the three code-difference inputs run to ground; the product decision; the fix in Python's soft table, outside the wire work | 0.5–1 d |
| S4.1a | the gate measures the public delta over the whole corpus (in shadow); the delta report and the signing file | 1 d |
| S4.1b | DRI review of the delta: signatures and release note | review |
| S4.1c | the switch commit: status, revision 4, `public_rejection`, the call site, regenerated files, tests | 1 d |
| S4.1d | optional: the three Lean statements, in a new module (row c of section 3) | 0.5 d |
| Items 2 to 6 | as section 4 | 13–14 d |

## 7. Risks

| Risk | Mitigation |
|---|---|
| The diagnostic layer changes a verdict | the call is inside the rejection's handler and returns the same error object; a test scans the call site's shape; the gate asserts the raised object's type and code against the legacy validator on every rejected case |
| The engine raises on some input and turns a rejection into a crash | `public_rejection` returns the error unchanged on any exception; the gate requires zero such cases on the corpus |
| A message changes that nobody signed | C3: the gate fails on a measured change whose check has no signature, and on a signature with no measured change |
| The corpus misses an input class, so the signed list is incomplete in the field | the corpus-completeness test is kept; the claim is "complete on the corpus", stated as such (section 8, question 7) |
| A caller matches on the old message text | `str(error)` changes with the message; the full suite and the conformance reports run in the switch commit, and every changed expectation is listed in it |
| The same fault reads differently through two entry points | recorded: only the soft route's admission is switched (section 8, question 3) |

## 8. Open questions

1. **No debate was held on S4.** The debate files are the base plan's. The statement review is the first review
   of anything specific to S4, and it should read section 3 as well as the statement spec.
2. **What "stage S4" covers.** The pointer describes one switch; the base plan's S4 row lists the Rust engine and
   four base contracts and no switch of the pilot. This draft reconciles them by order: the pilot's switch first
   (it is the pending step of row 1 and the only part that can be stated exactly today), the row's content after.
   If the DRI meant the row first, item 1 moves behind item 6 unchanged.
3. **One entry point or all of them.** Item 1 switches the soft route's admission only. `ve document check`,
   the rights route, the English front ends and `SoftEnvironment` alone keep today's messages until their own
   rows (13, 10) or a later item. Until then the same fault can read differently through two entry points; today
   it reads the same. The alternative is one call site per entry point in item 1, each with its own delta.
4. **Switching before the base contracts exist.** The pilot's inherited checks keep language-specific text, and
   turning them into includes after item 6 is a second delta for the same unit. The alternative is to switch the
   pilot after item 6, once. This draft switches now: the switch machinery is exercised on the smallest unit.
5. **Code differences.** This draft requires them fixed in Python first (S4-pre). The alternative is to sign them:
   the public error would then carry a `code` that differs from `diagnostic.code` on those inputs.
6. **Does edit c extend to S4?** It names S1b. If the review reads it narrowly, the Lean statements of item 1 are
   dropped; nothing else depends on them.
7. **"Complete" means complete on the corpus.** An input outside the gate's corpus can show a message change that
   no list contains. The corpus test bounds this for inputs the tests know; it does not bound it for all inputs.
8. **Lean's public rows never switch.** They are frozen. Where Lean's route text differs from the contract's
   (a name that is not a string and is longer than 80 bytes in compact JSON), a consumer gets the contract's text
   from `ve_diagnose` and Lean's own from the route. Whether a Python caller that relays a Lean row should attach
   Lean's record is not decided; no such call is added here.
9. **Items 2 to 6 have no statement specs yet**, and their effort figures are the base plan's, made before any
   contract existed.

## 9. Debate response table (draft 2)

Source: `manage-agents/debates/design-wire-s4/{fable,astra}.md`, a copy of the base plan's debate. Verdict there:
**BUILD (exact edits): S0 to S3 only, S1c moved to S4**; S4 onward by a separate decision.

| Debate edit | Change in this draft |
|---|---|
| a | section 3, row a; statement spec 2.9 |
| b | section 3, row b; section 5, C1; statement spec 2.3 and 4.2 |
| c | section 3, row c; section 5, C4; section 8, question 6; statement spec 5.2 and 5.4 |
| d | section 3, row d; section 5, C2; statement spec 2.3 (the deferred record at the call site) |
| e | section 3, row e; section 2 and section 6, step S4-pre; statement spec 2.8 |
| f | section 0, item 4; section 3, row f; statement spec 2.4 |
| g | section 3, row g; section 2 (one commit, one revert, delta report, release note) |
| h | section 3, row h; section 1 (the gate's numbers) |
| Scope: S1c moved to S4 | section 4, item 2 |
