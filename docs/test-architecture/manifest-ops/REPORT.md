# tarch-manifest-ops: what still selects the whole suite (rank 4 item 5, continued)

DRI signature needed: none. **Stopped after step 1 (the task's stop rule).** Fewer than 3 merges select
everything because of the manifest or the pins: 0 of 54 with the map taken as fresh, 2 of 54 with the
selector's own drift check. In both of those 2, the cause is the uncertain units, not the missing operation
map. No selector code changed, and no VE output changed (DELTA.md: no rows).

Task: test-architecture draft 2, rank 4 item 5 (`reviews/test-architecture-2026-10-14.md` 2.3 and 3.5),
which the DRI's decision #5 (`reviews/dri-decisions-20261017b.md`) asked to re-measure. The worry behind it:
`manifest_change`'s "no safe operation map" (`tools/select_tests.py:647-655`) and the checker-pins rule
(cutoff REPORT finding 1; escalations 2026-10-17 14:33Z; L59) make real changes select all ~400 units.

**R2 and R3 are unchanged.** Nothing here is on the merge train's full live `tools/gate.py` or on the
nightlies. This batch adds one evidence script and its saved rows under `docs/test-architecture/manifest-ops/`.

## 1. Measurement

`measure.py` replays `tools/select_tests.py` (through `answer_cutoff.select`, the entry the gate's selection
and `--run` use) on:

- all **54 first-parent merges of main** since 2026-10-14 00:00Z, from `dccd9cf5a` to `de9cfa84f`
  (this branch's base), each against its first parent;
- the **10 real changes** of the cutoff report's shadow table (`../cutoff/changes.json`), each with the map
  that table pinned (by SHA-256) and its drift check.

The selector is main's at `de9cfa84f`, run in private caches: no shared map, and no Lean build record, so
no binary cutoff. The merges use one map, the cutoff batch's recording of main `dae12d5ff`
(`../cutoff/evidence/recording-map.json.gz`, all 434 units, Mac seconds per unit). They are replayed in two
ways:

- `before`: the map is taken as recorded at each parent (`--assume-fresh`), the "map after every merge"
  of rank 4.
- `before-drift`: the selector's own drift check runs against the map's commit. This is the plan a real
  `--run` makes when that map is the nearest one. Its uncertain units are answered by the static graph, and
  a manifest edit adds all of them ("unmapped manifest reader").

A plan "selects everything" when it selects all 434 units, whether or not it has a full-suite reason.
A plan selects everything **because of** the manifest or the pins under two conditions. Either its
full-suite reasons hold "ve/assurance-manifest.json: no safe operation map". Or the units that still have a
reason after the manifest's reasons (`is_manifest`), the pins' reasons (`is_pin`: "reads", "names" or
"lists the directory of" `lean/checkers.lock`) or both are dropped are fewer than all 434.
`python3 docs/test-architecture/manifest-ops/measure.py --check` recomputes every saved row in a worktree
of the saved commit. It also fails when the tables below are not what `--table` prints from the saved rows
(D4: batch evidence, not a permanent test).

<!-- measure.py --table: begin -->
**before, merges**

| Merge | Subject | Paths | Units | Full-suite reasons | Top reasons (units) | Without manifest / pins / both | Because of |
|---|---|---:|---:|---|---|---|---|
| `4667e8de6` | lean-first/b14d | 60 | 434 | (none) | reads ve/backends/lean_service_schema/envelope.json (393); ve/backends/service_schema.py: new Compiler._x_reading_plan not called by name (393); reads lean/checkers.lock (293) | 434 / 434 / 434 | neither |
| `b98d87947` | question-answering/q2 | 151 | 434 | (none) | reads ve/backends/lean_service_schema/envelope.json (393); reads lean/checkers.lock (293); ve/backends/service_schema.py:_Rows.__getitem__ reads a changed name (290) | 434 / 434 / 434 | neither |
| `1cbd5ed1e` | infra/tarch-b1 | 17 | 434 | pyproject.toml; tests/conftest.py | reads tests/heavy.json (393); runs git, which reads .gitattributes (74); names tests/heavy.json (static) (44) | 434 / 434 / 434 | neither |
| `16a02693a` | lean-first/b14a | 52 | 434 | (none) | ve/backends/service_schema.py: new Compiler._x_source_span not called by name (393); reads lean/checkers.lock (293); ve/backends/service_schema.py:Compiler._compile reads a changed name (292) | 434 / 434 / 434 | neither |
| `91858c032` | infra/test-tail | 24 | 434 | tests/conftest.py | imports tools/test_schedule.py (static) (434); tools/test_schedule.py: import-time change (394); names tools/test-durations.json (static) (44) | 434 / 434 / 434 | neither |
| `8cbb3049f` | lean-first/b14c | 69 | 434 | (none) | ve/backends/service_schema.py: new Compiler._x_equal_fields not called by name (393); ve/backends/service_schema.py: new Compiler._x_same_length not called by name (393); reads ve/backends/lean_service_schema/common.json (294) | 434 / 434 / 434 | neither |
| `3160fb800` | infra/premise-scale | 102 | 434 | (none) | imports ve/backends/process_limits.py (static) (434); reads ve/backends/lean_service_schema/envelope.json (393); ve/backends/service_schema.py: new Compiler._x_unique_strings not called by name (393) | 434 / 434 / 434 | neither |
| `bf6c03baf` | infra/tarch-contract | 17 | 434 | .gitignore | runs git, which reads .gitattributes (74); imports tools/platform_contract.py (static) (45); runs git, which reads .gitattributes (static) (44) | 135 / 135 / 135 | neither |
| `8bc65a907` | lean-first/b16e | 43 | 434 | (none) | ve/backends/service_schema.py: new _LazyRef.__getitem__ not called by name (393); ve/backends/service_schema.py: new _LazyRef.__init__ not called by name (393); reads lean/checkers.lock (293) | 434 / 434 / 434 | neither |
| `f3046f7dc` | infra/tarch-store | 34 | 434 | tests/conftest.py | ve/backends/lean_service.py:LeanService.exchange (289); ve/backends/lean_service.py:LeanService.exchange reads a changed name (289); ve/backends/lean_service.py:LeanService._roundtrip (288) | 346 / 346 / 346 | neither |

10 of 54 plans select every unit (434); 0 of them because of the manifest or the pins.

**before, shadow**

| Change | Subject | Paths | Units | Full-suite reasons | Top reasons (units) | Without manifest / pins / both | Because of |
|---|---|---:|---:|---|---|---|---|
| `lf-14a` | lf-14a | 52 | 434 | (none) | imports ve/backends/service_schema.py (static) (434); imports ve/parser.py (static) (434); imports ve/printer.py (static) (434) | 434 / 434 / 434 | neither |
| `lf-14c` | lf-14c | 69 | 434 | (none) | ve/backends/service_schema.py: new Compiler._x_equal_fields not called by name (393); ve/backends/service_schema.py: new Compiler._x_same_length not called by name (393); reads ve/backends/lean_service_schema/common.json (293) | 434 / 434 / 434 | neither |
| `lf-16e` | lf-16e | 42 | 434 | (none) | ve/backends/service_schema.py: new _LazyRef.__getitem__ not called by name (393); ve/backends/service_schema.py: new _LazyRef.__init__ not called by name (393); reads lean/checkers.lock (292) | 434 / 434 / 434 | neither |
| `premise-scale` | premise-scale | 102 | 434 | (none) | imports ve/backends/process_limits.py (static) (434); reads ve/backends/lean_service_schema/envelope.json (393); ve/backends/service_schema.py: new Compiler._x_unique_strings not called by name (393) | 434 / 434 / 434 | neither |
| `qa-q2` | qa-q2 | 151 | 434 | (none) | reads ve/backends/lean_service_schema/envelope.json (374); reads lean/checkers.lock (284); ve/backends/lean_service.py:LeanService.exchange reads a changed name (281) | 434 / 434 / 434 | neither |

5 of 10 plans select every unit (434); 0 of them because of the manifest or the pins.

**before-drift, merges**

| Merge | Subject | Paths | Units | Full-suite reasons | Top reasons (units) | Without manifest / pins / both | Because of |
|---|---|---:|---:|---|---|---|---|
| `dccd9cf5a` | infra/runner-portability | 10 | 434 | (none) | imports tests/subprocesses.py (static) (434); imports ve/backends/lean_service.py (static) (434); imports ve/backends/rust_jsonl.py (static) (434) | 434 / 434 / 434 | neither |
| `4667e8de6` | lean-first/b14d | 60 | 434 | (none) | imports ve/backends/lean_service.py (static) (434); imports ve/backends/service_schema.py (static) (434); names lean/checkers.lock (static) (434) | 434 / 434 / 434 | neither |
| `4ce477e18` | infra/ts-B2 | 28 | 434 | (none) | imports ve/backends/lean_service.py (static) (434); names docs/test-speed-b2/evidence/summary.json (static) (434); runs git, which reads .gitattributes (static) (434) | 434 / 434 / 434 | neither |
| `b96f04a5a` | lean-first/b14b | 62 | 434 | (none) | imports ve/norms.py (static) (434); names lean/checkers.lock (static) (434); names ve/backends/lean_service_schema/family-norms.json (static) (434) | 434 / 434 / 434 | neither |
| `b98d87947` | question-answering/q2 | 151 | 434 | (none) | imports ve/backends/lean_service.py (static) (434); imports ve/backends/relay.py (static) (434); imports ve/backends/service_schema.py (static) (434) | 434 / 434 / 434 | neither |
| `1cbd5ed1e` | infra/tarch-b1 | 17 | 434 | pyproject.toml; tests/conftest.py | names tests/heavy.json (static) (434); runs git, which reads .gitattributes (static) (434); reads tests/heavy.json (393) | 434 / 434 / 434 | neither |
| `16a02693a` | lean-first/b14a | 52 | 434 | (none) | imports ve/backends/service_schema.py (static) (434); imports ve/parser.py (static) (434); imports ve/printer.py (static) (434) | 434 / 434 / 434 | neither |
| `c4fdd804a` | infra/arch-AR-2 | 26 | 434 | (none) | names ve/question/LOCK.json (static) (434); names docs/arch/AR-2/evidence/mutants.json (static) (168); names docs/arch/AR-2/evidence/checks.json (static) (165) | 434 / 434 / 434 | neither |
| `91858c032` | infra/test-tail | 24 | 434 | tests/conftest.py | imports tools/test_schedule.py (static) (434); names tools/test-durations.json (static) (434); tools/test_schedule.py: import-time change (394) | 434 / 434 / 434 | neither |
| `8cbb3049f` | lean-first/b14c | 69 | 434 | (none) | ve/backends/service_schema.py: new Compiler._x_equal_fields not called by name (393); ve/backends/service_schema.py: new Compiler._x_same_length not called by name (393); reads ve/backends/lean_service_schema/common.json (294) | 434 / 434 / 434 | neither |
| `3160fb800` | infra/premise-scale | 102 | 434 | (none) | imports ve/backends/lean.py (static) (434); imports ve/backends/lean_service.py (static) (434); imports ve/backends/process_limits.py (static) (434) | 434 / 434 / 434 | neither |
| `c53117326` | fix/ci-run-timeout | 15 | 434 | (none) | imports tests/subprocesses.py (static) (434); names docs/fix-ci-run-timeout/evidence/ab-cpu-quota.json (static) (165); names docs/fix-ci-run-timeout/evidence/loaded-full-run-load.log (static) (165) | 434 / 434 / 434 | neither |
| `bf6c03baf` | infra/tarch-contract | 17 | 434 | .gitignore | runs git, which reads .gitattributes (static) (434); names docs/test-architecture/contract/evidence/commits.txt (static) (171); names docs/test-architecture/contract/evidence/contract-runs.json (static) (171) | 434 / 434 / 434 | neither |
| `99f67a7a9` | infra/tarch-split | 26 | 434 | (none) | imports tools/test_schedule.py (static) (434); names tools/test-durations.json (static) (434); names docs/test-architecture/tarch-split/evidence/mac-after-durations.txt (static) (165) | 434 / 434 / 434 | neither |
| `d7ea7228b` | rd-9/integrate | 104 | 434 | (none) | imports ve/admission.py (static) (434); imports ve/norm_defaults_route.py (static) (434); imports ve/soft_route.py (static) (434) | 434 / 434 / 434 | neither |
| `8bc65a907` | lean-first/b16e | 43 | 434 | (none) | imports ve/backends/service_schema.py (static) (434); imports ve/softnorms.py (static) (434); names lean/checkers.lock (static) (434) | 434 / 434 / 434 | neither |
| `f59dde41e` | fix/relay-mutation-gate | 10 | 434 | (none) | names ve/backends/lean_service_schema/norm-defaults.json (static) (434); runs Lean via lean/ResponseShape/Schemas/NormDefaults.lean (static) (401); names lean/declarations.txt (static) (127) | 434 / 434 / 434 | neither |
| `2578fd9ad` | infra/tarch-binding | 20 | 434 | (none) | runs git, which reads .gitattributes (static) (434); names tests/data/binding-answers.jsonl.gz (static) (127); names docs/test-architecture/tarch-binding/mutants.json (static) (112) | 434 / 434 / 434 | neither |
| `5759be852` | infra/tarch-cutoff | 28 | 434 | (none) | names docs/test-architecture/cutoff/evidence/summary.json (static) (434); names docs/test-architecture/cutoff/evidence/mutants.json (static) (168); names docs/test-architecture/cutoff/evidence/seeds.json (static) (166) | 434 / 434 / 434 | neither |
| `f3046f7dc` | infra/tarch-store | 34 | 434 | tests/conftest.py | imports ve/backends/lean_service.py (static) (434); ve/backends/lean_service.py:LeanService.exchange (289); ve/backends/lean_service.py:LeanService.exchange reads a changed name (289) | 434 / 434 / 434 | neither |
| `85b20fcba` | infra/rights-licence-relay | 32 | 434 | (none) | names lean/checkers.lock (static) (434); names ve/backends/lean_service_schema/rights.json (static) (434); runs Lean via lean/ResponseShape/Audit.lean (static) (402) | 434 / 434 / 434 | neither |
| `f811fa69c` | fix/jt-crossplan | 61 | 434 | (none) | imports ve/english.py (static) (434); imports ve/printer.py (static) (434); names lean/checkers.lock (static) (434) | 434 / 434 / 434 | neither |
| `8a5b701b4` | infra/tarch-slowtail | 20 | 434 | (none) | imports tools/test_schedule.py (static) (434); names tools/test-durations.json (static) (434); names docs/test-architecture/slowtail/evidence/after-branch-d159baf4.log.gz (static) (165) | 434 / 434 / 434 | neither |
| `de309d61c` | infra/fu-rd9-checks | 13 | 434 | (none) | names ve/backends/lean_service_schema/rights.json (static) (434); runs Lean via lean/ResponseShape/Schemas/Rights.lean (static) (401); imports ve/rights_route.py (static) (214) | 434 / 434 / 434 | neither |
| `b5248038e` | infra/fu-lf14c-f4 | 20 | 434 | (none) | names lean/checkers.lock (static) (434); names ve/backends/lean_service_schema/family-norms.json (static) (434); unmapped manifest reader (434) | 434 / 434 / 434 | neither |
| `109c7de1d` | lean-first/b16f | 59 | 434 | (none) | names lean/checkers.lock (static) (434); names ve/backends/lean_service_schema/document.json (static) (434); unmapped manifest reader (434) | 434 / 434 / 434 | neither |
| `a4676c0b7` | infra/fu-docs-1017 | 11 | 434 | (none) | unmapped manifest reader (434); runs Lean via lean/VE/Core/Layers.lean (static) (401); runs Lean via lean/VE/Norms/Family.lean (static) (401) | 415 / 434 / 415 | manifest readers (19) |
| `c4d7ea565` | readings-defaults/rd7 | 60 | 434 | (none) | names lean/checkers.lock (static) (434); names ve/backends/lean_service_schema/readings-route.json (static) (434); unmapped manifest reader (434) | 434 / 434 / 434 | neither |
| `05b85b631` | infra/me-1a | 29 | 434 | (none) | imports ve/english.py (static) (434); names ve/numbers_phrases.json (static) (434); runs git, which reads .gitattributes (static) (434) | 434 / 434 / 434 | neither |
| `e7f6968d4` | infra/ties-fu-1017 | 14 | 434 | (none) | unmapped manifest reader (434); runs Lean via lean/ResponseShape/Audit.lean (static) (401); runs Lean via lean/ResponseShape/Encoders/Rights.lean (static) (401) | 411 / 434 / 411 | manifest readers (23) |
| `de9cfa84f` | infra/tarch-histdep | 18 | 434 | (none) | runs git, which reads .gitattributes (static) (434); names docs/test-architecture/histdep/DELTA.md (static) (119); names docs/test-architecture/histdep/mutants.json (static) (112) | 434 / 434 / 434 | neither |

31 of 54 plans select every unit (434); 2 of them because of the manifest or the pins.

Averages (minutes: the recorded Mac seconds of the selected units, summed, / 60):

| Changes | Rule | before: units / minutes / full | before-drift: units / minutes / full |
|---|---|---|---|
| merges (54) | plan | 201.9 / 68.1 / 4 | 330.4 / 105.1 / 4 |
| merges (54) | r1 | 201.9 / 68.1 / 4 | 330.4 / 105.1 / 4 |
| shadow (10) | plan | 343.4 / 114.2 / 0 | 343.4 / 114.2 / 0 |
| shadow (10) | r1 | 343.4 / 114.2 / 0 | 343.4 / 114.2 / 0 |

Upper bound of any narrowing of the manifest and pin rules: the units only their reasons select (plans without a full-suite reason), as if every one were dropped:

| Label | Changes | Manifest only | Pins only | Either | Plans with any | Per plan |
|---|---|---:|---:|---:|---:|---:|
| before | merges (54) | 17 | 7 | 24 | 10 | 0.4 |
| before | shadow (10) | 3 | 2 | 5 | 3 | 0.5 |
| before-drift | merges (54) | 42 | 0 | 42 | 2 | 0.8 |
| before-drift | shadow (10) | 3 | 2 | 5 | 3 | 0.5 |
<!-- measure.py --table: end -->

What the tables show:

- **The manifest always has a safe operation map now.** 14 of the 54 merges edit
  `ve/assurance-manifest.json`. None of the 256 saved plans (64 changes x 2 rules x 2 labels) gives "no safe operation map":
  no merge added or removed the file, changed `version`, or broke the operation list. tarch-select's
  shared-field narrowing (`../select/REPORT.md` row "5.") already covers every manifest edit made since
  2026-10-14. Candidates (a) and (b) of the task (presence changes, IMPORT_FIELDS edits) occur in none of
  these 54 merges.
- **The pins decide no plan.** 13 merges edit `lean/checkers.lock`. Every one of them adds `ve_service`
  digests: 1 to 22 per merge, 2 merges also add `rust_jsonl` digests, and no merge only removes pins. A
  pin change is therefore a new service build, and every service user is selected through the Lean change
  anyway. This holds with or without the binary cutoff: a changed `ve_service` digest selects all its
  runners (`service_impact`). The pin readers (293 units) are almost all service users or readers of the
  schema files, so dropping every pin reason changes 7 units across all 54 merges.
- **The manifest decides 2 plans, and only under drift** (`a4676c0b7` fu-docs-1017, `e7f6968d4`
  ties-fu-1017). The deciding reason is "unmapped manifest reader": a manifest edit adds every unit the
  drift check made uncertain. Without it, those plans select 415 and 411 units. That is map staleness, not
  the operation map, and it is under the stop rule's threshold.
- **The whole suite comes from elsewhere.** Fresh map, 10 of 54 merges:
  - 4 have full-suite reasons: `tests/conftest.py` (3 merges), `pyproject.toml` and `.gitignore`.
  - 6 Lean-first and premise-scale merges reach 434 through `ve/backends/service_schema.py`. A new
    `Compiler._x_*` method "not called by name" selects the file's 393 runners, along with the readers of
    `lean_service_schema/envelope.json` and `common.json`.

  Drift check, 31 of 54: the static graph's answers for uncertain units ("imports ve/backends/lean_service.py
  (static)", "names lean/checkers.lock (static)", "runs git, which reads .gitattributes (static)") reach all
  434 on their own.

## 2. Selected units and minutes

Minutes are the recorded Mac seconds of the selected units, summed, over 60 (the `dae12d5ff` recording;
all 434 units are 132.3 min). The averages and the upper bound are in the generated block above.

| Changes | Plan | Before: units / min / plans with full-suite reasons | After |
|---|---|---|---|
| 54 merges, fresh map | `plan` and `r1` (equal: no build record) | 201.9 / 68.1 / 4 | not built (stop rule) |
| 54 merges, drift check | `plan` and `r1` | 330.4 / 105.1 / 4 | not built (stop rule) |
| 10 shadow changes | `plan` and `r1` | 343.4 / 114.2 / 0 | not built (stop rule) |

**Upper bound on any narrowing of the manifest and pins rules**, sound or not: drop every unit only their
reasons select. That saves 24 units in all over 54 merges with a fresh map (0.4 per merge), 42 under drift
(0.8 per merge, in 2 merges), and 5 over the 10 shadow changes (0.5 per change). So step 2 could not move
the averages by even one unit, and it was not built.

Limits of the measurement:

- No Lean build record exists for these merges, so the binary cutoff is off. It would narrow only the Lean
  runners that are not the service; a pin change always comes with a service rebuild, as shown above.
  `r1` (the `modes` rule) therefore equals `plan` in every row.
- The merges use one recorded map. Real runs use the nearest cached map, which lies somewhere between the
  two labels.

## Follow-ups (not built here)

1. **`service_schema.py` is the largest real cause.** A new or changed `Compiler._x_*` method selects
   every runner of the module (393 units). The compiler dispatches on schema keywords (`x-<keyword>` runs `_x_<keyword>`,
   `service_schema.py:189`), and a new method "not called by name" keeps the whole file. A sound narrowing would read which keywords the
   schemas under `ve/backends/lean_service_schema/` use: those files are in the recorded map's reads, and
   a new keyword that no schema names selects only the compiler's own tests. This needs its own measurement
   and its own mutants.
2. **Map staleness under drift** (31 of 54 full). The static graph answers for every uncertain unit, and
   one coarse mention reaches all 434. Recording `tools/test_map.py update` after each merge
   (`../select/REPORT.md` item 1) attacks this directly. Narrowing "unmapped manifest reader" to the
   uncertain units whose static closure holds `ve/assurance.py` is sound but worth 2 merges.
3. **`tests/conftest.py` stays a full-suite reason** (3 merges). Its fixtures run in every unit, so this
   is correct as it stands.
4. Re-run the answer-level cutoff decision (#5) with the measurement above: the manifest and the pins are
   no longer the blocker named in the 14:33Z escalation.

## Orchestrator lines

None needed: nothing is installed or wired. For the record: `L59` ("a branch that touches the manifest
selects all ~400 units") describes the selector before tarch-select. On main `de9cfa84f` a manifest edit
selects its operation readers. With a stale map it also selects the uncertain units (2 of 54 merges decided
by that).

## Seeded bugs

Product code is unchanged: no Lean, Python product or Rust file is touched, so there is no product
behaviour to seed. The evidence script's three claims are each seeded in `measure.py`, shown to fail
`measure.py --check`, and restored:

| # | File | Seeded bug | Failing check |
|---|---|---|---|
| S1 | `docs/test-architecture/manifest-ops/measure.py` | `is_manifest` forgets "unmapped manifest reader" | `measure.py --check --only a4676c0b7,e7f6968d4` exits 1: "4 rows differ" (both labels; under drift `without_manifest` is 434, not 415/411) |
| S2 | `docs/test-architecture/manifest-ops/measure.py` | `is_pin` forgets "reads lean/checkers.lock" (the recorded pin readers) | `measure.py --check --only 109c7de1d` exits 1: "2 rows differ" (the fresh row's `pins_only` loses `tests/test_lean_first_oracle.py`) |
| S3 | `docs/test-architecture/manifest-ops/measure.py` | `because` counts a plan as caused when `without_manifest <= total` | `measure.py --check --only none` exits 1: "the tables between the markers are not what --table prints from the saved rows" |

## Self-review against BUILDER-CHECKLIST

See the build report's final section (the same items, one line each).
