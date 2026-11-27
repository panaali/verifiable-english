# Texts the tour uses

Every text the tour answers from, where it is, and how it was checked. "Written for the tour" texts are short rules
in VE's English: VE reads the sentences themselves, so there is no separate translation of an outside source. Every
text but the last stop's was read by an independent reader (an AI model given the text, a short brief and the files
that turn it into VE's rules, and asked to flag every place where they differ) before its outputs were recorded on
the page; the reader was from the same model family as the translators.

| stop(s) | text | where | branch | kind | independent reader (26 Nov 2026) |
|---|---|---|---|---|---|
| 1, 2, 3, 8 | A club's voting rules (4 sentences: active members are eligible; junior members are supervised; Ann is active; Bo is junior) | `tour/texts/club.ve.md` (built by `tour/texts/build_texts.py`) | main | written for the tour | no flag |
| 4 | A library's two loan rules (late after the last day of 21 days; on time on or before it) | `tour/stops/dates.py` | after-release (date arithmetic) | written for the tour | no flag |
| 5 | A pizza shop's bill rule (the bill = the sum of the charged pizzas) and its 30-minute promise | `tour/stops/sums.py` | after-release (sums) | written for the tour | one flag (the script had turned the promise into "every pizza within 30 minutes is charged"); fixed (the order now states each pizza's charge) and clear on the re-read |
| 6 | The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), one made-up applicant (`demo/b15.json`) | `usecases/eligibility/` | main | translation of a real law | two open points on parts the tour's applicant does not reach (a late claim's exception; opting out of the income charge); none on the applicant |
| 7, 9 | GitLab handbook "Relocation / Address Change" (CC BY-SA 4.0), case R009 (Ivo, 184 days in Spain in 2028); stop 9 plants one mistake in a copy of its translation (a stay's days counted without its last day) | `usecases/gitlab_relocation/` | after-release (ask on policies) | translation of a real company policy | as written: one open point on planned stays (not in Ivo's case), the other flags judged false alarms; none on case R009. Planted copy: the planted part flagged with high confidence (`tour/data/reader-planted.json`) |
| longer example | Universal Declaration of Human Rights, articles 23(4) to 26 ("Everyone has the right to form and to join trade unions ...") | `usecases/question-answering/udhr-part07.ve.md` | main | translation of a real text | one flag, judged a false alarm |
| last stop | Two members' rules written in plain lines with no word list declared (`own-rules.txt`: Ann is paid and not suspended, so allowed; `own-rules-new-word.txt`: uses "overlimit", a word not in VE's word list) | `tour/texts/own-rules.txt`, `tour/texts/own-rules-new-word.txt` | main | written for the tour | not run: there is no translation to compare (the lines are the rules); the words VE read are shown in the output |

The answers written from the GitLab policy alone, before its translation ran, for Ivo's case are in
`tour/data/relocation-R009-sealed.jsonl` (stop 9).
