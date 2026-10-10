import VE.Ask.Groups
import VE.Service.Document
import VE.EnglishGrammar.Read
import VE.Surface

/-! The binding of an `ask` request to its document (docs/spec/question-answering.md 5.2; plan 4.3 item 4, R5, Q2.2).

`CaseBinding text case E L`: the readings case Lean replays is this document's. Its environment and every listed
front-matter input are the front matter's, compared as canonical JSON text (`Same`); `E` is the English environment
Lean decodes from the front matter and `L` passes the vocabulary policy for it; its units are the front matter's in
order, each compiled as the compiler compiles it (`UnitBound`): `{"ast": φ}` to bare `φ`, norm content kept, an
English fence read by `read` and a strict fence by `Surface.parse`, each to exactly one formula. `checkUnit` and
`checkCase` decide them (`checkUnit_sound`, `checkCase_sound`). Lean's `Json` has no decidable equality (its `==`
is a `partial` function, and an object's tree shape is not observable), so the checks compare `compress`d text, the
relation `Same` names, and derive a `Json` equation only between two strings. -/

namespace VE.Ask
open Lean

/-- Canonical JSON: `compress` writes an object's keys in sorted order. -/
def Same (a b : Json) : Prop := a.compress = b.compress

instance (a b : Json) : Decidable (Same a b) := inferInstanceAs (Decidable (a.compress = b.compress))

/-- The document-level front-matter inputs the readings case carries besides its environment and units. -/
def boundKeys : List String := ["reading_sets", "couplings", "narrowings", "completions"]

/-- Unit `i` of the case is the compiled form of front-matter unit `i`. `{"ast": φ}` compiles to bare `φ`;
    `{"norm": …}` keeps its norm object. A fence compiles to one bare formula, read through its declared surface.
    `V` is the replayed document's formula environment. -/
def UnitBound (E : VE.EnglishGrammar.Env) (L : VE.EnglishGrammar.Lexicon) (V : VE.Environment)
    (fences : List (String × String))
    (cu fu : Json) : Prop :=
  Same (cu.getObjValD "id") (fu.getObjValD "id") ∧ Same (cu.getObjValD "kind") (fu.getObjValD "kind") ∧
  let authored := fu.getObjValD "content"
  let compiled := cu.getObjValD "content"
  if authored.getObjValD "fence" != .null then
    ∃ f, authored.getObjValD "fence" = fu.getObjValD "id" ∧
      fences.lookup ((fu.getObjValD "id").getStr?.toOption.getD "") = some f ∧
      ((fu.getObjValD "surface" = .str "english" ∧
        ∃ φ, VE.EnglishGrammar.read E {} L VE.EnglishGrammar.workBudget f = .ok [(φ, false)] ∧
          Same compiled φ.encode) ∨
       (fu.getObjValD "surface" = .str "strict" ∧
        ∃ ψ, VE.Surface.parse V f = some [ψ] ∧ Same compiled (VE.Route.Wire.encodeFormula ψ)))
  else if authored.getObjValD "ast" != .null then Same compiled (authored.getObjValD "ast")
  else Same compiled authored

/-- The case is this document's: its environment and every listed input equal the front matter's, its units are the
    front matter's in order, `E` is the environment Lean decodes from the front matter, and `L` passes the vocabulary
    policy for it (so it is the policy's selection, `policy_selection`). -/
def CaseBinding (text : String) (case : Json) (E : VE.EnglishGrammar.Env) (L : VE.EnglishGrammar.Lexicon) : Prop :=
  ∃ (sp : VE.Discourse.Loader.Split) (re : VE.Readings.Wire.ReadingsEnvironment),
    VE.Service.Document.split text = .ok sp ∧
    Same (case.getObjValD "environment") (sp.front.getObjValD "environment") ∧
    VE.Readings.Wire.decodeEnvironment (case.getObjValD "environment") = .ok re ∧
    (∀ k ∈ boundKeys, Same ((case.getObjValD "document").getObjValD k) (sp.front.getObjValD k)) ∧
    VE.EnglishGrammar.Env.decode (sp.front.getObjValD "environment") (Json.mkObj []) = .ok E ∧
    L.policyOk E {} = true ∧
    ∃ cus fus : Array Json, (case.getObjValD "document").getObjValD "units" = .arr cus ∧
      sp.front.getObjValD "units" = .arr fus ∧ cus.size = fus.size ∧
      ∀ i (h₁ : i < cus.size) (h₂ : i < fus.size),
        UnitBound E L re.se.ne.rv.environment sp.fences cus[i] fus[i]

/-! ## Deciding the binding -/

/-- A JSON string's text. -/
def strOf? : Json → Option String
  | .str s => some s
  | _ => none

theorem eq_of_strOf? {j : Json} {s : String} (h : strOf? j = some s) : j = .str s := by
  cases j <;> simp_all [strOf?]

/-- A fence's one formula through its declared surface, as `UnitBound` compiles it. -/
def fenceOk (E : VE.EnglishGrammar.Env) (L : VE.EnglishGrammar.Lexicon) (V : VE.Environment) (surface : Option String)
    (f : String) (compiled : Json) : Bool :=
  match surface with
  | some "english" => match VE.EnglishGrammar.read E {} L VE.EnglishGrammar.workBudget f with
    | .ok [(φ, false)] => decide (Same compiled φ.encode)
    | _ => false
  | some "strict" => match VE.Surface.parse V f with
    | some [ψ] => decide (Same compiled (VE.Route.Wire.encodeFormula ψ))
    | _ => false
  | _ => false

/-- `UnitBound`, decided. -/
def checkUnit (E : VE.EnglishGrammar.Env) (L : VE.EnglishGrammar.Lexicon) (V : VE.Environment)
    (fences : List (String × String)) (cu fu : Json) : Bool :=
  decide (Same (cu.getObjValD "id") (fu.getObjValD "id")) &&
  decide (Same (cu.getObjValD "kind") (fu.getObjValD "kind")) &&
  let authored := fu.getObjValD "content"
  let compiled := cu.getObjValD "content"
  if authored.getObjValD "fence" != .null then
    match strOf? (authored.getObjValD "fence"), strOf? (fu.getObjValD "id") with
    | some a, some b => a == b && match fences.lookup b with
      | some f => fenceOk E L V (strOf? (fu.getObjValD "surface")) f compiled
      | none => false
    | _, _ => false
  else if authored.getObjValD "ast" != .null then decide (Same compiled (authored.getObjValD "ast"))
  else decide (Same compiled authored)

theorem fenceOk_sound {E : VE.EnglishGrammar.Env} {L : VE.EnglishGrammar.Lexicon} {V : VE.Environment}
    {fu : Json} {f : String} {compiled : Json}
    (h : fenceOk E L V (strOf? (fu.getObjValD "surface")) f compiled = true) :
    (fu.getObjValD "surface" = .str "english" ∧
        ∃ φ, VE.EnglishGrammar.read E {} L VE.EnglishGrammar.workBudget f = .ok [(φ, false)] ∧
          Same compiled φ.encode) ∨
      (fu.getObjValD "surface" = .str "strict" ∧
        ∃ ψ, VE.Surface.parse V f = some [ψ] ∧ Same compiled (VE.Route.Wire.encodeFormula ψ)) := by
  unfold fenceOk at h
  split at h
  · rename_i hs
    left
    refine ⟨eq_of_strOf? hs, ?_⟩
    split at h
    · rename_i φ hr
      exact ⟨φ, hr, by simpa using h⟩
    · cases h
  · rename_i hs
    right
    refine ⟨eq_of_strOf? hs, ?_⟩
    split at h
    · rename_i ψ hp
      exact ⟨ψ, hp, by simpa using h⟩
    · cases h
  · cases h

theorem checkUnit_sound {E : VE.EnglishGrammar.Env} {L : VE.EnglishGrammar.Lexicon} {V : VE.Environment}
    {fences : List (String × String)} {cu fu : Json} (h : checkUnit E L V fences cu fu = true) :
    UnitBound E L V fences cu fu := by
  unfold checkUnit at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨hid, hkind⟩, h⟩ := h
  refine ⟨hid, hkind, ?_⟩
  dsimp only at h ⊢
  split
  · rename_i hf
    rw [if_pos hf] at h
    split at h
    · rename_i a b ha hb
      simp only [Bool.and_eq_true, beq_iff_eq] at h
      obtain ⟨hab, h⟩ := h
      subst hab
      split at h
      · rename_i f hl
        refine ⟨f, (eq_of_strOf? ha).trans (eq_of_strOf? hb).symm, ?_, fenceOk_sound h⟩
        rw [eq_of_strOf? hb]
        simpa using hl
      · cases h
    · cases h
  · rename_i hf
    rw [if_neg hf] at h
    split
    · rename_i ha
      rw [if_pos ha] at h
      simpa using h
    · rename_i ha
      rw [if_neg ha] at h
      simpa using h

/-- Every unit of the case is the compiled front-matter unit at its position. -/
def checkUnits (E : VE.EnglishGrammar.Env) (L : VE.EnglishGrammar.Lexicon) (V : VE.Environment)
    (fences : List (String × String)) (cus fus : Array Json) : Bool :=
  cus.size == fus.size && (List.range cus.size).all fun i => match cus[i]?, fus[i]? with
    | some cu, some fu => checkUnit E L V fences cu fu
    | _, _ => false

theorem checkUnits_sound {E : VE.EnglishGrammar.Env} {L : VE.EnglishGrammar.Lexicon} {V : VE.Environment}
    {fences : List (String × String)} {cus fus : Array Json} (h : checkUnits E L V fences cus fus = true) :
    cus.size = fus.size ∧ ∀ i (h₁ : i < cus.size) (h₂ : i < fus.size), UnitBound E L V fences cus[i] fus[i] := by
  unfold checkUnits at h
  simp only [Bool.and_eq_true, beq_iff_eq, List.all_eq_true, List.mem_range] at h
  refine ⟨h.1, fun i h₁ h₂ => ?_⟩
  have hi := h.2 i h₁
  rw [Array.getElem?_eq_getElem h₁, Array.getElem?_eq_getElem h₂] at hi
  exact checkUnit_sound hi

/-- The binding's checks, in order, each with the text of its failure; `E` is decoded from the front matter. The
    result carries the proof. -/
def checkCase (text : String) (case : Json) (L : VE.EnglishGrammar.Lexicon) :
    Except String { E : VE.EnglishGrammar.Env // CaseBinding text case E L } :=
  match hs : VE.Service.Document.split text with
  | .error e => .error e
  | .ok sp =>
    if he : Same (case.getObjValD "environment") (sp.front.getObjValD "environment") then
      match hr : VE.Readings.Wire.decodeEnvironment (case.getObjValD "environment") with
      | .error e => .error e
      | .ok re =>
        if hk : ∀ k ∈ boundKeys, Same ((case.getObjValD "document").getObjValD k) (sp.front.getObjValD k) then
          match hE : VE.EnglishGrammar.Env.decode (sp.front.getObjValD "environment") (Json.mkObj []) with
          | .error e => .error e
          | .ok E =>
            if hp : L.policyOk E {} = true then
              match hc : (case.getObjValD "document").getObjValD "units", hf : sp.front.getObjValD "units" with
              | .arr cus, .arr fus =>
                if hu : checkUnits E L re.se.ne.rv.environment sp.fences cus fus = true then
                  .ok ⟨E, sp, re, hs, he, hr, hk, hE, hp, cus, fus, hc, hf, (checkUnits_sound hu).1,
                    (checkUnits_sound hu).2⟩
                else .error "CheckerUnavailable: the case is not this document's (a unit differs)"
              | _, _ => .error "CheckerUnavailable: the case is not this document's (its units are not a list)"
            else .error "CheckerUnavailable: the lexicon does not pass the vocabulary policy for this document"
        else .error "CheckerUnavailable: the case is not this document's (a front-matter input differs)"
    else .error "CheckerUnavailable: the case is not this document's (another environment)"

end VE.Ask
