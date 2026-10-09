# Audit repair, run 20261008T1800Z

The latest audit received is `AUDIT-20261007T1800Z-received.md` (20/20 faithful). No audit marked a unit unfaithful or incomplete, and the run directory has no `AUDIT.md` of its own, so nothing needed repair from an audit. No unit that an audit rejected keeps a covered status.

The lead's rules of 2026-10-08 were applied by the previous run (`AUDIT-REPAIR-prev-20261008T0600Z.md`: readings come from the words only). This run re-checked the new content against them:

* Every candidate that gained content already was a candidate of its set; no reading was added. The defeasible candidate of a "should" set was recorded without content before; its content is the strict rule with one `unless` (an exception the text does not name), as `exception: unstated` was on the soft chain. The text spans that admit the two readings are those of the previous run.
* No right is turned into a duty, and no permission was invented: every predicate keeps the `unspecified` completion (the `deny` of the old soft-chain companion is gone from the documents of this run).
* Verified bytes: the previous run reported 2,235 audit-verified bytes. This run drops `u0073.s05` (234 bytes) until re-audited, because the English of its rule changed when `reword.py` removed an apostrophe from one act wording (no meaning change), leaving 2,001 bytes (1.08%). The five units changed by the previous run's repair are still waiting for re-audit.
