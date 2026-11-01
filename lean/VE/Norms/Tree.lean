import VE.Norms.Basic

/-! W1 norm documents (docs/spec/norms.md sections 1, 3, 4.1 and 6.1): regulated
declarations, W3 definitions, rule nodes, the one dependency DAG over defined ∪
regulated predicates, the precedence DAG over rule names, and the executable
well-formedness check.

A `Doc` is the complete environment `E` (every declared predicate, defined,
regulated or base), its declared `$string` literals, and the tree. The layer
symbols `syms D` are the defined and regulated predicates in the order returned
by `VE.Route.dependencyOrder`; `envAt D i` is the environment `E_i` containing
the base vocabulary and the first `i` layer symbols (`hide` of the rest), so
`envAt D 0` is `E_base` and `envAt D (syms D).length` is `E`. -/
namespace VE.Norms
open VE.Route

inductive Role | permission | obligation | plain
  deriving DecidableEq, Repr

structure Regulated where
  name : String
  sorts : List String
  allowByDefault : Bool
  role : Role
  /-- canonical act phrase; required except for plain -/
  act : Option String
  /-- the permission dual of an obligation, mandatory if the act has both roles (3.1) -/
  permission : Option String
  deriving DecidableEq, Repr

/-- A W3 definition `name(args) := body`, the shape of `VE.Definitions.Def`. -/
structure Definition where
  name : String
  args : List String
  body : VE.Formula
  deriving DecidableEq, Repr

/-- A rule. `guard` and `carveOuts` are typed in the context `(sorts pred).reverse`. -/
structure Node where
  name : String
  pred : String
  sign : Bool
  guard : VE.Formula
  carveOuts : List VE.Formula
  over : List String
  deriving DecidableEq, Repr

structure Tree where
  regulated : List Regulated
  definitions : List Definition
  nodes : List Node
  deriving DecidableEq, Repr

structure Doc where
  E : VE.Environment
  lits : List String
  T : Tree

/-! ## Rules, children and layer symbols -/

/-- Stable insertion sort (structural, so concrete documents reduce in the
kernel); on the unique names sorted here it agrees with Python's `sorted`. -/
def insertBy {α : Type} (lt : α → α → Bool) (x : α) : List α → List α
  | [] => [x]
  | y :: ys => if lt x y then x :: y :: ys else y :: insertBy lt x ys

def sortBy {α : Type} (lt : α → α → Bool) : List α → List α
  | [] => []
  | x :: xs => insertBy lt x (sortBy lt xs)

theorem mem_insertBy {α : Type} (lt : α → α → Bool) (x a : α) :
    ∀ l : List α, a ∈ insertBy lt x l ↔ a = x ∨ a ∈ l
  | [] => by simp [insertBy]
  | y :: ys => by
    unfold insertBy
    split
    · simp
    · simp only [List.mem_cons, mem_insertBy lt x a ys]
      constructor
      · rintro (h | h | h)
        · exact Or.inr (Or.inl h)
        · exact Or.inl h
        · exact Or.inr (Or.inr h)
      · rintro (h | h | h)
        · exact Or.inr (Or.inl h)
        · exact Or.inl h
        · exact Or.inr (Or.inr h)

theorem mem_sortBy {α : Type} (lt : α → α → Bool) (a : α) : ∀ l : List α, a ∈ sortBy lt l ↔ a ∈ l
  | [] => by simp [sortBy]
  | x :: xs => by simp [sortBy, mem_insertBy, mem_sortBy lt a xs]

/-- The rules on `p`, in document order. -/
def rulesOn (T : Tree) (p : String) : List Node := T.nodes.filter (·.pred == p)

/-- The exceptions of `N` (rules on the same predicate taking precedence over
it), sorted by name, one entry per occurrence of `N` in a rule's `over`, as
Python `ve/norms.py` builds its children lists. -/
def children (T : Tree) (N : Node) : List Node :=
  sortBy (fun a b => decide (a.name < b.name))
    (T.nodes.flatMap (fun C => if C.pred == N.pred then (C.over.filter (· == N.name)).map (fun _ => C) else []))

theorem mem_children_iff {T : Tree} {N C : Node} :
    C ∈ children T N ↔ C ∈ T.nodes ∧ C.pred = N.pred ∧ N.name ∈ C.over := by
  simp only [children, mem_sortBy, List.mem_flatMap]
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

def regulatedNames (T : Tree) : List String := T.regulated.map Regulated.name

/-- A layer symbol: a regulated or a defined predicate. -/
inductive Sym
  | reg (r : Regulated)
  | defn (d : Definition)
  deriving DecidableEq, Repr

def Sym.name : Sym → String
  | .reg r => r.name
  | .defn d => d.name

def Sym.sorts : Sym → List String
  | .reg r => r.sorts
  | .defn d => d.args

/-- The formulas a symbol's meaning reads: its rules' guards and carve-outs, or
its definition body. All are typed in `sorts.reverse` over the layer below. -/
def Sym.formulas (T : Tree) : Sym → List VE.Formula
  | .reg r => (rulesOn T r.name).flatMap (fun N => N.guard :: N.carveOuts)
  | .defn d => [d.body]

/-- The predicates a formula mentions. -/
def preds : VE.Formula → List String
  | .top | .bottom | .eq _ _ => []
  | .unary p _ | .binary p _ _ => [p]
  | .not a | .all _ a | .ex _ a => preds a
  | .and a b | .or a b | .implies a b => preds a ++ preds b

/-- The shared dependency DAG over defined ∪ regulated predicates (4.1(4)). -/
def stratumNodes (T : Tree) : List DepNode :=
  T.regulated.map (fun r => ⟨r.name, ((Sym.reg r).formulas T).flatMap preds⟩) ++
    T.definitions.map (fun d => ⟨d.name, preds d.body⟩)

/-- The precedence DAG over rule names: `N → M` for `M ∈ over(N)` (4.1(3)). -/
def precedenceNodes (T : Tree) : List DepNode := T.nodes.map (fun N => ⟨N.name, N.over⟩)

def lookupSym (T : Tree) (n : String) : Option Sym :=
  match T.regulated.find? (·.name == n) with
  | some r => some (.reg r)
  | none => (T.definitions.find? (·.name == n)).map .defn

/-- The layer order: `dependencyOrder` over the stratum DAG. -/
def order (T : Tree) : List String :=
  match dependencyOrder (stratumNodes T) with
  | .ok o => o
  | .error _ => []

def syms (T : Tree) : List Sym := (order T).filterMap (lookupSym T)

def layerNames (T : Tree) : List String := (syms T).map Sym.name

/-- `E_i`: the base vocabulary plus the first `i` layer symbols. -/
def envAt (D : Doc) (i : Nat) : VE.Environment := hide D.E ((layerNames D.T).drop i)

/-- The number of layer symbols; `envAt D (size D)` is the complete environment. -/
def size (D : Doc) : Nat := (syms D.T).length

/-- `before p`: the prefix length before `p` is introduced. -/
def before (D : Doc) (p : String) : Nat := (layerNames D.T).idxOf p

/-! ## Profile pairs (3.1) -/

/-- A declared pair `(r obligation, m permission)` and their common argument sorts. -/
structure Pair where
  req : String
  perm : String
  sorts : List String
  deriving DecidableEq, Repr

/-- Declared pairs in sorted order of `r`, as Python `ve/background.py` sorts them. -/
def pairs (T : Tree) : List Pair :=
  sortBy (fun a b => decide (a.req < b.req)) (T.regulated.filterMap (fun r => match r.role, r.permission with
    | .obligation, some m => some ⟨r.name, m, r.sorts⟩
    | _, _ => none))

/-! ## The executable well-formedness check -/

/-- Height of a rule in the precedence DAG (a leaf has height 1), with fuel. -/
def height (T : Tree) : Nat → Node → Nat
  | 0, _ => 1
  | f + 1, N => 1 + ((children T N).map (height T f)).foldl max 0

private def dupName (ns : List String) : Option String := ns.find? (fun n => ns.count n > 1)

/-- The conditions the metatheory uses (`Valid`), as one Boolean. Reached only
after every diagnostic check has passed. -/
def semanticCheck (D : Doc) : Bool :=
  let ss := syms D.T
  (dependencyOrder (precedenceNodes D.T)).isOk && (dependencyOrder (stratumNodes D.T)).isOk &&
  decide (layerNames D.T).Nodup &&
  ss.all (fun q => D.E.predicates q.name == some q.sorts &&
    (q.sorts.length == 1 || q.sorts.length == 2) && q.sorts.all D.E.sorts.contains) &&
  (List.range ss.length).all (fun k => match ss[k]? with
    | some q => (q.formulas D.T).all (fun φ => φ.check (envAt D k) q.sorts.reverse)
    | none => false) &&
  D.T.regulated.all (fun r => ss.contains (.reg r)) &&
  (pairs D.T).all (fun pr => pr.req != pr.perm &&
    ss.any (fun q => match q with | .reg r => r.name == pr.req && r.sorts == pr.sorts | _ => false) &&
    ss.any (fun q => match q with | .reg m => m.name == pr.perm && m.sorts == pr.sorts | _ => false))

/-- Python `repr` of a string (identifiers only; enough for these diagnostics). -/
def pyRepr (s : String) : String := "'" ++ s ++ "'"

def pyTuple (l : List String) : String :=
  "(" ++ ", ".intercalate (l.map pyRepr) ++ (if l.length == 1 then ",)" else ")")

/-- Python `_Checker.term`'s diagnostic and sort. -/
def termSort (E : VE.Environment) (Γ : List String) : VE.Term → Except String String
  | .var i => match Γ[i]? with
    | some s => .ok s
    | none => .error s!"UnboundVariable: Variable index {i} is outside its scope"
  | .const c => match E.constants c with
    | some s => .ok s
    | none => .error s!"UnknownSymbol: Unknown constant {pyRepr c}"

/-- Python `_Checker.formula`'s first diagnostic, in its traversal order,
rendered `<code>: <message>` as 11.1 writes diagnostics. -/
def typeDiagnostic (E : VE.Environment) : List String → VE.Formula → Except String Unit
  | _, .top | _, .bottom => .ok ()
  | Γ, .unary p t => do
    let some sig := E.predicates p | throw s!"UnknownSymbol: Unknown predicate {pyRepr p}"
    unless sig.length == 1 do throw s!"TypeMismatch: Predicate {pyRepr p} has arity {sig.length}, not 1"
    let a ← termSort E Γ t
    unless [a] == sig do throw s!"TypeMismatch: Predicate {pyRepr p} expects {pyTuple sig}, received {pyTuple [a]}"
  | Γ, .binary p t u => do
    let some sig := E.predicates p | throw s!"UnknownSymbol: Unknown predicate {pyRepr p}"
    unless sig.length == 2 do throw s!"TypeMismatch: Predicate {pyRepr p} has arity {sig.length}, not 2"
    let a ← termSort E Γ t
    let b ← termSort E Γ u
    unless [a, b] == sig do throw s!"TypeMismatch: Predicate {pyRepr p} expects {pyTuple sig}, received {pyTuple [a, b]}"
  | Γ, .eq t u => do
    let a ← termSort E Γ t
    let b ← termSort E Γ u
    unless a == b do throw s!"TypeMismatch: Equality requires one sort, received {pyRepr a} and {pyRepr b}"
  | Γ, .not a => typeDiagnostic E Γ a
  | Γ, .and a b | Γ, .or a b | Γ, .implies a b => do
    typeDiagnostic E Γ a
    typeDiagnostic E Γ b
  | Γ, .all s a | Γ, .ex s a => do
    unless E.sorts.contains s do throw s!"UnknownSymbol: Unknown binder sort {pyRepr s}"
    typeDiagnostic E (s :: Γ) a

/-- A rule name: `[a-z][a-z0-9-]*`, at most 64 bytes (3.2). -/
def ruleName (s : String) : Bool :=
  s.utf8ByteSize ≤ 64 && match s.toList with
    | c :: cs => ('a' ≤ c && c ≤ 'z') && cs.all (fun d => ('a' ≤ d && d ≤ 'z') || d.isDigit || d == '-')
    | [] => false

/-- The act-identity and permission-dual checks of 3.1 over the regulated
declarations, in the order Python's `Environment` runs them after decoding
every predicate. The norms decoder runs them with the declarations, so they
precede every rule check. -/
def actChecks (regulated : List Regulated) : Except String Unit := do
  -- Act identity (sorts, canonical act, role): at most one predicate per role.
  let keyed := regulated.filter (·.role != .plain)
  let mut seen : List (List String × Option String × Bool) := []
  for r in keyed do
    let key := (r.sorts, r.act, r.role == .permission)
    if seen.contains key then
      throw s!"DuplicateActRole: {if r.role == .permission then "permission" else "obligation"}, {r.act.getD ""}"
    seen := seen ++ [key]
  let mut linked : List String := []
  for r in regulated do
    if r.role != .obligation then continue
    let expected := regulated.find? (fun m => m.role == .permission && m.sorts == r.sorts && m.act == r.act)
    match r.permission with
    | none =>
      if let some m := expected then throw s!"MissingPermissionDual: {r.name}, {m.name}"
    | some pm =>
      match regulated.find? (·.name == pm) with
      | none => throw s!"MissingPermissionDual: {r.name}, {pm}"
      | some m =>
        unless m.role == .permission do throw s!"MissingPermissionDual: {r.name}, {pm}"
        unless m.sorts == r.sorts do throw s!"DualSortMismatch: {r.name}, {pm}"
        unless m.act == r.act do throw s!"DualActMismatch: {r.name}, {pm}"
        if linked.contains pm then throw s!"DuplicateActRole: obligation, {r.act.getD ""}"
        linked := linked ++ [pm]

/-- Declaration checks (3.1), 4.1, guard/carve-out typing and both DAG checks,
with the shared diagnostics of 11.1, in the order Python `ve/environment.py`
(declarations) and `ve/norms.py` `NormDocument` (rules) report them. -/
def check (D : Doc) : Except String Unit := do
  let T := D.T
  if T.regulated.length > 64 then throw "ResourceLimit: regulated predicates"
  let symNames := regulatedNames T ++ T.definitions.map Definition.name
  if let some n := dupName symNames then throw s!"DuplicateDeclaration: predicate {n}"
  for r in T.regulated do
    unless D.E.predicates r.name == some r.sorts do
      throw s!"UnknownSymbol: regulated predicate {r.name}"
    unless r.sorts.length == 1 || r.sorts.length == 2 do
      throw s!"UnsupportedArity: regulated predicate {r.name}"
    unless r.sorts.all D.E.sorts.contains do throw s!"UnknownSymbol: sort of {r.name}"
    match r.role, r.act with
    | .plain, some _ => throw s!"InvalidInput: invalid regulated fields for {r.name}"
    | .permission, none | .obligation, none =>
      throw s!"InvalidInput: invalid regulated fields for {r.name}"
    | _, _ => pure ()
    if r.role != .obligation && r.permission.isSome then
      throw s!"InvalidInput: invalid regulated fields for {r.name}"
  actChecks T.regulated
  for d in T.definitions do
    unless D.E.predicates d.name == some d.args do throw s!"UnknownSymbol: defined predicate {d.name}"
    unless d.args.length == 1 || d.args.length == 2 do
      throw s!"UnsupportedArity: defined predicate {d.name}"
    unless d.args.all D.E.sorts.contains do throw s!"UnknownSymbol: sort of {d.name}"
    typeDiagnostic D.E d.args.reverse d.body
    unless d.body.check D.E d.args.reverse do throw s!"InvalidInput: ill-typed definition {d.name}"
  -- Rules (4.1(1)-(3)), one at a time as Python checks them. Python types every
  -- rule with one `_Checker`, so the guards and carve-outs of the whole document
  -- share one `MAX_NODES` budget (term nodes count).
  if T.nodes.length > 256 then throw "ResourceLimit: rules"
  let mut names : List String := []
  let mut nodes := 0
  for N in T.nodes do
    unless ruleName N.name do throw s!"InvalidInput: invalid rule name {pyRepr N.name}"
    if names.contains N.name then throw s!"DuplicateDeclaration: rule {N.name}"
    names := names ++ [N.name]
    match T.regulated.find? (·.name == N.pred) with
    | none => throw s!"UnknownSymbol: regulated predicate {N.pred}"
    | some r =>
      if N.carveOuts.length > 8 then throw "InvalidInput: invalid sign or too many carve-outs"
      for φ in N.guard :: N.carveOuts do
        typeDiagnostic D.E r.sorts.reverse φ
        unless φ.check D.E r.sorts.reverse do throw s!"InvalidInput: ill-typed rule {N.name}"
        nodes := nodes + VE.Bridge.formulaNodes φ
        if nodes > 10000 then throw "ResourceLimit: AST exceeds 10,000 nodes"
  for N in T.nodes do
    for m in N.over do
      match T.nodes.find? (·.name == m) with
      | none => throw s!"UnknownRule: rule {m}"
      | some M =>
        unless M.pred == N.pred do
          throw s!"PrecedenceAcrossPredicates: rule {N.name} on {N.pred}, rule {M.name} on {M.pred}"
  match dependencyOrder (precedenceNodes T) with
  | .error e => throw e
  | .ok _ => pure ()
  if T.nodes.any (fun N => height T T.nodes.length N > 16) then
    throw "ResourceLimit: precedence depth"
  -- The shared stratum DAG (4.1(4)).
  match dependencyOrder (stratumNodes T) with
  | .error e => throw e
  | .ok _ => pure ()

/-- `check`, then the conditions of the metatheory. -/
def validate (D : Doc) : Except String Unit :=
  match check D with
  | .error e => .error e
  | .ok () => if semanticCheck D then .ok () else .error "InvalidInput: norm document is not stratified"

def WellFormed (D : Doc) : Bool := match validate D with
  | .ok () => true
  | .error _ => false

theorem semanticCheck_of_wellFormed (D : Doc) (h : WellFormed D = true) : semanticCheck D = true := by
  unfold WellFormed validate at h
  split at h <;> rename_i heq
  · split at heq
    · cases heq
    · split at heq
      · assumption
      · cases heq
  · cases h

end VE.Norms
