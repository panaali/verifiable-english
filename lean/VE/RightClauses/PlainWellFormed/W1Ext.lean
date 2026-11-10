import VE.RightClauses.PlainWellFormed.SoftExt
import VE.NormDefaults.Dag

/-! W1 trees under a change of guards and carve-outs (8.3, `plain_wellFormed`): two trees whose nodes are one
index list under two node maps `f`, `f'` with the same names, predicates, signs and `over`, and `f' x` extending
`f x` by `FExt`. Their children, `yields`, `selects` and heights correspond, the stratum DAG sees the same edges
(so the same layer order), and `semanticCheck` carries over. Proof vocabulary only. -/
namespace VE.RightClauses.PWF
open VE.Norms (Node Tree Doc anyF preds)

/-- `B` is `A` with its guard and carve-outs extended at `A`'s predicate. -/
def NRel (Q : String → VE.Formula → VE.Formula → Prop) (A B : Node) : Prop :=
  FExt (Q A.pred) A.guard B.guard ∧ ∃ cs : List (VE.Formula × VE.Formula),
    A.carveOuts = cs.map Prod.fst ∧ B.carveOuts = cs.map Prod.snd ∧ ∀ c ∈ cs, FExt (Q A.pred) c.1 c.2

/-- Two node maps over one index list: same keys, `f'` extends `f` on the list. -/
structure TRel (Q : String → VE.Formula → VE.Formula → Prop) {ι : Type} (L : List ι) (f f' : ι → Node) : Prop where
  name : ∀ x, (f' x).name = (f x).name
  pred : ∀ x, (f' x).pred = (f x).pred
  over : ∀ x, (f' x).over = (f x).over
  sign : ∀ x, (f' x).sign = (f x).sign
  rel : ∀ x ∈ L, NRel Q (f x) (f' x)

variable {Q : String → VE.Formula → VE.Formula → Prop} {ι : Type}

theorem NRel.applies {A B : Node} (h : NRel Q A B) :
    FExt (Q A.pred) (VE.Norms.applies A) (VE.Norms.applies B) := by
  obtain ⟨hg, cs, ha, hb, hc⟩ := h
  unfold VE.Norms.applies; rw [ha, hb]
  exact .and hg (.not (FExt.anyF Prod.fst Prod.snd cs hc))

/-- Children by index. -/
def cidx (f : ι → Node) (L : List ι) (x : ι) : List ι :=
  VE.Norms.sortBy (fun a b => decide ((f a).name < (f b).name))
    (L.flatMap (fun c => if (f c).pred == (f x).pred then ((f c).over.filter (· == (f x).name)).map (fun _ => c)
      else []))

theorem children_map (r : List VE.Norms.Regulated) (d : List VE.Norms.Definition) (f : ι → Node) (L : List ι)
    (x : ι) : VE.Norms.children ⟨r, d, L.map f⟩ (f x) = (cidx f L x).map f := by
  unfold VE.Norms.children cidx
  have h : ∀ c, (if (f c).pred == (f x).pred then ((f c).over.filter (· == (f x).name)).map (fun _ => f c) else []) =
      (if (f c).pred == (f x).pred then ((f c).over.filter (· == (f x).name)).map (fun _ => c) else []).map f := by
    intro c; split <;> simp
  simp only [List.flatMap_map, h]
  rw [← List.map_flatMap, sortBy_map]

theorem mem_cidx {f : ι → Node} {L : List ι} {x c : ι} (h : c ∈ cidx f L x) : c ∈ L ∧ (f c).pred = (f x).pred := by
  simp only [cidx, VE.Norms.mem_sortBy, List.mem_flatMap] at h
  obtain ⟨c', hc', hm⟩ := h
  split at hm
  · rename_i hp
    obtain ⟨_, -, rfl⟩ := List.mem_map.1 hm
    exact ⟨hc', by simpa using hp⟩
  · cases hm

theorem TRel.cidx_eq {L : List ι} {f f' : ι → Node} (h : TRel Q L f f') (x : ι) : cidx f' L x = cidx f L x := by
  simp only [cidx, h.name, h.pred, h.over]

theorem yields_ext {L : List ι} {f f' : ι → Node} (h : TRel Q L f f') (r : List VE.Norms.Regulated)
    (d : List VE.Norms.Definition) : ∀ (n : Nat) (x : ι), x ∈ L →
    FExt (Q (f x).pred) (VE.Norms.yields ⟨r, d, L.map f⟩ n (f x)) (VE.Norms.yields ⟨r, d, L.map f'⟩ n (f' x))
  | 0, x, hx => .or (h.rel x hx).applies (.refl _)
  | n + 1, x, hx => by
    simp only [VE.Norms.yields, children_map, h.cidx_eq, List.map_map]
    refine .or (h.rel x hx).applies (FExt.anyF _ _ _ (fun c hc => ?_))
    obtain ⟨hcL, hp⟩ := mem_cidx hc
    simp only [Function.comp_def]; rw [← hp]; exact yields_ext h r d n c hcL

theorem selects_ext {L : List ι} {f f' : ι → Node} (h : TRel Q L f f') (r : List VE.Norms.Regulated)
    (d : List VE.Norms.Definition) (n : Nat) (x : ι) (hx : x ∈ L) :
    FExt (Q (f x).pred) (VE.Norms.selects ⟨r, d, L.map f⟩ n (f x)) (VE.Norms.selects ⟨r, d, L.map f'⟩ n (f' x)) := by
  simp only [VE.Norms.selects, children_map, h.cidx_eq, List.map_map]
  refine .and (h.rel x hx).applies (.not (FExt.anyF _ _ _ (fun c hc => ?_)))
  obtain ⟨hcL, hp⟩ := mem_cidx hc
  simp only [Function.comp_def]; rw [← hp]; exact yields_ext h r d n c hcL

theorem rulesOn_map (r : List VE.Norms.Regulated) (d : List VE.Norms.Definition) (f : ι → Node) (L : List ι)
    (p : String) : VE.Norms.rulesOn ⟨r, d, L.map f⟩ p = (L.filter (fun x => (f x).pred == p)).map f := by
  simp [VE.Norms.rulesOn, List.filter_map, Function.comp_def]

theorem TRel.filter_eq {L : List ι} {f f' : ι → Node} (h : TRel Q L f f') (p : String) :
    L.filter (fun x => (f' x).pred == p) = L.filter (fun x => (f x).pred == p) := by
  simp only [h.pred]

/-! ### Heights and the precedence DAG -/

theorem TRel.height {L : List ι} {f f' : ι → Node} (h : TRel Q L f f') (r : List VE.Norms.Regulated)
    (d : List VE.Norms.Definition) : ∀ (n : Nat) (x : ι),
    VE.Norms.height ⟨r, d, L.map f'⟩ n (f' x) = VE.Norms.height ⟨r, d, L.map f⟩ n (f x)
  | 0, _ => rfl
  | n + 1, x => by
    simp only [VE.Norms.height, children_map, h.cidx_eq, List.map_map, Function.comp_def, h.height r d n]

theorem TRel.precedenceNodes {L : List ι} {f f' : ι → Node} (h : TRel Q L f f') (r : List VE.Norms.Regulated)
    (d : List VE.Norms.Definition) :
    VE.Norms.precedenceNodes ⟨r, d, L.map f'⟩ = VE.Norms.precedenceNodes ⟨r, d, L.map f⟩ := by
  simp only [VE.Norms.precedenceNodes, List.map_map, Function.comp_def, h.name, h.over]

theorem heightLevels_nodes (T T' : Tree) (hl : T'.nodes.length = T.nodes.length) (kids : Array (List Nat)) :
    ∀ n, VE.SoftNorms.heightLevels T' kids n = VE.SoftNorms.heightLevels T kids n
  | 0 => by
    simp only [VE.SoftNorms.heightLevels]
    congr 1
    apply List.ext_getElem (by simp [hl]); intro i _ _; simp
  | n + 1 => by simp only [VE.SoftNorms.heightLevels, heightLevels_nodes T T' hl kids n]

theorem TRel.heightExceeds {L : List ι} {f f' : ι → Node} (h : TRel Q L f f') (r : List VE.Norms.Regulated)
    (d : List VE.Norms.Definition) :
    VE.SoftNorms.heightExceeds ⟨r, d, L.map f'⟩ = VE.SoftNorms.heightExceeds ⟨r, d, L.map f⟩ := by
  unfold VE.SoftNorms.heightExceeds
  have hk : ((⟨r, d, L.map f'⟩ : Tree).nodes.map (fun N => (VE.Norms.children ⟨r, d, L.map f'⟩ N).filterMap
      (fun C => (L.map f').findIdx? (·.name == C.name)))) =
      ((⟨r, d, L.map f⟩ : Tree).nodes.map (fun N => (VE.Norms.children ⟨r, d, L.map f⟩ N).filterMap
      (fun C => (L.map f).findIdx? (·.name == C.name)))) := by
    simp only [List.map_map, Function.comp_def, children_map, h.cidx_eq, List.filterMap_map, List.findIdx?_map,
      h.name]
  simp only [hk, heightLevels_nodes ⟨r, d, L.map f⟩ ⟨r, d, L.map f'⟩ (by simp)]
  simp

/-! ### The stratum DAG and the layer order -/

theorem filter_flatMap_congr {α β : Type} (p : β → Bool) (g h : α → List β) :
    ∀ l : List α, (∀ x ∈ l, (g x).filter p = (h x).filter p) → (l.flatMap g).filter p = (l.flatMap h).filter p
  | [], _ => rfl
  | a :: l, hl => by
    simp only [List.flatMap_cons, List.filter_append, hl a (by simp),
      filter_flatMap_congr p g h l (fun x hx => hl x (by simp [hx]))]

theorem nodeNames_stratum (T : Tree) :
    VE.Route.nodeNames (VE.Norms.stratumNodes T) = T.regulated.map (·.name) ++ T.definitions.map (·.name) := by
  simp [VE.Norms.stratumNodes, VE.Route.nodeNames, Function.comp_def]

/-- What the stratum DAG keeps of a mention: a regulated or defined predicate. -/
def keepOf (r : List VE.Norms.Regulated) (d : List VE.Norms.Definition) (s : String) : Bool :=
  (r.map (·.name) ++ d.map (·.name)).contains s

theorem NRel.preds {A B : Node} {keep : String → Bool} (h : NRel Q A B)
    (hP : ∀ p a b, Q p a b → (preds b).filter keep = (preds a).filter keep) :
    ((B.guard :: B.carveOuts).flatMap preds).filter keep = ((A.guard :: A.carveOuts).flatMap preds).filter keep := by
  obtain ⟨hg, cs, ha, hb, hc⟩ := h
  simp only [List.flatMap_cons, List.filter_append, FExt.preds (hP _) hg, ha, hb, List.flatMap_map]
  congr 1
  exact filter_flatMap_congr keep _ _ cs (fun c hc' => FExt.preds (hP _) (hc c hc'))

theorem TRel.stratum_key {L : List ι} {f f' : ι → Node} (h : TRel Q L f f') (r : List VE.Norms.Regulated)
    (d : List VE.Norms.Definition) (hP : ∀ p a b, Q p a b → (preds b).filter (keepOf r d) = (preds a).filter (keepOf r d)) :
    VE.NormDefaults.keyOf (VE.Norms.stratumNodes ⟨r, d, L.map f'⟩) =
      VE.NormDefaults.keyOf (VE.Norms.stratumNodes ⟨r, d, L.map f⟩) := by
  unfold VE.NormDefaults.keyOf VE.Route.deps
  rw [nodeNames_stratum, nodeNames_stratum]
  simp only [VE.Norms.stratumNodes, List.map_append, List.map_map]
  congr 1
  apply List.map_congr_left
  intro r0 _
  simp only [Function.comp_def, VE.Norms.Sym.formulas, rulesOn_map, h.filter_eq, List.flatMap_map,
    List.flatMap_assoc]
  congr 1
  apply filter_flatMap_congr
  intro x hx
  exact (h.rel x (List.mem_filter.1 hx).1).preds hP

theorem TRel.dependencyOrder {L : List ι} {f f' : ι → Node} (h : TRel Q L f f') (r : List VE.Norms.Regulated)
    (d : List VE.Norms.Definition) (hP : ∀ p a b, Q p a b → (preds b).filter (keepOf r d) = (preds a).filter (keepOf r d)) :
    VE.Route.dependencyOrder (VE.Norms.stratumNodes ⟨r, d, L.map f'⟩) =
      VE.Route.dependencyOrder (VE.Norms.stratumNodes ⟨r, d, L.map f⟩) :=
  VE.NormDefaults.dependencyOrder_congr (h.stratum_key r d hP)

theorem TRel.syms {L : List ι} {f f' : ι → Node} (h : TRel Q L f f') (r : List VE.Norms.Regulated)
    (d : List VE.Norms.Definition) (hP : ∀ p a b, Q p a b → (preds b).filter (keepOf r d) = (preds a).filter (keepOf r d)) :
    VE.Norms.syms ⟨r, d, L.map f'⟩ = VE.Norms.syms ⟨r, d, L.map f⟩ := by
  simp only [VE.Norms.syms, VE.Norms.order, h.dependencyOrder r d hP]
  rfl

theorem NRel.check {A B : Node} {E : VE.Environment} {Γ : List String} (h : NRel Q A B)
    (hP : ∀ a b, Q A.pred a b → a.check E Γ = true → b.check E Γ = true)
    (hA : ∀ φ ∈ A.guard :: A.carveOuts, φ.check E Γ = true) : ∀ φ ∈ B.guard :: B.carveOuts, φ.check E Γ = true := by
  obtain ⟨hg, cs, ha, hb, hc⟩ := h
  intro φ hφ
  rcases List.mem_cons.1 hφ with rfl | hφ
  · exact FExt.check hP hg (hA _ (by simp))
  · rw [hb] at hφ
    obtain ⟨c, hcs, rfl⟩ := List.mem_map.1 hφ
    exact FExt.check hP (hc c hcs) (hA _ (List.mem_cons_of_mem _ (by rw [ha]; exact List.mem_map_of_mem hcs)))

theorem TRel.formulas_check {L : List ι} {f f' : ι → Node} (h : TRel Q L f f') (r : List VE.Norms.Regulated)
    (d : List VE.Norms.Definition) (r0 : VE.Norms.Regulated) {E : VE.Environment} {Γ : List String}
    (hP : ∀ a b, Q r0.name a b → a.check E Γ = true → b.check E Γ = true)
    (hA : ∀ φ ∈ (VE.Norms.Sym.reg r0).formulas ⟨r, d, L.map f⟩, φ.check E Γ = true) :
    ∀ φ ∈ (VE.Norms.Sym.reg r0).formulas ⟨r, d, L.map f'⟩, φ.check E Γ = true := by
  simp only [VE.Norms.Sym.formulas, rulesOn_map, h.filter_eq, List.mem_flatMap, List.mem_map, List.mem_filter,
    beq_iff_eq] at hA ⊢
  rintro φ ⟨_, ⟨x, ⟨hx, hp⟩, rfl⟩, hφ⟩
  refine (h.rel x hx).check ?_ (fun ψ hψ => hA ψ ⟨f x, ⟨x, ⟨hx, hp⟩, rfl⟩, hψ⟩) φ hφ
  rw [hp]; exact hP

theorem mem_syms_reg {T : Tree} {r0 : VE.Norms.Regulated} (h : VE.Norms.Sym.reg r0 ∈ VE.Norms.syms T) :
    r0 ∈ T.regulated := by
  simp only [VE.Norms.syms, List.mem_filterMap, VE.Norms.lookupSym] at h
  obtain ⟨n, -, hn⟩ := h
  split at hn
  · rename_i r1 hr1; cases hn; exact List.mem_of_find?_eq_some hr1
  · cases hd : T.definitions.find? (·.name == n) <;> simp [hd] at hn

theorem TRel.semanticCheck {L : List ι} {f f' : ι → Node} (h : TRel Q L f f') (E : VE.Environment)
    (lits : List String) (r : List VE.Norms.Regulated) (d : List VE.Norms.Definition)
    (hP : ∀ p a b, Q p a b → (preds b).filter (keepOf r d) = (preds a).filter (keepOf r d))
    (hC : ∀ r0 ∈ r, ∀ k a b, Q r0.name a b → a.check (VE.Norms.envAt ⟨E, lits, ⟨r, d, L.map f⟩⟩ k) r0.sorts.reverse = true →
      b.check (VE.Norms.envAt ⟨E, lits, ⟨r, d, L.map f⟩⟩ k) r0.sorts.reverse = true)
    (hA : VE.Norms.semanticCheck ⟨E, lits, ⟨r, d, L.map f⟩⟩ = true) :
    VE.Norms.semanticCheck ⟨E, lits, ⟨r, d, L.map f'⟩⟩ = true := by
  have hs := h.syms r d hP
  have hl : VE.Norms.layerNames ⟨r, d, L.map f'⟩ = VE.Norms.layerNames ⟨r, d, L.map f⟩ := by
    simp only [VE.Norms.layerNames, hs]
  have he : ∀ k, VE.Norms.envAt ⟨E, lits, ⟨r, d, L.map f'⟩⟩ k = VE.Norms.envAt ⟨E, lits, ⟨r, d, L.map f⟩⟩ k := by
    intro k; simp only [VE.Norms.envAt, hl]
  unfold VE.Norms.semanticCheck at hA ⊢
  simp only [hs, he, hl, h.precedenceNodes, h.dependencyOrder r d hP, Bool.and_eq_true] at hA ⊢
  obtain ⟨⟨⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩, h7⟩ := hA
  refine ⟨⟨⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, ?_⟩, h6⟩, h7⟩
  rw [List.all_eq_true] at h5 ⊢
  intro k hk
  have h5k := h5 k hk
  revert h5k
  cases hq : (VE.Norms.syms ⟨r, d, L.map f⟩)[k]? with
  | none => exact id
  | some q =>
    simp only [List.all_eq_true]
    intro h5k
    cases q with
    | defn d0 => exact h5k
    | reg r0 =>
      have hr0 : r0 ∈ r := mem_syms_reg (T := ⟨r, d, L.map f⟩) (List.mem_of_getElem? hq)
      exact h.formulas_check r d r0 (hC r0 hr0 k) h5k

end VE.RightClauses.PWF
