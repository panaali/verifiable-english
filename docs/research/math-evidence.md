# Science papers in VE: mathematics, physics, deep learning and VE's own paper (research)

> **Status.** Draft 1, 2026-10-12, branch `design/math-evidence` from `main` at `49de179e` (`ve-green-ts-B1`). DRI
> research wave: docs only, no product code, no tests, no generated files touched, no model calls. The plan for the
> recommended design is [docs/spec/math-evidence-PLAN.md](../spec/math-evidence-PLAN.md) (cited `plan n`).
>
> **Inputs read.** `VISION.md`, `ROADMAP.md`, `FUTURE.md` (a pointer to ROADMAP), `PLAN-EXPAND2.md`,
> `/home/seyran/code/ve-northstar/NORTH-STAR.md` (rows M, H, DL, V, D and the feature table),
> `/home/seyran/code/manage-agents/CURRENT-STATE.md` (in-flight list to 2026-10-12 23:00Z), the specs
> `docs/spec/{units-schema,document,data-stage1,risk,closure-induction}.md`, `docs/W6A-STATUS.md`,
> `docs/lean-first/b9/LEDGER.md`, `lean/VE/Definitions/STATEMENTS.md`, `design/vex-mandatory-evidence.md`,
> `design/evidence-layer-design.md`, `experiments/obfuscated-arguments/iceberg/VE.md`, the Lean sources named below,
> `usecases/*/GAPS.md`, `usecases/math-mini-paper/{coverage,boundary,definitions-report,report}.md`, the VE paper
> (`paper/sections/*.md`, `paper/analysis/README.md`, `paper/generated/*`), the constitution and UDHR pilot runs
> `run-20261012T1800Z`, and the sibling designs that existed when this was written (`weighing`, `attitudes`,
> `events-time-causation`, `act-phrases`). `quantities` and `scope` appeared before the plan was written; the plan
> (its decisions D6, D8, D12, D13 and section 10) aligns with them, and section 9 here notes the two points of contact.
>
> **How numbers were made.** Counts over the pilot ledgers come from ripgrep (the Grep tool) in this session; byte counts
> are span lengths (`end − start`) read from the ledgers and added by hand, each sum shown. File sizes and line counts
> come from `wc`. The shell allowed only `wc`, `ls` and read-only `git`; no script computed anything. The three new
> target texts are **not in the repository and were not fetched** (fetching tools summarise pages with a model, which
> this task forbids). Everything said about their content is from memory of the published texts and is marked
> **estimate**; plan batch ME-0 pins the texts and measures it. Anything not measured is labelled an estimate.

## 0. Summary

- **What exists.** VE already has most of the *logical* machinery a mathematics paper needs at the scale of a
  relational exercise: definitions, biconditionals and lemma citation (W3), closure induction, bounded n-ary
  relations, total functional relations and set membership (W5 `data@0`), and exact scaled decimals with nominal unit
  tags, dates and small counts (W6a, owned by Lean). The math mini-paper certifies 18 of 19 queries. What VE does not
  have is any way to check a **number that is computed** (a rate, a mean, a predicted effect), an **equation between
  quantities**, a **unit's dimension**, a **statistical result**, or a **theorem about the integers** beyond ground
  linear facts.
- **The need on the pinned pilots is zero.** No unit of the constitution (1,132 units) or the UDHR (130 units) names
  this topic as a primary blocker or a co-blocker (section 2.2). The words "evidence", "probability" and "empirical"
  occur in 12 constitution units (2,786 B), always as an epistemic standard on Claude's own judgement, which belongs to
  the attitudes and weighing designs. This design moves **no byte** of either pinned pilot, and the plan says so.
- **The need is in the new use cases** (NORTH-STAR rows M, H, DL, weight 3 each, all unmeasured) and in VE's own paper
  (row V, weight 3). VE's paper is 73,801 B; 55 of its 554 main-text lines and 131 of its 556 appendix lines carry a
  rate, fraction, percentage, interval or p-value (measured, section 2.5). Every one of those numbers is a calculation
  from data that sits in the repository.
- **Step 0 picks.** Physics: Michelson and Morley, "On the Relative Motion of the Earth and the Luminiferous Ether"
  (1887, 13 pages, public domain). Mathematics: Ramanujan, "A proof of Bertrand's postulate" (1919, 2 pages, public
  domain). Deep learning: no licence could be confirmed without fetching; three candidates are ranked and marked
  **unconfirmed** (section 2.4), and no text is copied.
- **Recommendation (section 8).** Build a Lean **calculation layer** (`calc@0`): exact rational arithmetic over named
  values, rounding claims read from the printed digits, tables pinned by SHA-256 with counts and means, linear
  derivations with checked Farkas certificates, dimensions with a proved unit-change invariance theorem, exact
  statistics, and algebraic identities checked by a proved normaliser. Treat **mathematics beyond that** as a separate
  statement layer (`arith@0`) whose theorems are proved either by bounded evaluation in VE or by **imported Lean and
  Mathlib proofs of VE's own statement**, first as a pre-registered experiment. Do not grow VE's tableau into a proof
  assistant. Pilot the papers in the order **physics, then deep learning, then mathematics**, with VE's own paper as
  the calculation layer's first fixture source.
- **Honest ceiling.** A science paper's checked spine is its calculations, data, derivations and stated results.
  Exposition, motivation, apparatus narrative and figures stay labelled; the truth of measurements, the applicability
  of a physical law and the assumptions of a statistical test stay named residuals forever. Rough estimates
  (section 7): physics about 5% checked now, 20 to 31% after the plan, 40 to 50% ceiling; deep learning 4 to 8%, 14 to
  25%, 35 to 45%; mathematics about 0%, 10 to 20%, 85 to 90% (the last only with a Mathlib formalisation of each
  inequality); VE's own paper 0 to 1%, 16 to 28%, 40 to 55%.

## 1. What VE already has

### 1.1 Merged on `main` (`49de179e`)

| Piece | Where | What it gives a science paper | What it does not give |
|---|---|---|---|
| W3 definitions, biconditionals, alias definitions, lemma citation | `lean/VE/Definitions/*` (`faithful`, `conservative`, `conservative_entails`, `acceptance`, `Bundle.bundle_sound`), [STATEMENTS.md](../../lean/VE/Definitions/STATEMENTS.md), `ve/surface/definitions.py` | "By definition, for every point, that point is greatest exactly when ..."; "By T7a and T7b, ..."; one fresh unary or binary predicate per definition, no recursion | functions, numbers, recursive definitions |
| Closure induction | `lean/VE/Closure/Induction.lean` (`closure_induction`), [closure-induction.md](../spec/closure-induction.md), `usecases/closure-induction` | induction along the transitive closure of a relation (math mini-paper T9, T9e) | induction over the integers, well-founded induction, structural induction |
| Bounded n-ary relations (W4 stage 1) | `lean/VE/Core/*` (`NARY.md`), `nary@0` | `sum(a, b, c)` as a ternary relation | combination with `order@0`, flags or definitions (W4 stage 2) |
| `data@0`: total and functional binary relations, `$string` literals, `member` | [data-stage1.md](../spec/data-stage1.md) | "the r of t is v" for a total functional attribute: the relational form of a unary function; set membership with no set axioms | functions of several arguments, set comprehension |
| Adapter records (`glob@1`, `prefix@1`, `regex@1`) | data-stage1.md, "Adapter record boundary" | a recomputable table bound to input hashes, parameters and implementation hash | they run in Python, and their labels are not yet bound to leaves |
| `order@0` | `lean/VE/Order/*` (frozen, `lean/VE/Route/frozen-sources.sha256` lines 191-206) | ground linear integer arithmetic with integer cuts (`VE.Order.Lin`, `tighten_sound`) | integer quantifiers (`numbers2`, unmerged); rational unknowns; products of unknowns |
| W6a quantities, Lean-owned since lean-first batch 9 | `lean/VE/Time/*`, [units-schema.md](../spec/units-schema.md), [W6A-STATUS.md](../W6A-STATUS.md), [b9 LEDGER](../lean-first/b9/LEDGER.md) | exact decimals with no rounding (`decimal_exact`, `lower_render`), nominal unit tags (`ve-units@1`), homogeneous linear arithmetic with integer coefficients, dates (`temporal_iff`), counting sugar up to 8/7/7, certificates and countermodels (`checkW6Certificate_sound`); mode `quantity` | the schema says so itself (W6 1): "no real-number solver, dimensional algebra, automatic unit conversion, measurement evidence, probability logic"; no division, no product of two quantities, no scientific notation |
| W2 documents | [document.md](../spec/document.md), `lean/VE/Discourse/*`, `lean/VE/Service/Document.lean` | 100% span accounting; kinds `exposition`, `example`, `meta`, `hedged`, `attributed`; field `support ∈ {assumption, certificate, observation, calculation, statistical, testimony, adapter, none}`; open terms with deciders; reading sets | `support: calculation` and `support: statistical` are **labels only**: nothing checks them |
| `reports@0` (attribution) | `lean/VE/Attribution/*`, `lean/REPORTS.md` | "X says that P" with typed content; never factive | citation records; quotes checked against a source file |
| `risk@0` stage A | `lean/VE/Risk/*`, [risk.md](../spec/risk.md) | estimates as inclusive integer ranges with provenance; an append-only log whose entries Lean hashes with SHA-256 (`VE.Risk.entryHash`, `VE.CertificateWire.sha256`) | likelihood (stage B), numeric chances (stage C) |
| Claim graphs with provenance labels | `lean/VE/ClaimGraph.lean` | labels `asserted`, `bridge:accepts`, `background:`, `cite:`, `open:`, `readings:`, `narrowing:` travel to the report's assumptions | no label for a calculation or an import |
| Lean service | `lean/VE/Service/Protocol.lean` (32 modes; environment handles keyed by SHA-256) | one persistent checker; the recipe in `CLAUDE.md` for a relayed route | a data handle; requests are capped at 16,777,216 bytes per line (`maxLineBytes`) |
| Core `Rat` and `grind` | `lean/Iceberg.lean` (`import Std`, `abbrev Q := Rat`, `mul_sub ... := by grind`, `Rat.le_of_mul_le_mul_right`) | exact rationals and an algebra tactic are available in the pinned toolchain (`leanprover/lean4:v4.24.0`) without Mathlib | `lean/lake-manifest.json` has **no packages**: VE has no Mathlib, no real numbers, no `log` or `sqrt` |
| The iceberg experiment | `experiments/obfuscated-arguments/iceberg/VE.md`, `lean/Iceberg.lean` (a library outside the service) | a physics argument proved in Lean over rationals; VE checks only the relational shell, with the Lean results imported as premises | the correspondence between the Lean statements and the VE premises is "documented and agent-reviewed, not a proved translation" |
| Math mini-paper | `usecases/math-mini-paper/` | 18 of 19 queries certified in Python and Lean (definitions-report.md: 15 tableau certificates, T9 and T9e by closure induction, T7mono by citation); C1 false with a one-element countermodel; 26 checked countermodels | the paper is relational on purpose; GAPS.md G1 (functions), G3 (sets), G6 (arithmetic), G9 (reals and units) remain |

### 1.2 Building (in flight on 2026-10-12, from CURRENT-STATE.md and `git branch`)

Nothing in flight builds this topic. These items touch files a build of this plan would also touch, so the plan
orders around them (plan 6): `lean-first/b14a` to `b14d` (Lean-first wave 14; `b14d` adds a service mode, so it edits
`lean/VE/Service/Protocol.lean`, `ve/backends/service_schema.py` and the response-shape roots), `question-answering/q2`
(Lean-rendered English answers in `lean/VE/Ask/*`, also a new mode), `rd-9/integrate`, `readings-defaults/rd5`,
`mig3/lean` and `mig3/py` (migration stage 3), `fix/main-relay` (main has been red since `ts-B1`), `infra/ts-B2`,
the architecture items `infra/arch-AR-3`, `AR-4`, `AR-9`, `arch-20261010-1` and `-2`, and the English track
(`english-lean/e2-flip` merged as shadow; its E3 quantities batch, which takes over the numeral helpers of
`ve/surface/time.py`, has no branch yet). The six sibling research designs of this wave run in parallel; section 9
and plan 10 name what this design takes from each.

### 1.3 Planned only

- **VEX, mandatory evidence** (`design/vex-mandatory-evidence.md`): "statistical claims carry data + the test; the
  checker recomputes data → result"; "physical approximations become theorems with explicit error bounds". An idea,
  analysed, "not a plan". The **evidence layer** (`design/evidence-layer-design.md`) designs records, coherence and
  Fréchet bounds; only its mathematics exists, as Python tests (`tests/test_evidence_bounds.py`); no product module.
- **ROADMAP 5**: "Lean statement layer for mathematics: VE renders Lean theorem statements for sign-off; proofs stay in
  Lean; gaps: lemma citation, arity > 2, functions, relation parameters. After round 2." Two of its four gaps (lemma
  citation, arity above two) have since merged.
- **PLAN-EXPAND2 research track** (line 968): "real numbers and units beyond scaled decimals; ... probability inside
  formulas; second-order sets; general arithmetic induction".
- **VISION, converged rule 6**: "Proof imports: cited Lean lemmas as labelled premises with statement review, pinned
  versions and axiom audit. Not a checker change." Rule 7: "Sibling results enter deductions only through a verified
  bridge keeping assumptions and kind; otherwise they are external support." Rule 8 lists empirical truth as outside
  certification for ever.
- **W6b** (gated on `numbers2`): integer binders, weekday arithmetic, finite traces.
- **NORTH-STAR**: rows M, H, DL (lead-added 2026-10-12, weight 3 each, "unmeasured"), V (weight 3, "unmeasured;
  estimated candidate gaps: definitions-in-prose, citations, attribution, evidence/statistical claims, quantities,
  discourse"), D (weight 3). Feature rows "Functions, sets/relation parameters, general arithmetic/induction" and
  "Statistical evidence, analogy and legal-authority arguments", both "unknown estimate". The 2026-10-07 coverage
  estimate puts VE's own paper and docs at 0%, "Dec; needs math backlog".

### 1.4 The rules any extension must follow

VISION's converged rule, as it bears here: elaborate into existing profiles by default; existing routes, identities and
theorem statements never change (so `order@0`, frozen, cannot be widened to rationals, and `ve-units@1` cannot gain
dimensions in place); a new profile needs explicit semantics, conservativity, certificate soundness, model validity so
that NO and UNKNOWN survive, gate theorems, statement review and a trust-cost line; empirical truth, interpretation
choices and open-term adjudication stay outside certification. `CLAUDE.md` adds: Lean owns every verdict, diagnostic
and derived value; Python does the command line, files, display, schema and binding only; Rust is an untrusted
accelerator; one owner per piece of logic.

## 2. The need, measured

### 2.1 Method

- Constitution: `pilots/claude-constitution/run-20261012T1800Z/units.json` (1,132 units, 184,893 bytes),
  `coverage.json`, `SUMMARY.md`, `FEATURE-REVIEW.md`. UDHR: `pilots/udhr/run-20261012T1800Z/units.json` (130 units,
  10,916 bytes), `coverage.json`, `SUMMARY.md`.
- "Primary blocker" is a unit's `missing_feature`; "co-blocker" is an entry of `other_blockers`. This topic would
  appear under tags such as evidence, statistics, mathematics, calculation, equations, empirical, numbers, arithmetic.
- Use cases: the five `usecases/*/GAPS.md`. New targets: section 2.4. VE's own paper: `paper/sections/*.md`.

### 2.2 The pinned pilots

**Tags.** The constitution's `unformalised_reasons` are attribution 12, causation 76, counting 31, defaults 50,
modality/belief 25, norms 669, other.discourse 81, other.graded-force 1, other.open-list 1, quantities 119, time 9
(`coverage.json`). The UDHR's primary tags are causation, attribution, modality/belief, norms, time, defaults,
quantities (1 unit, u097), and `other:` tags for act-phrase grammar, comparison, metaphor, evaluative claims, rights
lines, authority and priority. A search of both ledgers for a blocker tag named evidence, statistics, mathematics,
calculation, equation(s), empirical, science, probability, numbers or arithmetic returns **no match**.

| Pilot | Units, primary | Bytes, primary | Units, co-blocker | Bytes, co-blocker |
|---|---:|---:|---:|---:|
| Constitution (1,132 units, 184,893 B) | 0 | 0 | 0 | 0 |
| UDHR (130 units, 10,916 B) | 0 | 0 | 0 | 0 |

The `quantities` tags (constitution 119 primary; UDHR 1) belong to the sibling quantities design, which owns
quantities, graded comparison, vague degrees and counting.

**Word-level overlap.** A case-insensitive search of the constitution ledger for evidence, statistic, empiric,
probability, experiment, percent, equation, mathematic, proof, theorem and calculat matches 17 lines. Read one by one,
12 units use "evidence", "probability" or "empirical" as an **epistemic standard on Claude's own judgement** ("clear
evidence", "evidence is overwhelming", "calibrated uncertainty"); the other five are "calculated bet" (u0004.s02),
"run experiments" (u0030.s03), "thought experiments" (u0085.s08), "research and experimentation" (u0275.s01) and the
hard-constraint guard text (attitudes' "thinks it quite likely"). The table adds u0147.s04 by hand: it has none of the
words but is the ledger's one hypothetical frequency.

| Unit | Bytes | Excerpt (start) | Owner |
|---|---:|---|---|
| u0052.s02 | 233 | "Claude might reasonably trust the outputs of a well-established programming tool unless there's clear evidence it is faulty" | attitudes / weighing |
| u0112.s03 | 202 | "Calibrated: Claude tries to have calibrated uncertainty in claims based on evidence and sound reasoning" | attitudes |
| u0112.s08 | 279 | "Non-manipulative: Claude relies only on legitimate epistemic actions like sharing evidence, providing demonstrations" | norms / attitudes |
| u0135.s01 | 117 | "The probability that the action leads to harm at all" | risk stage B / attitudes |
| u0147.s04 | 170 | "even if only 1 in 1,000 (or 1 in 1 million) users could use them to cause harm to others" | quantities (W6 fixture CRATIO) / risk |
| u0198.s03 | 428 | "respecting the current state of evidence and uncertainty" | attitudes |
| u0199.s02 | 198 | "the same interest, rigor, and humility that we would want to apply to empirical claims" | norms |
| u0200.s03 | 169 | "discovers evidence that an operator is orchestrating a massive financial fraud" | events / attitudes |
| u0201.s02 | 266 | "that the evidence is conclusive, that intervention is the best response" | weighing |
| u0202.s01 | 130 | "Unlike a human employee who discovers similar evidence" | attitudes |
| u0203.s02 | 127 | "reserve independent action for cases where the evidence is overwhelming" | weighing |
| u0218.s12 | 236 | "less flagrant and lower-probability versions" | risk / attitudes |
| u0264.s03 | 401 | "human ethical agents can encounter evidence of their own mistakes" | attitudes |

Sum without u0147.s04: 233 + 202 + 279 + 117 + 428 + 198 + 169 + 266 + 130 + 127 + 236 + 401 = **2,786 B over 12
units**; with it, 2,956 B over 13 units. This design unlocks **none** of them: none states a measured value, a
calculation or a cited result; each is a norm about how Claude should weigh evidence or risk. The UDHR has no such
unit.

### 2.3 Use cases (`usecases/*/GAPS.md`): evidence of need, not pilot bytes

| Use case | Gap | Status today |
|---|---|---|
| Math mini-paper | G1 functions, G2 arity above two, G3 sets and relation parameters, G4 definitions and citation, G5 induction, G6 numbers, G7 biconditional, G8 restricted quantifiers, G9 reals and units, G10 proof search | G2, G4, G7, G8 and closure-specific G5 merged; **G1, G3, G6, G9 and general G5 open** (the definitions-report rerun: 18/19). The boundary probe (`boundary.md`) shows Euclid's statement "parses, type-checks, canonicalises, hashes, and reads correctly in English" and "is also worthless" without arithmetic. |
| News article | Numbers and arithmetic, 7 of 26 rows | W6a made rows 7, 13, 21, 22, 23 DIRECT (`coverage-w6a.md`); rows 7b and 22b stay NO (a missing operand) |
| Birthright debate | 1. Evidential/empirical claims, 3 of 9 claims, "very high importance": "roughly 10% of U.S. births involve a non-citizen parent" | open; the GAPS file's own direction is "an evidence/citation binding ... reify a cited statistic as a typed fact with provenance ... checked for internal consistency with other stated facts, but never verified against the world by VE itself" |
| Constitution excerpt, 14th Amendment | none in this topic | — |

### 2.4 Step 0: the pinned target texts

Selection rules from the brief: short (ideally under about 20 pages), representative of the field, and storable
(public domain or CC-BY). Licence status below rests on publication date and authors' deaths, which I know; source
URLs are from memory and **unconfirmed** until ME-0 fetches them without a model.

| Use case | Pick | Why | Licence | Source | Size (estimate) |
|---|---|---|---|---|---|
| **Physics (H)** | A. A. Michelson and E. W. Morley, "On the Relative Motion of the Earth and the Luminiferous Ether", *American Journal of Science*, 3rd series, vol. 34, no. 203, pp. 333-345, November 1887 | units (meters, wave-lengths, fractions of a fringe), equations (the travel times and path difference), an experiment with tables of readings, and a quantitative conclusion with graded hedges ("certainly less than ... probably less than"); the most cited null result in physics | **public domain**: published 1887 (public domain in the United States); Michelson died 1931, Morley 1923, so it is free in every country with a term of life plus 90 years or less | Wikisource, "On the Relative Motion of the Earth and the Luminiferous Ether" (URL **unconfirmed**); DOI 10.2475/ajs.s3-34.203.333 | 13 pages; about 30-40 KB of text and tables |
| Physics, alternate | A. Einstein, "Does the Inertia of a Body Depend upon its Energy-Content?" (1905), translation by W. Perrett and G. B. Jeffery in *The Principle of Relativity* (Methuen, 1923) | 3 pages: a thought experiment, a derivation by expansion "neglecting magnitudes of fourth and higher orders", the ergs-and-grammes statement of mass-energy, and a proposed test with radium salts | the 1923 translation is public domain in the United States; outside it the translators' terms may still run (Jeffery died 1957) — **unconfirmed** for storage outside the US | Wikisource (unconfirmed) | about 7 KB |
| **Mathematics (M)** | S. Ramanujan, "A proof of Bertrand's postulate", *Journal of the Indian Mathematical Society* 11 (1919), 181-182; reprinted in *Collected Papers of Srinivasa Ramanujan* (Cambridge, 1927) | a complete research note: definitions by sums over primes, a chain of identities and inequalities, the theorem, "by actual verification" for small values, and a corollary now called Ramanujan primes; Mathlib proves the main theorem by another route (`Nat.bertrand`, from memory), which makes it the natural test of proof imports | **public domain** everywhere: published 1919; Ramanujan died 1920 | Wikisource or the 1927 *Collected Papers* (URL **unconfirmed**) | 2 pages; about 4-6 KB |
| Mathematics, alternate (sets, functions, induction) | R. Dedekind, *Was sind und was sollen die Zahlen?* (1888), §§1-6, in W. W. Beman's translation *Essays on the Theory of Numbers* (1901) | systems, mappings and chains: Dedekind's chains are VE's closures, and his complete induction is VE's closure induction; exercises the missing "sets as parameters, general functions, general induction" directly | public domain: 1901 translation; Dedekind died 1916, Beman 1922 | Project Gutenberg (URL **unconfirmed**) | a §§1-6 slice of about 20 pages |
| **Deep learning (DL)** | **No pick confirmed.** Ranked candidates, all **licence unconfirmed**: (1) E. Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models" (arXiv 2106.09685; ICLR 2022); (2) T. Darcet et al., "Vision Transformers Need Registers" (arXiv 2309.16588; ICLR 2024); (3) J. Jumper et al., "Highly accurate protein structure prediction with AlphaFold", *Nature* 596 (2021) 583-589 | (1) a method stated by equations, parameter counts, many result tables against baselines, ablations and hedged hypotheses, about 12 pages of main text; (2) a shorter empirical paper with tables and baselines but few equations; (3) open access, probably CC BY 4.0 (from memory), but a science-application paper with its equations in the supplement | ME-0 checks the licence field of each arXiv abstract page (or OpenReview, or the journal page) and takes the first CC-BY one; if none qualifies, DL stays unpinned and the plan's DL batches wait | none fetched | — |

"Attention Is All You Need" (Vaswani et al., 2017) would be the most representative deep-learning paper, but as far
as I recall it carries arXiv's non-exclusive licence plus a permission notice limited to tables and figures, so it
cannot be stored; it is not a candidate.

### 2.5 Sentence kinds per target

For H, M and DL these are **estimates from memory of the texts**, to be replaced by ME-0's measured partition. For V
they are measured: `wc -c` and `wc -l` on `paper/sections/*.md`, and a ripgrep count of lines containing a fraction
(`\d+/\d+`), a two- or three-place decimal, a percentage, "p = ", "interval" or a bracketed signed decimal.

| Kind | Physics (Michelson-Morley) | Mathematics (Ramanujan) | Deep learning (LoRA as a structural proxy) | VE's paper (measured where stated) |
|---|---|---|---|---|
| Definitions | 2-4 (the symbols V, v, D, T) | 3-4 (the two prime sums, the counting function, notation) | 3-5 (the update, the scaling factor, notation) | 3-5 (FA, HA, balanced accuracy, d′, c) |
| Theorems, lemmas, proof steps | 0 | 1 theorem, 1 corollary, about 12 numbered formulas, about 10 proof-step sentences | 0 | 0 |
| Equations and derivation steps | about 8 (travel times, path lengths, the difference, the displacement, two expansions to second order) | most of the paper | 3-6 (the method; a similarity measure; parameter counts) | 2-3 |
| Quantities with units | about 15-25 (meters, wave-lengths, minutes, the stone's size, dates, fringe fractions) | 0 | about 15-30 (parameter counts, ranks, learning rates, GPU memory, hours) | about 10 (tokens, seconds) |
| Data tables | 2 tables of readings at 16 azimuths, with means | 0 | about 5-8 result tables | 11 included generated tables; the appendix tables are 36,111 B |
| Empirical claims | about 6 | 0 | about 15-25 | most numeric lines |
| Comparisons with baselines or expectations | about 4 (observed against expected displacement) | 0 | about 15-25 | about 20 contrasts |
| Statistical results (p-values, intervals, SD) | 0 (means only) | 0 | a few (spread over seeds) | measured: 55 of 554 main-text lines and 131 of 556 appendix lines carry such a number |
| Hedges | about 5 ("certainly", "probably", "it seems fair to conclude") | 1-2 ("it is easy to see") | about 5-10 ("we hypothesize", "suggests") | many ("compatible with", "does not exclude") |
| Citations | about 8 (Fresnel, Stokes, Lorentz, Fizeau, Michelson 1881) | 2 (Landau's *Handbuch*, Chebyshev) | about 50 | about 30 |
| Exposition, apparatus and procedure narrative | about 60% of the text | about 15% | about 45% | about 55% |

VE's paper: 73,801 B over eleven section files: 37,619 B in the main sections (00 to 08), 71 B in the reference stub
(09) and 36,111 B in the appendices (10), measured with `wc -c`. The line counts (554 main, 556 appendix) are `wc -l`;
the numeric-line counts by file are 00: 2, 02: 1, 04: 35, 05: 7, 06: 7, 07: 3, 10: 131 (186 in all).

### 2.6 Representative sentences

Unit ids are given for the pinned pilots. Target sentences are **paraphrases from memory** (marked) and VE paper
sentences are exact quotes from the repository.

| # | Source | Sentence | This design |
|---|---|---|---|
| 1 | Constitution u0203.s02 | "We think Claude can reserve independent action for cases where the evidence is overwhelming and the stakes are extremely high." | **No.** An epistemic threshold on Claude's judgement: weighing and attitudes. |
| 2 | Constitution u0112.s03 | "Calibrated: Claude tries to have calibrated uncertainty in claims based on evidence and sound reasoning, ..." | **No.** A norm about belief (defaults, attitudes). |
| 3 | Constitution u0147.s04 | "... decline to assist with them even if only 1 in 1,000 (or 1 in 1 million) users could use them to cause harm to others." | **No.** A hypothetical frequency in a norm (quantities, risk). The calculation layer could state the ratio, but the unit's force is normative. |
| 4 | UDHR u097 | "Education shall be free, at least in the elementary and fundamental stages." | **No.** A bound over ordered stages (quantities). |
| 5 | Math mini-paper, `boundary.md` | Euclid: "N = p₁ · p₂ · … · p_k + 1" | **Partly.** The statement layer `arith@0` can state "for every whole number there is a larger prime"; the product of an unknown list of primes needs a fold over a list, which stays research (plan EX-4). |
| 6 | Math mini-paper, GAPS G9 | "p = mv, F = dp/dt, in SI units" | **Partly.** `p = mv` with physical dimensions: yes (plan ME-6). A derivative: no (real analysis). |
| 7 | Birthright debate, GAPS 1 | "roughly 10% of U.S. births involve a non-citizen parent" | **Partly.** The ratio with its provenance and "roughly" as a reading set: yes; its truth: never. |
| 8 | VE paper, 04-e1.md | "Its scored baseline, 176/594 = .296, is outside the gate band." | **Yes.** 176/594 = 8/27 = 0.2963 rounds to .296 and lies below the band's lower end .30 (plan ME-1). Recounting 176 and 594 from the 21 MB trial file needs chunked data handles (plan EX-5); a committed count table serves meanwhile (plan ME-4). |
| 9 | VE paper, 04-e1.md | "false approval is 52/243 (.214) versus 31/243 (.128), an 8.6-point pooled increase." | **Yes.** 52/243 rounds to .214, 31/243 to .128, and 21/243 = 7/81 = 8.64 points rounds to 8.6 (plan ME-1). |
| 10 | VE paper, appendix | "SD between templates 0.108 ... SE with 12 templates 0.031 ... 97.5% half-width with 12 (t = 2.593) 0.081", from the twelve printed per-template differences | **Yes**, with a twist: the printed SD matches the sample SD (n − 1), not the population SD (n), which gives 0.103. "SD" is a two-reading word that the calculation distinguishes (plan ME-7, fixtures V-6 and V-6r). |
| 11 | Physics, paraphrase from memory | "The distance D was about eleven meters, or 2 × 10⁷ wave-lengths of yellow light; hence the displacement to be expected was 0.4 fringe. The actual displacement was certainly less than the twentieth part of this, and probably less than the fortieth part. ... the relative velocity of the earth and the ether is probably less than one sixth the earth's orbital velocity, and certainly less than one-fourth." | **Mostly.** 2 × (2 × 10⁷) × (10⁻⁴)² = 0.4 (plan ME-1); from "displacement is proportional to the square of the velocity" and "less than one twentieth", the bound "less than one fourth" follows because (1/4)² = 1/16 > 1/20 (plan ME-5); the "probably" pair follows the same way, (1/6)² = 1/36 > 1/40, but its hedge is the attitudes design's. "About eleven meters ... 2 × 10⁷ wave-lengths" needs the wavelength of yellow light, which the text does not give: an explicit premise. |
| 12 | Mathematics, paraphrase from memory | "Thus Bertrand's postulate is proved for all values of x not less than 162; and, by actual verification, we find that it is true for smaller values." | **Yes for the finite part** (bounded evaluation in `arith@0`); **the general theorem by import** if the Mathlib experiment passes (EX-1); Ramanujan's own analytic inequalities stay residual. |

### 2.7 What the numbers say

The pinned pilots do not need this design, and the plan must not claim otherwise. Its value is measured on
denominators that do not exist yet: three new texts and VE's own paper. So the first batch is a measurement (pin the
texts, partition them, record what today's VE checks), and the NORTH-STAR rows for M, H and DL stay "unmeasured" until
it lands. The VE paper is the cheapest denominator: it is in the repository, it is ours, and its numbers can be bound
to trial files that are also in the repository (`experiments/E1/runs/e1-scored-0921/trials.jsonl`, 20,975,471 B;
`paper/generated/posthoc-e1.json`, 11,096 B).

## 3. Prior art

Authors and years are from memory; anything I am unsure of is marked.

### 3.1 Formal semantics of mathematical and scientific language

- **Montague** ("English as a formal language", 1970; "The proper treatment of quantification", 1973) showed that a
  fragment of English can be given a model-theoretic semantics compositionally. **Kamp's** DRT (1981; Kamp and Reyle
  1993) handles anaphora across sentences, which mathematical prose uses constantly ("let x be ...; then x ...").
- **Ganesalingam**, *The Language of Mathematics* (Springer LNCS 7805, 2013), analyses how mathematicians'
  language is disambiguated by types and by the reader's knowledge of what objects are, and how much ambiguity real
  texts carry (for example `(a, b)` as a pair, an interval or a gcd). His conclusion that disambiguation needs a type
  system and that a fixed parser cannot guess is VE's "one reading or a reading set".
- **Ranta**, *Type-Theoretical Grammar* (1994) and Grammatical Framework (2004; book 2011): multilingual grammars over
  an abstract syntax, used for mathematical exercises (the WebALT project, about 2006, from memory) and as a
  front end to proof systems.

### 3.2 Controlled languages for mathematics and science

- **Mizar** (Trybulec, from 1973; Grabowski, Korniłowicz and Naumowicz, "Mizar in a nutshell", 2010): a readable
  proof language with a large library; texts read almost like mathematics but are Mizar, not English.
- **ForTheL and SAD** (Lyaletski, Paskevich, Verchinine, about 2002-2008) and **Naproche** (Koepke, Cramer, Schröder
  and others, from about 2009; Naproche-SAD; later an Isabelle component, about 2020, from memory): controlled
  natural language for mathematical texts, checked step by step with first-order provers. They show that theorem-proof
  texts can be written in checked controlled language. They accept the prover's "yes" without a certificate a small
  kernel replays (as far as I know), and they accept LaTeX formulas inside sentences.
- **MathNat** (Humayoun and Raffalli, about 2010, unsure of the venue) and **Verbose Lean** (Massot, about 2023,
  unsure of the date): controlled-English front ends to proof assistants, mainly for teaching.
- **Attempto Controlled English** (Fuchs, Kaljurand, Kuhn; from 1995) with its DRS semantics and the RACE reasoner;
  ACE admits numbers and simple arithmetic. **PENG** (Schwitter, 2002; PENG-ASP later). Kuhn's survey (*Computational
  Linguistics* 40(1), 2014) classifies CNLs; none of them targets measured quantities or statistical results.
- **OMDoc** (Kohlhase, 2006), **MMT** (Rabe and Kohlhase, 2013) and **sTeX**: semantic markup for mathematical
  documents with theories, definitions, theorems, proofs, examples and plain text as typed units. The closest prior
  art to VE's unit kinds for papers.
- **Lean blueprints** (Massot's `leanblueprint`, used by the PFR project in 2023): an informal document whose
  statements are linked to Lean declarations, with a dependency graph. Linking is by hand; nothing checks that the
  English statement means the Lean one.

### 3.3 Proof assistants, certificates and numbers

- **LCF** (Milner, 1972) and the de Bruijn criterion: an untrusted search, a small trusted checker. **Proof-carrying
  code** (Necula, 1997). **Lean 4** (de Moura and Ullrich, CADE 2021) and **Mathlib** (The mathlib Community, CPP 2020).
- Certificates for arithmetic: simplex with Farkas certificates in SMT (Dutertre and de Moura, CAV 2006); sums of
  squares for nonlinear real inequalities (Harrison, TPHOLs 2007); the Flyspeck proof's nonlinear inequalities (Hales
  and others, 2017). **Interval arithmetic** (Moore, 1966) and validated numerics (Tucker, 2011); Coq's Interval
  library (Melquiond, IJCAR 2008).
- **Autoformalisation** (Wu and others, NeurIPS 2022; ProofNet, Azerbayev and others, 2023; miniF2F, Zheng and others,
  2022): models translate statements into Lean; the measured bottleneck is the faithfulness of the formal *statement*,
  not the proof. VE's paper reports the same problem from the other side (E1).

### 3.4 Units and dimensions

- **Buckingham** (1914, the π theorem) and **Bridgman** (*Dimensional Analysis*, 1922): a dimensionally homogeneous
  equation keeps its truth under any change of base units; that invariance is the theorem dimensional analysis rests
  on. **Hart**, *Multidimensional Analysis* (1995).
- **Kennedy**: units of measure as types (POPL 1997; F# units of measure, about 2009-2010): dimension inference is
  unification in an abelian group, decidable and cheap. Libraries: Boost.Units, Python `pint`, Rust `uom`.
- **SI Brochure**, 9th edition (BIPM, 2019); **UCUM** (Schadow and McDonald); **QUDT**. A sound type system for units
  in Isabelle (Foster and Wolff, about 2020, **unsure**); physics in Lean 4 with Mathlib (HepLean, Tooby-Smith, 2024,
  later renamed PhysLean, **unsure**).

### 3.5 Reproducibility, provenance and statistical checking

- **Literate programming** (Knuth, 1984), Sweave (Leisch, 2002) and knitr (Xie, 2014): numbers in a paper produced by
  the code that computed them. They keep the computation honest but do not check the prose against it.
- **W3C PROV** (2013); **nanopublications** (Groth, Gibson and Velterop, 2010): an assertion with its provenance and
  publication record; **micropublications** (Clark, Ciccarese and Goble, 2014): claims, evidence, support and
  challenge in biomedical papers; the **Open Research Knowledge Graph** (Jaradeh and others, 2019); **AxCell**
  (Kardas and others, EMNLP 2020) extracting result tables from machine-learning papers. They structure claims and
  evidence; none gives a claim one checked meaning.
- **statcheck** (Epskamp and Nuijten's R package; Nuijten and others, *Behavior Research Methods* 2016) recomputes p
  values from reported test statistics in psychology papers. From memory: about half of papers with significance tests
  had at least one inconsistent p value and about one in eight a gross one. **GRIM** (Brown and Heathers, 2017) checks
  that a mean of integer data is possible for the reported sample size; **SPRITE** (Heathers and others, 2018)
  reconstructs samples. These checks find real errors with nothing but arithmetic on the printed numbers, the same
  thing this design does in Lean with one reading per number.
- The **NeurIPS reproducibility programme** and checklist (Pineau and others, *JMLR* 2021): the deep-learning field's
  own statement of what an empirical claim must carry (data, code, seeds, variance).
- **Catala** (Merigoux, Chataing and Protzenko, ICFP 2021): exact decimals and money with explicit rounding. Rounding
  is a declared rule, never silent.

### 3.6 Logic programming and arithmetic

**CLP(Q) and CLP(R)** (Jaffar and Lassez, 1987; Holzbaur, 1995) decide linear constraints over exact rationals;
**provenance semirings** (Green, Karvounarakis and Tannen, PODS 2007) give query answers a record of the facts they
came from. Both carry over directly: linear derivations over rationals, and every computed number bound to its inputs.

### 3.7 What carries over, and what conflicts with VE's constraints

| Idea | Carries over | Conflicts |
|---|---|---|
| Checked controlled language for proofs (Naproche, ForTheL) | statements and steps as units; per-step checking | formulas inside sentences (zero-training); a prover's unreplayed "yes" (small trusted checker) |
| Proof assistants and Mathlib | the kernel; a library of proved facts; certificates | Lean is not zero-training English; Mathlib is large: depending on it would grow VE's build and trusted tree |
| Statement-level faithfulness (blueprints, autoformalisation) | the gap VE exists for | linking by hand; nothing checks the English |
| Units as types (Kennedy, SI, UCUM) | dimensions form an abelian group; checking is decidable | unit symbols in what people read; affine units (degrees Celsius) |
| statcheck and GRIM | recompute printed numbers; flag inconsistencies, never fix them | regular-expression parsing of free text (one reading); assumed conventions |
| Nanopublications, micropublications, PROV | claim plus provenance plus support | free-text assertions with no checked meaning |
| Catala's exact decimals | rounding declared | — |
| CLP(Q), Farkas certificates | exact linear reasoning over rationals | — |
| Interval arithmetic, sums of squares | bounds on irrational values by rational certificates | proofs about real functions need real analysis |

## 4. Candidate designs

Each is judged against the constraints of the brief: one reading per sentence, zero-training English, a small
Lean-proved core grown only by proved conservative extensions with untrusted provers supplying certificates, honest
UNKNOWN, and open terms with deciders.

### D1. Labels and assertions only (today's language, used fully)

Exposition is LABELLED; a measured value is a W6a quantity asserted with `support: observation`; a computed value is
asserted with `support: calculation` and is not checked; citations are `reports@0` reports; equations are written as
`defined` predicates over reified quantities. **For**: no new code; honest. **Against**: the one thing a science
paper's reader can check mechanically, its arithmetic, stays unchecked; `support: calculation` remains a label that
anyone can attach to a wrong number; equations as predicates are worthless in exactly the way the Euclid probe showed.

### D2. A Lean calculation layer, `calc@0` (recommended for physics, deep learning and VE's paper)

A new profile and service mode, owned by Lean, whose meaning is exact rational arithmetic:

1. **Named values** with a source: stated by the text, defined by an expression, counted or averaged from a pinned
   table, or left free (unknown).
2. **Claims**: equals, is less than, is at most, lies from ... through ..., and "is p when rounded to d places" (the
   precision read from the printed digits: "0.30" is two places; the tie rule explicit). Verdicts: holds, fails,
   undefined (a missing value, a zero divisor) and unknown (a limit). A claim that fails in a translated source is a
   **finding about the source** (as statcheck reports), not a rejection of the translation.
3. **Tables pinned by SHA-256**, with filters and counts, sums, means, minima and maxima.
4. **Derivations with unknowns**: linear inequalities over rationals, certified by Farkas multipliers that Lean finds
   and checks, plus one proved rule for squares ("from 0 ≤ x, x² < a and a ≤ b², with b > 0, infer x < b").
5. **Dimensions**: a unit declares integer exponents over base dimensions and an exact factor; addition and comparison
   need equal dimensions; the proved theorem is unit-change invariance.
6. **Exact statistics**: proportions, differences, means, sample variance, standard deviation and standard error by
   squared bounds, exact sign-flip p values, exact binomial tails, Cohen's kappa; each test's assumptions as named
   residual leaves.
7. **Printed-number consistency**: given that inputs were rounded, is there an assignment within the rounding
   intervals that yields the printed outputs (a witness, checked exactly), or is there none (a proof by interval
   enclosure)? GRIM and statcheck, in Lean.
8. **Algebraic identities**: a proved normaliser for polynomials and rational functions over ℚ, so derivation steps
   such as "D/(V − v) + D/(V + v) = 2DV/(V² − v²)" are certified with their nonzero side conditions.

**Fit**: one reading per value and per claim (the precision is read from the printed digits; "about" is a reading set);
English made of fixed phrases ("the product of A and B", "A divided by B", "the square of A", "rounded to three
decimal places"), names for intermediate values instead of nested formulas, and a formula view only as an optional
display; a small core: exact rationals, `Rat` and `grind` from core Lean, no Mathlib; Farkas and witness certificates
are found by Lean and replayed by Lean; honest UNKNOWN when a search exceeds its budget or a value is irrational and
not bounded; no open term is decided (a "close enough" stays open). **Against**: real analysis is out (logs,
derivatives, integrals); a large data file exceeds the service's line cap (16 MB) and needs chunked handles.

### D3. A mathematics statement layer with proof imports, `arith@0` (recommended for mathematics, as an experiment first)

Statements about whole numbers and integers: addition, multiplication, divisibility, order, functions and predicates
defined by non-recursive terms and formulas, bounded and unbounded quantifiers. The meaning is a `Prop` defined in
VE's own core-Lean module (`VE.Arith.Holds`). Two ways to prove: (a) **bounded evaluation** in VE for statements
whose quantifiers are bounded ("for every whole number n from 1 to 161 there is a prime p with n < p ≤ 2n"); (b) an
**import**: a separate Lake project that requires Mathlib and VE proves `theorem t : VE.Arith.Holds ... s` for VE's
own statement `s`, with `#print axioms` inside the allowlist; VE records the pinned toolchain, Mathlib revision,
declaration and axioms, and the import enters reports as a labelled residual leaf (`import:...`), exactly VISION rule 6.
**For**: the statement a reader approves *is* the statement Lean proves (no hand translation, the iceberg's gap);
VE's trusted runtime does not grow; Mathlib's thousands of theorems become usable. **Against**: Mathlib's build and
disk cost; bridge lemmas per vocabulary item (VE's `prime` against Mathlib's `Nat.Prime`); reals (logs, Γ) need the
meaning function itself to live on the Mathlib side, outside VE's core; an import is trusted as a pinned external build,
not replayed by `ve_service`.

### D4. Grow VE's own logic into a mathematical prover

Function symbols, sets, recursion, general induction and real arithmetic inside the tableau and its Lean metatheory.
**Rejected**, for the reasons the math mini-paper's boundary study gave (`boundary.md` 5): it converges on
re-implementing a dependently typed proof assistant with a larger trusted checker; function symbols defeat finite
countermodel search, VE's most valuable single feature there; recursive definitions do not render as one-reading
English phrases; Mathlib has already done the work.

### Trade-offs

| Constraint | D1 labels | D2 `calc@0` | D3 `arith@0` + imports | D4 grow the prover |
|---|---|---|---|---|
| One reading per sentence | yes | yes; printed precision fixes rounding; "about" becomes a reading set | yes; variable domains (whole numbers or reals) become reading sets | yes, at large cost |
| Zero-training English | yes | yes, with names for intermediate values; formula view optional | yes for statements; proofs stay in Lean, unread | no for recursion |
| Small Lean-proved core | unchanged | grows by one profile: exact arithmetic, tables, Farkas, dimensions, normaliser (estimate 3,000-5,000 Lean lines with proofs) | grows a little (meaning, bounded evaluation, import record); Mathlib stays outside | grows without bound |
| Untrusted provers supply certificates | — | Farkas multipliers, witnesses and enclosures, found by Lean, checked by Lean | Mathlib proofs, checked by the Lean kernel in a pinned build | tableau certificates |
| Honest UNKNOWN | — | budgets; irrational values without bounds | unbounded statements without an import | yes |
| Open terms stay open | yes | yes ("close enough", "on par") | yes | yes |
| Unlocks science bytes | almost none | most calculations, data, derivations and results | theorems and finite checks | in principle everything, in practice nothing soon |

## 5. How far VE can go, kind by kind

**Definitions and lemmas, with untrusted-prover certificates, and Lean/Mathlib.** Relational definitions and citations
are merged (W3). Definitions of *numeric* values ("the expected displacement is twice the path length times the
square of the speed ratio") are `calc@0` definitions: non-recursive expressions in earlier names, checked acyclic.
Definitions of *arithmetic predicates* ("p is prime exactly when ...") are `arith@0` definitions with the same rule.
Lemmas about integers are proved by bounded evaluation, or imported from a Mathlib project that proves VE's own
statement. Relation to Lean and Mathlib: VE's checker deliberately builds without Mathlib (`lean/lake-manifest.json`
lists no packages), which keeps its build and trusted tree small; Mathlib is the natural untrusted prover and library,
reached through an import project, never linked into `ve_service`. Replaying imported proofs inside the service (in
the style of `lean4checker`) is a later option once import sizes are measured.

**Dimensional analysis as a checkable layer.** Yes, fully: dimensions are integer exponent vectors, inference is
exact, and the theorem worth proving is that a dimensionally consistent equation or inequality keeps its truth under
every change of base units (Buckingham and Bridgman's invariance). Affine units (degrees Celsius) and logarithmic
units (decibels) are excluded and rejected by name. The quantities design leaves "products and quotients of units
(rates, 'per', physics)" to this design's physics pilot (its research 5.2) and plans declared conversions in a
`ve-units@2` (its QT-A7); one registry for both is plan 10, piece 3.

**Equations as relations over declared quantities.** Ground equations: decided exactly. Equations with unknowns:
linear ones by Farkas certificates; one nonlinear step (squares) by a proved rule; polynomial and rational identities
by a proved normaliser. Physical laws ("the displacement is proportional to the square of the velocity") enter as
named premises, never as truths. Nonlinear inequalities in general (sums of squares) and approximations with error
terms are research (EX-2), though exact remainders often make "neglecting terms of the fourth order" exact: the
difference between 2DV²/(V² − v²) and 2D(1 + v²/V²) is exactly 2D(v/V)⁴/(1 − (v/V)²).

**Reproducible calculations.** Yes: the core of D2. A computed number in a paper becomes a claim Lean recomputes
from named inputs; inputs come from the text (support `observation` or `testimony`) or from a pinned table (support
`calculation`, checked).

**Statistical and empirical claims, with assumptions and evidence provenance.** The *computation* of a statistic from
data is checkable exactly when the statistic is a rational function of the data or has a rational characterisation
(squared bounds for square roots, exact enumeration for permutation tests, exact binomial sums). Quantiles of
continuous distributions (Student's t, the normal) are used as stated constants with provenance (a cited table value)
until interval bounds are researched. The *assumptions* (independence, exchangeability, a model's form) are named
residual leaves, as VE's own paper already writes them ("exact only conditional on independent, sign-exchangeable
template residuals"). The *truth* of data (that the trials happened as recorded) is never checked: a data file's
SHA-256 binds a claim to bytes, not bytes to the world. VEX's probability propagation (Fréchet bounds, coherence) is
not needed by papers that report results rather than weigh testimony; it stays with the evidence-layer design.

**What stays labelled exposition.** Motivation, history, related-work narrative, apparatus description beyond its
numbers, figure captions, acknowledgements, and the paper's prose interpretation of its own results ("this suggests").
In VISION's words, the target is a checked spine, not every sentence formal.

## 6. Buildable now, research, residual

Rough unlock figures are **estimates** in bytes of the target texts, whose sizes are themselves estimates until ME-0
(physics about 35 KB, mathematics about 5 KB, deep learning proxy about 50 KB; VE's paper 73,801 B measured). On the
pinned constitution and UDHR every row below unlocks **0 B**.

| Part | Status | Physics | VE's paper | Deep learning | Mathematics |
|---|---|---:|---:|---:|---:|
| Pin the texts and measure today's coverage (W6a facts, attributions, labels; dates before 1970 are outside W6) | buildable now, no code | 1.5-2.5 KB | 0.3-0.8 KB | 2-4 KB | 0 |
| Ground calculations with rounding (`calc@0` core and mode) | buildable now | 0.6-1.0 KB | 0.8-1.5 KB | 0.5-1.0 KB | 0 |
| Tables pinned by digest; counts, sums, means | buildable now | 2.5-3.5 KB | 1-2 KB | 3-5 KB | 0 |
| Linear derivations with Farkas certificates; the square rule | buildable now | 0.5-1.0 KB | 0 | 0.2-0.5 KB | 0 |
| Physical dimensions and unit-change invariance | buildable now (registry shared with quantities) | 0.3-0.5 KB new, plus upgrades | 0 | 0.2-0.5 KB | 0 |
| Exact statistics; printed-number consistency | buildable now | 0 | 2-4 KB main text, 8-12 KB appendix tables | 0.5-1.0 KB | 0 |
| Algebraic identities (normaliser) | buildable now (moderate proof effort) | 1.5-2.5 KB | 0.1 KB | 0.3-0.5 KB | 0 |
| `arith@0` statements with bounded evaluation | buildable now | 0 | 0 | 0 | 0.3-0.6 KB |
| Mathlib imports of VE's statements | **research**: EX-1 settles cost and feasibility on Bertrand's postulate | 0 | 0 | 0 | 0.2-0.4 KB |
| **Sum of the buildable rows** (estimate) | | 6.9-11.0 KB (20-31%) | 12.1-20.4 KB (16-28%) | 6.7-12.5 KB (14-25%) | 0.5-1.0 KB (10-20%) |
| Approximations with error bounds, sums of squares, square roots and logs by intervals | **research**: EX-2 | 0.5-1.0 KB | 0 | 0 | 1-2 KB with imports |
| Tensor shapes for deep-learning equations | **research**: EX-3 | 0 | 0 | 1-2 KB | 0 |
| Folds over lists, recursion, general induction inside VE | **research**, low priority: EX-4; imports cover the need meanwhile | 0 | 0 | 0 | small |
| Hedges ("probably"), procedures and dates as events, citations | sibling designs (attitudes, events-time-causation, attribution) | 1-3 KB | 2-4 KB | 2-5 KB | small |
| Truth of measurements, applicability of laws, statistical assumptions, interpretations, exposition | **residual forever** (labelled or named leaves) | about 60% of the text | about 55% | about 60% | about 15% |

## 7. Per-paper coverage estimates and the pilot order

"Checked" here means CHECKED plus OPEN bytes in the pilots' sense (an admitted reading with Lean-checked structure;
its premises remain assumptions). LABELLED bytes are reported separately, as NORTH-STAR asks. **All figures are
estimates** built as (estimated share of each sentence kind, section 2.5) × (the fraction of that kind each part
unlocks, section 6); ME-0 replaces the "now" column with a measurement and later pilot batches the others.

| Paper | Now: checked / labelled | After the plan: checked | Ceiling: checked | What limits the ceiling |
|---|---|---|---|---|
| Physics, Michelson-Morley (about 35 KB) | 4-7% / about 43% | 20-31% | 40-50% (with attitudes for hedges, events for the observation procedure, EX-2 for approximations) | apparatus and theory narrative is exposition; the ether theories' explanatory claims |
| Deep learning, LoRA-like proxy (about 50 KB) | 4-8% / about 40% | 14-25% | 35-45% | the experiments' truth is testimony; method prose; "on par" stays open |
| Mathematics, Ramanujan (about 5 KB) | about 0% / 10-15% | 10-20% (statements, finite checks, the imported main theorem if EX-1 passes; 6-12% if it fails) | 85-90%, only with a Mathlib formalisation of each analytic inequality | logs and the Gamma function need real analysis |
| VE's paper (73,801 B) | 0-1% / about 50% | 16-28% | 40-55% | method narrative; limitations; interpretation |

Weighted by NORTH-STAR's rule (weight × newly expressible bytes / document bytes), the upper endpoints give about
3 × (0.31 + 0.25 + 0.20 + 0.28) ≈ 3.1, which would rank beside the current first feature (soft norms, 3.37). This is
an upper-endpoint **estimate on unmeasured denominators** and says nothing until ME-0 measures them.

**Pilot order: physics, then deep learning, then mathematics.**

1. **Physics first.** Its licence is certain, its checked spine (calculations, two tables of readings, the velocity
   bound) needs only the buildable part of D2, and every batch from the first moves its number. VE's own paper runs
   alongside as the calculation layer's fixture source, because its data is in the repository.
2. **Deep learning second.** Its checked spine (result tables, comparisons with baselines, parameter counts) is the
   same buildable layer plus tables, but its licence is unconfirmed; ME-0 settles that.
3. **Mathematics third.** Most of Ramanujan's note is analytic inequalities; without the Mathlib import experiment
   (EX-1), only its statements and finite checks move. It pilots once EX-1 has answered.

## 8. Recommendation

**Build D2, `calc@0`, now; run D3, `arith@0` with Mathlib imports, as a pre-registered experiment and build it only if
the experiment passes; keep D1 as the baseline for everything else; reject D4.**

The reasons:

1. **It is where the checkable content of a science paper is.** A reader can check a paper's arithmetic, its tables,
   its derived bounds and its statistics mechanically, and errors there are common and consequential (statcheck's
   rates, from memory, about half of papers with at least one inconsistent p value). VE's paper alone has 186 lines
   with such numbers.
2. **It is buildable with known methods and a small proof effort**: exact rationals and `grind` are in the pinned
   toolchain (`lean/Iceberg.lean` uses both); Farkas certificates, dimension vectors and polynomial normal forms are
   textbook; no Mathlib, no new trusted search.
3. **It respects every constraint.** One reading per printed number (precision from the digits), zero-training
   phrases with names instead of nested formulas, Lean owning every value and verdict, UNKNOWN on budget, open terms
   never decided, and translation failures reported as findings about the source rather than silently repaired.
4. **Mathematics is different in kind.** Its theorems need induction, recursion and analysis; Mathlib already proves
   them. Importing proofs *of VE's own statement* closes the gap the iceberg experiment left open (a hand-reviewed
   correspondence) without growing VE's checker. Whether the cost (build time, disk, bridge lemmas) is acceptable is an
   empirical question, so it is an experiment with a bar first.
5. **It is honest about the pinned pilots**: zero bytes there. Its denominators are new, so its first batch is a
   measurement.

## 9. Open questions, risks and shared pieces

- **Owner of physical dimensions.** The quantities design owns unit identity (W6's nominal tags) and plans declared
  conversions; it leaves products and quotients of units to this design. This design specifies physical dimensions
  (plan ME-6), proposes one `ve-units@2` for both, and schedules ME-6 after the cross-plan review. Quantities' scales
  use "dimension" for a comparison scale, so this design says "physical dimension".
- **Rounding has one meaning, with an explicit tie rule.** The quantities plan defines "rounds to" for integer ratios
  with ties upward (its QT-A2). Python's formatting rounds exact binary ties to even: VE's own table prints 4/512 =
  0.0078125 as 0.007812 (plan fixture V-8), which ties upward would call wrong. So the tie rule is part of the claim:
  ties upward by default, "rounded half to even" declared by a document, and an undeclared exact tie in a translated
  source a reading set. One rounding module serves both designs (plan D6).
- **A rational type exists.** The quantities plan (its 2.3) says the Lean tree has no rational type; `lean/Iceberg.lean`
  uses core `Rat` with `import Std` at the pinned toolchain. Both designs can use it.
- **Derived float files are not data.** `paper/generated/posthoc-e1.json` stores per-template rates as binary floats
  (`-0.14999999999999997`); exact recomputation must start from integer counts in the trial files, which exceed the
  service's 16 MB line cap (plan EX-5).
- **Licences.** The deep-learning target is unpinned until a CC-BY licence is confirmed; the plan's DL batches wait.
- **Readability of worded equations.** Long formulas become chains of named values; whether readers follow them is a
  measurement for later (it needs model or human readers, which this design does not call).
- **Shared pieces** (plan 10): exact numerals and printed precision; one unit registry with dimensions; pinned inputs by
  digest (data handles, adapter records, risk logs); approximate words ("about", "roughly") as reading sets; hedges
  on quantitative claims (attitudes owns the words, this design the bound); observation procedures as dated events;
  arithmetic noun phrases in the English grammar; a residual line for external support (imports, adapters,
  observations); variable-domain readings ("x" as a whole number or a real).
