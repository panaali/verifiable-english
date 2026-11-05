# pc-2a-shadowmiss: correct two records that overclaim pc-2a's deletion

Feature item pc-2a-shadowmiss (family profile composition). It follows up merged pc-2a and changes wording only.
Backlog row: DRI decider, reviews/dri-decisions-20261104-pc-revise-apply.md. DRI lp0801 Q4 says it merges before the
next public push of main. reviews/dri-decisions-20261104-pc-l1only-apply.md says it continues while the other PC
rows are held. Finding: the pc-2a review shadow's F1 (`pc-2a-review-shadow.final.md`, grade A, overclaim).

## What changed

pc-2a removed only one thing: the retained Python branch's **acceptance** of the soft chain under
`norm-defaults@0` (`ve/document/load.py:416-420`). `check_soft_source` with the norm-defaults layer
(`ve/document/load.py:193-198`) and the loader checks before `:416` still run whenever Lean answers
`CheckerUnavailable`. They refuse with Python's own diagnostics. Two records said the branch was gone:

| # | File | Was | Now |
|---|---|---|---|
| 1 | `docs/spec/rd-9-relay-binding.md:15-16` | "the retained Python branch is gone, so this row is the answer" | "the retained Python branch no longer accepts this chain, so this row is the answer; its soft-source check and loader diagnostics stay until PC-2b" |
| 2 | `tests/test_relay_binding_inventory.py:52-53` (comment only) | "..., whose Python branch is deleted." | "... The retained Python branch no longer accepts this chain; its soft-source check and loader diagnostics stay until PC-2b." |

Size: `git diff --stat main...HEAD` before this REPORT gives 2 files, 4 insertions and 2 deletions, under the
20-line budget. The test logic did not change. Output bytes moved: 0 (estimate; no output, verdict or trusted
line changes).

The task listed places as accurate, and they were not touched. `git diff --name-only main...HEAD` names only the
two files above and this REPORT. The places:
- pc-2a's DELTA row 6
- pc-2a's REPORT section "The deletion"
- `ve/document/load.py:417-418`
- `ve/document/lean.py:121-122`
- `lean/VE/Service/DocumentChain.lean:10`

## The shadow's probe

The command is run from the worktree root:

    uv run python -c 'import pathlib as p; r=lambda f: " ".join(p.Path(f).read_text().split()); bad={f: s for f, s in {"docs/spec/rd-9-relay-binding.md": "the retained Python branch is gone", "tests/test_relay_binding_inventory.py": "whose Python branch is deleted"}.items() if s in r(f)}; assert not bad, bad'

On main (9721a29dd, before the fix) it fails on both files:

    AssertionError: {'docs/spec/rd-9-relay-binding.md': 'the retained Python branch is gone', 'tests/test_relay_binding_inventory.py': 'whose Python branch is deleted'}

After the fix (58a9207e6) it prints nothing and exits 0 (`fixed rc=0`).

## Seeded bugs

Python and Lean product code did not change (no file under `ve/`, `tools/`, `conformance/`, `lean/` or `rust/`).
Each record was checked by restoring its old phrase:

| # | File | Seeded bug | Failing check | Output |
|---|---|---|---|---|
| 1 | `docs/spec/rd-9-relay-binding.md` | restored "the retained Python branch is gone, so this row" | the shadow's probe (above) | `AssertionError: {'docs/spec/rd-9-relay-binding.md': 'the retained Python branch is gone'}`, rc 1 |
| 2 | `tests/test_relay_binding_inventory.py` | restored ", whose Python branch is deleted." in the comment | the shadow's probe (above) | `AssertionError: {'tests/test_relay_binding_inventory.py': 'whose Python branch is deleted'}` |

After each file was restored, the probe exited 0 (`restored rc=0`).

## Tests run

- `uv run pytest -q tests/test_relay_binding_inventory.py tests/test_architecture_docs.py` gave `71 passed in 128.79s`.
  - No test names `docs/spec/rd-9-relay-binding.md` directly. A grep for `rd-9-relay-binding` and `relay-binding`
    over `tests/` and `tools/` found none.
  - `tests/test_architecture_docs.py` holds the stale-document sweep over docs.
- `zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` exited 0. It ran 2 shards on GitHub
  Actions (run `pc-2a-shadowmiss-58a9207e-t843799`):
  - `SHARD 1/2: exit 0 in 360.8 s; 11 units, 11 passed`
  - `SHARD 2/2: exit 0 in 604.4 s; 12 units, 12 passed`
- I did not run the full gate. The chain runs it on the final HEAD.

## Trust and DELTA

- `uv run python tools/trust_map.py --check` reported `K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0`
  and `PASS`. There is no trust record.
- There is no DELTA.md. No output, verdict or trusted line changed, so there is no user-visible delta for a ruling
  to cover.

## Not this item

The shadow's C findings F2-F8 are **not fixed** here. They belong to pc-2b's task file, which is held for the
post-sprint PC redesign:
- F2: speed above ~200 rules against R4's 2 s
- F3: the BOUND status of `units[].status`
- F5: profile order
- F6: spec F4.3's stale refusal
- F7: the `lean is None` exemption
- F8: `Document.lean` scope

F4 (size) was already disclosed in pc-2a's REPORT.

Next item: none in this chain (pc-2b is held).

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A. No relayed answer or schema changed.
2. Deliverables built, no rule broken: PASS. Both records were corrected and the probe passes (section "The shadow's probe"). `git diff --name-only main...HEAD` lists only the task's files.
3. Tests can fail: PASS. Seeded bugs 1 and 2 each make the shadow's probe fail (section "Seeded bugs").
4. Python, Lean and Rust agree: N.A. No code changed. The selected tests passed (23 units).
5. R8 binding: N.A. No binding changed. `tests/test_relay_binding_inventory.py` passes with its logic unchanged.
6. Gate evidence matches HEAD: PASS for the selected run on 58a9207e6. This REPORT commit adds docs only. The full gate is run by the chain on the final HEAD.
7. No unsigned item: PASS. No DELTA row and no trust record; `trust_map.py --check` reports PASS with +0.
8. User-visible changes in DELTA: N.A. Wording only; no output or verdict changed.
9. Test selection finds the tests: PASS. The selection ran `tests/test_relay_binding_inventory.py` as changed (shard 1 log: `changed ['tests/test_relay_binding_inventory.py']`).
10. Lean statements: N.A. No Lean changed.
11. Budgets fail closed: N.A. No limit changed.
12. No CPU or memory regression: N.A. A comment and a doc line only.
13. Test-removed trailers: N.A. No test removed or renamed. The comment edit leaves the collected IDs the same.
14. Both directions, cited evidence, spec re-read: PASS.
    - Both directions: the probe fails on main and on each seeded file, and passes on the fix.
    - Every claim above cites its command output.
    - Spec re-read: the new wording against the shadow's fix line ("say the branch no longer accepts this chain, and its soft-source check and loader diagnostics stay until PC-2b"), `ve/document/load.py:193-198` (`check_soft_source` with the `norm-defaults@0` layer) and `:416-420` (acceptance replaced by `CheckerUnavailable`).
15. The four FIX classes:
    - Overclaim: PASS. The new wording says what remains ("stay until PC-2b"). The "Not this item" section names F2-F8 as not fixed.
    - No silent cut: PASS. Deliverables 1-3 are all built.
    - Every new check can fail: PASS. The probe has seeded bugs 1 and 2.
    - Limits charged before work: N.A. No evaluator or limit.
