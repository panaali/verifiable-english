# English in Lean, E2: the report

Plan [english-lean-E2-PLAN.md](english-lean-E2-PLAN.md) item E2.5; spec [english-lean-e2.md](english-lean-e2.md).
This report holds the E2.5 evidence and the DRI's authority decision. The readability replay of the reviewed
merge fails section 2.10: six of 36 writing messages lose base content, and five of 30 reading items become
unavailable. English admission is back on Python authority with Lean in shadow. The full per-item records and
side-by-side changed messages are in [evidence/readability-changes.md](../lean-first/e2/evidence/readability-changes.md).
The earlier G3 measurements below remain candidate evidence; they do not authorize a flip. Its
measured section is generated from [e2-evidence.json](../../conformance/english-lean/e2-evidence.json) by
`python -m conformance.english_lean_e2_report --write`, and `tests/test_english_e2_report.py` checks that the
committed section is that rendering. Every difference is mapped to a row of
[DELTA.md](../lean-first/e2/DELTA.md) or counted as undispositioned.

The evidence is produced by

    python -m conformance.english_lean_e2_evidence --workers 10 --per-config 5000 --per-usecase 500 \
        --fresh-per-seed 200 --documents 50 --reverse-samples 3000 --mutation-texts 40

in six parts (`--part`): `g3` (every corpus environment at the dispatched boundary: Lean's `english.read` through
the relay against Python's reader, the comparator's record per text, and the round trip of each rendered formula),
`reverse` (texts sampled from the `english.grammar` export of every corpus lexicon, with spacing and word-split
mutants), `mutation` (the corpus lexicon mutants, replayed with V1 to V6), `parity` (the port's selection, exported
by `english.grammar` as `policy`, against Python's producer symbol by symbol), `overlay` (Lean's overlay check
against the producer's three refusals on every corpus overlay and its mutants) and `latency` (GE2 item 9, on the
service).

## The review fix round (2026-10-07)

The reviews of the integrated build: `manage-agents/english-lean-e2-review-astra.final.md` (Astra) and
`manage-agents/reviews/english-lean-e2-review-fable.md` (Fable). Each finding was fixed as a class; the spec's
changes are its section 13.

| Finding | Class removed | Fix | Commit |
|---|---|---|---|
| Astra A1, Fable A1: `decode_encode` stated, not proved | an approved statement left unproved | `ETerm.encode` writes integers with `intText` (the text `toString` writes, checked on the compiled code); `decode_encode` proved over `String.toInt?`'s loops | `278e2415` |
| Astra A2, Fable A2: Lean's authority before GE2's evidence | authority without its evidence | this report, the E2.5 harness, `LEDGER.md`, `DELTA.md`, the section 8 fixtures in `E2Examples.lean`, the O1 to O3 overlay tests at the public boundary, and the comparator on in the suite (`tests/conftest.py`) | `15d58bfa`, `6bce2f19`, this report's commit |
| Astra A3, Fable A3: Python readers dropped from the assurance record; definitions, citations and S2 conclusions read by Python | a reader deciding admission outside the manifest | definitions and citations read through Lean again; the statement readers (`parse_statement_english`, `norm_english.parse_english`, `require_unique_derivation`) are `@semantic_entry("english.statement")`, a registered operation until E3; `python:backend-adapter` back in `english.admission`'s trusted list | `e87a15a6` |
| Astra B1, Fable B4: the relay's own class table and texts | a Python table that can drift from Lean's | `english.grammar` exports `codes`, `statuses`, `unsentenced`; `ve/english_grammar/codes.json` is generated from it and checked against the service; the relay raises the class Lean names (`ve.errors` by name); `invalidGrammar` text is Lean's; one validator for every transport, the test override included; `parse_english_argument` takes premises from Lean's obligations only | `a563e26a`, `9fe3ccd0` |
| Astra B2: `reports@0`, `readings@1`, `speech-acts@0` declarations stripped unvalidated | boundary fields dropped without a check | validated by their routes' decoders in the boundary's part 1; one-fault mutants of every status refused (fuzzer) | `a563e26a` |
| Astra B3, Fable B3: spans | a span not derived from the refusal's location | `lexicalSpan` (the offending character), `IllTyped` names its sentence, the whole source for a refusal naming no sentence; `english.read` and `senses.read` share `refusalExtras` | `a563e26a` |
| Fable B2: diagnostics lost | a narrowing of messages hidden by edited tests | nearest-wording help over Lean's sentence span; `risk-every-cannot` gives both rewrites with the sentence's words; the `alternatives-another` advice row | `a563e26a` |
| Fable B1: edited tests hide narrowings | test edits that hide availability changes | each narrowing restored or recorded as an `availability` row with its test (DELTA A1, A2) | `a563e26a`, `DELTA.md` |
| Astra B4: trust budget | unsigned trust growth | test-only Lean classified `T`; the growth signed in `docs/trust-baseline.json` (DRI note, ruling 9), recorded at the stage's growth over the merged main (952 V lines) | `4c465af1`, `2e5707b1` |
| Astra B5, Fable B5: out of date with main; the mutation matrix shrank | drift from main | merged main three times, last at `49d18263` (lf-13a: the block routes validate the submitted environment); the mutation matrix restored and the one-fault mutant fuzzer added | `6c5092b2`, `2359e6b1`, `2e5707b1`, `a563e26a` |
| GE2 item 9 (found by the evidence): V6 1.5 s at 256 predicates | a per-symbol re-derivation of environment tables | `PolicyCtx.of` computes them once; 5.2's text kept verbatim in `PolicyReference.lean` and checked equal on 34 environments | `a5ba55e2` |
| GE2 item 2 (found by the reverse corpus): Lean read 152 texts Python refuses, an integer mark glued to a word (`costs-5`, `at least[budget - 24]`, `[a + b]and`, `[a + b]- 2`) | an integer mark's spacing on the side away from its term (S3 2.2's table) | the lexer's `gluedFlags` and one `order@0` row per mark, mirrored in the Python lexer and the Lark conversion; every spacing mutant at every mark compared across both readers (`tests/test_english_e2_integer_marks.py`) | `4229e7c7` |
| GE2 items 2 and 6 (found by the reverse corpus): under `usecases/eligibility` (`ve-units@1`) the public outcome was `CheckerUnavailable` ("answer is malformed") where Python raised `UnsupportedProfile`, on 156 texts; G3 had compared no text there | a profile refusal of the environment read as a fault of Lean's answer; an environment the evidence skipped without saying so | the core checker's environment gate is one function (`ast.core_gate`), applied by the relay before it decodes Lean's formulas; the harness compares gated environments and reports any configuration with no text | `57a35559` |
| Fable checklist 11: the statement check read Lean source as text | a regex standing in for the compiler | Lean elaborates each approved 5.5 statement and the built theorem proves it; mutated statements are refused | `b8f16de9` |

## GE2

| Item | Status |
|---|---|
| 1. Suite | clean full gate on `2aad9b8f`: 11,850 Python tests passed, 7 allowed skips, 0 failures; 37 Rust tests passed ([saved gate result](../../conformance/english-lean/e2-gate-result.json)) |
| 2. G3, reverse corpus, mutation replay, volume and coverage | 145,550 candidate comparisons agree. The directed stream now reaches all 45 previously unreached fixed rules in 31 compared texts, with zero Python/Lean differences ([rule-by-rule texts](../lean-first/e2/evidence/coverage-directed.md)). |
| 3. Corpus A/B | **fails preservation** against base `9aaf918d`: 94,498 saved results on each side, 39,564 conformance agreements plus 54,178 other agreements; 48 + 319 wording changes, 192 order changes, 196 verdict changes and one availability change. The complete outcomes and classed rows are in [the A/B summary](../lean-first/e2/evidence/ab-summary.md). Verdict and availability rows remain unsigned. |
| 4. Readability items | **failed**: 36 writing attempts, six changed messages; 30 reading items, five newly unavailable after replay compatibility adjustments. Python authority restored ([saved comparison](../lean-first/e2/evidence/readability-comparison.json)). |
| 5. V6 and overlay parity | met (measured below) |
| 6. Availability | G3 over every corpus environment agrees; the narrowings are DELTA A1 and A2 (signatures deferred) |
| 7. Senses | the senses suite passes through the relay (`tests/test_senses_route.py`) |
| 8. Deletion ledger | [LEDGER.md](../lean-first/e2/LEDGER.md); `tools/relay_lint.py` passes; signature deferred (HUMAN) |
| 9. Latency | met (measured below) |

## Measured

<!-- BEGIN GENERATED: python -m conformance.english_lean_e2_report --write -->
Measured at `57a35559f8` from [e2-evidence.json](../../conformance/english-lean/e2-evidence.json).

### G3 at the dispatched boundary

Configurations: 39; texts compared: **145,550**; agreeing: **145,550**; differing: **0**; excluded (Python's wall-clock limit): 0. Streams: the sealed round-trip stream (5,000 texts per round-trip configuration, 500 per use-case environment), 50 documents of five sentences per configuration, and 14 fresh date seeds of 200 texts each per round-trip configuration (seeds 2026100700 to 2026100713).

| Stream | Texts | Agree | Differ |
|---|---:|---:|---:|
| sealed | 96,000 | 96,000 | 0 |
| documents | 1,950 | 1,950 | 0 |
| fresh | 47,600 | 47,600 | 0 |

Round trip (Lean's formulas against the formula each text was rendered from, or Lean refusing a text Python reads): **0** failures.

### Coverage

Over 39 configurations, 2,023 (configuration, fixed rule) pairs were not reached by a compared text; 45 fixed rules were reached in no configuration. Lexical families unreached somewhere: `adjective` (25), `copula` (25), `copula-adjective` (25), `natural-subject` (25), `relation` (13), `owner` (3), `int-plain-constant` (2), `head` (2), `clause` (1), `object-relative` (1), `relative` (1).

Fixed rules no compared text reached: `coordination.predicate-and`, `coordination.predicate-or`, `coordination.subject-and`, `coordination.subject-or`, `declaration.eighth`, `declaration.fifth`, `declaration.fourth`, `declaration.seventh`, `declaration.sixth`, `declaration.third`, `formula.coordination`, `formula.natural`, `guard-rel.that`, `guard-rel.who`, `listing.all.words`, `listing.any.words`, `listing.both.words`, `listing.if.markers`, `listing.if.words`, `marker.hence`, `marker.it-follows-that`, `marker.so`, `marker.therefore`, `natural-every.owner`, `natural-every.subject`, `natural-no`, `natural-some`, `natural-tail.both`, `natural-tail.owner`, `natural-tail.relative`, `natural.every`, `natural.no`, `natural.some`, `reach.body.listed`, `sentence.marked`, `some-tail.copula`, `some-tail.relative`, `some-tail.two`, `term.it`, `term.the-eighth`, `term.the-fifth`, `term.the-fourth`, `term.the-seventh`, `term.the-sixth`, `term.the-third`.

### The reverse corpus

111,528 texts were sampled from the `english.grammar` exports (3,000 draws per configuration); Lean read 6,453 of them, the rest failing a context condition the context-free sample cannot see (an unbound reference, an ordinal, a marker). Every text Lean reads, with its spacing and word-split mutants that Lean also reads, was read by Python: **12,906** agree, **0** differ. Lean's answer unavailable: **0**.

### Differences and their dispositions

| DELTA row | Disposition | G3 records |
|---|---|---:|
| O1 | order: S2's F3, Python's depth limit before a later fault | 0 |
| O2 | order: S3's or38 class, Python's ResourceLimit where Lean has no reading | 0 |
| W2 | wording: both refuse the text; the class is Lean's (spec 4.2) | 0 |
| — | **undispositioned** | **0** |

### The lexicon mutation replay

16,042 mutants of the corpus lexicons (`english_lean_lexicon.mutants`); V1 to V6 refused **14,128**, accepted **1,914**. Over the accepted mutants, 40 corpus texts each: unchanged 76,333, no longer read 227, **changed formula 0**.

### Port parity

Corpus environments compared symbol by symbol: 39, mismatched symbols **0**. Mutation set: 3,190 environments compared, mismatched symbols **0**; V6 refusing Python's own lexicon (a port defect): **0**; V1 to V5 refusing Python's lexicon (DELTA row A1): 16; mutants `Environment` refuses: 148.

### Overlay parity

Corpus overlays compared: 8, agreeing 8. Overlay mutants compared: 1,650, agreeing **1,650**, differing **0**; refused by `display_environment` before any Lean call (not compared): 163. Sites of the mutants: None 724, O1 78, O3 848.

### Latency (GE2 item 9)

| Measure | Measured | Budget | |
|---|---|---|---|
| a corpus sentence, p95 | 8.58 ms | 20 ms | met |
| a 150-token sentence | 8.37 ms (153 tokens, one) | 50 ms | met |
| a 300-token sentence (work budget) | 15.3 ms (303 tokens, one) | inside the work budget | met |
| the BlueDot document's English | 439.3 ms (40 sentences, 2 requests) | 1 s | met |
| grammar instantiation, worst corpus lexicon | 41.41 ms (`usecases/claude-constitution-excerpt/environment.json+overlay`) | 100 ms | met |
| `policyOk`, 256 predicates (CPU) | 60 ms | inside 100 ms | met |
| the generated modules | 3.1 s (6 files, `lake env lean`) | 60 s | met |

**Undispositioned differences: 0.**
<!-- END GENERATED -->
