# relb F1/F2 fixtures (relb-f1f2-grammar, 2026-11-22)

- `environment.json`, `rules.json`: copies of the eligibility environment and the 56 rule formulas
  (usecases/eligibility at 94a1826b0f), written by `make_fixtures.py`; `wordings.json`: `render_w6_sentence`'s
  wording of each rule. The tests read only these copies.
- `ten_sentences/`: the ten-sentence test (reviews/dri-decision-relb-english-rules-20261121.md item 5).
  `make_prompt.py` builds `input.json` and `prompt.txt` from the source clauses (verbatim lines of the source files,
  by cite) and the environment's constant names; nothing else (no formula, gloss, grammar or rendered wording).
  One fresh Claude Opus 5.5 session (`claude -p --model claude-opus-5-5`, no tools, empty working directory)
  answered `prompt.txt`; `writer_output.txt` is its answer, unedited. `record_results.py` writes `results.json`:
  each sentence's outcome under `parse_w6_sentence` (one reading, equal to the rule or not, or refused with the
  reason) and the spans the quantity grammar reads alone. Refusals are results, not failures to fix by editing.
