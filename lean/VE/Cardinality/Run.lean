import VE.Cardinality.Wire
import VE.Cardinality.Theorems

/-! Cardinality certificates and the case runner (docs/spec/quantities.md 4.1–4.3).

A problem (premises and conclusion) is decoded statement by statement, then checked against P1–P3, then erased into
W6a. A certificate is bound twice: to the cardinality identities of the statements, and, as a W6a certificate, to
the regenerated problem's W6a identities in the projection's environment (`CardEnv.w6`); its order trace is replayed
by the frozen checker on that problem (`checkCertificate_sound`). A claimed region table or erased problem must be
the regenerated one. The runner answers the case kinds `admission` and `certificate`. -/
namespace VE.Cardinality.Wire
universe v
open Lean
open VE.Bridge (stringField)
open VE.Time (QFormula)

/-- P1–P3 (spec 4.2): counted sorts, predicates per counted sort, then W6a's aggregate node limit on the erased
problem. -/
def problemChecks (E : CEnv) (ps : List CFormula) (c : CFormula) : Except String Unit := do
  problemLimits E (c :: ps)
  VE.Time.Wire.quantityLimits.aggregate ((erasedProblem E ps c).2 :: (erasedProblem E ps c).1)

/-- The regenerated problem's W6a identities (annotated, core) in the projection's environment, premises first. -/
def erasedIds (w : CardEnv) (ps : List CFormula) (c : CFormula) :
    Except String (List (String × String) × (String × String)) := do
  pure (← (erasedProblem w.env ps c).1.mapM (VE.Time.Wire.statementIds w.w6),
    ← VE.Time.Wire.statementIds w.w6 (erasedProblem w.env ps c).2)

def stale : String := "cardinality certificate is stale or bound to different statements"

/-- The problem's limits, the binding to the cardinality statements, W6a's two bindings to the regenerated problem,
the replay's step limit, then the frozen order replay of the erased problem. -/
def checkCertificate {w : CardEnv} (ps : List (CAdmission w)) (c : CAdmission w) (cert : CardCertificate) :
    Except String Bool :=
  match problemChecks w.env (ps.map (·.formula)) c.formula, erasedIds w (ps.map (·.formula)) c.formula with
  | .error e, _ => .error e
  | .ok _, .error e => .error e
  | .ok _, .ok (pids, cid) =>
    if !(cert.environmentId == w.environmentId && cert.premiseIds == ps.map (·.meaningId) &&
        cert.conclusionId == c.meaningId) then .error stale
    else if !(cert.w6.environmentId == w.w6.environmentId && cert.w6.premiseIds == pids.map (·.1) &&
        cert.w6.conclusionId == cid.1) then .error VE.Time.Wire.staleW6
    else if !(cert.w6.core.environment_id == w.w6.targetId &&
        cert.w6.core.premise_meaning_ids == pids.map (·.2) && cert.w6.core.conclusion_meaning_id == cid.2) then
      .error VE.Time.Wire.staleCore
    else if VE.Route.Steps.order cert.w6.core.trace > VE.Route.Steps.maxSteps then .error VE.Route.Steps.stepLimit
    else .ok (VE.Order.Tableau.checkCertificate (w.env.elab (c.formula :: ps.map (·.formula))).erase
      ((erasedProblem w.env (ps.map (·.formula)) c.formula).1.map QFormula.erase)
      (erasedProblem w.env (ps.map (·.formula)) c.formula).2.erase cert.w6.core)

/-- An accepted certificate is a W6a certificate of the regenerated problem, bound to the cardinality identities. -/
theorem checkCertificate_sound {w : CardEnv} (ps : List (CAdmission w)) (c : CAdmission w)
    (cert : CardCertificate) (h : checkCertificate ps c cert = .ok true) :
    cert.environmentId = w.environmentId ∧ cert.premiseIds = ps.map (·.meaningId) ∧
      cert.conclusionId = c.meaningId ∧ CEntails.{v} w.env (ps.map (·.formula)) c.formula := by
  unfold checkCertificate at h
  split at h
  · cases h
  · cases h
  split at h
  · cases h
  rename_i hb
  split at h
  · cases h
  split at h
  · cases h
  split at h
  · cases h
  simp only [Bool.not_eq_true', Bool.not_eq_false, Bool.and_eq_true, beq_iff_eq] at hb
  refine ⟨hb.1.1, hb.1.2, hb.2, ?_⟩
  have hps : ∀ a ∈ ps.map (·.formula), Admitted w.env a := fun a ha => by
    obtain ⟨b, _, rfl⟩ := List.mem_map.mp ha
    exact admits_sound _ _ b.admitted
  have hc := admits_sound _ _ c.admitted
  have hadm := erasedProblem_admitted w.env w.wf _ _ hps hc
  exact cardinality_elab_sound w.env w.wf _ _ hps hc
    (VE.Time.tentails_of_entails (fun a ha => hadm a (List.mem_append_left _ ha)) (hadm _ (by simp))
      (VE.Order.Tableau.checkCertificate_sound _ _ _ _ (Except.ok.inj h)))

/-! ## The runner -/

def statementJson {w : CardEnv} (a : CAdmission w) : Json :=
  Json.mkObj [("meaning_id", .str a.meaningId), ("formula", encode a.formula)]

/-- The region table: each counted sort's predicates in first-use order, and every region constant with its sort
and bits (the bit of each of those predicates, in that order). -/
def regionsJson (E : CEnv) (fs : List CFormula) : Json :=
  Json.mkObj [("predicates", Json.mkObj ((countedSorts fs).map fun s => (s, toJson (predsOn E fs s)))),
    ("constants", toJson ((regionTable E fs).map fun e =>
      Json.mkObj [("constant", .str e.1), ("sort", .str e.2.1), ("bits", .str (bitString e.2.2))]))]

/-- The regenerated problem, each formula with its W6a identities. -/
def erasedJson (w : CardEnv) (ps : List CFormula) (c : CFormula) : Except String Json := do
  let (pids, cid) ← erasedIds w ps c
  let one := fun (q : QFormula) (ids : String × String) => Json.mkObj [("Q", VE.Time.Wire.encQ q),
    ("core", VE.Time.Wire.encCore q.erase), ("meaning_id", .str ids.1), ("core_meaning_id", .str ids.2)]
  pure (Json.mkObj [("premises", Json.arr (((erasedProblem w.env ps c).1.zip pids).map fun x => one x.1 x.2).toArray),
    ("conclusion", one (erasedProblem w.env ps c).2 cid)])

/-- A claimed region table or erased problem must be the regenerated one (spec 4.1). -/
def claimed (j : Json) (field : String) (regenerated : Json) (text : String) : Except String Unit := do
  if let .ok claim := j.getObjVal? field then
    let same ← match VE.Time.Wire.canonicalText claim with
      | .ok t => pure (t == (← VE.Time.Wire.canonicalText regenerated))
      | .error _ => pure false
    unless same do throw text

def runCase (j : Json) : Except String Json := do
  let id ← stringField j "id"
  let kind ← match j.getObjVal? "kind" with
    | .ok k => k.getStr?
    | .error _ => pure "admission"
  unless kind == "admission" || kind == "certificate" do throw s!"unknown case kind {kind}"
  let w ← decodeEnvironment (← j.getObjVal? "environment")
  let ps ← (← (← j.getObjVal? "premises").getArr?).toList.mapM (decodeStatement w)
  let c ← decodeStatement w (← j.getObjVal? "conclusion")
  let fs := ps.map (·.formula)
  problemChecks w.env fs c.formula
  let regions := regionsJson w.env (c.formula :: fs)
  let erased ← erasedJson w fs c.formula
  claimed j "regions" regions "region table differs from the regenerated one"
  claimed j "erased" erased "erased problem differs from the regenerated one"
  let answer := [("environment_id", .str w.environmentId), ("w6_environment_id", .str w.w6.environmentId),
    ("w6_target_environment_id", .str w.w6.targetId), ("premises", Json.arr (ps.map statementJson).toArray),
    ("conclusion", statementJson c)]
  if kind == "admission" then
    return VE.Time.Wire.ok id (answer ++ [("regions", regions), ("erased", erased)])
  let valid ← checkCertificate ps c (← decodeCertificate (← j.getObjVal? "certificate"))
  pure (VE.Time.Wire.ok id (("valid", .bool valid) :: answer))

def runCaseReported (j : Json) : Json :=
  match runCase j with
  | .ok result => result
  | .error message => Json.mkObj ([("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)] ++
      (if (j.getObjValD "kind").getStr?.toOption == some "certificate" then [("valid", .bool false)] else []))

end VE.Cardinality.Wire
