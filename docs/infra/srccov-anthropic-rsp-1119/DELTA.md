# srccov-anthropic-rsp-1119 DELTA

No user-visible change of VE. This item changes no product code under `ve/`, `lean/` or `rust/`, and no gate, test
selection or tool logic. VE's diagnostics, fault order, fields, verdicts, availability and CPU stay as they are on main
at e01c3d6680 (the merge base). All changes are inside one use case:

- its vocabulary legends: text appended to the descriptions in `usecases/anthropic-rsp/rsp_vocabulary.py` (written to
  `environment.d1.json`). A carried quote follows its citation, never inside it. There are 21 changed legends (17 predicates, 4 threshold constants). Each keeps every word of
  its base description, in order, and no other field of the symbol (arguments, act, verbalisation, regulated role)
  changes. Evidence: `python3 docs/infra/srccov-anthropic-rsp-1119/evidence/legend_keep.py` printed "21 changed
  legends; 0 lose base words or change another field" (evidence/legend_keep.txt).
- its D3 date legends: descriptions of eight changelog date constants in `usecases/anthropic-rsp/stage0.py`
  (`DATE_WORDS`). D3's stated dates, goals and certificates do not change: `stage0.json` P4 still stores booleans
  only.
- its span records: `build_document.py` records three units as hopes (`unformalised`, reason `hope`, instead of
  `attributed`) and puts five headings in heading units. `spans.json` goes from 303 to 307 units.
- the outputs that measure or hash these files, which REPORT.md lists. The byte totals move:
  - CHECKED 5,327 -> 5,320: the sub-heading "Scope." leaves the D3-routed unit;
  - OPEN 13,214 -> 13,072: four headings leave OPEN units;
  - LABELLED 37,248 -> 36,890;
  - UNFORMALISED 3,621 -> 4,128: the three hope records.

No answer in `results.json` changes: `run.py` rewrote only the metrics that copy the measurement (M3's
`bytes_by_status` and `bytes_by_kind`, as above, and M10's units, 303 -> 307), and its items, comparison, mutants
and section 9 comparisons are byte for byte main's (`run.py --check` exits 0;
`test_rsp_run_recomputes_every_key_item_and_records_causes` is in the selected run). The use case's README states
the new byte figures (D3 442 B; the no-claim, JT and readings rows of the gaps table). This follows the fsf-repair-f1-leveldefs-1119 and fsf-r1 precedents (their DELTA.md files). No
standing ruling is needed, and no row is reserved for the DRI.
