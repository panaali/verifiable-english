# pc-6a build report: the decision key, staged

- **Status:** built; ready for review. No DRI signature is needed (trust S +5 under R16; no user-visible delta).
- **HEAD:** the commit that adds this report; the Lean and tables are final at `eb86dd1da`. Base `8c28fe286` (main).
- **What changed:** `SoftNode.splitFrom : Option String := none`, `decisionRule`, `decisionRule_unsplit` (proved) in
  `lean/VE/SoftNorms/Tree.lean`; fixture F6.1b in the new `lean/VE/SoftNorms/TreeExamples.lean`; one constructor site.
- **Open items:** none in this item. The full gate is run by the chain on the final HEAD (not run here, as instructed).

## Plan rows and directive lines

| Row (plan :1217-1234, spec 1.10 :1201-1222, 3.6 :2137-2142, F6.1b :3194, DRI item 1) | Delivered by |
|---|---|
| `SoftNode.splitFrom : Option String := none`, last field, spec 1.10's comment | `1262b7fab`, `lean/VE/SoftNorms/Tree.lean:45-46` |
| `def decisionRule (N : SoftNode) : String := N.splitFrom.getD N.name` | `1262b7fab`, `Tree.lean:49-50` |
| `theorem decisionRule_unsplit (N : SoftNode) (h : N.splitFrom = none) : decisionRule N = N.name`, proved (by `simp`) | `1262b7fab`, `Tree.lean:52-54`; `lean/statements.txt` and `lean/VE/Audit.lean` (`2ea973162`, regenerated) |
| Every anonymous-constructor site gains `none`, nothing else on the line | `1262b7fab`: the only one, `lean/VE/Defaults/MeaningExamples.lean:89` (`nπ`); a full `lake build` listed no other (log of the build: one error site, `MeaningExamples.lean:89:2`) |
| `DecidableEq` and `Repr` still derive | `Tree.lean:47`, unchanged `deriving` line; `lake build` succeeds (1193 jobs) |
| No decoder sets `splitFrom`, no lookup switched | no decoder or lookup is edited (`git diff --stat main...HEAD -- lean/` lists only Tree, TreeExamples, MeaningExamples, VE.lean and generated files) |
| F6.1b: a `#guard` over every rule of the soft-norms example and fixture documents that `decisionRule N = N.name`, plus `decisionRule_unsplit` | `TreeExamples.lean:26` (the 15 documents the layered route decodes with `decodeSoftU`: `dα dβ dγ dγ' dδ dδs dδo dε dζ dζ0 dσ` of `Defaults/Examples.lean`, `dTwo dSw dπ` of `Defaults/MeaningExamples.lean`, `dγb` of `Defaults/WireExamples.lean`; each must decode and have a rule), `:27` (the literal DF-π), `:28` (the rights examples after `correlate`), `:32` (`example` by `decisionRule_unsplit`), `:33` (`nπ`), `:36` (the opposite direction: a split part reads its source) |
| F6.1b is built by the gate | `lean/VE.lean` imports `VE.SoftNorms.TreeExamples` (`2ea973162`), so a plain `lake build` runs it |
| Seeded bug: `decisionRule` returns "" on an unsplit rule; F6.1b fails | below, mutant 1 |
| `lean/statements.txt` gains the lemma; `lean/axioms.txt` only standard axioms | `2ea973162`: `'VE.SoftNorms.decisionRule_unsplit' depends on axioms: [propext]`; `python3 lean/audit.py`: `PASS: 693 source files; 7810 named theorem declarations audited ...` |

There is no examples file under `lean/VE/SoftNorms/` on main, so this item adds `TreeExamples.lean` as Tree's
examples file. The soft-norms example documents on main are the layered fixtures above (`lean/VE/NormDefaults/Examples.lean`
holds W1 `UDoc`s, not soft documents; it is sa-nd-atoms' file and is neither edited nor needed).

**Synthesis round 2, edits-soft-norms item 3** (soft-norms owns the split decision key: `SoftNode.splitFrom`,
`excepted_key`, `decMeta`; its owner reviews PC-6's key). This item implements the `SoftNode.splitFrom` part of it,
in soft-norms' file, for soft-norms' owner to review. `excepted_key` and `decMeta` belong to PC-6. The edit and the
plan agree on everything PC-6a builds, so there was nothing to resolve.

**Statement gate:** pc-d2 confirmation review passed (2026-10-30 00:08Z); DRI item 1
(reviews/dri-decisions-20261031-pc-9-prereqs.md) SIGNED, condition F6.1b plus mutant 1, both kept.

**Spec re-read** (each word checked):
- the field against spec :1214 (`splitFrom : Option String := none`, last field; comment "the source rule of a part
  acts generated; none for an authored rule", written as a doc comment without "(new)");
- the definition against spec :1216-1217 (docstring "The rule whose decisions a rule reads." and body, word for word);
- the lemma against spec :1219-1220 (statement word for word; the docstring drops only "(proved in the stub, by `simp`)",
  which is now true of the proof itself);
- F6.1b against spec :3194 and plan :1230;
- the seeded bug against plan :1232.

## Elaborated statements that spell the new field

The Lean source of no existing theorem changes. Two theorems state a `{ M with … }` update of a `SoftNode`, so their
elaborated form in `lean/statements.txt` now spells out the copied field: `VE.Readings.relaxTo_of_eq`
(`…, hard := Nd.hard, splitFrom := M.splitFrom }`) and `VE.Rights.correlate_identity`
(`…, hard := __src.hard, splitFrom := __src.splitFrom })`). Same proofs, same meaning, no statement edited.

## Sibling lessons (pc-fid-rev4-review)

- A (an obligation that never touches the real function): F6.1b reads the documents the real `decodeSoftU` returns
  (each must decode), not a helper's output, and `decisionRule` is the definition PC-9 and PC-6 will read.
- B (a lemma false as stated): `decisionRule_unsplit` is proved, with no `sorry` and only `propext`.

## Seeded bugs (Lean; product code changed in Lean only)

Each was planted in `lean/VE/SoftNorms/Tree.lean`, built with `lake build VE.SoftNorms.TreeExamples`, and then restored
(`git checkout`). Recorded in `docs/profile-composition/pc-6a/mutants.json`.

1. `decisionRule` returns `""` on an unsplit rule (`N.splitFrom.getD ""`): `error: VE/SoftNorms/Tree.lean:53:98:
   unsolved goals` (`decisionRule_unsplit`). With that proof replaced by `sorry`, F6.1b fails:
   `error: VE/SoftNorms/TreeExamples.lean:26:0: Expression`, `:27:0`, `:28:0`, `:33:0`.
2. `decisionRule` ignores `splitFrom` (`N.name`): `error: VE/SoftNorms/TreeExamples.lean:36:0: Expression`.
3. The field's default is set (`:= some ""`, as if a decoder set it): `error: VE/Defaults/MeaningExamples.lean:116:0:
   Expression` (the decoded DF-π equals its literal, whose `splitFrom` is `none`).

`trust_mutants` (`mac-pytest.sh --trustmut -- --max-mutants 1000 --json docs/profile-composition/pc-6a/trust-mutants.json`,
exit 0): `0 definitions, 0 mutants`. `decisionRule`'s body is a `String` with no token that the tool's operators
mutate (no Bool, number, list or `++`), and fields are not mutated. The three hand mutants above cover each new
trusted definition (`decisionRule`, twice, and `SoftNode`'s new field).

## Trust

`uv run python tools/trust_map.py --check` on the final tree: `against 8c28fe28635a: K +0, S +5, D +0, G +0, tied +0,
unclassified +0, trusted +5`, `VE/SoftNorms/Tree.lean: trusted +5`, `PASS`. It was recorded with `--allow` and
`--signed "SIGNED by standing ruling R16 (DRI-RULINGS.md), pc-6a, 2026-10-18"` (DELTA row 1). The FOLLOW-UPS.md row
"## pc-6a" asks for the ties pass.

## Tests run

- Selected tests, once, on the finished code: `mac-pytest.sh --select -- --base 8c28fe286 --run` exit 0, on the
  cloud with 6 shards (79 + 73 + 67 + 65 + 63 + 57 = 404 units, all passed). The selection is 416/516 units because
  `SoftNode` sits under most of the Lean tree and no Lean build record was there to narrow it.
- `uv run python tools/gate_collection.py --check --prebuilt`: `31350 collected ... 0 added, 0 removed by a trailer, 0
  refused, 0 stale and 0 malformed trailers`.
- `uv run python tools/regen_generated.py --write`: exit 0. It also refreshed the codemap, which was stale on main.
  The Rust release binary was built first with `python3 tools/rust_build.py`, because `route-cases` needs it.
- Not run: the full gate (the chain runs it). Pre-existing reds (main-known-red.txt): none was hit.

## Size and bytes

Hand-written lines (`git diff --numstat 8c28fe286`, generated files excluded): Tree.lean +9, TreeExamples.lean +38,
MeaningExamples.lean 1/1, VE.lean +1, tools/trust-classes.json +7, docs/trust-baseline.json +7 (written by `--allow`),
plus this report, DELTA.md and mutants.json. Pilot bytes moved: 0 B (estimate; a structure row).

## Next item

pc-9 (after pc-3 and pk-1-conditions) reads `decisionRule` in `dfltUniformOf`; then pc-6 (the split, the revised
names and the table) sets `splitFrom` and switches `exceptedName`/`offName` to the key.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no route, schema, relay or encoder changes (no `Repr` output path; selected tests pass).
2. Every deliverable built: PASS, table above; diff grep: no Python copy, no report test, no file of an in-flight branch except generated `lean/statements.txt`.
3. Tests can fail: PASS, mutants.json (3 killed) and trust-mutants.json (exit 0).
4. Py/Lean/Rust agree: N.A., Lean only and no answer changes; selected tests (404 units) pass.
5. R8 binding: N.A., no field read from a Lean answer added.
6. Gate evidence: PASS, built and tested at the merge base `8c28fe286`; main has since gained two merges (pc-3 `a24d66a7c`, ap-1bf `4d9a0eeb0`), which touch no file of this item and add no `SoftNode` construction (`git diff 8c28fe286 main -- 'lean/*.lean' | grep -c '^+.*SoftNorms'` = 0); not merged here, the merge train syncs; the chain gates the final HEAD.
7. No unsigned item: PASS, DELTA row 1 cites R16; `trust_map.py --check` PASS.
8. Every user-visible change in DELTA: PASS, none (no decoder sets the field; F6.1b `TreeExamples.lean:26-28`; selected tests pass).
9. Test selection: PASS, `select_tests.py` selects 416/516 (a structure under most of Lean), not every unit; mutant 3 is caught by `MeaningExamples.lean:116`, inside the built tree.
10. Lean statements say what is claimed: PASS, mutant 1 breaks `decisionRule_unsplit` (`Tree.lean:53`); statement word for word as spec :1220.
11. Budgets and deadlines: N.A., no evaluator, budget or deadline.
12. CPU and memory: N.A., one `Option.getD`, no caller yet.
13. Test-removed trailers: PASS, `gate_collection.py --check --prebuilt`: 0 removed, 0 stale, 0 malformed.
14. Both directions, cited evidence, spec re-read: PASS, `TreeExamples.lean:26` (unsplit keeps the name) and `:36` (split reads the source); spec re-read list above.
