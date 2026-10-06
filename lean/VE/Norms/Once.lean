import VE.Norms.Tree

/-! W1's metatheory check with the layer order computed once (lean-first batch 7 review B1).

`semanticCheck` types every formula of the `k`-th layer symbol in `envAt D k`, and `envAt` computes the layer order
(`syms D.T`, a topological sort of the stratum DAG) afresh for every formula: work quartic in the regulated
predicates, which every soft and rights source pays for each regulated predicate of its environment.
`semanticCheckOnce` computes the layer names once; `validateOnce` and `WellFormedOnce` call it. Each is equal to the
function it replaces, and the `@[csimp]` lemmas make the compiler run it wherever compiled code calls the original,
in every module that imports this one (`VE.Norms.Valid` does, so every W1 consumer does). -/

namespace VE.Norms
open VE.Route

/-- `semanticCheck` with the layer symbols and their names computed once. -/
def semanticCheckOnce (D : Doc) : Bool :=
  let ss := syms D.T
  let names := ss.map Sym.name
  (dependencyOrder (precedenceNodes D.T)).isOk && (dependencyOrder (stratumNodes D.T)).isOk &&
  decide names.Nodup &&
  ss.all (fun q => D.E.predicates q.name == some q.sorts &&
    (q.sorts.length == 1 || q.sorts.length == 2) && q.sorts.all D.E.sorts.contains) &&
  (List.range ss.length).all (fun k => match ss[k]? with
    | some q =>
      let E := hide D.E (names.drop k)
      (q.formulas D.T).all (fun φ => φ.check E q.sorts.reverse)
    | none => false) &&
  D.T.regulated.all (fun r => ss.contains (.reg r)) &&
  (pairs D.T).all (fun pr => pr.req != pr.perm &&
    ss.any (fun q => match q with | .reg r => r.name == pr.req && r.sorts == pr.sorts | _ => false) &&
    ss.any (fun q => match q with | .reg m => m.name == pr.perm && m.sorts == pr.sorts | _ => false))

theorem semanticCheckOnce_eq (D : Doc) : semanticCheckOnce D = semanticCheck D := rfl

/-- `validate` over `semanticCheckOnce`. -/
def validateOnce (D : Doc) : Except String Unit :=
  match check D with
  | .error e => .error e
  | .ok () => if semanticCheckOnce D then .ok () else .error "InvalidInput: norm document is not stratified"

theorem validateOnce_eq (D : Doc) : validateOnce D = validate D := rfl

/-- `WellFormed` over `validateOnce`. -/
def WellFormedOnce (D : Doc) : Bool := match validateOnce D with
  | .ok () => true
  | .error _ => false

theorem WellFormedOnce_eq (D : Doc) : WellFormedOnce D = WellFormed D := rfl

@[csimp] theorem semanticCheck_eq_once : @semanticCheck = @semanticCheckOnce :=
  funext fun D => (semanticCheckOnce_eq D).symm

@[csimp] theorem validate_eq_once : @validate = @validateOnce :=
  funext fun D => (validateOnce_eq D).symm

@[csimp] theorem wellFormed_eq_once : @WellFormed = @WellFormedOnce :=
  funext fun D => (WellFormedOnce_eq D).symm

end VE.Norms
