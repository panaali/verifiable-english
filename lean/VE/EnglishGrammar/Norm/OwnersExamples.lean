import VE.EnglishGrammar.Norm.Owners
import VE.EnglishGrammar.LexiconFixtures
import VE.EnglishGrammar.ReadExamples

/-! EN-2 step 0's fixtures O1-O8 (docs/spec/en-e3-norm.md section 8): each owner piece, both directions of each
"exactly when", over `LexiconFixtures.envF` with its valid lexicon v1 (`LF`). -/

namespace VE.EnglishGrammar.Norm.OwnersExamples
open VE.EnglishGrammar VE.EnglishGrammar.Norm VE.EnglishGrammar.LexiconFixtures

instance {ε α : Type} [BEq ε] [BEq α] : BEq (Except ε α) where
  beq
    | .ok a, .ok b => a == b
    | .error e, .error f => e == f
    | _, _ => false

-- O1: `opOf_agrees` on every fitting (role, polarity) pair: the reader's sign is the owner's op.
def reg (role : VE.Norms.Role) : VE.Norms.Regulated := ⟨"p", ["act"], true, role, none, none⟩
def fitting : List (VE.Norms.Role × Polarity) :=
  [(.obligation, .modal .must), (.obligation, .modal .needNot), (.permission, .modal .may),
   (.permission, .modal .mustNot), (.plain, .plain true), (.plain, .plain false)]
#guard fitting.all fun (r, p) => p.fits r && VE.Acts.opOf (reg r) p.sign == p.op?
#guard (fitting.map fun (_, p) => p.op?) == [some .must, some .needNot, some .may, some .mustNot, some .right, none]
-- O2: outside the premise the two differ, so the premise is needed (the reader never produces these pairs).
#guard !(Polarity.modal .must).fits .permission &&
  VE.Acts.opOf (reg .permission) (Polarity.modal .must).sign != (Polarity.modal .must).op?
#guard !(Polarity.modal .needNot).fits .permission &&
  VE.Acts.opOf (reg .permission) (Polarity.modal .needNot).sign != (Polarity.modal .needNot).op?

-- O3: soft-norms' mode, both directions of `soft_strict_iff`.
#guard (Mode.strict).soft == .strict
#guard (Mode.default "company").soft == .default && (Mode.default "company").soft != .strict

-- O4/O5: the source view, V1-V5 with the use case's source spellings (`envF` and its valid lexicon v1).
def LF : Lexicon := ReadExamples.LF
def viewFailures (A : List (String × String × Bool)) : List String :=
  let (E, L) := sourceView envF LF A
  failureSet E L
#guard viewFailures [] == []
#guard viewFailures [("deployed", "{0} is rolled out", false)] == []
#guard viewFailures [("deployed", "{0} is reviewed", false)] == ["V4 predicate deployed", "V4 predicate reviewed"]
-- the source spellings follow the aliases the environment and the lexicon already have, in both
#guard let a := [("owns", "{0} holds {1}", false), ("reviewed", "{0} is checked", false)]
  let b := [("deployed", "{0} is rolled out", false)]
  let (E, L) := sourceView { envF with forms := { envF.forms with aliases := a } } { LF with aliases := a } b
  E.forms.aliases == a ++ b && L.aliases == a ++ b && E.forms.wordings == envF.forms.wordings && L.nouns == LF.nouns
-- a spelling selected in the lexicon only, not fixed in the environment's forms, is refused (V2)
#guard failureSet envF { LF with aliases := [("deployed", "{0} is rolled out", false)] } == ["V2 alias deployed"]

-- O6/O7: the span gate, both directions of `toNodeChecked_ok` and `toNodesChecked_ok`.
def cPub : Clause := ⟨.every "situation", .plain true, .strict, "in_scope", [], .pred "publicly_deployed" [.var 0], [], []⟩
def cSpan : Clause := { cPub with residuals := [⟨30, 46, "every|norm.modifier|norms@0", "ET-T1", .act⟩] }
def nPub : VE.Norms.Node := ⟨"rule-1", "in_scope", true, .unary "publicly_deployed" (.var 0), [], []⟩
#guard cPub.toNode "rule-1" [] == .ok nPub
#guard cPub.toNodeChecked "rule-1" [] == .ok nPub
#guard cSpan.toNode "rule-1" [] == .ok nPub
#guard cSpan.toNodeChecked "rule-1" [] == .error (unformalisedText 1)
#guard toNodesChecked [.rule ⟨1, []⟩ cPub, .precedence 1 1] == .ok [{ nPub with over := ["rule-1"] }]
#guard toNodesChecked [.rule ⟨1, []⟩ cSpan] == .error (unformalisedText 1)
#guard spansOf [.rule ⟨1, []⟩ cSpan, .precedence 1 1] == [⟨30, 46, "every|norm.modifier|norms@0", "ET-T1", .act⟩]
-- every span of every clause, in text order
#guard spansOf [.rule ⟨1, []⟩ cSpan, .rule ⟨2, []⟩ { cSpan with residuals := [⟨50, 55, "r", "o", .guard⟩] }] ==
  [⟨30, 46, "every|norm.modifier|norms@0", "ET-T1", .act⟩, ⟨50, 55, "r", "o", .guard⟩] &&
  toNodesChecked [.rule ⟨1, []⟩ cPub, .rule ⟨2, []⟩ cSpan] == .error (unformalisedText 1)
#guard unformalisedText 1 == "The text has 1 phrase(s) that the reader parsed and did not formalise. No rule is made " ++
  "from a sentence with such a phrase."

-- O8: the decoder refuses two forms `EFormula.encode` writes (M2; OPEN-1 is closed: `NodeRefused` stands) and
-- answers its two resource limits; the gate passes a clause without spans to the decoder unchanged.
def deep : Nat → EFormula
  | 0 => .pred "publicly_deployed" [.var 0]
  | n + 1 => .not (deep n)
def cAtom : Clause := { cPub with guard := .pred "r" [.var 0, .var 1, .var 2] }
def cBad : Clause := { cPub with guard := deep 300 }
def cWide : Clause := { cPub with carveOuts := List.replicate 5000 (.pred "deviates" [.var 0]) }
#guard VE.Limits.maxDepth == 64 && VE.Limits.maxNodes == 10000
#guard cAtom.toNode "rule-1" [] == .error "invalid indexed formula"
#guard ({ cPub with guard := .lt (.num 1) (.var 0) } : Clause).toNode "rule-1" [] == .error "invalid indexed formula"
#guard cBad.toNode "rule-1" [] == .error "ResourceLimit: formula depth exceeds 64"
#guard cBad.toNodeChecked "rule-1" [] == .error "ResourceLimit: formula depth exceeds 64"
#guard cWide.toNode "rule-1" [] == .error "ResourceLimit: AST exceeds depth or node budget"

end VE.EnglishGrammar.Norm.OwnersExamples
