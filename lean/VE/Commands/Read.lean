import VE.SpeechActs.Wire
import VE.EnglishGrammar.Run
import VE.Commands.Texts
import VE.Scope.Theorems

/-! The Lean command reader (docs/spec/commands-imperatives.md sections 1 to 4): a wording of the merged forms, read
against a decoded speech environment, its scope and english-lean's lexicon. It has no caller until `english.command`
(CI-2). Each value is read once: the condition only when an act matched, the phrase matches once, inside the limits. -/

namespace VE.Commands

open VE.SpeechActs (Scope Force)
open VE.SpeechActs.Wire (SpeechEnvironment actVerb asciiWording decodeClosedField asciiSpace)
open VE.EnglishGrammar (Env Lexicon TranslateOutcome translateRequest fillHoles)

def maxWordingBytes : Nat := 400
/-- The search cap, also the cap of the condition reader's enumeration. -/
def maxCandidates : Nat := 4096

/-- What fills one act slot after slot 0: a declared constant and the words that named it. -/
structure Fill where
  const : String
  words : String
  deriving DecidableEq, Repr

/-- One reading of a command wording. `fills` has one row per slot after slot 0, in slot order; `guard` is `.top`
when the wording has no `, if`. -/
structure Reading where
  force : Force
  act   : String
  fills : List Fill
  guard : VE.Formula
  deriving DecidableEq, Repr

/-- The speech-acts command a reading denotes. -/
def Reading.command (u : String) (r : Reading) : VE.SpeechActs.Command :=
  { unit := u, force := r.force, act := r.act, args := r.fills.map (·.const), guard := r.guard }

/-- Python's `wording_text`: the wording without leading or trailing ASCII whitespace. -/
def trimmed (s : String) : String :=
  String.mk ((s.toList.dropWhile asciiSpace).reverse.dropWhile asciiSpace).reverse

/-- Python's `ascii_fold`: `A`-`Z` to `a`-`z`, nothing else. -/
def fold (s : String) : String := s.map Char.toLower

/-- A wording split: `Do not ` gives forbid, nothing gives require; the body; the condition after the last `, if `. -/
structure Parts where
  force : Force
  body : String
  condition : Option String
  deriving DecidableEq, Repr

/-- Python's `rsplit(", if ", 1)`. -/
def splitLastIf (s : String) : String × Option String :=
  match s.splitOn ", if " with
  | [x] => (x, none)
  | xs => (", if ".intercalate xs.dropLast, xs.getLast?)

/-- The prefix refusals, in Python's order (`parse_speech`). -/
def prefixRefusal (s : String) : Option (String × String) :=
  let t := trimmed s
  if !asciiWording t then some Texts.nonAscii
  else if t.isEmpty then some Texts.empty
  else if t.startsWith "You may " then some Texts.permission
  else if t.startsWith "Please " then some Texts.please
  else none

def parts (s : String) : Option Parts :=
  let t := trimmed s
  if (prefixRefusal s).isSome || !t.endsWith "." then none
  else
    let (plain, condition) := splitLastIf (t.dropRight 1)
    if plain.startsWith "Do not " then some ⟨.forbid, plain.drop 7, condition⟩
    else some ⟨.require, plain, condition⟩

/-- A prohibition is never `¬required`. -/
def roleOf : Force → VE.Norms.Role
  | .require => .obligation
  | .forbid => .permission

/-- The fills of a slot of sort `srt`: each constant of `srt` by its name, then each definite phrase bound to it
(Python's `_command_candidates`). -/
def slotFills (se : SpeechEnvironment) (sc : Scope) (srt : String) : List Fill :=
  (se.ne.rv.vocabulary.constants.filter (·.2 == srt)).flatMap fun (c, _) =>
    ⟨c, c⟩ :: (sc.definites.filter (·.2 == c)).map fun (p, _) => ⟨c, p⟩

/-- The act phrase after `{0} ` with hole `{i}` filled by `(fs[i-1]).words`, through english-lean's `fillHoles`;
`none` unless the holes are exactly `1` to `fs.length`. -/
def filled (act : String) (fs : List Fill) : Option String :=
  let (hs, t) := fillHoles (act.drop 4) fun k => ((fs[k - 1]?).map (·.words)).getD ""
  if hs.all (fun k => decide (1 ≤ k ∧ k ≤ fs.length)) &&
      (List.range fs.length).all (fun i => hs.contains (i + 1)) then some t else none

def tuples : List (List Fill) → List (List Fill)
  | [] => [[]]
  | xs :: rest => xs.flatMap fun x => (tuples rest).map (x :: ·)

/-- The regulated predicates a command can name: a role that is not `plain`, and an act with a verb. -/
def commandable (g : VE.Norms.Regulated) : Bool := g.role != .plain && (g.act.bind actVerb).isSome

/-- Every phrase match of a body, whatever the role. -/
def phraseMatches (se : SpeechEnvironment) (sc : Scope) (body : String) :
    List (VE.Norms.Regulated × List Fill) :=
  (se.ne.regulated.filter commandable).flatMap fun g =>
    let a := g.act.getD ""
    (tuples ((g.sorts.drop 1).map (slotFills se sc))).filterMap fun fs =>
      match filled a fs with
      | some t => if fold t == fold body then some (g, fs) else none
      | none => none

/-- One more match, unless one with its predicate and constants is already there. -/
def firstMatch (acc : List (String × List Fill)) (m : VE.Norms.Regulated × List Fill) : List (String × List Fill) :=
  if acc.any (fun (a, gs) => a == m.1.name && gs.map (·.const) == m.2.map (·.const)) then acc
  else acc ++ [(m.1.name, m.2)]

/-- Of the phrase matches, those of the force's role, the first per `(predicate, constants)` (Python's
`dict.fromkeys` on `(predicate, args, role)`). -/
def ofForce (f : Force) (pm : List (VE.Norms.Regulated × List Fill)) : List (String × List Fill) :=
  (pm.filter (·.1.role == roleOf f)).foldl firstMatch []

/-- Every act match of the force's role with a verb, including a mismatched slot 0; the addressee check runs only
after a unique reading. -/
def actMatches (se : SpeechEnvironment) (sc : Scope) (s : String) : List (String × List Fill) :=
  match parts s with
  | none => []
  | some p => ofForce p.force (phraseMatches se sc p.body)

/-- Why a condition gave no single guard. -/
inductive GuardFault
  | ambiguous (gs : List VE.Formula)     -- two or more distinct guards; every one becomes a reading
  | limit                                -- the enumeration stopped at its budget or its cap
  | unread (code text : String)          -- english-lean's refusal, its code and text
  deriving Repr, DecidableEq

/-- english-lean's text of a sentence-0 refusal, said of the condition. -/
def ofCondition (text : String) : String := text.replace "Sentence 1 " "The condition "

/-- The string field `k` of a row, `""` when absent. -/
def strField (fs : List (String × Lean.Json)) (k : String) : String :=
  match VE.Bridge.lookup fs k with
  | some (.str t) => t
  | _ => ""

/-- `english.read`'s refusal of the sentence `c.`, said of the condition, from its existing translation. -/
def unreadOf (E : Env) (L : Lexicon) (c : String) (o : TranslateOutcome) : GuardFault :=
  let fs := VE.EnglishGrammar.Run.translationOf ⟨E, {}, L, none, []⟩ (c ++ ".") o
  .unread (strField fs "code") (ofCondition (strField fs "text"))

/- Injected refusals retain their original translation result, even if the sentence would translate
differently against this environment. Both proof tasks and command conditions use `guardOfOutcome`. -/
#guard let E : Env := { sorts := [], predicates := [], constants := [] }
  let L : Lexicon := { nouns := [], letters := [], wordings := [], negatives := [], aliases := [], spellings := [] }
  match unreadOf E L "x" .notOneSentence, unreadOf E L "x" (.lexical (.badCharacter 0)) with
  | .unread c _, .unread d _ => c == "NotOneSentence" && d == "BadCharacter"
  | _, _ => false

/-- The decision on one translation outcome of the sentence `c ++ "."`: an incomplete set or `.budget` is `limit`;
a marked reading is `ConclusionWithoutPremise`; a reading that does not decode closed and typed is `IllTyped`;
otherwise the distinct guards: one is `.ok`, two or more `ambiguous`, none (and every other outcome) `unreadOf`. -/
def guardOfOutcome (se : SpeechEnvironment) (E : Env) (L : Lexicon) (c : String)
    (o : TranslateOutcome) : Except GuardFault VE.Formula :=
  match o with
  | .readings rs complete =>
    if !complete then .error .limit
    else if rs.any (·.2.1) then
      .error (.unread "ConclusionWithoutPremise" (ofCondition (VE.EnglishGrammar.Run.noPremiseText 0)))
    else match rs.mapM (fun r => decodeClosedField se.ne.rv.environment r.1.encode) with
      | .error _ => .error (.unread "IllTyped" (ofCondition (VE.EnglishGrammar.Run.illTypedText (some 0))))
      | .ok gs => match gs.eraseDups with
        | [g] => .ok g
        | [] => .error (unreadOf E L c o)
        | gs => .error (.ambiguous gs)
  | .budget => .error .limit
  | _ => .error (unreadOf E L c o)

/-- A condition's guard, over english-lean's translation of the one sentence `c ++ "."`. -/
def guardOf (se : SpeechEnvironment) (E : Env) (L : Lexicon) (b : Nat) (c : String) :
    Except GuardFault VE.Formula :=
  guardOfOutcome se E L c (translateRequest E {} L maxCandidates b (c ++ "."))

/-- The guards of one read: its one guard, or each of an ambiguous condition's; none on a fault. -/
def guardList : Except GuardFault VE.Formula → List VE.Formula
  | .ok g => [g]
  | .error (.ambiguous gs) => gs
  | .error _ => []

/-- Every guard a condition can have. -/
def guardsOf (se : SpeechEnvironment) (E : Env) (L : Lexicon) (b : Nat) (c : String) : List VE.Formula :=
  guardList (guardOf se E L b c)

/-- The one read of a wording's condition, made only when an act matched; `.top` when it has none. -/
def conditionOf (se : SpeechEnvironment) (E : Env) (L : Lexicon) (b : Nat) (p : Parts)
    (ms : List (String × List Fill)) : Except GuardFault VE.Formula :=
  match p.condition, ms with
  | some c, _ :: _ => guardOf se E L b c
  | _, _ => .ok .top

/-- Each act match with each guard. -/
def readingsOf (p : Parts) (ms : List (String × List Fill)) (gs : List VE.Formula) : List Reading :=
  ms.flatMap fun (a, fs) => gs.map fun g => ⟨p.force, a, fs, g⟩

/-- Every reading of a wording. -/
def candidates (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String) :
    List Reading :=
  match parts s with
  | none => []
  | some p =>
    let ms := actMatches se sc s
    readingsOf p ms (guardList (conditionOf se E L b p ms))

/-- The fill tuples the matcher tries: over the commandable predicates, the product of their slots' fill counts. -/
def tupleCount (se : SpeechEnvironment) (sc : Scope) : Nat :=
  ((se.ne.regulated.filter commandable).map fun g =>
    ((g.sorts.drop 1).map fun srt => (slotFills se sc srt).length).foldl (· * ·) 1).sum

def withinLimits (se : SpeechEnvironment) (sc : Scope) (s : String) : Bool :=
  (trimmed s).utf8ByteSize ≤ maxWordingBytes && tupleCount se sc ≤ maxCandidates

/-- The addressee is bound and has the sort of the act's slot 0. -/
def addressed (se : SpeechEnvironment) (sc : Scope) (r : Reading) : Bool :=
  match sc.addressee, se.ne.regulated.find? (·.name == r.act) with
  | some (srt, _), some g => g.sorts.head? == some srt
  | _, _ => false

inductive Outcome
  | one (r : Reading)
  | many (rs : List Reading)       -- 2 to `readingsBound` readings
  | refused (code text : String)   -- a code of `Texts.codeClasses`, or english-lean's for the condition
  | limit                          -- `Texts.limitText`
  deriving Repr, DecidableEq

def Outcome.ofText (x : String × String) : Outcome := .refused x.1 x.2

def coordinated (t : String) : Bool := (t.splitOn " and ").length > 1 && !t.startsWith "Do not "

/-- The last refusal: section 4's rows 13 and 14. -/
def noReading (s : String) : Outcome :=
  .ofText (if coordinated (trimmed s) then Texts.coordinated else Texts.noReading)

/-- The refusal of a parsed wording with no candidate, from its one read of the matches and the condition. -/
def refusalOf (s : String) (p : Parts) (pm : List (VE.Norms.Regulated × List Fill))
    (ms : List (String × List Fill)) (gr : Except GuardFault VE.Formula) : Outcome :=
  match ms with
  | [] =>
    match pm.find? (·.1.role != roleOf p.force) with
    | some (g, _) =>
      .refused (if p.force = .require then Texts.missingObligation else Texts.missingPermission) (g.act.getD g.name)
    | none => noReading s
  | [_] =>
    match gr with
    | .error .limit => .limit
    | .error (.unread code text) => .refused code text
    | _ => noReading s
  | _ => .ofText Texts.actsMatch

/-- Shared by the ordinary command and the proof task; a single reading still needs an addressed slot 0. -/
def checkedAddressee (se : SpeechEnvironment) (sc : Scope) (r : Reading) : Outcome :=
  if addressed se sc r then .one r
  else if sc.addressee.isNone then .ofText Texts.unbound
  else .ofText Texts.addressee

/-- `many` holds at most the speech wire's bound; more is `limit`. -/
def manyOf (rs : List Reading) : Outcome :=
  if rs.length ≤ VE.SpeechActs.Wire.readingsBound then .many rs else .limit

def readCommand (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String) : Outcome :=
  match prefixRefusal s with
  | some (code, text) => .refused code text
  | none =>
    if !withinLimits se sc s then .limit
    else match parts s with
      | none => noReading s
      | some p =>
        let pm := phraseMatches se sc p.body
        let ms := ofForce p.force pm
        let gr := conditionOf se E L b p ms
        match (readingsOf p ms (guardList gr)).eraseDups with
        | [r] => checkedAddressee se sc r
        | [] => refusalOf s p pm ms gr
        | rs => manyOf rs

/-- What a read command's typing needs of an environment: each regulated predicate is declared with its sorts and is
the one of its name, and each listed constant has its sort. -/
def declared (se : SpeechEnvironment) : Bool :=
  se.ne.regulated.all (fun g => se.ne.rv.environment.predicates g.name == some g.sorts &&
    se.ne.regulated.find? (·.name == g.name) == some g) &&
  se.ne.rv.vocabulary.constants.all fun (c, srt) => se.ne.rv.environment.constants c == some srt

/-- Local command codes first; english-lean owns the condition's codes. -/
def Texts.classOf (code : String) : Option String :=
  (Texts.codeClasses.lookup code).orElse fun _ => VE.EnglishGrammar.Run.codeClasses.lookup code

/-! ## The statements (section 3) -/

theorem mem_dedup {α : Type} [BEq α] [LawfulBEq α] : ∀ (n : Nat) (l : List α), l.length ≤ n →
    ∀ a, a ∈ l.eraseDups ↔ a ∈ l
  | _, [], _, _ => by simp
  | 0, _ :: _, h, _ => by simp at h
  | n + 1, x :: xs, h, a => by
    have hf := List.length_filter_le (fun b => !b == x) xs
    rw [List.eraseDups_cons, List.mem_cons, List.mem_cons,
      mem_dedup n _ (by simp at h; omega), List.mem_filter]
    by_cases hx : a = x <;> simp [hx]

theorem dedup_sub {α : Type} [BEq α] : ∀ (n : Nat) (l : List α), l.length ≤ n → ∀ a, a ∈ l.eraseDups → a ∈ l
  | _, [], _, _, h => by simp at h
  | 0, _ :: _, h, _, _ => by simp at h
  | n + 1, x :: xs, h, a, hm => by
    have hf := List.length_filter_le (fun b => !b == x) xs
    rw [List.eraseDups_cons, List.mem_cons] at hm
    rcases hm with rfl | hm
    · simp
    · exact List.mem_cons_of_mem _ (List.mem_filter.mp (dedup_sub n _ (by simp at h; omega) a hm)).1

theorem parts_prefix {s : String} {p : Parts} (h : parts s = some p) : prefixRefusal s = none := by
  unfold parts at h
  cases hp : prefixRefusal s with
  | none => rfl
  | some x => simp [hp] at h

theorem mem_mapM {α β ε : Type} {f : α → Except ε β} : ∀ {l : List α} {t : List β},
    l.mapM f = .ok t → ∀ y ∈ t, ∃ x ∈ l, f x = .ok y
  | [], t, h, y, hy => by cases h; cases hy
  | x :: l, t, h, y, hy => by
    simp only [List.mapM_cons] at h
    obtain ⟨z, hz, h⟩ := VE.Kit.Except.bind_ok h
    obtain ⟨ys, hys, h⟩ := VE.Kit.Except.bind_ok h
    cases h
    rcases List.mem_cons.mp hy with rfl | hy
    · exact ⟨x, List.mem_cons_self, hz⟩
    · obtain ⟨w, hw, hf⟩ := mem_mapM hys y hy
      exact ⟨w, List.mem_cons_of_mem _ hw, hf⟩

theorem mem_firstMatch : ∀ (l : List (VE.Norms.Regulated × List Fill)) (acc : List (String × List Fill))
    {a : String} {fs : List Fill},
    (a, fs) ∈ l.foldl firstMatch acc → (a, fs) ∈ acc ∨ ∃ g, (g, fs) ∈ l ∧ g.name = a
  | [], _, _, _, h => .inl h
  | m :: l, acc, a, fs, h => by
    rw [List.foldl_cons] at h
    rcases mem_firstMatch l _ h with h | ⟨g', hg, hn⟩
    · unfold firstMatch at h
      split at h
      · exact .inl h
      · rcases List.mem_append.mp h with h | h
        · exact .inl h
        · simp only [List.mem_singleton, Prod.mk.injEq] at h
          exact .inr ⟨m.1, by rw [h.2]; simp, h.1.symm⟩
    · exact .inr ⟨g', List.mem_cons_of_mem _ hg, hn⟩

/-- An act match is a phrase match of the force's role. -/
theorem mem_ofForce {f : Force} {pm : List (VE.Norms.Regulated × List Fill)} {a : String} {fs : List Fill}
    (h : (a, fs) ∈ ofForce f pm) : ∃ g, (g, fs) ∈ pm ∧ g.name = a ∧ g.role = roleOf f := by
  rcases mem_firstMatch _ [] h with h | ⟨g, hg, hn⟩
  · cases h
  · have := List.mem_filter.mp hg
    exact ⟨g, this.1, hn, by simpa using this.2⟩

theorem mem_phraseMatches {se : SpeechEnvironment} {sc : Scope} {body : String} {g : VE.Norms.Regulated}
    {fs : List Fill} (h : (g, fs) ∈ phraseMatches se sc body) :
    g ∈ se.ne.regulated ∧ commandable g = true ∧ fs ∈ tuples ((g.sorts.drop 1).map (slotFills se sc)) ∧
      ∃ t, filled (g.act.getD "") fs = some t ∧ fold t = fold body := by
  obtain ⟨g', hg', h⟩ := List.mem_flatMap.mp h
  obtain ⟨fs', hfs, h⟩ := List.mem_filterMap.mp h
  have hg := List.mem_filter.mp hg'
  cases ht : filled (g'.act.getD "") fs' with
  | none => simp [ht] at h
  | some t =>
    by_cases he : fold t == fold body
    · simp only [ht, he, if_true, Option.some.injEq, Prod.mk.injEq] at h
      obtain ⟨rfl, rfl⟩ := h
      exact ⟨hg.1, hg.2, hfs, t, ht, by simpa using he⟩
    · simp [ht, he] at h

theorem mem_slotFills {se : SpeechEnvironment} {sc : Scope} {srt : String} {f : Fill} (h : f ∈ slotFills se sc srt) :
    (f.const, srt) ∈ se.ne.rv.vocabulary.constants ∧ (f.words = f.const ∨ (f.words, f.const) ∈ sc.definites) := by
  obtain ⟨⟨c, s0⟩, hc, hf⟩ := List.mem_flatMap.mp h
  have hc := List.mem_filter.mp hc
  have hs : s0 = srt := by simpa using hc.2
  subst hs
  change f ∈ ⟨c, c⟩ :: _ at hf
  rcases List.mem_cons.mp hf with rfl | hf
  · exact ⟨hc.1, .inl rfl⟩
  · obtain ⟨⟨p, c'⟩, hp, rfl⟩ := List.mem_map.mp hf
    have hp := List.mem_filter.mp hp
    have hc' : c' = c := by simpa using hp.2
    subst hc'
    exact ⟨hc.1, .inr hp.1⟩

theorem decodeClosedField_check {T : VE.Environment} {j : Lean.Json} {φ : VE.Formula}
    (h : decodeClosedField T j = .ok φ) : φ.check T [] = true := by
  unfold decodeClosedField at h
  obtain ⟨_, _, h⟩ := VE.Kit.Except.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Kit.Except.bind_ok h
  unfold VE.Route.Wire.decodeClosed at h
  obtain ⟨_, _, h⟩ := VE.Kit.Except.bind_ok h
  obtain ⟨a, _, h⟩ := VE.Kit.Except.bind_ok h
  simp only [Bool.false_and, Bool.false_eq_true, ↓reduceIte, pure, Except.pure, bind, Except.bind] at h
  split at h
  · cases h
    rename_i hc
    simpa using hc
  · cases h

section Statements

variable (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String)

/-- The prefix refusals come first, in Python's order. -/
theorem readCommand_prefix (code text : String) (h : prefixRefusal s = some (code, text)) :
    readCommand se sc E L b s = .refused code text := by
  simp [readCommand, h]

/-- Past the limits, `readCommand` is its `candidates`, with the refusal of the same reads. -/
theorem readCommand_read {p : Parts} (hp : parts s = some p) (hl : withinLimits se sc s = true) :
    readCommand se sc E L b s =
      match (candidates se sc E L b s).eraseDups with
      | [r] => checkedAddressee se sc r
      | [] => refusalOf s p (phraseMatches se sc p.body) (actMatches se sc s)
          (conditionOf se E L b p (actMatches se sc s))
      | rs => manyOf rs := by
  have hm : actMatches se sc s = ofForce p.force (phraseMatches se sc p.body) := by simp [actMatches, hp]
  simp only [readCommand, parts_prefix hp, hl, Bool.not_true, Bool.false_eq_true, if_false, hp, candidates, hm]

theorem refusalOf_refused (p : Parts) (pm : List (VE.Norms.Regulated × List Fill)) (ms : List (String × List Fill))
    (gr : Except GuardFault VE.Formula) :
    (∀ r, refusalOf s p pm ms gr ≠ .one r) ∧ ∀ rs, refusalOf s p pm ms gr ≠ .many rs := by
  have ho : noReading s = .refused _ _ := rfl
  unfold refusalOf
  split
  · split
    · simp
    · simp [ho]
  · split <;> simp [ho]
  · simp [Outcome.ofText]

/-- A wording with no candidate never reads. -/
theorem readCommand_empty (hc : candidates se sc E L b s = []) :
    (∀ r, readCommand se sc E L b s ≠ .one r) ∧ ∀ rs, readCommand se sc E L b s ≠ .many rs := by
  have ho : noReading s = .refused _ _ := rfl
  cases hpf : prefixRefusal s with
  | some x => simp [readCommand_prefix se sc E L b s x.1 x.2 hpf]
  | none =>
    cases hl : withinLimits se sc s with
    | false => simp [readCommand, hpf, hl]
    | true =>
      cases hp : parts s with
      | none => simp [readCommand, hpf, hl, hp, ho]
      | some p =>
        rw [readCommand_read se sc E L b s hp hl, hc]
        exact refusalOf_refused s _ _ _ _

theorem checked_one (r r' : Reading) : checkedAddressee se sc r = .one r' ↔ r = r' ∧ addressed se sc r = true := by
  unfold checkedAddressee
  split
  · rename_i h; simp [h]
  · rename_i h; split <;> simp [Outcome.ofText, h]

theorem checked_many (r : Reading) (rs : List Reading) : checkedAddressee se sc r ≠ .many rs := by
  unfold checkedAddressee
  split
  · simp
  · split <;> simp [Outcome.ofText]

theorem manyOf_one (l : List Reading) (r : Reading) : manyOf l ≠ .one r := by
  unfold manyOf
  split <;> simp

theorem manyOf_iff (l rs : List Reading) :
    manyOf l = .many rs ↔ l = rs ∧ l.length ≤ VE.SpeechActs.Wire.readingsBound := by
  unfold manyOf
  split
  · simp_all
  · rename_i h
    simp only [reduceCtorEq, false_iff]
    exact fun ⟨_, h2⟩ => h h2

theorem parts_of_candidate (hc : candidates se sc E L b s ≠ []) : ∃ p, parts s = some p := by
  cases hp : parts s with
  | none => simp [candidates, hp] at hc
  | some p => exact ⟨p, rfl⟩

theorem readCommand_one_iff (r : Reading) :
    readCommand se sc E L b s = .one r ↔
      withinLimits se sc s = true ∧ (candidates se sc E L b s).eraseDups = [r] ∧ addressed se sc r = true := by
  by_cases hc : candidates se sc E L b s = []
  · simp [hc, (readCommand_empty se sc E L b s hc).1]
  obtain ⟨p, hp⟩ := parts_of_candidate se sc E L b s hc
  cases hl : withinLimits se sc s with
  | false => simp [readCommand, parts_prefix hp, hl]
  | true =>
    rw [readCommand_read se sc E L b s hp hl]
    generalize (candidates se sc E L b s).eraseDups = l
    match l with
    | [] => simp [(refusalOf_refused s _ _ _ _).1]
    | [r'] =>
      simp only [checked_one, List.cons.injEq, and_true, true_and]
      constructor <;> (rintro ⟨rfl, h⟩; exact ⟨rfl, h⟩)
    | _ :: _ :: _ => simp [manyOf_one]

theorem readCommand_many (rs : List Reading) :
    readCommand se sc E L b s = .many rs ↔
      withinLimits se sc s = true ∧ rs = (candidates se sc E L b s).eraseDups ∧ 2 ≤ rs.length ∧
        rs.length ≤ VE.SpeechActs.Wire.readingsBound := by
  by_cases hc : candidates se sc E L b s = []
  · simp only [hc, (readCommand_empty se sc E L b s hc).2, List.eraseDups_nil, false_iff]
    rintro ⟨_, rfl, h, _⟩
    simp at h
  obtain ⟨p, hp⟩ := parts_of_candidate se sc E L b s hc
  cases hl : withinLimits se sc s with
  | false => simp [readCommand, parts_prefix hp, hl]
  | true =>
    rw [readCommand_read se sc E L b s hp hl]
    generalize (candidates se sc E L b s).eraseDups = l
    match l with
    | [] =>
      simp only [(refusalOf_refused s _ _ _ _).2, false_iff]
      rintro ⟨_, rfl, h, _⟩
      simp at h
    | [r'] =>
      simp only [checked_many, false_iff]
      rintro ⟨_, rfl, h, _⟩
      simp at h
    | x :: y :: zs =>
      simp only [manyOf_iff, true_and]
      constructor
      · rintro ⟨rfl, h⟩; exact ⟨rfl, by simp, h⟩
      · rintro ⟨rfl, _, h⟩; exact ⟨rfl, h⟩

/-- Completeness: a wording with a candidate that fits the addressee is never refused. -/
theorem readCommand_complete (r : Reading) (hl : withinLimits se sc s = true)
    (hr : r ∈ candidates se sc E L b s) (ha : addressed se sc r = true)
    (hn : (candidates se sc E L b s).eraseDups.length ≤ VE.SpeechActs.Wire.readingsBound) :
    readCommand se sc E L b s = .one r ∨ ∃ rs, readCommand se sc E L b s = .many rs ∧ r ∈ rs := by
  have hm : r ∈ (candidates se sc E L b s).eraseDups := (mem_dedup _ _ (Nat.le_refl _) r).mpr hr
  generalize hc : (candidates se sc E L b s).eraseDups = l at hm hn
  match l, hm with
  | [x], hm =>
    obtain rfl : r = x := by simpa using hm
    exact .inl ((readCommand_one_iff se sc E L b s _).mpr ⟨hl, hc, ha⟩)
  | x :: y :: zs, hm =>
    exact .inr ⟨_, (readCommand_many se sc E L b s _).mpr ⟨hl, hc.symm, by simp, hn⟩, hm⟩

/-- Over the speech wire's bound, `limit`: never a refusal and never a truncated `many`. -/
theorem readCommand_bound (_hp : prefixRefusal s = none) (hl : withinLimits se sc s = true)
    (hn : VE.SpeechActs.Wire.readingsBound < (candidates se sc E L b s).eraseDups.length) :
    readCommand se sc E L b s = .limit := by
  have hc : candidates se sc E L b s ≠ [] := by
    intro h; simp [h] at hn
  obtain ⟨p, hq⟩ := parts_of_candidate se sc E L b s hc
  rw [readCommand_read se sc E L b s hq hl]
  generalize (candidates se sc E L b s).eraseDups = l at hn
  match l, hn with
  | [], hn => simp at hn
  | [_], hn => simp [VE.SpeechActs.Wire.readingsBound] at hn
  | x :: y :: zs, hn => simp only [manyOf, if_neg (Nat.not_le.mpr hn)]

/-- Every candidate is the wording: its act, with a verb, filled by its fills, is the body up to `A`-`Z` case. -/
theorem candidate_reads_back (r : Reading) (hr : r ∈ candidates se sc E L b s) :
    ∃ p g a t, parts s = some p ∧ p.force = r.force ∧ g ∈ se.ne.regulated ∧ g.name = r.act ∧
      g.role = roleOf r.force ∧ g.act = some a ∧ (actVerb a).isSome ∧ filled a r.fills = some t ∧
      fold t = fold p.body := by
  unfold candidates at hr
  cases hp : parts s with
  | none => simp [hp] at hr
  | some p =>
    simp only [hp, readingsOf, List.mem_flatMap, List.mem_map, actMatches] at hr
    obtain ⟨⟨a, fs⟩, hm, g, _, rfl⟩ := hr
    obtain ⟨g', hg, hn, hrole⟩ := mem_ofForce hm
    obtain ⟨hreg, hcmd, _, t, ht, hf⟩ := mem_phraseMatches hg
    have hv : (g'.act.bind actVerb).isSome = true := (Bool.and_eq_true _ _ ▸ hcmd).2
    cases hact : g'.act with
    | none => simp [hact] at hv
    | some a' =>
      simp only [hact, Option.bind_some, Option.getD_some] at hv ht
      exact ⟨p, g', a', t, rfl, rfl, hreg, hn, hrole, hact, hv, ht, hf⟩

/-! ### The guard, fill and refusal statements (ci-1b) -/

theorem eraseDups_nodup {α : Type} [BEq α] [LawfulBEq α] : ∀ (n : Nat) (l : List α), l.length ≤ n → l.eraseDups.Nodup
  | _, [], _ => by simp
  | 0, _ :: _, h => by simp at h
  | n + 1, x :: xs, h => by
    have hf := List.length_filter_le (fun b => !b == x) xs
    have hl : (xs.filter fun b => !b == x).length ≤ n := by simp at h; omega
    rw [List.eraseDups_cons, List.nodup_cons]
    exact ⟨fun hm => by simpa using (List.mem_filter.mp ((mem_dedup n _ hl _).mp hm)).2, eraseDups_nodup n _ hl⟩

/-- Every fill of a tuple comes from its slot's fills. -/
theorem mem_tuples : ∀ {xss : List (List Fill)} {fs : List Fill}, fs ∈ tuples xss → ∀ f ∈ fs, ∃ xs ∈ xss, f ∈ xs
  | [], fs, h, f, hf => by simp [tuples] at h; simp [h] at hf
  | xs :: rest, fs, h, f, hf => by
    simp only [tuples, List.mem_flatMap, List.mem_map] at h
    obtain ⟨x, hx, ys, hys, rfl⟩ := h
    rcases List.mem_cons.mp hf with rfl | hf
    · exact ⟨xs, List.mem_cons_self, hx⟩
    · obtain ⟨zs, hz, hm⟩ := mem_tuples hys f hf
      exact ⟨zs, List.mem_cons_of_mem _ hz, hm⟩

theorem mem_candidates {r : Reading} (hr : r ∈ candidates se sc E L b s) :
    ∃ p a fs g, parts s = some p ∧ (a, fs) ∈ actMatches se sc s ∧
      g ∈ guardList (conditionOf se E L b p (actMatches se sc s)) ∧ r = ⟨p.force, a, fs, g⟩ := by
  unfold candidates at hr
  cases hp : parts s with
  | none => simp [hp] at hr
  | some p =>
    simp only [hp, readingsOf, List.mem_flatMap, List.mem_map] at hr
    obtain ⟨⟨a, fs⟩, hm, g, hg, rfl⟩ := hr
    exact ⟨p, a, fs, g, rfl, hm, hg, rfl⟩

theorem candidate_guard (r : Reading) (hr : r ∈ candidates se sc E L b s) :
    match (parts s).bind (·.condition) with
    | none => r.guard = .top
    | some c => r.guard ∈ guardsOf se E L b c := by
  obtain ⟨p, a, fs, g, hp, hm, hg, rfl⟩ := mem_candidates se sc E L b s hr
  cases hms : actMatches se sc s with
  | nil => simp [hms] at hm
  | cons x xs =>
    rw [hms] at hg
    cases hc : p.condition with
    | none => simpa [hp, hc, conditionOf, guardList] using hg
    | some c => simpa [hp, hc, conditionOf, guardsOf] using hg

/-- A fill is a constant's own name or a phrase the scope binds to it (CI-4 adds the spelling). -/
theorem candidate_fills (r : Reading) (hr : r ∈ candidates se sc E L b s) :
    ∀ f ∈ r.fills, f.words = f.const ∨ (f.words, f.const) ∈ sc.definites := by
  obtain ⟨p, a, fs, g, hp, hm, _, rfl⟩ := mem_candidates se sc E L b s hr
  simp only [actMatches, hp] at hm
  obtain ⟨g', hg, _, _⟩ := mem_ofForce hm
  obtain ⟨_, _, ht, _⟩ := mem_phraseMatches hg
  intro f hf
  obtain ⟨xs, hxs, hfx⟩ := mem_tuples ht f hf
  obtain ⟨srt, _, rfl⟩ := List.mem_map.mp hxs
  exact (mem_slotFills hfx).2

theorem bind_condition {c : String} (hc : (parts s).bind (·.condition) = some c) :
    ∃ p, parts s = some p ∧ p.condition = some c := by
  cases hp : parts s with
  | none => simp [hp] at hc
  | some p => exact ⟨p, rfl, by simpa [hp] using hc⟩

/-- A faulted condition with one act match: the wording has no candidate and the refusal reads the fault. -/
theorem readCommand_fault {c : String} {f : GuardFault} (hl : withinLimits se sc s = true)
    (hc : (parts s).bind (·.condition) = some c) (hg : guardOf se E L b c = .error f)
    (hf : guardList (.error f) = []) (hm : (actMatches se sc s).length = 1) :
    ∃ p, parts s = some p ∧
      readCommand se sc E L b s = refusalOf s p (phraseMatches se sc p.body) (actMatches se sc s) (.error f) := by
  obtain ⟨p, hp, hpc⟩ := bind_condition s hc
  match hms : actMatches se sc s, hm with
  | [x], _ =>
    have hgr : conditionOf se E L b p [x] = .error f := by simp [conditionOf, hpc, hg]
    refine ⟨p, hp, ?_⟩
    rw [readCommand_read se sc E L b s hp hl, hms, hgr]
    simp [candidates, hp, hms, hgr, hf, readingsOf]

/-- Exhaustion is `limit`, never a refusal and never "no reading" (verdicts are three-valued). -/
theorem guard_limit (c : String) (hc : (parts s).bind (·.condition) = some c)
    (hg : guardOf se E L b c = .error .limit) (hm : (actMatches se sc s).length = 1) :
    readCommand se sc E L b s = .limit := by
  obtain ⟨p, hp, _⟩ := bind_condition s hc
  cases hl : withinLimits se sc s with
  | false => simp [readCommand, parts_prefix hp, hl]
  | true =>
    obtain ⟨_, _, h⟩ := readCommand_fault se sc E L b s hl hc hg rfl hm
    rw [h]
    match hms : actMatches se sc s, hm with
    | [x], _ => rfl

/-- An unread condition refuses with english-lean's code and text. -/
theorem guard_unread (c code text : String) (hl : withinLimits se sc s = true)
    (hc : (parts s).bind (·.condition) = some c) (hg : guardOf se E L b c = .error (.unread code text))
    (hm : (actMatches se sc s).length = 1) :
    readCommand se sc E L b s = .refused code text := by
  obtain ⟨_, _, h⟩ := readCommand_fault se sc E L b s hl hc hg rfl hm
  rw [h]
  match hms : actMatches se sc s, hm with
  | [x], _ => rfl

theorem outcome_ambiguous {c : String} {o : TranslateOutcome} {gs : List VE.Formula}
    (h : guardOfOutcome se E L c o = .error (.ambiguous gs)) : gs.Nodup ∧ 2 ≤ gs.length := by
  cases o with
  | readings rs complete =>
    simp only [guardOfOutcome] at h
    split at h
    · cases h
    split at h
    · cases h
    split at h
    · cases h
    rename_i ys _
    have hn := eraseDups_nodup _ ys (Nat.le_refl _)
    cases he : ys.eraseDups with
    | nil => simp [he, unreadOf] at h
    | cons x xs =>
      cases xs with
      | nil => simp [he] at h
      | cons y zs =>
        simp only [he, Except.error.injEq, GuardFault.ambiguous.injEq] at h
        subst h
        exact ⟨he ▸ hn, by simp⟩
  | invalidGrammar _ | lexical _ | notOneSentence => simp [guardOfOutcome, unreadOf] at h
  | budget => simp [guardOfOutcome] at h

/-- An ambiguous condition is never a silent choice: every guard is a reading. -/
theorem guard_ambiguous (c : String) (gs : List VE.Formula) (m : String × List Fill)
    (hl : withinLimits se sc s = true) (hc : (parts s).bind (·.condition) = some c)
    (hg : guardOf se E L b c = .error (.ambiguous gs)) (hm : m ∈ actMatches se sc s)
    (hn : (candidates se sc E L b s).eraseDups.length ≤ VE.SpeechActs.Wire.readingsBound) :
    ∃ rs, readCommand se sc E L b s = .many rs ∧ ∀ g ∈ gs, ∃ r ∈ rs, r.guard = g := by
  obtain ⟨p, hp, hpc⟩ := bind_condition s hc
  obtain ⟨hnd, hlen⟩ := outcome_ambiguous se E L hg
  have hr : ∀ g ∈ gs, (⟨p.force, m.1, m.2, g⟩ : Reading) ∈ (candidates se sc E L b s).eraseDups := by
    intro g hgm
    refine (mem_dedup _ _ (Nat.le_refl _) _).mpr ?_
    cases hms : actMatches se sc s with
    | nil => simp [hms] at hm
    | cons x xs =>
      have hgr : conditionOf se E L b p (x :: xs) = .error (.ambiguous gs) := by simp [conditionOf, hpc, hg]
      simp only [candidates, hp, hms, hgr, guardList, readingsOf, List.mem_flatMap, List.mem_map]
      exact ⟨m, by rw [← hms]; exact hm, g, hgm, rfl⟩
  match gs, hlen, hnd, hr with
  | g1 :: g2 :: rest, _, hnd, hr =>
    have h1 := hr g1 (by simp)
    have h2 := hr g2 (by simp)
    have hne : g1 ≠ g2 := fun h => by simp [h] at hnd
    generalize hl' : (candidates se sc E L b s).eraseDups = l at hr hn h1 h2
    match l, h1, h2 with
    | [x], h1, h2 =>
      have e1 := List.mem_singleton.mp h1
      have e2 := List.mem_singleton.mp h2
      exact absurd (congrArg Reading.guard (e1.trans e2.symm)) hne
    | x :: y :: zs, _, _ =>
      exact ⟨_, (readCommand_many se sc E L b s _).mpr ⟨hl, hl'.symm, by simp, hn⟩, fun g hgm => ⟨_, hr g hgm, rfl⟩⟩

theorem mapM_length {α β ε : Type} {f : α → Except ε β} : ∀ {l : List α} {t : List β},
    l.mapM f = .ok t → t.length = l.length
  | [], t, h => by cases h; rfl
  | x :: l, t, h => by
    simp only [List.mapM_cons] at h
    obtain ⟨_, _, h⟩ := VE.Kit.Except.bind_ok h
    obtain ⟨ys, hy, h⟩ := VE.Kit.Except.bind_ok h
    cases h
    simp [mapM_length hy]

theorem classOf_run {c : String} (h : (VE.EnglishGrammar.Run.codeClasses.lookup c).isSome = true) :
    (Texts.classOf c).isSome = true := by
  unfold Texts.classOf
  cases Texts.codeClasses.lookup c with
  | none => simpa [Option.orElse] using h
  | some _ => rfl

open VE.EnglishGrammar.Run (status coded noReadingFields translationOf) in
/-- The fallback formats an outcome that is not one complete reading, so its row has a classed code. -/
theorem unreadOf_classed {c code text : String} {o : TranslateOutcome} (hn : ∀ r, o ≠ .readings [r] true)
    (h : unreadOf E L c o = .unread code text) : (Texts.classOf code).isSome = true := by
  simp only [unreadOf, GuardFault.unread.injEq] at h
  rw [← h.1]
  unfold translationOf
  cases o with
  | readings rs complete =>
    simp only
    by_cases h2 : 2 ≤ rs.length
    · rw [if_pos h2]; rfl
    rw [if_neg h2]
    cases complete with
    | false => rfl
    | true =>
      match rs, h2, hn with
      | [], _, _ =>
        rw [if_neg (by decide), if_pos (by rfl)]
        unfold noReadingFields
        dsimp only
        split <;> rfl
      | [r], _, hn => exact absurd rfl (hn r)
      | _ :: _ :: _, h2, _ => simp at h2
  | lexical r =>
    have hc : strField (status "rejected" ++ coded r.code (VE.EnglishGrammar.Run.rejectText 0 r) ++
        ((VE.EnglishGrammar.Run.lexicalSpan (c ++ ".") r).toList.map fun s =>
          ("span", VE.EnglishGrammar.Run.spanJson s))) "code" = r.code := by
      simp [strField, status, coded, VE.Bridge.lookup]
    rw [hc]
    exact classOf_run (VE.EnglishGrammar.Run.codeClasses_total r)
  | invalidGrammar _ | notOneSentence | budget => rfl

/-- english-lean's refusal of a condition names a classed code: the fallback never formats one reading. -/
theorem guardOf_classed (c code text : String) (h : guardOf se E L b c = .error (.unread code text)) :
    (Texts.classOf code).isSome = true := by
  unfold guardOf at h
  generalize translateRequest E {} L maxCandidates b (c ++ ".") = o at h
  cases o with
  | budget => simp [guardOfOutcome] at h
  | invalidGrammar _ | lexical _ | notOneSentence =>
    refine unreadOf_classed E L ?_ (by simpa [guardOfOutcome] using h)
    intro r hr; cases hr
  | readings rs complete =>
    simp only [guardOfOutcome] at h
    split at h
    · cases h
    split at h
    · simp only [Except.error.injEq, GuardFault.unread.injEq] at h
      rw [← h.1]; rfl
    split at h
    · simp only [Except.error.injEq, GuardFault.unread.injEq] at h
      rw [← h.1]; rfl
    rename_i ys hy
    cases he : ys.eraseDups with
    | nil =>
      have hys : ys = [] := List.eq_nil_iff_forall_not_mem.mpr fun x hx => by
        simpa [he] using (mem_dedup _ _ (Nat.le_refl _) x).mpr hx
      refine unreadOf_classed E L (fun r hr => ?_) (by simpa [he] using h)
      have := mapM_length hy
      simp only [TranslateOutcome.readings.injEq] at hr
      simp [hys, hr.1] at this
    | cons x xs => cases xs <;> simp [he] at h

theorem conditionOf_classed {p : Parts} {ms : List (String × List Fill)} {code text : String}
    (h : conditionOf se E L b p ms = .error (.unread code text)) : (Texts.classOf code).isSome = true := by
  unfold conditionOf at h
  split at h
  · exact guardOf_classed se E L b _ _ _ h
  · cases h

/-- Every refusal names a classed code, or is english-lean's refusal of the condition. -/
theorem refused_classed (code text : String) (h : readCommand se sc E L b s = .refused code text) :
    (Texts.classOf code).isSome = true := by
  have hn : ∀ {c t}, noReading s = .refused c t → (Texts.classOf c).isSome = true := by
    intro c t hr
    unfold noReading Outcome.ofText at hr
    split at hr <;> (cases hr; rfl)
  cases hpf : prefixRefusal s with
  | some x =>
    rw [readCommand_prefix se sc E L b s x.1 x.2 hpf] at h
    cases h
    simp only [prefixRefusal] at hpf
    repeat' split at hpf
    all_goals first | (cases hpf; rfl) | cases hpf
  | none =>
    cases hl : withinLimits se sc s with
    | false => simp [readCommand, hpf, hl] at h
    | true =>
      cases hp : parts s with
      | none => exact hn (by simpa [readCommand, hpf, hl, hp] using h)
      | some p =>
        rw [readCommand_read se sc E L b s hp hl] at h
        generalize (candidates se sc E L b s).eraseDups = l at h
        match l with
        | [] =>
          simp only at h
          unfold refusalOf at h
          split at h
          · split at h
            · cases h
              simp only [Texts.missingObligation, Texts.missingPermission]
              split <;> rfl
            · exact hn h
          · split at h
            · cases h
            · cases h; exact conditionOf_classed se E L b ‹_›
            · exact hn h
          · cases h; rfl
        | [r'] =>
          simp only [checkedAddressee, Outcome.ofText] at h
          split at h
          · cases h
          · split at h <;> (cases h; rfl)
        | _ :: _ :: _ =>
          simp only [manyOf] at h
          split at h <;> cases h

/-- A guard of a condition is closed and typed: `decodeClosedField` checked it. -/
theorem outcome_checked {c : String} {o : TranslateOutcome} {g : VE.Formula}
    (h : g ∈ guardList (guardOfOutcome se E L c o)) : g.check se.ne.rv.environment [] = true := by
  cases o with
  | readings rs complete =>
    simp only [guardOfOutcome] at h
    split at h
    · cases h
    split at h
    · cases h
    split at h
    · cases h
    rename_i ys hy
    have hm : ∀ x ∈ ys.eraseDups, x.check se.ne.rv.environment [] = true := fun x hx => by
      obtain ⟨_, _, hd⟩ := mem_mapM hy x (dedup_sub _ _ (Nat.le_refl _) x hx)
      exact decodeClosedField_check hd
    cases he : ys.eraseDups with
    | nil => simp [he, unreadOf, guardList] at h
    | cons x xs =>
      rw [he] at hm
      cases xs with
      | nil =>
        simp only [he, guardList, List.mem_singleton] at h
        rw [h]
        exact hm x (by simp)
      | cons y zs => exact hm g (by simpa [he, guardList] using h)
  | invalidGrammar _ | lexical _ | notOneSentence => simp [guardOfOutcome, unreadOf, guardList] at h
  | budget => simp [guardOfOutcome, guardList] at h

/-- Every fill of a tuple has its slot's sort. -/
theorem tuples_typed (hc : ∀ c srt, (c, srt) ∈ se.ne.rv.vocabulary.constants →
    se.ne.rv.environment.constants c = some srt) : ∀ (ss : List String) {fs : List Fill},
    fs ∈ tuples (ss.map (slotFills se sc)) →
    VE.SpeechActs.constsTyped se.ne.rv.environment (fs.map (·.const)) ss = true
  | [], fs, h => by simp [tuples] at h; simp [h, VE.SpeechActs.constsTyped]
  | srt :: ss, fs, h => by
    simp only [List.map_cons, tuples, List.mem_flatMap, List.mem_map] at h
    obtain ⟨x, hx, ys, hys, rfl⟩ := h
    simp [VE.SpeechActs.constsTyped, hc _ _ (mem_slotFills hx).1, tuples_typed hc ss hys]

/-- A read command passes the semantic core's own check, given the `declared` facts of its environment. ci-1b proves
those facts of a decoded `JsonWF` environment, which is the spec's `readCommand_typed`. -/
theorem readCommand_typed_of_facts (r : Reading) (D : VE.SpeechActs.SpeechDoc) (u : String)
    (hf : declared se = true) (h : readCommand se sc E L b s = .one r)
    (hE : D.E = se.ne.rv.environment) (hS : D.scope = sc) (hR : D.regulated = se.ne.regulated)
    (hk : VE.SpeechActs.scopeOk D = true) :
    VE.SpeechActs.commandOk D (r.command u) = true := by
  simp only [declared, Bool.and_eq_true, List.all_eq_true, beq_iff_eq] at hf
  obtain ⟨hreg, hcon⟩ := hf
  obtain ⟨_, hc, ha⟩ := (readCommand_one_iff se sc E L b s r).mp h
  have hr : r ∈ candidates se sc E L b s := (mem_dedup _ _ (Nat.le_refl _) r).mp (by simp [hc])
  unfold candidates at hr
  cases hp : parts s with
  | none => simp [hp] at hr
  | some p =>
    simp only [hp, readingsOf, List.mem_flatMap, List.mem_map] at hr
    obtain ⟨⟨a, fs⟩, hm, g, hg, rfl⟩ := hr
    obtain ⟨g0, hgm, rfl, hrole⟩ := mem_ofForce (by simpa only [actMatches, hp] using hm)
    obtain ⟨hmem, _, ht, _⟩ := mem_phraseMatches hgm
    have hguard : g.check se.ne.rv.environment [] = true := by
      cases hms : actMatches se sc s with
      | nil => simp [hms] at hm
      | cons x xs =>
        rw [hms] at hg
        unfold conditionOf at hg
        split at hg
        · exact outcome_checked se E L hg
        · have : g = .top := by simpa [guardList] using hg
          rw [this]; rfl
    have hfind := (hreg g0 hmem).2
    simp only [addressed, hfind] at ha
    cases hadr : sc.addressee with
    | none => simp [hadr] at ha
    | some x =>
      obtain ⟨srt, you⟩ := x
      simp only [hadr, beq_iff_eq] at ha
      cases hs : g0.sorts with
      | nil => simp [hs] at ha
      | cons s0 rest =>
        have h0 : s0 = srt := by simpa [hs] using ha
        subst h0
        have hyou : D.E.constants you = some s0 := by
          simp only [VE.SpeechActs.scopeOk, hS, hadr, Bool.and_eq_true, beq_iff_eq] at hk
          exact hk.1.1.1.2.2
        have htyped := tuples_typed se sc (fun c srt hm => hcon _ hm) rest (fs := fs) (by simpa [hs] using ht)
        simp only [VE.SpeechActs.commandOk, VE.SpeechActs.regOf, hR, Reading.command, hfind, hS, hadr]
        subst hS
        simp [hE ▸ hyou, hE, (hreg g0 hmem).1, hs, hguard, htyped, VE.SpeechActs.constsTyped, hrole]
        cases p.force <;> simp [roleOf]

end Statements

/-! ## The decoder half of `readCommand_typed` (ci-1b; reviews/dri-decisions-20261102-ci-1.md item 1): a decoded
environment whose JSON is `JsonWF` has the `declared` facts, since then `decodeRegulatedIn` and the vocabulary decoder
read the same `arguments` of each predicate entry. -/

section Decoded

open Lean (Json)
open VE.Kit.Except (bind_ok)

theorem regulated_shape {ps fx : List String} {p : String} {args : List String} {raw : Json}
    {g : VE.Norms.Regulated} (h : VE.Norms.Wire.decodeRegulatedIn ps fx p args raw = .ok g) :
    g.name = p ∧ g.sorts = args := by
  simp only [VE.Norms.Wire.decodeRegulatedIn, VE.Norms.Wire.decodeRegulatedWith] at h
  repeat' (first
    | (cases h; done)
    | (cases h; exact ⟨rfl, rfl⟩)
    | (have h' := VE.Kit.Except.bind_ok h; clear h; obtain ⟨_, _, h⟩ := h'; try dsimp only at h)
    | (have h' := VE.Norms.Wire.ite_ok_cases h; clear h
       rcases h' with ⟨hc, h⟩ | ⟨hc, h⟩ <;> try (simp at hc; done))
    | split at h)
  all_goals simp_all [pure, Except.pure]

theorem envelope_vocabulary {env : Json} {e : VE.Route.Gate.Envelope} (h : VE.Route.Gate.decodeEnvelope env = .ok e) :
    env.getObjVal? "vocabulary" = .ok e.vocabulary := by
  unfold VE.Route.Gate.decodeEnvelope at h
  obtain ⟨_, _, h⟩ := VE.Kit.Except.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Kit.Except.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Kit.Except.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Kit.Except.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Kit.Except.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Kit.Except.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Kit.Except.bind_ok h
  obtain ⟨_, hv, h⟩ := VE.Kit.Except.bind_ok h
  cases h
  exact hv

/-- What W1's decoder reads past the speech block: the vocabulary of the stripped environment is the original's. -/
theorem strip_vocabulary {j s v : Json} (hw : VE.Scope.JsonWF j) (h : VE.SpeechActs.Wire.stripSpeech j = .ok s)
    (hv : s.getObjVal? "vocabulary" = .ok v) : j.getObjVal? "vocabulary" = .ok v := by
  unfold VE.SpeechActs.Wire.stripSpeech at h
  obtain ⟨_, _, h⟩ := VE.Kit.Except.bind_ok h
  obtain ⟨_, _, h⟩ := VE.Kit.Except.bind_ok h
  obtain ⟨fs, hfs, h⟩ := VE.Kit.Except.bind_ok h
  cases h
  cases j with
  | obj kvs =>
    have hfs' : fs = kvs.toList := by simpa [VE.Bridge.fields, Json.getObj?, bind, Except.bind, pure, Except.pure] using hfs.symm
    subst hfs'
    have hwf := VE.Scope.jsonWF_top _ hw kvs rfl
    have hnd : ((kvs.toList.filter (·.1 != "speech_acts")).map (·.1)).Nodup := by
      have := VE.Scope.members_nodup kvs hwf
      rw [VE.Scope.members_obj] at this
      exact this.sublist (List.Sublist.map _ List.filter_sublist)
    simp only [Json.mkObj] at hv
    rcases (VE.Scope.setObjVal_get _ Std.TreeMap.Raw.WF.ofList _ _ _ _).mp hv with ⟨he, _⟩ | ⟨_, hv⟩
    · exact absurd he (by decide)
    have hm := (VE.Scope.mkObj_getObjVal _ hnd _ _).mp hv
    exact VE.Scope.members_get kvs hwf _ _ (by rw [VE.Scope.members_obj]; exact (List.mem_filter.mp hm).1)
  | _ => simp [VE.Bridge.fields, Json.getObj?, bind, Except.bind, throw, throwThe, MonadExceptOf.throw] at hfs

theorem mapM_out {α β ε : Type} {f : α → Except ε β} : ∀ {l : List α} {t : List β},
    l.mapM f = .ok t → ∀ x ∈ l, ∃ y ∈ t, f x = .ok y
  | [], t, h, x, hx => by cases hx
  | x :: l, t, h, z, hz => by
    simp only [List.mapM_cons] at h
    obtain ⟨_, hb, h⟩ := bind_ok h
    obtain ⟨_, hbs, h⟩ := bind_ok h
    cases h
    rcases List.mem_cons.mp hz with rfl | hz
    · exact ⟨_, List.mem_cons_self, hb⟩
    · obtain ⟨y, hy, hf⟩ := mapM_out hbs z hz
      exact ⟨y, List.mem_cons_of_mem _ hy, hf⟩

theorem mapM_keys {α β γ ε : Type} {f : α → Except ε β} {g : β → γ} {k : α → γ}
    (hk : ∀ x y, f x = .ok y → g y = k x) : ∀ {l : List α} {t : List β}, l.mapM f = .ok t → t.map g = l.map k
  | [], t, h => by cases h; rfl
  | x :: l, t, h => by
    simp only [List.mapM_cons] at h
    obtain ⟨_, hb, h⟩ := bind_ok h
    obtain ⟨_, hbs, h⟩ := bind_ok h
    cases h
    simp [hk _ _ hb, mapM_keys hk hbs]

theorem eraseDups_sublist {α : Type} [BEq α] : ∀ (n : Nat) (l : List α), l.length ≤ n → l.eraseDups.Sublist l
  | _, [], _ => by simp
  | 0, _ :: _, h => by simp at h
  | n + 1, x :: xs, h => by
    have hf := List.length_filter_le (fun b => !b == x) xs
    rw [List.eraseDups_cons]
    exact ((eraseDups_sublist n _ (by simp at h; omega)).trans List.filter_sublist).cons₂ x

theorem nodup_of_eraseDups {α : Type} [BEq α] [LawfulBEq α] {l : List α} (h : l.eraseDups.length = l.length) :
    l.Nodup := by
  have hs := eraseDups_sublist _ l (Nat.le_refl _)
  rw [← hs.eq_of_length h]
  exact eraseDups_nodup _ l (Nat.le_refl _)

theorem mapM_rel {α β γ ε : Type} {f : α → Except ε β} {R : α → β → Prop} {g : β → γ} {k : α → γ}
    (hR : ∀ x y, f x = .ok y → R x y) (hk : ∀ x y, R x y → g y = k x) {l : List α} {t : List β}
    (h : l.mapM f = .ok t) : t.map g = l.map k ∧ ∀ x ∈ l, ∃ y ∈ t, R x y :=
  ⟨mapM_keys (fun x y hf => hk x y (hR x y hf)) h, fun x hx => (mapM_out h x hx).imp fun _ ⟨hy, hf⟩ => ⟨hy, hR _ _ hf⟩⟩

/-- What a decoded vocabulary keeps of its `predicates` and `constants` members: distinct names, and each predicate's
sorts as its `arguments` decode. -/
theorem vocabulary_facts {profiles : List String} {v : Json} {rv : VE.Route.Wire.RouteVocabulary}
    (h : VE.Route.Wire.decodeVocabulary profiles v = .ok rv) :
    ∃ P predicates, v.getObjVal? "predicates" = .ok P ∧ VE.Bridge.fields P = .ok predicates ∧
      (rv.vocabulary.predicates.map (·.1)).Nodup ∧ (rv.vocabulary.constants.map (·.1)).Nodup ∧
      ∀ p e, (p, e) ∈ predicates → ∃ a ss, e.getObjVal? "arguments" = .ok a ∧ VE.Bridge.strings a = .ok ss ∧
        (p, ss) ∈ rv.vocabulary.predicates := by
  unfold VE.Route.Wire.decodeVocabulary at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨sorts, _, h⟩ := bind_ok h
  obtain ⟨P, hP, h⟩ := bind_ok h
  obtain ⟨predicates, hpreds, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨constants, _, h⟩ := bind_ok h
  split at h
  case isTrue => cases h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  extract_lets names sortNames allowed flagged jpA at h
  split at h
  case isFalse => cases h
  rename_i hnames
  obtain ⟨_, _, h⟩ := bind_ok h
  dsimp (config := { zeta := false }) only [jpA] at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨psAndFlags, hps, h⟩ := bind_ok h
  extract_lets ps flags at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨cs, hcs, h⟩ := bind_ok h
  extract_lets literals result jpC at h
  split at h
  case isTrue => cases h
  dsimp (config := { zeta := false }) only [jpC] at h
  split at h
  case isFalse => cases h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨entries, hentries, h⟩ := bind_ok h
  split at h
  case isFalse => cases h
  split at h
  case h_2 => cases h
  cases h
  have hnd : names.Nodup := nodup_of_eraseDups (by simpa using hnames)
  have hpk : (predicates.map (·.1)).Nodup := hnd.sublist (by
    simp only [names, List.map_append]; exact (List.sublist_append_right _ _).trans (List.sublist_append_left _ _))
  have hck : (constants.map (·.1)).Nodup := hnd.sublist (by simp only [names, List.map_append]; exact List.sublist_append_right _ _)
  obtain ⟨hkeys, hmem⟩ := mapM_rel (R := fun (x : String × Json) (y : (String × List String) × Option VE.Data.Background.Flag) =>
      y.1.1 = x.1 ∧ ∃ a, x.2.getObjVal? "arguments" = .ok a ∧ VE.Bridge.strings a = .ok y.1.2)
    (g := fun y => y.1.1) (k := Prod.fst) (fun x y hF => by
      obtain ⟨p, e⟩ := x
      dsimp only at hF ⊢
      repeat' (first
        | (cases hF; done)
        | (cases hF; exact ⟨rfl, _, ‹_›, ‹_›⟩)
        | (have h' := bind_ok hF; clear hF; obtain ⟨_, _, hF⟩ := h'; try dsimp only at hF)
        | (have h' := VE.Norms.Wire.ite_ok_cases hF; clear hF
           rcases h' with ⟨hc, hF⟩ | ⟨hc, hF⟩ <;> try (simp at hc; done))
        | split at hF)) (fun _ _ h => h.1) hps
  have hcs' := mapM_keys (g := Prod.fst) (k := Prod.fst) (fun x y hF => by
      obtain ⟨c, e⟩ := x
      dsimp only at hF ⊢
      repeat' (first
        | (cases hF; done)
        | (cases hF; rfl)
        | (have h' := bind_ok hF; clear hF; obtain ⟨_, _, hF⟩ := h'; try dsimp only at hF)
        | (have h' := VE.Norms.Wire.ite_ok_cases hF; clear hF
           rcases h' with ⟨hc, hF⟩ | ⟨hc, hF⟩ <;> try (simp at hc; done))
        | split at hF)) hcs
  refine ⟨P, predicates, hP, hpreds, ?_, ?_, ?_⟩
  · show ((psAndFlags.map Prod.fst).map (·.1)).Nodup
    rw [List.map_map]; exact hkeys ▸ hpk
  · show (cs.map (·.1)).Nodup
    exact hcs' ▸ hck
  · intro p e hpe
    obtain ⟨y, hy, hk, a, ha, hs⟩ := hmem _ hpe
    exact ⟨a, y.1.2, ha, hs, List.mem_map.mpr ⟨y, hy, Prod.ext hk rfl⟩⟩

theorem filterMapM_rel {α β γ ε : Type} {f : α → Except ε (Option β)} {R : α → β → Prop} {g : β → γ} {k : α → γ}
    (hR : ∀ x y, f x = .ok (some y) → R x y) (hk : ∀ x y, R x y → g y = k x) :
    ∀ {l : List α} {t : List β}, l.filterMapM f = .ok t → (t.map g).Sublist (l.map k) ∧ ∀ y ∈ t, ∃ x ∈ l, R x y
  | [], t, h => by cases h; simp
  | x :: l, t, h => by
    rw [List.filterMapM_cons] at h
    obtain ⟨o, ho, h⟩ := bind_ok h
    cases o with
    | none =>
      obtain ⟨hs, hm⟩ := filterMapM_rel hR hk h
      exact ⟨hs.cons _, fun y hy => (hm y hy).imp fun _ ⟨hx, hr⟩ => ⟨List.mem_cons_of_mem _ hx, hr⟩⟩
    | some y =>
      obtain ⟨ts, hts, h⟩ := bind_ok h
      cases h
      obtain ⟨hs, hm⟩ := filterMapM_rel hR hk hts
      refine ⟨by rw [List.map_cons, List.map_cons, hk _ _ (hR _ _ ho)]; exact hs.cons₂ _, fun z hz => ?_⟩
      rcases List.mem_cons.mp hz with rfl | hz
      · exact ⟨x, List.mem_cons_self, hR _ _ ho⟩
      · exact (hm z hz).imp fun _ ⟨hx, hr⟩ => ⟨List.mem_cons_of_mem _ hx, hr⟩

theorem lookup_of_mem {β : Type} {k : String} {b : β} : ∀ {l : List (String × β)}, (k, b) ∈ l → (l.map (·.1)).Nodup →
    VE.Bridge.lookup l k = some b
  | x :: l, hm, hn => by
    rw [List.map_cons, List.nodup_cons] at hn
    rcases List.mem_cons.mp hm with rfl | hm
    · simp [VE.Bridge.lookup]
    · have hx : (x.1 == k) = false := by
        simp only [beq_eq_false_iff_ne]; rintro rfl; exact hn.1 (List.mem_map.mpr ⟨_, hm, rfl⟩)
      simpa [VE.Bridge.lookup, List.find?_cons, hx] using lookup_of_mem hm hn.2

theorem wf_get {j v : Json} {k : String} (hw : VE.Scope.JsonWF j) (h : j.getObjVal? k = .ok v) : VE.Scope.JsonWF v := by
  simpa [Json.getObjValD, h] using VE.Scope.jsonWF_getD j hw k

theorem fields_obj {j : Json} {l : List (String × Json)} (h : VE.Bridge.fields j = .ok l) :
    ∃ kvs, j = .obj kvs ∧ l = kvs.toList := by
  cases j with
  | obj kvs => exact ⟨kvs, rfl, by simpa [VE.Bridge.fields, Json.getObj?, bind, Except.bind, pure, Except.pure] using h.symm⟩
  | _ => simp [VE.Bridge.fields, Json.getObj?, bind, Except.bind, throw, throwThe, MonadExceptOf.throw] at h

theorem map_some_ok {ε β : Type} {m : Except ε β} {y : β} (h : (some <$> m : Except ε (Option β)) = .ok (some y)) :
    m = .ok y := by
  cases m with
  | error e => cases h
  | ok x => cases h; rfl

/-- A member of a well-formed object: its value is the one `getObjVal?` reads. -/
theorem wf_member {kvs : Std.TreeMap.Raw String Json} (hw : VE.Scope.JsonWF (.obj kvs)) {k : String} {v : Json}
    (h : (k, v) ∈ kvs.toList) : (Json.obj kvs).getObjVal? k = .ok v :=
  VE.Scope.members_get kvs (VE.Scope.jsonWF_top _ hw kvs rfl) k v (by rwa [VE.Scope.members_obj])

/-- W1's decoder over a vocabulary whose objects are well formed: each regulated predicate is declared with its
sorts, and the regulated and constant names are distinct. -/
theorem norms_facts {env : Json} {ne : VE.Norms.Wire.NormsEnvironment}
    (h : VE.Norms.Wire.decodeNormsEnvironment env = .ok ne)
    (hw : ∀ v, env.getObjVal? "vocabulary" = .ok v → VE.Scope.JsonWF v) :
    (∀ g ∈ ne.regulated, ne.rv.environment.predicates g.name = some g.sorts) ∧ (ne.regulated.map (·.name)).Nodup ∧
      (ne.rv.vocabulary.constants.map (·.1)).Nodup := by
  unfold VE.Norms.Wire.decodeNormsEnvironment at h
  simp only [VE.Norms.Wire.actsProfiles, List.isEmpty_nil, if_true, Bool.false_eq_true, if_false,
    VE.Norms.Wire.joinedActs, Bool.false_and] at h
  obtain ⟨e, he, h⟩ := bind_ok h
  split at h <;> try (cases h; done)
  obtain ⟨_, _, h⟩ := bind_ok h
  split at h <;> try (cases h; done)
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨P, hP, h⟩ := bind_ok h
  obtain ⟨predicates, hpreds, h⟩ := bind_ok h
  obtain ⟨stripped, hstr, h⟩ := bind_ok h
  obtain ⟨rv, hrv, h⟩ := bind_ok h
  obtain ⟨regs, hregs, h⟩ := bind_ok h
  split at h <;> try (cases h; done)
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨_, _, h⟩ := bind_ok h
  cases h
  -- the vocabulary, its `predicates` object and each entry are well formed
  have hv := hw _ (envelope_vocabulary he)
  obtain ⟨vk, hvk⟩ : ∃ vk, e.vocabulary = .obj vk := by
    cases hq : e.vocabulary with
    | obj vk => exact ⟨vk, rfl⟩
    | _ => rw [hq] at hP; simp [Json.getObjVal?, throw, throwThe, MonadExceptOf.throw] at hP
  have hPw := wf_get hv hP
  obtain ⟨pk, rfl, rfl⟩ := fields_obj hpreds
  have hpk : ((pk.toList).map (·.1)).Nodup := by
    simpa [VE.Scope.members_obj] using VE.Scope.members_nodup pk (VE.Scope.jsonWF_top _ hPw pk rfl)
  have hentry : ∀ x ∈ pk.toList, VE.Scope.JsonWF x.2 := by
    cases hPw with | obj _ _ hall => exact hall
  -- the stripped entries, keyed as the original
  obtain ⟨hskeys, hsmem⟩ := mapM_rel (R := fun (x y : String × Json) =>
      y.1 = x.1 ∧ ∃ fs, VE.Bridge.fields x.2 = .ok fs ∧ y.2 = Json.mkObj (fs.filter (·.1 != "regulated")))
    (g := Prod.fst) (k := Prod.fst) (fun x y hF => by
      obtain ⟨_, hfs, hF⟩ := bind_ok hF
      cases hF; exact ⟨rfl, _, hfs, rfl⟩) (fun _ _ h => h.1) hstr
  have hsnd : (stripped.map (·.1)).Nodup := hskeys ▸ hpk
  have hvp : (e.vocabulary.setObjVal! "predicates" (Json.mkObj stripped)).getObjVal? "predicates" =
      .ok (Json.mkObj stripped) := by
    rw [hvk]
    exact (VE.Scope.setObjVal_get _ (VE.Scope.jsonWF_top _ (hvk ▸ hv) vk rfl) _ _ _ _).mpr (.inl ⟨rfl, rfl⟩)
  obtain ⟨P', preds', hP', hpreds', hrk, hck, hargs⟩ := vocabulary_facts hrv
  rw [hvp] at hP'
  cases hP'
  obtain ⟨sk, hsk, rfl⟩ := fields_obj hpreds'
  -- the regulated declarations, each from a predicate entry
  obtain ⟨hrsub, hrmem⟩ := filterMapM_rel (R := fun (x : String × Json) (g : VE.Norms.Regulated) =>
      g.name = x.1 ∧ ∃ a, x.2.getObjVal? "arguments" = .ok a ∧ VE.Bridge.strings a = .ok g.sorts)
    (g := (·.name)) (k := Prod.fst) (fun x y hF => by
      repeat' (first
        | (cases hF; done)
        | (obtain ⟨h1, h2⟩ := regulated_shape (map_some_ok hF); exact ⟨h1, _, ‹_›, by rw [h2]; assumption⟩)
        | (have h' := bind_ok hF; clear hF; obtain ⟨_, _, hF⟩ := h'; try dsimp only at hF)
        | (have h' := VE.Norms.Wire.ite_ok_cases hF; clear hF
           rcases h' with ⟨hc, hF⟩ | ⟨hc, hF⟩ <;> try (simp at hc; done))
        | split at hF)) (fun _ _ h => h.1) hregs
  refine ⟨fun g hg => ?_, hpk.sublist hrsub, hck⟩
  obtain ⟨⟨p, entry⟩, hx, hn, a, ha, hs⟩ := hrmem g hg
  obtain ⟨y, hy, hy1, fs, hfs, hy2⟩ := hsmem _ hx
  have hyk : y ∈ sk.toList := by
    rw [Json.mkObj] at hsk
    cases hsk
    refine (Std.TreeMap.Raw.mem_toList_iff_getElem?_eq_some Std.TreeMap.Raw.WF.ofList).mpr ?_
    exact (VE.Scope.getObjVal_obj _ _ _).mp ((VE.Scope.mkObj_getObjVal _ hsnd _ _).mpr hy)
  obtain ⟨a', ss, ha', hs', hmem⟩ := hargs y.1 y.2 hyk
  obtain ⟨ek, rfl, rfl⟩ := fields_obj hfs
  have hew := hentry _ hx
  have hfk : (((ek.toList).filter (·.1 != "regulated")).map (·.1)).Nodup :=
    (by simpa [VE.Scope.members_obj] using VE.Scope.members_nodup ek (VE.Scope.jsonWF_top _ hew ek rfl) :
      ((ek.toList).map (·.1)).Nodup).sublist (List.Sublist.map _ List.filter_sublist)
  rw [hy2] at ha'
  have := wf_member hew (List.mem_filter.mp ((VE.Scope.mkObj_getObjVal _ hfk _ _).mp ha')).1
  rw [ha] at this
  cases this
  rw [hs] at hs'
  cases hs'
  show VE.Bridge.lookup rv.vocabulary.predicates g.name = some g.sorts
  rw [hn, ← hy1]
  exact lookup_of_mem hmem hrk

theorem find?_of_nodup {g : VE.Norms.Regulated} : ∀ {l : List VE.Norms.Regulated}, g ∈ l → (l.map (·.name)).Nodup →
    l.find? (·.name == g.name) = some g
  | x :: l, hm, hn => by
    rw [List.map_cons, List.nodup_cons] at hn
    rcases List.mem_cons.mp hm with rfl | hm
    · simp
    · have hx : (x.name == g.name) = false := by
        simp only [beq_eq_false_iff_ne]; intro he; exact hn.1 (List.mem_map.mpr ⟨g, hm, he.symm⟩)
      simp [hx, find?_of_nodup hm hn.2]

/-- The decoder half of `readCommand_typed`: a decoded environment whose JSON is well formed has the `declared`
facts. -/
theorem declared_of_decode {j : Json} {se : VE.SpeechActs.Wire.SpeechEnvironment} (hw : VE.Scope.JsonWF j)
    (hd : VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = .ok se) : declared se = true := by
  unfold VE.SpeechActs.Wire.decodeSpeechEnvironmentFull at hd
  obtain ⟨_, _, hd⟩ := bind_ok hd
  obtain ⟨_, _, hd⟩ := bind_ok hd
  obtain ⟨_, _, hd⟩ := bind_ok hd
  obtain ⟨_, _, hd⟩ := bind_ok hd
  obtain ⟨_, _, hd⟩ := bind_ok hd
  obtain ⟨_, _, hd⟩ := bind_ok hd
  obtain ⟨_, _, hd⟩ := bind_ok hd
  obtain ⟨st, hst, hd⟩ := bind_ok hd
  obtain ⟨ne, hne, hd⟩ := bind_ok hd
  obtain ⟨_, _, hd⟩ := bind_ok hd
  obtain ⟨_, _, hd⟩ := bind_ok hd
  obtain ⟨_, _, hd⟩ := bind_ok hd
  cases hd
  obtain ⟨hp, hn, hc⟩ := norms_facts hne fun v hv => wf_get hw (strip_vocabulary hw hst hv)
  simp only [declared, Bool.and_eq_true, List.all_eq_true, beq_iff_eq]
  exact ⟨fun g hg => ⟨hp g hg, find?_of_nodup hg hn⟩, fun x hx => lookup_of_mem hx hc⟩

variable (se : SpeechEnvironment) (sc : Scope) (E : Env) (L : Lexicon) (b : Nat) (s : String)

/-- A read command passes the semantic core's own check in every speech document over the same decoded environment
with a valid scope. -/
theorem readCommand_typed (j : Lean.Json) (r : Reading) (D : VE.SpeechActs.SpeechDoc) (u : String)
    (hw : VE.Scope.JsonWF j)
    (hd : VE.SpeechActs.Wire.decodeSpeechEnvironmentFull j = .ok se)
    (h : readCommand se sc E L b s = .one r)
    (hE : D.E = se.ne.rv.environment) (hS : D.scope = sc) (hR : D.regulated = se.ne.regulated)
    (hk : VE.SpeechActs.scopeOk D = true) :
    VE.SpeechActs.commandOk D (r.command u) = true :=
  readCommand_typed_of_facts se sc E L b s r D u (declared_of_decode hw hd) h hE hS hR hk

end Decoded

end VE.Commands
