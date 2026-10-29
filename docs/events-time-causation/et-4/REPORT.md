# et-4 build report: the `events` block decoder, the pack, the certificate theorem

**Status:** done for this cut; review F1 fixed (below); ready for the gate. No signature reserved (row 1: R16).
**What changed:** `decodeEvents` checks spec 4 items 2 to 7 in order and regenerates the environment; `eventsPack`
is PK-1's `events` pack; `date__` is in PK-1's prefix table; `events_certificate_calendar` matches spec 6.3 exactly.
Nothing reaches a route yet (Python and Rust unchanged).
**Open items:** et-4b, cut by the size rule (below). Bytes 0. The review's C notes F2-F4 are below.

## Review fix (et-4 review F1)

**The finding, as a class:** a check of `decodeEvents` was tested only on its accepting side, or only through a
fixture that another check refuses first. The trusted mutant run never selected the reject-only checks (D[R]), so no
tool mutant reached them. The review's probe left 7 mutants alive before the fix, and none after it.

**The fix, structural:** the decoder's product code is unchanged; only fixtures and tests are added.
- `tests/test_events_wire_mutants.py` plants the review's 7. It also plants 66 mutants generated from `Wire.lean`'s
  own source, of kinds beyond the tool's operators: each check step of a `do` block dropped (21), each role list read
  for its sibling (22), and each two adjacent independent check steps swapped, which pins the fault order (23). 4 are
  equivalent, and the test shows each still passes. Before the new fixtures, 34 of these survived; now none do.
- The tool ran over the reject-only class (`--classes D[R]`, 166 mutants). The first run, at 5e4dc8828 (4 VM shards,
  merged), found 18 survivors of the same class: an unknown key read first or last, the first of two missing
  fields, the day sort first or last among the sorts, the first or last event's or state's roles, a repeat that is
  not adjacent, and the first of two premises. Each now has a fixture. `reject-mutants.json` is a full Mac run on
  97792c45: 120 KILLED, 0 SURVIVOR, 0 UNKNOWN, 28 INVALID, 18 ALLOWED, exit 0.
- `reject-mutants-allow.json` explains each of the 18 allowed, checked against the record's `raw_status`:
  - 13 are mutant texts Lean refuses (an untyped `[]`; `rolePreds linkPreds`).
  - 5 are equivalent. `optional` has at most one field. The seed `[V.before]` of the repeated-role check is dead,
    because a role named `before` is refused earlier by `checkDay`'s signature and line 112.
- The node limit inside `decodeEvents` cannot be reached: every generated premise has at most 20 nodes, and a
  `#guard` pins this. `checkPremiseSize` is now pinned on its own at both ends of its list.
- The new fixtures add no definition, so the trust classes stay the same: `trust_map.py --check` gives V +120 and
  passes. The R16 run (`trust-mutants.json`, a full Mac run on 97792c45) is unchanged: 199 KILLED, 0 SURVIVOR, exit 0.

**Seeded bugs** (Lean is the only language whose code is tested here; Python adds only the test): each mutant above
is a seeded bug in `lean/VE/Events/Wire.lean`, and the fixture that fails is in `WireExamples.lean`. The review's 7
are `test_every_mutant_fails_a_fixture[review-*]`; before the fixtures each was "survives every #guard".

**C notes:**
- F2: DELTA row 1 now quotes the final run.
- F3: the size grows with this fix (see Size).
- F4: these notes are et-4b's (FOLLOW-UP line of the review): count the 64 date constants in `assemble`'s name
  limit; run `LinkNotOpen` inside `decodeEvents`, before the date checks; fill `origins`.

Item: feature item et-4 (rank 95 of the feature feed, acting DRI dri-featurefeed, 2026-10-18). Branch
`feature/et-4` from main 6d0a10526. Plan and spec are on main, so nothing was copied.

## Statement gate

Draft 3 of the plan's change log records the converged statement review of ET-2's spec (FIX) applied. et-3d merged
(2d84b832c) with `embeddable_sound` proved under the DRI's amendment, so the gate is open. To compare, I ran et-3b's
`evidence/statements-diff.py.txt` with two edits: the section is `### 6.3 The pack, the wire and the answers (ET-4)`
up to `### 6.4`, and files ending in `Examples.lean` are skipped. Its output is `evidence/statements.json`:
- **Both theorems built here are exact:** `eventsX_absent` and `events_certificate_calendar`.
- **Three definitions differ, and no theorem changes** (see Deviations).
- **17 are not built:** they are et-4b's.

## Plan rows and directive lines

| Row | Delivered | Where |
|---|---|---|
| (1) `decodeEvents`: 2.9's checks in order, `regenEnv`, the texts (`EventsReserved` …); `eventsX_absent` | yes, items 2-7 of spec 4; item 1 (the profile row) and `LinkNotOpen` (item 5) → et-4b | `Wire.lean`; fixtures `WireExamples.lean` |
| (2) `eventsX` as PK-1's `events` pack: one provider line, last in `packOrder`, no assembly of its own | yes: the row `("events", "date__")` in `reservedPrefixes`; `eventsPack`; `assembleIn` places it after soft (`#guard`) | `Packs.lean:41`, `Wire.lean` |
| (3) `events_certificate_calendar` (from `acceptanceX`) | yes, exact text | `Chain.lean` |
| (3) `events_wire_acceptance` (`replayEventsEntailment`) | → et-4b | |
| (4) `embeddable` and the fragment on every reported situation; `events_countermodel_calendar` | → et-4b | |
| (5) seeded bugs: `eventsX` before soft | yes (`packOrder-events-first`) | `mutants.json` |
| (5) T3 and T3b through the service | → et-4b, with (4) | |
| (5) one mutant per new trusted definition | yes: `trust-mutants.json` (exit 0) plus hand mutants for `strAt`, `arrAt`, `eventsPack` | |
| report fields, shapes, encoder theorems, the `events@0` row | → et-4b (task: "follow as et-4b unless they fit") | |
| fixtures on both sides of each check | yes: every text refused at its boundary and accepted just inside it (64/65-byte decider, 64/65 dates with and without a new anchor, 1970-01-01 and 1969-12-31, `date__x` and `date_x`, the node limit at 5 and 4, …) | `WireExamples.lean` |

**Why (3b) and (4) are cut.** The soft and rights decoders refuse the `events` key and the `events@0` profile
(`decodeEnvelope`'s `exactFields`, `classify`). So a replay first needs the route hook: the environment without the
block, the date constants in its vocabulary JSON, the identity over the original bytes, the pack in `decodeSoftU`'s
`assemble` list, and `LinkNotOpen` over the document's open terms. Lean has no certificate producer, so an accepting
replay fixture needs a mode that produces one. With (1) and (2) at 420 lines of code and fixtures, that does not fit.

## Deviations (definitions only; every theorem keeps its reviewed text)

- **`eventsPack` declares no names** (`decls := []`, `consts := []`; the spec gives the dates as `decls`). Every
  checker stays over `envAt (fill U) 0` until AT-2 threads `envX` (premise-packs.md, "What pk-1 does not change").
  `events_certificate_calendar`'s `hX` types `eventsX V` over that environment too. So the date constants are in the
  regenerated environment, as `unsaid__` names are (plan 2.8). If the pack declared them as well, `assemble` would
  refuse them as already declared.
- **`EventsDecoded` gains `typed : EventsTyped E V = true`.** It is built by `regen_typed` from the
  `WellFormedEvents` check that ends `decodeEvents`. This is et-3d's FOLLOW-UP: the year bound, stated on the decoder's
  output. The spec's `VE.Packs.RequestPath` is `VE.NormDefaults.Packs.RequestPath`. `origins` is `[]` until et-4b's
  relay binds them (`OriginsExact` lands with AT-2).
- **`decided_by` is bound by `VE.Limits.maxIdentifierBytes` (64)**, not a literal (`test_lean_limits`).
- `decodeEvents` ends with `WellFormedEvents`. Items 3 to 6 cover every conjunct of it, so no fixture reaches its
  text `InvalidInput: events`.

## Seeded bugs (Lean; `mutants.json` is the output of `evidence/seeded-bugs-harness.py.txt`, unedited)

| Bug | File | Fails |
|---|---|---|
| `packOrder-events-first` (plan bug 1) | `lean/VE/NormDefaults/Packs.lean` | PK-1's `X_soft_first` (`Packs.lean:350`); the build stops before WireExamples' order guard |
| `prefix-row-dropped` | `lean/VE/NormDefaults/Packs.lean` | `#guard diag (env block (withConst "date__2026_10_12")) == "EventsReserved: …"` and 5 more |
| `absent-block-refused` | `lean/VE/Events/Wire.lean` | `eventsX_absent`'s proof |
| `anchor-not-added` | `lean/VE/Events/Wire.lean` | the base `#guard` (dates with the anchor) and 13 more |
| `decided-by-65` | `lean/VE/Events/Wire.lean` | the 65-byte decider `#guard` |
| `strAt-path` | `lean/VE/Events/Wire.lean` | `#guard … "InvalidInput: events.day"` |
| `arrAt-drops-first` | `lean/VE/Events/Wire.lean` | the base `#guard` and 33 more |
| `eventsPack-calendar-only` | `lean/VE/Events/Wire.lean` | `#guard … (eventsPack d).labelled == eventsLabelled d.V` |
| `roles-before-day` (fault order) | `lean/VE/Events/Wire.lean` | `#guard … == "EventsSort: date"`, `"EventsSort: stay_begins"` |

**Trust mutants:** `trust-mutants.json` is a full Mac run on the final Lean tree (97792c45), with
`--test lean/VE/Events/WireExamples.lean --allow trust-mutants-allow.json`. It exits 0:
- 199 KILLED, 0 SURVIVOR, 0 UNKNOWN, 36 INVALID, 33 ALLOWED.
- Of the 22 allow entries, 5 are equivalent survivors: `≤`/`<` on distinct dates, two `Option.toList` takes, and the
  prefix row's position under the owner filter. The other 17 are mutant texts Lean refuses (type errors).
- Python and Rust: no product code changed (`ve/assurance-manifest.json` and `tools/trust-classes.json` are data).

## Trust, size, tests

- **Trust:** `uv run python tools/trust_map.py --check` against 6d0a10526 gives K +0, S +0, **V +120**
  (`VE/Events/Wire.lean`), unclassified 0. It passes with the R16 allowance in `docs/trust-baseline.json`. The ties
  row is in `manage-agents/FOLLOW-UPS.md` `## et-4`. Reject-only checks are D[R], fixtures T, the theorem P.
- **Size:** 1108 hand-written lines before this round's report edits; the review measured about 705 at 7efef75a6,
  not 650 (F3). The fix adds the mutant test (294), fixtures (88), the D[R] allow file (12) and 4 trust-class lines.
  The first cut's figure was about 650 hand-written lines with this report, measured with `git diff --numstat 6d0a10526`, without
  generated inventories or tool-written evidence JSON. Of those, 420 are code and fixtures: `Wire.lean` 192,
  `WireExamples.lean` 204, `Chain.lean` 23, `Packs.lean` 1. The rest is the trust classes (57), the harness (46),
  the allow file (24), DELTA (13), two root imports and two manifest lines. That is over the ~600 rule by the
  evidence the R16 mutants needed. The product code was cut at (3a).
- **Tests:** the selected set ran once on the Mac runner over 6 shards (383 units): 381 passed, 2 failed. Both were
  fixed in b887dcc11 (`test_lean_limits`'s literal 64; the manifest's `other_json` for the two new files). Both files
  then passed locally: 141 passed. No `main-known-red.txt` test was hit. `gate_collection.py --check --prebuilt`:
  0 added, 0 removed, 0 refused. `lake build` (1135 jobs) and `python3 lean/audit.py` PASS (656 files).
- **Pilot bytes:** 0 (infrastructure; nothing reachable). ET-6's estimate (UDHR +201 to 548 B) still waits on et-4b,
  ET-E1, ET-5 and `infra/oom-rootcause`. Nothing is claimed before a pilot audit.

## Next items

- **et-4b:** the route hook in `decodeSoftU`/`decodeRightsU`. It covers the environment without the block, the
  regenerated vocabulary JSON, identity over the original bytes, the pack in the `assemble` list, and `LinkNotOpen`.
  Then `replayEventsEntailment` with `events_wire_acceptance`, (4) with the 6.3 answer theorems and T3/T3b through
  the service, the report fields with their shapes and encoder theorems, `origins`, and the `events@0` profile row
  with `events_row_composition`.
- Then ET-E1 (approved) and et-5.

Acceptance items: all AGENT; none HUMAN or EXTERNAL.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. No route, relay or response schema changes; `decodeEvents` is unreachable. Its malformed-input sides are `#guard`s (`events`, `events.day`, `events.states`, `events.dates`, `events.anchor`).
2. Deliverables: PASS. Every plan row is in the table, with what moved to et-4b by the size rule. Rule grep of `git diff main...HEAD`: no Python or Rust decision, no report test. No in-flight `feature/*`, `infra/*`, `lean-first/*` or `foundation/*` branch edits `Packs.lean` or `Events/{Wire,Chain,WireExamples}`.
3. Tests can fail: PASS. `mutants.json` (9 bugs, each failing a `#guard` or a proof); `trust-mutants.json` and `reject-mutants.json` (exit 0, Mac); `tests/test_events_wire_mutants.py` (73 mutants, 4 equivalent, each shown to pass).
4. Py/Lean/Rust agree: N.A. Only Lean changed, and it reaches no route.
5. R8 binding: N.A. No Lean answer is read by Python.
6. Gate evidence on final HEAD: PASS for what I ran. The selected tests ran on a592c61fd and the two fixes on b887dcc11; later commits change only evidence and docs. The chain runs the gate on the final HEAD.
7. No unsigned item: PASS. DELTA row 1 cites R16 with its conditions; no row is reserved.
8. Every user-visible change in DELTA: PASS. None is reachable; DELTA says why the prefix row is not visible.
9. Test selection: PASS. The selection (383 units) picked `test_lean_limits` and `test_assurance_manifest`, which caught this branch's two faults.
10. Lean statements: PASS. `evidence/statements.json` (2 exact theorems); `absent-block-refused` breaks `eventsX_absent`'s proof.
11. Budgets and limits: PASS. The 64-date, 64-byte and node limits fail closed with `ResourceLimit`/`InvalidInput`, tested at the limit and one over (`WireExamples.lean`, item 2, 6 and 7 `#guard`s).
12. CPU or memory: N.A. No runtime path changes.
13. Removed tests: N.A. `gate_collection.py --check --prebuilt`: 0 removed, 0 malformed.

## FIXMAP
Files:
- lean/VE/Events/Wire.lean: EventsDecoded, VocabView, the shape readers, checkDay/checkRoles/checkLinks/checkDates/checkPremiseSize, decodeEvents, eventsPack, eventsX_absent
- lean/VE/Events/Chain.lean: events_certificate_calendar
- lean/VE/Events/WireExamples.lean: fixtures; lean/VE/NormDefaults/Packs.lean:41: the events prefix row
- tools/trust-classes.json, docs/trust-baseline.json, ve/assurance-manifest.json, lean/VE.lean (roots)
- docs/events-time-causation/et-4/: DELTA, REPORT, mutants.json, trust-mutants.json, trust-mutants-allow.json, reject-mutants.json, reject-mutants-allow.json, evidence/
- tests/test_events_wire_mutants.py: the decoder's generated mutants (review F1)
Regression commands:
- cd lean && PATH=~/.elan/bin:$PATH lake build VE.Events.WireExamples VE.Events.Chain
- python3 docs/events-time-causation/et-4/evidence/seeded-bugs-harness.py.txt "$PWD" (prints mutants.json)
- uv run pytest -q tests/test_lean_limits.py tests/test_assurance_manifest.py
- uv run python tools/trust_map.py --check
- uv run pytest -q tests/test_events_wire_mutants.py
- zsh /home/seyran/code/manage-agents/mac-pytest.sh --trustmut -- --classes 'D[R]' --max-mutants 1000 --test lean/VE/Events/WireExamples.lean --allow docs/events-time-causation/et-4/reject-mutants-allow.json --json docs/events-time-causation/et-4/reject-mutants.json
- zsh /home/seyran/code/manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --test lean/VE/Events/WireExamples.lean --allow docs/events-time-causation/et-4/trust-mutants-allow.json --json docs/events-time-causation/et-4/trust-mutants.json
Generated files: lean/VE/Audit.lean, lean/{axioms,declarations,predicates,statements}.txt, lean/checkers.lock ->
  uv run python tools/regen_generated.py --write (route-cases needs the Rust release binary: python3 tools/rust_build.py)
## END FIXMAP
