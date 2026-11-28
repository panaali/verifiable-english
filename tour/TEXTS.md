# Texts the tour uses

Every text the tour answers from, where it is, and how it was checked. "Written for the tour" texts are short rules
in VE's English: VE reads the sentences themselves, so there is no separate translation of an outside source. Every
text but stop 12's was read by a separate reader from the same model family as the translators (an AI model given
the text, a short brief and the files that turn it into VE's rules, and asked to flag every place where they differ)
before its outputs were recorded on the page. A check by a different AI family is due on Monday 30 November 2026 and
has not yet run. Each flag was then judged by one fresh AI session of that same model family (Claude Opus 5.5), one
session per flag; no person judged a flag, and no person has signed off any translation on this page. Each flag that
was dismissed, and the session that dismissed it, is listed under "Who judged each dismissed flag" below.

| stop(s) | text | where | branch | kind | same-family reader (26 Nov 2026) |
|---|---|---|---|---|---|
| 1, 2, 3, 8 | A club's voting rules (4 sentences: active members are eligible; junior members are supervised; Ann is active; Bo is junior) | `tour/texts/club.ve.md` (built by `tour/texts/build_texts.py`) | main | written for the tour | no flag |
| 4 | A library's two loan rules (late after the last day of 21 days; on time on or before it) | `tour/stops/dates.py` | after-release (date arithmetic) | written for the tour | no flag |
| 5 | A pizza shop's bill rule (the bill = the sum of the charged pizzas) and its 30-minute promise | `tour/stops/sums.py` | after-release (sums) | written for the tour | one flag (the script had turned the promise into "every pizza within 30 minutes is charged"); fixed (the order now states each pizza's charge) and clear on the re-read |
| 6 | The Social Fund Winter Fuel Payment Regulations 2025 (SI 2025/969), one made-up applicant (`demo/b15.json`) | `usecases/eligibility/` | main | translation of a real law | two open points on parts the tour's applicant does not reach (a late claim's exception, regulation 4(6)(b); opting out of the income charge), each judged a real departure by a same-family session (the opting-out point was later closed as harmless: see below); none on the applicant; a third flag judged a false alarm by a same-family session |
| 7, 9 | GitLab handbook "Relocation / Address Change" (CC BY-SA 4.0), case R009 (Ivo, 184 days in Spain in 2028); stop 9 plants one mistake in a copy of its translation (a stay's days counted without its last day) | `usecases/gitlab_relocation/` | after-release (ask on policies) | translation of a real company policy | as written: one open point on planned stays (part 15; not in Ivo's case), the other five flags of the 26 Nov reader run dismissed by same-family sessions (four false alarms, and one real difference that changes no answer: see below; the five 27 Nov runs also raised flags on parts 4, 11, 13, 23 and 34 and a new point on part 6, not yet judged); none on case R009. Two more open points were found after the tour's outputs were recorded (mail delivered to the new place; a stay that runs past 31 December). All three are fixed on branch after-release after the commit the tour runs (`tour/AFTER_RELEASE_COMMIT`), and none changes case R009's answers. This translation once gave a real wrong answer (question R035-2: "yes" although the written pre-approval was missing), fixed in the commit the tour runs; that fix is not yet audited. Planted copy (27 Nov 2026): five reader runs on it and five on the translation as written, with one prompt (`tour/data/reader-runs.json`): the day-count problem raised in 5 of 5 planted runs and 0 of 5 as written; the planted rule named in 3 of 5 (2 at high confidence) |
| longer example | Universal Declaration of Human Rights, articles 23(4) to 26 ("Everyone has the right to form and to join trade unions ...") | `usecases/question-answering/udhr-part07.ve.md` | main | translation of a real text | one flag, judged a false alarm by a same-family session |
| 12 | A club's rules for its members, in plain lines with no word list declared (`own-rules.txt`: Ann is paid and not suspended, so allowed; `own-rules-new-word.txt`: uses "overlimit", a word not in VE's word list; `own-rules-new-word-fixed.txt`: the same with the `Words:` line VE offers; `own-rules-two-kinds.txt`: "free" said of members and of books, read as two words; `own-rules-two-meanings.txt`: "free" in two meanings for visitors, shown in a recorded run with the AI reader, `tour/data/reader-two-meanings.txt`) | `tour/texts/own-rules.txt`, `tour/texts/own-rules-new-word.txt`, `tour/texts/own-rules-new-word-fixed.txt`, `tour/texts/own-rules-two-kinds.txt`, `tour/texts/own-rules-two-meanings.txt` | main | written for the tour, except `own-rules-two-meanings.txt`: the first text of VE's own test set of texts with one word planted in two meanings | not run: VE's Python reader derives the words from its word list and shows them in the output for you to check; Lean does not check that step |

The answers written from the GitLab policy alone, before its translation ran, for Ivo's case are in
`tour/data/relocation-R009-sealed.jsonl` (stop 9). Their record is `tour/data/relocation-R009-sealed-provenance.json`,
and stop 9 prints it at the top of its output:

- **Written** on 25 November 2026, 19:17 to 19:26 UTC, by gpt-6-astra, an OpenAI model run through OpenAI's
  command-line agent: a different model family from the translators' (Claude Opus 5.5). It wrote the cases, the
  questions and these answers itself, from the policy's text and its written instructions only; it never saw the
  translation.
- **Sealed** on 25 November 2026 at 19:26 UTC as one set of 109 answers to 45 cases (SHA-256
  `676029e9c450294154812a0169711ad991b2e40bc58dd8460673fdbb4b32499e`), kept read-only in the project's private working
  records and never committed to a repository. The two answers here are its rows 23 and 24. The seal covers the whole
  set; each row's SHA-256 was taken from the sealed set on 28 November 2026 and is in the record, and stop 9 checks the
  two rows against it.
- **Translation frozen** before any question of the set existed: commit `8b113741bd` (25 November 2026, 11:00 UTC;
  `usecases/gitlab_relocation/translation.py` SHA-256 `a138701a902e0cc64667bff58ab033974bdfbb64e3d1177871fdf439cd517621`).
  The tour runs a later commit (`tour/AFTER_RELEASE_COMMIT`): the frozen translation plus one fix made after grading,
  for question R035-2. At the frozen commit, case R009's two answers were the same (no, no).
- **Who could read them:** rules, not locks. The set sits read-only on the project's machine, where any of the
  project's AI sessions could have opened it. By the run's written rules, the session that translated the policy never
  read it. The session that turned the questions into facts read only the questions until that work was committed (25
  November 2026, 19:53 UTC); it then ran the grading program and saw the grades. Two fresh AI sessions that built
  nothing judged 24 of the answers, a later check of the grading read the set, and the two rows here were copied from
  it. The grades, which quote the sealed answers, were open to the sessions that fixed the translation after grading.
- **In this repository** since commit `4bae6167b9` (26 November 2026), as a copy of the two rows. The original set has
  no commit of its own: by design it was kept out of every repository. The commit IDs on this page are those of the
  project's own repository; a published copy of its history has other IDs.

## The line after each Lean line

Stops 6, 7, 9 and 12 print one line after each Lean line of their output (stop 9 prints it after each answer), so that
"15 of 15" or "CHECKED" is not read as a score of the translation. The line is "Translation: " and then the stop's
cells in this table, joined by "; ". This table is the line's only source: `tour/stops/status.py` reads it here, and
the tour's test checks the recorded outputs against it, and its counts of open points against the table above, so a
change here is re-recorded with `tour/make_expected.py`.

| stops | who has read the translation | its open points | a check by a different AI family |
|---|---|---|---|
| 6 | read once by a same-family AI | 2 open points, none on this applicant | cross-family check due Nov 30 |
| 7 | read once by a same-family AI | 3 open points in the version run here (1 from that read, 2 found later), none on case R009; all three fixed on branch after-release after this commit | cross-family check due Nov 30 |
| 9 | the translation as written, not the planted copy: read once by a same-family AI | 3 open points in the version run here (1 from that read, 2 found later), none on case R009 | cross-family check due Nov 30 |
| 12 | none: these rules are written in VE's English, so there is no translation and no separate reader ran | Lean does not check the words VE read (listed above): check them yourself | |

## Who judged each dismissed flag

Every flag below was first judged by one fresh session of Claude Opus 5.5 (model ID `claude-opus-5-5`, effort high, no
tools) on 26 November 2026, one session per flag. Each judge was given the flag, the source's words, the translation's
lines, the reader's reason and the text's scope, and labelled the flag a real departure, a real difference that
changes no answer, or a false alarm. The judges are from the translators' model family; no person and no other AI
family has judged these flags yet. Each judgment's full text and its session record are in the project's working
records (the fidelity sweep's page for each text), not in this repository. Times are UTC, when the session started.

| stop(s) | text | flag (unit) | dismissed as | judge (Claude Opus 5.5 session) | why the judge dismissed it |
|---|---|---|---|---|---|
| 6 | Winter Fuel Payment Regulations 2025 | I24 (a payment made without a claim) | false alarm | `372ea93c-9772-4815-be7e-fa09cf0a3e3d`, 11:38 | the government's guide says people on a listed benefit "do not need to claim"; the translation assumes that payment only when the profile says nothing, and a profile that states otherwise overrides it |
| 6 | Winter Fuel Payment Regulations 2025 | I25 (opting out of the payment) | first judged a real departure (session `39dcfce2-085b-4091-a949-983ae5649abe`, 11:38); later closed as harmless | the Claude Opus 5.5 session that worked on the fix; its close was checked by a separate audit session `990edaad-e722-4c30-aea0-444f9b18c9a0`, 17:06 | VE refuses a profile that states an opt-out ("unknown field(s) opted_out"), and a profile silent on it is answered under a printed assumption that the applicant has not opted out, quoting the guide's sentence |
| 7, 9 | GitLab "Relocation / Address Change" | U6 (a lower day limit in some countries) | false alarm | `b35b1def-cddb-4668-aecb-8ede77832b44`, 10:59 | the policy's rules state 183 days only; the lower limit appears only in a duty to contact the People Operations team, and a country's own limit is outside the policy's text |
| 7, 9 | GitLab "Relocation / Address Change" | U16 (work from "most places" only) | false alarm | `cfb4808d-f71e-46a8-8253-3301f570e6bd`, 10:59 | the only restriction the policy gives is on taking company devices to US-embargoed countries, which the translation keeps, so its "yes" is the fair reading |
| 7, 9 | GitLab "Relocation / Address Change" | U33 (one year's tenure required for every request) | false alarm | `3e5df2bd-e7e2-41a2-8ec1-22d740edc6f5`, 10:59 | the policy requires one year's tenure without exception; its mention of prospective team members creates no exemption |
| 7, 9 | GitLab "Relocation / Address Change" | R011 (a 183-day stay that crosses 31 December) | false alarm | `90dab258-41db-44f6-8b23-0562cabd95dd`, 11:00 | the policy counts months per calendar year, and the case states the stay as two stays, one in each year, so the year-by-year count is right |
| 7, 9 | GitLab "Relocation / Address Change" | R033 (the case's recorded start date differs from the stated one) | a real difference that changes no answer | `bda9d1f4-337a-4924-8d3d-09784c98fcea`, 11:00 | the request date is on or after both the stated and the recorded start-date anniversary, so both of the case's answers stay the same |
| longer example | Universal Declaration of Human Rights, part 7 | U098 ("Elementary education shall be compulsory.") | false alarm | `09979e05-7adf-4d8e-94a9-ac40a7733965`, 10:51 | the sentence names no age, stage or class of persons, so the rule over every person is the plain reading |

No other flag on these texts was dismissed: stop 5's flag was fixed, the Winter Fuel I23 point and the GitLab U15
point were judged real departures and fixed on branch after-release, and the flags on stop 9's planted copy are left
open on purpose (the planted mistake is what the stop shows).
