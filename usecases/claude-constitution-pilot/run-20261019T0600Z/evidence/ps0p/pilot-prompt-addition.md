# PS-0p: pilot-prompt addition (draft for the DRI's merged prompt, SC2)

> From [presupposition-phase1.md](../../presupposition-phase1.md) section 4. Constitution only: the UDHR has no
> heading presuppositions (U5), so it gets no addition. Four of class A's five claims are **held**: VE English has no
> admitted wording for their relational nouns today (F1–F3, section 2.5). u0286 goes to the audit. Text to merge
> follows the rule line.

---

**Pilot addition** (`pilot-additions.txt`):

[presupposition plan, PS-0p: heading presuppositions and trigger tags] A heading that carries a presupposition is one
whose words take something for granted: a possessive ("Claude’s core values"), a definite ("the mission of
Anthropic"), a factive with an object ("Acknowledging open problems"), or a wh-word ("What constitutes …"). A heading
without such a word is a title (scope's rule): it records **no** `presupposed_claim`.
1. Remove `presupposed_claim` from u0040, u0075, u0151, u0162, u0174, u0195, u0207, u0212, u0257, u0260 (`.presupposition`)
   and note "no trigger word: a title (scope SC-3a)". Status unchanged. u0055 ("How to treat operators and users")
   has a wh-word: keep it UNFORMALISED, replace its claim with the note "wh-title: its presupposition is that there is
   a way to treat them; the recorded claim was not it", and list it for the audit.
2. u0254 and u0268: replace `presupposed_claim` with the note "the text withholds this (u0269.s02): not assumed".
   Status unchanged.
3. Declare the sort `entity`'s English noun as `{"singular": "thing", "plural": "things"}`, not the reserved
   "entity" (which falls back to `entity of sort "entity"`).
   - u0013, u0095, u0002, u0235: do **not** claim them. Keep them UNFORMALISED with the note "relational-noun wording
     not admitted in VE English (PS-0p phase 1): 'is a … of' wordings are refused". Do not use the quoted fallback
     wording ("has the recorded relation …") to claim them.
   - u0286: declare `open_problem(entity)` worded "{0} is unsolved", and offer the unit as an assumption with the
     fence "Some thing is unsolved." (`carrier: assumed`, `trigger: factive`, `trigger_words: Acknowledging`). It is
     claimed only if the audit accepts it.
4. Every unit: add `presupposition_triggers`, one entry per trigger (`words`, `class`: definite, possessive, plural,
   factive, change-of-state, iterative or wh-title; `pre` in English; `carrier`: proved, assumed, conditioned,
   asserted, unresolved, or `none` for a title). When a carrier is unresolved, add `presupposition` to
   `other_blockers`.
5. For each formalised rule whose act contains "the user", "the operator", or a role or pronoun possessive ("its
   content", "the operator’s instructions"), record in `presupposition-goals.json`: the unit, the words, the rule's
   name, guard and carve-outs. (PS-3 reads the count of distinct goals and of rules with identical applicability.)
6. If you add any predicate, constant or wording to the vocabulary: run the separating-situation step (`nd.py all`)
   afterwards, and check that every existing fenced English unit still parses unchanged (adding "{0} is a … of {1}"
   wordings turned "Claude is not human." into a refusal in phase 1).

**Audit addition** (`pilot-audit-additions.txt`):

[presupposition plan, PS-0p] For each heading presupposition the run claims: the trigger word is in the title; the
content is exactly the existence (for a singular description, existence and uniqueness) of what the trigger names,
and nothing more (no "is desired", "is relevant", "must"); and the source does not withhold it elsewhere (search for
"whether" or "uncertain" with the noun). Check u0055's note. Of class A, only u0286 may be claimed in this run:
accept it only if "Some thing is unsolved." is exactly the existence of what "open problems" names; otherwise it
reverts to UNFORMALISED. u0013, u0095, u0002 and u0235 should not be claimed.
