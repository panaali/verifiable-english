-- ve-layer: 4 (states theorems on Risk.Run.runCase, a layer-4 runner: kb-risk)
import VE.Risk.Run

/-! Runner theorems of the `risk` route's keyed case kinds (kb-risk; docs/spec/kernel-boundary.md 1.2, 1.3, 7).

The five frozen keys send two kinds on this route (docs/kernel/kb-risk/CALLS.md): `risk-elaborate` and
`risk-decision`. Each theorem below is about `VE.Risk.Run.runCase` itself: its hypotheses are `runCase j = .ok
answer`, the case kind and `usesRiskPath j = true`, and its conclusion names the decoders that read the case's
fields and states every field of `answer` a key reads as a Lean definition applied to the decoded objects.

* `risk_elaborate_wire_sound`: the answer is a closed field list whose `risk_premises` are the labelled
  `riskPremises` of the decoded document (`riskPremiseLabels` zipped with `riskPremises`); its `risk:class` rows
  are the decoded harm classes and its `risk:order` rows the order literals of every class pair
  (`riskPremiseRows_class`, `riskPremiseRows_order`).
* `risk_decision_wire_sound`: the answer is the CONFLICT answer exactly when `scenarioConflict` finds one on the
  decision model, otherwise the tables of `regenerate`, the statuses of `statuses`, the clear actions, the cited
  estimates and the unexamined possible cells; with the conclusion of `risk_wire_scenario_sound` (decoders,
  admission, validation, margin limit) and of `regenerate_sound` (what a `might` and a `leads` cell mean over the
  completed cases).
* `runCaseReported_ok`: the service's row is `runCase`'s answer on the risk path.

The answer shapes are written out inside the two theorems, not as definitions: a definition a statement reads is
trusted (`S`, docs/TRUST-MAP.md section 2) and this item adds no trusted Lean (kb-8's choice, docs/kernel/kb-8/
REPORT.md note 2); the verdict word `CONFLICT` likewise stays in a statement (kernel-boundary section 3 counts a
definition holding it as a verdict writer). Fields no key reads (renderings such as `text`, `worst_cases`,
`margins`, `legend`) are stated by key only: the answer is a closed list, so a stated field cannot be overridden
by an unstated one (kb-7 F1). A refusal (`.error`) asserts nothing. Kinds no key calls (`risk-conflict`,
`risk-followable`, `risk-audit`, `risk-certificate`) get no runner theorem here (docs/kernel/kb-risk/REPORT.md). -/
namespace VE.Risk.Run
open Lean
open VE.Norms
open Wire (RiskSource decodeRiskSource)
open VE.Order.ProfileGate (bind_ok)

/-! ## The labelled rows the keys read -/

theorem zip_const_filter_ne {β : Type} (l p : String) (xs : List β) (h : (l == p) = false) :
    ((xs.map fun _ => l).zip xs).filter (·.1 == p) = [] := by
  induction xs with
  | nil => rfl
  | cons x xs ih => simp only [List.map_cons, List.zip_cons_cons, List.filter_cons, h]; exact ih

theorem zip_const_filter_self {β : Type} (l : String) (xs : List β) :
    ((xs.map fun _ => l).zip xs).filter (·.1 == l) = xs.map fun x => (l, x) := by
  induction xs with
  | nil => rfl
  | cons x xs ih => simp only [List.map_cons, List.zip_cons_cons, List.filter_cons, beq_self_eq_true,
      ↓reduceIte, ih]

/-- The `risk:class` rows are the decoded harm classes, in order: `class(h, c)` for each `(h, c)`. -/
theorem riskPremiseRows_class (R : RiskDoc) :
    ((riskPremiseLabels R).zip (riskPremises R)).filter (·.1 == "risk:class") =
      R.risk.harmClasses.map fun p => ("risk:class", .binary classPred (.const p.1) (.const p.2)) := by
  unfold riskPremiseLabels riskPremises
  simp only [List.zip_cons_cons, List.filter_cons]
  rw [List.zip_append (by simp), List.filter_append, List.zip_append (by simp), List.filter_append,
    List.zip_cons_cons, List.filter_cons, zip_const_filter_ne _ _ _ (by decide),
    zip_const_filter_ne _ _ _ (by decide), zip_const_filter_self]
  simp [classFacts]

/-- The `risk:order` rows are the order literals of every class pair, in order: `more_severe(a, b)` for a pair
of the closed order, its negation otherwise. -/
theorem riskPremiseRows_order (R : RiskDoc) :
    ((riskPremiseLabels R).zip (riskPremises R)).filter (·.1 == "risk:order") =
      (classPairs R).map fun p => ("risk:order", orderLiteral R p) := by
  unfold riskPremiseLabels riskPremises
  simp only [List.zip_cons_cons, List.filter_cons]
  rw [List.zip_append (by simp), List.filter_append, List.zip_append (by simp), List.filter_append,
    List.zip_cons_cons, List.filter_cons, zip_const_filter_ne _ _ _ (by decide),
    zip_const_filter_self, zip_const_filter_ne _ _ _ (by decide)]
  simp [orderTable]

/-! ## The route's runner -/

/-- The risk route's answer to a `risk-elaborate` case: the case's own decoder reads the environment and the
document into a well-formed risk source, and the answer is exactly this closed field list for it: `status` is
`ok`, `environment_id` and `document_hash` are the decoded policy pair, `risk_premises` lists the labelled
`riskPremises` (label and encoded formula, in order), whose `risk:class` rows are the decoded harm classes, in
order, and whose `risk:order` rows are the order literals of every pair of classes, and `unranked_severities`
the pairs of `unrankedSeverities`; the other fields (the regenerated vocabulary, legend, inlined norms, the
alternatives' premises, followability formulas, W1's regenerated fields and, when the case asks for it,
`coverage`) by key. -/
theorem risk_elaborate_wire_sound (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "risk-elaborate") (hn : usesRiskPath j = true) :
    ∃ (id : String) (src : RiskSource),
      VE.Bridge.stringField j "id" = .ok id ∧
      Wire.decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document") = .ok src ∧
      WellFormedRisk src.R = true ∧
      (∃ (eRisk legend inlined alternatives base followable unmapped : Json)
          (norms coverage : List (String × Json)),
        norms.map (·.1) = ["order", "background", "premises", "conflict_targets", "fragment"] ∧
        (coverage = [] ∨ ∃ c, coverage = [("coverage", c)]) ∧
        answer = ok id ([("environment_id", .str src.R.policy.1), ("document_hash", .str src.R.policy.2),
          ("e_risk", eRisk), ("legend", legend),
          ("risk_premises", Json.arr (((riskPremiseLabels src.R).zip (riskPremises src.R)).map fun p =>
            Json.mkObj [("label", .str p.1), ("ast", Wire.enc p.2)]).toArray),
          ("unranked_severities", toJson ((Wire.unrankedSeverities src.R).map fun p => [p.1, p.2])),
          ("inlined", inlined), ("alternatives", alternatives), ("base_premises", base),
          ("followable", followable), ("unmapped_obligations", unmapped)] ++ norms ++ coverage)) ∧
      ((riskPremiseLabels src.R).zip (riskPremises src.R)).filter (·.1 == "risk:class") =
        src.R.risk.harmClasses.map (fun p => ("risk:class", .binary classPred (.const p.1) (.const p.2))) ∧
      ((riskPremiseLabels src.R).zip (riskPremises src.R)).filter (·.1 == "risk:order") =
        (classPairs src.R).map (fun p => ("risk:order", orderLiteral src.R p)) := by
  have _ := hn
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := bind_ok h
  obtain ⟨kind, hkind, h⟩ := bind_ok h
  have heq : kind = "risk-elaborate" := by rw [hkind] at hk; cases hk; rfl
  subst heq
  simp only [show ("risk-elaborate" == "admission") = false from by decide, beq_self_eq_true,
    Bool.false_eq_true, ↓reduceIte] at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨r, hr, h⟩ := bind_ok h
  cases h
  unfold runElaborate at hr
  obtain ⟨src, hs, hr⟩ := bind_ok hr
  simp only [pure, Except.pure, Except.ok.injEq] at hr
  subst hr
  refine ⟨id, src, hid, hs, src.wf, ⟨?e1, ?e2, ?e3, ?e4, ?e5, ?e6, ?e7,
    VE.Norms.Wire.regenerated (VE.Alternatives.inlineTree (toAlt src.R)), ?covl, rfl, ?cov, ?eq⟩,
    riskPremiseRows_class src.R, riskPremiseRows_order src.R⟩
  case eq =>
    simp only [Wire.regenerated, List.append_assoc]
    rfl
  case cov =>
    split
    · exact Or.inr ⟨_, rfl⟩
    · exact Or.inl rfl

/-- The risk route's answer to a `risk-decision` case. The case's own decoders read the source
(`decodeRiskSource`), the decision entry (`decodeEntry`) and the supplied entries (`decodeSupplied`); the record
`d` is the one `admitDecision` admits from them, valid and within the candidate limit (the conclusion of
`risk_wire_scenario_sound`). For them the answer is exactly the CONFLICT answer, with the target and tuple, when
`scenarioConflict` finds a conflict on the decision model; otherwise it is this closed field list: the `might`
table lists `regenerate`'s `might` cells (alternative and harm, in order; a row's only other field is its
`witness`), the `leads` table its `leads` cells, `statuses` the statuses of `statuses` with their firing rules,
`lines.unexamined_possible` the cells no record addresses whose completion is `⊤`, `clear` the clear
alternatives and `conditional_on` the cited entries. Each table means what `regenerate_sound` says: over the
alternatives and harms of the record, a cell is `might` when some completed case of the record has the harm,
and `leads` when every completed case has it. -/
theorem risk_decision_wire_sound (j answer : Json) (h : runCase j = .ok answer)
    (hk : VE.Route.Run.caseKind j = .ok "risk-decision") (hn : usesRiskPath j = true) :
    ∃ (id : String) (src : RiskSource) (entry : Entry) (supplied : Log) (d : Decision),
      VE.Bridge.stringField j "id" = .ok id ∧
      Wire.decodeRiskSource (j.getObjValD "environment") (j.getObjValD "document") = .ok src ∧
      Wire.decodeEntry (j.getObjValD "decision") = .ok entry ∧
      Wire.decodeSupplied (j.getObjValD "entries") = .ok supplied ∧
      admitDecision src.R entry supplied = .ok d ∧
      WellFormedRisk src.R = true ∧ validateDecision src.R d = .ok () ∧ marginLimit src.R d = .ok () ∧
      (match VE.Alternatives.scenarioConflict (toAlt src.R) (decisionModel src.R d) with
        | some (t, vs) => ∃ text : String, answer = ok id
            [("environment_id", .str src.R.policy.1), ("document_hash", .str src.R.policy.2),
             ("decision_record_id", .str (decisionRecordId entry)),
             ("verdict", .str "CONFLICT"), ("target", .str t.1), ("tuple", toJson (vs.map (·.2))),
             ("text", .str text)]
        | none => ∃ (witness : String × String → List (String × Json))
            (worst margins invalid conflict ruledOut points defaulted dilemmas legend : Json) (text : String),
          (∀ c, ∀ kv ∈ witness c, kv.1 = "witness") ∧
          answer = ok id
            [("environment_id", .str src.R.policy.1), ("document_hash", .str src.R.policy.2),
             ("decision_record_id", .str (decisionRecordId entry)),
             ("tables", Json.mkObj [
                ("might", Json.arr ((regenerate src.R d).might.map fun c =>
                  Json.mkObj ([("alternative", .str c.1), ("harm", .str c.2)] ++ witness c)).toArray),
                ("leads", Json.arr ((regenerate src.R d).leads.map fun c =>
                  Json.mkObj [("alternative", .str c.1), ("harm", .str c.2)]).toArray)]),
             ("statuses", Json.arr ((statuses src.R d).map fun p =>
                Json.mkObj [("alternative", .str p.1), ("permitted", .bool p.2.permitted),
                  ("required", .bool p.2.required), ("clear", .bool p.2.clear),
                  ("rules", toJson (firingRules src.R d p.1)),
                  ("by_default", .bool (firingRules src.R d p.1).isEmpty)]).toArray),
             ("worst_cases", worst), ("margins", margins), ("record_invalid", invalid),
             ("record_conflict", conflict),
             ("lines", Json.mkObj [
                ("unexamined_possible", toJson (((cellsOf src.R d).filter fun c =>
                  !addressed d c.1 c.2 && completion src.R c.2 == .top).map fun c => s!"{c.1}/{c.2}")),
                ("assumed_ruled_out", ruledOut), ("point_estimates", points), ("default_decided", defaulted),
                ("dilemmas", dilemmas)]),
             ("legend", legend),
             ("clear", toJson (((statuses src.R d).filter (·.2.clear)).map (·.1))),
             ("conditional_on", toJson (d.cited.map (·.id))), ("text", .str text)]) ∧
      (∀ a ∈ names d, ∀ hm ∈ harms src.R,
        ((a, hm) ∈ (regenerate src.R d).might ↔ ∃ v H, Completed src.R d v H ∧ H a hm = true) ∧
        ((a, hm) ∈ (regenerate src.R d).leads ↔ ∀ v H, Completed src.R d v H → H a hm = true)) := by
  have _ := hn
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := bind_ok h
  obtain ⟨kind, hkind, h⟩ := bind_ok h
  have heq : kind = "risk-decision" := by rw [hkind] at hk; cases hk; rfl
  subst heq
  simp only [show ("risk-decision" == "admission") = false from by decide,
    show ("risk-decision" == "risk-elaborate") = false from by decide, beq_self_eq_true,
    Bool.false_eq_true, ↓reduceIte] at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨r, h, hr⟩ := bind_ok h
  cases hr
  unfold runDecision at h
  obtain ⟨src, hs, h⟩ := bind_ok h
  obtain ⟨entry, he, h⟩ := bind_ok h
  obtain ⟨supplied, hsu, h⟩ := bind_ok h
  obtain ⟨d, hd, h⟩ := bind_ok h
  dsimp only at h
  split at h
  · obtain ⟨_, he, _⟩ := bind_ok h
    cases he
  rename_i hv
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, hm, h⟩ := bind_ok h
  obtain ⟨res, hres, h⟩ := bind_ok h
  have hsound := risk_wire_scenario_sound j res hres
  rcases res with ⟨src', entry', supplied', d', tables, conflict, sts, margin, ri, rc⟩
  obtain ⟨hs', _, he', hsu', hd', _, _, htab, hconf, hstat, -, -⟩ := hsound
  dsimp only at hs' he' hsu' hd' htab hconf hstat h
  rw [hs] at hs'; cases hs'
  rw [he] at he'; cases he'
  rw [hsu] at hsu'; cases hsu'
  rw [hd] at hd'; cases hd'
  subst htab hconf
  refine ⟨id, src, entry, supplied, d, hid, hs, he, hsu, hd, src.wf, hv, hm, ?_,
    fun a ha hm hh => regenerate_sound src.R src.wf d hv a hm ha hh⟩
  rcases hc : VE.Alternatives.scenarioConflict (toAlt src.R) (decisionModel src.R d) with _ | ⟨⟨t, vs⟩⟩
  · simp only [hc] at h
    obtain rfl := hstat hc
    cases h
    dsimp only
    refine ⟨fun c => match (regenerate src.R d).witness.find? (·.1 == c) with
      | some (_, v) => [("witness", caseJson src.R (box src.R d) v)]
      | none => [], _, _, _, _, _, _, _, _, _, _, ?_, rfl⟩
    intro c kv hkv
    dsimp only at hkv
    split at hkv
    · simp only [List.mem_singleton] at hkv
      subst hkv
      rfl
    · cases hkv
  · simp only [hc] at h
    cases h
    dsimp only
    exact ⟨_, rfl⟩

/-- On the risk path the service's row is `runCase`'s answer. -/
theorem runCaseReported_ok (j answer : Json) (hn : usesRiskPath j = true) (h : runCase j = .ok answer) :
    runCaseReported j = answer := by
  simp [runCaseReported, hn, h]

end VE.Risk.Run
