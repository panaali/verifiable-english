"""Generate the blinded E0 FOLIO second-rater record and check all v0 witnesses."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, "/private/tmp/ve-e0-integration")
import ve
from ve import Environment, check

ROOT = Path(__file__).resolve().parents[1]
DRAW = ROOT / "survey_samples" / "_drawn" / "folio.json"
OUT = Path(__file__).with_name("folio.jsonl")

def env(sorts, predicates, constants):
    return {
        "language": "ve.core@0", "profile": "relational-fol@0",
        "spec_revision": "ve-v0-draft-2026-09-20",
        "vocabulary": {
            "sorts": {k: {"description": v} for k, v in sorts.items()},
            "predicates": {k: {"arguments": a, "description": d} for k, (a, d) in predicates.items()},
            "constants": {k: {"sort": s, "description": d} for k, (s, d) in constants.items()},
        },
    }

def E(predicates, constants=None, sorts=None):
    sorts = sorts or {"entity": "An entity in the discourse."}
    constants = constants or {}
    return env(sorts, predicates, constants)

def item(label, constructs, rationale, source=None, environment=None, reification=None):
    return dict(label=label, construct_needed=constructs, rationale=rationale,
                formalization=source, environment=environment, reification=reification)

u = lambda d: (["entity"], d)
b = lambda d: (["entity", "entity"], d)
c = lambda d: ("entity", d)

def conjunction(parts):
    if len(parts) == 1:
        return parts[0]
    midpoint = len(parts) // 2
    return f"({conjunction(parts[:midpoint])}) and ({conjunction(parts[midpoint:])})"

def top_ten_source():
    """Top ten means that ten pairwise-distinct superheroes are not ranked above x."""
    names = [f"hero{i}" for i in range(1, 11)]
    parts = []
    for name in names:
        parts.extend((f"{name} is superhero", f"{name} ranked_above_by_america candidate"))
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            parts.append(f"not ({left} equals {right})")
    body = conjunction(parts)
    for name in reversed(names):
        body = f"there exists entity {name}, ({body})"
    top_ten = f"not ({body})"
    return f"for every entity candidate, (if ((candidate is superhero) and ({top_ten})), then (candidate speaks_language @english)).\n"

spec = {
"e773:c": item("DIRECT", ["unary predicates", "binary predicate", "constant", "universal quantification", "implication"],
 "Read distributively, every payment card issued by Bank of America is international. The gold FOL instead applies PaymentCard and International to the bank itself and loses the plurality/card relation.",
 "for every entity card, (if ((card is payment_card) and (card issued_by @bank_of_america)), then (card is international)).\n",
 E({"payment_card":u("The entity is a payment card."),"issued_by":b("The first entity is a card issued by the second entity."),"international":u("The payment card can be used internationally.")},{"bank_of_america":c("Bank of America.")})),
"e115:c": item("DIRECT", ["unary predicate", "constant"], "A unary property of a named band is in v0.", "@white_town is successful.\n", E({"successful":u("The band was successful.")},{"white_town":c("White Town.")})),
"e545:c": item("REIFIED", ["event reification", "binary predicates", "constants", "existential quantification", "negation", "conjunction"], "The future and remaining-game scope are exposed as relations on a possible ejection event. The claim denies any Henry-ejection event after now and during the remaining part of the game, rather than hiding futurity in a unary predicate.", "not (there exists entity event, ((((event is ejection_event) and (event has_ejectee @henry)) and (@now before event)) and (event during @rest_of_game))).\n", E({"ejection_event":u("The entity is an ejection event."),"has_ejectee":b("The event ejects the second entity."),"before":b("The first temporal entity occurs before the second."),"during":b("The first event occurs during the second temporal interval.")},{"henry":c("Henry."),"now":c("The present boundary for this claim."),"rest_of_game":c("The remaining temporal interval of the game.")}), "An ejection event exposes the ejectee, its position after now, and its occurrence within the rest-of-game interval."),
"e1336:c": item("DIRECT", ["unary predicate", "constant"], "Class membership for a named animal is unary FOL.", "@sea_eel is eel.\n", E({"eel":u("The entity is an eel.")},{"sea_eel":c("The sea eel.")})),
"e1203:c": item("DIRECT", ["unary predicate", "constant", "negation"], "The negated income classification is unary FOL.", "not (@james is high_income).\n", E({"high_income":u("The person has a high income.")},{"james":c("James.")})),
"s47:p2": item("DIRECT", ["unary predicates", "binary predicate", "universal quantification", "implication", "conjunction"], "The rule quantifies a child and controlled substance and relates exposure to chemical endangerment.", "for every entity person, (for every entity substance, (if (((person is child) and (substance is controlled_substance)) and (person exposed_to substance)), then (person is in_chemical_endangerment))).\n", E({"child":u("The entity is a child."),"controlled_substance":u("The entity is a controlled substance."),"exposed_to":b("The first entity is exposed to the second."),"in_chemical_endangerment":u("The child is in chemical endangerment.")})),
"e388:c": item("DIRECT", ["unary predicate", "binary predicate", "constant", "existential quantification", "conjunction"], "Existence of a supervised-learning method used to train the named model is function-free binary FOL.", "there exists entity algorithm, ((algorithm is supervised_learning) and (@state_of_the_art_text_summarization_model trained_with algorithm)).\n", E({"supervised_learning":u("The entity is a supervised-learning algorithm."),"trained_with":b("The first entity was trained using the second entity.")},{"state_of_the_art_text_summarization_model":c("The state-of-the-art text summarization model.")})),
"s181:p3": item("DIRECT", ["binary predicates", "constant", "universal quantification", "existential quantification", "negation", "equality", "fixed finite cardinality"], "Under the ordinary ranking reading, a superhero is in America's top ten exactly when there do not exist ten pairwise-distinct superheroes ranked above that superhero. Fixed finite cardinality is expressible with equality in v0, so no opaque top_ten predicate is needed. The ranking relation itself is ordinary supplied relational data; the formula does not compute a score. The gold instead says the superheroes are American and treats TopTenFavorite as an unexplained unary property.", top_ten_source(), E({"superhero":u("The entity is a superhero."),"ranked_above_by_america":b("The first superhero ranks above the second in America's stated favorite-superhero ranking."),"speaks_language":b("The first entity speaks the second language.")},{"english":c("English.")})),
"s151:p0": item("DIRECT", ["unary predicate", "binary predicates", "constants", "conjunction"], "The cove classification, naming relation, and Bulgarian location are all unary/binary facts.", "((@barutin_cove is cove) and (@barutin_cove named_after @barutin_settlement)) and (@barutin_settlement located_in @bulgaria).\n", E({"cove":u("The entity is a cove."),"named_after":b("The first entity is named after the second."),"located_in":b("The first entity is located in the second.")},{"barutin_cove":c("Barutin Cove."),"barutin_settlement":c("The Bulgarian settlement of Barutin."),"bulgaria":c("Bulgaria.")})),
"e532:c": item("REIFIED", ["event reification", "binary predicates", "constants", "existential quantification", "conjunction"], "Sharing has sharer, shared work, and recipient roles, so it is reified as a sharing event without dropping an argument.", "there exists entity event, ((((event is sharing_event) and (event has_sharer @karen)) and (event has_shared_item @black_mirror)) and (event has_recipient @lisa)).\n", E({"sharing_event":u("The entity is an event of sharing."),"has_sharer":b("The event has the person who will share as its sharer."),"has_shared_item":b("The event has the work shared as its item."),"has_recipient":b("The event has the recipient of the sharing.")},{"karen":c("Karen."),"black_mirror":c("Black Mirror."),"lisa":c("Lisa.")}), "A fresh event carries all three semantic roles of ShareWith(Karen, Black Mirror, Lisa)."),
"s482:p2": item("DIRECT", ["unary predicates", "binary predicate", "constant", "universal quantification", "implication"], "Location in Potterville and flying jointly imply coolness.", "for every entity person, (if ((person in_place @potterville) and (person is flies)), then (person is cool)).\n", E({"in_place":b("The first entity is in the second place."),"flies":u("The entity flies."),"cool":u("The entity is cool.")},{"potterville":c("Potterville.")})),
"s131:p4": item("DIRECT", ["unary predicates", "binary predicates", "constant", "universal quantification", "existential quantification", "implication"], "Read as a generic statement, every machine-learning algorithm used to train at least one text-summarization model requires labeled data. Quantifying the model preserves the plural category without inventing a collective constant.", "for every entity algorithm, (if ((algorithm is machine_learning_algorithm) and (there exists entity model, ((model is text_summarization_model) and (algorithm used_to_train model)))), then (algorithm requires @labeled_data)).\n", E({"machine_learning_algorithm":u("The entity is a machine-learning algorithm."),"text_summarization_model":u("The entity is a text summarization model."),"used_to_train":b("The first entity is used to train the second model."),"requires":b("The first entity requires the second.")},{"labeled_data":c("Labeled data.")})),
"s129:p3": item("DIRECT", ["binary predicate", "constants"], "Researching a topic is a binary relation. The gold's contributed-to wording is weaker/different, so the witness follows the sentence.", "@richard_hamming researched @numerical_methods.\n", E({"researched":b("The first entity researched the second topic.")},{"richard_hamming":c("Richard Hamming."),"numerical_methods":c("Numerical methods.")})),
"e1303:c": item("DIRECT", ["unary predicate", "binary predicate", "constants", "negation", "implication"], "A negated origin relation can serve as the antecedent of a material implication.", "if (not (@marvin from_place @mars)), then (@marvin is human).\n", E({"from_place":b("The first entity is from the second place."),"human":u("The entity is a human.")},{"marvin":c("Marvin."),"mars":c("Mars.")})),
"s161:p1": item("OPAQUE", ["numeric comparison beyond v0", "relational skeleton"], "The rule needs a numeric score and greater-than-95 comparison. v0 has neither numbers nor interpreted order; a greater_than_95 predicate would merely hide the required arithmetic.", None, None, None),
"e968:c": item("DIRECT", ["unary predicates", "binary predicate", "constant", "existential quantification", "conjunction"], "Living locally and owning at least one coffeemaker and at least one blender can be stated with two existential objects. The gold incorrectly replaces two owned appliance claims by one combined category and omits neighborhood residence.", "(@sam is lives_in_this_neighborhood) and (there exists entity coffee, ((coffee is coffeemaker) and ((@sam owns coffee) and (there exists entity appliance, ((appliance is blender) and (@sam owns appliance)))))).\n", E({"lives_in_this_neighborhood":u("The person lives in this neighborhood."),"coffeemaker":u("The entity is a coffeemaker."),"blender":u("The entity is a blender."),"owns":b("The first entity owns the second in the first entity's home.")},{"sam":c("Sam.")})),
"s470:p0": item("DIRECT", ["unary predicates", "binary predicate", "universal quantification", "existential quantification", "implication", "conjunction"], "The indefinite is generic in this taxonomic sentence: any Unix operating system used in at least one lab computer is software. Quantifying lab computers avoids treating a plural collection as one invented entity.", "for every entity system, (if ((system is unix_operating_system) and (there exists entity computer, ((computer is lab_computer) and (system used_in computer)))), then (system is software)).\n", E({"unix_operating_system":u("The entity is a Unix operating system."),"lab_computer":u("The entity is a computer in the lab."),"used_in":b("The first entity is used in the second computer."),"software":u("The entity is a piece of software.")})),
"e12:c": item("DIRECT", ["unary predicates", "binary predicate", "constants", "existential quantification", "implication", "conjunction"], "The consequent says Peter Parker wears some uniform, so the indefinite is existential rather than an arbitrary named constant.", "if (@thor is happy), then (there exists entity garment, ((garment is uniform) and (@peter_parker wears garment))).\n", E({"happy":u("The person is happy."),"uniform":u("The entity is a uniform."),"wears":b("The first entity wears the second.")},{"thor":c("Thor."),"peter_parker":c("Peter Parker.")})),
"s203:p3": item("DIRECT", ["unary predicate", "constant"], "The classification of space as a vacuum is unary FOL.", "@space is vacuum.\n", E({"vacuum":u("The entity is a vacuum.")},{"space":c("Space.")})),
"s367:p0": item("OPAQUE", ["temporal/frequency interpretation beyond v0", "relational skeleton"], "The core negative consequence is relational, but 'every morning' and 'regularly' require temporal or frequency semantics unavailable in v0. Naming predicates for those checks would conceal essential interpretation.", None, None, None),
"e578:c": item("DIRECT", ["unary predicate", "constant"], "Although informal and evaluative, 'sucks' can be represented as an uninterpreted unary property without additional logical machinery.", "@space is sucks.\n", E({"sucks":u("The entity sucks in the evaluative sense intended by the speaker.")},{"space":c("Space.")})),
"e1126:c": item("OPAQUE", ["propositional attitude", "embedded proposition", "disjunction", "negation"], "The outer disjunction is relationally simple, but both branches are propositional attitudes: wanting an addiction state and awareness of the proposition that caffeine is a drug. v0 has no proposition terms or attitude operators. Predicates such as wants_addiction_to and aware_is_drug would hide those essential embedded meanings.", None, None, None),
"s352:p5": item("DIRECT", ["unary predicates", "constant", "negation", "implication"], "The conditional and negated classification are directly expressible.", "if (@harvard_weekly_book_club is created_under_law), then (not (@harvard_weekly_book_club is private_company)).\n", E({"created_under_law":u("The organization is created under law."),"private_company":u("The organization is a private company.")},{"harvard_weekly_book_club":c("The Harvard Weekly Book Club.")})),
"s433:p5": item("DIRECT", ["unary predicates", "binary predicate", "constants", "negation", "conjunction"], "'Neither ... nor ...' negates each complete classification-plus-location conjunct. The gold incorrectly asserts Tower A is a building while only negating a coarse InNewHaven predicate.", "(not ((@tower_a is building) and (@tower_a in_place @new_haven))) and (not ((@tower_a is skyscraper) and (@tower_a in_place @manhattan))).\n", E({"building":u("The entity is a building."),"skyscraper":u("The entity is a skyscraper."),"in_place":b("The first entity is in the second place.")},{"tower_a":c("Tower A."),"new_haven":c("New Haven."),"manhattan":c("Manhattan.")})),
"s312:p4": item("DIRECT", ["unary predicate", "binary predicates", "constants", "existential quantification", "negation", "implication", "conjunction"], "Tom and the foreigner qualification remain explicit. The consequent existentially quantifies an academic program rather than inventing a constant. The gold has an unbound x and omits both Tom and the foreigner qualification.", "if (not (@tom studies_as_foreigner_in @united_states)), then (there exists entity program, ((program is academic_program) and (@tom enrolled_in program))).\n", E({"academic_program":u("The entity is an academic program."),"studies_as_foreigner_in":b("The first entity studies in the second place as a foreigner."),"enrolled_in":b("The first entity is enrolled in the second program.")},{"tom":c("Tom."),"united_states":c("The United States.")})),
"e573:c": item("NO", ["reachability/path quantification", "temporal avoidance"], "The essential claim quantifies over a possible course of play reaching yellow while never visiting green. v0 cannot quantify over paths or arbitrary sequences, express reachability, or state 'ever/never' along a path. The gold's RedToYellow predicate hides and also omits the avoidance condition.", None, None, None),
"s428:p0": item("DIRECT", ["unary predicate", "binary predicates", "constants", "universal quantification", "implication"], "The device restriction, company ownership, and Google Home connection form a binary relational rule.", "for every entity item, (if ((item is device) and (item belongs_to @company)), then (item connected_to @google_home)).\n", E({"device":u("The entity is a device."),"belongs_to":b("The first entity belongs to the second organization."),"connected_to":b("The first entity is connected to the second system.")},{"company":c("The company."),"google_home":c("Google Home.")})),
"s69:p1": item("REIFIED", ["event reification", "binary predicates", "constants", "existential quantification", "conjunction"], "The word 'after' requires relating an injury event to a retirement event; reifying both events preserves precedence and the retirement year. The gold omits the injury and ordering entirely.", "there exists entity injury, ((injury is injury_event) and ((injury has_participant @brian_winter) and (there exists entity retirement, ((((retirement is retirement_event) and (retirement has_participant @brian_winter)) and (retirement in_year @year_2012)) and (injury before retirement))))).\n", E({"injury_event":u("The entity is an injury event."),"retirement_event":u("The entity is a retirement event."),"has_participant":b("The event has the second entity as participant."),"in_year":b("The event occurred in the specified year."),"before":b("The first event occurred before the second event.")},{"brian_winter":c("Brian Winter."),"year_2012":c("The year 2012.")}), "Two event entities expose the participant, year, and temporal precedence as unary/binary relations."),
"s217:p2": item("OPAQUE", ["ability modality", "propositional attitude", "future modality", "implication"], "The sentence connects ability, desire, and a future action. v0 has neither modal accessibility nor proposition/action objects sufficient to interpret can, wants to, and will. Unary predicates named can_compose, wants_to_compose, and will_compose would hide every essential modal component.", None, None, None),
"e964:c": item("DIRECT", ["binary predicate", "constants"], "Containment of carbon in the mixture is a binary fact.", "@mixture contains @carbon.\n", E({"contains":b("The first entity contains the second substance.")},{"mixture":c("The mixture."),"carbon":c("Carbon.")})),
}

def main():
    assert Path(ve.__file__).resolve().is_relative_to(Path("/private/tmp/ve-e0-integration")), ve.__file__
    sample = json.loads(DRAW.read_text())["sample"]
    assert len(sample) == 30 and set(spec) == {x["id"] for x in sample}
    records = []
    for raw in sample:
        rec = {"dataset": "folio", "id": raw["id"], **spec[raw["id"]],
               "checker_source": {"commit": "12538d8d418b3eeec59e58d74c3886786e5139da",
                                  "module": str(Path(ve.__file__).resolve())}}
        if rec["formalization"] is None:
            rec["parse_result"] = {"status": "not_applicable", "reason": "No faithful complete v0 formalization for this label."}
        else:
            rec["parse_result"] = check(Environment(rec["environment"]), rec["formalization"])
        records.append(rec)
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records))
    print(json.dumps({"records": len(records), "labels": {label: sum(r["label"] == label for r in records) for label in ("DIRECT","REIFIED","OPAQUE","NO")}, "checked": sum(r["parse_result"].get("language") == "accepted" for r in records)}, sort_keys=True))

if __name__ == "__main__":
    main()
