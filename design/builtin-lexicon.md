# Plan: a built-in content-word lexicon (ACE-style)

Status: PLAN, for review by GPT-6 Astra (xhigh) and Claude Fable 5.1 (xhigh) before any build. Follows
`open-vocabulary-english.md` (whose reviewers cut phrase inference because phrase boundaries were ambiguous).

## Why

VE's English surface has fixed function words (every, some, who, that, is, is not, and, or, both, either, if, then)
and NO general content-word lexicon: every noun, adjective and verb must be declared per use case. ACE separates the
two: a fixed function-word grammar plus a large lexicon giving each content word its class and morphology only
(no meaning). Knowing the class of every word is what makes ACE's phrase boundaries deterministic. Canonical English
has a small lexicon with each word bound to a WordNet sense. The project lead wants sentences of ordinary English to
parse without hand-written files.

## Proposal

1. Lexicon data: a versioned JSON file shipped with VE, built by a reproducible script from Open English WordNet
   (CC-BY licence) filtered to common words: countable nouns (singular, plural), adjectives, transitive verbs
   (base, third-person singular, past participle for passives if ever supported), intransitive verbs. Frequency cutoff
   about 5,000 lemmas per class from a public frequency list. Proper nouns are NOT in the lexicon. Hash of the lexicon
   goes into the environment identity of any environment derived from it.
2. Mapping to VE: a noun used after every/some/no becomes a sort; "is a|an <noun>" a unary predicate; adjective after
   "is" a unary predicate; a transitive verb between two references a binary predicate; the same noun used as sort and as
   predicate is an error that names both uses. Sorts: single universal sort `thing` plus subsort-free declaration per
   binder noun (v0: one sort per binder noun, as today).
3. Parsing: the existing deterministic English parser gets a lexicon-backed token classifier. Phrase boundaries are
   decided by word class, never by guessing: an unknown word is a hard error naming it and suggesting `ve propose`
   or a declaration. Multi-word content terms come only from declarations (as today) or from a small closed idiom
   list; the lexicon has single words only.
4. Output: the derived environment (every symbol with its lexicon entry and class) is printed with the result and can
   be frozen to files with the existing adopt machinery, marked `lexicon-derived`, review status unreviewed.
5. Optional sense binding: a use case may pin `word -> WordNet sense id`; pinned senses are hashed into the identity.
6. Audit: the all-derivations audit is run with the lexicon's classes as terminals (finite); the strict surface, the
   identities, the checker, Lean and Rust are untouched.

## Questions for reviewers

- Does word-class knowledge remove the ambiguities found last time ("likes New York", "born in the United States",
  "a member of Acme", "research and development manager", "is owned by Alice")? Which remain, and what is the rule?
- Homographs (a word that is both noun and verb: "vote", "state"): resolve by position, or reject?
- Is a 5,000-lemma-per-class lexicon the right size for unambiguity audits and for a Lean proof later?
- Is deriving the environment from the words used compatible with meaning identities (same sentence, same lexicon
  version -> same environment_id)? What must be hashed?
- Licence and reproducibility of the lexicon build.
- Smallest version worth building first.
