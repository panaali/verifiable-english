"""Rights rendering must describe the checked unit status accurately."""

from tests.test_rights import claim, life_limitation, right, rights_document_file
from ve.document import load_document, render_document


def test_open_default_right_and_limitation_render_without_checked_label(tmp_path):
    line = claim()
    line["norm"].update(mode="default", exception={"decided_by": "unstated",
                         "sufficient": [], "necessary": [], "factors": []})
    path = rights_document_file(tmp_path, [right([line]), life_limitation()])
    assert [u["status"] for u in load_document(path)["units"]] == ["OPEN", "OPEN"]
    rendered = render_document(path)
    assert rendered.count("Open reading: ") == 2
    assert "Checked reading: " not in rendered


def test_open_bar_unit_renders_without_checked_label(tmp_path):
    liberty = {"kind": "liberty", "holder_slot": None, "cites": {},
               "norm": {"name": "may-act", "predicate": "person_may_act", "sign": True,
                        "guard": ["top"], "unless": [], "over": []}}
    bar = {"bar": {"name": "b30", "reading": "rule", "decided_by": "unstated"}}
    path = rights_document_file(tmp_path, [right([liberty]), bar])
    assert [u["status"] for u in load_document(path)["units"]] == ["OPEN", "OPEN"]
    rendered = render_document(path)
    assert rendered.count("Open reading: ") == 2
    assert "Checked reading: " not in rendered
