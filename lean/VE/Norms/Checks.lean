import VE.Norms.SmallModel
import VE.Route.Wire

/-! Executable checks for W1 norms (docs/spec/norms.md 10.1, 10.9, 10.11).

The first block compares Lean's regenerated elaborations, conflict formulas and
profile premises byte-for-byte with Python `ve/norms.py` on five documents
(the strings are Python's compact JSON output). The second block runs the
deterministic regressions of 10.1 on finite base models through the total
evaluator (`Formula.eval`, equal to `denote` by `eval_iff_denote`), including
the prefix-admissibility checks of (m), (n) and (o) through
`prefix_satisfaction` (a finite structure is prefix-admissible iff it is
admissible, base-admissible below and satisfies `PrefixPremises`). -/
namespace VE.Norms.Checks
open VE.Norms

def envOf (sorts : List String) (preds : List (String × List String)) : VE.Environment where
  sorts := sorts
  predicates p := (preds.find? (·.1 == p)).map Prod.snd
  constants _ := none

def perm (n : String) (sorts : List String) (allow : Bool) (act : String := "{0} be done") : Regulated :=
  ⟨n, sorts, allow, .permission, some act, none⟩

def oblig (n : String) (sorts : List String) (allow : Bool) (dual : Option String)
    (act : String := "{0} be done") : Regulated :=
  ⟨n, sorts, allow, .obligation, some act, dual⟩

def plain (n : String) (sorts : List String) (allow : Bool) : Regulated :=
  ⟨n, sorts, allow, .plain, none, none⟩

def rule (name pred : String) (sign : Bool) (guard : VE.Formula := .top)
    (carve : List VE.Formula := []) (over : List String := []) : Node :=
  ⟨name, pred, sign, guard, carve, over⟩

def u (p : String) : VE.Formula := .unary p (.var 0)

def enc (a : VE.Formula) : String := (VE.Route.Wire.encodeFormula a).compress

def conflictTargets (D : Doc) : List String :=
  (syms D.T).filterMap (fun | .reg r => some (enc (conflict D r)) | .defn _ => none) ++
    (pairs D.T).map (fun pr => enc (pairConflict D pr))

def mkDoc (sorts : List String) (base : List (String × List String)) (regs : List Regulated)
    (defs : List Definition) (nodes : List Node) : Doc where
  E := envOf sorts (base ++ regs.map (fun r => (r.name, r.sorts)) ++ defs.map (fun d => (d.name, d.args)))
  lits := []
  T := ⟨regs, defs, nodes⟩

def act : List String := ["act"]

def doc_c : Doc := mkDoc act [] [oblig "required" act false (some "permitted"), perm "permitted" act false] []
  [rule "must" "required" true, rule "may" "permitted" true]
def doc_d : Doc := mkDoc act [] [perm "permitted" act false] []
  [rule "r1" "permitted" false, rule "r2" "permitted" false (over := ["r1"]),
   rule "r3" "permitted" true (over := ["r2"])]
def doc_r : Doc := mkDoc act [("monday", act), ("on_call", act)] [perm "permitted" act false] []
  [rule "ban" "permitted" false (u "monday"),
   rule "release" "permitted" true (u "on_call") [u "monday"] ["ban"]]
def doc_t : Doc := mkDoc ["state", "person"] [("relation", ["state", "person"])]
  [perm "permitted" ["state", "person"] false "{0} help {1}"] []
  [rule "yes" "permitted" true (.binary "relation" (.var 1) (.var 0)),
   rule "no" "permitted" false (.binary "relation" (.var 1) (.var 0))]
def doc_p : Doc := mkDoc act [] [oblig "required" act false (some "permitted"), perm "permitted" act false] []
  [rule "need" "required" true (u "permitted"), rule "may" "permitted" true]

-- document (c): Python ve/norms.py premises, conflict targets and profile premises
#guard WellFormed doc_c
#guard layerNames doc_c.T == ["permitted", "required"]
#guard (elaborate doc_c.T).map enc == ["[\"forall\",\"act\",[\"and\",[\"and\",[\"and\",[\"top\"],[\"implies\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]],[\"unary\",\"permitted\",[\"var\",0]]]],[\"implies\",[\"bottom\"],[\"not\",[\"unary\",\"permitted\",[\"var\",0]]]]],[\"implies\",[\"and\",[\"not\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]]],[\"not\",[\"bottom\"]]],[\"not\",[\"unary\",\"permitted\",[\"var\",0]]]]]]", "[\"forall\",\"act\",[\"and\",[\"and\",[\"and\",[\"top\"],[\"implies\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]],[\"unary\",\"required\",[\"var\",0]]]],[\"implies\",[\"bottom\"],[\"not\",[\"unary\",\"required\",[\"var\",0]]]]],[\"implies\",[\"and\",[\"not\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]]],[\"not\",[\"bottom\"]]],[\"not\",[\"unary\",\"required\",[\"var\",0]]]]]]"]
#guard conflictTargets doc_c == ["[\"and\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]],[\"bottom\"]]", "[\"and\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]],[\"bottom\"]]", "[\"and\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]],[\"not\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]]]]"]
#guard (pairPremises doc_c.T).map enc == ["[\"forall\",\"act\",[\"implies\",[\"unary\",\"required\",[\"var\",0]],[\"unary\",\"permitted\",[\"var\",0]]]]"]

-- document (d): Python ve/norms.py premises, conflict targets and profile premises
#guard WellFormed doc_d
#guard layerNames doc_d.T == ["permitted"]
#guard (elaborate doc_d.T).map enc == ["[\"forall\",\"act\",[\"and\",[\"and\",[\"and\",[\"top\"],[\"implies\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]],[\"unary\",\"permitted\",[\"var\",0]]]],[\"implies\",[\"or\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"or\",[\"bottom\"],[\"or\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"or\",[\"bottom\"],[\"or\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"bottom\"]]]]]]]],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"or\",[\"bottom\"],[\"or\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"bottom\"]]]]]],[\"not\",[\"unary\",\"permitted\",[\"var\",0]]]]],[\"implies\",[\"and\",[\"not\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]]],[\"not\",[\"or\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"or\",[\"bottom\"],[\"or\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"or\",[\"bottom\"],[\"or\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"bottom\"]]]]]]]],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"or\",[\"bottom\"],[\"or\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"bottom\"]]]]]]]],[\"not\",[\"unary\",\"permitted\",[\"var\",0]]]]]]"]
#guard conflictTargets doc_d == ["[\"and\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]],[\"or\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"or\",[\"bottom\"],[\"or\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"or\",[\"bottom\"],[\"or\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"bottom\"]]]]]]]],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"or\",[\"bottom\"],[\"or\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"bottom\"]]]]]]]"]
#guard (pairPremises doc_d.T).map enc == []

-- document (r): Python ve/norms.py premises, conflict targets and profile premises
#guard WellFormed doc_r
#guard layerNames doc_r.T == ["permitted"]
#guard (elaborate doc_r.T).map enc == ["[\"forall\",\"act\",[\"and\",[\"and\",[\"and\",[\"top\"],[\"implies\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"unary\",\"on_call\",[\"var\",0]],[\"not\",[\"or\",[\"bottom\"],[\"unary\",\"monday\",[\"var\",0]]]]],[\"not\",[\"bottom\"]]]],[\"unary\",\"permitted\",[\"var\",0]]]],[\"implies\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"unary\",\"monday\",[\"var\",0]],[\"not\",[\"bottom\"]]],[\"not\",[\"or\",[\"bottom\"],[\"or\",[\"and\",[\"unary\",\"on_call\",[\"var\",0]],[\"not\",[\"or\",[\"bottom\"],[\"unary\",\"monday\",[\"var\",0]]]]],[\"bottom\"]]]]]],[\"not\",[\"unary\",\"permitted\",[\"var\",0]]]]],[\"implies\",[\"and\",[\"not\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"unary\",\"on_call\",[\"var\",0]],[\"not\",[\"or\",[\"bottom\"],[\"unary\",\"monday\",[\"var\",0]]]]],[\"not\",[\"bottom\"]]]]],[\"not\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"unary\",\"monday\",[\"var\",0]],[\"not\",[\"bottom\"]]],[\"not\",[\"or\",[\"bottom\"],[\"or\",[\"and\",[\"unary\",\"on_call\",[\"var\",0]],[\"not\",[\"or\",[\"bottom\"],[\"unary\",\"monday\",[\"var\",0]]]]],[\"bottom\"]]]]]]]],[\"not\",[\"unary\",\"permitted\",[\"var\",0]]]]]]"]
#guard conflictTargets doc_r == ["[\"and\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"unary\",\"on_call\",[\"var\",0]],[\"not\",[\"or\",[\"bottom\"],[\"unary\",\"monday\",[\"var\",0]]]]],[\"not\",[\"bottom\"]]]],[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"unary\",\"monday\",[\"var\",0]],[\"not\",[\"bottom\"]]],[\"not\",[\"or\",[\"bottom\"],[\"or\",[\"and\",[\"unary\",\"on_call\",[\"var\",0]],[\"not\",[\"or\",[\"bottom\"],[\"unary\",\"monday\",[\"var\",0]]]]],[\"bottom\"]]]]]]]"]
#guard (pairPremises doc_r.T).map enc == []

-- document (t): Python ve/norms.py premises, conflict targets and profile premises
#guard WellFormed doc_t
#guard layerNames doc_t.T == ["permitted"]
#guard (elaborate doc_t.T).map enc == ["[\"forall\",\"state\",[\"forall\",\"person\",[\"and\",[\"and\",[\"and\",[\"top\"],[\"implies\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"binary\",\"relation\",[\"var\",1],[\"var\",0]],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]],[\"binary\",\"permitted\",[\"var\",1],[\"var\",0]]]],[\"implies\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"binary\",\"relation\",[\"var\",1],[\"var\",0]],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]],[\"not\",[\"binary\",\"permitted\",[\"var\",1],[\"var\",0]]]]],[\"implies\",[\"and\",[\"not\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"binary\",\"relation\",[\"var\",1],[\"var\",0]],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]]],[\"not\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"binary\",\"relation\",[\"var\",1],[\"var\",0]],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]]]],[\"not\",[\"binary\",\"permitted\",[\"var\",1],[\"var\",0]]]]]]]"]
#guard conflictTargets doc_t == ["[\"and\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"binary\",\"relation\",[\"var\",1],[\"var\",0]],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]],[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"binary\",\"relation\",[\"var\",1],[\"var\",0]],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]]]"]
#guard (pairPremises doc_t.T).map enc == []

-- document (p): Python ve/norms.py premises, conflict targets and profile premises
#guard WellFormed doc_p
#guard layerNames doc_p.T == ["permitted", "required"]
#guard (elaborate doc_p.T).map enc == ["[\"forall\",\"act\",[\"and\",[\"and\",[\"and\",[\"top\"],[\"implies\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]],[\"unary\",\"permitted\",[\"var\",0]]]],[\"implies\",[\"bottom\"],[\"not\",[\"unary\",\"permitted\",[\"var\",0]]]]],[\"implies\",[\"and\",[\"not\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]]],[\"not\",[\"bottom\"]]],[\"not\",[\"unary\",\"permitted\",[\"var\",0]]]]]]", "[\"forall\",\"act\",[\"and\",[\"and\",[\"and\",[\"top\"],[\"implies\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"unary\",\"permitted\",[\"var\",0]],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]],[\"unary\",\"required\",[\"var\",0]]]],[\"implies\",[\"bottom\"],[\"not\",[\"unary\",\"required\",[\"var\",0]]]]],[\"implies\",[\"and\",[\"not\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"unary\",\"permitted\",[\"var\",0]],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]]],[\"not\",[\"bottom\"]]],[\"not\",[\"unary\",\"required\",[\"var\",0]]]]]]"]
#guard conflictTargets doc_p == ["[\"and\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]],[\"bottom\"]]", "[\"and\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]],[\"bottom\"]]", "[\"and\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]],[\"not\",[\"or\",[\"bottom\"],[\"and\",[\"and\",[\"top\"],[\"not\",[\"bottom\"]]],[\"not\",[\"bottom\"]]]]]]"]
#guard (pairPremises doc_p.T).map enc == ["[\"forall\",\"act\",[\"implies\",[\"unary\",\"required\",[\"var\",0]],[\"unary\",\"permitted\",[\"var\",0]]]]"]
/-! ## 10.1 regressions on finite base models -/

def model (doms : List (String × List String)) (rels : List (String × List (List String))) :
    VE.FiniteModel String where
  domains s := ((doms.find? (·.1 == s)).map Prod.snd).getD []
  constants _ := none
  relations p := ((rels.find? (·.1 == p)).map Prod.snd).getD []

def regOf (D : Doc) (n : String) : Regulated := ((D.T.regulated.find? (·.name == n))).getD (perm n [] false)
def conflictAt (D : Doc) (n : String) (M : VE.FiniteModel String) (vs : List String) : Bool :=
  (conflict D (regOf D n)).eval M (tupleVal vs)
def pairConflictAt (D : Doc) (M : VE.FiniteModel String) (vs : List String) : Bool :=
  (pairs D.T).any (fun pr => (pairConflict D pr).eval M (tupleVal vs))
def outcomeAt (D : Doc) (n : String) (M : VE.FiniteModel String) (vs : List String) : Bool :=
  (outcomeBase D n).eval M (tupleVal vs)
def selectsAt (D : Doc) (N : String) (M : VE.FiniteModel String) (vs : List String) : Bool :=
  match D.T.nodes.find? (·.name == N) with
  | some n => (selects D.T (fuel D.T) n).eval M (tupleVal vs)
  | none => false
/-- By `prefix_satisfaction`, a finite structure admissible at `k` is
prefix-admissible exactly when this holds (with `Background_base` empty here). -/
def prefixSat (D : Doc) (k : Nat) (M : VE.FiniteModel String) : Bool :=
  (PrefixPremises D k).all (fun a => a.eval M [])
def diag (D : Doc) : String := match validate D with
  | .ok () => "ok"
  | .error e => e

def m1 : VE.FiniteModel String := model [("act", ["a"])] []

-- (a) required by an unconditional rule, permission deny-by-default with no rule: pair CONFLICT at a;
-- the permission's own intra-predicate test sees nothing.
def doc_a : Doc := mkDoc act [] [oblig "required" act false (some "permitted"), perm "permitted" act false] []
  [rule "must" "required" true]
#guard WellFormed doc_a
#guard pairConflictAt doc_a m1 ["a"]
#guard !conflictAt doc_a "permitted" m1 ["a"] && !conflictAt doc_a "required" m1 ["a"]

-- (b) required by default (allow), permission deny with no rule: pair CONFLICT at a.
def doc_b : Doc := mkDoc act [] [oblig "required" act true (some "permitted"), perm "permitted" act false] [] []
#guard WellFormed doc_b
#guard pairConflictAt doc_b m1 ["a"]

-- (c) adding "Every act may be done": no conflict at a; required and permitted.
#guard !pairConflictAt doc_c m1 ["a"] && !conflictAt doc_c "required" m1 ["a"]
#guard outcomeAt doc_c "required" m1 ["a"] && outcomeAt doc_c "permitted" m1 ["a"]

-- (d) grandchild: rule 3 yields, rules 2 and 1 do not select; outcome p(a).
#guard outcomeAt doc_d "permitted" m1 ["a"] && !conflictAt doc_d "permitted" m1 ["a"]
#guard selectsAt doc_d "r3" m1 ["a"] && !selectsAt doc_d "r2" m1 ["a"] && !selectsAt doc_d "r1" m1 ["a"]

-- (e) a guard mentioning its own predicate is a self-edge.
def doc_e : Doc := mkDoc act [] [plain "p" act true] [] [rule "r1" "p" true (.not (u "p"))]
#guard diag doc_e == "DependencyCycle: p"

-- (f) mutual precedence.
def doc_f : Doc := mkDoc act [] [perm "permitted" act false] []
  [rule "r1" "permitted" true (over := ["r2"]), rule "r2" "permitted" false (over := ["r1"])]
#guard diag doc_f == "DependencyCycle: r1, r2"

-- (g) precedence across predicates.
def doc_g : Doc := mkDoc act [] [perm "permitted" act false, plain "admitted" act true] []
  [rule "r5" "permitted" true, rule "r3" "admitted" false (over := ["r5"])]
#guard diag doc_g == "PrecedenceAcrossPredicates: rule r3 on admitted, rule r5 on permitted"

-- (i) carve-out versus exception, deny default, rule 6 forbids independently.
def c1 : VE.FiniteModel String := model [("act", ["a"])] [("cond", [["a"]])]
def doc_ia : Doc := mkDoc act [("cond", act)] [perm "permitted" act false] []
  [rule "r3" "permitted" false (carve := [u "cond"]), rule "r6" "permitted" false]
def doc_ib : Doc := mkDoc act [("cond", act)] [perm "permitted" act false] []
  [rule "r3" "permitted" false, rule "r4" "permitted" true (u "cond") (over := ["r3"]),
   rule "r6" "permitted" false]
#guard !outcomeAt doc_ia "permitted" c1 ["a"] && !conflictAt doc_ia "permitted" c1 ["a"]
#guard conflictAt doc_ib "permitted" c1 ["a"]
-- (w) without the independent rule 6: carve-out forbidden by default, exception permitted.
def doc_wa : Doc := mkDoc act [("cond", act)] [perm "permitted" act false] []
  [rule "r3" "permitted" false (carve := [u "cond"])]
def doc_wb : Doc := mkDoc act [("cond", act)] [perm "permitted" act false] []
  [rule "r3" "permitted" false, rule "r4" "permitted" true (u "cond") (over := ["r3"])]
#guard !outcomeAt doc_wa "permitted" c1 ["a"] && outcomeAt doc_wb "permitted" c1 ["a"]
#guard !conflictAt doc_wb "permitted" c1 ["a"]

-- (j) doctor on Monday: rule 6 (exception to 5) forbids unless on call; default deny.
def doc_j : Doc := mkDoc act [("on_call", act), ("monday", act)] [perm "permitted" act false] []
  [rule "r5" "permitted" true, rule "r6" "permitted" false (carve := [u "on_call"]) (over := ["r5"])]
#guard outcomeAt doc_j "permitted" (model [("act", ["a"])] [("on_call", [["a"]]), ("monday", [["a"]])]) ["a"]
#guard !outcomeAt doc_j "permitted" (model [("act", ["a"])] [("monday", [["a"]])]) ["a"]

-- (k) same-sign overlap is not a conflict; both rules select.
def doc_k : Doc := mkDoc act [] [perm "permitted" act false] []
  [rule "first" "permitted" true, rule "second" "permitted" true]
#guard !conflictAt doc_k "permitted" m1 ["a"] && selectsAt doc_k "first" m1 ["a"] &&
  selectsAt doc_k "second" m1 ["a"]

-- (m) obligation ordered first, both deny, no rules: an intermediate table with areq(a) is not
-- prefix-admissible; the valid prefix has it false and expands uniquely to both false.
def doc_m : Doc := mkDoc act [] [oblig "areq" act false (some "bperm"), perm "bperm" act false] [] []
#guard WellFormed doc_m && layerNames doc_m.T == ["areq", "bperm"]
#guard !prefixSat doc_m 1 (model [("act", ["a"])] [("areq", [["a"]])])
#guard prefixSat doc_m 1 m1 && prefixSat doc_m 2 m1
#guard !prefixSat doc_m 2 (model [("act", ["a"])] [("bperm", [["a"]])])
#guard !pairConflictAt doc_m m1 ["a"]

-- (n) permission ordered first (deny, no rules), obligation allow-by-default: the lower table with
-- aperm(a) is not prefix-admissible; the valid lower table has no full expansion; CONFLICT.
def doc_n : Doc := mkDoc act [] [perm "aperm" act false, oblig "breq" act true (some "aperm")] [] []
#guard WellFormed doc_n && layerNames doc_n.T == ["aperm", "breq"]
#guard !prefixSat doc_n 1 (model [("act", ["a"])] [("aperm", [["a"]])]) && prefixSat doc_n 1 m1
#guard !prefixSat doc_n 2 m1 && !prefixSat doc_n 2 (model [("act", ["a"])] [("breq", [["a"]])])
#guard pairConflictAt doc_n m1 ["a"]

-- (o) (c) with a definition eligible(x) ↔ permitted(x) between the permission and a required rule
-- guarded by eligible: the definition sits between them, the unique expansion satisfies every
-- premise, and changing the defined table breaks prefix admissibility.
def doc_o : Doc := mkDoc act [] [oblig "required" act false (some "permitted"), perm "permitted" act false]
  [⟨"eligible", act, u "permitted"⟩] [rule "must" "required" true (u "eligible"), rule "may" "permitted" true]
def full_o : VE.FiniteModel String :=
  model [("act", ["a"])] [("permitted", [["a"]]), ("eligible", [["a"]]), ("required", [["a"]])]
#guard WellFormed doc_o && layerNames doc_o.T == ["permitted", "eligible", "required"]
#guard prefixSat doc_o 3 full_o && (background doc_o ++ elaborate doc_o.T).all (fun a => a.eval full_o [])
#guard !prefixSat doc_o 2 (model [("act", ["a"])] [("permitted", [["a"]])])
#guard !pairConflictAt doc_o m1 ["a"] && outcomeAt doc_o "required" m1 ["a"]

-- (p) a required rule guarded by its paired permission: both true; without the permission rule both
-- false; conflict-free either way.
def doc_p' : Doc := mkDoc act [] [oblig "required" act false (some "permitted"), perm "permitted" act false] []
  [rule "need" "required" true (u "permitted")]
#guard outcomeAt doc_p "required" m1 ["a"] && outcomeAt doc_p "permitted" m1 ["a"] && !pairConflictAt doc_p m1 ["a"]
#guard !outcomeAt doc_p' "required" m1 ["a"] && !outcomeAt doc_p' "permitted" m1 ["a"] &&
  !pairConflictAt doc_p' m1 ["a"]

-- (q) diamond: only r4 selects; positive outcome.
def doc_q : Doc := mkDoc act [] [perm "permitted" act false] []
  [rule "r1" "permitted" false, rule "r2" "permitted" false (over := ["r1"]),
   rule "r3" "permitted" false (over := ["r1"]), rule "r4" "permitted" true (over := ["r2", "r3"])]
#guard ["r1", "r2", "r3", "r4"].filter (fun n => selectsAt doc_q n m1 ["a"]) == ["r4"]
#guard outcomeAt doc_q "permitted" m1 ["a"] && !conflictAt doc_q "permitted" m1 ["a"]

-- (r) on call on a Tuesday: the exception decides although its parent's guard fails.
#guard outcomeAt doc_r "permitted" (model [("act", ["a"])] [("on_call", [["a"]])]) ["a"]
#guard selectsAt doc_r "release" (model [("act", ["a"])] [("on_call", [["a"]])]) ["a"]

-- (s) a carved-out rule's subtree still yields through its descendant.
def doc_s : Doc := mkDoc act [] [perm "permitted" act false] []
  [rule "r1" "permitted" false, rule "r2" "permitted" false (carve := [.top]) (over := ["r1"]),
   rule "r3" "permitted" true (over := ["r2"])]
#guard ["r1", "r2", "r3"].filter (fun n => selectsAt doc_s n m1 ["a"]) == ["r3"]
#guard outcomeAt doc_s "permitted" m1 ["a"]

-- (t) argument order: the tuple [Texas, Ann] is evaluated at the valuation [Ann, Texas].
def mt : VE.FiniteModel String :=
  model [("state", ["Texas"]), ("person", ["Ann"])] [("relation", [["Texas", "Ann"]])]
def doc_t1 : Doc := mkDoc ["state", "person"] [("relation", ["state", "person"])]
  [perm "permitted" ["state", "person"] false "{0} help {1}"] []
  [rule "yes" "permitted" true (.binary "relation" (.var 1) (.var 0))]
#guard outcomeAt doc_t1 "permitted" mt ["Texas", "Ann"] && !conflictAt doc_t1 "permitted" mt ["Texas", "Ann"]
#guard conflictAt doc_t "permitted" mt ["Texas", "Ann"]
#guard tupleVal ["Texas", "Ann"] == ["Ann", "Texas"]

-- (v) same-act duals.
def doc_v1 : Doc := mkDoc act [] [oblig "must_enter" act false none "{0} enter", perm "may_enter" act false "{0} enter"] [] []
def doc_v2 : Doc := mkDoc act [] [oblig "must_enter" act false (some "may_leave") "{0} enter",
  perm "may_enter" act false "{0} enter", perm "may_leave" act false "{0} leave"] [] []
def doc_v3 : Doc := mkDoc act [] [perm "may_enter" act false "{0} enter", perm "can_enter" act false "{0} enter"] [] []
#guard diag doc_v1 == "MissingPermissionDual: must_enter, may_enter"
#guard diag doc_v2 == "DualActMismatch: must_enter, may_leave"
#guard diag doc_v3 == "DuplicateActRole: permission, {0} enter"
def doc_v4 : Doc := mkDoc act [] [oblig "must_enter" act false (some "may_enter") "{0} enter",
  perm "may_enter" act false "{0} enter"] [] [rule "must" "must_enter" true, rule "mustnot" "may_enter" false]
#guard WellFormed doc_v4 && pairConflictAt doc_v4 m1 ["a"]

-- Fragment membership: quantifier-free guards are in; an existential guard is out.
#guard InFragment doc_c && InFragment doc_t
def doc_x : Doc := mkDoc act [("cond", act)] [perm "permitted" act false] []
  [rule "r" "permitted" true (.ex "act" (u "cond"))]
#guard WellFormed doc_x && !InFragment doc_x

end VE.Norms.Checks
