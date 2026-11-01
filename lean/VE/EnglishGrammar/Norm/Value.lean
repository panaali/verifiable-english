import VE.EnglishGrammar.Syntax

/-! The values of an authored W1 rule block and their assembly (docs/spec/english-lean-s6.md 2.2 to 2.4).

A block text is read one sentence at a time; each sentence has one `Piece`. `assemble` groups the pieces into
statements: a header opens a block, its clause sentence follows, and its except-when sentences append carve-outs.
Blocks are numbered 1, 2, … in order, and every rule a header or a precedence line names must exist (R1).
-/

namespace VE.EnglishGrammar.Norm
open VE.EnglishGrammar

/-- The four W1 modal words (`VE.Acts.Op` without `right`). -/
inductive Force where
  | must | needNot | may | mustNot
  deriving DecidableEq, Repr

/-- W1's stored sign: obligation `must` true, `need not` false; permission `may` true, `must not` false
(`ve/norm_english.py:97-100`). -/
def Force.sign : Force → Bool
  | .must => true
  | .needNot => false
  | .may => true
  | .mustNot => false

/-- R2: a consequence's force, either a modal word or a plain wording with its sign. -/
inductive Polarity where
  | modal (f : Force)
  | plain (positive : Bool)
  deriving DecidableEq, Repr

def Polarity.sign : Polarity → Bool
  | .modal f => f.sign
  | .plain b => b

/-- `strict` is W1; `default d` is a soft-norms default rule (EN-4; never produced here). -/
inductive Mode where
  | strict
  | default (decider : String)
  deriving DecidableEq, Repr

/-- Whom a clause binds, as read (en-e3-norm D8). Authoring produces only `every`. -/
inductive Bearer where
  | every (sort : String)
  | named (const : String)
  | author
  | unstated
  deriving DecidableEq, Repr

inductive Place where
  | act | guard | carveOut | bearer
  deriving DecidableEq, Repr

/-- A phrase parsed and not formalised (en-e3-norm D5, EN-7). Always empty in authoring. -/
structure Residual where
  start : Nat
  stop : Nat
  row : String
  owner : String
  place : Place
  deriving DecidableEq, Repr

/-- One reading of one norm clause. In authoring `args = []`: W1 binds every slot of the predicate by
"Every"/"each", and the W1 wire has no argument field (`normFields`, `Norms/Wire.lean:319`). -/
structure Clause where
  bearer : Bearer
  force : Polarity
  mode : Mode
  pred : String
  args : List ETerm
  guard : EFormula
  carveOuts : List EFormula
  residuals : List Residual
  deriving DecidableEq, Repr

structure Header where
  number : Nat
  exceptionTo : List Nat
  deriving DecidableEq, Repr

inductive NormStatement where
  | rule (h : Header) (c : Clause)
  | precedence (n m : Nat)
  | source (cs : List Clause)        -- translation mode (EN-5); never produced here
  deriving DecidableEq, Repr

def NormStatement.clauses : NormStatement → List Clause
  | .rule _ c => [c] | .precedence _ _ => [] | .source cs => cs

def NormStatement.number? : NormStatement → Option Nat
  | .rule h _ => some h.number | _ => none

/-- The rule numbers a statement names: a header's exception targets, both sides of a precedence line. -/
def NormStatement.refs : NormStatement → List Nat
  | .rule h _ => h.exceptionTo | .precedence n m => [n, m] | .source _ => []

def ruleCount (rs : List NormStatement) : Nat := (rs.filterMap NormStatement.number?).length

/-- The value of one sentence of a block text. -/
inductive Piece where
  | header (h : Header)
  | clause (c : Clause)
  | exceptWhen (φ : EFormula)
  | precedence (n m : Nat)
  deriving DecidableEq, Repr

/-- The bindings of the current block's consequence (a `Scope`), or none. -/
structure NState where
  scope : Option (List (String × String))
  deriving DecidableEq, Repr

def NState.init : NState := ⟨none⟩

inductive BlockFault where
  | expectedRule (index number : Nat)   -- sentence `index` opens a block not numbered `number`
  | noConsequence (index : Nat)         -- the header at `index` has no clause sentence
  | strayConsequence (index : Nat)      -- a clause sentence outside a block, or a second one in a block
  | strayCarveOut (index : Nat)         -- an except-when sentence before its block's clause
  | unknownRule (number : Nat)          -- a reference outside 1 … number of blocks
  deriving DecidableEq, Repr

/-- An open block: its header's sentence index, its header, and its clause once read. -/
abbrev Open := Option (Nat × Header × Option Clause)

/-- The statement of a closed block, or `noConsequence` when its clause is missing. -/
def close : Open → Except BlockFault (List NormStatement)
  | none => .ok []
  | some (_, h, some c) => .ok [.rule h c]
  | some (i, _, none) => .error (.noConsequence i)

/-- The pieces from sentence `i` on, with `k` blocks opened before and the open block `o`. -/
def assembleFrom : Nat → Nat → Open → List Piece → Except BlockFault (List NormStatement)
  | _, _, o, [] => close o
  | i, k, o, .header h :: ps => do
    let a ← close o
    if h.number ≠ k + 1 then throw (.expectedRule i (k + 1))
    return a ++ (← assembleFrom (i + 1) (k + 1) (some (i, h, none)) ps)
  | i, k, some (j, h, none), .clause c :: ps => assembleFrom (i + 1) k (some (j, h, some c)) ps
  | i, _, _, .clause _ :: _ => throw (.strayConsequence i)
  | i, k, some (j, h, some c), .exceptWhen φ :: ps =>
    assembleFrom (i + 1) k (some (j, h, some { c with carveOuts := c.carveOuts ++ [φ] })) ps
  | i, _, _, .exceptWhen _ :: _ => throw (.strayCarveOut i)
  | i, k, o, .precedence n m :: ps => do
    let a ← close o
    return a ++ .precedence n m :: (← assembleFrom (i + 1) k none ps)

/-- The statements of a block text's pieces (spec 2.4), or the first fault: the blocks' faults in text order,
then the first reference outside `1 … ruleCount`. -/
def assemble (ps : List Piece) : Except BlockFault (List NormStatement) := do
  let rs ← assembleFrom 0 0 none ps
  match (rs.flatMap NormStatement.refs).find? (fun n => n < 1 || ruleCount rs < n) with
  | some n => throw (.unknownRule n)
  | none => return rs

/-! ## Numbering -/

/-- A closed block is numbered as it was opened. -/
theorem close_numbered {o : Open} {k : Nat} {a : List NormStatement} (ho : ∀ j h c, o = some (j, h, c) → h.number = k)
    (h : close o = .ok a) : a.filterMap NormStatement.number? = if o.isSome then [k] else [] := by
  match o, h with
  | none, h => cases h; rfl
  | some (_, hd, some c), h => cases h; simp [NormStatement.number?, ho _ hd (some c) rfl]
  | some (_, _, none), h => cases h

/-- The rule numbers assembled from an open block numbered `k` (or none, after `k` blocks) run on from it. -/
theorem assembleFrom_numbered : ∀ (ps : List Piece) (i k : Nat) (o : Open) (rs : List NormStatement),
    (∀ j h c, o = some (j, h, c) → h.number = k) → assembleFrom i k o ps = .ok rs →
    rs.filterMap NormStatement.number? =
      List.range' (if o.isSome then k else k + 1) (rs.filterMap NormStatement.number?).length := by
  intro ps
  induction ps with
  | nil =>
    intro i k o rs ho h
    simp only [assembleFrom] at h
    rw [close_numbered ho h]
    cases o <;> simp
  | cons p ps ih =>
    intro i k o rs ho h
    cases p with
    | header hd =>
      simp only [assembleFrom, bind, Except.bind] at h
      split at h
      · cases h
      · rename_i a ha
        split at h
        · cases h
        · rename_i hn
          simp only [pure, Except.pure] at h
          split at h
          · cases h
          · rename_i rest hr
            cases h
            have h1 := close_numbered ho ha
            have h2 := ih _ _ _ _ (fun j h c e => by cases e; simpa using hn) hr
            simp only [Option.isSome_some, if_true] at h2
            rw [List.filterMap_append, h1, h2]
            cases o <;> simp [List.range'_succ]
    | clause c =>
      rcases o with _ | ⟨j, hd, _ | c2⟩ <;> simp only [assembleFrom] at h <;> try cases h
      have := ih _ _ _ _ (fun j2 h2 c3 e => by cases e; exact ho _ _ _ rfl) h
      simpa using this
    | exceptWhen φ =>
      rcases o with _ | ⟨j, hd, _ | c2⟩ <;> simp only [assembleFrom] at h <;> try cases h
      have := ih _ _ _ _ (fun j2 h2 c3 e => by cases e; exact ho _ _ _ rfl) h
      simpa using this
    | precedence n m =>
      simp only [assembleFrom, bind, Except.bind] at h
      split at h
      · cases h
      · rename_i a ha
        simp only [pure, Except.pure] at h
        split at h
        · cases h
        · rename_i rest hr
          cases h
          have h1 := close_numbered ho ha
          have h2 := ih _ _ _ _ (fun j h c e => by cases e) hr
          simp only [Option.isSome_none] at h2
          simp only [List.filterMap_append, List.filterMap_cons, NormStatement.number?, h1]
          rw [h2]
          cases o <;> simp [List.range'_succ]

/-- `readNorm_numbered`'s conclusion for every assembled list (spec 3.2). -/
theorem assemble_numbered : ∀ (ps : List Piece) (rs : List NormStatement), assemble ps = .ok rs →
    rs.filterMap NormStatement.number? = List.range' 1 (ruleCount rs) ∧
    ∀ n ∈ rs.flatMap NormStatement.refs, 1 ≤ n ∧ n ≤ ruleCount rs := by
  intro ps rs h
  simp only [assemble, bind, Except.bind] at h
  split at h
  · cases h
  · rename_i rs2 hr
    split at h
    · cases h
    · rename_i hf
      cases h
      refine ⟨assembleFrom_numbered ps 0 0 none rs (fun _ _ _ e => by cases e) hr, fun n hn => ?_⟩
      have := List.find?_eq_none.mp hf n hn
      simp only [Bool.or_eq_true, decide_eq_true_eq, not_or, Nat.not_lt] at this
      omega

end VE.EnglishGrammar.Norm
