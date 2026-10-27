import VE.Acts.Elaborate
import VE.Acts.TableExamples

/-! Fixtures of the elaboration (docs/spec/act-phrases.md 6.3, 11.3: E1 to E10, E16; sorts `person`, guards `top`).

Each check of `elaborateMap` is fixed on its refusing side and its accepting side, at its boundary where it has one.
The act trees are 11.2's, written by hand in `TableExamples.lean` (no parse yet).
-/

namespace VE.Acts.ElaborateExamples
open VE.Acts VE.Acts.TableExamples VE.Norms VE.NormDefaults

def env (ps : List (String × List String)) : VE.Environment :=
  { sorts := ["person"], predicates := fun q => ps.lookup q, constants := fun _ => none }
def rg (n : String) (role : Role) (act : Option String := some ("{0} " ++ n)) (perm : Option String := none)
    (sorts : List String := ["person"]) : Regulated := ⟨n, sorts, false, role, act, perm⟩
def nd (n p : String) (sign : Bool) (over : List String := []) (guard : VE.Formula := .top)
    (carveOuts : List VE.Formula := []) : Node := ⟨n, p, sign, guard, carveOuts, over⟩
/-- A document over its regulated predicates and `extra` base predicates (unary, `person`). -/
def doc (rs : List Regulated) (ns : List Node) (unspec : List String := []) (defs : List Definition := [])
    (extra : List String := []) : ActsDoc :=
  ⟨⟨⟨env (rs.map (fun r => (r.name, r.sorts)) ++ extra.map (·, ["person"])), [], ⟨rs, defs, ns⟩⟩, unspec⟩,
   ⟨[], []⟩, [], [], 0⟩
def withActs (D : ActsDoc) (fx : List String) (acts : List (String × Act)) : ActsDoc := { D with fixed := fx, acts }

/-- What a result shows: its regulated predicates, rules, unspecified names and map; or its refusal. -/
def shown (r : Except String (UDoc × SplitMap)) : Except String (List Regulated × List Node × List String × SplitMap) :=
  r.map fun (U, M) => (U.D.T.regulated, U.D.T.nodes, U.unspec, M)
def refusal (D : ActsDoc) : Option String := errOf (elaborateMap D)

/-- E1: permission `p027`, act G6, rule `r027` sign false (*must not*: two prohibitions). -/
def e1 : ActsDoc := withActs (doc [rg "p027" .permission] [nd "r027" "p027" false]) fx6 [("p027", g6)]

def r027 : List Regulated := [rg "p027__1" .permission (some "{0} be subjected to torture"),
  rg "p027__2" .permission (some "{0} be subjected to cruel, inhuman or degrading treatment or punishment")]
#guard (shown (elaborateMap e1)).toOption == some (r027, [nd "r027-a1" "p027__1" false, nd "r027-a2" "p027__2" false], [],
  ⟨[("p027__1", "p027", 1), ("p027__2", "p027", 2)], [("r027-a1", "r027", 1), ("r027-a2", "r027", 2)]⟩)
#guard (elaborate e1).toOption.map (·.D.T.regulated) == some r027
-- The parts are declared with the source's sorts; the source is not.
#guard (elaborate e1).toOption.map (fun U => [U.D.E.predicates "p027__1", U.D.E.predicates "p027__2",
  U.D.E.predicates "p027", U.D.E.predicates "b"]) == some [some ["person"], some ["person"], none, none]
#guard (elaborate (withActs (doc [rg "p027" .permission] [nd "r027" "p027" false] (extra := ["b"])) fx6
  [("p027", g6)])).toOption.map (·.D.E.predicates "b") == some (some ["person"])

/-- E2: obligation `p079`, act G7 (one atom, a joined filler), rule sign true: unchanged. -/
def e2 : ActsDoc := withActs (doc [rg "p079" .obligation] [nd "r079" "p079" true] ["p079"]) fx7 [("p079", g7)]
#guard (shown (elaborateMap e2)).toOption == some ([rg "p079" .obligation], [nd "r079" "p079" true], ["p079"], ⟨[], []⟩)

/-- E3: permission `p123`, act G14v, rule sign false: five prohibitions. -/
def fx14 : List String := ["the user", "a false identity", "deceptive tactics", "the safety of others", "the user's interests"]
def e3 : ActsDoc := withActs (doc [rg "p123" .permission] [nd "r123" "p123" false]) fx14 [("p123", g14v)]
#guard (shown (elaborateMap e3)).toOption.map (fun (rs, ns, _, M) => (rs.map (·.name), rs.map (·.act), ns.map (·.name),
  M.preds.length)) == some (["p123__1", "p123__2", "p123__3", "p123__4", "p123__5"],
  ["{0} abandon the user", "{0} claim a false identity", "{0} use deceptive tactics", "{0} endanger the safety of others",
   "{0} act against the user's interests"].map some, ["r123-a1", "r123-a2", "r123-a3", "r123-a4", "r123-a5"], 5)

/-- E4: E1 plus `r027b` sign true (*may*: each, by the split marker) over `r027`: precedence splits pairwise. -/
def e4 : ActsDoc :=
  withActs (doc [rg "p027" .permission] [nd "r027" "p027" false, nd "r027b" "p027" true ["r027"]]) fx6 [("p027", g6)]
#guard (shown (elaborateMap e4)).toOption.map (·.2.1) == some [nd "r027-a1" "p027__1" false,
  nd "r027-a2" "p027__2" false, nd "r027b-a1" "p027__1" true ["r027-a1"], nd "r027b-a2" "p027__2" true ["r027-a2"]]
#guard (shown (elaborateMap e4)).toOption.map (·.2.2.2.rules) == some
  [("r027-a1", "r027", 1), ("r027-a2", "r027", 2), ("r027b-a1", "r027b", 1), ("r027b-a2", "r027b", 2)]

/-- E5: E1 with `p027` unspecified, beside an unspecified `k` that does not split. -/
def e5 : ActsDoc := withActs (doc [rg "k" .obligation, rg "p027" .permission]
  [nd "rk" "k" true, nd "r027" "p027" false] ["k", "p027"]) fx6 [("p027", g6)]
#guard (shown (elaborateMap e5)).toOption.map (·.2.2.1) == some ["k", "p027__1", "p027__2"]

/-! ### Step 1: the readings (D-20 to D-24) -/

-- E9: G11 under *may*: two readings, D-23 with Lean's numbered paraphrases.
#guard refusal (withActs (doc [rg "p" .permission (sorts := ["person", "person"])] [nd "r" "p" true]) fx11
  [("p", g11)]) == some "InvalidInput: rule r has more than one reading: 1. {0} may directly take part in {1}, and {0} may take part in {1} through freely chosen representatives. 2. {0} may directly take part in {1} or take part in {1} through freely chosen representatives, as one act done in any one of these ways (not each way on its own)."
-- E10: a plain predicate under sign false has no op: D-21; under sign true, G6 splits with *to*.
#guard refusal (withActs (doc [rg "p" .plain none] [nd "r" "p" false]) fx6 [("p", g6)]) ==
  some "InvalidInput: rule r has no modal word for a joined act"
#guard (shown (elaborateMap (withActs (doc [rg "p" .plain none] [nd "r" "p" true]) fx6 [("p", g6)]))).toOption.map
  (·.1.map (·.act)) == some [some "{0} to be subjected to torture",
    some "{0} to be subjected to cruel, inhuman or degrading treatment or punishment"]
-- D-20: a joined act with no rule on it or its dual; a rule on another predicate does not read it.
#guard refusal (withActs (doc [rg "p" .permission, rg "k" .permission] [nd "rk" "k" false]) fx6 [("p", g6)]) ==
  some "InvalidInput: the joined act of p has no rule to read it by"
-- D-22: *need not*; a split marker's *or* under *must* (T8); an *or* under *must* is one act, kept unchanged.
#guard refusal (withActs (doc [rg "p" .obligation] [nd "r" "p" false]) fx6 [("p", g6)]) ==
  some "InvalidInput: rule r has no reading of its act; rewrite it"
#guard refusal (withActs (doc [rg "p" .obligation] [nd "r" "p" true]) fx6 [("p", g6)]) ==
  some "InvalidInput: rule r has no reading of its act; rewrite it"
#guard (shown (elaborateMap (withActs (doc [rg "p" .obligation] [nd "r" "p" true]) fx11 [("p", g11)]))).toOption ==
  some ([rg "p" .obligation], [nd "r" "p" true], [], ⟨[], []⟩)
-- The first failing rule in document order: D-22 before D-21, D-21 before D-22.
#guard refusal (withActs (doc [rg "p" .obligation, rg "k" .plain none] [nd "r" "p" false, nd "s" "p" true]) fx6
  [("p", g6)]) == some "InvalidInput: rule r has no reading of its act; rewrite it"
#guard refusal (withActs (doc [rg "p" .plain none] [nd "s" "p" false, nd "r" "p" true]) fx6 [("p", .any true false [torture, cruel])]) ==
  some "InvalidInput: rule s has no modal word for a joined act"
-- A rule on an undeclared predicate has no op.
#guard refusal (withActs (doc [] [nd "r" "p" true]) fx6 [("p", g6)]) ==
  some "InvalidInput: rule r has no modal word for a joined act"

/-- E7: obligation `q`, dual `qm`, act "use [the tool] or provide [the data]"; *must* keeps one act, *must not* splits. -/
def useA : Atom := ⟨false, false, ["use"], [("", .one (.fixed 0))], []⟩
def provideA : Atom := ⟨false, false, ["provide"], [("", .one (.fixed 1))], []⟩
def e7 (A : Act) (first : String) : ActsDoc :=
  withActs (doc [rg "q" .obligation (some "{0} use") (some "qm"), rg "qm" .permission (some "{0} use")]
    [nd "rq" "q" true, nd "rqm" "qm" false]) ["the tool", "the data"]
    (if first == "q" then [("q", A), ("qm", A)] else [("qm", A), ("q", A)])
#guard refusal (e7 (.any false false [useA, provideA]) "q") ==
  some "InvalidInput: the rules on q and its dual read its act differently; write the parts as separate predicates"
#guard refusal (e7 (.any false false [useA, provideA]) "qm") ==
  some "InvalidInput: the rules on qm and its dual read its act differently; write the parts as separate predicates"
-- The same reading on both (a split marker's *and*): both split, each part's dual is the dual's part.
#guard (shown (elaborateMap (e7 (.all false true [useA, provideA]) "q"))).toOption.map
  (·.1.map (fun r => (r.name, r.permission))) ==
  some [("q__1", some "qm__1"), ("q__2", some "qm__2"), ("qm__1", none), ("qm__2", none)]
-- A dual that does not split: the parts' duals are missing, refused by `validate` (step 5).
#guard refusal ({ e7 (.all false true [useA, provideA]) "q" with acts := [("q", .all false true [useA, provideA])] }) ==
  some "MissingPermissionDual: q__1, qm__1"

-- A join of one atom reads as one atom and does not split; two atoms split.
#guard (shown (elaborateMap (withActs (doc [rg "p" .plain none] [nd "r" "p" true]) [] [("p", .all false false [join])]))).toOption ==
  some ([rg "p" .plain none], [nd "r" "p" true], [], ⟨[], []⟩)
#guard (shown (elaborateMap (withActs (doc [rg "p" .plain none] [nd "r" "p" true]) [] [("p", g12 false)]))).toOption.map
  (·.2.2.2.preds.length) == some 2

/-! ### Step 2: a formula naming a split predicate (D-25) -/

/-- E6: E1 plus obligation `s` whose rule's guard, or carve-out, or a definition, names `p027` (or `b`). -/
def e6 (guard : VE.Formula) (carve : List VE.Formula := []) (defs : List Definition := []) : ActsDoc :=
  withActs (doc [rg "p027" .permission, rg "s" .obligation] [nd "r027" "p027" false, nd "rs" "s" true [] guard carve]
    (defs := defs) (extra := ["b", "d"])) fx6 [("p027", g6)]
#guard refusal (e6 (.unary "p027" (.var 0))) ==
  some "InvalidInput: rule rs names a predicate that is split into parts; name one of its parts"
#guard refusal (e6 .top [.not (.unary "p027" (.var 0))]) ==
  some "InvalidInput: rule rs names a predicate that is split into parts; name one of its parts"
#guard refusal (e6 .top (defs := [⟨"d", ["person"], .ex "person" (.unary "p027" (.var 0))⟩])) ==
  some "InvalidInput: definition d names a predicate that is split into parts; name one of its parts"
#guard refusal (e6 (.unary "b" (.var 0)) [.unary "d" (.var 0)]) == none

/-! ### Step 3: the generated names (D-26) -/

/-- E8: a 62-byte source name gives 65-byte parts; 61 bytes give 64. -/
def named (p r : String) : ActsDoc := withActs (doc [rg p .permission] [nd r p false]) fx6 [(p, g6)]
#guard refusal (named (String.mk (List.replicate 62 'p')) "r") ==
  some ("ResourceLimit: the part name " ++ String.mk (List.replicate 62 'p') ++ "__1 is over 64 bytes")
#guard refusal (named (String.mk (List.replicate 61 'p')) "r") == none
#guard refusal (named "p" (String.mk (List.replicate 62 'r'))) ==
  some ("ResourceLimit: the part rule name " ++ String.mk (List.replicate 62 'r') ++ "-a1 is not a rule name of at most 64 bytes")
#guard refusal (named "p" (String.mk (List.replicate 61 'r'))) == none
-- A part name declared in the environment, as a regulated predicate, as unspecified, or by another part.
def hideEnv (D : ActsDoc) (ps : List (String × List String)) : ActsDoc :=
  { D with U := { D.U with D := { D.U.D with E := env ps } } }
#guard refusal (withActs (doc [rg "p027" .permission] [nd "r027" "p027" false] (extra := ["p027__1"])) fx6
  [("p027", g6)]) == some "InvalidInput: the part name p027__1 is already declared"
#guard refusal (hideEnv (withActs (doc [rg "p027" .permission, rg "p027__2" .plain none] [nd "r027" "p027" false]) fx6
  [("p027", g6)]) [("p027", ["person"])]) == some "InvalidInput: the part name p027__2 is already declared"
#guard refusal (withActs (doc [rg "p027" .permission] [nd "r027" "p027" false] ["p027__1"]) fx6 [("p027", g6)]) ==
  some "InvalidInput: the part name p027__1 is already declared"
#guard refusal (withActs (doc [rg "p027" .permission, rg "p027" .permission] [nd "r027" "p027" false]) fx6
  [("p027", g6)]) == some "InvalidInput: the part name p027__1 is already declared"
-- A part rule name used by a source rule or by another part rule.
#guard refusal (withActs (doc [rg "p027" .permission, rg "s" .obligation] [nd "r027" "p027" false, nd "r027-a2" "s" true])
  fx6 [("p027", g6)]) == some "InvalidInput: the part rule name r027-a2 is already used"
#guard refusal (withActs (doc [rg "p027" .permission] [nd "r027" "p027" false, nd "r027" "p027" false]) fx6
  [("p027", g6)]) == some "InvalidInput: the part rule name r027-a1 is already used"

/-! ### Step 4: two parts with one act (D-27) -/

/-- E16: plain `p`, "{0} to seek asylum and to seek asylum" (two equal atoms), *has the right to*: refused. -/
def seek : Atom := ⟨true, false, ["seek"], [("", .one (w "asylum"))], []⟩
#guard refusal (withActs (doc [rg "p" .plain none] [nd "r" "p" true]) [] [("p", .all false false [seek, seek])]) ==
  some "InvalidInput: two parts of p are the same act"
#guard refusal (withActs (doc [rg "p" .permission] [nd "r" "p" false]) fx6 [("p", .any false true [torture, torture])]) ==
  some "InvalidInput: two parts of p are the same act"
#guard refusal (withActs (doc [rg "p" .plain none] [nd "r" "p" true]) [] [("p", .all false false [seek, join])]) == none

/-! ### Step 5: `validate` on the result (E12's boundary) and step 7, the backstop -/

def many (n : Nat) : List Regulated := (List.range n).map fun i => rg ("b" ++ toString i) .plain none
#guard refusal (withActs (doc (many 62 ++ [rg "p027" .permission]) [nd "r027" "p027" false]) fx6 [("p027", g6)]) == none
#guard refusal (withActs (doc (many 63 ++ [rg "p027" .permission]) [nd "r027" "p027" false]) fx6 [("p027", g6)]) ==
  some "ResourceLimit: regulated predicates"
-- An unspecified name that is not regulated; a source rule name kept beside its split twin.
#guard refusal (withActs (doc [rg "p027" .permission] [nd "r027" "p027" false] ["zzz"]) fx6 [("p027", g6)]) ==
  some "InvalidInput: the elaborated document is not well formed"
#guard refusal (withActs (doc [rg "p027" .permission, rg "k" .obligation] [nd "r" "p027" false, nd "r" "k" true]) fx6
  [("p027", g6)]) == some "InvalidInput: the elaborated document is not well formed"

/-! ### The order of the steps: the first failing step's text -/

#guard refusal ({ e6 (.unary "p027" (.var 0)) with acts := [("p027", g6), ("z", g6)] }) ==
  some "InvalidInput: the joined act of z has no rule to read it by"
#guard refusal (withActs (doc [rg "p027" .permission, rg "s" .obligation] [nd "r027" "p027" false,
  nd "rs" "s" true [] (.unary "p027" (.var 0))] (extra := ["p027__1"])) fx6 [("p027", g6)]) ==
  some "InvalidInput: rule rs names a predicate that is split into parts; name one of its parts"
#guard refusal (withActs (doc [rg "p" .plain none] [nd "r" "p" true] (extra := ["p__1"])) []
  [("p", .all false false [seek, seek])]) == some "InvalidInput: the part name p__1 is already declared"
#guard refusal (withActs (doc (many 63 ++ [rg "p" .plain none]) [nd "r" "p" true]) []
  [("p", .all false false [seek, seek])]) == some "InvalidInput: two parts of p are the same act"
#guard refusal (withActs (doc (many 63 ++ [rg "p027" .permission]) [nd "r027" "p027" false] ["zzz"]) fx6
  [("p027", g6)]) == some "ResourceLimit: regulated predicates"

end VE.Acts.ElaborateExamples
