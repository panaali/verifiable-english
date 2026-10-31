# ap-2bb: `read_normal` is false with spec 5.5's `normalOk` (statement gate)

`read_normal` (spec 5.6, reviewed text, unchanged):

```lean
theorem read_normal (V : Vocab) (h : framesOk V = true) (a : Atom) (ha : normalOk V a = true) :
    ∃ N0 b0, ∀ N b, N0 ≤ N → b0 ≤ b → read V N b a.normal.toArray = .ok (.one a.canon)
```

`normalOk V a` is written as spec 5.5 gives it: `atomOk V a`, every words part is non-empty and made of the frame's
filler words, no part is `{0}`, no argument marker occurs twice, and no joined filler sits under a split marker or as
a split object. Each atom below satisfies all of these, with `framesOk V = true`, and `read` was evaluated on main
`432763b06` with `N = rawCap` and `b = stepBudget`. Since `read` is `.none` or a different `.ok` there, it is not
`.ok (.one a.canon)` for large `N` and `b` either. The fixtures are `#guard`s in `lean/VE/Acts/RenderExamples.lean`.

| # | Atom (vocabulary) | Normal form | `read` | Why |
|---|---|---|---|---|
| C1 | G7's `held`: `by` the joined filler `[secret vote, fixed 0]` (V7, spec 11.2's own render fixture) | `{0} be held by secret vote or equivalent free voting procedures` | `none` | D9 (i), decided after draft 2's `normalOk`: a joined filler whose marker is written once and whose first or last part is two or more words has no meaning |
| C2 | `form` with the joined object `[trade unions, {1}]` (`form: [""]`) | `{0} form trade unions and {1}` | `none` | D9 (i) at `Oh`'s `PLh` |
| C3 | `held` with `by` the joined filler `[{1}]` (one part) | `{0} be held by {1}` | `ok (one held-by-.one {1})` | `listToks` writes a one-part list as the part, which reads back as `.one` |
| C4 | `held` with `by` the joined filler `[]` | `{0} be held by` | `none` | an empty list writes nothing after the marker |

Proposed resolution, in the way SR1 handled draft 1: keep the statement and strengthen only the definition of its
hypothesis. `normalOk` would add two conditions. (a) Every joined filler has at least two parts. (b) D9 (i): no
joined filler (an argument's, written once, or the object's) has a first or last part that is two or more words.
Spec 11.2's G7 render fixture would then read `normalOk` false, because by D9 (i) G7's own atom has no normal form
that reads back. G7 written with the marker repeated still reads `ok g7`. Otherwise C1's fixture would need G7's atom
with a fixed phrase for "secret vote".

Separately: with that `normalOk`, the general proof of `read_normal` needs an unambiguity argument over the whole
rule table (ap-2's REPORT: "the hardest proof of AP-2"). It does not fit the ~600-line size line beside the rest of
this item, so ap-2bb names it as ap-2bc.
