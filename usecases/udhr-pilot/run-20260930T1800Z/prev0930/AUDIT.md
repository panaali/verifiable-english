**Faithful: 14/20.** Read-only, no model calls. Writing `AUDIT.md` was denied in this session, so the audit is printed here only.

**Sample.** u074 (sole CHECKED) and u111 (sole OPEN), then one `Random("20260930T0600Z")`:
- `.sample(sorted(READINGS), 14)`: u022a, u022b, u022c, u032, u033a, u035, u039, u048, u049, u054, u066, u070, u073, u114.
- `.sample(sorted(LABELLED), 4)`: u023, u069, u104, u107.

Source hash and all spans match.

**Faithful (14):**
- The four headings, u074, u022a, u022b, u022c, u048, u066, u070, u073.
- u114, unchanged since the last audit.
- u111: necessary conditions only, decider unstated. It is inert, and its two purposes are never rendered.

**Unfaithful in meaning (3):**
- **u054, Art. 15(1): strengthened.** Every candidate binds every bearer toward every person: "every state must grant each person a nationality". The reading "each person has some nationality" is absent.
- **u039, Art. 10: weakened and unscoped.** The act phrases drop "in full equality" and "in the determination of his rights and obligations and of any criminal charge against him". The negative candidate also drops the tribunal, undisclosed.
- **u035, Art. 8: scope lost.** "for acts violating the fundamental rights granted him by the constitution or by law" survives only in a predicate description.

**Unfaithful in labels only (3):** polarity is offered as open where it is not; the candidates are separated only by predicate name.
- **u032, Art. 7:** "avoid denying equal protection" and "give equal protection" are one duty.
- **u033a, Art. 7:** "protection" fixes positive polarity; the negative candidate, "avoid exposing to discrimination", drops "equal protection".
- **u049, Art. 13(2):** the "positive" candidate, "allow to leave", repeats the negative duty; no securing reading exists.

The same duplicate sits in u035, u039 and u054; the rights spec itself narrows Art. 8 to positive. The three label defects are repairable in `table.py`.

**Across units (not counted):**
- No candidate combines lines, so "a liberty protected by a claim" cannot be chosen.
- Positive duties bind every state toward every person, with no jurisdiction relation (out of sample: u051, "must grant asylum").
- Newly verifiable bytes: 737 (708 substantive).

**Three highest-value missing features:**
1. **Strict and defeasible candidates in one reading set** (the force axis): 43 units, 4,175 bytes (38%), covering every "shall" unit and Articles 22–27.
2. **Structured right lines:** checked scope and trigger clauses in place of 80-byte act phrases, plus a bearer–holder relation ("some state", "his country"). Repairs u035, u039, u054; unblocks u076, u108.
3. **Per-choice rights elaboration:** limitations, the Art. 30 bar, "this right includes" lines and norm readings attached to reading-set candidates. Activates Art. 29(2), unblocks u067, u068, u071a, u071b, and moves premises off UNKNOWN.
