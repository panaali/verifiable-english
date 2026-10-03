"""Build the readability eval: items.json, writing.json and contexts/.

    uv run python experiments/readability-sonnet/build.py

Every reading key is a VE checker verdict computed here by `compute(item)`;
`ve_key.py ITEM` reruns the same call and prints the same JSON, which
items.json records as `ve_output` beside the command. Nothing here calls a
model. Lean must be built (`cd lean && lake build`) for the risk items.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vekit  # noqa: E402
from vekit import REPO, Environment  # noqa: E402
from items_spec import ITEMS, DNS  # noqa: E402

sys.path.insert(0, str(REPO))
LETTERS = "ABCD"
RISK_BINARY = REPO / "lean/.lake/build/bin/ve_risk_route"


def read_json(rel):
    return json.loads((REPO / rel).read_text())


# --- agent-policy -------------------------------------------------------------

def policy_rules():
    """Rule number -> rule content (the text after the header) in policy.ve."""
    rules = {}
    for line in (REPO / "usecases/agent-policy/policy.ve").read_text().splitlines():
        m = re.match(r"Rule (\d+)(?: \([^)]*\))?\. (.*)\Z", line)
        if m:
            rules[int(m[1])] = m[2]
    return rules


def excerpt(rules, numbers, contents):
    """Renumbered rule blocks; exception edges kept only between excerpted rules."""
    new = {orig: i for i, (orig, _) in enumerate(numbers, 1)}
    lines = []
    for orig, over in numbers:
        refs = [str(new[o]) for o in over]
        head = (f"Rule {new[orig]}." if not refs else
                f"Rule {new[orig]} (exception to rule {refs[0]})." if len(refs) == 1 else
                f"Rule {new[orig]} (exception to rules {', '.join(refs)}).")
        lines.append(head + " " + contents[orig])
    return "\n".join(lines)


def pruned_norm_item(raw, text, *, soft=False):
    """Parse on the use case's environment and keep only the words used, but
    only if VE renders the excerpt byte-for-byte as on the full environment
    (the vocabulary lint can select different wordings for a smaller
    vocabulary); otherwise keep the full vocabulary."""
    full = vekit.NormItem(raw, text, soft=soft)
    assert full.render() == text, "the excerpt is not VE's rendering of its rules"
    used = full.used()
    keep_p = {p for p in used if p in full.env.predicates}
    keep_c = {c for c in used if c in full.env.constants}
    pruned = vekit.prune(raw, keep_p, keep_c)
    pruned["profiles"] = sorted(set(raw["profiles"]) & set(vekit.PROFILES_NORMS + ["soft-norms@0"]) |
                                {"norm-defaults@0", "norms@0", "relational-fol@0"})
    try:
        small = vekit.NormItem(pruned, text, soft=soft)
        if small.render() == text:
            return small
    except Exception:
        pass
    return full


def situation_for(item_env, spec):
    domains = {s: [] for s in item_env.sorts}
    domains.update({s: list(v) for s, v in spec["domains"].items() if s in domains})
    constants = {c: c for c in item_env.constants}
    for c, d in item_env.constants.items():
        if c not in domains.get(d.sort, []):
            domains.setdefault(d.sort, []).append(c)
    return {"complete": True, "domains": domains, "constants": constants,
            "relations": {k: v for k, v in spec.get("relations", {}).items()}}


def norm_result(ni, situation, predicate, point, *, extra_text=()):
    verdict = ni.verdict(situation, predicate, point)
    role = ni.env.predicates[predicate].regulated.role
    label = vekit.norm_label(verdict, role)
    if label == "UNDECIDED":
        label = "DNS"
    text = ni.render()
    if extra_text:
        text = text + "\n" + "\n".join(extra_text)
    return dict(ve_text=text,
                legend=ni.completion_sentences() + vekit.legend_lines(ni.env, ni.used()),
                rendering={"type": "norm rule surface",
                           "renderer": "ve.norm_english.render_english (W1 rule blocks)",
                           "explicit_notation": explicit_notation(text)},
                verdict=verdict, label=label,
                legend_dependent="(by default)" in verdict["sentence"])


def explicit_notation(text):
    """Visible scaffolding a reader must decode: list markers or quoted names."""
    marks = []
    if re.search(r"\((?:a|b|i|ii)\) ", text):
        marks.append("list markers")
    if "first clause:" in text:
        marks.append("clause scaffolding")
    if 'classified as "' in text or "has the recorded relation" in text:
        marks.append("explicit-form fallback wording")
    if '"' in text:
        marks.append("quoted identifiers")
    return marks


def compute_agent_policy(item):
    raw = read_json("usecases/agent-policy/environment.unspecified.json")
    for p in ("permitted", "report_required"):
        raw["vocabulary"]["predicates"][p]["regulated"]["default"] = item["default"]
    text = excerpt(policy_rules(), item["rules"], policy_rules())
    ni = pruned_norm_item(raw, text)
    sit = situation_for(ni.doc.situation_environment(), item["situation"])
    return norm_result(ni, sit, item["predicate"], ["act"])


def compute_csam(item):
    import tests.test_norm_defaults as t
    from ve.norms import NormDocument
    from ve.norm_english import render_english
    raw = t.csam("unspecified").to_dict()
    text = render_english(NormDocument(Environment(vekit.without_norm_defaults(raw)), [t.CSAM_RULE]))[0]
    ni = vekit.NormItem(raw, text)
    strip = lambda r: {k: v for k, v in r.to_dict()["norm"].items() if k != "name"}
    assert [strip(r) for r in ni.parsed.rules] == [strip(t.CSAM_RULE)], "CSAM rule round trip"
    return norm_result(ni, t.CSAM_SITUATION, "csam_generation_permitted", [item["who"]])


ASIMOV_RULES = [(1, []), (2, [1]), (3, []), (8, [2]), (11, [])]


def compute_asimov(item):
    raw = read_json("usecases/asimov-laws/environment.json")
    raw.pop("alternatives", None)
    raw.pop("risk", None)
    raw["profiles"] = vekit.PROFILES_NORMS
    contents = policy_rules_from("usecases/asimov-laws/rules.ve")
    text = excerpt(contents, ASIMOV_RULES, contents)
    ni = pruned_norm_item(raw, text)
    sit = situation_for(ni.doc.situation_environment(),
                        {"domains": {"action": ["act"]}, "relations": item["relations"]})
    return norm_result(ni, sit, item["predicate"], ["act"])


def policy_rules_from(rel):
    rules = {}
    for line in (REPO / rel).read_text().splitlines():
        m = re.match(r"Rule (\d+)(?: \([^)]*\))?\. (.*)\Z", line)
        if m:
            rules[int(m[1])] = m[2]
    return rules


def fsf_blocks():
    blocks, name = {}, None
    for line in (REPO / "usecases/safety-framework/rules.d1.ve").read_text().splitlines():
        if line.startswith("## "):
            name = line[3:].split(" | ")[0]
            blocks[name] = {"header": line}
        elif line.startswith("Rule 1. ") and name:
            blocks[name]["rule"] = line[len("Rule 1. "):]
    return blocks


def compute_fsf(item):
    raw = read_json("usecases/safety-framework/environment.d1.json")
    raw.pop("soft", None)
    raw["vocabulary"].pop("soft", None)
    raw["profiles"] = vekit.PROFILES_NORMS
    blocks = fsf_blocks()
    order = item["blocks"]
    numbers = [(i, [order.index(o) + 1 for o in item["over"].get(name, [])]) for i, name in enumerate(order, 1)]
    contents = {i: blocks[name]["rule"] for i, name in enumerate(order, 1)}
    text = excerpt(contents, numbers, contents)
    ni = pruned_norm_item(raw, text)
    sit = situation_for(ni.doc.situation_environment(),
                        {"domains": {"proposal": ["p"]}, "relations": item["relations"]})
    return norm_result(ni, sit, item["predicate"], ["p"])


def fsf_en(item):
    blocks = fsf_blocks()
    quotes = []
    for name in item["blocks"]:
        quotes.extend(re.findall(r'"([^"]+)"', blocks[name]["header"].split(" | ", 2)[2]))
    return "\n\n".join(q if q.endswith(".") else q + "." for q in quotes)


SOFT_ENV = {
    "language": "ve.core@0.2",
    "profiles": ["norm-defaults@0", "norms@0", "relational-fol@0", "soft-norms@0"],
    "spec_revision": "ve-v0.2-expand2-2026-09-25",
    "vocabulary": {
        "sorts": {"assistant": {"description": "an AI assistant"},
                  "operator_instruction": {"description": "an instruction that an operator gives the assistant",
                                           "verbalisation": {"singular": "operator instruction",
                                                             "plural": "operator instructions"}}},
        "predicates": {
            "comply_required": {"arguments": ["assistant", "operator_instruction"],
                                "description": "the assistant must comply with the instruction",
                                "regulated": {"role": "obligation", "default": "deny",
                                              "act": "{0} comply with {1}", "permission": "comply_permitted"}},
            "comply_permitted": {"arguments": ["assistant", "operator_instruction"],
                                 "description": "the assistant may comply with the instruction",
                                 "regulated": {"role": "permission", "default": "allow",
                                               "act": "{0} comply with {1}"}},
            "demeaning": {"arguments": ["operator_instruction"],
                          "description": "the instruction directs the assistant to demean or disrespect the user "
                                         "in a way the user would not want",
                          "verbalisation": "{0} is demeaning", "negative_verbalisation": "{0} is not demeaning"}},
        "constants": {},
        "soft": {"parties": ["operator", "user"], "ranks": ["safety", "ethics", "guidelines", "helpfulness"],
                 "outranks": [["safety", "ethics"], ["ethics", "guidelines"], ["guidelines", "helpfulness"]],
                 "ties": [], "outranking": {"mode": "strict"}, "exception_decider": "the assistant"}}}
SOFT_TEXT = ("Rule 1. Every assistant should comply with each operator instruction. Rule 1 serves helpfulness.\n"
             "Rule 2. Every assistant should not comply with each operator instruction, if that operator "
             "instruction is demeaning. Rule 2 serves ethics.")


def compute_soft(item):
    ni = vekit.NormItem(copy.deepcopy(SOFT_ENV), SOFT_TEXT, soft=True)
    sit = {"complete": True, "domains": {"assistant": ["the_assistant"], "operator_instruction": ["i"]},
           "constants": {}, "relations": {"demeaning": [["i"]] if item["demeaning"] else []}}
    result = norm_result(ni, sit, item["predicate"], ["the_assistant", "i"],
                         extra_text=ni.soft_declarations())
    result["rendering"]["renderer"] += " + ve.surface.softnorms.render_declaration"
    return result


# --- risk ---------------------------------------------------------------------

RISK_RULES = (
    "Rule 1. Every action must not be performed, if there is a harm such that both that harm is severe and that "
    "action might lead to that harm.\n"
    "Rule 2. Every action must not be performed, if there is an agent such that that action is available to that "
    "agent and another action available to that agent has a less severe worst case than that action, unless the "
    "user has confirmed that action.\n"
    "Rule 3. Every action must not be performed, if that action allows task abandonment to happen.")


def risk_record(e1):
    lo, hi = e1
    return "\n".join([
        "Decision 17 of the build agent, log entry 41, 2026-09-29. Policy agent-ops.",
        "Available actions: running the job; running the job with the memory limit; asking the user; not running "
        "the job (inaction).",
        f"E1. The peak memory of the job is from {lo} GB through {hi} GB, including both bounds. "
        "[memory profiler 2.3; peak of the last 5 runs plus 20%; statistical; entry 38]",
        "E2. The free memory of the server during the job is from 8 GB through 10 GB, including both bounds. "
        "[server monitor; minimum over the last hour; observation; entry 40]",
        "S1. The memory limit equals 7 GB. [setting of \"running the job with the memory limit\"; entry 25]",
        "C1. Running the job cannot lead to a server outage unless the peak memory of the job is greater than the "
        "free memory of the server. [the build agent; assumption; entry 26]",
        "C2. Running the job with the memory limit cannot lead to a server outage unless the memory limit is "
        "greater than the free memory of the server. [the build agent; assumption: the limit is enforced by the "
        "kernel; entry 27]",
        "C3. Running the job with the memory limit leads to a job failure exactly when the peak memory of the job "
        "is greater than the memory limit. [the build agent; assumption; entry 28]",
        "C4. Running the job cannot lead to a job failure unless the peak memory of the job is greater than the "
        "free memory of the server. [the build agent; assumption; entry 29]",
        "T1. Asking the user leads to a task delay. T2. Not running the job leads to task abandonment. "
        "T3. Asking the user cannot lead to a server outage. T4. Not running the job cannot lead to a server "
        "outage. [the build agent; assumption; entries 30–33]",
        "T5. Running the job cannot lead to data loss. T6. Running the job with the memory limit cannot lead to "
        "data loss. T7. Asking the user cannot lead to data loss. T8. Not running the job cannot lead to data "
        "loss. [the platform team: jobs write only to scratch space; testimony; entries 34–37]"])


RISK_ACTIONS = {"running the job": "run", "running the job with the memory limit": "run_limited",
                "asking the user": "ask", "not running the job": "nothing"}
RISK_HARMS = {"a server outage": "server_outage", "a job failure": "job_failure", "data loss": "data_loss",
              "a task delay": "task_delay", "task abandonment": "task_abandonment"}


def risk_statement_checks(record_text):
    """Every C and T sentence is VE's registered record wording: it parses to
    one reading and renders back to itself (first letter lower-cased: the
    record labels are lower-case)."""
    from conformance.risk import agent_ops
    from ve.surface.risk import parse_wording, render_wording
    env = Environment(agent_ops())
    checks = []
    for sentence in re.findall(r"(?:^|(?<=\] )|(?<=\. ))(?:[CT]\d\. )([^.\[]+\.)", record_text, re.M):
        lowered = sentence[0].lower() + sentence[1:]
        reading = parse_wording(lowered, env, actions=RISK_ACTIONS, harms=RISK_HARMS, context="record")
        assert render_wording(reading, actions=RISK_ACTIONS, harms=RISK_HARMS) == lowered, sentence
        checks.append({"sentence": sentence, "reading": reading})
    return checks


def compute_risk(item):
    from conformance.risk import agent_ops, agent_ops_rules, log_l17, decision_17
    from ve.risk import run_case
    e1 = ("6", "12") if item["variant"] == "L17" else ("6", "7")
    env, norms = agent_ops(), agent_ops_rules()
    el = run_case({"id": "p", "kind": "risk-elaborate", "environment": env, "document": {"norms": norms}},
                  binary=RISK_BINARY)
    log = log_l17(e1=e1)
    dx = decision_17(log, (el["environment_id"], el["document_hash"]))
    cited = {c["id"] for c in dx["content"]["cites"]}
    res = run_case({"id": "d", "kind": "risk-decision", "environment": env, "document": {"norms": norms},
                    "decision": dx, "entries": [e for e in log.entries if e["id"] in cited]}, binary=RISK_BINARY)
    kind, alt, harm = item["ask"]
    might = sorted((m["alternative"], m["harm"]) for m in res["tables"]["might"])
    ruled = res["lines"]["assumed_ruled_out"]["cells"]
    if kind == "might":
        assert f"{alt}/{harm}" not in ruled, "the asked cell is only assumed ruled out"
        label = "MIGHT" if (alt, harm) in might else "CANNOT"
    else:
        status = next(s for s in res["statuses"] if s["alternative"] == alt)
        label = "PERMITTED" if status["permitted"] else "FORBIDDEN"
    record = risk_record(e1)
    verdict = {"status": res["status"], "statuses": res["statuses"], "might": might,
               "leads": sorted((m["alternative"], m["harm"]) for m in res["tables"]["leads"]),
               "assumed_ruled_out": ruled, "clear": res["clear"], "text": res.get("text"),
               "record_wordings_checked": len(risk_statement_checks(record))}
    text = RISK_RULES + "\n\n" + record
    legend = list(el["legend"]) + [line for line in res["legend"] if line not in el["legend"]]
    return dict(ve_text=text, legend=legend,
                rendering={"type": "risk rules and decision record",
                           "renderer": "docs/spec/risk.md 2.5 canonical IDE text (no Python renderer for "
                                       "decision records); C/T lines checked by ve.surface.risk "
                                       "parse_wording/render_wording; legend from the Lean risk route",
                           "explicit_notation": explicit_notation(text)},
                verdict=verdict, label=label, legend_dependent=False)


# --- prose with pronouns --------------------------------------------------------

def assist_env():
    env = Environment(read_json("examples/assist/environment.json"))
    return env, read_json("examples/assist/environment.english.json")


def compute_prose(item):
    env, voc = assist_env()
    formulas, shown = vekit.presentation(env, item["prose"], voc)
    assert " It " in " " + shown, f"the pronoun is not displayed: {shown}"
    conclusion = vekit.parse_ve(env, item["conclusion"], voc)[0]
    ent = vekit.entail3(env, formulas, conclusion)
    label = {"FOLLOWS": "YES", "CONTRADICTED": "NO", "NEITHER": "DNS"}[ent["label"]]
    names = set(env.predicates) | set(env.sorts) | set(env.constants)
    used = vekit.symbols_in([vekit.ast_data(f) for f in formulas], names)
    used |= {s_ for p in used if p in env.predicates for s_ in env.predicates[p].arguments}
    used |= {env.constants[c].sort for c in used if c in env.constants}
    return dict(ve_text=shown, legend=vekit.legend_lines(env, used, vocabulary=voc),
                rendering={"type": "natural (ve.prose@1)",
                           "renderer": "ve.natural.parse_presentation + render_presentation",
                           "explicit_notation": explicit_notation(shown)},
                verdict={"premises": [str(f) for f in formulas], "conclusion": str(conclusion), **ent},
                label=label, legend_dependent=False)


# --- speech acts --------------------------------------------------------------

def speech_env(addressee):
    from tests.test_speech_acts_lean import F0
    env = F0(addressee=("user", "alice") if addressee else None)
    words = {"reviewed": "{0} is reviewed", "cat": "{0} is a cat", "animal": "{0} is an animal"}
    for p, v in words.items():
        env["vocabulary"]["predicates"][p]["verbalisation"] = v
    return env


def speech_file(item, env, units, queries):
    lines = [l + "\n" for l in item["lines"]]
    pos = [0]
    for l in lines:
        pos.append(pos[-1] + len(l.encode()))
    for i, u in enumerate(units):
        u["span"] = pos[i:i + 2]
    meta = {"format": "ve-document@2", "environment": env, "units": units, "queries": queries}
    path = HERE / "sources" / item["id"] / "speech.ve.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("---\n" + json.dumps(meta, indent=1) + "\n---\n" + "".join(lines))
    return path


def speech_legend(env, used_predicates, addressee):
    from ve.speech_english import legend
    keep = []
    for line in legend(env).splitlines():
        if line.startswith("This document is task"):
            keep.append(line)
        elif line.startswith("In this task, you are") and addressee:
            keep.append(line)
        elif line.startswith("By default,") and any(w in line for w in used_predicates):
            keep.append(line)
    return keep


def compute_speech(item):
    from tests.test_speech_acts_lean import unit, command
    from ve.speech_acts import SpeechDocument
    from ve.ast import formula_from_data
    from ve.entailment import prove_entailment
    from ve.search import find_countermodel
    from ve.entailment import check_entailment_certificate
    from ve.speech_english import parse_speech
    if item["kind"] == "speech-follows":
        raw = speech_env(False)
        units = [unit("u1", 0, "asserted", {"ast": item["premises"][0]}),
                 unit("u2", 0, "asserted", {"ast": item["premises"][1]}),
                 unit("u3", 0, "question", {"question": {"mode": "follows", "query": "q1"}})]
        queries = [{"id": "q1", "premises": ["u1", "u2"], "target": {"ast": item["target"]}}]
        doc = SpeechDocument(Environment(raw), units, queries)
        # The lines are VE's natural view of the asserted ASTs and of the
        # target inside the registered follows-question wording; each line is
        # read back by VE's speech wording parser.
        shown = vekit.natural_view(doc.env, [formula_from_data(doc.env, a) for a in
                                             (*item["premises"], item["target"])])
        sentences = [s_["text"] for s_ in shown["sentences"]]
        target_text = sentences[2][0].lower() + sentences[2][1:]
        lines = [sentences[0] + ".", sentences[1] + ".",
                 f"Does it follow from these premises that {target_text}?"]
        for line, ast_ in zip(lines[:2], item["premises"]):
            assert vekit.parse_ve(doc.env, line) == [formula_from_data(doc.env, ast_)], line
        assert parse_speech(doc.env, lines[2], doc.env.speech_acts, query="q1")[1] == "question"
        item = {**item, "lines": lines, "forms": [s_["form"] for s_ in shown["sentences"]]}
        premises, target = doc._caller_premises("q1"), doc.queries["q1"].target
        proof = prove_entailment(doc.env, premises, target, max_steps=20_000)
        if proof.status == "Found":
            checked = doc.check_consequence_certificate("q1", proof.certificate)
            label = "FOLLOWS"
            verdict = {"judgment": "follows", "certificate": "checked by check_consequence_certificate",
                       "check": str(checked)[:300]}
        else:
            cm = find_countermodel(doc.env, list(premises), target, max_domain_size=2)
            assert cm.status == "Found"
            label = "GAP"
            verdict = {"judgment": "gap", "proof": proof.status, "countermodel": vekit._model_json(cm.model)}
        used = ["cat", "animal"]
        legend = speech_legend(doc.env, [], False) + vekit.legend_lines(
            doc.env, {"thing", "cat", "animal", "tom"})
    else:
        raw = speech_env(True)
        doc0 = SpeechDocument(Environment(raw), [], [])
        assert parse_speech(doc0.env, item["lines"][1], doc0.env.speech_acts)[1] == "instruction"
        units = [unit("u0", 0, "binding", {"binding": {"you": "alice"}}),
                 unit("u1", 0, "instruction", command("require", "click_required", ["check"]))]
        doc = SpeechDocument(Environment(raw), units, [])
        from tests.test_speech_acts_lean import model
        completed = doc.complete_model(model())
        table = completed.to_dict()["relations"]["click_required"]
        label = "REQUIRED" if ["alice", "check"] in table else "NOT-REQUIRED"
        verdict = {"rules": [r.to_dict() for r in doc.policy.rules], "click_required": table}
        legend = speech_legend(doc.env, ["click a control"], True) + vekit.legend_lines(
            doc.env, {"user", "control", "alice", "check"})
    path = speech_file(item, raw, units, queries if item["kind"] == "speech-follows" else [])
    cli = vekit.run_cli(["speech-acts", str(path.relative_to(REPO))])
    verdict["speech_acts_cli_status"] = cli.get("status")
    text = "\n".join(item["lines"])
    kind = "/".join(sorted(set(item.get("forms", ["speech-act wording"]))))
    return dict(ve_text=text, legend=legend,
                rendering={"type": kind,
                           "renderer": "ve.printer.natural_document for asserted lines; registered speech "
                                       "wordings read back by ve.speech_english.parse_speech; `python -m ve "
                                       "speech-acts` accepts the ve-document@2 file",
                           "explicit_notation": explicit_notation(text)},
                verdict=verdict, label=label, legend_dependent=False)


# --- 14th Amendment -------------------------------------------------------------

FOURTEENTH = "usecases/us-constitution-14th-s1/"
EXTRA_CONSTANTS = {
    "ann": ("person", "Ann, a person", "Ann"), "ben": ("person", "Ben, a person", "Ben"),
    "carl": ("person", "Carl, a person", "Carl"), "ohio": ("state", "the State of Ohio", "Ohio")}


def fourteenth_env():
    raw = read_json(FOURTEENTH + "environment.json")
    for name, (sort, description, _) in EXTRA_CONSTANTS.items():
        raw["vocabulary"]["constants"][name] = {"sort": sort, "description": description}
    env = Environment(raw)
    voc = read_json(FOURTEENTH + "environment.english.json")
    # The reviewed display overlay, re-bound to the extended environment, with
    # display names for the added constants.
    voc["environment_id"] = env.environment_id
    voc.setdefault("constants", {})
    for name, (_, _, shown) in EXTRA_CONSTANTS.items():
        voc["constants"][name] = {"verbalisation": shown}
    return env, voc


def source_clauses():
    text = (REPO / FOURTEENTH / "source.md").read_text()
    return re.findall(r"^\d\. \*\*[^*]+\*\* — \"(.*)\"$", text, re.M)


def compute_entail(item):
    from ve.parser import parse
    env, voc = fourteenth_env()
    claims = parse(env, (REPO / FOURTEENTH / "claims.ve").read_text()).formulas
    premises_shown = [claims[i] for i in item["claims"]]
    view = vekit.natural_view(env, premises_shown, voc)
    facts = vekit.parse_ve(env, item["facts"], voc)
    conclusion = vekit.parse_ve(env, item["conclusion"], voc)[0]
    ent = vekit.entail3(env, premises_shown + facts, conclusion)
    label = {"FOLLOWS": "YES", "CONTRADICTED": "NO", "NEITHER": "DNS"}[ent["label"]]
    used = vekit.symbols_in([vekit.ast_data(f) for f in premises_shown],
                            set(env.predicates) | set(env.sorts) | set(env.constants))
    used |= {s for p in used if p in env.predicates for s in env.predicates[p].arguments}
    forms = sorted({s["form"] for s in view["sentences"]})
    return dict(ve_text=view["text"], legend=vekit.legend_lines(env, used, vocabulary=voc),
                rendering={"type": "/".join(forms), "renderer": view["renderer"],
                           "sentences": view["sentences"], "explicit_notation": explicit_notation(view["text"])},
                verdict={"facts_as_parsed": [str(f) for f in facts], "conclusion": str(conclusion), **ent},
                label=label, legend_dependent=False)


# --- rights -------------------------------------------------------------------

RIGHTS_ENV = {
    "language": "ve.core@0.2",
    "profiles": sorted(["relational-fol@0", "norms@0", "soft-norms@0", "rights@0", "norm-defaults@0"]),
    "spec_revision": "ve-v0.2-expand2-2026-09-25",
    "vocabulary": {
        "sorts": {"state": {"description": "a state"}, "person": {"description": "a human being"}},
        "predicates": {
            "deprive_life_permitted": {"arguments": ["state", "person"],
                                       "description": "the state may deprive the person of life",
                                       "regulated": {"role": "permission", "default": "unspecified",
                                                     "act": "{0} deprive {1} of life"}},
            "protect_life_required": {"arguments": ["state", "person"],
                                      "description": "the state must protect the person against deprivation of life",
                                      "regulated": {"role": "obligation", "default": "unspecified",
                                                    "act": "{0} protect {1} against deprivation of life"}}},
        "constants": {"texas": {"sort": "state", "description": "the State of Texas", "verbalisation": "Texas"},
                      "ann": {"sort": "person", "description": "Ann, a person", "verbalisation": "Ann"}},
        "rights": {"holders": ["person"], "bearers": ["state"], "protected": [], "alters": {}}}}
RIGHT_CONTENT = {"right": {"name": "life", "holder": "person", "guard": ["top"], "lines": [
    {"kind": "claim", "holder_slot": None, "cites": {},
     "norm": {"name": "no-deprivation", "predicate": "deprive_life_permitted", "sign": False,
              "guard": ["top"], "unless": [], "over": []}}]}}


def compute_rights(item):
    from ve import norm_defaults as nd
    from ve.norm_defaults_english import legend, status_sentence
    from ve.rights import RightsDocument, RightsEnvironment
    from ve.surface.rights import render_unit
    env = RightsEnvironment(copy.deepcopy(RIGHTS_ENV))
    units = [{"source_units": ["u1"]}, RIGHT_CONTENT]
    doc = nd.UnspecifiedRightsDocument(env, units)
    placeholder = RightsDocument(RightsEnvironment(vekit.without_norm_defaults(RIGHTS_ENV)), units)
    text = render_unit(placeholder, RIGHT_CONTENT)
    sit = vekit.complete_situation(doc.situation_environment(), {
        "complete": True, "domains": {"state": ["texas"], "person": ["ann"]},
        "constants": {"texas": "texas", "ann": "ann"}, "relations": {}})
    s = doc.situation(sit)
    status = doc.status(s, item["predicate"], ("texas", "ann"))
    verdict = {"point": [item["predicate"], ["texas", "ann"]], "status": status.status, "value": status.value,
               "evidence": str(status.evidence), "sentence": status_sentence(doc, s, status)}
    role = env.predicates[item["predicate"]].regulated.role
    label = vekit.norm_label(verdict, role)
    label = "DNS" if label == "UNDECIDED" else label
    plain_raw = copy.deepcopy(RIGHTS_ENV)
    plain_raw["vocabulary"].pop("rights")
    plain_raw["vocabulary"]["predicates"] = {}
    plain_raw["vocabulary"]["constants"] = {}
    plain_raw["profiles"] = ["relational-fol@0"]
    plain = Environment(plain_raw)
    from ve.norm_english import default_sentence
    used = vekit.symbols_in(RIGHT_CONTENT, set(env.predicates))
    completions = [line for line in legend(env)
                   if line in {default_sentence(env, p) for p in used}]
    return dict(ve_text=text, legend=completions + vekit.legend_lines(plain, None),
                rendering={"type": "rights unit surface", "renderer": "ve.surface.rights.render_unit",
                           "explicit_notation": explicit_notation(text)},
                verdict=verdict, label=label, legend_dependent="(by default)" in verdict["sentence"])


COMPUTE = {"agent-policy": compute_agent_policy}
KINDS = {"csam": compute_csam, "asimov": compute_asimov, "fsf": compute_fsf, "soft": compute_soft,
         "risk": compute_risk, "prose": compute_prose, "speech-follows": compute_speech,
         "speech-command": compute_speech, "entail": compute_entail, "rights": compute_rights}


def compute(item):
    fn = KINDS.get(item.get("kind")) or COMPUTE[item["family"]]
    return fn(item)


def item_by_id(item_id):
    return next(i for i in ITEMS if i["id"] == item_id)


# --- prompts ------------------------------------------------------------------

READING_HEAD = "Read the text below and answer the question that follows it."
READING_TAIL = ("Answer with the letter of one option and a one-sentence reason, in exactly this form:\n"
                "ANSWER: <letter>\nREASON: <one sentence>")


def options_for(item):
    """Non-DNS options in a fixed per-item shuffled order, then DNS last."""
    opts = list(item["options"])
    seed = int(hashlib.sha256(item["id"].encode()).hexdigest(), 16)
    order = sorted(range(len(opts)), key=lambda i: (seed >> (8 * i)) & 0xFF)
    shuffled = [opts[i] for i in order] + [DNS]
    return [{"letter": LETTERS[i], "text": t, "label": l} for i, (l, t) in enumerate(shuffled)]


def reading_prompt(text, legend, question, options):
    parts = [READING_HEAD, "", "=== TEXT ===", text.strip()]
    if legend is not None:
        parts += ["", "=== LEGEND (explanations the editor shows for the words in the text) ===", *legend]
    parts += ["", "=== QUESTION ===", question, *[f"{o['letter']}. {o['text']}" for o in options], "",
              READING_TAIL]
    return "\n".join(parts) + "\n"


def build_reading():
    out = []
    for item in ITEMS:
        r = compute(item)
        options = options_for(item)
        key = [o for o in options if o["label"] == r["label"]]
        assert len(key) == 1, (item["id"], r["label"], [o["label"] for o in options])
        en = item.get("en")
        if item.get("en_from_headers"):
            en = fsf_en(item)
        if item.get("en_clauses") is not None:
            clauses = source_clauses()
            en = "\n\n".join(clauses[i] for i in item["en_clauses"])
        notation = r["rendering"]["explicit_notation"]
        # VE's own classification: the audited view's `explicit form`, or the
        # strict fallback wording (`classified as "…"`) that VE uses for a
        # predicate without an admitted English wording. Clause scaffolding
        # and list markers are natural-view output and stay in `notation`.
        r["rendering"]["form"] = ("explicit form" if r["rendering"]["type"] == "explicit form" or
                                  "explicit-form fallback wording" in notation else "natural")
        record = {
            "id": item["id"], "family": item["family"], "constructs": item["constructs"],
            "question": item["question"], "options": options,
            "key": key[0]["letter"], "key_label": r["label"],
            "ve_text": r["ve_text"], "legend": r["legend"], "rendering": r["rendering"],
            "legend_dependent": r["legend_dependent"],
            "en_text": en, "en_source": item.get("en_source") if en else None,
            "en_note": None if en else item.get("en_note"),
            "conditions": ["VE-L", "VE-C"] + (["EN"] if en else []),
            "world_knowledge": item.get("world_knowledge"),
            "ve_command": f"uv run python experiments/readability-sonnet/ve_key.py {item['id']}",
            "ve_output": json.dumps({"label": r["label"], "verdict": r["verdict"]}, sort_keys=True, default=str),
        }
        out.append(record)
        ctx = HERE / "contexts" / item["id"]
        ctx.mkdir(parents=True, exist_ok=True)
        (ctx / "VE-L.txt").write_text(reading_prompt(r["ve_text"], r["legend"], item["question"], options))
        (ctx / "VE-C.txt").write_text(reading_prompt(r["ve_text"], None, item["question"], options))
        if en:
            (ctx / "EN.txt").write_text(reading_prompt(en, None, item["question"], options))
        print(item["id"], r["label"], key[0]["letter"], flush=True)
    return out


def record_commands(items):
    """Run each recorded `ve_command` and store its literal stdout; it must be
    the verdict computed during the build."""
    import subprocess
    done = subprocess.run([sys.executable, str(HERE / "ve_key.py"), *[i["id"] for i in items]],
                          cwd=REPO, capture_output=True, text=True, check=True)
    lines = done.stdout.splitlines()
    assert len(lines) == len(items), done.stderr[-2000:]
    for item, line in zip(items, lines):
        assert json.loads(line) == json.loads(item["ve_output"]), item["id"]
        item["ve_output"] = line


def main(argv):
    what = argv[1:] or ["reading", "writing"]
    if "reading" in what:
        items = build_reading()
        record_commands(items)
        (HERE / "items.json").write_text(json.dumps({"format": "ve-readability-items@1", "items": items},
                                                    indent=1, ensure_ascii=False) + "\n")
    if "writing" in what:
        import writing_spec
        writing_spec.build(HERE)


if __name__ == "__main__":
    main(sys.argv)
