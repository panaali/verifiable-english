# Batch 13b report: core operations default to Lean

Branch `lean-first/b13b`, base `main` at `abc30811`. Plan row 13b (draft 3): typing, parse, definitions,
Background, bundles, norms, admission, graph, readings, premise status and compare default to Lean, for the inputs
Lean covers; the four stage-2c fallbacks stay until 14a–d. The 13a report scheduled the default certificate
replay here too, so it is switched as well. The [ledger](LEDGER.md) maps every deleted decision site to its Lean
owner; [DELTA.md](DELTA.md) classifies every changed answer and lists what is retained and what needs a signature.

## What changed

* **One owner.** `dispatch.LEAN_OWNED` (17 operations) joins `dispatch.SINGLE_OWNER` with engine `lean`:
  `execute` refuses them, `owned` runs them on Lean under every selection (`python`, `shadow`, `lean`,
  `rust-experimental`) and pins their constituents to Lean. The `python` and `shadow` paths of these operations,
  and their per-operation shadow comparison, are gone; the shadow machinery itself stays for the batch-15
  operations and goes in batch 18.
* **Deleted.** The Python FOL and norms admission with their decoders and diagnostics, the Python Background
  premise generators, the label and dependency-order checks, the typing closures (Python and Rust), and
  `validation.decided`, the arbitration under which Python's text won for definitions and bundles.
* **Lean added.** `Standalone.typingReduced` types formulas over `readings@1`, `norm-defaults@0` and `risk@0`
  environments (10 lines), which removed the last reason for a Python typing fallback on those profiles.
* **Relays bound.** `admission.bound_admission` binds an admission row to its request (kinds, root, report
  identity); the relay fuzz of `tests/test_lean_first_b13b.py` found the unbound report first.
* **Found and fixed on the way.** Lean's Background refused alternatives, risk, norm-defaults, readings and W6
  environments (now the model projection is sent); the norm-defaults fill premises were a slot of the deleted
  Python generator only (now sent to Lean's replay); premise status and compare over `norm-defaults@0`/`readings@1`
  have no Lean countermodel check yet (retained, listed).

## Gate evidence

<!-- BEGIN GENERATED: python docs/lean-first/b13b/report.py --write -->
| Corpus | Records per side | Same | Wording | Order | Verdict | Availability |
|---|---:|---:|---:|---:|---:|---:|
| conformance | 39,612 | 39,564 | 48 | 0 | 0 | 0 |
| discourse | 6,350 | 6,350 | 0 | 0 | 0 | 0 |
| document | 3,632 | 3,609 | 19 | 4 | 0 | 0 |
| norm_defaults | 2,020 | 2,020 | 0 | 0 | 0 | 0 |
| pilots | 443 | 436 | 7 | 0 | 0 | 0 |
| probe | 18,870 | 18,869 | 1 | 0 | 0 | 0 |
| quantity | 25,726 | 25,726 | 0 | 0 | 0 | 0 |
| readings | 1,137 | 1,137 | 0 | 0 | 0 | 0 |
| rights | 2,500 | 2,500 | 0 | 0 | 0 | 0 |
| **All** | **100,290** | **100,211** | **75** | **4** | **0** | **0** |

Unlisted differences: 0. Branch commits (`main..HEAD --no-merges`, saved): 10, merge base `abc30811`, last source commit `85b02e40`.
Code lines, production Python: +324/−833 (net -509).
Code lines, Lean: +10/−2 (net +8).
Differential fuzz: 15 paired runs (CI and 14 date seeds); reviewed baseline 254 → 250; head-only new signatures 0; head entries not reproduced 0; all runs ok: True.
Seeded faults: 7 of 7 caught and restored; service build restored: True.
Latency, udhr: base 63.3 s → head 68.2 s wall (1.078×), child CPU 1.078×; same output: True; within budget: True.
Latency, eligibility: base 260.8 s → head 281.5 s wall (1.080×), child CPU 1.072×; same output: True; within budget: True.
Latency, agent-policy: base 64.0 s → head 79.7 s wall (1.246×), child CPU 1.225×; same output: True; within budget: True.
Full gate: not yet recorded (`evidence/gate.json` is archived by the commit after the gate run).
<!-- END GENERATED -->

| Item | Tag | Status and evidence |
|---|---|---|
| Suite | AGENT | The full gate on a clean worktree, line above (`evidence/gate.json`). |
| Corpus A/B | AGENT | `evidence/corpus-ab.json` against `DELTA.json`: zero unlisted, zero verdict, zero availability. |
| Differential fuzz | AGENT | `evidence/difffuzz-ab.json`: 15 paired runs, the reviewed baseline shrinks, no head-only signature. |
| Deletion ledger | AGENT | [LEDGER.md](LEDGER.md); `test_no_consumer_of_a_deleted_decision_site`; `tools/relay_lint.py` and `tools/inventory_lint.py` pass. |
| Latency | AGENT | `evidence/latency.json`. UDHR and eligibility are inside the budgets. **Agent-policy is 1.25× wall and 1.23× child CPU**: inside the 1.25× wall row, outside the 20% CPU allowance, so listed for a DRI signature. |
| Wording block, 4 order records | HUMAN | DRI, signature of DELTA.md's wording block and of each order record (DRI answer 3 makes Lean's texts canonical; the exact pairs are not yet signed). |
| Retained scope gaps 5–7 | HUMAN | DRI, acceptance of DELTA.md items 5–7 (inputs Lean does not cover yet), each with its follow-up. |
| Trust budget | HUMAN | DRI, signature for trusted +8 in `VE/Service/Standalone.lean`, recorded unsigned (with its reason) in `docs/trust-baseline.json`'s history. |
| Agent-policy CPU | HUMAN | DRI, signature for the 1.23× child CPU of `check.py base`. |
| Operational soak | EXTERNAL | Owner: DRI, the three-day soak after 13b (DRI answer 1). Not started by this batch. |

What was not run: the agent-policy harness's mutant and replay parts and the constitution pilot's full load were
not timed (the A/B covers every historical pilot document's answers); the search fixtures were not timed (search
is batch 15's).

## Seeded faults

`docs/lean-first/b13b/mutants.py --root <scratch worktree of the head>` applies one fault per claimed behaviour,
runs its tests (they must fail), restores the source and runs them again (they must pass); results in
`evidence/mutants.json`:

1. `python_selection_wins`: drop the Lean override in `dispatch.owned`.
2. `admission_report_unbound`: drop the `report_id` binding in `bound_admission`.
3. `definitions_row_unpaired`: accept a Lean definitions row whose premises and generators do not pair.
4. `fill_premises_dropped`: stop sending the norm-defaults fill premises to Lean's replay.
5. `background_route_view`: send the route projection instead of the model projection for Background.
6. `sugar_rejection_to_lean`: send a rejection inside a `definitions@0` sugar production to Lean.
7. `lean_typing_refuses_readings` (Lean): remove the `readings@1` step from `typingReduced`.

The first run of this harness also found a defect: its restored run of `background_route_view` failed, which
showed that premise status and compare over `norm-defaults@0` were outside Lean's countermodel check
(fixed by `entailment.lean_check_scope`, DELTA.md item 6).

## Lines

The generated block above counts lines from the branch's own commits saved in `evidence/scope.json`. The plan
estimated about 2,000 deletable lines; the deletion is smaller because most of the remaining Python in these
operations is not a second decision: the graph, readings, premise-status and compare rules are the compositions
Lean's adapters themselves run over Lean-checked parts, Python's parser constructs the document only after Lean
accepts it, and the retained scope gaps of DELTA.md keep their Python until Lean covers their inputs.
