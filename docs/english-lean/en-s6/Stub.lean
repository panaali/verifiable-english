import VE.EnglishGrammar.Read
import VE.EnglishGrammar.Norm.Value
import VE.Norms.Wire
import VE.Grammar.Extension

/-! EN-0's stub (en-e3-norm-PLAN EN-0; DRI decision 20261031-spec-el-s6 item 3): the Lean blocks of
docs/spec/english-lean-s6.md 2.5 to 2.7 with placeholder bodies, and the eleven statements of section 4 word for word,
each as a `Prop`, elaborated under main's Lean 4.24.0 against main and en-s6's `Norm/Value.lean` (2.2 to 2.4, built):
`cd lean && lake env lean ../docs/english-lean/en-s6/Stub.lean` exits 0. Placeholders: `Ty.norm` (en-s6b adds the
constructor to `Syntax.lean`), and the bodies of `normGrammar`, `normActs`, `normTy`, `normMeaning` and `readNorm`.
The 2.7 definitions are Elab.lean's at 37c5fcb2f, which proved `toNode_fields`. Not built by `lake build`. -/
namespace VE.EnglishGrammar
/-- Stub only: stands for the `Ty` constructor `norm` that en-s6b adds to `Syntax.lean`. -/
def Ty.norm : Ty := .tok
end VE.EnglishGrammar

namespace VE.EnglishGrammar.Norm
open Lean VE.EnglishGrammar

def Polarity.fits : Polarity → VE.Norms.Role → Bool
  | .modal .must, .obligation => true
  | .modal .needNot, .obligation => true
  | .modal .may, .permission => true
  | .modal .mustNot, .permission => true
  | .plain _, .plain => true
  | _, _ => false

def regulatedOf (E : Env) : List VE.Norms.Regulated :=
  match VE.Norms.Wire.decodeNormsEnvironment E.source (acts := true) with
  | .ok ne => ne.regulated
  | .error _ => []

def normGrammar (E : Env) (L : Lexicon) : VE.Grammar.Grammar Terminal := grammar E L
def normActs (E : Env) (L : Lexicon) : Array (VE.Grammar.Action sig) := acts E L
def normTy (E : Env) (L : Lexicon) : Nat → Ty := ty E L
def prefixMap : VE.Grammar.RuleMap := ⟨id, id⟩
def normMeaning (G : VE.Grammar.Grammar Terminal) (acts : Array (VE.Grammar.Action sig)) :
    VE.Grammar.Meaning Tok NState Reject Piece := fun _ _ => .error .internal

inductive NormOutcome where
  | ok (rs : List NormStatement)
  | invalidGrammar (why : GrammarFault)
  | lexical (r : Reject)
  | stopped (index : Nat) (o : VE.Grammar.Outcome Tok Reject Piece)
  | misplaced (f : BlockFault)

def readNorm (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) : NormOutcome := .misplaced (.unknownRule 0)

def NormOneReading (E : Env) (O : Overlay) (L : Lexicon) (s : String) (rs : List NormStatement) : Prop :=
  L.valid E O = true ∧
  ∃ sents ps st2, lex s = .ok sents ∧
    VE.Grammar.DocOneReading (normGrammar E L) (normMeaning (normGrammar E L) (normActs E L)) NState.init
      (sents.toList.map (·.toList)) (ps.map (·, false)) st2 ∧
    assemble ps = .ok rs
def ruleName (i : Nat) : String := "rule-" ++ toString i

/-- `{"norm": {"name", "predicate", "sign", "guard", "unless", "over"}}`: `predicate` is `c.pred`, `sign`
is `c.force.sign`, `guard` is `c.guard.encode`, `unless` is `c.carveOuts.map EFormula.encode`. -/
def Clause.wire (name : String) (over : List String) (c : Clause) : Lean.Json :=
  Json.mkObj [("norm", Json.mkObj [("name", .str name), ("predicate", .str c.pred), ("sign", .bool c.force.sign),
    ("guard", c.guard.encode), ("unless", .arr (c.carveOuts.map EFormula.encode).toArray),
    ("over", .arr (over.map Json.str).toArray)])]

def Clause.toNode (name : String) (over : List String) (c : Clause) : Except String VE.Norms.Node :=
  VE.Norms.Wire.decodeNorm (c.wire name over)

/-- Rule `n`'s `over`: its header's targets, then the `m` of every `.precedence n m`, in text order
(`norm_english.py:290`, :323). -/
def overOf (rs : List NormStatement) (n : Nat) : List Nat :=
  (rs.filterMap fun | .rule h _ => if h.number = n then some h.exceptionTo else none | _ => none).flatten ++
  rs.filterMap fun | .precedence n2 m => if n2 = n then some m else none | _ => none

/-- The nodes of the rules in order; rule `i` is named `ruleName i` (Python without a manifest, :307). -/
def toNodes (rs : List NormStatement) : Except String (List VE.Norms.Node) :=
  (rs.filterMap fun | .rule h c => some (h, c) | _ => none).mapM fun (h, c) =>
    c.toNode (ruleName h.number) ((overOf rs h.number).map ruleName)

-- Section 4's statements, word for word, each as a Prop.
def S_prefixMap_ok : Prop :=
  ∀ (E : Env) (L : Lexicon),
  prefixMap.Ok (grammar E L) { normGrammar E L with start := (grammar E L).start } (acts E L) (normActs E L)

def S_condition_same : Prop :=
  ∀ (E : Env) (L : Lexicon) (X : VE.Grammar.Sym Terminal) (t : VE.Grammar.Tree Tok),
  t.derives (grammar E L) X = true →
  t.derives (normGrammar E L) X = true ∧ t.sem (normGrammar E L) sig (normActs E L) = t.sem (grammar E L) sig (acts E L)

def S_start_norm : Prop :=
  ∀ (E : Env) (L : Lexicon), normTy E L (normGrammar E L).start = .norm

def S_normMeaning_unmarked : Prop :=
  ∀ (E : Env) (L : Lexicon) (st st2 : NState) (t : VE.Grammar.Tree Tok) (p : Piece)
    (c : Bool),
  normMeaning (normGrammar E L) (normActs E L) st t = .ok (p, c, st2) → c = false

def S_readNorm_sound : Prop :=
  ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) (rs : List NormStatement),
  readNorm E O L b s = .ok rs → NormOneReading E O L s rs

def S_readNorm_complete : Prop :=
  ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String)
    (rs : List NormStatement),
  NormOneReading E O L s rs →
  (normGrammar E L).wf = true → terminatorFree (normGrammar E L) = true →
  (normGrammar E L).typed sig (normTy E L) (normActs E L) = true → normTy E L (normGrammar E L).start = .norm →
  readNorm E O L b s = .ok rs ∨ ∃ i, readNorm E O L b s = .stopped i .budget

def S_readNorm_unique : Prop :=
  ∀ (E : Env) (O : Overlay) (L : Lexicon) (s : String) (rs rs2 : List NormStatement),
  NormOneReading E O L s rs → NormOneReading E O L s rs2 → rs2 = rs

def S_readNorm_numbered : Prop :=
  ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String)
    (rs : List NormStatement),
  readNorm E O L b s = .ok rs →
  rs.filterMap NormStatement.number? = List.range' 1 (ruleCount rs) ∧
  ∀ n ∈ rs.flatMap NormStatement.refs, 1 ≤ n ∧ n ≤ ruleCount rs

def S_readNorm_authoring : Prop :=
  ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String)
    (rs : List NormStatement),
  readNorm E O L b s = .ok rs →
  (∀ r ∈ rs, ∀ cs, r ≠ .source cs) ∧
  ∀ c ∈ rs.flatMap NormStatement.clauses,
    c.mode = .strict ∧ c.residuals = [] ∧ c.args = [] ∧
    ∃ r ∈ regulatedOf E, r.name = c.pred ∧ ∃ s1 rest, r.sorts = s1 :: rest ∧ c.bearer = .every s1

def S_readNorm_regulated : Prop :=
  ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String)
    (rs : List NormStatement),
  readNorm E O L b s = .ok rs →
  ∀ c ∈ rs.flatMap NormStatement.clauses, ∃ r ∈ regulatedOf E, r.name = c.pred ∧ c.force.fits r.role = true

def S_toNode_fields : Prop :=
  ∀ (n : String) (o : List String) (c : Clause) (nd : VE.Norms.Node),
  c.toNode n o = .ok nd →
  nd.name = n ∧ nd.pred = c.pred ∧ nd.sign = c.force.sign ∧ nd.over = o ∧ nd.carveOuts.length = c.carveOuts.length

end VE.EnglishGrammar.Norm
