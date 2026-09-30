import VE.Definitions.Bundle
import VE.English.Statements

/-! # `ve.discourse@1`: the manifest as data (docs/spec/discourse.md 1.2 to 1.6, 9.1)

A `ve-document@2` document is W2's decoded document (`VE.Route.Admission.Doc`,
unchanged), a discourse manifest and the tokenised text of each unit. The manifest
records anchors, registered names and content names, mentions with their typed
targets, document names and imports, reading groups, compatibility constraints,
validity bindings, self-truth labels and the recorded reading choices.

Spans. On the wire a mention's span is a byte range of the prose. In Lean a
mention's `span` and a slot's `span` are token ranges `[i, j)` of the unit's token
list (`DDoc.text`): the decoder maps prose bytes to tokens through the lexer, which
is a named trust boundary exactly as for the core English surface (`Lexicon.lean`). -/
namespace VE.Discourse
open VE.Route.Admission (ReadingSet Doc DocUnit)

inductive TargetKind | entity | predicate | unit | anchor | rule | claim | document
  deriving DecidableEq, Repr

inductive Form
  | pronoun | demonstrative | definite | ordinalPair | such | possessive | plural
  | sectionRef | definitionRef | documentName | citation | navigation
  deriving DecidableEq, Repr

inductive Reading | assertive | presuppositional | distributive deriving DecidableEq, Repr
inductive ConstraintKind | requires | excludes deriving DecidableEq, Repr
inductive DocRefers | self | embedded (unit : String) | imported (key : String) | part (anchor : String)
  deriving DecidableEq, Repr
inductive Verdict | checked | refuted | unconfirmed (reason : String) deriving DecidableEq, Repr

structure Target where
  kind : TargetKind
  name : Option String
  version : Option Nat
  members : List String
  pair : Option (String × String)
  units : List String
  contentName : Option String
  deriving DecidableEq, Repr

structure Anchor where
  id : String
  kind : String
  parent : Option String
  label : String
  span : Nat × Nat
  edition : Option String
  exports : List String
  deriving DecidableEq, Repr

structure Name where
  constant : String
  display : String
  scope : String
  aliases : List String
  deriving DecidableEq, Repr

structure ContentName where
  name : String
  units : List String
  scope : String
  deriving DecidableEq, Repr

structure Mention where
  id : String
  unit : String
  span : Nat × Nat
  form : Form
  target : Target
  restriction : Option VE.Formula
  reading : Option Reading
  presuppositionUnit : Option String
  pin : Option Nat                    -- the target's recorded `version` pin (checked by `pinOk`)
  bytes : Nat × Nat := span           -- the prose byte range as recorded (slot discovery compares it)
  deriving DecidableEq, Repr

/-- A slot of a derivation: a surface position and a form, never a target (4.3); a
nested mention (1.4) is a slot inside another slot's span. -/
structure Slot where
  unit : String
  span : Nat × Nat
  form : Form
  deriving DecidableEq, Repr

structure DocName where
  name : String
  display : List String
  refers : DocRefers
  version : Nat
  author : Option String
  supersedes : List String
  scope : Option String
  sourceId : Option String
  documentId : Option String
  deriving DecidableEq, Repr

structure Import where
  key : String
  sourceId : String
  documentId : String
  bytes : Option ByteArray

structure Group where
  set : String
  version : Nat
  reading : Nat
  spans : List String
  deriving DecidableEq, Repr

structure Constraint where
  kind : ConstraintKind
  a : String × Nat × Nat
  b : String × Nat × Nat
  deriving DecidableEq, Repr

structure Validity where
  unit : String
  document : String
  holds : Bool
  deriving DecidableEq, Repr

structure Manifest where
  definitionsVersion : String
  documentSort : String
  anchors : List Anchor
  names : List Name
  contentNames : List ContentName
  mentions : List Mention
  documents : List DocName
  imports : List Import
  groups : List Group
  constraints : List Constraint
  validity : List Validity
  selfTruth : List String
  choices : List (String × Nat × Nat)

/-- An active reading set of the document (the latest version per unit, `ve/readings.py`):
its owning unit, status (`authored` or `open`) and readings as (reading id, content). W2's
decoded document keeps only the all-assertion sets, without ids or status. -/
structure FrontSet where
  id : String
  unit : String
  version : Nat
  status : String
  readings : List (String × VE.Formula)
  deriving DecidableEq, Repr

/-- A `ve-document@2` document: the environment, W2's decoded document, the manifest,
the source identity and the tokenised English text of each unit; beside W2's document, the
active reading sets and each unit's W2 status as the loader computed them. -/
structure DDoc where
  E : VE.Environment
  base : Doc
  K : Manifest
  sourceId : String
  text : String → Option (List VE.English.Tok)
  sets : List FrontSet
  status : List (String × String)
  prose : String                      -- the source (an embedded document is a unit's bytes of it)
  files : Lean.Json                   -- the sibling files an import may name (4.1(10))
  nouns : List (String × String) := [] -- (sort, declared singular noun): slot discovery and Acc read them

/-- The unit record of a unit id. -/
def unitOf (D : Doc) (u : String) : Option DocUnit := D.units.find? (fun x => x.id == u)

/-! ## The derived `BEq` of P0 terms and formulas is lawful

W3's citation checks compare leaves with the derived `BEq` of `VE.Formula`; these lemmas
let the discourse proofs read those Boolean checks as list membership. -/

theorem term_eq_of_beq : ∀ a b : VE.Term, (a == b) = true → a = b
  | .var i, .var j, h => by change (i == j) = true at h; simp at h; rw [h]
  | .const c, .const d, h => by change (c == d) = true at h; simp at h; rw [h]
  | .var _, .const _, h => by change false = true at h; cases h
  | .const _, .var _, h => by change false = true at h; cases h

theorem term_beq_refl : ∀ a : VE.Term, (a == a) = true
  | .var i => by change (i == i) = true; simp
  | .const c => by change (c == c) = true; simp

instance : LawfulBEq VE.Term where
  eq_of_beq := term_eq_of_beq _ _
  rfl := term_beq_refl _

theorem formula_eq_of_beq : ∀ a b : VE.Formula, (a == b) = true → a = b := by
  intro a
  induction a with
  | top => intro b h; cases b <;> first | rfl | (change false = true at h; cases h)
  | bottom => intro b h; cases b <;> first | rfl | (change false = true at h; cases h)
  | unary p t =>
    intro b h
    cases b with
    | unary q w =>
      change (p == q && t == w) = true at h
      simp only [Bool.and_eq_true, beq_iff_eq] at h
      rw [h.1, h.2]
    | _ => change false = true at h; cases h
  | binary p t w =>
    intro b h
    cases b with
    | binary q t' w' =>
      change (p == q && (t == t' && w == w')) = true at h
      simp only [Bool.and_eq_true, beq_iff_eq] at h
      rw [h.1, h.2.1, h.2.2]
    | _ => change false = true at h; cases h
  | eq t w =>
    intro b h
    cases b with
    | eq t' w' =>
      change (t == t' && w == w') = true at h
      simp only [Bool.and_eq_true, beq_iff_eq] at h
      rw [h.1, h.2]
    | _ => change false = true at h; cases h
  | not a ih =>
    intro b h
    cases b with
    | not a' => change (a == a') = true at h; rw [ih a' h]
    | _ => change false = true at h; cases h
  | and a c iha ihc =>
    intro b h
    cases b with
    | and a' c' =>
      change (a == a' && c == c') = true at h
      simp only [Bool.and_eq_true] at h
      rw [iha a' h.1, ihc c' h.2]
    | _ => change false = true at h; cases h
  | or a c iha ihc =>
    intro b h
    cases b with
    | or a' c' =>
      change (a == a' && c == c') = true at h
      simp only [Bool.and_eq_true] at h
      rw [iha a' h.1, ihc c' h.2]
    | _ => change false = true at h; cases h
  | implies a c iha ihc =>
    intro b h
    cases b with
    | implies a' c' =>
      change (a == a' && c == c') = true at h
      simp only [Bool.and_eq_true] at h
      rw [iha a' h.1, ihc c' h.2]
    | _ => change false = true at h; cases h
  | all s a ih =>
    intro b h
    cases b with
    | all s' a' =>
      change (s == s' && a == a') = true at h
      simp only [Bool.and_eq_true, beq_iff_eq] at h
      rw [h.1, ih a' h.2]
    | _ => change false = true at h; cases h
  | ex s a ih =>
    intro b h
    cases b with
    | ex s' a' =>
      change (s == s' && a == a') = true at h
      simp only [Bool.and_eq_true, beq_iff_eq] at h
      rw [h.1, ih a' h.2]
    | _ => change false = true at h; cases h

theorem formula_beq_refl : ∀ a : VE.Formula, (a == a) = true
  | .top => rfl
  | .bottom => rfl
  | .unary p t => by change (p == p && t == t) = true; simp
  | .binary p t w => by change (p == p && (t == t && w == w)) = true; simp
  | .eq t w => by change (t == t && w == w) = true; simp
  | .not a => by change (a == a) = true; exact formula_beq_refl a
  | .and a c => by change (a == a && c == c) = true; simp [formula_beq_refl a, formula_beq_refl c]
  | .or a c => by change (a == a && c == c) = true; simp [formula_beq_refl a, formula_beq_refl c]
  | .implies a c => by change (a == a && c == c) = true; simp [formula_beq_refl a, formula_beq_refl c]
  | .all s a => by change (s == s && a == a) = true; simp [formula_beq_refl a]
  | .ex s a => by change (s == s && a == a) = true; simp [formula_beq_refl a]

instance : LawfulBEq VE.Formula where
  eq_of_beq := formula_eq_of_beq _ _
  rfl := formula_beq_refl _

end VE.Discourse
