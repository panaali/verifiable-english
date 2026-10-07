# readings-defaults, Python and English work items: DELTA

Branch `readings-defaults/py`, from `1e15ef69` (spec draft 2, plan draft 3), 2026-10-07. Scope: the Python, English
and tooling items of [readings-defaults-PLAN.md](../spec/readings-defaults-PLAN.md) that do not wait for the Lean
batches (RD-1, RD-2a, RD-3 Lean, RD-4a). No Lean file changed; the spec requires no Rust. No model was called.

## What changed, by class

| Class | Change | Spec |
|---|---|---|
| `wording` (needs the DRI's signature, HUMAN) | The `<reading>` slot: when a set's candidates differ beyond the deontic verb, each candidate's own rendered sentence in italics without its final period; "reading <i>" is never shown. Verb-only sets keep the italic verb. `ve/readings_route.py` `Wording.reading_names`, `candidate_sentence` | 2.3, review A4 |
| `wording` | New templates registered in W7's all-derivations gate: E30, E31, E32, the result R7, norm-defaults' pair sentence as an E3 line (P1), and the filled-gap sentences read as part of a shown situation's result. `unsaid__` and `unsaid--` are non-wordings. `ve/readings_s2_english.py` | 2.1, 2.2, 2.5 |
| `wording` | A used `unsaid:pair:<r>,<m>` label gets the pair sentence as its E3 line, only for a declared obligation-permission pair. `ve/readings_s2_wording.py` `provided`, `pair_premise` | 2.2 |
| lint | `tools/relay_lint.py`: no `ve/readings*.py` module holds a reserved completion name (read with Python's `ast`); a non-wording guard carries `# relay-lint: non-wording` | plan RD-2b |
| tooling | `tools/lean_decided_share.py`: sums the span bytes of Lean's `decided_units`, with E2's qualifiers; decides nothing; refuses a malformed answer | 1.10, 10; plan 3.9, RD-5 |
| docs | composition-s2.md 2.1's `<reading>` row amended | 2.3 |

Fixtures whose English changed (verdicts unchanged), all from the A4 slot: S1's E19 and E21 "Under <reading>" lines
(`test_h3_e19_case_3_on_k12…`, `test_e21_between_two_assertions`); S2a's M9 (E7 and E12 lines), M12 and its limitation
variant, and the power-right fixture (E12 lines). M8's readings now render differently (one carries the precedence
note); before, both were "reading <i>".

## Decisions taken here (for the reviewers)

1. **Rule candidates carry `rule_notes`.** M8's two readings differ only in precedence, which `render_rule_sentence`
   (the renderer `reading_names` used) does not show, so the slot would name two readings with one sentence. The
   candidate sentence is the rule sentence followed by the document renderer's notes for precedence, switches, rank
   and exception conditions (`ve/surface/rights.py` `rule_notes`: "two rules differing in any of them render
   differently"). Assertions use their canonical VE sentence, read back by the English parser to the same formula;
   rights units the rights renderer (multi-sentence, long; a point for the reader test).
2. **Two candidates shown by one sentence are refused** (`InvalidInput: two readings of <set> are shown by the same
   sentence`), Python-only English construction, never a fallback to "reading <i>".
3. **The sentence keeps its capital.** The spec's derived example shows "*every agent must help each user*"; the
   rendered sentence is kept as rendered ("*Every agent must …*"), as the `<conclusion>` slot already is, since
   lowercasing would break a sentence that starts with a name. The spec leaves exact sentences to RD-3's renderer.
4. **F-ND7's list is incomplete.** It names S2a's M8, M9 and M12 as the only S1/S2a fixtures whose English changes;
   2.3 itself lists S1's "Under <reading>" sentences, and those change on S1 sets that differ beyond the verb (above).
5. **`companion` pass-through deferred** (RD-4b's Python part). Python's W2 validation refuses unknown reading keys
   today, while Lean's readings decoder ignores keys it does not read. Accepting `companion` in Python before RD-4a's
   Lean reads it would let a companion's environment be silently ignored, so the refusal stays until RD-4a lands.

## Not done (blocked on Lean batches), with owner

| Item | Waits for |
|---|---|
| RD-2b: relay of `filled`, `fill_premises` and the inner kinds; generators over Lean's filled documents; `_placeholder_frame` deletion | RD-2a (Lean worker) |
| RD-3 Python: `Enumerated` sends `readings-verdicts`; Python's fold, `_dependencies`, `_replays`, `restrictions` deleted; rendering from Lean's `english` plan | RD-3 Lean |
| Wiring E30, E31, E32, R7 and the filled-gap lines into answers (the builders are registered and tested) | Lean's `englishPlan` (RD-3, RD-4b) |
| RD-4b Python: `companion` in W2 (decision 5), `--sentence`, per-component evidence | RD-3 and RD-4a |
| RD-5: `migrate.py`, `situations.py`, measurements (pilot branch) | RD-4b |
| The DRI's signature on the A4 wording change | HUMAN (DRI) |
| Statement re-review PASS, branch review | EXTERNAL (Astra, Fable) |

## Finding for another owner

`ve/norm_english.py` (`pair_sentence`, `unspecified_clause`) and `ve/norm_defaults_english.py` choose "a" or "an" by
the first letter only, so the pair sentence reads "Whenever an agent must help an user, …". The spec's example says
"a user". It is norm-defaults' wording (Lean may mirror it), reused verbatim here and not changed; the test pins the
reused sentence rather than the spec's text.

## Gate (AGENT, at the branch head before this file; this worktree, not a separate clean one)

- `lake build`: 776 jobs, success. `python lean/audit.py`: PASS, 425 files, 4549 theorems, standard axioms only.
  `tools/lean_statements.py --check`: PASS, 4195 statements unchanged.
- Full suite in five chunks (`-n 16`, `VE_LEAN_PREBUILT=1`, the four slow tests deselected): 1912 passed, 1 skipped;
  3921 passed, 2 skipped, 2 failed (the gate-collection baseline, fixed by pinning the new tests, then both passed);
  1794 passed, 3 skipped; 2300 passed; 1535 passed. The four slow tests alone (`-n 4`): 28 passed.
- After the gate, one fix (null and deep answer files in `lean_decided_share`), with its tests: 34 passed.
- `tools/relay_lint.py`: PASS.

## Seeded bugs (each planted, its test failed, then removed)

| # | Bug | Failing tests |
|---|---|---|
| M1 | duplicate reading sentences accepted | `test_sentence_slots` |
| M2 | final period kept in the slot | `test_sentence_slots` and 7 S2 document tests |
| M3 | `unsaid__` names allowed in English | `test_reserved_names_are_never_shown[unsaid__…]` |
| M4 | pair label's permission not checked | `test_a_pair_label_that_names_no_declared_pair_is_refused[…,asks]` |
| M5 | rule notes dropped from rule readings | `test_m8_enumerated_conflict_under_one_reading`, `test_review_b2_…` |
| M6 | duplicate decided units summed | `test_a_malformed_answer_is_refused_never_summed[a unit twice]`, one more |
| M7 | reserved-name lint skips every literal | 6 `test_seeded_readings_modules` cases |
