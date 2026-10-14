# AT-0: the changed statements, for re-review (SR-8's last step)

> **Status.** 2026-10-13, branch `research/attitudes-p1`. The remaining SR-8 steps before the re-review are done:
> the stub is updated to the current spec draft (draft 4, whose Lean is draft 3's) with the frozen table written in,
> elaborated, and every fixture and the counterexample search are rerun on the frozen table, with the
> asserted-not-know form E2 admitted in the search's pool. Cited: the spec
> [docs/spec/attitudes.md](../spec/attitudes.md) (**spec n**), the E1/E2 report [attitudes-e1e2.md](attitudes-e1e2.md)
> (**E1E2 n**). The reviewers re-review only what section 2 lists. Nothing here is proved: elaborating a statement
> is not evidence that it holds, and the search is evidence against small counterexamples only.
>
> **2026-10-14: re-reviewed, FIX** (`manage-agents/attitudes-at0-review.final.md`): two B findings (2.2 items 1 and 3)
> and one C (2.5's seed count). Section 5 lists their corrections, spec section 17's **RR-1 to RR-3**, which the
> reviewers check next, and only those; sections 1, 2.2 and 2.5 are updated for them.

## 1. What was run

- **Stub:** `research/attitudes/stub/SpecStubs_attitudes.lean`, now committed (draft 1's was untracked in
  `ve-design-attitudes`). sha256 `dea412eb2654d245c12b48cc389c33d6292ad51c57421aa9640bec08d738f113` with RR-1 to RR-3
  (`0c73f880…` before them; `2178fb6e…` draft 1's), pinned in `research/attitudes/experiments.py` (`STUB_SHA256`).
- **Command:** from `lean/` at this branch's base `49de179e`: `lake env lean ../research/attitudes/stub/SpecStubs_attitudes.lean`.
  Exit 0, no `sorry`, no error, every `#guard` holds; 10 min 46 s, 1.5 GB with RR-1 to RR-3 (before them 10 min 53 s,
  1.5 GB; draft 1: 2 min 39 s, 210 documents). Full output: `docs/research/evidence/attitudes/at0-stub-run.txt`.
- **The stub's `table` is the frozen table:** Lean evaluates `PhaseOne.frozenTable == VE.Attitudes.table` to
  `true` with `e-table.lean`'s literal. On the new pin, `experiments.py selfcheck` holds 35 of 35 and
  `experiments.py table` gives `Table.reviewed` = `true` and an `e-table.lean` byte-identical to E1E2's.
- **Seeded bugs** (the stub is the only Lean changed; no product code changed): (A) `checkCond` without its last
  step `renderCheck`: 4 `#guard`s fail; the D14a–D14d rows answer `ok`; the search's `refusalMiss` = 190 of 190.
  (B) the search's admitted member read as `not K` (the refused form's other reading, without P): T9 = 1,040 of 2,080 valuations and the search's `#guard` fails (see
  section 2.2). For RR-1 and RR-2, on a copy without the full search: (C) `assertedNotKnows` as the composed tree
  `and P̂ (and P̂ (not K))`: RR-1's `#guard` fails (F-AT9's point `#guard`s and T9 still hold, since the two trees are
  equivalent: only the tree check sees it); (D) `assertedOf` ignoring the slot term: RR-1's `#guard` fails (`P̂` at
  the constant slot term `s1`); (E) the closed row's fixture expecting a refusal: RR-2's `#guard` fails. All
  restored; the committed stub is the one hashed above.

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

E2's six items reached 36 of 40 (E1E2 4.2), so the row's condition becomes "admitted (E2, six items)". The row is
English (AT-5), and its reading is the guard `and P̂ (not K)` with `K := att ⟨H, knows, σ, P⟩`, the same tree as
`NegatedFactive`'s first candidate (spec 3.4). After the re-review (section 5, RR-1) the reading is a spec definition,
`assertedNotKnows`, with its own statement. For re-review:

1. **Wording and reading.** The row's text reads `P ∧ ¬knows(P)`, as one tree, read whole (spec 3.1, RR-1). Composing
   `NegatedFactive`'s two candidates under "both P and …" would give `and P̂ (and P̂ (not K))` and `and P̂ (not K)`:
   equivalent formulas, but two trees, so equivalence alone does not give one derivation under the all-derivations
   rule (this item first said they "give the same guard", which overstated it). The grammar therefore reads the row
   as one construction, only when its first conjunct is the complement's clause with the same content and slot term,
   and its one derivation is `and P̂ (not K)`.
2. **The refusal's scope.** `NegatedFactive` now applies "anywhere but section 3.1's admitted row": the re-review
   checks that this exception is exactly the conjunct after "both P and" with the same P (holder, slot term and
   content), and nothing wider.
3. **Which statement carries the one reading.** `att_english_roundtrip` covers atomic conditions and
   `refused_have_rewrites` refused rows. The re-review asked for a statement (RR-1): `assertedNotKnows_one_reading`
   (spec 6.5), for each admitted `knows` occurrence `(Γ, c)`, the row's text in context `Γ` answers
   `readGuard = .ok (assertedNotKnows c)` and `readGuardAll = [assertedNotKnows c]`; and for fixtures read by the
   English reader (RR-2): spec 7.6's AT-5 read fixtures, the row alone, closed and nested, and the boundary of the
   exception refused (section 5).
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
   spec's citation should say so (done by RR-1: spec 3.4 and 6.5's `assertedOf`).
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
| candidate seeds enumerated (every sublist of the atoms) | 63,188 | 88,188 |
| seeds T4 checked (no nonfactive knowing; counted since RR-3) | — | 64,177 |
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

The re-review of section 2 returned FIX; what remains is the reviewers' check of section 5's corrections (RR-1 to
RR-3) only. Spec draft 5 then carries: the frozen table (2.1), the admitted row (2.2; its reading, statement and AT-5
fixtures are already in the spec by RR-1 and RR-2), the computed values in place of "*expected*" (2.3), the two
changed fixtures (2.4), the new search counts (2.5) and section 2.3's notes 1 and 3, as answered by the review
(note 2 is settled by RR-1).

## 5. The re-review's corrections (RR-1 to RR-3; spec section 17), for the reviewers' check

The re-review (`manage-agents/attitudes-at0-review.final.md`) returned FIX. Each finding is corrected as a class.

1. **RR-1 (B, 2.2 item 1): the admitted row's one derivation.** Equivalent readings are not one derivation:
   composing `NegatedFactive`'s candidates under "both P and …" gives two trees, `and P̂ (and P̂ (not K))` and
   `and P̂ (not K)`. Spec 3.1 now reads the row whole, as one construction, only when its first conjunct is the
   complement's clause with the same content and slot term; its one tree is `assertedNotKnows c` (spec 6.5, new, with
   `slotTermIn`, `slotIn`, `assertedOf`; `P̂ := base (assertedOf c)` in spec 3.4, which also settles section 2.3's
   note 2 on `Formula.subst`). New AT-5 statement, the singleton the review proposed:

   ```lean
   theorem assertedNotKnows_one_reading (A : AttDoc) (h : WellFormedAtt A = true) (Γ : List String) (c : Cond)
       (hc : (Γ, c) ∈ condsOf A) (hk : c.mode = .knows) :
       readGuard A Γ (renderAssertedNotKnows A Γ c) = .ok (assertedNotKnows c) ∧
         readGuardAll A Γ (renderAssertedNotKnows A Γ c) = [assertedNotKnows c]
   ```

   `renderAssertedNotKnows` is AT-5's renderer of the row (a stand-in in the stub, as `renderCond` is). The stub
   elaborates the statement, its instance on F-AT9 (`fat9_one_reading`), and a `#guard` that the row's tree is
   `and P̂ (not K)` and not the composed tree, that `P̂` is the content at a constant slot term and the content itself
   when closed, and that F-AT9's and the closed row's `knows` occurrences meet the statement's hypotheses.
2. **RR-2 (B, 2.2 item 3): AT-5 fixtures read by the reader.** Spec 7.6 lists AT-5's acceptance fixtures for the
   row, each a text read by the English reader in F-AT1's rule context (the stub's `readFixtures`, ten, with
   `readFixtures_hold`): the row's exact one reading alone (F-AT9's guard), on a closed content (`C(s1)`) and nested
   in "either … or"; and refused as `NegatedFactive` (`readGuard`, or `readRule` for the rule): another content in
   the first conjunct, another slot term on either side, the conjuncts reversed, the row's shape under "either … or",
   the bare form, and "unless". Their three documents (F-AT9 with `s1`, the closed row, the nested row) pass
   `checkAtt`, and a `#guard` checks that the texts are distinct and exactly the three row texts have one reading.
   F-AT9 is now in spec 7.1, and `att_english_roundtrip`'s AT-5 fixture list runs to F-AT9. F-AT9 and T9 still
   evaluate constructed guards; the reader's boundary is these fixtures' and AT-5's.
3. **RR-3 (C, 2.5): the seed count.** "Seeds tried" counted every sublist of the atoms (draft 1's too). It is now
   "candidate seeds enumerated", and the search also counts the seeds T4 checks, those with no nonfactive knowing
   (`seedsOf`, shared with T4): 64,177 of 88,188. Every other search count is unchanged.

For the check: the spec's section 3.1 paragraph and row, 3.4's `NegatedFactive` row and `P̂`, 6.5's new definitions
and statement, 7.1's F-AT9 and RR-2 rows, 7.5, 7.6's AT-5 read fixtures, 9's relabelled row, 12's new row and
section 17; and in the stub, S3f's additions and the fixtures and `#guard`s after F-AT9's.
