"""norm-defaults-cfr-1 evidence: Lean's own norm-defaults status and certificate rows all pass `bind_answers`.

Log: `PYTHONPATH=docs/premise-packs/norm-defaults-cfr-1/evidence NDLOG=<file> uv run pytest -p genuine_pairs ...`
records every ok (case, row) the service returns for those kinds (after the schema check). Check:
`uv run python docs/premise-packs/norm-defaults-cfr-1/evidence/genuine_pairs.py <file>` runs the binding on each.
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
    counts, refused = collections.Counter(), []
    for line in open(sys.argv[1]):
        pair = json.loads(line)
        shape = "document" if "document" in pair["case"] else "norms"
        acts = "acts@0" in pair["case"]["environment"].get("profiles", [])
        counts[(pair["case"]["kind"], shape, "acts" if acts else "-")] += 1
        try:
            _bind_norm_defaults(pair["row"], pair["case"])
        except Invalid as exc:
            refused.append(str(exc))
    print(json.dumps({"pairs": sum(counts.values()), "by_kind_source": {" ".join(k): v for k, v in sorted(counts.items())},
                      "refused": len(refused), "first_refusals": refused[:5]}, indent=1))
