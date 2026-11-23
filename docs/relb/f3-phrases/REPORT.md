# relb-f3-phrases: plain phrases for the eligibility yes/no facts (report)

## Number (MEASURED, same text before and after)
Text: the 56 rules of usecases/eligibility/translation.py and the 80 distinct profile facts that hold a yes/no
predicate. A rule or fact counts when its generated wording (render_w6_sentence) reads back (parse_w6_sentence) to
exactly one reading, equal to it, and every yes/no predicate in it reads with its declared wording.
Command: `python -B docs/relb/f3-phrases/evidence/measure.py <checkout> [--wordings <name->template json>]`.

| | before (main fc84ed56a2, no wordings) | after (this branch, plain_wordings.json declared) |
|---|---|---|
| rules in plain phrases | 1 of 56 (B1, no yes/no predicate) | **56 of 56** |
| facts in plain phrases | 0 of 80 | **80 of 80** |
| rules / facts that read back to themselves | 56 / 80 | 56 / 80 |
| wrong readings | 0 | 0 |

(evidence/measure-before.json, measure-after.json.) The same 48 natural wordings declared on main: 48 of 48 refused
by the shape lint, each falling back to 'is classified as' (measure-spike.json; causes in the spike page).

## Tests (tests/test_relb_f3_plain_phrases.py, 21; 10 fail on main, 21 pass here)
Every predicate has one plain wording; every wording is accepted; every rule and every fact reads back in plain
phrases (the facts also with applicant and housemate swapped: never read as the fact); near misses are refused
("Applicant is detained.", "Applicant is entitled.", "Applicant has moved to Scotland.", "... during the week.");
each phrase has one reading, its own (a longer phrase never reads as the shorter predicate, argument order is
literal); an unrelated wording, a duplicated wording and a wording outside the idiom list are refused.
Seeded mutants: 4 of 4 killed (mutants.json, evidence/mutants-run.json).

## Fresh-writer check (MEASURED; evidence/fresh-writer/, committed unedited)
A fresh Opus 5.5 seat (picker's pick) saw only the source text of ten facts (source.txt) and wrote one sentence per
fact (writer-out.txt). Read with the wordings: 1 of 10 read, equal to its fact (F2 "The applicant is a partner of the
housemate."), 9 refused, 0 wrong (read-branch.out); without them 0 of 10 (read-without-wordings.out). The writer kept
the source's own phrasing ("share accommodation as their mutual home", "did not make a claim"), so one fixed phrase
per predicate covers the generated text, not a writer's paraphrase or inline negation ("has not", "did not").
That gap is stream 2's (write naturally).

## Limits
- The idiom guard checks that a wording shares a content word with its predicate's name or legend; it does not
  check fidelity. Swapping the wordings of two exclusion predicates would be accepted (both contain "excluded").
  The checker does not vouch for English fidelity (kernel-boundary.md section 3); the wordings were written from
  the legends and are listed for review in plain_wordings.json.
- Constants still read by their names ('paid "state_pension"'); F3 covers predicates only.
- Negation inside a phrase ("Applicant is not excluded.", "has not reached") and inline "A and B" are refused
  for every wording, old or new; rules use the "It is not the case that" and "All of the following hold" layouts.

## Follows once relb-f1f2-eligibility merges
translation.py declares the 49 wordings from plain_wordings.json as `verbalisation`s; environment.json, results.json
(environment id, the fact rows' and relb-f1f2-eligibility's rule rows' sentences), RESULTS.md and
docs/kernel/ownership.json are regenerated; tests/test_eligibility_wfp.py's pinned environment id moves.
