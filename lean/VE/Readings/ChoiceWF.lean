import VE.Readings.SupAll

/-! `choice_wellFormed` (docs/spec/composition-s2.md 8.4) with the route's soft check of every choice as its
hypothesis (DRI ruling 5 of 2026-10-03).

Every conjunct of `sideWF D (choiceDoc D c)` except `WellFormedSoft` of the choice's soft document holds: it has no
rights content, its generated names fit (each is a name of the document S1 checked the rule in, or of `sup D`), on
the norms chain every rule is strict and unswitchable (as in its home document), and its assertions are typed over
its complete vocabulary (`asserted_shared`). The soft check itself counts the generated formulas against the
chain's size limits on the whole document; it is not derived here, and the route runs it on every compatible
choice instead (`choicesSoftChecked`, Choice.lean). What every other theorem of 8.4 uses of it, that W1 reads the
softened document as valid, is `choice_valid`. -/
namespace VE.Readings
open VE.Norms (envAt size)
open VE.SoftNorms (soften decisionNames)
open VE.Rights (correlate)
universe u

theorem home_chainWF {D : Doc} (hh : Hyps D) (keep : String → Bool) (pick : ReadingSet → Option Candidate)
    (hw : sideWF D (build D keep pick) = true) : chainWF D.chain (build D keep pick).1 = true := by
  simp only [sideWF, Bool.and_eq_true] at hw; exact hw.1

/-- `choice_wellFormed` holds as soon as the choice's soft document passes the soft check. -/
theorem choice_sideWF_of_soft (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights)
    (hs : superposable D = true) (c : Choice) (hc : Compatible D c)
    (hw : VE.SoftNorms.WellFormedSoft (choiceDoc D c).1.soft = true) : sideWF D (choiceDoc D c) = true := by
  have hh : Hyps D := ⟨h, hch, hs⟩
  have hYn := choiceDoc_noRights D c hh.noRights
  have hsupW : chainWF D.chain (sup D).1 = true := (sup_wellFormed D hs).1
  simp only [sideWF, Bool.and_eq_true, List.all_eq_true]
  refine ⟨?_, fun a ha => ?_⟩
  · cases hd : D.chain with
    | rights => exact absurd hd hch
    | soft =>
      rw [hd] at hsupW
      simp only [chainWF, Bool.and_eq_true] at hsupW ⊢
      refine ⟨⟨hYn, ?_⟩, hw⟩
      simp only [namesFit, List.all_eq_true]
      intro n hn
      obtain ⟨x, hx, rfl⟩ := List.mem_map.mp hn
      rcases mem_decisions.mp hx with ⟨N, hN, hdm, rfl⟩ | ⟨N, hN, π, hπ, rfl⟩ | ⟨a, L, H, ht, rfl⟩
      · obtain ⟨keep, pick, _, hwH, hm⟩ := choice_home hh c hN
        have hH := home_chainWF hh keep pick hwH
        rw [hd] at hH
        simp only [chainWF, Bool.and_eq_true, namesFit, List.all_eq_true] at hH
        exact hH.1.2 _ (List.mem_map.mpr ⟨_, mem_decisions.mpr (Or.inl ⟨N, hm, hdm, rfl⟩), rfl⟩)
      · obtain ⟨keep, pick, _, hwH, hm⟩ := choice_home hh c hN
        have hH := home_chainWF hh keep pick hwH
        rw [hd] at hH
        simp only [chainWF, Bool.and_eq_true, namesFit, List.all_eq_true] at hH
        exact hH.1.2 _ (List.mem_map.mpr ⟨_, mem_decisions.mpr (Or.inr (Or.inl ⟨N, hm, π, hπ, rfl⟩)), rfl⟩)
      · simp only [namesFit, List.all_eq_true] at hsupW
        exact hsupW.1.2 _ (List.mem_map.mpr ⟨_, mem_decisions.mpr (Or.inr (Or.inr ⟨a, L, H, triple_sup hh c ht,
          rfl⟩)), rfl⟩)
    | norms =>
      simp only [chainWF, Bool.and_eq_true]
      refine ⟨⟨hYn, ?_⟩, hw⟩
      simp only [allStrict, List.all_eq_true]
      intro N hN
      obtain ⟨keep, pick, _, hwH, hm⟩ := choice_home hh c hN
      have hH := home_chainWF hh keep pick hwH
      rw [hd] at hH
      simp only [chainWF, Bool.and_eq_true, allStrict, List.all_eq_true] at hH
      exact Bool.and_eq_true_iff.mpr (hH.1.2 N hm)
  · apply (VE.check_iff_wellFormed _ _ _).mpr
    rw [choice_correlate hh c]
    exact shared_liftY hh c (asserted_shared D h hh.ready c hc a ha)

/-- `choice_wellFormed` (8.4) under DRI ruling 5: the route runs the soft check on every compatible choice's
    document (`choicesSoftChecked`), and its success is the hypothesis here. The replays of the superposed case kinds
    discharge it (`SupReplay.checked`, `readings_wire_choice_wellFormed`). The unconditional statement, the soft
    check derived from `sup D`'s, is not claimed. -/
theorem choice_wellFormed (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights)
    (hs : superposable D = true) (hw : choicesSoftChecked D = true) (c : Choice) (hc : Compatible D c) :
    sideWF D (choiceDoc D c) = true :=
  choice_sideWF_of_soft D h hch hs c hc (choicesSoftChecked_spec D (superposable_supReady hs) hw c hc)

end VE.Readings
