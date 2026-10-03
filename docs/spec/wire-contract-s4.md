# Wire contracts, stage S4 item 1: `soft-norms@0` becomes public (statement specification)

> Status: statement specification, draft 2 (2026-10-02). This is the item-1 statement spec of
> [wire-contract-S4-PLAN.md](wire-contract-S4-PLAN.md) draft 3 (the **plan**). It covers item 1 only: the switch
> of the pilot contract `soft-norms@0` from `shadow` to `public`, which is step 6 of 5.1 of
> [wire-contract-PLAN.md](wire-contract-PLAN.md) (the **base plan**) for row 1 of its 5.3. It builds on
> [wire-contract.md](wire-contract.md) (the **base spec**) and changes no definition of it. The Astra + Fable
> statement review comes before any build step. It was held on draft 1
> (`manage-agents/debates/wire-s4-spec/{fable,astra}.md`; Sol at xhigh stood in for Astra, as `astra.md`
> records) and converged after round 2 on FIX. Draft 2 applies its edits, which section 13 lists, and makes no
> other change; both reviewers confirm the revised text against that list before the measurement commit. No
> debate was held on stage S4 before that review (plan, status paragraph), so it was the first reading of
> everything here that the base plan's debate did not decide; section 12 lists those choices. Fixtures are
> implementation obligations, not claims of completed tests. Nothing was built or run for this draft: the
> expected records of section 8 and the expected delta of section 6 were derived by hand, and every `file:line`
> reference was read on `main` at `2ee50149` and must be re-read at each step. Nothing here changes a verdict,
> an identity, a code, a frozen contract, an existing theorem statement or a checker function.

## 0. Scope, one paragraph

After S0 to S3 the contract `soft-norms@0` runs in shadow: both engines compute the record of every rejection,
the gate compares them on 8,576 inputs, and no output of any program has changed. Item 1 makes the contract
**public** in the one place where Python's validation of a submitted soft source on the soft route rejects
it: the error then carries the contract's record. When a check of the table fails, the record names the first one that fails and
the message is that check's text; otherwise the message is the validator's. The legacy validators still decide,
alone, whether a source is accepted. Lean's route rows are frozen and do not change; `ve_diagnose` already prints
the record. Before the switch, the list of messages that will change is measured on the gate's whole corpus and
signed by the DRI, and the three inputs on which the two legacy validators report different codes are settled
(S4-pre). The Rust engine and the base contracts are later items of the plan and are not specified here.

In this specification: the decisions (1), the definitions (2), the English, one reading each (3), the diagnostics
(4), the Lean statements relied on (5), the expected delta of this profile (6), the files and gates of the
measurement commit and the switch commit (7), the acceptance fixtures (8), the switch gate (9), limits (10), the
statement review checklist (11), the choices this specification resolves (12), and the statement review response
(13).

## 1. Decisions

| # | Decision | Where |
|---|---|---|
| D1 | A contract is public when its `status` is `public`. For `soft-norms@0` that has one effect: at the call site of 2.4, a rejection carries the reported record and its message is the record's text | 2.2 |
| D2 | One function, `ve.softnorms_contract.public_rejection`, turns a legacy rejection of a soft source into the public error. It returns the same error object and never raises | 2.3 |
| D3 | One production call site, in `ve/soft_route.py`, inside the handler of the rejection. On an accepted input no diagnostic module is imported | 2.4 |
| D4 | The legacy validators are not edited by the switch, so the gate keeps comparing the engine with them after the switch | 2.4, 7.1 |
| D5 | `code` is never written by the switch. On the corpus the record's `code` equals it; the three inputs where the legacy validators' codes differ are settled first, outside this work (S4-pre) | 2.8 |
| D6 | A public change is a changed message. The complete list on the gate's corpus is measured, stored, and signed check by check; when the contract is `public`, the gate fails on a change without a signature and on a signature without a change | 2.7, 9 |
| D7 | The switch is the contract's revision 4. In Lean only the generated table's revision changes (T3, L2) | 2.6 |
| D8 | Either reverting the switch commit, or setting `status` back to `shadow` under a new revision, restores today's output | 2.2 |
| D9 | The entry points that are not switched are listed, and stay as they are | 2.5 |

## 2. Definitions

### 2.1 Terms carried over from the base spec

| Term | Meaning (base spec) |
|---|---|
| record | the fault record of 2.7: `contract`, `revision`, `check`, `phase`, `code`, `class`, `path`, `text`, `args` |
| outcome | `fault(record)`, `clean` or `deferred(id)` (2.8) |
| overlay | the table of 2.8 that turns a legacy rejection and an outcome into the **reported record**: the fault record, the residual record, or the deferred record |
| legacy validator | for this unit, `load_soft_document` in Python and `Wire.decodeSoftSource` in Lean (section 6) |
| the gate, the corpus | `conformance/wire_contract_gate.py` and the cases of its `gate_cases`: tiers 0, A, B, the replayed sources and the legacy-difference inputs (tier L) |
| a corpus case that Lean reads | a corpus case that the gate sends to the Lean binaries (the last member of a case of `gate_cases`; `wire_contract_gate.py:487`). Lean reads every case except one built from a catalogue fault whose readers are not both engines, and a recorded test input that carries a `null`, which only the in-process API can pass |
| inherited check | a hook or classifier member marked `inherited`: its text is the inherited decoder's own, in each language (2.5, rule 5) |

A **soft source** is a pair of an environment and a list of norm units, the root of the contract
(`"input": ["environment", "norms"]`). The **legacy error** of a soft source is the `VEError` that Python's legacy
validation raises on it; its **legacy code** is the error's `code` and its **legacy text** is `str` of the error.

### 2.2 Shadow and public

`status` is a member of the contract file (base spec 2.2).

- While it is `shadow`, no output of any program depends on the contract.
- When it is `public`, exactly one output depends on it: the error that the call site of 2.4 raises.

"Public" is a property of Python's output at that call site. Nothing in Lean reads `status`: the generated table
has no such field (`Table.lean`), and `ve_diagnose` prints records in both states.

Changing `status` is a contract edit and raises the revision (base spec 2.8). The switch is revision 4. Today's
output is restored in either of two ways: reverting the switch commit, or a later revision that sets `status` to
`shadow` (the function of 2.3 then returns every error as it received it).

### 2.3 The boundary function

```
ve.softnorms_contract.public_rejection(environment, norms, error, *, contract=None, registry=None)
```

`environment` and `norms` are the soft source the legacy validation received; `error` is the `VEError` it raised.
The two keyword arguments exist for tests; the production call passes neither, and the function then uses the
locked contract `soft-norms@0` (`engine.load`, which may be cached for the process) and the module's `REGISTRY`.

The function returns `error`, the same object, in every case. It does this, in order:

1. If `error.diagnostic` is not `None`, return.
2. If the contract's `status` is not `public`, return.
3. Let the root be `{"environment": e, "norms": n}` with `e` and `n` deep copies of the two arguments, as the
   gate takes them (`wire_contract_gate.py:420`); the arguments are not modified.
4. Let `outcome` be `engine.run(contract, root, registry=registry)`.
5. Let `record` be `engine.overlay(contract, error, outcome)`, with no Lean argument.
6. Set `error.diagnostic` to `record`, and set `error.message` and `error.args` so that `error.message` and
   `str(error)` are both `record["text"]`. Return.

**Failure rule.** If loading the contract or any of steps 3 to 5 raises an `Exception`, the function returns
`error` as it received it: no `diagnostic`, the legacy text. A rejection is never turned into a different failure
by its diagnosis. The gate counts such cases and requires none (9).

What the function never does: it does not write `error.code`, `error.path` or `error.span`; it does not create
an error; it does not call the legacy validator on the source itself (the classifier `soft_semantic` does, inside
the engine, as in shadow); it starts no Lean process.

By the overlay, the reported record is one of three:

| Engine outcome | `error.diagnostic` | `error.message` |
|---|---|---|
| `fault(r)` | `r` | `r`'s `text` |
| `clean` | the residual record, whose `text` is the legacy text | unchanged in value |
| `deferred(id)` | the deferred record `{"contract", "revision", "deferred": id, "text"}`, whose `text` is the legacy text | unchanged in value |

A deferred record has no `check`, `code` or `path` and is never a residual (base spec 2.8). The pilot's Python
registry is complete, so the gate's deferred count in Python is 0 and must stay 0.

### 2.4 The call site

In `ve/soft_route.py`, `admit_soft_document(environment, document, *, soft_document=None)` validates the source
in its branch `soft_document is None` by three statements: `check_soft_source(environment, active)` (only when
`environment` is not a `SoftEnvironment`), `SoftEnvironment(environment)`, and `SoftNormDocument(env, active)`
(`soft_route.py:126–130`). `active` is the list of the document's active norm units. On a submitted environment
these three statements are `load_soft_document(environment, active)`, the legacy validator (`softnorms.py:501`).

The switch wraps those statements in one handler:

- A `VEError` they raise, when `environment` is not a `SoftEnvironment`, is passed to
  `public_rejection(environment, active, error)`, and the returned error is raised.
- When `environment` is a `SoftEnvironment`, the error is raised as it is.
- The import of `public_rejection` is a statement inside the handler.

Nothing else in the file changes. An error from `elaborate_soft_document` or from the admission row keeps
today's text and has no record.

Three properties follow from this shape. They are tested (8.1, 8.3), not proved:

- **(V1) The verdict is the legacy validator's.** The call site raises exactly when the three statements raise,
  and it raises the same object: same type, same `code`. The engine runs after the rejection is decided and
  cannot undo it; the handler ends in a `raise` on every path.
- **(V2) An accepted source does not reach the engine.** On an input the three statements accept, neither
  `ve.softnorms_contract` nor `ve.wire_contract` is imported by this call.
- **(V3) The engine and the legacy validator read the same source.** The root's `norms` is the list `active`
  that the legacy validation received, and its `environment` is the same object; the legacy validation does not
  modify either (fixture Z5).

The import rule of base spec 7.3 becomes, for Python: inside `ve/`, outside `ve/wire_contract/` and
`ve/softnorms_contract.py`, the only module that imports `ve.softnorms_contract` is `ve/soft_route.py`; it
imports the one name `public_rejection`; that name occurs there in one import statement and one call, both
inside one `except VEError` handler of `admit_soft_document`; the call is the operand of a `raise`; and no module
imports `ve.wire_contract`. `tests/test_softnorms_contract.py::test_diagnostic_modules_stay_off_verdict_import_paths`
is rewritten to check exactly this by a scan of the syntax trees. The Lean import rule is unchanged.

The scan resolves each import to the module it names before it compares. A relative import
(`from .softnorms_contract import …`, `from . import softnorms_contract`) is resolved against the package of the
importing file, and `from <package> import <module>` (`from ve import softnorms_contract`) is an import of
`<package>.<module>`. Today's scan compares absolute module names only (`test_softnorms_contract.py:236–241`)
and passes both forms; `soft_route.py` imports relatively.

### 2.5 Entry points: switched, and not switched

| Entry point | After the switch |
|---|---|
| `ve.soft_route.admit_soft_document(environment, document)` with a submitted environment; reached from `ve.admission` when the environment lists `soft-norms@0` (`admission.py:499–502`). This is the adapter's case kind `admission` | **public**: an error of the validation of 2.4 carries the reported record (2.3); a later error of the same call has none |

Not switched; each keeps today's message and has no record:

| Entry point | Why not in item 1 |
|---|---|
| `admit_soft_document` given a `SoftEnvironment`, or given `soft_document` (`document.py:1082`) | the source was validated elsewhere; `to_dict()` of an environment object is not the submitted input that `path` points into |
| `ve.document`'s check of a document (`document.py:337–367`) | its soft checks are interleaved with the document's own; it is the unit `ve-document@1` (base plan 5.3, row 13) |
| the rights route (`ve/rights.py`, `ve/rights_route.py`, `ve/surface/rights.py`) | the unit `rights@0` (row 10) |
| the English front ends (`ve/norm_english.py`, `ve/norm_strict.py`) and `ve/norm_defaults.py` | they build the source from English or from a filled document; there is no submitted JSON |
| `SoftEnvironment(data)` alone, `load_soft_document`, `decode_rule` on one unit, the validation of a generated `E′` | base spec section 10, item 7; and `load_soft_document` must stay the legacy validator the gate calls |
| an error that `run_soft_case` builds from a Lean route row | a Lean legacy row; the route is frozen |
| every Lean row and every Rust output | base plan 2.5; Rust has no soft validation |

Until their own rows, the same fault can therefore read differently through two entry points (plan section 8,
question 3).

### 2.6 The contract edit

Revision 4 of `ve/wire_contract/soft-norms@0.json` differs from revision 3 in two members: `"revision": 4` and
`"status": "public"`. No phase, check, code, text, limit or name class changes.

What follows mechanically, by `tools/wire_contract.py --write`:

- `contracts.lock`: the entry of `soft-norms@0.json`;
- `lean/VE/WireContract/Tables/SoftNorms.lean`: the header comment (revision and hash) and the numeral of the
  table's `revision`, and nothing else;
- the line of that module in `VE/Route/frozen-sources.sha256`;
- `docs/spec/soft-norms-wire-table.md`: no change is expected (it states no revision); `--check` decides.

Every record of either engine then has `"revision": 4`, so the stored reports that hold records are regenerated
(gate, golden, catalogue, delta).

### 2.7 A public change, and the delta

For a corpus case on which Python's legacy validator raises a legacy error with code `c` and text `m`, let `r` be
the reported record: `engine.overlay(contract, error, engine.run(contract, root, registry=REGISTRY))`.

- The case has a **text change** when `r`'s `text` is not `m`.
- The case has a **code difference** when `r` has a `code` and it is not `c`.
- The case is **attributed** to `r`'s `check` (a check id, or `residual`), or to `deferred` for a deferred
  record.

Every check counts here, inherited ones too. A case that the legacy validator accepts has no public change:
nothing is reported for it.

The **delta report** `conformance/wire-contract/soft-norms@0-delta.json` gains the member
`public_diagnostic_changes`: for each check with at least one text change or code difference, in table order,
the number of cases with a text change, the number with a code difference, and one example (the case's label,
`c`, `m`, and `r`'s `code` and `text`). It is computed over the whole corpus, not a sample, and is stored;
`--check` compares the stored file with regeneration, so a changed count is a visible diff.

The **signing file** `conformance/wire-contract/soft-norms@0-switch.json` is written by hand:

```json
{"contract": "soft-norms@0", "revision": 4,
 "signed": {"4.1c": "Python listed the unit's keys after the text; the contract's text is Lean's."},
 "release_note": "…"}
```

`signed` gives each check whose text may change one sentence saying what changes. It is the DRI's recorded
decision of base plan 5.1, step 5. A code difference cannot be signed (2.8).

### 2.8 The code rule, and S4-pre

**Rule K.** On every corpus case, tier L included, where the reported record is a fault, the record's `code` is
the legacy code.

Today rule K holds on every case outside tier L (the gate fails otherwise, `wire_contract_gate.py:527`). In tier
L it fails on three inputs (`soft-norms@0-delta.json`, `s3_pre.code_differences`):

| Input | Python's legacy validator | The contract (Lean's route) |
|---|---|---|
| `env()` and the base, with `speech-acts@0` added to the profiles | `SOFT_INVALID_INPUT`, `Incorrect fields (missing=['speech_acts'], unknown=[])` | 3.2, `SOFT_UNSUPPORTED_PROFILE`, `UnsupportedProfile: Unsupported profile speech-acts@0` |
| `env()` with profile `norm-defaults@0` and the default of `x_required` set to `unspecified` | `SOFT_UNSUPPORTED_PROFILE`, `UnsupportedProfile: norm-defaults@0 documents are checked through fill (ve.norm_defaults)` | 2.3, `SOFT_INVALID_INPUT`, the inherited text |

**S4-pre** blocks the switch. It is done as S3-pre was, outside this work:

1. Each input is treated as a class and run to ground: every profile that `ve/profiles.py` registers and the Lean
   route's registry lacks; and every source on which Python's phase 2 passes a profile on to W1 that Lean's
   `Phases.inheritedProfiles` does not (`softnorms.py:97` has `norm-defaults@0`).
2. Aligning Python's code with the Lean route's is a changed code of a rejected cell: a recorded product
   decision, implemented in Python first (SEMANTICS-MIGRATION-PLAN 2.3). The decision and what was run are
   recorded in `conformance/wire-contract/s4-pre.md`.
3. The fix is one separate commit in Python's soft table. It may change the code and text of a rejection on the
   inputs of those classes. It may not change a verdict: both legacy validators still reject each of the 14
   tier-L inputs, and on every other corpus case Python's legacy code and text are byte-identical to the
   snapshot taken before the commit.
4. Closed means: the gate reports `legacy_code_differences` empty, and the gate fails otherwise.

If a class cannot be aligned without changing a verdict, S4-pre stays open, the switch waits, and the question
goes back to the DRI. This draft has no fallback in which a public error carries a `code` that differs from its
record's.

Rule K says nothing about the residual and deferred records. A residual record's `code` is the contract's
residual code, `SOFT_INVALID_INPUT`, whatever the legacy code is; the gate requires the residual count to be 0.

### 2.9 What is constructed and what is tested

By construction:

- **(A) The public record is the measured one.** The call site reports `overlay(run(…))` through
  `public_rejection`, and the gate measures the delta with the same two functions on the same registry.
- **(B) In Lean only the generated table's revision changes (T3, L2).** The engine reads a table's phases only
  (`instances`, `Engine.lean:226–227`), and revision 4 has the phases of revision 3, so no finding changes. The
  evidence is the regenerated module's diff (T3) and the rows of `ve_diagnose` before and after (L2); no Lean
  statement is added for it.
- **(C) The base spec's claims (A) and (B)** hold as before: the expansion, and the record conditional on equal
  predicate results.

Tested, not constructed:

- that the engine reports a fault exactly when the legacy validator rejects, and rule K: on the corpus, at zero
  tolerance;
- that the signed list is complete: on the corpus only (10, item 3);
- that Python's public text equals the text of Lean's `ve_diagnose` record: on every corpus case that Lean
  reads, for checks that are not inherited. The order inside the classifier sets 5.7–5.8 and 6.5–6.15 is the
  validators' own;
- V1, V2 and V3 of 2.4.

## 3. English: one reading each

### 3.1 How a public rejection reads

The base spec fixes three sentences for the three records (its 3.3). Item 1 adds a fourth, for an error without
a record, and adds no surface that prints any of them: the public output is the error object. The sentences are
fixed here so that the first surface that shows a rejection to a person uses these words. A check id is a name,
like a rule name; `<wording>` is the check's row in `docs/spec/soft-norms-wire-table.md`.

| The error has | Sentence | What it does not say |
|---|---|---|
| a fault record | `This input is rejected. The first check that fails is <id>: <wording>` | that this is the only check that fails |
| a residual record | `This input is rejected, but no check in the table fails. The message shown comes from the validator, not from the table.` | that the input is valid |
| a deferred record | `This input is rejected. This program cannot tell which check fails first, because it cannot run check <id> itself. The message shown comes from the validator, not from the table.` | that check `<id>` fails |
| no record | `This input is rejected. The message shown comes from the validator. No contract record is available for this error.` | that no table covers this kind of input, or that the table was not consulted: the same input may have a record through another entry point (2.5), and under the failure rule of 2.3 the engine ran and raised |

Example, for the source of fixture S1: `This input is rejected. The first check that fails is 2.7a: The
`parties` item, when present, is a string in the class `soft_name`.` "First" always means the order of base spec
2.6, which the table file shows from top to bottom.

### 3.2 Wordings this replaces, and why

Each wording on the left was used for this step, in the plan's pointer, in a script comment or in talk about it,
and has two readings.

| Wording | Its two readings | Written instead |
|---|---|---|
| "The contract is switched to enforcing." | the contract decides whether an input is rejected; or it chooses the message of a rejection | "The contract is public: when the validator rejects a source, the contract chooses the message. It never decides whether a source is rejected." |
| "The diagnostics become uniform." | every program prints the same message for every input; or Python's message is the contract's text | "On every corpus case that Lean reads, Python's message is the text of the record that Lean's `ve_diagnose` gives for the same source, except on inherited checks." |
| "Rejections of soft sources carry the record." | every rejection, through every entry point; or the one of 2.4 | "A rejection raised while soft-route admission validates a submitted source carries the contract's record, one of the three of 2.3. A later error of the same call has none." |
| "`code` is unchanged." | the error's `code`; or the record's | "The error's `code` is the legacy validator's, as today. The record's `code` is the contract's. On the corpus they are equal." |
| "The message changes to the contract's text." | every message becomes different; or the message is now taken from the contract and is often the same words | "The message is the record's text. For most rejections these are the words the validator printed before; the delta report lists the checks for which they differ." |
| "The delta report is complete." | no other message can change; or no other message changes on the corpus | "Every message change on the gate's corpus is in the report." |

### 3.3 The release note

The `release_note` of the signing file is this text, with the list filled from `signed`:

> When soft-route admission in `ve` rejects a submitted soft-norm source while it validates that source, the
> error now has one more member, `diagnostic`: the error carries the contract's record. When a check of the table
> fails, the record names the first one that fails and the message is that check's text; otherwise the message
> is the validator's. The table is `docs/spec/soft-norms-wire-table.md`; "first" is its order from top to
> bottom. With the check, the record gives the place in the input and a code. For most rejections the message
> is the same as before. It is a different message for these checks. ⟨for each signed check, in table order:
> its id, a colon, a space, and its sentence from `signed`, the entries separated by a space⟩ Whether a source
> is accepted or rejected has not changed. The public switch does not change the error's `code`. An error
> raised after that validation, while the norms are elaborated or the document is admitted, has no record, and
> its message is as before. Other ways of submitting a soft source (a document check, the rights route, English
> input) report as before. Before the switch, S4-pre changed the code of two kinds of rejected source, so that
> Python's code is the Lean route's: an otherwise valid source that lists `speech-acts@0` now has the code
> `SOFT_UNSUPPORTED_PROFILE` and the message `UnsupportedProfile: Unsupported profile speech-acts@0`, instead
> of `SOFT_INVALID_INPUT` and a message about incorrect fields; an otherwise valid source that lists
> `norm-defaults@0` and declares an `unspecified` default now has the code `SOFT_INVALID_INPUT` instead of
> `SOFT_UNSUPPORTED_PROFILE`, with the same message.

### 3.4 The paragraph added to soft-norms.md, section 8

> **The public record.** When soft-route admission rejects a submitted source while it validates that source,
> the error carries the contract's record, in its member `diagnostic`. The contract is the wire contract
> `soft-norms@0` ([soft-norms-wire-table.md](soft-norms-wire-table.md); [wire-contract.md](wire-contract.md)
> 2.7). When a check of the table fails, the record names the first one that fails and the message is that
> check's text; otherwise the message is the validator's. The checks, their order and their codes are those of
> this section. The contract chooses the message only: the validator decides, as before, whether the source is
> rejected. An error raised after that validation, while the norms are elaborated or the document is admitted,
> has no record, and its message is as before.

## 4. Diagnostics

### 4.1 The public error

For the source of fixture S1 (parties `["p", "Q!"]`), `to_dict()` of the raised error is:

```json
{"code": "SOFT_INVALID_NAME", "message": "InvalidInput: invalid soft name Q!",
 "diagnostic": {"contract": "soft-norms@0", "revision": 4, "check": "2.7a", "phase": "declarations",
                "code": "SOFT_INVALID_NAME", "class": "InvalidInput",
                "path": "/environment/vocabulary/soft/parties/1",
                "text": "InvalidInput: invalid soft name Q!", "args": {"value": "Q!"}}}
```

Here the message is the one printed today. For the source of fixture S2 (a rule with an unknown member) the
message changes: today it is `InvalidInput: invalid norm fields` followed by Python's list of the unit's keys;
after the switch `to_dict()` is:

```json
{"code": "SOFT_INVALID_INPUT", "message": "InvalidInput: invalid norm fields",
 "diagnostic": {"contract": "soft-norms@0", "revision": 4, "check": "4.1c", "phase": "rule-fields",
                "code": "SOFT_INVALID_INPUT", "class": "InvalidInput", "path": "/norms/0/norm",
                "text": "InvalidInput: invalid norm fields", "args": {}}}
```

With a residual record or a deferred record, `message` is the legacy text and `diagnostic` is the record of base
spec 4.1. With no record, `to_dict()` is today's.

### 4.2 Field by field

| Field of the raised error | After the switch, at the call site of 2.4 |
|---|---|
| the object and its type | the object the legacy validation raised |
| `code` | unchanged; never written |
| `message`, `str(error)`, `to_dict()["message"]` | the reported record's `text` |
| `diagnostic`, `to_dict()["diagnostic"]` | the reported record; before the switch `None` and no member |
| `path`, `span` | unchanged; the record's `path` is not copied into `error.path` |
| every other member of `to_dict()` | unchanged; `VEError.to_dict` is not edited (`errors.py:22–30`) |

So `to_dict()` of the raised error is the legacy error's `to_dict()` with `message` replaced and `diagnostic`
added. A legacy error that has a `path` keeps it as a member (`errors.py:24–25`). The two paths are measured
from different places and may differ: the error's `path` is relative to the environment, and the record's is
relative to the root. W1's errors carry a `path` (`environment.py:364–532`) and reach the call site through
check 2.3; such an error can have the `path` `/vocabulary/predicates/x` while its record has `/environment`.
The soft table's own errors set no `path`, which is why the two objects of 4.1 have none.

A consumer that validates Python's error object against a closed shape must admit `diagnostic`. The switch
commit lists every such schema and stored expectation it had to change; none is known from reading.

### 4.3 Lean

- Every row of `ve_soft_norms_route` is byte-identical to its row before the switch, on every corpus case that
  Lean reads.
- `ve_diagnose soft-norms@0` prints the same rows as before, except that every record has `"revision": 4`.
- Where the Lean route's text differs from the contract's (a name that is not a string and whose compact JSON
  is longer than 80 bytes, checks 2.7a and 2.8c; base spec section 6), the route keeps its text. That is not a
  public change of item 1: no Lean output changes.

### 4.4 Tool diagnostics

`tools/wire_contract.py` gains no code. Raising `status` without the revision is `WC10`, as any edit is.

The gate (`conformance/wire_contract_gate.py`) prints one more line per unmet row of section 9:

| Line | Printed when |
|---|---|
| `gate fails: public delta: check <id> changes text in <n> cases and is not signed` | a measured text change is attributed to a check that `signed` lacks |
| `gate fails: public delta: signed check <id> has no text change` | `signed` names a check with no measured text change |
| `gate fails: public delta: <n> code differences` | rule K fails on `<n>` cases |
| `gate fails: legacy code differences <list>` | S4-pre is open |
| `gate fails: boundary: <n> errors without a record` | the failure rule of 2.3 applied on `<n>` corpus cases |
| `gate fails: boundary: <case>: <what differs>` | a row of tier P (8.2) fails |
| `gate fails: the legacy validator modified its source in <n> cases` | fixture Z5 fails |

The first two lines and the two `boundary` lines belong to rows that section 9 enforces only when the contract's
`status` is `public`; they are printed only then.

## 5. Lean: the statements relied on

The switch edits no hand-written Lean module and adds no Lean statement. Section 5.1 restates what the public
record rests on. Draft 1 offered three optional statements in a new module (`instances_phases_only`,
`run_phases_only`, `run_revision`); the statement review dropped them (section 13). The append-only exception
for `VE/Audit.lean` that the debate's edit c granted names S1b and is not extended, and (B) of 2.9 rests on the
fixtures T3 and L2.

### 5.1 Relied on, as built (`lean/VE/WireContract/Engine.lean:453–534`)

```lean
namespace VE.WireContract
open Lean

theorem run_clean_iff (t : Table) (h : Hooks) (j : Json) :
    run t h j = none ↔ ∀ i ∈ instances t h j, eval h i = none

theorem run_fault_first (t : Table) (h : Hooks) (j : Json) (d : Finding) :
    run t h j = some d ↔
      ∃ pre i post, instances t h j = pre ++ i :: post ∧ eval h i = some d ∧
        ∀ b ∈ pre, eval h b = none

theorem run_phase_major (t : Table) (ps qs : List Phase) (h : Hooks) (j : Json)
    (ht : t.phases = ps ++ qs) :
    run t h j = (run { t with phases := ps } h j).or (run { t with phases := qs } h j)

theorem run_congr_reached (t : Table) (h g : Hooks) (j : Json)
    (hv : ∀ name v, h.view name v = g.view name v)
    (hr : ∀ pre i post, instances t h j = pre ++ i :: post →
            (∀ b ∈ pre, eval h b = none) → eval h i = eval g i) :
    run t h j = run t g j

end VE.WireContract
```

These four, and their four helpers (`expand_views`, `expandAll_views`, `instances_views`,
`findSome_congr_reached`), are in `VE/Audit.lean` (lines 2974–2981). Item 1 changes none of them, and it does
not touch `VE/Audit.lean`, `lean/axioms.txt` or `tools/check_lean_imports.py`. No theorem relates the contract
to a decoder (base plan 3.2); none is added.

## 6. The expected delta of this profile

"Only diagnostics may become uniform, listed per profile": this is the list for `soft-norms@0`, from reading the
two validators, the stored delta report and `s3-pre.md`. None of it was run for this draft; the measured list of
2.7 replaces it, and the signatures are given on the measured list.

Python's message, at the call site of 2.4:

| Check | Today | After the switch | Read from |
|---|---|---|---|
| 4.1c | `InvalidInput: invalid norm fields`, a space, and Python's list of the unit's keys | `InvalidInput: invalid norm fields` | stored delta report: 136 of 2,000 sampled cases |
| 6.5a | `AST exceeds 10,000 nodes` | `ResourceLimit: AST exceeds 10,000 nodes` | stored delta report: 7 cases |
| 6.6 | `precedence depth` | `ResourceLimit: precedence depth` | base spec section 6; no case in the sample |
| 6.11 | `ResourceLimit: generated soft premise`, a space, and a label | `ResourceLimit: generated soft premise` | stored delta report: 1 case |
| 2.7a, 2.8c, on a name that is not a string | Python's `str` of the value | compact JSON of the value, cut at 80 bytes with `...` added | base spec section 6. The two are the same text for an integer and differ for a Boolean, an array or an object |
| 3.2, on `alternatives@0`, `norm-defaults@0`, `reports@0` or `risk@0` | Python's own text for the profile (`alternatives@0 with soft-norms@0`, …) | `UnsupportedProfile: Unsupported profile <profile>` | `s3-pre.md`. S4-pre may align these texts first; then they are not in the list |
| every other check that is not inherited | the contract's text | the same | the gate compares code on every case; text on the faults of tiers 0 and A |

The gate counts 303 text changes on checks that are not inherited, over the 8,576 cases at revision 3
(`soft-norms@0-gate.json`, `text_delta_count`).

Inherited checks (2.3, 4.2a, 4.13b, 4.13d, 5.7, 5.8a, 6.10b): the record's text is the message the hook passes
on, and no change is expected. One of them needs the measurement: the Python hook of 4.2a states W1's
rule-field checks again with texts of its own (`softnorms_contract.py:104–123`) instead of calling the
validator, so its text equals the legacy text only where the two wordings agree. Tiers 0 and A compare them on
the catalogue's faults; 2.7 compares them on every case, and any difference is a text change to sign or to fix
in the hook.

Lean: no row changes (4.3). Rust: no column.

Codes: none changes at the switch (rule K). The code changes of S4-pre are Python's legacy validator's, are
decided and recorded there (2.8), and are not part of this list.

## 7. The measurement commit and the switch commit: files and gates

### 7.1 Diff scope

Item 1 is two commits of this work, after the commit of S4-pre: the **measurement commit** (plan step S4.1a)
and the **switch commit** (S4.1c). The measured delta is read and signed between them (S4.1b).

**The measurement commit.** The contract stays at revision 3 and `shadow`; no file of `ve/` or `lean/` changes.

| Changed | By |
|---|---|
| `conformance/wire_contract_gate.py`, `conformance/wire_contract_delta.py` | the measurement of 2.7. From this commit the gate enforces the rows S4-pre and rule K of section 9 |
| the stored gate and delta reports under `conformance/wire-contract/` | regenerated at revision 3; the delta report is computed over the whole corpus and has `public_diagnostic_changes` |
| tests | the fixtures G3, G6 and G8 |

**The switch commit.**

| Changed | By |
|---|---|
| `ve/wire_contract/soft-norms@0.json`, `ve/wire_contract/contracts.lock` | 2.6 |
| `lean/VE/WireContract/Tables/SoftNorms.lean` and its line in `VE/Route/frozen-sources.sha256` | generated (2.6) |
| `ve/softnorms_contract.py` | gains `public_rejection` (2.3); its module comment no longer says it is imported by tools and tests only |
| `ve/soft_route.py` | the handler of 2.4 |
| `conformance/wire_contract_gate.py` | tier P (8.2), which calls `public_rejection` and so cannot come before it, and the rows of section 9 that the measurement commit did not add; three of them are enforced only at `public` |
| the stored reports under `conformance/wire-contract/` (gate, delta, golden, catalogue), with the new `soft-norms@0-switch.json` and, for the two sources of 8.5, `soft-norms@0-test-inputs.json` | regenerated at revision 4 (2.6); 2.7, 8.5, 9 |
| tests | the new fixtures of section 8, other than those of the measurement commit; `tests/contract_input_recorder.py`, which gains the two wrappers of 8.5; in `tests/test_softnorms_contract.py`, the import scan (2.4) and the assertion that `status` is `shadow` |
| `ve/assurance-manifest.json` and the generated part of `docs/spec/assurance-manifest.md` | the `reason` of `wire.diagnose` says "shadow diagnostic pilot"; it becomes "diagnostic only; no verdict or identity depends on it". Nothing else of the manifest changes: the call site starts no Lean process, so the operation gains no call site |
| `docs/spec/soft-norms.md` | the paragraph of 3.4 |
| this file | a response section, as the base spec's sections 14 to 18 |

Not changed by either commit, and checked by the diff-scope test of C1: `ve/softnorms.py`, `ve/errors.py`,
`ve/wire_contract/engine.py`, `limits.json`, `names.json`, `contract.schema.json`, the contract's examples, every
Lean module other than the generated table, `VE/Audit.lean`, `lean/axioms.txt`, `tools/check_lean_imports.py`,
`Main.lean`, every Rust file, `conformance/identity.json`, the frozen baseline.

The commit of S4-pre is a different commit, before both, with its own scope (2.8).

### 7.2 The gates

The four conservativity gates of base plan 5.2, as amended by the debate, are stated here for the switch
commit. The measurement commit meets them with nothing to show: its diff is its own table of 7.1 (C1), it
changes no verdict (C2) and no public diagnostic (C3), and its inventory diff is empty (C4).

- **C1.** The diff is within 7.1. `VEError.to_dict()` is not edited; the member `diagnostic`, which it has had
  since S1a, is set for the first time.
- **C2.** Legacy verdicts equal their snapshot. Each engine reports `clean` on every accepted corpus case and a
  fault on every rejected one. Python's deferred count is 0; a deferred outcome would be counted, not compared.
- **C3.** Public diagnostics change only as the signed delta lists (2.7); the gate fails otherwise.
- **C4.** `lake build`, `lean/audit.py`, `frozen.py` and the manifest test pass. The inventory diff is the
  generated rehash of 2.6 and nothing else, so the commit and its revert do not touch `VE/Audit.lean`.

The corpus-completeness test `tests/test_wire_gate_corpus.py` is kept, with its three tests as they are (8.5).

## 8. Acceptance fixtures for item 1

Deterministic, with expectations written by hand from sections 2 and 4 and from base spec sections 6 and 8.3.
Each reviewer derives the expectation of every fixture before reading the column "Expected".

The base **B** is `conformance.soft_norms.multi_fault_base()` (base spec 8.3). For a source with norms `N`, the
document **D(N)** is `{"units": [{"kind": "norm", "content": n}, …]}`, one unit for each `n` of `N`, in order;
nothing else of a document is read before the source is validated. "The call" is
`ve.soft_route.admit_soft_document(environment, D(N))`. All records have `"contract": "soft-norms@0"` and
`"revision": 4`.

### 8.1 The boundary and the call site

| Case | Input | Expected |
|---|---|---|
| S1 | the call on B with parties `["p", "Q!"]` | raises a `VEError` whose `to_dict()` is the first object of 4.1 |
| S2 | the call on B with a member `extra`, value `1`, added to rule 0's `norm` | `to_dict()` is the second object of 4.1; the legacy text of the same source, from `load_soft_document`, is longer |
| S3 | the call on B with `language` `"x"` | `code` `SOFT_UNSUPPORTED_PROFILE`; record: `1.2`, phase `envelope`, class `UnsupportedProfile`, path `/environment/language`, text `UnsupportedProfile: Unsupported language`, args `{}`; the error's type is the legacy error's |
| S4 | the call on B with rule 3 over `b1` | `code` `SOFT_OVER_HARD`; record: `6.8`, phase `semantic`, class `InvalidInput`, path `""`, text `SoftOverHard: rule d3 over b1`, args `{"detail": "rule d3 over b1"}`. The error comes from the third validation statement |
| S5 | for each of S1 to S4: the legacy error `e` from `load_soft_document` on the same source | the raised error has `e`'s type and `e`'s `code`; `str` of it, its `message` and its record's `text` are equal |
| S6 | the call on B (accepted), in a subprocess started without the recorder plugin (the plugin imports both diagnostic modules), with the Lean route available | admission returns as today; afterwards neither `ve.softnorms_contract` nor `ve.wire_contract` is in `sys.modules` |
| S7 | the call with `SoftEnvironment(B's environment)` and rule 3 renamed `b1` | raises the legacy error as today: `diagnostic` is `None`, the message is `DuplicateDeclaration: rule b1` |
| S8 | the call on B with `_run` replaced by a function that raises `VEError("x")` | raises that error: `diagnostic` is `None`, the message is `x` |
| S9 | `public_rejection` on B (accepted) with a hand-made `VEError("legacy says no")` whose `code` is set to `SOFT_INVALID_INPUT` | returns the same object; `message` is `legacy says no`; `diagnostic` is the residual record: `check` and `phase` `residual`, `code` `SOFT_INVALID_INPUT`, class `InvalidInput`, path `""`, text `legacy says no`, args `{}` |
| S10 | `public_rejection` on B with rule 3 renamed `b1` and its legacy error `e`, with a registry that lacks the hook `w1_declarations` | `diagnostic` is `{"contract": "soft-norms@0", "revision": 4, "deferred": "2.3", "text": "DuplicateDeclaration: rule b1"}`; the message is unchanged |
| S11 | as S10, with a registry whose `w1_declarations` raises `KeyError` | returns `e` unchanged: `diagnostic` is `None`, the message is the legacy text |
| S12 | `public_rejection` on S1's source and legacy error, with the contract of revision 3 (`shadow`) | returns the error unchanged |
| S13 | `public_rejection` twice on S1's source and error | the second call changes nothing; `diagnostic` is the object the first call set |
| S14 | `public_rejection` on S1's source and error | the two arguments are equal, after the call, to copies taken before it |
| S15 | the syntax-tree scan of 2.4 on the tree; and on each of three changed trees: (a) `ve/document.py` gains a relative import of the module (`from .softnorms_contract import soft_source`); (b) `ve/soft_route.py` gains a second call of `public_rejection`; (c) in `ve/soft_route.py` the one call is not the operand of a `raise` (its result is bound to a name, which is then raised) | passes; fails on each of (a), (b) and (c) |
| S16 | `load_soft_document` on S1's source; `SoftEnvironment` on S1's environment | each raises an error whose `diagnostic` is `None` and whose message is the legacy text |

### 8.2 The delta and the gate

Tier **P** of the gate runs only when the contract's `status` is `public` (section 9). It runs, for every corpus
case that Python's legacy validator rejects with an error `e`: `public_rejection(environment, norms, e′)` on a
fresh legacy error `e′` of the same source; and, where every norm of the case is an object with a member `norm`
(so that D(N) carries the source unchanged), the call.

| Case | Input | Expected |
|---|---|---|
| G1 | tier P, every case, the function | the returned error's `diagnostic` equals the reported record of 2.7, computed apart; its `message` is that record's `text`; its type and `code` are `e`'s |
| G2 | tier P, every case with a document, the call | raises; `to_dict()` equals the legacy error `e`'s `to_dict()` with `message` replaced by the `text` of G1's record and `diagnostic` added with that record. A `path` or `span` of `e` stays a member, unchanged (4.2) |
| G3 | the gate at the measurement commit: revision 3, `shadow`, after S4-pre | the sum of text changes over checks that are not inherited is the gate's `text_delta_count`; `public_diagnostic_changes` lists each check of section 6 that has a case, and any check beyond section 6 is reported, not dropped. The gate exits 0: the three rows that section 9 enforces only at `public` do not fail it |
| G4 | at `public`, the signing file without the entry of 4.1c | the gate fails with the first line of 4.4 |
| G5 | at `public`, the signing file with an entry `1.1` | the gate fails with the second line of 4.4 |
| G6 | the gate's measurement at the measurement commit, with Python's legacy code and text on the three inputs of 2.8 replaced, in the test only, by the values of the table of 2.8 (the values before S4-pre) | fails with `legacy code differences` naming the three inputs of 2.8, and with `public delta: 3 code differences` |
| G7 | the gate after S4-pre and the switch | exits 0: every row of section 9 holds |
| G8 | the delta report after a contract text is edited, without regeneration | `conformance/wire_contract_delta.py --check` fails |

### 8.3 Conservativity

- **Z1.** The full existing suite, the conformance reports, `conformance/identity.json`, the frozen baseline and
  every frozen hash are unchanged by the switch commit, except the files of 7.1. Every stored expectation of a
  Python error's text that the commit changes is listed in it.
- **Z2.** `VEError("x").to_dict()` is `{"code": "InvalidInput", "message": "x"}`, as today.
- **Z3.** Every row of `ve_soft_norms_route`, on every corpus case that Lean reads, is byte-identical to the
  snapshot before the commit.
- **Z4.** On every corpus case, Python's legacy validator gives the verdict, code and text of the snapshot
  before the commit. (The commit of S4-pre has its own snapshot rule, 2.8.)
- **Z5.** On every corpus case, the environment and the norms are equal, after `load_soft_document` returned or
  raised, to copies taken before it (V3 of 2.4).
- **Z6.** `frozen.py` passes; the inventory diff is as C4 says.

### 8.4 Lean and tooling

| Case | Input | Expected |
|---|---|---|
| L1 | `ve_diagnose soft-norms@0` on S1's source, as a `soft-elaborate` case | `{"id": …, "status": "ok", "outcome": "fault", "diagnostic": r}` with `r` the record of 4.1's first object |
| L2 | `ve_diagnose soft-norms@0` on every corpus case that Lean reads, before and after the commit | the rows are equal once `"revision": 3` is read as `4` |
| T1 | `tools/wire_contract.py --check` on the committed tree | exits 0 and prints nothing |
| T2 | the contract with `status` `public` and `revision` 3 | `WC10` |
| T3 | `lean/VE/WireContract/Tables/SoftNorms.lean` at the commit, against its parent | the diff is the header comment and the numeral of `revision`, and nothing else |
| T4 | the contract with `status` `open` | `WC01` |

### 8.5 The corpus-completeness test

`tests/test_wire_gate_corpus.py` keeps its three tests. The new tests of 8.1 are in files that its recorder's
globs match (`tests/test_*contract*`, `tests/test_soft*`).

The recorder as it is does not see the two new paths. It records a call only when the caller is a file of
`tests/` or the soft conformance module (`contract_input_recorder.py:25–27`). After the switch the legacy
validation is called from `ve/soft_route.py` and the engine from `ve/softnorms_contract.py`, so a source that a
test submits only through the call, or only through `public_rejection`, reaches no wrapper that records it. The
switch commit therefore edits `tests/contract_input_recorder.py` (7.1). It gains two wrappers; like the others,
each records only a call made from a file of `tests/` or from the soft conformance module, and passes every
call on unchanged:

- `ve.soft_route.admit_soft_document`: when `environment` is not a `SoftEnvironment` and `soft_document` is
  `None`, it records `(environment, active)`, with `active` selected as the call site selects it (2.4). A
  document from which `active` cannot be selected records nothing.
- `ve.softnorms_contract.public_rejection`: it records `(environment, norms)`.

Each wrapper is shown to work by one source that the tests submit through that path and through no other: no
test file hands it to a legacy validator, to an engine or to a Lean binary.

| Case | Input | Expected |
|---|---|---|
| S17 | the call on B with parties `["p", "R!"]` | raises as S1: `to_dict()` is the first object of 4.1 with `R!` for `Q!` in `message`, `text` and `args`. The source is in `soft-norms@0-test-inputs.json` |
| S18 | `public_rejection` on B with parties `["p", "T!"]` and a hand-made `VEError("x")` | returns the same object; `diagnostic` is S1's record with `T!` for `Q!` in `text` and `args`; the message is `InvalidInput: invalid soft name T!`; `code` is `InvalidInput`, the hand-made error's own. The source is in `soft-norms@0-test-inputs.json` |

A source is stored in `soft-norms@0-test-inputs.json` only if a test records it today and no other source of
the corpus builds it: that is the last assertion of
`test_gate_corpus_holds_every_contract_and_soft_test_input`, as it is. So with either wrapper missing, that test
fails on the stored source of its path.

So every source that S1 to S18 submit under the recorder is either built by a source of the corpus or stored in
`soft-norms@0-test-inputs.json`, and the gate replays it; a source the gate does not replay fails the test, as
today. S6 runs outside the recorder; its source is B, which the corpus holds.

## 9. The switch gate

The DRI reviews one gate report at revision 4, the delta report and the signing file. Astra and Fable read the
measured delta and the signing file before the switch commit (section 13). The switch commit is made only when
every row holds, and the gate exits non-zero on any unmet row that is enforced, judging each from the data and
not from a stated summary (base spec section 17).

| Row | Definition | Required |
|---|---|---|
| the continuation gate | every row of base spec section 9: tiers 0 and A, residual, deferred, coverage, feasibility, S3-pre | as there |
| S4-pre | `legacy_code_differences`, from tier L | empty |
| rule K | cases with a code difference (2.7) | 0 |
| the signed delta | the checks with a measured text change, against the keys of `signed` | the two sets are equal |
| the boundary | tier P: G1 on every rejected case, G2 on every case with a document | no difference |
| errors without a record | tier P cases on which the failure rule of 2.3 applied | 0 |
| the source is not modified | Z5 | 0 cases |
| the legacy validators | Z3 and Z4 | byte-identical |
| the corpus | `tests/test_wire_gate_corpus.py` | passes |

When each row is enforced:

- The rows S4-pre and rule K are enforced from the measurement commit on, whatever the `status`.
- The rows "the signed delta", "the boundary" and "errors without a record" are enforced only when the
  contract's `status` is `public`. In shadow they cannot hold: `public_rejection` returns every error as it
  received it (2.3, step 2), and the signatures are given on the list that the measurement commit stores. In
  shadow the gate still measures and stores `public_diagnostic_changes`.
- Every other row is enforced whatever the `status`.

A row that fails after the switch commit is handled by a revert of the commit, or by a revision that sets
`status` to `shadow` (2.2).

## 10. Limits, and what is not claimed

1. **No verdict and no identity.** The engine runs inside the handler of a rejection and returns the error it
   was given. That is a tested property of one call site (V1), not a theorem.
2. **One entry point.** Only the validation of a submitted source in soft-route admission is public; an error
   raised later in the same call, by elaboration or by the admission row, is not (2.4). The entry points of 2.5 keep
   today's messages, so two entry points can word the same fault differently until their own rows.
3. **The delta is complete on the corpus.** An input outside the gate's corpus can show a message change that
   no list contains, a code that differs from its record's, a residual record, or an error without a record.
   The corpus test bounds this for inputs the tests know.
4. **A residual record is possible in the field.** It carries the contract's residual code, which need not be
   the error's `code`. A source outside the restricted JSON domain, which only the in-process API can pass, gets
   the residual record: the engine evaluates nothing on it (base spec 2.1).
5. **Inherited texts differ between languages** until the base contracts exist (plan items 3 to 6). Making them
   includes is a later revision with its own delta.
6. **Lean's route text is not the contract's** on the Lean delta entries of base spec section 6 (4.3). No Lean
   output switches.
7. **The failure rule hides an engine defect from the caller.** The caller gets today's error. The defect is
   visible only where the gate or a test runs the same input.
8. **Cost.** A rejection at the call site costs one engine run, in which `soft_semantic` runs the legacy
   validator again. An accepted source costs nothing.
9. **Two paths.** The error's `path`, where the legacy validation set one, is relative to the environment; the
   record's `path` is relative to the root. They may differ (`/vocabulary/predicates/x` against `/environment`,
   4.2), and the switch changes neither.
10. **No surface prints the sentences of 3.1.** They are fixed, not shown; W8's fidelity gate may change them.

## 11. Statement review checklist (Astra + Fable, before any build step)

1. **Scope (plan section 8, questions 2 to 4).** Is the pilot's switch the right first item of S4? Is one entry
   point right, or should the entry points of 2.5 switch together?
2. **The boundary (2.3).** Is each step determined for every input? Is the failure rule right, or should an
   engine exception reach the caller? Is step 1 (an error that already has a record) needed?
3. **The call site (2.4).** Are the three statements `load_soft_document` exactly? Can the handler turn a
   rejection into an acceptance or into another failure? Is the import rule checkable as written?
4. **`str(error)` (4.2).** Does any caller or dispatcher between `ve.admission` and the user compare the text
   of a Python rejection with Lean's, so that the switch changes one side of a comparison?
5. **Rule K and S4-pre (2.8).** Is "fix in Python first, or wait" right, against signing the code differences?
   Can the two classes be aligned without a verdict change?
6. **The delta (2.7, 6).** Is a signature per check fine enough? Derive the expected list of section 6
   independently; attack 4.2a and the 3.2 rows.
7. **Wordings (3).** Does each sentence have one reading? Is any rejected wording of 3.2 still in this file or
   in the plan?
8. **Conservativity (7, 8.3).** Can anything in the switch commit change a verdict, an identity, a code, or a
   Lean byte other than the generated table's revision?
9. **The corpus (8.5).** Does the recorder see sources submitted through the two new paths?

## 12. Choices this specification resolves, and open points

The base plan and base spec fix that there is a switch commit, that it sets `VEError.diagnostic` and the
message, and that it adds one production call site. Everything below is this specification's own choice, put to
the statement review. The review withdrew R10, corrected the reason of R12 and reworded the texts of R11
(section 13); it asked for no change to the others.

| # | Choice | Relative to the base documents |
|---|---|---|
| R1 | Item 1 of stage S4 is the pilot's switch; the Rust engine and the base contracts follow | the base plan's S4 row has no switch of the pilot; the plan's pointer describes one (plan section 8, question 2) |
| R2 | The call site is soft-route admission of a submitted source, and no other entry point | base spec 7.3 says "the boundary where a rejection is returned" and names no function |
| R3 | The boundary is a function beside the hooks, outside the legacy validator; `ve/softnorms.py` is not edited | base spec 7.2 kept `ve/softnorms.py` unedited in S0 to S3; this keeps it so through the switch, which lets the gate call the legacy validator after the switch |
| R4 | `str(error)` changes together with `message` | base spec 4.2 names `message` only; the overlay reads the legacy text as `str` of the error |
| R5 | The failure rule: on an engine exception the error is returned unchanged | not in the base documents |
| R6 | The call site consults no Lean process; a deferred outcome is reported as the deferred record | base spec 2.8 allows both rows; the pilot's Python registry is complete |
| R7 | The import of the diagnostic module is inside the handler, and the import rule for Python is restated for one importer | base spec 7.3 forbade every import in S0 to S3 |
| R8 | A public change is defined on every check, inherited ones too, over the whole corpus; signatures are per check, in a file written by hand | base plan C3 says the delta report is complete; the stored report is a sample and counts checks that are not inherited |
| R9 | Rule K with S4-pre: code differences are fixed in Python first and cannot be signed | base plan 5.1, step 5, leaves the decision to the DRI; `s3-pre.md` left the three inputs for it |
| R11 | The sentence for an error without a record (3.1), and the texts of 3.3 and 3.4 | base spec 3.3 has three sentences |
| R12 | `error.path` is not set from the record's `path` | the two are measured from different places. W1's errors, which reach the call site through check 2.3, carry a `path` relative to the environment (`environment.py:364–532`); the record's `path` is relative to the root (4.2). The soft table's own errors set no `path` |

R10 (three optional Lean statements in a new module) is withdrawn; the numbers of R11 and R12 are kept.

Open, for the build to settle, with the two points that the statement review closed:

1. **The dispatcher. Closed by the statement review.** For a submitted soft environment `ve.admission` returns
   through `_admit_document_python` (`admission.py:446–449`) before it reaches `execute("admission", …)`
   (`admission.py:475`). So no dispatcher compares or rewrites the text of this rejection.
2. **S4-pre's second class.** `norm-defaults@0` in Python's inherited profiles may be needed by the
   norm-defaults route (`norm_defaults.py:683` builds a soft document over a placeholder environment). Not run.
3. **4.2a.** Whether the Python hook's texts equal the validator's on every input is not known (section 6).
4. **A closed error schema.** No consumer with a closed shape for Python's error object is known from reading;
   the suite decides (4.2).
5. **The recorder. Closed by the statement review.** `tests/contract_input_recorder.py` records only a call
   whose caller is a test file or the soft conformance module (lines 25–27), so as it is it does not see the two
   new paths. 8.5 states the two wrappers it gains, and 7.1 puts the file in the switch commit's scope.
6. **The stored delta report** states 6,007 cases and a 2,000-case sample, against the gate's 8,576. It is
   regenerated over the whole corpus by 2.7; until then its counts are not the corpus's.

## 13. Statement review response (draft 2)

Source: `manage-agents/debates/wire-s4-spec/{fable,astra}.md`. Verdict: **FIX**, converged after round 2. The
edits are the nine of Fable's round 2 list, which Astra's round 2 accepts, and the one that Astra's round 2
adds (row 10). Nothing was run for this draft.

| # | Edit of the review | Change in this draft |
|---|---|---|
| 1 | Recorder: `tests/contract_input_recorder.py` enters the switch commit's scope, with wrappers for `admit_soft_document` and `public_rejection`; S6 runs in a subprocess without the plugin; one test source submitted only through each new path | 7.1 (tests row, test-inputs file); 8.1 (S6); 8.5 (the two wrappers, S17, S18) |
| 2 | Import scan: it resolves relative imports and `from <package> import <module>`; S15 has three failing trees | 2.4; 8.1 (S15) |
| 3 | `path`: a legacy error keeps its `path`, so G2 compares with the legacy error's `to_dict()`; the two paths may differ; R12's reason was false | 4.2; 8.2 (G2); 10, item 9; 12 (R12) |
| 4 | Sequence: S4.1a is a commit of its own and enforces S4-pre and rule K; the rows "the signed delta", "the boundary" and "errors without a record" are enforced only at `public` | 7.1; 7.2; 9; 4.4; D6; 8.2 (tier P, G3, G4, G5) |
| 5 | Lean statements: 5.2 to 5.4, the last row of 7.1, C4's clause, L3, L4, R10, checklist item 7 and limit 9 are struck; D7 and (B) of 2.9 read "In Lean only the generated table's revision changes (T3, L2)"; 5.1 stays | status paragraph; D7; 2.4 (last sentence of the import rule); 2.9 (B); 5; 7.1; 7.2 (C4); 8.4; 10; 11; 12 |
| 6 | "copies" becomes "deep copies" | 2.3, step 3 |
| 7 | Outcome wording: "the error carries the contract's record. When a check of the table fails, the record names the first one that fails and the message is that check's text; otherwise the message is the validator's."; the sentence for no record ends "No contract record is available for this error." | 0; 2.5 (the switched row); 3.1; 3.2, row 3; 3.3; 3.4 |
| 8 | Lean scope: "on every corpus case that Lean reads" | 2.1 (the term); 2.9 (the tested text claim, which had the same fault); 3.2, row 2; 4.3; 8.3 (Z3); 8.4 (L2) |
| 9 | Open points 1 and 5 are closed | 12 |
| 10 | G6 cannot run "before S4-pre", because the measurement code comes after it; it becomes a fixture that runs once that code exists | 8.2 (G6) |

The plan's part of each edit is in its section 10.

Where an edit left the wording to this draft, the wording chosen is listed here, for the confirmation:

- the term "a corpus case that Lean reads" of 2.1, read from `gate_cases`;
- the two sources of S17 and S18, and the use of the corpus test's last assertion as their proof;
- the form of G6: the values of the table of 2.8 put in place of Python's legacy results, in the test only;
- the split of the gate's code in 7.1: the measurement and the rows S4-pre and rule K in the measurement
  commit; tier P and the other new rows in the switch commit, because tier P calls `public_rejection`;
- limit 9 of section 10: the struck limit's number now holds the limit on the two paths (edit 3).

Order, as the review fixed it:

- S4-pre may start at once: no edit touches it.
- Both reviewers confirm this revised text against the table above, in one pass on the diff, before the
  measurement commit.
- The switch commit waits for the measured, signed delta, which both reviewers read (section 9).

## 14. Item-1 implementation response (2026-10-02)

S4-pre is `10d8a0f8`: the two legacy code classes of 2.8 were aligned in Python's soft table. A positional
comparison of all 8,576 corpus cases found exactly the three intended rejected rows changed and no verdict
change; [s4-pre.md](../../conformance/wire-contract/s4-pre.md) records their old and new code and text.
The full suite subsequently found that the norm-defaults route still needs `norm-defaults@0` during fill
construction. Correction `1509d4ee` retains that inherited profile there while selecting Lean's narrower list
for submitted sources on the soft route; the same three corpus rows remain the only legacy changes.

The shadow measurement is `fd251c2d`. Its gate ran 8,576 cases with no mismatch, residual, deferred or code
difference. The measured, stored public text changes were:

| Check | Cases | Change in the public message |
|---|---:|---|
| `2.7a` | 43 | a non-string party name uses compact JSON spelling |
| `3.2` | 10 | an unsupported profile uses the route's standard text |
| `4.1c` | 210 | the norm's key list is omitted |
| `6.5a` | 20 | `ResourceLimit:` is added |
| `6.6` | 2 | `ResourceLimit:` is added |
| `6.11` | 16 | the generated premise label is omitted |

That is 301 message changes in six checks on the measurement corpus. No inherited check changed text. The
six sentences and the release note are in
[soft-norms@0-switch.json](../../conformance/wire-contract/soft-norms@0-switch.json). The user's instruction
for this implementation forbade model calls, so no new Astra or Fable review of the measured delta was run.

At revision 4, two additional test inputs enter the corpus through the new call paths. The public gate then
ran 8,578 cases with zero mismatches, residuals, deferred outcomes, legacy code differences, record/code
differences, errors without a record, source mutations or boundary differences. The six text-change counts
remained the same. `lake build`, `lean/audit.py`, and `VE/Route/frozen.py` passed. Only the generated Lean table
and its inventory hash changed; no handwritten Lean statement or Rust file changed for item 1. The final suite
result and switch commit are recorded in the implementation report to the user.

## 15. Review response: the item-1 switch (2026-10-03)

Sources: `manage-agents/wire-s4-review-astra.final.md` and `manage-agents/reviews/wire-s4-review-fable.md`, both
FIX, with no A finding. Each B finding was fixed as a class, with a regression test:

| Finding | Fix |
|---|---|
| Fable B1: 2.8c was predicted (section 6) but unmeasured, because ranks were mutated only to an integer | The block mutations give parties and ranks each a Boolean, an array and an object item. 2.8c changes text in 102 cases and is signed; 2.7a counts 138. A test requires every kind in both lists and both checks measured and signed |
| Fable B2: S4-pre made the `norm-defaults@0` row's text name a profile the source lists as missing | The soft route restates W1's remedy text for each profile it removes before W1 that the source lists, in the validator and the 2.3 hook through one function (`soft_route_environment`); the row keeps its S4-pre code and the text it had before S4-pre ([s4-pre.md](../../conformance/wire-contract/s4-pre.md)). A test fails if the soft route removes another profile without a restated text |
| Fable B3: G6 hand-set the report's summary fields | G6 runs `report()` over tier L with the real engine and Lean binaries, Python's legacy values on the three inputs of 2.8 replaced by those before S4-pre, in the test only |
| Fable B4 (release note), Astra B1, Astra B2 | 3.3 and 3.4 limit the record to errors of the source's validation and say that a later error of the same call has none; 3.3 scopes the unchanged `code` to the public switch, discloses S4-pre's two code changes, keeps the quotes around "first", and lists each signed sentence itself. The release note is generated from 3.3 and `signed`, and a test compares both it and the paragraph of `soft-norms.md` with this file. Section 0, 2.5, 3.2 and limit 2 of section 10 say the same |

At this response the gate runs 8,796 cases (tier R gains the new mutations, their combinations and one
recorded test input) with zero mismatches, residuals, deferred outcomes, legacy code differences, record and
code differences, errors without a record, source changes or boundary differences; the text changes are 498,
in seven signed checks.

Two points remain for the DRI, outside this work:

- **The signatures (Fable B4).** The seven sentences of `signed` were written by the implementer, and the
  switch commit came before the reviewers' reading of the measured delta that section 9 asks for. Fable's
  reading accepts the six earlier sentences subject to B1, which added 2.8c. The DRI's countersignature of the
  seven is still to be given.
- **The review gate of section 9 (Astra, C).** The implementation ran under a user instruction that forbade
  model calls, so the Astra and Fable reading of the measured delta came after the switch commit, in the two
  reviews above, instead of before it. That exception is recorded here; the gate's status is that both
  reviewers have read the delta, after the switch, and asked for the fixes of this section.

## 16. DRI countersignature (2026-10-03)

The DRI (orchestrator) has read the seven `signed` sentences in `conformance/wire-contract/soft-norms@0-switch.json`
(2.7a, 2.8c, 3.2, 4.1c, 6.5a, 6.6, 6.11) against the measured delta (8,796 cases, 498 text changes, zero
mismatches, no accept/reject, identity or code change outside the disclosed S4-pre rows) and countersigns all
seven. 4.1c and 6.11 make two rejection messages less detailed in exchange for one uniform contract text; this is
accepted. The section 9 exception (reviewers read the delta after the switch commit, then required the fixes of
section 15, which are done) is accepted and closes Fable B4 and Astra C.
