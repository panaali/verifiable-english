import VE.WireContract.Engine
import VE.WireContract.Tables.Corpus

/-! The hand-written hooks, classifier and view of the engine corpus (docs/spec/wire-contract.md 8.1).

They exercise the engine and decide no verdict. `lean_only` is registered here
and not in Python, so the corpus has a hook that Python defers.
-/

namespace VE.WireContract.Hooks.Corpus
open Lean
open VE.WireContract

def names : Pattern := ⟨.root, [.tok "doc", .tok "items", .star, .tok "name"]⟩
def refs : Pattern := ⟨.root, [.tok "doc", .tok "refs"]⟩
def note : Pattern := ⟨.root, [.tok "note"]⟩

/-- `no_bad_name` fails, with the values at `/doc/items/*/name` as `names`, when one of them is `"bad"`;
    `lean_only` fails when `/note` is `"lean"`. -/
def predicate : String → Json → List Pointer → HookResult
  | "no_bad_name", root, _ =>
    let found := (collect root [] names).map (·.2)
    if found.any (same · (.str "bad")) then .fail [("names", .arr found.toArray)] else .ok
  | "lean_only", root, _ =>
    if (resolve root [] note).any fun (_, v) => same v (.str "lean") then .fail [] else .ok
  | _, _, _ => .ok

/-- `demo_rules` on the number `k` of elements of `/doc/refs`: 3 is member 4.3a with `n` = 3, 2 is member 4.3b,
    4 names the undeclared member 4.3z, and any other number holds. -/
def classifier : String → Json → List Pointer → ClassifierResult
  | "demo_rules", root, _ =>
    match resolve root [] refs with
    | some (_, .arr xs) =>
      if xs.size == 3 then .fail "4.3a" [("n", natJson 3)]
      else if xs.size == 2 then .fail "4.3b" []
      else if xs.size == 4 then .fail "4.3z" []
      else .ok
    | _ => .ok
  | _, _, _ => .ok

/-- `part_view`: an object whose only member `x` is the `seed` of the value, or 0 when the value is not an
    object with a `seed`. -/
def view : String → Json → Json
  | "part_view", d => match d with
    | .obj _ => match d.getObjVal? "seed" with
      | .ok seed => Json.mkObj [("x", seed)]
      | .error _ => Json.mkObj [("x", natJson 0)]
    | _ => Json.mkObj [("x", natJson 0)]
  | _, v => v

def hooks : Hooks := ⟨predicate, classifier, view⟩

/-- The names this module registers. -/
def registered : List String := ["no_bad_name", "lean_only", "demo_rules", "part_view"]

#guard Tables.Corpus.Inner.table.hookNames.all registered.contains
#guard Tables.Corpus.Demo.table.hookNames.all registered.contains
#guard Tables.Corpus.Defer.table.hookNames.all registered.contains

end VE.WireContract.Hooks.Corpus
