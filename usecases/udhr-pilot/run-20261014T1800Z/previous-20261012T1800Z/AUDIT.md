Faithful: **20/20 sampled + 1/1 changed**.

Sampling: Python `random.Random("20261012T1800Z").sample(pool, 20)`, with eligible units sorted by ID. Draw: 3 CHECKED, 10 LABELLED, 6 OPEN, 1 READINGS. Changed unit u081 overlaps the sample and appears once below.

VERDICTS:
```text
u001 FAITHFUL
u012 FAITHFUL
u023 FAITHFUL
u032 FAITHFUL
u033b FAITHFUL
u038 FAITHFUL
u040 FAITHFUL
u046 FAITHFUL
u055 FAITHFUL
u056 FAITHFUL
u066 FAITHFUL
u070 FAITHFUL
u080 FAITHFUL
u081 FAITHFUL
u095 FAITHFUL
u099a FAITHFUL
u100a FAITHFUL
u100b FAITHFUL
u107 FAITHFUL
u113 FAITHFUL
```

Unfaithful units: **none**. Source spans, encoded content, vocabulary, companions, and relevant open terms were inspected. Labels fit the represented content; no unsupported bearers, invented readings, or extraneous unsettled questions were found.

The u081 repair retains “as a member of society” in the entitlement predicate without restricting “everyone” to a newly imposed eligibility condition. Its OPEN label is appropriate. u055 preserves both text-supported scopes of “arbitrarily”: deprivation alone, or deprivation and denial. u032/u033b retain the inherited subject and discrimination reference; u046 retains protection against arbitrary interference and against honour/reputation attacks.

Three highest-value missing features:

1. **Compositional act and entitlement phrases:** preserve coordinated lists, relative clauses, beneficiaries, and conditions without the 80-byte wording constraint; 11 units report this blocker.
2. **Rights references and inclusion across units/readings:** represent “this right includes…” without choosing an unsupported bearer or right interpretation; four units remain blocked.
3. **Temporal operators and comparisons:** express “until,” law applicable when an act occurred, marriage phases, and periodic entitlements without dropping qualifications.

Read-only audit; no model calls. Printed only: the requested `AUDIT.md` destination is outside the permitted writable roots.