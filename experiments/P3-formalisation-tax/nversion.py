"""N-version check: the item author's VE vs the independent agent's VE on many
perturbed worlds; the reference arbitrates any disagreement. Writes nversion_results.json."""
import json
import harness as H
from ve import evaluate

N = int(__import__("os").environ.get("P3_NV", "2000"))
out = []
for d in sorted(H.ITEMS.iterdir()):
    if not (d / "agent" / "formalisation.ve").exists():
        continue
    item = H.load_item(d.name)
    H.FORMAL_SUBDIR = ""
    env_m, doc_m, b_m = H.load_formalisation(item)
    H.FORMAL_SUBDIR = "agent"
    env_a, doc_a, b_a = H.load_formalisation(item)
    H.FORMAL_SUBDIR = ""
    dis, me_wrong, agent_wrong = 0, 0, 0
    for p in H.perturbations(item, N) + H.targeted_perturbations(item):
        q = p["q"] or {}
        vm = H.ve_answer(item, env_m, doc_m, b_m, q, p["world"], p["request"])["answer"]
        va = H.ve_answer(item, env_a, doc_a, b_a, q, p["world"], p["request"])["answer"]
        if vm != va:
            dis += 1
            ref = H.ref_answer(item, q, p["world"], p["request"])
            me_wrong += vm != ref
            agent_wrong += va != ref
    row = {"item": d.name, "worlds": N + len(H.targeted_perturbations(item)), "disagreements": dis, "author_wrong": me_wrong, "agent_wrong": agent_wrong,
           "author_chars": len((d / "formalisation.ve").read_text()), "agent_chars": len((d / "agent" / "formalisation.ve").read_text())}
    out.append(row)
    print(json.dumps(row), flush=True)
(H.HERE / "nversion_results.json").write_text(json.dumps(out, indent=1) + "\n")
