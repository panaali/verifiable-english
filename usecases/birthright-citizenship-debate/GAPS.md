# Gaps

Ranked by (frequency across the 9 identified claims) × (importance to
resolving or even representing the debate). Unlike `us-constitution-14th-s1/GAPS.md`,
several of these gaps are not "v0 syntax is too narrow" but "no amount of
first-order relational syntax would help," which is itself a finding worth
recording precisely.

## 1. Evidential / empirical claims about the actual world — 3 claims (F3, F4, A3's consequence), very high importance

**Smallest example:** Krikorian: "200 million foreign students, tourists,
foreign workers... every year," roughly 10% of U.S. births involve a
non-citizen parent.

**Why v0 cannot express it faithfully.** v0 checks a formula against a
*stipulated* finite model that the submitter attests is complete
(`docs/spec/v0-language.md`, "closed-world evaluation applies only within the
complete submitted model"). It has no channel to real-world statistics: a
predicate like `high_noncitizen_birth_rate(@us)` would type-check but its
truth would depend on data no VE model can supply or verify, making it
exactly the OPAQUE-without-saying-so move the project brief prohibits. This
is not a missing connective; a hypothetical arithmetic/statistics profile
(`order@0` or beyond) would let you *state* "10% of births" as a ratio
constraint over a supplied model, but the model's numbers would still have to
come from outside VE, and verifying they match reality is permanently outside
scope (`docs/spec/v0-language.md` is explicit that checking types "does not
prove those descriptions correspond to real-world concepts").

**Proposed direction:** not a language extension but a process one — an
evidence/citation binding analogous to the `order@0` string-adapter design
(`docs/spec/v0.1-profiles.md`, section C): reify a cited statistic as a typed
fact with provenance (source, date, method), checked for internal consistency
with other stated facts, but never verified against the world by VE itself.

## 2. Values / normative premises — 2 claims (A3, and the "right vs. privilege" framing), very high importance

**Smallest example:** Newman: "you don't blame the child for the actions of
the parents. That's fundamentally American."

**Why v0 cannot express it faithfully.** This is a moral "ought," not a
recorded fact; v0 has only extensional truth in a structure. As in the
constitution use case, `must`/`believes`/`eventually` are already reserved
identifiers with no semantics — the project has flagged this need but not
built it. Unlike the deontic-prohibition gap in the constitution document
(which is about a legal rule's *validity*), this is about a debater's moral
premise, which is not even legal-institutional; it would need a distinct
"value/ought" operator, plausibly never checkable the way descriptive claims
are (there may be no admissible-structure semantics for it at all, only a
recorded-position one — see gap 5).

## 3. Analogical / precedential (non-deductive) reasoning — 2 claims (A2's Wong Kim Ark extension, F2's Harlan-dissent citation), high importance

**Smallest example:** "Wong Kim Ark ... affirmed citizenship for children of
non-citizens ... settled law for 127 years" used to license a conclusion
about a different (undocumented-parent) profile.

**Why v0 cannot express it faithfully.** `countermodel` could test this
*once translated into a candidate universal premise* (`test3`/`test4` in
`countermodel/`), and did real work there — but choosing which universal
statement the precedent should be translated into is exactly the interpretive
step VE cannot make. Legal reasoning by analogy from a precedent's *ratio
decidendi* to a new fact pattern is not deduction from a stated rule; it is a
judgment about which stated rule the precedent stands for. VE can check any
candidate rule once proposed (as this document does), but cannot generate or
validate the candidate itself.

**Proposed direction:** none within relational-fol@0; this looks structurally
similar to the "definitions" gap (constitution use case, gap 2) — the
analogy's correctness is precisely the missing "definition" of what the
precedent's rule actually is.

## 4. Legal-authority weighting (originalism vs. precedent, text vs. purpose) — 2 claims (F2 vs. A2/A4), high importance

**Smallest example:** Cooper's originalist appeal to 1868 intent vs. Mayes's
127-years-of-precedent appeal — both invoke history, reaching opposite
conclusions about what should govern today.

**Why v0 cannot express it faithfully.** This is a second-order question
(which source of legal authority controls, and how much) layered on top of
first-order claims about what any one source says. v0's `Entails` is defined
over one fixed vocabulary and one notion of truth in a structure; it has no
represented hierarchy of authoritative sources to weigh against each other.

## 5. Attribution and quotation ("X said/argued that...") — pervasive (every claim in this document), moderate-to-high importance for a debate document specifically

**Smallest example:** "Cooper cited Justice Harlan's dissents... as evidence"
— this document had to flatten every claim to an assertion, dropping who said
it, in what tone, and with what hedge ("Krikorian focused on...", "Mayes
countered that..."). For a *debate* use case this loses genre-defining
content: the graph records the *positions*, not the *speech acts*, and cannot
represent that A2 is Mayes *rebutting* F1 rather than an independent claim.

**Why v0 cannot express it faithfully.** No reported-speech or attribution
construct exists; `p(t)` cannot take a formula as its argument (v0 is
function-free and first-order, no embedding of formulas as terms), so
"Krikorian believes P" or "Mayes said P" cannot be stated without a
belief/quotation operator, listed among the brief's example gap categories.

**Proposed surface syntax (sketch, not designed here):** `@krikorian said_that (P)` / `@mayes believes (P)`, parallel to the deontic sketch in the constitution GAPS.md, needing a similarly separate semantic design (attitude/report relation over agents and propositions) and its own soundness work before adoption.

## Summary

| Gap | Claims affected | Importance | Fixable by more v0/v0.1 expressiveness? |
|---|---:|---|---|
| 1. Evidential/empirical claims | 3 | Very high | No — needs an evidence-provenance process, not new syntax |
| 2. Values/normative premises | 2 | Very high | Partially — needs a new operator, and may lack admissible-structure semantics at all |
| 3. Analogical/precedential reasoning | 2 | High | No — the translation step itself is the missing piece |
| 4. Legal-authority weighting | 2 | High | No — a different kind of reasoning than `Entails` |
| 5. Attribution/quotation | pervasive | Moderate–high (genre-defining for debate) | Yes, in principle — needs a reported-speech construct, listed in the brief's own gap examples |

The debate document surfaced a different lesson than the constitution
document: most of its gaps are not "v0's grammar needs one more connective"
but "first-order relational consequence is the wrong tool for this kind of
claim," and it is worth recording that distinction precisely rather than
treating every gap as a future syntax feature.
