# et-4b build report: the `events@0` row, the hook in the layered decoders, the replay

**Status:** done for this cut, ready for the gate. No DRI signature reserved (DELTA row 1 R16, row 2 SYNTHESIS 2.2 as
ap-1bd's row 2, row 3 R2). **HEAD:** the branch's last commit (the chain gates it).
**What changed:** `events@0` is a row of AR-10's table; `decodeSoftU`/`decodeRightsU` run `eventsHook` (the row, the
block with `LinkNotOpen` in spec order, the environment without the block) and put the pack last in `assemble`'s
list; `replayEventsEntailment` replays certificates over it with `events_wire_acceptance` (spec 6.3, word for word).
Review fix F1 (B): a soft list with the profile and no block replays its certificate as the list without it
(`replayUnblockedEntailment`, `unblocked_wire_acceptance`) instead of refusing it; see "Review fixes".
**Open items:** et-4c (below): `embeddable` and the fragment on situations, the 6.3 answer theorems, T3/T3b, the other
report fields, `origins`. Until then every answer about a situation on an events document is refused by name.
Size: about 1,490 hand-written lines against the ~600 rule (see Size). Pilot bytes 0.
**Trust mutants on the Lean as merged (et-4b-tm, 2026-11-09):** 471 mutants, 331 KILLED, 0 SURVIVOR, 0 UNKNOWN,
74 INVALID, 66 ALLOWED, exit 0 ([trust-mutants.json](trust-mutants.json), section "et-4b-tm" below).

Item: feature item et-4b (rank 132 of the feature feed, acting DRI dri-featurefeed, 2026-10-18). Branch
`feature/et-4b` from main `fe252f79a`. Plan and spec are on main; nothing was copied.

## Statement gate and synthesis edits

- The plan's statement review accepted ET-4's section (et-4 built on it, `docs/events-time-causation/et-4/REPORT.md`
  "Statement gate"). No reviewed statement is false as written; none changed.
- **Exact:** `events_wire_acceptance` (spec 6.3 lines 1108-1112, the `.map` form; the plan's line 659 is the older
  form without `.map`, and the spec's is the one `decodeEvents : … Option EventsDecoded` types). `EventsEntailmentReplay`
  has the spec's seven fields and nothing else.
- **Synthesis round 2** (`debates/plan-synthesis-2/edits-events-time-causation.md`): this item implements **edit 2**
  (the row with slot `pack` and interface `.pack "events"`, `Compose/Dispatch.lean` `packRows`) and keeps **edit 1** as
  et-4 chose it (`.constraint`, `decls := []`, the dates declared in the regenerated environment, the RF-5 pattern);
  edit 7 (the prefix row) is et-4's. Edits 3-6 and 8 are other items'.

## Plan rows and directive lines

| Row | Delivered | Where |
|---|---|---|
| (1) the route hook in `decodeSoftU`/`decodeRightsU`: the environment without the block | yes: `routeView` drops the key and `events@0`; the route decodes it (`hookView`) | `Events/Wire.lean`, `NormDefaults/Layered.lean` |
| (1) the date constants in its regenerated vocabulary JSON | yes: one `date__…` constant of the day sort per date, the anchor's worded "the date of this document" (1.3); in `base_environment` | `routeView`; `WireExamples` view guards; `test_the_pack_is_last…` |
| (1) identity over the original bytes | yes: `environment_id`, `document_hash` and certificate bindings read the environment as written | `RouteExamples` identity guards; stale-certificate tests |
| (1) the pack in the `assemble` list | yes: `[softPack] ++ hookPacks H`, `[softPack, rightsPack] ++ hookPacks H`; the date constants charged to the vocabulary limit (review F4) | `hooked_X`, `decodeRightsU_packs`; the 245/246, 247/248, 248/249 boundaries |
| (1) `LinkNotOpen` over the document's open terms, before the dates (spec 4 item 5, review F4) | yes: `decodeEventsWith (checkOpen …)` between items 5 and 6; the terms are the case's `open_terms` or its document's (`caseOpenTerms`); `decodeEventsWith_ok` | `WireExamples` LinkNotOpen guards |
| (1) spec 4 item 1, the row before any events check | yes: `eventsHook` runs `gateOf profileTable` first | `WireExamples` row guards |
| (2) `replayEventsEntailment` with `events_wire_acceptance` | yes, exact text; mode `norm-defaults-certificate` (soft branch), dispatched by `Run.runCaseE` | `Events/Chain.lean` |
| (2) a mode that produces a certificate for an accepting fixture | the untrusted prover `ve.entailment.prove_entailment` (`tests/test_events_route.py`), and a one-node `close` proof of a pack premise bound by Lean's own identities (`RouteExamples`) | both accept (`valid: true`) and refuse (stale, rebound, other block) |
| (3) `embeddable` and the fragment on every reported situation; `events_countermodel_calendar`; T3, T3b through the service | **→ et-4c** (size). Meanwhile `pendingEvents` refuses every situation kind by name, so no uncalendared situation is reported | `RouteExamples` kind guards |
| (4) report fields with shapes and encoder theorems | in part: `events_premises` (the pack's labelled rows, typed `labelled_list`, `runCaseE_fits`/`layeredCase_fits`), needed for the accepting fixture; `named_dates`, `causal_links`, `calendar_days`, `origins` **→ et-4c** | `Packs.eventsArray`, `ResponseShape` |
| (4) the `events@0` row with `events_row_composition` | yes (SYNTHESIS 2.2's profile-gate row): `gate_events` (the gate half) and `events_row_composition` (refused with its text before any events check; admitted as the list without it; the pack last in `X` on both branches) | `Compose/Dispatch.lean`, `Events/Chain.lean` |
| every value evaluated once, size charged, a growing chain | yes: `labelled` evaluated once in `finishEvents` and carried (`labelled_eq`); roles and links charged against `maxPredicates` before they are read against each other, the pack against `maxNodes` once; `repeatOf` one pass; chains of 1, 10, 62, 63, 64, 2,000 dates and 20,000-entry lists | `WireExamples` |
| both sides of each new check, at and around each boundary | yes; the tool's survivors each got a fixture (Trust, mutants) | `WireExamples`, `RouteExamples` |

## Deviations (definitions only)

- `EventsDecoded` gains `labelled` with `labelled_eq` (evaluated once); `eventsPack` reads it. `decodeEvents` is
  `decodeEventsWith (fun _ => pure ())`, its body split into `decodeThroughLinks` and `finishEvents` (same order).
- New refusal `ResourceLimit: events premises` (common rules: a stated limit before any quadratic step). DELTA row 3.
- `decodeSoftU`/`decodeRightsU` take `(H : Option EventsHook := none)`; `decodeSoftU_source` and `decodeRightsU_soften`
  are generalised over `H` (premise-packs.md's hunk table describes the first; at `H = none` it is the old statement by
  definition). `layered_wire_acceptance` is unchanged; its replay is `replayLayeredOn` after `decodeSoftU`.
- `base_environment.constants` in the shape equals the request's except on an events case (`request_block/events`),
  where each row is typed; et-5's relay binds the dates.
- Not reached by the hook yet, refused by name: the plain norm-defaults branch, the readings wrapper, admission,
  `defaults-*`, every situation kind; a rights document's certificate kind (the rights branch has none today).

## Review fixes

The review of `194539566` (`manage-agents/et-4b-review.final.md`) had one B finding and five C findings.

- **F1 (B):** a soft document listing `events@0` without the block had its `norm-defaults-certificate` refused with
  `InvalidInput: events`, though spec 1.11 gives it no pack and 1.1 says the profile neither widens nor narrows the
  route. The class is "a kind the list without the profile answers that the list with it and no block refuses".
  - Fix: `VE/Events/Chain.lean` `replayUnblockedEntailment` decodes through the hook's view (`decodeSoftU … H`) and
    replays by `replayLayeredOn`. Its well-formedness is proved (`unhooked_X`, `unhooked_X_wellFormed`), and
    `unblocked_wire_acceptance` ties it: `X` is soft's premises, and a valid replay is `EntailsX`. `runCaseE` takes it
    when `hookBlock` is `none`. The docstring that named `replayLayeredEntailment` now names it. The answer shape is
    one builder, `Admission.certificateAnswer`, for `softCase` and both events branches. Theorem statements
    `events_wire_acceptance` and `EventsEntailmentReplay` are unchanged.
  - Regression: the probe is a `#guard`. `RouteExamples.lean` sweeps every kind (`legacyKinds` with the certificate,
    gaps, admission and `defaults-conflict`) on both branches: a kind `eventsServed` answers has the same status as
    on the list without `events@0`, and every other kind is refused by name. The replay is valid on `⊤` and not
    on `⊥`, and gives the same answer as on the plain list. Each list's certificate is stale on the other list,
    `X` is soft's two premises, and with a block the function refuses. `tests/test_events_route.py::
    test_a_certificate_listing_the_profile_without_the_block_replays_as_the_list_without_it` replays a prover
    certificate through the service and checks it with `check_row`.
  - DELTA row 2 now names the no-block answer, and row 1 the re-measured trust.
- **F2 to F6 (C):** not changed here. F2 and F4 (with F3's binding) are the review's follow-ups et-4b-c1 and
  et-4b-c2; F5 is the size note below; F6 (`gate_events` in `Dispatch.lean`) is left as built.

## Seeded bugs and mutants

Every seeded bug is in [mutants.json](mutants.json) (92 records, with `file` and `test`); the tool's mutants of
every other new trusted definition are [trust-mutants.json](trust-mutants.json).

- **Lean, `lean/VE/Events/Wire.lean`:** `tests/test_events_wire_mutants.py` elaborates `Wire.lean` with
  `WireExamples.lean` once per mutant. Its `HOOK` table plants 19 by hand, one per claimed behaviour of the hook,
  each failing a `#guard`:
  - the row skipped (`hook-no-row`) or read on every list (`hook-no-profile-test`);
  - `LinkNotOpen` dropped, its decider ignored, its first link only, an open term read by name only, or run after
    the dates (`hook-dates-before-open`);
  - the view keeping the block or the profile, losing the dates or the author's constants, or giving the anchor its
    ISO wording;
  - the charge counting states once, links not at all, or one too many;
  - the pack's sum off by one or read on its first premise;
  - `repeatOf` forgetting its seed or reporting the last repeat.

  The generator adds 68 more mutants from the source as written (every check step dropped, every independent pair
  swapped, every role list read for its sibling); with the review's 7 and the old equivalents, 98 tests. Mac runner,
  1c24fb3e: 96 passed and 2 failed (one killed by a stack crash, one by a proof). Both got a guard that kills them, and
  the rerun of those ids passed (3 passed). `drop-decodeEvents-15` (et-4's equivalent node limit) is no longer
  equivalent: the pack's total is reachable (`weaker 60`), so it is killed. et-4b-tm adds the `ORDER` table's two
  (`order-links-before-roles`, `order-dates-before-links`), which replace base `swap-decodeEvents-11`/`-12`; see
  "et-4b-tm".
- **Lean, `lean/VE/NormDefaults/Packs.lean`:** `eventsArray-reads-soft` and `eventsArray-key` in
  `tests/test_packs_guard_mutants.py`, each failing a `PacksExamples.lean` guard (46 passed, VM).
- **Lean, the route's files** (`Layered.lean`, `LayeredAdmission.lean`, `Run.lean`, `Compose/Dispatch.lean`,
  `Events/Chain.lean`, `Packs.lean`, the shapes): `tools/trust_mutants.py` with `--test WireExamples.lean --test
  RouteExamples.lean` (full Mac run at 28d5911b6, then an allow-only rescore at 01d9048b (385 verdicts reused, identical inputs): 454 mutants over 20 definitions, 316 KILLED, 0 SURVIVOR, 0 UNKNOWN, 54 INVALID, 84 ALLOWED, exit 0. The 84 allowed were under [trust-mutants-allow.json](trust-mutants-allow.json) (54 lines then, 44 now), one line per definition and operator: equivalent ones (a list of at most one element, a list only `isEmpty` reads, the key the next line sets again), texts Lean refuses, and mutants a broken proof or more than 100 failing guards stop. Each line names the same-operator mutants that are killed. The first runs (VM, ac7dfa4a3) left 44 survivors; each one got a fixture in `RouteExamples.lean` (the rights branch, an accepting replay, two decisions, two soft premises, two events and states, the view's profiles and constants)).
  That record was the run on 01d9048bc, before review F1's change; the run on the Lean as merged is et-4b-tm's
  (lp0401 Q3) and replaces it: 471 mutants, 331 KILLED, 0 SURVIVOR, 0 UNKNOWN, 74 INVALID, 66 ALLOWED, exit 0 (see
  "et-4b-tm"). The targeted run at 6ece79038 (reviews/tm-targeted/et-4b-et-4b-c050416.json in the orchestration
  repository) stood in until then; its 13 NOT RUN, cut to et-4b-tm (reviews/dri-decisions-20261105-et-4b-tm.md), are
  all KILLED in it.
- **Lean, F1:** `f1-unblocked-certificate-refused` (`runCaseE` refuses after the replay) fails the guards at
  `RouteExamples.lean:333` and `:336`. `f1-unblocked-reads-the-raw-environment` (`replayUnblockedEntailment`
  decodes without the hook's view) breaks the proof of `unblocked_wire_acceptance`; with that proof stubbed, it fails
  the guards at `:326` (the kind sweep) and `:332` to `:342`. Both are in `mutants.json`.
- **Python, `tools/layer_policy.py`:** dropping `VE.Events.RouteExamples` from the runner fixtures makes
  `python3 tools/check_lean_imports.py` print `new outward Lean import: VE.Events.RouteExamples -> VE.NormDefaults.Run`.
  The check runs in the gate and in `tests/test_precommit_hook.py`. No `ve/` or `rust/` product code changed (only
  generated data).

## et-4b-tm: the trust-mutant record on the Lean as merged (2026-11-09)

Item et-4b-tm (reviews/dri-decisions-20261105-lp0401-apply.md item 1, lp0401 Q3), branch `feature/et-4b-tm` from main
`268829b1a`. No definition, statement, verdict or Lean file changed; no DELTA row; no trust growth; no signature reserved.

- **Command** (`mac-pytest.sh --trustmut`, ve-mac-1, 6 jobs, 6,375 s, record head `6be3f873f`):
  `--base 1a39ebef39c0 --only @docs/events-time-causation/et-4b/trust-mutants-only.txt --max-mutants 1000 --test
  lean/VE/Events/WireExamples.lean --test lean/VE/Events/RouteExamples.lean --allow …/trust-mutants-allow.json
  --rescore …/trust-mutants.json --json …/trust-mutants.json`. Output: `331 KILLED, 0 SURVIVOR, 0 UNKNOWN, 74 INVALID,
  66 ALLOWED, 0 NOT RUN in 6375 s`; by class D[V] 158/60/48, G[V] 162/11/16, S 11/3/2 (KILLED/INVALID/ALLOWED); exit 0.
- **Why `--base` and `--only`:** the task's command has neither. Its default base (the merge base with main) holds
  none of et-4b's lines on this branch, so it plans nothing. `1a39ebef3` (main just before the et-4b merge `5fc9d8c7f`)
  plans 1,009 mutants over 55 definitions, 32 of them other items' merged since (Purposes, Route/Inert, Closure, …).
  `trust-mutants-only.txt` keeps the plan's mutants of et-4b's 23 definitions (the rebased record's,
  reviews/tm-targeted/et-4b-rebase-20261108.json at a97072e60). Checked before the run: `trust_mutants.py --plan` with
  the same options printed `definitions 23, mutants 471, to_run 471, not_run 0`; the 471 equal that record's 471 as
  (definition, operator, before, after) multisets (0 missing, 0 extra). The ids are plan positions over `1a39ebef3`
  and this tree: after a change to lean/, recompute them before a rerun.
- **`--rescore`/`--resume`:** the tool printed `a full run, since its inputs differ (tool)`. The committed record
  (454 mutants over 20 definitions, base fe252f79a) is another plan; no partial record exists to resume.
- **Against the rebased record** (same 471): 19+1 raw UNKNOWN are now INVALID (the tool now classes those refused
  texts itself); the 5 `requestOf` SURVIVORs (M039/M143/M164/M308/M329 there) are KILLED (`M121`, `M370`, `M413`,
  `M687`, `M730` here, at the guards `RouteExamples.lean:383` to `:385` the tmbarrier ruling added); every other raw
  verdict is the same. The 15 raw SURVIVORs and 51 raw UNKNOWNs left are allowed by lines et-4b's review already
  read, each a raw SURVIVOR or UNKNOWN there. Deliverables (2) and (3) therefore needed no guard and no allow line.
- **Allow file:** 54 to 44 lines. The 10 removed match no mutant of this record, each now INVALID or KILLED:
  `openTermsOf` list-first/-last/-drop-first/-drop-last, `softCase` list-empty (the DRI's M034 line,
  dri-decisions-20261105-et-4b-tm.md item 1: the tool now gives that text INVALID), `runCaseE` list-empty,
  `usesNormDefaultsPath` body-true/body-false/list-empty, `decodeRightsU` list-empty. The allow file is no verdict
  input (`inputs` has none). A probe checked that the statuses equal the raw ones with the pruned file applied
  (`status consistent with pruned allow: True`).
- **The 13 ids cut to this item** (c050416 numbering → this record, all KILLED, `killed_at` in RouteExamples.lean):
  M300 → M669 (:337), M320 → M711 (:337), M302 → M671 (:262), M322 → M713 (:262), M319 → M710 (:262),
  M344 → M762 (:263), M361 → M796 (:263), M402 → M883 (:263), M411 → M898 (:263), M378 → M834 (:305),
  M391 → M858 (:305), M419 → M915 (:334), M425 → M926 (:334). No SURVIVOR among them, so the ruling's condition holds.
- **Order mutants** (reviews/dri-decisions-20261108-et-4b-gate.md item 3), `ORDER` in
  `tests/test_events_wire_mutants.py`, on `decodeThroughLinks`:
  - `order-links-before-roles` (checkLinks before checkRoles) fails the item-4 sort-fault guards of
    `WireExamples.lean` (:128, :129, :132, :152, :153, :169, :176, :178). Each has two faults: the base block's link
    `contributed_to` reads `act` and `stay`, which a role fault leaves without a role sort.
  - `order-dates-before-links` (`checkDates` inside `decodeThroughLinks`, before its `checkLinks`, as
    `hook-dates-before-open` inserts the later step before the earlier one) fails "Item 5 before item 6" (:232) and
    `LinkNotOpen` on `badDate` (:352).
  - The two-fault fixtures existed, so no fixture was added. Both test ids pass (4 passed with the unmutated and
    coverage tests, local).
- **Required test** (reviews/dri-decisions-20261108-adv1416.md item 4): `RouteExamples.lean:390` to `:426`, added
  on main by pk-1-conditions-b under the same ruling. It covers events@0 not owned (:416), the owned `Env` built
  explicitly (`ownedEnv`), `layeredOf` refusing, never `.ok` (:420), `requestOf` null (:421), today's text (:423),
  and the control (:425, :426). `check` binds `layeredOf` with `←` (`Service/Document.lean:2440`), so the error is the
  document's refusal and the silent path is not reachable. The text `object expected` does not name events@0. The DRI
  accepted that (dri-decisions-20261109-pk-1-conditions-b.md item 1), and naming it is the signed follow-up
  events0-owned-named-refusal. No new finding. It stays selected: `lean/VE.lean` imports it, and `lake build VE` runs
  in the `lake` fixture of `tests/test_events_wire_mutants.py` and in the gate.
- **Seeded bugs** (each restored; the first two are in `mutants.json`):
  1. All 8 guards that kill `order-links-before-roles` commented out:
     `test_every_mutant_fails_a_fixture[order-links-before-roles]` FAILED, "survives every #guard".
  2. :232 and :352 commented out: `[order-dates-before-links]` FAILED the same way (both runs:
     `2 failed, 98 deselected`).
  3. Lean, `Service/Document.lean` `requestOf`: the events@0 test emptied (`([] : List String).contains`, the silent
     path; trust mutant M121's text), with DocumentChain's proofs stubbed. `lake build VE.Events.RouteExamples`
     failed only at `#guard`s :383, :384, :385, :420, :421 and :423.
- **Merge barrier:** `tm-barrier.py` reads `docs/*/et-4b-tm/` and `reviews/tm-targeted/et-4b-tm-*`. This record is in
  `docs/events-time-causation/et-4b/` (the task's file list), so the barrier finds no record for et-4b-tm and the review
  judges this one by hand.

## Trust, size, tests

- **Trust:** `uv run python tools/trust_map.py --check` against `fe252f79a` gives K +0, S +0, V +129, unclassified 0,
  PASS, with two R16 allowances in `docs/trust-baseline.json` (+123, and +6 for F1's `Run.lean` lines). Per file:
  `Events/Wire.lean` +56, `Run.lean` +19, `Layered.lean` +18, `Compose/Dispatch.lean` +14, `Events/Chain.lean` +10, `Packs.lean` +7, shapes +5. The ties row is
  `manage-agents/FOLLOW-UPS.md` "## et-4b". New fixtures are T, `checkOpen` and the kind gate are reject-only.
- **Size (over the rule):** `git diff --numstat fe252f79a` gives about 1,490 hand-written lines, without generated
  files, tool-written evidence and `mutants.json` (2,259 with them), against ~600:
  - product Lean, about 520: `Wire.lean` 126, `Chain.lean` 138, `Dispatch.lean` 84, `Layered.lean` 32,
    `LayeredAdmission.lean` 41, `Run.lean` 36, shapes and encoders about 35;
  - fixtures and tests, about 645: `RouteExamples.lean` 323, `WireExamples.lean` 122, `test_events_route.py` 164,
    the two mutant tests 38;
  - inventories, about 250: `trust-classes.json`, the manifest's pins, the Compose and profile-table guards;
  - docs, about 130.

  The product code was cut at (2). The excess is mostly the both-sides fixtures that the tool's survivors asked for
  (about 180 lines of `RouteExamples.lean`, added after the first trust run).
- **Tests:** the selected set ran once on the finished route, on the tree of ac7dfa4a3 plus the report (run
  et-4b-2eb17c0c-t676215, Claude cloud, 6 shards, 545 units).
  - Every unit passed but `tests/test_packs_guard_mutants.py::test_every_trusted_definition_has_a_mutant`. It was
    fixed in 6ede4003b (`eventsArray`'s two mutants), and that file then passed whole (46 passed, VM).
  - The first selection's failures were the new import edge (`check_lean_imports`, and `test_precommit_hook` through
    it), `test_assurance_manifest` ×4, `test_profile_table` and `test_route_row_schemas` ×2. All were inventory lines
    and fixed before that run; those files passed (189 passed, local).
  - Fixtures added afterwards for the tool's survivors: built by `lake build` in the regeneration at 28d5911b6, and
    `tests/test_events_wire_mutants.py` with `tests/test_events_route.py` on the Mac (112 passed, 28d5911b).
  - `trust_map.py --check` PASS. No `main-known-red.txt` test failed. Not run: the full gate (the chain's).
  - After F1, at abd1b9e8: the selected set on the Mac (`mac-pytest.sh --select`, 530 units, exit 0, 0 failed),
    `lake build`, `python3 lean/audit.py` PASS, `regen_generated.py --check` 35 entries, and
    `tests/test_events_route.py` (15 passed, local).
- **Pilot bytes:** 0. Python has no model of `events@0`, so no document, English line or pilot output moves.
  ET-6's estimate (UDHR +201 to 548 B) waits for et-4c and et-5. Nothing is claimed before a pilot audit.

## Next items

- **et-4c:** (3) `embeddable` and the completion fragment on every reported situation (`NotCalendar` UNKNOWN,
  `modelSafe`/`witnessSafe`/`settledSafe`/`undecidedSafe`), `fillPremises_canonical_completion`,
  `events_countermodel_calendar` and the 6.3 answer theorems, T3 and T3b through the service, the situation budget for
  the pack's premises; then the report fields `named_dates`, `causal_links`, `calendar_days` and `origins`, and the
  hook on the plain branch, admission and the readings wrapper. Then lift `pendingEvents` kind by kind.
- **et-5** reads `events_premises` now and the et-4c fields after it; ET-6 waits for both.

Acceptance items: all AGENT; none HUMAN or EXTERNAL.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: PASS. The one new field, `events_premises`, is the typed `labelled_list`
   (`runCaseE_fits`, `layeredCase_fits`), and every retyping of it is refused
   (`tests/test_events_route.py::test_a_retyped_events_premises_row_is_refused`, 10 values). `base_environment`'s
   constants are typed on an events case. The binding is et-5's relay (R8, row 2 of the plan's ET-5).
2. Deliverables: PASS. The plan-row table above names each row's code and test, or et-4c. A grep of
   `git diff main...HEAD` finds no Python copy of a Lean decision (the kind gate, the row, the view and the replay are
   Lean's) and no report test. `feature/pc-1` (`Dispatch.lean`, `layersApart`) and `feature/pc-3b`
   (`ContractExamples.lean`, the end of the file) overlap in other hunks.
3. Tests can fail: PASS. `mutants.json`; `tests/test_events_wire_mutants.py` (HOOK and generated);
   `tests/test_packs_guard_mutants.py`; `trust-mutants.json` (et-4b-tm, on the Lean as merged: 331 KILLED, 0 SURVIVOR,
   0 UNKNOWN, 74 INVALID, 66 ALLOWED, exit 0).
4. Py/Lean/Rust agree: PASS. No Python or Rust decision changed. A list without `events@0` keeps every answer
   (`gate_legacy`, the block-less guards); the route cases are in the selected run.
5. R8 binding: N.A. Python reads none of the new fields yet (et-5 binds them). The schema half is item 1.
6. Gate evidence on the final HEAD: PASS for what I ran (Tests, above). The chain runs the gate.
7. No unsigned item: PASS. DELTA row 1 cites R16, row 2 cites SYNTHESIS 2.2 as ap-1bd's row 2 did, row 3 cites R2.
8. Every user-visible change is in DELTA: PASS. The three rows. Nothing changes for a list without `events@0`.
9. Test selection: PASS. The 545-unit selection picked `test_profile_table`, `test_route_row_schemas`,
   `test_assurance_manifest`, `test_packs_guard_mutants` and `check_lean_imports`, which caught this branch's
   inventory faults.
10. Lean statements: PASS. `events_wire_acceptance` matches spec 6.3 word for word. `gate_events`,
    `events_row_composition`, `hooked_X` and `decodeEventsWith_ok` state the returned values. The tool's
    proof-breaking mutants name the proofs they break.
11. Budgets and limits: PASS. `ResourceLimit: events premises` is tested at 253/254 and 250/251 (two of each) and at
    20,000 links. The pack total is tested at `nodes 0 + nodes 1` and one under, `weaker 60`/`weaker 30`. The dates
    are tested at 63/64 and 2,000, the vocabulary at 245/246, 247/248, 248/249 and 244/245. All fail closed with
    `ResourceLimit`.
12. CPU or memory: PASS. Every check before a quadratic step is charged first, and `repeatOf` is one pass (the
    20,000-entry lists end in seconds, with no timing assert). No route without `events@0` does new work.
13. Removed tests: N.A. No test removed.
14. Both directions, cited evidence, spec re-read: PASS. Each new check has an accepting and a refusing fixture (the
    tables above). Spec re-read:
    - spec 1.1 (the row) against `packRows`;
    - spec 3 (identity, the dates in the regenerated vocabulary, `base_environment`) against `routeView` and the
      identity guards;
    - spec 4 items 1 and 5 (the row first, `LinkNotOpen` before the dates) against `eventsHook` and
      `decodeEventsWith`;
    - spec 6.3 (`events_wire_acceptance`, `EventsEntailmentReplay`) against `Chain.lean`;
    - plan ET-4 and 3.3 against the plan-row table.

## FIXMAP
Files:
- lean/VE/Compose/Dispatch.lean: eventsRefused, packRows (first in profileTable), eventsFault, gate_events
- lean/VE/Events/Wire.lean: checkOpen, BlockLinks, decodeThroughLinks, finishEvents, decodeEventsWith(_ok), openTermsOf, EventsHook, routeView, eventsHook; repeatOf one pass; checkPremiseSize total
- lean/VE/Events/Chain.lean: eventsHook_block, hooked_X, decodeRightsU_packs, events_row_composition, EventsEntailmentReplay, replayEventsEntailment, events_wire_acceptance; F1: unhooked_X(_wellFormed), replayUnblockedEntailment, unblocked_wire_acceptance
- lean/VE/NormDefaults/Layered.lean: hookView/hookBlock/hookPacks/hookNames, caseOpenTerms, the hook in decodeSoftU/decodeRightsU/decodeLayered, eventsArray in layeredElaborate
- lean/VE/NormDefaults/LayeredAdmission.lean: replayLayeredOn(_L), layered_entailment_of_valid; Run.lean: eventsServed, pendingEvents, runCaseE, certificateAnswer (F1)
- lean/VE/NormDefaults/Packs.lean: eventsArray; ResponseShape: the events selector, events_premises, digests, runCaseE_fits
- fixtures: lean/VE/Events/{WireExamples,RouteExamples}.lean; tests/test_events_route.py; tests/test_events_wire_mutants.py (HOOK, ORDER)
- inventories by hand: tools/trust-classes.json, ve/assurance-manifest.json (decoder pins), tools/layer_policy.py (RouteExamples a runner fixture), tests/test_profile_table.py, tests/test_route_row_schemas.py, lean/VE/Compose/Examples.lean, ContractExamples.lean, Cardinality/Gate.lean
Regression commands:
- cd lean && PATH=~/.elan/bin:$PATH lake build VE.Events.RouteExamples VE.Events.WireExamples ResponseShape
- uv run pytest -q tests/test_events_route.py tests/test_events_wire_mutants.py tests/test_profile_table.py
- uv run python tools/trust_map.py --check
- zsh /home/seyran/code/manage-agents/mac-pytest.sh --trustmut -- --base 1a39ebef39c00863cf608956b2a12a928f19cd1d --only @docs/events-time-causation/et-4b/trust-mutants-only.txt --max-mutants 1000 --test lean/VE/Events/WireExamples.lean --test lean/VE/Events/RouteExamples.lean --allow docs/events-time-causation/et-4b/trust-mutants-allow.json --json docs/events-time-causation/et-4b/trust-mutants.json
Generated files: uv run python tools/regen_generated.py --write
## END FIXMAP
