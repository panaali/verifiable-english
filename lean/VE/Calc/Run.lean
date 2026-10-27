import VE.Calc.Wire
import VE.Calc.Render

/-! The `calc` mode's runner (math-evidence spec 3.4, ME-2): what each outcome of a check states, one row per
`claims` entry in order, and the row theorem on the wire (`Run.row_sound`). It has the `claim` and `follows` (ME-5)
kinds; ME-8 and ME-9 add their kinds, their clauses and their cases of `Check.run_sound`. -/

namespace VE.Calc
open Lean VE.Numbers

/-- The names a check's meaning quantifies over: the free values. -/
def Check.keep (ds : List Decl) : Check → List String
  | _ => freeNames ds

/-- The reasons for unknown that each kind may give (1.5). -/
def Check.reasons : Check → List UnknownReason
  | .claim _ => [.limit .digits, .limit .evaluations]
  | .follows .. => [.limit .derivationSteps, .derivationInconclusive, .limit .digits, .limit .evaluations]

/-- The named cause of an unknown row (J2). A claim is unknown only at the digit limit with a value on the way beyond
it, or at the budget with a read of an exhausted counted value: `Claim.run_unknown`'s disjunction. The other kinds
may also give their own reasons (1.5); at those two limits their causes are the same, in one of their expressions,
since they meet the digit limit only in the lowering (2.7, `Expr.inline_tooLarge`). -/
def Check.UnknownCause (ds : List Decl) : Check → UnknownReason → Prop
  | .claim c, u => (u = .limit .digits ∧ c.Overflows ds) ∨ (u = .limit .evaluations ∧ c.ReadsExhausted ds)
  | k, u => u ∈ k.reasons ∧ (u = .limit .digits → ∃ e ∈ k.exprs, e.Overflows ds) ∧
      (u = .limit .evaluations → ∃ e ∈ k.exprs, e.ReadsExhausted ds)

/-- What each outcome states, one clause per kind and outcome; the clauses are tried in order. -/
def Check.OutcomeMeans (ds : List Decl) : Check → Outcome → Prop
  | .claim c, .decided v => v = c.decide (values ds)
  | .follows P links C, .decided .holds => Follows ds P links C
  | .follows P links C, .decided .fails => HasCounterexample ds P links C
  | k, .decided .undefined => ∃ e ∈ k.exprs, ∀ κ x, ¬ Denotes (values (assign ds (k.keep ds) κ)) e x
  | k, .unknown u => k.UnknownCause ds u

/-- The first fault inlining by the table `t` meets in a check's expressions, in order (2.7). -/
def Check.fault (t : Inlined) (k : Check) : Option Val :=
  k.exprs.findSome? fun e => match e.subst t with
    | .error v => some v
    | .ok _ => none

/-- `Claim.facts` with the inlining table `t` (`Claim.factsIn_eq`), built once for a whole derivation. -/
def Claim.factsIn (t : Inlined) (c : Claim) : Option (List QFact) := (c.subst t).toOption.bind Claim.lower

theorem Claim.factsIn_eq (ds : List Decl) : Claim.factsIn (inlineTable ds (freeNames ds)) = Claim.facts ds := by
  funext c
  unfold Claim.factsIn Claim.facts Claim.inline
  split <;> simp_all [Except.toOption]

/-- A derivation's outcome from the search over its lowered facts (spec 5): follows only with a certificate that
replays, does not follow only with a counterexample checked by evaluation, square links included. -/
def Derive.outcome (P : List QFact) (links : List (String × String)) (g : QFact) : Outcome :=
  match Derive.search P links g with
  | .follows d => if d.check P links g then .decided .holds else .unknown .derivationInconclusive
  | .counterexample κ =>
    if counterexampleCheck P links g (Answer.point κ) then .decided .fails else .unknown .derivationInconclusive
  | .unknown (.limit .derivationSteps) => .unknown (.limit .derivationSteps)
  | .unknown _ => .unknown .derivationInconclusive

/-- A claim's outcome; a derivation's from its inlining's first fault (2.7), else, within `maxPolyTerms` nodes of
each inlined expression, from the search over the lowered premises and conclusion (spec 5). One inlining table
serves the whole derivation. -/
def Check.run (ds : List Decl) : Check → Outcome
  | .claim c => c.run ds
  | k@(.follows P links C) =>
    let t := inlineTable ds (k.keep ds)
    match k.fault t with
    | some .undefined => .decided .undefined
    | some .exhausted => .unknown (.limit .evaluations)
    | some _ => .unknown (.limit .digits)
    | none =>
      if !k.exprs.all fun e => (e.subst t).toOption.all (·.nodesWithin maxPolyTerms |>.isSome) then
        .unknown (.limit .derivationSteps)
      else match P.mapM (Claim.factsIn t), C.factsIn t with
        | some fss, some [g] => Derive.outcome fss.flatten links g
        | _, _ => .unknown .derivationInconclusive

theorem Check.outcomeMeans_claim (ds : List Decl) (c : Claim) (v : Verdict) :
    (Check.claim c).OutcomeMeans ds (.decided v) ↔ v = c.decide (values ds) := by
  cases v <;> rfl

/-- A claim's decided row is decidable, so route cases can check it. -/
instance (ds : List Decl) (c : Claim) (v : Verdict) : Decidable ((Check.claim c).OutcomeMeans ds (.decided v)) :=
  decidable_of_iff _ (Check.outcomeMeans_claim ds c v).symm

theorem Check.fault_some {ds : List Decl} {k : Check} {v : Val}
    (h : k.fault (inlineTable ds (k.keep ds)) = some v) : ∃ e ∈ k.exprs, e.inline ds (k.keep ds) = .error v := by
  obtain ⟨e, he, hv⟩ := List.exists_of_findSome?_eq_some h
  refine ⟨e, he, ?_⟩
  split at hv <;> simp_all [Expr.inline]

theorem Check.run_claim (ds : List Decl) (c : Claim) : (Check.claim c).run ds = c.run ds := rfl

/-- The row theorem (J3): every outcome means what its kind's clause says. -/
theorem Check.run_sound (ds : List Decl) (h : WellFormed ds) (k : Check) : k.OutcomeMeans ds (k.run ds) := by
  cases k with
  | claim c =>
    cases hr : c.run ds with
    | decided v => simpa [Check.run, Check.OutcomeMeans, hr] using Claim.run_decided ds h c v hr
    | unknown u => simpa [Check.run, Check.OutcomeMeans, Check.UnknownCause, hr] using Claim.run_unknown ds h c u hr
  | follows P links C =>
    have own : ∀ u, u ≠ .limit .digits → u ≠ .limit .evaluations → u ∈ (Check.follows P links C).reasons →
        (Check.follows P links C).OutcomeMeans ds (.unknown u) := fun u hd he hu =>
      ⟨hu, fun h => absurd h hd, fun h => absurd h he⟩
    simp only [Check.run, Check.keep]
    cases hf : (Check.follows P links C).fault (inlineTable ds (freeNames ds)) with
    | some v =>
      obtain ⟨e, he, hv⟩ := Check.fault_some hf
      rcases Expr.inline_error ds _ e v hv with rfl | rfl
      · exact ⟨e, he, Expr.inline_undefined ds h _ e hv⟩
      · show (Check.follows P links C).UnknownCause ds (.limit .evaluations)
        exact ⟨by simp [Check.reasons], fun h => absurd h (by decide), fun _ => ⟨e, he, Expr.inline_exhausted ds _ e hv⟩⟩
    | none =>
      simp only
      split
      · exact own _ (by decide) (by decide) (by simp [Check.reasons])
      · split
        · rename_i fss g hP hC
          rw [Claim.factsIn_eq] at hP hC
          unfold Derive.outcome
          split
          · rename_i d _
            split
            · exact follows_of_check ds h P links C fss g d hP hC (by assumption)
            · exact own _ (by decide) (by decide) (by simp [Check.reasons])
          · rename_i κ _
            split
            · exact counterexample_of_check ds h P links C fss g _ hP hC (by assumption)
            · exact own _ (by decide) (by decide) (by simp [Check.reasons])
          · exact own _ (by decide) (by decide) (by simp [Check.reasons])
          · exact own _ (by decide) (by decide) (by simp [Check.reasons])
        · exact own _ (by decide) (by decide) (by simp [Check.reasons])

structure Row where
  id : String
  outcome : Outcome
  reproduction : Option Outcome
  deriving Repr

def Run.row (c : Case) (cl : String × Check) : Row :=
  { id := cl.1, outcome := cl.2.run c.decls,
    reproduction := c.software.map fun _ => .unknown .floatingPointNotModelled }

def Run.rows (c : Case) : List Row := c.claims.map (Run.row c)

theorem Run.row_outcome (c : Case) (cl : String × Check) : (Run.row c cl).outcome = cl.2.run c.decls := rfl

theorem Run.rows_outcome (c : Case) (i : Nat) (hi : i < c.claims.length) :
    ((Run.rows c)[i]'(by simpa [Run.rows] using hi)).outcome = (c.claims[i]'hi).2.run c.decls := by
  simp [Run.rows, Run.row_outcome]

namespace Run

/-- An outcome's `outcome` and `reason` on the wire (1.5). -/
def words : Outcome → String × Option String
  | .decided .holds => ("holds", none)
  | .decided .fails => ("fails", none)
  | .decided .undefined => ("undefined", none)
  | .unknown u => ("unknown", some (u.text VE.Limits.maxEvaluations))

/-- Every outcome, so that a row's words read back as the one outcome they state (`outcomeAt`). -/
def outcomes : List Outcome :=
  [.decided .holds, .decided .fails, .decided .undefined] ++
    [.limit .digits, .limit .evaluations, .limit .derivationSteps, .limit .witnessPoints, .limit .polyTerms,
      .floatingPointNotModelled, .derivationInconclusive, .consistencyInconclusive, .identityNotShown,
      .unboundedStatement].map .unknown

theorem outcomes_words (o : Outcome) : outcomes.find? (words · == words o) = some o := by
  rcases o with v | u
  · cases v <;> decide
  · rcases u with l | _ | _ | _ | _ | _
    · cases l <;> decide
    all_goals decide

/-- A check's kind on the wire: the form of the request's check. -/
def kind : Check → String
  | .claim _ => "claim"
  | .follows .. => "follows"

/-! ## Row fields (spec 3.4): Lean's line, and a claim's sides, display and tie -/

/-- Each value's words in the request (3.1), by name: the decoder has read each as a string. -/
def wordsIn (j : Json) : String → Option String :=
  let ws : List (String × String) := match j.getObjVal? "values" with
    | .ok (.arr vs) => vs.toList.filterMap fun v => match v.getObjVal? "name", v.getObjVal? "words" with
      | .ok (.str n), .ok (.str w) => some (n, w)
      | _, _ => none
    | _ => []
  fun n => ws.lookup n

/-- A check's English line (11.1, 9), `none` where an expression is beyond 11.2's nesting rule or a value's words
are not 11.2's form. -/
def line (words : String → Option String) : Check → Option String
  | .claim c => English.renderClaim words c
  | .follows P links C => English.renderFollows words P links C

/-- An exact value as a reduced fraction "n/d", or "n" for an integer (3.4). -/
def exact (q : Rat) : String := if q.den = 1 then toString q.num else s!"{q.num}/{q.den}"

/-- 2.5's display of `x` at `k` places: truncated toward zero, then "…" when the truncation dropped a nonzero
remainder. -/
def truncated (k : Int) (x : Rat) : String :=
  let y := x * tenPow k
  (if x < 0 then "-" else "") ++ VE.Time.renderAmount k.toNat (y.num.natAbs / y.den * 10 ^ (-k).toNat) ++
    (if y.num.natAbs % y.den = 0 then "" else "…")

/-- A claim's sides: each expression's value under the case's bounded values (`Claim.run` reads the same). -/
def sides (σ : String → Val) (c : Claim) : List Val := c.exprs.map (Expr.evalL σ)

/-- A rounding claim's display, at two places beyond the printed ones (2.5), where its value is known. -/
def display (σ : String → Val) : Claim → Option String
  | .rounds _ e p => match e.evalL σ with
    | .ok x => some (truncated (p.places + 2) x)
    | _ => none
  | _ => none

/-- 2.2's tie flag (`Claim.tieSensitive`), `none` where a rule's claim has no known value. -/
def tie (σ : String → Val) : Claim → Option Bool
  | .rounds .tiesUp e p | .rounds .halfEven e p => match e.evalL σ with
    | .ok x => some (tieAt p.places x)
    | .undefined => some false
    | _ => none
  | _ => some false

/-- The members of a claim row beyond a follows row's: its sides, display and tie. -/
def claimFields (σ : String → Val) : Check → List (String × Json)
  | .claim c => [("sides", .arr (sides σ c |>.map fun | .ok q => .str (exact q) | _ => .null).toArray),
    ("display", (display σ c).elim .null Json.str), ("tie", (tie σ c).elim .null Json.bool)]
  | .follows .. => []

def rowJson (claimId : String) (named : String → Option String) (σ : String → Val) (k : Check) (r : Row) : Json :=
  Json.mkObj ([("status", .str "ok"), ("claim", .str r.id), ("claim_id", .str claimId), ("kind", .str (kind k)),
    ("outcome", .str (words r.outcome).1), ("reason", (words r.outcome).2.elim .null Json.str),
    ("line", (line named k).elim .null Json.str), ("finding", .null),
    ("reproduction", if r.reproduction.isSome then .str "unknown" else .null)] ++ claimFields σ k)

/-- The service answer: the case's `meaning_id` and its rows, or the refusal of the case. A standalone case is no
translated document, so no row has a finding (2.5, 13.6). -/
def runCaseReported (j : Json) : Json :=
  match Wire.decode j with
  | .ok (c, mid, ids) =>
    let σ := valuesL c.decls
    Json.mkObj [("status", .str "ok"), ("meaning_id", .str mid),
      ("rows", .arr (c.claims.mapIdx fun i cl => rowJson (ids.getD i "") (wordsIn j) σ cl.2 (Run.row c cl)).toArray)]
  | .error e => Json.mkObj [("status", .str "error"), ("error", .str e)]

/-- The outcome row `i` of an answer states. -/
def outcomeAt (answer : Json) (i : Nat) : Option Outcome := do
  let .ok (.arr rows) := answer.getObjVal? "rows" | none
  let row ← rows[i]?
  let .ok (.str w) := row.getObjVal? "outcome" | none
  let reason := match row.getObjVal? "reason" with
    | .ok (.str s) => some s
    | _ => none
  outcomes.find? (words · == (w, reason))

theorem outcome_sound (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) (i : Nat)
    (hi : i < c.claims.length) :
    Run.outcomeAt (Run.runCaseReported j) i = some ((c.claims[i]'hi).2.run c.decls) := by
  unfold Wire.decodeCase at h
  cases hd : Wire.decode j with
  | error e => rw [hd] at h; cases h
  | ok d =>
    rw [hd] at h
    cases h
    have get : ∀ (l : List (String × Json)) (k : String) (v : Json), (l.map (·.1)).Nodup → (k, v) ∈ l →
        (Json.mkObj l).getObjVal? k = .ok v := fun l k v hn hm => by
      have hp : l.Pairwise (fun a b => ¬ compare a.1 b.1 = .eq) :=
        (List.pairwise_map.mp hn).imp (fun hne heq => hne (Std.LawfulEqOrd.eq_of_compare heq))
      simp only [Json.mkObj, Json.getObjVal?, Std.TreeMap.Raw.get?_eq_getElem?,
        Std.TreeMap.Raw.getElem?_ofList_of_mem (cmp := compare) (k_eq := Std.ReflCmp.compare_self) hp hm]
      rfl
    have hrows : (runCaseReported j).getObjVal? "rows" =
        .ok (.arr (d.1.claims.mapIdx fun i cl =>
          rowJson (d.2.2.getD i "") (wordsIn j) (valuesL d.1.decls) cl.2 (Run.row d.1 cl)).toArray) := by
      simp only [runCaseReported, hd]
      exact get _ _ _ (by simp) (by simp)
    have ho := outcomes_words ((d.1.claims[i]'hi).2.run d.1.decls)
    have hout (k : Check) (r : Row) :
        (rowJson (d.2.2.getD i "") (wordsIn j) (valuesL d.1.decls) k r).getObjVal? "outcome" =
          .ok (.str (words r.outcome).1) := get _ _ _ (by cases k <;> simp [claimFields]) (by simp)
    have hreason (k : Check) (r : Row) :
        (rowJson (d.2.2.getD i "") (wordsIn j) (valuesL d.1.decls) k r).getObjVal? "reason" =
          .ok ((words r.outcome).2.elim .null Json.str) := get _ _ _ (by cases k <;> simp [claimFields]) (by simp)
    simp only [outcomeAt, hrows, List.getElem?_toArray, List.getElem?_mapIdx, List.getElem?_eq_getElem hi,
      Option.map_some, Option.bind_eq_bind, Option.bind_some, hout, hreason, Run.row_outcome]
    generalize words ((d.1.claims[i]'hi).2.run d.1.decls) = wo at ho ⊢
    rcases wo with ⟨w, _ | s⟩ <;> exact ho

/-- The row theorem on the wire, for every kind. -/
theorem row_sound (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) (i : Nat)
    (hi : i < c.claims.length) (o : Outcome) (ho : Run.outcomeAt (Run.runCaseReported j) i = some o) :
    (c.claims[i]'hi).2.OutcomeMeans c.decls o := by
  rw [outcome_sound j c h i hi] at ho
  cases ho
  exact Check.run_sound c.decls (Wire.decodeCase_wellFormed j c h) _

/-- Debate A1, for claims: agreement with the total decision is conditional on completion. -/
theorem verdict_sound (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) (i : Nat)
    (hi : i < c.claims.length) (cl : Claim) (hk : (c.claims[i]'hi).2 = .claim cl) (v : Verdict)
    (hv : Run.outcomeAt (Run.runCaseReported j) i = some (.decided v)) :
    v = cl.decide (values c.decls) := by
  have := row_sound j c h i hi _ hv
  rw [hk] at this
  exact (Check.outcomeMeans_claim _ _ _).mp this

/-- Unknown arises only from its named cause (J2). -/
theorem unknown_named (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) (i : Nat)
    (hi : i < c.claims.length) (u : UnknownReason)
    (hu : Run.outcomeAt (Run.runCaseReported j) i = some (.unknown u)) :
    (c.claims[i]'hi).2.UnknownCause c.decls u := by
  have := row_sound j c h i hi _ hu
  cases hk : (c.claims[i]'hi).2 <;> rw [hk] at this <;> exact this

end Run

end VE.Calc
