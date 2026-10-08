**18 of the 20 sampled units are faithful.** I couldn't create `AUDIT.md`: writing to the run directory was denied, so the audit is printed below. Everything was read-only with no model calls.

**How I sampled:** `random.Random("20260929T1800Z").sample(pool, 20)` over the 55 units with status CHECKED, LABELLED, OPEN or READINGS, in `units.json` order. That drew 14 LABELLED, 5 READINGS and 1 OPEN unit. The only CHECKED unit, `u0248`, wasn't drawn.

**Faithful (18):**
- **LABELLED (14):** the heading markers of `u0002`, `u0008`, `u0013`, `u0040`, `u0042`, `u0075`, `u0083`, `u0151`, `u0162`, `u0195`, `u0257` and `u0268`, plus `u0103` and `u0298`. Every heading label matches the source bytes, and each marker sits right next to its unformalised title.
- **READINGS (3):** `u0052.s01`, `u0168.s01` and `u0263.s04.p2`. The act, the condition and the strict/defeasible pair match the source. For these duties, "not required" in excepted cases is what a lifted duty means.
- **OPEN (1):** `u0073.s05`. "Generally" justifies giving it one defeasible reading. "Not unsafe, unethical, or against Anthropic's guidelines" is correctly read as none of the three.

**Minor issues, not counted:**
- The bare "### " markers of `u0040.heading` and `u0083.heading` carry a stray `genuine_helpfulness` tag inherited from the parent. This is in the ledger only.
- In `u0168.s01`, "these lines" is resolved to the hard constraints only in the ledger note, not in the predicate wording as the run's `FEATURE-REVIEW.md` says.
- The English rendering of `u0073.s05` does not parse back to the same rule.

**Unfaithful (2):**
- **`u0156.s03`** ("Claude shouldn't actively deceive the user…"). The defeasible reading is supposed to lift the prohibition in excepted cases. But every regulated act must default to allow or deny, and the default here is deny, so an excepted case still comes out "not permitted". That makes the defeasible reading identical to the strict one: that reading is effectively missing, and the unit forbids something where the source says nothing. The model recorded as telling the two readings apart can't do so; it is one empty model shared by all 14 reading sets. The run discloses this limitation in `metrics.json`, but as in the previous audit, disclosure doesn't cure added content.
- **`u0165.s03`** (the cyberweapons hard constraint). Its defeasible reading collapses into the strict one in the same way. The impact is lower because the translator's recorded choice keeps the strict reading, which "absolute restrictions" supports. Two further problems:
  - The act phrase and both English readings drop "if deployed".
  - "cyberweapons-or-malicious-code that could…" makes the damage clause cover cyberweapons too, which the open term leaves undecided.

**Three highest-value missing features:**
1. **Allow "unspecified" as an outcome.** A regulated act should be able to leave cases that no rule covers undecided. The forced allow/deny default caused the rejections in both of the last two audits: first an invented permission, now an invented prohibition.
2. **Let norm reading candidates hold their rules.** The check should then require a model that really tells the readings apart. That would have caught this collapse, made the translator's narrowing choices take effect, and removed the main document's UNKNOWN premise status and the need for companion documents.
3. **Let norms combine with attribution, causation, quantities and ordering.** Act phrases also need structure, without the 80-character limit or the reserved-word ban. Most of the 668 units blocked on norms are "we want Claude to…", "could cause…" or "vast majority…" sentences.
