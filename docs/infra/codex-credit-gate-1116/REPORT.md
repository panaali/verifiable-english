# codex-credit-gate-1116: no caller of ours can spend Codex credits

- Status: built and STAGED (`*.new-codexw` in `/home/seyran/code/manage-agents`); INSTALL WAITS FOR DECIDER READ (section 5).
- What changed: `codex-allowed.sh` loses its credit branch (the balance and has_credits never open it) and gains a credit stop
  that holds in every mode, `--ceiling` included; a new shim `c2b-codex-shim.sh` gates every spending `codex` call on
  ve-cloud-2 through the VM's live gate; `cloud2-codex.sh` starts that shim instead of `/usr/local/bin/codex`.
- Open items: none in this branch. No DRI signature is reserved and there are no DELTA rows (no Lean, no VE product code, no
  trust base: only manage-agents control-plane scripts). No Codex account setting or login was touched.
- SIZE: 77 product, 123 tests, 124 other hand-written lines (this report).

## 1. Spec (row note, decision reviews/dri-decisions-20261116-targets.md) and how each word is met

| Spec words | Where | Test (tools-local/test_codex_credit_gate.sh unless named) |
|---|---|---|
| "has_credits must never open the gate" / "remove codex-allowed.sh's credit branch" | credit branch deleted; past the plan cap the gate refuses: "Codex never runs on credits" | A1, A2, A3, A4 (fail on the installed gate: `credits: spent 2500 < allowance 33656`) |
| "when CODEX_WEEK_CEILING or the allowance closes it" | the ceiling block is unchanged; the allowance is gone with the branch | A11 (ceiling 97 closes 98), A12 (allowance spent), A14 (`caller * 0`), A13 (Astra) |
| "the credit branch opens ~Dec 17" | the clock no longer matters: no line of the gate reads the date for credits | A1/A2 use a balance whose paced allowance is open today, the state the branch would reach about 2026-12-17 |
| "no caller of ours can spend Codex credits" | CREDIT STOP in every mode: a reading at most CODEX_FRESH_MAX (900) s old, and week + 1 x (1 + sessions running) <= 100 | A5-A10 (fail on the installed gate: `no hard stop`), A15-A18 (what still runs) |
| "ve-cloud-2 /usr/local/bin/codex has no shim" / "gate ve-cloud-2's ungated codex with the shim" / "a call on ve-cloud-2 goes through the gate" | `c2b-codex-shim.sh`: on the host as `~/c2b/codex-shim.sh`, linked from `~/.local/bin/codex`; asks `ssh ve-cloud-1 zsh .../codex-allowed.sh --ceiling` | B0-B13 (B0 fails on the installed tree: no shim), D1 (live read of ve-cloud-2: fails until installed) |
| (the same) | `cloud2-codex.sh` runs `$RSHIM`, forwards CODEX_CALLER and PICK_ITEM, fails before sending when the host has no shim | C1-C6 (C1-C4 fail on the installed file) |
| "Do not change any Codex account setting or login" | nothing reads or writes auth.json, config.toml or the account; the shim and the gate only read the meter | n/a (no such command in the diff: `staged-changes.diff`) |

## 2. Design choices (conservative option taken each time, no DRI question needed)

1. **Credit stop at 100, in every mode.** Credits are spent by a run past the plan week's 100%. The VM shim and the host shim
   ask `--ceiling`, which before had no stop at all without a ceiling line in force (after 2026-11-26 no line of the live file
   is in force). The stop is not liftable by CODEX_WEEK_CEILING (A9: a "120" line), CODEX_PLAN_CAP or CODEX_USE_ALL (A10).
2. **A fresh reading is needed in every mode** (it was needed only under a ceiling line). A stale low reading is how the 11-11
   leak happened; with no ceiling in force the old gate opened on a 5-day-old reading (A7; in `test_codex_week_ceiling.sh`
   two cases relied on that and now read a fresh value, plus a stale case that refuses).
3. **The host shim asks the VM's live gate over ssh**, not the host's read-only mirror of manage-agents (its copy of
   `codex-allowed.sh` is from 11-16 06:09Z and of `CODEX_WEEK_CEILING` from 11-16 12:20Z, both older than the live files:
   `ls -la` on ve-cloud-2, 2026-11-17). Unreachable VM, missing gate or any exit but 0: refused, exit 75 (B3, B4). Only
   CODEX_CALLER and PICK_ITEM reach the gate, each refused unless a plain name (B10); the host's own CODEX_WEEK_CEILING and
   CODEX_NOW do not (B7). ve-cloud-2 reaches ve-cloud-1 with its existing peer key (`~/.ssh/config` there); no key or
   authorized_keys line was added.
4. **cloud2-codex.sh fails closed on a host without the shim** (C4): `fail` writes `<item>-c2b-failed`, so run_builder reruns
   on the VM, where the VM shim gates it. ve-cloud-3 (paused, `#PAUSED` in remote-hosts.tsv) therefore needs the same install
   before its lane opens again; see Notes.

## 3. Test runs (saved logs in this directory)

| Run | Command | Result |
|---|---|---|
| new test, staged files | `zsh tools-local/test_codex_credit_gate.sh <gate>.new-codexw c2b-codex-shim.sh.new-codexw cloud2-codex.sh.new-codexw` | PASS, 47 ok (`run-staged.log`) |
| new test, installed files | `zsh tools-local/test_codex_credit_gate.sh` | FAILED: A1-A10, B0, C1-C4, D1; 10 ok (`run-installed.log`) |
| staged ceiling test, staged gate | `zsh tools-local/test_codex_week_ceiling.sh.new-codexw <gate>.new-codexw codex-shim.sh` | PASS, 79 ok (`run-week-ceiling-staged.log`) |
| staged ceiling test, installed gate | same, installed gate | FAILED on exactly the 3 new cases (`run-week-ceiling-installed.log`) |
| installed ceiling test, staged gate | `zsh tools-local/test_codex_week_ceiling.sh <gate>.new-codexw codex-shim.sh` | FAILED on exactly the 3 changed cases (`run-week-ceiling-old-test-on-staged.log`): two stale readings, and the audit at 88 on the full gate that only the credit branch had opened |
| syntax | `zsh -n` (gate, cloud2-codex.sh, both tests), `bash -n` (host shim) | clean (B13, C6) |

Hashes of the staged and live files at hand-off: `sha256.txt`. Full staged diff: `staged-changes.diff`.

## 4. Seeded bugs (`seeded-bugs.json`; each a temp copy of one staged file, the test run on it)

| Id | File | Bug | Failing tests |
|---|---|---|---|
| S1 | manage-agents/codex-allowed.sh.new-codexw | credit branch back (balance > 0 opens) | A1, A3, A4, A12, A13 |
| S2 | manage-agents/codex-allowed.sh.new-codexw | credit stop only under a ceiling line | A8 |
| S3 | manage-agents/codex-allowed.sh.new-codexw | stop at 120 instead of 100 | A5, A6, A9, A10, B5 |
| S4 | manage-agents/c2b-codex-shim.sh.new-codexw | opens when the VM's gate cannot be asked | B4, B10 |
| S5 | manage-agents/c2b-codex-shim.sh.new-codexw | forwards the host's CODEX_WEEK_CEILING | B1, B7, B9, B11 |
| S6 | manage-agents/c2b-codex-shim.sh.new-codexw | drops the caller | B8 |
| S7 | manage-agents/cloud2-codex.sh.new-codexw | starts /usr/local/bin/codex again | C1, C2 |

All 7 caught (rc 1). No Lean, VE Python or Rust changed, so there is no seed in those languages.

## 5. Install (INSTALL WAITS FOR DECIDER READ)

No svc-* loop holds these files (each is a script started fresh per call), so there is no restart. Order matters: the
gate and its test together, then the host shim, then cloud2-codex.sh (which refuses a host without the shim).

```
M=/home/seyran/code/manage-agents; cd $M; B=bak-20261117-codexw
# 1. the gate and the ceiling test (VM)
cp -p codex-allowed.sh codex-allowed.sh.$B && mv codex-allowed.sh.new-codexw codex-allowed.sh
cp -p tools-local/test_codex_week_ceiling.sh tools-local/test_codex_week_ceiling.sh.$B && mv tools-local/test_codex_week_ceiling.sh.new-codexw tools-local/test_codex_week_ceiling.sh
# 2. ve-cloud-2's shim: the VM copy at its live name, then the host copy and the link (~/.local/bin/codex is absent today)
mv c2b-codex-shim.sh.new-codexw c2b-codex-shim.sh && chmod 755 c2b-codex-shim.sh
scp -q c2b-codex-shim.sh ve-cloud-2:c2b/codex-shim.sh.new && ssh ve-cloud-2 'mkdir -p ~/c2b/logs ~/.local/bin && chmod 755 ~/c2b/codex-shim.sh.new && mv -f ~/c2b/codex-shim.sh.new ~/c2b/codex-shim.sh && ln -sfn ~/c2b/codex-shim.sh ~/.local/bin/codex'
# 3. the lane wrapper (VM)
cp -p cloud2-codex.sh cloud2-codex.sh.$B && mv cloud2-codex.sh.new-codexw cloud2-codex.sh
# verify (both must print PASS; D1 reads ve-cloud-2)
zsh tools-local/test_codex_credit_gate.sh && zsh tools-local/test_codex_week_ceiling.sh
```

Undo: `mv codex-allowed.sh.$B codex-allowed.sh; mv cloud2-codex.sh.$B cloud2-codex.sh; mv tools-local/test_codex_week_ceiling.sh.$B tools-local/test_codex_week_ceiling.sh; rm c2b-codex-shim.sh; ssh ve-cloud-2 'rm -f ~/.local/bin/codex ~/c2b/codex-shim.sh'`.
`tools-local/test_codex_credit_gate.sh` is a new test at its final name (no live file before it; no service runs it).

## 6. Notes for the DRI

1. **Audits stop at the plan cap (88) on the full gate.** `caller audit 97` lets the ceiling block pass up to 97, but the full
   gate (run-codex.sh asks it) refuses at 88 and up now that the credit branch is gone. That was already the effect today:
   spent 53.3k > allowance, so the branch refused. Runs between 88 and 100 are paid by the plan, not credits; if the audits
   should use them, the lever is CODEX_USE_ALL or CODEX_PLAN_CAP (still under the credit stop at 100), not credits.
2. **run-codex.sh's Astra-to-Sol switch "on credits" (line 156) no longer fires**: Astra and Sol now get the same answer.
   Its comments still describe the credit rule; not edited (not needed for the gate; the comments are wrong only).
3. **Residual on ve-cloud-2:** a non-login `ssh ve-cloud-2 codex ...` (PATH without ~/.local/bin) still finds
   `/usr/local/bin/codex`. None of our scripts does that after this change (cloud2-codex.sh names the shim; c2b-job.sh and
   login shells put ~/.local/bin first). Closing it fully means replacing the root-owned npm link `/usr/local/bin/codex`,
   which an npm update would undo; not staged.
4. **ve-cloud-3** (paused) has the same ungated binary; run step 2 with `ve-cloud-3` before its lane opens, or cloud2-codex.sh
   fails there and the run goes back to the VM (fail closed).
5. The credit stop counts Codex sessions running on the VM only (as the ceiling's seat rule always did); a run on ve-cloud-2
   is not counted by a later start. The test knobs CODEX_FRESH_MAX, CODEX_SEAT_RESERVE, CODEX_RUNNING and CODEX_NOW still
   loosen the gate if a caller sets them; no caller does (unchanged from before).

## 7. Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no Lean answer relayed).
2. Every deliverable built, no rule broken: PASS (section 1 table; credit branch removed A1-A4, ve-cloud-2 shim B0-B13, C1-C6).
3. Tests and gates can fail: PASS (`run-installed.log` fails 16 cases; seeds S1-S7 in `seeded-bugs.json`).
4. Python, Lean and Rust agree: N.A. (none changed).
5. R8 binding: N.A. (no relay); the host shim refuses an unplain CODEX_CALLER/PICK_ITEM (B10).
6. Gate evidence matches the final HEAD: PASS (this branch holds evidence only; the chain gates the final HEAD).
7. No unsigned item left: PASS (no DELTA rows, no reserved signature).
8. User-visible change in DELTA: N.A. (no VE user-visible change).
9. Test selection still finds the tests: N.A. (no VE code changed; the manage-agents tests are run by hand, section 3).
10. Lean statements and proofs: N.A.
11. Budgets, limits and deadlines fail closed: PASS (no reading A8, stale A7, unreachable VM B3, missing gate B4, no host shim C4).
12. No CPU or memory regression: PASS (one ssh per spending call on ve-cloud-2, B2 counts it; the VM gate unchanged in cost).
13. Removed or renamed tests have a Test-removed trailer: N.A. (no VE test removed; 3 manage-agents cases changed, section 3).
14. Both directions, cited evidence, spec re-read: PASS (refuse A1-A14 and run A15-A18, B2/B6/B8/B12; section 1 re-reads each spec phrase).
15. No overclaim / no silent cut / every check can fail / limits before work: PASS ("no caller" is scoped in Notes 3-5; nothing cut; S1-S7; the gate is asked before the binary starts, B1).
