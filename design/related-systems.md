# Related systems: Canonical English and Attempto Controlled English

Read 2026-09-21. **The CE repository (`MichaelCurrie/canonical-english`) returned 404, so no code, tests or
history were inspected; CE claims come from canonical-english.org only.** ACE: APE clone, ACE 6.7 rule pages,
Kuhn 2013 and Fuchs 2018 PDFs.

## 1. Comparison

| | Canonical English (CE) 1.0.0 | ACE 6.7 / APE | VE v0 |
|---|---|---|---|
| Semantics | None of its own. Guarantees one parse, one sense, one referent per document. The site says noah-parser emits a DRS, but defines no model theory, entailment or proof rule | DRS, mapped to FOL (`drs_to_fol_to_prenex.pl`), TPTP, OWL/SWRL, RuleML. Reasoner RACE is separate | Many-sorted function-free FOL with equality; finite-model evaluation, countermodels, checked deductions |
| Ambiguity | Rejects ambiguous text by linter verdict; "not defined constructively"; the ideal language is admittedly unobservable | Constructive grammar plus interpretation rules choose one reading: quantifier scope follows surface order, PPs attach to the verb, pronouns take the most recent accessible agreeing NP | Fully bracketed grammar, explicit binders, no pronouns; uniqueness to be proved |
| Lexical grounding | Every content word bound to an Open English WordNet synset IRI, function words to Wikidata lexemes, proper nouns to Wikidata entities, in JSON-LD frontmatter | About 100k-entry lexicon with word class and morphology only; no sense grounding | Free-text description per symbol, hashed into the environment identity |
| Verification story | Conformance only: is this CE? | Parse, paraphrase, consistency and entailment via RACE | Evaluate, refute by countermodel, certify deductions, preserve assumptions |
| Implementation | Rust linter "under development". 11 executable rules, all encoding, spacing, frontmatter and lexicon membership. Grammar, anaphora and figurative-language rules are "not machine-checked yet". Body must be one plain paragraph. 139 forms, 129 senses, 52 tests. Project began 2026-08-09. The prefix checker for constrained decoding does not exist | SWI-Prolog, developed 1995–2013, last commit 2024-04; about 5k lines of regression tests; mature and dormant | Python 3.14, experimental, tested; Lean proofs pending |
| Licence | CC0 (data), MIT-0 (code) | LGPL-3.0 | none declared yet |

## 2. Ideas worth taking

**2.1 Sense-bound vocabulary (2–3 h).** Optional `senses` (OEWN or Wikidata IRI) on each symbol, hashed into the
environment identity. On a vocabulary merge, same name with different IRIs is an error; different names with the
same IRI are flagged as synonyms. The merged-vocabulary attack in E5 then needs a forged IRI as well. It does not
show that a description matches the world.

**2.2 `.ve.md` format (2 h).** Markdown with JSON frontmatter (valid YAML, so renderers skip it) holding the
environment identifier, vocabulary and renderer version; fenced `ve` blocks carry strict text; prose between them
has no meaning. Reject any frontmatter/body mismatch, as CE-0003 and CE-0009 do.

**2.3 Gatekeeper loop (3 h; constrained decoding 1–2 days).** The model proposes VE, the parser rejects with a
located diagnostic and a stable code (as CE's `CE-0003`), the model repairs, up to k rounds. Report accept rate per
round in E0. VE has a small context-free grammar and a closed vocabulary, so a GBNF grammar for llama.cpp or vLLM
can be generated per environment. CE cannot do this yet: its language is a verdict, not a grammar. The loop
guarantees form, not faithfulness, so it needs 2.5.

**2.4 ACE verbalisation for the natural view (4–6 h).** The view now prints "x1 stands in relation owns to x0".
Add a hashed `template` per predicate ("{0} owns {1}"). Rules: surface order equals scope order; guards become
relative clauses; no pronouns (Fuchs 2018); name a variable only if reused; no passive, so argument order stays
visible; keep brackets where `and` and `or` mix.

| FOL | Recommended sentence |
|---|---|
| ∀s (dep(s) → rev(s)) | Every service that is deployed is reviewed. |
| ∀s (dep(s) → ∃p owns(p,s)) | For every service S that is deployed, there is a person who owns S. |
| ∃p ∀s (dep(s) → owns(p,s)) | There is a person P such that P owns every service that is deployed. |
| ¬∃s (dep(s) ∧ ¬rev(s)) | It is false that there is a service that is deployed and that is not reviewed. |
| ∀s (dep(s) → ¬rev(s)) | No service that is deployed is reviewed. |
| ¬∀s (dep(s) → rev(s)) | It is false that every service that is deployed is reviewed. |
| ∀s ((dep(s) ∧ ¬ s=@legacy) → rev(s)) | Every service that is deployed and that is not @legacy is reviewed. |
| ∀p ∀s (owns(p,s) → audits(p,s)) | For every person P and every service S, if P owns S then P audits S. |
| ∀p ∀s (owns(p,s) → audits(s,p)) | For every person P and every service S, if P owns S then S audits P. |
| ∀s ∀p ∀q ((owns(p,s) ∧ owns(q,s)) → p=q) | For every service S, every person P and every person Q, if P owns S and Q owns S then P is Q. |

ACE itself would allow "Every deployed service is owned by a person" for row 2, the scope-ambiguous English
reading that E1 attacks. Prefer the global forms "for every" and "there is ... such that".

**2.5 Paraphrase-back (1 h after 2.4).** APE returns a Core ACE paraphrase (`drs_to_coreace.pl`) so authors see
what was understood. VE: show input, canonical text and natural view, all generated from the AST, never by the
model. In E1 this is the deterministic counterpart to the attacker's explanation.

**2.6 Interpretation tests (cite only).** E1b is Kuhn's ontograph method: does this statement hold in this small
model?

## 3. Where VE goes further, and where it is behind

Further: model theory with finite evaluation and bindings; countermodel search; checked deductions that preserve
assumptions; identity hashes binding vocabulary to a confirmation; an adversarial framing. CE has no semantics. ACE
has semantics but no sign-off binding or certificates, and Fuchs concedes its English surface can mislead.

Behind: VE text is bracketed logic with English keywords, far less readable than ACE. ACE covers plurals, numbers,
n-ary verbs, modality, anaphora and questions, with a morphological lexicon. ACE has human evidence (64
participants, 91.4% against 86.3% for a Manchester-style syntax, less learning time); VE has none. VE lacks sense
grounding (CE's one real contribution), a document format, an authoring loop and a paraphraser.

## 4. Citations

Verified through Crossref or the primary source:

- Fuchs, Kaljurand, Kuhn (2008). Attempto Controlled English for Knowledge Representation. *Reasoning Web*, LNCS,
  104–124. https://doi.org/10.1007/978-3-540-85658-0_3
- Kuhn (2013). The understandability of OWL statements in controlled English. *Semantic Web* 4(1), 101–115.
  https://doi.org/10.3233/SW-2012-0063
- Kuhn (2014). A survey and classification of controlled natural languages. *Computational Linguistics* 40(1),
  121–170. https://doi.org/10.1162/COLI_a_00168 (the CE site's DOI for it, 10.1613/jair.3908, is an unrelated paper)
- Fuchs (2018). Understanding Texts in Attempto Controlled English. *Controlled Natural Language (CNL 2018)*, IOS
  Press. https://doi.org/10.3233/978-1-61499-904-1-75
- Fuchs (2012). First-Order Reasoning for Attempto Controlled English. *CNL 2010*, LNCS, 73–94.
  https://doi.org/10.1007/978-3-642-31175-8_5
- Geng, Josifoski, Peyrard, West (2023). Grammar-Constrained Decoding for Structured NLP Tasks without Finetuning.
  *EMNLP 2023*, 10932–10952. https://doi.org/10.18653/v1/2023.emnlp-main.674
- Kaljurand, Fuchs, Kuhn. APE 6.7 (2013), LGPL-3.0. https://github.com/Attempto/APE ; rules at
  http://attempto.ifi.uzh.ch/site/docs/ace_interpretationrules.html
- Currie (2026). Canonical English 1.0.0. https://canonical-english.org/ (website only; no paper or public
  repository found)

Not verified: LNCS volume numbers; the ACE DRS technical report (Fuchs, Kaljurand, Kuhn 2010).
