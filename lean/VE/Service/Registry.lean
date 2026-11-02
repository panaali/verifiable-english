/-! # The service's route registry (docs/ARCHITECTURE-REVIEW-2026-10.md, AR-10)

The one place a mode of `ve_service` is registered: its constructor, its wire name and its
`RouteSpec`. The handshake states the modes from `registry` (`VE.Service.handshake`), the
response shapes render them into `envelope.json` (`ResponseShape.Schemas.Envelope.handshake`),
and the client reads them from there (`ve/backends/service_schema.py`). A new `Mode` constructor
without a name or a `modes` entry fails to compile (`Mode.name`, `modes_complete`). Deadlines are
not here: they stay a Python operational policy (`ve/backends/lean_service.py`, F4). -/
namespace VE.Service

inductive Mode where
  | evaluate | checkCertificate | order | route | norms | english | englishRead | englishGrammar | englishCheck
  | environment | model | check | identity
  | parse | graph | readings | readingsChoices | bundle | familyNorms
  | softNorms | rights | speechActs | reports | alternatives | risk | riskEval | quantity | normDefaults
  | discourse | readingsRoute | diagnose | document | englishQuestion | searchBudget | ask | words | metered | calc
  | cardinality | scope | sensesProject
  deriving DecidableEq, Repr

def Mode.name : Mode → String
  | .evaluate => "evaluate"
  | .checkCertificate => "check-certificate"
  | .order => "order"
  | .route => "route"
  | .norms => "norms"
  | .english => "english"
  | .englishRead => "english.read"
  | .englishGrammar => "english.grammar"
  | .englishCheck => "english.check"
  | .environment => "environment"
  | .model => "model"
  | .check => "check"
  | .identity => "identity"
  | .parse => "parse"
  | .graph => "graph"
  | .readings => "readings"
  | .readingsChoices => "readings-choices"
  | .bundle => "bundle"
  | .familyNorms => "family-norms"
  | .softNorms => "soft-norms"
  | .rights => "rights"
  | .speechActs => "speech-acts"
  | .reports => "reports"
  | .alternatives => "alternatives"
  | .risk => "risk"
  | .riskEval => "risk-eval"
  | .quantity => "quantity"
  | .normDefaults => "norm-defaults"
  | .discourse => "discourse"
  | .readingsRoute => "readings-route"
  | .diagnose => "diagnose"
  | .document => "document"
  | .englishQuestion => "english.question"
  | .searchBudget => "search-budget"
  | .ask => "ask"
  | .words => "words"
  | .metered => "metered"
  | .calc => "calc"
  | .cardinality => "cardinality"
  | .scope => "scope"
  | .sensesProject => "senses.project"

def modes : List Mode := [.evaluate, .checkCertificate, .order, .route, .norms, .english,
  .englishRead, .englishGrammar, .englishCheck,
  .environment, .model, .check, .identity, .parse, .graph, .readings, .readingsChoices, .bundle, .familyNorms,
  .softNorms, .rights, .speechActs, .reports, .alternatives, .risk, .riskEval, .quantity, .normDefaults,
  .discourse, .readingsRoute, .diagnose, .document, .englishQuestion, .searchBudget, .ask, .words, .metered,
  .calc, .cardinality, .scope, .sensesProject]

def Mode.ofName? (name : String) : Option Mode := modes.find? (·.name == name)

/-- One public mode of the service. AR-12b adds its null policy (`nulls`). Deadlines are not
here: they stay a Python operational policy (F4). -/
structure RouteSpec where
  mode : Mode
  deriving Repr

def registry : List RouteSpec := modes.map fun m => ⟨m⟩

theorem modes_complete (m : Mode) : m ∈ modes := by cases m <;> decide
theorem registry_modes : registry.map (·.mode) = modes := by decide
theorem registry_names_nodup : (registry.map (·.mode.name)).Nodup := by decide

end VE.Service
