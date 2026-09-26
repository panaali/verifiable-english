import VE.Route.Admission
import VE.Definitions.Bundle
import VE.Json
import VE.Core.Wire

/-! The `route` subcommand of `ve_conformance` (PLAN-EXPAND2 3.4). Each case
is `{"id", "environment", "kind"?, ...}` with a `ve.core@0.2` environment; the
envelope is decoded and gated first (`route_gate`), then the case is run on its
checker family:

* `evaluate` (default): `model`, `ast` → `values`;
* `countermodel`: `model`, `premises`, `conclusion` → `refutes`;
* `certificate`: `premises`, `conclusion`, `certificate` → `valid` (the checker
  receives regenerated Background, then the premises; the certificate binds
  both by meaning id);
* `dependency-order`: `nodes` → `order`, or the shared cycle diagnostic;
* `bundle` (FOL family): `lemmas` → every lemma checked in order with its
  citations (`VE.Definitions.Bundle`), or the first citation diagnostic;
* `background`: → the regenerated Background (definitions, then literals) and
  each premise's generator (the W3 differential elaboration check);
* `label`: `label` → the canonical label, or `AdmissionError: invalid label`;
* `admission` (FOL family): `document` → the admitted report.

Every model is validated against Background: a violation is reported as
`status: error` with `generator` and never as a truth value. The existing
subcommands are untouched. -/
namespace VE.Route.Run
open Lean
open VE.Bridge (stringField)
open VE.Graph (Claim)

/-- A claim on the wire; the default label is omitted. -/
def claimJson (c : Claim) : Json :=
  Json.mkObj ([("name", .str c.name), ("ast", Wire.encodeFormula c.formula)] ++
    if c.label == "asserted" then [] else [("label", .str c.label)])

def caseKind (j : Json) : Except String String :=
  match j.getObjVal? "kind" with
  | .ok k => k.getStr?
  | .error _ => .ok "evaluate"

def runAdmit (profiles : List String) (environment : Json) (rv : Wire.RouteVocabulary) (id : String)
    (j : Json) : Except String Json := do
  let document ← j.getObjVal? "document"
  let res ← Admission.admitDocument profiles environment rv document
  unless res.wires.all (fun w => match Admission.parseLabel w.claim.label with
    | some (.cite _ _) => false
    | _ => true) do
    throw (Gate.unsupported "document citations require a checked bundle binding")
  let report := Json.mkObj [("root", claimJson res.report.root),
    ("assumptions", Json.arr (res.report.assumptions.map claimJson).toArray)]
  let envId ← Wire.environmentId profiles environment
  let reportId ← VE.CertificateWire.digest s!"ve-report-{Wire.identityVersion profiles}\n"
    (Json.mkObj [("environment_id", .str envId), ("document", document), ("report", report)])
  pure (Wire.ok id [("admitted", .bool true), ("report", report), ("report_id", .str reportId),
    ("kinds", Json.arr res.kinds.toArray)])

/-- The FOL/closure vocabulary; `defined` declarations need `definitions@0`. -/
def decodeRouteVocabulary (e : Gate.Envelope) : Except String Wire.RouteVocabulary := do
  let rv ← Wire.decodeVocabulary e.vocabulary
  unless rv.definitions.isEmpty || e.profiles.contains "definitions@0" do
    throw "defined declarations require the definitions@0 profile"
  pure rv

/-- Run a case whose envelope has been decoded and gated. -/
def dispatch (id : String) (environment : Json) (e : Gate.Envelope) (j : Json) : Except String Json := do
  let kind ← caseKind j
  if kind == "dependency-order" then
    return ← Wire.runDependencyOrder id j
  if kind == "label" then
    if e.family == .closureNary then
      let _ ← VE.Core.Bridge.decodeEnvironment environment
      pure ()
    else if e.family == .order then
      let _ ← Wire.decodeOrderVocabulary e.vocabulary
      pure ()
    else
      let _ ← Wire.decodeVocabulary e.vocabulary
      pure ()
    -- The label grammar alone (PLAN-EXPAND2 3.6): only canonical labels parse.
    let s ← stringField j "label"
    return ← match Admission.parseLabel s with
      | some l => pure (Wire.ok id [("label", .str l.render)])
      | none => throw s!"AdmissionError: invalid label {s}"
  match e.family with
  | .closureNary =>
    VE.Core.Wire.run e.profiles environment id kind j
  | .order =>
    if kind == "admission" then throw (Gate.unsupported "admission on the order family is deferred")
    let v ← Wire.decodeOrderVocabulary e.vocabulary
    if kind == "background" then
      return Wire.runBackground id ((Background.literals v.literals).map (·, "literals"))
    Wire.runOrder e.profiles environment v id kind j
  | .closure =>
    if kind == "admission" then throw (Gate.unsupported "admission on the closure family is deferred")
    if kind == "bundle" then throw (Gate.unsupported "lemma bundles on the closure family are deferred")
    let rv ← decodeRouteVocabulary e
    if kind == "background" then return Wire.runBackground id (Wire.fullBackground rv)
    Wire.runClosure e.profiles environment rv id kind j
  | .fol =>
    let rv ← decodeRouteVocabulary e
    if kind == "background" then return Wire.runBackground id (Wire.fullBackground rv)
    if kind == "bundle" then return ← VE.Definitions.Bundle.runBundle e.profiles environment rv id j
    if kind == "admission" then
      unless rv.definitions.isEmpty do
        throw (Gate.unsupported "admission of documents with definitions is deferred")
      runAdmit e.profiles environment rv id j
    else Wire.runFol e.profiles environment rv id kind j

/-- Every case: the envelope is decoded and gated before anything else. -/
def runCase (j : Json) : Except String Json := do
  let id ← stringField j "id"
  let environment ← j.getObjVal? "environment"
  let e ← Gate.decodeEnvelope environment
  dispatch id environment e j

def generatorOf (message : String) : Option String :=
  if message.startsWith "InvalidModel(" then some ((message.drop 13).takeWhile (· != ')')) else none

def runCaseReported (j : Json) : Json :=
  match runCase j with
  | .ok result => result
  | .error message => Json.mkObj ([("id", j.getObjValD "id"), ("status", .str "error"),
      ("error", .str message)] ++
      (match generatorOf message with
       | some g => [("generator", .str g)]
       | none => []) ++
      (if j.getObjValD "kind" == .str "certificate" then [("valid", .bool false)] else []))

open VE.Order.ProfileGate in
/-- `route_gate`: every successful `route` case has a `ve.core@0.2`
environment whose profiles form an allowed checker family. -/
theorem route_gate (j r : Json) (h : runCase j = .ok r) :
    ∃ env e, j.getObjVal? "environment" = .ok env ∧ Gate.decodeEnvelope env = .ok e ∧
      VE.Bridge.stringField env "language" = .ok Gate.language ∧ Gate.AllowedFamily e.profiles e.family := by
  unfold runCase at h
  obtain ⟨_, _, h⟩ := bind_ok h
  obtain ⟨env, he, h⟩ := bind_ok h
  obtain ⟨e, hd, _⟩ := bind_ok h
  obtain ⟨hl, _, ha⟩ := Gate.decodeEnvelope_sound env e hd
  exact ⟨env, e, he, hd, hl, ha⟩

/-- An envelope whose profiles are not an allowed family is rejected by `route`. -/
theorem route_gate_rejects (j env : Json) (ps : List String)
    (he : j.getObjVal? "environment" = .ok env) (hp : Gate.profilesOf env = .ok ps)
    (hn : ∀ f, ¬ Gate.AllowedFamily ps f) : ∀ r, runCase j ≠ .ok r := by
  intro r h
  obtain ⟨env', e, he', hd, _, _⟩ := route_gate j r h
  rw [he] at he'
  cases he'
  exact Gate.route_gate_envelope env ps hp hn e hd

/-- The rejection happens before any checking: the case's result is exactly
the envelope diagnostic. -/
theorem route_rejects_before_checking (j env : Json) (id message : String)
    (hi : stringField j "id" = .ok id) (he : j.getObjVal? "environment" = .ok env)
    (hd : Gate.decodeEnvelope env = .error message) : runCase j = .error message := by
  simp [runCase, hi, he, hd, bind, Except.bind]

/-- The `route` subcommand: read a JSON case list, print the results. -/
def main (paths : List String) : IO UInt32 := do
  let input ← match paths with
    | [] | ["-"] => (← IO.getStdin).readToEnd
    | [path] => IO.FS.readFile path
    | _ =>
      (← IO.getStderr).putStrLn "usage: ve_conformance route [cases.json|-]"
      return 2
  match VE.JsonInput.parseCases input with
  | .error message =>
    (← IO.getStderr).putStrLn message
    return 2
  | .ok cases =>
    let results := cases.mapIdx fun index c => match c with
      | .ok j => runCaseReported j
      | .error message => Json.mkObj [("status", .str "error"),
          ("case_index", toJson index), ("error", .str message)]
    (← IO.getStdout).putStrLn (Json.arr results).compress
    return if results.any (fun r => r.getObjValD "status" == .str "error") then 1 else 0

end VE.Route.Run
