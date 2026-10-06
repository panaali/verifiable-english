import VE.Senses.Read
import VE.Senses.Decode
import VE.EnglishGrammar.ReadExamples

/-! The fixture dictionaries, environments and lexicons of docs/spec/senses.md section 8, and the
summaries the checks of `VE.Senses.Examples` compare by `==`. -/

namespace VE.Senses.Fixtures
open Lean VE.Grammar VE.EnglishGrammar VE.Senses

/-! ## Dictionaries -/

def srt (name letter : String) : PackSort := ⟨name, name, name ++ "s", "A " ++ name ++ ".", letter⟩

def sFunny1 : Sense := ⟨"funny", 1, "amusing", "causes laughter", ["joke"], "{0} is funny", none⟩
def sFunny2 : Sense := ⟨"funny", 2, "strange", "odd, hard to explain", ["joke"], "{0} is funny", none⟩
def sOdd1 : Sense := ⟨"odd", 1, "strange", "odd, hard to explain", ["joke"], "{0} is odd", none⟩
def sOdd2 : Sense := ⟨"odd", 2, "uneven", "not divisible by two", ["number"], "{0} is odd", none⟩
def sTells1 : Sense := ⟨"tells", 1, "says aloud", "says the joke to someone", ["person", "joke"], "{0} tells {1}", none⟩
def sDeployed1 : Sense := ⟨"deployed", 1, "live", "running in production", ["service"], "{0} is deployed", none⟩
def sReviewed1 : Sense := ⟨"reviewed", 1, "checked", "examined by a reviewer", ["service"], "{0} is reviewed", none⟩
def sReviewed2 : Sense := ⟨"reviewed", 2, "rated", "given a public rating", ["service"], "{0} is reviewed", none⟩
def sAccess1 : Sense := ⟨"access", 1, "read", "may read the resource", ["principal", "resource"],
  "{0} may access {1}", some "{0} may not access {1}"⟩

/-- The pack of spec 2.2 with the sorts `principal` (`R`) and `resource` (`Q`) of section 8. -/
def sortsF : List PackSort :=
  [srt "joke" "J", srt "service" "S", srt "person" "P", srt "number" "N", srt "principal" "R", srt "resource" "Q"]

def sensesF : List Sense :=
  [sFunny1, sFunny2, sOdd1, sOdd2, sTells1, sDeployed1, sReviewed1, sReviewed2, sAccess1]

def packF : Pack := ⟨"fixtures@1", sortsF, sensesF⟩
def F : Dictionary := ⟨[packF], []⟩

/-- `F` with its senses changed by `f` and its sorts replaced. -/
def Fwith (f : List Sense → List Sense) (sorts : List PackSort := sortsF) : Dictionary :=
  ⟨[{ packF with senses := f sensesF, sorts := sorts }], []⟩
def swap (old new : Sense) (l : List Sense) : List Sense := l.map fun s => if s == old then new else s

def sWeird : Sense := ⟨"weird", 1, "peculiar", "out of the ordinary", ["joke"], "{0} is funny weird", none⟩
/-- `Fn`: `near` 1 (`beside bob`, one person) and `near` 2 (`beside`, two persons). -/
def sNear1 : Sense := ⟨"near", 1, "beside bob", "is beside bob in particular", ["person"], "{0} is near bob", none⟩
def sNear2 : Sense := ⟨"near", 2, "beside", "is beside someone", ["person", "person"], "{0} is near {1}", none⟩
def Fn : Dictionary := Fwith fun l => l ++ [sNear1, sNear2]
/-- `Fd`, the counterexample of R1: `near` 1 (`beside`, `{0} is near bob`), `near` 2 (`beside bob`, `{0} is near`). -/
def sNearA : Sense := ⟨"near", 1, "beside", "is beside someone", ["person"], "{0} is near bob", none⟩
def sNearB : Sense := ⟨"near", 2, "beside bob", "is beside bob in particular", ["person"], "{0} is near", none⟩
def Fd : Dictionary := Fwith fun l => l ++ [sNearA, sNearB]
def sTells2 : Sense := ⟨"tells", 2, "reveals", "gives away the answer of the joke", ["person", "joke"], "{0} tells {1}", none⟩
def F2 : Dictionary := Fwith fun l => l ++ [sTells2]
def three (w : String) : List Sense := [("plain", 1), ("usual", 2), ("great", 3)].map fun (g, i) =>
  ⟨w, i, g ++ "ly " ++ w, "a sense of " ++ w, ["joke"], "{0} is " ++ w, none⟩
def F3 : Dictionary := Fwith fun l => l ++ three "warm" ++ three "cool" ++ three "mild"

/-! ## Environments and lexicons -/

def mkEnv (sorts : List String) (consts : List (String × String)) (displays : List (String × String) := [])
    (preds : List ReadExamples.PredSpec := []) : Env :=
  ReadExamples.env (ReadExamples.envJson false (sorts.map fun s => (s, none)) preds consts) displays

def EJ : Env := mkEnv ["joke", "person"] [("alice", "person"), ("riddle", "joke")] [("riddle", "the riddle")]
def LJ : Lexicon := {
  nouns := [("joke", "joke"), ("person", "person")], letters := [("joke", "J"), ("person", "P")],
  wordings := [], negatives := [], aliases := [],
  spellings := [("alice", "alice"), ("riddle", "the riddle")] }
def EJn : Env := mkEnv ["joke", "person"] [("alice", "person"), ("riddle", "joke"), ("bob", "person")]
  [("riddle", "the riddle")]
def LJn : Lexicon := { LJ with spellings := LJ.spellings ++ [("bob", "bob")] }
def EJs : Env := mkEnv ["joke", "person", "service"] [("alice", "person"), ("riddle", "joke"), ("legacy", "service")]
  [("riddle", "the riddle")]
def LJs : Lexicon := { LJ with
  nouns := LJ.nouns ++ [("service", "service")], letters := LJ.letters ++ [("service", "S")],
  spellings := LJ.spellings ++ [("legacy", "legacy")] }
def ES : Env := mkEnv ["service"] [("legacy", "service"), ("beta", "service"), ("gamma", "service")]
def LS : Lexicon := {
  nouns := [("service", "service")], letters := [("service", "S")], wordings := [], negatives := [],
  aliases := [], spellings := [("beta", "beta"), ("gamma", "gamma"), ("legacy", "legacy")] }
def EP : Env := mkEnv ["principal", "resource"] [("alice", "principal"), ("api", "resource")]
def LP : Lexicon := {
  nouns := [("principal", "principal"), ("resource", "resource")],
  letters := [("principal", "R"), ("resource", "Q")], wordings := [], negatives := [], aliases := [],
  spellings := [("alice", "alice"), ("api", "api")] }
/-- j6: `EJ` with an own predicate `funny` worded `{0} is funny`. -/
def EJ6 : Env := mkEnv ["joke", "person"] [("alice", "person"), ("riddle", "joke")] [("riddle", "the riddle")]
  [("funny", ["joke"], "{0} is funny", none)]
def LJ6 : Lexicon := { LJ with wordings := [("funny", "{0} is funny")] }
/-- j7: `EJ` with an own predicate `peculiar` worded `{0} is strange`. -/
def EJ7 : Env := mkEnv ["joke", "person"] [("alice", "person"), ("riddle", "joke")] [("riddle", "the riddle")]
  [("peculiar", ["joke"], "{0} is strange", none)]
def LJ7 : Lexicon := { LJ with wordings := [("peculiar", "{0} is strange")] }

/-! ## Texts -/

def J : String :=
  "In this document, funny means amusing.\nEvery joke that is funny (meaning strange) is not funny.\n" ++
  "Alice tells the riddle.\nThe riddle is funny (meaning strange).\nTherefore the riddle is not funny."
def Jbody : List String :=
  ["Every joke that is funny (meaning strange) is not funny.", "Alice tells the riddle.",
   "The riddle is funny (meaning strange).", "Therefore the riddle is not funny."]
def lineFunny : String := "In this document, funny means amusing."
def doc (ss : List String) : String := "\n".intercalate ss
def A1 : Assignment := ⟨[("funny", 1)]⟩

def sentsOf (s : String) : List (List Tok) :=
  match lex s with
  | .ok ss => ss.toList.map (·.toList)
  | .error _ => []

/-! ## Summaries -/

/-- A sentence outcome without its trees. -/
inductive O where
  | ok | none | many | rejected (r : Reject) | budget
  deriving DecidableEq, Repr

def O.of : Outcome Tok Reject EFormula → O
  | .ok _ _ => .ok
  | .noDerivation => .none
  | .ambiguous _ _ => .many
  | .rejected r => .rejected r
  | .budget => .budget

/-- `readWithSenses`'s outcome without trees and without the projection. -/
inductive Out where
  | ok (units : List SenseUnit) (senses : List SenseOccurrence) (mixed : List (String × List String))
       (unused : List String)
  | fault (f : SenseFault)
  | lexical (r : Reject)
  | invalid (g : GrammarFault)
  | stopped (i : Nat) (o : O)
  | illTyped
  deriving DecidableEq, Repr

def out : SensesOutcome → Out
  | .ok us sm mx un _ => .ok us sm mx un
  | .fault f => .fault f
  | .lexical r => .lexical r
  | .invalidGrammar g => .invalid g
  | .stopped i o => .stopped i (O.of o)
  | .illTyped => .illTyped

def rs (D : Dictionary) (E : Env) (L : Lexicon) (s : String) (b : Nat := workBudget) : Out :=
  out (readWithSenses D E L b s)

/-- The preamble's result, compared by `==`. -/
def pre (D : Dictionary) (s : String) (b : Nat := workBudget) : Except SenseFault (Assignment × Nat) :=
  readPreamble D b (sentsOf s)

def preIs (D : Dictionary) (s : String) (b : Nat) (want : Except SenseFault (Assignment × Nat)) : Bool :=
  match pre D s b, want with
  | .ok x, .ok y => x == y
  | .error f, .error g => f == g
  | _, _ => false

/-- A projection's fault, or none. -/
def projFault (P : Except SenseFault Projection) : Option SenseFault :=
  match P with
  | .ok _ => none
  | .error f => some f

/-- The number of derivations of each sentence of `s` under a grammar (cap 2); 99 past the budget. -/
def countsIn (G : Grammar Terminal) (s : String) : List Nat :=
  match lex s with
  | .ok sents => sents.toList.map fun w =>
      match parse G 2 workBudget w with
      | some ts => ts.length
      | none => 99
  | _ => [98]

/-- Formula shorthands. -/
def u (p : String) (x : String) : EFormula := .pred p [.const x]
def bin (p : String) (x y : String) : EFormula := .pred p [.const x, .const y]
def v0 : ETerm := .var 0
def st (rs : List String) (binder : Bool := false) : DState := ⟨rs, binder⟩
def res (A : EFormula) (after : DState) (m : Bool := false) : SenseUnit := ⟨some (A, m), [], [], after⟩
def occ (i a b : Nat) (p : String) (d : Bool) (c : Option Nat := none) : SenseOccurrence := ⟨i, a, b, p, d, c⟩

end VE.Senses.Fixtures
