# ap-1a delta: lexical acts (`VE.Acts.LexicalBase`, `VE.Acts.Lexical`, `VE.Acts.Compat`) and the profile-aware decoder

Base: `git merge-base HEAD main`. ap-1a is the first part of batch AP-1 of
[act-phrases-PLAN.md](../../spec/act-phrases-PLAN.md) (section 4, "AP-1"); the rest is named in [REPORT.md](REPORT.md)
section 6.

**Public output: none changes.** `acts@0` has no profile row (ap-1b), so the envelope refuses it as today
(`UnsupportedProfile: Unsupported profile acts@0`, `tests/test_acts_lexical.py::test_the_acts_profile_is_refused_until_its_row_lands`),
and no request reaches `Lexical.check`. Without `acts@0` the regulated decoder is today's
(`decodeRegulated_without_acts`, `canonicalActIn_without_acts`), and every case recorded in
`tests/data/route-cases.jsonl` (330 cases, all 13 route modes) answers byte-identically at the merge base and here
([evidence/byte-identity.json](evidence/byte-identity.json), `byte_identity.py`). The service tests of
`tests/test_acts_lexical.py` pin today's texts through the refactored decoder: a plain act or a form is refused
("invalid regulated fields"), and a long, joined, comma or curly-apostrophe act is refused by today's check ("invalid act
phrase"). No verdict, diagnostic, fault order, English line or CPU figure changes, so none of these is a row below.

## User-visible deltas

Trust growth, re-measured with `python3 tools/trust_map.py --check` on the final code: K +0, S +19, untied V +131,
trusted +150, against the merge base; recorded as two allowances (S 19, V 131) in `docs/trust-baseline.json` with
`trust_map.py --allow`, and `trust_map.py --check` passes. R16's cap is 150 lines per item, none in K: this item is
at the cap. The ties-pass row R16 asks for is in manage-agents FOLLOW-UPS.md, section "## ap-1a". The seeded bugs that
make the checks below fail are in [mutants.json](mutants.json) (`seed_bugs.py`); line numbers are
`lean/VE/Acts/LexicalExamples.lean`'s.

| # | File | Trusted lines (class, declarations) | Exercised by | Ruling |
|---|---|---|---|---|
| 1 | `lean/VE/Acts/Lexical.lean`, `lean/VE/Acts/LexicalBase.lean`, `lean/VE/Norms/Wire.lean`, `lean/VE/Acts/Syntax.lean` | Lexical.lean +138: S 28 (`Tok`, `joinWords`, `clauseWords`, moved byte for byte from Syntax.lean, which is -9 for them; `maxActBytes`, `maxPhraseBytes`, `maxPhrases`, `fixedOk`, `Form`, `Form.text`, `wording`), D[V] 110 (`fold`, `normal`, `dropComma`, `slotOf?`, `pieceToks`, `rawLex`, `phraseToks`, `clash`, `decodeFixed`, `group`, `lex`, `check`, `Form.ofText?`). LexicalBase.lean +48: D[V] (`actReserved`, `scanSlotsAux`, `scanSlots`, `pyWhitespace`, `words`, `asciiLetter`, `actWord`, moved verbatim from Wire.lean). Wire.lean -27: -48 for the move, +21 D[V] (`canonicalActIn`, `decodeRegulatedWith`, `decodeRegulatedIn`). Net: S +19, V +131 | the fixtures A1-A6, A13, A15-A19, A21-A30, A32, A33 of spec 11.1 (lines 26-159), the acts-free decoder (161-170) and the boundaries of every limit and diagnostic (172-259): 400/401-byte acts, 300/301-byte phrases, 128/129 phrases, D-1 to D-14 and D-19 each with its exact text, every token kind, case folds, a later duplicate, a contained phrase; the proofs of `check_no_join`, `wording_subject_first`, `decodeRegulated_without_acts` and `canonicalActIn_without_acts`; 42 seeded bugs, at least one in each new trusted definition, all killed (`Tok` and `Form` are inductives whose every constructor a guard reads) | SIGNED by standing ruling R16 (DRI-RULINGS.md) |
