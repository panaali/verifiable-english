# pk-1-conditions-b-cfr-1: the readers of `Pack.conditions` (REPORT)

Summary: the docstring of `Pack.conditions` (lean/VE/NormDefaults/Packs.lean) no longer says "no reader yet"; it names
its two readers, `packConditions` and `providerConditions`, and `tests/test_pack_conditions_doc.py` holds it there.
Comment and test only: no definition, statement or proof changed. No DELTA row, no DRI signature reserved. Pilot
bytes 0. Next item: none.

Source: DRI 2026-11-09, reviews/dri-decisions-20261109-l1-c-regrade-norm-defaults.md item 1; regrade #10 in
reviews/l1-c-regrade-norm-defaults-20261109.md; finding pkcb-F3 of pk-1-conditions-b-review.final.md. The plan is the
code on main (merge base 9f5dd46ab); no plan section or statement gate applies.

## Deliverables

| # | Row (task) | Delivered by |
|---|---|---|
| 1 | The docstring states its readers: `packConditions` (decision premises) and `providerConditions` (the defaults route refuses a document with any stated condition until EXP-D3 settles), keeping the profile-composition 1.9 reference | lean/VE/NormDefaults/Packs.lean:36-38 |
| 2 | `test_pack_conditions_reader_documentation` (tests/test_pack_conditions_doc.py): fails while the docstring says "no reader"; passes only when it names both readers and each is a `def` in lean/VE/Defaults/Uniform.lean | tests/test_pack_conditions_doc.py; fails on main (below) |
| 3 | Grep lean/ for any other "no reader" / "not read yet" comment on a pack field | None: see below |

### The test fails on main

On the merge base's Packs.lean (`git show main:lean/VE/NormDefaults/Packs.lean`), before the docstring edit:

```
$ uv run pytest -q --noconftest tests/test_pack_conditions_doc.py
E   AssertionError: Each stated sufficient condition and its decision (profile-composition 1.9; no reader yet).
FAILED tests/test_pack_conditions_doc.py::test_pack_conditions_reader_documentation
1 failed
```

With the new docstring: `1 passed`. (`--noconftest` skips only conftest's backend build; the test reads two source
files and needs no backend.)

### Other "no reader" comments on pack fields

`grep -rniE "no reader|not (yet )?read|nothing reads|read by no|no consumer|unused yet" lean/VE` finds only
Packs.lean:36 on a pack field. The other matches concern other things (decoders that do not read a block, front
matter that does not parse, observations past a limit). None was changed.

## Seeded bugs

Each was planted in the worktree, run against `uv run pytest -q --noconftest tests/test_pack_conditions_doc.py`
(the test `test_pack_conditions_reader_documentation`), seen to fail, and restored. The test passed again afterwards.

| # | Language | File | Bug | Result |
|---|---|---|---|---|
| S1 | Lean | lean/VE/NormDefaults/Packs.lean | the old docstring restored (`git show main:...`) | fails: "no reader" matched |
| S2 | Python | tests/test_pack_conditions_doc.py | `providerConditions` in `READERS` renamed to `providerConditionsX` | fails: the docstring does not name providerConditionsX |
| S3 | Lean | lean/VE/NormDefaults/Packs.lean | "(profile-composition 1.9)" dropped from the docstring | fails: the 1.9 reference is missing |
| S4 | Lean | lean/VE/NormDefaults/Packs.lean | `` `providerConditions` `` replaced by "the provider guard" in the docstring | fails: the docstring does not name providerConditions |
| S5 | Lean | lean/VE/Defaults/Uniform.lean (planted only, never committed) | `def providerConditions` renamed to `providerConditionsOld` | fails: providerConditions is not defined in Uniform.lean |

S1 and S2 are the seeded bugs the task names. The only product code changed is a Lean docstring; no Python or Rust
product code changed.

## Trust

Docstrings are not trusted lines: `uv run python tools/trust_map.py --check` on the final HEAD is expected to show
+0 K+S+V; the measured numbers are below.

## Scope

Files: lean/VE/NormDefaults/Packs.lean (docstring only), tests/test_pack_conditions_doc.py, this directory. No
in-flight branch touches either file. The other C findings of the regrade stay their own follow-ups.
