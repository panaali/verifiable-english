import VE.Acts.Readings

/-! ap-parse-index's measurement (docs/act-phrases/ap-parse-index/REPORT.md): where reading an act phrase spends its
CPU as the frames grow. Built on demand: `lake build ve_parse_index_bench && .lake/build/bin/ve_parse_index_bench`.
Each row prints the sizes, the steps `Prepared.steps` counts, and microseconds for the grammar, `prepare`, each part
of the table's rows (`accepted`, `ntRowGo`, the two `sufGroups`; without the budget), the table within the budget
and `readings` (grammar, table and meaning). Measurement only: no fixture reads it. -/

open VE.Acts VE.Grammar

def frameOf (h : String) (m s mods : List String) : Frame := ⟨wordsOf h, m, s, mods⟩
def letters : List Char := "abcdefghijklmnopqrstuvwxyz".toList
def pad (n : Nat) : List Frame :=
  (List.range n).map fun i => frameOf ("seek" ++ String.mk [letters[i / 26]!, letters[i % 26]!]) [""] [] []
def V5 : List Frame := [frameOf "seek" [""] [] ["in"], frameOf "enjoy" [""] [] ["in"]]
def cities : List String :=
  ["first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth"].map fun n => s!"the {n} city"
def l6 : String := "{0} to seek and to enjoy asylum" ++ String.join ((cities.take 6).map (" in " ++ ·))
def long400 : String := "{0} to seek" ++ String.join (List.replicate 193 " a") ++ " ab"
def toks (fx : List String) (s : String) : Array Lexical.Tok := ((Lexical.lex fx s).toOption.getD []).toArray

/-- `a`, after printing when `b`: keeps the compiler from dropping or moving a timed computation. -/
def force {α : Type} (b : Bool) (a : α) : IO α := do
  if b then IO.println "!"
  return a

def time {α : Type} (f : Unit → IO α) : IO (α × Nat) := do
  let t0 ← IO.monoNanosNow
  let a ← f ()
  return (a, ((← IO.monoNanosNow) - t0) / 1000)

/-- `fill` without the budget, adding up the time of each part of a row. -/
def fillTimed (P : Prepared Term) (w : Array Lexical.Tok) (empty : SufRow Lexical.Tok) :
    Nat → Array (SufRow Lexical.Tok) → Nat → List Nat → IO (Nat × List Nat)
  | 0, _, steps, ts => return (steps, ts)
  | k + 1, suf, steps, ts => do
    let (acc, t1) ← time fun _ => do let x := accepted P.terms w k; force (x.size == 12345) x
    let ((nt, s1), t2) ← time fun _ => do
      let r := ntRowGo acc rawCap w k suf P.order (Array.replicate P.grammar.rank.size []) 0; force (r.2 == 12345) r
    let ((o1, c1), t3) ← time fun _ => do
      let r := sufGroups rawCap w k nt suf (fun j => acc.getD j false) P.byTerm empty 0; force (r.2 == 12345) r
    let ((o2, c2), t4) ← time fun _ => do
      let r := sufGroups rawCap w k nt suf (fun B => !(nt.getD B []).isEmpty) P.byNt o1 c1; force (r.2 == 12345) r
    fillTimed P w empty k (suf.setIfInBounds k o2) (steps + s1 + P.positions + c2)
      ((ts.zip [t1, t2, t3, t4]).map fun (a, b) => a + b)

def row (name : String) (fs : List Frame) (fx : List String) (s : String) : IO Unit := do
  let V : Vocab := ⟨fs, []⟩
  let w := toks fx s
  let (G, tg) ← time fun _ => do let G := grammar V; force (G.rules.size == 0) G
  let (P, tp) ← time fun _ => do let P := G.prepare; force (P.positions == 0) P
  let ((all, parts), _) ← time fun _ =>
    fillTimed P w (P.shape.map fun n => Array.replicate n []) w.size (Array.replicate (w.size + 1) #[]) 0 [0, 0, 0, 0]
  let (st, tt) ← time fun _ => do let r := P.steps rawCap stepBudget w; force (r == some 12345) r
  let (rd, tr) ← time fun _ => do
    return (match readings V rawCap stepBudget w with | .ok xs => s!"ok {xs.length}" | .limit => "limit")
  IO.println s!"{name} frames={fs.length} tokens={w.size} rules={G.rules.size} terms={P.terms.size} \
    positions={P.positions} steps={st} unbudgetedSteps={all} | grammar={tg} prepare={tp} \
    accepted/ntRowGo/sufTerm/sufNt={parts} table={tt} readings={tr} ({rd})"

def main : IO Unit := do
  for n in [0, 30, 62, 126] do row "L6" (V5 ++ pad n) cities l6
  for n in [0, 30, 127] do row "long400" (frameOf "seek" [""] [] [] :: pad n) [] long400
