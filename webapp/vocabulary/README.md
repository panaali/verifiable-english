# Web app English measurement

`environment.json` declares the app's sorts, predicates and constants.
`english-vocabulary.json` gives exact display aliases for JSON, CSRF header and
request ID. `ui-terms.json` is the closed word inventory for short labels;
its aliases include VE/app, desk/workspace, claim/conclusion and
countermodel/world. These files are a vocabulary for app copy, separate from
the editable vocabulary in a user's document.

`catalogue.json` inventories the served HTML, browser JavaScript literals,
Python literals that can reach the page, and every reader string of the
VE-built Asimov section (`ve_webapp/asimov.json`; the explanation sentences a
live re-run can add are catalogued from `ve_webapp/asimov.py`). Rebuild
`asimov.json` before regenerating the catalogue. Every visible entry is a SENTENCE or
LABEL. A sentence marked `gap` failed the writable English parser's complete
all-derivations check. `dynamic_gaps` records text whose runtime value cannot
be checked as a fixed sentence. INTERNAL entries make the source inventory
closed: a source edit requires catalogue review.

Run the measurement and strict gate from the repository root:

```bash
.venv/bin/python -m webapp.vocabulary.audit --strict
make webapp-build
```

The strict gate returns a nonzero exit code while any gap remains. It is
the prerequisite of the `webapp-build` target, so that build stops on a copy
violation. It is expected to fail at this measurement point. The regular test checks the
served page, the source inventory, the vocabulary, all passing VE sentences,
and all labels; it keeps the measured gaps explicit so the broader suite can
stay green. To review changes after editing copy, run
`.venv/bin/python -m webapp.vocabulary.build_catalogue`, inspect the catalogue
diff, and run the strict gate again. Regeneration is not a waiver: it records
new failures.

The main language gaps are commands and questions; temporal and numeric
limits; modal rule text; causal explanations, identity and synonym claims;
legal quotations; and sentence fragments in example descriptions. Several
example documents use a different declared vocabulary or the norms grammar.
Browser messages also include arbitrary user wording, library diagnostics,
model suggestions, generated finite-world descriptions and revision numbers.
Those paths require a runtime admission policy before the full page can be
certified as VE. The catalogue lists each fixed failing string and each
dynamic path; none is silently declared valid.
