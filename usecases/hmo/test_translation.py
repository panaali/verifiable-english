"""HMO translation tests (no VE call): AtLeast's subset form equals its literal FOL form; grounding sanity; mutants differ."""
import itertools
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import rows as R  # noqa: E402
import translation as T  # noqa: E402


def evaluate(f, val):
    h = f[0]
    if f == T.TRUE:
        return True
    if f == T.FALSE:
        return False
    if h in ("unary", "binary"):
        return val[T.key(f)]
    if h == "not":
        return not evaluate(f[1], val)
    if h == "and":
        return evaluate(f[1], val) and evaluate(f[2], val)
    if h == "or":
        return evaluate(f[1], val) or evaluate(f[2], val)
    if h == "implies":
        return (not evaluate(f[1], val)) or evaluate(f[2], val)
    raise ValueError(h)


def test_atleast_equals_fol():
    for n in range(0, 6):
        dom = {"person": [f"person{i}" for i in range(1, n + 1)]}
        for k in (2, 3, 5):
            body = R.U("occ", R.V(0))
            a = T.ground(R.AtLeast(k, "person", body), dom)
            b = T.ground(T.atleast_fol(k, "person", body), dom)
            atoms = [T.key(R.U("occ", p)) for p in dom["person"]]
            for bits in itertools.product([False, True], repeat=len(atoms)):
                val = dict(zip(atoms, bits))
                assert evaluate(a, val) == evaluate(b, val) == (sum(bits) >= k), (n, k, bits)


def test_rules_ground_and_define():
    dom = {"person": [f"person{i}" for i in range(1, 6)], "place": ["premises", "unit1"], "amenity": list(R.AMENITIES)}
    rs = T.rules(dom)
    targets = [d for r in rs for d in r["defines"]]
    assert len(targets) == len(set(targets)), "each atom fixed by one rule"
    assert any('"same_hh"' in t for t in targets) and any('"prescribed"' in t for t in targets)
    for m in T.MUTANTS:
        assert [r["formula"] for r in T.rules(dom, m)] != [r["formula"] for r in rs], m


if __name__ == "__main__":
    test_atleast_equals_fol()
    test_rules_ground_and_define()
    print("ok")
