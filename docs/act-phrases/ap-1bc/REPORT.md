# ap-1bc build report: the words route decodes `acts@0` clauses

**No DRI signature is reserved; nothing stops the item.** DELTA has one row, recorded under the DRI decision ap-1b's
DELTA row 2 cites (the words route's `acts@0` clauses). Part (2) is cut to **ap-1be**, as the task directs, because
df-1ae (rank 58), in flight, edits `lean/VE/NormDefaults/Run.lean` and the route's shape and encoder. Part (3) is cut to
ap-1be by the size rule, and it has a Lean blocker (section 5).

Plan and spec on `main` (byte-identical to `a547f2141`): [act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) 4 "AP-1",
2.1, 2.5, 2.8; [act-phrases.md](../../spec/act-phrases.md) 3.1-3.3, 4.4, 14.3; [ap-1bb's REPORT](../ap-1bb/REPORT.md)
("Overlap", rows (3)-(5), section 6) and the DELTAs of ap-1b (row 2) and ap-1bb.

## 0. Statement gate, order and overlap

The spec's statement review converged (14.3, FIX applied in draft 2): this is the gate ap-1a, ap-1b and ap-1bb took.
No approved theorem changed. `lean/statements.txt` is unchanged by this item, so `gate_acts`,
`decodeRegulated_without_acts`, `canonicalActIn_without_acts`, `decodeRegulated_plain` and every other statement keep
their text. No theorem was added.
**Overlap** (hand-written files against `git diff --name-only main...<branch>` for every `lean-first/*`, `feature/*`,
`infra/*` and `foundation/*` branch):
- `lean/VE/Words/Situation.lean`, `lean/VE/Service/ActsExamples.lean` and `tests/test_acts_profile.py` are edited by
  no other branch.
- `tools/trust-classes.json` (the shared side table) is also edited by ap-3, df-1ae, jt-2, q1-4, qt-a3, sc-1b, me-1 and
  arch-20261026-2. `git merge-tree` merges each of them with this branch without a conflict.

Not touched: `lean/VE/Service/Protocol.lean` and `ve/backends/service_schema.py` (the protocol queue);
`lean/VE/Service/Standalone.lean` and `lean/VE/Readings/Wire.lean` (jt-2); `lean/VE/Acts/*` (ap-3);
`lean/VE/NormDefaults/Run.lean` (df-1ae).

## 1. Task rows delivered and not delivered

| Task part | Status | Where |
|---|---|---|
| (1) `lean/VE/Words/Situation.lean`'s regulated decode of `acts@0` (Lean owns it; no Python copy), with fixtures on the accepting and the refusing side of each new check | **done**. `regulatedOf` decodes with `decodeRegulatedIn`, using the environment's profiles (`actsProfiles`: `acts@0` only from a sorted unique list) and its block's fixed phrases (`actsFixed`), as `Env.decode`'s `modalForm` does. No Python changed: `ve/words.py` relays Lean's lines and binds them as before (R8). This fixes ap-1bb review F3 (FOLLOW-UPS "## ap-1bb"). Each check has fixtures on both sides: `acts@0` read or not (absent from the list; an unsorted list); the fixed phrases read or not (block absent, one phrase missing, a refused phrase); the act limits at 80/81 and 400/401 bytes; regulated or not (a base predicate); a pair or not (a plain act, a permission) | `dd4842012`; `ActsExamples.lean` section "ap-1bc" (17 guards); `tests/test_acts_profile.py::test_the_words_route_words_acts_clauses_by_leans_decoder`, `::test_the_words_route_still_refuses_what_is_not_a_regulated_clause`; DELTA row 1 |
| (2) the norm-defaults route's wordings, as a field of an answer that route already gives, typed and bound (R8) | **cut to ap-1be**: the field belongs on `norm-defaults-elaborate`, which `NormDefaults/Run.lean` (`runOtherCase`) writes. It needs `Run.lean`, `ResponseShape/Schemas/NormDefaults.lean` (`elaborateFields`) and `ResponseShape/Encoders/NormDefaults.lean`, and df-1ae (rank 58, in flight) edits all three. The task says to cut (2) in that case. `Wire.regeneratedU` is no alternative: the alternatives and layered routes share it | — |
| (3) `ve/wire_contract/acts@0.json` with its registry entry, examples and catalogue | **cut to ap-1be** (size, and a Lean blocker; section 5) | — |

## 2. Deviations

None from the task. Part (1) changes no Python or Rust code: the relay's type and binding are unchanged.

## 3. Seeded bugs

[seed_bugs.py](seed_bugs.py) plants, runs and restores each bug; [mutants.json](mutants.json) records `file`, `test` and
the first failure. **4 bugs, all killed**, all in Lean (`lean/VE/Words/Situation.lean`, `VE.Words.regulatedOf`); the
check for each is the module build of `VE.Service.ActsExamples`, whose `#guard`s fail.

| Id | Bug | First failure |
|---|---|---|
| `regulatedOf-base-decoder` | the base's `decodeRegulated` (review F3 itself) | `ActsExamples.lean:334` (A1-A3) |
| `regulatedOf-acts-unread` | `actsProfiles false`: `acts@0` never read | `ActsExamples.lean:334` |
| `regulatedOf-any-list` | `acts@0` read from any list (`readsActs` skipped) | `ActsExamples.lean:337` (the unsorted lists) |
| `regulatedOf-block-unread` | the block's fixed phrases not read | `ActsExamples.lean:334` |

The Python test fails on the base too. With the base's own pinned service, the words route refuses every item that
`test_the_words_route_words_acts_clauses_by_leans_decoder` expects a line for: [evidence/delta.json](evidence/delta.json),
base side. No Python or Rust product code changed, so there are no Python or Rust bugs to seed.

## 4. Trust, size, evidence and tests

- **Trust:** `trust_map.py --check` PASS against `110b3bf3a`: K +0, S +0, trusted +0 (G +4: `regulatedOf` is G[R],
  render). The 10 new fixture definitions in `ActsExamples.lean` are listed as `T` in `tools/trust-classes.json`.
  R16 is not used, and so there is no FOLLOW-UPS row and no `trust-mutants.json` (no new trusted definition).
- **Size** (hand-written lines added or changed, `git diff --numstat` against the merge base):
  - product Lean 8;
  - Lean fixtures 60;
  - tests 45;
  - evidence scripts 186 (`seed_bugs.py` 86, mostly ap-1bb's runner unchanged; `delta.py` 100);
  - side table 12;
  - DELTA and this report about 110;

  about 420 in all.
- **Evidence:** [evidence/delta.json](evidence/delta.json): 18 records, 6 identical, 12 `worded`. Both sides were
  recorded by this checkout's client, each against its own pinned `ve_service`; the base was built at `110b3bf3a` in a
  temporary worktree. `--compare` exits 1 head against head and on empty input.
  [evidence/commits.txt](evidence/commits.txt) is `git log main..HEAD --no-merges`, through the commit before the one
  that adds it.
- **Generated** (`regen_generated.py --write`; `--check` passes, 33 entries): `lean/checkers.lock` and
  `lean/declarations.txt`.
- **Tests:**
  - `lake build` (1,082 jobs) and `lean/audit.py` PASS.
  - `tests/test_acts_profile.py`: 93 passed.
  - Selected tests (`mac-pytest.sh --select`) at `d48f5d7b`: 371 units, 0 failed.
  - `gate_collection.py --check --prebuilt`: 5 added, 0 refused, 0 stale, 0 malformed.
  - Pre-existing failures (`main-known-red.txt`): none was selected or touched.
  - The full gate is the chain's.
- **Pilot bytes expected to move:** 0 B (*estimate*). No pilot environment lists `acts@0` yet. The UDHR's 8 act-phrase
  units (1,403 B) need ap-1bd's typing and model path before a pilot can claim them (M7).

## 5. Next items: ap-1be, then ap-1bd

**ap-1be** (what does not fit here):
- **(2) The norm-defaults route's wordings, after df-1ae merges.**
  - Add a `wordings` member to `norm-defaults-elaborate` (`Norms.Wire.plainWordings` of the decoded source), with its
    shape and encoder theorem.
  - Bind it with `ve/norms.py`'s `_bind_wordings` (the same R8 check, slots by `relay.slots_bound`).
  - Let `plain_wordings` ask it for `norm-defaults@0` environments (ap-1bb deviation 2), so they display Lean's
    wording too.
- **(3) `ve/wire_contract/acts@0.json`.** Measured: 500-800 hand-written lines, so (3) may need its own item. It needs:
  - a `UNITS` row in `tools/wire_contract.py`;
  - a registry module (in `conformance/`, as the soft hooks are);
  - two examples under `ve/wire_contract/examples/acts@0/`;
  - `conformance/wire_contract_faults_acts.py`, which writes `conformance/wire-contract/acts@0-catalogue.json`;
  - a Lean hooks module `lean/VE/WireContract/Hooks/Acts.lean` and its row in `WireContract/Diagnose.lean`;
  - tests, and the manifest and trust-class entries.

  The blocker: the inherited environment checks `Hooks/Norms.lean` `w1Environment` and `typingEnvironment` call
  `decodeNormsEnvironment` without `acts := true`, so Lean's `diagnose` would refuse every `acts@0` source under a
  contract that includes `norms@0`'s environment phase. The contract therefore needs its own `acts@0`-aware environment
  hook. The spec names no checks or codes for the contract. The limits it describes (400-byte act, 300-byte phrase,
  128 phrases) must stay Lean's (`VE.Acts.Lexical`), with the contract reading them, never a copy (one owner).

**ap-1bd** (after jt-2 merges): typing and the model path read `acts@0` (`Standalone.typingReduced`,
`modelEnvironment`), the readings route's decoder (`Readings/Wire.lean`) and the model oracle's re-recorded
answers. Then the pilots can use `acts@0`; then AP-3 (ap-4 after ap-3).

## 6. Self-review against BUILDER-CHECKLIST

One line per item of `manage-agents/BUILDER-CHECKLIST.md`.

1. PASS: no answer field added. The words row's type and binding are unchanged and tested by `tests/test_words.py::test_an_answer_not_bound_to_its_request_is_refused` (10 mutants) and `::test_a_genuine_answer_is_bound`; the new lines are Lean's content.
2. PASS: section 1 copies each task part with its commit and test; (2) is cut by the task's own df-1ae rule and (3) by the size rule, both to ap-1be. `git diff main...HEAD` has no Python product change, no Python copy of a Lean decision and no report test; the only overlap is the shared `tools/trust-classes.json`, which merges cleanly.
3. PASS: [mutants.json](mutants.json) (4 killed). The Python test fails against the base service ([evidence/delta.json](evidence/delta.json)). `delta.py --compare` exits 1 head against head and on empty input. R16 mutants: none needed (trust +0).
4. PASS: [evidence/delta.json](evidence/delta.json), base and head side by side: the control and the refusing items are identical. Without `acts@0`, `regulatedOf` is the base's (`decodeRegulated_without_acts`). Rust is unchanged and refuses `acts@0` (`test_rust_refuses_an_acts_environment`).
5. PASS: Python reads no new field. Input-side refusals: `test_lean_refuses_an_item_it_cannot_word` (undeclared predicate and constant, wrong arity: unchanged and passing) and `test_the_words_route_still_refuses_what_is_not_a_regulated_clause` (a base predicate; a pair on a plain act or a permission).
6. PASS: `main` is the merge base `110b3bf3a` (no sync needed); `git merge-tree --write-tree HEAD main` is clean; [evidence/commits.txt](evidence/commits.txt) is from `main..HEAD --no-merges`; the gate is the chain's, on the final HEAD.
7. PASS: DELTA row 1 cites the DRI decision files ap-1b's DELTA row 2 cites; trust +0 needs no row; no signature is reserved.
8. PASS: every changed record of `evidence/delta.json` (12, `worded`) is DELTA row 1.
9. PASS: `select_tests` picks 366 of 462 units, including `lake build` (which every seeded bug fails), `tests/test_acts_profile.py` and `tests/test_words.py`.
10. N.A.: no theorem added or changed (`lean/statements.txt` unchanged).
11. N.A.: no budget, limit or deadline code changed (`maxItems` and the act limits are untouched).
12. N.A.: no pilot environment lists `acts@0`. For every other environment, `regulatedOf` adds one profile read per item and decodes no block (`actsFixed []` returns at once); under `acts@0` it adds one `decodeFixed` per item, beside the one `Lexical.check` already runs.
13. PASS: no test removed or renamed; `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
