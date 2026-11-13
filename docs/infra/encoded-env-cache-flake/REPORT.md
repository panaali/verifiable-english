# encoded-env-cache-flake: REPORT

- Status: done, ready for the chain gate. Branch `infra/encoded-env-cache-flake`; the final HEAD is the commit that adds this report.
- Change: `ve/environment_wire.py` `encoded_value` now evicts only the least recently used entry when the cache is full (LRU, `OrderedDict`). It used to clear all 256 entries.
- Tests: 4 new tests in `tests/test_lean_handles.py`. All 4 fail on the old code and pass on the new code. The condition test's assertions are unchanged.
- Open items: none. DELTA: none (layer 1 wire cache, no verdict or text changes). No DRI signature is reserved. Trust +0.
- SIZE: 13 product, 60 tests, 0 other hand-written lines (this report excluded); `git diff --numstat main...HEAD`.

## Cause

`encoded_value` called `_cache.clear()` once `len(_cache) >= _LIMIT` (256). The test
`test_adapter_environment_is_encoded_once_and_immutable` does these steps in order:

1. Cache the lean projection.
2. Cache the rust projection.
3. Ask for the lean projection again and expect the same object (`is lean`).

If the rust insert in step 2 hit the limit, the cache was cleared and step 3 built a new object. Whether that happened depended on how many entries earlier tests in the same worker had left. The failure text is in main 3d5e0abe's aarch64 leg s1 (`gha-arm/armsh-watch-3d5e0abe-3d5e0abe-t517486/s1/gate.log.tail`, `tests/test_lean_handles.py:185: AssertionError` on `assert cached_route_environment(env) is lean`).

## Fix, and why LRU rather than insertion order

The cache is now an `OrderedDict`:

- A hit calls `move_to_end` under the lock. This is O(1).
- An insert into a full cache calls `popitem(last=False)`. This removes the one least recently used entry.
- The lock discipline is the same as before: read under the lock, build outside it, insert with `setdefault` under it. The first builder's object wins.
- A key that another builder cached during the build evicts nothing (`key not in _cache` guard).
- The bound stays at `_LIMIT` entries.

I chose LRU over insertion order (`del _cache[next(iter(_cache))]`) because insertion order does not fix this flake. Suppose an earlier test cached the lean projection of the same environment first, and 255 other entries came after it. In the test, step 1 is then a hit on the oldest entry. The rust insert in step 2 evicts that oldest entry, which is lean, and step 3 fails as before. Seeded bug M2 below shows this: without `move_to_end` on a hit, the `lean-oldest` case fails.

## Tests (task item 3)

All 4 tests use the fixture `wire_cache`. It saves the cache's entries in order, empties the cache, and restores the saved entries after the test. The new tests therefore leave later tests the cache state they would otherwise have had. The condition test has no fixture and is unchanged.

| test | task item | on old code (`main` 6949e5de `environment_wire.py`) | on the fix |
|---|---|---|---|
| `test_a_full_environment_cache_keeps_the_entries_in_use[full-cache]` | (a): fill to `_LIMIT - 1`, then lean, rust, lean `is` | FAILED (`is lean`) | passed |
| `test_a_full_environment_cache_keeps_the_entries_in_use[lean-oldest]` | (a) variant: lean cached first, so it is the oldest entry | FAILED (`is lean`) | passed |
| `test_the_environment_cache_keeps_its_newest_limit_entries` | (b): `_LIMIT + 10` inserts leave `len == _LIMIT` and exactly the newest `_LIMIT` keys | FAILED (`assert 10 == 256`) | passed |
| `test_a_key_another_builder_cached_first_evicts_nothing` | opposite direction: a second builder of a cached key gets the first object and evicts nothing | FAILED (`{'builder': 'second'} is {'builder': 'first'}`: the old code clears the cache, then inserts the second object) | passed |

Runs:

- Old code, before the fix (first three tests plus the condition test):
  `uv run pytest -q -p no:randomly tests/test_lean_handles.py -k "environment_cache or encoded_once"` gave
  `3 failed, 1 passed`. The failures are the three tests above; the condition test passed alone.
  The 4th test, run on main's `ve/environment_wire.py` (`git checkout main -- ve/environment_wire.py`, `-k evicts_nothing`), gave `1 failed`.
- Fix: the same command with `-k "environment_cache or encoded_once or evicts_nothing"` gave `5 passed, 41 deselected`.
- Task item 4, every test file that imports `environment_wire`, `lean_runner` or `rust_jsonl` (22 files, `grep -lE "^\s*(from|import) .*(environment_wire|lean_runner|rust_jsonl)" tests/*.py`, `tests/test_lean_handles.py` included):
  `zsh mac-pytest.sh -- -q <22 files>` gave `1461 passed in 106.26s`, exit 0. It ran on the VM (runner's choice: "MAC_LAST").
- Final selected run on the committed HEAD: see "Selected run" below.

## Seeded bugs (Python; the only product language changed)

Each bug was planted in `ve/environment_wire.py`, run with the tests above, and restored with `git checkout`. The tree was clean after each.

| # | mutant | failing test(s) |
|---|---|---|
| M1 | `_cache.popitem(last=False)` changed to `_cache.clear()` (the old behaviour) | both `test_a_full_environment_cache_keeps_the_entries_in_use` cases, `test_the_environment_cache_keeps_its_newest_limit_entries` |
| M2 | `move_to_end` on a hit removed (insertion-order eviction) | `test_a_full_environment_cache_keeps_the_entries_in_use[lean-oldest]` |
| M3 | `popitem(last=True)` (evicts the newest entry) | all three of M1's tests |
| M4 | `len(_cache) > _LIMIT` (bound off by one) | all three of M1's tests |
| M5 | `key not in _cache` guard removed | `test_a_key_another_builder_cached_first_evicts_nothing` |
| M6 | `_cache[key] = fresh` instead of `setdefault` (the second builder wins) | `test_a_key_another_builder_cached_first_evicts_nothing` |

## Selected run

`MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` was run on the committed HEAD. The result is given in the build report that hands this item back; this file was committed before that run (docs-only commits after it keep the chain's reuse).

## Pre-existing failures

None met. `main-known-red.txt` lists nothing in these files.

## Notes for the DRI

- `ve/backends/lean_runner.py` `_MODELS` and `_FORMULAS` (`_MODELS_LIMIT = 256`) and `ve/backends/validation.py` `_ACCEPTED` use the same clear-all pattern (`if len(...) >= LIMIT:` at `lean_runner.py:97,116` and `validation.py:60`). I did not check whether any test asserts object identity across them. They are outside this task's scope, so I am not filing a follow-up. If one of them shows the same flake, the same LRU change applies.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No relayed answer, schema or route changed.
2. Deliverables built, no rule broken: PASS.
   - (1) LRU fix: commit 22dc67a136.
   - (2) Condition test assertions unchanged, no skip, xfail or fixture: `git diff main...HEAD -- tests/test_lean_handles.py` adds lines only.
   - (3a), (3b) and their teardown: the tests above.
   - (4): the 22-file run.
3. Tests can fail: PASS. Mutants M1 to M6 are in the table above, each with its failing test.
4. Python, Lean and Rust agree: PASS. The cache only memoises transport text. The 22-file run covers the relay, Rust JSONL and differential files (`test_question_differential.py`, `test_route_transport.py`, `test_rust_jsonl_schema.py`): 1461 passed.
5. R8 binding: N.A. No binding changed.
6. Gate evidence matches the final HEAD: PASS. The chain runs the gate on the final HEAD, and the final selected run is on committed code.
7. No unsigned item: PASS. DELTA none, trust +0, no reserved signature.
8. User-visible change in DELTA: N.A. Cache eviction is not visible to users: entries are keyed by an identity that fixes the bytes, so a miss rebuilds the same text (`test_adapter_environment_is_encoded_once_and_immutable` asserts the text equals the fresh projection).
9. Test selection: PASS. The final selected run includes `tests/test_lean_handles.py` (the touched file).
10. Lean statements: N.A. No Lean changed.
11. Budgets and limits fail closed: PASS. The bound holds at exactly `_LIMIT` (`test_the_environment_cache_keeps_its_newest_limit_entries`). The tests use no sleeps or timeouts.
12. No CPU or memory regression: PASS.
    - A hit is one `OrderedDict.get` plus one O(1) `move_to_end`.
    - Memory is still at most `_LIMIT` entries (`test_the_environment_cache_keeps_its_newest_limit_entries`).
    - Fewer clear-all events mean fewer rebuilds.
13. Test-removed trailers: N.A. No test was removed or renamed.
14. Both directions and cited evidence: PASS.
    - Evict side: `..._keeps_its_newest_limit_entries`.
    - Keep side: `..._keeps_the_entries_in_use[lean-oldest]` and `..._evicts_nothing`.
    - Every claim above cites its command.
15. Overclaim, silent cut, checks can fail, limits charged first: PASS.
    - Universal words are each backed by a named test.
    - No deliverable was cut.
    - Mutants M1 to M6.
    - The limit is checked before the insert (M4).
