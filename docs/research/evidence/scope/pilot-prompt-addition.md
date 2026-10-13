# SC-M0: proposed addition to the pilot prompts (not applied)

Draft text for the orchestrator to add to the next constitution and UDHR pilot prompts
(`manage-agents/prompts/pilot-*.txt`). It is not applied from this branch: the prompts are shared pipeline files
outside the repository, and the runs that would follow them are model runs (scope-phase1.md, section 4).

---

**Cross-sentence scope tally (SC-M0).** A *governor* is a unit whose words change other units: a lead-in ending in
":" over the list after it; a heading or a bullet's bold label over the text under it; a sentence that names a list
("The current hard constraints ... are as follows."); a later sentence that narrows, replaces or carves out the
condition of earlier rules, or orders them ("notwithstanding", "subject to"); a "This ..." / "That said, ..."
sentence that qualifies earlier text.

1. On every governor unit and every unit it governs, add `other:scope` to `other_blockers` (or make it
   `missing_feature` when scope is the main thing missing). Do not remove any existing tag.
2. On every governed unit, record `governed_by: [<governor unit ids>]`. Where a unit already records
   `scoped_by_source`, also record that unit in `governed_by`; keep `scoped_by` as it is.
3. Write `scope-tally.json` beside `units.json`: for each governor, `{unit, reach, effect, governed, bytes}` with
   `reach` one of `list`, `list_name`, `anchor`, `label`, `rules`, `frontier` and `effect` one of `frame`,
   `reguard`, `carve-out`, `precedes`, `yields`, `title`, or `none` for a sentence about a list that changes no rule
   (u0170.s01); then the totals of units and bytes by reach and by effect. A reach the text leaves open is
   `frontier` with every candidate listed; never pick one.
4. Do not change any unit's status or content for this tally.

---

Check after the run: `research/scope/sc_m0_tally.py` regenerates the structural reaches (`list`, `label`) from the
source bytes; the run's `governed_by` for those reaches should equal the script's (`scope-tally.json`,
`governed_by`), and every difference is a finding for the pilot audit.
