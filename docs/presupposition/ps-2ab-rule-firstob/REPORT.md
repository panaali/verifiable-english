# ps-2ab-rule-firstob: the rule check names the rule's first obligation, else none

Status: built; no DRI signature reserved; no DELTA row (diagnostic text only, no verdict change). Trust V +5 (Admit.lean,
`ruleOb`), K +0, under standing ruling R16. Change: `admit`'s step 5 rule check (`unitsOk`) names the first obligation on
the failing rule, else none (`PresuppositionMismatch: : rule`), never another unit's obligation (ps-2ac review F2, DRI
adv1658 item 3). Run.lean's module docstring and ps-2ac/REPORT.md:47 say so; PROBE F2 exits 0. Next item: ps-4 (held).

SIZE: 12 product, 88 tests, 155 other hand-written lines (`git diff --numstat` against the merge base b81b82ef91;
product = Admit.lean + Run.lean's docstring; tests = Run.lean's guard section + the new pytest; other = this REPORT,
mutants.json, the allow file, ps-2ac/REPORT.md, trust-classes.json, trust-baseline.json; generated inventories and
the trust-mutants records excluded).

## Step 1: measured on main (b81b82ef91, before any edit)

F2's block (its construction was not saved with the recheck, so it was rebuilt from the finding's text): units u0
(`theOwnerU`), u1 (`theOwner`), u2 (r2's rule goal), u8 (rule r2); p1 a claim on u1 assumed by u0, p2 a rule act on r2
assumed by u2; the tree `[r1, r1', r2]`, where r1' is r1 with guard `⊤`. `lake env lean` on a scratch file that
`#eval`s `errOf (admit ...)` printed:

- one r1 node: `"admitted"`
- two r1 nodes: `"PresuppositionMismatch: p1: rule"` (p1 is a claim on u1, no obligation of r1)

Which `firstOb` calls in `Admit.lean` (main's lines) can reach the block-wide fallback:

| call | reaches the fallback | reason |
|---|---|---|
| :99 `bases3`, `(·.unit == x.id)` | no | `x` ranges over `withObligations D obs` (:88-89), which keeps only units with `obs.any (·.unit == x.id)`, so `find?` always finds one |
| :257 `unitsOk` content check, `(·.unit == x.1)` | no | `x` ranges over `R.bases = basesOf P` (:102-103), `P` built by `bases3` over `withObligations`, so each `x.1` has an obligation |
| :259 `unitsOk` rule check, `(·.position == .ruleAct N.name)` | **yes (the defect)** | `R.baseTree.nodes` holds every rule of `D.norms` (`baseTreeOf`, :106-112, maps all nodes), with or without a rule act; F2's r1 has none |
| :261 `unitsOk` tree check, any `.ruleAct _` | yes, by design | documented fallback "the block's first rule act, else its first obligation, else none"; guarded at Run.lean:337-341 (main); unchanged |

So only the rule check had the defect; the other callers keep `firstOb` and their text.

## Delivered

1. `lean/VE/Presupposition/Admit.lean`: `ruleOb obs n` (:34-37), the id of the first obligation whose position is
   `.ruleAct n`, else `""`; the rule check (:264) calls it instead of `firstOb`. Rule obligations are exactly the
   `.ruleAct n` positions (`regen`, :136-137, requires `N₀.name == n`). `firstOb` and its other three callers are unchanged.
2. Wording: Run.lean's module docstring (:13-15) now reads "steps 3 and 5 name the unit's first obligation, step 5's
   rule check the rule's first obligation, else none (`PresuppositionMismatch: : rule`), the tree check ...";
   docs/presupposition/ps-2ac/REPORT.md:47-48 says the same. PROBE F2 (ps-2ac-looprecheck1.final.md line 8), run from
   the worktree root: exit 0 (`PROBE_F2=0`); on main it exits 1.
3. Guards, Run.lean:342-359 (fixtures `r1b`, `docF2`, `obsF2`, classed T in tools/trust-classes.json like the other
   RunExamples): the three blocks `[p1, p2]`, `[p1, p2, p3]`, `[p1, p3, p2]` (p3 r1's own assumed rule act on u9) are
   each admitted with one r1 node (:355); with two r1 nodes (:357) the first is refused `PresuppositionMismatch: : rule`
   quoting no obligation and no unit (not p1, the block's first; not p2, which the tree check would name), and the
   other two `PresuppositionMismatch: p3: rule` (r1's own act, whether after p2 or before it).
   `tests/test_presupposition_rule_ob.py` (new) runs the same blocks and checks the same texts (3 tests, `3 passed`).
   Both fail on main: main's text for the two-node block is `p1: rule` (seeded bug M1 below restores exactly main's
   lookup, and both the guard and the test fail).

Deviation (conservative, no new exposure): the task asks for the pytest to run the block "through the service". No
service mode runs `admit` on main (`grep -rl Presupposition lean/VE/Service` is empty; `admitWrapped` is wired into the
document answer by PS-4, which is held). The test therefore elaborates the block with `lake env lean` against the
built `VE.Presupposition.Examples` under `tmp_path` and compares the text Lean prints; Python decides nothing. Adding a
service route for this would be a new mode and a new exposure, outside this row.

Tried and dropped: a fourth case giving r2 two nodes stops at step 4 (`PresuppositionAssumedUnit: p2: u2`), before
the rule check, so it does not test this row.

## Seeded bugs and mutants (docs/presupposition/ps-2ab-rule-firstob/mutants.json)

Each was planted, built with `lake build VE.Presupposition.Run`, run with
`VE_NATIVE_PREBUILT=1 VE_LEAN_PREBUILT=1 uv run pytest -q tests/test_presupposition_rule_ob.py`, and restored; Lean is
the only product language changed (no Python or Rust product code).

| id | file | mutant | fails |
|---|---|---|---|
| M1 (seeded 1) | lean/VE/Presupposition/Admit.lean (`ruleOb`) | restore the block-wide fallback | Run.lean:357; `test_rule_without_obligation_names_none` (`p1: rule`) |
| M2 (seeded 2) | lean/VE/Presupposition/Admit.lean (`ruleOb`) | the block's last obligation instead | Run.lean:357; `test_rule_without_obligation_names_none` (`p2: rule`) |
| M3 | Admit.lean (`ruleOb`) | first rule act on any rule | Run.lean:357; both refusal tests |
| M4 | Admit.lean (`ruleOb`) | search the last obligation only (run 1's list-last survivor) | Run.lean:357; `test_rule_with_obligation_names_its_first` |
| M5 | Admit.lean (`unitsOk`) | look the rule's obligations up by `N.pred` | Examples.lean:1053 |

Trust-mutants sweep (`zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --json docs/presupposition/ps-2ab-rule-firstob/trust-mutants.json --test lean/VE/Presupposition/Run.lean`, ran on ve-cloud-2/3):

- run 1 (head 19c133983a; record trust-mutants-run1.json): 32 KILLED, 14 SURVIVOR, 4 UNKNOWN, 8 INVALID, exit 1. 13
  survivors were in the fixture `docF2` (then unclassified, so counted trusted); one in `ruleOb` (list-last). Fix:
  the fixtures are classed T, and the `[p1, p3, p2]` block kills list-last (M4).
- run 2 (head 880a0ea866; trust-mutants-run2.json): 1 definition (`ruleOb`), 16 mutants: 5 KILLED, 0 SURVIVOR,
  3 UNKNOWN, 8 INVALID, exit 1. The 3 UNKNOWN are `list-empty` mutants that do not elaborate (type mismatch / invalid
  field notation at Admit.lean:37).
- run 3 (`--allow trust-mutants-allow.json --rescore trust-mutants-run2.json`; trust-mutants.json, head 56969fa370): 5 KILLED,
  0 SURVIVOR, 0 UNKNOWN, 8 INVALID, 3 ALLOWED, exit 0 (13 verdicts reused, identical inputs). The allow reason cites
  M1-M3, which change the same lookup and fail.

## Trust (R16)

`uv run python tools/trust_map.py --check` on the final tree: `K +0, S +0, D +0, G +0, tied +0, unclassified +5,
trusted +5; VE/Presupposition/Admit.lean: trusted +5` (`ruleOb` with its docstring), exit 0 after
`trust_map.py --allow` (`allowed V +5 over b81b82ef91ad`, signed "SIGNED by standing ruling R16 (DRI-RULINGS.md),
ps-2ab-rule-firstob, 2026-11-11"). The new trusted definition `ruleOb` is exercised by Run.lean:357 and the pytest,
which can fail (M1-M4). FOLLOW-UPS.md row under "## ps-2ab-rule-firstob" asks for the ties pass.

## DELTA

None: only the id inside one diagnostic's text changes, and only on blocks whose failing rule has no obligation; no
verdict, code or availability changes (the guards at Run.lean:355 still admit the one-node blocks; every other
refusal guard in Run.lean and Examples.lean builds unchanged: `lake build` completed, 1395 jobs).

## Checks run

- `lake build` (whole library): `Build completed successfully (1395 jobs)`; `python3 lean/audit.py`: `PASS: 849 source
  files; 9508 named theorem declarations audited`.
- `uv run python tools/regen_generated.py --write` after the last Lean edit; `tools/lean_statements.py` rerun.
- `uv run python tools/gate_collection.py --check --prebuilt`: `3 added, 0 removed by a trailer, 0 refused, 0 stale
  and 0 malformed trailers`.
- `tools/select_tests.py --base $(git merge-base HEAD main)`: 121/591 units, `tests/test_presupposition_rule_ob.py`
  among them; the Lean change selects the lake build that runs Run.lean's guards.
- Selected tests on the committed final tree: see the build report (run after this file is committed).

spec re-read: "step 5 names the rule's first obligation, or none" against reviews/dri-decisions-20261110-adv1658.md
item 3 (:47-49) and the backlog row's note; "the rule's obligations" against `regen`'s `.ruleAct n` case
(Admit.lean:136-145).

Pilot bytes expected to move: 0 (no pilot output carries `admit`'s report before PS-4; an estimate, not audited).

## Notes for the DRI

- The pytest elaborates Lean directly rather than through the service (see Deviation); PS-4 can move it onto the
  document route when that route exists.
- Main's `docs/codemap/*` were stale at the merge base; `regen_generated.py --write` refreshed entries of other items
  (act-phrases, Acts) along with this item's.
