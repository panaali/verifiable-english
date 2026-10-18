# RD-8: senses in `ve document` (Lean and Python)

Batch RD-8 of [readings-defaults-PLAN.md](../../spec/readings-defaults-PLAN.md), section 6, on branch
`readings-defaults/rd8` from `167eb8ff`. Built by one builder session on 2026-10-07; no model was called. The
numbers below are copied from [evidence.json](evidence.json), and `tests/test_readings_defaults_rd8_report.py`
checks this file against it.

## What a user sees

A `ve-document@1` front matter may name `"senses": {"packs": [...], "own": [...], "defaults": {word: index}}`.
Every `surface: english` fence of such a document is read by Lean's sense reader instead of Python's English
reader: the fences go, in unit order, in one `senses.read` request, one sentence each. Each unit gets Lean's
formula, and its environment (and so its meaning id) is Lean's projected environment. Front-matter defaults
read exactly as the same text with the lines `In this document, <word> means <gloss>.` written first.

New refusals, each Lean's text relayed verbatim:

- `InvalidInput: defaults are given both in the front matter and as lines` (the plan's text);
- `InvalidInput: the front matter gives <word> the default <index>, which is not one of its senses`;
- `InvalidInput: English fence <n> holds <m> sentences; each VE fence must contain exactly one sentence`;
- a fence whose sentence has candidates, without a reading set for its unit, is refused with Lean's `Unresolved`
  text, for example `Sentence 1 uses odd, which has two senses here, and only strange gives a reading of this
  sentence. Add the line "In this document, odd means strange." to say so.`
  Under front-matter defaults the number counts the author's fences only, and the text asks for a default:
  `... Add the default "odd": 1 to the front matter to say so.`;
- fence identities refused by their fault, for example `InvalidInput: unit id u1 names more than one English fence`.

`ve senses check` retains its source-mode JSON shape (`readDocument_source`). Lean includes unresolved English
only for document fence requests.

## What changed

- **Lean.** `readWithSenses` now lexes and calls `readSents`, the token-level reader (one reader for a source and
  for fences). `lean/VE/Senses/Document.lean` (new): `SenseText` (a source, or fences), `fenceSents`,
  `badDefault`, `defaultSents` (the defaults rendered with `Assignment.lines` and lexed), `documentInput`,
  `readDocument`, `fenceUnits` (each fence's unit, or a preamble line) and `unresolvedText`.
  `lean/VE/Senses/Run.lean`: the request takes `source` or `fences`, and optional `defaults`; an open fence unit gets
  `text`; a fence request's admitted answer gets `fences` (a unit index, or `"line"`, since the transport reads no
  JSON null). `lean/VE/Senses/DocumentExamples.lean` (new): the fixtures as `#guard`.
- **Python.** `ve/senses_document.py` (new) reads the pack files (a bundled name, or a path relative to the
  document) and maps Lean's answer to units. `ve/document.py` accepts the `senses` key, sends the fences, bypasses
  `parse_english` for them, and checks in the projected environment. `ve/backends/senses.py` gains `read_fences`
  and validates the new fields (`fences` against the number sent, `text` exactly on open units).
  `tools/relay_lint.py` has a third rule: no module of the senses path names `parse_english`, and no `senses`
  branch of `ve/document.py` does. No Python sense logic was added: Python counts, searches and classifies nothing.
- **Bookkeeping.** `lean/VE.lean`, `lean/VE/Audit.lean`, `lean/VE/Route/frozen-sources.sha256`, `lean/axioms.txt`,
  `lean/statements.txt`, `lean/declarations.txt`, `lean/predicates.txt`, `tools/trust-classes.json`,
  `ve/assurance-manifest.json` (the `Run.lean` pin, the theorems and tests of `senses.read`, the call site
  `ve.backends.senses:_read`), `docs/spec/assurance-manifest.md`, `tools/layer_policy.py`, `.importlinter`,
  `docs/ARCHITECTURE-LAYERS.md`, `tools/gate-collection.json`.

## Theorems (all proved, no `sorry`)

| Theorem | Statement in words |
|---|---|
| `VE.Senses.readSents_ok` | The facts of sentences the reader accepts: preamble, projection, S2's checks, the body. |
| `VE.Senses.readDocument_source` | With no defaults, a source reads exactly as `readWithSenses` reads it. |
| `VE.Senses.readDocument_bad_default` | A default that names no sense of its word is refused with its text. |
| `VE.Senses.badDefault_none` | No bad default exactly when every default names a sense of its word. |
| `VE.Senses.readDocument_both` | Defaults together with a written preamble line are refused. |
| `VE.Senses.readDocument_defaults` | Defaults are read as their rendered lines put before the text's sentences. |
| `VE.Senses.defaults_read_as_lines` | When a source lexes to those lines followed by the text, the request with defaults gets `readWithSenses`'s answer on that source. |
| `VE.Senses.fenceSents_ok` | Every fence of an accepted list is exactly one sentence, in order. |
| `VE.Senses.readDocument_ok` | The facts of an accepted request: the dictionary passed and the reader accepted the sentences. |
| `VE.Senses.documentInput_fences` | The sentences of a fence request are the rendered lines, then one sentence per fence. |
| `VE.Senses.document_unit_sound` | A fence mapped to a unit is its own sentence, and a resolved unit's formula is the one reading of that sentence under the projection. |
| `VE.Senses.document_line_sound` | A fence mapped to no unit is a preamble line with one derivation under the preamble grammar. |

The section lists no Lean statements of its own, so these 12 were written for this batch; they are not in the
approved statement spec (see *Deferred*).

## Fixtures (plan, section 6)

- s1, s9, s16 and s22 as fences, in Lean (`DocumentExamples.lean`) and through `ve document`
  (`tests/test_senses_document.py`): the same formulas, meaning ids and refusals as `ve senses check` on the same
  text. The document environment has no English overlay, so the constant reads `Riddle` where the spec writes
  `the riddle`.
- A document with `{"funny": 1, "odd": 1}` reads as s9 with its two lines written: the same formula, meaning id
  and projected environment.
- The relay lint rule, seeded both ways; a run with `parse_english` patched to fail loads a senses document and
  fails a plain one.
- One fence read by the document and by `ve senses check` gets the same answer for 12 texts, among them NBSP,
  double space, tab, `\r`, curly quotes, U+212A, dotted I and a control character.

Tests added: 67 in `tests/test_senses_document.py`, 12 in `tests/test_relay_lint.py` (79 in all).

## Seeded bugs (each made a check fail, then was removed)

| Id | Behaviour | File | Caught by |
|---|---|---|---|
| M1 | defaults lines go before the text | `lean/VE/Senses/Document.lean` | lake build: readDocument_defaults and document_unit_sound no longer prove |
| M2 | defaults together with a written line are refused | `lean/VE/Senses/Document.lean` | lake build: readDocument_both no longer proves |
| M3 | each fence is one sentence | `lean/VE/Senses/Document.lean` | lake build: fenceSents_ok no longer proves |
| M4 | the Unresolved text is Lean's (one candidate) | `lean/VE/Senses/Document.lean` | lake build: three #guard fixtures of VE.Senses.DocumentExamples fail |
| M5 | a senses document's fences bypass parse_english | `ve/document.py` | pytest: 5 tests of tests/test_senses_document.py fail (with -x), among them test_s9_formula_and_meaning_id_are_leans |
| M6 | the relay checks Lean's fence map | `ve/backends/senses.py` | pytest: 6 cases of test_genuine_fence_answer_mutations_are_rejected fail |
| M7 | an open fence is refused unless its unit has a reading set | `ve/senses_document.py` | pytest: test_open_fence_refused_with_leans_unresolved_text[s16] and test_one_fence_gets_the_answer_senses_check_gives fail |
| M8 | the relay lint forbids parse_english on the senses path | `tools/relay_lint.py` | pytest: 4 cases of test_seeded_senses_modules fail (with -x) |

M4 with only the route rebuilt also stops the Python suite, whose Lean prebuild check fails on the same
fixtures.

The report's own test (`tests/test_readings_defaults_rd8_report.py`, 8 tests, added after the gate run) was
seeded with three errors in this file, one at a time: a changed pytest count, a dropped mutant row and a
renamed theorem. Each made it fail.

## Historical gate (run on `787781a9`, before the report commit)

| Check | Result |
|---|---|
| `lake build` | Build completed successfully (789 jobs) |
| `python3 lean/audit.py` | PASS: 433 source files, 4684 theorems, standard axioms only |
| `python3 VE/Route/frozen.py` | PASS |
| `tools/lean_statements.py --check` | PASS: 4323 statements |
| `tools/check_lean_imports.py` | layer graph kept (433 modules) |
| `tools/check_python_layers.py` | 1 contract kept, 0 broken |
| `tools/gate_collection.py --check` | PASS: 11891 IDs |
| `tools/relay_lint.py` | PASS (three rules) |
| full pytest, 5 file chunks with `-n 16`, `VE_LEAN_PREBUILT=1`, 4 slow tests deselected | 2022 + 3929 + 1877 + 2440 + 1578 passed, 1 + 2 + 4 + 0 + 0 skipped, 0 failed |
| the 4 slow tests alone (`-n 4`) | 28 passed |
| `tools/` tests | 51 passed |

Not run: `tools/gate.py` (the hermetic gate that rebuilds every toolchain from scratch); Rust was not touched and
has no senses code. `tools/trust_map.py --check` fails as on the base: the base's own overage is S 9334 and
V 31353; this batch adds S +82 (`Document.lean` +79, `Read.lean` +3) and V +20 (`Run.lean`), to S 9416 and
V 31373. The baseline was not rewritten, since that would sign the base's growth under this batch.

## Decisions taken here

1. **Fences on the wire.** The plan says each fence is sent "one sentence per fence, in one `senses.read` request".
   Joining the fences into one source would let a fence without a full stop merge with the next, and only a
   count in Python could catch it. So the request carries `fences`, Lean lexes each one and refuses a fence that is
   not one sentence. Defaults are put before the text as lexed lines (`readDocument_defaults`), which is the same
   reading as prepending them to the source text (`defaults_read_as_lines`, and the s9 fixtures).
2. **Preamble lines in fences** are allowed when the front matter has no defaults; their units carry no claim
   (`fences` maps them to `"line"`). This is what makes the plan's "both" refusal reachable in a document.
3. **The order of defaults** is the order of the words: the front matter is a JSON object, which has no order.
4. **Refusals that have no Lean text yet.** The sense faults (`UnknownGloss`, `Collision`, ...) have codes and
   arguments but no English in Lean (the senses spec's texts of 3.2 are not built). A document relays the code as
   the message and Lean's whole reading as the diagnostic; S2's outcomes carry their text.
5. **Routes not read with senses.** `soft-norms@0`, `rights@0`, `reports@0`, `norm-defaults@0`, `readings@1`, the
   quantity route and `ve-document@2` are refused with `UnsupportedProfile`, since each of them builds its own
   formula environment.

## Deferred (owner: orchestrator)

- EXTERNAL (Astra + Fable): review of the 12 statements above, which the plan says RD-8's statements need before
  their build; they were written in this batch.
- EXTERNAL (Astra + Fable) and HUMAN (a reader): the English of `unresolvedText` for several words and for several
  candidates of several words, which the senses plan does not give; and the new refusal texts.
- HUMAN: the user-visible `senses` key.

## Review fixes and final gate

The B review identified three code issues. Lean now receives fence IDs and the units with reading sets, and it
refuses the first uncovered open fence itself. The Python document path only relays that refusal. Fence responses
are checked against the request's exact sentence start, including written preamble fences and rendered defaults.
Source-mode open units keep their original JSON shape; only fence-mode units contain `text`. Regression tests
cover the original failing examples and adjacent cases: two open fences with only one reading set, an omitted
reading-set list, and coherent shifts of both units and sense-map occurrences by one or ten sentences.

The historical gate above describes its actual earlier run. The final-HEAD gate is recorded separately in
`evidence.json` as `final_gate`. Its `HEAD` target is symbolic because a commit cannot embed its own hash. The
report commit completes the commit list as the `self` entry; the report test checks the saved list and final target.
The final gate runs `lake build`, `python3 lean/audit.py`, and the full pytest suite in the foreground on that
exact committed HEAD.

The first full pytest attempt exposed stale generated bookkeeping: the assurance table, the gate's collected
test IDs, and a one-space separator in the frozen Lean source inventory. The generated table and collection
were refreshed, the separator restored, and all five directly affected tests passed before the final gate.

## Second review round (rd-8-looprecheck1)

| Finding | Fix | Commit |
|---|---|---|
| A reading set's `unit` of another type (`["u1"]`, a dict) made `ve document check` raise `TypeError` | `read_senses` takes the raw reading sets and keeps string units only (`covered_units`); only a string id names a fence, which also closes a unit id equal to its fence's list id. A type-confusion test replaces every front-matter node outside the environment, and every node holding the unit id at once, by nine values | `b0739788` |
| Under defaults the open-fence text counted the hidden default lines and asked for a line that is then refused | Lean's `documentText` numbers the author's own sentences and, with defaults, asks for a front-matter default; the runner's unit text and its refusal share it. `#guard` fixtures for each text case under defaults; a test that following the advice admits the document | `60914d2c` |
| Duplicate fence ids were reported as malformed identities | Lean's `fenceIdsProblem` names the fault (count, empty, duplicate, repeated or unknown reading-set unit) | `60914d2c` |
| The report test found its commit with `git log --all` | It reads HEAD's history only | `4fe6ceb5` |
| No test compared an admitted open fence's `text` with its refusal | Six cases (one and several candidates, with and without defaults) and the document's relayed text | `60914d2c` |

This round adds V +15 (`fenceIdsProblem` in `Run.lean`); S is unchanged. The DRI's 20:15Z ruling on `text` in
`ve senses check` is still open and was not touched.

Gate on `4fe6ceb5` (the code of this commit), in the foreground: `lake build` completed (789 jobs);
`python3 lean/audit.py` PASS (433 source files, 4684 theorems); full pytest in 5 file chunks with `-n 16`,
`VE_LEAN_PREBUILT=1` and the 4 slow tests deselected: 2022 + 3958 + 1858 + 2464 + 1578 passed, 1 + 2 + 3 + 0 + 0
skipped, 0 failed; the 4 slow tests alone: 28 passed; `tools/` tests: 38 passed.
