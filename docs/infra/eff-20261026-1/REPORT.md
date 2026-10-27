STOP RULE (both rules fire, measured): only 7 of the 46 corpus mutants are SURVIVOR at their reviewed tree and KILLED at their fixed tree under `--classes all` (8 needed); and on me-12a's reviewed HEAD the widened sweep takes 3.01× the default sweep (202 s against 67 s; 2.5× allowed). `--classes` is kept only as `prototype.patch`. `tools/` and `tests/` are the merge base's, byte for byte. No row reserves a DRI signature.

# eff-20261026-1: widen trust_mutants beyond trusted definitions, measured and stopped

`python3 docs/infra/eff-20261026-1/check.py` exits 0 and prints: "pairs 7 of 46 rows (stop below 8); widened/default me-12a 3.01x (202 s / 67 s), df-1ad 1.5x (510 s / 341 s) (stop above 2.5x or 2700 s); fired: ['pairs', 'time']; 0 problems".

## What was measured

**The prototype.** The tool is `tools/trust_mutants.py` at the merge base `058fea806`, plus [prototype.patch](prototype.patch). The patch adds four things:
- `--classes LIST`: `trusted` is the default. A list may also hold `all` (every trust_map class but P and T) or trust_map's own class names, which it reads from `trust_map.CLASSES` and `KIND_CLASSES`.
- Each mutant records its `trust_class` and `trusted`, and SURVIVOR and UNKNOWN lines name the class.
- The summary counts verdicts per class.
- `inputs` records the classes inside `options`. That is the key speed-tmchecks' `previous` treats as fixed, so `--rescore` never carries a verdict across a different selection, before or after that item merges.

The default selection is unchanged. On this checkout, `plan()` of main's tool and of the prototype without the flag gave the same mutants, field for field, over two bases: 666 and 1,372 mutants (`evidence.json` `default_plan`). With `--classes all` the same bases give 1,491 and 3,631 mutants.

**The corpus** has 46 rows (`evidence.json` `corpus`):
- The 21 rows of eff-20261021-1 whose gap is "unselected". Its REPORT says 19, but its `evidence.json` lists 21: me-5 has 5, me-9 1, me-9b 7, df-1ac 1 and me-2 7.
- One row for each PROBE mutant of me-12a F1 (7) and F2 (17) and of df-1ad F1 (1).

Each row was replayed by [replay.py](replay.py), which works as eff-20261021-1's replay did. It uses detached scratch worktrees of the reviewed and the fixed tree, with lean/.lake hard-linked from this checkout's build (the same toolchain and manifest), on the VM, one Lean build at a time. The tool's own `plan` names the row's declaration, its class, and whether the default and `--classes all` select it. It also lists every mutant `all` writes on that line. The row's `replay` mutant is either the reviewer's form or the tool's mutant with the same behaviour on that line (`replay_note` says which, and why). That mutant was run through the tool's unchanged `main`, with the plan narrowed to the item's replay mutants. The raw output is in [replay/](replay/). The columns are derived by `replay.derive`, the one owner of the rule.

me-12a was read only through git and detached worktrees; `/home/seyran/code/ve-me-12a` was never touched. (me-12a merged into main at `f1943fab6` during this item.)

## Rule 1: the corpus replay

| Outcome (reviewed → fixed tree) | Rows | Why |
| --- | ---: | --- |
| **SURVIVOR → KILLED (a pair)** | **7** | me-5's limits: `maxFacts` twice, `maxUnknowns`, `maxSteps`. me-2: `supports` drop-first and drop-last, and `recordJson` `≤`→`<`. Five use the reviewer's exact form; me-5 27 and 29 use a same-behaviour `lit-plus`. |
| not generated | 27 | The form is beyond OPERATORS. 7 are me-12a F1 (the environment `(x :: ρ)` → `[x]`, a branch → `none`), and all 7 are class S, which the default already selects. 12 are me-12a F2: an arm → `[]`, a cons tail dropped, the left `++` operand dropped (append-right cuts only the atom before `++`), `k` → `k + 1`, two ranks swapped, a conjunct added. 3 are me-2 (sibling argument, string literal, pattern alternative), 3 are me-9b (match-arm and `do`-effect order), 1 is me-5 (`>` → `≥`) and 1 is df-1ad F1 (an argument → `[]`). |
| SURVIVOR → SURVIVOR | 5 | me-9 and 4 me-9b rows. Their fixes added pytest fixtures only, which no Lean check can see (L93's class). |
| SURVIVOR → UNKNOWN, UNKNOWN → UNKNOWN | 4 + 1 | me-12a F2 in `Term.sites`, `Term.sitesList` and `Formula.sites`, one `mutual` block. The fixed tree's checks refute the mutants (`Examples.lean:290`, `:292`), but the probe sees the block's sibling constants change, so its unchanged rule gives no kill. F2-9's `[].length` does not elaborate, so it is UNKNOWN at both trees. |
| KILLED → KILLED | 1 | df-1ac W9: `and-or` on `x.collides &&` is killed at the reviewed tree already. It differs from dropping the conjunct when `collides` holds. |
| SURVIVOR → text changed | 1 | me-2 scan-six: the fix rewrote the line. |

What the widened sweep does show is earlier signal. At the reviewed trees, 17 of the 46 rows are SURVIVOR under `--classes all`, and the default selects none of their declarations. Those 17 come from 5 of the 7 items: me-5 4, me-9b 4, me-2 4, me-12a 4 and me-9 1. So a builder would have seen a survivor on the line a reviewer later mutated by hand. But the tool confirms the fix (KILLED) in only 2 items, me-5 and me-2.

| Item | Row | Definition | Class | Default selects | `all` selects | Replay mutant | Reviewed | Fixed | Pair |
| --- | --- | --- | --- | :---: | :---: | --- | --- | --- | :---: |
| me-5 | review-26 | `Calc.FM.maxFacts` | G[R] | no | yes | `lit-minus` (exact) | SURVIVOR | KILLED | **yes** |
| me-5 | review-27 | `Calc.FM.maxFacts` | G[R] | no | yes | `lit-plus` (same behaviour) | SURVIVOR | KILLED | **yes** |
| me-5 | review-28 | `Calc.FM.maxUnknowns` | G[R] | no | yes | `lit-minus` (exact) | SURVIVOR | KILLED | **yes** |
| me-5 | review-29 | `Calc.FM.maxSteps` | G[R] | no | yes | `lit-plus` (same behaviour) | SURVIVOR | KILLED | **yes** |
| me-5 | review-30 | `Calc.FM.eliminate` | C | no | yes | none (beyond OPERATORS) | NOT GENERATED | TEXT CHANGED | no |
| me-9 | denominator-true | `Calc.Poly.fits` | C | no | yes | `and-or` (same behaviour) | SURVIVOR | SURVIVOR | no |
| me-9b | numerator-zero-divisor-dropped | `Calc.Expr.zeroDivisor` | C | no | yes | `or-and` (same behaviour) | SURVIVOR | SURVIVOR | no |
| me-9b | left-operand-zero-divisor-dropped | `Calc.Expr.zeroDivisor` | C | no | yes | `or-and` (same behaviour) | SURVIVOR | SURVIVOR | no |
| me-9b | point-names-left-only | `Calc.identityDecide` | C | no | yes | `append-left` (exact) | SURVIVOR | SURVIVOR | no |
| me-9b | twelve-points | `Calc.identityDecide` | C | no | yes | `lit-minus` (exact) | SURVIVOR | SURVIVOR | no |
| me-9b | bin2-right-fault-first | `Calc.Expr.bin2` | C | no | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-9b | claim-compare-second-side-first | `Calc.Claim.inline` | C | no | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-9b | claim-within-lo-first | `Calc.Claim.inline` | C | no | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| df-1ac | W9 | `Defaults.Wire.CoherenceReplay.pairs` | G[V] tied | no | yes | `and-or` (same behaviour) | KILLED | KILLED | no |
| me-2 | span-hash | `Calc.Wire.recordJson` | D[I] | no | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-2 | support-hash | `Calc.Wire.recordJson` | D[I] | no | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-2 | supports-no-observation | `Calc.Wire.supports` | D[I] | no | yes | `list-drop-first` (exact) | SURVIVOR | KILLED | **yes** |
| me-2 | supports-no-assumption | `Calc.Wire.supports` | D[I] | no | yes | `list-drop-last` (exact) | SURVIVOR | KILLED | **yes** |
| me-2 | span-strict | `Calc.Wire.recordJson` | D[I] | no | yes | `le-lt` (exact) | SURVIVOR | KILLED | **yes** |
| me-2 | literal-form | `Calc.Wire.literalFault` | D[R] | no | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-2 | scan-six | `Calc.Wire.limitFault` | D[R] | no | yes | `lit-minus` (same behaviour) | SURVIVOR | TEXT CHANGED | no |
| me-12a | F1-1 | `Arith.Term.value` | S | yes | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-12a | F1-2 | `Arith.Holds` | S | yes | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-12a | F1-3 | `Arith.Holds` | S | yes | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-12a | F1-4 | `Arith.Holds` | S | yes | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-12a | F1-5 | `Arith.Holds` | S | yes | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-12a | F1-6 | `Arith.Defs.env` | S | yes | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-12a | F1-7 | `Arith.Defs.env` | S | yes | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-12a | F2-1 | `Arith.Formula.sites` | G[R] | no | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-12a | F2-2 | `Arith.Formula.sites` | G[R] | no | yes | `append-left` (exact) | SURVIVOR | UNKNOWN | no |
| me-12a | F2-3 | `Arith.Formula.sites` | G[R] | no | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-12a | F2-4 | `Arith.Formula.sites` | G[R] | no | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-12a | F2-5 | `Arith.Term.sites` | G[R] | no | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-12a | F2-6 | `Arith.Term.sites` | G[R] | no | yes | `append-left` (exact) | SURVIVOR | UNKNOWN | no |
| me-12a | F2-7 | `Arith.Term.sitesList` | G[R] | no | yes | `append-left` (exact) | SURVIVOR | UNKNOWN | no |
| me-12a | F2-8 | `Arith.Term.sites` | G[R] | no | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-12a | F2-9 | `Arith.Term.sites` | G[R] | no | yes | `list-empty` (same behaviour) | UNKNOWN | UNKNOWN | no |
| me-12a | F2-10 | `Arith.Formula.sites` | G[R] | no | yes | `append-left` (exact) | SURVIVOR | UNKNOWN | no |
| me-12a | F2-11 | `Arith.Formula.sites` | G[R] | no | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-12a | F2-12 | `Arith.Term.sites` | G[R] | no | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-12a | F2-13 | `Arith.Refusal.rank` | G[R] | no | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-12a | F2-14 | `Arith.Refusal.rank` | G[R] | no | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-12a | F2-15 | `Arith.Refusal.rank` | G[R] | no | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-12a | F2-16 | `Arith.Refusal.rank` | G[R] | no | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| me-12a | F2-17 | `Arith.Defs.refusals` | G[R] | no | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |
| df-1ad | F1-1 | `Defaults.Wire.replayModelOn` | C | no | yes | none (beyond OPERATORS) | NOT GENERATED | NOT GENERATED | no |

## Rule 2: the cost, on ve-mac-1

Each HEAD was swept twice with `mac-pytest.sh --worktree <detached worktree> --trustmut -- --base 7855620f3 --jobs 6 --max-mutants 1000 [--classes all]`. The worktree's only uncommitted file was the prototype's `tools/trust_mutants.py`. Times are each JSON's `seconds`, the tool's own measure. The runner's one-off setup for each new tree (a lake build: 336 s and 251 s) came before the first sweep and is in the logs only.

| HEAD | Default | `--classes all` | Ratio |
| --- | --- | --- | ---: |
| me-12a `57071552` | 163 mutants, **67 s** ([json](cost/me-12a-default.json)) | 529 mutants, **202 s** ([json](cost/me-12a-all.json)) | **3.01×** |
| df-1ad `b8f32f8f` | 80 mutants, 341 s ([json](cost/df-1ad-default.json)) | 114 mutants, 510 s ([json](cost/df-1ad-all.json)) | 1.50× |

The 45-minute cap is far off: the longest widened sweep took 8.5 minutes. In both HEADs, the widened sweep's trusted mutants are exactly the default sweep's, with the same verdicts; `check.py` compares them as multisets. On me-12a, the default sweep's 163 trusted mutants in `VE.Arith` (S) give 0 KILLED, 147 SURVIVOR, 12 UNKNOWN and 4 INVALID. The widened sweep adds 366 G[R] mutants: 110 KILLED, 109 SURVIVOR, 99 UNKNOWN and 48 INVALID.

## Build outcome

The stop rule fired, so nothing was built. The committed change is evidence only, all of it under `docs/infra/eff-20261026-1/`:
- this REPORT, `evidence.json`, `replay.py`, `check.py` and `prototype.patch`;
- the raw `replay/` and `cost/` output.

The prototype's commit `739c18d85` is undone in `9fd0f67a2`. `git diff $(git merge-base HEAD main) HEAD -- tools tests` is empty. No product, Lean, Rust or generated file changed. Trust is +0. There is no user-visible delta, so there is no DELTA.md. No gate, merge train or nightly reads anything here.

`check.py` is the saved-evidence check (architecture decision D4); no permanent report test was added. It checks:
- every row's `before` text exists in its reviewed tree (`git show`);
- every row has a plan at both trees, the plan read that tree, and every run the plan asks for exists. A missing one fails the row as skipped;
- no verdict is unmeasured, and every chosen replay mutant is one the tool writes at the reviewed tree;
- every recorded column equals `replay.derive`;
- each cost sweep ran on ve-mac-1 over its HEAD (from its log), with nothing NOT RUN and the same options, and its trusted verdicts equal the default sweep's;
- the recorded pairs, times, fired rules and decision equal what it recomputes.

`replay.py` reruns from the patch. Rerunning one tree's plan (me-9 reviewed) with the patched tool worktree gave the saved plan exactly.

Coordination: `tools/` is untouched, so speed-tmchecks merges without a conflict here. `mac-pytest.sh --trustmut` passes `--classes all` and `--classes=all` through unchanged; neither falls into its two-argument cases, and the cost logs show `--classes all` reaching the runner.

## Seeded bugs (check.py; each planted, `check.py` run with exit 1, then restored with `git checkout`)

1. `evidence.json`: me-5 review-26 `fixed_verdict` set to SURVIVOR. It fails with "evidence.json does not state the replay … ('SURVIVOR', 'KILLED')".
2. `replay/me-2-fixed.json` deleted. It fails with "me-2/span-hash: skipped (a plan or a run its plan asks for is missing)", and the same for every me-2 row.
3. `cost/me-12a-all.json` `seconds` set to 150 (2.24×). It fails with "stop_rule times … measured …" and "the measurements fire ['pairs']".
4. `replay.py` `KILLS` also counts UNKNOWN as a kill. It fails with "me-12a/F2-2: … {'pair': (False, True)}".
5. `cost/df-1ad-all.json`: one trusted mutant's `raw_status` changed from KILLED to SURVIVOR. It fails with "df-1ad: the widened sweep's trusted mutants are not the default's, with its verdicts".
6. `cost/df-1ad-all.json` `NOT RUN` set to 3. It fails with "df-1ad all: 3 mutants NOT RUN of 114".

No product code changed in any language, so no Lean, Rust or product-Python seeded bug applies. The task's three tool seeded bugs need the tool built, and the stop rule forbids that.

Selected tests: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run` at `9fd0f67a` ran 9 units on ve-mac-1, with 0 failed. As directed, no full release gate was run. No test from `main-known-red.txt` came up.

## Orchestrator lines

None to install. The flag is not built, so BUILDER-CHECKLIST item 3 and build-checklist.txt line 13a stay as installed, and the review prompt is unchanged.

If the DRI decides to build `--classes` despite the stop (see follow-up 1), these are the lines:
- build-checklist.txt 13a, appended: "An item that adds or changes decoders, admission checks or limits in Lean (trust_map D[R], D[I], G[R], G[I], C or tied [V]) also runs the sweep with `--classes all`. Every survivor there gets a killing fixture or an `--allow` reason. An UNKNOWN in a `mutual` block is allowed with that reason."
- BUILDER-CHECKLIST 3, the trust_mutants bullet: the same sentence.
- Review prompt: "Rerun trust_mutants with `--classes all` before planting hand mutants. Plant only forms it does not write."

## Follow-ups (not built here)

1. **DRI decision: build `--classes` despite the stop?** The flag would flag a survivor on the reviewed line in 5 of 7 items (17 of 46 rows) before review. It would confirm the fix in only 2, and it costs 1.5–3.0× a sweep: +135 s and +169 s on these HEADs.
2. **Mutual blocks give no kill.** A check that refutes a mutant of one member of a `mutual` block is UNKNOWN, because the probe's drift test sees the siblings change. Treating the block's members as the mutated declaration is a verdict-rule change, so it needs its own hunt.
3. **Forms beyond OPERATORS**, which account for 27 rows: a cons tail dropped, an arm → `[]`, an argument → a sibling or a constant, `k` → `k + 1`, `>` and `≥`, and two literals swapped.
4. **Pytest-only fixtures** (L93) still read as survivors.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean response route or schema changed.
2. PASS: the measurement, the stop rule and its evidence (`evidence.json`, `check.py`) are the deliverables; nothing was built past the stop.
3. PASS: `check.py` fails on all six seeded bugs listed above. N.A. for trust_mutants: no trusted Lean change.
4. N.A.: no product behaviour changed.
5. N.A.: no relayed field changed.
6. N.A.: the chain runs the final-HEAD gate.
7. PASS: no DELTA row, no reserved signature, trust +0.
8. PASS: no user-visible change, so no DELTA.md.
9. PASS: `mac-pytest.sh --select` at `9fd0f67a` selected 9 units, 0 failed.
10. N.A.: no Lean statement or theorem changed.
11. N.A.: no public budget, limit or deadline changed.
12. N.A.: no runtime product path changed; the sweep times above are the task's measurement.
13. PASS: no test was removed or renamed.
