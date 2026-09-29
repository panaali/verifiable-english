# Translator's self-review of the 15 upgraded units

This is the translator's own whole-span check of each unit against its source words (act identification, scope,
what the formal reading leaves out). It is not an independent audit; none of these bytes is counted as
audit-verified. Every difference below is either carried by a named open term or left in an UNFORMALISED span.

Common to all seven hard-constraint bullets (`u0165.s01–s07`): the subject "Claude" and the force "should never"
come from the list lead-in `u0164.s02`, which is a different unit (still UNFORMALISED); the reading set records the
force ambiguity and the translator's narrowing to strict (citing `u0166.s01`, `u0166.s04`). The act phrase is at most
80 characters, so it abbreviates the bullet; the bullet's own words are in the predicate description and the open
term's factors. The rule reaches every instance of Claude and no other party.

| Unit | Formal reading | What it leaves out or narrows | Verdict |
|---|---|---|---|
| `u0165.s01` | must not give serious uplift to would-be makers of mass-casualty weapons | The list "biological, chemical, nuclear, or radiological" (a weapon of one of those kinds with the potential for mass casualties is what the source means; the phrase says "mass-casualty weapons"); "seeking to create" is rendered "would-be makers". Both stay in the open term `mass_casualty_weapon_uplift`. | keep as OPEN classification |
| `u0165.s02` | must not give serious uplift to attacks on critical infrastructure-or-safety systems | The parenthetical examples (power grids, water systems, financial systems). "critical infrastructure or critical safety systems" is read as "critical (infrastructure or safety systems)". | keep |
| `u0165.s03` | must not create cyberweapons-or-malicious-code that could cause significant damage | "if deployed". Whether the damage qualifier covers cyberweapons as well as malicious code is a factor of the open term, not decided. | keep |
| `u0165.s04` | must not clearly-and-substantially undermine Anthropic's AI oversight-and-correction | "ability to", "advanced", "models"; the pointer "(see Being broadly safe below)" is a cross-reference, not content. | keep; weakest abbreviation |
| `u0165.s05` | must not engage-or-aid attempts to kill-or-disempower the vast majority of humanity | "or the human species as whole" (read as the same group); "engage or assist in an attempt" becomes "engage-or-aid attempts". "vast majority" is inside the open term, no threshold chosen. | keep |
| `u0165.s06` | must not engage-or-aid attempts to seize unprecedented illegitimate absolute control | "any individual or group with", "degrees of", and the list "societal, military, or economic" (so the phrase says absolute control of any kind). The list is a factor of the open term. | keep; the omitted list makes the act phrase broader than the source |
| `u0165.s07` | must not generate child sexual abuse material | The abbreviation "(CSAM)". | keep; audit repair |
| `u0052.s01` | duty to use good judgment when evaluating conversational inputs | "always" is folded into the force reading. "good judgment" is the open term `good_judgment`. | keep |
| `u0036.s05` | duty to seek clarification in a situation that is a case of genuine ambiguity | "ask for" is rendered "seek" (the act-phrase word list bans "for"). | keep |
| `u0156.s03` | must not actively deceive a user about a system prompt's existence-or-content | "the user" becomes "each user". | keep |
| `u0125.s04.p2` | must not directly deny being Claude | "that it is Claude" becomes "being Claude". The sentence's opening "Still, " and its "as that would cross the line …" clause are separate UNFORMALISED spans (`.p1`, `.p3`). | keep |
| `u0263.s04.p2` | duty to comply with the instruction against unintended exploits, when Claude has explicitly been instructed not to engage in them | "And " is a separate UNFORMALISED span (`.p1`). "comply" is read as complying with that instruction. | keep |
| `u0078.s01` | duty to follow operator instructions when operator and user goals genuinely conflict, unless one of six things is required | "err on the side of" is folded into the force reading. The scope of "in ways that damage their interests" is left in the open term, not decided. | keep |
| `u0168.s01` | duty to remain firm when the situation has seemingly compelling arguments to cross the hard-constraint lines | "these lines" is resolved by the translator to the hard-constraint lines (context `u0166.s01`). | keep; one translator resolution, recorded |
| `u0073.s05` | defeasible duty to comply with the system prompt's instructions, guarded by "an operator prompt addresses the case" and none of unsafe / unethical / against guidelines | The bullet marker and bold markup sit inside the span. "not unsafe, unethical, or against Anthropic's guidelines" is read as none of the three. | keep; one reading |

Nothing was changed after this review except two act phrases (`u0165.s01`, `u0165.s04`) that were made closer to the
source once the length limit was measured.
