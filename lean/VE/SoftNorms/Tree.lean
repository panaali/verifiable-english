import VE.Norms.Replay

/-! Soft-norm documents (docs/spec/soft-norms.md sections 1, 3 and 9.1): the three
independent rule attributes (mode, alterable, rank), the environment `soft` block,
the rank order and its closure `outranks⁺`, effects and colliding pairs `CP(T)`,
and the decision vocabulary that extends `E` to `E′`.

A `SoftDoc` is a W1 document whose rules carry the soft attributes; `D.base` is the
W1 document obtained by dropping them. Nothing here refers to the elaboration: the
generated formulas, `soften` and `WellFormedSoft` are in `Soften.lean`.

The rank closure is computed by `belowF` with fuel `ranks.length`; on a document
whose rank graph passes the shared `VE.Route.dependencyOrder` check it is exactly
reachability (`outranksPlus_iff_path`), hence irreflexive and transitive. `rankHeight`
is the spec's longest ascending chain, computed with the same fuel; `rankHeight_lt`
is the fact that makes the dominance recursion well-founded. -/
namespace VE.SoftNorms
open VE.Norms
open VE.Route (DepNode DepPath DepEdge DagAcyclic dependencyOrder)

inductive Mode | strict | default
  deriving DecidableEq, Repr

inductive Outranking | strict | holistic
  deriving DecidableEq, Repr

structure Exception where
  /-- `none` inherits the environment's `exception_decider`; `some "unstated"` is allowed. -/
  decidedBy : Option String
  /-- Typed in the context `(sorts pred).reverse`, over the base predicates of `E` only. -/
  sufficient : List VE.Formula
  necessary : List VE.Formula
  factors : List String
  deriving DecidableEq, Repr

structure SoftNode extends Node where
  mode : Mode
  rank : Option String
  /-- Sorted, distinct declared parties. -/
  alterable : List String
  /-- `some` iff `mode = default`. -/
  exception : Option Exception
  hard : Bool
  deriving DecidableEq, Repr

structure SoftEnv where
  parties : List String
  ranks : List String
  outranks : List (String × String)
  ties : List (String × String)
  outranking : Outranking
  outrankingDecider : Option String
  exceptionDecider : Option String
  /-- base predicate ↦ party -/
  instructionOf : List (String × String)
  deriving DecidableEq, Repr

structure SoftTree where
  regulated : List Regulated
  definitions : List Definition
  nodes : List SoftNode
  deriving DecidableEq, Repr

structure SoftDoc where
  E : VE.Environment
  lits : List String
  soft : SoftEnv
  T : SoftTree

/-- The W1 document without the soft attributes. -/
def SoftDoc.base (D : SoftDoc) : Doc :=
  ⟨D.E, D.lits, ⟨D.T.regulated, D.T.definitions, D.T.nodes.map SoftNode.toNode⟩⟩

/-! ## Declarations read by the soft semantics -/

/-- The argument sorts of a regulated predicate (`[]` if undeclared). -/
def sortsIn (regs : List Regulated) (p : String) : List String :=
  ((regs.find? (·.name == p)).map (·.sorts)).getD []

def sortsOf (D : SoftDoc) (p : String) : List String := sortsIn D.T.regulated p

/-- The permission dual `m` of a declared pair `(r, m)`. -/
def dualPerm (D : SoftDoc) (r : String) : Option String :=
  ((pairs D.base.T).find? (·.req == r)).map (·.perm)

/-- The obligation `r` of a declared pair `(r, m)`. -/
def dualOblig (D : SoftDoc) (m : String) : Option String :=
  ((pairs D.base.T).find? (·.perm == m)).map (·.req)

/-- The act key (1.3): the act's permission predicate when declared, else the act's
only regulated predicate. -/
def actKey (D : SoftDoc) (p : String) : String := (dualPerm D p).getD p

def act (D : SoftDoc) (N : SoftNode) : String := actKey D N.pred

def actSortsOf (D : SoftDoc) (a : String) : List String := sortsOf D a

def actSorts (D : SoftDoc) (N : SoftNode) : List String := sortsOf D N.pred

def rk (N : SoftNode) : String := N.rank.getD ""

def rulesOn (D : SoftDoc) (p : String) : List SoftNode := D.T.nodes.filter (·.pred == p)

def rulesOnAct (D : SoftDoc) (a : String) : List SoftNode := D.T.nodes.filter (fun N => act D N == a)

def fuel (D : SoftDoc) : Nat := D.T.nodes.length

/-! ## Children (the author precedence DAG, W1's shape) -/

/-- The exceptions of `N` among `ns`, sorted by name, one entry per occurrence of
`N` in a rule's `over` (W1 `children`). -/
def childrenIn (ns : List SoftNode) (N : SoftNode) : List SoftNode :=
  sortBy (fun a b => decide (a.name < b.name))
    (ns.flatMap (fun C => if C.pred == N.pred then (C.over.filter (· == N.name)).map (fun _ => C) else []))

def children (D : SoftDoc) (N : SoftNode) : List SoftNode := childrenIn D.T.nodes N

theorem mem_childrenIn_iff {ns : List SoftNode} {N C : SoftNode} :
    C ∈ childrenIn ns N ↔ C ∈ ns ∧ C.pred = N.pred ∧ N.name ∈ C.over := by
  simp only [childrenIn, mem_sortBy, List.mem_flatMap]
  constructor
  · rintro ⟨C', hC', hm⟩
    split at hm
    · rename_i hp
      obtain ⟨_, hx, rfl⟩ := List.mem_map.mp hm
      obtain ⟨hx, he⟩ := List.mem_filter.mp hx
      simp only [beq_iff_eq] at hp he
      exact ⟨hC', hp, he ▸ hx⟩
    · cases hm
  · rintro ⟨hC, hp, hn⟩
    refine ⟨C, hC, ?_⟩
    rw [if_pos (by simpa using hp)]
    exact List.mem_map.mpr ⟨N.name, List.mem_filter.mpr ⟨hn, by simp⟩, rfl⟩

/-- Children commute with any node map that keeps names, predicates and `over`. -/
theorem mem_childrenIn_map {ns : List SoftNode} (f : SoftNode → SoftNode)
    (hname : ∀ N, (f N).name = N.name) (hpred : ∀ N, (f N).pred = N.pred)
    (hover : ∀ N, (f N).over = N.over) (N C' : SoftNode) :
    C' ∈ childrenIn (ns.map f) (f N) ↔ ∃ C ∈ childrenIn ns N, C' = f C := by
  simp only [mem_childrenIn_iff, List.mem_map]
  constructor
  · rintro ⟨⟨C, hC, rfl⟩, hp, hn⟩
    exact ⟨C, ⟨hC, by simpa [hpred] using hp, by simpa [hname, hover] using hn⟩, rfl⟩
  · rintro ⟨C, ⟨hC, hp, hn⟩, rfl⟩
    exact ⟨⟨C, hC, rfl⟩, by simp [hpred, hp], by simp [hname, hover, hn]⟩

/-- The same for W1 children of a mapped tree. -/
theorem mem_children_map {ns : List SoftNode} (f : SoftNode → Node)
    (hname : ∀ N, (f N).name = N.name) (hpred : ∀ N, (f N).pred = N.pred)
    (hover : ∀ N, (f N).over = N.over) (T : Tree) (hT : T.nodes = ns.map f) (N : SoftNode) (C' : Node) :
    C' ∈ VE.Norms.children T (f N) ↔ ∃ C ∈ childrenIn ns N, C' = f C := by
  rw [VE.Norms.mem_children_iff, hT]
  simp only [mem_childrenIn_iff, List.mem_map]
  constructor
  · rintro ⟨⟨C, hC, rfl⟩, hp, hn⟩
    exact ⟨C, ⟨hC, by simpa [hpred] using hp, by simpa [hname, hover] using hn⟩, rfl⟩
  · rintro ⟨C, ⟨hC, hp, hn⟩, rfl⟩
    exact ⟨⟨C, hC, rfl⟩, by simp [hpred, hp], by simp [hname, hover, hn]⟩

/-! ## The rank order (1.2) -/

/-- The ranks directly below `a` (declared edges `a outranks b`). -/
def directBelow (env : SoftEnv) (a : String) : List String :=
  (env.outranks.filter (·.1 == a)).map (·.2)

/-- The ranks reachable below `a` in at most `f` steps. -/
def belowF (env : SoftEnv) : Nat → String → List String
  | 0, _ => []
  | f + 1, a => (directBelow env a).flatMap (fun c => c :: belowF env f c)

/-- `a outranks⁺ b`: the transitive closure of the declared edges. -/
def outranksPlus (env : SoftEnv) (a b : String) : Bool := (belowF env env.ranks.length a).contains b

/-- The rank dependency graph: `a → b` for each declared `a outranks b`. -/
def rankNodes (env : SoftEnv) : List DepNode := env.ranks.map (fun a => ⟨a, directBelow env a⟩)

def maxOf : List Nat → Nat
  | [] => 0
  | x :: xs => max x (maxOf xs)

/-- The longest ascending `outranks⁺` chain above `a`, with fuel. -/
def heightR (env : SoftEnv) : Nat → String → Nat
  | 0, _ => 0
  | f + 1, a => maxOf ((env.ranks.filter (fun b => outranksPlus env b a)).map (fun b => 1 + heightR env f b))

/-- `rankHeight D N` (9.1): zero for an unranked rule or a rank with no higher rank. -/
def rankHeight (D : SoftDoc) (N : SoftNode) : Nat :=
  match N.rank with
  | some a => heightR D.soft D.soft.ranks.length a
  | none => 0

def rankFuel (D : SoftDoc) : Nat := D.soft.ranks.length + 1

/-- `higher D M N`: both ranked and `rank(M) outranks⁺ rank(N)`. -/
def higher (D : SoftDoc) (M N : SoftNode) : Bool :=
  match M.rank, N.rank with
  | some a, some b => outranksPlus D.soft a b
  | _, _ => false

def Comparable (D : SoftDoc) (M N : SoftNode) : Bool := higher D M N || higher D N M

/-! ## Effects and colliding pairs (1.4) -/

/-- Opposite polarity on one act: the same predicate with opposite signs, or
`+r` against `−m` across the declared pair `(r, m)`. -/
def Incompatible (D : SoftDoc) (M N : SoftNode) : Bool :=
  (M.pred == N.pred && M.sign != N.sign) ||
    (M.sign && !N.sign && dualPerm D M.pred == some N.pred) ||
    (N.sign && !M.sign && dualPerm D N.pred == some M.pred)

def pairLt (x y : SoftNode × SoftNode) : Bool :=
  decide (x.1.name < y.1.name) || (x.1.name == y.1.name && decide (x.2.name < y.2.name))

/-- `CP(T)`: the colliding default pairs, each unordered pair once with the names
in order, the list sorted by the name pair. -/
def collidingPairs (D : SoftDoc) : List (SoftNode × SoftNode) :=
  sortBy pairLt (D.T.nodes.flatMap (fun M => D.T.nodes.filterMap (fun N =>
    if M.mode = .default ∧ N.mode = .default ∧ M.name < N.name ∧ Incompatible D M N = true
    then some (M, N) else none)))

theorem mem_collidingPairs {D : SoftDoc} {M N : SoftNode} :
    (M, N) ∈ collidingPairs D ↔ M ∈ D.T.nodes ∧ N ∈ D.T.nodes ∧ M.mode = .default ∧
      N.mode = .default ∧ M.name < N.name ∧ Incompatible D M N = true := by
  simp only [collidingPairs, mem_sortBy, List.mem_flatMap, List.mem_filterMap]
  constructor
  · rintro ⟨M', hM', N', hN', h⟩
    split at h
    · rename_i hc
      cases h
      exact ⟨hM', hN', hc⟩
    · cases h
  · rintro ⟨hM, hN, hc⟩
    exact ⟨M, hM, N, hN, by rw [if_pos hc]⟩

/-! ## The decision vocabulary (1.3) -/

/-- A rule name's `-` becomes `_` (rule names contain no `_`). -/
def ruleKey (n : String) : String := n.map (fun c => if c == '-' then '_' else c)

def exceptedName (N : SoftNode) : String := "soft__excepted__" ++ ruleKey N.name
def offName (N : SoftNode) (π : String) : String := "soft__off__" ++ ruleKey N.name ++ "__" ++ π
def outweighsName (a L H : String) : String := "soft__outweighs__" ++ L ++ "__" ++ H ++ "__" ++ a

/-- The act and ordered rank pair `(a, L, H)` of a comparable colliding pair,
`H` above `L`. -/
def pairTriple (D : SoftDoc) (M N : SoftNode) : String × String × String :=
  if higher D M N then (act D N, rk N, rk M) else (act D M, rk M, rk N)

def dedup {α : Type} [BEq α] : List α → List α
  | [] => []
  | x :: xs => if (dedup xs).contains x then dedup xs else x :: dedup xs

/-- The `outweighs` triples, under the holistic flag only, in `CP(T)` order, first occurrence kept. -/
def outweighsTriples (D : SoftDoc) : List (String × String × String) :=
  if D.soft.outranking = .holistic then
    (dedup ((collidingPairs D).filterMap (fun (M, N) =>
      if Comparable D M N then some (pairTriple D M N) else none)).reverse).reverse
  else []

def exceptedDecisions (D : SoftDoc) : List (String × List String) :=
  (D.T.nodes.filter (·.mode == .default)).map (fun N => (exceptedName N, sortsOf D N.pred))

def offDecisions (D : SoftDoc) : List (String × List String) :=
  D.T.nodes.flatMap (fun N => N.alterable.map (fun π => (offName N π, sortsOf D N.pred)))

def outweighsDecisions (D : SoftDoc) : List (String × List String) :=
  (outweighsTriples D).map (fun (a, L, H) => (outweighsName a L H, actSortsOf D a))

/-- Every decision predicate with its argument sorts. -/
def decisions (D : SoftDoc) : List (String × List String) :=
  exceptedDecisions D ++ offDecisions D ++ outweighsDecisions D

def decisionNames (D : SoftDoc) : List String := (decisions D).map (·.1)

/-- `E′ = E + decisions`. -/
def envPrime (D : SoftDoc) : VE.Environment :=
  { D.E with predicates := fun p => match (decisions D).find? (·.1 == p) with
      | some d => some d.2
      | none => D.E.predicates p }

/-- The weighing symbols: exceptions, the switches of default rules and `outweighs`. -/
def weighingSyms (D : SoftDoc) : List String :=
  (exceptedDecisions D).map (·.1) ++
    (D.T.nodes.filter (·.mode == .default)).flatMap (fun N => N.alterable.map (offName N)) ++
    (outweighsDecisions D).map (·.1)

/-- The predicates attributed to party `π`: `instruction_of = π`, plus every `off_{N,π}`. -/
def attributed (D : SoftDoc) (π : String) : List String :=
  (D.soft.instructionOf.filter (·.2 == π)).map (·.1) ++
    D.T.nodes.flatMap (fun N => if N.alterable.contains π then [offName N π] else [])

/-! ## List lemmas -/

theorem length_le_of_nodup_subset {α : Type} [DecidableEq α] :
    ∀ {l m : List α}, l.Nodup → (∀ x ∈ l, x ∈ m) → l.length ≤ m.length
  | [], _, _, _ => Nat.zero_le _
  | a :: l, m, hn, hs => by
    have ha : a ∈ m := hs a List.mem_cons_self
    obtain ⟨hnot, hn'⟩ := List.nodup_cons.mp hn
    have hle : l.length ≤ (m.erase a).length :=
      length_le_of_nodup_subset hn' (fun x hx =>
        (List.mem_erase_of_ne (by intro e; subst e; exact hnot hx)).mpr (hs x (List.mem_cons_of_mem _ hx)))
    rw [List.length_erase_of_mem ha] at hle
    have := List.length_pos_of_mem ha
    simp only [List.length_cons]
    omega

theorem le_maxOf : ∀ {l : List Nat} {x : Nat}, x ∈ l → x ≤ maxOf l
  | _ :: _, _, List.Mem.head _ => Nat.le_max_left _ _
  | _ :: _, _, List.Mem.tail _ h => Nat.le_trans (le_maxOf h) (Nat.le_max_right _ _)

theorem maxOf_le : ∀ {l : List Nat} {k : Nat}, (∀ x ∈ l, x ≤ k) → maxOf l ≤ k
  | [], _, _ => Nat.zero_le _
  | x :: _, _, h => Nat.max_le.mpr ⟨h x List.mem_cons_self,
      maxOf_le (fun y hy => h y (List.mem_cons_of_mem _ hy))⟩

theorem exists_of_lt_maxOf : ∀ {l : List Nat} {k : Nat}, k < maxOf l → ∃ x ∈ l, k < x
  | [], _, h => absurd h (Nat.not_lt_zero _)
  | x :: xs, k, h => by
    simp only [maxOf] at h
    by_cases hx : k < x
    · exact ⟨x, List.mem_cons_self, hx⟩
    · have hk : k < maxOf xs := by
        simp only [Nat.max_def] at h
        split at h <;> omega
      obtain ⟨y, hy, hk⟩ := exists_of_lt_maxOf hk
      exact ⟨y, List.mem_cons_of_mem _ hy, hk⟩

/-! ## The rank closure is reachability -/

section Ranks
variable (env : SoftEnv)

/-- The facts about the rank graph that the closure lemmas use (checked by
`WellFormedSoft`). -/
structure RanksValid : Prop where
  declared : ∀ e ∈ env.outranks, e.1 ∈ env.ranks ∧ e.2 ∈ env.ranks
  order : ∃ o, dependencyOrder (rankNodes env) = .ok o

variable {env}

theorem mem_directBelow {a b : String} : b ∈ directBelow env a ↔ (a, b) ∈ env.outranks := by
  simp only [directBelow, List.mem_map, List.mem_filter, beq_iff_eq]
  constructor
  · rintro ⟨⟨x, y⟩, ⟨hm, rfl⟩, rfl⟩; exact hm
  · intro h; exact ⟨(a, b), ⟨h, rfl⟩, rfl⟩

theorem nodeNames_rankNodes : VE.Route.nodeNames (rankNodes env) = env.ranks := by
  simp [VE.Route.nodeNames, rankNodes, List.map_map, Function.comp_def]

theorem depEdge_iff (hv : RanksValid env) {a b : String} :
    DepEdge (rankNodes env) a b ↔ (a, b) ∈ env.outranks := by
  constructor
  · rintro ⟨n, hn, rfl, hb⟩
    simp only [rankNodes, List.mem_map] at hn
    obtain ⟨a, _, rfl⟩ := hn
    simp only [VE.Route.deps, List.mem_filter] at hb
    exact mem_directBelow.mp hb.1
  · intro h
    refine ⟨⟨a, directBelow env a⟩, List.mem_map.mpr ⟨a, (hv.declared _ h).1, rfl⟩, rfl, ?_⟩
    simp only [VE.Route.deps, List.mem_filter, nodeNames_rankNodes, List.contains_iff_mem]
    exact ⟨mem_directBelow.mpr h, (hv.declared _ h).2⟩

theorem belowF_path (hv : RanksValid env) : ∀ (f : Nat) (a b : String), b ∈ belowF env f a →
    DepPath (rankNodes env) a b
  | 0, _, _, h => by simp [belowF] at h
  | f + 1, a, b, h => by
    simp only [belowF, List.mem_flatMap, List.mem_cons] at h
    obtain ⟨c, hc, rfl | hb⟩ := h
    · exact .edge ((depEdge_iff hv).mpr (mem_directBelow.mp hc))
    · exact .trans (.edge ((depEdge_iff hv).mpr (mem_directBelow.mp hc))) (belowF_path hv f c b hb)

theorem depPath_head {ns : List DepNode} {a b : String} (h : DepPath ns a b) :
    ∃ c, DepEdge ns a c ∧ (c = b ∨ DepPath ns c b) := by
  induction h with
  | edge he => exact ⟨_, he, Or.inl rfl⟩
  | trans _ q ih₁ _ =>
    obtain ⟨c, hc, h⟩ := ih₁
    rcases h with rfl | h
    · exact ⟨c, hc, Or.inr q⟩
    · exact ⟨c, hc, Or.inr (.trans h q)⟩

theorem belowF_mono : ∀ {f g : Nat} {a b : String}, f ≤ g → b ∈ belowF env f a → b ∈ belowF env g a
  | 0, _, _, _, _, h => by simp [belowF] at h
  | f + 1, g + 1, a, b, hfg, h => by
    simp only [belowF, List.mem_flatMap, List.mem_cons] at h ⊢
    obtain ⟨c, hc, h⟩ := h
    refine ⟨c, hc, ?_⟩
    rcases h with rfl | h
    · exact Or.inl rfl
    · exact Or.inr (belowF_mono (by omega) h)
  | _ + 1, 0, _, _, hfg, _ => absurd hfg (by omega)

/-- The rank order of a valid rank graph and its position function. -/
theorem order_facts (hv : RanksValid env) : ∃ o : List String, o.Nodup ∧ (∀ x, x ∈ o ↔ x ∈ env.ranks) ∧
    (∀ a b, DepPath (rankNodes env) a b → o.idxOf b < o.idxOf a) ∧ DagAcyclic (rankNodes env) := by
  obtain ⟨o, ho⟩ := hv.order
  obtain ⟨hn, hm, he, hd⟩ := VE.Route.dag_acyclic _ _ ho
  refine ⟨o, hn, fun x => by rw [hm, nodeNames_rankNodes], fun a b hp => VE.Route.depPath_rank _ o he a b hp, hd⟩

theorem path_source_mem (hv : RanksValid env) {a b : String} (h : DepPath (rankNodes env) a b) :
    a ∈ env.ranks ∧ b ∈ env.ranks := by
  induction h with
  | edge he => exact hv.declared _ ((depEdge_iff hv).mp he)
  | trans _ _ ih₁ ih₂ => exact ⟨ih₁.1, ih₂.2⟩

theorem idxOf_lt_length {o : List String} {x : String} (h : x ∈ o) : o.idxOf x < o.length :=
  List.idxOf_lt_length_iff.mpr h

/-- Reachability is found within `ranks.length` steps. -/
theorem path_belowF (hv : RanksValid env) {a b : String} (h : DepPath (rankNodes env) a b) :
    b ∈ belowF env env.ranks.length a := by
  obtain ⟨o, hn, hm, hpos, _⟩ := order_facts hv
  have key : ∀ k a b, o.idxOf a < k → DepPath (rankNodes env) a b → b ∈ belowF env k a := by
    intro k
    induction k with
    | zero => intro a b h; exact absurd h (Nat.not_lt_zero _)
    | succ k ih =>
      intro a b ha hp
      obtain ⟨c, hc, hcb⟩ := depPath_head hp
      simp only [belowF, List.mem_flatMap, List.mem_cons]
      refine ⟨c, mem_directBelow.mpr ((depEdge_iff hv).mp hc), ?_⟩
      rcases hcb with rfl | hcb
      · exact Or.inl rfl
      · exact Or.inr (ih c b (by have := hpos a c (.edge hc); omega) hcb)
  have hlen : o.length ≤ env.ranks.length :=
    length_le_of_nodup_subset hn (fun x hx => (hm x).mp hx)
  have ha : a ∈ o := (hm a).mpr (path_source_mem hv h).1
  exact key _ a b (Nat.lt_of_lt_of_le (idxOf_lt_length ha) hlen) h

theorem outranksPlus_iff_path (hv : RanksValid env) (a b : String) :
    outranksPlus env a b = true ↔ DepPath (rankNodes env) a b := by
  simp only [outranksPlus, List.contains_iff_mem]
  exact ⟨belowF_path hv _ a b, path_belowF hv⟩

theorem outranksPlus_irrefl (hv : RanksValid env) (a : String) : outranksPlus env a a = false := by
  obtain ⟨_, _, _, _, hd⟩ := order_facts hv
  cases h : outranksPlus env a a
  · rfl
  · exact absurd ((outranksPlus_iff_path hv a a).mp h) (hd a)

theorem outranksPlus_trans (hv : RanksValid env) {a b c : String} (h₁ : outranksPlus env a b = true)
    (h₂ : outranksPlus env b c = true) : outranksPlus env a c = true :=
  (outranksPlus_iff_path hv a c).mpr
    (.trans ((outranksPlus_iff_path hv a b).mp h₁) ((outranksPlus_iff_path hv b c).mp h₂))

theorem outranksPlus_asymm (hv : RanksValid env) {a b : String} (h : outranksPlus env a b = true) :
    outranksPlus env b a = false := by
  cases h' : outranksPlus env b a
  · rfl
  · have := outranksPlus_trans hv h h'
    rw [outranksPlus_irrefl hv] at this
    cases this

/-! ## Rank heights -/

theorem heightR_le : ∀ (f : Nat) (a : String), heightR env f a ≤ f
  | 0, _ => Nat.le_refl 0
  | f + 1, a => by
    simp only [heightR]
    apply maxOf_le
    intro x hx
    obtain ⟨b, _, rfl⟩ := List.mem_map.mp hx
    have := heightR_le f b
    omega

theorem heightR_ge {f : Nat} {a b : String} (hb : b ∈ env.ranks) (h : outranksPlus env b a = true) :
    1 + heightR env f b ≤ heightR env (f + 1) a := by
  simp only [heightR]
  exact le_maxOf (List.mem_map.mpr ⟨b, List.mem_filter.mpr ⟨hb, h⟩, rfl⟩)

/-- A strict increase with more fuel only happens while the height equals the fuel. -/
theorem heightR_grow : ∀ (f : Nat) (a : String), heightR env f a < heightR env (f + 1) a →
    heightR env f a = f
  | 0, _, _ => rfl
  | g + 1, a, h => by
    have e : heightR env (g + 1 + 1) a = maxOf ((env.ranks.filter (fun b => outranksPlus env b a)).map
        (fun b => 1 + heightR env (g + 1) b)) := rfl
    have h' := h
    rw [e] at h'
    obtain ⟨x, hx, hlt⟩ := exists_of_lt_maxOf h'
    obtain ⟨b, hb, rfl⟩ := List.mem_map.mp hx
    obtain ⟨hbr, hba⟩ := List.mem_filter.mp hb
    have hge := heightR_ge (f := g) hbr hba
    have hb' : heightR env g b < heightR env (g + 1) b := by omega
    have := heightR_grow g b hb'
    have h1 := heightR_le (env := env) (g + 1) b
    have h2 := heightR_le (env := env) (g + 1) a
    omega

theorem heightR_mono : ∀ (f : Nat) (a : String), heightR env f a ≤ heightR env (f + 1) a
  | 0, _ => Nat.zero_le _
  | g + 1, a => by
    show maxOf ((env.ranks.filter (fun b => outranksPlus env b a)).map (fun b => 1 + heightR env g b)) ≤
      maxOf ((env.ranks.filter (fun b => outranksPlus env b a)).map (fun b => 1 + heightR env (g + 1) b))
    apply maxOf_le
    intro x hx
    obtain ⟨b, hb, rfl⟩ := List.mem_map.mp hx
    have := heightR_mono g b
    exact Nat.le_trans (by omega) (le_maxOf (List.mem_map.mpr ⟨b, hb, rfl⟩))

/-- Heights are bounded by the position in the rank order. -/
theorem heightR_pos (hv : RanksValid env) {o : List String}
    (hm : ∀ x, x ∈ o ↔ x ∈ env.ranks)
    (hpos : ∀ a b, DepPath (rankNodes env) a b → o.idxOf b < o.idxOf a) :
    ∀ (f : Nat) (a : String), a ∈ env.ranks → heightR env f a + o.idxOf a < o.length
  | 0, a, ha => by simpa [heightR] using idxOf_lt_length ((hm a).mpr ha)
  | f + 1, a, ha => by
    have hbound : ∀ x ∈ (env.ranks.filter (fun b => outranksPlus env b a)).map (fun b => 1 + heightR env f b),
        x ≤ o.length - 1 - o.idxOf a := by
      intro x hx
      obtain ⟨b, hb, rfl⟩ := List.mem_map.mp hx
      obtain ⟨hbr, hba⟩ := List.mem_filter.mp hb
      have h₁ := heightR_pos hv hm hpos f b hbr
      have h₂ := hpos b a ((outranksPlus_iff_path hv b a).mp hba)
      omega
    have := maxOf_le hbound
    have hlt := idxOf_lt_length ((hm a).mpr ha)
    simp only [heightR]
    omega

theorem heightR_lt_ranks (hv : RanksValid env) (f : Nat) {a : String} (ha : a ∈ env.ranks) :
    heightR env f a < env.ranks.length := by
  obtain ⟨o, hn, hm, hpos, _⟩ := order_facts hv
  have := heightR_pos hv hm hpos f a ha
  have hlen : o.length ≤ env.ranks.length := length_le_of_nodup_subset hn (fun x hx => (hm x).mp hx)
  omega

/-- The height at `ranks.length` is stable. -/
theorem heightR_stable (hv : RanksValid env) {a : String} (ha : a ∈ env.ranks) :
    heightR env (env.ranks.length + 1) a = heightR env env.ranks.length a := by
  have hlt := heightR_lt_ranks hv env.ranks.length ha
  have hmono := heightR_mono (env := env) env.ranks.length a
  by_cases h : heightR env env.ranks.length a < heightR env (env.ranks.length + 1) a
  · have := heightR_grow _ a h; omega
  · omega

/-- A higher rank has a strictly smaller height. -/
theorem heightR_lt_of_outranks (hv : RanksValid env) {a b : String} (h : outranksPlus env b a = true) :
    heightR env env.ranks.length b < heightR env env.ranks.length a := by
  have hp := (outranksPlus_iff_path hv b a).mp h
  obtain ⟨hb, ha⟩ := path_source_mem hv hp
  have := heightR_ge (f := env.ranks.length) hb h
  rw [heightR_stable hv ha] at this
  omega

end Ranks

theorem rankHeight_lt_of_higher {D : SoftDoc} (hv : RanksValid D.soft) {M N : SoftNode}
    (h : higher D M N = true) : rankHeight D M < rankHeight D N := by
  unfold higher at h
  unfold rankHeight
  split at h
  · rename_i a b hM hN
    rw [hM, hN]
    exact heightR_lt_of_outranks hv h
  · cases h

theorem rankHeight_lt_fuel (D : SoftDoc) (N : SoftNode) : rankHeight D N < rankFuel D := by
  unfold rankHeight rankFuel
  split
  · rename_i a _
    have := heightR_le (env := D.soft) D.soft.ranks.length a
    omega
  · omega

theorem higher_asymm {D : SoftDoc} (hv : RanksValid D.soft) {M N : SoftNode} (h : higher D M N = true) :
    higher D N M = false := by
  unfold higher at h ⊢
  split at h
  · rename_i a b hM hN
    rw [hN, hM]
    exact outranksPlus_asymm hv h
  · cases h

theorem higher_irrefl {D : SoftDoc} (hv : RanksValid D.soft) (M : SoftNode) : higher D M M = false := by
  unfold higher
  split
  · rename_i a b hM hN
    rw [hM] at hN; cases hN
    exact outranksPlus_irrefl hv a
  · rfl

theorem comparable_symm (D : SoftDoc) (M N : SoftNode) : Comparable D M N = Comparable D N M := by
  simp [Comparable, Bool.or_comm]

theorem str_beq_comm (a b : String) : (a == b) = (b == a) := by
  by_cases h : a = b
  · subst h; rfl
  · have h' : b ≠ a := fun e => h e.symm
    rw [beq_eq_false_iff_ne.mpr h, beq_eq_false_iff_ne.mpr h']

theorem incompatible_symm (D : SoftDoc) (M N : SoftNode) : Incompatible D M N = Incompatible D N M := by
  unfold Incompatible
  rw [str_beq_comm M.pred N.pred]
  cases hM : M.sign <;> cases hN : N.sign <;> simp [Bool.or_comm]

end VE.SoftNorms
