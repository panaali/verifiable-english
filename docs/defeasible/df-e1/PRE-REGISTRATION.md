# DF-E1 preregistration — the two default-answer forms

Frozen before the first reader call. This follows `docs/spec/defeasible-PLAN.md` §DF-E1, D6 and §2.8. `items.json` is the exact UTF-8 reader input inventory. Each row records the source commit and the command that rendered it. `prepare.py --items` generated the inventory from real Lean answers.

## Items and rendering

- N01–N12 have Lean basis `needs` and a checked strict countermodel. N01–N06 are short eligible. N07–N08 have a stated exception, N09–N10 a switch, and N11–N12 a ranking.
- S01–S12 are strict controls. `ve.defaults.ask()` returned `{"question": "strict", "valid": true}` through the real Lean certificate route for each, with Lean's deciders `["assistant"]` and their DE5 sentence "This holds whatever the assistant decides." (df-1bbb, plan DF-ζ). Their answer is the strict route's JSON display, using `json.dumps(..., ensure_ascii=False, indent=2)`, as main prints it. Their rule text comes from the document's English renderer. No other sentence is added. The DE5 fields were added to these rows before the first reader call. At that change, the needs rows gained Lean's `deciders` in `lean_answer`, and their rendered strings did not change.
- Every `needs` item is shown in DE1′ through `ve.defaults_english.sentences()`. For N01–N06, DE1 changes only the `form` field of that same checked Lean row to `short` before calling that renderer. Only those six have a short call. DE6 and DE6′ follow the DE1 decision; they are not separate reader items.
- `tests/test_df_e1.py::test_saved_item_bytes_equal_checked_renderers` regenerates every row and checks the saved rule text, checked answer and rendered UTF-8 strings. The prompt is the rule text, rendered answer and the following question only.

## Reader and decision, fixed before calls

One separate subscription Sonnet 5.5 `claude` CLI call per item and form: 24 long and six short, at most 40 calls and 3,000,000 CW. Use the account chosen by `pick-claude-account.sh`. Before a call, stop if calls made = 40 or if CW so far plus the largest single call so far would exceed 3,000,000. The first call reserves 100,000 CW. Failed attempts are saved and stop the run for inspection.

> Could the conclusion be false in a situation the text allows, if the decider finds that an exception applies, a party turns the rule off, or the lower-ranked consideration outweighs the higher one?

Expected answer: YES for `needs`, NO for strict. A form passes if at most one of its `needs` items is read as strict and at most one of the 12 strict items is read as `needs`. The long form must pass. The short form is kept only if it passes and has fewer misreadings than the long form on N01–N06. If the long form fails, DF-3 waits for a redesign of the wording. If the short form is dropped, Lean always selects DE1′, and DE6 follows DE1.

Reader results are proxy evidence about this model's reading, not proof about human readers. No answer, bar or wording will be changed after seeing a reader result.
