# Question answering, Q1 evidence: the reverse question corpus (plan Q1.3)

**Summary.** F1 reads with its sentence's formula for 97,532 of 98,187 questions. All 655 misses are `QuestionTooLong`
(the question limits of plan 3.6), not a reading by Lean's reader. F2 reads with the formula for 1,029 of 1,029, with
no `many`. None of the 3,191 moved-word sentences is accepted. Both latency gates of 3.6 are **missed**: p95 is
146.8 ms (gate 100 ms) and the 64-candidate maximum is 3,372 ms (gate 1 s). Their revision goes to review (plan R12),
as follow-up q1-3c. Two of the seal's streams are not asked; q1-3b asks them.

## Commands

- **C1**: `uv run python -m conformance.question_reverse --workers 12` (defaults `--per-config 5000 --per-usecase 500`,
  the whole corpus), run at `7652add57`. It wrote `docs/question-answering/q1-3/evidence/question-reverse.json`. Each
  number below cites C1 with its key in that file.
- **C2**: `python3 -c 'import json;d=json.load(open("docs/question-answering/q1-3/evidence/question-reverse.json"));print(sum(v["sentences"] for v in d["configs"].values()),sum(v["one_formula"] for v in d["configs"].values()))'`
  prints `98452 98187`.
- **C3**: the same script with one worker and `--per-config 300 --per-usecase 100`, run at `22b7f5382`. It wrote
  `docs/question-answering/q1-3/evidence/question-reverse-sample.json`: 8,152 sentences. It is cited for its latency
  only, because it ran one question at a time.

## Corpus

- **Configurations:** 52 (C1 `configs`): the 43 corpus configurations of `english_lean_e2_evidence`, then 9
  use-case documents (`usecases/**/*.ve.md`, pilot runs excluded). None was skipped (C1 `coverage.skipped`).
- **Round-trip streams:** 17 of 5,000 texts, 85,000 in all, every one read with one formula. Each is byte for byte the
  stream the seal digests: C1 `coverage.sealed_streams` is 17 and `coverage.unsealed_streams` is empty, compared with
  `corpus_sha256` in `conformance/english-lean/corpus-seal.json`.
- **Use-case environment streams:** 26 of 500 texts, 13,000 in all, of which 12,905 read with one formula. These
  streams are not in the seal; they use the seal's generator at the size E2 chose.
- **Sentences:** with the documents' 464 unit texts that end with `.` (452 distinct), that makes 98,452 sentences, of
  which Lean reads 98,187 with exactly one formula (C2). The other 265 have an answer: 256 `none` and 9 `rejected`
  (C1 `configs.*.dropped`). No read was unavailable and no stream stopped short (C1 `coverage`).
- **Not asked:** the seal's other streams. These are `english-mixed` (6,757 texts) and `natural-view` (1,220 statements)
  (C1 `coverage.other_sealed_streams`), and, for each round-trip configuration, the 250 random Earley texts and 50
  multi-statement documents of `conformance/english-surface-report.json`. q1-3b asks the sentences among them.
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
| F1 read with the sentence's formula | 97,532 of 98,187 (0.993329) | C1 `f1` |
| F1 misses | 655, all `budget` / `QuestionTooLong`, questions of 1,192 to 3,803 bytes, in 30 configurations | C1 `f1.misses` |
| F2 read with the formula, or `many` | 1,029 of 1,029 (1.0); `many` 0 | C1 `f2` |
| F2 asked through a gap other than the subject's | 0 | C1 `f2.other_sentence` |
| Moved-word sentences (odd English) | 3,191, from 982 F2 questions with a second gap | C1 `odd` |
| Moved-word sentences Lean accepts | 0 | C1 `odd.accepted`, `odd.acceptances` |

**The F1 misses** are listed with their configurations in C1 `f1.misses`, each with its first 120 characters, its
length and its SHA-256 (the whole texts come from C1's stream). Every one is under 4,096 bytes and an F1 question has
one candidate, so the limit it meets is the 300-token one (3.6; `lean/VE/Question/Read.lean`, `classify`). The sentence
reader's cap is higher than the question reader's limits, and `caseThat_reads` assumes those limits (spec open point
3). None of the misses is a wrong reading, so no fix item for Lean's reader follows. **`many`** never occurs on the
corpus (spec open point 10.1). **Odd English:** each moved-word sentence puts the fronted word back before another word
of the question's rest. Lean reads none of them. This measures subjects without a clause only: fronting a word out of
a relative clause, the over-generation plan 4.9 describes (fixture G11), is not built here, so its measure is q1-3b's.

**Mutants** (C1 `mutants`, the same counts for F1 and F2):

| Kind | F1 outcome | F2 outcome |
|---|---|---|
| `double-space` | 98,179 `BadSpacing`; 8 `QuestionTooLong` | 1,029 `BadSpacing` |
| `space-before-mark` | 98,187 `BadSpacing` | 1,029 `BadSpacing` |
| `leading-space`, `lower-initial`, `upper-auxiliary` | 98,187 `QuestionForm` | 1,029 `QuestionForm` |
| `capital-body` (the body's first letter capitalised) | 92,359 read with the formula; 648 `QuestionTooLong` (93,007 built) | 93 of 93 read |

The 8 `double-space` questions pass 4,096 bytes once their spaces are doubled, and Lean checks the byte limit first.

## Latency against plan 3.6

| Gate | Measured | Budget | Met | Source |
|---|---|---|---|---|
| p95, every question asked, mutants included (688,396 questions) | 146.76 ms (F1 166.2, F2 212.5, mutants 144.4); max 3,619 ms | 100 ms | **no** | C1 `latency` |
| maximum, 64-candidate question (156 runs, 3 per configuration) | 3,372 ms; over 1 s in 13 of 52 configurations | 1 s | **no** | C1 `latency`, `limits` |
| 65 candidates | `QuestionTooLong` in all 52 configurations | the limit | yes | C1 `limits` |

- **How each question was timed:** sent alone through `relay.rows` to a persistent service, from the call until
  the row returned. The time includes the environment and lexicon the request carries.
- **Workers and load:** C1 ran 12 workers side by side, on a host whose load average went from 16.6 to 22.3 on 32 CPUs
  (C1 `workers`, `load_average`), so these times carry that load. C3, one question at a time with load from 10.8 to
  55.5, gave p95 126.47 ms and a 64-candidate maximum of 4,111.5 ms, so both gates are missed on either run.
- **Transport:** a request Lean refuses before reading anything (`NotOneQuestion`) takes a median of 2.1 to
  128.3 ms, depending on the configuration (C1 `configs.*.transport_ms`). In the slowest configurations most of the
  p95 is transport, not reading.
- **Long questions:** a 64-candidate question cycles a configuration's own words and reads as `none`. It is the
  worst case: every candidate is tried.
- **R12:** both gates are missed, so their revision is reviewed (q1-3c). Options for that review: keep the
  environment and lexicon in the service session, or measure on an idle host.

## Not measured here (q1-3b)

- F2 for subjects with a clause, with the 4.9 measure on them.
- The seal's streams listed under **Not asked**.
- Questions over norm documents.
- The closest-candidate count of spec open point 2.
