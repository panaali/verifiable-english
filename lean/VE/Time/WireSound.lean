import VE.Time.Document

/-! Wire theorems of the `quantity` service mode (kernel boundary, KB-8).

`VE.Time.Wire.runCase j more` answers one case of the mode. For each case kind whose answer carries
a verdict there is one theorem here, with the hypothesis that the runner accepted (`runCase j more =
.ok answer`) and the case's `kind`; its conclusion names what the case's own decoders read from it
(the environment, the statements, the model, the certificate, the document), says the answer is
exactly a fixed list of fields over them (no open tail: every key is named), and ends in the proved
checker's soundness theorem:

* `admission` (also a case with no `kind`), in two theorems, one per shape of the answer: the
  statement is `Admitted` and its core well formed (`Admission.sound`); without a `model` member the
  answer is the seven fields (`_plain`), and with one it adds the reported `value`, the core's truth in
  the decoded model (`evalB_sorted_sound`), and `evaluations`, the evaluator's work, of which nothing
  is stated (`_valued`).
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

/-- KB-8, `admission` (the default kind) without a `model` member: an answer reports the decoded
statement's regenerated artifacts and identities, exactly seven fields and no value; the statement is
admitted and its core well formed. -/
theorem quantity_admission_wire_sound_plain (j answer : Json) (more : Extension)
    (h : runCase j more = .ok answer)
    (hk : j.getObjVal? "kind" = .ok (.str "admission") ∨ ∃ e, j.getObjVal? "kind" = .error e)
    (hm : ∃ e, j.getObjVal? "model" = .error e) :
    ∃ (id : String) (env : Json) (w : W6Env) (quantity : Json) (a : Admission w),
      stringField j "id" = .ok id ∧
      j.getObjVal? "environment" = .ok env ∧ decodeEnvironment env = .ok w ∧
      j.getObjVal? "quantity" = .ok quantity ∧ decodeQuantity w quantity = .ok a ∧
      answer = ok id [("assurance", .str "lean-admitted"), ("Q", a.Q), ("core", a.core),
        ("meaning_id", .str a.meaningId), ("core_meaning_id", .str a.coreId),
        ("environment_id", .str w.environmentId), ("target_environment_id", .str w.targetId)] ∧
      Admitted w.vocab.env [] a.formula ∧ a.formula.erase.WellFormed w.vocab.env.erase [] := by
  obtain ⟨_, hm⟩ := hm
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := bind_ok h
  rcases hk with hk | ⟨e, hk⟩ <;> simp only [hk, Json.getStr?, pure_bind] at h
  all_goals
    rw [if_neg (by decide)] at h
    obtain ⟨env, henv, h⟩ := bind_ok h
    obtain ⟨w, hw, h⟩ := bind_ok h
    split at h
    · rename_i hmj
      rw [hm] at hmj
      cases hmj
    · obtain ⟨quantity, hqj, h⟩ := bind_ok h
      obtain ⟨a, ha, h⟩ := bind_ok h
      cases h
      exact ⟨id, env, w, quantity, a, hid, henv, hw, hqj, ha, rfl, (Admission.sound a).1,
        (Admission.sound a).2⟩

/-- KB-8, `admission` (the default kind) with a `model` member: the model decodes, and an answer
reports the decoded statement's regenerated artifacts and identities, then the core's truth in the
decoded model (`value`) and the evaluator's work (`evaluations`, of which nothing is stated): exactly
nine fields. The statement is admitted and its core well formed. -/
theorem quantity_admission_wire_sound_valued (j answer model : Json) (more : Extension)
    (h : runCase j more = .ok answer)
    (hk : j.getObjVal? "kind" = .ok (.str "admission") ∨ ∃ e, j.getObjVal? "kind" = .error e)
    (hm : j.getObjVal? "model" = .ok model) :
    ∃ (id : String) (env : Json) (w : W6Env) (quantity : Json) (a : Admission w)
      (d : VE.Order.ModelData VE.Order.Wire.Entity) (b : Bool) (work : Nat),
      stringField j "id" = .ok id ∧
      j.getObjVal? "environment" = .ok env ∧ decodeEnvironment env = .ok w ∧
      j.getObjVal? "quantity" = .ok quantity ∧ decodeQuantity w quantity = .ok a ∧
      VE.Route.Decode.decodeOrderModel w.vocab.core model = .ok d ∧
      answer = ok id [("assurance", .str "lean-admitted"), ("Q", a.Q), ("core", a.core),
        ("meaning_id", .str a.meaningId), ("core_meaning_id", .str a.coreId),
        ("environment_id", .str w.environmentId), ("target_environment_id", .str w.targetId),
        ("value", .bool b), ("evaluations", toJson work)] ∧
      Admitted w.vocab.env [] a.formula ∧ a.formula.erase.WellFormed w.vocab.env.erase [] ∧
      b = a.formula.erase.eval d.toModel [] := by
  unfold runCase at h
  obtain ⟨id, hid, h⟩ := bind_ok h
  rcases hk with hk | ⟨e, hk⟩ <;> simp only [hk, Json.getStr?, pure_bind] at h
  all_goals
    rw [if_neg (by decide)] at h
    obtain ⟨env, henv, h⟩ := bind_ok h
    obtain ⟨w, hw, h⟩ := bind_ok h
    split at h
    · rename_i model' hmj
      rw [hm] at hmj
      cases hmj
      obtain ⟨quantity, hqj, h⟩ := bind_ok h
      obtain ⟨a, ha, h⟩ := bind_ok h
      obtain ⟨d, hd, h⟩ := bind_ok h
      split at h
      · rename_i b work hb
        cases h
        exact ⟨id, env, w, quantity, a, d, b, work, hid, henv, hw, hqj, ha, hd, rfl,
          (Admission.sound a).1, (Admission.sound a).2,
          evalB_sorted_sound d (predicateNames w) _ _ _ _ hb⟩
      · cases h
    · rename_i hmj
      rw [hm] at hmj
      cases hmj

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

/-! ## Ground date expressions (date-arith; SIZING section 3, items 10-12 and 14)

`elabCal_sound` and `calCmp_sound` are listed theorems of the `quantity` path: a date worked
out while decoding is the date `CalDenotes` names, and a decided or shown comparison means the
order `CalOrder` names between those dates. -/

theorem except_ok_inj {ε α : Type} {a b : α} (h : (Except.ok a : Except ε α) = .ok b) : a = b := by
  cases h; rfl

theorem integer_nat {s : String} {z : Int} (h : integer s = .ok z) (hz : ¬ z < 0) :
    integer s = .ok (z.toNat : Int) := by
  rw [h, Int.toNat_of_nonneg (by omega)]

theorem arr_of_toList {xs : Array Json} {l : List Json} (h : xs.toList = l) : Json.arr xs = .arr l.toArray := by
  cases xs; simp at h; subst h; rfl

/-- Item 10: every date `elabCal` returns is the date its expression denotes, and lies in
1900..9999 with a valid month and day. -/
theorem elabCal_sound : ∀ (fuel : Nat) (j : Json) (D : Civil), elabCal fuel j = .ok D →
    CalDenotes j D ∧ D.Ground
  | 0, _, _, h => by cases h
  | fuel + 1, j, D, h => by
    unfold elabCal at h
    split at h
    · rename_i xs
      split at h
      · rename_i s hl
        rw [arr_of_toList hl]
        exact ⟨.date h, parseIsoFrom_valid h⟩
      · rename_i e sk sr hl
        rw [arr_of_toList hl]
        obtain ⟨D0, h0, h⟩ := bind_ok h
        obtain ⟨ih, g0⟩ := elabCal_sound fuel e D0 h0
        split at h
        · rename_i r hr
          obtain ⟨k, hk, h⟩ := bind_ok h
          split at h
          · rename_i D' hD'
            split at h
            · rename_i hg
              cases h
              exact ⟨.plusMonths ih hk hr (addMonths_spec hD') hg, hg⟩
            · cases h
          · cases h
        · cases h
      · rename_i e sk hl
        rw [arr_of_toList hl]
        obtain ⟨D0, h0, h⟩ := bind_ok h
        obtain ⟨ih, g0⟩ := elabCal_sound fuel e D0 h0
        obtain ⟨k, hk, h⟩ := bind_ok h
        split at h
        · rename_i hb
          cases h
          simp only [Bool.and_eq_true, decide_eq_true_eq] at hb
          obtain ⟨⟨⟨hpb, hk0⟩, hkm⟩, h9⟩ := hb
          have hpr := (Civil.properB_iff _).mp hpb
          have hp' := addDays_proper hpr k.toNat
          have hn := num_addDays hpr k.toNat
          refine ⟨.plusDays ih hk hk0 ⟨hpr, g0.2.1⟩ ⟨hp', h9⟩ (by omega), ?_⟩
          obtain ⟨hy, hm1, hm12, hd1, hdm⟩ := hp'
          exact ⟨by unfold minGroundYear; omega, h9, hm1, hm12, hd1, hdm⟩
        · cases h
      · rename_i e _ hl
        rw [arr_of_toList hl]
        obtain ⟨D0, h0, h⟩ := bind_ok h
        obtain ⟨ih, g0⟩ := elabCal_sound fuel e D0 h0
        cases h
        obtain ⟨g1, g2, g3, g4, _, _⟩ := g0
        exact ⟨.monthFirst ih, g1, g2, g3, g4, Nat.le_refl 1, monthLen_pos g3 g4⟩
      · rename_i e _ _ hl
        rw [arr_of_toList hl]
        obtain ⟨D0, h0, h⟩ := bind_ok h
        obtain ⟨ih, g0⟩ := elabCal_sound fuel e D0 h0
        cases h
        obtain ⟨g1, g2, g3, g4, _, _⟩ := g0
        exact ⟨.monthLast ih, g1, g2, g3, g4, monthLen_pos g3 g4, Nat.le_refl _⟩
      · rename_i n w m y hl
        rw [arr_of_toList hl]
        obtain ⟨n', hn, h⟩ := bind_ok h
        obtain ⟨w', hw, h⟩ := bind_ok h
        obtain ⟨m', hm, h⟩ := bind_ok h
        obtain ⟨y', hy, h⟩ := bind_ok h
        split at h
        · rename_i D' hD'
          cases h
          obtain ⟨hv, hyy, hmm, hwd, hn1, hd⟩ := nthWeekday_spec hD'
          refine ⟨.nthWeekday hn hw (hmm ▸ hm) (hyy ▸ hy) hv hwd hn1 hd, ?_⟩
          obtain ⟨⟨hy1, hm1, hm12, hd1, hdm⟩, h9⟩ := hv
          exact ⟨by unfold minGroundYear; omega, h9, hm1, hm12, hd1, hdm⟩
        · cases h
      · cases h
    · cases h

/-- Item 11: a `["cal", E]` day term's date is the date `E` denotes, and it is valid
(1970..9999), so today's guard holds for its day number. -/
theorem calDay_sound {e : Json} {D : Civil} (h : calDay e = .ok D) : CalDenotes e D ∧ D.Valid := by
  unfold calDay at h
  obtain ⟨D0, h0, h⟩ := bind_ok h
  obtain ⟨ih, g0⟩ := elabCal_sound _ _ _ h0
  split at h
  · rename_i hb
    cases h
    exact ⟨ih, (Civil.properB_iff _).mp hb, g0.2.1⟩
  · cases h

theorem before_asymm {a b : Civil} (h : a.Before b) : ¬ b.Before a := by
  unfold Civil.Before at *; omega

theorem noLater_iff {a b : Civil} : (a.Before b ∨ a = b) ↔ ¬ b.Before a := by
  rcases a with ⟨ay, am, ad⟩; rcases b with ⟨by', bm, bd⟩
  unfold Civil.Before; simp only [Civil.mk.injEq]; omega

theorem coord_num {x T : Civil} (hx : x.Valid) : Coord (x.num : Int) T ↔ T = x := by
  constructor
  · rintro ⟨hT, hn⟩; exact num_injective hT.1 hx.1 (by omega)
  · rintro rfl; exact ⟨hx, rfl⟩

theorem tdates_num.{u} {α : Type u} {R : Int → Int → Prop} {x y : Civil} :
    TDates (α := α) R (some (.qty dayTag (x.num : Int))) (some (.qty dayTag (y.num : Int))) ↔
      R x.num y.num := by
  constructor
  · rintro ⟨a, b, ha, hb, hr⟩
    cases ha; cases hb; exact hr
  · intro hr; exact ⟨_, _, rfl, rfl, hr⟩

/-- Item 12: a `cal_cmp` node means the order its operator names between the dates its two
expressions denote, in every tagged structure: when both dates are valid it is today's date
node over their day numbers, else it is decided `top` or `bottom`. -/
theorem calCmp_sound.{u} {op : String} {a b : Json} {f : QFormula} (h : elabCalCmp op a b = .ok f) :
    ∃ x y, CalDenotes a x ∧ CalDenotes b y ∧
      ∀ {α : Type u} (T : TStructure α) (ρ : List α), f.tdenote T ρ ↔ CalOrder op x y := by
  unfold elabCalCmp at h
  obtain ⟨x, hx, h⟩ := bind_ok h
  obtain ⟨y, hy, h⟩ := bind_ok h
  obtain ⟨dx, gx⟩ := elabCal_sound _ _ _ hx
  obtain ⟨dy, gy⟩ := elabCal_sound _ _ _ hy
  refine ⟨x, y, dx, dy, ?_⟩
  intro α T ρ
  split at h
  · rename_i node hm
    cases h
    by_cases hv : x.properB = true ∧ y.properB = true
    · have vx : x.Valid := ⟨(Civil.properB_iff _).mp hv.1, gx.2.1⟩
      have vy : y.Valid := ⟨(Civil.properB_iff _).mp hv.2, gy.2.1⟩
      rw [if_pos (by simp [hv.1, hv.2])]
      unfold calNode at hm
      split at hm <;> cases hm <;>
        simp [QFormula.tdenote, QTerm.tdenote, tdates_num, CalOrder, CalBefore, CalAfter, CalOn,
          CalNoLater, coord_num vx, coord_num vy, noLater_iff]
    · rw [if_neg (by simpa using hv)]
      split <;> simp_all [QFormula.tdenote]
  · cases h

/-- Group 14 (C7): for valid dates `cal_cmp` is exactly today's date node over their day numbers,
so a sentence lowered as ground dates and one lowered as day constants mean the same. -/
theorem calCmp_agrees {op : String} {a b : Json} {f : QFormula} {x y : Civil}
    (ha : elabCal VE.Limits.maxDepth a = .ok x) (hb : elabCal VE.Limits.maxDepth b = .ok y)
    (vx : x.Valid) (vy : y.Valid) (h : elabCalCmp op a b = .ok f) :
    (op = "before" ∧ f = .dateBefore (.num dayTag x.num) (.num dayTag y.num)) ∨
    (op = "after" ∧ f = .dateAfter (.num dayTag x.num) (.num dayTag y.num)) ∨
    (op = "on" ∧ f = .dateOn (.num dayTag x.num) (.num dayTag y.num)) ∨
    (op = "on_or_before" ∧ f = .dateNoLater (.num dayTag x.num) (.num dayTag y.num)) ∨
    (op = "on_or_after" ∧ f = .dateNoLater (.num dayTag y.num) (.num dayTag x.num)) := by
  unfold elabCalCmp at h
  rw [ha, hb] at h
  have hpx := (Civil.properB_iff x).mpr vx.1
  have hpy := (Civil.properB_iff y).mpr vy.1
  obtain ⟨_, hx, h⟩ := bind_ok h
  cases hx
  obtain ⟨_, hy, h⟩ := bind_ok h
  cases hy
  split at h
  · rename_i node hm
    cases h
    rw [if_pos (by simp [hpx, hpy])]
    unfold calNode at hm
    split at hm <;> cases hm <;> simp
  · cases h

/-- Group 14 (C1): a statement's meaning id is the id of its canonical object with the dates its
ground expressions start from (none: today's object), so other case dates give another id. -/
theorem statementIds_inputs {w : W6Env} {f : QFormula} {inputs : List String} {m c : String}
    (h : statementIds w f inputs = .ok (m, c)) :
    VE.Route.Wire.meaningId w.profiles w.environmentId
      (Json.mkObj ([("format", .str "ve-quantity@1"), ("formula", encQ f), ("traces", Json.arr #[])] ++
        inputsField inputs)) = .ok m := by
  unfold statementIds at h
  obtain ⟨m', hm, h⟩ := bind_ok h
  obtain ⟨c', _, h⟩ := bind_ok h
  cases h
  exact hm


theorem monthsLater_unique {D D1 D2 : Civil} {k : Int} {r : Option MonthEnd}
    (h1 : D.MonthsLater k r D1) (h2 : D.MonthsLater k r D2) : D1 = D2 := by
  obtain ⟨y, m, m1, m12, hi, hs⟩ := h1
  obtain ⟨y', m', m1', m12', hi', hs'⟩ := h2
  obtain ⟨rfl, rfl⟩ : y = y' ∧ m = m' := by omega
  split at hs <;> rename_i hc <;> simp only [hc, if_true, if_false, not_false_eq_true] at hs'
  · rw [hs, hs']
  · rcases hs with ⟨hr, rfl⟩ | ⟨hr, rfl⟩ <;> rcases hs' with ⟨hr', rfl⟩ | ⟨hr', rfl⟩ <;>
      first | rfl | (rw [hr] at hr'; cases hr')

theorem same_week_day {y m d d' : Nat} (hd : 1 ≤ d) (hd' : 1 ≤ d')
    (hw : Civil.weekday ⟨y, m, d⟩ = Civil.weekday ⟨y, m, d'⟩) (hq : (d - 1) / 7 = (d' - 1) / 7) : d = d' := by
  unfold Civil.weekday Civil.num at hw
  simp only at hw
  omega

/-- B6: a ground date expression denotes at most one date, so `elabCal_sound` and `calCmp_sound` name the
date of each expression. -/
theorem calDenotes_unique {j : Json} {D D' : Civil} (h : CalDenotes j D) (h' : CalDenotes j D') : D = D' := by
  induction h generalizing D' with
  | @date s D hp =>
    generalize hj : Json.arr #[.str "date", .str s] = j' at h'
    cases h' <;> simp at hj
    subst hj; rename_i hp'; rw [hp] at hp'; cases hp'; rfl
  | @plusMonths e sk sr D0 D1 k r _ hk hr hm _ ih =>
    generalize hj : Json.arr #[.str "plus_months", e, .str sk, .str sr] = j' at h'
    cases h' <;> simp at hj
    rename_i he' hk' hr' hm' _
    obtain ⟨rfl, rfl, rfl⟩ := hj
    have := ih he'; subst this
    rw [hk] at hk'; cases hk'; rw [hr] at hr'; cases hr'
    exact monthsLater_unique hm hm'
  | @plusDays e sk D0 D1 k _ hk _ _ hv hn ih =>
    generalize hj : Json.arr #[.str "plus_days", e, .str sk] = j' at h'
    cases h' <;> simp at hj
    rename_i he' hk' _ _ hv' hn'
    obtain ⟨rfl, rfl⟩ := hj
    have := ih he'; subst this
    rw [hk] at hk'; cases hk'
    exact num_injective hv.1 hv'.1 (by omega)
  | @monthFirst e D0 _ ih =>
    generalize hj : Json.arr #[.str "month_first", e] = j' at h'
    cases h' <;> simp at hj
    subst hj; rename_i he'; rw [ih he']
  | @monthLast e D0 _ ih =>
    generalize hj : Json.arr #[.str "month_last", e] = j' at h'
    cases h' <;> simp at hj
    subst hj; rename_i he'; rw [ih he']
  | @nthWeekday n w m y n1 w1 D0 hn hw hm hy hv hwd _ hd =>
    generalize hj : Json.arr #[.str "nth_weekday", n, w, m, y] = j' at h'
    cases h' <;> simp at hj
    rename_i hn' hw' _ hm' hy' hv' hwd' hd'
    obtain ⟨rfl, rfl, rfl, rfl⟩ := hj
    rw [hn] at hn'; rw [hw] at hw'; rw [hm] at hm'; rw [hy] at hy'
    simp only [Except.ok.injEq] at hn' hw' hm' hy'
    subst hn' hw'
    obtain ⟨y0, m0, d0⟩ := D0
    obtain ⟨y1, m1, d1⟩ := D'
    simp only at hm' hy' hd hd' hwd hwd' ⊢
    subst hm' hy'
    have := same_week_day (y := y0) (m := m0) hv.1.2.2.2.1 hv'.1.2.2.2.1 (hwd.trans hwd'.symm) (hd.trans hd'.symm)
    simp only at this
    rw [this]

end VE.Time.Wire
