import ResponseShape.Schemas
import ResponseShape.Skeleton
import Lean.Elab.Command

/-! # The skeleton of every mode's row shape

`ResponseShape.Skeletons.<mode>` is the skeleton (`ResponseShape.Skeleton`) of the row shape
`<mode>.json#/row`, extracted from `ResponseShape.Schemas` by `skel%` when this module is built, one
definition per constructor of `VE.Service.Mode`, and `row` maps each mode to its own (its match is
exhaustive over the constructors; the `#guard` below checks that each is its mode's file). Nothing
here is written by hand but the names: a shape that changes changes its skeleton, and the encoder
theorems (`ResponseShape.Encoders`) are checked against the new one. Each definition is a source
declaration of its own, so the trust map (tools/trust_map.py) classifies it by its lines. -/

namespace ResponseShape.Skeletons
open Lean Elab

/-- `skel% "file.json#/pointer"`: the skeleton of that shape, extracted when the term is
elaborated (for the lemmas about one encoder of a mode). -/
syntax (name := skelTerm) "skel% " str : term

elab_rules : term
  | `(skel% $target:str) => do
    match skeleton Schemas.files target.getString with
    | .error e => throwError "{target.getString}: {e}"
    | .ok (_, recursive@(_ :: _)) => throwError "{target.getString}: recursive skeleton through {recursive}"
    | .ok (k, []) => pure (toExpr k)

abbrev evaluate : Skel := skel% "evaluate.json#/row"
abbrev checkCertificate : Skel := skel% "check-certificate.json#/row"
abbrev order : Skel := skel% "order.json#/row"
abbrev route : Skel := skel% "route.json#/row"
abbrev norms : Skel := skel% "norms.json#/row"
abbrev english : Skel := skel% "english.json#/row"
abbrev englishRead : Skel := skel% "english.read.json#/row"
abbrev englishGrammar : Skel := skel% "english.grammar.json#/row"
abbrev englishCheck : Skel := skel% "english.check.json#/row"
abbrev environment : Skel := skel% "environment.json#/row"
abbrev model : Skel := skel% "model.json#/row"
abbrev check : Skel := skel% "check.json#/row"
abbrev identity : Skel := skel% "identity.json#/row"
abbrev parse : Skel := skel% "parse.json#/row"
abbrev graph : Skel := skel% "graph.json#/row"
abbrev readings : Skel := skel% "readings.json#/row"
abbrev bundle : Skel := skel% "bundle.json#/row"
abbrev familyNorms : Skel := skel% "family-norms.json#/row"
abbrev softNorms : Skel := skel% "soft-norms.json#/row"
abbrev rights : Skel := skel% "rights.json#/row"
abbrev speechActs : Skel := skel% "speech-acts.json#/row"
abbrev reports : Skel := skel% "reports.json#/row"
abbrev alternatives : Skel := skel% "alternatives.json#/row"
abbrev risk : Skel := skel% "risk.json#/row"
abbrev riskEval : Skel := skel% "risk-eval.json#/row"
abbrev quantity : Skel := skel% "quantity.json#/row"
abbrev normDefaults : Skel := skel% "norm-defaults.json#/row"
abbrev discourse : Skel := skel% "discourse.json#/row"
abbrev readingsRoute : Skel := skel% "readings-route.json#/row"
abbrev diagnose : Skel := skel% "diagnose.json#/row"
abbrev document : Skel := skel% "document.json#/row"

def row : VE.Service.Mode → Skel
  | .evaluate => evaluate
  | .checkCertificate => checkCertificate
  | .order => order
  | .route => route
  | .norms => norms
  | .english => english
  | .englishRead => englishRead
  | .englishGrammar => englishGrammar
  | .englishCheck => englishCheck
  | .environment => environment
  | .model => model
  | .check => check
  | .identity => identity
  | .parse => parse
  | .graph => graph
  | .readings => readings
  | .bundle => bundle
  | .familyNorms => familyNorms
  | .softNorms => softNorms
  | .rights => rights
  | .speechActs => speechActs
  | .reports => reports
  | .alternatives => alternatives
  | .risk => risk
  | .riskEval => riskEval
  | .quantity => quantity
  | .normDefaults => normDefaults
  | .discourse => discourse
  | .readingsRoute => readingsRoute
  | .diagnose => diagnose
  | .document => document

#guard VE.Service.modes.all fun m =>
  (skeleton Schemas.files s!"{m.name}.json#/row").toOption == some (row m, [])

end ResponseShape.Skeletons
