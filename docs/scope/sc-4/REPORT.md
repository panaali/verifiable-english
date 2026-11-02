# sc-4 report: far precedence and forward exceptions (SC-4)

- **Status:** built; no DRI signature outstanding. Two DRI decisions were taken during the build and signed their
  rows (reviews/dri-decisions-20261101-sc-4.md, reviews/dri-decisions-20261101-sc-4-edges.md).
- **Changed:** `scope@0` gains the `forward` member, `(unit w, rule r, anchor a)`. `forwardCheck` runs as step 9 of
  `admitBlock`, with or without governors, and more than 256 declarations are a `ResourceLimit`. Proved verbatim:
  `forward_exception_sound`, `forward_exception_complete`, `no_effect_refused`. The 7.6 fixtures F11 to F12-f0 are
  `#guard`s, each with the exact text of its refusal.
- **Cut, under the edges decision's fallback:** `precedes_edges` and `yields_edges` with `(hw : JsonWF D.doc)` move to
  sc-4b. **Open:** F15 (a candidate, 7.6) and the forward declaration's status fold (1.6).

## Plan rows (task "Deliver", scope-PLAN.md SC-4, spec 1.9, 5.6, 7.6, 6.1 `admitBlock`)

| Row | Delivered | Where |
| --- | --- | --- |
| (1) what main has | `edgesOf` and the `ScopeNoEffect` check in `govern` and `governBody` (sc-1ad, Govern.lean at 9635574eb; the fixtures are at Examples.lean:588-614). `precedes_edges`, `yields_edges` and `no_effect_refused` were not stated or proved on main (`grep -rn` over lean/ and tests/ finds none) | — |
| (2) the declaration on the wire, `forwardCheck`, step 9 before the identity shortcut | yes: `SDoc.forwards`, `decodeForward`, `decodeParts` (Wire.lean); `laterUnitsIn`, `forwardCheck` (5.6's text), `forwardsOk`, `admitBlock`'s last step (Govern.lean) | a31ff965a |
| (3) `forward_exception_sound`, `_complete` | yes, 5.6's text verbatim (`tests/test_scope_5_6_statements.py`) | FarTheorems.lean |
| (4) the graph theorems still missing | `no_effect_refused` is proved verbatim. `precedes_edges` and `yields_edges` are false as written: F-raw-edges (`FarExamples.lean:129-150`) gives the premises `[false, true, true, true, false]` on a raw unit tree and all true on the well-formed document. The DRI signed `(hw : JsonWF D.doc)` and set a fallback; I took it (size, below) | FarTheorems.lean; sc-4b |
| (5) the 7.6 fixtures on both sides | F11 `:40`, F11-a `:45`, F11-y `:49`, F11′ `:51`, F11-u `:52`, F11″ `:64` (W1's `DependencyCycle: r3a, r9`, acyclic without the governor), F12 `:79-81`, F12-f `:106-107`, F12-f0 `:112-115` (FarExamples.lean). F15 is not a fixture | db1446e0c |
| F12 | not recorded: the pinned u0047.s05-s06 (no content, `meaning: {"unformalised": "norms"}`) is returned as written, and a guessed declaration is refused (`ScopeForward: u0047.s06: …`) | FarExamples.lean:79-81 |
| DELTA: a document without the member answers byte-identically | yes: main's answers were recorded with main's own service (`docs/scope/sc-4/record_absent.py`). With main's binary, a block that has the member gives `InvalidInput: scope@0 unknown member scope.forward`, so the recording ran on main | tests/test_scope_forward.py |

The edits in debates/plan-synthesis-2/edits-scope.md (1-7, DEC 10, DEC 16) do not touch SC-4. This item implements
none of them.

## Size and the cut

`git diff --numstat $(git merge-base HEAD main)` counts 581 hand-written lines added (generated files excluded;
side tables and evidence included), before this report. The two proofs need a top-level `JsonWF` chain through
`composed` (`mergeParts`, `applyEffect`), an `over`-array lemma for `decodeNorm` on both chains, and an `addOver`
lemma. sc-2d's `baseObj_jsonWF` and W1 field reader are not on main. My estimate is about 200 lines, so the item
would pass 600. Under the edges decision's fallback, sc-4b takes both theorems, their statement change, the 5.6 text
update and the `over` lemma. sc-4 changes no statement, and the 5.6 statement test checks that neither theorem is
stated under its name yet.

## The DRI's decisions applied

- **`forward` accepted** (item 1): DELTA row 1, with conditions (a)-(d) as listed there.
- **The bound** (item 2): `ResourceLimit: scope forward declarations` comes after the governors' and the list names'
  bounds in step 1, and before step 2. Measured once, from the command in the build log:
  `uv run python -c "…_answer(forward_text([d]*n, later=64))…"`. The document-mode request with 256 declarations over
  64 later units took 379.8 ms; the same document with no declarations took 61.7 ms. These are wall times of one
  request each, after warm-up, on the VM. For the spec amendment: the 6.1 row is
  `ResourceLimit: scope forward declarations`, more than 256 forward declarations, `admitBlock` 1. The 8.2 limit is
  "forward declarations ≤ 256" (follow-up sc-4-spec-limit).
- **Edges** (edges decision): the fallback was taken (above), so there is no DELTA row for a changed statement.
  F-raw-edges stays as the reason.

## Seeded bugs (Lean is the only product language changed; `docs/scope/sc-4/mutants.json`)

| Id | Bug | Caught by |
| --- | --- | --- |
| M1 | `laterUnitsIn` takes every unit of the anchor (`forwardCheck` accepts an earlier unit) | FarExamples.lean:106, :107 (F12-f's failing side passes), :112 |
| M2 | `edgesOf`/`edgesOfF` drop the same-predicate condition | FarExamples.lean:40, :45, :51 (F11′); Examples.lean:594, :627 |
| M3 | bound `> 257` | FarExamples.lean:121, :125 |
| M4 | `forwardsOk` checks only the first declaration | FarExamples.lean:117 |
| M5 | `forwardCheck` answers `.ok ()` on refusal | FarTheorems.lean:78 (`forward_exception_sound`), FarExamples.lean:80, :107, :112, :117 |
| M6 | `decodeForward` swaps rule and anchor | WireExamples.lean:62 |
| M7 | `decodeParts` drops the declarations | WireExamples.lean:62, :69 |

## Trust

`uv run python tools/trust_map.py --check` against 9635574ebf2b gives K +0, S +1 (`SDoc.forwards`), untied V +1
(`decodeParts`), trusted +2. The other four definitions are reject-only: G[R] `laterUnitsIn`, `forwardCheck`,
`forwardsOk` and D[R] `decodeForward`. This is SIGNED by standing ruling R16, with the allowance in
docs/trust-baseline.json and the FOLLOW-UPS.md row under `## sc-4`. The trust mutants
(`mac-pytest.sh --trustmut`, rescored at 482c94133's Lean) give 18 KILLED, 0 SURVIVOR, 0 UNKNOWN, 8 INVALID and
2 ALLOWED (two `decodeBlock` list-empty mutants that do not elaborate): `docs/scope/sc-4/trust-mutants.json`.

## Tests

- `lake build`: Build completed successfully (1215 jobs). `python3 lean/audit.py`: "PASS: 711 source files; 7919
  named theorem declarations audited"; the new theorems use only `propext`, `Classical.choice` and `Quot.sound`
  (lean/axioms.txt).
- Selected tests (`mac-pytest.sh --select` at ae3628d9f; 432 units): the fast stage gave 4 failed, 9792 passed and
  6 skipped. The six cloud shards' results are on `claude/cc-result-sc-4-ae3628d9-t535106-s0`..`s5` (`shard.json`):
  431 units passed. The one failed unit is `test_assurance_manifest.py`, with the same 4 tests (Wire.lean's decoder
  pin and FarExamples' classification). I fixed them in 482c94133, and rerunning the 4 ids gave 4 passed. None is in
  main-known-red.txt.
- Pilot bytes expected to move: 0 (SC-M0: no unit says "notwithstanding", and none is a forward declaration).

## Overlaps with branches in flight

- feature/sc-2d edits Theorems.lean and Examples.lean. My hunks are `admitBlock_drop` and `forwardsOk_drop` near
  :1611, and the `SDoc` literals at Examples.lean:447, :657, :723-725, :979-987. sc-2d's hunks are at :705-760,
  :1867 and :2035+, and Examples.lean:1188+.
- feature/pc-1 edits ScopeAdmission.lean at :266 and :313; mine is `decodeParts_wf` at :206.

## Spec re-read

`laterUnitsIn` and `forwardCheck` were checked against scope.md:1403-1409, and the three statements against
:1398-1417 (the test compares them). The wire member was checked against :430, the texts against :1601 (and the
new limit, above), the order against :1616-1625, and the fixtures against :1735-1747.

## Next items

sc-6 (UDHR rights reach) as planned. Follow-ups: sc-4b (the two graph theorems), sc-4-spec-limit (the DRI's doc
item), and sc-4c: the forward declaration unit's status. Spec 1.6's row gives `governorStatus` over the later rules
it announces, and today the unit keeps the document mode's own status.

## Self-review against BUILDER-CHECKLIST

1. PASS: no new relay field or route. The document mode's answer is unchanged in shape:
   `test_a_document_without_forward_answers_byte_for_byte_as_main`.
2. PASS: the plan rows are above. The one rule break checked is overlaps: sc-2d and pc-1 are listed, with no
   overlapping hunks.
3. PASS: M1-M7 and the trust mutants, which exit 0 (`docs/scope/sc-4/trust-mutants.json`).
4. PASS: the twin check (`test_f12_f_the_passing_declaration_answers_as_its_twin_without_it`) and main's answers. No
   Rust or Python path decides forwards.
5. N.A.: Python reads no new field of a Lean answer. The member is bound by Lean's decoder
   (`test_the_member_is_read_by_leans_decoder`, WireExamples.lean:69-78).
6. PASS: the gate is run by the chain on the final HEAD. Evidence is saved: forward-absent-main.json and the trust
   JSON.
7. PASS: DELTA rows 1-2 cite the DRI decisions, and row 3 cites R16. No signature is outstanding.
8. PASS: DELTA covers the member, its refusals, the bound and the trust lines. Documents without the member are
   unchanged (test above).
9. PASS: `tools/select_tests.py --base …` selects test_scope_forward.py, test_scope_5_6_statements.py and
   test_scope_lean.py.
10. PASS: `tests/test_scope_5_6_statements.py` (with a vacuity check). M5 breaks `forward_exception_sound`.
11. PASS: the 257 bound gives `ResourceLimit` (UNKNOWN), FarExamples.lean:121-127 and
    `test_256_declarations_over_64_later_units_are_admitted_and_257_are_a_resource_limit`. There is no timing assert.
12. PASS: with no declarations the work is unchanged (the byte test). With 256 × 64 the request takes 380 ms against
    62 ms (one measurement, above). No pilot unit has the member.
13. N.A.: no test removed or renamed. WireExamples.lean:62's main guard is changed into the acceptance guard (the
    DRI's item 1).
14. PASS: both directions for each check: F12-f's two sides, 256 and 257, the member with and without, and F11 with
    F11′. Every claim cites a command, and the spec re-read is above.
