import Lean.Data.Json
import VE.Readings.Stage

/-! The env-gated stage timer of `ve_service` (reviews/dri-decisions-20261029-scale-admission-profile.md item 2).
The production stage functions write the marker lines of `VE.Readings.Stage` to stderr; `stream` is the service's
stderr, which reads them. Under `VE_READINGS_STAGE_TIMES=1` each stage becomes one JSON line, timed from its `begin`
to its `end` marker, with the component it ran in; under `=markers` the marker lines pass through as they are (the
count the timed lines are tested against); otherwise they are dropped. Every other write passes through unchanged.
Diagnostic only: no answer reads it. -/
namespace VE.Service.StageTimes
open Lean

/-- What `VE_READINGS_STAGE_TIMES` asks for. -/
inductive Mode where
  | off
  | timed
  | markers
  deriving BEq

def mode : Option String → Mode
  | some "1" => .timed
  | some "markers" => .markers
  | _ => .off

#guard mode (some "1") == .timed && mode (some "markers") == .markers && mode (some "0") == .off && mode none == .off

/-- The process's user and system CPU time in clock ticks (fields 14 and 15 of `/proc/self/stat`), 0 when unread. -/
def cpuTicks : IO Nat := do
  try
    let stat ← IO.FS.readFile "/proc/self/stat"
    let fields := (((stat.splitOn ") ").getLast?).getD "").splitOn " "
    return ((fields.getD 11 "0").toNat?).getD 0 + ((fields.getD 12 "0").toNat?).getD 0
  catch _ => return 0

/-- An open stage (`begin`) or component (`enter`), with its start. -/
structure Open where
  word : String
  name : String
  nanos : Nat
  ticks : Nat

/-- A marker line's word and the rest of its text, without the line's newline. -/
def parse (s : String) : Option (String × String) := do
  let body ← (s.dropRightWhile (· == '\n')).toSubstring.dropPrefix? VE.Readings.Stage.marker.toSubstring
  let word := body.takeWhile (· != ' ')
  pure (word.toString, (body.drop (word.bsize + 1)).toString)

#guard parse "ve-stage end ok rs a\n" == some ("end", "ok rs a") && parse "usage: ve_service\n" == none

/-- The JSON line of a closed stage: the innermost open component of `rest` is its part (`""` outside any). -/
def row (o : Open) (status : String) (rest : List Open) (nanos ticks : Nat) : Json :=
  Json.mkObj [("stage", .str o.name), ("part", .str ((rest.find? (·.word == "enter")).map (·.name) |>.getD "")),
    ("status", .str status), ("nanos", toJson (nanos - o.nanos)), ("cpu_ticks", toJson (ticks - o.ticks))]

/-- One marker at time `nanos`, `ticks` over the open `stack`: an opening one is pushed; a closing one pops its
    opening one, and a stage's gives its row. A closing marker whose opening one is not on top gives a row of
    status `unmatched` and leaves the stack as it is. -/
def step (stack : List Open) (word rest : String) (nanos ticks : Nat) : List Open × Option Json :=
  if word == "begin" || word == "enter" then (⟨word, rest, nanos, ticks⟩ :: stack, none) else
  let status := rest.takeWhile (· != ' ')
  let name := rest.drop (status.length + 1)
  match stack with
  | o :: more =>
    if o.word == (if word == "end" then "begin" else "enter") && o.name == name then
      (more, if word == "end" then some (row o status more nanos ticks) else none)
    else (stack, some (row ⟨word, name, nanos, ticks⟩ "unmatched" stack nanos ticks))
  | [] => (stack, some (row ⟨word, name, nanos, ticks⟩ "unmatched" [] nanos ticks))

#guard (step [⟨"begin", "admitS2", 5, 1⟩, ⟨"enter", "main", 2, 0⟩] "end" "ok admitS2" 9 4).2.map (·.compress) ==
  some "{\"cpu_ticks\":3,\"nanos\":4,\"part\":\"main\",\"stage\":\"admitS2\",\"status\":\"ok\"}"
#guard (step [⟨"enter", "rs a", 2, 0⟩] "leave" "error rs a" 9 4).1.isEmpty
#guard (step [⟨"enter", "main", 2, 0⟩] "end" "ok admitS2" 9 4).2.map (·.getObjValD "status") == some "unmatched"
#guard (step [] "begin" "admitNDFull" 1 1).1.map (·.name) == ["admitNDFull"]

/-- The service's stderr over `out` under mode `m`. -/
def stream (m : Mode) (out : IO.FS.Stream) : IO IO.FS.Stream := do
  let stack ← IO.mkRef ([] : List Open)
  pure { out with
    putStr := fun s => do
      match parse s with
      | none => out.putStr s
      | some (word, rest) =>
        match m with
        | .off => pure ()
        | .markers => out.putStr s
        | .timed =>
          let (next, line) := step (← stack.get) word rest (← IO.monoNanosNow) (← cpuTicks)
          stack.set next
          if let some j := line then out.putStrLn j.compress
      out.flush }

end VE.Service.StageTimes
