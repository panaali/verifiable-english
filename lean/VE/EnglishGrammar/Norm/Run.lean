import VE.EnglishGrammar.Run
import VE.EnglishGrammar.Norm.Owners

/-! EN-2: the mode `english.statement`, kind `blocks` (docs/spec/en-e3-norm.md 2.3). The request is `english.read`'s
case with `kind` and `source`; the answer is `readNorm`'s outcome, each rule block's node through the span gate and the
one decoder (`toNodesChecked`), and each rule row's byte span from the lexer's sentence positions (M10). The code,
status and field tables are `Run.lean`'s (M8, M9). Kind `render` is EN-3's. -/

namespace VE.EnglishGrammar.Norm
open Lean VE.EnglishGrammar

def BlockFault.code : BlockFault → String
  | .expectedRule .. => "ExpectedRule"
  | .noConsequence _ => "NoConsequence"
  | .strayConsequence _ => "StrayConsequence"
  | .strayCarveOut _ => "StrayCarveOut"
  | .unknownRule _ => "UnknownRule"

def BlockFault.text : BlockFault → String
  | .expectedRule i n => s!"Sentence {i + 1} starts a block that is not numbered {n}. Start it with \"Rule {n}.\""
  | .noConsequence i => s!"The block that starts at sentence {i + 1} has no rule sentence after its header."
  | .strayConsequence i => s!"Sentence {i + 1} is a rule sentence outside a block, or a second one in its block."
  | .strayCarveOut i => s!"Sentence {i + 1} is an \"Except when\" sentence before its block's rule sentence."
  | .unknownRule n => s!"The text names rule {n}, and it has no rule {n}."

def BlockFault.sentence? : BlockFault → Option Nat
  | .expectedRule i _ | .noConsequence i | .strayConsequence i | .strayCarveOut i => some i
  | .unknownRule _ => none


namespace Run
open VE.EnglishGrammar.Run (Case decodeCase status coded spanJson rejectText budgetFields invalidFields
  invalidOverlayFields lexicalSpan treeJson optionalFields statementUnsentenced partialStatus)

def placeText : Place → String
  | .act => "act"
  | .guard => "guard"
  | .carveOut => "carve_out"
  | .bearer => "bearer"

def spanRow (u : UnformalisedSpan) : Json :=
  Json.mkObj [("start", toJson u.start), ("stop", toJson u.stop), ("row", .str u.row), ("owner", .str u.owner),
    ("place", .str (placeText u.place))]

/-- Whether a sentence opens a statement: its first token is the word "Rule" (the header and precedence forms,
english-lean-s6.md 3.1). A clause sentence opens with its consequence wording, an except-when sentence with
"Except". -/
def opensStatement (sent : Array Spanned) : Bool :=
  match sent[0]? with
  | some (Tok.word w _, _, _) => fold w == "rule"
  | _ => false

/-- The bytes of a sentence: its first token's start to its period (`sentenceSpans`' ends, in bytes). -/
def sentenceBytes (sent : Array Spanned) : Option (Nat × Nat) := do
  let first ← sent[0]?
  let last ← sent.back?
  pure (first.2.1, last.2.2 + 1)

/-- The byte span of each statement of the text, in text order, from the sentence positions `lexSpans` gives
(`lex`, which `readNorm` reads, is `lexSpans` with the positions erased): a statement runs from the first byte of
a sentence that opens one to the period of the last sentence before the next. No line split is involved. -/
def statementSpans (source : String) : List (Nat × Nat) :=
  match lexSpans source with
  | .error _ => []
  | .ok sents => sents.toList.foldl (fun acc sent => match sentenceBytes sent with
      | none => acc
      | some (a, b) =>
        if opensStatement sent then acc ++ [(a, b)]
        else match acc.getLast? with
          | some (a0, _) => acc.dropLast ++ [(a0, b)]
          | none => acc) []

/-- The spans of a `one` answer's rows: one per statement, and no translation-mode statement (`readNorm` writes
none, `readNorm_authoring`; kept total without that premise). -/
def oneSpans (source : String) (rs : List NormStatement) : Option (List (Nat × Nat)) :=
  let sps := statementSpans source
  if rs.any (fun | .source _ => true | _ => false) || sps.length != rs.length then none else some sps

def rowsInternalText : String :=
  "The reader returned statements that are not the text's rule blocks and precedence lines."

/-- A rule row carries its block's byte span; a precedence row none. `oneSpans` excludes `.source`, so its case
is never written. -/
def statementRow (rs : List NormStatement) (sp : Nat × Nat) : NormStatement → Json
  | .rule h c => Json.mkObj [("kind", .str "rule"), ("number", toJson h.number),
      ("exception_to", toJson h.exceptionTo), ("node", c.wire (ruleName h.number) ((overOf rs h.number).map ruleName)),
      ("span", spanJson sp)]
  | .precedence n m => Json.mkObj [("kind", .str "precedence"), ("rule", toJson n), ("over", toJson m)]
  | .source _ => .null

/-- A decoder refusal's code: a resource limit is `NodeLimit` (class ResourceLimit, as `NestingLimit`), any
other refusal `NodeRefused`. -/
def decoderCode (t : String) : String := if t.startsWith "ResourceLimit:" then "NodeLimit" else "NodeRefused"

/-- Whether a stop's answer names its sentence: not for the engine's impossible `.ok`, and not for a rejection
whose code is unsentenced (`Reject.internal`; M11). -/
def stopNamesSentence : VE.Grammar.Outcome Tok Reject Piece → Bool
  | .ok _ _ => false
  | .rejected r => !statementUnsentenced.contains r.code
  | _ => true

def stoppedFields (tags : Array String) (i : Nat) : VE.Grammar.Outcome Tok Reject Piece → List (String × Json)
  | .ok _ _ => status "rejected" ++ coded "Internal" (rejectText i .internal)
  | .noDerivation => status "none" ++
      coded "NoDerivation" s!"Sentence {i + 1} has no reading as a rule block sentence with the current vocabulary." ++
      [("sentence", toJson i)]
  | .ambiguous t u => status "many" ++
      coded "Ambiguous" s!"Sentence {i + 1} can be read in more than one way. Two of the ways are shown." ++
      [("sentence", toJson i), ("witnesses", Json.arr #[treeJson tags t, treeJson tags u])]
  | .rejected r => status "rejected" ++ coded r.code (rejectText i r) ++
      (if statementUnsentenced.contains r.code then [] else [("sentence", toJson i)])
  | .budget => budgetFields i

/-- The result fields of one reader outcome. -/
def outcomeFields (c : Case) (tags : Array String) (source : String) : NormOutcome → List (String × Json)
  | .ok rs => match toNodesChecked rs with
    | .ok _ => match oneSpans source rs with
      | some sps => status "one" ++
          [("statements", Json.arr ((rs.zip sps).map fun (r, sp) => statementRow rs sp r).toArray)]
      | none => status "rejected" ++ coded "Internal" rowsInternalText
    | .error t => if (spansOf rs).isEmpty then status "rejected" ++ coded (decoderCode t) t
      else status partialStatus ++ coded "UnformalisedSpan" t ++
        [("spans", Json.arr ((spansOf rs).map spanRow).toArray)]
  | .invalidGrammar g => invalidFields "english.statement" c g
  | .lexical r => status "rejected" ++ coded r.code (rejectText 0 r) ++
      ((lexicalSpan source r).toList.map fun s => ("span", spanJson s))
  | .stopped i o => stoppedFields tags i o
  | .misplaced f => status "rejected" ++ coded f.code f.text ++ (f.sentence?.toList.map fun i => ("sentence", toJson i))

/-- The request of kind `blocks`: `english.read`'s case fields, `kind` and `source`. -/
def statementRequest (j : Json) : Except String (String × Case × String) := do
  VE.Bridge.exactFields j (["id", "environment", "lexicon", "kind", "source"] ++ optionalFields j)
  let id ← VE.Bridge.stringField j "id"
  unless (← VE.Bridge.stringField j "kind") == "blocks" do
    throw "InvalidInput: english.statement reads kind blocks or render"
  let c ← decodeCase j
  let source ← VE.Bridge.stringField j "source"
  pure (id, c, source)

structure Reader where
  read : Env → Overlay → Lexicon → Nat → String → NormOutcome
  tags : Env → Lexicon → Array String

def answerWith (R : Reader) (id : String) (c : Case) (source : String) : Json :=
  let identities := Json.mkObj ([("source_sha256", .str (VE.CertificateWire.sha256 source.toUTF8))] ++ c.identities)
  let fields := match c.overlayFailure with
    | some f => invalidOverlayFields "english.statement" f
    | none => outcomeFields c (R.tags c.E c.L) source (R.read c.E c.O c.L workBudget source)
  VE.Route.Wire.ok id [("result", Json.mkObj (fields ++ [("identities", identities)]))]

def leanReader : Reader := ⟨readNorm, normTags⟩

def answer (id : String) (c : Case) (source : String) : Json := answerWith leanReader id c source

def resultOf (row : Json) : Json := row.getObjValD "result"

/-- The mode at EN-2: kind `blocks` (EN-3 adds the dispatch on `kind`, 2.5). -/
def statementCase (j : Json) : Except String Json := do
  let (id, c, source) ← statementRequest j
  pure (answer id c source)

def statementCaseReported (j : Json) : Json :=
  match statementCase j with
  | .ok row => row
  | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]

end Run

/-! ## Section 4, part A: what the answer says (docs/spec/en-e3-norm.md 4) -/

namespace Run

/-! Lookups in an answer: `Json.mkObj` keeps the last binding of a key. -/

theorem findSome_lookup (t : List (String × Json)) (k : String) :
    t.findSome? (fun (p : String × Json) => if p.1 = k then some p.2 else none) = t.lookup k := by
  induction t with
  | nil => rfl
  | cons p t ih =>
    obtain ⟨a, b⟩ := p
    by_cases h : a = k
    · subst h; simp
    · have h2 : (k == a) = false := by simpa using fun e => h e.symm
      simp only [List.findSome?_cons, List.lookup_cons, h, h2, if_false]
      exact ih

/-- A lookup in `Json.mkObj l` is the last binding of the key in `l`. -/
theorem getD_mkObj (l : List (String × Json)) (k : String) :
    (Json.mkObj l).getObjValD k = (l.reverse.lookup k).getD .null := by
  have hw : (∅ : Std.TreeMap.Raw String Json compare).WF := Std.TreeMap.Raw.WF.empty
  have := Std.TreeMap.Raw.getElem?_insertMany_list (l := l) (k := k) hw
  simp only [Json.mkObj, Json.getObjValD, Json.getObjVal?, Std.TreeMap.Raw.get?_eq_getElem?,
    Std.TreeMap.Raw.ofList_eq_insertMany_empty, this, Std.TreeMap.Raw.getElem?_emptyc, Option.or_none,
    List.findSomeRev?_eq_findSome?_reverse, Std.compare_eq_iff_eq, findSome_lookup]
  cases List.lookup k l.reverse <;> rfl

theorem lookup_append (l1 l2 : List (String × Json)) (k : String) :
    (l1 ++ l2).lookup k = (l1.lookup k).or (l2.lookup k) := by
  induction l1 with
  | nil => simp
  | cons p t ih => obtain ⟨a, b⟩ := p; simp only [List.cons_append, List.lookup_cons]; split <;> simp [ih]

theorem lookup_none (l : List (String × Json)) (k : String) (h : ∀ p ∈ l, p.1 ≠ k) : l.lookup k = none := by
  induction l with
  | nil => rfl
  | cons p t ih =>
    obtain ⟨a, b⟩ := p
    have : (k == a) = false := by simpa using fun e => h (a, b) (by simp) e.symm
    simp only [List.lookup_cons, this]
    exact ih fun q hq => h q (by simp [hq])


end Run

open Run VE.EnglishGrammar.Run

theorem Run.statementStatusCodes_classed : ∀ s ∈ Run.statementStatusCodes, ∀ c ∈ s.2,
    ((VE.EnglishGrammar.Run.codeClasses ++ Run.statementCodeRows ++ Run.renderCodeRows).lookup c).isSome = true := by
  decide

theorem Run.statementFields_statuses :
    Run.statementFields.map (·.1) = Run.statementStatusCodes.map (·.1) := by
  decide

/-- The answer's fields, read as `outcomeFields` writes them. -/
local macro "answer_simp" : tactic => `(tactic| simp_all [getD_mkObj, lookup_append, List.lookup_cons, lookup_none,
  Run.outcomeFields, Run.stoppedFields, Run.stopNamesSentence, coded, status, budgetFields, invalidFields,
  invalidOverlayFields, failureJson, BlockFault.sentence?, partialStatus])

theorem Run.answer_misplaced : ∀ (id : String) (c : Case) (s : String) (f : BlockFault),
  c.overlayFailure = none → readNorm c.E c.O c.L workBudget s = .misplaced f →
    (Run.resultOf (Run.answer id c s)).getObjValD "code" = .str f.code ∧
    (Run.resultOf (Run.answer id c s)).getObjValD "status" = .str "rejected" := by
  intro id c s f hc hr
  simp only [Run.resultOf, Run.answer, Run.answerWith, Run.leanReader, VE.Route.Wire.ok, hc, hr]
  cases f <;> answer_simp

theorem Run.answer_stopped : ∀ (id : String) (c : Case) (s : String) (i : Nat)
    (o : VE.Grammar.Outcome Tok Reject Piece),
  c.overlayFailure = none → readNorm c.E c.O c.L workBudget s = .stopped i o →
    (Run.resultOf (Run.answer id c s)).getObjValD "status" ≠ .str "one" ∧
    (Run.resultOf (Run.answer id c s)).getObjValD "sentence" =
      (if Run.stopNamesSentence o then toJson i else Json.null) := by
  intro id c s i o hc hr
  simp only [Run.resultOf, Run.answer, Run.answerWith, Run.leanReader, VE.Route.Wire.ok, hc, hr]
  cases o with
  | rejected r => cases h : statementUnsentenced.contains r.code <;> answer_simp
  | _ => answer_simp

theorem Run.answer_one_iff : ∀ (id : String) (c : Case) (s : String),
  (Run.resultOf (Run.answer id c s)).getObjValD "status" = .str "one" ↔
    c.overlayFailure = none ∧ ∃ rs nds sps, readNorm c.E c.O c.L workBudget s = .ok rs ∧
      toNodesChecked rs = .ok nds ∧ Run.oneSpans s rs = some sps := by
  intro id c s
  simp only [Run.resultOf, Run.answer, Run.answerWith, Run.leanReader, VE.Route.Wire.ok]
  cases hc : c.overlayFailure with
  | some f => answer_simp
  | none =>
    cases hr : readNorm c.E c.O c.L workBudget s with
    | ok rs =>
      cases hn : toNodesChecked rs with
      | ok nds => cases hs : Run.oneSpans s rs <;> answer_simp
      | error t => by_cases he : spansOf rs = [] <;> answer_simp
    | invalidGrammar g => cases g <;> answer_simp <;> split <;> answer_simp
    | stopped i o => cases o <;> answer_simp <;> split <;> answer_simp
    | lexical r => cases h : lexicalSpan s r <;> answer_simp
    | _ => answer_simp

theorem Run.answer_one_rows : ∀ (id : String) (c : Case) (s : String) (rs : List NormStatement)
    (nds : List VE.Norms.Node) (sps : List (Nat × Nat)),
  c.overlayFailure = none → readNorm c.E c.O c.L workBudget s = .ok rs → toNodesChecked rs = .ok nds →
  Run.oneSpans s rs = some sps →
  (Run.resultOf (Run.answer id c s)).getObjValD "statements" =
    Json.arr ((rs.zip sps).map fun (r, sp) => Run.statementRow rs sp r).toArray ∧
  ∀ h cl, NormStatement.rule h cl ∈ rs →
    VE.Norms.Wire.decodeNorm (cl.wire (ruleName h.number) ((overOf rs h.number).map ruleName)) =
      cl.toNode (ruleName h.number) ((overOf rs h.number).map ruleName) := by
  intro id c s rs nds sps hc hr hn hs
  refine ⟨?_, fun _ _ _ => rfl⟩
  simp only [Run.resultOf, Run.answer, Run.answerWith, Run.leanReader, VE.Route.Wire.ok]
  answer_simp

theorem Run.answer_partial_no_node : ∀ (id : String) (c : Case) (s : String),
  (Run.resultOf (Run.answer id c s)).getObjValD "status" = .str VE.EnglishGrammar.Run.partialStatus →
    (Run.resultOf (Run.answer id c s)).getObjValD "statements" = .null ∧
    ∃ rs, readNorm c.E c.O c.L workBudget s = .ok rs ∧ spansOf rs ≠ [] ∧
      (Run.resultOf (Run.answer id c s)).getObjValD "spans" = Json.arr ((spansOf rs).map Run.spanRow).toArray := by
  intro id c s
  simp only [Run.resultOf, Run.answer, Run.answerWith, Run.leanReader, VE.Route.Wire.ok]
  cases hc : c.overlayFailure with
  | some f => answer_simp
  | none =>
    cases hr : readNorm c.E c.O c.L workBudget s with
    | ok rs =>
      cases hn : toNodesChecked rs with
      | ok nds => cases hs : Run.oneSpans s rs <;> answer_simp
      | error t => by_cases he : spansOf rs = [] <;> answer_simp
    | invalidGrammar g => cases g <;> answer_simp <;> split <;> answer_simp
    | stopped i o => cases o <;> answer_simp <;> split <;> answer_simp
    | lexical r => cases h : lexicalSpan s r <;> answer_simp
    | _ => answer_simp

end VE.EnglishGrammar.Norm
