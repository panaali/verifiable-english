# sol-vs-claude-12: Sol vs Claude builders, 12 merges each

**Status: built; ready for the chain's gate.** Branch infra/sol-vs-claude-12, merge base 4e961f0ad (main).
**Result: WORSE on the rule fixed in advance** (first-review FIX 8/12 vs 4/12; fix rounds 1.00 vs 0.50 per merge).
**What changed:** this folder only: docs and saved evidence. No product code, tests, flags or generated files.
**Open items:** the review's four wording and method notes below stay open in the report's text; `SOL_BUILDER_CAP` keeps
its "concurrent: 3" line until the DRI removes it. **No DRI signature needed; no DELTA rows; trust +0.**

## What this folder is

- `sol-vs-claude-20261103.md`: the comparison, a byte-for-byte copy of `reviews/sol-vs-claude-20261103.md` in
  manage-agents, which is the row's named output and what the DRI message cites. Its "evidence in" path means that
  folder; the two files below are the saved numbers from it.
- `evidence/items.json`: the 24 items: arm, builder, merge SHA, first review, first reviewer, fix rounds, lines, CW, Codex
  input tokens. `evidence/cw.json`: the Claude CW per item and role.
- The analysis scripts stay in manage-agents (`reviews/sol-vs-claude-20261103-evidence/`). They read logs that are not in
  this repository, so a copy here could not run.

The first build wrote all of this outside the repository and left the branch empty, which failed the pre-review gate
(`[commits]`). As fp-fulltext and fp-onedoc-per-source did, this round records the result under `docs/`. It changes no
number and no sentence of the comparison.

## Checks (each command run on this tree)

| claim | command | output |
|---|---|---|
| The copies match their sources | `cmp` on the report, items.json and cw.json | no difference, exit 0 |
| The report is within 60 lines | `wc -l sol-vs-claude-20261103.md` | 44 |
| The verdict counts hold | recount of `evidence/items.json` | sol: 12 items, FIX 8, rounds 12; claude: 12 items, FIX 4, rounds 6 |
| The size and cost means hold | same recount | median code lines 402 vs 225; CW 0.59M vs 1.28M; Codex 149M vs 17M |
| Every item is a real merge | `git merge-base --is-ancestor <merge_sha> main` for each | 24 distinct SHAs, all on main |
| The cap was not edited | `stat SOL_BUILDER_CAP`; `grep concurrent` | last changed 2026-11-02 09:12Z, before the item started at 13:23Z; line present |

The gap is 4 first-review items, above the one-item INCONCLUSIVE band, so the rule gives WORSE.

Done in the first round and not repeated: the DRI message (`inbox/dri/20261102T134053Z-sol-vs-claude-12-2648482.md`) and
the CURRENT-STATE line (13:40Z). The verdict has not changed, so a second message or line would only duplicate them.

## Review notes still open (all severity C, from the review of 4e961f0ad)

The comparison is kept as reviewed. Read it with these four notes:

- **F1:** the headline's "item size alone explains the whole gap" is too strong, and so is the DRI message's "explains it
  fully". The size cut was chosen after looking, and the first reviewer also moves with the arm. "Is consistent with the
  size mix" is what the data supports. The reverse adjustment still leaves a gap of 1.5 items.
- **F2:** the Claude window starts at the build start of usecase-safetyfw-b, which brings in three merges from before the
  first Sol-arm merge (sc-1ae, et-4, me-4). Those three hold 3 of Claude's 4 FIXes. Without them Claude is 1/9, so the
  raw gap widens; the sensitivity line in the comparison gives this.
- **F3:** the scripts read a moving checkout. The saved `evidence/` files and their merge SHAs now fix the numbers; rerunning
  the scripts can still differ.
- **F4:** "Even if Sol took all 89 points, it would be 0.9 per point" does not say what it divides. It is the lower bound
  on sessions per point: 2651.8M gpt-6-sol input tokens (`sess.py`) over all 89 points is 29.8M per point, and that over
  the 34M median builder session is 0.88. The number stands; only the wording is unclear.

## Seeded bugs

None: N.A. No product code changed in any language (Lean, Python or Rust), and there is no code here to seed. The
pre-review gate reports `[mutants] no product code changed`.

## Self-review against BUILDER-CHECKLIST

1. Lean answers typed and contained: N.A. (no relay or route change).
2. Deliverables built, no rule broken: PASS. Report, verdict message and CURRENT-STATE line exist (Checks table);
   `git diff main...HEAD --stat` lists only this folder; `SOL_BUILDER_CAP` is unedited.
3. Tests can fail: N.A. (no test or code added; there is nothing to seed).
4. Python, Lean and Rust agree: N.A. (no product code changed).
5. R8 binding: N.A. (no field is read from a Lean answer).
6. Gate evidence matches the final HEAD: PASS. The base is `git merge-base HEAD main` (4e961f0ad); the chain gates the
   committed final HEAD, and only docs changed after the selected run recorded below.
7. No unsigned item: PASS. There are no DELTA rows and no trust growth (`git diff main...HEAD --stat`).
8. Every user-visible change in DELTA: N.A. (no user-visible change).
9. Test selection: SELECTED_RUN_PLACEHOLDER
10. Lean statements: N.A. (no Lean change).
11. Budgets fail closed: N.A. (no budget, limit or deadline code).
12. No CPU or memory regression: N.A. (no code).
13. `Test-removed` trailer: N.A. (no test removed or renamed).
14. Pre-review self-check: PASS. Opposite direction: N.A. (no new check or guard). Every claim here names its command in
    the Checks table. Spec re-read: the verdict rule against `prompts/dri-task-sol-vs-claude-12.txt:3`, applied as written
    (each metric at or below Claude's, else WORSE, INCONCLUSIVE only at one item or less).
