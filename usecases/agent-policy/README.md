# Agent permission policy, checked in VE

This case checks a tool-use policy for a coding assistant agent, and an action log of that agent, both
**written directly in VE**. The policy author writes VE norm rules. The agent and its tools emit VE facts. No
English source is translated, so no translation-fidelity metric applies. The case measures what VE can
**check**: conflicts and gaps in the policy, and a decision for each logged action.

The policy is **authored for this use case**. It is modelled on public material ([sources.md](sources.md)),
but it does not reproduce any published policy. The plan, with the answer key written before VE was run, is
[PLAN.md](PLAN.md). Section 12 of the plan lists every deviation.

| File | Contents | SHA-256 |
|---|---|---|
| [policy.ve](policy.ve) | 26 rules; [policy.manifest.json](policy.manifest.json) binds them to their names | `42de2a255d9647e018ba084dcf49a0d8a9c83b816e0f8b9a3fa848df7046f7cd` |
| [log.ve](log.ve) | an inventory of 10 files, 5 hosts and 3 people, then 42 action records (501 sentences) | `1e329a6e5644afafb8ac62ffaba77394012c1f453be6d044a7811bdcf65186e3` |
| [log-schema.ve](log-schema.ve) | six assumptions about log records, used only by the gap queries | `8cec9bce64eb45802decc4f11f373e9d4f1ddd105b1f9220ae2b1218d80b4c3f` |
| `environment.*.json` | the vocabulary, in four copies that differ only in the two defaults, plus a Lean copy | |
| `environment.unspecified*.json` | both defaults `unspecified` under `norm-defaults@0`, plus a flag-free Lean copy | |
| [answer-key.json](answer-key.json) | PLAN sections 6, 7 and 11 as data | |
| [check.py](check.py), [focused.py](focused.py) | the harness that runs VE on every case | |
| [unspecified.py](unspecified.py) | the re-run with both defaults `unspecified`, replayed in Lean | |
| [results.json](results.json) | everything the harness computed | |

## Result: agreement with the answer key

VE agrees with the answer key on **42 of 42** actions. There is no disagreement to report.

| Metric | Result | Expected |
|---|---|---|
| M1 verdicts | 42/42 | 42/42 |
| M2 deciding rules (and the open rules of UNDETERMINED actions) | 42/42 | 42/42 |
| M3 actions approved or rejected although no rule selects them | 0 | 0 |
| M4 actions whose completed outcome changes with the default | a27, a36, a37, a38 | the same four |
| M4 with the default `unspecified`: actions whose permission the policy does not settle | a27, a36, a37, a38 (UNDECIDED) | the same four |
| M5 policy findings | as expected (below) | section 7 |
| M6 seeded defects found | 4/4 | 4/4 |
| M7 mutants that change exactly the named results | 6/6 | 6/6 |
| M8 selected rules on the finite model versus entailment (complete records a01 to a39) | 39/39 | 39/39 |
| M8 independent Python reading ([reference_policy.py](reference_policy.py)) versus VE | 42/42 | 42/42 |

The confusion matrix is diagonal: 16 APPROVED, 19 REJECTED, 4 NOT-COVERED, 1 CONFLICT and 2 UNDETERMINED.

## The policy and the check status of each rule

All 26 rules are **CHECKED**. Each one parses with exactly one reading, and VE renders the parsed rules back to
the same bytes. No rule is LABELLED, OPEN or UNFORMALISED. The facts a rule reads, such as "a file is
confidential" or "an action is confirmed", are decided by named tools outside VE (see "What stayed OPEN").

Every prohibition (rules 13 to 24) takes precedence over every permission (rules 1 to 12), except for one
missing edge (defect D1). A permission for a confirmed action is a separate rule, because an exception does
not inherit the guard of the rule it overrides.

| Rule | Name | In plain English | Status |
|---|---|---|---|
| 1 | read-workspace | An action may read a file in the workspace. | CHECKED |
| 2 | read-confirmed | A confirmed action may read a file. | CHECKED |
| 3 | write-workspace | An action may write a file in the workspace. | CHECKED |
| 4 | delete-workspace | An action may delete a file in the workspace. | CHECKED |
| 5 | shell-read-only | A read-only shell command may run. | CHECKED |
| 6 | shell-confirmed | A confirmed shell command may run. | CHECKED |
| 7 | network-allowlisted | An action may contact a host on the allowlist. | CHECKED |
| 8 | network-confirmed | A confirmed action may contact a host. | CHECKED |
| 9 | message-user | An action may message the user. | CHECKED |
| 10 | purchase-confirmed | A confirmed purchase may be made. | CHECKED |
| 11 | secret-fetch-confirmed | A confirmed secret fetch may be made. | CHECKED |
| 12 | credential-read-confirmed | A confirmed action may read a confidential file. | CHECKED |
| 13 | read-outside | An action must not read a file outside the workspace, unless it is confirmed. | CHECKED |
| 14 | write-outside | An action must not write a file outside the workspace. It does not override rule 3 (D1). | CHECKED |
| 15 | delete-outside | An action must not delete a file outside the workspace. | CHECKED |
| 16 | delete-untracked | An action must not delete an untracked file, unless it is confirmed. | CHECKED |
| 17 | shell-changes | A shell command that is not read-only must not run, unless it is confirmed. | CHECKED |
| 18 | network-unlisted | An action must not contact a host off the allowlist, unless it is confirmed. | CHECKED |
| 19 | message-others | An action must not message anyone but the user, unless it is confirmed (D2). | CHECKED |
| 20 | purchase-unconfirmed | A purchase must not be made, unless it is confirmed. | CHECKED |
| 21 | purchase-over-limit | A purchase over the spending limit must not be made. | CHECKED |
| 22 | elevated | An action with elevated privileges must not run. | CHECKED |
| 23 | disclose-secret | An action that discloses a secret must not run. | CHECKED |
| 24 | credential-read | An action must not read a confidential file. | CHECKED |
| 25 | report-delete | An action that deletes a file must be reported to the user. | CHECKED |
| 26 | report-purchase | A purchase must be reported to the user. | CHECKED |

The plan's rule 25 ("deletes a file or is a purchase") is written as rules 25 and 26. VE's English has no
one-line form for that disjunction (PLAN section 12, item 4).

## Decision for each logged action

VE decides each action from the inventory and that action's own record. APPROVED means some permission is
selected, no prohibition is, and no prohibition is left open. REJECTED is the mirror case. NOT-COVERED means VE
proves that no rule selects the action. CONFLICT means a permission and a prohibition are both selected.
UNDETERMINED means a missing fact leaves a rule open. VE shows this with two checked models of the same record
that disagree.

The "deny" and "allow" columns give the completed outcome when the environment's default is to forbid or to
permit: P (permitted), F (forbidden), ⊥ (the record contradicts the rules) or ? (not decided).

| Action | What it is | Verdict | Deciding rules | deny | allow | Report (rules 25 and 26) |
|---|---|---|---|---|---|---|
| a01 | read `src/app.py` | APPROVED | 1 | P | P | not covered |
| a02 | read `README.md`, confirmed | APPROVED | 1, 2 | P | P | not covered |
| a03 | read `/etc/hosts` | REJECTED | 13 | F | F | not covered |
| a04 | read `/etc/hosts`, confirmed | APPROVED | 2 | P | P | not covered |
| a05 | read `.env` | REJECTED | 24 | F | F | not covered |
| a06 | read the SSH key, confirmed | REJECTED | 24 | F | F | not covered |
| a07 | edit `src/app.py` | APPROVED | 3 | P | P | not covered |
| a08 | append to `~/.bashrc` | REJECTED | 14 | F | F | not covered |
| a09 | append to `~/.bashrc`, confirmed | REJECTED | 14 | F | F | not covered |
| a10 | one patch to `src/app.py` and `~/.bashrc` | **CONFLICT** | 3 permits, 14 forbids | ⊥ | ⊥ | not covered |
| a11 | delete `build/cache.bin` | REJECTED | 16 | F | F | required |
| a12 | delete `build/cache.bin`, confirmed | APPROVED | 4 | P | P | required, and reported |
| a13 | delete `README.md`, not reported | APPROVED | 4 | P | P | required, **not reported** |
| a14 | delete another project's notes, confirmed | REJECTED | 15 | F | F | required |
| a15 | `git status` | APPROVED | 5 | P | P | not covered |
| a16 | `pytest -q` | REJECTED | 17 | F | F | not covered |
| a17 | `pytest -q`, confirmed | APPROVED | 6 | P | P | not covered |
| a18 | `sudo apt install jq`, confirmed | REJECTED | 22 | F | F | not covered |
| a19 | `pip install requests`, confirmed | APPROVED | 6, 7, 8 | P | P | not covered |
| a20 | `curl` from pastebin.com | REJECTED | 18 | F | F | not covered |
| a21 | fetch a github.com page | APPROVED | 7 | P | P | not covered |
| a22 | fetch the weather API | REJECTED | 18 | F | F | not covered |
| a23 | fetch the weather API, confirmed | APPROVED | 8 | P | P | not covered |
| a24 | send `.env` to pastebin.com, confirmed | REJECTED | 23, 24 | F | F | not covered |
| a25 | email the user a summary | APPROVED | 9 | P | P | not covered |
| a26 | email a colleague | REJECTED | 19 | F | F | not covered |
| a27 | email a colleague, confirmed | **NOT-COVERED** | none | F | P | not covered |
| a28 | chat to the user, copied to an external list | REJECTED | 19 | F | F | not covered |
| a29 | chat to the user and a colleague, confirmed | APPROVED | 9 | P | P | not covered |
| a30 | email the user a file with an API key | REJECTED | 23 | F | F | not covered |
| a31 | buy a $5 credit, confirmed | APPROVED | 10 | P | P | required, and reported |
| a32 | buy a $5 credit | REJECTED | 20 | F | F | required |
| a33 | buy $900 of GPU hours, confirmed | REJECTED | 21 | F | F | required |
| a34 | buy $900 of GPU hours | REJECTED | 20, 21 | F | F | required |
| a35 | fetch the deploy token, confirmed | APPROVED | 11 | P | P | not covered |
| a36 | fetch the deploy token | **NOT-COVERED** | none | F | P | not covered |
| a37 | register a nightly job | **NOT-COVERED** | none | F | P | not covered |
| a38 | start a sub-agent | **NOT-COVERED** | none | F | P | not covered |
| a39 | write the user's crontab | REJECTED | 14 | F | F | not covered |
| a40 | read `/etc/hosts`; the confirmation is missing | **UNDETERMINED** | 2 and 13 open | ? | ? | not covered |
| a41 | write a symbolic link; its location is unknown | **UNDETERMINED** | 3 and 14 open | ? | ? | not covered |
| a42 | read `src/app.py`; the confirmation is missing | APPROVED | 1 (2 open) | P | P | not covered |

Seven pairs differ only in the confirmation. In six of them it lifts a prohibition: a03/a04, a11/a12,
a16/a17, a22/a23, a26/a27 and a31/a32. In a35/a36 no prohibition applies; the confirmation activates the
permission of rule 11, and without it a36 is NOT-COVERED. The confirmation does not help in a05/a06, a08/a09
or a33, because those prohibitions have no carve-out.

No action is approved or rejected by a default. The four NOT-COVERED actions are forbidden under the deny
default and permitted under the allow default, and they are the only ones that change (M4). In a10 the
conflict makes every completed outcome a contradiction, the report obligation included, although no reporting
rule applies to a10. This is how classical logic treats inconsistent premises; the verdict CONFLICT is the
useful answer there.

**The reporting obligation.** Rules 25 and 26 cover 8 actions (a11 to a14 and a31 to a34), and no rule covers
the other 34. Under the "need not be reported" default, one approved action is not reported although it must
be: **a13**. Under the "must be reported" default, 13 more approved actions become breaches: a01, a02, a04,
a07, a15, a17, a19, a21, a23, a25, a29, a35 and a42.

## With the default `unspecified` (norm-defaults@0)

The policy states no default, so the four environments above each add one it does not state.
`environment.unspecified.json` says what the policy says instead: where no rule decides, the text is silent
(`docs/spec/norm-defaults.md`, fixture u4). [unspecified.py](unspecified.py) computes the status of
`permitted(a)` and `report_required(a)` for the 39 records that are one finite model (a01 to a39; a40 to a42
leave facts open, so their situation is not one model and they are not in this check). Lean's norm-defaults route
replays every status, the a10 conflict witness and both gap witnesses: **81 of 81 agree**, on a flag-free copy of
the environment, as for the norms route (the statuses are the same without the flags; the harness checks this).

**The verdicts do not change.** The harness's verdict never reads the default, so all 42 verdicts, the deciding
rules and the policy findings stay as above. What changes is the completed outcome, and only where a default
decided it:

| Action | Predicate | Before: deny / allow (or need not / must) | After | Why |
|---|---|---|---|---|
| a27, a36, a37, a38 | `permitted` | F / P | **UNDECIDED** | no rule decides the action (NOT-COVERED), and the policy states no default |
| the 30 complete records that rules 25 and 26 do not cover, a10 excepted | `report_required` | F / P | **UNDECIDED** | no reporting rule covers the action, and the policy states no default |
| a10 | `report_required` | ⊥ / ⊥ | **UNDECIDED** | no reporting rule covers a10. A completed outcome was a contradiction because of the permission conflict; the status ranges over every admissible filling, and fillings answer either way |
| every other point | both | | unchanged | a rule decides it: SETTLED with the same value, and a10's `permitted` is still a CONFLICT between rules 3 and 14 |

So `permitted` is UNDECIDED exactly on the four actions the key marks as forced by the default (M4), and nothing
a rule decides moves. Both predicates have reachable gaps (a27 is a witness for each), and neither inherits
undecidedness from the other (`inherits_from` is empty: rules 25 and 26 do not mention permission).

**Reporting breaches.** a13 is still a breach: rule 25 requires the report, and no default is involved. The
other approved, unreported actions were breaches only under the "must be reported" default. Now the policy
does not say whether they must be reported: a01, a02, a04, a07, a15, a17, a19, a21, a23, a25, a29 and a35 are
UNDECIDED (a42 is outside the finite-model check; the key's entry for it is unchanged).

The four shipped environments stay as regressions, and the answer key is unchanged.

## Policy-level findings

| Finding | Result | Evidence |
|---|---|---|
| Conflicting rules | `permitted` has a **CONFLICT**: rule 3 permits and rule 14 forbids an action that writes one file inside and one outside the workspace (a10). `report_required` is **CONFLICT-FREE**. | a checked witness model (a10's record); a certificate for `report_required` |
| Rule pairs that can conflict | 1 of the 144 permission/prohibition pairs: **(3, 14)**. The other 143 are refuted. | a10's model; 143 certificates |
| Rules that can never decide | **rule 12**. Its guard implies rule 24's guard, and rule 24 overrides it. | a certificate |
| Rules that can never apply | none: every rule applies to some logged action | a record model for each rule |
| Tools that a well-formed record may leave uncovered | **send_email** and **post_message** (a confirmed message to people other than the user), **get_secret** (an unconfirmed fetch), **schedule_task** and **spawn_agent** (no rule mentions them), and any **undeclared tool** | a checked witness model for each |
| Tools always covered | read_file, write_file, delete_file, shell, web_fetch and purchase | a certificate for each |
| Actions no rule covers in the log | a27, a36, a37 and a38 | the per-action proofs above |
| Same-sign overlaps (not conflicts) | (1, 2), (6, 7), (6, 8), (7, 8), (20, 21) and (23, 24) | the record models of a02, a19, a34 and a24 |

A well-formed record is one that meets [log-schema.ve](log-schema.ve): a file tool touches some file, a web
fetch contacts some host, and a mail or chat action messages some person. These are assumptions about the log,
not rules of the policy. VE's models may contain a tool name that the environment does not declare, so an
action with such a tool is a gap too.

**The four seeded defects were all found (M6).**

- D1, a missing precedence edge: a10 is a CONFLICT, and the pair (3, 14) is the only satisfiable pair.
- D2, "must not … unless confirmed" with no rule permitting the confirmed case: a27 is NOT-COVERED, and
  send_email and post_message are gaps.
- D3, an unmentioned complement: a36 is NOT-COVERED, and get_secret is a gap.
- D4, a permission that can never decide: rule 12 never decides.

## Mutants (M7: 6 of 6)

| Mutant | Change | What changed |
|---|---|---|
| m1 | add rule 3 to rule 14's exceptions (fixes D1) | `permitted` becomes CONFLICT-FREE; a10 becomes REJECTED by rule 14; no pair can conflict |
| m2 | add rule 27, a permission for confirmed messages to others, overridden by rules 13 to 24 (fixes D2) | a27 becomes APPROVED by rule 27; a29's deciding rules become 9 and 27; the send_email and post_message gaps close; 156 pairs, and still only (3, 14) conflicts; new overlap (9, 27) |
| m3 | shorten rule 2 to "that action is confirmed" | a27 becomes APPROVED by rule 2; rule 2 joins the deciding rules of a12, a17, a19, a23, a29, a31 and a35; the send_email and post_message gaps close for the wrong reason; the other gaps stay |
| m4 | delete a01's closure sentence for reads | a01 becomes UNDETERMINED with rules 1, 13 and 24 open |
| m5 | remove rule 12 from rule 24's exceptions | a06 becomes a CONFLICT between rules 12 and 24; the pair (12, 24) can conflict; rule 12 now decides |
| m6 | state that a36 is confirmed | a36 becomes APPROVED by rule 11 |

In m3, rule 2 also overlaps with each rule it now shares an action with. That follows from the named change.

## Where VE forced a choice

1. **Completion defaults (resolved by `norm-defaults@0`).** `norms@0` requires a default for each regulated
   predicate, and allows only "deny" or "allow". The policy states none. The case therefore ships four
   environments with each combination, and the verdict never reads the default; VE's completed outcome for a27,
   a36, a37 and a38 was whatever default the environment was given. `environment.unspecified.json` no longer
   forces a choice: those four are UNDECIDED (see "With the default `unspecified`" above).
2. **Precedence edge by edge.** `norms@0` has no "every prohibition overrides every permission" declaration.
   The 143 edges are listed rule by rule, and omitting one of them is defect D1.
3. **The spending limit.** VE cannot compare amounts over a variable action here, so the payment tool emits a
   yes-or-no `affordable` fact.
4. **Workspace containment.** The path resolver emits whether a file resides in the workspace. The optional
   directory-tree variant (PLAN section 8, part E) was not built.
5. **Confirmation.** A confirmation is a flag on the action, not an act by the user.
6. **Wording.** VE's vocabulary rules decided the words of the facts, such as "is principal" for "is the user"
   and "is confidential" for "is a credential file" (PLAN section 12, item 2).

## Evidence (M9) and cost (M10)

- **2,488 certificates**, each replayed by VE's Python checker and then by **Lean: 2,488 valid**. Of these,
  2,325 are over the base environment. The other 163 are completed-outcome certificates. Lean replays those on
  the P0 route with the norm layers passed as ordinary premises, which checks the inference but not the layer
  generation.
- **87 model evaluations** (witnesses and the paired models of OPEN results) re-evaluated by **Rust: 87 agree**.
- **Lean norms route** on the flag-free environment: the `permitted` conflict witness replays as CONFLICT.
  Python checks the same model against the `tool` flags. The obligation rules replay as CONFLICT-FREE, and so
  does the whole fixed policy of mutant m1. A certificate over fewer premises stays valid when the flags are
  added; that step is an argument, not a Lean proof.
- **UNKNOWN results: 0.** Every rule selection was either proved or shown OPEN by two checked models.
- **Cost:** 1,237 calls to VE's prover (88,562 steps) and 1,266 focused searches (36,454 nodes). The base run
  took about 115 seconds with 6 worker processes; the six mutants took 26 to 105 seconds each.

VE's prover alone could not decide the selection formulas: it runs out of steps on a permission rule that
negates 12 prohibitions. The harness therefore proves each rule's guard with VE's prover first. Then the
focused search in [focused.py](focused.py) proves the selection formulas from those results. The search only
chooses among VE's own tableau rules, and VE's checker and Lean replay everything it produces (PLAN section 12,
item 6).

## What stayed OPEN, and why

1. **The truth of the log.** VE proves consequences of the facts. It does not establish them. The shell
   classifier, the path resolver, the network layer, the data-loss scanner, git and the payment tool decide
   them.
2. **Numbers and totals.** A per-action amount, a daily budget or a rate cannot be written over a variable
   action, because `order@0` forbids quantifying over integers.
3. **Time.** "Confirmed before the action", "reported after it", and permissions that expire are not
   expressible.
4. **An unspecified default.** Closed by `norm-defaults@0`: with the default `unspecified`, an uncovered action's
   permission and an uncovered action's report obligation are UNDECIDED, not the environment's default. The
   statuses of a40 to a42, whose records are not one finite model, are not computed.
5. **A combining algorithm.** "Deny overrides allow" has to be written as 143 edges.
6. **The speech-act items below.**

## What would need speech acts

| Item | Now | With speech acts |
|---|---|---|
| "the user has confirmed it" | a flag the harness emits; the agent could emit it too | an assent by the user, bound to the action and made before it |
| who asked for the action (the user, or text inside a fetched page) | not expressible | directive acts with a speaker, so a rule can require that the user asked |
| standing permissions ("always allow `npm test`") and revoking them | a policy edit | a grant or revocation that changes the permissions from then on |
| rules 25 and 26, "must be reported to the user" | a `reported` flag | a statement by the agent to the user about the action |
| messages sent for the user (a26 to a30) | recipients only | whose claims a message carries, the user's or the agent's |
| handing work to a sub-agent (a38) | an uncovered tool | commands passed to the sub-agent, and which policy binds it |

## How to run

From the repository root, with `~/.elan/bin` on `PATH`:

```sh
python usecases/agent-policy/check.py base --write       # every action and the policy queries
python usecases/agent-policy/check.py mutants --write    # the six mutants (several minutes)
python usecases/agent-policy/check.py replay --write     # Lean and Rust replay of the base evidence
python usecases/agent-policy/unspecified.py --write      # the default `unspecified`, with Lean replay
pytest -q tests/test_agent_policy.py tests/test_agent_policy_rerun.py tests/test_agent_policy_unspecified.py
```

`tests/test_agent_policy.py` checks the files, the answer key against the plan, and `results.json` against
the key. `tests/test_agent_policy_rerun.py` reruns VE on every action and policy query and fails on any change
from `results.json`. `tests/test_agent_policy_unspecified.py` recomputes the `unspecified` statuses and checks
each changed outcome against the key.
