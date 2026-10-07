# English in Lean, E2: DELTA

Every difference between Python deciding English admission (the base) and Lean deciding it (this head) that the
evidence shows, with its class (`wording`, `order`, `verdict`, `availability`; plan GE2 item 3). The measured counts
are in [the E2 report](../../spec/english-lean-e2-report.md), generated from
[e2-evidence.json](../../../conformance/english-lean/e2-evidence.json); `conformance/english_lean_e2_report.py`
maps each recorded difference to a row here (`DISPOSITIONS`) and counts what no row covers.

**Signatures.** GE2 asks the DRI to sign each `verdict` and `availability` row. They are recorded here, unsigned:
owner the English E2 DRI (HUMAN, deferred). No `verdict` row is listed.

## wording

| Row | Base (Python) | Head (Lean) |
|---|---|---|
| W1 | Python's texts for every refusal (`Unknown English phrase …`, `Expected …`, `A conclusion needs an earlier premise.`, …) | Lean's texts of spec 4.2 for every code, verbatim; for a sentence without a reading, Lean's text followed by Lean's advice, or by the relay's nearest-wording help (`Unknown English phrase '…'. Nearest declared wordings: …`, spec 2.8) |
| W2 | a refusal's class as Python's parser chose it (`RelativeForm` as `SyntaxError` or a typing class; a typing failure as `UnknownSymbol`, `TypeMismatch` or `UnsupportedProfile`) | Lean's class of the code (`codeClasses`): `RelativeForm` `SyntaxError`, `IllTyped` `TypeMismatch` (D10); the comparator keeps the tolerance |
| W3 | the producer's overlay refusals: `Duplicate English wording '…' for '…'; existing symbol(s): …`, `English wording for '…' reuses a risk@0 wording`, `English vocabulary entry fails the template linter: …` | `InvalidOverlay` (class `VEError`): `The vocabulary overlay gives p a wording that another symbol already has.`, `… a wording that risk@0 reserves.`, `The vocabulary overlay entry for n cannot be used as written.`, each followed by `No text was read.`; when two entries fail at one site, the entry named follows Lean's key order |
| W4 | `The marked conclusion has no checked derivation from earlier premises: <status>` (`parse_english`), the same without the status (`parse_english_argument`) | `Sentence i is marked as a conclusion, and no checked derivation from the earlier premises was found: <status>` from both |
| W5 | Python's rewrite hints inside its error texts (`Use 'might lead to' …`, `Write the long form …`, `Another action needs a rule on an action as its reference.`, the two `every … cannot lead to` rewrites) | Lean's text, then Lean's advice row (spec 4.3, with `alternatives-another` added), or for `risk-every-cannot` Lean's text naming both rewrites with the sentence's words |
| W6 | `Phrase '…' extends existing wording …` from the hand parser (a longer phrase beginning with a declared wording) | `Sentence i has no reading with the current vocabulary.` with the nearest-wording help naming the declared wording; `ve propose` keeps Python's message |
| W7 | `The marked conclusion certificate did not replay in the claim graph.` (`SyntaxError`) | `CheckerUnavailable`: a prover certificate the claim graph does not replay is a checker fault, not the text's |
| W8 | a lexical refusal's span from Python's parser position | the offending character's span in code points (`BadCharacter`, `OpenQuote`, `BadNumeral`, `BadSpacing`), the whole source for a refusal naming no sentence, the named sentence's span otherwise (spec 4.4) |

## order

| Row | Base (Python) | Head (Lean) |
|---|---|---|
| O1 | S2's F3: the hand parser's 64-level nesting limit (`ResourceLimit`) before a word or spacing it would refuse later | Lean reads the words first and refuses with their code |
| O2 | S3's or38 class: Python's `ResourceLimit` where its depth check precedes a malformed integer shape | Lean has no reading (`none`) |
| O3 | the producer's overlay refusal before any text is read | Lean's order of spec 2.5: the boundary, the overlay check, V6, V1 to V5, then the text |

## availability

| Row | Base (Python) | Head (Lean) | Evidence |
|---|---|---|---|
| A1 | an environment where one predicate's declared wording has the key of another symbol's selected wording (two predicates declaring one wording; a declared wording equal to a `risk@0` form; a sort noun equal to the severity noun): Python's producer quotes the declared one and admits texts | V4 compares every selection with every symbol's *declared* wording (S3's `Lexicon.valid`, D2: unchanged), so the request is `invalidGrammar lexicon: V4 …` (`CheckerUnavailable`) | the parity mutation set (the report's port-parity count of V1 to V5 refusals); `tests/test_risk_english.py::test_declared_wording_that_reuses_a_risk_form_keeps_its_identifier` |
| A2 | a `risk@0` severity class whose name is a reserved word (`every`) is a generated constant Python admits | Lean's typing view declares the classes as constants, and the frozen route decoder refuses a reserved name: the environment is refused at the boundary | `tests/test_risk_english.py::test_class_names_take_the_reserved_word_check` |
| A3 | texts that Python's 30 s Earley wall-clock limit refused | Lean decides them within its work budget | the evidence's excluded count (none in this run) |
| A4 | statement-layer conclusions over a `rights@0` frame or generated decision atoms read by Python | unchanged: `S2Wording.conclusion` stays on Python's statement reader (`english.statement`, until E3), since those atoms are outside the E2 reader | `docs/lean-first/e2/LEDGER.md` |
