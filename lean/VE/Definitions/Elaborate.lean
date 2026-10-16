import VE.Definitions.Route
import VE.Route.Route
import VE.Typing
import VE.Order.ProfileGate
import VE.Bridge

/-! Executable elaboration of identity-bound `defined` declarations, mirroring
Python `ve/definitions.py:compile_definitions`: order the definitions by the
one dependency DAG (`VE.Route.dependencyOrder`, the same algorithm and cycle
diagnostic as Python), then check each body over the symbols strictly below it.
Each generated biconditional then has the AST limits of any formula, as Python
checks `premise(definition)` after the body: at most 10,000 nodes and 64
levels. `chainOk_sound` connects the Boolean check to `Chain`, the hypothesis of
the layer and acceptance theorems. -/
namespace VE.Definitions
open VE.Route

/-- The predicate symbols a body mentions (edges of the dependency DAG). -/
def mentions : VE.Formula → List String
  | .unary p _ => [p]
  | .binary p _ _ => [p]
  | .not a | .all _ a | .ex _ a => mentions a
  | .and a b | .or a b | .implies a b => mentions a ++ mentions b
  | .top | .bottom | .eq _ _ => []

/-- One elaboration step over the full environment `E`, with the definitions
named `later` still hidden. -/
def stepOk (E : VE.Environment) (later : List String) (d : Def) : Bool :=
  !later.contains d.name && E.predicates d.name == some d.args &&
    (d.args.length == 1 || d.args.length == 2) && d.args.all E.sorts.contains &&
    d.body.check (hide E (d.name :: later)) d.args.reverse

def chainOk (E : VE.Environment) : List Def → Bool
  | [] => true
  | d :: ds => stepOk E (names ds) d && chainOk E ds

theorem stepOk_sound (E : VE.Environment) (later : List String) (d : Def)
    (h : stepOk E later d = true) : Step (hide E (d.name :: later)) (hide E later) d := by
  simp only [stepOk, Bool.and_eq_true, Bool.not_eq_true',
    beq_iff_eq, Bool.or_eq_true, List.all_eq_true, List.contains_iff_mem] at h
  obtain ⟨⟨⟨⟨hlater, hdecl⟩, har⟩, hargs⟩, hbody⟩ := h
  have hlater : d.name ∉ later := fun hm => by
    have := List.contains_iff_mem.mpr hm
    rw [hlater] at this; cases this
  exact {
    sorts := rfl
    constants := rfl
    fresh := by simp [hide]
    declared := by simp [hide, hlater, hdecl]
    others := fun r hr => by simp [hide, hr]
    arity := by simpa [Def.Arity] using har
    args := fun s hs => hargs s hs
    body := (VE.check_iff_wellFormed _ _ _).mp hbody }

theorem chainOk_sound (E : VE.Environment) : (ds : List Def) → chainOk E ds = true → Chain E ds
  | [], _ => trivial
  | d :: ds, h => by
    simp only [chainOk, Bool.and_eq_true] at h
    exact ⟨stepOk_sound E (names ds) d h.1, chainOk_sound E ds h.2⟩

/-- Formula levels as Python's checker counts them (a leaf is level 1). -/
def levels : VE.Formula → Nat
  | .top | .bottom | .unary .. | .binary .. | .eq .. => 1
  | .not a | .all _ a | .ex _ a => levels a + 1
  | .and a b | .or a b | .implies a b => max (levels a) (levels b) + 1

/-- The generated biconditional is within the AST limits of one formula. -/
def premiseWithin (d : Def) : Bool :=
  decide (VE.Bridge.formulaNodes d.premise ≤ 10000) && decide (levels d.premise ≤ 64)

/-- The diagnostic of a definition whose generated biconditional exceeds the AST limits. -/
def premiseTooLarge (name : String) : String :=
  s!"ResourceLimit: Definition {name}: the generated biconditional exceeds the AST node or depth limit"

/-- The diagnostic of a definition whose body does not type over the symbols below it. -/
def bodyNotTyped (name : String) : String :=
  s!"Definition {name}: the body is not a typed formula over the symbols below it"

/-- The first definition (in dependency order) whose step fails, or whose
generated biconditional exceeds the AST limits, with the diagnostic. -/
def firstBad (E : VE.Environment) : List Def → Option (Def × String)
  | [] => none
  | d :: ds =>
    if stepOk E (names ds) d then
      if premiseWithin d then firstBad E ds
      else some (d, premiseTooLarge d.name)
    else some (d, bodyNotTyped d.name)

/-- The checked result, or the diagnostic naming the first failing definition. -/
def finish (E : VE.Environment) (ds : List Def) : Except String (List Def) :=
  match firstBad E ds with
  | some (_, e) => .error e
  | none => .ok ds

theorem firstBad_none (E : VE.Environment) : (ds : List Def) → firstBad E ds = none →
    chainOk E ds = true
  | [], _ => rfl
  | d :: ds, h => by
    unfold firstBad at h
    split at h
    · rename_i hs
      split at h
      · simp [chainOk, hs, firstBad_none E ds h]
      · cases h
    · cases h

theorem finish_chain (E : VE.Environment) (ds ds' : List Def) (h : finish E ds = .ok ds') :
    Chain E ds' := by
  unfold finish at h
  split at h
  · cases h
  · rename_i hn
    cases h
    exact chainOk_sound E _ (firstBad_none E _ hn)

/-- Order and check declared definitions `(name, arguments, body)` over the
full environment `E`. The result is in dependency order. -/
def elaborate (E : VE.Environment) (entries : List (String × List String × VE.Formula)) :
    Except String (List Def) := do
  if entries.length > 256 then throw "ResourceLimit: dependency graph size"
  let order ← dependencyOrder (entries.map fun (p, _, b) => ⟨p, mentions b⟩)
  finish E (order.filterMap fun p =>
    (entries.find? (fun e => e.1 == p)).map fun (p, ss, b) => ⟨p, ss, b⟩)

open VE.Order.ProfileGate in
/-- Every elaborated list satisfies the layer's hypothesis. -/
theorem elaborate_chain (E : VE.Environment) (entries : List (String × List String × VE.Formula))
    (ds : List Def) (h : elaborate E entries = .ok ds) : Chain E ds := by
  unfold elaborate at h
  split at h
  · cases h
  · obtain ⟨_, _, h⟩ := bind_ok h
    obtain ⟨_, _, h⟩ := bind_ok h
    exact finish_chain E _ ds h

end VE.Definitions
