import VE.Rights.Tree
import VE.SoftNorms.Coherence

/-! The elaboration `correlate(D) = (E″, T″)` and `Lim_D` (docs/spec/rights.md 1.3–1.6,
4.1, 4.2, 5.1), the syntactic narrowing inventory of 4.5 and the executable check
`WellFormedRights`.

* `nodeOf D N` is a line instance's node in `T″`: its guard conjoined with the holder
  guard at the holder slot (omitted when `H_R` is syntactically `⊤`) and its author
  carve-outs followed by the one packed limitation carve-out `limpack_N` (omitted when no
  limitation is in scope).
* `barNode D m` is the strict, hard, unswitchable node `¬m(x̄) if aimed_m(x̄)` with
  precedence over every right-derived positive node on `m`, present under the rule
  reading only.
* `correlate D` lists the line nodes in instance order, then the norm units outside
  rights unchanged, then the bar nodes by predicate name; nothing else changes.

`narrowings` and `condF` (4.5) live here rather than in `Scope.lean` because the
well-formedness check records the typing facts the scope proofs need (as
`softSemanticCheck` does for the soft proofs). `WellFormedRights` runs the rights
diagnostics of 4.1 in the order of 8, then `validateSoft` on the elaboration, the
identifier limit on `E″′`, and finally `rightsSemanticCheck`, the facts the proofs use. -/
namespace VE.Rights
open VE.Norms (Regulated Role anyF atom bindAll subst size envAt Sat)
open VE.SoftNorms (SoftNode SoftDoc soften envPrime WellFormedSoft dualPerm dualOblig primeNode
  childrenIn Incompatible Comparable higher act rk)
universe u

/-! ## 4.2: the nodes of `T″` -/

/-- `G ∧ H_R` at the holder slot (W1's capture-free `inst`); `G` when `H_R` is `⊤`. -/
def holderConj (D : RightsDoc) (N : Line) (G : VE.Formula) : VE.Formula :=
  match rightOf D N.right with
  | some R => if R.guard = .top then G
      else .and G (VE.Norms.inst [.var ((sortsOf D N).length - 1 - holderSlot D N)] R.guard)
  | none => G

/-- `own_N := G_N ∧ H_R`. -/
def ownGuard (D : RightsDoc) (N : Line) : VE.Formula := holderConj D N N.node.guard

/-- The atom `lim_{L,a_N}(x̄)`. -/
def limF (D : RightsDoc) (L : Limitation) (N : Line) : VE.Formula :=
  atom (limName (limIndex D L (lineAct D N))) (sortsOf D N)

/-- The limitations with `N` in scope (right and source kind both filtered). -/
def scopeLimits (D : RightsDoc) (N : Line) : List Limitation := D.limits.filter (fun L => inScope D L N.right N)

/-- `limpack_N`: the disjunction of `lim_{L,a_N}` over the limitations in scope; `⊥` when none is. -/
def limPack (D : RightsDoc) (N : Line) : VE.Formula := anyF ((scopeLimits D N).map (limF D · N))

/-- `[limPack D N]`, or `[]` when no limitation is in scope. -/
def limPackList (D : RightsDoc) (N : Line) : List VE.Formula :=
  if scopeLimits D N = [] then [] else [limPack D N]

/-- A line instance's node in `T″`. -/
def nodeOf (D : RightsDoc) (N : Line) : SoftNode :=
  { N.node with guard := ownGuard D N, carveOuts := N.node.carveOuts ++ limPackList D N }

def lineNodes (D : RightsDoc) : List SoftNode := (linesOf D).map (fun RN => nodeOf D RN.2)

/-- The norm units outside rights. -/
def outsideRules (D : RightsDoc) : List SoftNode := D.soft.T.nodes

/-- `T″` without the bar nodes: the rules the direct semantics reads. -/
def directNodes (D : RightsDoc) : List SoftNode := lineNodes D ++ D.soft.T.nodes

/-- The atom `aimed_m(x̄)`. -/
def aimedF (D : RightsDoc) (m : String) : VE.Formula :=
  atom (aimedName (barIndex D m)) (VE.SoftNorms.sortsOf D.soft m)

/-- The names of the right-derived positive nodes on `m`. -/
def posLineNames (D : RightsDoc) (m : String) : List String :=
  ((lineNodes D).filter (fun X => X.pred == m && X.sign)).map (·.name)

/-- `bar_m` (1.4). -/
def barNode (D : RightsDoc) (m : String) : SoftNode :=
  { name := barRuleName (barIndex D m), pred := m, sign := false, guard := aimedF D m, carveOuts := [],
    over := posLineNames D m, mode := .strict, rank := none, alterable := [], exception := none, hard := true }

/-- By predicate name, rule reading only. -/
def barNodes (D : RightsDoc) : List SoftNode := if ruleReading D then (barPreds D).map (barNode D) else []

def correlate (D : RightsDoc) : SoftDoc :=
  { D.soft with E := envR D,
                T := { D.soft.T with nodes := (linesOf D).map (fun RN => nodeOf D RN.2) ++ D.soft.T.nodes ++ barNodes D } }

/-- The lines as written before the outside rules, nothing else. -/
def flattenTop (D : RightsDoc) : SoftDoc :=
  { D.soft with T := { D.soft.T with nodes := (linesOf D).map (·.2.node) ++ D.soft.T.nodes } }

/-- `φ°`: W1's outcome substitution to `E″′_base`. -/
def outcomeSubst (D : RightsDoc) (φ : VE.Formula) : VE.Formula :=
  subst (soften (correlate D)).T (size (soften (correlate D))) φ

/-- `selects″_N` as a formula on `T″′`. -/
def selectsR (D : RightsDoc) (N : Line) : VE.Formula :=
  VE.Norms.selects (soften (correlate D)).T (VE.Norms.fuel (soften (correlate D)).T) (primeNode (correlate D) (nodeOf D N))

/-! ## `Lim_D` (1.3, 5.1) -/

def limAtom (D : RightsDoc) (L : Limitation) (a : String) : VE.Formula :=
  atom (limName (limIndex D L a)) (VE.SoftNorms.sortsOf D.soft a)

def condAtom (D : RightsDoc) (L : Limitation) (c : Condition) (a : String) : VE.Formula :=
  atom (condName (condIndex D L c a)) (VE.SoftNorms.sortsOf D.soft a)

/-- The premise of one `(L, a, c)`: necessary `∀x̄. lim → cond`, sufficient `∀x̄. cond → lim`. -/
def limPremise (D : RightsDoc) (L : Limitation) (a : String) (c : Condition) : VE.Formula :=
  bindAll (VE.SoftNorms.sortsOf D.soft a)
    (if c.necessary then .implies (limAtom D L a) (condAtom D L c a) else .implies (condAtom D L c a) (limAtom D L a))

def keyPremise (D : RightsDoc) (k : String × String × String) : Option (String × VE.Formula) :=
  match D.limits.find? (·.name == k.1) with
  | none => none
  | some L =>
    match L.conditions.find? (·.name == k.2.2) with
    | none => none
    | some c => some (s!"rights:limitation:{L.name}:{k.2.1}:{if c.necessary then "necessary" else "sufficient"}:{c.name}",
                      limPremise D L k.2.1 c)

/-- `Lim_D` with its labels, in the order (limitation, act key, condition) sorted by name. -/
def limPremisesLabelled (D : RightsDoc) : List (String × VE.Formula) := (condKeys D).filterMap (keyPremise D)

/-- `Lim_D`. -/
def limPremises (D : RightsDoc) : List VE.Formula := (limPremisesLabelled D).map (·.2)

/-! ## 5.1 -/

def backgroundBaseR (D : RightsDoc) : List VE.Formula := VE.SoftNorms.backgroundBase' (correlate D) ++ limPremises D
def backgroundR (D : RightsDoc) : List VE.Formula := VE.SoftNorms.background' (correlate D) ++ limPremises D

def BaseAdmissibleR (D : RightsDoc) (B : VE.Structure.{u}) : Prop :=
  VE.SoftNorms.BaseAdmissible' (correlate D) B ∧ Sat B (limPremises D)

def RightsConflictFree (D : RightsDoc) : Prop :=
  ∀ B : VE.Structure.{u}, BaseAdmissibleR D B → VE.Norms.ConflictFree (soften (correlate D)) B

/-! ## 4.5: the narrowing inventory (syntactic, from `T″′`) -/

/-- The right-derived permission predicate whose bar reaches `N`: its own predicate, or the
permission dual of a default obligation `+` line. -/
def barReach (D : RightsDoc) (N : Line) : Option String :=
  if rightPermission D N.node.pred then some N.node.pred
  else if N.node.mode = .default ∧ N.node.sign = true then
    match dualPerm (correlate D) N.node.pred with
    | some m => if rightPermission D m then some m else none
    | none => none
  else none

inductive Narrowing
  | carveOut (i : Nat) | exception (M : String) | limPack | excepted | switch (party : String)
  | blockedBy (M : String) | dominatedBy (M : String) | bar
  deriving DecidableEq, Repr

/-- The rule of `T″` without bars named `M`. -/
def nodeNamed (D : RightsDoc) (M : String) : Option SoftNode := (directNodes D).find? (·.name == M)

/-- `M` blocks `X` in soft-norms 4.2 step 2 when strict and selecting: on `X`'s predicate
with either sign, or against `X`'s effect across the declared pair. -/
def blocksOn (C : SoftDoc) (X M : SoftNode) : Bool :=
  M.pred == X.pred || (X.sign && dualPerm C X.pred == some M.pred && !M.sign) ||
    (!X.sign && dualOblig C X.pred == some M.pred && M.sign)

/-- `dom(M, N)` for one opponent `M` (the body of soft's `domWith`). -/
def domOneF (C : SoftDoc) (eff : SoftNode → VE.Formula) (M N : SoftNode) : VE.Formula :=
  .or (if higher C M N = true then
        .and (eff M) (if C.soft.outranking = .holistic then .not (VE.SoftNorms.outweighsF C (act C N) (rk N) (rk M)) else .top)
       else .bottom)
      (if C.soft.outranking = .holistic ∧ higher C N M = true then
        .and (VE.SoftNorms.eligibleF C M) (VE.SoftNorms.outweighsF C (act C N) (rk M) (rk N))
       else .bottom)

/-- `M` can dominate `X` (the two disjuncts of `domOneF`): `M` outranks `X`, or, under holistic
outranking, `X` outranks `M` and may be outweighed. A lower-ranked `M` under strict outranking
never dominates, so it is no mechanism of `X`. -/
def dominable (C : SoftDoc) (M X : SoftNode) : Bool :=
  higher C M X || (decide (C.soft.outranking = .holistic) && higher C X M)

/-- Every way the line can fail to select where its own guard holds (4.5): author carve-outs,
exceptions (direct children, each covering its subtree), the packed limitation, the soft
exception, switches, blocking strict rules, dominating ranked rules and the bar. `exception
bar_m` and `blockedBy bar_m`, on `m` and across the dual pair, fold into `bar`, listed when
`barReach D N = some m` under the rule reading (the only reading with a bar node). -/
def narrowings (D : RightsDoc) (N : Line) : List Narrowing :=
  let X := nodeOf D N
  let C := correlate D
  (List.range N.node.carveOuts.length).map .carveOut ++
  (childrenIn (directNodes D) X).map (fun M => .exception M.name) ++
  (if limPackList D N = [] then [] else [.limPack]) ++
  (if N.node.mode = .default then [.excepted] else []) ++
  N.node.alterable.map .switch ++
  (if N.node.mode = .default then
    ((directNodes D).filter (fun M => M.mode == .strict && blocksOn C X M)).map (fun M => .blockedBy M.name)
   else []) ++
  (if N.node.mode = .default then
    ((directNodes D).filter (fun M => M.mode == .default && Incompatible C M X && dominable C M X)).map
      (fun M => .dominatedBy M.name)
   else []) ++
  (if ruleReading D && (barReach D N).isSome then [.bar] else [])

/-- `cond_n` of the table of 4.5, as a formula on `T″′` in the line's context. -/
def condF (D : RightsDoc) (N : Line) : Narrowing → VE.Formula
  | .carveOut i => .and (ownGuard D N) (N.node.carveOuts[i]?.getD .bottom)
  | .exception M =>
    match nodeNamed D M with
    | some M' => VE.Norms.yields (soften (correlate D)).T (VE.Norms.fuel (soften (correlate D)).T) (primeNode (correlate D) M')
    | none => .bottom
  | .limPack => limPack D N
  | .excepted => VE.SoftNorms.exceptedF (correlate D) (nodeOf D N)
  | .switch π => atom (VE.SoftNorms.offName (nodeOf D N) π) (VE.SoftNorms.sortsOf (correlate D) N.node.pred)
  | .blockedBy M =>
    match nodeNamed D M with
    | some M' => VE.SoftNorms.selects' (correlate D) M'
    | none => .bottom
  | .dominatedBy M =>
    match nodeNamed D M with
    | some M' => domOneF (correlate D) (VE.SoftNorms.effF (correlate D) (correlate D).soft.ranks.length) M' (nodeOf D N)
    | none => .bottom
  | .bar =>
    match barReach D N with
    | some m => aimedF D m
    | none => .bottom

/-! ## 4.1: the diagnostics -/

def regOfName (D : RightsDoc) (p : String) : Option Regulated := D.soft.T.regulated.find? (·.name == p)

def beginsRightsRule (n : String) : Bool := n.startsWith "rights-"
def beginsRightsPred (p : String) : Bool := p.startsWith "rights__"

/-- An identifier of the predicate grammar (`[a-z][a-z0-9_]*`, at most 64 bytes). -/
def identifier (s : String) : Bool :=
  s.utf8ByteSize ≤ 64 && match s.toList with
    | c :: cs => ('a' ≤ c && c ≤ 'z') && cs.all (fun d => ('a' ≤ d && d ≤ 'z') || d.isDigit || d == '_')
    | [] => false

def validDecider (d : Option String) : Bool := d.all (fun s => !s.isEmpty && s.utf8ByteSize ≤ 64)

/-- The environment `rights` block (3.1). -/
def checkBlock (D : RightsDoc) : Except String Unit := do
  let env := D.rights
  let E := D.soft.E
  if env.holders.isEmpty || env.bearers.isEmpty then throw "InvalidInput: invalid rights block"
  for s in env.holders ++ env.bearers do
    unless E.sorts.contains s do throw s!"UnknownSymbol: sort {s}"
  if let some s := VE.SoftNorms.dupOf env.holders then throw s!"DuplicateDeclaration: holder {s}"
  if let some s := VE.SoftNorms.dupOf env.bearers then throw s!"DuplicateDeclaration: bearer {s}"
  for q in env.protected do
    match E.predicates q with
    | none => throw s!"InvalidInput: protected {q}"
    | some ss =>
      if VE.SoftNorms.definedOrRegulated D.soft q || !(ss.any env.holders.contains) then
        throw s!"InvalidInput: protected {q}"
  if let some a := VE.SoftNorms.dupOf (env.alters.map (·.actKey)) then throw s!"DuplicateDeclaration: alters {a}"
  for a in env.alters do
    let bad := s!"InvalidInput: alters {a.actKey}"
    match regOfName D a.actKey with
    | none => throw bad
    | some r =>
      unless r.role == .permission do throw bad
      match r.sorts[a.holderSlot]? with
      | none => throw bad
      | some h =>
        unless env.holders.contains h do throw bad
        match E.predicates a.status with
        | none => throw bad
        | some ss => if VE.SoftNorms.definedOrRegulated D.soft a.status || !ss.contains h then throw bad
        match a.recognition with
        | none => pure ()
        | some rc =>
          match regOfName D rc with
          | none => throw bad
          | some q =>
            unless q.role == .obligation && ((q.sorts.head?.map env.bearers.contains).getD false) &&
                q.sorts.contains h do throw bad

def altersOf (D : RightsDoc) (p : String) : Option AltersEntry := D.rights.alters.find? (·.actKey == p)

/-- The object slots of the holder sort. -/
def holderObjectSlots (sorts : List String) (h : String) : List Nat :=
  ((List.range sorts.length).drop 1).filter (fun i => sorts[i]? == some h)

/-- The shape table of 1.2 on one line instance. -/
def checkShape (D : RightsDoc) (R : Right) (N : Line) : Except String Unit := do
  let env := D.rights
  let shape := s!"IncidentShape: {N.node.name} on right {R.name}"
  let some r := regOfName D N.node.pred | throw s!"UnknownSymbol: regulated predicate {N.node.pred}"
  let subj := r.sorts.head?.getD ""
  let h := R.holder
  let objectSlot : Except String Unit := do
    match N.source.holderSlot with
    | some k => unless k ≥ 1 && r.sorts[k]? == some h do throw shape
    | none =>
      match holderObjectSlots r.sorts h with
      | [] => throw shape
      | [_] => pure ()
      | _ => throw s!"HolderSlotAmbiguous: {N.node.name}"
  match N.ikind with
  | .claim =>
    unless env.bearers.contains subj do throw shape
    unless (r.role == .obligation && N.node.sign) || (r.role == .permission && !N.node.sign) do throw shape
    objectSlot
  | .liberty =>
    unless subj == h && r.role == .permission && N.node.sign do throw shape
  | .immunity =>
    unless env.bearers.contains subj && r.role == .permission && !N.node.sign do throw shape
    let some a := altersOf D N.node.pred | throw shape
    objectSlot
    unless holderSlot D N == a.holderSlot do throw shape
  | .powerLiberty =>
    unless subj == h && r.role == .permission && N.node.sign do throw shape
    let some a := altersOf D N.node.pred | throw shape
    unless a.holderSlot == 0 && a.recognition.isSome do throw shape
  | .powerRecognition =>
    unless env.bearers.contains subj && r.role == .obligation && N.node.sign do throw shape
    let some l := N.source.liberty | throw shape
    let some a := altersOf D l.pred | throw shape
    unless a.recognition == some N.node.pred do throw shape
    objectSlot

/-- One source line: its fields by kind and its fan-out map (3.2). -/
def checkSourceLine (D : RightsDoc) (R : Right) (S : SourceLine) : Except String Unit := do
  match S.kind with
  | .power =>
    match S.norm, S.liberty, S.recognition with
    | none, some _, some _ => pure ()
    | _, _, _ => throw s!"IncidentShape: power on right {R.name}"
    unless S.fanOut.isEmpty do throw s!"IncidentShape: power on right {R.name}"
  | _ =>
    let some n := S.norm | throw s!"IncidentShape: line on right {R.name}"
    if S.liberty.isSome || S.recognition.isSome then throw s!"IncidentShape: {n.name} on right {R.name}"
    unless S.fanOut.isEmpty do
      if S.kind == .liberty then throw s!"IncidentShape: {n.name} on right {R.name}"
      for b in D.rights.bearers do
        unless S.fanOut.any (·.1 == b) do throw s!"FanOutUndeclared: {n.name}, {b}"
      if let some b := VE.SoftNorms.dupOf (S.fanOut.map (·.1)) then throw s!"FanOutUndeclared: {n.name}, {b}"
      for (b, p) in S.fanOut do
        unless D.rights.bearers.contains b do throw s!"FanOutUndeclared: {n.name}, {b}"
        match regOfName D p with
        | none => throw s!"FanOutUndeclared: {n.name}, {b}"
        | some r =>
          unless r.sorts.head? == some b do throw s!"FanOutUndeclared: {n.name}, {b}"
          match S.fanOut.head? with
          | none => pure ()
          | some (_, p0) =>
            match regOfName D p0 with
            | none => throw s!"FanOutUndeclared: {n.name}, {b}"
            | some r0 =>
              unless r.act == r0.act && r.role == r0.role && r.sorts.drop 1 == r0.sorts.drop 1 do
                throw s!"FanOutUndeclared: {n.name}, {b}"

/-- The author rule names of a source line (the fan-out instances are generated). -/
def authorNodes (S : SourceLine) : List SoftNode := S.norm.toList ++ S.liberty.toList ++ S.recognition.toList

/-- The rights diagnostics of 4.1 steps 1–4, in the order of 8. -/
def checkRights (D : RightsDoc) : Except String Unit := do
  checkBlock D
  if D.rs.length > 128 then throw "ResourceLimit: rights"
  if D.limits.length > 16 then throw "ResourceLimit: limitations"
  let names := D.rs.map (·.name) ++ D.limits.map (·.name) ++ D.bars.map (·.name)
  let ruleNames := (D.rs.flatMap (fun R => R.lines.flatMap authorNodes)).map (·.name) ++ D.soft.T.nodes.map (·.name)
  for n in names ++ ruleNames do
    if beginsRightsRule n then throw s!"InvalidInput: name {n} begins with rights-"
  if let some n := VE.SoftNorms.dupOf (names ++ ruleNames) then
    if (D.rs.map (·.name)).contains n then throw s!"DuplicateDeclaration: right {n}"
    else if (D.limits.map (·.name)).contains n then throw s!"DuplicateDeclaration: limitation {n}"
    else if (D.bars.map (·.name)).contains n then throw "DuplicateDeclaration: bar"
    else throw s!"DuplicateDeclaration: rule {n}"
  for p in D.soft.T.regulated.map (·.name) ++ D.soft.T.definitions.map (·.name) do
    if beginsRightsPred p then throw s!"InvalidInput: author predicate {p} begins with rights__"
  for d in genDecls D do
    if (D.soft.E.predicates d.1).isSome then throw s!"InvalidInput: author predicate {d.1} begins with rights__"
  for M in D.rs.flatMap (fun R => R.lines.flatMap authorNodes) ++ D.soft.T.nodes do
    for m in M.over do
      if beginsRightsRule m then throw s!"UnknownSymbol: rule {m}"
  for R in D.rs do
    unless D.rights.holders.contains R.holder do throw s!"UnknownSymbol: sort {R.holder}"
    VE.Norms.typeDiagnostic D.soft.E [R.holder] R.guard
    unless R.guard.check D.soft.E [R.holder] do throw s!"InvalidInput: ill-typed right {R.name}"
    for S in R.lines do
      checkSourceLine D R S
  for RN in linesOf D do
    match rightOf D RN.1 with
    | none => throw s!"UnknownRight: {RN.1}"
    | some R =>
      checkShape D R RN.2
      if RN.2.node.carveOuts.length > 6 then throw s!"ResourceLimit: carve-outs of rule {RN.2.node.name}"
  for R in D.rs do
    unless (linesOf D).any (·.1 == R.name) do throw s!"RightWithoutIncident: {R.name}"
  for L in D.limits do
    match L.scope with
    | none => pure ()
    | some rs =>
      if rs.isEmpty then throw s!"InvalidInput: invalid scope of limitation {L.name}"
      for r in rs do
        unless (D.rs.map (·.name)).contains r do throw s!"UnknownRight: {r}"
    if L.kinds == some [] then throw s!"InvalidInput: invalid kinds of limitation {L.name}"
    if L.conditions.length > 8 then throw "ResourceLimit: conditions"
    for c in L.conditions do
      unless identifier c.name do throw s!"InvalidInput: invalid condition {c.name}"
      unless validDecider c.decidedBy do throw s!"InvalidInput: invalid decider for condition {c.name}"
    if let some c := VE.SoftNorms.dupOf (L.conditions.map (·.name)) then
      throw s!"DuplicateDeclaration: condition {c}"
    unless validDecider L.decidedBy do throw s!"InvalidInput: invalid decider for limitation {L.name}"
    if L.decidedBy.isNone then throw s!"MissingExceptionDecider: limitation {L.name}"
  if D.bars.length > 1 then throw "DuplicateDeclaration: bar"
  for b in D.bars do
    unless validDecider b.decidedBy do throw s!"InvalidInput: invalid decider for bar {b.name}"
  -- 4.1 step 3: every citation names a source unit, so no citation to a non-existent unit
  -- licenses a mechanism (4.5).
  for cs in D.rs.flatMap (fun R => R.lines.map (·.cites)) ++ D.outsideCites.map (·.2) do
    for kv in cs do
      for u in kv.2 do
        unless D.sourceUnits.contains u do throw s!"UnknownSymbol: unit {u}"

/-! ## The facts behind the proofs -/

/-- The facts the proofs use; each follows from the construction or the diagnostics above. -/
def rightsSemanticCheck (D : RightsDoc) : Bool :=
  let C := correlate D
  let Ep := envAt (soften C) (size (soften C))
  let E0 := envAt (soften C) 0
  (C.T.nodes.all (fun X => (barNodes D).all (fun B => !X.over.contains B.name))) &&
  ((permPreds D).all (fun m => dualPerm C m == none)) &&
  ((linesOf D).all (fun RN =>
    let N := RN.2
    let Γ := (sortsOf D N).reverse
    (ownGuard D N).check Ep Γ && (selectsR D N).check Ep Γ &&
      (narrowings D N).all (fun n => (condF D N n).check Ep Γ) &&
      (limPack D N).check E0 Γ &&
      (match barReach D N with | some m => !ruleReading D || (aimedF D m).check E0 Γ | none => true))) &&
  ((limPremises D).all (fun φ => φ.check E0 []))

/-- 4.1: the rights checks, soft well-formedness of `(E″, T″)`, the identifier limit on `E″′`,
then the facts the proofs use. -/
def validateRights (D : RightsDoc) : Except String Unit :=
  match checkRights D with
  | .error e => .error e
  | .ok () =>
    match VE.SoftNorms.validateSoft (correlate D) with
    | .error e => .error e
    | .ok () =>
      match (VE.SoftNorms.decisionNames (correlate D)).find? (fun n => n.utf8ByteSize > 64) with
      | some n => .error s!"ResourceLimit: identifier {n} exceeds 64 bytes"
      | none => if rightsSemanticCheck D then .ok () else .error "InvalidInput: rights document is not stratified"

/-- `validateRights` with soft well-formedness checked by `validateSoftOnce` (lean-first plan F5d). -/
def validateRightsOnce (D : RightsDoc) : Except String Unit :=
  match checkRights D with
  | .error e => .error e
  | .ok () =>
    match VE.SoftNorms.validateSoftOnce (correlate D) with
    | .error e => .error e
    | .ok () =>
      match (VE.SoftNorms.decisionNames (correlate D)).find? (fun n => n.utf8ByteSize > 64) with
      | some n => .error s!"ResourceLimit: identifier {n} exceeds 64 bytes"
      | none => if rightsSemanticCheck D then .ok () else .error "InvalidInput: rights document is not stratified"

theorem validateRightsOnce_eq (D : RightsDoc) : validateRightsOnce D = validateRights D := by
  unfold validateRightsOnce validateRights
  rw [VE.SoftNorms.validateSoftOnce_eq]

def WellFormedRights (D : RightsDoc) : Bool :=
  match validateRights D with
  | .ok () => true
  | .error _ => false

structure RightsValid (D : RightsDoc) : Prop where
  wfSoft : WellFormedSoft (correlate D) = true
  barOver : ∀ X ∈ (correlate D).T.nodes, ∀ B ∈ barNodes D, B.name ∉ X.over
  permNoDual : ∀ m, rightPermission D m = true → dualPerm (correlate D) m = none
  ownTyped : ∀ RN ∈ linesOf D, (ownGuard D RN.2).WellFormed
    (envAt (soften (correlate D)) (size (soften (correlate D)))) (sortsOf D RN.2).reverse
  selTyped : ∀ RN ∈ linesOf D, (selectsR D RN.2).WellFormed
    (envAt (soften (correlate D)) (size (soften (correlate D)))) (sortsOf D RN.2).reverse
  condTyped : ∀ RN ∈ linesOf D, ∀ n ∈ narrowings D RN.2, (condF D RN.2 n).WellFormed
    (envAt (soften (correlate D)) (size (soften (correlate D)))) (sortsOf D RN.2).reverse
  packTyped : ∀ RN ∈ linesOf D, (limPack D RN.2).WellFormed (envAt (soften (correlate D)) 0) (sortsOf D RN.2).reverse
  aimedTyped : ∀ RN ∈ linesOf D, ∀ m, ruleReading D = true → barReach D RN.2 = some m →
    (aimedF D m).WellFormed (envAt (soften (correlate D)) 0) (sortsOf D RN.2).reverse
  limTyped : ∀ φ ∈ limPremises D, φ.WellFormed (envAt (soften (correlate D)) 0) []

theorem rightsValid_of_wellFormed (D : RightsDoc) (h : WellFormedRights D = true) : RightsValid D := by
  unfold WellFormedRights validateRights at h
  split at h
  · rename_i heq
    split at heq
    · cases heq
    · rename_i hs
      split at heq
      · cases heq
      · rename_i hsoft
        split at heq
        · cases heq
        · split at heq
          · rename_i hsem
            have hw : WellFormedSoft (correlate D) = true := by
              unfold WellFormedSoft; rw [hsoft]
            simp only [rightsSemanticCheck, Bool.and_eq_true, List.all_eq_true, Bool.not_eq_true',
              beq_iff_eq] at hsem
            obtain ⟨⟨⟨hb, hd⟩, hl⟩, hp⟩ := hsem
            refine ⟨hw, fun X hX B hB hm => ?_, fun m hm => hd m (by
              simpa [rightPermission] using hm), fun RN hRN => ?_, fun RN hRN => ?_,
              fun RN hRN n hn => ?_, fun RN hRN => ?_, fun RN hRN m hr hm => ?_,
              fun φ hφ => (VE.check_iff_wellFormed _ _ _).mp (hp φ hφ)⟩
            · have := hb X hX B hB
              simp [hm] at this
            · exact (VE.check_iff_wellFormed _ _ _).mp (hl RN hRN).1.1.1.1
            · exact (VE.check_iff_wellFormed _ _ _).mp (hl RN hRN).1.1.1.2
            · exact (VE.check_iff_wellFormed _ _ _).mp ((hl RN hRN).1.1.2 n hn)
            · exact (VE.check_iff_wellFormed _ _ _).mp (hl RN hRN).1.2
            · have := (hl RN hRN).2
              rw [hm] at this
              simp only [hr, Bool.not_true, Bool.false_or] at this
              exact (VE.check_iff_wellFormed _ _ _).mp this
          · cases heq
  · cases h

/-! ## 9.2: what `correlate` changes and what it keeps -/

/-- 4.1 ⇒ soft well-formedness of `T″` over `E″`. -/
theorem correlate_wellFormed (D : RightsDoc) (h : WellFormedRights D = true) : WellFormedSoft (correlate D) = true :=
  (rightsValid_of_wellFormed D h).wfSoft

theorem correlate_shape (D : RightsDoc) (_h : WellFormedRights D = true) :
    (correlate D).E = envR D ∧ (correlate D).lits = D.soft.lits ∧ (correlate D).soft = D.soft.soft ∧
    (correlate D).T.regulated = D.soft.T.regulated ∧ (correlate D).T.definitions = D.soft.T.definitions ∧
    (correlate D).T.nodes = (linesOf D).map (fun RN => nodeOf D RN.2) ++ D.soft.T.nodes ++ barNodes D :=
  ⟨rfl, rfl, rfl, rfl, rfl, rfl⟩

theorem scopeLimits_nil (D : RightsDoc) (h : D.limits = []) (N : Line) : scopeLimits D N = [] := by
  simp [scopeLimits, h]

theorem barNodes_nil (D : RightsDoc) (h : D.bars = []) : barNodes D = [] := by
  simp [barNodes, ruleReading, h]

theorem correlate_identity (D : RightsDoc) (_h : WellFormedRights D = true)
    (hn : D.limits = [] ∧ (∀ R ∈ D.rs, ∀ N ∈ R.lines, N.kind ≠ .power ∧ N.fanOut = []) ∧ D.bars = []) :
    (correlate D).E = D.soft.E ∧
    (correlate D).T.nodes =
      (linesOf D).map (fun RN => { RN.2.node with guard := holderConj D RN.2 RN.2.node.guard }) ++ D.soft.T.nodes := by
  obtain ⟨hl, _, hb⟩ := hn
  refine ⟨envR_of_no_gen D (genDecls_nil D hl hb), ?_⟩
  simp only [correlate, barNodes_nil D hb, List.append_nil, nodeOf, limPackList, scopeLimits_nil D hl, if_true,
    ownGuard]

theorem holderConj_top (D : RightsDoc) (ht : ∀ R ∈ D.rs, R.guard = .top) (N : Line) (G : VE.Formula) :
    holderConj D N G = G := by
  unfold holderConj
  split
  · rename_i R hR
    rw [if_pos (ht R (List.mem_of_find?_eq_some hR))]
  · rfl

/-- Every `H_R` top as well: the whole soft document. -/
theorem correlate_identity_top (D : RightsDoc) (_h : WellFormedRights D = true)
    (hn : D.limits = [] ∧ (∀ R ∈ D.rs, ∀ N ∈ R.lines, N.kind ≠ .power ∧ N.fanOut = []) ∧ D.bars = [])
    (ht : ∀ R ∈ D.rs, R.guard = .top) :
    correlate D = flattenTop D := by
  obtain ⟨hl, _, hb⟩ := hn
  have hE := envR_of_no_gen D (genDecls_nil D hl hb)
  unfold correlate flattenTop
  rw [hE, barNodes_nil D hb, List.append_nil]
  have : (linesOf D).map (fun RN => nodeOf D RN.2) = (linesOf D).map (·.2.node) := by
    apply List.map_congr_left
    intro RN _
    simp only [nodeOf, limPackList, scopeLimits_nil D hl, if_true, List.append_nil, ownGuard,
      holderConj_top D ht]
  rw [this]

theorem correlate_identity_top_env (D : RightsDoc) (h : WellFormedRights D = true)
    (hn : D.limits = [] ∧ (∀ R ∈ D.rs, ∀ N ∈ R.lines, N.kind ≠ .power ∧ N.fanOut = []) ∧ D.bars = [])
    (ht : ∀ R ∈ D.rs, R.guard = .top) :
    envR D = D.soft.E ∧ envPrime (correlate D) = envPrime (flattenTop D) := by
  refine ⟨?_, by rw [correlate_identity_top D h hn ht]⟩
  have := (correlate_shape D h).1
  rw [← this, correlate_identity_top D h hn ht]
  rfl

end VE.Rights
