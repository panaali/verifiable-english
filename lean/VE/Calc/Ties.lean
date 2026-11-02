import VE.Calc.Run

/-! The R16 ties of me-5e's evidence (ties-me-5e): what `Shown.matches`, `Derive.shown`, `Check.runShown`, `Run.row`
and `Run.rowJson` mean, stated in the derivation's own terms (`Follows`, `QFact.Holds`, `Claim.Holds` at the shown
point, `Check.OutcomeMeans`). A holds row shows a certificate that replays (`Derivation.check_sound`), a fails row a
point that is a counterexample (`Counterexample.check_sound`), and every other outcome shows nothing; on the wire, a
follows row's `certificate` and `counterexample` are those, or `null`. Proofs only: `tools/trust-classes.json` lists
the ties. -/

namespace VE.Calc
open Lean VE.Numbers

/-- What `Shown.matches` accepts: a nonempty certificate with holds, a counterexample with fails, and nothing with
every other outcome. -/
theorem Shown.matches_iff (o : Outcome) (s : Shown) :
    Shown.matches o s = true ↔
      (o = .decided .holds ∧ ∃ st sts, s = .certificate (st :: sts)) ∨
        (o = .decided .fails ∧ ∃ κ, s = .counterexample κ) ∨
        (o ≠ .decided .holds ∧ o ≠ .decided .fails ∧ s = .nothing) := by
  rcases o with v | u
  · cases v <;> rcases s with _ | (_ | _) | _ <;> simp [Shown.matches]
  · rcases s with _ | (_ | _) | _ <;> simp [Shown.matches]

/-- The search's holds shows a certificate that replays over the facts, so the goal holds wherever the facts and
the square links do (`Derivation.check_sound`). -/
theorem Derive.shown_holds (P : List QFact) (links : List (String × String)) (g : QFact) (s : Shown)
    (h : Derive.shown P links g = (.decided .holds, s)) :
    ∃ d : Derivation, s = .certificate d.steps ∧ d.check P links g = true ∧
      ∀ κ : String → Rat, (∀ f ∈ P, f.Holds κ) → (∀ l ∈ links, κ l.1 = κ l.2 * κ l.2 ∧ 0 ≤ κ l.2) → g.Holds κ := by
  unfold Derive.shown at h
  split at h
  · rename_i d _
    split at h
    · rename_i hc
      cases h
      exact ⟨d, rfl, hc, Derivation.check_sound P links g d hc⟩
    · cases h
  · split at h <;> cases h
  · cases h
  · cases h

/-- The search's fails shows a point where every fact and square link holds and the goal does not
(`Counterexample.check_sound`). -/
theorem Derive.shown_fails (P : List QFact) (links : List (String × String)) (g : QFact) (s : Shown)
    (h : Derive.shown P links g = (.decided .fails, s)) :
    ∃ κ, s = .counterexample κ ∧ (∀ f ∈ P, f.Holds (Answer.point κ)) ∧
      (∀ l ∈ links, Answer.point κ l.1 = Answer.point κ l.2 * Answer.point κ l.2 ∧ 0 ≤ Answer.point κ l.2) ∧
      ¬ g.Holds (Answer.point κ) := by
  unfold Derive.shown at h
  split at h
  · split at h <;> cases h
  · rename_i κ _
    split at h
    · rename_i hc
      cases h
      exact ⟨κ, rfl, Counterexample.check_sound P links g _ hc⟩
    · cases h
  · cases h
  · cases h

/-- Every other outcome of the search shows nothing. -/
theorem Derive.shown_nothing (P : List QFact) (links : List (String × String)) (g : QFact) (o : Outcome)
    (s : Shown) (h : Derive.shown P links g = (o, s)) (hh : o ≠ .decided .holds) (hf : o ≠ .decided .fails) :
    s = .nothing := by
  unfold Derive.shown at h
  split at h
  · split at h
    · cases h; exact absurd rfl hh
    · cases h; rfl
  · split at h
    · cases h; exact absurd rfl hf
    · cases h; rfl
  · cases h; rfl
  · cases h; rfl

/-- A derivation shows evidence only from the search over its lowered premises and conclusion; an outcome reached
before the search (a fault, the node limit, a premise or conclusion that does not lower) shows nothing and is
neither holds nor fails. -/
theorem Check.runShown_follows (ds : List Decl) (P : List Claim) (links : List (String × String)) (C : Claim)
    (o : Outcome) (s : Shown) (hr : (Check.follows P links C).runShown ds = (o, s)) :
    (s = .nothing ∧ o ≠ .decided .holds ∧ o ≠ .decided .fails) ∨
      ∃ fss g, P.mapM (Claim.facts ds) = some fss ∧ C.facts ds = some [g] ∧
        Derive.shown fss.flatten links g = (o, s) := by
  simp only [Check.runShown, Check.keep] at hr
  split at hr
  · cases hr; exact .inl ⟨rfl, by decide, by decide⟩
  · cases hr; exact .inl ⟨rfl, by decide, by decide⟩
  · cases hr; exact .inl ⟨rfl, by decide, by decide⟩
  · split at hr
    · cases hr; exact .inl ⟨rfl, by decide, by decide⟩
    · split at hr
      · rename_i fss g hP hC
        rw [Claim.factsIn_eq] at hP hC
        exact .inr ⟨fss, g, hP, hC, hr⟩
      · cases hr; exact .inl ⟨rfl, by decide, by decide⟩

/-- The outcome `runShown` gives is `Check.run`'s, so it means what its kind's clause says (`Check.run_sound`). -/
theorem Check.runShown_sound (ds : List Decl) (h : WellFormed ds) (k : Check) :
    k.OutcomeMeans ds (k.runShown ds).1 :=
  Check.run_sound ds h k

/-- A derivation that holds shows a certificate that replays over its lowered premises and conclusion, and the
conclusion follows (`Derivation.check_sound`, `follows_of_check`). -/
theorem Check.runShown_holds (ds : List Decl) (h : WellFormed ds) (P : List Claim) (links : List (String × String))
    (C : Claim) (s : Shown) (hr : (Check.follows P links C).runShown ds = (.decided .holds, s)) :
    ∃ fss g, ∃ d : Derivation, P.mapM (Claim.facts ds) = some fss ∧ C.facts ds = some [g] ∧
      s = .certificate d.steps ∧ d.check fss.flatten links g = true ∧ Follows ds P links C := by
  rcases Check.runShown_follows ds P links C _ s hr with ⟨_, hh, _⟩ | ⟨fss, g, hP, hC, hd⟩
  · exact absurd rfl hh
  · obtain ⟨d, rfl, hc, _⟩ := Derive.shown_holds _ links g s hd
    exact ⟨fss, g, d, hP, hC, rfl, hc, follows_of_check ds h P links C fss g d hP hC hc⟩

/-- A derivation that fails shows a point at which every square link and premise holds and the conclusion does
not (`Counterexample.check_sound`, `counterexample_of_check`). -/
theorem Check.runShown_fails (ds : List Decl) (h : WellFormed ds) (P : List Claim) (links : List (String × String))
    (C : Claim) (s : Shown) (hr : (Check.follows P links C).runShown ds = (.decided .fails, s)) :
    ∃ κ, s = .counterexample κ ∧
      (∀ l ∈ links, Answer.point κ l.1 = Answer.point κ l.2 * Answer.point κ l.2 ∧ 0 ≤ Answer.point κ l.2) ∧
      (∀ p ∈ P, p.Holds (values (assign ds (freeNames ds) (Answer.point κ)))) ∧
      ¬ C.Holds (values (assign ds (freeNames ds) (Answer.point κ))) := by
  rcases Check.runShown_follows ds P links C _ s hr with ⟨_, _, hf⟩ | ⟨fss, g, hP, hC, hd⟩
  · exact absurd rfl hf
  · obtain ⟨κ, rfl, hf, hl, hg⟩ := Derive.shown_fails _ links g s hd
    refine ⟨κ, rfl, hl, (premises_iff ds h P fss hP _).mp hf, fun hc => hg ?_⟩
    simpa using (Claim.facts_sound ds h C [g] hC _).mpr hc

/-- A claim shows nothing, and so does a derivation whose outcome is neither holds nor fails. -/
theorem Check.runShown_nothing (ds : List Decl) (k : Check) (o : Outcome) (s : Shown)
    (hr : k.runShown ds = (o, s)) (hk : (∃ c, k = .claim c) ∨ (o ≠ .decided .holds ∧ o ≠ .decided .fails)) :
    s = .nothing := by
  cases k with
  | claim c => simp only [Check.runShown, Prod.mk.injEq] at hr; exact hr.2.symm
  | follows P links C =>
    rcases Check.runShown_follows ds P links C o s hr with ⟨hs, _⟩ | ⟨fss, g, _, _, hd⟩
    · exact hs
    · rcases hk with ⟨_, hc⟩ | ⟨hh, hf⟩
      · cases hc
      · exact Derive.shown_nothing _ links g o s hd hh hf

/-- A row states its check's outcome, which means what the check's clause says, and shows what `runShown` shows. -/
theorem Run.row_means (c : Case) (h : WellFormed c.decls) (cl : String × Check) :
    cl.2.OutcomeMeans c.decls (Run.row c cl).outcome ∧ (Run.row c cl).shown = (cl.2.runShown c.decls).2 :=
  ⟨Check.run_sound c.decls h cl.2, rfl⟩

namespace Run

/-- A key of an object with distinct keys reads its value. -/
theorem mkObj_get (l : List (String × Json)) (k : String) (v : Json) (hn : (l.map (·.1)).Nodup)
    (hm : (k, v) ∈ l) : (Json.mkObj l).getObjVal? k = .ok v := by
  have hp : l.Pairwise (fun a b => ¬ compare a.1 b.1 = .eq) :=
    (List.pairwise_map.mp hn).imp (fun hne heq => hne (Std.LawfulEqOrd.eq_of_compare heq))
  simp only [Json.mkObj, Json.getObjVal?, Std.TreeMap.Raw.get?_eq_getElem?,
    Std.TreeMap.Raw.getElem?_ofList_of_mem (cmp := compare) (k_eq := Std.ReflCmp.compare_self) hp hm]
  rfl

/-- A row's `outcome` and `reason` are words that read back as the row's outcome, and nothing else (`outcomeAt`). -/
theorem rowJson_outcome (ds : List Decl) (id : String) (named : String → Option String) (vs : List Val)
    (k : Check) (r : Row) :
    ∃ w reason, (rowJson ds id named vs k r).getObjVal? "outcome" = .ok (.str w) ∧
      (rowJson ds id named vs k r).getObjVal? "reason" = .ok (reason.elim .null Json.str) ∧
      outcomes.find? (words · == (w, reason)) = some r.outcome :=
  ⟨(words r.outcome).1, (words r.outcome).2,
    mkObj_get _ _ _ (by cases k <;> simp [claimFields]) (by simp),
    mkObj_get _ _ _ (by cases k <;> simp [claimFields]) (by simp),
    outcomes_words r.outcome⟩

/-- A follows row whose evidence matches its outcome writes, on holds, the certificate's steps and a `null`
counterexample; on fails, a `null` certificate and the counterexample's value of each free value it reads; and two
`null`s for every other outcome. -/
theorem rowJson_shown (ds : List Decl) (id : String) (named : String → Option String) (vs : List Val)
    (P : List Claim) (links : List (String × String)) (C : Claim) (r : Row)
    (h : Shown.matches r.outcome r.shown = true) :
    (r.outcome = .decided .holds → ∃ steps, r.shown = .certificate steps ∧
      (rowJson ds id named vs (.follows P links C) r).getObjVal? "certificate" =
        .ok (.arr (steps.map stepJson).toArray) ∧
      (rowJson ds id named vs (.follows P links C) r).getObjVal? "counterexample" = .ok .null) ∧
    (r.outcome = .decided .fails → ∃ κ, r.shown = .counterexample κ ∧
      (rowJson ds id named vs (.follows P links C) r).getObjVal? "certificate" = .ok .null ∧
      (rowJson ds id named vs (.follows P links C) r).getObjVal? "counterexample" =
        .ok (.arr ((reads ds (.follows P links C)).map fun (n : String) =>
          Json.arr #[.str n, .str (exact (Answer.point κ n))]).toArray)) ∧
    (r.outcome ≠ .decided .holds → r.outcome ≠ .decided .fails →
      (rowJson ds id named vs (.follows P links C) r).getObjVal? "certificate" = .ok .null ∧
      (rowJson ds id named vs (.follows P links C) r).getObjVal? "counterexample" = .ok .null) := by
  rcases r with ⟨rid, o, s, p⟩
  have hc : (rowJson ds id named vs (.follows P links C) ⟨rid, o, s, p⟩).getObjVal? "certificate" =
      .ok (shownJson ds (.follows P links C) s).1 :=
    mkObj_get _ _ _ (by cases s <;> simp [claimFields, shownJson]) (by simp [claimFields])
  have hx : (rowJson ds id named vs (.follows P links C) ⟨rid, o, s, p⟩).getObjVal? "counterexample" =
      .ok (shownJson ds (.follows P links C) s).2 :=
    mkObj_get _ _ _ (by cases s <;> simp [claimFields, shownJson]) (by simp [claimFields])
  dsimp only at h ⊢
  rcases (Shown.matches_iff o s).mp h with ⟨rfl, st, sts, rfl⟩ | ⟨rfl, κ, rfl⟩ | ⟨hh, hf, rfl⟩
  · exact ⟨fun _ => ⟨_, rfl, hc, hx⟩, fun h => (by cases h), fun h => absurd rfl h⟩
  · exact ⟨fun h => (by cases h), fun _ => ⟨κ, rfl, hc, hx⟩, fun _ h => absurd rfl h⟩
  · exact ⟨fun h => absurd h hh, fun h => absurd h hf, fun _ _ => ⟨hc, hx⟩⟩

end Run

end VE.Calc
