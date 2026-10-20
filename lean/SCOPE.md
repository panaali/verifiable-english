# Cross-sentence scope (`scope@0`) in Lean

`scope@0` lets one unit change other units. The first case is a list: a lead-in such as "Claude should never:"
completes each item of the list after it. The design is [docs/spec/scope-PLAN.md](../docs/spec/scope-PLAN.md); the
exact definitions and statements are [docs/spec/scope.md](../docs/spec/scope.md) (sections 1.2-1.5, 4 and 5.1).

This file covers what is built so far: item sc-1a, the layout's list runs, that is, which units a lead-in governs;
item sc-3a, the layout's label reaches and anchors, with discourse's anchor containment and anchor checks moved
into the layout so that one body serves both; and item sc-1ab, the effects on a rule's JSON object (joining the
lead-in's part to each item's part, conditions and `own`, the order table). No route or service mode calls the scope
parts yet. `govern`, the block's admission and the run path `governFast` come next (sc-1ac), and the document mode
after that (SC-1b).

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
