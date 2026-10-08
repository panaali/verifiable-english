# Audit repair and readings-from-the-words repair, run 20261008T0600Z

**Audit.** The latest audit received (`AUDIT-20261007T1800Z-received.md`, run 20261007T1800Z) accepted all 20 sampled units and marked none unfaithful or incomplete, so there was nothing to repair for it. Earlier repairs (`AUDIT-REPAIR-prev.md`, `AUDIT-REPAIR-20261005T1800Z.md`) stand.

**New rule (lead, 2026-10-08): readings come from the words only.** I checked all nine reading sets of the previous run (`repair.py` applies the result; `metrics.json` `readings_from_the_words_rule`):

| Set | Result | Words that admit it |
|---|---|---|
| u0052.s01 "should always use good judgment" | **defeasible reading removed**; one strict rule, status READINGS to OPEN | none: "always" excludes exceptions, and no span of the text states or implies one (same ground as the lead's rule on "never"/"shall") |
| u0036.s05 "should ask for clarification", u0263.s04.p2 "it should comply" | both readings kept | "should" is "directive language" (u0253.s04) and the document "generally favor[s] cultivating good values and judgment over strict rules" (u0011.s01); cited in the note and the admission |
| u0125.s04.p2 "should never directly deny", u0156.s03 "shouldn't actively deceive" | both readings kept | the text implies exceptions to the honesty norm they apply: "should basically never directly lie or actively deceive" (u0109.s06), honesty is "something quite similar to" a hard constraint (u0109.s05); cited |
| u0062.s01, u0123.s02.p1 ("can"), u0123.s03 ("cannot") | kept (permission/ability; narrow/wide scope) | the words "can"/"cannot" and the position of "while role-playing as a custom AI persona" |
| u0123.s01.p1 ("permitted") | kept (three limits readings) | the scope readings of u0123.s03 only; the force is not ambiguous |

No reading adds a party, a duty-bearer or a convention from outside knowledge. **Open terms:** `broad_safety`, `appropriate_oversight`, `genuine_helpfulness` and `ethical_harm` were declared but used by no unit and their `factors` were mine, so they are removed (36 to 32); `good_judgment` keeps the one question its words raise ("what counts as good judgment").

**Judgment calls for the auditor** (also in `metrics.json`): (1) plain "should" keeps both readings (u0036.s05, u0263.s04.p2); the alternative is one strict reading like u0168.s01; (2) "should never" / "shouldn't" keep the defeasible reading on the strength of the honesty spans, which are about honesty in general; (3) the ability reading of "can legitimately instruct" (u0123.s02.p1) is admitted by "can" although "legitimately" leans to permission.

**Verified bytes.** u0052.s01 changed in substance; u0036.s05, u0125.s04.p2, u0156.s03 and u0263.s04.p2 only gained the cited spans in their note and admission wording (readings unchanged). All five were in the audited set; none counts as audit-verified until re-audited: **2,235 audit-verified covered bytes (1.21%)**, against 2,996 claimed (2,569 if the four justification-only edits were ignored).
