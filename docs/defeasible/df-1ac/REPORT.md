# df-1ac: the wire, first part (build report)

No DRI signature is reserved: the one delta (trust, DELTA T1) is signed by standing ruling R16. **Size cut, twice**:
this item delivers the view and the document kinds (`defaults-elaborate`, `defaults-coherence`). The question kinds
(`defaults-certificate`, `defaults-model`), the kind-table row, the shapes and the encoder theorems are **df-1ad**
(section 5). The question kinds are already built and proved on branches `wip/df-1ad-question` and
`wip/df-1ad-model`.

Branch `feature/df-1ac`, base main c5197da78. Plan and spec as on main (df-1a's verbatim copies, unchanged here).

**Statement gate.** DF-S passed (`manage-agents/defeasible-p3ver1.final.md`, the review of commit 632bc4ed). The
four statements the task names (`defaults_coherence_sound`, `forcedAt_sound`, `decodeLayered_soften`,
`defaultsCase_other`) are equal in 632bc4ed and on main after whitespace normalisation; spec 7.2 is byte-identical
between the two. None had to change. `evidence/compare_statements.py` compares every spec 7.2 declaration with the
built one, with comments, docstrings and proofs removed:
- HEAD: 20 OK, and 22 MISSING, all of them the question kinds cut to df-1ad (`evidence/statements.out`).
- `wip/df-1ad-model`, which has all four kinds: 42 OK, 0 DIFF.
- The comparator reports DIFF when a `¬` is dropped from `defaults_coherence_sound`.

No text claims minimality (DF-2 is not proved).

## 1. Plan rows delivered

| Row (task deliverables, spec 7.2, 8.1, 8.9) | Delivered | Where |
| --- | --- | --- |
| (1) `DefaultsView`, `ViewRest`, `viewRest` (diagnostics 1, 2, 6, 4), `viewOf` (decoder refusals, then 7), `decodeLayered_soften`, `viewOf_layered` | yes, proved | `Wire.lean` |
| (1) `elaborateRows`, `elaborateRows_eq` | yes | `Wire.lean` |
| (1) `CoherenceReplay`, `PairStatus`, `pairs`, `verdict`, `replayCoherence` (diagnostic 5), `defaults_coherence_sound`, `coherence_collision_shown` (review F1), `coherence_collision_named` (recheck F5) | yes, proved | `Wire.lean` |
| (1) `defaultsCase`, `defaultsCase_other` | yes, for the two document kinds | `Wire.lean` |
| (1) `CertReplay`, `replayCert`, `defaults_follows_gated`, `defaults_certificate_sound` | **df-1ad** (size): built, proved and fixtured on `wip/df-1ad-question` | — |
| (1) `forcedAt`, `ModelReplay`, `replayModel`, `forcedAt_sound`, `defaults_model_sound` | **df-1ad** (size): built and proved on `wip/df-1ad-model` | — |
| (2) the four kinds as one row of PK-1's kind table (DF4) | **df-1ad** (size; see deviation 1) | — |
| (3) shapes and encoder theorems | **df-1ad** (they come with the row) | — |
| (4) DF-θ, wire answers of DF-α, DF-γ, DF-γ′, DF-ω | yes, as `#guard`s through `viewOf` and `defaultsCase` | `WireExamples.lean` |
| (4) wire answers of DF-α′, DF-β, DF-δ′, DF-ε, DF-ζ, DF-ι, DF-κ, DF-η | **df-1ad**: they are certificate and model answers (on `wip/df-1ad-question`) | — |
| Seeded bug `defaults-coherence` COHERENT without a collision | yes (W1) | `mutants.json` |
| Seeded bugs `defaultsCase` without the gate, `forcedAt` `[]` | **df-1ad**: they mutate the question kinds. The first is on `wip/df-1ad-question` and fails DF-γ's gate regression there | — |
| `lean/DEFAULTS.md`, plain words, no minimality claim | yes | `lean/DEFAULTS.md` |
| Generated files through `regen_generated.py --write` | `Audit.lean`, `axioms.txt`, `{statements,predicates,declarations}.txt`; spec table by `tools/assurance_manifest.py --write` | — |

## 2. Deviations (no approved statement changed)

1. **Where the kind row goes (df-1ad).** `Wire.lean` imports `NormDefaults/Layered.lean`, for `LayeredU` and
   `decodeLayered`. So `Layered.lean` cannot hold a row that calls `defaultsCase`. The row, and the table `runLayered`
   dispatches over, must sit in a module after `Wire.lean`. Today `NormDefaults/Run.lean` sends only
   `norm-defaults-*` kinds to `runLayered`, so the routing changes too. The shapes must come in the same item,
   because `runLayered_fits` must keep holding. KindRow matches one kind, so "one row" is one entry of the table's
   construction (`defaultsKinds.map`, as `legacyRows`), needing the `soft` pack.
2. **pk-1b's deviation 3.2 (the choice dispatch), decided here.** A readings choice's inner case
   (`Readings/UnspecifiedWire.lean` `choiceInnerX`) keeps calling `layeredCase`, and the `defaults-*` row is not
   reachable from it. DF-3 folds default answers over choices with its own per-choice semantics (`dSem`, spec 7.4),
   not through an inner `defaults-*` case. `choiceInnerX`'s approved RD-9 text therefore stays unchanged, and
   `kindCase_eq` keeps both dispatches equal on every legacy kind.
3. **DF-θ.** On main the layered decoder refuses `weighing@0` itself ("UnsupportedProfile: Unsupported profile
   weighing@0"). Spec section 5 puts the decoder's refusals before diagnostic 1, so through `viewOf` DF-θ gets that
   refusal. Diagnostic 1's text is checked on `viewRest` with a decoded document. It becomes reachable through
   `viewOf` when the layered decoder accepts weighing documents.
4. **COHERENT on a colliding pair.** Diagnostic 5 needs the request's pair list in `coherence_targets` order, so
   DF-ω's `[]` variant is diagnostic 5 on the wire, and its `[none]` variant is UNKNOWN with the pair `unknown`.
   DF-δ's pair certificate is the untrusted search's (df-1b). DF-γb, which is DF-γ with r1 guarded by `⊥`, gives
   COHERENT with a hand-written certificate bound as a producer binds one. DF-γ2 has two pairs and a two-entity
   tuple, and kills `trust_mutants`' list mutants. DF-γ3 has two pairs that share their second rule, one kept apart by
   its guard (recheck F5).
5. **The wire form (this item's design; df-1b relays it).**
   - Requests: `coherence` is a list of `{"rules": [m, n], "certificate": … | null}`. `collision` is
     `{"model", "filling", "rules": [m, n]}`.
   - The coherence answer: `verdict`, then `pairs` as `[{"rules", "status"}]`, then with COLLISION
     `collision: {"rules", "tuple" (entity ids), "deciders"}`.
   - The situation is the request's own collision model, which the relay binds; it is not echoed.
   - A pair certificate is bound by `bindingOk` to the source environment, to `backgroundBase ++ (Exc_T ++ R ++ Dflt_T)
     ++ Fill_T` and to the pair's `cohPremiseU`. One that does not bind is absent.
6. `defaultsCase` uses `replayCoherenceOn v j` on the view it is given, so the document is not decoded twice.
   `replayCoherence j` is the spec's entry, and is `viewOf j` followed by `replayCoherenceOn`.
7. `docs/defeasible/df-1a/evidence/run_mutants.py` reads a mutants file's `source`, `fixtures`, kept theorems and
   module, instead of a second copy of the runner. On this tree, df-1ab's run is byte-identical to its saved
   `mutants.out`, and df-1a's run is identical to main's runner.

## 3. Evidence

- `lake build` (1,054 jobs): every `#guard` of `WireExamples.lean` passes.
- `python3 lean/audit.py`: PASS (599 source files, standard axioms only).
- `uv run python tools/regen_generated.py --check`: 32 entries, exit 0.
- `uv run python tools/trust_map.py --check`: PASS with the recorded allowance.
- `uv run python tools/gate_collection.py --check --prebuilt`: 18,943 collected; 0 added, 0 removed, 0 refused,
  0 stale, 0 malformed.
- `tools/check_*_statements.py` (4 scripts): PASS.
- Selected tests on the Mac runner: `mac-pytest.sh --select -- --base c5197da78 --run`, HEAD fa21b617, clean.
  76 of 459 units, including `lake build`: **0 failed** (1,529 s).
  - An earlier run, at 199f1a57, failed only `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`.
  - 81bdf255c fixed it by pinning `Wire.lean` as a decoder and classifying its fixture file. That file then passed
    137 tests.
- Pre-existing failures (`main-known-red.txt`): none failed.
- Not run by me: the full gate (the chain runs it on the final HEAD).

## 4. Seeded bugs, trust, size

**Seeded bugs (Lean only).** No Python or Rust product file changed. They are in `mutants.json`, run by
`python3 docs/defeasible/df-1a/evidence/run_mutants.py docs/defeasible/df-1ac/mutants.json`, with the saved run in
`evidence/mutants.out`. The control has 0 failures, and all 12 mutants fail.

| # | File, definition: bug | Fails |
| --- | --- | --- |
| W1 | `Wire.lean`, `CoherenceReplay.verdict`: COHERENT when no collision is supplied (the plan's seeded bug) | DF-ω, DF-γb without its certificate |
| W2 | `PairStatus.label`: resolved shown as collision | DF-γb with its certificate |
| W3, W4 | `coherenceFields`: DE7's deciders dropped; the collision's pair looked up by either name | DF-γ, DF-γ2; DF-γ2 |
| W5 | `elaborateFields`: coherence targets reversed | DF-γ elaborate |
| W6 | `entityIds`: a tuple shown by sort | DF-γ, DF-γ2 |
| W7, W8 | `defaultsCase`: coherence answered as elaborate; an unknown `defaults-` kind answered | DF-α and DF-ω coherence; other kinds |
| W9 | `CoherenceReplay.pairs` without `x.collides &&`: a pair shown `collision` under UNKNOWN (review F1) | DF-δ with an unchecked collision; `coherence_collision_shown` |
| W10 | `coherenceFields` matching `true`, not the verdict: a `collision` member under UNKNOWN (review F1) | DF-δ with an unchecked collision; `coherence_collision_shown` |
| W11 | `CoherenceReplay.pairs` matching the collision's second rule only: a pair that shares one rule shown `collision` (recheck F5) | DF-γ3; `coherence_collision_named` |
| W12 | `coherenceFields`' `find?` on the second rule only: the tuple and deciders of the wrong pair (recheck F5) | DF-γ3; `coherence_collision_named` |

`tools/trust_mutants.py --max-mutants 1000 --allow trust-mutants-allow.json --json trust-mutants.json` exits 0
on the recheck-fix Lean (HEAD 1ed5cc2a9, 1 job on a loaded VM, 5,928 s): 84 killed, 0 survivors, 0 UNKNOWN, 6 allowed. Each allowed mutant writes an empty list that Lean cannot type there.

**Trust** (R16, DELTA T1): V +36, K +0, S +0, all in `Wire.lean`. FOLLOW-UPS "## df-1ac" asks for the ties pass.

**Size.** From `git diff --numstat $(git merge-base HEAD main)`, hand-written lines only. Generated files and tool
outputs (`mutants.out`, `statements.out`, `trust-mutants.json`, `trust-baseline.json`) are left out.

| Kind | Lines |
| --- | --- |
| `Wire.lean` (about 120 of them spec 7.2's text) | 316 |
| `WireExamples.lean` | 157 |
| `run_mutants.py` change | 34 |
| `compare_statements.py` | 36 |
| `mutants.json` (one mutant per line) and the allow file | 29 |
| `DEFAULTS.md` | 31 |
| `trust-classes.json` | 81 |
| assurance manifest | 25 |
| `VE.lean` | 2 |
| DELTA | 15 |
| this report | 188 |

That is about 920 lines in all, above the ~600 guideline (about 880 before the review fix F1, section 7). The first cut (the model kind) left about 1,100 lines, so
the certificate kind was cut too. What is left is the smallest part that holds the view and both document kinds with
their fixtures. About 330 of the lines are fixed costs (ledgers, the manifest pin, the runner change, DELTA and this
report).

## 5. Next items

- **df-1ad**, the question kinds and the route. It covers:
  - `defaults-certificate`, from `wip/df-1ad-question` with its fixtures (DF-α, DF-α′, the strict basis, DF-β's long
    form, DF-γ's gate regression with and without a certificate, DF-ι, DF-κ, DF-η) and its seeded bugs (the gate,
    the `reason` order);
  - `defaults-model`, from `wip/df-1ad-model` (`default_exception`: a well-formed soft document's default rules all
    have an exception), with DF-β (i)'s forced fixture and the seeded bug `forcedAt` `[]`;
  - the kind row, the routing in `Run.lean`, the shapes and the encoder theorems (deviation 1).

  Cut again by size as needed. pk-1c waits on the row.
- Then **df-1b**, the relay and the first pilot number. df-03's baseline (P-1 0 of 3, P-2 SOME ×3) is recorded for
  it. DF-2 comes alongside.

## 6. Pilot bytes

None expected: no CLI path or service mode reaches these definitions yet.

Evidence commit list (`git log --oneline main..HEAD --no-merges`, before this report's commit): fa21b617a, a3d0ff6b3,
6bd8247b0, b08b7dea7, 81bdf255c, 199f1a575, 7f4aa4226, ccf71608f, 02b0fd6dc, d9cd5ed10, 1af3e4388, 1552ab288,
dd18fca56, 5f9b87684.

## 7. Review fixes (`manage-agents/df-1ac-review.final.md`, review of 07db019f1)

| Finding | Fix | Regression test | Commit |
| --- | --- | --- | --- |
| F1 (B): nothing tested what the answer shows of a collision that names a real pair but does not check; two dropped conditions (W9, W10) passed every guard and proof | **Class:** a `collision` status or member shown without a checked collision. DF-δ guard: `collJ L "r1" "r2"` on the holistic document gives UNKNOWN, the pair `unknown`, no `collision` member. New theorem `coherence_collision_shown`: a pair shown `collision` needs `x.collides`, a `collision` member needs verdict COLLISION, and a checked collision means not coherent. `CoherenceReplay.pairs` is now tied to it for the `collision` status (DELTA T1), so "already tied" holds for both statuses it claims | `lean/VE/Defaults/WireExamples.lean` `#guard holds (layered δEnv δR) …`; `mutants.json` W9, W10 (each fails the guard and the theorem, `evidence/mutants.out`); `coherence_collision_shown` (`lean/VE/Audit.lean`) | f484e28cc |

PROBE F1, as the review gives it: before the fix `surviving: [both mutants]` (AssertionError); after it `surviving: []`.
The sweep the review did (the `verdict`, `resolved`, diagnostic 5, limit and kind checks) needs nothing more. W1 to W8
still fail as before.

Evidence after the fix, on HEAD 257158960:
- `lake build` (1,054 jobs) and `python3 lean/audit.py`: PASS (599 files, 6,825 theorems).
- `regen_generated.py --check`: 32 entries, exit 0. `trust_map.py --check`: PASS, trusted +36, unchanged.
- `compare_statements.py`: unchanged (20 OK, 22 MISSING for df-1ad).
- `trust_mutants.py`: 84 killed, 6 allowed, exit 0.
- Selected tests: `mac-pytest.sh --select -- --base c5197da78 --run`, 76 units, **0 failed** (1,554 s).
  Pre-existing failures (`main-known-red.txt`): none failed.

F2 to F4 (C) go to df-1ad, as the review says.

## 8. Recheck fixes (`manage-agents/df-1ac-looprecheck1.final.md`, recheck of 4193af444)

| Finding | Fix | Regression test | Commit |
| --- | --- | --- | --- |
| F5 (B): two more dropped conditions passed every guard and proof: `pairs` and `coherenceFields`' `find?` matched the collision's second rule only. DF-γ2's pairs share their first rule, so no fixture noticed, and `coherence_collision_shown` said only that some collision checked | **Class:** a collision shown on, or with the tuple of, a pair other than the one it names by both rules. New theorem `coherence_collision_named`: a pair shown `collision` is named `w.m`, `w.n` by the collision `w`, and the `collision` member's tuple and deciders are those of a colliding pair `(P, Q)` with `P.name = w.m` and `Q.name = w.n`. So any partial-key lookup in either place breaks a proof, not only the two mutants. DF-γ3 guard (r1 guarded by `⊥`; r1/r3 and r2/r3 share their second rule): a collision on r2/r3 is COLLISION, r1/r3 `unknown`, r2/r3 `collision`, tuple `[e_assistant]`; a collision on r1/r3 is UNKNOWN. W4 (the `||` lookup) now also fails DF-γ3. The only other pair-by-name check in `Wire.lean`, diagnostic 5, compares the whole `[P.name, Q.name]` list. `CoherenceReplay.pairs` is also tied to the new theorem (the budget is unchanged, V +36) | `lean/VE/Defaults/WireExamples.lean` `#guard holds (layered αEnv γ3R) …`; `mutants.json` W11, W12 (each fails the guard and the theorem, `evidence/mutants.out`); `coherence_collision_named` (`lean/VE/Audit.lean`) | 1ed5cc2a9 |

PROBE F5, as the recheck gives it: before the fix `surviving: ['w.n == p.2.name', '(fun p => p.2.name == w.n)']`
(AssertionError); after it `surviving: []`, exit 0. W1 to W10 still fail, each with at least the guards it names.

Evidence after the fix, on HEAD 1ed5cc2a9:
- `lake build` (1,054 jobs) and `python3 lean/audit.py`: PASS (599 files, 6,826 theorems).
- `regen_generated.py --check`: 32 entries, exit 0. `trust_map.py --check`: PASS, trusted +36, unchanged.
- `compare_statements.py`: unchanged (20 OK, 22 MISSING for df-1ad).
- `run_mutants.py docs/defeasible/df-1ac/mutants.json`: control 0 failures, W1 to W12 fail (`evidence/mutants.out`).
- `trust_mutants.py`: 84 killed, 6 allowed, exit 0.
- Selected tests: `mac-pytest.sh --select -- --base c5197da78 --run`, 76 units, **0 failed** (1,503 s).
  Pre-existing failures (`main-known-red.txt`): none failed.

## Self-review against BUILDER-CHECKLIST

1. **Every Lean answer typed and contained.** N.A.: no response shape, schema, relay or service mode changes. The
   kinds are unreachable until df-1ad's row, which comes with their shapes (`regen_generated.py --check`: no schema
   rewritten).
2. **Every required deliverable built.** PASS. Section 1 lists each row with its place, or df-1ad under the task's
   size rule.
   - Diff grep: no Python product file, no Python copy of a Lean decision, no permanent report test.
   - Overlap with in-flight branches: only `lean/VE.lean` (a union) and `tools/trust-classes.json` (own module
     entries).
3. **Tests and gates can fail.** PASS. W1 to W12 cover every trusted definition but a type (`evidence/mutants.out`).
   `trust_mutants.py` exits 0 (`trust-mutants.json`). The control passes.
4. **Python, Lean and Rust agree; valid inputs pass.** N.A.: nothing reaches the new code from Python or Rust. The
   fixtures decode real JSON through `decodeSoftU`, including a two-place act (DF-γ2) and a new party (`operator`).
5. **R8 binding.** N.A.: no relayed field yet (df-1b). On the Lean side, a collision that names its pair reversed is
   no collision (DF-γ's reversed guard: the pair stays `unknown`), and a pair list out of order, too long or too short
   is refused (the diagnostic 5 guard).
6. **Gate evidence matches the final HEAD.** PASS. The base is main c5197da78, the merge base. The chain gates the
   final HEAD. The commit list is from `main..HEAD --no-merges`.
7. **No unsigned item.** PASS: DELTA T1 cites R16 with its evidence.
8. **Every user-visible change in DELTA.** PASS. There is none besides trust: no mode, schema or pin changes
   (`regen_generated.py --check`).
9. **Test selection.** PASS. The selected plan (76 units) includes `lake build`, which elaborates every guard, so W1
   to W12 fail it.
10. **Lean statements say what is claimed.** PASS.
    - `evidence/compare_statements.py`: 20 OK on HEAD, 42 OK on the wip branch.
    - The comparator catches a dropped `¬`.
    - `defaults_coherence_sound` is about the returned verdict and the pairs shown `resolved`;
      `coherence_collision_shown` is about a pair shown `collision` and the `collision` member (review F1);
      `coherence_collision_named` says which pair they are (recheck F5).
11. **Budgets and limits fail closed.** PASS: diagnostic 4 (`limitDiag`) refuses through `viewRest`
    (`WireExamples.lean`, the `deepen` guard). No budget or deadline is added.
12. **No CPU or memory regression.** N.A.: no route runs the new code; no pilot run (L70).
13. **Test-removed trailers.** PASS: `tools/gate_collection.py --check --prebuilt`: 0 added, 0 removed, 0 refused,
    0 stale, 0 malformed.
