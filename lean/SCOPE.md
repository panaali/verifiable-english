# Cross-sentence scope (`scope@0`) in Lean

`scope@0` lets one unit change other units. The first case is a list: a lead-in such as "Claude should never:"
completes each item of the list after it. The design is [docs/spec/scope-PLAN.md](../docs/spec/scope-PLAN.md); the
exact definitions and statements are [docs/spec/scope.md](../docs/spec/scope.md) (sections 1.2-1.5, 4 and 5.1).

This file covers what is built so far: item sc-1a, the layout's list runs, that is, which units a lead-in governs;
item sc-3a, the layout's label reaches and anchors, with discourse's anchor containment and anchor checks moved
into the layout so that one body serves both; and item sc-1ab, the effects on a rule's JSON object (joining the
lead-in's part to each item's part, conditions and `own`, the order table). No route or service mode calls the scope
parts yet. Item sc-1ac adds `govern` and the block's admission; the precedence graph step, the theorems about what
`govern` writes and the run path `governFast` are sc-1ad, the anchor and label reaches and the block's anchor checks
sc-3ab, and the document mode SC-1b (below).

## `VE/Layout/List.lean`: what the source bytes say

The layout is read from the source bytes and each unit's span, never from the wire.

- `Unit`: one unit as the layout sees it. `item = some d` when the unit begins a list item at depth `d`;
  `midLine` when other text precedes it on its line; `lead` when its last non-blank byte is ":"; `label` when it is
  an item that opens with a bold label ending in ":"; `para` is the number of blank lines before it.
- `ofSource`: the layout of every unit, from the source text and the units' byte spans. Its byte tests are
  `lineStart`, `spacesOnly`, `skipSpaces`, `markerLen` (`* `, `- `, `+ `, or digits then `. `), `lastNonBlank`,
  `boldLabel`, `isBlank` and `isDigit`. An item needs an even indentation; depth is half of it.
- `paraCounts`: one pass over the bytes gives the blank-line count at every position.
- `listRun L lead`: the governed items of a lead-in. The lead-in must end with ":" and be followed by an item of
  some depth `d`; the run then continues over items of depth at least `d` and units that begin mid-line, and stops
  at the first other unit. Only the items of depth exactly `d` are governed. Otherwise `NotALeadIn: <unit>`, or
  `ScopeUnknownUnit: <unit>` for a unit the layout does not have. Its helpers are `indexOf`, `continues` and
  `runFrom`.
- `GovernedItem L lead u`: the same thing said independently, by positions: `u` comes after the lead-in, has the
  first item's depth, and every unit between them continues the run.

Theorems:
- `listRun_iff`: when unit ids are distinct, a unit is in a successful run exactly when it is a `GovernedItem`.
- `listRun_ok_iff`: when unit ids are distinct, the run succeeds exactly when the unit exists, ends with ":" and the
  next unit is an item.
- Helpers: `continues_iff`, `mem_runFrom` (a unit is in a run exactly when it is an item of the depth and every unit
  before it continues), `indexOf_iff` (with distinct ids, the index is exactly the unit's position), `listRun_ok`.

Label reach (sc-3a, spec 1.2 "Item units"):
- `itemRun L item`: the units a bold label reaches. The unit must be an item with a bold label (`label`); its reach
  is the item, then every following unit that is a deeper item or begins mid-line, up to the first other unit.
  Otherwise `NotALabel: <unit>`, or `ScopeUnknownUnit: <unit>`. Its helper is `itemFrom`.
- `ItemUnit L item u`: the same said by positions.
- `itemRun_iff`: when unit ids are distinct, a unit is in a successful item run exactly when it is an `ItemUnit`.
  Helpers: `mem_itemFrom`, `itemRun_ok`.

## `VE/Layout/Anchors.lean`: anchors, one owner for discourse and scope

- `within spans anchors u a`: the unit's span lies inside the anchor's. `narrower` and `innermostAnchor`: the
  smallest anchor holding a unit, the first of equal size. These are discourse's bodies, moved here; discourse's
  `within`, `narrower` and `innermostAnchor` call them on its own unit spans and anchors.
- `anchorUnits`: the layout units within an anchor, in source order. `headingOf`: the first of them.
  `anchorReach`: the others, the units a heading reaches; `ScopeUnknownAnchor: <a>` when the anchor holds no unit.
- `anchorsOk anchors defSpans unary`: discourse's anchor checks (its spec 4.1(2)), in order: at most 1,024 anchors,
  distinct ids, one root, every anchor reaches the root inside its parent's span (`reachesRoot`), sibling labels
  distinct without case and sibling spans disjoint, and every export a unary predicate with a definition unit inside
  the anchor. Discourse's `anchorsOk` calls it with its definition units' spans and its environment's unary test.
  The generic checks it uses (`req`, `runAll`, `allOk`, `dupOf`, `spanIn`, `spansDisjoint` and their lemmas) moved
  here from `VE/Discourse/WellFormed.lean` with their names.

Theorems: `anchorReach_iff` (with distinct ids, a unit is in the reach exactly when it is a layout unit within the
anchor and not its heading), `mem_anchorUnits`, `narrower_mem`, `innermost_within` (the innermost anchor holds the
unit; discourse's theorems of the same names now follow from these).

## `VE/Layout/Discourse.lean`: discourse is unchanged

`discourse_within_unchanged`, `discourse_innermost_unchanged` and `discourse_anchorsOk_unchanged`: discourse's three
definitions are the moved bodies on discourse's own spans, anchors, definition spans and environment. That the move
changed no discourse answer is proved against the pre-move bodies on every document, in saved evidence outside the
tree (`docs/scope/sc-3a/evidence/before-bodies.lean.txt`).

## `VE/Scope/Effects.lean` and `VE/Scope/Theorems.lean`: the effects on a rule's JSON object

Scope decodes no rule field: it only joins and rewrites JSON, and the chain's own decoder reads the result.
- `mergeParts u lead item`: the lead-in's part joined to an item's part. Both must be objects; a key on both sides is
  `ScopeConflict: <u>: <key>`, never an override; otherwise the union. It reads each side's members through
  `lookups` (each key once, with the value lookup finds), not `VE.Bridge.fields` as the spec's text does: on a raw
  tree whose keys are out of order the two differ, and the spec's text then breaks `mergeParts_keys`
  (counterfixture `unordered_join`). On every well-formed object, which is every object the JSON parser builds, the
  two are the same (`lookups_fields`, `mergeParts_text`).
- Conditions: in a condition the JSON string `"own"` stands for the governed rule's own guard. `hasOwn` finds it,
  `substOwn g` replaces it by `g` (object keys untouched), `ownSafe` refuses it under `forall` or `exists`, and
  `depthOk` bounds the depth at `depthLimit` (64). All are total by fuel.
- The order table: `Effect` (frame, reguard, carve-out, precedes, yields, title); `narrowing` (`["and", "own", C]`
  with `C` free of `own`); `Commutes`, true only for two narrowings, a narrowing and an own-free carve-out (either
  order) or two own-free carve-outs.

Theorems: `mergeParts_keys` (every key of the joined object comes from exactly one side, with its value),
`mergeParts_conflict` (a key on both sides refuses the join), `substOwn_no_own` (an own-free guard leaves no `own`),
`substOwn_id` (an own-free condition is unchanged), `commutes_symm`. Helpers: `lookups_spec`, `lookups_absent`,
`lookups_fields`, `mkObj_getObjVal`, `firstKeys_mem`, `firstKeys_self`, `hasOwn_mono`, `substOwn_no_own_le`,
`substOwn_id_le`, `impl_map_eq`, `members_obj`.

## `VE/Scope/Govern.lean`: `govern`, the block's admission and the run path (sc-1ac, sc-1ad)

`govern D` returns the complete document with the content of each affected unit replaced by its composed rule, as
the chain's own norm object; the chain's decoder then reads it as if the rule had been written out in full.
- `SDoc`: the layout, the document after RESOLVE, the `scope` block, the governors, the list names, the anchors and
  the chain's decoding environment. A `Governor` is its id, its unit, its `Effect`, its `Reach` and its recorded units.
- The reaches: `coveredLayout` (a list is its lead-in's run; a list name is the run of its lead-in, and its recorded
  units must equal it), `covered` (adds the `rules` reach: the rule units whose base name is one of the names).
  An anchor reach is the layout's `anchorReach` (the anchor's units after its heading) and a label reach its
  `itemRun` (sc-3ab). A frontier reach is refused (`UnsupportedProfile`) until SC-5.
- `baseObj`: a norm's own object, or, under exactly one frame, the frame joined to the unit's part or norm; a part no
  frame covers is `ScopeOrphanPart`, two frames `ScopeOrder`, any other written content `ScopeNotARule`.
- `applyEffect`: `reguard c` makes the guard `c` with `own` replaced by the rule's guard; `carve_out c` appends `c`
  (with `own` replaced) to `unless`; the other effects leave the object. `composed` applies the unit's unary
  governors (`governorsOf`) to its base object in order 1.4 (`ordered`: by reach class, then by the position of the
  governor's unit, stably). `orderCheck` refuses two unary governors on a unit that do not `Commutes`.
- `admitBlock`, before anything else and with or without governors: the limits (256 governors, 256 list names),
  repeated ids and names, unknown units, a vocabulary symbol named `own`, each list name (its scope, its unit, its
  run), then each governor (depth, `own` under a binder, its effect's reach and unit, its recorded units, reading
  sets, units it cannot change). Step 7 (sc-3ab) runs discourse's anchor checks (`VE.Layout.anchorsOk`) on the
  block's anchors, with the definition units' spans (`defSpans`, by `kindOf`) and the environment's unary test; in
  step 8 a non-graph governor of an anchor reach sits on its heading, and of a label reach on its item.
- The graph step (sc-1ad): `ruleTable` decodes, with the chain's own decoder, the composed rule of each unit a
  `precedes` or `yields` governor reads. `edgesOf`: a `precedes` governor's rule goes over each reached rule on its
  predicate with another name; under `yields`, each such rule goes over the governor's rule. `addOver` appends each
  new name to `over` once.
- `govern`: with no governor, the document itself or `ScopeOrphanPart`; otherwise `orderCheck`, the composition of
  every `affected` unit, `ruleTable`, `ScopeNoEffect` for a graph governor that adds no edge, then `patch`, each
  composed rule with the edges into it.
- `governFast`, the run path SC-1b calls (1.5.8): `governBody`, the same steps after the admission, reading the
  order, each reach and each rule unit's base name from tables computed once (`fastReads`, keyed by reach; `memo`
  reads a table and falls back to the definition).

Theorems (`VE/Scope/Theorems.lean`): `itemRule_decoder` (an item's rule is the chain's decoding of the joined
object), `govern_admits` (an answer means the block was admitted), `govern_identity` (no governor, no part: the
document exactly as written), `govern_orphan`, `governorsOf_iff` (a governor applies to a unit exactly when it is
unary and its regenerated reach holds the unit), `ordered_sorted` (order 1.4), `baseName_some`, and the helpers
`coversU_iff` and `mem_ordered`. From sc-1ad: `frontier_graph_refused`, `readings_refused` and `nonrule_refused`
(through `admit_governor`, what an admitted block says of each governor); `governFast_eq` (the run path answers as
`govern`, through `fastReads_eq`, `memo_map` and one `rfl` equation per step, `frameOnF_slow` to `governBody_slow`);
`ruleTable_decoder`, `edgesFor_ok`, `edgesOf_graph`, `edgesInto_mem`, `addOver_nil`. The theorems about what `govern`
writes (`govern_preserves`, `govern_provenance`, `govern_strings`, `govern_no_new_symbols`, `decodeNorm_name`) fail
as the spec states them on objects no JSON parser builds (F-raw below); they wait for the DRI's decision (sc-1ae).
From sc-3ab: `anchor_reach_iff` and `label_reach_iff` (spec 5.5: a heading's reach and a label's reach are the
layout's). `title_identity` fails as spec 5.5 states it on the same objects (F-raw-title below) and waits for the
same decision (sc-3ac).

## `VE/Scope/Wire.lean` and `VE/Service/ScopeAdmission.lean`: the document mode (SC-1b)

The Lean document mode (`VE.Service.Document.checkDoc`) admits `scope@0`, a wrapper at step 1b that AR-10's
profile table registers (`VE/Compose/Dispatch.lean`, `gate_scope`: the list's route without it, never an outside
route or discourse). For a document listing it the mode gates the profiles by the table, decodes the `scope` block
(`decodeScope`: the block's governors, list names and anchors, and the layout of exactly the document's units read
from its source bytes), runs `governFast`, answers the governed units on the environment without `scope@0`
(`checkCore`, the entry as it was), and folds each governor unit's status (`foldGovernors`). A governor unit
without content, meaning `specified`, that hosts a frame, reguard or carve-out takes `governorStatus`: the weakest
status of the units its governors cover, UNFORMALISED when one has none or there is none. The identities are the
document's as written, block and parts included.

Theorems (spec 5.2): `governor_status_weakest` (a folded status is the weakest of the covered units' and one of
them has it), `governor_status_none`, `decodeScope_layout` (the layout's ids are the document's unit ids, in order),
`scope_admission` (on a `scope@0` document the mode's answer is the fold of its answer on `govern`'s units; the call
is `governFast`, carried by `governFast_eq`) and `scope_absent_unchanged` (without `scope@0` the mode is `checkCore`).
`decodeScope_bound` and `decoded_no_new_symbols` wait for sc-1ae (`BlockBound`, `HasStr`). Fixtures:
`VE/Scope/WireExamples.lean` (every reach and effect, each wire fault, the layout, the status table) and
`VE/Service/ScopeExamples.lean` (F1-doc, F1-bad, F1-off, the row's refusals and the identities on a small part
document); `tests/test_scope_document.py` runs the pilot's F1 part document end to end.

## `VE/Scope/Examples.lean`: the fixtures

The spec's 7.1 layout fixtures, over the pilot's own bytes (shortened inside sentences only): L1 (the layout
of the hard constraints), L1-p (`paraCounts` against draft 1's per-unit count at every byte), F1 and F1‴ (the run of
"Claude should never:" is its seven bullets, and the sentence after it is not an item), F2 (mid-line continuations
belong to the run but are not items), F2′ (sub-bullets are depth 1), F2″ (`NotALeadIn`, including a unit without
":" that an item follows). The pilot excerpts are `#guard`s; the same contracts are kernel theorems (`decide`) on
short layouts (`short_layout`, `short_run`, `of_source`, `markers`, `bold_labels`, `byte_tests`, `para_counts`), so
each layout definition is stated about by a theorem.

The SC-3a fixtures (spec 7.5), the layout half: F8 (the UDHR's Article 29 under the root anchor: its reach is its
three paragraphs, its heading `u109`), F8-out (neither heading is in the reach), F8-tree (two articles under a missing
root are refused with discourse's text), F9′ (the pinned constitution's "Instructable behaviors": the run splits the
heading into its marker and its words, so the marker is the heading), F10 (a bold label reaches its item, the item's
continuing sentences and its sub-bullets, and stops at the next item of its depth). Kernel theorems: `short_items`,
`box_anchors` (containment at both boundaries, the innermost anchor, a tie, the reach and its refusals), `span_tests`,
`reaches_root`, and `anchor_checks` with `#guard`s, one per anchor diagnostic and the limit's boundary.

The effects fixtures (sc-1ab, spec 7.1 and 7.4's F7-t): F1-m (the frame joined to u0165.s01's part is the whole
rule, all six W1 keys), F1′ (`ScopeConflict: u0165.s03: sign`), parts that are not objects, `unordered_join` and
`mergeParts_text`, F-own (u0173.s01's condition: `own` found, gone after substitution, safe, within depth; an
own-free condition unchanged), `own` as an object value and as a key, the depth limit's boundary, `own_binder`,
`depth_bound`, `narrowings`, `effects_six` and the F7-t `Commutes` table.

The `govern` fixtures (sc-1ac, spec 7.1), on the hard-constraint layout with the norms chain's environment: F1-g
(the frame over the seven parts gives each rule in full), F1″ (`govern` succeeds and the chain's decoder refuses an
item without `predicate` with its own text), F-id, F-orph, F-meta, F-fg, F-mm,
F-2f, F-rs, F-nr, F-pend and F-go; each admission step's refusal and the limits' boundaries; the order of two
carve-outs of one class and of a `rules` reach; and the frontier refusal that stands until SC-5. sc-1ad adds the graph
step's fixtures (`precedes`, `yields`, `ScopeNoEffect`, a decoder's refusal, `addOver`), `governFast` against
`govern` on refusals and answers, one fixture per mutant sc-1ac's review found surviving, and F-raw: on an
unbalanced or unordered tree `setObjVal!` drops a member, exposes a hidden one or loses a unit's `id`, and the soft
chain's decoder reads a rule's `name` that lookup does not find. sc-3ab adds the `govern` halves of SC-3a's
fixtures: F8 and F9′ (a heading as a title: the document unchanged, by `govern` and the run path), F8-tree (refused
at step 7, before step 8), F10 (a label as a title), F-meta's two-root case (discourse's text); step 8's unit
checks; a narrowing and a `precedes` governor over an anchor; step 7's export check; and F-raw-title (with one title
governor `govern` writes the document back through `patch`, so on an unbalanced tree removing the title changes
the answer). Kernel theorems
on a three-unit document (`short_access`, `short_base`, `short_effects`, `short_govern`) state each definition's
values, and `reaches_seven`, `governor_fields` and `sdoc_fields` pin the data types.
