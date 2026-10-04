# English in Lean, stage S2: the English instance (plan)

**Status:** plan, draft 2, 2026-10-04, branch `design/english-lean-s2` (draft 1 was the pointer plan at
`340b9877`). Item 1 of this plan is stage S2 of [english-lean-PLAN.md](english-lean-PLAN.md) (the **base
plan**, draft 2): the English instance of the generic grammar engine. It builds on S0 and S1a/S1b, which are on
branch `english-lean/integrate` at `689219b1` and merge as `ve-green-english-lean`
([english-lean-measured.md](english-lean-measured.md), [english-lean-s1.md](english-lean-s1.md) on that branch).
The item-1 statement spec is [english-lean-s2.md](english-lean-s2.md). **Nothing was built for this draft.** The
spec's Lean statements were type-checked as stubs against the S1 build, and every verdict and count in its
fixtures was computed by the proved S1 parser; formulas were derived by hand and are confirmed against Python in
S2 (spec, section 0).

**Review provenance.** The debate directory `manage-agents/debates/design-english-lean-s2/` holds the review of
the base plan (rounds of 2026-10-03, converged after round 3: Fable's eight edits of round 3 with Astra's three
qualifications; where the two texts differ, Astra's governs). No round was held on the pointer plan itself. Draft
2 therefore applies that joint position as it bears on S2 (section 2), and the DRI's amendments of the pointer
plan (section 3), which take precedence where they differ from an edit. The statement spec is reviewed before
S2 proof work (section 1, S2.3).

## 0. Decision in brief

S2 makes the one-reading decision for formula-level English a Lean decision on real documents, under Python
authority. It writes the base profile's fixed rules as data, builds the lexical rules from the validated lexicon,
writes the action library and the readers, proves the English statements, exposes two service modes, wires the
Python adapter in shadow, and runs the G2 comparison on the sealed corpus, the reverse corpus and the lexicon
mutation replay. Nothing user-visible changes: `english.admission` keeps `authority: python` (DRI ruling 6).

Three things are decided here and nowhere else in this stage.

1. **Lean owns the grammar** (DRI amendment 1). Python gets no generated copy of the grammar. Python's hand parser
   and the Lark audit stay as the comparators of G2 and are retired with the authority flip (LEAN-FIRST E2).
2. **G2 is a corpus gate, not a calendar gate** (DRI amendment 2). The dispatch shadow log is the comparison
   instrument; there is no 14-day window in this plan.
3. **The readability writing gaps are fixtures, not parity.** "For every X, if A and B, then C" and "A or B, or
   both" have no derivation under today's grammar, and Python rejects them. The rules that would accept them are
   written and measured (spec 2.12, 8.5), but they enter the generated tables only by a signed product decision
   under SEMANTICS-MIGRATION-PLAN 2.3. The negated-existential message and the prohibition-as-exception guidance
   are diagnostic fixtures (spec 3.3, 4.5).

## 1. Item 1: stage S2

| # | Content | Owner | Done when |
|---|---|---|---|
| S2.0 | **Fixed rules as data.** `ve/english_grammar/relational-fol@0.json` (spec 2.9) for the base constructs, contractions, listings, guards, coordination, closure and natural clauses; the generator to `lean/VE/EnglishGrammar/Fixed/*.lean` (table literals, no theorem) with `--check`; `ve/english_grammar/LOCK.json` with `actions_version`; the commit-hook check (spec 4.5, t1, i5) | Python implementer | the generated table equals the fixed rules of spec 2.5 rule for rule; `--check` and the lock check fail on t1 and i5 |
| S2.1 | **Grammar construction.** `lexRules` (spec 2.6), `grammar`, `ty`, the nonterminal catalogue (spec 2.4); `start_sentence` holds by construction (spec 5.6); `terminatorFree` of every generated and lexical rule | Lean implementer | spec 8.1 verdict fixtures b1 to b48 and d1 to d4 reproduce; `grammar_rules` and `lexRules_terminatorFree` proved |
| S2.2 | **Actions and meaning.** The action library of spec 2.7 (fixed actions and the lexical constructors), the context threading (`Ctx`), the side conditions, the two new `Reject` codes for the DRI (spec 2.8); `meaning` | Lean implementer | spec 8.2 meaning fixtures reproduce against Python's formulas; no action constructs `Reject.internal` (source test) |
| S2.3 | **Readers and statements.** `read`, `translate`, `checkRendering`, `EnglishOneReading`; the theorems of spec 5.6 proved; audit, frozen-inventory and layer entries | Lean implementer | `lean/audit.py` clean, standard axioms only; the statement review of the spec has passed before any proof is written |
| S2.4 | **Service.** Modes `english.read` and `english.grammar` in a new executable (`Main.lean` is frozen); the six identities (spec 2.10); the JSON export (spec 4.4) | Lean implementer | fixtures i1 to i6, t4 |
| S2.5 | **Adapter and shadow.** `ve/backends/english_lean.py`: the Lean call under `dispatch.execute("english.admission", …)`; authority stays `python`; shadow records with the spec's comparison classes; `invalidGrammar` fails closed as `CheckerUnavailable`; the `glued` flags in the Python reference lexer and in `conformance/english_lean_tokens.py` (S1 report, section 6) | Python implementer | under `VE_AUTHORITY_OVERRIDES=english.admission=shadow` every call is recorded; nothing changes under the default |
| S2.6 | **G2 harness.** The tree correspondence (spec 2.11); the comparison on the sealed corpus (`conformance/english_lean_seal.py --check` first); the reverse corpus sampled from the `english.grammar` export with spacing and word-split mutants; the lexicon mutation replay; the three-way differential on the 57,765 core texts; the use-case documents and pilots read through the seal; the readability-gap fixtures; the two budgets S1a could not measure (BlueDot document ≤ 1 s, generated modules ≤ 60 s of `lake build`) | Python implementer | the G2 report `docs/spec/english-lean-s2-report.md` |

**Gate G2** (base plan, section 5, as amended): on every sealed corpus text, the verdict (zero, one or many),
the formulas in wire form, the canonical strict text, the conclusion marks and the witness multiplicity agree
with Python under the tree correspondence; on the reverse corpus every text Lean accepts is accepted by Python
with the same formulas, or is dispositioned under SEMANTICS-MIGRATION-PLAN 2.3; under lexicon mutation no corpus
text gets a different formula; zero unexplained differences; the two budgets met or their revision reviewed;
audit clean with the spec's theorems in the inventory. Known listed items that are not differences:
`usecases/asimov-extended` fails V1 until S3 (DRI ruling 2); wall-clock `ResourceLimit` outcomes are excluded
and listed.

**Not in S2:** the profiles (`order@0`, `data@0` sugar and its factoring, alternatives guards, risk wordings:
S3); the authority flip, the deletion of `EnglishParser` acceptance and the Lark audit, and the retirement of the
reference implementations (LEAN-FIRST E2, which merges the base plan's S5 and S7); statement-layer English (E3);
the widenings of spec 2.12 as accepted forms; a two-lexicon theorem; the static tier.

**Order.** S2.0 and S2.5 (Python) run in parallel with S2.1 and S2.2 (Lean). S2.3's proofs start only after the
statement review of the spec. S2.4 after S2.3; S2.6 after S2.4 and S2.5. Effort as the base plan: two to three
weeks elapsed.

## 2. Converged edits applied

The joint position of the review (section "Review provenance") as it bears on this stage. Edits 1, 2 and 2a
were discharged by S0 and S1a and are only inherited here.

| # | Converged edit | Where applied in this stage |
|---|---|---|
| 1 | **Size.** No fixed ceiling; the attribute-property product is factored | inherited: S0 measured it (measured.md, section 2); the factoring is S3's. The spec's fixture grammar for the base profile has 117 rules and `|G|` = 479 (spec 8.1), measured, not estimated |
| 2 | **Cost.** Cap invariant, rule-suffix memoisation, measured steps | inherited: S1a/S1b (s1.md, section 2). S2 owes the two remaining G1a figures (S2.6) |
| 2a | **G1a is a pass gate** | inherited; the two owed budgets keep that rule: met, or a reviewed revision (S2.6, G2) |
| 3 | **Parity.** Tree correspondence; compare verdicts, formulas and witness multiplicity, not rule sets | S2.6; spec 2.11 writes the correspondence out, with the capitalised-spelling case that S0 left open (spec 11, Q5); G2 compares the three |
| 4 | **Reverse corpus.** Texts sampled from Lean's exported grammar, spacing and word-split mutants, against the hand parser and Lark; Lark a logged comparator until retirement | S2.4 (`english.grammar`), S2.6 (the sampler, spec 2.11); Lark and the hand parser stay comparators until E2 (section 3, amendment 1) |
| 5 | **`extension_safe`.** Semantic `Embeds`; vocabulary reselection is not an extension | inherited (proved in S1b). S2 writes the body of `Extends` for the reviewers, as the statement spec of item 1 required (spec 2.13, 5.6 `grammar_extension`); q5 shows reselection is not an extension, q6 an extension |
| 6 | **Lexicon.** `valid` with V4 and V5; the lint sort; P1 per lexicon; mutation replay an empirical gate; no meaning-neutrality claim | inherited (S1b, DRI ruling 4); S2.6 runs the mutation replay (spec 2.11, fixtures e23 and m1 to m5); the final lint list is fixed at this spec's statement review (spec 2.14, Q3); `english_reading_unique` is proved for one lexicon and claims nothing more |
| 7 | **Contract.** `DocOneReading` fold; `read_ok` and `checkRendering` conclude formulas and marks; `EnglishOneReading` includes `Lexicon.valid`; evidence binds six identities | S2.3 and S2.4: spec 5.6 (`read_ok`, `read_stopped`, `checked_rendering`, `checked_rendering_exact`), 2.10 (identities) |
| 8 | **Options, shadow.** Option H in reserve; G4 keeps its window and adds volume and coverage targets (Astra's text governs) | option H: inherited (not needed; S1b proved the chosen parser). G4: **superseded by the DRI** (section 3, amendment 2): no calendar window; the volume and coverage targets of S0 (measured.md, section 10) become the reverse-corpus and coverage rows of G2 (spec 2.11) |

Astra's three qualifications: (1) mutation replay is empirical and the guarantee is per lexicon (spec 2.11,
5.7); (2) semantic preservation reaches complete results and `actions_version` covers every trusted definition
file (spec 2.10, 5.6); (3) G1a stays a pass gate (S2.6). All three hold in this draft.

## 3. DRI amendments and rulings in force

| # | Amendment (lead directive 2026-10-04; pointer plan) | Where applied |
|---|---|---|
| A1 | Lean owns the grammar and the one-reading decision; Python gets no generated copy; Python's English path calls Lean once the authority flips; the Python parser is only the comparator until then | section 0 (1); S2.5; spec 2.11 (comparators), 9 (not claimed). The base plan's "Python's grammar is generated from Lean's" (section 4, S5 row) is replaced by LEAN-FIRST E2's text: the editor's Lark grammar is generated from Lean's data and never decides acceptance |
| A2 | The 14-day shadow is replaced by corpus evidence (LEAN-FIRST E2) | section 0 (2); G2; edit 8 above |
| A3 | The readability-eval writing gaps are fixtures (`manage-agents/ARCH-ROADMAP.md`, "English grammar coverage") | section 0 (3); spec 2.12, 3.3, 4.5, 8.5 |
| A4 | DRI rulings 1 to 6 (`manage-agents/english-lean-dri-note.md`) stay in force | ruling 1: the `glued` flags are in the tokens and the fixed rules name them (spec 2.5, b30, b31); ruling 2: no V1 exemption, `asimov-extended` listed (G2); ruling 3: `coefficientNotNumeral` and the two blocked-wording ids are in `Reject` and the action library uses them (spec 2.8); ruling 4: the ported codes are V3 to V5, the retained eight stay Python checks in S2, final list at the statement review (spec 2.14); ruling 5: `workBudget` 2,100,000 steps is the `b` of `read` (spec 2.3); ruling 6: the merge scope of S0 + S1 is unchanged by this plan, and S2 is the next merge |

## 4. Honest open questions

1. **The two widenings (A3).** "Every service is deployed or reviewed, or both." and "For every person, if that
   person is deployed and that person is reviewed, then that person is reviewed." have no derivation today
   (computed: spec b27, b28), and the three rules of spec 2.12 give each exactly one (spec 8.5) without changing
   any other fixture's verdict in the sample. Accepting them widens the language. Recommendation: keep the rules
   in the JSON source with `"status": "proposed"`, excluded from the generated table, until the DRI signs the
   widening under SEMANTICS-MIGRATION-PLAN 2.3; then they enter with a release note and the G2 harness treats the
   affected corpus texts as dispositioned. Not decided here.
2. **Two new rejection codes** (spec 2.8): `coordinationRepeated` (a coordination names one constant or one
   adjective twice; Python rejects it as an unknown phrase) and `naturalScoped` (a natural clause under a
   binder; Python's natural hook returns nothing when the scope is not empty). Both are tier B additions like
   `coefficientNotNumeral`. For the DRI at the statement review.
3. **The final lint list** (ruling 4; LEAN-FIRST DRI answer 5). Proposal in spec 2.14: five of the eight retained
   codes and the hole-order rule of `TEMPLATE_SHAPE` protect the reading and become Lean validity conditions
   when Python's lint retires (E2); three are style and become editor warnings. In S2 all eighteen stay in the
   Python producer, so nothing widens. Fixed at the statement review.
4. **The body of `Extends`** (spec 2.13) is proposed, not accepted: profiles equal, every symbol and selection
   kept, both lexicons valid. Fixtures q5 and q6 give both directions. The reviewers decide; the profile case
   stays deferred.
5. **Mid-sentence capitalised spellings.** Python derives `The api` mid-sentence through a capitalised duplicate
   alternative; S0's conversion dropped it and recorded the difference. The fix needs a terminal that accepts a
   word only when it is not initial (spec 2.2, `kwMid`), a tier B change to `Terminal`. Without it the
   sentence-initial `The api` would have two derivations. Fixtures are obligations (spec 8.1, c1 to c3), not
   computed here.
6. **V3 and the terminator.** A declared wording containing `.` lexes as two sentences. Proposal (spec 2.6): V3
   also requires the wording to lex as one sentence of word and quoted tokens, so `lexRules_terminatorFree`
   holds by construction. Python's lint already refuses such wordings, so no corpus lexicon changes class.
7. **Budgets owed.** BlueDot ≤ 1 s and `lake build` of the generated modules ≤ 60 s are unmeasured until S2.6.
8. **The `english.grammar` export** fixes a JSON shape (spec 4.4) that the reverse-corpus sampler and, after E2,
   the editor's grammar generator read. A later change is a wire change of that tool, not of any identity.
9. **Translation mode over documents** stays unspecified (base spec O9); `translate` reads one sentence.
10. **`Reject.internal`** is never constructed by an action: a property of the library checked by a source test,
    not a theorem (spec 5.7, `meaning_total` makes it unreachable from a derivation).
