import VE.SoftNorms.Tree

/-! The elaboration `soften(T) = T′` over `E′` (docs/spec/soft-norms.md 4.2, 5 and
6.1) and the executable well-formedness check `WellFormedSoft` (4.1, 8).

Every step of `ValueSoft` has a generated formula here, written with W1's
connectives (`anyF`, `atom`, `bindAll`) and fuel conventions:

* strict selection (`strictDecidesF`, 4.2 step 1) is computed on the *strict core*
  of the document (`coreNode`: ranks, exceptions, `hard` and the switches of
  default rules removed), so that it syntactically cannot read a weighing input;
* `blockedF` (step 2), `eligibleF`, `effF`/`dominatedF` (step 3, fuel `g`: `effF`
  at `g + 1` inlines `effF` at `g` for every higher comparable colliding rule);
* `derived` is the one derived carve-out per rule (5.1), omitted when it is
  syntactically `⊥` (a strict rule without switches), and `soften` adds it after
  the author carve-outs, keeping every predicate, sign, guard and `over` edge.

`WellFormedSoft` runs the diagnostics in the spec's order (environment block, W1's
checks on the base document, the soft rule checks in document order, `over`
against modes, ranks and ties, the size of the unfolded carve-outs and W1's
`validate` on `soften D`), then `softSemanticCheck`: the facts the proofs use,
each implied by the diagnostics (as W1's `semanticCheck` is), so it rejects no
document the diagnostics accept. -/
namespace VE.SoftNorms
open VE.Norms

/-! ## Step 1: strict selection on the strict core -/

def switchIn (regs : List Regulated) (N : SoftNode) : VE.Formula :=
  anyF (N.alterable.map (fun π => atom (offName N π) (sortsIn regs N.pred)))

/-- A strict rule is live: guard, no author carve-out, no switch. -/
def liveStrictIn (regs : List Regulated) (N : SoftNode) : VE.Formula :=
  .and (.and N.guard (.not (anyF N.carveOuts))) (.not (switchIn regs N))

def strictYieldsIn (regs : List Regulated) (ns : List SoftNode) : Nat → SoftNode → VE.Formula
  | 0, N => .or (if N.mode = .strict then liveStrictIn regs N else .bottom) (anyF [])
  | f + 1, N => .or (if N.mode = .strict then liveStrictIn regs N else .bottom)
      (anyF ((childrenIn ns N).map (strictYieldsIn regs ns f)))

def strictSelectsIn (regs : List Regulated) (ns : List SoftNode) (f : Nat) (N : SoftNode) : VE.Formula :=
  if N.mode = .strict then
    .and (liveStrictIn regs N) (.not (anyF ((childrenIn ns N).map (strictYieldsIn regs ns f))))
  else .bottom

def strictDecidesIn (regs : List Regulated) (ns : List SoftNode) (p : String) (sign : Bool) : VE.Formula :=
  anyF (((ns.filter (·.pred == p)).filter (·.sign == sign)).map (strictSelectsIn regs ns ns.length))

/-- The strict core of a rule: what strict selection may read. -/
def coreNode (N : SoftNode) : SoftNode :=
  { N with rank := none, exception := none, hard := false,
           alterable := if N.mode = .strict then N.alterable else [] }

/-- `P^s_p` (`sign = true`) and `N^s_p` (`sign = false`). -/
def strictDecidesF (D : SoftDoc) (p : String) (sign : Bool) : VE.Formula :=
  strictDecidesIn D.T.regulated (D.T.nodes.map coreNode) p sign

def strictPos (D : SoftDoc) (p : String) : VE.Formula := strictDecidesF D p true
def strictNeg (D : SoftDoc) (p : String) : VE.Formula := strictDecidesF D p false

/-! ## Steps 0, 2 and 3 -/

def switchF (D : SoftDoc) (N : SoftNode) : VE.Formula := switchIn D.T.regulated N
def exceptedF (D : SoftDoc) (N : SoftNode) : VE.Formula := atom (exceptedName N) (sortsOf D N.pred)

/-- `live_N`: guard, no author carve-out, no switch, and for a default rule no exception. -/
def liveF (D : SoftDoc) (N : SoftNode) : VE.Formula :=
  .and (liveStrictIn D.T.regulated N) (if N.mode = .default then .not (exceptedF D N) else .top)

/-- `blocked_N`: a strict rule decides the predicate either way, or decides the
act against `N`'s effect across the declared pair. -/
def blockedF (D : SoftDoc) (N : SoftNode) : VE.Formula :=
  .or (.or (.or (strictPos D N.pred) (strictNeg D N.pred))
      (if N.sign then (match dualPerm D N.pred with
        | some m => strictNeg D m
        | none => .bottom) else .bottom))
    (if N.sign then .bottom else (match dualOblig D N.pred with
      | some r => strictPos D r
      | none => .bottom))

def eligibleF (D : SoftDoc) (N : SoftNode) : VE.Formula :=
  if N.mode = .default then .and (liveF D N) (.not (blockedF D N)) else .bottom

def outweighsF (D : SoftDoc) (a L H : String) : VE.Formula := atom (outweighsName a L H) (actSortsOf D a)

/-- The opponents that may dominate `N`: default, incompatible and comparable. -/
def opponents (D : SoftDoc) (N : SoftNode) : List SoftNode :=
  D.T.nodes.filter (fun M => Incompatible D M N && M.mode == .default && Comparable D M N)

/-- `dom(M, N)` for each opponent, given the formula `eff` of the opponents' effectiveness. -/
def domWith (D : SoftDoc) (eff : SoftNode → VE.Formula) (N : SoftNode) : VE.Formula :=
  anyF ((opponents D N).map (fun M =>
    .or (if higher D M N = true then
          .and (eff M) (if D.soft.outranking = .holistic then .not (outweighsF D (act D N) (rk N) (rk M)) else .top)
         else .bottom)
        (if D.soft.outranking = .holistic ∧ higher D N M = true then
          .and (eligibleF D M) (outweighsF D (act D N) (rk M) (rk N))
         else .bottom)))

/-- `eff_N` with fuel: at `g + 1` the dominance of `N` inlines `eff` at `g`. -/
def effF (D : SoftDoc) : Nat → SoftNode → VE.Formula
  | 0, N => eligibleF D N
  | g + 1, N => .and (eligibleF D N) (.not (domWith D (effF D g) N))

def dominatedF (D : SoftDoc) (g : Nat) (N : SoftNode) : VE.Formula := domWith D (effF D g) N

/-! ## The derived carve-out and `soften` (5.1) -/

def derived (D : SoftDoc) (N : SoftNode) : VE.Formula :=
  match N.mode with
  | .strict => switchF D N
  | .default => .or (.or (.or (exceptedF D N) (switchF D N)) (blockedF D N)) (dominatedF D D.soft.ranks.length N)

/-- `[]` exactly when `N` is strict and unswitchable (a hard rule). -/
def derivedList (D : SoftDoc) (N : SoftNode) : List VE.Formula :=
  if N.mode = .strict ∧ N.alterable = [] then [] else [derived D N]

def primeNode (D : SoftDoc) (N : SoftNode) : Node :=
  { N.toNode with carveOuts := N.carveOuts ++ derivedList D N }

/-- `soften D = ⟨E′, lits, T′⟩`. -/
def soften (D : SoftDoc) : Doc :=
  ⟨envPrime D, D.lits, ⟨D.T.regulated, D.T.definitions, D.T.nodes.map (primeNode D)⟩⟩

/-! ## Selection on `T′`, exception and coherence premises (6.1) -/

/-- `selects′_N`: W1's `selects` on `T′`. -/
def selects' (D : SoftDoc) (N : SoftNode) : VE.Formula :=
  VE.Norms.selects (soften D).T (VE.Norms.fuel (soften D).T) (primeNode D N)

/-- `P^d_p` / `N^d_p`: some default rule of the sign selects on `T′`. -/
def defaultDecidesF (D : SoftDoc) (p : String) (sign : Bool) : VE.Formula :=
  anyF ((((rulesOn D p).filter (·.mode == .default)).filter (·.sign == sign)).map (selects' D))

def defaultPos (D : SoftDoc) (p : String) : VE.Formula := defaultDecidesF D p true
def defaultNeg (D : SoftDoc) (p : String) : VE.Formula := defaultDecidesF D p false

/-- `Exc_T` for one rule: `∀x̄. C → excepted_N` per sufficient and `∀x̄. excepted_N → C`
per necessary condition. -/
def excPremisesOf (D : SoftDoc) (N : SoftNode) : List VE.Formula :=
  match N.mode, N.exception with
  | .default, some e =>
    e.sufficient.map (fun C => bindAll (sortsOf D N.pred) (.implies C (exceptedF D N))) ++
      e.necessary.map (fun C => bindAll (sortsOf D N.pred) (.implies (exceptedF D N) C))
  | _, _ => []

def excPremises (D : SoftDoc) : List VE.Formula := D.T.nodes.flatMap (excPremisesOf D)

/-- The coherence conjunct of a colliding pair: `∀x̄. ¬(selects′_M° ∧ selects′_N°)`. -/
def cohPremise (D : SoftDoc) (M N : SoftNode) : VE.Formula :=
  bindAll (actSorts D M) (.not (.and (subst (soften D).T (size (soften D)) (selects' D M))
                                     (subst (soften D).T (size (soften D)) (selects' D N))))

def cohPremises (D : SoftDoc) : List VE.Formula := (collidingPairs D).map (fun (M, N) => cohPremise D M N)

/-- `Soft_T := Exc_T ++ Coh_T`, the `soft` Background slot. -/
def softPremises (D : SoftDoc) : List VE.Formula := excPremises D ++ cohPremises D

/-! ## The executable check (4.1, 8) -/

/-- Formula size in nodes (`MAX_NODES` counts the same way). -/
def fsize : VE.Formula → Nat
  | .top | .bottom | .unary .. | .binary .. | .eq .. => 1
  | .not a | .all _ a | .ex _ a => 1 + fsize a
  | .and a b | .or a b | .implies a b => 1 + fsize a + fsize b

def maxNodes : Nat := 10000

def dupOf (ns : List String) : Option String := ns.find? (fun n => ns.count n > 1)

def sortedDistinct (l : List String) : Bool := decide l.Nodup && l == VE.Route.sortStrings l

/-- A name reserved by the canonical decision names (1.3). -/
def reservedPredicate (p : String) : Bool := p.startsWith "soft__"
def containsDunder (s : String) : Bool := (s.splitOn "__").length > 1

def definedOrRegulated (D : SoftDoc) (p : String) : Bool :=
  (D.T.regulated.map (·.name)).contains p || (D.T.definitions.map (·.name)).contains p

/-- The environment `soft` block (3.1). -/
def checkSoftEnv (D : SoftDoc) : Except String Unit := do
  let env := D.soft
  if env.parties.length > 8 then throw "ResourceLimit: parties"
  if env.ranks.length > 16 then throw "ResourceLimit: ranks"
  if let some a := dupOf env.ranks then throw s!"DuplicateDeclaration: rank {a}"
  if let some π := dupOf env.parties then throw s!"DuplicateDeclaration: party {π}"
  for x in env.ranks ++ env.parties do
    if containsDunder x || x.isEmpty then throw s!"InvalidInput: invalid soft name {x}"
  for e in env.outranks ++ env.ties do
    unless env.ranks.contains e.1 do throw s!"UnknownRank: {e.1}"
    unless env.ranks.contains e.2 do throw s!"UnknownRank: {e.2}"
  if env.outranking = .holistic && env.outrankingDecider.isNone then
    throw "MissingExceptionDecider: outranking"
  for d in env.outrankingDecider.toList ++ env.exceptionDecider.toList do
    if d.utf8ByteSize > 64 then throw "InvalidInput: invalid soft fields for environment"
  for (p, π) in env.instructionOf do
    unless env.parties.contains π do throw s!"UnknownSymbol: party {π}"
    if definedOrRegulated D p || (D.E.predicates p).isNone then throw s!"InvalidInput: instruction_of on {p}"

/-- One rule's soft checks, in the order of 8: mode and fields, rank, parties,
decider, `hard`, exception typing. -/
def checkSoftRule (D : SoftDoc) (N : SoftNode) : Except String Unit := do
  let env := D.soft
  match N.mode, N.exception with
  | .strict, some _ => throw s!"InvalidInput: rule {N.name} is strict and declares an exception"
  | .default, none => throw s!"InvalidInput: invalid soft fields for {N.name}"
  | _, _ => pure ()
  unless sortedDistinct N.alterable do throw s!"InvalidInput: invalid soft fields for {N.name}"
  if let some e := N.exception then
    unless e.factors.all (·.utf8ByteSize ≤ 200) && (e.decidedBy.all (·.utf8ByteSize ≤ 64)) do
      throw s!"InvalidInput: invalid soft fields for {N.name}"
  if let some a := N.rank then
    unless env.ranks.contains a do throw s!"UnknownRank: rule {N.name}, {a}"
  for π in N.alterable do
    unless env.parties.contains π do throw s!"UnknownSymbol: party {π}"
  if let some e := N.exception then
    if e.decidedBy.isNone && env.exceptionDecider.isNone then
      throw s!"MissingExceptionDecider: rule {N.name}"
  if N.hard && (N.mode == .default || !N.alterable.isEmpty) then
    throw s!"HardConstraintAltered: rule {N.name}"
  if let some e := N.exception then
    for C in e.sufficient ++ e.necessary do
      if let some q := (preds C).find? (fun q => definedOrRegulated D q || reservedPredicate q) then
        throw s!"InvalidInput: exception condition of rule {N.name} mentions {q}"
      typeDiagnostic D.E (sortsOf D N.pred).reverse C
      unless C.check D.E (sortsOf D N.pred).reverse do
        throw s!"InvalidInput: ill-typed rule {N.name}"

/-- The diagnostics of 4.1 in the order of 8. -/
def checkSoft (D : SoftDoc) : Except String Unit := do
  let env := D.soft
  checkSoftEnv D
  for (p, _) in D.T.regulated.map (fun r => (r.name, r.sorts)) do
    if containsDunder p then throw s!"InvalidInput: invalid soft name {p}"
  for p in D.T.definitions.map (·.name) do
    if reservedPredicate p then throw s!"InvalidInput: invalid soft name {p}"
  VE.Norms.check D.base
  for N in D.T.nodes do
    checkSoftRule D N
  for N in D.T.nodes do
    if N.mode = .default then
      for m in N.over do
        match D.T.nodes.find? (·.name == m) with
        | some M => if M.mode = .strict then throw s!"SoftOverHard: rule {N.name} over {M.name}"
        | none => pure ()
  match dependencyOrderOf env with
  | .error e => throw e
  | .ok _ => pure ()
  for (a, b) in env.ties do
    if outranksPlus env a b || outranksPlus env b a then throw s!"TieAgainstOrder: {a}, {b}"
  for N in D.T.nodes do
    if (derivedList D N).any (fun φ => fsize φ > maxNodes) then
      throw s!"ResourceLimit: derived carve-out of rule {N.name}"
  VE.Norms.validate (soften D)
where
  dependencyOrderOf (env : SoftEnv) : Except String (List String) := VE.Route.dependencyOrder (rankNodes env)

/-- The facts the proofs use; each follows from the diagnostics above. -/
def softSemanticCheck (D : SoftDoc) : Bool :=
  VE.Norms.WellFormed (soften D) &&
  decide (D.T.nodes.map (·.name)).Nodup &&
  decide (D.T.regulated.map (·.name)).Nodup &&
  decide ((pairs D.base.T).map (·.req)).Nodup &&
  decide ((pairs D.base.T).map (·.perm)).Nodup &&
  (pairs D.base.T).all (fun pr => !((pairs D.base.T).map (·.req)).contains pr.perm) &&
  D.T.nodes.all (fun N => (D.T.regulated.map (·.name)).contains N.pred) &&
  D.soft.outranks.all (fun e => D.soft.ranks.contains e.1 && D.soft.ranks.contains e.2) &&
  (VE.Route.dependencyOrder (rankNodes D.soft)).isOk &&
  D.T.nodes.all (fun N => N.mode != .default ||
    N.over.all (fun m => (D.T.nodes.find? (·.name == m)).all (·.mode == .default))) &&
  decide (decisionNames D).Nodup &&
  (decisionNames D).all (fun n => (D.E.predicates n).isNone) &&
  D.T.nodes.all (fun N => (N.guard :: N.carveOuts).all (fun φ => φ.check D.E (sortsOf D N.pred).reverse)) &&
  (softPremises D).all (fun φ => φ.check (envAt (soften D) 0) []) &&
  D.T.regulated.all (fun r =>
    [strictPos D r.name, strictNeg D r.name, defaultPos D r.name, defaultNeg D r.name].all
      (fun φ => φ.check (envAt (soften D) (size (soften D))) r.sorts.reverse))

def validateSoft (D : SoftDoc) : Except String Unit :=
  match checkSoft D with
  | .error e => .error e
  | .ok () => if softSemanticCheck D then .ok () else .error "InvalidInput: soft norm document is not stratified"

/-- `WellFormedSoft` (4.1): the soft checks, then W1's `WellFormed` on the unfolded `T′`. -/
def WellFormedSoft (D : SoftDoc) : Bool :=
  match validateSoft D with
  | .ok () => true
  | .error _ => false

theorem softSemanticCheck_of_wellFormed (D : SoftDoc) (h : WellFormedSoft D = true) :
    softSemanticCheck D = true := by
  unfold WellFormedSoft validateSoft at h
  split at h <;> rename_i heq
  · split at heq
    · cases heq
    · split at heq
      · assumption
      · cases heq
  · cases h

/-! ## The facts behind the proofs -/

structure SoftValid (D : SoftDoc) : Prop where
  wf : VE.Norms.WellFormed (soften D) = true
  names : (D.T.nodes.map (·.name)).Nodup
  regNames : (D.T.regulated.map (·.name)).Nodup
  pairReq : ((pairs D.base.T).map (·.req)).Nodup
  pairPerm : ((pairs D.base.T).map (·.perm)).Nodup
  permNotReq : ∀ pr ∈ pairs D.base.T, pr.perm ∉ (pairs D.base.T).map (·.req)
  predReg : ∀ N ∈ D.T.nodes, N.pred ∈ D.T.regulated.map (·.name)
  ranks : RanksValid D.soft
  softOverHard : ∀ N ∈ D.T.nodes, N.mode = .default → ∀ m ∈ N.over,
    ∀ M, D.T.nodes.find? (·.name == m) = some M → M.mode = .default
  decNodup : (decisionNames D).Nodup
  decFresh : ∀ n ∈ decisionNames D, D.E.predicates n = none
  typed : ∀ N ∈ D.T.nodes, ∀ φ ∈ N.guard :: N.carveOuts, φ.WellFormed D.E (sortsOf D N.pred).reverse
  premTyped : ∀ φ ∈ softPremises D, φ.WellFormed (envAt (soften D) 0) []
  decTyped : ∀ r ∈ D.T.regulated, ∀ φ ∈ [strictPos D r.name, strictNeg D r.name, defaultPos D r.name,
    defaultNeg D r.name], φ.WellFormed (envAt (soften D) (size (soften D))) r.sorts.reverse

theorem softValid_of_wellFormed (D : SoftDoc) (h : WellFormedSoft D = true) : SoftValid D := by
  have hs := softSemanticCheck_of_wellFormed D h
  simp only [softSemanticCheck, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true,
    Bool.not_eq_true', List.contains_iff_mem, Bool.or_eq_true, bne_iff_ne, ne_eq,
    Option.all_eq_true, Option.isNone_iff_eq_none, beq_iff_eq] at hs
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨hwf, hn⟩, hr⟩, hpr⟩, hpp⟩, hpn⟩, hpred⟩, hout⟩, hord⟩, hsoh⟩, hdn⟩, hdf⟩, hty⟩, hpt⟩,
    hdt⟩ := hs
  refine ⟨hwf, hn, hr, hpr, hpp, fun pr hpr' hm => ?_, hpred, ⟨hout, VE.Norms.isOk_ok hord⟩,
    fun N hN hd m hm M hM => ?_, hdn, hdf,
    fun N hN φ hφ => (VE.check_iff_wellFormed _ _ _).mp (hty N hN φ hφ),
    fun φ hφ => (VE.check_iff_wellFormed _ _ _).mp (hpt φ hφ),
    fun r hr' φ hφ => (VE.check_iff_wellFormed _ _ _).mp (hdt r hr' φ hφ)⟩
  · have := hpn pr hpr'
    simp_all
  · rcases hsoh N hN with h | h
    · exact absurd hd h
    · have := h m hm
      rw [hM] at this
      simpa using this

/-! ## Shape of the elaboration -/

/-- 4.1 ⇒ W1 well-formedness of `T′` over `E′`. -/
theorem soften_wellFormed (D : SoftDoc) (h : WellFormedSoft D = true) :
    VE.Norms.WellFormed (soften D) = true :=
  (softValid_of_wellFormed D h).wf

/-- 5.1: what `soften` changes and what it keeps. -/
theorem soften_shape (D : SoftDoc) (_h : WellFormedSoft D = true) :
    (soften D).E = envPrime D ∧ (soften D).lits = D.lits ∧
    (soften D).T.regulated = D.T.regulated ∧ (soften D).T.definitions = D.T.definitions ∧
    (soften D).T.nodes = D.T.nodes.map (fun N => { N.toNode with carveOuts := N.carveOuts ++ derivedList D N }) :=
  ⟨rfl, rfl, rfl, rfl, rfl⟩

theorem envPrime_of_no_decisions (D : SoftDoc) (h : decisions D = []) : envPrime D = D.E := by
  unfold envPrime
  rw [h]
  rfl

/-- All-hard documents elaborate to themselves (fixture ξ). -/
theorem soften_hard_identity (D : SoftDoc) (_h : WellFormedSoft D = true)
    (hh : ∀ N ∈ D.T.nodes, N.mode = .strict ∧ N.alterable = []) :
    envPrime D = D.E ∧ (soften D).T.nodes = D.T.nodes.map SoftNode.toNode := by
  have hcp : collidingPairs D = [] := by
    cases hc : collidingPairs D with
    | nil => rfl
    | cons x xs =>
      have hx : (x.1, x.2) ∈ collidingPairs D := by rw [hc]; exact List.mem_cons_self
      obtain ⟨hM, _, hd, _⟩ := mem_collidingPairs.mp hx
      rw [(hh _ hM).1] at hd
      cases hd
  refine ⟨envPrime_of_no_decisions D ?_, ?_⟩
  · simp only [decisions, exceptedDecisions, offDecisions, outweighsDecisions, outweighsTriples, hcp,
      List.append_eq_nil_iff, List.map_eq_nil_iff, List.filter_eq_nil_iff, List.flatMap_eq_nil_iff]
    refine ⟨⟨fun N hN => by simp [(hh N hN).1], fun N hN => by simp [(hh N hN).2]⟩, ?_⟩
    split <;> rfl
  · simp only [soften, List.map_inj_left]
    intro N hN
    simp [primeNode, derivedList, (hh N hN).1, (hh N hN).2]

end VE.SoftNorms
