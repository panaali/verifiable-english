"""VE calls shared by build.py, ve_key.py and score.py.

Every reader-facing string here is produced by VE itself: rule text by
`ve.norm_english.render_english`, formula text by the audited natural view
(`ve.printer.natural_document`), completion sentences by
`ve.norm_defaults_english.legend`, and legend lines from the data of
`ve.english.english_legend` (one line per word used). Every key is a VE
checker verdict: a norm status (`UnspecifiedDocument.status`), a conflict
report (`check_conflict`), an entailment certificate or a checked countermodel.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from ve.environment import Environment  # noqa: E402

PROFILES_NORMS = ["norm-defaults@0", "norms@0", "relational-fol@0"]


# --- vocabulary --------------------------------------------------------------

def symbols_in(data, names):
    """Every string inside `data` (AST JSON) that is one of `names`."""
    found = set()

    def walk(x):
        if isinstance(x, str):
            if x in names:
                found.add(x)
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, (list, tuple)):
            for v in x:
                walk(v)
    walk(data)
    return found


def prune(raw, predicates, constants=()):
    """The environment restricted to the named predicates and constants and the
    sorts they use. The kept declarations are byte-for-byte the use case's."""
    raw = copy.deepcopy(raw)
    voc = raw["vocabulary"]
    voc["predicates"] = {k: v for k, v in voc["predicates"].items() if k in predicates}
    voc["constants"] = {k: v for k, v in voc.get("constants", {}).items() if k in constants}
    used = {s for d in voc["predicates"].values() for s in d["arguments"]}
    used |= {d["sort"] for d in voc["constants"].values()}
    voc["sorts"] = {k: v for k, v in voc["sorts"].items() if k in used}
    for p, d in voc["predicates"].items():
        reg = d.get("regulated")
        if reg and reg.get("permission") and reg["permission"] not in voc["predicates"]:
            del reg["permission"]
    return raw


def legend_lines(env, used=None, vocabulary=None):
    """One line per sort, predicate and constant used, from VE's English legend
    data (`ve.english.english_legend`): the selected wording, then the
    declared description. Templates show each argument as <noun>."""
    from ve.english import english_legend
    options = {"vocabulary": vocabulary} if vocabulary is not None else {}
    data = json.loads(english_legend(env, "json", **options))
    nouns = {name: entry["noun"] for name, entry in data["sorts"].items()}
    lines = []
    for name, entry in data["sorts"].items():
        if used is None or name in used:
            lines.append(f'{entry["noun"]}: {entry["description"]}')
    for name, entry in data["predicates"].items():
        if used is not None and name not in used:
            continue
        if env.predicates[name].regulated is not None:
            continue  # regulated predicates are explained by their completion sentence
        args = ["<" + nouns.get(s, s.lstrip("$")) + ">" for s in entry["arguments"]]
        template = entry["template"].format(*args)
        line = f"{template}: {entry['description'].format(*args)}"
        if entry.get("negative_template"):
            line += f' (negative: {entry["negative_template"].format(*args)})'
        lines.append(line)
    for name, entry in data["constants"].items():
        if used is None or name in used:
            lines.append(f'{entry["name"]} ({nouns.get(entry["sort"], entry["sort"])}): {entry["description"]}')
    return lines


def ast_data(formula):
    from ve.ast import _to_data
    return _to_data(formula)


def run_cli(args):
    """`python -m ve ARGS` from the repository root; its JSON output."""
    import subprocess
    done = subprocess.run([sys.executable, "-m", "ve", *args], cwd=REPO, capture_output=True, text=True)
    try:
        return json.loads(done.stdout)
    except json.JSONDecodeError:
        return {"status": f"exit {done.returncode}", "stderr": done.stderr[-500:]}


# --- norms -------------------------------------------------------------------

def without_norm_defaults(raw):
    """The same environment with each `unspecified` completion read as `deny`
    and without `norm-defaults@0`: the norm English parser and the rights
    renderer read rules only on this placeholder (the rule text and its AST are
    the same; `ve.norm_defaults._placeholder` does the same)."""
    raw = copy.deepcopy(raw)
    raw["profiles"] = [p for p in raw["profiles"] if p != "norm-defaults@0"]
    for d in raw["vocabulary"]["predicates"].values():
        reg = d.get("regulated")
        if reg and reg.get("default") == "unspecified":
            reg["default"] = "deny"
    return raw


def complete_situation(base_env, situation):
    """Every base table the situation does not mention is empty (closed world)."""
    relations = dict(situation.get("relations", {}))
    for p in base_env.predicates:
        relations.setdefault(p, [])
    return {**situation, "relations": relations}


class NormItem:
    """A W1 rule text under `norm-defaults@0` and one situation. With
    `soft=True` the rules are soft-norms@0 rules (UnspecifiedSoftDocument)."""

    def __init__(self, env_raw, rules_text, *, soft=False):
        from ve.norm_english import parse_english
        from ve import norm_defaults as nd
        self.env_raw = env_raw
        self.soft = soft
        if soft:
            from ve.softnorms import SoftEnvironment
            self.env = SoftEnvironment(env_raw)
            self.parsed = parse_english(SoftEnvironment(without_norm_defaults(env_raw)), rules_text)
            self.doc = nd.UnspecifiedSoftDocument(self.env, [r.to_dict() for r in self.parsed.rules])
        else:
            self.env = Environment(env_raw)
            self.parsed = parse_english(self.env, rules_text)
            self.doc = nd.UnspecifiedDocument(self.env, self.parsed.rules)

    def soft_declarations(self):
        """The document's soft declarations in their registered English."""
        from ve.surface.softnorms import render_declaration
        soft = self.env_raw["vocabulary"]["soft"]
        lines = [render_declaration("outranks", tuple(pair)) for pair in soft["outranks"]]
        lines.append(render_declaration("outranking", soft["outranking"]))
        lines.append(render_declaration("exception_decider", soft["exception_decider"]))
        return lines

    def render(self):
        from ve.norm_english import render_english
        text = render_english(self.parsed)
        return text[0] if isinstance(text, tuple) else text

    def completion_sentences(self):
        """VE's completion (and pair) legend sentences for the regulated
        predicates the excerpt uses, in the order `legend(env)` gives them."""
        from ve.norm_defaults_english import legend
        from ve.norm_english import default_sentence, pair_sentence
        used = self.used()
        wanted = {default_sentence(self.env, p) for p, d in self.env.predicates.items()
                  if d.regulated is not None and p in used}
        for p, d in self.env.predicates.items():
            reg = d.regulated
            if reg is not None and reg.permission is not None and p in used and reg.permission in used:
                try:
                    wanted.add(pair_sentence(self.env, p))
                except Exception:
                    pass
        return [line for line in legend(self.env) if line in wanted]

    def used(self):
        names = set(self.env.predicates) | set(self.env.constants) | set(self.env.sorts)
        used = symbols_in([r.to_dict() for r in self.parsed.rules], names)
        for p in list(used):
            if p in self.env.predicates:
                used |= set(self.env.predicates[p].arguments)
        return used

    def verdict(self, situation, predicate, values):
        """The status at one point (SETTLED yes/no, UNDECIDED or UNKNOWN), its
        English paraphrase, and whether the situation has a conflict witness."""
        from ve import norm_defaults as nd
        from ve.norm_defaults_english import status_sentence
        situation = complete_situation(self.doc.situation_environment(), situation)
        sit = self.doc.situation(situation)
        status = self.doc.status(sit, predicate, tuple(values))
        out = {"point": [predicate, list(values)], "status": status.status, "value": status.value,
               "evidence": str(status.evidence),
               "sentence": status_sentence(self.doc, sit, status)}
        if not self.soft:
            conflict = nd.check_conflict(self.doc, model=situation)
            # With a model, a conflict witness is searched exhaustively in the
            # finite situation; no witness (and no exhausted budget) means none.
            out["situation_conflict"] = ("CONFLICT" if conflict.status == "CONFLICT" else
                                         "UNKNOWN" if conflict.detail == "MAX_EVALUATIONS" else "NONE")
            if conflict.status == "CONFLICT":
                out["conflict"] = {"target": conflict.target, "values": list(conflict.tuple),
                                   "kind": conflict.kind}
        out["situation"] = situation
        return out


def norm_label(verdict, role):
    """The answer label of a norm verdict at the queried point."""
    if verdict.get("situation_conflict") == "CONFLICT":
        return "CONFLICT"
    if verdict["status"] == "UNDECIDED":
        return "UNDECIDED"
    if verdict["status"] != "SETTLED":
        return "UNKNOWN"
    if role == "permission":
        return "PERMITTED" if verdict["value"] else "FORBIDDEN"
    if role == "obligation":
        return "REQUIRED" if verdict["value"] else "NOT-REQUIRED"
    return "TRUE" if verdict["value"] else "FALSE"


# --- formulas: natural view and entailment -----------------------------------

def parse_ve(env, text, vocabulary=None):
    """Formulas of VE English text (one derivation per sentence, or VE raises)."""
    from ve.english import parse_english
    options = {"vocabulary": vocabulary} if vocabulary is not None else {}
    return list(parse_english(env, text, **options).formulas)


def natural_view(env, formulas, vocabulary=None):
    """The audited natural view (`ve.printer.natural_document`): the text and,
    per sentence, `natural` or `explicit form` with the fallback reason."""
    from ve.ast import Document
    from ve.printer import natural_document
    options = {"vocabulary": vocabulary} if vocabulary is not None else {}
    view = natural_document(env, Document(tuple(formulas)), **options)
    return {"text": view.text, "renderer": f"{view.renderer} v{view.version}",
            "sentences": [{"text": s["text"], "form": s["form"], "fallback_reason": s.get("fallback_reason")}
                          for s in view.sentences]}


def presentation(env, text, vocabulary=None):
    """`ve.prose@1`: parse author prose (pronouns included) and render it back
    with the same parser; returns the formulas and VE's displayed text."""
    from ve.natural import parse_presentation, render_presentation
    options = {"vocabulary": vocabulary} if vocabulary is not None else {}
    parsed = parse_presentation(env, text, **options)
    shown = render_presentation(env, parsed.document, **options)
    return list(parsed.document.formulas), shown.text if hasattr(shown, "text") else str(shown)


def _model_json(model):
    return model.to_dict() if hasattr(model, "to_dict") else str(model)


def entail3(env, premises, conclusion, *, max_steps=20_000, max_domain_size=3):
    """FOLLOWS (a replayable tableau certificate for the conclusion),
    CONTRADICTED (one for its negation), NEITHER (checked countermodels both
    ways: the premises decide nothing) or UNKNOWN."""
    from ve.ast import Not
    from ve.entailment import check_entailment_certificate, prove_entailment
    from ve.search import find_countermodel
    out = {}
    for label, goal in (("conclusion", conclusion), ("negation", Not(conclusion))):
        proof = prove_entailment(env, premises, goal, max_steps=max_steps)
        replay = (check_entailment_certificate(env, premises, goal, proof.certificate).valid
                  if proof.status == "Found" else None)
        out[label] = {"proof": proof.status, "certificate_replayed": replay}
        if proof.status == "Found" and replay:
            out["label"] = "FOLLOWS" if label == "conclusion" else "CONTRADICTED"
            return out
    for label, goal in (("conclusion", conclusion), ("negation", Not(conclusion))):
        found = find_countermodel(env, premises, goal, max_domain_size=max_domain_size)
        out[label]["countermodel"] = found.status
        if found.status == "Found":
            out[label]["model"] = _model_json(found.model)
    both = all(out[k].get("countermodel") == "Found" for k in ("conclusion", "negation"))
    out["label"] = "NEITHER" if both else "UNKNOWN"
    return out


# --- writing: mechanical scoring ---------------------------------------------

def _error(exc):
    from ve.errors import AmbiguousDerivation
    message = str(exc)
    kind = "ambiguous" if isinstance(exc, AmbiguousDerivation) or "two derivations" in message else "parse_failure"
    return {"outcome": kind, "ve_message": message, "error_type": type(exc).__name__}


def _equivalence(env, a, b):
    from ve.equivalence import compare
    result = compare(env, a, b)
    return {"status": result.status, "relation": result.relation,
            "detail": getattr(result, "relation_detail", None)}


def score_formula(env, sentence, gold, vocabulary=None):
    """parse_failure / ambiguous / not_one_sentence / wrong_meaning / correct / unknown."""
    from ve.english import parse_english_with_metadata
    from ve.errors import VEError
    options = {"vocabulary": vocabulary} if vocabulary is not None else {}
    try:
        meta = parse_english_with_metadata(env, sentence, **options)
    except (VEError, ValueError) as exc:
        return _error(exc)
    formulas = meta.document.formulas
    if len(formulas) != 1:
        return {"outcome": "not_one_sentence", "ve_message": meta.english_text,
                "sentences": len(formulas)}
    eq = _equivalence(env, formulas[0], gold)
    outcome = {"EQUIVALENT": "correct", "DIFFERENT": "wrong_meaning"}.get(eq["status"], "unknown")
    return {"outcome": outcome, "ve_message": meta.english_text.strip(), "equivalence": eq}


def _instantiate_outcome(document, predicate, names):
    from ve.ast import Const
    from ve.norms import _instantiate
    return _instantiate(document.outcome(predicate, base=True), tuple(Const(n) for n in names))


def score_norm(env_raw, sentence, gold_text, predicate, fresh, context_text=None):
    """A rule text is correct when, under the environment's declared default,
    the completed outcome of `predicate` at fresh constants is equivalent to
    the gold rule's (ve.equivalence.compare over the base vocabulary)."""
    from ve.errors import VEError
    from ve.norm_english import parse_english, render_english
    from ve.norms import NormDocument
    scoring = copy.deepcopy(env_raw)
    scoring["vocabulary"]["constants"].update(fresh)
    env = Environment(scoring)
    text = sentence.strip()
    number = 1 + (context_text.count("\n") + 1 if context_text else 0)
    if not text.startswith("Rule "):
        text = f"Rule {number}. " + text  # the editor numbers a new rule block
    if context_text:
        text = context_text.strip() + "\n" + text
    try:
        parsed = parse_english(Environment(env_raw), text)
    except (VEError, ValueError) as exc:
        return _error(exc)
    shown = render_english(parsed)
    shown = shown[0] if isinstance(shown, tuple) else shown
    attempt = NormDocument(env, [r for r in parsed.rules])
    gold = NormDocument(env, list(parse_english(Environment(env_raw), gold_text).rules))
    base = gold.base_environment()
    names = tuple(fresh)
    eq = _equivalence(base, _instantiate_outcome(gold, predicate, names),
                      _instantiate_outcome(attempt, predicate, names))
    outcome = {"EQUIVALENT": "correct", "DIFFERENT": "wrong_meaning"}.get(eq["status"], "unknown")
    # Two rules that select the same case leave W1's outcome undefined there
    # (a CONFLICT); an equivalent outcome formula does not make that correct.
    from ve.norms import check_conflict
    conflict = check_conflict(attempt, prove=True).status
    if outcome == "correct" and conflict != "CONFLICT-FREE":
        outcome = "wrong_meaning" if conflict == "CONFLICT" else "unknown"
    return {"outcome": outcome, "ve_message": shown, "rules": len(parsed.rules), "equivalence": eq,
            "conflict": conflict}


def score_risk(env_raw, sentence, gold, actions, harms):
    """A record statement is correct when VE reads it as exactly the gold
    reading. Form, action and harm are VE's parse; a condition is compared as
    W6 condition text after whitespace normalisation, because no Python decoder
    for record condition text exists (ve/surface/risk.py returns it as text)."""
    from ve.errors import VEError
    from ve.surface.risk import parse_wording, render_wording
    env = Environment(env_raw)
    try:
        reading = parse_wording(sentence.strip(), env, actions=actions, harms=harms, context="record")
    except (VEError, ValueError) as exc:
        return _error(exc)
    shown = render_wording(reading, actions=actions, harms=harms)
    norm = lambda r: {k: (" ".join(v.split()) if k == "condition_text" else v) for k, v in r.items()}
    same = norm(reading) == norm(gold)
    if same:
        outcome, status = "correct", "EQUIVALENT"
    elif ({k: v for k, v in reading.items() if k != "condition_text"} ==
          {k: v for k, v in gold.items() if k != "condition_text"}):
        # Same form, action and harm; only the condition text differs. VE has
        # no decoder that could decide whether the two conditions agree, so
        # this is neither a verified meaning nor a verified wrong meaning.
        outcome, status = "condition_unverified", "UNKNOWN"
    else:
        outcome, status = "wrong_meaning", "DIFFERENT"
    return {"outcome": outcome, "ve_message": shown, "reading": reading,
            "equivalence": {"status": status, "method": "identical registered reading"}}
