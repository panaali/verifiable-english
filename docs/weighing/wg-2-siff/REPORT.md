# wg-2-siff REPORT: `strength_iff` with the DRI's hypothesis (Lean)

**Done; no DRI signature reserved.** `strength_iff` (weighing.md 5.1) is proved with one added hypothesis `hr`: every
regulated name begins with an ASCII letter. That is the wider of the two forms that reviews/dri-decisions-20261104-wg-2-strength.md item 2 signs, needed
because the narrow form is false (F19's mirror; confirmed by reviews/dri-decisions-20261105-wg-2-siff.md item 2).
Standard axioms only; trusted growth +0; public output unchanged (bytes 0). Selected tests pass (98 units, exit 0).
The chain's full gate on this HEAD is not run by me (task rule). Next item: wg-3.

Base: 14e200f24 (`git merge-base HEAD main`). Commits (`git log --oneline main..HEAD --no-merges`, saved here before
this report's own commit): e5870cffb, e12e8c356, 883c0b048, bde26e303, 98cd48339, 31d260b16, then the commit adding
this report.

## 1. Deliverables

| Task line | Delivered | Commit | Evidence |
|---|---|---|---|
| (1) `strength_iff` in `Conditions.lean` with the hypothesis, proved: forward through `outweighsName`'s injectivity, reverse through `strength_mem` | yes, `Conditions.lean:1525`. Forward: the premise's formula fixes the act's sorts (`bindAll_not_inj`), an arity-1/2 atom fixes the name (`atom_inj`, `triple_arity`), both acts are regulated since their sorts are not `[]` (`regulated_of_sorts`), so `hr` gives each a letter head; ranks are `validSoftName` (`checkSoftEnv_names`; the triple's through `chain_of_strictPair`, `chain_members_ranks`); `outweighsName_inj` (`:1479`, two uses of `split_dunder_left`, `:1448`) recovers `(a, L, H)`. Reverse: `strength_mem` | e5870cffb | `lake build` (1298 jobs) passes; `python3 lean/audit.py`: "PASS: 771 source files; 8597 named theorem declarations audited"; `lean/axioms.txt`: `VE.Weighing.strength_iff` uses `[propext, Classical.choice, Quot.sound]` |
| (1) which form of the hypothesis | the wider form (every regulated name). The narrow form on the queried `a` is false. Mirror document `mxW`: real triple `(_x_permitted, l, c)`, query `(x_permitted, l, c_)`, the same name. The DRI was told and confirmed it (decision of 2026-11-05 item 2) | e12e8c356 | `Examples.lean:257` |
| (1) listed in `Audit.lean` beside `strength_mem` | yes, through `regen_generated.py --write` (`lean-audit-manifests`); `#print axioms VE.Weighing.strength_iff` is the line before `strength_mem`'s | bde26e303 | `git show bde26e303 -- lean/VE/Audit.lean` |
| (1) module comment `:16-:17` updated | yes (`Conditions.lean:15-18`) | e5870cffb | the file |
| (2) keep `cxD`/`cxX`/`cxW` and the decoder guard | yes, unchanged (`Examples.lean:200-214`) | - | `git diff main -- lean/VE/Weighing/Examples.lean` adds lines only |
| (2) the statement without the hypothesis refuted on that document | `#guard` at `Examples.lean:243`: every other hypothesis holds at `(_x_permitted, l, c)` (`hyps`), `hr` fails (`!lettered cxX`), left side true, right side false. A `#guard`, not a kernel `example`: the document is decoded from JSON, which the kernel does not reduce in reasonable time | e12e8c356 | build; mutant G4 |
| (2) a `#guard` per direction on W-β1/W-β2/W-γ | `:236` W-β1 `(s,h)` (true, true); `:238` W-β2 `(e,h)`, a triple, holistic (false, false); `:240` W-γ: strict pair, no triple (false, false); each with `hyps` and `lettered` true | e12e8c356 | mutants G1-G3 |
| (2, beyond the task) F9 and F13 as guards | `:262`, `:264`: decoded, lettered documents where the statement without `hL`/`hH` is false | e12e8c356 | mutants G6, G7 |
| (3) weighing.md 5.1: the statement and one plain-words sentence naming the decoder rule | yes (`weighing.md:969-976`; the sentence at `:981-983`, "Invalid ASCII identifier", `Surface.identifier`); the proof note is updated to the proof (`outweighsName_inj`) | 883c0b048 | the file |
| (3) 7.3 falsifying row | **F19**, not F14: F14 already exists (weighing.md:184). Renumbered by reviews/dri-decisions-20261105-wg-2-siff.md item 1, with its note (`weighing.md:1506`) | 883c0b048 | the file |
| (3) change-log entry "wg-2-siff, DRI 2026-11-04 wg-2-strength item 2" | yes (`weighing.md:1719`) | 883c0b048 | the file |
| (4) DELTA: one row, Ruling exactly as given | yes ([DELTA.md](DELTA.md) row 1) | 31d260b16 | the file |
| generated inventories through `regen_generated.py --write` | once, after the Lean was done: Audit.lean, axioms, statements, declarations, and codemap (main's drift: `test_trust_mutants_probe_scope.py`) | bde26e303 | `regen_generated: wrote 35 entries` |
| Trust: <= 20 lines K+S+V under R16, no K growth; `--allow`; FOLLOW-UPS row | `uv run python tools/trust_map.py --check`: "K +0, S +0, D +0, G +0, tied +0, unclassified +0, trusted +0 ... PASS". The 11 new fixture definitions are T in `tools/trust-classes.json` (98cd48339), as wg-2's are; the 7 lemmas and the theorem are P. `--allow` answered "nothing to allow". FOLLOW-UPS.md row under "## wg-2-siff" says so | 98cd48339 | the commands' output |
| Must stay selected | `cxD`/`cxX`/`cxW`, the decoder guard, the refutations (`:243`, `:257`) are `#guard`s in `Examples.lean`, built by `lake build` and selected through `tests/test_lean_default_build.py` (in this run's selection, `/tmp` log line "98/544 test units") | - | selection log |

Deviations from the task's file list (both needed for correctness, neither a statement change): `lean/WEIGHING.md`
(it said `strength_iff` "is not proved"; now one bullet in plain words, 31d260b16) and `tools/trust-classes.json`
(the fixture classes, 98cd48339). Size: 216 hand-written lines (`git diff --numstat` against the base, generated
files excluded, before this report), under ~600.

Not changed: Zone.lean, Tree.lean, any plan, any Python, Rust or decoder file. `ha` stays in the statement as approved
(the proof does not need it once `hr` holds, since a query with sorts `[]` is never a premise. The statement keeps it,
so the change is exactly the one hypothesis).

## 2. Seeded bugs (Lean, the only product language changed; [mutants.json](mutants.json))

Each was planted, shown failing, and restored. After L4 `lake build` was rerun on the restored tree: "Build completed successfully (1298 jobs)".

| Id | File | Mutant | Fails |
|---|---|---|---|
| L1 | `lean/VE/Weighing/Conditions.lean` | the injectivity lemma's hypothesis dropped: `split_dunder_left`'s `p'.head? ≠ some '_'` weakened to `≠ some 'z'` | `lake build VE.Weighing.Conditions`: `Conditions.lean:1466:10: unsolved goals`, the case `k = c :: []`, `k' = []` (the `c_` / `c` + `_x` split, the counterexample's) |
| L2 | `lean/VE/Weighing/Conditions.lean` | `strength_iff` without `hH` (weakened to `H ≠ ""`) | `lake build VE.Weighing.Conditions`: `:1563:37 Application type mismatch`; F13's `#guard` (`Examples.lean:264`) is the document that refutes it |
| L3 | `lean/VE/Weighing/Conditions.lean` | `strengthEntries` builds `outweighsF a H L` (swapped) | `lake build`: `:902` (`strength_mem`), `:1150`, `:1563` (`strength_iff`) |
| L4 | `lean/VE/Bridge.lean` | the decoder accepts a `_`-initial identifier | `lake build VE.Weighing.Examples`: `Examples.lean:211:0`, the decoder guard, only that one |
| G1-G7 | `lean/VE/Weighing/Examples.lean` | each new `#guard`'s fixture or `lettered` moved (mutants.json) | each its own guard line: 236, 238, 240, 243 and 257 (G4), 257 (G5), 262, 264 |

No new trusted definition, so no per-definition trust mutants and no trust_mutants run (13a applies to trusted growth).

## 3. Numbers and runs

- `zsh mac-pytest.sh --select -- --base 14e200f24 --run`: "98/544 test units", every file and chunk exit 0,
  "summary: ran LOCALLY (VM) because: could not send the coverage maps to ve-mac-1; exit=0; 3738s". Deferred to the
  chain gate by the selector: `tests/test_safety_framework.py` (over 120 s, weak reason).
- `uv run python tools/gate_collection.py --check --prebuilt`: "32293 collected ... 0 added, 0 removed by a trailer,
  0 refused, 0 stale and 0 malformed trailers".
- Not run: the full gate (the chain runs it on this HEAD), trust_mutants (no trusted growth).
- Pilot bytes expected to move: 0 (no wire document has a `_`-initial name; nothing on a public path reads these modules).

## 4. Spec re-read

- `strength_iff` against weighing.md:969-976 and Conditions.lean:1525-1530: the same binders, in order (`h`, `a L H`,
  `hL`, `hH`, `ha`, then `hr`), the same conclusion; `hr` is the only change.
- `hr`'s words against item 2 of the 2026-11-04 decision: "every regulated name of the document begins with an ASCII letter"; `Char.isAlpha` is
  ASCII `A-Z`/`a-z`, weaker than the decoder's `a-z` (`Surface.identifier`, `VE/Surface.lean:71`), so it holds on
  every decoded document.
- DELTA row 1's Ruling cell against the task text: verbatim.
- F19 against reviews/dri-decisions-20261105-wg-2-siff.md item 1: the note text is verbatim.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A., no relayed route or response changes.
2. Every deliverable built: PASS, section 1's table (each task line with commit and evidence); rule-break grep: no Python copy, no report test, the only overlap with in-flight branches is `tools/trust-classes.json` (ci-2, cmp-s4c, df-5, et-4b, pc-1g, me-1: another module's lines).
3. Tests can fail: PASS, mutants L1-L4, G1-G7 (mutants.json), each failing a named build line or `#guard`.
4. Py/Lean/Rust agree: N.A., no Python or Rust change and no output change.
5. R8 binding: N.A., no relayed field.
6. Gate evidence matches HEAD: PASS for what I ran (selected tests on the committed tree 31d260b16 plus this report; the report changes no code); the full gate is the chain's.
7. No unsigned item: PASS, DELTA row 1 is SIGNED by the DRI with decision file; trust +0 needs no allowance (`trust_map.py --check` PASS).
8. Every user-visible change in DELTA: PASS, none besides the statement (no product file on a public path changed; DELTA header).
9. Selection finds the tests: PASS, `tests/test_lean_default_build.py` is selected and builds the tree in which L1-L4 fail.
10. Lean statements say what is claimed: PASS, L1 and L2 break the proof. L3 shows the theorem is about `strengthEntries`' own premise. The added hypothesis has a DRI ruling and mechanised counterexamples (`Examples.lean:243`, `:257`).
11. Budgets and deadlines: N.A., no evaluator or limit.
12. CPU/memory: N.A., no runtime path; `lake build VE.Weighing.Examples` 8.6 s.
13. Test-removed trailers: PASS, `gate_collection.py --check --prebuilt` 0 removed, 0 stale, 0 malformed.
14. Both directions, cited evidence, spec re-read: PASS, guards for both sides (`:236` true/true, `:238`/`:240` false/false, `:243`/`:257`/`:262`/`:264` true/false), section 3 cites each command, section 4.
15. No overclaim / no silent cut / checks can fail / limits: PASS. Universal words checked: "none changes" (DELTA: no public path imports the modules, wg-2's DELTA), "every wire document" (decoder guard `:211`, L4), "+0" (`trust_map.py --check`); no deliverable cut; G1-G7; limits N.A.
