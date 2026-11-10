"""The senses display: Lean's reading shown as English, each rendering re-read by Lean under its own projection.

Senses plan 2.8 and B7: Python formats and relays; it decides nothing. A rendering is Python's renderer over a
formula in an environment Lean projected: a resolved body's in the reading's own projected environment, after Lean's
preamble lines; a candidate's in the environment `senses.project` returns for its resolving lines. Lean then
re-reads it: the body as a whole document (one reading of the same formulas and marks under the same projection
identities), a candidate through `senses.read`'s `reread` member (sn-b6d: read under the candidate's own projection
from the state before its unit), so never under the base projection (in which the unresolved word has no bare
rule). The renderer is an untrusted producer (lean-first 2.3): any other answer is `CheckerUnavailable`. Every text
shown beside a rendering (the preamble and resolving lines, the unit's text, the warnings) is Lean's, relayed
verbatim; the glossary and the hover rows are the sense map's entries, with the source bytes of their Lean spans.
"""
from __future__ import annotations

import warnings

from .. import ast
from ..backends import senses as route
from ..english import UnreviewedVocabularyWarning
from ..environment import Environment
from ..errors import CheckerUnavailable, ResourceLimit, VEError
from ..identity import meaning_id
from ..model import FiniteModel
from ..printer import render
from ..readings import validate_reading_sets

# The display's limit on the candidates one call renders and re-reads (one `senses.read` each); each distinct set of
# resolving lines is projected once. Lean caps each unit at `route.CANDIDATE_CAP` candidates.
MAX_CANDIDATES = 64


def _display_overlay(overlay: dict | None, env: Environment) -> dict | None:
    """The author's display overlay (constant spellings, plurals) addressed to the projected environment: display
    data only, since Lean re-reads the rendering."""
    return None if overlay is None else {**overlay, "environment_id": env.environment_id}


def _render(environment: dict, formulas: list, marks: list[bool], overlay: dict | None) -> str:
    try:
        env = Environment(environment)
        nodes = tuple(ast.formula_from_data(env, formula) for formula in formulas)
        with warnings.catch_warnings():
            # The re-addressed copy has the author's overlay's review status, which the CLI reports.
            warnings.simplefilter("ignore", UnreviewedVocabularyWarning)
            return render(ast.Document(nodes), env, "ve_english", vocabulary=_display_overlay(overlay, env),
                          conclusions=tuple(i for i, mark in enumerate(marks) if mark)).rstrip("\n")
    except (VEError, KeyError, TypeError, ValueError) as exc:
        raise CheckerUnavailable(f"CheckerUnavailable: a reading could not be rendered: {exc}") from exc


def _rendered(projection: dict, candidate: dict, overlay: dict | None) -> str:
    return _render(projection["environment"], [candidate["formula"]], [candidate["mark"]], overlay)


def reread(env, packs: list[bytes], source: str, sentence: int, index: int, text: str, *, own=None,
           overlay=None) -> bool:
    """Whether Lean's senses reader reads `text` under the projection of candidate `index` of the unit at
    `sentence` of `source`, from the state before that unit, to exactly that candidate's formula and mark (Lean's
    `reread` outcome `same`). `unknown` (the budget ended) and `different` are not."""
    answer = route.read(env, source, packs, own=own, overlay=overlay, reread=(sentence, index, text))["reading"]
    return answer.get("reread", {}).get("outcome") == "same"


def body(env, packs: list[bytes], source: str, reading: dict, *, own=None, overlay=None) -> str | None:
    """The checked text of a reading with status `one` (plan 2.8): Lean's preamble lines, then Python's rendering of
    the body's formulas under the reading's projected environment, returned only when Lean reads that document back
    to one reading of the same formulas and marks under a projection with the same identities. None for any other
    status, and for a body whose sense map has a switched occurrence: the renderer has no wording for a sense with
    its gloss (sn-b7c), so it renders none rather than one Lean refuses."""
    if reading.get("status") != "one" or not all(o["is_default"] for o in reading["sense_map"]):
        return None
    units = reading["units"]
    text = "\n".join([*reading["preamble"], _render(reading["environment"], [u["formula"] for u in units],
                                                    [u["mark"] for u in units], overlay)])
    again = route.read(env, text, packs, own=own, overlay=overlay)["reading"]
    if (again["status"] != "one" or len(again["units"]) != len(units)
            or not all(a.get("formula") == u["formula"] and a.get("mark") is u["mark"]
                       for a, u in zip(again["units"], units))
            or any(again["identities"][key] != reading["identities"][key] for key in route.PROJECTION_IDS)):
        raise CheckerUnavailable("CheckerUnavailable: the rendered text does not re-read to the reading")
    return text


def candidates(env, packs: list[bytes], source: str, reading: dict, *, own: list[dict] | None = None,
               overlay: dict | None = None) -> list[dict]:
    """Each candidate of each open unit of a relayed `senses.read` reading of `source`: its sentence, its position,
    Lean's resolving lines, those of them the document's preamble lacks, and its English, rendered under the
    projection of its lines and re-read by Lean under the same projection. A projection whose identities are not
    the ones the reading lists for the candidate (i7), or a rendering Lean does not read back, is
    `CheckerUnavailable`."""
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
            if not reread(env, packs, source, unit["sentence"], index, text, own=own, overlay=overlay):
                raise CheckerUnavailable("CheckerUnavailable: a candidate's rendering does not re-read under its "
                                         "projection")
            rows.append({"sentence": unit["sentence"], "candidate": index, "lines": lines,
                         "lacking": [line for line in lines.split("\n") if line not in reading["preamble"]],
                         "text": text})
    return rows


def _written(source: str, occurrence: dict) -> str:
    """The source text of a sense-map occurrence: the bytes of its Lean span (`byte_start`, `byte_stop`)."""
    return source.encode("utf-8")[occurrence["byte_start"]:occurrence["byte_stop"]].decode("utf-8")


def _description(reading: dict, symbol: str) -> str:
    try:
        return reading["environment"]["vocabulary"]["predicates"][symbol]["description"]
    except (KeyError, TypeError) as exc:
        raise CheckerUnavailable("CheckerUnavailable: a sense of the sense map is not in the projected "
                                 "environment") from exc


def hover(source: str, reading: dict) -> list[dict]:
    """The hover rows (plan 2.8), one per sense-map entry in Lean's order: its byte span, sentence, sense, gloss,
    the projected sense's description, whether it is the default, and the candidate of an open unit it belongs
    to."""
    if "sense_map" not in reading:
        return []
    return [{"byte_start": o["byte_start"], "byte_stop": o["byte_stop"], "sentence": o["sentence"],
             "symbol": o["symbol"], "gloss": o["gloss"], "description": _description(reading, o["symbol"]),
             "is_default": o["is_default"], **({"candidate": o["candidate"]} if "candidate" in o else {})}
            for o in reading["sense_map"]]


def glossary(source: str, reading: dict) -> dict:
    """The glossary (plan 2.8): one row per sense the resolved occurrences of the sense map use, in Lean's order,
    with its first occurrence as written (the source bytes of its span), its gloss and description, whether it is
    the default, and the sentences it occurs in; then Lean's unused defaults."""
    rows: dict[str, dict] = {}
    for o in reading.get("sense_map", ()):
        if "candidate" in o:
            continue
        row = rows.setdefault(o["symbol"], {"symbol": o["symbol"], "written": _written(source, o),
                                            "gloss": o["gloss"], "description": _description(reading, o["symbol"]),
                                            "is_default": o["is_default"], "sentences": []})
        if o["sentence"] not in row["sentences"]:
            row["sentences"].append(o["sentence"])
    return {"senses": list(rows.values()), "unused": list(reading.get("unused", ()))}


def propose_readings(env, packs: list[bytes], source: str, reading: dict, *, own=None, overlay=None) -> dict:
    """The reading sets of an open reading (plan B7, 2.6 step 7): one `open` set per open unit with two or more
    candidates whose every pair has Lean's distinguishing flip model, one reading per candidate (its formula,
    `admission.who` `senses`, `why` the unit's Lean text, the flip models by id), validated by the existing readings
    validation over the reading's projected environment; each reading's text is its candidate's checked rendering.
    A one-candidate unit gets no set: its row gives the lines it lacks and Lean's text. A unit with a pair Lean
    does not distinguish gets no set either (`undistinguished`, with Lean's flip statuses)."""
    if reading.get("status") != "open":
        return {"reading_sets": [], "texts": [], "resolving": [], "undistinguished": []}
    shown = {(row["sentence"], row["candidate"]): row for row in candidates(env, packs, source, reading, own=own,
                                                                            overlay=overlay)}
    projected = Environment(reading["environment"])
    flips = {(f["sentence"], f["first"], f["second"]): f for f in reading["flips"]}
    sets, texts, resolving, undistinguished = [], [], [], []
    for unit in reading["units"]:
        sentence, count = unit["sentence"], len(unit["candidates"])
        if count == 0:
            continue
        if count == 1:
            resolving.append({"sentence": sentence, "lacking": shown[(sentence, 0)]["lacking"],
                              "text": unit["text"]})
            continue
        pairs = {(i, j): flips.get((sentence, i, j)) for i in range(count) for j in range(i + 1, count)}
        if not all(f is not None and f["status"] == "distinguished" for f in pairs.values()):
            undistinguished.append({"sentence": sentence, "flips": [
                [i, j, None if f is None else f["status"]] for (i, j), f in pairs.items()]})
            continue
        try:
            models = {pair: (FiniteModel.from_dict(projected, f["model"]).model_id, f["model"])
                      for pair, f in pairs.items()}
            ids = [f"candidate-{i}" for i in range(count)]
            readings = [{"id": ids[i], "kind": "asserted",
                         "meaning_id": meaning_id(projected, ast.formula_from_data(projected, c["formula"])),
                         "content": c["formula"],
                         "admission": {"who": "senses", "why": unit["text"], "distinguishing_models": {
                             ids[j]: models[(min(i, j), max(i, j))][0] for j in range(count) if j != i}}}
                        for i, c in enumerate(unit["candidates"])]
        except (VEError, KeyError, TypeError, ValueError) as exc:
            raise CheckerUnavailable(f"CheckerUnavailable: a flip model or candidate is unusable: {exc}") from exc
        set_id = f"senses-{sentence}"
        sets.append({"id": set_id, "unit": str(sentence), "version": 1, "status": "open", "readings": readings,
                     "models": {model_id: model for model_id, model in models.values()}})
        texts += [{"set": set_id, "reading": ids[i], **{k: shown[(sentence, i)][k] for k in ("lines", "text")}}
                  for i in range(count)]
    try:
        validate_reading_sets(projected, sets, {str(unit["sentence"]) for unit in reading["units"]})
    except VEError as exc:
        raise CheckerUnavailable(f"CheckerUnavailable: the readings validation refused a proposed set: {exc}") from exc
    return {"reading_sets": sets, "texts": texts, "resolving": resolving, "undistinguished": undistinguished}
