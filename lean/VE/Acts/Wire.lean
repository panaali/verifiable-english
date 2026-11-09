import VE.Acts.Readings
import VE.Acts.Table
import VE.Acts.Lexical

/-! The act check under `acts@0` from AP-3 on (docs/spec/act-phrases.md 6.4; D-15 to D-18 in 10).

A lexical act is `Lexical.check`'s, unchanged, and never enters the grammar (`checkAct_lexical`). An act that
`Lexical.check` refuses only for its join words or commas (1.3 condition 6, D-4 and D-5: every earlier condition and
the lexing passed) is a joined act: every slot must stand alone as a word, and it must have exactly one meaning,
from one complete listing (`readings V rawCap stepBudget`, at most `maxReadings` meanings). The listing is computed
once; `read`, which `checkAct_joined` names, is that listing's one-element case.

The norms decoder's hook calls `checkAct` (ap-3db). `decodeVocab` reads the `acts` block's `frames` and `adverbs`
(3.1), and `checkVocab` raises D-31.
-/

namespace VE.Acts.Wire
open Lean VE.Acts.Lexical
open VE.Bridge (exactFields stringField strings)

/-- One frame of the `acts` block (1.4, 3.1); `head` is its words as one string. -/
def decodeFrame (j : Json) : Except String Frame := do
  exactFields j ["head", "markers", "split", "modifiers"]
  pure ⟨wordsOf (← stringField j "head"), ← strings (j.getObjValD "markers"), ← strings (j.getObjValD "split"),
    ← strings (j.getObjValD "modifiers")⟩

/-- The `acts` block's `frames` and `adverbs` (3.1): an absent field is empty, and `checkVocab` raises D-31. -/
def decodeVocab (block : Json) : Except String Vocab := do
  let frames ← match block.getObjVal? "frames" with
    | .ok fs => (← fs.getArr?).toList.mapM decodeFrame
    | .error _ => pure []
  let adverbs ← match block.getObjVal? "adverbs" with
    | .ok xs => strings xs
    | .error _ => pure []
  let V : Vocab := ⟨frames, adverbs⟩
  checkVocab V
  pure V

/-- The `acts` block's `fixed` list, `[]` when absent or not a list of strings (6.4). -/
def fixedOf (environment : Json) : List String :=
  (strings (((environment.getObjValD "vocabulary").getObjValD "acts").getObjValD "fixed")).toOption.getD []

/-- A joined act's one meaning from its tokens `ts` (6.4): the slots standing alone (D-18), then one complete
    listing: one meaning, none (D-16), two or more (D-15, every meaning's text), or the limit (D-17). -/
def joinedActBy (R : Array RuleS × VE.Grammar.Prepared Term) (fx : List String) (V : Vocab) (name : String)
    (ts : List Tok) : Except String Act := do
  if ts.any (fun t => match t with | .word w => w.contains '{' | _ => false) then
    throw s!"InvalidInput: act phrase for {name} has a slot joined to a word"
  match readingsBy V R rawCap stepBudget ts.toArray with
  | .ok [A] => pure A
  | .ok [] => throw s!"InvalidInput: act phrase for {name} has no reading under the declared frames"
  | .ok As => do
    let ms ← meaningTexts fx s!"the act phrase for {name}" As
    throw (s!"InvalidInput: act phrase for {name} has more than one reading: " ++ numbered ms)
  | .limit => throw s!"ResourceLimit: act phrase for {name} has too many readings to list; split the sentence"

/-- `joinedActBy` the vocabulary's reader, built for this act. -/
def joinedAct (fx : List String) (V : Vocab) (name : String) (ts : List Tok) : Except String Act :=
  joinedActBy (reader V) fx V name ts

/-- `checkAct` through a reader; a document's acts share one (`Norms.Wire.actsOf`). -/
def checkActBy (R : Array RuleS × VE.Grammar.Prepared Term) (fx : List String) (V : Vocab) (name : String) (arity : Nat)
    (raw : Json) : Except String (String × Option Act) :=
  match check fx name arity raw with
  | .ok a => .ok (a, none)
  | .error e => match checkWith (fun act ts => pure (act, ts)) fx name arity raw with
    | .ok (act, ts) => (joinedActBy R fx V name ts).map fun A => (act, some A)
    | .error _ => .error e

/-- The act check under `acts@0` from AP-3 on: a lexical act (`Lexical.check`), or a joined act: every condition of
    1.3 except 6, every slot standing alone as a word, and exactly one meaning (`read V rawCap stepBudget`). Returns
    the canonical act and, for a joined act, its act tree. With two or more meanings it raises D-15, which lists every
    meaning of `readings V rawCap stepBudget` through `meaningTexts` (6.2). An act `check` refuses while conditions
    1 to 5 and the lexing pass (`checkWith`) failed condition 6 only: it is joined. -/
def checkAct (fx : List String) (V : Vocab) (name : String) (arity : Nat) (raw : Json) :
    Except String (String × Option Act) :=
  checkActBy (reader V) fx V name arity raw

/-! ### Theorems (6.4) -/

/-- An act AP-1 accepts never enters the grammar (plan 2.5). -/
theorem checkAct_lexical (fx V name k raw a) (h : Lexical.check fx name k raw = .ok a) :
    VE.Acts.Wire.checkAct fx V name k raw = .ok (a, none) := by
  unfold checkAct checkActBy; rw [h]

theorem checkWith_lex {fx name k raw act ts}
    (h : checkWith (fun a ts => (pure (a, ts) : Except String (String × List Tok))) fx name k raw = .ok (act, ts)) :
    lex fx act = .ok ts := by
  unfold checkWith at h
  simp only [bind, Except.bind, pure, Except.pure] at h
  repeat' split at h
  all_goals first | (cases h; done) | skip
  all_goals (simp only [Except.ok.injEq, Prod.mk.injEq] at h; obtain ⟨rfl, rfl⟩ := h; assumption)

theorem joinedAct_read {fx V name ts A} (h : joinedAct fx V name ts = .ok A) :
    read V rawCap stepBudget ts.toArray = .ok A := by
  unfold joinedAct joinedActBy at h
  rw [readingsBy_reader] at h
  simp only [bind, Except.bind] at h
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
  unfold checkAct checkActBy at h
  split at h
  · cases h
  · split at h
    next act ts hw =>
      cases hj : joinedActBy (reader V) fx V name ts with
      | error e => rw [hj] at h; cases h
      | ok A' =>
        rw [hj] at h
        simp only [Except.map, Except.ok.injEq, Prod.mk.injEq, Option.some.injEq] at h
        obtain ⟨rfl, rfl⟩ := h
        exact ⟨ts, checkWith_lex hw, joinedAct_read hj⟩
    · cases h

end VE.Acts.Wire
