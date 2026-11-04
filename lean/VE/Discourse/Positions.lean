import VE.Discourse.WellFormed
import VE.Compose.Content

/-! # Formula positions, slots and their resolution (docs/spec/discourse.md 14.2, 14.3)

`positions E c` lists every formula of a `VE.Compose.Content` with the sorts of the variables free in it;
`withPositions` writes formulas back. Inside a fenced content a recorded formula-producing mention `m` stands as
the reserved constant or predicate `slotName m.id`; `resolveContent` rewrites each slot by its recorded target
(14.3 resolution steps 1 to 4) and type-checks every position. `IntendedAt` reads a position of the content as
written with each slot interpreted directly in the structure (4.4's table, one row per slot), and
`resolve_position_faithful` is their agreement. The steps of 14.3 that the composed path runs around the fence
compiler (1 and 3 to 7) are cmp-s4ab's; no route calls anything here before cmp-s4. -/
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
           recognition := l.recognition.map (nodeSet · ((fs.drop (optCount l.norm)).drop (optCount l.liberty))) }

def linesSet : List VE.Rights.SourceLine → List VE.Formula → List VE.Rights.SourceLine
  | [], _ => []
  | l :: ls, fs => lineSet l fs :: linesSet ls (((fs.drop (optCount l.norm)).drop (optCount l.liberty)).drop
      (optCount l.recognition))

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

/-- The mentions whose slot occurs in `A`, in span order (the slots of a position have disjoint spans). -/
def slotsIn (ms : List Mention) (A : VE.Formula) : List Mention :=
  let syms := symbolsOf A
  (ms.filter fun m => syms.contains (slotName m.id)).mergeSort fun a b => a.span.1 ≤ b.span.1

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
def slotCheck (ms : List Mention) (ps : List (List String × VE.Formula)) : Except String Unit :=
  let syms := ps.flatMap fun x => symbolsOf x.2
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
    let ps := positions E c
    slotCheck ms ps
    let rs ← resolveAll E ms ps
    checkAll E unit 0 ps rs
    match withPositions E c (rs.map (·.2)) with
    | some c' => .ok c'
    | none => .error ("InvalidInput: " ++ unit ++ ": positions")

/-! ## The intended meaning (4.4 at a position) -/

/-- `S` with constant `n` interpreted as `a`, and with relation `n` interpreted as `R`; nothing else changed. -/
def _root_.VE.Structure.withConstant (S : VE.Structure) (n : String) (a : S.Carrier) : VE.Structure :=
  { S with constant := fun c => if c = n then some a else S.constant c }
def _root_.VE.Structure.withRelation (S : VE.Structure) (n : String) (R : List S.Carrier → Prop) : VE.Structure :=
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

/-! ## Writing back what `positions` reads -/

theorem drop_app {α} {n : Nat} {l r : List α} (h : n = l.length) : (l ++ r).drop n = r := by
  subst h; simp
theorem split2 {α} (fs : List α) (a b : Nat) (h : fs.length = a + b) :
    ∃ x y, fs = x ++ y ∧ x.length = a ∧ y.length = b :=
  ⟨fs.take a, fs.drop a, (List.take_append_drop a fs).symm, by simp; omega, by simp; omega⟩

/-- `set` writes back what `pos` reads, from the front of the list, keeping every context. -/
def Fills {X : Type} (pos : X → List (List String × VE.Formula)) (set : X → List VE.Formula → X) : Prop :=
  ∀ x, (∀ r, set x ((pos x).map (·.2) ++ r) = x) ∧ ∀ fs r, fs.length = (pos x).length →
    (pos (set x (fs ++ r))).map (·.2) = fs ∧ (pos (set x (fs ++ r))).map (·.1) = (pos x).map (·.1) ∧
      ∀ r', set (set x (fs ++ r)) ((pos x).map (·.2) ++ r') = x

theorem fills_node (E : VE.Environment) : Fills (nodePositions E) nodeSet := by
  rintro ⟨⟨name, pred, sign, g, cs, over⟩, mode, rank, alt, ex, hard⟩
  cases ex with
  | none =>
    refine ⟨fun r => ?_, fun fs r hl => ?_⟩
    · simp [nodeSet, nodePositions, Function.comp_def]
    · simp [nodePositions] at hl
      obtain ⟨f, fs, rfl⟩ : ∃ f fs', fs = f :: fs' := by cases fs <;> simp_all
      simp at hl
      simp [nodeSet, nodePositions, nodeContext, hl, Function.comp_def, List.map_const']
  | some x =>
    obtain ⟨dec, suf, nec, fac⟩ := x
    refine ⟨fun r => ?_, fun fs r hl => ?_⟩
    · simp [nodeSet, nodePositions, excSet, Function.comp_def]
    · simp [nodePositions] at hl
      obtain ⟨f, fs, rfl⟩ : ∃ f fs', fs = f :: fs' := by cases fs <;> simp_all
      simp at hl
      obtain ⟨c1, fs, rfl, h1, hl⟩ := split2 fs _ _ hl
      obtain ⟨s1, n1, rfl, h2, h3⟩ := split2 fs _ _ hl
      simp [nodeSet, nodePositions, nodeContext, excSet, h1, h2, h3, Function.comp_def,
        List.map_const']

theorem optCount_eq (E : VE.Environment) (o : Option VE.SoftNorms.SoftNode) :
    optCount o = (o.toList.flatMap (nodePositions E)).length := by
  rcases o with _ | ⟨N⟩
  · rfl
  · cases h : N.exception <;> simp [optCount, nodePositions, h] <;> omega

theorem fills_opt (E : VE.Environment) :
    Fills (fun (o : Option VE.SoftNorms.SoftNode) => o.toList.flatMap (nodePositions E))
      (fun o fs => o.map (nodeSet · fs)) := by
  rintro (_ | ⟨N⟩)
  · exact ⟨fun _ => rfl, fun fs r h => by simp_all⟩
  · obtain ⟨h1, h2⟩ := fills_node E N
    refine ⟨fun r => by simpa using h1 r, fun fs r h => ?_⟩
    obtain ⟨a, b, c⟩ := h2 fs r (by simpa using h)
    exact ⟨by simpa using a, by simpa using b, fun r' => by simpa using c r'⟩

theorem fills_line (E : VE.Environment) : Fills (linePositions E) lineSet := by
  rintro ⟨kind, n, li, re, fan, hs, cites⟩
  obtain ⟨n1, n2⟩ := fills_opt E n
  obtain ⟨l1, l2⟩ := fills_opt E li
  obtain ⟨r1, r2⟩ := fills_opt E re
  simp only at n1 n2 l1 l2 r1 r2
  refine ⟨fun r => ?_, fun fs r h => ?_⟩
  · simp only [lineSet, linePositions, List.flatMap_append, List.map_append, List.append_assoc]
    rw [drop_app (by rw [optCount_eq E, List.length_map]), drop_app (by rw [optCount_eq E, List.length_map]),
      n1, l1, r1]
  · simp only [linePositions, List.flatMap_append, List.length_append, Nat.add_assoc] at h
    obtain ⟨a, fs, rfl, ha, h⟩ := split2 fs _ _ h
    obtain ⟨b, c, rfl, hb, hc⟩ := split2 fs _ _ h
    obtain ⟨na, nb, nc⟩ := n2 a (b ++ c ++ r) ha
    obtain ⟨la, lb, lc⟩ := l2 b (c ++ r) hb
    obtain ⟨ra, rb, rc⟩ := r2 c r hc
    have ea : ∀ {X : List VE.Formula}, (a ++ X).drop (optCount n) = X := drop_app (by rw [optCount_eq E, ha])
    have eb : ∀ {X : List VE.Formula}, (b ++ X).drop (optCount li) = X := drop_app (by rw [optCount_eq E, hb])
    simp only [List.append_assoc] at na nb nc la lb lc ra rb rc
    have ca : optCount (n.map (nodeSet · (a ++ (b ++ (c ++ r))))) = optCount n := by
      have := congrArg List.length na; rw [List.length_map] at this; rw [optCount_eq E, this, ha, optCount_eq E]
    have cb : optCount (li.map (nodeSet · (b ++ (c ++ r)))) = optCount li := by
      have := congrArg List.length la; rw [List.length_map] at this; rw [optCount_eq E, this, hb, optCount_eq E]
    have fa : ∀ {X : List VE.Formula}, (((n.toList.flatMap (nodePositions E)).map (·.2)) ++ X).drop (optCount n) = X :=
      drop_app (by rw [optCount_eq E, List.length_map])
    have fb : ∀ {X : List VE.Formula}, (((li.toList.flatMap (nodePositions E)).map (·.2)) ++ X).drop (optCount li) = X :=
      drop_app (by rw [optCount_eq E, List.length_map])
    simp only [lineSet, linePositions, List.append_assoc, ea, eb, List.flatMap_append, List.map_append, na, nb, nc,
      la, lb, ra, rb, ca, cb, fa, fb, lc, rc, and_self, implies_true]

theorem drop_line (E : VE.Environment) (l : VE.Rights.SourceLine) (X : List VE.Formula) :
    ((X.drop (optCount l.norm)).drop (optCount l.liberty)).drop (optCount l.recognition) =
      X.drop (linePositions E l).length := by
  simp only [List.drop_drop, linePositions, List.flatMap_append, List.length_append, optCount_eq E]

theorem fills_lines (E : VE.Environment) :
    Fills (fun (ls : List VE.Rights.SourceLine) => ls.flatMap (linePositions E)) linesSet := by
  intro ls
  induction ls with
  | nil => exact ⟨fun _ => rfl, fun fs r h => by simp_all [linesSet]⟩
  | cons l ls ih =>
    obtain ⟨h1, h2⟩ := fills_line E l
    obtain ⟨i1, i2⟩ := ih
    simp only [List.flatMap_cons, List.map_append, List.length_append, List.append_assoc] at i1 i2 ⊢
    refine ⟨fun r => ?_, fun fs r h => ?_⟩
    · simp only [linesSet, drop_line E, h1, drop_app (List.length_map _).symm, i1]
    · obtain ⟨a, b, rfl, ha, hb⟩ := split2 fs _ _ h
      obtain ⟨a1, a2, a3⟩ := h2 a (b ++ r) ha
      obtain ⟨b1, b2, b3⟩ := i2 b r hb
      have ca : (linePositions E (lineSet l (a ++ (b ++ r)))).length = (linePositions E l).length := by
        have := congrArg List.length a1; simp at this; omega
      simp only [List.append_assoc, linesSet, drop_line E, drop_app ha.symm, ca, drop_app (List.length_map _).symm,
        List.flatMap_cons, List.map_append, a1, a2, a3, b1, b2, b3, implies_true, and_self]

theorem fills_content (E : VE.Environment) : Fills (positions E) contentSet := by
  rintro (φ | N | R | ⟨rn, ls⟩ | L)
  · refine ⟨fun r => rfl, fun fs r h => ?_⟩
    obtain ⟨f, rfl⟩ : ∃ f, fs = [f] := by
      match fs, h with | [f], _ => exact ⟨f, rfl⟩
    simp [positions, contentSet]
  · obtain ⟨h1, h2⟩ := fills_node E N
    exact ⟨fun r => by simp [positions, contentSet, h1], fun fs r h => by simpa [positions, contentSet] using h2 fs r h⟩
  · obtain ⟨name, holder, g, ls⟩ := R
    obtain ⟨i1, i2⟩ := fills_lines E ls
    simp only at i1 i2
    refine ⟨fun r => by simp [positions, contentSet, i1], fun fs r h => ?_⟩
    obtain ⟨f, fs, rfl⟩ : ∃ f fs', fs = f :: fs' := by cases fs <;> simp_all [positions]
    simp only [positions, List.length_cons, Nat.add_right_cancel_iff] at h
    obtain ⟨b1, b2, b3⟩ := i2 fs r h
    simp [positions, contentSet, b1, b2, b3]
  · obtain ⟨i1, i2⟩ := fills_lines E ls
    exact ⟨fun r => by simp [positions, contentSet, i1], fun fs r h => by simpa [positions, contentSet] using i2 fs r h⟩
  · exact ⟨fun _ => rfl, fun fs r h => by simp_all [positions, contentSet]⟩

/-- `withPositions` writes back what `positions` reads. -/
theorem positions_withPositions (E : VE.Environment) (c : VE.Compose.Content) (fs : List VE.Formula)
    (h : fs.length = (positions E c).length) :
    ∃ c', withPositions E c fs = some c' ∧ (positions E c').map (·.2) = fs ∧
      (positions E c').map (·.1) = (positions E c).map (·.1) := by
  obtain ⟨a, b, -⟩ := (fills_content E c).2 fs [] h
  simp only [List.append_nil] at a b
  exact ⟨_, by simp [withPositions, h], a, b⟩
theorem withPositions_self (E : VE.Environment) (c : VE.Compose.Content) :
    withPositions E c ((positions E c).map (·.2)) = some c := by
  simpa [withPositions] using (fills_content E c).1 []

/-! ## Rewriting a slot denotes interpreting it -/

theorem placeT_denote (S : VE.Structure.{u}) (n : String) (t : Nat → VE.Term) (a : S.Carrier)
    (ext ρ π : VE.Valuation S) (ht : (t π.length).denote S (π ++ ext ++ ρ) = some a) (x : VE.Term) :
    (placeT n t ext.length π.length x).denote S (π ++ ext ++ ρ) = x.denote (S.withConstant n a) (π ++ ρ) := by
  cases x with
  | var i =>
    by_cases hi : i < π.length
    · simp only [placeT, hi, if_true, VE.Term.denote]
      rw [List.append_assoc, List.getElem?_append_left hi]; exact (List.getElem?_append_left hi).symm
    · simp only [placeT, hi, if_false, VE.Term.denote]
      rw [List.append_assoc, List.getElem?_append_right (by omega), List.getElem?_append_right (by omega)]
      refine Eq.trans ?_ (List.getElem?_append_right (l₁ := π) (l₂ := ρ) (by omega)).symm
      congr 1; omega
  | const c =>
    by_cases hc : c = n
    · subst hc; simp only [placeT, if_true]; rw [ht]; simp [VE.Term.denote, VE.Structure.withConstant]
    · simp [placeT, VE.Term.denote, VE.Structure.withConstant, hc]

theorem place_denote (S : VE.Structure.{u}) (n : String) (t : Nat → VE.Term) (a : S.Carrier) (ext ρ : VE.Valuation S)
    (ht : ∀ π : VE.Valuation S, (t π.length).denote S (π ++ ext ++ ρ) = some a) :
    ∀ (A : VE.Formula) (π : VE.Valuation S),
      (place n t ext.length π.length A).denote S (π ++ ext ++ ρ) ↔ A.denote (S.withConstant n a) (π ++ ρ)
  | .top, _ | .bottom, _ => Iff.rfl
  | .unary p x, π => by
    simp only [place, VE.Formula.denote, placeT_denote S n t a ext ρ π (ht π)]; rfl
  | .binary p x y, π => by
    simp only [place, VE.Formula.denote, placeT_denote S n t a ext ρ π (ht π)]; rfl
  | .eq x y, π => by
    simp only [place, VE.Formula.denote, placeT_denote S n t a ext ρ π (ht π)]; rfl
  | .not A, π => not_congr (place_denote S n t a ext ρ ht A π)
  | .and A B, π => and_congr (place_denote S n t a ext ρ ht A π) (place_denote S n t a ext ρ ht B π)
  | .or A B, π => or_congr (place_denote S n t a ext ρ ht A π) (place_denote S n t a ext ρ ht B π)
  | .implies A B, π => imp_congr (place_denote S n t a ext ρ ht A π) (place_denote S n t a ext ρ ht B π)
  | .all s A, π => forall_congr' fun v => imp_congr_right fun _ => place_denote S n t a ext ρ ht A (v :: π)
  | .ex s A, π => exists_congr fun v => and_congr_right fun _ => place_denote S n t a ext ρ ht A (v :: π)

theorem place_const (S : VE.Structure.{u}) (n c : String) (a : S.Carrier) (ρ : VE.Valuation S)
    (h : S.constant c = some a) (B : VE.Formula) :
    (place n (fun _ => .const c) 0 0 B).denote S ρ ↔ B.denote (S.withConstant n a) ρ :=
  place_denote S n (fun _ => .const c) a [] ρ (fun _ => h) B []

theorem place_binder (S : VE.Structure.{u}) (n : String) (j : Nat) (a : S.Carrier) (ρ : VE.Valuation S)
    (h : ρ[j]? = some a) (B : VE.Formula) :
    (place n (fun d => .var (j + d)) 0 0 B).denote S ρ ↔ B.denote (S.withConstant n a) ρ :=
  place_denote S n (fun d => .var (j + d)) a [] ρ (fun π => by
    simp only [VE.Term.denote, List.append_nil]
    rw [List.getElem?_append_right (by omega)]; simpa using h) B []

theorem place_var (S : VE.Structure.{u}) (n : String) (a : S.Carrier) (ρ : VE.Valuation S) (B : VE.Formula) :
    (place n .var 1 0 B).denote S (a :: ρ) ↔ B.denote (S.withConstant n a) ρ :=
  place_denote S n .var a [a] ρ (fun π => by simp [VE.Term.denote]) B []

theorem renameP_denote (S : VE.Structure.{u}) (n p : String) : ∀ (A : VE.Formula) (ρ : VE.Valuation S),
    (renameP n p A).denote S ρ ↔ A.denote (S.withRelation n (S.relation p)) ρ
  | .top, _ | .bottom, _ | .eq _ _, _ => Iff.rfl
  | .unary q x, ρ => by
    by_cases h : q = n <;> simp [renameP, VE.Formula.denote, VE.Structure.withRelation, h] <;> rfl
  | .binary q x y, ρ => by
    by_cases h : q = n <;> simp [renameP, VE.Formula.denote, VE.Structure.withRelation, h] <;> rfl
  | .not A, ρ => not_congr (renameP_denote S n p A ρ)
  | .and A B, ρ => and_congr (renameP_denote S n p A ρ) (renameP_denote S n p B ρ)
  | .or A B, ρ => or_congr (renameP_denote S n p A ρ) (renameP_denote S n p B ρ)
  | .implies A B, ρ => imp_congr (renameP_denote S n p A ρ) (renameP_denote S n p B ρ)
  | .all s A, ρ => forall_congr' fun v => imp_congr_right fun _ => renameP_denote S n p A (v :: ρ)
  | .ex s A, ρ => exists_congr fun v => and_congr_right fun _ => renameP_denote S n p A (v :: ρ)

theorem restriction_at {E : VE.Environment} {σ : String} {Dr : VE.Formula} (h : Dr.check E [σ] = true)
    (S : VE.Structure.{u}) (a : S.Carrier) (ρ : VE.Valuation S) : Dr.denote S (a :: ρ) ↔ Dr.denote S [a] :=
  denote_prefix Dr [σ] _ _ ((VE.check_iff_wellFormed E [σ] Dr).mp h) fun i hi => by
    simp at hi; subst hi; rfl

/-- The rewritten position denotes the slots interpreted row by row. -/
theorem rewrite_denote (E : VE.Environment) (ctx : List String) (A : VE.Formula) :
    ∀ (xs : List (Mention × Row)) (S : VE.Structure.{u}) (ρ : VE.Valuation S),
      xs.all (·.2.typed E ctx) = true → (∀ c, (E.constants c).isSome → (S.constant c).isSome) →
      (∀ j < ctx.length, ∃ a, ρ[j]? = some a) → ((rewrite xs A).denote S ρ ↔ slotMeaning A xs S ρ)
  | [], _, _, _, _, _ => Iff.rfl
  | (m, r) :: xs, S, ρ, ht, hS, hρ => by
    simp only [List.all_cons, Bool.and_eq_true] at ht
    have hC : ∀ a c, (E.constants c).isSome → ((S.withConstant (slotName m.id) a).constant c).isSome := by
      intro a c hc; simp only [VE.Structure.withConstant]; split <;> simp [hS c hc]
    have ih := fun a => rewrite_denote E ctx A xs (S.withConstant (slotName m.id) a) ρ ht.2 (hC a) hρ
    change (r.apply (slotName m.id) (rewrite xs A)).denote S ρ ↔ _
    cases r with
    | const c =>
      obtain ⟨a, ha⟩ := Option.isSome_iff_exists.mp (hS c (by simpa [Row.typed] using ht.1))
      simp only [Row.apply, place_const S _ c a ρ ha, ih, slotMeaning, ha, Option.some.injEq, exists_eq_left']
    | binder j =>
      obtain ⟨a, ha⟩ := hρ j (by simpa [Row.typed] using ht.1)
      simp only [Row.apply, place_binder S _ j a ρ ha, ih, slotMeaning, ha, Option.some.injEq, exists_eq_left']
    | assertive σ Dr =>
      have hD := restriction_at (by simpa [Row.typed] using ht.1) S
      simp only [Row.apply, VE.Discourse.assertive, VE.Discourse.assertiveAt, VE.Formula.denote, place_var, ih,
        slotMeaning, hD, VE.Term.denote, List.getElem?_cons_zero, List.getElem?_cons_succ, Option.some.injEq]
      exact exists_congr fun a => and_congr_right fun _ => and_congr_right fun _ => and_congr_left fun _ =>
        forall_congr' fun b => imp_congr_right fun _ => imp_congr_right fun _ =>
          ⟨fun ⟨_, h1, h2⟩ => h1.trans h2.symm, fun h => ⟨a, h, rfl⟩⟩
    | presupposed σ Dr =>
      have hD := restriction_at (by simpa [Row.typed] using ht.1) S
      simp only [Row.apply, VE.Discourse.presupposed, VE.Formula.denote, place_var, ih, slotMeaning, hD]
    | plural cs =>
      have hcs : ∀ c ∈ cs, (E.constants c).isSome := by simpa [Row.typed] using ht.1
      simp only [Row.apply, conj_denote_at, List.forall_mem_map, slotMeaning]
      refine forall₂_congr fun c hc => ?_
      obtain ⟨a, ha⟩ := Option.isSome_iff_exists.mp (hS c (hcs c hc))
      simp only [place_const S _ c a ρ ha, ih, ha, Option.some.injEq, exists_eq_left']
    | pred p =>
      simp only [Row.apply, renameP_denote, slotMeaning]
      exact rewrite_denote E ctx A xs (S.withRelation (slotName m.id) (S.relation p)) ρ ht.2 hS hρ

/-! ## Resolution's steps -/

theorem resolveAll_ok (E : VE.Environment) (ms : List Mention) :
    ∀ (ps : List (List String × VE.Formula)) (rs : List (List (Mention × Row) × VE.Formula)),
      resolveAll E ms ps = .ok rs → rs.length = ps.length ∧
        ∀ (k : Nat) (ctx : List String) (A : VE.Formula), ps[k]? = some (ctx, A) →
        ∃ xs, rowsAt E ms ctx A = .ok xs ∧ rs[k]? = some (xs, rewrite xs A)
  | [], rs, h => by cases h; simp
  | (ctx, A) :: ps, rs, h => by
    simp only [resolveAll, bind, Except.bind] at h
    cases hx : rowsAt E ms ctx A with
    | error e => simp [hx] at h
    | ok xs =>
      cases hr : resolveAll E ms ps with
      | error e => simp [hx, hr] at h
      | ok rs' =>
        simp only [hx, hr, pure, Except.pure, Except.ok.injEq] at h
        subst h
        obtain ⟨hl, hk⟩ := resolveAll_ok E ms ps rs' hr
        refine ⟨by simp [hl], fun k c' A' hk' => ?_⟩
        cases k with
        | zero => simp at hk'; obtain ⟨rfl, rfl⟩ := hk'; exact ⟨xs, hx, rfl⟩
        | succ k => simpa using hk k c' A' (by simpa using hk')

theorem checkAll_ok (E : VE.Environment) (u : String) :
    ∀ (k : Nat) (ps : List (List String × VE.Formula)) (rs : List (List (Mention × Row) × VE.Formula)),
      checkAll E u k ps rs = .ok () → ∀ (i : Nat) (ctx : List String) (A : VE.Formula) (xs : List (Mention × Row))
        (A' : VE.Formula), ps[i]? = some (ctx, A) → rs[i]? = some (xs, A') →
        A'.check E ctx = true ∧ xs.all (·.2.typed E ctx) = true
  | k, (ctx, A) :: ps, (xs, A') :: rs, h, i, ctx', B, xs', B', hp, hr => by
    simp only [checkAll] at h
    split at h
    · rename_i hc
      cases i with
      | zero =>
        simp at hp hr; obtain ⟨rfl, rfl⟩ := hp; obtain ⟨rfl, rfl⟩ := hr
        simpa using hc
      | succ i => exact checkAll_ok E u (k + 1) ps rs h i ctx' B xs' B' (by simpa using hp) (by simpa using hr)
    · cases h
  | _, [], _, _, i, _, _, _, _, hp, _ => by simp at hp
  | _, _ :: _, [], _, i, _, _, _, _, _, hr => by simp at hr

/-- What a successful resolution is: the identity, or every position rewritten, checked and written back. -/
theorem resolve_ok (E : VE.Environment) (K : Manifest) (u : String) (c c' : VE.Compose.Content)
    (h : resolveContent E K u c = .ok c') :
    (formulaMentions K u = [] ∧ c' = c) ∨ (formulaMentions K u ≠ [] ∧ ∃ rs,
      resolveAll E (formulaMentions K u) (positions E c) = .ok rs ∧
      checkAll E u 0 (positions E c) rs = .ok () ∧ c' = contentSet c (rs.map (·.2)) ∧
      rs.length = (positions E c).length) := by
  cases hm : formulaMentions K u with
  | nil => simp only [resolveContent, hm, Except.ok.injEq] at h; exact .inl ⟨rfl, h.symm⟩
  | cons m ms =>
    refine .inr ⟨by simp, ?_⟩
    simp only [resolveContent, hm, bind, Except.bind] at h
    cases hs : slotCheck (m :: ms) (positions E c) with
    | error e => simp [hs] at h
    | ok _ =>
      cases hr : resolveAll E (m :: ms) (positions E c) with
      | error e => simp [hs, hr] at h
      | ok rs =>
        cases hc : checkAll E u 0 (positions E c) rs with
        | error e => simp [hs, hr, hc] at h
        | ok _ =>
          have hl := (resolveAll_ok E _ _ rs hr).1
          simp only [hs, hr, hc, withPositions, List.length_map, hl, if_true, Except.ok.injEq] at h
          exact ⟨rs, rfl, hc, h.symm, hl⟩

/-- A position of a resolved content: the written position rewritten by its rows, closed and typed. -/
theorem resolved_at (E : VE.Environment) (u : String) (ms : List Mention) (c : VE.Compose.Content)
    (rs : List (List (Mention × Row) × VE.Formula)) (hr : resolveAll E ms (positions E c) = .ok rs)
    (hc : checkAll E u 0 (positions E c) rs = .ok ()) (hl : rs.length = (positions E c).length)
    (k : Nat) (ctx : List String) (A : VE.Formula)
    (hk : (positions E (contentSet c (rs.map (·.2))))[k]? = some (ctx, A)) :
    ∃ A₀ xs, (positions E c)[k]? = some (ctx, A₀) ∧ rowsAt E ms ctx A₀ = .ok xs ∧ A = rewrite xs A₀ ∧
      A.check E ctx = true ∧ xs.all (·.2.typed E ctx) = true := by
  obtain ⟨f1, f2, -⟩ := (fills_content E c).2 (rs.map (·.2)) [] (by simp [hl])
  simp only [List.append_nil] at f1 f2
  have h1 : ((positions E c).map (·.1))[k]? = some ctx := by rw [← f2]; simp [hk]
  have h2 : (rs.map (·.2))[k]? = some A := by rw [← f1]; simp [hk]
  simp only [List.getElem?_map] at h1 h2
  obtain ⟨⟨ctx₀, A₀⟩, hp, hctx⟩ := Option.map_eq_some_iff.mp h1
  simp only at hctx; subst hctx
  obtain ⟨xs, hx, hrk⟩ := (resolveAll_ok E ms _ rs hr).2 k ctx₀ A₀ hp
  rw [hrk] at h2; simp only [Option.map_some, Option.some.injEq] at h2; subst h2
  obtain ⟨hch, hty⟩ := checkAll_ok E u 0 _ rs hc k ctx₀ A₀ xs _ hp hrk
  exact ⟨A₀, xs, hp, hx, rfl, hch, hty⟩

theorem contentSet_declared (c : VE.Compose.Content) (fs : List VE.Formula) :
    (contentSet c fs).kind = c.kind ∧ (contentSet c fs).declared = c.declared := by
  have hl : ∀ ls fs, (linesSet ls fs).flatMap VE.Compose.lineRuleNames = ls.flatMap VE.Compose.lineRuleNames := by
    intro ls; induction ls with
    | nil => intro; rfl
    | cons l ls ih =>
      intro fs
      obtain ⟨_, n, li, re, _, _, _⟩ := l
      cases n <;> cases li <;> cases re <;> simp [linesSet, lineSet, VE.Compose.lineRuleNames, ih, nodeSet]
  cases c <;> simp [contentSet, VE.Compose.Content.kind, VE.Compose.Content.declared, hl, nodeSet]

/-! ## The theorems of 14.3 -/

/-- Identity when unused (plan rule 5): a unit with no formula-producing mention keeps its content. -/
theorem resolve_identity (E : VE.Environment) (K : Manifest) (u : String) (c : VE.Compose.Content)
    (h : formulaMentions K u = []) : resolveContent E K u c = .ok c := by
  simp [resolveContent, h]

/-- Position-wise faithfulness: discourse 9.3's `elaborate_faithful` under the position's context instead of the
    empty one. -/
theorem resolve_position_faithful (E : VE.Environment) (K : Manifest) (u : String) (c c' : VE.Compose.Content)
    (h : resolveContent E K u c = .ok c') (k : Nat) (ctx : List String) (A : VE.Formula)
    (hk : (positions E c')[k]? = some (ctx, A)) (S : VE.Structure) (hS : S.Admissible E)
    (ρ : VE.Valuation S) (hρ : VE.Valuation.Typed S ctx ρ) :
    A.denote S ρ ↔ IntendedAt E K u c k S ρ := by
  rcases resolve_ok E K u c c' h with ⟨hm, rfl⟩ | ⟨_, rs, hr, hc, rfl, hl⟩
  · simp [IntendedAt, hk, rowsAt, hm, slotsIn, slotMeaning, pure, Except.pure]
  · obtain ⟨A₀, xs, hp, hx, rfl, -, hty⟩ := resolved_at E u _ c rs hr hc hl k ctx A hk
    simp only [IntendedAt, hp, hx]
    refine rewrite_denote E ctx A₀ xs S ρ hty (fun c hc => ?_) (fun j hj => ?_)
    · obtain ⟨s, hs⟩ := Option.isSome_iff_exists.mp hc
      obtain ⟨v, hv, -⟩ := hS.1 c s hs
      simp [hv]
    · obtain ⟨v, hv, -⟩ := hρ j ctx[j] (by simp [hj])
      exact ⟨v, hv⟩

/-- A resolution that rewrote something yields closed, well-typed positions. -/
theorem resolve_typed (E : VE.Environment) (K : Manifest) (u : String) (c c' : VE.Compose.Content)
    (h : resolveContent E K u c = .ok c') (hm : formulaMentions K u ≠ []) :
    ∀ x ∈ positions E c', x.2.check E x.1 = true := by
  rcases resolve_ok E K u c c' h with ⟨hm', -⟩ | ⟨_, rs, hr, hc, rfl, hl⟩
  · exact absurd hm' hm
  · intro ⟨ctx, A⟩ hx
    obtain ⟨k, hk⟩ := List.getElem?_of_mem hx
    obtain ⟨_, _, -, -, -, hch, -⟩ := resolved_at E u _ c rs hr hc hl k ctx A hk
    exact hch

/-- No new symbols: every symbol of a resolved position is declared in `E` or was already a symbol of the
    content as written other than a slot name; no witness constant, no choice function, no fresh predicate. -/
theorem resolve_no_new_symbols (E : VE.Environment) (K : Manifest) (u : String) (c c' : VE.Compose.Content)
    (h : resolveContent E K u c = .ok c') :
    ∀ x ∈ positions E c', ∀ q ∈ symbolsOf x.2,
      DeclaredSymbol E q ∨
        ((∃ y ∈ positions E c, q ∈ symbolsOf y.2) ∧ (slotPrefix.isPrefixOf q = true → formulaMentions K u = [])) := by
  intro x hx q hq
  by_cases hm : formulaMentions K u = []
  · rw [resolve_identity E K u c hm, Except.ok.injEq] at h; subst h
    exact .inr ⟨⟨x, hx, hq⟩, fun _ => hm⟩
  · exact .inl (symbolsOf_declared x.2 x.1
      ((VE.check_iff_wellFormed E x.1 x.2).mp (resolve_typed E K u c c' h hm x hx)) q hq)

/-- Only positions change: the kind, the declared names and every other field are kept. -/
theorem resolve_keeps_shape (E : VE.Environment) (K : Manifest) (u : String) (c c' : VE.Compose.Content)
    (h : resolveContent E K u c = .ok c') :
    c'.kind = c.kind ∧ c'.declared = c.declared ∧
      (positions E c').map (·.1) = (positions E c).map (·.1) ∧
      withPositions E c' ((positions E c).map (·.2)) = some c := by
  rcases resolve_ok E K u c c' h with ⟨-, rfl⟩ | ⟨_, rs, -, -, rfl, hl⟩
  · exact ⟨rfl, rfl, rfl, withPositions_self E _⟩
  · obtain ⟨f1, f2, f3⟩ := (fills_content E c).2 (rs.map (·.2)) [] (by simp [hl])
    simp only [List.append_nil] at f1 f2 f3
    obtain ⟨hk, hd⟩ := contentSet_declared c (rs.map (·.2))
    refine ⟨hk, hd, f2, ?_⟩
    have hlen : ((positions E c).map (·.2)).length = (positions E (contentSet c (rs.map (·.2)))).length := by
      rw [← List.length_map (f := (·.2)) (as := positions E (contentSet c _)), f1]; simp [hl]
    simp only [withPositions, hlen, if_true]
    simpa using f3 []

theorem resolveFormula_assertion (E : VE.Environment) (K : Manifest) (unit : String) (φ ψ : VE.Formula) :
    resolveFormula E K unit φ = .ok ψ ↔ resolveContent E K unit (.assertion φ) = .ok (.assertion ψ) := by
  unfold resolveFormula
  split <;> simp_all
end VE.Discourse
