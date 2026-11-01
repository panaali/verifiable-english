"""The senses display: each candidate of an open unit as English, rendered and re-read under its own projection.

Senses plan 2.8 and B7: Python formats and relays; it decides nothing. A candidate's English is Python's renderer
over the candidate's formula in the environment Lean projects for its resolving lines (`senses.project`). Lean's
senses reader then re-reads the candidate's lines followed by that text: the rendering is shown only when the
re-read has one reading, of exactly the candidate's formula and mark, under a projection whose identities are the
ones the reading lists for the candidate, so the same projection and never the base one (in which the unresolved
word has no bare rule). The renderer is an untrusted producer (lean-first 2.3): any other answer is
`CheckerUnavailable`. Every text shown beside a rendering (the resolving lines) is Lean's, relayed verbatim.
"""
from __future__ import annotations

import warnings

from .. import ast
from ..backends import senses as route
from ..english import UnreviewedVocabularyWarning
from ..environment import Environment
from ..errors import CheckerUnavailable, ResourceLimit, VEError
from ..printer import render

# The display's limit on the candidates one call renders and re-reads (one `senses.read` each); each distinct set of
# resolving lines is projected once. Lean caps each unit at `route.CANDIDATE_CAP` candidates.
MAX_CANDIDATES = 64


def _display_overlay(overlay: dict | None, env: Environment) -> dict | None:
    """The author's display overlay (constant spellings, plurals) addressed to the projected environment: display
    data only, since Lean re-reads the rendering."""
    return None if overlay is None else {**overlay, "environment_id": env.environment_id}


def _rendered(projection: dict, candidate: dict, overlay: dict | None) -> str:
    try:
        env = Environment(projection["environment"])
        node = ast.formula_from_data(env, candidate["formula"])
        with warnings.catch_warnings():
            # The re-addressed copy has the author's overlay's review status, which the CLI reports.
            warnings.simplefilter("ignore", UnreviewedVocabularyWarning)
            return render(ast.Document((node,)), env, "ve_english", vocabulary=_display_overlay(overlay, env),
                          conclusions=(0,) if candidate["mark"] else ()).rstrip("\n")
    except (VEError, KeyError, TypeError, ValueError) as exc:
        raise CheckerUnavailable(f"CheckerUnavailable: a candidate could not be rendered: {exc}") from exc


def reread(env, packs: list[bytes], candidate: dict, text: str, *, own=None, overlay=None) -> bool:
    """Whether Lean's senses reader reads the candidate's lines followed by `text` to one reading of exactly the
    candidate's formula and mark, under the candidate's projection (its listed identities)."""
    reading = route.read(env, candidate["lines"] + "\n" + text, packs, own=own, overlay=overlay)["reading"]
    if reading["status"] != "one" or len(reading["units"]) != 1:
        return False
    unit = reading["units"][0]
    return (unit["formula"] == candidate["formula"] and unit["mark"] is candidate["mark"]
            and {key: reading["identities"][key] for key in route.PROJECTION_IDS} == candidate["identities"])


def candidates(env, packs: list[bytes], reading: dict, *, own: list[dict] | None = None,
               overlay: dict | None = None) -> list[dict]:
    """Each candidate of each open unit of a relayed `senses.read` reading: its sentence, its position, Lean's
    resolving lines and its English, rendered under the projection of those lines and re-read by Lean under the same
    projection. A projection whose identities are not the ones the reading lists for the candidate (i7), or a
    rendering Lean does not read back, is `CheckerUnavailable`."""
    units = reading.get("units", ())
    if sum(len(unit["candidates"]) for unit in units) > MAX_CANDIDATES:
        raise ResourceLimit(f"The senses display renders at most {MAX_CANDIDATES} candidates")
    projections: dict[str, dict] = {}
    rows = []
    for unit in units:
        for index, candidate in enumerate(unit["candidates"]):
            lines = candidate["lines"]
            if lines not in projections:
                projections[lines] = route.project(env, packs, lines, list(reading["used"]), own=own,
                                                   overlay=overlay)["projection"]
            projection = projections[lines]
            if projection.get("status") != "ok" or {key: projection["identities"][key] for key in
                                                    route.PROJECTION_IDS} != candidate["identities"]:
                raise CheckerUnavailable("CheckerUnavailable: a candidate's projection is not the one its reading "
                                         "lists")
            text = _rendered(projection, candidate, overlay)
            if not reread(env, packs, candidate, text, own=own, overlay=overlay):
                raise CheckerUnavailable("CheckerUnavailable: a candidate's rendering does not re-read under its "
                                         "projection")
            rows.append({"sentence": unit["sentence"], "candidate": index, "lines": lines, "text": text})
    return rows
