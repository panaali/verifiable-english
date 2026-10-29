# JT-E1r pre-registration (2026-10-29)

Status: frozen before any reader call. Main renderer pin: `8868ce212`. The 40 new rows in [`items.tsv`](items.tsv) contain 20 UDHR-inspired and 20 Claude constitution-inspired synthetic cases. Each corpus has settled, turns and conditional keys. These are probes about judgments in those sources, not claims that the source documents contain the synthetic sentences. None repeats JT-E1's source situations or variants. The rows freeze the source, conclusion, answer key, bound judgment predicate and atom, named decider or `unstated`, candidate template and actual lint result. The key is withheld from readers.

The control is the byte-for-byte stdout of `python -m ve render --view ve_english` for each saved `.ve` statement and environment at the pin. Its environment omits the template so main produces its identifier fallback. [`render.py`](render.py) writes the inputs, command and output under `captures/`. It derives the English declaration line mechanically from section 2.4 of the plan, using the frozen atom and decider. It copies the identifier bytes for absent or rejected templates. The shared `SOURCE`, `CONCLUSION`, and `JUDGMENT` lines make the judgment predicate, atom and decider explicit in both arms. No answer line is assembled from the key. A pre-call audit recomputes the lint, displays and equivalent shared information. U17–U20 lack a template; C17–C20 have `LOGICAL_WORD` rejection. Those eight rows are reported separately and supply no evidence of a wording advantage.

**Verbatim reader prompt:**

> Read only the source and displayed lines below as a reader of this document. For the named conclusion, answer in exactly this format: `CLASS: SETTLED|TURNS|CONDITIONAL; DECIDER: <name or NONE>; WHY: <one sentence>`. SETTLED means it holds whatever is judged. TURNS means two admissible judgments can change it. CONDITIONAL means it is certified only given a judgment criterion. Name the decider if the text names one; otherwise say NONE. Do not use outside knowledge.

The runner appends the shared lines and one captured display. Each row gets one independent, blinded call in each arm. `CLASS` and `DECIDER` are scored against the frozen key; `WHY` is retained. A `turns` or `conditional` item read as settled or checked is critical. Missing/malformed answers are incorrect; prose that declares a dependent conclusion settled or checked is critical. Class and decider must both be correct. For a settled key with no named decider, the expected decider is `NONE`.

## Frozen bars (verbatim from JT-E1's pre-registration)

> (a) At least 90% correct with 2.4's English, and at least 15 points above the identifier arm.
>
> (b) No critical misreading in 40: an answer that turns on a judgment read as settled or checked.

Bar (a) requires at least 36 of 40 English responses fully correct and at least six more correct than control. Bar (b) applies to all 40 English responses. Call errors count incorrect. The experiment is proxy readability, not human comprehension; a human reader audit is a separate acceptance item. At most 100 Sonnet 5.5 calls and 3M reported CW, subscription only. If either bar fails, a wording revision and fresh rerun are a follow-up, not a change to this frame.
