import VE.Risk.Piecewise

/-! The log and the audit (docs/spec/risk.md 4.10 and 7.2).

`snapshotOf R log hd` reads only `logPrefix log hd.seq`: it checks the hash
chain over the prefix, finds the decision entry `(hd.id, hd.seq)` and runs the
admission of 4.4 (A1 to A3) with the prefix as the entries. The snapshot has
no outcome and no `taken` field. `auditQ12` answers Q1 (the decision report
replayed from the snapshot) and Q2 (the same replay with every live recorded
estimate of the record's quantities), with the procedure lines; it reads only
the prefix, so `verdict_ignores_outcomes` is structural. Q3 reads the outcome
entries by design and carries no theorem (7.4). -/
namespace VE.Risk
open Lean
open VE.Norms (tupleVal)

def logPrefix (log : Log) (k : Nat) : Log := log.filter (fun x => x.seq ≤ k)

structure DecisionRef where
  id : String
  seq : Nat
  deriving DecidableEq, Repr

/-- No outcome and no taken field. -/
structure Snapshot where
  decision : Decision
  entries : Log

/-- The hash chain: each entry's `prev` is the previous entry's hash (the first one's is empty), its recomputed
hash is its `hash` field, and sequence numbers strictly increase. -/
def chainFailure : Log → String → Nat → Option String
  | [], _, _ => none
  | x :: xs, prev, floor =>
    if x.prev != prev || entryHash x != x.hash then some s!"AlteredEntry: {x.id}"
    else if x.seq < floor then some "InvalidInput: risk-log.seq"
    else chainFailure xs x.hash (x.seq + 1)

def snapshotCore (R : RiskDoc) (pre : Log) (hd : DecisionRef) : Except String Snapshot :=
  match chainFailure pre "" 0 with
  | some e => .error e
  | none => match pre.find? (fun x => x.id == hd.id && x.seq == hd.seq && x.kind == .decision) with
    | none => .error s!"MissingEntry: {hd.id}"
    | some dx => match admitDecision R dx pre with
      | .error e => .error e
      | .ok d => .ok ⟨d, pre⟩

/-- Reads `logPrefix log hd.seq` only: the hash chain, the decision entry, then `admitDecision` with the prefix. -/
def snapshotOf (R : RiskDoc) (log : Log) (hd : DecisionRef) : Except String Snapshot :=
  snapshotCore R (logPrefix log hd.seq) hd

inductive Q1 | permitted (clear : Bool) | forbidden (rules : List Nat) | noClearAction | notReplayable (diagnostic : String)
  deriving DecidableEq, Repr

inductive Q2 | same | different (unused : List String) | notComparable (diagnostic : String)
  deriving DecidableEq, Repr

structure AuditQ12 where
  q1 : Q1
  q2 : Q2
  procedure : List String
  deriving DecidableEq, Repr

/-- The rules (1-based, in document order) on the `performed` permission that prohibit at `a` on the model:
guard true, every carve-out false. Rendering aid only (7.4). -/
def decidingRules (R : RiskDoc) (d : Decision) (a : String) : List Nat :=
  match R.alt.performed with
  | none => []
  | some (m, _) =>
    let M := decisionModel R d
    let x : VE.Bridge.Entity := (R.alt.action, a)
    let nodes := (VE.Alternatives.inlineTree (toAlt R)).T.nodes
    (List.range nodes.length).filterMap fun i => match nodes[i]? with
      | some N => if N.pred == m && !N.sign && N.guard.eval M [x] && N.carveOuts.all (fun c => !c.eval M [x])
          then some (i + 1) else none
      | none => none

/-- Q1 on an admitted record (4.10): no clear action at the decision (a dilemma or a conflict) comes first, then
forbidden, then permitted. -/
def q1Of (R : RiskDoc) (d : Decision) (a : String) : Q1 :=
  match validateDecision R d with
  | .error e => .notReplayable e
  | .ok () =>
    if (VE.Alternatives.scenarioConflict (toAlt R) (decisionModel R d)).isSome then .noClearAction
    else
      let st := statuses R d
      if st.all (fun p => !p.2.clear) then .noClearAction
      else match st.lookup a with
        | none => .notReplayable s!"UnknownSymbol: alternative {a}"
        | some s => if s.permitted then .permitted s.clear else .forbidden (decidingRules R d a)

/-- The live estimates of the record's quantities recorded before the decision (4.10 Q2). -/
def liveEstimates (sn : Snapshot) : Log :=
  sn.entries.filter fun x => x.kind == .estimate && decide (x.seq < sn.decision.seq) &&
    !withdrawnBefore sn.entries sn.decision.seq x.id &&
    match x.content.getObjValD "quantity" with
    | .str q => (sn.decision.quantities.map (·.name)).contains q
    | _ => false

def allEstimatesRecord (R : RiskDoc) (sn : Snapshot) : Except String Decision := do
  let items ← (liveEstimates sn).mapM (decodeItem R sn.decision.quantities)
  let issues := itemsIssues items
  pure { sn.decision with estimates := itemsEstimates items, issues := sn.decision.issues ++ issues }

def q2Of (R : RiskDoc) (sn : Snapshot) (a : String) (q1 : Q1) : Q2 × List String :=
  let unused := ((liveEstimates sn).filter (fun x => !sn.decision.cited.any (·.id == x.id))).map (·.id)
  let procedure := if R.risk.useAllRecorded then
      unused.map (fun id => s!"PROCEDURE BREACH: estimate {id} not used (the agent's fault)") else []
  match allEstimatesRecord R sn with
  | .error e => (.notComparable e, procedure)
  | .ok d' => match validateDecision R d' with
    | .error e => (.notComparable e, procedure)
    | .ok () => (if q1Of R d' a == q1 then .same else .different unused, procedure)

def auditCore (R : RiskDoc) (pre : Log) (hd : DecisionRef) (a : String) : AuditQ12 :=
  match snapshotCore R pre hd with
  | .error e => ⟨.notReplayable e, .notComparable e, []⟩
  | .ok sn =>
    let q1 := q1Of R sn.decision a
    let (q2, procedure) := q2Of R sn a q1
    ⟨q1, q2, procedure⟩

/-- Q1 and Q2 with the procedure lines, from the prefix up to the decision. -/
def auditQ12 (R : RiskDoc) (log : Log) (hd : DecisionRef) (a : String) : AuditQ12 :=
  auditCore R (logPrefix log hd.seq) hd a

/-- Q3 (no theorem, 7.4): per observed harm of the outcome entries naming the decision, whether the
decision-time cells of `a` allowed it. -/
def auditQ3 (R : RiskDoc) (log : Log) (hd : DecisionRef) (a : String) : List String :=
  match snapshotOf R log hd with
  | .error _ => []
  | .ok sn =>
    let d := sn.decision
    let t := regenerate R d
    let outcomes := log.filter fun x => x.kind == .outcome && x.content.getObjValD "decision" == .str hd.id
    outcomes.flatMap fun x =>
      let harmsSeen := match VE.Bridge.strings (x.content.getObjValD "harms") with
        | .ok hs => hs
        | .error _ => []
      harmsSeen.map fun h =>
        if t.might.contains (a, h) then s!"{h}: within the declared model"
        else if addressed d a h then s!"{h}: surprise: ruled out by {((condsOn d a h).map (·.id) ++ (stmtsOn d a h).map (·.id)).headD "a statement"}"
        else match R.risk.unexamined with
          | .ruledOutBy decider => s!"{h}: unexamined: ruled out by {decider}"
          | _ => s!"{h}: unexamined: ruled out by {d.chooserLabel}"

/-! ## Theorems (7.2) -/

theorem logPrefix_idem (log : Log) (k : Nat) : logPrefix (logPrefix log k) k = logPrefix log k := by
  simp [logPrefix, List.filter_filter]

/-- 4.10: the audit reads only the prefix up to the decision. -/
theorem snapshot_prefix (R : RiskDoc) (log : Log) (hd : DecisionRef) :
    snapshotOf R log hd = snapshotOf R (logPrefix log hd.seq) hd := by
  simp only [snapshotOf, logPrefix_idem]

/-- 4.10: Q1 and Q2 (and the procedure lines) never read outcomes: two logs that agree up to the decision's
sequence number give equal results for the same decision and the same queried alternative. -/
theorem verdict_ignores_outcomes (R : RiskDoc) (log₁ log₂ : Log) (hd : DecisionRef) (a : String)
    (hsame : logPrefix log₁ hd.seq = logPrefix log₂ hd.seq) :
    auditQ12 R log₁ hd a = auditQ12 R log₂ hd a := by
  simp only [auditQ12, hsame]

/-- 4.10: an admitted snapshot's decision is the record the decision entry carries, and every citation precedes
it and matches a prefix entry by id, sequence number and hash. -/
theorem snapshot_no_hindsight (R : RiskDoc) (log : Log) (hd : DecisionRef) (sn : Snapshot)
    (hs : snapshotOf R log hd = .ok sn) :
    sn.decision.seq = hd.seq ∧
    ∀ c ∈ sn.decision.cited, c.seq < hd.seq ∧ ∃ x ∈ sn.entries, x.id = c.id ∧ x.seq = c.seq ∧ x.hash = c.hash := by
  unfold snapshotOf snapshotCore at hs
  split at hs
  · cases hs
  split at hs
  · cases hs
  rename_i dx hdx
  split at hs
  · cases hs
  rename_i d hadm
  cases hs
  have hp := List.find?_some hdx
  simp only [Bool.and_eq_true, beq_iff_eq] at hp
  obtain ⟨hseq, _, hcited⟩ := admitDecision_sound R dx _ d hadm
  refine ⟨by rw [hseq, hp.1.2], fun c hc => ?_⟩
  obtain ⟨hlt, ⟨x, hx, h1, h2, h3, _⟩, _⟩ := hcited c hc
  exact ⟨by rw [← hp.1.2]; exact hlt, x, hx, h1, h2, h3⟩

end VE.Risk
