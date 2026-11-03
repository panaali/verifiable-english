# et-4b build report: the `events@0` row, the hook in the layered decoders, the replay

**Status:** done for this cut, ready for the gate. No DRI signature reserved (DELTA row 1 R16, row 2 SYNTHESIS 2.2 as
ap-1bd's row 2, row 3 R2). **HEAD:** the branch's last commit (the chain gates it).
**What changed:** `events@0` is a row of AR-10's table; `decodeSoftU`/`decodeRightsU` run `eventsHook` (the row, the
block with `LinkNotOpen` in spec order, the environment without the block) and put the pack last in `assemble`'s
list; `replayEventsEntailment` replays certificates over it with `events_wire_acceptance` (spec 6.3, word for word).
**Open items:** et-4c (below): `embeddable` and the fragment on situations, the 6.3 answer theorems, T3/T3b, the other
report fields, `origins`. Until then every answer about a situation on an events document is refused by name.
Size: 1,300+ hand-written lines against the ~600 rule (see Size). Pilot bytes 0.

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

## Seeded bugs and mutants

FILL-SEEDED

## Trust, size, tests

FILL-TRUST

## Next items

- **et-4c:** (3) `embeddable` and the completion fragment on every reported situation (`NotCalendar` UNKNOWN,
  `modelSafe`/`witnessSafe`/`settledSafe`/`undecidedSafe`), `fillPremises_canonical_completion`,
  `events_countermodel_calendar` and the 6.3 answer theorems, T3 and T3b through the service, the situation budget for
  the pack's premises; then the report fields `named_dates`, `causal_links`, `calendar_days` and `origins`, and the
  hook on the plain branch, admission and the readings wrapper. Then lift `pendingEvents` kind by kind.
- **et-5** reads `events_premises` now and the et-4c fields after it; ET-6 waits for both.

Acceptance items: all AGENT; none HUMAN or EXTERNAL.

## Self-review against BUILDER-CHECKLIST

FILL-SELF

## FIXMAP
Files:
- lean/VE/Compose/Dispatch.lean: eventsRefused, packRows (first in profileTable), eventsFault, gate_events
- lean/VE/Events/Wire.lean: checkOpen, BlockLinks, decodeThroughLinks, finishEvents, decodeEventsWith(_ok), openTermsOf, EventsHook, routeView, eventsHook; repeatOf one pass; checkPremiseSize total
- lean/VE/Events/Chain.lean: eventsHook_block, hooked_X, decodeRightsU_packs, events_row_composition, EventsEntailmentReplay, replayEventsEntailment, events_wire_acceptance
- lean/VE/NormDefaults/Layered.lean: hookView/hookBlock/hookPacks/hookNames, caseOpenTerms, the hook in decodeSoftU/decodeRightsU/decodeLayered, eventsArray in layeredElaborate
- lean/VE/NormDefaults/LayeredAdmission.lean: replayLayeredOn(_L), layered_entailment_of_valid; Run.lean: eventsServed, pendingEvents, runCaseE
- lean/VE/NormDefaults/Packs.lean: eventsArray; ResponseShape: the events selector, events_premises, digests, runCaseE_fits
- fixtures: lean/VE/Events/{WireExamples,RouteExamples}.lean; tests/test_events_route.py; tests/test_events_wire_mutants.py (HOOK)
- inventories by hand: tools/trust-classes.json, ve/assurance-manifest.json (decoder pins), tools/layer_policy.py (RouteExamples a runner fixture), tests/test_profile_table.py, tests/test_route_row_schemas.py, lean/VE/Compose/Examples.lean, ContractExamples.lean, Cardinality/Gate.lean
Regression commands:
- cd lean && PATH=~/.elan/bin:$PATH lake build VE.Events.RouteExamples VE.Events.WireExamples ResponseShape
- uv run pytest -q tests/test_events_route.py tests/test_events_wire_mutants.py tests/test_profile_table.py
- uv run python tools/trust_map.py --check
- zsh /home/seyran/code/manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --test lean/VE/Events/WireExamples.lean --test lean/VE/Events/RouteExamples.lean --allow docs/events-time-causation/et-4b/trust-mutants-allow.json --json docs/events-time-causation/et-4b/trust-mutants.json
Generated files: uv run python tools/regen_generated.py --write
## END FIXMAP
