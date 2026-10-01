import VE.Discourse.Grammar
import VE.Discourse.Documents

/-! # Elaboration and the intended meaning (docs/spec/discourse.md 4.4 to 4.6, 9.2, 9.3)

`elaborateD D d σ` substitutes each slot of the derivation `d` by its target's elaboration:
a constant term, the members of a distributive plural (a conjunction), a copied property, or
a definite description (the assertive `∃x:σ (Dr x ∧ ∀y:σ (Dr y → y = x) ∧ P x)` or the
presuppositional claim `∀x:σ (Dr x → P x)`), the nested possessive first. Slot terms are
constants, so substitution is capture-avoiding by construction. The reading of a definite is
the recorded mention's reading, a fixed input and never a filter. `SlotMeaning` interprets
each slot directly in a structure, without reference to `elaborateD`; `elaborateD_capture`
is their agreement. Targets enter only through `canonTarget`, so aliases never change a
formula (`elaborate_alias`). -/
namespace VE.Discourse
open VE.English (Tok)
universe u

/-- A location target (1.4): a `unit` or `anchor` target produces no formula and never fills a
slot, whatever the mention's form. -/
def locationKind (k : TargetKind) : Bool := k == .unit || k == .anchor

/-- The mention the manifest records at a slot (its unit, span and form); a location binding
is never one. -/
def mentionAt (D : DDoc) (m : Slot) : Option Mention :=
  D.K.mentions.find? fun x => x.unit == m.unit && x.span == m.span && x.form == m.form &&
    !locationKind x.target.kind

/-- `K.target(m)`: the target the manifest records at slot `m`. -/
def recordedTarget (D : DDoc) (m : Slot) : Option Target := (mentionAt D m).map Mention.target

def readingAt (D : DDoc) (m : Slot) : Option Reading := (mentionAt D m).bind Mention.reading

def Assignment := Slot → Target

/-- The constant a target denotes as a term. -/
def termConst : Target → Option String
  | ⟨.entity, some c, none, [], none, [], none⟩ => if notBinder c then some c else none
  | ⟨.entity, some c, none, [], some _, [], none⟩ => some c
  | ⟨.document, some d, none, [], none, [], none⟩ => some d
  | _ => none

def pluralMembers : Target → Option (List String)
  | ⟨.entity, none, none, ms, none, [], none⟩ => if 2 ≤ ms.length then some ms else none
  | _ => none

def npConsts (D : DDoc) (σ : Assignment) : NP → Option (List String)
  | .name c _ => some [c]
  | .slot m => if m.form == .plural then pluralMembers (canonTarget D (σ m))
      else (termConst (canonTarget D (σ m))).map ([·])
  | .definite _ _ => none

def conjOn (p : String) (cs : List String) : VE.Formula := conj (cs.map fun c => .unary p (.const c))

/-- The restriction's sort and formula over `[sort]`, the nested possessive substituted first. -/
def restrFormula (D : DDoc) (σ : Assignment) : Restr → Option (String × VE.Formula)
  | .noun q => match D.E.predicates q with
    | some [s] => some (s, .unary q (.var 0))
    | _ => none
  | .rel q poss => match D.E.predicates q, termConst (canonTarget D (σ poss)) with
    | some [s, _], some c => some (s, .binary q (.var 0) (.const c))
    | _, _ => none

def definiteFormula (D : DDoc) (σ : Assignment) (m : Slot) (r : Restr) (p : String) : Option VE.Formula :=
  if canonTarget D (σ m) = entityTarget "binder:0" then
    match restrFormula D σ r, readingAt D m with
    | some (s, Dr), some .assertive => some (assertive s Dr (.unary p (.var 0)))
    | some (s, Dr), some .presuppositional => some (presupposed s Dr (.unary p (.var 0)))
    | _, _ => none
  else none

def predFormula (D : DDoc) (σ : Assignment) (subj : NP) (p : String) : Option VE.Formula :=
  match subj with
  | .definite m r => definiteFormula D σ m r p
  | _ => (npConsts D σ subj).map (conjOn p)

def propertyOf : Target → Option String
  | ⟨.predicate, some q, none, [], none, [], none⟩ => some q
  | _ => none

def modPred (D : DDoc) (σ : Assignment) : Mod → Option (Option String)
  | .none => some none
  | .adj q => some (some q)
  | .slot m => (propertyOf (canonTarget D (σ m))).map some

def quantBody (q : Option String) (p : String) (conn : VE.Formula → VE.Formula → VE.Formula) : VE.Formula :=
  match q with
  | none => .unary p (.var 0)
  | some q => conn (.unary q (.var 0)) (.unary p (.var 0))

def relFormula (p : String) : Option (List String) → Option (List String) → Option VE.Formula
  | some [a], some [b] => some (.binary p (.const a) (.const b))
  | _, _ => none

def coreFormula (D : DDoc) (σ : Assignment) : Core → Option VE.Formula
  | .pred subj _ p => predFormula D σ subj p
  | .coord a _ b _ p => some (.and (.unary p (.const a)) (.unary p (.const b)))
  | .rel subj p obj => relFormula p (npConsts D σ subj) (npConsts D σ obj)
  | .every m srt p => (modPred D σ m).map fun q => .all srt (quantBody q p .implies)
  | .some _ m srt p => (modPred D σ m).map fun q => .ex srt (quantBody q p .and)
  | .everyDef m srt p _ => (propertyOf (canonTarget D (σ m))).map fun q =>
      .all srt (.implies (.unary q (.var 0)) (.unary p (.var 0)))

def isClaim : Target → Bool
  | ⟨.claim, some _, none, [], none, [], none⟩ => true
  | _ => false

/-- 4.4: the closed formula of a derivation under an assignment. -/
def elaborateD (D : DDoc) (d : DTree) (σ : Assignment) : Option VE.Formula :=
  match d.tree with
  | .core c => coreFormula D σ c
  | .cite m c => if isClaim (canonTarget D (σ m)) then coreFormula D σ c else none

/-! ## The intended meaning, slot by slot -/

def constHolds (S : VE.Structure.{u}) (p c : String) : Prop := ∃ v, S.constant c = some v ∧ S.relation p [v]

def restrMeaning (D : DDoc) (S : VE.Structure.{u}) (σ : Assignment) :
    Restr → Option (String × (S.Carrier → Prop))
  | .noun q => match D.E.predicates q with
    | some [s] => some (s, fun a => S.relation q [a])
    | _ => none
  | .rel q poss => match D.E.predicates q, termConst (canonTarget D (σ poss)) with
    | some [s, _], some c => some (s, fun a => ∃ v, S.constant c = some v ∧ S.relation q [a, v])
    | _, _ => none

def definiteMeaning (D : DDoc) (S : VE.Structure.{u}) (σ : Assignment) (m : Slot) (r : Restr) (p : String) :
    Option Prop :=
  if canonTarget D (σ m) = entityTarget "binder:0" then
    match restrMeaning D S σ r, readingAt D m with
    | some (s, R), some .assertive =>
      some (∃ a, S.domain s a ∧ R a ∧ (∀ b, S.domain s b → R b → b = a) ∧ S.relation p [a])
    | some (s, R), some .presuppositional => some (∀ a, S.domain s a → R a → S.relation p [a])
    | _, _ => none
  else none

def predMeaning (D : DDoc) (S : VE.Structure.{u}) (σ : Assignment) (subj : NP) (p : String) : Option Prop :=
  match subj with
  | .definite m r => definiteMeaning D S σ m r p
  | _ => (npConsts D σ subj).map fun cs => ∀ c ∈ cs, constHolds S p c

def quantMeaning (S : VE.Structure.{u}) (q : Option String) (p : String) (a : S.Carrier)
    (conn : Prop → Prop → Prop) : Prop :=
  match q with
  | none => S.relation p [a]
  | some q => conn (S.relation q [a]) (S.relation p [a])

def coreMeaning (D : DDoc) (S : VE.Structure.{u}) (σ : Assignment) : Core → Option Prop
  | .pred subj _ p => predMeaning D S σ subj p
  | .coord a _ b _ p => some (constHolds S p a ∧ constHolds S p b)
  | .rel subj p obj => match npConsts D σ subj, npConsts D σ obj with
    | some [a], some [b] => some (∃ v w, S.constant a = some v ∧ S.constant b = some w ∧ S.relation p [v, w])
    | _, _ => none
  | .every m srt p => (modPred D σ m).map fun q => ∀ a, S.domain srt a → quantMeaning S q p a (· → ·)
  | .some _ m srt p => (modPred D σ m).map fun q => ∃ a, S.domain srt a ∧ quantMeaning S q p a (· ∧ ·)
  | .everyDef m srt p _ => (propertyOf (canonTarget D (σ m))).map fun q =>
      ∀ a, S.domain srt a → S.relation q [a] → S.relation p [a]

def meaningOf (D : DDoc) (S : VE.Structure.{u}) (d : DTree) (σ : Assignment) : Option Prop :=
  match d.tree with
  | .core c => coreMeaning D S σ c
  | .cite m c => if isClaim (canonTarget D (σ m)) then coreMeaning D S σ c else none

/-- The derivation's meaning with each slot interpreted directly in `S` (4.4). The formulas
are closed, so the valuation is not read. -/
def SlotMeaning (D : DDoc) (S : VE.Structure.{u}) (_ρ : VE.Valuation S) (d : DTree) (σ : Assignment) : Prop :=
  match meaningOf D S d σ with
  | some P => P
  | none => False

def contextOf (_d : DTree) : List String := []

/-! ## Agreement of the formula and the meaning -/

theorem conj_denote_at (S : VE.Structure.{u}) (ρ : VE.Valuation S) : ∀ l : List VE.Formula,
    (conj l).denote S ρ ↔ ∀ r ∈ l, r.denote S ρ
  | [] => by simp [conj, VE.Formula.denote]
  | [a] => by simp [conj]
  | a :: b :: l => by
    simp only [conj, VE.Formula.denote]
    rw [conj_denote_at S ρ (b :: l)]
    simp

theorem conjOn_denote (S : VE.Structure.{u}) (ρ : VE.Valuation S) (p : String) (cs : List String) :
    (conjOn p cs).denote S ρ ↔ ∀ c ∈ cs, constHolds S p c := by
  unfold conjOn
  rw [conj_denote_at]
  simp [VE.Formula.denote, VE.Term.denote, constHolds]

theorem unary_var0 (S : VE.Structure.{u}) (p : String) (a : S.Carrier) (ρ : VE.Valuation S) :
    (VE.Formula.unary p (.var 0)).denote S (a :: ρ) ↔ S.relation p [a] := by
  simp [VE.Formula.denote, VE.Term.denote]

theorem restr_agree (D : DDoc) (S : VE.Structure.{u}) (σ : Assignment) (r : Restr) :
    (restrFormula D σ r).map Prod.fst = (restrMeaning D S σ r).map Prod.fst ∧
    ∀ s Dr, restrFormula D σ r = some (s, Dr) → ∃ R, restrMeaning D S σ r = some (s, R) ∧
      ∀ (a : S.Carrier) (ρ : VE.Valuation S), Dr.denote S (a :: ρ) ↔ R a := by
  cases r with
  | noun q =>
    simp only [restrFormula, restrMeaning]
    split
    · refine ⟨rfl, fun s Dr h => ?_⟩
      cases h
      exact ⟨_, rfl, fun a ρ => unary_var0 S q a ρ⟩
    · exact ⟨rfl, fun _ _ h => by cases h⟩
  | rel q poss =>
    simp only [restrFormula, restrMeaning]
    split
    · refine ⟨rfl, fun s Dr h => ?_⟩
      cases h
      refine ⟨_, rfl, fun a ρ => ?_⟩
      simp [VE.Formula.denote, VE.Term.denote]
    · refine ⟨rfl, fun _ _ h => by cases h⟩

theorem definite_agree (D : DDoc) (S : VE.Structure.{u}) (σ : Assignment) (m : Slot) (r : Restr) (p : String)
    (A : VE.Formula) (h : definiteFormula D σ m r p = some A) (ρ : VE.Valuation S) :
    ∃ P, definiteMeaning D S σ m r p = some P ∧ (A.denote S ρ ↔ P) := by
  unfold definiteFormula at h
  unfold definiteMeaning
  split at h
  · rename_i hb
    rw [if_pos hb]
    cases hr : restrFormula D σ r with
    | none => rw [hr] at h; simp at h
    | some x =>
      obtain ⟨s, Dr⟩ := x
      obtain ⟨R, hR, hDR⟩ := (restr_agree D S σ r).2 s Dr hr
      rw [hr] at h
      rw [hR]
      cases hread : readingAt D m with
      | none => rw [hread] at h; simp at h
      | some rd =>
        rw [hread] at h
        cases rd with
        | assertive =>
          simp only [Option.some.injEq] at h
          subst h
          refine ⟨_, rfl, ?_⟩
          simp only [assertive, VE.Formula.denote, VE.Term.denote, List.getElem?_cons_zero,
            List.getElem?_cons_succ, Option.some.injEq, unary_var0]
          constructor
          · rintro ⟨a, ha, hDa, hu, ⟨v, hv, hPa⟩⟩
            cases hv
            refine ⟨a, ha, (hDR a ρ).mp hDa, fun b hb hRb => ?_, hPa⟩
            obtain ⟨v, rfl, rfl⟩ := hu b hb ((hDR b (a :: ρ)).mpr hRb)
            rfl
          · rintro ⟨a, ha, hRa, hu, hPa⟩
            exact ⟨a, ha, (hDR a ρ).mpr hRa, fun b hb hDb =>
              ⟨b, rfl, (hu b hb ((hDR b (a :: ρ)).mp hDb)).symm⟩, ⟨a, rfl, hPa⟩⟩
        | presuppositional =>
          simp only [Option.some.injEq] at h
          subst h
          refine ⟨_, rfl, ?_⟩
          simp only [presupposed, VE.Formula.denote]
          exact forall_congr' fun a => imp_congr_right fun _ => imp_congr (hDR a ρ) (unary_var0 S p a ρ)
        | distributive => simp at h
  · cases h

theorem core_agree (D : DDoc) (S : VE.Structure.{u}) (σ : Assignment) (c : Core) (A : VE.Formula)
    (h : coreFormula D σ c = some A) (ρ : VE.Valuation S) :
    ∃ P, coreMeaning D S σ c = some P ∧ (A.denote S ρ ↔ P) := by
  cases c with
  | pred subj are p =>
    simp only [coreFormula, coreMeaning] at h ⊢
    cases subj with
    | definite m r => exact definite_agree D S σ m r p A h ρ
    | name c k =>
      simp only [predFormula, predMeaning] at h ⊢
      cases hc : npConsts D σ (.name c k) with
      | none => rw [hc] at h; cases h
      | some cs =>
        rw [hc] at h
        simp only [Option.map_some, Option.some.injEq] at h
        subst h
        exact ⟨_, rfl, conjOn_denote S ρ p cs⟩
    | slot m =>
      simp only [predFormula, predMeaning] at h ⊢
      cases hc : npConsts D σ (.slot m) with
      | none => rw [hc] at h; cases h
      | some cs =>
        rw [hc] at h
        simp only [Option.map_some, Option.some.injEq] at h
        subst h
        exact ⟨_, rfl, conjOn_denote S ρ p cs⟩
  | coord a ka b kb p =>
    simp only [coreFormula, coreMeaning, Option.some.injEq] at h ⊢
    subst h
    refine ⟨_, rfl, ?_⟩
    simp [VE.Formula.denote, VE.Term.denote, constHolds]
  | rel subj p obj =>
    simp only [coreFormula, coreMeaning] at h ⊢
    unfold relFormula at h
    split at h
    · rename_i a b ha hb
      cases h
      refine ⟨_, rfl, ?_⟩
      simp [VE.Formula.denote, VE.Term.denote]
    · cases h
  | every m srt p =>
    simp only [coreFormula, coreMeaning] at h ⊢
    cases hq : modPred D σ m with
    | none => rw [hq] at h; cases h
    | some q =>
      rw [hq] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      refine ⟨_, rfl, ?_⟩
      simp only [VE.Formula.denote]
      refine forall_congr' fun a => imp_congr_right fun _ => ?_
      cases q with
      | none => exact unary_var0 S p a ρ
      | some q => simp [quantBody, quantMeaning, VE.Formula.denote, VE.Term.denote]
  | some an m srt p =>
    simp only [coreFormula, coreMeaning] at h ⊢
    cases hq : modPred D σ m with
    | none => rw [hq] at h; cases h
    | some q =>
      rw [hq] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      refine ⟨_, rfl, ?_⟩
      simp only [VE.Formula.denote]
      refine exists_congr fun a => and_congr_right fun _ => ?_
      cases q with
      | none => exact unary_var0 S p a ρ
      | some q => simp [quantBody, quantMeaning, VE.Formula.denote, VE.Term.denote]
  | everyDef m srt p sec =>
    simp only [coreFormula, coreMeaning] at h ⊢
    cases hq : propertyOf (canonTarget D (σ m)) with
    | none => rw [hq] at h; cases h
    | some q =>
      rw [hq] at h
      simp only [Option.map_some, Option.some.injEq] at h
      subst h
      refine ⟨_, rfl, ?_⟩
      simp [VE.Formula.denote, VE.Term.denote]

/-- Capture-avoiding substitution: the slot substitution denotes the slot's value. -/
theorem elaborateD_capture (D : DDoc) (d : DTree) (σ : Assignment) (A : VE.Formula) (h : elaborateD D d σ = some A)
    (S : VE.Structure) (hS : S.Admissible D.E) (ρ : VE.Valuation S) (hρ : VE.Valuation.Typed S (contextOf d) ρ) :
    A.denote S ρ ↔ SlotMeaning D S ρ d σ := by
  unfold elaborateD at h
  unfold SlotMeaning meaningOf
  split at h
  · rename_i c hc
    obtain ⟨P, hP, hA⟩ := core_agree D S σ c A h ρ
    rw [hP]
    exact hA
  · rename_i m c hc
    split at h
    · rename_i hcl
      obtain ⟨P, hP, hA⟩ := core_agree D S σ c A h ρ
      simp only [hcl, if_true, hP]
      exact hA
    · cases h

/-! ## Congruence: only the canonical targets of the derivation's slots matter -/

theorem npConsts_congr (D : DDoc) (σ σ' : Assignment) (np : NP)
    (h : ∀ m ∈ npSlots np, canonTarget D (σ m) = canonTarget D (σ' m)) :
    npConsts D σ np = npConsts D σ' np := by
  cases np with
  | name c k => rfl
  | slot m => simp only [npConsts, h m (by simp [npSlots])]
  | definite m r => rfl

theorem predFormula_congr (D : DDoc) (σ σ' : Assignment) (subj : NP) (p : String)
    (h : ∀ m ∈ npSlots subj, canonTarget D (σ m) = canonTarget D (σ' m)) :
    predFormula D σ subj p = predFormula D σ' subj p := by
  cases subj with
  | name c k => rfl
  | slot m => simp only [predFormula, npConsts_congr D σ σ' (.slot m) h]
  | definite m r =>
    simp only [predFormula, definiteFormula, h m (by cases r <;> simp [npSlots])]
    cases r with
    | noun q => rfl
    | rel q poss => simp only [restrFormula, h poss (by simp [npSlots])]

theorem modPred_congr (D : DDoc) (σ σ' : Assignment) (m : Mod)
    (h : ∀ x ∈ modSlots m, canonTarget D (σ x) = canonTarget D (σ' x)) :
    modPred D σ m = modPred D σ' m := by
  cases m with
  | none => rfl
  | adj q => rfl
  | slot x => simp only [modPred, h x (by simp [modSlots])]

theorem coreFormula_congr (D : DDoc) (σ σ' : Assignment) (c : Core)
    (h : ∀ m ∈ coreSlots c, canonTarget D (σ m) = canonTarget D (σ' m)) :
    coreFormula D σ c = coreFormula D σ' c := by
  cases c with
  | pred subj are p => exact predFormula_congr D σ σ' subj p h
  | coord => rfl
  | rel subj p obj =>
    simp only [coreFormula, npConsts_congr D σ σ' subj (fun m hm => h m (List.mem_append_left _ hm)),
      npConsts_congr D σ σ' obj (fun m hm => h m (List.mem_append_right _ hm))]
  | every m srt p => simp only [coreFormula, modPred_congr D σ σ' m h]
  | some an m srt p => simp only [coreFormula, modPred_congr D σ σ' m h]
  | everyDef m srt p sec => simp only [coreFormula, h m (by simp [coreSlots])]

/-- Aliases never change a formula: the elaboration reads a slot's target only through
`canonTarget`, and only at the derivation's slots. -/
theorem elaborate_alias (D : DDoc) (d : DTree) (σ σ' : Assignment)
    (h : ∀ m ∈ slotsOf d.tree, AliasEq D (σ m) (σ' m)) : elaborateD D d σ = elaborateD D d σ' := by
  unfold elaborateD
  split
  · rename_i c hc
    exact coreFormula_congr D σ σ' c (fun m hm => h m (by rw [hc]; exact hm))
  · rename_i m c hc
    have hm : canonTarget D (σ m) = canonTarget D (σ' m) := h m (by rw [hc]; exact List.mem_cons_self)
    rw [hm, coreFormula_congr D σ σ' c (fun x hx => h x (by rw [hc]; exact List.mem_cons_of_mem _ hx))]

theorem elaborate_congr (D : DDoc) (d : DTree) (σ σ' : Assignment)
    (h : ∀ m ∈ slotsOf d.tree, σ m = σ' m) : elaborateD D d σ = elaborateD D d σ' :=
  elaborate_alias D d σ σ' (fun m hm => by unfold AliasEq; rw [h m hm])

end VE.Discourse
