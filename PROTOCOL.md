# Working protocol for the two workers

Two workers build VE under one orchestrator. The orchestrator assigns tasks, routes reviews, and decides merges.
The user is away for about 12 hours. Nobody can answer permission prompts, so never wait for a human.

## Who is who

| Role | Agent | Worktree | Base branch |
|---|---|---|---|
| Orchestrator | Claude session `verifiable-english-ab` | `~/code/ve-integration` | `ve-integration` |
| Worker C | Claude Code, session name `ve-claude-worker` | `~/code/ve-claude` | `claude/main` |
| Worker X | Codex (GPT-6 Astra), thread name given at launch | `~/code/ve-codex` | `codex/main` |

## Rules

1. **Stay in your own worktree.** Never edit files in another worktree or in `~/code/verifiable-english`. All three
   worktrees share one git repository, so you can read any branch with `git show`, `git diff`, or `git log`.
2. **Never push, never open GitHub PRs, never change git remotes or global config.** Review happens locally.
3. **One task, one branch.** Branch from the current `ve-integration`: `git switch -c <you>/<task> ve-integration`
   (`claude/...` or `codex/...`). Commit small and often. Tests must pass before you report.
4. **Report when done.** Send the orchestrator a report with exactly these parts:
   `BRANCH`, `SUMMARY` (what and why, 5 lines at most), `VERIFY` (commands that reproduce your checks and their
   results), `GAPS` (what is missing, uncertain, or not tested), `PLAN CHANGES` (proposed edits to `ROADMAP.md`, if any).
   Worker C reports with SendMessage to `verifiable-english-ab`. Worker X puts the report in its final message of the
   turn; the orchestrator reads it from the session file.
5. **Review requests.** When asked to review a branch, do not edit it. Read `git diff ve-integration...<branch>`.
   To run its code, check it out inside your own worktree:
   `git worktree add .review/<name> <branch>`, and remove it when done. Reply with:
   `VERDICT: merge | changes-required`, `BLOCKING` (each with file:line, a reproduction, and why it matters),
   `NON-BLOCKING`, and `SCIENCE` (threats to validity, leaks of ground truth to a judge, unfair baselines,
   claims the evidence would not support). Be adversarial about the science and practical about style.
   A review that finds nothing should say what it checked.
6. **The orchestrator decides.** It merges into `ve-integration` or returns the branch with required changes.
   After a merge, start your next branch from the new `ve-integration`.
7. **Delegate.** Use subagents for bulk or parallel work (dataset conversion, test writing, literature checks,
   long experiment runs) so your own context stays small. You remain responsible for what they produce.
8. **Blocked?** If a command fails because of sandbox or permission limits, do not look for a way around it.
   Put the exact command and error in your report and continue with other work. The orchestrator can run it.
9. **Honesty over a good story.** Negative and inconclusive results are results. Never tune a baseline to lose,
   never drop failed items from a denominator, never let a judge see ground truth, never invent a citation
   or a number. If something was not run, say it was not run.

## Conventions

- Python 3.14 with `uv`. One package, `ve/`, at the repository root, with `pyproject.toml`, tests under `tests/`,
  experiments under `experiments/<id>/`, paper under `paper/`.
- Model calls only through the shared client (`ve_experiments/llm.py`, to be built first): disk cache, retry,
  concurrency limit, token log. Commands: `claude -p --model <id>` and
  `codex exec -m <id> -s read-only --skip-git-repo-check`. There are no API keys.
- Large raw outputs go under `experiments/<id>/runs/` and are committed only if under about 5 MB; otherwise commit
  a summary and the script that regenerates them.
- Every number in the paper must trace to a committed file and a command.
