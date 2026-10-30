"""SC-1b: the Lean document mode admits `scope@0` (docs/spec/scope.md 5.2, 7.2) on the F1 part document, the pinned
constitution's hard-constraint block (u0164.s01-u0166.s01) rewritten with the lead-in's part and seven item parts.
Lean governs and folds the statuses; Python relays the case and builds the document from the bound answer (R8)."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from ve import document as D
from ve.backends.relay import answer

F1 = Path(__file__).parent / "data/scope/hard-constraints.scope.md"
ITEMS = [f"u0165.s0{i}" for i in range(1, 8)]


def _split(text: str):
    front, body = text[4:].split("\n---\n", 1)
    return json.loads(front), body


def _text(meta: dict, body: str) -> str:
    return "---\n" + json.dumps(meta, ensure_ascii=False) + "\n---\n" + body


def _rows(text: str):
    row, error = answer("document", {"id": "d", "document": text, "admit": True})
    return ({u["id"]: u for u in row["units"]}, row) if error is None else (None, str(error))


def _written_in_full(meta: dict) -> dict:
    """The block as the translation writes it today: each rule in full, no lead-in part, no scope@0."""
    meta = json.loads(json.dumps(meta))
    lead = meta.pop("scope")["governors"][0]["effect"]["frame"]
    meta["environment"]["profiles"].remove("scope@0")
    for unit in meta["units"]:
        if "part" in unit.get("content", {}):
            unit["content"] = {"norm": {**unit["content"]["part"], **lead}}
        if unit["id"] == "u0164.s02":
            unit.update(kind=["unformalised", "norms"], meaning={"unformalised": "norms"})
    return meta


def test_f1_doc_the_lead_in_takes_its_items_status_and_each_item_is_its_rule_in_full():
    meta, body = _split(F1.read_text())
    rows, _ = _rows(F1.read_text())
    today, _ = _rows(_text(_written_in_full(meta), body))
    assert rows["u0164.s02"]["status"] == "OPEN" and today["u0164.s02"]["status"] == "UNFORMALISED"
    assert all(rows[u] == today[u] for u in ITEMS)  # the seven rows byte for byte, statuses OPEN
    assert {rows[u]["status"] for u in ITEMS} == {"OPEN"}


def test_f1_bad_an_item_not_admitted_leaves_the_lead_in_unformalised():
    meta, body = _split(F1.read_text())
    unit = next(u for u in meta["units"] if u["id"] == "u0165.s02")
    unit.pop("content")
    unit.update(kind=["unformalised", "norms"], meaning={"unformalised": "norms"})
    rows, row = _rows(_text(meta, body))
    assert rows["u0164.s02"]["status"] == "UNFORMALISED"
    assert row["coverage"]["bytes_by_status"] == {"OPEN": 896 - 139 - 22, "UNFORMALISED": 472 + 139 + 22}


def test_f1_off_without_scope_the_document_is_answered_as_before():
    meta, body = _split(F1.read_text())
    meta["environment"]["profiles"].remove("scope@0")
    assert _rows(_text(meta, body))[1] == "unknown document metadata"
    del meta["scope"]
    assert _rows(_text(meta, body))[1] == "unit fence must match its id"


@pytest.mark.parametrize("profiles, text", [
    (["alternatives@0", "norms@0", "relational-fol@0", "scope@0"], "UnsupportedProfile: scope@0 with alternatives@0"),
    (["relational-fol@0", "scope@0"], "UnsupportedProfile: scope@0 requires norms@0")])
def test_the_profile_tables_scope_row_refuses_first(profiles, text):
    meta, body = _split(F1.read_text())
    meta["environment"]["profiles"] = profiles
    assert _rows(_text(meta, body))[1] == text


def test_ve_document_check_builds_the_governed_document_from_the_bound_answer(tmp_path):
    path = tmp_path / "f1.ve.md"
    path.write_text(F1.read_text())
    units = {u["id"]: u for u in D.load_document(path)["units"]}
    assert units["u0164.s02"]["status"] == "OPEN"
    assert [units[u]["content"]["norm"]["name"] for u in ITEMS[:2]] == ["hc-cbrn-uplift", "hc-infrastructure-uplift"]
    assert D.check_document(path)["coverage"]["bytes_by_status"] == {"OPEN": 896, "UNFORMALISED": 472}


def test_every_structural_mutant_of_the_f1_answer_is_refused(tmp_path, monkeypatch):
    """The scope@0 answer is typed and bound as every document answer (R8): each one-fault structural mutant of the
    genuine F1 row (a member dropped or added, a list element dropped or duplicated, a value retyped) is refused by
    the response schema or by the binding, never relayed into a document."""
    accepted, count = structural_mutants_accepted(tmp_path, monkeypatch, F1.read_text())
    assert count > 200 and not accepted, accepted


def structural_mutants_accepted(tmp_path, monkeypatch, text, bind_unit="u0164.s02"):
    """The one-fault mutants of a scope@0 document's genuine row that the schema and the binding let through."""
    from tests.test_document_lean_switch import _structural_mutants
    from ve.backends import relay
    from ve.backends.lean_service import CheckerUnavailable
    from ve.backends.service_schema import ROWS, Context, Invalid
    path = tmp_path / "f1.ve.md"
    path.write_text(text)
    case = {"id": "document", "document": path.read_text(), "admit": True}
    row = D._lean_answer(path.read_bytes(), True)
    lead = next(i for i, u in enumerate(row["units"]) if u["id"] == bind_unit)
    rebound = [(("rename", "absent"), lambda r: r["units"][lead].update(id="absent")),
               (("span", "+1"), lambda r: r["units"][lead].update(span=[n + 1 for n in r["units"][lead]["span"]])),
               (("extra",), lambda r: r["units"].append({**r["units"][lead], "id": "u9999.s01"})),
               (("source_id",), lambda r: r.update(source_id="0" * 64))]
    accepted, count = [], 0
    for where, mutate in [*_structural_mutants(row), *rebound]:
        mutant = json.loads(json.dumps(row))
        mutate(mutant)
        count += 1
        try:
            ROWS["document"][0](mutant, Context(case), {})
        except Invalid:
            continue
        monkeypatch.setattr(relay, "answer", lambda mode, case, mutant=mutant: (mutant, None))
        try:
            D.check_document(path)
        except CheckerUnavailable:
            continue
        accepted.append(where)
    return accepted, count


# ------------------------------------------------------------------- sc-1b review F1: governed rules are relayed
# Lean's govern rewrites the content of every rule unit a governor affects (`VE.Scope.patch`), on every chain the
# profile table admits under scope@0. The relay binds each governed rule to the request's members and Lean's meaning
# id, never to the rule as written, and builds every container from the governed units. Each effect of the wire
# (read from Lean's decoder, so a new effect fails here until it has a case) on each chain: plain norms, soft norms
# and rights.

WIRE = Path(__file__).resolve().parents[1] / "lean/VE/Scope/Wire.lean"
CHAINS = {"norms": ["norms@0", "relational-fol@0"],
          "soft-norms": ["norms@0", "relational-fol@0", "soft-norms@0"],
          "rights": ["norms@0", "relational-fol@0", "rights@0", "soft-norms@0"]}
OWN = ["and", "own", ["top"]]
FRAME = {"predicate": "protect_required", "sign": True, "unless": [], "over": []}
COMPOSED = ["and", ["top"], ["top"]]
# Each effect's governor over the list u1-u3 (rules a, b, c on one predicate) and what Lean answers per rule:
# (guard, unless, over).
EFFECTS = {
    "frame": ({"unit": "u0", "reach": {"list": "u0"}, "units": ["u1", "u2", "u3"], "effect": {"frame": FRAME}}, {}),
    "title": ({"unit": "u2", "reach": {"label": "u2"}, "units": ["u2"], "effect": "title"}, {}),
    "reguard": ({"unit": "u1", "reach": {"rules": ["b"]}, "units": ["u2"], "effect": {"reguard": OWN}},
                {"b": (COMPOSED, [], [])}),
    "carve_out": ({"unit": "u1", "reach": {"rules": ["b"]}, "units": ["u2"], "effect": {"carve_out": OWN}},
                  {"b": (["top"], [COMPOSED], [])}),
    "precedes": ({"unit": "u1", "reach": {"rules": ["b"]}, "units": ["u2"], "effect": "precedes"},
                 {"a": (["top"], [], ["b"])}),
    "yields": ({"unit": "u1", "reach": {"rules": ["b"]}, "units": ["u2"], "effect": "yields"},
               {"b": (["top"], [], ["a"])})}


def _wire_effects() -> set:
    """The effect names `VE.Scope.decodeEffect` reads."""
    text = WIRE.read_text()
    body = text[text.index("def decodeEffect"):text.index("def decodeGovernor")]
    return set(re.findall(r'\.str "(\w+)" =>', body)) | set(re.findall(r'\[\("(\w+)", \w\)\] =>', body))


def _governed_text(chain: str, effect: str) -> str:
    """A list of three rules under a lead-in (each a part under a frame), with a right after it on the rights chain,
    and one governor."""
    from tests.test_rights import right, rights_env
    env = rights_env()
    env["profiles"] = sorted(CHAINS[chain] + ["scope@0"])
    if chain != "rights":
        del env["vocabulary"]["rights"]
    lines = [("u0", "The rules:\n", None)] + [
        (f"u{i}", f"- **Rule {n}:** Unit {n}.\n",
         {"part": {"name": n, "guard": ["top"]}} if effect == "frame" else {"norm": {"name": n, **FRAME, "guard": ["top"]}})
        for i, n in ((1, "a"), (2, "b"), (3, "c"))]
    if chain == "rights":
        lines.append(("u4", "\nThe right.\n", right()))
    units, start = [], 0
    for uid, line, content in lines:
        end = start + len(line.encode())
        units.append({"id": uid, "span": [start, end], "support": "none",
                      **({"kind": next(iter(content)) if "part" not in content else "norm", "meaning": "specified",
                          "content": content} if content else
                         {"kind": ["unformalised", "norms"], "meaning": {"unformalised": "norms"}})})
        start = end
    meta = {"format": "ve-document@1", "environment": env, "units": units,
            "scope": {"version": "scope@0", "governors": [{"id": "g1", **EFFECTS[effect][0]}]}}
    return _text(meta, "".join(line for _, line, _ in lines))


def test_every_effect_of_the_wire_has_a_governed_case():
    assert _wire_effects() == set(EFFECTS) == {"frame", "title", "reguard", "carve_out", "precedes", "yields"}


def test_f1_probe_a_carve_out_over_a_rule_name_on_the_pilot_document(tmp_path):
    """The review's probe: a carve-out by rule name over a rule written in full is Lean's `ok`, relayed."""
    meta, body = _split(F1.read_text())
    meta = _written_in_full(meta)
    meta["environment"]["profiles"] = sorted(meta["environment"]["profiles"] + ["scope@0"])
    meta["scope"] = {"version": "scope@0", "governors": [
        {"id": "g1", "unit": "u0166.s01", "reach": {"rules": ["hc-cbrn-uplift"]}, "units": ["u0165.s01"],
         "effect": {"carve_out": "own"}}]}
    path = tmp_path / "c.ve.md"
    path.write_text(_text(meta, body))
    assert D.check_document(path)["coverage"]
    units = {u["id"]: u for u in D.load_document(path)["units"]}
    assert units["u0165.s01"]["content"]["norm"]["unless"] == [meta["units"][2]["content"]["norm"]["guard"]]


@pytest.mark.parametrize("effect", sorted(EFFECTS))
@pytest.mark.parametrize("chain", sorted(CHAINS))
def test_each_effect_is_relayed_on_each_chain_and_its_containers_hold_the_governed_rules(tmp_path, chain, effect):
    path = tmp_path / "g.ve.md"
    path.write_text(_governed_text(chain, effect))
    rows, row = _rows(path.read_text())
    assert rows is not None, row
    doc = D.load_document(path)
    assert [u.get("content") for u in doc["units"]] == [u.get("content") for u in row["units"]]
    answered = {u["content"]["norm"]["name"]: u["content"]["norm"] for u in row["units"]
                if "norm" in (u.get("content") or {})}
    assert set(answered) >= {"a", "b", "c"}
    for name in ("a", "b", "c"):
        guard, unless, over = EFFECTS[effect][1].get(name, (["top"], [], []))
        assert (answered[name]["guard"], answered[name]["unless"], answered[name]["over"]) == (guard, unless, over)
    container = doc["soft_document"] or doc["norms"]
    held = {getattr(r, "core", r).name: getattr(r, "core", r).to_dict()["norm"] for r in container.rules}
    assert {n: [held[n][k] for k in ("guard", "unless", "over")] for n in answered} == \
        {n: [r[k] for k in ("guard", "unless", "over")] for n, r in answered.items()}
    assert D.check_document(path)["coverage"]["bytes_by_status"]
    assert "Rule b" in D.render_document(path)


@pytest.mark.parametrize("chain, effect", [("norms", "carve_out"), ("soft-norms", "precedes"), ("rights", "frame")])
def test_every_mutant_of_a_governed_rule_is_refused(tmp_path, monkeypatch, chain, effect):
    """R8 on the governed units: each one-fault structural mutant of every unit's content in a genuine governed
    answer (a member dropped or added, a list element dropped or duplicated, a value retyped) is refused by the
    response schema or the binding, never relayed into a document."""
    from tests.test_document_lean_switch import _structural_mutants
    from ve.backends import relay
    from ve.backends.lean_service import CheckerUnavailable
    from ve.backends.service_schema import ROWS, Context, Invalid
    path = tmp_path / "g.ve.md"
    path.write_text(_governed_text(chain, effect))
    case = {"id": "document", "document": path.read_text(), "admit": True}
    row = D._lean_answer(path.read_bytes(), True)
    mutants = [m for i, u in enumerate(row["units"]) if "content" in u
               for m in _structural_mutants(u["content"], ("units", i, "content"))]
    mutants += [(("units", i, "content", "-"), lambda r, i=i: r["units"][i].pop("content"))
                for i, u in enumerate(row["units"]) if "content" in u]
    accepted = []
    for where, mutate in mutants:
        mutant = json.loads(json.dumps(row))
        mutate(mutant)
        try:
            ROWS["document"][0](mutant, Context(case), {})
        except Invalid:
            continue
        monkeypatch.setattr(relay, "answer", lambda mode, case, mutant=mutant: (mutant, None))
        try:
            D.check_document(path)
        except CheckerUnavailable:
            continue
        accepted.append(where)
    assert len(mutants) > 100 and not accepted, accepted


@pytest.mark.parametrize("unit, forge", [
    ("u3", lambda c: c["norm"].update(over=["a"])),     # a rule the block does not name keeps its rule as written
    ("u2", lambda c: c.update(cites={})),               # a governed rule keeps the authored members
    ("u2", lambda c: c.update(norm=[c["norm"]]))])      # and its rule is an object
def test_a_forged_rule_with_its_meaning_id_recomputed_is_refused(tmp_path, monkeypatch, unit, forge):
    """Two faults at once: the content and the meaning id that hashes it. A rule the block names (u1, u2) is bound to
    the authored members, its rule Lean's composition (which named rules a governor changes is Lean's `affected`,
    not recomputed here); every other rule (u3) is bound as written."""
    from ve.backends import relay
    from ve.backends.lean_service import CheckerUnavailable
    from ve.wire import digest
    path = tmp_path / "g.ve.md"
    path.write_text(_governed_text("norms", "carve_out"))
    row = D._lean_answer(path.read_bytes(), True)
    env = D.load_document(path)["environment"]
    target = next(u for u in row["units"] if u["id"] == unit)
    forge(target["content"])
    target["meaning_id"] = digest(f"ve-meaning-{env.identity_version}\n",
                                  {"environment_id": env.environment_id, "ast": target["content"]})
    monkeypatch.setattr(relay, "answer", lambda mode, case: (row, None))
    with pytest.raises(CheckerUnavailable, match="not bound to the document sent"):
        D.check_document(path)


def test_a_governed_soft_rule_not_in_its_containers_form_is_refused(tmp_path, monkeypatch):
    """On the soft chain a governed rule is bound in the form its container holds, as every soft rule Lean answers
    (`_soft_bound`): a strict mode written out, with the meaning id recomputed, is not that form."""
    from ve.backends import relay
    from ve.backends.lean_service import CheckerUnavailable
    from ve.document.containers import _content_environment
    from ve.readings import rights_meaning_id
    path = tmp_path / "g.ve.md"
    path.write_text(_governed_text("soft-norms", "carve_out"))
    row = D._lean_answer(path.read_bytes(), True)
    doc = D.load_document(path)
    target = next(u for u in row["units"] if u["id"] == "u2")
    target["content"]["norm"]["mode"] = "strict"
    target["meaning_id"] = rights_meaning_id(
        _content_environment(doc["environment"], doc["soft_document"].extended_env, "norm"), target["content"])
    monkeypatch.setattr(relay, "answer", lambda mode, case: (row, None))
    with pytest.raises(CheckerUnavailable, match="not bound to the document sent"):
        D.check_document(path)


# ------------------------------------------------------------- sc-1b recheck F6: the proposal's environment
# The lexicon proposal a case with English fences carries names the environment Lean's chain reads the fences in:
# the environment without the `scope@0` wrapper (`chain_environment`, Lean's `lowerScope`), on every chain. Where
# that environment is one the relay cannot build before Lean answers (the soft route's `E″` of governed rules), Lean's
# refusal of the proposal is a fault of the case sent: `CheckerUnavailable`, never the document's diagnostic.

PROBE_F6 = Path(__file__).parent / "data/readings_s2/constitution-nd-readings.ve.md"
SENTENCE = "Every person may act."
UNSTATED = {"decided_by": "unstated", "sufficient": [], "necessary": [], "factors": []}


def _with_english(text: str) -> str:
    """The document with an English unit at its end, its fence after its line."""
    meta, body = _split(text)
    start, line = len(body.encode()), SENTENCE + "\n"
    meta["units"].append({"id": "u9", "span": [start, start + len(line.encode())], "support": "assumption",
                          "kind": "asserted", "meaning": "specified", "content": {"fence": "u9"},
                          "surface": "english"})
    return _text(meta, body + line + f"```ve u9\n{SENTENCE}\n```\n")


def _defaults(text: str, governed: bool = True) -> str:
    """The frame document with each rule a default; without `scope@0`, each rule written in full."""
    meta, body = _split(text)
    for unit in meta["units"]:
        content = unit.get("content") or {}
        if "part" in content:
            content["part"].update(mode="default", exception=json.loads(json.dumps(UNSTATED)))
            if not governed:
                unit["content"] = {"norm": {**FRAME, **content.pop("part")}}
    if not governed:
        del meta["scope"]
        meta["environment"]["profiles"].remove("scope@0")
    return _text(meta, body)


def test_f6_probe_an_english_fence_under_scope_is_read_on_the_environment_without_it(tmp_path):
    """The review's probe: an English fence of a `scope@0` document is read with the proposal of the environment
    without `scope@0`, and the document is answered as without it."""
    meta, body = _split(PROBE_F6.read_text())
    plain = tmp_path / "plain.ve.md"
    plain.write_text(PROBE_F6.read_text())
    meta["environment"]["profiles"] = sorted(meta["environment"]["profiles"] + ["scope@0"])
    meta["scope"] = {"version": "scope@0", "governors": []}
    path = tmp_path / "s.ve.md"
    path.write_text(_text(meta, body))
    assert D.check_document(path)["coverage"]["bytes_by_status"] == {"CHECKED": 23, "OPEN": 359} == \
        D.check_document(plain)["coverage"]["bytes_by_status"]
    fence, = (u for u in D.load_document(path)["units"] if u["id"] == "u0248")
    assert fence["status"] == "CHECKED"
    assert fence["content"] == next(u for u in D.load_document(plain)["units"] if u["id"] == "u0248")["content"]
    assert D.render_document(path)


@pytest.mark.parametrize("effect", sorted(EFFECTS))
@pytest.mark.parametrize("chain", ["norms", "soft-norms"])
def test_each_chain_reads_an_english_fence_under_scope_with_the_proposal_of_its_environment(tmp_path, chain, effect):
    """Every chain whose fences the mode reads, and every effect: the proposal names the environment the answer is
    bound to (the soft route's `E″` on the soft chain), and the fence is read."""
    path = tmp_path / "g.ve.md"
    path.write_text(_with_english(_governed_text(chain, effect)))
    case = D._document_case(path.read_bytes(), True)
    doc = D.load_document(path)
    words = doc["soft_document"].extended_env if chain == "soft-norms" else doc["environment"]
    assert case["lexicon"]["environment_id"] == words.environment_id
    fence, = (u for u in doc["units"] if u["id"] == "u9")
    assert fence["status"] == "CHECKED" and fence["content"]
    assert D.check_document(path)["coverage"]["bytes_by_status"]["CHECKED"]


def test_a_rights_documents_fence_is_left_to_the_retained_path_which_refuses_scope(tmp_path):
    """The mode leaves formula content in a rights document to the retained path, with or without `scope@0`; that
    path refuses `scope@0` at the environment (DELTA row 3(e)), never a Python verdict on it."""
    from ve.backends.relay import answer
    from ve.errors import UnsupportedProfile
    text = _with_english(_governed_text("rights", "carve_out"))
    _, error = answer("document", D._document_case(text.encode(), True))
    assert str(error) == "CheckerUnavailable: formula content in a rights document is typed in its extended environment"
    path = tmp_path / "r.ve.md"
    path.write_text(text)
    with pytest.raises(UnsupportedProfile, match="Unsupported profile scope@0"):
        D.load_document(path)


def test_a_proposal_lean_reads_in_another_environment_is_unavailable_never_the_documents_diagnostic(tmp_path):
    """The soft chain under a frame over default rules: Lean reads the fence in the `E″` of the governed rules, whose
    decisions the proposal built from the rules as written does not have. The same rules written in full are
    checked, so the refusal is the relay's, not the document's."""
    from ve.backends.lean_service import CheckerUnavailable
    governed = _with_english(_governed_text("soft-norms", "frame"))
    full = tmp_path / "full.ve.md"
    full.write_text(_defaults(governed, governed=False))
    assert next(u for u in D.load_document(full)["units"] if u["id"] == "u9")["status"] == "CHECKED"
    path = tmp_path / "g.ve.md"
    path.write_text(_defaults(governed))
    for run in (D.load_document, D.check_document):
        with pytest.raises(CheckerUnavailable, match="another environment than the lexicon proposal"):
            run(path)


def test_any_proposal_for_another_environment_is_unavailable(tmp_path, monkeypatch):
    """The class on a document without `scope@0`: a proposal naming another environment than the chain's is the
    case's fault, whatever made it so."""
    from ve.backends.lean_service import CheckerUnavailable
    from ve.document import lean
    case_of = lean._document_case

    def elsewhere(*args, **kwargs):
        case = case_of(*args, **kwargs)
        case["lexicon"]["environment_id"] = "0" * 64
        return case
    path = tmp_path / "n.ve.md"
    path.write_text(_with_english(_governed_text("norms", "title")))
    D.check_document(path)
    monkeypatch.setattr(lean, "_document_case", elsewhere)
    with pytest.raises(CheckerUnavailable, match="another environment than the lexicon proposal"):
        D.check_document(path)


def test_the_proposal_refusal_is_leans_text():
    """The text the relay reads as a refusal of its proposal is the one `decodeLexicon` throws."""
    from ve.document.lean import PROPOSAL_ELSEWHERE
    text = (Path(__file__).resolve().parents[1] / "lean/VE/EnglishGrammar/Run.lean").read_text()
    body = text[text.index("def decodeLexicon"):text.index("theorem riskView_eq")]
    assert f'throw "{PROPOSAL_ELSEWHERE}"' in body
