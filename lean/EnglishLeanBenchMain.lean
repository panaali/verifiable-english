import Lean.Data.Json
import VE.Grammar.Table
import VE.EnglishGrammar.Lexer

/-! G1a measurement of the grammar engine (docs/spec/english-lean-PLAN.md section 5, S1a).

    lake build ve_english_lean_bench
    .lake/build/bin/ve_english_lean_bench <input.json> [repetitions]
    .lake/build/bin/ve_english_lean_bench --lex <sources.json>

The input lists grammars over the English tokens and terminals with sentences to read; it is written
by `bench/english_lean_g1a.py`. For each sentence the tool runs `parse` with cap 2 and a budget that
cannot be exhausted, and prints one JSON line: the number of tokens, the verdict, the steps of the
step counter of spec 2.6 and the least CPU time of the repetitions in microseconds.
With `--lex` it reads a JSON list of sources and prints, per source, the tokens of `lexSpans` with
their byte spans, or the rejection: the instrument of the lexer differential against the Python reference.
Measurement only: no admission path reads it.
-/

open Lean (Json toJson)
open VE.Grammar VE.EnglishGrammar

namespace EnglishLeanBench

def str (j : Json) : Except String String := j.getStr?
def nat (j : Json) : Except String Nat := j.getNat?
def arr (j : Json) : Except String (Array Json) := j.getArr?

def tok (j : Json) : Except String Tok := do
  let a ← arr j
  match a.toList with
  | [k, t, i] =>
    match ← str k with
    | "word" => return .word (← str t) ((← i.getBool?))
    | "label" => return .label (← str t) (← nat i)
    | other => throw s!"token kind {other}"
  | [k, t] =>
    match ← str k with
    | "quoted" => return .quoted (← str t)
    | "numeral" => return .numeral (← t.getInt?)
    | "punct" => return .punct (← str t) false false
    | other => throw s!"token kind {other}"
  | [k, t, b, c] =>
    match ← str k with
    | "punct" => return .punct (← str t) (← b.getBool?) (← c.getBool?)
    | other => throw s!"token kind {other}"
  | _ => throw "token shape"

def terminal (j : Json) : Except String Terminal := do
  let a ← arr j
  match a.toList with
  | [k, x] =>
    match ← str k with
    | "kw" => return .kw (← str x)
    | "content" => return .content (← str x)
    | "exact" => return .exact (← tok x)
    | "cls" =>
      match (← arr x).toList with
      | [c] => if (← str c) == "numeral" then return .cls .numeral else throw "class"
      | [c, l] => if (← str c) == "label" then return .cls (.label (← str l)) else throw "class"
      | _ => throw "class shape"
    | other => throw s!"terminal kind {other}"
  | _ => throw "terminal shape"

def sym (j : Json) : Except String (Sym Terminal) :=
  match j.getObjVal? "n" with
  | .ok n => return .n (← nat n)
  | .error _ => return .t (← terminal (← j.getObjVal? "t"))

def rule (j : Json) : Except String (Rule Terminal) := do
  let rhs ← (← arr (← j.getObjVal? "rhs")).mapM sym
  return { lhs := ← nat (← j.getObjVal? "lhs"), rhs := rhs.toList, act := 0,
           tag := (j.getObjValAs? String "tag").toOption.getD "" }

def grammar (j : Json) : Except String (Grammar Terminal) := do
  let rules ← (← arr (← j.getObjVal? "rules")).mapM rule
  let rank ← (← arr (← j.getObjVal? "rank")).mapM nat
  return { rules, start := ← nat (← j.getObjVal? "start"), rank }

def sentences (j : Json) : Except String (Array (Array Tok)) := do
  (← arr (← j.getObjVal? "sentences")).mapM fun s => do (← arr s).mapM tok

/-- The CPU time of this thread in nanoseconds (`/proc/thread-self/schedstat`), so that the load of
other processes does not enter the measurement. -/
def cpuNanos : IO Nat := do
  let s ← IO.FS.readFile "/proc/thread-self/schedstat"
  return ((s.splitOn " ").head?.bind String.toNat?).getD 0

def verdictName (P : Prepared Terminal) (w : Array Tok) : String :=
  match P.parse 2 1000000000000 w with
  | none => "budget"
  | some [] => "zero"
  | some [_] => "one"
  | some _ => "many"

/-- The CPU time of `k` parses of `w`, in nanoseconds. Each parse is run inside `IO.lazyPure` with its
own budget, so the compiler neither moves it out of the timed region nor shares it between runs. -/
def timeBatch (P : Prepared Terminal) (w : Array Tok) (k : Nat) : IO Nat := do
  let t0 ← cpuNanos
  let mut total := 0
  for j in [0:k] do
    let n ← IO.lazyPure fun _ => ((P.parse 2 (1000000000000 + j) w).map List.length).getD 0
    total := total + n
  let t1 ← cpuNanos
  if total == 1000000007 then IO.eprintln "unreachable"
  return t1 - t0

/-- The CPU time of one parse: runs are repeated until they take 20 ms together (or 4,096 runs), so
that the coarse clock of `schedstat` does not dominate. -/
def timeOne (P : Prepared Terminal) (w : Array Tok) : IO Nat := do
  let mut k := 1
  for _ in [0:7] do
    let ns ← timeBatch P w k
    if ns ≥ 20000000 || k ≥ 4096 then return ns / k
    k := k * 4
  return (← timeBatch P w k) / k

def runOne (name : String) (P : Prepared Terminal) (reps : Nat) (index : Nat) (w : Array Tok) : IO Unit := do
  let steps := (P.steps 2 1000000000000 w).getD 0
  let mut best := 0
  for k in [0:reps] do
    let ns ← timeOne P w
    if k == 0 || ns < best then best := ns
  let line := Json.mkObj [("configuration", toJson name), ("sentence", toJson index), ("tokens", toJson w.size),
    ("verdict", toJson (verdictName P w)), ("steps", toJson steps), ("micros", toJson (best / 1000)),
    ("nanos", toJson best)]
  IO.println line.compress

/-- The CPU time of `Grammar.prepare`, run inside `IO.lazyPure`. -/
def prepareTime (G : Grammar Terminal) : IO (Prepared Terminal × Nat) := do
  let t0 ← cpuNanos
  let P ← IO.lazyPure fun _ => G.prepare
  let n := P.terms.size + P.positions + P.order.length
  let t1 ← cpuNanos
  return (P, if n == 0 then t1 - t0 + 1 else t1 - t0)

def tokJson : Tok → Json
  | .word t i => Json.arr #[toJson "word", toJson t, toJson i]
  | .quoted n => Json.arr #[toJson "quoted", toJson n]
  | .label l k => Json.arr #[toJson "label", toJson l, toJson k]
  | .numeral v => Json.arr #[toJson "numeral", toJson v]
  | .punct t b a => Json.arr #[toJson "punct", toJson t, toJson b, toJson a]

def rejectJson (r : Reject) : Json :=
  let pos : Option Nat := match r with
    | .badCharacter k | .openQuote k | .badNumeral k | .emptySentence k => some k
    | _ => none
  Json.mkObj ([("reject", toJson (repr r).pretty)] ++ (pos.map fun k => ("at", toJson k)).toList)

def lexMain (path : String) : IO UInt32 := do
  let .ok input := Json.parse (← IO.FS.readFile path) | IO.eprintln "input is not JSON"; return 2
  let .ok sources := input.getArr? | IO.eprintln "expected a list of sources"; return 2
  for s in sources do
    let .ok text := s.getStr? | IO.eprintln "a source is not a string"; return 2
    let line := match lexSpans text with
      | .ok ss => Json.mkObj [("sentences", Json.arr (ss.map fun (sent : Array Spanned) =>
          Json.arr (sent.map fun (x : Spanned) => Json.arr #[tokJson x.1, toJson x.2.1, toJson x.2.2])))]
      | .error r => rejectJson r
    IO.println line.compress
  return 0

end EnglishLeanBench

open EnglishLeanBench in
def main (args : List String) : IO UInt32 := do
  if let ["--lex", path] := args then return ← lexMain path
  let some path := args.head? | IO.eprintln "usage: ve_english_lean_bench <input.json> [repetitions]"; return 2
  let reps := (args.drop 1).head?.bind String.toNat? |>.getD 3
  let text ← IO.FS.readFile path
  let .ok input := Json.parse text | IO.eprintln "input is not JSON"; return 2
  let .ok configs := input.getObjVal? "configurations" >>= Json.getArr? | IO.eprintln "no configurations"; return 2
  for c in configs do
    match (do
      let name ← (c.getObjValAs? String "name")
      let G ← grammar c
      let ws ← sentences c
      return (name, G, ws)) with
    | .error e => IO.eprintln e; return 2
    | .ok (name, G, ws) =>
      if !G.wf then IO.eprintln s!"{name}: grammar not well-formed"; return 2
      let (P, ns) ← prepareTime G
      IO.println (Json.mkObj [("configuration", toJson name), ("prepare_micros", toJson (ns / 1000)),
        ("terminals", toJson P.terms.size)]).compress
      let mut i := 0
      for w in ws do
        runOne name P reps i w
        i := i + 1
  return 0
