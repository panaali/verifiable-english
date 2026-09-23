# `ve assist`: interactive, sentence-level assisted formalisation (2026-09-22), for review

Motivation: the P5 authoring probes (surface: 0/12; schema-constrained JSON: 0/12) gave Gemini 3.1 Pro ONE shot plus ONE
repair and no interactive tool. That tests one-pass formalisation, not formalisation; neither humans nor agents write
formal text that way. The lead proposes an interactive tool; this plan specifies it.

Tool (CLI + JSON tool-calling API, usable by humans and agents):
1. `propose(sentence, context)`: a cheap model (Haiku 4.5) returns 1-k VE candidates for ONE English sentence given the
   current environment and already-accepted claims; every candidate is parsed and type-checked; invalid ones are
   repaired or dropped before display; each shown with the deterministic English paraphrase.
2. Ambiguity: when candidates differ in meaning (`compare` oracle), show a small DISTINGUISHING MODEL for each pair.
3. `accept(candidate)` / `rewrite(text)` / `declare(predicate)` by the author (human or agent); nothing enters the
   document without an explicit author action; vocabulary additions go through `ve propose` gates.
4. `check_step(node)`: immediately reports whether the step follows from its declared parents; if not, the missing
   premise candidates or a countermodel; `status()` summarises unproved edges.
5. Ledger: every proposal, choice, check and token count; authoring cost is fully charged (author + proposer).
Evaluation: re-run P5's 12 dev items as a feasibility probe with tool-using agents (Opus 5.5, Gemini 3.1 Pro), fixed
tool-call and token budgets, success = all edges certified and the graph replays; report success rate, cost, and a
fidelity check (does the certified graph say what the prose says, independent audit). If >= 50%, give the P5 VE arm a
fair dev run with the tool, cost charged. Human use: document the CLI for the lead.
