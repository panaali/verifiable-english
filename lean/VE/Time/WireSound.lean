import VE.Time.Document

/-! Wire theorems of the `quantity` service mode (kernel boundary, KB-8).

`VE.Time.Wire.runCase j more` answers one case of the mode. For each case kind whose answer carries
a verdict there is one theorem here, with the hypothesis that the runner accepted (`runCase j more =
.ok answer`) and the case's `kind`; its conclusion names what the case's own decoders read from it
(the environment, the statements, the model, the certificate, the document), says the answer is
exactly a fixed list of fields over them (no open tail: every key is named), and ends in the proved
checker's soundness theorem:

* `admission` (also a case with no `kind`): the statement is `Admitted` and its core well formed
  (`Admission.sound`); with a model, the reported `value` is the core's truth in the decoded model
  (`evalB_sorted_sound`). The `evaluations` count is the evaluator's work: nothing is stated about it.
* `countermodel`: `refutes` is whether the decoded model makes every premise core true and the
  conclusion core false (`refutesB_sorted_sound`).
* `certificate`: `valid = true` means the certificate is bound to the statements and they are
  entailed over every admissible tagged structure (`checkW6Certificate_sound`); `valid = false`
  asserts nothing (a rejected certificate is no refutation).
* `document` (on `runCase j Document.extension`): the decoded document is admitted with the
  properties of `Document.admitDecoded_sound`, and the answer is its report.

A budget that runs out ends the case with an error, never an answer, so no theorem covers it. The
case kinds that carry no verdict (`count`: `runCount`; the conversions `day`, `civil`, `lower` and
`render`: `runConversion`) are listed in `tools/kernel-paths.json` as non-verdict exits.

The conclusions name decoders, the answer's fields and the semantic relations (`Admitted`,
`Formula.eval`, `TEntails`, the document's admission relations), never an executable evaluator. -/
namespace VE.Time.Wire
universe v
open Lean
open VE.Bridge (stringField)
open VE.Order.ProfileGate (bind_ok)

/-- KB-8, `admission` (the default kind): an answer reports the decoded statement's regenerated
artifacts and identities; the statement is admitted and its core well formed; with a `model` field,
the reported `value` is the core's truth in the decoded model, and without one there is no value. -/
theorem quantity_admission_wire_sound (j answer : Json) (more : Extension)
    (h : runCase j more = .ok answer)
    (hk : j.getObjVal? "kind" = .ok (.str "admission") ∨ ∃ e, j.getObjVal? "kind" = .error e) :
    ∃ (id : String) (env : Json) (w : W6Env) (quantity : Json) (a : Admission w)
      (value : List (String × Json)),
      stringField j "id" = .ok id ∧
      j.getObjVal? "environment" = .ok env ∧ decodeEnvironment env = .ok w ∧
      j.getObjVal? "quantity" = .ok quantity ∧ decodeQuantity w quantity = .ok a ∧
      answer = ok id ([("assurance", .str "lean-admitted"), ("Q", a.Q), ("core", a.core),
        ("meaning_id", .str a.meaningId), ("core_meaning_id", .str a.coreId),
        ("environment_id", .str w.environmentId), ("target_environment_id", .str w.targetId)] ++
        value) ∧
      Admitted w.vocab.env [] a.formula ∧ a.formula.erase.WellFormed w.vocab.env.erase [] ∧
      ((∃ e, j.getObjVal? "model" = .error e) ∧ value = [] ∨
        ∃ (model : Json) (d : VE.Order.ModelData VE.Order.Wire.Entity) (b : Bool) (work : Nat),
          j.getObjVal? "model" = .ok model ∧
          VE.Route.Decode.decodeOrderModel w.vocab.core model = .ok d ∧
          value = [("value", .bool b), ("evaluations", toJson work)] ∧
          b = a.formula.erase.eval d.toModel []) := by
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := bind_ok h
  rcases hk with hk | ⟨e, hk⟩ <;> simp only [hk, Json.getStr?, pure_bind] at h
  all_goals
    rw [if_neg (by decide)] at h
    obtain ⟨env, henv, h⟩ := bind_ok h
    obtain ⟨w, hw, h⟩ := bind_ok h
    split at h
    · rename_i model hmj
      obtain ⟨quantity, hqj, h⟩ := bind_ok h
      obtain ⟨a, ha, h⟩ := bind_ok h
      obtain ⟨d, hd, h⟩ := bind_ok h
      split at h
      · rename_i b work hb
        cases h
        exact ⟨id, env, w, quantity, a, _, hid, henv, hw, hqj, ha, rfl, (Admission.sound a).1,
          (Admission.sound a).2,
          .inr ⟨model, d, b, work, hmj, hd, rfl, evalB_sorted_sound d (predicateNames w) _ _ _ _ hb⟩⟩
      · cases h
    · rename_i e' hmj
      obtain ⟨quantity, hqj, h⟩ := bind_ok h
      obtain ⟨a, ha, h⟩ := bind_ok h
      cases h
      exact ⟨id, env, w, quantity, a, _, hid, henv, hw, hqj, ha, rfl, (Admission.sound a).1,
        (Admission.sound a).2, .inl ⟨⟨e', hmj⟩, rfl⟩⟩

/-- KB-8, `countermodel`: an answer echoes the decoded statements' identities, the statements are
admitted, and `refutes` is whether the decoded model makes every premise's core true and the
conclusion's core false. -/
theorem quantity_countermodel_wire_sound (j answer : Json) (more : Extension)
    (h : runCase j more = .ok answer) (hk : j.getObjVal? "kind" = .ok (.str "countermodel")) :
    ∃ (id : String) (env : Json) (w : W6Env) (premises conclusion model : Json)
      (ps : List (Admission w)) (c : Admission w) (d : VE.Order.ModelData VE.Order.Wire.Entity)
      (refutes : Bool),
      stringField j "id" = .ok id ∧
      j.getObjVal? "environment" = .ok env ∧ decodeEnvironment env = .ok w ∧
      j.getObjVal? "premises" = .ok premises ∧ admissions w premises = .ok ps ∧
      j.getObjVal? "conclusion" = .ok conclusion ∧ decodeQuantity w conclusion = .ok c ∧
      j.getObjVal? "model" = .ok model ∧ VE.Route.Decode.decodeOrderModel w.vocab.core model = .ok d ∧
      answer = ok id [("refutes", .bool refutes),
        ("premise_meaning_ids", toJson (ps.map (·.meaningId))),
        ("conclusion_meaning_id", .str c.meaningId),
        ("core_premise_meaning_ids", toJson (ps.map (·.coreId))),
        ("core_conclusion_meaning_id", .str c.coreId),
        ("environment_id", .str w.environmentId), ("target_environment_id", .str w.targetId)] ∧
      (∀ a ∈ c :: ps, Admitted w.vocab.env [] a.formula) ∧
      refutes = ((ps.map (·.formula.erase)).all (fun f => f.eval d.toModel []) &&
        !c.formula.erase.eval d.toModel []) := by
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := bind_ok h
  simp only [hk, Json.getStr?, pure_bind] at h
  rw [if_neg (by decide)] at h
  obtain ⟨env, henv, h⟩ := bind_ok h
  obtain ⟨w, hw, h⟩ := bind_ok h
  split at h <;> try (exfalso; simp_all; done)
  obtain ⟨premises, hpj, h⟩ := bind_ok h
  obtain ⟨ps, hps, h⟩ := bind_ok h
  obtain ⟨conclusion, hcj, h⟩ := bind_ok h
  obtain ⟨c, hc, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨model, hmj, h⟩ := bind_ok h
  obtain ⟨d, hd, h⟩ := bind_ok h
  split at h
  · rename_i refutes hr
    cases h
    refine ⟨id, env, w, premises, conclusion, model, ps, c, d, refutes, hid, henv, hw, hpj, hps,
      hcj, hc, hmj, hd, rfl, fun a _ => (Admission.sound a).1, ?_⟩
    exact refutesB_sorted_sound d (predicateNames w) _ _ _ _ refutes hr
  · cases h

/-- KB-8, `certificate`: an answer echoes the decoded statements' identities and the statements are
admitted; `valid = true` means the decoded certificate is bound to exactly these annotated
statements and they are entailed over every admissible tagged structure. `valid = false` states
nothing about entailment. -/
theorem quantity_certificate_wire_sound (j answer : Json) (more : Extension)
    (h : runCase j more = .ok answer) (hk : j.getObjVal? "kind" = .ok (.str "certificate")) :
    ∃ (id : String) (env : Json) (w : W6Env) (premises conclusion certificate : Json)
      (ps : List (Admission w)) (c : Admission w) (cert : W6Certificate) (valid : Bool),
      stringField j "id" = .ok id ∧
      j.getObjVal? "environment" = .ok env ∧ decodeEnvironment env = .ok w ∧
      j.getObjVal? "premises" = .ok premises ∧ admissions w premises = .ok ps ∧
      j.getObjVal? "conclusion" = .ok conclusion ∧ decodeQuantity w conclusion = .ok c ∧
      j.getObjVal? "certificate" = .ok certificate ∧ decodeW6Certificate certificate = .ok cert ∧
      answer = ok id [("valid", .bool valid),
        ("premise_meaning_ids", toJson (ps.map (·.meaningId))),
        ("conclusion_meaning_id", .str c.meaningId),
        ("core_premise_meaning_ids", toJson (ps.map (·.coreId))),
        ("core_conclusion_meaning_id", .str c.coreId),
        ("environment_id", .str w.environmentId), ("target_environment_id", .str w.targetId)] ∧
      (∀ a ∈ c :: ps, Admitted w.vocab.env [] a.formula) ∧
      (valid = true →
        cert.environmentId = w.environmentId ∧ cert.premiseIds = ps.map (·.meaningId) ∧
        cert.conclusionId = c.meaningId ∧ TEntails.{v} w.vocab.env (ps.map (·.formula)) c.formula) := by
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := bind_ok h
  simp only [hk, Json.getStr?, pure_bind] at h
  rw [if_neg (by decide)] at h
  obtain ⟨env, henv, h⟩ := bind_ok h
  obtain ⟨w, hw, h⟩ := bind_ok h
  split at h <;> try (exfalso; simp_all; done)
  obtain ⟨premises, hpj, h⟩ := bind_ok h
  obtain ⟨ps, hps, h⟩ := bind_ok h
  obtain ⟨conclusion, hcj, h⟩ := bind_ok h
  obtain ⟨c, hc, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨certificate, hcertj, h⟩ := bind_ok h
  obtain ⟨cert, hcert, h⟩ := bind_ok h
  obtain ⟨valid, hvalid, h⟩ := bind_ok h
  cases h
  refine ⟨id, env, w, premises, conclusion, certificate, ps, c, cert, valid, hid, henv, hw, hpj, hps,
    hcj, hc, hcertj, hcert, rfl, fun a _ => (Admission.sound a).1, ?_⟩
  intro hv
  subst hv
  exact checkW6Certificate_sound.{v} ps c cert hvalid

/-- KB-8, the route's extension (`Document.extension`, which `runCase` hands every kind it does not
know): it answers only `document`, and the answer means what `quantity_document_wire_sound`
states. -/
theorem extension_document_sound (w : W6Env) (id kind : String) (j answer : Json)
    (h : Document.extension w id kind j = .ok answer) :
    kind = "document" ∧
    ∃ (document : Json) (D : Document.QDoc w) (nodes : List (Document.QNode w)) (root : String)
      (res : Document.Admitted w) (report : Json) (reportId : String),
      j.getObjVal? "document" = .ok document ∧
      Document.decodeDocument w document = .ok (D, nodes, root) ∧
      (res.doc = D ∧ res.nodes = nodes ∧ res.root.name = root ∧
        (∃ n ∈ nodes, n.name = root ∧ n.adm = res.root.adm ∧ n.label = res.root.label) ∧
        (∀ n ∈ nodes, Document.NodeAdmitted D n) ∧
        (∀ x ∈ res.root.assumptions, ∃ n ∈ nodes, n.deduction = none ∧
          (n.name, n.adm, n.label) = x ∧ Document.LeafAdmitted D n) ∧
        Document.CitationsClosed D res.root ∧ Document.ChoicesCompatible res.root ∧
        Document.Entry.Sound.{v} res.root ∧ Document.Entry.SoundOverLeaves.{v} res.root) ∧
      report = Json.mkObj [("root", Document.claimJson res.root.name res.root.adm res.root.label),
        ("assumptions",
          Json.arr (res.root.assumptions.map (fun x => Document.claimJson x.1 x.2.1 x.2.2)).toArray)] ∧
      VE.CertificateWire.digest s!"ve-report-{VE.Route.Wire.identityVersion w.profiles}\n"
        (Json.mkObj [("environment_id", .str w.environmentId), ("document", document),
          ("report", report)]) = .ok reportId ∧
      answer = ok id [("admitted", .bool true), ("assurance", .str "lean-admitted"),
        ("report", report), ("report_id", .str reportId), ("environment_id", .str w.environmentId),
        ("kinds", Json.arr (D.units.map (fun u => VE.Route.Admission.renderKind u.kind)).toArray)] := by
  unfold Document.extension at h
  split at h
  · rename_i hkind
    refine ⟨by simpa using hkind, ?_⟩
    unfold Document.runDocument at h
    obtain ⟨document, hdj, h⟩ := bind_ok h
    obtain ⟨res, hres, h⟩ := bind_ok h
    obtain ⟨reportId, hid, h⟩ := bind_ok h
    cases h
    unfold Document.admitDocument at hres
    obtain ⟨⟨D, nodes, root⟩, hdec, hadm⟩ := bind_ok hres
    obtain ⟨hd, hn, hr, hroot, hnodes, hleaves, hcl, hc, hs, hso⟩ :=
      Document.admitDecoded_sound.{v} D nodes root res hadm
    refine ⟨document, D, nodes, root, res, _, reportId, hdj, hdec,
      ⟨hd, hn, hr, hroot, hnodes, hleaves, hcl, hc, hs, hso⟩, rfl, hid, ?_⟩
    rw [hd]
  · cases h

/-- KB-8, `document` (on the mode's own runner, `runCase j Document.extension`): the case's
`document` field decodes to a document, its graph nodes and its root; their admission `res` has
the properties of `Document.admitDecoded_sound` (the root is a submitted node; every node is
admitted; every assumption is a submitted leaf; citations are closed; choices are compatible; the
root holds in every admissible tagged structure where its assumptions hold); and the answer is
exactly the report of `res`, the report's identity (the digest of the environment id, the
document and the report) and the units' kinds. -/
theorem quantity_document_wire_sound (j answer : Json)
    (h : runCase j Document.extension = .ok answer)
    (hk : j.getObjVal? "kind" = .ok (.str "document")) :
    ∃ (id : String) (env : Json) (w : W6Env),
      stringField j "id" = .ok id ∧
      j.getObjVal? "environment" = .ok env ∧ decodeEnvironment env = .ok w ∧
    ∃ (document : Json) (D : Document.QDoc w) (nodes : List (Document.QNode w)) (root : String)
      (res : Document.Admitted w) (report : Json) (reportId : String),
      j.getObjVal? "document" = .ok document ∧
      Document.decodeDocument w document = .ok (D, nodes, root) ∧
      (res.doc = D ∧ res.nodes = nodes ∧ res.root.name = root ∧
        (∃ n ∈ nodes, n.name = root ∧ n.adm = res.root.adm ∧ n.label = res.root.label) ∧
        (∀ n ∈ nodes, Document.NodeAdmitted D n) ∧
        (∀ x ∈ res.root.assumptions, ∃ n ∈ nodes, n.deduction = none ∧
          (n.name, n.adm, n.label) = x ∧ Document.LeafAdmitted D n) ∧
        Document.CitationsClosed D res.root ∧ Document.ChoicesCompatible res.root ∧
        Document.Entry.Sound.{v} res.root ∧ Document.Entry.SoundOverLeaves.{v} res.root) ∧
      report = Json.mkObj [("root", Document.claimJson res.root.name res.root.adm res.root.label),
        ("assumptions",
          Json.arr (res.root.assumptions.map (fun x => Document.claimJson x.1 x.2.1 x.2.2)).toArray)] ∧
      VE.CertificateWire.digest s!"ve-report-{VE.Route.Wire.identityVersion w.profiles}\n"
        (Json.mkObj [("environment_id", .str w.environmentId), ("document", document),
          ("report", report)]) = .ok reportId ∧
      answer = ok id [("admitted", .bool true), ("assurance", .str "lean-admitted"),
        ("report", report), ("report_id", .str reportId), ("environment_id", .str w.environmentId),
        ("kinds", Json.arr (D.units.map (fun u => VE.Route.Admission.renderKind u.kind)).toArray)] := by
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := bind_ok h
  simp only [hk, Json.getStr?, pure_bind] at h
  rw [if_neg (by decide)] at h
  obtain ⟨env, henv, h⟩ := bind_ok h
  obtain ⟨w, hw, h⟩ := bind_ok h
  split at h <;> try (exfalso; simp_all; done)
  exact ⟨id, env, w, hid, henv, hw, (extension_document_sound.{v} w id _ j answer h).2⟩

/-- The mode's entry (`runCaseReported`) answers with the runner's answer whenever the runner
accepts. -/
theorem runCaseReported_ok (j answer : Json) (more : Extension) (h : runCase j more = .ok answer) :
    runCaseReported j more = answer := by
  simp [runCaseReported, h]

end VE.Time.Wire
