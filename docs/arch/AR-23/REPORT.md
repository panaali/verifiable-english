# AR-23: closure's meaning through Core (consolidation step 3c)

**No DELTA row waits for a DRI signature.** DELTA has R7 rows only: records unavailable on both sides with identical
outputs. No approved theorem statement changed and no hypothesis was added, so nothing here needs a DRI decision.

Batch AR-23 of the architecture plan (`ARCHITECTURE-REVIEW-2026-10.md` 4.5, Phase C), named by the DRI for the
2026-11-09 pass (`reviews/dri-decisions-20261105-arch-pass.md` item 2). Branch `infra/arch-20261109-1`. Merge base at
the time of writing: `a3454b6ba`.

Main was merged three times, each followed by a regeneration of the generated files under R12:
- at `a8572afb0` (regenerated at `8c9b52855`);
- at `b58755067` (regenerated at `eb334fbd1`);
- at `7f741e751` (regenerated at `ee43c72ce`).

After the last evidence, main moved on to `f3f40d51d` with two merges (en-e3a, sa-checked-view). They touch none of
this batch's files and were not merged here. The merge base of this branch and main is still `a3454b6ba`, which the
saved evidence names.

## Measured outcome

| Measure | Before (base) | After (head) | Command and output |
|---|---|---|---|
| Trusted lines, whole tree | 62,095 (K 994, S 14,568) at `de7fb9469` | 62,085 (K 984, S 14,568) | `uv run python tools/trust_map.py --check` at head: "against a3454b6ba598: K -10, S +0, D +0, G +0, tied +0, unclassified +0, trusted -10 … PASS" |
| K in `VE/Closure/` | 102 (`Syntax` 92, `Paths` 6, `Consequence` 4) | 92 (`Syntax` 82, `Paths` 6, `Consequence` 4) | `trust_map.py --files <outside the tree>` at base and head (`evidence/trust.json`, `closure_files`) |
| Untied [V] | 46,533 | 46,533 | the same `--check` run: D +0, G +0, tied +0 |
| Untrusted lines | C 12,817, P 112,752 | C 12,761, P 112,648 | `evidence/trust.json` `totals.delta`: C −56, P −104, T +24, all lines −138 |
| `Closure/{Paths,Finite}` | 87 + 120 lines | 87 + 43 lines | `wc -l`; `Finite` holds only aliases and one-line corollaries |
| Statements | 8,506 entries | 8,507 (1 added, 0 removed, 0 changed) | `uv run python tools/lean_statements.py --diff <base> <head>` (`evidence/statements.json`) |
| Behaviour | – | 0 unlisted | corpus A/B, OUT, closure probe (below) |

**K fell by 10 lines, not by the plan's estimate of about 50 (closure K 76 → about 25, "the inductive only").** The
row's code change is done in full, but the estimate does not hold for two reasons.

1. **The embedding is now trusted.** The embedding into Core (`VE.Closure.Formula.toCore`, 18 lines) now defines what
   a closure formula means, so it is K. At base the same map was `VE.Core.embedClosure`, classed C (untrusted),
   because closure had its own semantics then and `embedClosure_denote` proved the two agree. The plan's figure
   counts only the inductive. It leaves out the map that the new definition of `denote` reads, and classing that map
   as anything but K would be wrong.
2. **Four syntax declarations stay K.** `embed` and `erase` (the v0 ↔ closure syntax maps, 14 lines each), `Edge` (7)
   and `reach` (5) are unchanged and remain K. Core's twins of all four are K too.

What did fall:
- closure's `denote` went from 19 lines to 4, and `WellFormed` from 14 to 4;
- the proofs that compared closure's semantics with Core's are gone (P −104 lines);
- closure's evaluator and checker copies are gone (C −56).

The measured closure K is 102, not the plan's 76: the plan's figure was taken on an older tree.

## Row 3c, item by item

Plan row (`docs/CONSOLIDATION-PLAN.md`, step 3, row 3c): "One semantics, two syntaxes: keep `Closure.Formula` as a syntax
type, define `Closure.Formula.denote a := (embedClosure a).denote` and `Closure.Entails` through Core;
`Closure/{Paths,Finite}` (315 lines) reduce to aliases of Core's | K 76 → about 25 (the inductive only);
`embedClosure_denote` becomes `rfl` | L, ST (statements of `conservativity`, `closure_route_acceptance` unchanged);
`Route/Budget.evalC` soundness restated through Core". Architecture plan 4.5, the AR-23 row: "`Closure.Formula.denote`
through Core; `Closure/{Paths,Finite}` aliases | `embedClosure_denote` by `rfl`; `conservativity` and
`closure_route_acceptance` unchanged | about 50 K lines".

| Deliverable (task) | Delivered | Commit | Shown by |
|---|---|---|---|
| 1. Keep `Closure.Formula` as a syntax type; `denote a := (embedClosure a).denote`; `Entails` through Core; `embedClosure_denote` by `rfl` | The inductive is unchanged. One embedding, `VE.Closure.Formula.toCore`, lives next to it in `Closure/Syntax.lean`. `VE.Core.embedClosure` is that embedding under its old name (`def embedClosure := VE.Closure.Formula.toCore`, still in `Core/Conservativity`, so every `-- uses …@VE.Core.Conservativity` tag stays). `Formula.denote S ρ a := a.toCore.denote S ρ`. `Entails E ps c := VE.Core.Entails E (ps.map toCore) c.toCore`. `embedClosure_denote` is `Iff.rfl`, `embedClosure_check` is `rfl`, and `entails_closure` is the identity, each with its statement byte-identical | `e81ed6800` | `lake build` rc 0; `statements.json` (`named_in_task_byte_identical`: all true); `lean/axioms.txt`: `embedClosure_denote`, `embedClosure_check` and `entails_closure` now "does not depend on any axioms" |
| 2. `Closure/{Paths,Finite}` aliases of Core's; every old name stays | `Closure/Finite` is Core's `Finite`: `namedEdges` and `bodyEdges` are abbreviations, `Formula.eval` is Core's `eval` on the embedding, and `mem_namedEdges`, `mem_bodyEdges`, `reachable_congr`, `eval_iff_denote` and `eval_false_iff_not_denote` are one-line corollaries with identical statements. `Closure/Paths` is unchanged: since AR-20 it already re-exports `VE/Paths.lean`, the module Core's `Paths` re-exports too, so it was already an alias file (frozen; no edit needed) | `e81ed6800` | `statements.json`: 0 changed; seeded bug M2 |
| 3. Every audited theorem name kept; `statements.txt` byte-identical for kept names; the 14 statements that use `VE.Closure.Formula.denote` byte-identical | 0 removed, 0 changed, 1 added (`VE.Closure.entails_iff`). All 14 are byte-identical, `conservativity` and `closure_route_acceptance` among them | `e81ed6800`, regenerated at `8c9b52855` | `evidence/statements.json`: `kept_all_byte_identical`, `uses_closure_denote_all_byte_identical` (14) |
| 4. Delete the closure-only lemmas the new definitions make redundant, each with its cover | None qualifies. Every lemma the new definitions make trivial is an audited name that item 3 keeps, or an old name that item 2 keeps, and its only cover would be a definitional equation, not a Core theorem; such a theorem "stays". Their proofs shrank to `rfl`, `Iff.rfl` or Core's theorem | `e81ed6800` | DELTA.md "Removed theorems" |
| `Route/Budget.evalC` soundness through Core (plan row 3c, evidence column) | The statement of `evalC_sound` is unchanged (item 3 forbids restating it). Its `Formula.eval` is now Core's on the embedding, and its proof unfolds Core's `eval` | `e81ed6800` | `statements.json`: `VE.Route.Budget.evalC_sound` byte-identical |
| Must not change: verdict, refusal text, step count, wire field, fault order | Not changed | – | corpus A/B, OUT and closure probe (below) |
| `checkCertificate`, `Closure.embed`, `decodeClosureTrace` stay; `decodeTrace_ne_embed` stays proved | All four untouched | – | `statements.json` (0 removed, 0 changed); `lean/audit.py` PASS |

### Frozen-file edits

Each edit to a file in `lean/VE/Route/frozen-sources.sha256`, and why row 3c needs it. The list was regenerated at
`8decd382f` and again after the merge.

- `lean/VE/Closure/Syntax.lean` (named by the task). Adds the embedding `Formula.toCore`, and defines `WellFormed`,
  `check` and `denote` through it. `check_iff_wellFormed` is now Core's theorem on the embedding.
  `conservativity` is reproved; its statement is unchanged. Adds `import VE.Core.Syntax`.
  Typing and its checker go beyond row 3c's literal "`denote`". They follow from its estimate "K → the inductive
  only", which leaves no closure-specific typing in K. They are behaviour-neutral: at base,
  `embedClosure_check` already proved by induction that closure's `check` equals Core's on the embedding, and the A/B
  confirms it.
- `lean/VE/Closure/Consequence.lean` (named by the task). Defines `Entails` through Core and adds `entails_iff`.
  `countermodel_sound` is reproved; its statement is unchanged. Adds `import VE.Core.Consequence`.
  `countermodelCheck` is untouched.
- `lean/VE/Route/Checker.lean` (not named by the task; K, frozen). Two proof edits only.
  - `closure_entails_iff` is now `(VE.Closure.entails_iff E ps c).symm`. Its statement is unchanged.
  - `closureValid_certificateSound` now goes through `closure_entails_iff`.
  - The cause: `Closure.Entails` is defined through Core's `Entails` of the mapped premises, so it is no longer
    definitionally the generic `Semantics.Entails` over closure formulas, and the old `Iff.rfl` no longer checks.
- `lean/VE/Closure/Paths.lean`: not edited.

### Other edits outside the closure files

Proof edits only. Every statement is unchanged (`statements.json`: 0 changed):
- `Closure/Tableau.lean` (`checkCertificate_sound_v0`);
- `Closure/CoreEquiv.lean` (`embedClosure_inj`, `reach_embed`);
- `Core/Conservativity.lean` (`path_iff`, `reachable_iff`, `embedClosure_denote`, `embedClosure_check`,
  `entails_closure`);
- `Route/Budget.lean` (`named_value`, `body_value`, `evalC_sound`);
- `Route/WireSound.lean` (`closure_denote_forget`);
- `Route/Background.lean`, `Data/Background.lean`, `Definitions/Route.lean`;
- `Service/Family.lean`, `Service/FamilyBundle.lean`.

The two `Service` files are pinned whole in `ve/assurance-manifest.json` as decoder files. Only theorem proofs changed
in them (`closure_graph_sound`, `closure_graph_entails`, `closure_readings_*_sound`, `closure_bundle_sound`), and no
decoder changed. Their pins (lines, SHA-256, range) and the decoder total were updated at `6566dd8b7`:
`tests/test_assurance_manifest.py -k pinned` gives 2 passed.

`lean/VE/Closure/Checks.lean` gains 19 `#guard`s (13 → 32) at `a585d8363`. They check the embedding per constructor kind,
closure's finite evaluation of each connective, the checker, and the two edge lists.

Trust table (`tools/trust-classes.json`): one row added, `VE.Closure.Formula.toCore` as K. `VE.Core.embedClosure` keeps
its base class C, as AR-20 kept its aliases' classes: it is now a one-line alias of the K embedding. No file was
deleted or moved, so `tools/layer_policy.py`, `tools/lean-layer-exceptions.json` and `tools/consolidation-ledger.json`
are untouched.

## Behaviour evidence (plan 4.1 item 2)

- **Corpus A/B, first merge base `de7fb9469`.** `tools/lean_first_diff.py record` over all nine corpora: the base from
  its own worktree (`/home/seyran/code/ve-ar23-base`) and the head (`547dc3aa2`) from this checkout, at the same time.
  The two recordings are byte-identical (SHA-256 `e2dbb554…` for both). Compared with `uv run python -m tools.evidence
  ab … --delta evidence/ab-delta.json`: "ab PASS", with 100,529 the same, 31 unavailable on both sides with identical
  outputs (R7, DELTA), and 0 unlisted.
- **Corpus A/B, merge base `95ed0e49b` (after the first merge of main).** Recorded again the same way: the base
  worktree at `95ed0e49b` and the head at `14e7dbe2e`. The recordings are byte-identical (`4d806d67…`): 100,530 the
  same, 30 unavailable on both sides, 0 unlisted.
- **Corpus A/B, merge base `a5088a09b` (after the second merge of main).** Recordings byte-identical (`8de0da3e…`):
  100,538 the same, 22 unavailable on both sides, 0 unlisted.
- **Corpus A/B, merge base `a3454b6ba` (after the third merge of main; the saved one).** The base worktree at
  `a3454b6ba` and the head at `ee43c72ce`, recorded at the same time.
  - The raw recordings differed in 4 pilot `document_check` records. On each, one side's Rust accelerator subprocess
    timed out (`CheckerUnavailable: Rust checker failed: … timed out after 14–20 seconds`) while the other side
    answered: 1 head-side time-out and 3 base-side.
  - All 4 were re-run on both sides with `uv run python docs/arch/AR-20/pilot_rerun.py` (AR-20's script, unchanged).
    Each answered the same on both sides, in 80–200 s. Each re-run equals the recorded answer of the side that
    answered: 1 of 1 on base, 3 of 3 on head (`evidence/pilot-rerun.json`).
  - With the re-run outcomes in place of those 4 records, the two recordings are byte-identical (SHA-256 `c62acba7…`).
  - `uv run python -m tools.evidence ab … --base-commit a3454b6ba… --head-commit ee43c72ce… --delta
    evidence/ab-delta.json` gave "ab PASS" over 100,560 records: 100,531 the same, 29 unavailable on both sides with
    identical outputs (R7, DELTA rows 1–4), and 0 unlisted (`evidence/ab.json`).
  - Review F1: the first `ab.json` named the base `a3454b6ba598c95e…`, typed by hand, which is no commit; the merge
    base is `a3454b6ba5982d7c…`. `tools.evidence ab` now resolves every typed commit through Git and refuses one the
    repository lacks (`tools/evidence/__init__.py` `commit`; tests `test_ar23_f1_*` in
    `tests/test_evidence_toolkit.py`). `ab.json` was rebuilt from the same recordings (`c62acba7…` on both sides)
    with the base from Git: "ab PASS", and only `base_commit` differs from the first record.
  - After `ee43c72ce`, only `docs/` and `tools/trust-classes.json` change. The table gets back main's module order (the
    auto-merges had reordered it; its content, one added row, is unchanged), and only `tools/trust_map.py` reads it.
- **The four runs agree.** Whole-UDHR pilot records timed out on both sides in each run: 10, 9, 1, then 8. The
  machine load differed between runs. `udhr-20261018T1800Z` `translation-whole.ve.md` timed out in all four. Every
  other one answered in at least one run, the same on both sides.
- **Lean output differential (OUT).** Every `lean_exe` was built in both checkouts. The baseline was saved at
  `de7fb9469` with `tools/lean_output_diff.py --save-baseline`, and the head was compared with `--all --jobs 8`:
  "441 invocations, 441 run on both builds …; 1 differences, 0 timed out". The one difference is the `ve_service`
  corpus session's stderr, after two pre-existing `PANIC at Lean.Json.setObjVal!` lines that are the same on both
  builds. Exit code and stdout are equal, and so is stderr without the backtrace frames. Two runs of the base binary
  differ in the same way (`evidence/out.json`), as AR-22 found. Not an output change.
- **Closure's gates, row for row.** `docs/arch/AR-23/closure_probe.py` was run in each checkout with its own `ve`,
  `ve_conformance` and `ve_service`. It covers:
  - an induction certificate at `@1`, at `@0`, at the unknown `@2` and at Core's version;
  - an n-ary `atom` invariant and an `atom` conclusion, which closure refuses with "invalid indexed formula";
  - a stale certificate and an unknown rule;
  - every original closure certificate at `@0` and at `@1`;
  - on the route runner: `@1`, `@0`, `@2`, an atom invariant, induction under `@0` (steps 1) and an unknown rule.

  Result: "closure probe EQUAL {'certificate': 134, 'route': 6}", base and head rows byte-identical
  (`evidence/closure-probe.json`).
- **Closure tests.** `VE_NATIVE_PREBUILT=1 uv run pytest -q tests/test_closure.py tests/test_closure_certificates.py
  tests/test_closure_core_replay.py tests/test_closure_induction.py tests/test_closure_witnesses.py
  tests/test_data_three_way.py tests/test_p0_three_way.py tests/test_assurance_manifest.py -n 8`: "235 passed,
  3 skipped". The three skips are three-way rows outside Rust's scope.
- **Closure fuzz.** `uv run python rust/fuzz_closure.py`: 3000 cases, 3000 agreements. Its JSONL is byte-identical at
  base and head (SHA-256 `23e85ddd…`, the same as AR-22's record) (`evidence/closure-tests.json`).
- **CPU.** `ve_conformance` over `conformance/closure.json` (46 cases), base and head alternated five times: CPU median
  0.219 s at base and 0.221 s at head, stdout byte-identical (`evidence/closure-tests.json` `cpu`). The extra cost is
  within noise: closure's `check` and `eval` now walk the embedding once before Core's.

## Seeded bugs

Lean is the only product language this batch changes. `uv run python tools/mutants.py docs/arch/AR-23/mutants.json
--evidence docs/arch/AR-23/evidence/mutants.json`: "mutants: 4/4 killed". Each command builds `VE.Closure.Checks` and
prints Lean's errors.

| Id | File | Seeded | Fails |
|---|---|---|---|
| M1 (a) | `lean/VE/Closure/Syntax.lean` | the embedding that defines `denote` swaps a connective: `.and` → `.or` | `VE/Closure/Syntax.lean:85:43` (`VE.Closure.conservativity`, unsolved goals). With that proof cut by hand: `#guard`s `VE/Closure/Checks.lean:17` (on main), `:35` and `:47` |
| M2 (b) | `lean/VE/Closure/Finite.lean` | the `bodyEdges` alias points at the wrong Core definition (`VE.Core.namedEdges`) | `VE/Closure/Finite.lean:20:2` (`VE.Closure.mem_bodyEdges`, type mismatch). With that proof cut by hand: `#guard` `VE/Closure/Checks.lean:56` |
| M3 (c) | `lean/VE/Closure/Syntax.lean` | one case of the embedding (`reachNamed`) dropped | `VE/Closure/Syntax.lean:27:2`: "Missing cases" (a build failure, not a check) |
| M4 (c') | `lean/VE/Closure/Syntax.lean` | the `reachNamed` case kept but embedded as `.plus` whatever its kind | `#guard`s `VE/Closure/Checks.lean:13` (on main) and `:43` |

**Trust mutants (R16).** `zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --allow
docs/arch/AR-23/trust-mutants-allow.json …` selected 18 mutants of the 4 changed K definitions (`toCore`, `WellFormed`,
`denote`, `Entails`).
- The first run gave 0 KILLED, 14 SURVIVOR and 4 UNKNOWN.
- Rerun with the allow file (`--rescore`): "0 KILLED, 0 SURVIVOR, 0 UNKNOWN, 0 INVALID, 18 ALLOWED, 0 NOT RUN", exit 0.
- Rescored again after each merge of main (bases `95ed0e49b`, `a5088a09b` and `a3454b6ba`): the same result, exit 0 (`docs/arch/AR-23/trust-mutants.json`).

The 16 allowed mutants of `denote`, `WellFormed` and `Entails` are Props that no check can evaluate. Each allow reason
names the proofs that mutant breaks, as R16 asks. The 2 `all-any` mutants of `toCore` name a constructor that does not
exist. `toCore` itself is checked per constructor kind by the new `#guard`s, and M1 and M4 show those checks fail.

## Trust (D3)

`uv run python tools/trust_map.py --check` on the final head: K 984, S 14,568, trusted 62,085. Against the merge base,
K −10, S +0, untied [V] +0, with no new allowance. "PASS: K, S and untied [V] within a3454b6ba598 and the allowances
introduced since". Phase C asks for a reduction (plan 4.1 item 3), and K fell. See "Measured outcome" for why it fell
less than the plan estimated.

## What AR-24 or the next consolidation step may now do

- Closure has one meaning, Core's, so any later statement about closure consequence can be proved once, for Core.
  - `VE.Closure.entails_iff` gives closure's consequence in closure's own syntax.
  - `VE.Core.entails_closure` is the identity.
  - AR-24's route skeleton may treat closure's consequence as Core's on the embedding (no separate semantics to
    instantiate); its soundness instance is still `checkCertificate_sound`.
- More K can come out of `Closure/Syntax` the same way, through `toCore`. None of this is required by row 3c, so it
  was not done in this batch's frozen file.
  - `Closure.erase`: 13 lines, defined in K. It could be `VE.Core.erase a.toCore`, reproving `erase_embed` and
    `embed_of_erase` through Core (about −12 K).
  - `countermodelCheck` (C): a remaining one-owner copy of Core's, which could become
    `VE.Core.countermodelCheck M (ps.map toCore) c.toCore`.
  - `embed`, `Edge` and `reach` are closure syntax and stay.
- Step 2b and step 8a (the formula codec) may get smaller. Closure's typing, meaning and finite evaluation are now
  Core's. What stays closure-specific: its syntax (the inductive, `Closure/Surface` parse and print, the `Closure/Bridge`
  decoders), its certificate version gate, and the route's budgeted evaluator `Route/Budget.evalC`. `evalC`'s soundness
  statement reads `Formula.eval`, which is now Core's on the embedding.
- Not done, and not in this step (plan): making `Closure.Formula` a subtype of `Core.Formula`, and merging Order into
  a core parameterised by a term theory.

## After the gate

The chain gates the final commit `<G>`. From `ee43c72ce` (the commit the A/B recorded) to `<G>`, only these change:
`docs/arch/AR-23/`, `docs/CONSOLIDATION-PLAN.md` (the quoted step 3 ledger row) and `tools/trust-classes.json` (main's
module order restored). No recorder reads any of them. Then make one report commit that changes only
`docs/arch/AR-23/`:

    cp gate-result.json docs/arch/AR-23/evidence/gate.json
    uv run python -m tools.evidence scope --base main --head <G> --out docs/arch/AR-23/evidence/scope.json
    uv run python -m tools.evidence ab ~/.cache/ve-ar23d/base2.jsonl ~/.cache/ve-ar23d/head2.jsonl \
        --base-commit a3454b6ba --head-commit <G> \
        --out docs/arch/AR-23/evidence/ab.json --delta docs/arch/AR-23/evidence/ab-delta.json \
        --corpus probe conformance readings pilots discourse rights quantity norm_defaults document
    uv run python tools/batch_evidence.py --check docs/arch/AR-23 --report-commit HEAD

`ab` resolves `a3454b6ba` through Git and saves the full id (`a3454b6ba5982d7cb5e216d10432a94f6177652a`, the
scope's `base`); it refuses an id that names no commit. Name the commit the recordings were made at, not
`$(git merge-base …)`: after another merge of main the check then refuses the old recordings instead of relabelling
them. If main is merged again before the train merges this branch, record the A/B again against the new merge base,
as above (`~/.cache/ve-ar23d/` holds the recordings of `a3454b6ba`). Main had already moved to `f3f40d51d` when this
report was written.

## Selected tests

`MAC_PYTEST_NO_DEFER=1 zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`, on the committed
`9b5e061ea` (clean tree): 465 test units in 6 shards; 1 failed.
- The failure was `tests/test_consolidation_tools.py::test_committed_ledger_names_real_declarations`. The plan's
  section 4 quotes the trust ledger's measured figures, and step 3's "removed" figure fell from 30 to 14 trusted lines
  because this batch did part of step 3.
- Fixed at `68f6e9d80`: `docs/CONSOLIDATION-PLAN.md` quotes the remeasured row, with a note in its measurement
  paragraph. `tools/consolidation-ledger.json` is unchanged, because no file went or moved.
- Rerun of the failed id alone: `zsh mac-pytest.sh -- tests/test_consolidation_tools.py::test_committed_ledger_names_real_declarations`
  gave "1 passed" (HEAD `68f6e9d8`, clean).
- After the third merge of main: `uv run pytest -q tests/test_consolidation_tools.py -k ledger` gave "45 passed".
  `tests/test_assurance_manifest.py -k pinned` gave "2 passed".
- The selected set was not run again after that merge, which brought only main's own changes. The chain's gate runs
  on the final HEAD.

## Spec re-read

- "define `Closure.Formula.denote a := (embedClosure a).denote`" against `docs/CONSOLIDATION-PLAN.md:336`.
  `denote S ρ a := a.toCore.denote S ρ`, where `embedClosure := toCore`; `embedClosure_denote` is `Iff.rfl`.
- "and `Closure.Entails` through Core" against `docs/CONSOLIDATION-PLAN.md:336`: `Entails := VE.Core.Entails (ps.map
  toCore) c.toCore`.
- "API kept: `VE.Closure.Formula`, `Closure.Entails`, `Closure.Tableau.checkCertificate` …, `Closure.embed`, every
  audited theorem name" against `docs/CONSOLIDATION-PLAN.md:339`: `statements.json`, 0 removed.
- "Not in this step: … making `Closure.Formula` a subtype of `Core.Formula`" against `docs/CONSOLIDATION-PLAN.md:341`:
  not done.
- "`embedClosure_denote` by `rfl`; `conservativity` and `closure_route_acceptance` unchanged" against the AR-23 row of
  `ARCHITECTURE-REVIEW-2026-10.md` 4.5 (line 1128 of `design/arch-review`): `statements.json`.
- "What AR-23 may now do" against `docs/arch/AR-22/REPORT.md:197-207`: the 14 statements are kept byte-identical, and
  `Closure/{Paths,Finite}` needed no change in AR-22's files.

SELF-REVIEW: 1 A, 1 B, 6 C; fixed 5. The A (stale decoder pins) is fixed at `6566dd8b7`. The B (name the
`Route/Checker` frozen edit and the typing edits) is fixed in "Frozen-file edits" above. Of the C items:
- the honest K statement, the `embedClosure` class, the implicit row items and the mutated `toCore` case (M4) are done;
- `erase` and `countermodelCheck` through Core are named above as later cuts and not done in the frozen files.

## Self-review against BUILDER-CHECKLIST

1. Typed and contained Lean answers: N.A. No relayed answer, schema or wire field changed. The A/B is byte-identical
   and `closure-probe.json` is EQUAL.
2. Every deliverable built, no rule broken: PASS. See "Row 3c, item by item" (commits and evidence per row). There is
   no Python copy of Lean logic and no permanent report test; the overlap check is under "Coordination" below.
3. Tests and gates can fail: PASS. Seeded M1–M4, 4/4 killed (`evidence/mutants.json`). Trust mutants exit 0 with
   18 allowed (`trust-mutants.json`).
4. Python, Lean and Rust agree: PASS. Corpus A/B 0 unlisted; `rust/fuzz_closure.py` 3000/3000; the
   `test_data_three_way.py` and `test_p0_three_way.py` runs pass (`closure-tests.json`).
5. R8 binding: N.A. No Python reading of a Lean answer changed.
6. Gate evidence matches the final HEAD: PASS for what the build can show. The A/B was recorded at the merge base
   after the sync with main. Scope and gate follow "After the gate".
7. No unsigned item: PASS. DELTA rows cite R7, and the trust budget fell (`trust_map.py --check` PASS).
8. Every user-visible change in DELTA: PASS. There is none; the A/B lists 0 unlisted and OUT shows no output change.
9. Test selection: PASS. `tools/select_tests.py --base $(git merge-base HEAD main)` selects
   `tests/test_closure*.py`, `test_closure_core_replay.py` and the three-way tests.
10. Lean statements say what is claimed: PASS. 0 changed statements (`statements.json`). `embedClosure_denote` and
    `embedClosure_check` are `rfl`, about the returned value. M1 breaks `conservativity`.
11. Budgets, limits and deadlines: N.A. No limit, budget or evaluator changed. `evalC` is unchanged code; only its
    proof changed.
12. No CPU or memory regression: PASS. `closure-tests.json` `cpu`: median 0.219 s base and 0.221 s head on the closure
    corpus. The ten whole-UDHR pilot records that timed out on both sides contain no closure formula (DELTA row 2).
13. `Test-removed` trailers: PASS. `uv run python tools/gate_collection.py --check --prebuilt`: "0 added, 0 removed by
    a trailer, 0 refused, 0 stale and 0 malformed trailers"; no test was removed.
14. Both directions, cited evidence, spec re-read: PASS.
    - The new `#guard`s check both truth values (`eval` true and false, `check` true and false).
    - Each claim here names its command or file.
    - The spec re-read is the section above.
15. The four classes:
    - No overclaim: PASS. "No delta" is backed by `ab.json`, `out.json` and `closure-probe.json`. "Byte-identical" is
      backed by `statements.json`.
    - No silent cut: PASS. Items 1–4 are all built. Item 4 deletes nothing, by the task's own rule, and that is stated.
    - Every new check can fail: PASS. M1, M2 (proof cut) and M4 fail named `#guard`s.
    - Limits charged before work: N.A. No limit changed.

## Coordination

Files touched, checked at the start against `git diff --name-only main...<branch>` for every in-flight branch
(`lean-first/*`, `feature/*`, `infra/*`, `foundation/*`):
- No branch edits `lean/VE/Closure/`, `lean/VE/Core/`, `lean/VE/Paths.lean` or `lean/VE/Route/{Budget,Closure}.lean`.
- `tools/trust-classes.json` (one added row) is shared with ten branches, and `ve/assurance-manifest.json` with
  several. Both are shared tables. The merge with main was automatic, and the files were regenerated and checked
  (`regen_generated.py --check`, `tests/test_assurance_manifest.py -k pinned`).
- `tools/layer_policy.py` is not touched.
- `docs/CONSOLIDATION-PLAN.md`: the quoted step 3 ledger row (14 removed lines, down from 30) and a one-line note in
  its measurement paragraph (`68f6e9d80`).

## Pre-existing failures

None met. The one failure of the selected run (above) was this batch's, and it is fixed. No test listed in
`main-known-red.txt` failed in the selected run.
