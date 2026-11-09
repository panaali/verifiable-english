import VE.Presupposition.Table
import VE.Readings.Doc

/-! # `admit`: the presupposition check (docs/spec/presupposition.md 4.7, "The check, in order")

`admitWith t fx` checks a decoded document's obligation block in spec 4.7's five steps under the candidate table
`t` and the fixed inputs `fx` of step 5; `admit := admitWith candidateTable admitInputs` (DRI ps-2a item 2). The
first failing step gives the answer. Inside step 4 every obligation is regenerated and its carrier checked in block
order (pass 1); then, in block order, each unresolved obligation's open set is compared with `expectedReadings`,
which reads the whole report (pass 2). In step 1 the block's size is charged before anything is walked; each
regenerated goal and each regenerated unit content is charged against W1's node budget where it is built. -/

namespace VE.Presupposition

/-- Step 1's limits: obligations per block, and W1's AST budget per regenerated formula. -/
def maxObligations : Nat := 256
def budget : String := "ResourceLimit: presuppositions"

def ensure (b : Bool) (e : String) : Except String Unit := if b then .ok () else .error e

def mapE {α β : Type} (f : α → Except String β) : List α → Except String (List β)
  | [] => .ok []
  | a :: as => do let b ← f a; let bs ← mapE f as; pure (b :: bs)

def allE {α : Type} (f : α → Except String Unit) : List α → Except String Unit
  | [] => .ok ()
  | a :: as => do f a; allE f as

/-- The id of the first obligation of the block that satisfies `p` (the diagnostic names it). -/
def firstOb (obs : List Obligation) (p : Obligation → Bool) : String := ((obs.find? p).map (·.id)).getD ""

/-! ## Step 2: ids, units and rows -/

def checkIds (D : PDoc) : List String → List Obligation → Except String Unit
  | _, [] => .ok ()
  | seen, o :: os => do
    ensure (!seen.contains o.id) s!"PresuppositionMismatch: {o.id}: id"
    ensure (unitOf D o.unit).isSome s!"PresuppositionMismatch: {o.id}: unit"
    ensure (rowNames.contains o.row) s!"PresuppositionUnknownRow: {o.id}: {o.row}"
    checkIds D (o.id :: seen) os

/-! ## Step 3: the base content of each unit with obligations -/

/-- A unit's base: its claim with the root goals peeled, or its rule with the recorded conditions peeled. -/
inductive Base where
  | claim (B : VE.Formula)
  | rule (N : VE.Norms.Node)
  deriving DecidableEq, Repr

/-- The roots of the unit's obligations in block order, its first unresolved one read as `k` (a second is refused
    in step 4). -/
def rootsWith (obs : List Obligation) (u : String) (k : Root) : List Root :=
  let os := obs.filter (·.unit == u)
  let first := (os.find? (·.carrier == .unresolved)).map (·.id)
  os.map (fun o => if some o.id == first then k else o.carrier.root)

def peelWith (rs : List Root) (a : VE.Formula) : Option VE.Formula :=
  peel (rs.filter (· == .asserted)).length (rs.filter (· == .conditioned)).length a

/-- The inverse of `k` steps of `conditionNode`. -/
def peelRule : Nat → VE.Norms.Node → Option VE.Norms.Node
  | 0, N => some N
  | k + 1, N => match N.guard with
    | .and g _ => peelRule k { N with guard := g }
    | _ => none

/-- `f`'s common value over a non-empty list. -/
def allSame {α β : Type} [DecidableEq β] (f : α → Option β) : List α → Option β
  | [] => none
  | a :: as => (f a).bind (fun b => if as.all (fun a' => f a' == some b) then some b else none)

def baseOf (D : PDoc) (obs : List Obligation) (x : DocUnit) : Option Base :=
  let nc (k : Root) := ((rootsWith obs x.id k).filter (· == .conditioned)).length
  match x.content with
  | .claim a => (peelWith (rootsWith obs x.id .bare) a).map .claim
  | .rule n => (D.norms.nodes.find? (·.name == n)).bind (fun M => (peelRule (nc .bare) M).map .rule)
  | .readings rs => match rs.head? with
    | some ⟨_, _, .claim _, _⟩ => (allSame (fun r => match r.content with
        | .claim a => peelWith (rootsWith obs x.id r.cand.root) a | .rule _ => none) rs).map .claim
    | some ⟨_, _, .rule _, _⟩ => (allSame (fun r => match r.content with
        | .rule M => peelRule (nc r.cand.root) M | .claim _ => none) rs).map .rule
    | none => none
  | .unformalised => none

/-- The units with obligations, each once (the first unit of its id), in document order. -/
def withObligations (D : PDoc) (obs : List Obligation) : List DocUnit :=
  D.units.filter (fun x => obs.any (·.unit == x.id) && unitOf D x.id == some x)

def isRuleUnit (x : DocUnit) : Bool := match x.content with
  | .rule _ => true
  | .readings (⟨_, _, .rule _, _⟩ :: _) => true
  | _ => false

def bases3 (D : PDoc) (obs : List Obligation) : Except String (List (DocUnit × Base)) :=
  mapE (fun x => match baseOf D obs x with
    | some b => .ok (x, b)
    | none => .error s!"PresuppositionMismatch: {firstOb obs (·.unit == x.id)}: {if isRuleUnit x then "rule" else "content"}")
    (withObligations D obs)

def basesOf (P : List (DocUnit × Base)) : List (String × VE.Formula) :=
  P.filterMap (fun x => match x.2 with | .claim B => some (x.1.id, B) | .rule _ => none)

/-- Every rule with the carriers' conditions removed: the fixed rules in place, then the open rules. -/
def baseTreeOf (D : PDoc) (P : List (DocUnit × Base)) : VE.Norms.Tree :=
  let ruleBase (fixed : Bool) (x : DocUnit × Base) : Option VE.Norms.Node := match x.1.content, x.2 with
    | .rule _, .rule N => if fixed then some N else none
    | .readings _, .rule N => if fixed then none else some N
    | _, _ => none
  { D.norms with nodes := D.norms.nodes.map (fun M => ((P.filterMap (ruleBase true)).find? (·.name == M.name)).getD M)
      ++ P.filterMap (ruleBase false) }

/-! ## Step 4: position, arguments and carrier, per obligation -/

/-- Pass 1's regeneration: the position locates, the arguments build, the located subformula is `strong`. -/
def regen (D : PDoc) (obs : List Obligation) (P : List (DocUnit × Base)) (T : VE.Norms.Tree) (o : Obligation) :
    Except String Checked :=
  let pos := s!"PresuppositionPosition: {o.id}"
  let mm (f : String) := s!"PresuppositionMismatch: {o.id}: {f}"
  match o.position, ((P.find? (·.1.id == o.unit)).map (·.2) : Option Base) with
  | .path p, some (.claim B) => match Frame.locate B p with
    | some (f, s) => do
      ensure (obs.all (fun d => d.unit != o.unit || match d.position with
        | .path q => !entersRestriction d.row q p | _ => true)) pos
      let r ← (buildReading o.row f.binders.length o.args.tuple).mapError mm
      ensure (s == r.strong) (mm "clause")
      ensure (VE.Bridge.formulaNodes (f.goal r.pre) ≤ VE.Limits.maxNodes) budget
      pure ⟨o, f, r.pre, some r, f.goal r.pre, f.cls⟩
    | none => .error pos
  | .ruleAct n, some (.rule N₀) => do
    ensure (N₀.name == n) pos
    match T.nodes.find? (·.name == n) with
    | none => .error pos
    | some N => match D.norms.regulated.find? (·.name == N.pred) with
      | none => .error (mm "rule")
      | some r => do
        let pre ← (buildPre o.row r.sorts.length o.args.tuple).mapError mm
        ensure (VE.Bridge.formulaNodes (ruleGoal r N pre) ≤ VE.Limits.maxNodes) budget
        pure ⟨o, .hole, pre, none, ruleGoal r N pre, .ruleAct⟩
  | .heading, some (.claim _) => do
    let pre ← (buildPre o.row 0 o.args.tuple).mapError mm
    ensure (VE.Bridge.formulaNodes pre ≤ VE.Limits.maxNodes) budget
    pure ⟨o, .hole, pre, none, pre, .top⟩
  | _, _ => .error pos

def provedOk (D : PDoc) (c : Checked) (n : String) : Bool :=
  match nodeCertificate D n with
  | some cert => VE.Tableau.checkCertificate (env D) (premisesBefore D c.ob.unit) c.goal cert
  | none => false

/-- R-7: a conditioned rule, or an unresolved rule obligation whose cell lists conditioned, needs `unspecified`. -/
def needsUnspec (t : CandidateTable) (o : Obligation) : Bool :=
  o.carrier == .conditioned || (o.carrier == .unresolved && (t o.row .ruleAct).contains .conditioned)

/-- The unit an assumed or unconditional carrier names, and the predicate of a rule-act obligation's rule. -/
def Carrier.unitName : Carrier → String
  | .assumed u | .unconditional u => u
  | _ => ""
def rulePred (T : VE.Norms.Tree) (o : Obligation) : String := match o.position with
  | .ruleAct n => ((T.nodes.find? (·.name == n)).map (·.pred)).getD n
  | _ => ""

/-- Pass 1's carrier check, in spec 4.7's order. -/
def carrierOk (t : CandidateTable) (D : PDoc) (T : VE.Norms.Tree) (c : Checked) : Except String Unit := do
  ensure (match c.ob.carrier with | .proved n => provedOk D c n | _ => true)
    s!"PresuppositionCertificate: {c.ob.id}"
  ensure (match c.ob.carrier with
    | .assumed u => unitAsserted D u && unitContent D u == some c.goal && (c.ob.position == .heading || u != c.ob.unit)
    | .unconditional u => unitAsserted D u && unitContent D u == some (c.frame.close c.pre) && u != c.ob.unit
    | _ => true) s!"PresuppositionAssumedUnit: {c.ob.id}: {c.ob.carrier.unitName}"
  ensure (c.ob.position != .heading || match c.ob.carrier with | .proved _ | .assumed _ => true | _ => false)
    s!"PresuppositionCandidates: {c.ob.id}"
  ensure (match c.ob.position with
    | .ruleAct n => !needsUnspec t c.ob || T.nodes.any (fun N => N.name == n && D.unspec.contains N.pred)
    | _ => true) s!"PresuppositionDefault: {c.ob.id}: {rulePred T c.ob}"
  ensure (match c.ob.carrier.cand with | some k => c.ob.position == .heading || carrierAllowed t c k | none => true)
    s!"PresuppositionCandidates: {c.ob.id}"
  ensure (c.ob.carrier != .unresolved || (unitReadings D c.ob.unit).isSome) s!"PresuppositionUnresolved: {c.ob.id}"

/-- Pass 2: an unresolved obligation's unit carries exactly the expected readings, at least two, and it is the
    unit's first unresolved obligation. -/
def openOk (t : CandidateTable) (D : PDoc) (R : Report) (c : Checked) : Except String Unit :=
  if c.ob.carrier == .unresolved then
    ensure ((match expectedReadings t R c with
        | some rs => unitReadings D c.ob.unit == some rs && decide (2 ≤ rs.length)
        | none => false) &&
      (R.checked.find? (fun d => d.ob.unit == c.ob.unit && d.ob.carrier == .unresolved)).map (·.ob.id) ==
        some c.ob.id) s!"PresuppositionCandidates: {c.ob.id}"
  else .ok ()

/-! ## Step 5: contents, rules, the soft chain and separation, per unit -/

/-- Step 5's fixed inputs (spec 4.7 step 5; DRI ps-2a item 2): the readings environment's chain, read here as
    `abstention` reads `re.chain` (`lean/VE/Readings/Wire.lean`). -/
structure Fixed where
  chain : VE.Readings.Chain

def softText : String := "UnsupportedProfile: a conditioned rule reading needs the norms chain (presupposition)"

/-- R-8 (A26): on the soft chain an open set with a conditioned rule reading is refused before separation. -/
def softOk (fx : Fixed) (rs : List RReading) : Bool :=
  fx.chain != .soft || !rs.any (fun r => r.cand == .conditioned && match r.content with | .rule _ => true | _ => false)

def unitsOk (fx : Fixed) (D : PDoc) (obs : List Obligation) (R : Report) : Except String Unit := do
  allE (fun x => do
    let a := carried (unitModes R x.1) x.2
    ensure (VE.Bridge.formulaNodes a ≤ VE.Limits.maxNodes) budget
    ensure (R.checked.any (fun c => c.ob.unit == x.1 && c.ob.carrier == .unresolved) || unitContent D x.1 == some a)
      s!"PresuppositionMismatch: {firstOb obs (·.unit == x.1)}: content") R.bases
  allE (fun N => ensure (D.norms.nodes.all (fun M => M.name != N.name || M == (ruleConditions R N.name).foldl conditionNode N))
      s!"PresuppositionMismatch: {firstOb obs (·.position == .ruleAct N.name)}: rule") R.baseTree.nodes
  ensure (VE.Norms.WellFormed ⟨D.E, D.lits, D.norms⟩ && VE.Norms.WellFormed ⟨D.E, D.lits, R.baseTree⟩)
    s!"PresuppositionMismatch: {firstOb obs (fun o => match o.position with | .ruleAct _ => true | _ => false)}: rule"
  allE (fun x => match x.content with
    | .readings rs => ensure (softOk fx rs) softText
    | _ => .ok ()) (withObligations D obs)

/-! ## `admit` -/

def admitWith (t : CandidateTable) (fx : Fixed) (D : PDoc) : Except String Report :=
  match D.block with
  | none => .error "PresuppositionMismatch: no block"
  | some obs => do
    ensure (obs.length ≤ maxObligations) budget
    checkIds D [] obs
    let P ← bases3 D obs
    let T := baseTreeOf D P
    let cs ← mapE (fun o => do let c ← regen D obs P T o; carrierOk t D T c; pure c) obs
    let R : Report := ⟨cs, basesOf P, T⟩
    allE (openOk t D R) cs
    unitsOk fx D obs R
    pure R

/-- `admit`'s fixed inputs: the norms chain. -/
def admitInputs : Fixed := ⟨.norms⟩

def admit : PDoc → Except String Report := admitWith candidateTable admitInputs

/-- The document mode's `presuppositions` field: absent without the block (PS-4 puts it in the answer). -/
def admitBase (_ : PDoc) : Option (Except String Report) := none
def admitWrapped (D : PDoc) : Option (Except String Report) := D.block.map (fun _ => admit D)

end VE.Presupposition
