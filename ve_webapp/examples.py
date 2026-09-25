"""Small, explicitly scoped teaching examples; no inferred real-world facts."""
from ve.environment import LANGUAGE, PROFILE, SPEC_REVISION


def example(id, title, category, english, note, sort, predicates, constants, premises, claim, true):
    env = {"language": LANGUAGE, "profile": PROFILE, "spec_revision": SPEC_REVISION,
           "vocabulary": {"sorts": {sort: {"description": f"Objects of type {sort} in this example."}},
                          "predicates": {p: {"arguments": [sort] * arity, "description": gloss}
                                         for p, arity, gloss in predicates},
                          "constants": {c: {"sort": sort, "description": gloss} for c, gloss in constants}}}
    names = [c for c, _ in constants]
    return dict(id=id, title=title, category=category, english=english, note=note, environment=env,
                premises=premises, claim=claim,
                world={"complete": True, "domains": {sort: names}, "constants": {c: c for c in names},
                       "relations": {p: true.get(p, []) for p, _, _ in predicates}})


EXAMPLES = [
    example("policy", "From a rule to a reason", "01 / POLICY", "Every reviewed service is safe. The API is reviewed. Therefore the API is safe.",
            "Safe is a declared predicate, not a security audit. Remove the review rule in the IDE to find a countermodel.",
            "service", [("reviewed", 1, "Has passed the team's review."), ("safe", 1, "Classified as safe under the stated policy.")],
            [("api", "The API service."), ("web", "The web service.")],
            "for every service x, (if (x is reviewed), then (x is safe)).\n@api is reviewed.", "@api is safe.",
            {"reviewed": [["api"]], "safe": [["api"]]}),
    example("citizenship", "Make the conditions visible", "02 / 14TH AMENDMENT",
            "All persons born or naturalized in the United States, and subject to the jurisdiction thereof, are citizens of the United States…",
            "Teaching formalisation of part of Section 1, not the full amendment or legal advice. State citizenship is omitted. The predicates leave legal interpretation explicit.",
            "person", [("born_us", 1, "Born in the United States."), ("naturalized_us", 1, "Naturalized in the United States."),
                       ("subject_jurisdiction", 1, "Subject to the jurisdiction thereof."), ("citizen_us", 1, "A citizen of the United States.")],
            [("alex", "A fictional person.")],
            "for every person p, (if (((p is born_us) or (p is naturalized_us)) and (p is subject_jurisdiction)), then (p is citizen_us)).\n@alex is born_us.\n@alex is subject_jurisdiction.",
            "@alex is citizen_us.", {"born_us": [["alex"]], "subject_jurisdiction": [["alex"]], "citizen_us": [["alex"]]}),
    example("math", "Follow a transitive relation", "03 / MATHEMATICS", "If a precedes b and b precedes c, then a precedes c, provided precedes is transitive.",
            "A relational math statement. Transitivity is an explicit assumption, not a hidden property of the word ‘precedes’.",
            "point", [("precedes", 2, "The abstract relation under study.")], [("a", "Point a."), ("b", "Point b."), ("c", "Point c.")],
            "for every point x, (for every point y, (for every point z, (if ((x precedes y) and (y precedes z)), then (x precedes z)))).\n@a precedes @b.\n@b precedes @c.",
            "@a precedes @c.", {"precedes": [["a", "b"], ["b", "c"], ["a", "c"]]}),
    example("news", "A headline can overreach", "04 / NEWS CLAIM", "One sampled district reported a drop. Did every sampled district report a drop?",
            "Fictional reporting example. A countermodel disproves the inference, not the actual headline. VE does not verify the underlying data.",
            "district", [("reported_drop", 1, "Reported a drop in the metric during the specified period.")],
            [("north", "North district."), ("south", "South district.")], "@north is reported_drop.",
            "for every district d, (d is reported_drop).", {"reported_drop": [["north"]]}),
]
BY_ID = {e["id"]: e for e in EXAMPLES}
