/-
Stub of weighing.md (WG-1's re-elaboration, 2026-11-02), generated from its Lean blocks by
manage-agents/debates/wg-1/gen-stub.py. Checked with spec-stub-check.sh against main; see weighing.md's header.
Sections 1 and 2.5 are the spec's text. Each theorem of sections 5 and 6 is `def T binders : Prop := C`, the same text.
The fixtures below the generated part compute every value of section 7 that does not need WG-3's route.
-/
import VE.Acts.Elaborate
import VE.Closure.Order
import VE.Compose.Dispatch
import VE.NormDefaults.LayeredEntail
import VE.Risk.Wire
import VE.Route.Gate
import VE.SoftNorms.Semantics
import VE.Weighing.Zone
import VE.Defaults.Examples
import VE.EnglishGrammar.SourceWords

set_option linter.unusedVariables false

open Lean

/-- Stand-in for AP's refusal (weighing.md 1.6), which WG-2 factors out of `Acts/Elaborate.lean`. -/
def VE.Acts.splitRefusal (role name : String) : String :=
  s!"InvalidInput: {role} {name} names a predicate that is split into parts; name one of its parts"

/-- Stand-in for the NEW profile filter (owner composition), generalised from `withoutDocumentLayers`. -/
def VE.Compose.withoutProfiles (qs : List String) (environment : Json) : Json :=
  match environment.getObjVal? "profiles" with
  | .ok (.arr ps) => environment.setObjVal! "profiles" (.arr (ps.filter fun p => !qs.any (.str · == p)))
  | _ => environment

/-- `withoutDocumentLayers` is the filter's instance at `documentLayers`. -/
theorem VE.Compose.withoutDocumentLayers_eq :
    VE.Compose.withoutDocumentLayers = VE.Compose.withoutProfiles VE.Compose.documentLayers := rfl

namespace VE.Weighing
open VE.Norms VE.SoftNorms
universe u




inductive CondKind | necessary | sufficient
  deriving DecidableEq, Repr

def CondKind.label : CondKind → String
  | .necessary => "necessary"
  | .sufficient => "sufficient"

/-- The open decision a condition constrains (soft 1.3). -/
inductive Target
  | outweighs (act lower higher : String)
  | off (rule party : String)
  deriving DecidableEq, Repr

structure CondDecl where
  target : Target
  kind : CondKind
  condition : VE.Formula    -- context (targetSorts target).reverse; base predicates of E only; quantifier-free;
                            -- decoded through the chain's guard decoder (3.1)
  deriving DecidableEq, Repr

structure FactorDecl where
  target : Target
  factors : List String
  deriving DecidableEq, Repr

structure GrantDecl where
  rule : String
  party : String
  grantor : String
  predicate : String        -- a base predicate with instruction_of = grantor, over the rule's argument sorts
  deriving DecidableEq, Repr

/-- The decoded block. Only `always` edges are on the wire: "generally outranks" is an input synonym of a plain
    "outranks" (plan D5). -/
structure WeighEnv where
  always : List (String × String)
  conditions : List CondDecl
  factors : List FactorDecl
  grants : List GrantDecl
  deriving DecidableEq, Repr

def WeighEnv.empty : WeighEnv := ⟨[], [], [], []⟩

/-- A soft document with its block, and AP's split map (empty unless `acts@0` split a rule or an act). -/
structure WeighDoc where
  D : SoftDoc
  W : WeighEnv
  split : VE.Acts.SplitMap


/-- Soft's ranks and declared edges as QS-1's order (`atLeast := reachEval .star`). -/
def rankOrder (Wd : WeighDoc) : VE.Closure.Order String := ⟨Wd.D.soft.ranks, Wd.D.soft.outranks⟩

/-- `(H, L)` is strict: some `always` edge `(a, b)` has `H` at or above `a` and `b` at or above `L`. -/
def strictPair (Wd : WeighDoc) (H L : String) : Bool :=
  Wd.W.always.any (fun e => (rankOrder Wd).atLeast H e.1 && (rankOrder Wd).atLeast e.2 L)

def chainEdges : List String → List (String × String)
  | a :: b :: rest => (a, b) :: chainEdges (b :: rest)
  | _ => []

/-- A chain of declared edges from `H` down to `L`. -/
def RankChain (Wd : WeighDoc) (H L : String) (c : List String) : Prop :=
  c.head? = some H ∧ c.getLast? = some L ∧ 2 ≤ c.length ∧ ∀ e ∈ chainEdges c, e ∈ Wd.D.soft.outranks

/-- Every chain of declared edges from `a` down to `L`, with fuel (the rank graph is acyclic, soft 4.1). -/
def chainsFrom (E : List (String × String)) (L : String) : Nat → String → List (List String)
  | 0, _ => []
  | f + 1, a => (E.filter (·.1 == a)).flatMap (fun e =>
      if e.2 == L then [[a, L]] else (chainsFrom E L f e.2).map (a :: ·))

def chainLt (c d : List String) : Bool :=
  c.length < d.length || (c.length == d.length && decide (c < d))

/-- The chain the paraphrase shows (2.3): the shortest chain from `H` to `L` that contains an `always` edge, the
    least in `String` list order on ties; `none` exactly when the pair is not strict (`strictWitness_isSome`).
    Display only; at most 2^14 chains on 16 ranks. -/
def strictWitness (Wd : WeighDoc) (H L : String) : Option (List String) :=
  ((chainsFrom Wd.D.soft.outranks L Wd.D.soft.ranks.length H).filter
      (fun c => (chainEdges c).any (Wd.W.always.contains ·))).foldl
    (fun best c => match best with
      | none => some c
      | some b => if chainLt c b then some c else some b) none


def nodeNamed (D : SoftDoc) (n : String) : Option SoftNode := D.T.nodes.find? (·.name == n)

def ruleSorts (Wd : WeighDoc) (n : String) : List String :=
  match nodeNamed Wd.D n with
  | some N => sortsOf Wd.D N.pred
  | none => []

def targetSorts (Wd : WeighDoc) : Target → List String
  | .outweighs a _ _ => actSortsOf Wd.D a
  | .off n _ => ruleSorts Wd n

def targetF (Wd : WeighDoc) : Target → VE.Formula
  | .outweighs a L H => outweighsF Wd.D a L H
  | .off n π => match nodeNamed Wd.D n with
    | some N => atom (offName N π) (sortsOf Wd.D N.pred)
    | none => .bottom

/-- The decision exists in `E′` (soft 1.3): an `outweighs` triple of a comparable colliding pair under the holistic
    flag, or a switch the rule declares. -/
def targetExists (Wd : WeighDoc) : Target → Bool
  | .outweighs a L H => (outweighsTriples Wd.D).contains (a, L, H)
  | .off n π => match nodeNamed Wd.D n with
    | some N => N.alterable.contains π
    | none => false

def renderTarget : Target → String
  | .outweighs a L H => s!"outweighs {a}, {L}, {H}"
  | .off n π => s!"off rule {n}, {π}"


abbrev RequestPath := VE.NormDefaults.Packs.RequestPath

def blockPath : RequestPath := ["environment", "vocabulary", "weighing"]

/-- `Str_T`: one premise per `outweighs` decision of a strict pair, in `outweighsTriples` order; its origin is the
    first `always` edge (block order) through which the pair is strict. -/
def strengthEntries (Wd : WeighDoc) : List (String × VE.Formula × RequestPath) :=
  (outweighsTriples Wd.D).filterMap (fun (a, L, H) =>
    match Wd.W.always.zipIdx.find? (fun (e, _) => (rankOrder Wd).atLeast H e.1 && (rankOrder Wd).atLeast e.2 L) with
    | some (_, i) => some (s!"weigh:strength:{H}:{L}:{a}",
        bindAll (actSortsOf Wd.D a) (.not (outweighsF Wd.D a L H)), blockPath ++ ["always", toString i])
    | none => none)

/-- The one premise generator (soft's `excPremisesOf` shape). -/
def condPremise (Wd : WeighDoc) (c : CondDecl) : VE.Formula :=
  match c.kind with
  | .sufficient => bindAll (targetSorts Wd c.target) (.implies c.condition (targetF Wd c.target))
  | .necessary => bindAll (targetSorts Wd c.target) (.implies (targetF Wd c.target) c.condition)

/-- `Dec_T`, in block order. -/
def condEntries (Wd : WeighDoc) : List (String × VE.Formula × RequestPath) :=
  Wd.W.conditions.zipIdx.map (fun (c, i) =>
    (s!"weigh:condition:{i}:{c.kind.label}", condPremise Wd c, blockPath ++ ["conditions", toString i]))

def grantEdges (Wd : WeighDoc) (n : String) : List (String × String) :=
  (Wd.W.grants.filter (·.rule == n)).map (fun g => (g.party, g.grantor))

/-- `ρ` is reached from `π` through the grants on rule `n`: `π`'s grantor, that grantor's grantor, … -/
def grantReach (Wd : WeighDoc) (n π ρ : String) : Bool := VE.Closure.reachEval .plus (grantEdges Wd n) π ρ

/-- The parties `π`'s switch on rule `n` is granted through, in declared party order, `π` excluded (on an accepted
    document `π` never reaches itself: grant cycles are refused, 4.5). -/
def grantedThrough (Wd : WeighDoc) (n π : String) : List String :=
  Wd.D.soft.parties.filter (fun ρ => ρ != π && grantReach Wd n π ρ)

/-- `Grant_T` as necessary `.off` conditions on the grantee's switch (debate E3): the grant itself, then for each
    party the switch is granted through, that party's necessary switch conditions and that party's own grant. -/
def grantConds (Wd : WeighDoc) : List (String × CondDecl × RequestPath) :=
  Wd.W.grants.zipIdx.flatMap (fun (g, j) =>
    let tgt := Target.off g.rule g.party
    (s!"weigh:grant:{g.rule}:{g.party}", ⟨tgt, .necessary, atom g.predicate (ruleSorts Wd g.rule)⟩,
        blockPath ++ ["grants", toString j]) ::
    (grantedThrough Wd g.rule g.party).flatMap (fun ρ =>
      (Wd.W.conditions.zipIdx.filterMap (fun (c, i) =>
        if c.target == Target.off g.rule ρ && c.kind == .necessary then
          some (s!"weigh:grant:{g.rule}:{g.party}:condition:{i}", ⟨tgt, .necessary, c.condition⟩,
            blockPath ++ ["conditions", toString i])
        else none)) ++
      (Wd.W.grants.zipIdx.filterMap (fun (g', k) =>
        if g'.rule == g.rule && g'.party == ρ then
          some (s!"weigh:grant:{g.rule}:{g.party}:grant:{ρ}",
            ⟨tgt, .necessary, atom g'.predicate (ruleSorts Wd g.rule)⟩, blockPath ++ ["grants", toString k])
        else none))))

def grantEntries (Wd : WeighDoc) : List (String × VE.Formula × RequestPath) :=
  (grantConds Wd).map (fun (l, c, p) => (l, condPremise Wd c, p))

/-- `Weigh_T := Str_T ++ Dec_T ++ Grant_T`, each premise with its label and the request path of its entry. -/
def weighEntries (Wd : WeighDoc) : List (String × VE.Formula × RequestPath) :=
  strengthEntries Wd ++ condEntries Wd ++ grantEntries Wd

def strengthPremises (Wd : WeighDoc) : List VE.Formula := (strengthEntries Wd).map (·.2.1)
def weighLabelled (Wd : WeighDoc) : List (String × VE.Formula) := (weighEntries Wd).map (fun (l, φ, _) => (l, φ))
def weighOrigins (Wd : WeighDoc) : List (String × RequestPath) := (weighEntries Wd).map (fun (l, _, p) => (l, p))
def weighPremises (Wd : WeighDoc) : List VE.Formula := (weighLabelled Wd).map (·.2)

/-- The decision a target names, as soft's key (profile-composition 1.9: a reader finds a decision by its key). -/
def Target.key : Target → DecisionKey
  | .outweighs a L H => .outweighs a L H
  | .off n π => .off n π

/-- `Pack.conditions` (PK-1's field, profile-composition 1.9): each stated sufficient condition with its decision,
    in block order. Necessary conditions and grants export nothing. -/
def weighConditions (Wd : WeighDoc) : List (DecisionKey × VE.Formula) :=
  Wd.W.conditions.filterMap (fun c => if c.kind == .sufficient then some (c.target.key, c.condition) else none)


def atomsOf : VE.Formula → List VE.Formula
  | .unary p t => [.unary p t]
  | .binary p t w => [.binary p t w]
  | .eq t w => [.eq t w]
  | .not a => atomsOf a
  | .and a b | .or a b | .implies a b => atomsOf a ++ atomsOf b
  | _ => []

/-- A formula read propositionally: each distinct atom is a variable. -/
def evalProp (v : VE.Formula → Bool) : VE.Formula → Bool
  | .top => true
  | .bottom => false
  | .unary p t => v (.unary p t)
  | .binary p t w => v (.binary p t w)
  | .eq t w => v (.eq t w)
  | .not a => !evalProp v a
  | .and a b => evalProp v a && evalProp v b
  | .or a b => evalProp v a || evalProp v b
  | .implies a b => !evalProp v a || evalProp v b
  | .all _ _ | .ex _ _ => false

def subsetsOf {α : Type} : List α → List (List α)
  | [] => [[]]
  | x :: xs => (subsetsOf xs).map (x :: ·) ++ subsetsOf xs

def maxPropAtoms : Nat := 12

def propAtoms (a b : VE.Formula) : List VE.Formula := (atomsOf a ++ atomsOf b).eraseDups

/-- `a → b` holds under every truth assignment to their atoms. Sound (`propImplies_sound`), not complete: equality
    and definitions are not read (W-θ12). Decided exactly; it never searches. -/
def propImplies (a b : VE.Formula) : Bool :=
  VE.Norms.Formula.qfree a && VE.Norms.Formula.qfree b && decide ((propAtoms a b).length ≤ maxPropAtoms) &&
    (subsetsOf (propAtoms a b)).all (fun t =>
      !evalProp (fun φ => t.contains φ) a || evalProp (fun φ => t.contains φ) b)


def targetCheck (Wd : WeighDoc) (t : Target) : Except String Unit := do
  match t with
  | .outweighs a _ _ => if Wd.split.preds.any (·.2.1 == a) then throw (VE.Acts.splitRefusal "act" a)
  | .off n _ => if Wd.split.rules.any (·.2.1 == n) then throw (VE.Acts.splitRefusal "rule" n)
  unless targetExists Wd t do throw s!"NoSuchDecision: {renderTarget t}"

/-- Section 4, steps 3 to 7, in order. -/
def checkWeigh (Wd : WeighDoc) : Except String Unit := do
  let D := Wd.D
  for e in Wd.W.always do
    unless D.soft.outranks.contains e do throw s!"StrengthOnUndeclaredEdge: {e.1}, {e.2}"
    if Wd.W.always.count e > 1 then throw s!"DuplicateDeclaration: strength {e.1}, {e.2}"
  for (c, i) in Wd.W.conditions.zipIdx do
    targetCheck Wd c.target
    match c.target, c.kind with
    | .off _ _, .sufficient => throw s!"InvalidInput: condition {i} on a switch must be necessary"
    | .outweighs _ L H, _ =>
      if strictPair Wd H L then throw s!"ConditionOnStrictPair: {renderTarget c.target}"
    | _, _ => pure ()
    let Γ := (targetSorts Wd c.target).reverse
    typeDiagnostic D.E Γ c.condition
    unless c.condition.check D.E Γ do throw s!"InvalidInput: ill-typed condition {i}"
    if let some q := (preds c.condition).find? (fun q => definedOrRegulated D q || reservedPredicate q) then
      throw s!"InvalidInput: condition {i} mentions {q}"
    unless VE.Norms.Formula.qfree c.condition do throw s!"InvalidInput: condition {i} is not quantifier-free"
  for (f, i) in Wd.W.factors.zipIdx do
    targetCheck Wd f.target
    unless f.factors.length ≤ 16 && f.factors.all (·.utf8ByteSize ≤ 200) do
      throw s!"InvalidInput: invalid factors {i}"
  for g in Wd.W.grants do
    if (Wd.W.grants.filter (fun g' => g'.rule == g.rule && g'.party == g.party)).length > 1 then
      throw s!"DuplicateDeclaration: grant {g.rule}, {g.party}"
    targetCheck Wd (.off g.rule g.party)
    unless targetExists Wd (.off g.rule g.grantor) do
      throw s!"DelegationExceedsGrantor: rule {g.rule}, {g.party}, {g.grantor}"
    unless D.soft.instructionOf.contains (g.predicate, g.grantor) do
      throw s!"GrantNotAttributed: {g.predicate}, {g.grantor}"
    unless D.E.predicates g.predicate == some (ruleSorts Wd g.rule) do
      throw s!"InvalidInput: grant predicate {g.predicate} does not take the arguments of rule {g.rule}"
  for g in Wd.W.grants do
    if grantReach Wd g.rule g.party g.party then throw s!"DelegationCycle: rule {g.rule}, {g.party}"
  for (s, i) in Wd.W.conditions.zipIdx do
    if s.kind == .sufficient then
      for (n, j) in Wd.W.conditions.zipIdx do
        if n.kind == .necessary && n.target == s.target then
          if (propAtoms s.condition n.condition).length > maxPropAtoms then
            throw s!"ResourceLimit: conditions {i}, {j}"
          unless propImplies s.condition n.condition do
            throw s!"ConditionsDisagree: the checker cannot show that condition {i} implies condition {j}"
  for (l, φ) in weighLabelled Wd do
    unless withinLimits φ do throw s!"ResourceLimit: generated weighing premise {l}"

def weighWarnings (Wd : WeighDoc) : List String :=
  if Wd.D.soft.outranking = .strict then Wd.W.always.map (fun e => s!"StrengthInert: {e.1}, {e.2}") else []

def WellFormedWeigh (Wd : WeighDoc) : Bool :=
  WellFormedSoft Wd.D && (match checkWeigh Wd with
    | .ok () => true
    | .error _ => false)


/-- PK-1's `weighing` pack: it constrains existing decisions and declares no symbol and no constant. -/
def weighPack (Wd : WeighDoc) : VE.NormDefaults.Packs.Pack :=
  ⟨"weighing", .constraint, [], [], weighLabelled Wd, weighOrigins Wd, weighConditions Wd⟩

/-- AR-10's row in `Compose/Dispatch.lean`'s `baseRows`. `norm-defaults@0` is required because the layered branch
    runs only when it is listed (plan D11). `rights@0` is refused until AR-10's composition proof and a fixture both
    cover the combination (ruling item 12). -/
def weighingRow : VE.Compose.ProfileRow :=
  ⟨"weighing@0", ["norm-defaults@0", "norms@0", "soft-norms@0"], VE.Compose.refusing "weighing@0" ["rights@0"],
    "pack", .pack "weighing"⟩


namespace Wire
open Lean

def blockOf (environment : Json) : Option Json :=
  ((environment.getObjValD "vocabulary").getObjVal? "weighing").toOption

/-- The environment the soft decoder receives: `weighing@0` and the `weighing` block removed, nothing else. Total:
    a non-object is returned unchanged, `profiles` and `vocabulary` are rewritten only when present, and
    `Json.setObjVal!` is applied only to an object. The block is dropped by `VE.Risk.Wire.dropField` (no second copy),
    and the profile by the profile filter `VE.Compose.withoutProfiles` (NEW, owner composition), generalised from
    `withoutDocumentLayers`, which becomes `withoutProfiles documentLayers`. Weighing is not a document layer: an
    environment decoder reads its block. -/
def stripWeighing (environment : Json) : Json :=
  match VE.Bridge.fields environment with
  | .ok kvs => VE.Compose.withoutProfiles ["weighing@0"] (Json.mkObj (kvs.map (fun (k, v) =>
      (k, if k == "vocabulary" then VE.Risk.Wire.dropField "weighing" v else v))))
  | .error _ => environment

/-- The case with its environment stripped; total in the same way (`stripCase {} = {}`). -/
def stripCase (j : Json) : Json :=
  match VE.Bridge.fields j with
  | .ok kvs => Json.mkObj (kvs.map (fun (k, v) => (k, if k == "environment" then stripWeighing v else v)))
  | .error _ => j

/-- WG-3's step-1 gate (3.2 step 1, diagnostic 4.1), on the original environment, before anything is stripped: the
    envelope's profile list (a string array), then AR-10's gate over it (sorted, unique, `weighingRow`'s
    prerequisites present and its refused profiles absent, in AR-10's fault order and texts), then a `weighing` block
    only with `weighing@0`. -/
def weighGate (environment : Json) : Except String Unit := do
  let ps ← VE.Route.Gate.profilesOf environment
  discard (VE.Compose.gateOf VE.Compose.profileTable ps)
  if !ps.contains "weighing@0" && (blockOf environment).isSome then
    throw "UnsupportedProfile: the weighing block requires weighing@0"

/-- The decoded document without its identity fields `envId` and `docHash`: everything a layered kind reads.
    `D` carries `D.E`; WG-3's decoder takes `baseEnv` from the stripped environment (the block declares no base
    symbol). PK-1's `L.packs` replaced `labelled` and `rightsCount` on `main`. -/
def LayeredU.core (L : VE.NormDefaults.Wire.LayeredU) :=
  (L.route, L.D, L.U, L.packs, L.sitVocab, L.baseEnv)

end Wire


/-- en-wg's value: 1.1's objects, plus the edge E2's input synonym repeats. -/
inductive WeighStatement
  | always (a b : String)
  | edge (a b : String)
  | condition (c : CondDecl)
  | factors (f : FactorDecl)
  | grant (g : GrantDecl)
  deriving DecidableEq, Repr

/-- A sentence's form with its slots resolved. -/
inductive WeighFrame
  | always (a b : String)
  | generally (a b : String)
  | onlyWhen (act lower higher : String) (c : VE.Formula)
  | whenever (act lower higher : String) (c : VE.Formula)
  | account (act lower higher : String) (fs : List String)
  | switchOnly (party rule : String) (c : VE.Formula)
  | switchWhen (party rule : String) (c : VE.Formula)
  | allows (party rule grantor : String)
  | allowsNamely (party rule grantor predicate : String)
  deriving DecidableEq, Repr

/-- E7's candidates: the predicates attributed to `g`, typed over rule `n`'s argument sorts, in `instruction_of` order. -/
def grantCandidates (D : SoftDoc) (n g : String) : List String :=
  (D.soft.instructionOf.filter (fun e =>
    e.2 == g && D.E.predicates e.1 == some (ruleSorts ⟨D, WeighEnv.empty, ⟨[], []⟩⟩ n))).map (·.1)

def generallyRefusal (a b : String) : String := s!"GenerallyUnderStrictOutranking: {a}, {b}"
def switchWhenRefusal : String := "InvalidInput: a switch condition must say \"only when\""
def noGrantRefusal (n g : String) : String :=
  s!"InvalidInput: rule {n}: no predicate records an instruction of {g} over this rule's arguments; declare one first"
/-- `verbal` is the predicate's verbalisation (soft's `instruction_of` legend line): a reader never sees a symbol. -/
def severalGrantsRefusal (verbal : String → String) (n g : String) (ps : List String) : String :=
  s!"InvalidInput: rule {n}: several predicates record an instruction of {g}; add one of: " ++
    "; ".intercalate (ps.map (fun p => s!"namely where {verbal p}"))

/-- The object of a frame, or its refusal. Block-level faults stay `checkWeigh`'s (1.6). -/
def readFrame (D : SoftDoc) (verbal : String → String) : WeighFrame → Except String WeighStatement
  | .always a b => .ok (.always a b)
  | .generally a b =>
    if D.soft.outranking = .strict then .error (generallyRefusal a b) else .ok (.edge a b)
  | .onlyWhen x l h c => .ok (.condition ⟨.outweighs x l h, .necessary, c⟩)
  | .whenever x l h c => .ok (.condition ⟨.outweighs x l h, .sufficient, c⟩)
  | .account x l h fs => .ok (.factors ⟨.outweighs x l h, fs⟩)
  | .switchOnly π n c => .ok (.condition ⟨.off n π, .necessary, c⟩)
  | .switchWhen _ _ _ => .error switchWhenRefusal
  | .allowsNamely π n g p => .ok (.grant ⟨n, π, g, p⟩)
  | .allows π n g =>
    match grantCandidates D n g with
    | [] => .error (noGrantRefusal n g)
    | [p] => .ok (.grant ⟨n, π, g, p⟩)
    | ps => .error (severalGrantsRefusal verbal n g ps)




/-- The word row in en-sw's `SourceWords.lean` (2): *generally* in the rank frame is the plain sentence. -/
def generallyRow : VE.EnglishGrammar.SourceWordRow :=
  ⟨"generally", "<Rank a> generally outranks <rank b>.", "weighing@0", "en-wg",
    .fixed "<Rank a> outranks <rank b>."⟩


section Theorems5


/-- A strict pair is ordered. -/
def strictPair_outranks (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (H L : String)
    (hs : strictPair Wd H L = true) : Prop :=
  outranksPlus Wd.D.soft H L = true

/-- An `always` edge is a strict pair. -/
def strictPair_of_always (Wd : WeighDoc) (a b : String) (hab : (a, b) ∈ Wd.W.always) : Prop :=
  strictPair Wd a b = true

/-- Strictness is inherited downward and upward along the order. -/
def strictPair_down (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (H M L : String)
    (h₁ : strictPair Wd H M = true) (h₂ : outranksPlus Wd.D.soft M L = true) : Prop :=
  strictPair Wd H L = true
def strictPair_up (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (H M L : String)
    (h₁ : outranksPlus Wd.D.soft H M = true) (h₂ : strictPair Wd M L = true) : Prop :=
  strictPair Wd H L = true

/-- D4, exactly: a pair is holistic iff no chain of declared edges from `H` to `L` contains an `always` edge. -/
def holistic_iff_no_always_chain (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (H L : String) : Prop :=
  strictPair Wd H L = false ↔ ∀ c, RankChain Wd H L c → ∀ e ∈ chainEdges c, e ∉ Wd.W.always

/-- The paraphrase names a chain exactly for strict pairs, and the chain it names is one. -/
def strictWitness_isSome (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (H L : String) : Prop :=
  (strictWitness Wd H L).isSome = strictPair Wd H L
def strictWitness_chain (Wd : WeighDoc) (H L : String) (c : List String)
    (hc : strictWitness Wd H L = some c) : Prop :=
  RankChain Wd H L c ∧ ∃ e ∈ chainEdges c, e ∈ Wd.W.always

/-- `Str_T` has a premise exactly for the `outweighs` decisions of strict pairs, queried at declared ranks and a
    declared predicate. -/
def strength_iff (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (a L H : String)
    (hL : L ∈ Wd.D.soft.ranks) (hH : H ∈ Wd.D.soft.ranks)
    (ha : ∃ ss, Wd.D.E.predicates a = some ss) : Prop :=
  bindAll (actSortsOf Wd.D a) (.not (outweighsF Wd.D a L H)) ∈ strengthPremises Wd ↔
      (a, L, H) ∈ outweighsTriples Wd.D ∧ strictPair Wd H L = true


/-- In every structure satisfying `Str_T`, an effective higher default rule dominates a colliding lower default
    rule of a strict pair. Fixtures W-α, W-β1. -/
def always_dominates (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (strengthPremises Wd)) (M N : SoftNode) (hM : M ∈ Wd.D.T.nodes) (hN : N ∈ Wd.D.T.nodes)
    (hMd : M.mode = .default) (hNd : N.mode = .default) (hi : Incompatible Wd.D M N = true)
    (hh : higher Wd.D M N = true) (hs : strictPair Wd (rk M) (rk N) = true)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (actSortsOf Wd.D (act Wd.D N)) vs)
    (heff : EffD Wd.D S (tupleVal vs) (rankFuel Wd.D) M) : Prop :=
  DominatedD Wd.D S (tupleVal vs) (rankFuel Wd.D) N

/-- ... and the lower rule never dominates the higher one by override: `DomWithD`'s override disjunct for `M` with
    opponent `N` is false (under the strict flag it is false by its first conjunct). Fixtures W-α, W-α′, W-β1. -/
def always_no_override (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (strengthPremises Wd)) (M N : SoftNode) (hM : M ∈ Wd.D.T.nodes) (hN : N ∈ Wd.D.T.nodes)
    (hMd : M.mode = .default) (hNd : N.mode = .default) (hi : Incompatible Wd.D M N = true)
    (hh : higher Wd.D M N = true) (hs : strictPair Wd (rk M) (rk N) = true)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (actSortsOf Wd.D (act Wd.D M)) vs) : Prop :=
  ¬ (Wd.D.soft.outranking = .holistic ∧ higher Wd.D M N = true ∧ EligibleD Wd.D S (tupleVal vs) N ∧
        OutweighsD Wd.D S (tupleVal vs) (act Wd.D M) (rk N) (rk M))

def strictFlag (D : SoftDoc) : SoftDoc :=
  { D with soft := { D.soft with outranking := .strict, outrankingDecider := none } }

/-- Where every comparable colliding pair is strict, the document decides as the same document under the strict
    flag, on every structure satisfying `Str_T`, at tuples typed for the act. Fixtures W-β1 (both directions), W-β2
    (the hypothesis is needed). -/
def all_always_is_strict (Wd : WeighDoc) (h : WellFormedWeigh Wd = true)
    (hall : ∀ M N, (M, N) ∈ collidingPairs Wd.D → Comparable Wd.D M N = true →
      strictPair Wd (rk M) (rk N) = true ∨ strictPair Wd (rk N) (rk M) = true)
    (S : VE.Structure.{u}) (hS : Sat S (strengthPremises Wd)) (p : String) (sign : Bool)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (actSortsOf Wd.D (actKey Wd.D p)) vs) : Prop :=
  DecidesSoftD Wd.D S (tupleVal vs) p sign ↔ DecidesSoftD (strictFlag Wd.D) S (tupleVal vs) p sign


/-- The implication check is sound. -/
def propImplies_sound (a b : VE.Formula) (hp : propImplies a b = true) (S : VE.Structure.{u})
    (ρ : VE.Valuation S) (ha : a.denote S ρ) : Prop :=
  b.denote S ρ

/-- E3 and E6: outside a necessary condition its decision is false. Fixtures W-δ, W-ζ2, W-μ. -/
def condition_necessary (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (weighPremises Wd)) (c : CondDecl) (hc : c ∈ Wd.W.conditions)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (targetSorts Wd c.target) vs) : Prop :=
  c.kind = .necessary → ¬ c.condition.denote S (tupleVal vs) → ¬ (targetF Wd c.target).denote S (tupleVal vs)

/-- E4: inside a sufficient condition its decision is true. Fixtures W-ε, θ11. -/
def condition_sufficient (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (weighPremises Wd)) (c : CondDecl) (hc : c ∈ Wd.W.conditions)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (targetSorts Wd c.target) vs) : Prop :=
  c.kind = .sufficient → c.condition.denote S (tupleVal vs) → (targetF Wd c.target).denote S (tupleVal vs)


/-- A delegated switch works only where its grant holds. Fixture W-ζ. -/
def grant_needed (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (weighPremises Wd)) (g : GrantDecl) (hg : g ∈ Wd.W.grants)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (ruleSorts Wd g.rule) vs)
    (hng : ¬ (atom g.predicate (ruleSorts Wd g.rule)).denote S (tupleVal vs)) : Prop :=
  ¬ (targetF Wd (.off g.rule g.party)).denote S (tupleVal vs)

/-- :138 ("operators cannot grant users more than operator-level trust"): a switch carries every necessary
    condition and every grant of each party it is granted through (`ρ`: the grantor, its grantor, …).
    Fixtures W-ζ2, W-ζ3. -/
def grant_within_grantor (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (S : VE.Structure.{u})
    (hS : Sat S (weighPremises Wd)) (n π ρ : String) (hr : grantReach Wd n π ρ = true)
    (vs : List S.Carrier) (typed : VE.TupleTyped S (ruleSorts Wd n) vs)
    (hoff : (targetF Wd (.off n π)).denote S (tupleVal vs)) : Prop :=
  (∀ c ∈ Wd.W.conditions, c.target = .off n ρ → c.condition.denote S (tupleVal vs)) ∧
    (∀ g ∈ Wd.W.grants, g.rule = n → g.party = ρ →
      (atom g.predicate (ruleSorts Wd n)).denote S (tupleVal vs))

/-- No party is granted a switch its grantor lacks. -/
def delegation_bounded (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (g : GrantDecl)
    (hg : g ∈ Wd.W.grants) : Prop :=
  ∃ N ∈ Wd.D.T.nodes, N.name = g.rule ∧ g.party ∈ N.alterable ∧ g.grantor ∈ N.alterable ∧
      (g.predicate, g.grantor) ∈ Wd.D.soft.instructionOf


/-- Weighing's typing obligation to PK-1 (provider obligation 2): closed base formulas of the filled environment. -/
def weighPremises_wellFormed (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (unspec : List String)
    (hw : VE.NormDefaults.WellFormedU ⟨soften Wd.D, unspec⟩ = true) : Prop :=
  ∀ a ∈ weighPremises Wd, a.WellFormed (envAt (VE.NormDefaults.fill ⟨soften Wd.D, unspec⟩) 0) []

/-- The fragment (soft's gate, plan D6): every premise survives sort-respecting substructures. -/
def weighPremises_substructure (Wd : WeighDoc) (h : WellFormedWeigh Wd = true)
    (B₀ B : VE.Structure.{u}) (hsub : BaseSubstructure Wd.D B₀ B) (hs : Sat B (weighPremises Wd)) : Prop :=
  Sat B₀ (weighPremises Wd)

/-- `B'` agrees with `B` on every predicate that is not a decision of `E′`. -/
def SameBase (Wd : WeighDoc) (B B' : VE.Structure.{u}) : Prop :=
  ∃ R : String → List B.Carrier → Prop, B' = { B with relation := R } ∧
    ∀ p vs, p ∉ decisionNames Wd.D → (R p vs ↔ B.relation p vs)

/-- The narrow base-freedom of synthesis edit 1: `Weigh_T` alone never constrains the base. It says nothing about
    `Weigh_T` together with soft's coherence (W-κ). -/
def weigh_alone_base_free (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (B : VE.Structure.{u}) : Prop :=
  ∃ B' : VE.Structure.{u}, SameBase Wd B B' ∧ Sat B' (weighPremises Wd)

/-- The witness: each `outweighs` atom is the disjunction of its sufficient conditions, each switch is off,
    every other relation is `B`'s. -/
def freeWitness (Wd : WeighDoc) (B : VE.Structure.{u}) : String → List B.Carrier → Prop := fun p vs =>
  match (outweighsTriples Wd.D).find? (fun t => outweighsName t.1 t.2.1 t.2.2 == p) with
  | some (a, L, H) => ∃ c ∈ Wd.W.conditions, c.target = .outweighs a L H ∧ c.kind = .sufficient ∧
      c.condition.denote B (tupleVal vs)
  | none => if ((offDecisions Wd.D).map (·.1)).contains p then False else B.relation p vs

def wellFormedWeigh_empty (D : SoftDoc) (sm : VE.Acts.SplitMap) : Prop :=
  WellFormedWeigh ⟨D, WeighEnv.empty, sm⟩ = WellFormedSoft D


end Theorems5

section Theorems6
open VE.NormDefaults



/-- Certified entailment on a weighing document: RD-9's `acceptanceX` at PK-1's assembled X, whose members are
    weighing premises or typed by their own provider (`assemble_wellFormed`). -/
def weigh_acceptance (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (unspec : List String)
    (hw : WellFormedU ⟨soften Wd.D, unspec⟩ = true) (X : List VE.Formula)
    (hX : ∀ a ∈ X, a ∈ weighPremises Wd ∨ a.WellFormed (envAt (fill ⟨soften Wd.D, unspec⟩) 0) [])
    (Γ : List VE.Formula) (φ : VE.Formula) (cert : VE.Tableau.Certificate)
    (hv : VE.Tableau.checkCertificate (envAt (fill ⟨soften Wd.D, unspec⟩) (size (fill ⟨soften Wd.D, unspec⟩)))
      (Wire.premisesX ⟨soften Wd.D, unspec⟩ X Γ) φ cert = true) : Prop :=
  EntailsX.{u} ⟨soften Wd.D, unspec⟩ X Γ φ

/-- Conflict-freedom on a weighing document: RD-9's `conflictFreeCheckX_sound` at PK-1's X. -/
def weigh_conflict_free (Wd : WeighDoc) (h : WellFormedWeigh Wd = true) (unspec : List String)
    (hw : WellFormedU ⟨soften Wd.D, unspec⟩ = true) (X : List VE.Formula)
    (hX : ∀ a ∈ X, a ∈ weighPremises Wd ∨ a.WellFormed (envAt (fill ⟨soften Wd.D, unspec⟩) 0) [])
    (certs : List (Option VE.Tableau.Certificate))
    (hc : Wire.conflictFreeCheckX ⟨soften Wd.D, unspec⟩ X certs = true) : Prop :=
  Wire.ConflictFreeX.{u} ⟨soften Wd.D, unspec⟩ X

namespace Wire

/-- The strip keeps every other vocabulary entry. -/
def stripWeighing_other (environment : Json) (k : String) (hk : k ≠ "weighing") : Prop :=
  ((stripWeighing environment).getObjValD "vocabulary").getObjValD k =
      (environment.getObjValD "vocabulary").getObjValD k
def stripWeighing_profiles (environment : Json) : Prop :=
  VE.NormDefaults.Wire.profilesOf (stripWeighing environment) =
      (VE.NormDefaults.Wire.profilesOf environment).filter (· != "weighing@0")

/-- The strip is idempotent; `runWeigh_delegates` needs it because the decoder strips the stripped case again. -/
def stripCase_idem (j : Json) : Prop :=
  stripCase (stripCase j) = stripCase j

/-- Debate E4 as restated by synthesis edit 3 and the statement review: a case that passes the original envelope
    and profile validation (`hg`, run before stripping) and has no `weighing` block decodes to the document of its
    stripped case. `core` is everything a layered kind reads except `envId` and `docHash`, so every layered kind but
    the `defaults-*` kinds (diagnostic 1, until DF-6) answers as on the stripped case except for those two fields and
    admission's `report_id`; certificates are bound to the full source and
    compared through packages rebound to it (W-η). -/
def runWeigh_delegates (j : Json) (hg : weighGate (j.getObjValD "environment") = .ok ())
    (hb : blockOf (j.getObjValD "environment") = none) : Prop :=
  (VE.NormDefaults.Wire.decodeLayered j).map LayeredU.core =
      (VE.NormDefaults.Wire.decodeLayered (stripCase j)).map LayeredU.core

/-- Identity: a decoded weighing document is bound to the full environment, block included. -/
def weigh_identity (j : Json) (L : VE.NormDefaults.Wire.LayeredU)
    (hL : VE.NormDefaults.Wire.decodeLayered j = .ok L) : Prop :=
  ∃ c, VE.NormDefaults.Wire.canonicalEnvironmentJsonU (j.getObjValD "environment") = .ok c ∧
      VE.Route.Wire.environmentId (VE.NormDefaults.Wire.profilesOf (j.getObjValD "environment")) c = .ok L.envId ∧
      ((c.getObjValD "vocabulary").getObjVal? "weighing").toOption = blockOf (j.getObjValD "environment")
end Wire


end Theorems6

end VE.Weighing


/-! ## Section 7's fixtures, recomputed on `main`

Each check is `#eval chk "<row>" actual expected`: a difference is a Lean error that prints the actual value, so a clean
run means every value below is the spec's. Documents are wire JSON decoded by `decodeSoftSource`; premises come from
section 1's definitions; outcomes are `outcomeBase (soften D)` evaluated with `Formula.eval` (`eval_iff_denote`). -/
namespace VE.Weighing.Fix
open Lean VE.Norms VE.SoftNorms VE.Weighing
open VE.Defaults.Fixtures (regJ baseJ ruleJ un)

abbrev Ent := String
abbrev GAtom := String × List Ent

def chk {α : Type} [BEq α] [Repr α] (name : String) (actual expected : α) : IO Unit :=
  unless actual == expected do
    throw (IO.userError s!"DIFF {name}: actual {repr actual}")

/-- Compare two answer sets, each answer a set of true atoms with its outcome. -/
def norm (xs : List (List String × Bool)) : List (List String × Bool) :=
  VE.SoftNorms.dedup ((xs.map (fun (t, b) => (VE.Route.sortStrings t, b))).map (fun (t, b) => (t, b))) |>.toArray
    |>.qsort (fun x y => toString (repr x) < toString (repr y)) |>.toList

def xReq : String := VE.Defaults.Fixtures.xReq "deny"
def xPerm : String := VE.Defaults.Fixtures.xPerm
def attrJ (p owner : String) (args : String := "[\"assistant\"]") : String :=
  "\"" ++ p ++ "\":{\"arguments\":" ++ args ++ ",\"description\":\"" ++ p ++ "\",\"instruction_of\":\"" ++ owner ++ "\"}"

def softProfiles : List String := ["norms@0", "relational-fol@0", "soft-norms@0"]
def envOf (preds : List String) (soft : String) (profiles : List String := softProfiles) : Json :=
  (Json.parse ("{\"language\":\"ve.core@0.2\",\"profiles\":" ++ (toJson profiles).compress ++
    ",\"spec_revision\":\"ve-v0.2-expand2-2026-09-25\",\"vocabulary\":{\"sorts\":{" ++
    "\"assistant\":{\"description\":\"assistant\"},\"user\":{\"description\":\"user\"}},\"predicates\":{" ++
    ",".intercalate preds ++ "},\"constants\":{},\"soft\":" ++ soft ++ "}}")).toOption.get!

def quoteL (xs : List String) : String := (toJson xs).compress
def softJ (ranks : List String) (edges : List (String × String)) (holistic : Bool) (parties : List String := []) : String :=
  "{\"parties\":" ++ quoteL parties ++ ",\"ranks\":" ++ quoteL ranks ++ ",\"outranks\":" ++
    (toJson (edges.map (fun e => [e.1, e.2]))).compress ++ ",\"outranking\":" ++
    (if holistic then "{\"mode\":\"holistic\",\"decided_by\":\"assistant\"}" else "{\"mode\":\"strict\"}") ++ "}"

def dfltR (name pred : String) (sign : Bool) (rank : Option String := none) (alterable : List String := [])
    (necessary : List String := []) : String :=
  ruleJ name pred sign (",\"mode\":\"default\",\"exception\":{\"decided_by\":\"assistant\",\"sufficient\":[],\"necessary\":" ++
    "[" ++ ",".intercalate necessary ++ "],\"factors\":[]}" ++
    (match rank with | some r => ",\"rank\":\"" ++ r ++ "\"" | none => "") ++
    (if alterable.isEmpty then "" else ",\"alterable\":" ++ quoteL alterable))
def strictR (name pred : String) (sign : Bool) (alterable : List String) (rank : Option String := none) : String :=
  ruleJ name pred sign (",\"mode\":\"strict\",\"alterable\":" ++ quoteL alterable ++
    (match rank with | some r => ",\"rank\":\"" ++ r ++ "\"" | none => ""))

def decode (env : Json) (rules : List String) : Except String SoftDoc :=
  (VE.SoftNorms.Wire.decodeSoftSource env (Json.parse ("[" ++ ",".intercalate rules ++ "]")).toOption.get!).map (·.D)

instance : Inhabited SoftDoc :=
  ⟨⟨⟨[], fun _ => none, fun _ => none⟩, [], ⟨[], [], [], [], .strict, none, none, [], []⟩, ⟨[], [], []⟩⟩⟩
instance : Inhabited SoftNode :=
  ⟨{ name := "", pred := "", sign := true, guard := .top, carveOuts := [], over := [], mode := .strict, rank := none,
     alterable := [], exception := none, hard := false }⟩
def must (e : Except String SoftDoc) : SoftDoc := match e with
  | .ok D => D
  | .error m => panic! m

def W (always : List (String × String) := []) (conditions : List CondDecl := []) (grants : List GrantDecl := [])
    (factors : List FactorDecl := []) : WeighEnv := ⟨always, conditions, factors, grants⟩
def wd (D : SoftDoc) (w : WeighEnv := W) (sm : VE.Acts.SplitMap := ⟨[], []⟩) : WeighDoc := ⟨D, w, sm⟩

def verdict (Wd : WeighDoc) : String := match checkWeigh Wd with
  | .ok () => "accepted"
  | .error e => e

/-! ### Situations and assignments -/

def doms1 : String → List Ent := fun s =>
  if s == "assistant" then ["a"] else if s == "user" then ["u"] else []
def modelOf (doms : String → List Ent) (facts : List GAtom) : VE.FiniteModel Ent :=
  ⟨doms, fun _ => none, fun p => (facts.filter (·.1 == p)).map (·.2)⟩

def atomsAt (D : SoftDoc) (doms : String → List Ent) : List GAtom := decisionAtoms D (modelOf doms [])

/-- The admissible assignments: every subset of the decision atoms the record does not fix, kept when `ps` hold. -/
def assignments (D : SoftDoc) (doms : String → List Ent) (fixed : List (GAtom × Bool)) : List (List GAtom) :=
  let free := (atomsAt D doms).filter (fun a => !fixed.any (·.1 == a))
  (subsetsOf free).map (fun t => (fixed.filter (·.2)).map (·.1) ++ t)

def holdsAll (ps : List VE.Formula) (M : VE.FiniteModel Ent) : Bool := ps.all (fun φ => φ.eval M [])
def softX (D : SoftDoc) : List (String × VE.Formula) := VE.SoftNorms.Wire.softLabelled D
def admX (Wd : WeighDoc) : List VE.Formula := (softX Wd.D ++ weighLabelled Wd).map (·.2)

def outcome (D : SoftDoc) (M : VE.FiniteModel Ent) (r : String) (vs : List Ent) : Bool :=
  (outcomeBase (soften D) r).eval M (tupleVal vs)

/-- The answers of 7.2's tables: true decision atoms (names), and the outcome of `r` at `vs`. -/
def answers (Wd : WeighDoc) (doms : String → List Ent) (base : List GAtom) (fixed : List (GAtom × Bool))
    (r : String := "x_required") (vs : List Ent := ["a"]) : List (List String × Bool) :=
  norm (((assignments Wd.D doms fixed).filter (fun t => holdsAll (admX Wd) (modelOf doms (base ++ t)))).map
    (fun t => (t.map (·.1), outcome Wd.D (modelOf doms (base ++ t)) r vs)))

def ex (n : String) : String := "soft__excepted__" ++ n
def ow (L H : String) (a : String := "x_permitted") : String := outweighsName a L H
def sw (n π : String) : String := "soft__off__" ++ n ++ "__" ++ π
def at1 (p : String) : GAtom := (p, ["a"])
def noExc (D : SoftDoc) : List (GAtom × Bool) :=
  (D.T.nodes.filter (·.mode == .default)).map (fun N => (at1 (exceptedName N), false))
def nodeOf (D : SoftDoc) (n : String) : SoftNode := match nodeNamed D n with
  | some N => N
  | none => panic! n

def U (a : String) : VE.Formula := .unary a (.var 0)
def urgent := U "urgent"
def serious := U "serious"
def emergency := U "emergency"
def tOut (L H : String) (a : String := "x_permitted") : Target := .outweighs a L H

/-! ### Documents -/

def predsA : List String := [xReq, xPerm, baseJ "urgent", baseJ "serious", baseJ "emergency"]
def alphaOf (ranks : List String) (edges : List (String × String)) (hi lo : String) (holistic := true)
    (preds := predsA) : Except String SoftDoc :=
  decode (envOf preds (softJ ranks edges holistic))
    [dfltR "h" "x_required" true (some hi), dfltR "l" "x_permitted" false (some lo)]
def α : SoftDoc := must (alphaOf ["a", "b"] [("a", "b")] "a" "b")
def αs : SoftDoc := must (alphaOf ["a", "b"] [("a", "b")] "a" "b" false)
def ranks4 : List String := ["e", "g", "h", "s"]
def edges4 : List (String × String) := [("s", "e"), ("e", "g"), ("g", "h")]
def betaOf (hi lo : String) : SoftDoc := must (decode (envOf predsA (softJ ranks4 edges4 true))
  [dfltR "ra" "x_required" true (some hi), dfltR "rb" "x_permitted" false (some lo)])
def β1 := betaOf "s" "h"
def β2 := betaOf "e" "h"
def γd : SoftDoc := must (alphaOf ["e", "s"] [("s", "e")] "s" "e" false)

/-! ### W-α, W-α′ -/

#eval chk "α soft decode" (α.soft.outranking == .holistic && (decisionNames α).length == 3) true
def wα := wd α (W [("a", "b")])
#eval chk "α Str_T" (strengthEntries wα).length 1
#eval chk "α label" ((strengthEntries wα).map (·.1)) ["weigh:strength:a:b:x_permitted"]
#eval chk "α premise" ((strengthEntries wα).map (fun e => (VE.Route.Wire.encodeFormula e.2.1).compress))
  ["[\"forall\",\"assistant\",[\"not\",[\"unary\",\"soft__outweighs__b__a__x_permitted\",[\"var\",0]]]]"]
#eval chk "α origin" ((strengthEntries wα).map (fun e => ".".intercalate e.2.2)) ["environment.vocabulary.weighing.always.0"]
#eval chk "α accepted" (verdict wα) "accepted"
#eval chk "α no exception" (answers wα doms1 [] (noExc α)) [([], true)]
#eval chk "α h excepted" (answers wα doms1 [] [(at1 (ex "h"), true), (at1 (ex "l"), false)]) [([ex "h"], false)]
#eval chk "α without block" (answers (wd α) doms1 [] (noExc α)) (norm [([ow "b" "a"], false), ([], true)])
#eval chk "α atom true refused"
  (((weighLabelled wα).filter (fun e => !e.2.eval (modelOf doms1 [at1 (ow "b" "a")]) [])).map (·.1))
  ["weigh:strength:a:b:x_permitted"]

/-- `always_dominates`'s and `always_no_override`'s bodies at `a`, read through `eff_denote`, `domWith_denote`. -/
def dominates (D : SoftDoc) (M : VE.FiniteModel Ent) (Mn Nn : SoftNode) : Bool :=
  !(effF D (rankFuel D) Mn).eval M ["a"] || (dominatedF D (rankFuel D) Nn).eval M ["a"]
def overrideDisjunct (D : SoftDoc) (M : VE.FiniteModel Ent) (Mn Nn : SoftNode) : Bool :=
  decide (D.soft.outranking = .holistic) && higher D Mn Nn && (eligibleF D Nn).eval M ["a"] &&
    (outweighsF D (act D Mn) (rk Nn) (rk Mn)).eval M ["a"]
def satStr (Wd : WeighDoc) (t : List GAtom) : Bool := holdsAll (strengthPremises Wd) (modelOf doms1 t)
def bothHold (Wd : WeighDoc) (m n : String) : Nat × Bool :=
  let ts := (assignments Wd.D doms1 []).filter (satStr Wd)
  let Mn := nodeOf Wd.D m; let Nn := nodeOf Wd.D n
  (ts.length, ts.all fun t => dominates Wd.D (modelOf doms1 t) Mn Nn && !overrideDisjunct Wd.D (modelOf doms1 t) Mn Nn)
#eval chk "α theorems on 4" (bothHold wα "h" "l") (4, true)
def names (t : List GAtom) : List String := VE.Route.sortStrings (t.map (·.1))
def wBlank := assignments α doms1 []
#eval chk "α counterexample, override"
  (norm ((wBlank.filter fun t => overrideDisjunct α (modelOf doms1 t) (nodeOf α "h") (nodeOf α "l")).map (fun t => (names t, true))))
  (norm [([ex "h", ow "b" "a"], true), ([ow "b" "a"], true)])
#eval chk "α counterexample, dominates"
  (norm ((wBlank.filter fun t => !dominates α (modelOf doms1 t) (nodeOf α "h") (nodeOf α "l")).map (fun t => (names t, true))))
  (norm [([ex "l", ow "b" "a"], true)])

def wαs := wd αs (W [("a", "b")])
#eval chk "α′ warning" (weighWarnings wαs) ["StrengthInert: a, b"]
#eval chk "α′ Str_T" (strengthPremises wαs).length 0
#eval chk "α′ decisions" (decisionNames αs) [ex "h", ex "l"]
#eval chk "α′ accepted" (verdict wαs) "accepted"
#eval chk "α′ raw atom true"
  ((outweighsF αs "x_permitted" "b" "a").eval (modelOf doms1 [at1 (ow "b" "a")]) ["a"]) true
#eval chk "α′ theorem on 4" (((assignments αs doms1 []).all fun t =>
  !overrideDisjunct αs (modelOf doms1 (at1 (ow "b" "a") :: t)) (nodeOf αs "h") (nodeOf αs "l")), (assignments αs doms1 []).length) (true, 4)

/-! ### W-β -/

def wβ (always : List (String × String)) (D := β1) := wd D (W always)
def allPairs : List (String × String) := ranks4.flatMap fun a => ranks4.map (a, ·)
def strictOf (w : WeighDoc) : List (String × String) := allPairs.filter (fun p => strictPair w p.1 p.2)
def setEq (a b : List (String × String)) : Bool := a.all b.contains && b.all a.contains && a.length == b.length
def wb := wβ [("s", "e")]
#eval chk "β strict" (setEq (strictOf wb) [("s", "e"), ("s", "g"), ("s", "h")]) true
def brute (w : WeighDoc) (H L : String) : Bool :=
  (chainsFrom w.D.soft.outranks L w.D.soft.ranks.length H).any (fun c => (chainEdges c).any w.W.always.contains)
#eval chk "β brute 16" (allPairs.all fun p => strictPair wb p.1 p.2 == brute wb p.1 p.2) true
#eval chk "β witness" (strictWitness wb "s" "h", strictWitness wb "s" "g", strictWitness wb "s" "e",
  strictWitness wb "e" "h", strictWitness wb "g" "h", strictWitness wb "h" "s")
  (some ["s", "e", "g", "h"], some ["s", "e", "g"], some ["s", "e"], none, none, none)
#eval chk "β e,g" (setEq (strictOf (wβ [("e", "g")])) [("s", "g"), ("s", "h"), ("e", "g"), ("e", "h")]) true
#eval chk "β g,h" (setEq (strictOf (wβ [("g", "h")])) [("s", "h"), ("e", "h"), ("g", "h")]) true
#eval chk "β g,h witness" (strictWitness (wβ [("g", "h")]) "s" "h") (some ["s", "e", "g", "h"])
def triples := ranks4.flatMap fun a => ranks4.flatMap fun b => ranks4.map (a, b, ·)
#eval chk "β down/up 64" (triples.length, ([("s", "e"), ("e", "g"), ("g", "h")] : List (String × String)).all fun e =>
  let w := wβ [e]
  triples.all fun (H, M, L) =>
    (!strictPair w H M || !outranksPlus w.D.soft M L || strictPair w H L) &&
    (!outranksPlus w.D.soft H M || !strictPair w M L || strictPair w H L)) (64, true)
#eval chk "β1 triple, Str_T" ((outweighsTriples β1), (weighLabelled wb).map (·.1))
  ([("x_permitted", "h", "s")], ["weigh:strength:s:h:x_permitted"])
#eval chk "β1 outcomes" (((answers wb doms1 [] (noExc β1)).map (·.2))) [true]
def wb2 := wd β2 (W [("s", "e")])
#eval chk "β2 triple, Str_T" (outweighsTriples β2, (strengthPremises wb2).length) ([("x_permitted", "h", "e")], 0)
#eval chk "β2 outcomes" (VE.Route.sortStrings ((answers wb2 doms1 [] (noExc β2)).map (fun x => toString x.2))) ["false", "true"]
#eval chk "strength_iff β1" ((strengthPremises wb).contains (bindAll (actSortsOf β1 "x_permitted")
  (.not (outweighsF β1 "x_permitted" "h" "s")))) true
#eval chk "β1 theorems on 4" (bothHold wb "ra" "rb") (4, true)
def decidesAt (D : SoftDoc) (M : VE.FiniteModel Ent) (p : String) (sign : Bool) : Bool :=
  (subst (soften D).T (size (soften D)) (defaultDecidesF D p sign)).eval M ["a"]
/-- (holistic, strict flag) for "decides yes" and "decides no". -/
def bothDocs (D : SoftDoc) (t : List GAtom) : (Bool × Bool) × (Bool × Bool) :=
  let M := modelOf doms1 t
  ((decidesAt D M "x_required" true, decidesAt (strictFlag D) M "x_required" true),
   (decidesAt D M "x_permitted" false, decidesAt (strictFlag D) M "x_permitted" false))
#eval chk "all_always {ra,rb}" (bothDocs β1 [at1 (ex "ra"), at1 (ex "rb")]) ((false, false), (false, false))
#eval chk "all_always {ra}" (bothDocs β1 [at1 (ex "ra")]) ((false, false), (true, true))
#eval chk "all_always {rb}" (bothDocs β1 [at1 (ex "rb")]) ((true, true), (false, false))
#eval chk "all_always {}" (bothDocs β1 []) ((true, true), (false, false))
#eval chk "β2 hypothesis" (bothDocs β2 [at1 (ow "h" "e")]) ((false, true), (true, false))

/-! ### W-γ, W-δ, W-ε, θ11 -/

def wγ := wd γd (W [("s", "e")])
#eval chk "γ" (verdict wγ, weighWarnings wγ, (strengthPremises wγ).length, outweighsTriples γd)
  ("accepted", ["StrengthInert: s, e"], 0, [])
def cond (t : Target) (k : CondKind) (φ : VE.Formula) : CondDecl := ⟨t, k, φ⟩
def wδ := wd α (W [] [cond (tOut "b" "a") .necessary urgent])
def wε := wd α (W [] [cond (tOut "b" "a") .sufficient urgent])
#eval chk "δ premise" ((weighLabelled wδ).map (fun e => (e.1, (VE.Route.Wire.encodeFormula e.2).compress)))
  [("weigh:condition:0:necessary", "[\"forall\",\"assistant\",[\"implies\",[\"unary\",\"soft__outweighs__b__a__x_permitted\",[\"var\",0]],[\"unary\",\"urgent\",[\"var\",0]]]]")]
#eval chk "δ false" (answers wδ doms1 [] (noExc α)) [([], true)]
#eval chk "δ true" (answers wδ doms1 [at1 "urgent"] (noExc α)) (norm [([ow "b" "a"], false), ([], true)])
#eval chk "ε true" (answers wε doms1 [at1 "urgent"] (noExc α)) [([ow "b" "a"], false)]
#eval chk "ε false" (answers wε doms1 [] (noExc α)) (norm [([ow "b" "a"], false), ([], true)])
def bases : List (List GAtom) := subsetsOf [at1 "urgent", at1 "serious", at1 "emergency"]
def allModels (D : SoftDoc) (doms := doms1) (bs := bases) : List (VE.FiniteModel Ent) :=
  bs.flatMap fun b => (assignments D doms []).map fun t => modelOf doms (b ++ t)
def condNec (w : WeighDoc) (doms := doms1) (bs := bases) (vs : List Ent := ["a"]) : Bool :=
  (allModels w.D doms bs).all fun M => !holdsAll (weighPremises w) M ||
    w.W.conditions.all fun c => c.kind == .sufficient || c.condition.eval M (tupleVal vs) || !(targetF w c.target).eval M (tupleVal vs)
def condSuf (w : WeighDoc) : Bool :=
  (allModels w.D).all fun M => !holdsAll (weighPremises w) M ||
    w.W.conditions.all fun c => c.kind == .necessary || !c.condition.eval M ["a"] || (targetF w c.target).eval M ["a"]
def θ11 := wd α (W [] [cond (tOut "b" "a") .sufficient (.and urgent serious), cond (tOut "b" "a") .necessary urgent])
#eval chk "δ condition_necessary" (condNec wδ) true
#eval chk "ε condition_sufficient" (condSuf wε) true
#eval chk "θ11 condition_sufficient" (condSuf θ11) true
#eval chk "factors_inert" (weighPremises (wd α (W [] [cond (tOut "b" "a") .necessary urgent] []
  [⟨tOut "b" "a", ["how much the user would lose", "how severe the ethical cost is"]⟩])) == weighPremises wδ,
  weighPremises wδ == weighPremises wε) (true, false)
#eval chk "θ11" (verdict θ11, answers θ11 doms1 [] (noExc α), answers θ11 doms1 [at1 "urgent"] (noExc α),
    answers θ11 doms1 [at1 "urgent", at1 "serious"] (noExc α))
  ("accepted", [([], true)], norm [([ow "b" "a"], false), ([], true)], [([ow "b" "a"], false)])

/-! ### W-ζ and its grants -/

def predsZ : List String := [xReq, xPerm, baseJ "emergency", attrJ "operator_allows" "operator",
  attrJ "user_allows" "user", attrJ "developer_allows" "developer",
  attrJ "operator_allows_for" "operator" "[\"assistant\",\"user\"]"]
def zOf (alterable : List String) (parties : List String := ["developer", "operator", "user"]) (preds := predsZ) : SoftDoc :=
  must (decode (envOf preds (softJ [] [] false parties)) [strictR "n" "x_required" true alterable])
def ζd := zOf ["operator", "user"]
def gr (party grantor p : String) (n : String := "n") : GrantDecl := ⟨n, party, grantor, p⟩
def wζ := wd ζd (W [] [] [gr "user" "operator" "operator_allows"])
#eval chk "ζ premise" ((weighEntries wζ).map (fun e => (e.1, (VE.Route.Wire.encodeFormula e.2.1).compress, ".".intercalate e.2.2)))
  [("weigh:grant:n:user", "[\"forall\",\"assistant\",[\"implies\",[\"unary\",\"soft__off__n__user\",[\"var\",0]],[\"unary\",\"operator_allows\",[\"var\",0]]]]",
    "environment.vocabulary.weighing.grants.0")]
def opOff : List (GAtom × Bool) := [(at1 (sw "n" "operator"), false)]
#eval chk "ζ off, not allowed" (answers wζ doms1 [] opOff) [([], true)]
#eval chk "ζ off, allowed" (answers wζ doms1 [at1 "operator_allows"] opOff) (norm [([sw "n" "user"], false), ([], true)])
#eval chk "ζ no record" (answers wζ doms1 [] []) (norm [([sw "n" "operator"], false), ([], true)])
#eval chk "ζ alterable user" (verdict (wd (zOf ["user"]) wζ.W)) "DelegationExceedsGrantor: rule n, user, operator"
#eval chk "ζ instruction_of user" (verdict (wd (zOf ["operator", "user"] (preds := [xReq, xPerm,
  attrJ "operator_allows" "user"])) wζ.W)) "GrantNotAttributed: operator_allows, operator"
#eval chk "ζ twice" (verdict (wd ζd (W [] [] [gr "user" "operator" "operator_allows", gr "user" "operator" "operator_allows"])))
  "DuplicateDeclaration: grant n, user"
#eval chk "ζ nobody" (verdict (wd ζd (W [] [] [gr "nobody" "operator" "operator_allows"]))) "NoSuchDecision: off rule n, nobody"
#eval chk "ζ emergency" (verdict (wd ζd (W [] [] [gr "user" "operator" "emergency"]))) "GrantNotAttributed: emergency, operator"
#eval chk "ζ binary predicate" (verdict (wd ζd (W [] [] [gr "user" "operator" "operator_allows_for"])))
  "InvalidInput: grant predicate operator_allows_for does not take the arguments of rule n"
#eval chk "cycle self" (verdict (wd ζd (W [] [] [gr "user" "user" "user_allows"]))) "DelegationCycle: rule n, user"
#eval chk "cycle two" (verdict (wd ζd (W [] [] [gr "user" "operator" "operator_allows", gr "operator" "user" "user_allows"])))
  "DelegationCycle: rule n, user"
def ζ3d := zOf ["developer", "operator", "user"]
def wζ3 := wd ζ3d (W [] [] [gr "user" "operator" "operator_allows", gr "operator" "developer" "developer_allows"])
#eval chk "ζ3 accepted" (verdict wζ3) "accepted"
#eval chk "ζ3 through" (grantedThrough wζ3 "n" "user") ["developer", "operator"]
#eval chk "ζ3 labels" ((weighEntries wζ3).map (fun e => (e.1, ".".intercalate (e.2.2.drop 3))))
  [("weigh:grant:n:user", "grants.0"), ("weigh:grant:n:user:grant:operator", "grants.1"), ("weigh:grant:n:operator", "grants.1")]
def wζ2 := wd ζd (W [] [cond (.off "n" "operator") .necessary emergency] [gr "user" "operator" "operator_allows"])
#eval chk "ζ2 labels" ((weighEntries wζ2).map (fun e => (e.1, ".".intercalate (e.2.2.drop 3))))
  [("weigh:condition:0:necessary", "conditions.0"), ("weigh:grant:n:user", "grants.0"),
   ("weigh:grant:n:user:condition:0", "conditions.0")]
#eval chk "ζ2 allows only" (answers wζ2 doms1 [at1 "operator_allows"] opOff) [([], true)]
#eval chk "ζ2 both" (answers wζ2 doms1 [at1 "operator_allows", at1 "emergency"] opOff) (norm [([sw "n" "user"], false), ([], true)])
def ζ3off : List (GAtom × Bool) := [(at1 (sw "n" "operator"), false), (at1 (sw "n" "developer"), false)]
#eval chk "ζ3 operator only" (answers wζ3 doms1 [at1 "operator_allows"] ζ3off) [([], true)]
#eval chk "ζ3 both" (answers wζ3 doms1 [at1 "operator_allows", at1 "developer_allows"] ζ3off) (norm [([sw "n" "user"], false), ([], true)])
def basesZ : List (List GAtom) := subsetsOf [at1 "operator_allows", at1 "developer_allows", at1 "emergency"]
def inv (w : WeighDoc) (ante : VE.Formula) (cons : VE.Formula) : Bool :=
  (allModels w.D doms1 basesZ).all fun M => !holdsAll (weighPremises w) M || !ante.eval M ["a"] || cons.eval M ["a"]
def offU : VE.Formula := .unary (sw "n" "user") (.var 0)
#eval chk "grant_needed ζ" (inv wζ offU (U "operator_allows")) true
#eval chk "grant_within ζ2" (inv wζ2 offU emergency) true
#eval chk "grant_within ζ3" (inv wζ3 offU (U "developer_allows")) true
#eval chk "control ζ" (inv wζ offU emergency) false

/-! ### W-η: the empty block; the gate -/

def wWithDup (D : SoftDoc) : SoftDoc := { D with T := { D.T with nodes := D.T.nodes ++ D.T.nodes } }
def κd : SoftDoc := must (decode (envOf predsA (softJ [] [] false ["operator", "user"]))
  [dfltR "ra" "x_required" true none ["operator"] ["[\"bottom\"]"],
   dfltR "rb" "x_permitted" false none ["user"] ["[\"bottom\"]"]])
def ld : SoftDoc := must (decode (envOf predsA (softJ [] [] false ["user"]))
  [strictR "n-a1" "x_required" true ["user"], strictR "n-a2" "x_required" true ["user"]])
#eval chk "η empties" (([α, β1, β2, γd, ζd, ζ3d, κd, ld] : List SoftDoc).all fun D =>
  (weighPremises (wd D WeighEnv.empty)).isEmpty && WellFormedWeigh (wd D WeighEnv.empty) && WellFormedSoft D) true
#eval chk "η doubled" (WellFormedWeigh (wd (wWithDup α) WeighEnv.empty), WellFormedSoft (wWithDup α)) (false, false)

def tableW : List VE.Compose.ProfileRow := VE.Compose.baseRows ++ [weighingRow] ++ VE.Compose.wrapperRows
def tableL : List VE.Compose.ProfileRow := VE.Compose.baseRows ++ VE.Compose.wrapperRows ++ [weighingRow]
/-- `weighGate` with `weighingRow` in the table (main's `profileTable` does not hold it yet). -/
def gateT (t : List VE.Compose.ProfileRow) (environment : Json) : String :=
  match (do
    let ps ← VE.Route.Gate.profilesOf environment
    discard (VE.Compose.gateOf t ps)
    if !ps.contains "weighing@0" && (Wire.blockOf environment).isSome then
      throw "UnsupportedProfile: the weighing block requires weighing@0" : Except String Unit) with
  | .ok () => "ok"
  | .error e => e
def envP (ps : List String) : Json := Json.mkObj [("profiles", toJson ps)]
def blockE (ps : List String) : Json := Json.mkObj [("profiles", toJson ps),
  ("vocabulary", Json.mkObj [("weighing", Json.mkObj [("always", toJson [["a", "b"]])])])]
def ok4 := ["norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0", "weighing@0"]
def gateCases : List (String × Json × String) := [
  ("missing soft", envP ["norm-defaults@0", "norms@0", "relational-fol@0", "weighing@0"],
    "UnsupportedProfile: weighing@0 requires soft-norms@0"),
  ("missing nd", envP ["norms@0", "relational-fol@0", "soft-norms@0", "weighing@0"],
    "UnsupportedProfile: weighing@0 requires norm-defaults@0"),
  ("j = {}", Json.mkObj [], "UnsupportedProfile: profiles must be a sorted unique array"),
  ("not an object", .str "x", "UnsupportedProfile: profiles must be a sorted unique array"),
  ("profiles a string", Json.mkObj [("profiles", .str "x")], "UnsupportedProfile: profiles must be a sorted unique array"),
  ("twice", envP (ok4 ++ ["weighing@0"]), "UnsupportedProfile: profiles must be sorted and unique"),
  ("unsorted", envP ok4.reverse, "UnsupportedProfile: profiles must be sorted and unique"),
  ("rights", envP ["norm-defaults@0", "norms@0", "relational-fol@0", "rights@0", "soft-norms@0", "weighing@0"],
    "UnsupportedProfile: weighing@0 with rights@0"),
  ("block off", blockE ["norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"],
    "UnsupportedProfile: the weighing block requires weighing@0"),
  ("accepted", envP ok4, "ok")]
#eval do
  for (n, e, x) in gateCases do
    chk s!"gate {n}" (gateT tableW e) x
    chk s!"gate last {n}" (gateT tableL e) x
#eval chk "row slot" (VE.Compose.slotAgrees weighingRow.slot weighingRow.interface) true
#eval chk "strip totals" (gateCases.all fun (_, e, _) =>
  let j := Json.mkObj [("environment", e)]
  Wire.stripCase (Wire.stripCase j) == Wire.stripCase j &&
    Wire.stripCase (Json.mkObj []) == Json.mkObj []) true
#eval chk "strip content" (Wire.stripWeighing (blockE ok4)).compress
  ((Json.mkObj [("profiles", toJson (ok4.filter (· != "weighing@0"))), ("vocabulary", Json.mkObj [])]).compress)

/-! ### W-θ -/

def θ (block : WeighEnv) (D := α) : String := verdict (wd D block)
#eval chk "θ1" (θ (W [("b", "a")])) "StrengthOnUndeclaredEdge: b, a"
#eval chk "θ2" (θ (W [("a", "b"), ("a", "b")])) "DuplicateDeclaration: strength a, b"
#eval chk "θ3" (θ (W [] [cond (tOut "a" "b") .necessary urgent])) "NoSuchDecision: outweighs x_permitted, a, b"
#eval chk "θ4" (θ (W [] [cond (tOut "b" "a") .necessary (U "x_required")])) "InvalidInput: condition 0 mentions x_required"
#eval chk "θ5" (θ (W [] [cond (tOut "b" "a") .necessary (.all "assistant" urgent)])) "InvalidInput: condition 0 is not quantifier-free"
#eval chk "θ6" (θ (W [] [cond (tOut "b" "a") .necessary (.unary "urgent" (.var 1))])) "UnboundVariable: Variable index 1 is outside its scope"
#eval chk "θ7" (θ (W [("a", "b")] [cond (tOut "b" "a") .sufficient urgent])) "ConditionOnStrictPair: outweighs x_permitted, b, a"
#eval chk "θ8" (θ (W [("s", "e")] [cond (tOut "h" "s") .necessary urgent]) β1) "ConditionOnStrictPair: outweighs x_permitted, h, s"
#eval chk "θ9" (θ (W [] [cond (.off "n" "user") .sufficient emergency]) ζd) "InvalidInput: condition 0 on a switch must be necessary"
#eval chk "θ10" (θ (W [] [cond (tOut "b" "a") .sufficient urgent, cond (tOut "b" "a") .necessary (.not urgent)]))
  "ConditionsDisagree: the checker cannot show that condition 0 implies condition 1"
#eval chk "θ12" (θ (W [] [cond (tOut "b" "a") .sufficient urgent, cond (tOut "b" "a") .necessary (.and urgent (.eq (.var 0) (.var 0)))]))
  "ConditionsDisagree: the checker cannot show that condition 0 implies condition 1"
#eval chk "θ13" (θ (W [] [] [] [⟨tOut "b" "a", (List.range 17).map toString⟩])) "InvalidInput: invalid factors 0"
#eval chk "θ14" (θ (W [] [] [] [⟨tOut "a" "b", ["f"]⟩])) "NoSuchDecision: outweighs x_permitted, a, b"
def negs : Nat → VE.Formula
  | 0 => urgent
  | n + 1 => .not (negs n)
#eval chk "θ15" (θ (W [] [cond (tOut "b" "a") .necessary (negs 62)])) "ResourceLimit: generated weighing premise weigh:condition:0:necessary"
#eval chk "θ16" (θ (W [] [cond (tOut "b" "a") .necessary (negs 60)])) "accepted"
#eval chk "θ17" (θ (W [("s", "e")] [cond (tOut "h" "e") .necessary urgent]) β2) "accepted"
#eval chk "θ18" (θ (W [] [cond (tOut "b" "a") .necessary urgent]) αs) "NoSuchDecision: outweighs x_permitted, b, a"
def predsP := [xReq, xPerm] ++ (List.range 13).map (fun i => baseJ s!"p{i}")
def αP : SoftDoc := must (alphaOf ["a", "b"] [("a", "b")] "a" "b" true predsP)
def conj : List VE.Formula → VE.Formula
  | [] => .top
  | [a] => a
  | a :: as => .and a (conj as)
def ps (n : Nat) : VE.Formula := conj ((List.range n).map (fun i => U s!"p{i}"))
#eval chk "θ19" (θ (W [] [cond (tOut "b" "a") .sufficient (ps 12), cond (tOut "b" "a") .necessary (U "p0")]) αP) "accepted"
#eval chk "θ20" (θ (W [] [cond (tOut "b" "a") .sufficient (ps 13), cond (tOut "b" "a") .necessary (U "p0")]) αP) "ResourceLimit: conditions 0, 1"

/-! ### W-θ, bypassed -/

def θ7 := wd α (W [("a", "b")] [cond (tOut "b" "a") .sufficient urgent])
def θ10 := wd α (W [] [cond (tOut "b" "a") .sufficient urgent, cond (tOut "b" "a") .necessary (.not urgent)])
def countW (w : WeighDoc) (b : List GAtom) : Nat :=
  ((assignments w.D doms1 []).filter fun t => holdsAll (weighPremises w) (modelOf doms1 (b ++ t))).length
#eval chk "bypassed θ7" (countW θ7 [at1 "urgent"], countW θ7 []) (0, 4)
#eval chk "bypassed θ10" (countW θ10 [at1 "urgent"], countW θ10 []) (0, 8)
def firstRefuted (ps : List (String × VE.Formula)) (M : VE.FiniteModel Ent) : Option String :=
  (ps.find? fun e => !e.2.eval M []).map (·.1)
def labelsAt (w : WeighDoc) (b : List GAtom) : List (Option String) :=
  (assignments w.D doms1 []).map fun t => firstRefuted (softX w.D ++ weighLabelled w) (modelOf doms1 (b ++ t))
def deduped (l : List (Option String)) : List String := VE.Route.sortStrings (VE.SoftNorms.dedup (l.filterMap id))
#eval chk "bypassed θ7 labels" (deduped (labelsAt θ7 [at1 "urgent"]), (labelsAt θ7 [at1 "urgent"]).all (·.isSome), (labelsAt θ7 [at1 "urgent"]).length)
  (["weigh:condition:0:sufficient", "weigh:strength:a:b:x_permitted"], true, 8)
#eval chk "bypassed θ10 labels" (deduped (labelsAt θ10 [at1 "urgent"]), (labelsAt θ10 [at1 "urgent"]).all (·.isSome))
  (["weigh:condition:0:sufficient", "weigh:condition:1:necessary"], true)

/-! ### W-κ -/

def wκ := wd κd (W [] [cond (.off "ra" "operator") .necessary urgent, cond (.off "rb" "user") .necessary urgent])
#eval chk "κ accepted" (verdict wκ) "accepted"
#eval chk "κ labels" ((softX κd ++ weighLabelled wκ).map (·.1))
  ["soft:exception:ra:necessary:0", "soft:exception:rb:necessary:0", "soft:coherence:ra,rb",
   "weigh:condition:0:necessary", "weigh:condition:1:necessary"]
#eval chk "κ pair" ((collidingPairs κd).length, (collidingPairs κd).all fun p => !Comparable κd p.1 p.2) (1, true)
def countP (ps : List VE.Formula) (b : List GAtom) : Nat :=
  ((assignments κd doms1 []).filter fun t => holdsAll ps (modelOf doms1 (b ++ t))).length
#eval chk "κ counts" (countP (admX wκ) [], countP (admX wκ) [at1 "urgent"],
  countP ((softX κd).map (·.2)) [], countP (weighPremises wκ) [], (assignments κd doms1 []).length) (0, 3, 3, 4, 16)
def κrow (er eb ora orb : Bool) : Option String :=
  let t := ([(er, ex "ra"), (eb, ex "rb"), (ora, sw "ra" "operator"), (orb, sw "rb" "user")].filter (·.1)).map (at1 ·.2)
  firstRefuted (softX κd ++ weighLabelled wκ) (modelOf doms1 t)
def eR := "soft:exception:ra:necessary:0"
def eB := "soft:exception:rb:necessary:0"
#eval chk "κ 16 rows" (([false, true].flatMap fun a => [false, true].flatMap fun b => [false, true].flatMap fun c =>
    [false, true].map fun d => κrow a b c d).filterMap id)
  (["soft:coherence:ra,rb", "weigh:condition:1:necessary", "weigh:condition:0:necessary", "weigh:condition:0:necessary",
    eB, eB, eB, eB, eR, eR, eR, eR, eR, eR, eR, eR])

/-! ### W-λ, W-μ -/

def lmap : VE.Acts.SplitMap := ⟨[], [("n-a1", "n", 1), ("n-a2", "n", 2)]⟩
def lc (r : String) : WeighEnv := W [] [cond (.off r "user") .necessary urgent]
#eval chk "λ source" (verdict (wd ld (lc "n") lmap))
  "InvalidInput: rule n names a predicate that is split into parts; name one of its parts"
#eval chk "λ part" (verdict (wd ld (lc "n-a1") lmap)) "accepted"
#eval chk "λ no map" (verdict (wd ld (lc "n"))) "NoSuchDecision: off rule n, user"
#eval chk "λ act" (verdict (wd α (W [] [cond (tOut "b" "a") .necessary urgent]) ⟨[("x_permitted__1", "x_permitted", 1)], []⟩))
  "InvalidInput: act x_permitted names a predicate that is split into parts; name one of its parts"

def yReq : String := regJ "y_required" "[\"assistant\",\"user\"]" "obligation" "deny" ",\"act\":\"{0} meet {1}\",\"permission\":\"y_permitted\""
def yPerm : String := regJ "y_permitted" "[\"assistant\",\"user\"]" "permission" "allow" ",\"act\":\"{0} meet {1}\""
def μd : SoftDoc := must (decode (envOf [yReq, yPerm,
    "\"trusts\":{\"arguments\":[\"assistant\",\"user\"],\"description\":\"trusts\"}",
    attrJ "operator_allows_for" "operator" "[\"assistant\",\"user\"]"] (softJ [] [] false ["operator", "user"]))
  [strictR "n" "y_required" true ["operator", "user"]])
def trustsF : VE.Formula := .binary "trusts" (.var 1) (.var 0)
def wμ := wd μd (W [] [cond (.off "n" "operator") .necessary trustsF] [gr "user" "operator" "operator_allows_for"])
def doms2 : String → List Ent := fun s =>
  if s == "assistant" then ["a1", "a2"] else if s == "user" then ["u1", "u2"] else []
def baseμ : List GAtom := [("trusts", ["a1", "u2"]), ("operator_allows_for", ["a1", "u2"]), ("operator_allows_for", ["a2", "u1"])]
#eval chk "μ accepted" (verdict wμ) "accepted"
#eval chk "μ labels" ((weighLabelled wμ).map (·.1)) ["weigh:condition:0:necessary", "weigh:grant:n:user", "weigh:grant:n:user:condition:0"]
def μAll := (assignments μd doms2 []).filter fun t => holdsAll (admX wμ) (modelOf doms2 (baseμ ++ t))
#eval chk "μ 4 of 256" (μAll.length, (assignments μd doms2 []).length) (4, 256)
#eval chk "μ subsets" (μAll.all fun t => t.all fun a => a.2 == ["a1", "u2"]) true
def μOut (vs : List Ent) : List String := VE.Route.sortStrings (VE.SoftNorms.dedup (μAll.map fun t => toString (outcome μd (modelOf doms2 (baseμ ++ t)) "y_required" vs)))
#eval chk "μ (a1,u2)" (μOut ["a1", "u2"], (μAll.filter fun t => outcome μd (modelOf doms2 (baseμ ++ t)) "y_required" ["a1", "u2"]).map (·.length)) (["false", "true"], [0])
#eval chk "μ others" (μOut ["a2", "u1"], μOut ["a1", "u1"], μOut ["a2", "u2"]) (["true"], ["true"], ["true"])
#eval chk "μ swapped" (verdict (wd μd (W [] [cond (.off "n" "operator") .necessary (.binary "trusts" (.var 0) (.var 1))])))
  "TypeMismatch: Predicate 'trusts' expects ('assistant', 'user'), received ('user', 'assistant')"

/-! ### `weigh_alone_base_free`, 7.3's `strength_iff` rows, `Pack.conditions`, the refusal text -/

/-- `freeWitness` as atoms: each `outweighs` atom the disjunction of its sufficient conditions, each switch off. -/
def freeAtoms (w : WeighDoc) (b : List GAtom) (exc : List GAtom) : List GAtom :=
  let M := modelOf doms1 b
  b ++ exc ++ (outweighsTriples w.D).filterMap fun (a, L, H) =>
    if w.W.conditions.any (fun c => c.target == .outweighs a L H && c.kind == .sufficient && c.condition.eval M ["a"])
    then some (at1 (outweighsName a L H)) else none
def baseFree (w : WeighDoc) (bs : List (List GAtom)) : Bool :=
  bs.all fun b => (subsetsOf ((exceptedDecisions w.D).map fun e => at1 e.1)).all fun e =>
    holdsAll (weighPremises w) (modelOf doms1 (freeAtoms w b e))
#eval chk "base-free" (([wα, wb, wδ, wε, wκ] : List WeighDoc).all (baseFree · bases) &&
  ([wζ, wζ2, wζ3] : List WeighDoc).all (baseFree · basesZ)) true

def strengthQ (w : WeighDoc) (a L H : String) : Bool × Bool :=
  ((strengthPremises w).contains (bindAll (actSortsOf w.D a) (.not (outweighsF w.D a L H))),
   (outweighsTriples w.D).contains (a, L, H) && strictPair w H L)
def f9 := wd (must (alphaOf ["a", "b_"] [("a", "b_")] "a" "b_")) (W [("a", "b_")])
def f13 := wd (must (alphaOf ["c", "c_"] [("c", "c_")] "c" "c_")) (W [("c", "c_")])
def f10 := wd (must (decode (envOf predsA (softJ ["c", "c_", "l"] [("c_", "l"), ("c", "l")] true))
    [dfltR "h" "x_required" true (some "c_"), dfltR "l" "x_permitted" false (some "l")])) (W [("c_", "l")])
#eval chk "F9" (verdict f9, strengthQ f9 "x_permitted" "b" "_a", outweighsName "x_permitted" "b" "_a" == outweighsName "x_permitted" "b_" "a") ("accepted", (true, false), true)
#eval chk "F13" (verdict f13, strengthQ f13 "x_permitted" "c" "_c", outweighsName "x_permitted" "c" "_c" == outweighsName "x_permitted" "c_" "c") ("accepted", (true, false), true)
#eval chk "F10" (verdict f10, strengthQ f10 "_x_permitted" "l" "c", outweighsName "_x_permitted" "l" "c" == outweighsName "x_permitted" "l" "c_") ("accepted", (false, false), true)

#eval chk "conditions ε" ((weighConditions wε).map (·.1)) [.outweighs "x_permitted" "b" "a"]
#eval chk "conditions δ" (weighConditions wδ).length 0
#eval chk "conditions ζ2" (weighConditions wζ2).length 0
#eval chk "AP's texts" (VE.Acts.splitRefusal "rule" "r", VE.Acts.splitRefusal "definition" "d")
  ("InvalidInput: rule r names a predicate that is split into parts; name one of its parts",
   "InvalidInput: definition d names a predicate that is split into parts; name one of its parts")

/-! ### 2.5 and 7.6: frames, objects, refusals -/

def vb (p : String) : String := match p with
  | "operator_allows" => "the operator allows it"
  | "operator_permits" => "the operator permits it"
  | _ => p
def rd (D : SoftDoc) (f : WeighFrame) : Except String WeighStatement := readFrame D vb f
instance : BEq (Except String WeighStatement) := ⟨fun a b => match a, b with
  | .ok x, .ok y => x == y
  | .error x, .error y => x == y
  | _, _ => false⟩
instance : Repr (Except String WeighStatement) := ⟨fun e _ => match e with
  | .ok x => repr x
  | .error m => repr m⟩
#eval chk "E1" (rd α (.always "a" "b")) (.ok (.always "a" "b"))
#eval chk "E2" (rd α (.generally "a" "b")) (.ok (.edge "a" "b"))
#eval chk "E2 strict" (rd αs (.generally "a" "b")) (.error "GenerallyUnderStrictOutranking: a, b")
#eval chk "E3 = δ" (rd α (.onlyWhen "x_permitted" "b" "a" urgent)) (.ok (.condition (cond (tOut "b" "a") .necessary urgent)))
#eval chk "E4 = ε" (rd α (.whenever "x_permitted" "b" "a" urgent)) (.ok (.condition (cond (tOut "b" "a") .sufficient urgent)))
#eval chk "E5" (rd α (.account "x_permitted" "b" "a" ["f"])) (.ok (.factors ⟨tOut "b" "a", ["f"]⟩))
#eval chk "E6 = ζ2" (rd ζd (.switchOnly "operator" "n" emergency)) (.ok (.condition (cond (.off "n" "operator") .necessary emergency)))
#eval chk "switch when" (rd ζd (.switchWhen "user" "n" emergency)) (.error "InvalidInput: a switch condition must say \"only when\"")
def ζ2g : GrantDecl := gr "user" "operator" "operator_allows"
#eval chk "E7 one" (rd ζd (.allows "user" "n" "operator")) (.ok (.grant ζ2g))
#eval chk "E7′" (rd ζd (.allowsNamely "user" "n" "operator" "operator_allows")) (.ok (.grant ζ2g))
#eval chk "candidates skip the binary predicate" (grantCandidates ζd "n" "operator") ["operator_allows"]
def ζ0 := zOf ["operator", "user"] (preds := [xReq, xPerm, baseJ "emergency", attrJ "operator_allows" "user",
  attrJ "operator_allows_for" "operator" "[\"assistant\",\"user\"]"])
#eval chk "E7 zero" (rd ζ0 (.allows "user" "n" "operator"))
  (.error "InvalidInput: rule n: no predicate records an instruction of operator over this rule's arguments; declare one first")
def ζ9 := zOf ["operator", "user"] (preds := predsZ ++ [attrJ "operator_permits" "operator"])
#eval chk "E7 several" (rd ζ9 (.allows "user" "n" "operator"))
  (.error "InvalidInput: rule n: several predicates record an instruction of operator; add one of: namely where the operator allows it; namely where the operator permits it")
def wζ9 := wd ζ9 (W [] [cond (.off "n" "operator") .necessary emergency] [gr "user" "operator" "operator_allows"])
#eval chk "E7′ on several, inherits" (verdict wζ9, (grantConds wζ9).map (·.1))
  ("accepted", ["weigh:grant:n:user", "weigh:grant:n:user:condition:0"])
#eval chk "generally row" (VE.EnglishGrammar.sourceWordsValid [generallyRow]) true

/-! ### W-ι: identity -/
def idOf (env : Json) : Except String String := do
  VE.Route.Wire.environmentId (VE.NormDefaults.Wire.profilesOf env) (← VE.NormDefaults.Wire.canonicalEnvironmentJsonU env)
def ndProfiles := ["norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0", "weighing@0"]
def blockJ (j : Json) (b : Json) : Json :=
  let v := (j.getObjValD "vocabulary").setObjVal! "weighing" b
  j.setObjVal! "vocabulary" v
def ιbase := envOf predsA (softJ ["a", "b"] [("a", "b")] true) ndProfiles
def ι1 := blockJ ιbase (Json.mkObj [("always", toJson [["a", "b"]])])
def ι2 := blockJ ιbase (Json.mkObj [("always", toJson [["a", "b"]]), ("factors", Json.arr #[Json.mkObj [("target", Json.mkObj [("outweighs", Json.mkObj [("act", "x_permitted"), ("lower", "b"), ("higher", "a")])]), ("factors", toJson ["how much the user would lose"])]])])
#eval chk "ι ids" (idOf ι1 |>.toOption, idOf ι2 |>.toOption, idOf ιbase |>.toOption)
  (some "9bf0a85662d0ff89af34af0d2c890c214da9dfbc77f36a06d8d89120bccc1404",
   some "1eb9fdd2c2f73f1f35d4bab3f56518ca92ac7bdf862ae3c0d323abec8589fc7f",
   some "025c8e3dbcca2470d37a659329d47bcee3d69c249f37119b0395fb240d86c0c3")

end VE.Weighing.Fix

/-! ### Short statements proved here -/

-- proved: weigh_conservative
theorem VE.Weighing.weigh_conservative (D : VE.SoftNorms.SoftDoc) (sm : VE.Acts.SplitMap) :
    weighPremises ⟨D, WeighEnv.empty, sm⟩ = [] := by
  simp [weighPremises, weighLabelled, weighEntries, strengthEntries, condEntries, grantEntries, grantConds, WeighEnv.empty]

-- proved: factors_inert
theorem VE.Weighing.factors_inert (D : VE.SoftNorms.SoftDoc) (W : WeighEnv) (sm : VE.Acts.SplitMap) (fs : List FactorDecl) :
    weighPremises ⟨D, {W with factors := fs}, sm⟩ = weighPremises ⟨D, W, sm⟩ := rfl

-- proved: weighPack_shape
theorem VE.Weighing.weighPack_shape (Wd : WeighDoc) :
    (weighPack Wd).id = "weighing" ∧ (weighPack Wd).kind = .constraint ∧ (weighPack Wd).decls = [] ∧
      (weighPack Wd).consts = [] ∧ (weighPack Wd).labelled = weighLabelled Wd ∧
      (weighPack Wd).origins.map (·.1) = (weighLabelled Wd).map (·.1) ∧
      (weighPack Wd).conditions = weighConditions Wd := by
  simp [weighPack, weighLabelled, weighOrigins, Function.comp_def]

-- proved: readFrame_kinds
theorem VE.Weighing.readFrame_kinds (D : VE.SoftNorms.SoftDoc) (verbal : String → String) (x l h : String) (c : VE.Formula) :
    readFrame D verbal (.onlyWhen x l h c) = .ok (.condition ⟨.outweighs x l h, .necessary, c⟩) ∧
    readFrame D verbal (.whenever x l h c) = .ok (.condition ⟨.outweighs x l h, .sufficient, c⟩) := ⟨rfl, rfl⟩

-- proved: readFrame_always
theorem VE.Weighing.readFrame_always (D : VE.SoftNorms.SoftDoc) (verbal : String → String) (a b : String) :
    readFrame D verbal (.always a b) = .ok (.always a b) := rfl

-- proved: readFrame_generally
theorem VE.Weighing.readFrame_generally (D : VE.SoftNorms.SoftDoc) (verbal : String → String) (a b : String) :
    (D.soft.outranking = .holistic → readFrame D verbal (.generally a b) = .ok (.edge a b)) ∧
    (D.soft.outranking = .strict → readFrame D verbal (.generally a b) = .error (generallyRefusal a b)) := by
  constructor <;> intro h <;> simp [readFrame, h]

-- proved: readFrame_allows
theorem VE.Weighing.readFrame_allows (D : VE.SoftNorms.SoftDoc) (verbal : String → String) (π n g p : String)
    (hc : grantCandidates D n g = [p]) :
    readFrame D verbal (.allows π n g) = .ok (.grant ⟨n, π, g, p⟩) ∧
    readFrame D verbal (.allows π n g) = readFrame D verbal (.allowsNamely π n g p) := by
  simp [readFrame, hc]

-- proved: readFrame_allows_none
theorem VE.Weighing.readFrame_allows_none (D : VE.SoftNorms.SoftDoc) (verbal : String → String) (π n g : String)
    (hc : grantCandidates D n g = []) :
    readFrame D verbal (.allows π n g) = .error (noGrantRefusal n g) := by
  simp [readFrame, hc]

-- proved: readFrame_allows_several
theorem VE.Weighing.readFrame_allows_several (D : VE.SoftNorms.SoftDoc) (verbal : String → String) (π n g : String)
    (ps : List String) (hc : grantCandidates D n g = ps) (hl : 2 ≤ ps.length) :
    readFrame D verbal (.allows π n g) = .error (severalGrantsRefusal verbal n g ps) := by
  subst hc
  match h : grantCandidates D n g, hl with
  | _ :: _ :: _, _ => simp [readFrame, h]
