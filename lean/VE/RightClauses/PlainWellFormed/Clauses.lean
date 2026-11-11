import VE.RightClauses.PlainWellFormed.SoftValid

/-! What a checked structured line and a well-formed rights document give `plain_wellFormed` (8.3): each line
instance's node is its source line's norm (`mem_linesOf`); a checked entry's clauses and relation atom are typed
over the base vocabulary in the line's context (`entry_typed`); the base stratum order exists, so a base
predicate is never regulated or defined (`layer_names`, used by `baseEnv_keep` in Hyp.lean); no generated rights predicate is an author predicate
(`genDecls_fresh`). Proof vocabulary only. -/
namespace VE.RightClauses.PWF
open VE.Rights (RightsDoc SourceLine Line linesOf sourceLines)
open VE.SoftNorms (SoftNode SoftDoc)

open VE.Rights (checkBlock authorNodes beginsRightsRule beginsRightsPred genDecls rightOf checkSourceLine checkShape
  validDecider identifier)

/-- `checkRights` after its `genDecls` loop (the same statements). -/
def restRights (D : RightsDoc) : Except String Unit := do
  for M in D.rs.flatMap (fun R => R.lines.flatMap authorNodes) ++ D.soft.T.nodes do
    for m in M.over do
      if beginsRightsRule m then throw s!"UnknownSymbol: rule {m}"
  for R in D.rs do
    unless D.rights.holders.contains R.holder do throw s!"UnknownSymbol: sort {R.holder}"
    VE.Norms.typeDiagnostic D.soft.E [R.holder] R.guard
    unless R.guard.check D.soft.E [R.holder] do throw s!"InvalidInput: ill-typed right {R.name}"
    for S in R.lines do
      checkSourceLine D R S
  for RN in linesOf D do
    match rightOf D RN.1 with
    | none => throw s!"UnknownRight: {RN.1}"
    | some R =>
      checkShape D R RN.2
      if RN.2.node.carveOuts.length > 6 then throw s!"ResourceLimit: carve-outs of rule {RN.2.node.name}"
  for R in D.rs do
    unless (linesOf D).any (·.1 == R.name) do throw s!"RightWithoutIncident: {R.name}"
  for L in D.limits do
    match L.scope with
    | none => pure ()
    | some rs =>
      if rs.isEmpty then throw s!"InvalidInput: invalid scope of limitation {L.name}"
      for r in rs do
        unless (D.rs.map (·.name)).contains r do throw s!"UnknownRight: {r}"
    if L.kinds == some [] then throw s!"InvalidInput: invalid kinds of limitation {L.name}"
    if L.conditions.length > 8 then throw "ResourceLimit: conditions"
    for c in L.conditions do
      unless identifier c.name do throw s!"InvalidInput: invalid condition {c.name}"
      unless validDecider c.decidedBy do throw s!"InvalidInput: invalid decider for condition {c.name}"
    if let some c := VE.SoftNorms.dupOf (L.conditions.map (·.name)) then
      throw s!"DuplicateDeclaration: condition {c}"
    unless validDecider L.decidedBy do throw s!"InvalidInput: invalid decider for limitation {L.name}"
    if L.decidedBy.isNone then throw s!"MissingExceptionDecider: limitation {L.name}"
  if D.bars.length > 1 then throw "DuplicateDeclaration: bar"
  for b in D.bars do
    unless validDecider b.decidedBy do throw s!"InvalidInput: invalid decider for bar {b.name}"
  -- 4.1 step 3: every citation names a source unit, so no citation to a non-existent unit
  -- licenses a mechanism (4.5).
  for cs in D.rs.flatMap (fun R => R.lines.map (·.cites)) ++ D.outsideCites.map (·.2) do
    for kv in cs do
      for u in kv.2 do
        unless D.sourceUnits.contains u do throw s!"UnknownSymbol: unit {u}"

/-- `checkRights` up to its `genDecls` loop, then `k`. -/
def checkRightsK (D : RightsDoc) (k : Except String Unit) : Except String Unit := do
  checkBlock D
  if D.rs.length > 128 then throw "ResourceLimit: rights"
  if D.limits.length > 16 then throw "ResourceLimit: limitations"
  let names := D.rs.map (·.name) ++ D.limits.map (·.name) ++ D.bars.map (·.name)
  let ruleNames := (D.rs.flatMap (fun R => R.lines.flatMap authorNodes)).map (·.name) ++ D.soft.T.nodes.map (·.name)
  for n in names ++ ruleNames do
    if beginsRightsRule n then throw s!"InvalidInput: name {n} begins with rights-"
  if let some n := VE.SoftNorms.dupOf (names ++ ruleNames) then
    if (D.rs.map (·.name)).contains n then throw s!"DuplicateDeclaration: right {n}"
    else if (D.limits.map (·.name)).contains n then throw s!"DuplicateDeclaration: limitation {n}"
    else if (D.bars.map (·.name)).contains n then throw "DuplicateDeclaration: bar"
    else throw s!"DuplicateDeclaration: rule {n}"
  for p in D.soft.T.regulated.map (·.name) ++ D.soft.T.definitions.map (·.name) do
    if beginsRightsPred p then throw s!"InvalidInput: author predicate {p} begins with rights__"
  for d in genDecls D do
    if (D.soft.E.predicates d.1).isSome then throw s!"InvalidInput: author predicate {d.1} begins with rights__"
  k

theorem checkRights_eq (D : RightsDoc) : VE.Rights.checkRights D = checkRightsK D (restRights D) := rfl

theorem genDecls_fresh (X : RightsDoc) (h : VE.Rights.checkRights X = .ok ()) :
    ∀ d ∈ genDecls X, X.soft.E.predicates d.1 = none := by
  rw [checkRights_eq] at h
  generalize restRights X = k at h
  unfold checkRightsK at h
  simp only [] at h
  obtain ⟨_, -, h⟩ := bind_eq_ok.1 h
  split at h
  · simp [bind, Except.bind] at h
  obtain ⟨_, -, h⟩ := bind_eq_ok.1 h
  split at h
  · simp [bind, Except.bind] at h
  obtain ⟨_, -, h⟩ := bind_eq_ok.1 h
  obtain ⟨_, -, h⟩ := bind_eq_ok.1 h
  split at h
  · split at h
    · simp [throw, throwThe, MonadExceptOf.throw, bind, Except.bind] at h
    · split at h
      · simp [throw, throwThe, MonadExceptOf.throw, bind, Except.bind] at h
      · split at h <;> simp [throw, throwThe, MonadExceptOf.throw, bind, Except.bind] at h
  · obtain ⟨_, -, h⟩ := bind_eq_ok.1 h
    obtain ⟨_, -, h⟩ := bind_eq_ok.1 h
    obtain ⟨u, h4, -⟩ := bind_eq_ok.1 h
    cases u
    intro d hd
    have hb := (VE.NormDefaults.forIn_unit_ok _ (fun x r hx => by
      split at hx <;> simp_all [bind, Except.bind, pure, Except.pure]) (genDecls X)).1 h4 d hd
    cases hp : X.soft.E.predicates d.1 with
    | none => rfl
    | some s => simp [hp, bind, Except.bind] at hb

/-! ### The base stratum order -/

theorem nodup_of_dependencyOrder {ns : List VE.Route.DepNode} {o : List String}
    (h : VE.Route.dependencyOrder ns = .ok o) : (VE.Route.nodeNames ns).Nodup := by
  unfold VE.Route.dependencyOrder at h
  split at h
  · cases h
  · rename_i hf
    rw [List.nodup_iff_count]
    intro a
    by_cases ha : a ∈ VE.Route.nodeNames ns
    · have := List.find?_eq_none.1 hf a ha
      simp only [decide_eq_true_eq, gt_iff_lt, Nat.not_lt] at this
      exact this
    · rw [List.count_eq_zero_of_not_mem ha]; exact Nat.zero_le _

theorem depPath_mono {ns ns' : List VE.Route.DepNode}
    (h : ∀ a b, VE.Route.DepEdge ns a b → VE.Route.DepEdge ns' a b) :
    ∀ {a b}, VE.Route.DepPath ns a b → VE.Route.DepPath ns' a b
  | _, _, .edge e => .edge (h _ _ e)
  | _, _, .trans p q => .trans (depPath_mono h p) (depPath_mono h q)

/-- The base tree's stratum edges are among those of `soften C` when `C`'s nodes include the base ones. -/
theorem stratum_edge_sub (C : SoftDoc) (Tb : VE.Norms.Tree) (hr : Tb.regulated = C.T.regulated)
    (hd : Tb.definitions = C.T.definitions)
    (hn : ∀ N ∈ Tb.nodes, ∃ M ∈ C.T.nodes, M.pred = N.pred ∧ M.guard = N.guard ∧ ∀ φ ∈ N.carveOuts, φ ∈ M.carveOuts) :
    ∀ a b, VE.Route.DepEdge (VE.Norms.stratumNodes Tb) a b →
      VE.Route.DepEdge (VE.Norms.stratumNodes (VE.SoftNorms.soften C).T) a b := by
  have hnames : VE.Route.nodeNames (VE.Norms.stratumNodes Tb) =
      VE.Route.nodeNames (VE.Norms.stratumNodes (VE.SoftNorms.soften C).T) := by
    rw [nodeNames_stratum, nodeNames_stratum, hr, hd]; rfl
  rintro a b ⟨n, hn', rfl, hb⟩
  simp only [VE.Route.deps, List.mem_filter] at hb
  simp only [VE.Norms.stratumNodes, List.mem_append, List.mem_map] at hn'
  rcases hn' with ⟨r, hr', rfl⟩ | ⟨d, hd', rfl⟩
  · refine ⟨⟨r.name, ((VE.Norms.Sym.reg r).formulas (VE.SoftNorms.soften C).T).flatMap VE.Norms.preds⟩,
      by simp only [VE.Norms.stratumNodes, List.mem_append, List.mem_map]; exact Or.inl ⟨r, by show r ∈ C.T.regulated; rw [← hr]; exact hr', rfl⟩,
      rfl, ?_⟩
    simp only [VE.Route.deps, List.mem_filter, ← hnames]
    refine ⟨?_, hb.2⟩
    obtain ⟨φ, hφ, hbφ⟩ := List.mem_flatMap.1 hb.1
    simp only [VE.Norms.Sym.formulas, VE.Norms.rulesOn, List.mem_flatMap, List.mem_filter, beq_iff_eq] at hφ
    obtain ⟨N, ⟨hN, hp⟩, hφN⟩ := hφ
    obtain ⟨M, hM, hMp, hMg, hMc⟩ := hn N hN
    refine List.mem_flatMap.2 ⟨φ, ?_, hbφ⟩
    simp only [VE.Norms.Sym.formulas, VE.Norms.rulesOn, List.mem_flatMap, List.mem_filter, beq_iff_eq]
    refine ⟨VE.SoftNorms.primeNode C M, ⟨by simp [VE.SoftNorms.soften]; exact ⟨M, hM, rfl⟩, by simp [VE.SoftNorms.primeNode, hMp, hp]⟩, ?_⟩
    rcases List.mem_cons.1 hφN with rfl | hc
    · simp [VE.SoftNorms.primeNode, hMg]
    · simp [VE.SoftNorms.primeNode, hMc φ hc]
  · refine ⟨⟨d.name, VE.Norms.preds d.body⟩,
      by simp only [VE.Norms.stratumNodes, List.mem_append, List.mem_map]; exact Or.inr ⟨d, by show d ∈ C.T.definitions; rw [← hd]; exact hd', rfl⟩,
      rfl, ?_⟩
    simp only [VE.Route.deps, List.mem_filter, ← hnames]
    exact hb

theorem layer_names (C : SoftDoc) (Tb : VE.Norms.Tree) (hr : Tb.regulated = C.T.regulated)
    (hd : Tb.definitions = C.T.definitions)
    (hn : ∀ N ∈ Tb.nodes, ∃ M ∈ C.T.nodes, M.pred = N.pred ∧ M.guard = N.guard ∧ ∀ φ ∈ N.carveOuts, φ ∈ M.carveOuts)
    (hsem : VE.Norms.semanticCheck (VE.SoftNorms.soften C) = true) :
    ∀ n, keepOf Tb.regulated Tb.definitions n = true → n ∈ VE.Norms.layerNames Tb := by
  have hso : (VE.Route.dependencyOrder (VE.Norms.stratumNodes (VE.SoftNorms.soften C).T)).isOk = true := by
    simp only [VE.Norms.semanticCheck, Bool.and_eq_true, and_assoc] at hsem; exact hsem.2.1
  obtain ⟨o, ho⟩ : ∃ o, VE.Route.dependencyOrder (VE.Norms.stratumNodes (VE.SoftNorms.soften C).T) = .ok o := by
    revert hso; cases VE.Route.dependencyOrder (VE.Norms.stratumNodes (VE.SoftNorms.soften C).T) <;> simp [Except.isOk, Except.toBool]
  have hnames : VE.Route.nodeNames (VE.Norms.stratumNodes Tb) =
      VE.Route.nodeNames (VE.Norms.stratumNodes (VE.SoftNorms.soften C).T) := by
    rw [nodeNames_stratum, nodeNames_stratum, hr, hd]; rfl
  have hacb : VE.Route.DagAcyclic (VE.Norms.stratumNodes Tb) := fun a hp =>
    (VE.Route.dag_acyclic _ _ ho).2.2.2 a (depPath_mono (stratum_edge_sub C Tb hr hd hn) hp)
  obtain ⟨ob, hob⟩ := VE.NormDefaults.dependencyOrder_ok _ (by rw [hnames]; exact nodup_of_dependencyOrder ho) hacb
  have hmem := (VE.Route.dag_acyclic _ _ hob).2.1
  intro n hk
  have hn' : n ∈ ob := (hmem n).2 (by rw [nodeNames_stratum]; simpa [keepOf] using hk)
  have hord : VE.Norms.order Tb = ob := by simp [VE.Norms.order, hob]
  simp only [VE.Norms.layerNames, VE.Norms.syms, hord, List.mem_map, List.mem_filterMap]
  simp only [keepOf, List.contains_iff_mem, List.mem_append, List.mem_map] at hk
  unfold VE.Norms.lookupSym
  cases hf : Tb.regulated.find? (·.name == n) with
  | some r => exact ⟨.reg r, ⟨n, hn', by rw [hf]⟩, by simpa using List.find?_some hf⟩
  | none =>
    rcases hk with ⟨r, hr', rfl⟩ | ⟨d, hd', rfl⟩
    · exact absurd (List.find?_eq_none.1 hf r hr') (by simp)
    · obtain ⟨d', hd''⟩ : ∃ d', Tb.definitions.find? (·.name == d.name) = some d' := by
        cases h' : Tb.definitions.find? (·.name == d.name) with
        | none => exact absurd (List.find?_eq_none.1 h' d hd') (by simp)
        | some d' => exact ⟨d', rfl⟩
      exact ⟨.defn d', ⟨d.name, hn', by rw [hf, hd'']; rfl⟩, by simpa using List.find?_some hd''⟩

/-! ### A checked entry is typed over the base vocabulary -/

theorem relAtom_check {B : VE.Environment} {Rt : VE.Rights.Right} {hs : Option Nat} {ss : List String}
    {rel : Relation} (h : relationOk B Rt hs ss rel = true) :
    (relAtom ss.length rel).check B ss.reverse = true := by
  simp only [relationOk, Bool.and_eq_true, bne_iff_ne, ne_eq, decide_eq_true_eq, beq_iff_eq] at h
  obtain ⟨⟨⟨⟨⟨-, h1⟩, h2⟩, hp⟩, -⟩, -⟩ := h
  have g : ∀ j, j < ss.length → (VE.Term.var (ss.length - 1 - j)).sortOf B ss.reverse = some (ss.getD j "") := by
    intro j hj
    simp only [VE.Term.sortOf, List.getElem?_reverse (by omega : ss.length - 1 - j < ss.length),
      show ss.length - 1 - (ss.length - 1 - j) = j by omega, List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hj,
      Option.getD_some]
  simp [relAtom, VE.Formula.check, hp, g _ h1, g _ h2]

theorem entry_typed (D : ClauseDoc) (h : WellFormedClauses D = true) (x : String × String × CLine)
    (hx : x ∈ D.lines) :
    (∀ c ∈ x.2.2.clauses, c.formula.check (baseEnv D) (lineSorts D.doc.soft x.2.2.line).reverse = true) ∧
    (∀ rel, x.2.2.relation = some rel →
      (relAtom (lineSorts D.doc.soft x.2.2.line).length rel).check (baseEnv D)
        (lineSorts D.doc.soft x.2.2.line).reverse = true) := by
  have hc : checkClauses D = .ok () := by
    unfold WellFormedClauses at h; split at h <;> simp_all
  have he := forM_ok _ _ hc x hx
  unfold checkEntry at he
  split at he
  · rename_i Rt _
    split at he
    · cases he
    split at he
    · cases he
    obtain ⟨R, n, L⟩ := x
    unfold checkBody at he
    obtain ⟨u1, h1, he⟩ := bind_eq_ok.1 he
    obtain ⟨u2, -, he⟩ := bind_eq_ok.1 he
    cases u1
    have hl1 := (VE.NormDefaults.forIn_unit_ok _ (fun x r hx => by
      simp only [bind, Except.bind, pure, Except.pure] at hx
      split at hx <;> cases hx <;> rfl) _).1 h1
    refine ⟨fun c hc => ?_, fun rel hrel => ?_⟩
    · obtain ⟨⟨c', i⟩, hci, rfl⟩ : ∃ p ∈ L.clauses.zipIdx, p.1 = c := by
        have : c ∈ L.clauses.zipIdx.map Prod.fst := by simp; exact hc
        exact List.mem_map.1 this
      have := hl1 _ hci
      revert this
      split <;> simp_all [bind, Except.bind, pure, Except.pure]
    · obtain ⟨u3, h3, -⟩ := bind_eq_ok.1 he
      cases u3
      have hl2 := (VE.NormDefaults.forIn_unit_ok _ (fun x r hx => by
        simp only [bind, Except.bind, pure, Except.pure] at hx
        split at hx
        · split at hx <;> cases hx <;> rfl
        · cases hx) _).1 h3 rel (by simp only at hrel; simp [hrel])
      simp only [bind, Except.bind, pure, Except.pure] at hl2
      split at hl2
      · rename_i hro; exact relAtom_check hro
      · cases hl2
  · cases he

end VE.RightClauses.PWF
