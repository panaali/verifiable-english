import VE.Norms.Wire
import VE.NormDefaults.Tree
import VE.Readings.Choice
import VE.Readings.Separate
import VE.Grammar.Reading

/-! Scratch stub for docs/spec/act-phrases.md, draft 1 (2026-10-13). NOT COMMITTED: delete it before any commit.

Every theorem the specification asks a batch to prove is written as `def <name>_stmt : Prop := <statement>`, so the
file needs no `sorry`. The definitions the fixtures compute have bodies. Each `#guard` pins one number of the
specification's section 11 (marked *hand* there). Run:

  cd lean && PATH=~/.elan/bin:$PATH lake env lean SpecStubs_act-phrases.lean

This file was written in a session whose shell was unavailable; it has never been elaborated. -/

/-! ## AP-1: `VE.Acts.Lexical` (spec 4.2, 4.3) -/

namespace VE.Acts.Lexical
open VE.Norms.Wire (actReserved words actWord scanSlots)

def joinWords : List String := ["and", "or", "nor", "for"]
def clauseWords : List String := actReserved.filter (fun w => !joinWords.contains w)

inductive Tok | word (w : String) | fixed (i : Nat) | slot (i : Nat) | comma
  deriving DecidableEq, Repr

def maxActBytes : Nat := 400
def maxPhraseBytes : Nat := 300
def maxPhrases : Nat := 128

def fold (s : String) : String := s.map (fun c => if c.toNat == 0x2019 then '\'' else c)
def normal (s : String) : String := " ".intercalate (words (fold s))
def dropComma (w : String) : String := if w.endsWith "," then w.dropRight 1 else w

def slotOf? (w : String) : Option Nat :=
  if w.length ≥ 3 && w.startsWith "{" && w.endsWith "}" then
    let d := (w.drop 1).dropRight 1
    if d.all Char.isDigit then some d.toNat! else none
  else none

def pieceToks (p : String) : Except String (List Tok) :=
  let body := dropComma p
  if body.isEmpty || body.contains ',' then .error "comma"
  else
    let t := match slotOf? body with
      | some i => Tok.slot i
      | none => Tok.word body
    .ok (if p.endsWith "," then [t, Tok.comma] else [t])

def rawLex (s : String) : Except String (List Tok) := do
  let tss ← ((s.splitOn " ").filter (· ≠ "")).mapM pieceToks
  let ts := tss.foldl (· ++ ·) []
  if ts.getLast? == some Tok.comma then throw "comma"
  pure ts

def phraseToks (p : String) : Except String (List Tok) := do
  let n := normal p
  if n.utf8ByteSize > maxPhraseBytes then throw s!"ResourceLimit: fixed phrase '{p}' is over 300 bytes"
  let ts ← match rawLex n with
    | .ok ts => pure ts
    | .error _ => throw s!"InvalidInput: fixed phrase '{p}' has a comma that does not follow a word"
  for t in ts do
    match t with
    | .slot _ => throw s!"InvalidInput: fixed phrase '{p}' holds a slot"
    | .word w =>
      unless actWord w do throw s!"InvalidInput: fixed phrase '{p}' has '{w}', which is not a word of letters"
      if clauseWords.contains w.toLower then throw s!"InvalidInput: fixed phrase '{p}' uses the clause word '{w}'"
    | _ => pure ()
  let nw := (ts.filter (fun t => match t with | .word _ => true | _ => false)).length
  unless nw ≥ 2 do throw s!"InvalidInput: fixed phrase '{p}' must hold two words or more"
  let edgeOk : Option Tok → Bool := fun
    | some (.word w) => !joinWords.contains w.toLower
    | _ => false
  unless edgeOk ts.head? && edgeOk ts.getLast? do
    throw s!"InvalidInput: fixed phrase '{p}' must begin and end with a word other than and, or, nor and for"
  pure ts

def clash (p q : List Tok) : Bool :=
  (List.range p.length).any (fun k =>
    let r := p.drop k
    (k != 0 || p != q) && (r.isPrefixOf q || q.isPrefixOf r))

def decodeFixed (fx : List String) : Except String (List (List Tok)) := do
  if fx.length > maxPhrases then throw "ResourceLimit: more than 128 fixed phrases"
  let ps ← fx.mapM phraseToks
  for i in List.range ps.length do
    for j in List.range ps.length do
      let p := ps.getD i []
      let q := ps.getD j []
      if i < j ∧ p = q then throw s!"InvalidInput: fixed phrase '{fx.getD j ""}' is declared twice"
      if (i = j ∧ clash p p = true) ∨ (i ≠ j ∧ p ≠ q ∧ clash p q = true) then
        throw s!"InvalidInput: fixed phrases '{fx.getD i ""}' and '{fx.getD j ""}' overlap, or one holds the other"
  pure ps

def fixedOk (fx : List String) : Bool := (decodeFixed fx).isOk

def group (ps : List (List Tok)) : Nat → List Tok → List Tok
  | 0, ts => ts
  | _ + 1, [] => []
  | n + 1, t :: rest =>
    match (List.range ps.length).find? (fun i => !(ps.getD i []).isEmpty && (ps.getD i []).isPrefixOf (t :: rest)) with
    | some i => .fixed i :: group ps n ((t :: rest).drop (ps.getD i []).length)
    | none => t :: group ps n rest

def lex (fx : List String) (s : String) : Except String (List Tok) := do
  let ps ← decodeFixed fx
  let ts ← rawLex (normal s)
  pure (group ps ts.length ts)

def check (fx : List String) (name : String) (arity : Nat) (raw : Lean.Json) : Except String String := do
  let act := normal ((raw.getStr?).toOption.getD "")
  let (slots, replaced) := scanSlots act.toList
  let ws := words (String.mk replaced)
  unless act.startsWith "{0} " && slots == (List.range arity).map toString && ws.length ≥ 2 &&
      ws.all (fun w => actWord (dropComma w)) do
    throw s!"InvalidInput: invalid act phrase for {name}"
  unless act.utf8ByteSize ≤ maxActBytes do throw s!"ResourceLimit: act phrase for {name} is over 400 bytes"
  if let some w := ws.find? (fun w => w != "slot" && clauseWords.contains (dropComma w).toLower) then
    throw s!"InvalidInput: act phrase for {name} uses the clause word '{dropComma w}'; write the condition in the rule's guard"
  let ts ← match lex fx act with
    | .ok ts => pure ts
    | .error e => if e == "comma" then throw s!"InvalidInput: act phrase for {name} ends with a comma" else throw e
  match ts.find? (fun t => match t with | .word w => joinWords.contains w.toLower | .comma => true | _ => false) with
  | some (.word w) => throw s!"InvalidInput: act phrase for {name} joins acts with '{w}' outside a fixed phrase"
  | some _ => throw s!"InvalidInput: act phrase for {name} has a comma outside a fixed phrase"
  | none => pure act

def Accepts (fx : List String) (k : Nat) (raw : Lean.Json) (a : String) : Prop :=
  let ws := words (String.mk (scanSlots a.toList).2)
  a = normal ((raw.getStr?).toOption.getD "") ∧ a.startsWith "{0} " = true ∧
  (scanSlots a.toList).1 = (List.range k).map toString ∧ 2 ≤ ws.length ∧
  (∀ w ∈ ws, actWord (dropComma w) = true) ∧ a.utf8ByteSize ≤ maxActBytes ∧
  (∀ w ∈ ws, w ≠ "slot" → clauseWords.contains (dropComma w).toLower = false) ∧
  ∃ ts, lex fx a = .ok ts ∧ ∀ t ∈ ts, t ≠ .comma ∧ ∀ w, t = .word w → joinWords.contains w.toLower = false

def check_spec_stmt : Prop :=
  ∀ (fx : List String), fixedOk fx = true → ∀ (name : String) (k : Nat) (raw : Lean.Json) (a : String),
    check fx name k raw = .ok a ↔ Accepts fx k raw a
def check_no_join_stmt : Prop :=
  ∀ (fx : List String) (name : String) (k : Nat) (raw : Lean.Json) (a : String), check fx name k raw = .ok a →
    ∀ ts : List Tok, lex fx a = .ok ts → ∀ t ∈ ts, (∀ w, t = .word w → joinWords.contains w.toLower = false) ∧ t ≠ .comma
def check_no_clause_stmt : Prop :=
  ∀ (fx : List String) (name : String) (k : Nat) (raw : Lean.Json) (a : String), check fx name k raw = .ok a →
    ∀ w ∈ words a, clauseWords.contains w.toLower = false
def fixedOk_unique_stmt : Prop :=
  ∀ (fx : List String) (ps : List (List Tok)) (ts : List Tok), decodeFixed fx = .ok ps →
    ∀ i j (hi : i < ps.length) (hj : j < ps.length) (m n : Nat),
      (ps[i]).isPrefixOf (ts.drop m) = true → (ps[j]).isPrefixOf (ts.drop n) = true → (i, m) ≠ (j, n) →
      m + (ps[i]).length ≤ n ∨ n + (ps[j]).length ≤ m
def check_extends_stmt : Prop :=
  ∀ (fx : List String), fixedOk fx = true → ∀ (name : String) (k : Nat) (raw : Lean.Json) (a : String),
    VE.Norms.Wire.canonicalAct name k raw = .ok a → (∀ w ∈ words a, w.toLower ≠ "nor") → check fx name k raw = .ok a

inductive Form | right | entitled
  deriving DecidableEq, Repr
def Form.text : Form → String
  | .right => "has the right"
  | .entitled => "is entitled"
def Form.ofText? (s : String) : Option Form :=
  if s == "has the right" then some .right else if s == "is entitled" then some .entitled else none
def wording (f : Form) (act : String) : String := "{0} " ++ f.text ++ " " ++ act.drop 4
def wording_subject_first_stmt : Prop :=
  ∀ (f : Form) (act : String), act.startsWith "{0} " = true → (wording f act).startsWith "{0} " = true

end VE.Acts.Lexical

/-! ## AP-1: the decoder hunks (spec 4.2, 4.3) -/

namespace VE.Acts.WireStub
open VE.Acts.Lexical (Form)

def decodeRegulatedActs (fx : List String) (name : String) (args : List String) (raw : Lean.Json) :
    Except String VE.Norms.Regulated := do
  let obj ← match raw.getObj? with
    | .ok o => pure o.toList
    | .error _ => throw s!"InvalidInput: regulated declaration {name} needs role and default"
  let keys := obj.map Prod.fst
  unless keys.contains "role" && keys.contains "default" do
    throw s!"InvalidInput: regulated declaration {name} needs role and default"
  let role ← match raw.getObjValD "role" with
    | .str "permission" => pure VE.Norms.Role.permission
    | .str "obligation" => pure VE.Norms.Role.obligation
    | .str "plain" => pure VE.Norms.Role.plain
    | _ => throw s!"InvalidInput: invalid regulated role or default for {name}"
  let allow ← match raw.getObjValD "default" with
    | .str "allow" => pure true
    | .str "deny" => pure false
    | _ => throw s!"InvalidInput: invalid regulated role or default for {name}"
  let required := ["role", "default"] ++ (if role == .plain then [] else ["act"])
  let allowed := required ++ (if role == .obligation then ["permission"] else []) ++
    (if role == .plain then ["act", "form"] else [])
  unless keys.all allowed.contains && required.all keys.contains do
    throw s!"InvalidInput: invalid regulated fields for {name}"
  if role == .plain && (keys.contains "act" != keys.contains "form") then
    throw s!"InvalidInput: a plain act for {name} needs its form, and a form needs its act"
  if role == .plain && keys.contains "form" then
    match raw.getObjValD "form" with
    | .str s => unless (Form.ofText? s).isSome do throw s!"InvalidInput: invalid form for {name}"
    | _ => throw s!"InvalidInput: invalid form for {name}"
  let act ← if keys.contains "act" then some <$> VE.Acts.Lexical.check fx name args.length (raw.getObjValD "act")
    else pure none
  let permission ← match raw.getObjVal? "permission" with
    | .error _ => pure none
    | .ok .null => pure none
    | .ok (.str m) => pure (some m)
    | .ok _ => throw s!"InvalidInput: invalid permission dual for {name}"
  pure ⟨name, args, allow, role, act, permission⟩

def decodeRegulatedIn (profiles fx : List String) (name : String) (args : List String) (raw : Lean.Json) :
    Except String VE.Norms.Regulated :=
  if profiles.contains "acts@0" then decodeRegulatedActs fx name args raw
  else VE.Norms.Wire.decodeRegulated name args raw

def canonicalActIn (profiles fx : List String) (name : String) (k : Nat) (raw : Lean.Json) : Except String String :=
  if profiles.contains "acts@0" then VE.Acts.Lexical.check fx name k raw else VE.Norms.Wire.canonicalAct name k raw

def decodeRegulated_without_acts_stmt : Prop :=
  ∀ (ps fx : List String), "acts@0" ∉ ps → decodeRegulatedIn ps fx = VE.Norms.Wire.decodeRegulated
def canonicalActIn_without_acts_stmt : Prop :=
  ∀ (ps fx : List String), "acts@0" ∉ ps → canonicalActIn ps fx = VE.Norms.Wire.canonicalAct
def decodeRegulated_plain_stmt : Prop :=
  ∀ (name : String) (args : List String) (raw : Lean.Json) (r : VE.Norms.Regulated),
    VE.Norms.Wire.decodeRegulated name args raw = .ok r → r.role = .plain → r.act = none

end VE.Acts.WireStub

/-! ## AP-2: the act grammar (spec 5) -/

namespace VE.Acts
open Lexical (Tok)

structure Frame where
  head : List String
  markers : List String
  split : List String
  mods : List String
  deriving DecidableEq, Repr

structure Vocab where
  frames : List Frame
  adverbs : List String
  deriving DecidableEq, Repr

inductive Join | and | or | nor
  deriving DecidableEq, Repr
inductive Part | slot (i : Nat) | fixed (i : Nat) | words (ws : List String)
  deriving DecidableEq, Repr
inductive Filler | one (p : Part) | joined (j : Join) (ps : List Part)
  deriving DecidableEq, Repr
inductive Modifier | adv (w : String) | prep (m : String) (p : Part)
  deriving DecidableEq, Repr

structure Atom where
  toWord : Bool
  beWord : Bool
  head : List String
  args : List (String × Filler)
  mods : List Modifier
  deriving DecidableEq, Repr

inductive Act
  | one (a : Atom)
  | all (shared split : Bool) (parts : List Atom)
  | any (nor split : Bool) (parts : List Atom)
  deriving DecidableEq, Repr

def emptyAtom : Atom := { toWord := false, beWord := false, head := [], args := [], mods := [] }

inductive Attach | own | first | last | all
  deriving DecidableEq, Repr

inductive Elt
  | arg (m : String) (fl : Filler)
  | split (m : String) (j : Join) (ps : List Part)
  | adv (w : String) (att : Attach)
  | prep (m : String) (p : Part) (att : Attach)
  | group (j : Join) (ms : List Modifier)
  deriving DecidableEq, Repr

structure Item where
  fw : List String
  advs : List (String × Attach)
  head : List String
  elts : List Elt
  deriving DecidableEq, Repr

/-! ### Terminals (5.1) -/

inductive Term
  | subj | slot | fixed | comma | never
  | kw (w : String)
  | adv (ws : List String)
  | fill (excl : List String)
  deriving DecidableEq, Repr

def Term.accepts : Term → Tok → Bool
  | .subj, .slot 0 => true
  | .slot, .slot (_ + 1) => true
  | .fixed, .fixed _ => true
  | .comma, .comma => true
  | .kw w, .word v => v.toLower == w
  | .adv ws, .word v => ws.contains v.toLower
  | .fill ex, .word v => !ex.contains v.toLower
  | _, _ => false

instance : VE.Grammar.Accepts Term Tok := ⟨Term.accepts⟩

/-! ### Frames (1.4) -/

def wordsOf (m : String) : List String := (m.splitOn " ").filter (· ≠ "")
def firstWord (m : String) : Option String := (wordsOf m).head?
def Frame.hasObject (f : Frame) : Bool := f.markers.contains ""
def Frame.argMarkers (f : Frame) : List String := f.markers.filter (· ≠ "")
def Frame.splitMarkers (f : Frame) : List String := f.argMarkers.filter (fun m => f.split.contains m)
def Frame.plainMarkers (f : Frame) : List String := f.argMarkers.filter (fun m => !f.split.contains m)
def Frame.objSplit (f : Frame) : Bool := f.hasObject && f.split.contains ""

def fillExcl (V : Vocab) (f : Frame) : List String :=
  ["and", "or", "nor", "to", "be"] ++ V.adverbs ++ (f.markers ++ f.mods).filterMap firstWord ++
    V.frames.filterMap (fun g => g.head.head?)

def wordOk (w : String) : Bool := VE.Norms.Wire.actWord w && w == w.toLower
def prefixFree (ms : List (List String)) : Bool :=
  ms.all (fun a => ms.all (fun b => a == b || !a.isPrefixOf b))

def framesOk (V : Vocab) : Bool :=
  let fs := V.frames
  let heads := fs.map (·.head)
  let reserved := ["and", "or", "nor", "to", "be"] ++ Lexical.clauseWords
  let markerReserved := ["and", "or", "nor", "be"] ++ Lexical.clauseWords
  let markerWords := fs.flatMap (fun f => (f.markers ++ f.mods).flatMap wordsOf)
  decide (fs.length ≤ 128) && decide heads.Nodup && prefixFree heads &&
  fs.all (fun f =>
    !f.head.isEmpty && f.head.all (fun w => wordOk w && !reserved.contains w) &&
    decide f.markers.Nodup && decide f.mods.Nodup &&
    f.split.all (fun m => f.markers.contains m) &&
    f.mods.all (fun m => m != "" && !f.markers.contains m) &&
    (f.markers ++ f.mods).all (fun m => (wordsOf m).all (fun w => wordOk w && !markerReserved.contains w)) &&
    prefixFree (((f.markers ++ f.mods).filter (· ≠ "")).map wordsOf)) &&
  decide V.adverbs.Nodup &&
  V.adverbs.all (fun a => wordOk a && !reserved.contains a && !markerWords.contains a &&
    !heads.any (fun h => h.contains a)) &&
  heads.all (fun h => match h.head? with
    | some w => !markerWords.contains w
    | none => false)

/-! ### The rule table (5.2) -/

inductive Kind
  | pass | head | fw | part
  | arg (m : String)
  | list (m : String) (split : Bool)
  | adv (att : Attach)
  | padv (att : Attach)
  | prep (m : String) (att : Attach)
  | modAdv
  | modPrep (m : String)
  | group | core | item | single
  | coord (shared rnr : Bool)
  | start
  deriving DecidableEq, Repr

inductive RSym | t (a : Term) | n (x : String)
  deriving DecidableEq, Repr

structure RuleS where
  lhs : String
  rhs : List RSym
  kind : Kind
  deriving Repr

def kwSyms (ws : List String) : List RSym := ws.map (fun w => RSym.t (.kw w))

def globalRules (V : Vocab) : List RuleS :=
  let advT := RSym.t (.adv V.adverbs)
  let ms := ((V.frames.flatMap (fun f => f.markers ++ f.mods)).filter (· ≠ "")).eraseDups
  ([ ⟨"S", [.t .subj, .n "SINGLE"], .start⟩, ⟨"S", [.t .subj, .n "COORD"], .start⟩,
    ⟨"J", kwSyms ["and"], .pass⟩, ⟨"J", kwSyms ["or"], .pass⟩, ⟨"J", kwSyms ["nor"], .pass⟩,
    ⟨"FW", kwSyms ["to"], .fw⟩, ⟨"FW", kwSyms ["be"], .fw⟩, ⟨"FW", kwSyms ["to", "be"], .fw⟩,
    ⟨"TOK", [.t .slot], .pass⟩, ⟨"TOK", [.t .fixed], .pass⟩,
    ⟨"ADVO", [advT], .padv .own⟩,
    ⟨"ADVSO", [.n "ADVO"], .pass⟩, ⟨"ADVSO", [.n "ADVO", .n "ADVSO"], .pass⟩,
    ⟨"E1X", [advT], .padv .first⟩, ⟨"E1X", [advT], .padv .all⟩,
    ⟨"E1S", [.n "E1X"], .pass⟩, ⟨"E1S", [.n "E1X", .n "E1S"], .pass⟩ ] : List RuleS) ++
  ms.map (fun m => (⟨"MK:" ++ m, kwSyms (wordsOf m), .pass⟩ : RuleS))

def singleRules : List RuleS :=
  [ ⟨"SINGLE", [.n "SC"], .single⟩, ⟨"SINGLE", [.n "ADVSO", .n "SC"], .single⟩,
    ⟨"SINGLE", [.n "FW", .n "SC"], .single⟩, ⟨"SINGLE", [.n "ADVSO", .n "FW", .n "SC"], .single⟩,
    ⟨"SINGLE", [.n "FW", .n "ADVSO", .n "SC"], .single⟩,
    ⟨"SINGLE", [.n "ADVSO", .n "FW", .n "ADVSO", .n "SC"], .single⟩ ]

def coordRules : List RuleS :=
  let pre1S (c : String) : List RuleS :=
    [ ⟨"F1S:" ++ c, [.n c], .item⟩, ⟨"F1S:" ++ c, [.n "E1S", .n c], .item⟩,
      ⟨"F1S:" ++ c, [.n "FW", .n c], .item⟩, ⟨"F1S:" ++ c, [.n "E1S", .n "FW", .n c], .item⟩,
      ⟨"F1S:" ++ c, [.n "FW", .n "E1S", .n c], .item⟩, ⟨"F1S:" ++ c, [.n "E1S", .n "FW", .n "E1S", .n c], .item⟩ ]
  let laterS (c : String) : List RuleS :=
    [ ⟨"LS:" ++ c, [.n c], .item⟩, ⟨"LS:" ++ c, [.n "ADVSO", .n c], .item⟩ ]
  let pre1O (c : String) : List RuleS :=
    [ ⟨"F1O:" ++ c, [.n "FW", .n c], .item⟩, ⟨"F1O:" ++ c, [.n "E1S", .n "FW", .n c], .item⟩,
      ⟨"F1O:" ++ c, [.n "FW", .n "ADVSO", .n c], .item⟩, ⟨"F1O:" ++ c, [.n "E1S", .n "FW", .n "ADVSO", .n c], .item⟩ ]
  let laterO (c : String) : List RuleS :=
    [ ⟨"LO:" ++ c, [.n "FW", .n c], .item⟩, ⟨"LO:" ++ c, [.n "ADVSO", .n "FW", .n c], .item⟩,
      ⟨"LO:" ++ c, [.n "FW", .n "ADVSO", .n c], .item⟩, ⟨"LO:" ++ c, [.n "ADVSO", .n "FW", .n "ADVSO", .n c], .item⟩ ]
  let coords (M : String) (sh : Bool) : List RuleS :=
    let F (c : String) : String := "F1" ++ M ++ ":" ++ c
    let L (c : String) : String := "L" ++ M ++ ":" ++ c
    let tB := "T" ++ M ++ ":B"
    let tR := "T" ++ M ++ ":R"
    let tF := "T" ++ M ++ ":F"
    [ ⟨"COORD", [.n (F "CB"), .n tB], .coord sh false⟩,
      ⟨tB, [.n "J", .n (L "CB")], .pass⟩, ⟨tB, [.t .comma, .n "J", .n (L "CB")], .pass⟩,
      ⟨tB, [.t .comma, .n (L "CB"), .n tB], .pass⟩,
      ⟨"COORD", [.n (F "CB"), .n tR], .coord sh true⟩,
      ⟨tR, [.n "J", .n (L "CR")], .pass⟩, ⟨tR, [.t .comma, .n "J", .n (L "CR")], .pass⟩,
      ⟨tR, [.t .comma, .n (L "CB"), .n tR], .pass⟩,
      ⟨"COORD", [.n (F "CO"), .n tF], .coord sh false⟩,
      ⟨tF, [.n "J", .n (L "CL")], .pass⟩, ⟨tF, [.n "J", .n (L "CB")], .pass⟩,
      ⟨tF, [.t .comma, .n "J", .n (L "CL")], .pass⟩, ⟨tF, [.t .comma, .n "J", .n (L "CB")], .pass⟩,
      ⟨tF, [.t .comma, .n (L "CO"), .n tF], .pass⟩ ]
  (["CB", "CO"].flatMap pre1S) ++ (["CB", "CO", "CL", "CR"].flatMap laterS) ++
  (["CB", "CO"].flatMap pre1O) ++ (["CB", "CO", "CL", "CR"].flatMap laterO) ++
  coords "S" true ++ coords "O" false

def frameRules (V : Vocab) (h : Nat) (f : Frame) : List RuleS :=
  let s := toString h
  let nm (x : String) : String := x ++ s
  let nmm (x m : String) : String := x ++ s ++ ":" ++ m
  let fillT : RSym := .t (.fill (fillExcl V f))
  let advT : RSym := .t (.adv V.adverbs)
  let argMs := f.argMarkers
  let splitMs := f.splitMarkers
  let plainMs := f.plainMarkers
  let modMs := f.mods
  let core : List RuleS :=
    [ ⟨nm "HD", kwSyms f.head, .head⟩,
      ⟨"CB", [.n (nm "HD")], .core⟩, ⟨"CO", [.n (nm "HD"), .n (nm "OWNM")], .core⟩,
      ⟨"CL", [.n (nm "HD"), .n (nm "LFM")], .core⟩, ⟨"CR", [.n (nm "HD"), .n (nm "RM")], .core⟩,
      ⟨"SC", [.n (nm "HD")], .core⟩, ⟨"SC", [.n (nm "HD"), .n (nm "SM")], .core⟩ ]
  let fillers : List RuleS :=
    [ ⟨nm "WR", [fillT], .pass⟩, ⟨nm "WR", [fillT, .n (nm "WR")], .pass⟩,
      ⟨nm "FL", [.n (nm "WR")], .part⟩, ⟨nm "FL", [.n "TOK"], .part⟩,
      ⟨nm "PL", [.n (nm "FL"), .n (nm "PT")], .pass⟩,
      ⟨nm "PT", [.n "J", .n (nm "FL")], .pass⟩, ⟨nm "PT", [.t .comma, .n "J", .n (nm "FL")], .pass⟩,
      ⟨nm "PT", [.t .comma, .n (nm "FL"), .n (nm "PT")], .pass⟩ ]
  let args : List RuleS := argMs.flatMap (fun m =>
    let sp := splitMs.contains m
    let lst := if sp then nmm "FS" m else nmm "FN" m
    [ ⟨nmm "AR" m, [.n ("MK:" ++ m), .n (nm "FL")], .arg m⟩,
      ⟨nmm "RL" m, [.n (nmm "AR" m), .n (nmm "RT" m)], .pass⟩,
      ⟨nmm "RT" m, [.n "J", .n (nmm "AR" m)], .pass⟩,
      ⟨nmm "RT" m, [.t .comma, .n "J", .n (nmm "AR" m)], .pass⟩,
      ⟨nmm "RT" m, [.t .comma, .n (nmm "AR" m), .n (nmm "RT" m)], .pass⟩,
      ⟨nmm "OL" m, [.n ("MK:" ++ m), .n (nm "PL")], .pass⟩,
      ⟨lst, [.n (nmm "RL" m)], .list m sp⟩,
      ⟨lst, [.n (nmm "OL" m)], .list m sp⟩ ])
  let obj : List RuleS :=
    if f.hasObject then
      ([⟨nm "O", [.n (nm "FL")], .arg ""⟩] : List RuleS) ++
      (if f.objSplit then ([⟨nm "OS", [.n (nm "PL")], .list "" true⟩] : List RuleS)
       else ([⟨nm "O", [.n (nm "PL")], .list "" false⟩] : List RuleS))
    else []
  let own : List RuleS :=
    argMs.map (fun m => (⟨nm "EE", [.n (nmm "AR" m)], .pass⟩ : RuleS)) ++
    plainMs.map (fun m => (⟨nm "EE", [.n (nmm "FN" m)], .pass⟩ : RuleS)) ++
    ([⟨nm "EE", [advT], .adv .own⟩] : List RuleS) ++
    modMs.map (fun m => (⟨nm "EE", [.n ("MK:" ++ m), .n (nm "FL")], .prep m .own⟩ : RuleS)) ++
    ([ ⟨nm "ER", [.n (nm "EE")], .pass⟩, ⟨nm "ER", [.n (nm "EE"), .n (nm "ER")], .pass⟩ ] : List RuleS) ++
    argMs.map (fun m => (⟨nm "NM", [.n (nmm "AR" m)], .pass⟩ : RuleS)) ++
    plainMs.map (fun m => (⟨nm "NM", [.n (nmm "FN" m)], .pass⟩ : RuleS)) ++
    ([ ⟨nm "ERN", [.n (nm "NM")], .pass⟩, ⟨nm "ERN", [.n (nm "EE"), .n (nm "ERN")], .pass⟩ ] : List RuleS) ++
    (if f.hasObject then ([⟨nm "OWNM", [.n (nm "O")], .pass⟩, ⟨nm "OWNM", [.n (nm "O"), .n (nm "ER")], .pass⟩] : List RuleS)
     else ([⟨nm "OWNM", [.n (nm "ER")], .pass⟩] : List RuleS))
  let edge (x : String) (tokOnly : Bool) : List RuleS :=
    ([⟨x, [advT], .adv .last⟩, ⟨x, [advT], .adv .all⟩] : List RuleS) ++
    modMs.flatMap (fun m =>
      let fl : RSym := if tokOnly then .n "TOK" else .n (nm "FL")
      ([⟨x, [.n ("MK:" ++ m), fl], .prep m .last⟩, ⟨x, [.n ("MK:" ++ m), fl], .prep m .all⟩] : List RuleS))
  let lfm : List RuleS :=
    if f.hasObject then
      [ ⟨nm "LFM", [.n (nm "O")], .pass⟩, ⟨nm "LFM", [.n (nm "O"), .n (nm "ERN")], .pass⟩,
        ⟨nm "LFM", [.n (nm "O"), .n (nm "TR")], .pass⟩, ⟨nm "LFM", [.n (nm "O"), .n (nm "ERN"), .n (nm "TR")], .pass⟩ ]
    else
      [ ⟨nm "LFM", [.n (nm "ERN")], .pass⟩, ⟨nm "LFM", [.n (nm "TR")], .pass⟩,
        ⟨nm "LFM", [.n (nm "ERN"), .n (nm "TR")], .pass⟩ ]
  let trs : List RuleS := [ ⟨nm "TR", [.n (nm "TE")], .pass⟩, ⟨nm "TR", [.n (nm "TE"), .n (nm "TR")], .pass⟩ ]
  let lastFull : List RuleS := edge (nm "TE") false ++ trs ++ lfm
  let rep : List RuleS := [ ⟨nm "REP", [.n (nm "REt")], .pass⟩, ⟨nm "REP", [.n (nm "RE"), .n (nm "REP")], .pass⟩ ]
  let rx : List RuleS :=
    argMs.map (fun m => (⟨nm "RX", [.n (nmm "AR" m)], .pass⟩ : RuleS)) ++
    plainMs.map (fun m => (⟨nm "RX", [.n (nmm "FN" m)], .pass⟩ : RuleS))
  let rr : List RuleS :=
    [ ⟨nm "RX", [.n (nm "RE")], .pass⟩,
      ⟨nm "RR", [.n (nm "RX")], .pass⟩, ⟨nm "RR", [.n (nm "RX"), .n (nm "RR")], .pass⟩ ]
  let rm : List RuleS :=
    if f.hasObject then
      [ ⟨nm "RM", [.n (nm "O")], .pass⟩, ⟨nm "RM", [.n (nm "O"), .n (nm "RR")], .pass⟩,
        ⟨nm "RM", [.n (nm "REP"), .n (nm "O")], .pass⟩, ⟨nm "RM", [.n (nm "REP"), .n (nm "O"), .n (nm "RR")], .pass⟩ ]
    else [ ⟨nm "RM", [.n (nm "RR")], .pass⟩ ]
  let rnr : List RuleS := edge (nm "RE") false ++ edge (nm "REt") true ++ rep ++ rx ++ rr ++ rm
  let spl : List RuleS :=
    splitMs.map (fun m => (⟨nm "SPL", [.n (nmm "FS" m)], .pass⟩ : RuleS)) ++
    ([ ⟨nm "SPL", [.n (nm "MG")], .pass⟩ ] : List RuleS)
  let px : List RuleS :=
    argMs.map (fun m => (⟨nm "PX", [.n (nmm "AR" m)], .pass⟩ : RuleS)) ++
    plainMs.map (fun m => (⟨nm "PX", [.n (nmm "FN" m)], .pass⟩ : RuleS)) ++
    edge (nm "PX") false
  let po : List RuleS := [ ⟨nm "PO", [.n (nm "PX")], .pass⟩, ⟨nm "PO", [.n (nm "PX"), .n (nm "PO")], .pass⟩ ]
  let smObj : List RuleS :=
    [ ⟨nm "SM", [.n (nm "OWNM")], .pass⟩, ⟨nm "SM", [.n (nm "OWNM"), .n (nm "SPL")], .pass⟩,
      ⟨nm "SM", [.n (nm "OWNM"), .n (nm "SPL"), .n (nm "PO")], .pass⟩ ]
  let smOS : List RuleS :=
    if f.objSplit then [ ⟨nm "SM", [.n (nm "OS")], .pass⟩, ⟨nm "SM", [.n (nm "OS"), .n (nm "PO")], .pass⟩ ] else []
  let smNo : List RuleS :=
    [ ⟨nm "SM", [.n (nm "ER")], .pass⟩, ⟨nm "SM", [.n (nm "ER"), .n (nm "SPL")], .pass⟩,
      ⟨nm "SM", [.n (nm "ER"), .n (nm "SPL"), .n (nm "PO")], .pass⟩,
      ⟨nm "SM", [.n (nm "SPL")], .pass⟩, ⟨nm "SM", [.n (nm "SPL"), .n (nm "PO")], .pass⟩ ]
  let single : List RuleS := spl ++ px ++ po ++ (if f.hasObject then smObj ++ smOS else smNo)
  let mel : List RuleS :=
    ([ ⟨nm "MEL", [advT], .modAdv⟩ ] : List RuleS) ++
    modMs.map (fun m => (⟨nm "MEL", [.n ("MK:" ++ m), .n (nm "FL")], .modPrep m⟩ : RuleS))
  let mgt : List RuleS :=
    [ ⟨nm "MGT", [.n "J", .n (nm "MEL")], .pass⟩, ⟨nm "MGT", [.t .comma, .n "J", .n (nm "MEL")], .pass⟩,
      ⟨nm "MGT", [.t .comma, .n (nm "MEL"), .n (nm "MGT")], .pass⟩,
      ⟨nm "MG", [.n (nm "MEL"), .n (nm "MGT")], .group⟩ ]
  let mg : List RuleS := mel ++ mgt
  core ++ fillers ++ args ++ obj ++ own ++ lastFull ++ rnr ++ single ++ mg

def schema (V : Vocab) : List RuleS :=
  globalRules V ++ singleRules ++ coordRules ++
    (List.range V.frames.length).flatMap (fun h => match V.frames[h]? with
      | some f => frameRules V h f
      | none => [])

def computeRanks (n : Nat) (rules : List (VE.Grammar.Rule Term)) : Array Nat :=
  (List.range (n + 1)).foldl (fun rk _ =>
    rules.foldl (fun acc R => match R.rhs with
      | .n B :: _ => acc.modify R.lhs (fun x => max x (acc.getD B 0 + 1))
      | _ => acc) rk) (Array.replicate n 0)

structure Built where
  rules : Array (VE.Grammar.Rule Term)
  kinds : Array Kind
  rank : Array Nat
  start : Nat

def build (V : Vocab) : Built :=
  let rs0 := schema V
  let defined := (rs0.map (·.lhs)).eraseDups
  let used := rs0.flatMap (fun r => r.rhs.filterMap (fun s => match s with | .n x => some x | .t _ => none))
  let missing := (used.filter (fun x => !defined.contains x)).eraseDups
  let rs := rs0 ++ missing.map (fun x => ({ lhs := x, rhs := [.t .never], kind := .pass } : RuleS))
  let names := defined ++ missing
  let rules : List (VE.Grammar.Rule Term) := rs.map (fun r =>
    { lhs := names.idxOf r.lhs,
      rhs := r.rhs.map (fun s => match s with
        | RSym.n x => VE.Grammar.Sym.n (names.idxOf x)
        | RSym.t a => VE.Grammar.Sym.t a),
      act := 0, tag := "" })
  { rules := rules.toArray, kinds := (rs.map (·.kind)).toArray, rank := computeRanks names.length rules,
    start := names.idxOf "S" }

def grammarOf (B : Built) : VE.Grammar.Grammar Term := { rules := B.rules, start := B.start, rank := B.rank }
def grammar (V : Vocab) : VE.Grammar.Grammar Term := grammarOf (build V)

/-! ### Meaning (5.3) -/

inductive Piece
  | w (s : String) | f (s : String) | slot (i : Nat) | fixed (i : Nat) | comma
  | part (p : Part) | elt (e : Elt) | mod (m : Modifier) | head (ws : List String) | fw (ws : List String)
  | padv (w : String) (att : Attach) | core (h : List String) (es : List Elt) | item (it : Item) | act (A : Act)

def leafPiece : Term → Tok → List Piece
  | .kw w, _ => [.w w]
  | .adv _, .word v => [.w v.toLower]
  | .fill _, .word v => [.f v]
  | .slot, .slot i => [.slot i]
  | .fixed, .fixed i => [.fixed i]
  | .comma, _ => [.comma]
  | _, _ => []

def joinOf? (s : String) : Option Join :=
  if s == "and" then some .and else if s == "or" then some .or else if s == "nor" then some .nor else none

def partOf? : List Piece → Option Part
  | [.part p] => some p
  | [.slot i] => some (.slot i)
  | [.fixed i] => some (.fixed i)
  | ps =>
    let ws := ps.filterMap (fun x => match x with | .f s => some s | _ => none)
    if !ws.isEmpty && ws.length == ps.length then some (.words ws) else none

def splitList (ps : List Piece) : Option Join × List (List Piece) :=
  let step := fun (acc : Option Join × List (List Piece) × List Piece) (p : Piece) =>
    match p with
    | .comma => (acc.1, acc.2.1 ++ [acc.2.2], [])
    | .w s => match joinOf? s with
      | some j => (some j, acc.2.1 ++ [acc.2.2], [])
      | none => (acc.1, acc.2.1, acc.2.2 ++ [p])
    | _ => (acc.1, acc.2.1, acc.2.2 ++ [p])
  let r := ps.foldl step (none, [], [])
  (r.1, (r.2.1 ++ [r.2.2]).filter (fun x => !x.isEmpty))

def memberPart? : List Piece → Option Part
  | [.part p] => some p
  | [.elt (.arg _ (.one p))] => some p
  | _ => none

def addMod (a : Atom) (md : Modifier) : Atom := { a with mods := a.mods ++ [md] }
def addArg (a : Atom) (m : String) (fl : Filler) : Atom := { a with args := a.args ++ [(m, fl)] }
def baseAtom (fw : List String) (h : List String) : Atom :=
  { toWord := fw.contains "to", beWord := fw.contains "be", head := h, args := [], mods := [] }
def ownElt (a : Atom) : Elt → Atom
  | .arg m fl => addArg a m fl
  | .adv w _ => addMod a (.adv w)
  | .prep m p _ => addMod a (.prep m p)
  | _ => a
def onLast (n : Nat) (g : Atom → Atom) (ps : List Atom) : List Atom :=
  ps.mapIdx (fun i a => if i + 1 == n then g a else a)
def joinAct (j : Join) (shared split : Bool) (ps : List Atom) : Act :=
  match j with
  | .and => .all shared split ps
  | .or => .any false split ps
  | .nor => .any true split ps
def isSplitElt : Elt → Bool
  | .split .. => true
  | .group .. => true
  | _ => false

def singleAct (it : Item) : Except String Act := do
  let base := it.advs.foldl (fun a x => addMod a (.adv x.1)) (baseAtom it.fw it.head)
  match it.elts.findIdx? isSplitElt with
  | none => pure (.one (it.elts.foldl ownElt base))
  | some k =>
    let pre := (it.elts.take k).foldl ownElt base
    let after := it.elts.drop (k + 1)
    let (j, sp, parts0) ← match it.elts[k]? with
      | some (.split m j ps) => pure (j, true, ps.map (fun p => addArg pre m (.one p)))
      | some (.group j ms) => pure (j, false, ms.map (fun md => addMod pre md))
      | _ => throw "InvalidInput: no split element"
    let n := parts0.length
    let parts := after.foldl (fun (ps : List Atom) e => match e with
      | .arg m fl => ps.map (fun a => addArg a m fl)
      | .adv w .last => onLast n (fun a => addMod a (.adv w)) ps
      | .adv w _ => ps.map (fun a => addMod a (.adv w))
      | .prep m p .last => onLast n (fun a => addMod a (.prep m p)) ps
      | .prep m p _ => ps.map (fun a => addMod a (.prep m p))
      | _ => ps) parts0
    pure (joinAct j true sp parts)

def coordAct (shared rnr : Bool) (j : Join) (its : List Item) : Act :=
  let n := its.length
  let fw1 := (its.head?.map (·.fw)).getD []
  let atoms0 := its.mapIdx (fun i it =>
    let fw := if shared && i != 0 then fw1 else it.fw
    let a0 := it.advs.foldl (fun a x => if x.2 == .own then addMod a (.adv x.1) else a) (baseAtom fw it.head)
    it.elts.foldl (fun a e => match e with
      | .arg m fl => if rnr && i + 1 == n then a else addArg a m fl
      | .adv w .own => addMod a (.adv w)
      | .prep m p .own => addMod a (.prep m p)
      | _ => a) a0)
  let firstAdvs := ((its.head?.map (·.advs)).getD []).filter (fun x => x.2 != .own)
  let atoms1 := firstAdvs.foldl (fun (ps : List Atom) x =>
    ps.mapIdx (fun i a => if x.2 == .all || i == 0 then addMod a (.adv x.1) else a)) atoms0
  let lastElts := (its.getLast?.map (·.elts)).getD []
  let atoms2 := lastElts.foldl (fun (ps : List Atom) e => match e with
    | .arg m fl => if rnr then ps.map (fun a => addArg a m fl) else ps
    | .adv w .last => onLast n (fun a => addMod a (.adv w)) ps
    | .adv w .all => ps.map (fun a => addMod a (.adv w))
    | .prep m p .last => onLast n (fun a => addMod a (.prep m p)) ps
    | .prep m p .all => ps.map (fun a => addMod a (.prep m p))
    | _ => ps) atoms1
  joinAct j shared false atoms2

def itemOf (cs : List Piece) : Except String Item :=
  match cs.getLast? with
  | some (.core h es) =>
    let pre := cs.dropLast
    let fw := pre.foldl (fun acc p => match p with | .fw ws => acc ++ ws | _ => acc) []
    let advs := pre.filterMap (fun p => match p with | .padv a att => some (a, att) | _ => none)
    .ok { fw := fw, advs := advs, head := h, elts := es }
  | _ => .error "item"

def applyKind (k : Kind) (cs : List Piece) : Except String (List Piece) :=
  match k with
  | .pass => .ok cs
  | .head => .ok [.head (cs.filterMap (fun x => match x with | .w s => some s | _ => none))]
  | .fw => .ok [.fw (cs.filterMap (fun x => match x with | .w s => some s | _ => none))]
  | .part => match partOf? cs with
    | some p => .ok [.part p]
    | none => .error "part"
  | .arg m => match partOf? (cs.drop (wordsOf m).length) with
    | some p => .ok [.elt (.arg m (.one p))]
    | none => .error "arg"
  | .list m sp =>
    let body := cs.dropWhile (fun x => match x with | .w s => (joinOf? s).isNone | _ => false)
    match splitList body with
    | (some j, ms) =>
      match ms.mapM memberPart? with
      | some ps =>
        if 2 ≤ ps.length then .ok [.elt (if sp then .split m j ps else .arg m (.joined j ps))] else .error "list"
      | none => .error "list"
    | (none, _) => .error "list"
  | .adv att => match cs with
    | [.w a] => .ok [.elt (.adv a att)]
    | _ => .error "adv"
  | .padv att => match cs with
    | [.w a] => .ok [.padv a att]
    | _ => .error "padv"
  | .prep m att => match partOf? (cs.drop (wordsOf m).length) with
    | some p => .ok [.elt (.prep m p att)]
    | none => .error "prep"
  | .modAdv => match cs with
    | [.w a] => .ok [.mod (.adv a)]
    | _ => .error "mod"
  | .modPrep m => match partOf? (cs.drop (wordsOf m).length) with
    | some p => .ok [.mod (.prep m p)]
    | none => .error "mod"
  | .group =>
    match splitList cs with
    | (some j, ms) =>
      match ms.mapM (fun x => match x with | [.mod md] => some md | _ => none) with
      | some mds => .ok [.elt (.group j mds)]
      | none => .error "group"
    | (none, _) => .error "group"
  | .core => match cs with
    | .head h :: rest =>
      match rest.mapM (fun x => match x with | .elt e => some e | _ => none) with
      | some es => .ok [.core h es]
      | none => .error "core"
    | _ => .error "core"
  | .item => match itemOf cs with
    | .ok it => .ok [.item it]
    | .error e => .error e
  | .single => match itemOf cs with
    | .ok it => match singleAct it with
      | .ok A => .ok [.act A]
      | .error e => .error e
    | .error e => .error e
  | .coord sh rnr =>
    let its := cs.filterMap (fun x => match x with | .item it => some it | _ => none)
    match (cs.filterMap (fun x => match x with | .w s => joinOf? s | _ => none)).head? with
    | some j => .ok [.act (coordAct sh rnr j its)]
    | none => .error "coord"
  | .start => match cs.filterMap (fun x => match x with | .act A => some A | _ => none) with
    | [A] => .ok [.act A]
    | _ => .error "start"

mutual
def piecesOf (B : Built) : VE.Grammar.Tree Tok → Except String (List Piece)
  | .leaf _ => .error "leaf"
  | .node r kids =>
    match B.rules[r]?, B.kinds[r]? with
    | some R, some k =>
      match piecesKids B R.rhs kids with
      | .ok cs => applyKind k cs
      | .error e => .error e
    | _, _ => .error "rule"
def piecesKids (B : Built) : List (VE.Grammar.Sym Term) → List (VE.Grammar.Tree Tok) → Except String (List Piece)
  | [], [] => .ok []
  | .t a :: syms, .leaf tok :: kids =>
    match piecesKids B syms kids with
    | .ok rest => .ok (leafPiece a tok ++ rest)
    | .error e => .error e
  | .n _ :: syms, k :: kids =>
    match piecesOf B k, piecesKids B syms kids with
    | .ok p, .ok rest => .ok (p ++ rest)
    | .error e, _ => .error e
    | _, .error e => .error e
  | _, _ => .error "shape"
end

def frameOf (V : Vocab) (h : List String) : Option Frame := V.frames.find? (fun f => f.head == h)

def atomOk (V : Vocab) (a : Atom) : Bool :=
  match frameOf V a.head with
  | none => false
  | some f =>
    (a.args.filter (fun x => x.1 == "")).length == (if f.hasObject then 1 else 0) &&
    a.args.all (fun x => f.markers.contains x.1) &&
    a.mods.all (fun md => match md with
      | .adv w => V.adverbs.contains w
      | .prep m _ => f.mods.contains m)

def actOk (V : Vocab) : Act → Bool
  | .one a => atomOk V a
  | .all _ _ ps => decide (2 ≤ ps.length) && ps.all (atomOk V)
  | .any _ _ ps => decide (2 ≤ ps.length) && ps.all (atomOk V)

def meaningWith (V : Vocab) (B : Built) : VE.Grammar.Meaning Tok Unit String Act := fun _ t =>
  match piecesOf B t with
  | .ok [.act A] => if actOk V A then .ok (A, false, ()) else .error "InvalidInput: a part of this act does not fit its frame"
  | .ok _ => .error "shape"
  | .error e => .error e
def meaning (V : Vocab) : VE.Grammar.Meaning Tok Unit String Act := meaningWith V (build V)

/-! ### Readings, reading, analysis (5.4) -/

def rawCap : Nat := 256
def stepBudget : Nat := 2100000
def maxReadings : Nat := 64

inductive Listing (α : Type) | ok (xs : List α) | limit

def firsts {α : Type} [DecidableEq α] : List α → List α
  | [] => []
  | x :: xs => x :: (firsts xs).filter (· ≠ x)

def listing {α : Type} [DecidableEq α] (N L : Nat) (parsed : Option (List (VE.Grammar.Tree Tok)))
    (μ : VE.Grammar.Tree Tok → Option α) : Listing α :=
  match parsed with
  | none => .limit
  | some ts => if N ≤ ts.length then .limit else
      let ms := firsts (ts.filterMap μ)
      if L < ms.length then .limit else .ok ms

def readings (V : Vocab) (N b : Nat) (ts : Array Tok) : Listing Act :=
  let B := build V
  listing N maxReadings (VE.Grammar.parse (grammarOf B) N b ts)
    (fun t => match meaningWith V B () t with | .ok (A, _, _) => some A | .error _ => none)

inductive ReadOutcome | ok (A : Act) | none | many (A B : Act) | limit

def read (V : Vocab) (N b : Nat) (ts : Array Tok) : ReadOutcome :=
  match readings V N b ts with
  | .limit => .limit
  | .ok [] => .none
  | .ok [A] => .ok A
  | .ok (A :: B :: _) => .many A B

def analyse (V : Vocab) (N b : Nat) (ts : Array Tok) : Option Atom :=
  match read V N b ts with
  | .ok (.one a) => some a
  | _ => none

/-! ### Rendering (5.5) -/

def joinWord : Join → String
  | .and => "and"
  | .or => "or"
  | .nor => "nor"
def Part.toks : Part → List Tok
  | .slot i => [.slot i]
  | .fixed i => [.fixed i]
  | .words ws => ws.map Tok.word
def listToks (j : Join) : List Part → List Tok
  | [] => []
  | [p] => p.toks
  | [p, q] => p.toks ++ [Tok.word (joinWord j)] ++ q.toks
  | p :: rest => p.toks ++ [Tok.comma] ++ listToks j rest
def Filler.toks : Filler → List Tok
  | .one p => p.toks
  | .joined j ps => listToks j ps
def Atom.normal (a : Atom) : List Tok :=
  [Tok.slot 0] ++ (if a.toWord then [Tok.word "to"] else []) ++ (if a.beWord then [Tok.word "be"] else []) ++
  a.mods.flatMap (fun md => match md with | .adv w => [Tok.word w] | _ => []) ++ a.head.map Tok.word ++
  (a.args.filter (fun x => x.1 == "")).flatMap (fun x => x.2.toks) ++
  (a.args.filter (fun x => x.1 != "")).flatMap (fun x => (wordsOf x.1).map Tok.word ++ x.2.toks) ++
  a.mods.flatMap (fun md => match md with | .prep m p => (wordsOf m).map Tok.word ++ p.toks | _ => [])
def Atom.canon (a : Atom) : Atom :=
  { a with args := a.args.filter (fun x => x.1 == "") ++ a.args.filter (fun x => x.1 != ""),
           mods := a.mods.filter (fun md => match md with | .adv _ => true | _ => false) ++
                   a.mods.filter (fun md => match md with | .prep .. => true | _ => false) }
def partOk (V : Vocab) (f : Frame) : Part → Bool
  | .words ws => !ws.isEmpty && ws.all (fun w => !(fillExcl V f).contains w.toLower)
  | _ => true
def normalOkIn (V : Vocab) (f : Frame) (a : Atom) : Bool :=
  a.args.all (fun x => match x.2 with
    | .one p => partOk V f p
    | .joined _ ps => decide (2 ≤ ps.length) && ps.all (partOk V f) && !f.split.contains x.1) &&
  a.mods.all (fun md => match md with
    | .adv _ => true
    | .prep _ p => partOk V f p)
def normalOk (V : Vocab) (a : Atom) : Bool :=
  atomOk V a && (match frameOf V a.head with
    | none => false
    | some f => normalOkIn V f a)

def tokStr (fx : List String) : Tok → String
  | .word w => w
  | .slot i => "{" ++ toString i ++ "}"
  | .fixed i => Lexical.normal (fx.getD i "")
  | .comma => ","
def tokText (fx : List String) (ts : List Tok) : String :=
  ts.foldl (fun acc t => match t with
    | .comma => acc ++ ","
    | _ => if acc.isEmpty then tokStr fx t else acc ++ " " ++ tokStr fx t) ""

/-! ### AP-2 theorems (5.6) -/

def Derived (V : Vocab) (ts : List Tok) (A : Act) : Prop :=
  ∃ d, VE.Grammar.Derives (grammar V) (.n (grammar V).start) ts d ∧ ∃ c, meaning V () d = .ok (A, c, ())

def grammar_wf_stmt : Prop := ∀ V : Vocab, framesOk V = true → (grammar V).wf = true
def read_unique_stmt : Prop :=
  ∀ (V : Vocab) (N b : Nat) (ts : Array Tok) (A : Act), framesOk V = true → read V N b ts = .ok A →
    Derived V ts.toList A ∧ ∀ d B c, VE.Grammar.Derives (grammar V) (.n (grammar V).start) ts.toList d →
      meaning V () d = .ok (B, c, ()) → B = A
def read_none_stmt : Prop :=
  ∀ (V : Vocab) (N b : Nat) (ts : Array Tok), framesOk V = true → read V N b ts = .none →
    ∀ A, ¬ Derived V ts.toList A
def read_many_stmt : Prop :=
  ∀ (V : Vocab) (N b : Nat) (ts : Array Tok) (A B : Act), framesOk V = true → read V N b ts = .many A B →
    A ≠ B ∧ Derived V ts.toList A ∧ Derived V ts.toList B
def readings_exact_stmt : Prop :=
  ∀ (V : Vocab) (N b : Nat) (ts : Array Tok) (As : List Act), framesOk V = true → readings V N b ts = .ok As →
    ∀ A, A ∈ As ↔ Derived V ts.toList A
def readings_nodup_stmt : Prop :=
  ∀ (V : Vocab) (N b : Nat) (ts : Array Tok) (As : List Act), readings V N b ts = .ok As → As.Nodup
def readings_limit_stmt : Prop :=
  ∀ (V : Vocab) (N b : Nat) (ts : Array Tok),
    readings V N b ts = .limit ↔
      (VE.Grammar.parse (grammar V) N b ts = none ∨
       ∃ trees, VE.Grammar.parse (grammar V) N b ts = some trees ∧
         (N ≤ trees.length ∨ maxReadings < (firsts (trees.filterMap (fun t => match meaning V () t with
            | .ok (A, _, _) => some A | .error _ => none))).length))
def listing_ok_stmt : Prop :=
  ∀ (α : Type) [DecidableEq α] (N L : Nat) (parsed : Option (List (VE.Grammar.Tree Tok)))
    (μ : VE.Grammar.Tree Tok → Option α) (xs : List α),
    listing N L parsed μ = .ok xs ↔ ∃ ts, parsed = some ts ∧ ts.length < N ∧ xs = firsts (ts.filterMap μ) ∧ xs.length ≤ L
def read_normal_stmt : Prop :=
  ∀ (V : Vocab) (a : Atom), framesOk V = true → normalOk V a = true →
    ∃ N0 b0, ∀ N b, N0 ≤ N → b0 ≤ b → read V N b a.normal.toArray = .ok (.one a.canon)
def analyse_one_stmt : Prop :=
  ∀ (V : Vocab) (N b : Nat) (ts : Array Tok) (a : Atom), analyse V N b ts = some a → read V N b ts = .ok (.one a)

/-! ## AP-3: the table and elaboration (spec 6) -/

inductive Simple | atom (a : Atom) | whole (A : Act)
  deriving DecidableEq, Repr

inductive Op | must | needNot | may | mustNot | right
  deriving DecidableEq, Repr

def opOf (r : VE.Norms.Regulated) (sign : Bool) : Option Op :=
  match r.role, sign with
  | .obligation, true => some .must
  | .obligation, false => some .needNot
  | .permission, true => some .may
  | .permission, false => some .mustNot
  | .plain, true => some .right
  | .plain, false => none

def freeTable : Act → List (List Simple)
  | .one a => [[.atom a]]
  | .all false _ ps => [ps.map Simple.atom]
  | .all true true ps => [ps.map Simple.atom]
  | .all true false ps => [ps.map Simple.atom, [.whole (.all true false ps)]]
  | .any true _ _ => []
  | .any false true ps => [ps.map Simple.atom]
  | .any false false ps => [ps.map Simple.atom, [.whole (.any false false ps)]]

def table : Op → Act → List (List Simple)
  | _, .one a => [[.atom a]]
  | .needNot, _ => []
  | .must, .all _ _ ps => [ps.map Simple.atom]
  | .must, .any nor sp ps => if nor || sp then [] else [[.whole (.any nor sp ps)]]
  | .mustNot, .any _ _ ps => [ps.map Simple.atom]
  | .mustNot, .all s sp ps => if sp then [ps.map Simple.atom] else [ps.map Simple.atom, [.whole (.all s sp ps)]]
  | .may, A => freeTable A
  | .right, A => freeTable A

def table_one_stmt : Prop := ∀ (op : Op) (a : Atom), table op (.one a) = [[.atom a]]
def table_must_all_stmt : Prop := ∀ (s sp : Bool) (ps : List Atom), table .must (.all s sp ps) = [ps.map Simple.atom]
def table_must_any_stmt : Prop := ∀ ps : List Atom, table .must (.any false false ps) = [[.whole (.any false false ps)]]
def table_must_any_refused_stmt : Prop :=
  ∀ (n sp : Bool) (ps : List Atom), (n = true ∨ sp = true) → table .must (.any n sp ps) = []
def table_mustNot_any_stmt : Prop := ∀ (n sp : Bool) (ps : List Atom), table .mustNot (.any n sp ps) = [ps.map Simple.atom]
def table_mustNot_all_stmt : Prop :=
  ∀ (s : Bool) (ps : List Atom), table .mustNot (.all s false ps) = [ps.map Simple.atom, [.whole (.all s false ps)]]
def table_mustNot_all_split_stmt : Prop :=
  ∀ (s : Bool) (ps : List Atom), table .mustNot (.all s true ps) = [ps.map Simple.atom]
def table_free_all_own_stmt : Prop :=
  ∀ (op : Op), (op = .may ∨ op = .right) → ∀ (sp : Bool) (ps : List Atom), table op (.all false sp ps) = [ps.map Simple.atom]
def table_free_all_shared_stmt : Prop :=
  ∀ (op : Op), (op = .may ∨ op = .right) → ∀ ps : List Atom,
    table op (.all true false ps) = [ps.map Simple.atom, [.whole (.all true false ps)]]
def table_free_all_split_stmt : Prop :=
  ∀ (op : Op), (op = .may ∨ op = .right) → ∀ ps : List Atom, table op (.all true true ps) = [ps.map Simple.atom]
def table_free_any_stmt : Prop :=
  ∀ (op : Op), (op = .may ∨ op = .right) → ∀ ps : List Atom,
    table op (.any false false ps) = [ps.map Simple.atom, [.whole (.any false false ps)]]
def table_free_any_split_stmt : Prop :=
  ∀ (op : Op), (op = .may ∨ op = .right) → ∀ ps : List Atom, table op (.any false true ps) = [ps.map Simple.atom]
def table_free_nor_stmt : Prop :=
  ∀ (op : Op), (op = .may ∨ op = .right) → ∀ (sp : Bool) (ps : List Atom), table op (.any true sp ps) = []
def table_needNot_stmt : Prop := ∀ A : Act, (∀ a, A ≠ .one a) → table .needNot A = []

def modalText : Op → Option Lexical.Form → String
  | .must, _ => "must"
  | .needNot, _ => "need not"
  | .may, _ => "may"
  | .mustNot, _ => "must not"
  | .right, some f => f.text
  | .right, none => Lexical.Form.right.text
def sentence (fx : List String) (op : Op) (f : Option Lexical.Form) (a : Atom) : String :=
  "{0} " ++ modalText op f ++ " " ++ (tokText fx a.normal).drop 4
def paraphrase (fx : List String) (phrase : String) (op : Op) (f : Option Lexical.Form) : List Simple → String
  | [.atom a] => sentence fx op f a ++ "."
  | [.whole (.all ..)] => "{0} " ++ modalText op f ++ " " ++ (Lexical.normal phrase).drop 4 ++
      ", as one act done together (not each on its own)."
  | [.whole _] => "{0} " ++ modalText op f ++ " " ++ (Lexical.normal phrase).drop 4 ++
      ", as one act done in any one of these ways (not each way on its own)."
  | xs =>
    let ss := xs.filterMap (fun x => match x with | .atom a => some (sentence fx op f a) | _ => none)
    match ss with
    | [s1, s2] => s1 ++ ", and " ++ s2 ++ "."
    | _ => "; ".intercalate ss.dropLast ++ "; and " ++ (ss.getLast?.getD "") ++ "."

/-! ### Elaboration (6.3) -/

structure ActsDoc where
  U : VE.NormDefaults.UDoc
  V : Vocab
  fixed : List String
  acts : List (String × Act)

structure SplitMap where
  preds : List (String × String × Nat)
  rules : List (String × String × Nat)
  deriving DecidableEq, Repr

def partPred (p : String) (i : Nat) : String := p ++ "__" ++ toString i
def partRule (n : String) (i : Nat) : String := n ++ "-a" ++ toString i

def dualOf (T : VE.Norms.Tree) (p : String) : Option String :=
  match T.regulated.find? (fun r => r.name == p) with
  | some r =>
    match r.role, r.permission with
    | .obligation, some m => some m
    | .permission, _ => (T.regulated.find? (fun o => o.role == .obligation && o.permission == some p)).map (·.name)
    | _, _ => none
  | none => none

def readingOf (D : ActsDoc) (p : String) (A : Act) : Except String (List Simple) :=
  match A with
  | .one a => .ok [.atom a]
  | _ => do
    let T := D.U.D.T
    let names := p :: (dualOf T p).toList
    let rules := T.nodes.filter (fun N => names.contains N.pred)
    if rules.isEmpty then throw s!"InvalidInput: the joined act of {p} has no rule to read it by"
    let rs ← rules.mapM (fun N => do
      let some r := T.regulated.find? (fun r => r.name == N.pred)
        | throw s!"UnknownSymbol: regulated predicate {N.pred}"
      let some op := opOf r N.sign
        | throw s!"InvalidInput: rule {N.name} has no modal word for a joined act"
      match table op A with
      | [R] => pure R
      | [] => throw s!"InvalidInput: rule {N.name} has no reading of its act; rewrite it"
      | _ => throw s!"InvalidInput: rule {N.name} has more than one reading")
    match rs with
    | R :: rest =>
      if rest.all (fun x => x == R) then pure R
      else throw s!"InvalidInput: the rules on {p} and its dual read its act differently; write the parts as separate predicates"
    | [] => throw s!"InvalidInput: the joined act of {p} has no rule to read it by"

def mentions (ps : List String) (φ : VE.Formula) : Bool := (VE.Norms.preds φ).any (fun q => ps.contains q)

/-- The source predicate of a generated part name. -/
def partSource (M : SplitMap) (n : String) : Option String := (M.preds.find? (fun y => y.1 == n)).map (fun y => y.2.1)
/-- The elaborated environment's predicates: a part has its source's sorts; a split source is undeclared. -/
def predsAfter (E : VE.Environment) (M : SplitMap) (split : List String) (n : String) : Option (List String) :=
  match partSource M n with
  | some p => E.predicates p
  | none => if split.contains n then none else E.predicates n

def elaborateMap (D : ActsDoc) : Except String (VE.NormDefaults.UDoc × SplitMap) := do
  let T := D.U.D.T
  let mut splits : List (String × List Atom) := []
  for x in D.acts do
    let R ← readingOf D x.1 x.2
    let atoms := R.filterMap (fun s => match s with | .atom a => some a | .whole _ => none)
    if 2 ≤ atoms.length && atoms.length == R.length then
      splits := splits ++ [(x.1, atoms)]
  let split := splits.map (·.1)
  for N in T.nodes do
    if (N.guard :: N.carveOuts).any (mentions split) then
      throw s!"InvalidInput: rule {N.name} names a predicate that is split into parts; name one of its parts"
  for d in T.definitions do
    if mentions split d.body then
      throw s!"InvalidInput: definition {d.name} names a predicate that is split into parts; name one of its parts"
  let atomsOf := fun (p : String) => ((splits.find? (fun y => y.1 == p)).map (·.2)).getD []
  let regs := T.regulated.flatMap (fun r =>
    if split.contains r.name then
      (List.range (atomsOf r.name).length).map (fun i =>
        { r with name := partPred r.name (i + 1),
                 act := some (tokText D.fixed ((atomsOf r.name).getD i emptyAtom).normal),
                 permission := r.permission.map (fun m => partPred m (i + 1)) })
    else [r])
  let nodes := T.nodes.flatMap (fun N =>
    if split.contains N.pred then
      (List.range (atomsOf N.pred).length).map (fun i =>
        { N with name := partRule N.name (i + 1), pred := partPred N.pred (i + 1),
                 over := N.over.map (fun m => partRule m (i + 1)) })
    else [N])
  let M : SplitMap :=
    { preds := splits.flatMap (fun y => (List.range y.2.length).map (fun i => (partPred y.1 (i + 1), y.1, i + 1))),
      rules := T.nodes.flatMap (fun N => if split.contains N.pred then
        (List.range (atomsOf N.pred).length).map (fun i => (partRule N.name (i + 1), N.name, i + 1)) else []) }
  for q in M.preds do
    if T.regulated.any (fun r => r.name == q.1) || (D.U.D.E.predicates q.1).isSome then
      throw s!"InvalidInput: the part name {q.1} is already declared"
    if q.1.utf8ByteSize > 64 then throw s!"ResourceLimit: the part name {q.1} is over 64 bytes"
  for q in M.rules do
    if T.nodes.any (fun N => N.name == q.1) then throw s!"InvalidInput: the part rule name {q.1} is already used"
    unless VE.Norms.ruleName q.1 do
      throw s!"ResourceLimit: the part rule name {q.1} is not a rule name of at most 64 bytes"
  let E := D.U.D.E
  let E' : VE.Environment := { E with predicates := predsAfter E M split }
  let U' : VE.NormDefaults.UDoc :=
    { D := { E := E', lits := D.U.D.lits, T := { T with regulated := regs, nodes := nodes } },
      unspec := D.U.unspec.flatMap (fun p => if split.contains p then
        (List.range (atomsOf p).length).map (fun i => partPred p (i + 1)) else [p]) }
  unless VE.NormDefaults.WellFormedU U' do
    match VE.Norms.validate U'.D with
    | .error e => throw e
    | .ok () => throw "InvalidInput: the elaborated document is not well formed"
  pure (U', M)

def elaborate (D : ActsDoc) : Except String VE.NormDefaults.UDoc := (elaborateMap D).map (·.1)

def checkAct (fx : List String) (V : Vocab) (name : String) (arity : Nat) (raw : Lean.Json) :
    Except String (String × Option Act) :=
  match Lexical.check fx name arity raw with
  | .ok a => .ok (a, none)
  | .error e =>
    if !(e.startsWith s!"InvalidInput: act phrase for {name} joins acts" ||
         e.startsWith s!"InvalidInput: act phrase for {name} has a comma outside") then .error e
    else
      let act := Lexical.normal ((raw.getStr?).toOption.getD "")
      match Lexical.lex fx act with
      | .error e2 => .error e2
      | .ok ts =>
        if ts.any (fun t => match t with | .word w => w.contains '{' | _ => false) then
          .error s!"InvalidInput: act phrase for {name} has a slot joined to a word"
        else match read V rawCap stepBudget ts.toArray with
          | .ok A => .ok (act, some A)
          | .none => .error s!"InvalidInput: act phrase for {name} has no reading under the declared frames"
          | .many _ _ => .error s!"InvalidInput: act phrase for {name} has more than one reading"
          | .limit => .error s!"ResourceLimit: act phrase for {name} has too many readings to list; split the sentence"

def checkAct_lexical_stmt : Prop :=
  ∀ (fx : List String) (V : Vocab) (name : String) (k : Nat) (raw : Lean.Json) (a : String),
    Lexical.check fx name k raw = .ok a → checkAct fx V name k raw = .ok (a, none)
def checkAct_joined_stmt : Prop :=
  ∀ (fx : List String) (V : Vocab) (name : String) (k : Nat) (raw : Lean.Json) (a : String) (A : Act),
    checkAct fx V name k raw = .ok (a, some A) → ∃ ts, Lexical.lex fx a = .ok ts ∧ read V rawCap stepBudget ts.toArray = .ok A

/-! ### AP-3 theorems (6.6) -/

universe u

def readAs (p q : String) (S : VE.Structure.{u}) : VE.Structure.{u} :=
  { S with relation := fun r vs => if r = p then S.relation q vs else S.relation r vs }

def partNames (D : ActsDoc) (p : String) : List String :=
  match List.lookup p D.acts with
  | some A => match readingOf D p A with
    | .ok R => if 2 ≤ R.length then (List.range R.length).map (fun i => partPred p (i + 1)) else [p]
    | .error _ => [p]
  | none => [p]

def IntendedActs (D : ActsDoc) (S : VE.Structure.{u}) : Prop :=
  ∀ r ∈ D.U.D.T.regulated, ∀ q ∈ partNames D r.name, VE.Norms.IntendedAt D.U.D.T r (readAs r.name q S)

def elaborateMap_fst_stmt : Prop := ∀ D : ActsDoc, (elaborateMap D).map (·.1) = elaborate D
def splitMap_exact_stmt : Prop :=
  ∀ (D : ActsDoc) (U' : VE.NormDefaults.UDoc) (M : SplitMap), elaborateMap D = .ok (U', M) →
    (∀ q, (q ∈ U'.D.T.regulated.map (·.name) ∧ q ∉ D.U.D.T.regulated.map (·.name)) ↔ ∃ p i, (q, p, i) ∈ M.preds) ∧
    (∀ n, (n ∈ U'.D.T.nodes.map (·.name) ∧ n ∉ D.U.D.T.nodes.map (·.name)) ↔ ∃ m i, (n, m, i) ∈ M.rules) ∧
    (∀ q p i, (q, p, i) ∈ M.preds →
      q = partPred p i ∧ p ∈ D.U.D.T.regulated.map (·.name) ∧ p ∉ U'.D.T.regulated.map (·.name) ∧ 1 ≤ i) ∧
    (∀ n m i, (n, m, i) ∈ M.rules →
      n = partRule m i ∧ m ∈ D.U.D.T.nodes.map (·.name) ∧ m ∉ U'.D.T.nodes.map (·.name) ∧ 1 ≤ i) ∧
    (∀ q p i j, (q, p, i) ∈ M.preds → 1 ≤ j → j ≤ i → ∃ q', (q', p, j) ∈ M.preds) ∧
    (M.preds.map (·.1)).Nodup ∧ (M.rules.map (·.1)).Nodup
def elaborate_identity_stmt : Prop :=
  ∀ D : ActsDoc, (∀ p A, (p, A) ∈ D.acts → ∃ a, A = .one a) → VE.NormDefaults.WellFormedU D.U = true →
    elaborate D = .ok D.U
def elaborate_wellFormed_stmt : Prop :=
  ∀ (D : ActsDoc) (U' : VE.NormDefaults.UDoc), elaborate D = .ok U' → VE.NormDefaults.WellFormedU U' = true
def elaborate_one_reading_stmt : Prop :=
  ∀ (D : ActsDoc) (U' : VE.NormDefaults.UDoc), elaborate D = .ok U' →
    ∀ p A, (p, A) ∈ D.acts → (∃ a, A = .one a) ∨ ∃ R, readingOf D p A = .ok R ∧
      ∀ N ∈ D.U.D.T.nodes, (N.pred = p ∨ some N.pred = dualOf D.U.D.T p) →
        ∃ r op, D.U.D.T.regulated.find? (fun r => r.name == N.pred) = some r ∧ opOf r N.sign = some op ∧ table op A = [R]
def elaborate_unspec_stmt : Prop :=
  ∀ (D : ActsDoc) (U' : VE.NormDefaults.UDoc), elaborate D = .ok U' → U'.unspec = D.U.unspec.flatMap (partNames D)
def elaborate_faithful_stmt : Prop :=
  ∀ (D : ActsDoc) (U' : VE.NormDefaults.UDoc), elaborate D = .ok U' →
    ∀ S : VE.Structure.{u}, VE.Norms.holdsCatala U'.D.T S ↔ IntendedActs D S

/-! ## AP-4: readings from derivations, exact sets (spec 7) -/

def attachOf : Kind → Option Attach
  | .adv a => some a
  | .padv a => some a
  | .prep _ a => some a
  | _ => none
def edgeLhs (x : String) : Attach → Bool
  | .own => true
  | .first => x == "E1X"
  | .last => ["TE", "RE", "PX"].any (fun p => x.startsWith p)
  | .all => x == "E1X" || ["TE", "RE", "PX"].any (fun p => x.startsWith p)
def modifier_edges_stmt : Prop :=
  ∀ V : Vocab, ∀ r ∈ schema V, ∀ a, attachOf r.kind = some a → edgeLhs r.lhs a = true

def phraseReadings (V : Vocab) (op : Op) (N b : Nat) (ts : Array Tok) : Listing (List Simple) :=
  match readings V N b ts with
  | .limit => .limit
  | .ok As =>
    let Rs := firsts (As.flatMap (table op))
    if maxReadings < Rs.length then .limit else .ok Rs

def phraseReadings_exact_stmt : Prop :=
  ∀ (V : Vocab) (op : Op) (N b : Nat) (ts : Array Tok) (Rs : List (List Simple)), framesOk V = true →
    phraseReadings V op N b ts = .ok Rs → ∀ R, R ∈ Rs ↔ ∃ A, Derived V ts.toList A ∧ R ∈ table op A

structure Source where
  phrase : String
  role : VE.Norms.Role
  sign : Bool
  form : Option Lexical.Form
  template : VE.Norms.Node
  allow : Bool
  units : List String
  sets : List String

abbrev View := String × VE.Norms.Role × Bool × VE.Formula × List VE.Formula × List String × Bool

def ruleView (D : VE.Readings.Doc) (N : VE.SoftNorms.SoftNode) : Option View :=
  (D.frame.soft.T.regulated.find? (fun r => r.name == N.pred)).bind (fun r =>
    r.act.map (fun a => (a, r.role, N.sign, N.guard, N.carveOuts, N.over, r.allowByDefault)))

def Simple.text (fx : List String) (phrase : String) : Simple → String
  | .atom a => tokText fx a.normal
  | .whole _ => Lexical.normal phrase

def expected (fx : List String) (s : Source) (x : Simple) : View :=
  (x.text fx s.phrase, s.role, s.sign, s.template.guard, s.template.carveOuts, s.template.over, s.allow)

def choicesOn (D : VE.Readings.Doc) (sets : List String) : List (List (String × Nat)) :=
  firsts ((VE.Readings.choices D).map (fun c => c.filter (fun x => sets.contains x.1)))

def choiceRules (D : VE.Readings.Doc) (s : Source) (c : List (String × Nat)) : List VE.SoftNorms.SoftNode :=
  D.items.filterMap (fun it => match it with
    | .fixed u (.norm N) _ => if s.units.contains u then some N else none
    | .set R =>
      if s.sets.contains R.id then
        match (c.find? (fun x => x.1 == R.id)).bind (fun x => R.candidates[x.2]?) with
        | some cand => match cand.content with
          | some (.norm N) => some N
          | _ => none
        | none => none
      else none
    | _ => none)

def opOfSource (s : Source) : Option Op := opOf ⟨"", [], s.allow, s.role, none, none⟩ s.sign

def sourceCheck (D : VE.Readings.Doc) (V : Vocab) (fx : List String) (N b : Nat) (s : Source) : Except String Unit := do
  let ts ← Lexical.lex fx s.phrase
  let some op := opOfSource s | throw "InvalidInput: the source's role and sign have no modal word"
  let Rs ← match phraseReadings V op N b ts.toArray with
    | .ok Rs => pure Rs
    | .limit => throw "ResourceLimit: the source phrase has too many readings to list; split the sentence"
  let views := (choicesOn D s.sets).map (fun c => (choiceRules D s c).map (ruleView D))
  let exp := Rs.map (fun R => R.map (fun x => some (expected fx s x)))
  if views.length != exp.length then
    throw s!"InvalidInput: the reading sets give {views.length} choices for a phrase with {exp.length} readings"
  for e in exp do
    unless views.contains e do throw "InvalidInput: a reading of the source phrase has no choice"
  for v in views do
    unless exp.contains v do
      throw "InvalidInput: a choice is not a reading of the source phrase, or changes the source rule's modal, guard, exceptions, precedence or completion"
  unless views.all (fun v => views.count v == 1) do throw "InvalidInput: two choices give the same reading"
  pure ()

def SourceExact (D : VE.Readings.Doc) (V : Vocab) (fx : List String) (N b : Nat) (s : Source) : Prop :=
  ∃ ts op Rs, Lexical.lex fx s.phrase = .ok ts ∧ opOfSource s = some op ∧
    phraseReadings V op N b ts.toArray = .ok Rs ∧
    (∀ R, R ∈ Rs ↔ ∃ A, Derived V ts A ∧ R ∈ table op A) ∧
    ((choicesOn D s.sets).map (fun c => (choiceRules D s c).map (ruleView D))).Nodup ∧
    List.Perm ((choicesOn D s.sets).map (fun c => (choiceRules D s c).map (ruleView D)))
      (Rs.map (fun R => R.map (fun x => some (expected fx s x))))

def sourceCheck_exact_stmt : Prop :=
  ∀ (D : VE.Readings.Doc) (V : Vocab) (fx : List String) (N b : Nat) (s : Source), framesOk V = true →
    sourceCheck D V fx N b s = .ok () → SourceExact D V fx N b s
def sourceCheck_complete_stmt : Prop :=
  ∀ (D : VE.Readings.Doc) (V : Vocab) (fx : List String) (N b : Nat) (s : Source), framesOk V = true →
    SourceExact D V fx N b s → sourceCheck D V fx N b s = .ok ()

/-- The plan's `atomSituation`, as a signature only (no new theorem: `separates_separated` covers it). -/
def atomSituation_sig : Type := VE.Readings.Doc → String → Nat → Nat → VE.Readings.Situation Nat

/-! ## AP-5: specialisation (spec 8) -/

structure Restrictive where
  markers : List String
  adverbs : List String
  deriving DecidableEq, Repr

def Modifier.restrictive (ρ : Restrictive) : Modifier → Bool
  | .adv w => ρ.adverbs.contains w
  | .prep m _ => ρ.markers.contains m

def specialises (ρ : Restrictive) (a b : Atom) : Bool :=
  a.toWord == b.toWord && a.beWord == b.beWord && a.head == b.head &&
  b.args.all (fun x => a.args.contains x) && b.mods.all (fun x => a.mods.contains x) &&
  (a.args.filter (fun x => !b.args.contains x)).all (fun x => ρ.markers.contains x.1) &&
  (a.mods.filter (fun x => !b.mods.contains x)).all (Modifier.restrictive ρ)

def specPremises (E : VE.Norms.Doc) (ρ : Restrictive) (acts : List (String × Atom)) : List VE.Formula :=
  acts.flatMap (fun x => acts.filterMap (fun y =>
    match E.T.regulated.find? (fun r => r.name == x.1), E.T.regulated.find? (fun r => r.name == y.1) with
    | some rp, some rq =>
      if x.1 != y.1 && rp.role == rq.role && rp.role != .plain && rp.sorts == rq.sorts && x.2 != y.2 &&
          specialises ρ x.2 y.2
      then some (VE.Norms.bindAll rp.sorts (.implies (VE.Norms.atom x.1 rp.sorts) (VE.Norms.atom y.1 rq.sorts)))
      else none
    | _, _ => none))

def specialises_refl_stmt : Prop := ∀ (ρ : Restrictive) (a : Atom), specialises ρ a a = true
def specialises_trans_stmt : Prop :=
  ∀ (ρ : Restrictive) (a b c : Atom), specialises ρ a b = true → specialises ρ b c = true → specialises ρ a c = true
def specPremises_typed_stmt : Prop :=
  ∀ (E : VE.Norms.Doc) (ρ : Restrictive) (acts : List (String × Atom)), VE.Norms.WellFormed E = true →
    ∀ φ ∈ specPremises E ρ acts, φ.check E.E [] = true
def specPremises_plain_stmt : Prop :=
  ∀ (E : VE.Norms.Doc) (ρ : Restrictive) (acts : List (String × Atom)),
    ∀ r ∈ E.T.regulated, r.role = .plain → ∀ φ ∈ specPremises E ρ acts, r.name ∉ VE.Norms.preds φ

/-! ## Fixtures (spec section 11) -/

namespace Fix
open VE.Acts.Lexical (check lex decodeFixed)

def okS (e : Except String String) : Option String := e.toOption
def errS (e : Except String String) : Option String := match e with
  | .error m => some m
  | .ok _ => none
def errFixed (fx : List String) : Option String := match decodeFixed fx with
  | .error m => some m
  | .ok _ => none
def nToks (fx : List String) (s : String) : Option Nat := (lex fx s).toOption.map List.length

/-! ### 11.1 AP-1 -/

def a1 := "{0} in full equality to a fair and public hearing by an independent and impartial tribunal in {1}"
def fx1 := ["a fair and public hearing by an independent and impartial tribunal"]
#guard a1.utf8ByteSize == 97
#guard (fx1.getD 0 "").utf8ByteSize == 66
#guard okS (check fx1 "p" 2 (.str a1)) == some a1
#guard nToks fx1 a1 == some 8
#guard Lexical.wording .entitled a1 ==
  "{0} is entitled in full equality to a fair and public hearing by an independent and impartial tribunal in {1}"
#guard (Lexical.wording .entitled a1).utf8ByteSize == 109

def a2 := "{0} to equal pay for equal work without any discrimination"
def fx2 := ["equal pay for equal work"]
#guard a2.utf8ByteSize == 58
#guard okS (check fx2 "p" 1 (.str a2)) == some a2
#guard nToks fx2 a2 == some 6
#guard Lexical.wording .right a2 == "{0} has the right to equal pay for equal work without any discrimination"
#guard (Lexical.wording .right a2).utf8ByteSize == 72

def a3 := "{0} to the protection of the moral and material interests resulting from {1}"
def fx3 := ["the moral and material interests"]
#guard a3.utf8ByteSize == 76
#guard okS (check fx3 "p" 2 (.str a3)) == some a3
#guard nToks fx3 a3 == some 9

def a4 := "{0} to seek as well as enjoy in other countries asylum from persecution"
#guard a4.utf8ByteSize == 71
#guard okS (VE.Norms.Wire.canonicalAct "p" 1 (.str a4)) == some a4
#guard okS (check fx1 "p" 1 (.str a4)) == some a4

def a5 := "{0} to seek and to enjoy in other countries asylum from persecution"
#guard errS (check [] "p" 1 (.str a5)) == some "InvalidInput: act phrase for p joins acts with 'and' outside a fixed phrase"

def a6 := "{0} be subjected to torture or to cruel, inhuman or degrading treatment or punishment"
def fx6 := ["cruel, inhuman or degrading treatment or punishment"]
#guard a6.utf8ByteSize == 85
#guard (fx6.getD 0 "").utf8ByteSize == 51
#guard errS (check fx6 "p" 1 (.str a6)) == some "InvalidInput: act phrase for p joins acts with 'or' outside a fixed phrase"

def a7 := "{0} be held by secret vote or by equivalent free voting procedures"
def fx7 := ["equivalent free voting procedures"]
#guard a7.utf8ByteSize == 66
#guard errS (check fx7 "p" 1 (.str a7)) == some "InvalidInput: act phrase for p joins acts with 'or' outside a fixed phrase"

def a13 := "{0} actively deceive {1} about the existence of a system prompt or its content"
def fx13 := ["the existence of a system prompt or its content"]
#guard a13.utf8ByteSize == 78
#guard (fx13.getD 0 "").utf8ByteSize == 47
#guard okS (check fx13 "p" 2 (.str a13)) == some a13

def a15 := "{0} take place"
#guard a15.utf8ByteSize == 14
#guard okS (check [] "p" 1 (.str a15)) == some a15

def a16 := "{0} to be presumed innocent until proved guilty according to law in a public trial at which they have had all the guarantees necessary for their defence"
def fx16 := ["a public trial at which they have had all the guarantees necessary for their defence"]
#guard a16.utf8ByteSize == 152
#guard (fx16.getD 0 "").utf8ByteSize == 84
#guard okS (check fx16 "p" 1 (.str a16)) == some a16

def a17 := "{0} take part if {1} is open"
#guard a17.utf8ByteSize == 28
#guard errS (check [] "p" 2 (.str a17)) ==
  some "InvalidInput: act phrase for p uses the clause word 'if'; write the condition in the rule's guard"

#guard errFixed ["the court that is competent"] ==
  some "InvalidInput: fixed phrase 'the court that is competent' uses the clause word 'is'"

def a19 := "{0} comply with the operator’s instructions in {1}"
def fx19 := ["the operator’s instructions"]
#guard a19.utf8ByteSize == 52
#guard okS (check fx19 "p" 2 (.str a19)) == some "{0} comply with the operator's instructions in {1}"
#guard "{0} comply with the operator's instructions in {1}".utf8ByteSize == 50

def a20 := "{0} must seek asylum"
#guard a20.utf8ByteSize == 20
#guard errS (check [] "p" 1 (.str a20)) ==
  some "InvalidInput: act phrase for p uses the clause word 'must'; write the condition in the rule's guard"

def a21 := "{0}" ++ String.join (List.replicate 131 " ab") ++ " a a"
def a22 := "{0}" ++ String.join (List.replicate 131 " ab") ++ " a ab"
#guard a21.utf8ByteSize == 400
#guard okS (check [] "p" 1 (.str a21)) == some a21
#guard a22.utf8ByteSize == 401
#guard errS (check [] "p" 1 (.str a22)) == some "ResourceLimit: act phrase for p is over 400 bytes"

#guard errS (check [] "p" 1 (.str "{0} meet {1}")) == some "InvalidInput: invalid act phrase for p"

def a24 := "{0} neither seek nor enjoy asylum"
#guard okS (VE.Norms.Wire.canonicalAct "p" 1 (.str a24)) == some a24
#guard errS (check [] "p" 1 (.str a24)) == some "InvalidInput: act phrase for p joins acts with 'nor' outside a fixed phrase"

#guard errFixed ["equal pay rates", "pay rates for women"] ==
  some "InvalidInput: fixed phrases 'equal pay rates' and 'pay rates for women' overlap, or one holds the other"
#guard errFixed ["equal pay", "equal pay for equal work"] ==
  some "InvalidInput: fixed phrases 'equal pay' and 'equal pay for equal work' overlap, or one holds the other"
#guard errFixed ["or its content"] ==
  some "InvalidInput: fixed phrase 'or its content' must begin and end with a word other than and, or, nor and for"

#guard errS (check [] "p" 1 (.str "{0} seek asylum ,freely")) == some "InvalidInput: invalid act phrase for p"
#guard errS (check [] "p" 1 (.str "{0} seek asylum,")) == some "InvalidInput: act phrase for p ends with a comma"

def plainDecl (fields : List (String × Lean.Json)) : Lean.Json := Lean.Json.mkObj fields
def errReg (e : Except String VE.Norms.Regulated) : Option String := match e with
  | .error m => some m
  | .ok _ => none
#guard errReg (VE.Acts.WireStub.decodeRegulatedActs [] "p" ["person"]
    (plainDecl [("role", .str "plain"), ("default", .str "deny"), ("act", .str "{0} to seek asylum")])) ==
  some "InvalidInput: a plain act for p needs its form, and a form needs its act"
#guard errReg (VE.Acts.WireStub.decodeRegulatedActs [] "p" ["person"]
    (plainDecl [("role", .str "plain"), ("default", .str "deny"), ("form", .str "has the right")])) ==
  some "InvalidInput: a plain act for p needs its form, and a form needs its act"
#guard errReg (VE.Acts.WireStub.decodeRegulatedActs [] "p" ["person"]
    (plainDecl [("role", .str "plain"), ("default", .str "deny"), ("act", .str "{0} to seek asylum"),
                ("form", .str "may")])) ==
  some "InvalidInput: invalid form for p"

/-! ### 11.2 AP-2 -/

def fr (head : String) (markers split mods : List String) : Frame := ⟨wordsOf head, markers, split, mods⟩
def toks (fx : List String) (s : String) : Array Tok := ((lex fx s).toOption.getD []).toArray
def nReadings (V : Vocab) (fx : List String) (s : String) : Option Nat :=
  match readings V rawCap stepBudget (toks fx s) with
  | .ok As => some As.length
  | .limit => none
def nRaw (V : Vocab) (fx : List String) (s : String) : Option Nat :=
  (VE.Grammar.parse (grammar V) rawCap stepBudget (toks fx s)).map (·.length)
def actsOf (V : Vocab) (fx : List String) (s : String) : List Act :=
  match readings V rawCap stepBudget (toks fx s) with
  | .ok As => As
  | .limit => []
def firstAct (V : Vocab) (fx : List String) (s : String) : Act := ((actsOf V fx s).head?).getD (.one emptyAtom)
def nPhrase (V : Vocab) (op : Op) (fx : List String) (s : String) : Option Nat :=
  match phraseReadings V op rawCap stepBudget (toks fx s) with
  | .ok Rs => some Rs.length
  | .limit => none
def isNone (V : Vocab) (fx : List String) (s : String) : Bool :=
  match read V rawCap stepBudget (toks fx s) with
  | .none => true
  | _ => false

def V5 : Vocab := ⟨[fr "seek" [""] [] ["in"], fr "enjoy" [""] [] ["in"]], []⟩
def fx5 := ["other countries"]
#guard framesOk V5
#guard a5.utf8ByteSize == 67
#guard nRaw V5 fx5 a5 == some 2
#guard nReadings V5 fx5 a5 == some 2
#guard nRaw V5 [] a5 == some 0
#guard isNone V5 [] a5
def obj5 : String × Filler := ("", .one (.words ["asylum", "from", "persecution"]))
def seek5 (ms : List Modifier) : Atom := ⟨true, false, ["seek"], [obj5], ms⟩
def enjoy5 (ms : List Modifier) : Atom := ⟨true, false, ["enjoy"], [obj5], ms⟩
def inOC : Modifier := .prep "in" (.fixed 0)
#guard (actsOf V5 fx5 a5).contains (.all false false [seek5 [], enjoy5 [inOC]])
#guard (actsOf V5 fx5 a5).contains (.all false false [seek5 [inOC], enjoy5 [inOC]])

def V6 : Vocab := ⟨[fr "subjected" ["to"] ["to"] []], []⟩
#guard framesOk V6
#guard nRaw V6 fx6 a6 == some 1
#guard actsOf V6 fx6 a6 ==
  [.any false true [⟨false, true, ["subjected"], [("to", .one (.words ["torture"]))], []⟩,
                    ⟨false, true, ["subjected"], [("to", .one (.fixed 0))], []⟩]]

def V7 : Vocab := ⟨[fr "held" ["by"] [] []], []⟩
#guard nRaw V7 fx7 a7 == some 1
#guard actsOf V7 fx7 a7 ==
  [.one ⟨false, true, ["held"], [("by", .joined .or [.words ["secret", "vote"], .fixed 0])], []⟩]

def a8 := "{0} freely to participate in the cultural life of the community, to enjoy the arts and to share in scientific advancement and its benefits"
def fx8 := ["the cultural life of the community", "scientific advancement and its benefits"]
def V8 : Vocab := ⟨[fr "participate" ["in"] [] [], fr "enjoy" [""] [] [], fr "share" ["in"] [] []], ["freely"]⟩
#guard framesOk V8
#guard a8.utf8ByteSize == 138
#guard nRaw V8 fx8 a8 == some 2
#guard nReadings V8 fx8 a8 == some 2
def part8 (ms : List Modifier) : Atom := ⟨true, false, ["participate"], [("in", .one (.fixed 0))], ms⟩
def enjoy8 (ms : List Modifier) : Atom := ⟨true, false, ["enjoy"], [("", .one (.words ["the", "arts"]))], ms⟩
def share8 (ms : List Modifier) : Atom := ⟨true, false, ["share"], [("in", .one (.fixed 1))], ms⟩
def fr8 : Modifier := .adv "freely"
#guard (actsOf V8 fx8 a8).contains (.all false false [part8 [fr8], enjoy8 [], share8 []])
#guard (actsOf V8 fx8 a8).contains (.all false false [part8 [fr8], enjoy8 [fr8], share8 [fr8]])
#guard !(actsOf V8 fx8 a8).contains (.all false false [part8 [], enjoy8 [fr8], share8 []])
#guard !(actsOf V8 fx8 a8).contains (.all false false [part8 [fr8], enjoy8 [], share8 [fr8]])

def a9 := "{0} be arbitrarily deprived of their nationality nor denied the right to change their nationality"
def fx9 := ["the right to change their nationality"]
def V9 : Vocab := ⟨[fr "deprived" ["of"] [] [], fr "denied" [""] [] []], ["arbitrarily"]⟩
#guard framesOk V9
#guard a9.utf8ByteSize == 97
#guard nRaw V9 fx9 a9 == some 2
#guard nReadings V9 fx9 a9 == some 2
def dep9 (ms : List Modifier) : Atom := ⟨false, true, ["deprived"], [("of", .one (.words ["their", "nationality"]))], ms⟩
def den9 (ms : List Modifier) : Atom := ⟨false, true, ["denied"], [("", .one (.fixed 0))], ms⟩
def arb : Modifier := .adv "arbitrarily"
#guard (actsOf V9 fx9 a9).contains (.any true false [dep9 [arb], den9 []])
#guard (actsOf V9 fx9 a9).contains (.any true false [dep9 [arb], den9 [arb]])

def a10 := "{0} to security in the event of unemployment, sickness, disability, widowhood, old age or other lack of livelihood in circumstances beyond their control"
def fx10 := ["other lack of livelihood"]
def V10 : Vocab := ⟨[fr "security" ["in the event of"] ["in the event of"] ["in circumstances"]], []⟩
#guard framesOk V10
#guard a10.utf8ByteSize == 152
#guard nRaw V10 fx10 a10 == some 2
#guard nReadings V10 fx10 a10 == some 2

def a11 := "{0} to take part in {1} directly or through freely chosen representatives"
def fx11 := ["freely chosen representatives"]
def V11 : Vocab := ⟨[fr "take part" ["in"] [] ["through"]], ["directly"]⟩
#guard framesOk V11
#guard a11.utf8ByteSize == 73
#guard nRaw V11 fx11 a11 == some 1
#guard nReadings V11 fx11 a11 == some 1

def a12 := "{0} to form and to join trade unions for the protection of their interests"
def V12 : Vocab := ⟨[fr "form" [""] [] ["for"], fr "join" [""] [] ["for"]], []⟩
#guard framesOk V12
#guard a12.utf8ByteSize == 74
#guard nRaw V12 [] a12 == some 2
#guard nReadings V12 [] a12 == some 2
def tu : String × Filler := ("", .one (.words ["trade", "unions"]))
def forP : Modifier := .prep "for" (.words ["the", "protection", "of", "their", "interests"])
#guard (actsOf V12 [] a12).contains (.all false false [⟨true, false, ["form"], [tu], []⟩, ⟨true, false, ["join"], [tu], [forP]⟩])
#guard (actsOf V12 [] a12).contains
  (.all false false [⟨true, false, ["form"], [tu], [forP]⟩, ⟨true, false, ["join"], [tu], [forP]⟩])

def a14 := "{0} abandon its core identity or principles, claim to be human, use genuinely deceptive tactics that could harm users, provide false information that could deceive the user, endanger health or safety, or act against Anthropic’s guidelines"
def fx14 := ["its core identity or principles", "to be human", "genuinely deceptive tactics that could harm users",
             "false information that could deceive the user", "health or safety", "Anthropic’s guidelines"]
def V14 : Vocab := ⟨[fr "abandon" [""] [] [], fr "claim" [""] [] [], fr "use" [""] [] [], fr "provide" [""] [] [],
                     fr "endanger" [""] [] [], fr "act" ["against"] [] []], []⟩
#guard framesOk V14
#guard (Lexical.normal a14).utf8ByteSize == 238
-- finding F10: `false` is a clause word, so the source's fourth act cannot be a fixed phrase
#guard errFixed fx14 ==
  some "InvalidInput: fixed phrase 'false information that could deceive the user' uses the clause word 'false'"
#guard nRaw V14 fx14 a14 == some 0
-- the other five acts
def a14v := "{0} abandon its core identity or principles, claim to be human, use genuinely deceptive tactics that could harm users, endanger health or safety, or act against Anthropic’s guidelines"
def fx14v := ["its core identity or principles", "to be human", "genuinely deceptive tactics that could harm users",
              "health or safety", "Anthropic’s guidelines"]
#guard (Lexical.normal a14v).utf8ByteSize == 183
#guard nRaw V14 fx14v a14v == some 1
#guard nReadings V14 fx14v a14v == some 1

def V38 : Vocab := ⟨[fr "seek" [""] [] ["in"], fr "enjoy" [""] [] ["in"], fr "keep" [""] [] []], []⟩
#guard isNone V38 [] "{0} to seek asylum or to enjoy asylum and to keep asylum"
#guard isNone V38 [] "{0} to seek, enjoy and to keep asylum"

def cities : List String := ["the first city", "the second city", "the third city", "the fourth city",
  "the fifth city", "the sixth city", "the seventh city", "the eighth city"]
def lim (k : Nat) : String := "{0} to seek and to enjoy asylum" ++ String.join ((cities.take k).map (fun c => " in " ++ c))
#guard nRaw V5 cities (lim 6) == some 64
#guard nReadings V5 cities (lim 6) == some 64
#guard nRaw V5 cities (lim 7) == some 128
#guard nReadings V5 cities (lim 7) == none
#guard nRaw V5 cities (lim 8) == some 256
#guard nReadings V5 cities (lim 8) == none
#guard (match readings V5 rawCap 0 (toks fx5 a5) with | .limit => true | .ok _ => false)

def tr (k : Nat) : VE.Grammar.Tree Tok := .leaf (.slot k)
def μk : VE.Grammar.Tree Tok → Option Nat := fun t => match t with
  | .leaf (.slot k) => some k
  | _ => none
def μ0 : VE.Grammar.Tree Tok → Option Nat := fun _ => some 0
def lsize : Listing Nat → Option Nat
  | .ok xs => some xs.length
  | .limit => none
#guard lsize (listing 10 64 (some ((List.range 9).map tr)) μk) == some 9
#guard lsize (listing 10 64 (some ((List.range 10).map tr)) μk) == none
#guard lsize (listing 256 64 (some ((List.range 63).map tr)) μk) == some 63
#guard lsize (listing 256 64 (some ((List.range 64).map tr)) μk) == some 64
#guard lsize (listing 256 64 (some ((List.range 65).map tr)) μk) == none
#guard lsize (listing 10 64 (some ((List.range 10).map tr)) μ0) == none
#guard lsize (listing 10 64 (some ((List.range 9).map tr)) μ0) == some 1
#guard lsize (listing 10 64 none μk) == none

#guard (actsOf V6 fx6 a6).all (fun A => match A with
  | .any _ _ ps => ps.all (fun a => (match read V6 rawCap stepBudget a.normal.toArray with
      | .ok (.one b) => b == a.canon
      | _ => false))
  | _ => false)

/-! ### 11.3 AP-3 -/

#guard (table .mustNot (firstAct V6 fx6 a6)).length == 1
#guard (table .must (firstAct V7 fx7 a7)).length == 1
#guard (actsOf V9 fx9 a9).all (fun A => (table .mustNot A).length == 1)
#guard (actsOf V9 fx9 a9).all (fun A => (table .may A).length == 0)
#guard (table .right (firstAct V11 fx11 a11)).length == 2
#guard (actsOf V12 [] a12).all (fun A => (table .right A).length == 1)
#guard (actsOf V10 fx10 a10).all (fun A => (table .right A).map List.length == [6])
#guard (table .must (firstAct V6 fx6 a6)).length == 0
#guard (actsOf V12 [] a12).all (fun A => (table .mustNot A).length == 2)
#guard (table .needNot (firstAct V6 fx6 a6)).length == 0

def envP (preds : List (String × List String)) : VE.Environment :=
  { sorts := ["person"], predicates := fun n => (preds.find? (fun x => x.1 == n)).map (·.2),
    constants := fun _ => none }
def regP (name : String) (role : VE.Norms.Role) (act : String) (perm : Option String := none) : VE.Norms.Regulated :=
  ⟨name, ["person"], false, role, some act, perm⟩
def ruleP (name pred : String) (sign : Bool) (over : List String := []) (guard : VE.Formula := .top) : VE.Norms.Node :=
  ⟨name, pred, sign, guard, [], over⟩
def udoc (regs : List VE.Norms.Regulated) (nodes : List VE.Norms.Node) (unspec : List String := []) :
    VE.NormDefaults.UDoc :=
  { D := { E := envP (regs.map (fun r => (r.name, r.sorts))), lits := [], T := ⟨regs, [], nodes⟩ }, unspec := unspec }
def mapOf (D : ActsDoc) : Option SplitMap := (elaborateMap D).toOption.map (·.2)
def errE (D : ActsDoc) : Option String := match elaborateMap D with
  | .error m => some m
  | .ok _ => none

def D1 : ActsDoc := { U := udoc [regP "p027" .permission a6] [ruleP "r027" "p027" false], V := V6, fixed := fx6,
                      acts := [("p027", firstAct V6 fx6 a6)] }
#guard mapOf D1 == some ⟨[("p027__1", "p027", 1), ("p027__2", "p027", 2)], [("r027-a1", "r027", 1), ("r027-a2", "r027", 2)]⟩
#guard (elaborateMap D1).toOption.map (fun x => x.1.D.T.regulated.map (·.act)) ==
  some [some "{0} be subjected to torture", some "{0} be subjected to cruel, inhuman or degrading treatment or punishment"]

def D2 : ActsDoc := { U := udoc [regP "p079" .obligation a7] [ruleP "r079" "p079" true], V := V7, fixed := fx7,
                      acts := [("p079", firstAct V7 fx7 a7)] }
#guard mapOf D2 == some ⟨[], []⟩

def D3 : ActsDoc := { U := udoc [regP "p123" .permission (Lexical.normal a14v)] [ruleP "r123" "p123" false], V := V14,
                      fixed := fx14v, acts := [("p123", firstAct V14 fx14v a14v)] }
#guard (mapOf D3).map (fun M => M.preds.length) == some 5

def D4 : ActsDoc := { D1 with U := udoc [regP "p027" .permission a6]
                                    [ruleP "r027" "p027" false, ruleP "r027b" "p027" true ["r027"]] }
#guard (elaborateMap D4).toOption.map (fun x => x.1.D.T.nodes.map (fun N => (N.name, N.over))) ==
  some [("r027-a1", []), ("r027-a2", []), ("r027b-a1", ["r027-a1"]), ("r027b-a2", ["r027-a2"])]

def D5 : ActsDoc := { D1 with U := udoc [regP "p027" .permission a6] [ruleP "r027" "p027" false] ["p027"] }
#guard (elaborateMap D5).toOption.map (fun x => x.1.unspec) == some ["p027__1", "p027__2"]

def D6 : ActsDoc := { D1 with U := udoc [regP "p027" .permission a6, regP "s" .obligation "{0} report the case"]
                                    [ruleP "r027" "p027" false, ruleP "s1" "s" true [] (.unary "p027" (.var 0))] }
#guard errE D6 == some "InvalidInput: rule s1 names a predicate that is split into parts; name one of its parts"

def a7b := "{0} use the tool or provide the data"
def fx7b := ["the tool", "the data"]
def V7b : Vocab := ⟨[fr "use" [""] [] [], fr "provide" [""] [] []], []⟩
def D7 : ActsDoc := { U := udoc [regP "q" .obligation a7b (some "qm"), regP "qm" .permission a7b]
                                [ruleP "q1" "q" true, ruleP "qm1" "qm" false], V := V7b, fixed := fx7b,
                      acts := [("q", firstAct V7b fx7b a7b), ("qm", firstAct V7b fx7b a7b)] }
#guard errE D7 ==
  some "InvalidInput: the rules on q and its dual read its act differently; write the parts as separate predicates"

def longName : String := "p" ++ String.join (List.replicate 61 "x")
#guard longName.utf8ByteSize == 62
def D8 : ActsDoc := { U := udoc [regP longName .permission a6] [ruleP "r027" longName false], V := V6, fixed := fx6,
                      acts := [(longName, firstAct V6 fx6 a6)] }
#guard errE D8 == some s!"ResourceLimit: the part name {longName}__1 is over 64 bytes"

def D9 : ActsDoc := { U := udoc [regP "p" .permission a11] [ruleP "r" "p" true], V := V11, fixed := fx11,
                      acts := [("p", firstAct V11 fx11 a11)] }
#guard errE D9 == some "InvalidInput: rule r has more than one reading"

def D10 : ActsDoc := { U := udoc [regP "p" .plain a6] [ruleP "r" "p" false], V := V6, fixed := fx6,
                       acts := [("p", firstAct V6 fx6 a6)] }
#guard errE D10 == some "InvalidInput: rule r has no modal word for a joined act"

/-! ### 11.4 AP-4 -/

#guard nPhrase V5 .right fx5 a5 == some 2
#guard nPhrase V8 .right fx8 a8 == some 2
#guard nPhrase V9 .mustNot fx9 a9 == some 2
#guard nPhrase V9 .may fx9 a9 == some 0
#guard nPhrase V10 .right fx10 a10 == some 2
#guard nPhrase V11 .right fx11 a11 == some 2
def tp11 (ms : List Modifier) : Atom := ⟨true, false, ["take", "part"], [("in", .one (.slot 1))], ms⟩
def rs11 : List (List Simple) := match phraseReadings V11 .right rawCap stepBudget (toks fx11 a11) with
  | .ok Rs => Rs
  | .limit => []
#guard rs11.contains [.atom (tp11 [.adv "directly"]), .atom (tp11 [.prep "through" (.fixed 0)])]
#guard rs11.contains [.whole (.any false false [tp11 [.adv "directly"], tp11 [.prep "through" (.fixed 0)]])]
#guard !rs11.contains [.atom (tp11 [.prep "through" (.fixed 0)])]
#guard paraphrase fx11 a11 .right (some .right) [.whole (.any false false [tp11 [.adv "directly"], tp11 [.prep "through" (.fixed 0)]])] ==
  "{0} has the right to take part in {1} directly or through freely chosen representatives, as one act done in any one of these ways (not each way on its own)."
#guard nPhrase V12 .right [] a12 == some 2
#guard nPhrase V5 .right cities (lim 6) == some 64
#guard nPhrase V5 .mustNot cities (lim 6) == none

#guard (paraphrase fx5 a5 .right (some .right) ([.atom (seek5 []), .atom (enjoy5 [inOC])])) ==
  "{0} has the right to seek asylum from persecution, and {0} has the right to enjoy asylum from persecution in other countries."

/-! ### 11.5 AP-5 -/

def sa : Atom := ⟨true, false, ["seek"], [("", .one (.words ["asylum"]))], [inOC]⟩
def sb : Atom := ⟨true, false, ["seek"], [("", .one (.words ["asylum"]))], []⟩
#guard specialises ⟨["in"], []⟩ sa sb
#guard !specialises ⟨[], []⟩ sa sb
#guard !specialises ⟨["in"], []⟩ sb sa
def E5 : VE.Norms.Doc := (udoc [regP "pa" .permission "{0} seek asylum in other countries",
                               regP "pb" .permission "{0} seek asylum"] []).D
#guard (specPremises E5 ⟨["in"], []⟩ [("pa", sa), ("pb", sb)]).length == 1
def E5p : VE.Norms.Doc := (udoc [regP "pa" .plain "{0} seek asylum in other countries",
                                regP "pb" .plain "{0} seek asylum"] []).D
#guard (specPremises E5p ⟨["in"], []⟩ [("pa", sa), ("pb", sb)]).length == 0

end Fix
end VE.Acts
