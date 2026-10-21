# df-1ad: the question kinds (build report)

No DRI signature is reserved: the one delta (trust, DELTA T1) is signed by standing ruling R16. **Size cut:** this
item delivers deliverables (1) `defaults-certificate` and (2) `defaults-model`. Deliverable (3), the kind-table row,
the routing in `NormDefaults/Run.lean`, the shapes and the encoder theorems, is **df-1ae** (section 5).

Branch `feature/df-1ad`, base main 7855620f3 (the merge base). Plan and spec as on main (df-1a's verbatim copies,
unchanged here).

**Where the code came from.** `wip/df-1ad-question` (81bdf255c) and `wip/df-1ad-model` (5f9b87684) are both ancestors
of main: df-1ac's later commits b08b7dea7 and dd18fca56 cut the two kinds. So nothing could be merged. I restored the
kinds by applying those two commits' Lean changes in reverse. Then I resolved them against df-1ac's review fixes
(`coherence_collision_shown`, `coherence_collision_named`, DF-γ3). I also restored `βEnv`/`βR`, which 6bd8247b0 had
dropped as unused.

**Statement gate.** DF-S passed (`manage-agents/defeasible-p3ver1.final.md`). `docs/defeasible/df-1ac/evidence/
compare_statements.py` on this HEAD gives **42 OK, 0 not OK** (`evidence/statements.out`), the same as on
`wip/df-1ad-model`. No statement changed. No text claims minimality (DF-2 is not proved).

## 1. Plan rows delivered

| Row (task deliverables; spec 7.2, 8.1, 8.9) | Delivered | Where, test |
| --- | --- | --- |
| (1) `CertReplay`, `replayCert`, `defaults_follows_gated`, `defaults_certificate_sound` | yes, proved | `Wire.lean` (efdc90293); `lean/VE/Audit.lean` |
| (1) DF-α, DF-α′ (two forms), the strict basis, DF-β long, DF-ι, DF-κ (two forms), DF-η | yes, `#guard`s | `WireExamples.lean` "`defaults-certificate`" |
| (1) DF-γ's gate regression with and without a certificate, with and without a collision | yes | `γCase` guards |
| (1) Seeded bugs: `defaultsCase` without the gate; the `reason` order | yes (Q1, Q2) | `mutants.json` |
| (2) `forcedAt`, `ModelReplay`, `replayModel`, `forcedAt_sound`, `defaults_model_sound` (`default_exception`) | yes, proved | `Wire.lean` (a9784975b) |
| (2) DF-β (i)'s forced fixture (`forced = [(r1, 0, a)]`) and DF-α's default model (`forced = []`, DE6) | yes | `WireExamples.lean` "`defaults-model`" |
| (2) Seeded bug `forcedAt` `[]` | yes (M1) | `mutants.json` |
| (3) The four kinds as one entry of the layered kind table, the routing in `Run.lean`, shapes, encoder theorems | **df-1ae** (size) | section 5 |
| df-1ac review F2–F4 (C, sent to df-1ad) | F3 (the wire form) goes to df-1ae with the shapes. F2's survivors fail closed (C). F4 is the size | section 5 |

## 2. Deviations (no approved statement changed)

1. **Two more fixtures.**
   - DF-β2 has two default rules, r1 with two stated conditions (`calm`, then `urgent`), at two assistants. It kills
     the 16 list mutants of `forcedAt` and `modelFields` that `trust_mutants.py` found surviving against
     single-rule, single-entity fixtures.
   - DF-δ on the certificate kind sends a collision that names the pair but does not check. That is df-1ac review
     F1's class on the new kind: a `reason` matching `true` in place of `x.collides` passed every guard before it
     (Q8).
2. **The "other kinds" guard** now lists `defaults-other` and `norm-defaults-elaborate`, because both question kinds
   now answer. df-1ac's saved W8 names the old guard's first line. Rerun on this tree, W8 still fails the renamed
   guard, but the runner's prefix match reports it as SURVIVES (`evidence/df-1ac-mutants-rerun.out`, saved). All
   other df-1ac mutants fail as recorded. df-1ac's saved evidence is left unchanged.

## 3. Evidence

- `lake build` (1,061 jobs): every `#guard` passes. `python3 lean/audit.py`: PASS (606 files, 6,967 theorems).
- `regen_generated.py --check`: 33 entries, exit 0. `trust_map.py --check`: PASS with the R16 allowance.
- `tools/check_*_statements.py` (4): exit 0. `gate_collection.py --check --prebuilt`: 19,256 collected; 0 added,
  0 removed, 0 refused, 0 stale, 0 malformed.
- Selected tests on the Mac: `mac-pytest.sh --select -- --base 7855620f3 --run`, HEAD 5efff76b2: 76 units, including
  `lake build`, **0 failed** (1,405 s). Pre-existing failures (`main-known-red.txt`): none failed.
- Not run by me: the full gate (the chain runs it on the final HEAD).

## 4. Seeded bugs, trust, size

**Seeded bugs (Lean only;** no Python or Rust product file changed). They are listed in `mutants.json` and run by
`python3 docs/defeasible/df-1a/evidence/run_mutants.py docs/defeasible/df-1ad/mutants.json`. The saved run is
`evidence/mutants.out`: control 0 failures, all 13 fail.

| # | `Wire.lean` definition: bug | Fails |
| --- | --- | --- |
| Q1 | `CertReplay.verdict`: FOLLOWS without the gate (plan) | DF-γ's gate regression, with and without a collision |
| Q2 | `CertReplay.reason`: the certificate tested before the collision (plan, spec 8.9) | DF-γ without a certificate |
| Q3, Q4 | `basisLabel`: needs shown strict; `formLabel`: short shown long | DF-α, DF-β; DF-α, DF-α′, strict |
| Q5, Q6 | `certFields`: assumptions dropped; `CertReplay.form` with no kept assumption | every FOLLOWS; DF-β long |
| Q7 | `defaultsCase`: certificate answered as coherence | 13 certificate guards |
| Q8 | `CertReplay.reason`: an unchecked collision given as the reason | DF-δ certificate |
| M1, M2 | `forcedAt`: `[]` (plan); the condition index replaced by the count | DF-β (i), DF-β2 |
| M3, M4 | `ModelReplay.verdict` without the check; `modelFields`: `forced` under UNKNOWN | DF-β {excepted}, the empty domain |
| M5 | `defaultsCase`: `defaults-model` unanswered | DF-β (i), DF-β2, DF-α's default model |

`trust_mutants.py --max-mutants 1000 --allow trust-mutants-allow.json` (Mac, HEAD 9ec298b54) gives 55 killed,
0 survivors, 0 UNKNOWN and 25 allowed, exit 0 (`trust-mutants.json`). Each allowed mutant does not elaborate: an
Option, or a field list that loses its expected type. Every list mutant that elaborates is killed.

**Trust** (R16, DELTA T1): V +37, K +0, S +0, all in `Wire.lean`. FOLLOW-UPS "## df-1ad" asks for the ties pass.

**Size** (`git diff --numstat 7855620f3`, hand-written only):

| File | Lines |
| --- | --- |
| `Wire.lean` | 328 (about 300 of them spec 7.2's text and its proofs, restored) |
| `WireExamples.lean` | 118 |
| `DEFAULTS.md` | 35 |
| `trust-classes.json`, `ve/assurance-manifest.json` | 79 |
| `mutants.json`, allow file | 49 |
| DELTA, this report | 161 |

That is about 770 lines, above the ~600 guideline. I measured after (2), which was restored code rather than new
work, and cut (3) there. With the certificate kind alone, the item would have been about 560 lines, and df-1ae would
carry the model kind as well as the row, the routing, the shapes and the encoders.

## 5. Next items

- **df-1ae**, the route:
  - the four kinds as one entry of the layered kind table's construction (`defaultsKinds.map`, as `legacyRows`, with
    the `soft` pack), in a module after `Wire.lean` (df-1ac deviation 1);
  - the routing of `defaults-*` kinds in `NormDefaults/Run.lean`, the response shapes and the encoder theorems, so
    that `runLayered_fits` keeps holding;
  - settling df-1ac review F3's wire points with the shapes: COLLISION without the situation, DF-ω's `[]`,
    `"coherence": null`, and a collision naming an undeclared rule.

  pk-1c waits on the row.
- Then **df-1b**, the relay and the first pilot number (df-03's baseline: P-1 0 of 3, P-2 SOME ×3). DF-2 comes
  alongside.

## 6. Pilot bytes

None expected: no CLI path or service mode reaches these definitions until df-1ae's row.

Evidence commit list (`git log --oneline main..HEAD --no-merges`, before this report's commit): 5efff76b2,
9ec298b54, 956f4d4cd, 73853ce43, 13e7af426, 54dd2de8e, a9784975b, efdc90293.

## Self-review against BUILDER-CHECKLIST

1. **Lean answers typed and contained.** N.A.: no shape, schema, relay or mode changes (df-1ae). `regen_generated.py
   --check` rewrites no schema.
2. **Every deliverable built.** PASS. Section 1 gives each row its commit and guard, or df-1ae under the size rule. A
   diff grep finds no Python product file and no permanent report test. Overlap with in-flight branches is limited to
   the shared ledgers `tools/trust-classes.json` and `ve/assurance-manifest.json` (own entries), plus generated files
   (R12).
3. **Tests can fail.** PASS. Q1–Q8 and M1–M5 (`evidence/mutants.out`) cover at least one per trusted definition.
   `trust_mutants.py` exits 0 (`trust-mutants.json`). The control passes.
4. **Python, Lean and Rust agree.** N.A.: nothing reaches the new code from Python or Rust. Fixtures decode real JSON
   through `decodeSoftU`, including two conditions and two entities (DF-β2).
5. **R8 binding.** N.A.: no relayed field yet (df-1b). On the Lean side, a certificate bound to another premise list is
   absent (DF-κ's second guard), and diagnostic 3 refuses a decision premise (DF-η).
6. **Gate evidence matches the final HEAD.** PASS. The base is the merge base 7855620f3, the commit list comes from
   `main..HEAD --no-merges`, and the chain gates the final HEAD.
7. **No unsigned item.** PASS: DELTA T1 cites R16 with its evidence.
8. **Every user-visible change in DELTA.** PASS. There is none besides trust: no mode, schema or pin changes
   (`regen_generated.py --check`).
9. **Test selection.** PASS. The plan's 76 units include `lake build`, which elaborates every guard, so every Q and M
   mutant fails it.
10. **Statements say what is claimed.** PASS. `compare_statements.py` gives 42 OK. `defaults_certificate_sound` is
    about `x.verdict`, `x.basis` and `x.assumptions`, the values `certFields` shows. `forcedAt_sound` and
    `defaults_model_sound` are about `x.ok` and `x.forced`, the values `modelFields` shows.
11. **Budgets fail closed.** PASS: no budget or deadline is added. With no model or certificate the answer is UNKNOWN,
    never FOLLOWS (`#guard answer (αCase notExc cNeeds.trace [])`, DF-κ). With no checked countermodel it is
    UNKNOWN, never DOES-NOT-FOLLOW (the empty-domain guard, M3).
12. **No CPU or memory regression.** N.A.: no route runs the new code; no pilot run (L70).
13. **Test-removed trailers.** PASS: `gate_collection.py --check --prebuilt`: 0 added, 0 removed, 0 refused, 0 stale,
    0 malformed.
