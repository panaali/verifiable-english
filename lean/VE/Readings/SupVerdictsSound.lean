import VE.Readings.SupVerdictsWire

/-! RD-7's wire evidence chained with the fold. A certificate is global or under a complete
choice; a checked model identifies its own compatible choice. NONE needs a countermodel for every
covered choice, and SOME needs both witnesses. Exhaustion supplies neither. -/
namespace VE.Readings.Wire
open VE.Readings
open VE.Norms (Sat)
open VE.SoftNorms (soften circ)
open VE.Rights (correlate)
open VE.Compose (slotConflictFreeCheck)
universe u

/-- ALL from one certificate, including the global A = [] case. -/
theorem readings_wire_sup_verdicts_all (j : Lean.Json) (r : CertificateReplay)
    (h : replayCertificate j = .ok r)
    (hc : slotConflictFreeCheck (correlate (sup r.D).1) (slotUnder r.D r.assumed) r.conflictCerts = true)
    (ha : supCertificateCheck r.D r.assumed r.Γ r.φ r.cert = true) :
    ∀ c, Compatible r.D c → (∀ x ∈ r.assumed, x ∈ c) → ∀ B : VE.Structure.{u},
      VE.Rights.BaseAdmissibleR (choiceDoc r.D c).1 B →
      Sat (expand (choiceDoc r.D c).1 B) ((choiceDoc r.D c).2 ++ r.Γ) →
      r.φ.denote (expand (choiceDoc r.D c).1 B) [] :=
  readings_wire_all_sound j r h hc ha

/-- A wire countermodel is attached to the choice its bits encode, never another reading. -/
theorem readings_wire_sup_counter_row (j : Lean.Json) (r : ModelReplay) (h : replayModel j = .ok r)
    (hm : supModelCheck r.D r.assumed r.Γ r.M = true)
    (hn : (circ (correlate (sup r.D).1) r.φ).eval r.M [] = false) :
    ∃ c, Compatible r.D c ∧ (∀ x ∈ r.assumed, x ∈ c) ∧ Encodes r.D c r.M.asStructure ∧
      ∃ B : VE.Structure.{0}, VE.Rights.BaseAdmissibleR (choiceDoc r.D c).1 B ∧
        Sat (expand (choiceDoc r.D c).1 B) ((choiceDoc r.D c).2 ++ r.Γ) ∧
        ¬ r.φ.denote (expand (choiceDoc r.D c).1 B) [] := by
  obtain ⟨c, hc, hA, he, hB, hp, hf⟩ := readings_wire_model_sound j r h hm hn
  exact ⟨c, hc, hA, he, pull r.D c r.M.asStructure, hB, hp, hf⟩

/-- SOME is a proved choice and a choice with a checked countermodel, past the conflict gate. Each row's
    hypotheses are what its evidence proves: a certificate for `proved`, a countermodel for `refuted`. -/
theorem readings_wire_sup_verdicts_some (D : Doc) (Γ : List VE.Formula) (φ : VE.Formula)
    (cs rs : List (Choice × ChoiceResult))
    (rows : ∀ x ∈ rs, Compatible D x.1 ∧
      (x.2 = .proved → ∀ B : VE.Structure.{u}, VE.Rights.BaseAdmissibleR (choiceDoc D x.1).1 B →
        Sat (expand (choiceDoc D x.1).1 B) ((choiceDoc D x.1).2 ++ Γ) →
        φ.denote (expand (choiceDoc D x.1).1 B) []) ∧
      (x.2 = .refuted → ∃ B : VE.Structure.{0}, VE.Rights.BaseAdmissibleR (choiceDoc D x.1).1 B ∧
        Sat (expand (choiceDoc D x.1).1 B) ((choiceDoc D x.1).2 ++ Γ) ∧
        ¬ φ.denote (expand (choiceDoc D x.1).1 B) []))
    (h : foldEntailment cs rs = .some) :
    (∃ c, Compatible D c ∧ ∀ B : VE.Structure.{u}, VE.Rights.BaseAdmissibleR (choiceDoc D c).1 B →
        Sat (expand (choiceDoc D c).1 B) ((choiceDoc D c).2 ++ Γ) → φ.denote (expand (choiceDoc D c).1 B) []) ∧
      ∃ c, Compatible D c ∧ ∃ B : VE.Structure.{0}, VE.Rights.BaseAdmissibleR (choiceDoc D c).1 B ∧
        Sat (expand (choiceDoc D c).1 B) ((choiceDoc D c).2 ++ Γ) ∧ ¬ φ.denote (expand (choiceDoc D c).1 B) [] := by
  obtain ⟨_, ⟨p, hp, he⟩, ⟨m, hm, hn⟩⟩ := foldEntailment_some h
  have pp := rows p hp
  have mm := rows m hm
  exact ⟨⟨p.1, pp.1, pp.2.1 he⟩, m.1, mm.1, mm.2.2 hn⟩

/-- NONE covers every compatible choice taking A, with its own checked countermodel. -/
theorem readings_wire_sup_verdicts_none (D : Doc) (A : Choice) (Γ : List VE.Formula) (φ : VE.Formula)
    (cs rs : List (Choice × ChoiceResult))
    (covers : ∀ c, (Compatible D c ∧ ∀ x ∈ A, x ∈ c) ↔ c ∈ rs.map (·.1))
    (rows : ∀ x ∈ rs, x.2 = .refuted → ∃ B : VE.Structure.{0}, VE.Rights.BaseAdmissibleR (choiceDoc D x.1).1 B ∧
        Sat (expand (choiceDoc D x.1).1 B) ((choiceDoc D x.1).2 ++ Γ) ∧
        ¬ φ.denote (expand (choiceDoc D x.1).1 B) [])
    (h : foldEntailment cs rs = .none) :
    ∀ c, Compatible D c → (∀ x ∈ A, x ∈ c) → ∃ B : VE.Structure.{0}, VE.Rights.BaseAdmissibleR (choiceDoc D c).1 B ∧
        Sat (expand (choiceDoc D c).1 B) ((choiceDoc D c).2 ++ Γ) ∧ ¬ φ.denote (expand (choiceDoc D c).1 B) [] := by
  obtain ⟨_, _, hall⟩ := foldEntailment_none h
  intro c hc hA
  obtain ⟨x, hx, he⟩ := List.mem_map.mp ((covers c).mp ⟨hc, hA⟩)
  have hh := rows x hx (hall x hx)
  subst he
  exact hh

/-- A per-reading premise model, read from the same checked model theorem at bottom. -/
theorem readings_wire_sup_premises_model (j : Lean.Json) (r : ModelReplay) (h : replayModel j = .ok r)
    (hm : supModelCheck r.D r.assumed r.Γ r.M = true)
    (hn : (circ (correlate (sup r.D).1) r.φ).eval r.M [] = false) :
    ∃ c, Compatible r.D c ∧ (∀ x ∈ r.assumed, x ∈ c) ∧
      ∃ B : VE.Structure.{0}, VE.Rights.BaseAdmissibleR (choiceDoc r.D c).1 B ∧
        Sat (expand (choiceDoc r.D c).1 B) ((choiceDoc r.D c).2 ++ r.Γ) := by
  obtain ⟨c, hc, hA, _, hB, hp, _⟩ := readings_wire_model_sound j r h hm hn
  exact ⟨c, hc, hA, pull r.D c r.M.asStructure, hB, hp⟩

theorem readings_wire_sup_dead (D : Doc) (hr : supReady D = true) (s : String) (i : Nat)
    (cert : VE.Tableau.Certificate) (hd : deadCheck D s i cert = true) :
    ∀ c, Compatible D c → (s, i) ∉ c := dead_sound D hr s i cert hd

/-- The same global-certificate guarantee under the unspecified completion, including Fill_T. -/
theorem readings_wire_sup_nd_all (j : Lean.Json) (r : CertificateReplayND)
    (h : replayCertificateNDJ j = .ok r)
    (hc : slotConflictFreeCheck (correlate (sup (fillDoc r.f.r.N)).1)
      (slotUnder (fillDoc r.f.r.N) r.assumed ++ ndQ r.f.r.N) r.conflictCerts = true)
    (ha : supCertificateCheckExtra (fillDoc r.f.r.N) r.assumed (ndQ r.f.r.N) r.Γ r.φ r.cert = true) :
    ∀ c, Compatible r.f.r.N.D c → (∀ x ∈ r.assumed, x ∈ c) →
      VE.NormDefaults.ConflictFreeU.{u} (choiceU r.f.r.N c) ∧
        VE.NormDefaults.EntailsU.{u} (choiceU r.f.r.N c) ((choiceDoc r.f.r.N.D c).2 ++ r.Γ) r.φ :=
  readings_wire_nd_all_sound j r h hc ha

/-- Filled countermodels retain the separate filling and the choice their bits encode. -/
theorem readings_wire_sup_nd_counter (j : Lean.Json) (r : ModelReplayND)
    (h : replayModelNDJ j = .ok r)
    (hm : supModelCheckExtra (fillDoc r.f.r.N) r.assumed (ndQ r.f.r.N) r.Γ r.M = true)
    (hn : (circ (correlate (sup (fillDoc r.f.r.N)).1) r.φ).eval r.M [] = false) :
    ∃ c, Compatible r.f.r.N.D c ∧ (∀ x ∈ r.assumed, x ∈ c) ∧ Encodes (fillDoc r.f.r.N) c r.M.asStructure ∧
      VE.NormDefaults.BaseAdmissibleU (choiceU r.f.r.N c) (pull (fillDoc r.f.r.N) c r.M.asStructure) ∧
      Sat (VE.SoftNorms.canon (VE.NormDefaults.fill (choiceU r.f.r.N c)) (pull (fillDoc r.f.r.N) c r.M.asStructure))
        ((choiceDoc r.f.r.N.D c).2 ++ r.Γ) ∧
      ¬ r.φ.denote (VE.SoftNorms.canon (VE.NormDefaults.fill (choiceU r.f.r.N c))
        (pull (fillDoc r.f.r.N) c r.M.asStructure)) [] :=
  readings_wire_nd_model_sound j r h hm hn

end VE.Readings.Wire
