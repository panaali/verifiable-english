# Reported content and attitudes: implementation plan

2026-09-28 · Design only · Baseline `df874bd`, `design/attribution`.
Four design pages; summary follows. No implementation or pilot gain is claimed.

## 1 / 4 — Semantics and boundary

**Decision:** add a versioned `reports@0` statement elaborator and document admission route over existing FOL. Preserve frozen routes, canonical bytes, identities and certificates. Build on [W2 documents](document.md), [W1 norms](norms.md), [W3 definitions](../../PLAN-EXPAND2.md#w3-definitions-lemma-citation-and-statement-layer-sugar) and the [natural view](../natural-view.md), under the [verified-profile rule](../../VISION.md#converged-rule-elaborate-by-default-extend-only-through-verified-profiles-astra--fable-2026-09-25). W2's nested kinds and bridges already prevent quotation-to-premise promotion; they do not yet supply these compositional semantics.

**Content is inspectable.** A quotation contains a closed, typed formula, norm block, definition package, or another report/assessment. Bind its environment, profile versions, recursive content, references and reading choices. Keep source snapshot/span and utterance context in a separate occurrence identity; repeated occurrences may share content. Literal quotation also binds exact words; paraphrase does not claim word identity. Content equality is structural under declared canonicalisation, never equality of truth values or automatic logical equivalence.

**Independent meaning.** A source model is `(S, J)`: an ordinary admissible structure plus arbitrary attitude relations on holders, explicit contexts and structured contents. Write `J_m(h,c,q)` for holder `h` saying, believing, wanting or intending content `q`. Speech, belief, desire and intention are distinct relations. Promising, pledging and denying require distinct reviewed acts; none is silently renamed “intends” or “believes not.” An occurrence's tense remains explicit; dates do not acquire temporal inference from labels.

`J_says(h,c,q)` can hold while `q` is false. Neither `J_believes(h,c,q)` nor `J_wants(h,c,q)` entails `q`; intention entails neither success nor obligation. Nested `says(article, believes(Anthropic,q))` asserts neither Anthropic's belief nor `q` outside that report. Contradictory quoted contents need not make the reporting document inconsistent.

**Elaboration:** for each finite, acyclic, closed content/context/act key, generate a fresh unary predicate on its holder sort; epistemic judgments similarly use predicates on evidence contexts. Boolean combinations use existing FOL; no truth predicate, dynamic quotation or new proof rule is added. The quote table is checked recursively, not an opaque string dictionary. Restriction/expansion between `(S,J)` and generated FOL interpretations must preserve both proofs and countermodels. Fresh attitude relations have arbitrary interpretations: this is vocabulary extension, **not** a W3 definition or a claim of `Layer.expands` uniqueness over `S` alone. Deterministic subordinate layers retain their existing contracts.

**Checking inside:** from explicitly selected payloads `P` and `P implies Q`, certify the scoped conditional consequence `Q`. Display “Q follows from the reported contents.” Do not output “the speaker believes Q,” “the article says Q,” or bare `Q`. Payload selection carries occurrence/context IDs; sharing a speaker does not merge contexts. Check inner consistency and vacuity separately; an inconsistent quotation does not automatically supply outer premises.

Quoted W1 rules get a local conflict/completion check but no active outer norm layer. Quoted W3 definitions use a pinned local environment and never redefine outer vocabulary. Unsupported combinations retain the [existing integration gates](../INTEGRATION-GAPS.md); storing content does not certify its elaboration.

<div style="page-break-after: always;"></div>

## 2 / 4 — English, modality and readings

These **proposed writable templates** await parser implementation. Names and contexts use reviewed vocabulary; technical keys stay in the inspector.

| One-reading wording | Committed scope |
|---|---|
| “The article says that the service is safe.” | Report of the safety claim; safety remains embedded. |
| “Anthropic believes that Claude is helpful.” | Belief with a typed, inspectable helpfulness claim. |
| “Anthropic wants Claude to be helpful.” | Desire; no duty or achieved helpfulness. |
| “The team intends to publish the results.” | Intention; no publication fact or promise. |
| “Anthropic believes that Claude is not human.” | Negation inside belief. |
| “It is not the case that Anthropic believes that Claude is human.” | Negation outside belief. |
| “The article says that Anthropic believes that Claude is helpful.” | Two retained attribution scopes. |
| “Given the stated evidence, the service may be safe.” | Epistemic possibility, with a bound evidence context. |
| “Given the stated evidence, the service is probably safe.” | Qualitative likelihood assessment in that context. |
| “Alice is permitted to access the server.” | Permission through W1; distinct from epistemic “may.” |

**Epistemic first slice:** `May(c,q)` and `Probably(c,q)` are named, compositional **open judgments** over structured content. Their declared criteria, assessor where supplied, evidence context and version are retained. The logic around them is exact; whether the assessment applies remains open. They are not probabilities over translation readings. No invented percentage, default threshold, probability calculus, factivity or modal inference is licensed. An unstated assessor remains unstated. Merely attaching a hedge label does not implement either judgment.

If a committed pilot requires modal inference, record the failed elaboration/budget and propose a separate verified profile. A candidate epistemic semantics is `May(c,φ) iff some alternative admitted by c satisfies φ`, with world-relative vocabulary and explicit domain/reference rules. Prove its standard translation and executable model validity before admission; do not assume actual-world accessibility or psychological belief closure. Numerical “probably” requires a source-justified probability model and threshold; otherwise it remains open. This plan does not ship that profile.

**Scope admission:** the all-derivations gate checks the whole sentence and every complement; ambiguity or budget exhaustion rejects. Negation, coordination and quantifiers retain scope. No pronoun crosses a quote boundary implicitly. The first slice requires closed complements with resolved names; de re or cross-boundary bindings stay unresolved until their semantics exists. Desire/duty, promise/prediction and “probably not”/“not probably” are never synonyms.

**Zero-training workflow:** show plain-English alternatives and distinguishing situations; authors choose and approve a meaning-bound sentence. Typed and rendered text must round-trip through the same grammar, including its kind and nested content. Extend W2-aware presentation and W8 unit actions; formula-only `ve.prose@1` is not a whole-document export. Explicit-form fallback is a visible repair, not a passed English gate.

Translation preserves all admitted readings in extensible versioned sets. Narrowings are separate attributed units. Correlated choices share a key; citations inherit compatible choices, and updates make dependents stale. Use W2's assertion shortcut only with proved shared backgrounds; otherwise check complete choices up to 64, then UNKNOWN. Unelaborated alternatives remain unresolved.

<div style="page-break-after: always;"></div>

## 3 / 4 — Bridges, assurance and implementation gates

**Bridges are explicit premises.** “For this argument, the reviewer accepts the article's safety claim as true” introduces the exact inner formula as an assumption, with reviewer, occurrence, content identity, environment, choices and reason. For nested reports, name the exact target: accepting the article's complement yields a belief claim; accepting that a report occurred does not. The belief's payload needs its own bridge. An independent proof of the payload can instead be cited with all its dependencies. Testimony, prestige, a URL and a certificate of faithful quotation never discharge truth acceptance.

Norm adoption and definition import are separate typed operations: state the destination context and regenerate validated W1 layers or W3 environments. A formula bridge cannot activate rules or install definitions. An unsupported import stays unsupported. New labels preserve the legacy `bridge:accepts` meaning; never retrofit a different meaning into old records. All used bridges, assumptions, open decisions and narrowings propagate transitively through citations, scoped checks and final conclusions.

| Status | What the report establishes |
|---|---|
| CHECKED | Accepted scope/types/identities and admitted content; any claimed consequence has replayed evidence. Assumptions are identified, not proved true. |
| LABELLED | Source/act/support metadata or retained prose only; no substantive coverage from an empty complement. |
| OPEN | An admitted compositional meaning depends on specified open judgments. Open-term inventories alone do not qualify. |
| READINGS / UNFORMALISED | Elaborated alternatives with witnesses / residual missing meanings. Unelaborated reading lists earn no READINGS coverage. |

**Lean obligations, all pending:** independently define `Intended`, typing and scope; prove elaboration faithfulness at every universe and model correspondence in both directions, including finite witness decoding. Prove old-language conservativity without new assumptions; do not confuse arbitrary attitude interpretations with unique definitional expansion. Prove scoped consequence soundness, bridge/adoption admission and graph composition with exact transitive leaves. Supply executable model validity, countermodel soundness and `CertificateSound` without an assumed soundness oracle. Prove parser/renderer correspondence and one-reading claims for the admitted surface; tests alone do not discharge them. Audit under the existing axiom allowlist and bind exact statements, route/build, profiles, environments, quote tables and choices. Keep known decoding/display trust and unfinished surface obligations visible under the [verification contract](verification-contract.md).

**Work items, in dependency order:**

1. Pin four sources and challenge cases; review `Intended`, distinctions between speech and attitudes, and the quote/bridge wire schema. Register the new route and its trust cost; preserve frozen fixtures.
2. Implement independent Lean semantics, elaborator, executable admission and proofs under proposed `lean/VE/Reports/`. Gate scope, local W1/W3 calls and mixed profiles explicitly. No modal calculus in this slice.
3. Add untrusted production/orchestration in `ve/reports.py`; version document/readings/bundle adapters and the open-term schema for content arguments. Reuse existing certificate replay. Follow the [migration plan](SEMANTICS-MIGRATION-PLAN.md): Lean owns semantic verdicts; Python presents them; Rust searches witnesses.
4. Add English/natural rendering and W8 review actions. Regress nested attribution, negation, ambiguous “may,” reference scope, contradictory payloads, quoted norms/definitions, missing bridges, changed quotes, incompatible choices and stripped citation leaves. Validate Python/Rust/Lean agreement without treating it as proof.
5. Rerun pilots and whole-span fidelity review after admission and English gates. Report zero gains when co-blockers remain. No model calls are needed for local replay; independent human fidelity and zero-training evidence remain explicit release gates.

<div style="page-break-after: always;"></div>

## 4 / 4 — Evidence, accounting, unlock and risks

The [North Star portfolio](/home/seyran/code/ve-northstar/NORTH-STAR.md) (`01b1090`, snapshot 2026-09-27) supplies priorities, not promised gains. Constitution/UDHR evidence below is from `run-20260927T1800Z`: read each run's `metrics.json`, `units.json`, `AUDIT.md` and parent `TREND.md`. Primary-blocker tags are coarse and sometimes inherited across split clauses.

| Evidence and baseline | Expected unlock; remaining blockers |
|---|---|
| [Claude constitution pilot](/home/seyran/code/manage-agents/pilots/claude-constitution/run-20260927T1800Z/): 184,893 B / 1,124 units; C 22/1, L 349/39, O/R 0, U 184,522/1,084. Attribution 12 units/1,880 B; belief/modality 24/3,223 B. | Inspectable belief/desire wrappers, especially `u0007.s01` (wants helpfulness) and `u0169.s01` (believes constraints serve interests). Norms, causal force, comparisons and open helpfulness remain. Tagged opportunity **0–5,103 B**, not a forecast. |
| [UDHR pilot](/home/seyran/code/manage-agents/pilots/udhr/run-20260927T1800Z/): 10,916 B / 116 units; C/O/R 0, L 535/34, U 10,381/82. Attribution 4/681 B; modality 2/286 B. | Retain reaffirmed faith (`u008a`), determination (`u008b`) and pledge (`u009`) separately. Rights, promotion/causation and vague standards remain. **0–967 B** tagged opportunity; `u006–007` “essential” is not automatically epistemic possibility. |
| [News source](../../usecases/news-article/source.md) and [coverage](../../usecases/news-article/coverage.md): 26 rows / 14 sentences; attribution 3, hedge/inference 5, overlapping co-blockers. | Replace inert content tokens in S7's statement and S14's pledge; retain S8's likelihood scope. Numbers, future time, causal “support,” speed and intention remain. Byte gain **unknown**; reconcile published D/R/O/NO 1/11/3/11 versus row counts 1/9/5/11. |
| [BlueDot grant](/home/seyran/code/ve-bluedot/usecases/bluedot-grant/README.md), external commit `fbe0337`: authoring, 7,619 B / 93 units; reported C 780/12, L 3,513/50, O 2,081/22, U 1,245/9. | Handoff arrived after North Star's pending snapshot. Milestones become inspectable intentions; “may misstate” stays epistemic; “should help” needs an approved hope/prediction reading. Plans/predictions currently among labels are not substantive coverage. Gain **unknown**; these totals lack an independent fidelity audit. |

**Accounting gate:** pin source hashes, language/profile commits, ledger boundaries and evidence. Partition every UTF-8 byte once, including punctuation. Recursive complements add no duplicate bytes; report inner-check counts separately. A wrapper alone cannot upgrade a whole span. Split mixed spans without losing dependencies, compare against a split-only baseline and retain old-boundary aggregation. Upgrade only complete, admitted meanings with reviewed scope/force; distinguish metadata, open adjudication, readings and missing semantics. Keep residual counts and used bridges prominent.

C/U audits sampled mostly metadata (C: one assertion plus 19 labels; U: 20 labels), so they do not validate substantive translation. Review every proposed upgrade against its whole source context, including missing alternatives. Do not add feature estimates across overlapping tags or extrapolate news rows into bytes. A source-authority claim is neither a proof nor a fidelity audit.

**Principal risks:** logical omniscience from rewriting content; scope leakage through bridges, norms or definitions; hiding substantive omissions behind open predicates; accidental obligation from desire; fabricated probability precision; unreadable English accepted through fallback; and stale sources/readings inflating coverage. Require countermodels where a report holds but its payload fails, an intention is unfulfilled, equivalent payloads have different belief attributions, and belief in `P` and `P implies Q` coexists with no belief in `Q`. Display inner inconsistency locally and outer premise vacuity explicitly. Human source fidelity remains separate from all mechanical guarantees.

<div style="page-break-after: always;"></div>

## Summary

Add structured reported content through a versioned statement elaborator over existing FOL. Preserve speakers, contexts, force, nested content and reading choices. Check embedded formulas, rules and definitions locally; never infer their truth, adoption or the speaker's belief in their consequences. Truth acceptance requires explicit, identity-bound bridge premises. Belief, desire and intention remain distinct; qualitative epistemic judgments stay open without invented probabilities. Stronger modal inference requires a separately justified verified profile. English must be writable, uniquely parsed and faithfully rendered. Lean obligations cover semantics, elaboration, model correspondence, admission and provenance. Pilot accounting separates substantive meaning from labels and inventories, preserves translation alternatives and counts bytes once. Constitution and UDHR tags bound opportunities, not gains; news and grant gains remain unmeasured until admitted translations and fidelity review exist.
