# tm-elab-unknown: an elaboration error in the mutant's own text is INVALID

Status: built, ready for review; no DRI signature needed, nothing reserved. Branch infra/tm-elab-unknown.
Changed: `tools/trust_mutants.py` `REFUSED` adds "Function expected", "Invalid dotted identifier notation" and
"don't know how to synthesize implicit argument"; the existing span rule (`invalid`) decides as for "Invalid field".
Result: all 12 recorded UNKNOWN ids (df-5's 11, et-4b's M034) become INVALID under Lean's own error positions.
Open: the rule covers those three error families, not every elaboration error (type mismatch and instance failures
stay UNKNOWN, review F11/F12, hunt H2/H3: section "Scope"). No DELTA (tool only), trust +0, no Lean change.

Item tm-elab-unknown (infra; DRI row 2026-11-08 06:20Z, reviews/dri-decisions-20261108-df-5-tm.md item 2; task
file by the DRI decider, lead proxy 1201Z Q3, reviews/dri-decisions-20261108-lp1201.md item 3; both files in
manage-agents).

## The change

`tools/trust_mutants.py`, `REFUSED` (the refusals `refused` reads) and its comment, plus the module docstring's
INVALID line. A mutant is INVALID only when every error Lean reports in the mutated declaration is a refusal
located inside the mutant's own text (`invalid`'s `edit`, a character range) and outside every tactic block. That
rule is the one "Invalid field" already used (review F12, hunt Q9, R3); this item changes only which messages count
as a refusal:

| message (as Lean 4 starts it) | records | before | now, inside the mutant's text | now, outside it |
|---|---|---|---|---|
| `Function expected at` | df-5 M041, M058, M073 | UNKNOWN | INVALID | UNKNOWN |
| `Invalid dotted identifier notation` | df-5 M170, M176, M201, M206, M356, M362, M395, M400 | UNKNOWN | INVALID | UNKNOWN |
| `don't know how to synthesize implicit argument` | et-4b M034 | UNKNOWN | INVALID | UNKNOWN |

Nothing else changes: KILLED and SURVIVOR judgement, the barrier, `NO_ANSWER` (a refusal that quotes Lean's budget is
still none), and every other class. `invalid`, `refused` and `in_tactic` have no diff (`git diff main...HEAD --
tools/trust_mutants.py`: two hunks, the docstring and `REFUSED` with its comment).

## Scope: which elaboration errors

The DRI row says "classify any elaboration error located inside the mutated span as INVALID"; the task's FIX line
says "same class and same reporting as the existing Invalid field rule" and "No change to ... any other class". So
the rule adds the error families the two records hold, by message, to the same class. It does not make every
elaboration error a refusal, because two families the tool already keeps UNKNOWN on purpose are elaboration errors
too:

- `Type mismatch` / `Application type mismatch`: a term-mode proof that is false or stuck gives one (review F11), so
  inside the span it can be a proof the mutant broke, not text Lean refused. Kept UNKNOWN:
  `test_an_elaboration_error_in_the_mutants_own_text_is_invalid[M041-type-mismatch]`,
  `[M034-beside-a-type-mismatch]`, `test_invalid_only_when_lean_refuses_the_mutated_text[type-mismatch]`.
- `failed to synthesize` (an instance): instance search fails alike on a missing instance and on its own size or
  heartbeat budget (hunt H2, H3). Kept UNKNOWN: `test_invalid_only_when_lean_refuses_the_mutated_text[synthesize]`.

If the DRI wants every elaboration error inside the span to be INVALID, that is a wider rule than this item's
"no change to any other class" and needs its own row.

"Function expected" had been taken out of `REFUSED` by speed-trustmut TM58 (hunt N5: a coercion's instance search
out of its size budget says it). Since hunt Q9 a refusal counts only inside the mutant's own text, and the N5 form's
error sits on the applied term `x`, outside the mutated literal, so N5 stays UNKNOWN:
`test_a_hunt_form_gets_no_verdict_that_hides_it[N5]` passes on this branch (a real Lean run; command in "Runs").
What remains: a mutant whose own text is a term with a `CoeFun` instance that runs out of budget would now be
INVALID. No operator in `OPERATORS` writes such a head (they write `[]`, literals, `.take 1`, `.drop 1`, ...); a
mutant that did would also fail to elaborate in the repository at the project's settings.

## Reclassified ids under the new rule

Probe: `docs/infra/tm-elab-unknown/reclass.py` writes each recorded UNKNOWN mutant (its `before` -> `after` on its
line in this tree's file), elaborates it with `lake env lean`, keeps the errors inside the mutated declaration and
asks this branch's `invalid` for the verdict. Command (run from the worktree):
`PATH=~/.elan/bin:$PATH uv run python -I docs/infra/tm-elab-unknown/reclass.py . <manage-agents>/reviews/tm-targeted/df-5-df-5-c050431.json <manage-agents>/reviews/tm-targeted/et-4b-et-4b-c050416.json`.
Output: [reclass.txt](reclass.txt) (12 lines, all `UNKNOWN -> INVALID`; produced by the same script before its work
directory became a `tempfile`).

| record | id | line (this tree) | edit columns | Lean's errors (line:column) | record | new rule |
|---|---|---|---|---|---|---|
| df-5 | M041 | ZoneWire.lean:400 | 20-22 | 400:20 Function expected | UNKNOWN | INVALID |
| df-5 | M058 | ZoneWire.lean:402 | 20-22 | 402:20 Function expected | UNKNOWN | INVALID |
| df-5 | M073 | ZoneWire.lean:404 | 24-26 | 404:24 Function expected | UNKNOWN | INVALID |
| df-5 | M170 | ZoneWire.lean:401 | 15-96 | 401:26, :44, :61, :80 Invalid dotted identifier | UNKNOWN | INVALID |
| df-5 | M176 | ZoneWire.lean:401 | 15-98 | 401:26, :44, :61, :80 Invalid dotted identifier | UNKNOWN | INVALID |
| df-5 | M201 | ZoneWire.lean:403 | 15-101 | 403:25, :43, :65, :85 Invalid dotted identifier | UNKNOWN | INVALID |
| df-5 | M206 | ZoneWire.lean:403 | 15-103 | 403:25, :43, :65, :85 Invalid dotted identifier | UNKNOWN | INVALID |
| df-5 | M356 | ZoneWire.lean:401 | 15-104 | 401:26, :44, :61, :80 Invalid dotted identifier | UNKNOWN | INVALID |
| df-5 | M362 | ZoneWire.lean:401 | 15-96 | 401:26, :44, :61, :80 Invalid dotted identifier | UNKNOWN | INVALID |
| df-5 | M395 | ZoneWire.lean:403 | 15-109 | 403:25, :43, :65, :85 Invalid dotted identifier | UNKNOWN | INVALID |
| df-5 | M400 | ZoneWire.lean:403 | 15-101 | 403:25, :43, :65, :85 Invalid dotted identifier | UNKNOWN | INVALID |
| et-4b | M034 | Run.lean:127 (record 131) | 26-28 | 127:26 twice, implicit argument `α` | UNKNOWN | INVALID |

Notes: ZoneWire.lean:398-404 is the same in this tree as in df-5's record (the record's lines). Run.lean's
`softCase` moved up 4 lines since et-4b's record (6ece79038, lines 123-132); the probe finds the line by the
occurrence of the mutant's `before` nearest the record's line, and the declaration is the same text. et-4b's other
two list-empty ids (M066, M097, already ALLOWED in the record) were not probed: their `before` text is no longer in
`runCaseE`. The probe's Lean run of M034 also printed errors at Run.lean:329 and :385 (stale Acts oleans in this
worktree); they are outside the mutated declaration, which is all the tool reads for INVALID.

## Tests (tests/test_trust_mutants.py, no Lean unless named)

- `test_an_elaboration_error_in_the_mutants_own_text_is_invalid[14 cases]`: the mutated declarations of M041, M170,
  M034 and M158 copied from the mutated files (checked equal to the files `lake env lean` elaborated) with Lean's
  messages and columns. Inside the edit: M041, M170 (four errors), M034 (two) -> INVALID; M158 "Invalid field"
  -> INVALID, unchanged. The same error just after the edit (M041 col 22, M034 col 28), just before it (M170 col 14),
  on the next line (M041, M170, M034, M158), or one of two outside (M170) -> UNKNOWN; a type mismatch at M041's
  edit, or beside M034's refusal -> UNKNOWN.
- `test_invalid_only_when_lean_refuses_the_mutated_text`: rows `implicit` and `function-expected` move from
  UNKNOWN to INVALID (same ids; the comment names this item); new rows `implicit-in-tactic`,
  `function-expected-elsewhere`, `dotted-in-tactic` (UNKNOWN), `dotted` (INVALID), `implicit-budget` (a refusal
  quoting Lean's heartbeats: UNKNOWN).
- Unchanged and rerun (Lean-backed): `test_a_hunt_form_gets_no_verdict_that_hides_it[N5]`, `[H2]`, `[N10]`,
  `test_a_proof_term_in_the_mutated_definition_is_no_refusal`, `test_a_name_lean_does_not_know_is_invalid`.

## Seeded bugs (all in tools/trust_mutants.py, Python; each planted, run, then restored with git checkout)

Command for each: `uv run pytest -q tests/test_trust_mutants.py -k "elaboration_error_in_the_mutants_own_text or
invalid_only_when_lean_refuses"`.

| # | bug | failing tests |
|---|---|---|
| S1 | `invalid`'s span widened by one line (`edit[1]` -> end of the next line) | `test_an_elaboration_error_in_the_mutants_own_text_is_invalid[M041-next-line]`, `[M170-next-line]`, `[M034-next-line]`, `[M158-invalid-field-next-line]`, `[M041-after-the-edit]`, `[M034-after-the-edit]` (6 failed, 38 passed) |
| S2 | `Function expected` dropped from `REFUSED` | `[M041]`, `test_invalid_only_when_lean_refuses_the_mutated_text[function-expected]` (2 failed) |
| S3 | `dotted identifier notation` dropped from `REFUSED` | `[M170]`, `test_invalid_only_when_lean_refuses_the_mutated_text[dotted]` (2 failed) |
| S4 | `don't know how to synthesize implicit argument` dropped | `[M034]`, `test_invalid_only_when_lean_refuses_the_mutated_text[implicit]` (2 failed) |
| S5 | `Type mismatch` admitted to `REFUSED` | `[M041-type-mismatch]`, `[M034-beside-a-type-mismatch]`, `test_invalid_only_when_lean_refuses_the_mutated_text[type-mismatch]` (3 failed) |

No Lean or Rust product code changed, so no seeded bug there.

## Runs

- New and edited unit tests: `uv run pytest -q tests/test_trust_mutants.py -k "elaboration_error_in_the_mutants_own_text
  or invalid_only_when_lean_refuses or invalid_needs_every_error"`: 52 passed (before the fixture line was wrapped;
  after it, `-k elaboration_error_in_the_mutants_own_text`: 14 passed).
- Lean-backed: `uv run pytest -q tests/test_trust_mutants.py -k "hunt_form_gets_no_verdict_that_hides_it and (N5 or
  H2 or N10) or proof_term_in_the_mutated_definition_is_no_refusal or name_lean_does_not_know_is_invalid"`: 5 passed.
- `uv run python tools/trust_map.py --check`: `against 1a39ebef39c0: K +0, S +0, D +0, G +0, tied +0, unclassified
  +0, trusted +0` and `PASS`. No trust growth.
- `uv run python tools/regen_generated.py --check` on the tool commit: exit 0, 37 entries; `--write` once after
  this probe script was added (it is a codemap input: docs/codemap/docs__infra.md).
- Selected tests: `zsh manage-agents/mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` on
  ffedd5fbc (ran on the VM: ve-mac-1 unreachable, cloud pools full): 35 units recorded; 34 reported `exit 0`
  (tests/test_trust_mutants.py in 4 chunks among them) before the agent harness stopped the job at its
  background limit; the one unit left, `tests/test_trust_mutants_probe_scope.py`, was then run alone
  (`mac-pytest.sh -- -q tests/test_trust_mutants_probe_scope.py`): 30 passed. `tests/test_test_chunks.py` was
  deferred by select_tests to the chain gate ("over 120 s selected only for weak reasons"). No failure, so
  no main-known-red test was met.
- Not run: `tools/gate.py` (the chain runs it on the final HEAD); a trust_mutants sweep, `lake build` and
  `lean/audit.py` (no Lean change, nothing trusted grows: build-checklist 13a does not apply).

## DELTA

None: tool-only change in `tools/trust_mutants.py` (the trust-mutant classifier); no output of the VE product
(checker verdicts, diagnostics, CLI, schemas) changes, so there is no DELTA.md and no ruling cell.

## Spec re-read

- "an elaboration error whose reported position lies inside the mutated span -> INVALID (same class and same
  reporting as the existing Invalid field rule). An error outside the span stays UNKNOWN" against
  manage-agents/prompts/tm-elab-unknown.txt (FIX line): same class (`REFUSED`), same reporting (`invalid`'s detail
  `brief(errors[0][2])`), span = `invalid`'s `edit`; outside -> UNKNOWN (tests `*-next-line`, `*-after-the-edit`).
- "Kill or survive results stay as they are" against reviews/dri-decisions-20261108-df-5-tm.md:12: `settle` and
  `judge` have no diff.
- "any elaboration error" against the same line: narrowed by the task's "No change to ... any other class" (section
  "Scope").

## Commits (main..HEAD --no-merges)

`git log --oneline main..HEAD --no-merges` before this report's last commit (which adds only these run results):

- ad9951f14 the rule (`REFUSED`) and the tests
- c294c677d REPORT, reclass.py, reclass.txt
- ffedd5fbc regenerate the codemap

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A., no relayed route or schema touched.
2. Deliverables: PASS, the FIX (`REFUSED`), the TESTS line (inside/outside/Invalid field cases:
   `test_an_elaboration_error_in_the_mutants_own_text_is_invalid`), the seeded bug (S1), the report with the
   reclassified ids (table above, reclass.txt); no Python copy of a Lean decision, no report test.
3. Tests can fail: PASS, S1-S5 above.
4. Py/Lean/Rust agree: N.A., no checker path changed; the probe uses Lean as the oracle for positions.
5. R8 binding: N.A., no relayed field.
6. Gate evidence matches HEAD: N.A. for the builder (the chain runs the gate on the final HEAD).
7. No unsigned item: PASS, no DELTA row, trust +0 (`tools/trust_map.py --check`).
8. Every user-visible change in DELTA: PASS (none: tool only; section DELTA).
9. Test selection finds the tests: PASS, `tools/repo_map.py file tools/trust_mutants.py` lists the test files;
   selected run (section Runs) included tests/test_trust_mutants.py and its probe-scope sibling.
10. Lean statements: N.A., no Lean change.
11. Budgets fail closed: PASS, a refusal that quotes Lean's budget stays UNKNOWN
    (`test_invalid_only_when_lean_refuses_the_mutated_text[implicit-budget]`); N5 stays UNKNOWN
    (`test_a_hunt_form_gets_no_verdict_that_hides_it[N5]`).
12. No CPU or memory regression: N.A., one more regex alternative on error messages.
13. Test-removed trailers: N.A., no test removed or renamed (two table rows changed their expected verdict).
14. Both directions, cited evidence, spec re-read: PASS, inside/outside pairs per id; every count cites its
    command; section "Spec re-read".
15. No overclaim / no silent cut / every check can fail / limits: PASS, the narrower-than-"any" scope is stated in
    the summary and "Scope"; S1-S5; limits N.A.
