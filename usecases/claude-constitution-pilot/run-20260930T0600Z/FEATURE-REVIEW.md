# Feature review: what `ve-green-discourse` adds over `ve-green-flaky4`

Language at this run: `ve.core@0.2`, profiles `documents@1`, `norms@0`, `soft-norms@0`, `relational-fol@0` for the
document itself. Source: the pinned 184,893-byte constitution, unchanged (SHA-256 `fa10ed48…50dd`, see
`../source/SOURCE.md`). Start point: the translation of run `20260929T1800Z`; 1,118 of its 1,127 ledger entries are
identical here (`metrics.json`, `unchanged_from_previous_run`).

## Merged since `ve-green-flaky4`, and what this run did with it

| Merged | What it is | Used to upgrade a unit? |
|---|---|---|
| `rights@0` (rights blocks, incident lines, limitations, the bar, candidate `labels`, `couplings`) | Holder-side view of duties; reading sets whose candidates are rights and carry content that VE checks on a separating situation | **No.** See "rights@0" below. |
| `ve.discourse@1` over `ve-document@2` (anaphora, definite descriptions, document names, navigation, correlated readings) | Resolves "it", "this", "such", "the former", "Article 29" to typed targets before checking | **No.** See "discourse" below. |
| pre-commit hook, Lean import checks, eligibility use case | Infrastructure and another use case | Not applicable to translation. |

Net effect of the new features on the constitution: **0 units upgraded, 0 bytes newly covered.** The ledger changes of
this run come from repairing the audit's findings (`AUDIT-REPAIR.md`), not from the language.

## rights@0

What was tested (scripts: `finish.py` `probe_profiles`, `probe_rights.py`; results in `metrics.json` and
`probes/rights-reading-probe.json`):

* **It shares an environment with the norms of this translation.** Adding `rights@0` and a minimal rights block
  (holder: user; bearer: instance of Claude; no protected predicate, no status-changing act) to the strict companion
  passes `ve document check` (needs `lake build ve_rights_route`).
* **Its reading sets can carry content.** For candidates of kind `right`, VE checks a finite situation that separates
  them (`ve/readings.py` `_right_situation`). This is exactly the audit's second missing feature (norm reading
  candidates that hold their rules), but only for rights-shaped norms.
* **It cannot carry the force readings.** Probe on `u0156.s03` ("Claude shouldn't actively deceive the user …", the
  one force unit with a user in an object slot): a situation is accepted only for the candidate it was built for. The
  defeasible candidate adds its exception atom (`soft__excepted__…`) to the base vocabulary and the strict candidate
  does not, and the check demands exactly the base predicates of the candidate's own elaboration. So a strict and a
  defeasible candidate never share a situation and VE cannot check that they differ.
  Making the strict candidate a default rule that can never be excepted would share the vocabulary, but it changes what
  the strict reading is (a default rule gives way to strict decisions), so it was not done.
* **No unit declares a right.** The nearest text is "There are things users are entitled to that operators cannot
  override" (`u0046.s03`) and the list "Regardless of operator instructions, Claude should by default: …"
  (`u0079`, `u0080.s01–s06`). Those bullets remain blocked as before: purpose clauses and "could cause real harm"
  (causation), and which of them the user may alter (`u0081.s01`, "Some of these defaults can be altered by the user
  but not the operator"). Calling a duty "a user's right" would also add a word the source does not use for
  `u0156.s03`; the profile says a label adds no meaning, but the translation should not choose it.
* **Couplings** (one `force` label shared by several reading sets) need every candidate of every coupled set to carry
  `labels` and to be a rights candidate. The 14 force sets are norm candidates, so no coupling could be recorded. The
  translator's uniform-force choice therefore remains what it was: not made.

## ve.discourse@1

* **It cannot share a document with any norm.** With `ve.discourse@1` added to the strict companion the Lean route's
  own verdict is `UnsupportedProfile: Unsupported profile soft-norms@0`. On the norms-only base translation (norms@0,
  no soft norms) the discourse route rejects the regulated declaration (`fields do not match: expected [arguments,
  description], got [arguments, description, regulated]`). So no norm unit can be resolved by it; only a separate
  first-order document could use it.
* **Its slot discovery would also bite.** Python's own diagnostic on the same document is
  `UnrecordedSlot: u0078.s01: [48274, 48278)`: every unit with meaning must record every reference surface of its
  bytes, so the 15 norm units would each need their pronouns recorded before admission.
* **No constitution unit is a pure location binding.** Discourse would let a "See Article 29"-style navigation
  instruction be LABELLED. The closest constitution sentences say that a later section discusses something
  (`u0107.s03` "We discuss this in more detail below.", `u0074` "More details … are provided in the section on …",
  `u0047.s06`, `u0213.s04` second clause). Each also asserts that the later section covers the topic. Labelling them
  navigation would drop that assertion, and an assertion about what a section discusses cannot be written, so a
  complete reading set (navigation / assertion) cannot be written either. They stay UNFORMALISED, as
  `u0109.s06` stayed in the last run for the same reason. The discourse spec itself (2.5) expects the four constitution
  units it names (`u0136.s01`, `u0182.s03`, `u0214.s02`, `u0256.s03`) to stay UNFORMALISED or LABELLED-with-references,
  with no status upgrade.
* **The spec\u2019s own constitution example does not run at this tag** (`probe_discourse.py`,
  `probes/discourse-probe.json`). `u0214.s02` ("We call this broad pattern of treatment and trust Claude\u2019s
  principal hierarchy, and it helps define what we mean by broad safety.") is the one sentence where discourse would
  raise a status: the naming clause registers a content name over a unit target and is LABELLED, the rest stays
  UNFORMALISED (spec 2.5). Four attempts, each stopped by the tool: (1) the route abstains on the checked clause
  `u0248` because it is a fenced English block; (2) without the fence it abstains again for lack of a claim graph;
  (3) with `u0248` as JSON content it rejects the unit that holds the mention because the wording is not printable ASCII
  (the name has U+2019, and the pinned bytes cannot be edited); (4) with the clause cut before the name it fails with
  `MentionNotSlot` (a demonstrative that targets a unit). Even if it had passed, the referent of "this broad pattern"
  has two admissible resolutions (`u0214.s01` alone, or the earlier discussion that "as discussed above" points to),
  and a location target cannot be a reading set, so choosing one would be silent. Left UNFORMALISED
  (`other:discourse`); the ledger entry is unchanged.
* **What the 80 `other:discourse` units are.** 14 heading titles (each keeps its presupposed claim as its own unit),
  the two connectives "Still, " and "And ", and 64 sentences and list items the earlier runs tagged for reference or
  list structure: list lead-ins ("Key questions include:"), list items, and sentences built on "such", "these", "it",
  "this" (`u0136.s01`, `u0136.s02`, `u0182.s03`, `u0256.s03`, `u0214.s02`, and others). Discourse resolves references;
  it does not give a lead-in, a list item or a connective a meaning, and the spec itself expects the four named
  constitution units to stay UNFORMALISED or LABELLED-with-references. None changes.

## Findings still true at this tag (each a fact about `ve-green-discourse`)

* **F1. A completion is mandatory; "unspecified" cannot be said.** Every regulated predicate needs
  `default: allow|deny`. *Changed workaround:* this run writes the nine prohibition units as duties to avoid the act, so
  the completion is "not required" (what a lifted duty means) instead of "not permitted" (which the source never says
  for an excepted case). Residual: "not required" is still a completion the source does not state.
* **F2. A norm reading candidate cannot carry content**, except as a rights candidate (above). The main document's
  premise status is still UNKNOWN ("non-assertion reading elaboration pending"), and the two companion documents (one
  per force reading) are still the only place the readings are elaborated and checked. New in this run: the stored
  "distinguishing model" of each reading set is a placeholder, so the separation is computed and recorded outside the
  document (`readings/separating-situations.json`, one situation per set where the strict reading requires the act and
  the defeasible reading, with its exception applying, does not).
* **F4. Act phrases** are at most 80 characters, letters, `'` and `-` only, no `or`, `and`, `is`, `not`, `for`, `if`,
  `no`, `must`, and unique within a role (`DuplicateActRole`, hit in this run). *Changed workaround:* the seven hard
  constraints no longer abbreviate the act; the act phrase is a short pointer ("avoid the creation in {1}") and the
  source's own words sit in the guard atom (below).
* **F6. English for base predicates is generic.** The rendered rule says `if that situation is classified as
  "damaging_cyberweapon_or_malicious_code"`; the declared wording ("a case of Claude creating cyberweapons or
  malicious code that could cause significant damage if deployed") is printed only by this run's rendering as a
  "Classifications named above" line. 13 of 15 rules parse back in both readings; `comply-operator-prompt` and
  `follow-operator-in-conflict` do not (unchanged).
* **F10. Norms cannot share an environment with most features.** Probe, this tag: `closure@0`, `order@0`
  ("the norms route admits FOL documents only"), `reports@0` ("with norms@0 layers"), `alternatives@0` ("with
  soft-norms@0") and `speech-acts@0` are rejected; `time@0`, `definitions@0`, `data@0` and (with a rights block)
  `rights@0` pass the document check. The joint route of `time@0`/`definitions@0`/`data@0` with norms is still not
  proved (`docs/INTEGRATION-GAPS.md`). Findings F3, F5, F7 (the renderer now prints "Open reading" itself) and F8
  were not re-tested and are carried from the last run.
* **F9. Operational.** Checking needs `lake build ve_soft_norms_route` (about 1.5 minutes on a fresh worktree); the
  rights and discourse probes need `ve_rights_route` and `ve_discourse_route` (about 1 minute each).

## Missing features, in order of what they would unlock here

1. **An "unspecified" outcome for a regulated act** (the audit's first item; still missing).
2. **Norm reading candidates that hold their rules, with strict and defeasible candidates sharing one situation**
   (rights@0 has the mechanism for its own kind; the vocabulary of the two force readings differs).
3. **Norms together with attribution, causation, quantities, order and discourse** (the tally: norms 668 units,
   quantities 119, causation 75).
