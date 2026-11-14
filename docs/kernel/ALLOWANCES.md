# Kernel allowances

The kernel's size is the `kernel_lines` of [closure-baseline.json](closure-baseline.json), measured by
`python3 tools/kernel_closure.py` ([the kernel boundary](../spec/kernel-boundary.md), sections 2 and 6).
It may fall freely. It may rise only with a line in the table below, added in the same change that
raises it and signed by the architect seat (`manage-agents/fable-team/architect/HANDOFF.md`).
`tests/test_kernel_closure.py` reads the figure after the words "signed total:".

signed total: 10,015 lines

| Date | Change | Door | Lines | Total after | Signed |
|---|---|---|---:|---:|---|
| 2026-11-11 | First measurement on main `97b3c7999a`: the paths certificate, route, norms and softNorms | none | 9,565 | 9,565 | architect seat, round 1 |
| 2026-11-11 | Review kb-0 F1: `certificate` re-measured with the subject its theorems state (`Query.accepts`, `ClosureQuery.accepts`); its 637-line wire has no theorem, so the path is a candidate (KB-6) | none | -609 | 8,956 | not needed (a fall, section 6.2) |
| 2026-11-11 | Review kb-0 F3: each kernel path's spec is cut at the registry's `uncovered` runners, as the census body already was (route's `runCase_dispatch` read `Definitions.Bundle.runBundle` and `Route.Run.runAdmit` into the kernel) | none | -224 | 8,732 | not needed (a fall, section 6.2) |
| 2026-11-11 | KB-7: `metered` promoted to the kernel with `VE.Route.MeteredRun.runWith_sound` (its wire code under 24,945 keyed calls is now behind a theorem) and `VE.SoftNorms.Run.soft_wire_elaborate` listed on `softNorms` | C | +772 | 9,504 | architect seat, round 2 |
| 2026-11-12 | kb-10a: `VE.SoftNorms.Run.soft_wire_selected` listed on `softNorms` (the `soft-selected` kind's whole answer; its spec reads `selectedAt`, `outcomeAt`, `QueryDecoded` and `SelectedAnswer`; path 4,761 to 4,920 lines, distinct kernel lines +48) | C | +48 | 9,552 | kb-10a, door C, pre-signed by the architect seat up to +300 lines |
| 2026-11-13 | kb-3: the premise slot on the wire. `VE.SoftNorms.Run.slot_wire_certificate` and `slot_wire_conflict` (the `slot-certificate` and `slot-conflict` kinds' whole answers) and the replay theorems of `VE.Compose.SlotWire` (`slot_wire_acceptance`, `slot_wire_conflict_sound`, `slot_wire_conflict_witness_sound`, `slot_wire_empty`, `slot_wire_conflict_facts`, `slot_wire_entailment_facts`, `slot_wire_witness_facts`) listed on `softNorms`, with the three slot replays as subjects; the spec reads the answers (`SoftNorms.Run` +123), the soft replays `slot_wire_empty` compares with (`SoftNorms.Wire` +118), `decodeFacts` and `factsModel` (`Compose.SlotWire` +58) and the slot's semantics (path 4,920 to 5,368 lines, distinct kernel lines +395) | C | +395 | 9,947 | kb-3, door C (the slot claim kinds), pre-signed by the architect seat up to +400 lines |
| 2026-11-13 | kb-validators part 1: the norms profile condition enforced and stated on the metered path (`VE.Route.MeteredRun.profiled` on every family, `ProfileAdmits` in `EvaluationAnswer`, the bridge `VE.Norms.Plain.profileOkOn_holds`, the pin `prepare_profile`; up to +80) | C | +68 | 10,015 | architect seat, round 4 (entered after kb-3 at the merge with ve-integration: the two signed rises are disjoint, 9,552 + 395 + 68 measured as 10,015) |

Pre-signed, to be entered by the change that uses it:

| Change | Door | At most |
|---|---|---:|
| KB-1: `lean/VE/Kernel/Carry.lean` as in the specification's section 3 (it is counted only once a kernel path's fold uses it) | C | 80 |
