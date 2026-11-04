# sc-9 DELTA

No user-visible delta. sc-9 is pilot tooling and measurement. It changes no file under `ve/`, `lean/`, `rust/` or `tools/` (`git diff --stat $(git merge-base HEAD main) -- ve lean rust tools` prints nothing), and it leaves the committed translation unchanged. No standing ruling is needed, so there is no row.

What the probe measured, before (the translation as committed) and after (the soft form), is recorded in `usecases/claude-constitution-pilot/run-20261104T0716Z/SUMMARY.md`. Those are properties of a probe document, not changes to the product. Any conflict or separation it reports about the source is a CANDIDATE under R14 until an independent source check has run.
