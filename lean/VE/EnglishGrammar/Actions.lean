import VE.EnglishGrammar.Rules
import VE.EnglishGrammar.Fixed.Version
import VE.Grammar.Meaning

/-! The action library of the base profile (docs/spec/english-lean-s2.md 2.7, 2.8 and 5.2).

A derivation's value is computed bottom-up: a `formula` value is a function from the context (scope,
document state, list-marker depth, nesting, leftmost position) to a formula or a declared rejection; a
`relative` value is the same with the subject `var 0`; a `term` value gives a term and, for a written
constant, its datum; a `declaration` value gives the binding it introduces. The side conditions of the
hand parser are rejections computed here; they never remove a derivation.

`acts E L = fixedActs ++ lexActs E L`. `fixedActs` is closed: the action of fixed row `i` is
`FixedAct.action` of that row, which reads neither `E` nor `L`; the sorts it needs arrive inside the
children's values. `lexActs E L` has one action per lexical row, `LexAct.action` of the row, built from
the row's data alone. An action's argument types are the types of its rule's right-hand side; when they
do not have the shape the action reads, the action is `unfit`, which `Grammar.typed` refuses, so `read`
reports `invalidGrammar notTyped` instead of computing anything.
-/

namespace VE.EnglishGrammar
open VE.Grammar

/-- The bindings in force, innermost first: a sort and a reference text. -/
abbrev Scope := List (String × String)

structure Ctx where
  scope : Scope
  st : DState
  /-- The list-marker depth. -/
  depth : Nat
  /-- The formula nesting, 1 at the top. -/
  nesting : Nat
  /-- Whether the value's first token is the first token of the sentence's formula. -/
  leftmost : Bool

/-- The datum of a written constant (2.6): its name, its sort, and whether the spelling that wrote it is
a name form (2.1), which the coordination actions require (2.7). -/
structure ConstVal where
  name : String
  sort : String
  nameForm : Bool
  deriving DecidableEq, Repr

/-- A term with the constant's datum when the term is a constant written by a spelling rule; `none` for
`it`, a reference and a label (2.7). -/
structure TermVal where
  term : ETerm
  written : Option ConstVal := none
  deriving DecidableEq, Repr

/-- The value of each semantic type (spec 5.2). -/
def Sem : Ty → Type
  | .tok => Tok
  | .sentence => DState → Except Reject (EFormula × Bool × DState)
  | .formula => Ctx → Except Reject EFormula
  | .relative => Ctx → Except Reject EFormula
  | .term => Ctx → Except Reject TermVal
  | .intTerm => Ctx → Except Reject TermVal
  | .declaration => Ctx → Except Reject (String × String)
  | .guard => Ctx → Except Reject EFormula
  | .marker => Bool
  | .unit => Unit
  | .listMarker => String
  | .noun => String × String
  | .label => String × String
  | .constant => ConstVal
  | .adjective => String × String
  | .natSubject => String × String × String
  | .count => Bool
  | .relation => String

def sig : Sig Tok where
  Ty := Ty
  decEq := inferInstance
  Sem := Sem
  tok := .tok
  leaf := fun t => t

/-! ## The document state -/

def ETerm.consts : ETerm → List String
  | .const c => [c]
  | .var _ | .num _ => []
  | .add a b => a.consts ++ b.consts
  | .scale _ t => t.consts

/-- The constants of a formula, as `_mentioned_constants` collects them (`english.py:88–100`): every
constant of a unary or binary atom, an equation, a comparison or a reach, under any connective; an atom
of three or more arguments is not visited. -/
def EFormula.consts : EFormula → List String
  | .top | .bottom => []
  | .pred _ [t] => t.consts
  | .pred _ [t, u] => t.consts ++ u.consts
  | .pred _ _ => []
  | .eq t u | .lt t u | .le t u => t.consts ++ u.consts
  | .not a | .all _ a | .ex _ a => a.consts
  | .and a b | .or a b | .implies a b => a.consts ++ b.consts
  | .reachNamed _ _ t u => t.consts ++ u.consts
  | .reachBody _ _ a t u => a.consts ++ t.consts ++ u.consts

/-- Whether a formula has a binder, as `_has_discourse_binder` decides (`english.py:103–115`): an
`all` or `ex` anywhere, a reach body included. -/
def EFormula.hasBinder : EFormula → Bool
  | .all _ _ | .ex _ _ => true
  | .not a => a.hasBinder
  | .and a b | .or a b | .implies a b => a.hasBinder || b.hasBinder
  | .reachBody _ _ a _ _ => a.hasBinder
  | _ => false

/-- The state after a sentence (spec 2.7): the referents joined with the formula's constants, sorted,
without repeats; `binderSeen` or-ed with whether the formula has a binder. -/
def DState.after (st : DState) (A : EFormula) : DState :=
  ⟨((st.referents ++ A.consts).mergeSort fun a b => decide (a ≤ b)).eraseDups, st.binderSeen || A.hasBinder⟩

/-! ## Contexts -/

/-- The context of a sentence's formula. -/
def Ctx.start (st : DState) : Ctx := ⟨[], st, 0, 1, true⟩

/-- A child after a terminal or a sibling: not leftmost. -/
def Ctx.inner (c : Ctx) : Ctx := { c with leftmost := false }

/-- A formula child of `child()` (`english.py:1395`): one level deeper. -/
def Ctx.deeper (c : Ctx) : Ctx := { c with nesting := c.nesting + 1, leftmost := false }

/-- A listed child: one list level and one nesting level deeper. -/
def Ctx.listed (c : Ctx) : Ctx := { c with depth := c.depth + 1, nesting := c.nesting + 1, leftmost := false }

/-- The context under a new binding, innermost. -/
def Ctx.push (c : Ctx) (b : String × String) : Ctx := { c with scope := b :: c.scope, leftmost := false }

/-- The index of the innermost binding whose reference text is `ref`. -/
def Ctx.lookup (c : Ctx) (ref : String) : Except Reject TermVal :=
  match c.scope.findIdx? (·.2 == ref) with
  | some i => .ok ⟨.var i, none⟩
  | none => .error .unboundReference

/-- A declaration's binding, unless its reference text is already in scope (`english.py:942`). -/
def Ctx.bind (c : Ctx) (b : String × String) : Except Reject (String × String) :=
  if c.scope.any (·.2 == b.2) then .error .shadowedName else .ok b

/-- The `it` rule (spec 2.7): the sole referent of the earlier sentences, at the start of a top-level
formula, when no earlier sentence had a binder. -/
def Ctx.it (c : Ctx) : Except Reject TermVal :=
  if c.leftmost && c.scope.isEmpty && !c.st.binderSeen then
    match c.st.referents with
    | [x] => .ok ⟨.const x, none⟩
    | _ => .error .pronounUnresolved
  else .error .pronounUnresolved

/-! ## Building actions -/

/-- The argument types without the terminals. -/
def strip : List Ty → List Ty
  | [] => []
  | τ :: τs => if τ = .tok then strip τs else τ :: strip τs

/-- The arguments without the terminals' values. -/
def stripArgs : (τs : List Ty) → Args sig τs → Args sig (strip τs)
  | [], _ => ()
  | τ :: τs, xs =>
    if h : τ = .tok then
      cast (show Args sig (strip τs) = Args sig (strip (τ :: τs)) by simp [strip, h]) (stripArgs τs xs.2)
    else
      let ys : Args sig (τ :: strip τs) := (xs.1, stripArgs τs xs.2)
      cast (show Args sig (τ :: strip τs) = Args sig (strip (τ :: τs)) by simp [strip, h]) ys

/-- No action of the library: no argument and no value. A rule that has it is not typed. -/
def unfit : Action sig := ⟨[], .unit, fun _ => ()⟩

/-- The action over the argument types `τs` that reads the values of its nonterminal children, of
types `core`, with `f`; `unfit` when the children do not have those types. -/
def build (core : List Ty) (out : Ty) (f : Args sig core → Sem out) (τs : List Ty) : Action sig :=
  if h : strip τs = core then ⟨τs, out, fun xs => f (cast (congrArg (Args sig) h) (stripArgs τs xs))⟩
  else unfit

/-- The action of a rule whose children are terminals, with a value that reads none of them. -/
def constant (out : Ty) (v : Sem out) (τs : List Ty) : Action sig :=
  if τs.all (· == .tok) then ⟨τs, out, fun _ => v⟩ else unfit

/-- The text of a token. -/
def tokText : Tok → String
  | .word s _ | .quoted s => s
  | .label l i => l ++ toString i
  | .numeral v => toString v
  | .punct s _ _ => s

/-- The action of a rule of exactly one terminal, whose value reads its text. -/
def ofToken (out : Ty) (f : String → Sem out) (τs : List Ty) : Action sig :=
  if τs = [.tok] then ⟨[.tok], out, fun xs => f (tokText xs.1)⟩ else unfit

/-- The term values among the arguments, in order. -/
def termsOf : (τs : List Ty) → Args sig τs → List (Sem .term)
  | [], _ => []
  | τ :: τs, xs => if h : τ = .term then cast (by rw [h]; rfl) xs.1 :: termsOf τs xs.2 else termsOf τs xs.2

/-- The action of a rule of terminals and terms, which reads the terms with `f`; `f` learns whether the
first symbol is a term (and may then keep `leftmost`). -/
def ofTerms (out : Ty) (f : Bool → List (Sem .term) → Sem out) (τs : List Ty) : Action sig :=
  if τs.all (fun τ => τ == .tok || τ == .term) then ⟨τs, out, fun xs => f (τs.head? == some .term) (termsOf τs xs)⟩
  else unfit

/-- Runs the terms of a clause: the first keeps `leftmost` when it begins the rule, the others do not. -/
def runTerms : List (Sem .term) → Ctx → Bool → Except Reject (List ETerm)
  | [], _, _ => .ok []
  | t :: ts, c, first => do
    let v ← t (if first then c else c.inner)
    let vs ← runTerms ts c false
    pure (v.term :: vs)

/-- The arguments in declaration order: the one written at the hole `j` is argument `j`. -/
def permute {α : Type} (order : List Nat) (xs : List α) : List α :=
  (List.range order.length).filterMap fun j => ((order.zip xs).find? (·.1 == j)).map (·.2)

/-- A clause and, when negated, its negation. -/
def polarity (negated : Bool) (A : EFormula) : EFormula := if negated then .not A else A

def Conn.make : Conn → EFormula → EFormula → EFormula
  | .and => .and
  | .or => .or
  | .implies => .implies

/-- The markers of a listing at a depth (`_markers`, `english.py:564`). -/
def markersAt (depth : Nat) : String × String := if depth % 2 == 0 then ("(a)", "(b)") else ("(i)", "(ii)")

/-- A written constant whose spelling is a name form (`english.py:1574–1577`). -/
def TermVal.name? (t : TermVal) : Option ConstVal :=
  match t.written with
  | some v => if v.nameForm then some v else none
  | none => none

/-- The three-name coordination (`english.py:1570–1599`): the scope, the name forms, distinct names,
the adjective's sort; then the right-associated formula. -/
def runCoordSubjects (k : Conn) (t1 t2 t3 : Sem .term) (adj : String × String) (c : Ctx) : Except Reject EFormula :=
  if !c.scope.isEmpty then .error .coordinationForm
  else do
    let u1 ← t1 c
    let u2 ← t2 c.inner
    let u3 ← t3 c.inner
    match u1.name?, u2.name?, u3.name? with
    | some a, some b, some d =>
      if a.name == b.name || a.name == d.name || b.name == d.name then .error .coordinationRepeated
      else if a.sort != adj.2 || b.sort != adj.2 || d.sort != adj.2 then .error .sortMismatch
      else
        let atom := fun (x : ConstVal) => EFormula.pred adj.1 [.const x.name]
        .ok (k.make (atom a) (k.make (atom b) (atom d)))
    | _, _, _ => .error .coordinationForm

/-- The three-property coordination (`english.py:1600–1613`). -/
def runCoordAdjectives (k : Conn) (t : Sem .term) (a1 a2 a3 : String × String) (c : Ctx) :
    Except Reject EFormula :=
  if !c.scope.isEmpty then .error .coordinationForm
  else do
    let u ← t c
    match u.name? with
    | some x =>
      if a1.1 == a2.1 || a1.1 == a3.1 || a2.1 == a3.1 then .error .coordinationRepeated
      else if x.sort != a1.2 || x.sort != a2.2 || x.sort != a3.2 then .error .sortMismatch
      else
        let atom := fun (a : String × String) => EFormula.pred a.1 [.const x.name]
        .ok (k.make (atom a1) (k.make (atom a2) (atom a3)))
    | none => .error .coordinationForm

/-- The relative of a natural `every` clause is a negation (`english.py:1538–1540`). -/
def negatedTail : EFormula → Bool
  | .not _ => true
  | .and (.not _) _ => true
  | _ => false

/-- The sort of the innermost binding. -/
def Ctx.innerSort (c : Ctx) : Option String := c.scope.head?.map (·.1)

/-- A reach with a body (`english.py:1458–1477`): the terms, the source declaration in the scope, the
destination with the source pushed, one sort, then the body with both pushed. -/
def runReachBody (listed refl : Bool) (t u : Sem .term) (src dst : Sem .declaration) (body : Sem .formula)
    (c : Ctx) : Except Reject EFormula := do
  let a ← t c.inner
  let b ← u c.inner
  let s ← src c.inner
  let d ← dst (c.push s)
  if s.1 != d.1 then .error .sortMismatch
  else
    let inner := (c.push s).push d
    let B ← body (if listed then inner.listed else inner.deeper)
    pure (.reachBody refl s.1 B a.term b.term)

/-- The action of a fixed row, from the type of its left-hand side and the types of its right-hand
side (spec 2.7). -/
def FixedAct.action (lhs : Ty) (τs : List Ty) : FixedAct → Action sig
  | .sentence false =>
    build [.formula] .sentence (fun xs st => (fun A => (A, false, st.after A)) <$> xs.1 (Ctx.start st)) τs
  | .sentence true =>
    build [.marker, .formula] .sentence (fun xs st => (fun A => (A, true, st.after A)) <$> xs.2.1 (Ctx.start st)) τs
  | .mark => constant .marker true τs
  | .unit => constant .unit () τs
  | .listMarker => ofToken .listMarker id τs
  | .through => build [lhs] lhs (fun xs => xs.1) τs
  | .nest =>
    build [.formula] .formula (fun xs c => if c.nesting > 64 then .error .nestingLimit else xs.1 c) τs
  | .not => build [.formula] .formula (fun xs c => EFormula.not <$> xs.1 c.deeper) τs
  | .and2 => build [.formula, .formula] .formula (fun xs c => do
      let a ← xs.1 c.inner
      let b ← xs.2.1 c.inner
      pure (.and a b)) τs
  | .or2 => build [.formula, .formula] .formula (fun xs c => do
      let a ← xs.1 c.inner
      let b ← xs.2.1 c.inner
      pure (.or a b)) τs
  | .implies2 => build [.formula, .formula] .formula (fun xs c => do
      let a ← xs.1 c.deeper
      let b ← xs.2.1 c.deeper
      pure (.implies a b)) τs
  | .listWords k => build [.formula, .formula] .formula (fun xs c => do
      let a ← xs.1 c.listed
      let b ← xs.2.1 c.listed
      pure (k.make a b)) τs
  | .listMarkers k => build [.listMarker, .formula, .listMarker, .formula] .formula (fun xs c =>
      let m1 : String := xs.1
      let m2 : String := xs.2.2.1
      if m1 != (markersAt c.depth).1 then .error .markerDepth
      else do
        let a ← xs.2.1 c.listed
        if m2 != (markersAt c.depth).2 then .error .markerDepth
        else do
          let b ← xs.2.2.2.1 c.listed
          pure (k.make a b)) τs
  | .guardAnd | .relAnd => build [.relative, .relative] .relative (fun xs c => do
      let a ← xs.1 c.inner
      let b ← xs.2.1 c.inner
      pure (.and a b)) τs
  | .guardLeft => build [.relative, .relative, .relative] .relative (fun xs c => do
      let a ← xs.1 c.inner
      let b ← xs.2.1 c.inner
      let d ← xs.2.2.1 c.inner
      pure (.and (.and a b) d)) τs
  | .guardRight => build [.relative, .relative, .relative] .relative (fun xs c => do
      let a ← xs.1 c.inner
      let b ← xs.2.1 c.inner
      let d ← xs.2.2.1 c.inner
      pure (.and a (.and b d))) τs
  | .forallBody => build [.declaration, .formula] .formula (fun xs c => do
      let b ← xs.1 c.inner
      let B ← xs.2.1 (c.push b).deeper
      pure (.all b.1 B)) τs
  | .forallGuardBody => build [.declaration, .unit, .relative, .formula] .formula (fun xs c => do
      let b ← xs.1 c.inner
      let G ← xs.2.2.1 (c.push b)
      let B ← xs.2.2.2.1 (c.push b).deeper
      pure (.all b.1 (.implies G B))) τs
  | .forallRel => build [.declaration, .relative] .formula (fun xs c => do
      let b ← xs.1 c.inner
      let R ← xs.2.1 (c.push b)
      pure (.all b.1 R)) τs
  | .forallGuardRel => build [.declaration, .unit, .relative, .relative] .formula (fun xs c => do
      let b ← xs.1 c.inner
      let G ← xs.2.2.1 (c.push b)
      let R ← xs.2.2.2.1 (c.push b)
      pure (.all b.1 (.implies G R))) τs
  | .existsBody => build [.unit, .declaration, .formula] .formula (fun xs c => do
      let b ← xs.2.1 c.inner
      let B ← xs.2.2.1 (c.push b).deeper
      pure (.ex b.1 B)) τs
  | .existsRel => build [.unit, .declaration, .relative] .formula (fun xs c => do
      let b ← xs.2.1 c.inner
      let R ← xs.2.2.1 (c.push b)
      pure (.ex b.1 R)) τs
  | .declThat => build [.noun] .declaration (fun xs c => c.bind (xs.1.1, "that " ++ xs.1.2)) τs
  | .declOrdinal o =>
    build [.noun] .declaration (fun xs c => c.bind (xs.1.1, "the " ++ o ++ " " ++ xs.1.2)) τs
  | .declNamed => build [.noun, .label] .declaration (fun xs c =>
      if xs.2.1.1 != xs.1.1 then .error .sortMismatch else c.bind (xs.1.1, xs.2.1.2)) τs
  | .termConst => build [.constant] .term (fun xs _ => .ok ⟨.const xs.1.name, some xs.1⟩) τs
  | .termIt => build [] .term (fun _ c => c.it) τs
  | .termRef pre => build [.noun] .term (fun xs c => c.lookup (pre ++ " " ++ xs.1.2)) τs
  | .termLabel => build [.label] .term (fun xs c => c.lookup xs.1.2) τs
  | .top => build [] .formula (fun _ _ => .ok .top) τs
  | .bottom => build [] .formula (fun _ _ => .ok .bottom) τs
  | .eq => build [.term, .term] .formula (fun xs c => do
      let t ← xs.1 c
      let u ← xs.2.1 c.inner
      pure (.eq t.term u.term)) τs
  | .coordSubjects k => build [.term, .term, .term, .adjective] .formula
      (fun xs => runCoordSubjects k xs.1 xs.2.1 xs.2.2.1 xs.2.2.2.1) τs
  | .coordAdjectives k => build [.term, .adjective, .adjective, .adjective] .formula
      (fun xs => runCoordAdjectives k xs.1 xs.2.1 xs.2.2.1 xs.2.2.2.1) τs
  | .naturalTop => build [.formula] .formula (fun xs c =>
      if c.scope.isEmpty then xs.1 c else .error .naturalScoped) τs
  | .someDecl => build [.declaration, .relative] .formula (fun xs c => do
      let b ← xs.1 c.inner
      let T ← xs.2.1 (c.push b)
      pure (.ex b.1 T)) τs
  | .copulaAnd => build [.relative, .adjective] .relative (fun xs c => do
      let R ← xs.1 c.inner
      if c.innerSort != some xs.2.1.2 then .error .sortMismatch
      else pure (.and R (.pred xs.2.1.1 [.var 0]))) τs
  | .noDecl => build [.declaration, .relative] .formula (fun xs c => do
      let b ← xs.1 c.inner
      let R ← xs.2.1 (c.push b)
      pure (.not (.ex b.1 R))) τs
  | .everySubject => build [.natSubject, .relative] .formula (fun xs c => do
      let (p, s, n) := xs.1
      let T ← xs.2.1 (c.push (s, "that " ++ n))
      if negatedTail T then .error (.blockedWording "natural-negation")
      else pure (.all s (.implies (.pred p [.var 0]) T))) τs
  | .everyOwner => build [.declaration, .relative] .formula (fun xs c => do
      let b ← xs.1 c.inner
      let O ← xs.2.1 (c.push b)
      pure (.all b.1 O)) τs
  | .reachNamed => build [.term, .term, .count, .relation] .formula (fun xs c => do
      let a ← xs.1 c.inner
      let b ← xs.2.1 c.inner
      pure (.reachNamed xs.2.2.1 xs.2.2.2.1 a.term b.term)) τs
  | .reachBody listed =>
    build [.term, .term, .count, .unit, .declaration, .unit, .declaration, .formula] .formula
      (fun xs => runReachBody listed xs.2.2.1 xs.1 xs.2.1 xs.2.2.2.2.1 xs.2.2.2.2.2.2.1 xs.2.2.2.2.2.2.2.1) τs
  | .count refl => constant .count refl τs

/-- The action of a lexical row, from the types of its right-hand side (spec 2.7). -/
def LexAct.action (τs : List Ty) : LexAct → Action sig
  | .pred p order negated => ofTerms .formula (fun first ts c => do
      let ws ← runTerms ts c first
      pure (polarity negated (.pred p (permute order ws)))) τs
  | .relSubject p order negated => ofTerms .relative (fun first ts c =>
      if ts.length == order.length then do
        -- the wording begins with a word: the rule keeps every term, and the subject is prepended
        let ws ← runTerms ts c first
        pure (polarity negated (.pred p (.var 0 :: permute order ws)))
      else if order.head? == some 0 then do
        let ws ← runTerms ts c first
        pure (polarity negated (.pred p (permute order (.var 0 :: ws))))
      else .error .relativeForm) τs
  | .relObject p negated => ofTerms .relative (fun first ts c => do
      let ws ← runTerms ts c first
      pure (polarity negated (.pred p (ws ++ [.var 0])))) τs
  | .noun s n => constant .noun (s, n) τs
  | .label s => ofToken .label (fun text => (s, text)) τs
  | .const c s nf => constant .constant ⟨c, s, nf⟩ τs
  | .adjective p s => constant .adjective (p, s) τs
  | .natSubject p s n => constant .natSubject (p, s, n) τs
  | .copulaRel p => constant .relative (fun _ => .ok (.pred p [.var 0])) τs
  | .owner s1 s2 => constant .relative (fun c =>
      if c.innerSort == some s2 then .ok (.ex s1 (.pred "owns" [.var 0, .var 1])) else .error .sortMismatch) τs
  | .relation r => constant .relation r τs

/-- The types of a right-hand side. -/
def rhsTys (rhs : List (Sym Terminal)) : List Ty := rhs.map (symTy sig ntTy)

/-- The fixed actions: the action of fixed row `i` at index `i`. Closed: no environment, no lexicon. -/
def fixedActs : Array (Action sig) :=
  relationalFolRows.map fun r => r.act.action (ntTy r.lhs) (rhsTys r.rhs)

/-- One action per lexical rule, in the order of `lexRules E L`. -/
def lexActs (E : Env) (L : Lexicon) : Array (Action sig) :=
  (lexRows E L).toArray.map fun r => r.act.action (rhsTys r.rhs)

def acts (E : Env) (L : Lexicon) : Array (Action sig) := fixedActs ++ lexActs E L

/-- The version of the trusted definitions of the English instance (spec 2.9, 5.2): the one constant
`Fixed.actionsVersion` that `tools/english_grammar_gen.py --write` renders from `LOCK.json`, never a copy. -/
def actionsVersion : String := Fixed.actionsVersion

end VE.EnglishGrammar
