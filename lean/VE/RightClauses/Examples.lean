import VE.RightClauses.Relation
import VE.RightClauses.ElidedBytes
import VE.Rights.Examples

/-! The section 9.1 fixtures this part decides (docs/spec/right-clauses.md 9.1), as `#guard`s: the build fails if
one is false. Environment: `VE.Rights.Examples`' (one state `Texas`, persons `Ann`, `Bob`) with the base predicates
`country_of(state, person)` and `charged(person)`; right `r21`, holder `person`, guard `⊤`, one claim line
`equal-access` on `public_service_access_required(state, person)`, obligation `+`, guard `⊤`; unit span `[0, 100)`.

K9 and K15 (`elided` missing) and K10 (profile off) are the wire decoder's (Wire.lean, cmp-s3b); K3's premise and K13's
slot are Relation.lean's (the last section). Each check has fixtures on its accepting and its refusing side, at and around each span boundary. -/
namespace VE.RightClauses.Examples
open VE.Rights (RightsDoc SourceLine Right)
open VE.Rights.Examples (mkRights block strictNode line diag selectsAt model epsilon fanLine fanMap tortureRegs l29)

def accessLine (guard : VE.Formula := .top) : SourceLine :=
  line .claim (strictNode "equal-access" "public_service_access_required" true guard)

def r21 (guard : VE.Formula := .top) (lineGuard : VE.Formula := .top) : Right :=
  ⟨"r21", "person", guard, [accessLine lineGuard]⟩

def r21Doc (guard : VE.Formula := .top) (lineGuard : VE.Formula := .top) (limits : List VE.Rights.Limitation := [])
    (base : List (String × List String) := []) : RightsDoc :=
  mkRights ["state", "person"] ([("country_of", ["state", "person"]), ("charged", ["person"])] ++ base)
    [VE.Norms.Checks.oblig "public_service_access_required" ["state", "person"] false none "{0} grant {1} access",
     VE.Norms.Checks.plain "vulnerable" ["person"] false]
    [] block [r21 guard lineGuard] limits []

def charged (i : Nat) : VE.Formula := .unary "charged" (.var i)
def trig (φ : VE.Formula) (a b : Nat) : Clause := ⟨.trigger, φ, (a, b)⟩
def rel (slots : Nat × Nat) (total : Option Nat := none) (pred := "country_of") (cites : List String := []) :
    Relation := ⟨pred, slots, total, cites⟩

def cline (clauses : List Clause) (relation : Option Relation) (elided : List (Nat × Nat))
    (lineGuard : VE.Formula := .top) : CLine :=
  ⟨accessLine lineGuard, clauses, relation, elided, (0, 100)⟩

def cdoc (L : CLine) (doc : RightsDoc := r21Doc) : ClauseDoc := ⟨doc, [("r21", "equal-access", L)], []⟩

def verdict : Except String Unit → String
  | .ok () => "ok"
  | .error e => e

def check (L : CLine) (doc : RightsDoc := r21Doc) : String := verdict (checkClauses (cdoc L doc))

def guardAfter (L : CLine) (doc : RightsDoc := r21Doc) : VE.Formula := guardOf (plain (cdoc L doc)) "equal-access"

#guard diag r21Doc == "ok"

/-! ## K1: no clause, no relation -/

def k1 : CLine := cline [] none []

example : plain (cdoc k1) = r21Doc := plain_identity _ (by simp [cdoc, k1, cline])
#guard check k1 == "ok"
#guard VE.Rights.sourceLines (plain (cdoc k1)) == VE.Rights.sourceLines r21Doc
#guard VE.Rights.limPremisesLabelled (plain (cdoc k1)) == [] && VE.Rights.limPremises r21Doc == []

/-! ## K2: a relation, not total; the line selects only where it holds -/

def k2 : CLine := cline [] (some (rel (0, 1))) []

#guard check k2 == "ok"
#guard guardAfter k2 == .and .top (.binary "country_of" (.var 1) (.var 0))
#guard diag (plain (cdoc k2)) == "ok"
#guard selectsAt (plain (cdoc k2)) "equal-access" (model [("country_of", [["Texas", "Ann"]])]) ["Texas", "Ann"]
#guard !selectsAt (plain (cdoc k2)) "equal-access" (model [("country_of", [["Texas", "Ann"]])]) ["Texas", "Bob"]

-- a decoded document's source order is plained too; an unknown rule's guard is `⊤`
#guard guardAfter k2 { r21Doc with sourceOrder := some [("r21", accessLine)] } ==
  .and .top (.binary "country_of" (.var 1) (.var 0))
#guard guardOf (plain (cdoc k2)) "other" == .top

-- slots (1, 0): slot 1 is variable 0
#guard guardAfter (cline [] (some (rel (1, 0) (pred := "resident_of"))) [])
    (r21Doc (base := [("resident_of", ["person", "state"])])) == .and .top (.binary "resident_of" (.var 0) (.var 1))
#guard check (cline [] (some (rel (1, 0) (pred := "resident_of"))) []) (r21Doc (base := [("resident_of", ["person", "state"])])) ==
  "ok"

/-! ## K3 accepted: total on the holder slot 1, `H_R = ⊤` typed -/

def k3 : CLine := cline [] (some (rel (0, 1) (some 1))) []

#guard check k3 == "ok"

/-! ## K4: a trigger clause and an elided span -/

def k4 : CLine := cline [trig (charged 0) 10 20] none [(30, 40)]

#guard check k4 == "ok"
#guard guardAfter k4 == .and .top (charged 0)
-- `elided_bytes = 10`, by the product code the route emits it with (ElidedBytes.lean): [30, 40) is 10 bytes
#guard elidedTotal (entryElided (cdoc k4)) == 10
#guard elidedTotal (entryElided (cdoc (cline [trig (charged 0) 10 20] none [(30, 40), (40, 41), (60, 100)]))) == 51
#guard elidedTotal (entryElided (cdoc (cline [] none []))) == 0
-- the line's own guard is kept and comes first; clauses in wire order, then the relation atom
#guard guardAfter (cline [trig (charged 0) 10 20, trig (.binary "country_of" (.var 1) (.var 0)) 20 30]
    (some (rel (0, 1))) [] (charged 0)) (r21Doc (lineGuard := charged 0)) ==
  .and (.and (.and (charged 0) (charged 0)) (.binary "country_of" (.var 1) (.var 0)))
    (.binary "country_of" (.var 1) (.var 0))
#guard check (cline [trig (charged 0) 10 20] none [] (charged 0)) (r21Doc (lineGuard := charged 0)) == "ok"

/-! ## K5: a clause span inside the unit `[0, 100)`, at and around its ends -/

#guard check (cline [trig (charged 0) 90 110] none []) == "ClauseSpan: equal-access: [90, 110)"
#guard check (cline [trig (charged 0) 90 100] none []) == "ok"
#guard check (cline [trig (charged 0) 90 101] none []) == "ClauseSpan: equal-access: [90, 101)"
#guard check (cline [trig (charged 0) 0 10] none []) == "ok"
#guard check { cline [trig (charged 0) 4 10] none [] with unitSpan := (5, 100) } == "ClauseSpan: equal-access: [4, 10)"
#guard check { cline [trig (charged 0) 5 10] none [] with unitSpan := (5, 100) } == "ok"
#guard check (cline [trig (charged 0) 10 10] none []) == "ClauseSpan: equal-access: [10, 10)"
#guard check (cline [trig (charged 0) 10 11] none []) == "ok"
#guard check (cline [] none [(99, 101)]) == "ClauseSpan: equal-access: [99, 101)"

/-! ## K6: an elided span overlapping a clause; adjacent spans are disjoint -/

#guard check (cline [trig (charged 0) 10 20] none [(15, 25)]) == "ClauseSpan: equal-access: [15, 25)"
#guard check (cline [trig (charged 0) 10 20] none [(20, 25)]) == "ok"
#guard check (cline [trig (charged 0) 10 20] none [(19, 25)]) == "ClauseSpan: equal-access: [19, 25)"
#guard check (cline [trig (charged 0) 10 20] none [(5, 10)]) == "ok"
#guard check (cline [trig (charged 0) 10 20] none [(5, 11)]) == "ClauseSpan: equal-access: [5, 11)"
#guard check (cline [trig (charged 0) 10 20] none [(30, 40), (35, 45)]) == "ClauseSpan: equal-access: [35, 45)"
#guard check (cline [trig (charged 0) 10 20, trig (charged 0) 12 14] none []) == "ClauseSpan: equal-access: [12, 14)"

-- gaps on either side of an earlier span; an overlap with an older span than the last
#guard check (cline [trig (charged 0) 10 20] none [(25, 30), (0, 5)]) == "ok"
#guard check (cline [trig (charged 0) 10 20, trig (charged 0) 30 40] none [(15, 16)]) == "ClauseSpan: equal-access: [15, 16)"

/-! ## K7: clause typing in the line's context `[person, state]` (var 0 the person, var 1 the state) -/

#guard check (cline [trig (charged 1) 10 20] none []) == "InvalidInput: ill-typed clause 0 of rule equal-access"
#guard check (cline [trig (charged 0) 10 20, trig (charged 1) 20 30] none []) ==
  "InvalidInput: ill-typed clause 1 of rule equal-access"
#guard check (cline [trig (.binary "country_of" (.var 1) (.var 0)) 10 20] none []) == "ok"
#guard check (cline [trig (.binary "country_of" (.var 0) (.var 1)) 10 20] none []) ==
  "InvalidInput: ill-typed clause 0 of rule equal-access"
-- not a base formula: a regulated predicate
#guard check (cline [trig (.unary "vulnerable" (.var 0)) 10 20] none []) ==
  "InvalidInput: ill-typed clause 0 of rule equal-access"
-- typing comes before spans (4.1 step 3)
#guard check (cline [trig (charged 1) 90 110] none []) == "InvalidInput: ill-typed clause 0 of rule equal-access"

/-! ## K8: the relation's slots, predicate and totality -/

#guard check (cline [] (some (rel (1, 1))) []) == "RelationShape: equal-access"
#guard check (cline [] (some (rel (0, 1) (some 0))) []) == "RelationShape: equal-access"
#guard check (cline [] (some (rel (0, 2))) []) == "RelationShape: equal-access"
#guard check (cline [] (some (rel (1, 0))) []) == "RelationShape: equal-access"
#guard check (cline [] (some (rel (0, 1) (some 2))) []) == "RelationShape: equal-access"
#guard check (cline [] (some (rel (0, 1) (pred := "charged"))) []) == "RelationShape: equal-access"
#guard check (cline [] (some (rel (0, 1) (pred := "public_service_access_required"))) []) ==
  "RelationShape: equal-access"
-- 1.5: a reserved prefix is refused even when declared
#guard check (cline [] (some (rel (0, 1) (pred := "ve__near"))) []) (r21Doc (base := [("ve__near", ["state", "person"])])) ==
  "RelationShape: equal-access"
#guard check (cline [] (some (rel (0, 1) (pred := "near"))) []) (r21Doc (base := [("near", ["state", "person"])])) == "ok"
#guard check (cline [] (some (rel (0, 1) (pred := "rights__near"))) []) (r21Doc (base := [("rights__near", ["state", "person"])])) ==
  "RelationShape: equal-access"
#guard check (cline [] (some (rel (0, 1) (pred := "soft__near"))) []) (r21Doc (base := [("soft__near", ["state", "person"])])) ==
  "RelationShape: equal-access"
-- a slot equal to the arity is out of range whatever the sorts read there
#guard check (cline [] (some (rel (0, 2) (pred := "odd"))) []) (r21Doc (base := [("odd", ["state", ""])])) ==
  "RelationShape: equal-access"
#guard check (cline [] (some (rel (2, 0) (pred := "odd"))) []) (r21Doc (base := [("odd", ["", "state"])])) ==
  "RelationShape: equal-access"
-- on a ternary line the holder slot 1 is not one of the relation's slots (0, 2)
def triDoc : RightsDoc :=
  mkRights ["state", "person"] [("country_of", ["state", "person"])]
    [VE.Norms.Checks.oblig "p3" ["state", "person", "person"] false none] [] block
    [⟨"r21", "person", .top, [line .claim (strictNode "tri" "p3" true)]⟩] [] []
#guard verdict (checkClauses ⟨triDoc, [("r21", "tri", ⟨line .claim (strictNode "tri" "p3" true), [], some (rel (0, 2) (some 1)),
    [], (0, 100)⟩)], []⟩) == "RelationShape: tri"
-- spans come before the relation
#guard check (cline [] (some (rel (1, 1))) [(90, 110)]) == "ClauseSpan: equal-access: [90, 110)"

/-! ## Cites -/

#guard check (cline [] (some (rel (0, 1) (cites := ["u1", "u082"]))) []) == "ok"
#guard check (cline [] (some (rel (0, 1) (cites := ["u1", "u9"]))) []) == "UnknownSymbol: unit u9"
#guard check (cline [] (some (rel (0, 1) (cites := ["u9", "u1"]))) []) == "UnknownSymbol: unit u9"
#guard check (cline [] (some (rel (1, 1) (cites := ["u9"]))) []) == "RelationShape: equal-access"

/-! ## K14: `H_R` typed over the base vocabulary for a total relation -/

#guard check k3 (r21Doc (.unary "vulnerable" (.var 0))) == "RelationShape: equal-access"
#guard check k2 (r21Doc (.unary "vulnerable" (.var 0))) == "ok"
#guard check k3 (r21Doc (charged 0)) == "ok"

#guard holderGuardOf (cdoc k3 (r21Doc (charged 0))) "r21" == charged 0 && holderGuardOf (cdoc k3) "r9" == .top
#guard WellFormedClauses (cdoc k4) && !WellFormedClauses (cdoc (cline [trig (charged 0) 90 110] none []))

/-! ## K11: clauses or a relation on a power or a fan-out line -/

/-- ε's power line, as `VE.Rights.Examples.epsilon` writes it. -/
def marryLine : SourceLine :=
  ⟨.power, none, some (strictNode "may-marry" "marry_permitted" true),
    some (strictNode "recognise-marriage" "recognise_marriage_required" true), [], none, []⟩

def onPower (L : CLine) : ClauseDoc := ⟨epsilon, [("r16", "may-marry", L)], []⟩

#guard verdict (checkClauses (onPower ⟨marryLine, [], some (rel (0, 1)), [], (0, 100)⟩)) == "ClauseLineShape: may-marry"
#guard verdict (checkClauses (onPower ⟨marryLine, [trig (.unary "married" (.var 0)) 1 2], none, [], (0, 100)⟩)) ==
  "ClauseLineShape: may-marry"
#guard verdict (checkClauses (onPower ⟨marryLine, [], none, [(1, 2)], (0, 100)⟩)) == "ok"
#guard verdict (checkClauses ⟨VE.Rights.Examples.beta fanMap,
    [("r5", "no-torture", ⟨fanLine fanMap, [], some (rel (0, 1) (pred := "near")), [], (0, 100)⟩)], []⟩) ==
  "ClauseLineShape: no-torture"
#guard verdict (checkClauses ⟨VE.Rights.Examples.beta fanMap,
    [("r5", "no-torture", ⟨fanLine fanMap, [], none, [(0, 5)], (0, 100)⟩)], []⟩) == "ok"

#guard verdict (checkClauses ⟨VE.Rights.Examples.beta [("state", "torture_permitted_state")],
    [("r5", "no-torture", ⟨fanLine [("state", "torture_permitted_state")], [], some (rel (0, 1)), [], (0, 100)⟩)], []⟩) ==
  "ClauseLineShape: no-torture"

/-! ## Entries

Every entry fault goes through `entryError`, whether or not the entry's right is in the document. A rule on two lines
of the rights document gets rights' own `DuplicateDeclaration` text when that is rights' first fault on the document
(`twice`, `across`); otherwise, and for every other entry fault, the text is `InvalidInput: invalid clauses of rule
<n>` (`twice` with no holders, `twoHolders`, the one-line `r21Doc`). -/

#guard verdict (checkClauses ⟨r21Doc, [("r21", "equal-access", k1), ("r21", "equal-access", k2)], []⟩) ==
  "InvalidInput: invalid clauses of rule equal-access"
#guard verdict (checkClauses ⟨r21Doc, [("r21", "equal-access", k2), ("r21", "equal-access", k2)], []⟩) ==
  "InvalidInput: invalid clauses of rule equal-access"
def twice : RightsDoc := { r21Doc with rs := [⟨"r21", "person", .top, [accessLine, accessLine]⟩] }
#guard diag twice == "DuplicateDeclaration: rule equal-access"
#guard check k2 twice == diag twice
#guard verdict (checkClauses ⟨twice, [("r21", "equal-access", k1), ("r21", "equal-access", k2)], []⟩) == diag twice
#guard verdict (checkClauses ⟨twice, [("r21", "equal-access", k2)], []⟩) == diag twice
-- the entry names a right `r9` that is not in the document: still `entryError`, so rights' text (F1)
#guard verdict (checkClauses ⟨twice, [("r9", "equal-access", k2)], []⟩) == diag twice
#guard verdict (checkClauses ⟨{ twice with rights.holders := [] }, [("r9", "equal-access", k2)], []⟩) ==
  "InvalidInput: invalid clauses of rule equal-access"
#guard diag { twice with rights.holders := [] } == "InvalidInput: invalid rights block"
#guard check k2 { twice with rights.holders := [] } == "InvalidInput: invalid clauses of rule equal-access"
-- the rule on a line of each of two rights: still a duplicate, rights' text
def across : RightsDoc := { r21Doc with rs := [r21, ⟨"r22", "person", .top, [accessLine]⟩] }
#guard diag across == "DuplicateDeclaration: rule equal-access"
#guard check k2 across == diag across
-- the rule on one line: rights' first fault, a duplicate holder, is not the entry's; the head keeps its text
def twoHolders : RightsDoc := { r21Doc with rights.holders := ["person", "person"] }
#guard diag twoHolders == "DuplicateDeclaration: holder person"
#guard verdict (checkClauses ⟨twoHolders, [("r21", "equal-access", k2), ("r21", "equal-access", k2)], []⟩) ==
  "InvalidInput: invalid clauses of rule equal-access"
#guard verdict (checkClauses ⟨r21Doc, [("r9", "equal-access", k1)], []⟩) == "InvalidInput: invalid clauses of rule equal-access"
#guard verdict (checkClauses ⟨r21Doc, [("r21", "other", k1)], []⟩) == "InvalidInput: invalid clauses of rule other"
#guard verdict (checkClauses ⟨r21Doc, [("r21", "equal-access", cline [] none [] (charged 0))], []⟩) ==
  "InvalidInput: invalid clauses of rule equal-access"
#guard verdict (checkClauses ⟨r21Doc, [], []⟩) == "ok"

/-! ## K13: `Lim_D` unchanged by `plain` -/

#guard VE.Rights.limPremisesLabelled (plain (cdoc k4 (r21Doc (limits := [l29])))) ==
    VE.Rights.limPremisesLabelled (r21Doc (limits := [l29])) &&
  (VE.Rights.limPremisesLabelled (r21Doc (limits := [l29]))).length == 2

/-! ## K12: a reading candidate's line with a total relation; `plainContent` otherwise -/

def candDoc (L : CLine) : ClauseDoc :=
  ⟨r21Doc, [], [("s", 0, .right (r21 (lineGuard := charged 0)), []), ("s", 1, .right r21, [("r21", "equal-access", L)])]⟩

#guard verdict (checkCandidates (candDoc k3)) == "RelationOnCandidate: s:1: equal-access"
#guard verdict (checkCandidates (candDoc k2)) == "ok"
-- a candidate whose own right has two lines named `equal-access`: rights' text on that right
#guard verdict (checkCandidates ⟨r21Doc, [], [("s", 1, .right ⟨"r21", "person", .top, [accessLine, accessLine]⟩,
    [("r21", "equal-access", k2)])]⟩) == "DuplicateDeclaration: rule equal-access"
-- the same with the entry naming a right `r9` that is not the candidate's: rights' text on that right (F1)
#guard verdict (checkCandidates ⟨r21Doc, [], [("s", 1, .right ⟨"r21", "person", .top, [accessLine, accessLine]⟩,
    [("r9", "equal-access", k2)])]⟩) == "DuplicateDeclaration: rule equal-access"
-- `.rightLines`: the two lines are the candidate's, not rights' (`D.doc`'s); the head keeps its text, also when
-- `D.doc` has a fault of its own
#guard verdict (checkCandidates ⟨r21Doc, [], [("s", 1, .rightLines "r21" [accessLine, accessLine],
    [("r21", "equal-access", k2)])]⟩) == "InvalidInput: invalid clauses of rule equal-access"
#guard verdict (checkCandidates ⟨twoHolders, [], [("s", 1, .rightLines "r21" [accessLine, accessLine],
    [("r21", "equal-access", k2)])]⟩) == "InvalidInput: invalid clauses of rule equal-access"
#guard verdict (checkCandidates (candDoc (cline [trig (charged 0) 90 110] none []))) == "ClauseSpan: equal-access: [90, 110)"
-- the candidate's own right gives `H_R`: refused before the abstention
#guard verdict (checkCandidates ⟨r21Doc, [], [("s", 1, .right (r21 (.unary "vulnerable" (.var 0))),
    [("r21", "equal-access", k3)])]⟩) == "RelationShape: equal-access"
#guard verdict (checkCandidates ⟨r21Doc, [], [("s", 1, .rightLines "r21" [accessLine], [("r21", "equal-access", k3)])]⟩) ==
  "RelationOnCandidate: s:1: equal-access"
#guard verdict (checkCandidates ⟨r21Doc, [], [("s", 1, .rightLines "r21" [accessLine], [("r21", "equal-access", k2)])]⟩) == "ok"
#guard verdict (checkCandidates ⟨r21Doc, [], [("s", 1, .assertion .top, [("r21", "equal-access", k2)])]⟩) ==
  "InvalidInput: invalid clauses of rule equal-access"
#guard plainContent r21Doc.soft [("r21", "equal-access", k2)] (.right r21) ==
  .right { r21 with lines := [accessLine (.and .top (.binary "country_of" (.var 1) (.var 0)))] }
#guard plainContent r21Doc.soft [("r21", "equal-access", k2)] (.rightLines "r21" [accessLine]) ==
  .rightLines "r21" [accessLine (.and .top (.binary "country_of" (.var 1) (.var 0)))]
#guard plainContent r21Doc.soft [("r9", "equal-access", k2)] (.right r21) == .right r21

/-! ## Several rights, lines and entries, the structured one in the middle of each -/

def nl (n : String) : SourceLine := line .claim (strictNode n "public_service_access_required" true)
def unl (n : String) : CLine := ⟨nl n, [], none, [], (0, 100)⟩
def mid : Right := ⟨"r21", "person", .top, [nl "b", accessLine, nl "c"]⟩
def many : RightsDoc := { r21Doc with rs := [⟨"r20", "person", .top, [nl "a"]⟩, mid, ⟨"r22", "person", .top, [nl "d"]⟩] }
def midEntries (L : CLine) : List (String × String × CLine) :=
  [("r21", "b", unl "b"), ("r21", "equal-access", L), ("r21", "c", unl "c")]
def manyDoc (L : CLine) (doc : RightsDoc := many) : ClauseDoc :=
  ⟨doc, ("r20", "a", unl "a") :: midEntries L ++ [("r22", "d", unl "d")], []⟩
def k2Guard : VE.Formula := .and .top (.binary "country_of" (.var 1) (.var 0))
def k5 : CLine := cline [trig (charged 0) 90 110] none []

#guard verdict (checkClauses (manyDoc k2)) == "ok"
#guard verdict (checkClauses (manyDoc k5)) == "ClauseSpan: equal-access: [90, 110)"
#guard guardOf (plain (manyDoc k2)) "equal-access" == k2Guard && guardOf (plain (manyDoc k2)) "c" == .top
#guard guardOf (plain (manyDoc k2 { many with sourceOrder := some (many.rs.flatMap (fun R => R.lines.map (R.name, ·))) }))
  "equal-access" == k2Guard
#guard verdict (checkCandidates ⟨many, [], [("s", 1, .right mid, midEntries k2)]⟩) == "ok"
#guard verdict (checkCandidates ⟨many, [], [("s", 1, .right mid, midEntries k3)]⟩) == "RelationOnCandidate: s:1: equal-access"
#guard verdict (checkCandidates ⟨many, [], [("s", 1, .right mid, midEntries k5)]⟩) == "ClauseSpan: equal-access: [90, 110)"
#guard verdict (checkCandidates ⟨many, [], [("s", 1, .rightLines "r21" mid.lines, midEntries k2)]⟩) == "ok"
#guard plainContent many.soft (midEntries k2) (.right mid) == .right { mid with lines := [nl "b", accessLine k2Guard, nl "c"] }
#guard plainContent many.soft (midEntries k2) (.rightLines "r21" mid.lines) == .rightLines "r21" [nl "b", accessLine k2Guard, nl "c"]

/-! ## Relation.lean: `Rel_D` and the slot (K2, K3, K13) -/

/-- K3's ρ: `∀x:person. ⊤ → ∃y:state. country_of(y, x)`. -/
def k3Premise (H : VE.Formula := .top) : VE.Formula :=
  .all "person" (.implies H (.ex "state" (.binary "country_of" (.var 0) (.var 1))))
def onlyAnn : VE.FiniteModel String := model [("country_of", [["Texas", "Ann"]])]
def both : VE.FiniteModel String := model [("country_of", [["Texas", "Ann"], ["Texas", "Bob"]])]
def slotValid (D : ClauseDoc) (M : VE.FiniteModel String) : Bool :=
  VE.Compose.backgroundValidP (VE.Rights.correlate (plain D)) (clauseSlot D) M

-- K2: not total, so `Rel_D = []` and the slot is `Lim_D` (`clauseSlot_no_total`)
#guard relPremisesLabelled (cdoc k2) == [] && clauseSlot (cdoc k2) == VE.Rights.limPremises (plain (cdoc k2))
#guard relPremisesLabelled (cdoc k1) == [] && relPremisesLabelled (cdoc k4) == []
-- K3: one premise, labelled by the rule; false where Bob has no country, true once he has one
#guard relPremisesLabelled (cdoc k3) == [("rights:relation:equal-access:total", k3Premise)]
#guard relPremises (cdoc k3) == [k3Premise] && clauseSlot (cdoc k3) == [k3Premise]
#guard diag (plain (cdoc k3)) == "ok"
#guard !slotValid (cdoc k3) onlyAnn && slotValid (cdoc k3) both && slotValid (cdoc k2) onlyAnn
-- `relation_some_bearer` at Bob: Texas is related to him, and the line selects at (Texas, Bob)
#guard both.relations "country_of" |>.contains ["Texas", "Bob"]
#guard selectsAt (plain (cdoc k3)) "equal-access" both ["Texas", "Bob"] &&
  !selectsAt (plain (cdoc k3)) "equal-access" onlyAnn ["Texas", "Bob"]
-- the holder guard is the premise's antecedent; slots (1, 0) put the holder first
#guard relPremises (cdoc k3 (r21Doc (guard := charged 0))) == [k3Premise (charged 0)]
#guard relPremises (cdoc (cline [] (some (rel (1, 0) (some 1) "resident_of")) [])
    (r21Doc (base := [("resident_of", ["person", "state"])]))) ==
  [.all "person" (.implies .top (.ex "state" (.binary "resident_of" (.var 1) (.var 0))))]
-- two entries, in document order; an entry without a total relation adds nothing
#guard (relPremisesLabelled ⟨many, [("r20", "a", { unl "a" with relation := some (rel (0, 1) (some 1)) }),
    ("r21", "equal-access", k2), ("r22", "d", { unl "d" with relation := some (rel (0, 1) (some 1)) })], []⟩).map (·.1) ==
  ["rights:relation:a:total", "rights:relation:d:total"]
-- K13: `Lim_D` of l29 first, then `Rel_D`; `plain` leaves `Lim_D` unchanged (`plain_limPremises`)
def k13 : ClauseDoc := cdoc k3 (r21Doc (limits := [l29]))
#guard clauseSlotLabelled k13 == VE.Rights.limPremisesLabelled (plain k13) ++ relPremisesLabelled k13
#guard (clauseSlotLabelled k13).map (·.1) ==
  (VE.Rights.limPremisesLabelled k13.doc).map (·.1) ++ ["rights:relation:equal-access:total"]
#guard (VE.Rights.limPremisesLabelled k13.doc).length == 2 && clauseSlot k13 ==
  VE.Rights.limPremises k13.doc ++ [k3Premise]
#guard VE.Rights.limPremises (plain k13) == VE.Rights.limPremises k13.doc
#guard VE.Compose.Labelled.wellLabelled (clauseSlotLabelled k13)
-- two total relations: both premises, in document order, after `Lim_D`
def twoTotal : ClauseDoc := ⟨{ many with limits := [l29] }, [("r20", "a", { unl "a" with relation := some (rel (0, 1) (some 1)) }),
  ("r22", "d", { unl "d" with relation := some (rel (0, 1) (some 1)) })], []⟩
#guard relPremises twoTotal == [k3Premise, k3Premise] &&
  (clauseSlotLabelled twoTotal).map (·.1) == (VE.Rights.limPremisesLabelled twoTotal.doc).map (·.1) ++
    ["rights:relation:a:total", "rights:relation:d:total"] &&
  clauseSlot twoTotal == VE.Rights.limPremises twoTotal.doc ++ [k3Premise, k3Premise]
-- `clauseSlot_labelled` needs `Lim_D`'s labels distinct (DRI question Q3): pk-1c's `cx`
-- (lean/VE/NormDefaults/PacksLegacyExamples.lean), rebuilt here without importing `VE.Readings`, satisfies the
-- spec's two hypotheses and repeats `rights:limitation:x:p:q:necessary:c`.
open VE.Norms.Checks (perm) in
def cxDoc : ClauseDoc := ⟨mkRights ["state", "person"] []
    [perm "p:q" ["state", "person"] true "{0} arrest {1}", perm "q" ["state", "person"] true "{0} detain {1}"] [] block
    [⟨"r9", "person", .top, [line .claim (strictNode "no-a" "p:q" false), line .claim (strictNode "no-b" "q" false)]⟩]
    [⟨"x", none, none, some "unstated", [⟨"c", true, "c holds", none⟩], []⟩,
     ⟨"x:p", none, none, some "unstated", [⟨"c", true, "c holds", none⟩], []⟩] [], [], []⟩
#guard WellFormedClauses cxDoc && VE.Rights.WellFormedRights (plain cxDoc) &&
  !VE.Compose.Labelled.wellLabelled (clauseSlotLabelled cxDoc) &&
  !VE.Compose.Labelled.wellLabelled (VE.Rights.limPremisesLabelled cxDoc.doc)
-- DRI question Q1 (`elaborate_plain`, Wire.lean, cmp-s3b): the rights decoder reads a clause of depth 64, but not
-- that clause under the one `and` that `plain` adds, and `WellFormedRights` bounds no depth.
def notChain : Nat → Lean.Json
  | 0 => .arr #["top"]
  | n + 1 => .arr #["not", notChain n]
#guard (VE.Norms.Wire.budgetFormula VE.Limits.maxDepth 0 (notChain 63)).isOk &&
  !(VE.Norms.Wire.budgetFormula VE.Limits.maxDepth 0 (.arr #["and", .arr #["top"], notChain 63])).isOk

/-! ## cmp-s3-cfr-1b: the span check's reference, 9.2's F11 to F14 -/

/-- Section 7's span check as written: each span against every earlier one. `checkSpans` answers as it does. -/
def checkSpansPairwise (n : String) (u : Nat × Nat) : List (Nat × Nat) → List (Nat × Nat) → Except String Unit
  | _, [] => .ok ()
  | earlier, s :: rest =>
    if s.1 < s.2 && u.1 ≤ s.1 && s.2 ≤ u.2 && earlier.all (fun t => s.2 ≤ t.1 || t.2 ≤ s.1) then
      checkSpansPairwise n u (s :: earlier) rest
    else .error s!"ClauseSpan: {n}: [{s.1}, {s.2})"
/-- Every list of at most `k` spans with ends in `0 … m`. -/
def spanLists (m k : Nat) : List (List (Nat × Nat)) :=
  let spans := (List.range (m + 1)).flatMap fun a => (List.range (m + 1)).map fun b => (a, b)
  (List.range (k + 1)).flatMap fun i => (List.range i).foldl (fun ls _ => ls.flatMap fun l => spans.map (· :: l)) [[]]
def samePairwise (m k : Nat) (u : Nat × Nat) : Bool :=
  (spanLists m k).all fun l => verdict (checkSpans "n" u ∅ l) == verdict (checkSpansPairwise "n" u [] l)
-- every list of up to three spans in [0, 5] and of four in [0, 3], inside and across the unit's ends
#guard (spanLists 5 3).length == 1 + 36 + 36 ^ 2 + 36 ^ 3 && samePairwise 5 3 (1, 4) && samePairwise 3 4 (0, 3)

/-- A finite model over the given domains. -/
def world (doms : List (String × List String)) (rels : List (String × List (List String))) : VE.FiniteModel String where
  domains s := ((doms.find? (·.1 == s)).map (·.2)).getD []
  constants _ := none
  relations p := ((rels.find? (·.1 == p)).map (·.2)).getD []
/-- One right `r` (holder person) with one claim line `n` on the obligation `p(state, person)`, over `base`. -/
def oneClaim (r n p : String) (base : List (String × List String)) (sorts := ["state", "person"]) : RightsDoc :=
  { mkRights sorts base [VE.Norms.Checks.oblig p ["state", "person"] false none "{0} act for {1}"] [] block
      [⟨r, "person", .top, [line .claim (strictNode n p true)]⟩] [] [] with sourceUnits := ["u035", "u039", "u054"] }
def claimLine (n p : String) (clauses : List Clause) (relation : Option Relation) (u : Nat × Nat) : CLine :=
  ⟨line .claim (strictNode n p true), clauses, relation, [], u⟩

-- F11 (UDHR u035 [3469, 3637), Art. 8): the trigger clause of 3 ("for acts violating the fundamental rights granted
-- him ... by law", [3541, 3635)) and `has_tribunals_competent_for`, total on the holder slot, cites u035
def f11Trigger : VE.Formula :=
  .ex "act" (.and (.binary "violates_right_of" (.var 0) (.var 1)) (.unary "right_granted_by_law" (.var 0)))
def f11 : ClauseDoc :=
  ⟨oneClaim "r8" "remedy" "remedy_required" [("violates_right_of", ["act", "person"]), ("right_granted_by_law", ["act"]),
      ("has_tribunals_competent_for", ["state", "person"])] ["state", "person", "act"],
    [("r8", "remedy", claimLine "remedy" "remedy_required" [⟨.trigger, f11Trigger, (3541, 3635)⟩]
      (some ⟨"has_tribunals_competent_for", (0, 1), some 1, ["u035"]⟩) (3469, 3637))], []⟩
def f11World (violated : Bool) : VE.FiniteModel String :=
  world [("state", ["S"]), ("person", ["P"]), ("act", ["A"])]
    ([("has_tribunals_competent_for", [["S", "P"]]), ("right_granted_by_law", [["A"]])] ++
      if violated then [("violates_right_of", [["A", "P"]])] else [])
#guard WellFormedClauses f11 && diag (plain f11) == "ok"
#guard guardOf (plain f11) "remedy" ==
  .and (.and .top f11Trigger) (.binary "has_tribunals_competent_for" (.var 1) (.var 0))
-- no violated right: the line selects at no tuple of that person; with one it does; the premise is in the slot
#guard !selectsAt (plain f11) "remedy" (f11World false) ["S", "P"] && selectsAt (plain f11) "remedy" (f11World true) ["S", "P"]
#guard (clauseSlotLabelled f11).map (·.1) == ["rights:relation:remedy:total"]

-- F12 (UDHR u039 [3734, 3935), Art. 10): a scope clause and "in full equality" as a clause on `full_equality`, both
-- in the guard in wire order, `elided: []`
def f12Scope : VE.Formula := .unary "rights_and_charges_determined" (.var 0)
def f12 : ClauseDoc :=
  ⟨oneClaim "r10" "fair-hearing" "fair_hearing_required" [("rights_and_charges_determined", ["person"]),
      ("full_equality", ["person"])],
    [("r10", "fair-hearing", claimLine "fair-hearing" "fair_hearing_required"
      [⟨.scope, f12Scope, (3838, 3934)⟩, ⟨.scope, .unary "full_equality" (.var 0), (3755, 3771)⟩] none (3734, 3935))], []⟩
#guard WellFormedClauses f12 && diag (plain f12) == "ok" && relPremisesLabelled f12 == []
#guard guardOf (plain f12) "fair-hearing" == .and (.and .top f12Scope) (.unary "full_equality" (.var 0))
#guard selectsAt (plain f12) "fair-hearing" (model [("rights_and_charges_determined", [["Ann"]]),
    ("full_equality", [["Ann"]])]) ["Texas", "Ann"] &&
  !selectsAt (plain f12) "fair-hearing" (model [("rights_and_charges_determined", [["Ann"]])]) ["Texas", "Ann"]

-- F13 (UDHR u054 [5239, 5284), Art. 15(1)), S3's share: the claim reading with `responsible_for` total on the holder.
-- Two states, one person, responsible_for only with the first: the slot holds (relation_some_bearer's bearer is S1),
-- the second state owes nothing under this line, and the unscoped claim would have it owe
def f13 (relation : Option Relation := some ⟨"responsible_for", (0, 1), some 1, []⟩) : ClauseDoc :=
  ⟨oneClaim "r15" "nationality" "nationality_required" [("responsible_for", ["state", "person"])],
    [("r15", "nationality", claimLine "nationality" "nationality_required" [] relation (5239, 5284))], []⟩
def twoStates : VE.FiniteModel String :=
  world [("state", ["S1", "S2"]), ("person", ["P"])] [("responsible_for", [["S1", "P"]])]
#guard WellFormedClauses (f13) && diag (plain (f13)) == "ok" && slotValid (f13) twoStates
#guard !slotValid (f13) (world [("state", ["S1", "S2"]), ("person", ["P"])] [])
#guard selectsAt (plain (f13)) "nationality" twoStates ["S1", "P"] &&
  !selectsAt (plain (f13)) "nationality" twoStates ["S2", "P"] &&
  selectsAt (plain (f13 none)) "nationality" twoStates ["S2", "P"]

-- `clauseSlot_wellFormed` at K3, K13 and F11: every premise of the slot checks at layer 0 of `correlate (plain D)`
def slotChecks (D : ClauseDoc) : Bool :=
  (clauseSlot D).all (·.check (VE.Norms.envAt (VE.SoftNorms.soften (VE.Rights.correlate (plain D))) 0) [])
#guard slotChecks (cdoc k3) && slotChecks k13 && slotChecks f11 && (clauseSlot f11).length == 1

-- F14 (UDHR u077 [6861, 6938), Art. 21(2)): the candidate with `country_of` (total null) plains through
-- `plainContent`, the one without it is unchanged; a state that is not the person's country separates them
#guard plainContent r21Doc.soft [("r21", "equal-access", k2)] (.right r21) ==
  .right (r21 (lineGuard := .and .top (.binary "country_of" (.var 1) (.var 0)))) &&
  plainContent r21Doc.soft [] (.right r21) == .right r21 &&
  plainContent r21Doc.soft [("r21", "equal-access", k2)] (.rightLines "r21" [accessLine]) ==
    .rightLines "r21" [accessLine k2Guard]
#guard !selectsAt (plain (cdoc k2)) "equal-access" (model []) ["Texas", "Ann"] &&
  selectsAt (plain (cdoc k1)) "equal-access" (model []) ["Texas", "Ann"]

end VE.RightClauses.Examples
