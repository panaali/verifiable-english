import VE.RightClauses.PlainWellFormed.W1Ext
import VE.NormDefaults.Check

/-! W1's checks under a change of guards (8.3, `plain_wellFormed`): on `TRel`-related trees every check but the
shared AST budget reads the same answer, so `checkW1` on the extended tree passes or reports
`ResourceLimit: AST exceeds 10,000 nodes`, and when it passes so does W1's `check`. `checkW1` is read through its
named steps (`checkW1_eq`, `rfl`, as `VE.NormDefaults.check_eq` reads `check`). Proof vocabulary only. -/
namespace VE.RightClauses.PWF
open VE.Norms (Node Tree Doc)
open VE.NormDefaults (ruleBody astBody overBody overInner regBody defBody dupNameOf CheckOK NodeOK RulesOK
  OverOK ruleNodes)

/-- `checkW1` after its rule loop. -/
def tailW1 (D : Doc) : Except String Unit :=
  forIn D.T.nodes PUnit.unit (overBody D) >>= fun _ =>
  match VE.Route.dependencyOrder (VE.Norms.precedenceNodes D.T) with
  | .error e => throw e
  | .ok _ =>
    if VE.SoftNorms.heightExceeds D.T = true then throw "ResourceLimit: precedence depth"
    else match VE.Route.dependencyOrder (VE.Norms.stratumNodes D.T) with
      | .error e => throw e
      | .ok _ => pure ()

/-- `checkW1` with its loop bodies named. -/
def checkW1Steps (D : Doc) : Except String Unit :=
  if D.T.regulated.length > 64 then throw "ResourceLimit: regulated predicates" else
  match dupNameOf (VE.Norms.regulatedNames D.T ++ D.T.definitions.map VE.Norms.Definition.name) with
  | some n => throw s!"DuplicateDeclaration: predicate {n}"
  | _ =>
    forIn D.T.regulated PUnit.unit (regBody D) >>= fun _ =>
    VE.Norms.actChecks D.T.regulated >>= fun _ =>
    forIn D.T.definitions PUnit.unit (defBody D) >>= fun _ =>
    if D.T.nodes.length > 256 then throw "ResourceLimit: rules" else
    forIn D.T.nodes (⟨[], 0⟩ : MProd (List String) Nat) (ruleBody D) >>= fun r =>
    match r with
    | ⟨_, _⟩ => tailW1 D

theorem checkW1_eq (D : Doc) : VE.SoftNorms.checkW1 D = checkW1Steps D := rfl

/-! ### Typing passes, so only the budget can fail -/

theorem termSort_ok {E : VE.Environment} {Γ : List String} {t : VE.Term} {s : String}
    (h : t.sortOf E Γ = some s) : VE.Norms.termSort E Γ t = .ok s := by
  cases t <;> simp_all [VE.Norms.termSort, VE.Term.sortOf]

theorem typeDiagnostic_ok (E : VE.Environment) :
    ∀ (Γ : List String) (φ : VE.Formula), φ.check E Γ = true → VE.Norms.typeDiagnostic E Γ φ = .ok ()
  | _, .top, _ | _, .bottom, _ => rfl
  | Γ, .unary p t, h => by
    simp only [VE.Formula.check] at h
    split at h
    · rename_i s r hp ht
      simp only [beq_iff_eq] at h; subst h
      simp [VE.Norms.typeDiagnostic, hp, termSort_ok ht, bind, Except.bind, pure, Except.pure]
    · cases h
  | Γ, .binary p t u, h => by
    simp only [VE.Formula.check] at h
    split at h
    · rename_i s r s' r' hp ht hu
      simp only [Bool.and_eq_true, beq_iff_eq] at h; obtain ⟨rfl, rfl⟩ := h
      simp [VE.Norms.typeDiagnostic, hp, termSort_ok ht, termSort_ok hu, bind, Except.bind, pure, Except.pure]
    · cases h
  | Γ, .eq t u, h => by
    simp only [VE.Formula.check] at h
    split at h
    · rename_i s r ht hu
      simp only [beq_iff_eq] at h; subst h
      simp [VE.Norms.typeDiagnostic, termSort_ok ht, termSort_ok hu, bind, Except.bind, pure, Except.pure]
    · cases h
  | Γ, .not a, h => typeDiagnostic_ok E Γ a h
  | Γ, .and a b, h | Γ, .or a b, h | Γ, .implies a b, h => by
    simp only [VE.Formula.check, Bool.and_eq_true] at h
    simp [VE.Norms.typeDiagnostic, typeDiagnostic_ok E Γ a h.1, typeDiagnostic_ok E Γ b h.2, bind, Except.bind]
  | Γ, .all s a, h | Γ, .ex s a, h => by
    simp only [VE.Formula.check, Bool.and_eq_true] at h
    have hs : s ∈ E.sorts := by simpa using h.1
    simp [VE.Norms.typeDiagnostic, hs, typeDiagnostic_ok E _ a h.2, bind, Except.bind, pure, Except.pure]

/-- The resource-limit text of the shared AST budget. -/
def astRL : String := "ResourceLimit: AST exceeds 10,000 nodes"

theorem astLoop_rl (D : Doc) (r : VE.Norms.Regulated) (N : Node) :
    ∀ (fs : List VE.Formula) (n : Nat), (∀ φ ∈ fs, φ.check D.E r.sorts.reverse = true) →
      forIn fs n (astBody D r N) = .ok (n + (fs.map VE.Bridge.formulaNodes).sum) ∨
        forIn fs n (astBody D r N) = .error astRL
  | [], n, _ => Or.inl (by simp; rfl)
  | φ :: fs, n, h => by
    have hφ := h φ (by simp)
    have hd := typeDiagnostic_ok D.E _ φ hφ
    rw [List.forIn_cons]
    by_cases hb : n + VE.Bridge.formulaNodes φ > VE.Limits.maxNodes
    · right
      simp [astBody, hd, hφ, hb, bind, Except.bind, astRL, throw, throwThe, MonadExceptOf.throw]
    · have hs : astBody D r N φ n = .ok (.yield (n + VE.Bridge.formulaNodes φ)) := by
        simp [astBody, hd, hφ, hb, bind, Except.bind, pure, Except.pure]
      rw [hs]
      simp only [bind, Except.bind]
      rcases astLoop_rl D r N fs _ (fun ψ hψ => h ψ (by simp [hψ])) with h' | h'
      · left; rw [h']; simp [Nat.add_assoc]
      · right; exact h'

/-- A node whose checks pass but for the budget. -/
def NodeOKT (D : Doc) (N : Node) : Prop :=
  VE.Norms.ruleName N.name = true ∧ N.carveOuts.length ≤ 8 ∧
    ∃ r, D.T.regulated.find? (fun x => x.name == N.pred) = some r ∧
      ∀ φ ∈ N.guard :: N.carveOuts, φ.check D.E r.sorts.reverse = true

theorem ruleLoop_rl (D : Doc) :
    ∀ (ns : List Node) (names : List String) (k : Nat), (∀ N ∈ ns, NodeOKT D N) → (ns.map Node.name).Nodup →
      (∀ N ∈ ns, N.name ∉ names) →
      (∃ s, forIn ns (⟨names, k⟩ : MProd (List String) Nat) (ruleBody D) = .ok s) ∨
        forIn ns (⟨names, k⟩ : MProd (List String) Nat) (ruleBody D) = .error astRL
  | [], _, _, _, _, _ => Or.inl ⟨_, rfl⟩
  | N :: ns, names, k, hok, hnd, hfr => by
    obtain ⟨hn, hc, r, hr, ht⟩ := hok N (by simp)
    have hnN : N.name ∉ names := hfr N (by simp)
    rw [List.forIn_cons]
    have hb : ruleBody D N ⟨names, k⟩ = (forIn (N.guard :: N.carveOuts) k (astBody D r N) >>= fun nodes =>
        pure (.yield ⟨names ++ [N.name], nodes⟩)) := by
      simp [ruleBody, hn, hnN, hr, Nat.not_lt.2 hc]
    rw [hb]
    rcases astLoop_rl D r N _ k ht with h' | h'
    · rw [h']
      simp only [bind, Except.bind, pure, Except.pure]
      simp only [List.map_cons, List.nodup_cons, List.mem_map, not_exists, not_and] at hnd
      exact ruleLoop_rl D ns _ _ (fun M hM => hok M (by simp [hM])) hnd.2
        (fun M hM h => by
          simp only [List.mem_append, List.mem_singleton] at h
          rcases h with h | h
          · exact hfr M (by simp [hM]) h
          · exact hnd.1 M hM h)
    · right; rw [h']; rfl

/-! ### Transfer -/

theorem bind_eq_ok {α : Type} {x : Except String α} {f : α → Except String Unit} :
    (x >>= f) = .ok () ↔ ∃ a, x = .ok a ∧ f a = .ok () := by
  cases x <;> simp [bind, Except.bind]

section Transfer
variable {Q : String → VE.Formula → VE.Formula → Prop} {ι : Type} {L : List ι} {f f' : ι → Node}
  (h : TRel Q L f f') (E : VE.Environment) (lits : List String) (r : List VE.Norms.Regulated)
  (d : List VE.Norms.Definition)

/-- The extensions type wherever the old formulas do, at each rule's declared sorts. -/
def TypesAt (Q : String → VE.Formula → VE.Formula → Prop) (L : List ι) (f : ι → Node) (E : VE.Environment)
    (r : List VE.Norms.Regulated) : Prop :=
  ∀ x ∈ L, ∀ r0, r.find? (fun y => y.name == (f x).pred) = some r0 → ∀ a b, Q (f x).pred a b →
    a.check E r0.sorts.reverse = true → b.check E r0.sorts.reverse = true

include h

theorem TRel.nodeOKT (hT : TypesAt Q L f E r) {x : ι} (hx : x ∈ L) (hok : NodeOK ⟨E, lits, ⟨r, d, L.map f⟩⟩ (f x)) :
    NodeOKT ⟨E, lits, ⟨r, d, L.map f'⟩⟩ (f' x) := by
  obtain ⟨hn, hc, r0, hr, ht⟩ := hok
  obtain ⟨hg, cs, ha, hb, hcs⟩ := h.rel x hx
  refine ⟨by rw [h.name]; exact hn, by rw [hb, List.length_map]; rw [ha, List.length_map] at hc; exact hc, r0,
    by simp only [h.pred]; exact hr, ?_⟩
  exact (h.rel x hx).check (hT x hx r0 hr) (fun φ hφ => (ht φ hφ).2)

theorem TRel.overBody_eq (x : ι) :
    overBody ⟨E, lits, ⟨r, d, L.map f'⟩⟩ (f' x) = overBody ⟨E, lits, ⟨r, d, L.map f⟩⟩ (f x) := by
  have hi : overInner ⟨E, lits, ⟨r, d, L.map f'⟩⟩ (f' x) = overInner ⟨E, lits, ⟨r, d, L.map f⟩⟩ (f x) := by
    funext m u
    unfold overInner
    simp only [List.find?_map, Function.comp_def, h.name]
    cases L.find? (fun y => (f y).name == m) with
    | none => rfl
    | some y => simp only [Option.map_some, h.pred, h.name]
  unfold overBody
  rw [h.over, hi]

theorem TRel.tailW1 (hP : ∀ p a b, Q p a b → (VE.Norms.preds b).filter (keepOf r d) = (VE.Norms.preds a).filter (keepOf r d)) :
    tailW1 ⟨E, lits, ⟨r, d, L.map f'⟩⟩ = tailW1 ⟨E, lits, ⟨r, d, L.map f⟩⟩ := by
  unfold PWF.tailW1
  simp only [List.forIn_map, h.overBody_eq, h.precedenceNodes, h.heightExceeds, h.dependencyOrder r d hP]

theorem TRel.checkW1 (hT : TypesAt Q L f E r)
    (hP : ∀ p a b, Q p a b → (VE.Norms.preds b).filter (keepOf r d) = (VE.Norms.preds a).filter (keepOf r d))
    (hA : VE.SoftNorms.checkW1 ⟨E, lits, ⟨r, d, L.map f⟩⟩ = .ok ()) :
    OkOrRL (VE.SoftNorms.checkW1 ⟨E, lits, ⟨r, d, L.map f'⟩⟩) ∧
      (VE.SoftNorms.checkW1 ⟨E, lits, ⟨r, d, L.map f'⟩⟩ = .ok () →
        RulesOK ⟨E, lits, ⟨r, d, L.map f'⟩⟩) := by
  have hreg : regBody ⟨E, lits, ⟨r, d, L.map f'⟩⟩ = regBody ⟨E, lits, ⟨r, d, L.map f⟩⟩ := rfl
  have hdef : defBody ⟨E, lits, ⟨r, d, L.map f'⟩⟩ = defBody ⟨E, lits, ⟨r, d, L.map f⟩⟩ := rfl
  rw [checkW1_eq] at hA ⊢
  unfold checkW1Steps at hA ⊢
  simp only [hreg, hdef, List.length_map, h.tailW1 E lits r d hP, VE.Norms.regulatedNames] at hA ⊢
  by_cases h64 : r.length > 64
  · simp [h64, VE.NormDefaults.ethrow_ok] at hA
  simp only [h64, if_false] at hA ⊢
  cases hdup : dupNameOf (r.map VE.Norms.Regulated.name ++ d.map VE.Norms.Definition.name) with
  | some n => simp [hdup, VE.NormDefaults.ethrow_ok] at hA
  | none =>
    simp only [hdup] at hA ⊢
    obtain ⟨u1, h1, hA⟩ := bind_eq_ok.1 hA
    obtain ⟨u2, h2, hA⟩ := bind_eq_ok.1 hA
    obtain ⟨u3, h3, hA⟩ := bind_eq_ok.1 hA
    by_cases h256 : L.length > 256
    · simp [h256, VE.NormDefaults.ethrow_ok] at hA
    simp only [h256, if_false] at hA
    obtain ⟨sA, hsA, hA⟩ := bind_eq_ok.1 hA
    obtain ⟨hokA, hndA, -, -, -⟩ := (VE.NormDefaults.rulesLoop_ok _ (L.map f) [] 0 sA).1 hsA
    have hok : ∀ N ∈ L.map f', NodeOKT ⟨E, lits, ⟨r, d, L.map f'⟩⟩ N := by
      intro N hN
      obtain ⟨x, hx, rfl⟩ := List.mem_map.1 hN
      exact h.nodeOKT E lits r d hT hx (hokA _ (List.mem_map_of_mem hx))
    have hnd : ((L.map f').map Node.name).Nodup := by
      simpa only [List.map_map, Function.comp_def, h.name] using hndA
    have hrule : ruleBody ⟨E, lits, ⟨r, d, L.map f'⟩⟩ = ruleBody ⟨E, lits, ⟨r, d, L.map f⟩⟩ := rfl
    have htail : PWF.tailW1 ⟨E, lits, ⟨r, d, L.map f⟩⟩ = .ok () := by cases sA; exact hA
    rw [h1, h2, h3]
    simp only [bind, Except.bind, h256, if_false]
    rcases ruleLoop_rl _ (L.map f') [] 0 hok hnd (by simp) with ⟨sB, hsB⟩ | hrl
    · rw [hsB]
      refine ⟨by cases sB; exact Or.inl htail, fun _ => ?_⟩
      obtain ⟨hokB, hndB, -, hsum, -⟩ := (VE.NormDefaults.rulesLoop_ok _ (L.map f') [] 0 sB).1 hsB
      refine ⟨hokB, hndB, ?_⟩
      by_cases hL : L.map f' = []
      · rw [hL]; simp
      · simpa using hsum hL
    · rw [hrl]
      exact ⟨Or.inr ⟨_, rfl, ⟨"AST exceeds 10,000 nodes", by decide⟩⟩, fun h' => by cases h'⟩

theorem TRel.check (hP : ∀ p a b, Q p a b → (VE.Norms.preds b).filter (keepOf r d) = (VE.Norms.preds a).filter (keepOf r d))
    (hA : VE.Norms.check ⟨E, lits, ⟨r, d, L.map f⟩⟩ = .ok ()) (hR : RulesOK ⟨E, lits, ⟨r, d, L.map f'⟩⟩) :
    VE.Norms.check ⟨E, lits, ⟨r, d, L.map f'⟩⟩ = .ok () := by
  rw [VE.NormDefaults.check_iff] at hA ⊢
  obtain ⟨c1, c2, c3, c4, c5, c6, -, c8, c9, c10, c11⟩ := hA
  refine ⟨c1, c2, c3, c4, c5, by simpa using c6, hR, ?_, ?_, ?_, ?_⟩
  · intro N hN m hm
    obtain ⟨x, hx, rfl⟩ := List.mem_map.1 hN
    rw [h.over] at hm
    obtain ⟨M, hM, hMp⟩ := c8 (f x) (List.mem_map_of_mem hx) m hm
    simp only [List.find?_map, Option.map_eq_some_iff, Function.comp_def] at hM ⊢
    obtain ⟨y, hy, rfl⟩ := hM
    refine ⟨f' y, ⟨y, by simpa only [h.name] using hy, rfl⟩, ?_⟩
    rw [h.pred, h.pred, hMp]
  · simp only [h.precedenceNodes]; exact c9
  · intro N hN
    obtain ⟨x, hx, rfl⟩ := List.mem_map.1 hN
    simp only [List.length_map] at c10 ⊢
    rw [h.height]
    simpa using c10 (f x) (List.mem_map_of_mem hx)
  · simp only [h.dependencyOrder r d hP]; exact c11

end Transfer

end VE.RightClauses.PWF
