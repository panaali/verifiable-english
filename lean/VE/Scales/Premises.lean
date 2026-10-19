import VE.Scales.Syntax
import VE.Route.Route
import VE.Closure.Order

/-! The generated premises of `scales@0` (docs/spec/quantities.md 6.1): labelled, universal,
quantifier-free bodies, and the block's well-formedness check. Nothing else is generated: no density,
no end points, no threshold, no number. -/
namespace VE.Scales

/-- The labelled premises of one dimension. Under `.all s (.all s φ)`, `x` is `var 1` and `y` is `var 0`. -/
def premises (d : Dimension) : List (String × VE.Formula) :=
  let s := d.sort
  let m := d.more
  let lbl := fun (x : String) => d.name ++ "/" ++ x
  let all2 := fun (φ : VE.Formula) => VE.Formula.all s (.all s φ)
  let all3 := fun (φ : VE.Formula) => VE.Formula.all s (.all s (.all s φ))
  [(lbl "irreflexive", .all s (.not (rel2 m 0 0))),
   (lbl "transitive", all3 (.implies (.and (rel2 m 2 1) (rel2 m 1 0)) (rel2 m 2 0)))] ++
  (match d.same with
   | none => []
   | some e =>
     [(lbl "same-reflexive", .all s (rel2 e 0 0)),
      (lbl "same-symmetric", all2 (.implies (rel2 e 1 0) (rel2 e 0 1))),
      (lbl "same-transitive", all3 (.implies (.and (rel2 e 2 1) (rel2 e 1 0)) (rel2 e 2 0))),
      (lbl "same-not-more", all2 (.implies (rel2 e 1 0) (.not (rel2 m 1 0)))),
      (lbl "same-left", all3 (.implies (.and (rel2 e 2 1) (rel2 m 1 0)) (rel2 m 2 0))),
      (lbl "same-right", all3 (.implies (.and (rel2 m 2 1) (rel2 e 1 0)) (rel2 m 2 0)))] ++
     (if d.comparable then
       [(lbl "comparable", all2 (.or (rel2 m 1 0) (.or (rel2 m 0 1) (rel2 e 1 0))))] else [])) ++
  d.grades.flatMap (fun g =>
    [(lbl (g.name ++ "/closed"), all2 (.implies
        (.and (rel1 g.name 0) (match g.direction with
          | .upper => rel2 m 1 0
          | .lower => rel2 m 0 1)) (rel1 g.name 1)))] ++
    (match d.same with
     | some e => [(lbl (g.name ++ "/same"), all2 (.implies (.and (rel1 g.name 0) (rel2 e 1 0)) (rel1 g.name 1)))]
     | none => [])) ++
  d.above.map (fun p => (lbl (p.1 ++ "/above/" ++ p.2), .all s (.implies (rel1 p.1 0) (rel1 p.2 0))))

def scalePremises (D : ScaleDoc) : List (String × VE.Formula) := D.dims.flatMap premises

/-- The grade order of a dimension is a QS-1 `Order` (no closure of this plan's own). -/
def gradeOrder (d : Dimension) : VE.Closure.Order String := ⟨d.grades.map (·.name), d.above⟩
def gradeCaps : VE.Closure.Caps := ⟨16, 64⟩

def aboveNodes (d : Dimension) : List VE.Route.DepNode :=
  d.grades.map fun g => ⟨g.name, (d.above.filter (·.1 == g.name)).map (·.2)⟩

/-- One dimension per predicate; no two premises share a label (so no two dimensions share a name and no
`above` pair is repeated); predicates declared with the right signatures; `comparable` only with `same`;
grades are W2 open terms; `above` pairs within one dimension and one direction, within QS-1's caps,
acyclic by `kahn`. -/
def WellFormed (E : VE.Environment) (openTerms : List String) (D : ScaleDoc) : Bool :=
  decide D.symbols.Nodup &&
  decide ((scalePremises D).map (·.1)).Nodup &&
  D.dims.all fun d =>
    E.sorts.contains d.sort &&
    E.predicates d.more == some [d.sort, d.sort] &&
    (match d.same with
     | some e => E.predicates e == some [d.sort, d.sort]
     | none => !d.comparable) &&
    d.grades.all (fun g => E.predicates g.name == some [d.sort] && openTerms.contains g.name) &&
    d.above.all (fun p => match d.grades.find? (·.name == p.1), d.grades.find? (·.name == p.2) with
      | some g, some h => g.direction == h.direction && p.1 != p.2
      | _, _ => false) &&
    ((gradeOrder d).admit gradeCaps).isOk &&
    (VE.Route.dependencyOrder (aboveNodes d)).isOk

end VE.Scales
