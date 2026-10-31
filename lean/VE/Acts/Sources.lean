import VE.Acts.Readings
import VE.Readings.Choice
import VE.NormDefaults.Tree

/-! Sources and exact reading sets (docs/spec/act-phrases.md 1.8, 7; plan AP-4, G4).

A `Source` names an act phrase, the template every reading keeps (role and sign, which fix the op; guard, carve-outs
and precedence; the three-valued completion), the fixed units every reading shares and the reading sets the phrase is
read into. `sourceCheck` lexes the phrase, lists its readings under the op (`phraseReadings`, once) and their
paraphrases (D-32), then compares each choice's rules with the readings' simple acts up to order: every choice is a
reading, no two choices are the same reading, every reading has a choice, and the matching is a bijection (D-29).
`sourceCheck_exact` is spec 7's statement. The completion is read from the original metadata (`unspec`), never from
the frame's placeholder `deny`, so a choice that changes only `unspecified` to `deny` is refused (S7; SR3). No route
calls `sourceCheck` yet: ap-4's admission hook does.
-/

/-- Two lists of one length related pointwise by `R` (Mathlib's `List.Forall₂`, which spec 7's `SourceExact` names;
    this project has no Mathlib). -/
inductive List.Forall₂ {α β : Type} (R : α → β → Prop) : List α → List β → Prop
  | nil : List.Forall₂ R [] []
  | cons {a b l₁ l₂} : R a b → List.Forall₂ R l₁ l₂ → List.Forall₂ R (a :: l₁) (b :: l₂)

namespace VE.Acts
open Lexical (Tok)

/-- A source: an act phrase as the source words it, the source template (role and sign, which fix the op; the guard,
    carve-outs and precedence; the completion), the units every reading shares, and the reading sets it is read into. -/
structure Source where
  phrase : String
  role : VE.Norms.Role
  sign : Bool
  form : Option Lexical.Form
  template : VE.Norms.Node        -- guard, carve-outs and precedence every reading keeps; `name` and `pred` unused
  completion : VE.NormDefaults.Completion   -- deny, allow or unspecified: the completion every part keeps (SR3)
  units : List String             -- fixed units every reading shares (u105a)
  sets : List String

/-- What a rule says, for comparison: its predicate's act, role and completion; its sign, guard, carve-outs, over. -/
abbrev View := String × VE.Norms.Role × Bool × VE.Formula × List VE.Formula × List String × VE.NormDefaults.Completion
set_option synthInstance.maxSize 1024 in
instance : DecidableEq View := inferInstance

/-- `unspec` is the frame's original `unspecified` predicates (`VE.Readings.Wire.unspecOf`): the frame itself is decoded
    with `unspecified` read as the placeholder `deny`, so the completion is read as `VE.NormDefaults.completionOf`
    does with `unspec`, never from `allowByDefault` alone. A rule on an undeclared predicate, or on one with no act,
    has no view. -/
def ruleView (D : VE.Readings.Doc) (unspec : List String) (N : VE.SoftNorms.SoftNode) : Option View :=
  (D.frame.soft.T.regulated.find? (·.name == N.pred)).bind fun r => r.act.map fun a =>
    (a, r.role, N.sign, N.guard, N.carveOuts, N.over,
     VE.NormDefaults.completionOf ⟨⟨D.frame.soft.E, [], ⟨[], [], []⟩⟩, unspec⟩ r)

/-- The act is `Simple.text fx (some (s.role == .plain)) x`: the part's act for an atom (`partAct`), the join's text
    for a whole join (5.5). -/
def expected (fx : List String) (s : Source) (x : Simple) : View :=
  (Simple.text fx (some (s.role == .plain)) x, s.role, s.sign, s.template.guard, s.template.carveOuts,
   s.template.over, s.completion)

def choicesOn (D : VE.Readings.Doc) (sets : List String) : List (List (String × Nat)) :=
  firsts ((VE.Readings.choices D).map (fun c => c.filter (fun x => sets.contains x.1)))

/-- The rules of a choice in the document's item order: each listed fixed unit's rule and the rule of the candidate
    `c` chooses in each set it names (`choicesOn` names the listed sets only). -/
def choiceRules (D : VE.Readings.Doc) (s : Source) (c : List (String × Nat)) : List VE.SoftNorms.SoftNode :=
  D.items.flatMap fun
    | .fixed u (.norm M) _ => if s.units.contains u then [M] else []
    | .set R => match ((VE.Readings.Choice.index c R.id).bind (R.candidates[·]?)).bind (·.content) with
      | some (.norm M) => [M]
      | _ => []
    | _ => []

def choiceViews (D : VE.Readings.Doc) (unspec : List String) (s : Source) : List (List (Option View)) :=
  (choicesOn D s.sets).map (fun c => (choiceRules D s c).map (ruleView D unspec))
def readingViews (fx : List String) (s : Source) (Rs : List (List Simple)) : List (List (Option View)) :=
  Rs.map (fun R => R.map (fun x => some (expected fx s x)))

/-- The op the template's role and sign fix: `opOf`'s table (1.7), read on the template. -/
def opOfSource (s : Source) : Option Op :=
  opOf ⟨"", [], false, s.role, none, none⟩ s.sign

/-! ### The comparison (D-29) -/

/-- For each reading, the first choice whose views are a permutation of it; `none` when a reading has none. -/
def pick (cs : List (List (Option View))) : List (List (Option View)) → Option (List (List (Option View)))
  | [] => some []
  | r :: rs => match cs.find? (fun c => decide (c.Perm r)), pick cs rs with
    | some c, some σ => some (c :: σ)
    | _, _ => none

def d29 (m : String) : String := "InvalidInput: " ++ m

/-- D-29 in its order: a choice that is no reading (a changed modal, guard, exceptions, precedence or completion
    included), two choices that are one reading, a reading with no choice (named by its paraphrase), the counts. -/
def compareViews (ps : List String) (cs rs : List (List (Option View))) : Except String Unit :=
  if !cs.all (fun c => rs.any (fun r => decide (c.Perm r))) then
    .error (d29 ("a choice is not a reading of the source phrase, or changes the source rule's modal, guard, " ++
      "exceptions, precedence or completion"))
  else if !decide (cs.Pairwise (fun v w => ¬ v.Perm w)) then .error (d29 "two choices give the same reading")
  else match pick cs rs with
    | none => .error (d29 ("a reading of the source phrase has no choice: " ++
        ((ps.zip rs).find? (fun x => (cs.find? (fun c => decide (c.Perm x.2))).isNone)).elim "" (·.1)))
    | some σ => if decide (σ.Perm cs) then .ok ()
      else .error (d29 s!"the reading sets give {cs.length} choices for a phrase with {rs.length} readings")

/-- Lex the phrase, list its readings under the template's op once, their paraphrases (D-32), then compare (D-29).
    Each value is computed once, and the comparison is bounded before it starts: at most `maxReadings` readings
    (`phraseReadings_length`) and `VE.Readings.maxChoices + 1` choices (`VE.Readings.choices` is cut there), so each
    of its steps makes at most 65 × 64 permutation tests. -/
def sourceCheck (D : VE.Readings.Doc) (unspec : List String) (V : Vocab) (fx : List String) (N b : Nat) (s : Source) :
    Except String Unit :=
  match Lexical.lex fx s.phrase, opOfSource s with
  | .error e, _ => .error e
  | .ok _, none => .error "InvalidInput: the source has no modal word for its act"
  | .ok ts, some op => match phraseReadings V op N b ts.toArray with
    | .limit => .error "ResourceLimit: the source phrase has too many readings to list; split the sentence"
    | .ok Rs => match paraphrases fx op s.form "the source phrase" Rs with
      | .error e => .error e
      | .ok ps => compareViews ps (choiceViews D unspec s) (readingViews fx s Rs)

/-- The outer bijection is kept; each choice's rules are compared with its reading's simple acts up to order (SR14):
    `σ` lists the choices' views reordered so that the k-th is a permutation of reading k's. -/
def SourceExact (D : VE.Readings.Doc) (unspec : List String) (V : Vocab) (fx : List String) (N b : Nat)
    (s : Source) : Prop :=
  ∃ ts op Rs, Lexical.lex fx s.phrase = .ok ts ∧ opOfSource s = some op ∧
    phraseReadings V op N b ts.toArray = .ok Rs ∧
    (∀ R, R ∈ Rs ↔ ∃ A, Derived V ts A ∧ R ∈ table op A) ∧
    (Rs.map (paraphrase fx op s.form)).Nodup ∧
    (choiceViews D unspec s).Pairwise (fun v w => ¬ v.Perm w) ∧
    ∃ σ, σ.Perm (choiceViews D unspec s) ∧ List.Forall₂ List.Perm σ (readingViews fx s Rs)

theorem pick_forall₂ {cs : List (List (Option View))} :
    ∀ {rs σ}, pick cs rs = some σ → List.Forall₂ List.Perm σ rs
  | [], σ, h => by cases h; exact .nil
  | r :: rs, σ, h => by
    unfold pick at h
    split at h
    · rename_i c σ' hc hσ
      cases h
      have hp := List.find?_some hc
      exact .cons (of_decide_eq_true hp) (pick_forall₂ hσ)
    · cases h

theorem compareViews_ok {ps : List String} {cs rs : List (List (Option View))} (h : compareViews ps cs rs = .ok ()) :
    cs.Pairwise (fun v w => ¬ v.Perm w) ∧ ∃ σ, σ.Perm cs ∧ List.Forall₂ List.Perm σ rs := by
  unfold compareViews at h
  split at h
  · cases h
  split at h
  · cases h
  rename_i hp
  split at h
  · cases h
  rename_i σ hσ
  split at h
  · rename_i hperm
    exact ⟨of_decide_eq_true (by simpa using hp), σ, of_decide_eq_true hperm, pick_forall₂ hσ⟩
  · cases h

/-- Exactness: a bijection between the phrase's readings, complete against the grammar, and the listed choices;
    each choice's rules regulate exactly its reading's simple acts, in any order, with the template's sign, guard,
    carve-outs, precedence, role and completion. -/
theorem sourceCheck_exact (D unspec V fx N b s) (h : framesOk V = true)
    (hc : sourceCheck D unspec V fx N b s = .ok ()) : SourceExact D unspec V fx N b s := by
  unfold sourceCheck at hc
  split at hc
  · cases hc
  · cases hc
  rename_i ts op hl ho
  split at hc
  · cases hc
  rename_i Rs hR
  split at hc
  · cases hc
  rename_i ps hps
  obtain ⟨-, hn⟩ := paraphrases_nodup hps
  obtain ⟨hpw, σ, hσ, hf⟩ := compareViews_ok hc
  refine ⟨ts, op, Rs, hl, ho, hR, fun R => ?_, (paraphrases_nodup hps).1 ▸ hn, hpw, σ, hσ, hf⟩
  simpa using phraseReadings_exact V h hR R

end VE.Acts
