import VE.Grammar.Meaning
import VE.Grammar.Reading
import VE.Grammar.Extension
import VE.EnglishGrammar.Token

/-! The engine corpus run with the English tokens and terminals (docs/spec/english-lean.md 8.1 to 8.3
and 8.7; `conformance/english-lean/engine.json`). Each check runs the executable parser; the expected
results are the hand-derived ones of the specification. g18 (random grammars against an exhaustive
enumerator) stays with the Python reference harness. -/

namespace VE.EnglishGrammar.EngineExamples
open VE.Grammar VE.EnglishGrammar

def a : Sym Terminal := .t (.kw "a")
def b : Sym Terminal := .t (.kw "b")
def c : Sym Terminal := .t (.kw "c")
def x : Sym Terminal := .t (.kw "x")
def z : Sym Terminal := .t (.kw "z")
def N (A : Nat) : Sym Terminal := .n A

def rl (lhs : Nat) (rhs : List (Sym Terminal)) (act : Nat := 0) : Rule Terminal :=
  { lhs, rhs, act, tag := "" }

def gr (rules : List (Rule Terminal)) (rank : List Nat) : Grammar Terminal :=
  { rules := rules.toArray, start := 0, rank := rank.toArray }

def ws (l : List String) : Array Tok := (l.map fun s => Tok.word s false).toArray
def lf (s : String) : Tree Tok := .leaf (.word s false)
def nd (r : Nat) (ks : List (Tree Tok)) : Tree Tok := .node r ks

def big : Nat := 1000000

-- Nonterminals: S 0, then A 1, B 2, C 3 (N 1 in G6).
def G1 := gr [rl 0 [a, N 1], rl 1 [b] 1] [0, 0]
def G2 := gr [rl 0 [x], rl 0 [x]] [0]
def G3 := gr [rl 0 [N 1, N 2], rl 1 [a], rl 1 [a, a], rl 2 [a], rl 2 [a, a]] [1, 0, 0]
def G4 := gr [rl 0 [N 1, N 2, N 3], rl 1 [a], rl 1 [a, a], rl 2 [a], rl 2 [a, a], rl 3 [a], rl 3 [a, a]]
  [1, 0, 0, 0]
def G5 := gr [rl 0 [N 1], rl 1 [N 2], rl 2 [x]] [2, 1, 0]
def G6 := gr [rl 0 [.t (.kw "every"), N 1], rl 1 [.t (.content "service")], rl 1 [.t (.exact (.quoted "svc"))],
  rl 1 [.t (.cls (.label "S"))], rl 1 [.t (.cls .numeral)]] [0, 0]
def G17 := gr [rl 0 [N 1, N 1, N 1, N 1, N 1, N 1, N 1, N 1, z], rl 1 [a], rl 1 [a, a]] [1, 0]
def G20 := gr [rl 0 [N 1, N 1, N 1], rl 0 [N 1, N 1, N 1], rl 1 [N 2, N 2], rl 2 [a], rl 2 [a]] [2, 1, 0]

-- g1, g2
#guard parse G1 2 big (ws ["a", "b"]) == some [nd 0 [lf "a", nd 1 [lf "b"]]]
#guard [["a"], ["a", "b", "b"], ["b", "a"], []].all fun i => parse G1 2 big (ws i) == some []
-- g3: two rules equal as data are two derivations
#guard parse G2 2 big (ws ["x"]) == some [nd 0 [lf "x"], nd 1 [lf "x"]]
-- g4 to g6
#guard parse G3 2 big (ws ["a", "a"]) == some [nd 0 [nd 1 [lf "a"], nd 3 [lf "a"]]]
#guard (parse G3 2 big (ws ["a", "a", "a"])).map (·.length) == some 2
#guard (parse G3 2 big (ws ["a", "a", "a"])).all fun ts =>
  ts.all (· ∈ [nd 0 [nd 1 [lf "a"], nd 4 [lf "a", lf "a"]], nd 0 [nd 2 [lf "a", lf "a"], nd 3 [lf "a"]]])
#guard parse G3 2 big (ws ["a", "a", "a", "a"]) == some [nd 0 [nd 2 [lf "a", lf "a"], nd 4 [lf "a", lf "a"]]]
-- g7 to g9
def g7trees : List (Tree Tok) :=
  [nd 0 [nd 1 [lf "a"], nd 3 [lf "a"], nd 6 [lf "a", lf "a"]],
   nd 0 [nd 1 [lf "a"], nd 4 [lf "a", lf "a"], nd 5 [lf "a"]],
   nd 0 [nd 2 [lf "a", lf "a"], nd 3 [lf "a"], nd 5 [lf "a"]]]
#guard (parse G4 4 big (ws ["a", "a", "a", "a"])).all fun ts => ts.length == 3 && g7trees.all (· ∈ ts)
#guard (parse G4 2 big (ws ["a", "a", "a", "a"])).all fun ts =>
  ts.length == 2 && ts.all (· ∈ g7trees) && ts[0]? != ts[1]?
#guard (parse G4 3 big (ws ["a", "a", "a", "a"])).all fun ts => ts.length == 3 && g7trees.all (· ∈ ts)
-- g10: a chain of unit rules with decreasing rank
#guard parse G5 2 big (ws ["x"]) == some [nd 0 [nd 1 [nd 2 [lf "x"]]]]
-- g11 to g14: the matching of 2.3
def kidRule (ts : Option (List (Tree Tok))) : Option Nat :=
  match ts with
  | some [.node 0 [_, .node r _]] => some r
  | _ => none
#guard [ws ["every", "service"], #[.word "Every" true, .word "Service" false], ws ["every", "SERVICE"],
  ws ["every", "ſervice"]].all fun i => kidRule (parse G6 2 big i) == some 1
#guard [ws ["Every", "service"], #[.word "EVERY" true, .word "service" false], ws ["every", "services"]].all
  fun i => parse G6 2 big i == some []
#guard kidRule (parse G6 2 big #[.word "every" false, .quoted "svc"]) == some 2
#guard kidRule (parse G6 2 big #[.word "every" false, .label "S" 3]) == some 3
#guard kidRule (parse G6 2 big #[.word "every" false, .numeral 7]) == some 4
#guard [#[.word "every" false, .quoted "SVC"], #[.word "every" false, .label "T" 3], ws ["every", "svc"]].all
  fun i => parse G6 2 big i == some []
-- g15: not well-formed
#guard !(gr [rl 0 [N 0, x], rl 0 [x]] [0]).wf
#guard !(gr [rl 0 [N 0, x], rl 0 [x]] [5]).wf
#guard !(gr [rl 0 [], rl 0 [x]] [0]).wf
#guard !(gr [rl 0 [N 1], rl 1 [N 2], rl 2 [N 1]] [2, 1, 0]).wf
#guard !(gr [rl 0 [N 1]] [0]).wf
#guard !({ rules := #[rl 0 [x]], start := 1, rank := #[0] } : Grammar Terminal).wf
-- g16: no result below the threshold, the result of g5 from it on
def g16 (budget : Nat) : Option (List (Tree Tok)) := parse G3 2 budget (ws ["a", "a", "a"])
#guard (List.range 49).all fun k => g16 k == none
#guard (List.range 40).all fun k => g16 (49 + k) == g16 big
#guard (g16 49).isSome
-- g17: forty `a` with no `z`
#guard parse G17 2 big (ws (List.replicate 40 "a")) == some []
#guard G17.prepare.steps 2 big (ws (List.replicate 40 "a")) == some 599
-- g20: saturation
#guard (parse G20 64 big (ws (List.replicate 6 "a"))).map (·.length) == some 64
#guard (parse G20 129 big (ws (List.replicate 6 "a"))).map (·.length) == some 128

-- 8.2: meanings. Types: `tok` (false) and `num` (true).
def sigA : Sig Tok where
  Ty := Bool
  decEq := inferInstance
  Sem := fun
    | true => Nat
    | false => Tok
  tok := false
  leaf := fun t => t

def numeralOf : Tok → Nat
  | .numeral v => v.toNat
  | _ => 0

def actNum : Action sigA := { args := [false], out := true, run := fun (t, ()) => numeralOf t }
def actSum : Action sigA :=
  { args := [false, true, false, true, false], out := true, run := fun (_, m, _, n, _, ()) =>
    ((show Nat from m) + (show Nat from n) : Nat) }
def actSum3 : Action sigA := { args := [false, true, false], out := true, run := fun (_, m, _, ()) => (show Nat from m) }

def pu (s : String) : Sym Terminal := .t (.exact (.punct s false false))
def GA := gr [rl 0 [.t (.cls .numeral)] 0, rl 0 [pu "(", N 0, pu "+", N 0, pu ")"] 1] [0]
def GA4 := gr [rl 0 [.t (.cls .numeral)] 0, rl 0 [pu "(", N 0, pu "+", N 0, pu ")"] 7] [0]
def tyA : Nat → Bool := fun _ => true
def m2input : Array Tok :=
  #[.punct "(" false false, .numeral 1, .punct "+" false false, .punct "(" false false, .numeral 2,
    .punct "+" false false, .numeral 3, .punct ")" false false, .punct ")" false false]

def valueOf (acts : Array (Action sigA)) : Option Nat :=
  match parse GA 2 big m2input with
  | some [t] =>
    match t.sem GA sigA acts with
    | some ⟨true, v⟩ => some v
    | _ => none
  | _ => none

-- m1 to m5
#guard GA.typed sigA tyA #[actNum, actSum]
#guard valueOf #[actNum, actSum] == some 6
#guard !GA.typed sigA tyA #[actNum, actSum3]
#guard !GA4.typed sigA tyA #[actNum, actSum]
#guard valueOf #[actNum, actSum3] == none

-- 8.3: sentences, documents and the state
def mu1 : Meaning Tok Nat String Nat := fun k _ => .ok (k, false, k + 1)
def mu2 : Meaning Tok Nat String Nat := fun _ _ => .error "no"

def outName : Outcome Tok String Nat × Nat → String × Nat
  | (.ok v m, s) => (s!"ok {v} {m}", s)
  | (.noDerivation, s) => ("noDerivation", s)
  | (.ambiguous _ _, s) => ("ambiguous", s)
  | (.rejected r, s) => (s!"rejected {r}", s)
  | (.budget, s) => ("budget", s)

#guard outName (readSentence G1 mu1 5 big (ws ["a", "b"])) == ("ok 5 false", 6)
#guard outName (readSentence G1 mu1 5 big (ws ["a"])) == ("noDerivation", 5)
#guard (match readSentence G2 mu1 5 big (ws ["x"]) with
  | (.ambiguous t u, 5) => t == nd 0 [lf "x"] && u == nd 1 [lf "x"]
  | _ => false)
#guard outName (readSentence G1 mu2 5 big (ws ["a", "b"])) == ("rejected no", 5)
#guard outName (readSentence G3 mu1 5 40 (ws ["a", "a", "a"])) == ("budget", 5)

def docName : DocOutcome Tok String Nat × Nat → String × Nat
  | (.ok rs, s) => (s!"ok {rs}", s)
  | (.stopped i o, s) => (s!"stopped {i} {(outName (o, s)).1}", s)

#guard docName (readDocument G1 mu1 0 big [ws ["a", "b"], ws ["a", "b"], ws ["a", "b"]]) ==
  ("ok [(0, false), (1, false), (2, false)]", 3)
#guard docName (readDocument G1 mu1 0 big [ws ["a", "b"], ws ["a"], ws ["a", "b"]]) == ("stopped 1 noDerivation", 1)
#guard docName (readDocument G1 mu1 0 big []) == ("ok []", 0)
-- r9: two trees with the same value are still two readings
def mu9 : Meaning Tok Nat String Nat := fun _ _ => .ok (0, false, 1)
#guard outName (readSentence G3 mu9 0 big (ws ["a", "a", "a"])) == ("ambiguous", 0)
#guard (parse G3 2 big (ws ["a", "a", "a"])).map (fun ts => readingSet mu9 0 ts) == some [(0, false, 1), (0, false, 1)]
-- r10: translation mode; a rejected meaning shortens the set, and the set is not complete
def mu10 : Meaning Tok Nat String Nat := fun _ t => if t == nd 0 [lf "x"] then .ok (0, false, 1) else .error "no"
#guard (parse G2 2 big (ws ["x"])).map (fun ts => (decide (ts.length < 2), readingSet mu10 0 ts)) == some (false, [(0, false, 1)])

-- 8.7: extensions. q2: the larger grammar makes `a b` ambiguous; q3: the swapped grammar.
def G1ab := gr [rl 0 [a, N 1], rl 1 [b] 1, rl 0 [a, b] 3] [0, 0]
def G1swap := gr [rl 1 [b] 1, rl 0 [a, N 1]] [0, 0]
def G1c := gr [rl 0 [a, N 1], rl 1 [b] 1, rl 0 [c] 2] [0, 0]
#guard parse G1c 2 big (ws ["a", "b"]) == some [nd 0 [lf "a", nd 1 [lf "b"]]]
#guard (parse G1ab 2 big (ws ["a", "b"])).map (·.length) == some 2
#guard parse G1swap 2 big (ws ["a", "b"]) == some [nd 1 [lf "a", nd 0 [lf "b"]]]
#guard (RuleMap.tree ⟨fun r => 1 - r, id⟩ (nd 0 [lf "a", nd 1 [lf "b"]]) : Tree Tok) == nd 1 [lf "a", nd 0 [lf "b"]]

end VE.EnglishGrammar.EngineExamples
