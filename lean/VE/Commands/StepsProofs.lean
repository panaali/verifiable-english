import VE.Commands.Steps
import VE.Commands.SplitOnLemmas
import VE.Question.Strings

/-! Section 7's `preposed_eq` (docs/spec/commands-imperatives.md; item ci-3b), proved over the `String.splitOn`
lemmas of `VE.Commands.SplitOnLemmas`: the shape `If <c>, <x>.` takes `<x>` from a split at `, `, so `<x>` holds no
`, then ` and the condition-scope refusal never fires. `readStep_core` is `readStep_conservative` for a wording that
begins with neither `If ` nor `Then `; the act linter's half (a read command never begins so) is ci-3bb's. -/

namespace VE.Commands

open VE.SpeechActs (Scope)
open VE.SpeechActs.Wire (SpeechEnvironment asciiSpace)
open VE.EnglishGrammar (Env Lexicon)
open VE.Readings (eq_append_of_startsWith)
open VE.Commands.SplitOn (splitOn_two splitOn_free)

/-! ### Strings -/

/-- The trimmed wording is a run of the wording's characters. -/
theorem trimmed_infix (y : String) : (trimmed y).data <:+: y.data := by
  have h1 : (y.data.dropWhile asciiSpace).reverse.dropWhile asciiSpace <:+ (y.data.dropWhile asciiSpace).reverse :=
    List.dropWhile_suffix _
  have h2 : ((y.data.dropWhile asciiSpace).reverse.dropWhile asciiSpace).reverse <+: y.data.dropWhile asciiSpace := by
    simpa using List.reverse_prefix.2 h1
  exact h2.isInfix.trans (List.dropWhile_suffix _).isInfix

/-- An occurrence of `l ++ u` with `u` non-empty in `x ++ [d]` puts `l` inside `x`. -/
theorem infix_of_cut {l u x : List Char} {d : Char} (hu : u ≠ []) (h : l ++ u <:+: x ++ [d]) : l <:+: x := by
  obtain ⟨p, q, he⟩ := h
  have hne : u ++ q ≠ [] := by simp [hu]
  refine ⟨p, (u ++ q).dropLast, ?_⟩
  have := congrArg List.dropLast he
  rw [List.dropLast_concat, show p ++ (l ++ u) ++ q = p ++ l ++ (u ++ q) by simp,
    List.dropLast_append_of_ne_nil hne] at this
  exact this

theorem not_if_then {body : String} (h1 : body.startsWith "If " = true) : body.startsWith "Then " = false := by
  obtain ⟨u, rfl⟩ := eq_append_of_startsWith (by decide) h1
  cases h2 : ("If " ++ u).startsWith "Then " with
  | false => rfl
  | true =>
    obtain ⟨v, hv⟩ := eq_append_of_startsWith (by decide) h2
    have := congrArg (fun z : String => z.data.head?) hv
    simp [String.data_append] at this

/-- `If <c>, <x>.` takes `<x>` from the split of the body after `If ` at `, `. -/
theorem shapes_preposed {s c x : String} (h : shapes s = [.preposed c x]) :
    x ∈ (((trimmed s).dropRight 1).drop 3).splitOn ", " := by
  unfold shapes at h
  dsimp only at h
  split at h
  · simp at h
  generalize (trimmed s).dropRight 1 = body at h ⊢
  split at h
  · simp at h
  by_cases hi : body.startsWith "If " = true
  · rw [if_pos hi, if_neg (by simp [not_if_then hi]), if_neg (by simp [hi])] at h
    simp only [List.append_nil] at h
    generalize (body.drop 3).splitOn ", " = ws at h ⊢
    have hl := congrArg List.length h
    simp only [List.length_map, List.length_range, List.length_singleton] at hl
    rw [show ws.length - 1 = 1 by omega, show List.range 1 = [0] from rfl] at h
    simp only [List.map_cons, List.map_nil, List.cons.injEq, Shape.preposed.injEq, and_true] at h
    match ws, hl with
    | [_, _], _ => rw [← h.2]; exact .tail _ (.head _)
  · rw [if_neg hi] at h
    split at h <;> split at h <;> simp at h

/-- `<x>` of `If <c>, <x>.` holds no `, then `, so its step never has the condition-scope refusal. -/
theorem hasThen_preposed {s c x : String} (h : shapes s = [.preposed c x]) : hasThen (x ++ ".") = false := by
  have hx := splitOn_free _ ", " (by decide) x (shapes_preposed h)
  unfold hasThen
  apply decide_eq_false
  intro hlen
  have hi := (splitOn_two _ ", then " (by decide)).1 hlen
  have hi' : ", ".data ++ "then ".data <:+: x.data ++ ['.'] := by
    simpa [String.data_append] using hi.trans (trimmed_infix (x ++ "."))
  exact hx (infix_of_cut (by decide) hi')

/-! ### The statements -/

variable (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String)

/-- Section 7's statement with the hypothesis `hb` (SIGNED by the DRI 2026-11-09,
reviews/dri-decisions-20261109-ci-3a-wording.md item 1): `readStep` charges `maxWordingBytes` first. -/
theorem preposed_eq (c x : String) (r : Reading) (h : shapes s = [.preposed c x])
    (hb : (trimmed s).utf8ByteSize ≤ maxWordingBytes) :
    readStep se sc E L b s = .one r false ↔
      readCommand se sc E L b (capitalise x ++ ", if " ++ c ++ ".") = .one r := by
  rw [readStep_one se sc E L b s hb h]
  simp only [shapeOutcome, hasThen_preposed h, Bool.false_eq_true, if_false, lift_one, and_true]

/-- `readStep_conservative` for a wording whose body begins with neither `If ` nor `Then `: the only shape is the
merged wording, since `hs` leaves no sequence. -/
theorem readStep_core (r : Reading) (h : readCommand se sc E L b s = .one r) (hs : hasThen s = false)
    (hi : ((trimmed s).dropRight 1).startsWith "If " = false)
    (ht : ((trimmed s).dropRight 1).startsWith "Then " = false) :
    readStep se sc E L b s = .one r false := by
  have hw := ((readCommand_one_iff se sc E L b s r).1 h).1
  simp only [withinLimits, Bool.and_eq_true, decide_eq_true_eq] at hw
  have hsq : ¬ 2 ≤ (((trimmed s).dropRight 1).splitOn ", then ").length := by
    rw [splitOn_two _ _ (by decide), VE.Question.Str.dropRight_one]
    intro hi'
    have := (splitOn_two (trimmed s) ", then " (by decide)).2 (hi'.trans (List.dropLast_prefix _).isInfix)
    unfold hasThen at hs
    simp at hs; omega
  have hsh : shapes s = [.core s] := by
    unfold shapes
    dsimp only
    split
    · rfl
    rw [if_neg (by simp [hi]), if_neg (by simp [ht]), if_neg (by simp [hsq])]
    rfl
  rw [readStep_one se sc E L b s hw.1 hsh]
  simp [shapeOutcome, lift, h]

/-! ### Fixtures -/

#guard shapes "If draft is approved, click Ask." == [.preposed "draft is approved" "click Ask"]
#guard hasThen ("click Ask" ++ ".") == false
#guard capitalise "click Ask" ++ ", if " ++ "draft is approved" ++ "." == "Click Ask, if draft is approved."
#guard shapes "Click Check rule conflict." == [.core "Click Check rule conflict."]

end VE.Commands
