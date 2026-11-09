# pe-1 REPORT: the `VE.Purposes` core (PE-1, honest version, L1 only)

No DRI signature is reserved. The size line binds, so (3) is cut at the seam the task names (after (2)):
`FOLLOW-UP: pe-1b`, below.

Plan and spec: `docs/spec/purpose-explanation-PLAN.md` "PE-1" and `docs/spec/purpose-explanation.md` sections 1-4, 9
and 11.1. Both are copied verbatim from 611a58063 (commit 7fd29ba0f; `git diff --stat 611a58063 HEAD -- docs/spec/purpose-explanation-PLAN.md
docs/spec/purpose-explanation.md` is empty). The build was paused 2026-11-04 (family re-audit) at 6b26a0003. It resumed 2026-11-08
(pe-1.held-lifted-20261108T1437Z.md: "merge main first, then finish the task"). Main a6d0d389a was merged cleanly in
e39a245f3.

## Delivered

F1 review fix: the required `NotChecked` type and all five constructors are restored in `Decl.lean`. The review's
probe failed with `lean.unknownIdentifier` before the fix and prints `VE.Purposes.NotChecked : Type` after it.
`Examples.notChecked_cases` proves the constructors exhaustive; its adjacent `#guard` checks they are distinct.
Renaming each constructor alone in a temporary copy of `Decl.lean` made the matching `#check` fail. This exercises
the full declaration class while `eligible` remains PE-2's user.

| Plan row / deliverable | Where | Evidence |
|---|---|---|
| (1) `Decl.lean`: `Relation` (no `prevents`), `Polarity`, `Share`, `Ref`, `Link`, `Block`, `maxLinks`, `NotChecked` (all five constructors) and the three `Relation` theorems | fab019c2d; F1 fix | `lake build` (1324 jobs, 0 errors); `Examples.notChecked_cases` and the distinctness `#guard` |
| (1) `Wire.lean`: `decodeBlock` (exact fields, `prevents` refused, F5), `renderBlock`, `decodeBlock_render`, `decodeBlock_relations` | b07d1ed28 | the wire #guards in `Examples.lean` (spec 7.1 texts) |
| (1) `WellFormed.lean`: `check` in spec 7.2's fault order, `shareOk`, `markerAgrees`, `markerHonest`, `nonfactive`, `sideAdjacent`, `WellFormed`, `check_ok_iff` and every other spec 4.4 theorem except the † ones | 655d9fcce | `python3 lean/audit.py`: "PASS: 791 source files; 8782 named theorem declarations audited" |
| (1) `Route/Inert.lean` (namespace `VE.Route.Admission`): `Kind.inert`, `Kind.inert_active`, `inert_unnamed`, `admit_inert`, `normRole_inert`, `inForce_inert` (D8a). `Route/Admission.lean` is not edited | fab019c2d | `git diff --stat $(git merge-base HEAD main) -- lean/VE/Route/Admission.lean` is empty |
| (2) `Examples.lean`: F1-F8 with F7e, F7f, F8a, F8b and every mutant the plan lists for them, plus the decoder's texts | 8b18582da | `lake build VE.Purposes.Examples`: 0 errors |
| R16: a fixture for each surviving trust mutant ("Each part of the check alone") | 517c1d279 | `trust-mutants.json` exit 0 |
| (4) the S5 amendment (D3), proposed to `docs/spec/document.md`'s owner | this report | below; `document.md` is not edited |
| Generated files (`lean/VE.lean`, `lean/VE/Audit.lean`, inventories, codemap) | 6b26a0003, 014f05dfb | `uv run python tools/regen_generated.py --write --skip route-cases` ("wrote 35 entries"); `tools/lean_statements.py`: "removed: 0, changed: 0" (additions only) |

Statements: every statement of spec 1.1, 1.2, 3 and 4.4 that is not marked † is proved. A mechanical comparison of each
spec statement with its Lean text, after normalising whitespace, gives SAME for 19 of 20. The 20th,
`decodeBlock_relations`, names its unused hypothesis `_h` (the unused-variable lint), so its meaning is the same.
The four † statements (`packsInert_iff`, `packsInert_nil`, `shownUnder_iff`, `unlinkedActive_iff`) are pe-1b's.

The kinds come from main's W2 decoder. `Part.kind` is `VE.Route.Admission.Kind`, the type that main's
`VE.Route.Admission.decodeKind` produces. This item adds no kind parser and no loader: `Wire.lean` decodes only
the link words (`relation`, `polarity`, `share`) and ids. The typed checked-document view (plan order item 3) is not
on main (`grep -rln "checkDocSetsView\|CheckedView" lean/VE` finds nothing). So nothing builds `Units` from a
document yet; the projection is PE-2's (spec 5.1). `relations` is reused (D9): `decodeBlock_relations`
and `Relation.wire_mem` read `VE.Route.Admission.relations`.

## Not delivered (cut, with where it goes)

- **(3) PE-R11 and PE-R8 → pe-1b.** These are `Part.readings`, `Units.packSources`, `packsInert` (with `check` step 6a
  and its `WellFormed` conjunct), `targetKind`, `holdsTarget`, `shownUnder`, `unlinkedActive`, the four † theorems,
  fixtures F2c, F2d, F2e, F9, F9a and F10, F3's `unlinkedActive = []`, and the plan's four seeded bugs for them.
  - Why: the size line. The hand-written Lean is 986 lines (`git diff --numstat $(git merge-base HEAD main)`:
    Decl 68, Wire 287, WellFormed 280, Examples 272, Inert 79). (1)-(2) alone were already about 950 lines at the
    pause. The task names this seam ("the seam if the size line binds is after (2)").
  - What pe-1b changes: `check` and `WellFormed` get the 6a step and conjunct. `check_ok_iff`'s statement keeps its
    form, but its right side gains `packsInert U L = true`, as spec 4.4 writes it.
- **The stub elaboration for pe-1b is done.** The task's first step was run before the cut, against main.
  - I applied spec 4.1-4.4's † text to `WellFormed.lean` (theorems with `sorry`), built it, `#eval`ed the fixtures,
    and reverted the change. Nothing was committed.
  - Every † statement elaborates.
  - `check_ok_iff`'s existing proof closes with the 6a conjunct added.
  - Every existing #guard still passes with the defaulted fields.
  - The `#eval` values all equal the plan's:
    - F2c and F2d: "InvalidPurposes: link l1 has a side the text does not state, and a pack takes a premise from it".
    - F2e: `.ok ()`.
    - F9 (61 B): `.ok ()`, `shownUnder = [("f.p3", ["rationale", "limiting"])]`, `unlinkedActive = []`.
    - F9a: `.ok ()`, `shownUnder = [("f.p3", [])]`.
    - F10 (68 B): `.ok ()`, `shownUnder = []`, `unlinkedActive = ["g.p1"]`.
    - F3: `unlinkedActive = []`.
    - F1, F2 and F8: `shownUnder = []`.
  - So pe-1b needs no DRI question.
- **`eligible` (spec 6.3) → PE-2**, its first user. The `NotChecked` vocabulary it consumes is delivered in PE-1.
- **Regen skipped `route-cases` only.** Its writer needs the Rust release binary, which this worktree has not
  built ("missing Rust executable"). This branch changes none of its inputs, and the file is main's.

## Seeded bugs (Lean; the only language changed)

The method is recorded in `mutants.json`'s `command`. Each bug is planted alone, in memory, in its module. The
mutated module(s) and `Examples.lean` are elaborated as one file with `lake env lean`, so a broken proof does not
hide the failing #guards behind it. A control run with no mutation reports 0 errors. Nothing in the checkout is
written.

| # | Plan bug | File | Fails |
|---|---|---|---|
| 1 | `shareOk` counting a duplicate link as a rival | `lean/VE/Purposes/WellFormed.lean` (`rivals`) | F7a, `Examples.lean:157`; `shareOk_iff` |
| 2 | `markerAgrees` ignoring slot order | `WellFormed.lean` | F1 swap, `Examples.lean:53` |
| 3 | `nonfactive` checking only `asserted` | `WellFormed.lean` | F1 norm purpose, `Examples.lean:56` (and the `definition` one at :57); `nonfactive_iff` |
| 4 | `nonfactive` ignoring reading candidates | `WellFormed.lean` | F1 candidate, `Examples.lean:58`; `nonfactive_iff` |
| 5 | `markerHonest` always true | `WellFormed.lean` | F1 LABELLED, `Examples.lean:61`; `markerHonest_labelled` |
| 6 | `Kind.inert` admitting `norm` | `lean/VE/Route/Inert.lean` | `normRole_inert` (Inert.lean:72), F1 norm purpose (`Examples.lean:56`), the 9.1 #guard (:38) |
| 7 | `shareOk` ignoring the other link's share | `WellFormed.lean` | F7e `Examples.lean:162`, F7f :163; `shareOk_iff` |
| 8 | `sideAdjacent` touching only | `WellFormed.lean` | F8a, `Examples.lean:182`; `sideAdjacent_iff` |
| 9 | `sideAdjacent` order only | `WellFormed.lean` | F8b, `Examples.lean:183`; `sideAdjacent_iff` |

The plan's other four (`packsInert` twice, `holdsTarget`, `unlinkedActive`) go to pe-1b with their code.

Five more hand-planted mutants cover the trusted definitions that got no killed trust mutant:
- `Link.slots` (an unswapped `inOrderTo`): fails F1 at `Examples.lean:52`.
- `Units.kind?` (a constant kind): fails F1 at :52.
- `Ref.partId?` (a mention read as a part): fails F5's mention fixture at :131.
- `shareOf` (an absent share read as `sole`): fails :243.
- `wordOf` (refusing a known word): fails :242, and also breaks `decodeLink_render`.

## Trust (R16)

`python tools/trust_map.py --check` after the F1 fix: "against a6d0d389a07b: K +0, S +133, D +121, G +26,
tied +141, unclassified +0, trusted +149 … PASS: K, S and untied [V] within a6d0d389a07b and the allowances
introduced since". The original allowance is `SIGNED by standing ruling R16 (DRI-RULINGS.md), pe-1, 2026-10-18`;
the F1 allowance is `SIGNED by standing ruling R16 (DRI-RULINGS.md), pe-1 F1, 2026-11-08`
(`docs/trust-baseline.json`). DELTA.md rows 1–2 itemise the growth per file:
- WellFormed.lean +77 S
- Decl.lean +51 S, including `NotChecked`'s five constructors (+9)
- Inert.lean +5 S
- Wire.lean +16 untied D[V] (`wordOf`, `linksOf`); `shareOf_render` ties `shareOf` (-7)

The classes, in `tools/trust-classes.json`:
- **S:** the meaning definitions and types.
- **C, tied by `check_ok_iff`:** `check`.
- **G[V], tied by their `_iff`/`_eq` theorems:** `nonfactive`, `shareOk`, `sideAdjacent`, `unstated`.
- **D[V], tied by their `_ok`/`_render`/`ofWire_wire` theorems:** the decoders, the encoders and the wire words.
- **D[R]:** `linkFields`, `linkFieldsOk`, `sideText`.
- **T:** the fixtures.

R16's conditions:
- 149 ≤ 150, and K +0.
- **Every new trusted definition is exercised by a check that can fail.**
  - The run: `zsh mac-pytest.sh --trustmut -- --max-mutants 1000 --test lean/VE/Purposes/Examples.lean --allow
    docs/purpose-explanation/pe-1/trust-mutants-allow.json --json docs/purpose-explanation/pe-1/trust-mutants.json`.
  - Its history: the first run was at f482b1c53. Two `--rescore` runs followed the fixture commit 517c1d279; the
    prior final one was at 3a816e76f. The F1 run at 70b7564d produced five UNKNOWN constructor drops. Its
    `--rescore` with the exact `NotChecked`/`ctor-drop` allowance exited 0: **KILLED 154, INVALID 32,
    ALLOWED 109, SURVIVOR 0, UNKNOWN 0, NOT RUN 0.** The five removals each fail the named constructor check.
  - The allow file gives one reason per definition and operator:
    - The Prop `WellFormed`. Each mutant breaks `check_ok_iff` (WellFormed.lean:151). Each also fails the
      `wf` #guards, which decide `WellFormed`; the tool reads those failures as UNKNOWN because the `Decidable`
      instance changes with the mutant.
    - Type-error mutants (a list put where a `Units`, an `Option` or a pair is), which the tool reads as UNKNOWN.
    - Constructor drops: a name error at each constructor's users.
    - Equivalent mutants: `take 1` under `isEmpty`, and the `isSome` conjunct that `sameUnit` implies. Dropping
      the marker's own id from `sameUnit`'s parent check is equivalent too.
    - `body-true`/`body-false` of `sideOfKind` and `covered`. Their direct #guards refute these; the tool reports
      UNKNOWN because Lean shares their `Option` matcher with a later definition.
    - `Kind.inert`'s `bool-flip`, refuted by the #guard at `Examples.lean:40` with a message the tool leaves
      unexplained.
  - In the prior record, the allowed mutants' raw verdicts were 98 UNKNOWN and 6 SURVIVOR. The F1 record has
    103 UNKNOWN (including the five constructor drops) and the same 6 equivalent SURVIVOR cases:
    `sideOfKind` and `rivals` each have `list-first` and `list-last`; the other two are `sameUnit`
    `list-drop-first` on `L.partIds` and `WellFormed` `eq-le` on `isSome`.
  - `Link` and `Block`, structures that no operator mutates, are read by every #guard.
- The FOLLOW-UPS.md row is under "## pe-1" (ties pass).

## Tests

- Lean: `cd lean && lake build` gives "Build completed successfully (1324 jobs)". `python3 lean/audit.py` gives PASS.
- `uv run python tools/gate_collection.py --check --prebuilt`: "32851 collected … 0 added, 0 removed by a trailer,
  0 refused, 0 stale and 0 malformed trailers".
- Selected tests, run once on 71866bc0e (`zsh mac-pytest.sh --select -- --base $(git merge-base HEAD main) --run`,
  on ve-mac-1): "1 failed, 138 passed" in the last pytest batch; the runner's summary line is "exit=1; failed/error
  ids=1" (177 units recorded).
  - The failure was `tests/test_assurance_manifest.py::test_every_json_handling_lean_file_is_classified`. It is not in
    main-known-red.txt.
  - Cause: the two new Lean files that handle JSON (`Purposes/Wire.lean`, `Purposes/Examples.lean`) had no entry in
    `ve/assurance-manifest.json`.
  - Fix (the next commit): two `other_json` entries, following `lean/VE/Events/Wire.lean`'s precedent ("no service
    mode, route or runner path reaches it until …").
  - Rerun: `uv run pytest -q tests/test_assurance_manifest.py` gives "139 passed".
- Deviation from the task's file list ("no ve/ file"): `ve/assurance-manifest.json` gains those two data entries,
  which the test requires. No Python file changes.
- No Python or Rust file changes, so the relay, schema and R8-binding rules have no new answer to bind. No
  route, mode or relay calls `VE.Purposes`.

## Pilot bytes

Estimate: 0, as the plan says. Nothing calls the code, so no answer, verdict or byte changes. Nothing is claimed
before a pilot audit.

## The S5 amendment (D3), proposed to `docs/spec/document.md`'s owner

Proposed sentence, after "lists for `attributed`, `hedged`, `causal`, and `unformalised`.":

> In `["causal", r, c, e]`, `c` is the kind of the cause side and `e` the kind of the effect side: for `"because"`,
> `c` is the reason's kind and `e` the kind of what it is a reason for; for `"in order to"`, `c` is the kind of the
> means (the rule or act) and `e` the kind of the purpose.

No fixture or merged plan on main uses the opposite order. A grep of every .json, .jsonl, .md and .lean file finds
`["causal","because","asserted","asserted"]` 4 times, which is symmetric, and the plan's own two examples. So D3 stands
as written (DRI 2(g)). `document.md` is not edited here.

`FOLLOW-UP: pe-1-doc-s5 add the one-sentence causal slot-order amendment (purpose-explanation D3, S5) to docs/spec/document.md (owner: document model)`

## Next items

- `FOLLOW-UP: pe-1b PE-R11 and PE-R8 in VE.Purposes: packsInert (check step 6a and its WellFormed conjunct), targetKind, holdsTarget, shownUnder, unlinkedActive, their four theorems, F2c-F2e, F9, F9a, F10, F3's [] and the plan's four seeded bugs (statements elaborated and values computed in pe-1's REPORT)`
- `FOLLOW-UP: pe-2-eligible use Decl's NotChecked in eligible (spec 6.3) in PE-2`
- pe-2 (the `purposes` block in the document mode) follows pe-1b. PE-E1 sits beside it.

## Spec re-read

- `Relation`, `Polarity`, `Share`, `Ref`, `Link`, `Block`, `maxLinks`, `NotChecked`, `Relation.wire`, `Relation.ofWire?`,
  `Share.wire` against spec 1.1-1.2 (`purpose-explanation.md` lines 59-176): the same text after normalising
  whitespace.
- `Units.find?`, `Units.kind?`, `Ref.partId?`, `Link.partIds`, `Link.slots`, `sideOfKind`, `markerAgrees`,
  `sameUnit`, `sideAdjacent`, `sidesAdjacent`, `rivals`, `shareOk`, `markersLinked`, `covered`, `unstated`,
  `nonfactive`, `markerHonest` against spec 4.2 (lines 540-656): the same text.
- `check` against spec 4.3 (lines 658-683): the same faults, in the same order, with the same texts. It is written
  with `VE.Route.Gate.require` instead of `unless … throw`, and `check_ok_iff` proves it equal to `WellFormed`.
  The 6a step is pe-1b's.
- `WellFormed`, `Part` and `Units` against spec 4.1 and 4.4: the same, without the † `packsInert` conjunct and the
  † `readings` and `packSources` fields (pe-1b).
- Every theorem statement of spec 1, 3 and 4.4 against its Lean text: the same (above).
- `Kind.inert` against spec 3 (lines 454-505): the same five kinds.
- The fixture texts and byte offsets against plan lines 958-1022: F1 is 109 B (#guard), F8 is 15 B, F9 is 61 B,
  F10 is 68 B (`#eval`).

## Self-review against BUILDER-CHECKLIST

1. N.A.: no Lean answer reaches a relay. No route, mode or schema is added (no Python or Rust file changes; the one `ve/` change is the manifest's data entry).
2. PASS: the Delivered and Not delivered tables. The cut of (3) is at the seam the task names. `NotChecked` is
   delivered here; `eligible` remains with its first user. No Python copy of a Lean decision, and no report test. No in-flight branch touches these files:
   `git diff --name-only main...<branch>` for every `feature/*`, `lean-first/*`, `infra/*` and `foundation/*` branch
   not on main finds no `lean/VE/Purposes/`, `lean/VE/Route/Inert.lean` or `docs/spec/purpose-explanation*`.
3. PASS: 9 plan seeded bugs and 5 hand-planted mutants, each failing a named #guard (`mutants.json`). The trust
   mutants exit 0 (`trust-mutants.json`). The allow entries name exact definitions and operators.
4. N.A.: no Python or Rust path computes these checks; there is one owner, Lean.
5. N.A.: no field is relayed to Python.
6. PASS: main was merged first (e39a245f3). The gate runs on the committed final HEAD (the chain's step). Evidence
   names its commits.
7. PASS: DELTA.md row 1 cites R16, with the trust-mutant evidence that R16 asks for.
8. PASS: DELTA.md says "no user-visible delta". No code path calls `VE.Purposes`
   (`grep -rn "VE.Purposes" lean/VE --include=*.lean` finds only the Purposes modules, the generated
   `lean/VE.lean` and `lean/VE/Audit.lean`).
9. PASS: the selection (`tools/select_tests.py --base $(git merge-base HEAD main)`) held the one test the change broke (`test_every_json_handling_lean_file_is_classified`, above), so the selection finds this branch's tests.
10. PASS: each seeded bug breaks the proof it should (`shareOk_iff`, `nonfactive_iff`, `markerHonest_labelled`,
    `normRole_inert`, `sideAdjacent_iff`). The statements are the spec's (Spec re-read). No `tools/check_*_statements.py`
    covers purposes.
11. PASS: `check` counts the links against `maxLinks` before any other step, and `decodeBlock` counts the array
    before decoding a link (#guards: 257 links give "ResourceLimit: purposes links exceed 256", 256 pass; 256 bad
    entries are refused on the first one). This item adds no evaluator and no clock.
12. N.A.: no route calls the code, so no pilot time changes.
13. PASS: no test removed (`gate_collection.py --check --prebuilt`: 0 removed, 0 stale, 0 malformed).
14. PASS: both directions in every fixture group (F1-F8 pass and fail; each part's #guards accept and refuse). Each
    claim here cites its command. Spec re-read above.
15. PASS:
    - Overclaim: "every statement of spec 1-4 proved" is limited to the non-† ones, and (3) is written as cut.
    - Cut: at the seam the task names.
    - Every new check can fail: the seeded bugs and trust mutants.
    - Limits before work: item 11.
