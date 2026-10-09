"""Regression for the reserved main component name in the readings split."""

from tests.test_readings_companions_lean import alone, components, env_main, lean, merged, own, set_a, set_b
from tests.test_readings_nd_lean import one


def test_companion_set_cannot_claim_the_main_component(lean):
    """The split must have unique component names before any kind dispatches a named component."""
    rs, sid, companion_env = set_a(set_id="main")
    document = {"units": [{"id": "u_a"}], "reading_sets": [rs]}
    expected = "InvalidInput: reading set main conflicts with the reserved component name"
    # The original counterexample: the same readings work when written as a document of their own.
    standalone = one(lean, "readings-separate", merged(companion_env),
                     alone(rs, [{"id": "u_a"}]), set="main", situation=sid, other="asks")
    assert standalone["status"] == "ok" and standalone["pair"]["separated"] is True
    for kind in ("readings-validate", "readings-elaborate", "readings-separate", "readings-choice",
                 "readings-conflict", "readings-certificate", "readings-model", "readings-dead"):
        for component in (None, "main"):
            fields = {} if component is None else {"component": component}
            row = one(lean, kind, env_main(), document, **fields)
            assert row["status"] == "error" and row["error"] == expected, (kind, component, row)
    other, _, _ = set_b()
    document["units"].append({"id": "u_b"})
    document["reading_sets"].insert(0, other)
    assert one(lean, "readings-validate", env_main(), document, component="rs_b")["error"] == expected
    # A plain set called main belongs to the document component and creates no collision.
    plain = {"units": [{"id": "u_a"}], "reading_sets": [own(rs)]}
    assert one(lean, "readings-validate", merged(companion_env), plain)["status"] == "ok"
    plain["units"].append({"id": "u_b"})
    plain["reading_sets"].append(other)
    answers, order = components(one(lean, "readings-validate", merged(companion_env), plain))
    assert order == ["main", "rs_b"] and answers["main"]["status"] == "ok"
