# kb-9a: the round trip of the route's formula codec (build report)

DRI signatures needed: none. DELTA: none (no executable, decoder, encoder, Python or Rust change; no DELTA row). FOLLOW-UP: none.

SIZE: 371 product (lean/VE/Route/CodecRoundTrip.lean, proofs and statements), 33 tests (its `#guard` section), 80 other hand-written lines (lean/VE.lean 1, ve/assurance-manifest.json 1, docs/kernel/kb-9a/seeded-bugs.json 78), plus this report. Generated: lean/VE/Audit.lean, lean/axioms.txt, lean/declarations.txt, lean/predicates.txt, lean/statements.txt, docs/kernel/kb-9a/trust-mutants.json.

Commits (`git log --oneline --no-merges main..HEAD`): a797b63cae (module), 3c13fd66ea (inventories), 83c613043f (assurance manifest), d8f3b9a5ce (counterexample guards, inventories), 168123b51b (seeded bugs and trust-mutants record), then this report.

## What is proved (lean/VE/Route/CodecRoundTrip.lean, namespace VE.Route.Wire)

(1) `decodeClosed_encodeFormula (E φ data) (hCheck : φ.check E [] = true) (hDepth : VE.Surface.formulaDepth φ < VE.Limits.maxDepth) (hNodes : VE.Bridge.formulaNodes φ ≤ VE.Limits.maxNodes) (hData : data = true → usesStringBinder φ = false) : decodeClosed E (encodeFormula φ) data = .ok φ`. Corollary `decodeClosed_encodeFormula_wellFormed`: the same with `hWellFormed : φ.WellFormed E []` (through `VE.check_iff_wellFormed`).

(2) `decodeFormulas_encode (E fs data) (hCheck : ∀ φ ∈ fs, φ.check E [] = true) (hDepth : ∀ φ ∈ fs, formulaDepth φ < maxDepth) (hNodes : (fs.map formulaNodes).foldl (· + ·) 0 ≤ maxNodes) (hData : data = true → ∀ φ ∈ fs, usesStringBinder φ = false) : decodeFormulas E (Json.arr (fs.map encodeFormula).toArray) data = .ok fs`, and `decodeFormulas_encode_wellFormed`. `hNodes` is the list-level limit, in the decoder's own form (`nodeLimit`'s fold); `AstLimit.check` applies the same bound across the list.

Each hypothesis is named after its gate and is the decoder's own bound, not a weaker one:
- `hDepth`: `decodeClosed_refuses_depth` and `decodeFormulas_refuses_depth` (theorems, by `rfl`): the chain of `maxDepth` negations over `⊤` (`depth_negationChain`: its `formulaDepth` is exactly `maxDepth`) is refused with `AstLimit.depthLimit`. Seed S3 shows `<` cannot become `≤`.
- `hNodes`, `hCheck`, `hData`: `#guard`s at the end of the module, each breaking that hypothesis only (a 16,383-node conjunction; two 8,191-node formulas, each within the limit, refused together; an unbound variable; a `$string` binder in an environment that declares the sort, refused on a data route and read back on any other). A node-limit theorem by `rfl` costs about 77 s of kernel evaluation (measured with a scratch file), so it is a `#guard`.

Helpers (all theorems, P by kind): `decodeTerm_encodeTerm`, `decodeFormula_encodeFormula` (any fuel above the depth), `walk_encodeTerm`, `walk_encodeFormula` (AstLimit.walk counts exactly `formulaNodes` and reports no limit), `foldlM_walk_encode`, `astLimit_check_encode`, `mapM_decodeFormula_encode`, and one-step unfoldings of `AstLimit.walk` proved by `rfl` (`walk_var`, `walk_const`, `walk_leafNode`, `walk_unaryAtom`, `walk_pairAtom`, `walk_unaryNode`, `walk_binaryNode`, `node_step`, `term_step`, `walk_bind`, `ok_bind`, `foldl_add`, `encodeFormula_arr`). No definitions were added. The module builds in about 3 s. A first version took 70 s because simp reduced `walk`'s and `decodeFormula`'s matches; the `rfl` unfoldings replaced that.

## Deliverable (3): hypotheses the soft route's premises do not obviously satisfy

The statement was not weakened. To use (2) for the premises a soft-elaborate answer carries (`PremisesField D`: the encodings of `elaborate (soften D).T`, kb-7), kb-9 needs, for `fs = elaborate (soften D).T` in the environment `E` the route decodes them in:
- `hDepth` and `hNodes`: no theorem gives these yet. The likely source is `WellFormedSoft D` (`lean/VE/SoftNorms/Soften.lean`, `validateSoft`): 6.12 checks `withinLimits (elabPremise (soften D).T r)` for each layer symbol (:660), and 6.15 checks `fitsTogether (sizes.layers.map (·.2) ++ [fsize noSubst .top])` (:673), with `withinLimits_iff` (:274). Three missing lemmas would bridge it: (i) `elaborate (soften D).T` is the list of those `elabPremise` formulas in layer order; (ii) `fsize noSubst φ = (formulaNodes φ, formulaDepth φ + 1)` (both count term nodes, and `limitWalk`'s depth is 1-based like `AstLimit.walk`'s); (iii) `generatedSizes`' layer sizes equal `fsize` of the built premises. `checkW1` (:469) bounds only the rules' guards and carve-outs (a 10,000-node total and typing in the rule's context), not the elaborated premises.
- `hCheck`: typing of the elaborated premises in the route's environment (`envPrime D`, as the certificate case carries it). The pieces exist per premise. `soften_wellFormed` (Soften.lean:772) gives `VE.Norms.WellFormed (soften D)`. `VE.Norms.elab_wellFormed` (lean/VE/Norms/Elaborate.lean:252) gives `(elabPremise T r).WellFormed E []` and `definition_premise_wellFormed` (:271) gives `d.premise.WellFormed E []`, each from per-rule typing hypotheses. Missing: a list-level lemma that every member of `elaborate (soften D).T` is one of those premises and that `WellFormed (soften D)` supplies their hypotheses in `envPrime D` (`grep -rnE "theorem \w*elaborat\w*" lean/VE/Norms lean/VE/SoftNorms` finds only `elaborate_iff`, `elaborate_iff_at` and `soft_elaborate_iff`, which are semantic, not typing).
- `hData`: holds whenever `$string ∉ E.sorts`, which the route's environments guarantee (`Wire.lean`'s module docstring: `$string` is never a quantifiable sort). With that, `hCheck` refuses a `$string` binder before `hData` is needed.

## Seeded bugs (docs/kernel/kb-9a/seeded-bugs.json; each planted, built, restored from git, rebuilt)

- S1, task (a), `lean/VE/Route/Wire.lean`: `encodeFormula` swaps a binary atom's arguments. `lake build VE.Route.CodecRoundTrip` fails: `decodeFormula_encodeFormula` (binary case) and `walk_pairAtom`.
- S2a, task (b), fuel only, `lean/VE/Route/Wire.lean`: `decodeFormulas` and `decodeClosed` decode with fuel `maxDepth + 1`. Only the proofs of `decodeClosed_encodeFormula` and `decodeFormulas_encode` fail, because they rewrite at the literal fuel; their statements remain true. **Finding:** no statement and no test catches this change, and none can, because it changes no answer. `AstLimit.check` runs first and refuses depth 65 with the same diagnostic, so the fuel check never fires on a well-shaped formula.
- S2b, task (b), both checks, `lean/VE/Route/AstLimit.lean` plus S2a: the decoder accepts depth `maxDepth + 1`. `decodeClosed_refuses_depth` and `decodeFormulas_refuses_depth` fail (maximum recursion depth while checking `rfl`). An `#eval` of `decodeClosed` on the 65-level chain returned `ok` under the seed and `ResourceLimit: formula depth exceeds 64` after the restore and rebuild, so the statements are false under the seed.
- S3, `lean/VE/Route/CodecRoundTrip.lean`: `hDepth` relaxed from `<` to `≤`. `decodeClosed_encodeFormula` and its corollary fail.
- S4, `lean/VE/Route/Wire.lean`: `nodeLimit` refuses a total of `maxNodes` (`>` changed to `≥`). `decodeFormulas_encode` fails.
- S5, `lean/VE/Route/AstLimit.lean`: the walk's node limit doubled. Caught first by AstLimit's own `#guard`s (:113, :116, :121).
- S6, `lean/VE/Route/Wire.lean`: `decodeClosed`'s data gate removed. The `hData` `#guard` fails.
- S7, `lean/VE/Route/Wire.lean`: `decodeClosed`'s typing gate removed. The `hCheck` `#guard` fails.

## Evidence (commands run on this branch)

- `uv run python tools/regen_generated.py --write --only lean-statements --only lean-audit-manifests --only lean-roots`: rc 0, audit `PASS: 865 source files; 9938 named theorem declarations audited ... only the declared standard axiom allowlist`. The new theorems use only `propext`, `Classical.choice` and `Quot.sound` (lean/axioms.txt).
- `cd lean && lake build`: `Build completed successfully (1430 jobs)`. `python3 lean/audit.py`: rc 0, the same PASS line.
- `uv run python tools/regen_generated.py --check`: `checked 40 entries`, no stale file.
- `python3 tools/kernel_closure.py --check docs/kernel/closure-baseline.json`: `PASS: kernel 9504 <= 9504` (unchanged).
- `uv run python tools/trust_map.py --check`: `K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0`, PASS.
- `uv run python tools/repo_map.py --check`: PASS, 45 modes. `python3 tools/check_lean_imports.py`: `Lean layer graph kept`. The module's layer is 2 (by name rule, as for VE.Route.Wire) and its imports are at layers 1 and 2, so no layer_policy line.
- `python3 -I .../light-lane.py check`: NOT (the new file, VE.lean, Audit.lean: "trusted until classified"; the module has only theorems and `#guard`s, which take no trust-classes entry). The sweep was run anyway: `mac-pytest.sh --trustmut -- --max-mutants 1000 --json docs/kernel/kb-9a/trust-mutants.json`: `0 definitions, 0 mutants`, exit 0.
- The five frozen keys' harnesses, `.venv/bin/python` with the commands of docs/kernel/frozen-keys-20261111.md (without the tracer), on d8f3b9a5ce plus the docs commit: anthropic-rsp `--check` rc 0 (299 s), openai-preparedness `--check --base-only` rc 0 (142 s), safety-framework `--check` rc 0 (170 s), agent-policy `check.py base` rc 0 (130 s), eligibility `--no-write --no-mutants` rc 0 (208 s). Afterwards `git status --short` was empty. No executable imports the `VE` root (lean/lakefile.toml roots), so no binary links the new module.
- Selected tests, final, on committed 168123b51b (clean tree): `MAC_PYTEST_NO_DEFER=1 mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`: `recorded 112 units ...; 0 failed`, exit 0 (ran on ve-cloud-3, 7626 s). Commits after it touch docs/*.md only (this report).
- Pre-existing red tests (main-known-red.txt): none was selected or failed in this run.

## Notes for the DRI

- Depth is checked twice on the route (AstLimit.walk, then decodeFormula's fuel) with one diagnostic, so loosening either alone changes nothing visible (S2a). The refusal theorems here pin the combined bound. This matters to KB-4's "one formula codec": one of the two checks is redundant.
- A node-limit refusal theorem by `rfl` costs about 77 s of kernel evaluation, so it is a `#guard`. A general converse (`formulaNodes φ > maxNodes → decodeClosed … = .error nodeLimit` for well-typed φ) would need the walk's overflow case and the fact that a closed formula's variable indices are below 2^53 (from `hCheck`). It is not proved here.
- The decoders (`encodeFormula`, `decodeClosed`, `decodeFormulas`, `decodeFormula`) could now be tied to these theorems in tools/trust-classes.json. I did not tie them: the task says no trust-table change, and a round trip is not a statement of what a decoded formula means.
- The spec (docs/spec/kernel-boundary.md 1.2, softNorms paragraph, :116-122) still says the carry step is open. That is right: this item supplies the codec half, and kb-9's composition theorem closes it.

## Spec re-read

- `decodeClosed_encodeFormula` against the task's deliverable (1) and lean/VE/Route/Wire.lean:544-550: order AstLimit.check, decodeFormula maxDepth, data, check. All four are hypotheses, named after the limit or flag.
- `decodeFormulas_encode` against deliverable (2) and Wire.lean:523-541: `formulasJson` with no conclusion, `AstLimit.check` over the list, `mapM`, `nodeLimit` (the list-level limit, stated as `hNodes`), data, all-check.
- The "used with kb-7" requirement against lean/VE/SoftNorms/ElaborateSound.lean:45-50: `PremisesField` writes `enc e.2` (= `VE.Route.Wire.encodeFormula`, the function these theorems are about).
- KB-4 against docs/spec/kernel-boundary.md:386 ("one formula codec with a round-trip theorem"): stated for the route's FOL codec only. The closure, core and order codecs are out of scope, as the task says.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relayed answer, schema or relay changed (diff: Lean theorems, inventories, one manifest line).
2. Deliverables built: PASS. (1) a797b63cae `decodeClosed_encodeFormula`(+`_wellFormed`); (2) `decodeFormulas_encode`(+`_wellFormed`); (3) the section above; (4) lean/VE.lean import, inventories (3c13fd66ea, d8f3b9a5ce), assurance manifest (83c613043f), no layer line needed (`check_lean_imports.py`), no trust-classes change (`trust_map.py --check` +0); no existing Lean file edited (`git diff --stat main...HEAD`).
3. Tests and gates can fail: PASS, seeds S1-S7 above, each with its failing build. Trust mutants: 0 selected (docs/kernel/kb-9a/trust-mutants.json).
4. Python, Lean and Rust agree: N.A., no executable change. The five frozen-key harnesses pass unchanged (rc 0 each, above).
5. R8 binding: N.A., no field read from a Lean answer changed.
6. Gate evidence matches HEAD: PASS for the selected run on 168123b51b (only docs/*.md after it). The full gate is run by the chain on the final HEAD.
7. No unsigned item: PASS, no DELTA row and no trust growth (`trust_map.py --check`: trusted +0).
8. User-visible change in DELTA: PASS (none). No answer changes: no decoder, encoder or executable edit, and the frozen-key harnesses pass.
9. Test selection: PASS, `select_tests` selected 112 units (not every unit). tests/test_assurance_manifest.py was selected and caught the missing other_json entry before 83c613043f.
10. Lean statements say what is claimed: PASS. S1 (wrong encoder output breaks the build); S2b, S3 and S4 (bounds exact); S6 and S7 (gates). The theorems are about `decodeClosed`/`decodeFormulas` applied to `encodeFormula φ`, the values the route returns. The hypotheses are the decoder's own gates, each with a mechanised counterexample (`decodeClosed_refuses_depth`, the `#guard`s).
11. Budgets fail closed: PASS. The limits are hypotheses, and the over-limit inputs are refused with ResourceLimit (`decodeClosed_refuses_depth`, `decodeFormulas_refuses_depth`, the hNodes `#guard`s).
12. No CPU or memory regression: N.A., no executable change. The module builds in about 3 s.
13. Test-removed trailers: N.A., no test removed or renamed.
14. Both directions, cited evidence, spec re-read: PASS. Accept (the round-trip theorems) and refuse (the refusal theorems and `#guard`s) for each hypothesis. Each claim above names its command. Spec re-read section above.
15. No overclaim / no silent cut / every new check can fail / limits charged first: PASS. "No hypothesis is redundant" is limited to what the counterexamples show. `hData` is noted as implied by `hCheck` on route environments. Nothing was cut. Each `#guard` and refusal theorem has a seed (S2b, S6, S7; the hNodes guards with S5, caught first by AstLimit's own guards). Limits are unchanged code.
