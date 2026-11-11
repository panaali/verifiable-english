import VE.Commands.RunExamples
import Lean

/-! Prints `usecases/webapp-commands/environment.json` (tools/webapp_commands_env.py): the web environment
`VE.Commands.Examples.E_web` (commands-imperatives section 5) and the lexicon an `english.command` request over it
carries (`VE.Commands.RunExamples.lexJson`), which Python reads and never writes (plan CI-8, row (iv)). -/
open Lean VE.Commands.Examples VE.Commands.RunExamples

def main : IO Unit :=
  IO.println <| (Json.mkObj [("environment", E_web), ("lexicon", lexJson E_web)]).pretty
