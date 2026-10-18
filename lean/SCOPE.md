# Cross-sentence scope (`scope@0`) in Lean

`scope@0` lets one unit change other units. The first case is a list: a lead-in such as "Claude should never:"
completes each item of the list after it. The design is [docs/spec/scope-PLAN.md](../docs/spec/scope-PLAN.md); the
exact definitions and statements are [docs/spec/scope.md](../docs/spec/scope.md) (sections 1.2, 4.1 and 5.1).

This file covers what is built so far, item sc-1a: the layout's list runs, that is, which units a lead-in governs.
No route or service mode calls them yet. The effects on a rule's JSON object (joining the lead-in's part to each
item's part, conditions and `own`, the order table) come next (sc-1ab), then `govern`, the block's admission and
the run path `governFast` (sc-1ac), and the document mode after that (SC-1b).

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

## `VE/Scope/Examples.lean`: the fixtures

The spec's 7.1 layout fixtures, over the pilot's own bytes (shortened inside sentences only): L1 (the layout
of the hard constraints), L1-p (`paraCounts` against draft 1's per-unit count at every byte), F1 and F1‴ (the run of
"Claude should never:" is its seven bullets, and the sentence after it is not an item), F2 (mid-line continuations
belong to the run but are not items), F2′ (sub-bullets are depth 1), F2″ (`NotALeadIn`, including a unit without
":" that an item follows). The pilot excerpts are `#guard`s; the same contracts are kernel theorems (`decide`) on
short layouts (`short_layout`, `short_run`, `of_source`, `markers`, `bold_labels`, `byte_tests`, `para_counts`), so
each layout definition is stated about by a theorem.
