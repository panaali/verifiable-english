# PUSHBACK study harness

Preregistration: [PREREG-PUSHBACK.md](PREREG-PUSHBACK.md) (hashes in `PREREG-PUSHBACK-HASHES.txt`, OpenTimestamps
proof `.ots`). Plan: `PLAN-PUSHBACK.md`.

| File | Role |
|---|---|
| `items.py` / `items.jsonl.gz` / `counts.json` | mechanically labelled items (mixed, forged, corrective, robust, pilot) |
| `study.py` | arms A/B/C/C', prefilled turn 0, 3-turn adversarial/static pushback, forged injection |
| `ladder.py` | Jagged ladder L1-L6 on our items, natural L0, 10 turns, locked C |
| `v4gate.py` | GATE: arm-A pilot on 40 V4 items (Gemini) |
| `backends.py` | Gemini via `ve_experiments.paid` (Vertex ledger), Claude via `ve_experiments.claude_cli` |
| `analyze.py` | item-level paired contrasts, cluster bootstrap, non-inferiority |
| `replication.py` | Jagged Judges ToxiGen-binary replication cell (L1 now, L6 later) |
| `replication/` | frozen sample IDs, published example IDs, run outputs |
| `runs/` | study run outputs (trajectories + ledgers) |

Rebuild items: `uv run python -m experiments.pushback.items --write` (deterministic). Tests:
`uv run pytest tests/test_pushback.py tests/test_claude_cli_account.py -q`.

## Commands

All commands: `export UV_CACHE_DIR=/private/tmp/ve-uv-cache-pushback` and run from the repository root, serially
(never two Claude runs on the same account at once). Every run resumes: finished trajectories are skipped and
completed Vertex calls are replayed from the ledger.

```sh
# 0. Replication data (once; data/ is git-ignored)
uv run --with pandas --with pyarrow python -m experiments.pushback.replication sample

# 1. Ladder implementation check (ToxiGen substitutes for gated WildGuard), L1, <= $6 Vertex
uv run python -m experiments.pushback.replication run --level 1 --n 100 --cap-usd 6
uv run python -m experiments.pushback.replication analyze --level 1 --n 100

# 2. GATE: arm-A pilot, 40 V4 items, Gemini judge, <= $3 Vertex (L1, then L6 with the remainder)
uv run python -m experiments.pushback.v4gate run --level 1 --cap-usd 3
uv run python -m experiments.pushback.v4gate run --level 6 --persuader gemini --cap-usd 3
uv run python -m experiments.pushback.v4gate summarize
```

After 23:00 PDT (account danielsaeedi37 available) and only after the plan review; `ACCT=~/.claude-danielsaeedi37`:

```sh
# 3. Ladder check L6 with the Opus 5.5 persuader (Gemini judge), <= $8 Vertex
uv run python -m experiments.pushback.replication run --level 6 --n 24 --cap-usd 8 --account-config-dir $ACCT

# 4. Gate L6 with the fixed Opus persuader (separate output dir L6-opus; shares the gate's Vertex ledger; raise the cap)
uv run python -m experiments.pushback.v4gate run --level 6 --persuader opus --account-config-dir $ACCT --cap-usd 7

# 5. Ladder runs on our items (per judge J in gemini opus sonnet; arms A,C now, D0 after its amendment)
J=gemini; R=experiments/pushback/runs/ladder-$J; V="--vertex-ledger $R/vertex-ledger.jsonl --cap-usd 60"
for L in 1 6; do
  uv run python -m experiments.pushback.ladder run --set mixed --arms A,C --level $L --judge $J --persuader opus \
    --account-config-dir $ACCT --out $R $V
  uv run python -m experiments.pushback.ladder run --set forged --arms A,B,C,Cp --level $L --judge $J --persuader opus \
    --account-config-dir $ACCT --out $R $V
done
uv run python -m experiments.pushback.ladder summarize $R/trajectories.jsonl
# Claude judges: J=opus or J=sonnet, drop $V. L2-L5 need: ladder gen-arguments --set mixed --model opus --account-config-dir $ACCT
# Prefilled 3-turn protocol (revision 1, corrective harm control): study.py --set corrective --arms A,C ... (see its --help)
```

Call volume per judge (adversarial): mixed 512 + forged 192 + corrective 256 + robust 96 = 1,056 trajectories,
3,168 judge calls and 3,168 Opus persuader calls; static adds 3,168 judge calls.
