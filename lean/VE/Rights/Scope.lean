import VE.Rights.Bar

/-! `Narrows`, licensing and the audit `limitationScope` (docs/spec/rights.md 4.5, 9.2).

A narrowing mechanism of a line instance `N` is any way `N` can fail to select where its
own guard holds; `narrowings D N` (in `Correlate.lean`) lists them syntactically from
`T″′`, and `narrowings_complete` proves the list complete: where the own guard holds and
the line does not select, some listed mechanism is active (`NarrowsAt`).

A mechanism is licensed by the limitation itself (`limPack`), by the bar (`bar`, Art. 30),
by a citation (`cited`), as a collision with another right's line of the opposite effect
(`rightCollision`), as same-effect strict blocking (`sameEffectStrict`), or by an accepted
certificate for the target `∀x̄. cond_n° → limpack_N` over `Background_base″`
(`certified`). The audit lists every unlicensed mechanism of a line in scope of some
limitation as a finding; `limitation_scope_sound` is what "no finding" means.

Carve-out indices are 0-based here and rendered 1-based (`carve-out 1`, citation key
`unless:1`), as the spec numbers `U_1`. -/
namespace VE.Rights
open VE.Norms (tupleVal atom bindAll anyF envAt size)
open VE.SoftNorms (SoftNode SoftDoc LiveD StrictSelectsD StrictDecidesD BlockedD EligibleD DomWithD EffD
  AppliesSoftD YieldsSoftD SelectsSoftD OutweighsD childrenIn dualPerm dualOblig Incompatible Comparable
  higher act rk rankFuel soften)
universe u

/-! ## Activity of a mechanism -/

/-- The body of soft's `DomWithD` for one opponent `M`. -/
def DomOneD (C : SoftDoc) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (eff : SoftNode → Prop) (M X : SoftNode) : Prop :=
  (higher C M X = true ∧ eff M ∧ (C.soft.outranking = .holistic → ¬ OutweighsD C S ρ (act C X) (rk X) (rk M))) ∨
  (C.soft.outranking = .holistic ∧ higher C X M = true ∧ EligibleD C S ρ M ∧ OutweighsD C S ρ (act C X) (rk M) (rk X))

/-- The mechanism is active at `ρ` (a full structure). -/
def NarrowsAt (D : RightsDoc) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (N : Line) : Narrowing → Prop
  | .carveOut i => i < N.node.carveOuts.length ∧ (N.node.carveOuts[i]?.getD .bottom).denote S ρ
  | .exception M => ∃ M', nodeNamed D M = some M' ∧ YieldsSoftD (correlate D) S ρ (VE.SoftNorms.fuel (correlate D)) M'
  | .limPack => (limPack D N).denote S ρ
  | .excepted => N.node.mode = .default ∧ (VE.SoftNorms.exceptedF (correlate D) (nodeOf D N)).denote S ρ
  | .switch π => π ∈ N.node.alterable ∧
      (atom (VE.SoftNorms.offName (nodeOf D N) π) (VE.SoftNorms.sortsOf (correlate D) N.node.pred)).denote S ρ
  | .blockedBy M => ∃ M', nodeNamed D M = some M' ∧ StrictSelectsD (correlate D) S ρ (VE.SoftNorms.fuel (correlate D)) M'
  | .dominatedBy M => ∃ M', nodeNamed D M = some M' ∧
      DomOneD (correlate D) S ρ (EffD (correlate D) S ρ (correlate D).soft.ranks.length) M' (nodeOf D N)
  | .bar => ruleReading D = true ∧ ∃ m, barReach D N = some m ∧ (aimedF D m).denote S ρ

/-! ## Licences -/

structure Finding where
  code : String
  rule : String
  right : String
  span : String
  text : String
  deriving DecidableEq, Repr

/-- A non-empty citation under key `k`. -/
def hasKey (cs : List (String × List String)) (k : String) : Bool := cs.any (fun e => e.1 == k && !e.2.isEmpty)

/-- The citations of the rule of `T″` named `n`: a line's source citations, or an outside rule's. -/
def citesOf (D : RightsDoc) (n : String) : List (String × List String) :=
  match (linesOf D).find? (fun RN => (nodeOf D RN.2).name == n) with
  | some RN => RN.2.source.cites
  | none => ((D.outsideCites.find? (·.1 == n)).map (·.2)).getD []

/-- The names a `narrows:<line>` citation may use: the instance's rule and its source norm. -/
def lineKeys (N : Line) : List String := N.node.name :: (N.source.norm.map (·.name)).toList

def citesNarrows (D : RightsDoc) (M : String) (N : Line) : Bool :=
  (lineKeys N).any (fun k => hasKey (citesOf D M) s!"narrows:{k}")

def cited (D : RightsDoc) (N : Line) : Narrowing → Bool
  | .carveOut i => hasKey N.source.cites s!"unless:{i + 1}"
  | .exception M => (lineKeys N).any (fun k => hasKey (citesOf D M) s!"over:{k}") || citesNarrows D M N
  | .limPack => true
  | .excepted => hasKey N.source.cites "exception"
  | .switch π => hasKey N.source.cites s!"alterable:{π}"
  | .blockedBy M => citesNarrows D M N
  | .dominatedBy M => hasKey N.source.cites "rank" || citesNarrows D M N
  | .bar => true

/-- Blocked or dominated by a right-derived line of the opposite effect. -/
def rightCollision (D : RightsDoc) (N : Line) : Narrowing → Bool
  | .blockedBy M | .dominatedBy M =>
    match nodeNamed D M with
    | some M' => (lineNodes D).contains M' && Incompatible (correlate D) M' (nodeOf D N)
    | none => false
  | _ => false

/-- `N` default; `M ≠ bar_m` a strict rule of `T″` on `N`'s predicate with `N`'s sign. -/
def sameEffectStrict (D : RightsDoc) (N : Line) (M : String) : Bool :=
  N.node.mode == .default &&
    match nodeNamed D M with
    | some M' => M'.mode == .strict && M'.pred == N.node.pred && M'.sign == N.node.sign
    | none => false

/-- The certification target `∀x̄. cond_n° → limpack_N`. -/
def certTarget (D : RightsDoc) (N : Line) (n : Narrowing) : VE.Formula :=
  bindAll (sortsOf D N) (.implies (outcomeSubst D (condF D N n)) (limPack D N))

def certified (D : RightsDoc) (certs : List (Option VE.Tableau.Certificate)) (N : Line) (n : Narrowing) : Bool :=
  certs.any (fun c => match c with
    | some c => VE.Tableau.checkCertificate (envAt (soften (correlate D)) 0) (backgroundBaseR D) (certTarget D N n) c
    | none => false)

def licensed (D : RightsDoc) (certs : List (Option VE.Tableau.Certificate)) (N : Line) : Narrowing → Bool
  | .limPack => true
  | .bar => true
  | .blockedBy M => cited D N (.blockedBy M) || rightCollision D N (.blockedBy M) || sameEffectStrict D N M ||
      certified D certs N (.blockedBy M)
  | n => cited D N n || rightCollision D N n || certified D certs N n

def mechText : Narrowing → String
  | .carveOut i => s!"carve-out {i + 1}"
  | .exception M => s!"exception {M}"
  | .limPack => "limitation"
  | .excepted => "exception"
  | .switch π => s!"switch {π}"
  | .blockedBy M => s!"blockedBy {M}"
  | .dominatedBy M => s!"dominatedBy {M}"
  | .bar => "bar"

/-- The audit: every unlicensed mechanism of a line in scope of some limitation. -/
def limitationScope (D : RightsDoc) (certs : List (Option VE.Tableau.Certificate)) : List Finding :=
  (linesOf D).flatMap (fun RN =>
    if D.limits.any (fun L => inScope D L RN.1 RN.2) then
      (narrowings D RN.2).filterMap (fun n =>
        if licensed D certs RN.2 n then none
        else some ⟨"UnlicensedLimitation", RN.2.node.name, RN.1, "",
          s!"UnlicensedLimitation: {mechText n} of rule {RN.2.node.name} on right {RN.1}"⟩)
    else [])

theorem licensed_of_scope {D : RightsDoc} {certs : List (Option VE.Tableau.Certificate)}
    (hc : limitationScope D certs = []) {L : Limitation} (hL : L ∈ D.limits) {R : String} {N : Line}
    (hN : (R, N) ∈ linesOf D) (hs : inScope D L R N = true) {n : Narrowing} (hn : n ∈ narrowings D N) :
    licensed D certs N n = true := by
  have h1 := List.flatMap_eq_nil_iff.mp hc (R, N) hN
  have hany : D.limits.any (fun L => inScope D L R N) = true := List.any_eq_true.mpr ⟨L, hL, hs⟩
  simp only [hany, if_true] at h1
  have h2 := List.filterMap_eq_nil_iff.mp h1 n hn
  cases hl : licensed D certs N n
  · rw [hl] at h2; simp at h2
  · rfl

theorem licensed_cases {D : RightsDoc} {certs : List (Option VE.Tableau.Certificate)} {N : Line} {n : Narrowing}
    (h : licensed D certs N n = true) :
    n = .limPack ∨ n = .bar ∨ cited D N n = true ∨ rightCollision D N n = true ∨
      (∃ M, n = .blockedBy M ∧ sameEffectStrict D N M = true) ∨ certified D certs N n = true := by
  cases n with
  | limPack => exact Or.inl rfl
  | bar => exact Or.inr (Or.inl rfl)
  | blockedBy M =>
    simp only [licensed, Bool.or_eq_true] at h
    rcases h with ((h | h) | h) | h
    · exact Or.inr (Or.inr (Or.inl h))
    · exact Or.inr (Or.inr (Or.inr (Or.inl h)))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inl ⟨M, rfl, h⟩))))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr h))))
  | carveOut _ | exception _ | excepted | switch _ | dominatedBy _ =>
    simp only [licensed, Bool.or_eq_true] at h
    rcases h with (h | h) | h
    · exact Or.inr (Or.inr (Or.inl h))
    · exact Or.inr (Or.inr (Or.inr (Or.inl h)))
    · exact Or.inr (Or.inr (Or.inr (Or.inr (Or.inr h))))

/-! ## The inventory is complete -/

section Inventory
variable {D : RightsDoc} (hv : RightsValid D)
include hv

theorem direct_names_nodup : ((directNodes D).map (·.name)).Nodup := by
  have hn := (VE.SoftNorms.softValid_of_wellFormed _ hv.wfSoft).names
  have : (correlate D).T.nodes = directNodes D ++ barNodes D := rfl
  rw [this, List.map_append] at hn
  exact (List.nodup_append.mp hn).1

theorem nodeNamed_self {X : SoftNode} (hX : X ∈ directNodes D) : nodeNamed D X.name = some X :=
  VE.SoftNorms.find_key (fun N : SoftNode => N.name) _ (direct_names_nodup hv) X hX

omit hv in
theorem nodeNamed_mem {M : String} {M' : SoftNode} (h : nodeNamed D M = some M') : M' ∈ directNodes D :=
  List.mem_of_find?_eq_some h

end Inventory

section Members
variable (D : RightsDoc) (N : Line)

theorem mem_narrowings_carveOut {i : Nat} (hi : i < N.node.carveOuts.length) : Narrowing.carveOut i ∈ narrowings D N := by
  simp only [narrowings, List.mem_append]
  exact Or.inl (Or.inl (Or.inl (Or.inl (Or.inl (Or.inl (Or.inl (List.mem_map.mpr ⟨i, List.mem_range.mpr hi, rfl⟩)))))))

theorem mem_narrowings_exception {M : SoftNode} (hM : M ∈ childrenIn (directNodes D) (nodeOf D N)) :
    Narrowing.exception M.name ∈ narrowings D N := by
  simp only [narrowings, List.mem_append]
  exact Or.inl (Or.inl (Or.inl (Or.inl (Or.inl (Or.inl (Or.inr (List.mem_map.mpr ⟨M, hM, rfl⟩)))))))

theorem mem_narrowings_limPack (h : limPackList D N ≠ []) : Narrowing.limPack ∈ narrowings D N := by
  simp only [narrowings, List.mem_append, h, if_false]
  exact Or.inl (Or.inl (Or.inl (Or.inl (Or.inl (Or.inr List.mem_cons_self)))))

theorem mem_narrowings_excepted (h : N.node.mode = .default) : Narrowing.excepted ∈ narrowings D N := by
  simp only [narrowings, List.mem_append, h, if_true]
  exact Or.inl (Or.inl (Or.inl (Or.inl (Or.inr List.mem_cons_self))))

theorem mem_narrowings_switch {π : String} (h : π ∈ N.node.alterable) : Narrowing.switch π ∈ narrowings D N := by
  simp only [narrowings, List.mem_append]
  exact Or.inl (Or.inl (Or.inl (Or.inr (List.mem_map.mpr ⟨π, h, rfl⟩))))

theorem mem_narrowings_blockedBy (hd : N.node.mode = .default) {M : SoftNode} (hM : M ∈ directNodes D)
    (hs : M.mode = .strict) (hb : blocksOn (correlate D) (nodeOf D N) M = true) :
    Narrowing.blockedBy M.name ∈ narrowings D N := by
  simp only [narrowings, List.mem_append, hd, if_true]
  refine Or.inl (Or.inl (Or.inr (List.mem_map.mpr ⟨M, List.mem_filter.mpr ⟨hM, ?_⟩, rfl⟩)))
  simp [hs, hb]

theorem mem_narrowings_dominatedBy (hd : N.node.mode = .default) {M : SoftNode} (hM : M ∈ directNodes D)
    (hMd : M.mode = .default) (hi : Incompatible (correlate D) M (nodeOf D N) = true)
    (hc : Comparable (correlate D) M (nodeOf D N) = true) :
    Narrowing.dominatedBy M.name ∈ narrowings D N := by
  simp only [narrowings, List.mem_append, hd, if_true]
  refine Or.inl (Or.inr (List.mem_map.mpr ⟨M, List.mem_filter.mpr ⟨hM, ?_⟩, rfl⟩))
  simp [hMd, hi, hc]

theorem mem_narrowings_bar (hr : ruleReading D = true) {m : String} (h : barReach D N = some m) :
    Narrowing.bar ∈ narrowings D N := by
  simp only [narrowings, List.mem_append, h, hr, Option.isSome_some, Bool.and_self, if_true]
  exact Or.inr List.mem_cons_self

end Members

section Complete
variable {D : RightsDoc} (hv : RightsValid D) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (N : Line)
include hv

omit hv in
/-- A failed live with the own guard holding: a carve-out, the pack, a switch or the exception. -/
theorem live_fail (hown : (ownGuard D N).denote S ρ) (hl : ¬ LiveD (correlate D) S ρ (nodeOf D N)) :
    ∃ n ∈ narrowings D N, NarrowsAt D S ρ N n := by
  classical
  unfold LiveD at hl
  have hg : (nodeOf D N).guard.denote S ρ := hown
  by_cases hc : ∃ U ∈ (nodeOf D N).carveOuts, U.denote S ρ
  · obtain ⟨U, hU, hd⟩ := hc
    rcases List.mem_append.mp hU with hU | hU
    · obtain ⟨i, hi⟩ := List.mem_iff_getElem?.mp hU
      have hlt : i < N.node.carveOuts.length := (List.getElem?_eq_some_iff.mp hi).1
      refine ⟨.carveOut i, mem_narrowings_carveOut D N hlt, hlt, ?_⟩
      rw [hi]; exact hd
    · have hne : limPackList D N ≠ [] := fun he => by rw [he] at hU; cases hU
      refine ⟨.limPack, mem_narrowings_limPack D N hne, ?_⟩
      exact (limPackList_denote D N S ρ).mp ⟨U, hU, hd⟩
  · by_cases hs : (VE.SoftNorms.switchF (correlate D) (nodeOf D N)).denote S ρ
    · simp only [VE.SoftNorms.switchF, VE.SoftNorms.switchIn, VE.Norms.anyF_denote, List.mem_map] at hs
      obtain ⟨_, ⟨π, hπ, rfl⟩, hd⟩ := hs
      exact ⟨.switch π, mem_narrowings_switch D N hπ, hπ, hd⟩
    · have he : (nodeOf D N).mode = .default ∧ (VE.SoftNorms.exceptedF (correlate D) (nodeOf D N)).denote S ρ := by
        by_cases hd : (nodeOf D N).mode = .default
        · exact ⟨hd, Classical.byContradiction fun hx => hl ⟨hg, hc, hs, fun _ => hx⟩⟩
        · exact absurd ⟨hg, hc, hs, fun h => absurd h hd⟩ hl
      exact ⟨.excepted, mem_narrowings_excepted D N he.1, he.1, he.2⟩

/-- 4.5: not selecting where the own guard holds means some listed mechanism is active. -/
theorem narrowings_complete_of_valid (hown : (ownGuard D N).denote S ρ) (hns : ¬ SelectsRN D S ρ N) :
    ∃ n ∈ narrowings D N, NarrowsAt D S ρ N n := by
  classical
  have hsv := VE.SoftNorms.softValid_of_wellFormed _ hv.wfSoft
  unfold SelectsRN SelectsSoftD at hns
  by_cases hch : ∃ C' ∈ VE.SoftNorms.children (correlate D) (nodeOf D N),
      YieldsSoftD (correlate D) S ρ (VE.SoftNorms.fuel (correlate D)) C'
  · obtain ⟨C', hC, hy⟩ := hch
    rcases (mem_children_correlate D _ C').mp hC with hC | ⟨hB, hp, _⟩
    · have hCd := mem_childrenIn_direct D hC
      exact ⟨.exception C'.name, mem_narrowings_exception D N hC, C', nodeNamed_self hv hCd, hy⟩
    · obtain ⟨hr, m, hm, rfl⟩ := (mem_barNodes D _).mp hB
      simp only [barNode] at hp
      have hm' : rightPermission D N.node.pred = true := by rw [← show m = N.node.pred from hp]; exact hm
      have hreach : barReach D N = some N.node.pred := by simp [barReach, hm']
      have ha := (yields_bar hv S ρ hB _).mp hy
      simp only [barNode] at ha
      rw [show m = N.node.pred from hp] at ha
      exact ⟨.bar, mem_narrowings_bar D N hr hreach, hr, N.node.pred, hreach, ha⟩
  · have hna : ¬ AppliesSoftD (correlate D) S ρ (nodeOf D N) := fun ha => hns ⟨ha, hch⟩
    have hmode : (nodeOf D N).mode = N.node.mode := rfl
    unfold AppliesSoftD at hna
    cases hm : N.node.mode with
    | strict =>
      rw [hmode, hm] at hna
      exact live_fail S ρ N hown hna
    | default =>
      rw [hmode, hm] at hna
      simp only [rankFuel, EffD] at hna
      by_cases hel : EligibleD (correlate D) S ρ (nodeOf D N)
      · have hdom := Classical.byContradiction fun h => hna ⟨hel, h⟩
        obtain ⟨M, hM, hi, hMd, hc, hbody⟩ := hdom
        have hMdir : M ∈ directNodes D := by
          rcases (mem_correlate_nodes D M).mp hM with h | h
          · exact h
          · rw [bar_mode D h] at hMd; cases hMd
        exact ⟨.dominatedBy M.name, mem_narrowings_dominatedBy D N hm hMdir hMd hi hc, M,
          nodeNamed_self hv hMdir, hbody⟩
      · unfold EligibleD at hel
        by_cases hl : LiveD (correlate D) S ρ (nodeOf D N)
        · have hblk : BlockedD (correlate D) S ρ (nodeOf D N) :=
            Classical.byContradiction fun hb => hel ⟨by rw [hmode, hm], hl, hb⟩
          -- a strict witness on the predicate or across the pair
          have key : ∀ q s, StrictDecidesD (correlate D) S ρ q s →
              (∀ M ∈ directNodes D, M.pred = q → M.sign = s → blocksOn (correlate D) (nodeOf D N) M = true) →
              (s = false → rightPermission D q = true → barReach D N = some q) →
              ∃ n ∈ narrowings D N, NarrowsAt D S ρ N n := by
            intro q s ⟨M, hMq, hMs, hsel⟩ hbl hbar
            obtain ⟨hMc, hMp⟩ := VE.SoftNorms.mem_rulesOn.mp hMq
            rcases (mem_correlate_nodes D M).mp hMc with hMd | hMb
            · exact ⟨.blockedBy M.name, mem_narrowings_blockedBy D N hm hMd hsel.1 (hbl M hMd hMp hMs),
                M, nodeNamed_self hv hMd, hsel⟩
            · obtain ⟨hr, m, hmp, rfl⟩ := (mem_barNodes D _).mp hMb
              simp only [barNode] at hMp hMs
              subst hMp
              have hreach := hbar hMs.symm hmp
              have ha := (strictSelects_bar hv S ρ hMb _).mp hsel
              exact ⟨.bar, mem_narrowings_bar D N hr hreach, hr, _, hreach, ha⟩
          have hX : (nodeOf D N).pred = N.node.pred := rfl
          have hXs : (nodeOf D N).sign = N.node.sign := rfl
          rcases hblk with hb | hb | ⟨hsg, m, hdm, hb⟩ | ⟨hsg, r, hdr, hb⟩
          · exact key _ true hb (fun M _ hp _ => by simp [blocksOn, hp]) (fun h => by cases h)
          · refine key _ false hb (fun M _ hp _ => by simp [blocksOn, hp]) (fun _ hrp => ?_)
            show barReach D N = some N.node.pred
            simp [barReach, show rightPermission D N.node.pred = true from hrp]
          · refine key _ false hb (fun M _ hp hs => by simp [blocksOn, hsg, hdm, hp, hs]) (fun _ hrp => ?_)
            have hno : rightPermission D N.node.pred = false := by
              cases hq : rightPermission D N.node.pred
              · rfl
              · have := hv.permNoDual _ hq
                rw [hX] at hdm
                rw [this] at hdm
                cases hdm
            rw [hX] at hdm
            simp [barReach, hno, hm, hXs ▸ hsg, hdm, hrp]
          · exact key _ true hb (fun M _ hp hs => by simp [blocksOn, hsg, hdr, hp, hs]) (fun h => by cases h)
        · exact live_fail S ρ N hown hl

end Complete

theorem narrowings_complete (D : RightsDoc) (h : WellFormedRights D = true) (N : Line)
    (_hN : N ∈ (linesOf D).map (·.2)) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (hown : (ownGuard D N).denote S ρ) (hns : ¬ SelectsRN D S ρ N) :
    ∃ n ∈ narrowings D N, NarrowsAt D S ρ N n :=
  narrowings_complete_of_valid (rightsValid_of_wellFormed D h) S ρ N hown hns

/-! ## Active mechanisms satisfy their conditions -/

theorem domOne_denote (C : SoftDoc) (S : VE.Structure.{u}) (ρ : VE.Valuation S) (eff : SoftNode → VE.Formula)
    (effP : SoftNode → Prop) (he : ∀ M, (eff M).denote S ρ ↔ effP M) (M X : SoftNode) :
    (domOneF C eff M X).denote S ρ ↔ DomOneD C S ρ effP M X := by
  unfold domOneF DomOneD
  simp only [VE.Formula.denote]
  apply or_congr
  · by_cases hh : higher C M X = true
    · simp only [hh, if_true, VE.Formula.denote, he, true_and]
      apply and_congr_right
      intro _
      by_cases hol : C.soft.outranking = .holistic
      · simp [hol, VE.Formula.denote, VE.SoftNorms.outweighs_denote]
      · simp [hol, VE.Formula.denote]
    · simp [hh, VE.Formula.denote]
  · by_cases hh : C.soft.outranking = .holistic ∧ higher C X M = true
    · simp only [hh, and_self, if_true, VE.Formula.denote, VE.SoftNorms.eligible_denote,
        VE.SoftNorms.outweighs_denote, true_and]
    · simp only [hh, if_false, VE.Formula.denote, false_iff]
      rintro ⟨h1, h2, _⟩
      exact hh ⟨h1, h2⟩

theorem condF_of_narrowsAt {D : RightsDoc} (hv : RightsValid D) (S : VE.Structure.{u}) (ρ : VE.Valuation S)
    (N : Line) (hown : (ownGuard D N).denote S ρ) (n : Narrowing) (hact : NarrowsAt D S ρ N n) :
    (condF D N n).denote S ρ := by
  have hsv := VE.SoftNorms.softValid_of_wellFormed _ hv.wfSoft
  cases n with
  | carveOut i => exact ⟨hown, hact.2⟩
  | exception M =>
    obtain ⟨M', hM', hy⟩ := hact
    simp only [condF, hM']
    rw [VE.Norms.yields_denote, VE.SoftNorms.fuel_soften, VE.SoftNorms.yieldsD_prime]
    exact hy
  | limPack => exact hact
  | excepted => exact hact.2
  | switch π => exact hact.2
  | blockedBy M =>
    obtain ⟨M', hM', hsel⟩ := hact
    simp only [condF, hM']
    rw [VE.SoftNorms.selectsPrime_denote]
    have hMc : M' ∈ (correlate D).T.nodes := (mem_correlate_nodes D _).mpr (Or.inl (nodeNamed_mem hM'))
    exact (VE.SoftNorms.selects_strict hsv _ M' hMc hsel.1).mpr hsel
  | dominatedBy M =>
    obtain ⟨M', hM', hd⟩ := hact
    simp only [condF, hM']
    exact (domOne_denote _ S ρ _ _ (fun M => VE.SoftNorms.eff_denote _ S ρ _ M) M' _).mpr hd
  | bar =>
    obtain ⟨_, m, hm, ha⟩ := hact
    simp only [condF, hm]
    exact ha

/-! ## Soundness -/

/-- The certified case: an accepted certificate for `cond_n° → limpack_N` over `Background_base″`. -/
theorem licensed_certified_sound (D : RightsDoc) (_h : WellFormedRights D = true) (N : Line) (n : Narrowing)
    (c : VE.Tableau.Certificate)
    (acc : VE.Tableau.checkCertificate (envAt (soften (correlate D)) 0) (backgroundBaseR D)
             (bindAll (sortsOf D N) (.implies (outcomeSubst D (condF D N n)) (limPack D N))) c = true)
    (B : VE.Structure.{u}) (hB : BaseAdmissibleR D B) (vs : List B.Carrier) (typed : VE.TupleTyped B (sortsOf D N) vs)
    (hact : (outcomeSubst D (condF D N n)).denote B (tupleVal vs)) :
    (limPack D N).denote B (tupleVal vs) := by
  have hbg : ∀ a ∈ backgroundBaseR D, a.denote B [] := by
    intro a ha
    rcases List.mem_append.mp ha with ha | ha
    · exact VE.SoftNorms.sat_backgroundBasePrime hB.1 a ha
    · exact hB.2 a ha
  have he := VE.Tableau.checkCertificate_sound.{u} _ _ _ c acc B hB.1.1.1 hbg
  exact (VE.Norms.bindAll_denote_nil B _ _).mp he vs typed hact

/-- 4.5: with no finding, a line in scope gives way only where some limitation covering it holds
(the pack), a cited mechanism is active, another right's line collides, a strict rule of its own
effect selects, or the bar applies, on the line's own permission predicate or across the dual pair. -/
theorem limitation_scope_sound (D : RightsDoc) (h : WellFormedRights D = true)
    (certs : List (Option VE.Tableau.Certificate)) (hc : limitationScope D certs = [])
    (L : Limitation) (hL : L ∈ D.limits) (R : String) (N : Line) (hN : (R, N) ∈ linesOf D)
    (hs : inScope D L R N = true) (B : VE.Structure.{u}) (hB : BaseAdmissibleR D B)
    (vs : List B.Carrier) (typed : VE.TupleTyped B (sortsOf D N) vs)
    (hown : (outcomeSubst D (ownGuard D N)).denote B (tupleVal vs))
    (hns : ¬ (outcomeSubst D (selectsR D N)).denote B (tupleVal vs)) :
    (limPack D N).denote B (tupleVal vs)
    ∨ (∃ n ∈ narrowings D N, cited D N n = true ∧ (outcomeSubst D (condF D N n)).denote B (tupleVal vs))
    ∨ (∃ n ∈ narrowings D N, rightCollision D N n = true ∧ (outcomeSubst D (condF D N n)).denote B (tupleVal vs))
    ∨ (∃ M, sameEffectStrict D N M = true ∧ (outcomeSubst D (condF D N (.blockedBy M))).denote B (tupleVal vs))
    ∨ (ruleReading D = true ∧ ∃ m, barReach D N = some m ∧ (aimedF D m).denote B (tupleVal vs)) := by
  have hv := rightsValid_of_wellFormed D h
  have hsv := VE.SoftNorms.softValid_of_wellFormed _ hv.wfSoft
  let S := VE.SoftNorms.canon (soften (correlate D)) B
  have hρ := VE.Norms.tupleVal_typed B (sortsOf D N) vs typed
  have conv : ∀ φ : VE.Formula, φ.WellFormed (envAt (soften (correlate D)) (size (soften (correlate D)))) (sortsOf D N).reverse →
      ((outcomeSubst D φ).denote B (tupleVal vs) ↔ φ.denote S (tupleVal vs)) :=
    fun φ hφ => VE.SoftNorms.circ_canon hsv B hB.1.1 φ _ hφ _ hρ
  have base : ∀ φ : VE.Formula, φ.WellFormed (envAt (soften (correlate D)) 0) (sortsOf D N).reverse →
      (φ.denote S (tupleVal vs) ↔ φ.denote B (tupleVal vs)) :=
    fun φ hφ => VE.SoftNorms.canon_base B φ _ hφ _
  have hown' := (conv _ (hv.ownTyped _ hN)).mp hown
  have hns' : ¬ SelectsRN D S (tupleVal vs) N := fun hsel =>
    hns ((conv _ (hv.selTyped _ hN)).mpr ((VE.SoftNorms.selectsPrime_denote _ S _ (nodeOf D N)).mpr hsel))
  obtain ⟨n, hn, hact⟩ := narrowings_complete_of_valid hv S _ N hown' hns'
  have hcond : (outcomeSubst D (condF D N n)).denote B (tupleVal vs) :=
    (conv _ (hv.condTyped _ hN n hn)).mpr (condF_of_narrowsAt hv S _ N hown' n hact)
  rcases licensed_cases (licensed_of_scope hc hL hN hs hn) with rfl | rfl | hcit | hcol | ⟨M, rfl, hse⟩ | hcert
  · exact Or.inl ((base _ (hv.packTyped _ hN)).mp hact)
  · obtain ⟨hr, m, hm, ha⟩ := hact
    exact Or.inr (Or.inr (Or.inr (Or.inr ⟨hr, m, hm, (base _ (hv.aimedTyped _ hN m hr hm)).mp ha⟩)))
  · exact Or.inr (Or.inl ⟨n, hn, hcit, hcond⟩)
  · exact Or.inr (Or.inr (Or.inl ⟨n, hn, hcol, hcond⟩))
  · exact Or.inr (Or.inr (Or.inr (Or.inl ⟨M, hse, hcond⟩)))
  · obtain ⟨c, _, hcc⟩ := List.any_eq_true.mp hcert
    cases c with
    | none => cases hcc
    | some c =>
      exact Or.inl (licensed_certified_sound D h N n c hcc B hB vs typed hcond)

end VE.Rights
