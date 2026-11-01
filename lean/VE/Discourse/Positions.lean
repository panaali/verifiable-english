import VE.Discourse.WellFormed
import VE.Compose.Content

/-! # Formula positions, slots and their resolution (docs/spec/discourse.md 14.2, 14.3)

`positions E c` lists every formula of a `VE.Compose.Content` with the sorts of the variables free in it;
`withPositions` writes formulas back. Inside a fenced content a recorded formula-producing mention `m` stands as
the reserved constant or predicate `slotName m.id`; `resolveContent` rewrites each slot by its recorded target
(14.3 resolution steps 1 to 4) and type-checks every position. `IntendedAt` reads a position of the content as
written with each slot interpreted directly in the structure (4.4's table, one row per slot), and
`resolve_position_faithful` is their agreement. The other steps of 14.3 that the composed path runs around the fence
compiler (reserved names, header slots, rule targets, soft fields, JSON contents, uniqueness) are the functions of
the last section; no route calls any of them before cmp-s4. -/
namespace VE.Discourse
open VE.Compose (Content)
universe u

/-- A W1 node's context: its predicate's argument sorts, reversed (de Bruijn order). -/
def nodeContext (E : VE.Environment) (N : VE.SoftNorms.SoftNode) : List String :=
  ((E.predicates N.pred).getD []).reverse

/-- A node's positions: its guard, each carve-out, then each sufficient and each necessary exception condition. -/
def nodePositions (E : VE.Environment) (N : VE.SoftNorms.SoftNode) : List (List String × VE.Formula) :=
  let ctx := nodeContext E N
  ((ctx, N.guard) :: N.carveOuts.map (ctx, ·)) ++
    (match N.exception with
     | some x => (x.sufficient ++ x.necessary).map (ctx, ·)
     | none => [])

/-- A right line's positions: those of its norm, liberty and recognition nodes, in that order. -/
def linePositions (E : VE.Environment) (l : VE.Rights.SourceLine) : List (List String × VE.Formula) :=
  (l.norm.toList ++ l.liberty.toList ++ l.recognition.toList).flatMap (nodePositions E)

/-- The formula positions of a content with their contexts, in canonical order (plan 2.8). -/
def positions (E : VE.Environment) : VE.Compose.Content → List (List String × VE.Formula)
  | .assertion φ => [([], φ)]
  | .norm N => nodePositions E N
  | .right R => ([R.holder], R.guard) :: R.lines.flatMap (linePositions E)
  | .rightLines _ ls => ls.flatMap (linePositions E)
  | .limitation _ => []

/-! ## Writing positions back: each `…Set` takes its formulas from the front of the list, in `positions` order -/

def excSet (x : VE.SoftNorms.Exception) (fs : List VE.Formula) : VE.SoftNorms.Exception :=
  { x with sufficient := fs.take x.sufficient.length,
           necessary := (fs.drop x.sufficient.length).take x.necessary.length }

def nodeSet (N : VE.SoftNorms.SoftNode) (fs : List VE.Formula) : VE.SoftNorms.SoftNode :=
  { N with guard := fs.headD N.guard, carveOuts := (fs.drop 1).take N.carveOuts.length,
           exception := N.exception.map (excSet · (fs.drop (N.carveOuts.length + 1))) }

/-- The number of positions of an optional node. -/
def optCount : Option VE.SoftNorms.SoftNode → Nat
  | some N => N.carveOuts.length + 1 + (match N.exception with
      | some x => x.sufficient.length + x.necessary.length | none => 0)
  | none => 0

def lineSet (l : VE.Rights.SourceLine) (fs : List VE.Formula) : VE.Rights.SourceLine :=
  { l with norm := l.norm.map (nodeSet · fs), liberty := l.liberty.map (nodeSet · (fs.drop (optCount l.norm))),
           recognition := l.recognition.map (nodeSet · (fs.drop (optCount l.norm + optCount l.liberty))) }

def linesSet : List VE.Rights.SourceLine → List VE.Formula → List VE.Rights.SourceLine
  | [], _ => []
  | l :: ls, fs => lineSet l fs :: linesSet ls (fs.drop (optCount l.norm + optCount l.liberty + optCount l.recognition))

def contentSet : Content → List VE.Formula → Content
  | .assertion φ, fs => .assertion (fs.headD φ)
  | .norm N, fs => .norm (nodeSet N fs)
  | .right R, fs => .right { R with guard := fs.headD R.guard, lines := linesSet R.lines (fs.drop 1) }
  | .rightLines r ls, fs => .rightLines r (linesSet ls fs)
  | .limitation L, _ => .limitation L

/-- The content with its position formulas replaced, in `positions` order, every other field kept; `none` when the
    list's length is not the number of positions. -/
def withPositions (E : VE.Environment) (c : VE.Compose.Content) (fs : List VE.Formula) : Option VE.Compose.Content :=
  if fs.length = (positions E c).length then some (contentSet c fs) else none

/-- The unit's recorded formula-producing mentions (1.4: a formula-producing form and a target that is neither a
    `unit` nor an `anchor`), in manifest order. -/
def formulaMentions (K : Manifest) (unit : String) : List Mention :=
  K.mentions.filter fun m => m.unit == unit && producing m

/-- The reserved name of mention `m`'s slot. -/
def slotPrefix : String := "ve__slot__"
def slotName (m : String) : String := slotPrefix ++ m

/-! ## Rewriting one slot (14.3 resolution step 3) -/

/-- At depth `d`: the slot constant `n` becomes `t d`; every other free variable is lifted by `k`. -/
def placeT (n : String) (t : Nat → VE.Term) (k d : Nat) : VE.Term → VE.Term
  | .var i => if i < d then .var i else .var (i + k)
  | .const c => if c = n then t d else .const c

def place (n : String) (t : Nat → VE.Term) (k : Nat) : Nat → VE.Formula → VE.Formula
  | _, .top => .top
  | _, .bottom => .bottom
  | d, .unary p x => .unary p (placeT n t k d x)
  | d, .binary p x y => .binary p (placeT n t k d x) (placeT n t k d y)
  | d, .eq x y => .eq (placeT n t k d x) (placeT n t k d y)
  | d, .not a => .not (place n t k d a)
  | d, .and a b => .and (place n t k d a) (place n t k d b)
  | d, .or a b => .or (place n t k d a) (place n t k d b)
  | d, .implies a b => .implies (place n t k d a) (place n t k d b)
  | d, .all s a => .all s (place n t k (d + 1) a)
  | d, .ex s a => .ex s (place n t k (d + 1) a)

/-- The slot predicate symbol `n` becomes `p`. -/
def renameP (n p : String) : VE.Formula → VE.Formula
  | .top => .top
  | .bottom => .bottom
  | .unary q x => .unary (if q = n then p else q) x
  | .binary q x y => .binary (if q = n then p else q) x y
  | .eq x y => .eq x y
  | .not a => .not (renameP n p a)
  | .and a b => .and (renameP n p a) (renameP n p b)
  | .or a b => .or (renameP n p a) (renameP n p b)
  | .implies a b => .implies (renameP n p a) (renameP n p b)
  | .all s a => .all s (renameP n p a)
  | .ex s a => .ex s (renameP n p a)

/-- One row of 4.4's table at a position: a constant, the context variable `j` (`binder:<i>`, `j = |ctx| - 1 - i`),
    an assertive or presuppositional description over `σ`, a distributive plural, a predicate. -/
inductive Row
  | const (c : String)
  | binder (j : Nat)
  | assertive (σ : String) (Dr : VE.Formula)
  | presupposed (σ : String) (Dr : VE.Formula)
  | plural (cs : List String)
  | pred (p : String)
  deriving DecidableEq, Repr

def Row.apply (n : String) : Row → VE.Formula → VE.Formula
  | .const c, A => place n (fun _ => .const c) 0 0 A
  | .binder j, A => place n (fun d => .var (j + d)) 0 0 A
  | .assertive σ Dr, A => VE.Discourse.assertive σ Dr (place n .var 1 0 A)
  | .presupposed σ Dr, A => VE.Discourse.presupposed σ Dr (place n .var 1 0 A)
  | .plural cs, A => conj (cs.map fun c => place n (fun _ => .const c) 0 0 A)
  | .pred p, A => renameP n p A

/-- The row of mention `m` at a position with context `ctx`, or its 14.3 diagnostic. -/
def rowOf (E : VE.Environment) (ctx : List String) (m : Mention) : Except String Row :=
  let ill := "IllTypedTarget: " ++ m.id ++ ": " ++ targetText m.target
  match m.target.kind, m.target.name with
  | .predicate, some p => .ok (.pred p)
  | .document, _ => .error ("UnsupportedTarget: " ++ m.id ++ ": document")
  | .claim, _ => .error ("UnsupportedTarget: " ++ m.id ++ ": claim")
  | .entity, name =>
    if m.form == .definite then
      match m.restriction, m.reading, m.restriction.bind fun Dr => E.sorts.find? (Dr.check E [·]) with
      | some Dr, some .assertive, some σ => .ok (.assertive σ Dr)
      | some Dr, some .presuppositional, some σ => .ok (.presupposed σ Dr)
      | _, _, _ => .error ill
    else if m.form == .plural then
      match pluralMembers m.target with
      | some cs => .ok (.plural cs)
      | none => .error ill
    else match name with
      | some c =>
        if notBinder c then .ok (.const c)
        else match (c.drop 7).toNat? with
          | some i => if i < ctx.length then .ok (.binder (ctx.length - 1 - i))
              else .error ("WitnessEscape: " ++ m.id)
          | none => .error ill
      | none => .error ill
  | k, _ => .error ("TargetKindMismatch: " ++ m.id ++ ": " ++ formText m.form ++ ", " ++ kindText k)

/-- What resolution step 4's type check needs of a row beyond the rewritten formula's check; each conjunct is implied
    by that check whenever the slot occurs in the position, so it refuses nothing more. -/
def Row.typed (E : VE.Environment) (ctx : List String) : Row → Bool
  | .const c => (E.constants c).isSome
  | .binder j => j < ctx.length
  | .assertive σ Dr | .presupposed σ Dr => Dr.check E [σ]
  | .plural cs => cs.all fun c => (E.constants c).isSome
  | .pred _ => true

/-- The mentions whose slot occurs in `A`, in span order. -/
def slotsIn (ms : List Mention) (A : VE.Formula) : List Mention :=
  (ms.filter fun m => (symbolsOf A).contains (slotName m.id)).mergeSort
    fun a b => a.span.1 < b.span.1 || (a.span.1 == b.span.1 && a.span.2 ≤ b.span.2)

/-- The rows of a position's slots, in span order. -/
def rowsAt (E : VE.Environment) (ms : List Mention) (ctx : List String) (A : VE.Formula) :
    Except String (List (Mention × Row)) :=
  (slotsIn ms A).mapM fun m => (rowOf E ctx m).map (m, ·)

/-- The rewritten position: the slots taken in reverse span order, so the one written first is outermost. -/
def rewrite (xs : List (Mention × Row)) (A : VE.Formula) : VE.Formula :=
  xs.foldr (fun x B => x.2.apply (slotName x.1.id) B) A

/-! ## Resolution (14.3) -/

/-- A mention nested in another formula-producing mention of the unit: no separate slot (14.3 step 2, 1.4). -/
def nested (ms : List Mention) (m : Mention) : Bool :=
  ms.any fun o => o.span != m.span && o.span.1 ≤ m.span.1 && m.span.2 ≤ o.span.2

/-- Resolution step 2: each (outermost) mention has a slot in `c`, and each slot of `c` is a mention. -/
def slotCheck (E : VE.Environment) (ms : List Mention) (c : Content) : Except String Unit :=
  let syms := (positions E c).flatMap fun x => symbolsOf x.2
  match ms.find? (fun m => !nested ms m && !syms.contains (slotName m.id)),
      syms.find? (fun q => slotPrefix.isPrefixOf q && !ms.any (slotName ·.id == q)) with
  | some m, _ => .error ("MentionNotSlot: " ++ m.id)
  | none, some q => .error ("MentionNotSlot: " ++ q.drop slotPrefix.length)
  | none, none => .ok ()

/-- Resolution step 3 at every position, in `positions` order. -/
def resolveAll (E : VE.Environment) (ms : List Mention) :
    List (List String × VE.Formula) → Except String (List (List (Mention × Row) × VE.Formula))
  | [] => .ok []
  | (ctx, A) :: ps => do
    let xs ← rowsAt E ms ctx A
    let rs ← resolveAll E ms ps
    pure ((xs, rewrite xs A) :: rs)

/-- Resolution step 4: every rewritten position closed and well-typed in its context, else the first failure. -/
def checkAll (E : VE.Environment) (unit : String) :
    Nat → List (List String × VE.Formula) → List (List (Mention × Row) × VE.Formula) → Except String Unit
  | k, (ctx, _) :: ps, (xs, A) :: rs =>
    if A.check E ctx && xs.all (·.2.typed E ctx) then checkAll E unit (k + 1) ps rs
    else .error (match xs.head? with
      | some (m, _) => "IllTypedTarget: " ++ m.id ++ ": " ++ targetText m.target
      | none => "InvalidInput: " ++ unit ++ ": position " ++ toString k)
  | _, _, _ => .ok ()

/-- Resolution of a content's slots by the manifest's recorded targets (14.3). -/
def resolveContent (E : VE.Environment) (K : Manifest) (unit : String) (c : VE.Compose.Content) :
    Except String VE.Compose.Content :=
  match formulaMentions K unit with
  | [] => .ok c
  | ms => do
    slotCheck E ms c
    let rs ← resolveAll E ms (positions E c)
    checkAll E unit 0 (positions E c) rs
    match withPositions E c (rs.map (·.2)) with
    | some c' => .ok c'
    | none => .error ("InvalidInput: " ++ unit ++ ": positions")

/-! ## The intended meaning (4.4 at a position) -/

/-- `S` with constant `n` interpreted as `a`, and with relation `n` interpreted as `R`; nothing else changed. -/
def _root_.VE.Structure.withConstant (S : VE.Structure.{u}) (n : String) (a : S.Carrier) : VE.Structure.{u} :=
  { S with constant := fun c => if c = n then some a else S.constant c }
def _root_.VE.Structure.withRelation (S : VE.Structure.{u}) (n : String) (R : List S.Carrier → Prop) :
    VE.Structure.{u} :=
  { S with relation := fun q => if q = n then R else S.relation q }

/-- The position `A` with its slots interpreted directly, the first row outermost (4.4's table, row by row). -/
def slotMeaning (A : VE.Formula) : List (Mention × Row) → (S : VE.Structure.{u}) → VE.Valuation S → Prop
  | [], S, ρ => A.denote S ρ
  | (m, .const c) :: xs, S, ρ => ∃ a, S.constant c = some a ∧ slotMeaning A xs (S.withConstant (slotName m.id) a) ρ
  | (m, .binder j) :: xs, S, ρ => ∃ a, ρ[j]? = some a ∧ slotMeaning A xs (S.withConstant (slotName m.id) a) ρ
  | (m, .assertive σ Dr) :: xs, S, ρ => ∃ a, S.domain σ a ∧ Dr.denote S [a] ∧
      (∀ b, S.domain σ b → Dr.denote S [b] → b = a) ∧ slotMeaning A xs (S.withConstant (slotName m.id) a) ρ
  | (m, .presupposed σ Dr) :: xs, S, ρ => ∀ a, S.domain σ a → Dr.denote S [a] →
      slotMeaning A xs (S.withConstant (slotName m.id) a) ρ
  | (m, .plural cs) :: xs, S, ρ => ∀ c ∈ cs, ∃ a, S.constant c = some a ∧
      slotMeaning A xs (S.withConstant (slotName m.id) a) ρ
  | (m, .pred p) :: xs, S, ρ => slotMeaning A xs (S.withRelation (slotName m.id) (S.relation p)) ρ

/-- The intended meaning of position `k` of the content `c` as written (4.4 at a position, plan 2.8). -/
def IntendedAt (E : VE.Environment) (K : Manifest) (unit : String) (c : VE.Compose.Content) (k : Nat)
    (S : VE.Structure) (ρ : VE.Valuation S) : Prop :=
  match (positions E c)[k]? with
  | some (ctx, A) => match rowsAt E (formulaMentions K unit) ctx A with
    | .ok xs => slotMeaning A xs S ρ
    | .error _ => False
  | none => False

/-- (PC-11 reads it) One position's resolution, the position read as an asserted formula of the unit. -/
def resolveFormula (E : VE.Environment) (K : Manifest) (unit : String) (φ : VE.Formula) : Except String VE.Formula :=
  match resolveContent E K unit (.assertion φ) with
  | .ok (.assertion ψ) => .ok ψ
  | .ok _ => .error "InvalidInput: resolution changed the content kind"
  | .error e => .error e

/-! ## The steps of 14.3 around the fence compiler -/

/-- 14.3 step 1: an environment that declares a sort, predicate or constant named with `slotPrefix` is refused. -/
def reservedNames (environment : Lean.Json) : Except String Unit :=
  let v := environment.getObjValD "vocabulary"
  let names := ["sorts", "predicates", "constants"].flatMap fun key =>
    match v.getObjValD key with
    | .obj kvs => kvs.toList.map (·.1)
    | _ => []
  match names.find? (slotPrefix.isPrefixOf ·) with
  | some n => .error ("InvalidInput: reserved name " ++ n)
  | none => .ok ()

/-- 14.3 step 3: a header slot of mention `m` at argument `i` of `N`'s predicate is the binder `x_i`, and
    `x_i equals @ve__slot__<m>` is conjoined to the guard; only a declared constant (or pair member) fills it. -/
def headerSlot (E : VE.Environment) (m : Mention) (i : Nat) (N : VE.SoftNorms.SoftNode) :
    Except String VE.SoftNorms.SoftNode :=
  let ctx := nodeContext E N
  match m.target.kind, m.target.name with
  | .entity, some c =>
    if notBinder c && (E.constants c).isSome && i < ctx.length then
      let e := VE.Formula.eq (.var (ctx.length - 1 - i)) (.const (slotName m.id))
      .ok { N with guard := if N.guard = .top then e else .and N.guard e }
    else .error ("UnsupportedTarget: " ++ m.id ++ ": rule header")
  | _, _ => .error ("UnsupportedTarget: " ++ m.id ++ ": rule header")

/-- 14.3 step 4: a rule target in a header option is written into the node's `over`; it must name a norm unit. -/
def headerOver (rules : List String) (m : Mention) (N : VE.SoftNorms.SoftNode) :
    Except String VE.SoftNorms.SoftNode :=
  match m.target.kind, m.target.name with
  | .rule, some r => if rules.contains r then .ok { N with over := N.over ++ [r] } else .error ("UnknownRule: " ++ r)
  | k, _ => .error ("TargetKindMismatch: " ++ m.id ++ ": " ++ formText m.form ++ ", " ++ kindText k)

/-- 14.3 step 5: a mention inside a `rank`, party, decider or `soft` field (`fields`, spans of the fence text). -/
def softFields (K : Manifest) (unit : String) (fields : List (Nat × Nat)) : Except String Unit :=
  match (formulaMentions K unit).find? (fun m => fields.any fun f => f.1 ≤ m.span.1 && m.span.2 ≤ f.2) with
  | some m => .error ("UnsupportedTarget: " ++ m.id ++ ": soft")
  | none => .ok ()

/-- 14.3 step 6: a unit with a JSON content has no slot; `unrecorded` are its prose's unrecorded reference spans. -/
def jsonContent (K : Manifest) (unit : String) (unrecorded : List String) : Except String Unit :=
  match formulaMentions K unit, unrecorded with
  | m :: _, _ => .error ("MentionNotSlot: " ++ m.id)
  | [], s :: _ => .error ("UnrecordedSlot: " ++ unit ++ ": " ++ s)
  | [], [] => .ok ()

/-- A reading of a mention as the ambiguity diagnostic names it: its target, or `the <restriction symbols>`. -/
def readingText (m : Mention) : String :=
  match m.restriction with
  | some Dr => "the " ++ " ".intercalate (symbolsOf Dr)
  | none => targetText m.target

/-- 14.3 step 7, uniqueness: among the accessible readings of mention `m` (each `m` with another target, restriction
    or reading; accessibility and kind fit are 4.1(6)'s), at most one for which `resolveContent` succeeds. -/
def uniqueTarget (E : VE.Environment) (K : Manifest) (unit : String) (c : Content) (m : Mention)
    (accessible : List Mention) : Except String Unit :=
  let with_ (r : Mention) : Manifest := { K with mentions := K.mentions.map fun x => if x.id == m.id then r else x }
  let fits := ((accessible.filter fun r => (resolveContent E (with_ r) unit c).toBool).map readingText).eraseDups
  if fits.length ≤ 1 then .ok ()
  else .error ("AmbiguousReference: " ++ m.id ++ ": " ++ ", ".intercalate (fits.mergeSort fun a b => decide (a ≤ b)))

end VE.Discourse
