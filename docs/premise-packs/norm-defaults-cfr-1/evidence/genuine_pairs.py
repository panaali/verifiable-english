"""norm-defaults-cfr-1 evidence: Lean's own status and certificate rows pass the row schema and the binding.

Log: `PYTHONPATH=docs/premise-packs/norm-defaults-cfr-1/evidence NDLOG=<file> uv run pytest -p genuine_pairs ...`
records every ok (case, row) the service returns for those kinds (after the schema check). Check:
`uv run python docs/premise-packs/norm-defaults-cfr-1/evidence/genuine_pairs.py <file>` runs the row schema
(`check_row`) and the binding (`_bind_norm_defaults`) of this tree on each.
"""
import collections
import json
import os
import sys

if __name__ != "__main__":  # the pytest plugin
    import ve.backends.lean_service as service

    _check = service.check_response

    def _logged(mode, response, request):
        _check(mode, response, request)
        if mode == "norm-defaults":
            cases = request.get("cases") or []
            with open(os.environ["NDLOG"], "a") as out:
                for result in response.get("results") or ():
                    row, case = result.get("result"), cases[result.get("index")]
                    if row.get("status") == "ok" and case.get("kind") in ("norm-defaults-status",
                                                                         "norm-defaults-certificate"):
                        out.write(json.dumps({"case": case, "row": row}) + "\n")

    service.check_response = _logged
else:
    from ve.backends.lean_service import Invalid, _bind_norm_defaults
    from ve.backends.service_schema import check_row
    counts, refused = collections.Counter(), []
    for line in open(sys.argv[1]):
        pair = json.loads(line)
        shape = "document" if "document" in pair["case"] else "norms"
        profiles = pair["case"]["environment"].get("profiles", [])
        layers = [p for p in ("soft-norms@0", "events@0", "rights@0", "acts@0") if p in profiles] or ["plain"]
        counts[(pair["case"]["kind"], shape, "+".join(layers))] += 1
        try:
            check_row("norm-defaults", pair["row"], pair["case"], 0)
            _bind_norm_defaults(pair["row"], pair["case"])
        except Invalid as exc:
            refused.append(str(exc))
    print(json.dumps({"pairs": sum(counts.values()), "by_kind_source": {" ".join(k): v for k, v in sorted(counts.items())},
                      "refused": len(refused), "first_refusals": refused[:5]}, indent=1))
