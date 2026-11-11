# df-5b: `--assume-no-exception` at one situation, and W7 on DE10-DE13

No DRI signature is reserved. The CLI row is SIGNED (reviews/dri-decisions-20261110-et-5b-df-5b.md item 2). Condition
(iii) was restated by the DRI at the builder's request (reviews/dri-decisions-20261110-df-5b.md, item 3 final): on main
no request reaches spec 5 row 1's text (the layered decoder refuses `weighing@0` first, df-5's DF-θ guards).

## Delivered (task deliverables and DRI conditions)

| Row | Where | Test or evidence |
| --- | --- | --- |
| (1) A question object naming `situation` (with `record`, `observations`, `query`) sends df-5's `defaults-zone` request through `ve.defaults` (`ask_zone`; `answer` binds it, R8) and prints Lean's answer and the English of the rows Lean chose | `ve/document/cli.py` `_assume_no_exception`; `ve/defaults.py` `ask_zone` | `test_every_cli_fixture_answers_as_the_service_mode`, `test_situated_routing_and_refusals` |
| (2) W7's all-derivations gate for DE10/DE10′/DE10″, DE10f, DE11 (after DE10 and after DE6′) and DE13: each sentence and each row inside DE10″ has one derivation over S2's wordings and Lean's zone words, its own, with no generated name | `ve/defaults_english.py` `templates`, `Gate`; `ve/readings_s2_english.py` `derivations`/`gated` take the template set (no second gate) | `test_w7_every_zone_sentence_has_one_derivation_its_own`, `test_w7_refuses_a_sentence_two_wordings_read` |
| (i) every other call byte-identical | `docs/defeasible/df-5b/fixtures/unchanged.json` (P-1 x3, P-3 x2, CE4; recorded with main's Python, all exit 0) | `test_every_other_call_prints_what_it_printed_before`; `tests/test_document_chain.py` (saved answers) |
| (ii) one CLI fixture per 8.6 case, answer = the service mode's for the request sent | fixtures DF-μ, DF-μ′, DF-μ″, DF-δz, DF-ξ, DF-ξ′, DF-π′, plus a record, X's labels, `unknown` (budget 26 > 12) and the largest in budget (6 operators, 12 atoms) | `test_every_cli_fixture_answers_as_the_service_mode` (English literal, from spec 8.6 and 4); `test_each_fixture_is_df_5s_request` |
| (iii) as restated | `fixtures/weighing.ve.md` | `test_weighing_documents_are_refused_by_lean_on_the_cli_path`: CLI and `ask_zone` raise the service mode's own text for the same request, print nothing |
| (iv) df-5's conditions | unchanged files; `git diff <base> -- lean` is empty (0 lines), so the service is main's and `conservativity.json` stands | `tests/test_defaults_zone.py` (selected); `tests/test_route_row_schemas.py` 32 passed on HEAD (not in the selection; run by hand) |

Not delivered: nothing of the task. Left to df-1bbc (its row): W7 for DE1-DE9 and DE6/DE6′'s heads. Limit (review C):
the gate's slot classes are strings, so two acts with the same phrase ("do x") are one value; df-1bbc's "shared act
phrase" owns that.

## Seeded bugs (Python only: no Lean or Rust product code changed)

`mutants.json`, each with its file, exact mutation and failing test (run by a throwaway script; tree restored):
S1 `observations` dropped from the request (task bug 1; every fixture, DF-ξ's included, fails);
S2 DE10's form picked in Python in `zone()` (task bug 2; DF-δz fails); S3 a call with no situation routed to the zone
(task bug 3; condition (i) fails); S4 empty observations (DF-μ); S5 gate checks nothing; S6 DE10″'s rows ungated;
S7 no labels (noCompletion fixture); S8 DE11 after DE6′ ungated; S9 S2's wordings only. The two both-sides tests also
joined `tests/test_defaults_checks.py`'s check sweep; its one survivor (`layered.get("rights", [])`, a required
member) became `layered["rights"]`.

## Trust, size, bytes

Trust: `uv run python tools/trust_map.py --check`: K +0, S +0, D +0, G +0 (no Lean line). Size: 467 added and 23
deleted before this report (`git diff --numstat <base>`), fixtures included. Pilot bytes expected to move: 0 (no pilot
document asks a zone question).

## Runs

Final selected run on the committed tree b47367d448 (`MAC_PYTEST_NO_DEFER=1 zsh .../mac-pytest.sh --select -- --base
<base> --run`, run df-5b-d6fae4e8-t329294): exit 0, 4 shards, 111 units, 111 passed, 0 failed (36 + 25 + 26 + 24),
`tests/test_defaults_checks.py` and `tests/test_defaults_zone_cli.py` among them. `regen_generated.py --check`: 38
entries up to date. No test of main-known-red.txt was touched.

## Self-review against BUILDER-CHECKLIST

SELF-REVIEW: 2 A, 6 B, 6 C; fixed 12 (all A and B; C: service compared on the request sent, mutations recorded exactly,
size, the extra refusal cases; C1 stated as fault order in DELTA; C3 kept: the member check is the CLI's).

1. PASS: the zone answer is `run`'s schema-checked row, bound by `bind_zone`; only VEError escapes (reviewer's CLI fuzz).
2. PASS: the table above; no Python decision (Lean's form, zone and rows are relayed; the gate refuses only).
3. PASS: `mutants.json` S1-S9, each failing a named test.
4. PASS: `test_every_other_call_prints_what_it_printed_before`; `tests/test_document_chain.py` 168 passed with the
   judgments and binding-inventory sweeps.
5. PASS: `bind_zone` (df-5's tests) binds every name; the CLI fixtures compare the whole sent request.
6. PASS: final selected run on the committed tree b47367d448 (Runs, above); the chain runs the gate.
7. PASS: DELTA D1 SIGNED by the DRI decision; no other row.
8. PASS: DELTA D1 lists the base outputs (both main refusals) and every new refusal.
9. PASS: `tools/select_tests.py` selects `tests/test_defaults_zone_cli.py` and `tests/test_defaults_checks.py`.
10. N.A.: no Lean statement or proof.
11. PASS: the `budget` fixture is `unknown`, never an answer; the largest in-budget fixture answers.
12. PASS: one extra Lean call per question (the layered row); no per-candidate calls.
13. N.A.: no test removed or renamed.
14. PASS: both directions (`test_situated_routing_and_refusals`, both W7 tests); spec re-read: 8.6 rows against
    docs/spec/defeasible.md:1441-1452, section 5 row 1 against :305, DF-1b's flag against defeasible-PLAN.md:1075.
15. PASS: claims above each cite a test or command; no deferred deliverable; limits are Lean's (`zoneSizes`).
