import VE.Readings.SupExtra
import VE.Readings.Examples

/-! The fixtures of RD-6a (docs/spec/readings-defaults-PLAN.md RD-6a) on S2a's M1 document `K1`: X1 and X2 as `#guard`s,
X3 as a Lean refutation.

X1 is the counterexample that made `superpose_all_extra` take `hQw` (the approved statement has no typing of `Q`).
`noAvoid` is `∀agent ∀user. ¬avoid_required`. It is over the shared vocabulary and over each choice's complete
vocabulary, and the name map fixes `avoid_required`. A base admissible for `sup K1` gives `avoid_required`, a layer
symbol and so not in its base vocabulary, no tuple, and the pulled base gives it the same relation. So
`Q = Q' c = [noAvoid]` holds of every such base, and `Transfers K1 [noAvoid] (fun _ => [noAvoid])` holds, and so
does the conflict-freedom hypothesis, since K1 is CONFLICT-FREE (S2a M1, one rule per reading) and `Q` excludes no
base. The certificate `closeCert` (one closing step) is accepted with `Q` in the slot. Yet the bare base, admissible
for both readings' documents and satisfying `noAvoid` as a base, has `avoid_required (a, u)` on both readings'
expansions, so `noAvoid` is false there: the approved conclusion fails. `hQw` excludes `Q` (X1.3). X2 checks that the
`_extra` checks at `Q = []` are the S2a checks on M2's bases. X3 mechanises X1 (DRI ruling 2026-10-07): the
approved statement, as one proposition, is refuted. -/
namespace VE.Readings.SupExtraExamples
open VE.Readings
open VE.Readings.Examples (K1 baseM)
open VE.Rights (correlate)
open VE.Norms (envAt Sat size)
open VE.SoftNorms (soften circ)
open VE.Compose (BaseAdmissibleP ConflictFreeP)
universe u

def noAvoid : VE.Formula := .all "agent" (.all "user" (.not (.binary "avoid_required" (.var 1) (.var 0))))
def closeCert : VE.Tableau.Certificate := ⟨"ve-tableau-checker@2", "", [], "", .close⟩
/-- One agent, one user, no constant and no tuple. -/
def bare : VE.FiniteModel String where
  domains s := match s with | "agent" => ["a"] | "user" => ["u"] | _ => []
  constants _ := none
  relations _ := []

/-! ## X1: `superpose_all_extra` without `hQw` -/

-- X1.1: `φ = noAvoid` is over the shared vocabulary (`hφ`)
#guard noAvoid.check (sharedEnv K1) []
-- X1.2: `Q' c = [noAvoid]` is over each choice's complete vocabulary (`Transfers`' first conjunct), and the name map
-- fixes `avoid_required`, so the pulled base reads it as the base does
#guard choices K1 == [[("rs1", 0)], [("rs1", 1)]]
#guard (choices K1).all (fun c => noAvoid.check (choiceEnvFull K1 c) [] && nameMap K1 c "avoid_required" == "avoid_required")
-- X1.3: `noAvoid` is not over `sup K1`'s base vocabulary (`hQw` fails), while the slot is
#guard !VE.Compose.slotCheck (correlate (sup K1).1) [noAvoid]
#guard VE.Compose.slotCheck (correlate (sup K1).1) (slotUnder K1 [])
-- X1.4: the certificate is accepted with `Q` in the slot, and not without it
#guard supCertificateCheckExtra K1 [] [noAvoid] [] noAvoid closeCert
#guard !supCertificateCheck K1 [] [] noAvoid closeCert
-- X1.5: the bare base satisfies each reading's background with `Q' c`, and `noAvoid` as a base sentence, and K1's
-- readings assert nothing
#guard (choices K1).all (fun c => VE.Compose.backgroundValidP (correlate (choiceDoc K1 c).1)
  (VE.Rights.limPremises (choiceDoc K1 c).1 ++ [noAvoid]) bare && (choiceDoc K1 c).2.isEmpty)
#guard noAvoid.eval bare []
-- X1.6: on each reading's expansion of the bare base `noAvoid` is false (`circ_canon`)
#guard (choices K1).all (fun c => !(circ (correlate (choiceDoc K1 c).1) noAvoid).eval bare [])

/-! ## X2: at `Q = []` the checks are S2a's (`supCertificateCheckExtra_nil`, `supModelCheckExtra_nil`) -/

#guard [baseM true true, baseM false false, baseM false true].all (fun M =>
  supModelCheckExtra K1 [] [] [] M == supModelCheck K1 [] [] M &&
  supModelCheckExtra K1 [("rs1", 1)] [] [] M == supModelCheck K1 [("rs1", 1)] [] M)
#guard supCertificateCheckExtra K1 [] [] [noAvoid] noAvoid closeCert == supCertificateCheck K1 [] [noAvoid] noAvoid closeCert
#guard supCertificateCheck K1 [] [noAvoid] noAvoid closeCert
-- with `Q` the model check reads `Q` on the base: `baseM true true` satisfies `noAvoid` and not `¬noAvoid`
#guard supModelCheckExtra K1 [] [noAvoid] [] (baseM true true)
#guard !supModelCheckExtra K1 [] [.not noAvoid] [] (baseM true true)

/-! ## X3: X1 mechanised, the approved `superpose_all_extra` is false (DRI ruling 2026-10-07)

`SuperposeAllExtraApproved` is 6.7's approved `superpose_all_extra`, binder for binder and without `hQw`, as one
proposition; `tools/check_readings_defaults_statements.py` checks it against the spec text. `superpose_all_extra_refuted`
instantiates it at K1, `Q = Q' c = [noAvoid]`, `Γ = []`, `φ = noAvoid`, `closeCert`, the reading `[("rs1", 0)]` and
`bare`, and derives `False`. Lean proves every hypothesis that quantifies over structures: `Transfers`
(`transfers_x1`), the slot's conflict-freedom over every base (`x1_conflict_free`, from the two conflict certificates
the route finds, by `slot_conflict_free`), the admissibility of `bare` (`bare_admissible`) and the failing conclusion
(through `canon_subst`). The four checker runs on closed data that the kernel cannot reduce are the premise
`X1Checks`: core's `List.mergeSort` and the `String` functions behind generated names are well-founded recursion,
which the kernel does not unfold, and the audit admits no decision by compiled code. Lean's evaluator runs them
(`#guard X1Checks`), as it runs every other fixture of this file. -/

set_option linter.unusedVariables false in
/-- 6.7's approved `superpose_all_extra` (no `hQw`), as one proposition. -/
def SuperposeAllExtraApproved : Prop :=
  ∀ (D : Doc) (h : WellFormedDoc D = true) (hch : D.chain ≠ .rights)
    (hs : superposable D = true) (A : Choice) (hA : ∀ x ∈ A, (candidate D x.1 x.2).isSome)
    (Q : List VE.Formula) (Q' : Choice → List VE.Formula) (hq : Transfers.{u} D Q Q')
    (hcf : ConflictFreeP.{u} (correlate (sup D).1) (slotUnder D A ++ Q))
    (Γ : List VE.Formula) (φ : VE.Formula) (hΓ : ∀ a ∈ Γ, a.WellFormed (sharedEnv D) [])
    (hφ : φ.WellFormed (sharedEnv D) []) (cert : VE.Tableau.Certificate)
    (accepted : supCertificateCheckExtra D A Q Γ φ cert = true)
    (c : Choice) (hc : Compatible D c) (hAc : ∀ x ∈ A, x ∈ c) (B : VE.Structure.{u})
    (hB : BaseAdmissibleP (correlate (choiceDoc D c).1) (VE.Rights.limPremises (choiceDoc D c).1 ++ Q' c) B)
    (hp : Sat (expand (choiceDoc D c).1 B) ((choiceDoc D c).2 ++ Γ)),
  φ.denote (expand (choiceDoc D c).1 B) []

/-- The approved proposition gives the built `superpose_all_extra`, binder for binder with `hQw` dropped: both are
    over the same constants, and the built one only adds `hQw`. -/
example (H : SuperposeAllExtraApproved.{u}) : type_of% @superpose_all_extra.{u} :=
  fun D h hch hs A hA Q Q' hq _ hcf => H D h hch hs A hA Q Q' hq hcf

/-- The certificate the route finds for each of K1's two conflict targets (`avoid_required`, `help_required`) over
    `Background_base′` and the slot: four expansions, then a close. -/
def conflictCert : VE.Tableau.Certificate :=
  ⟨"ve-tableau-checker@2", "", [], "", .expand 1 none [.expand 2 none [.expand 3 none [.expand 4 none [.close]]]]⟩

/-- The closed checker runs X1 needs: K1 is well formed and superposable, `closeCert` is accepted with `noAvoid` in
    the slot (X1.4), and the conflict certificates are accepted on the slot. -/
def X1Checks : Prop :=
  WellFormedDoc K1 = true ∧ superposable K1 = true ∧
    supCertificateCheckExtra K1 [] [noAvoid] [] noAvoid closeCert = true ∧
    VE.Compose.slotConflictFreeCheck (correlate (sup K1).1) (slotUnder K1 []) [some conflictCert, some conflictCert] = true

instance : Decidable X1Checks := inferInstanceAs (Decidable (_ ∧ _ ∧ _ ∧ _))

#guard X1Checks

theorem k1_hyps (hx : X1Checks) : Hyps K1 := ⟨hx.1, by decide, hx.2.1⟩

theorem k1_compatible {c : Choice} (hc : Compatible K1 c) : c = [("rs1", 0)] ∨ c = [("rs1", 1)] := by
  have := (choices_spec K1 (by decide) (by decide) c).mpr hc
  rw [show choices K1 = [[("rs1", 0)], [("rs1", 1)]] by decide] at this
  simpa using this

theorem noAvoid_of_empty (B : VE.Structure.{u}) (h : ∀ vs, ¬ B.relation "avoid_required" vs) :
    noAvoid.denote B [] := by
  intro _ _ _ _ hr
  simp only [VE.Formula.denote, VE.Term.denote] at hr
  obtain ⟨_, _, _, _, hr⟩ := hr
  exact h _ hr

/-- X1.1 and X1.2 for every structure: `Q' c = [noAvoid]` is over each choice's complete vocabulary, and at an
    admissible base of `sup K1` both `Q` and `Q' c` on the pulled base hold, since `avoid_required` has no tuple. -/
theorem transfers_x1 (hx : X1Checks) : Transfers.{u} K1 [noAvoid] (fun _ => [noAvoid]) := by
  refine ⟨fun c hc a ha => ?_, fun c _ B hB _ => ?_⟩
  · simp only [List.mem_singleton] at ha; subst ha
    rcases k1_compatible hc with rfl | rfl
    · exact (VE.check_iff_wellFormed _ _ _).mp (by decide)
    · exact (VE.check_iff_wellFormed _ _ _).mp (by decide)
  · have hB0 : ∀ vs, ¬ B.relation "avoid_required" vs := fun vs hr => by
      obtain ⟨_, hss, _⟩ := hB.1.1.1.2 "avoid_required" vs hr
      rw [show (envAt (soften (correlate (sup K1).1)) 0).predicates "avoid_required" = none by decide] at hss
      cases hss
    have hnm : nameMap K1 c "avoid_required" = "avoid_required" := nameMap_shared (k1_hyps hx) c (by decide)
    constructor
    · intro _ a ha; simp only [List.mem_singleton] at ha; subst ha
      exact noAvoid_of_empty _ (fun vs hr => hB0 vs (hnm ▸ hr.2))
    · intro _ a ha; simp only [List.mem_singleton] at ha; subst ha
      exact noAvoid_of_empty B hB0

/-- The hypothesis `hcf`: K1's slot with `noAvoid` is conflict-free over every base. -/
theorem x1_conflict_free (hx : X1Checks) :
    ConflictFreeP.{u} (correlate (sup K1).1) (slotUnder K1 [] ++ [noAvoid]) :=
  VE.Compose.conflictFreeP_append _ _ _ (VE.Compose.slot_conflict_free _
    (by rw [sup_correlate (k1_hyps hx)]; exact sup_wfSoft (k1_hyps hx)) _ _ hx.2.2.2)

/-- X1.5: `bare` is an admissible base of the strict reading's document with `Q' c`. -/
theorem bare_admissible (hx : X1Checks) :
    BaseAdmissibleP (correlate (choiceDoc K1 [("rs1", 0)]).1)
      (VE.Rights.limPremises (choiceDoc K1 [("rs1", 0)]).1 ++ [noAvoid]) bare.asStructure := by
  refine VE.Compose.baseAdmissibleP_of_valid _ _ bare ⟨fun x s hx' => ?_, fun _ _ hr => nomatch hr⟩
    (by simp (config := { ground := true, decide := true }))
  rw [VE.Norms.envAt_constants, soften_E, envPrime_constants, choice_correlate (k1_hyps hx),
    choice_E] at hx'
  cases hx'

/-- The approved `superpose_all_extra` is false: at X1 every hypothesis holds and the conclusion fails (X1.6). -/
theorem superpose_all_extra_refuted (hx : X1Checks) : ¬ SuperposeAllExtraApproved.{0} := by
  intro H
  have hc : Compatible K1 [("rs1", 0)] := (by decide : compatible K1 [("rs1", 0)] = true)
  have hB := bare_admissible hx
  have hφY := H K1 hx.1 (by decide) hx.2.1 [] (fun _ h => nomatch h) [noAvoid] (fun _ => [noAvoid])
    (transfers_x1 hx) (x1_conflict_free hx) [] noAvoid (fun _ h => nomatch h)
    ((VE.check_iff_wellFormed _ _ _).mp (by decide)) closeCert hx.2.2.1 [("rs1", 0)] hc (fun _ h => nomatch h)
    bare.asStructure hB (by rw [show (choiceDoc K1 [("rs1", 0)]).2 = [] by decide]; exact VE.Compose.sat_nil _)
  have hv : VE.Norms.Valid (soften (correlate (choiceDoc K1 [("rs1", 0)]).1)) := by
    rw [choice_correlate (k1_hyps hx)]; exact choice_valid (k1_hyps hx) hc
  have hcirc := VE.SoftNorms.canon_subst hv bare.asStructure hB.1.1.1.1
    (size (soften (correlate (choiceDoc K1 [("rs1", 0)]).1))) noAvoid []
    ((VE.check_iff_wellFormed _ _ _).mp (by decide)) [] (typed_nil _)
  have hn : (circ (correlate (choiceDoc K1 [("rs1", 0)]).1) noAvoid).eval bare [] = false := by decide
  have ht : (circ (correlate (choiceDoc K1 [("rs1", 0)]).1) noAvoid).eval bare [] = true :=
    (VE.eval_iff_denote bare [] _).mpr (hcirc.mpr hφY)
  rw [hn] at ht
  cases ht

end VE.Readings.SupExtraExamples
