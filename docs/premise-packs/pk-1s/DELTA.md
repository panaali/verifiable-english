# pk-1s DELTA

There is no user-visible delta. This item adds documents only:
- `docs/spec/premise-packs.md`;
- its statement stub `docs/spec/premise-packs/SpecStubs_pk1.lean` (outside `lean/`, so it is imported by nothing);
- its seeded-bug record `docs/spec/premise-packs/mutants.json`.

No Lean, Python or Rust product file, generated file, schema, golden, diagnostic text or verdict changes. The
trust budget is unchanged (`tools/trust_map.py --check`: K +0, S +0, trusted +0 against `802b8ff9b`). So no row
needs a ruling.

The deltas pk-1 will carry are planned in the spec, section 5. All of them are byte-identical on today's routes.
pk-1's own DELTA records its trust growth under R16.
