# Q1.4bd: the `english.read` relay keeps Lean's type-error text verbatim

Status: delivered, waiting for the chain's gate. No DRI signature is reserved. Python only; no Lean, Rust or statement change.
A document's ill-typed sentence now reads `Sentence 2 was read, …`, as Lean wrote it, not `TypeMismatch: Sentence 2 was read, …`.
DELTA has one row, W1 (24 records), under R1, with the saved delta and its test.
Open: none. Next item: Q2.1, per the question-answering plan (q1-4bb's report).

Item: FOLLOW-UP of docs/question-answering/q1-4b/REPORT.md ("FOLLOW-UP (fix round 6)") and q1-4bb's "Not delivered"
(`LeanReading.rejection`'s code-worded class). Statement gate: none (no statement changes; Lean's text is already the
owner). Synthesis round 2 edits (`debates/plan-synthesis-2/edits-question-answering.md`): this item implements none
of its five edits or DEC 14. It is the relay follow-up that q1-4b and q1-4bb named, and it contradicts none of them.

## Where the code was added (deliverable 1)

- `english.read` raises one refusal: `LeanReading.rejection` (`ve/backends/english_lean.py`), whose only caller is
  `ve/english.py:_lean_reading`. Every public English entry reaches it (`parse_english`, `ve parse --surface
  english`, document checks).
- `rejection` built `cls(self.message(), span=…)` for the class Lean names. `errors._CodeWorded.__init__` adds
  `Code: ` to any text that lacks it.
- Of `english.read`'s code table (`ve/english_grammar/codes.json`), only `IllTyped` has a code-worded class
  (`TypeMismatch`). Its Lean texts (`lean/VE/EnglishGrammar/Run.lean:81-82`) carry no code.
- It is the same place as q1-4bb's "`LeanReading.rejection`'s code-worded class". That class is this one; there
  is no second site. `grep -rn "\.rejection()\|lean_reading" ve tools` finds only `ve/english.py:1760` raising it,
  plus readers of `lean_reading` (`ve/surface/time.py:227` and the shadow record) that read the status, not the text.
- The fix: `rejection` and `read_question` now build their refusal through one helper, `_refusal`. It sets the
  message and args to the caller's text as Lean wrote it. `read_question`'s copy of q1-4b fix round 6's line is
  deleted (one owner).
- Probe: `uv run ve parse --env <F> --surface english <doc>` on `Legacy is deployed. Starting from legacy, …` printed
  `"message": "TypeMismatch: Sentence 2 was read, …"` before the fix and `"message": "Sentence 2 was read, …"`
  after it (exit 2 both times, the same span).
- Python's own checkers still write `Code: text`. `_CodeWorded` is unchanged, and
  `test_an_ill_typed_document_is_refused_with_leans_text_verbatim` asserts `TypeMismatch("x").message == "TypeMismatch: x"`.

## Delivered

| Task row | Commit | Evidence |
|---|---|---|
| (1) relay Lean's text verbatim | 27cffeac2 | `_refusal` (`ve/backends/english_lean.py`). `tests/test_english_e2_responses.py::test_an_ill_typed_document_is_refused_with_leans_text_verbatim` checks that `str`, `message` and `to_dict()["message"]` are Lean's `message()`, that a `SyntaxError` refusal is Lean's too, and that Python's own `TypeMismatch` keeps its code. `tests/test_speech_polar_lean.py -k code_worded` (q1-4b's question test) passes through the shared helper |
| (2) re-record the pinned tests and head records; each changed only by the dropped prefix; a test over the saved delta | 3f38d1c26, this commit | No test or recorded fixture pinned the prefixed `english.read` text. A `grep` over every tracked file, `.gz` included, found it only in q1-4's saved base evidence, which is left as recorded. `tests/data/route-cases.jsonl` has no `TypeMismatch` row. So the head records are new: `evidence/english_read_delta.py` records 205 documents at base and head (the 163 S3 fixtures and 42 ill-typed ones). `delta.json` holds 24 rows, all `TypeMismatch`, each its base with `TypeMismatch: ` dropped; the other 181 records did not move (`english_read_delta.py check` prints `OK`). Tests: `::test_the_saved_delta_moved_only_the_dropped_code` (saved files only), `::test_the_delta_check_finds_a_planted_change` (a kept prefix, a moved span, `true` for `1`, another record moved, a missing row, head against head, empty input: each must fail the check), `::test_a_delta_record_is_refused_live_with_leans_text` (each of the 24 records read again: Lean's text, the head's span) |
| (3) `TYPING` (english_lean.py:42) | none | Left unchanged. This item changes no class, so no row of `TYPING` or `COMPARATOR_CLASSES` goes dead: Lean's `IllTyped` is still class `TypeMismatch`, and Python's reader still raises `UnknownSymbol`, `TypeMismatch` or `UnsupportedProfile` for it. The comparator compares classes, never text (`shadow_record`). In the test runs above it recorded `{"records": 25, "classes": {"agree": 25}}` |
| DELTA | this commit | [DELTA.md](DELTA.md) W1 (R1) |

Bytes: 0 expected (the task's estimate; UNVERIFIED, since no pilot was run). Nothing is claimed before a pilot
audit.

## Seeded bugs (each restored; [mutants.json](mutants.json))

| Id | Language | File | Bug | Fails |
|---|---|---|---|---|
| M1 | Python | `ve/backends/english_lean.py` | the prefix restored (`_refusal` leaves `_CodeWorded`'s message) | `test_a_delta_record_is_refused_live_with_leans_text` and the verbatim test: 25 failed; `test_speech_polar_lean.py -k code_worded`: 2 failed |
| M2 | Python | `ve/backends/english_lean.py` | the span's column ignores the line start | `test_a_delta_record_is_refused_live_with_leans_text[it3-*,it4-*]`: 8 failed |
| M3 | Python | `docs/question-answering/q1-4bd/evidence/english_read_delta.py` | the check skips the delta-equals-difference test | `test_the_delta_check_finds_a_planted_change[row missing]` |
| M4 | Python | `docs/question-answering/q1-4bd/evidence/english_read_delta.py` | the check compares with `==` (`true == 1`) | `test_the_delta_check_finds_a_planted_change[true for 1]` |

No Lean or Rust product code changed.

## Trust

`uv run python tools/trust_map.py --check`: `K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0`, PASS.
No allowance and no FOLLOW-UPS row (neither R6 nor R16 applies).

## Checks

- `tools/relay_lint.py`: PASS (19 relayed modules, 7 relayed functions, no own content diagnostic).
- `tools/regen_generated.py --check`: 34 entries checked, none stale.
- `tools/select_tests.py --base <merge-base>` selects 165 of 511 units, among them `tests/test_english_e2_responses.py`
  and `tests/test_speech_polar_lean.py`.
- Selected tests (`mac-pytest.sh --select -- --base <merge-base> --run`, at `1c3259a47`, clean tree): 151 of 511
  units ran on GitHub Actions in 2 shards (79 + 72 passed, 0 failed, exit 0). The runner deferred 14 slow files,
  selected only for weak reasons, to the chain gate. No test from `main-known-red.txt` came up.
- Not run here: the full gate (the chain runs it), `lake build` and `lean/audit.py` (no Lean change), and trust
  mutants (no trusted Lean).

## Spec re-read

- R1 (`DRI-RULINGS.md:14-18`) against W1: (a) the base quotes no name; (b) the span is kept; (c) the text is the
  same, without the code. The evidence test reads the saved delta.
- `docs/spec/english-lean.md:569`: `IllTyped`'s text has no code. The head now shows that text as written.
- `CLAUDE.md` "Who owns what": Lean owns the text, and the relay adds no wording (R8).

## Self-review against BUILDER-CHECKLIST

1. PASS: no schema or field was added. The answer is checked by the unchanged `response_problem`/`question_problem`,
   and `_refusal` reads only checked fields (`class`, `span`).
2. PASS: the three task rows and DELTA are in the table above with commits and tests. No Python copy of a Lean
   decision was added (one was deleted: `read_question`'s line). No permanent report test was added: the delta tests
   check the relay's own records. No overlap with in-flight branches (`git diff --name-only main...<b>` for every
   `lean-first/*`, `feature/*`, `infra/*` and `foundation/*` branch).
3. PASS: M1-M4 above. The comparator fails on a changed value, `true` for `1`, a missing record, head against head
   and empty input (`test_the_delta_check_finds_a_planted_change`).
4. PASS: base and head ran side by side on 205 documents, comparing code, text and span
   (`test_the_saved_delta_moved_only_the_dropped_code`). Matching uses structured keys.
5. N.A.: no new field is read from a Lean answer. The span binding is unchanged (`refusal_problem`).
6. PASS: the merge base is the current main (`e68b0dd88`). The gate runs on the final HEAD in the chain.
7. PASS: W1 cites R1 with the test it asks for. Trust growth is zero.
8. PASS: every changed record is in W1 (24 of 24), with counts from `delta.json`.
9. PASS: the selection contains `tests/test_english_e2_responses.py` and `tests/test_speech_polar_lean.py`, which
   catch M1-M4.
10. N.A.: no Lean statement or proof changed.
11. N.A.: no budget, limit or deadline path changed.
12. N.A.: no evaluation path changed. The refusal is built once, as before.
13. N.A.: no test was removed or renamed. The IllTyped test only reads its reach sentence from the evidence module.
14. PASS: both directions are tested: the refusal Lean wrote is kept, a Python-own `TypeMismatch` keeps its code, and
    another class is unchanged (`test_an_ill_typed_document_is_refused_with_leans_text_verbatim`). Every claim names
    its command. Spec re-read above.
