import VE.Service.Protocol

/-- `ve_service`: the persistent JSON-lines front end over the existing runners
(docs/spec/SEMANTICS-MIGRATION-PLAN.md, stage 1; `VE.Service` for the protocol).
Prints the handshake line, then one response line per request line, flushed, until
end of input. The supervisor bounds memory and time from outside. -/
def main (args : List String) : IO UInt32 := do
  unless args.isEmpty do
    (← IO.getStderr).putStrLn "usage: ve_service  (JSON lines on stdin and stdout)"
    return 2
  let stdin ← IO.getStdin
  let stdout ← IO.getStdout
  stdout.putStrLn VE.Service.handshake.compress
  stdout.flush
  repeat
    let line ← stdin.getLine
    if line.isEmpty then break
    if let some answer := VE.Service.handleLine line then
      stdout.putStrLn answer.compress
      stdout.flush
  return 0
