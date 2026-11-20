"""C5 dry check for F7: render each unit's legend part with the reads-1119 counter's own seq_unit_legends, and the counted
legend carrier with legend_raw + _omit_legend_segments, at two VE commits of a worktree."""
import importlib.util, json, subprocess, sys
counter, ve, base, head = sys.argv[1:5]
import importlib.machinery
spec = importlib.util.spec_from_loader("ucaudit_r16", importlib.machinery.SourceFileLoader("ucaudit_r16", counter))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
def show_at(commit):
    def show(n):
        r = subprocess.run(["git", "-C", ve, "show", f"{commit}:usecases/safety-framework/{n}"], capture_output=True, text=True)
        return r.stdout if r.returncode == 0 else None
    return show
SENT = {
 "governance_found_acceptable_with_safety_case_where_ccl_reached": ["In particular, we will deem deployment mitigations adequate if the evidence suggests that for the T/CCLs the model has reached, the increase in likelihood of harm from the proposed external deployment has been reduced to an acceptable level."],
 "mitigates": ["We assess that the deployment mitigations have brought the residual risk of harm to an acceptable level, based on considerations such as the effectiveness of mitigations, the scope of the deployment, what capabilities and mitigations are available on other publicly available models (e.g. if other models are similarly capable and have few mitigations, then the marginal risk added by our external deployment is likely low), and the historical incidence and severity of related events.",
   "We assess that the deployment mitigations have brought the residual risk of severe harm to an acceptable level, based on considerations such as the effectiveness of mitigations, and information pertaining to model propensities and the severity of related events.",
   "We assess that the deployment mitigations have brought the residual risk of significant harm to an acceptable level, based on considerations such as the effectiveness of mitigations, and information pertaining to model propensities and the severity of related events, or if we assess that the model is very unlikely to possess the propensities that would be required for material risk of significant harm through misalignment risk."],
 "acceptable": ["A model for which inherent risk assessment indicates no T/CCL is reached will be deemed to pose an acceptable level of risk for further development and deployment, because it should not possess the capabilities required to substantially contribute to significant or severe risk scenarios."],
}
src = open(sys.argv[5]).read()
for k, ss in SENT.items():
    for s in ss: assert " ".join(src.split()).count(s) == 1, s[:60]
out = {}
for tag, commit in (("base", base), ("head", head)):
    show = show_at(commit); rules, facts = show("rules.d1.ve"), show("facts.d1.ve")
    units = list(m.rule_blocks(rules)) + list(m.rule_blocks(facts)) + ["FACTS"]
    rend = {u: m.seq_unit_legends("safety-framework", u, rules, facts, show) for u in units}
    vlines = show("vocabulary.py").splitlines()
    carrier = {k: " ".join(seg[0] for seg in m._omit_legend_segments(m.legend_raw(k, vlines)) if seg[0]) for k in SENT}
    out[tag] = (rend, carrier)
rb, cb = out["base"]; rh, ch = out["head"]
print("unit legend-part growth (bytes), units whose part changed:")
tot = 0
for u in rh:
    d = len(rh[u].encode()) - len(rb.get(u, "").encode())
    if d: print(f"  {u}: +{d}"); tot += d
print("  sum over all units:", tot)
for k, ss in SENT.items():
    users = [u for u in rh if u != "FACTS" and f"- {k}: " in rh[u]]
    for s in ss:
        shown = [u for u in users if s in rh[u]]
        counted = m.omit_norm(s) in ch[k]
        print(f"{k[:24]:24} {s[:40]!r}: rendered in {len(shown)}/{len(users)} using units {shown}; counted carrier head={counted} base={m.omit_norm(s) in cb[k]}")
