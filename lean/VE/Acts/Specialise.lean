import VE.Acts.Tree
import VE.Norms.Elaborate

/-! Specialisation (docs/spec/act-phrases.md 1.9, 8; plan 2.6, decision D5): when one simple act is a way of doing
another, through the markers and adverbs the `acts` block declares restrictive only, and the premises
`∀ x̄. p_a x̄ → p_b x̄` it licenses between permission or obligation predicates.

AP-5 defines and proves these only. Nothing calls them: no route, profile, pack or Background hook reads
`specPremises` until AP-5b's bridge (`act-specialise@0`) passes its own review (plan AP-5b). `acts` is built from
`analyse` on each declared act and from the parts of a split; `analyse` renames nothing.
-/

namespace VE.Acts

structure Restrictive where
  markers : List String
  adverbs : List String
  deriving DecidableEq, Repr
def Modifier.restrictive (ρ : Restrictive) : Modifier → Bool
  | .adv w => ρ.adverbs.contains w
  | .prep m _ => ρ.markers.contains m
/-- `a ⊑ b`: same function words and head; every argument and modifier of `b` is one of `a`; every argument or
    modifier `a` has beyond `b` is restrictive. -/
def specialises (ρ : Restrictive) (a b : Atom) : Bool :=
  a.toWord == b.toWord && a.beWord == b.beWord && a.head == b.head &&
  b.args.all (a.args.contains ·) && b.mods.all (a.mods.contains ·) &&
  (a.args.filter (fun x => !b.args.contains x)).all (fun x => ρ.markers.contains x.1) &&
  (a.mods.filter (fun x => !b.mods.contains x)).all (Modifier.restrictive ρ)

/-- The regulated declaration named `n`, when exactly one declares it. -/
def declaredOnce (E : VE.Norms.Doc) (n : String) : Option VE.Norms.Regulated :=
  match E.T.regulated.filter (·.name == n) with
  | [r] => some r
  | _ => none

/-- One premise `∀ x̄. p_a x̄ → p_b x̄` per ordered pair of declared simple acts of one permission or obligation role,
    equal sorts, `a ⊑ b`, `a ≠ b`. -/
def specPremises (E : VE.Norms.Doc) (ρ : Restrictive) (acts : List (String × Atom)) : List VE.Formula :=
  acts.flatMap fun pa => acts.filterMap fun pb =>
    match declaredOnce E pa.1, declaredOnce E pb.1 with
    | some ra, some rb =>
      if ra.role != .plain && ra.role == rb.role && ra.sorts == rb.sorts && pa.2 != pb.2 &&
          specialises ρ pa.2 pb.2 then
        some (VE.Norms.bindAll ra.sorts (.implies (VE.Norms.atom ra.name ra.sorts) (VE.Norms.atom rb.name ra.sorts)))
      else none
    | _, _ => none

/-! ### The statements of spec 8 -/

theorem specialises_refl (ρ : Restrictive) (a : Atom) : specialises ρ a a = true := by
  simp only [specialises, beq_self_eq_true, List.all_eq_true, List.contains_iff_mem, List.mem_filter,
    Bool.and_eq_true, Bool.not_eq_true']
  exact ⟨⟨⟨⟨⟨⟨trivial, trivial⟩, trivial⟩, fun _ h => h⟩, fun _ h => h⟩,
    fun _ h => by simp [h.1] at h⟩,
    fun _ h => by simp [h.1] at h⟩

theorem specialises_trans {ρ : Restrictive} {a b c : Atom} :
    specialises ρ a b = true → specialises ρ b c = true → specialises ρ a c = true := by
  simp only [specialises, Bool.and_eq_true, beq_iff_eq, List.all_eq_true, List.contains_iff_mem, List.mem_filter,
    Bool.not_eq_true', and_imp]
  intro h1 h2 h3 hba hbm hra hrm g1 g2 g3 hcb hcm gra grm
  refine ⟨⟨⟨⟨⟨⟨h1.trans g1, h2.trans g2⟩, h3.trans g3⟩, fun x hx => hba x (hcb x hx)⟩,
    fun x hx => hbm x (hcm x hx)⟩, fun x hx hnc => ?_⟩, fun x hx hnc => ?_⟩
  · by_cases hb : x ∈ b.args
    · exact gra x hb hnc
    · exact hra x hx (by simpa using hb)
  · by_cases hb : x ∈ b.mods
    · exact grm x hb hnc
    · exact hrm x hx (by simpa using hb)

theorem declaredOnce_mem {E : VE.Norms.Doc} {n : String} {r : VE.Norms.Regulated} (h : declaredOnce E n = some r) :
    r ∈ E.T.regulated ∧ r.name = n ∧ ∀ r' ∈ E.T.regulated, r'.name = n → r' = r := by
  unfold declaredOnce at h
  split at h
  · rename_i hf
    cases h
    have hm : r ∈ E.T.regulated.filter (·.name == n) := by rw [hf]; exact List.mem_singleton_self r
    simp only [List.mem_filter, beq_iff_eq] at hm
    refine ⟨hm.1, hm.2, fun r' hr' hn => ?_⟩
    have : r' ∈ E.T.regulated.filter (·.name == n) := List.mem_filter.mpr ⟨hr', by simpa using hn⟩
    rw [hf] at this
    exact List.mem_singleton.mp this
  · cases h

/-- What a premise is: `ra` and `rb`, each the one declaration of its name, of one non-plain role and equal sorts. -/
theorem mem_specPremises {E : VE.Norms.Doc} {ρ : Restrictive} {acts : List (String × Atom)} {φ : VE.Formula}
    (h : φ ∈ specPremises E ρ acts) : ∃ pa pb ra rb, declaredOnce E pa = some ra ∧ declaredOnce E pb = some rb ∧
      ra.role ≠ .plain ∧ ra.role = rb.role ∧ ra.sorts = rb.sorts ∧
      φ = VE.Norms.bindAll ra.sorts (.implies (VE.Norms.atom ra.name ra.sorts) (VE.Norms.atom rb.name ra.sorts)) := by
  simp only [specPremises, List.mem_flatMap, List.mem_filterMap] at h
  obtain ⟨pa, -, pb, -, hφ⟩ := h
  split at hφ
  · rename_i ra rb hra hrb
    split at hφ
    · rename_i hc
      simp only [Bool.and_eq_true, bne_iff_ne, ne_eq, beq_iff_eq] at hc
      obtain ⟨⟨⟨⟨hp, hr⟩, hs⟩, -⟩, -⟩ := hc
      cases hφ
      exact ⟨pa.1, pb.1, ra, rb, hra, hrb, hp, hr, hs, rfl⟩
    · cases hφ
  · cases hφ

theorem specPremises_typed (E : VE.Norms.Doc) (ρ : Restrictive) (acts : List (String × Atom))
    (h : VE.Norms.WellFormed E = true) : ∀ φ ∈ specPremises E ρ acts, φ.check E.E [] = true := by
  intro φ hφ
  obtain ⟨pa, pb, ra, rb, hra, hrb, -, -, hs, rfl⟩ := mem_specPremises hφ
  have hv := VE.Norms.valid_of_wellFormed E h
  obtain ⟨hpa, ha, hsa⟩ := hv.decl _ (hv.regulated ra (declaredOnce_mem hra).1)
  obtain ⟨hpb, -, -⟩ := hv.decl _ (hv.regulated rb (declaredOnce_mem hrb).1)
  simp only [VE.Norms.Sym.name, VE.Norms.Sym.sorts] at hpa ha hsa hpb
  rw [← hs] at hpb
  rw [VE.check_iff_wellFormed]
  refine VE.Norms.bindAll_wellFormed hsa [] _ ?_
  simp only [List.append_nil]
  exact ⟨VE.Norms.atom_wellFormed ha hpa, VE.Norms.atom_wellFormed ha hpb⟩

theorem preds_bindAll (body : VE.Formula) : ∀ ss : List String, VE.Norms.preds (VE.Norms.bindAll ss body) =
    VE.Norms.preds body
  | [] => rfl
  | s :: ss => by simpa [VE.Norms.bindAll, VE.Norms.preds] using preds_bindAll body ss

theorem mem_preds_atom {p n : String} {ss : List String} (h : n ∈ VE.Norms.preds (VE.Norms.atom p ss)) : n = p := by
  unfold VE.Norms.atom at h
  split at h <;> simp_all [VE.Norms.preds]

theorem specPremises_plain (E : VE.Norms.Doc) (ρ : Restrictive) (acts : List (String × Atom)) :
    ∀ r ∈ E.T.regulated, r.role = .plain → ∀ φ ∈ specPremises E ρ acts, r.name ∉ VE.Norms.preds φ := by
  intro r hr hp φ hφ hn
  obtain ⟨pa, pb, ra, rb, hra, hrb, hna, hab, -, rfl⟩ := mem_specPremises hφ
  obtain ⟨-, hnA, huA⟩ := declaredOnce_mem hra
  obtain ⟨-, hnB, huB⟩ := declaredOnce_mem hrb
  rw [preds_bindAll] at hn
  simp only [VE.Norms.preds, List.mem_append] at hn
  rcases hn with hn | hn
  · exact hna (huA r hr ((mem_preds_atom hn).trans hnA) ▸ hp)
  · exact hna (hab ▸ huB r hr ((mem_preds_atom hn).trans hnB) ▸ hp)

end VE.Acts
