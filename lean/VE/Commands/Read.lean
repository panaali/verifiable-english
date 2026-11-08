import VE.SpeechActs.Wire
import VE.EnglishGrammar.Run
import VE.Commands.Texts

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

/-! ## The statements (section 3); the others are ci-1b's -/

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

end VE.Commands
