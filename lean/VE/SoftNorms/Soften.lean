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

def maxNodes : Nat := 10000
def maxDepth : Nat := 64

/-- Python's `_Checker` budgets (`MAX_NODES`, term nodes included, and `MAX_DEPTH`)
on one generated formula, with `n` nodes already spent and the formula at depth
`d`: each formula node counts, then its depth is checked, then each term of an
atom counts. The node count after the formula, or `none` at the first overrun.
The walk stops there, so it visits at most `MAX_NODES + 1` nodes of a formula
however large its unfolding. -/
def limitWalk (n d : Nat) : VE.Formula → Option Nat
  | .top | .bottom => tick n d 0
  | .unary .. => tick n d 1
  | .binary .. | .eq .. => tick n d 2
  | .not a | .all _ a | .ex _ a => tick n d 0 >>= fun m => limitWalk m (d + 1) a
  | .and a b | .or a b | .implies a b =>
    tick n d 0 >>= fun m => limitWalk m (d + 1) a >>= fun k => limitWalk k (d + 1) b
where
  tick (n d terms : Nat) : Option Nat :=
    if n + 1 > maxNodes || d > maxDepth || n + 1 + terms > maxNodes then none else some (n + 1 + terms)

/-- One generated formula, serialised on its own (a fresh `_Checker`), is within
`MAX_NODES` and `MAX_DEPTH`. -/
def withinLimits (φ : VE.Formula) : Bool := (limitWalk 0 1 φ).isSome

/-! ## Sizes without construction

The size of a generated formula, `(nodes, depth)` as `limitWalk` counts them (term
nodes included), computed from per-rule tables instead of the formula: a rule's
`yields` and `eff` formulas are sized once per level and read by every formula
that inlines them, and an outcome substitution reads the size of each earlier
layer symbol's expansion (`inst` keeps sizes: terms are variables and constants).
A structure whose unfolding is far beyond `MAX_NODES` is therefore rejected in
time polynomial in the source, never built; the formulas are built only once
their sizes fit. `withinLimits φ` holds exactly when `fits (fsize noSubst φ)`
(`withinLimits_iff`). -/

abbrev FSize := Nat × Nat

def sLeaf : FSize := (1, 1)
def sNot (a : FSize) : FSize := (a.1 + 1, a.2 + 1)
def sBin (a b : FSize) : FSize := (a.1 + b.1 + 1, max a.2 b.2 + 1)
/-- `anyF` and `allF`: a left fold from a one-node constant. -/
def sFold (l : List FSize) : FSize := l.foldl sBin sLeaf
def sBind (sorts : List String) (a : FSize) : FSize := (a.1 + sorts.length, a.2 + sorts.length)

def fits (s : FSize) : Bool := s.1 ≤ maxNodes && s.2 ≤ maxDepth

/-- Formulas typed one after another by one checker: their nodes share one budget. -/
def fitsTogether (l : List FSize) : Bool :=
  (l.map (·.1)).foldl (· + ·) 0 ≤ maxNodes && l.all (·.2 ≤ maxDepth)

/-- The size an atom's symbol takes after substitution; `none` keeps the atom. -/
abbrev STable := String → Option FSize

def noSubst : STable := fun _ => none

def fsize (tbl : STable) : VE.Formula → FSize
  | .top | .bottom => sLeaf
  | .unary q _ => (tbl q).getD (2, 1)
  | .binary q _ _ => (tbl q).getD (3, 1)
  | .eq .. => (3, 1)
  | .not a | .all _ a | .ex _ a => sNot (fsize tbl a)
  | .and a b | .or a b | .implies a b => sBin (fsize tbl a) (fsize tbl b)

theorem tick_eq (n d t : Nat) :
    limitWalk.tick n d t = if n + 1 + t ≤ maxNodes ∧ d ≤ maxDepth then some (n + 1 + t) else none := by
  unfold limitWalk.tick
  by_cases h : n + 1 + t ≤ maxNodes ∧ d ≤ maxDepth
  · rw [if_pos h, if_neg (by simp only [Bool.or_eq_true, decide_eq_true_eq, not_or]; omega)]
  · rw [if_neg h, if_pos (by simp only [Bool.or_eq_true, decide_eq_true_eq]; omega)]

theorem fsize_pos (φ : VE.Formula) : 1 ≤ (fsize noSubst φ).1 ∧ 1 ≤ (fsize noSubst φ).2 := by
  cases φ <;> simp [fsize, noSubst, sLeaf, sNot, sBin]

theorem limitWalk_eq (φ : VE.Formula) : ∀ n d, 1 ≤ d →
    limitWalk n d φ = if n + (fsize noSubst φ).1 ≤ maxNodes ∧ d - 1 + (fsize noSubst φ).2 ≤ maxDepth
      then some (n + (fsize noSubst φ).1) else none := by
  induction φ with
  | top | bottom | unary | binary | eq =>
    intro n d hd
    simp only [limitWalk, tick_eq, fsize, noSubst, sLeaf, Option.getD_none]
    split <;> split <;> first | rfl | (simp only [Option.some.injEq]; omega) | (exfalso; omega)
  | not a ih | all _ a ih | ex _ a ih =>
    intro n d hd
    have := fsize_pos a
    simp only [limitWalk, tick_eq, fsize, sNot]
    split
    · simp only [Option.bind_eq_bind, Option.bind_some, ih (n + 1 + 0) (d + 1) (by omega)]
      split <;> split <;> first | rfl | (simp only [Option.some.injEq]; omega) | (exfalso; omega)
    · simp only [Option.bind_eq_bind, Option.bind_none]
      split
      · exfalso; omega
      · rfl
  | and a b iha ihb | or a b iha ihb | implies a b iha ihb =>
    intro n d hd
    have := fsize_pos a
    have := fsize_pos b
    simp only [limitWalk, tick_eq, fsize, sBin]
    split
    · simp only [Option.bind_eq_bind, Option.bind_some, iha (n + 1 + 0) (d + 1) (by omega)]
      split
      · simp only [Option.bind_some, ihb _ (d + 1) (by omega)]
        split <;> split <;> first | rfl | (simp only [Option.some.injEq]; omega) | (exfalso; omega)
      · simp only [Option.bind_eq_bind, Option.bind_none]
        split
        · exfalso; omega
        · rfl
    · simp only [Option.bind_eq_bind, Option.bind_none]
      split
      · exfalso; omega
      · rfl

/-- A formula is within both limits exactly when its size fits. -/
theorem withinLimits_iff (φ : VE.Formula) : withinLimits φ = fits (fsize noSubst φ) := by
  unfold withinLimits fits
  rw [limitWalk_eq φ 0 1 (Nat.le_refl 1)]
  by_cases h : (fsize noSubst φ).1 ≤ maxNodes ∧ (fsize noSubst φ).2 ≤ maxDepth
  · rw [if_pos (by omega)]
    simp [h.1, h.2]
  · rw [if_neg (by omega)]
    simp only [Option.isSome_none]
    exact (Bool.eq_false_iff.mpr (fun h' => h (by simpa using h'))).symm

/-- A table of sizes, one per rule, indexed by the rule's position. -/
def at' (a : Array FSize) (i : Nat) : FSize := a.getD i sLeaf

/-- The positions of `ns` named by `names`, in order. -/
def positions (ns : List SoftNode) (names : List String) : List Nat :=
  names.filterMap (fun n => ns.findIdx? (·.name == n))

/-- The sizes of a recursion `Y (f + 1) N = .or own_N (anyF (kids_N.map (Y f)))`,
`Y 0 N = .or own_N (anyF [])`, at level `f`: W1's `yields` and the strict core's
`strictYieldsIn`. -/
def levelSizes (own : Array FSize) (kids : Array (List Nat)) : Nat → Array FSize
  | 0 => own.map (fun s => sBin s sLeaf)
  | f + 1 =>
    let prev := levelSizes own kids f
    (own.zip kids).map (fun (s, ks) => sBin s (sFold (ks.map (at' prev))))

/-- The level read by `selects` at fuel `f`. Precedence height is at most 16 (6.6),
so a rule's `yields` at every level from 15 on is the same formula: levels past
16 repeat. -/
def capLevel (f : Nat) : Nat := min f 16

/-! ### The derived carve-outs (6.9) -/

/-- `strictSelectsIn` on the strict core, for every rule. -/
def strictSelectsSizes (D : SoftDoc) : Array FSize :=
  let regs := D.T.regulated
  let ns := D.T.nodes.map coreNode
  let live := (ns.map (fun N => fsize noSubst (liveStrictIn regs N))).toArray
  let own := (ns.map (fun N => if N.mode = .strict then fsize noSubst (liveStrictIn regs N) else sLeaf)).toArray
  let kids := (ns.map (fun N => positions ns ((childrenIn ns N).map (·.name)))).toArray
  let lvl := levelSizes own kids (capLevel ns.length)
  ((ns.zip (List.range ns.length)).map (fun (N, i) =>
    if N.mode = .strict then
      sBin (at' live i) (sNot (sFold ((kids.getD i []).map (at' lvl))))
    else sLeaf)).toArray

/-- `strictDecidesF D p sign`, from the strict selection sizes. -/
def strictDecidesSize (D : SoftDoc) (sel : Array FSize) (p : String) (sign : Bool) : FSize :=
  sFold (((D.T.nodes.zip (List.range D.T.nodes.length)).filter
    (fun (N, _) => N.pred == p && N.sign == sign)).map (fun (_, i) => at' sel i))

def blockedSize (D : SoftDoc) (sel : Array FSize) (N : SoftNode) : FSize :=
  sBin (sBin (sBin (strictDecidesSize D sel N.pred true) (strictDecidesSize D sel N.pred false))
      (if N.sign then (match dualPerm D N.pred with
        | some m => strictDecidesSize D sel m false
        | none => sLeaf) else sLeaf))
    (if N.sign then sLeaf else (match dualOblig D N.pred with
      | some r => strictDecidesSize D sel r true
      | none => sLeaf))

def eligibleSize (D : SoftDoc) (sel : Array FSize) (N : SoftNode) : FSize :=
  if N.mode = .default then sBin (fsize noSubst (liveF D N)) (sNot (blockedSize D sel N)) else sLeaf

/-- `domWith D eff N`, from the sizes of the opponents' `eff` and eligibility. -/
def domSize (D : SoftDoc) (elig eff : Array FSize) (opps : List (SoftNode × Nat)) (N : SoftNode) : FSize :=
  sFold (opps.map (fun (M, j) =>
    sBin (if higher D M N = true then
          sBin (at' eff j) (if D.soft.outranking = .holistic then
            sNot (fsize noSubst (outweighsF D (act D N) (rk N) (rk M))) else sLeaf)
         else sLeaf)
        (if D.soft.outranking = .holistic ∧ higher D N M = true then
          sBin (at' elig j) (fsize noSubst (outweighsF D (act D N) (rk M) (rk N)))
         else sLeaf)))

/-- The opponents of every rule with their positions, in `opponents` order. -/
def opponentTable (D : SoftDoc) : Array (List (SoftNode × Nat)) :=
  let indexed := D.T.nodes.zip (List.range D.T.nodes.length)
  (D.T.nodes.map (fun N => indexed.filter (fun (M, _) =>
    Incompatible D M N && M.mode == .default && Comparable D M N))).toArray

/-- `effF D g` for every rule. -/
def effSizes (D : SoftDoc) (elig : Array FSize) (opps : Array (List (SoftNode × Nat))) : Nat → Array FSize
  | 0 => elig
  | g + 1 =>
    let prev := effSizes D elig opps g
    ((D.T.nodes.zip (List.range D.T.nodes.length)).map (fun (N, i) =>
      sBin (at' elig i) (sNot (domSize D elig prev (opps.getD i []) N)))).toArray

/-- The size of every rule's derived carve-out `derived D N`. -/
def derivedSizes (D : SoftDoc) : List FSize :=
  let sel := strictSelectsSizes D
  let elig := (D.T.nodes.map (eligibleSize D sel)).toArray
  let opps := opponentTable D
  let eff := effSizes D elig opps D.soft.ranks.length
  (D.T.nodes.zip (List.range D.T.nodes.length)).map (fun (N, i) =>
    match N.mode with
    | .strict => fsize noSubst (switchF D N)
    | .default => sBin (sBin (sBin (fsize noSubst (exceptedF D N)) (fsize noSubst (switchF D N)))
        (blockedSize D sel N)) (domSize D elig eff (opps.getD i []) N))

/-! ### W1's formulas on `T′` (6.11 to 6.15)

After 6.10 the rules of `T′` are explicit and within W1's document budget; what
may still be exponential is the unfolding of `yields` over the precedence DAG and
of outcome substitution over the layers. -/

/-- The size of `selects T (fuel T) N` for every rule, atoms sized by `tbl`. -/
def selectsSizes (T : Tree) (tbl : STable) : Array FSize :=
  let app := (T.nodes.map (fun N => fsize tbl (applies N))).toArray
  let kids := (T.nodes.map (fun N => (VE.Norms.children T N).filterMap
    (fun C => T.nodes.findIdx? (·.name == C.name)))).toArray
  let lvl := levelSizes app kids (capLevel (VE.Norms.fuel T))
  (app.zip kids).map (fun (a, ks) => sBin a (sNot (sFold (ks.map (at' lvl)))))

/-- `decides T p sign`. -/
def decidesSize (T : Tree) (sel : Array FSize) (p : String) (sign : Bool) : FSize :=
  sFold (((T.nodes.zip (List.range T.nodes.length)).filter
    (fun (N, _) => N.pred == p && N.sign == sign)).map (fun (_, i) => at' sel i))

/-- `elabPremise T r` from the sizes of `P_p` and `N_p`. -/
def elabSize (r : Regulated) (P Nn : FSize) : FSize :=
  let A := fsize noSubst (atom r.name r.sorts)
  sBind r.sorts (sFold [sBin P A, sBin Nn (sNot A),
    sBin (sBin (sNot P) (sNot Nn)) (if r.allowByDefault then A else sNot A)])

/-- The expansion table in layer order (each symbol's meaning under the table of
the symbols before it, as `expTable`), and for each regulated symbol the sizes of
`P_p°` and `N_p°` under that prefix (`conflict`). -/
def expansionSizes (T : Tree) : List (String × FSize) × List (String × FSize × FSize) :=
  (syms T).foldl (fun (tbl, rows) q =>
    let t : STable := fun n => (tbl.find? (·.1 == n)).map (·.2)
    match q with
    | .reg r =>
      let sel := selectsSizes T t
      let P := decidesSize T sel r.name true
      let Nn := decidesSize T sel r.name false
      (tbl ++ [(r.name, if r.allowByDefault then sNot Nn else P)], rows ++ [(r.name, P, Nn)])
    | .defn d => (tbl ++ [(d.name, fsize t d.body)], rows)) ([], [])

/-- The sizes of the generated structures of 6.11 to 6.15, in their check order. -/
structure GeneratedSizes where
  /-- `softPremises D`: the exception premises, then the coherence premises. -/
  soft : List FSize
  /-- `elaborate T′`, one per regulated layer symbol. -/
  layers : List (String × FSize)
  /-- `targetConclusion t` for every `t ∈ targets (soften D)`. -/
  targets : List (String × FSize)

def generatedSizes (D : SoftDoc) : GeneratedSizes :=
  let T := (soften D).T
  let (tbl, rows) := expansionSizes T
  let full : STable := fun n => (tbl.find? (·.1 == n)).map (·.2)
  let selFull := selectsSizes T full
  let index (N : SoftNode) : Nat := (D.T.nodes.findIdx? (·.name == N.name)).getD 0
  let coh := (collidingPairs D).map (fun (M, N) =>
    sBind (actSorts D M) (sNot (sBin (at' selFull (index M)) (at' selFull (index N)))))
  let sel := selectsSizes T noSubst
  let layers := (syms T).filterMap (fun
    | .reg r => some (r.name, elabSize r (decidesSize T sel r.name true) (decidesSize T sel r.name false))
    | .defn _ => none)
  let entry (n : String) : FSize := match T.regulated.find? (·.name == n) with
    | some _ => (full n).getD sLeaf
    | none => sLeaf
  let targets := rows.map (fun (n, P, Nn) => (n, sBind (sortsIn T.regulated n) (sNot (sBin P Nn)))) ++
    (pairs T).map (fun pr => (pr.req ++ "->" ++ pr.perm,
      sBind pr.sorts (sNot (sBin (entry pr.req) (sNot (entry pr.perm))))))
  ⟨(excPremises D).map (fsize noSubst) ++ coh, layers, targets⟩

def dupOf (ns : List String) : Option String := ns.find? (fun n => ns.count n > 1)

/-! ### W1's checks with a memoized precedence height

W1's `check` computes `height` by recursion on every path of the precedence DAG,
which is exponential in a DAG of wide diamonds (sixteen levels of sixteen rules).
`checkW1` is the same sequence of checks and diagnostics, with the height of every
rule computed once per level. -/

/-- W1's `height T f N` for every rule of `T` at level `f`, by position. -/
def heightLevels (T : Tree) (kids : Array (List Nat)) : Nat → Array Nat
  | 0 => (T.nodes.map (fun _ => 1)).toArray
  | f + 1 =>
    let prev := heightLevels T kids f
    kids.map (fun ks => 1 + (ks.map (prev.getD · 1)).foldl max 0)

/-- `T.nodes.any (fun N => height T T.nodes.length N > 16)`, after the precedence DAG
passed `dependencyOrder`. On an acyclic DAG `height T f N = 1 + min f L` for the
longest path `L` below `N`, so for `f ≥ 16` it exceeds 16 exactly when it does at
level 16. -/
def heightExceeds (T : Tree) : Bool :=
  let kids := (T.nodes.map (fun N => (VE.Norms.children T N).filterMap
    (fun C => T.nodes.findIdx? (·.name == C.name)))).toArray
  (heightLevels T kids (min T.nodes.length 16)).any (· > 16)

/-- W1's `check` (declarations, rules, precedence and stratum DAGs), in its order
and with its diagnostics. -/
def checkW1 (D : Doc) : Except String Unit := do
  let T := D.T
  if T.regulated.length > 64 then throw "ResourceLimit: regulated predicates"
  let symNames := regulatedNames T ++ T.definitions.map Definition.name
  if let some n := dupOf symNames then throw s!"DuplicateDeclaration: predicate {n}"
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
  match VE.Route.dependencyOrder (precedenceNodes T) with
  | .error e => throw e
  | .ok _ => pure ()
  if heightExceeds T then throw "ResourceLimit: precedence depth"
  match VE.Route.dependencyOrder (stratumNodes T) with
  | .error e => throw e
  | .ok _ => pure ()

/-- W1's `validate`: `checkW1`, then the conditions of the metatheory. -/
def validateW1 (D : Doc) : Except String Unit :=
  match checkW1 D with
  | .error e => .error e
  | .ok () => if semanticCheck D then .ok () else .error "InvalidInput: norm document is not stratified"

/-- Whether a rule has a derived carve-out (`derivedList D N ≠ []`), without building it. -/
def hasDerived (N : SoftNode) : Bool := !(N.mode == .strict && N.alterable.isEmpty)

def sortedDistinct (l : List String) : Bool := decide l.Nodup && l == VE.Route.sortStrings l

/-- A name reserved by the canonical decision names (1.3). -/
def reservedPredicate (p : String) : Bool := p.startsWith "soft__"
def containsDunder (s : String) : Bool := (s.splitOn "__").length > 1

def validSoftName (s : String) : Bool :=
  match s.toList with
  | [] => false
  | first :: rest =>
    first ≥ 'a' && first ≤ 'z' &&
      rest.all (fun c => (c ≥ 'a' && c ≤ 'z') ||
                         (c ≥ '0' && c ≤ '9') || c == '_') &&
      s.utf8ByteSize ≤ 64 && !containsDunder s

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
    unless validSoftName x do throw s!"InvalidInput: invalid soft name {x}"
  for e in env.outranks ++ env.ties do
    unless env.ranks.contains e.1 do throw s!"UnknownRank: {e.1}"
    unless env.ranks.contains e.2 do throw s!"UnknownRank: {e.2}"
  if env.outranking = .holistic && env.outrankingDecider.isNone then
    throw "MissingExceptionDecider: outranking"
  if env.outranking = .strict && env.outrankingDecider.isSome then
    throw "InvalidInput: strict outranking has no decider"
  for d in env.outrankingDecider.toList do
    if d.isEmpty || d.utf8ByteSize > 64 then throw "InvalidInput: invalid decider for outranking"
  for d in env.exceptionDecider.toList do
    if d.isEmpty || d.utf8ByteSize > 64 then throw "InvalidInput: invalid decider for exception"
  for (field, pairs) in [("outranks", env.outranks), ("ties", env.ties)] do
    for pair in pairs do
      if pair.1 == pair.2 || pairs.count pair > 1 then
        throw s!"InvalidInput: invalid {field} pair"
  for (p, π) in env.instructionOf do
    unless env.parties.contains π do throw s!"UnknownSymbol: party {π}"
    if definedOrRegulated D p || (D.E.predicates p).isNone then throw s!"InvalidInput: instruction_of on {p}"

/-- One rule's soft checks, in the order of 8: mode and fields, rank, parties,
decider, `hard`, exception typing. -/
def checkSoftRule (D : SoftDoc) (N : SoftNode) : Except String Unit := do
  let env := D.soft
  if let some a := N.rank then
    unless env.ranks.contains a do throw s!"UnknownRank: rule {N.name}, {a}"
  unless sortedDistinct N.alterable do
    throw s!"InvalidInput: alterable of rule {N.name} must be sorted and distinct"
  for π in N.alterable do
    unless env.parties.contains π do throw s!"UnknownSymbol: party {π}"
  if N.hard && (N.mode == .default || !N.alterable.isEmpty) then
    throw s!"HardConstraintAltered: rule {N.name}"
  match N.mode, N.exception with
  | .strict, some _ => throw s!"InvalidInput: rule {N.name} is strict and declares an exception"
  | .default, none => throw s!"InvalidInput: rule {N.name} needs an exception"
  | _, _ => pure ()
  if let some e := N.exception then
    unless e.decidedBy.all (fun d => !d.isEmpty && d.utf8ByteSize ≤ 64) do
      throw s!"InvalidInput: invalid decider for rule {N.name}"
  if let some e := N.exception then
    if e.decidedBy.isNone && env.exceptionDecider.isNone then
      throw s!"MissingExceptionDecider: rule {N.name}"
  if let some e := N.exception then
    for C in e.sufficient ++ e.necessary do
      typeDiagnostic D.E (sortsOf D N.pred).reverse C
      unless C.check D.E (sortsOf D N.pred).reverse do
        throw s!"InvalidInput: ill-typed rule {N.name}"
      if let some q := (preds C).find? (fun q => definedOrRegulated D q || reservedPredicate q) then
        throw s!"InvalidInput: exception condition of rule {N.name} mentions {q}"
    unless e.factors.all (·.utf8ByteSize ≤ 200) do
      throw s!"InvalidInput: invalid factors of rule {N.name}"

/-- The diagnostics of 4.1 in the order of 8. -/
def checkSoft (D : SoftDoc) : Except String Unit := do
  let env := D.soft
  checkSoftEnv D
  for (p, _) in D.T.regulated.map (fun r => (r.name, r.sorts)) do
    if containsDunder p then throw s!"InvalidInput: invalid soft name {p}"
  for p in D.T.definitions.map (·.name) do
    if reservedPredicate p then throw s!"InvalidInput: invalid soft name {p}"
  checkW1 D.base
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
  if (env.ties.map (fun (a, b) => if a ≤ b then (a, b) else (b, a))).eraseDups.length != env.ties.length then
    throw "DuplicateDeclaration: tie"
  -- 6.9: the count, and each derived carve-out on its own within both limits, before
  -- 6.10 types `T′` and spends W1's one document budget on it. Sized first: a
  -- carve-out is built only once every carve-out fits.
  for (N, s) in D.T.nodes.zip (derivedSizes D) do
    if N.carveOuts.length + (if hasDerived N then 1 else 0) > 8 || (hasDerived N && !fits s) then
      throw s!"ResourceLimit: derived carve-out of rule {N.name}"
  for N in D.T.nodes do
    unless (derivedList D N).all withinLimits do
      throw s!"ResourceLimit: derived carve-out of rule {N.name}"
  validateW1 (soften D)
  -- 6.11: Python serialises each generated premise through its own `_Checker`; sized
  -- from the expansion table, then built.
  let sizes := generatedSizes D
  for s in sizes.soft do
    unless fits s do throw "ResourceLimit: generated soft premise"
  for φ in softPremises D do
    unless withinLimits φ do throw "ResourceLimit: generated soft premise"
  -- 6.12: likewise each generated norm layer `layer:norms:<p>`, in layer order, so an
  -- accepted document's whole elaboration serialises.
  for (p, s) in sizes.layers do
    unless fits s do throw s!"ResourceLimit: generated norm layer layer:norms:{p}"
  for s in syms (soften D).T do
    if let .reg r := s then
      unless withinLimits (elabPremise (soften D).T r) do
        throw s!"ResourceLimit: generated norm layer layer:norms:{r.name}"
  -- 6.13: each conflict target's certified conclusion `∀x̄. ¬conflict`, in target order,
  -- on its own: a target expands every lower predicate's outcome.
  for (t, s) in sizes.targets do
    unless fits s do throw s!"ResourceLimit: generated conflict target {t}"
  for t in targets (soften D) do
    unless withinLimits (targetConclusion t) do throw s!"ResourceLimit: generated conflict target {t.1}"
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
  decide (D.soft.below = closureOf D.soft.ranks D.soft.outranks) &&
  D.T.nodes.all (fun N => N.mode != .default ||
    N.over.all (fun m => (D.T.nodes.find? (·.name == m)).all (·.mode == .default))) &&
  decide (decisionNames D).Nodup &&
  (decisionNames D).all (fun n => (D.E.predicates n).isNone) &&
  D.T.nodes.all (fun N => (N.guard :: N.carveOuts).all (fun φ => φ.check D.E (sortsOf D N.pred).reverse)) &&
  (softPremises D).all (fun φ => φ.check (envAt (soften D) 0) []) &&
  D.T.nodes.all (fun N => (selects' D N).check (envAt (soften D) (size (soften D))) (sortsOf D N.pred).reverse) &&
  (collidingPairs D).all (fun x => sortsOf D x.1.pred == sortsOf D x.2.pred) &&
  D.T.regulated.all (fun r => (D.E.predicates r.name).isSome) &&
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
  selTyped : ∀ N ∈ D.T.nodes, (selects' D N).WellFormed (envAt (soften D) (size (soften D))) (sortsOf D N.pred).reverse
  cpSorts : ∀ x ∈ collidingPairs D, sortsOf D x.1.pred = sortsOf D x.2.pred
  regDecl : ∀ r ∈ D.T.regulated, (D.E.predicates r.name).isSome
  decTyped : ∀ r ∈ D.T.regulated, ∀ φ ∈ [strictPos D r.name, strictNeg D r.name, defaultPos D r.name,
    defaultNeg D r.name], φ.WellFormed (envAt (soften D) (size (soften D))) r.sorts.reverse

theorem softValid_of_wellFormed (D : SoftDoc) (h : WellFormedSoft D = true) : SoftValid D := by
  have hs := softSemanticCheck_of_wellFormed D h
  simp only [softSemanticCheck, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true,
    Bool.not_eq_true', List.contains_iff_mem, Bool.or_eq_true, bne_iff_ne, ne_eq,
    Option.all_eq_true, Option.isNone_iff_eq_none, beq_iff_eq] at hs
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨hwf, hn⟩, hr⟩, hpr⟩, hpp⟩, hpn⟩, hpred⟩, hout⟩, hord⟩, hcl⟩, hsoh⟩, hdn⟩, hdf⟩, hty⟩,
    hpt⟩, hst⟩, hcs⟩, hrd⟩, hdt⟩ := hs
  refine ⟨hwf, hn, hr, hpr, hpp, fun pr hpr' hm => ?_, hpred, ⟨hout, VE.Norms.isOk_ok hord, hcl⟩,
    fun N hN hd m hm M hM => ?_, hdn, hdf,
    fun N hN φ hφ => (VE.check_iff_wellFormed _ _ _).mp (hty N hN φ hφ),
    fun φ hφ => (VE.check_iff_wellFormed _ _ _).mp (hpt φ hφ),
    fun N hN => (VE.check_iff_wellFormed _ _ _).mp (hst N hN), hcs, hrd,
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
