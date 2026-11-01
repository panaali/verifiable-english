import VE.EnglishGrammar.Norm.Value

/-! The en-s6 fixtures of docs/spec/english-lean-s6.md section 6, at the piece level (DRI decision
reviews/dri-decisions-20261101-en-s6.md item 1): the block faults of f13-f16 and f24, the statements of f7 and f8,
and the carve-outs of f10 and f11. Each piece is the value spec 2.5 gives its sentence; the reader that computes
them from the text is en-s6b, whose fixtures read the same texts. Each check has an accepting and a refusing side. -/

namespace VE.EnglishGrammar.Norm.Examples
open VE.EnglishGrammar VE.EnglishGrammar.Norm

/-- A W1 clause over "Every act", as a consequence row gives it (spec 2.5). -/
def cl (f : Force) (u : List EFormula := []) : Clause := ⟨.every "act", .modal f, .strict, "permitted", [], .top, u, []⟩

def hd (n : Nat) (refs : List Nat := []) : Piece := .header ⟨n, refs⟩

def may : Piece := .clause (cl .may)
def mustNot : Piece := .clause (cl .mustNot)

def faultOf (ps : List Piece) : Option BlockFault :=
  match assemble ps with
  | .ok _ => none
  | .error f => some f

def statements (ps : List Piece) : Option (List NormStatement) := (assemble ps).toOption

-- f13: `Rule 2. Every act may be done.` opens block 1 with the wrong number.
#guard faultOf [hd 2, may] == some (.expectedRule 0 1)
#guard statements [hd 1, may] == some [.rule ⟨1, []⟩ (cl .may)]
#guard faultOf [hd 1, may, hd 3, may] == some (.expectedRule 2 2)
-- f14: `Rule 1. Every act may be done.` `Rule 1 takes precedence over rule 3.`
#guard faultOf [hd 1, may, .precedence 1 3] == some (.unknownRule 3)
#guard statements [hd 1, may, .precedence 1 1] == some [.rule ⟨1, []⟩ (cl .may), .precedence 1 1]
-- f15: `Rule 1. Rule 2. Every act may be done.`
#guard faultOf [hd 1, hd 2, may] == some (.noConsequence 0)
#guard (statements [hd 1, may, hd 2, may]).map ruleCount == some 2
#guard faultOf [hd 1, may, hd 2] == some (.noConsequence 2)
-- f16: `Rule 1. Except when this holds in all cases.`
#guard faultOf [hd 1, .exceptWhen .top] == some (.strayCarveOut 1)
#guard statements [hd 1, may, .exceptWhen .top] == some [.rule ⟨1, []⟩ (cl .may [.top])]
-- f24: `Rule 9 takes precedence over rule 1.` with no block; a reference to 0 is out of range too (spec 2.3).
#guard faultOf [.precedence 9 1] == some (.unknownRule 9)
#guard faultOf [hd 1, may, .precedence 1 0] == some (.unknownRule 0)
#guard faultOf [hd 1 [0], may] == some (.unknownRule 0)
#guard faultOf [hd 1 [2], may] == some (.unknownRule 2)
#guard faultOf [hd 1, may, hd 2 [1], may] == none
-- a block's faults come before an unknown reference
#guard faultOf [hd 1, may, .precedence 1 5, hd 3, may] == some (.expectedRule 3 2)
-- a clause sentence outside a block, or a second one in a block
#guard faultOf [may] == some (.strayConsequence 0)
#guard faultOf [hd 1, may, mustNot] == some (.strayConsequence 2)
#guard faultOf [hd 1, may, .precedence 1 1, mustNot] == some (.strayConsequence 3)

-- f7: `Rule 1. Every act must not be done.` `Rule 2. Every act may be done.` `Rule 2 takes precedence over rule 1.`
#guard statements [hd 1, mustNot, hd 2, may, .precedence 2 1] ==
  some [.rule ⟨1, []⟩ (cl .mustNot), .rule ⟨2, []⟩ (cl .may), .precedence 2 1]
-- f8: `Rule 3 (exception to rules 1 and 2).` keeps its targets in text order.
#guard statements [hd 1, mustNot, hd 2, mustNot, hd 3 [1, 2], may] ==
  some [.rule ⟨1, []⟩ (cl .mustNot), .rule ⟨2, []⟩ (cl .mustNot), .rule ⟨3, [1, 2]⟩ (cl .may)]
#guard (statements [hd 1, mustNot, hd 2, mustNot, hd 3 [1, 2], may]).map (·.flatMap NormStatement.refs) ==
  some [1, 2]

-- f10, f11: an inline carve-out stays first, and except-when sentences append theirs in text order.
def a : EFormula := .pred "describes_mitigation_and_deviates" [.var 0]
def b : EFormula := .pred "noteworthy" [.var 0]
#guard statements [hd 1, .clause (cl .may [a]), .exceptWhen b] == some [.rule ⟨1, []⟩ (cl .may [a, b])]
#guard statements [hd 1, may, .exceptWhen a, .exceptWhen b] == some [.rule ⟨1, []⟩ (cl .may [a, b])]
#guard statements [hd 1, may, .exceptWhen a, .exceptWhen b] != some [.rule ⟨1, []⟩ (cl .may [b, a])]
#guard faultOf [hd 1, may, .precedence 1 1, .exceptWhen a] == some (.strayCarveOut 3)

-- W1's stored signs (`norm_english.py:97-100`), and a plain wording's own sign (R2).
#guard [Force.must, .needNot, .may, .mustNot].map (Polarity.sign ∘ .modal) == [true, false, true, false]
#guard [true, false].map (Polarity.sign ∘ .plain) == [true, false]
-- The values later layers produce (EN-4, EN-5, EN-7) are distinct; authoring produces none of them.
#guard [Bearer.every "act", .named "the company", .author, .unstated].eraseDups.length == 4
#guard [Place.act, .guard, .carveOut, .bearer].eraseDups.length == 4
#guard Mode.default "decider" != .strict
#guard cl .may != { cl .may with residuals := [⟨0, 4, "word|frame|profile", "EN-7", .act⟩] }
#guard NState.init.scope == none
-- A translation-mode statement has its clauses, no number and no reference.
#guard (NormStatement.source [cl .may, cl .mustNot]).clauses == [cl .may, cl .mustNot]
#guard (NormStatement.source [cl .may]).refs == [] && (NormStatement.source [cl .may]).number? == none
#guard ruleCount [.source [cl .may], .rule ⟨1, []⟩ (cl .may), .precedence 1 1] == 1
#guard (statements [hd 1, may, .precedence 1 1]).map (·.flatMap NormStatement.clauses) == some [cl .may]

/-- A long well-formed block: a header, its clause and `k` except-when sentences. `assemble` reads each piece
once, by structural recursion on the list. -/
def long (k : Nat) : List Piece := hd 1 :: may :: List.replicate k (.exceptWhen a)

#guard (statements (long 5000)).map (·.flatMap (·.clauses.map (·.carveOuts.length))) == some [5000]
#guard faultOf (long 5000 ++ [hd 2]) == some (.noConsequence 5002)

end VE.EnglishGrammar.Norm.Examples
