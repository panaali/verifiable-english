import ResponseShape.Schemas.Common
import ResponseShape.Schemas.Envelope
import ResponseShape.Schemas.Alternatives
import ResponseShape.Schemas.Bundle
import ResponseShape.Schemas.Check
import ResponseShape.Schemas.CheckCertificate
import ResponseShape.Schemas.Diagnose
import ResponseShape.Schemas.Document
import ResponseShape.Schemas.Question
import ResponseShape.Schemas.Ask
import ResponseShape.Schemas.Discourse
import ResponseShape.Schemas.English
import ResponseShape.Schemas.EnglishLean
import ResponseShape.Schemas.Environment
import ResponseShape.Schemas.Evaluate
import ResponseShape.Schemas.FamilyNorms
import ResponseShape.Schemas.Graph
import ResponseShape.Schemas.Identity
import ResponseShape.Schemas.Model
import ResponseShape.Schemas.NormDefaults
import ResponseShape.Schemas.Norms
import ResponseShape.Schemas.Order
import ResponseShape.Schemas.Parse
import ResponseShape.Schemas.Quantity
import ResponseShape.Schemas.Readings
import ResponseShape.Schemas.ReadingsRoute
import ResponseShape.Schemas.Reports
import ResponseShape.Schemas.Rights
import ResponseShape.Schemas.Risk
import ResponseShape.Schemas.RiskEval
import ResponseShape.Schemas.Route
import ResponseShape.Schemas.SoftNorms
import ResponseShape.Schemas.SpeechActs

/-! The client's response schemas (`ve/backends/lean_service_schema/`), one module per file. -/

namespace ResponseShape.Schemas
open Lean ResponseShape

/-- Every schema file, its local references qualified with its name. -/
def files : List File := [
  Common.file,
  Envelope.file,
  Alternatives.file,
  Bundle.file,
  Check.file,
  CheckCertificate.file,
  Diagnose.file,
  Document.file,
  Discourse.file,
  English.file,
  EnglishLean.readFile,
  EnglishLean.grammarFile,
  EnglishLean.checkFile,
  Question.file,
  Ask.file,
  Environment.file,
  Evaluate.file,
  FamilyNorms.file,
  Graph.file,
  Identity.file,
  Model.file,
  NormDefaults.file,
  Norms.file,
  Order.file,
  Parse.file,
  Quantity.file,
  Readings.file,
  ReadingsRoute.file,
  Reports.file,
  Rights.file,
  Risk.file,
  RiskEval.file,
  Route.file,
  SoftNorms.file,
  SpeechActs.file].map File.qualified

/-- `{file name: document}`: what `tools/response_schemas.py` writes. -/
def rendered : Except String Json := do
  pure (Json.mkObj (← files.mapM fun f => do pure (f.name, ← f.render)))

/-- The row shape of a mode (`<mode>.json#/row`). -/
def row (mode : String) : Option Shape := lookup files s!"{mode}.json#/row"

/- Every schema renders, every mode of the service has its row, and the service's own handshake is
valid under its schema. -/
#guard rendered.toBool
#guard VE.Service.modes.all fun m => (row m.name).isSome
#guard (decide files (.ref "envelope.json#/handshake") {value := .null} VE.Service.handshake).toBool

end ResponseShape.Schemas
