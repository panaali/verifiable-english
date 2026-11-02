# Question answering, Q1 evidence: the reverse question corpus (plan Q1.3)

**Summary.** F1 reads with its sentence's formula for 97,532 of 98,187 questions. All 655 misses are `QuestionTooLong`
(the question limits of plan 3.6), not a reading by Lean's reader. F2 reads with the formula for 1,029 of 1,029, with
no `many`. None of the 3,191 moved-word sentences is accepted. Both latency gates of 3.6 are **missed**: p95 is
146.8 ms (gate 100 ms) and the 64-candidate maximum is 3,372 ms (gate 1 s). Their revision goes to review (plan R12),
as follow-up q1-3c. q1-3b (C4, below) adds every fronting of *is*, *must* or *may*, the seal's other streams, the norm
part documents and open point 10.2's count: no fronting reads another formula or is `many`, no norm unit's text is
a question's source, and the closest candidate is a leftmost tie with the moved word second in most cases.

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
  --per-usecase 500`), run at `5728eb968`. It wrote `docs/question-answering/q1-3b/evidence/question-reverse-b.json`
  in 12,248 s on a host whose load average went from 34.1 to 74.4 on 32 CPUs (C4 `seconds`, `load_average`). Each
  number in this section cites C4 with its key in that file.
- **C5**: a sample, for the reason only: `run_config_b` on texts 1,000 to 1,149 of the `ordinary` sealed stream
  (`R.stream_of((0, 5000))`, `asks_f1=False`, `every=False`), with `5728eb968`'s code.

### Coverage (C4 `coverage`, `streams`)

C4 `coverage.whole_streams` is true. Each stream is the one its generator draws, compared with the seal's record.

| Stream | Drawn | Compared with | One-formula sentences | F1 read with the formula | F2 frontings (read with the formula) |
|---|---|---|---|---|---|
| `english-surface` (17 sealed streams) | 85,000 | `corpus_sha256`, 17 of 17 | 85,000 | asked in C1 | 343,977 (20,347) |
| `usecase-surface` (26 streams) | 13,000 | the seal's generator (not sealed) | 12,905 | asked in C1 | 44,984 (3,058) |
| `usecase-documents` (9) | 452 distinct | the files | 282 | asked in C1 | 316 (222) |
| random Earley (17 × 250) | 4,250 | `random_earley_corpus_sha256`, 17 of 17 | 4,250 | 4,163 of 4,250 | 33,256 (408) |
| documents of five (17 × 50) | 850 | `document_corpus_sha256`, 17 of 17 | each is its five random Earley sentences (`documents_not_their_sentences` 0), so its questions are theirs | | |
| `english-mixed` (18 configurations) | 6,757 texts | the report's `corpus_sha256`, 18 of 18; the seal's 6,757 | 5,073 (1,684 paragraphs are their sentences) | 5,073 of 5,073 | 8,752 (1,766) |
| `natural-view` (71 corpora) | 1,220 statements | the seal's 1,220 | 1,219 distinct | 1,202 of 1,219 | 3,851 (372) |
| norm part documents (15) | 5,858 units | the pilot blobs' SHA-256 (C4 `norm.documents.*.sha256`) | 0 | 0 of 5,117 asked | 0 of 2,121 |

- **How the new streams are drawn:** `english-mixed` by `english_mixed.mixed` itself (its texts kept, its parsing
  left out) and `natural-view` by `natural_surface.audit` itself (each `render_natural_sentence` text, the audit
  stopped at its prose example). The random Earley stream is drawn as `english_surface.audit` draws it. The digests
  in the table show each is the stream the seal records.
- **The 104 F1 misses** (C4 `f1.misses`) are all `QuestionTooLong` (87 random Earley, 17 `natural-view`), of 1,270 to
  4,162 bytes: the question limits of 3.6, as in C1.

### F2 for every fronting (plan 4.9; C4 `f2`)

Every occurrence of *is*, *must* or *may* after a sentence's first word is fronted in turn, whatever the subject.
Python does not choose the main sentence's word: Lean decides each candidate question.

| Measure | Value | Source |
|---|---|---|
| Frontings of one-formula sentences | 435,136, from 102,207 sentences | C4 `f2.frontings`, `f2.sentences` |
| Outcomes | 26,173 `one`; 196,666 `moved` (`QuestionWordMoved`); 212,297 `budget` (`QuestionTooLong`) | C4 `f2.outcomes` |
| Read with another formula | **0** | C4 `f2.other_formula` |
| `many` | 0 | C4 `f2.many_causes` |
| Sentences with a fronting that reads with the formula, or `many` | 26,173 of 102,207 (0.256078) | C4 `f2.share` |
| The same, without the 24,264 sentences whose every fronting is over the limits | 26,173 of 77,943 (0.335797) | C4 `f2.limited`, `f2.share_within_limits` |
| Sentences with two frontings that read | 0 | C4 `f2.by_subject.*.several_same` |
| Subjects q1-3's `f2` builds (no clause) | 1,117 of 1,117, each by q1-3's question | C4 `f2.by_subject."q1-3 subject"` |
| Every other sentence (a clause, a conditional, a list, a quantifier phrase) | 25,056 of 101,090 | C4 `f2.by_subject."other subject"` |

- **Over-generation:** no fronting reads with a formula other than its sentence's, so the 4.9 measure finds no
  acceptance to list.
- **Moved refusals:** the sentences that no fronting reaches within the limits have no auxiliary in the main sentence.
  Each one begins `If …, then`, `At least one of the following holds:`, `All of the following hold:` or
  `For every X, …`. Lean refuses each fronting as `moved` and offers the F1 rephrasing. In C5, 111 of 148 sentences
  are like this; their first words are `If` (30), `At` (23), `All` (20), `For` (18) and `Both` (13). Every one of
  them has its F1 question, which C1 reads unless it is over the limits.

### Questions over norm documents (C4 `norm`)

- **Documents:** the latest version of each part document that AR-17's `pilot_parts.selected` picks from the
  `pilot/*` branches, with no whole documents (L70). These are 5 constitution readings parts (`s1`, `nd-s01p1`,
  `nd-force`, `nd-op`, `soft-chain`), 9 UDHR `translation-part<n>`, and main's `udhr-part07`.
- **Reached:** no unit sentence is read by `english.read` with one formula, so no F1 or F2 question has a source
  sentence (C4 `norm.documents.*.reach`, `streams.norm-documents.one_formula` 0).
- **Why, by unit (5,858):**
  - 3,794 `english.read` `none` (`NoDerivation`);
  - 1,004 unavailable: the `soft-chain` part's environment has profile `soft-norms@0`, which `english.read` and
    `english.question` refuse (`UnsupportedProfile`);
  - 736 not one sentence (a heading, or several lines);
  - 324 `rejected` by the lexer: 232 `BadSpacing`, 80 `BadCharacter` (curly quotes, `/`, `;`, `[`), 8 `BadNumeral` and 4
    `OpenQuote`.
- **By kind:** 5,429 `unformalised`, 244 `meta`, 143 `norm` (73 with a norm content), 41 `asserted` (30 with an AST,
  8 with a fence) and 1 without a kind. A norm's or an assertion's meaning is in its `content`, not in its text. The
  text is the source English, which is not VE English. A norm is not a statement, so it is not a question's source.
  Two example texts of each class are in C4 `norm.documents.*.examples`.
- **Questions asked anyway** (F1 for each of the 5,117 one-line units, and each fronting): 7,238. None reads (C4
  `streams.norm-documents`). They are the population of 10.2 below.

### Open point 10.2: the closest candidate (C4 `closest`)

- **Which questions:** every question with no reading, 5,252 of them (3,746 F1, 1,506 F2), all from the norm part
  documents. The corpus streams give none: their F2 outcomes have no `none`, and their F1 misses are limits. Each one
  names its closest sentence tried (`named` 5,252).
- **What is measured:** `english.read`'s own diagnosis of every candidate. Python counts the candidates that share the
  right-most diagnosis start, in bytes, and checks Lean's named choice against the leftmost of them. Lean chose; Python
  does not.

| Measure | Value | Source |
|---|---|---|
| F1: one candidate, so no tie | 3,746 | C4 `closest.one_candidate` |
| F2 with more than one candidate, its closest one of the word-gap candidates | 1,446 | C4 `closest.measured` |
| F2 whose closest is not a word-gap candidate (Lean's token gaps around Markdown `**`) | 60 (1,506 − 1,446; 20 listed) | C4 `closest.named_unmatched` |
| Lean's closest is the leftmost of its ties | every one of 5,192 (0 inconsistent) | C4 `closest.inconsistent` |
| The closest is a tie of two or more | 1,314 of 1,446 (0.908714); unique 132 | C4 `closest.tied`, `closest.unique`, `closest.share_tied` |
| Its moved word sits second (the first gap; A9, U1, U8's pattern) | 1,406 of 1,446 (0.972337); 1,286 of them tied | C4 `closest.moved_second`, `closest.moved_second_tied` |
| Not the reader's sentence (the source order, a candidate in 1,430) | 1,239 of 1,430 (0.866434) | C4 `closest.not_the_readers`, `closest.share_not_the_readers` |

- **Examples:** C4 `closest.examples` holds ten, all from the constitution part `s1`. In each one, every one of 32 to
  54 candidates fails at the same token, so the tie goes to `<first word> is …`. For example, `Is for example, it
  probably good for Claude …` gets `for is example, it probably good …`.
- **For the plan:** on these questions the leftmost-tie rule names the moved-word-second sentence in 97% of cases,
  and a sentence other than the reader's in 87%. The population is prose that has no reading at all. A better tie
  rule, for example the candidate whose gap follows the subject's noun phrase, needs its own statement (10.2). This
  count is the evidence for weighing that row.

### Latency (recorded for q1-3c, not judged)

C4 `latency`: 452,916 questions, p95 1,226.8 ms (F1 530.8, F2 1,257.2), maximum 24,136 ms, with 12 workers on the
loaded host above. The long random Earley and constitution sentences make most of it. The two gates of 3.6 are q1-3c's
(HUMAN).
