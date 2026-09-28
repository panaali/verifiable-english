import VE.Attribution.Content

/-! Spec 6: unit and document status. A unit's status is the meet of its meaning
status (W2's inference) and every result computed for its nested content (an
assessment node is OPEN, an act outside the slice anywhere in its kind LABELLED,
an unformalised node anywhere in its kind UNFORMALISED);
a document's is the meet of its units' statuses and every scoped check's
replayed status. One order: UNFORMALISED, OPEN and UNKNOWN below LABELLED below
CHECKED (the three lowest ranked in that order, so the meet is determined). The
only CHECKED results are a specified unit with content, a scoped check that
replayed, and the meet of results that are all CHECKED (`foldStatus_checked`). -/
namespace VE.Reports

inductive Status where
  | unformalised
  | «open»
  | unknown
  | labelled
  | checked
  deriving DecidableEq, Repr

def Status.rank : Status → Nat
  | .unformalised => 0
  | .«open» => 1
  | .unknown => 2
  | .labelled => 3
  | .checked => 4

def Status.render : Status → String
  | .unformalised => "UNFORMALISED"
  | .«open» => "OPEN"
  | .unknown => "UNKNOWN"
  | .labelled => "LABELLED"
  | .checked => "CHECKED"

def Status.meet (a b : Status) : Status := if a.rank ≤ b.rank then a else b

/-- The meet of a list of results; CHECKED for none. -/
def foldStatus (xs : List Status) : Status := xs.foldl Status.meet .checked

/-- W2's status of a unit's own meaning (`ve/document.py`): CHECKED for a
specified meaning with content, OPEN, UNFORMALISED, and LABELLED otherwise
(including a unit without a meaning on the Lean wire). -/
def meaningStatus (hasContent : Bool) : Option Meaning → Status
  | some .specified => if hasContent then .checked else .labelled
  | some (.«open» _) => .«open»
  | some (.unformalised _) => .unformalised
  | _ => .labelled

/-- A scoped check's replayed verdict (5.1): decided with evidence, or UNKNOWN. -/
def verdictStatus : String → Status
  | "FOLLOWS" | "DOES NOT FOLLOW" | "PAYLOADS INCONSISTENT" => .checked
  | _ => .unknown

def unitStatus (own : Status) (nested : List Status) : Status := foldStatus (own :: nested)

def documentStatus (units verdicts : List Status) : Status := foldStatus (units ++ verdicts)

theorem meet_rank_left (a b : Status) : (a.meet b).rank ≤ a.rank := by
  unfold Status.meet; split <;> omega

theorem meet_rank_right (a b : Status) : (a.meet b).rank ≤ b.rank := by
  unfold Status.meet; split <;> omega

theorem foldl_meet_rank_init (acc : Status) (xs : List Status) :
    (xs.foldl Status.meet acc).rank ≤ acc.rank := by
  induction xs generalizing acc with
  | nil => exact Nat.le_refl _
  | cons x xs ih => exact Nat.le_trans (ih _) (meet_rank_left acc x)

theorem foldl_meet_rank_le (acc : Status) (xs : List Status) :
    ∀ x ∈ xs, (xs.foldl Status.meet acc).rank ≤ x.rank := by
  induction xs generalizing acc with
  | nil => intro x hx; cases hx
  | cons y ys ih =>
    intro x hx
    rcases List.mem_cons.mp hx with rfl | hx
    · exact Nat.le_trans (foldl_meet_rank_init _ ys) (meet_rank_right acc x)
    · exact ih _ x hx

/-- The fold is at most every folded result. -/
theorem foldStatus_le (xs : List Status) : ∀ x ∈ xs, (foldStatus xs).rank ≤ x.rank :=
  foldl_meet_rank_le _ xs

theorem rank_checked {s : Status} (h : 4 ≤ s.rank) : s = .checked := by
  cases s <;> simp_all [Status.rank]

/-- The fold is CHECKED only when every folded result is. -/
theorem foldStatus_checked {xs : List Status} (h : foldStatus xs = .checked) : ∀ x ∈ xs, x = .checked := by
  intro x hx
  have hle := foldStatus_le xs x hx
  rw [h] at hle
  exact rank_checked hle

theorem unitStatus_le (own : Status) (nested : List Status) :
    (unitStatus own nested).rank ≤ own.rank ∧ ∀ x ∈ nested, (unitStatus own nested).rank ≤ x.rank :=
  ⟨foldStatus_le _ _ (List.mem_cons_self ..), fun _ hx => foldStatus_le _ _ (List.mem_cons_of_mem _ hx)⟩

/-- A document's status is at most every unit's status, every result nested in
a unit and every scoped check's replayed status. -/
theorem documentStatus_le (units : List (Status × List Status)) (verdicts : List Status) :
    let d := documentStatus (units.map fun u => unitStatus u.1 u.2) verdicts
    (∀ u ∈ units, ∀ x ∈ u.2, d.rank ≤ x.rank) ∧ ∀ x ∈ verdicts, d.rank ≤ x.rank := by
  intro d
  refine ⟨fun u hu x hx => ?_, fun x hx => foldStatus_le _ _ (List.mem_append_right _ hx)⟩
  have hunit : d.rank ≤ (unitStatus u.1 u.2).rank :=
    foldStatus_le _ _ (List.mem_append_left _ (List.mem_map_of_mem hu))
  exact Nat.le_trans hunit ((unitStatus_le u.1 u.2).2 x hx)

end VE.Reports
