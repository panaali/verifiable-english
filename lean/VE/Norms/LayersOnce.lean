import VE.Norms.SmallModel

/-! The layers of a W1 document computed once (lean-first plan F5d; batch 7 review B1).

`subst T i φ` reads every layer symbol through `expTable T i`, which computes the layer order (`syms T`, a
topological sort of the stratum DAG) at each of the `i` levels for every lookup and keeps nothing between lookups,
so `targets` and `InFragment`, which build a conflict formula for every regulated predicate and declared pair, are
quartic in the regulated predicates of the environment: about 0.5 s of the service's CPU on the UDHR pilot's 62
for an empty rights document, paid by every rights, soft-norms and readings request. The functions here compute
the layers once per document. Each is declared in the namespace of the function it replaces, with a lemma that the
two are equal, so every theorem about the original holds of the run. The `@[csimp]` lemmas at the end make the
compiler run the hoisted function wherever compiled code calls the original, in every module that imports this one
(`VE.Norms.Wire` does, so every route that decodes a W1 document does). `targets` is defined after this module,
in `VE.Norms.Replay`, and is replaced by `targetsIn` there, right after its definition, so that `Replay`'s own
consumers of it compile to the twin as well. -/

namespace VE.Norms

/-! ## The expansion table built once

`expTable T i` answers a lookup by computing the layer order (`syms T`, a topological sort) at each of the `i`
levels and the meaning of the symbol it finds afresh, recursively; nothing is kept between lookups. `expEntries T`
holds one entry per layer symbol, newest first, each symbol's base formula built when first read and then kept
(a `Thunk`), and `expAt` reads the table of any prefix from it. `expAt_expEntries` says it is `expTable`. -/

/-- The table of an entry list kept newest first: a name's newest entry. -/
def entryTable (es : List (String × Thunk VE.Formula)) : Table := fun n => (es.find? (·.1 == n)).map (·.2.get)

/-- The entries with the next layer symbol added: its meaning under the entries before it. -/
def expStep (T : Tree) (es : List (String × Thunk VE.Formula)) (q : Sym) : List (String × Thunk VE.Formula) :=
  (q.name, Thunk.mk (fun _ => substWith (entryTable es) (q.meaning T))) :: es

/-- One entry per layer symbol of `T`, newest first. -/
def expEntries (T : Tree) : List (String × Thunk VE.Formula) := (syms T).foldl (expStep T) []

/-- The table of the first `i` layer symbols, read from the entries of all of them. -/
def expAt (es : List (String × Thunk VE.Formula)) (i : Nat) : Table := entryTable (es.drop (es.length - i))

theorem expStep_foldl_length (T : Tree) : ∀ (l : List Sym) (es : List (String × Thunk VE.Formula)),
    (l.foldl (expStep T) es).length = es.length + l.length
  | [], _ => rfl
  | q :: l, es => by
    rw [List.foldl_cons, expStep_foldl_length T l, expStep, List.length_cons, List.length_cons]
    omega

theorem expStep_foldl_drop (T : Tree) : ∀ (l : List Sym) (es : List (String × Thunk VE.Formula)),
    (l.foldl (expStep T) es).drop l.length = es
  | [], _ => rfl
  | q :: l, es => by
    rw [List.foldl_cons, List.length_cons, ← List.drop_drop, expStep_foldl_drop T l, expStep, List.drop_one,
      List.tail_cons]

theorem entryTable_take (T : Tree) : ∀ k : Nat, entryTable (((syms T).take k).foldl (expStep T) []) = expTable T k
  | 0 => by funext n; simp [entryTable, expTable]
  | k + 1 => by
    funext n
    cases hq : (syms T)[k]? with
    | some q =>
      have hk : (syms T).take (k + 1) = (syms T).take k ++ [q] := by rw [List.take_succ, hq]; rfl
      have ih := entryTable_take T k
      rw [hk, List.foldl_append, List.foldl_cons, List.foldl_nil, expStep]
      simp only [expTable, hq, ← ih]
      by_cases h : q.name = n
      · simp [entryTable, h, Thunk.get]
      · simp [entryTable, h, Ne.symm h]
    | none =>
      have hk : (syms T).take (k + 1) = (syms T).take k := by rw [List.take_succ, hq]; simp
      rw [hk, entryTable_take T k]
      simp only [expTable, hq]

theorem expAt_expEntries (T : Tree) (i : Nat) : expAt (expEntries T) i = expTable T i := by
  have hs : syms T = (syms T).take i ++ (syms T).drop i := (List.take_append_drop i (syms T)).symm
  have hl : (expEntries T).length - i = ((syms T).drop i).length := by
    rw [expEntries, expStep_foldl_length, List.length_drop]
    simp
  unfold expAt
  rw [hl, expEntries, hs, List.foldl_append, ← hs, expStep_foldl_drop, entryTable_take]

/-- `subst` read from the entries. -/
theorem subst_expAt (T : Tree) (i : Nat) (φ : VE.Formula) : substWith (expAt (expEntries T) i) φ = subst T i φ := by
  rw [expAt_expEntries]
  rfl

/-- What every formula of a document reads from its layers, computed once per document: the layer symbols in
order, their names, and the expansion table's entries. -/
structure Layers where
  syms : List Sym
  names : List String
  entries : List (String × Thunk VE.Formula)

def layersOf (D : Doc) : Layers :=
  let ss := syms D.T
  ⟨ss, ss.map Sym.name, ss.foldl (expStep D.T) []⟩

theorem layersOf_syms (D : Doc) : (layersOf D).syms = syms D.T := rfl
theorem layersOf_names (D : Doc) : (layersOf D).names = layerNames D.T := rfl
theorem layersOf_entries (D : Doc) : (layersOf D).entries = expEntries D.T := rfl

/-- `subst D.T i` from a document's layers. -/
def substIn (L : Layers) (i : Nat) (φ : VE.Formula) : VE.Formula := substWith (expAt L.entries i) φ

theorem substIn_eq (D : Doc) (i : Nat) (φ : VE.Formula) : substIn (layersOf D) i φ = subst D.T i φ :=
  subst_expAt D.T i φ

/-- `conflict`, `outcomeBase` and `pairConflict` from the document's layers, computed once (plan F5d). -/
def conflictIn (D : Doc) (L : Layers) (r : Regulated) : VE.Formula :=
  let i := L.names.idxOf r.name
  .and (substIn L i (pos D.T r.name)) (substIn L i (neg D.T r.name))

def outcomeBaseIn (D : Doc) (L : Layers) (n : String) : VE.Formula :=
  match D.T.regulated.find? (·.name == n) with
  | some r => substIn L (L.names.idxOf n) (outcome D.T r)
  | none => .bottom

def pairConflictIn (D : Doc) (L : Layers) (pr : Pair) : VE.Formula :=
  .and (outcomeBaseIn D L pr.req) (.not (outcomeBaseIn D L pr.perm))

theorem conflictIn_eq (D : Doc) (r : Regulated) : conflictIn D (layersOf D) r = conflict D r := by
  simp only [conflictIn, conflict, substIn_eq, layersOf_names, before]

theorem outcomeBaseIn_eq (D : Doc) (n : String) : outcomeBaseIn D (layersOf D) n = outcomeBase D n := by
  simp only [outcomeBaseIn, outcomeBase, substIn_eq, layersOf_names, before]
  all_goals rfl

theorem pairConflictIn_eq (D : Doc) (pr : Pair) : pairConflictIn D (layersOf D) pr = pairConflict D pr := by
  simp only [pairConflictIn, pairConflict, outcomeBaseIn_eq]

/-- `targets` from the document's layers, computed once (plan F5d). -/
def targetsIn (D : Doc) (L : Layers) : List (String × List String × VE.Formula) :=
  L.syms.filterMap (fun | .reg r => some (r.name, r.sorts, conflictIn D L r) | .defn _ => none) ++
    (pairs D.T).map (fun pr => (pr.req ++ "->" ++ pr.perm, pr.sorts, pairConflictIn D L pr))


/-- `InFragment` from the document's layers. -/
def InFragmentIn (D : Doc) (L : Layers) : Bool :=
  D.T.regulated.all (fun r => Formula.qfree (conflictIn D L r)) &&
    (pairs D.T).all (fun pr => Formula.qfree (pairConflictIn D L pr))

theorem InFragmentIn_eq (D : Doc) : InFragmentIn D (layersOf D) = InFragment D := by
  simp only [InFragmentIn, InFragment, conflictIn_eq, pairConflictIn_eq]

/-! ## The compiled code runs the hoisted functions

Each lemma below replaces, in code compiled by a module that imports this one, a call of the original by a call of
the hoisted function equal to it. -/

/-- `InFragment` with the layers computed once. -/
def InFragmentOnce (D : Doc) : Bool := InFragmentIn D (layersOf D)

@[csimp] theorem inFragment_eq_once : @InFragment = @InFragmentOnce :=
  funext fun D => (InFragmentIn_eq D).symm

end VE.Norms
