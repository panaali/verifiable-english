# Corrections to frozen preregistration text (experiments/)

Frozen files are not edited (hashes in `PREREG-HASHES.txt`). Corrections are recorded here.

## 2026-09-22: obfuscated-arguments position

**Affected:** `PREREG-DESIGN.md` lines 15-17, which adopt the 2026-09-21 correction banners of
`design/ve-protocol-design.md` §§3(a), 4/F0. Those banners said explicit premises and checked deductions "contribute
nothing on the canonical cases" of obfuscated arguments.

**Correction:** that holds only under leaf acceptance (leaves accepted without proof). Under a mandatory-proof rule (nothing is accepted unless VE's verified checker derives it from declared, reviewed foundations), a dishonest prover cannot win by assuming false sub-claims; this defeats the Barnes-Christiano construction for fully formalised claims. Limits: the honest side wins only when the truth has an affordable proof (otherwise "unresolved"); proofs beyond budget (debate's PSPACE regime); foundation leaves accepted without proof; formalisation faithfulness; cost. The benefit comes from sound proof checking, not from VE's English surface.

Sources: `design/positioning-vs-debate-theory.md` correction 2; `~/code/manage-agents/reviews/obfuscation-recheck.md` §3.
The preregistered hypotheses, arms and analyses are unaffected; only the framing sentence is qualified.
