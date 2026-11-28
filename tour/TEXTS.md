# Texts the tour uses

Every text the tour answers from, where it is, and how it was checked. "Written for the tour" texts are short rules
in VE's English: VE reads the sentences themselves, so there is no separate translation of an outside source. Every
text but stop 12's was read by a separate reader from the same model family as the translators (an AI model given
the text, a short brief and the files that turn it into VE's rules, and asked to flag every place where they differ)
before its outputs were recorded on the page. A check by a different AI family is due on Monday 30 November 2026 and
has not yet run. Each flag was then judged by one fresh AI session of that same model family (Claude Opus 5.5), one
session per flag; no person judged a flag, and no person has signed off any translation on this page.

| stop(s) | text | where | branch | kind | same-family reader (26 Nov 2026) |
|---|---|---|---|---|---|
| 1, 2, 3, 8 | A club's voting rules (4 sentences: active members are eligible; junior members are supervised; Ann is active; Bo is junior) | `tour/texts/club.ve.md` (built by `tour/texts/build_texts.py`) | main | written for the tour | no flag |
| 4 | A library's two loan rules (late after the last day of 21 days; on time on or before it) | `tour/stops/dates.py` | after-release (date arithmetic) | written for the tour | no flag |
| 5 | A pizza shop's bill rule (the bill = the sum of the charged pizzas) and its 30-minute promise | `tour/stops/sums.py` | after-release (sums) | written for the tour | one flag (the script had turned the promise into "every pizza within 30 minutes is charged"); fixed (the order now states each pizza's charge) and clear on the re-read |
| 6 | The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), one made-up applicant (`demo/b15.json`) | `usecases/eligibility/` | main | translation of a real law | two open points on parts the tour's applicant does not reach (a late claim's exception, regulation 4(6)(b); opting out of the income charge), each judged a real departure by a same-family session; none on the applicant; a third flag judged a false alarm by a same-family session |
| 7, 9 | GitLab handbook "Relocation / Address Change" (CC BY-SA 4.0), case R009 (Ivo, 184 days in Spain in 2028); stop 9 plants one mistake in a copy of its translation (a stay's days counted without its last day) | `usecases/gitlab_relocation/` | after-release (ask on policies) | translation of a real company policy | as written: one open point on planned stays (part 15; not in Ivo's case), the other flags of the 26 Nov reader run judged false alarms by same-family sessions (the five 27 Nov runs also raised flags on parts 4, 11, 13, 23 and 34 and a new point on part 6, not yet judged); none on case R009. Two more open points were found after the tour's outputs were recorded (mail delivered to the new place; a stay that runs past 31 December). All three are fixed on branch after-release after the commit the tour runs (`tour/AFTER_RELEASE_COMMIT`), and none changes case R009's answers. This translation once gave a real wrong answer (question R035-2: "yes" although the written pre-approval was missing), fixed in the commit the tour runs; that fix is not yet audited. Planted copy (27 Nov 2026): five reader runs on it and five on the translation as written, with one prompt (`tour/data/reader-runs.json`): the day-count problem raised in 5 of 5 planted runs and 0 of 5 as written; the planted rule named in 3 of 5 (2 at high confidence) |
| longer example | Universal Declaration of Human Rights, articles 23(4) to 26 ("Everyone has the right to form and to join trade unions ...") | `usecases/question-answering/udhr-part07.ve.md` | main | translation of a real text | one flag, judged a false alarm by a same-family session |
| 12 | A club's rules for its members, in plain lines with no word list declared (`own-rules.txt`: Ann is paid and not suspended, so allowed; `own-rules-new-word.txt`: uses "overlimit", a word not in VE's word list; `own-rules-new-word-fixed.txt`: the same with the `Words:` line VE offers) | `tour/texts/own-rules.txt`, `tour/texts/own-rules-new-word.txt`, `tour/texts/own-rules-new-word-fixed.txt` | main | written for the tour | not run: VE's Python reader derives the words from its word list and shows them in the output for you to check; Lean does not check that step |

The answers written from the GitLab policy alone, before its translation ran, for Ivo's case are in
`tour/data/relocation-R009-sealed.jsonl` (stop 9). They are two rows of a sealed set written on 25 November 2026 by
an AI of a different model family (an OpenAI model), after the translation was frozen; the seal's record (time and
SHA-256) is in the project's working records, not in this repository.
