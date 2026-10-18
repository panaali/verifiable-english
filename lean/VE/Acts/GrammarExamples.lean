import VE.Acts.Read

/-! Fixtures of the act grammar (docs/spec/act-phrases.md 11.2, 11.2a, 11.2b; D-31 in 10).

This file holds the fixtures that need no rule table: the generic listing boundaries LG1 to LG8, the same limits on a
real parse (a small grammar whose phrases have 63, 64, 65, 255 and 256 derivations), the vocabulary check with one
fixture per D-31 text, the review's counterexamples FR1, FR2 and FR6, and FR7 (every vocabulary of 11.2, 11.2b and
the ap-2 measurement passes). The rule table's fixtures (G5 to L0, the 11.2b raw and meaning counts, N1 to N5) join
them with the grammar.
-/

namespace VE.Acts.Examples
open VE.Acts
open VE.Acts.Lexical (Tok)
open VE.Grammar (Tree Grammar)

/-! ### LG1 to LG8: the generic listing (synthetic trees `t k`, meaning `some k` or all `some 0`) -/

def t (k : Nat) : Tree Tok := .node k []
def trees (n : Nat) : List (Tree Tok) := (List.range n).map t
def own : Tree Tok → Option Nat
  | .node k _ => some k
  | .leaf _ => none
def zero : Tree Tok → Option Nat := fun _ => some 0

#guard listing 10 64 (some (trees 9)) own == .ok (List.range 9)      -- LG1: N−1 raw
#guard listing 10 64 (some (trees 10)) own == .limit                 -- LG2: N raw, saturated
#guard listing 256 64 (some (trees 63)) own == .ok (List.range 63)   -- LG3
#guard listing 256 64 (some (trees 64)) own == .ok (List.range 64)   -- LG4: exactly 64 are listed
#guard listing 256 64 (some (trees 65)) own == .limit                -- LG5: 65 > 64
#guard listing 10 64 (some (trees 10)) zero == .limit                -- LG6: one meaning may hide another
#guard listing 10 64 (some (trees 9)) zero == .ok [0]                -- LG7
#guard listing 10 64 none own == .limit                              -- LG8: budget exhausted
#guard firsts [2, 1, 2, 3, 1] == [2, 1, 3]

/-! ### The limits on a real parse

`L → X | X L`, and `X` reads the word `w` by `k` rules for each `(w, k)` of `alts`: a phrase of words `w₁ … wₙ` has
the product of their `k` as its derivations. `μd` gives each derivation its own meaning (the rules it used), `μ1`
gives every derivation one meaning, and `μlast` gives the derivation through the last `g` rule another one. -/

def alts : List (String × Nat) := [("b", 2), ("c", 3), ("d", 5), ("e", 7), ("f", 13), ("g", 17)]
def toy : Grammar Term :=
  { rules := #[⟨1, [.n 0], 0, ""⟩, ⟨1, [.n 0, .n 1], 0, ""⟩] ++
      (alts.flatMap (fun (w, k) => List.replicate k (⟨0, [.t (.kw w)], 0, ""⟩ : VE.Grammar.Rule Term))).toArray,
    start := 1, rank := #[0, 1] }
def phrase (ws : List String) : Array Tok := (ws.map Tok.word).toArray
def rulesOf : Tree Tok → List Nat
  | .node r ks => r :: ks.flatMap rulesOf
  | .leaf _ => []
def μd : VE.Grammar.Meaning Tok Unit String (List Nat) := fun _ d => .ok (rulesOf d, false, ())
def μ1 : VE.Grammar.Meaning Tok Unit String String := fun _ _ => .ok ("a", false, ())
def μlast : VE.Grammar.Meaning Tok Unit String String :=
  fun _ d => .ok (if (rulesOf d).contains (toy.rules.size - 1) then "b" else "a", false, ())
def raw (ws : List String) : Option Nat := (VE.Grammar.parse toy rawCap stepBudget (phrase ws)).map (·.length)
def count : Listing (List Nat) → Option Nat
  | .ok xs => some xs.length
  | .limit => none

#guard toy.wf
#guard raw ["e", "c", "c"] == some 63 && raw ["b", "b", "b", "b", "b", "b"] == some 64 && raw ["d", "f"] == some 65
#guard raw ["c", "d", "g"] == some 255 && raw ["b", "b", "b", "b", "b", "b", "b", "b"] == some 256
#guard count (readingsIn toy μd rawCap stepBudget (phrase ["e", "c", "c"])) == some 63            -- 63 readings
#guard count (readingsIn toy μd rawCap stepBudget (phrase ["b", "b", "b", "b", "b", "b"])) == some 64  -- 64
#guard readingsIn toy μd rawCap stepBudget (phrase ["d", "f"]) == .limit                          -- 65: limit
#guard readIn toy μ1 rawCap stepBudget (phrase ["c", "d", "g"]) == .ok "a"                        -- N−1 raw
#guard readIn toy μ1 rawCap stepBudget (phrase ["b", "b", "b", "b", "b", "b", "b", "b"]) == .limit -- N raw
#guard readIn toy μ1 rawCap 0 (phrase ["b"]) == .limit                                            -- no steps
#guard readIn toy μ1 0 stepBudget (phrase ["b"]) == .limit                                        -- N = 0
#guard readIn toy μlast rawCap stepBudget (phrase ["g"]) == .many "a" "b"                        -- hidden "b"
#guard readIn toy μ1 rawCap stepBudget (phrase ["a"]) == .none

/-! ### Terminals (5.1) -/

#guard Term.accepts .subj (.slot 0) && !Term.accepts .subj (.slot 1) && Term.accepts .slot (.slot 1) &&
  !Term.accepts .slot (.slot 0) && Term.accepts .fixed (.fixed 3) && Term.accepts .comma .comma &&
  Term.accepts (.kw "seek") (.word "Seek") && !Term.accepts (.kw "seek") (.word "seeks") &&
  Term.accepts (.adv ["freely"]) (.word "Freely") && !Term.accepts (.adv ["freely"]) (.word "fully") &&
  Term.accepts (.fill ["and"]) (.word "asylum") && !Term.accepts (.fill ["and"]) (.word "And") &&
  !Term.accepts .never (.word "seek") && !Term.accepts .never .comma && !Term.accepts (.fill []) .comma

/-! ### The vocabulary check (1.4): one fixture per D-31 text -/

def fr (h : String) (m s mods : List String) : Frame := ⟨wordsOf h, m, s, mods⟩
def errOf (V : Vocab) : String :=
  match checkVocab V with
  | .ok () => "ok"
  | .error e => e
def frames (fs : List Frame) : Vocab := ⟨fs, []⟩

#guard errOf (frames (List.replicate 129 (fr "seek" [""] [] []))) == "ResourceLimit: more than 128 frames"   -- 31a
#guard errOf (frames [fr "" [] [] []]) == "InvalidInput: a frame has an empty head"                          -- 31b
#guard errOf (frames [⟨["Seek"], [], [], []⟩]) ==
  "InvalidInput: frame 'Seek' has the head word 'Seek', which is not a lower-case word of letters"           -- 31c
#guard errOf (frames [fr "be held" [] [] []]) == "InvalidInput: frame 'be held' has the reserved head word 'be'" -- 31d
#guard errOf (frames [fr "seek" [] [] [], fr "seek" [] [] []]) == "InvalidInput: frame 'seek' is declared twice" -- 31e
#guard errOf (frames [fr "take" [] [] [], fr "take part" [] [] []]) ==
  "InvalidInput: frame heads 'take' and 'take part' overlap: one begins the other"                          -- 31f
#guard errOf (frames [fr "seek" ["in", "in"] [] []]) == "InvalidInput: frame 'seek' lists the marker 'in' twice" -- 31g
#guard errOf (frames [fr "seek" [] [] ["in", "in"]]) ==
  "InvalidInput: frame 'seek' lists the modifier marker 'in' twice"                                         -- 31h
#guard errOf (frames [fr "subjected" ["to"] ["by"] []]) ==
  "InvalidInput: frame 'subjected' splits 'by', which is not one of its markers"                            -- 31i, FR6
#guard errOf (frames [fr "seek" [] [] [""]]) == "InvalidInput: frame 'seek' has an empty modifier marker"     -- 31j
#guard errOf (frames [fr "seek" ["in"] [] ["in"]]) ==
  "InvalidInput: frame 'seek' lists 'in' both as a marker and as a modifier marker"                         -- 31k
#guard errOf (frames [fr "seek" ["", " "] [] []]) ==
  "InvalidInput: frame 'seek' has the marker ' ', which is not words separated by single spaces"            -- 31l, FR1
#guard errOf (frames [fr "stand" ["in front", "in  front"] [] []]) ==
  "InvalidInput: frame 'stand' has the marker 'in  front', which is not words separated by single spaces"   -- 31l, FR2
#guard errOf (frames [fr "seek" [] [] [" in"]]) ==
  "InvalidInput: frame 'seek' has the marker ' in', which is not words separated by single spaces"          -- 31l
#guard errOf (frames [fr "seek" ["In"] [] []]) ==
  "InvalidInput: frame 'seek' has the marker word 'In', which is not a lower-case word of letters"          -- 31m
#guard errOf (frames [fr "seek" ["or"] [] []]) == "InvalidInput: frame 'seek' has the reserved marker word 'or'" -- 31n
#guard errOf (frames [fr "seek" ["in"] [] ["in front"]]) ==
  "InvalidInput: frame 'seek' has the markers 'in' and 'in front', and one begins the other"                -- 31o
#guard errOf ⟨[], ["freely", "freely"]⟩ == "InvalidInput: the adverb 'freely' is declared twice"             -- 31p
#guard errOf ⟨[], ["and"]⟩ == "InvalidInput: the adverb 'and' is not a lower-case word of letters, or is reserved" -- 31q
#guard errOf ⟨[fr "seek" [] [] ["freely"]], ["freely"]⟩ ==
  "InvalidInput: the adverb 'freely' is also a marker or head word"                                         -- 31r
#guard errOf (frames [fr "seek" ["in"] [] [], fr "in vain" [] [] []]) ==
  "InvalidInput: frame 'in vain' begins with the marker word 'in'"                                          -- 31s
#guard errOf (frames [fr "must seek" [] [] []]) == "InvalidInput: frame 'must seek' has the reserved head word 'must'"
#guard errOf (frames [fr "seek" ["if"] [] []]) == "InvalidInput: frame 'seek' has the reserved marker word 'if'"
#guard errOf ⟨[], ["not"]⟩ == "InvalidInput: the adverb 'not' is not a lower-case word of letters, or is reserved"
#guard Lexical.clauseWords == ["true", "false", "is", "equals", "not", "if", "then", "every", "there", "exists",
  "believes", "must", "eventually", "no"]                                                                   -- 1.2
#guard framesOk (frames [fr "work" ["for"] [] []])        -- *for* is a join word of AP-1, an ordinary marker here
#guard !framesOk (frames [fr "seek" ["", " "] [] []])                                                       -- FR1
#guard !framesOk (frames [fr "stand" ["in front", "in  front"] [] []])                                      -- FR2
#guard framesOk (frames [fr "stand" ["in front"] [] []])

/-! ### FR7: the vocabularies of 11.2, the 13 `ap0` rows of 11.2b and the ap-2 measurement's generated frames -/

def V5 : Vocab := frames [fr "seek" [""] [] ["in"], fr "enjoy" [""] [] ["in"]]
def V6 : Vocab := frames [fr "subjected" ["to"] ["to"] []]
def V7 : Vocab := frames [fr "held" ["by"] [] []]
def V8 : Vocab := ⟨[fr "participate" ["in"] [] [], fr "enjoy" [""] [] [], fr "share" ["in"] [] []], ["freely"]⟩
def V9 : Vocab := ⟨[fr "deprived" ["of"] [] [], fr "denied" [""] [] []], ["arbitrarily"]⟩
def V10 : Vocab := frames [fr "security" ["in the event of"] ["in the event of"] ["in circumstances"]]
def V11 : Vocab := ⟨[fr "take part" ["in"] [] ["through"]], ["directly"]⟩
def V12 : Vocab := frames [fr "form" [""] [] ["for"], fr "join" [""] [] ["for"]]
def V14 : Vocab := frames ((["abandon", "claim", "use", "provide", "endanger"].map (fr · [""] [] [])) ++
  [fr "act" ["against"] [] []])
def ap0 : List Vocab :=
  [frames [fr "held" ["in"] [] []], frames [fr "subjected" ["to"] [] []], frames [fr "subjected" ["to"] ["to"] []],
   frames [fr "marry" [] [] [], fr "found" [""] [] []], frames [fr "change" [""] [] []],
   ⟨[fr "manifest" [""] [] ["in"]], ["alone"]⟩,
   frames (["seek", "receive", "impart"].map (fr · [""] [] ["through", "regardless of"])),
   frames [fr "promote" ["", "among"] [] []], frames [fr "give" [""] [] []],
   ⟨[fr "deceive" ["", "about"] [] []], ["actively"]⟩, frames [fr "engage" ["in"] [] [], fr "assist" ["in"] [] []],
   frames [fr "engage" ["", "with"] [] [], fr "assist" ["", "with"] [] []]]
def measured : List Vocab :=
  [frames [fr "presumed innocent" [] [] ["until", "according", "to", "in"]],
   frames [fr "realization" [] [] ["through", "in", "with", "of", "for"]], frames [fr "just" [] [] ["for", "of", "by"]],
   frames [fr "a standard" [] [] ["of", "for", "including"]], frames [fr "the protection" [] [] ["of", "from"]],
   frames [fr "a social" [] [] ["in"]]]

#guard [V5, V6, V7, V8, V9, V10, V11, V12, V14].all framesOk && ap0.all framesOk && measured.all framesOk

end VE.Acts.Examples
