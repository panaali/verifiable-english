# Lean-first batch 4 (discourse): DELTA

Base `776a64d7` (the head of batch 0, `lean-first/b0`), head `lean-first/b4`. Gate item 2 of
`docs/LEAN-FIRST-PLAN.md` 5.1: every public result of the corpora below, base against head, by
`tools/lean_first_diff.py` (each side recorded from its own checkout and builds; `compare --delta
docs/lean-first/b4/delta.json`). The batch: `ve/discourse.py` relays the Lean discourse route
(`rejection` always returns Lean's diagnostic; the joint choices, the joint disjunction and the
composition gate are Lean's), and Python's validator, resolver and joint checks and Rust's
`discourse.rs` are deleted ([`LEDGER.md`](LEDGER.md)).

## The discourse corpus

No `ve-document@2` file is stored in the repository, and the pilot branches hold one discourse probe.
The batch's own corpus is therefore the 3,175 distinct `ve-document@2` texts the discourse tests write
(`tests/test_discourse*.py`, `test_compose_dispatch.py`, `test_environment_field_types.py`,
`test_speech_acts*.py`), captured at the base with the sibling files their imports name
(`docs/lean-first/b4/capture_discourse.py`, `docs/lean-first/discourse-corpus.json.gz`). Each goes
through `check_document` and `render_document`. At the base, 308 are admitted and 2,867 rejected,
with 42 distinct leading diagnostics.

## Result

| Corpus | Records per side | Same | Wording | Order | Verdict | Availability |
|---|---:|---:|---:|---:|---:|---:|
| discourse (default authority) | 6,350 | 4,758 | 180 | 1,370 | 42 | 0 |
| probe, `python` | 9,435 | 9,435 | 0 | 0 | 0 | 0 |
| probe, `lean` | 9,435 | 9,435 | 0 | 0 | 0 | 0 |
| conformance, `python` | 19,806 | 19,806 | 0 | 0 | 0 | 0 |
| conformance, `lean` | 19,806 | 19,806 | 0 | 0 | 0 | 0 |
| pilots (`ve document check`) | 237 | 232 | 5 | 0 | 0 | 0 |
| **All** | 65,069 | 63,472 | 185 | 1,370 | 42 | 0 |

Both `compare` runs exit 0 with `"unlisted": 0` against [`delta.json`](delta.json) (28 wording pairs,
1,370 order records, 42 verdict records). Each discourse document appears twice (check and render) with the
same change. Every difference comes from one rule, **R4: a `ve-document@2` document Lean rejects raises
Lean's diagnostic, never Python's** (before, Python's diagnostic was kept whenever Python rejected too).
The only other difference is the dropped hints of V1.

## O4: the same text with its own code (`order`, 671 documents)

Python raised its copy of Lean's text as a plain `VEError`, whose `code` is `InvalidInput`. The relay now
raises Lean's text with the code its prefix names (`ve/discourse.py` `_error_of`, which already did this
whenever Lean's text was shown). The text is unchanged. By code: `UnrecordedSlot` 461, `UnresolvedReference`
79, `TargetKindMismatch` 68, `AmbiguousReference` 20, `ManifestMismatch` 15, `MentionNotSlot` 9,
`StaleTarget` 6, `IllTypedTarget` 3, `UnsupportedTarget` 2, `DanglingAnchor` 2, `UnknownRule` 2,
`DuplicateDeclaration` 1, `InaccessibleTarget` 1, `IndependentFragment` 1, `WitnessSplit` 1.

## O5: Lean's diagnostic where the two differed (`order`, 14 documents)

This is the known limitation of `docs/spec/discourse.md` 8: Python's expansion parser and Lean's grammar
named different faults.

| Id | Base (Python) | Head (Lean) | Documents |
|---|---|---|---:|
| O5.1 | `IllTypedTarget: m1: web_api` | `ManifestMismatch: bound.u2` | 6 |
| O5.2 | `IllTypedTarget: m1: alice` | `ManifestMismatch: bound.u2` | 5 |
| O5.3 | `IllTypedTarget: m1: alice` | `ManifestMismatch: bound.u1` | 2 |
| O5.4 | `InvalidInput: group rs1@1:same-witness spans are outside the supported fragment` | `ManifestMismatch: groups.rs1@1:same-witness` | 1 |

## W4: Lean's text where Python's differed (`wording`, 90 discourse documents + 5 pilot records)

Every distinct pair is in `delta.json` `wording`. Grouped:

- **W4.1, the abstention (7 documents).** `UnsupportedProfile: the Lean discourse route abstains
  (NotImplemented: X)` becomes `UnsupportedProfile: NotImplemented: X` for X = `norm content`, `fenced English
  or strict content` and `a document without a claim graph`. This is Lean's text under its class's `Code: `
  form, the same rule as batch 0's W1. Python no longer rewords it, so `ve/discourse.py` passes
  `tools/relay_lint.py`.
- **W4.2, outside Lean's fragment (45 documents).** `IllTypedTarget: m1: alice|api` (39 + 2),
  `MentionNotSlot: m1` (2), `Citation is absent, cyclic, or not earlier in the bundle` (1) and `UnknownDocument:
  policy` (1) become `InvalidInput: unit u1|u2 is outside the supported discourse fragment`. Python's checks
  reached a later fault, but Lean stops at the first fault in its order.
- **W4.3, decoder texts of malformed blocks (19 documents).** Python's field-naming texts become Lean's
  generic decoder texts: `InvalidInput: discourse.anchors|documents|groups|mentions` → `array expected`;
  `InvalidInput: discourse block|constraint|name`, `InvalidInput: document` and `InvalidInput: import k` →
  `object expected`; `InvalidInput: discourse fields`, `InvalidInput: document`, `InvalidInput: import k` and
  `invalid unit schema` → `fields do not match: expected [...], got [...]`. The same applies inside a stored
  document (`InvalidInput: document policy2: ...`). **These are port candidates under DRI answer 3** (Python's
  better user-facing texts move into Lean): Python's texts name the field, Lean's do not. They were not ported
  here, because batch 4 has no Lean work and the decoder is `Discourse/Wire.lean`. They are listed for the DRI.
- **W4.4, the front matter (19 documents + the 5 pilot records).** `unknown document metadata` (Python, which
  read past a key Lean's reader refuses) becomes `invalid JSON front matter`. The five pilot records are one
  probe document on five constitution-pilot branches
  (`probes/discourse-in-translation-probe.ve.md`). It went from `UnrecordedSlot: u0078.s01: [48274, 48278)`
  (or `u0123.s02.p1: [76303, 76305)`) to `invalid JSON front matter`: its reading sets hold `"content": null`,
  which Lean's restricted JSON reader refuses. Both sides reject; only the text changes. **Finding for the
  DRI:** `docs/spec/discourse.md` 3.1 says the frozen parser rejects `null` (what Lean does), but its relay
  paragraph and `lean/VE/Discourse/Loader.lean`'s header call JSON `null` `NotImplemented` (an abstention). The
  two statements disagree. The more useful text was Python's, which this batch cannot keep.

## V1: `discourse_hints` dropped (`verdict`, 42 documents)

`check_document` reported `discourse_hints` beside an admission when Python's own validator rejected a
document Lean admitted, for example `IllTypedTarget: m1: web_api` (18), `IllTypedTarget: m1: alice` (16),
Python's "not implemented in Python" abstentions (6) and Python's group fragment text (1). The verdict,
statuses, references and report id were Lean's, and they are unchanged. The hints were the second opinion this
batch deletes, so they go with it. **This removes a capability by name and needs the DRI's acceptance.**

## Reviewed presentations: unchanged

A unit's reviewed wording (`reviewed_presentations`, `Reviewed wording:` in `ve document render`) now
displays Lean's resolved targets by their registered displays. It is shown only when the English parser
reads it, by the parser's spellings, as exactly the formula Lean bound to the unit (build checklist 9).
Without that gate, 36 documents Lean admits but Python's parser cannot read (`It are safe.`, `She
owns"web_api".`) gained a presentation. With it, the corpus shows no presentation difference.

## Rust

`ve conformance` refuses every `elaborated-document` case without `profile: reports@0`
(`UnsupportedProfile`, tested in `rust/ve/src/main.rs`). Before, such a case was the deleted discourse
re-check. No corpus sends one (the P0 `elaborated-document` cases carry no `family` member), and no Rust text
reaches a user (rule 4).

## Signatures needed

- **W4 + O4 + O5 (wording and order, one block):** signed by the DRI 2026-10-04 (Lean's texts and order are canonical; LEAN-FIRST-PLAN DRI answer 3). JSON `null`: the frozen parser's rejection (spec 3.1) is the rule; the Loader.lean header's `NotImplemented` wording is a stale comment to correct; Python's clearer message for this case is to be ported into Lean's text (FOLLOW-UPS).
- **V1 (`discourse_hints` dropped):** signed by the DRI 2026-10-04: the hints were Python's second opinion beside Lean's verdict; with one owner they go. Verdicts, statuses, references and report ids are unchanged.

## Rest of the gate (5.1)

- **Suite (item 1).** The full suite ran at the head (`ab66aeec`'s tests, `VE_NATIVE_PREBUILT=1`), in two
  halves at `-n 10`. First half: 5,764 passed, 5 skipped, 1 failed:
  `test_gate_collection.py::test_gate_baseline_is_the_gate_collection`, fixed in `ab66aeec` by
  `tools/gate_collection.py --write`, which removed four IDs of deleted Python internals or renamed tests and
  added the new ones; the file then passes, 19 tests. Second half: 2,970 passed, 1 skipped. The English merge
  smoke is included. Outside pytest, on the head: `lake build` (561 jobs), `lean/audit.py` (287 files, 3,045
  theorems, standard axioms only), `VE/Route/frozen.py`, `tools/relay_lint.py`, `tools/rust_build.py --check`
  and `tools/check_rust_deps.py` all pass.
- **Differential fuzzer (item 2).** `infra/difffuzz` (`7c34a1a8`) was merged onto the base and onto the head in
  scratch worktrees (no Lean or Rust change in it). The CI sample gives 23 new signatures on each side, the same
  ones, with 329 baseline entries seen and 80 not reproduced. The 13 date seeds 20260921 to 20261003
  (`--deep 1 --seed`) give the same corpus, mutants, answers, new count and baseline counts on both sides, seed
  by seed, with the same finding signatures and counts on every surface. With the CI sample that is 14 seeds.
  The baseline does not grow. The fuzzer has no discourse surface.
- **Deletion ledger (item 3).** [`LEDGER.md`](LEDGER.md). `tools/relay_lint.py` now covers `ve/discourse.py`
  and passes.
- **Latency (item 4).** `docs/lean-first/b4/cpu.py` runs `check_document` over the 3,175 corpus documents
  sequentially. Python's own CPU went from 24.2 s and 15.1 s (base, two runs) to 6.4 s and 8.3 s (head, two
  runs). The Lean route's CPU (the process's children) dominates and moved with host load: 150 to 268 s on
  either side, at loads from 9 to 58. Wall time likewise: 171 s and 1,512 s (base), 154 s and 407 s (head).
  The batch adds no Lean work per call besides encoding the joint list. No wall-clock gain is claimed. The
  one-shot route start is batch 1's.

## Not in the corpora above

- **Use-case harnesses** were not rerun by the A/B tool. Their answer keys are pinned by the suite, which passes
  at the head. No use case writes a `ve-document@2` document.
- **Theorem statements.** No theorem changed or was added. `discourse_wire_acceptance` still states that a
  successful `admission` answer is `encodeAdmission` of a checked admission, and `encodeAdmission` now appends
  `jointFields`.
- **Answer binding (lf-4 review B).** After the corpora above were recorded, `ve/discourse.py` began binding
  every member of Lean's answer that it reads to the loaded document (`_bind_answer`). That covers the units'
  statuses, the references, the bound units, the validity claims, the report id and the joint set: choices
  in range, in the enumeration's strictly increasing order, UNKNOWN exactly over the budget, and the
  disjunction its choices denote. An answer that fails is `CheckerUnavailable`. A genuine answer always passes
  (`tests/test_discourse_answer.py::test_genuine_answers_are_bound` and the suite), so no public result of the
  corpora should change. The A/B tool was not rerun. Every one- and two-fault mutant of five genuine answers is
  `CheckerUnavailable` or shown identically (`test_genuine_answer_mutants_never_pass_as_answers`).
  The unit statuses and validity verdicts are bound by key membership, not key order, because Lean emits
  JSON object keys in lexical order (lf-4 looprecheck1 B). Every genuine answer with every object's keys
  reversed or sorted is shown identically (`test_object_key_order_is_no_part_of_the_answer`). The joint
  conjunction and disjunction are built without Python recursion. A joint set over 1,000 open sets passes
  (`test_a_joint_set_deeper_than_pythons_call_depth_is_admitted`). An answer nested deeper than the C stack
  can read is `CheckerUnavailable` (`test_an_answer_deeper_than_the_c_stack_is_no_answer`).
  This change leaves one earlier, fail-closed limit in place. A constrained joint set whose disjunction is
  deeper than Python's AST budget (`ve/limits.py`, depth 64), such as 64 choices over six sets, is still
  `CheckerUnavailable` when `_report` decodes the disjunction as a premise.
- **Stale prose.** `docs/spec/discourse.md` 4.1(6) and its history sections, and a doc comment in
  `lean/VE/Discourse/Grammar.lean` (frozen, rebuilt only with a Lean change), still name Python's deleted
  `reference_surfaces` as a second implementation.
