import VE.Acts.Specialise
import VE.Acts.MeaningExamples

/-! Fixtures of `specialises` and `specPremises` (docs/spec/act-phrases.md 8, 11.5; plan AP-5).

Spec 11.5's: `a` = "seek asylum in [other countries]" ⊑ `b` = "seek asylum" when *in* is declared restrictive, not
when nothing is declared, and never `b` ⊑ `a`; `specPremises` gives one premise `∀ x. pa x → pb x` on two permission
predicates and on two obligation predicates, none on two plain ones. The acts are built by `analyse`, as spec 8's last
paragraph says (one, `b` read with *be*, is `b` with that field changed). The other guards are where the plan's seeded
bugs and the mutants of docs/act-phrases/ap-5/mutants.json fail: an undeclared adverb, a different head, *to* or *be*,
arguments and modifiers beyond `b` with only some restrictive, an argument or modifier of `b` that `a` lacks, each with
the one that matters first and last in its list, `a = b`, unequal sorts, two roles, and a name declared twice or not at
all.
-/

namespace VE.Acts.SpecialiseExamples
open VE.Acts VE.Acts.MeaningExamples VE.Acts.Examples VE.Acts.RuleExamples
open VE.Norms (Doc Regulated Role)

/-- *seek* and *request* with an object, *seek* also with *from* and *against*; *in* and *for* modify; two adverbs. -/
def Vsp : Vocab :=
  ⟨[fr "seek" ["", "from", "against"] [] ["in", "for"], fr "request" [""] [] ["in"]], ["nearly", "freely"]⟩
def act (fx : List String) (s : String) : Atom :=
  (analyse Vsp rawCap stepBudget (toks fx s)).getD ⟨false, false, [], [], []⟩

def a := act ["other countries"] "{0} to seek asylum in other countries"
def b := act [] "{0} to seek asylum"
def nearly := act [] "{0} to nearly seek asylum"
def request := act [] "{0} to request asylum"
def fromP := act [] "{0} to seek asylum from persecution"
def noTo := act [] "{0} seek asylum"
def nearIn := act ["other countries"] "{0} to nearly seek asylum in other countries"
def inNear := act ["other countries"] "{0} to seek asylum in other countries nearly"
def nearInFor := act ["other countries"] "{0} to nearly seek asylum in other countries for safety"
def refugeFrom := act [] "{0} to seek refuge from persecution"
def fromAgainst := act [] "{0} to seek asylum from persecution against expulsion"
/-- *seek from persecution* with no object, which `Vsp` does not read: built by hand. -/
def fromOnly : Atom := ⟨true, false, ["seek"], [("from", .one (.words ["persecution"]))], []⟩

-- each act is `analyse`'s simple act, as written
#guard a == ⟨true, false, ["seek"], [("", .one (.words ["asylum"]))], [.prep "in" (.fixed 0)]⟩
#guard b == ⟨true, false, ["seek"], [("", .one (.words ["asylum"]))], []⟩
#guard nearly == ⟨true, false, ["seek"], [("", .one (.words ["asylum"]))], [.adv "nearly"]⟩
#guard request.head == ["request"] && fromP.args.length == 2 && noTo == { b with toWord := false }
#guard [nearIn.mods, inNear.mods, nearInFor.mods] == [[.adv "nearly", .prep "in" (.fixed 0)],
  [.prep "in" (.fixed 0), .adv "nearly"], [.adv "nearly", .prep "in" (.fixed 0), .prep "for" (.words ["safety"])]] &&
  refugeFrom.args.map (·.1) == ["", "from"] && fromAgainst.args.map (·.1) == ["", "from", "against"]

/-! ### `specialises` (11.5, then one guard per seeded bug and mutant) -/

#guard specialises ⟨["in"], []⟩ a b = true
#guard specialises ⟨[], []⟩ a b = false              -- nothing declared, so nothing narrows
#guard specialises ⟨["in"], []⟩ b a = false          -- `b` has no *in*
#guard specialises ⟨[], ["in"]⟩ a b = false          -- *in* declared as an adverb is not a marker
#guard specialises ⟨["in"], []⟩ nearly b = false     -- an undeclared adverb never narrows
#guard specialises ⟨[], ["nearly"]⟩ nearly b = true && specialises ⟨["nearly"], []⟩ nearly b = false
#guard specialises ⟨["in"], []⟩ request b = false && specialises ⟨["in"], []⟩ b request = false   -- another head
#guard specialises ⟨["in"], []⟩ noTo b = false && specialises ⟨["in"], []⟩ b noTo = false         -- *to*
#guard specialises ⟨["in"], []⟩ { b with beWord := true } b = false                              -- *be*
#guard specialises ⟨["from"], []⟩ fromP b = true && specialises ⟨["in"], []⟩ fromP b = false   -- an argument beyond `b`
#guard specialises ⟨["from"], []⟩ b fromP = false                                              -- an argument `a` lacks
#guard specialises ⟨["in"], []⟩ b b = true && specialises ⟨[], []⟩ a a = true                  -- `specialises_refl`

-- two extra modifiers, each order: both must be restrictive, and a declaration counts wherever it is in its list
#guard [nearIn, inNear].all fun x => !specialises ⟨["in"], []⟩ x b && !specialises ⟨[], ["nearly"]⟩ x b &&
  specialises ⟨["in"], ["nearly"]⟩ x b && specialises ⟨["for", "in"], ["freely", "nearly"]⟩ x b &&
  specialises ⟨["in", "for"], ["nearly", "freely"]⟩ x b
-- `b` with two modifiers, `a` with one of them: never; `a` with both and one more: only that one need be restrictive
#guard [nearIn, inNear].all fun x => !specialises ⟨["in"], ["nearly"]⟩ a x && specialises ⟨[], ["nearly"]⟩ x a &&
  specialises ⟨["for"], []⟩ nearInFor x && !specialises ⟨["in"], ["nearly"]⟩ nearInFor x
-- two extra arguments: both must be restrictive, in either order of declaration
#guard !specialises ⟨["from"], []⟩ fromAgainst b && !specialises ⟨["against"], []⟩ fromAgainst b &&
  specialises ⟨["from", "against"], []⟩ fromAgainst b && specialises ⟨["against", "from"], []⟩ fromAgainst b &&
  specialises ⟨["against"], []⟩ fromAgainst fromP
-- `b` with two arguments, `a` with only the last: never, even with `a`'s object declared restrictive
#guard !specialises ⟨["", "from"], []⟩ refugeFrom fromP && specialises ⟨[""], []⟩ refugeFrom fromOnly
-- `a`'s first argument extra and not restrictive: never
#guard !specialises ⟨["from"], []⟩ refugeFrom fromOnly

/-! ### `specPremises` -/

def reg (n : String) (role : Role) (sorts : List String := ["person"]) : Regulated :=
  ⟨n, sorts, true, role, if role == .plain then none else some n, none⟩
def env : VE.Environment :=
  ⟨["person", "country"], fun p => if p.startsWith "q" then some ["person", "country"] else
    if p.startsWith "p" then some ["person"] else if p.startsWith "c" then some ["country"] else none, fun _ => none⟩
def doc (rs : List Regulated) : Doc := ⟨env, [], ⟨rs, [], []⟩⟩
def ρ : Restrictive := ⟨["in"], []⟩
def prem (ra rb : String) : VE.Formula := .all "person" (.implies (.unary ra (.var 0)) (.unary rb (.var 0)))
def sp (rs : List Regulated) (acts : List (String × Atom)) : List VE.Formula := specPremises (doc rs) ρ acts

-- two permissions, two obligations: exactly one premise, from the specific act to the general one
#guard sp [reg "pa" .permission, reg "pb" .permission] [("pa", a), ("pb", b)] == [prem "pa" "pb"]
#guard sp [reg "pa" .permission, reg "pb" .permission] [("pb", b), ("pa", a)] == [prem "pa" "pb"]
#guard sp [reg "pa" .obligation, reg "pb" .obligation] [("pa", a), ("pb", b)] == [prem "pa" "pb"]
-- three acts, each pair in `acts` order: every premise, none dropped
#guard specPremises (doc [reg "pa" .permission, reg "pb" .permission, reg "pc" .permission]) ⟨["in"], ["nearly"]⟩
    [("pa", a), ("pb", b), ("pc", nearIn)] == [prem "pa" "pb", prem "pc" "pa", prem "pc" "pb"]
-- two plain entitlements: none
#guard sp [reg "pa" .plain, reg "pb" .plain] [("pa", a), ("pb", b)] == []
-- one permission and one obligation: none
#guard sp [reg "pa" .permission, reg "pb" .obligation] [("pa", a), ("pb", b)] == []
-- `a = b`: none (two predicates, one act)
#guard sp [reg "pa" .permission, reg "pb" .permission] [("pa", b), ("pb", b)] == []
-- unequal sorts: none
#guard sp [reg "pa" .permission, reg "qb" .permission ["person", "country"]] [("pa", a), ("qb", b)] == []
#guard sp [reg "pa" .permission, reg "cb" .permission ["country"]] [("pa", a), ("cb", b)] == []
-- nothing narrows: none
#guard specPremises (doc [reg "pa" .permission, reg "pb" .permission]) ⟨[], []⟩ [("pa", a), ("pb", b)] == []
-- a name declared twice or not at all: none
#guard sp [reg "pa" .permission, reg "pa" .plain, reg "pb" .permission] [("pa", a), ("pb", b)] == []
#guard sp [reg "pa" .plain, reg "pa" .permission, reg "pb" .permission] [("pa", a), ("pb", b)] == []
#guard sp [reg "pb" .permission] [("pa", a), ("pb", b)] == []
-- two sorts: both bound, in declared order, and the premise is typed in the document's environment
#guard sp [reg "qa" .permission ["person", "country"], reg "qb" .permission ["person", "country"]]
    [("qa", a), ("qb", b)] == [.all "person" (.all "country"
      (.implies (.binary "qa" (.var 1) (.var 0)) (.binary "qb" (.var 1) (.var 0))))]
#guard (sp [reg "qa" .permission ["person", "country"], reg "qb" .permission ["person", "country"]]
    [("qa", a), ("qb", b)]).all (·.check env [])
#guard VE.Norms.WellFormed (doc [reg "pa" .permission, reg "pb" .permission])

end VE.Acts.SpecialiseExamples
