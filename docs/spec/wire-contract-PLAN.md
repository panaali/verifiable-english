# Wire contract: one ordered validation table for Python, Lean and Rust (PLAN)

**Status:** plan only, draft 2, 2026-10-02, branch `design/wire` from `main` at `c9a34582`. No code or proofs change
with this document. Draft 2 applies, in one commit, the exact edits of the converged Fable/Astra design debate
(`manage-agents/debates/design-wire/{fable,astra}.md`, CONVERGED after round 3; Sol at xhigh stood in for Astra, as
`astra.md` records). Verdict: **BUILD (exact edits): S0 to S3 only, with S1c moved to S4**; S4 onward needs a
separate decision (section 7). Section 11 maps each debate edit to its change here. The item-1 statement spec is
[wire-contract.md](wire-contract.md); its statement review comes before S0 to S3 start. The plan was written from
reading the sources; nothing was built or run, and the `file:line` references below were collected by read-only
sweeps and must be re-read at each step.
Inputs: ARCH-ROADMAP (P1 "versioned wire/profile contracts + codegen", the W6a, speech-acts and discourse known
limitations, the LIMITS CONTRACT item), [assurance-manifest.md](assurance-manifest.md),
[SEMANTICS-MIGRATION-PLAN.md](SEMANTICS-MIGRATION-PLAN.md) (sections 2.3 and 5), [soft-norms.md](soft-norms.md)
section 8, `lean/VE/Route/frozen.py`, `tools/hooks/README.md`, `ve/backends/lean_service_schema/README.md`.

## 0. Decision in brief

1. **One contract per wire unit**, a JSON file under `ve/wire_contract/`, holding an ordered table of checks
   grouped in phases. Every check has a position, a stable code, a message template and a path. It is the
   soft-norms validation table (soft-norms.md 8) made machine-readable and extended to every profile.
2. **Tables are generated; engines are written once.** Each language gets one small generic engine that runs a
   table and returns the first failing check. The Lean and Rust tables are generated data files; Python reads the
   JSON. Table expansion (which checks run on which items, in which order) is therefore the same in all three by
   construction, and so are the position, code, path and text of the reported check, conditional on every predicate
   reached returning the same result in each (section 2.4). Two orders are outside that claim and are described
   separately: the order inside a classifier set (T3, section 2.3) is test-enforced, and the fault order of the raw
   JSON scanners (`json@0`, question 7) is open.
3. **The contract decides the diagnostic, never the verdict.** The existing decoders and validators stay as they
   are and keep deciding accept or reject. On a rejection, the engine picks the diagnostic. Accept/reject and
   every identity are unchanged because the code that produces them is not touched.
4. **Lean: only data is generated.** Generated Lean modules are table literals with no theorems. The engine, the
   hooks and all proofs are hand-written. No existing Lean module is edited beyond added lines in the aggregation
   files (3.2; `VE/Audit.lean` only if the optional lemmas are added, C4 in 5.2), so no soundness proof moves.
5. **What "by construction" does not cover** is stated in section 2.4: checks that need semantics are hand-written
   predicates per language, and their agreement is tested, not generated.
6. Migration is one contract at a time, soft-norms first (its table and multi-fault generator already exist), each
   step gated by the conservativity checks of section 5.2 and a reviewed list of changed diagnostics.

## 1. The problem, as the code stands

| | Python | Lean | Rust |
|---|---|---|---|
| Decoding | hand-written chains of `if …: raise`; first fault wins (`ve/environment.py:315` `_decode`, `ve/wire.py`) | hand-written over `Lean.Json`, fuel-indexed, often proof-carrying (`decodeSoftSource`, `SpeechActs.Wire.decodeDocument`); 16,985 pinned decoder lines | hand-walked `serde_json::Value`, about 353 hand-written error sites, no derive, no `build.rs` |
| Diagnostic | `VEError.code` is one of about ten classes; finer codes are prefixes inside the message (`"MissingPermissionDual: …"` has code `InvalidInput`) | `Except String` with `"Class: detail"`; no shared type; only the soft route emits a `code` field | `{code, message, span?}`; sub-codes inside the message (`InvalidDate(…)`) |
| Order | statement order | statement order; `runAll` stages in discourse, V1–V11 in risk | statement order |
| Path, list of faults | none; one diagnostic | none; one diagnostic | none; one diagnostic |

Only soft norms has an explicit ordered table: soft-norms.md 8 (checks 1.1 to 6.15), mirrored by hand in
`ve/softnorms.py:89–491` and `lean/VE/SoftNorms/Phases.lean`, and enforced by generated multi-fault inputs
(`conformance/soft_norms.py:725–915`). Everywhere else the order is a comment ("in Python's order",
"in the Lean decoder's order") and the tests tolerate differences:

- `tests/test_p0_three_way.py:28–50` and `conformance/p0.py:569–570` collapse every code outside a short list to
  `rejected`; Lean supplies only accept/reject for the parser and validation families (`conformance/README.md:138`).
- `conformance/rights_differential.py:270` accepts a suffix match of the text.
- `tests/test_speech_acts_conformance.py:1856–1871` compares status only (speech-acts.md:884–888: two independent
  faults give different first diagnostics in Python and Lean).
- `tests/test_discourse_lean.py:1601–1608, 1692–1705` pin differing codes (discourse.md:984–997).
- W6a: malformed decimal literals get different classes in the three implementations (ARCH-ROADMAP:12);
  `tests/test_w6a2_looprecheck1.py:47–52` passes any code other than `ResourceLimit`.
- Rust's profile gate runs its rules in a different order from `ve/profiles.py:47–99` (same class, different text
  on a multi-fault profile list); the same concept has two encodings inside Rust (`risk.rs:111` and `units.rs:155`).

Three constraints shape the design:

- **Frozen Lean.** All 249 `lean/VE/**/*.lean` modules are hash-listed in `VE/Route/frozen-sources.sha256`; a new
  module must be listed; `Main.lean`'s existing subcommands are hash-frozen. The assurance manifest pins every
  decoder file by SHA-256 and line range and classifies every other JSON-handling file.
- **Proofs unfold decoders.** About thirty theorems unfold decoder or runner bodies, many counting exact bind steps
  (`SoftNorms.Admission.admitDocument_spec`, `SpeechActs.Wire.scope_in_identity`, `Route.Gate.classify_sound`,
  `Route.Run.route_rejects_before_checking`, the discourse rejection theorems). `partial` is a forbidden token.
- **Codes are a compatibility surface.** Migration plan 2.3: no rejected cell may change its code without a
  recorded product decision, implemented in Python first. Diagnostic messages are a recorded class, changed in one
  reviewed commit. This plan amends that wording to one reviewed switch commit per unit (about fourteen in all);
  the amendment is recorded in 5.1, step 6.

## 2. Design

### 2.1 What a contract is and where it lives

```
ve/wire_contract/
  contract.schema.json     meta-schema, in the lean_service_schema dialect (compiled by ve/backends/service_schema.py)
  limits.json              the named limits (today's ve/limits.py values); shared with the LIMITS CONTRACT item
  names.json               named lexical classes: identifier, soft_name, token, label, profile_id, …
  <unit>.json              one contract: soft-norms@0.json, envelope@0.2.json, speech-acts@0.json, …
  examples/<unit>/*.json   at least two valid inputs per contract, the bases of the fault generator
  contracts.lock           {unit: {revision, sha256 of the canonical JSON}}; a contract edit without a lock update fails
  engine.py                the Python engine (kernel layer; imports ve.wire, ve.errors, ve.limits only)
```

The files ship inside the package, as `ve/assurance-manifest.json` and `ve/backends/lean_service_schema/` do.
JSON is chosen because all three languages already read it with their own restricted readers and Lean has no
package dependencies. This extends the mig1 pattern (one source of truth for response shapes, a second
implementation that must agree on genuine and mutated inputs) from responses to inputs; the response schemas stay
as they are. JSON Schema itself is not used for the checks: it fixes neither codes nor a cross-item order, and
"no check of a phase runs before every earlier phase has passed over the whole source" cannot be said in it.

A contract (excerpt; the full soft-norms table is the 67 numbered checks of soft-norms.md 8; `MAX_RULES` stands
for a named entry of `limits.json`, where today the 256 is a literal in both validators):

```json
{"contract": "soft-norms@0", "revision": 1, "input": ["environment", "norms"],
 "uses": ["limits", "names", "norms@0"],
 "codes": {"SOFT_INVALID_NAME": {"class": "InvalidInput", "summary": "Invalid or reserved soft name."}},
 "phases": [
  {"name": "envelope", "checks": [
    {"id": "1.1", "at": "/environment", "kind": "exact_keys",
     "keys": ["language", "profiles", "spec_revision", "vocabulary"],
     "code": "SOFT_INVALID_INPUT", "text": "InvalidInput: invalid environment envelope"},
    {"id": "1.7", "at": "/norms", "kind": "max_items", "limit": "MAX_RULES",
     "code": "SOFT_RESOURCE_LIMIT", "text": "ResourceLimit: rules"}]},
  {"name": "declarations", "checks": [
    {"id": "2.3", "kind": "include", "contract": "norms@0", "phases": ["declarations"],
     "view": "w1_environment", "as": "SOFT_INVALID_INPUT"},
    {"id": "2.7", "each": "/environment/vocabulary/soft/parties/*", "checks": [
      {"id": "2.7a", "kind": "name", "class": "soft_name",
       "code": "SOFT_INVALID_NAME", "text": "InvalidInput: invalid soft name {value}"},
      {"id": "2.7b", "kind": "unique_so_far",
       "code": "SOFT_DUPLICATE_DECLARATION", "text": "DuplicateDeclaration: party {value}"}]}]},
  {"name": "semantic", "checks": [
    {"id": "6.1", "kind": "hook", "hook": "outranks_acyclic",
     "code": "SOFT_DEPENDENCY_CYCLE", "text": "DependencyCycle: {names}"}]}]}
```

### 2.2 Order: the one rule every engine implements

The reported diagnostic is the first failing check in table order. Precisely:

- Phases run in order; a phase starts only when every check of the earlier phases has passed over the whole input.
- Inside a phase, entries run in order. An entry is a check or an `each` group.
- An `each` group iterates its path pattern and runs its sub-entries for one item before moving to the next item
  (item-major inside the group; groups nest). Two groups in sequence give check-major order. Both orders occur in
  soft-norms.md 8 (4.x is per rule, 5.4 to 5.9 is per rule, 5.1 to 5.3 are whole-source).
- Arrays iterate in index order. Object members iterate in Unicode code point order of the key, which is the
  natural order of all three (`Lean.Json` objects, Python `sorted`, Rust `BTreeMap`). This is *not* the UTF-16
  order of the canonical serialiser; the two differ only for keys outside the BMP, and the engine test corpus
  has such keys. The order in which an author wrote the keys never matters.
- A check's position is the tuple (phase, entry, item index, sub-entry, …), compared lexicographically. The fault
  generator computes expected diagnostics from these tuples (section 6).

### 2.3 Checks, in three tiers

| Tier | Kinds | Who decides pass or fail | Agreement across languages |
|---|---|---|---|
| T1 declarative | `type`, `exact_keys`, `keys` (required and optional), `const`, `enum`, `max_items`, `max_bytes`, `max_count` (named limit), `name` (named lexical class), `sorted_unique`, `unique_so_far`, `declared_in` (a reference resolves in a set collected from a path), `requires`/`excludes` (conditional presence), `when` (guard), `include` (run another contract's phases here, optionally re-coded with `as`) | the generic engine | by construction, given the engine conformance corpus (6.1) |
| T2 predicate hook | `hook`: a named, hand-written predicate per language, from the input to `ok` or `fail(args)` | hand-written code; it cannot choose position, code or text | order, code, text by construction; the truth value is tested per hook |
| T3 classifier hook | `classifier`: an existing validator that fails with one of a *declared set* of checks (`"emits": ["6.5", …]`), mapped by a hand-written function | the existing validator, including the order inside the set | checked against the contract by the multi-fault generator; not by construction |

T3 exists because some semantic validators are one function with many internal steps (`validateSoft` 6.5 to 6.15,
`Norms.Tree.check`, risk's `checkView` V1 to V11). Splitting each step into a predicate would duplicate logic next
to frozen, proved code. The contract still owns the codes and texts of those checks and states their order; the
generator verifies that order. A T3 set is split into T2 hooks only where drift was actually observed.
Every contract ends with a catch-all `residual` check (code `<UNIT>_INVALID_INPUT`, text = the legacy text) so that
every legacy rejection has a diagnostic. The residual count on the generated corpora is a gated metric; target zero.

Hook rules: a hook reads the input and, for an `each`, the current item; it returns `ok` or `fail` with named
string arguments; it never throws a diagnostic and never sees other checks. A hook may assume every earlier check
passed, and is only required to agree across languages on such inputs. `view` names a hand-written JSON
transformation (for example soft-norms 2.3, "the vocabulary without the soft block, under the inherited profiles").

### 2.4 The diagnostic record, codes and texts

```json
{"contract": "soft-norms@0", "revision": 1, "check": "2.7a", "phase": "declarations",
 "code": "SOFT_INVALID_NAME", "class": "InvalidInput", "path": "/environment/vocabulary/soft/parties/1",
 "text": "InvalidInput: invalid soft name Q!", "args": {"value": "Q!"}}
```

- `code` is the stable fine-grained code. Profiles without codes today get `<UNIT>_<NAME>` codes; the sub-codes
  that now live in message prefixes (`MissingPermissionDual`, `InvalidDate`, `UnitPrecision`, …) become codes.
- `class` is the legacy `VEError` class. `VEError.code` keeps reporting the class, so existing callers and the
  support matrix keep their vocabulary; the fine code is new information, not a renaming.
- `path` is an RFC 6901 pointer into the submitted input. No implementation reports one today. Under an `include`
  with a `view` the checked value is a transformation of the input, so the inner pointer does not point into the
  submitted input: there `path` is the include site's `at`, and the inner pointer goes in `args`.
- `text` is the template with arguments substituted. Argument renderers are a closed set: `raw` (a string as is),
  `json` (canonical JSON of the value, cut at 80 bytes), `index`, `count`, `list` (sorted, joined by `, `). No
  language-native quoting (`{key!r}`, `{key:?}`, `compress`), which is a present source of text drift.
- Texts are ASCII and may not contain, as a whole word, any token that `lean/audit.py` forbids: the audit scans
  strings too, and the texts land in generated Lean files. The generator imports `FORBIDDEN` from `lean/audit.py`
  (today `sorry`, `sorryAx`, `admit`, `axiom`, `unsafe`, `native_decide`, `implemented_by`, `partial`, `opaque`,
  `extern`) and keeps no list of its own.

**What is by construction and what is not.** "By construction" in this plan means two things only: table
expansion (which checks run on which items, in which order), and the position, code, path and text of the reported
check, conditional on equal predicate results. Given the same contract revision, two engines report the same record
when (a) each engine implements the T1 kinds and the order rule correctly, and (b) every predicate reached (a hook,
a classifier or a view) returns the same result in both. (a) is established once, independent of profiles (6.1; in
Lean also by the optional lemmas of 3.2). (b) is per-hook hand-written code; it is tested (6.2, 6.3) and its
failures are local: a disagreement is one named predicate on one input, not an ordering question spread over a
decoder. Two orders are not by construction and are described separately: the order inside a T3 classifier set is
the existing validator's and is test-enforced by the generator (6.2); the fault order of the raw JSON scanners is
open (question 7).

### 2.5 How the contract meets the existing validators: an overlay

```
verdict    = legacy_validator(input)                    # unchanged code, unchanged accept/reject, unchanged ids
diagnostic = engine.run(contract, hooks, input)         # consulted only when the verdict is a rejection
```

- If the legacy validator accepts, the engine is not consulted in production. In tests it must report no fault.
- If the legacy validator rejects, the engine's first failing check is the diagnostic. If only the residual check
  fires, the legacy text is reported and counted.
- The soft route already does this: `SoftNorms/Run.lean:344–352` re-runs `Phases.checkSource` to take the code.

Python and Rust engines return `fault`, `clean` or `deferred(check id)`. `deferred` means a hook this language
cannot evaluate (Rust has no soft-norms validation; after migration stage 5 Python has no typing or elaboration).
A T1 fault found before the first deferred check is final and needs no other process: that is the IDE's fast path.
Otherwise the diagnostic is requested from Lean. Both run the same table, so the answer is the same record.

When Lean is not consulted or cannot answer (a standalone Rust binary, `wire.diagnose` unavailable), the outcome
stays deferred, so that the public message does not silently depend on the deployment. A deferred outcome:

- carries the contract, the revision, the deferred check id and the legacy text;
- has no `check`, `code` or `path`, because the engine has not identified the first failing check;
- is counted under the deferred share, never under residual (residual means the contract has no check for a legacy
  rejection, 2.3; deferred means this language could not evaluate a hook).

Emission:

- Python: `VEError.to_dict()` gains `diagnostic` (the record above). `code` and `message` are kept. `message`
  switches to the contract text per profile in the step that removes the profile's test tolerance (section 5).
  `ve/backends/diagnostics.py` reads the class from the contract instead of parsing prefixes.
- Lean: a new executable `ve_diagnose` (a new `lean_exe`; `Main.lean` untouched) takes the same case JSON as the
  route and returns `{id, status: "fault" | "clean", diagnostic}`. Legacy runner rows stay byte-identical, so no
  assurance binding or response schema changes. One new manifest operation, `wire.diagnose`, with no verdict; if it
  is unavailable the deferred outcome above is reported with the legacy text (a diagnostic is not a verdict).
- Rust: the `error` object gains `diagnostic`; `code` and `message` are kept until the same per-profile switch.

### 2.6 Versioning

A contract carries `contract` (the unit and its wire version) and `revision` (an integer bumped on every edit).
`contracts.lock` pins the SHA-256 of each file; generated files name the hash they were generated from. A revision
bump can change diagnostics only; it cannot change a verdict or an identity, because nothing on those paths reads
the contract. `checker_build` changes with every build as today (migration plan section 5 projection).

## 3. What is generated and what is hand-written

| Artefact | Generated or hand-written | Check |
|---|---|---|
| `ve/wire_contract/*.json`, `examples/` | hand-written, reviewed; the source of truth | meta-schema; contract lint (6.1); lock |
| `lean/VE/Contract/Tables/<Unit>.lean` | **generated** table literal | `tools/wire_contract.py --check` regenerates and compares bytes |
| `lean/VE/Contract/Limits.lean`, `Names.lean` | **generated** constants and class tables | same |
| `rust/ve-core/src/contract_tables.rs` | **generated** static data, committed (no `build.rs`, so the reproducible build and `lean/checkers.lock` are unaffected in method) | same; a cargo test compares the embedded hashes with the lock |
| Python tables | none: `engine.py` loads the JSON | — |
| Spec tables (soft-norms.md 8 and the "Order:" paragraphs of the other specs) | **generated** between `<!-- BEGIN GENERATED -->` markers, as `tools/assurance_manifest.py` does | `--check` |
| Fault catalogue skeleton for T1 checks | **generated** at test time from the contract | — |
| Engines: `ve/wire_contract/engine.py`, `lean/VE/Contract/Engine.lean`, `rust/ve-core/src/contract.rs` | hand-written once, about 300 to 500 lines each | engine conformance corpus (6.1); Lean lemmas (3.2) |
| Hooks and views: Python in the profile modules, `lean/VE/Contract/Hooks/<Unit>.lean`, Rust beside each decoder | hand-written | per-hook differential (6.2) |
| Existing decoders, validators, canonical serialisers, identity code | hand-written, **unchanged** | section 5.2 |
| Lean soundness and replay proofs | hand-written, **unchanged** | `lean/audit.py`, `frozen.py` |

### 3.1 Generated Lean: how it is audited and frozen

1. **Grammar.** A generated module is: the `GENERATED … do not edit` header naming the contract and its hash, one
   `import VE.Contract.Table`, one namespace, one `def table : VE.Contract.Table := …` built from constructors and
   string and number literals, `end`. No `theorem`, `instance`, `macro`, `open`, `#eval`, no recursion. Lean's
   elaborator type-checks the literal; a reviewer never has to read it.
2. **Bound to its source.** `tools/wire_contract.py --check` (in the gate, and in the pre-commit hook, where it is
   pure text and well under a second) fails when a committed generated file differs from regeneration. This is the
   `lean/VE/Service/english_copy.py --check` precedent.
3. **Frozen inventory.** Each generated module, the engine and the hooks are new entries in
   `frozen-sources.sha256` (the guard requires every `VE/**/*.lean` to be listed). `--write` rewrites the hash
   lines of the generated modules in the same commit. Existing entries do not change in any migration step, with
   the one exception of C4 (5.2): the `VE/Audit.lean` line in S1b, if the optional lemmas are added. The gate for
   each step checks that the inventory diff is additions plus generated-table rehashes only, plus that exception.
4. **Assurance manifest.** Table modules handle no JSON and need no entry. `Engine.lean` and `Hooks/*.lean` read
   JSON and are classified under `other_json` as "diagnostic only: no verdict depends on it". That claim is
   enforced: `tools/check_lean_imports.py` gets the rule that `VE.Contract.*` is imported only by
   `VE/Contract/*` and `DiagnoseMain.lean`. The trusted decoder count (16,985 lines) does not grow.
5. **Forbidden tokens.** The generator refuses a contract whose ids or texts contain an audit token (2.4); it
   imports `FORBIDDEN` from `lean/audit.py` instead of keeping its own list, so `lean/audit.py` and the hook stay
   as they are and the two cannot drift.
6. **Audit.** The engine lemmas (3.2), if added, are recorded in `VE/Audit.lean` and `lean/axioms.txt`; this is
   the reviewed append-only diff that C4 allows. Tables add no theorems.

### 3.2 Lean proofs

Unchanged: every existing theorem, because no existing module is edited (`VE.lean`, `VE/Audit.lean`,
`lakefile.toml` and the inventory gain entries only, the footprint of every feature so far).

New, hand-written once, about the engine and for any table. They are optional: if they cost more than planned,
the engine corpus stands for Lean as well and the lemmas are recorded as open (section 8). Adding them is the one
case in which an existing inventory line changes (`VE/Audit.lean`, C4):

```lean
theorem run_clean_iff  : run t h j = none ↔ ∀ c ∈ instances t j, holds h j c
theorem run_fault_first : run t h j = some d →
    ∃ i, d = diagnosticOf (instances t j)[i] ∧ ¬ holds h j (instances t j)[i] ∧ ∀ k < i, holds h j (instances t j)[k]
```

`instances t j` is the table expanded over the items of `j` in the order of 2.2. These make "first failing check in
table order" a theorem on the Lean side. They are statement schemata, not existing code; the engine is structurally
recursive on the table (no fuel problem: the table is a finite tree, arrays are lists).

Not planned: a theorem relating a contract to its legacy decoder (`diagnose j = some _ ↔ decode j = .error _`).
No decoder has a refinement theorem today, and this plan does not add one; both directions are tested (6.3).
The same holds for new profiles: a contract is never on a verdict or identity path (0.3, 2.6). A new profile's
route validates with its own hand-written decoder, as today, and the contract supplies its diagnostics (S10).
Making `Engine.run` a route's structural validation would put the generated table, the generator and the contract
JSON on the verdict path, against 0.3, 2.6 and the import rule of 3.1; it is not part of this plan and would need
its own.

## 4. Scope

In: JSON wire inputs that are validated before checking: the restricted JSON layer, the environment envelope and
profile gate, vocabulary and its statement layers, formulas, models, norm documents and the profile blocks,
quantity declarations, `ve-document@1` and `@2` metadata and units.

Out: English and strict-surface parse diagnostics (Rust supplies spans), certificate and witness replay failures,
operational failures, service response shapes (mig1's schemas), resource metering of derived structures (the
LIMITS CONTRACT item; this plan only supplies the generated `limits` table and the `max_*` kinds it will use),
and returning several diagnostics at once (section 9, question 5).

## 5. Migration

### 5.1 Procedure for one contract

1. **Author** the contract from the spec's order paragraph and the authority's code. Order rule: where the spec
   has a numbered table, the spec; otherwise the current behaviour of the implementation whose verdict is
   authoritative for the unit (the assurance manifest's `authority`; for discourse, soft norms, rights, risk and
   alternatives that is Lean). This keeps the authoritative implementation's rejected cells unchanged by default.
   For new contracts and where the authority has no consistent order: shape of the whole source, then cross
   references, then semantics, then derived-structure limits (the soft-norms layout).
2. **Hooks** in Lean, then Python, then Rust where Rust supports the unit. Lean hooks call the frozen decoders
   read-only (the `inherited` pattern of `Phases.lean:30`).
3. **Generate** tables and the spec table; add inventory and lock entries.
4. **Shadow.** Every implementation computes the record next to its legacy diagnostic; nothing public changes.
   The generator (section 6) runs; the **delta report** `conformance/wire-contract/<unit>-delta.json` lists every
   corpus case whose public class or text would change, per implementation, grouped by check.
5. **Review** the delta report. It is the recorded product decision that migration plan 2.3 requires for a changed
   code, taken by the DRI, with a release note. Changes go to Python first where Python has an implementation.
6. **Switch**: the public message becomes the contract text, the `diagnostic` record is emitted, the unit's test
   tolerance (last column of 5.3) is deleted and the spec's known-limitation paragraph is removed. One commit,
   one revert. **Recorded amendment to SEMANTICS-MIGRATION-PLAN** (stage 2, "Diagnostics", and its risk table):
   that plan says message wording changes "land in one reviewed commit". Under this plan they land in one
   reviewed switch commit per unit, about fourteen in all (5.3), each with its own delta report and release
   note. Codes remain a zero-tolerance class and section 2.3 of that plan is unchanged.

### 5.2 Conservativity gates (every step)

- **C1 identities.** No diff in any decoder, canonical serialiser, identity serialisation (a `to_dict` whose
  output is hashed or compared as an identity) or digest function (a diff-scope check on the step's file list:
  decoder files pinned in the manifest and existing inventory lines are untouched, C4's exception apart).
  `VEError.to_dict()` is diagnostic serialisation, not identity serialisation: it may gain the `diagnostic` field
  of 2.5, and that is the only change to it this plan permits. `conformance/identity.json`, the frozen baseline
  `conformance/baseline-2026-09/` and the v0 replay are byte-identical on accepted inputs.
- **C2 accept/reject.** The baseline's outcome classes and the three-way suites are unchanged. On the generated
  corpus: the legacy verdict of each implementation equals its pre-step snapshot; where an implementation
  supports the unit and completes diagnosis, its engine reports `clean` on every accepted input and a fault on
  every rejected one (zero tolerance both ways). A deferred outcome (2.5) is counted under the deferred share of
  its language and not compared; an implementation that does not support the unit is not run on it. Residual
  count reported; a deferred outcome is never a residual.
- **C3 diagnostics.** The delta report is the complete list of public changes; any change outside it fails.
  The frozen golden `conformance/wire-contract/<unit>.golden.json` (first diagnostic of a fixed corpus) shows every
  later contract edit as a reviewable diff.
- **C4 Lean.** `lake build`, `lean/audit.py`, `frozen.py` and the assurance-manifest test pass; the inventory diff
  is additions and generated rehashes only, with one exception in S1b. If the optional lemmas (3.2) are added,
  C4 also allows a reviewed append-only diff to `VE/Audit.lean` (lines are only added: the new `import` and
  `#print axioms` lines; no existing line is changed, moved or removed) together with the rehash of its inventory
  line. `lean/audit.py` reads `#print axioms` from `VE/Audit.lean` alone and stays unchanged (3.1), so a separate
  audit file is not an alternative. If the lemmas are dropped, no existing inventory line changes.

### 5.3 Order of migration and what becomes uniform, in the sense of 2.4

"Uniform" has the limited meaning of 2.4: table expansion, and position, code, path and text conditional on equal
predicate results. The order inside a T3 set is test-enforced, and raw JSON scanner order is open (row 2,
question 7). A tolerance in the last column is removed only for implementations that support the unit and
complete diagnosis: three-way comparisons cover non-deferred records, and deferred outcomes are counted (C2).
"Changes" lists what may differ from today; verdicts and identities never do. Rows are in migration order.

| # | Contract | Order taken from | Diagnostics that may change | Tolerance removed |
|---|---|---|---|---|
| 1 | `soft-norms@0` (pilot) | soft-norms.md 8 | Texts compared for every check (today: code for all, text for 17 cases, `soft_norms.py:1103`); checks 6.5–6.15 become a declared T3 set. Rust: unchanged, deferred (it does not validate the soft block) | hand-mirrored table in `softnorms.py` / `Phases.lean` becomes checked against the contract |
| 2 | `json@0` (restricted JSON) | Python (`wire.json`, 40 cases, pins Python and Rust) | Lean gains classes (today bare texts such as `duplicate object key`); texts uniform; see question 7 on order | Lean joins the `wire.json` comparison |
| 3 | `envelope@0.2` + profile gate | Python (`profiles.py:47–99`); Lean already follows (`Gate.lean:150`) | Rust message on multi-fault profile lists (`environment.rs:171–240`); Rust `reports@0` and `unspecified` texts | — |
| 4 | `vocabulary@0.2` with `data@0`, `definitions@0`, `time@0`, `documents@1`, `norms@0` declarations | Python (`environment._decode`) | prefix sub-codes become codes in all three; name quoting uniform | `p0.py:569–570`, `test_p0_three_way.py:28–50` (`rejected` collapse), in part |
| 5 | `formula@0.2`, `model@0.2` | Python (`_Decoder`: limits, shape, typing; Rust and Lean already follow) | Lean reports classes for the parser and validation families (today accept/reject only); `InvalidModel` generator becomes an argument (today attribute, prefix, suffix) | `conformance/README.md:138` limitation; rest of the row-4 collapse |
| 6 | `norms@0` documents (W1) | Python (`norms.py`; `Norms.Tree.check` mirrors it) | texts | substring matches in `test_norms_three_way.py` |
| 7 | `norm-defaults@0` | Lean and Python agree where tested | rejections are compared for the first time (today a Lean error is a mismatch); deltas unknown until shadow | — |
| 8 | `speech-acts@0` | speech-acts.md 7 "Order", refined to a numbered table; shape of all units before references | first diagnostic on multi-fault documents in Python **and** Lean; the two recorded reproducers get one answer | `test_speech_acts_conformance.py:1856–1871`; speech-acts.md:884–888 |
| 9 | `alternatives@0`, `risk@0` | Lean (`checkAlt`, `checkRisk`, `checkView`) | generic texts (`test_risk_w6_extension.py:205–258`); `UnitPrecision` gets one encoding | those `GENERIC` cases |
| 10 | `rights@0` | Lean (reuses the soft phases by `include`) | Python texts that are only suffix-equal today | `rights_differential.py:270` |
| 11 | `reports@0` | Lean (`scopedOk`, `bridgeOk`, `metaOk`) | texts; Rust `reports@0` gate text | — |
| 12 | `ve-units@1` (quantity, W6a) | Python | malformed decimal literals get one class (ARCH-ROADMAP:12); `InvalidDate`, `DateRange`, `UnitPrecision` become codes | `test_w6a2_looprecheck1.py:47–52`; substring matches in the units tests |
| 13 | `ve-document@1` (W2 admission) | Python (`admission.py`) | `AdmissionError` sub-reasons become codes | remaining `rejected` collapse |
| 14 | `ve-document@2` + `ve.discourse@1` | Lean (Python's verdict is Lean's) | Python reports Lean's record on every input both reject; the three recorded cases close (question 6) | `test_discourse_lean.py:1601–1608, 1692–1705`; discourse.md:984–997 |

Rows 2 to 5 come before the remaining profiles because profiles inherit them: until the base is contracted, an
inherited check is one coarse hook whose text is language-specific (soft-norms 2.3, 4.2, 5.7 report
`SOFT_INVALID_INPUT` with the inherited text). After row 5 those become `include`s with uniform text.

## 6. Tests

### 6.1 Engine and contract (profile-independent)

- **Engine conformance corpus** `conformance/wire-contract/engine.json`: small synthetic contracts and inputs with
  expected records, covering every T1 kind, nested `each`, check-major against item-major, `when`, `include` with
  and without `as`, every argument renderer, key-order permutations, keys outside the BMP, empty arrays, absent
  optional members. The three engines must return byte-identical records (Python and Lean in S0 to S3; Rust joins
  in S4, section 7). This is the evidence for claim (a) of 2.4.
- **Contract lint** (static): unique ids in increasing position; every code declared and used; placeholders match
  the kind's arguments; limits and name classes exist; every hook and classifier has at least one fault mutation;
  every code a spec lists has a check; no forbidden token; lock and revision in step.
- **Generation**: `--check` in the gate and the hook; `tools/mutation_check.py` gains one injected fault (two rows
  swapped in a generated table) that `--check` must catch.

### 6.2 Multi-fault differential generator

One generic generator, `conformance/wire_contract.py`, replacing the per-profile one in
`conformance/soft_norms.py:725–915`, whose design it keeps.

- **Bases**: the contract's valid examples.
- **Fault catalogue**: for T1 checks, mutations derived from the check (delete a required key, add an unknown key,
  each wrong JSON type, limit plus one, duplicate an item, break sorting, dangle a reference, a fixed list of
  hostile names); for T2 and T3, the hand-written mutations the lint requires. Each fault carries its check
  position, its expected code and its footprint (the pointers it writes).
- **Tier 0, single faults**: each fault alone must produce its own check as the diagnostic in all engines, and the
  legacy validators must reject. A failure here is a catalogue or contract bug and is fixed before the other tiers.
- **Tier A, oracle**: all pairs inside one phase, a seeded sample of cross-phase pairs and of triples, pairs of the
  same check on two items (the earlier item must win), all pairs inside each T3 set. Faults are combined only when
  their footprints are disjoint. Expected record: the fault with the least position. Assert Python = Lean =
  Rust (where the unit is supported) = expected, on the whole record, for non-deferred records; deferred outcomes
  are counted, not compared (C2).
- **Tier B, agreement without an oracle**: random stacks of two to five mutations, dependent ones included, with
  key order shuffled. Assert the engines agree with each other, and that fault ⇔ the legacy validator rejects, in
  each language that completes diagnosis (C2). A disagreement is reduced by removing mutations one at a time and
  reported as a hook defect.
- **Tier C, conservativity**: on every case of A and B, the C1 and C2 checks of 5.2.
- **Coverage, gated**: every check is the first diagnostic at least once and is masked by an earlier one at least
  once; every adjacent phase pair occurs; residual count is zero; the deferred share per language is reported.
- **Budget**: seeded and xdist-safe; about 2,000 cases per contract per commit, about 50,000 nightly.

### 6.3 Per-hook and legacy cross-checks

- Each T2 hook: Python, Lean and Rust results compared on the Tier 0 to B inputs at the point the hook is reached.
- Corpora replay: the conformance fixtures, the stage-0 baseline's rejection cells and the use-case documents run
  through the engines in shadow; `clean` on accepted, fault on rejected, residual zero.

## 7. Steps and effort

Engineer-days for an agent worker with review loops, as in earlier plans. Steps S1a and S1b run in parallel.
**Authorised by the design debate: S0 to S3 only.** S4 onward is a separate decision, taken after the
continuation gate below.

| Step | Content | Effort |
|---|---|---|
| S0 | meta-schema, `limits.json`, `names.json`, `tools/wire_contract.py` (validate, lint, `--write`, `--check`, spec tables, lock), hook and gate wiring | 3 d |
| S1a | Python engine, `deferred`, `VEError.diagnostic` in shadow | 2 d |
| S1b | Lean `Table`, `Engine`, the two lemmas (optional; C4), `ve_diagnose`, inventory, manifest and import-rule entries | 5–7 d (the lemmas are the uncertainty) |
| S2 | engine corpus, generic generator with tiers 0, A, B, C and coverage, delta and golden reports (Python and Lean) | 4 d |
| S3-pre | **blocks S3:** run the inherited `norm-defaults@0` difference (`ve/softnorms.py:97` lists it among the inherited profiles; `Phases.lean:36` and soft-norms.md 2.3 do not) to ground with an input that reaches it. A reachable accept/reject difference is outside this plan's licence to change and is fixed separately, before the pilot is called conservative | 0.5 d |
| S3 | pilot: `soft-norms@0` contract, hooks, T3 set, generated spec table; retire the hand-mirrored table check | 4 d |
| S4 | Rust engine and generated tables module 3 d (S1c, moved here: Rust does not validate soft norms, so before S4 only the synthetic corpus would exercise it); base: `json@0` 1.5 d, `envelope@0.2` 2 d, `vocabulary@0.2` and layers 4 d, `formula@0.2` and `model@0.2` 3 d | 13–14 d |
| S5 | `norms@0` 3 d, `norm-defaults@0` 2 d | 5 d |
| S6 | `speech-acts@0` (numbered table for the spec, two-sided delta) | 4 d |
| S7 | `alternatives@0` 2 d, `risk@0` 4 d | 6 d |
| S8 | `rights@0` 2 d, `reports@0` 3 d, `ve-units@1` 3 d | 8 d |
| S9 | `ve-document@1` 3 d, `ve-document@2` + `ve.discourse@1` 4 d | 7 d |
| S10 | "contract first" rule for new profiles in PLAN-EXPAND2 and AGENTS.md, for diagnostics only: a new profile ships its contract with its decoder, and the decoder still decides the verdict (3.2); docs; remove dead prefix classifiers | 2 d |

About 64 to 67 engineer-days; about 6 calendar weeks with three workers once S2 is done. S0 to S3 (18.5 to 20.5
days of effort, about 3 calendar weeks) is a complete, useful increment and the point to decide whether to
continue (question 1).

**Continuation gate after S3, reviewed by the DRI:**

- the residual count is zero;
- Tier 0 and Tier A are green in Python and Lean;
- at least two thirds of the 67 soft-norms checks are expressed as T1 or T2 without a coarse `view` hook, with the
  T1 and T2 counts reported separately (the threshold measures feasibility; agreement of T2 hooks remains evidence
  from differential tests, not a construction);
- step S3-pre is closed.

If the gate fails, keep S2's generic multi-fault generator over the hand-mirrored tables and stop the migration.
S4 onward needs a separate decision in either case.

Dependencies on other roadmap items: LIMITS CONTRACT consumes `limits.json` and the `max_*` kinds (S0); the
migration's `diagnostics.py` mapping reads classes from contracts after S4; the pre-commit hook gains the
`--check` call in S0.

## 8. Risks

| Risk | Mitigation |
|---|---|
| Hooks drift as the hand-written phase lists did | a hook is one predicate with a name, a position it cannot change and its own differential test; Tier B finds disagreements without an oracle; the T3 share and the residual count are gated metrics |
| The contract and the legacy validator disagree on the verdict | the engine never decides a verdict; Tier B and the corpora replay assert fault ⇔ reject at zero tolerance |
| A Lean hook re-implements a private step of a frozen decoder and differs from it | prefer calling the decoder as a predicate (coarser but exact); a finer hook that disagrees shows up as a residual |
| Contract authoring is slow or wrong for the large units (vocabulary, documents) | Tier 0 rejects a wrong catalogue early; the delta report is the review artefact; the pilot calibrates the estimate |
| Double validation cost | only on rejection; one extra Lean call per rejected batch; the Python T1 fast path needs no process |
| Engine lemmas cost more than planned | the plan does not depend on them for Python or Rust agreement; fall back to the engine corpus for Lean as well and record the lemmas as open |
| A diagnostic text trips the Lean token audit | the generator refuses it (2.4) |
| Public behaviour changes without review | C3: the delta report is complete by test; one switch commit per unit |

## 9. Open questions

1. **How large is T3?** If most semantic checks stay classifier sets, the by-construction part is the shape and
   reference checks only, and semantic-phase order is still test-enforced (better organised than today, but the
   same kind of guarantee). The pilot measures this on soft-norms 6.5 to 6.15; the continuation decision after S3
   should use that number.
2. **Phase-major or document order?** The soft-norms layout reports a shape fault in the last rule before a
   reference fault in the first. For an author in the IDE, the earliest fault in the document may be the better
   message. This plan keeps the authority's order for existing units (least change) and has not tested either with
   users. It affects speech acts most, where both implementations change and neither order is consistent today.
3. **Whose order wins when the authority's order is an accident?** "The authority's current behaviour" preserves
   rejected cells but may freeze an arbitrary order (for example Python's profile-gate rule order). The delta
   review can override it per unit; there is no general rule.
4. **`ve_diagnose` or a service mode?** A new executable touches no frozen file. A `diagnose` mode in `ve_service`
   avoids a second process but edits `Service/Protocol.lean`, whose dispatch is pinned by `rfl` theorems. Start
   with the executable; revisit if rejection latency matters in the IDE.
5. **Several diagnostics at once.** With the table as data, an engine could continue past the first fault inside a
   phase and return every independent one, which suits English rephrasing in the IDE. All three implementations
   return one diagnostic today; this is left out to keep the first version small.
6. **Discourse.** Of the three recorded cases, only the unknown mention form is a wire-order difference. The other
   two come from two different English parsers reading the same wording (discourse.md:988–995). A contract cannot
   make two parsers agree; the plan closes them by rule: the hook is the authority's parser, Python relays Lean's
   record, and Python's own reading becomes a hint, as it already is in the opposite direction. Whether Python's
   port of the discourse checks is then needed at all is a migration stage-5 question.
7. **JSON layer order.** The restricted readers are byte scanners, not table-driven. Python detects a duplicate key
   when the object closes (`object_pairs_hook`), Rust at the second key (`wire.rs:132`), so a duplicate key followed
   by a syntax error inside the same object probably reports differently (read from the code, not run). Making
   that uniform means changing a scanner or adding a tolerant re-scan for diagnostics only. The plan treats
   `json@0` as codes and texts plus one T3 set and leaves offset order open; the user value is low.
8. **`include` with a view.** Soft-norms 2.3 runs W1's declaration checks on a transformed vocabulary under a
   restricted profile list. If such views are common, `include` is less declarative than it looks and inherited
   checks stay coarse hooks. To be learned in S3 and S5.
9. **Unverified reading in the pilot's area: no longer a question.** `ve/softnorms.py:97` lists `norm-defaults@0`
   among the inherited profiles; `Phases.lean:36` and soft-norms.md 2.3 do not. This was seen by reading only. It
   is now the blocking step S3-pre (section 7): run it to ground before S3, and fix any reachable verdict
   difference outside this plan. The continuation gate requires it closed.
10. **Fine codes on the public surface.** The plan keeps `VEError.code` as the class and adds `diagnostic.code`.
    Promoting the fine code to `code` would be simpler for callers and would change every rejected cell of the
    support matrix once. Not proposed here; it needs its own product decision.
11. **Composition.** The FEATURE COMPOSITION item (discourse with norms, soft norms and rights) will need
    contracts that include each other under profile adapters. `include` is the intended place, but composition is
    not designed here and may need more than re-coding.
12. **Trust in the generator.** `tools/wire_contract.py` is new trusted tooling for diagnostics (not for verdicts).
    Lean type-checks its output and the engine corpus exercises it, but a generator bug that reorders rows the same
    way for Lean and Rust would be seen only through the golden files and the Python engine, which reads the JSON
    directly. That independence is the reason Python does not use a generated table.

## 10. Alternatives considered

- **Generate complete decoders in all three languages.** Rejected. Lean decoders are proof-carrying and
  fuel-indexed, about thirty proofs unfold their bodies, and every one is hash-pinned as trusted code; regenerating
  them would move the trusted base and the proofs at once. It would also not fix order, which is a cross-item,
  cross-phase property that typed decoding does not express.
- **One diagnoser only (Python).** Since verdicts agree, one implementation could choose every diagnostic. Rejected:
  semantic checks need the authority's semantics, which Python loses at migration stage 5; the Lean and Rust
  binaries are used standalone by the conformance suites and the `rust-experimental` deployment.
- **JSON Schema for inputs.** Kept for response shapes and for the contract meta-schema. Not used for the checks:
  no codes, no order across items.
- **Keep hand-mirrored tables with multi-fault tests, as soft norms does.** It works, and the pilot starts from it.
  It leaves two or three copies of each table to be kept in step by reading, which is the cost each feature has
  paid again; the Python and Lean soft-norms copies already show one difference found only by reading (question 9).
  It is also the fallback if the continuation gate fails (section 7): S2's generic generator is kept over the
  hand-mirrored tables.

## 11. Debate response table (draft 2)

Source: `manage-agents/debates/design-wire/{fable,astra}.md`, CONVERGED after round 3 (Sol at xhigh stood in for
Astra in all three rounds, as `astra.md` records). Verdict: **BUILD (exact edits): S0 to S3 only, S1c moved to
S4**, after one plan commit carrying edits a to h of Fable's round 3, which Astra's round 3 restates. No further
plan review round unless an edit deviates from the list. This draft changes nothing else in the design.

| Debate edit | Change in this draft |
|---|---|
| a. Limit "by construction" to table expansion, and to position, code, path and text conditional on equal predicate results; describe T3 order and raw JSON scanner order separately, as test-enforced or open | 0 (item 2); 2.4 ("What is by construction and what is not"); 5.3 heading and its first paragraph |
| b. Scope C1 to identity serialisation; `VEError.to_dict()` may gain `diagnostic` | 5.2, C1 |
| c. C4 allows additions, generated rehashes, and a reviewed append-only `VE/Audit.lean` diff with its rehash in S1b; the lemmas stay optional | 5.2, C4; 0 (item 4); 3.1 (items 3 and 6); 3.2 (lemmas marked optional); section 7, S1b |
| d. C2 zero tolerance and the 5.3 tolerance removals apply only where an implementation supports the unit and completes diagnosis; a deferred outcome carries the contract, revision, deferred check id and legacy text, has no `check`, `code` or `path`, and is counted under the deferred share, never under residual | 2.5 (the deferred outcome; the Lean emission bullet); 5.2, C2; 5.3, first paragraph; 6.2, tiers A and B |
| e. Run the inherited `norm-defaults@0` difference to ground before S3; fix any reachable verdict difference outside this plan | section 7, step S3-pre; question 9 |
| f. Strike the last paragraph of 3.2; S10's "contract first" rule covers diagnostics only | 3.2: the new-profile rule (`Engine.run` as a route's structural validation) is struck and replaced by the statement that contracts stay off every verdict and identity path, for new profiles too; the paragraph's first two sentences (no refinement theorem; both directions tested) are kept. Section 7, S10 |
| g. Under a `view`, `path` is the include site and the inner pointer goes in `args`; the generator imports `FORBIDDEN` from `lean/audit.py`; record the one-switch-commit-per-unit amendment to the migration plan | 2.4 (the `path` and text bullets); 3.1 (item 5); section 1 (third constraint) and 5.1, step 6 (the recorded amendment; SEMANTICS-MIGRATION-PLAN.md itself is not edited by this commit) |
| h. After S3 the DRI reviews: residual count zero; Tier 0 and Tier A green in Python and Lean; at least two thirds of the 67 soft-norms checks as T1 or T2 without a coarse `view` hook, T1 and T2 reported separately; item e closed. If the gate fails, keep S2's generic multi-fault generator and stop migration. S4 onward needs a separate decision | section 7 (authorisation line, continuation gate); section 10, last bullet |
| Scope: S1c moved to S4 | section 7 (S1c row removed, S4 row and totals); 6.1 (Python and Lean in S0 to S3) |
