# Semantics migration, stage 3: shadow mode (statement specification)

> Status: statement specification, draft 2 (2026-10-03), branch `design/mig3` from `main` at `a093a14d`. This is
> the item-1 statement spec of [mig3-PLAN.md](mig3-PLAN.md) draft 3 (the **plan**). Item 1 is Stage 3 of
> [SEMANTICS-MIGRATION-PLAN.md](SEMANTICS-MIGRATION-PLAN.md), revision 3 (the **base plan**): its section "Stage 3:
> shadow mode" with Gate 3, and the parts of its sections 4 and 5 that Stage 3 names. **No design debate was held
> on this stage.** The directory `manage-agents/debates/design-mig3/` that the pipeline step names does not exist,
> so there were no converged edits to apply and none is invented (plan, status paragraph). The only converged
> debate on the design is the base plan's (`manage-agents/debates/semantics-migration/{fable,astra}.md`, CONVERGED
> after round 3), and its edits are already in revision 3. **The statement review of draft 1 was held**
> (`manage-agents/debates/mig3-spec/`, Astra + Fable, three rounds, 2026-10-03). Both reviewers' verdict was FIX;
> the DRI's ruling (`DRI-RULING.md` there) applies the union of both reviewers' corrections with Astra's three
> round-3 refinements. Draft 2 applies that ruling and nothing else; section 13 lists each correction and where it
> landed. Both reviewers verify the corrective diff before M3.1 starts (plan, section 6). Section 12 lists the
> choices the base plan does not fix and the open questions. Fixtures are implementation obligations, not claims
> of completed tests. Nothing was built or run for this draft. Every `file:line` reference was read at `eb96d5ed`
> and must be re-read at each step; every number quoted from another document is that document's. Nothing here
> changes a verdict, an identity, a code, a frozen contract, a default authority, a Lean file or a theorem
> statement.

## 0. Scope, one paragraph

Gate 2 is met: every class-A operation has an adapter, and the suite passes under `VE_AUTHORITY=lean`
([stage2-progress.md](stage2-progress.md)). Python is still the default authority for 24 of the 26 operations of
the assurance manifest (`docs/TRUST-MAP.md` on branch `docs/trust-map`, section 1). Stage 3 changes no default. It
runs the base plan's corpora under the authority `shadow`: each call of a class-A operation runs Python and the
adapter that would answer under Lean authority, returns Python's result, and writes a record when the two differ.
A day is clean when every corpus ran, no compared call differed in a zero-tolerance class, and no call that
Python answered got no answer from the backend. Gate 3 is 14 clean days in a row with no restart event among
them. This specification fixes what a shadow call does, how two results are compared and classed, what is
written, what a run, a day and the count of days are, how a finding is triaged, and what the Gate 3 report
states. The switch of the default (Stage 4) is not specified here.

In this specification: the decisions (1), the definitions (2), the English, one reading each (3), the diagnostics
(4), the Lean statements relied on (5), where the code stands against the base plan (6), the files and gates of
the build (7), the acceptance fixtures (8), Gate 3 (9), limits (10), the statement review checklist (11), the
choices this specification resolves with the open questions (12), and the changes of draft 2 (13).

## 1. Decisions

| # | Decision | Where |
|---|---|---|
| D1 | A shadow call returns the object Python returns, or raises the exception Python raises. Nothing in the comparison or the recording can change that | 2.3 |
| D2 | The candidate of a shadow call is the function passed as `lean=`: the adapter that answers the operation under `VE_AUTHORITY=lean`, run at that authority. A call without `lean=` has no candidate, whatever `rust=` it passes. Where the adapter uses Rust, Rust's part is inside it | 2.2, 2.3 |
| D3 | Two results are compared after the base plan's comparison projection: `checker_build` and `record_id` are dropped, a mapped wording at an eligible location counts as equal, and nothing else is excluded. An error is compared as its whole public record | 2.4 |
| D4 | There are ten classes, the base plan's: eight at zero tolerance, two recorded with bounds reported | 2.5 |
| D5 | There are four kinds of record: `divergence`, `unavailable`, `lean-only` and `recorder-fault`. A `lean-only` record is how "`python: none`" is logged | 2.6 |
| D6 | A call that an adapter routes to Python without a candidate is counted, with its reason, and reported. It is outside what the gate shows | 2.7 |
| D7 | A run is one corpus at one commit of `main`, registered before it starts; every worker process registers before its first shadow call and leaves a finalized tally. The corpora are the base plan's list, in a registry with floors from calibration runs | 2.7, 2.8, 2.9 |
| D8 | A day is clean when every corpus has a complete run in its nightly, every class-A operation was compared, every commit since the previous nightly that needs a merge run has one, and no registered run of the day has a zero-tolerance record, a completion failure or a recorder fault. A day is certified only after it has ended and every registered run of it has finished | 2.10 |
| D9 | Every zero-tolerance record, every unavailable call and every recorder fault is a finding with one cause. The causes `python`, `glue` and `spec` carry the base plan's triage rule word for word | 2.11 |
| D10 | The count of clean days goes back to zero at the merge of a fix of adapter, glue, decoder or Rust code, however the fault was found. Every other change under `ve/` or to the candidate surface is classed by the DRI, file by file, with a reason, before the gate can be met | 2.12 |
| D11 | Gate 3 is a statement about one day and that day's nightly commit | 2.12, 9 |
| D12 | No file under `lean/` or `rust/` changes, and no Lean statement is added | 5, 7 |

## 2. Definitions

### 2.1 Terms carried over

| Term | Meaning (source) |
|---|---|
| authority | the value that `authority_for(op)` returns for an operation: `python`, `shadow`, `lean` or `rust-experimental`, from `VE_AUTHORITY`, `VE_AUTHORITY_OVERRIDES` and a pin (`ve/backends/dispatch.py:57–70`). The default is `python` (line 61) |
| class-A operation | an operation whose verdict the base plan moves behind an adapter (base plan 1.4). In this file it is named by its **dispatch name**: the first argument of a call of `dispatch.execute` (2.2) |
| adapter | a function with the signature and result type of the Python function, which answers from Lean or Rust (base plan, stage 2a): the code of `ve/backends/` and the functions passed to `execute` as `lean=` and `rust=` |
| glue | the Lean service modes: `lean/VE/Service/` and `lean/Serve.lean` (base plan 2.1) |
| decoder | a Lean JSON or wire decoder listed under `lean_decoders` in `ve/assurance-manifest.json` |
| outcome class | one of the manifest's five: verdict, unknown, rejection, budget, operational (`ve/assurance-manifest.json:5–11`) |
| `CheckerUnavailable` | the operational code: no answer was obtained. It is never a verdict and never `ResourceLimit` (base plan, stage 1) |
| baseline | `conformance/baseline-2026-09/python.json`, Python's output for every matrix cell (base plan, stage 0) |
| scope gap | an input that an adapter routes to the retained Python statically (stage2-progress.md, "Scope gaps that remain") |
| DRI | the person who decides for this work; today the orchestrator |

"Shadow" in this file always means the authority `shadow`. It has nothing to do with the status `shadow` of a
wire contract ([wire-contract.md](wire-contract.md) 2.2).

### 2.2 The operations

The 23 dispatch names, as read from the calls of `execute` in `ve/`:

| Dispatch name | Manifest operation | Dispatched at |
|---|---|---|
| `parse` | `parse` | `ve/parser.py:384` |
| `typing` | `typing` | `ve/ast.py:364, 396` |
| `environment_validation` | `environment` | `ve/environment.py:312` |
| `model_validation` | `model`; `definitions.elaborate` | `ve/model.py:98`; `ve/background.py:267` |
| `evaluate` | `evaluate` | `ve/evaluate.py:275` |
| `countermodel_check` | `countermodel.check` | `ve/search.py:229` |
| `countermodel_search` | `countermodel.search` | `ve/search.py:737` |
| `distinguishing_model` | `countermodel.search` | `ve/search.py:901` |
| `certificate_replay` | `certificate.check` | `ve/entailment.py:690` |
| `background` | `definitions.elaborate` | `ve/background.py:235` |
| `dependency_order` | `definitions.elaborate` | `ve/background.py:332` |
| `definitions_elaboration` | `definitions.elaborate` | `ve/definitions.py:108` |
| `norms_elaborate` | `norms.elaborate` | `ve/norms.py:350, 374` |
| `norms_conflict` | `norms.conflict` | `ve/norms.py:608` |
| `norms_certificate` | `norms.certificate` | `ve/norms.py:510` |
| `norms_admission` | `admission` | `ve/norm_admission.py:48` |
| `admission` | `admission` | `ve/admission.py:475` |
| `label` | `label` | `ve/admission.py:125` |
| `readings` | `readings` | `ve/readings.py:472–479` |
| `graph` | `graph.compose` | `ve/argument.py:581` |
| `bundle` | `bundle.check` | `ve/bundle.py:148` |
| `premise_status` | `premise-status` | `ve/vacuity.py:28` |
| `compare` | `compare` | `ve/equivalence.py:192` |

These cover 19 of the manifest's 26 operations. The other seven:

| Manifest operation | Authority | In shadow |
|---|---|---|
| `identity` | python | no adapter of its own. An identity is compared as a member of another operation's result (class `identity`) |
| `check`, `document.check`, `reference.validate` | python | no adapter of their own. Each is a Python rule over operations of the table above, and those are compared |
| `english.admission` | python | not compared. The English surface stays Python by the base plan's decision (its 2.3). The ASTs it produces are typed through `typing` |
| `soft.elaborate`, `wire.diagnose` | lean-only | nothing to compare, and nothing to log: neither has a call site in `ve` (`lean_call_sites` is empty for both, `ve/assurance-manifest.json:661, 989`) |

The operations that in fact have no Python implementation are the **statement-layer routes**: `ve` hands their
cases to a Lean route executable and answers nothing itself. TRUST-MAP.md (sections 1 and 8.1) names them: norm
defaults, soft norms, rights, risk, alternatives, reports, readings (`readings@1`), discourse (`@2`) and
quantity. The manifest does not list them as operations of their own. A call of one of them at the authority
`shadow` is a **Lean-only call** and is logged as a `lean-only` record (2.6). Six of the functions through which
`ve` makes these calls are in `ve/backends/lean.py` (`run_soft_case`, `run_alternatives_case`,
`run_discourse_case`, `run_reports_case`, `run_norm_defaults_cases`, `run_readings_cases`; lines 33–255). The
last two take a list of cases and make one call to Lean for the list. The build fixes the full list (section 12,
question 13).

The **candidate** of a shadow call is the function passed as `lean=`, and only that. It is the function
`execute` calls when the authority is `lean`; without `lean=`, `execute` raises `CheckerUnavailable` there and
does not use `rust=` (`dispatch.py:163–166`). So the candidate is the code that would answer after the switch,
and a call without `lean=` has no candidate in shadow either, whatever `rust=` it passes: it is case C of 2.5.
(Today's shadow path takes `lean or rust` as the candidate, `dispatch.py:180`; the build removes that.) Today
every call of the table passes `lean=`.

A candidate is not always an independent implementation. Read at `eb96d5ed`:

- `evaluate`: Rust evaluates; Lean evaluates the same formulas, and a different value is `CheckerUnavailable`.
  When Rust ends in `ResourceLimit`, Rust's result is the answer (`ve/evaluate.py:265–273`).
- `countermodel_search`, `distinguishing_model`: the function passed as `lean=` is the Rust search, whose witness
  goes through `countermodel_check` by way of `_witness_checked`, with no pin of its own (`ve/search.py:711–715,
  737, 901`). Under 2.3 that nested call runs at the authority `lean` because `execute` pins the candidate.
- `premise_status`, `compare`: Python's rule, with its constituents pinned to Lean (`dispatch.composed`).
- `readings`: Python enumerates the choices with its constituents on Lean, and Lean's `readings` mode must
  confirm the verdict. For coupled sets and joint choices the rule stays Python's (`ve/readings.py:467–478`).
- `environment_validation`, `model_validation`, `definitions_elaboration`, `bundle`, `parse`: both decoders run,
  and on an accepted input the candidate returns Python's container when its identity is the one Lean
  recomputed (stage2-progress.md, "Lean decides, Python names").

The candidates of the other operations were not read for this draft; stage2-progress.md's adapter table
describes them.

### 2.3 A shadow call

A **shadow call** is a call `execute(op, payload, python, lean=…, rust=…)` at which `authority_for(op)` is
`shadow`. It does this, in order:

1. Run `python()`. If it returns a value `v`, Python's outcome is *returned(v)*. If it raises an `Exception`
   `e`, Python's outcome is *raised(e)*.
2. Run the candidate inside `pinned("lean")`: `execute` sets the pin itself, so every call of `execute` inside
   the candidate runs at the authority `lean`, whether or not the candidate pins (the search candidates do not,
   2.2). The candidate's outcome is *returned(w)* or *raised(f)*, or *no adapter* when the call passes no
   `lean=`. The candidate runs whatever Python's outcome is.
3. Compare the two outcomes (2.4, 2.5), write a record if one is due (2.6), and add to the tally (2.7).
4. Return `v`, the same object; or raise `e`, the same object.

Four properties follow from this shape. They are tested (8.1, 8.5), not proved:

- **(V1) The outcome is Python's.** An `Exception` that the candidate raises is its outcome and goes no further.
  An `Exception` raised inside step 3 is caught, counted as a recorder fault (2.6), and goes no further.
- **(V2) Without `shadow`, nothing changes.** At the authorities `python`, `lean` and `rust-experimental`,
  `execute` does what it does today: no file is written and no tally is kept.
- **(V3) Other exceptions pass through.** A `BaseException` that is not an `Exception` (`KeyboardInterrupt`,
  `SystemExit`) leaves `execute` from either side, as today.
- **(V4) The candidate does not change Python's result.** The candidate may run Python's structural decoder
  again on the object Python filled (2.2, last item). On every compared call of the baseline corpus, the public
  record (2.4) of the object Python returned is the same before and after the candidate ran.

A shadow call can happen inside the `python` function of another shadow call, when an operation composes others.
It is a shadow call of its own, with its own record and tally. Inside a candidate no shadow call happens:
`execute` runs the candidate under `pinned("lean")` (step 2; `dispatch.py:36–46`; `pinned("shadow")` is
refused), so a constituent the candidate reaches through `execute` is answered by the backend, not compared.

### 2.4 What is compared

The **public record** of a returned value is `_record` of it: `to_dict()` where the value has one, the fields of
a dataclass, and dictionaries, lists and tuples member by member, a tuple as a list (`dispatch.py:73–82`).

The **error record** of a raised exception `e` is `e.to_dict()` where `e` has one: for a `VEError`, `code` and
`message`, with `path`, `span` and `diagnostic` when they are set (`ve/errors.py:22–30`), and `generator` for an
`InvalidModel` (lines 69–73). Otherwise it is `{"code": c, "message": str(e)}`, where `c` is the name of `e`'s
type. That is the record the baseline compares (`tests/probe_matrix.py:137–143`); today's shadow path keeps
`code` and `message` only (`dispatch.py:177–178`), and the build changes that.

The **comparison projection** is applied to both records before they are compared:

1. Every member named `checker_build` or `record_id` is removed, at any depth. This is the function
   `baseline_projection` (`tests/probe_matrix.py:146–153`); shadow and the baseline use one definition of it,
   not two copies.
2. A **mapped wording** counts as equal. The wording map is the file `conformance/shadow/wording.json`, a list
   of entries `{"op", "path", "python", "backend", "reviewed"}`. `path` is a list of member names: a path in the
   sense of 2.5. Where the two records of operation `op` have, at a position whose path is `path`, the string
   `python` on Python's side and the string `backend` on the candidate's side, the two strings count as equal.
   The strings are matched exactly; an entry has no pattern. `reviewed` names the commit or document of the
   review.

An entry's `op` and `path` must name an **eligible location**, and these are the only eligible locations:

- **diagnostic text**: any dispatch name of 2.2, and a path whose last name is `message` or `detail` and that
  passes through no `explanation`, `trace` or composition member (2.5);
- **graph-proof wording**: the dispatch name `graph`, and the path `["proof"]`: the member `proof` at the root of
  the graph record (`ve/argument.py:390, 763`).

`--check` (4.3) rejects an entry at every other location (fixture T3). Among the rejected: a `status`, a `code`,
a `generator`, a count member, an identity member, a `kind` under `explanation`, and a binding identifier
(`local_id` in the `bindings` of an explanation, `ve/evaluate.py:26`). A wording entry can therefore not hide a
verdict, an identity, a code, a count or a structural difference.

The wording map starts as the empty list. An entry is added only in the reviewed commit that changes the wording
(base plan, stage 2a: "changes land in one reviewed commit"; section 5: "explicitly mapped for comparison"). No
other difference is excluded (base plan, section 5).

### 2.5 The classes

The class names are exactly these ten. **Zero tolerance:** `verdict`, `identity`, `diagnostic-code`, `schema`,
`explanation`, `budget-outcome`, `composition`, `count-value`. **Recorded, with bounds reported:**
`diagnostic-message`, `latency`.

The **class set** of a shadow call is defined by cases on the two outcomes.

**Case A: both returned, or both raised.** Let `a` be Python's projected record and `b` the candidate's. Walk
the two from the root, keeping the **path**: the list of member names passed through. A position in a list adds
nothing to the path.

- If `a` and `b` have different types, that is a *shape difference* at the path. The types are dictionary, list,
  string, integer, float, Boolean and null; a Boolean is not an integer.
- If both are dictionaries: different key sets are a shape difference at the path. Each common key is walked,
  with the key added to the path.
- If both are lists: different lengths are a shape difference at the path. The items are walked in pairs, up to
  the shorter length, with the path unchanged.
- Otherwise: equal values, or a mapped wording, are no difference. Unequal values are a *leaf difference* at the
  path; its **key** is the last name of the path, or the empty string at the root.

A shape difference gives `schema`. It also gives `explanation` when the path contains `explanation` or `trace`,
and `composition` when the path contains a composition member.

A leaf difference gives the classes of the first row that applies:

| # | Condition | Classes |
|---|---|---|
| 1 | the path contains `explanation` or `trace` | `explanation` |
| 2 | the path contains a composition member | `composition` |
| 3 | the key is `status` | `verdict` and `budget-outcome` |
| 4 | the key is `valid`, `value`, `values`, `refutes`, `composed` or `verdict` | `verdict`; and also `composition` when the key is `verdict` and the operation is `readings` |
| 5 | the key is an identity member | `identity` |
| 6 | the key is `evaluations`, `steps` or `models_checked` | `count-value` |
| 7 | the key is `code` or `generator` | `diagnostic-code` |
| 8 | the key is `message` or `detail` | `diagnostic-message` |
| 9 | anything else | `schema` |

The **composition members** are `composition`, `assumptions`, `assumption_claim_ids`, `supporting_edge_ids` and
`unresolved_obligations`. The **identity members** are `environment_id`, `source_id`, `meaning_id`, `model_id`,
`claim_id`, `edge_id`, `graph_id`, `report_id` and `document_hash`.

Row 3 is the base plan's `budget-outcome`: "the outcome class Satisfied/Violated/Found/NotFound/Valid/Invalid/
ResourceLimit under the same nominal budget". A different `status` is a different outcome, so it is in both
classes. Row 4's second half is the base plan's "Python's readings verdict versus Lean's" under `composition`.

**Case B: one returned and the other raised**, and neither raised `CheckerUnavailable`. The class set is
`verdict` and `schema`. It also has `budget-outcome` when the raised code is `ResourceLimit`, or when the
returned record is a dictionary whose `status` is `ResourceLimit`.

**Case C: the backend gave no answer.** The candidate's outcome is *no adapter*, or it raised an exception whose
code is `CheckerUnavailable`. There is no class set; the record is of the kind `unavailable` (2.6).

**Case D: Python gave no answer.** Python raised an exception whose code is `CheckerUnavailable`. There is no
class set; the record is of the kind `unavailable`. When C and D both hold, there is one record.

A **compared call** is a shadow call in case A or B. A **zero-tolerance record** is a `divergence` record whose
class list has at least one of the eight zero-tolerance classes.

`latency` is never in a class list, because every call differs in duration. It is recorded for every compared
call, in the tally (2.7). "With bounds reported" means, for `latency`: the report states, for each operation and
each side, the number of calls, the smallest and largest duration, the sum and the histogram. For
`diagnostic-message` it means: the report states the number of records and the number of distinct triples of
operation, Python text and backend text.

### 2.6 Records

A record is one JSON object on one line: UTF-8, keys sorted, no optional white space, a newline at the end. A
value that JSON cannot hold is written as the string `<unserializable T>`, with `T` the name of its type; the
comparison itself uses the values, not this string.

| Member | Value |
|---|---|
| `kind` | `divergence`, `unavailable`, `lean-only` or `recorder-fault` |
| `op` | the dispatch name; for a `lean-only` record, the name of the route executable |
| `input_digest` | the SHA-256, in lowercase hex, of the payload in canonical compact JSON (`dispatch.py:193–194`); `null` when the payload cannot be written |
| `python` | Python's public record or error record, before the projection; `null` in a `lean-only` record |
| `lean` | the candidate's record, before the projection; for *no adapter*, the error record of the table below |
| `rust` | `null` in every record of this stage: a call with `rust=` alone has no candidate (2.2). The member is kept because the base plan's record has it |
| `class` | the class set, as a sorted list; the empty list in every kind but `divergence` |
| `python_ms`, `backend_ms` | the time of step 1 and of step 2, in milliseconds, by the monotonic clock; `null` for a side that did not run |
| `run` | the value of `VE_SHADOW_RUN`, or `null` |
| `test` | the value of `PYTEST_CURRENT_TEST`, or `null` |
| `input` | the payload itself when its canonical JSON has at most 65,536 bytes; otherwise `null` |
| `sides` | in an `unavailable` record only: the sorted list of the sides that gave no answer, out of `backend` and `python` |
| `error` | in a `recorder-fault` record only: the type name and the text of the exception |

The base plan's record is `{op, input_digest, python, lean, rust, class}`. The other members are additions of
this draft (section 12, R1 and R11).

**Requirement (I).** The payload of a class-A call determines the call's input: two calls of one operation with
different inputs have different payloads. Nine call sites do not meet it today (section 6, row 3).

When each kind is written:

| Kind | Written when | Notes |
|---|---|---|
| `divergence` | case A or B, and the class set is not empty | |
| `unavailable` | case C or D | for *no adapter*, `lean` is `{"code": "CheckerUnavailable", "message": "no adapter for <op>"}`, as today (`dispatch.py:183`) |
| `lean-only` | a Lean-only call (2.2) is made while the variable `VE_AUTHORITY` is `shadow` | one record for each case: a function that hands a list of cases to Lean in one call (`run_norm_defaults_cases`, `run_readings_cases`) writes one record per case of the list, each with that case's `input_digest` and Lean's row for it. `python` is `null`, which is how `none` is written in JSON; `lean` is what Lean answered; the call returns or raises as it does today. It is not a comparison and belongs to no class |
| `recorder-fault` | step 3 of 2.3 raised an `Exception` | written if it can be; counted in the tally in any case |

A **completion failure** is an `unavailable` record whose `sides` is `["backend"]`: Python gave an outcome and
the backend gave none.

Where records go:

- If `VE_SHADOW_LOG` is set, records are appended to that file, as today, and nothing is tallied. With no record
  to write, the file is not created (`tests/test_stage2_evaluation.py:220–226`).
- Otherwise, if `VE_SHADOW_DIR` is set, it names a directory. Each process registers there when it first
  resolves the authority `shadow` (2.7), appends its records to a file of its own, `records-<pid>-<nonce>.jsonl`,
  and keeps its tally in `tally-<pid>-<nonce>.json`. The record file is created at the first record; a process
  that writes no record has a tally and no record file.
- Otherwise records are appended to `ve-shadow.jsonl` in the working directory, as today.

A record is written with one write on a file opened for appending, and is flushed before the shadow call
returns. A crash after the call therefore does not lose it.

### 2.7 Tallies, and calls that are not compared

A **tally** is one JSON object per process. It holds `run` (the value of `VE_SHADOW_RUN`, or `null`), `pid`,
`nonce`, `started` (the time of registration), `final` (`false` or `true`), `calls` (the number of shadow calls),
and, for each operation, these counts:

| Count | Counts |
|---|---|
| `compared` | compared calls (2.5); it is the sum of the next three |
| `agree` | compared calls with an empty class set |
| `recorded_only` | compared calls whose class set is `diagnostic-message` alone |
| `zero_tolerance` | compared calls whose class set has a zero-tolerance class |
| `completion_failures` | calls with `sides` `["backend"]` |
| `unavailable_other` | every other `unavailable` call |
| `uncompared` | for each reason, the calls noted as below |
| `lean_only` | `lean-only` records |
| `recorder_faults` | recorder faults |
| `count_members` | for each of `evaluations`, `steps` and `models_checked`: the leaf comparisons under that key, outside an `explanation`, `trace` or composition path, that were `equal` and that were `different` |
| `latency` | for each side, over the compared calls: the number, the sum, the smallest and the largest duration, and a histogram |

The histogram has the upper bounds 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200, 500, 1,000, 2,000 and 5,000
milliseconds, and one more cell above them. A duration is counted in the first cell whose bound is not below it.

**Registration.** A process **registers** as a worker of its run the first time `authority_for` returns
`shadow` in it, before any shadow call runs: it writes its tally file with `final: false` and every count zero.
The tally file is replaced as a whole, never written in part. It is rewritten, still with `final: false`, after
every 1,000 shadow calls, and rewritten with `final: true` when the process exits normally (an `atexit`
handler). A process that is killed, or that exits by a signal, leaves a tally with `final: false`, and its run
is not complete (2.8). A process that cannot write its tally writes one line on standard error (4.2), and its
run is not complete through that line. It cannot miss a record: 2.6 writes every record before its call returns.

**Reconciliation.** The counts that stand for records agree with the record file of the same process: the
number of `divergence` lines is `zero_tolerance` plus `recorded_only`, the number of `unavailable` lines is
`completion_failures` plus `unavailable_other`, the number of `lean-only` lines is `lean_only`, and the number of
`recorder-fault` lines is at most `recorder_faults`; a tally whose record counts are all zero has no record
file. `agree` and `uncompared` stand for no record and cannot be reconciled; that is why `final` is required.

An **uncompared call** is a call of a class-A entry, at the authority `shadow`, that the adapter answers from
Python without a candidate because the input is a scope gap (`ve/parser.py:382–383` is one such branch; the 14
branches are listed in section 6, row 10). Before it runs Python, the adapter calls
`dispatch.note_uncompared(op, reason)`. That function only counts, and only at the authority `shadow`; it never
raises. The reasons are names in a table in `ve/backends/dispatch.py`, one for each condition that routes an
input to Python statically, each with one sentence. Every scope gap of stage2-progress.md that is routed this
way has a reason. A reason that is not in the table is counted under `unregistered` and is a recorder fault.

A scope gap whose adapter does call `execute`, with a candidate that keeps Python's rule (coupled reading sets,
joint choices), is a compared call, not an uncompared one (limit 4 of section 10).

### 2.8 A run

A **run** is one execution of one corpus (2.9) by `tools/shadow_run.py --corpus <id> --out <directory>`, in a
clean checkout of one commit, with `VE_AUTHORITY=shadow`, `VE_AUTHORITY_OVERRIDES` unset, `VE_SHADOW_LOG` unset,
`VE_SHADOW_DIR` the run's directory and `VE_SHADOW_RUN` the run's name. The name is the corpus id, the first
twelve digits of the commit and the start time. The tool **registers the run** before it starts the corpus
command: it writes `run.json` with every member but `finished`, `exit`, `cases` and `stderr_faults`. It copies
the command's standard error to `stderr.txt` in the directory, and when the command exits it rewrites `run.json`
whole. The directory then holds the record files, the tally files, `stderr.txt` and `run.json`:

```json
{"run": "suite-eb96d5ed0000-20261004T000500Z", "corpus": "suite", "commit": "<40 hex>", "trigger": "nightly",
 "started": "2026-10-04T00:05:00Z", "finished": "2026-10-04T03:10:00Z", "exit": 0, "cases": 4478,
 "builds": {"ve_service": "<64 hex>", "rust_jsonl": "<64 hex>"}, "seed": null, "webapp_commit": null,
 "stderr_faults": 0}
```

`trigger` is `nightly`, `merge` or `manual`. `builds` holds the SHA-256 of the two checker binaries the run
loaded. `seed` is set for a corpus that takes one. `webapp_commit` is the commit of the repository `ve-webapp`
for the corpus `webapp`, `null` for every other. `stderr_faults` is the number of lines of `stderr.txt` that
begin with `ve shadow:` (4.2): each is a recorder fault that no tally may hold.

A run is **complete** when all of these hold:

1. `exit` is the corpus's `expected_exit`.
2. The checkout was clean, at `commit`, when the run started and when it finished.
3. Both hashes of `builds` are pinned in `lean/checkers.lock` at `commit` (its keys `ve_service` and
   `rust_jsonl`).
4. Every line of every record file is a record, and every tally file is a tally.
5. Every tally has `final` `true`: every registered worker finalized its tally, the workers that wrote no
   record among them.
6. Every record file has the tally of its process, and every tally reconciles with its record file (2.7).
7. The run has no recorder fault: `recorder_faults` is 0 in every tally and `stderr_faults` is 0.
8. `cases` is at least the corpus's `min_cases`, and the run's `compared` is at least its `min_compared`.
9. For a corpus with a seed, `seed` is the seed of 2.9.
10. `finished` is set.

Missing evidence is never read as agreement: a worker that registered and left no final tally, a record file
without a tally, a count that does not match its file, or a tally that could not be written, each makes the run
not complete, however far the other workers exceed the floors.

A run is **registered** when its trigger is `nightly` or `merge` and its commit is a first-parent commit of
`main`. Only registered runs count towards a day. A manual run is evidence for triage and, as a calibration run
(2.9), for the floors, and for nothing else.

### 2.9 The corpora

The registry is `conformance/shadow/corpora.json`: a list of entries `{"id", "plan", "command", "expected_exit",
"min_cases", "min_compared", "calibration", "merge"}`. `plan` quotes the base plan's words for the corpus;
`calibration` is the name of the calibration run that gave the floors. The ids, from the base plan's list (its
Stage 3, "Corpora"):

| id | The base plan's words | `min_cases`, where the base plan or a stored report gives a number |
|---|---|---|
| `suite` | "the full suite" | the number of tests in `tools/gate-collection.json` |
| `baseline` | "the stage-0 baseline (every matrix cell, including rejections and budget boundaries)" | 9,384 cells (stage2-progress.md) |
| `conformance` | "every conformance fixture and generator (evaluation 701, countermodels 708, parser 742, identity 706, certificates 732 plus 150 forged, the closure, order, induction, admission, elaborated-document and norms families" | 701 + 708 + 742 + 706 + 882, and the families' own counts |
| `differentials` | "the 1,000-set definitions and 1,000-case data differentials" | 2,000 |
| `english` | "85,000 English pairs" | 85,000 |
| `fuzz-core` | "fuzz (5,000 core" | 5,000 |
| `fuzz-closure` | "3,000 closure" | 3,000 |
| `fuzz-nightly` | "plus a fresh 5,000-case seed nightly" | 5,000 |
| `pilots` | "the `usecases/` pilots through `ve document check`" | the number of pilot documents at the commit |
| `assist` | "assist ledgers (tests, `experiments/authoring-gates/`, T1c)" | measured |
| `validators` | "E1, P1 and iceberg validators" | measured |
| `webapp` | "the web app API tests" | measured; the tests are in the repository `ve-webapp` and run against `ve` at the run's commit |

A **calibration run** of a corpus is a manual run, not registered, that meets every condition of 2.8 but the
floors (conditions 1 to 7, 9 and 10). Every `min_compared`, and every `min_cases` marked "measured", is the
`cases` or the `compared` of the corpus's calibration run. The **calibration commit** is a reviewed commit that
writes each corpus's `command`, its floors and its `calibration` into the registry; no run is registered before
it. A floor changes only by a later reviewed commit that says why. Completeness is therefore never measured
against a run that it would itself qualify: the calibration run is not registered and is not held to the floors.

The seed of `fuzz-nightly` for the day D is the integer written as the eight digits of D, year, month, day
(`20261012` for 12 October 2026). The committed fuzz seeds have this form (`conformance/README.md:164, 208`), so
anyone can run a day's fuzz again.

Only `suite` has `"merge": true`. Each corpus's command is read from the repository at the build and written
by the calibration commit; this draft has not read them (section 12, question 12).

### 2.10 A day

A **day** is a UTC calendar date. A run belongs to the day of its `started`.

The **nightly commit** of a day D, written **n(D)**, is the commit of the earliest-started registered run with
the trigger `nightly` that started on D. The **nightly** of D is the set of registered runs with the trigger
`nightly` that started on D at n(D). A registered run of D with the trigger `nightly` at another commit (a
re-run after a merge, for one) is not in the nightly: it counts under the four conditions of clean below, like
every registered run of D, and not under coverage.

A **merge run** is a registered run with the trigger `merge`: the corpus `suite`, at a first-parent commit of
`main` that changes a file outside `docs/` and `conformance/shadow/`. Such a commit **needs a merge run**. The
merge train starts it after the commit's gate (`tools/gate.py`) passes. The merge itself is never blocked by it.

D is **covered** when:

1. the nightly of D has a complete run of every corpus of the registry, at n(D);
2. every dispatch name of 2.2 has `compared` of at least 1, summed over the nightly; and
3. every first-parent commit of `main` after n(D′) up to and including n(D) that needs a merge run has a
   complete merge run, where D′ is the last day before D that has a nightly. When there is no such day, the
   commits are those after the commit of the first registered run.

D is **clean** when D is covered and, over every registered run that started on D:

1. every run is complete;
2. there is no zero-tolerance record;
3. there is no completion failure; and
4. there is no recorder fault.

A day with no nightly is not covered, and so not clean. A day with a commit that needed a merge run and has
none is not covered, and so not clean (base plan: "CI runs shadow on every merge"); the only way past that is
an amendment of the base plan (section 12, question 6).

D is **final** when D has ended (the UTC clock is past the end of D) and every registered run that started on D
has `finished`. A day is certified only when it is final: `tools/shadow_gate.py day <D>` writes the ledger entry
of a final day and exits 2 for any other (4.3), so that a morning report cannot certify a day before a later
run of it fails.

The **ledger entry** of D is `conformance/shadow/ledger/<D>.json`, written by `tools/shadow_gate.py day <D>`. It
holds `written`, the UTC time it was written; for each registered run of D, the members of `run.json`, whether
the run is complete, its tally summed over its processes, and the SHA-256 of each of its files; the sums for
each operation; the two answers `covered` and `clean` with the reasons of 3.1; the commits of condition 3 of
covered, each with its merge run or none; and, for each group of records with the same operation, kind and class
list, the number of records and the first 20 of them. `--check` rejects an entry whose `written` is before the
end of its day or before the `finished` of any of its runs. The entry is committed to `main` in a commit that
changes nothing outside `conformance/shadow/`. The run directories are kept outside the repository for the
length of the stage.

### 2.11 Findings and triage

A **finding** is a group of records of registered runs with the same operation, kind, class list and
`input_digest`, of these kinds: a zero-tolerance record, an `unavailable` record, a recorder fault.

The triage file is `conformance/shadow/triage.json`: a list of entries `{"id", "first_day", "op", "kind",
"class", "input_digest", "cause", "fix", "evidence", "note"}`. Each finding has exactly one entry and one cause:

| Cause | The base plan's rule | The entry needs | Restart (2.12) |
|---|---|---|---|
| `python` | "a Python deviant is a Python bug, fixed with a new conformance case" | the fix commit; the path of the new conformance case | no |
| `glue` | "a Lean glue or decoder deviant is fixed with statement review" | the fix commit; where the statement review is recorded | yes |
| `adapter` | named in "Any adapter or glue fix restarts the 14-day clock" | the fix commit | yes |
| `spec` | "a spec ambiguity gets a spec note and a fixture" | the spec note (file and section); the fixture; and the cause of the side that was changed to match the note, if one was | as that side's cause |
| `rust` | none: the base plan's triage rule does not name Rust | the fix commit; the Rust test | yes |
| `harness` | none | what in the corpus or the test was at fault (a test that injects a backend fault without choosing its authority, for one); the fix commit | no |
| `operational` | "every `CheckerUnavailable` in shadow is triaged" (base plan, section 4) | what happened on the machine: a timeout, a kill, a missing or unpinned binary. No code changes | no |

A finding is **closed** when its entry has what its cause needs and its fix commit, if it has one, is on `main`.

What makes a day not clean is fixed by 2.10 and not by the triage: a zero-tolerance record, a completion
failure (an `unavailable` record whose `sides` is `["backend"]`), a recorder fault, or missing coverage, whatever
the cause turns out to be. An `unavailable` finding whose `sides` has `python` (Python itself gave no answer,
alone or with the backend) does not by itself make its day not clean; it is a finding all the same, and the gate
needs it closed. A `spec` finding whose note changes what a supported input returns is also a product decision
of base plan 2.3: implemented in Python first, with a release note. No difference is exempt as "by design" (base
plan, stage 0).

The cause names the code that made the candidate's answer wrong, wherever that code lives: in `ve/backends/`, in
an adapter function outside it, in a helper the adapter uses (`ve/wire.py`, `ve/errors.py`:
`ve/backends/lean.py:29–30`), in the glue, in a decoder or in Rust. A fix of that code restarts the count (2.12)
whether or not its files are on the candidate surface.

### 2.12 The count, and restart events

The **candidate surface** is these paths, where the candidate's code lives:

- `ve/backends/`;
- every module of `ve/` that has a call of `execute` or a Lean-only handoff (2.2): the files that the scans L11
  and L13 find at the commit's first parent (at `eb96d5ed`, 25 modules outside `ve/backends/`: 17 with a call
  of `execute`, 8 that call one of the six handoff functions of 2.2; the build's full list of handoffs,
  question 13, may add to the 8);
- `lean/VE/Service/` and `lean/Serve.lean` (the glue);
- `lean/checkers.lock` (it stands for every change to the two checker binaries); and
- every file listed under `lean_decoders` in `ve/assurance-manifest.json` at the commit's first parent (the
  decoders; they sit outside `lean/VE/Service/`, `lean/VE/Bridge.lean` and `lean/VE/Json.lean` among them).

The **classed paths** are the candidate surface and every file under `ve/`. A first-parent commit of `main`
**needs classing** when `git diff --name-only` between it and its first parent has a file of the classed paths.
Both sets are decided from that list of names and the two files named above, and from nothing else.

A **restart event** is a first-parent commit of `main` that is either

- (a) the fix commit of a triage entry whose cause is `adapter`, `glue` or `rust`, or whose cause is `spec` and
  whose side changed to match the note has one of those causes. The cause names the code that was wrong,
  wherever it lives (2.11); the fix commit is a restart event whether or not its files are on the candidate
  surface, and whether shadow or anything else found the fault; or
- (b) a commit that needs classing and whose entry has a file classed `restart`.

The classing file is `conformance/shadow/changes.json`: a list of entries `{"commit", "class", "reason",
"files", "signed"}`. `files` has one line `{"path", "class", "reason"}` for each changed file of the classed
paths, and no other: `--check` compares the paths with `git diff --name-only`. A file's `class` is `restart` or
`no-restart`; the entry's `class` is `restart` when any of its files is, and `no-restart` otherwise. Every commit
that needs classing and is not a restart event by (a) has an entry. The DRI classes each file by this rule:

- `restart`: the change fixes adapter, glue, decoder or Rust code, however the fault was found (by shadow, by a
  test, by reading), or otherwise changes what a candidate answers on some input. Such a change is `restart`
  wherever the file lies: a fix in `ve/wire.py` that changes what an adapter sends to Lean is one.
- `no-restart`: the change is not such a fix and changes no candidate's answer: a change to retained Python
  only (the English surface, a renderer, a Python body of a class-A operation), a comment, a test hook. The
  reason says what the change is and why no candidate is affected. For a file on the candidate surface the
  reason must say why none of that file's candidate code changed.

`no-restart` never means "shadow did not find it".

The **count** on a day D is the largest number k for which:

1. each of the k days that end with D is clean; and
2. no restart event, and no commit that needs classing and has no entry, is among the first-parent commits
   after n(F) up to and including n(D), where F is the first of those k days.

So the first day of the count is a day whose nightly already ran with every restart event in it.

**Gate 3 is met on D** when the count on D is at least 14, every finding since the first registered run is
closed, and the reports of section 9 are attached. It is a statement about D and the commit n(D).

### 2.13 Completion rate, count parity and latency

Over a set of registered runs:

- The **completion rate** is n out of d. d is the number of compared calls plus the number of completion
  failures. n is the number of compared calls whose class set has neither `verdict` nor `budget-outcome`. On 14
  clean days n is d: that is the base plan's "100%".
- **Count parity** is, for each of `evaluations`, `steps` and `models_checked`, the two numbers `equal` and
  `different` of the tallies. On 14 clean days `different` is 0.
- The **latency report** is the tallies' `latency`, for each operation and each side.

The base plan's sentence counts "cases that complete under Python within nominal budgets". d also counts the
calls in which Python itself ended in `ResourceLimit`, because the budget-boundary row of the base plan's
section 4 asks for Python's outcome there too.

### 2.14 What is constructed and what is tested

Nothing in this stage is proved, and no theorem is cited for it.

By construction:

- **(A) Shadow measures the code that would answer.** The candidate is the function that `execute` calls at the
  authority `lean`, and it runs at that authority (2.2, 2.3).
- **(B) A record is not lost to a later crash** (2.6).

Tested, not constructed: V1 to V4; the class table; the projection; the tallies; the arithmetic of days and of
the count.

Shown by none of it: that Python and the backend agree on an input outside the corpora; that either is right
where they agree; that an uncompared call would have agreed.

## 3. English: one reading each

### 3.1 The sentences of the reports

`tools/shadow_gate.py` prints these sentences and no others about a day or the gate. Each is fixed here so that
a report, a ledger entry and a triage note say the same thing in the same words.

| Statement | Sentence | What it does not say |
|---|---|---|
| a clean day | `On <date>, every corpus ran in shadow at commit <c>, no compared call differed in a zero-tolerance class, and no call that Python answered got no answer from the backend.` | that Python and the backend agree on other inputs; that either result is correct |
| a day that is not clean | `<date> is not a clean day: <reason>.` | that the backend was wrong |
| a day that is not final | `<date> is not final: <reason>.` (exit 2; no entry is written) | that the day is or is not clean |
| the count | `The count of clean days in a row is <k>, from <first date> to <last date>.` | that the days before <first date> were not clean |
| a restart | `The count went back to zero at commit <c>: <reason>.` | that the commit was a mistake |
| the gate, met | `Gate 3 is met on <date> at commit <c>: the 14 days from <first date> to <date> are clean, no restart event is among the commits after <c_first> up to <c>, and every finding is closed.` Here `<c_first>` is n(<first date>) | that the default authority has changed, or may change without Gate 4; that no file changed between the two commits |
| the gate, not met | `Gate 3 is not met on <date>: <reason>.` | |
| completion | `Of <d> calls that Python completed, the backend completed <n> with the same outcome.` | that every call completed in Python |
| uncompared calls | `<n> calls of <op> were answered by Python alone, because the adapter does not take the input (<reason>). They were not compared.` | that these calls would have agreed |
| Lean-only calls | `<n> calls of <op> have no Python implementation. Lean answered them, and nothing was compared.` | that Lean's answers were checked against anything |
| a finding | `Finding <id>: on <date>, <op> gave a different result in Python and on the backend (<classes>). Cause: <cause>.` and then `Fixed by <commit>.` or `Open.` | which side was right, unless the cause says so |
| an unavailable call | `Finding <id>: on <date>, a call of <op> got no answer from <side> (CheckerUnavailable): <message>. Cause: <cause>.` | that the side is not installed |

The reasons of a day that is not clean, one line each:

- `the corpus <id> has no complete run in the nightly`
- `the operation <op> has no compared call in the nightly`
- `the commit <c> needs a merge run and has no complete one`
- `the run <run> is not complete: <condition of 2.8>`, where conditions 5 to 7 read `the worker <pid>-<nonce>
  did not finalize its tally`, `the tally of <pid>-<nonce> does not match its records` and `<n> recorder faults
  (<m> on standard error)`
- `<n> compared calls differ in a zero-tolerance class`
- `<n> calls completed in Python and got no answer from the backend`
- `<n> recorder faults`

The reasons of a day that is not final: `the day has not ended`; `the run <run> has not finished`.

The reasons of a restart: `it fixes finding <id> (<cause>)`, or `the DRI classed <path> as a restart: <reason>`.

The reasons of a gate that is not met: `the count is <k>, and 14 are needed`; `finding <id> is open`;
`commit <c> changes a classed path and is not classed`.

### 3.2 Wordings this replaces, and why

Each wording on the left was used for this stage, in the base plan, in the plan's pointer or in talk about it,
and has two readings.

| Wording | Its two readings | Written instead |
|---|---|---|
| "Shadow ran clean for 14 days." | no record was written for 14 days, which is also true when nothing ran; or every corpus ran on each day and no call differed | the sentences for a clean day and for the count |
| "Zero divergences." | no record of any class; or none in a zero-tolerance class | "No compared call differed in a zero-tolerance class. <n> compared calls differed in message text only." |
| "Lean and Python agree." | on every input, or on the compared calls of the corpora; and Lean alone, or Lean with Rust inside the adapter | "On <n> compared calls, the result under Lean authority equals Python's result after the comparison projection." |
| "on real traffic (suite, use cases, pilots, web app)" (the plan's pointer) | calls from people who use a deployed program; or the corpora of the base plan, among them the web app's API tests | "Every corpus of the registry runs in shadow. No call from a person using a deployed program is among them." |
| "Any adapter or glue fix restarts the clock." | any change to adapter or glue code; or a change that fixes a finding | "The count goes back to zero when a fix of adapter, Lean glue, Lean decoder or Rust code is merged, however the fault was found. Every other change under `ve/` or to the candidate surface is classed by the DRI, file by file, with a reason." |
| "14 consecutive days" | 14 nightly runs, whenever they happen; or 14 UTC calendar days with none between them | "14 UTC days in a row, each with its own nightly." |
| "The completion rate is 100%." | every call completed; or every call that Python completed also completed on the backend with the same outcome | the sentence for completion |
| "a Python deviant", "a Lean deviant" | the side whose result differs from the other's, which is both sides; or the side that is wrong against the specification | "Cause: python" means that Python's result was wrong against the specification and Python was fixed. "Cause: glue" means the same of the Lean glue or a Lean decoder |
| "The backend is unavailable." | Lean or Rust is not installed; or this one call got no answer | the sentence for an unavailable call |
| "shadow" | the authority; or the status of a wire contract | "the authority `shadow`" where the two could be confused |
| "`python: none`" | Python returned the value `None`; or there is no Python implementation | "a record of the kind `lean-only`, whose `python` is `null`" |

## 4. Diagnostics

### 4.1 The records

A divergence, for the call of `tests/test_stage2_dispatch.py:34–44`, outside a run:

```json
{"backend_ms": 0.01, "class": ["budget-outcome", "count-value", "verdict"], "input": {"ast": ["top"]},
 "input_digest": "<64 hex>", "kind": "divergence", "lean": {"evaluations": 2, "status": "Violated"},
 "op": "evaluate", "python": {"evaluations": 1, "status": "Satisfied"}, "python_ms": 0.01, "run": null,
 "rust": null, "test": "tests/test_stage2_dispatch.py::test_shadow_returns_python_and_logs_drift (call)"}
```

An unavailable call, for the call of `tests/test_stage2_dispatch.py:47–53`:

```json
{"backend_ms": 0.01, "class": [], "input": {}, "input_digest": "<64 hex>", "kind": "unavailable",
 "lean": {"code": "CheckerUnavailable", "message": "gone"}, "op": "check", "python": {"status": "ok"},
 "python_ms": 0.01, "run": null, "rust": null, "sides": ["backend"], "test": "<the test>"}
```

A Lean-only call:

```json
{"backend_ms": 41.0, "class": [], "input": {"…": "the case"}, "input_digest": "<64 hex>", "kind": "lean-only",
 "lean": {"…": "what Lean answered"}, "op": "<the soft route's executable>", "python": null,
 "python_ms": null, "run": "suite-…", "rust": null, "test": "<the test>"}
```

### 4.2 What a caller sees

Nothing new. At the authority `shadow` the caller gets Python's value or Python's exception (V1). No `VEError`
code is added, no message changes, and no record that `ve` returns gains or loses a member.

| Event inside a shadow call | What the caller sees | What is written |
|---|---|---|
| the candidate raises `CheckerUnavailable` | Python's outcome | an `unavailable` record; `completion_failures` + 1 when Python gave an outcome |
| the call passes no adapter | Python's outcome | an `unavailable` record with the message `no adapter for <op>` |
| the comparison or the tally raises | Python's outcome | a `recorder-fault` record if it can be written; `recorder_faults` + 1 |
| a record cannot be written (no space, no permission) | Python's outcome | one line on standard error for the process, `ve shadow: cannot write records: <text>`; `recorder_faults` + 1 in the tally only; no `recorder-fault` record is attempted |
| the tally cannot be written (at registration or later) | Python's outcome | one line on standard error for the process, `ve shadow: cannot write tally: <text>`. Nothing else can hold this fault; the run's `stderr_faults` counts the line (2.8) |

### 4.3 The tools

`tools/shadow_run.py` registers the run (writes `run.json` without `finished`) before it starts the corpus
command, copies the command's standard error to `stderr.txt`, rewrites `run.json` when the command exits, and
exits with the command's own status. It prints one line when the run is not complete: `run <run> is not
complete: <condition>`.

`tools/shadow_gate.py` has three commands. `day <date>` writes the ledger entry of a final day (2.10) and prints
the sentence for a clean day or the sentences for a day that is not clean; for a day that is not final it writes
nothing, prints the sentence for that and exits 2. `gate <date>` prints the count, the gate's sentence and the
report of section 9. `--check` reads the committed files and prints nothing when they are well formed and each
ledger entry's `covered` and `clean` follow from its own rows. Well formed means also: every wording entry is at
an eligible location (2.4); every ledger entry's `written` is after the end of its day and after the `finished`
of each of its runs; every entry of `changes.json` has a file line for each changed file of the classed paths
and for no other (2.12).

| Exit | Meaning |
|---|---|
| 0 | the day is clean; the gate is met; `--check` found nothing |
| 1 | the day is not clean; the gate is not met |
| 2 | the day is not final; a file is malformed, or a ledger entry does not follow from its rows. The line names the file and the member: `ledger entry <date> does not match its runs: <member>`, `wording entry <n> is not at an eligible location: <op> <path>`, `changes entry <commit> does not match its diff: <path>` |

## 5. Lean: the statements relied on

Stage 3 edits no file under `lean/` and adds no Lean statement. The build has no Lean work item: its Lean part
is to confirm that `lake build`, `lean/audit.py` and `VE/Route/frozen.py` pass with no difference under `lean/`
(fixture T1). A Lean change during the 14 days is a change to the candidate surface (2.12).

What shadow relies on from Lean is only that each service mode is its runner. These are the statements, as
built (`lean/VE/Service/Protocol.lean:468–498`):

```lean
namespace VE.Service

theorem runMode_evaluate (j : Json) : runMode .evaluate j = VE.Order.runEvaluationCaseReported j := rfl
theorem runMode_checkCertificate (j : Json) :
    runMode .checkCertificate j = VE.CertificateWire.runCaseReported j := rfl
theorem runMode_order (j : Json) : runMode .order j = VE.Order.Surface.runCaseReported j := rfl
theorem runMode_route (j : Json) : runMode .route j = VE.Route.Run.runCaseReported j := rfl
theorem runMode_norms (j : Json) : runMode .norms j = VE.Norms.Run.runCaseReported j := rfl
theorem runMode_english (j : Json) :
    runMode .english j = match VE.English.ServiceRun.run
        (match j with | .str text => text | _ => j.compress) with
      | .ok result => result
      | .error message => Json.mkObj [("status", .str "error"), ("error", .str message)] := rfl
theorem runMode_environment (j : Json) :
    runMode .environment j = Standalone.reported Standalone.environmentCase j := rfl
theorem runMode_model (j : Json) :
    runMode .model j = Standalone.reported Standalone.modelCase j := rfl
theorem runMode_check (j : Json) :
    runMode .check j = Standalone.reported Standalone.checkCase j := rfl
theorem runMode_identity (j : Json) :
    runMode .identity j = Standalone.reported Standalone.identityCase j := rfl
theorem runMode_parse (j : Json) :
    runMode .parse j = Standalone.reported Standalone.parseCase j := rfl
theorem runMode_graph (j : Json) :
    runMode .graph j = Standalone.reported Family.graphMode j := rfl
theorem runMode_readings (j : Json) :
    runMode .readings j = Standalone.reported Family.readingsMode j := rfl
theorem runMode_bundle (j : Json) :
    runMode .bundle j = Standalone.reported FamilyBundle.bundleCase j := rfl
theorem runMode_familyNorms (j : Json) :
    runMode .familyNorms j = FamilyNorms.runCaseReported j := rfl

theorem caseResult_ok (m : Mode) (i : Nat) (j : Json) : caseResult m i (.ok j) = runMode m j := rfl

end VE.Service
```

The namespace is the file's (its lines 39 and 535). Stage 3 changes none of these statements.

What they do not give this stage: no theorem says that a Lean runner's answer equals Python's, and none is
added. Agreement is measured on the corpora. Which theorem covers which operation after the switch is Stage 4's
`docs/spec/theorem-coverage.md` (base plan, stage 4), not this file. The trust map's list of verdicts with no
theorem on their path (its 5.1) is unchanged by this stage: shadow compares those runners with Python and proves
nothing about them.

## 6. Where the code stands against the base plan (read, not run)

| # | The base plan's Stage 3 | The code at `eb96d5ed` | The build adds |
|---|---|---|---|
| 1 | "runs Python and Lean/Rust on every semantic call, returns Python's result" | `execute` does this for a call that reaches it (`dispatch.py:172–200`). The comparison and the write are not guarded: an exception in `_classes` or `_append` reaches the caller. The shadow path takes `lean or rust` as its candidate (line 180), which the `lean` path does not (lines 163–166), and runs it without a pin, so a constituent the candidate reaches through `execute` (`search.py:713`) is itself a shadow call answered by Python | V1; the candidate is `lean=` only, run under `pinned("lean")` (2.2, 2.3) |
| 2 | "appends a divergence record `{op, input_digest, python, lean, rust, class}`" | written, with `python_ms` and `backend_ms`, and only when the two differ (`dispatch.py:192–197`). An exception is recorded as `code` and `message` only (lines 177–178, 188–189), while the baseline compares `to_dict()` (`probe_matrix.py:140`) | `kind` and the other members of 2.6; the error record of 2.4 |
| 3 | `input_digest` | nine call sites pass a payload that does not determine the input. Six pass a constant, so every input has one digest: `{"kind": "readings"}` (`readings.py:472–479`), `{"kind": "model"}` (`model.py:98`, `background.py:267`), `{"kind": "environment"}` (`environment.py:312`), `{"kind": "graph"}` (`argument.py:581`), `{"kind": "bundle"}` (`bundle.py:148`), `{"kind": "parse"}` (`parser.py:384`). Three pass a part: `certificate_replay` omits the premises, the conclusion and `max_steps` (`entailment.py:688–689`); `norms_certificate` omits the premises and the conclusion (`norms.py:508–509`); `norms_conflict` omits the model, the certificates and the budgets (`norms.py:608`) | requirement (I) |
| 4 | "For Lean-only operations … log `python: none` outside the divergence classes" | absent | the `lean-only` record |
| 5 | the ten classes | `_classes` (`dispatch.py:85–139`) has rows 1 to 9 of 2.5 without the `readings` half of row 4 and without `report_id` and `document_hash`. It applies no projection, so a different `checker_build` is `schema`. One side returning and the other raising falls to `schema`. A candidate that raises `CheckerUnavailable` is classed as a difference | 2.4, 2.5 |
| 6 | the corpora; "CI runs shadow on every merge"; "a fresh 5,000-case seed nightly" | absent | 2.8 to 2.10; `tools/shadow_run.py` |
| 7 | "the completion rate of section 4 is 100%"; "public-count parity and latency reports attached" | nothing is counted when the two sides agree, so no rate, parity or latency can be stated | the tallies |
| 8 | "Zero divergences in the zero-tolerance classes on all corpora for 14 consecutive days" | absent | 2.10, 2.12; `tools/shadow_gate.py` |
| 9 | the triage rule; "Any adapter or glue fix restarts the 14-day clock" | absent | 2.11, 2.12 |
| 10 | — | calls routed to Python statically leave no trace. There are 14 such branches: an `authority_for` guard with a disjunct that is not about the authority, at `ast.py:336, 372`, `parser.py:382`, `environment.py:303`, `model.py:93`, `background.py:259`, `definitions.py:105`, `readings.py:465`, `argument.py:579`, `entailment.py:685` and `norms.py:340, 367, 506, 606` | `note_uncompared` in each (fixture L12) |

Stage 2 work that is still open and changes the candidate surface when it lands (stage2-progress.md, its last
list): the scope gaps of stage 2c, due before Gate 4; the argument record's wording and the four provenance
members; batching; Rust parse diagnostics; the manifest's bindings for the service adapters. Section 12,
question 2, is about their order.

## 7. The build: files and gates

### 7.1 Diff scope

| Changed or added | By |
|---|---|
| `ve/backends/dispatch.py` | 2.3 to 2.7: the candidate is `lean=` only and runs under `pinned("lean")`; the error record is `to_dict()`; registration and final tallies |
| the modules that call `execute` (the third column of 2.2) | the payloads of requirement (I) (nine sites) and the calls of `note_uncompared` (14 branches), and nothing else. No statement that computes a Python result changes |
| the functions through which `ve` hands a case to a statement-layer route (2.2), in `ve/backends/lean.py` and wherever else the build finds one | the `lean-only` record, one per case, and nothing else |
| `tools/shadow_run.py`, `tools/shadow_gate.py` | new |
| `conformance/shadow/corpora.json` (written by the calibration commit, M3.3); `wording.json`, `triage.json` and `changes.json`, each the empty list; `ledger/` | new |
| `tests/probe_matrix.py` | `baseline_projection` has one definition that shadow also uses |
| tests | the fixtures of section 8. Each expectation of `tests/test_stage2_dispatch.py` and `tests/test_stage2_evaluation.py` that changes is listed in the commit |
| `ve/assurance-manifest.json`, `reviewed_broad_handlers`, the entry of `dispatch.execute`; the generated part of `docs/spec/assurance-manifest.md` | the entry's sentence, if the handler's shape changes |
| `docs/spec/stage3-progress.md` | new: the checkpoint, and at the end the Gate 3 report |

Not changed: every file under `lean/` and `rust/`; `lean/checkers.lock`; `conformance/baseline-2026-09/`;
`conformance/identity.json`; every frozen hash; the default of `VE_AUTHORITY` (`dispatch.py:61`); the
`authority` of every operation in the manifest; `tools/gate.py`.

### 7.2 Gates for every build commit

- **B1.** The baseline replays byte for byte at the default authority (`tests/probe_matrix.py`).
- **B2.** `tools/stage2_parity.py --authority lean` reports 0 regressions and 0 different cells.
- **B3.** The full suite passes at the default authority and under `VE_AUTHORITY=lean`, as at Gate 2.
- **B4.** `lake build`, `lean/audit.py` and `VE/Route/frozen.py` pass, with no difference under `lean/`.
- **B5.** `tools/inventory_lint.py` and the Python layer ledger pass.

The first nightly comes after the last build commit: a build commit changes `ve/backends/`, which is a change to
the candidate surface.

## 8. Acceptance fixtures

Deterministic, with expectations written by hand from sections 2 and 4. Each reviewer derives the expectation of
every fixture before reading the column "Expected". Unless a row says otherwise, the two sides are plain
functions given to `execute`, the authority is `shadow`, and `VE_SHADOW_DIR` is a fresh directory.

### 8.1 The shadow call

| Case | Input | Expected |
|---|---|---|
| S1 | Python returns an object `v`; the candidate returns an equal record | returns `v`, the same object; no record; the tally has `compared` 1 and `agree` 1 |
| S2 | Python returns `{"status": "Satisfied", "evaluations": 1}`; the candidate returns `{"status": "Violated", "evaluations": 2}` | returns Python's object; one record with the `kind`, `op`, `class`, `python`, `lean` and `rust` of the first object of 4.1; `zero_tolerance` 1 |
| S3 | Python raises a `VEError` `e`; the candidate raises another with the same code and text | raises `e`, the same object; no record; `agree` 1 |
| S4 | as S3, with a different text | raises `e`; a record with class `["diagnostic-message"]`; `recorded_only` 1 |
| S5 | as S3, with a different code and the same text | a record with class `["diagnostic-code"]` |
| S6 | Python returns `{"status": "ok"}`; the candidate raises a `VEError` with the code `InvalidInput` | returns Python's object; class `["schema", "verdict"]` |
| S7 | Python returns `{"status": "Satisfied"}`; the candidate raises `ResourceLimit` | class `["budget-outcome", "schema", "verdict"]` |
| S8 | Python returns `{"status": "ok"}`; the candidate raises `CheckerUnavailable("gone")` | returns Python's object; one record with the `kind`, `class`, `python`, `lean`, `rust` and `sides` of the second object of 4.1; `completion_failures` 1, `compared` 0 |
| S9 | the call passes neither `lean=` nor `rust=`; then `rust=` alone, a function that records that it ran | an `unavailable` record whose `lean` is `{"code": "CheckerUnavailable", "message": "no adapter for <op>"}`, `rust` `null`, `sides` `["backend"]`, both times; the `rust=` function did not run |
| S10 | Python raises `CheckerUnavailable`; the candidate returns | raises Python's exception; an `unavailable` record with `sides` `["python"]`; `unavailable_other` 1, `completion_failures` 0 |
| S11 | both raise `CheckerUnavailable` | one record with `sides` `["backend", "python"]`; `unavailable_other` 1 |
| S12 | the candidate returns a value whose comparison raises `RuntimeError` | returns Python's object; `recorder_faults` 1; a `recorder-fault` record |
| S13 | `VE_SHADOW_DIR` names a directory that cannot be written; the two sides differ | returns Python's object and raises nothing; standard error has the line of 4.2 |
| S14 | Python raises `KeyboardInterrupt` | it leaves `execute`; the candidate is not run. The same with the candidate raising it |
| S15 | the authorities `python`, `lean` and `rust-experimental`, each with two sides that differ | the directory stays empty; the result is that side's, as today; with no `lean=` at `lean`, `CheckerUnavailable` (`tests/test_stage2_dispatch.py:28–31`) |
| S16 | the candidate of an operation A calls `execute` for an operation B, with no `pinned` of its own, and B's two sides differ; A's `python` function does not call B. Then the same with A's `python` function also calling `execute` for B | the tally has `compared` 1 for A and 0 for B, and no record for B: inside the candidate the authority is `lean`, so the nested call is not a shadow call and B's `lean=` answers it. Then `compared` 1 for A and 1 for B, the one from Python's side |
| S17 | `VE_SHADOW_LOG` names a file and `VE_SHADOW_DIR` is also set; first two sides that differ, then two that agree | the record is in the file and the directory stays empty; with the two that agree alone, the file is not created |
| S18 | one case is handed to the soft route through `run_soft_case`, with `VE_AUTHORITY=shadow` and the Lean binaries built; then the same with `VE_AUTHORITY` unset; then three cases in one call of `run_readings_cases` at `shadow` | returns the row it returns at the default authority; one record of the kind `lean-only` with `python` `null`, class `[]` and the route executable's name as `op`; `lean_only` 1. With the variable unset: no record. For the batch: three `lean-only` records with three different `input_digest`, each with Lean's row for its case; `lean_only` 3 |
| S19 | `note_uncompared("parse", r)` for a reason `r` of the table, at `shadow`; then at `python`; then with a reason that is not in the table, at `shadow` | `uncompared[r]` is 1 and there is no record; nothing; `uncompared["unregistered"]` 1 and `recorder_faults` 1, and nothing is raised |
| S20 | in a fresh process with `VE_SHADOW_DIR` set, `authority_for("evaluate")` returns `shadow` for the first time; no call of `execute` has been made; then the process exits normally | at the first return, the tally file exists with `final` `false` and `calls` 0, and there is no record file; after the exit, the tally has `final` `true` |

### 8.2 The classes and the projection

Both sides return; the operation is `evaluate` unless the row names one.

| Case | The two records differ in | Expected class list |
|---|---|---|
| C1 | `checker_build` at the root, and `record_id` two levels down | none: `agree` |
| C2 | `graph_id`; then `report_id` | `["identity"]`, both times |
| C3 | operation `graph`, path `["proof"]`, `"Python replay checked"` against `"Lean graph report checked"`, with that entry in the wording map; then without the entry; then with the entry and the operation `bundle`; then with the entry and the strings at the path `["root", "proof"]` | none; `["schema"]`; `["schema"]`; `["schema"]` |
| C4 | a `kind` inside `explanation.children`, and an item of `composition.supporting_edge_ids` (`tests/test_stage2_dispatch.py:63–72`) | `["composition", "explanation"]` |
| C5 | `verdict`, `"ALL"` against `"SOME"`: operation `readings`; then operation `compare` | `["composition", "verdict"]`; `["verdict"]` |
| C6 | the length of `assumptions`; then the length of `values`, with equal items in the common part | `["composition", "schema"]`; `["schema"]` |
| C7 | `value`, `true` against `1` | `["schema"]` |
| C8 | `evaluations`, 3 against 4, at the root; then inside `explanation` | `["count-value"]`; `["explanation"]` |
| C9 | `detail`; then `generator` | `["diagnostic-message"]`; `["diagnostic-code"]` |
| C10 | a member `foo` with two values; then a member `foo` on one side only | `["schema"]`, both times |
| C11 | `status` and `message` | `["budget-outcome", "diagnostic-message", "verdict"]` |
| C12 | the projection of every output of the baseline, by shadow's function and by `baseline_projection` | equal on every cell |
| C13 | both sides raise `InvalidModel`, with the same `code` and `message`, and the records differ in `generator` only; then in `span.line` only; then in `path` only; then in `message` only | `["diagnostic-code"]`; `["schema"]`; `["schema"]`; `["diagnostic-message"]` |

### 8.3 Records, tallies and runs

| Case | Input | Expected |
|---|---|---|
| L1 | the record of S2, read as bytes | one line; keys in sorted order; no space after `:` or `,`; a newline at the end; the members are those of 2.6 for its kind and no others |
| L2 | for each dispatch name of 2.2, and for each argument of the call on which the operation's result depends (for `certificate_replay`: the environment, the premises, the conclusion, the certificate and `max_steps`; for `norms_certificate`: the document, the premises, the conclusion and the certificate; for `norms_conflict`: the document, the model, the certificates, `max_evaluations`, `prove` and `tableau_steps`; and so on for each): two real calls that differ in that argument alone, each with a candidate replaced so that it differs | the two records have different `input_digest`, for every argument |
| L3 | a payload of 65,536 bytes in canonical JSON; then one of 65,537 | `input` is the payload; `input` is `null`, and `input_digest` is set |
| L4 | two processes, one shadow call each, one directory | two record files and two tally files; the sums are 2 |
| L5 | three compared calls whose backend durations are set to 0.05, 3 and 7,000 milliseconds | one each in the cells 0.1, 5 and the cell above 5,000; smallest 0.05, largest 7,000 |
| L6 | Python's record holds a `bytes` value; the two sides differ | the line is JSON; the member is `"<unserializable bytes>"` |
| L7 | a process is killed with `SIGKILL` after a shadow call with a difference has returned | the record is in the file, as a whole line |
| L8 | a run directory with, in turn: `exit` 1; a hash that `checkers.lock` lacks; half a line at the end of a record file; a tally with `final` `false`; a tally whose `zero_tolerance` plus `recorded_only` is 2 while its record file has one `divergence` line; a record file with no tally; `recorder_faults` 1; `stderr_faults` 1 with a tally that has `recorder_faults` 0; `cases` below the floor; `compared` below the floor; the wrong seed; no `finished` | not complete each time, with that condition named |
| L9 | the corpus `baseline` at `shadow`, with the parity tool's observer | every probe cell has a compared call, or an uncompared call, or is in the parity tool's class "same, python"; the build reports the three numbers |
| L10 | one input for each scope gap that 2.7 gives a reason; one coupled reading set | the tally has `uncompared` 1 under that reason, and no record; the coupled set is a compared call |
| L11 | the first arguments of all calls of `execute` in `ve/`, found by a scan of the syntax trees | the 23 names of 2.2; the scan also lists the modules, for 2.12 |
| L12 | a scan of the syntax trees of `ve/` for every `if` whose test calls `authority_for` and has a disjunct that does not (the 14 of section 6, row 10) | each such branch's static Python path calls `note_uncompared` with a reason of the table before it runs Python; a branch without the call fails the fixture |
| L13 | a scan of `ve/` for every function that hands a case to a statement-layer route executable (2.2) | the build's list of handoff functions (question 13); with L11, the modules of the candidate surface outside `ve/backends/` (25 at `eb96d5ed` by the six handoff functions named in 2.2: 17 by L11, 8 by L13) |
| L14 | a process is killed with `SIGKILL` after it registered and before its first shadow call | its tally has `final` `false`; the run is not complete, condition 5 of 2.8 |
| L15 | a run of three workers: two exceed every floor of the corpus, and the third makes only calls that agree (no record file) and is killed before it exits | the run is not complete: `the worker <pid>-<nonce> did not finalize its tally`; the floors do not save it |
| L16 | a run of three workers: two exceed every floor, and in the third every write to `VE_SHADOW_DIR` fails (its tally at registration, its records) while its calls differ | `stderr.txt` has the two lines of 4.2 for that process; `stderr_faults` is at least 1; the run is not complete, condition 7 of 2.8; the caller got Python's outcome on every call |

### 8.4 Days, the count and the gate

On ledgers and a commit history made for the test. The days are numbered 1 to 14; unless a row says otherwise
every day is clean, no commit changes a classed path, every commit that needs a merge run has a complete one,
`day` is run after the day has ended and its runs have finished, and no finding is open.

| Case | Input | Expected |
|---|---|---|
| G1 | as stated | the count on day 14 is 14; `gate` prints the sentence for the gate met and exits 0 |
| G2 | days 2 to 14 only | the count on day 14 is 13; `the count is 13, and 14 are needed`; exit 1 |
| G3 | on day 7 the corpus `english` has no complete run | day 7 is not clean, with the first reason of 3.1; the count on day 14 is 7 |
| G4 | on day 7 a merge run has one zero-tolerance record | day 7 is not clean; the count on day 14 is 7 |
| G5 | on day 7 one record with class `["diagnostic-message"]` | day 7 is clean; the count on day 14 is 14 |
| G6 | on day 7 one completion failure; then, in its place, one `unavailable` record with `sides` `["python"]` and a closed entry; then one with `sides` `["backend", "python"]` and a closed entry; then the last with its entry open | not clean, and the count on day 14 is 7; clean, and the gate is met; clean, and the gate is met; clean, and `finding <id> is open`, exit 1 |
| G7 | the fix of a finding with cause `adapter` is merged on day 5: after n(5); then before n(5) | the count on day 14 is 9; then 10 |
| G8 | a commit before n(9) changes one file of the candidate surface, in turn: `lean/VE/Service/Graph.lean`; `ve/parser.py`; `lean/VE/Bridge.lean`. Each with no entry in `changes.json`; with the file classed `no-restart`; with the file classed `restart` | with no entry: `commit <c> changes a classed path and is not classed`, exit 1, for all three; with `no-restart`: the gate is met, for all three (the tool does not judge the reason, limit 14); with `restart`: the count on day 14 is 6, for all three |
| G8a | a commit before n(9) changes `ve/wire.py`, a fix of the canonical JSON of the payload the Lean adapters send (candidate-affecting, off the surface): with no entry; then classed `restart` with that reason | `commit <c> changes a classed path and is not classed`, exit 1; the count on day 14 is 6, and the restart's reason is `the DRI classed ve/wire.py as a restart: <reason>` |
| G8b | a commit before n(9) changes `ve/english.py`, a Python-only fix (the English surface stays Python, base plan 2.3): with no entry; then classed `no-restart` with that reason | `commit <c> changes a classed path and is not classed`, exit 1; the gate is met, and the entry is listed in the report's classed changes with its reason |
| G8c | a commit before n(9) changes `ve/wire.py` and `ve/english.py`; its entry has a line for `ve/wire.py` only; then lines for both and a third for `ve/printer.py` | exit 2, `changes entry <commit> does not match its diff: ve/english.py`; exit 2, naming `ve/printer.py` |
| G9 | a finding of day 0 has an entry with no cause | `finding <id> is open`; exit 1 |
| G10 | the fix of a finding with cause `python` is merged on day 10 | the count on day 14 is 14 |
| G11 | the ledger entry of day 3 says `clean` and one of its run rows has `zero_tolerance` 1 | exit 2, with the line of 4.3 |
| G12 | day 7 has no nightly | day 7 is not clean; the count on day 14 is 7 |
| G13 | on day 7 the operation `distinguishing_model` has `compared` 0 in the nightly | day 7 is not covered, with the second reason of 3.1 |
| G14 | on day 7 the run of `fuzz-nightly` has the seed of day 6 | that run is not complete; day 7 is not clean |
| G15 | on day 7 a manual run has a zero-tolerance record | the ledger entry of day 7 does not hold it; day 7 is clean |
| G16 | a commit that changes only `conformance/shadow/ledger/` | it needs no merge run and no entry in `changes.json` |
| G17 | a commit after n(6) and before n(7) changes `tests/test_x.py` and has no merge run; then it has a complete merge run; then a merge run that is not complete | day 7 is not covered, with the third reason of 3.1, and the count on day 14 is 7; covered; not covered |
| G18 | `day 7` is run at 23:00Z on day 7; then on day 8 while a registered run that started on day 7 has no `finished`; then after that run finished | `7 is not final: the day has not ended`, exit 2, no entry; `7 is not final: the run <run> has not finished`, exit 2, no entry; the entry is written, with `written` after both |
| G19 | the ledger entry of day 3 has `written` at 20:00Z on day 3; then `written` on day 4 but before the `finished` of one of its runs | `--check` exits 2 both times, naming the entry and `written` |
| G20 | on day 7, after the nightly, a second set of nightly runs starts at a later commit, and one of them has a zero-tolerance record | n(7) is the first set's commit and day 7 is covered by it; day 7 is not clean (the later run is a registered run of day 7); the count on day 14 is 7 |
| G21 | the fix of a finding with cause `spec` is merged on day 5 after n(5): the side changed to match the note is the glue; then it is Python | the count on day 14 is 9; then 14 |

### 8.5 Conservativity

- **Z1.** The suite, with `VE_AUTHORITY=shadow` set for the whole run, collects the tests it collects at the
  default authority and gives each the same outcome. A test that must choose its own authority to pass is
  changed to choose it, as `meter_python` does (stage2-progress.md, the decision of 2026-09-30), and is listed
  in the commit.
- **Z2.** B1 and B2 of 7.2 hold after the last build commit.
- **Z3.** On every compared call of the corpus `baseline`, the public record of the object Python returned is
  equal before and after the candidate ran (V4).
- **Z4.** The build's commits change no file under `lean/` or `rust/`, and not `lean/checkers.lock`, the
  baseline or `conformance/identity.json`.
- **Z5.** With no variable set, `authority_for("evaluate")` is `python`. The manifest still has 24 operations
  with the authority `python` and 2 with `lean-only`.
- **Z6.** The tests of `tests/test_stage2_dispatch.py` and `tests/test_stage2_evaluation.py` that use the
  authority `shadow` pass. Their assertions on `class`, on `lean.code` and on a file that is not created hold
  unchanged.

### 8.6 Lean and tooling

| Case | Input | Expected |
|---|---|---|
| T1 | `lake build`, `lean/audit.py`, `VE/Route/frozen.py` after the build | pass, with the file and theorem counts they had before it |
| T2 | `tools/shadow_gate.py --check` on the committed tree | exits 0 and prints nothing |
| T3 | `corpora.json` without the corpus `english`; `triage.json` with a cause `unknown`; `changes.json` with a class `maybe`; `wording.json` with an entry at each of these locations in turn: `evaluate` `["status"]`, `parse` `["code"]`, `model_validation` `["generator"]`, `evaluate` `["evaluations"]`, `graph` `["graph_id"]`, `evaluate` `["explanation", "children", "kind"]`, `evaluate` `["explanation", "bindings", "local_id"]`, `evaluate` `["explanation", "detail"]`, `graph` `["composition", "message"]`, `bundle` `["proof"]`; then `parse` `["message"]` and `graph` `["proof"]` | exit 2 each time, with a line that names the file and the member; for the ten wording entries, `wording entry <n> is not at an eligible location: <op> <path>`; the last two are accepted (exit 0) |

## 9. Gate 3

The DRI reviews one report, made by `tools/shadow_gate.py gate <date>` and stored at the end of
`docs/spec/stage3-progress.md`. Astra and Fable read it before any step of Stage 4. The tool judges each row
from the ledger, the triage file, the classing file and the commit history, not from a stated summary.

| Row | Definition | Required |
|---|---|---|
| the count | 2.12, on the day of the report | at least 14 |
| coverage | each of the 14 days is covered (2.10): every corpus in its nightly, every operation compared, a complete merge run for every commit that needed one | all 14 |
| zero-tolerance classes | zero-tolerance records in the registered runs of the 14 days | 0 |
| completion | completion failures in those runs; the rate of 2.13 | 0; n is d |
| recorder faults | in those runs, in the tallies and on standard error | 0 |
| findings | findings since the first registered run that are not closed | 0 |
| the classed changes | among the first-parent commits after the first day's nightly commit, up to the last day's: restart events; commits that need classing and have no entry | 0; 0 |
| finality | each of the 14 ledger entries was written after its day ended and its runs finished | all 14 |
| conservativity | B1, B2 and B4 of 7.2, at the last day's nightly commit | hold |

Attached to the report, as the base plan asks ("public-count parity and latency reports attached"). These rows
carry no threshold of this gate:

| Attachment | Content |
|---|---|
| count parity | 2.13, for each operation |
| latency | 2.13, for each operation and each side. The targets of the base plan's section 4 are Gate 4's |
| message differences | the number of `diagnostic-message` records and of distinct triples (2.5) |
| uncompared calls | for each operation and reason, the number, in the sentence of 3.1 |
| Lean-only calls | for each operation, the number, in the sentence of 3.1 |
| merge runs | each commit of the 14 days that needed a merge run, with its run. Coverage already requires every one of them; this row only lists them |
| the classed changes | every entry of `changes.json` for the 14 days, each file line with its class and reason, and whether the file is on the candidate surface |

Gate 3 allows Stage 4 to be specified and built. It does not change the default authority; that is Gate 4's.

## 10. Limits, and what is not claimed

1. **Agreement, not correctness.** Shadow shows that two programs gave the same result. Where both are wrong in
   the same way, nothing is recorded. The runners that the trust map lists with no theorem on their path (its
   5.1) are compared with Python, not proved.
2. **The corpora, not use.** Every compared call comes from a test, a fixture, a generator or a pilot document.
   No call from a person using a deployed program is included.
3. **Not every operation is compared.** `english.admission` is not. `identity`, `check`, `document.check` and
   `reference.validate` are compared only through other operations. An uncompared call (2.7) and a Lean-only
   call (2.6) are counted and compared with nothing.
4. **Some candidates share code with Python.** For `environment_validation`, `model_validation`,
   `definitions_elaboration`, `bundle` and `parse`, an accepted input comes back in Python's own container, so
   only the acceptance, the code and the identity can differ. For `premise_status` and `compare`, and for
   `readings` on coupled sets and joint choices, the rule is Python's on both sides and only the constituents
   differ.
5. **The typing cache.** The `typing` candidate for one formula asks Lean once for each pair of environment and
   formula in a process (`ve/ast.py:351–358`); a later call with the same pair is answered from the cache.
6. **A test that sets its own authority is not shadowed** inside that test.
7. **The ledger is as good as the process that writes it.** The hashes make an entry checkable against the run
   directories. Nothing proves that a run happened, or that its directory was not edited before it was hashed.
8. **A process killed before it registers leaves no trace.** Registration is the first resolution of the
   authority `shadow`, before any shadow call, so such a process has compared nothing and lost no comparison;
   its cases are missing from `cases` and, for a test runner, from `exit`, and nothing else detects it. A process
   that registered and did not finalize, or whose evidence could not be written, makes its run not complete
   (2.7, 2.8).
9. **Shadow latency is not the latency of the switch.** Both sides run one after the other in one process. The
   end-to-end rows of the base plan's section 4 are measured under `VE_AUTHORITY=lean`, by that section's
   method.
10. **One fault can give several records**: one for a constituent and one for the operation that composes it.
11. **Records hold inputs.** `input` and the two result records can hold the text of the corpus. That is the
    project's own test material today. It would be a person's text if a deployed program ever ran at `shadow`.
12. **Gate 3 is about one commit.** A change to the candidate surface after n(D) is not covered by a gate met on
    D. Stage 4's specification has to say what such a change does to the switch.
13. **Cost.** A compared call runs Python and the candidate. An operation that composes others runs its
    constituents three times: once in Python, once as their own candidates, once inside its candidate. How long
    a nightly takes is not known.
14. **The class of a change is the DRI's word.** The tool checks that every changed file of the classed paths has
    a class line; it cannot check that `no-restart` is right. A wrong `no-restart` is found only by the next
    difference shadow records.

## 11. Statement review checklist (Astra + Fable, before any build step)

1. **Scope.** Is this the base plan's Stage 3, with nothing of Stage 4 in it? Is anything of the Stage 3 text
   missing from sections 2 and 9?
2. **The shadow call (2.3).** Is each step determined for every outcome of the two sides? Can anything in step
   2 or 3 reach the caller? Is V4 the right property for the adapters that fill Python's container?
3. **The classes (2.5).** Derive the class list of every fixture of 8.2 before reading it. Is the table total
   and is its order right? Are cases B, C and D the right reading of the base plan's ten classes? Is
   `unavailable` rightly kept out of them?
4. **The projection (2.4).** Does it exclude exactly what the base plan's section 5 excludes? Can a wording
   entry hide a difference that is not a wording?
5. **The day (2.10).** Can a day be clean when a corpus did not run, when nothing was compared, or when a record
   was lost? Is a day that is not covered rightly a break in the run of days?
6. **The count (2.12).** Is (a) the base plan's restart rule? Is the classing of the other changes by the DRI
   acceptable, or should every change to the candidate surface restart the count? Is the surface the right set
   of paths?
7. **Completion (2.6, 2.13).** Is one unanswered call rightly enough to lose a day? Is the rate the base plan's?
8. **Wordings (3).** Does each sentence have one reading? Is any rejected wording of 3.2 still in this file or in
   the plan?
9. **Conservativity (7, 8.5).** Can a build commit change a verdict, an identity, a code, a default or a Lean
   byte?
10. **The open questions (12).** Which of them must be answered before the build, and which before the first
    nightly?

## 12. Choices this specification resolves, and open questions

The base plan fixes: what the authority `shadow` does; the record's six members; the ten classes and their two
tolerances; the corpora; that CI runs shadow on every merge; the triage rule; that an adapter or glue fix
restarts the clock; Gate 3. Everything below is this specification's own choice. No design debate decided any of
it; the statement review (section 13) confirmed each or corrected it as the rows now read.

| # | Choice | Relative to the base plan |
|---|---|---|
| R1 | Records have a `kind`. An unanswered call is a record of the kind `unavailable`, not an eleventh class | the plan names ten classes and asks, in its section 4, that every `CheckerUnavailable` be triaged |
| R2 | A completion failure leaves its day not clean, whatever its triage says | Gate 3 asks for a completion rate of 100% "over the accepted workload" and does not say per day |
| R3 | A day that is not covered is not clean and ends the run of days | the plan says "14 consecutive days" |
| R4 | Restart events are the fixes of adapter, glue, decoder or Rust code, however the fault was found: the fix commits of findings with those causes (and of `spec` findings whose changed side is one of them), and any file the DRI classes `restart`. Every other change under `ve/` or to the candidate surface is classed by the DRI, file by file; a commit that is not classed blocks the gate | the plan says "Any adapter or glue fix" and names no Rust fix and no change that is not a fix |
| R5 | The candidate surface is `ve/backends/`, the `ve/` modules with an `execute` call or a Lean-only handoff, `lean/VE/Service/`, `lean/Serve.lean`, `lean/checkers.lock` and the manifest's `lean_decoders`; the classed paths add the rest of `ve/` | not in the plan. The lock file stands for every change to the two checker binaries |
| R6 | An error record is the exception's `to_dict()` where it has one: the whole public record, as the baseline compares it | the plan names the classes `diagnostic-code` and `diagnostic-message`; its section 5 excludes nothing else |
| R7 | One side returning and the other raising is `verdict` and `schema`, with `budget-outcome` for `ResourceLimit` | not in the plan; today's code gives `schema` |
| R8 | `report_id` and `document_hash` are identity members. A different `verdict` of `readings` is also `composition` | plan 2.2 lists both identities; its Stage 3 puts the readings verdict under `composition` |
| R9 | A different `status` is `verdict` and `budget-outcome`, as in today's code | the plan's definition of `budget-outcome` |
| R10 | `latency` is tallied for every compared call, in a histogram with fixed bounds, and is never in a class list | "recorded with bounds reported" |
| R11 | The record gains `python_ms`, `backend_ms`, `run`, `test`, `input` and `sides` | the plan's record has six members |
| R12 | Uncompared calls are counted by reason and reported; they are outside the gate | not in the plan; stage2-progress.md records the scope gaps |
| R13 | A `lean-only` record is written for each call of a statement-layer route that has no Python implementation, at the function that hands the case to Lean | "For Lean-only operations with no Python implementation, log `python: none`". The plan does not say which operations those are |
| R14 | The registry, the floors from calibration runs that are not registered, and the nightly seed that is the date | the plan lists the corpora and says "fresh … seed nightly" |
| R15 | The nightly runs every corpus. A merge run is the corpus `suite`. A commit that needs a merge run and has no complete one leaves its day not covered, so not clean; the merge itself is never blocked | "CI runs shadow on every merge". Any exception is an amendment of the base plan (question 6) |
| R16 | The ledger is in the repository, one entry for each day, with the hashes of the run files and the first 20 records of each group | not in the plan |
| R17 | The causes `harness` and `operational` | the plan's triage rule has three cases |
| R18 | `VE_SHADOW_DIR`; an explicit `VE_SHADOW_LOG` comes first | not in the plan; today's tests use `VE_SHADOW_LOG` |
| R19 | The wording map matches exact strings for one operation at one structural path, at the eligible locations only (diagnostic text, graph-proof wording), and starts empty | "explicitly mapped for comparison" |
| R20 | No Lean statement and no Lean file | the plan's Stage 3 names none |
| R21 | The completion rate's d counts the calls in which Python ended in `ResourceLimit` | the plan's sentence has "within nominal budgets"; its budget-boundary row asks for the outcome there |
| R22 | Coverage asks for a compared call of every dispatch name in every nightly | the pointer's "every class-A operation" |

Open questions. Each is a point on which the base plan can be read in two ways or says nothing, and on which
this draft's choice may be wrong. The DRI ruling of the statement review sends questions 2, 3 and 6 to the DRI
before the first nightly, not before the build.

1. **No design debate was held on this stage.** The pipeline step asked for the converged edits of
   `debates/design-mig3/`, which does not exist. The statement review (section 13) was the first review, and
   this draft applies it. If a design debate was meant to come first, this draft is its input, not its result.
2. **The order of the open Stage 2 work** (to the DRI before the first nightly). The scope gaps of 2c, batching,
   the record wording and Rust parse diagnostics each change adapters or glue. By R4 each is a change the DRI
   classes. Classed `no-restart`, an input that is newly sent to Lean has fewer than 14 days of comparison at
   the gate. Classed `restart`, each costs the days counted so far. The base plan's calendar has stage 2c finish
   before shadow begins (its section 6), its text sets 2c's deadline at Gate 4 (its 2.3), and Gate 2 was met
   with 2c open. This draft recommends landing whatever of that list is meant to land before the first nightly,
   and asks the DRI for the order.
3. **Timeouts** (to the DRI before the first nightly). The adapters call the service with its default limit,
   which is the interactive 5 seconds (`ve/backends/lean_runner.py:92–99`; `lean_service.py:201`). Stage 2 saw
   two such timeouts in one suite run at 14 workers (stage2-progress.md, "Verification"). By R2 one of them
   costs a day. The choices are: registered runs use the batch limit of 60 seconds, which is a change to the
   candidate surface; fewer workers; or a rule that an unanswered call which is answered, and agrees, when run
   again alone is not a completion failure. This draft has no such rule.
4. **A day that is not covered.** R3 ends the run of days when the machine was down or resized. The other
   reading lets such a day count as neither clean nor not clean.
5. **The web app.** The base plan's corpus is "the web app API tests"; the plan's pointer says "real traffic
   (suite, use cases, pilots, web app)". This draft takes the base plan's words. Running a deployed web app at
   `shadow` would put people's inputs into the records (limit 11) and needs its own decision.
6. **Merge runs: whether to amend the base plan** (to the DRI before the first nightly). As specified (R15), a
   commit that needs a merge run and has no complete one leaves its day not covered, which is what "CI runs
   shadow on every merge" requires. The suite at `shadow` is at least twice the work of the suite, and the cost
   on the merge train is not measured. If that cost is too high, the way out is an explicit amendment of the
   base plan (a different merge corpus, or a merge run that is reported and does not cost the day), recorded in
   the base plan's change log; it is not a free choice of this stage.
7. **Uncompared calls and the gate.** Should Gate 3 ask that no class-A call is uncompared, which means stage 2c
   closed first? This draft reports them and does not gate on them, because the base plan puts 2c at Gate 4.
8. **Gate 4's data.** The base plan says the performance gates are "met from shadow data" (Gate 4) and that
   latency is measured "under `VE_AUTHORITY=lean`" (section 4). Shadow's durations can serve the row "per
   authority call through the service" and cannot serve an end-to-end row (limit 9). Stage 4's specification
   has to choose.
9. **Rust.** The base plan's triage rule does not name a Rust fault. R4 treats a Rust fix as a restart, because
   Rust answers inside the candidate for `evaluate` and the two searches. The other reading leaves Rust fixes
   to the DRI's classing, like any change of `checkers.lock`.
10. **Expansion work on the candidate surface.** A new statement layer has, so far, changed
    `lean/VE/Service/Standalone.lean` (the typing reductions) and so the service binary. Each such merge needs
    the DRI's class. If each is a restart, the gate cannot be met while new layers land at today's rate. If
    none is, the 14 days are not about one build. The consolidation chain's work on the route runners (trust
    map 5.1) raises the same question through `checkers.lock`.
11. **Changes to Python's class-A bodies** (resolved by the statement review). Every changed file under `ve/`
    carries a class line (2.12), so such a change is classed `no-restart` with its reason and listed in the
    report, or `restart` when it affects a candidate. The base plan's section 6 forbids new Python semantics
    since stage 2, and B1 holds the baseline.
12. **Not read, not measured.** The corpus commands; the floors; the size of the records, above all of the
    `lean-only` ones, which are written for every call; how long a nightly takes; whether the suite passes with
    `VE_AUTHORITY=shadow` set for the whole run (Z1); which tests inject a backend fault without choosing an
    authority.
13. **Which operations are Lean-only.** No one place says. The manifest calls two operations `lean-only`, and
    neither has a call site in `ve`; its entry `soft.elaborate` still says that no implementation exists in any
    engine, although the soft route exists. The statement-layer routes that the trust map describes as decided
    by Lean alone are not operations of the manifest. R13 takes the trust map's list, and the build has to find
    every function that hands a case to such a route. The trust map's list also has "norms", which the manifest
    gives a Python implementation and three adapters; this draft treats norms as class-A (2.2), not as
    Lean-only. Correcting the manifest is not part of this stage.

## 13. Changes of draft 2 (the statement review applied)

The statement review is `manage-agents/debates/mig3-spec/` (Astra and Fable, rounds 1 to 3, 2026-10-03; both
verdicts FIX; `DRI-RULING.md`: the union of both reviewers' corrections with Astra's three round-3 refinements).
Each row is one correction of the ruling and where it landed. No row changes a frozen contract, a quoted Lean
statement, a verdict, an identity, a code or a default; the §5 block is byte for byte draft 1's. Both reviewers
verify this diff before M3.1 starts.

| # | Correction (source) | Where it landed |
|---|---|---|
| 1 | The candidate is `lean=` only; without `lean=` the call is unavailable (case C), never `rust=`; `execute` runs the candidate inside `pinned("lean")`, since the search candidates reach `countermodel_check` unpinned (Astra 1; Fable round 2, 1) | D2; 2.2; 2.3 steps 2 and the last paragraph; 2.6 `lean`, `rust`; 2.14 (A); 6 row 1; 7.1; fixtures S9, S16 |
| 2 | The error record is the exception's `to_dict()`, as the baseline compares it; limit 6 ("code and message only") deleted; fixtures for `generator`, `span`, `path` (Fable 2; Astra 2) | D3; 2.4; 6 row 2; R6; limits renumbered; fixture C13 |
| 3 | The wording map is an allowlist by operation and structural path; the eligible locations are diagnostic text and graph-proof wording; every other location is rejected by `--check`; rejection fixtures for `status`, `code`, counts, an explanation `kind` and a binding identifier `local_id` (Astra round 3, 3, as ruled) | 2.4 (entries `{"op", "path", …}`, eligible locations); 4.3; R19; fixtures C3, T3 |
| 4 | Requirement (I) also fails at `certificate_replay`, `norms_certificate` and `norms_conflict`; L2 varies each argument in turn (Fable 3) | 2.6 ("nine call sites"); 6 row 3; 7.1; fixture L2 |
| 5 | The 14 static `authority_for` branches each call `note_uncompared`; fixture L12 (Fable 4) | 2.7; 6 row 10; 7.1; fixture L12 |
| 6 | What makes a day not clean is fixed by 2.10, not by the triage: zero-tolerance records, completion failures, recorder faults, missing coverage; an `unavailable` finding with `python` among its sides still needs closure; both-sides unavailability tested (Astra 6; Fable 5a) | 2.11; fixture G6 |
| 7 | The clean-day sentence: "no call that Python answered got no answer from the backend" (Fable 5b) | 0; 3.1 |
| 8 | The gate-met sentence, §0, D10 and the plan's summary no longer say "adapter or glue fix": "no restart event among the commits after `<c_first>` up to `<c>`" (Fable 5c) | 0; D10; 3.1; 3.2; plan 0 and 2 |
| 9 | n(D) is the commit of the earliest-started nightly run; the nightly is the runs at n(D); nightly runs of D at a later commit are registered runs of D under the four conditions of clean and outside coverage (Fable 6; Astra's proviso, round 2) | 2.10; fixture G20 |
| 10 | Tallies: workers register before their first shadow call (tally with `final: false`), finalize at exit; every registered worker, the agreement-only ones with no record file among them, must leave a final tally; record counts reconcile with the JSONL; a worker whose evidence writes all fail is caught on standard error; missing evidence is incomplete, whatever the floors; limit 9 replaced; fixtures for a kill before the first call, an agreement-only worker killed before finalization, and a worker whose writes all fail (Astra round 3, 1, as ruled; Fable round 2, 4) | D7; 2.6 (where records go); 2.7 (registration, reconciliation); 2.8 (`stderr.txt`, `stderr_faults`, conditions 5 to 7 and 10); 4.2; 4.3; limit 8; fixtures S20, L8, L14, L15, L16 |
| 11 | Day finalization: `day <D>` exits 2 before D ends or while a registered run of D lacks `finished`; the entry records `written`; `--check` rejects a `written` before D's end or before a run's `finished` (Astra 5; Fable round 2, 5) | D8; 2.10 ("final"); 3.1; 4.3; section 9 ("finality"); fixtures G18, G19 |
| 12 | Floors come from calibration runs, manual and not registered, meeting every condition but the floors; the calibration commit writes each corpus's `command` and floors before the first registered run (Astra 7; Fable round 2, 6) | 2.8; 2.9 (`calibration`); 7.1; R14; plan M3.3 |
| 13 | Merge coverage: every commit after the previous nightly's commit up to n(D) that needs a merge run has a complete one, else D is not covered; the merge is never blocked; question 6 becomes whether to amend the base plan (Astra 8; Fable round 3) | D8; 2.10 (covered, condition 3); 3.1; section 9; R15; question 6; fixture G17 |
| 14 | Restart and classing: the candidate surface is `ve/backends/`, the `ve/` modules with an `execute` call or a Lean-only handoff, the glue, `checkers.lock` and the manifest's `lean_decoders`; every changed file under `ve/` or on the surface carries a class line, decided from `git diff --name-only`; a fix of adapter, glue, decoder or Rust code restarts however found and wherever it lives, `spec` findings included; `no-restart` is for a change that fixes nothing of the candidate and changes no candidate's answer; G8 cases for a candidate-affecting `ve/wire.py` fix and a Python-only fix (Fable 1 and round 3 (a), (b); Astra round 3, 2, as ruled; Fable's minor edit on `spec`) | D10; 2.11 (last paragraph); 2.12; 3.1; 3.2; 7.2; section 9; R4; R5; question 11; limit 14; fixtures G8, G8b, G21 |
| 15 | `run.json` records the `ve-webapp` commit (Fable, minor) | 2.8 (`webapp_commit`) |
| 16 | A `lean-only` record is one per case for the batch handoffs (Fable, minor) | 2.2; 2.6; 7.1; fixture S18 |
| 17 | Questions 2, 3 and 6 go to the DRI before the first nightly, not before the build (both reviewers; the ruling) | 12 (preamble, questions 2, 3, 6); plan 6 and 8 |
