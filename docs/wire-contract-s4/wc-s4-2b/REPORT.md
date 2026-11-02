# wc-s4-2b: the Rust contract engine and the engine corpus in Rust (wire-contract S4 item 2, second part)

No DRI signature is reserved in this item. DELTA: none (the `error` object, the only user-visible part, was
cut to wc-s4-2bb at the size line; see Size). Trust: +0.

Inputs read: docs/spec/wire-contract-s4-2.md (accepted, `reviews/dri-decisions-20261031-wc-s4-2.md`), sections
1, 6, 7, 8, 9; docs/spec/wire-contract-S4-PLAN.md section 3 rows b and d, section 4 item 2; wire-contract.md
2.6, 2.7, 2.8, 8.1; docs/wire-contract-s4/wc-s4-2/REPORT.md. The synthesis round 2 edits
(debates/plan-synthesis-2/edits-wire-contract.md) concern the S6 to S10 shadow items and DEC 12 (no shared table
engine); this item implements none of them and contradicts none (the engine runs wire-contract's own generated
tables, no shared table engine).

## Plan rows delivered

| Task or plan line | Delivered by | Test or evidence |
|---|---|---|
| (1) the engine run over the generated tables: the order rule of 2.6 | `rust/ve-kernel/src/contract.rs` `run`, `Run::entries`, `Run::entry` (phases in order, entries in order, groups item-major, scopes read at their site) | F5 below; seeded bug B1 |
| (1) the record of 2.7 with the closed renderer set | `Run::finding`, `render`, `render_json` (`raw`, `json`, `index`, `count`, `list`; absent renders as `""`; `json` cut at 80 bytes with `...`) | F5 (E23 is the cut, E25 a `count`, E28's `list` is deferred); seeded bug B2 |
| (1) the outcomes of 2.8: `fault(record)`, `clean`, `deferred(id)`, deferring on every hook, classifier and view Rust lacks | `Outcome`; `Run::eval` defers on `Hook` and `Classifier`, `Run::entry` on a `Scope` with a view whose `at` resolves (2.8: the scope "contributes one instance in its place") | `every_deferred_outcome_names_what_rust_lacks`; `a_unit_without_hooks_is_clean_or_gives_lean_s_record` (`clean` on `inner@0`) |
| (1) evaluator rule of 2026-10-27: each value read once, its size charged against a stated limit | `MAX_ENGINE_UNITS` = 1,000,000; `Run::charge`; the domain pass charges each node of the root once; each instance, guard literal, pattern step, compared node and type-form element is charged | F6 below; seeded bugs B4, B5 |
| F6: a large well-formed input ends within its stated limit; one step over is refused with the limit's own code | `a_large_input_ends_within_the_limit_and_one_step_over_is_refused`: a `demo@0` document with 90,897 table entries spends exactly 129 + 11 × 90,897 = 999,996 units and defers at `3.4`; 90,898 entries is `ResourceLimit` "wire contract engine exceeds 1000000 units"; budget 0 is `ResourceLimit` | `cargo test -p ve-kernel --test contract_engine`: 4 passed |
| (2) F5: the engine corpus run in Rust, every fault and `clean` byte-identical to engine-golden.json | `rust/ve-kernel/tests/contract_engine.rs` `engine_corpus_equals_the_golden` (a cargo test, the Rust runner beside the Python and Lean ones); canonical JSON of each record compared | on engine.json: "engine corpus in Rust: 24 equal to the golden, 3 to their hand-derived expected, 10 deferred: E1@3.4 E2@3.4 E13@3.4 E27@3.4 E28@3.4 E29a@3.4 E29b@3.4 E30@3.4 E31@3.4 E32@3.4" (`cargo test … -- --nocapture`) |
| (2) … and to Python's and Lean's | `tests/test_wire_contract_rust.py::test_rust_engine_records_equal_lean_python_and_the_golden`: all 43 golden cases (the `DEMO` and `DEFER` cases of tests/test_wire_contract_lean.py, whose records the golden is generated from) sent to the cargo runner; each non-deferred record equals Lean's, the golden's and Python's (`conformance/wire_contract_engine.py` with the corpus registry) as canonical JSON | "engine corpus in Rust: 31 equal to the golden, 0 to their hand-derived expected, 12 deferred: E1@3.4 E13@3.4 E27@3.4 E28@3.4 E29a@3.4 E29b@3.4 E30@3.4 E31@3.4 E32@3.4 E34@d2 E35@d2 E36@d2" (`pytest -s tests/test_wire_contract_rust.py`) |
| (2) plan row d: every deferred outcome counted under Rust's deferred share and never compared; the count printed | `share` in the pytest; the cargo runner counts and prints; both pin the share (cargo: (24, 3, 10) on engine.json; pytest: (31, 12)) | `test_the_deferred_share_is_counted_and_never_compared`; seeded bug B3 |
| (3) the `error` object's `diagnostic` member and its jsonl schema entry | NOT DELIVERED: cut to **wc-s4-2bb** at the size line (see Size) | — |
| (4) seeded bugs | `seeded-bugs.json` beside this report: B1 to B5 | see below |
| Rust hash moved: pin `lean/checkers.lock` first | `regen_generated.py --write --only checker-pins` (86fb0ad10); `--check` then reported no stale entry ("checked 35 entries") | `tools/rust_build.py --check` printed "d55731df…: NOT pinned" before the pin |

**Not delivered here (wc-s4-2bb):** task deliverable (3), spec section 6 and fixture F7: `Error.diagnostic` in
`rust/ve-kernel/src/lib.rs` (`skip_serializing_if = "Option::is_none"`), the Rust overlay of 2.8 that sets it
(fault, residual or deferred record from the engine's `Outcome`), the optional member under
`$defs/error/properties/error` of `ve/backends/rust_schema/jsonl.json` typed as the three records, its tests (the
member equals the Lean record on every corpus case where Rust does not defer; absent where unset; fuzz that
retypes, removes and adds each field), its DELTA row (R3), and the seeded bug "`diagnostic` serialised as
`null`". It was built and passing in c14566b6e (about 95 lines) and removed in 2469444a8; wc-s4-2bb can restore
it from there. The engine's `Outcome` is already what that overlay reads. The spec's sentence "That commit
belongs to wc-s4-2b" (spec 6) therefore holds for wc-s4-2bb, the rest of item 2's second part; the spec is not
edited.

## Deviations, recorded here and not in the spec

1. **The root.** Generated tables carry no `input` list (spec 3; `Table.lean` has none), so `run` takes the root
   that the unit's adapter built (base spec 2.1: "The unit's input adapter (2.5) builds the root"). The corpus
   runner builds it from the contract's `input`, as Lean's `caseRoot` and Python's `run` do.
2. **Names in the corpus.** engine.json names four cases differently from engine-golden.json (`E2` and `E17b`
   have no golden; `E6` and `E19` are the golden's `E6a` and `E19a`). The cargo runner compares those four with
   engine.json's own hand-derived `expected` (check, path, text) and every other case with the golden byte for
   byte; the pytest covers every golden case by its own name.
3. **No `inner_path`.** Rust lacks every view, so it never enters one (it defers at the scope); a Rust record never
   has `inner_path`, and the frame keeps no view site.
4. **Rendering is charged through the domain pass.** The record is built once per run, from values the domain
   pass has already charged, so `render` itself charges nothing.

## Size

`git diff --numstat $(git merge-base HEAD main)` before this report: `contract.rs` +476 −2, `contract_engine.rs`
+161, `tests/test_wire_contract_rust.py` +81 −9 (plus the one generated line of `lean/checkers.lock`): 727 lines,
over the ~600 line. Deliverables (1) and (2), with F6 and the seeded bugs, are one coherent part and already
exceed it (the engine alone is 476 lines, after a compaction from 618: no overlay, no view frame, `serde_json`'s
compact form for the `json` renderer). The cut the task's order leaves is (3), the `error` object, which moved to
wc-s4-2bb (see above). No further coherent cut is left inside (1) and (2): F5 needs the whole engine, and F6 and
the rule of 2026-10-27 may not be moved.

## Seeded bugs (each shown failing, then restored with `git checkout`)

| # | Language, file | Bug | Failing check |
|---|---|---|---|
| B1 | Rust, `rust/ve-kernel/src/contract.rs` `Run::entries` | the first two entries of each list swapped (group 2.2 runs before 2.1 in the items phase) | `engine_corpus_equals_the_golden`: left 2.2a "Shape: tags of a are not sorted", right the golden's 2.1c "Duplicate: a" |
| B2 | Rust, same file, `render` | a string under `json` rendered as `raw` | `engine_corpus_equals_the_golden`: left "Shape: mode shut", right "Shape: mode \"shut\"" (E3) |
| B3 | Python test runner, `tests/test_wire_contract_rust.py` `share` | a deferred row compared as a fault (the `continue` dropped) | `test_the_deferred_share_is_counted_and_never_compared`: "AssertionError: E1, assert b'{"wrong":true}' == 'clean'" |
| B4 | Rust, same file, `Run::charge` | the limit never refuses | `a_large_input_ends_within_the_limit_and_one_step_over_is_refused`: "called `Result::unwrap_err()` on an `Ok` value: Deferred("3.4")" |
| B5 | Rust, same file, `Run::domain` | the domain pass charges nothing | the same test: "left: (112, 10), right: (129, 11)" |

Rust is the only language whose product code changed. The fourth seeded bug of the task ("`diagnostic` serialised
as `null`") belongs to the cut deliverable (3).

## Trust

`uv run python tools/trust_map.py --check` on ca4a4efd8: "against 6793180ca39e: K +0, S +0, D +0, G +0, tied +0,
unclassified +0, trusted +0 … PASS". Rust and tests are untrusted and no Lean file changed, so there is no new
trusted definition and no mutants.json. `git diff main -- conformance/wire-contract/contracts/` is empty (0 lines).

## Tests

- While iterating: `cargo test -p ve-kernel --test contract_engine` (4 passed) and
  `uv run pytest -q tests/test_wire_contract_rust.py` (3 passed); `cargo clippy -p ve-kernel --tests` reports
  nothing in the files changed here.
- `tools/select_tests.py --base $(git merge-base HEAD main)` selects 438 of 523 units, `tests/test_wire_contract_rust.py`
  among them (a kernel change and the release pin reach every Rust user, as in wc-s4-2).
- Selected set, once, on the committed tree (recorded as tree `6aed8d83a3`):
  `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` gave six shards, "exit 0" each: 88, 66, 67,
  86, 67 and 67 units, all passed (441 units; log `/tmp/wc-s4-2b-select.log`, "summary: … exit=0; 2099s").
  No test of `main-known-red.txt` failed; none needed a rerun.

## Pilot bytes

None expected: no output, verdict, message or schema changes; the engine is reached by tests only (estimate;
nothing is claimed before a pilot audit).

## Spec re-read

- "The Rust engine returns `fault(record)`, `clean` or `deferred(id)` … defers on every hook, classifier and view it
  lacks", against docs/spec/wire-contract-s4-2.md:115-117: `Outcome`, `Run::eval`, `Run::entry`.
- "A deferred outcome is counted under Rust's deferred share and never compared … a fault or `clean` is compared
  with Lean's and Python's records byte for byte", against wire-contract-s4-2.md:117-119 and
  wire-contract-S4-PLAN.md:101: `share`, `engine_corpus_equals_the_golden`.
- The one order rule, against wire-contract.md:266-289: phases, entries, item-major groups, scopes.
- "for a view, `id` is the include's id … it contributes one instance in its place, at the scope's position",
  against wire-contract.md:343-347: the deferred id of a view scope is the include ids and its own id.
- The renderers, against wire-contract.md:324-331 (and Lean's escape table, which escapes only `"`, `\` and
  characters below U+0020, the first two letter forms rewritten by `lowerEscapes`).
- "every check, its position, code, class, text and limit comes from the generated table", against
  wire-contract-s4-2.md:126-127: the engine reads only `Table`.

## Next item

wc-s4-2bb (the `error` object, above), then wc-s4-3 (`json@0`: its statement spec first; base plan question 7,
the scanner order, stays open), then wc-s4-4 to wc-s4-6.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer is relayed or changed; the Rust engine's records are compared, never relayed.
2. PASS: the plan rows table above, with commit and test per row; (3) is cut at the size line under the common
   rule "deliver the first coherent part … name the rest as the next item" (wc-s4-2bb). No Python copy of a Lean
   decision (the engine is Rust, untrusted, compared only); no permanent report test; in-flight branches touch none
   of these files (checked with `git diff --name-only main...<branch>` for every lean-first, feature, infra and
   foundation branch).
3. PASS: seeded bugs B1 to B5; the comparator fails on a changed record (B2; `test_the_deferred_share_…` changes
   `text`), on no rows and on a missing row (`share([])`, `share(rows[:-1])` raise).
4. PASS: Rust equals Lean, the golden and Python on every non-deferred golden case
   (`test_rust_engine_records_equal_lean_python_and_the_golden`); member order cannot matter (objects are read in
   code point order of the keys); valid inputs: `inner@0` clean (`a_unit_without_hooks_…`).
5. N.A.: Python reads no field from a Lean answer here.
6. PASS: the selected tests ran once on the committed final code; the gate is run by the chain on the final HEAD.
7. PASS: no DELTA row and trust +0; no signature reserved.
8. PASS: DELTA none: no output changes (the engine is reached only by tests; `Error` and `jsonl.json` are unchanged
   on this branch, `git diff main...HEAD --stat` lists neither).
9. PASS: the selection contains `tests/test_wire_contract_rust.py`, which B3 fails; the cargo tests run in the
   gate's `cargo_test` stage.
10. N.A.: no Lean statement.
11. PASS: budget 0 is `ResourceLimit`; one entry over the limit is `ResourceLimit`; exhaustion is never an outcome
    (`a_large_input_ends_within_the_limit_and_one_step_over_is_refused`). No timing in any test.
12. PASS: a step-count test (no timing): F6 pins 129 + 11 units per table entry, so an eager or repeated read
    changes the count and fails it.
13. PASS: no test removed or renamed.
14. PASS: both directions (the large input within the limit and one over; a deferred row ignored and a wrong
    fault record refused; `clean` and a fault on `inner@0`); every claim above names its command; spec re-read above.
