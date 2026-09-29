import VE.Attribution.Assess

/-! Spec 9.3, bridges (5.2): a bridge is an explicit, identity-bound premise
naming its exact target. Root targets keep the legacy `bridge:accepts` label and
meaning byte for byte (the frozen two-token parser branch); nested targets use
the new `bridge:accepts_at(<agent>,<unit>,<path>)` label, parsed only where the
frozen parser rejects, and need a bridge record. -/
namespace VE.Reports
open VE.Route.Admission (Kind parseLabelRaw QuotedUnit token)
universe u

inductive BridgeLabel
  /-- bridge:accepts(<agent>,<unit>): the frozen two-token branch -/
  | root (agent unit : String)
  /-- bridge:accepts_at(<agent>,<unit>,<path>): the new branch, path = 1(.1)* -/
  | nested (agent unit : String) (depth : Nat)
  deriving DecidableEq, Repr

def BridgeLabel.agent : BridgeLabel → String
  | .root a _ => a
  | .nested a _ _ => a

/-- root a u ↦ ⟨u, 0⟩; nested a u n ↦ ⟨u, n⟩ -/
def BridgeLabel.path : BridgeLabel → Path
  | .root _ u => ⟨u, 0⟩
  | .nested _ u n => ⟨u, n⟩

def BridgeLabel.render : BridgeLabel → String
  | .root a u => "bridge:accepts(" ++ a ++ "," ++ u ++ ")"
  | .nested a u n => "bridge:accepts_at(" ++ a ++ "," ++ u ++ "," ++ ".".intercalate (List.replicate n "1") ++ ")"

/-- A wire path `1(.1)*`: the number of descents. -/
def parsePath (p : String) : Option Nat :=
  let parts := p.splitOn "."
  if parts.all (· == "1") then some parts.length else none

def parseNested (s : String) : Option BridgeLabel :=
  if s.startsWith "bridge:accepts_at(" && s.endsWith ")" then
    match ((s.drop 18).dropRight 1).splitOn "," with
    | [a, u, p] => if token a && token u then (parsePath p).map (.nested a u) else none
    | _ => none
  else none

/-- Root case: exactly `VE.Route.Admission.parseLabelRaw`'s bridge branch; the
nested branch runs only on strings the frozen parser rejects. -/
def parseBridge (s : String) : Option BridgeLabel :=
  match parseLabelRaw s with
  | some (.bridge a u) => some (.root a u)
  | some _ => none
  | none => parseNested s

/-- The holder rule: a report node's holder must match; an assessment node's
accepting agent is unrestricted (W2's agentMatches for hedged kinds); no other
node is a target. -/
def HolderOk (D : ReportDoc) (p : Path) (a : String) : Prop := isAssessmentAt D p = true ∨ holderAt D p = some a

def BridgeAdmitted (D : ReportDoc) (leaf : VE.Graph.Claim) : Prop :=
  ∃ l, parseBridge leaf.label = some l ∧ HolderOk D l.path l.agent ∧ bridgeFormula D l.path = some leaf.formula ∧
    envAt D l.path = some D.E ∧
    (match l with | .root .. => True | .nested _ u n => ∃ b ∈ D.bridges, b.target = ⟨u, n⟩)

/-- 3.3: the W2 kind of a content tree; a negated node is transparent. -/
def kindOf : Content → Kind
  | .formula _ => .asserted
  | .norm .. => .norm
  | .definition .. => .definition
  | .report h act _ b _ => .attributed h act.name (kindOf b)
  | .assessment j _ b => .hedged (match j with | .may => "could" | .probably => "likely") (kindOf b)
  | .negated n => kindOf n

/-- The W2 view of D: the rest of the document, plus each report, assessment or
negated unit with its kind as in 3.3 and, as content, the elaboration of its
root complement. -/
def w2Doc (D : ReportDoc) : VE.Route.Admission.Doc :=
  { D.w2 with
    units := D.w2.units ++ D.units.map (fun u => ⟨u.id, 0, 0, kindOf u.content, bridgeFormula D ⟨u.id, 0⟩⟩)
    openTerms := D.w2.openTerms ++ openTerms D }

/-! ## Facts about root paths -/

theorem parentAt_root {D : ReportDoc} (hw : WF D) {u : Unit} (hu : u ∈ D.units) :
    parentAt D u.id 0 = some u.content := by
  simp [parentAt, unitOf_eq hw hu]

theorem envAt_root {D : ReportDoc} (hw : WF D) {u : Unit} (hu : u ∈ D.units) :
    envAt D ⟨u.id, 0⟩ = some D.E := by
  have hst := hw.stmt u hu
  simp only [envAt, scopeAt, scopeAux, parentAt_root hw hu, Option.map_some]
  cases hc : u.content <;> rw [hc] at hst <;> simp_all [Content.isStatement, enterScope, authorScope]

theorem kindOf_quoted {x : Content} (hx : x.isStatement = true) : (kindOf x).quoted = true := by
  cases x with
  | negated n => cases n <;> simp_all [Content.isStatement, Content.isReport, Content.isAssessment, kindOf, Kind.quoted]
  | _ => simp_all [Content.isStatement, kindOf, Kind.quoted]

/-- On a top-level statement the holder rule is W2's `agentMatches`. -/
theorem holder_rule_root {D : ReportDoc} (hw : WF D) {u : Unit} (hu : u ∈ D.units) (a : String) :
    HolderOk D ⟨u.id, 0⟩ a ↔ VE.Route.Admission.agentMatches (kindOf u.content) a = true := by
  have hst := hw.stmt u hu
  unfold HolderOk isAssessmentAt holderAt
  rw [parentAt_root hw hu]
  simp only [Option.bind_some]
  generalize u.content = x at hst ⊢
  cases x with
  | report h act c b lit =>
    simp only [isAssessNode, holderOf, kindOf, VE.Route.Admission.agentMatches, Kind.agent?,
        Bool.false_eq_true, false_or, Option.some.injEq, beq_iff_eq]
    exact eq_comm
  | assessment j a' b =>
    simp [isAssessNode, kindOf, VE.Route.Admission.agentMatches, Kind.agent?]
  | negated n =>
    cases n with
    | report h act c b lit =>
      simp only [isAssessNode, holderOf, kindOf, VE.Route.Admission.agentMatches, Kind.agent?,
        Bool.false_eq_true, false_or, Option.some.injEq, beq_iff_eq]
      exact eq_comm
    | assessment j a' b =>
      simp [isAssessNode, kindOf, VE.Route.Admission.agentMatches, Kind.agent?]
    | _ => simp [Content.isStatement, Content.isReport, Content.isAssessment] at hst
  | _ => simp [Content.isStatement] at hst

theorem unit_of_bridgeFormula {D : ReportDoc} {u : String} {φ : VE.Formula}
    (h : bridgeFormula D ⟨u, 0⟩ = some φ) : ∃ x ∈ D.units, x.id = u := by
  unfold bridgeFormula contentAt parentAt unitOf at h
  cases hf : D.units.find? (·.id == u) with
  | none => simp [hf] at h
  | some x => exact ⟨x, List.mem_of_find?_eq_some hf, findEq hf⟩

/-! ## 5.2 -/

theorem bridge_root_is_legacy (D : ReportDoc) (h : WellFormedReports D = true) (leaf : VE.Graph.Claim)
    (hl : ∃ a u, parseBridge leaf.label = some (.root a u)) :
    BridgeAdmitted D leaf ↔ ∃ a u, parseBridge leaf.label = some (.root a u) ∧
      VE.Route.Admission.QuotedUnit (w2Doc D) a u leaf.formula := by
  have hw := wf_of h
  obtain ⟨a, u, hp⟩ := hl
  constructor
  · rintro ⟨l, hl, hho, hbf, _, _⟩
    rw [hp] at hl; cases hl
    refine ⟨a, u, hp, ?_⟩
    obtain ⟨x, hx, rfl⟩ := unit_of_bridgeFormula hbf
    exact ⟨⟨x.id, 0, 0, kindOf x.content, bridgeFormula D ⟨x.id, 0⟩⟩,
      List.mem_append_right _ (List.mem_map_of_mem hx), rfl, kindOf_quoted (hw.stmt x hx), hbf,
      (holder_rule_root hw hx a).mp hho⟩
  · rintro ⟨a', u', hp', y, hy, hyid, hq, hcont, hag⟩
    rw [hp] at hp'
    simp only [Option.some.injEq, BridgeLabel.root.injEq] at hp'
    obtain ⟨rfl, rfl⟩ := hp'
    rcases List.mem_append.mp hy with hy | hy
    · have := hw.w2quoted y hy
      rw [hq, hcont] at this
      simp at this
    · obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hy
      subst hyid
      exact ⟨.root a x.id, hp, (holder_rule_root hw hx a).mpr hag, hcont, envAt_root hw hx, trivial⟩

theorem parseNested_not_root (s a u : String) : parseNested s ≠ some (.root a u) := by
  intro hp
  unfold parseNested at hp
  split at hp
  · split at hp
    · split at hp
      · simp only [Option.map_eq_some_iff] at hp
        obtain ⟨_, _, h⟩ := hp
        cases h
      · cases hp
    · cases hp
  · cases hp

theorem bridge_root_parse_frozen (s : String) :
    (∃ a u, parseBridge s = some (.root a u)) ↔ (∃ a u, VE.Route.Admission.parseLabelRaw s = some (.bridge a u)) := by
  unfold parseBridge
  cases hr : parseLabelRaw s with
  | none =>
    simp only [reduceCtorEq, exists_const, iff_false, not_exists]
    exact fun a u => parseNested_not_root s a u
  | some l =>
    cases l <;> simp

theorem bridge_nested_label_new (s : String) (hl : ∃ a u n, parseBridge s = some (.nested a u n)) :
    VE.Route.Admission.parseLabelRaw s = none := by
  obtain ⟨a, u, n, hp⟩ := hl
  cases hr : parseLabelRaw s with
  | none => rfl
  | some l =>
    exfalso
    unfold parseBridge at hp
    rw [hr] at hp
    cases l <;> simp at hp

theorem bridge_formula_exact (D : ReportDoc) (h : WellFormedReports D = true) (leaf : VE.Graph.Claim)
    (hb : BridgeAdmitted D leaf) :
    ∃ l, parseBridge leaf.label = some l ∧ bridgeFormula D l.path = some leaf.formula ∧ envAt D l.path = some D.E := by
  obtain ⟨l, hl, _, hbf, he, _⟩ := hb
  exact ⟨l, hl, hbf, he⟩

theorem bridge_kind_rejected (D : ReportDoc) (h : WellFormedReports D = true) (p : Path)
    (hc : (∃ Eq x, contentAt D p = some (.norm Eq x)) ∨ (∃ Eq x st, contentAt D p = some (.definition Eq x st)) ∨
          envAt D p ≠ some D.E) :
    ¬ ∃ leaf l, BridgeAdmitted D leaf ∧ parseBridge leaf.label = some l ∧ l.path = p := by
  rintro ⟨leaf, l, ⟨l', hl', _, hbf, he, _⟩, hl, rfl⟩
  rw [hl] at hl'; cases hl'
  rcases hc with ⟨Eq, x, hc⟩ | ⟨Eq, x, st, hc⟩ | hc
  · simp [bridgeFormula, hc, «elab»] at hbf
  · simp [bridgeFormula, hc, «elab»] at hbf
  · exact hc he

theorem bridge_nested_needs_record (D : ReportDoc) (h : WellFormedReports D = true) (leaf : VE.Graph.Claim)
    (a u : String) (n : Nat)
    (hl : parseBridge leaf.label = some (.nested a u n)) (hb : BridgeAdmitted D leaf) :
    ∃ b ∈ D.bridges, b.target = ⟨u, n⟩ := by
  obtain ⟨l, hl', _, _, _, hm⟩ := hb
  rw [hl] at hl'; cases hl'
  exact hm

theorem bridge_assessment_any_agent (D : ReportDoc) (h : WellFormedReports D = true) (p : Path)
    (hp : isAssessmentAt D p = true) (a a' : String) :
    HolderOk D p a ↔ HolderOk D p a' :=
  ⟨fun _ => Or.inl hp, fun _ => Or.inl hp⟩

theorem bridge_payload_not_belief (D : ReportDoc) (h : WellFormedReports D = true) (u : Unit) (hu : u ∈ D.units)
    (h₁ h₂ c c' : String) (act : Act) (q : VE.Formula) (lit : Option String)
    (hb : u.content = .report h₁ act c (.report h₂ .believes c' (.formula q) none) lit) :
    bridgeFormula D ⟨u.id, 0⟩ = «elab» D (.report h₂ .believes c' (.formula q) none) ∧
    bridgeFormula D ⟨u.id, 1⟩ = some q ∧ «elab» D (.report h₂ .believes c' (.formula q) none) ≠ some q := by
  have hw := wf_of h
  have hp0 := parentAt_root hw hu
  refine ⟨?_, ?_, ?_⟩
  · simp [bridgeFormula, contentAt, hp0, hb, complementOf]
  · have hp1 : parentAt D u.id 1 = some (.report h₂ .believes c' (.formula q) none) := by
      simp only [parentAt] at hp0 ⊢
      rw [hp0, hb]; rfl
    simp [bridgeFormula, contentAt, hp1, complementOf, «elab»]
  · have ho : Occurs D (.report h₂ .believes c' (.formula q) none) := ⟨u, hu, by rw [hb]; exact body_mem_report⟩
    have hq : q.WellFormed D.E [] := occurs_formula_wellFormed hw (occurs_sub ho body_mem_report)
    cases hs : holderSort D h₂ with
    | none => simp [«elab», hs]
    | some s =>
      simp only [«elab», hs, Option.map_some, ne_eq, Option.some.injEq]
      intro he
      rw [← he] at hq
      obtain ⟨s', hs', _⟩ := hq
      rw [fresh_pred hw (reportName_mem (report_key_mem ho hs))] at hs'
      cases hs'

theorem bridge_through_negation (D : ReportDoc) (h : WellFormedReports D = true) (u : Unit) (hu : u ∈ D.units)
    (n : Content) (hb : u.content = .negated n) :
    contentAt D ⟨u.id, 0⟩ = complementOf n := by
  simp [contentAt, parentAt_root (wf_of h) hu, hb, complementOf]

end VE.Reports
