**Faithful: 14/20.**

Sampling: Python `Random("20261009T0600Z")`; five units sampled from each ID-sorted status group, in CHECKED/LABELLED/OPEN/READINGS order. Audited primary part content, companions, open terms, and source context. No model calls or file changes.

```text
VERDICTS:
u001 FAITHFUL
u012 FAITHFUL
u021 FAITHFUL
u022b UNFAITHFUL
u022c UNFAITHFUL
u029 UNFAITHFUL
u033b FAITHFUL
u037 UNFAITHFUL
u045b FAITHFUL
u046 FAITHFUL
u047 FAITHFUL
u054 FAITHFUL
u059 FAITHFUL
u074 FAITHFUL
u080 FAITHFUL
u084c FAITHFUL
u084d FAITHFUL
u096 UNFAITHFUL
u100b FAITHFUL
u112 UNFAITHFUL
```

Unfaithful units:

- **u022b:** The negative-claim alternative converts the right to liberty into an unconditional requirement to spare everyone deprivation of liberty. This adds a blanket prohibition the entitlement does not state.
- **u022c:** “Must be spared endangerment” adds an unconditional protection against risk, strengthening “right to … security of person.”
- **u029:** The claim alternative requires recognition to be supplied. Leaving its bearer unnamed does not justify adding that obligation as a separate reading of the entitlement.
- **u037:** The primary part changes the regulated act from “take place” to “be ordered.” Prohibiting orders does not prohibit arbitrary arrest, detention or exile carried out without an order. The companion retains the faithful wording.
- **u096:** The negative-claim alternative substitutes mandatory non-exclusion for the right to education. It neither preserves the full entitlement nor follows as a distinct reading specified by the sentence.
- **u112:** `exercise_unprotected` merely removes protection. That weakens “may in no case be exercised,” because lack of protection does not itself prohibit the exercise.

The correct alternatives do not rescue units containing unsupported readings. Sampled structural labels and open-term questions otherwise fit their source.

Three highest-value missing features:

1. **Compositional act phrases:** preserve events, participants, and modifiers without changing acts to satisfy wording constraints; currently blocks 11 units.
2. **Explicit entitlement semantics:** distinguish rights, permissions, and obligations, and require textual support for every reading.
3. **Temporal scope:** represent birth, “until,” historical applicability, and periodicity; currently blocks five units.

Not saved: the requested `AUDIT.md` directory is outside the permitted writable roots.