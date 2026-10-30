import VE.Acts.Readings
import VE.Acts.Table
import VE.Acts.Lexical

/-! The act check under `acts@0` from AP-3 on (docs/spec/act-phrases.md 6.4; D-15 to D-18 in 10).

A lexical act is `Lexical.check`'s, unchanged, and never enters the grammar (`checkAct_lexical`). An act that
`Lexical.check` refuses only for its join words or commas (1.3 condition 6, D-4 and D-5: every earlier condition and
the lexing passed) is a joined act: every slot must stand alone as a word, and it must have exactly one meaning,
from one complete listing (`readings V rawCap stepBudget`, at most `maxReadings` meanings). The listing is computed
once; `read`, which `checkAct_joined` names, is that listing's one-element case.

No route calls `checkAct` yet: the norms decoder's hook switches to it with the entry points that elaborate (ap-3db).
-/

namespace VE.Acts.Wire
open Lean VE.Acts.Lexical

/-- `Lexical.check`'s refusal for condition 6 (D-4, D-5), which it raises only after conditions 1 to 5 and the lexing
    passed. -/
def joinRefusal (name e : String) : Bool :=
  e == s!"InvalidInput: act phrase for {name} has a comma outside a fixed phrase" ||
    (e.startsWith s!"InvalidInput: act phrase for {name} joins acts with '" && e.endsWith "' outside a fixed phrase")

/-- A joined act's one meaning from its canonical act `act` (6.4): the slots standing alone (D-18), then one
    complete listing: one meaning, none (D-16), two or more (D-15, every meaning's text), or the limit (D-17). -/
def joinedAct (fx : List String) (V : Vocab) (name act : String) : Except String Act := do
  let ts ← lex fx act
  if ts.any (fun t => match t with | .word w => w.contains '{' | _ => false) then
    throw s!"InvalidInput: act phrase for {name} has a slot joined to a word"
  match readings V rawCap stepBudget ts.toArray with
  | .ok [A] => pure A
  | .ok [] => throw s!"InvalidInput: act phrase for {name} has no reading under the declared frames"
  | .ok As => do
    let ms ← meaningTexts fx s!"the act phrase for {name}" As
    throw (s!"InvalidInput: act phrase for {name} has more than one reading: " ++ numbered ms)
  | .limit => throw s!"ResourceLimit: act phrase for {name} has too many readings to list; split the sentence"

/-- The act check under `acts@0` from AP-3 on: a lexical act (`Lexical.check`), or a joined act: every condition of
    1.3 except 6, every slot standing alone as a word, and exactly one meaning (`read V rawCap stepBudget`). Returns
    the canonical act and, for a joined act, its act tree. With two or more meanings it raises D-15, which lists every
    meaning of `readings V rawCap stepBudget` through `meaningTexts` (6.2). -/
def checkAct (fx : List String) (V : Vocab) (name : String) (arity : Nat) (raw : Json) :
    Except String (String × Option Act) :=
  match check fx name arity raw with
  | .ok a => .ok (a, none)
  | .error e =>
    if joinRefusal name e then
      let act := normal ((raw.getStr?).toOption.getD "")
      (joinedAct fx V name act).map fun A => (act, some A)
    else .error e

/-! ### Theorems (6.4) -/

/-- An act AP-1 accepts never enters the grammar (plan 2.5). -/
theorem checkAct_lexical (fx V name k raw a) (h : Lexical.check fx name k raw = .ok a) :
    VE.Acts.Wire.checkAct fx V name k raw = .ok (a, none) := by
  unfold checkAct; rw [h]

theorem joinedAct_read {fx V name act A} (h : joinedAct fx V name act = .ok A) :
    ∃ ts, Lexical.lex fx act = .ok ts ∧ read V rawCap stepBudget ts.toArray = .ok A := by
  unfold joinedAct at h
  cases hl : lex fx act with
  | error e => simp [hl, bind, Except.bind] at h
  | ok ts =>
    simp only [hl, bind, Except.bind] at h
    refine ⟨ts, rfl, ?_⟩
    split at h
    · cases h
    · unfold read readIn
      rw [← readings]
      cases hr : readings V rawCap stepBudget ts.toArray with
      | limit => rw [hr] at h; cases h
      | ok As =>
        rw [hr] at h
        rcases As with _ | ⟨A', _ | ⟨B, rest⟩⟩
        · cases h
        · cases h; rfl
        · dsimp only at h
          cases hm : meaningTexts fx s!"the act phrase for {name}" (A' :: B :: rest) <;> rw [hm] at h <;> cases h

theorem checkAct_joined (fx V name k raw a A) (h : VE.Acts.Wire.checkAct fx V name k raw = .ok (a, some A)) :
    ∃ ts, Lexical.lex fx a = .ok ts ∧ read V rawCap stepBudget ts.toArray = .ok A := by
  unfold checkAct at h
  split at h
  · cases h
  · split at h
    · dsimp only at h
      cases hj : joinedAct fx V name (normal ((raw.getStr?).toOption.getD "")) with
      | error e => rw [hj] at h; cases h
      | ok A' =>
        rw [hj] at h
        simp only [Except.map, Except.ok.injEq, Prod.mk.injEq, Option.some.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        exact joinedAct_read hj
    · cases h

end VE.Acts.Wire
