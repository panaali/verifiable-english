# rights-cfr-5 report: single right lines round-trip with their header options

**Status:** built and waiting for the chain's gate. The DRI does not need to sign anything: row 1 of DELTA is
pre-signed (reviews/dri-decisions-20261109-lp0801.md item 1) and row 2 cites R1.
**What changed:** `render_line` and `parse_line` (ve/surface/rights.py) now carry the switch header that norm_english
renders (`Claim of right r (user may turn off). …`) and no other header.
**Open:** 126 of 506 generated lines still fail. Every one has two or more carve-outs, and the cause is
norm_english's soft parser, not this item (section 3). That fix is follow-up rights-cfr-5b. Trust +0. Pilot bytes: 0.
**HEAD:** the last commit on feature/rights-cfr-5 (see `git log`). Base: `49f1682dc`.

## 1. Task deliverables

The task is regrade #6 (reviews/l1-c-regrade-rights-20261109.md), item rights-cfr-5. The plan is
docs/spec/rights.md :228 (header options) and :436 (round-trip).

| # | Deliverable | Delivered by |
|---|---|---|
| 1 | `render_line` and `parse_line` accept exactly the header forms norm_english renders, read from the renderer and not retyped. | `render_line` keeps the renderer's own header text: it matches norm_english's `_SOFT_HEADER` and keeps `source[len("Rule 1"):]`. `parse_line` splits the line with the same `_SOFT_HEADER`, decodes the options with `softnorms.parse_header_options`, and accepts the header only if it equals `render_header_options((), parties)`, the renderer's spelling for one rule. A single line never renders a precedence option. ve/norm_english.py is unchanged. Tests: `test_rights_incident_roundtrip_with_switch` and `test_rights_incident_header_the_renderer_never_writes_is_refused`. |
| 2 | `test_rights_incident_roundtrip_with_switch`, failing on main first. | tests/test_rights.py. It covers a strict line, a default line and a line with two parties. On main's ve/surface/rights.py it fails with `InvalidInput: rights incident must have one rule`. I ran it by putting `git show main:ve/surface/rights.py` in place; the result was `3 failed` for the switch, negative and generated tests, and the file was restored afterwards. |
| 3 | A generated round-trip over the rights generator's lines, with the failure count before and after. | `line_roundtrip.py 200` covers every claim, liberty and immunity line with a predicate, in the 159 documents (seeds 0-199 of conformance/rights_differential.py) that correlate: 506 lines. **Before: 180 failed** (71 `InvalidInput: rights incident must have one rule`, the header; 109 `Expected a complete rule sentence`) (line-roundtrip-before.json). **After: 126 failed**, all `Expected a complete rule sentence`, all with `unless=2` (line-roundtrip-after.json). The permanent test `test_generated_rights_lines_round_trip_one_by_one` covers seeds 0-39 and every line with at most one carve-out. It asserts at least 50 lines and at least 5 with a switch. |
| 4 | A negative test: a header variant that norm_english never renders is still refused. | `test_rights_incident_header_the_renderer_never_writes_is_refused` uses 20 variants: empty parentheses, precedence options (`rule`/`rules`, either order with the switch), a trailing `;`, doubled spaces, case, other wording, a comma list, brackets, NBSP, tab, CR, full-width parentheses and a duplicate party. Each is refused with main's exact text. Unsorted and undeclared parties, which are in the rendered spelling, are refused by the soft checker (DELTA row 2). |

The 572-line set of the rights3 builder was not saved, so I could not reproduce it. Its current equivalent is the
506-line set above. The regrade (line 92) did not reproduce it either.

## 2. Seeded bugs (Python; ve/surface/rights.py, the only product file changed)

`seeded_bugs.sh` plants each bug, runs the one test named, and restores the file. Output: seeded-bugs.log, which ends
`RESTORED`.

| Bug | Mutation | Failing test |
|---|---|---|
| S1 switch dropped on parse | `raw.pop("alterable", None)` in `parse_line` | `test_rights_incident_roundtrip_with_switch` (dict mismatch) |
| S2 non-rendered header accepted | `_rendered_header` returns `True` | `test_rights_incident_header_the_renderer_never_writes_is_refused` (DID NOT RAISE) |
| S3 precedence option let through | the comparison uses `render_header_options(_refs, parties)` | the negative test (message `DependencyCycle: rule-1`, not main's text) |
| S6 unparsed header passed on | `except VEError: return True` | the negative test (message `Unknown rule header option …`) |
| S4 header dropped on render | `render_line` returns `. ` + body | `test_rights_incident_roundtrip_with_switch` (startswith) |
| S5 switch dropped on default lines | pop `alterable` when `mode == "default"` | `test_generated_rights_lines_round_trip_one_by_one` (seed 7) |

The task's two required bugs are S1 (the condition test fails) and S2 (the negative test fails). DRI adv0838 item
3(b) asks for the negative test to fail on a seeded break: S2, S3 and S6 show it does.

## 3. Lines still failing (126 of 506): cause

Every remaining failure is a line with two carve-outs. norm_english renders them as separate sentences:
`Rule 1. Every state must not …, if that person is adult. Except when … . Except when … .` Its own soft parser does not
read that back, even as a whole document. `parse_english(env, render_english(doc))` raises
`SyntaxError: Expected a complete rule sentence`; I probed this directly with a two-carve-out norm in the
correlated environment of seed 0. The cause is in `_parse_soft_english` (ve/norm_english.py:530 and :540).
`carveouts = first[sentence_end + 1:]` keeps the leading space, and line 540 adds another `" "`. The W1 parser then
gets `.  Except when` with two spaces. The task allows ve/norm_english.py to be edited only to expose the header
grammar, and the fix changes what parse_english accepts, so it is not made here.

FOLLOW-UP: rights-cfr-5b soft norm English: rules with two or more carve-outs do not parse back (double space at ve/norm_english.py:540)

## 4. DELTA, trust, size, pilot bytes

- DELTA.md has two rows. Row 1 is SIGNED by the DRI 2026-11-09 (lp0801 item 1), with its condition and negative
  tests. Row 2 cites R1 and has its saved-delta test. No verdict changes.
- Trust: `uv run python tools/trust_map.py --check` gives `K +0, S +0, D +0, G +0, tied +0, unclassified +0,
  trusted +0` and `PASS`. So no allowance and no FOLLOW-UPS.md row were needed.
- Size: `git diff --numstat 49f1682dc` gives +378 -5. Of that, 27/-5 is ve/surface/rights.py, 106 is tests, and the
  rest is docs and evidence. All of it is hand-written.
- Pilot bytes expected to move: 0. `render_line` and `parse_line` have no caller in `ve/`; I checked with
  `grep -rn "render_line\|parse_line" ve/`. Document rendering goes through `render_unit`.
- Spec re-read: the header options against docs/spec/rights.md:228-230. That text names `(users may turn off)` as an
  example and gives no grammar of its own, so the renderer's `render_header_options` spelling is the form. The
  round-trip against :436 (`print(parse(s)) = s` on canonical text).
- The spec's `(exception to claim 3 of right 12)` header (:229) is a W1 precedence form on a right line. Neither
  norm_english nor `render_line` renders it, so it stays refused, as the task asks.
- Evaluators and runners: no evaluator, runner or mode is added, so the rule does not apply.
- Not run by me: the full release gate (the chain runs it), trust_mutants (no Lean changed) and the Rust build (no Rust changed).

## 5. Next item

None (task: "Next item: none"), apart from the follow-up rights-cfr-5b above.
