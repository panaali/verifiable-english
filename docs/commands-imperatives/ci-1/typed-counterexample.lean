import VE.Commands.Examples
/-! Scratch evidence for ci-1, run with `cd lean && lake env lean ../docs/commands-imperatives/ci-1/typed-counterexample.lean`.
`readCommand_typed` of docs/spec/commands-imperatives.md section 3 is false over an arbitrary `Lean.Json`. The entry of
`share_permitted` below is a misordered raw tree holding `arguments` twice: `decodeRegulatedIn` reads the first through
`getObjVal?`, and W1's vocabulary reads the second through `Json.mkObj (fields entry)`. The environment decodes, the
wording reads `.one`, `scopeOk` is true and `commandOk` is false. Output: `one, scopeOk true, commandOk false`. -/
open Lean Json VE.Commands VE.Commands.Examples
open VE.SpeechActs.Wire (decodeSpeechEnvironmentFull)

def rawShare : String × Json :=
  ("share_permitted",
    match (permission "share_permitted" ["user", "token"] "{0} share {1}").2 with
    | .obj kvs =>
      let l : Std.TreeMap.Raw String Json compare :=
        Std.TreeMap.Raw.ofList [("arguments", toJson ["user", "token"])] compare
      let r : Std.TreeMap.Raw String Json compare := Std.TreeMap.Raw.ofList
        [("regulated", kvs["regulated"]?.getD .null), ("arguments", toJson ["user", "control"])] compare
      .obj ⟨⟨.inner 4 "description" (.str "x") l.inner.inner r.inner.inner⟩⟩
    | _ => .null)

def rawEnv : Json := envOf ["user", "control", "ledger", "text", "reading", "token"]
    (actsWeb.filter (·.1 != "share_permitted") ++ [rawShare])
    [("reader", "user"), ("draft", "reading"), ("assistant", "control"), ("calls", "ledger"),
     ("question1", "text"), ("meaning1", "text"), ("token1", "token")]
    "webapp-copy" (some ("user", "reader")) definitesWeb

#eval match decodeSpeechEnvironmentFull rawEnv, lexOf E_web with
  | .ok se, .ok (E, L) =>
    match readCommand se se.scope E L 2100000 "Do not share the token." with
    | .one r =>
      let D : VE.SpeechActs.SpeechDoc := ⟨se.ne.rv.environment, [], se.scope, se.ne.regulated, [], [], [], [], []⟩
      s!"one, scopeOk {VE.SpeechActs.scopeOk D}, commandOk {VE.SpeechActs.commandOk D (r.command "u")}"
    | _ => "other"
  | _, _ => "fixture"
