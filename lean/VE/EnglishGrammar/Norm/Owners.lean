import VE.EnglishGrammar.Norm.Value
import VE.EnglishGrammar.Norm.Read
import VE.EnglishGrammar.Norm.Elab
import VE.Acts.Table
import VE.SoftNorms.Tree

/-! EN-2 step 0 (docs/spec/en-e3-norm.md 2.2): the owner pieces that the reader's values are bound to. A consequence's
op is act phrases' `VE.Acts.Op`, a clause's mode is soft-norms' `Mode`, a source spelling is an alias of the lexicon,
and a clause with an unformalised span never becomes a node (the span gate). -/

namespace VE.EnglishGrammar.Norm
open VE.EnglishGrammar

/-- The owner's op of a modal word (act phrases' `VE.Acts.Op`). -/
def Force.op : Force → VE.Acts.Op
  | .must => .must
  | .needNot => .needNot
  | .may => .may
  | .mustNot => .mustNot

/-- A consequence's op as act phrases fixes it (`VE.Acts.opOf`): a plain positive is `right`, a plain negative
has none. -/
def Polarity.op? : Polarity → Option VE.Acts.Op
  | .modal f => some f.op
  | .plain true => some .right
  | .plain false => none

theorem opOf_agrees : ∀ (r : VE.Norms.Regulated) (p : Polarity),
    p.fits r.role = true → VE.Acts.opOf r p.sign = p.op? := by
  intro r p h
  rcases r with ⟨n, ss, d, role, a, pm⟩
  cases role <;> rcases p with f | b <;> (try cases f) <;> (try cases b) <;>
    simp_all [Polarity.fits, VE.Acts.opOf, Polarity.sign, Force.sign, Polarity.op?, Force.op]

/-- soft-norms' mode of a clause (`VE.SoftNorms.Mode`); the decider is exception data, not the mode. -/
def Mode.soft : Mode → VE.SoftNorms.Mode
  | .strict => .strict
  | .default _ => .default

theorem soft_strict_iff : ∀ m : Mode, m.soft = .strict ↔ m = .strict := by
  intro m
  cases m <;> simp [Mode.soft]

/-- The source view: the use case's source spellings `A` as aliases, fixed in the environment's forms and
selected in the lexicon, so that V1-V5 (V4 included) check them with every other alias. -/
def sourceView (E : Env) (L : Lexicon) (A : List (String × String × Bool)) : Env × Lexicon :=
  ({ E with forms := { E.forms with aliases := E.forms.aliases ++ A } }, { L with aliases := L.aliases ++ A })

theorem sourceView_nil : ∀ (E : Env) (L : Lexicon), sourceView E L [] = (E, L) := by
  intro E L
  simp [sourceView]

/-- An unformalised span (NEW; not ve-limits' `Residual`): a clause's `Residual` as an answer names it. -/
structure UnformalisedSpan where
  start : Nat
  stop : Nat
  row : String
  owner : String
  place : Place
  deriving DecidableEq, Repr

def Residual.span (r : Residual) : UnformalisedSpan := ⟨r.start, r.stop, r.row, r.owner, r.place⟩

def unformalisedText (k : Nat) : String :=
  s!"The text has {k} phrase(s) that the reader parsed and did not formalise. No rule is made from a sentence " ++
  "with such a phrase."

/-- The span gate: a clause with a span never becomes a node. -/
def Clause.toNodeChecked (name : String) (over : List String) (c : Clause) : Except String VE.Norms.Node :=
  if c.residuals.isEmpty then c.toNode name over else .error (unformalisedText c.residuals.length)

def spansOf (rs : List NormStatement) : List UnformalisedSpan :=
  (rs.flatMap NormStatement.clauses).flatMap fun c => c.residuals.map Residual.span

def toNodesChecked (rs : List NormStatement) : Except String (List VE.Norms.Node) :=
  if (spansOf rs).isEmpty then toNodes rs else .error (unformalisedText (spansOf rs).length)

theorem toNodeChecked_ok : ∀ (n : String) (o : List String) (c : Clause) (nd : VE.Norms.Node),
    c.toNodeChecked n o = .ok nd ↔ c.residuals = [] ∧ c.toNode n o = .ok nd := by
  intro n o c nd
  unfold Clause.toNodeChecked
  cases h : c.residuals <;> simp

theorem toNodesChecked_ok : ∀ (rs : List NormStatement) (nds : List VE.Norms.Node),
    toNodesChecked rs = .ok nds ↔ spansOf rs = [] ∧ toNodes rs = .ok nds := by
  intro rs nds
  unfold toNodesChecked
  cases h : spansOf rs <;> simp

/-- en-s6b's `readNorm_authoring` (english-lean-s6.md 4), which main states as `#guard`s over its fixtures (en-s6b
REPORT): a premise of `toNodesChecked_authoring`, not an assumption of the product. -/
def ReadNormAuthoring : Prop := ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String)
    (rs : List NormStatement),
  readNorm E O L b s = .ok rs →
  (∀ r ∈ rs, ∀ cs, r ≠ .source cs) ∧
  ∀ c ∈ rs.flatMap NormStatement.clauses,
    c.mode = .strict ∧ c.residuals = [] ∧ c.args = [] ∧
    ∃ r ∈ regulatedOf E, r.name = c.pred ∧ ∃ s1 rest, r.sorts = s1 :: rest ∧ c.bearer = .every s1

/-- `ReadNormAuthoring` against english-lean-s6.md 4's `readNorm_authoring`, copied here as it reads there: an edit of
the definition breaks this (the copy is checked against the spec by review, not by a tool). -/
theorem ReadNormAuthoring_eq : ReadNormAuthoring ↔ ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String)
    (rs : List NormStatement),
  readNorm E O L b s = .ok rs →
  (∀ r ∈ rs, ∀ cs, r ≠ .source cs) ∧
  ∀ c ∈ rs.flatMap NormStatement.clauses,
    c.mode = .strict ∧ c.residuals = [] ∧ c.args = [] ∧
    ∃ r ∈ regulatedOf E, r.name = c.pred ∧ ∃ s1 rest, r.sorts = s1 :: rest ∧ c.bearer = .every s1 := Iff.rfl

/-- From en-s6b's `readNorm_authoring` (stated in the stub as `ReadNormAuthoring`). -/
theorem toNodesChecked_authoring : ReadNormAuthoring →
    ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) (rs : List NormStatement),
      readNorm E O L b s = .ok rs → toNodesChecked rs = toNodes rs := by
  intro ha E O L b s rs h
  have hs : spansOf rs = [] := by
    simp only [spansOf, List.flatMap_eq_nil_iff, List.map_eq_nil_iff]
    intro c hc
    exact ((ha E O L b s rs h).2 c hc).2.1
  simp [toNodesChecked, hs]

end VE.EnglishGrammar.Norm
