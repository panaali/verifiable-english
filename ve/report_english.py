"""Bound, canonical review wording for decoded reports@0 units.

The manifest carries the exact report object. Parsing checks an exact canonical
round trip against that object; arbitrary new report prose is not admitted yet.
"""
from __future__ import annotations

from . import ast
from .english import parse_english, render_english
from .errors import VEError

_VERBS = {
    "says": ("says", "said", "has said"),
    "believes": ("believes", "believed", "has believed"),
    "wants": ("wants", "wanted", "has wanted"),
    "intends": ("intends", "intended", "has intended"),
}


def _sentence(reports, node):
    tag, value = next(iter(node.items()))
    if tag == "ast":
        formula = ast.formula_from_data(reports.environment, value)
        text = render_english(formula, reports.environment)
        if parse_english(reports.environment, text + ".").formulas != (formula,):
            raise VEError("English formula changed its reading")
        return text
    if tag == "negated":
        inner = _sentence(reports, value)
        return "It is not the case that " + inner
    if tag == "report":
        holder = reports.environment.constants[value["holder"]]
        name = holder.verbalisation or holder.description or value["holder"]
        tense = reports.contexts[value["context"]]["tense"]
        verb = _VERBS[value["act"]][("present", "past", "perfect").index(tense)]
        if value.get("literal") is not None:
            if value["act"] != "says":
                raise VEError("Literal wording is admitted only for saying")
            return name + " " + verb + ', "' + value["literal"] + '"'
        inner = _sentence(reports, value["content"])
        return name + " " + verb + " that " + inner
    if tag == "assessment":
        inner = _sentence(reports, value["content"])
        phrase = "it may be that " if value["judgment"] == "may" else "it is probably the case that "
        return "According to the stated assessment, " + phrase + inner
    raise VEError("No reviewed wording for this content")


def render_report_unit(reports, unit_id):
    """Render one unit with its full document envelope and identity."""
    unit = next((u for u in reports.units if u["id"] == unit_id), None)
    if unit is None:
        raise VEError(f"Unknown report unit {unit_id}")
    return {"text": _sentence(reports, unit["content"]) + ".",
            "unit": unit_id, "meaning_id": reports.meaning_id(unit["content"]),
            "envelope": reports.envelope,
            "contexts": list(reports.contexts.values()),
            "assessments": list(reports.assessments.values()),
            "profiles": list(reports.environment.profiles), "choices": reports.choices}


def parse_rendered_report(reports, rendering):
    """Accept only the unique wording tied to this document's manifest."""
    if type(rendering) is not dict or "unit" not in rendering:
        raise VEError("ManifestMismatch: missing report unit")
    expected = render_report_unit(reports, rendering["unit"])
    if rendering != expected:
        raise VEError(f"ManifestMismatch: {rendering['unit']}")
    return next(u["content"] for u in reports.units if u["id"] == rendering["unit"])
