import VE.Judgments.Status
import VE.SoftNorms.Tree
import VE.NormDefaults.Packs
import VE.Rights.Correlate
import VE.Readings.Strings
import VE.Bridge

/-! Judgment terms beside the soft chain (docs/spec/profile-composition.md 3.1, PC-1; owner judgment-terms). A soft
rule's unit reads its author rule: the guard and the author carve-outs, never what the soft route generates from it
(`primeNode`'s derived carve-out reads opponents' guards, so it is no reader of the unit's own text). A rights block's
unit reads its block as written (`blockFormulas`, pc-1g), and every judgment the rights route's rules and limitation
premises read is read by an author formula (`correlate_judged`). -/

namespace VE.Judgments

/-- PC-1 (1). Formulas whose every predicate is reserved, or already read, change no scan. -/
theorem opensIn_generated (J : List String) (fs gs : List VE.Formula)
    (hJ : ∀ j ∈ J, VE.NormDefaults.Packs.reserved j = false)
    (hg : ∀ g ∈ gs, ∀ p ∈ VE.Norms.preds g,
      VE.NormDefaults.Packs.reserved p = true ∨ ∃ f ∈ fs, p ∈ VE.Norms.preds f) :
    opensIn J (fs ++ gs) = opensIn J fs := by
  unfold opensIn
  apply List.filter_congr
  intro j hj
  simp only [List.any_append, Bool.or_eq_left_iff_imp, List.any_eq_true, List.contains_iff_mem]
  rintro ⟨g, hg', hp⟩
  rcases hg g hg' j hp with hr | ⟨f, hf, hpf⟩
  · exact absurd hr (by simp [hJ j hj])
  · exact ⟨f, hf, hpf⟩

/-- PC-1 (2). What a soft rule's unit reads: its author rule (guard and author carve-outs). -/
def softContent (N : VE.SoftNorms.SoftNode) : Content := .rule N.toNode

theorem softContent_formulas (N : VE.SoftNorms.SoftNode) : (softContent N).formulas = N.guard :: N.carveOuts := rfl

/-! ## The rights chain's reader (PC-1 (3), pc-1g)

Every name the rights route generates (`rights__lim__k`, `rights__cond__k`, `rights__bar__k`) is reserved, so it is no
judgment and names no definition: the route's rules and `Lim_D` read no judgment their author formulas do not. A
limitation's condition is a name with no formula, read as an atom of that name (the scan reads names only); an aim
states no author formula (a bar's name is an identifier, its `aimed` atom generated). The norm units outside rights
are read as written, guard and author carve-outs, as a soft rule is (`softContent`). -/

/-- PC-1 (3). The author formulas of a rights source, as written: holder guards, line guards and author
carve-outs, limitation conditions, aims. -/
def rightsAuthorFormulas (R : VE.Rights.RightsDoc) : List VE.Formula :=
  R.rs.map (·.guard) ++ (VE.Rights.linesOf R).flatMap (fun RN => RN.2.node.guard :: RN.2.node.carveOuts) ++
    R.soft.T.nodes.flatMap (fun N => N.guard :: N.carveOuts) ++
    R.limits.flatMap fun L => L.conditions.map fun c => .unary c.name (.var 0)

theorem preds_inst (σ : List VE.Term) (φ : VE.Formula) : VE.Norms.preds (VE.Norms.inst σ φ) = VE.Norms.preds φ := by
  induction φ generalizing σ <;> simp_all [VE.Norms.inst, VE.Norms.preds]

theorem preds_foldl_or (l : List VE.Formula) (a : VE.Formula) :
    VE.Norms.preds (l.foldl .or a) = VE.Norms.preds a ++ l.flatMap VE.Norms.preds := by
  induction l generalizing a with
  | nil => simp
  | cons b l ih => simp [List.foldl, ih, VE.Norms.preds]

theorem preds_bindAll_eq (ss : List String) (φ : VE.Formula) :
    VE.Norms.preds (VE.Norms.bindAll ss φ) = VE.Norms.preds φ := by
  induction ss with
  | nil => rfl
  | cons s ss ih => simpa [VE.Norms.bindAll, VE.Norms.preds] using ih

theorem preds_atom (p : String) (ss : List String) : ∀ x ∈ VE.Norms.preds (VE.Norms.atom p ss), x = p := by
  unfold VE.Norms.atom
  split <;> simp [VE.Norms.preds]

theorem reserved_rights (t : String) : VE.NormDefaults.Packs.reserved ("rights__" ++ t) = true := by
  have h := VE.Readings.startsWith_append_ascii "rights__" t (by decide)
  simp [VE.NormDefaults.Packs.reserved, VE.NormDefaults.Packs.reservedPrefixes, h]

theorem reserved_generated (k : Nat) :
    VE.NormDefaults.Packs.reserved (VE.Rights.limName k) = true ∧
      VE.NormDefaults.Packs.reserved (VE.Rights.condName k) = true ∧
      VE.NormDefaults.Packs.reserved (VE.Rights.aimedName k) = true := by
  refine ⟨?_, ?_, ?_⟩
  · have := reserved_rights ("lim__" ++ toString k)
    simpa [VE.Rights.limName, String.append_assoc] using this
  · have := reserved_rights ("cond__" ++ toString k)
    simpa [VE.Rights.condName, String.append_assoc] using this
  · have := reserved_rights ("bar__" ++ toString k)
    simpa [VE.Rights.aimedName, String.append_assoc] using this

theorem mem_author_holder (R : VE.Rights.RightsDoc) (H : VE.Rights.Right) (h : H ∈ R.rs) :
    H.guard ∈ rightsAuthorFormulas R := by
  unfold rightsAuthorFormulas
  exact List.mem_append_left _ (List.mem_append_left _ (List.mem_append_left _ (List.mem_map_of_mem h)))

theorem mem_author_line (R : VE.Rights.RightsDoc) (RN : String × VE.Rights.Line) (h : RN ∈ VE.Rights.linesOf R)
    (φ : VE.Formula) (hφ : φ ∈ RN.2.node.guard :: RN.2.node.carveOuts) : φ ∈ rightsAuthorFormulas R := by
  unfold rightsAuthorFormulas
  exact List.mem_append_left _ (List.mem_append_left _ (List.mem_append_right _ (List.mem_flatMap.mpr ⟨RN, h, hφ⟩)))

theorem mem_author_outside (R : VE.Rights.RightsDoc) (N : VE.SoftNorms.SoftNode) (h : N ∈ R.soft.T.nodes)
    (φ : VE.Formula) (hφ : φ ∈ N.guard :: N.carveOuts) : φ ∈ rightsAuthorFormulas R := by
  unfold rightsAuthorFormulas
  exact List.mem_append_left _ (List.mem_append_right _ (List.mem_flatMap.mpr ⟨N, h, hφ⟩))

/-- What the rights route's rules and premises name: an author formula's predicate, or a generated (reserved) one. -/
theorem correlate_covered (R : VE.Rights.RightsDoc) :
    ∀ φ ∈ (((VE.Rights.correlate R).T.nodes.map fun N => Content.rule N.toNode) ++
      (VE.Rights.limPremises R).map Content.formula).flatMap Content.formulas,
    ∀ p ∈ VE.Norms.preds φ, VE.NormDefaults.Packs.reserved p = true ∨
      ∃ ψ ∈ rightsAuthorFormulas R, p ∈ VE.Norms.preds ψ := by
  have lim : ∀ k ss p, p ∈ VE.Norms.preds (VE.Norms.atom (VE.Rights.limName k) ss) →
      VE.NormDefaults.Packs.reserved p = true := fun k ss p hp => by
    rw [preds_atom _ _ p hp]; exact (reserved_generated k).1
  have cond : ∀ k ss p, p ∈ VE.Norms.preds (VE.Norms.atom (VE.Rights.condName k) ss) →
      VE.NormDefaults.Packs.reserved p = true := fun k ss p hp => by
    rw [preds_atom _ _ p hp]; exact (reserved_generated k).2.1
  have aimed : ∀ k ss p, p ∈ VE.Norms.preds (VE.Norms.atom (VE.Rights.aimedName k) ss) →
      VE.NormDefaults.Packs.reserved p = true := fun k ss p hp => by
    rw [preds_atom _ _ p hp]; exact (reserved_generated k).2.2
  intro φ hφ p hp
  simp only [VE.Rights.correlate, List.map_append, List.map_map, List.flatMap_append, List.mem_append,
    List.mem_flatMap, List.mem_map, Function.comp] at hφ
  rcases hφ with ((⟨_, ⟨RN, hRN, rfl⟩, hφ⟩ | ⟨_, ⟨N, hN, rfl⟩, hφ⟩) | ⟨_, ⟨N, hN, rfl⟩, hφ⟩) | ⟨_, ⟨f, hf, rfl⟩, hφ⟩
  · -- a line instance's node: its own guard with the holder guard, its author carve-outs, the packed limitations
    have own : ∀ ψ ∈ RN.2.node.guard :: RN.2.node.carveOuts, p ∈ VE.Norms.preds ψ →
        VE.NormDefaults.Packs.reserved p = true ∨ ∃ ψ ∈ rightsAuthorFormulas R, p ∈ VE.Norms.preds ψ :=
      fun ψ hψ hp => .inr ⟨ψ, mem_author_line R RN hRN ψ hψ, hp⟩
    simp only [Content.formulas, VE.Rights.nodeOf, List.mem_cons, List.mem_append] at hφ
    rcases hφ with rfl | hc | hc
    · unfold VE.Rights.ownGuard VE.Rights.holderConj at hp
      split at hp
      · rename_i H hH
        split at hp
        · exact own _ (List.mem_cons_self ..) hp
        · simp only [VE.Norms.preds, List.mem_append, preds_inst] at hp
          rcases hp with hp | hp
          · exact own _ (List.mem_cons_self ..) hp
          · exact .inr ⟨H.guard, mem_author_holder R H (List.mem_of_find?_eq_some hH), hp⟩
      · exact own _ (List.mem_cons_self ..) hp
    · exact own _ (List.mem_cons_of_mem _ hc) hp
    · unfold VE.Rights.limPackList at hc
      split at hc
      · simp at hc
      · simp only [List.mem_singleton] at hc
        subst hc
        unfold VE.Rights.limPack VE.Norms.anyF at hp
        rw [preds_foldl_or] at hp
        simp only [VE.Norms.preds, List.nil_append, List.mem_flatMap, List.mem_map] at hp
        obtain ⟨_, ⟨L, _, rfl⟩, hp⟩ := hp
        exact .inl (lim _ _ p hp)
  · -- a norm unit outside rights, as written
    exact .inr ⟨φ, mem_author_outside R N hN φ hφ, hp⟩
  · -- a bar node: its generated `aimed` atom
    unfold VE.Rights.barNodes at hN
    split at hN
    · obtain ⟨m, _, rfl⟩ := List.mem_map.mp hN
      simp only [Content.formulas, VE.Rights.barNode, List.mem_singleton] at hφ
      subst hφ
      exact .inl (aimed _ _ p hp)
    · simp at hN
  · -- a premise of `Lim_D`: generated atoms under binders
    simp only [Content.formulas, List.mem_singleton] at hφ
    subst hφ
    simp only [VE.Rights.limPremises, VE.Rights.limPremisesLabelled, List.mem_map, List.mem_filterMap] at hf
    obtain ⟨⟨_, φ⟩, ⟨k, _, hk⟩, rfl⟩ := hf
    unfold VE.Rights.keyPremise at hk
    split at hk
    · simp at hk
    · split at hk
      · simp at hk
      · simp only [Option.some.injEq, Prod.mk.injEq] at hk
        obtain ⟨_, rfl⟩ := hk
        unfold VE.Rights.limPremise at hp
        rw [preds_bindAll_eq] at hp
        unfold VE.Rights.limAtom VE.Rights.condAtom at hp
        split at hp <;>
        · simp only [VE.Norms.preds, List.mem_append] at hp
          rcases hp with hp | hp
          · first | exact .inl (lim _ _ p hp) | exact .inl (cond _ _ p hp)
          · first | exact .inl (lim _ _ p hp) | exact .inl (cond _ _ p hp)

/-- A reserved predicate reaches no judgment: it is none, and names no definition. -/
theorem reserved_reaches_none (defs : List VE.Definitions.Def) (J : List String)
    (hJ : ∀ j ∈ J, VE.NormDefaults.Packs.reserved j = false)
    (hd : ∀ d ∈ defs, VE.NormDefaults.Packs.reserved d.name = false) (p j : String) (hj : j ∈ J)
    (hp : VE.NormDefaults.Packs.reserved p = true) :
    ¬ (p = j ∨ VE.Closure.Reachable .plus (fun a b => (a, b) ∈ defEdges defs) p j) := by
  rintro (rfl | hr)
  · simp [hJ p hj] at hp
  · have first : ∃ b, (p, b) ∈ defEdges defs := by
      cases hr with
      | edge h => exact ⟨_, h⟩
      | cons h _ => exact ⟨_, h⟩
    obtain ⟨b, hb⟩ := first
    obtain ⟨d, hd', rfl, _⟩ := (mem_defEdges defs _ _).mp hb
    simp [hd d hd'] at hp

/-- PC-1 (3). Every judgment the rights route's rules and limitation premises read is read by an author formula. -/
theorem correlate_judged (defs : List VE.Definitions.Def) (J : List String) (R : VE.Rights.RightsDoc)
    (hJ : ∀ j ∈ J, VE.NormDefaults.Packs.reserved j = false)
    (hd : ∀ d ∈ defs, VE.NormDefaults.Packs.reserved d.name = false) :
    ∀ j ∈ dependsOnC defs J (((VE.Rights.correlate R).T.nodes.map fun N => Content.rule N.toNode) ++
      (VE.Rights.limPremises R).map Content.formula),
    j ∈ dependsOn defs J (rightsAuthorFormulas R) := by
  intro j hj
  obtain ⟨hjJ, φ, hφ, p, hp, hr⟩ := (dependsOn_iff defs J _ j).mp hj
  rcases correlate_covered R φ hφ p hp with hres | ⟨ψ, hψ, hpψ⟩
  · exact absurd hr (reserved_reaches_none defs J hJ hd p j hjJ hres)
  · exact (dependsOn_iff defs J _ j).mpr ⟨hjJ, ψ, hψ, p, hpψ, hr⟩

/-- PC-1 (3). The scan reads names only, so one conjunction carries a block's formulas for it; it is never a claim. -/
def andAll (fs : List VE.Formula) : VE.Formula := fs.foldr .and .top
theorem preds_andAll (fs : List VE.Formula) : VE.Norms.preds (andAll fs) = fs.flatMap VE.Norms.preds := by
  induction fs with
  | nil => rfl
  | cons f fs ih => simp [andAll, VE.Norms.preds] at ih ⊢; exact ih

/-- A formula of a block as written; an absent guard is `⊤`. -/
def blockFormula : Lean.Json → Except String VE.Formula
  | .null => pure .top
  | g => VE.Bridge.decodeFormula VE.Limits.maxDepth g

/-- A rule object's author formulas: its guard and its author carve-outs (`unless`). -/
def ruleFormulas (n : Lean.Json) : Except String (List VE.Formula) := do
  let carveOuts ← match n.getObjValD "unless" with
    | .arr xs => xs.toList.mapM blockFormula
    | _ => pure []
  pure ((← blockFormula (n.getObjValD "guard")) :: carveOuts)

/-- A block's lines: each line's rules (`norm`, a power's `liberty` and `recognition`), in order. -/
def linesFormulas (block : Lean.Json) : Except String (List VE.Formula) := do
  let lines := match block.getObjValD "lines" with
    | .arr ls => ls.toList
    | _ => []
  let fs ← lines.mapM fun l => do
    let rules := ["norm", "liberty", "recognition"].filterMap fun k => (l.getObjVal? k).toOption
    return (← rules.mapM ruleFormulas).flatten
  pure fs.flatten

/-- PC-1 (3). The author formulas of one rights block, by its unit. -/
-- A right: its holder guard and its lines; added lines (`right_lines`): those lines; a limitation: its conditions,
-- as the rights route decoded them (`R.limits`, by name); a bar: none; a norm outside rights is a soft rule's unit.
def blockFormulas (R : VE.Rights.RightsDoc) (block : Lean.Json) : Except String (List VE.Formula) :=
  match block with
  | .obj kvs => match kvs.toList with
    | [("right", r)] => do pure ((← blockFormula (r.getObjValD "guard")) :: (← linesFormulas r))
    | [("right_lines", r)] => linesFormulas r
    | [("limitation", l)] =>
      pure (((R.limits.find? fun L => .str L.name == l.getObjValD "name").map fun L =>
        L.conditions.map fun c => VE.Formula.unary c.name (.var 0)).getD [])
    | [("bar", _)] => pure []
    | _ => throw "a rights block outside the rights reader"
  | _ => throw "a rights block outside the rights reader"

/-- An absent guard reads as `⊤`. -/
theorem blockFormula_null : blockFormula .null = .ok .top := rfl

/-- A rule reads its guard first, then each author carve-out (`unless`) in order. -/
theorem ruleFormulas_ok (n : Lean.Json) (g : VE.Formula) (us : Array Lean.Json) (cs : List VE.Formula)
    (hg : blockFormula (n.getObjValD "guard") = .ok g) (hu : n.getObjValD "unless" = .arr us)
    (hc : us.toList.mapM blockFormula = .ok cs) : ruleFormulas n = .ok (g :: cs) := by
  simp only [ruleFormulas, hu, hc, hg, bind, Except.bind, pure, Except.pure]

/-- A block with no lines reads none. -/
theorem linesFormulas_none (b : Lean.Json) (h : b.getObjValD "lines" = .arr #[]) : linesFormulas b = .ok [] := by
  simp [linesFormulas, h, pure, Except.pure, bind, Except.bind, List.mapM_nil]

/-- A bar reads nothing, and a limitation reads its conditions by name, as the rights route decoded them. -/
theorem blockFormulas_bar (R : VE.Rights.RightsDoc) (kvs : Std.TreeMap.Raw String Lean.Json) (b : Lean.Json)
    (h : kvs.toList = [("bar", b)]) : blockFormulas R (.obj kvs) = .ok [] := by
  simp [blockFormulas, h, pure, Except.pure]

theorem blockFormulas_limitation (R : VE.Rights.RightsDoc) (kvs : Std.TreeMap.Raw String Lean.Json) (l : Lean.Json)
    (L : VE.Rights.Limitation) (h : kvs.toList = [("limitation", l)])
    (hL : R.limits.find? (fun L => .str L.name == l.getObjValD "name") = some L) :
    blockFormulas R (.obj kvs) = .ok (L.conditions.map fun c => .unary c.name (.var 0)) := by
  simp [blockFormulas, h, hL, pure, Except.pure]

end VE.Judgments
