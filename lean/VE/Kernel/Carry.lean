import Lean.Data.Json

/-! The carry rule (docs/spec/kernel-boundary.md, section 3): a shell mode states no verdict of
its own. It elaborates a request into kernel cases, the kernel answers each case, and the answer
is a fold of the kernel's rows. The elaboration is any function; the theorems below do not
depend on what it computes, so it is not part of what must be trusted. -/
namespace VE.Kernel
open Lean

/-- A kernel verdict path: the runner of a service mode, the reviewed statement of what an
answer it accepts means, and the path's acceptance theorem. -/
structure Path where
  run : Json → Except String Json
  Meaning : Json → Json → Prop
  sound : ∀ case answer, run case = .ok answer → Meaning case answer

/-- One kernel case with a result for it: an answer or a refusal text. -/
structure Row where
  case : Json
  result : Except String Json

/-- The kernel's own row for a case. -/
def Path.row (p : Path) (case : Json) : Row := ⟨case, p.run case⟩

/-- `r` is the kernel's row: its result is what the path's runner returns for its case. -/
def Path.Ran (p : Path) (r : Row) : Prop := r.result = p.run r.case

/-- A shell mode. `elaborate` turns the request into kernel cases (untrusted: any function);
`fold` builds the answer from the request and the kernel's rows (kernel code: it is what a
reviewer reads). A request the elaboration refuses is refused. -/
def shell (p : Path) (elaborate : Json → Except String (List Json)) (fold : Json → List Row → Json)
    (request : Json) : Except String Json :=
  (elaborate request).map fun cases => fold request (cases.map p.row)

/-- Provenance: an answer of a shell mode is the fold of rows the kernel itself gave. The
elaboration appears nowhere in the conclusion. -/
theorem shell_provenance (p : Path) (elaborate : Json → Except String (List Json))
    (fold : Json → List Row → Json) (request answer : Json)
    (h : shell p elaborate fold request = .ok answer) :
    ∃ rows : List Row, (∀ r ∈ rows, p.Ran r) ∧ answer = fold request rows := by
  unfold shell at h
  cases he : elaborate request with
  | error e => rw [he] at h; cases h
  | ok cases =>
    rw [he] at h
    refine ⟨cases.map p.row, ?_, ?_⟩
    · intro r hr
      obtain ⟨c, _, rfl⟩ := List.mem_map.mp hr
      rfl
    · simpa [Except.map] using h.symm

/-- An accepted row of the kernel means what the path's reviewed statement says. -/
theorem ran_meaning (p : Path) (r : Row) (h : p.Ran r) (answer : Json) (ha : r.result = .ok answer) :
    p.Meaning r.case answer :=
  p.sound r.case answer (h ▸ ha)

/-- The two together: in a shell answer, every accepted row carries the kernel's meaning. -/
theorem shell_sound (p : Path) (elaborate : Json → Except String (List Json))
    (fold : Json → List Row → Json) (request answer : Json)
    (h : shell p elaborate fold request = .ok answer) :
    ∃ rows : List Row, answer = fold request rows ∧
      ∀ r ∈ rows, ∀ a, r.result = .ok a → p.Meaning r.case a := by
  obtain ⟨rows, hran, hfold⟩ := shell_provenance p elaborate fold request answer h
  exact ⟨rows, hfold, fun r hr a ha => ran_meaning p r (hran r hr) a ha⟩

/-- The plain fold: the shell's own display data under `view` (no verdict is read from it) and
the kernel's rows verbatim under `rows`. -/
def carry (view : Json → Json) (request : Json) (rows : List Row) : Json :=
  Json.mkObj [("view", view request),
    ("rows", Json.arr (rows.map fun r => Json.mkObj [("case", r.case),
      match r.result with
      | .ok a => ("answer", a)
      | .error e => ("refused", Json.str e)]).toArray)]

end VE.Kernel

