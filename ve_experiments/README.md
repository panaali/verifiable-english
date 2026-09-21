# ve_experiments: experiment harness

| Module | Purpose |
|---|---|
| `llm.py` | The only place that calls models. `LLMClient.call/map`, disk cache keyed by (model, system, prompt, seed), retries, concurrency limit 6, JSONL call log with tokens and latency, `parse_verdict` |
| `runner.py` | `Experiment(items, conditions, judges)`: group-wise dev/scored split, paired assignment (`crossed` or `rotated`), preregistration gate, `run()` writes `experiments/<id>/runs/<split>-<time>/{trials.jsonl,manifest.json}` |
| `stats.py` | False approval, honest acceptance, bootstrap CIs over groups, paired contrasts, exact sign test, per-judge breakdown, markdown table |
| `ve_iface.py` | `render / evaluate / find_countermodel` interface to the `ve` package, with an untrusted stub until it lands |
| `smoke.py` | `uv run python -m ve_experiments.smoke`: one live call per model plus a cached replay |

## Rules the code enforces

- A scored run refuses to start unless `experiments/<id>/PREREG.md` exists, is tracked, has no uncommitted
  changes, and names a primary metric, a primary contrast, a refutation condition and a sample size. The manifest
  records the preregistration commit and blob. Scored runs cannot be truncated with `limit`.
- A group (base item with its faithful and weakened variants) is never in both splits.
- A prompt builder receives only the payload, without keys that start with `_`, and never the label or the id.
  A prompt that contains the item id is rejected.
- Failed calls and unparseable verdicts stay in the data with `approved = null`. `stats.py` scores them as the worst
  case for their label (approved if bad, rejected if good) and reports the failure rate beside every metric.
- Verdict parsing is strict: the reply must end with a JSON object whose `verdict` is exactly one of the allowed
  strings. No keyword search and no case folding.

## Model calls

`claude -p --model <id> --output-format json --tools "" --strict-mcp-config --system-prompt <s>` with the prompt on
stdin, and `codex exec -m <id> -s read-only --skip-git-repo-check --json --ephemeral -` with system text and prompt
on stdin. Both run from an empty temporary directory, so no judge can read this repository. With these flags a
trivial Claude call carries about 500 input tokens instead of about 30,000. `codex exec` has no equivalent flag and
carries about 13,600 input tokens of its own context per call; judges from the two families therefore do not see
identical surrounding context, which is a limitation to state in the paper.

The CLIs accept no sampling seed. `seed` only separates cache entries: a new seed is a new independent sample, and
a repeated seed replays the stored reply.

Measured on 2026-09-21: 24 short calls (12 per model) at concurrency 6 took 23.4 s, about 1 s per call effective;
mean latency 4.3 s (Haiku 4.5) and 5.7 s (gpt-5.6-luna); no failures.

The concurrency limit is per `LLMClient` (per process). Two experiment processes at once double the load.

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
