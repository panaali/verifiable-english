# E1: sign-off on adversarially weakened formalizations

Code: `ve_experiments/e1/`. The scored materials are built; no judge has seen a scored item.

| File | Content |
|---|---|
| `PREREG.md` | Draft preregistration, parametrised by judge set. Must be committed unchanged before a scored run |
| `judges.json` | Judge set with measured dev gates and roles |
| `DEV-qwen.md` | Dev results of the open-weight judges: ten cells, contrasts, per-template variance, E1b |
| `items/scored.jsonl` | Scored candidates (874), generated before any judge call; `colab/` holds batch job inputs and outputs |
| `PILOT.md` | Dev capability gate: four models on fol_symbols, no explanation |
| `TUNING.md` | Dev false approval for every difficulty setting and judge tier tried |
| `items/dev.jsonl` | Dev candidates, attack recipe v1 (157: 48 good, 109 bad). `dev-v2.jsonl`: recipe v2 (not adopted) |
| `items/*.rejected.jsonl` | Attacks discarded by validation, with the reason |
| `splits.json` | Persistent split assignment of every base item |
| `runs/` | One directory per run: `trials.jsonl` (with full replies) and `manifest.json` |

## Reproduce

```
uv run python -m ve_experiments.e1.build dev [--recipe v2]      # items; model calls are cached in .llm_cache/
uv run python -m ve_experiments.e1.pilot gate dev               # capability gate
uv run python -m ve_experiments.e1.tuning run <name ...>        # names: see RUNS in tuning.py; E1_ITEMS=dev-v2 for recipe v2
uv run python -m ve_experiments.e1.pilot report dev             # writes PILOT-dev.md
uv run python -m ve_experiments.e1.tuning report                # writes TUNING.md
```

Run directories are never overwritten; delete or rename one to regenerate it. Replies come from the cache when the
trial identity and prompt are unchanged, so regenerating a report costs no model calls.

## Design in brief

- 16 semantic templates (quantifier alternation, exceptions, existence conditions, argument order, vacuity,
  equality) x 12 fresh vocabularies in 6 domain families. Dev: 4 templates x 2 families. Scored: the other 12
  templates x 4 families. Template x family cells that mix the two are unused.
- Good candidates: the canonical faithful AST plus up to two sound rewrites (contraposition, exportation, De Morgan,
  implication as disjunction, commuted conjunction), so that "looks canonical" is not a cue.
- Bad candidates: seven mechanical attack families and model-written attacks from both strong families, generated
  once, before any cell exists. Each is type-checked, must mention exactly the faithful AST's sorts and predicates,
  and must have a distinguishing finite model that the `ve` evaluator confirms.
- Explanations: written by an attacker model with one prompt for good and bad candidates alike.
- One judge prompt; cells differ only in the rendered statement and the presence of the explanation block.
- E1b: truth of the statement in two small finite models, no requirement shown.
