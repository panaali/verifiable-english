# Risk wording probe 2: the c5 replacement (sealed)

The single re-probe of `docs/spec/risk-PLAN.md` 2.6 rule 4 for construct c5. **Status: sealed.** The second plan
reviewer checked every key and critical option (`manage-agents/risk-probe2-check.final.md`: "DROP: none"; wording
accepted), so all four items are kept. `MANIFEST.sha256` lists every sealed file with its SHA-256; nothing it lists is
edited after sealing. An item found defective afterwards is reported in `RESULTS.md` with its reason, and c5 is
scored with and without it. The first probe (`../risk-wording-probe/`) is sealed and is not touched.

## Why

In the first probe c5, `<action> leads to <harm> if <condition>` (one reading: sufficient condition; critical rival:
"only if", a necessary condition), scored 15/16 in L. The one wrong answer was critical: haiku-r1-L-06 on c5-1
("The outage only occurs if peak memory > 8GB … the condition for the outage is not met"). Rule 1 allows no
critical answer, so c5 is pending wording (`../risk-wording-probe/RESULTS.md`; `docs/spec/risk.md` 2.1).

## The proposed wording

> **If `<condition>`, `<action>` leads to `<harm>`.**
>
> Example: "If the size of the backup is greater than 250 gigabytes, copying the backup to the new disk leads to a
> job failure."

This is the replacement the two reviewers already converged on (`risk.md` 2.1, 11 item 18 and 12.1; plan section
12, item 1a). This probe tests it and proposes nothing else. The one reading and the semantics do not
change: a sufficient source, `S = C` (plan 2.2). The legend line is the probed c5 line with only the wording
replaced:

```text
"If <condition>, <action> leads to <harm>" means the harm happens in every case they allow in which the condition holds.
```

As in the first probe, the items spell out "the declared estimates, conditions and statements" in place of "they",
because no earlier legend line in an item introduces "they".

Why this form:

- **The condition comes first.** The failing reader took the trailing `if` as a limit on the harm ("the outage only
  occurs if …"). The fronted "If C, X" is the usual English form of a sufficient condition. It also stops c5 from
  sharing the frame `<action> leads to <harm> <connective> <condition>` with c7 (`exactly when`), where only the
  connective separated a one-direction condition from a two-direction one. c6 (`cannot lead to … unless`) and c7
  keep their trailing conditions, so each of the three condition forms now has a different shape.
- **It keeps the frozen verb.** `leads to` stays (rule 3; c3a passed in L and C), so the consequent carries c3a's
  tested reading, "in every case". No new word is added.
- **No `then`.** `if FORMULA, then FORMULA` is the core surface's implication (`docs/english-surface.md`,
  Conditionals and grammar). A record condition written with `then` would have two derivations: one as the core
  implication, one as a record condition. Without `then` the record form stays distinct. `then` would also add
  nothing to the reading, and some readers take it as a time order ("and after that").
- **Not `whenever`.** It would be a new connective. VE reserves the word (`docs/rendering-views.md`) but uses it
  nowhere. It also speaks of repeated occasions, which the semantics does not have (one decision, a box of
  valuations), and it sits close to c3a's rival, "usually".

Limit: putting the condition first does not remove conditional perfection (reading "if" as "if and only if") in
principle. Whether it does so in practice for these readers is exactly what this probe measures.

Condition wordings stay record-only (`risk.md` 2.1, 2.3). So the fronted `If` never meets a W1 rule's guard `if`.

## Items

`items.json` holds four scored items for c5. The fields and layout are those of the first probe (see its README,
table of fields). The file is serialised in the layout of `../risk-wording-probe/seal.py` `dump_items`, so the same
round-trip check applies. Ids are `c5r-n`, with construct `c5`.

| Item | Domain, setting | What it tests | Key | Critical | Separates | Against world knowledge |
|---|---|---|---|---|---|---|
| c5r-1 | agent-operations, agent operations | condition fails (the failing c5-1 pattern) | "The text does not say." | "No job failure happens, because …" | yes | no |
| c5r-2 | non-computer, delivery robot | condition holds | "A fall happens." | "might happen or might not" and "The text does not say." | yes | yes (3 kg on a ramp) |
| c5r-3 | non-computer, clinic | condition fails | "The text does not say." | "No confusion happens, because …" | yes | no |
| c5r-4 | agent-operations, agent operations | no harm seen, so the condition failed (contrapositive) | "No: it was 60 gigabytes or less." | "The text does not say." | yes | no |

How this meets 2.6:

- **Separating items.** All four separate the rival; at least two are required.
- **Domains.** Two items are agent-operations (section 9's domain) and two are non-computer (a delivery robot and a
  clinic).
- **World knowledge.** One item (c5r-2) goes against world knowledge.
- **Options.** Each item has three or four options, and exactly one of them is "The text does not say."
- **Conditions.** Each item runs in L (legend first) and in C (no legend).
- **Answer balance.** Two keys are "The text does not say" and two are definite answers. So a reader who leans
  towards "does not say" cannot pass on that lean alone, which it could in the first probe (three of its four c5
  keys).

The items were written from plan 2.1 and 2.6, the replacement wording and its legend line in `risk.md` 2.1 and 2.4,
and the first probe's c5 items and answers, which show the failure to target. The situations are new.

## Scoring (unchanged)

Nothing about scoring changes. The first probe's rules, scorer and reader set are reused as sealed there:

- Scoring is mechanical against the sealed key. An unparseable answer counts as wrong but not critical.
- **Rule 1.** c5 passes when, in L, at least 15 of its 16 answers are correct and none is critical. If the checking
  reviewer drops items before sealing, the first probe's sealed allowance applies to the answers that remain: at
  most one of them is not correct, and none is critical.
- **Legend-dependent.** If c5 passes L with a critical answer in C, it is marked legend-dependent and W8 re-tests it.
- **If c5 passes**, item 1 freezes the new wording (rule 2): the `risk.md` 2.1 row, the 2.4 legend line, surface
  registration, and the end of the `(wording pending)` rendering.
- **If c5 fails**, this was the one re-probe (rule 4), and only c5 stays pending. The surface registers no c5
  wording. Records carry `"form": "sufficient"` in JSON, and reports render the condition with
  `(wording pending)` (`risk.md` 2.1).
- **The session is unchanged.** The reader instruction is the same (`../risk-wording-probe/prompt.txt`). The readers
  are the same two, Claude Haiku 4.5 and GPT-6 Sol, each in fresh sessions with no tools, no repository and no VE
  documents. Each item is answered in each condition by two independent sessions per family. Every result is
  labelled "proxy; human readability unmeasured".

## Sealing

1. The other plan reviewer checked that each key follows from the one reading and each critical option from the
   rival (`manage-agents/risk-probe2-check.final.md`). It dropped no item.
2. `seal.py` (the first probe's script with only `DROP` changed, here empty) wrote the files below with a fresh
   random seed recorded in `sessions.json`, then `MANIFEST.sha256`. Under the rule of at most one item per construct
   per session, four items of one construct give one item per session: 4 items × 2 conditions × 2 families × 2
   replicates = 32 sessions and 32 answers (16 in L, 16 in C). The other 2.6 session constraints (never c3a with
   c3b, never c12 with a `prevents` control, never both conditions) hold trivially and are still checked by
   `seal.py`.

| File | What it is |
|---|---|
| `items.json` | the 4 scored c5 items, unchanged by sealing |
| `prompt.txt` | the fixed reader instruction (2.6 Readers), and nothing else; identical to the first probe's |
| `readers.json` | the reader list: family, model and the exact invocation |
| `sessions.json` | the seed, the dropped ids (none), and for every session its family, replicate, condition and item, with the shown-letter to sealed-label map of the item's shuffled options |
| `sessions/<session>.txt` | the exact text each reader session receives |
| `seal.py` | the script that wrote the files above (run once) |
| `score.py` | the mechanical scorer (the first probe's parser; decisions for c5 only); it writes `scored.json` and `RESULTS.md` |

Session ids are `<family>-r<replicate>-<L|C>-<nn>`; readers never see ids, constructs or keys. In L the text starts
with a `Legend:` block of the item's legend lines; in C the block is absent and the text is otherwise identical.

## After sealing (not in the manifest)

`run.py` (the first probe's runner, unchanged) sends each session to its reader in a fresh empty temporary directory
outside the repository and saves the raw output under `runs/<session>/`; `scored.json` and `RESULTS.md` are generated
by `score.py`. Every result is labelled "proxy; human readability unmeasured".
