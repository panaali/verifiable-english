# P5 study-cap schedule amendment — 2026-09-22

The study cap remains **$40**. The first schedule fitting that cap is **(a)**:
Gemini primary plus Qwen replication, all X/S/VE/L arms, four unchanged dev
families and **nine scored families** (27 scored packets). Cross-examination
retains three isolated initial answers and one adaptive follow-up. All v9
stage input/output limits and LOW thinking remain unchanged.

**2026-09-22 orchestrator amendments adopted:** the common matched ceiling is
**$0.45** for every arm. Only accepted provider responses count toward it;
infrastructure failures/holds and reconciled interrupted calls count against
the $40 study cap only. The amended largest retained-plus-future VE bound is
**$0.4275424776**. The former $0.4465404776 bound included infrastructure and
CPU attribution. See [AMENDMENTS.md](AMENDMENTS.md) for acceptance semantics.

| Priority | Judges | Scored families | Worst-case study total | $40 gate |
|---|---|---:|---:|---|
| (a) | Gemini + Qwen | 9 | $35.2264590298 | Pass |
| (b) | Gemini | 24 | $70.3533941698 | Fail |
| (c) | Gemini | 9 | $34.3760741698 | Pass |

For (a), the next balanced increment, 12 families, costs $42.6181656898.
For (c), 12 costs $41.5715381698. The calculation reserves the full $0.30 new
calibration authorization and retains **$2.8957301698** in prior study ledger
commitments. This includes the full v6/v7 rewrite and v8 review envelopes,
provider and old calibration charges, the superseded dev attempt and the
already charged $0.1344 CPU allowance. Revision actual costs are covered by
those retained envelopes, not added twice or refunded. Generator-rendered
materials need no further paraphrase calls. The earlier $69.8036611616 formula
was a 24-family schedule envelope, not this retained-ledger accounting.

Selection is deterministic: ascending original family IDs, first three families
in each of the 20/40/60-predicate strata, i.e. `p5-scored-00` through `08`.
Every selected family contributes its complete sibling triple. All 84 reviewed
packets and their evidence remain archived. Runtime assignments, block
reservations, analysis denominators and cost reports use only the selected
families. No selection uses model outcomes, diagnoses or favorable gate scores.

Nine independent scored families replace 24. Under square-root-N planning,
standard errors/interval half-widths increase by **sqrt(24/9) = 1.633**: the
primary planning half-width becomes about **±0.49**, potentially **±0.49–0.82**,
and benign difference about **±0.245**. These are planning approximations,
not a measured power estimate. The +0.10 margin would need a point contrast
roughly +0.59 at ±0.49 precision. Zero harmful discordances in nine families
still leaves a one-sided exact 95% upper rate of **28.3%**. The 20,000 family
bootstrap draws, seed, estimands, multiplicity and boundary safeguards remain
unchanged. This is a feasibility pilot with markedly reduced precision.

Six genuinely new 4,096-token Gemini configs were calibrated through Vertex ADC
for **$0.035710**, inside the $0.30 cap. Complete earlier matching configs were
reused; every bill remains append-only. No dev/scored call was made. Native
counts cover all **1,764 stage fixtures plus 84 common packets**, a superset of
the selected schedule, with the exact config correction and enlarged history
reserves. All counts pass; the largest common packet is 1,650 of 2,048 tokens.

After passing the renewed freeze gates, the separate-authorisation dev resume
command is:

```sh
UV_CACHE_DIR=/private/tmp/ve-uv-cache-codex uv run python \
  experiments/P5-shifting-definitions/run_p5.py resume --split dev --cap-usd 40
```

The cap is cumulative study spending, not an additional $40. The dev online
reservation is $9.8556088800. Scored execution still requires a completed dev
contract/source-fidelity gate. This amendment does not authorize either run.
