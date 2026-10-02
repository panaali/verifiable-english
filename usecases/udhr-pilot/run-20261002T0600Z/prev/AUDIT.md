I couldn't write AUDIT.md because file writes are denied in this session, so the audit is printed here instead.

**Faithful: 18/20.**

**Sample:** all five units that aren't LABELLED: u074 (CHECKED) and u017, u052, u112, u114 (READINGS; the tool reports these as OPEN). Added to them are 15 LABELLED units drawn with Python `Random("20260929T1800Z").sample(sorted(LABELLED_ids), 15)`: u002, u012, u014, u021, u026, u028, u036, u050, u053, u072, u080, u083, u088, u095, u109. This is the same sampling method as earlier audits. The 90 UNFORMALISED units weren't in the statuses you asked for. The source SHA-256 and all 20 byte spans match `source/udhr.md`.

**Faithful:**
- **15 LABELLED units:** 14 headings plus "The General Assembly," labelled as a speaker marker; its attribution is recorded on u013a. None of them assumes a claim.
- **u074, Art. 20(2):** a prohibition with no conditions, covering every actor and every person. The default for other cases is never used, and the witnesses replayed. One nit: the English rendering "must not compel each person" can be misread as "not every person", but the VE itself is correct.
- **u017, Art. 1:** has a strict reading and a defeasible (exception-allowed) obligation reading, and replayed proofs show they differ where the exception applies. Caveat: "one another" exists only as text in the act phrase; the checked predicate takes one argument.
- **u114, Art. 30:** both readings (a ban on that interpretation, and "the Declaration implies no such right") are faithful. Every condition, though, is prose inside a sort or predicate description.

**Unfaithful:**
- **u052, Art. 14(2): strengthened, and a reading is missing.** The source bars invoking asylum only *in the case of* these prosecutions. Both readings apply to the person instead: "every prosecuted person must not invoke the right to seek asylum" and "anyone so prosecuted is not entitled to asylum". So someone prosecuted for an ordinary crime who is also politically persecuted loses asylum entirely.
  - The reading tied to the prosecution itself (the right doesn't cover such prosecutions) is absent, even though the unit's `unresolved_features` lists exception scope.
  - The act phrase drops "and to enjoy".
  - The two readings share no predicate, so nothing checked separates them; only their wording differs.
- **u112, Art. 29(3): the `scope_limited` reading strengthens the source.** It has no argument for the individual exercise of a right. So `exercises_contrary_to_un(p,r) → ¬right_protects_exercise(p,r)` removes protection from every one of p's exercises of r after a single contrary exercise. The norm reading, which ranges over contrary exercises, is faithful.

**Across units:** older open terms (`genuine`, `spirit_of_brotherhood`) name deciders the source never names (`human_rights_interpreter`, `applicable_court`). Newer terms correctly use `unstated`.

**Three highest-value missing features:**
1. **Rights and entitlements** (who holds the right, what it covers, who owes the duty): 78 units, 8,150 bytes (74.7% of the text), are blocked on norms.
2. **Conditional norms tied to a specific act or case:** give the exercise, prosecution or invocation its own argument, with checked conditions and an unspecified default for other cases. Conditions would then stop living in prose sort descriptions, which is exactly where u052 and u112 go wrong.
3. **Norm readings inside the main document's reading sets:** all readings would share one vocabulary, their differences would be checked, and the premise verdict could move past UNKNOWN. Today the main document's "distinguishing models" are empty placeholders.

This was read-only with no model calls. I added a one-line note of the result to my memory file for this pilot.
