import VE.Acts.Read

/-! Fixtures of the act grammar (docs/spec/act-phrases.md 11.2, 11.2a, 11.2b; D-31 in 10).

This file holds the fixtures that need no rule table: the generic listing boundaries LG1 to LG8, the same limits on a
real parse (a small grammar whose phrases have 63, 64, 65, 255 and 256 derivations), the vocabulary check with one
fixture per D-31 text and every pair of them in D-31's order, the review's counterexamples FR1, FR2 and FR6, and FR7
(every vocabulary of 11.2, 11.2b and the ap-2 measurement passes). The rule table's fixtures (G5 to L0, the 11.2b raw
and meaning counts, N1 to N5) join them with the grammar.
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
#guard rawCap == 256 && stepBudget == 2100000 && maxReadings == 64     -- D2's values (docs/act-phrases/ap-2)
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

/-! Each terminal over a list with its word first and last of two, and each case fold with every letter a capital
(ap-2 reviews F13 and F14: a terminal that reads one end of its list, or folds the case of one end of a word). -/

#guard Term.accepts (.adv ["freely", "gladly"]) (.word "freely") &&
  Term.accepts (.adv ["freely", "gladly"]) (.word "gladly") && !Term.accepts (.adv ["freely", "gladly"]) (.word "fully")
#guard !Term.accepts (.fill ["and", "or"]) (.word "and") && !Term.accepts (.fill ["and", "or"]) (.word "or") &&
  Term.accepts (.fill ["and", "or"]) (.word "asylum")
#guard Term.accepts (.kw "seek") (.word "SEEK") && Term.accepts (.adv ["freely"]) (.word "FREELY") &&
  !Term.accepts (.fill ["and"]) (.word "AND")

/-! ### The vocabulary check (1.4): one fixture per D-31 text -/

def fr (h : String) (m s mods : List String) : Frame := ⟨wordsOf h, m, s, mods⟩
def errOf (V : Vocab) : String :=
  match checkVocab V with
  | .ok () => "ok"
  | .error e => e
def frames (fs : List Frame) : Vocab := ⟨fs, []⟩

/-- One vocabulary per D-31 row, in D-31's order, with the row's text: each fails its own row's condition and no
earlier one. Across rows the heads are distinct and none begins another, and the adverbs are distinct, so the union
of two rows' vocabularies fails no earlier condition than the two fail alone (31r and 31s, which look across frames
and adverbs, come last). -/
def d31 : List (String × Vocab × String) :=
  [("31a", frames (List.replicate 129 (fr "seek" [""] [] [])), "ResourceLimit: more than 128 frames"),
   ("31b", frames [fr "" [] [] []], "InvalidInput: a frame has an empty head"),
   ("31c", frames [⟨["Seek"], [], [], []⟩],
    "InvalidInput: frame 'Seek' has the head word 'Seek', which is not a lower-case word of letters"),
   ("31d", frames [fr "be held" [] [] []], "InvalidInput: frame 'be held' has the reserved head word 'be'"),
   ("31e", frames [fr "claim" [] [] [], fr "claim" [] [] []], "InvalidInput: frame 'claim' is declared twice"),
   ("31f", frames [fr "take" [] [] [], fr "take part" [] [] []],
    "InvalidInput: frame heads 'take' and 'take part' overlap: one begins the other"),
   ("31g", frames [fr "gather" ["in", "in"] [] []], "InvalidInput: frame 'gather' lists the marker 'in' twice"),
   ("31h", frames [fr "hold" [] [] ["at", "at"]], "InvalidInput: frame 'hold' lists the modifier marker 'at' twice"),
   ("31i", frames [fr "subjected" ["to"] ["by"] []],                                                         -- FR6
    "InvalidInput: frame 'subjected' splits 'by', which is not one of its markers"),
   ("31j", frames [fr "join" [] [] [""]], "InvalidInput: frame 'join' has an empty modifier marker"),
   ("31k", frames [fr "keep" ["in"] [] ["in"]],
    "InvalidInput: frame 'keep' lists 'in' both as a marker and as a modifier marker"),
   ("31l", frames [fr "stand" ["in front", "in  front"] [] []],                                              -- FR2
    "InvalidInput: frame 'stand' has the marker 'in  front', which is not words separated by single spaces"),
   ("31m", frames [fr "mark" ["In"] [] []],
    "InvalidInput: frame 'mark' has the marker word 'In', which is not a lower-case word of letters"),
   ("31n", frames [fr "name" ["or"] [] []], "InvalidInput: frame 'name' has the reserved marker word 'or'"),
   ("31o", frames [fr "open" ["in"] [] ["in front"]],
    "InvalidInput: frame 'open' has the markers 'in' and 'in front', and one begins the other"),
   ("31p", ⟨[], ["freely", "freely"]⟩, "InvalidInput: the adverb 'freely' is declared twice"),
   ("31q", ⟨[], ["and"]⟩, "InvalidInput: the adverb 'and' is not a lower-case word of letters, or is reserved"),
   ("31r", ⟨[fr "rest" [] [] ["gladly"]], ["gladly"]⟩,
    "InvalidInput: the adverb 'gladly' is also a marker or head word"),
   ("31s", frames [fr "sit" ["on"] [] [], fr "on hold" [] [] []],
    "InvalidInput: frame 'on hold' begins with the marker word 'on'")]

def union (V W : Vocab) : Vocab := ⟨V.frames ++ W.frames, V.adverbs ++ W.adverbs⟩
/-- D-31's order: for every two rows, the union of their vocabularies, either way round, raises the earlier row's
text. A permutation of the checks that is not the identity puts some pair of rows out of order. -/
def inOrder : List (String × Vocab × String) → Bool
  | [] => true
  | (_, V, e) :: rest => rest.all (fun (_, W, _) => errOf (union V W) == e && errOf (union W V) == e) && inOrder rest

#guard d31.map (·.1) == ["31a", "31b", "31c", "31d", "31e", "31f", "31g", "31h", "31i", "31j", "31k", "31l", "31m",
  "31n", "31o", "31p", "31q", "31r", "31s"]
#guard d31.all (fun (_, V, e) => errOf V == e)                                     -- each row's text
#guard inOrder d31                                                                 -- D-31's order, every pair

/-! The other cases of each condition: both sides of 31a's limit, each half of a condition that has two (`wordOk`,
31q, 31r; 31l's second half, `wordsOf m == []`, never decides, since a marker other than `""` without words fails its
first half), every reserved word in each position (1.2), and words and heads that are prefixes as strings only. -/

/-- `k` distinct heads of three lower-case letters. -/
def heads (k : Nat) : List Frame :=
  (List.range k).map (fun i => fr (String.mk ['w', Char.ofNat (97 + i / 26), Char.ofNat (97 + i % 26)]) [] [] [])
#guard errOf (frames (heads 128)) == "ok" && errOf (frames (heads 129)) == "ResourceLimit: more than 128 frames"
#guard errOf (frames [fr "se3k" [] [] []]) ==
  "InvalidInput: frame 'se3k' has the head word 'se3k', which is not a lower-case word of letters"          -- 31c
#guard errOf (frames [fr "seek" [] [] ["se3k"]]) ==
  "InvalidInput: frame 'seek' has the marker word 'se3k', which is not a lower-case word of letters"        -- 31m
#guard errOf (frames [fr "seek" [] [] ["-in"]]) ==
  "InvalidInput: frame 'seek' has the marker word '-in', which is not a lower-case word of letters"         -- 31m
#guard errOf ⟨[], ["Freely"]⟩ == "InvalidInput: the adverb 'Freely' is not a lower-case word of letters, or is reserved"
#guard errOf ⟨[], ["se3k"]⟩ == "InvalidInput: the adverb 'se3k' is not a lower-case word of letters, or is reserved"
#guard framesOk ⟨[fr "check-in" ["o'er"] [] []], ["half-heartedly"]⟩       -- inner `-` and `'` are word letters
#guard errOf (frames [fr "seek" ["", " "] [] []]) ==
  "InvalidInput: frame 'seek' has the marker ' ', which is not words separated by single spaces"            -- 31l, FR1
#guard errOf (frames [fr "seek" [] [] [" in"]]) ==
  "InvalidInput: frame 'seek' has the marker ' in', which is not words separated by single spaces"          -- 31l
#guard errOf ⟨[fr "rest" [] [] []], ["rest"]⟩ == "InvalidInput: the adverb 'rest' is also a marker or head word" -- 31r
#guard errOf ⟨[fr "rest" ["in"] [] []], ["in"]⟩ == "InvalidInput: the adverb 'in' is also a marker or head word"
#guard errOf (frames [fr "to go" [] [] []]) == "InvalidInput: frame 'to go' has the reserved head word 'to'" -- 31d

/-- The reserved words of 1.2, from the spec's lists: a head word may be none of `headReserved`, a marker word none of
`markerReserved` (*to* and *for* are markers), an adverb none of `headReserved`. -/
def headReserved : List String := ["and", "or", "nor", "to", "be"] ++ Lexical.clauseWords
def markerReserved : List String := ["and", "or", "nor", "be"] ++ Lexical.clauseWords

#guard headReserved.all fun w =>
  errOf (frames [fr ("seek " ++ w) [] [] []]) == s!"InvalidInput: frame 'seek {w}' has the reserved head word '{w}'"
#guard markerReserved.all fun w =>
  errOf (frames [fr "seek" ["in " ++ w] [] []]) == s!"InvalidInput: frame 'seek' has the reserved marker word '{w}'" &&
  errOf (frames [fr "seek" [] [] [w]]) == s!"InvalidInput: frame 'seek' has the reserved marker word '{w}'"
#guard headReserved.all fun w =>
  errOf ⟨[], [w]⟩ == s!"InvalidInput: the adverb '{w}' is not a lower-case word of letters, or is reserved"
#guard framesOk (frames [fr "seek" ["to"] [] ["for"]]) && framesOk (frames [fr "care for" [] [] []])
#guard framesOk (frames [fr "take" [] [] [], fr "taken" [] [] []])      -- 31f is about words, not letters
#guard framesOk (frames [fr "seek" ["in"] [] ["into"]])                   -- 31o likewise
#guard framesOk (frames [fr "sit" ["on"] [] [], fr "carry on" [] [] []])   -- 31s: only a head's first word
#guard errOf (frames [fr "must seek" [] [] []]) == "InvalidInput: frame 'must seek' has the reserved head word 'must'"
#guard errOf (frames [fr "seek" ["if"] [] []]) == "InvalidInput: frame 'seek' has the reserved marker word 'if'"
#guard errOf ⟨[], ["not"]⟩ == "InvalidInput: the adverb 'not' is not a lower-case word of letters, or is reserved"
#guard Lexical.clauseWords == ["true", "false", "is", "equals", "not", "if", "then", "every", "there", "exists",
  "believes", "must", "eventually", "no"]                                                                   -- 1.2
#guard framesOk (frames [fr "work" ["for"] [] []])        -- *for* is a join word of AP-1, an ordinary marker here
#guard !framesOk (frames [fr "seek" ["", " "] [] []])                                                       -- FR1
#guard !framesOk (frames [fr "stand" ["in front", "in  front"] [] []])                                      -- FR2
#guard framesOk (frames [fr "stand" ["in front"] [] []])

/-! Each condition over a list with its fault in a later element (a later head word, marker, marker word, frame or
adverb), and each condition on the marker list 1.4 names: argument markers, modifier markers, or both, `""` counted
where 1.4 counts it (ap-2 review F7). -/

#guard errOf (frames [fr "seek Asylum" [] [] []]) ==
  "InvalidInput: frame 'seek Asylum' has the head word 'Asylum', which is not a lower-case word of letters"  -- 31c
#guard framesOk (frames [fr "take part" [] [] [], fr "take care" [] [] []])          -- 31f: one first word only
#guard errOf (frames [fr "take part" [] [] [], fr "take part in" [] [] []]) ==
  "InvalidInput: frame heads 'take part' and 'take part in' overlap: one begins the other"                  -- 31f
#guard errOf (frames [fr "gather" ["in", "on", "in"] [] []]) ==
  "InvalidInput: frame 'gather' lists the marker 'in' twice"                                                -- 31g
#guard errOf (frames [fr "seek" ["", ""] [] []]) == "InvalidInput: frame 'seek' lists the marker '' twice"  -- 31g
#guard errOf (frames [fr "subjected" ["to"] ["to", "by"] []]) ==
  "InvalidInput: frame 'subjected' splits 'by', which is not one of its markers"                            -- 31i
#guard errOf (frames [fr "hold" ["to"] ["at"] ["at"]]) ==
  "InvalidInput: frame 'hold' splits 'at', which is not one of its markers"                       -- 31i: not a modifier
#guard framesOk (frames [fr "promote" ["", "among"] ["among"] []]) && framesOk (frames [fr "form" [""] [""] []])
#guard errOf (frames [fr "join" [] [] ["in", ""]]) == "InvalidInput: frame 'join' has an empty modifier marker" -- 31j
#guard errOf (frames [fr "keep" ["in"] [] ["at", "in"]]) ==
  "InvalidInput: frame 'keep' lists 'in' both as a marker and as a modifier marker"                         -- 31k
#guard errOf (frames [fr "keep" ["", "in"] [] ["in"]]) ==
  "InvalidInput: frame 'keep' lists 'in' both as a marker and as a modifier marker"                         -- 31k
#guard errOf (frames [fr "mark" ["in Front"] [] []]) ==
  "InvalidInput: frame 'mark' has the marker word 'Front', which is not a lower-case word of letters"       -- 31m
#guard errOf (frames [fr "mark" ["in", "On"] [] []]) ==
  "InvalidInput: frame 'mark' has the marker word 'On', which is not a lower-case word of letters"          -- 31m
#guard errOf (frames [fr "name" ["in", "or"] [] []]) == "InvalidInput: frame 'name' has the reserved marker word 'or'"
#guard [["in front", "in"], ["in", "in front"]].all fun ms =>                                     -- 31o, either order
  errOf (frames [fr "stand" ms [] []]) ==
    "InvalidInput: frame 'stand' has the markers 'in' and 'in front', and one begins the other"
#guard errOf (frames [fr "open" ["in front"] [] ["in"]]) ==
  "InvalidInput: frame 'open' has the markers 'in' and 'in front', and one begins the other"     -- 31o: a modifier first
#guard errOf (frames [fr "stand" ["in front", "in front of"] [] []]) ==
  "InvalidInput: frame 'stand' has the markers 'in front' and 'in front of', and one begins the other"      -- 31o
#guard framesOk (frames [fr "stand" ["in front", "in back"] [] []])                  -- 31o: one first word only
#guard errOf ⟨[fr "rest" [] [] []], ["gladly", "rest"]⟩ == "InvalidInput: the adverb 'rest' is also a marker or head word"
#guard errOf ⟨[fr "sit" [] [] [], fr "rest" [] [] []], ["rest"]⟩ ==
  "InvalidInput: the adverb 'rest' is also a marker or head word"                                           -- 31r
#guard errOf ⟨[fr "take part" [] [] []], ["part"]⟩ == "InvalidInput: the adverb 'part' is also a marker or head word"
#guard errOf ⟨[fr "rest" ["in", "on"] [] []], ["on"]⟩ == "InvalidInput: the adverb 'on' is also a marker or head word"
#guard errOf (frames [fr "sit" ["on", "at"] [] [], fr "at rest" [] [] []]) ==
  "InvalidInput: frame 'at rest' begins with the marker word 'at'"                                          -- 31s

/-! Each condition that reads the marker lists or the marker words of `ms f` with its fault in a later modifier
marker, and with its fault in a marker's later word (ap-2 review F10: `ms f` is `f.markers ++ f.mods`, and the marker
words are each marker's words). -/

#guard errOf (frames [fr "stand" [] [] ["at", "in  front"]]) ==
  "InvalidInput: frame 'stand' has the marker 'in  front', which is not words separated by single spaces"   -- 31l
#guard errOf (frames [fr "mark" [] [] ["at", "In"]]) ==
  "InvalidInput: frame 'mark' has the marker word 'In', which is not a lower-case word of letters"          -- 31m
#guard errOf (frames [fr "name" [] [] ["at", "or"]]) == "InvalidInput: frame 'name' has the reserved marker word 'or'"
#guard errOf (frames [fr "open" [] [] ["at", "in", "in front"]]) ==
  "InvalidInput: frame 'open' has the markers 'in' and 'in front', and one begins the other"                -- 31o
#guard errOf ⟨[fr "rest" [] [] ["at", "gladly"]], ["gladly"]⟩ ==
  "InvalidInput: the adverb 'gladly' is also a marker or head word"                                         -- 31r
#guard errOf (frames [fr "sit" [] [] ["at", "on"], fr "on hold" [] [] []]) ==
  "InvalidInput: frame 'on hold' begins with the marker word 'on'"                                          -- 31s
#guard errOf ⟨[fr "stand" ["in front"] [] []], ["front"]⟩ ==
  "InvalidInput: the adverb 'front' is also a marker or head word"                                          -- 31r
#guard errOf (frames [fr "stand" ["in front"] [] [], fr "front desk" [] [] []]) ==
  "InvalidInput: frame 'front desk' begins with the marker word 'front'"                                    -- 31s

/-! Each condition over a list with its fault at the other end: in the first element and not in the last (a first
head word, marker, marker word, frame or adverb), and 31s on a one-word head (ap-2 review F11). -/

#guard errOf (frames [fr "Seek asylum" [] [] []]) ==
  "InvalidInput: frame 'Seek asylum' has the head word 'Seek', which is not a lower-case word of letters"  -- 31c
#guard errOf (frames [fr "take part" [] [] [], fr "take" [] [] []]) ==
  "InvalidInput: frame heads 'take' and 'take part' overlap: one begins the other"            -- 31f: the longer first
#guard errOf (frames [fr "subjected" ["to"] ["by", "to"] []]) ==
  "InvalidInput: frame 'subjected' splits 'by', which is not one of its markers"                            -- 31i
#guard framesOk (frames [fr "subjected" ["to", "by"] ["to"] []])                    -- 31i: a split marker not last
#guard errOf (frames [fr "join" [] [] ["", "in"]]) == "InvalidInput: frame 'join' has an empty modifier marker" -- 31j
#guard errOf (frames [fr "keep" ["in"] [] ["in", "at"]]) ==
  "InvalidInput: frame 'keep' lists 'in' both as a marker and as a modifier marker"                         -- 31k
#guard errOf (frames [fr "keep" ["in", "at"] [] ["in"]]) ==
  "InvalidInput: frame 'keep' lists 'in' both as a marker and as a modifier marker"                         -- 31k
#guard errOf (frames [fr "stand" ["in  front", "at"] [] []]) ==
  "InvalidInput: frame 'stand' has the marker 'in  front', which is not words separated by single spaces"   -- 31l
#guard errOf (frames [fr "mark" ["In front", "at"] [] []]) ==
  "InvalidInput: frame 'mark' has the marker word 'In', which is not a lower-case word of letters"          -- 31m
#guard errOf (frames [fr "name" ["or else", "at"] [] []]) ==
  "InvalidInput: frame 'name' has the reserved marker word 'or'"                                            -- 31n
#guard errOf ⟨[fr "rest" [] [] []], ["rest", "gladly"]⟩ ==
  "InvalidInput: the adverb 'rest' is also a marker or head word"                                           -- 31r
#guard errOf ⟨[fr "rest" [] [] [], fr "sit" [] [] []], ["rest"]⟩ ==
  "InvalidInput: the adverb 'rest' is also a marker or head word"                                           -- 31r
#guard errOf ⟨[fr "take part" [] [] []], ["take"]⟩ == "InvalidInput: the adverb 'take' is also a marker or head word"
#guard errOf ⟨[fr "rest" ["in front", "on"] [] []], ["in"]⟩ ==
  "InvalidInput: the adverb 'in' is also a marker or head word"                                             -- 31r
#guard errOf (frames [fr "on hold" [] [] [], fr "sit" ["on"] [] []]) ==
  "InvalidInput: frame 'on hold' begins with the marker word 'on'"                                          -- 31s
#guard errOf (frames [fr "sit" ["on"] [] [], fr "on hold" [] [] [], fr "wait" ["at"] [] []]) ==
  "InvalidInput: frame 'on hold' begins with the marker word 'on'"                         -- 31s: a later marker word
#guard errOf (frames [fr "sit" ["on"] [] [], fr "on" [] [] []]) ==
  "InvalidInput: frame 'on' begins with the marker word 'on'"                                    -- 31s: one-word head

/-! `wordOk`'s case check with a capital past the first letter and with one only at the end (ap-2 review F14: a case
fold of the first letter only accepts `sEek`). -/

#guard errOf (frames [fr "sEek" [] [] []]) ==
  "InvalidInput: frame 'sEek' has the head word 'sEek', which is not a lower-case word of letters"          -- 31c
#guard errOf (frames [fr "seeK" [] [] []]) ==
  "InvalidInput: frame 'seeK' has the head word 'seeK', which is not a lower-case word of letters"          -- 31c
#guard errOf (frames [fr "mark" ["iN"] [] []]) ==
  "InvalidInput: frame 'mark' has the marker word 'iN', which is not a lower-case word of letters"          -- 31m
#guard errOf ⟨[], ["frEely"]⟩ == "InvalidInput: the adverb 'frEely' is not a lower-case word of letters, or is reserved"

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
