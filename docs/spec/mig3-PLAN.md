# Migration stage 3: shadow mode (PLAN)

**Status:** plan only, draft 3, 2026-10-03, branch `design/mig3` from `main` at `a093a14d`. No code or proofs
change with this document. Draft 3 applies the statement review of the statement spec and of this plan
(`manage-agents/debates/mig3-spec/`, Astra + Fable, three rounds; both verdicts FIX; the DRI ruling of
2026-10-03 applies the union of both reviewers' corrections with Astra's three round-3 refinements). The
statement spec's section 13 lists each correction; section 9 below lists what changed in this plan. Draft 1
(`eb96d5ed`) was a pointer of one paragraph:

> Item 1 of THIS plan is Stage 3 (shadow mode) of docs/spec/SEMANTICS-MIGRATION-PLAN.md: run every class-A
> operation under both authorities on real traffic (suite, use cases, pilots, web app) and record every
> difference; the 14-consecutive-clean-days gate and its measurement as the plan states. Gate 2 is met
> (docs/spec/stage2-progress.md). Inputs: docs/TRUST-MAP.md on branch docs/trust-map (24 of 26 operations still
> default to Python). Apply that plan's Stage 3 section exactly; honest open questions.

Draft 2 wrote the plan out and changed nothing of the pointer's intent; draft 3 changes nothing of it either.
[SEMANTICS-MIGRATION-PLAN.md](SEMANTICS-MIGRATION-PLAN.md), revision 3, is the **base plan**. The item-1
statement spec is [mig3.md](mig3.md) (the **statement spec**), now draft 2; its statement review is done, and
both reviewers verify the corrective diff before the first build step (section 6, M3.0b).

**What the debate files are.** The pipeline step asked for "the converged edits in
`manage-agents/debates/design-mig3/` (final joint position in fable.md/astra.md)". That directory does not
exist. No design debate on this stage was started, and, unlike for
[wire-contract-S4-PLAN.md](wire-contract-S4-PLAN.md), no copy of the base plan's debate was put there. So there
were no converged design edits to apply, and this draft invents none. The design debate that does exist is the
base plan's: `manage-agents/debates/semantics-migration/{fable,astra}.md`, CONVERGED after round 3, applied in
revision 3 of the base plan (its section 8, change log of 2026-09-27). Section 3 restates each of its edits as
it binds Stage 3; no design choice of that debate is reopened or added to. Everything in this plan and in the
statement spec that the base plan does not fix is marked as a choice of this draft (statement spec, section 12)
and went to the statement review (`manage-agents/debates/mig3-spec/`), the first review of this stage; its
corrections are applied in statement spec draft 2 and in this draft.

The plan was written from reading the sources at `eb96d5ed`, and `docs/TRUST-MAP.md` in the worktree of branch
`docs/trust-map`. Nothing was built or run, and every `file:line` reference must be re-read at each step.

## 0. Decision in brief

1. **Item 1 is Stage 3 of the base plan, as written there**: about one week of build, then the days in shadow
   until Gate 3. It is the only item this plan starts.
2. **No default changes.** `VE_AUTHORITY` stays `python` by default. The authority `shadow` returns Python's
   result on every call. No file under `lean/` or `rust/` changes, and no Lean statement is added.
3. **The code can record a difference today; it cannot show a clean day.** Nothing is written when the two sides
   agree, nine call sites pass a payload that does not determine the input, calls that an adapter routes to
   Python leave no trace, the shadow path takes `lean or rust` as its candidate and runs it without a pin, an
   error is recorded by code and message only, and there are no corpora runs, no ledger and no gate tool
   (statement spec, section 6). The build closes exactly these.
4. **Gate 3 is the base plan's**: no difference in a zero-tolerance class on any corpus for 14 days in a row, a
   completion rate of 100%, and the count-parity and latency reports attached. The statement spec fixes how each
   word of that is measured.
5. **Stage 4 is not started by this plan.** The switch of the default needs its own statement spec and its own
   decision by the DRI, after Gate 3.

## 1. Where the work stands (read at `eb96d5ed`, not run)

| Fact | Source |
|---|---|
| Gate 2 is met: every class-A operation dispatches its own adapter; the suite passes under `VE_AUTHORITY=lean` (4,472 passed, 6 skipped); parity over 9,384 cells has 0 regressions and 0 different cells | `docs/spec/stage2-progress.md` |
| `VE_AUTHORITY` defaults to `python`. 24 of the 26 operations of the manifest have the authority `python`; 2 are `lean-only` | `ve/backends/dispatch.py:61`; `ve/assurance-manifest.json`; `docs/TRUST-MAP.md` (branch `docs/trust-map`), section 1 |
| 23 dispatch names go through `dispatch.execute`; they cover 19 of the 26 manifest operations | statement spec 2.2 |
| The authority `shadow` exists: it runs Python, then `lean=` or, failing that, `rust=`, with no pin on the candidate, returns Python's result, and appends a record to `VE_SHADOW_LOG` when the two differ. Under `lean`, a call without `lean=` raises and never uses `rust=` | `ve/backends/dispatch.py:150–200`; `tests/test_stage2_dispatch.py:34–72` |
| The classifier is a table over member names. It applies no comparison projection | `ve/backends/dispatch.py:85–139` |
| Stage 2 work that is still open: the scope gaps of 2c (due before Gate 4), the argument record's wording and the four provenance members, batching, Rust parse diagnostics, the manifest's bindings for the service adapters | `docs/spec/stage2-progress.md`, last list |
| The baseline and its projection exist: `checker_build` and `record_id` are dropped | `conformance/baseline-2026-09/`; `tests/probe_matrix.py:146–153` |
| The two checker binaries are pinned by hash | `lean/checkers.lock` (keys `ve_service`, `rust_jsonl`) |
| The trust map's first candidate to shrink the trusted base is to make Lean the default authority; it calls that configuration and process work | `docs/TRUST-MAP.md`, section 7, item 1 |

## 2. Item 1: Stage 3

The statement spec fixes every detail; this section is the plan-level summary.

- **A shadow call.** At the authority `shadow`, each call of a class-A operation runs Python and then the
  function passed as `lean=`, the adapter that would answer under Lean authority, run at that authority, and
  returns Python's object or raises Python's exception. A call without `lean=` has no candidate and is logged as
  unavailable. Nothing in the comparison or the recording can change the result (statement spec 2.2, 2.3).
- **The comparison.** The two results are compared after the base plan's comparison projection; an error is
  compared as its whole public record, and a wording counts as equal only through a reviewed entry at an
  eligible location. A difference falls into the base plan's ten classes: eight at zero tolerance, two recorded
  with bounds reported (statement spec 2.4, 2.5).
- **What is written.** A record for each difference, for each call that got no answer, and for each call of a
  statement-layer route that has no Python implementation ("`python: none`"). A tally for every call, kept by
  every worker from before its first shadow call to a final write at exit, so that agreement, completion, count
  parity and latency can be stated and nothing missing passes for agreement (statement spec 2.6, 2.7).
- **The corpora** are the base plan's list, in a registry with floors taken from calibration runs that are not
  registered. A nightly runs all of them at one commit of `main`; a merge runs the suite (statement spec 2.8 to
  2.10).
- **A clean day** is a UTC day on which every corpus has a complete run in its nightly, every class-A
  operation was compared, every commit since the previous nightly that needs a merge run has a complete one,
  and no registered run has a zero-tolerance record, a call that Python answered and the backend did not, or a
  recorder fault. A day is certified only after it has ended and every registered run of it has finished
  (statement spec 2.10).
- **Triage.** Every such record is a finding with one cause. The base plan's rule is kept word for word: a
  Python deviant is fixed with a new conformance case; a Lean glue or decoder deviant with statement review; a
  spec ambiguity gets a spec note and a fixture (statement spec 2.11).
- **The count** of clean days in a row goes back to zero at the merge of a fix of adapter, glue, decoder or
  Rust code, however the fault was found. Every other change under `ve/` or to the candidate surface is classed
  by the DRI, file by file, with a reason, before the gate can be met (statement spec 2.12).
- **Gate 3** is met on a day when the count is at least 14, every finding is closed and the reports are
  attached. It allows Stage 4 to be specified; it switches nothing (statement spec, section 9).

## 3. The base plan's converged edits, as they bind Stage 3

Each row restates one edit of the base plan's debate (Astra's round 3 with Fable's rounds 2 and 3) for Stage 3.
The base plan's text for each is unchanged.

| Edit of the base plan's debate | What it requires of Stage 3 |
|---|---|
| Shadow compares the exact compatibility projection, not leaf sets: named leaves in declaration order, distinct aliases, provenance, supporting-edge identities and order, Background (Astra round 3, item 1) | Any difference under a composition member is the class `composition`, at zero tolerance. The comparison is by position, so a reordered or collapsed list is a difference (statement spec 2.5) |
| A discovered difference needs an implementation correction or the explicit product-change process; a "by-design" mismatch is not exempt (Astra round 3, item 2; Fable round 3, point 4) | No finding is closed as "by design". A `spec` finding that changes what a supported input returns goes through base plan 2.3 (statement spec 2.11) |
| Legacy public charging and counters are preserved by the executing backend, at zero shadow tolerance; internal counters are separate (Astra round 3, item 3) | `evaluations`, `steps` and `models_checked` are the class `count-value`; a different `status` under the same budget is `budget-outcome`; the gate report attaches count parity (statement spec 2.5, 2.13) |
| The comparison's exclusions are listed: the build id, the record ids derived from it, reviewed wording; artefact identities stay exact (Fable round 2 (e); Astra round 2, item 5) | The comparison projection drops `checker_build` and `record_id` and nothing else; a wording counts as equal only through a reviewed entry of the wording map (statement spec 2.4) |
| Shadow logs `python: none` for Lean-only operations, outside the divergence classes (Fable round 2 (f)) | The record kind `lean-only`: no comparison, no class, not part of a clean day (statement spec 2.6) |
| The `model` mode reproduces Python's normalisation; a mismatch is a Lean glue bug, and shadow checks identity at zero tolerance (Fable round 2 (f)) | A different `model_id` is the class `identity`; its cause is `glue` (statement spec 2.5, 2.11) |
| Full baseline and API compatibility belong to Gate 2 and shadow; end-to-end latency to Gate 4 (Astra round 2, item 5) | Stage 3 attaches a latency report and sets no latency threshold (statement spec, section 9) |

The oracle labels of the base plan's stage 5 (`lean+rust`, `lean+pinned-python`, `reviewed`) bind fixtures made
after the deletion. A conformance case added in Stage 3 for a Python fix is made while Python is still there, so
no label is needed for it yet.

## 4. What this plan does not start

| Later work | Needs first |
|---|---|
| Stage 4: the default becomes `lean`; assurance narrowed per operation; packaging; rollback rehearsal | Gate 3; a statement spec of its own; a decision by the DRI. The statement spec's question 8 (which data the performance gates use) and limit 12 (a change after the gate's commit) are for that spec |
| Stage 5: deletion of the Python semantics | Gate 4 |
| The open Stage 2 work (2c scope gaps, batching, record wording, Rust parse diagnostics, manifest bindings) | not part of item 1. Its order against the 14 days is the DRI's (section 8, question 2) |

## 5. Gates for every build commit

Item 1's build changes Python only. For each of its commits (statement spec 7.2):

- **B1.** The baseline replays byte for byte at the default authority.
- **B2.** `tools/stage2_parity.py --authority lean`: 0 regressions, 0 different cells.
- **B3.** The full suite passes at the default authority and under `VE_AUTHORITY=lean`.
- **B4.** `lake build`, `lean/audit.py` and `VE/Route/frozen.py` pass, with no difference under `lean/`.
- **B5.** `tools/inventory_lint.py` and the Python layer ledger pass.

And the default stays: with no variable set the authority is `python`, and the manifest's authorities are
unchanged (fixture Z5).

## 6. Steps and effort

| Step | Content | Effort |
|---|---|---|
| M3.0 | statement review of the statement spec and this plan (Astra + Fable): done, `manage-agents/debates/mig3-spec/`, verdict FIX, the DRI ruling applied in statement spec draft 2 and this draft | review (done) |
| M3.0b | both reviewers verify the corrective diff (statement spec draft 1 to draft 2, this plan draft 2 to draft 3) by diff, with no new round; M3.1 starts after that | review |
| M3.1 | the recorder: the guarded shadow call with the candidate `lean=` only under `pinned("lean")`, the projection, the `to_dict()` error record, the classes, the record kinds, registration and final tallies (`ve/backends/dispatch.py`); fixtures S (S16, S20 among them), C (C13 among them) and most of L | 2 d |
| M3.2 | the call sites: payloads that determine the input (nine sites), `note_uncompared` (14 branches), the `lean-only` record, one per case; fixtures L2, L9, L10, L12, L13, S18 | 1–2 d |
| M3.3 | the corpora: the registry and `tools/shadow_run.py`; one calibration run of each corpus (manual, not registered, complete in every condition but the floors); the calibration commit, reviewed, that writes each corpus's command, floors and calibration run into the registry. No run is registered before it | 1–2 d |
| M3.4 | the days: `tools/shadow_gate.py` (`day` only for a final day, `--check` with the wording, `written` and classing checks), the ledger, the triage and classing files; fixtures G, T, L14 to L16 | 1–2 d |
| M3.5 | the suite at `shadow` for the whole run (Z1); the merge train starts merge runs; the nightly is scheduled; the DRI's decisions on questions 2, 3 and 6 (section 8) are recorded | 1 d |
| M3.6 | the first nightly. From here: one nightly each day, triage of each finding, and the DRI's class, file by file, for each change under `ve/` or to the candidate surface | 14 days at the least; about 1 d of triage a week (base plan, section 6) |
| M3.7 | the Gate 3 report in `docs/spec/stage3-progress.md`; the DRI's review; Astra and Fable read it | review |

The base plan gives Stage 3 "1 week to build, then 14 consecutive clean days". M3.1 to M3.5 are that week. The
Lean worker of the build has no work item beyond B4.

## 7. Risks

| Risk | Mitigation |
|---|---|
| The recorder changes a result | V1 of the statement spec: the comparison and the write are guarded, and the call returns Python's object. Z1 runs the whole suite at `shadow`; B1 and B2 hold on every build commit |
| A day looks clean because nothing ran | a clean day needs a complete run of every corpus, floors on cases and on compared calls, and a compared call of every operation |
| A difference is lost | a record is written before its call returns; a record file that does not parse makes its run incomplete; a recorder fault costs the day |
| A worker's evidence is missing and the rest looks fine | every worker registers before its first shadow call and must leave a final tally that matches its records; a worker killed before that, or one whose writes all fail, makes its run incomplete, however far the other workers exceed the floors |
| A day is certified before its runs end | the ledger entry is written only after the day has ended and every registered run of it has finished; `--check` rejects an entry written earlier |
| A wording entry or the projection hides a real difference | the projection drops two member names and nothing else; a wording entry matches two exact strings at one structural path of one operation, at a diagnostic-text or graph-proof location only, and is added only by a reviewed commit; `--check` rejects every other location |
| The count survives a change to the code it is about | every commit that changes a file under `ve/`, the glue, a decoder or the pinned binaries is found from the history and must be a restart or carry the DRI's class and reason for each changed file; one without blocks the gate. A fix of candidate code restarts wherever it lives and however it was found |
| Timeouts under load cost days | recorded as findings with the cause `operational`; the choice of limit and of worker count is section 8, question 3 |
| The 14 days never complete while expansion work changes the glue | section 8, questions 2 and 10: the DRI orders the work |
| Agreement is taken for correctness | statement spec, limit 1: shadow shows that two programs agree on the corpora and proves nothing |

## 8. Open questions

The statement spec's section 12 has the full list with its reasons. The ones the DRI has to decide. By the
ruling of the statement review, questions 2, 3 and 6 are decided before the first nightly (M3.5), not before the
build:

1. **No design debate was held on this stage.** The statement review has been held and applied. If a design
   debate was meant to come before it, this draft and the statement spec are its input.
2. **The order of the open Stage 2 work against the 14 days** (before the first nightly). Each piece changes
   adapters or glue. Landed inside the 14 days, each needs the DRI's class: a restart loses the days counted,
   and no restart means a newly routed input has fewer than 14 days of comparison at the gate. This draft
   recommends landing first what is meant to land.
3. **Timeouts** (before the first nightly). The adapters use the service's interactive limit of 5 seconds. Stage
   2 saw two timeouts in one suite run at 14 workers. As specified, one such call costs a day.
4. **A day on which the machine was down** ends the run of days, as specified. The other reading does not count
   that day either way.
5. **"Real traffic" and the web app.** The base plan's corpus is the web app's API tests. No call from a person
   using a deployed program is in any corpus. Running a deployed web app at `shadow` would put people's inputs
   into the records and needs its own decision.
6. **Merge runs: whether to amend the base plan** (before the first nightly). As specified, a merge runs the
   suite at `shadow`, and a commit that needs a merge run and has no complete one leaves its day not covered,
   which is what the base plan's "CI runs shadow on every merge" requires; the merge itself is never blocked.
   The cost on the merge train is not measured. If it is too high, the way out is an explicit, recorded
   amendment of the base plan, not a choice of this stage.
7. **Calls that are not compared.** Scope gaps are answered by Python alone and are outside the gate. Should
   Gate 3 wait until stage 2c has closed them? The base plan puts 2c at Gate 4.
8. **Rust.** The base plan's restart rule names adapter and glue fixes. As specified, a Rust fix restarts too,
   because Rust answers inside the candidate for evaluation and search.
9. **Expansion and consolidation work.** A new statement layer has so far changed the service glue, and the
   consolidation chain will change the route runners; both change the pinned service binary. Each such merge
   needs the DRI's class during the 14 days.
10. **Which operations are Lean-only.** The manifest names two, and neither has a call site. The statement-layer
    routes are not manifest operations. The statement spec takes the trust map's list for the `python: none`
    records; the manifest is not corrected here.
11. **Not read, not measured:** the corpus commands, the floors, the size of the records, the length of a
    nightly, and whether the suite passes with `shadow` set for the whole run.

## 9. Debate response table (draft 3)

There is no design debate on this stage to respond to (status paragraph). The base plan's debate is answered
in the base plan's own section 8; section 3 above restates its edits for Stage 3 and changes none of them. The
statement review is answered here and in the statement spec's section 13.

| Source | Change in this draft |
|---|---|
| `manage-agents/debates/design-mig3/` | does not exist; nothing applied |
| the pointer of draft 1 | written out as sections 0 to 8 (draft 2); its "real traffic" is read as the base plan's corpora (section 8, question 5) |
| the base plan's Stage 3, Gate 3, section 4 (completion rate, budget boundaries) and section 5 (comparison projection) | applied as written; each operational choice the base plan leaves open is listed in the statement spec, section 12 (R1 to R22) |
| `manage-agents/debates/mig3-spec/` (statement review; DRI ruling of 2026-10-03: the union of both reviewers' corrections with Astra's three round-3 refinements) | applied in full in statement spec draft 2 (its section 13, 17 rows). In this plan: the status paragraphs; section 0 item 3 (what the code cannot do today); section 1 (the shadow path's candidate); section 2 (the candidate is `lean=` run at `lean`, the error record and the wording allowlist, final tallies, calibration floors, merge coverage and day finality in a clean day, the restart and classing rule); section 4 (limit renumbered); section 6 (M3.0 done, M3.0b the diff check, M3.1 to M3.6 amended); section 7 (two risks added, three amended); section 8 (questions 1, 2, 3 and 6). No design choice is added |
