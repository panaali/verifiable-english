"""Synthetic smoke cases written by the translator BEFORE the encoder file was opened (hand-worked expectations in
test_smoke.py). Not questions of the corpus; never counted."""
CASES = [
 {"id": "X1", "txns": ["t"], "persons": ["a"], "facts": {"t": ["freehold", "allres", "usedsingle", "landtxn"], "a": ["individual"]},
  "pt": [("acquires", "a", "t"), ("intends", "a", "t")], "ints": {"cons_t": "400000.00"},
  "questions": [{"qid": "X1-1", "item": "t", "form": "taxnr"}, {"qid": "X1-2", "item": "t", "form": "claim"}, {"qid": "X1-3", "item": "t", "form": "taxr"}]},
 {"id": "X2", "txns": ["t", "p"], "persons": ["a"], "facts": {"t": ["lease", "allres", "usedsingle", "landtxn"], "p": ["freehold", "usedsingle", "abroad", "equivalent"], "a": ["individual"]},
  "pt": [("acquires", "a", "t"), ("intends", "a", "t"), ("acquires", "a", "p")], "links": [("earlier", "p", "t")], "ints": {"cons_t": "1600000.00", "years_t": "99"},
  "questions": [{"qid": "X2-1", "item": "t", "form": "taxnr"}, {"qid": "X2-2", "item": "t", "form": "claim"}, {"qid": "X2-3", "item": "t", "form": "taxr"}]},
 {"id": "X3", "txns": ["t", "g"], "persons": ["a"], "facts": {"t": ["freehold", "allres", "usedsingle", "landtxn"], "g": ["freehold", "allres", "landtxn"], "a": ["individual"]},
  "pt": [("acquires", "a", "t"), ("intends", "a", "t"), ("acquires", "a", "g")], "links": [("linked", "t", "g"), ("linked", "g", "t"), ("gardenof", "g", "t")], "ints": {"cons_t": "300000.00", "cons_g": "100000.00"},
  "questions": [{"qid": "X3-1", "item": "t", "form": "taxnr"}, {"qid": "X3-2", "item": "t", "form": "claim"}, {"qid": "X3-3", "item": "g", "form": "claim"}, {"qid": "X3-4", "item": "t", "form": "taxr"}]},
 {"id": "X4", "txns": ["t"], "persons": ["a"], "facts": {"t": ["freehold", "usedsingle", "landtxn"], "a": ["individual"]},
  "pt": [("acquires", "a", "t"), ("intends", "a", "t")], "ints": {"cons_t": "260000.00"},
  "questions": [{"qid": "X4-1", "item": "t", "form": "taxnr"}]},
 {"id": "X5", "txns": ["t"], "persons": ["a"], "facts": {"t": ["freehold", "allres", "usedsingle", "landtxn", "extraland", "extragarden"], "a": ["individual"]},
  "pt": [("acquires", "a", "t"), ("intends", "a", "t")], "ints": {"cons_t": "350000.00"},
  "questions": [{"qid": "X5-1", "item": "t", "form": "claim"}, {"qid": "X5-2", "item": "t", "form": "taxr"}]},
 {"id": "X6", "txns": ["t", "p"], "persons": ["a"], "facts": {"t": ["freehold", "allres", "usedsingle", "landtxn"], "p": ["lease", "usedsingle", "abroad", "equivalent"], "a": ["individual"]},
  "pt": [("acquires", "a", "t"), ("intends", "a", "t"), ("acquires", "a", "p")], "links": [("earlier", "p", "t")], "ints": {"cons_t": "250000.00", "years_p": "20"},
  "questions": [{"qid": "X6-1", "item": "t", "form": "claim"}, {"qid": "X6-2", "item": "t", "form": "taxr"}]},
]
SMOKE_EXTRA = None
PROBES = {}
PROBE_QIDS = {}
UNSUPPORTED = {}
