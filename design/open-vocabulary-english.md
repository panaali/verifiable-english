# Plan: open-vocabulary English (write a sentence, no files)

Status: PLAN, not started. Must be reviewed by GPT-6 Astra (xhigh) and Claude Fable 5.1 (xhigh) before any build.

## Problem

The project lead typed `Every person who is born in the United States ... is a UK citizen.` and got a syntax error,
because `uk_citizen` is not declared in `environment.json` and has no wording in `environment.english.json`. The lead
expected VE to accept a subset of regular English directly, without editing files. Today the English surface is a
closed-vocabulary surface: grammar is fixed AND every content phrase must be pre-declared with a reviewed wording.

How the two reference systems handle this (from `design/related-systems.md`):
- Canonical English is stricter than VE, not looser: every content word must be bound to a WordNet synset in JSON-LD
  frontmatter; it has no semantics and its linter checks lexicon membership.
- Attempto Controlled English is the one that works as the lead hoped: a fixed grammar of function words, a large
  built-in lexicon with word class and morphology only, and unknown content words accepted by word-class prefix
  (`n:`, `v:`, `a:`) or by guessing. Content words are uninterpreted symbols; only the function words carry logic.

## Proposal

Add an OPEN vocabulary mode to the English surface. Function words and clause shapes stay fixed and unambiguous;
content phrases in fixed slots become symbols, and the environment is INFERRED from the text.

    echo 'Every person who is born in the US is a UK citizen.' | ve parse --open -

1. Slots. `every/some/no <NOUN>` introduces a sort; `<ref> is a|an <NOUN PHRASE>` and `<ref> is <ADJ PHRASE>` a unary
   predicate; `<ref> <VERB PHRASE> <ref>` a binary predicate; capitalised or quoted phrases in reference position are
   constants. Phrase boundaries come from the fixed function words and punctuation, never from a statistical parser.
2. Normalisation is deterministic and minimal: lower-case, collapse spaces, strip the article, third-person `-s` and
   the copula; NO synonym merging, NO lemmatiser beyond a tiny fixed table. `uk citizen` and `british citizen` are
   different predicates on purpose.
3. Output always contains the inferred environment (sorts, predicates with arity and argument sorts, constants), the
   canonical strict text, the identities, and a list `introduced` of every symbol that did not exist before.
   A typo therefore shows up as a NEW predicate, not as a silent parse. With `--env E` given, open mode extends E and
   reports only the additions; with `--closed` (default when `--env` is given) behaviour is as today.
4. Sort inference: argument sorts come from the binder noun of each reference; a predicate used with conflicting
   sorts is an error that names both uses. No subsorting in v0.
5. Trust: the inferred environment is `unreviewed` by construction; identities are computed as today from the
   generated environment, so nothing in the trusted path changes. `ve env freeze` writes the two files for the user,
   so files still exist for anything that must be signed off, but nobody writes them by hand.
6. Better errors in closed mode: name the unknown phrase and suggest the nearest declared wordings.

## Risks to review

- Ambiguity returns through open slots: where does a verb phrase end and an object noun phrase begin
  ("x is born in the United States": unary `born in the united states`, or binary `born in` + constant)? Proposed
  rule: prepositions do not split; a binary reading requires the object to be a reference form (`that person`,
  `some state`, a quoted or capitalised constant declared by use). Is that rule unambiguous and unsurprising?
- Morphology: "person who owns" vs "persons own"; negation "does not own" -> needs verb base form. A fixed tiny rule
  set, or require the user to write the base form once?
- Passive and converse ("is owned by") create distinct predicates unless declared converses.
- Silent meaning drift: an LLM author in open mode can coin near-duplicate predicates; mitigation is the `introduced`
  list plus the existing `compare` oracle. Enough?
- Does this conflict with PLAN-V3's freeze on language work? It is surface-only, touches no checker, and is a direct
  request from the lead; cost is Codex quota only.
- Unambiguity evidence: extend the all-derivations audit to open mode; Lean proof still deferred.

## Build size

One Codex task (high), then cross-family review, then merge. No API spend.
