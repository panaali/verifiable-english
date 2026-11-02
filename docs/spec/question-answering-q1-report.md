# Question answering, Q1 evidence: the reverse question corpus (plan Q1.3)

**Summary.** F1 reads with its sentence's formula for 97,532 of 98,187 questions. All 655 misses are `QuestionTooLong`
(the question limits of plan 3.6), not a reading by Lean's reader. F2 reads with the formula for 1,029 of 1,029, with
no `many`. None of the 3,191 moved-word sentences is accepted. Both latency gates of 3.6 are **missed**: p95 is
146.8 ms (gate 100 ms) and the 64-candidate maximum is 3,372 ms (gate 1 s). Their revision goes to review (plan R12),
as follow-up q1-3c. q1-3b (C4, below) adds every fronting of *is*, *must* or *may*, the seal's other streams, the norm
part documents and open point 10.2's count. No fronting that Lean answers reads another formula or is `many` (C4
`f2.other_formula`, `f2.many_causes`). In the norm part documents, 5 of 5,859 units are reached, all `ve` fences of kind
`asserted`; of the 143 units of kind `norm`, `english.read` answers 100 and reads none (97 `none`, 3 `rejected`), and of
the other 43, 30 are not one sentence and 13 are in `soft-chain`, whose 1,006 units have no answer (C4 `norm.reached`,
`norm.by_why`, `norm.documents.*.reach`). On the 1,442 F2 questions with no reading that 10.2 can measure, the closest
candidate is a tie in 91% and has its moved word second in 97% (C4 `closest.measured`, `closest.share_tied`,
`closest.share_moved_second`).

## Commands

- **C1**: `uv run python -m conformance.question_reverse --workers 12` (defaults `--per-config 5000 --per-usecase 500`,
  the full size of every stream it draws), run at `7652add57`. It wrote `docs/question-answering/q1-3/evidence/question-reverse.json`. Each
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

## q1-3b: every fronting, the other streams, norm documents and open point 10.2

- **C4**: `uv run python -m conformance.question_reverse --part b --workers 12` (defaults `--per-config 5000
  --per-usecase 500`), run at `5c56edcec`. It wrote `docs/question-answering/q1-3b/evidence/question-reverse-b.json`
  in 13,694 s on a host whose load average went from 20.4 to 46.0 on 32 CPUs (C4 `seconds`, `load_average`). Each
  number in this section cites C4 with its key in that file. It replaces the run at `5728eb968`, which read each
  unit's prose and never its `ve` fence.
- **C5**, **C6**: `uv run python docs/question-answering/q1-3b/samples.py`, with `5c56edcec`'s code under
  `conformance/`. It wrote `docs/question-answering/q1-3b/evidence/samples.json` (keys `c5`, `c6`). C5 is a sample, for
  the reason only: `run_config_b` on texts 1,000 to 1,149 of the `ordinary` sealed stream (`asks_f1=False`,
  `every=False`). C6 reads under changed profile lists, for the cause only, so its outcomes are never C4's answers.
- **Claims**: `uv run python docs/question-answering/q1-3b/claims.py` checks this section and the summary above against
  those files: each sentence cites its key, and each number is that key's value.

### Coverage (C4 `coverage`, `streams`)

C4 `coverage.whole_streams` is false for one reason: the `soft-chain` part's 1,005 sentences have no answer
(C4 `coverage.unavailable_reads`; every other key of `coverage` that leaves a run partial is empty or zero). The table
says what each stream is compared with; `usecase-surface` is not in the seal.

| Stream | Drawn | Compared with | One-formula sentences | F1 read with the formula | F2 frontings (read with the formula) |
|---|---|---|---|---|---|
| `english-surface` (17 sealed streams) | 85,000 | `corpus_sha256`, 17 of 17 | 85,000 | asked in C1 | 343,977 (20,347) |
| `usecase-surface` (26 streams) | 13,000 | not compared: drawn by the seal's generator (not sealed) | 12,905 | asked in C1 | 44,984 (3,058) |
| `usecase-documents` (9) | 452 distinct | not compared: read from the files | 282 | asked in C1 | 316 (222) |
| random Earley (17 × 250) | 4,250 | `random_earley_corpus_sha256`, 17 of 17 | 4,250 | 4,163 of 4,250 | 33,256 (408) |
| documents of five (17 × 50) | 850 | `document_corpus_sha256`, 17 of 17 | each is its five random Earley sentences (`documents_not_their_sentences` 0), so its questions are theirs | | |
| `english-mixed` (18 configurations) | 6,757 texts | the report's `corpus_sha256`, 18 of 18; the seal's 6,757 | 5,073 (1,684 paragraphs are their sentences) | 5,073 of 5,073 | 8,752 (1,766) |
| `natural-view` (71 corpora) | 1,220 statements | the seal's 1,220 | 1,219 distinct | 1,202 of 1,219 | 3,851 (372) |
| norm part documents (15) | 5,859 units | not compared: each part's git blob id, or `udhr-part07`'s SHA-256, recorded (C4 `norm.documents.*.sha256`) | 5 | 5 of 5,119 asked (1,005 unanswered) | 4 of 2,125 (422 unanswered) |

- **How the new streams are drawn:** `english-mixed` by `english_mixed.mixed` itself (its texts kept, its parsing
  left out) and `natural-view` by `natural_surface.audit` itself (each `render_natural_sentence` text, the audit
  stopped at its prose example). The random Earley stream is drawn as `english_surface.audit` draws it. The digests
  in the table show each is the stream on record; `natural-view` has only the seal's count to compare.
- **The 104 F1 misses** (C4 `f1.misses`) are all `QuestionTooLong` (87 random Earley, 17 `natural-view`), of 1,270 to
  4,162 bytes: the question limits of 3.6, as in C1.

### F2 for every fronting (plan 4.9; C4 `f2`)

Every occurrence of *is*, *must* or *may* after a sentence's first word is fronted in turn, whatever the subject.
Python does not choose the main sentence's word: Lean decides each candidate question.

| Measure | Value | Source |
|---|---|---|
| Frontings of one-formula sentences | 435,142, from 102,212 sentences | C4 `f2.frontings`, `f2.sentences` |
| Outcomes | 26,177 `one`; 196,667 `moved` (`QuestionWordMoved`); 212,297 `budget` (`QuestionTooLong`); 1 `unavailable` | C4 `f2.outcomes` |
| Read with another formula | **0** | C4 `f2.other_formula` |
| `many` | 0 | C4 `f2.many_causes` |
| Sentences with a fronting that reads with the formula, or `many` | 26,177 of 102,212 (0.256105) | C4 `f2.share` |
| The same, without the 24,264 sentences whose every fronting is over the limits | 26,177 of 77,948 (0.335826) | C4 `f2.limited`, `f2.share_within_limits` |
| Sentences with two frontings that read | 0 | C4 `f2.by_subject.*.several_same` |
| Subjects q1-3's `f2` builds (no clause) | 1,121 of 1,121, each by q1-3's question | C4 `f2.by_subject."q1-3 subject"` |
| Every other sentence (a clause, a conditional, a list, a quantifier phrase) | 25,056 of 101,091 | C4 `f2.by_subject."other subject"` |

- **Over-generation:** no answered fronting reads with a formula other than its sentence's, so the 4.9 measure finds
  no acceptance to list (C4 `f2.other_formula`).
- **The one `unavailable`:** a `usecase-surface` fronting (C4 `streams.usecase-surface.f2_unavailable`) got no answer
  in this run. It is not a Lean answer, and it changes no share: `f2.by_subject."other subject".reached` is 25,056 in
  both runs. C4 saved its count, not its text or error, so the cause is not known. The run at `5728eb968` had no
  `unavailable` outcome over the same frontings.
- **Moved refusals:** C4 does not save which sentences no fronting reaches, so their shape is known from C5 only. There,
  111 of 148 sentences have no fronting that reads, and each begins with a frame, not a subject, such as `If …, then`,
  `At least one of the following holds:`, `All of the following hold:` or `For every X, …`. Their first words are `If`
  (30), `At` (23), `All` (20), `For` (18), `Both` (13), `There` (4), `It` (2) and `Either` (1) (C5 `sentences`,
  `unreached`, `first_words`). Lean refuses their frontings as `moved`, with the F1 rephrasing, or at its limits (C5
  `outcomes`). Each has its F1 question, which C1 reads unless it is over the limits (C1 `f1.misses`).

### Questions over norm documents (C4 `norm`)

- **Documents:** the latest version of each part document that AR-17's `pilot_parts.selected` picks from the
  `pilot/*` branches, with no whole documents (L70). These are 5 constitution readings parts (`s1`, `nd-s01p1`,
  `nd-force`, `nd-op`, `soft-chain`), 9 UDHR `translation-part<n>`, and main's `udhr-part07`.
- **What is read:** each unit as the document loader reads it (`document_units`): the parts of a `MIXED` unit, and
  the English `ve` fence a unit names as its text, whatever its lines, since that is the sentence Lean reads. A unit
  with no fence has its span, which is source prose.
- **Reached:** 5 units, all fences (C4 `norm.reached`, `streams.norm-documents.one_formula`, and each document's
  `norm.documents.*.examples`): `Claude is not human.` (u0248) in `s1`, `nd-s01p1`, `nd-force` and `nd-op`, and the list
  `Both of the following hold: …` (u0166.s04.p4) in `nd-s01p1`. All 5 F1 questions read with the formula
  (`f1_same` 5). `Is Claude not human?` reads with it in all 4 parts (`f2_same` 4), and both frontings of the list are
  `moved`. These are all the English fences Lean answers for; the other 3, in `soft-chain`, have no answer. All 8 are
  of kind `asserted` (C4 `norm.documents.*.reach`).
- **Why, by unit (5,859; C4 `norm.by_why`):**
  - 5 reached;
  - 3,789 `english.read` `none` (`NoDerivation`);
  - 1,006 unavailable: the `soft-chain` part's environment lists both `soft-norms@0` and `norm-defaults@0`, and
    `english.read` and `english.question` refuse that pair (`UnsupportedProfile`, whose text names `soft-norms@0`).
    Each alone reads: `s1` lists only `soft-norms@0`, `nd-s01p1` only `norm-defaults@0` (C6 `pair`, `soft_only`,
    `defaults_only`). Without `soft-norms@0`, `soft-chain` reads its 3 fences and none of its other 1,002 sentences
    (C6 `soft_chain_without_soft`), and it cannot drop `norm-defaults@0` (C6 `soft_chain_without_defaults`);
  - 735 not one sentence (a heading, or several lines);
  - 324 `rejected` by the lexer: 232 `BadSpacing`, 80 `BadCharacter` (curly quotes, `/`, `;`, `[`), 8 `BadNumeral` and 4
    `OpenQuote`.
- **By kind (C4 `norm.documents.*.reach`):** 5,424 `unformalised` (20 of them attributed), 245 `meta`, 143 `norm`
  (73 with a norm content), 42 `asserted` (31 with an AST, 8 with a fence), and 5 attributed norms or assertions. A
  fenced unit's sentence is in the document. The meaning of those 73 norms and 31 AST assertions is in their `content`,
  and the document holds no VE sentence for it: their text is the source English, which is not VE English. The other
  70 norms have no `content`. This run does not render those 104 contents into English, so no question starts from them
  here. A norm is not a statement, but its text is read like any unit's: `english.read` answers 100 of the 143 and reads
  none (97 `none`, 3 `rejected`); 13 in `soft-chain` have no answer and 30 are not one sentence. Two example texts of each class
  are in C4 `norm.documents.*.examples`.
- **Questions asked of every sentence** (F1 for each of the 5,119 sentences, and each fronting): 7,244, of which 1,427
  have no answer (`f1_unavailable` 1,005, `f2_unavailable` 422, all `soft-chain`). Only the 9 above read (C4
  `streams.norm-documents`). The 5,243 with no reading are the population of 10.2 below (C4 `closest.no_reading`).
- **Repeats:** the five constitution parts repeat one source text, and each part is asked in full. The answered
  questions come from 1,066 distinct sentences (`norm.distinct_answered_sentences`), and their 1,703 frontings are 433
  distinct texts (`norm.distinct_answered_frontings`). So the 10.2 counts below weigh a text once per part.

### Open point 10.2: the closest candidate (C4 `closest`)

- **Which questions:** every question with no reading, 5,243 of them (3,741 F1, 1,502 F2), all from the norm part
  documents, and 1,336 distinct texts (C4 `closest.distinct_no_reading`). The corpus streams give none: their F2
  outcomes have no `none`, and their F1 misses are limits (C4 `f2.outcomes`, `f1.misses`). Each one names its closest
  sentence tried (C4 `closest.named`).
- **What is measured:** `english.read`'s own diagnosis of every candidate. Python counts the candidates that share the
  right-most diagnosis start, in bytes, and checks Lean's named choice against the leftmost of them. Lean chose; Python
  does not.

| Measure | Value | Source |
|---|---|---|
| F1: one candidate, so no tie | 3,741 | C4 `closest.one_candidate` |
| F2 with more than one candidate, its closest one of the word-gap candidates | 1,442, 364 distinct texts | C4 `closest.measured`, `closest.distinct_measured` |
| F2 whose closest is not a word-gap candidate (Lean's token gaps around Markdown `**`) | 60 (1,502 − 1,442; 20 listed) | C4 `closest.named_unmatched` |
| Lean's closest is the leftmost of its ties | every one of 5,183 (0 inconsistent): 3,741 have one candidate, so 1,442 had a choice | C4 `closest.inconsistent`, `closest.one_candidate`, `closest.measured` |
| The closest is a tie of two or more | 1,310 of 1,442 (0.90846); unique 132 | C4 `closest.tied`, `closest.unique`, `closest.share_tied` |
| Its moved word sits second (the first gap; A9, U1, U8's pattern) | 1,402 of 1,442 (0.972261); 1,282 of them tied | C4 `closest.moved_second`, `closest.moved_second_tied` |
| Not the reader's sentence (the source order, a candidate in 1,426) | 1,239 of 1,426 (0.868864) | C4 `closest.not_the_readers`, `closest.share_not_the_readers` |

- **Examples:** C4 `closest.examples` holds ten, all from the constitution part `s1`. In each one, 32 to 54 candidates
  tie at the same token (C4 `closest.examples.*.ties`), so the tie goes to `<first word> <moved word> …`. For example,
  `Is But we want Claude to know that it was brought into being …` gets `But is we want Claude to know that it was …`.
- **For the plan:** on these questions the leftmost-tie rule names the moved-word-second sentence in 97% of cases, and
  a sentence other than the reader's in 87% (C4 `closest.share_moved_second`, `closest.share_not_the_readers`). The
  population is prose with no reading, 5,243 questions (C4 `closest.no_reading`). A better tie rule, for example the
  candidate whose gap follows the subject's noun phrase, needs its own statement (10.2). This count is the evidence
  for weighing that row.

### Latency (recorded for q1-3c, not judged)

C4 `latency`: 452,922 questions, p95 1,451.3 ms (F1 291.2, F2 1,481.0), maximum 51,468 ms, with 12 workers (C4 `workers`)
on the loaded host above. C4 saves no latency by sentence length, so it gives no cause; the highest p95 of one
configuration is 6,813 ms, `anthropic-rsp`'s (C4 `configs.*.p95_ms`). The two gates of 3.6 are q1-3c's (HUMAN).
