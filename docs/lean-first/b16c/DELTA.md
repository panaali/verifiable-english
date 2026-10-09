# Lean-first batch 16c: document mode progress, incomplete

The branch forked from `67ae1e5a` (`main` at start). The saved scope captures the later
`main..f0c44d43 --no-merges` range after `main` advanced to `abc30811`.
This is an incremental implementation of the JSON boundary and response binding. The batch's
profile composition, 99% pilot target, corpus targets, Python deletion, and nine-corpus A/B
gate are **not complete**. No claim of batch 16c acceptance is made.

## Saved measurement

`report.py` renders this block only from the captured files in `evidence/`.
`tests/test_b16c_evidence.py` regenerates it and checks the per-case ledger. The scope is
`main..HEAD --no-merges` as captured at the final code commit, so later syncs and merges do not
change the historical report.

<!-- BEGIN GENERATED B16C METRICS -->
- Saved scope: `abc30811..f0c44d43 --no-merges`, 5 commit(s): `f0c44d43`, `1fde205e`, `c686d65f`, `8ff3ef5d`, `d094b056`.
- pilots: Lean decides 4/412; 408 listed residues.
- rights: Lean decides 0/1250; 1250 listed residues.
- norm_defaults: Lean decides 0/1010; 1010 listed residues.
- document: Lean decides 843/1816; 973 listed residues.
- Per-case residue rows: 3641. Seeded faults caught: 3/3.
- Clean gate at `f0c44d43`: passed; 13362 passed, 92 skipped, 0 failed; 36 Rust tests passed.
<!-- END GENERATED B16C METRICS -->

The 412 pilot inputs include eight `ve-document@2` documents, which go to the discourse
route. The @1 share is 4/404. Every residue, including invalid inputs the current mode
marks undecided, is named with its cause and source hash in `evidence/residues.json.gz`.
The dominant causes are norm-defaults (904 document-corpus cases, 339 pilots and all
1,010 norm-defaults cases), rights/readings (all 1,250 rights cases), soft norms (22
pilots), norm content (18 pilots), senses (7 pilots), fenced content (9 document cases),
and distinguishing models (26 document cases). The ledger preserves the smaller
malformed-profile and environment-key groups individually.

## Boundary and binding change

The document mode's case array and front matter now use Lean's `Json.parse`, which accepts
JSON `null` and standard JSON number forms. The frozen `VE.JsonInput` parser and hash-frozen
`Main.lean` are untouched. This is the smaller trusted change: one mode-specific entry
point and a document-specific identity serializer. Certificate canonicalisation keeps its
null-refusing behavior. `content: null` is absent content in the unit row, as in the
Python loader. The document identity still includes the authored null. Values Lean cannot
serialize into Python's document identity are `CheckerUnavailable`, never a verdict.

The generated document response schema now types checked formula content, exact two-number
spans, and the existing identity and count fields. The receiver binds every accepted
unit's authored fields, checked AST, identities, parents, coverage tables and residual
counts to the request, and checks status values against the allowed set. A forged alternate formula with its matching meaning ID
is rejected by `test_identities_and_content_are_leans`. `kind` and `meaning` remain
untyped in the response schema itself; their request equality is checked by the receiver.
This does **not** satisfy the requested fully typed schema yet.

## Verification and outstanding work

- `lake build ve_service`, `lake build ve_response_decode`, schema generation/check, and
  `lean/audit.py` passed. The audit found 4,865 named theorem declarations with only the
  approved axiom allowlist. No theorem statement changed.
- Document-focused tests: 332 passed, 83 existing strict xfails. The three seeded bugs
  in `evidence/mutants.json` each made its named test fail, then were removed: treating
  null content as present; accepting a forged alternate checked formula; accepting an
  untyped formula in the response schema.
- The full gate passed on clean code commit `f0c44d43` (`evidence/gate.json`):
  13,362 passed, 92 allowed skips, zero failures, and 36 Rust tests passed. The
  Lean full build and audit passed. `python3 tools/trust_map.py --check` passed
  with zero trusted-line growth. The initial clean gate found a deep JSON parser
  crash and stale inventories; the second had zero test failures but two unlisted
  Rust-scope skips. Both were fixed before the passing run.
- Nine-corpus A/B, differential fuzz across all parsers, and latency measurement
  were **not run** for this incomplete migration. The earlier document-focused
  suite and the saved per-case share are the only corpus measurements here.
- Lean still needs composition of the norm-defaults, rights, readings@1 (including
  defaults in parts), soft-norms, senses, norms, surface, model and remaining family
  routes. The Python document loader, coverage and report wrapper remain necessary for
  the listed residues and were not deleted. Deletion must follow a measured empty
  retained-path ledger and zero unlisted A/B differences.

Acceptance classification: the JSON boundary, binding and tests are AGENT work completed
here. The 16c profile/deletion/corpus gates are AGENT work pending. Any DRI acceptance of
diagnostic changes is HUMAN work pending; none is claimed.
