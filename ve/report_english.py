"""The reports@0 English of attribution.md section 2: one grammar for typed and
rendered text, bound to a manifest (2.4).

The printer writes the wordings of 2.1; the parser reads them with every
derivation enumerated and admits a sentence only when exactly one derivation
exists (the all-derivations gate of 2.1). A formula content is read by the
existing all-derivations English parser. A sentence alone is not a unit: the
manifest carries the environment, the context record of each verb and the
assessment record of each assessment in reading order, the content of each
literal quotation and the reading choices, and parsing under a manifest that
the document does not have is ``ManifestMismatch``.
"""
from __future__ import annotations

import re

from . import ast
from .english import EnglishVocabulary, parse_english, render_english
from .errors import VEError

TENSES = ("present", "past", "perfect")
_VERBS = {
    "says": ("says", "said", "has said"),
    "believes": ("believes", "believed", "has believed"),
    "wants": ("wants", "wanted", "has wanted"),
    "intends": ("intends", "intended", "has intended"),
}
# 2.2: input synonyms rendered canonically, and nothing else.
_SYNONYMS = {("says", "states"): "present", ("says", "stated"): "past"}
_ASSESSED = "according to the stated assessment, "
_MAY, _PROBABLY, _LIKELY = "it may be that ", "it is probably the case that ", "it is likely that "
_NOT = "it is not the case that "
# 2.2: not synonyms, each rejected with its reason.
_REJECTED = {
    "thinks that": "belief or opinion; not admitted",
    "claims that": "act pending review", "argues that": "act pending review",
    "denies that": "act pending review; a denial is not a negated belief",
    "plans to": "promise, prediction and intention are never identified",
    "hopes to": "promise, prediction and intention are never identified",
    "expects to": "promise, prediction and intention are never identified",
    "predicts that": "promise, prediction and intention are never identified",
    "should": "desire and duty are never synonyms",
    "could": "not the assessment template", "might": "not the assessment template",
    "possibly": "not the assessment template",
}


class _Words:
    """The display names of one document's environment."""

    def __init__(self, reports):
        self.reports = reports
        env = reports.environment
        self.legend = EnglishVocabulary(env).constants
        holders = env.reports["holders"]
        self.holders = {name: (decl.verbalisation or self.legend[name])
                        for name, decl in env.constants.items() if decl.sort in holders}


def _capital(text):
    return text[0].upper() + text[1:]


# ---------------------------------------------------------------- formulas


def _formula_text(reports, words, formula):
    """The formula's one-reading English, lower-cased at its start unless it begins
    with a capitalised declared name (as `render_english` marks conclusions)."""
    sentence = render_english(formula, reports.environment)
    proper = any(display and display[0].isupper() and sentence.startswith(display)
                 for display in words.legend.values())
    return sentence if proper else sentence[0].lower() + sentence[1:]


def _parse_formula(reports, text):
    try:
        formulas = parse_english(reports.environment, text + ".").formulas
    except VEError:
        return []
    return [{"ast": ast.formula_to_data(reports.environment, f)} for f in formulas] if len(formulas) == 1 else []


def _infinitive(finite):
    """`is safe` -> `be safe`: the finite verb phrase of a declared template as an
    infinitive, only where `_finite` gives it back exactly."""
    head, _, rest = finite.partition(" ")
    if rest.startswith("not ") or not re.fullmatch(r"[a-z]+", head):
        return None
    base = {"is": "be", "has": "have", "does": "do"}.get(head)
    if base is None:
        if re.search(r"[^aeiou]ies\Z", head):
            base = head[:-3] + "y"
        elif re.search(r"(?:ss|sh|ch|x|z|o)es\Z", head):
            base = head[:-2]
        elif head.endswith("s") and not head.endswith("ss"):
            base = head[:-1]
    infinitive = base + (" " + rest if rest else "") if base else None
    return infinitive if infinitive and _finite(infinitive) == finite else None


def _finite(infinitive):
    head, _, rest = infinitive.partition(" ")
    verb = {"be": "is", "have": "has", "do": "does"}.get(head)
    if verb is None:
        if re.search(r"[^aeiou]y\Z", head):
            verb = head[:-1] + "ies"
        elif re.search(r"(?:s|sh|ch|x|z|o)\Z", head):
            verb = head + "es"
        else:
            verb = head + "s"
    return verb + (" " + rest if rest else "")


def _subject_split(reports, words, node):
    """A formula content as (subject name, subject display, infinitival VP): its
    rendering is `<display of a declared constant> <finite VP>`."""
    if next(iter(node)) != "ast":
        return None
    formula = ast.formula_from_data(reports.environment, node["ast"])
    if type(formula) not in (ast.Unary, ast.Binary):
        return None
    subject = formula.term if type(formula) is ast.Unary else formula.left
    if type(subject) is not ast.Const:
        return None
    text, display = _formula_text(reports, words, formula), words.legend[subject.name]
    if not text.startswith(display + " "):
        return None
    infinitive = _infinitive(text[len(display) + 1:])
    return (subject.name, display, infinitive) if infinitive else None


# ---------------------------------------------------------------- printer


def _print(reports, words, node, manifest, initial):
    tag, value = next(iter(node.items()))
    if tag == "negated":
        inner = _print(reports, words, value, manifest, False)
        text = _NOT.rstrip() + ", " + inner if "assessment" in value else _NOT + inner
    elif tag == "report":
        context = reports.contexts[value["context"]]
        manifest["contexts"].append(context)
        holder = words.holders[value["holder"]]
        verb = _VERBS[value["act"]][TENSES.index(context["tense"])]
        if value.get("literal") is not None:
            if value["act"] != "says":
                raise VEError("No reviewed wording: a literal quotation is admitted only for saying")
            manifest["literals"].append(value["content"])
            text = holder + " " + verb + ', "' + value["literal"] + '"'
        elif value["act"] in ("says", "believes"):
            text = holder + " " + verb + " that " + _complement(reports, words, value["content"], manifest)
        else:
            split = _subject_split(reports, words, value["content"])
            if split is None:
                raise VEError(f"No reviewed wording: {value['act']} needs a sentence '<Name> <verb phrase>' "
                              "about a declared name")
            name, display, vp = split
            if name == value["holder"]:
                text = holder + " " + verb + " to " + vp
            elif value["act"] == "wants":
                text = holder + " " + verb + " " + display + " to " + vp
            else:
                raise VEError("No reviewed wording: an intention's embedded subject is the holder (1.3)")
    elif tag == "assessment":
        manifest["assessments"].append(reports.assessments[value["record"]])
        split = _subject_split(reports, words, value["content"])
        if split is not None and value["judgment"] == "may":
            text = _ASSESSED + split[1] + " may " + split[2]
        elif split is not None and split[2].startswith("be "):
            text = _ASSESSED + split[1] + " is probably " + split[2][3:]
        else:
            lead = _MAY if value["judgment"] == "may" else _PROBABLY
            text = _ASSESSED + lead + _complement(reports, words, value["content"], manifest)
    else:
        raise VEError("No reviewed wording for this content")
    return _capital(text) if initial else text


def _complement(reports, words, node, manifest):
    if next(iter(node)) == "ast":
        return _formula_text(reports, words, ast.formula_from_data(reports.environment, node["ast"]))
    return _print(reports, words, node, manifest, False)


# ---------------------------------------------------------------- parser
#
# Every function returns every derivation of its whole input: a list of report
# skeletons whose report nodes carry a tense (not yet a context) and whose
# assessment nodes carry no record, both bound from the manifest afterwards in
# reading order.


def _statement(reports, words, text, initial):
    results = []
    lead = (lambda s: _capital(s)) if initial else (lambda s: s)
    if text.startswith(lead(_NOT.rstrip() + ", ")):
        results += [{"negated": n} for n in _assessment(reports, words, text[len(_NOT) + 1:], False)]
    elif text.startswith(lead(_NOT)):
        results += [{"negated": n} for n in _report(reports, words, text[len(_NOT):], False)]
    results += _report(reports, words, text, initial)
    results += _assessment(reports, words, text, initial)
    return results


def _report(reports, words, text, initial):
    results = []
    for holder, display in words.holders.items():
        for shown in {display, _capital(display)} if initial else {display}:
            if not text.startswith(shown + " "):
                continue
            rest = text[len(shown) + 1:]
            for act, forms in _VERBS.items():
                spellings = [(form, tense) for form, tense in zip(forms, TENSES)]
                spellings += [(word, tense) for (a, word), tense in _SYNONYMS.items() if a == act]
                for form, tense in spellings:
                    if not rest.startswith(form + " ") and not rest.startswith(form + ","):
                        continue
                    tail = rest[len(form):]
                    node = {"holder": holder, "act": act, "tense": tense}
                    if act in ("says", "believes") and tail.startswith(" that "):
                        results += [{"report": {**node, "content": c}}
                                    for c in _complement_parse(reports, words, tail[6:])]
                    if act == "says" and tail.startswith(', "') and tail.endswith('"') and len(tail) > 4:
                        results.append({"report": {**node, "literal": tail[3:-1], "content": None}})
                    if act in ("wants", "intends") and tail.startswith(" to "):
                        results += [{"report": {**node, "content": c}}
                                    for c in _parse_formula(reports, words.legend[holder] + " " + _finite(tail[4:]))]
                    if act == "wants":
                        for subject, sdisplay in words.legend.items():
                            if tail.startswith(" " + sdisplay + " to "):
                                vp = tail[len(sdisplay) + 5:]
                                results += [{"report": {**node, "content": c}}
                                            for c in _parse_formula(reports, sdisplay + " " + _finite(vp))]
    return results


def _assessment(reports, words, text, initial):
    lead = _capital(_ASSESSED) if initial else _ASSESSED
    if not text.startswith(lead):
        return []
    rest, results = text[len(lead):], []
    for prefix, judgment in ((_MAY, "may"), (_PROBABLY, "probably"), (_LIKELY, "probably")):
        if rest.startswith(prefix):
            results += [{"assessment": {"judgment": judgment, "content": c}}
                        for c in _complement_parse(reports, words, rest[len(prefix):])]
    for subject, display in words.legend.items():
        if not rest.startswith(display + " "):
            continue
        tail = rest[len(display) + 1:]
        for word in ("may not ", "is probably not "):
            if tail.startswith(word):
                raise VEError(f"'{word.strip()}' has two readings; write the negation inside ('it may be that it "
                              "is not the case that S') or outside ('It is not the case that, according to the "
                              "stated assessment, it may be that S')")
        for word, judgment, verb in (("may ", "may", ""), ("is probably ", "probably", "be ")):
            if tail.startswith(word):
                for c in _parse_formula(reports, display + " " + _finite(verb + tail[len(word):])):
                    formula = ast.formula_from_data(reports.environment, c["ast"])
                    if type(formula) in (ast.Unary, ast.Binary):
                        results.append({"assessment": {"judgment": judgment, "content": c}})
    return results


def _complement_parse(reports, words, text):
    return _statement(reports, words, text, False) + _parse_formula(reports, text)


def _bind(reports, node, manifest, cursor):
    """Give each report node the next manifest context (its tense must be the verb's)
    and each assessment node the next manifest record, in reading order."""
    tag, value = next(iter(node.items()))
    if tag == "ast":
        return node
    if tag == "negated":
        return {"negated": _bind(reports, value, manifest, cursor)}
    if tag == "report":
        contexts = manifest.get("contexts", [])
        if cursor["contexts"] >= len(contexts) or contexts[cursor["contexts"]].get("tense") != value["tense"]:
            raise VEError("ManifestMismatch: the verb's tense and the manifest's context differ")
        context = contexts[cursor["contexts"]]["id"]
        cursor["contexts"] += 1
        if value.get("literal") is not None:
            literals = manifest.get("literals", [])
            if cursor["literals"] >= len(literals):
                raise VEError("ManifestMismatch: a literal quotation without its content")
            content = literals[cursor["literals"]]
            cursor["literals"] += 1
            return {"report": {"holder": value["holder"], "act": value["act"], "context": context,
                               "literal": value["literal"], "content": content}}
        return {"report": {"holder": value["holder"], "act": value["act"], "context": context,
                           "literal": None, "content": _bind(reports, value["content"], manifest, cursor)}}
    records = manifest.get("assessments", [])
    if cursor["assessments"] >= len(records):
        raise VEError("ManifestMismatch: an assessment without its record")
    record = records[cursor["assessments"]]["id"]
    cursor["assessments"] += 1
    return {"assessment": {"judgment": value["judgment"], "record": record,
                           "content": _bind(reports, value["content"], manifest, cursor)}}


def _rejection(words, text):
    lowered = text.lower()
    for phrase, reason in _REJECTED.items():
        if re.search(r"\b" + re.escape(phrase) + r"\b", lowered):
            return f"'{phrase}' is not a reports wording: {reason}"
    if lowered.startswith("according to ") and not lowered.startswith(_ASSESSED):
        return "'According to <Holder>, S' is W2's rendering of a labelled unit, not a reports sentence"
    for display in words.holders.values():
        for verbs in _VERBS.values():
            if any(re.search(r"\b(?:and|or) " + re.escape(display) + " " + re.escape(v) + r"\b", text)
                   for v in verbs):
                return "a Boolean over report wordings has no reading: write separate units"
    if re.match(r"(?:every|some|each) ", lowered):
        return "OpenComplement: a binder over holders is outside this slice"
    return "no reports wording derives this sentence"


def parse_report_sentence(reports, text, manifest):
    """The report content one sentence has under a manifest: every derivation of
    the grammar is enumerated, and exactly one must exist."""
    _check_manifest(reports, manifest)
    if type(text) is not str or not text.endswith("."):
        raise VEError("A report sentence ends with a full stop")
    words = _Words(reports)
    body = text[:-1]
    derivations = _statement(reports, words, body, True)
    if not derivations:
        raise VEError(_rejection(words, body))
    bound = []
    for skeleton in derivations:
        cursor = {"contexts": 0, "assessments": 0, "literals": 0}
        node = _bind(reports, skeleton, manifest, cursor)
        if cursor != {key: len(manifest.get(key, [])) for key in cursor}:
            raise VEError("ManifestMismatch: the manifest does not match the sentence")
        if node not in bound:
            bound.append(node)
    if len(bound) != 1:
        raise VEError(f"The sentence has {len(bound)} readings; the reports grammar admits one")
    return bound[0]


def _manifest_for(reports):
    return {"environment_id": reports.environment.environment_id,
            "profiles": list(reports.environment.profiles), "choices": list(reports.choices),
            "contexts": [], "assessments": [], "literals": []}


def _check_manifest(reports, manifest):
    if type(manifest) is not dict:
        raise VEError("ManifestMismatch: missing manifest")
    expected = _manifest_for(reports)
    for key in ("environment_id", "profiles", "choices"):
        if manifest.get(key) != expected[key]:
            raise VEError(f"ManifestMismatch: {key}")
    for key, table in (("contexts", reports.contexts), ("assessments", reports.assessments)):
        for record in manifest.get(key, []):
            if type(record) is not dict or table.get(record.get("id")) != record:
                raise VEError(f"ManifestMismatch: {key}")


def render_report_sentence(reports, node):
    """The one wording of a report content, with its manifest; the wording must
    parse back, under that manifest, to exactly this content (P4)."""
    manifest = _manifest_for(reports)
    text = _print(reports, _Words(reports), node, manifest, True) + "."
    try:
        parsed = parse_report_sentence(reports, text, manifest)
    except VEError as exc:
        raise VEError(f"No writable wording passed the one-reading check: {exc}") from exc
    if reports.meaning_id(parsed) != reports.meaning_id(node):
        raise VEError("No writable wording passed the one-reading check")
    return text, manifest


def render_report_unit(reports, unit_id):
    """Render one unit with its manifest and identity."""
    unit = next((u for u in reports.units if u["id"] == unit_id and type(u.get("content")) is dict
                 and set(u["content"]) & {"report", "assessment", "negated"}), None)
    if unit is None:
        raise VEError(f"Unknown report unit {unit_id}")
    text, manifest = render_report_sentence(reports, unit["content"])
    return {"text": text, "unit": unit_id, "meaning_id": reports.meaning_id(unit["content"]),
            "envelope": reports.envelope, "manifest": manifest}


def parse_rendered_report(reports, rendering):
    """Parse a rendered unit's text under its manifest; the manifest must be this
    document's (2.4), and the content comes from the grammar, not from the unit."""
    if type(rendering) is not dict or type(rendering.get("text")) is not str:
        raise VEError("ManifestMismatch: missing report text")
    node = parse_report_sentence(reports, rendering["text"], rendering.get("manifest"))
    if "meaning_id" in rendering and reports.meaning_id(node) != rendering["meaning_id"]:
        raise VEError(f"ManifestMismatch: {rendering.get('unit')}")
    return node
