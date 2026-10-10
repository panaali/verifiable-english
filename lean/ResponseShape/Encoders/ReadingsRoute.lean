import ResponseShape.Encoders.Rights
import ResponseShape.Encoders.NormDefaults

/-! The `readings-route` mode (`Readings.Run.runCaseReported`) against `readings-route.json#/row`. A
case of another kind is the lower route's (rights, soft-norms, norm-defaults or norms). -/

namespace ResponseShape.Encoders.ReadingsRoute
open Lean ResponseShape ResponseShape.Skeletons
open VE.Readings VE.Readings.Run

variable {req : Json}

theorem keyJson_fits (k : GenKey) : Fits req (skel% "readings-route.json#/$defs/key") (Wire.keyJson k) := by
  cases k with
  | excepted r b => cases b <;> simp only [Wire.keyJson, Option.toList, List.map_cons, List.map_nil] <;> fits
  | off r b π => cases b <;> simp only [Wire.keyJson, Option.toList, List.map_cons, List.map_nil] <;> fits
  | _ => unfold Wire.keyJson; fits

theorem candidate_fits (a : Wire.Admitted) (R : ReadingSet) (i : Nat) :
    OkFits req (skel% "readings-route.json#/$defs/candidate") (Run.candidateJson a R i) := by
  unfold Run.candidateJson
  okfits
  all_goals (try simp only [keyEntry])
  all_goals fits using keyJson_fits

theorem pair_fits (f : PairFacts) (sid : String) :
    Fits req (skel% "readings-route.json#/$defs/pair") (pairJson f sid) := by
  unfold pairJson optBool
  fits

/-- An element of `setPairs`: a pair of readings and their separating situation's facts. -/
def PairEntry (x : Json) : Prop :=
  ∃ r o f sid, x = Json.mkObj [("reading", .str r), ("other", .str o), ("pair", pairJson f sid)]

theorem setPairsWith_entries (adjust : PairFacts → PairFacts) (a : Wire.Admitted) (R : ReadingSet) (RJ : Wire.SetJ) :
    OkP (fun out => ∀ x ∈ out, PairEntry x) (setPairsWith adjust a R RJ) := by
  unfold setPairsWith
  simp only [bind_pure]
  refine OkP.forIn (P := fun (out : List Json) => ∀ x ∈ out, PairEntry x) ?_ ?_
  · intro _ h
    cases h
  intro x _ r hr
  apply OkP.bind
  intro r' hr'
  apply OkP.pure
  refine OkP.forIn (P := fun (out : List Json) => ∀ x ∈ out, PairEntry x) hr (fun y _ s hs => ?_) r' hr'
  okfits
  all_goals simp only [ForInStep.value, List.mem_append, List.mem_singleton]
  all_goals first
    | exact hs
    | (intro z hz; rcases hz with hz | rfl
       · exact hs z hz
       · exact ⟨_, _, _, _, rfl⟩)

theorem setPairs_entries (a : Wire.Admitted) (R : ReadingSet) (RJ : Wire.SetJ) :
    OkP (fun out => ∀ x ∈ out, PairEntry x) (setPairs a R RJ) :=
  setPairsWith_entries id a R RJ

/-- A row of `validateResult`: one content-bearing set with its candidates and pairs. -/
def SetEntry (req : Json) (x : Json) : Prop :=
  ∃ (s : String) (v : Json) (cands pairs : List Json) (fs : Json), x = Json.mkObj [("set", .str s), ("version", v), ("candidates", Json.arr cands.toArray),
      ("pairs", Json.arr pairs.toArray), ("findings", fs)] ∧
    (∀ c ∈ cands, Fits req (skel% "readings-route.json#/$defs/candidate") c) ∧ (∀ p ∈ pairs, PairEntry p)

/-- The fields `validateResultWith` returns: no content-bearing set, or one entry per content-bearing set. -/
def ValidateRows (req : Json) (l : List (String × Json)) : Prop :=
  l = [("content_bearing", .bool false)] ∨
    ∃ rows : List Json, l = [("content_bearing", .bool true), ("sets", Json.arr rows.toArray)] ∧
      ∀ x ∈ rows, SetEntry req x

theorem validateWith_rows (adjust : PairFacts → PairFacts) (a : Wire.Admitted) :
    OkP (ValidateRows req) (validateResultWith adjust a) := by
  unfold validateResultWith
  simp only []
  okfits
  · exact Or.inl rfl
  rename_i rows hrows
  have hrows := OkP.forIn (P := fun (out : List Json) => ∀ x ∈ out, SetEntry req x) (fun _ h => by cases h) (fun R _ r hr => by
      okfits
      all_goals simp only [ForInStep.value, List.mem_append, List.mem_singleton]
      all_goals first
        | exact hr
        | (intro z hz
           rcases hz with hz | rfl
           · exact hr z hz
           · exact ⟨_, _, _, _, _, rfl, OkP.mapM (fun i _ => candidate_fits a R i) _ ‹_›,
               setPairsWith_entries adjust a R _ _ ‹_›⟩)) rows hrows
  exact Or.inr ⟨_, rfl, hrows⟩

theorem validate_fits (id : String) (a : Wire.Admitted) :
    OkP (fun l => Fits req (skel% "readings-route.json#/$defs/validate") (VE.Route.Wire.ok id l)) (validateResult a) := by
  intro l hl
  rcases validateWith_rows _root_.id a l hl with rfl | ⟨rows, rfl, hrows⟩
  · simp only [VE.Route.Wire.ok]
    fits
  · simp only [VE.Route.Wire.ok]
    fits
    obtain ⟨s, v, cands, pairs, fs, rfl, hc, hp⟩ := hrows _ ‹_›
    fits
    · exact hc _ ‹_›
    · obtain ⟨r, o, f, sid, rfl⟩ := hp _ ‹_›
      fits using pair_fits

/-! The S2a kinds (`runS2`). -/

theorem elaborateFields_fits (id : String) (nd : Bool) (n : Nat) (D : Doc) :
    Fits req (skel% "readings-route.json#/$defs/elaborate") (okWith id (elaborateFields nd n D)) := by
  simp only [okWith, VE.Route.Wire.ok, elaborateFields]
  split <;> (try simp only [choicesJson]) <;> (try split) <;>
    simp only [List.cons_append, List.nil_append, vocabularyJson, slotJson, sizesJson]
  all_goals fits

theorem elaborate_fits (id : String) (b : Wire.Admitted2) :
    OkFits req (skel% "readings-route.json#/$defs/elaborate") (runElaborate id b) := by
  unfold runElaborate
  okfits
  exact elaborateFields_fits _ _ _ _

theorem conflict_fits (id : String) (b : Wire.Admitted2) (j : Json) :
    OkFits req (skel% "readings-route.json#/$defs/conflict") (runConflict id b j) := by
  unfold runConflict
  okfits
  all_goals (try simp only [okWith, VE.Route.Wire.ok])
  all_goals fits

theorem certificate_fits (id : String) (b : Wire.Admitted2) (j : Json) :
    OkFits req (skel% "readings-route.json#/$defs/certificate") (runCertificate id b j) := by
  unfold runCertificate
  okfits
  simp only [okWith, VE.Route.Wire.ok]
  fits

theorem model_fits (id : String) (b : Wire.Admitted2) (j : Json) :
    OkFits req (skel% "readings-route.json#/$defs/model") (runModel id b j) := by
  unfold runModel
  okfits
  all_goals (try simp only [okWith, VE.Route.Wire.ok])
  all_goals fits

theorem deadAnswer_fits (id : String) (D : Doc) (j : Json) :
    OkFits req (skel% "readings-route.json#/$defs/dead") (deadAnswer id D j) := by
  unfold deadAnswer
  okfits
  all_goals (try simp only [okWith, VE.Route.Wire.ok])
  all_goals fits

theorem dead_fits (id : String) (b : Wire.Admitted2) (j : Json) :
    OkFits req (skel% "readings-route.json#/$defs/dead") (runDead id b j) := by
  unfold runDead
  exact deadAnswer_fits _ _ _

theorem choice_fits (lower : List String → Json → Json) (id : String) (b : Wire.Admitted2) (j : Json) :
    OkFits req (skel% "readings-route.json#/$defs/choice_answer") (runChoice lower id b j) := by
  unfold runChoice
  okfits
  all_goals (try simp only [okWith, VE.Route.Wire.ok])
  all_goals fits

/-! Under the unspecified completion (readings-defaults.md 3; `UnspecifiedWire.lean`, `runS2ND`). -/

theorem elaborateND_fits (id : String) (r : Wire.AdmittedND) :
    OkFits req (skel% "readings-route.json#/$defs/elaborate") (runElaborateND id r) := by
  unfold runElaborateND runElaborateNDWith
  okfits
  simp only [List.append_nil]
  exact elaborateFields_fits _ _ _ _

theorem choiceND_fits (id : String) (r : Wire.AdmittedND) (j : Json) :
    OkFits req (skel% "readings-route.json#/$defs/choice_answer") (runChoiceND id r j) := by
  unfold runChoiceND
  okfits
  all_goals (try simp only [okWith, VE.Route.Wire.ok])
  all_goals fits

theorem fillPremises_fits (N : NDoc) (side : String → Nat → VE.Rights.RightsDoc × List VE.Formula) :
    Fits req (skel% "readings-route.json#/$defs/fill_premises") (Wire.fillPremisesJson N side) := by
  unfold Wire.fillPremisesJson Wire.encF
  fits

theorem filled_fits (r : Wire.AdmittedND) :
    OkFits req (skel% "readings-route.json#/$defs/filled") (Wire.filledJson r) := by
  unfold Wire.filledJson
  okfits
  fits

theorem elaborateNDFilled_fits (id : String) (f : Wire.AdmittedNDFull) :
    OkFits req (skel% "readings-route.json#/$defs/elaborate") (runElaborateNDFilled id f) := by
  unfold runElaborateNDFilled runElaborateNDWith
  okfits
  rename_i extra hextra
  cases hf : Wire.filledJson f.r with
  | error e => simp only [hf, bind, Except.bind] at hextra; cases hextra
  | ok fl =>
    simp only [hf, bind, Except.bind, pure, Except.pure, Except.ok.injEq] at hextra
    subst hextra
    simp only [okWith, VE.Route.Wire.ok, elaborateFields]
    split <;> (try simp only [choicesJson]) <;> (try split) <;>
      simp only [List.cons_append, List.nil_append, vocabularyJson, slotJson, sizesJson]
    all_goals fits
    all_goals exact filled_fits _ _ hf

theorem validateND_fits (id : String) (f : Wire.AdmittedNDFull) :
    OkFits req (skel% "readings-route.json#/$defs/validate") (runValidateND id f) := by
  unfold runValidateND
  okfits
  rename_i rows hrows env henv
  rcases validateWith_rows _ _ rows hrows with rfl | ⟨rows, rfl, hrows⟩
  · simp only [VE.Route.Wire.ok, List.cons_append, List.nil_append]
    fits
    exact filled_fits _ _ henv
  · simp only [VE.Route.Wire.ok, List.cons_append, List.nil_append]
    fits
    all_goals first
      | exact filled_fits _ _ henv
      | (obtain ⟨s, v, cands, pairs, fs, rfl, hc, hp⟩ := hrows _ ‹_›
         fits
         · exact hc _ ‹_›
         · obtain ⟨r, o, f, sid, rfl⟩ := hp _ ‹_›
           fits using pair_fits)

theorem separateND_fits (id : String) (f : Wire.AdmittedNDFull) (j : Json) :
    OkFits j (skel% "readings-route.json#/$defs/separate") (runSeparateND id f j) := by
  unfold runSeparateND
  okfits
  simp only [VE.Route.Wire.ok]
  fits using pair_fits

theorem runS2_fits (lower : List String → Json → Json) (id kind : String) (b : Wire.Admitted2) (j : Json)
    (hK : KindRead "evaluate" req kind) : OkFits req Skeletons.readingsRoute (runS2 lower id kind b j) := by
  unfold runS2
  rcases hK with hK | ⟨hK, hd⟩
  all_goals (try subst hd)
  all_goals okfits
  all_goals kind_norm
  all_goals first
    | (intro v hv; fits_from elaborate_fits _ _ v hv)
    | (intro v hv; fits_from conflict_fits _ _ _ v hv)
    | (intro v hv; fits_from certificate_fits _ _ _ v hv)
    | (intro v hv; fits_from model_fits _ _ _ v hv)
    | (intro v hv; fits_from dead_fits _ _ _ v hv)
    | (intro v hv; fits_from choice_fits _ _ _ _ v hv)

/-! The status words a fold yields (the result's closed enumerations). -/

theorem foldConflict_range (rs : List (Choice × ChoiceResult)) :
    foldConflict rs = .free ∨ foldConflict rs = .conflict ∨ foldConflict rs = .unknown := by
  unfold foldConflict
  split
  · exact Or.inr (Or.inl rfl)
  · split
    · exact Or.inl rfl
    · exact Or.inr (Or.inr rfl)

theorem foldPremises_range (rs : List (Choice × ChoiceResult)) :
    foldPremises rs = .model ∨ foldPremises rs = .inconsistent ∨ foldPremises rs = .unknown := by
  unfold foldPremises
  split
  · exact Or.inl rfl
  · split
    · exact Or.inr (Or.inl rfl)
    · exact Or.inr (Or.inr rfl)

theorem conflictWord_fits (rs : List (Choice × ChoiceResult)) (h : foldConflict rs = .free → False) :
    Fits req (.strIn ["CONFLICT", "UNKNOWN"]) (.str (word (foldConflict rs))) := by
  apply Fits.strIn_lit
  rcases foldConflict_range rs with h' | h' | h' <;> simp only [h'] at h ⊢
  · exact (h trivial).elim
  all_goals decide

theorem premisesWord_fits (rs : List (Choice × ChoiceResult)) :
    Fits req (.strIn ["model", "INCONSISTENT", "UNKNOWN"]) (.str (word (foldPremises rs))) := by
  apply Fits.strIn_lit
  rcases foldPremises_range rs with h' | h' | h' <;> simp only [h'] <;> decide

theorem candidateWord_fits (rs : List (Choice × ChoiceResult)) :
    Fits req (.strIn ["dead", "model", "INCONSISTENT", "UNKNOWN"]) (.str (word (foldPremises rs))) := by
  apply Fits.strIn_lit
  rcases foldPremises_range rs with h' | h' | h' <;> simp only [h'] <;> decide

theorem modelWord_fits (x : ChoiceResult) (h : (x == .model) = true) :
    Fits req (.strIn ["model"]) (.str (word x)) := by
  apply Fits.strIn_lit
  cases x <;> first | decide | (exact absurd h (by decide))

theorem reasonOf_status {cs rs : List (Choice × ChoiceResult)} {s : ChoiceResult} {c : Choice}
    (h : reasonOf cs rs = some (.conflictStatus s c)) : s = .conflict ∨ s = .unknown := by
  unfold reasonOf at h
  split at h
  · split at h
    · simp only [Option.map_eq_some_iff] at h
      obtain ⟨_, _, h⟩ := h
      cases h
    · cases h
  · rename_i hs
    simp only [Option.map_eq_some_iff, Reason.conflictStatus.injEq] at h
    obtain ⟨_, _, rfl, _⟩ := h
    rcases foldConflict_range cs with h' | h' | h'
    · exact absurd h' hs
    · exact Or.inl h'
    · exact Or.inr h'

theorem reasonWord_fits {cs rs : List (Choice × ChoiceResult)} {s : ChoiceResult} {c : Choice}
    (h : reasonOf cs rs = some (.conflictStatus s c)) :
    Fits req (.strIn ["CONFLICT", "UNKNOWN"]) (.str (word s)) := by
  apply Fits.strIn_lit
  rcases reasonOf_status h with rfl | rfl <;> decide

theorem result_conflict_fits (D : Doc) (A : Choice) (assumed : Option Choice)
    (infos : Option (List RowInfo)) (over : List RowInfo) (dead : List Json) :
    Fits req (skel% "readings-route.json#/$defs/verdicts_conflict") (resultOf "conflict" D A assumed infos over dead) := by
  unfold resultOf conflictResult overBudgetFields overBudgetRest
  (repeat' split) <;> (try (exfalso; simp_all (config := {decide := true}); done)) <;>
    (try simp only [List.cons_append, List.nil_append]) <;> fits using conflictWord_fits

theorem result_premises_fits (D : Doc) (A : Choice) (assumed : Option Choice)
    (infos : Option (List RowInfo)) (over : List RowInfo) (dead : List Json) :
    Fits req (skel% "readings-route.json#/$defs/verdicts_premises") (resultOf "premises" D A assumed infos over dead) := by
  unfold resultOf premisesResult overBudgetFields overBudgetRest
  (repeat' split) <;> (try (exfalso; simp_all (config := {decide := true}); done)) <;>
    (try simp only [List.cons_append, List.nil_append]) <;>
    fits using premisesWord_fits, candidateWord_fits, modelWord_fits

theorem result_query_fits (D : Doc) (A : Choice) (assumed : Option Choice)
    (infos : Option (List RowInfo)) (over : List RowInfo) (dead : List Json) :
    Fits req (skel% "readings-route.json#/$defs/verdicts_query") (resultOf "query" D A assumed infos over dead) := by
  unfold resultOf entailmentResult overBudgetFields overBudgetRest
  cases assumed <;> simp only [assumedFields] <;> (repeat' split) <;>
    (try (exfalso; simp_all (config := {decide := true}); done)) <;>
    (try simp only [List.cons_append, List.nil_append, List.append_nil]) <;> fits using reasonWord_fits


theorem line_fits (l : Line) : Fits req (skel% "readings-route.json#/$defs/verdicts_line") l.json := by
  unfold Line.json
  fits

theorem perChoiceJson_fits (question : String) (i : RowInfo) :
    Fits req (skel% "readings-route.json#/$defs/verdicts_row") (perChoiceJson question i) := by
  unfold perChoiceJson
  (repeat' split) <;> simp only [List.cons_append, List.nil_append, List.append_nil] <;> fits

theorem deadNote_fits (D : Doc) (infos : List RowInfo) (dead : List Json) :
    ∀ x ∈ (deadOf D infos dead).2, Fits req (skel% "readings-route.json#/$defs/verdicts_dead") x := by
  intro x hx
  simp only [deadOf, List.mem_map] at hx
  obtain ⟨d, _, rfl⟩ := hx
  split <;> fits

theorem verdictsAnswer_fits (id question : String) (nd : Bool) (D : Doc) (A : Choice)
    (assumed : Option Choice) (infos : Option (List RowInfo)) (over : List RowInfo) (dead : List Json)
    (hq : verdictsQuestions.contains question) :
    Fits req (skel% "readings-route.json#/$defs/verdicts") (verdictsAnswer id question nd D A assumed infos over dead) := by
  simp only [verdictsQuestions, List.contains_cons, List.contains_nil, Bool.or_false, Bool.or_eq_true, beq_iff_eq] at hq
  rcases hq with rfl | rfl | rfl
  all_goals
    unfold verdictsAnswer answerFields deadReadingsJson untakenJson
    simp only [okWith, VE.Route.Wire.ok]
    fits
  all_goals first
    | apply result_conflict_fits
    | apply result_premises_fits
    | apply result_query_fits
    | apply perChoiceJson_fits
    | apply line_fits
    | (apply deadNote_fits; assumption)

theorem verdicts_fits (lower : List String → Json → Json) (id : String) (b : Wire.Admitted2) (j : Json) :
    OkFits req (skel% "readings-route.json#/$defs/verdicts") (runVerdicts lower id b j) := by
  unfold runVerdicts
  okfits
  all_goals first
    | (apply verdictsAnswer_fits; assumption)
    | skip

theorem runS2ND_fits (lower : List String → Json → Json) (id kind : String) (b : Wire.Admitted2) (j : Json)
    (hK : KindRead "evaluate" req kind) : OkFits req Skeletons.readingsRoute (runS2ND lower id kind b j) := by
  have hK0 := hK
  unfold runS2ND
  rcases hK with hK | ⟨hK, hd⟩
  all_goals (try subst hd)
  all_goals okfits
  all_goals first
    | exact runS2_fits _ _ _ _ _ hK0
    | skip
  all_goals (try (intro v hv; fits_from verdicts_fits _ _ _ _ v hv))
  all_goals (try kind_norm)
  all_goals first
    | (intro v hv; fits_from elaborateNDFilled_fits _ _ v hv)
    | (intro v hv; fits_from choiceND_fits _ _ _ v hv)
    | (intro v hv; fits_from deadAnswer_fits _ _ _ v hv)

theorem validateOne_fits (id : String) (environment document : Json) :
    OkFits req (skel% "readings-route.json#/$defs/validate") (validateOne id environment document) := by
  unfold validateOne
  okfits
  all_goals first
    | fits_from validate_fits _ _ _ ‹_›
    | (intro v hv; fits_from validateND_fits _ _ v hv)

theorem elaborateOne_fits (j : Json) (id : String) (environment document : Json) :
    OkFits req (skel% "readings-route.json#/$defs/elaborate") (elaborateOne j id environment document) := by
  unfold elaborateOne runS2ND runS2
  okfits
  all_goals (try simp only [String.reduceEq, Bool.false_eq_true, String.reduceBEq] at *)
  all_goals okfits
  all_goals first
    | (intro v hv; fits_from elaborate_fits _ _ v hv)
    | (intro v hv; fits_from elaborateNDFilled_fits _ _ v hv)
    | exact elaborate_fits _ _
    | exact elaborateND_fits _ _

/-- One case of the split (`runOne`): the runners of `runCase` before the split, on the case's environment and
    document. -/
theorem runOne_fits (j : Json) (id kind : String) (environment document : Json) (hK : KindRead "evaluate" j kind) :
    OkFits j Skeletons.readingsRoute (runOne j id kind environment document) := by
  have hK0 := hK
  unfold runOne
  rcases hK with hK | ⟨hK, hd⟩
  all_goals (try subst hd)
  all_goals okfits
  all_goals (try kind_norm)
  all_goals first
    | exact runS2ND_fits _ _ _ _ _ hK0
    | (intro v hv; fits_from validateOne_fits _ _ _ v hv)
    | (intro v hv; fits_from separateND_fits _ _ _ v hv)
    | (simp only [VE.Route.Wire.ok]; fits using pair_fits)

/-- A case's environment or document in its component row (`asObject`) is an object. -/
theorem asObject_fits (j : Json) : Fits req Skel.anyObject (asObject j) := by
  unfold asObject Skel.anyObject
  split
  · exact Fits.obj (fun _ _ _ => Fits.any _) (fun _ h => by cases h) (fun _ h => by cases h)
  · exact Fits.mkObj (by decide) (fun _ h => by cases h)

theorem componentRows (j : Json) (id kind : String) (parts : List (String × Json × Json)) :
    OkP (fun rows => ∀ r ∈ rows, ∃ (name : String) (e d d' a : Json), r = componentRowOf kind name e d d' a ∧
      (kind = "readings-validate" → Fits j (skel% "readings-route.json#/$defs/validate") a) ∧
      (kind ≠ "readings-validate" → Fits j (skel% "readings-route.json#/$defs/elaborate") a))
      (parts.mapM (fun p => do
        let a ← if kind == "readings-validate" then validateOne id p.2.1 p.2.2 else elaborateOne j id p.2.1 p.2.2
        pure (componentRowOf kind p.1 p.2.1 p.2.2 p.2.2 a))) := by
  apply OkP.mapM
  intro p _
  by_cases hk : kind = "readings-validate"
  · subst hk
    simp only [beq_self_eq_true, reduceIte]
    apply OkP.bind
    intro a ha
    exact OkP.pure ⟨_, _, _, _, _, rfl, fun _ => validateOne_fits _ _ _ a ha, fun h => absurd rfl h⟩
  · have : (kind == "readings-validate") = false := by simpa using hk
    simp only [this, Bool.false_eq_true, reduceIte]
    apply OkP.bind
    intro a ha
    exact OkP.pure ⟨_, _, _, _, _, rfl, fun h => absurd h hk, fun _ => elaborateOne_fits _ _ _ _ a ha⟩

/-- Per case of the split (`runComponents`), for `readings-validate` and `readings-elaborate`. -/
theorem runComponents_fits (j : Json) (id kind : String) (parts : List (String × Json × Json))
    (hK : KindRead "evaluate" j kind) (hv : kind = "readings-validate" ∨ kind = "readings-elaborate") :
    OkFits j Skeletons.readingsRoute (runComponents j id kind parts) := by
  unfold runComponents
  apply OkP.bind
  intro rows hrows
  apply OkP.pure
  have hr := componentRows j id kind parts rows hrows
  rcases hK with hK | ⟨hK, hd⟩
  · rcases hv with rfl | rfl
    · simp only [VE.Route.Wire.ok]
      fits
      obtain ⟨name, e, d, d', a, rfl, h1, _⟩ := hr _ ‹_›
      unfold componentRowOf componentRow
      simp only [String.reduceBEq, Bool.false_eq_true, if_false]
      fits
      exact h1 rfl
    · simp only [VE.Route.Wire.ok]
      fits
      obtain ⟨name, e, d, d', a, rfl, _, h2⟩ := hr _ ‹_›
      unfold componentRowOf
      simp only [beq_self_eq_true, if_true]
      fits
      all_goals first
        | exact h2 (by decide)
        | exact asObject_fits _
  · subst hd
    simp at hv

theorem or_beq {k a b : String} (h : (k == a || k == b) = true) : k = a ∨ k = b := by simpa using h

theorem runAdmitted_fits (j : Json) (id kind : String) (ready : ComponentAdmission)
    (hK : KindRead "evaluate" j kind) : OkFits j Skeletons.readingsRoute (runAdmitted j id kind ready) := by
  have hK0 := hK
  unfold runAdmitted
  rcases hK with hK | ⟨hK, hd⟩
  all_goals (try subst hd)
  all_goals (cases ready)
  all_goals okfits
  all_goals (try kind_norm)
  all_goals first
    | exact runS2_fits _ _ _ _ _ hK0
    | (intro v hv; fits_from verdicts_fits _ _ _ _ v hv)
    | fits_from validate_fits _ _ _ ‹_›
    | (intro v hv; fits_from validateND_fits _ _ v hv)
    | (intro v hv; fits_from separateND_fits _ _ _ v hv)
    | (intro v hv; fits_from elaborateNDFilled_fits _ _ v hv)
    | (intro v hv; fits_from choiceND_fits _ _ _ v hv)
    | (intro v hv; fits_from deadAnswer_fits _ _ _ v hv)
    | (simp only [VE.Route.Wire.ok]; fits using pair_fits)

theorem runAdmitted_validate_fits (j : Json) (id : String) (ready : ComponentAdmission) :
    OkFits j (skel% "readings-route.json#/$defs/validate")
      (runAdmitted j id "readings-validate" ready) := by
  cases ready with
  | s1 a =>
    simp only [runAdmitted, beq_self_eq_true, reduceIte]
    okfits
    exact validate_fits _ _ _ ‹_›
  | s2 b =>
    simp only [runAdmitted, beq_self_eq_true, reduceIte]
    okfits
    exact validate_fits _ _ _ ‹_›
  | nd f =>
    simpa [runAdmitted] using validateND_fits (req := j) id f

theorem runAdmitted_elaborate_fits (j : Json) (id : String) (ready : ComponentAdmission) :
    OkFits j (skel% "readings-route.json#/$defs/elaborate")
      (runAdmitted j id "readings-elaborate" ready) := by
  cases ready with
  | s1 _ => simp [runAdmitted, OkFits, OkP]
  | s2 b => simpa [runAdmitted, runS2] using elaborate_fits (req := j) id b
  | nd f => simpa [runAdmitted] using elaborateNDFilled_fits (req := j) id f

theorem admittedComponentRows (j : Json) (id kind : String)
    (parts : List (String × Json × Json × Json × ComponentAdmission))
    (hv : kind = "readings-validate" ∨ kind = "readings-elaborate") :
    OkP (fun rows => ∀ r ∈ rows, ∃ (name : String) (e d d' a : Json), r = componentRowOf kind name e d d' a ∧
      (kind = "readings-validate" → Fits j (skel% "readings-route.json#/$defs/validate") a) ∧
      (kind ≠ "readings-validate" → Fits j (skel% "readings-route.json#/$defs/elaborate") a))
      (parts.mapM (fun p =>
        do pure (componentRowOf kind p.1 p.2.1 p.2.2.1 p.2.2.2.1 (← runAdmitted j id kind p.2.2.2.2)))) := by
  apply OkP.mapM
  intro p _
  by_cases hk : kind = "readings-validate"
  · subst hk
    apply OkP.bind
    intro a ha
    exact OkP.pure ⟨_, _, _, _, _, rfl, fun _ => runAdmitted_validate_fits _ _ _ a ha, fun h => absurd rfl h⟩
  · apply OkP.bind
    intro a ha
    exact OkP.pure ⟨_, _, _, _, _, rfl, fun h => absurd h hk, fun _ =>
      by have he : kind = "readings-elaborate" := hv.resolve_left hk
         subst he
         exact runAdmitted_elaborate_fits _ _ _ a ha⟩

theorem runAdmittedComponents_fits (j : Json) (id kind : String)
    (parts : List (String × Json × Json × Json × ComponentAdmission)) (hK : KindRead "evaluate" j kind)
    (hv : kind = "readings-validate" ∨ kind = "readings-elaborate") :
    OkFits j Skeletons.readingsRoute (runAdmittedComponents j id kind parts) := by
  unfold runAdmittedComponents
  apply OkP.bind
  intro rows hrows
  apply OkP.pure
  have hr := admittedComponentRows j id kind parts hv rows hrows
  rcases hK with hK | ⟨hK, hd⟩
  · rcases hv with rfl | rfl
    · simp only [VE.Route.Wire.ok]
      fits
      obtain ⟨name, e, d, d', a, rfl, h1, _⟩ := hr _ ‹_›
      unfold componentRowOf componentRow
      simp only [String.reduceBEq, Bool.false_eq_true, if_false]
      fits
      exact h1 rfl
    · simp only [VE.Route.Wire.ok]
      fits
      obtain ⟨name, e, d, d', a, rfl, _, h2⟩ := hr _ ‹_›
      unfold componentRowOf
      simp only [beq_self_eq_true, if_true]
      fits
      all_goals first
        | exact h2 (by decide)
        | exact asObject_fits _
  · subst hd
    simp at hv

/-! ### The product over a document's components (`runProduct`, plan RD-4b) -/

theorem anyWord_fits (x : ChoiceResult) :
    Fits req (.strIn ["CONFLICT-FREE", "CONFLICT", "UNKNOWN", "proved", "refuted", "model", "INCONSISTENT"])
      (.str (word x)) := by
  apply Fits.strIn_lit
  cases x <;> decide

theorem routeText_fits (r : Route) :
    Fits req (.strIn ["w2", "pending", "abstention", "superposed", "enumerated"]) (.str r.text) := by
  apply Fits.strIn_lit
  cases r <;> decide

theorem productConflict_range (rows : List ComponentRows) :
    productConflict rows = .free ∨ productConflict rows = .conflict ∨ productConflict rows = .unknown := by
  unfold productConflict
  split
  · exact Or.inl rfl
  · split
    · exact Or.inr (Or.inl rfl)
    · exact Or.inr (Or.inr rfl)

theorem productConflictWord_fits (rows : List ComponentRows) :
    Fits req (.strIn ["CONFLICT-FREE", "CONFLICT", "UNKNOWN"]) (.str (word (productConflict rows))) := by
  apply Fits.strIn_lit
  rcases productConflict_range rows with h | h | h <;> simp only [h] <;> decide

theorem productPremisesWord_fits (rows : List ComponentRows) :
    Fits req (.strIn ["model", "UNKNOWN"]) (.str (word (productPremises rows))) := by
  apply Fits.strIn_lit
  unfold productPremises
  split <;> decide

theorem othersReason_status {rows : List ComponentRows} {k : Nat} {s : ChoiceResult} {j : Nat} {c : Choice}
    (h : othersReason rows k = some (s, j, c)) : s = .conflict ∨ s = .unknown := by
  unfold othersReason at h
  simp only at h
  split at h
  · rename_i x hx
    cases h
    obtain ⟨y, _, hy⟩ := List.exists_of_findSome?_eq_some hx
    split at hy
    · simp only [Option.map_eq_some_iff] at hy
      obtain ⟨_, _, hy⟩ := hy
      cases hy
      exact Or.inl rfl
    · cases hy
  · obtain ⟨y, _, hy⟩ := List.exists_of_findSome?_eq_some h
    split at hy
    · simp only [Option.map_eq_some_iff] at hy
      obtain ⟨_, _, hy⟩ := hy
      cases hy
      exact Or.inr rfl
    · cases hy

theorem othersReasonWord_fits {rows : List ComponentRows} {k : Nat} {s : ChoiceResult} {j : Nat} {c : Choice}
    (h : othersReason rows k = some (s, j, c)) : Fits req (.strIn ["CONFLICT", "UNKNOWN"]) (.str (word s)) := by
  apply Fits.strIn_lit
  rcases othersReason_status h with rfl | rfl <;> decide

theorem partRun_answer_fits (r : PartRun) :
    Fits req (skel% "readings-route.json#/$defs/verdicts") r.answer :=
  verdictsAnswer_fits _ _ _ _ _ _ _ _ _ r.hq

theorem componentJson_fits (r : PartRun) :
    Fits req (skel% "readings-route.json#/$defs/product_component") (componentJson r) := by
  unfold componentJson
  fits
  all_goals first
    | exact routeText_fits _
    | exact verdictsAnswer_fits _ _ _ _ _ _ _ _ _ r.hq

theorem entryJson_fits (x : Option String × Line) :
    Fits req (skel% "readings-route.json#/$defs/product_line") (entryJsonP x) := by
  unfold entryJsonP entryJson
  cases x.1 <;> fits

theorem statusRows_fits (runs : List PartRun) (f : ComponentRows → ChoiceResult) :
    Fits req (skel% "readings-route.json#/$defs/verdicts_component_status") (statusRows runs f) := by
  unfold statusRows
  fits
  all_goals (try exact anyWord_fits _)

theorem productResult_conflict_fits (runs : List PartRun) (k : Nat) :
    Fits req (skel% "readings-route.json#/$defs/product_conflict") (productResult "conflict" runs k) := by
  unfold productResult
  simp only [beq_self_eq_true, if_true]
  fits
  all_goals first
    | exact productConflictWord_fits _
    | exact statusRows_fits _ _

theorem productResult_premises_fits (runs : List PartRun) (k : Nat) :
    Fits req (skel% "readings-route.json#/$defs/product_premises") (productResult "premises" runs k) := by
  unfold productResult
  simp only [String.reduceBEq, Bool.false_eq_true, if_false, beq_self_eq_true, if_true]
  fits
  all_goals first
    | exact productPremisesWord_fits _
    | exact statusRows_fits _ _

theorem productResult_query_fits (runs : List PartRun) (k : Nat) :
    Fits req (skel% "readings-route.json#/$defs/product_query") (productResult "query" runs k) := by
  unfold productResult
  simp only [String.reduceBEq, Bool.false_eq_true, if_false]
  (repeat' split) <;> fits
  all_goals (try (apply othersReasonWord_fits; assumption))

theorem productAnswer_fits (id question : String) (runs : List PartRun) (k : Nat) (sentence : Option String)
    (hq : verdictsQuestions.contains question) :
    Fits req (skel% "readings-route.json#/$defs/verdicts_components") (productAnswer id question runs k sentence) := by
  simp only [verdictsQuestions, List.contains_cons, List.contains_nil, Bool.or_false, Bool.or_eq_true, beq_iff_eq] at hq
  rcases hq with rfl | rfl | rfl
  all_goals
    unfold productAnswer
    simp only [okWith, VE.Route.Wire.ok]
    cases sentence <;> fits
  all_goals first
    | exact componentJson_fits _
    | exact productResult_conflict_fits _ _
    | exact productResult_premises_fits _ _
    | exact productResult_query_fits _ _
    | exact entryJson_fits _
    | exact routeText_fits _
    | exact partRun_answer_fits _
    | exact productConflictWord_fits _
    | exact productPremisesWord_fits _
    | exact anyWord_fits _
    | exact line_fits _
    | (apply othersReasonWord_fits; assumption)

theorem runProduct_fits (j : Json) (id : String) (cases : List (String × Json × Json)) :
    OkFits req (skel% "readings-route.json#/$defs/verdicts_components") (runProduct j id cases) := by
  unfold runProduct
  okfits
  all_goals first
    | (apply productAnswer_fits; assumption)
    | skip

theorem runCase_fits (j : Json) : OkFits j Skeletons.readingsRoute (runCase j) := by
  unfold runCase
  okfits
  all_goals read_kind
  all_goals first
    | (intro v hv; fits_from runProduct_fits _ _ _ v hv)
    | exact runAdmitted_fits _ _ _ _ (KindRead.of_str ‹_›)
    | exact runAdmitted_fits _ _ _ _ (Or.inr ⟨‹_›, rfl⟩)
    | exact runAdmittedComponents_fits _ _ _ _ (KindRead.of_str ‹_›) (or_beq ‹_›)
    | exact runAdmittedComponents_fits _ _ _ _ (Or.inr ⟨‹_›, rfl⟩) (or_beq ‹_›)
    | exact runOne_fits _ _ _ _ _ (KindRead.of_str ‹_›)
    | exact runOne_fits _ _ _ _ _ (Or.inr ⟨‹_›, rfl⟩)
    | exact runComponents_fits _ _ _ _ (KindRead.of_str ‹_›) (or_beq ‹_›)
    | exact runComponents_fits _ _ _ _ (Or.inr ⟨‹_›, rfl⟩) (or_beq ‹_›)

/-! ## The lower routes

A case of another kind is answered by the lower route `Compose.dispatch` names, on the case with
`readings@1` dropped from its environment's profiles (`runLower`). Its row fits for the rewritten
case, and so for the case: every condition on the case in the lower routes' skeletons is on its
kind, on a field other than `environment`, or the lower routes' own tests of the case, which read
no profile but their own (`*_lower`). -/

section Lower

theorem toList_of_mapM {xs : List Json} {l : List String} (h : xs.mapM Json.getStr? = .ok l) : xs = l.map Json.str := by
  induction xs generalizing l with
  | nil => cases h; rfl
  | cons x xs ih =>
    simp only [List.mapM_cons] at h
    cases hx : x.getStr? with
    | error e => rw [hx] at h; cases h
    | ok s =>
      cases hr : xs.mapM Json.getStr? with
      | error e => rw [hx, hr] at h; cases h
      | ok r =>
        rw [hx, hr] at h
        cases h
        rw [ResponseShape.Encoders.Common.str_of_getStr hx, ih hr]
        rfl

theorem strings_arr {P : Json} {l : List String} (h : VE.Bridge.strings P = .ok l) : P = .arr (l.map Json.str).toArray := by
  unfold VE.Bridge.strings at h
  cases P with
  | arr a =>
    simp only [Json.getArr?] at h
    have := toList_of_mapM h
    rw [← this]
  | _ => simp [Json.getArr?] at h <;> cases h

theorem any_filter_map {l : List String} {r : String} (q : Json → Bool) (hq : q (.str r) = false) :
    ((l.filter (· != r)).map Json.str).any q = (l.map Json.str).any q := by
  induction l with
  | nil => rfl
  | cons x xs ih =>
    by_cases hx : x = r
    · subst hx; simp [hq, ih]
    · simp [hx, ih]

theorem toJson_strings (l : List String) : toJson l = Json.arr (l.map Json.str).toArray := by
  show Json.arr (l.toArray.map toJson) = _
  simp [toJson]

/-- Setting a field of a well-formed object map. -/
theorem getObjValD_set_ne {m : Std.TreeMap.Raw String Json compare} (wf : m.WF) {k k' : String} (hk : k ≠ k') (v : Json) :
    (Json.obj m |>.setObjVal! k v).getObjValD k' = (Json.obj m).getObjValD k' := by
  simp only [CaseCond.getObjValD_eq]
  rw [getObjVal_setObjVal (j := .obj m) (fun _ h => by cases h; exact wf) rfl hk]

theorem getObjValD_set_eq {m : Std.TreeMap.Raw String Json compare} (wf : m.WF) (k : String) (v : Json) :
    (Json.obj m |>.setObjVal! k v).getObjValD k = v := by
  simp only [Json.setObjVal!, CaseCond.getObjValD_eq, Json.getObjVal?]
  rw [Std.TreeMap.Raw.get?_eq_getElem?, Std.TreeMap.Raw.getElem?_insert_self wf]
  rfl

theorem getObjVal_set_ne {m : Std.TreeMap.Raw String Json compare} (wf : m.WF) {k k' : String} (hk : k ≠ k') (v : Json) :
    (Json.obj m |>.setObjVal! k v).getObjVal? k' = (Json.obj m).getObjVal? k' :=
  getObjVal_setObjVal (j := .obj m) (fun _ h => by cases h; exact wf) rfl hk v


theorem getObjVal_set_eq {m : Std.TreeMap.Raw String Json compare} (wf : m.WF) (k : String) (v : Json) :
    (Json.obj m |>.setObjVal! k v).getObjVal? k = .ok v := by
  simp only [Json.setObjVal!, Json.getObjVal?]
  rw [Std.TreeMap.Raw.get?_eq_getElem?, Std.TreeMap.Raw.getElem?_insert_self wf]
  rfl

theorem mapM_str (l : List String) : (l.map Json.str).mapM Json.getStr? = .ok l := by
  induction l with
  | nil => rfl
  | cons x xs ih => simp only [List.map_cons, List.mapM_cons, Json.getStr?, ih]; rfl

theorem strings_toJson (l : List String) : VE.Bridge.strings (toJson l) = .ok l := by
  rw [toJson_strings]
  unfold VE.Bridge.strings
  simp only [Json.getArr?, List.toList_toArray]
  exact mapM_str l

theorem contains_filter_ne {l : List String} {r p : String} (h : p ≠ r) :
    (l.filter (· != r)).contains p = l.contains p := by
  induction l with
  | nil => rfl
  | cons x xs ih =>
    simp only [List.filter_cons]
    by_cases hx : x = r
    · subst hx
      have : (p == x) = false := beq_eq_false_iff_ne.mpr h
      simp only [bne_self_eq_false, Bool.false_eq_true, ↓reduceIte, ih, List.contains_cons, this, Bool.false_or]
    · have : (x != r) = true := bne_iff_ne.mpr hx
      simp only [this, ↓reduceIte, List.contains_cons, ih]

theorem ok_bind {ε α β : Type} (x : α) (f : α → Except ε β) : (Except.ok x >>= f) = f x := rfl

theorem strip_spec {env env' : Json} (h : VE.Readings.Wire.stripReadings env = .ok env') :
    ∃ P l, env.getObjVal? "profiles" = .ok P ∧ VE.Bridge.strings P = .ok l ∧
      env' = env.setObjVal! "profiles" (toJson (l.filter (· != VE.Readings.Wire.readingsProfile))) := by
  unfold VE.Readings.Wire.stripReadings at h
  obtain ⟨P, hP, h⟩ := VE.Order.ProfileGate.bind_ok h
  obtain ⟨l, hl, h⟩ := VE.Order.ProfileGate.bind_ok h
  exact ⟨P, l, hP, hl, (Except.ok.inj h).symm⟩

theorem getObjValD_of_ok {j v : Json} {k : String} (h : j.getObjVal? k = .ok v) : j.getObjValD k = v := by
  rw [CaseCond.getObjValD_eq, h]; rfl

theorem soft_lower {m e : Std.TreeMap.Raw String Json compare} {env' : Json} (wf : m.WF) (wfe : e.WF)
    (he : (Json.obj m).getObjValD "environment" = .obj e)
    (hs : VE.Readings.Wire.stripReadings (.obj e) = .ok env') :
    VE.SoftNorms.Run.usesSoftPath ((Json.obj m).setObjVal! "environment" env') =
      VE.SoftNorms.Run.usesSoftPath (.obj m) := by
  obtain ⟨P, l, hP, hl, rfl⟩ := strip_spec hs
  have hPa := strings_arr hl
  unfold VE.SoftNorms.Run.usesSoftPath
  simp only [getObjValD_set_eq wf, getObjValD_set_ne wf (show "environment" ≠ "kind" by decide),
    getObjValD_set_ne wf (show "environment" ≠ "norms" by decide),
    getObjValD_set_ne wf (show "environment" ≠ "document" by decide), he,
    getObjValD_set_ne wfe (show "profiles" ≠ "vocabulary" by decide), getObjValD_set_eq wfe,
    getObjValD_of_ok hP, hPa, toJson_strings]
  rw [any_filter_map _ (by decide)]


theorem rights_lower {m e : Std.TreeMap.Raw String Json compare} {env' : Json} (wf : m.WF) (wfe : e.WF)
    (he : (Json.obj m).getObjValD "environment" = .obj e)
    (hs : VE.Readings.Wire.stripReadings (.obj e) = .ok env') :
    VE.Rights.Run.usesRightsPath ((Json.obj m).setObjVal! "environment" env') =
      VE.Rights.Run.usesRightsPath (.obj m) := by
  obtain ⟨P, l, hP, hl, rfl⟩ := strip_spec hs
  have hPa := strings_arr hl
  unfold VE.Rights.Run.usesRightsPath
  simp only [getObjValD_set_eq wf, getObjValD_set_ne wf (show "environment" ≠ "kind" by decide),
    getObjValD_set_ne wf (show "environment" ≠ "document" by decide), he,
    getObjValD_set_ne wfe (show "profiles" ≠ "vocabulary" by decide), getObjValD_set_eq wfe,
    getObjValD_of_ok hP, hPa, toJson_strings]
  rw [any_filter_map _ (by decide)]

theorem layered_lower {e : Std.TreeMap.Raw String Json compare} {env' : Json} (wfe : e.WF)
    (hs : VE.Readings.Wire.stripReadings (.obj e) = .ok env') :
    VE.Norms.Plain.layered env' = VE.Norms.Plain.layered (.obj e) := by
  obtain ⟨P, l, hP, hl, rfl⟩ := strip_spec hs
  have hPa := strings_arr hl
  unfold VE.Norms.Plain.layered
  simp only [getObjValD_set_eq wfe, getObjValD_of_ok hP, hPa, toJson_strings, Array.any_toList.symm,
    List.toList_toArray]
  rw [any_filter_map _ (by decide)]

theorem norms_lower {m e : Std.TreeMap.Raw String Json compare} {env' : Json} (wf : m.WF) (wfe : e.WF)
    (he : (Json.obj m).getObjValD "environment" = .obj e)
    (hs : VE.Readings.Wire.stripReadings (.obj e) = .ok env') :
    VE.Norms.Run.usesNormsPath ((Json.obj m).setObjVal! "environment" env') =
      VE.Norms.Run.usesNormsPath (.obj m) := by
  obtain ⟨P, l, hP, hl, rfl⟩ := strip_spec hs
  unfold VE.Norms.Run.usesNormsPath
  simp only [getObjValD_set_eq wf, getObjValD_set_ne wf (show "environment" ≠ "kind" by decide),
    getObjValD_set_ne wf (show "environment" ≠ "document" by decide), he,
    getObjVal_set_ne wf (show "environment" ≠ "norms" by decide),
    getObjValD_set_ne wfe (show "profiles" ≠ "vocabulary" by decide)]

theorem nd_lower {m e : Std.TreeMap.Raw String Json compare} {env' : Json} (wf : m.WF) (wfe : e.WF)
    (he : (Json.obj m).getObjValD "environment" = .obj e)
    (hs : VE.Readings.Wire.stripReadings (.obj e) = .ok env') :
    VE.NormDefaults.Run.usesNormDefaultsPath ((Json.obj m).setObjVal! "environment" env') =
      VE.NormDefaults.Run.usesNormDefaultsPath (.obj m) := by
  obtain ⟨P, l, hP, hl, rfl⟩ := strip_spec hs
  unfold VE.NormDefaults.Run.usesNormDefaultsPath VE.NormDefaults.Wire.hasProfile VE.NormDefaults.Wire.profilesOf
    VE.NormDefaults.Wire.unspecifiedNames
  simp only [getObjValD_set_eq wf, getObjValD_set_ne wf (show "environment" ≠ "kind" by decide), he,
    getObjVal_set_ne wfe (show "profiles" ≠ "vocabulary" by decide), getObjVal_set_eq wfe, hP,
    hl]
  rw [ok_bind, ok_bind, strings_toJson, hl]
  simp only [Except.toOption, Option.getD,
    contains_filter_ne (r := VE.Readings.Wire.readingsProfile) (p := VE.NormDefaults.Wire.profile) (by decide)]


/-- The conditions the lower routes' skeletons put on the case, each read the same of the case and
of its rewrite: a condition other than a conjunction (`atomInv`), or a conjunction of those. -/
def atomInv : CaseCond → Bool
  | .kind _ => true
  | .lacks k => k != "environment"
  | .path [k] => k != "environment"
  | .decided d => d == .rightsPath || d == .softPath || d == .normDefaultsPath || d == .normsPath
  | _ => false

def lowerInv : CaseCond → Bool
  | .all cs => cs.all atomInv
  | c => atomInv c

theorem atomInv_holds {m e : Std.TreeMap.Raw String Json compare} {env' : Json} (wf : m.WF) (wfe : e.WF)
    (he : (Json.obj m).getObjValD "environment" = .obj e)
    (hs : VE.Readings.Wire.stripReadings (.obj e) = .ok env') (cond : CaseCond) (h : atomInv cond = true) :
    cond.holds (.obj m) = cond.holds ((Json.obj m).setObjVal! "environment" env') := by
  match cond, h with
  | .kind k, _ =>
    simp only [CaseCond.holds, getObjValD_set_ne wf (show "environment" ≠ "kind" by decide)]
  | .lacks k, h =>
    have hk : "environment" ≠ k := by simp [atomInv] at h; exact fun e => h e.symm
    simp only [CaseCond.holds, Json.setObjVal!]
    rw [← Json.setObjVal!, getObjVal_set_ne wf hk]
  | .path [k], h =>
    have hk : "environment" ≠ k := by simp [atomInv] at h; exact fun e => h e.symm
    simp only [CaseCond.holds, Json.setObjVal!]
    rw [← Json.setObjVal!, getObjVal_set_ne wf hk]
  | .decided d, h =>
    simp only [CaseCond.holds_decided]
    cases d
    · exact (soft_lower wf wfe he hs).symm
    · exact (rights_lower wf wfe he hs).symm
    · exact (nd_lower wf wfe he hs).symm
    · simp only [CaseDecider.fn, getObjValD_set_eq wf, he]
      rw [norms_lower wf wfe he hs, layered_lower wfe hs]
    all_goals exact absurd h (by decide)
  | .path [], h => simp [atomInv] at h
  | .path (_ :: _ :: _), h => simp [atomInv] at h
  | .has _, h => simp [atomInv] at h
  | .all _, h => simp [atomInv] at h

theorem lowerInv_holds {m e : Std.TreeMap.Raw String Json compare} {env' : Json} (wf : m.WF) (wfe : e.WF)
    (he : (Json.obj m).getObjValD "environment" = .obj e)
    (hs : VE.Readings.Wire.stripReadings (.obj e) = .ok env') (cond : CaseCond) (h : lowerInv cond = true) :
    cond.holds (.obj m) = cond.holds ((Json.obj m).setObjVal! "environment" env') := by
  cases cond with
  | all cs =>
    simp only [lowerInv, List.all_eq_true] at h
    induction cs with
    | nil => rfl
    | cons c cs ih =>
      simp only [CaseCond.holds_all_cons]
      rw [atomInv_holds wf wfe he hs c (h c List.mem_cons_self),
        ih (fun x hx => h x (List.mem_cons_of_mem _ hx))]
  | _ => exact atomInv_holds wf wfe he hs _ h

/-- The rewritten case is one the service could decode. -/
theorem caseWF_lower {m e : Std.TreeMap.Raw String Json compare} {env' : Json} (wf : m.WF) (wfe : e.WF)
    (hs : VE.Readings.Wire.stripReadings (.obj e) = .ok env') : CaseWF ((Json.obj m).setObjVal! "environment" env') := by
  obtain ⟨P, l, hP, hl, rfl⟩ := strip_spec hs
  refine ⟨fun m' h => ?_, fun m' h => ?_⟩
  · simp only [Json.setObjVal!] at h
    cases h
    exact Std.TreeMap.Raw.WF.insert wf
  · rw [getObjValD_set_eq wf] at h
    simp only [Json.setObjVal!] at h
    cases h
    exact Std.TreeMap.Raw.WF.insert wfe

end Lower

/-- A row of the lower route for the rewritten case, of a skeleton whose conditions on the case
`lowerInv` admits, is a row for the case. -/
theorem lower {m e : Std.TreeMap.Raw String Json compare} {env' : Json} (wf : m.WF) (wfe : e.WF)
    (he : (Json.obj m).getObjValD "environment" = .obj e)
    (hs : VE.Readings.Wire.stripReadings (.obj e) = .ok env') {k : Skel} {v : Json}
    (h : Fits ((Json.obj m).setObjVal! "environment" env') k v) (hc : Skel.condsOk lowerInv 1000 k = true) :
    Fits (.obj m) k v :=
  Fits.congr (p := lowerInv) (fun cond hp => (lowerInv_holds wf wfe he hs cond hp).symm) h 1000 hc

/-- The case is of none of the readings kinds: the selection reaches the lower routes' rows. -/
theorem of_lower_row {v : Json} {s : Skel} (hs : s ∈ [Skeletons.rights, Skeletons.softNorms, Skeletons.normDefaults,
      Skeletons.norms])
    (hn : ∀ k ∈ ["readings-validate", "readings-separate", "readings-elaborate", "readings-conflict",
      "readings-certificate", "readings-model", "readings-dead", "readings-choice", "readings-verdicts"], (CaseCond.kind k).holds req = false)
    (h : Fits req s v) : Fits req Skeletons.readingsRoute v := by
  skel_norm
  repeat (refine Fits.onCaseE (hn _ (by simp)) ?_)
  simp only [List.mem_cons, List.not_mem_nil, or_false] at hs
  rcases hs with rfl | rfl | rfl | rfl
  all_goals fits_from h

/-- The lower route's row, for a case of none of the readings kinds. -/
theorem runLower_fits (j : Json) (hj : CaseWF j)
    (hn : ∀ k ∈ ["readings-validate", "readings-separate", "readings-elaborate", "readings-conflict",
      "readings-certificate", "readings-model", "readings-dead", "readings-choice", "readings-verdicts"], (CaseCond.kind k).holds j = false) :
    Fits j Skeletons.readingsRoute (runLower j) := by
  unfold runLower
  split
  · exact of_lower_row (by simp) hn (Rights.runCaseReported_fits j hj)
  · rename_i ps hps
    -- The environment is an object (its profiles were read) and so is the case.
    obtain ⟨P, hP, _⟩ := VE.Order.ProfileGate.bind_ok hps
    cases hen : j.getObjValD "environment" with
    | obj e =>
      cases j with
      | obj m =>
        have wf := hj.1 m rfl
        have wfe := hj.2 e hen
        split
        · rename_i env' hs
          have hj' := caseWF_lower wf wfe hs
          simp only []
          repeat' split
          all_goals first
            | exact of_lower_row (by simp) hn (lower wf wfe hen hs (Rights.runCaseReported_fits _ hj') (by decide))
            | exact of_lower_row (by simp) hn (lower wf wfe hen hs (SoftNorms.runCaseReported_fits _ hj') (by decide))
            | exact of_lower_row (by simp) hn
                (lower wf wfe hen hs (NormDefaults.runCaseReported_fits _ hj') (by decide))
            | exact of_lower_row (by simp) hn (lower wf wfe hen hs (Norms.runCaseReported_fits _ hj') (by decide))
        · simp only []
          repeat' split
          all_goals first
            | exact of_lower_row (by simp) hn (Rights.runCaseReported_fits _ hj)
            | exact of_lower_row (by simp) hn (SoftNorms.runCaseReported_fits _ hj)
            | exact of_lower_row (by simp) hn (NormDefaults.runCaseReported_fits _ hj)
            | exact of_lower_row (by simp) hn (Norms.runCaseReported_fits _ hj)
      | _ => cases hen
    | _ =>
      rw [hen] at hP
      simp [Json.getObjVal?] at hP

/-- A case whose `kind` is `x` is read as `x`. -/
theorem caseKind_of_holds {j : Json} {x : String} (h : (CaseCond.kind x).holds j = true) :
    VE.Route.Run.caseKind j = .ok x := by
  simp only [CaseCond.holds, CaseCond.getObjValD_eq] at h
  unfold VE.Route.Run.caseKind
  cases hv : j.getObjVal? "kind" with
  | error e => rw [hv] at h; simp [Option.getD, Except.toOption, Json.getStr?] at h
  | ok v =>
    rw [hv] at h
    cases v with
    | str s =>
      have h' : (some s == some x) = true := h
      have : s = x := by simpa using h'
      subst this
      rfl
    | _ => simp [Json.getStr?, Except.toOption, Option.getD] at h

theorem runCaseReported_fits (j : Json) (hj : CaseWF j) : Fits j Skeletons.readingsRoute (runCaseReported j) := by
  unfold runCaseReported
  split
  · rename_i k hk
    split
    · rename_i hr
      split
      · exact runCase_fits j _ ‹_›
      · -- The runner's error row, for a case of a readings kind.
        have hK : j.getObjValD "kind" = .str k := by
          unfold VE.Route.Run.caseKind at hk
          split at hk
          · exact CaseCond.getObjValD_of_str ‹_› hk
          · cases hk; simp [s2Kinds] at hr
        simp only [s2Kinds, Bool.or_eq_true, beq_iff_eq, List.contains_cons, List.contains_nil,
          Bool.or_false] at hr
        simp only [or_assoc] at hr
        rcases hr with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl <;> fits
    · rename_i hr
      refine runLower_fits j hj fun x hx => ?_
      cases hb : (CaseCond.kind x).holds j
      · rfl
      · have := caseKind_of_holds hb
        rw [hk] at this
        cases this
        simp [s2Kinds] at hr hx
        rcases hx with rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl | rfl <;> simp_all
  · rename_i hk
    refine runLower_fits j hj fun x hx => ?_
    cases hb : (CaseCond.kind x).holds j
    · rfl
    · exact absurd (caseKind_of_holds hb) (hk x)

end ResponseShape.Encoders.ReadingsRoute
