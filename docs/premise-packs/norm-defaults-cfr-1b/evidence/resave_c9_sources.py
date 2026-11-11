"""Re-ask every saved C9 point-status case and add only the `sources` field Lean now sends (norm-defaults-cfr-1b)."""
import importlib.util, json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
RUN = Path("usecases/claude-constitution-pilot/run-20261104T0716Z").resolve()
def load(name, file):
    spec = importlib.util.spec_from_file_location(name, RUN / file); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m
migrate, c9_status = load("sc9_migrate_soft", "migrate_soft.py"), load("sc9_status", "c9_status.py")
from ve.readings_route import run_lean
probe = migrate.PROBE
meta, source = migrate.pilot.read(probe)
tmp = Path(tempfile.mkdtemp()); strict = tmp / "strict.ve.md"
migrate.pilot.write(strict, c9_status.strict_twin(meta), source)
for document, path in (("after", probe), ("strict", strict)):
    out = RUN / "answers" / document / "point-status-c9.out"
    data = json.loads(out.read_text())
    cases, _ = c9_status.point_status_cases(path)
    live = run_lean(cases)
    assert len(live) == len(data["cases"]) == len(cases)
    for record, case, answer in zip(data["cases"], cases, live, strict=True):
        assert record["inner_request"] == case["inner"]
        old = record["answer"]
        stripped = {**answer, "inner": {k: v for k, v in answer["inner"].items() if k != "sources"}}
        assert stripped == old, (document, record["scenario"])
        assert [s["rule"] for s in answer["inner"]["sources"]] == answer["inner"]["rules"]
        record["answer"] = answer
    out.write_text(json.dumps(data, indent=1) + "\n")
    print(document, "re-saved", len(live), "answers; only `sources` added")
