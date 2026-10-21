Faithful: **19/20 sampled + 4/5 changed** (two overlap).

Sample: Python `Random("20261021T0600Z").sample` over 61 eligible units sorted by ID. Below: 20 sampled, three remaining changed, then seven supplementary checks.

VERDICTS:
```text
u0165.s05 FAITHFUL
u0257.heading FAITHFUL
u0075.heading FAITHFUL
u0042.presupposition FAITHFUL
u0286.heading FAITHFUL
u0008.heading FAITHFUL
u0156.s03 UNFAITHFUL
u0165.s07 FAITHFUL
u0168.s01 FAITHFUL
u0165.s03 FAITHFUL
u0207.heading FAITHFUL
u0298 FAITHFUL
u0095.heading FAITHFUL
u0027.heading FAITHFUL
u0108 FAITHFUL
u0052.s01 FAITHFUL
u0069.heading FAITHFUL
u0254.heading FAITHFUL
u0040.heading FAITHFUL
u0174.heading FAITHFUL
u0013.presupposition FAITHFUL
u0036.s05 FAITHFUL
u0263.s04.p2 FAITHFUL
u0032.presupposition FAITHFUL
u0043.s02.p1 FAITHFUL
u0043.s02.p2 FAITHFUL
u0069.presupposition FAITHFUL
u0083.presupposition FAITHFUL
u0245.presupposition FAITHFUL
u0286.presupposition FAITHFUL
```

**u0156.s03:** The contextual readings still lose the situation. `asked_to_keep_system_prompt_confidential(Claude,user)` cannot distinguish two conversations involving the same pair. A request in one consequently governs both. The source supplies no one-conversation-per-pair restriction; mentioning “which conversation” in the open-term factors cannot supply the missing binding.

Open-term records and vocabulary descriptions were inspected. Sampled hard-constraint guards bind the acting instance and preserve both u0173.s01 alternatives, including possibly mistaken belief. Both cyberweapon modifier attachments are represented. The repaired u0168.s01 guard binds the actor correctly. No sampled CHECKED content uses open predicates or undeclared evaluative predicates.

Claimed presuppositions pass trigger, content, and withholding checks. u0042 asserts exactly three distinct Claude principal types without naming them; u0043 closes only Claude’s types. “At the moment” has no date. u0286’s vocabulary defines “unsolved” as an unsolved problem. u0055’s note correctly records existence of a way to treat operators/users. Excluded headings remain unclaimed.

FAITHFUL verdicts on UNFORMALISED entries accept their disposition and verify **zero covered bytes**. No ledger entries have `claimed: false`.

Three highest-value missing features:

1. Document scope with explicit conversation/event identity and participant binding.
2. Native defeasible “should,” preserving silence as UNKNOWN rather than exemption.
3. Typed knowledge, intention, and belief, including factivity distinctions.

Read-only; no model calls. `AUDIT.md` was not written because its directory is outside the sandbox’s writable roots.