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

/-- What a decided derivation shows (spec 3.4): the steps of its replayed certificate, or the point of its checked
counterexample; nothing for any other outcome or kind. -/
inductive Shown where
  | nothing
  | certificate (steps : List Step)
  | counterexample (κ : List (String × Rat))
  deriving Repr, DecidableEq

/-- The evidence carried by each outcome; a replayed certificate has a last step. -/
def Shown.matches : Outcome → Shown → Bool
  | .decided .holds, .certificate (_ :: _) => true
  | .decided .fails, .counterexample _ => true
  | .decided .undefined, .nothing => true
  | .unknown _, .nothing => true
  | _, _ => false

theorem checked_steps (P : List QFact) (links : List (String × String)) (g : QFact)
    (d : Derivation) (h : d.check P links g = true) : d.steps ≠ [] := by
  intro he
  simp [Derivation.check, he, Derivation.replay] at h

/-- A derivation's outcome from the search over its lowered facts (spec 5), with what it shows: follows only with a
certificate that replays, does not follow only with a counterexample checked by evaluation, square links included. -/
def Derive.shown (P : List QFact) (links : List (String × String)) (g : QFact) : Outcome × Shown :=
  match Derive.search P links g with
  | .follows d =>
    if d.check P links g then (.decided .holds, .certificate d.steps) else (.unknown .derivationInconclusive, .nothing)
  | .counterexample κ =>
    if counterexampleCheck P links g (Answer.point κ) then (.decided .fails, .counterexample κ)
    else (.unknown .derivationInconclusive, .nothing)
  | .unknown (.limit .derivationSteps) => (.unknown (.limit .derivationSteps), .nothing)
  | .unknown _ => (.unknown .derivationInconclusive, .nothing)

theorem Derive.shown_matches (P : List QFact) (links : List (String × String)) (g : QFact) :
    Shown.matches (Derive.shown P links g).1 (Derive.shown P links g).2 = true := by
  unfold Derive.shown
  cases hs : Derive.search P links g with
  | follows d =>
    simp only [hs]
    by_cases hc : d.check P links g = true
    · obtain ⟨st, sts, hsteps⟩ := List.exists_cons_of_ne_nil (checked_steps P links g d hc)
      simp [hc, hsteps, Shown.matches]
    · simp [hc, Shown.matches]
  | counterexample κ =>
    by_cases hc : counterexampleCheck P links g (Answer.point κ) = true <;> simp [hs, hc, Shown.matches]
  | unknown u => cases u with
    | limit l => cases l <;> simp [hs, Shown.matches]
    | _ => simp [hs, Shown.matches]

/-- A claim's outcome; a derivation's from its inlining's first fault (2.7), else, within `maxPolyTerms` nodes of
each inlined expression, from the search over the lowered premises and conclusion (spec 5), with what it shows. One
inlining table serves the whole derivation, and one search gives both. -/
def Check.runShown (ds : List Decl) : Check → Outcome × Shown
  | .claim c => (c.run ds, .nothing)
  | k@(.follows P links C) =>
    let t := inlineTable ds (k.keep ds)
    match k.fault t with
    | some .undefined => (.decided .undefined, .nothing)
    | some .exhausted => (.unknown (.limit .evaluations), .nothing)
    | some _ => (.unknown (.limit .digits), .nothing)
    | none =>
      if !k.exprs.all fun e => (e.subst t).toOption.all (·.nodesWithin maxPolyTerms |>.isSome) then
        (.unknown (.limit .derivationSteps), .nothing)
      else match P.mapM (Claim.factsIn t), C.factsIn t with
        | some fss, some [g] => Derive.shown fss.flatten links g
        | _, _ => (.unknown .derivationInconclusive, .nothing)

theorem Check.followsShown_matches (ds : List Decl) (P : List Claim)
    (links : List (String × String)) (C : Claim) :
    Shown.matches ((Check.follows P links C).runShown ds).1
      ((Check.follows P links C).runShown ds).2 = true := by
  let k := Check.follows P links C
  let t := inlineTable ds (k.keep ds)
  cases hf : k.fault t with
  | some v => cases v <;> simp [Check.runShown, k, t, hf, Shown.matches]
  | none =>
    by_cases hb : !k.exprs.all (fun e => (e.subst t).toOption.all (·.nodesWithin maxPolyTerms |>.isSome))
    · simp [Check.runShown, k, t, hf, hb, Shown.matches]
    · cases hp : P.mapM (Claim.factsIn t) with
      | none => simp [Check.runShown, k, t, hf, hb, hp, Shown.matches]
      | some fss =>
        cases hc : C.factsIn t with
        | none => simp [Check.runShown, k, t, hf, hb, hp, hc, Shown.matches]
        | some gs =>
          cases gs with
          | nil => simp [Check.runShown, k, t, hf, hb, hp, hc, Shown.matches]
          | cons g rest =>
            cases rest with
            | nil => simpa [Check.runShown, k, t, hf, hb, hp, hc] using Derive.shown_matches fss.flatten links g
            | cons h tail => simp [Check.runShown, k, t, hf, hb, hp, hc, Shown.matches]

def Check.run (ds : List Decl) (k : Check) : Outcome := (k.runShown ds).1

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
    | decided v => simpa [Check.run, Check.runShown, Check.OutcomeMeans, hr] using Claim.run_decided ds h c v hr
    | unknown u =>
      simpa [Check.run, Check.runShown, Check.OutcomeMeans, Check.UnknownCause, hr] using Claim.run_unknown ds h c u hr
  | follows P links C =>
    have own : ∀ u, u ≠ .limit .digits → u ≠ .limit .evaluations → u ∈ (Check.follows P links C).reasons →
        (Check.follows P links C).OutcomeMeans ds (.unknown u) := fun u hd he hu =>
      ⟨hu, fun h => absurd h hd, fun h => absurd h he⟩
    simp only [Check.run, Check.runShown, Check.keep]
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
          unfold Derive.shown
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
  shown : Shown
  reproduction : Option Outcome
  deriving Repr

def Run.row (c : Case) (cl : String × Check) : Row :=
  let (outcome, shown) := cl.2.runShown c.decls
  { id := cl.1, outcome, shown,
    reproduction := c.software.map fun _ => .unknown .floatingPointNotModelled }

def Run.rows (c : Case) : List Row := c.claims.map (Run.row c)

theorem Run.row_matches (c : Case) (cl : String × Check) :
    match cl.2 with
    | .claim _ => True
    | .follows .. => Shown.matches (Run.row c cl).outcome (Run.row c cl).shown = true := by
  rcases cl with ⟨id, k⟩
  cases k with
  | claim _ => trivial
  | follows P links C => simpa [Run.row] using Check.followsShown_matches c.decls P links C

theorem Run.row_outcome (c : Case) (cl : String × Check) : (Run.row c cl).outcome = cl.2.run c.decls := rfl

theorem Run.rows_outcome (c : Case) (i : Nat) (hi : i < c.claims.length) :
    ((Run.rows c)[i]'(by simpa [Run.rows] using hi)).outcome = (c.claims[i]'hi).2.run c.decls := by
  simp [Run.rows, Run.row_outcome]

/-- A row from its check's sides (3.2 (a)): a claim's outcome read from its values, evaluated once; a derivation's
row is 5's (`Run.row`). -/
def Run.rowOf (c : Case) (cl : String × Check) (vs : List Val) : Row :=
  match cl.2 with
  | .claim k =>
    { id := cl.1, outcome := Work.Claim.ofSides k vs, shown := Shown.nothing,
      reproduction := c.software.map fun _ => .unknown .floatingPointNotModelled }
  | .follows .. => Run.row c cl

/-- The case's rows within `limit` units, each with its claim's sides: the table, then each claim's expressions once,
in claim order (limit 10). -/
def Run.rowsC (limit : Nat) (c : Case) : Option (List (Row × List Val) × Nat) :=
  (c.sidesC limit).map fun (vss, w) => (List.zipWith (fun cl vs => (Run.rowOf c cl vs, vs)) c.claims vss, w)

/-- The case's claim rows within `limit` units, with each claim's sides (3.2). -/
def runC (limit : Nat) (c : Case) : Option (List (Outcome × List Val) × Nat) :=
  (Run.rowsC limit c).map fun r => (r.1.map fun (row, vs) => (row.outcome, vs), r.2)

theorem Run.rowOf_outcome (c : Case) (h : WellFormed c.decls) (cl : String × Check) :
    (Run.rowOf c cl (cl.2.sides (valuesL c.decls))).outcome = cl.2.run c.decls := by
  rcases cl with ⟨id, k⟩
  cases k with
  | claim k => exact Work.Claim.ofSides_eq c.decls h k
  | follows => rfl

theorem Run.rowsC_some (limit : Nat) (c : Case) (rs : List (Row × List Val)) (w : Nat)
    (hr : Run.rowsC limit c = some (rs, w)) :
    rs = c.claims.map (fun cl => (Run.rowOf c cl (cl.2.sides (valuesL c.decls)), cl.2.sides (valuesL c.decls))) ∧
      w ≤ limit := by
  obtain ⟨⟨vss, w'⟩, hs, h⟩ := Option.map_eq_some_iff.mp hr
  cases h
  obtain ⟨rfl, hw⟩ := Case.sidesC_some _ _ _ _ hs
  refine ⟨?_, hw⟩
  generalize c.claims = l
  induction l <;> simp_all

theorem Run.rowOf_matches (c : Case) (cl : String × Check) (vs : List Val) :
    match cl.2 with
    | .claim _ => True
    | .follows .. => Shown.matches (Run.rowOf c cl vs).outcome (Run.rowOf c cl vs).shown = true := by
  rcases cl with ⟨id, k⟩
  cases k with
  | claim _ => trivial
  | follows => exact Run.row_matches c (id, .follows ..)

theorem Run.rowOf_reproduction (c : Case) (cl : String × Check) (vs : List Val) :
    (Run.rowOf c cl vs).reproduction = c.software.map fun _ => .unknown .floatingPointNotModelled := by
  rcases cl with ⟨id, k⟩
  cases k <;> rfl

/-- Each row the charged run gives is its check's, from the sides it is paired with. -/
theorem Run.rowsC_rows (limit : Nat) (c : Case) (rs : List (Row × List Val)) (w : Nat)
    (hr : Run.rowsC limit c = some (rs, w)) : ∀ x ∈ c.claims.zip rs, x.2.1 = Run.rowOf c x.1 x.2.2 := by
  rw [(Run.rowsC_some _ _ _ _ hr).1]
  generalize c.claims = l
  induction l with
  | nil => simp
  | cons cl l ih => intro x hx; simp only [List.map_cons, List.zip_cons_cons, List.mem_cons] at hx; rcases hx with rfl | hx
                    · rfl
                    · exact ih x hx

/-- The charged run means what 2.4 and 3.4 say (3.2 (a)). -/
theorem runC_sound (limit : Nat) (c : Case) (h : WellFormed c.decls) (rows : List (Outcome × List Val)) (w : Nat)
    (hr : runC limit c = some (rows, w)) : rows.map Prod.fst = c.claims.map fun k => k.2.run c.decls := by
  obtain ⟨⟨rs, w'⟩, hs, he⟩ := Option.map_eq_some_iff.mp hr
  cases he
  obtain ⟨rfl, _⟩ := Run.rowsC_some _ _ _ _ hs
  simp only [List.map_map]
  exact List.map_congr_left fun cl _ => Run.rowOf_outcome c h cl

/-- Its refusal depends only on the case: within a limit, the same answer under any larger one. -/
theorem runC_mono (limit limit' : Nat) (c : Case) (r : List (Outcome × List Val) × Nat)
    (h : runC limit c = some r) (hl : limit ≤ limit') : runC limit' c = some r := by
  obtain ⟨r1, h1, rfl⟩ := Option.map_eq_some_iff.mp h
  obtain ⟨r2, h2, rfl⟩ := Option.map_eq_some_iff.mp h1
  simp only [runC, Run.rowsC, Case.sidesC_mono _ _ hl h2, Option.map_some]

/-- It never passes its limit. -/
theorem runC_work (limit : Nat) (c : Case) (r : List (Outcome × List Val) × Nat)
    (h : runC limit c = some r) : r.2 ≤ limit := by
  obtain ⟨⟨rs, w⟩, hs, rfl⟩ := Option.map_eq_some_iff.mp h
  exact (Run.rowsC_some _ _ _ _ hs).2

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

/-! ## What a decided derivation shows (spec 3.4): its certificate and its counterexample -/

/-- A fact `0 ≤ L`, or `0 < L` when strict, as spec 3.4 writes it: the constant, one `[name, "n/d"]` per coefficient. -/
def factJson (f : QFact) : Json :=
  Json.mkObj [("const", .str (exact f.form.const)),
    ("coeffs", .arr (f.form.coeffs.map fun (p : String × Rat) => Json.arr #[.str p.1, .str (exact p.2)]).toArray),
    ("strict", .bool f.strict)]

/-- A replayed step: a Farkas refutation's goal and its weights, one per fact in the order it combines them, or a
square step's link and bounds. -/
def stepJson : Step → Json
  | .farkas goal cert => Json.mkObj [("farkas", Json.mkObj [("goal", factJson goal),
      ("weights", .arr (cert.weights.map fun (w : Rat) => Json.str (exact w)).toArray)])]
  | .square s r a b => Json.mkObj [("square", Json.mkObj [("square", .str s), ("root", .str r),
      ("a", .str (exact a)), ("b", .str (exact b))])]

/-- The free values a check reads, in declaration order: those its inlined expressions name and those its links name
(as ME-9's point reads its sides'). -/
def reads (ds : List Decl) (k : Check) : List String :=
  let t := inlineTable ds (k.keep ds)
  let inlined : List Expr := k.exprs.filterMap fun e => (e.subst t).toOption
  let linked : List String := match k with
    | .follows _ links _ => links.flatMap fun (l : String × String) => [l.1, l.2]
    | _ => []
  let read : List String := inlined.flatMap Expr.names ++ linked
  (k.keep ds).filter (· ∈ read)

/-- A row's `certificate` and `counterexample` (spec 3.4): the replayed steps in order, or one `[name, "n/d"]` per
free value read at the checked point; `null` where the outcome shows neither. -/
def shownJson (ds : List Decl) (k : Check) : Shown → Json × Json
  | .certificate steps => (.arr (steps.map stepJson).toArray, .null)
  | .counterexample κ =>
    (.null, .arr ((reads ds k).map fun (n : String) => Json.arr #[.str n, .str (exact (Answer.point κ n))]).toArray)
  | .nothing => (.null, .null)

/-- 2.5's display of `x` at `k` places: truncated toward zero, then "…" when the truncation dropped a nonzero
remainder. -/
def truncated (k : Int) (x : Rat) : String :=
  let y := x * tenPow k
  (if x < 0 then "-" else "") ++ VE.Time.renderAmount k.toNat (y.num.natAbs / y.den * 10 ^ (-k).toNat) ++
    (if y.num.natAbs % y.den = 0 then "" else "…")

/-- A rounding claim's display, at two places beyond the printed ones (2.5), where its value is known; `vs` is the
claim's sides, evaluated once (`Check.sides`). -/
def display (vs : List Val) : Claim → Option String
  | .rounds _ _ p => match vs with
    | [.ok x] => some (truncated (p.places + 2) x)
    | _ => none
  | _ => none

/-- 2.2's tie flag (`Claim.tieSensitive`), `none` where a rule's claim has no known value. -/
def tie (vs : List Val) : Claim → Option Bool
  | .rounds .tiesUp _ p | .rounds .halfEven _ p => match vs with
    | [.ok x] => some (tieAt p.places x)
    | [.undefined] => some false
    | _ => none
  | _ => some false

/-- The members of a claim row beyond a follows row's: its sides, display and tie, read from its sides `vs`. -/
def claimFields (vs : List Val) : Check → List (String × Json)
  | .claim c => [("sides", .arr (vs.map fun | .ok q => .str (exact q) | _ => .null).toArray),
    ("display", (display vs c).elim .null Json.str), ("tie", (tie vs c).elim .null Json.bool)]
  | .follows .. => []

def rowJson (ds : List Decl) (claimId : String) (named : String → Option String)
    (vs : List Val) (k : Check) (r : Row) : Json :=
  Json.mkObj ([("status", .str "ok"), ("claim", .str r.id), ("claim_id", .str claimId), ("kind", .str (kind k)),
    ("outcome", .str (words r.outcome).1), ("reason", (words r.outcome).2.elim .null Json.str),
    ("line", (line named k).elim .null Json.str), ("finding", .null),
    ("reproduction", if r.reproduction.isSome then .str "unknown" else .null)] ++ claimFields vs k ++
    match k with
    | .claim _ => []
    | .follows .. => let (cert, cx) := shownJson ds k r.shown
      [("certificate", cert), ("counterexample", cx)])

#guard let row := rowJson [] "" (fun _ => none) [] (Check.follows [] [] (.compare ⟨.eq, false⟩ (.lit 0) (.lit 0))) { id := "c", outcome := .decided .holds, shown := .certificate [.square "s" "r" 0 1], reproduction := none }
  (row.getObjVal? "certificate").toOption.isSome &&
    (row.getObjVal? "counterexample").toOption.isSome

/-- The service answer: the case's `meaning_id` and its rows, or the refusal of the case. A standalone case is no
translated document, so no row has a finding (2.5, 13.6). -/
def runCaseReported (j : Json) : Json :=
  match Wire.decode j with
  | .ok (c, mid, ids) => match Run.rowsC Work.maxWork c with
    | some (rows, _) => Json.mkObj [("status", .str "ok"), ("meaning_id", .str mid),
      ("rows", .arr ((c.claims.zip rows).mapIdx fun i (cl, r, vs) =>
        rowJson c.decls (ids.getD i "") (wordsIn j) vs cl.2 r).toArray)]
    | none => Json.mkObj [("status", .str "error"), ("error", .str Wire.workLimit)]
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
  obtain ⟨⟨⟨mid, ids⟩, hd⟩, ⟨⟨vss, w⟩, hs⟩⟩ := Wire.decodeCase_decode j c h
  have hwf := Wire.decodeCase_wellFormed j c h
  let g := fun (cl : String × Check) => (Run.rowOf c cl (cl.2.sides (valuesL c.decls)), cl.2.sides (valuesL c.decls))
  obtain ⟨rs, w', hrc, hrs⟩ : ∃ rs w', Run.rowsC Work.maxWork c = some (rs, w') ∧ rs = c.claims.map g := by
    have hrc : Run.rowsC Work.maxWork c =
        some (List.zipWith (fun cl vs => (Run.rowOf c cl vs, vs)) c.claims vss, w) := by
      simp only [Run.rowsC, hs, Option.map_some]
    exact ⟨_, _, hrc, (Run.rowsC_some _ _ _ _ hrc).1⟩
  have hz : c.claims.zip rs = c.claims.map fun cl => (cl, g cl) := by
    rw [hrs]; generalize c.claims = l; induction l <;> simp_all
  have get : ∀ (l : List (String × Json)) (k : String) (v : Json), (l.map (·.1)).Nodup → (k, v) ∈ l →
      (Json.mkObj l).getObjVal? k = .ok v := fun l k v hn hm => by
    have hp : l.Pairwise (fun a b => ¬ compare a.1 b.1 = .eq) :=
      (List.pairwise_map.mp hn).imp (fun hne heq => hne (Std.LawfulEqOrd.eq_of_compare heq))
    simp only [Json.mkObj, Json.getObjVal?, Std.TreeMap.Raw.get?_eq_getElem?,
      Std.TreeMap.Raw.getElem?_ofList_of_mem (cmp := compare) (k_eq := Std.ReflCmp.compare_self) hp hm]
    rfl
  have hrows : (runCaseReported j).getObjVal? "rows" =
      .ok (.arr ((c.claims.map fun cl => (cl, g cl)).mapIdx fun i (x : (String × Check) × Row × List Val) =>
        rowJson c.decls (ids.getD i "") (wordsIn j) x.2.2 x.1.2 x.2.1).toArray) := by
    simp only [runCaseReported, hd, hrc, ← hz]
    exact get _ _ _ (by simp) (by simp)
  have ho := outcomes_words ((c.claims[i]'hi).2.run c.decls)
  have hout (vs : List Val) (k : Check) (r : Row) :
      (rowJson c.decls (ids.getD i "") (wordsIn j) vs k r).getObjVal? "outcome" =
        .ok (.str (words r.outcome).1) := get _ _ _ (by cases k <;> simp [claimFields, rowJson]) (by simp [rowJson])
  have hreason (vs : List Val) (k : Check) (r : Row) :
      (rowJson c.decls (ids.getD i "") (wordsIn j) vs k r).getObjVal? "reason" =
        .ok ((words r.outcome).2.elim .null Json.str) :=
    get _ _ _ (by cases k <;> simp [claimFields, rowJson]) (by simp [rowJson])
  simp only [outcomeAt, hrows, List.getElem?_toArray, List.getElem?_mapIdx, List.getElem?_map,
    List.getElem?_eq_getElem hi, Option.map_some, Option.bind_eq_bind, Option.bind_some, hout, hreason, g,
    Run.rowOf_outcome c hwf]
  generalize words ((c.claims[i]'hi).2.run c.decls) = wo at ho ⊢
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
