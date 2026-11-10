import VE.Presupposition.Rows
import VE.Events.Decl

/-! # Change of state, continuation and iteration (presupposition PLAN PS-7)

The `pre` of each PS-7 trigger over events' state and event sorts, and each trigger's reading as an
instance of the reviewed `generic` row (`strong = pre ∧ body`, `weak = pre → body`). Every formula is
built over the hole's context: the instance term `x` and the day term `t` may be variables, and each
binder added here lifts them by `VE.Norms.Term.shift`. Readings whose subject is an agent doing an act
wait for events' ET-D2 (ps-7b). -/
namespace VE.Presupposition.Events
open VE.Events
open VE.Norms (Term.shift)
universe u

/-- Events' "`x` is in progress on `t`" (state sort `S`):
    `∃b. begins_S(x, b) ∧ ¬before(t, b) ∧ ¬∃e. ends_S(x, e) ∧ before(e, t)`. -/
def inProgress (V : EventsEnv) (S : StateSort) (x t : VE.Term) : VE.Formula :=
  .ex V.day (.and (.binary S.begins (Term.shift x) (.var 0)) (.and (.not (.binary V.before (Term.shift t) (.var 0)))
    (.not (.ex V.day (.and (.binary S.ends (Term.shift (Term.shift x)) (.var 0))
      (.binary V.before (.var 0) (Term.shift (Term.shift t))))))))

/-- "In progress before the day": `∃u. before(u, t) ∧ IP_S(x, u)`; the `pre` of "stops", "ceases",
    "continues", "remains" and "no longer". -/
def inProgressBefore (V : EventsEnv) (S : StateSort) (x t : VE.Term) : VE.Formula :=
  .ex V.day (.and (.binary V.before (.var 0) (Term.shift t)) (inProgress V S (Term.shift x) (.var 0)))

/-- "An earlier state that ended", the `pre` of "resumes": `∃y:S. ∃u. ends_S(y, u) ∧ before(u, t)`. Latest-stay limit
    (shared with "returns to", row ps-7c): it asks for some earlier state that ended, not that the latest one did. -/
def endedBefore (V : EventsEnv) (S : StateSort) (t : VE.Term) : VE.Formula :=
  .ex S.sort (.ex V.day (.and (.binary S.ends (.var 1) (.var 0))
    (.binary V.before (.var 0) (Term.shift (Term.shift t)))))

/-- "An earlier event of the same sort", the `pre` of "again": `∃y:E. ∃u. on_E(y, u) ∧ before(u, t)`. -/
def occurredBefore (V : EventsEnv) (E : EventSort) (t : VE.Term) : VE.Formula :=
  .ex E.sort (.ex V.day (.and (.binary E.on (.var 1) (.var 0))
    (.binary V.before (.var 0) (Term.shift (Term.shift t)))))

/-- "An earlier state at the place that ended", the `pre` of "returns to" (reviews/dri-decisions-20261110-ps-7.md):
    `∃y:S. ∃u. ends_S(y, u) ∧ before(u, t) ∧ at(y, p)`, `at` a base predicate (S, place) the document declares. -/
def endedAtBefore (V : EventsEnv) (S : StateSort) (atP : String) (p t : VE.Term) : VE.Formula :=
  .ex S.sort (.ex V.day (.and (.binary S.ends (.var 1) (.var 0)) (.and
    (.binary V.before (.var 0) (Term.shift (Term.shift t))) (.binary atP (.var 1) (Term.shift (Term.shift p))))))

/-- "stops" and "ceases" ("ceases" reads as "stops"). -/
def stops (V : EventsEnv) (S : StateSort) (x t : VE.Term) (body : VE.Formula) : Reading :=
  generic (inProgressBefore V S x t) body
/-- "continues" and "remains"; the translator's `body` is the "on the day" part (`IP_S(x, t)`). -/
def continues (V : EventsEnv) (S : StateSort) (x t : VE.Term) (body : VE.Formula) : Reading :=
  generic (inProgressBefore V S x t) body
/-- "no longer"; the translator's `body` is the "not on the day" part (`¬IP_S(x, t)`). -/
def noLonger (V : EventsEnv) (S : StateSort) (x t : VE.Term) (body : VE.Formula) : Reading :=
  generic (inProgressBefore V S x t) body
/-- "resumes". -/
def resumes (V : EventsEnv) (S : StateSort) (t : VE.Term) (body : VE.Formula) : Reading :=
  generic (endedBefore V S t) body
/-- "again", on an event sort. -/
def again (V : EventsEnv) (E : EventSort) (t : VE.Term) (body : VE.Formula) : Reading :=
  generic (occurredBefore V E t) body

/-- "returns to" the place `p` (reviews/dri-decisions-20261110-ps-7-returns.md item 1). Contract: "X returns to P on t"
    takes for granted an earlier stay of X at P that ended before t, and asserts a new arrival at P on t. The caller
    supplies an arrival body; an occupancy body ("X is at P on t") is not a return (guard (k) in Events/Examples.lean).
    The instances of `S` are the subject's own stays. Stays that end on t itself are a limit of the day-level model
    (guard (h)). The pre asks for some earlier stay that ended, not that the latest one did: the latest-stay limit,
    shared with "resumes", goes to row ps-7c. The reason for ENDS is that departure projects: "X did not return to P"
    of an X who never left is not true (guards (f), (l)). -/
def returnsTo (V : EventsEnv) (S : StateSort) (atP : String) (p t : VE.Term) (body : VE.Formula) : Reading :=
  generic (endedAtBefore V S atP p t) body

theorem stops_eq (V : EventsEnv) (S : StateSort) (x t : VE.Term) (body : VE.Formula) :
    stops V S x t body = generic (inProgressBefore V S x t) body := rfl
theorem continues_eq (V : EventsEnv) (S : StateSort) (x t : VE.Term) (body : VE.Formula) :
    continues V S x t body = generic (inProgressBefore V S x t) body := rfl
theorem noLonger_eq (V : EventsEnv) (S : StateSort) (x t : VE.Term) (body : VE.Formula) :
    noLonger V S x t body = generic (inProgressBefore V S x t) body := rfl
theorem resumes_eq (V : EventsEnv) (S : StateSort) (t : VE.Term) (body : VE.Formula) :
    resumes V S t body = generic (endedBefore V S t) body := rfl
theorem again_eq (V : EventsEnv) (E : EventSort) (t : VE.Term) (body : VE.Formula) :
    again V E t body = generic (occurredBefore V E t) body := rfl
theorem returnsTo_eq (V : EventsEnv) (S : StateSort) (atP : String) (p t : VE.Term) (body : VE.Formula) :
    returnsTo V S atP p t body = generic (endedAtBefore V S atP p t) body := rfl

theorem stops_defined (V : EventsEnv) (S : StateSort) (x t : VE.Term) (body : VE.Formula)
    (M : VE.Structure.{u}) (τ : VE.Valuation M) : (stops V S x t body).DefinedAt M τ :=
  generic_defined _ _ M τ
theorem continues_defined (V : EventsEnv) (S : StateSort) (x t : VE.Term) (body : VE.Formula)
    (M : VE.Structure.{u}) (τ : VE.Valuation M) : (continues V S x t body).DefinedAt M τ :=
  generic_defined _ _ M τ
theorem noLonger_defined (V : EventsEnv) (S : StateSort) (x t : VE.Term) (body : VE.Formula)
    (M : VE.Structure.{u}) (τ : VE.Valuation M) : (noLonger V S x t body).DefinedAt M τ :=
  generic_defined _ _ M τ
theorem resumes_defined (V : EventsEnv) (S : StateSort) (t : VE.Term) (body : VE.Formula)
    (M : VE.Structure.{u}) (τ : VE.Valuation M) : (resumes V S t body).DefinedAt M τ :=
  generic_defined _ _ M τ
theorem again_defined (V : EventsEnv) (E : EventSort) (t : VE.Term) (body : VE.Formula)
    (M : VE.Structure.{u}) (τ : VE.Valuation M) : (again V E t body).DefinedAt M τ :=
  generic_defined _ _ M τ
theorem returnsTo_defined (V : EventsEnv) (S : StateSort) (atP : String) (p t : VE.Term) (body : VE.Formula)
    (M : VE.Structure.{u}) (τ : VE.Valuation M) : (returnsTo V S atP p t body).DefinedAt M τ :=
  generic_defined _ _ M τ

end VE.Presupposition.Events
