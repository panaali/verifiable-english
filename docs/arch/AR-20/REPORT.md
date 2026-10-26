# AR-20: `bind_ok`, the document decoder copies, one `VE/Paths.lean`, and L6

**Built and committed with a clean tree. No DRI signature is needed: DELTA.md has only R7 rows, the trusted base
falls (K −3, S +0, untied V −45; trusted −48), and no kept Lean statement changes. One gap:
`tools/batch_evidence.py --check docs/arch/AR-20` passes every section except `[gate]`**, which can only be saved
after the chain's gate has run; the saved scope, A/B and gate must then name the gated commit and are re-saved in
one commit that touches only `docs/arch/AR-20/` (see "After the gate").

Plan: architecture review 2026-10 (`design/arch-review` 6ae55ebb8), section 4.5, row AR-20 ("4a + L6 + Paths");
batch gate 4.1; coordination 4.2; `docs/CONSOLIDATION-PLAN.md` step 4a; DRI decisions D2 (frozen files) and D3
(trust ratchet). Its gate is met: lf-14a to lf-14d and lf-18 have merged.

## Measured outcome

From `tools/trust_map.py` (`evidence/trust.json`), `tools/lean_statements.py --diff` (`evidence/statements.json`),
`tools/lean_first_diff.py` (`evidence/ab.json`) and `wc -l`, against the merge base `25ac4131`:

- **Trust (D3).** `uv run python tools/trust_map.py --check`: "against 25ac413119c8: K -3, S +0, D -51, G +1,
  tied +0, unclassified +0, trusted -48 ... PASS". K 997 → 994, S 11,497 → 11,497, untied V 42,213 → 42,168,
  trusted 54,707 → 54,659. No allowance was added.

  | File | Lines | K | D[V] | G[V] | D[I] | trusted |
  |---|---:|---:|---:|---:|---:|---:|
  | `VE/SoftNorms/Admission.lean` | 332 → 309 | | −23 | | | −23 |
  | `VE/NormDefaults/Admission.lean` | 367 → 344 | | −23 | | | −23 |
  | `VE/Paths.lean` (new) | 0 → 195 | +15 | | | | +15 |
  | `VE/Core/Paths.lean` | 195 → 87 | −9 | | | | −9 |
  | `VE/Closure/Paths.lean` | 195 → 87 | −9 | | | | −9 |
  | `VE/Route/Budget.lean` | +1 | | | +1 | | +1 |
  | `VE/CertificateWire.lean` | 312 → 321 | | | | −5 | 0 |
  | `VE/Kit/Except.lean` (new) | 0 → 11 | | | | | 0 (P) |
  | **Total** | | **−3** | **−46** | **+1** | **−5** | **−48** |

  Against the plan's expectations: part 2 removes D −46, not the plan's "about −67" (its "D 26" and "D 41" were
  measured before; `trust_map.py` counted 28 lines for each copy on main, and each name keeps a 5-line delegating
  definition because approved theorems state it). Paths removes K −3 and 21 lines, not "one 195-line file": the
  two old modules keep every name as an abbreviation or a corollary that restates its statement (87 lines each,
  P and C apart from 6 K lines), since the plan requires identical statements. L6's encoders are D[I], which the
  trusted count does not include; the guards added for L6 are T.
- **Lean statements (4.1 item 3).** `lean_statements.py --diff` against the base: 15 added (`VE.Kit.Except.bind_ok`
  and 14 `VE.Paths.*` theorems), 0 removed, 0 changed. Deleting the added entries from the head's
  `statements.txt` and `predicates.txt` gives the base's files byte for byte (`kept_byte_identical: true` for
  both). `predicates.txt` adds only `module VE.Kit.Except`, `module VE.Paths` and the four `VE.Paths` predicates.
- **Behaviour (4.1 item 2).** `tools/lean_first_diff.py` over all nine corpora, base `25ac4131` from its own
  worktree and head from this checkout: **0 differences** — 100,460 records identical and 22 unavailable on both sides with identical outputs (R7); the base and head recordings are byte-identical (SHA-256 `b0f82720…` for both, `evidence/ab.json`). A pilot branch, `udhr-20261026T1800Z`, was published during the run: its 4 documents were recorded on both sides the recorder's way with its 600 s limit (`pilot_rerun.py`, `evidence/new-pilots.json`) and added to both recordings: 3 identical answers, and the whole-UDHR document timed out on both sides. Before the merge of main, the same A/B against `f1943fab` gave 100,457 identical and 21 R7 pairs, recordings byte-identical too. Every unavailable pair is listed under
  R7 (`evidence/ab-delta.json`, DELTA.md).
- **Audit.** `python3 lean/audit.py` (in `regen_generated.py --check`): "PASS: 620 source files; 7058 named theorem
  declarations audited ...; only the declared standard axiom allowlist." No new axiom: the 15 added theorems use
  at most `propext` and `Quot.sound` (`lean/axioms.txt`).

## The four parts

1. **`bind_ok`** (`85101d91`). `lean/VE/Kit/Except.lean` holds the one proof. `VE.Order.ProfileGate.bind_ok` and
   `VE.Readings.Wire.bind_ok` keep their statements and delegate to it, so no call site changes.
   `VE.Readings.Lines.bind_ok_right` (a different statement) is untouched.
2. **The document decoders** (`f289e2645`). Compared line by line with `VE.Route.Admission.decodeDoc`: the same
   checks in the same order with the same messages and limits (unit count 10,000, duplicate unit id, sorted spans,
   duplicate lemma, open terms, duplicate reading set version, narrowings), the same helpers (`require` is
   `Gate.require` through `Admission.require`), and the same result; they differ only in their environment, data
   flag and route vocabulary, which `decodeDoc` already takes. So neither is kept as a variant, and there is no
   follow-up difference to report. `decodeSoftDoc src j = decodeDoc src.se.ne.rv (src.se.profiles.contains "data@0")
   j (envPrime src.D)`, `decodeFilledDoc s j = decodeDoc s.src.ne.rv (s.src.ne.profiles.contains "data@0") j
   (fill s.U).E`; the theorems that mention the old names keep their statements. No wire-contract hook names
   either decoder.
3. **Paths** (`458a9846`, `8f78e9e8`). `VE/Paths.lean` is the Core copy with the namespace `VE.Paths`. The two
   old modules declare every old name: `Path`, `Reachable`, `ClosedAt`, `dedup`, `pivot`, `warshall`,
   `vertices`, `reachEval` and `Kind.plus`/`Kind.star` (with `@[match_pattern]`) as abbreviations, `Path.below` too
   (so `predicates.txt` keeps it), and every theorem as a corollary with the identical statement.
   `Kind` is a plain `def` alias with its own `DecidableEq`, `BEq` and `Repr` instance names: as an `abbrev`, the
   Core and Closure kinds shared one instance, and six kept statements (`Route.Budget.body_value(N)`,
   `named_value(N)`, `Route.Closure.reachValue_closure`, `reachValue_core`) named `VE.Paths.instDecidableEqKind`
   in their `uses` and `expr` lines. With the `def`, they are byte-identical. Proof-only edits where a proof
   unfolded the alias: `simp` sets add `VE.Paths.Reachable` (Core and Closure `Substitution`, `Closure/Order`,
   `Route/Closure`), `rw` uses `VE.Paths.Path.unfold`, `PathRules` calls `Path.first hp` and `.edge h`, and
   `Route/Budget` derives `Hashable` once for `VE.Paths.Kind` with one named instance per alias (hash values
   unchanged: the derived hash does not read the type's name). `VE.Paths` and `VE.Kit.*` are layer 1
   (`tools/layer_policy.py`; `check_lean_imports.py` refuses `VE.Core.Paths → VE.Paths` otherwise, M7).
4. **L6** (`f1f4b3b1`, `2d4d3f75`). `canonicalWith (null)` holds the cases once; `canonical := canonicalWith
   (throw "null is not in certificate wire format")` and `documentCanonical := canonicalWith (pure "null")`.
   `canonical`'s type is unchanged and it gives the same result on every input: the old `documentCanonical`
   recursed with itself through arrays and objects and called `canonical (fuel+1)` for the scalars, which is
   `canonicalWith`'s behaviour with the null case as a parameter. Evidence: guards after the decoders pin both
   encoders' bytes (null at depth, UTF-16 key order, escapes), the certificate's null refusal and the depth
   limit, and the same guards hold for main's definitions (`lake env lean` against the base build); and
   `canonical_equiv.lean` runs main's two definitions, copied verbatim, against the new ones on 50 generated JSON
   values at 6 fuels, results and errors included: "50 inputs x 6 fuels: 300/300 agree"
   (`evidence/canonical-equiv.txt`).

## Plan rows and directives

| Directive | Delivered by | Test or evidence |
|---|---|---|
| `bind_ok` to `VE/Kit/Except.lean`, both old names as aliases with the identical statement | `85101d91` | statements.json (both old entries byte-identical); M1 |
| `decodeSoftDoc`, `decodeFilledDoc` call `decodeDoc` with the same environment and data flag; compared line by line first; old names stay defined | `f289e2645` | part 2 above; `test_admission_refuses_each_document_check_of_w2s_decoder`, `test_admission_document_checks_are_w2s_decoder_in_both`; M2, M3, M8, M9 |
| One `VE/Paths.lean`; both old modules re-export it; every old name resolves with the identical statement | `458a9846`, `8f78e9e8` | statements.json (0 changed; the predicates keep `Path.below`); M4, M7 |
| L6: `documentCanonical` reuses `canonical`'s cases, byte-identical output; stop if `canonical` must change | `f1f4b3b1`, `2d4d3f75` | `canonical`'s type and outputs unchanged (guards, canonical-equiv.txt); M5, M6 |
| `statements.txt`, `predicates.txt` byte-identical for kept names; diff only adds `VE.Kit`/`VE.Paths` names | `d62767c5`, the merge `b10992ca` | `evidence/statements.json` |
| `lake build`, `lean/audit.py`, axiom audit pass, no new axiom | | "Audit" above |
| Frozen list, inventories, trust classes, audit manifests, pins only through `regen_generated.py --write` | `d62767c5`, `2d4d3f75`, merge | `regen_generated.py --check`: "checked 33 entries", PASS. `tools/trust-classes.json` has no writer (`trust-tables [json]`, "write: -"): its new entries give `VE/Paths.lean` Core/Paths' former classes, each alias the class of the name it keeps, `canonicalWith` D[I] like `canonical`, `refusal` T. `--seed` against the draft trust map reclassified unrelated modules, so it was not kept |
| `ve/assurance-manifest.json` through its own entry; its check passes | `d62767c5`, `2d4d3f75` | its entry is hand-reviewed pins ("write: -", check `check_assurance_pins()`): the four decoder files repinned, ranges reviewed (CertificateWire's two ranges move by −5 lines; the guards sit after them), total 37,804 → 37,752; `tests/test_assurance_manifest.py`: 137 passed |
| Rebuild and repin (`rust_build.py --check`, `lean/checkers.lock`) | | `python3 tools/rust_build.py --check`: pinned; `checker-pins` regenerated |
| `lean_first_diff.py` over the gate corpora, 0 differences | evidence | `evidence/ab.json` |
| D3: K, S, untied V each unchanged or lower, no allowance | | "Trust" above |
| Seeded bugs per part in the one remaining owner, failing for every route that used the deleted copy | `docs/arch/AR-20/mutants.json` | 9/9 killed, `evidence/mutants.json` |
| D4: no report test, no per-batch mutant script; `evidence.toml`; evidence under 1 MB | `docs/arch/AR-20/` | the two new tests check route behaviour, not batch numbers; mutants run by `tools/mutants.py`; largest evidence file 15 KB; the recordings stay in `~/.cache/ve-ar20-ab2/` (about 100 MB each), their SHA-256 in `ab.json` |
| Coordination | | see "Coordination" |
| Never weaken a check or delete a distinct test | | `gate_collection.py --check --prebuilt`: 2 added, 0 removed, 0 refused, 0 stale, 0 malformed |

## Seeded bugs

`docs/arch/AR-20/mutants.json`, run in a separate worktree at `f355c3ff` (the merge of main changes none of the
mutated files: each row's `source_sha256` equals the file at the head) by `uv run python tools/mutants.py
docs/arch/AR-20/mutants.json --evidence docs/arch/AR-20/evidence/mutants.json`: **9/9 killed**, each with a
passing baseline. Lean: M1 to M6, M8, M9; Python: M7 (`tools/layer_policy.py`). No Rust changed.

The service mutants (M2, M3, M8, M9) rebuild `ve_service`, pin the mutant's build in `lean/checkers.lock` for
the run and restore the lock (a mutant that does not build or cannot be pinned exits 0, so it would show as a
survivor, never a kill). The Lean-check mutants fail at a theorem or a guard, never at syntax.

| Id | File | Bug | Fails |
|---|---|---|---|
| M1 | `lean/VE/Kit/Except.lean` | the owner drops `f a = .ok b` | the alias `VE.Order.ProfileGate.bind_ok` no longer type-checks (Companions' alias is in a module that imports it) |
| M2 | `lean/VE/Route/Admission.lean` | `decodeDoc` drops the duplicate unit id check | `test_soft_norms_lean.py::test_admission_refuses_each_document_check_of_w2s_decoder` and `test_norm_defaults_three_way.py::test_admission_document_checks_are_w2s_decoder_in_both` |
| M3 | `lean/VE/Route/Admission.lean` | `decodeDoc` drops the sorted-span check | the same two tests |
| M4 | `lean/VE/Paths.lean` | `reachEval` tests reflexivity for `plus` | `VE.Paths.reachEval_iff` (of which the Core and Closure `reachEval_iff` are corollaries) |
| M5 | `lean/VE/CertificateWire.lean` | `canonical` accepts JSON null | the two null-refusal guards |
| M6 | `lean/VE/CertificateWire.lean` | `canonicalWith` writes `, ` between array items | the byte guards of both encoders |
| M7 | `tools/layer_policy.py` | `VE.Paths` drops to layer 2 | `python tools/check_lean_imports.py`: "new outward Lean import: VE.Core.Paths -> VE.Paths" |
| M8 | `lean/VE/SoftNorms/Admission.lean` | `decodeSoftDoc` passes `false` as the data flag | `test_admission_refuses_each_document_check_of_w2s_decoder` (`$string` under `data@0`) |
| M9 | `lean/VE/NormDefaults/Admission.lean` | `decodeFilledDoc` passes `false` as the data flag | `test_admission_document_checks_are_w2s_decoder_in_both` |

## Trust mutants (checklist 13a)

R16 covers trusted growth; this batch has none, so 13a does not apply. It was still run (`mac-pytest.sh
--trustmut`, which fell back to the VM because both Mac slots were busy; `evidence/trust-mutants.json`, at
`2d4d3f75` with the tests of `9d937101`, Lean as at the head): 23 mutants of the 7 trusted definitions on changed
lines, 0 killed by a Lean check, 18 survivors, 5 unknown (type errors). They fall in two classes:

- the data flag of `decodeSoftDoc` and `decodeFilledDoc` (10): no Lean check reads it, and the route tests now do
  (`c367dd08`; M8, M9 kill a constant flag). The tool builds Lean checks only, so it cannot see them.
- `VE.Paths.Reachable` and the two `Reachable` aliases (8): a K predicate moved verbatim, whose meaning only proofs
  pin (`reachEval_iff`, `star_least`); the tool counts no proof as a kill. Not allowed (`--allow` is for
  equivalent mutants, and these are not); listed as follow-up 1.

## Tests run

- Selected tests (`mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`), before the merge of main,
  on ve-mac-1 at `2d4d3f75`: every unit selected (`tools/layer_policy.py` changed); 2 failed, both from this
  batch and both fixed in `f355c3ff`: `test_consolidation_tools.py::test_committed_ledger_names_real_declarations`
  (the plan quotes the ledger's measured rows 3 and 4: 30 and 691 now; the whole file then passed, 288) and
  `test_wire_gate_corpus.py::test_gate_corpus_holds_every_test_input_of_every_unit` (the new soft test's two
  sources recorded by `python -m conformance.wire_contract_gate --record-test-inputs`; the file then passed, 8).
  After the merge of main: on ve-mac-1 at `b10992ca` (plus the uncommitted `docs/arch/AR-20/`): 375 units, 0 failed, exit 0 (3,451 s).
- The two new tests and the tests each mutant names; `tests/test_assurance_manifest.py` (137 passed).
- `gate_collection.py --check --prebuilt`: "2 added, 0 removed by a trailer, 0 refused, 0 stale and 0 malformed".
- Not run here, per the task: the full gate (`tools/gate.py`), which the chain runs on the final HEAD.

## Coordination

At the start, the hand-written files of the four parts were checked against `git diff --name-only main...<branch>`
for every branch in flight (`lean-first/*`, `feature/*`, `infra/*`, `foundation/*`): no overlap. At the end, over
the whole diff: the branches in flight (`feature/ap-1f`, `ap-3`, `df-1ae`, `jt-2`, `q1-4`, `qt-a3`, `sc-1b`,
`foundation/me-1`, `infra/arch-20261026-1`, `infra/arch-AR-1`) share only generated inventories (`Audit.lean`,
`axioms.txt`, `statements.txt`, `predicates.txt`, `declarations.txt`, `checkers.lock`, `frozen-sources.sha256`,
`docs/spec/assurance-manifest.md`; R12) and the two merge-driver tables `tools/trust-classes.json` and
`ve/assurance-manifest.json` (a merge keeps each side's entries and pins). `foundation/me-1` edits
`tools/consolidation-ledger.json`, so this batch updates only the figures the plan quotes, not the ledger. Main
moved during the build (me-2b, eff-20261026-1, speed-tmchecks); it was merged in `b10992ca` with
`regen_generated.py --resolve`, and the A/B, statements and trust evidence were re-measured against the new merge
base `25ac4131`.

## Follow-ups (not in this batch)

1. `VE.Paths.Reachable` (K) has no evaluable check: a trust-mutant run reports its mutants as survivors because only
   proofs refute them. A decidable form or a `#guard` over `reachEval` with its iff would let the tool see them.
2. The `--record-test-inputs` run (52 min at load 70) also rewrote `conformance/wire-contract/soft-norms@0-gate.json`
   with many "function record or message differs" boundary problems across faults this batch does not touch; the
   file was left as main's, and the wire-gate tests pass with it. Whether that rewrite reproduces on main on an
   idle machine is unverified.
3. The whole-UDHR pilot records time out at 600 s on both sides (L75); a concurrent re-run of the first A/B's 7
   (base `f1943fab`) with 2,400 s also timed out on both sides at load 50 to 70 (`evidence/pilot-rerun.json`).
4. Step 4b can delete the delegating `decodeSoftDoc` and `decodeFilledDoc` only by restating the theorems at
   `SoftNorms/Admission.lean` and `NormDefaults/Admission.lean` that mention them, which changes approved statements.
5. AR-23 makes the Closure Paths names aliases of Core's; with `VE.Paths` the Core names can become the shared
   module's directly and the alias module of Closure can go, if the statements that print `VE.Closure.Kind.*` are
   re-approved.

## After the gate

The scope, the A/B and the gate must name the commit the chain gates (`<G>`). After the chain's gate of `<G>`,
make one report commit that changes only `docs/arch/AR-20/`:

    cp gate-result.json docs/arch/AR-20/evidence/gate.json
    uv run python -m tools.evidence scope --base main --head <G> --out docs/arch/AR-20/evidence/scope.json
    uv run python -m tools.evidence ab ~/.cache/ve-ar20-ab2/base-with-new-pilots.jsonl \
        ~/.cache/ve-ar20-ab2/head-with-new-pilots.jsonl \
        --base-commit 25ac413119c8991d1385cc95c51bcaac7415f9a2 --head-commit <G> \
        --out docs/arch/AR-20/evidence/ab.json --delta docs/arch/AR-20/evidence/ab-delta.json
    uv run python tools/batch_evidence.py --check docs/arch/AR-20 --report-commit HEAD

The head recording was made at `b10992ca` (the merge of main). From there to `<G>`, `ve/`, `lean/`, `rust/` and
`tools/lean_first_diff.py` are unchanged (`git diff --stat b10992ca <G> -- ve lean rust tools/lean_first_diff.py` is
empty); the commits after it change only `docs/arch/AR-20/`.

## Self-review against BUILDER-CHECKLIST

1. Every Lean answer typed and contained: N.A. No relay, response schema or binding changed; the routes' rows are
   byte-identical in the A/B (`evidence/ab.json`).
2. Every deliverable built, no rule broken: PASS. "Plan rows and directives" maps each row to its commit and
   evidence. No Python copy of a Lean decision, no report test (the new tests check route behaviour), no authority
   switch; overlaps under "Coordination".
3. Tests can fail: PASS. 9/9 seeded mutants killed, one or more per part and per language changed
   (`evidence/mutants.json`); the trust-mutant run is in "Trust mutants".
4. Python, Lean and Rust agree; valid inputs pass: PASS. Corpus A/B over nine corpora, 0 differences, recordings
   byte-identical (`evidence/ab.json`); `canonical-equiv.txt` 300/300.
5. R8 binding: N.A. No field Python reads from a Lean answer changed.
6. Gate evidence matches the final HEAD: N.A. here; the chain gates the final HEAD, "After the gate" re-saves the
   scope, A/B and gate for it. Synced with main (`b10992ca`); the scope base is the merge base `25ac4131`.
7. No unsigned item: PASS. DELTA's two rows cite R7; trust −48 with no allowance (`trust_map.py --check` PASS).
8. Every user-visible change in DELTA: PASS. The A/B diff is empty; the only listed records are R7 pairs.
9. Test selection finds the tests: PASS. The selection ran every unit (`tools/layer_policy.py` is a policy file),
   and it found the two failures above.
10. Lean statements say what is claimed: PASS. No new statement beyond the moved `VE.Kit`/`VE.Paths` copies;
    `lean_statements.py --diff`: 0 changed; each alias's statement is checked by Lean against its owner (M1, M4).
11. Budgets and limits fail closed: N.A. No budget or limit changed; the depth limit of both encoders is guarded.
12. No CPU or memory regression: PASS. Aliases are abbreviations (the compiled code calls the same functions);
    the A/B recorded the same 100,478 records on both sides with byte-identical output.
13. `Test-removed` trailers: N.A. No test removed or renamed (`gate_collection.py --check --prebuilt`: 0 removed).
