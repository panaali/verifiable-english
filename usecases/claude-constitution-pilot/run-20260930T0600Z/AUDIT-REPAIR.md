# Audit repair

Input: the audit of run `20260929T1800Z` (`AUDIT-20260929T1800Z-received.md`): 18 of 20 sampled units faithful, two
rejected. This run repaired both, then repaired the seven other units that have the same defect, before looking at
what the newly merged features could add (nothing, see `FEATURE-REVIEW.md`).

## The two rejected units

### `u0156.s03` — "Claude shouldn't actively deceive the user about the existence of a system prompt or its content." (bytes [95093, 95193))

**Finding.** The defeasible reading is supposed to lift the prohibition in excepted cases. The rule was a *permission*
predicate (`system_prompt_deception_permitted`, sign negative) with completion `deny`, so an excepted case still came
out "not permitted": the defeasible reading was the strict one, and the unit forbade something where the source says
nothing. The one model stored as telling the readings apart was empty and shared by all 14 reading sets.

**Repair.**

| | 18:00Z | this run |
|---|---|---|
| predicate | `system_prompt_deception_permitted(claude_instance, user)`, permission, deny | `system_prompt_deception_avoidance_required(claude_instance, user)`, obligation, deny |
| rule | sign negative ("must not") | sign positive: "must avoid actively deceiving each user about a system prompt's existence-or-content" |
| excepted case (defeasible reading) | "not permitted" (not in the source) | "not required to avoid" — what a lifted duty means, and the wording the audit accepted for the six duties |
| status | READINGS | READINGS (not re-audited) |

### `u0165.s03` — "* Create cyberweapons or malicious code that could cause significant damage if deployed." (bytes [101609, 101698))

**Finding.** Same collapse of the defeasible reading into the strict one. Also: the act phrase and both English
readings dropped "if deployed", and "cyberweapons-or-malicious-code that could…" let the damage clause cover cyberweapons,
which the open term deliberately leaves undecided.

**Repair.** Same duty framing, plus a different place for the words. The rule is now guarded by the base atom
`damaging_cyberweapon_or_malicious_code(situation)`, declared as "the situation is a case of Claude creating cyberweapons
or malicious code that could cause significant damage if deployed" (the source’s words, unabbreviated, attachment not
decided), and that name is the open term whose factors already listed "whether ‘that could cause significant damage if
deployed’ qualifies cyberweapons as well as malicious code". The act phrase ("avoid the creation in {1}") is only a
pointer: no qualifier is attached to any noun. The rendered readings print the atom’s words on a "Classifications named
above" line, because the renderer prints only the atom’s name.

## The same defect, repaired together (found by reviewing the class, not sampled by the audit)

`u0165.s01, s02, s04, s05, s06, s07` (the other six hard constraints) and `u0125.s04.p2` ("Claude should never directly
deny that it is Claude") had the same permission-with-deny-completion shape, so their defeasible readings collapsed the
same way. All are now duties to avoid the act. For the six hard constraints the act was also abbreviated ("engage-or-aid",
"existence-or-content"-style hyphen joins); their act phrases are now short pointers and the source’s words sit in the
guard atoms, as for `u0165.s03`. Their status stays READINGS; none is re-audited, so none is audit-verified.

## What is verified now, and what is not

* Every regulated predicate is now an obligation of an instance of Claude with completion `deny` = "not required"; no
  permission predicate and no `default: allow` remains (`metrics.json`, `no_invented_permissions`; asserted in
  `finish.py`).
* All three documents pass `ve document check` (main; strict companion; default companion). Both English readings of
  all nine repaired rules parse back to the same rule (`readings/english.json`).
* **Separation of the readings, now shown for every reading set** (`readings/separating-situations.json`): a
  one-element situation with every guard atom true and every carve-out false; the strict reading requires the act, and
  the defeasible reading with its exception applying does not. This is computed with VE’s own elaboration and evaluator
  in `finish.py`. VE itself still cannot check it: a candidate norm carries no content, so the model stored inside each
  reading set is a placeholder, and its `admission.why` says so.
* **Limits that remain.** The language has no "unspecified" outcome, so "not required" is still a completion the source
  never states (the audit’s first missing feature). The two companion documents, not the main document, are where the
  readings are elaborated (the second missing feature; rights@0 has the mechanism only for its own candidate kind and
  cannot pair a strict with a defeasible candidate, `FEATURE-REVIEW.md`).

## Minor issues from the audit

* Bare "### " markers of `u0040.heading` and `u0083.heading` (and `u0027`, `u0032`, `u0207`) carried the parent’s
  open-term tag in the ledger; the tag now lives only on the title/presupposition unit. Ledger only; no status change.
* `u0168.s01`: "these lines" is resolved in the atom’s own wording ("the lines drawn by the hard constraints"), as well as
  in the ledger note.
* The English of `u0073.s05` still does not parse back (nested "all of the following" list); unchanged and disclosed.
