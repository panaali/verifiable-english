# Semantics migration, stage 3: shadow mode (statement specification)

> Status: statement specification, draft 1 (2026-10-03), branch `design/mig3` from `main` at `a093a14d`. This is
> the item-1 statement spec of [mig3-PLAN.md](mig3-PLAN.md) draft 2 (the **plan**). Item 1 is Stage 3 of
> [SEMANTICS-MIGRATION-PLAN.md](SEMANTICS-MIGRATION-PLAN.md), revision 3 (the **base plan**): its section "Stage 3:
> shadow mode" with Gate 3, and the parts of its sections 4 and 5 that Stage 3 names. **No debate was held on this
> stage.** The directory `manage-agents/debates/design-mig3/` that the pipeline step names does not exist, so there
> were no converged edits to apply and none is invented (plan, status paragraph). The only converged debate on the
> subject is the base plan's (`manage-agents/debates/semantics-migration/{fable,astra}.md`, CONVERGED after round
> 3), and its edits are already in revision 3. The Astra + Fable statement review of this file is therefore the
> first review of everything here that the base plan does not fix; section 12 lists those choices and the open
> questions. Fixtures are implementation obligations, not claims of completed tests. Nothing was built or run for
> this draft. Every `file:line` reference was read at `eb96d5ed` and must be re-read at each step; every number
> quoted from another document is that document's. Nothing here changes a verdict, an identity, a code, a frozen
> contract, a default authority, a Lean file or a theorem statement.

## 0. Scope, one paragraph

Gate 2 is met: every class-A operation has an adapter, and the suite passes under `VE_AUTHORITY=lean`
([stage2-progress.md](stage2-progress.md)). Python is still the default authority for 24 of the 26 operations of
the assurance manifest (`docs/TRUST-MAP.md` on branch `docs/trust-map`, section 1). Stage 3 changes no default. It
runs the base plan's corpora under the authority `shadow`: each call of a class-A operation runs Python and the
adapter that would answer under Lean authority, returns Python's result, and writes a record when the two differ.
A day is clean when every corpus ran and no compared call differed in a zero-tolerance class or failed to
complete on the backend. Gate 3 is 14 clean days in a row with no adapter or glue fix among them. This
specification fixes what a shadow call does, how two results are compared and classed, what is written, what a
run, a day and the count of days are, how a finding is triaged, and what the Gate 3 report states. The switch of
the default (Stage 4) is not specified here.

In this specification: the decisions (1), the definitions (2), the English, one reading each (3), the diagnostics
(4), the Lean statements relied on (5), where the code stands against the base plan (6), the files and gates of
the build (7), the acceptance fixtures (8), Gate 3 (9), limits (10), the statement review checklist (11), and the
choices this specification resolves with the open questions (12).

## 1. Decisions

| # | Decision | Where |
|---|---|---|
| D1 | A shadow call returns the object Python returns, or raises the exception Python raises. Nothing in the comparison or the recording can change that | 2.3 |
| D2 | The candidate of a shadow call is the adapter that answers the operation under `VE_AUTHORITY=lean`. Where that adapter uses Rust, Rust's part is inside it | 2.2, 2.3 |
| D3 | Two results are compared after the base plan's comparison projection: `checker_build` and `record_id` are dropped, a mapped wording counts as equal, and nothing else is excluded | 2.4 |
| D4 | There are ten classes, the base plan's: eight at zero tolerance, two recorded with bounds reported | 2.5 |
| D5 | There are four kinds of record: `divergence`, `unavailable`, `lean-only` and `recorder-fault`. A `lean-only` record is how "`python: none`" is logged | 2.6 |
| D6 | A call that an adapter routes to Python without a candidate is counted, with its reason, and reported. It is outside what the gate shows | 2.7 |
| D7 | A run is one corpus at one commit of `main`. The corpora are the base plan's list, in a registry with floors | 2.8, 2.9 |
| D8 | A day is clean when every corpus has a complete run in its nightly, every class-A operation was compared, and no registered run of the day has a zero-tolerance record, a completion failure or a recorder fault | 2.10 |
| D9 | Every zero-tolerance record, every unavailable call and every recorder fault is a finding with one cause. The causes `python`, `glue` and `spec` carry the base plan's triage rule word for word | 2.11 |
| D10 | The count of clean days goes back to zero at the merge of an adapter or glue fix. Every other change to the candidate surface is classed by the DRI, with a reason, before the gate can be met | 2.12 |
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
build fixes the full list (section 12, question 13).

The **candidate** of a shadow call is the function passed as `lean=`; where none is passed, the function passed
as `rust=`. That is the function `execute` calls when the authority is `lean` (`dispatch.py:163–166`), so the
candidate is the code that would answer after the switch. Today every call of the table passes `lean=`.

A candidate is not always an independent implementation. Read at `eb96d5ed`:

- `evaluate`: Rust evaluates; Lean evaluates the same formulas, and a different value is `CheckerUnavailable`.
  When Rust ends in `ResourceLimit`, Rust's result is the answer (`ve/evaluate.py:265–273`).
- `countermodel_search`, `distinguishing_model`: the function passed as `lean=` is the Rust search, whose witness
  goes through `countermodel_check` (`ve/search.py:711–715, 737, 901`).
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
2. Run the candidate. Its outcome is *returned(w)* or *raised(f)*, or *no adapter* when the call passes neither
   `lean=` nor `rust=`. The candidate runs whatever Python's outcome is.
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
It is a shadow call of its own, with its own record and tally. Inside a candidate, `dispatch.pinned` sets the
authority to `lean`, so no shadow call happens there (`dispatch.py:36–46`; `pinned("shadow")` is refused).

### 2.4 What is compared

The **public record** of a returned value is `_record` of it: `to_dict()` where the value has one, the fields of
a dataclass, and dictionaries, lists and tuples member by member, a tuple as a list (`dispatch.py:73–82`).

The **error record** of a raised exception `e` is `{"code": c, "message": str(e)}`, where `c` is `e.code` if `e`
has one and the name of `e`'s type otherwise (`dispatch.py:177–178`).

The **comparison projection** is applied to both records before they are compared:

1. Every member named `checker_build` or `record_id` is removed, at any depth. This is the function
   `baseline_projection` (`tests/probe_matrix.py:146–153`); shadow and the baseline use one definition of it,
   not two copies.
2. A **mapped wording** counts as equal. The wording map is the file `conformance/shadow/wording.json`, a list
   of entries `{"op", "key", "python", "backend", "reviewed"}`. Where the two records of operation `op` have, at
   the same place and under the member name `key`, the string `python` on Python's side and the string `backend`
   on the candidate's side, the two strings count as equal. The strings are matched exactly; an entry has no
   pattern. `reviewed` names the commit or document of the review.

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
| `lean` | the candidate's record, before the projection, when the candidate was passed as `lean=`; otherwise `null` |
| `rust` | the candidate's record when the call passed only `rust=`; otherwise `null` |
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
different inputs have different payloads. Six call sites do not meet it today (section 6, row 3).

When each kind is written:

| Kind | Written when | Notes |
|---|---|---|
| `divergence` | case A or B, and the class set is not empty | |
| `unavailable` | case C or D | for *no adapter*, `lean` is `{"code": "CheckerUnavailable", "message": "no adapter for <op>"}`, as today (`dispatch.py:183`) |
| `lean-only` | a Lean-only call (2.2) is made while the variable `VE_AUTHORITY` is `shadow` | `python` is `null`, which is how `none` is written in JSON; `lean` is what Lean answered; the call returns or raises as it does today. It is not a comparison and belongs to no class |
| `recorder-fault` | step 3 of 2.3 raised an `Exception` | written if it can be; counted in the tally in any case |

A **completion failure** is an `unavailable` record whose `sides` is `["backend"]`: Python gave an outcome and
the backend gave none.

Where records go:

- If `VE_SHADOW_LOG` is set, records are appended to that file, as today, and nothing is tallied. With no record
  to write, the file is not created (`tests/test_stage2_evaluation.py:220–226`).
- Otherwise, if `VE_SHADOW_DIR` is set, it names a directory. Each process appends its records to a file of its
  own there, `records-<pid>-<nonce>.jsonl`, and writes its tally to `tally-<pid>-<nonce>.json` (2.7).
- Otherwise records are appended to `ve-shadow.jsonl` in the working directory, as today.

A record is written with one write on a file opened for appending, and is flushed before the shadow call
returns. A crash after the call therefore does not lose it.

### 2.7 Tallies, and calls that are not compared

A **tally** is one JSON object per process. For each operation it holds these counts:

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

A tally file is replaced as a whole, never written in part. It is written when the process exits and after
every 1,000 shadow calls. A process that is killed can therefore miss calls in its tally. It cannot miss a
record: 2.6 writes every record before its call returns.

An **uncompared call** is a call of a class-A entry, at the authority `shadow`, that the adapter answers from
Python without a candidate because the input is a scope gap (`ve/parser.py:382–383` is one such branch). Before
it runs Python, the adapter calls `dispatch.note_uncompared(op, reason)`. That function only counts, and only at
the authority `shadow`; it never raises. The reasons are names in a table in `ve/backends/dispatch.py`, one for
each condition that routes an input to Python statically, each with one sentence. Every scope gap of
stage2-progress.md that is routed this way has a reason. A reason that is not in the table is counted under
`unregistered` and is a recorder fault.

A scope gap whose adapter does call `execute`, with a candidate that keeps Python's rule (coupled reading sets,
joint choices), is a compared call, not an uncompared one (limit 4 of section 10).

### 2.8 A run

A **run** is one execution of one corpus (2.9) by `tools/shadow_run.py --corpus <id> --out <directory>`, in a
clean checkout of one commit, with `VE_AUTHORITY=shadow`, `VE_AUTHORITY_OVERRIDES` unset, `VE_SHADOW_LOG` unset,
`VE_SHADOW_DIR` the run's directory and `VE_SHADOW_RUN` the run's name. The name is the corpus id, the first
twelve digits of the commit and the start time. The directory then holds the record files, the tally files and
`run.json`:

```json
{"run": "suite-eb96d5ed0000-20261004T000500Z", "corpus": "suite", "commit": "<40 hex>", "trigger": "nightly",
 "started": "2026-10-04T00:05:00Z", "finished": "2026-10-04T03:10:00Z", "exit": 0, "cases": 4478,
 "builds": {"ve_service": "<64 hex>", "rust_jsonl": "<64 hex>"}, "seed": null}
```

`trigger` is `nightly`, `merge` or `manual`. `builds` holds the SHA-256 of the two checker binaries the run
loaded. `seed` is set for a corpus that takes one.

A run is **complete** when all of these hold:

1. `exit` is the corpus's `expected_exit`.
2. The checkout was clean, at `commit`, when the run started and when it finished.
3. Both hashes of `builds` are pinned in `lean/checkers.lock` at `commit` (its keys `ve_service` and
   `rust_jsonl`).
4. Every line of every record file is a record, and every tally file is a tally.
5. The run has no recorder fault.
6. `cases` is at least the corpus's `min_cases`, and the run's `compared` is at least its `min_compared`.
7. For a corpus with a seed, `seed` is the seed of 2.9.

A run is **registered** when its trigger is `nightly` or `merge` and its commit is a first-parent commit of
`main`. Only registered runs count towards a day. A manual run is evidence for triage and for nothing else.

### 2.9 The corpora

The registry is `conformance/shadow/corpora.json`: a list of entries `{"id", "plan", "command", "expected_exit",
"min_cases", "min_compared", "merge"}`. `plan` quotes the base plan's words for the corpus. The ids, from the
base plan's list (its Stage 3, "Corpora"):

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

Every `min_compared`, and every `min_cases` marked "measured", is the value of the corpus's first complete run,
written into the registry by a reviewed commit. A floor changes only by a reviewed commit that says why.

The seed of `fuzz-nightly` for the day D is the integer written as the eight digits of D, year, month, day
(`20261012` for 12 October 2026). The committed fuzz seeds have this form (`conformance/README.md:164, 208`), so
anyone can run a day's fuzz again.

Only `suite` has `"merge": true`. Each corpus's command is read from the repository at the build; this draft
has not read them (section 12, question 12).

### 2.10 A day

A **day** is a UTC calendar date. A run belongs to the day of its `started`.

The **nightly** of a day D is the set of registered runs with the trigger `nightly` that started on D, all at
one commit, written **n(D)**: the head of `main` when the first of them started.

A **merge run** is a registered run with the trigger `merge`: the corpus `suite`, at a first-parent commit of
`main` that changes a file outside `docs/` and `conformance/shadow/`. The merge train starts it after the
commit's gate (`tools/gate.py`) passes.

D is **covered** when:

1. the nightly of D has a complete run of every corpus of the registry, at n(D); and
2. every dispatch name of 2.2 has `compared` of at least 1, summed over the nightly.

D is **clean** when D is covered and, over every registered run that started on D:

1. every run is complete;
2. there is no zero-tolerance record;
3. there is no completion failure; and
4. there is no recorder fault.

A day with no nightly is not covered, and so not clean.

The **ledger entry** of D is `conformance/shadow/ledger/<D>.json`, written by `tools/shadow_gate.py day <D>`. It
holds, for each registered run of D, the members of `run.json`, whether the run is complete, its tally summed
over its processes, and the SHA-256 of each of its files. It also holds the sums for each operation, the two
answers `covered` and `clean` with the reasons of 3.1, and, for each group of records with the same operation,
kind and class list, the number of records and the first 20 of them. The entry is committed to `main` in a
commit that changes nothing outside `conformance/shadow/`. The run directories are kept outside the repository
for the length of the stage.

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

Whatever its cause, a finding leaves its day not clean (2.10). A `spec` finding whose note changes what a
supported input returns is also a product decision of base plan 2.3: implemented in Python first, with a release
note. No difference is exempt as "by design" (base plan, stage 0).

### 2.12 The count, and restart events

The **candidate surface** is these paths: `ve/backends/`, `lean/VE/Service/`, `lean/Serve.lean` and
`lean/checkers.lock`. A first-parent commit of `main` **changes the candidate surface** when the difference
between it and its first parent has a file of those paths.

A **restart event** is a first-parent commit of `main` that is either

- (a) the fix commit of a triage entry whose cause is `adapter`, `glue` or `rust`; or
- (b) a commit that changes the candidate surface and that the DRI has classed `restart`.

The classing file is `conformance/shadow/changes.json`: a list of entries `{"commit", "class", "reason",
"signed"}`, with `class` `restart` or `no-restart`. Every commit that changes the candidate surface and is not a
restart event by (a) needs an entry. `no-restart` is for a change that fixes nothing that shadow found; the
reason says what the change is.

The **count** on a day D is the largest number k for which:

1. each of the k days that end with D is clean; and
2. no restart event, and no commit that changes the candidate surface without an entry, is among the first-parent
   commits after n(F) up to and including n(D), where F is the first of those k days.

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
  authority `lean` (2.2).
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
| a clean day | `On <date>, every corpus ran in shadow at commit <c>, and no compared call differed in a zero-tolerance class or failed to complete on the backend.` | that Python and the backend agree on other inputs; that either result is correct |
| a day that is not clean | `<date> is not a clean day: <reason>.` | that the backend was wrong |
| the count | `The count of clean days in a row is <k>, from <first date> to <last date>.` | that the days before <first date> were not clean |
| a restart | `The count went back to zero at commit <c>: <reason>.` | that the commit was a mistake |
| the gate, met | `Gate 3 is met on <date> at commit <c>: the 14 days from <first date> to <date> are clean, no adapter or glue fix was merged after the nightly of <first date> started, and every finding is closed.` | that the default authority has changed, or may change without Gate 4 |
| the gate, not met | `Gate 3 is not met on <date>: <reason>.` | |
| completion | `Of <d> calls that Python completed, the backend completed <n> with the same outcome.` | that every call completed in Python |
| uncompared calls | `<n> calls of <op> were answered by Python alone, because the adapter does not take the input (<reason>). They were not compared.` | that these calls would have agreed |
| Lean-only calls | `<n> calls of <op> have no Python implementation. Lean answered them, and nothing was compared.` | that Lean's answers were checked against anything |
| a finding | `Finding <id>: on <date>, <op> gave a different result in Python and on the backend (<classes>). Cause: <cause>.` and then `Fixed by <commit>.` or `Open.` | which side was right, unless the cause says so |
| an unavailable call | `Finding <id>: on <date>, a call of <op> got no answer from <side> (CheckerUnavailable): <message>. Cause: <cause>.` | that the side is not installed |

The reasons of a day that is not clean, one line each:

- `the corpus <id> has no complete run in the nightly`
- `the operation <op> has no compared call in the nightly`
- `the run <run> is not complete: <condition of 2.8>`
- `<n> compared calls differ in a zero-tolerance class`
- `<n> calls completed in Python and got no answer from the backend`
- `<n> recorder faults`

The reasons of a restart: `it fixes finding <id> (<cause>)`, or `the DRI classed it as a restart: <reason>`.

The reasons of a gate that is not met: `the count is <k>, and 14 are needed`; `finding <id> is open`;
`commit <c> changes the candidate surface and is not classed`.

### 3.2 Wordings this replaces, and why

Each wording on the left was used for this stage, in the base plan, in the plan's pointer or in talk about it,
and has two readings.

| Wording | Its two readings | Written instead |
|---|---|---|
| "Shadow ran clean for 14 days." | no record was written for 14 days, which is also true when nothing ran; or every corpus ran on each day and no call differed | the sentences for a clean day and for the count |
| "Zero divergences." | no record of any class; or none in a zero-tolerance class | "No compared call differed in a zero-tolerance class. <n> compared calls differed in message text only." |
| "Lean and Python agree." | on every input, or on the compared calls of the corpora; and Lean alone, or Lean with Rust inside the adapter | "On <n> compared calls, the result under Lean authority equals Python's result after the comparison projection." |
| "on real traffic (suite, use cases, pilots, web app)" (the plan's pointer) | calls from people who use a deployed program; or the corpora of the base plan, among them the web app's API tests | "Every corpus of the registry runs in shadow. No call from a person using a deployed program is among them." |
| "Any adapter or glue fix restarts the clock." | any change to adapter or glue code; or a change that fixes a finding | "The count goes back to zero when a fix of a finding whose cause is the adapter, the Lean glue, a Lean decoder or Rust is merged. Every other change to the candidate surface is classed by the DRI, with a reason." |
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
| a record cannot be written (no space, no permission) | Python's outcome | one line on standard error for the process, `ve shadow: cannot write records: <text>`; `recorder_faults` + 1 |

### 4.3 The tools

`tools/shadow_run.py` exits with the corpus command's own status. It prints one line when the run is not
complete: `run <run> is not complete: <condition>`.

`tools/shadow_gate.py` has three commands. `day <date>` writes the ledger entry and prints the sentence for a
clean day or the sentences for a day that is not clean. `gate <date>` prints the count, the gate's sentence and
the report of section 9. `--check` reads the committed files and prints nothing when they are well formed and
each ledger entry's `covered` and `clean` follow from its own rows.

| Exit | Meaning |
|---|---|
| 0 | the day is clean; the gate is met; `--check` found nothing |
| 1 | the day is not clean; the gate is not met |
| 2 | a file is malformed, or a ledger entry does not follow from its rows. The line names the file and the member: `ledger entry <date> does not match its runs: <member>` |

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
| 1 | "runs Python and Lean/Rust on every semantic call, returns Python's result" | `execute` does this for a call that reaches it (`dispatch.py:172–200`). The comparison and the write are not guarded: an exception in `_classes` or `_append` reaches the caller | V1 (2.3) |
| 2 | "appends a divergence record `{op, input_digest, python, lean, rust, class}`" | written, with `python_ms` and `backend_ms`, and only when the two differ (`dispatch.py:192–197`) | `kind` and the other members of 2.6 |
| 3 | `input_digest` | six call sites pass a constant payload, so every input has one digest: `{"kind": "readings"}` (`readings.py:472–479`), `{"kind": "model"}` (`model.py:98`, `background.py:267`), `{"kind": "environment"}` (`environment.py:312`), `{"kind": "graph"}` (`argument.py:581`), `{"kind": "bundle"}` (`bundle.py:148`), `{"kind": "parse"}` (`parser.py:384`) | requirement (I) |
| 4 | "For Lean-only operations … log `python: none` outside the divergence classes" | absent | the `lean-only` record |
| 5 | the ten classes | `_classes` (`dispatch.py:85–139`) has rows 1 to 9 of 2.5 without the `readings` half of row 4 and without `report_id` and `document_hash`. It applies no projection, so a different `checker_build` is `schema`. One side returning and the other raising falls to `schema`. A candidate that raises `CheckerUnavailable` is classed as a difference | 2.4, 2.5 |
| 6 | the corpora; "CI runs shadow on every merge"; "a fresh 5,000-case seed nightly" | absent | 2.8 to 2.10; `tools/shadow_run.py` |
| 7 | "the completion rate of section 4 is 100%"; "public-count parity and latency reports attached" | nothing is counted when the two sides agree, so no rate, parity or latency can be stated | the tallies |
| 8 | "Zero divergences in the zero-tolerance classes on all corpora for 14 consecutive days" | absent | 2.10, 2.12; `tools/shadow_gate.py` |
| 9 | the triage rule; "Any adapter or glue fix restarts the 14-day clock" | absent | 2.11, 2.12 |
| 10 | — | calls routed to Python statically leave no trace (`parser.py:382–383`, `ast.py:336`, `environment.py:303–311`, `readings.py:465–466`) | `note_uncompared` |

Stage 2 work that is still open and changes the candidate surface when it lands (stage2-progress.md, its last
list): the scope gaps of stage 2c, due before Gate 4; the argument record's wording and the four provenance
members; batching; Rust parse diagnostics; the manifest's bindings for the service adapters. Section 12,
question 2, is about their order.

## 7. The build: files and gates

### 7.1 Diff scope

| Changed or added | By |
|---|---|
| `ve/backends/dispatch.py` | 2.3 to 2.7 |
| the modules that call `execute` (the third column of 2.2) | the payloads of requirement (I) and the calls of `note_uncompared`, and nothing else. No statement that computes a Python result changes |
| the functions through which `ve` hands a case to a statement-layer route (2.2), in `ve/backends/lean.py` and wherever else the build finds one | the `lean-only` record, and nothing else |
| `tools/shadow_run.py`, `tools/shadow_gate.py` | new |
| `conformance/shadow/corpora.json`; `wording.json`, `triage.json` and `changes.json`, each the empty list; `ledger/` | new |
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
| S9 | the call passes neither `lean=` nor `rust=` | an `unavailable` record whose `lean` is `{"code": "CheckerUnavailable", "message": "no adapter for <op>"}`; `sides` `["backend"]` |
| S10 | Python raises `CheckerUnavailable`; the candidate returns | raises Python's exception; an `unavailable` record with `sides` `["python"]`; `unavailable_other` 1, `completion_failures` 0 |
| S11 | both raise `CheckerUnavailable` | one record with `sides` `["backend", "python"]`; `unavailable_other` 1 |
| S12 | the candidate returns a value whose comparison raises `RuntimeError` | returns Python's object; `recorder_faults` 1; a `recorder-fault` record |
| S13 | `VE_SHADOW_DIR` names a directory that cannot be written; the two sides differ | returns Python's object and raises nothing; standard error has the line of 4.2 |
| S14 | Python raises `KeyboardInterrupt` | it leaves `execute`; the candidate is not run. The same with the candidate raising it |
| S15 | the authorities `python`, `lean` and `rust-experimental`, each with two sides that differ | the directory stays empty; the result is that side's, as today; with no `lean=` at `lean`, `CheckerUnavailable` (`tests/test_stage2_dispatch.py:28–31`) |
| S16 | the `python` function of an operation A calls `execute` for an operation B; A's candidate calls `execute` for B inside `pinned("lean")` | the tally has `compared` 1 for A and 1 for B: the call inside the candidate is not a shadow call |
| S17 | `VE_SHADOW_LOG` names a file and `VE_SHADOW_DIR` is also set; first two sides that differ, then two that agree | the record is in the file and the directory stays empty; with the two that agree alone, the file is not created |
| S18 | one case is handed to the soft route through `run_soft_case`, with `VE_AUTHORITY=shadow` and the Lean binaries built; then the same with `VE_AUTHORITY` unset | returns the row it returns at the default authority; one record of the kind `lean-only` with `python` `null`, class `[]` and the route executable's name as `op`; `lean_only` 1. With the variable unset: no record |
| S19 | `note_uncompared("parse", r)` for a reason `r` of the table, at `shadow`; then at `python`; then with a reason that is not in the table, at `shadow` | `uncompared[r]` is 1 and there is no record; nothing; `uncompared["unregistered"]` 1 and `recorder_faults` 1, and nothing is raised |

### 8.2 The classes and the projection

Both sides return; the operation is `evaluate` unless the row names one.

| Case | The two records differ in | Expected class list |
|---|---|---|
| C1 | `checker_build` at the root, and `record_id` two levels down | none: `agree` |
| C2 | `graph_id`; then `report_id` | `["identity"]`, both times |
| C3 | operation `graph`, key `proof`, `"Python replay checked"` against `"Lean graph report checked"`, with that entry in the wording map; then without the entry; then with the entry and the operation `bundle` | none; `["schema"]`; `["schema"]` |
| C4 | a `kind` inside `explanation.children`, and an item of `composition.supporting_edge_ids` (`tests/test_stage2_dispatch.py:63–72`) | `["composition", "explanation"]` |
| C5 | `verdict`, `"ALL"` against `"SOME"`: operation `readings`; then operation `compare` | `["composition", "verdict"]`; `["verdict"]` |
| C6 | the length of `assumptions`; then the length of `values`, with equal items in the common part | `["composition", "schema"]`; `["schema"]` |
| C7 | `value`, `true` against `1` | `["schema"]` |
| C8 | `evaluations`, 3 against 4, at the root; then inside `explanation` | `["count-value"]`; `["explanation"]` |
| C9 | `detail`; then `generator` | `["diagnostic-message"]`; `["diagnostic-code"]` |
| C10 | a member `foo` with two values; then a member `foo` on one side only | `["schema"]`, both times |
| C11 | `status` and `message` | `["budget-outcome", "diagnostic-message", "verdict"]` |
| C12 | the projection of every output of the baseline, by shadow's function and by `baseline_projection` | equal on every cell |

### 8.3 Records, tallies and runs

| Case | Input | Expected |
|---|---|---|
| L1 | the record of S2, read as bytes | one line; keys in sorted order; no space after `:` or `,`; a newline at the end; the members are those of 2.6 for its kind and no others |
| L2 | for each dispatch name of 2.2: two real calls with different inputs, each with a candidate replaced so that it differs | the two records have different `input_digest` |
| L3 | a payload of 65,536 bytes in canonical JSON; then one of 65,537 | `input` is the payload; `input` is `null`, and `input_digest` is set |
| L4 | two processes, one shadow call each, one directory | two record files and two tally files; the sums are 2 |
| L5 | three compared calls whose backend durations are set to 0.05, 3 and 7,000 milliseconds | one each in the cells 0.1, 5 and the cell above 5,000; smallest 0.05, largest 7,000 |
| L6 | Python's record holds a `bytes` value; the two sides differ | the line is JSON; the member is `"<unserializable bytes>"` |
| L7 | a process is killed with `SIGKILL` after a shadow call with a difference has returned | the record is in the file, as a whole line |
| L8 | a run directory with, in turn: `exit` 1; a hash that `checkers.lock` lacks; half a line at the end of a record file; `recorder_faults` 1; `cases` below the floor; `compared` below the floor; the wrong seed | not complete each time, with that condition named |
| L9 | the corpus `baseline` at `shadow`, with the parity tool's observer | every probe cell has a compared call, or an uncompared call, or is in the parity tool's class "same, python"; the build reports the three numbers |
| L10 | one input for each scope gap that 2.7 gives a reason; one coupled reading set | the tally has `uncompared` 1 under that reason, and no record; the coupled set is a compared call |
| L11 | the first arguments of all calls of `execute` in `ve/`, found by a scan of the syntax trees | the 23 names of 2.2 |

### 8.4 Days, the count and the gate

On ledgers and a commit history made for the test. The days are numbered 1 to 14; unless a row says otherwise
every day is clean, no commit changes the candidate surface, and no finding is open.

| Case | Input | Expected |
|---|---|---|
| G1 | as stated | the count on day 14 is 14; `gate` prints the sentence for the gate met and exits 0 |
| G2 | days 2 to 14 only | the count on day 14 is 13; `the count is 13, and 14 are needed`; exit 1 |
| G3 | on day 7 the corpus `english` has no complete run | day 7 is not clean, with the first reason of 3.1; the count on day 14 is 7 |
| G4 | on day 7 a merge run has one zero-tolerance record | day 7 is not clean; the count on day 14 is 7 |
| G5 | on day 7 one record with class `["diagnostic-message"]` | day 7 is clean; the count on day 14 is 14 |
| G6 | on day 7 one completion failure; then, in its place, one `unavailable` record with `sides` `["python"]` and a closed entry | not clean, and the count on day 14 is 7; clean, and the gate is met |
| G7 | the fix of a finding with cause `adapter` is merged on day 5: after n(5); then before n(5) | the count on day 14 is 9; then 10 |
| G8 | a commit before n(9) changes `lean/VE/Service/Graph.lean`: with no entry in `changes.json`; with `no-restart`; with `restart` | `commit <c> changes the candidate surface and is not classed`, exit 1; the gate is met; the count on day 14 is 6 |
| G9 | a finding of day 0 has an entry with no cause | `finding <id> is open`; exit 1 |
| G10 | the fix of a finding with cause `python` is merged on day 10 | the count on day 14 is 14 |
| G11 | the ledger entry of day 3 says `clean` and one of its run rows has `zero_tolerance` 1 | exit 2, with the line of 4.3 |
| G12 | day 7 has no nightly | day 7 is not clean; the count on day 14 is 7 |
| G13 | on day 7 the operation `distinguishing_model` has `compared` 0 in the nightly | day 7 is not covered, with the second reason of 3.1 |
| G14 | on day 7 the run of `fuzz-nightly` has the seed of day 6 | that run is not complete; day 7 is not clean |
| G15 | on day 7 a manual run has a zero-tolerance record | the ledger entry of day 7 does not hold it; day 7 is clean |
| G16 | a commit that changes only `conformance/shadow/ledger/` | it needs no merge run and no entry in `changes.json` |

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
| T3 | `corpora.json` without the corpus `english`; `triage.json` with a cause `unknown`; `changes.json` with a class `maybe` | exit 2 each time, with a line that names the file and the member |

## 9. Gate 3

The DRI reviews one report, made by `tools/shadow_gate.py gate <date>` and stored at the end of
`docs/spec/stage3-progress.md`. Astra and Fable read it before any step of Stage 4. The tool judges each row
from the ledger, the triage file, the classing file and the commit history, not from a stated summary.

| Row | Definition | Required |
|---|---|---|
| the count | 2.12, on the day of the report | at least 14 |
| coverage | each of the 14 days is covered (2.10) | all 14 |
| zero-tolerance classes | zero-tolerance records in the registered runs of the 14 days | 0 |
| completion | completion failures in those runs; the rate of 2.13 | 0; n is d |
| recorder faults | in those runs | 0 |
| findings | findings since the first registered run that are not closed | 0 |
| the candidate surface | among the first-parent commits after the first day's nightly commit, up to the last day's: restart events; commits that change the surface and are not classed | 0; 0 |
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
| merge runs | the commits of the 14 days that needed a merge run and have none |
| the classed changes | every entry of `changes.json` for the 14 days, with its reason |

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
6. **A rejection is compared by code and message only.** The path and the span of an error are not compared.
7. **A test that sets its own authority is not shadowed** inside that test.
8. **The ledger is as good as the process that writes it.** The hashes make an entry checkable against the run
   directories. Nothing proves that a run happened, or that its directory was not edited before it was hashed.
9. **A process that writes nothing leaves no trace.** The floors of 2.9 bound this; they do not exclude it.
10. **Shadow latency is not the latency of the switch.** Both sides run one after the other in one process. The
    end-to-end rows of the base plan's section 4 are measured under `VE_AUTHORITY=lean`, by that section's
    method.
11. **One fault can give several records**: one for a constituent and one for the operation that composes it.
12. **Records hold inputs.** `input` and the two result records can hold the text of the corpus. That is the
    project's own test material today. It would be a person's text if a deployed program ever ran at `shadow`.
13. **Gate 3 is about one commit.** A change to the candidate surface after n(D) is not covered by a gate met on
    D. Stage 4's specification has to say what such a change does to the switch.
14. **Cost.** A compared call runs Python and the candidate. An operation that composes others runs its
    constituents three times: once in Python, once as their own candidates, once inside its candidate. How long
    a nightly takes is not known.

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
restarts the clock; Gate 3. Everything below is this specification's own choice. No debate decided any of it.

| # | Choice | Relative to the base plan |
|---|---|---|
| R1 | Records have a `kind`. An unanswered call is a record of the kind `unavailable`, not an eleventh class | the plan names ten classes and asks, in its section 4, that every `CheckerUnavailable` be triaged |
| R2 | A completion failure leaves its day not clean, whatever its triage says | Gate 3 asks for a completion rate of 100% "over the accepted workload" and does not say per day |
| R3 | A day that is not covered is not clean and ends the run of days | the plan says "14 consecutive days" |
| R4 | Restart events are the fixes of findings with the causes `adapter`, `glue` and `rust`. Any other change to the candidate surface is classed by the DRI; one that is not classed blocks the gate | the plan says "Any adapter or glue fix" and names no Rust fix and no change that is not a fix |
| R5 | The candidate surface is `ve/backends/`, `lean/VE/Service/`, `lean/Serve.lean` and `lean/checkers.lock` | not in the plan. The lock file stands for every change to the two checker binaries |
| R6 | An error record has `code` and `message` only, as in today's code | the plan names the classes `diagnostic-code` and `diagnostic-message` |
| R7 | One side returning and the other raising is `verdict` and `schema`, with `budget-outcome` for `ResourceLimit` | not in the plan; today's code gives `schema` |
| R8 | `report_id` and `document_hash` are identity members. A different `verdict` of `readings` is also `composition` | plan 2.2 lists both identities; its Stage 3 puts the readings verdict under `composition` |
| R9 | A different `status` is `verdict` and `budget-outcome`, as in today's code | the plan's definition of `budget-outcome` |
| R10 | `latency` is tallied for every compared call, in a histogram with fixed bounds, and is never in a class list | "recorded with bounds reported" |
| R11 | The record gains `python_ms`, `backend_ms`, `run`, `test`, `input` and `sides` | the plan's record has six members |
| R12 | Uncompared calls are counted by reason and reported; they are outside the gate | not in the plan; stage2-progress.md records the scope gaps |
| R13 | A `lean-only` record is written for each call of a statement-layer route that has no Python implementation, at the function that hands the case to Lean | "For Lean-only operations with no Python implementation, log `python: none`". The plan does not say which operations those are |
| R14 | The registry, the floors, and the nightly seed that is the date | the plan lists the corpora and says "fresh … seed nightly" |
| R15 | The nightly runs every corpus. A merge run is the corpus `suite`. A missing merge run is reported and does not by itself cost the day | "CI runs shadow on every merge" |
| R16 | The ledger is in the repository, one entry for each day, with the hashes of the run files and the first 20 records of each group | not in the plan |
| R17 | The causes `harness` and `operational` | the plan's triage rule has three cases |
| R18 | `VE_SHADOW_DIR`; an explicit `VE_SHADOW_LOG` comes first | not in the plan; today's tests use `VE_SHADOW_LOG` |
| R19 | The wording map matches exact strings for one operation and one key, and starts empty | "explicitly mapped for comparison" |
| R20 | No Lean statement and no Lean file | the plan's Stage 3 names none |
| R21 | The completion rate's d counts the calls in which Python ended in `ResourceLimit` | the plan's sentence has "within nominal budgets"; its budget-boundary row asks for the outcome there |
| R22 | Coverage asks for a compared call of every dispatch name in every nightly | the pointer's "every class-A operation" |

Open questions. Each is a point on which the base plan can be read in two ways or says nothing, and on which
this draft's choice may be wrong.

1. **No debate was held on this stage.** The pipeline step asked for the converged edits of
   `debates/design-mig3/`, which does not exist. The statement review is the first review. If a design debate
   was meant to come first, this draft is its input, not its result.
2. **The order of the open Stage 2 work.** The scope gaps of 2c, batching, the record wording and Rust parse
   diagnostics each change adapters or glue. By R4 each is a change the DRI classes. Classed `no-restart`, an
   input that is newly sent to Lean has fewer than 14 days of comparison at the gate. Classed `restart`, each
   costs the days counted so far. The base plan's calendar has stage 2c finish before shadow begins (its section
   6), its text sets 2c's deadline at Gate 4 (its 2.3), and Gate 2 was met with 2c open. This draft recommends
   landing whatever of that list is meant to land before the first nightly, and asks the DRI for the order.
3. **Timeouts.** The adapters call the service with its default limit, which is the interactive 5 seconds
   (`ve/backends/lean_runner.py:92–99`; `lean_service.py:201`). Stage 2 saw two such timeouts in one suite run
   at 14 workers (stage2-progress.md, "Verification"). By R2 one of them costs a day. The choices are: registered
   runs use the batch limit of 60 seconds, which is a change to the candidate surface; fewer workers; or a rule
   that an unanswered call which is answered, and agrees, when run again alone is not a completion failure.
   This draft has no such rule.
4. **A day that is not covered.** R3 ends the run of days when the machine was down or resized. The other
   reading lets such a day count as neither clean nor not clean.
5. **The web app.** The base plan's corpus is "the web app API tests"; the plan's pointer says "real traffic
   (suite, use cases, pilots, web app)". This draft takes the base plan's words. Running a deployed web app at
   `shadow` would put people's inputs into the records (limit 12) and needs its own decision.
6. **Merge runs.** Is the suite the right corpus for a merge? Should a merge without a merge run cost the day?
   The suite at `shadow` is at least twice the work of the suite; the cost on the merge train is not measured.
7. **Uncompared calls and the gate.** Should Gate 3 ask that no class-A call is uncompared, which means stage 2c
   closed first? This draft reports them and does not gate on them, because the base plan puts 2c at Gate 4.
8. **Gate 4's data.** The base plan says the performance gates are "met from shadow data" (Gate 4) and that
   latency is measured "under `VE_AUTHORITY=lean`" (section 4). Shadow's durations can serve the row "per
   authority call through the service" and cannot serve an end-to-end row (limit 10). Stage 4's specification
   has to choose.
9. **Rust.** The base plan's triage rule does not name a Rust fault. R4 treats a Rust fix as a restart, because
   Rust answers inside the candidate for `evaluate` and the two searches. The other reading leaves Rust fixes
   to the DRI's classing, like any change of `checkers.lock`.
10. **Expansion work on the candidate surface.** A new statement layer has, so far, changed
    `lean/VE/Service/Standalone.lean` (the typing reductions) and so the service binary. Each such merge needs
    the DRI's class. If each is a restart, the gate cannot be met while new layers land at today's rate. If
    none is, the 14 days are not about one build. The consolidation chain's work on the route runners (trust
    map 5.1) raises the same question through `checkers.lock`.
11. **Changes to Python's class-A bodies.** A change there that is not the fix of a finding is not on the
    candidate surface and restarts nothing. The base plan's section 6 forbids new Python semantics since stage
    2, and B1 holds the baseline; nothing in this draft lists such commits in the report.
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
