# Feature review: what `ve-green-english-lean-s2` adds over `ve-green-difffuzz`

Source: the pinned 184,893-byte constitution, unchanged (SHA-256 `fa10ed48…50dd`, `source/SOURCE.md`). Start point: the translation of run `20261005T0600Z` (`prev/`): all 1,132 ledger entries, the main document and the three companions are identical in this run.

## Merged since `ve-green-difffuzz` (`git log --first-parent`, `git diff --stat`: 414 files, 73 under `ve/`)

| Merged | What it is | Changes what can be written? |
|---|---|---|
| `compose-s2` (S2a) | superposed verdicts across the readings of a content-bearing `readings@1` document on the soft and norms chains (`ve/readings_sup.py`, `readings_verdicts.py`, `readings_s2_wording.py`); enumerated fallback up to 64 compatible choices; `ve document readings --conclusion / --under` | Adds verdicts (premises, conflict status, ALL/SOME/NONE across readings), no new text form and no status; applies to documents without `norm-defaults@0` |
| `english-lean-s2` | the English reader and printer as a Lean executable (`ve_english_route`), Python shadowing it | No. Same English. |
| `lean-first/b1` (lf-1), `b3b`, `b3d` | response shapes of the Lean routes proved against their encoders; readings and discourse relays composed; Python duplicates removed | No. Infrastructure. |
| `infra/consolidate-b1` | one owner per piece of logic across Python, Lean and Rust | No. |

Result: **one newly expressible feature (verdicts across readings), zero units upgraded by it.** S2a's spec itself expects "no status change of any unit" for the constitution (composition-s2.md 11).

## Measured at this tag

* **Main translation:** `ve document check` gives the same output as at the previous tag (premises UNKNOWN, "non-assertion reading elaboration pending"), also for the strict and default companions. S2a does not change it: the main document's profiles include `norm-defaults@0`, where `readings@1` content is a named abstention, and its reading sets carry no content.
* **Demonstration companion `readings/s1.ve.md`** (8 content-bearing sets: 5 force sets and 3 operator sets; completes duties with `deny`, demonstration only): previous tag premises UNKNOWN "superposition pending", now route `superposed`, premises `model` with the choice "all index 0", conflict status CONFLICT-FREE under every reading with certificates, a compatible-choice count over the 64-choice enumeration budget (768 choices covered), so the superposed route does the work, no dead reading, 389 nodes / 50 predicates / 7 sorts against limits 10,000 / 256 / 32; per candidate 17 `model`, 2 `UNKNOWN` (the ability candidates of `u0062.s01` and `u0123.s02.p1`: no model and no certificate within budget). Check time about 7 minutes.
* **Conclusion probe** (`probes/s2/`, unit `u0125.s04.p2`, formula: every instance of Claude must avoid directly denying being Claude): ALL under `--under force-u0125-s04-p2:0` (the *must* reading; certificate, English "Read sentence 471 as *must*: the conclusion follows"), UNKNOWN under `:1` (the *should* reading; budget, no certificate), UNKNOWN across all readings (over 64 choices, E28). This is the first place VE itself separates "must" from "should" for a conclusion instead of two documents or two candidate texts.
* **Probes** (all five re-run): unspecified (34 points: 21 SETTLED, 13 UNDECIDED, 0 CONFLICT), risk, discourse and rights files byte-identical to the previous run's. `probes/s1-probe.json` changed: (a) the main document with `readings@1` added is now accepted (before: `UnsupportedProfile: readings@1 requires norms@0`, a message false of the document), it adds nothing since no set has content; (b) a strict norm as content beside `norm-defaults@0` is now the named abstention `UnsupportedProfile: readings@1 content with norm-defaults@0 is not implemented` (before: `InvalidInput: invalid regulated role or default for clarification_required`); (c) the soft companion with `norm-defaults@0` added is refused with `norm-defaults@0 documents on the soft and rights routes await the Lean route`.

## What it shows about the language

* **F1 (the blocker).** `readings@1` content cannot sit beside `norm-defaults@0`, so the main translation (where every completion is `unspecified`) cannot use S2a; the companion that can use it completes duties with `deny`, which the source does not state. Once `readings@1` content works with `norm-defaults@0` (or soft-norms@0 allows `unspecified`), the nine READINGS units move from "pending" to checked verdicts across readings, and the main document's premise status can leave UNKNOWN.
* **F23 (new).** Across-all-readings answers other than ALL need one check per compatible choice: 768 choices here against a budget of 64, so SOME and NONE are not reported for the constitution's sets; only ALL (a certificate) and named readings (`--under`) are available.
* **F24 (new).** An ability candidate ("operators cannot issue the instruction") gets premise status UNKNOWN: VE finds neither a model nor a refutation within its budget, so it cannot say whether that reading is consistent with the rest.
* **F14, F22 (still true).** How far one sentence's limits reach depends on how another sentence is read, and the language links the two only by listing named candidates; "can / cannot" still needs a typed action complement. S2a shows both inside one document (`scope-modal-u0123-s03` has 4 candidates, all with a model), but does not remove them.
* Others as in `FEATURE-REVIEW-prev-20261005T0600Z.md` (F2, F4, F6, F10–F13, F15–F21): unchanged.

## Missing features, in order of what they would unlock here (ledger tally `UNFORMALISED`)

norms 669, quantities 119, `other:discourse` 81, causation 76, defaults 50 (stale), counting 31, modality/belief 24, attribution 12, time 9, `other:open-list` 1, `other:graded-force` 1. Unchanged.

1. **`readings@1` content beside `norm-defaults@0`** (F1): the one step that lets S2a reach the main translation.
2. **Typed modals with action complements** (F22) and **graded normative force**.
3. **S2b** (rights chain), **cross-sentence scope** (F14), the certified form of the `decision_only_sound` finding.
4. Binary relation wording (F6, F19), nested-list English (F20).
