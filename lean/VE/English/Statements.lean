import VE.English.Render
import VE.English.Parse

/-! # Statements of the English surface theorems (PLAN-EXPAND2 W7)

The three W7 theorems are stated once, for any surface presented as a renderer,
a parser, and a grammar whose derivations are data:

* `ParseRender S`: parsing the canonical rendering of an admitted meaning gives
  that meaning back;
* `RenderInjective S`: distinct admitted meanings render to distinct texts
  (synonymous input strings need not coincide: only the canonical renderer is
  injective);
* `UniqueDerivation S`: a text has at most one grammatical derivation, even when
  two derivations would denote the same AST;
* `ParseSound S`: whatever the parser returns is the reading of a derivation of
  exactly that text, so together with `UniqueDerivation` every accepted text has
  exactly one reading.

`Proofs.lean` proves all four for the core fragment (`coreSurface`). The same
statements for the full lexicon (contractions, validated negatives, closure,
order and later profiles) are deferred until W7's trigger (PLAN-EXPAND2
section 7: no wording change for two weeks after W1, W3, W5 and W6 merge). -/
namespace VE.English

structure Surface where
  Text : Type
  Meaning : Type
  Derivation : Type
  admitted : Meaning → Prop
  render : Meaning → Text
  parse : Text → Option Meaning
  derives : Derivation → Prop
  yield : Derivation → Text
  reading : Derivation → Option Meaning

def ParseRender (S : Surface) : Prop :=
  ∀ m, S.admitted m → S.parse (S.render m) = some m

def RenderInjective (S : Surface) : Prop :=
  ∀ m m', S.admitted m → S.admitted m' → S.render m = S.render m' → m = m'

def UniqueDerivation (S : Surface) : Prop :=
  ∀ d d', S.derives d → S.derives d' → S.yield d = S.yield d' → d = d'

def ParseSound (S : Surface) : Prop :=
  ∀ text m, S.parse text = some m → ∃ d, S.derives d ∧ S.yield d = text ∧ S.reading d = some m

/-- Injectivity of the canonical renderer follows from the round trip. -/
theorem renderInjective_of_parseRender {S : Surface} (h : ParseRender S) : RenderInjective S := by
  intro m m' hm hm' heq
  have h1 := h m hm
  rw [heq, h m' hm'] at h1
  exact (Option.some.inj h1).symm

/-- Admitted meanings: nonempty documents of closed well-typed formulas. -/
def Checked (E : Environment) (As : List Formula) : Prop :=
  As ≠ [] ∧ ∀ A ∈ As, A.check E [] = true

/-- The core fragment as a surface: token texts, document derivations. -/
def coreSurface (E : Environment) (L : Lexicon) : Surface where
  Text := List Tok
  Meaning := List Formula
  Derivation := List Tree
  admitted := Checked E
  render := render L
  parse := parse E L
  derives := fun ts => ∀ t ∈ ts, t.Syntactic L
  yield := docYield L
  reading := readTrees E

end VE.English
