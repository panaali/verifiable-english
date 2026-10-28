# sc-1ae: spec 5.1's statements about what `govern` writes, under the DRI's fix (a) (scope@0, Lean core). Build report

**No DRI signature is reserved.** Delivered: `JsonWF`, `HasStr`, `payload`, `BlockBound`, and four of the five stopped
statements (`decodeNorm_name`, `govern_strings`, `govern_no_new_symbols`, `govern_preserves`), each with the signed
`JsonWF` hypothesis, and F-sym. Not delivered: `govern_provenance` (**sc-1aeb**, size rule) and the parser lemma
(**sc-1af**): `Lean.Json.parse` is built of `partial def`s, so no lemma about its output can be proved. So, as the
decision says, SC-1b's statements may not take `JsonWF` as a hypothesis until sc-1af proves it.

## fix1 (review `sc-1ae-review.final.md`)

One B finding, fixed as a class. **F1 (B)**: deleting `JsonWF`'s `bool` and `num` still built, so the four
statements could hold vacuously on every real document. The example: F-sym's document is now proved well formed
(`parts_wf`, through `hcDoc_wf` and `part_wf`, `lean/VE/Scope/Examples.lean`; `part` writes its guard as a term,
and a `#guard` shows it equals the text `j` parses), a rule object with `"sign": false` too (`leadPart_wf`), and
`govern_no_new_symbols` is applied to F-sym's document on its `BlockBound` side (both hypotheses proved, the same
class: no fixture had them hold at once). The general lemma `jsonWF_mkObj` (`lean/VE/Scope/Theorems.lean`) builds
each. The class: no tool dropped a constructor of a new inductive, so an unread one went unseen. `tools/trust_mutants.py`
now has `ctor-drop` (each constructor dropped alone, its doc comment with it); a SURVIVOR's detail names the proofs
it breaks; and `--allow` never allows a constructor drop that breaks no proof, so an unread constructor stays a
SURVIVOR (exit 1) whatever the allow file says. The PROBE F1 failed before the fix and passes after it (errors at
`Examples.lean:789` `.num` and `:824` `.bool`). F2, F3 and F5 (C) are left to their FOLLOW-UPs; F4's two allow
reasons are reworded (`eq-le` INVALID by hand; `BlockBound` `body-false`'s meaningful kill is `Examples.lean:764`).

## fix2 (recheck `sc-1ae-looprecheck1.final.md`)

One new B finding, fixed as a class. **F6 (B)**: `--rescore` reused an ALLOWED row with an empty detail (it kept
the detail only where `--allow` changed nothing), so a `ctor-drop` came back as breaking no proof, `--allow` refused
it, and a rescore of allowed evidence on an identical tree reported each allowed drop as a SURVIVOR (exit 1). The
class: any part of a verdict that `--allow` writes over is lost to `--rescore`. Now `allowed` records the whole
verdict before `--allow` (`raw_status` and `raw_detail`), the evidence writes `raw_detail` on every row `--allow`
changed, `previous` reads it for every operator and status, `Reads.verdict` reads it too, and evidence with an
allowed row that has no `raw_detail` is not reused: the tool does a full run and prints why, so it never reads an
empty detail. PROBE F6 failed before the fix (`('SURVIVOR', '') != ('ALLOWED', …)`) and passes after it. On this
item: the evidence was rerun with the new tool (a full run, since the tool's digest changed; 3 KILLED, 13 ALLOWED,
exit 0), then the recorded command rescored it into [trust-mutants-rescore.json](trust-mutants-rescore.json):
mode "identical", 15 reused, 1 rerun (`HasStr` `eq-le`, UNKNOWN before `--allow`, which is never reused), 3 KILLED,
13 ALLOWED, exit 0; each of the 9 `ctor-drop`s stays ALLOWED and names the proofs it breaks.

- Branch `feature/sc-1ae`, worktree `/home/seyran/code/ve-sc-1ae`, merge base `72a241fba` (main, after a merge of
  main at `a93aa5df3`; the work started on `c2a0ee977`).
- Decision: `reviews/dri-decisions-20261027-featureplan-gates.md` item 2 (manage-agents), fix (a). Plan and spec on
  main, unchanged: `docs/spec/scope-PLAN.md` "SC-1a", `docs/spec/scope.md` 4.2, 5.1, 7.1 (F-sym), 11.3
  (`Pinned.JsonWF`); sc-1ad's REPORT rows (2), (3), F-raw and "Next items"; FOLLOW-UPS "## sc-1ad".

## Statement gate

The scope statement review closed with PASS (sc-1ad's report, "Statement gate"). The DRI's decision is the amendment:
each of the five gains the hypothesis that every JSON object of the document (and of the decoded rule) is well formed,
and the definitions stay spec text. [statement-diff.txt](statement-diff.txt) (sc-1ac's `evidence/spec_diff.py` on
this HEAD) shows it: `HasStr`, `payload`, `BlockBound` and `govern` are exact; the four theorems differ from spec 5.1
only by `(hw : JsonWF o)` (`decodeNorm_name`) or `(hw : JsonWF D.doc)` (the other three); `JsonWF` is the text of
spec 11.3's stub `Pinned.JsonWF` (`docs/spec/scope/SpecStubs_sc5r.lean`), defined once in
`lean/VE/Scope/Govern.lean`, where sc-3ac (`title_identity`) and sc-5rc use it. No other statement changes.

## Plan rows

| Row (task) | Status | Where |
|---|---|---|
| (1) `decodeNorm_name` under `.WF` | delivered | `Theorems.lean:762`, through `decodeNorm_name_top` (`:724`) |
| (1) `govern_strings` under `.WF` | delivered | `Theorems.lean:1130` |
| (1) `govern_no_new_symbols` under `.WF` | delivered | `Theorems.lean:1149` |
| (1) `govern_preserves` under `.WF` | delivered | `Theorems.lean:1157` |
| (1) `govern_provenance` under `.WF` | **sc-1aeb** (size rule) | "Size" below; the lemmas it needs are here (`unitsOf_patch`, `comp_entry`, `composed_src`) |
| (1) `HasStr`, `payload`, `BlockBound` as spec 4.2 defines them | delivered, exact | `Govern.lean:292`, `:298`, `:305` |
| (1) F-sym | delivered | `Examples.lean:751`: `govern` writes `invented` 7 times (one per hard constraint), the document has none; `invented_payload`; `¬ BlockBound` with `block = null`, `BlockBound` with the condition in the block |
| (2) a proved lemma that `Json.parse` output satisfies `.WF` | **sc-1af**: does not fit (cannot be proved of either parser) | "The parser lemma" below |
| (3) F-raw's four `#guard`s stay in `Examples.lean` | delivered, unchanged | `Examples.lean:738` (items 1 and 2), `:743` (item 3), `:748` (item 4) |
| (4) seeded bugs: `.WF` dropped from each theorem; one mutant per new trusted definition | delivered | "Seeded bugs" below |
| Define `.WF` once, where sc-3ac can use it | delivered | `VE.Scope.JsonWF`, `Govern.lean:283` |
| DELTA, trust, FOLLOW-UPS row | delivered | [DELTA.md](DELTA.md); "Trust"; FOLLOW-UPS "## sc-1ae (2026-10-28)" |

## What is built

- **The hypothesis is needed only at the level written to.** Every lemma takes the top level of the object
  `setObjVal!` writes to as a well-formed tree (`∀ kvs, o = .obj kvs → kvs.WF`), and `JsonWF D.doc` supplies it for
  the document, each unit and each content (`jsonWF_top`, `jsonWF_getD`, `unitsOf_mem`, `contentOf_src`). The
  objects scope builds itself are well formed by construction (`Json.mkObj` is `ofList`; `setObjVal!` keeps `.WF`),
  so the composed rule needs no hypothesis (`composed_src`).
- **No hypothesis on the payloads.** Spec 11.3 says `governSets_strings` takes `JsonWF` of each payload, because
  `mergeParts` reads a frame part by traversal. On this tree it reads them through `lookups` (sc-1ad), i.e. by
  lookup, and `substOwn` maps a tree without changing its shape (`impl_get_map`, proved on any `Impl`). So
  `govern_strings` holds with `JsonWF D.doc` alone, as the DRI's text gives it. Recorded for sc-5rc, which can drop
  `hp` from `governSets_strings`.
- **`decodeNorm_name`.** The norms chain reads `name` by lookup (`w1_name`, `normFields_name`), with no hypothesis.
  The soft chain's `Phases.ruleFields` reads the members by `toList` and rebuilds the object; on a well-formed tree
  `toList` and lookup agree (`members_get`), and the rest of `ruleFields` keeps W1's name (`ruleFields_name`, walked
  through its join points).
- **`govern_strings`.** A string of the answer is in the document (`patch_src`), in a composed rule (`composed_src`:
  the document or a governor's payload, through `baseObj_src`, `mergeParts_src`, `applyEffect_src`,
  `hasStr_substOwn`, `fold_src`), or a name `addOver` writes (`addOver_src`, `fresh_mem`), which is a decoded rule's
  name (`edgesInto_mem`, `edgesOf_name`, `ruleTable_decoder`) and so a string of that composed rule
  (`decodeNorm_name_top`). `govern_no_new_symbols` follows with `BlockBound`.
- **`govern_preserves`.** `patch` writes `units` only (`setObjVal_ne`); `unitsOf_patch` gives the answer's units as
  the document's, mapped; a unit keeps its `id` and every member but `content` (`idOf_set`, `setObjVal_ne`), and a
  unit outside `affected D` is not written (`comp_entry`, `lookup_mem`).

## The parser lemma (sc-1af)

The decision's condition is a proved lemma that `Json.parse` output satisfies `.WF`. It does not fit, and cannot be
proved of the parser as it is: `Lean.Json.parse` runs `Lean.Json.Parser.anyCore`, `objectCore` and `arrayCore`, all
`partial def` (toolchain `Lean/Data/Json/Parser.lean:204-233`), which the kernel sees as opaque constants. The
repository's own `VE.JsonInput.parse` (`lean/VE/Json.lean`) is fuel-bounded but reads through Std's Parsec `many` and
`manyChars`, also `partial` (`Std/Internal/Parsec/Basic.lean:153`, `:248`). So sc-1af needs a route change, not only
a lemma: either rebuild each object at the boundary (`Json.mkObj` of its `toList`, `JsonWF` by a structural proof),
or check each tree's order and balance with a lemma that the check gives `.WF`. Either is a DELTA row. Until then,
per the decision, SC-1b's statements do not take `JsonWF` as a hypothesis.

## Size

Hand-written lines against the merge base: Lean 686 (`Theorems.lean` +622, all proofs; `Govern.lean` +29;
`Examples.lean` +35), `lean/SCOPE.md` +11/−4, `tests/test_scope_lean.py` +3/−2, `tools/trust-classes.json` +7,
`docs/trust-baseline.json` +7, DELTA 15, `mutants.json` 20, the allow file 8: about 765, and this report. That is
over the feed's ~600. I measured after the first three statements: `decodeNorm_name` with `govern_strings` and
`govern_no_new_symbols` alone took about 600 lines of proof (the soft chain's decoder walk is about 95, the composed
rule's string lemmas about 130, the JSON lemmas about 180). That was the smallest coherent part.
`govern_preserves` added about 45 lines on the same lemmas, so I kept it; `govern_provenance` (an estimated 80 more)
is cut to sc-1aeb. The outputs (`statement-diff.txt` 83, `trust-mutants.json`, `trust-mutants-run1.json`) and the
generated inventories are not counted.

## Overlap check

Hand-written files: `lean/VE/Scope/{Govern,Theorems,Examples}.lean`, `lean/SCOPE.md`, `tests/test_scope_lean.py`,
`tools/trust-classes.json`, `docs/trust-baseline.json`, `docs/scope/sc-1ae/*`. Against `git diff --name-only
main...<b>` for every `lean-first/*`, `feature/*`, `infra/*`, `foundation/*` branch (2026-10-28): none touches
`lean/VE/Scope/`, `lean/SCOPE.md` or `tests/test_scope_lean.py`. The ledgers merge through the `ve-generated` driver.
sc-3ac (rank 88) follows on the same files.

## Seeded bugs (Lean; [mutants.json](mutants.json), [trust-mutants.json](trust-mutants.json))

Lean is the only language whose product code changed (the Python changes are a test's case list and, in fix1, the
`trust_mutants` tool and its tests).

**fix1 (F1).** Rerun on `30896a2c9` with the new tool (a full run, its digest changed): 16 mutants of 4 definitions,
**3 KILLED**, **13 ALLOWED**, 0 SURVIVOR, 0 UNKNOWN, exit 0. The 9 new ones are `ctor-drop`s of `JsonWF` (6) and
`HasStr` (3); each names the proofs it breaks (`JsonWF`'s `bool`: `Examples.lean:820` `leadPart_wf`; `num`:
`Examples.lean:772` `part_wf`). Seeded bugs in the tool (Python), each restored: (1) no `ctor-drop` generated:
`tests/test_trust_mutants.py::test_the_generator_drops_each_constructor_of_an_inductive`, `..._of_json_wf` and
`test_a_constructor_no_proof_reads_survives_with_no_proof_named_and_is_never_allowed` fail; (2) a SURVIVOR's detail
empty: the last fails; (3) `--allow` applied to an unread constructor: the last fails. Lean: PROBE F1, below as
`JsonWF-no-bool-num`.

**fix2 (F6).** Seeded bug in the tool (Python), restored: `previous` reads the detail only where `--allow` changed
nothing (the old line): `tests/test_trust_mutants.py::test_rescore_reads_the_whole_verdict_before_allow` (3 of 4
cases: ctor-drop, lt-le SURVIVOR, lt-le UNKNOWN) and
`::test_a_constructor_no_proof_reads_survives_with_no_proof_named_and_is_never_allowed` fail. No Lean or Rust changed.

**Mechanical (R16, checklist 13a).** `zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --allow
docs/scope/sc-1ae/trust-mutants-allow.json --rescore docs/scope/sc-1ae/trust-mutants.json --json
docs/scope/sc-1ae/trust-mutants.json` on `3aa5f8151` (after the merge of main): 7 mutants of the 3 definitions with
an operator site: **3 KILLED** (`payload`'s three arms, by the `#guard` at `Examples.lean:779`), **4 ALLOWED**, 0
SURVIVOR, 0 UNKNOWN, exit 0. The first run (`trust-mutants-run1.json`) had 3 survivors and 4 unknowns: the tool counts
only evaluated checks, and `HasStr` and `BlockBound` are propositions no `#guard` or `decide` can read. The allow
file gives each of these definitions and operators its proof kill (below), as me-12a did. `HasStr`'s `= -> ≤`
is text Lean refuses. `payload`'s `rfl` fixture became a `#guard`, which kills its arms. `JsonWF` has no operator
site the tool mutated before fix1 (`ctor-drop`, above).

**By hand (19).** Each was applied, built with `cd lean && lake build VE.Scope.Examples`, and restored from git. The
tree was clean after each.

| Mutant (definition) | Claimed behaviour | First failure |
|---|---|---|
| `JsonWF-obj-no-WF` (`JsonWF`) | a well-formed object's tree is `.WF`, the added hypothesis | `Theorems.lean:759` `jsonWF_top` |
| `JsonWF-obj-no-members` (`JsonWF`) | well formed at every depth | `Theorems.lean:808` `jsonWF_getD` |
| `HasStr-obj-any-value` (`HasStr`) | a string is reached through a member's lookup | `Theorems.lean:587` (34 errors) |
| `HasStr-no-arr` (`HasStr`) | a string of an element is one of the array | `Theorems.lean:818` `unitsOf_mem` |
| `payload-carveOut-null` (`payload`) | a carve-out's payload is its condition | `Theorems.lean:946` `applyEffect_src` |
| `payload-frame-null` (`payload`) | a frame's payload is its part | `Theorems.lean:915` `baseObj_src` |
| `BlockBound-reads-doc` (`BlockBound`) | payloads bound to the block, not the document | `Theorems.lean:1153` `govern_no_new_symbols` |
| `drop-WF-decodeNorm_name` | `.WF` dropped from `decodeNorm_name` (F-raw item 4, `Examples.lean:748`) | `Theorems.lean:764` |
| `drop-WF-decodeNorm_name_top` | the soft chain reads by `toList` (F-raw item 4) | `Theorems.lean:750` (`members_get` needs it) |
| `drop-WF-govern_strings` | `.WF` dropped (F-raw item 2, `Examples.lean:738`) | `Theorems.lean:1134` |
| `drop-WF-govern_no_new_symbols` | `.WF` dropped (F-raw item 2) | `Theorems.lean:1151` |
| `drop-WF-govern_preserves` | `.WF` dropped (F-raw items 1 and 3, `Examples.lean:738`, `:743`) | `Theorems.lean:1166` |
| `tm-BlockBound-body-true`, `tm-BlockBound-body-false` | proof kills of the allowed mechanical mutants | `Theorems.lean:1153` |
| `tm-HasStr-eq-ne` | proof kill of the allowed mechanical mutant | `Theorems.lean:587` (23 errors) |
| `tm-payload-{frame,reguard,carveOut}-null` | the arms, with proofs (the `#guard` kills them mechanically) | `Theorems.lean:915`, `:932`, `:946` |
| `JsonWF-no-bool-num` (`JsonWF`, fix1 F1) | a document with a boolean or a number is well formed | `Examples.lean:789` `part_wf`, `:824` `leadPart_wf` |

A dropped `.WF` fails where the proof uses it. F-raw's `#guard`s are the mechanised reason it cannot be proved
otherwise: each computes a `govern` answer, or a decoded name, that breaks the statement on a tree no parser builds.

## Trust

`uv run python tools/trust_map.py --check` against `72a241fba` on this HEAD: **PASS** after `--allow`.
- K +0, **S +27**, V +0, all in `lean/VE/Scope/Govern.lean`: `JsonWF` 9, `HasStr` 5, `payload` 6, `BlockBound` 3
  (source ranges in `lean/declarations.txt`) and the 4 lines between them. Theorems are P; F-sym's `inventedC`, `gI`
  and `count` are T.
- Recorded with `--allow` as `SIGNED by standing ruling R16 (DRI-RULINGS.md), sc-1ae, 2026-10-18`; FOLLOW-UPS row
  "## sc-1ae (2026-10-28)".
- Every new trusted definition is named by a theorem, and the check can fail for each:
  `tests/test_scope_lean.py::test_a_govern_definition_no_theorem_uses_is_reported[VE.Scope.JsonWF|HasStr|payload|BlockBound]`.

## Tests

- **Lean**: `lake build` (1,135 jobs) has no error after the merge of main. `python3 lean/audit.py` ran inside
  `regen_generated --write` (`lean-audit-manifests`): PASS, standard axioms only. Every `#guard` and kernel fixture
  holds.
- **Generated files**: `uv run python tools/regen_generated.py --write --skip route-cases`: 32 entries
  (`route-cases` needs the Rust release binary, absent here; this item changes no route; the gate checks it).
- **Gate collection**: `tools/gate_collection.py --check --prebuilt`: 20,025 collected, 4 added, 0 removed, 0
  refused, 0 stale, 0 malformed. No test was removed.
- **Selected tests** (`zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`) on ve-mac-1 at
  `0b8da307c` (clean; this report follows): 430 of 481 units, exit 0, 0 failed. No test of `main-known-red.txt`
  failed.
- **fix1**: `lake build` (1,135 jobs) and `python3 lean/audit.py` PASS; `regen_generated --check` 33 entries;
  `trust_map.py --check` S +27 (unchanged); `gate_collection.py --check --prebuilt`: 20,028 collected, 7 added, 0
  removed. Selected tests on ve-mac-1 at `c8991ddcf`: 1 failed, `tests/test_trust_mutants.py::test_the_truth_table_statuses`
  (it read a SURVIVOR's detail as empty; fixed in `418fdd5d1`), and every other selected file exit 0; then
  `tests/test_trust_mutants.py` in full at `418fdd5d1`'s tree: 348 passed. No test of `main-known-red.txt` failed.
- **fix2**: see "Tests (fix2)" below.
- **Full gate**: not run by me, as the task says; the chain runs it on the final HEAD.

## Pilot bytes (estimate)

0. The item adds statements and their definitions; no answer of any route changes.

## Next items

- **sc-1aeb**: `govern_provenance` under `JsonWF D.doc`, on this item's lemmas.
- **sc-1af**: the parser condition, as a route change (see "The parser lemma").
- **sc-3ac** (`title_identity`, rank 88), on the same files: `JsonWF` is in `Govern.lean`, and `govern_preserves`'
  lemmas (`unitsOf_patch`, `setObjVal_ne`, `patch_src`) cover `patch` writing the document back.

## Self-review against BUILDER-CHECKLIST

1. **Every Lean answer is fully typed and contained.** N.A.: no route, response or relay changes.
2. **Every required deliverable is built.** PASS with two cuts, each by a rule the task names: "Plan rows" lists each
   row with its place; `govern_provenance` is cut by the size rule (sc-1aeb), and the parser lemma by the decision's
   own clause (sc-1af). No Python copy of a Lean decision, no report test; no in-flight branch overlaps ("Overlap check").
3. **Your tests and gates can fail.** PASS: 18 hand mutants (`mutants.json`, each failing the build at a named
   proof); `trust_mutants` exit 0 (`trust-mutants.json`); `tests/test_scope_lean.py::test_a_govern_definition_no_theorem_uses_is_reported[VE.Scope.HasStr]` (and the other three).
4. **Python, Lean and Rust agree; valid inputs pass.** N.A. for agreement (Lean only). Valid inputs: F-sym's answer
   (`Examples.lean:757`) and every earlier `govern` fixture still holds (`lake build VE.Scope.Examples`).
5. **R8 binding.** N.A.: no relayed field.
6. **Gate evidence matches the final HEAD.** PASS as far as I take it: synced with main (`a93aa5df3`), regenerated,
   committed and clean; the evidence commit list below is `git log --no-merges main..HEAD`; the chain runs the gate.
7. **No unsigned item.** PASS: DELTA row 1 cites the DRI's decision of 2026-10-27 item 2 with its condition tests;
   row 2 cites R16 and meets it (27 <= 150, K +0, itemised, exercised, FOLLOW-UPS row). No signature reserved.
8. **Every user-visible change in DELTA.** PASS: no answer changes (DELTA.md: no computing definition is edited);
   the statement change is row 1.
9. **Test selection finds the tests.** PASS: `select_tests.py --base $(git merge-base HEAD main)` selects 430 of 481
   units, among them `lake build` and `tests/test_scope_lean.py`, which every hand mutant fails.
10. **Lean statements say what is claimed.** PASS: `statement-diff.txt` (the four theorems are spec 5.1's text plus
    the DRI-signed hypothesis; `HasStr`, `payload`, `BlockBound` exact; `JsonWF` the stub's text); the added
    hypothesis has the DRI's ruling and F-raw as its mechanised counterexample.
11. **Budgets fail closed.** N.A.: no budget or limit is touched.
12. **No CPU or memory regression.** N.A.: no executable code changes (`payload` is read by no route).
13. **Test-removed trailers.** PASS: `tools/gate_collection.py --check --prebuilt`: 0 refused, 0 stale, 0
    malformed; no test removed.

## Evidence commit list (`git log --no-merges main..HEAD`, before this report's commit)

```
0b8da307c sc-1ae: trust_mutants evidence after the merge of main (3 killed, 4 allowed, exit 0)
3aa5f8151 sc-1ae: regenerate after the merge of main
9a7ba6971 sc-1ae: DELTA (the DRI-signed hypothesis, R16 trust), statement diff; the can-fail test names the four new definitions
fa2364c33 sc-1ae: SCOPE.md: the four statements, F-sym; provenance sc-1aeb, the parser lemma sc-1af
aec3e09c6 sc-1ae: trust_mutants evidence on the final allow file (exit 0)
01e32cc8f sc-1ae: mutants and allow file name hasStr_null, the proof at Theorems.lean:587
43ef482e5 sc-1ae: trust_mutants rescored (3 killed, 4 allowed, exit 0); 18 hand-seeded Lean mutants with the proof or fixture each breaks
901643410 sc-1ae: regenerate; first trust_mutants run kept as trust-mutants-run1.json
16d45df83 sc-1ae: payload's fixture as a #guard (the mechanical mutants of its arms); trust_mutants evidence and allow file for the Prop definitions
ab23e195a sc-1ae: trust classes (S: JsonWF, HasStr, payload, BlockBound; T: F-sym fixtures); R16 allowance S +27, K +0
cefbd9d37 sc-1ae: rename hasStr_set' (the audit reads no primed name); regenerate
d1e2702b4 sc-1ae: JsonWF, HasStr, payload, BlockBound; decodeNorm_name, govern_strings, govern_no_new_symbols, govern_preserves under JsonWF (the DRI's fix (a)); F-sym and definition fixtures
```

## FIXMAP
Files:
- `lean/VE/Scope/Govern.lean`: spec 4.2's `HasStr`, `payload`, `BlockBound` and spec 11.3's `JsonWF` (section "What the statements of 5.1 claim", after `govern`).
- `lean/VE/Scope/Theorems.lean`: section `Statements` (from `:571` to the end): the JSON lemmas, the decoder walk, the composed-rule and `patch` lemmas, and the four theorems.
- `lean/VE/Scope/Examples.lean`: F-sym and the definitions' fixtures (`:751`-`:784`); F-raw (`:727`-`:749`) unchanged.
- `lean/SCOPE.md`: the theorem and fixture lists.
- `tests/test_scope_lean.py`: the can-fail case list of `test_a_govern_definition_no_theorem_uses_is_reported`.
- `tools/trust-classes.json`, `docs/trust-baseline.json`: classes (S, T) and the R16 allowance.
- `docs/scope/sc-1ae/`: REPORT, DELTA, statement diff, mutants, trust-mutants evidence and allow file.
Definitions and theorems (spec section -> place):
- 11.3 `JsonWF` -> Govern.lean:283; 4.2 `HasStr` -> :292, `payload` -> :298, `BlockBound` -> :305
- 5.1 `decodeNorm_name` -> Theorems.lean:762 (`decodeNorm_name_top` :724, `ruleFields_name` :663, `normFields_name` :626, `w1_name` :650)
- 5.1 `govern_strings` -> Theorems.lean:1130 (`patch_src` :1085, `composed_src` :967, `baseObj_src` :884, `applyEffect_src` :919, `fold_src` :951, `addOver_src` :1013, `edgesOf_name` :1105, `comp_entry` :1121, `govern_ok` :981)
- 5.1 `govern_no_new_symbols` -> Theorems.lean:1149
- 5.1 `govern_preserves` -> Theorems.lean:1157 (`unitsOf_patch` :1064, `setObjVal_ne` :1049, `idOf_set` :1061)
- JSON lemmas: `getObjVal_map` :617 (any `Impl`, via `impl_get_map`), `mkObj_get_mem` :768, `hasStr_set` :790, `hasStr_substOwn` :833, `jsonWF_top` :758
- 7.1 F-sym -> Examples.lean:751; its document well formed (`parts_wf`, `hcDoc_wf`, `part_wf`, `leadPart_wf`) and `govern_no_new_symbols` on it -> Examples.lean:768 (fix1 F1); `jsonWF_mkObj` -> Theorems.lean:778
- fix2 F6 class: `tools/trust_mutants.py` `Mutant.raw_detail`, `allowed` (records it), `previous` (reads it; refuses an allowed row without it), `Reads.verdict`, the `--json` rows; tests `tests/test_trust_mutants.py::test_rescore_reads_the_whole_verdict_before_allow`, `::test_rescore_of_evidence_whose_mutants_differ_is_a_full_run`, `::test_a_constructor_no_proof_reads_*` (its rescore of allowed evidence)
- fix1 F1 class: `tools/trust_mutants.py` `ctor-drop` (in `mutants`), the SURVIVOR detail (in `run`), `allowed`; tests `tests/test_trust_mutants.py::test_the_generator_drops_each_constructor_*`, `::test_a_constructor_no_proof_reads_*`
Regression commands:
- `cd lean && PATH=~/.elan/bin:$PATH lake build VE.Scope.Examples` (every proof and fixture of this item)
- `uv run pytest -q tests/test_scope_lean.py`
- `python3 docs/scope/sc-1ac/evidence/spec_diff.py` (statements against the spec)
- `uv run python tools/trust_map.py --check`
Generated files: `lean/declarations.txt`, `lean/statements.txt`, `lean/predicates.txt`, `lean/VE/Audit.lean`, `lean/axioms.txt`, `lean/checkers.lock`: `uv run python tools/regen_generated.py --write` (`--skip route-cases` without the Rust release binary). The audit rejects primed theorem names.
trust_mutants: `zsh /home/seyran/code/manage-agents/mac-pytest.sh --trustmut -- --max-mutants 1000 --allow docs/scope/sc-1ae/trust-mutants-allow.json --rescore docs/scope/sc-1ae/trust-mutants.json --json docs/scope/sc-1ae/trust-mutants.json`
Hand mutants: the 19 edits in `docs/scope/sc-1ae/mutants.json` (`mutation.from` -> `mutation.to`), each built with the regression build above.
## END FIXMAP
