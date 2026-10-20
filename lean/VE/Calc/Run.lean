import VE.Calc.Wire

/-! The `calc` mode's runner (math-evidence spec 3.4, ME-2): what each outcome of a check states, one row per
`claims` entry in order, and the row theorem on the wire (`Run.row_sound`). This batch has the `claim` kind only;
ME-5, ME-8 and ME-9 add their kinds, their clauses and their cases of `Check.run_sound`. -/

namespace VE.Calc
open Lean VE.Numbers

/-- The named cause of an unknown row (J2): a claim is unknown only at the digit limit with a value on the way
beyond it, or at the budget with a read of an exhausted counted value (`Claim.run_unknown`'s disjunction). -/
def Check.UnknownCause (ds : List Decl) : Check → UnknownReason → Prop
  | .claim c, u => (u = .limit .digits ∧ c.Overflows ds) ∨ (u = .limit .evaluations ∧ c.ReadsExhausted ds)

/-- What each outcome states, one clause per kind and outcome; the clauses are tried in order. -/
def Check.OutcomeMeans (ds : List Decl) : Check → Outcome → Prop
  | .claim c, .decided v => v = c.decide (values ds)
  | k, .unknown u => k.UnknownCause ds u

def Check.run (ds : List Decl) : Check → Outcome
  | .claim c => c.run ds

/-- A decided row's meaning is decidable, so route cases can check it. -/
instance (ds : List Decl) (k : Check) (v : Verdict) : Decidable (k.OutcomeMeans ds (.decided v)) := by
  cases k
  unfold Check.OutcomeMeans
  infer_instance

theorem Check.run_claim (ds : List Decl) (c : Claim) : (Check.claim c).run ds = c.run ds := rfl

/-- The row theorem (J3): every outcome means what its kind's clause says. -/
theorem Check.run_sound (ds : List Decl) (h : WellFormed ds) (k : Check) : k.OutcomeMeans ds (k.run ds) := by
  cases k with
  | claim c =>
    cases hr : c.run ds with
    | decided v => simpa [Check.run, Check.OutcomeMeans, hr] using Claim.run_decided ds h c v hr
    | unknown u => simpa [Check.run, Check.OutcomeMeans, Check.UnknownCause, hr] using Claim.run_unknown ds h c u hr

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

def rowJson (claimId : String) (r : Row) : Json :=
  Json.mkObj [("status", .str "ok"), ("claim", .str r.id), ("claim_id", .str claimId), ("kind", .str "claim"),
    ("outcome", .str (words r.outcome).1), ("reason", (words r.outcome).2.elim .null Json.str),
    ("reproduction", if r.reproduction.isSome then .str "unknown" else .null)]

/-- The service answer: the case's `meaning_id` and its rows, or the refusal of the case. -/
def runCaseReported (j : Json) : Json :=
  match Wire.decode j with
  | .ok (c, mid, ids) => Json.mkObj [("status", .str "ok"), ("meaning_id", .str mid),
    ("rows", .arr ((Run.rows c).mapIdx fun i r => rowJson (ids.getD i "") r).toArray)]
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
    have hr : i < (Run.rows d.1).length := by simpa [Run.rows] using hi
    have hrows : (runCaseReported j).getObjVal? "rows" =
        .ok (.arr ((Run.rows d.1).mapIdx fun i r => rowJson (d.2.2.getD i "") r).toArray) := by
      simp only [runCaseReported, hd]
      exact get _ _ _ (by simp) (by simp)
    have ho := outcomes_words ((d.1.claims[i]'hi).2.run d.1.decls)
    rw [← Run.rows_outcome d.1 i hi] at ho ⊢
    have hout (r : Row) : (rowJson (d.2.2.getD i "") r).getObjVal? "outcome" =
        .ok (.str (words r.outcome).1) := get _ _ _ (by simp) (by simp)
    have hreason (r : Row) : (rowJson (d.2.2.getD i "") r).getObjVal? "reason" =
        .ok ((words r.outcome).2.elim .null Json.str) := get _ _ _ (by simp) (by simp)
    simp only [outcomeAt, hrows, List.getElem?_toArray, List.getElem?_mapIdx, List.getElem?_eq_getElem hr,
      Option.map_some, Option.bind_eq_bind, Option.bind_some, hout, hreason]
    generalize words ((Run.rows d.1)[i]'hr).outcome = wo at ho ⊢
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
  exact this

/-- Unknown arises only from its named cause (J2). -/
theorem unknown_named (j : Lean.Json) (c : Case) (h : Wire.decodeCase j = .ok c) (i : Nat)
    (hi : i < c.claims.length) (u : UnknownReason)
    (hu : Run.outcomeAt (Run.runCaseReported j) i = some (.unknown u)) :
    (c.claims[i]'hi).2.UnknownCause c.decls u := by
  have := row_sound j c h i hi _ hu
  cases hk : (c.claims[i]'hi).2 with
  | claim cl => rw [hk] at this; exact this

end Run

end VE.Calc
