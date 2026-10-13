# AT-0: the changed statements, for re-review (SR-8's last step)

> **Status.** 2026-10-13, branch `research/attitudes-p1`. The remaining SR-8 steps before the re-review are done:
> the stub is updated to the current spec draft (draft 4, whose Lean is draft 3's) with the frozen table written in,
> elaborated, and every fixture and the counterexample search are rerun on the frozen table, with the
> asserted-not-know form E2 admitted in the search's pool. Cited: the spec
> [docs/spec/attitudes.md](../spec/attitudes.md) (**spec n**), the E1/E2 report [attitudes-e1e2.md](attitudes-e1e2.md)
> (**E1E2 n**). The reviewers re-review only what section 2 lists. Nothing here is proved: elaborating a statement
> is not evidence that it holds, and the search is evidence against small counterexamples only.

## 1. What was run

- **Stub:** `research/attitudes/stub/SpecStubs_attitudes.lean`, now committed (draft 1's was untracked in
  `ve-design-attitudes`). sha256 `0c73f88055c387c4418524c3c892b74ed6079760ed917f5cd121b084847b6a17`, pinned in
  `research/attitudes/experiments.py` (`STUB_SHA256`; was `2178fb6e…`).
- **Command:** from `lean/` at this branch's base `49de179e`: `lake env lean ../research/attitudes/stub/SpecStubs_attitudes.lean`.
  Exit 0, no `sorry`, no error, every `#guard` holds; 10 min 53 s, 1.5 GB (draft 1: 2 min 39 s, 210 documents).
  Full output: `docs/research/evidence/attitudes/at0-stub-run.txt`.
- **The stub's `table` is the frozen table:** Lean evaluates `PhaseOne.frozenTable == VE.Attitudes.table` to
  `true` with `e-table.lean`'s literal. On the new pin, `experiments.py selfcheck` holds 35 of 35 and
  `experiments.py table` gives `Table.reviewed` = `true` and an `e-table.lean` byte-identical to E1E2's.
- **Seeded bugs** (the stub is the only Lean changed; no product code changed): (A) `checkCond` without its last
  step `renderCheck`: 4 `#guard`s fail; the D14a–D14d rows answer `ok`; the search's `refusalMiss` = 190 of 190.
  (B) the search's admitted member read as `not K` (the refused form's other reading, without P): T9 = 1,040 of 2,080 valuations and the search's `#guard` fails (see
  section 2.2). Both restored; the committed stub is the one hashed above.

## 2. Changed since the statement review's re-check (p3ver1), for re-review

### 2.1 From E1 and E2: the frozen table (`table`, spec 2.1)

`table` now holds E1E2 4.3: `lowerBound` almost certain, very likely, quite likely, likely, more likely than not
(each `E1.cert.<w>`); `above` their 10 pairs (each `E1.pair.<a>.<b>`); `factive` `E2.factive`; `knowsBelieves`
`E2.knows-believes`; `knowsThinks` the five words (each `E2.knows-thinks.<w>`). `Table`, `Table.reviewed`,
`scaleCaps` and every statement are unchanged; `table_reviewed` holds (`#guard`), and the closure of the 10 pairs
adds none. Consequences to re-review:

1. `knows` and five `thinks w` modes are admitted; "as likely as not", "unlikely" and "very unlikely" are refused
   (D9, D0). E1E2 6 item 2: "as likely as not" fails for its own reason (read as about even), so its refusal
   advice should not group it with the downward words.
2. `BareThinks` (spec 3.4) has six rewrites: "H believes that P", then "H thinks it *w* that P" for the five words in
   `table`'s order; the row's "if E1 admits no word" branch is not taken.

### 2.2 From E2: "both P and H does not know that P" admitted (spec 3.1's last row)

E2's six items reached 36 of 40 (E1E2 4.2), so the row's condition becomes "admitted (E2, six items)". **No Lean
statement or definition changes**: the row is English (AT-5), and its reading is an existing guard, `and P̂ (not K)`
with `K := att ⟨H, knows, σ, P⟩`, the same guard as `NegatedFactive`'s first candidate (spec 3.4). For re-review:

1. **Wording and reading.** The row's text reads `P ∧ ¬knows(P)`. Inside "both P and …", `NegatedFactive`'s two
   candidates (`and P̂ (not K)`, and `not K` with P outside the scope) give the same guard, since P is asserted by
   the first conjunct; that is why the form can have one reading where the bare "H does not know that P" cannot.
2. **The refusal's scope.** `NegatedFactive` now applies "anywhere but section 3.1's admitted row": the re-review
   checks that this exception is exactly the conjunct after "both P and" with the same P (holder, slot term and
   content), and nothing wider.
3. **Which statement carries the one reading.** `att_english_roundtrip` covers atomic conditions and
   `refused_have_rewrites` refused rows, so the admitted row's one reading is carried today only by AT-5's
   acceptance fixtures (spec 7.6). Open for the reviewers: whether AT-5 needs a statement for it, for example
   `readGuardAll A Γ (text of the row) = [and P̂ (not K)]` for each admitted `knows` condition. The stub adds none.
4. **Fixture F-AT9** (new): F-AT1's rule with the guard `and C(var 0) (not knows C)`. Computed: check ok; one key
   `attitudes__knows__1`; one frame premise (`attitude:factive:attitudes__knows__1`); elaborated guard
   `and C(v0) (not knows__1(v1, v0))`. At the four points (category true/false × knows absent/present): intended
   true, true, true, false; guard true, false, false, false, under both the attitude semantics and the elaborated
   guard on `interp`. So the form holds exactly where the category holds and the knowing does not, and the frame
   neither refutes nor forces it.
5. **Search:** pool member 17 and check T9 (section 2.4).

### 2.3 Draft 2's and 3's statements and definitions, now elaborated

Until now these were written in the spec but not elaborated ("*expected*", spec status). All elaborate as written
in the spec, and every expected value is computed as the spec states:

- Statements: `frame_unsaidFree` (with `hw`), `decodeAttDoc_wellFormed`, `att_english_roundtrip` (on
  `(Γ, c) ∈ condsOf A`), `renderCond_injective`, `refused_have_rewrites` (with `Site` and `Candidates`).
- Definitions: `Lex`, `AttDoc.lex`, `mentionsSlot`, `lexPred`, `lexTerm`, `lexCovers`, `renderCheck`, `renderable`,
  `lexAgrees`, `checkCond`, `checkAtt`, `Site`, `Candidates`, `Refusal`.
- Diagnostics: D6a `InvalidInput: the English lexicon fails V1 for predicate mass_casualty_weapon_uplift`, D6b,
  D14a–D14d, each with section 5.2's text; D15 with its extended lexicon answers `ResourceLimit: MAX_PREDICATES`
  (RC-3). A `#guard` checks all 25 rows against section 5.2's texts.
- Fixtures: C-a, C-b, C-c admit the first document and refuse the second at D14a, D14b, D14c; C-d refuses both at
  D14d; F-AT8 passes `checkAtt`, `toU` gives a document, a factive premise names
  `unsaid__weapons_uplift_permitted`, and `WellFormedU` is false (so `frame_unsaidFree` without `hw` is false and,
  with it, does not apply); F-AT1's `U1` has `WellFormedU` true and an unsaid-free frame. The fixture lexicon and
  the search lexicon are valid (`Lexicon.failures` empty) and `lexAgrees` holds.

Where the stub had to choose what the spec leaves open (re-review only if the reviewers want them in the spec):

1. `VE.Attribution.Words.wantsPhrase?` is AT-1w's; the stub's stand-in knows only the copula ("{0} is …" gives
   "be …"), which is all C-c and the search use.
2. Spec 3.4 defines `P̂` with `Formula.subst` of `lean/VE/Core/Substitution.lean`, which is over `VE.Core.Formula`,
   not `VE.Formula`. A content is quantifier-free, so the stub's fixture helper replaces variable 0 directly. The
   spec's citation should say so (draft 5).
3. The fixture lexicon's wordings beyond the spec's: the regulated predicate "{0} is permitted to do the weapons
   uplift in {1}", hand-named terms 2–7 "{0} intentionally does <action> in {1}" with seven distinct actions, and a
   sort's letter its first letter. Category atoms take the quoted fallback, as spec 7 says.

### 2.4 Fixtures moved onto the frozen table, and the two the move changed

Every fixture that used the hypothetical `fixtureTable` now uses `table`: F-AT0, F-AT1, F-AT2, F-AT5, F-AT6, F-AT8,
F-AT9, C-a to C-d, the diagnostics, the AT-2 route points and the search. `fixtureTable` and its variants stay only
where a fixture needs a table E1 and E2 did not give: F-AT3 (no pair), F-AT7 (premise 3 for one word), D3 (the
review failures), D17 (a 58-byte word). Every value of spec 7.1–7.4 is unchanged on the frozen table (F-AT1's names,
frame and points M1–M4, RM1–RM4 with `table3`, `enumerateSettled` and the `InvalidModel` label; F-AT2's four
premises; F-AT5's 14 keys and 14 premises; F-AT6's four premises). F-AT3 and F-AT7 are also computed on `table`:
one premise from the table's own pair; two premises, "very likely" having its own item.

Two fixtures had to change, since the frozen table now admits what they used as inadmissible:

| Row | Was | Now | Answer |
|---|---|---|---|
| D4 | `declared := [("likely", "quite likely")]` | `declared := [("as likely as not", "quite likely")]` | unchanged: `UnsupportedProfile: a declared scale pair names a word that attitudes@0 does not admit` |
| D0 | F-AT1 with `T := table` (empty): `UnsupportedProfile: 'knows' is not admitted by attitudes@0` | F-AT1 under `table` is admitted; D0 is now `thinks "as likely as not"` under `table` | `UnsupportedProfile: 'thinks it as likely as not' is not admitted by attitudes@0` |

### 2.5 The counterexample search, rerun (spec 9)

On `table`, with the search lexicon and the spec's five new members (12–16: `knows ⊤` with an unused slot, D14a;
`knows p_case(var 0)` slotted at `c0`, D14b; `wants` of `p_case ∧ q_case`, D14c; the closed `knows p_case(c1)`
with `c1` in `E` only, D14d; `wants` of `p_case(x)`, admitted) and the admitted form (17:
`and p_case(x) (not knows p_case(x))`). A document holding a refused member must answer that member's row (the
first such member in document order); every other document is checked for T1–T8 as before and, when it holds
member 17, for **T9**: at every valuation where P holds, some intended relation makes the member true and some makes
it false; where P fails, none makes it true.

| | Draft 1 | Now |
|---|---:|---:|
| documents | 210 | 477 |
| draft 1's 210 documents admitted | 210 | 210 |
| admitted documents checked | 210 | 287 |
| refused documents answering their member's row | — | 190 of 190 |
| documents refused or over two keys without a refused member | — | 0 |
| document-model pairs | 6,720 | 9,184 |
| collapse instances tried | 480 | 768 |
| seeds tried | 63,188 | 88,188 |
| documents holding the admitted form, valuations T9 tried | — | 40, 2,080 |
| counterexamples to T1, T2, T3, T4, T5, T7, T8, T9 | 0 each | 0 each |
| control: draft-1 `guard_collapse` counterexample valuations | 17,096 | 34,237 |

The control still finds A3's counterexample class; its count grows with the documents. Seeded bug B (member 17
read as `not K`) gives T9 = 1,040: at each valuation where P fails, the empty relation makes `not K` true.

## 3. Unchanged

Every other statement, definition, diagnostic text and fixture value of spec draft 4 is unchanged and elaborates
as before. Sections 2.1 and 2.2 change no Lean statement; section 2.3 lists draft 2's and 3's changes, which the
re-check (p3ver1) already reviewed in text and which are now elaborated.

## 4. What AT-0 PASS still needs

The re-review of section 2 by both reviewers. Spec draft 5 then carries: the frozen table (2.1), the admitted row
(2.2), the computed values in place of "*expected*" (2.3), the two changed fixtures (2.4), the new search counts
(2.5) and section 2.3's three notes, as answered by the review.
