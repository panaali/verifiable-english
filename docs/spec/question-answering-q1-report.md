# Question answering, Q1 evidence: the reverse question corpus (plan Q1.3)

**Summary.** F1 reads with its sentence's formula for 7,957 of 7,967 questions. All 10 misses are `QuestionTooLong`
(the question limits of plan 3.6), not a reading by Lean's reader. F2 reads with the formula for 269 of 269, with
no `many`. None of the 484 moved-word sentences is accepted. Both latency gates of 3.6 are **missed**: p95 is
126.5 ms (gate 100 ms) and the 64-candidate maximum is 4,111 ms (gate 1 s). Their revision goes to review (plan R12),
as follow-up q1-3c.

## Commands

- **C1**: `uv run python -m conformance.question_reverse` (defaults `--per-config 300 --per-usecase 100`), run at
  `22b7f5382`. It wrote `docs/question-answering/q1-3/evidence/question-reverse.json`. Each number below cites C1
  with its key in that file.
- **C2**: `python3 -c 'import json;d=json.load(open("docs/question-answering/q1-3/evidence/question-reverse.json"));print(sum(v["sentences"] for v in d["configs"].values()),sum(v["one_formula"] for v in d["configs"].values()))'`
  prints `8152 7967`.

## Corpus

- **Configurations:** 52 (C1 `configs`): the 43 corpus configurations of `english_lean_e2_evidence`, then 9
  use-case documents (`usecases/**/*.ve.md`, pilot runs excluded).
- **Sentences:** each configuration gives the first 300 texts of its sealed stream (round-trip) or the first 100
  (use-case environment); a document gives its unit texts that end with `.`. That makes 8,152 sentences, of which
  Lean reads 7,967 with exactly one formula (C2).
- **Use-case documents:** only `group.ve.md` (3) and three agent-policy documents (93 each) give sentences that
  `english.read` reads (C1 `configs.*.one_formula`). The other units are norms in another wording (`a-rules`,
  `udhr-part07`), metadata or prose.
- **Questions:** each kept sentence gets its F1 question. Where the sentence begins with a quantified subject
  without a clause or comma, or a one-word name, followed by *is*, *must* or *may*, it also gets an F2 question.
  Each question gets its six mutants. A subject with a clause gets no F2 question, because which word belongs to the
  main sentence is Lean's decision (`VE.Question.Moved`); that is q1-3b.

## Measures

| Measure | Value | Source |
|---|---|---|
| F1 read with the sentence's formula | 7,957 of 7,967 (0.998745) | C1 `f1` |
| F1 misses | 10, all `budget` / `QuestionTooLong`, questions of 1,496 to 2,742 bytes | C1 `f1.misses` |
| F2 read with the formula, or `many` | 269 of 269 (1.0); `many` 0 | C1 `f2` |
| F2 asked through a gap other than the subject's | 0 | C1 `f2.other_sentence` |
| Moved-word sentences (odd English) | 484, from 230 F2 questions with a second gap | C1 `odd` |
| Moved-word sentences Lean accepts | 0 | C1 `odd.accepted`, `odd.acceptances` |

**The F1 misses** are listed with their configurations in C1 `f1.misses`. Every one is under 4,096 bytes, so the
limit it meets is the 300-token one (3.6). The sentence reader's cap is higher than the question reader's limits,
and `caseThat_reads` assumes those limits (spec open point 3). None of the misses is a wrong reading, so no fix item
for Lean's reader follows. **`many`** never occurs on the corpus (spec open point 10.1). **Odd English:** each
moved-word sentence puts the fronted word back before another word of the question's rest. Lean reads none of them,
so the corpus shows no over-generation of the kind plan 4.9 describes.

**Mutants** (C1 `mutants`, the same counts for F1 and F2):

| Kind | F1 outcome | F2 outcome |
|---|---|---|
| `double-space`, `space-before-mark` | 7,967 `BadSpacing` | 269 `BadSpacing` |
| `leading-space`, `lower-initial`, `upper-auxiliary` | 7,967 `QuestionForm` | 269 `QuestionForm` |
| `capital-body` (the body's first letter capitalised) | 7,458 read with the formula; 10 `QuestionTooLong` (7,468 built) | 13 of 13 read |

## Latency against plan 3.6

| Gate | Measured | Budget | Met | Source |
|---|---|---|---|---|
| p95, corpus question (56,897 questions) | 126.47 ms (F1 144.1, F2 85.8, mutants 124.1); max 325.8 ms | 100 ms | **no** | C1 `latency` |
| maximum, 64-candidate question (156 runs, 3 per configuration) | 4,111.5 ms; over 1 s in 16 of 52 configurations | 1 s | **no** | C1 `latency`, `limits` |
| 65 candidates | `QuestionTooLong` in all 52 configurations | the limit | yes | C1 `limits` |

- **How each question was timed:** sent alone through `relay.rows` to the persistent service, from the call until
  the row returned. The time includes the environment and lexicon the request carries.
- **Transport:** a request Lean refuses before reading anything (`NotOneQuestion`) takes a median of 2.0 to
  182.3 ms, depending on the configuration (C1 `configs.*.transport_ms`). In the slowest configurations most of the
  p95 is transport, not reading.
- **Load:** the host's load average rose from 10.8 to 55.5 on 32 CPUs during the run (C1 `load_average`).
- **Long questions:** a 64-candidate question cycles a configuration's own words and reads as `none`. It is the
  worst case: every candidate is tried.
- **R12:** both gates are missed, so their revision is reviewed (q1-3c). Options for that review: keep the
  environment and lexicon in the service session, or measure on an idle host.

## Not measured here (q1-3b)

- F2 for subjects with a clause.
- Questions over norm documents.
- The closest-candidate count of spec open point 2.
