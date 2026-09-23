import VE.TableauExtendedInduction

namespace VE.Closure.Tableau
universe u

def next (E : Environment) (b : Branch) (index : Nat) (parameter : Option String) :
    Option (List Branch) := do
  let a ← b.formulas[index]?
  match a.rule with
  | .literal => none
  | .closure k e t r => do
    if parameter.isSome || index ∈ b.expanded then none else
      let f ← unfoldAt E b a.bindings k e t r
      some [({ b with expanded := index :: b.expanded }).add [⟨f,a.positive,a.bindings⟩]]
  | .gamma s f => do
    let text ← parameter
    let t ← Token.parse text
    if t.sortOf E b ≠ some s || (index, t) ∈ b.instantiated then none else
      some [({ b with instantiated := (index, t) :: b.instantiated }).add
        [⟨f, a.positive, t :: a.bindings⟩]]
  | rule =>
    if parameter.isSome || index ∈ b.expanded then none else
      let b' := { b with expanded := index :: b.expanded }
      match rule with
      | .one xs => some [b'.add xs]
      | .two x y => some [b'.add [x], b'.add [y]]
      | .delta s f => some [({ b' with witnesses := b.witnesses ++ [s] }).add
          [⟨f, a.positive, .witness b.witnesses.length :: a.bindings⟩]]
      | _ => none

/-- A satisfiable parent has a satisfiable child, possibly under an extended
parameter valuation. This is the invariant used by recursive replay. -/
theorem next_sound {E : Environment} {S : Structure} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hρ : Assignment.Typed S b ρ)
    (hs : b.scoped = true) (hk : b.known E = true) (hh : b.Holds S ρ)
    (index : Nat) (parameter : Option String) (bs : List Branch)
    (hn : next E b index parameter = some bs) :
    ∃ child ∈ bs, ∃ σ, Assignment.Typed S child σ ∧ child.Holds S σ := by
  cases ha : b.formulas[index]? with
  | none => simp [next, ha] at hn
  | some a =>
    have ham : a ∈ b.formulas := List.mem_of_getElem? ha
    have hah := hh a ham
    cases hr : a.rule with
    | literal => simp [next, ha, hr] at hn
    | closure k e t r =>
      simp only [next, ha, hr, bind, Option.bind] at hn
      split at hn
      next => contradiction
      next =>
        cases hf : unfoldAt E b a.bindings k e t r with
        | none => simp [hf] at hn
        | some f =>
          simp only [hf] at hn
          cases hn
          refine ⟨_,List.mem_cons_self,ρ,hρ,?_⟩
          apply add_holds S ρ _ _ hh
          simpa using closure_holds hS b ρ hρ a (known_bindings hS b ρ hρ hk a ham)
            k e t r f hr hah hf
    | gamma s f =>
      cases hp : parameter with
      | none => simp [next, ha, hr, hp] at hn
      | some text =>
        cases ht : Token.parse text with
        | none => simp [next, ha, hr, hp, ht] at hn
        | some t =>
          simp only [next, ha, hr, hp, ht, bind, Option.bind] at hn
          split at hn
          next => contradiction
          next hg =>
            have hsort : t.sortOf E b = some s := by
              have hg' : t.sortOf E b = some s ∧ (index, t) ∉ b.instantiated := by simpa using hg
              exact hg'.1
            obtain ⟨v, hv, hd⟩ := token_defined hS hρ hsort
            cases hn
            refine ⟨_, List.mem_cons_self, ρ, ?_, ?_⟩
            · exact hρ
            apply add_holds S ρ { b with instantiated := (index, t) :: b.instantiated } _ hh
            simpa using gamma_holds S ρ a s f t v hr hah hv hd
    | one xs =>
      simp only [next, ha, hr, bind, Option.bind] at hn
      split at hn
      next => contradiction
      next =>
        cases hn
        refine ⟨_, List.mem_cons_self, ρ, ?_, ?_⟩
        · exact hρ
        · exact add_holds S ρ { b with expanded := index :: b.expanded } xs hh
            (one_holds S ρ a xs hr hah)
    | two x y =>
      simp only [next, ha, hr, bind, Option.bind] at hn
      split at hn
      next => contradiction
      next =>
        cases hn
        rcases two_holds S ρ a x y hr hah with hx | hy
        · refine ⟨_, List.mem_cons_self, ρ, ?_, ?_⟩
          · exact hρ
          · exact add_holds S ρ { b with expanded := index :: b.expanded } [x] hh (by simpa)
        · refine ⟨_, List.mem_cons_of_mem _ (List.mem_cons_self), ρ, hρ, ?_⟩
          exact add_holds S ρ _ [y] hh (by simpa)
    | delta s f =>
      simp only [next, ha, hr, bind, Option.bind] at hn
      split at hn
      next => contradiction
      next =>
        cases hn
        obtain ⟨v, hv, hf⟩ := delta_witness S ρ a s f hr hah
        let σ := extend ρ b.witnesses.length v
        refine ⟨_, List.mem_cons_self, σ, ?_, ?_⟩
        · exact typed_extend S ρ b hρ s v hv
        apply add_holds S σ { b with witnesses := b.witnesses ++ [s], expanded := index :: b.expanded }
          _ (holds_extend S ρ b v hs hh)
        intro x hx
        have hx' : x = ⟨f, a.positive, .witness b.witnesses.length :: a.bindings⟩ := by simpa using hx
        subst x
        have hb := bindings_extend S ρ b.witnesses.length v a.bindings
          (List.all_eq_true.mp hs a ham)
        have hvalue : bindingsValue S σ (.witness b.witnesses.length :: a.bindings) =
            v :: bindingsValue S ρ a.bindings := by
          have he : Token.denote S σ (.witness b.witnesses.length) = some v := by
            simp [Token.denote, σ, extend]
          simp only [bindingsValue, List.filterMap_cons, he]
          exact congrArg (List.cons v) hb
        simpa only [Signed.Holds, hvalue] using hf

def checkChildren (check : Branch → Trace → Bool) : List Branch → List Trace → Bool
  | [], [] => true
  | b :: bs, t :: ts => check b t && checkChildren check bs ts
  | _, _ => false

theorem checkChildren_member (check : Branch → Trace → Bool) (bs : List Branch)
    (ts : List Trace) (hc : checkChildren check bs ts = true) :
    ∀ b ∈ bs, ∃ t, check b t = true := by
  induction bs generalizing ts with
  | nil => simp
  | cons b bs ih =>
    cases ts with
    | nil => contradiction
    | cons t ts =>
      have hc' : check b t = true ∧ checkChildren check bs ts = true := by simpa [checkChildren] using hc
      intro x hx
      rcases List.mem_cons.mp hx with rfl | hx
      · exact ⟨t, hc'.1⟩
      · exact ih ts hc'.2 x hx

def step (E : Environment) (b : Branch) (rule : String) (index : Nat)
    (parameter : Option String) : Option (List Branch) :=
  if extraRule rule then extra E b rule index parameter
  else if (b.formulas[index]?).any (fun a => a.tag == rule) then next E b index parameter
  else none

theorem step_sound {E : Environment} {S : Structure} (hS : S.Admissible E)
    (b : Branch) (ρ : Assignment S) (hρ : Assignment.Typed S b ρ)
    (hs : b.scoped = true) (hk : b.known E = true) (hh : b.Holds S ρ)
    (rule : String) (index : Nat) (parameter : Option String) (bs : List Branch)
    (hn : step E b rule index parameter = some bs) :
    ∃ child ∈ bs, ∃ σ, Assignment.Typed S child σ ∧ child.Holds S σ := by
  unfold step at hn
  split at hn
  · exact extra_sound hS b ρ hρ hh rule index parameter bs hn
  · split at hn
    · exact next_sound hS b ρ hρ hs hk hh index parameter bs hn
    · contradiction

/-- Fuel counts depth, not successful logical steps. Exhaustion rejects. -/
def replay (E : Environment) (compound : Bool := false) (induction : Bool := false) : Nat → Branch → Trace → Bool
  | 0, _, _ => false
  | fuel + 1, b, t =>
    b.scoped && b.known E && match t with
      | .close => (closed E b || (compound && complementary b)) || reachClosed b
      | .expand rule index parameter children =>
        match step E b rule index parameter with
        | none => false
        | some bs => checkChildren (replay E compound induction fuel) bs children
      | .induct index s P children =>
        induction && match induct E b index s P with
        | none => false
        | some bs => checkChildren (replay E compound induction fuel) bs children

theorem replay_sound {E : Environment} {S : Structure} (hS : S.Admissible E)
    (compound induction : Bool) (fuel : Nat) (b : Branch) (ρ : Assignment S) (hρ : Assignment.Typed S b ρ)
    (hh : b.Holds S ρ) (t : Trace) (hc : replay E compound induction fuel b t = true) : False := by
  induction fuel generalizing b ρ t with
  | zero => contradiction
  | succ fuel ih =>
    have hc' := Bool.and_eq_true_iff.mp hc
    obtain ⟨hs, hk⟩ := Bool.and_eq_true_iff.mp hc'.1
    cases t with
    | close =>
      rcases Bool.or_eq_true_iff.mp hc'.2 with hc | hc
      · rcases Bool.or_eq_true_iff.mp hc with hl | hc
        · exact closed_sound hS b ρ hρ hk hh hl
        · exact complementary_sound b ρ hh (Bool.and_eq_true_iff.mp hc).2
      · exact reachClosed_sound hS b ρ hρ hk hh hc
    | expand rule index parameter children =>
      cases hn : step E b rule index parameter with
      | none => simp [replay, hn] at hc
      | some bs =>
        have hchildren : checkChildren (replay E compound induction fuel) bs children = true := by
          simpa [hn] using hc'.2
        obtain ⟨child, hm, σ, ht, hh⟩ := step_sound hS b ρ hρ hs hk hh rule index parameter bs hn
        obtain ⟨t, hc⟩ := checkChildren_member (replay E compound induction fuel) bs children hchildren child hm
        exact ih child σ ht hh t hc
    | induct index s P children =>
      have hc'' := (Bool.and_eq_true_iff.mp hc'.2).2
      cases hn : induct E b index s P with
      | none => simp [hn] at hc''
      | some bs =>
        have hchildren : checkChildren (replay E compound induction fuel) bs children = true := by
          simpa [hn] using hc''
        obtain ⟨child,hm,σ,ht,hh⟩ := induct_sound hS b ρ hρ hh index s P bs hn
        obtain ⟨t,hc⟩ := checkChildren_member (replay E compound induction fuel) bs children hchildren child hm
        exact ih child σ ht hh t hc

def initial (premises : List Formula) (conclusion : Formula) : Branch :=
  ⟨premises.map (fun f => ⟨f, true, []⟩) ++ [⟨conclusion, false, []⟩], [], [], []⟩

/-- The logical checker uses exact AST inputs; wire identity validation is an
additional gate. All constructors and all equality rules are supported. -/
def checkCertificate (E : Environment) (premises : List Formula) (conclusion : Formula)
    (c : Certificate) : Bool :=
  (c.checker_version == "ve-tableau-closure-checker@0" ||
    c.checker_version == "ve-tableau-closure-checker@1") &&
    premises.all (fun f => f.check E []) && conclusion.check E [] &&
    replay E true (c.checker_version == "ve-tableau-closure-checker@1") 125 (initial premises conclusion) c.trace

/-- Sound over every admissible structure at every universe, including empty
sorts and an empty common carrier. There is no certificate-soundness premise. -/
theorem checkCertificate_sound (E : Environment) (premises : List Formula)
    (conclusion : Formula) (c : Certificate) (hc : checkCertificate E premises conclusion c = true) :
    Entails.{u} E premises conclusion := by
  classical
  intro S hS hp
  apply Classical.byContradiction
  intro hn
  have hr : replay E true (c.checker_version == "ve-tableau-closure-checker@1") 125
      (initial premises conclusion) c.trace = true :=
    (Bool.and_eq_true_iff.mp hc).2
  apply replay_sound hS _ _ _ (initial premises conclusion) (fun _ => none) _ _ c.trace hr
  · intro i s hi
    simp [initial] at hi
  · intro a ha
    rcases List.mem_append.mp ha with ha | ha
    · obtain ⟨f, hm, rfl⟩ := List.mem_map.mp ha
      exact hp f hm
    · have he : a = ⟨conclusion, false, []⟩ := by simpa using ha
      subst a
      exact hn

/-- The extended soundness theorem specializes to the unchanged v0 consequence
relation through the proved denotation conservativity theorem. -/
theorem checkCertificate_sound_v0 (E : Environment) (premises : List VE.Formula)
    (conclusion : VE.Formula) (c : Certificate)
    (hc : checkCertificate E (premises.map embed) (embed conclusion) c = true) :
    VE.Entails.{u} E premises conclusion := by
  intro S hS hp
  apply (conservativity S [] conclusion).mp
  apply checkCertificate_sound E (premises.map embed) (embed conclusion) c hc S hS
  intro a ha
  obtain ⟨f,hf,rfl⟩ := List.mem_map.mp ha
  exact (conservativity S [] f).mpr (hp f hf)

end VE.Closure.Tableau
