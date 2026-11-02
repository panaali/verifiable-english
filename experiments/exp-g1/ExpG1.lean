import VE.Readings.SupPacks
import VE.Readings.SupExtraExamples
import VE.NormDefaults.LayeredEntail

/-! EXP-G1: may one pack's premises mention another pack's names? (docs/spec/profile-composition-PLAN.md, EXP-G1).
Scratch work: not imported by `lean/VE.lean`, compiled with `lake env lean` from `lean/`; see REPORT.md.

Part 1 is on main's definitions. Part 2 is a COPY of the unbuilt G1b text (profile-composition.md 1.6): the statement
`acceptanceXV` is a `Prop` here, never a theorem. Part 3 is fixture `EXP-G1-mixed`, the condition PC-11 cites. -/
namespace ExpG1
open VE.NormDefaults VE.NormDefaults.Packs
open VE.Readings (Doc Choice Transfers)
open VE.Norms (envAt size Sat restrictAll)
universe u

/-! ## Part 1: the order of `X` on main's definitions -/

theorem X_perm {qs qs' : List Pack} (h : qs.Perm qs') : (X qs).Perm (X qs') :=
  (h.flatMap_right _).map _
theorem sat_perm (S : VE.Structure.{u}) {as bs : List VE.Formula} (h : as.Perm bs) : Sat S as ↔ Sat S bs :=
  ⟨fun hs a ha => hs a (h.mem_iff.mpr ha), fun hs a ha => hs a (h.mem_iff.mp ha)⟩

/-- `Sat` does not read the order of `X`. -/
theorem sat_X_perm (S : VE.Structure.{u}) {qs qs' : List Pack} (h : qs.Perm qs') : Sat S (X qs) ↔ Sat S (X qs') :=
  sat_perm S (X_perm h)

/-- `Transfers` does not read the order of either family. -/
theorem transfers_perm {D : Doc} {Q Q₂ : List VE.Formula} {Qc Qc₂ : Choice → List VE.Formula}
    (hQ : Q.Perm Q₂) (hc : ∀ c, (Qc c).Perm (Qc₂ c)) (h : Transfers.{u} D Q Qc) : Transfers.{u} D Q₂ Qc₂ :=
  ⟨fun c hcc a ha => h.1 c hcc a ((hc c).mem_iff.mpr ha), fun c hcc B hB he =>
    (sat_perm B hQ).symm.trans ((h.2 c hcc B hB he).trans (sat_perm _ (hc c)))⟩

/-- `transfers_X`'s conclusion does not read the order of the packs. -/
theorem transfers_X_perm (D : Doc) {qs qs' : List Pack} (h : qs.Perm qs') (Qc : Pack → Choice → List VE.Formula) :
    Transfers.{u} D (X qs) (fun c => qs.flatMap (fun p => Qc p c)) ↔
      Transfers.{u} D (X qs') (fun c => qs'.flatMap (fun p => Qc p c)) :=
  ⟨transfers_perm (X_perm h) (fun _ => h.flatMap_right _),
    transfers_perm (X_perm h.symm) (fun _ => h.symm.flatMap_right _)⟩

/-- `transfers_X` itself, at either order, from the same per-pack hypotheses: no hypothesis mentions another pack. -/
theorem transfers_X_either (D : Doc) {qs qs' : List Pack} (hp : qs.Perm qs') (Qc : Pack → Choice → List VE.Formula)
    (h : ∀ p ∈ qs, Transfers.{u} D (p.labelled.map (·.2)) (Qc p)) :
    Transfers.{u} D (X qs') (fun c => qs'.flatMap (fun p => Qc p c)) :=
  VE.Readings.transfers_X D qs' Qc (fun p hm => h p (hp.mem_iff.mpr hm))

/-- G1 (`EntailsX`, main's), the constraint-pack case: no hypothesis at all. -/
theorem entailsX_perm (U : UDoc) {qs qs' : List Pack} (h : qs.Perm qs') (Γ : List VE.Formula) (φ : VE.Formula) :
    EntailsX.{u} U (X qs) Γ φ ↔ EntailsX.{u} U (X qs') Γ φ :=
  forall_congr' fun S => by simp only [Wire.BaseAdmissibleX, sat_X_perm _ h]

/-- `acceptanceX` (main's, proved) from a certificate at one order gives the entailment at the other. -/
theorem acceptanceX_order_free (U : UDoc) (hU : WellFormedU U = true) {qs qs' : List Pack} (h : qs.Perm qs')
    (hX : ∀ a ∈ X qs, a.WellFormed (envAt (fill U) 0) []) (Γ : List VE.Formula) (φ : VE.Formula)
    (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (envAt (fill U) (size (fill U))) (Wire.premisesX U (X qs) Γ) φ cert = true) :
    EntailsX.{u} U (X qs') Γ φ :=
  (entailsX_perm U h Γ φ).mp (acceptanceX U hU (X qs) hX Γ φ cert hv)

/-! ## Part 2: G1b, a COPY of the unbuilt statement (profile-composition.md 1.6, at 3dfadd302) -/

def fullEnvX (U : UDoc) (qs : List Pack) : VE.Environment :=
  extendEnv (fullEnv U) (qs.flatMap (·.decls)) (qs.flatMap (·.consts))

def BaseAdmissibleXV (U : UDoc) (qs : List Pack) (B : VE.Structure.{u}) : Prop :=
  B.Admissible (envX U qs) ∧ Sat B (VE.Norms.backgroundBase (fill U)) ∧ Sat B (fillPremises U) ∧ Sat B (X qs)

def DocumentExpansionXV (U : UDoc) (qs : List Pack) (B S : VE.Structure.{u}) : Prop :=
  restrictAll (fill U).T S = B ∧ S.Admissible (fullEnvX U qs) ∧
    Sat S (VE.Norms.background (fill U) ++ VE.Norms.elaborate (fill U).T)

def EntailsXV (U : UDoc) (qs : List Pack) (Γ : List VE.Formula) (φ : VE.Formula) : Prop :=
  ∀ S : VE.Structure.{u}, BaseAdmissibleXV U qs (restrictAll (fill U).T S) →
    DocumentExpansionXV U qs (restrictAll (fill U).T S) S → Sat S Γ → φ.denote S []

/-- `acceptanceXV`'s statement as a `Prop`: nothing here proves it (PK-1's owner builds it). -/
def AcceptanceXV : Prop :=
  ∀ (U : UDoc) (_ : WellFormedU U = true) (qs : List Pack)
    (_ : ∀ n ∈ names qs, declaredIn (fullEnv U) n = false)
    (_ : ∀ a ∈ X qs, a.WellFormed (envX U qs) []) (Γ : List VE.Formula) (φ : VE.Formula)
    (cert : VE.Tableau.Certificate)
    (_ : VE.Tableau.checkCertificate (fullEnvX U qs) (Wire.premisesX U (X qs) Γ) φ cert = true),
    EntailsXV.{u} U qs Γ φ

/-! ### The order claim over the copy -/

theorem lookup_perm {β : Type} {l l' : List (String × β)} (h : l.Perm l') (hn : (l.map (·.1)).Nodup) (n : String) :
    l.lookup n = l'.lookup n := by
  induction h with
  | nil => rfl
  | cons x _ ih =>
    obtain ⟨k, v⟩ := x
    simp only [List.map_cons, List.nodup_cons] at hn
    simp only [List.lookup, ih hn.2]
  | swap x y l =>
    obtain ⟨k₁, v₁⟩ := x
    obtain ⟨k₂, v₂⟩ := y
    simp only [List.map_cons, List.nodup_cons, List.mem_cons, not_or] at hn
    simp only [List.lookup]
    split <;> split <;> simp_all
  | trans h₁ _ ih₁ ih₂ =>
    rw [ih₁ hn, ih₂ ((h₁.map _).nodup_iff.mp hn)]

theorem keys_sublist (qs : List Pack) : ((qs.flatMap (·.decls)).map (·.1)).Sublist (names qs) ∧
    ((qs.flatMap (·.consts)).map (·.1)).Sublist (names qs) := by
  induction qs with
  | nil => exact ⟨.refl _, .refl _⟩
  | cons p ps ih =>
    simp only [List.flatMap_cons, List.map_append, names, Pack.names]
    exact ⟨(List.sublist_append_left _ _).append ih.1, (List.sublist_append_right _ _).append ih.2⟩

/-- `extendEnv` reads the order of its lists only through `lookup`'s first match. -/
theorem extendEnv_perm (E : VE.Environment) {qs qs' : List Pack} (h : qs.Perm qs') (hd : (names qs).Nodup) :
    extendEnv E (qs.flatMap (·.decls)) (qs.flatMap (·.consts)) =
      extendEnv E (qs'.flatMap (·.decls)) (qs'.flatMap (·.consts)) := by
  have h₁ := lookup_perm (h.flatMap_right (·.decls)) (hd.sublist (keys_sublist qs).1)
  have h₂ := lookup_perm (h.flatMap_right (·.consts)) (hd.sublist (keys_sublist qs).2)
  simp only [extendEnv, h₁, h₂]

theorem envX_perm (U : UDoc) {qs qs' : List Pack} (h : qs.Perm qs') (hd : (names qs).Nodup) :
    envX U qs = envX U qs' := extendEnv_perm _ h hd
theorem fullEnvX_perm (U : UDoc) {qs qs' : List Pack} (h : qs.Perm qs') (hd : (names qs).Nodup) :
    fullEnvX U qs = fullEnvX U qs' := extendEnv_perm _ h hd
theorem baseAdmissibleXV_perm (U : UDoc) {qs qs' : List Pack} (h : qs.Perm qs') (hd : (names qs).Nodup)
    (B : VE.Structure.{u}) : BaseAdmissibleXV U qs B ↔ BaseAdmissibleXV U qs' B := by
  simp only [BaseAdmissibleXV, envX_perm U h hd, sat_X_perm B h]

theorem documentExpansionXV_perm (U : UDoc) {qs qs' : List Pack} (h : qs.Perm qs') (hd : (names qs).Nodup)
    (B S : VE.Structure.{u}) : DocumentExpansionXV U qs B S ↔ DocumentExpansionXV U qs' B S := by
  simp only [DocumentExpansionXV, fullEnvX_perm U h hd]

/-- G1b's entailment does not read the order, on a list with distinct names. -/
theorem entailsXV_perm (U : UDoc) {qs qs' : List Pack} (h : qs.Perm qs') (hd : (names qs).Nodup)
    (Γ : List VE.Formula) (φ : VE.Formula) : EntailsXV.{u} U qs Γ φ ↔ EntailsXV.{u} U qs' Γ φ := by
  simp only [EntailsXV, baseAdmissibleXV_perm U h hd, documentExpansionXV_perm U h hd]

theorem firstRepeat_none : ∀ (seen : List String) (l : List (String × String)), firstRepeat seen l = none →
    (l.map (·.2)).Nodup ∧ ∀ n ∈ l.map (·.2), n ∉ seen
  | _, [], _ => ⟨List.nodup_nil, fun _ hn => nomatch hn⟩
  | seen, (i, n) :: rest, h => by
    simp only [firstRepeat] at h
    split at h
    · cases h
    rename_i hs
    obtain ⟨hn, hr⟩ := firstRepeat_none (n :: seen) rest h
    refine ⟨List.nodup_cons.mpr ⟨fun hm => hr n hm (List.mem_cons_self ..), hn⟩, fun m hm => ?_⟩
    rcases List.mem_cons.mp hm with rfl | hm
    · simpa using hs
    · exact fun hc => hr m hm (List.mem_cons_of_mem _ hc)

theorem named_keys (qs : List Pack) :
    (qs.flatMap (fun p => p.names.map (fun n => (p.id, n)))).map (·.2) = names qs := by
  simp [names, List.map_flatMap, Function.comp_def]
/-- Assembly's own check: every list `assembleIn` returns has distinct names, so "declared by some pack" is "by one". -/
theorem assembleIn_distinct {pre : List (String × String)} {E : VE.Environment} {used : Nat} {ps qs : List Pack}
    (h : assembleIn pre E used ps = .ok qs) : (names qs).Nodup := by
  obtain ⟨_, _, _, _, _, hr, _⟩ := assembleIn_ok h
  simpa [named_keys] using (firstRepeat_none [] _ hr).1

/-- Assembly's own check: `hfresh`, as 1.6 says. -/
theorem assembleIn_fresh {pre : List (String × String)} {E : VE.Environment} {used : Nat} {ps qs : List Pack}
    (h : assembleIn pre E used ps = .ok qs) : ∀ n ∈ names qs, declaredIn E n = false := by
  obtain ⟨_, _, _, _, hf, _⟩ := assembleIn_ok h
  intro n hn
  rw [← named_keys] at hn
  obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hn
  exact hf x hx

/-- The whole order claim for G1b on what `assemble` returns: a certificate at `packOrder`'s order gives the
    entailment at every reordering of the list, with only `hX` (every name is declared) as a typing hypothesis. -/
theorem g1b_order_free (hA : AcceptanceXV.{u}) (U : UDoc) (hU : WellFormedU U = true) {used : Nat} {ps qs qs' : List Pack}
    (hok : assemble U used ps = .ok qs) (h : qs.Perm qs') (hX : ∀ a ∈ X qs, a.WellFormed (envX U qs) [])
    (Γ : List VE.Formula) (φ : VE.Formula) (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (fullEnvX U qs) (Wire.premisesX U (X qs) Γ) φ cert = true) :
    EntailsXV.{u} U qs' Γ φ :=
  (entailsXV_perm U h (assembleIn_distinct hok) Γ φ).mp (hA U hU qs (assembleIn_fresh hok) hX Γ φ cert hv)

/-! ## Part 3: fixture `EXP-G1-mixed`, the synthetic mixed-condition test PC-11 cites

"Helpfulness outweighs caution on answering when the user believes the information is hazardous": weighing's
`condPremise` shape (weighing-PLAN, `.sufficient`) over an attitude atom. Both packs are by hand; neither is on main.
`V` is the plan's case, every name declared by some pack. `C` is the shape the attitudes and weighing plans build,
`.constraint` packs whose names `U` declares (attitudes.md 2.4, RF-5; weighing-PLAN D3). -/

def attBelieves : String := "attitudes__believes__1"
def attKnows : String := "attitudes__knows__2"
def guardName : String := "weighing__outweighs__answer__helpfulness__caution"
/-- The condition under test, in context `[user, agent]`. Its one definition: the REPORT's mutants edit this line. -/
def mixedCondition : VE.Formula := .unary attBelieves (.var 0)
def mixedGuard : VE.Formula := .binary guardName (.var 1) (.var 0)
def mixedPremise : VE.Formula := .all "agent" (.all "user" (.implies mixedCondition mixedGuard))
def bridgePremise : VE.Formula := .all "user" (.implies (.unary attKnows (.var 0)) (.unary attBelieves (.var 0)))
def weighingV : Pack := ⟨"weighing", .vocabulary, [(guardName, ["agent", "user"])], [],
  [("weighing:condition:1", mixedPremise)], [], [(.outweighs "answer" "helpfulness" "caution", mixedCondition)]⟩
def attitudesV : Pack := ⟨"attitudes", .vocabulary, [(attBelieves, ["user"]), (attKnows, ["user"])], [],
  [("attitudes:bridge:1", bridgePremise)], [], []⟩
def weighingC : Pack := { weighingV with kind := .constraint, decls := [] }
def attitudesC : Pack := { attitudesV with kind := .constraint, decls := [] }
/-- `packOrder`'s order: weighing's premise mentions a name of the later pack. -/
def mixedV : List Pack := [weighingV, attitudesV]
def mixedC : List Pack := [weighingC, attitudesC]
def envG (ps : List (String × List String)) : VE.Environment := ⟨["agent", "user"], fun n => ps.lookup n, fun _ => none⟩
def namesG : List (String × List String) := [(attBelieves, ["user"]), (attKnows, ["user"]), (guardName, ["agent", "user"])]
/-- `V`: only the packs declare the names. -/
def uV : UDoc := ⟨⟨envG [], [], ⟨[], [], []⟩⟩, []⟩
/-- `C`: `U` declares the names, as `envAtt` does. -/
def uC : UDoc := ⟨⟨envG namesG, [], ⟨[], [], []⟩⟩, []⟩
/-- The predicate names a formula mentions. -/
def preds : VE.Formula → List String
  | .unary p _ | .binary p _ _ => [p]
  | .top | .bottom | .eq _ _ => []
  | .not a | .all _ a | .ex _ a => preds a
  | .and a b | .or a b | .implies a b => preds a ++ preds b

/-- A prefix table with `V`'s two rows: main's has none for weighing or attitudes (AT-2 adds attitudes'). -/
def prefixesG : List (String × String) := reservedPrefixes ++ [("weighing", "weighing__"), ("attitudes", "attitudes__")]
def idsOf : Except String (List Pack) → List String
  | .ok qs => qs.map (·.id)
  | .error e => [e]

-- The mention is real: weighing's premise names a name only the later pack declares.
#guard packOrder.idxOf "weighing" < packOrder.idxOf "attitudes"
#guard (preds mixedPremise).contains attBelieves && !(weighingV.names.contains attBelieves) && attitudesV.names.contains attBelieves
-- Typing: over the whole list at both orders, and neither over the base alone nor over weighing's own names alone.
#guard (X mixedV).all (·.check (envX uV mixedV) [])
#guard (X mixedV.reverse).all (·.check (envX uV mixedV.reverse) [])
#guard !mixedPremise.check (envAt (fill uV) 0) []
#guard !mixedPremise.check (envX uV [weighingV]) []
-- Assembly puts weighing first from either input order, once its prefix rows exist.
#guard idsOf (assembleIn prefixesG (fullEnv uV) 0 [attitudesV, weighingV]) == ["weighing", "attitudes"]
#guard idsOf (assembleIn prefixesG (fullEnv uV) 0 mixedV) == ["weighing", "attitudes"]
-- Main's table refuses shape `V`; shape `C` assembles on main.
#guard idsOf (assemble uV 0 mixedV) == ["InvalidInput: a generated name of pack weighing lacks its reserved prefix"]
#guard idsOf (assemble uC 0 mixedC) == ["weighing", "attitudes"]
#guard WellFormedU uV && WellFormedU uC

/-! ### Non-vacuity: the attitude atom decides the guard -/

/-- One agent, one user; the attitude atoms and the guard as given. -/
def mK (knows believes guard : Bool) : VE.FiniteModel String where
  domains s := match s with | "agent" => ["a"] | "user" => ["u"] | _ => []
  constants _ := none
  relations p := if p == attBelieves then (if believes then [["u"]] else [])
    else if p == attKnows then (if knows then [["u"]] else [])
    else if p == guardName then (if guard then [["a", "u"]] else []) else []
/-- `knows` empty. -/
def mG (believes guard : Bool) : VE.FiniteModel String := mK false believes guard

def holdsX (qs : List Pack) (M : VE.FiniteModel String) : Bool := (X qs).all (·.eval M [])
/-- Atom off, guard off: `X` holds. Flip only the atom: `X` breaks. Turn the guard on: `X` holds again. -/
def nonVacuous (qs : List Pack) : Bool :=
  holdsX qs (mG false false) && !holdsX qs (mG true false) && holdsX qs (mG true true)

#guard nonVacuous mixedV && nonVacuous mixedV.reverse && nonVacuous mixedC && nonVacuous mixedC.reverse
/-- `mK` is admissible over any environment with no constants that declares the three names as `namesG` does. -/
theorem mK_admissible {E : VE.Environment} (hc : ∀ c, E.constants c = none)
    (hE : ∀ n ∈ namesG, E.predicates n.1 = some n.2) (k b g : Bool) : (mK k b g).asStructure.Admissible E := by
  refine ⟨fun c s h => (by rw [hc c] at h; cases h), fun p vs hr => ?_⟩
  change vs ∈ (mK k b g).relations p at hr
  simp only [mK] at hr
  have h₁ : attKnows ≠ attBelieves ∧ guardName ≠ attBelieves ∧ guardName ≠ attKnows := by decide
  by_cases hb : p = attBelieves
  · subst hb
    cases b <;> simp at hr
    subst hr
    exact ⟨["user"], hE (attBelieves, ["user"]) (by decide), by simp [VE.TupleTyped, VE.FiniteModel.asStructure, mK]⟩
  by_cases hk : p = attKnows
  · subst hk
    cases k <;> simp [h₁] at hr
    subst hr
    exact ⟨["user"], hE (attKnows, ["user"]) (by decide), by simp [VE.TupleTyped, VE.FiniteModel.asStructure, mK]⟩
  by_cases hg : p = guardName
  · subst hg
    cases g <;> simp [h₁] at hr
    subst hr
    exact ⟨["agent", "user"], hE (guardName, ["agent", "user"]) (by decide),
      by simp [VE.TupleTyped, VE.FiniteModel.asStructure, mK]⟩
  · simp [hb, hk, hg] at hr
theorem mG_admissible (b g : Bool) : (mG b g).asStructure.Admissible (envX uV mixedV) :=
  mK_admissible (fun _ => rfl) (by decide) false b g

theorem sat_of_holdsX {qs : List Pack} {M : VE.FiniteModel String} (h : holdsX qs M = true) : Sat M.asStructure (X qs) :=
  fun a ha => (VE.eval_iff_denote _ _ _).mp (List.all_eq_true.mp h a ha)
theorem uV_backgroundBase : VE.Norms.backgroundBase (fill uV) = [] := by
  show VE.Route.Background.literals [] = []
  simp [VE.Route.Background.literals, VE.Route.sortStrings, VE.Route.Background.pairs]
theorem uV_fillPremises : fillPremises uV = [] := by decide
theorem uV_background : VE.Norms.background (fill uV) = [] := by
  simp only [VE.Norms.background, uV_backgroundBase]; simp (config := { ground := true, decide := true })
theorem uV_elaborate : VE.Norms.elaborate (fill uV).T = [] := by
  simp (config := { ground := true, decide := true })

/-- On `V`, at `packOrder`'s order, the attitude atom decides the guard at G1b's bases. -/
theorem mixedV_decides :
    BaseAdmissibleXV uV mixedV (mG false false).asStructure ∧ BaseAdmissibleXV uV mixedV (mG true true).asStructure ∧
      ¬ BaseAdmissibleXV uV mixedV (mG true false).asStructure := by
  have hb : ∀ B : VE.Structure.{0}, Sat B (VE.Norms.backgroundBase (fill uV)) ∧ Sat B (fillPremises uV) := fun _ => by
    rw [uV_backgroundBase, uV_fillPremises]
    exact ⟨fun _ ha => (nomatch ha), fun _ ha => (nomatch ha)⟩
  have hv : nonVacuous mixedV = true := by decide
  simp only [nonVacuous, Bool.and_eq_true, Bool.not_eq_true'] at hv
  refine ⟨⟨mG_admissible _ _, (hb _).1, (hb _).2, sat_of_holdsX hv.1.1⟩,
    ⟨mG_admissible _ _, (hb _).1, (hb _).2, sat_of_holdsX hv.2⟩, fun h => ?_⟩
  have := hv.1.2
  have hs : holdsX mixedV (mG true false) = true :=
    List.all_eq_true.mpr fun a ha => (VE.eval_iff_denote _ _ _).mpr (h.2.2.2 a ha)
  simp [this] at hs

/-! ### Acceptance at either order -/

def mixedφ : VE.Formula :=
  .all "agent" (.all "user" (.implies (.unary attKnows (.var 0)) (.binary guardName (.var 1) (.var 0))))

/-- A trace for premises `[…, …, ¬φ]`, with the mixed premise at `iw` and the bridge at `ia`: it needs both packs. -/
def traceAt (iw ia : Nat) : VE.Tableau.Trace :=
  .expand 2 none [.expand 3 none [.expand 4 none [.expand ia (some "w:1") [.expand iw (some "w:0") [
    .expand 8 (some "w:1") [.expand 7 none [.close, .expand 9 none [.close, .close]]]]]]]]
def certAt (iw ia : Nat) : VE.Tableau.Certificate := ⟨"ve-tableau-checker@2", "", [], "", traceAt iw ia⟩
def certOK (U : UDoc) (E : VE.Environment) (qs : List Pack) (c : VE.Tableau.Certificate) : Bool :=
  VE.Tableau.checkCertificate E (Wire.premisesX U (X qs) []) mixedφ c

-- Each order needs its own certificate: `Trace` names premises by index. The entailment (below) is not so bound.
#guard certOK uV (fullEnvX uV mixedV) mixedV (certAt 0 1)
#guard certOK uV (fullEnvX uV mixedV.reverse) mixedV.reverse (certAt 1 0)
#guard !certOK uV (fullEnvX uV mixedV.reverse) mixedV.reverse (certAt 0 1)
#guard certOK uC (fullEnv uC) mixedC (certAt 0 1)
#guard certOK uC (fullEnv uC) mixedC.reverse (certAt 1 0)
#guard !certOK uC (fullEnv uC) mixedC.reverse (certAt 0 1)
-- The diagnostic does read the order, with the same truth value: `packOrder` is what fixes this text.
#guard (firstFailing mixedV (fun _ => false)).map (·.1) == some "weighing"
#guard (firstFailing mixedV.reverse (fun _ => false)).map (·.1) == some "attitudes"

set_option maxRecDepth 100000 in
/-- `C`, on main's own definitions and main's proved `acceptanceX`, with no copy: a certificate at `packOrder`'s
    order gives `EntailsX` at both orders. `hv` is the `#guard` above (the repo's `X1Checks` pattern: the kernel cannot reduce the replay). -/
theorem mixedC_accepted (hv : certOK uC (fullEnv uC) mixedC (certAt 0 1) = true) :
    EntailsX.{u} uC (X mixedC) [] mixedφ ∧ EntailsX.{u} uC (X mixedC.reverse) [] mixedφ :=
  have hU : WellFormedU uC = true := by decide
  have hX : ∀ a ∈ X mixedC, a.WellFormed (envAt (fill uC) 0) [] := fun a ha =>
    (VE.check_iff_wellFormed _ _ _).mp (List.all_eq_true.mp (by decide : (X mixedC).all (·.check (envAt (fill uC) 0) []) = true) a ha)
  ⟨acceptanceX uC hU (X mixedC) hX [] mixedφ _ hv,
    acceptanceX_order_free uC hU (List.reverse_perm mixedC).symm hX [] mixedφ _ hv⟩

/-- A model of `X qs` at `uC`'s bases where `mixedφ` fails refutes `EntailsX`. -/
theorem not_entailsX_uC {qs : List Pack} (k b g : Bool) (hX : holdsX qs (mK k b g) = true)
    (hφ : mixedφ.eval (mK k b g) [] = false) : ¬ EntailsX.{0} uC (X qs) [] mixedφ := by
  intro H
  have ha := mK_admissible (E := envAt (fill uC) 0) (fun _ => rfl) (by decide) k b g
  have hr := VE.Norms.restrictAll_self (D := fill uC) _ ha
  have hs : size (fill uC) = 0 := by decide
  have hbb : VE.Norms.backgroundBase (fill uC) = [] := by
    show VE.Route.Background.literals [] = []
    simp [VE.Route.Background.literals, VE.Route.sortStrings, VE.Route.Background.pairs]
  have hfp : fillPremises uC = [] := by decide
  have hbg : VE.Norms.background (fill uC) ++ VE.Norms.elaborate (fill uC).T = [] := by
    simp only [VE.Norms.background, hbb]; simp (config := { ground := true, decide := true })
  have hφ' := H (mK k b g).asStructure
    (by rw [hr]; exact ⟨⟨⟨ha, by rw [hbb]; exact fun _ h => nomatch h⟩, by rw [hfp]; exact fun _ h => nomatch h⟩,
      sat_of_holdsX hX⟩)
    ⟨rfl, by rw [hs]; exact ha, by rw [hbg]; exact fun _ h => nomatch h⟩ (fun _ h => nomatch h)
  simp [(VE.eval_iff_denote _ _ _).mpr hφ'] at hφ

/-- The conclusion needs both packs: a model of each pack's `X` alone refutes it. Weighing alone: `knows` on,
    `believes` and the guard off. Attitudes alone: `knows` and `believes` on, the guard off. (A trace refused at one
    pack's indices is no such check: with one pack, index 2 is out of range whatever the pack says.) -/
theorem single_pack_refuted : ¬ EntailsX.{0} uC (X [weighingC]) [] mixedφ ∧ ¬ EntailsX.{0} uC (X [attitudesC]) [] mixedφ :=
  ⟨not_entailsX_uC true false false (by decide) (by decide), not_entailsX_uC true true false (by decide) (by decide)⟩

/-- `V`: the conclusion of `acceptanceXV` at this fixture, at either order, from main's `checkCertificate_sound`. This
    proves the instance, not the unbuilt `acceptanceXV`. -/
theorem mixedV_accepted (hv : certOK uV (fullEnvX uV mixedV) mixedV (certAt 0 1) = true) :
    EntailsXV.{u} uV mixedV [] mixedφ ∧ EntailsXV.{u} uV mixedV.reverse [] mixedφ := by
  have h : EntailsXV.{u} uV mixedV [] mixedφ := by
    intro S hB hE _
    apply VE.Tableau.checkCertificate_sound.{u} _ _ _ _ hv S hE.2.1
    intro a ha
    simp only [Wire.premisesX, List.mem_append] at ha
    rcases ha with (((ha | ha) | ha) | ha) | ha
    · exact hE.2.2 a (List.mem_append_left _ ha)
    · have hw : a.WellFormed (envX uV mixedV) [] := (VE.check_iff_wellFormed _ _ _).mp
        (List.all_eq_true.mp (by decide : (X mixedV).all (·.check (envX uV mixedV) []) = true) a ha)
      exact (VE.Norms.denote_forget (by decide) S a [] [] hw).mp (hB.2.2.2 a ha)
    · rw [uV_fillPremises] at ha; cases ha
    · exact hE.2.2 a (List.mem_append_right _ ha)
    · cases ha
  exact ⟨h, (entailsXV_perm uV (List.reverse_perm mixedV).symm (by decide) [] mixedφ).mp h⟩

/-! ## Part 4: the one case where G1b's order matters, and why it is not a pack-order rule

Two packs declare one name with different arities. `extendEnv` takes `lookup`'s first match, so the environment reads
the order. `assemble` refuses this list (`Packs.lean:105`), and no premise mentions anything: the rule "a pack's
premises mention only names of packs before it" would not touch it. -/

def dupName : String := "weighing__n"
def dupA : Pack := { weighingV with decls := [(dupName, ["agent"])], labelled := [], conditions := [] }
def dupB : Pack := { attitudesV with decls := [(dupName, ["agent", "agent"])], labelled := [] }
/-- True exactly when the binary reading of the name is empty. -/
def dupφ : VE.Formula := .all "agent" (.all "agent" (.not (.binary dupName (.var 1) (.var 0))))

#guard idsOf (assembleIn prefixesG (fullEnv uV) 0 [dupA, dupB]) ==
  ["InvalidInput: generated name weighing__n of pack attitudes is declared twice"]

/-- One element; the name holds of the pair. -/
def dupS : VE.Structure.{0} where
  Carrier := Unit
  domain _ _ := True
  constant _ := none
  relation p vs := p = dupName ∧ vs = [(), ()]

theorem dup_order_matters :
    EntailsXV.{0} uV [dupA, dupB] [] dupφ ∧ ¬ EntailsXV.{0} uV [dupB, dupA] [] dupφ := by
  constructor
  · intro S _ hE _ v _ w _ hr
    simp only [VE.Formula.denote, VE.Term.denote] at hr
    obtain ⟨_, _, hv, hw, hr⟩ := hr
    simp only [List.getElem?_cons_zero, List.getElem?_cons_succ, Option.some.injEq] at hv hw
    subst hv hw
    obtain ⟨ss, hss, ht⟩ := hE.2.1.2 _ _ hr
    rw [show (fullEnvX uV [dupA, dupB]).predicates dupName = some ["agent"] by decide] at hss
    cases hss
    simp [VE.TupleTyped] at ht
  · intro H
    have hA : dupS.Admissible (fullEnvX uV [dupB, dupA]) :=
      ⟨fun _ _ hc => (nomatch hc), fun p vs hr => by
        obtain ⟨rfl, rfl⟩ := hr
        exact ⟨["agent", "agent"], by decide, trivial, trivial, trivial⟩⟩
    have hA₀ : (restrictAll (fill uV).T dupS).Admissible (envX uV [dupB, dupA]) :=
      ⟨fun _ _ hc => (nomatch hc), fun p vs hr => by
        obtain ⟨_, rfl, rfl⟩ := hr
        exact ⟨["agent", "agent"], by decide, trivial, trivial, trivial⟩⟩
    have hbg : Sat dupS (VE.Norms.background (fill uV) ++ VE.Norms.elaborate (fill uV).T) := by
      intro a ha
      rw [uV_background, uV_elaborate] at ha
      cases ha
    have hbase : BaseAdmissibleXV.{0} uV [dupB, dupA] (restrictAll (fill uV).T dupS) :=
      ⟨hA₀, by rw [uV_backgroundBase]; exact fun _ ha => (nomatch ha), by rw [uV_fillPremises]; exact fun _ ha => (nomatch ha),
        fun _ ha => (nomatch ha)⟩
    have := H dupS hbase ⟨rfl, hA, hbg⟩ (fun _ ha => (nomatch ha))
    exact this () trivial () trivial ⟨(), (), rfl, rfl, rfl, rfl⟩

/-! ## Part 5: `Transfers` on the readings route, at the fixture

A readings document whose frame declares the names (shape `C`), so the atom can decide a guard at `Transfers`' own
bases. -/

open VE.Readings
open VE.Readings.Examples (docK frameK rs1 ex₂)
open VE.Rights (correlate)
open VE.SoftNorms (soften)
open VE.Compose (BaseAdmissibleP)

def envKG : VE.Environment :=
  let E₀ := frameK.soft.E
  { E₀ with predicates := fun n => match namesG.lookup n with | some s => some s | none => E₀.predicates n }
def frameG : VE.Rights.RightsDoc :=
  let s := frameK.soft
  { frameK with soft := { s with E := envKG } }
def kG : Doc := docK [.set rs1] .soft frameG
def KGChecks : Prop := WellFormedDoc kG = true ∧ superposable kG = true
instance : Decidable KGChecks := inferInstanceAs (Decidable (_ ∧ _))
#guard KGChecks
#guard choices kG == [[("rs1", 0)], [("rs1", 1)]]

theorem kG_hyps (hx : KGChecks) : Hyps kG := ⟨hx.1, by decide, hx.2⟩

/-- A formula over frame predicates reads a pulled base as it reads the base. -/
theorem denote_pull {D : Doc} (hh : Hyps D) (c : Choice) (S : VE.Structure.{u}) (a : VE.Formula) (ρ : VE.Valuation S)
    (ha : ∀ p ∈ preds a, D.frame.soft.E.predicates p ≠ none) : a.denote (pull D c S) ρ ↔ a.denote S ρ := by
  induction a generalizing ρ with
  | top | bottom | eq => exact Iff.rfl
  | unary p t =>
    simp only [VE.Formula.denote]
    exact exists_congr fun v => and_congr_right fun _ => pull_frame hh c S (ha p (by simp [preds])) _
  | binary p t u =>
    simp only [VE.Formula.denote]
    exact exists_congr fun v => exists_congr fun w => and_congr_right fun _ => and_congr_right fun _ =>
      pull_frame hh c S (ha p (by simp [preds])) _
  | not a ih => exact not_congr (ih ρ ha)
  | and a b iha ihb =>
    exact and_congr (iha ρ fun p hp => ha p (by simp [preds, hp])) (ihb ρ fun p hp => ha p (by simp [preds, hp]))
  | or a b iha ihb =>
    exact or_congr (iha ρ fun p hp => ha p (by simp [preds, hp])) (ihb ρ fun p hp => ha p (by simp [preds, hp]))
  | implies a b iha ihb =>
    exact imp_congr (iha ρ fun p hp => ha p (by simp [preds, hp])) (ihb ρ fun p hp => ha p (by simp [preds, hp]))
  | all s a ih => exact forall_congr' fun v => imp_congr_right fun _ => ih _ ha
  | ex s a ih => exact exists_congr fun v => and_congr_right fun _ => ih _ ha

def QcG (p : Pack) (_ : Choice) : List VE.Formula := p.labelled.map (·.2)

theorem kG_compatible (hx : KGChecks) {c : Choice} (hc : Compatible kG c) : c = [("rs1", 0)] ∨ c = [("rs1", 1)] := by
  have := (choices_spec kG (kG_hyps hx).ready (by decide) c).mpr hc
  rw [show choices kG = [[("rs1", 0)], [("rs1", 1)]] by decide] at this
  simpa using this

/-- Each pack's premises transfer, on `C`, with no reference to the other pack, though weighing's names attitudes'. -/
theorem mixedC_packs_transfer (hx : KGChecks) : ∀ p ∈ mixedC, Transfers.{u} kG (p.labelled.map (·.2)) (QcG p) := by
  intro p hp
  have hw : ∀ a ∈ X mixedC, ∀ c, (c = [("rs1", 0)] ∨ c = [("rs1", 1)]) → a.check (choiceEnvFull kG c) [] = true := by
    intro a ha c hc
    rcases hc with rfl | rfl
    · exact List.all_eq_true.mp (by decide : (X mixedC).all (·.check (choiceEnvFull kG [("rs1", 0)]) []) = true) a ha
    · exact List.all_eq_true.mp (by decide : (X mixedC).all (·.check (choiceEnvFull kG [("rs1", 1)]) []) = true) a ha
  have hmem : ∀ a ∈ p.labelled.map (·.2), a ∈ X mixedC := fun a ha => by
    simp only [X, labelledX, List.mem_map, List.mem_flatMap]
    obtain ⟨b, hb, rfl⟩ := List.mem_map.mp ha
    exact ⟨b, ⟨p, hp, hb⟩, rfl⟩
  have hfr : ∀ a ∈ X mixedC, ∀ q ∈ preds a, kG.frame.soft.E.predicates q ≠ none := by
    intro a ha q hq
    have hall : (X mixedC).all (fun a => (preds a).all (fun q => (kG.frame.soft.E.predicates q).isSome)) = true := by decide
    have := List.all_eq_true.mp (List.all_eq_true.mp hall a ha) q hq
    simpa [Option.isSome_iff_ne_none] using this
  refine ⟨fun c hc a ha => (VE.check_iff_wellFormed _ _ _).mp (hw a (hmem a ha) c (kG_compatible hx hc)), fun c _ B _ _ => ?_⟩
  exact ⟨fun hs a ha => (denote_pull (kG_hyps hx) c B a [] (hfr a (hmem a ha))).mpr (hs a ha),
    fun hs a ha => (denote_pull (kG_hyps hx) c B a [] (hfr a (hmem a ha))).mp (hs a ha)⟩

/-- `transfers_X` at `packOrder`'s order and at the other. -/
theorem mixedC_transfers (hx : KGChecks) :
    Transfers.{u} kG (X mixedC) (fun c => mixedC.flatMap (fun p => QcG p c)) ∧
      Transfers.{u} kG (X mixedC.reverse) (fun c => mixedC.reverse.flatMap (fun p => QcG p c)) :=
  ⟨transfers_X kG mixedC QcG (mixedC_packs_transfer hx),
    transfers_X_either kG (List.reverse_perm mixedC).symm QcG (mixedC_packs_transfer hx)⟩

/-- M2's base (reading 1) with the attitude atom and the guard as given. -/
def baseG (believes guard : Bool) : VE.FiniteModel String where
  domains s := match s with | "agent" => ["a"] | "user" => ["u"] | "ve__reading" => ["e"] | _ => []
  constants x := if x == "ve__here" then some "e" else none
  relations p := if p == "ve__bit__1__0" then [["e"]] else if p == ex₂ then [["a", "u"]]
    else (mG believes guard).relations p

-- Non-vacuity at `Transfers`' own bases: each is slot-admissible and spells reading 1, and the atom decides `X`.
#guard [(false, false), (true, false), (true, true)].all fun (b, g) =>
  VE.Compose.backgroundValidP (correlate (sup kG).1) (slotP kG) (baseG b g) && (choiceAtom kG "rs1" 1).eval (baseG b g) []
#guard holdsX mixedC (baseG false false) && !holdsX mixedC (baseG true false) && holdsX mixedC (baseG true true)
#guard holdsX mixedC.reverse (baseG false false) && !holdsX mixedC.reverse (baseG true false)

/-! ### Shape `V` on the readings route: order free, and the atom decides nothing -/

/-- `Transfers`' bases are admissible over the document's old vocabulary, so a name the document does not declare has
    no tuple there: draft 3's G1b defect (profile-composition.md 1.6). The order plays no part. -/
theorem undeclared_empty_at_transfers_bases {D : Doc} {P : List VE.Formula} {B : VE.Structure.{u}} {n : String}
    (hB : BaseAdmissibleP (correlate (sup D).1) P B)
    (hn : (envAt (soften (correlate (sup D).1)) 0).predicates n = none) (vs : List B.Carrier) : ¬ B.relation n vs :=
  fun hr => by
    obtain ⟨_, hss, _⟩ := hB.1.1.1.2 n vs hr
    rw [hn] at hss
    cases hss

-- On a document without the names: undeclared at the base, and untyped over each choice's complete vocabulary.
#guard (envAt (soften (correlate (sup VE.Readings.Examples.K1).1)) 0).predicates attBelieves == none
#guard (choices VE.Readings.Examples.K1).all (fun c => !mixedPremise.check (choiceEnvFull VE.Readings.Examples.K1 c) [])

end ExpG1
#print axioms ExpG1.sat_X_perm
#print axioms ExpG1.transfers_X_perm
#print axioms ExpG1.entailsX_perm
#print axioms ExpG1.acceptanceX_order_free
#print axioms ExpG1.entailsXV_perm
#print axioms ExpG1.g1b_order_free
#print axioms ExpG1.mixedV_decides
#print axioms ExpG1.mixedC_accepted
#print axioms ExpG1.mixedV_accepted
#print axioms ExpG1.single_pack_refuted
#print axioms ExpG1.dup_order_matters
#print axioms ExpG1.mixedC_transfers
#print axioms ExpG1.undeclared_empty_at_transfers_bases
