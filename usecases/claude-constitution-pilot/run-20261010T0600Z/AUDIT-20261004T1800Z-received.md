**18/20 faithful**, including seven metadata-only labels. Faithfulness respects declared OPEN/READINGS limitations; it does not imply complete formalisation.

Sampling: Python `Random("20261004T1800Z")`, sequential samples from ID-sorted status groups: CHECKED 1, LABELLED 7, OPEN 6, READINGS 6. Compared source spans/context, ledger, main VE, and strict companion; excluded explicitly unclaimed demonstrations.

VERDICTS:
```text
u0248 FAITHFUL
u0103 FAITHFUL
u0083.heading FAITHFUL
u0032.heading FAITHFUL
u0174.heading FAITHFUL
u0235.heading FAITHFUL
u0130.heading FAITHFUL
u0075.heading FAITHFUL
u0166.s04.p4 FAITHFUL
u0165.s06 FAITHFUL
u0123.s01.p1 UNFAITHFUL
u0165.s02 FAITHFUL
u0165.s05 FAITHFUL
u0168.s01 FAITHFUL
u0125.s04.p2 FAITHFUL
u0036.s05 FAITHFUL
u0052.s01 FAITHFUL
u0123.s03 UNFAITHFUL
u0156.s03 FAITHFUL
u0263.s04.p2 FAITHFUL
```

Unfaithful units:

- **u0123.s01.p1:** Its single permission rule hardcodes six exceptions using the narrow prohibition reading of `u0123.s03`. Yet that sentence retains wide-scope and ability alternatives. The exceptions do not change with those alternatives: outside role-play, the wide reading would not supply five of these exclusions; inability alone supplies no prohibition. This weakens the permission and fails to preserve the admitted combinations.
- **u0123.s03:** The ability candidates replace “cannot instruct” with inability to **get Claude to perform** the behaviours. Issuing an instruction and securing compliance are different actions. The surrounding passage states operator permissions and limits; it does not establish that inducing these behaviours is impossible. These candidates add an unsupported capability guarantee.

Three highest-value missing features:

1. **Executable strict/defeasible readings with `unspecified` completion**, preserving silence without inventing permission or absence of duty.
2. **Typed modal action complements**, distinguishing permission, ability to issue instructions, and ability to induce behaviour.
3. **Linked reading choices across sentences**, propagating scope and modality into dependent permissions and exceptions.

No model calls or file changes. `AUDIT.md` was not written because the requested directory is outside this session’s writable roots.