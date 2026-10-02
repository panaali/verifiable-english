import VE.Compose.Content
import VE.Rights.Route

/-! Reading candidates with content and a candidate's document (docs/spec/composition-s1.md 1.1 to 1.4, 4.2 to
4.4, 8.2).

A `Doc` is the chain, the frame (the environment without any unit) and the items in source order: a fixed
content, a fixed bar, or an open reading set. `Attached D u t` says that fixed unit `u` uses a name declared by
set `t`, directly or through other fixed units; `attached` computes it (`attached_iff`). `one D s i` is the
ordinary chain document of the fixed units that depend on no other open set and candidate `i` of set `s`,
assembled as the rights decoder assembles units (`place` is `VE.Rights.Wire.addUnit`'s fold step on decoded
units). `WellFormedDoc` is admission without separation: reserved names, distinct declarations, closure, single
attachment, the chain's well-formedness of `free D` and of every `one D s i`. Nothing here changes a frozen
file: `Content` and `Content.declared` are S0's. -/
namespace VE.Readings
open VE.Norms (Regulated Sat tupleVal envAt size)
open VE.SoftNorms (SoftNode SoftDoc soften WellFormedSoft ValueSoft)
open VE.Rights (RightsDoc Bar SourceLine correlate limPremises WellFormedRights sourceLines)
open VE.Compose (Content)
universe u

inductive Chain | norms | soft | rights
  deriving DecidableEq, Repr
def chainOf (ps : List String) : Chain :=
  if ps.contains "rights@0" then .rights else if ps.contains "soft-norms@0" then .soft else .norms

structure Candidate where
  id : String
  /-- `none`: pending, or a candidate S1 does not elaborate (a quantity, a bar, a composite kind). -/
  content : Option Content
  /-- The `cites` of a norm content; `[]` otherwise. -/
  cites : List (String × List String)
  labels : List (String × String)
  deriving DecidableEq, Repr
structure ReadingSet where
  id : String
  unit : String
  version : Nat
  candidates : List Candidate
  deriving DecidableEq, Repr
/-- A unit in source order (1.2). -/
inductive Item
  | fixed (unit : String) (c : Content) (cites : List (String × List String))
  | bar (unit : String) (b : Bar)
  | set (R : ReadingSet)
  deriving DecidableEq, Repr
structure Coupling where
  id : String
  axis : String
  sets : List (String × Nat)
structure Narrowing where
  id : String
  set : String
  version : Nat
  keeps : List String
structure Doc where
  chain : Chain
  /-- E, literals, the soft block, regulated predicates, definitions, the rights block, the source unit ids; no
      rule, right, limitation or bar, and `sourceOrder := some []`. -/
  frame : RightsDoc
  items : List Item
  couplings : List Coupling
  narrowings : List Narrowing

def Doc.sets (D : Doc) : List ReadingSet := D.items.filterMap (fun | .set R => some R | _ => none)
def candidate (D : Doc) (s : String) (i : Nat) : Option Candidate :=
  (D.sets.find? (·.id == s)).bind (·.candidates[i]?)

/-! ## Names (1.3) -/

def nodeUses (N : SoftNode) : List (String × String) := N.over.map (fun n => ("rule", n))
def citeUses (cs : List (String × List String)) : List (String × String) :=
  cs.filterMap (fun kv => if kv.1.startsWith "over:" then some ("rule", kv.1.drop 5)
                          else if kv.1.startsWith "narrows:" then some ("rule", kv.1.drop 8) else none)
def lineUses (S : SourceLine) : List (String × String) :=
  (S.norm.toList ++ S.liberty.toList ++ S.recognition.toList).flatMap nodeUses ++ citeUses S.cites
def uses (c : Content) (cites : List (String × List String)) : List (String × String) :=
  match c with
  | .assertion _ => []
  | .norm N => nodeUses N ++ citeUses cites
  | .right R => R.lines.flatMap lineUses
  | .rightLines r ls => ("right", r) :: ls.flatMap lineUses
  | .limitation L => (L.scope.getD []).map (fun r => ("right", r))

def declaredBy (R : ReadingSet) : List (String × String) :=
  (R.candidates.filterMap (·.content)).flatMap (·.declared)
def interfaceOf (R : ReadingSet) : List (String × String) :=
  (declaredBy R).filter (fun n => R.candidates.all (fun a => (a.content.map (·.declared.contains n)).getD false))
/-- Fixed unit u is attached to set t (1.3): the least such relation. -/
inductive Attached (D : Doc) : String → String → Prop
  | direct {u : String} {c : Content} {cs : List (String × List String)} {t : String}
      (hu : Item.fixed u c cs ∈ D.items) (n : String × String) (hn : n ∈ uses c cs)
      (R : ReadingSet) (hR : R ∈ D.sets) (ht : R.id = t) (hd : n ∈ declaredBy R) : Attached D u t
  | step {u u' : String} {c c' : Content} {cs cs' : List (String × List String)} {t : String}
      (hu : Item.fixed u c cs ∈ D.items) (hu' : Item.fixed u' c' cs' ∈ D.items)
      (n : String × String) (hn : n ∈ uses c cs) (hd : n ∈ c'.declared) (h : Attached D u' t) : Attached D u t

/-! ### Computing `Attached` -/

/-- The fixed units in source order: unit, content, cites. -/
def fixedUnits (D : Doc) : List (String × Content × List (String × List String)) :=
  D.items.filterMap (fun | .fixed u c cs => some (u, c, cs) | _ => none)
def fixedNames (D : Doc) : List String := (fixedUnits D).map (·.1)
/-- The names the fixed units called `u` use. -/
def usesOfUnit (D : Doc) (u : String) : List (String × String) :=
  (fixedUnits D).flatMap (fun x => if x.1 == u then uses x.2.1 x.2.2 else [])
/-- The sets that declare a name `u` uses. -/
def directSets (D : Doc) (u : String) : List String :=
  (D.sets.filter (fun R => (usesOfUnit D u).any (fun n => (declaredBy R).contains n))).map (·.id)
/-- The fixed units that declare a name `u` uses. -/
def nextUnits (D : Doc) (u : String) : List String :=
  ((fixedUnits D).filter (fun y => (usesOfUnit D u).any (fun n => y.2.1.declared.contains n))).map (·.1)
/-- The sets reached from `u` in at most `f` steps through fixed units. -/
def attachedF (D : Doc) : Nat → String → List String
  | 0, u => directSets D u
  | f + 1, u => directSets D u ++ (nextUnits D u).flatMap (attachedF D f)
/-- `attachedF` at level 0 for every fixed unit, as a table. -/
def attachedLevel0 (D : Doc) : List (String × List String) :=
  (fixedNames D).map (fun u => (u, VE.SoftNorms.dedup (directSets D u)))
/-- One more level, read from the previous level's table: each level is computed once for every unit. -/
def attachedStep (D : Doc) (tbl : List (String × List String)) : List (String × List String) :=
  (fixedNames D).map (fun u =>
    (u, VE.SoftNorms.dedup (directSets D u ++ (nextUnits D u).flatMap (VE.SoftNorms.belowAt tbl))))
/-- `attachedStep` iterated, stopping early at a fixed point. -/
def attachedIter (D : Doc) : Nat → List (String × List String) → List (String × List String)
  | 0, tbl => tbl
  | n + 1, tbl => if attachedStep D tbl == tbl then tbl else attachedIter D n (attachedStep D tbl)
/-- The sets a fixed unit is attached to, computed with fuel `D.items.length`. -/
def attached (D : Doc) (unit : String) : List String :=
  VE.SoftNorms.belowAt (attachedIter D D.items.length (attachedLevel0 D)) unit

/-! ## A candidate's document (1.4) -/

/-- One unit appended, as `VE.Rights.Wire.addUnit` appends it. -/
def place (X : RightsDoc) (c : Content) (cites : List (String × List String)) : RightsDoc :=
  match c with
  | .assertion _ => X
  | .norm N => { X with soft := { X.soft with T := { X.soft.T with nodes := X.soft.T.nodes ++ [N] } },
                        outsideCites := X.outsideCites ++ (if cites.isEmpty then [] else [(N.name, cites)]) }
  | .right R => { X with rs := X.rs ++ [R],
                         sourceOrder := some (X.sourceOrder.getD [] ++ R.lines.map (R.name, ·)) }
  | .rightLines r ls =>
    { X with rs := X.rs.map (fun R => if R.name == r then { R with lines := R.lines ++ ls } else R),
             sourceOrder := some (X.sourceOrder.getD [] ++ ls.map (r, ·)) }
  | .limitation L => { X with limits := X.limits ++ [L] }
def asserted : Content → List VE.Formula
  | .assertion φ => [φ]
  | _ => []
def build (D : Doc) (keep : String → Bool) (pick : ReadingSet → Option Candidate) : RightsDoc × List VE.Formula :=
  D.items.foldl (fun acc it => match it with
    | .fixed u c cs => if keep u then (place acc.1 c cs, acc.2 ++ asserted c) else acc
    | .bar u b => if keep u then ({ acc.1 with bars := acc.1.bars ++ [b] }, acc.2) else acc
    | .set R => match (pick R).bind (fun a => a.content.map (fun c => (c, a.cites))) with
      | some (c, cs) => (place acc.1 c cs, acc.2 ++ asserted c)
      | none => acc) (D.frame, [])
def free (D : Doc) : RightsDoc × List VE.Formula := build D (fun u => (attached D u).isEmpty) (fun _ => none)
def one (D : Doc) (s : String) (i : Nat) : RightsDoc × List VE.Formula :=
  build D (fun u => (attached D u).all (· == s)) (fun R => if R.id == s then R.candidates[i]? else none)

/-! ## Admission without separation (4.2 to 4.4) -/

def noRights (X : RightsDoc) : Bool :=
  X.rs.isEmpty && X.limits.isEmpty && X.bars.isEmpty && (sourceLines X).isEmpty
def allStrict (X : RightsDoc) : Bool := X.soft.T.nodes.all (fun N => N.mode == .strict && N.alterable.isEmpty)
def chainWF : Chain → RightsDoc → Bool
  | .rights, X => WellFormedRights X
  | .soft, X => noRights X && WellFormedSoft X.soft
  | .norms, X => noRights X && allStrict X && WellFormedSoft X.soft
def sideWF (D : Doc) (X : RightsDoc × List VE.Formula) : Bool :=
  chainWF D.chain X.1 &&
    X.2.all (fun a => a.check (envAt (soften (correlate X.1)) (size (soften (correlate X.1)))) [])
/-- A sort, constant or predicate name reserved for S2 (1.8). -/
def reservedSym (n : String) : Bool := n.startsWith "ve__"
/-- A rule, right or limitation name reserved for S2 (1.8). -/
def reservedName (n : String) : Bool := n.startsWith "rd-"
def contentReserved (c : Content) : Bool := c.declared.any (fun n => reservedName n.2)
/-- 1.8 on the frame and on every fixed and candidate content. The frame's sorts, literals, regulated and defined
    predicates and any unit it holds are checked here; the environment's base predicate and constant names are
    functions in `VE.Environment`, and the wire decoder checks them as it reads them. -/
def reservedFree (D : Doc) : Bool :=
  !((D.frame.soft.E.sorts ++ D.frame.soft.lits ++ D.frame.soft.T.regulated.map (·.name) ++
      D.frame.soft.T.definitions.map (·.name)).any reservedSym) &&
  !((D.frame.soft.T.nodes.map (·.name) ++ D.frame.rs.map (·.name) ++ D.frame.limits.map (·.name)).any reservedName) &&
  D.items.all (fun it => match it with
    | .fixed _ c _ => !contentReserved c
    | .bar _ _ => true
    | .set R => R.candidates.all (fun a => !((a.content.map contentReserved).getD false)))
/-- The names a fixed unit or a bar declares; none for a set. -/
def Item.names : Item → List String
  | .fixed _ c _ => c.declared.map (·.2)
  | .bar _ b => [b.name]
  | .set _ => []
/-- 4.3: no name declared by a candidate is declared by a fixed unit or by a candidate of another set, and no two
    fixed units declare one name. -/
def distinctAcrossSets (D : Doc) : Bool :=
  D.sets.all (fun R => (declaredBy R).all (fun n =>
    D.items.all (fun it => match it with
      | .fixed _ c _ => c.declared.all (fun m => m.2 != n.2)
      | .bar _ b => b.name != n.2
      | .set R' => R'.id == R.id || (declaredBy R').all (fun m => m.2 != n.2)))) &&
  decide (D.items.Pairwise (fun x y => ∀ n ∈ x.names, n ∉ y.names))
/-- 4.2: every name a fixed unit uses that a set declares is an interface name of that set. -/
def interfaceClosed (D : Doc) : Bool :=
  D.items.all (fun it => match it with
    | .fixed _ c cs => (uses c cs).all (fun n =>
        D.sets.all (fun R => !(declaredBy R).contains n || (interfaceOf R).contains n))
    | _ => true)
/-- 4.2: no fixed unit is attached to two sets. Such a unit would be in neither `free D` nor any `one D s i`. -/
def singlyAttached (D : Doc) : Bool :=
  (fixedNames D).all (fun u => (attached D u).all (fun t => (attached D u).all (· == t)))
def WellFormedDoc (D : Doc) : Bool :=
  reservedFree D && distinctAcrossSets D && interfaceClosed D && singlyAttached D && sideWF D (free D) &&
  D.sets.all (fun R => (List.range R.candidates.length).all (fun i =>
    (R.candidates[i]?.bind (·.content)).isNone || sideWF D (one D R.id i)))

/-! ## Proofs -/

theorem mem_sets {D : Doc} {R : ReadingSet} : R ∈ D.sets ↔ Item.set R ∈ D.items := by
  simp only [Doc.sets, List.mem_filterMap]
  constructor
  · rintro ⟨it, hit, h⟩
    cases it <;> simp at h
    subst h; exact hit
  · intro h; exact ⟨_, h, rfl⟩

theorem mem_fixedUnits {D : Doc} {u : String} {c : Content} {cs : List (String × List String)} :
    (u, c, cs) ∈ fixedUnits D ↔ Item.fixed u c cs ∈ D.items := by
  simp only [fixedUnits, List.mem_filterMap]
  constructor
  · rintro ⟨it, hit, h⟩
    cases it <;> simp at h
    obtain ⟨rfl, rfl, rfl⟩ := h
    exact hit
  · intro h; exact ⟨_, h, rfl⟩

theorem mem_usesOfUnit {D : Doc} {u : String} {n : String × String} :
    n ∈ usesOfUnit D u ↔ ∃ c cs, Item.fixed u c cs ∈ D.items ∧ n ∈ uses c cs := by
  simp only [usesOfUnit, List.mem_flatMap]
  constructor
  · rintro ⟨⟨u', c, cs⟩, hx, hn⟩
    split at hn
    · rename_i h
      simp only [beq_iff_eq] at h
      subst h
      exact ⟨c, cs, mem_fixedUnits.mp hx, hn⟩
    · cases hn
  · rintro ⟨c, cs, hx, hn⟩
    exact ⟨(u, c, cs), mem_fixedUnits.mpr hx, by simp [hn]⟩

theorem mem_directSets {D : Doc} {u t : String} :
    t ∈ directSets D u ↔ ∃ R ∈ D.sets, R.id = t ∧ ∃ n ∈ usesOfUnit D u, n ∈ declaredBy R := by
  simp only [directSets, List.mem_map, List.mem_filter, List.any_eq_true, List.contains_iff_mem]
  constructor
  · rintro ⟨R, ⟨hR, n, hn, hd⟩, rfl⟩; exact ⟨R, hR, rfl, n, hn, hd⟩
  · rintro ⟨R, hR, rfl, n, hn, hd⟩; exact ⟨R, ⟨hR, n, hn, hd⟩, rfl⟩

theorem mem_nextUnits {D : Doc} {u u' : String} :
    u' ∈ nextUnits D u ↔ ∃ c' cs', Item.fixed u' c' cs' ∈ D.items ∧ ∃ n ∈ usesOfUnit D u, n ∈ c'.declared := by
  simp only [nextUnits, List.mem_map, List.mem_filter, List.any_eq_true, List.contains_iff_mem]
  constructor
  · rintro ⟨⟨u'', c', cs'⟩, ⟨hx, n, hn, hd⟩, rfl⟩
    exact ⟨c', cs', mem_fixedUnits.mp hx, n, hn, hd⟩
  · rintro ⟨c', cs', hx, n, hn, hd⟩
    exact ⟨(u', c', cs'), ⟨mem_fixedUnits.mpr hx, n, hn, hd⟩, rfl⟩

theorem mem_fixedNames_of_uses {D : Doc} {u : String} {n : String × String} (h : n ∈ usesOfUnit D u) :
    u ∈ fixedNames D := by
  obtain ⟨c, cs, hx, _⟩ := mem_usesOfUnit.mp h
  exact List.mem_map.mpr ⟨(u, c, cs), mem_fixedUnits.mpr hx, rfl⟩

/-- A walk from the head through fixed units to a unit that uses a name the set `t` declares. -/
def PathTo (D : Doc) (t : String) : List String → Prop
  | [] => False
  | [u] => t ∈ directSets D u
  | u :: v :: rest => v ∈ nextUnits D u ∧ PathTo D t (v :: rest)

theorem attachedF_path {D : Doc} {t : String} :
    ∀ (f : Nat) (u : String), t ∈ attachedF D f u ↔ ∃ p, PathTo D t (u :: p) ∧ p.length ≤ f
  | 0, u => by
    simp only [attachedF, Nat.le_zero, List.length_eq_zero_iff]
    constructor
    · intro h; exact ⟨[], h, rfl⟩
    · rintro ⟨p, hp, rfl⟩; exact hp
  | f + 1, u => by
    simp only [attachedF, List.mem_append, List.mem_flatMap]
    constructor
    · rintro (h | ⟨v, hv, h⟩)
      · exact ⟨[], h, Nat.zero_le _⟩
      · obtain ⟨p, hp, hl⟩ := (attachedF_path f v).mp h
        exact ⟨v :: p, ⟨hv, hp⟩, by simp; omega⟩
    · rintro ⟨p, hp, hl⟩
      match p, hp with
      | [], hp => exact Or.inl hp
      | v :: p, ⟨hv, hp⟩ =>
        exact Or.inr ⟨v, hv, (attachedF_path f v).mpr ⟨p, hp, by simp at hl; omega⟩⟩

theorem pathTo_suffix {D : Doc} {t : String} : ∀ (a : List String) (y : String) (rest : List String),
    PathTo D t (a ++ y :: rest) → PathTo D t (y :: rest)
  | [], _, _, h => h
  | [_], _, _, h => h.2
  | _ :: b :: a, y, rest, h => pathTo_suffix (b :: a) y rest h.2

theorem pathTo_cut {D : Doc} {t : String} : ∀ (a : List String) (x : String) (b c : List String),
    PathTo D t (a ++ x :: (b ++ x :: c)) → PathTo D t (a ++ x :: c)
  | [], x, b, c, h => by
    have := pathTo_suffix (x :: b) x c (by simpa using h)
    simpa using this
  | [a0], x, b, c, h => ⟨h.1, pathTo_cut [] x b c h.2⟩
  | a0 :: a1 :: a, x, b, c, h => ⟨h.1, pathTo_cut (a1 :: a) x b c h.2⟩

theorem exists_dup_split {α : Type} : ∀ {l : List α}, ¬ l.Nodup → ∃ a x b c, l = a ++ x :: (b ++ x :: c)
  | [], h => absurd List.nodup_nil h
  | y :: ys, h => by
    by_cases hy : y ∈ ys
    · obtain ⟨b, c, rfl⟩ := List.append_of_mem hy
      exact ⟨[], y, b, c, rfl⟩
    · have : ¬ ys.Nodup := fun hn => h (List.nodup_cons.mpr ⟨hy, hn⟩)
      obtain ⟨a, x, b, c, rfl⟩ := exists_dup_split this
      exact ⟨y :: a, x, b, c, rfl⟩

theorem pathTo_head {D : Doc} {t : String} : ∀ {l : List String}, PathTo D t l → ∃ u p, l = u :: p
  | [], h => h.elim
  | u :: p, _ => ⟨u, p, rfl⟩

/-- Every walk can be shortened to one without repeated units, from the same unit. -/
theorem pathTo_nodup {D : Doc} {t : String} : ∀ (n : Nat) (u : String) (p : List String), p.length ≤ n →
    PathTo D t (u :: p) → ∃ q, PathTo D t (u :: q) ∧ (u :: q).Nodup ∧ q.length ≤ p.length
  | n, u, p, hn, h => by
    by_cases hd : (u :: p).Nodup
    · exact ⟨p, h, hd, Nat.le_refl _⟩
    · obtain ⟨a, x, b, c, he⟩ := exists_dup_split hd
      have h' : PathTo D t (a ++ x :: c) := pathTo_cut a x b c (he ▸ h)
      obtain ⟨u', p', hu'⟩ := pathTo_head h'
      have hlen : (a ++ x :: c).length < (u :: p).length := by
        rw [he]; simp; omega
      have hhead : u' = u := by
        cases a with
        | nil => simp at he hu'; exact (he.1.trans hu'.1).symm
        | cons a0 a => simp at he hu'; exact (he.1.trans hu'.1).symm
      rw [hu', hhead] at h'
      rw [hu'] at hlen
      match n with
      | 0 =>
        simp at hn; subst hn; simp at hlen
      | n + 1 =>
        have hl' : p'.length ≤ n := by simp at hlen; omega
        obtain ⟨q, hq, hqd, hql⟩ := pathTo_nodup n u p' hl' h'
        exact ⟨q, hq, hqd, by simp at hlen; omega⟩

theorem pathTo_fixed {D : Doc} {t : String} : ∀ (l : List String), PathTo D t l → ∀ v ∈ l, v ∈ fixedNames D
  | [], h => h.elim
  | [u], h => by
    intro v hv
    simp at hv; subst hv
    obtain ⟨_, _, _, n, hn, _⟩ := mem_directSets.mp h
    exact mem_fixedNames_of_uses hn
  | u :: w :: rest, h => by
    intro v hv
    rcases List.mem_cons.mp hv with rfl | hv
    · obtain ⟨_, _, _, n, hn, _⟩ := mem_nextUnits.mp h.1
      exact mem_fixedNames_of_uses hn
    · exact pathTo_fixed (w :: rest) h.2 v hv

theorem attached_path_iff {D : Doc} {u t : String} : Attached D u t ↔ ∃ p, PathTo D t (u :: p) := by
  constructor
  · intro h
    induction h with
    | direct hu n hn R hR ht hd =>
      exact ⟨[], mem_directSets.mpr ⟨R, hR, ht, n, mem_usesOfUnit.mpr ⟨_, _, hu, hn⟩, hd⟩⟩
    | step hu hu' n hn hd _ ih =>
      obtain ⟨p, hp⟩ := ih
      exact ⟨_ :: p, mem_nextUnits.mpr ⟨_, _, hu', n, mem_usesOfUnit.mpr ⟨_, _, hu, hn⟩, hd⟩, hp⟩
  · rintro ⟨p, hp⟩
    induction p generalizing u with
    | nil =>
      obtain ⟨R, hR, ht, n, hn, hd⟩ := mem_directSets.mp hp
      obtain ⟨c, cs, hx, hn⟩ := mem_usesOfUnit.mp hn
      exact .direct hx n hn R hR ht hd
    | cons v p ih =>
      obtain ⟨c', cs', hx', n, hn, hd⟩ := mem_nextUnits.mp hp.1
      obtain ⟨c, cs, hx, hn⟩ := mem_usesOfUnit.mp hn
      exact .step hx hx' n hn hd (ih hp.2)

theorem attachedF_iff (D : Doc) (u t : String) : t ∈ attachedF D D.items.length u ↔ Attached D u t := by
  rw [attached_path_iff, attachedF_path]
  constructor
  · rintro ⟨p, hp, _⟩; exact ⟨p, hp⟩
  · rintro ⟨p, hp⟩
    obtain ⟨q, hq, hqd, _⟩ := pathTo_nodup p.length u p (Nat.le_refl _) hp
    refine ⟨q, hq, ?_⟩
    have h1 := VE.SoftNorms.length_le_of_nodup_subset hqd (pathTo_fixed _ hq)
    have h2 : (fixedNames D).length ≤ D.items.length := by
      simp only [fixedNames, fixedUnits, List.length_map]
      exact List.length_filterMap_le _ _
    simp at h1
    omega

theorem usesOfUnit_nil {D : Doc} {u : String} (h : u ∉ fixedNames D) : usesOfUnit D u = [] := by
  apply List.eq_nil_iff_forall_not_mem.mpr
  intro n hn
  exact h (mem_fixedNames_of_uses hn)

theorem attachedF_nil {D : Doc} {u : String} (h : u ∉ fixedNames D) : ∀ f, attachedF D f u = [] := by
  have hd : directSets D u = [] := by simp [directSets, usesOfUnit_nil h]
  have hn : nextUnits D u = [] := by simp [nextUnits, usesOfUnit_nil h]
  intro f
  cases f <;> simp [attachedF, hd, hn]

/-- `attachedStep` iterated `n` times. -/
def attachedLevels (D : Doc) : Nat → List (String × List String)
  | 0 => attachedLevel0 D
  | n + 1 => attachedStep D (attachedLevels D n)

theorem mem_attachedLevels (D : Doc) : ∀ (n : Nat) (u t : String),
    t ∈ VE.SoftNorms.belowAt (attachedLevels D n) u ↔ t ∈ attachedF D n u
  | 0, u, t => by
    simp only [attachedLevels, attachedLevel0, VE.SoftNorms.belowAt_map]
    split
    · simp [VE.SoftNorms.mem_dedup, attachedF]
    · rename_i h; simp [attachedF_nil h]
  | n + 1, u, t => by
    simp only [attachedLevels, attachedStep, VE.SoftNorms.belowAt_map]
    split
    · simp only [VE.SoftNorms.mem_dedup, attachedF, List.mem_append, List.mem_flatMap, mem_attachedLevels D n]
    · rename_i h; simp [attachedF_nil h]

theorem attachedIter_eq (D : Doc) : ∀ (n k : Nat), attachedIter D n (attachedLevels D k) = attachedLevels D (k + n)
  | 0, k => rfl
  | n + 1, k => by
    simp only [attachedIter]
    split
    · rename_i h
      have hfix : attachedLevels D (k + 1) = attachedLevels D k := by
        simpa [attachedLevels] using h
      have : ∀ m, attachedLevels D (k + m) = attachedLevels D k := by
        intro m
        induction m with
        | zero => rfl
        | succ m ih =>
          show attachedStep D (attachedLevels D (k + m)) = _
          rw [ih]; exact hfix
      rw [this (n + 1)]
    · have := attachedIter_eq D n (k + 1)
      simp only [attachedLevels] at this
      rw [this]; congr 1; omega

theorem attached_iff (D : Doc) (u t : String) : t ∈ attached D u ↔ Attached D u t := by
  have h := attachedIter_eq D D.items.length 0
  simp only [attachedLevels, Nat.zero_add] at h
  rw [attached, h, mem_attachedLevels, attachedF_iff]

theorem distinctAcrossSets_spec (D : Doc) : distinctAcrossSets D = true ↔
  (∀ R ∈ D.sets, ∀ n ∈ declaredBy R, ∀ u c cs, Item.fixed u c cs ∈ D.items → ∀ m ∈ c.declared, m.2 ≠ n.2) ∧
  (∀ R ∈ D.sets, ∀ n ∈ declaredBy R, ∀ u b, Item.bar u b ∈ D.items → b.name ≠ n.2) ∧
  (∀ R ∈ D.sets, ∀ R' ∈ D.sets, R.id ≠ R'.id → ∀ n ∈ declaredBy R, ∀ m ∈ declaredBy R', m.2 ≠ n.2) ∧
  D.items.Pairwise (fun x y => ∀ n ∈ x.names, n ∉ y.names) := by
  simp only [distinctAcrossSets, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true]
  constructor
  · rintro ⟨h, hp⟩
    refine ⟨fun R hR n hn u c cs hx m hm => ?_, fun R hR n hn u b hx => ?_,
      fun R hR R' hR' hne n hn m hm => ?_, hp⟩
    · have := h R hR n hn _ hx
      simp only [List.all_eq_true, bne_iff_ne, ne_eq] at this
      exact this m hm
    · have := h R hR n hn _ hx
      simpa using this
    · have := h R hR n hn _ (mem_sets.mp hR')
      simp only [Bool.or_eq_true, beq_iff_eq, List.all_eq_true, bne_iff_ne, ne_eq] at this
      rcases this with he | this
      · exact absurd he.symm hne
      · exact this m hm
  · rintro ⟨h1, h2, h3, hp⟩
    refine ⟨fun R hR n hn it hit => ?_, hp⟩
    cases it with
    | fixed u c cs =>
      simp only [List.all_eq_true, bne_iff_ne, ne_eq]
      exact fun m hm => h1 R hR n hn u c cs hit m hm
    | bar u b => simpa using h2 R hR n hn u b hit
    | set R' =>
      simp only [Bool.or_eq_true, beq_iff_eq, List.all_eq_true, bne_iff_ne, ne_eq]
      by_cases he : R'.id = R.id
      · exact Or.inl he
      · exact Or.inr (fun m hm => h3 R hR R' (mem_sets.mpr hit) (fun e => he e.symm) n hn m hm)

theorem interfaceClosed_spec (D : Doc) : interfaceClosed D = true ↔
  ∀ u c cs, Item.fixed u c cs ∈ D.items → ∀ n ∈ uses c cs, ∀ R ∈ D.sets, n ∈ declaredBy R → n ∈ interfaceOf R := by
  simp only [interfaceClosed, List.all_eq_true]
  constructor
  · intro h u c cs hx n hn R hR hd
    have := h _ hx
    simp only [List.all_eq_true, Bool.or_eq_true, Bool.not_eq_true', List.contains_iff_mem] at this
    rcases this n hn R hR with h' | h'
    · rw [List.contains_iff_mem.mpr hd] at h'
      cases h'
    · exact h'
  · intro h it hit
    cases it with
    | fixed u c cs =>
      simp only [List.all_eq_true, Bool.or_eq_true, Bool.not_eq_true', List.contains_iff_mem]
      intro n hn R hR
      by_cases hd : n ∈ declaredBy R
      · exact Or.inr (h u c cs hit n hn R hR hd)
      · exact Or.inl (by simpa using hd)
    | bar => rfl
    | set => rfl

theorem singlyAttached_spec (D : Doc) : singlyAttached D = true ↔
  ∀ u t t', Attached D u t → Attached D u t' → t = t' := by
  simp only [singlyAttached, List.all_eq_true, beq_iff_eq]
  constructor
  · intro h u t t' ht ht'
    have hu : u ∈ fixedNames D := by
      obtain ⟨p, hp⟩ := attached_path_iff.mp ht
      exact pathTo_fixed _ hp u List.mem_cons_self
    exact (h u hu t ((attached_iff D u t).mpr ht) t' ((attached_iff D u t').mpr ht')).symm
  · intro h u _ t ht t' ht'
    exact (h u t t' ((attached_iff D u t).mp ht) ((attached_iff D u t').mp ht')).symm

/-- Without rights content the rights elaboration is the soft document itself. -/
theorem correlate_noRights (X : RightsDoc) (h : noRights X = true) : correlate X = X.soft ∧ limPremises X = [] := by
  simp only [noRights, Bool.and_eq_true, List.isEmpty_iff] at h
  obtain ⟨⟨⟨_, hl⟩, hb⟩, hs⟩ := h
  have hlines : VE.Rights.linesOf X = [] := by simp [VE.Rights.linesOf, hs, VE.Rights.linesAux]
  have hE := VE.Rights.envR_of_no_gen X (VE.Rights.genDecls_nil X hl hb)
  refine ⟨?_, ?_⟩
  · simp only [correlate, hlines, List.map_nil, List.nil_append, VE.Rights.barNodes_nil X hb, List.append_nil, hE]
  · simp [limPremises, VE.Rights.limPremisesLabelled, VE.Rights.condKeys_nil X hl]

theorem chain_soft (c : Chain) (X : RightsDoc) (h : chainWF c X = true) : WellFormedSoft (correlate X) = true := by
  cases c with
  | rights => exact VE.Rights.correlate_wellFormed X h
  | soft =>
    simp only [chainWF, Bool.and_eq_true] at h
    rw [(correlate_noRights X h.1).1]; exact h.2
  | norms =>
    simp only [chainWF, Bool.and_eq_true] at h
    rw [(correlate_noRights X h.1.1).1]; exact h.2

/-- On the norms chain the value is W1's. -/
theorem chain_norms_value (X : RightsDoc) (h : chainWF .norms X = true) (r : Regulated)
    (hr : r ∈ X.soft.T.regulated) (S : VE.Structure.{u}) (vs : List S.Carrier) :
  ValueSoft (correlate X) r S vs = VE.Norms.Value X.soft.base.T r S vs := by
  simp only [chainWF, Bool.and_eq_true] at h
  obtain ⟨⟨hn, hs⟩, hw⟩ := h
  rw [(correlate_noRights X hn).1, ← VE.SoftNorms.soften_faithful X.soft hw r hr]
  have hh : ∀ N ∈ X.soft.T.nodes, N.mode = .strict ∧ N.alterable = [] := by
    intro N hN
    simp only [allStrict, List.all_eq_true, Bool.and_eq_true, beq_iff_eq, List.isEmpty_iff] at hs
    exact hs N hN
  have := (VE.SoftNorms.soften_hard_identity X.soft hw hh).2
  have hT : (soften X.soft).T = X.soft.base.T := by
    show (⟨X.soft.T.regulated, X.soft.T.definitions, X.soft.T.nodes.map (VE.SoftNorms.primeNode X.soft)⟩ :
      VE.Norms.Tree) = ⟨X.soft.T.regulated, X.soft.T.definitions, X.soft.T.nodes.map VE.SoftNorms.SoftNode.toNode⟩
    rw [← this]; rfl
  rw [hT]

/-- The fold step of `build`. -/
def buildStep (keep : String → Bool) (pick : ReadingSet → Option Candidate)
    (acc : RightsDoc × List VE.Formula) (it : Item) : RightsDoc × List VE.Formula :=
  match it with
  | .fixed u c cs => if keep u then (place acc.1 c cs, acc.2 ++ asserted c) else acc
  | .bar u b => if keep u then ({ acc.1 with bars := acc.1.bars ++ [b] }, acc.2) else acc
  | .set R => match (pick R).bind (fun a => a.content.map (fun c => (c, a.cites))) with
    | some (c, cs) => (place acc.1 c cs, acc.2 ++ asserted c)
    | none => acc

theorem build_eq (D : Doc) (keep : String → Bool) (pick : ReadingSet → Option Candidate) :
    build D keep pick = D.items.foldl (buildStep keep pick) (D.frame, []) := rfl

theorem buildStep_set_fst (keep : String → Bool) (P : ReadingSet → Option Candidate) (R : ReadingSet)
    (hP : ∀ a ∈ P R, ∀ c, a.content = some c → ∃ φ, c = .assertion φ) (acc : RightsDoc × List VE.Formula) :
    (buildStep keep P acc (.set R)).1 = acc.1 := by
  simp only [buildStep]
  cases hPR : P R with
  | none => rfl
  | some a =>
    cases hc : a.content with
    | none => simp [hc]
    | some c =>
      obtain ⟨φ, rfl⟩ := hP a hPR c hc
      simp [hc, place]

theorem build_fst_assertions (D : Doc) (keep : String → Bool) (pick : ReadingSet → Option Candidate)
    (keep' : String → Bool) (pick' : ReadingSet → Option Candidate)
    (hk : ∀ u c cs, Item.fixed u c cs ∈ D.items → (∀ φ, c ≠ .assertion φ) → keep u = keep' u)
    (hb : ∀ u b, Item.bar u b ∈ D.items → keep u = keep' u)
    (hp : ∀ R, Item.set R ∈ D.items → ∀ a ∈ pick R, ∀ c, a.content = some c → ∃ φ, c = .assertion φ)
    (hp' : ∀ R, Item.set R ∈ D.items → ∀ a ∈ pick' R, ∀ c, a.content = some c → ∃ φ, c = .assertion φ) :
    (build D keep pick).1 = (build D keep' pick').1 := by
  rw [build_eq, build_eq]
  suffices ∀ (l : List Item), (∀ it ∈ l, it ∈ D.items) → ∀ (acc acc' : RightsDoc × List VE.Formula),
      acc.1 = acc'.1 → (l.foldl (buildStep keep pick) acc).1 = (l.foldl (buildStep keep' pick') acc').1 from
    this D.items (fun _ h => h) _ _ rfl
  intro l
  induction l with
  | nil => intro _ acc acc' h; exact h
  | cons it l ih =>
    intro hl acc acc' h
    simp only [List.foldl_cons]
    apply ih (fun x hx => hl x (List.mem_cons_of_mem _ hx))
    have hit := hl it List.mem_cons_self
    cases it with
    | fixed u c cs =>
      by_cases hc : ∃ φ, c = .assertion φ
      · obtain ⟨φ, rfl⟩ := hc
        by_cases h1 : keep u <;> by_cases h2 : keep' u <;> simp [buildStep, h1, h2, place, h]
      · have := hk u c cs hit (fun φ e => hc ⟨φ, e⟩)
        by_cases h1 : keep u <;> simp [buildStep, h1, ← this, h]
    | bar u b =>
      have := hb u b hit
      by_cases h1 : keep u <;> simp [buildStep, h1, ← this, h]
    | set R =>
      rw [buildStep_set_fst keep pick R (hp R hit), buildStep_set_fst keep' pick' R (hp' R hit), h]

theorem not_attached_of_formula_only (D : Doc)
    (h : ∀ R ∈ D.sets, ∀ a ∈ R.candidates, ∀ c, a.content = some c → ∃ φ, c = .assertion φ) (u t : String) :
    ¬ Attached D u t := by
  intro ha
  induction ha with
  | direct _ n _ R hR _ hd =>
    simp only [declaredBy, List.mem_flatMap, List.mem_filterMap] at hd
    obtain ⟨c, ⟨a, ha, hc⟩, hn⟩ := hd
    obtain ⟨φ, rfl⟩ := h R hR a ha c hc
    simp [VE.Compose.Content.declared] at hn
  | step _ _ _ _ _ _ ih => exact ih

/-- Identity when unused (composition.md 4.1 rule 5): assertion candidates leave the document as it is, and
    without a declaring candidate no fixed unit is attached. -/
theorem one_formula_only (D : Doc)
    (h : ∀ R ∈ D.sets, ∀ a ∈ R.candidates, ∀ c, a.content = some c → ∃ φ, c = .assertion φ) (s : String) (i : Nat) :
  (one D s i).1 = (free D).1 ∧ (free D).1 = (build D (fun _ => true) (fun _ => none)).1 := by
  have hnil : ∀ u, attached D u = [] := by
    intro u
    apply List.eq_nil_iff_forall_not_mem.mpr
    intro t ht
    exact not_attached_of_formula_only D h u t ((attached_iff D u t).mp ht)
  have hpick : ∀ R, Item.set R ∈ D.items → ∀ a ∈ (if R.id == s then R.candidates[i]? else none),
      ∀ c, a.content = some c → ∃ φ, c = .assertion φ := by
    intro R hR a ha c hc
    split at ha
    · exact h R (mem_sets.mpr hR) a (List.mem_of_getElem? ha) c hc
    · cases ha
  have hnone : ∀ R, Item.set R ∈ D.items → ∀ a ∈ ((fun _ => none) R : Option Candidate),
      ∀ c, a.content = some c → ∃ φ, c = .assertion φ := by
    intro R _ a ha; cases ha
  refine ⟨build_fst_assertions D _ _ _ _ (fun u _ _ _ _ => by simp [hnil u]) (fun u _ _ => by simp [hnil u])
      hpick hnone,
    build_fst_assertions D _ _ _ _ (fun u _ _ _ _ => by simp [hnil u]) (fun u _ _ => by simp [hnil u])
      hnone hnone⟩
end VE.Readings
