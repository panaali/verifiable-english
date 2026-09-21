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

## After review (2026-09-21): both reviewers said BUILD WITH CHANGES

Reviews: `~/code/manage-agents/reviews/openvocab-review-astra.md`, `openvocab-review-fable.md`. Common ground, adopted:

- The slot grammar above is NOT unambiguous ("likes New York", "born in the United States", "a member of Acme",
  "research and development manager", "does not own", "is owned by", "believes that state ..."). Capitalisation must
  never carry meaning. Inferring binary predicates, constants, sorts, plurals, passives and morphology is CUT.
- An `introduced` list is not a safeguard: in open mode every typo parses, and a pipeline will not read the list.
- The plan was wrong about the code: `--env` is required; there is no `ve env` command; no `some`/`no` forms;
  descriptions are mandatory and hashed; extending an environment changes `environment_id` and so unbinds the
  overlay's pinned review; the ambiguity audit relies on a finite lexicon.

Version 1 (the only thing approved to build):
1. Closed-mode errors name the unknown phrase with its span and suggest the nearest declared wordings.
2. `ve propose --env E [--english-vocabulary O] TEXT`: uses today's grammar; the ONLY new thing it may infer is a
   unary predicate from `<ref> is a|an <phrase>` / `<ref> is <phrase>` / `<ref> is not ...`, where a phrase is a maximal
   run of tokens containing no boundary token (is, does, not, and, or, if, then, that, who, which, comma, period,
   both, either, every, some, for); anything else is rejected as today. The argument sort comes from the binder noun
   of the reference. Output: a PREVIEW with each proposed symbol, its source span, its signature, the nearest existing
   symbols (edit distance and shared stem), a generated description that says it is machine-proposed, and the
   deterministic paraphrase; plus candidate environment and overlay files written to an output directory, overlay
   entries `suggested: true`, status unreviewed.
3. A near-duplicate of an existing symbol (small edit distance or same stem) is a hard error unless acknowledged with
   an explicit flag naming the symbol.
4. Proposed environments cannot feed `check --prove`, `countermodel` or certificates until adopted: adoption is an
   explicit command that writes the files and prints the new `environment_id`; nothing is adopted implicitly.
5. The all-derivations audit is extended only to the finite lexicon obtained AFTER adoption (the open step is a
   proposal generator, not a parser whose unambiguity we claim).
