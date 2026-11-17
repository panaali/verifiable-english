# tm-esc-sc7-wordchar: guards that read `wordChar`'s filler list

Status: done, test-only. HEAD bc3699d5d3 (the guards; this report and its evidence come in the next commit), base b00f97f5c2.
What changed: 8 `#guard` lines and a 3-line comment in lean/VE/Scope/AuthoringExamples.lean (sc-7 review F9 section), plus
lean/declarations.txt regenerated. Result: the 5 filler-list mutants of `VE.Scope.Pinned.wordChar` go from 5 SURVIVOR at the
base to 5 KILLED at HEAD. Open items: none. DRI signature: none needed (no DELTA, no trust growth).
SIZE: 0 product, 11 tests, ~70 other hand-written lines (this report and seeded-bugs.json).

## The guards (lean/VE/Scope/AuthoringExamples.lean:187-197)

```lean
-- `wordChar`'s filler list read directly, one code point each, inside a word where `clause`'s own refusal does not
-- apply (none is a `VE.Discourse.spaceChar` or in the control ranges): kills its list-empty, list-first, list-last,
-- list-drop-first and list-drop-last mutants; the plain space and a heading without a filler stay admitted
#guard !spaced "aᅟb"
#guard !spaced "aᅠb"
#guard !spaced "a⠀b"
#guard !spaced "aㅤb"
#guard !spaced "aﾠb"
#guard spaced "a b"
#guard readHeading "# AㅤB" == none
#guard readHeading "# A B" != none
```

`readHeading` is reachable from the examples (it is in `VE.Scope.Pinned`, which the module opens), so step 1's heading guard
is there, with its opposite direction ("# A B" is still read).

## Step 2: each code point depends on the list alone

`wordChar c = !VE.Discourse.spaceChar c && 0x20 ≤ c.toNat && !(0x7F ≤ c.toNat && c.toNat ≤ 0x9F) && ![…].contains c.toNat`.
`spaceChar` (lean/VE/Discourse/Access.lean:31) is `Char.isWhitespace` (space, tab, CR, LF) or 0x09-0x0D, 0x1C-0x1F, 0x85,
0xA0, 0x1680, 0x2000-0x200A, 0x2028, 0x2029, 0x202F, 0x205F, 0x3000; the control test refuses below 0x20 and 0x7F-0x9F.
None of 0x115F, 0x1160, 0x2800, 0x3164, 0xFFA0 is in either, so no mutant is equivalent. The builds confirm it per code
point. Each guard below failed under a mutant that removes only list entries:
- U+115F, line 190: M995, M5771, M6108.
- U+1160, line 191: M3104.
- U+2800 and U+3164, lines 192 and 193: seed-3.
- U+FFA0, line 194: M3441.

## Step 3: the mutant runs (failing first)

The plan maps the mutants by text (`tm.plan(root, base)` filtered to `Pinned.wordChar`'s `list-*` operators, script
/tmp/sc7wc-scripts/planmap.py). At the base b00f97f5c2 and at HEAD the plan gives the same 8703 mutants and the same ids
M995 list-empty, M3104 list-first, M3441 list-drop-last, M5771 list-last and M6108 list-drop-first, all on
lean/VE/Scope/Authoring.lean:26. These are main 1bd44797b's ids in reviews/tm-survivors-20261116-evidence. The selection
base is the nightly's 039d3dd5190e. With the merge base as `--base`, `wordChar` is unchanged and so not selected.

Command, run once with the base checked out (detached at b00f97f5c2) and once at HEAD bc3699d5d3:

```
zsh /home/seyran/code/manage-agents/iso.sh tmesc-sc7wc-{base,head} 16G -- nice -n 19 uv run python tools/trust_mutants.py \
  --base 039d3dd5190e5eea878d24c4f88af811dfd05914 --max-mutants 5000 --jobs 4 --only M995,M3104,M3441,M5771,M6108 \
  --test lean/VE/Scope/AuthoringExamples.lean --json <out>
```

| run | record | head | KILLED | SURVIVOR | other |
|---|---|---|---|---|---|
| base | trust-mutants-base.json | b00f97f5c2 | 0 | 5 | 0 |
| HEAD | trust-mutants-head.json | bc3699d5d3 | 5 | 0 | 0 |

The kills at HEAD are at AuthoringExamples.lean:190 for M995, M5771 and M6108, :191 for M3104 and :194 for M3441 (the
`detail` field of each record). The first HEAD run was on e1e4d2d75a, where the same guards had lower-case hex escapes,
and it also gave 5 KILLED. The run was repeated on bc3699d5d3 so the record matches the final test text.

## Seeded bugs (seeded-bugs.json)

The changed file is the test module lean/VE/Scope/AuthoringExamples.lean. Every seed edits lean/VE/Scope/Authoring.lean,
and each was restored with `git checkout`. The check is `lake build VE.Scope.AuthoringExamples`, which failed (rc 1) at:
- M995, M3104, M3441, M5771 and M6108 (the filler list): AuthoringExamples.lean:190, :191 and :194, as above.
- seed-1, readHeading's `spaced h` changed to `!h.isEmpty`: AuthoringExamples.lean:196 (the heading guard), also :69 and :80.
- seed-2, 0x62 added to the filler list: AuthoringExamples.lean:195 (the positive control `spaced "a b"`), among others.
- seed-3, 0x2800 and 0x3164 dropped and readHeading's `k ≤ 6` changed to `k ≤ 0`: AuthoringExamples.lean:192 and :193
  (U+2800 and U+3164), and :197 (`readHeading "# A B" != none`). The older `#guard !clause "x.ㅤ"` guards at
  :181-185 still passed under this seed, as the task said they would.

## Trust and DELTA

`uv run python tools/trust_map.py --since b00f97f5c2` gave: `K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0`
and `PASS`. There is no DELTA.md: the change adds checks to a test module, so nothing a user sees changes.
`python3 -I …/light-lane.py check` printed `LIGHT 11 changed lines … no trusted-core file`. The task still asks for the
mutant record, so the two targeted runs above were done anyway.

## Not run here

The full gate is run by the chain on the final HEAD. The selected tests are in the build report.
