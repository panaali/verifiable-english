# English in Lean, stages S3 + E2: the profiles, then Lean as the authority (plan)

**Status:** plan, draft 3, 2026-10-05, branch `design/english-lean-s3` (draft 1 was the pointer plan at
`6b48c009`; draft 2 is `3034d60e`). Draft 3 applies the corrections of the statement review of the spec
(section 6). Item 1 of this plan combines stage S3 of [english-lean-PLAN.md](english-lean-PLAN.md) (the **base
plan**, draft 2: formula-level profiles in the Lean grammar) with track E2 of `docs/LEAN-FIRST-PLAN.md` (branch
`design/lean-first`, sections 5.2 and 6.3): `english.admission` moves to Lean on corpus evidence, and the Python
English parser leaves the admission path. It builds on S2, merged on `main` at `1e68d6d6`
([english-lean-s2.md](english-lean-s2.md), the **S2 spec**; [english-lean-s2-integrate.md](english-lean-s2-integrate.md),
the **S2 record**). The item-1 statement spec is [english-lean-s3.md](english-lean-s3.md), draft 2. **Nothing was
built for this draft.** The spec's Lean statements were type-checked as stubs against the S2 build, and every
verdict, formula, count and step figure of its fixtures was computed by the proved parser and the S2 reader over
hand-written profile rows (spec section 12). Python's outcome on each fixture was read from the source and is
confirmed in S3.5; a difference there is a finding, not a failed fixture. Draft 2 of the spec changed text
only: its added fixtures are obligations, and its changed Lean texts were not elaborated again.

**Review provenance.** The debate directory `manage-agents/debates/design-english-lean-s3/` holds the review of
the base plan (rounds of 2026-10-03, converged after round 3: Fable's eight edits of round 3 with Astra's three
qualifications; where the two texts differ, Astra's governs). It is the same joint position that the S2 plan
applied. No round was held on the pointer plan itself. This draft applies that joint position as it bears on S3
and E2 (section 2), and the DRI's amendments of the pointer plan (section 3), which take precedence where they
differ from an edit.

The statement review of the spec was then held in `manage-agents/debates/english-lean-s3-spec/` (Astra and
Fable, three rounds on 2026-10-05). It converged on FIX: a package of corrections, not a pass of draft 1. The
theorem statements of admission needed no change. Draft 2 of the spec and this draft apply the package
(section 6). What remains before proof work is a bounded re-check of the changed sections by both reviewers
(section 1, S3.4).

## 0. Decision in brief

S3 gives the Lean reader the five formula-level profile surfaces: integer terms and comparisons (`order@0`),
attribute sugar (`data@0`), the three guard phrases (`alternatives@0`), the risk wordings with their blocked
forms (`risk@0`), and the modal wording of regulated predicates (`norms@0`). E2 then makes Lean the authority
for `english.admission`. Five things are decided here.

1. **Two gates, one stage.** S3 ends at gate G3 under Python authority, as S2 ended at G2. E2 ends at gate GE2,
   which is the lean-first gate (suite, corpus A/B, deletion ledger, latency). Authority moves only at GE2.
   G2's harness was not built in S2 (S2 record, section 5); S3.5 builds it once, for the base profile and the
   profiles together.
2. **No new type, context field or rejection code for the profiles.** The profile rows use the `Ty`, `Ctx`,
   `TermVal` and `Reject` of S2. The stub shows it: the profile actions type-check against the S2 `sig` (spec
   2.4, 2.7, section 12).
3. **V3 gains "subject first" in S3, not in E2.** Every selected wording begins with `{0}` and has its holes in
   increasing order. The guard phrases need it (spec 2.6), Python's lint already enforces it for every wording
   its producer selects, and it makes the three corners that cost S2 three verification passes unreachable
   (S2 spec e51 to e53). The rest of Python's acceptance of a declared wording (V6) moves in E2.1, and no lint
   code that refuses a wording today becomes a warning there without the DRI's signature (spec D14).
4. **The product is factored per value sort**, as the converged edit 1 requires: one rule per relation over a
   property nonterminal of its value sort. On the fixture every pair has one derivation in both shapes and the
   same formula; at 128 relations and 128 properties the rows are 384 against 16,512 (spec 8.2, 8.10).
5. **After the flip Python's parser decides nothing.** `parse_english` relays Lean's answer. The hand parser and
   the Lark audit run only as a comparator that is switched on in gate runs, logs differences and can never
   change a result. They are deleted from the admission path at E2.3. The class `EnglishParser` itself stays
   until E3 has moved the statement layers that call it (`norm_english.py`, `norm_defaults_english.py`).

## 1. Item 1: stages S3 and E2

| # | Content | Owner | Done when |
|---|---|---|---|
| S3.0 | **Profile rows as data.** `ve/english_grammar/order@0.json` (25 rows) and `alternatives@0.json` (8 rows) (spec 2.5); the catalogue additions and the profile certificate `ranksStaged` (spec 2.4); the generator writes `Fixed/Order.lean` and `Fixed/Alternatives.lean`; `LOCK.json` and `actions_version`. The base table source is not edited | Python implementer | the generated tables equal spec 2.5 row for row; `--check` and the lock check pass; `grammar_id` of a base-profile environment is unchanged (spec ev1) |
| S3.1 | **Environment, boundary and validity.** `Env` gains `alternatives`; `PredDecl` gains `functional`, `total`, `modal` and `description`, all with defaults; the risk flag is read from the profile list and is no field (spec D19). `Env.decode` adds the symbols the blocks generate and computes `forms`, the modal form from the canonical act of `Norms.Wire` (spec 2.3). **The JSON boundary** (spec D18, 2.3): the profile and block declarations validated as submitted, the family decoders and the typed check over the typing view with a new `riskReduced`, `environment_id` over the submitted environment; `Route.Gate.decodeEnvelope` is not edited. V3 gains subject first, and V2 counts the modal form as the only honest wording of a modal predicate (spec 2.9, D17). `risk__more_severe` gets the wording `{0} is more severe than {1}` in Lean's forms and in Python's producer (DRI ruling 2, a signed change of the English surface) | Lean and Python implementers | spec 8.6 reproduces, lx9b to lx9d included; `english.read` admits the real environment JSON of `FA`, `FR`, `FM` and of a unit-bearing risk environment with the identity Python computes, types their documents, and refuses the malformed declarations (spec ev8 to ev13); `usecases/asimov-extended` passes V1; over the corpus environments every selected wording is subject first (spec lx14) |
| S3.2 | **Rules.** The lexical families of spec 2.6: integer slots and constants, attribute and property rows over value-sort nonterminals, the guard family; a noun or a spelling is spelled with `textSyms`, never by splitting at spaces (spec D20); `fixedRules`, `ranksFor`, `ty`, `grammar` by profile list (spec 5.2) | Lean implementer | the verdicts of spec 8.1 to 8.5 and 8.7 reproduce on `grammar E L`, the quoted names included (spec or37, al36 to al38); the sizes of 8.10 are measured on the real rows |
| S3.3 | **Actions.** The actions of spec 2.7, with the evaluation order of a clause's slots and the guard's checks in Python's order; the guard's risk flag is an argument that `lexActs` sets from the profile list | Lean implementer | the formulas and rejections of spec 8.1 to 8.5 reproduce, ri16 as a test of the action alone; `Grammar.typed` holds for every fixture grammar; no action constructs `Reject.internal` |
| S3.4 | **Statements.** The statements of spec 5.5 proved; audit, frozen-inventory and layer entries | Lean implementer | `lean/audit.py` clean, standard axioms only; the bounded re-check of spec draft 2 (spec section 10, items 14 to 21) has passed before any proof is written |
| S3.5 | **G2 and G3 harness** (owed from S2.6, extended per profile): the comparison on the sealed corpus at the dispatched boundary; the reverse corpus per profile; the lexicon mutation replay; the three-way differential on the 57,765 core texts; the use-case documents and the pilots through the seal; the readability fixtures; the Python outcome of every spec fixture; the two budgets owed since G1a | Python implementer | the report `docs/spec/english-lean-s3-report.md`, with one delta section per profile |
| E2.0 | **Service.** `english.read`, `english.grammar` and `english.check` as modes of `ve_service` with their response shapes, and a grammar cache keyed by `environment_id` and `lexicon_id` (spec 2.10); `ve_english_route` is deleted with its transport | Lean implementer | spec ev2 to ev4; the latency rows of GE2 measured on the service |
| E2.1 | **Python's acceptance of a declared wording** becomes condition V6 of `Lexicon.valid` (spec 2.9), in three parts: every lint code that refuses a declared wording today, with the rescue; the idiom branch, which keeps the anchor, collision, direction and negated-head checks and reads `PredDecl.description`; the reserved risk wordings. No code becomes a warning: `TEMPLATE_LENGTH`, `BINARY_VERB`, `IDIOM_UNRELATED` and `ENGLISH_STRUCTURE_WORD` still refuse, and a code the DRI drops is a signed `verdict` row of `DELTA.md` | Lean and Python implementers | spec lx15 to lx24; Python's own selection passes V6 on every corpus environment; the bounded statement review of V6's ported tables (the code set, the rescue patterns, the idiom branch) has passed |
| E2.2 | **Admission in Lean.** `admit`: the reading and the obligations of the marked conclusions (spec 2.10, 5.3); Lean's codes and texts with the advice table (spec 4.2, 4.3); the message table exported, so the relay holds no text of its own | Lean implementer | spec 8.8, 8.9; the theorems `admit_ok`, `admit_exact`, `admit_no_premise`, `obligations_exact` proved |
| E2.3 | **The flip.** `english.admission` gets `authority: lean` in the assurance manifest and leaves `dispatch.SHADOW_ONLY`; `parse_english`, `parse_english_with_metadata` and `parse_english_argument` relay `admit`; the renderer's candidates are checked by `english.check`; records carry claim C2 with the six identities; the hand parser and the Lark audit run only as the comparator of spec 2.10 | Python implementer | gate GE2 |
| E2.4 | **Deletions.** The deletion ledger of the lean-first gate: every Python decision site of formula-level admission is mapped to the Lean check that owns it, deleted, or listed as kept for E3 with its caller; the test-only reference implementations (`conformance/english_lean_{engine,lexer,lexicon}.py`) are deleted once nothing compares against them | Python implementer | `tools/relay_lint.py` passes on `ve/english.py`'s admission path; the ledger is signed |

**Gate G3** (base plan, section 5, as amended; under Python authority): on every sealed corpus text of every
profile, the verdict (zero, one or many), the formulas in wire form, the canonical strict text, the conclusion
marks and the witness multiplicity agree with Python at the dispatched boundary under the tree correspondence
of spec 2.11; on the reverse corpus every text Lean accepts is accepted by Python with the same formulas, or is
dispositioned under SEMANTICS-MIGRATION-PLAN 2.3; under lexicon mutation no corpus text gets a different
formula; zero unexplained differences; one delta report per profile; audit clean with the spec's theorems in
the inventory. Listed items that are not differences: wall-clock `ResourceLimit` outcomes (excluded and
listed); the texts `risk__more_severe` newly reads (DRI ruling 2, listed in the risk delta); the texts in
which an integer term deeper than 64 stands before a malformed part of the clause's integer slots, where
Python reports `ResourceLimit` and Lean no reading (spec 2.11, or38; listed in the `order@0` delta).

**Gate GE2** (LEAN-FIRST 5.1, for this batch): (1) the full suite at the batch head, test changes limited to
the listed wording and order changes; (2) the corpus A/B between the base commit and the batch head over the
85,000 English pairs, the 12,750 audit texts, the 850 documents, the mixed and natural-view streams, every
use-case document and harness with its answer key, and every historical pilot document, identical or listed in
`DELTA.md` as `wording`, `order`, `verdict` or `availability`, each verdict or availability change signed by
the DRI; the comparator on, with zero undispositioned differences; (3) the deletion ledger of E2.4; (4)
latency, on the service: the base plan's budgets (corpus sentence p95 at most 20 ms, a 150-token sentence at
most 50 ms, the BlueDot document at most 1 s, grammar instantiation at most 100 ms and cached, the generated
modules at most 60 s of `lake build`), and a 300-token sentence inside the work budget with its latency
reported (DRI ruling 5 sets the design point and no latency figure for it); each budget met, or a revision
reviewed before the flip (the rule of G1a). There is no calendar window.

**Not in this stage:** statement-layer English (E3: norm rule blocks, legends, reports, speech, quantities,
definitions, soft norms, rights, and the `rights@0` wordings that the rights correlation installs); the two
widenings of S2 spec 2.12 as accepted forms; a two-lexicon theorem; the static tier; a Lean renderer; the
senses layer (`design/senses`), which comes next and reads this stage only through `Env`, `Overlay`, `Lexicon`
and the six identities.

**Order.** S3.0 and S3.5's harness (Python) run in parallel with S3.1 to S3.3 (Lean). As the statement review
converged: S3.0 and S3.5's harness could start on draft 1; S3.1 to S3.3 start on spec draft 2, which carries
the corrected definitions and recipes; S3.4's proofs and E2.1 start after the bounded re-check of spec draft 2
by both reviewers. That re-check covers the changed sections and their fixtures (spec section 10, items 14 to
21) and is not a full pass. V6's ported tables keep their own bounded review before the flip. G3, then E2.0 to
E2.2 in parallel, then E2.3 at GE2, then E2.4. Effort: S3 one to one and a half weeks (base plan), E2 one
batch of the lean-first size for each of E2.0 to E2.4.

## 2. Converged edits applied

The joint position of the review (section "Review provenance") as it bears on this stage.

| # | Converged edit | Where applied in this stage |
|---|---|---|
| 1 | **Size.** No fixed ceiling; factor the attribute-property product into one rule per relation over a per-sort property nonterminal, derivations one to one; otherwise the DRI reviews a new limit | S3.2; spec 2.4 and 2.6 (one property nonterminal per value sort), 2.11 (the correspondence), 8.2 (da17 to da19: six pairs, the same verdict and the same formula in both shapes) and 8.10 (384 rows against 16,512 at 128 by 128, computed). S3.5 measures the real sizes on the `english.grammar` export |
| 2 | **Cost.** Cap invariant, rule-suffix memoisation, measured steps | inherited (S1). Measured here on the fixture grammars: at most 14,503 steps for a sentence, 0.69% of the work budget (spec 8.10). The two budgets S1a could not measure are owed by S3.5 and GE2 |
| 2a | **G1a is a pass gate** | GE2, item 4: each latency budget is met, or its revision is reviewed before the flip |
| 3 | **Parity.** Tree correspondence; compare verdicts, formulas and witness multiplicity, not rule sets | S3.5; spec 2.11 writes the correspondence for each profile, with the three places where Lean's rows are not Lark's shape (the factoring, the punctuation nonterminals of integer terms, the head of a guard's verb), the two where Lean derives less than Lark on texts Python rejects, and the one class where both refuse and the class of the refusal differs by agreement (a term too deep before a malformed part) |
| 4 | **Reverse corpus.** Texts sampled from Lean's exported grammar, spacing and word-split mutants, against the hand parser and Lark; Lark a logged comparator until retirement | S3.5, per profile; after the flip the hand parser and Lark are the comparator of spec 2.10 until E2.4 and E3 delete them (section 3, amendment P2) |
| 5 | **`extension_safe`.** Semantic `Embeds`; vocabulary reselection is not an extension | inherited (proved). S3 restates `Extends` for any one profile list with a renaming of the property nonterminals (spec 2.13, 5.4, 5.5 `grammar_extension`); if the proof does not go through in S3.4, the statement stays on S2's domain, deferred rather than weakened |
| 6 | **Lexicon.** `valid` with V4 and V5; the lint sort; P1 per lexicon; mutation replay an empirical gate; no meaning-neutrality claim | S3.1: the profile forms that V2 and V5 read are computed in Lean, V3 gains subject first, and V2 gives a modal predicate one honest wording; E2.1: V6, which relaxes nothing Python refuses today; S3.5 runs the mutation replay, the three bypasses of a modal wording included; `english_reading_unique` is unchanged and claims nothing about a second lexicon |
| 7 | **Contract.** `DocOneReading` fold; `read_ok` and `checkRendering` conclude formulas and marks; `EnglishOneReading` includes `Lexicon.valid`; evidence binds six identities | the S2 statements stand word for word over the wider grammar (spec 5.5); E2.2 adds `admit` and its four statements; E2.3 attaches the six identities to every record |
| 8 | **Options, shadow.** Option H in reserve; G4 keeps its window and adds volume and coverage targets (Astra's text governs) | option H: not needed. G4: **superseded by the DRI** (section 3, amendment P1): corpus evidence at GE2, no calendar window |

Astra's three qualifications: (1) mutation replay is empirical and the guarantee is per lexicon (spec 2.11,
section 9); (2) semantic preservation reaches complete results, and `actions_version` covers every trusted
definition file, the two new tables included (spec 2.14); (3) the budgets are pass gates (GE2). All three hold
in this draft.

## 3. DRI amendments and rulings in force

| # | Amendment (pointer plan, DRI, 2026-10-05) | Where applied |
|---|---|---|
| P1 | E2 moves `english.admission` to Lean on corpus evidence (the English pairs, use cases, pilots) instead of S4's 14-day shadow | GE2; edit 8 above |
| P2 | The Python English parser leaves the admission path and is kept only as a logged comparator until deleted | section 0 (5); E2.3, E2.4; spec 2.10. LEAN-FIRST 6.3 says "deleted in the same batch"; the pointer plan is later and governs, and the statement layers still call the class (question 3 below) |
| P3 | One owner: Lean decides English acceptance and the one-reading check; Python calls it through the relay and keeps file I/O and display | E2.2 (`admit`, the message table), E2.3 (the relay); spec D10 to D13 |
| P4 | No Python copy of the grammar | S3.0 (the tables are generated into Lean only); the editor's Lark grammar, if it is kept, is generated from the `english.grammar` export and never decides (LEAN-FIRST 5.2) |
| P5 | DRI rulings 1 to 6 of `manage-agents/english-lean-dri-note.md` stay in force | ruling 1: the integer marks carry their spacing in the rules, and the guard and attribute rows match exactly where Python's `take` is exact (spec 2.2, 2.5, 2.6); ruling 2: S3.1; ruling 3: `coefficientNotNumeral` and `risk-every-cannot` are used (spec 2.8); ruling 4: E2.1; ruling 5: 300 tokens and 2,100,000 steps are GE2's design point; ruling 6 scoped the S0 and S1 merge, and S2 kept `authority: python`: authority moves at GE2 and nowhere earlier |
| P6 | The readability-eval writing gaps stay required fixtures | spec 2.12, 8.7, 8.8: the three sentences keep verdict zero under every profile grammar (computed), the widening rules stay proposed, and W12's message is the advice `negated-existential` |
| P7 | The senses design is next and must be able to extend this lexicon without changing identities | spec 2.14: `Lexicon`, its wire form and the preimage of every identity are unchanged; every new `Env` field has a default; the base table source is not edited; rule tags do not depend on what else the lexicon holds |

## 4. What S2 left open, and where it goes

| Item (S2 record, section 5) | Here |
|---|---|
| S2.6, the G2 harness | S3.5 |
| g1, the suggestion quotes whole tokens | E2.2: the suggestion is Python's editor help over Lean's tokens (spec 4.3) |
| `LeanService` transport; `english.read` is one-shot | E2.0 |
| the grammar-instantiation diagnostic (first failing rule) | E2.0 |
| the manifest binding of `english.read` | E2.3 |
| DRI rulings on the four S2 codes, `kwMid`, V3 and the terminator, F3 | assumed adopted as built; F3 (the order of the nesting limit and a later fault) is listed in GE2's `DELTA.md` as `order` |

## 5. Honest open questions

1. **Python's outcomes are read, not run.** Every fixture of the spec was computed in Lean. What Python does on
   each was derived from `ve/english.py` by hand, as S2's formulas were. S3.5 runs them; the corners most likely
   to differ are the capitalised reference at the head of a guard's verb, `it` inside an attribute, the
   order of two faults in one integer term (spec 8.3, 8.2, 8.1), and the fixtures spec draft 2 adds, none of
   which was computed in Lean either: the quoted names, the lexicon cases of V2 and V6, and the boundary.
2. **Lean derives less than Lark in two places** (spec 2.11): a guard whose action noun is not written exactly,
   and a guard's verb that is an atom not headed by the guard's own reference. Python rejects both texts in the
   hand parser, so outcomes agree, but the witness count against Lark alone is zero against one. The harness
   must compare Python's outcome there, not Lark's count. If the DRI prefers one derivation with a rejected
   meaning, the noun and the verb head need the written text of a reference in `TermVal`, which this draft
   avoids. **In a third place the outcome class differs**: when an integer term deeper than 64 stands before a
   malformed part of the clause's integer slots, Python reports `ResourceLimit` and Lean no reading, because
   Lean's depth rejection belongs to a derivation and the text has none. Both refuse. The harness lists the
   class, and `DELTA.md` lists it as `order` (spec or38, Q11). The alternative is a rule that derives a
   malformed integer term only to reject it.
3. **`EnglishParser` cannot be deleted in E2.** `norm_english.py` and `norm_defaults_english.py` construct it
   and run the Lark audit themselves. Until E3 moves those layers, Python still decides the embedded formulas
   of norm blocks. E2 removes it from `english.admission` only. This is weaker than LEAN-FIRST's "deleted in the
   same batch" and is what the pointer plan's wording allows.
4. **The lexicon is still proposed by Python.** After E2 Lean validates the selection (V1 to V6) and refuses a
   bad one as `invalidGrammar`; it does not compute the selection. The policy that chooses among honest
   wordings (`EnglishVocabulary`, about 300 lines) stays a Python producer, untrusted but necessary. Whether
   Lean should compute the default selection, so that the relay carries no policy, is not decided here.
   Recommendation: not in this stage; the senses layer is the first Lean-side producer and will show the shape.
5. **V6 is specified by its checks, not yet by its tables.** Spec 2.9 states V6 in three parts: the code set
   with the rescue, the idiom branch, and the reserved risk wordings. The rescue that lets a wording through
   when it matches a fixed complement or verb pattern is about 70 lines of `english.py` with two regex tables,
   and the idiom branch is about 30 more: an idiom licenses syntax only, and Python still checks its anchor in
   the predicate's name or description, its collisions with the shared-family rule, the passive `by`, and
   negated heads. E2.1 ports all of it as data, and the statement review of that port is bounded to it. Until
   V6 is in `Lexicon.valid`, the flip would leave these reader-protection checks in trusted Python; this plan
   does not allow the flip before E2.1. **The disposition of the codes is open for the DRI.** S2 spec 2.14
   proposed `TEMPLATE_LENGTH`, `BINARY_VERB` and `IDIOM_UNRELATED` as warnings. Each refuses a declared wording
   today, as does `ENGLISH_STRUCTURE_WORD`, so a warning would widen what is accepted. The review converged on
   keeping `IDIOM_UNRELATED`. Fable's round 3 extended the same argument to the other three; Astra's last
   round did not see that text. This draft keeps all four as refusals. Recommendation: keep them through GE2
   so that the corpus A/B shows no `verdict` change from V6, and let the DRI drop a style code afterwards as a
   signed `verdict` row.
6. **`rights@0` wordings.** The rights correlation installs fixed wordings on a derived environment
   (`ve/rights.py:542`). Lean does not compute them in this stage, so a lexicon that selects one fails V2.
   Recommendation: formula-level English of a rights environment stays with the rights layer's own step in E3,
   and GE2's `DELTA.md` lists any corpus text this makes `availability`. If the corpus A/B shows such texts on
   the admission path, the flip waits for the rights forms.
7. **The conclusion check is split.** Lean computes which sentences are obligations and their premises; the
   existing entailment operation proves each. A document is admitted when every obligation is found. The
   English theorems say nothing about the proof search (claim C4 stays). Whether `admit` should call the
   entailment checker inside Lean is left to the lean-first batch that owns entailment.
8. **Performance at pilot size is unmeasured.** The fixture sentences cost at most 0.69% of the work budget,
   but they are short. The BlueDot document, the 266-token sentence of S0 and grammar instantiation for a
   256-predicate environment are measured only at GE2, on the service. LEAN-FIRST names this the largest single
   risk. If a budget is missed, the flip waits; the reader's correctness does not depend on it.
9. **`grammar_extension` for profiles is stated, not proved.** The S2 proof uses the identity on nonterminals.
   With per-value-sort nonterminals the map renames them, and the row-containment lemma must carry the
   renaming. The fallback is S2's domain. The senses layer needs growth of a lexicon under a fixed profile
   list, which is the case the statement covers.
10. **Ordered commitment.** The hand parser commits to a guard on its prefix, and to an attribute on `the`
    with a relation's name; Lean reads all derivations. A text that the prefix matches and that only another
    rule derives would be accepted by Lean and rejected by Python. None is known. The reverse corpus looks for
    it (base plan 7.3).
11. **The advice table is advisory and wider than Python's.** Lean matches the rejected wordings anywhere in a
    sentence without a reading; Python matched them after a recognised subject. A sentence can therefore get
    advice it did not get before. It never changes a verdict. The texts are Python's, ported, and listed in
    `DELTA.md` as `wording`.
12. **One name can be read two ways under `data@0` and `risk@0`.** A constant spelled like a property, or a
    severity class spelled like an adjective, gives two derivations (spec 8.7). Both sides reject. V4 does not
    refuse such a lexicon, because a property is named by its identifier and not by a wording. Whether V4 should
    grow is for the statement review.
