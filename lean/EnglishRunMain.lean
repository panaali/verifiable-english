import VE.English.Run

def main (args : List String) : IO UInt32 := do
  let input ← match args with
    | [path] => IO.FS.readFile path
    | _ => (← IO.getStdin).readToEnd
  match VE.English.Run.run input with
  | .ok j => IO.println j.compress; return 0
  | .error e => IO.eprintln e; return 2
