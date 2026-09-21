# ve_experiments: experiment harness

| Module | Purpose |
|---|---|
| `llm.py` | The only place that calls models. `LLMClient.call/map`, disk cache keyed by (model, system, prompt, seed), retries, concurrency limit 6, JSONL call log with tokens and latency, `parse_verdict` |
| `runner.py` | `Experiment(items, conditions, judges)`: group-wise dev/scored split, paired assignment (`crossed` or `rotated`), preregistration gate, `run()` writes `experiments/<id>/runs/<split>-<time>/{trials.jsonl,manifest.json}` |
| `colab.py` | Batch backend for open-weight judges (`vllm:<hf id>`): export prompts keyed by trial, one Colab job per split, import replies into the cache, replay through `runner.run` |
| `stats.py` | False approval, honest acceptance, bootstrap CIs over groups, paired contrasts, exact sign test, per-judge breakdown, markdown table |
| `ve_iface.py` | `render / evaluate / find_countermodel` interface to the `ve` package, with an untrusted stub until it lands |
| `smoke.py` | `uv run python -m ve_experiments.smoke`: one live call per model plus a cached replay |

## Rules the code enforces

- A scored run refuses to start unless `experiments/<id>/PREREG.md` is committed and its working bytes equal the
  HEAD blob (so `assume-unchanged` cannot hide an edit), and it has a non-empty section for each Plan v2 field:
  primary contrast, refutation condition, honest-acceptance constraint, smallest useful effect, capability or
  calibration gate, sample size. The manifest records commit and blob. Scored runs cannot be truncated with `limit`,
  require the real `ve` backend (never the stub), and require the split file, if one is used, to be committed.
- Splits are per group and persistent: each group is hashed on its own, so adding items cannot move another group;
  with a `split_file` a recorded group can never move, and an attempt to move it is an error.
- Every trial has a stable identity (experiment, split, item, cell, judge, sample) that is part of the cache key
  and is never shown to the model. Two trials that share a prompt are two model calls; a rerun replays both.
- Judges have no tools. If a reply nevertheless contains a command, tool or search event, the trial is kept, marked
  invalid, and scored as the worst case.
- A prompt builder receives only the payload, without keys that start with `_`, and never the label or the id.
  A prompt that contains the item id is rejected.
- Failed calls and unparseable verdicts stay in the data with `approved = null`. `stats.py` scores them as the worst
  case for their label and reports the failure rate beside every metric.
- Verdict parsing is strict: the reply must end with a JSON object whose `verdict` is exactly one of the allowed
  strings. No keyword search and no case folding.
- Run directories are created atomically before any call and are never reused; files are opened with `x`.
- `stats.py` reports each judge separately (a pooled row only on request, exploratory), bootstraps over the cluster
  field the experiment names (semantic template for E1), and reports no p-value.

## Model calls

Claude: `claude -p --model <id> --output-format json --tools "" --strict-mcp-config --system-prompt <s>`, prompt on
stdin. Codex: `codex exec -m <id> -s read-only --skip-git-repo-check --json --ephemeral --ignore-user-config
--ignore-rules --disable shell_tool --disable apps --disable browser_use --disable computer_use --disable plugins
-c web_search="disabled" -`, system text and prompt on stdin. Both run from an empty temporary directory.

`-s read-only` alone is not isolation: with the default flags gpt-5.6-luna, asked to list `/Users/.../code`, ran
`ls` and printed the listing, so a judge could have read ground truth. With the flags above the same request is
answered "CANNOT", and Claude with `--tools ""` answers the same. Both were checked live on 2026-09-21.

Context asymmetry: a trivial call carries about 500 input tokens for Claude and about 6,600 for Codex with these
flags (13,600 before). Judges from the two families therefore do not see identical surrounding context.

The CLIs accept no sampling seed. `seed` and the trial identity only separate cache entries.

Concurrency is limited per provider CLI (6 for `claude`, 6 for `codex`) and per process. Measured on 2026-09-21:
about 4 s (Haiku 4.5) and 6 s (gpt-5.6-luna) for a one-line reply; E1 judge prompts with 150 words of reasoning take
10-30 s.

## Minimal use

```python
from ve_experiments.llm import LLMClient
from ve_experiments.runner import Condition, Experiment, Item, assign_splits, run, load_trials
from ve_experiments.stats import summarize, to_markdown

items = assign_splits([Item(id="req017-weak", label="bad", group="req017", payload={...}), ...], dev_fraction=0.25, seed=1)
exp = Experiment("E1", items, [Condition("fol", build_fol_prompt), Condition("ve_strict", build_ve_prompt)],
                 judges=["claude-haiku-4-5-20251001", "gpt-5.6-luna"])
run_dir = run(exp, LLMClient(), split="dev")          # "scored" requires the committed PREREG.md
print(to_markdown(summarize(load_trials(run_dir), contrasts=[("ve_strict", "fol")])))
```
