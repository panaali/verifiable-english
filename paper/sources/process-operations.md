# Supplied historical operations entry

- 04:57 **OUTAGE 04:00-04:50: Claude session usage limit hit** (too many parallel Claude subagents). It killed the paper agent,
  the Colab agent and Worker C. NEW RULE: at most 2 Claude subagents at a time; Codex (separate quota) does building,
  paper drafting and re-reviews where possible; Claude reviews only for trusted code and experiment science.
  COLAB LADDER DONE (E1 dev, fol_symbols/none, L4, ~3.5 units): Qwen2.5-7B FA 57% HA 83% (primary); 14B-AWQ 39%/98%
  (primary); 32B-AWQ 14%/92% (near-floor, secondary); Llama-3.1-8B 4%/23% (degenerate); gemma-2-9b 96%/100%; phi-4-AWQ 17%
  parse fail. Table: ~/code/manage-agents/colab/results/e1-dev-ladder/ladder_table.md. Runtime kept alive by tiny
  keepalive jobs (40-min idle shutdown): resubmit from each heartbeat; `cc stop` when no GPU work is pending.
  MERGED codex/rust-closure (self-verified; tag ve-green-0510). Pending review: codex/closure-cert (Claude reviewer
  a9ae5940484cbcb64 resumed), codex/e5 rev2 (shortcut fix; verify leak audit myself), claude/harness+claude/e1 (Codex
  re-review running, log codex-rereview-harness). Running: Worker C2 a9209d3f4efc313eb (E1: Colab backend, scored
  materials, dev run on Qwen ladder, final PREREG; must NOT score), Codex paper draft (paper/draft in ~/code/ve-claude-paper).
