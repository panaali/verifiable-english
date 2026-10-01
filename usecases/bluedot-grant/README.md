# BlueDot grant draft, authored in VE

This measures translation of our own grant draft. The source is unchanged:
[`source.md`](source.md) has SHA-256
`a9fa225acce6a684af7519c9c6fa82a20fc3a7e685a04b7e1a4bac88a0d6ed22`
and 7,619 UTF-8 bytes. [`document.ve.md`](document.ve.md) partitions every
source byte into the same 93 units as the 2026-09-27 baseline, and copies the
source byte for byte after its JSON front matter.
[`natural-view.md`](natural-view.md) lists each span, its status, its kind and
the checked rendering.

## Before and after coverage

The previous version reported 88.1% CHECKED. Review found that most of it was
relabelling: one-off atoms such as `uses_50_to_5000_steps` were auto-declared
per unit, the five definitions were never used, and causal links, a year,
obligations and a risk default were invented. Those statuses are withdrawn.

| Status | 2026-09-27 baseline | Previous (withdrawn) | Now |
|---|---:|---:|---:|
| CHECKED | 780 B (10.2%), 12 units | 6,709 B (88.1%), 67 | **3,351 B (44.0%), 40** |
| LABELLED | 3,513 B (46.1%), 50 | 853 B (11.2%), 25 | 1,029 B (13.5%), 25 |
| OPEN | 2,081 B (27.3%), 22 | 0 B (0%), 0 | 2,114 B (27.7%), 19 |
| UNFORMALISED | 1,245 B (16.3%), 9 | 57 B (0.7%), 1 | 1,125 B (14.8%), 9 |
| **Total** | **7,619 B, 93** | **7,619 B, 93** | **7,619 B, 93** |

`ve document coverage` reports 100% byte accounting, 4 open terms and 19
assumption lines. `ve document check` reports premise consistency `UNKNOWN`
under its bounded search. A CHECKED status means a typed formula states what
the span says. It does not establish the draft's predictions, provenance,
risk reduction or causal mechanisms.

## What CHECKED means here

[`semantic_readings.py`](semantic_readings.py) has one authored entry for each
of the 93 units. Nothing is auto-declared. A CHECKED formula uses relations
between named constants, quantifiers, equality or a defined term. Every
content word in its symbols occurs in the span or in a recorded resolution.
Tests enforce both rules.

The kind keeps the speaker and the force. Only the author's notes are plain
assertions (19 units, each with a signed reading set). OLD, NEW and PASTE
wording is attributed to that text (16 units). Each title candidate is
attributed to its candidate (4). The paste instruction (u067) is the last one.
Hedges and commitments stay nested inside the attribution, for example
`old_text says (applicant promised …)`. A note is never recast as a belief,
an intention or exposition: an OPEN note is `author says …`, and an
unformalisable note keeps the plain `unformalised` kind.

VEX is a proposal. Where the draft calls it "proposed mandatory evidence" or
says it "would require" evidence, the reading states that VEX is evidence and
that, once adopted, it is mandatory for statistical and approximate claims and
requires evidence. Nothing states that VEX is adopted.

## Author choices for the five terms

[`author_choices.py`](author_choices.py) gives each term a signed rule and a
reason. The rule is a list of clauses. The document records the choice in the
term's definition. The predicate's description carries the signature, the
rule and the reason, and its body is the conjunction of the clauses. `decide()`
is exactly the conjunction of the same clauses, so the classifier and the
definition cannot drift. Tests show that every clause can fail on its own.

| Term | Clauses (author choice) |
|---|---|
| `matched_cost` | same task; budget registered before the comparison starts; the cost of authoring, formalisation, proof production, compute and review is counted for both arms; arm totals differ by at most 5% of the larger |
| `real_artefact` | provenance SHA-256 recorded; created for a non-benchmark task; created before selection; no flaw seeded by evaluators |
| `affordable_proof` | proof cost and formalisation cost recorded; complete certificate; accepted by the checker; budget and deadline registered before the claim; cost within budget and time within deadline |
| `misleading_formalisation` | source and formula hashes pinned; an answer-changing concrete input; two distinct reviewers reproduce it; every reproducing reviewer is blind to the arm |
| `catastrophic_risk` | documented pathway; pathway evidence recorded; severity assessment recorded; extinction or at least 1,000,000 projected deaths. Possibility is a separate judgment. |

No record of a real trial or event is supplied as true.

## Where the definitions are used, and where they stay open

Every unit that mentions a defined term either uses that term's predicate or
is OPEN on it:

| Term | Used by CHECKED units | OPEN units |
|---|---|---|
| `affordable_proof` | `u038 u050 u089`; `u051` uses its `within_budget` clause | none |
| `matched_cost` | `u062` (the comparison in the revised form text includes formalisation and proof production) | `u013 u018 u024 u079` |
| `real_artefact` | `u041 u092` (real artefacts in the benchmark test transfer) | `u015 u021 u031 u063 u082` |
| `misleading_formalisation` | none | `u014 u017 u040 u064 u078 u091` |
| `catastrophic_risk` | none | `u022 u027 u083 u085` |

The four open terms are declared in the document's `open_terms` with their
reasons. OLD wording predates the author's rules. Milestone items are plans,
so they are not formalised. "Misleading-formalisation controls" and error
classes do not say how they relate to a formalisation. BlueDot, not the
author, decides what its form heading means by "catastrophic risk".

## Removed or corrected content

| Finding | Correction |
|---|---|
| Causal "because" on "test these harms", "test transfer", "is a benefit of", "cover" | No causal kind anywhere. These are plain relations (`tests`, `benefit_of`) or OPEN. |
| Merged causation route never invoked | [`causal.ve.md`](causal.ve.md) checks `u029 u035 u047 u086` on `alternatives@0` over the same bytes. Lean admission types `prevents` in u047. The Lean route refuses `alternatives@0` together with definitions, so these units are UNFORMALISED (`causal_route_excludes_definitions`) in the main document and are not counted as CHECKED. |
| Stated causal links the route cannot express | `u026 u084` ("blocks … by excluding …") are `causal_means`; `u060` ("motivates") is `motivation_link`. All three are UNFORMALISED. |
| u041/u092 gained "beyond planted flaws" | They now state only "real artefacts test transfer". |
| Year 2026 and "intended" OLD u012 | No date reading remains, because the source gives no year. u012 is a LABELLED plan attributed to the OLD text. |
| Milestone clauses turned into `require` obligations with deny/allow defaults | Removed. Milestones are LABELLED plans, or OPEN where they mention a defined term. |
| Risk default `unexamined: possible` | Removed. No risk policy, severity class or default is supplied. |
| u054 "claims no novelty" | Now "the draft does not claim novelty …". |
| u039/u090 made VEX require the quality review | Once adopted, VEX requires evidence, and that evidence still needs quality review. |
| u007, u009, u056, u074, u076 dropped "mandatory evidence": the readings held if VEX were optional or not evidence | VEX is evidence and, once adopted, is mandatory for statistical and approximate claims (`is_evidence`, `adopted`, `mandatory_for`). |
| u039/u090 dropped the force of "would": a required evidence item existed now | The requirement is conditional on VEX being adopted. |
| u062 "are included" was recast as the applicant's intention | Asserted, with a signed reading set. |
| Same class: u033 (OLD hope) was the applicant's, not the OLD text's; u053 and u069 were the author's beliefs; u063 and u064 were exposition | u033 is attributed to the OLD text. u053 (`vague_evaluation`) and u069 (`vague_comparison`) are plain UNFORMALISED notes, and u063 and u064 are `author says …` (OPEN). |
| u060 attributed the author's motivation to the update | UNFORMALISED. No attribution to the update remains. |
| Omissions in u003, u019, u026, u029, u052 | u003 states both tools and all three issues, and u029 both harms. u052 keeps "in general". u019 is a LABELLED plan, and u026 is UNFORMALISED. |
| `decide()` gaps | It now checks proof-cost recording, budget and deadline registered before the claim, reviewer blindness and the severity assessment. |

## Author resolutions

The discourse route does not admit these resolutions. Each is an author
choice, recorded in `RESOLUTIONS` and in the reading set's `why`.

| Unit | Resolution |
|---|---|
| u030 | "these harms": the two false-confidence harms of u029 |
| u040, u091 | "these harms": the harms of the preceding NEW sentence (unit stays OPEN) |
| u041, u092 | "real artefacts": those included in the benchmark; "transfer" left unqualified |
| u045 | "its": bluedot-rapid-draft-v3.md |
| u048 | "the guarantee": the guarantee of mandatory proof |
| u049 | "It": the guarantee; "their": the declared foundations |
| u050 | "needs": needed for the claim not to remain unresolved |
| u051 | "the claim": the claim those proofs prove; "beyond budget": not `within_budget` |
| u052 | "This": note 2's protection against arbitrary false sub-claims |
| u054, u058 | "is claimed": by this draft |
| u059 | "its": VEX |
| u062 | "the matched-cost comparison": the one in the revised form text |
| u067 | "its label or count": the pasted candidate's |
| u068 | "sentence and paragraph": respectively |
| u007, u056, u074 | "proposed mandatory evidence (VEX)": VEX is evidence and, once adopted, is mandatory for the two claim classes |
| u009, u076 | "developing mandatory evidence (VEX)": the same, for the VEX being developed |
| u039, u090 | "would": once VEX is adopted |
| u070 | "its": the proof rule; "the extra space": in the revised passages |

## Remaining limits

| Missing capability | Units | Treatment |
|---|---|---|
| Causation route together with definitions | `u029 u035 u047 u086` | UNFORMALISED here; checked in `causal.ve.md` |
| Means and motivation links | `u026 u060 u084` | UNFORMALISED |
| Baseline and tolerance for "close to the current length" | `u069` | UNFORMALISED |
| A sense of "appropriate" for the existing credit | `u053` | UNFORMALISED |
| Natural wording for this vocabulary | all 40 CHECKED | The natural grammar's lint rejects these templates, so every rendering is the explicit form, parsed back to the same formula. |

Headings, OLD/NEW/PASTE labels, plans and the OLD text's hope in `u033`
remain LABELLED.

## Recheck

```sh
UV_CACHE_DIR=/tmp/uv-cache uv run python -m usecases.bluedot-grant.build_document
UV_CACHE_DIR=/tmp/uv-cache uv run python -m ve document check usecases/bluedot-grant/document.ve.md
UV_CACHE_DIR=/tmp/uv-cache uv run python -m ve document check usecases/bluedot-grant/causal.ve.md
UV_CACHE_DIR=/tmp/uv-cache uv run python -m ve document coverage usecases/bluedot-grant/document.ve.md
PATH="$HOME/.elan/bin:$PATH" lake build  # in lean/
UV_CACHE_DIR=/tmp/uv-cache uv run python lean/audit.py
UV_CACHE_DIR=/tmp/uv-cache uv run python -m pytest
```

The generator uses only local source bytes and checker APIs. It makes no model
calls and does not modify `source.md`.

Verification on this worktree (2026-10-01): `lake build` completed 488 jobs;
`lean/audit.py` passed its 249-file, 2,437-declaration audit; the BlueDot test
file passed 13 tests. The full suite passed **4,895 tests, 10 skipped, 0
failed** with `VE_NATIVE_PREBUILT=1`, `VE_LEAN_PREBUILT=1` and
`VE_RUST_SHA256=04470aa2a3a7c14367f4040d1da37e2b356ad0c07f82a0b9731f0b34049261f4`,
the SHA-256 of the Rust binary built from this checkout. `main` pins a
different build in `lean/checkers.lock`. The suite ran in four parts with
`pytest -n` because the machine was shared: three file groups and then the
remaining 116 files. No Rust source or trust lock was changed for this use
case.
