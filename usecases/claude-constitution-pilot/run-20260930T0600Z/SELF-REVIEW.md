# Translator's self-review of the nine repaired units

This is the translator's own whole-span check of each repaired unit against its source words. It is not an independent
audit; none of these bytes is counted as audit-verified (`metrics.json`, `audit_rejected_units_and_repair_status`). The
other five READINGS units and the one OPEN unit (`u0036.s05`, `u0052.s01`, `u0078.s01`, `u0168.s01`, `u0263.s04.p2`,
`u0073.s05`) are unchanged in translation content; the last audit accepted four of them (`u0052.s01`, `u0168.s01`,
`u0263.s04.p2`, `u0073.s05`).

Common to the seven hard-constraint bullets (`u0165.s01–s07`): the subject "Claude" and the force "should never" come
from the list lead-in `u0164.s02`, which stays UNFORMALISED. The reading set keeps both force readings (strict rule,
defeasible rule) and the translator’s recorded narrowing to strict, citing `u0166.s01` and `u0166.s04`. Each rule is
now: *for every instance of Claude and every situation that is a case of ‹the source’s words›, Claude must avoid the
act*. The case is an open term (the source gives no test for it); the act phrase is a pointer.

| Unit | Source (short) | Case atom (source words, open term) | Formal reading, strict | What it still leaves out or narrows |
|---|---|---|---|---|
| `u0165.s01` | Provide serious uplift to those seeking to create [CBRN] weapons with the potential for mass casualties | "Claude providing serious uplift to those seeking to create biological, chemical, nuclear, or radiological weapons with the potential for mass casualties" | must avoid giving weapons uplift in a situation classified as that case | Nothing dropped from the source words. The pointer "weapons uplift" is shorter than the clause; the atom carries the clause. |
| `u0165.s02` | serious uplift to attacks on critical infrastructure (…) or critical safety systems | "… attacks on critical infrastructure (power grids, water systems, financial systems) or critical safety systems" | must avoid giving attack uplift in that case | "critical (infrastructure or safety systems)" vs "(critical infrastructure) or (critical safety systems)" is a factor of the open term, not decided. |
| `u0165.s03` | Create cyberweapons or malicious code that could cause significant damage if deployed | "Claude creating cyberweapons or malicious code that could cause significant damage if deployed" | must avoid the creation in that case | "if deployed" is kept. Whether the damage clause covers cyberweapons or only malicious code is kept as a factor of the open term (audit repair). |
| `u0165.s04` | Take actions that clearly and substantially undermine Anthropic’s ability to oversee and correct advanced AI models (see Being broadly safe below) | "… taking actions that clearly and substantially undermine Anthropic’s ability to oversee and correct advanced AI models" | must avoid the undermining in that case | The cross-reference "(see Being broadly safe below)" is not content (kept as a factor of the open term). |
| `u0165.s05` | Engage or assist in an attempt to kill or disempower the vast majority of humanity or the human species as whole | "… engaging or assisting in an attempt to kill or disempower the vast majority of humanity or the human species as whole" | must avoid assisting an attempt on humanity in that case | The pointer says "assisting", the atom says "engaging or assisting". "vast majority" has no threshold. |
| `u0165.s06` | Engage or assist any individual or group with an attempt to seize unprecedented and illegitimate degrees of absolute societal, military, or economic control | "… engaging or assisting any individual or group with an attempt to seize unprecedented and illegitimate degrees of absolute societal, military, or economic control" | must avoid assisting an attempt to seize control in that case | The list "societal, military, or economic" is in the atom (it was dropped from the old act phrase). |
| `u0165.s07` | Generate child sexual abuse material (CSAM) | "Claude generating child sexual abuse material (CSAM)" | must avoid the generation in that case | Nothing dropped. Whether material is CSAM is the open term. |
| `u0156.s03` | Claude shouldn’t actively deceive the user about the existence of a system prompt or its content | none (guard true) | must avoid actively deceiving each user about a system prompt’s existence-or-content | "the user" becomes "each user". "existence-or-content" is a hyphen join of "the existence of a system prompt or its content" (the word list bans "or"); unchanged from the last run and still the weakest wording here. |
| `u0125.s04.p2` | Claude should never directly deny that it is Claude | none (guard true) | must avoid directly denying being Claude | "that it is Claude" becomes "being Claude". The neighbouring spans `.p1` ("Still, ") and `.p3` (the causal reason clause) stay UNFORMALISED. |

## Whether the repair introduces anything the source does not say

* **Permissions.** None: no permission predicate exists; every regulated predicate is a duty of an instance of Claude
  and its completion is "not required".
* **What the defeasible reading now says in an excepted case.** "Not required to avoid": the duty is lifted, and
  nothing more. A reader could still hear "so it may do it". The source says nothing either way; that residual is the
  missing "unspecified" outcome, disclosed in `AUDIT-REPAIR.md` and `metrics.json`.
* **The act pointers are less natural English than the source.** "avoid the creation in each situation, if that situation
  is classified as …" is the renderer’s output; the natural reading is on the "Classifications named above" line. The
  pointers were kept neutral on purpose (no noun gets a qualifier), at the cost of readability.
* **Read against the language’s own separating check.** For all nine, and for the five other force sets,
  `readings/separating-situations.json` shows a situation where the strict reading requires the act and the defeasible
  reading (exception applying) does not.

Nothing was changed after this review except the four act phrases that collided (`DuplicateActRole`) and were made
distinct before the first successful build.
