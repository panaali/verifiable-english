# en-e3bb DELTA (this item's merge)

No user-visible delta. Python's W1 reader still decides every answer. Lean is asked only when both
`VE_STATEMENT_COMPARATOR=1` and `VE_SHADOW_LOG` are set, and it writes only that log. Python's document is returned,
and its refusal raised, as it stands (`test_the_shadow_asks_lean_and_keeps_python_s_answer`;
`test_the_shadow_needs_both_flags`). With either flag unset nothing is called or written.

The W1 delta between Python and Lean is EN-2's evidence for the DRI's decision at the stop point before EN-3
(spec en-e3-norm.md section 6). It is in `docs/en-e3-norm/en-2/DELTA.md` and `delta.json`, not here. That decision
gates en-e3, not this merge.

Trust: no Lean file changes; `tools/trust_map.py --check` gives K +0, S +0, trusted +0 against the merge base. No
standing ruling or DRI signature is needed for this item.
