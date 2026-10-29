import VE.Service.Protocol

def readingsMemoStatsEnabled (value : Option String) : Bool := value == some "1"
#guard readingsMemoStatsEnabled (some "1") && !readingsMemoStatsEnabled (some "0")

/-- `ve_service`: the persistent JSON-lines front end over the existing runners
(docs/spec/SEMANTICS-MIGRATION-PLAN.md, stage 1; `VE.Service` for the protocol).
Prints the handshake line, then one response line per request line, flushed, until
end of input. Process state holds environment handles and a bounded readings admission
memo. The supervisor bounds memory and time from outside. -/
def main (args : List String) : IO UInt32 := do
  unless args.isEmpty do
    (← IO.getStderr).putStrLn "usage: ve_service  (JSON lines on stdin and stdout)"
    return 2
  let stdin ← IO.getStdin
  let stdout ← IO.getStdout
  stdout.putStrLn VE.Service.handshake.compress
  stdout.flush
  let mut handles : VE.Service.Handles := {}
  let mut memo : VE.Readings.Run.AdmissionMemo := {}
  let stats := readingsMemoStatsEnabled (← IO.getEnv "VE_READINGS_MEMO_STATS")
  repeat
    let line ← stdin.getLine
    if line.isEmpty then break
    let (answer, nextHandles, nextMemo) := VE.Service.handleLineMemo handles memo line
    handles := nextHandles
    memo := nextMemo
    if let some answer := answer then
      if stats then
        (← IO.getStderr).putStrLn s!"readings_memo admissions={memo.admissions} hits={memo.hits} entries={memo.entries.length} bytes={memo.entries.foldl (fun n e => n + e.bytes) 0}"
      stdout.putStrLn answer.compress
      stdout.flush
  return 0
