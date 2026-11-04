# ps-1b: the readings and the rows (spec 4.3 Reading.lean, 4.4 Rows.lean) (build report)

No DRI signature is reserved in this item. There are no DELTA rows: the item adds only new Lean, and no answer changes.
Trusted growth is +64 (K +0, S +43, V +21), covered by standing ruling R16 (see "Trust").
Status: built. Every statement in spec 4.3 and 4.4 is proved, with its 7.1/7.2 fixtures. Seeded bugs M4, `peel` and
`buildPre "plural"` are each killed, plus one mutant per new trusted definition.
Checks: Lean audit PASS, trust_map --check PASS, trust_mutants exit 0, selected tests exit 0, ps-1's discourse tests 163 passed.
Open: the full gate runs in the chain on the final HEAD.

Feature item ps-1b (PS-1's second part; plan `docs/spec/presupposition-PLAN.md:731-751`; spec `docs/spec/presupposition.md`
on main since ps-1). Branch `feature/ps-1b`, merge base 8205a8e69.

## Preconditions

- **Statement gate.** PASSED, as the task states (p3ver1 statements PASS, PS-S stub gate 115/115, re-check 2 PASS). The
  DRI's ps-s-stub items 1-3 change no 4.3/4.4 statement. Synthesis round 2's edits 1-7 and DEC 10 touch neither file.
- **Statements are the spec's text.** Probe: I split each `lean` block of 4.3 (`presupposition.md:593-698`) and 4.4
  (`:699-751`) at its declarations and whitespace-normalised each piece. Reading: 25 pieces, Rows: 12, none missing from
  the normalised files. No statement changed.
- **In-flight overlap.** I ran `git diff --name-only main...<b>` over `lean-first/*`, `feature/*`, `infra/*` and
  `foundation/*`. No branch touches `lean/VE/Presupposition/`. `lean/VE.lean` and `tools/trust-classes.json` are shared
  with at-1a, ci-2, cmp-s3, cmp-s4c, df-5, et-4b, pc-1g, pe-1 and me-1. My edits there are two import lines and two new
  module entries, so they merge by union.

## Plan rows delivered

| Row (task "Deliver") | Delivered | Evidence |
|---|---|---|
| (1) Reading.lean: `Reading`, `DefinedAt`, the three carriers, `Root`, `carried`, `peel`. Its 13 theorems are proved: `collapse`, `collapse_certified`, `collapse_assumed`, `asserted_false_off_goal`, `conditioned_vacuous_off_goal`, `carriers_on_goal`, `carried_denote`, `carried_asserted`, `carried_conditioned_off`, `carried_on_goals`, `peel_carried`, `carried_idle` and `inPlace_iff_conditioned_shallow` | 997f12a03 | `python3 lean/audit.py`: "PASS: 771 source files; 8591 named theorem declarations audited …; only the declared standard axiom allowlist." |
| (2) Rows.lean: `definite`, `plural`, `generic`, `buildReading`, `buildPre`. Proved: `definite_defined`, `plural_defined`, `generic_defined` | 997f12a03 | `definite 0`'s `pre` and `strong` are `uniqueD` and `assertive` (Examples.lean:35-36). They are built through ps-1's `uniqueOpen` and `assertiveOpen`, with no second builder |
| (3) Examples.lean: ps-1's literal rows rebuilt from the rows, with the literal values kept as equalities | 890a338ff | `rOwner`, `rManager`, `rMgr`, `rPl` and `rTheir` (:28-29, :65, :90, :104). The literal guards are at :35-38, :68, :93 and :107 |
| (3) 7.1 rows | 890a338ff, 25570a808 | Examples.lean:153-317 holds 67 new `#guard`s (43 → 110):<br>• S1 definedness :166-169; S1/S13 :172-174<br>• S12 :181-197; S25 :199-203; S26 (whole unit through `carried`) :205-214<br>• S16 :216-247; S20 :266-291; S23 :293-298; S24 :300-317<br>• S21's asserted and conditioned values :137-140 |
| (3) 7.2, both directions of the rows this item owns | same | • `plug_congr`/`collapse` :187-189<br>• `DefinedAt` (definite) :166-168<br>• `carriers_on_goal` :175-177 (true) and :190-192 (false)<br>• `carried_denote` :230-232<br>• `inPlace_iff_conditioned_shallow` :193-197 (true, S12) and :202-203 (false, S25), plus S26 :212-214 |
| ps-s-stub-c: the two false-side guards | 890a338ff | **`carried_conditioned_off`: Examples.lean:238** (S16 neither: unit F = owner's goal F), beside the true side at :237. **`carried_on_goals`: Examples.lean:243** (S16 unready owner, idle manager: unit F = `B` F), beside the true side at :242 |
| (4) `lean/VE.lean` | 890a338ff | `import VE.Presupposition.Reading`, `import VE.Presupposition.Rows` |
| (4) `tools/trust-classes.json` | 890a338ff, 25570a808 | • S: `Reading`, `Reading.DefinedAt`, `assertedAt`, `conditionedAt`, `inPlaceAt`, `Root`, `carried`, `peel`, `definite`, `plural`, `generic`<br>• D[V]: `buildReading`, `buildPre` (wire-tuple builders, like discourse's `uniqueD`)<br>• T: the fixtures<br>• No K |
| (4) generated inventories | 61ba55def (+ 25570a808: `lean_statements.py` after the fixture edit) | `uv run python tools/regen_generated.py --write` ("wrote 35 entries"). `tools/layer_policy.py` is not edited (ps-1's probe: `VE.Presupposition.*` is layer 2) |

**Not in this item:**
- ps-1c: S14 and S22 (they need `ruleGoal`/`conditionRule`), S8 (`data_attribute_proved`), P1-P4, P13 and M3.
- PS-2a: the parts of S12, S25 and S27 that read `expectedReadings` or `carrierAllowed`, S26 over `claimReading`, S23's
  `unitContent` check, S15, S17-S19 and the `expected`/`table` rows.
- Not a fixture: S2's `collapse_certified` step needs a replayed tableau certificate. S2's goal stays proved by ps-1's
  `example` (Examples.lean:82).

## Deviations

- **Helper lemmas.** I added these, all proved, under the standard axioms:
  - Reading.lean: `foldr_and_denote`, `foldr_implies_denote`, `peel_ands` and `peel_implies`.
  - Rows.lean: `raise1_denote`. It reads `VE.Norms.inst_denote` and `VE.Discourse.denote_prefix`; neither file is edited.
- **Unused hypotheses.** `definite_defined`'s `hσ`, `hP` and `hS` are unused, as in `description_definedness`. The
  statement is the spec's, so they stay.

## S11: discourse is unchanged

This item edits no Discourse file. `mac-pytest.sh -- tests/test_discourse.py tests/test_discourse_answer.py
tests/test_discourse_lean.py tests/test_discourse_three_way.py tests/test_discourse_constitution.py` gave "163 passed"
(exit 0; `evidence/tests.txt`).

## Seeded bugs (Lean only; this item changes no Python or Rust product code)

`mutants.json` lists 13 hand mutants, one per new trusted definition. Each was applied alone, built with
`lake build VE.Presupposition.Examples` and restored. The "proofs" column lists what fails in the plain build. The
"#guards" column lists what fails when the theorem bodies of Reading/Rows are replaced by `sorry`; otherwise the broken
proofs stop the build before the guards run.

| Id | Definition | Mutant | Proofs | #guards (Examples.lean) |
|---|---|---|---|---|
| M4 (spec 7.5) | `carried` | conditioned goals outside the asserted ones | `carried_denote`, `peel_carried` | **S16's first guard :223**, :230, :234, S26 :213 |
| L-peel | `peel` | `0, 0` → `0, 1` (stops one binder early) | `peel_implies` | **`peel_carried`'s :252**, :253, :254, :257 |
| L-buildPre-plural | `buildPre` | `"plural"` without `∃` | — | **S23 :295**, S20 :270, :289 |
| L-Reading | `Reading` | without `DecidableEq` | — | :274-279 (they do not elaborate) |
| L-DefinedAt | `Reading.DefinedAt` | `strong ↔ weak` | `collapse` | — (a Prop that only proofs read) |
| L-assertedAt | `assertedAt` | `close` for `goal` | `asserted_false_off_goal`, `carriers_on_goal` | S21 :137 |
| L-conditionedAt | `conditionedAt` | plugs `weak` | `carriers_on_goal` | :195 |
| L-inPlaceAt | `inPlaceAt` | plugs `weak` | `carriers_on_goal` | S12 :184, :195, S25 :202 |
| L-Root | `Root` | drop `bare` | `carried_on_goals`, `carried_idle`, `inPlace_iff_conditioned_shallow` | (statements do not elaborate) |
| L-definite | `definite` | `uniqueAt σ D D` (no `raise1`) | `definite_defined` | S24 :312, :316 |
| L-plural | `plural` | `strong` without `∃` | `plural_defined` | :93, :107, :260 |
| L-generic | `generic` | `weak := body` | `generic_defined` | :263 |
| L-buildReading | `buildReading` | `generic b p` | — | :278 |

**R16 mechanical mutants.** The first run was `mac-pytest.sh --trustmut -- --max-mutants 1000 --json
docs/presupposition/ps-1b/trust-mutants.json --test lean/VE/Presupposition/Examples.lean`. It gave 27 KILLED,
5 SURVIVOR and 7 UNKNOWN.
- Two survivors were in `carried`: the conditioned list cut to its first or last element. The new two-conditioned
  guard at Examples.lean:257 kills both.
- The rest are allowed in `trust-mutants-allow.json`:
  - three mutants of `DefinedAt`, a Prop, each naming the four proofs it breaks;
  - `plural` `all-any`, `carried` `list-empty` and `Root` `ctor-drop`, which do not elaborate.

The rerun used `--allow … --rescore` with the first JSON: 29 KILLED, 10 ALLOWED, 0 SURVIVOR, 0 UNKNOWN, exit 0 (head
25570a808, `trust-mutants.json`).

## Trust

`uv run python tools/trust_map.py --check` reports "PASS: K, S and untied [V] within 8205a8e69668 and the allowances
introduced since". The growth is under R16's 150 lines:
- Reading.lean: S +33.
- Rows.lean: S +10 and D[V] +21.
- K +0; trusted +64 in all.

The allowance in `docs/trust-baseline.json` is "SIGNED by standing ruling R16 (DRI-RULINGS.md), ps-1b, 2026-10-18". R16's
conditions are met: no K growth, and a mutant per new trusted definition that a named check kills (above). The
"## ps-1b" ties-pass row is in FOLLOW-UPS.md.

## Size, bytes, evaluators

- **Size.** `git diff --numstat 8205a8e69`, without generated files and tool outputs (`trust-mutants.json`,
  `trust-baseline.json`), gives:
  - Lean 459/18: Reading 161, Rows 93, Examples 203/18, VE.lean 2. About 145 of these lines are the spec's 4.3/4.4
    blocks, pasted verbatim.
  - trust-classes.json 69/1.
  - mutants.json, the allow file, evidence and this report: about 150.

  The total is about 680 lines, or about 535 without the pasted spec text. That is over the ~600 limit by the same
  margin as ps-1 (its F2): the 7.1/7.2 fixtures the task names take 67 guards. No deliverable was cut.
- **Pilot bytes.** 0, as the plan claims for PS-1. The RF census row (19 units, 1,432 B, estimate) waits for PS-2a.
- **Evaluators.** None added. `carried` and `peel` are structural over lists and formulas the caller already holds, and
  the builders are single matches. PS-2a's runner charges them.

## Tests run

- While iterating: `lake build` of `VE.Presupposition.Reading`, `VE.Presupposition.Rows` and
  `VE.Presupposition.Examples`.
- Once on the finished code:
  - `regen_generated.py --write` (it needed `python3 tools/rust_build.py` first: the route-cases step reads the Rust
    binary);
  - `lake build` (1298 jobs) and `python3 lean/audit.py` PASS, rerun once after the last fixture edit;
  - `trust_map.py --check` PASS;
  - `gate_collection.py --check --prebuilt`: "0 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed";
  - `mac-pytest.sh --select -- --base 8205a8e69 --run`: 99/543 units, exit 0, 0 failed, tree bc15aba101 (VM; no Mac
    slot). It is in `evidence/tests.txt`. Later commits add only `docs/presupposition/ps-1b/` files.
- Not run: the full gate (the chain runs it). No test in main-known-red.txt was touched.

## Spec re-read

- 4.3's 25 pieces against `presupposition.md:595-678` and 4.4's 12 against `:700-746`, by the probe in Preconditions.
- 7.1's rows S1, S1 (definedness), S12, S13, S16, S20, S21, S23, S24, S25 and S26 (`:1268-1291`), value by value.
  S16's "one ready owner" has the manager's goal true (vacuous, since the owner's `strong` holds). So the true side of
  `carried_on_goals` is at that model, as 7.2 says.
- 7.2's rows `plug_congr`/`collapse`, `DefinedAt`, `carriers_on_goal`, `carried_denote`, `carried_conditioned_off`,
  `carried_on_goals` and `inPlace_iff_conditioned_shallow` (`:1300-1311`).
- 7.5's M4 (`:1389`).

## Next item

ps-1c: spec 4.5 Rules.lean and 4.6 Agree.lean (`ruleGoal`, `conditionNode`, `conditionRule`, `source_identity_entails`,
the agreement theorems), with S8, S14, S22, P1-P4, P13 and M3. Then PS-2a.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed Lean answer; no mode, wire field or decoder is added.
2. PASS: every "Deliver" row above has a commit and evidence. The diff has no Python and no report test, and overlap is
   checked (Preconditions).
3. PASS: `mutants.json` has 13 hand mutants, all killed. `trust-mutants.json` exits 0 with
   `trust-mutants-allow.json`, whose rows name exact definitions and operators.
4. PASS: S11. The five discourse tests gave 163 passed (`evidence/tests.txt`). There is no Python/Rust change to
   compare.
5. N.A.: no field is read from a Lean answer.
6. PASS: the selected run is on tree bc15aba101, the tree of the last code commit. The full gate runs in the chain on
   the final HEAD.
7. PASS: no DELTA row. Trust growth cites R16 with its mutants, and no signature is reserved.
8. PASS: no output changes. No Discourse or other existing product file is edited, and the discourse tests pass.
9. PASS: `tools/select_tests.py --base 8205a8e69` selects 99/543 units, not all. The Lean mutants are caught by the
   gate's `lake build` (Examples.lean is in `lean/VE.lean`).
10. PASS: each theorem has a seed that breaks its proof (`mutants.json` "proofs"). The statements are the spec's text
    (the probe). There is no `tools/check_*_statements.py` for this plan.
11. N.A.: no budget, limit or deadline.
12. N.A.: no runner or route changes; the new definitions are single structural passes.
13. PASS: no test removed. `gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0 malformed.
14. PASS: both directions for every 7.2 row this item owns:
    - `carried_conditioned_off` :237/:238 and `carried_on_goals` :242/:243;
    - `buildPre`/`buildReading` ok and each error (`row`, `arguments`, `body`) :266-291;
    - `peel` some and none :252-257.

    Each claim cites its command or file, and the spec re-read is listed.
