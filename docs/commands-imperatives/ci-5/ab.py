"""The CI-5 A/B: from a checkout's root, `uv run python <this file> OUT.json`, on the merge base and on HEAD; then
`python3 <this file> --merge BASE.json HEAD.json AB.json` saves the rows with their class, one row per line."""
import json
import sys
from pathlib import Path

SIDES = ("command", "document", "elaborate")


def merge(base_file, head_file, out):
    base, head = json.loads(Path(base_file).read_text()), json.loads(Path(head_file).read_text())
    rows = []
    for b, h in zip(base["rows"], head["rows"]):
        row = {k: h[k] for k in ("class", "name", "wording", "environment")}
        row.update(base={k: b[k] for k in SIDES}, head={k: h[k] for k in SIDES})
        if h["class"] == "b2":
            row["refusal"] = h["elaborate"]["error"]
        rows.append(json.dumps(row, sort_keys=True))
    identical = json.dumps(base["acts_off"] == head["acts_off"])
    Path(out).write_text('{"acts_off_identical": %s, "acts_off_rows": %d, "rows": [\n%s\n]}\n'
                         % (identical, len(head["acts_off"]), ",\n".join(rows)))


if sys.argv[1] == "--merge":
    merge(*sys.argv[2:])
    sys.exit()

sys.path.insert(0, str(Path.cwd()))
from tests import lean_routes
from tests.lean_service_corpus import command_cases
from ve import Environment
from ve.english import EnglishVocabulary
from ve.english_grammar import export
from ve.errors import VEError
from ve.profiles import LANGUAGE, SPEC_REVISION
from ve.speech_document import SpeechSource

ACTS = ["acts@0", "norms@0", "relational-fol@0", "speech-acts@0"]
OFF = ["norms@0", "relational-fol@0", "speech-acts@0"]
CHOICES = {"choose_scenario_required": "{0} choose a scenario and its listed facts",
           "choose_kinds_required": "{0} choose declared kinds of things for the new word",
           "enter_required": "{0} enter a clarification or restatement"}
FIXED = ["a scenario and its listed facts", "clarification or restatement",
         "declared kinds of things for the new word"]
READ = {"Choose a scenario and its listed facts.": "b1", "Choose declared kinds of things for the new word.": "b1",
        "Enter a clarification or restatement.": "b1"}


def env(acts, fixed, profiles):
    vocabulary = {"sorts": {s: {"description": s} for s in ("user", "text")},
                  "predicates": {p: {"arguments": ["user", "text"] if "{1}" in a else ["user"], "description": p,
                                     "regulated": {"role": "obligation", "default": "deny", "act": a}}
                                 for p, a in acts.items()},
                  "constants": {"reader": {"sort": "user", "description": "reader"},
                                "the_word": {"sort": "text", "description": "the new word"}}}
    if fixed is not None:
        vocabulary["acts"] = {"fixed": fixed}
    return {"language": LANGUAGE, "spec_revision": SPEC_REVISION, "profiles": profiles,
            "speech_acts": {"task": "webapp-copy", "addressee": {"sort": "user", "constant": "reader"},
                            "definites": {"the new word": "the_word"}},
            "vocabulary": vocabulary}


def service(mode, case):
    try:
        return lean_routes.rows(mode, [case])[0]
    except VEError as refused:
        return {"refused": refused.message}


def command(environment, wording):
    try:
        lexicon = export(EnglishVocabulary(Environment(environment)))
    except VEError as refused:
        return {"refused_before_mode": refused.message}
    return service("english.command", {"id": "c", "environment": environment, "lexicon": lexicon, "unit": "u1",
                                       "wording": wording, "queries": []})


def document(environment, wording):
    source = wording + "\n"
    metadata = {"format": "ve-document@2", "environment": environment,
                "units": [{"id": "u1", "span": [0, len(source)], "kind": "instruction", "meaning": "specified",
                           "support": "none", "content": {"fence": "u1"}, "surface": "english"}]}
    try:
        report = SpeechSource(metadata, source.encode(), {"u1": source}).report
    except VEError as refused:
        return {"refused": refused.message}
    return {"commands": report.get("commands")}


def row(klass, name, environment, wording):
    return {"class": klass, "name": name, "wording": wording, "environment": environment,
            "command": command(environment, wording), "document": document(environment, wording),
            "elaborate": service("ve_speech_acts_route", {"id": "e", "kind": "speech-elaborate",
                                                          "environment": environment, "document": {"units": []}})}


rows = [row(k, "fixed phrases, acts@0 on", env(CHOICES, FIXED, ACTS), w) for w, k in READ.items()]
rows += [row("none", "the same acts, acts@0 off", env(CHOICES, None, OFF), w) for w in READ]
click = {"click_required": "{0} click Check and save"}
rows += [row("b2", "joined act, acts@0 on", env(click, [], ACTS), "Click Check and save."),
         row("b1", "the same words as a fixed phrase, acts@0 on", env(click, ["Check and save"], ACTS),
             "Click Check and save."),
         row("b2", "slot after for, acts@0 on", env({"choose_kinds_required": "{0} choose declared kinds of things"
                                                     " for {1}"}, [], ACTS),
             "Choose declared kinds of things for the new word.")]
off = [{"id": c["id"], "answer": service("english.command", c)} for c in command_cases()]
Path(sys.argv[1]).write_text(json.dumps({"rows": rows, "acts_off": off}, indent=1, sort_keys=True) + "\n")
