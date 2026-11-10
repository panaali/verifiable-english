# en-e3-norm: EN-2 and EN-3, the mode `english.statement` and Lean authority over W1 rule blocks (statement specification)

> Status: statement specification, draft 5 (2026-11-02), branch `design/en-e3-norm` at `a26f6faf3` (main merged in).
> Draft 2 applied the statement review's edits 1 to 22 (`MA/debates/en-e3-norm-spec/DRI-RULING.md`, verdict FIX);
> the review edit each change answers is cited as "(review N)". Draft 3 applied the four findings of the verifier's
> report on draft 2 (`MA/en-e3-norm-p3ver1.final.md`, FAIL), cited as "(verifier N)". Draft 4 applies the two items of
> the verifier's report on draft 3 (`MA/en-e3-norm-p3ver2.final.md`, FAIL), cited as "(second report N)": no Lean block,
> statement or fixture value changes. Draft 5 applies the one finding of the verifier's report on draft 4
> (`MA/en-e3-norm-p3ver3.final.md`, FAIL): the probes line of 2.5, with no Lean block, statement or fixture value changed.
> EN-1's statements and the frozen W1, soft and P0 contracts are unchanged.
> This is the item-1 spec of the en-e3-norm pipeline. By the DRI's decision of 2026-11-02 (item 2,
> `MA/reviews/dri-decisions-20261102-en-e3-norm.md`) it covers EN-2 and EN-3 of [the plan](en-e3-norm-PLAN.md), draft 6.
> It is the "review covering EN-2 onward" that `MA/reviews/dri-decisions-20261031-spec-el-s6.md` item 2 requires before
> the sprint row en-e3 gets its task file. EN-1's statements are main's [english-lean-s6.md](english-lean-s6.md). They
> are fixed, and this file does not restate or edit them. Section 2.6 also states the round-3 contracts that EN-5, EN-7
> and EN-10 inherit; en-e3 builds none of them. Every Lean block here was elaborated against main's Lean, en-s6's
> `Norm/Value.lean` included, in a scratch stub (section 10). Every fixture value in section 8 was computed by `#guard`
> or `#eval` in that stub. None was written by hand.

## 0. Scope, one paragraph

en-s6 (merged) and en-s6b (building) give Lean a reader of authored W1 rule blocks, `readNorm`, with its statements in
english-lean-s6.md. Python's `ve/norm_english.py` still decides every block, and nothing relays to Lean. EN-2 first
adds the four owner pieces that the design debate asked for and EN-1 does not have. It then adds the relayed mode
`english.statement` (kind `blocks`) by `docs/ROUTE-RECIPE.md`. Python calls it in shadow, beside its own reader, and a
saved delta report lists every disagreement. EN-2 changes no route's answer. The DRI decides every delta row that is
not `agree` or `both-refuse`, once, for the W1 layer. That decision is the stop point. EN-3 then makes Lean the
authority for W1 blocks. The mode's
kind `render` renders a document's blocks with their numbering context and reads the whole text back. Python's W1
matcher is deleted in the same change, with no fallback.

## 1. Sources and decisions

**Sources.**
- The plan, draft 5 (this branch): D1 to D4, D9 to D11; batches EN-2 and EN-3; section 7's requests.
- The DRI's orders: `MA/debates/design-en-e3-norm/DRI-CROSSPLAN.md` and `MA/reviews/dri-decisions-20261102-en-e3-norm.md`.
  The converged debate: `MA/debates/design-en-e3-norm/{astra,fable}.md`, round 3.
- The statement review of draft 1: `MA/debates/en-e3-norm-spec/DRI-RULING.md` (FIX, edits 1 to 22) and
  `MA/debates/en-e3-norm-spec/{astra,fable}.md`, rounds 1 to 3.
- The verifier's report on draft 2: `MA/en-e3-norm-p3ver1.final.md` (FAIL, findings 1 to 4).
- The verifier's report on draft 3: `MA/en-e3-norm-p3ver2.final.md` (FAIL, items 1 and 2).
- EN-1's statements: [english-lean-s6.md](english-lean-s6.md) (reviewed: spec-el-s6 FIX, then spec-el-s6-r2 PASS).
- main at `a26f6faf3`, read for every name this file cites as existing:
  - `lean/VE/EnglishGrammar/Norm/Value.lean` (en-s6): `Force`, `Force.sign`, `Polarity`, `Polarity.sign`, `Mode`,
    `Bearer`, `Place`, `Residual`, `Clause`, `Header`, `NormStatement`, `Piece`, `NState`, `BlockFault`, `assemble`,
    `assemble_numbered`;
  - `lean/VE/EnglishGrammar/Run.lean` (`english.read`'s runner): `Case`, `decodeCase`, `status`, `coded`,
    `codeClasses`, `rejectCodes`, `statusCodes`, `unsentencedCodes`, `rejectText`, `budgetFields`, `invalidFields`,
    `invalidOverlayFields`, `lexicalSpan`, `spanJson`, `treeJson`, `optionalFields`, `sentenceSpans`, and the
    `english.grammar` export of `codes`, `statuses` and `unsentenced` (:652-656);
  - `lean/VE/EnglishGrammar/Lexer.lean`: `Spanned`, `lexSpans` (:250), and `lex` (:270, `lexSpans` with the
    positions erased); `Token.lean`: `fold`; `Read.lean:25` (`meaning`'s `.internal`); `Syntax.lean`: `Reject`;
  - `lean/VE/EnglishGrammar/Lexicon.lean`: `Env`, `Lexicon` (`aliases`), `ProfileForms` (`aliases`), `Lexicon.valid`,
    `Lexicon.failures`, `workBudget`; `LexiconFixtures.lean`: `envF`, `failureSet`;
  - `lean/VE/EnglishGrammar/SourceWords.lean` (en-sw, merged, no rows): `SourceWordRow`, `SourceWordReading`,
    `SourceWordKind`;
  - `lean/VE/Acts/Table.lean`: `VE.Acts.Op`, `VE.Acts.opOf`; `lean/VE/SoftNorms/Tree.lean`: `VE.SoftNorms.Mode`;
    `lean/VE/SoftNorms/Wire.lean:69`: `decodeSoftNorm (se : SoftEnvironment) (j : Json)`;
  - `lean/VE/Norms/Wire.lean`: `decodeNorm`, `decodeNormsEnvironment`, `budgetTerm` and `budgetFormula`
    (:265-312); `lean/VE/Norms/Tree.lean`: `Node`, `Regulated`, `Role`; `lean/VE/Limits.lean`: `maxDepth`,
    `maxNodes`;
  - `lean/VE/Discourse/Joint.lean`: `allChoices`, `mem_allChoices`, `length_allChoices`, `productSize`,
    `compatible_budget`; `lean/VE/Readings/Choice.lean`: `maxChoices`; `lean/VE/Readings/Doc.lean`: `Doc`,
    `ReadingSet`, `Candidate`, `Item`; `lean/VE/Compose/Content.lean`: `Content`;
  - `lean/VE/Compose/Dispatch.lean`: `gateOf`, `profileTable`; `lean/VE/Scope/Readings.lean:44`: `shapeOf` (the
    precedent for a set's shape);
  - `lean/VE/Service/Registry.lean`, `Protocol.lean` (`Mode`, `runMode`); `lean/ResponseShape/Skeleton.lean` (`Skel`,
    `Fits`);
  - `ve/norm_english.py` (`_parse_guard` :54-73, `_consequence` :90-109, `render_rule_sentence` :155-171,
    `render_english` :174-204, `_HEADER` :207, `_block_grammar` :210-245, `_parse_consequence` :248-268, `parse_english`
    :271-366, `_soft_consequence` :376, `_soft_rewrite_consequence` :391, `_parse_soft_notes` :438 with its
    `_parse_guard` call at :468, `_parse_soft_english` :506 with its `_w1=True` call at :542, `_render_soft_english`
    :596 with its `_w1=True` call at :613 and `_consequence` at :621);
    `ve/surface/rights.py` (:44, :119); `ve/document/render.py`; `ve/readings_route.py` (:1185);
    `ve/backends/relay.py`; `ve/backends/english_lean.py` (`codes()` :33, `FIELDS` :145-150, `QUESTION_FIELDS` from
    `ve/question/codes.json` :373-387, the shadow log precedent :589-700, its default `ve-shadow.jsonl` :665);
    `ve/english_grammar/__init__.py` (`codes()` :67); `tools/english_codes.py` (`from_lean`, `render`);
    `ve/english.py` (`VE_ENGLISH_COMPARATOR`, :1780); `tools/lean_first_diff.py` (:373, a scratch log path);
    `tools/relay_lint.py` (`RELAYED_FUNCTIONS`, `findings`); `tests/test_english_e2_ledger_sites.py` (`KEPT`);
    `lean/ResponseShape/Schemas.lean`, `Skeletons.lean`, `Encoders.lean`;
    `ve/assurance-manifest.json` (`english.statement`, :4421);
  - `tools/layer_policy.py` (`lean_layer`, :158), `tools/check_lean_imports.py` (:298, an import from a lower layer is
    refused), `tools/relay_mutation_gate.py` (`SERVICE_READERS`, and a route without an `ok` fixture fails the gate);
    `lean/VE/Service/RegistryExamples.lean` (the mode count); `lean/VE/EnglishGrammar/Run.lean`'s `refusalExtras`
    (:535, `english.read`'s and `senses.read`'s `advice`); `lean/VE/EnglishGrammar/Lexer.lean`'s `digitsValue` (:78);
  - the tests that pin the W1 path or the mode list: `tests/test_norm_english.py`, `tests/test_english_unambiguity.py`,
    `tests/test_numeral_conversion.py`, `tests/test_risk_english.py`, `tests/test_alternatives_profile.py`,
    `tests/test_lean_service.py` (`_SCHEMA_SEEDS`, :1328).
- Standing rulings (`MA/DRI-RULINGS.md`): R6 (trusted growth that replaces a deleted Python path), R8 (what Python checks
  in a relayed answer), R16 (+150 trusted lines per item).

### 1.1 Decisions taken (not reopened)

- **One reader, one output path** (plan D1, D4). Every W1 block is read by `readNorm`. A rule becomes a node only
  through `VE.Norms.Wire.decodeNorm`.
- **Authority moves after a delta** (D10). EN-2 runs in shadow and changes no answer. The DRI decides every delta row
  that is not `agree` or `both-refuse` (section 6), once, for the W1 layer. That decision is the stop point between
  EN-2 and EN-3. No other signature is reserved.
- **No fallback.** After EN-3, an unavailable Lean gives `CheckerUnavailable`, never a Python reading.
- **Trust** (review 18; section 6 says the same). EN-2 deletes nothing, so its new trusted Lean lines
  (`Norm/Run.lean`, `Norm/Owners.lean`, and any OPEN-2 hunk in `Norm/Rules.lean`) go under R16 at EN-2's merge:
  estimated at 150 lines or fewer, and above 150 the item is cut. At EN-3, R6 covers only the lines that replace the
  deleted W1 path: `Norm/Render.lean`'s frame and `Norm/Run.lean`'s render kind (request, decoder, encoder), with the
  deleted Python lines named. Any other new trusted line goes under R16. en-s6b's `Rules`, `Read` and `Elab` were
  counted at en-s6b's merge and are not on either list.
- **No composability claim** (plan-synthesis-2 DECISIONS item 9). Nothing here states that two profiles compose.

### 1.2 The EN-0 corrections that touch EN-1

The DRI's order: check main. Write "done in EN-1" where main does the correction. Otherwise the correction is EN-2's
first step, with a fixture. No merged statement is edited.

| Correction (design debate round 3) | On main | Where |
|---|---|---|
| Sentence events plus block assembly, not one rule per sentence | `english-lean-s6.md` R1; `Piece`, `assemble` in `Norm/Value.lean` | done in EN-1 |
| Plain positive and negative consequences | R2; `Polarity.plain` | done in EN-1 |
| A seeded mutation that flips a real sign | `english-lean-s6.md` 6: `.mustNot` mapped to `true` in `Force.sign`; f1, f2 and f21 fail | done in EN-1 |
| act phrases' `VE.Acts.Op`/`opOf` instead of a second modal table | `Force` restates `Op` without `right` | EN-2 step 0: `Force.op`, `Polarity.op?`, `opOf_agrees`; fixtures O1, O2 |
| soft-norms' `Mode` plus separate exception data | `Mode.default (decider : String)` carries the decider | EN-2 step 0: `Mode.soft`, `soft_strict_iff`; fixture O3 |
| A source view over `Lexicon.aliases`, not a new spelling list | EN-1 reads no source | EN-2 step 0: `sourceView`, `sourceView_nil`; fixtures O4, O5 |
| A clause with an unformalised span never reaches `toNode` | `Clause.toNode` has no gate (`readNorm_authoring` proves authored clauses have no span) | EN-2 step 0: `UnformalisedSpan`, `Clause.toNodeChecked`, `toNodesChecked`; fixtures O6, O7 |

### 1.3 Corrections forced by main (found by the elaboration; proposed, the review decides)

- **M1. en-s6b's names are not on main.** `Norm/Rules.lean`, `Norm/Read.lean` and `Norm/Elab.lean` are en-s6b's,
  which is building now. The stub states `readNorm`, `NormOutcome`, `Polarity.fits`, `regulatedOf`, `ruleName`,
  `Clause.wire`, `Clause.toNode`, `overOf`, `toNodes` and `readNorm_authoring` with english-lean-s6.md's exact
  signatures. Their bodies are given where that spec gives them; the rest are `opaque`. Two more en-s6b names are
  needed and are stated as `opaque`: the rule tags of `normGrammar` (`normTags`, for witness trees), and the
  consequence wordings of a predicate and sign (`consequenceWordings`, for EN-3's rendering). Each must be en-s6b's own
  function, never a copy. If en-s6b exposes neither, EN-2 adds it to `Norm/Rules.lean` in one hunk.
- **M2. The decoder refuses two forms that `EFormula.encode` writes.** `decodeNorm` answers "invalid indexed formula"
  for a guard with a predicate of three or more arguments (`EFormula.encode`'s `"atom"` form), and for a comparison
  `lt` (fixture O8). It answers "ResourceLimit: formula depth exceeds 64" beyond `VE.Limits.maxDepth`
  (`Wire.lean:273`), and "ResourceLimit: AST exceeds depth or node budget" beyond `VE.Limits.maxNodes` (:266, :276).
  A clause `readNorm` accepts can therefore fail `toNode`. The answer is never `one`: a text beginning
  `ResourceLimit:` is `NodeLimit` (class ResourceLimit, as `NestingLimit`), and any other decoder text is `NodeRefused`
  (review 3). OPEN-1 is closed (review 4): W1's frozen formula wire (`Wire.lean:277-312`) has no n-ary or `lt` atom
  for `Clause.wire` to write, so `NodeRefused` stands, en-s6b does not change, and EN-2's delta lists every block that
  hits `NodeRefused` or `NodeLimit`.
- **M3. A source spelling must be fixed in the environment too.** V2 compares a lexicon's selected aliases with the
  environment's fixed aliases (`Lexicon.lean:472-478`). An alias added to the lexicon alone fails V2 (fixture O5). The
  source view therefore adds the spellings to both, and V4 then checks them against every other symbol's wording.
- **M4. Main has no Lean formula renderer.** `checkRendering` (`Read.lean:57`) checks a text that a producer
  rendered. EN-3 renders headers, consequences and the block frame in Lean. The guard and carve-out English comes from
  Python's `_guard_text`, as an untrusted producer. The whole-text read-back makes a wrong guard text fail.
- **M5. `partial` is a Lean keyword.** EN-10's result constructor is `CheckResult.partialSpans`, and its wire word is
  `partial`.
- **M6. `Matrix.lean` is not on main.** The route refusal reads `VE.Compose.gateOf profileTable` (main), and
  profile-composition's `Matrix.documentRefusal` once PC-4 lands.
- **M7. One manifest operation has one authority.** `english.statement` (`ve/assurance-manifest.json:4421`) covers
  three Python readers (`parse_english`, `parse_statement_english`, `require_unique_derivation`). EN-3 moves the W1 part
  into its own operation, `english.statement.w1` (2.5).
- **M8. The new codes join the one code table.** `Run.codeClasses` is the code-to-class table that `english.grammar`
  exports and that `ve/english_grammar/codes.json` is generated from. EN-2 appends its eight codes there in one hunk,
  and EN-3 its four. It keeps no second table. The stub does not edit `Run.lean`, so its computed rows show no
  `class` for the new codes (fixtures E1 to E15).
- **M9. english.statement's tables live in `Run.lean`'s hunk** (review 1, 2). `english.grammar`'s export
  (`Run.lean:652-656`) writes `codes.json`, and `Norm/Run.lean` imports `Run.lean`, so `Run.lean` cannot read a table
  defined in `Norm/Run.lean`. `statementStatusCodes`, `statementFields` and `statementUnsentenced` are therefore
  defined in EN-2's code hunk of `Run.lean`, beside `statusCodes`, and the export writes them beside `codes`,
  `statuses` and `unsentenced`. EN-3's hunk adds `rendered` and the four render codes. The stub states these tables
  in `Norm.Run`, as 2.3 does. `tools/english_codes.py` copies only the export's `codes`, `statuses` and `unsentenced`
  (`from_lean`, `render`), so EN-2 extends it with the new members, or they never reach `codes.json`. EN-2 also adds
  their reader beside `codes()` in `ve/english_grammar/__init__.py` (verifier 2).
- **M10. A rule row's span comes from the lexer's sentences** (review 6). `NormOutcome.ok` carries statements
  without positions, and `NormStatement` gains no field. `lex`, which `readNorm` reads, is `lexSpans` with the
  positions erased (`Lexer.lean:270`). `statementSpans` takes `lexSpans`' sentences. A sentence opens a statement when
  its first token is the word "Rule": the header and precedence forms begin with it, a clause sentence begins with
  its consequence wording, and an except-when sentence with "Except" (english-lean-s6.md 3.1, 2.5). A statement runs
  from its opening sentence to the period of the last sentence before the next one. A block over two lines is one
  span (fixture E13).
- **M11. Both encoder faults of an `ok` outcome are `rejected Internal`** (review 5, 6). The encoder writes `one` only
  when `oneSpans` holds: there is no translation-mode `.source` statement, and there is one span per statement. Each
  holds for en-s6b's reader (`readNorm_authoring`; M10's forms), and neither is assumed. So `answer_one_iff` and
  `answer_one_rows` carry `oneSpans s rs = some sps`. These `Internal` answers name no sentence, so `Internal` is in
  the unsentenced set. A stop obeys the same rule (verifier 4). `stopped i (.ok _ _)` (never produced) and
  `stopped i (.rejected r)` with `r.code` unsentenced carry no `sentence`. The second covers `Reject.internal`, the
  reader's answer for a tree with no sentence value (`Read.lean:25`), and the lexer's codes, which a stop never
  carries. `answer_stopped` states the sentence of every stop through `stopNamesSentence`. A `lexical r` needs no
  such test: each of `lexSpans`' nine rejections (`Lexer.lean`) has a code in `unsentencedCodes`. So the relay's rule
  (a `rejected` answer names a sentence exactly when its code is not unsentenced) has no exception.

## 2. Definitions

### 2.1 Terms

- **Block text**, **rule block**, **header sentence**, **clause sentence**, **except-when sentence**, **precedence
  line**, **consequence wording**: as english-lean-s6.md 2.1.
- **Statement**: a `NormStatement`, the value `readNorm` returns for one rule block or one precedence line.
- **Node**: a `VE.Norms.Node`, the W1 rule that `decodeNorm` gives. **The nodes of a text**: `toNodes rs` of its
  statements. Rule `i` is named `rule-i`, and its `over` lists the targets of its header, then those of its precedence
  lines.
- **Unformalised span**: a phrase that the reader parses and does not formalise. Its record is `UnformalisedSpan`
  (NEW; not ve-limits' `Residual`, which holds an OPEN unit's open terms or its active reading set). Main's `Clause`
  carries spans in its merged `residuals` field (`Residual`). `Residual.span` names one as the answer names it.
- **Owner pieces**: the owners' own definitions that the reader's values are bound to: act phrases' `Op`, soft-norms'
  `Mode`, the lexicon's aliases.
- **Shadow**: when `VE_STATEMENT_COMPARATOR=1` and `VE_SHADOW_LOG` are both set, Python also calls the mode on each
  authored W1 text it reads, compares Lean's nodes with its own, and keeps its own answer (review 12).
- **Delta row**: one disagreement between the two readers, with its class (2.4).
- **Producer**: code outside Lean whose output Lean checks before anything uses it. Here that is Python's `_guard_text`.

### 2.2 EN-2 step 0: the owner pieces (`lean/VE/EnglishGrammar/Norm/Owners.lean`, new)

Imports `Norm/Value.lean`, `VE.Acts.Table`, `VE.SoftNorms.Tree` and en-s6b's `Norm/Elab.lean`. All are in layers 2 and 3
(`tools/layer_policy.py:186`), so no layer rule changes.

```lean
namespace VE.EnglishGrammar.Norm

/-- The owner's op of a modal word (act phrases' `VE.Acts.Op`). -/
def Force.op : Force → VE.Acts.Op
  | .must => .must
  | .needNot => .needNot
  | .may => .may
  | .mustNot => .mustNot

/-- A consequence's op as act phrases fixes it (`VE.Acts.opOf`): a plain positive is `right`, a plain negative
has none. -/
def Polarity.op? : Polarity → Option VE.Acts.Op
  | .modal f => some f.op
  | .plain true => some .right
  | .plain false => none

/-- soft-norms' mode of a clause (`VE.SoftNorms.Mode`); the decider is exception data, not the mode. -/
def Mode.soft : Mode → VE.SoftNorms.Mode
  | .strict => .strict
  | .default _ => .default

/-- The source view: the use case's source spellings `A` as aliases, fixed in the environment's forms and
selected in the lexicon, so that V1-V5 (V4 included) check them with every other alias. -/
def sourceView (E : Env) (L : Lexicon) (A : List (String × String × Bool)) : Env × Lexicon :=
  ({ E with forms := { E.forms with aliases := E.forms.aliases ++ A } }, { L with aliases := L.aliases ++ A })

/-- An unformalised span (NEW; not ve-limits' `Residual`): a clause's `Residual` as an answer names it. -/
structure UnformalisedSpan where
  start : Nat
  stop : Nat
  row : String
  owner : String
  place : Place
  deriving DecidableEq, Repr

def Residual.span (r : Residual) : UnformalisedSpan := ⟨r.start, r.stop, r.row, r.owner, r.place⟩

def unformalisedText (k : Nat) : String :=
  s!"The text has {k} phrase(s) that the reader parsed and did not formalise. No rule is made from a sentence " ++
  "with such a phrase."

/-- The span gate: a clause with a span never becomes a node. -/
def Clause.toNodeChecked (name : String) (over : List String) (c : Clause) : Except String VE.Norms.Node :=
  if c.residuals.isEmpty then c.toNode name over else .error (unformalisedText c.residuals.length)

def spansOf (rs : List NormStatement) : List UnformalisedSpan :=
  (rs.flatMap NormStatement.clauses).flatMap fun c => c.residuals.map Residual.span

def toNodesChecked (rs : List NormStatement) : Except String (List VE.Norms.Node) :=
  if (spansOf rs).isEmpty then toNodes rs else .error (unformalisedText (spansOf rs).length)
```

`Force` and `Mode` stay as merged. Every new consumer reads the op through `Polarity.op?` and the mode through
`Mode.soft`. EN-4's `Clause.toSoft` takes its decider from the notes (`SoftNotes.decidedBy`), never from
`Mode.default`'s argument (plan EN-4). EN-5 reads the source view instead of draft 1's `SourceLexicon`. Authoring mode
reads no source spelling (`sourceView_nil`).

### 2.3 EN-2: the mode `english.statement` (`lean/VE/EnglishGrammar/Norm/Run.lean`, new; layer 4)

**Request** (kind `blocks`): `english.read`'s case fields and two more. It has exactly the members `id`,
`environment`, `lexicon`, `kind` and `source`, plus `english.read`'s optional members (`optionalFields`: `overlay`,
the generated frame). `kind` must be `"blocks"`. `decodeCase` decodes the environment, overlay and lexicon, as it does
for `english.read`. The budget is `workBudget`. EN-3's kind `render` has its own request (2.5, review 7);
`statementCase` dispatches on `kind`, and every other kind is refused.

**Answer**: `VE.Route.Wire.ok id [("result", …)]`. Its result has `status`, `identities` (`source_sha256` and
`decodeCase`'s identities), and the members of its status:

| `status` | When | Members |
|---|---|---|
| `one` | `readNorm` returned `ok rs`, `toNodesChecked rs = ok _` and `oneSpans source rs = some sps` | `statements`: one row per statement, in text order |
| `rejected` | `ok rs`, `toNodesChecked rs = ok _`, and `oneSpans` fails (a `.source` statement, or a span count that is not the statement count; never for en-s6b's reader, kept total; review 5, M11) | `code` `Internal`, `text`; no `sentence` |
| `partial` | `ok rs` and some clause has a span | `code` `UnformalisedSpan`, `text`, `spans` (rows); no `statements` |
| `rejected` | `ok rs`, no span, and the decoder refuses a node with a text beginning `ResourceLimit:` | `code` `NodeLimit`, `text` (the decoder's) (review 3) |
| `rejected` | `ok rs`, no span, and the decoder refuses a node with any other text | `code` `NodeRefused`, `text` (the decoder's) |
| `rejected` | `misplaced f` | `code` (`BlockFault.code f`), `text`, and `sentence` when the fault names one |
| `rejected` | `lexical r`, or `stopped i (.rejected r)` | `r.code`, `rejectText`; `span` (lexical), or `sentence` unless `r.code` is in `statementUnsentenced` (`Reject.internal` has none; M11) |
| `rejected` | `stopped i (.ok _ _)` (the engine never stops on a reading; kept total) | `Internal`; no `sentence` (M11) |
| `none` | `stopped i .noDerivation` | `NoDerivation`, `sentence` |
| `many` | `stopped i (.ambiguous t u)` | `Ambiguous`, `sentence`, `witnesses` (both trees, rule tags of `normGrammar`) |
| `budget` | `stopped i .budget` | `Budget`, `sentence` (`budgetFields`) |
| `invalidGrammar` | an overlay failure, or `invalidGrammar g` | `english.read`'s fields (`InvalidOverlay`, `InvalidGrammar`) |
| `rendered` | kind `render` (EN-3, 2.5): `renderChecked` passed | `text`, `blocks` (each `{"header", "sentence"}`) |

A rule row is `{"kind": "rule", "number", "exception_to", "node", "span"}`, where `node` is the clause's wire
(`{"norm": {...}}`) under `rule-<number>` with its `over`, and `span` is the rule block's byte span
`[start, stop]` in the source (review 6, M10). A precedence row is `{"kind": "precedence", "rule", "over"}`. A span
row is `{"start", "stop", "row", "owner", "place"}`. Its `place` is `act`, `guard`, `carve_out` or `bearer`, and its
offsets are bytes of the source.

**The field table** (review 1). english.statement has its own table of required and optional members per status,
`statementFields`, and its own unsentenced set, `statementUnsentenced`. They are defined once in Lean, beside
`statementStatusCodes` (M9). The table admits `partial`. The unsentenced set is the lexer codes (english.read's
`unsentencedCodes`, reused, not copied), `UnknownRule`, `NodeRefused`, `NodeLimit` and `UnformalisedSpan`; also
`Internal` (M11) and the four render codes, which name no sentence either. A `rejected` answer names a sentence
exactly when its code is not in the set. Step 2's schema reads the table. `english.grammar` exports the table and
the set, and `tools/english_codes.py` writes them to `ve/english_grammar/codes.json`, as it writes `codes`, `statuses`
and `unsentenced` today (`english_lean.py:33`; `QUESTION_FIELDS` is the same precedent for
`ve/question/codes.json`, :373-387). The relay reads them from that file, through a reader beside `codes()` in
`ve/english_grammar/__init__.py` (M9). Python keeps no second table: english.read's `FIELDS`
(`english_lean.py:145-150`) is not used, because it requires `span` for `none`, `many`, `budget` and `rejected` and
has no `partial`.

```lean
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
  invalidOverlayFields lexicalSpan treeJson optionalFields)

/-- The rows EN-2 appends to `Run.codeClasses` (one hunk; the one code table). -/
def statementCodeRows : List (String × String) :=
  [("ExpectedRule", "SyntaxError"), ("NoConsequence", "SyntaxError"), ("StrayConsequence", "SyntaxError"),
   ("StrayCarveOut", "SyntaxError"), ("UnknownRule", "VEError"), ("UnformalisedSpan", "VEError"),
   ("NodeRefused", "VEError"), ("NodeLimit", "ResourceLimit")]

/-- The rows EN-3 appends to `Run.codeClasses` (kind `render`; `UnknownRule` is EN-2's). -/
def renderCodeRows : List (String × String) :=
  [("RenderUnread", "CheckerUnavailable"), ("RenderMismatch", "CheckerUnavailable"),
   ("NoWording", "CheckerUnavailable"), ("InvalidInput", "VEError")]

/-- english.statement's statuses and the codes each may carry (`rendered` and the four render codes join with
EN-3's rows). -/
def statementStatusCodes : List (String × List String) :=
  [("one", []), ("partial", ["UnformalisedSpan"]), ("none", ["NoDerivation"]), ("many", ["Ambiguous"]),
   ("budget", ["Budget"]), ("invalidGrammar", ["InvalidGrammar", "InvalidOverlay"]), ("rendered", []),
   ("rejected", VE.EnglishGrammar.Run.rejectCodes ++
     ["ExpectedRule", "NoConsequence", "StrayConsequence", "StrayCarveOut", "UnknownRule", "NodeRefused", "NodeLimit",
      "RenderUnread", "RenderMismatch", "NoWording", "InvalidInput"])]

/-- english.statement's members of each status besides `status` and `identities`: required, then optional. The
schema (recipe step 2) reads it; `english.grammar` exports it, `tools/english_codes.py` writes it to
`ve/english_grammar/codes.json`, and the relay reads it there. -/
def statementFields : List (String × List String × List String) :=
  [("one", ["statements"], []), ("partial", ["code", "text", "class", "spans"], []),
   ("none", ["code", "text", "class", "sentence"], []),
   ("many", ["code", "text", "class", "sentence", "witnesses"], []),
   ("budget", ["code", "text", "class", "sentence"], []),
   ("invalidGrammar", ["code", "text", "class"], ["fault", "failure"]),
   ("rendered", ["text", "blocks"], []),
   ("rejected", ["code", "text", "class"], ["sentence", "span"])]

/-- The codes whose answer never names a sentence: the lexer's (english.read's `unsentencedCodes`), the codes of a
whole text, and the render codes. A `rejected` answer names a sentence exactly when its code is not here. -/
def statementUnsentenced : List String :=
  VE.EnglishGrammar.Run.unsentencedCodes ++
    ["UnknownRule", "NodeRefused", "NodeLimit", "UnformalisedSpan", "Internal", "RenderUnread", "RenderMismatch",
     "NoWording", "InvalidInput"]

def placeText : Place → String
  | .act => "act" | .guard => "guard" | .carveOut => "carve_out" | .bearer => "bearer"

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

def outcomeFields (c : Case) (tags : Array String) (source : String) : NormOutcome → List (String × Json)
  | .ok rs => match toNodesChecked rs with
    | .ok _ => match oneSpans source rs with
      | some sps => status "one" ++
          [("statements", Json.arr ((rs.zip sps).map fun (r, sp) => statementRow rs sp r).toArray)]
      | none => status "rejected" ++ coded "Internal" rowsInternalText
    | .error t => if (spansOf rs).isEmpty then status "rejected" ++ coded (decoderCode t) t
      else status "partial" ++ coded "UnformalisedSpan" t ++
        [("spans", Json.arr ((spansOf rs).map spanRow).toArray)]
  | .invalidGrammar g => invalidFields "english.statement" c g
  | .lexical r => status "rejected" ++ coded r.code (rejectText 0 r) ++
      ((lexicalSpan source r).toList.map fun s => ("span", spanJson s))
  | .stopped i o => stoppedFields tags i o
  | .misplaced f => status "rejected" ++ coded f.code f.text ++ (f.sentence?.toList.map fun i => ("sentence", toJson i))

def statementRequest (j : Json) : Except String (String × Case × String) := do
  VE.Bridge.exactFields j (["id", "environment", "lexicon", "kind", "source"] ++ optionalFields j)
  let id ← VE.Bridge.stringField j "id"
  unless (← VE.Bridge.stringField j "kind") == "blocks" do
    throw "InvalidInput: english.statement reads kind blocks or render"
  let c ← decodeCase j
  let source ← VE.Bridge.stringField j "source"
  pure (id, c, source)

def answer (id : String) (c : Case) (source : String) : Json :=
  let identities := Json.mkObj ([("source_sha256", .str (VE.CertificateWire.sha256 source.toUTF8))] ++ c.identities)
  let fields := match c.overlayFailure with
    | some f => invalidOverlayFields "english.statement" f
    | none => outcomeFields c (normTags c.E c.L) source (readNorm c.E c.O c.L workBudget source)
  VE.Route.Wire.ok id [("result", Json.mkObj (fields ++ [("identities", identities)]))]

def resultOf (row : Json) : Json := row.getObjValD "result"

end Run
```

`statementCase`, which dispatches on `kind`, and `statementCaseReported` follow kind `render`'s request in 2.5,
because `Norm/Run.lean` imports `Norm/Render.lean`.

**The route recipe's seven steps** (`docs/ROUTE-RECIPE.md`):
1. The runner is `Run.statementCaseReported`. The registry gains `Mode.englishStatement`, named `english.statement`,
   with its `modes` entry. `runMode .englishStatement j = Norm.Run.statementCaseReported j` holds by `rfl`
   (`runMode_englishStatement`), and is listed in `lean/VE/Audit.lean`. At EN-2, `statementCase` is kind `blocks`
   alone; EN-3 adds the dispatch on `kind` (2.5). The count of modes in `lean/VE/Service/RegistryExamples.lean` rises
   with the new entry, or its `#guard` fails (second report 1).
2. `lean/ResponseShape/Schemas/EnglishStatement.lean`: the row's shape, typed to the leaves. Its members per status
   are `statementFields`' (review 1). `status` is one of the seven words of the table above other than `rendered`;
   `rendered` joins them with EN-3's kind `render`, and EN-3 regenerates the schema. `code` is a member of the
   status's list in `statementStatusCodes`. `node` is the W1 norm wire object, and a rule row's `span` is a pair of
   naturals. `lean/ResponseShape/Schemas.lean` imports the shape, and `Skeletons.lean` gains the mode's skeleton and
   case.
3. `lean/ResponseShape/Encoders/EnglishStatement.lean` proves `statementCaseReported_fits` (section 4), which is listed
   in `lean/ResponseShapeAudit.lean`. It covers the rule rows' `span`, and at EN-3 both kinds. The every-mode theorem
   of `lean/ResponseShape/Encoders.lean` gains the mode's import and case.
4. The generated `ve/backends/lean_service_schema/english.statement.json` (`tools/response_schemas.py --write`), the
   regenerated `ve/english_grammar/codes.json` (english.statement's code rows, field table and unsentenced set, M9;
   `tools/english_codes.py`'s `from_lean` and `render` gain those members, verifier 2),
   and the mode's CPU deadline in `ve/backends/lean_service.py`'s `DEADLINES` (the same as `english.read`'s).
5. The Python relay (2.4).
6. Route fixtures recorded in `tests/data/route-cases.jsonl`, and the relay mutation gate's in
   `tests/data/relay-gate-cases.jsonl` (`tools/relay_mutation_gate.py --record`), because a route without an `ok` fixture
   fails that gate. The relay's reader joins the gate's `SERVICE_READERS`, and what stays accepted by design joins
   `tools/relay-gate-allow.json` (second report 1).
7. Fuzz tests `tests/test_english_statement_answer.py` (2.4). `_SCHEMA_SEEDS` of `tests/test_lean_service.py` gains the
   mode's seed, because its schema test samples every mode (second report 1).

In the product, `answer` reads `readNorm` and `normTags`. The stub states it once over a reader parameter
(`answerWith`, where `answer = answerWith ⟨readNorm, normTags⟩`), so that section 8 can compute rows for given reader
outcomes.

### 2.4 EN-2: the Python relay, the binding, the shadow and the delta report

**Relay.** `ve/norm_english.py`'s W1 path sends `{id, environment, lexicon, kind: "blocks", source}` through
`ve/backends/relay.py` (`answer`). It checks the answer with `ve/backends/service_schema.py` (step 4's schema). By R8,
Python checks the schema and the binding only. The binding:
- `id` is the request's; `identities.source_sha256` is the SHA-256 of the request's source; the other identities are
  bound as `english.read`'s relay binds them (`ve/backends/english_lean.py`);
- the members of each status are exactly those of `statementFields`, read from `ve/english_grammar/codes.json`
  (review 1); `code` is in its status's list there;
- for `one`: the rule rows' `number`s run 1, 2, …, k in row order, with no gap or repeat. Every `exception_to` entry,
  and each precedence row's `rule` and `over`, lies in 1 … k. Each rule row's `node.norm.name` is `rule-<number>`, and
  its `over` entries are `rule-<m>` with m in 1 … k. No row is empty, and no member is extra;
- for `one`, the rule rows' spans (review 8): exactly one `span` per rule row; `start < stop ≤` the source's byte
  length, with both ends on UTF-8 character boundaries of the source; and the spans strictly increasing in row
  order, none overlapping the next. The relay has no layout check, whole-line or any other: where a block may lie is
  Lean's (`english-lean-s6.md:520`; the layout rows are decided at the stop point, section 6). The relay converts
  each span to code points for the manifest check (EN-3, below);
- for `partial`: every span has `start < stop ≤` the source's byte length;
- for `rejected`: `sentence` is present exactly when `code` is not in `statementUnsentenced` (from `codes.json`), and
  is a natural number; `span` is bound as `english.read`'s relay binds it;
- `class` is the class the generated code table (`ve/english_grammar/codes.json`) gives `code`.

**The render binding** (EN-3, kind `render`; review 9). The request is `{id, environment, lexicon, kind: "render",
rules, guard_texts}`. For `rendered`: the number of `blocks` equals the number of the request's rules; no `header`
or `sentence` is empty; no row or member is extra. Python does not check that `text` is the blocks' `partsText`:
`render_text_parts` is Lean's theorem, and R8 bars Python from rechecking it (review 7).

**The manifest** (EN-3, `parse_english` with an export manifest; review 10). The manifest checks run only on `one`.
On any other status, Python relays Lean's refusal. Python keeps the renaming of `ve/norm_english.py:306-311`
(`existing_names`, `rule-<candidate>`) and the block mapping of :312-322, checked against Lean's rows. `blocks` are
the source's substrings at Lean's spans, in row order, and the block count check of :297-298 reads them. Each
manifest entry's `span` must equal both (a) Lean's span of that block converted to code points and (b) :314's
offset computed over those `blocks` (the code points of the blocks before it, each plus one for its line break).
The two agree for every manifest that `render_english` builds (:184-199), since there each block is one line and the
text holds no other line. A text with a standalone precedence line before rule 2 has a source offset for rule 2
that differs from :314's, so its manifest gives `IdentityMetadataMismatch` (fixture P4).

Anything else is `CheckerUnavailable`. For a rejection, the relay raises `relay.rejection(code, text)`, the class Lean
names with Lean's text.

**Fuzz tests** (`tests/test_english_statement_answer.py`; review 11). They mutate genuine recorded answers one and
two faults at a time: each member dropped, emptied, retyped or duplicated; rows reordered; a `number` pushed out of
range; a `name` changed. Each rule row's `span` is retyped and rebound by each condition of the span binding (a span
dropped or doubled, `start = stop`, an end past the source, an end off a UTF-8 boundary, two spans overlapping or out
of order). For kind `render`, every member of the request and of the answer, and every row of `blocks`, is retyped
and rebound (a block dropped or added, a header or sentence emptied). Every mutant is `CheckerUnavailable`, or
changes nothing the relay shows.

**Shadow (EN-2 only; review 12).** `parse_english`'s W1 path keeps its own reading as the answer. It also asks Lean
only when `VE_STATEMENT_COMPARATOR=1` is set (the precedent of `VE_ENGLISH_COMPARATOR`, `ve/english.py:1780`) and
`VE_SHADOW_LOG` is set too. It then appends one record to the log that `VE_SHADOW_LOG` names (the comparator precedent
of `ve/backends/english_lean.py:589-700`). The default `ve-shadow.jsonl` of `english_lean.py:665` is never reached,
because the shadow does not run without `VE_SHADOW_LOG`. Tests set `VE_SHADOW_LOG` under `tmp_path`. The shadow never
changes the answer. The record holds the source's SHA-256, Python's outcome (its nodes or its error class and
message), Lean's status, code and nodes, and exactly one class (review 13).

A `CheckerUnavailable` answer is a relay failure (Lean unreachable, or an answer that fails the schema or the binding)
or an answer whose code has class `CheckerUnavailable` (`Internal`, `InvalidGrammar`). The comparator tests
`lean-unavailable` first, and every other row reads only answers that are not `CheckerUnavailable`. So the classes
partition the records, and such an answer is always a delta row, never `both-refuse` or `lean-stricter` (verifier 3).
The wording of the ruling's item 13 has the same overlap; this order settles it and changes nothing else in the item.

| Class | Python | Lean |
|---|---|---|
| `lean-unavailable` | any | `CheckerUnavailable`; a delta row, listed by id in `delta.json` |
| `agree` | admits | `one`, and its nodes equal Python's rules after both are renamed `rule-i` by position |
| `lean-unknown` | admits | `budget`, or any code of class ResourceLimit (`NodeLimit`, `NestingLimit`, …) |
| `lean-stricter` (a changed rejection) | admits | neither `one` nor a `lean-unknown` answer |
| `lean-looser` | refuses | `one` |
| `different-node` | admits | `one`, and the nodes differ |
| `both-refuse` | refuses | anything other than `one`, UNKNOWN included; the record keeps both codes |

A Lean answer's class (CheckerUnavailable, ResourceLimit or other) is the one `codes.json` gives its code; the
comparator keeps no class table of its own.

**Delta report** (saved evidence, `docs/en-e3-norm/en-2/`):
- `delta.json`: the commit; the corpora, each listed by name and size; for each corpus, the count of each class; and
  every row of a class other than `agree` and `both-refuse`, with its corpus, id, source SHA-256 and both outcomes.
  `lean-unavailable` rows are listed by id there (review 13). The corpora are:
  - the suite's `parse_english` calls (one run with `VE_STATEMENT_COMPARATOR=1` and `VE_SHADOW_LOG` set to a scratch
    log path, as `tools/lean_first_diff.py:373` does);
  - the soft and rights calls that reach the W1 path with `_w1=True`: `_parse_soft_english` (`:542`) and
    `_render_soft_english` (`:613`), reached also through `ve/surface/rights.py:44` (review 15);
  - the 120 pinned blocks (`tests/data/norm-blocks/rsp.jsonl` 76, `fsf.jsonl` 44);
  - the constitution and UDHR units with an English round trip.
- Every block whose Lean answer is `NodeRefused` or `NodeLimit` is a row of `delta.json` (review 4).
- `DELTA.md`: one row per `delta.json` row, with its class, and a column for the DRI's decision on every row
  (section 6). `lean-unknown` rows have their own section and are not decided as rejections. The known differences of
  english-lean-s6.md section 5 (empty text, layout, casing, the sort-three-times predicate) appear here as rows, not
  as fixes.
- The report and its tests read only these saved files, never a live run against a moving HEAD.

**Tests the en-e3 task file keeps and adds** (DRI 2026-11-02 item 2):
- `tests/test_english_statement_blocks.py` (the 120-block comparison) stays selected;
- `tests/test_english_statement_shadow.py` (new), the shadow agreement test. It reads `delta.json` and checks that
  each pinned block's recorded class is `agree`, or is a row of DELTA.md with that class. It checks that every record
  has exactly one class (review 13), and that the per-class counts sum to the corpus size. It checks the comparator
  on fixed records too: the classes of fixture E14, a `CheckerUnavailable` answer under both Python outcomes included
  (verifier 3), and that with `VE_STATEMENT_COMPARATOR=1` and no `VE_SHADOW_LOG` Lean is not called and no file is
  written in the working directory (fixture P5).

### 2.5 EN-3: authority, rendering, deletions

**Needs** the DRI's decision on EN-2's delta.

**Authority.** The W1 part of `english.statement` moves into its own manifest operation, `english.statement.w1`:
- `authority: lean`;
- lean: `ve_service english.statement`;
- theorems: section 4's EN-2 and EN-3 statements, plus en-s6b's `readNorm_sound`, `readNorm_unique`,
  `readNorm_complete`, `readNorm_numbered`, `readNorm_authoring`, `readNorm_regulated` and `toNode_fields`;
- python: the W1 relay (`ve.norm_english:parse_w1_english`, the W1 path of `parse_english` moved into one function)
  and the render relay (`ve.norm_english:render_english`'s W1 path).
- probes: `conformance/binding_probes.py`'s `BUILDERS` gains one hand-written accepted case for each binding key,
  `("english.statement.w1", "ve_service", "english.statement", kind)` for kinds `blocks` and `render`:
  `test_every_lean_binding_has_a_probe` (`tests/test_assurance_manifest.py:416`) requires the binding keys to equal
  `BUILDERS` exactly, so the manifest edit fails that test until they are added (third report).

`english.statement` keeps its other readers (`parse_statement_english`, `require_unique_derivation`, and the soft
path until EN-4).

**Every caller of the W1 path, and where it goes at EN-3** (review 16):
- `parse_english` and `render_english` with `_w1=True`, called by `_parse_soft_english` (`ve/norm_english.py:542`)
  and `_render_soft_english` (`:613`), and through them by `ve/surface/rights.py:44`. At EN-3 these calls go to Lean:
  the soft path's W1 text is read and rendered by the mode. EN-2's shadow corpus holds them (2.4), so their changes
  are delta rows the DRI decided.
- `_consequence` (`:90-109`), called from `_soft_consequence` (`:378`), `_soft_rewrite_consequence` (`:399`),
  `_render_soft_english` (`:621`) and, through `_soft_consequence`, `ve/surface/rights.py:119`. Only its W1 call sites
  go at EN-3 (`_block_grammar` :223, `_parse_consequence` :255, `render_rule_sentence`'s strict branch :161). The
  function stays, for the soft path, until EN-4.
- `_parse_guard` (`:54-73`), called from `parse_english` (`:339-340`) and `_parse_soft_notes` (`:468`). Only its W1
  call sites (`:339-340`) go at EN-3. The function stays, for the soft notes, until EN-4 (verifier 1).
- `render_rule_sentence` (`:155-171`), called from `ve/surface/rights.py:149`, `ve/document/render.py:109, :118` and
  `ve/readings_route.py:1185, :1270`. Its strict branch goes to Lean (below). Its soft branch (`_soft_consequence`,
  :159) stays until EN-4.

`_consequence`, `_parse_guard` and the soft branch of `render_rule_sentence` are recorded under an E2 ledger row
(`docs/lean-first/e2/LEDGER.md`) that names EN-4 as their deletion.

**Rendering** (`lean/VE/EnglishGrammar/Norm/Render.lean`, new; kind `render` of the mode). The request carries the
document's rules (the W1 wire's rule objects) and one `GuardTexts` per rule. These hold the guard's English (`null`
for `top`) and each carve-out's, from Python's `_guard_text`. Lean numbers the rules by position and writes each
header from the `over` targets' positions. It takes the consequence from en-s6b's wordings and builds the block frame
as `render_english` and `render_rule_sentence` lay it out. It then reads the whole text back.

```lean
/-- Rule `i` of a document is `ruleName (i + 1)`; each `over` entry becomes its target's `ruleName`. -/
def numbered (nds : List VE.Norms.Node) : Except String (List VE.Norms.Node) :=
  let names := nds.map (·.name)
  ((List.range nds.length).zip nds).mapM fun (i, nd) => do
    let over ← nd.over.mapM fun o => match names.idxOf? o with
      | some k => pure (ruleName (k + 1))
      | none => throw s!"UnknownRule: rule {nd.name} is an exception to {o}, which is not a rule of the document"
    pure { nd with name := ruleName (i + 1), over }

/-- The producer's English of one rule's guard (`none` for `top`) and carve-outs (Python's `_guard_text`;
untrusted: Lean reads the whole text back). -/
structure GuardTexts where
  guard : Option String
  carveOuts : List String

def headerText (names : List String) (i : Nat) (nd : VE.Norms.Node) : Except String String := do
  let refs ← nd.over.mapM fun o => match names.idxOf? o with
    | some k => pure (toString (k + 1))
    | none => throw s!"UnknownRule: rule {nd.name} is an exception to {o}, which is not a rule of the document"
  pure <| match refs with
    | [] => s!"Rule {i}."
    | [k] => s!"Rule {i} (exception to rule {k})."
    | ks => s!"Rule {i} (exception to rules {", ".intercalate ks})."

/-- The header and the rule sentence of rule `i`, in `render_rule_sentence`'s layout. -/
def renderBlockWith (cw : String → Bool → List String) (names : List String) (i : Nat) (nd : VE.Norms.Node)
    (g : GuardTexts) : Except String (String × String) := do
  let header ← headerText names i nd
  let some consequence := (cw nd.pred nd.sign).head?
    | throw s!"NoWording: rule {nd.name}'s predicate {nd.pred} has no consequence wording"
  unless g.carveOuts.length == nd.carveOuts.length do
    throw s!"InvalidInput: rule {nd.name} has {nd.carveOuts.length} carve-outs and {g.carveOuts.length} texts"
  let guard := match g.guard with | some t => ", if " ++ t | none => ""
  let inline := match g.carveOuts with | [u] => ", unless " ++ u | _ => ""
  let after := match g.carveOuts with
    | [] | [_] => ""
    | us => " " ++ " ".intercalate (us.map fun u => "Except when " ++ u ++ ".")
  pure (header, consequence ++ guard ++ inline ++ "." ++ after)

def renderPartsWith (cw : String → Bool → List String) (nds : List VE.Norms.Node) (gs : List GuardTexts) :
    Except String (List (String × String)) := do
  unless nds.length == gs.length do throw "InvalidInput: one guard text entry is required for each rule"
  let names := nds.map (·.name)
  ((List.range nds.length).zip (nds.zip gs)).mapM fun (i, nd, g) => renderBlockWith cw names (i + 1) nd g

/-- The document's text: each block is its header, a space and its sentence; blocks are joined by line breaks. -/
def partsText (ps : List (String × String)) : String := "\n".intercalate (ps.map fun (h, t) => h ++ " " ++ t)

def renderParts (E : Env) (L : Lexicon) (nds : List VE.Norms.Node) (gs : List GuardTexts) :
    Except String (List (String × String)) := renderPartsWith (consequenceWordings E L) nds gs

def renderDocument (E : Env) (L : Lexicon) (nds : List VE.Norms.Node) (gs : List GuardTexts) :
    Except String String := partsText <$> renderParts E L nds gs

/-- The rendered text, only if Lean reads the whole text back to the document's rules, renumbered by position. -/
def renderChecked (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (nds : List VE.Norms.Node)
    (gs : List GuardTexts) : Except String String := do
  let s ← renderDocument E L nds gs
  let want ← numbered nds
  match readNorm E O L b s with
  | .ok rs => match toNodesChecked rs with
    | .ok got => if got = want then pure s else throw "RenderMismatch: the rendered text reads as other rules"
    | .error e => throw ("RenderMismatch: " ++ e)
  | _ => throw "RenderUnread: the rendered text is not read as rule blocks"

/-- The code of an error text `"<Code>: <text>"`. -/
def codeOf (e : String) : String := (e.splitOn ": ").headD e

/-- The result fields of kind `render`: the checked text and each block's header and sentence, or the refusal. -/
def renderFields (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (nds : List VE.Norms.Node) (gs : List GuardTexts) :
    List (String × Json) :=
  match renderChecked E O L b nds gs, renderParts E L nds gs with
  | .ok t, .ok ps => VE.EnglishGrammar.Run.status "rendered" ++ [("text", .str t),
      ("blocks", Json.arr (ps.map fun (h, s) => Json.mkObj [("header", .str h), ("sentence", .str s)]).toArray)]
  | .ok _, .error e | .error e, _ => VE.EnglishGrammar.Run.status "rejected" ++ VE.EnglishGrammar.Run.coded (codeOf e) e
```

Draft 1's per-block `renderChecked` cannot hold. "Rule 1." and its rule sentence are two sentences, and a lone
"Rule 2." is refused (`expectedRule`). This version renders the whole document and reads it back. The render codes
`RenderUnread`, `RenderMismatch` and `NoWording` (class `CheckerUnavailable`: Lean could not certify its own display),
and `InvalidInput` (class `VEError`), join `Run.codeClasses` with EN-3's hunk (`renderCodeRows`), and `rendered` and
these four join `statementStatusCodes` (review 2). `UnknownRule` is already there.

**Layers** (second report 1). `renderFields` reads `Run.status` and `Run.coded`, so `Norm/Render.lean` imports the
layer-4 `Run.lean`. Fixture R10 reads `statementStatusCodes`, which is in the same file (M9), so
`Norm/RenderExamples.lean` imports it too. `lean_layer` (`tools/layer_policy.py:186`) places both modules in layer 3,
and `tools/check_lean_imports.py` refuses an import from a lower layer. EN-3 therefore gives
`VE.EnglishGrammar.Norm.Render` its own layer-4 row, as `VE.Question.Spans` has (:177), and adds
`VE.EnglishGrammar.Norm.RenderExamples` to the runner-boundary fixtures of :161, as EN-2 does for
`Norm/RunExamples.lean`.

**Kind `render` on the wire** (`Norm/Run.lean`; review 7). The request has exactly the members `id`, `environment`,
`lexicon`, `kind` (`"render"`), `rules` and `guard_texts`, plus `optionalFields`. The decoder refuses any extra member
and any other kind. `statementCase` dispatches on `kind`. A render answer's `identities` are `decodeCase`'s.

```lean
namespace Run
open VE.EnglishGrammar.Run (Case decodeCase optionalFields invalidOverlayFields)

/-- One rule's guard texts: `{"guard": <string or null>, "carve_outs": [<string>, …]}`. -/
def guardTextsOf (j : Json) : Except String GuardTexts := do
  VE.Bridge.exactFields j ["guard", "carve_outs"]
  let guard ← match j.getObjValD "guard" with
    | .null => pure none
    | .str t => pure (some t)
    | _ => throw "InvalidInput: a guard text is a string or null"
  let carveOuts ← match j.getObjValD "carve_outs" with
    | .arr xs => xs.toList.mapM fun
      | .str t => pure t
      | _ => throw "InvalidInput: a carve-out text is a string"
    | _ => throw "InvalidInput: carve_outs is an array"
  pure ⟨guard, carveOuts⟩

/-- The request of kind `render`: exactly `id`, `environment`, `lexicon`, `kind`, `rules` (the W1 wire's rule
objects) and `guard_texts`, plus `english.read`'s optional members. -/
def renderRequest (j : Json) : Except String (String × Case × List VE.Norms.Node × List GuardTexts) := do
  VE.Bridge.exactFields j (["id", "environment", "lexicon", "kind", "rules", "guard_texts"] ++ optionalFields j)
  let id ← VE.Bridge.stringField j "id"
  unless (← VE.Bridge.stringField j "kind") == "render" do
    throw "InvalidInput: english.statement reads kind blocks or render"
  let c ← decodeCase j
  let nds ← match j.getObjValD "rules" with
    | .arr xs => xs.toList.mapM fun x => VE.Norms.Wire.decodeNorm x
    | _ => throw "InvalidInput: rules is an array"
  let gs ← match j.getObjValD "guard_texts" with
    | .arr xs => xs.toList.mapM guardTextsOf
    | _ => throw "InvalidInput: guard_texts is an array"
  pure (id, c, nds, gs)

def renderAnswer (id : String) (c : Case) (nds : List VE.Norms.Node) (gs : List GuardTexts) : Json :=
  let fields := match c.overlayFailure with
    | some f => invalidOverlayFields "english.statement" f
    | none => renderFields c.E c.O c.L workBudget nds gs
  VE.Route.Wire.ok id [("result", Json.mkObj (fields ++ [("identities", Json.mkObj c.identities)]))]

/-- The mode dispatches on `kind`: `render`, or else kind `blocks` (which refuses every other kind). -/
def statementCase (j : Json) : Except String Json := do
  if j.getObjValD "kind" == .str "render" then
    let (id, c, nds, gs) ← renderRequest j
    pure (renderAnswer id c nds gs)
  else
    let (id, c, source) ← statementRequest j
    pure (answer id c source)

def statementCaseReported (j : Json) : Json :=
  match statementCase j with
  | .ok row => row
  | .error message => Json.mkObj [("id", j.getObjValD "id"), ("status", .str "error"), ("error", .str message)]

end Run
```

Python after EN-3:
- `parse_english`'s W1 path is the relay (`parse_w1_english`). Its manifest checks are those of 2.4 (review 10), on
  `one` only; on any other status it relays Lean's refusal. `:343-349` builds the norms from Lean's nodes, with the
  names of the renaming or the manifest.
- `render_english` sends the rules and the guard texts and builds its export manifest (handles, line spans, text
  digest) from Lean's text, as identity metadata.
- `render_rule_sentence`'s strict branch (a strict rule outside a layer) sends a one-rule document with `over` cleared
  and shows its block's `sentence`.

**Deleted** from `ve/norm_english.py` in the same change (review 17; these replace draft 1's "(:207, :303-340)" and
"(:90-109)"):
- `:283-296`: the line split, the standalone precedence regex with its `require_unique_derivation` call, and the
  `UnknownRule` display check (Lean owns these decisions);
- `:303-305`: the `_HEADER` match and its `Expected Rule` error;
- `:323-342`: the reference parse, the clause string splits, `_parse_consequence`'s and `_parse_guard`'s calls, and the
  block's `require_unique_derivation` call;
- `:346-347`: the second `UnknownRule` check;
- `_HEADER` (`:207`), `_parse_consequence` (`:248-268`), and `_block_grammar` and its Lark audit (`:210-245`).

Rewritten: `:297-322`, as 2.4's manifest paragraph states (the block count, the renaming and the block mapping against
Lean's rows and spans). Kept: `:343-349`, building the norms from Lean's nodes. `_consequence` (`:90-109`) and
`_parse_guard` (`:54-73`) are not deleted; only their W1 call sites go (above), and EN-4 deletes both with the soft
path. `_guard_text` stays as the producer. The E2 ledger (`docs/lean-first/e2/LEDGER.md`) records the rows.

`parse_english` then calls no Python reader, so `tests/test_english_e2_ledger_sites.py` drops its site from `KEPT`;
the `_parse_guard` site stays until EN-4.

`tools/relay_lint.py` does not change at EN-3 (second report 2). `RELAYED_FUNCTIONS` gains neither relay, because the
lint refuses a raise with a function's own text and both relays keep such raises. The W1 relay keeps the type check
(`:276`), 2.4's manifest checks (`:280`, `:298`, `:319`, `:365`) and `GuardOnOwnOutcome` (`:356`). `render_english`
keeps its handle check (`:181`).

**Tests.**
- A test asserts that `ve/norm_english.py` has no block parser left: no `_parse_consequence`, no `_block_grammar`, no
  `_HEADER`, and no W1 call of `_consequence` or `_parse_guard`. It does not require either function to be absent
  (review 16; verifier 1).
- A soft block with a "Rule n is excepted when …" note still reads after EN-3, through `_parse_soft_notes` and
  `_parse_guard` (verifier 1).
- An unavailable Lean gives `CheckerUnavailable` for both `parse_english` and `render_english`, never a Python reading.
- The manifest and render binding fixtures P1 to P4 (section 8).

The first three go in `tests/test_norm_english.py`.

**Existing tests EN-3 edits** (second report 1). Each pins what a deleted line did, and moves to Lean's class and text.
No test gains a Python message.
- `tests/test_norm_english.py`: `:8` imports `_block_grammar`, so the whole module fails at collection until that
  import goes, and `test_norm_block_grammar_uses_normalized_english_input` (`:33-37`) goes with the function. The
  `match`es of `:59-62` and `:71` are `_parse_consequence`'s text (`:267`), `:108`'s is `require_unique_derivation`'s
  (`:341`), and `:145-148`'s is the deleted `UnknownRule` check (`:296`): Lean's text does not hold that word.
- `tests/test_english_unambiguity.py:292`: W1's half of the test, on `_parse_consequence`'s text. `:377` stays until
  EN-4, because it reaches the soft reader's text (`:424`).
- `tests/test_numeral_conversion.py:111-115`: W1's half pins `ResourceLimit` from `ast.numeral_value` (`:290`, `:304`,
  `:323`, all deleted). Lean's lexer reads a numeral of any length (`digitsValue`, `Lexer.lean:78`). The soft half
  stays until EN-4.
- `tests/test_risk_english.py` (`:111-112`, `:119-120`, `:127-130`, `:147-155`) and
  `tests/test_alternatives_profile.py:541`: rule guards' `match`es on Python's advice, which `_parse_guard`'s W1 calls
  raised. english.statement has no `advice` member (`statementFields`; `refusalExtras` is `english.read`'s and
  `senses.read`'s), so a rule guard's `none` answer gives Lean's text alone. A lost rewrite is a `diagnostic` entry of
  the shadow record, not a delta row (section 5).

### 2.6 Contracts fixed for EN-5, EN-7 and EN-10 (stated and type-checked here; en-e3 builds none of them)

These are the round-3 items that the DRI's orders list beside EN-2 and EN-3. EN-2 and EN-3 carry two of them: the span
gate (2.2) and the whole-document check (2.5). The rest bind later batches. Their statements are fixed here, so that
those batches build against a reviewed contract.

```lean
/-- EN-7: the span's owner is its row's meaning owner (`unowned` for a placeholder row), never this plan. -/
def rowKeyText (row : SourceWordRow) : String := row.word ++ "|" ++ row.frame ++ "|" ++ row.profile

def ownerOk (R : List SourceWordRow) (u : UnformalisedSpan) : Bool :=
  R.any fun row => rowKeyText row == u.row && row.owner == u.owner && row.owner != "en-e3-norm"

def UnformalisedSpan.covers (u : UnformalisedSpan) (k : Nat) : Bool := u.start ≤ k && k < u.stop

/-- EN-7: every span is nonempty and inside the sentence, and no byte is in two spans; the read part is the rest,
so read part and spans partition the sentence's bytes. -/
def spansPartition (s : String) (us : List UnformalisedSpan) : Bool :=
  us.all (fun u => u.start < u.stop && u.stop ≤ s.utf8ByteSize) &&
  (List.range s.utf8ByteSize).all fun k => (us.filter (·.covers k)).length ≤ 1

/-- EN-7: the restricting mark of a span's row (recorded data; it licenses nothing). -/
opaque restricting (R : List SourceWordRow) (u : UnformalisedSpan) : Bool

/-- EN-5: one matched readings-row of the sentence's one structure. -/
structure Slot where
  key : String
  candidates : List SourceWordReading

/-- A slot as `VE.Discourse.allChoices` reads it: id, version and number of readings (scope's `shapeOf`). -/
def slotShape (sl : Slot) : VE.Route.Admission.ReadingSet := ⟨sl.key, 0, sl.candidates.map fun _ => .top⟩

/-- Every combination of the slots' candidates, in `allChoices` order; `none` over the W2 limit (UNKNOWN). -/
def choicesOf (slots : List Slot) : Option (List VE.Discourse.Choice) :=
  if VE.Discourse.productSize (slots.map slotShape) > VE.Readings.maxChoices then none
  else some (VE.Discourse.allChoices (slots.map slotShape))

inductive CandReading where
  | rule (A : NormStatement)
  | noRule (reason : String)
  | pending (code : String)

structure Candidate where
  rows : List String               -- every row that contributed, one per slot, in slot order
  choice : VE.Discourse.Choice     -- the combination it is
  wording : String
  reading : CandReading

inductive SourceOutcome where
  | one (A : NormStatement)
  | readings (cs : List Candidate)                              -- a W2 authored set (PLANS-INDEX D11)
  | mixed (A : NormStatement) (spans : List UnformalisedSpan)   -- its own outcome, never `.one`
  | unformalised (spans : List UnformalisedSpan) (why : String)
  | parses (t u : VE.Grammar.Tree Tok)
  | refused (code advice : String)
  | limit                                                       -- UNKNOWN

opaque readSource (E : Env) (O : Overlay) (L : Lexicon) (R : List SourceWordRow) (b : Nat) (s : String) :
  SourceOutcome
opaque slotsOf (E : Env) (L : Lexicon) (R : List SourceWordRow) (s : String) : List Slot

/-- EN-5: a candidate refused for its route carries the gate's text (`VE.Compose.gateOf`; PC-4's
`Matrix.documentRefusal` once it lands); no `JoinRoute` code. -/
def routeRefusal (ps : List String) : Option String :=
  match VE.Compose.gateOf VE.Compose.profileTable ps with
  | .ok _ => none
  | .error e => some e

/-- EN-10: what the reader's reading is compared with. -/
inductive Field where
  | force | mode | sign | predicate | guard | carveOuts | setNotCollapsed | hiddenResidual (word : String)
  | bearerNote

/-- EN-10's results (NEW under PLANS-INDEX D8). `partialSpans` is the wire word `partial`. -/
inductive CheckResult where
  | verified
  | partialSpans (spans : List UnformalisedSpan)
  | pending (codes : List String)
  | mismatch (fields : List Field)
  | unread (code : String)
  | unknown

def contentNode : VE.Compose.Content → Option VE.Norms.Node
  | .norm N => some N.toNode
  | _ => none

/-- The hand rules of unit `u` of W2 document `D`: a fixed unit's rule, or every candidate of its set (before any
narrowing: the narrowings are cited in `D`, never silent). -/
def handNodes (D : VE.Readings.Doc) (u : String) : List VE.Norms.Node :=
  D.items.flatMap fun
    | .fixed u' c _ => if u' == u then (contentNode c).toList else []
    | .set R => if R.unit == u then R.candidates.filterMap (fun a => a.content.bind contentNode) else []
    | .bar _ _ => []

def handPending (D : VE.Readings.Doc) (u : String) : Nat :=
  D.items.foldl (fun n it => match it with
    | .set R => if R.unit == u then n + (R.candidates.filter (·.content.isNone)).length else n
    | _ => n) 0

def ruleCandidateNodes (cs : List Candidate) : Except String (List VE.Norms.Node) :=
  (cs.filterMap fun c => match c.reading with | .rule A => some A | _ => none).flatMapM fun A => toNodes [A]

def pendingCodes (cs : List Candidate) : List String :=
  cs.filterMap fun c => match c.reading with | .pending k => some k | _ => none

def pendingCount (cs : List Candidate) : Nat := (pendingCodes cs).length

def sameSet (a b : List VE.Norms.Node) : Prop := (∀ x ∈ a, x ∈ b) ∧ ∀ x ∈ b, x ∈ a

opaque checkHand (E : Env) (O : Overlay) (L : Lexicon) (R : List SourceWordRow) (b : Nat) (s : String)
  (D : VE.Readings.Doc) (u : String) : CheckResult
```

Their theorems are in section 4, part C. The plan's EN-5, EN-7 and EN-10 Lean blocks restate them with the names
above. Two plan statements need parse-tree names that only EN-5 defines (`span_elsewhere`'s `uniqueParse` and
`forceAt`; `candidates_from_rows`'s `fillHoles`, `slotWordings`, `sourceParts` and `profilesOf`). They are not stubbed
here, and EN-5 and EN-7 bind them.

## 3. English: one reading each

### 3.1 What the answers say

- **`one`.** Lean read every sentence of the text in exactly one way. The sentences group into these rule blocks and
  precedence lines, in this order. Each rule is this W1 node. Rule n is named `rule-n`, and its `over` is its
  header's targets, then its precedence lines' targets. Rule n's block occupies the bytes of its `span` in the text:
  from the first byte of its header sentence to the period of its last sentence.
- **`partial`.** Lean read the text, and some sentence holds a phrase that it parsed and did not formalise (listed in
  `spans`, with each phrase's row and meaning owner). No rule is made from it. In authoring mode this never happens.
- **`rejected` with `NodeRefused`.** Lean read the text, and the W1 decoder refused the node of a rule for its form.
  The decoder's own text says why, for example "invalid indexed formula". No rule is made.
- **`rejected` with `NodeLimit`.** Lean read the text, and a rule's node is larger than the W1 decoder's limits
  (depth 64, or 10,000 nodes). The decoder's text says which. No rule is made. The text is refused at a resource
  limit, as `NestingLimit` refuses it in `english.read`; it is not a finding about the text's meaning.
- **`rejected` with `Internal` and no sentence.** The checker failed: the reader's statements are not the text's rule
  blocks and precedence lines, or the reader found no meaning for a derivation. Neither is expected with en-s6b's
  reader; the class is `CheckerUnavailable`.
- **`rejected` with a block code.**
  - `ExpectedRule`: sentence i opens a block with the wrong number.
  - `NoConsequence`: a header has no rule sentence.
  - `StrayConsequence`: a rule sentence stands outside a block, or is a second one in its block.
  - `StrayCarveOut`: an "Except when" sentence comes before its block's rule sentence.
  - `UnknownRule`: a header or a precedence line names a rule the text does not have.
- **`none`, `many`, `budget`.**
  - `none`: sentence i has no reading as a block sentence.
  - `many`: sentence i has two readings, and two trees are shown.
  - `budget`: the reader stopped at its work limit on sentence i. This is UNKNOWN, not a refusal of the text.
- **`rendered`.** Lean wrote this text for the document's rules and read the whole text back to those same rules,
  renumbered by position. Each block's header and sentence are also given.

### 3.2 The theorems in plain words

- `opOf_agrees`: wherever a consequence's polarity fits its predicate's role, the reader's stored sign is act phrases'
  op for that role and sign. So `Force` adds no modal meaning of its own.
- `soft_strict_iff`: a clause is strict in soft-norms' sense exactly when its mode is `strict`.
- `sourceView_nil`: with no source spellings, the view is the environment and the lexicon unchanged.
- `toNodeChecked_ok`: the gate gives a node exactly when the clause has no span and the decoder gives that node.
  `toNodesChecked_ok` is the same for a whole text.
- `toNodesChecked_authoring`: for an authored text (`readNorm_authoring`), the gate changes nothing.
- `statementStatusCodes_classed`: every code the mode can answer, EN-3's included, has a class in the one table.
  `statementFields_statuses`: the field table has exactly the code table's statuses, in its order.
- `answer_one_iff`: the answer is `one` exactly when no overlay failure, `readNorm` read the text, every rule
  passed the gate and the decoder, and the text's sentences give one span per statement and no statement is
  translation mode's. `answer_one_rows`: then the rows are exactly the statements, each with its span, and each node
  is the decoder's.
- `answer_partial_no_node`: a `partial` answer has no statement rows, and its spans are the text's spans.
- `answer_stopped`, `answer_misplaced`: a stop is never `one`. It names its sentence exactly when `stopNamesSentence`
  holds, which is for every stop but the engine's impossible `.ok` and a rejection with an unsentenced code. A block
  fault gives its code.
- `statementCaseReported_fits`: every row the mode writes, of either kind, fits the generated shape.
- `render_fits`: every row of kind `render` fits the shape, and every code a render refusal carries is one of the
  table's `rejected` codes.
- `renderChecked_reads_back`: a checked rendering is the rendered text of the document, and Lean reads it back to the
  document's renumbered rules.
- `render_rendered_iff`: the render answer is `rendered` exactly when the check passes. `render_text_parts`: the text
  is its blocks' headers and sentences.
- Part C (later batches): candidates are every combination (`readings_complete`), UNKNOWN over the limit
  (`readings_budget`); `.one` has no span; MIXED has spans that partition the sentence and name their owners; check
  mode verifies only against the whole set, answers `partial` for MIXED, `pending` for a pending-only set, `unknown`
  at the limit, and `unread` only when the reader read nothing.

## 4. Lean: the exact statements

Namespace `VE.EnglishGrammar.Norm`. Part A is `Norm/Owners.lean` and `Norm/Run.lean` (EN-2), part B is
`Norm/Render.lean` (EN-3), and part C is the later batches' contracts. In the stub, each statement is
`def X : Prop := …`, and the ones proved there say so.

```lean
-- A. EN-2
theorem opOf_agrees : ∀ (r : VE.Norms.Regulated) (p : Polarity),
  p.fits r.role = true → VE.Acts.opOf r p.sign = p.op?                                          -- proved in the stub

theorem soft_strict_iff : ∀ m : Mode, m.soft = .strict ↔ m = .strict                          -- proved in the stub

theorem sourceView_nil : ∀ (E : Env) (L : Lexicon), sourceView E L [] = (E, L)                -- proved in the stub

theorem toNodeChecked_ok : ∀ (n : String) (o : List String) (c : Clause) (nd : VE.Norms.Node),
  c.toNodeChecked n o = .ok nd ↔ c.residuals = [] ∧ c.toNode n o = .ok nd                        -- proved in the stub

theorem toNodesChecked_ok : ∀ (rs : List NormStatement) (nds : List VE.Norms.Node),
  toNodesChecked rs = .ok nds ↔ spansOf rs = [] ∧ toNodes rs = .ok nds                           -- proved in the stub

/-- From en-s6b's `readNorm_authoring` (stated in the stub as `ReadNormAuthoring`). -/
theorem toNodesChecked_authoring : ReadNormAuthoring →
  ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (s : String) (rs : List NormStatement),
    readNorm E O L b s = .ok rs → toNodesChecked rs = toNodes rs                                  -- proved in the stub

theorem Run.statementStatusCodes_classed : ∀ s ∈ Run.statementStatusCodes, ∀ c ∈ s.2,
  ((VE.EnglishGrammar.Run.codeClasses ++ Run.statementCodeRows ++ Run.renderCodeRows).lookup c).isSome = true
                                                                                                -- `decide`, in the stub

theorem Run.statementFields_statuses :
  Run.statementFields.map (·.1) = Run.statementStatusCodes.map (·.1)                             -- `decide`, in the stub

theorem Run.answer_one_iff : ∀ (id : String) (c : Case) (s : String),
  (Run.resultOf (Run.answer id c s)).getObjValD "status" = .str "one" ↔
    c.overlayFailure = none ∧ ∃ rs nds sps, readNorm c.E c.O c.L workBudget s = .ok rs ∧
      toNodesChecked rs = .ok nds ∧ Run.oneSpans s rs = some sps

theorem Run.answer_one_rows : ∀ (id : String) (c : Case) (s : String) (rs : List NormStatement)
    (nds : List VE.Norms.Node) (sps : List (Nat × Nat)),
  c.overlayFailure = none → readNorm c.E c.O c.L workBudget s = .ok rs → toNodesChecked rs = .ok nds →
  Run.oneSpans s rs = some sps →
  (Run.resultOf (Run.answer id c s)).getObjValD "statements" =
    Json.arr ((rs.zip sps).map fun (r, sp) => Run.statementRow rs sp r).toArray ∧
  ∀ h cl, NormStatement.rule h cl ∈ rs →
    VE.Norms.Wire.decodeNorm (cl.wire (ruleName h.number) ((overOf rs h.number).map ruleName)) =
      cl.toNode (ruleName h.number) ((overOf rs h.number).map ruleName)

theorem Run.answer_partial_no_node : ∀ (id : String) (c : Case) (s : String),
  (Run.resultOf (Run.answer id c s)).getObjValD "status" = .str "partial" →
    (Run.resultOf (Run.answer id c s)).getObjValD "statements" = .null ∧
    ∃ rs, readNorm c.E c.O c.L workBudget s = .ok rs ∧ spansOf rs ≠ [] ∧
      (Run.resultOf (Run.answer id c s)).getObjValD "spans" = Json.arr ((spansOf rs).map Run.spanRow).toArray

theorem Run.answer_stopped : ∀ (id : String) (c : Case) (s : String) (i : Nat)
    (o : VE.Grammar.Outcome Tok Reject Piece),
  c.overlayFailure = none → readNorm c.E c.O c.L workBudget s = .stopped i o →
    (Run.resultOf (Run.answer id c s)).getObjValD "status" ≠ .str "one" ∧
    (Run.resultOf (Run.answer id c s)).getObjValD "sentence" =
      (if Run.stopNamesSentence o then toJson i else Json.null)

theorem Run.answer_misplaced : ∀ (id : String) (c : Case) (s : String) (f : BlockFault),
  c.overlayFailure = none → readNorm c.E c.O c.L workBudget s = .misplaced f →
    (Run.resultOf (Run.answer id c s)).getObjValD "code" = .str f.code ∧
    (Run.resultOf (Run.answer id c s)).getObjValD "status" = .str "rejected"

-- ResponseShape.Encoders.EnglishStatement (recipe step 3); `Skeletons.englishStatement` is generated in step 2.
-- Both kinds: `Run.statementCaseReported` dispatches on `kind` (2.5).
theorem statementCaseReported_fits : ∀ j : Json,
  ResponseShape.Fits j ResponseShape.Skeletons.englishStatement (Run.statementCaseReported j)

-- VE.Service (recipe step 1; the constructor is new, so the stub cannot state it: EN-2's build checks it)
theorem runMode_englishStatement (j : Json) :
  VE.Service.runMode .englishStatement j = VE.EnglishGrammar.Norm.Run.statementCaseReported j := rfl

-- B. EN-3
theorem renderChecked_reads_back : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat)
    (nds : List VE.Norms.Node) (gs : List GuardTexts) (s : String),
  renderChecked E O L b nds gs = .ok s →
  ∃ rs want, numbered nds = .ok want ∧ readNorm E O L b s = .ok rs ∧ toNodesChecked rs = .ok want ∧
    renderDocument E L nds gs = .ok s                                                             -- proved in the stub

theorem render_rendered_iff : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (nds : List VE.Norms.Node)
    (gs : List GuardTexts),
  (Json.mkObj (renderFields E O L b nds gs)).getObjValD "status" = .str "rendered" ↔
    ∃ t, renderChecked E O L b nds gs = .ok t

theorem render_text_parts : ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (nds : List VE.Norms.Node)
    (gs : List GuardTexts) (t : String),
  renderChecked E O L b nds gs = .ok t → ∃ ps, renderParts E L nds gs = .ok ps ∧ t = partsText ps

-- ResponseShape.Encoders.EnglishStatement (review 7)
theorem render_fits :
  (∀ j : Json, j.getObjValD "kind" = .str "render" →
    ResponseShape.Fits j ResponseShape.Skeletons.englishStatement (Run.statementCaseReported j)) ∧
  ∀ (E : Env) (O : Overlay) (L : Lexicon) (b : Nat) (nds : List VE.Norms.Node) (gs : List GuardTexts),
    (Json.mkObj (renderFields E O L b nds gs)).getObjValD "status" = .str "rejected" →
    ∃ code, (Json.mkObj (renderFields E O L b nds gs)).getObjValD "code" = .str code ∧
      code ∈ (Run.statementStatusCodes.lookup "rejected").getD []

-- C. Contracts for EN-5, EN-7 and EN-10
theorem readings_complete : ∀ E O L R b s (cs : List Candidate),
  readSource E O L R b s = .readings cs →
  ∃ chs, choicesOf (slotsOf E L R s) = some chs ∧ cs.map (·.choice) = chs ∧
    ∀ c ∈ cs, c.rows = c.choice.map (·.1)

theorem readings_budget : ∀ E O L R b s,
  slotsOf E L R s ≠ [] →
  VE.Discourse.productSize ((slotsOf E L R s).map slotShape) > VE.Readings.maxChoices →
  readSource E O L R b s = .limit

theorem one_no_spans : ∀ E O L R b s (A : NormStatement),
  readSource E O L R b s = .one A → ∀ cl ∈ A.clauses, cl.residuals = []

theorem mixed_carrier : ∀ E O L R b s (A : NormStatement) (us : List UnformalisedSpan),
  readSource E O L R b s = .mixed A us → us = spansOf [A]

theorem mixed_place : ∀ E O L R b s (A : NormStatement) (us : List UnformalisedSpan),
  readSource E O L R b s = .mixed A us → ∀ u ∈ us,
    ∃ cl ∈ A.clauses, u ∈ cl.residuals.map Residual.span ∧ u.place = .act ∧ cl.force = .modal .must ∧
      restricting R u = true

theorem mixed_spans : ∀ E O L R b s (A : NormStatement) (us : List UnformalisedSpan),
  readSource E O L R b s = .mixed A us → us ≠ [] ∧ spansPartition s us = true ∧ ∀ u ∈ us, ownerOk R u = true

theorem verified_whole_set : ∀ E O L R b s D u,
  checkHand E O L R b s D u = .verified →
  (∃ A nds, readSource E O L R b s = .one A ∧ toNodes [A] = .ok nds ∧ sameSet nds (handNodes D u)) ∨
  (∃ cs nds, readSource E O L R b s = .readings cs ∧ ruleCandidateNodes cs = .ok nds ∧
    sameSet nds (handNodes D u) ∧ pendingCount cs = handPending D u)

theorem mixed_partial : ∀ E O L R b s D u (A : NormStatement) (us : List UnformalisedSpan),
  readSource E O L R b s = .mixed A us → checkHand E O L R b s D u = .partialSpans us

theorem partial_never_verified : ∀ E O L R b s D u,
  checkHand E O L R b s D u = .verified → ∀ A us, readSource E O L R b s ≠ .mixed A us

theorem pending_only : ∀ E O L R b s D u (cs : List Candidate),
  readSource E O L R b s = .readings cs → cs ≠ [] →
  (∀ c ∈ cs, ∃ k, c.reading = .pending k) →
  checkHand E O L R b s D u = .pending (pendingCodes cs)

theorem mismatch_named : ∀ E O L R b s D u (fs : List Field),
  checkHand E O L R b s D u = .mismatch fs →
  fs ≠ [] ∧ ((∃ A, readSource E O L R b s = .one A) ∨ ∃ cs, readSource E O L R b s = .readings cs)

theorem limit_unknown : ∀ E O L R b s D u,
  readSource E O L R b s = .limit → checkHand E O L R b s D u = .unknown

theorem unread_is_reader : ∀ E O L R b s D u (k : String),
  checkHand E O L R b s D u = .unread k →
  match readSource E O L R b s with
  | .one _ | .readings _ | .mixed _ _ | .limit => False
  | _ => True
```

**How each is expected to follow.** These notes are not part of the statements.
- Part A's gate and owner statements are proved in the stub by case analysis and `simp`. EN-2 copies those proofs.
- `answer_one_iff` and its siblings unfold `answer` and `outcomeFields`. They need two lemmas: a lookup in
  `Json.mkObj` of a field list whose keys are distinct, and the distinctness of each status's field names.
  `answer_one_iff` also splits on `oneSpans`.
- `statementCaseReported_fits` follows `ResponseShape.Encoders.EnglishLean`'s `read_fits` pattern, case by case over
  `outcomeFields`, then over `renderFields` for kind `render`. A rule row's `span` is `spanJson` of a pair of
  naturals.
- `renderChecked_reads_back` is proved in the stub, by unfolding the `Except` binds. `render_text_parts` is the same
  unfolding with `renderDocument`'s definition. `render_rendered_iff` is a case split over the pair that
  `renderFields` matches. `render_fits`' second half is a case analysis of the error texts that `numbered`,
  `headerText`, `renderBlockWith`, `renderPartsWith` and `renderChecked` throw: their codes are `UnknownRule`,
  `NoWording`, `InvalidInput`, `RenderMismatch` and `RenderUnread` (the stub checks these five against the table).
- Part C: `readings_complete` comes from `mem_allChoices` and `length_allChoices` with `choicesOf`'s definition, and
  `readings_budget` from `choicesOf`'s `none` branch (the rule `compatible_budget` states for `compatibleChoices`). The
  rest are EN-5's, EN-7's and EN-10's to prove.

**Not claimed.**
- The mode does not claim that the rules form a valid W1 document: the existing checks stay with
  `decodeSource`/`validate`, as english-lean-s6.md 4 says.
- EN-3's render check does not claim that `_guard_text` is right. It claims only that the text Lean returns reads back
  to the rules.

## 5. Diagnostics

| Code | Class | Status | Text (`i` counts sentences from 0, written from 1) |
|---|---|---|---|
| `ExpectedRule` | SyntaxError | rejected | `Sentence {i+1} starts a block that is not numbered {n}. Start it with "Rule {n}."` |
| `NoConsequence` | SyntaxError | rejected | `The block that starts at sentence {i+1} has no rule sentence after its header.` |
| `StrayConsequence` | SyntaxError | rejected | `Sentence {i+1} is a rule sentence outside a block, or a second one in its block.` |
| `StrayCarveOut` | SyntaxError | rejected | `Sentence {i+1} is an "Except when" sentence before its block's rule sentence.` |
| `UnknownRule` | VEError | rejected | `The text names rule {n}, and it has no rule {n}.` (no `sentence`) |
| `UnformalisedSpan` | VEError | partial | `The text has {k} phrase(s) that the reader parsed and did not formalise. No rule is made from a sentence with such a phrase.` |
| `NodeRefused` | VEError | rejected | the decoder's text, when it does not begin `ResourceLimit:`, e.g. `invalid indexed formula` (no `sentence`) |
| `NodeLimit` | ResourceLimit | rejected | the decoder's text beginning `ResourceLimit:`: `ResourceLimit: formula depth exceeds 64` or `ResourceLimit: AST exceeds depth or node budget` (no `sentence`) |
| `Internal` | CheckerUnavailable | rejected | `The reader returned statements that are not the text's rule blocks and precedence lines.`, or `rejectText`'s `The reader found no meaning for a derivation.` for a stop on a reading or on `Reject.internal` (no `sentence`) |
| `NoDerivation` | SyntaxError | none | `Sentence {i+1} has no reading as a rule block sentence with the current vocabulary.` |
| `Ambiguous` | AmbiguousDerivation | many | `Sentence {i+1} can be read in more than one way. Two of the ways are shown.` |
| `Budget` | ResourceLimit | budget | `budgetFields`' text (UNKNOWN) |
| lexical and reject codes | `codeClasses`' | rejected | `rejectText` |
| `InvalidGrammar`, `InvalidOverlay` | `codeClasses`' | invalidGrammar | `english.read`'s texts, with "No text was read." |
| `RenderUnread` | CheckerUnavailable | rejected (render) | `RenderUnread: the rendered text is not read as rule blocks` |
| `RenderMismatch` | CheckerUnavailable | rejected (render) | `RenderMismatch: the rendered text reads as other rules`, or `RenderMismatch: ` and the gate's text |
| `NoWording` | CheckerUnavailable | rejected (render) | `NoWording: rule {name}'s predicate {p} has no consequence wording` |
| `UnknownRule` (render) | VEError | rejected (render) | `UnknownRule: rule {name} is an exception to {o}, which is not a rule of the document` |
| `InvalidInput` | VEError | rejected (render) | the two texts of 2.5 (guard text count; carve-out count) |

EN-2 adds eight rows to `Run.codeClasses`: the five block codes, `UnformalisedSpan`, `NodeRefused` and `NodeLimit`.
EN-3 adds four: `RenderUnread`, `RenderMismatch`, `NoWording` and `InvalidInput`. `Internal` is already there.
A `rejected` answer names a sentence exactly when its code is not in `statementUnsentenced` (2.3).
Python's texts differ from these (for example "Expected Rule 2 with its own block"). Every such difference is a
`diagnostic` entry of the shadow record. It is not a delta row unless the verdict differs.

## 6. Delta, trust and the stop point

- **EN-2 changes no answer.** Python's reader decides. Lean's answer is logged and compared (2.4).
- **The stop point** (review 14). No EN-3 work merges until the DRI has decided every DELTA.md row that is not
  `agree` or `both-refuse`, once for the W1 layer:
  - `lean-stricter` (a changed rejection), `lean-looser` (a newly admitted text) and `different-node` (a changed
    meaning);
  - `lean-unknown`, in its own DELTA.md section, not decided as rejections;
  - `lean-unavailable`: either the count is zero, or the DRI decides each row.

  The layout rows (`english-lean-s6.md:520`: blocks that share a line or run over several lines) are decided here. If
  the DRI refuses a layout, the refusal is a Lean code, never a relay check. No other signature is reserved.
- **Trust** (review 18; section 1.1 says the same). The DELTA of each item itemises trusted lines per file, measured
  on its final HEAD with `tools/trust_map.py`. Each item's new declarations and signed allowance are in the ledgers
  `tools/trust-classes.json` and `docs/trust-baseline.json`, which `tools/regen_generated.py --write` does not write
  (second report 1):
  - **EN-2** deletes nothing, so R6 cannot apply. Its new trusted lines, `Norm/Run.lean` and `Norm/Owners.lean`, go
    under R16 at EN-2's merge, estimated at 150 lines or fewer. Any OPEN-2 hunk in `Norm/Rules.lean` counts toward that
    total. Each line is exercised by a test that can fail, with a FOLLOW-UPS ties-pass row. Above 150 the item is cut.
  - **EN-3**: R6 covers only the lines that replace the deleted W1 path: `Norm/Render.lean`'s frame and
    `Norm/Run.lean`'s render kind (request, decoder, encoder), with the deleted Python lines of 2.5 named. Any other
    new trusted line goes under R16, as above.
  - en-s6b's `Norm/Rules.lean`, `Norm/Read.lean` and `Norm/Elab.lean` were counted at en-s6b's merge. They are part
    of the base at EN-2 and EN-3, and are on neither list.

## 7. What this item is not

- Not EN-1: its statements are english-lean-s6.md's, built by en-s6 and en-s6b.
- Not soft blocks (EN-4), translation mode (EN-5), commitment rows (EN-6), MIXED (EN-7), joins and list items (EN-8,
  EN-9), or check mode (EN-10). Section 2.6 fixes their contracts and builds nothing.
- No Lean formula renderer: `_guard_text` stays a producer whose output Lean checks.
- No change to `decodeNorm`, `VE.Acts`, `VE.SoftNorms`, `VE.Discourse.Joint`, `VE.Compose` or the merged
  `Norm/Value.lean`.

## 8. Acceptance fixtures

Every value in the O, E, R, C, S and K tables below was computed in the stub, by `#guard` (98 in all, every one
true) or by `#eval` (22: the answer rows, E1's spans and the render decoder's refusals). The route fixtures (R-f, R-rt)
and the relay fixtures (P1 to P5) are stated here and computed by EN-2's and EN-3's builds. Each "exactly when" claim
has a fixture for each direction. The environment is `LexiconFixtures.envF` with its valid lexicon v1 (`LF`).

**EN-2 step 0** (`Norm/OwnersExamples.lean`):

| # | Input | Expected (computed) |
|---|---|---|
| O1 | the six fitting (role, polarity) pairs: (obligation, must), (obligation, need not), (permission, may), (permission, must not), (plain, true), (plain, false) | each fits, and `opOf (reg role) p.sign == p.op?`; the ops are `[some .must, some .needNot, some .may, some .mustNot, some .right, none]` |
| O2 | (permission, `.modal .must`), (permission, `.modal .needNot`) | each does not fit, and the two sides differ (the premise is needed) |
| O3 | `Mode.strict`, `Mode.default "company"` | `.strict`; `.default`, which is not `.strict` (both directions of `soft_strict_iff`) |
| O4 | `sourceView envF LF A`: `A = []`; `A = [("deployed", "{0} is rolled out", false)]`; `A = [("deployed", "{0} is reviewed", false)]` | failures `[]`; `[]`; `["V4 predicate deployed", "V4 predicate reviewed"]` |
| O5 | the second `A` in the lexicon only (`{ LF with aliases := A }`) | `["V2 alias deployed"]` |
| O6 | `cPub` (Every situation, plain true, `in_scope`, guard `publicly_deployed(x0)`, no span): `toNode`, `toNodeChecked`, `toNodesChecked [rule 1 cPub, precedence 1 1]` | `ok nPub` for both (name `rule-1`, guard `unary "publicly_deployed" (var 0)`); the list `ok [nPub with over ["rule-1"]]` |
| O7 | `cSpan` (cPub with the span 30-46, row `every\|norm.modifier\|norms@0`, owner ET-T1, place act): `toNode`, `toNodeChecked`, `toNodesChecked`, `spansOf` | `toNode` alone gives `ok nPub`; the gate gives `error (unformalisedText 1)` for one clause and for the list; `spansOf` is that one span |
| O8 | guards: a 3-argument atom (`cAtom`); `lt (num 1) (var 0)`; `not` nested 300 deep (`cBad`); `cPub` with 5,000 carve-outs `deviates(x0)` (`cWide`; `maxNodes` is 10,000, two nodes each) | `toNode`: "invalid indexed formula" twice; "ResourceLimit: formula depth exceeds 64"; "ResourceLimit: AST exceeds depth or node budget"; the gate passes `cBad` to the decoder unchanged (M2) |

**EN-2 answers** (`Norm/RunExamples.lean`; reader outcomes given, rows computed by `answerWith`). The source is
"Rule 1. X." unless a row names another; it feeds only the rule rows' spans and `source_sha256`. E15 is EN-3's: the
render decoder exists only at EN-3, which adds that row to this file (second report 1).

| # | Reader outcome | Expected (computed) |
|---|---|---|
| E1 | `ok [rule 1 cPub, rule 2 cPub, precedence 2 1]`, source "Rule 1. X.\nRule 2. Y.\nRule 2 takes precedence over rule 1." (review 20) | status `one`; `statementSpans` `[(0, 10), (11, 21), (22, 58)]`; `statements` = `[{"exception_to":[],"kind":"rule","node":{"norm":{"guard":["unary","publicly_deployed",["var",0]],"name":"rule-1","over":[],"predicate":"in_scope","sign":true,"unless":[]}},"number":1,"span":[0,10]},{"exception_to":[],"kind":"rule","node":{"norm":{"guard":["unary","publicly_deployed",["var",0]],"name":"rule-2","over":["rule-1"],"predicate":"in_scope","sign":true,"unless":[]}},"number":2,"span":[11,21]},{"kind":"precedence","over":1,"rule":2}]` |
| E2 | `ok [rule 1 cSpan]` | status `partial`, code `UnformalisedSpan`, `spans` `[{"owner":"ET-T1","place":"act","row":"every\|norm.modifier\|norms@0","start":30,"stop":46}]`; `statements` absent (`null`) |
| E3 | `ok [rule 1 cBad]`; `ok [rule 1 cWide]`; `ok [rule 1 cAtom]` | `rejected`, `NodeLimit`, "ResourceLimit: formula depth exceeds 64"; `rejected`, `NodeLimit`, "ResourceLimit: AST exceeds depth or node budget"; `rejected`, `NodeRefused`, "invalid indexed formula" (review 3, 21) |
| E4 | `misplaced (expectedRule 0 1)` | `rejected`, `ExpectedRule`, `sentence` 0, text `Sentence 1 starts a block that is not numbered 1. Start it with "Rule 1."` |
| E5 | `misplaced (unknownRule 3)` | `rejected`, `UnknownRule`, no `sentence`, text "The text names rule 3, and it has no rule 3." |
| E6 | `stopped 1 noDerivation`; `stopped 1 budget` | `none`, `NoDerivation`, class SyntaxError, `sentence` 1; `budget`, `Budget`, class ResourceLimit, `sentence` 1 |
| E7 | `lexical emptyDocument` | `rejected`, `EmptyDocument`, class SyntaxError, "Write at least one statement ending with a period." |
| E8 | the outcomes of E2, E3, E5, E6, E7, E9, E10, E11 and E16; and E1's outcome with an overlay failure | never `one` (the other direction of `answer_one_iff`); `invalidGrammar` |
| E9 | `misplaced (strayConsequence 2)` (review 21) | `rejected`, `StrayConsequence`, `sentence` 2, text "Sentence 3 is a rule sentence outside a block, or a second one in its block." |
| E10 | `stopped 1 (ambiguous tA tB)`, two one-rule trees with tags `r0`, `r1` (review 21) | `many`, `Ambiguous`, class AmbiguousDerivation, `sentence` 1, `witnesses` `[[["r0",0,1]],[["r1",0,1]]]` |
| E11 | `ok [source []]` (review 5, 21) | `rejected`, `Internal`, class CheckerUnavailable, no `sentence`, text "The reader returned statements that are not the text's rule blocks and precedence lines." |
| E12 | `ok [rule 1 cPub]`, source "Rule 1. X.\nRule 2. Y." (two spans, one statement; M11) | `rejected`, `Internal`, no `sentence` |
| E13 | `ok [rule 1 cPub]`, source "Rule 1.\nX." (a block over two lines; review 21) | `one`; the rule row's `span` `[0,10]`, from the lexer's positions: header to period, across the line break |
| E14 | the class of a record, for each Lean answer and Python's outcome (review 13, 21; verifier 3) | every row below has exactly one class, in all four cases of Python admitting or refusing and the nodes being equal or not. `lean-unavailable`, when Python admits and when it refuses, for E11's and E12's `Internal`, E16's two `Internal` rows and `invalidGrammar notWellFormed` (class CheckerUnavailable in the table). Python admits: `lean-unknown` for E6's `budget` and E3's two `NodeLimit` rows (class ResourceLimit in the table); `lean-stricter` for E3's `NodeRefused`, E9 and E6's `none`. Python refuses: `both-refuse` for those six rows. E1's answer: `agree` or `different-node` when Python admits, by the nodes; `lean-looser` when it refuses |
| E15 | EN-3: the render request decoder (review 7, 21): a render request with an extra member `source`; kind `Render`; a `blocks` request of kind `lines`; `guardTextsOf {"guard": null, "carve_outs": ["A holds"]}` | status `error` ("fields do not match: expected [id, environment, lexicon, kind, rules, guard_texts], got [environment, guard_texts, id, kind, lexicon, rules, source]"); status `error`; error "InvalidInput: english.statement reads kind blocks or render"; `ok ⟨none, ["A holds"]⟩` |
| E16 | `stopped 1 (rejected internal)`; `stopped 1 (ok (precedence 1 1) false)`; `stopped 1 (rejected emptyDocument)`; `stopped 1 (rejected nestingLimit)` (M11; verifier 4) | `rejected`, `Internal`, class CheckerUnavailable, no `sentence`, text "The reader found no meaning for a derivation.", twice; `rejected`, `EmptyDocument`, no `sentence`; `rejected`, `NestingLimit`, class ResourceLimit, `sentence` 1, text "Sentence 2 is nested more than 64 levels deep." |

A further `#guard` checks, over E3, E4, E5, E7, E9, E11 and E16, that a `rejected` answer names a sentence exactly
when its code is not in `statementUnsentenced`. Another checks the same for a stop on each of `Reject`'s 23
constructors, and a third that `stopNamesSentence` is false on E16's `ok` and `internal` and true on `noDerivation`,
`ambiguous`, `budget` and `nestingLimit`.

E14's classes are computed in the stub by `deltaClasses`, which restates 2.4's table only to check that it partitions.
It is no product definition: the comparator stays Python's, and `tests/test_english_statement_shadow.py` is E14's
product test.

Every row's `identities` is `{"environment_id":"env","source_sha256":"b9f1e10d…94e1"}`, the SHA-256 of the stub's
source "Rule 1. X.", except E1 (`1713bb5f…08d1`), E12 (`9d4519a2…94ba`) and E13 (`8512791f…0be7`). The stub does not
edit `Run.codeClasses`, so its rows have no `class` for the new codes (M8). After EN-2's hunk, every row with a
`code` also carries its `class`.

**EN-2 and EN-3 relay fixtures** (Python, `tests/test_english_statement_answer.py` and
`tests/test_english_statement_shadow.py`; review 21):
- P1 (render binding, EN-3): a `rendered` answer with one block fewer or more than the request's rules; and one with
  an empty `header`, and one with an empty `sentence`. Each gives `CheckerUnavailable`.
- P2 (span binding): a `one` answer whose rule-row span ends off a UTF-8 character boundary of the source; one whose
  two spans overlap; one whose span ends past the source. Each gives `CheckerUnavailable`.
- P3 (span binding): E13's text, "Rule 1.\nX.", through the mode: the binding accepts its span `[0, 10]`.
- P4 (manifest, EN-3): a manifest whose `text_digest` matches a text with a standalone precedence line before rule 2
  ("Rule 1. …\nRule 2 takes precedence over rule 1.\nRule 2. …"). Lean's span of rule 2 in code points differs from
  :314's offset, so the answer is `IdentityMetadataMismatch`.
- P5 (shadow gate): `VE_STATEMENT_COMPARATOR=1` with `VE_SHADOW_LOG` unset. Lean is not called, and no file is
  written in the working directory (the test runs in a `tmp_path` working directory and lists it).

**EN-2 route fixtures** (`tests/data/route-cases.jsonl`, through the mode; the reader is en-s6b's):
- R-f1 to R-f24: english-lean-s6.md's f1 to f24 through `english.statement`. Each answer is the status that the
  fixture's outcome, as en-s6b records it, maps to by the table of 2.3:
  - every fixture that english-lean-s6.md expects `ok` gives `one` with the nodes it expects (f1, f2, f5, f7, f8, f10,
    f11, f12, f20, f21, f23, and f22's blocks not headed by "should");
  - `stopped 1 .noDerivation` gives `none` (f3, f4, f6, f9 at sentence 4, f17, and f22's "should" blocks);
  - f18 gives `many` with two witnesses;
  - the `misplaced` fixtures give `rejected` with their block codes: f13 `ExpectedRule` with `sentence` 0, f14 and
    f24 `UnknownRule`, f15 `NoConsequence`, f16 `StrayCarveOut`;
  - f19 gives `rejected EmptyDocument`.
- R-stale: a request whose `environment` does not match the lexicon's environment id gives `decodeCase`'s refusal,
  as `english.read` gives it.
- R-pinned: the 120 pinned blocks. Their classes are recorded in `delta.json`.

**EN-3** (`Norm/RenderExamples.lean`; `cw` gives "Every act may be done" / "Every act must not be done" for
`permitted`, and nothing else):

| # | Input | Expected (computed) |
|---|---|---|
| R1 | `numbered [a, b over a, c over a and b]` | `ok [rule-1, rule-2 over rule-1, rule-3 over rule-1 and rule-2]` |
| R2 | `numbered [a over zz]` | `error "UnknownRule: rule a is an exception to zz, which is not a rule of the document"` |
| R3 | headers of a, b (over a), c (over a, b) | "Rule 1.", "Rule 2 (exception to rule 1).", "Rule 3 (exception to rules 1, 2)." |
| R4 | rule 1 over rule 2 (a forward reference) | "Rule 1 (exception to rule 2)." |
| R5 | f7's two rules: x (sign false), y over x; no guard text | `ok "Rule 1. Every act must not be done.\nRule 2 (exception to rule 1). Every act may be done."`; parts `[("Rule 1.", "Every act must not be done."), ("Rule 2 (exception to rule 1).", "Every act may be done.")]` |
| R6 | one rule with a guard and one carve-out | "Rule 1. Every act may be done, if that act is noteworthy, unless that act deviates." |
| R7 | one rule with two carve-outs | "Rule 1. Every act may be done. Except when A holds. Except when B holds." |
| R8 | refusals: a carve-out text with no carve-out; predicate `sung`; no guard entry | "InvalidInput: rule x has 0 carve-outs and 1 texts"; "NoWording: rule x's predicate sung has no consequence wording"; "InvalidInput: one guard text entry is required for each rule" |
| R9 | `codeOf` of the three error texts | `["RenderUnread", "NoWording", "UnknownRule"]` |
| R10 | the five codes a render refusal can carry: `RenderUnread`, `RenderMismatch`, `NoWording`, `InvalidInput`, `UnknownRule` | each is in `statementStatusCodes`' `rejected` list (review 2, 7); that table is the layer-4 `Run.lean`'s (M9, and 2.5's layers) |

The stub computes the rendering half of EN-3 (R1 to R10) and the render request's decoder (E15). Both directions of
`render_rendered_iff` and
`renderChecked_reads_back` need en-s6b's `readNorm`, which is not on main. EN-3's build computes them through the
route fixtures that follow: R-rt1 is the `rendered` side, and R-rt2 and R-rt3 are the refused side.

EN-3's route fixtures (through the mode, with en-s6b's reader):
- R-rt1: Python's `render_english` texts of english-lean-s6.md f1, f7, f8 and f11, rendered by Lean, are `rendered`.
  Each text is byte-equal to Python's render of the same document.
- R-rt2: a guard text that reads as another formula is `rejected RenderMismatch`, both ways: a wrong text gives
  `RenderMismatch`, and the right text gives `rendered`.
- R-rt3: a guard text with two readings is `rejected RenderUnread`.

**Contracts** (2.6; computed now, rebuilt by EN-5, EN-7 and EN-10):

| # | Input | Expected (computed) |
|---|---|---|
| C1 | `choicesOf` of one two-candidate slot | `some`, 2 choices |
| C2 | two slots ("must" row and "employees" row) | `some`, 4 choices; for slots s1, s2: `[[(s1,0,0),(s2,0,0)], [(s1,0,0),(s2,0,1)], [(s1,0,1),(s2,0,0)], [(s1,0,1),(s2,0,1)]]` |
| C3 | six two-candidate slots (product 64) | `some`, 64 choices |
| C4 | seven two-candidate slots (product 128 > `maxChoices` 64) | `none` (UNKNOWN) |
| C5 | no slot | `some [[]]` |
| C6 | `routeRefusal ["acts@0", "norms@0", "relational-fol@0", "soft-norms@0"]` | `some "UnsupportedProfile: acts@0 with soft-norms@0 is not implemented"` |
| C7 | `routeRefusal` of `["acts@0", "norms@0", "relational-fol@0"]` and `["norms@0", "relational-fol@0", "soft-norms@0"]` | `none`, `none` |
| S1 | "We will publish a Risk Report every 3-6 months." (47 bytes; bytes 30-46 are "every 3-6 months"), span 30-46 | `spansPartition` true |
| S2 | no span | true |
| S3 | spans 30-46 and 40-46 (overlap); 30-30 (empty); 30-60 (outside) | false, false, false |
| S4 | `ownerOk` with rows "every" (owner ET-T1), "promptly" (`unowned`), "regularly" (`en-e3-norm`): span of "every" owned ET-T1; "promptly" owned `unowned` | true, true |
| S5 | "regularly" owned `en-e3-norm`; "every" owned W6 (not its row's); "soon" (no row) | false, false, false |
| K1 | `pendingCodes` of a rule, a pending ("UnsupportedProfile: x") and a no-rule candidate | `["UnsupportedProfile: x"]`; `pendingCount` of one rule candidate is 0 |

## 9. Seeded bugs

Each is introduced, shown to fail, and restored. The record names the file and the failing test.
- **Lean (EN-2 step 0):** map `Force.op .needNot` to `.mustNot`. O1 fails.
- **Lean (EN-2 step 0):** let the gate pass a clause with a span (`toNodeChecked := toNode`). O7 and E2 fail.
- **Lean (EN-2):** let the runner answer `one` when `readNorm` stops. E8 and R-f13 fail.
- **Lean (EN-2):** drop `sentence` from a block fault. E4 fails.
- **Lean (EN-2):** give every decoder refusal the code `NodeRefused`. E3 and E14 fail.
- **Lean (EN-2):** let a stop's rejection always name its sentence. E16 fails (verifier 4).
- **Python (EN-2):** let the relay accept an answer with one rule row more than the request's numbering allows. The
  fuzz test fails.
- **Python (EN-2):** drop the span binding's overlap check. P2 and the span fuzz test fail.
- **Python (EN-2):** let the shadow comparator class a Lean refusal of a Python-admitted text as `both-refuse`. The
  shadow test fails.
- **Python (EN-2):** let the shadow comparator test `lean-unavailable` last, so that a `CheckerUnavailable` answer to
  a Python-refused text is `both-refuse`. E14's shadow test fails (verifier 3).
- **Lean (EN-3):** check only the first block of the rendered text. R-rt2 fails on rule 2.
- **Lean (EN-3):** render "rules 1, 2" as "rule 1, 2". R3 and R-rt1 (f8) fail.
- **Python (EN-3):** keep a fallback to Python's reader when Lean is unavailable. The no-fallback test fails.
- **Python (EN-3):** delete `_parse_guard` with the W1 path. The soft-note test fails (verifier 1).

## 10. Lean check

**Command** (as the brief gives it; Bash timeout 3,000,000 ms):
`zsh /home/seyran/code/manage-agents/spec-stub-check.sh /home/seyran/code/ve-design-en-e3-norm lean/SpecStubs_en-e3-norm.lean`

**Stub**: `lean/SpecStubs_en-e3-norm.lean`, untracked and not committed. It imports `VE.EnglishGrammar.Norm.Value`,
`.Run`, `.SourceWords`, `.LexiconFixtures`, `VE.Acts.Table`, `VE.SoftNorms.Wire`, `VE.Norms.Wire`,
`VE.Discourse.Joint`, `VE.Compose.Dispatch`, `VE.Compose.Content`, `VE.Readings.Choice` and
`ResponseShape.Skeleton`. It holds:
- section 0's stand-ins for en-s6b (M1);
- every definition and statement of sections 2 and 4, each statement as `def … : Prop` (draft 2 adds
  `renderCodeRows`, `statementFields`, `statementUnsentenced`, `opensStatement`, `sentenceBytes`, `statementSpans`,
  `oneSpans`, `decoderCode`, the render request with `guardTextsOf`, `renderAnswer` and the dispatch, and
  `render_fits`; draft 3 adds `stopNamesSentence`, restates `answer_stopped` with it, and adds fixture E16 and E14's
  `deltaClasses`; draft 4 changes nothing in it);
- nine proofs: `opOf_agrees`, `soft_strict_iff`, `sourceView_nil`, `toNodeChecked_ok`, `toNodesChecked_ok`,
  `toNodesChecked_authoring`, `statementStatusCodes_classed` (`decide`, over EN-2's and EN-3's rows),
  `statementFields_statuses` (`decide`) and `renderChecked_reads_back`;
- section 8's 98 `#guard`s and 22 `#eval`s.

`statementCaseReported_fits` and `render_fits` are stated over an `opaque` stand-in skeleton (`englishStatementSkel`),
because the skeleton is generated in EN-2's step 2. `runMode_englishStatement` cannot be stated before the registry
constructor exists, and EN-2's build checks it.

**Final run** (draft 4, 2026-11-02; the stub is draft 3's, byte for byte):

```
restore: own build current (no restore needed); untracked stubs parked: 1
lake build: ok in 1s
== cd lean && lake env lean SpecStubs_en-e3-norm.lean  (rc 0, 24s, 22 lines)
SPEC-STUB-CHECK SpecStubs_en-e3-norm.lean: lean rc 0, errors 0, warnings 0 (sorry 0), stub sha256 52d98bc9aa14966bc4d2772d0d4c3ad30874aa984fa5f60f2f5358e0bcd99a89, lake build ok 1s, restore: own build current (no restore needed), total 33s, log /home/seyran/code/manage-agents/spec-stub-check/ve-design-en-e3-norm-SpecStubs_en-e3-norm-20261102T062954Z.log
```

- **Exit code:** 0. **Errors:** none. **Warnings:** none. **`sorry`:** none.
- **Guards:** all 98 `#guard`s evaluate to `true` (a false `#guard` is an error, and there are none). The 22 `#eval`s
  print the rows that section 8 quotes: E1 (with its spans `[(0, 10), (11, 21), (22, 58)]`), E2, E3's three rows, E4
  to E7, E9 to E13, E15's two field refusals, and E16's four rows.
- **Build:** the shared build was current ("restore: own build current (no restore needed)", lake build ok in 1s).
- **Draft 3's final run** (same stub sha256, log `…20261102T061018Z.log`): exit code 0, 0 errors, 0 warnings,
  `sorry` 0.
- **Draft 3's first run** (same session, log `…20261102T060848Z.log`): the same stub sha256, exit code 0, 0 errors, 0
  warnings, `sorry` 0.
- **Seeded run between draft 3's two runs** (same session, stub sha256 `6129c548…744c`, log
  `…20261102T060936Z.log`): draft 2's two bugs put back, a stop's rejection always naming its sentence and
  `lean-stricter` and `both-refuse` not excluding `lean-unavailable`. Exit code 1, 6 errors, 0 warnings, `sorry` 0.
  Each error is a false `#guard`: lines 930 and 932 (the partition and `lean-unavailable` checks), 947, 955 and 966
  (E16 and the check over `Reject`) and 980 (the sentence rule). Its `#eval` printed the verifier's probe, `Internal`
  with `sentence` 1. Restoring the stub gave draft 3's final run.
- **Draft 2's final run** (stub sha256 `825206f4…d037`): exit code 0, 0 errors, 0 warnings, `sorry` 0, 86 `#guard`s and
  18 `#eval`s.
- **Draft 2's run before that** (stub sha256 `291cfb5c…1304`): exit code 1, 45 errors, 0 warnings, `sorry` 0.
  All 45 came from one root error, `SpecStubs_en-e3-norm.lean:262:10: Invalid dotted identifier notation: The
  expected type of '.word' … is not of the form 'C …'`, in `opensStatement`'s pattern. The other 44 were the `#eval`s
  and `#guard`s that use it ("cannot evaluate code because 'VE.EnglishGrammar.Norm.Run.opensStatement' uses 'sorry'
  and/or contains errors", or "aborting evaluation since the expression depends on the 'sorry' axiom"). The fix named
  the constructor (`Tok.word`).

**Corrections the elaboration forced** (all applied above):
- `BlockFault.code` and its siblings must be in namespace `VE.EnglishGrammar.Norm` for dot notation.
- `partial` is a keyword (M5).
- `decodeNorm` accepts an empty predicate name, so a refused node needs a deep or "atom" guard (O8, M2).
- An alias needs the environment's forms (M3).
- `Except` has no `BEq`, so the fixtures declare one locally.
- Span offsets are bytes: "every 3-6 months" is 30-46, not 29-46.
- `Polarity.fits` is en-s6b's (`Norm/Rules.lean`), and is stated in the stub from english-lean-s6.md 2.5.
- Draft 2: a pattern on a lexer token names its constructor (`Tok.word`). A fixture whose reader outcome is `one`
  needs a source whose sentences give one span per statement, so E1, E12 and E13 carry their own sources (M10, M11).
  The node budget is reached with 5,000 carve-outs (`cWide`), since the guard and each carve-out count two nodes.
- Draft 3: none. Its changes elaborated on their first run.
- Draft 4: none. It changes no Lean block. Its layer rows are `tools/layer_policy.py`'s, which the stub cannot check:
  the stub is one module, and EN-3's `tools/check_lean_imports.py` checks the rows.

## 11. OPEN lines (for the review; not decided here)

- **OPEN-1 is closed** (review 4; M2). W1's frozen formula wire (`Norms/Wire.lean:277-312`) has no n-ary or `lt`
  atom, so en-s6b's `Clause.wire` has no other form to write. A W1 guard with `EFormula.encode`'s `"atom"` or `lt` form
  is `NodeRefused`; a guard beyond the decoder's limits is `NodeLimit`. en-s6b does not change, and EN-2's delta lists
  every block that hits either code.
- **OPEN-2. The consequence wordings and the rule tags (M1).** EN-3 needs en-s6b's consequence wordings as a function
  (`consequenceWordings`), and EN-2 needs `normGrammar`'s rule tags. If en-s6b's `Norm/Rules.lean` exposes neither,
  EN-2 adds them there in one hunk, never as a copy. That hunk counts toward EN-2's R16 total (section 6).
- **OPEN-3. The manifest split (M7).** This spec proposes the operation id `english.statement.w1`. The assurance
  manifest's owner may name it otherwise. The rule stands that one operation has one authority.
