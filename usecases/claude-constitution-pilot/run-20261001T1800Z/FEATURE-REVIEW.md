# Feature review: what `ve-green-risk-c5` adds over `ve-green-risk`

Language at this run: `ve.core@0.2`, profiles `documents@1`, `norms@0`, `soft-norms@0`, `relational-fol@0` for the
document itself. Source: the pinned 184,893-byte constitution, unchanged (SHA-256 `fa10ed48…50dd`, see
`../source/SOURCE.md`). Start point: the translation of run `20260930T1800Z`, reproduced byte for byte by `build.py`;
all 1,127 ledger entries are identical (`metrics.json`, `unchanged_from_previous_run`).

## Merged since `ve-green-risk`, and what this run did with it

`git log ve-green-risk..ve-green-risk-c5` (322 files) holds two changes to what can be written (the c5 wording and the
discourse location bindings); everything else is the Lean/Rust migration (stage 2), the Rust build pin, the layers doc and
the release gate.

| Merged | What it is | Used to upgrade a unit? |
|---|---|---|
| `risk@0` c5 wording frozen | A sufficient condition on a risk cell is written "If `<condition>`, `<action>` leads to `<harm>`" (probe 2: 16/16 both readers). | **No.** It is a *record statement* only (docs/spec/risk.md 2.3): a condition on one cell of a decision record with estimates. The constitution contains no decision record and no estimate; the probe's verdicts for `u0087.s06`, `u0209.s07`, `u0141.s02`, `u0218.s13`, `u0218.s14` are identical to the previous run's (`probes/risk-probe.json`). The same three blockers hold: no attribution wrapper for "what a thoughtful senior Anthropic employee would not want", a harm list the source never gives, and `alternatives@0` rejects `soft-norms@0` (profile gate). |
| `ve.discourse@1` location bindings (spec 1.4, 4.1(4), 2.5; Lean `formFits`, `UnknownRule`) | A pronoun or demonstrative that names a *unit* ("this broad pattern of treatment and trust", "it") is a location binding: no slot, no formula, no discourse wording. `u0214.s02` is a regression fixture. | **Admitted in a companion probe, not in the translation.** See below. 0 units and 0 bytes upgraded in the main document. |
| Lean `readings`, argument composition, norm documents, Background validity on more families; Rust reproducible build; release gate | Checker authority and infrastructure. | Not applicable. All three documents check with the same verdicts as before. |

Net effect on the constitution: **0 units upgraded, 0 bytes newly covered.** The measured distance to the constitution
is therefore unchanged: 2,438 of 184,893 bytes claimed (1.32%); 1,714 substantive plus 325 label bytes audit-verified
(up from 935 plus 317 only because the last audit accepted units that were already covered).

## Discourse: what the new feature does for `u0214.s02`

Source (bytes 133,749 to 133,882): "We call this broad pattern of treatment and trust Claude's principal hierarchy, and it
helps define what we mean by broad safety." The previous run failed four ways. This run (`probe_discourse.py`,
`probes/discourse-probe.json`):

| Attempt | Previous run | This run |
|---|---|---|
| Naming clause cut before the name, two LABELLED fragments `u0214.s02.p1`, `.p1b`; `", and"` and the claim about broad safety kept UNFORMALISED; both mentions recorded as location bindings to `u0214.s01` under the content name "Claude's principal hierarchy" | `MentionNotSlot: m-this-pattern` | **accepted** at document-check level (both references have status `navigation`); coverage of the companion 100%, LABELLED 429 bytes (80 bytes more than the main translation), CHECKED 22 |
| The same block added to the real translation (norm units, soft norms, one fenced clause) | not tried | **rejected**: Python `UnrecordedSlot: u0078.s01: [48274, 48278)`; Lean's own verdict `UnsupportedProfile: Unsupported profile soft-norms@0` (`metrics.json`, `profile_combination_probe`); the route does not compose with norm and soft-norm units (spec 11) |
| The sentence kept whole as one unit | `InvalidInput: discourse wording` (curly apostrophe) | not used: a unit that holds a location binding must have no meaning, and labelling the whole sentence content-free would mislabel "it helps define what we mean by broad safety", a substantive claim (and a presupposition of the section). |

What this means: the language now *locates* "this" and "it" (they point at the previous sentence) but still does not
*say* anything: the naming claim ("we call X Y") is not a formula, and "helps define what we mean by broad safety"
needs a definition relation to an undefined term. The main document therefore keeps `u0214.s02` UNFORMALISED
(`other:discourse`). Counted gain for the main translation: 0. Potential gain in a norms-free companion: 80 label bytes.
Next asks: discourse composing with soft norms and fenced clauses; a naming/definition attribution ("we call");
a way to give a mention-bearing sentence a mixed unit where only part has meaning.

## Findings still true at this tag (each a fact about `ve-green-risk-c5`; F1, F2, F4, F6 and F10 were re-checked this run by the build, the three documents' checks, the probes and the profile gate; the others are carried)

* **F1. A completion is mandatory; "unspecified" cannot be said.** Every regulated predicate needs
  `default: allow|deny`. *Changed workaround:* this run writes the nine prohibition units as duties to avoid the act, so
  the completion is "not required" (what a lifted duty means) instead of "not permitted" (which the source never says
  for an excepted case). Residual: "not required" is still a completion the source does not state.
* **F2. A norm reading candidate cannot carry content**, except as a rights candidate (`rights@0`, re-probed this run: same verdict, `probes/rights-reading-probe.json`). The main document's
  premise status is still UNKNOWN ("non-assertion reading elaboration pending"), and the two companion documents (one
  per force reading) are still the only place the readings are elaborated and checked. New in this run: the stored
  "distinguishing model" of each reading set is a placeholder, so the separation is computed and recorded outside the
  document (`readings/separating-situations.json`, one situation per set where the strict reading requires the act and
  the defeasible reading, with its exception applying, does not).
* **F4. Act phrases** are at most 80 characters, letters, `'` and `-` only, no `or`, `and`, `is`, `not`, `for`, `if`,
  `no`, `must`, and unique within a role (`DuplicateActRole`, hit in the previous run). *Changed workaround:* the seven hard
  constraints no longer abbreviate the act; the act phrase is a short pointer ("avoid the creation in {1}") and the
  source's own words sit in the guard atom (below).
* **F6. English for base predicates is generic.** The rendered rule says `if that situation is classified as
  "damaging_cyberweapon_or_malicious_code"`; the declared wording ("a case of Claude creating cyberweapons or
  malicious code that could cause significant damage if deployed") is printed only by this run's rendering as a
  "Classifications named above" line. 13 of 15 rules parse back in both readings; `comply-operator-prompt` and
  `follow-operator-in-conflict` do not (unchanged).
* **F10. Norms cannot share an environment with most features.** Probe, this tag: `closure@0`, `order@0`
  ("the norms route admits FOL documents only"), `reports@0` ("with norms@0 layers"), `alternatives@0` ("with
  soft-norms@0"), `risk@0` ("requires alternatives@0") and `speech-acts@0` are rejected; `time@0`, `definitions@0`, `data@0` and (with a rights block)
  `rights@0` pass the document check. The joint route of `time@0`/`definitions@0`/`data@0` with norms is still not
  proved (`docs/INTEGRATION-GAPS.md`). Findings F3, F5, F7 (the renderer now prints "Open reading" itself) and F8
  were not re-tested and are carried from the last run.
* **F9. Operational.** Checking needs the Lean routes (`lake build` of the whole lakefile took about 4 minutes on a fresh worktree, and every check also needs the `uv run` environment: system python lacks `lark`); the
  rights and discourse probes need `ve_rights_route` and `ve_discourse_route` (about 1 minute each).

## Missing features, in order of what they would unlock here

1. **An "unspecified" outcome for a regulated act** (the audit's first item; still missing).
2. **Norm reading candidates that hold their rules, with strict and defeasible candidates sharing one situation**
   (rights@0 has the mechanism for its own kind; the vocabulary of the two force readings differs).
3. **Norms together with attribution, causation, quantities, order and discourse** (the tally: norms 668 units,
   quantities 119, causation 75).
4. **From risk@0:** a risk policy in the same document as soft norms (or soft norms inside `alternatives@0`), an open
   harm universe (harms described by a condition, not listed), and an attribution wrapper that can hold such a rule.
