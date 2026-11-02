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

/-- Of the phrase matches, those of the force's role, the first per `(predicate, constants)` (Python's
`dict.fromkeys` on `(predicate, args, role)`). -/
def ofForce (f : Force) (pm : List (VE.Norms.Regulated × List Fill)) : List (String × List Fill) :=
  (pm.filter (·.1.role == roleOf f)).foldl (fun acc (g, fs) =>
    if acc.any (fun (a, gs) => a == g.name && gs.map (·.const) == fs.map (·.const)) then acc
    else acc ++ [(g.name, fs)]) []

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

/-- `english.read`'s refusal of the sentence `c.`, said of the condition. -/
def unreadOf (E : Env) (L : Lexicon) (c : String) : GuardFault :=
  let fs := VE.EnglishGrammar.Run.translation ⟨E, {}, L, none, []⟩ maxCandidates (c ++ ".")
  .unread (strField fs "code") (ofCondition (strField fs "text"))

/-- The decision on one translation outcome of the sentence `c ++ "."`: an incomplete set or `.budget` is `limit`;
a marked reading is `ConclusionWithoutPremise`; a reading that does not decode closed and typed is `IllTyped`;
otherwise the distinct guards: one is `.ok`, two or more `ambiguous`, none (and every other outcome) `unreadOf`. -/
def guardOfOutcome (se : SpeechEnvironment) (E : Env) (L : Lexicon) (c : String) :
    TranslateOutcome → Except GuardFault VE.Formula
  | .readings rs complete =>
    if !complete then .error .limit
    else if rs.any (·.2.1) then
      .error (.unread "ConclusionWithoutPremise" (ofCondition (VE.EnglishGrammar.Run.noPremiseText 0)))
    else match rs.mapM (fun r => decodeClosedField se.ne.rv.environment r.1.encode) with
      | .error _ => .error (.unread "IllTyped" (ofCondition (VE.EnglishGrammar.Run.illTypedText (some 0))))
      | .ok gs => match gs.eraseDups with
        | [g] => .ok g
        | [] => .error (unreadOf E L c)
        | gs => .error (.ambiguous gs)
  | .budget => .error .limit
  | _ => .error (unreadOf E L c)

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

/-- Local command codes first; english-lean owns the condition's codes. -/
def Texts.classOf (code : String) : Option String :=
  (Texts.codeClasses.lookup code).orElse fun _ => VE.EnglishGrammar.Run.codeClasses.lookup code

end VE.Commands
