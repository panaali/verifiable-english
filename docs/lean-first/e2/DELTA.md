# English in Lean, E2: DELTA

Every difference between Python deciding English admission (the base) and the Lean-authoritative reviewed merge
`9cc8418d` that the
evidence shows, with its class (`wording`, `order`, `verdict`, `availability`; plan GE2 item 3). The measured counts
are in [the E2 report](../../spec/english-lean-e2-report.md), generated from
[e2-evidence.json](../../../conformance/english-lean/e2-evidence.json); `conformance/english_lean_e2_report.py`
maps each recorded difference to a row here (`DISPOSITIONS`) and counts what no row covers.

**Signatures.** GE2 asks the DRI to sign each `verdict` and `availability` row. They are recorded here, unsigned:
owner the English E2 DRI (HUMAN, deferred). One `verdict` row is listed (V1).

## E2.5 authority ruling at this head

**SHADOW.** The saved readability replay found six changed writing messages across 36 attempts at `9cc8418d`.
The changed messages lose a name or a suggestion from the base text. Five of 30 reading items, R23–R25 and
R29–R30, changed from a verdict to an unavailable checker outcome. The frozen risk replay was adjusted to the
current route signature and agrees for R17–R20. The exact base and
merge messages are side by side in [readability-changes.md](evidence/readability-changes.md), with every item in
the saved JSONL files. This fails the DRI's section 2.10 condition. `english.admission` therefore has Python
authority again; Lean's reader runs as a shadow and its E2 code and tests remain. On Python authority all 36
writing attempts recovered the base verdict and message. The directed coverage comparison reaches all 45
previously unreached fixed rules with no Python/Lean difference
([coverage-directed.json](evidence/coverage-directed.json)).

R23–R25 cannot import the frozen scorer's `SpeechDocument` from the current `ve.speech_acts`. Their base
verdicts are FOLLOWS, GAP and REQUIRED. The R29/R30 errors are `VEError: fields do not match: expected [sort, description], got [description, sort,
verbalisation]` for the frozen readability environment. The base returned FORBIDDEN and DNS respectively. The
authority revert does not conceal this separate availability regression.

## GE2 corpus A/B at Python authority with Lean in shadow

The [complete A/B comparison](evidence/ab-summary.md) records 94,498 public results on each side against
base `9aaf918d`: 93,742 same, 367 wording, 192 order, 196 verdict and one availability difference. The 708
non-conformance changed records, including both full outcomes, are in
[ab-other-compare.json](evidence/ab-other-compare.json). The conformance 48 are in
[ab-conformance-compare.json](evidence/ab-conformance-compare.json). The following rows describe their classes;
they are **not DRI signatures** or acceptance of the changed results.

| Row | Class and count | Base to head |
|---|---:|---|
| W9 | wording, 48 | Lean conformance diagnostic text gains a public class prefix; 15 exact text pairs are saved. |
| W10 | wording, 319 | Probe budget wording (1), rights diagnostic wording (224), and quantity diagnostic wording (94), including class prefixes. Every pair is in the saved comparison. |
| O4 | order, 148 | Rights document check/render reports `InvalidInput` before `UnknownSymbol` on the base, and `UnknownSymbol` on the head (74 cases, two operations each). |
| O5 | order, 44 | Quantity error class changes, including noncanonical Unicode digits (`SyntaxError` to `InvalidInput`). |
| V2 | verdict, 190 | The base refuses headed rights cases with `UnsupportedProfile: readings@1`; the head returns a document report. |
| V3 | verdict, 6 | Quantity changes four certificate results from `false` to `ResourceLimit` and two countermodel error structures; both Python and Lean authority recordings contain these differences. |
| A5 | availability, 1 | The base pilot `readings/s1.ve.md` check times out at 600 seconds; the head returns a report. |

V2, V3 and A5 remain unsigned. Together with the readability failure, they preclude the E2.5 authority flip.

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
| W9 | the base Lean conformance adapter reports the bare parser or budget diagnostic (`document must contain at least one statement`, for example) | the head prefixes it with its public class (`SyntaxError: document must contain at least one statement`); 48 conformance A/B records, 15 exact text pairs in [ab-conformance-delta.json](evidence/ab-conformance-delta.json), with unchanged verdicts |

## order

| Row | Base (Python) | Head (Lean) |
|---|---|---|
| O1 | S2's F3: the hand parser's 64-level nesting limit (`ResourceLimit`) before a word or spacing it would refuse later | Lean reads the words first and refuses with their code |
| O2 | S3's or38 class: Python's `ResourceLimit` where its depth check precedes a malformed integer shape | Lean has no reading (`none`) |
| O3 | the producer's overlay refusal before any text is read | Lean's order of spec 2.5: the boundary, the overlay check, V6, V1 to V5, then the text |

## verdict

| Row | Base (Python) | Head (Lean) | Evidence |
|---|---|---|---|
| V1 | an `nary@0` wording with words before `{0}` (`the value of {0} at {1} is {2}`): Python's `template_parts` accepted it, Python selected it and its reader admitted texts written with it (`The value of speed at instant is high.`) | V3 refuses a selected wording that does not begin with `{0}` (S3 D8). Python's `template_parts` and the port's `templateParts` (5.2) now refuse it as well, so the mechanical form is selected and the environment is read; a text written with the refused wording has no reading (`SyntaxError`). Before this row the request was `invalidGrammar lexicon: V3` for every text (recheck 1 of E2, B) | `tests/test_nary.py::test_fret_user_sort_time_and_arity_six`; `tests/test_english_e2_selection.py` |

## availability

| Row | Base (Python) | Head (Lean) | Evidence |
|---|---|---|---|
| A1 | an environment where one predicate's declared wording has the key of another symbol's selected wording (two predicates declaring one wording; a declared wording equal to a `risk@0` form; a sort noun equal to the severity noun): Python's producer quotes the declared one and admits texts | V4 compares every selection with every symbol's *declared* wording (S3's `Lexicon.valid`, D2: unchanged), so the request is `invalidGrammar lexicon: V4 …` (`CheckerUnavailable`) | the parity mutation set (the report's port-parity count of V1 to V5 refusals); `tests/test_risk_english.py::test_declared_wording_that_reuses_a_risk_form_keeps_its_identifier` |
| A2 | a `risk@0` severity class whose name is a reserved word (`every`) is a generated constant Python admits | Lean's typing view declares the classes as constants, and the frozen route decoder refuses a reserved name: the environment is refused at the boundary | `tests/test_risk_english.py::test_class_names_take_the_reserved_word_check` |
| A3 | texts that Python's 30 s Earley wall-clock limit refused | Lean decides them within its work budget | the evidence's excluded count (none in this run) |
| A4 | statement-layer conclusions over a `rights@0` frame or generated decision atoms read by Python | unchanged: `S2Wording.conclusion` (through `canonical_sentence` with `statement_layer`) stays on Python's statement reader (`english.statement`, until E3), since those atoms are outside the E2 reader | `docs/lean-first/e2/LEDGER.md` |
