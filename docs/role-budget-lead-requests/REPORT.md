# role-budget-lead-requests (2026-10-31): the picker's role hold does not hold work the lead asked for (PICK_LEAD=1)

Status: built and installed in manage-agents, which is not a git repository. This branch carries only this report.
Signature: none needed. There is no VE product code, no DELTA row and no Ruling cell.

Row: "Role budget must not hold work the lead asked for directly (dri-definability's analysts waited 2 h in the picker
under the design cap): a PICK_LEAD=1 env (set by DRI delegates tagged lead-request) skips the role hold; keep the token
caps". Note: "also DRI-critical delegates (sprint replans, revise launches): dri-lp1037 waited ~4 h on 2026-10-30 under the
management cap". Not done by another change: before this item, nothing in manage-agents read PICK_LEAD.

## Change (all in /home/seyran/code/manage-agents)

Each edited file went through a `.new` copy, `zsh -n` or `py_compile`, a backup `.bak-20261030-role-budget-lead-requests`,
then `mv`. One `dri-delegate.sh` run (dri-syn2-0401) was live while I installed. It keeps reading the old inode.

- `pick-claude-account.sh` `rolehold`: `PICK_LEAD` joins `PICK_LIGHT$PICK_FAST$PICK_COORD`, so a lead pick never calls
  `role-budget.py check`. Nothing else changed. `pick()` still applies the 5-h and weekly caps, the worker caps and the
  endgame limits. The load gate (`overloaded`) does not read PICK_LEAD.
- `tools-local/lead-request.sh <name> <prompt-file>` (new): exits 0 when the delegate counts as lead work. That is true in
  two cases. (a) The prompt file has a tag line `Tag: lead-request` or `Tags: ..., lead-request` (case-insensitive, whole
  word). (b) The name is a DRI-critical delegate: `dri-lp[0-9]*` (lead-prompt answers, as dri-lp1037), `*replan*` or
  `dri-sprint*` (sprint replans), or `*-revise*` or `*fid-rev*` (revise launches).
- `dri-delegate.sh`: `zsh $M/tools-local/lead-request.sh "$n" "$pf" && export PICK_LEAD=1` runs before its pick. The
  delegate's own pick inherits the variable, and so does every pick under it, such as the analysts a lead-requested
  delegate starts with `run-analyst.sh`. This covers the dri-definability case.

How the DRI tags a delegate: put a line `Tag: lead-request` in the delegate's prompt file. Reruns from the alert line keep
the tag because it lives in the prompt file.

## Tests (python3 -I tools-local/test_role_budget.py: Ran 15 tests, OK on the installed files; 10 before, 5 added)

| Claim | Test |
|---|---|
| PICK_LEAD=1 is not held (management and design over cap); without it, both are held (other direction) | PickerHold.test_exempt_lead |
| the token caps stay: 5-h 95 or weekly 95 refuses the only account for a lead pick (design and builder) | PickerHold.test_lead_keeps_token_caps |
| DRI-critical names are tagged (dri-lp1037, replans, dri-sprint, -revise, fid-rev); others are not (dri-checkin, dri-improve, dri-decide-1, dri-lp, dri-definability, ...) | LeadRequest.test_critical_names |
| prompt tag line: Tag/Tags, any case, list form; not tagged: prose, `lead-requests`, `not-lead-request`, an empty or missing file | LeadRequest.test_prompt_tag |
| dri-delegate.sh exports PICK_LEAD from lead-request.sh before its pick | LeadRequest.test_delegate_exports_before_pick |

These also pass on the installed files: `test_pick_mgmt.py`, `test_pick_longroom.py` and `test_endgame.py` (all OK).

## Seeded bugs (shell: pick-claude-account.sh, dri-delegate.sh, tools-local/lead-request.sh; each was run on a temp copy and the installed files were left unchanged)

| Mutant (file) | Failing test |
|---|---|
| `$PICK_LEAD` dropped from `rolehold` (pick-claude-account.sh) | PickerHold.test_exempt_lead |
| PICK_LEAD lifts the 5-h and weekly caps in `pick()` (pick-claude-account.sh) | PickerHold.test_lead_keeps_token_caps |
| `dri-lp[0-9]*` dropped from the names (tools-local/lead-request.sh) | LeadRequest.test_critical_names |
| tag match case-sensitive (`grep -qE`) (tools-local/lead-request.sh) | LeadRequest.test_prompt_tag |
| export line removed (dri-delegate.sh) | LeadRequest.test_delegate_exports_before_pick |

No Lean, Python or Rust product code of VE changed, so the per-language seeded-bug rule has no VE language to cover.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relay or Lean change)
2. Deliverables built, no rule broken: PASS (title: PICK_LEAD skips the role hold and the token caps stay; note:
   DRI-critical names. Running scripts were replaced by .new + mv with backups. PickerHold.test_exempt_lead,
   LeadRequest.test_critical_names)
3. Tests can fail: PASS (5 seeded bugs above, each caught)
4. Python/Lean/Rust agree: N.A.
5. R8 binding: N.A.
6. Gate evidence matches final HEAD: PASS (the chain gates the final HEAD; this branch only adds this file)
7. No unsigned item: PASS (no DELTA row)
8. User-visible change in DELTA: N.A. (no VE user-visible change; the picker is orchestration infra)
9. Test selection: N.A. (no VE code changed)
10. Lean statements: N.A.
11. Budgets fail closed: PASS (the exemption covers only the role hold. Account caps still refuse: PickerHold.test_lead_keeps_token_caps)
12. No CPU or memory regression: PASS (one extra `zsh` + `grep` per delegate launch; a lead pick skips `role-budget.py check`)
13. Removed tests: N.A. (none removed)
14. Both directions: PASS (exempt with PICK_LEAD and held without it; tagged names and lines, and the near misses that are
    not tagged: test_exempt_lead, test_critical_names, test_prompt_tag)
