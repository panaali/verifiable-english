# fsf-r2: the DeepMind translation re-measured on 2026-10-28, and one probe per merged item

Status: done. Main base 6d0a10526 (2026-10-28). The translation is fsf-r1's, unchanged. **No byte moved since Oct 18:**
every unit keeps its status and every answer is the same (257 of 262 agree with the key). Of the three merged items,
none lets a unit of the D1 document be written so that VE checks it: `judgments@0` keeps a judged unit OPEN by
theorem and cannot yet be listed with `soft-norms@0`, the defaults flag refuses a document with open reading sets, and
`scope@0` refuses a reading set on a governor's own unit, which is where RS8 sits.

Files: [units.json](units.json) and [gaps.json](gaps.json) (fsf-r1's measurement of the saved spans and results, with
each unit's Oct 18 status and each feature's family), [probes.json](probes.json) (VE's answer on each probe). All
three are written by [`usecases/safety-framework/measure_r2.py`](../../../../usecases/safety-framework/measure_r2.py).
fsf-r1's evidence ([../fsf-r1/](../fsf-r1/)) is unchanged.

## (a) The existing harness, unchanged

| Command (from the repository root, after `lake build` in `lean/` and `python3 tools/rust_build.py`) | Result |
|---|---|
| `uv run python usecases/safety-framework/run.py --check` | exit 0 (3 min 7 s): `results.json` recomputed byte for byte; 257/262 agree, the same five disagreements |
| `uv run python usecases/safety-framework/build_document.py --check` | exit 0: `spans.json` and `coverage.json` unchanged |
| `uv run python usecases/safety-framework/readings_r1.py --check` | exit 0: `readings/results.json` unchanged |
| `uv run python usecases/safety-framework/measure_r1.py --check` | exit 0: fsf-r1's `units.json` and `gaps.json` unchanged |

No unit changed its status or its answer, so there is no cause to report. `gaps.json` records
`units_changed_status_since_oct18: []`.

| Status | Oct 1 | Oct 18 (fsf-r1) | Oct 28 (fsf-r2) |
|---|---|---|---|
| CHECKED | 4,595 (8.5%) | 4,595 (8.5%) | 4,595 (8.5%) |
| OPEN | 7,356 (13.5%) | 7,356 (13.5%) | 7,356 (13.5%) |
| LABELLED | 35,557 (65.4%) | 35,557 (65.4%) | 35,557 (65.4%) |
| UNFORMALISED | 6,865 (12.6%) | 6,865 (12.6%) | 6,865 (12.6%) |

## (b) The probes

Each probe is a part document cut from the pinned source: the probed units' own bytes, their rules from
`rules.d1.ve` and their open terms. Lean's document mode answers it through the one relay entry (`ve.backends.relay`),
or `ve document readings --assume-no-exception` does for the flag. Each answer below is in probes.json.

### jt-2, jt-2b: `judgments@0` (feature "judgment terms", JT: 36 units, 7,976 B; alone 23 units, 5,114 B)

| Probe | Document | VE's answer |
|---|---|---|
| JT-a | s134-rra (rule f7-rra, OT1) in D1's own environment (`norms@0`, `readings@1`, `relational-fol@0`, `soft-norms@0`) with `judgments@0` and `documents@1` | refused: `CheckerUnavailable: judgments@0 with soft-norms@0 needs its composed Lean route` |
| JT-b | the same unit without `soft-norms@0` and `readings@1`; OT1 declared as D1 declares it (`ot1_level_reached`, a name no formula reads) | refused: `JudgmentUnbound: ot1_level_reached` |
| JT-c | as JT-b, with OT1 declared on the open predicate the rule reads (`reached`) | admitted; s134-rra **OPEN**; usage map `reached: [s134-rra]` |
| JT-d | all 8 units with a rule of their own and an open term (1,291 B), each listing the open predicates its rule reads | admitted; all 8 **OPEN**; usage map `adherence_undermined`, `approaches`, `frontier`, `internal_risk_unacceptable_without_safeguards`, `reached` (5 units) |

Why no byte moves:

- D1 needs `soft-norms@0` (RS3 Ds, RS4 and the default rules), and the document mode refuses `judgments@0` beside it
  until the composing modes are built (jt-2c, not merged; jt-2 REPORT, "Compositions refused by name").
- Where it is admitted, a unit whose content uses a bound judgment is OPEN by theorem (`status_never_checked`,
  judgment-terms.md 4.3), never CHECKED. The profile adds the usage map, which says which term each OPEN unit waits on.
  It does not change any status.
- JT-b shows that D1's open-term records are names no formula reads. Under `judgments@0`, each record has to be
  declared on the open predicate the rule reads. That is a re-expression (fsf-r3). It also drops a record with no
  predicate: s321-periodic lists `ot12_periodic`, and no formula reads "periodic", so under JT-d it lists only
  `reached`.

### df-1b, df-1bb: the defaults relay behind `--assume-no-exception` (feature "two readings kept", 7 units, 1,436 B; "defeasible (stated adjustments)", DF, 2 units, 551 B)

| Probe | Document | VE's answer |
|---|---|---|
| DF-a | RS4holistic's part document (s135-holistic with its force set, strict or default, as D1 writes it) | flag refused: `--assume-no-exception applies to a soft-norms@0 document without open reading sets`; the unit stays **OPEN** |
| DF-b | s135-holistic with only the default reading as its content, no set. This collapses RS4holistic, which a translation of someone else's text never does, so it is a probe only | flag refused: `UnsupportedProfile: case kind defaults-elaborate is not available on the norms route` (the environment lists no `norm-defaults@0`); `ve document check` gives the unit **CHECKED** |
| DF-c | DF-b with `norm-defaults@0` and `documents@1` listed, as df-1bb's probe documents are | flag answers the default question **UNKNOWN** ("no certificate"); `ve document check` refuses: `Unsupported profile norm-defaults@0` |

Why no byte moves:

- Every force set of D1 (RS3 Ds strict or default, RS4holistic, RS4within, RS4elicitation) is an open reading set,
  which the flag refuses (DF-a).
- The flag answers a question; it does not set a unit's status. A unit becomes CHECKED only by dropping a reading
  (DF-b), and the translation rules forbid that.
- The "may be adjusted" units (s22-adjusted 482 B, fn11 69 B) could be written as a default rule with an exception
  decided by the developer (OT16). They would need `norm-defaults@0` in D1, and `ve document check` refuses that
  profile in a document (DF-c). They would also be OPEN (OT16), not CHECKED.

### sc-5r, sc-5rb: per-choice GOVERN over a reading set inside a governed list (feature "readings: a reading with no rule or several rules", 11 units, 2,161 B; RS8 on 3 units, 307 B)

RS8's unit, "This is required only for external deployment, not internal deployment or further development"
(s135-bullet2-only), narrows the DM rule of the sub-bullet before it (f9-dm). Written in `scope@0`, it is a
governor whose effect re-guards f9-dm, and RS8's two readings (scope: no rule; rel: a release) are readings of the
governing words themselves.

| Probe | Document | VE's answer |
|---|---|---|
| SC-a | D1's chain (soft, `readings@1`) + `scope@0`: s135-bullet2-dm (f9-dm) and s135-bullet2-only as a governor re-guarding f9-dm, with RS8's set on the governor's unit | refused: `CheckerUnavailable: soft-norms with norm-defaults, readings, alternatives or risk needs its composed Lean route` |
| SC-b | SC-a without the set (and without `readings@1`) | admitted; both units **OPEN** (OT2 in f9-dm; the governor takes its rule's status) |
| SC-c | SC-a on the plain norms chain (`norms@0`, `readings@1`, `relational-fol@0`, `scope@0`) | refused: `ScopeReadings: s135-bullet2-only` |
| SC-d | SC-c without the set | admitted; both units **OPEN** |

Why no byte moves:

- sc-5rb governs a set per choice only when the set's unit is an item the governor covers, never when it is the
  governor's own unit (scope.md 11.1: "A set on a governor's own unit: the governing words themselves have readings,
  which is SC-5's case"). RS8 is that case (SC-c).
- On D1's soft chain, `scope@0` with `readings@1` is not composed yet (SC-a).
- Without the set, the governor is admitted, but it is OPEN (SC-b, SC-d), and writing it without the set would drop
  RS8's release reading.
- The other pending sets (RS1 G, RS5 R: several rules; RS3 F, RS4aim intent, RS7 M: no rule) are on units no
  governor covers, so sc-5rb carries them unchanged.

### The other fsf-r1 features

No merged item since Oct 18 bears on modality (AT, 3,276 B), attitudes (AT, 1,855 B and 486 B), process and
deadline wording (ET, 2,212 B), external references (1,978 B), causation (WG, 807 B), addressee (SC, 283 B) or the
units with no claim to check (29,619 B). No probe was run for them.

## Bytes moved since Oct 18, per merged item

| Merged item | Bytes moved | Why |
|---|---|---|
| jt-2, jt-2b (`judgments@0`) | 0 | refused with `soft-norms@0` (JT-a); where admitted, a judged unit is OPEN by theorem (JT-c, JT-d) |
| df-1b, df-1bb (defaults flag) | 0 | refused on open reading sets (DF-a); a query answer, not a status; CHECKED only by a forbidden collapse (DF-b) |
| sc-5r, sc-5rb (`scope@0` per choice) | 0 | RS8 is a set on a governor's own unit: `ScopeReadings` (SC-c); not composed on the soft chain (SC-a) |

## fsf-r3: the re-expressions these probes name (not made here)

These need the independent second-model fidelity check that fsf-r1's re-expressions had, so this item does not
make them. Expected bytes:

| Re-expression | Needs | Expected move |
|---|---|---|
| Declare each open term on the open predicate its rule reads (`judgments@0`, JT-c/JT-d), add `documents@1` | jt-2c (`judgments@0` with `soft-norms@0` and `readings@1`) | 0 B to CHECKED; the usage map for the 36 JT units (7,976 B). The UNFORMALISED judgment-term units (1,355 B: "as appropriate", "where appropriate", degree terms) can be written with content and move UNFORMALISED → OPEN (judgment-terms.md F2) |
| Write "may be adjusted" (s22-adjusted, fn11) as a default rule with an exception decided by the developer (OT16) | `norm-defaults@0` admitted by `ve document check` in D1 (DF-c) | 551 B UNFORMALISED → OPEN; 0 B to CHECKED |
| RS8 as a governor's re-guard with its readings | SC-5 proper (a set on a governor's own unit) and `scope@0` with `readings@1` on the soft chain | 0 B (the units stay OPEN on OT2 and the open set) |

So fsf-r3 would move at most 1,906 B from UNFORMALISED to OPEN, and none to CHECKED.
