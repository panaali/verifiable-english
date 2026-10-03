"""The 15 writing tasks, their environments, gold meanings and contexts.

Fixed before any model session. A task gives a plain-English intention, the
vocabulary the editor shows (VE legend lines), at most five example VE
sentences (one fixed set per family, from a different vocabulary or not
equivalent to any gold) and asks for one VE sentence. `score.py check W01
"..."` scores an attempt mechanically (see vekit.score_*).
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import vekit  # noqa: E402
from vekit import REPO, Environment  # noqa: E402

LANG = {"language": "ve.core@0.2", "spec_revision": "ve-v0.2-expand2-2026-09-25"}


def read_json(rel):
    return json.loads((REPO / rel).read_text())


# --- family N: rules (norms@0) -----------------------------------------------

def regulated(role, default, act):
    return {"role": role, "default": default, "act": act}


def norm_env(defaults):
    """An agent-tools vocabulary in the style of usecases/agent-policy, with
    acts on (agent, file) and (agent, host). `defaults` sets each regulated
    predicate's completion for the task."""
    preds = {
        "resides_in": {"arguments": ["file", "directory"], "description": "the file resides in the directory, as "
                                                                          "resolved by the path resolver",
                       "verbalisation": "{0} resides in {1}", "negative_verbalisation": "{0} does not reside in {1}"},
        "confidential": {"arguments": ["file"], "description": "the file is on the credential path list",
                         "verbalisation": "{0} is confidential", "negative_verbalisation": "{0} is not confidential"},
        "deletes": {"arguments": ["agent", "file"], "description": "the agent deleted the file, as recorded by the tools",
                    "verbalisation": "{0} deletes {1}", "negative_verbalisation": "{0} does not delete {1}"},
        "allowlisted": {"arguments": ["host"], "description": "the host is on the network allowlist",
                        "verbalisation": "{0} is allowlisted", "negative_verbalisation": "{0} is not allowlisted"},
        "approved": {"arguments": ["host"], "description": "the user approved the host in a dialog",
                     "verbalisation": "{0} is approved", "negative_verbalisation": "{0} is not approved"},
        "delete_permitted": {"arguments": ["agent", "file"], "description": "the agent may delete the file",
                             "regulated": regulated("permission", defaults.get("delete", "deny"), "{0} delete {1}")},
        "read_permitted": {"arguments": ["agent", "file"], "description": "the agent may read the file",
                           "regulated": regulated("permission", defaults.get("read", "allow"), "{0} read {1}")},
        "contact_permitted": {"arguments": ["agent", "host"], "description": "the agent may contact the host",
                              "regulated": regulated("permission", defaults.get("contact", "allow"),
                                                     "{0} contact {1}")},
        "report_required": {"arguments": ["agent", "file"],
                            "description": "the agent must report the file to the user",
                            "regulated": regulated("obligation", defaults.get("report", "deny"),
                                                   "{0} report {1} to the user")},
    }
    return {**LANG, "profiles": ["norms@0", "relational-fol@0"],
            "vocabulary": {"sorts": {"agent": {"description": "an AI agent that uses tools"},
                                     "file": {"description": "a file path, as resolved by the path resolver"},
                                     "host": {"description": "a network host"},
                                     "directory": {"description": "a directory, such as the agent's workspace"}},
                           "predicates": preds,
                           "constants": {"workspace": {"sort": "directory",
                                                       "description": "the workspace directory of the agent's task"}}}}


NORM_FRESH = {"agent": {"w_agent": {"sort": "agent", "description": "scoring constant"}},
              "file": {"w_file": {"sort": "file", "description": "scoring constant"}},
              "host": {"w_host": {"sort": "host", "description": "scoring constant"}}}


def fresh_for(env_raw, predicate):
    out = {}
    for sort in env_raw["vocabulary"]["predicates"][predicate]["arguments"]:
        out.update(NORM_FRESH[sort])
    return out


WARD_ENV = {**LANG, "profiles": ["norms@0", "relational-fol@0"], "vocabulary": {
    "sorts": {"doctor": {"description": "a doctor on the hospital staff"},
              "patient": {"description": "a patient in the hospital"}},
    "predicates": {
        "infectious": {"arguments": ["doctor"], "description": "{0} is infectious, as recorded by occupational health",
                       "verbalisation": "{0} is infectious", "negative_verbalisation": "{0} is not infectious"},
        "rostered": {"arguments": ["doctor"], "description": "{0} is rostered, as recorded on the duty roster",
                     "verbalisation": "{0} is rostered", "negative_verbalisation": "{0} is not rostered"},
        "admits": {"arguments": ["doctor", "patient"], "description": "{0} admits {1}, as recorded at admission",
                   "verbalisation": "{0} admits {1}", "negative_verbalisation": "{0} does not admit {1}"},
        "discharged": {"arguments": ["patient"], "description": "{0} is discharged, as recorded at discharge",
                       "verbalisation": "{0} is discharged", "negative_verbalisation": "{0} is not discharged"},
        "enter_permitted": {"arguments": ["doctor"], "description": "the doctor may enter the ward",
                            "regulated": regulated("permission", "deny", "{0} enter the ward")},
        "treat_required": {"arguments": ["doctor", "patient"], "description": "the doctor must treat the patient",
                           "regulated": regulated("obligation", "deny", "{0} treat {1}")}},
    "constants": {}}}
NORM_EXAMPLES = [
    "Rule 1. Every doctor may enter the ward.",
    "Rule 2 (exception to rule 1). Every doctor must not enter the ward, if that doctor is infectious, unless that "
    "doctor is rostered.",
    "Rule 1. Every doctor must treat each patient, if that doctor admits that patient.",
    "Rule 2 (exception to rule 1). Every doctor need not treat each patient, if that patient is discharged.",
]

# --- family R: risk record statements (risk@0, docs/spec/risk.md 2.5) ----------

RISK_EXAMPLES = [
    "Running the job cannot lead to a server outage unless the peak memory of the job is greater than the free "
    "memory of the server.",
    "Running the job with the memory limit leads to a job failure exactly when the peak memory of the job is greater "
    "than the memory limit.",
    "Asking the user leads to a task delay.",
    "Not running the job cannot lead to a server outage.",
]
RISK_QUANTITIES = ["the peak memory of the job", "the free memory of the server", "the memory limit"]

# --- family F: formulas (relational-fol@0) -----------------------------------------

FORMULA_EXAMPLE_ENV = "usecases/agent-policy/environment.deny-neednot.json"
FORMULA_EXAMPLES_STRICT = [
    'for every file x0, (if (x0 is confidential), then (x0 is tracked)).',
    'there exists file x0, (x0 resides_in @workspace).',
    'not (there exists action x0, (x0 is privileged)).',
    'for every action x0, (if (there exists file x1, (x0 deletes x1)), then (x0 is reported)).',
    'for every action x0, (if (x0 is confirmed), then ((x0 is reported) or (x0 is readonly))).',
]

TASKS = [
    # ---- rules ----
    dict(id="W01", family="rules", constructs=["permission", "declared defaults (deny/allow)"],
         intention="The agent may delete files only inside the workspace.",
         defaults={"delete": "deny"}, predicate="delete_permitted",
         gold="Rule 1. Every agent may delete each file, if that file resides in workspace."),
    dict(id="W02", family="rules", constructs=["prohibition"],
         intention="The agent must not read confidential files.",
         defaults={"read": "allow"}, predicate="read_permitted",
         gold="Rule 1. Every agent must not read each file, if that file is confidential."),
    dict(id="W03", family="rules", constructs=["prohibition", "exceptions/unless"],
         intention="The agent must not contact a host that is not on the allowlist, unless the user has approved "
                   "that host.",
         defaults={"contact": "allow"}, predicate="contact_permitted",
         gold="Rule 1. Every agent must not contact each host, if that host is not allowlisted, unless that host "
              "is approved."),
    dict(id="W04", family="rules", constructs=["obligation"],
         intention="Whenever the agent deletes a file, it must report that file to the user.",
         defaults={"report": "deny"}, predicate="report_required",
         gold="Rule 1. Every agent must report each file to the user, if that agent deletes that file."),
    dict(id="W05", family="rules", constructs=["precedence", "prohibition"],
         intention="Add a second rule to the existing rule: even inside the workspace, the agent must not read "
                   "confidential files. The new rule should win over rule 1.",
         defaults={"read": "deny"}, predicate="read_permitted",
         context_rules="Rule 1. Every agent may read each file, if that file resides in workspace.",
         gold="Rule 1. Every agent may read each file, if that file resides in workspace.\n"
              "Rule 2 (exception to rule 1). Every agent must not read each file, if that file is confidential."),
    # ---- risk ----
    dict(id="W06", family="risk", constructs=["might/cannot risk"],
         intention="Asking the user can never cause data loss.",
         gold_reading={"form": "cannot", "action": "ask", "harm": "data_loss"}),
    dict(id="W07", family="risk", constructs=["might/cannot risk", "conditions"],
         intention="If the job's peak memory exceeds the free memory of the server, running the job causes a "
                   "server outage.",
         gold_reading={"form": "sufficient", "action": "run", "harm": "server_outage",
                       "condition_text": "the peak memory of the job is greater than the free memory of the server"}),
    # ---- formulas ----
    dict(id="W08", family="formulas", constructs=["universal", "relative clause", "conjunction"],
         env="usecases/us-constitution-14th-s1/environment.json",
         vocabulary="usecases/us-constitution-14th-s1/environment.english.json",
         intention="Anyone who was born in the United States and is subject to its jurisdiction is a citizen of "
                   "the United States.",
         gold="for every person x0, (if ((x0 is born_in_us) and (x0 is subject_to_us_jurisdiction)), then "
              "(x0 is us_citizen))."),
    dict(id="W09", family="formulas", constructs=["universal", "binary relation", "negation"],
         env="usecases/us-constitution-14th-s1/environment.json",
         vocabulary="usecases/us-constitution-14th-s1/environment.english.json",
         intention="No state denies the equal protection of the laws to a person who is within its jurisdiction.",
         gold="for every state x0, (for every person x1, (if (x1 within_jurisdiction_of x0), then "
              "(not (x0 denies_equal_protection x1))))."),
    dict(id="W10", family="formulas", constructs=["universal", "relative clause"],
         env="usecases/birthright-citizenship-debate/environment.json",
         vocabulary="usecases/birthright-citizenship-debate/environment.english.json",
         intention="Everyone who has a noncitizen parent domiciled in the United States is subject to US "
                   "jurisdiction.",
         gold="for every person x0, (if (x0 is has_noncitizen_domiciled_parent), then (x0 is subject_to_jurisdiction))."),
    dict(id="W11", family="formulas", constructs=["universal", "named constant", "negation"],
         env="usecases/claude-constitution-excerpt/environment.json",
         vocabulary="usecases/claude-constitution-excerpt/environment.english.json",
         intention="Claude does not undermine any appropriate mechanism.",
         gold="for every mechanism x0, (if (x0 is appropriate), then (not (@claude undermines x0)))."),
    dict(id="W12", family="formulas", constructs=["negated existential"],
         env="examples/environment.json",
         intention="There is no deployed service that is not reviewed.",
         gold="not (there exists service x0, ((x0 is deployed) and (not (x0 is reviewed))))."),
    dict(id="W13", family="formulas", constructs=["existential", "quantifier scope"],
         env="examples/environment.json",
         intention="A single person owns all the deployed services.",
         gold="there exists person x0, (for every service x1, (if (x1 is deployed), then (x0 owns x1)))."),
    dict(id="W14", family="formulas", constructs=["universal", "disjunction"],
         env="examples/environment.json",
         intention="Every service is deployed or reviewed, or both.",
         gold="for every service x0, ((x0 is deployed) or (x0 is reviewed))."),
    dict(id="W15", family="formulas", constructs=["universal", "named constant", "relative clause"],
         env="usecases/claude-constitution-excerpt/environment.json",
         vocabulary="usecases/claude-constitution-excerpt/environment.english.json",
         intention="Claude follows every relevant guideline.",
         gold="for every guideline x0, (if (x0 is relevant), then (@claude follows x0))."),
]


# Dropped by the pre-run check (manage-agents/readability-check.final.md): the
# condition is compared as text, so no paraphrase can score correct and no wrong
# condition can count as silent-wrong; the "Comparison:" legend line is the
# builder's, not VE's. The definition stays for the record; no context is built.
DROPPED = {"W07"}


def task_by_id(task_id):
    return next(t for t in TASKS if t["id"] == task_id)


# --- environments and scoring ---------------------------------------------------

def risk_env():
    from conformance.risk import agent_ops
    return agent_ops()


def task_env(task):
    """(raw environment, English vocabulary overlay or None) for scoring."""
    if task["family"] == "rules":
        return norm_env(task["defaults"]), None
    if task["family"] == "risk":
        return risk_env(), None
    raw = read_json(task["env"])
    voc = read_json(task["vocabulary"]) if task.get("vocabulary") else None
    return raw, voc


def gold_formula(task):
    from ve.parser import parse
    raw, _ = task_env(task)
    return parse(Environment(raw), task["gold"] + "\n").formulas[0]


def score(task, sentence):
    """The mechanical outcome of one attempt and the message VE shows for it."""
    from build import RISK_ACTIONS, RISK_HARMS
    raw, voc = task_env(task)
    if task["family"] == "rules":
        return vekit.score_norm(raw, sentence, task["gold"], task["predicate"], fresh_for(raw, task["predicate"]),
                                task.get("context_rules"))
    if task["family"] == "risk":
        text = sentence.strip()
        # The record labels are lower-case and VE's record parser compares them
        # exactly; an editor lower-cases a capitalised first letter, as
        # build.risk_statement_checks does for the displayed record.
        if text[:1].isupper() and text[:1].lower() + text[1:2] != text[:2] and not text.startswith("If "):
            text = text[0].lower() + text[1:]
        return vekit.score_risk(raw, text, task["gold_reading"], RISK_ACTIONS, RISK_HARMS)
    return vekit.score_formula(Environment(raw), sentence, gold_formula(task), voc)


# --- contexts ---------------------------------------------------------------------

WRITING_HEAD = ("You are writing in Verifiable English (VE), a controlled form of English that a checker reads. "
                "Write one VE sentence that says what you want to say.")
WRITING_TAIL = ("Answer with your sentence and a one-sentence reason, in exactly this form:\n"
                "SENTENCE: <your VE sentence>\nREASON: <one sentence>")
RETRY = ("VE's response to your sentence:\n{ve_message}\n\n"
         "Write the sentence again (attempt {attempt} of 3). You may change it or keep it.\n" + WRITING_TAIL)


def examples(task):
    if task["family"] == "rules":
        env = Environment(WARD_ENV)
        from ve.norm_english import parse_english
        # Examples 1-2 and 3-4 are two two-rule documents.
        for first, second in (NORM_EXAMPLES[0:2], NORM_EXAMPLES[2:4]):
            parse_english(env, first + "\n" + second)
        return list(NORM_EXAMPLES)
    if task["family"] == "risk":
        from build import RISK_ACTIONS, RISK_HARMS
        from ve.surface.risk import parse_wording
        env = Environment(risk_env())
        for text in RISK_EXAMPLES:
            parse_wording(text[0].lower() + text[1:], env, actions=RISK_ACTIONS, harms=RISK_HARMS,
                          context="record")
        return list(RISK_EXAMPLES)
    from ve.parser import parse
    raw = read_json(FORMULA_EXAMPLE_ENV)
    from ve.norms import NormDocument
    base = NormDocument(Environment(raw), ()).base_environment()
    formulas = [parse(base, s + "\n").formulas[0] for s in FORMULA_EXAMPLES_STRICT]
    view = vekit.natural_view(base, formulas)
    return [s["text"] + "." for s in view["sentences"]]


def legend(task):
    raw, voc = task_env(task)
    if task["family"] == "rules":
        from ve.norm_english import default_sentence
        env = Environment(raw)
        lines = [default_sentence(env, p) for p, d in env.predicates.items() if d.regulated is not None]
        return lines + vekit.legend_lines(env, None)
    if task["family"] == "risk":
        from build import RISK_ACTIONS, RISK_HARMS, RISK_BINARY
        from conformance.risk import agent_ops_rules
        from ve.risk import run_case
        el = run_case({"id": "p", "kind": "risk-elaborate", "environment": raw,
                       "document": {"norms": agent_ops_rules()}}, binary=RISK_BINARY)
        lines = ["Actions: " + "; ".join(RISK_ACTIONS), "Harms: " + "; ".join(RISK_HARMS),
                 "Quantities: " + "; ".join(RISK_QUANTITIES),
                 "Comparison: <quantity> is greater than <quantity>"]
        return lines + list(el["legend"])
    return vekit.legend_lines(Environment(raw), None, vocabulary=voc)


def prompt(task):
    parts = [WRITING_HEAD, "", "=== WHAT YOU WANT TO SAY ===", task["intention"]]
    if task.get("context_rules"):
        parts += ["", "=== THE DOCUMENT SO FAR ===", task["context_rules"]]
    parts += ["", "=== WORDS AVAILABLE (the editor's legend) ===", *legend(task),
              "", "=== EXAMPLE VE SENTENCES ===", *[f"{i}. {e}" for i, e in enumerate(examples(task), 1)],
              "", WRITING_TAIL]
    return "\n".join(parts) + "\n"


def build(out_dir):
    records = []
    for task in TASKS:
        if task["id"] in DROPPED:
            continue
        gold_check = score(task, gold_surface(task))
        assert gold_check["outcome"] == "correct", (task["id"], gold_check)
        ex = examples(task)
        for e in ex:
            # No example is itself a correct answer to the task.
            if task["family"] == "rules" or task["family"] == "risk":
                continue
            try:
                assert score(task, e)["outcome"] != "correct", (task["id"], e)
            except Exception:
                pass
        ctx = out_dir / "contexts" / task["id"]
        ctx.mkdir(parents=True, exist_ok=True)
        (ctx / "attempt1.txt").write_text(prompt(task))
        (ctx / "retry.txt").write_text(RETRY + "\n")
        records.append({
            "id": task["id"], "family": task["family"], "constructs": task["constructs"],
            "intention": task["intention"], "context_rules": task.get("context_rules"),
            "environment": task.get("env") or ("norm_env (writing_spec.py) with defaults " +
                                               json.dumps(task.get("defaults")) if task["family"] == "rules"
                                               else "conformance.risk.agent_ops (risk.md 8.1 agent-ops)"),
            "vocabulary_overlay": task.get("vocabulary"),
            "gold": task.get("gold") or task.get("gold_reading"),
            "gold_surface": gold_surface(task),
            "gold_check": gold_check,
            "equivalence_method": {
                "rules": "ve.equivalence.compare on the completed outcome of the regulated predicate at fresh "
                         "constants, under the declared default, plus ve.norms.check_conflict CONFLICT-FREE",
                "risk": "identical registered reading from ve.surface.risk.parse_wording (form, action, harm; "
                        "condition text compared after whitespace normalisation: no Python decoder exists)",
                "formulas": "ve.equivalence.compare (two replayed certificates for EQUIVALENT)"}[task["family"]],
            "examples": ex, "legend": legend(task),
            "score_command": f'uv run python experiments/readability-sonnet/score.py check {task["id"]} "<sentence>"',
        })
        print(task["id"], gold_check["outcome"], flush=True)
    (out_dir / "writing.json").write_text(json.dumps({"format": "ve-readability-writing@1", "tasks": records},
                                                     indent=1, ensure_ascii=False) + "\n")


def gold_surface(task):
    """A VE sentence with the gold meaning, as VE writes it (used only to check
    that the scorer accepts the gold; never shown to a session)."""
    if task["family"] == "rules":
        text = task["gold"]
        if task.get("context_rules"):
            text = text[len(task["context_rules"]) + 1:]
        return text
    if task["family"] == "risk":
        from build import RISK_ACTIONS, RISK_HARMS
        from ve.surface.risk import render_wording
        return render_wording(task["gold_reading"], actions=RISK_ACTIONS, harms=RISK_HARMS)
    raw, voc = task_env(task)
    view = vekit.natural_view(Environment(raw), [gold_formula(task)], voc)
    return view["sentences"][0]["text"] + "."
