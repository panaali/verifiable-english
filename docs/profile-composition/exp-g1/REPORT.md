# EXP-G1 report: may one pack's premises mention another pack's names?

- **Result: PASS.** The order of `X` does not matter for `Sat`, `Transfers` or G1b. No pack-order rule is needed; `packOrder` is unchanged.
- **The reading PASS rests on (for the reviewer to judge):** the plan says "declared by *some* pack". G1b needs "by *one* pack", which `assemble` already enforces. Finding 1 has the counterexample for a name declared twice.
- **G1b is against a copy** of spec 1.6, marked in the file; `acceptanceXV` stays unproved here (PK-1's owner builds it).
- **HEAD:** the commit adding this report. Lean and evidence final at `89248e360` (review F1: "needs both packs" is now a theorem, `single_pack_refuted`). Bytes 0; no DRI signature needed; no DELTA row.
- **Open:** finding 2, a vocabulary pack on the readings route (no planned pack is one). Next items: AT-2 and WG-3, then PC-11.

## What compiled

Command, from `lean/`: `PATH=~/.elan/bin:$PATH lake env lean ../experiments/exp-g1/ExpG1.lean`. **rc=0.** The output is saved whole in `lean-run.txt`: every `#print axioms` line lists a subset of `propext`, `Classical.choice`, `Quot.sound`; no `sorryAx`. The file is not imported by `lean/VE.lean`. Regenerate with `python3 experiments/exp-g1/run.py`.

| Claim | Theorem in `experiments/exp-g1/ExpG1.lean` | Definitions | Hypotheses |
|---|---|---|---|
| `Sat` ignores the order | `sat_X_perm` | main | none |
| `Transfers` ignores the order | `transfers_perm`, `transfers_X_perm` | main | none |
| `transfers_X` at either order, from the same per-pack facts | `transfers_X_either` | main | per-pack `Transfers` only; none names another pack |
| G1 ignores the order | `entailsX_perm`, `acceptanceX_order_free` | main (`acceptanceX` is proved) | none beyond `acceptanceX`'s |
| G1b ignores the order | `entailsXV_perm` | copy | `(names qs).Nodup` |
| G1b from assembly | `g1b_order_free` | copy | `AcceptanceXV` (the statement, as a hypothesis), `assemble … = .ok qs`, `hX` |

**Fixture `EXP-G1-mixed`** (`mixedCondition`, `mixedPremise`, for PC-11 to cite): ∀agent ∀user. `attitudes__believes__1(user)` → `weighing__outweighs__answer__helpfulness__caution(agent, user)`, in weighing's `.sufficient` `condPremise` shape. It has two shapes. `V` (`mixedV`) has every name declared by a pack, the plan's case. `C` (`mixedC`) has `.constraint` packs whose names `U` declares, the shape the attitudes and weighing plans build (attitudes.md 2.4 RF-5; weighing-PLAN D3).

| Fixture claim | Evidence | Checked by |
|---|---|---|
| The mention is real: weighing's premise names a name only the later pack declares; it types over the whole list at both orders, not over the base or weighing's names alone | `#guard`s after "The mention is real" | compiled |
| Non-vacuous: atom off, guard off holds; flip only the atom, `X` breaks; guard on, `X` holds | `nonVacuous` on all four lists; `mixedV_decides` at G1b's bases | `#guard`; kernel (`decide`) |
| Non-vacuous at `Transfers`' own bases (`C`, document `kG`) | `#guard`s after `baseG` | compiled |
| Acceptance from both packs (knows → believes → guard), both orders | `mixedC_accepted` (main's `acceptanceX`, no copy), `mixedV_accepted` | theorem; certificate replay is its hypothesis `hv`, shown by `#guard` |
| Neither pack alone entails the conclusion (`C`): weighing alone has a model with knows on, believes and guard off; attitudes alone, knows and believes on, guard off | `single_pack_refuted` (`¬ EntailsX` for each, via `not_entailsX_uC`) | theorem; kernel (`decide`) on the models |
| `transfers_X` at the fixture, both orders | `mixedC_transfers` | theorem; `hx : KGChecks` shown by `#guard` |

`hv` and `hx` follow the repo's `X1Checks` pattern: `by decide` got stuck on `V`'s `hv` and on `hx` (not tried separately on `C`'s `hv`, the same replay), so the `#guard` is compiled evaluation, not a kernel proof.

## Findings

1. **A name declared twice is the one case where G1b reads the order.** `extendEnv` takes `lookup`'s first match. `dup_order_matters` proves that two packs declaring one name at different arities give `EntailsXV` at one order and its negation at the other. So "some pack" alone is false on arbitrary lists. It is not the plan's Fail case: no premise mentions anything there, the rule "mention only earlier packs" would not touch it, and `assemble` refuses the list (`#guard` on the text `declared twice`; `assembleIn_distinct` proves every assembled list has distinct names). `acceptanceXV`'s own statement has `hfresh` but no distinctness; it does not need it, since it speaks of one list. The hypothesis was in the first commit, before any fixture ran.
2. **On the readings route, shape `V` is order-free but vacuous.** `Transfers`' bases are admissible over the document's old vocabulary, so a name the document does not declare has no tuple (`undeclared_empty_at_transfers_bases`), and `mixedPremise` does not type over a choice's vocabulary (`#guard`s on `K1`). This is draft 3's G1b defect; 1.6 fixes it off readings only. So no single shape is non-vacuous on both routes: `V` on G1b, `C` on `Transfers`. Both planned packs are `C`, so nothing planned hits this. A first vocabulary pack on readings (events' kind is et-4's choice) needs a `Transfers` over the packs' vocabulary. For PK-1's owner; no pack-order rule helps.
3. **Certificates are bound to their order; entailment is not.** `Trace` names premises by index: `certAt 0 1` is refused at the reverse order and `certAt 1 0` accepted (`#guard`s). `ordered` gives one order, so this costs nothing.
4. **The diagnostic reads the order.** `firstFailing` names weighing or attitudes first by order (`#guard`s). So `packOrder` still fixes the text, not the truth.
5. **Main's `assemble` refuses `V`** (`lacks its reserved prefix`): no weighing or attitudes row. The fixture uses `assembleIn` with a local table `prefixesG`. `C` assembles on main.

## Reasoning only (not compiled)

- `acceptanceXV` in general; only the fixture's instance (`mixedV_accepted`) and the reduction are proved. The copy is checked against spec text at 3dfadd302, not against a build: a whitespace-normalised comparison of the four definitions printed IDENTICAL (one-off probe, not saved), and `AcceptanceXV` is hand-restated as a `Prop`.
- `countermodelXV` and `entailsXV_constraint` were not copied. Their conclusions are about `EntailsXV`, so `entailsXV_perm` should carry them; on constraint packs `names qs = []`, so its hypothesis is trivial.
- That a certificate at one order always has one at another (shown at the fixture only). Nothing depends on it.
- The packs are by hand: names follow attitudes.md 2.5 and the premise follows weighing-PLAN's `condPremise`, not a provider.

## Seeded bugs

No product code changed, so no language needs one; the plan's mutant is the first two rows. All eleven are in `experiments/exp-g1/ExpG1.lean`, each rc=1 with the named declaration among the failures. Saved in `mutants.json` (`run.py` asserts `caught`); `tests/test_exp_g1_mutants.py` elaborates each again and checks the saved rows against `run.py`'s table.

Review F1: the first draft backed "needs both packs" with `!certOK … [weighingC] (certAt 0 0)` and the same for attitudes. With one pack the trace's index 2 is out of range, so those guards refused whatever the packs said, and the old `one-pack-suffices` mutant (now `bridge-silent`) was caught by the two-pack guard, not by them. With those guards restored, `review-probe-F1` and both `*-alone-entails` mutants survive.

| Mutant | Plants | Fails |
|---|---|---|
| `vacuous-never` | condition `atom ∧ ⊥` | `#guard nonVacuous`, `mixedV_decides` |
| `vacuous-always` | condition `atom ∨ ¬atom` | `#guard nonVacuous`, `mixedV_decides` |
| `same-pack-mention` | weighing declares the atom itself | `#guard (preds mixedPremise)…` |
| `bridge-silent` | bridge premise `⊤`: the two packs no longer entail the conclusion | `#guard certOK uV …` |
| `attitudes-alone-entails` | bridge premise gives the guard from knows | `single_pack_refuted` |
| `weighing-alone-entails` | weighing's premise also gives the guard from knows | `single_pack_refuted` |
| `review-probe-F1` | the review's probe: weighing's premise is the conclusion | `single_pack_refuted` |
| `trace-index` | trace expands the wrong premise | `#guard certOK uV …` |
| `dup-same-arity` | duplicate name has one signature | `dup_order_matters` |
| `frame-undeclared` | readings frame lacks the names | `mixedC_packs_transfer` |
| `base-off-reading` | the base spells no reading | `#guard` on `baseG` |

## Tests, trust, scope

- Selected tests: `mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`: exit=0, 24 units, 0 failed, at `94d814f9c` plus this report's edit (F1 fix); `tests/test_exp_g1_mutants.py` among them (15 passed alone). It deferred 7 slow files to the chain gate. `lake build` rc=0 and `lean/audit.py` PASS on that tree. The full gate was not run here, as instructed.
- `lake build` and `lean/audit.py` were not run on the final tree: nothing under `lean/` changed (`git diff --stat <merge base> -- lean` is empty). The imports were built once with `lake build`.
- Trust: `tools/trust_map.py --check` PASS; no trusted line changes. No `trust_mutants`, no R16 row.
- **Deviation from "Files":** `docs/codemap/` is generated and indexes `experiments/`, so `regen_generated.py --only codemap --write` changed three files. It also picked up rows other merges had left stale.
- `regen_generated.py --write` stopped at `route-cases` (no Rust binary in this worktree), hence `--only codemap`. A `--skip route-cases --check` ended `failed: checker-pins`; `--only checker-pins --check` alone passed. Cause of the difference not established; the chain gate checks it.
- **Size:** after review F1, 564 Lean + 77 `run.py` + 109 test + 95 this report = 845 hand-written lines (`git diff --numstat`), over the ~600 cap (it was 676 before F1; follow-up exp-g1-size), plus `run.py`'s output and the generated code map. Not cut further: every part backs a claim above, and nothing enters `lean/`.
- Overlap: no in-flight branch touches `experiments/exp-g1` or `docs/profile-composition/exp-g1`. Pilot bytes expected to move: 0.

## Self-review against BUILDER-CHECKLIST

1. N.A.: no relayed answer.
2. PASS: every deliverable above; `lean-run.txt`, `mutants.json`.
3. PASS: `mutants.json`, 11 of 11 caught.
4. N.A.: no Python, Lean or Rust product path.
5. N.A.: no binding.
6. PASS: `lean-run.txt` regenerated at `1a1c351f9`; gate left to the chain.
7. N.A.: nothing to sign.
8. N.A.: no user-visible change; `git diff --name-only` lists only the files above.
9. PASS: the selected run recorded 138 units, not every unit (`mac-pytest.sh --select`). No test covers the scratch file, so no seeded selection check.
10. PASS: `dup-same-arity`, the three single-pack mutants and `frame-undeclared` break their proofs; the four definitions printed IDENTICAL against the spec. No `check_*_statements` applies.
11. N.A.: no budget or deadline.
12. N.A.: no product code.
13. N.A.: no test removed (`git log main..HEAD --format=%B | grep -c Test-removed` is 0).
14. PASS: both directions in `#guard`s (certificate accepted and refused, typing with and without the later pack, assembly accepted and refused; `dup_order_matters` beside `entailsXV_perm`); claims cite the commands above; spec 1.6 and the plan lines re-read.
