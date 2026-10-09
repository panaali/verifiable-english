# Audit repair, run 20261009T0600Z

Latest audit received: `AUDIT-20261008T1800Z-received.md` (17/20 faithful; the previous run's own `AUDIT.md`). It marked three units UNFAITHFUL:

| Unit | Audit's reason | Repair |
|---|---|---|
| u0123.s02.p1 | "can legitimately instruct" grants the permission; the conditional-permission candidate adds an unsettled legitimacy condition and the ability candidate imports a capability claim into a normative passage | both candidates removed; the open term `instruction_is_legitimate`, used only by them, removed from the vocabulary, the open terms and the unit. Two candidates remain (permission under the narrow and the wide limits of u0123.s03) |
| u0123.s03 | "cannot instruct" is a prohibition; reading it as inability invents a capability restriction | `narrow-ability` and `wide-ability` removed; the candidates are now `narrow-prohibition` and `wide-prohibition` (were `narrow-permission`, `wide-permission`, which named a prohibition) |
| u0123.s01.p1 | `permission-no-limits` rested on that inability reading and strengthens the permission | removed; the narrow-limits and wide-limits candidates remain |

Beyond the audit: **u0062.s01** ("Operators can give Claude ...") had the same ability candidate in the same normative passage (the next sentence speaks of what they are "permitted" to do), so I applied the audit's reasoning to it and removed it. That is my extension, not an audit finding; an auditor may disagree.

The ambiguity that stays comes from the words alone: "while role-playing as a custom AI persona" can qualify the first item only or every item of the list. The permissions the limits attach to take the same scope (scoped permissions), so the four sets carry a coupling on the label axis `limits-scope` and cannot be read with different scopes. No default was added anywhere: the completion is `unspecified`, so inputs no rule decides are UNDECIDED, not allowed.

The four units keep status READINGS but are not audit-verified: they wait for a re-audit. A unit the audit rejected keeps no covered status it did not earn: READINGS here means "open reading set", and the set is now what the words support. Audit-verified bytes: 2,001 -> 1,349 (0.73%); claimed coverage is unchanged at 2,996 bytes. u0073.s05 and u0052.s01 return to the verified list (that audit saw their present form); u0036.s05, u0156.s03 and u0263.s04.p2 were accepted but now carry content in the translation, so they wait for a re-audit.
