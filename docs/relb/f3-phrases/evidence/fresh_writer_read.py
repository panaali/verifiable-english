"""Read the fresh writer's ten sentences (fresh-writer/writer-out.txt, committed unedited) in the eligibility
environment with the plain wordings declared (usecases/eligibility/plain_wordings.json) and, with --main, without
them. Each sentence: READ-EQUAL (one reading, the fact), READ-OTHER (one reading, not the fact: a wrong reading)
or REFUSED. usage: uv run python docs/relb/f3-phrases/evidence/fresh_writer_read.py [--main]"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[4]; HERE = Path(__file__).resolve().parent / "fresh-writer"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "usecases" / "eligibility"))
import translation as T
from ve.environment import Environment
from ve.errors import VEError
from ve.surface.time import parse_w6_sentence
from ve.units import elaborate_quantity
raw = T.environment()
if "--main" not in sys.argv:
    for n, t in json.loads((ROOT / "usecases/eligibility/plain_wordings.json").read_text())["predicates"].items():
        raw["vocabulary"]["predicates"][n]["verbalisation"] = t
env = Environment(raw)
facts = {f["id"]: f["formula"] for f in json.loads((HERE / "facts.json").read_text())}
counts = {"READ-EQUAL": 0, "READ-OTHER": 0, "REFUSED": 0}
for line in (HERE / "writer-out.txt").read_text().splitlines():
    if ":" not in line: continue
    fid, sentence = line.split(":", 1); sentence = sentence.strip()
    canonical, _ = elaborate_quantity(env, T.q(facts[fid]))
    try:
        got = parse_w6_sentence(env, sentence)
        verdict = "READ-EQUAL" if got == canonical else "READ-OTHER"
        why = json.dumps(got["formula"])
    except VEError as exc:
        verdict, why = "REFUSED", f"{type(exc).__name__}: {str(exc)[:100]}"
    counts[verdict] += 1
    print(f"{fid:4} {verdict:10} {sentence[:90]} :: {why[:110]}")
print(json.dumps(counts))
