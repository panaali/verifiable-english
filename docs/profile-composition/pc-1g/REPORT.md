# pc-1g report: G3 for `judgments@0` in the document mode, and the rights@0 reader

Status: STOPPED on statements (task: "If one must change, stop on it only, build the rest and ask the DRI decider
through msg.sh"). Question sent to the DRI decider on 2026-11-03 (msg.sh dri pc-1g). The work the question does not
block continues below.

Plan: docs/spec/profile-composition-PLAN.md "PC-1" and spec 1.7 at 3dfadd302 (main's copies are byte-identical:
`git -C ../verifiable-english show 3dfadd302:<file> | diff -q - <file>` prints nothing). This item proves edit 2 of
debates/plan-synthesis-2/edits-profile-composition.md, the G3 amendment (the exchange applies only when it is one to
one, decided in Lean first), as far as the stop below allows.

## The stop: three of the approved statements cannot be proved as written

1. **The round-trip lemma (deliverable 2) is not provable without an axiom in this toolchain.** `withoutJudgments`
   writes the twin's front matter with `Lean.Json.compress`, and the twin's check reads it back with
   `Lean.Json.parse` (`frontJson`, Document.lean:330). In Lean v4.24.0 both are `partial def`s
   (`Lean/Data/Json/Printer.lean:164` `compress`; `Lean/Data/Json/Parser.lean:75,94,204-233` `strCore`, `natCore`,
   `arrayCore`, `objectCore`, `anyCore`). The kernel cannot unfold a `partial def`, so no fact about its value can
   be proved. Even `Json.parse "1" = .ok 1` and `Json.compress (.num 1) = "1"` fail by `rfl`, and
   `decide` has no instance. The DRI's condition (20261031 item 2: "a theorem, not an axiom") therefore cannot be
   met for any front matter. Every theorem that reads `checkDocSets (withoutJudgments j)` or
   `swapInjective (withoutJudgments j)` rests on it: `swapInjective_twin`, `withoutJudgments_ids`,
   `checkDocSets_swapClash` (its first two conjuncts), `checkDocSets_judgments_transparent`, and
   `checkDocSets_withoutStatuses` (`withoutStatuses` writes the front matter again too).
2. **`swap_correct` is false.** A key stated in two reading sets for two contents has two pairs, and `exchange` is
   a function of the value alone, so it reads the first. Take set 1 stating model A under `K`, and set 2 stating
   model B under `K = v₁(B)`. `swapInjective j` holds: the values are `[K, K]`, and every pair's value is `K`.
   `(K, v₁(B), v₂(B)) ∈ statedPairs j`, and `K ∈ statedIds j`. But `exchange j K = swap v₁(A) v₂(A) K = K`, so
   `(exchange j K == v₂(B)) = false`, while `(K == v₁(B)) = true`. No digest collision is needed. The witness is a
   `#guard` in lean/VE/Judgments/ChainExamples.lean (`twoSets`). `withoutJudgments_ids` fails on the same case, at
   the model site (s2, K).
3. **`verdictFields` as specified makes G3 false** (pc-1 DELTA row 10, recorded there and left open). A judged
   answer carries jt-3a's `undeclared_evaluative`, and its twin has no such member. Spec 2e says "No other field is
   dropped".

Also on size: G3 relates two runs of the whole document chain, `check` and everything it calls (Document.lean is
2,695 lines, plus the soft, readings, discourse and rights decoders). Even with 1 to 3 settled, its proof is a
multi-thousand-line relational proof. It does not fit the 600-line size line or R16's 150 trusted lines.
