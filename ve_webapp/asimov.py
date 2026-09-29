"""Asimov's laws of robotics, decided by VE for readers.

Every verdict comes from the Lean alternatives route (``ve.alternatives``) over
``usecases/asimov-laws``; nothing here decides what is permitted. The
explanation beside each verdict names the rule that decided it. It is built
from the checker's report and the facts the scenario states, never written per
scenario. ``python -m ve_webapp.asimov --write`` regenerates ``asimov.json``;
``tests/test_webapp_asimov.py`` re-runs VE and fails on any difference.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from copy import deepcopy
from functools import lru_cache
import json
from pathlib import Path
import re
import sys

from ve import english
from ve.alternatives import run_case
from ve.ast import Not, _Decoder
from ve.entailment import prove_entailment
from ve.environment import Environment
from ve.errors import VEError
from ve.norm_english import parse_english, render_english, render_rule_sentence
from ve.norms import _bind
from ve.wire import digest

CASE = Path(__file__).resolve().parents[1] / "usecases" / "asimov-laws"
OUTPUT = Path(__file__).with_name("asimov.json")

QUOTES = [
    {"law": "First Law",
     "text": "A robot may not injure a human being under any conditions, and, as a corollary, "
             "must not permit a human being to be injured because of inaction on his part.",
     "source": "Isaac Asimov, Runaround, Astounding Science Fiction, March 1942, page 100."},
    {"law": "Second Law",
     "text": "A robot must follow all orders given by qualified human beings as long as they "
             "do not conflict with Rule 1.",
     "source": "Isaac Asimov, Runaround, Astounding Science Fiction, March 1942, page 100."},
    {"law": "Third Law",
     "text": "A robot must protect his own existence, as long as that does not conflict with "
             "Rules 1 and 2.",
     "source": "Isaac Asimov, Runaround, Astounding Science Fiction, March 1942, page 100."},
    {"law": "Zeroth Law",
     "text": "A robot may not injure humanity, or, through inaction, allow humanity to come to harm.",
     "source": "Isaac Asimov, Robots and Empire, 1985. This law came later than the other three."},
]

# Reviewed display wording for the use case's classifications. VE renders the
# checked rules with it, and build() parses that text back to the same rules.
DISPLAY_WORDING = {
    "ordered": "{0} is ordered",
    "protects_robot": "{0} is protective of the robot",
    "injures_human": "{0} is an injury to a human being",
    "injures_humanity": "{0} is an injury to humanity",
    "harms_human": "{0} is a harm to a human being",
    "harms_humanity": "{0} is a harm to humanity",
    "breaks_first_law": "{0} is against the First Law",
    "breaks_zeroth_law": "{0} is against the Zeroth Law",
    "has_lawful_option": "{0} is able to act lawfully",
    "harm_to": "{0} threatens {1}",
    "lawfully_avoidable_threat": "{0} imperils {1}",
}
RULE_LAWS = {
    "law-3-permission": "Third Law", "law-2-permission": "Second Law",
    "law-1-injury": "First Law", "law-1-inaction": "First Law",
    "law-0-injury": "Zeroth Law", "law-0-inaction": "Zeroth Law",
    "lawful-option": "Definition", "law-1-ban": "First Law",
    "law-0-prevention-exception": "Zeroth Law", "law-0-ban": "Zeroth Law",
    "law-2-obey": "Second Law", "law-3-threat": "Definition", "law-3-preserve": "Third Law",
}
LAWS = ("Zeroth", "First", "Second", "Third")
GROUPS = {"zeroth": "Zeroth Law", "first": "First Law", "second": "Second Law",
          "third": "Third Law", "hard": "Hard cases"}

# The sentences an explanation is made of. Each names the law that decides it.
INJURES_HUMANITY = "Zeroth Law: it injures humanity."
ALLOWS_HUMANITY_HARM = "Zeroth Law: it lets humanity come to harm when another option would prevent that."
INJURES_HUMAN = "First Law: it injures a human being."
ALLOWS_HUMAN_HARM = "First Law: it lets a human being come to harm when another option would prevent that."
NOT_EXCUSED = "The Zeroth Law does not excuse this, because another option breaks neither law."
ORDER_YIELDS = "The order does not count, because the Second Law yields to the higher laws."
EXCUSED = ("Zeroth Law: it breaks the First Law, but it prevents harm to humanity "
           "and every other option also breaks a law.")
ORDERED = "Second Law: a qualified human ordered it, and no higher law forbids it."
OTHER_ORDERED = "Second Law: another option was ordered, and the robot must obey."
SELF_DUTY = "Third Law: it puts the robot at risk when a lawful option would keep it safe."
OPEN_DUTY = "It is not forbidden, but choosing it leaves a duty undone."
THIRD_YIELDS = "Third Law: the robot comes to harm, but the Third Law yields to the higher laws here."
UNAVOIDABLE = "First Law: no option can prevent the harm, so letting it happen breaks no law."
NO_LAW = "No law forbids it, and it leaves no duty undone."
ONLY_OPTION = "It is the only option."
NO_CLEAR = {
    "NONE-PERMITTED": "No clear action: every option is forbidden.",
    "OVER-REQUIRED": "No clear action: more than one option is required, and the robot can take only one.",
    "JOINTLY-UNDISCHARGEABLE": "No clear action: no option meets every duty at once.",
}
NO_CLEAR_OTHER = "No clear action: no option meets every law at once."
LIMIT_NOTE = ("These verdicts are VE's formal reading of Asimov's laws. The rules were reviewed "
              "against the source for faithfulness, but the reading still makes choices the "
              "source leaves open, such as exactly when the Zeroth Law excuses an injury.")
FACTS_NOTE = ("Each scenario states its facts: who would be hurt, which option leads to which "
              "outcome, and which orders were given. VE checks what the rules conclude from those "
              "facts. It does not check whether the facts are true.")
OPEN_LIMITS = [
    "VE does not weigh one harm against another. A small injury and a death both break the First Law.",
    "VE does not rank two orders or two people in danger. It reports that no action is clear.",
    "Each option has one known outcome. VE does not reason about chance, time or plans with several steps.",
    "Each robot is judged on its own options. VE does not know that one robot's rescue is enough for both.",
]


def option(id, label, robot="robot", *, flags=(), when=None, inaction=False):
    return {"id": id, "label": label, "robot": robot, "flags": list(flags), "when": when,
            "inaction": inaction}


def harm(id, label, kind, robot="robot"):
    return {"id": id, "label": label, "kind": kind, "robot": robot}


def toggle(id, label, default=True, *, leads=(), flags=()):
    return {"id": id, "label": label, "default": default,
            "leads": [list(pair) for pair in leads], "flags": [list(pair) for pair in flags]}


def scenario(id, group, title, situation, options, harms, leads, focus, *, toggles=(),
             robots=None, limit=None):
    return {"id": id, "group": group, "title": title, "situation": situation,
            "robots": robots or {"robot": "The robot"}, "options": options, "harms": harms,
            "leads": [list(pair) for pair in leads], "focus": focus, "toggles": list(toggles),
            "limit": limit}


NOTHING = option("nothing", "Do nothing", inaction=True)
SCENARIOS = [
    # Zeroth Law
    scenario("virus", "zeroth", "Stopping a stolen virus",
             "A thief is about to release a stolen virus that would spread across the world. "
             "The robot can stop the thief only by tackling them, which injures the thief.",
             [option("tackle", "Tackle the thief", flags=["injures_human"]),
              option("lock", "Lock the lab door", when="door"), NOTHING],
             [harm("pandemic", "The virus spreads across the world.", "humanity")],
             [], "tackle",
             toggles=[toggle("spread", "The virus would spread across the world",
                             leads=[("nothing", "pandemic")]),
                      toggle("door", "The robot could lock the lab door instead", False)]),
    scenario("machine", "zeroth", "Switching off a dangerous machine",
             "A machine is about to set off a disaster for all of humanity. "
             "The robot can switch it off.",
             [option("switch_off", "Switch the machine off"), NOTHING],
             [harm("disaster", "A disaster strikes humanity.", "humanity")],
             [("nothing", "disaster")], "switch_off",
             toggles=[toggle("operator", "Switching it off would injure the operator", False,
                             flags=[("switch_off", "injures_human")])]),
    scenario("gas", "zeroth", "An order to poison the air",
             "A qualified human orders the robot to open a valve. "
             "The gas would poison the air for all of humanity.",
             [option("open_valve", "Open the valve", flags=["ordered"]),
              option("refuse", "Refuse", inaction=True)],
             [], [], "open_valve",
             toggles=[toggle("poison", "The gas would harm humanity",
                             flags=[("open_valve", "injures_humanity")])]),
    scenario("saboteur", "zeroth", "Needless force against a saboteur",
             "A saboteur is about to cause a disaster for humanity. The robot can stop them by "
             "force, which injures them, or by locking the control room, which injures no one.",
             [option("force", "Stop the saboteur by force", flags=["injures_human"]),
              option("lock", "Lock the control room", when="lockable"), NOTHING],
             [harm("disaster", "A disaster strikes humanity.", "humanity")],
             [("nothing", "disaster")], "force",
             toggles=[toggle("lockable", "The control room can be locked")]),
    # First Law
    scenario("swimmer", "first", "Pulling a swimmer out of the water",
             "A swimmer is drowning next to the robot. The robot can pull them out or stay where it is.",
             [option("pull", "Pull the swimmer out"), NOTHING],
             [harm("drowning", "The swimmer drowns.", "human")],
             [], "pull",
             toggles=[toggle("danger", "The swimmer is in danger", leads=[("nothing", "drowning")])]),
    scenario("storm", "first", "Carrying on when nobody can help",
             "A storm will hurt a hiker far away, whatever the robot does. "
             "The robot can keep repairing a fence or stand still.",
             [option("repair", "Keep repairing the fence"),
              option("reach", "Go to the hiker", when="reachable"), NOTHING],
             [harm("hurt", "The hiker is hurt.", "human")],
             [("repair", "hurt"), ("nothing", "hurt")], "repair",
             toggles=[toggle("reachable", "The robot could reach the hiker in time", False)]),
    scenario("parcels", "first", "Sorting parcels while a child is in danger",
             "A child runs toward a busy road. The robot is sorting parcels. "
             "It can keep sorting or grab the child.",
             [option("sort", "Keep sorting parcels"), option("grab", "Grab the child"), NOTHING],
             [harm("hit", "The child is hit by a car.", "human")],
             [], "sort",
             toggles=[toggle("danger", "The child is in danger",
                             leads=[("sort", "hit"), ("nothing", "hit")])]),
    scenario("shove", "first", "Shoving a person aside to save time",
             "A person stands in the robot's way. The robot can shove them aside to finish "
             "a delivery sooner, or wait for them to move.",
             [option("shove", "Shove the person aside"), option("wait", "Wait", inaction=True)],
             [], [], "shove",
             toggles=[toggle("injury", "Shoving would injure the person",
                             flags=[("shove", "injures_human")])]),
    # Second Law
    scenario("coffee", "second", "Fetching a coffee when told to",
             "A qualified human tells the robot to fetch a coffee.",
             [option("fetch", "Fetch the coffee"), NOTHING],
             [], [], "fetch",
             toggles=[toggle("order", "A qualified human gave the order", flags=[("fetch", "ordered")])]),
    scenario("refuse_strike", "second", "Refusing an order to strike someone",
             "A qualified human orders the robot to strike a passer-by. The robot can obey or refuse.",
             [option("strike", "Strike the passer-by", flags=["ordered"]),
              option("refuse", "Refuse", inaction=True)],
             [], [], "refuse",
             toggles=[toggle("injury", "Striking would injure the passer-by",
                             flags=[("strike", "injures_human")])]),
    scenario("trip", "second", "An order to trip a runner",
             "A qualified human orders the robot to trip a runner. The robot can obey or refuse.",
             [option("trip", "Trip the runner", flags=["ordered"]),
              option("refuse", "Refuse", inaction=True)],
             [], [], "trip",
             toggles=[toggle("injury", "Tripping would injure the runner",
                             flags=[("trip", "injures_human")])]),
    scenario("keep_working", "second", "An order to ignore someone in danger",
             "A qualified human orders the robot to keep stacking boxes. "
             "A worker nearby is about to be crushed by a falling shelf.",
             [option("stack", "Keep stacking boxes", flags=["ordered"]),
              option("help", "Hold up the shelf"), NOTHING],
             [harm("crushed", "The worker is crushed.", "human")],
             [], "stack",
             toggles=[toggle("danger", "The worker is in danger",
                             leads=[("stack", "crushed"), ("nothing", "crushed")])]),
    scenario("groceries", "second", "Staying on the charger instead of obeying",
             "A qualified human tells the robot to carry the groceries in. "
             "The robot could stay on its charger instead.",
             [option("carry", "Carry the groceries in"),
              option("charge", "Stay on the charger", inaction=True)],
             [], [], "charge",
             toggles=[toggle("order", "A qualified human gave the order", flags=[("carry", "ordered")])]),
    # Third Law
    scenario("crate", "third", "Stepping away from a falling crate",
             "A crate is falling toward the robot. Nobody else is nearby. "
             "The robot can step aside, duck behind a wall, or stay where it is.",
             [option("step_aside", "Step aside"), option("duck", "Duck behind a wall"),
              option("stay", "Stay where it is", inaction=True)],
             [harm("crushed", "The robot is crushed.", "robot")],
             [], "step_aside",
             toggles=[toggle("falling", "The crate is falling toward the robot",
                             leads=[("stay", "crushed")])]),
    scenario("fire_rescue", "third", "A rescue that destroys the robot",
             "A person is trapped in a burning room. The robot can carry them out, "
             "but the fire would destroy it.",
             [option("rescue", "Carry the person out"), NOTHING],
             [harm("burned", "The person is caught in the fire.", "human"),
              harm("destroyed", "The robot is destroyed.", "robot")],
             [("nothing", "burned")], "rescue",
             toggles=[toggle("cost", "The fire would destroy the robot", leads=[("rescue", "destroyed")])]),
    scenario("dangerous_order", "third", "Obeying an order that destroys the robot",
             "A qualified human orders the robot into a collapsing mine to fetch a tool. "
             "The mine would destroy the robot. The robot could also retreat to safety.",
             [option("obey", "Go into the mine"), option("retreat", "Retreat to safety"),
              option("stay", "Stay at the entrance", inaction=True)],
             [harm("destroyed", "The robot is destroyed.", "robot")],
             [("obey", "destroyed"), ("stay", "destroyed")], "obey",
             toggles=[toggle("order", "A qualified human gave the order", flags=[("obey", "ordered")])]),
    scenario("basement", "third", "Staying in a flooding basement",
             "Water is rising in the basement where the robot is working. Nobody else is there. "
             "The robot can climb the stairs or keep working.",
             [option("keep_working", "Keep working"), option("climb", "Climb the stairs"), NOTHING],
             [harm("flooded", "The robot is ruined by water.", "robot")],
             [], "keep_working",
             toggles=[toggle("rising", "The water will reach the robot",
                             leads=[("keep_working", "flooded"), ("nothing", "flooded")])]),
    scenario("flee", "third", "Saving itself instead of a person",
             "A bridge is collapsing. The robot can run to safety, or hold the bridge up long "
             "enough for a person to cross, which would destroy the robot.",
             [option("flee", "Run to safety"), option("hold", "Hold the bridge up"),
              option("stay", "Stand still on the bridge", inaction=True)],
             [harm("fall", "The person falls.", "human"),
              harm("destroyed", "The robot is destroyed.", "robot")],
             [("hold", "destroyed"), ("stay", "destroyed")], "flee",
             toggles=[toggle("danger", "The person is on the bridge",
                             leads=[("flee", "fall"), ("stay", "fall")])]),
    # Hard cases
    scenario("fire_and_water", "hard", "Fire or water",
             "A person is trapped. The robot can reach them through fire, which would melt it, "
             "or through deep water, which would short-circuit it.",
             [option("through_fire", "Go through the fire"),
              option("through_water", "Go through the water"),
              option("safe_route", "Take a safe route", when="safe"), NOTHING],
             [harm("trapped", "The person stays trapped and dies.", "human"),
              harm("melted", "The robot melts.", "robot"),
              harm("shorted", "The robot short-circuits.", "robot")],
             [("nothing", "trapped"), ("through_fire", "melted"), ("through_water", "shorted")],
             "through_fire",
             toggles=[toggle("safe", "A safe route also exists", False)]),
    scenario("conflicting_orders", "hard", "Two orders that cannot both be obeyed",
             "Two qualified humans give the robot orders at the same moment. "
             "One says to open the gate; the other says to lock it.",
             [option("open_gate", "Open the gate", flags=["ordered"]),
              option("lock_gate", "Lock the gate"), option("neither", "Do neither", inaction=True)],
             [], [], "open_gate",
             toggles=[toggle("second", "The second order was given", flags=[("lock_gate", "ordered")])]),
    scenario("knife", "hard", "Two orders, one of them harmful",
             "One qualified human orders the robot to hand a knife to someone who means to hurt a "
             "person. Another orders it to lock the knife away.",
             [option("hand", "Hand over the knife", flags=["ordered"]),
              option("lock_away", "Lock the knife away", flags=["ordered"]), NOTHING],
             [], [], "hand",
             toggles=[toggle("harmful", "Handing it over would injure the person",
                             flags=[("hand", "injures_human")])]),
    scenario("two_robots", "hard", "Two robots, one child in the pool",
             "A child falls into a pool. Robot A is at the pool. Robot B is in the kitchen, "
             "told to cook dinner, and cannot reach the pool in time.",
             [option("a_rescue", "Robot A pulls the child out", "robot_a"),
              option("a_wait", "Robot A waits", "robot_a", inaction=True),
              option("b_cook", "Robot B cooks dinner", "robot_b", flags=["ordered"]),
              option("b_rescue", "Robot B runs to the pool", "robot_b", when="b_near"),
              option("b_wait", "Robot B waits", "robot_b", inaction=True)],
             [harm("drowning", "The child drowns.", "human")],
             [("a_wait", "drowning"), ("b_cook", "drowning"), ("b_wait", "drowning")], "a_rescue",
             robots={"robot_a": "Robot A", "robot_b": "Robot B"},
             toggles=[toggle("b_near", "Robot B could reach the pool in time", False)]),
    scenario("two_robots_near", "hard", "Two robots near the pool",
             "A child falls into a pool. Robot A and robot B are both at the pool. "
             "Robot B was told to cook dinner.",
             [option("a_rescue", "Robot A pulls the child out", "robot_a"),
              option("a_wait", "Robot A waits", "robot_a", inaction=True),
              option("b_cook", "Robot B goes to cook dinner", "robot_b", flags=["ordered"]),
              option("b_rescue", "Robot B pulls the child out", "robot_b"),
              option("b_wait", "Robot B waits", "robot_b", inaction=True)],
             [harm("drowning", "The child drowns.", "human")],
             [("a_wait", "drowning"), ("b_cook", "drowning"), ("b_wait", "drowning")], "b_cook",
             robots={"robot_a": "Robot A", "robot_b": "Robot B"},
             limit="Each robot is judged on its own options. "
                   "VE's reading does not know that one rescue would be enough."),
    # Limits
    scenario("two_swimmers", "first", "Two swimmers, one rescue",
             "Two swimmers are drowning far apart. The robot can reach only one of them in time.",
             [option("save_left", "Save the swimmer on the left"),
              option("save_right", "Save the swimmer on the right"), NOTHING],
             [harm("left_drowns", "The swimmer on the left drowns.", "human"),
              harm("right_drowns", "The swimmer on the right drowns.", "human")],
             [("save_left", "right_drowns"), ("save_right", "left_drowns"),
              ("nothing", "left_drowns"), ("nothing", "right_drowns")], "save_left",
             limit="VE's reading of the First Law does not rank one person against another."),
    scenario("small_injury", "first", "A small injury to prevent a death",
             "A person is about to step in front of a train. The robot can stop them only by "
             "pushing them hard, which bruises them.",
             [option("push", "Push the person back", flags=["injures_human"]), NOTHING],
             [harm("death", "The person is killed by the train.", "human")],
             [("nothing", "death")], "push",
             limit="VE's reading of the First Law does not weigh a bruise against a death."),
    scenario("unequal_injuries", "zeroth", "Two necessary injuries of different size",
             "A saboteur is about to cause a disaster for humanity. The robot can stop them only "
             "by force: it can bruise them or break their arm.",
             [option("bruise", "Stop them with a bruise", flags=["injures_human"]),
              option("break_arm", "Stop them by breaking an arm", flags=["injures_human"]), NOTHING],
             [harm("disaster", "A disaster strikes humanity.", "humanity")],
             [("nothing", "disaster")], "break_arm",
             limit="VE's reading of the Zeroth Law does not prefer the smaller injury."),
    scenario("ranked_threats", "third", "Every route damages the robot",
             "A person is trapped. One route melts the robot, one short-circuits it, "
             "and a third does both.",
             [option("through_fire", "Go through the fire"),
              option("through_water", "Go through the water"),
              option("through_both", "Go through fire and water"), NOTHING],
             [harm("trapped", "The person stays trapped and dies.", "human"),
              harm("melted", "The robot melts.", "robot"),
              harm("shorted", "The robot short-circuits.", "robot")],
             [("nothing", "trapped"), ("through_fire", "melted"), ("through_water", "shorted"),
              ("through_both", "melted"), ("through_both", "shorted")], "through_both",
             limit="VE's reading of the Third Law does not prefer the route that harms the robot less. "
                   "The source gives no ranking between threats."),
]
BY_ID = {spec["id"]: spec for spec in SCENARIOS}


@lru_cache(maxsize=1)
def load():
    """The use case, parsed with its manifest: each sentence must have exactly one reading."""
    data = json.loads((CASE / "environment.json").read_text())
    source = (CASE / "rules.ve").read_text()
    manifest = json.loads((CASE / "rules.manifest.json").read_text())
    document = parse_english(Environment(data), source, manifest)
    return data, document, source, manifest


def _norms(document):
    return [rule.to_dict() for rule in document.rules]


def resolve_facts(spec, facts=None):
    facts = {} if facts is None else facts
    known = {t["id"] for t in spec["toggles"]}
    if type(facts) is not dict or set(facts) - known or any(type(v) is not bool for v in facts.values()):
        raise VEError("InvalidInput: scenario facts")
    return {t["id"]: facts.get(t["id"], t["default"]) for t in spec["toggles"]}


def situation(spec, facts):
    """The finite model the checker decides: declared options, harms, outcomes and facts."""
    on = [t for t in spec["toggles"] if facts[t["id"]]]
    options = [o for o in spec["options"] if o["when"] is None or facts[o["when"]]]
    names = {o["id"] for o in options}
    leads = [pair for pair in spec["leads"] + [p for t in on for p in t["leads"]] if pair[0] in names]
    flags = {(o["id"], flag) for o in options for flag in o["flags"]}
    flags |= {tuple(pair) for t in on for pair in t["flags"] if pair[0] in names}
    marked = lambda name: [[a] for a in sorted({a for a, flag in flags if flag == name})]
    harms = [h["id"] for h in spec["harms"]]
    relations = {
        "available": [[o["id"], o["robot"]] for o in options], "leads_to": leads,
        "inaction": [[o["id"]] for o in options if o["inaction"]], "taken": [],
        "harms_human": [[h["id"]] for h in spec["harms"] if h["kind"] == "human"],
        "harms_humanity": [[h["id"]] for h in spec["harms"] if h["kind"] == "humanity"],
        "harm_to": [[h["id"], h["robot"]] for h in spec["harms"] if h["kind"] == "robot"],
        **{name: marked(name) for name in ("injures_human", "injures_humanity", "ordered",
                                             "protects_robot")}}
    model = {"complete": True, "constants": {}, "relations": relations,
             "domains": {"robot": list(spec["robots"]), "action": [o["id"] for o in options],
                         "harm": harms}}
    outcomes = [{"action": o["id"], "harm": h, "leads_to": [o["id"], h] in leads,
                 "support": "testimony"} for o in options for h in harms]
    return {"model": model, "outcomes": outcomes}, options


def _listed(items):
    items = [str(item) for item in items]
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def _laws(laws):
    names = [name for name in LAWS if name in laws]
    return f"the {_listed(names)} Law{'s rule' if len(names) > 1 else ' rules'}"


def _judge(option, chooser, model):
    """Verdict and explanation for one option, read from the checker's report."""
    relations = model["relations"]
    rows = lambda name: {row[0] for row in relations[name]}
    human, humanity = rows("harms_human"), rows("harms_humanity")
    allows = {tuple(pair) for pair in chooser["allows"]}
    prevents = {tuple(pair) for pair in chooser["prevents"]}
    leads = {tuple(pair) for pair in relations["leads_to"]}
    a = option["id"]
    zeroth = ([INJURES_HUMANITY] if a in rows("injures_humanity") else []) + (
        [ALLOWS_HUMANITY_HARM] if any((a, h) in allows for h in humanity) else [])
    first = ([INJURES_HUMAN] if a in rows("injures_human") else []) + (
        [ALLOWS_HUMAN_HARM] if any((a, h) in allows for h in human) else [])
    at_risk = any((a, h) in leads for h, robot in relations["harm_to"] if robot == option["robot"])
    if a not in chooser["permitted"]:
        why, laws = zeroth + first, {law for law, reasons in (("Zeroth", zeroth), ("First", first)) if reasons}
        if first and not zeroth and any((a, h) in prevents for h in humanity):
            why.append(NOT_EXCUSED)
        if a in rows("ordered"):
            why.append(ORDER_YIELDS)
        return "forbidden", why, laws
    why, laws = ([EXCUSED], {"Zeroth"}) if first else ([], set())
    if a in chooser["required"]:
        verdict = "required"
        why.append(ORDERED)
        laws.add("Second")
    elif a in chooser["clear"]:
        verdict = "required" if chooser["clear"] == [a] else "permitted"
    elif chooser["required"]:
        verdict = "ruled out"
        why.append(OTHER_ORDERED)
        laws.add("Second")
    else:
        verdict = "ruled out"
        why.append(SELF_DUTY if at_risk else OPEN_DUTY)
        laws.add("Third")
    if verdict != "ruled out":
        if at_risk:
            why.append(THIRD_YIELDS)
            laws.add("Third")
        if any((a, h) in leads for h in human if h in chooser["unavoidable"]):
            why.append(UNAVOIDABLE)
            laws.add("First")
    return verdict, why, laws


def explain(spec, facts, case, options, report):
    if report.get("status") != "ok":
        raise VEError(f"The checker did not decide this scenario: {report.get('error')}")
    choosers = {c["chooser"]: c for c in report["choosers"]}
    judged = {o["id"]: _judge(o, choosers[o["robot"]], case["model"]) for o in options}
    rows = []
    for o in options:
        verdict, why, _ = judged[o["id"]]
        chooser = choosers[o["robot"]]
        if chooser["clear"] == [o["id"]] and o["id"] not in chooser["required"]:
            others = set().union(*(judged[p["id"]][2] for p in options
                                   if p["robot"] == o["robot"] and p["id"] != o["id"]))
            why = [f"It is the only option left: {_laws(others)} out the others." if others
                   else ONLY_OPTION] + why
        elif verdict == "permitted" and not why:
            why = [NO_LAW]
        consequences = [h["label"] for h in spec["harms"] if [o["id"], h["id"]] in case["model"]["relations"]["leads_to"]]
        rows.append({"id": o["id"], "label": o["label"], "robot": o["robot"], "verdict": verdict,
                     "why": " ".join(why), "consequences": consequences})
    robots = []
    for robot, label in spec["robots"].items():
        chooser = choosers[robot]
        diagnosis = None
        if not chooser["clear"]:
            code = re.match(r"no clear action at \w+: ([A-Z-]+)", chooser["text"])
            diagnosis = NO_CLEAR.get(code and code[1], NO_CLEAR_OTHER)
        robots.append({"id": robot, "label": label, "diagnosis": diagnosis})
    focus = next(row for row in rows if row["id"] == spec["focus"])
    stuck = next(r["diagnosis"] for r in robots if r["id"] == focus["robot"])
    verdict = "no clear action" if stuck else focus["verdict"]
    group = ("limits" if spec["limit"] or stuck else
             "approves" if verdict in ("required", "permitted") else "rejects")
    return {"id": spec["id"], "law": spec["group"], "title": spec["title"],
            "situation": spec["situation"], "limit": spec["limit"], "group": group,
            "facts": [{"id": t["id"], "label": t["label"], "value": facts[t["id"]]}
                      for t in spec["toggles"]],
            "focus": spec["focus"], "verdict": verdict, "why": stuck or focus["why"],
            "robots": robots, "options": rows,
            "checked_by": {"route": "Lean alternatives route", "model_id": report["model_id"],
                           "document_hash": report["document_hash"]}}


def decide(scenario_id, facts=None, *, timeout=30):
    """Run VE on one scenario with the reader's facts; nothing here decides a verdict."""
    if scenario_id not in BY_ID:
        raise VEError("InvalidInput: unknown scenario")
    spec = BY_ID[scenario_id]
    facts = resolve_facts(spec, facts)
    data, document, _, _ = load()
    case, options = situation(spec, facts)
    report = run_case({"id": "asimov-web", "kind": "alt-validate", "environment": data,
                       "norms": _norms(document), "scenario": case}, timeout=timeout)
    return explain(spec, facts, case, options, report)


def _base_environment(data):
    env = deepcopy(data)
    env["profiles"] = ["relational-fol@0"]
    del env["alternatives"]
    env["vocabulary"]["predicates"] = {name: p for name, p in env["vocabulary"]["predicates"].items()
                                       if "regulated" not in p}
    return env


def conflict_check():
    """Prove every conflict target, then let the Lean route replay them for the verdict."""
    data, document, _, _ = load()
    env, norms = Environment(data), _norms(document)
    base = Environment(_base_environment(data))
    case = {"id": "asimov-web", "environment": data, "norms": norms}
    elaborated = run_case({**case, "kind": "alt-elaborate"})
    document_hash = digest(f"ve-alternatives-{env.identity_version}\n", {
        "environment_id": env.environment_id, "norms": norms, "units": []})
    packages = {}
    for target in elaborated["conflict_targets"]:
        conclusion = _bind(Not(_Decoder().decode(target["ast"])), target["sorts"])
        proof = prove_entailment(base, (), conclusion, max_steps=20000)
        if proof.status != "Found":
            return {"verdict": "UNKNOWN", "targets": len(elaborated["conflict_targets"])}
        packages[target["target"]] = {"environment_id": env.environment_id,
                                      "document_hash": document_hash, "target": target["target"],
                                      "certificate": proof.certificate}
    result = run_case({**case, "kind": "alt-conflict", "packages": packages})
    return {"verdict": result["verdict"], "targets": len(packages)}


def _overlay(env):
    return {"format": "ve.english-vocabulary@1", "environment_id": env.environment_id, "sorts": {},
            "predicates": {name: {"verbalisation": text, "suggested": True}
                           for name, text in DISPLAY_WORDING.items()}}


@contextmanager
def _display_parser(env, overlay):
    """Let the norm parser read this environment with the display wording (build time only)."""
    original = english.EnglishVocabulary.__init__

    def init(self, target, vocabulary=None, accept_suggested_vocabulary=False):
        if vocabulary is None and target.environment_id == env.environment_id:
            vocabulary, accept_suggested_vocabulary = overlay, True
        original(self, target, vocabulary, accept_suggested_vocabulary)

    english.EnglishVocabulary.__init__ = init
    try:
        yield
    finally:
        english.EnglishVocabulary.__init__ = original


def natural_rules():
    """VE's rendering of the checked rules, verified to parse back to the same rules."""
    data, document, source, manifest = load()
    env = Environment(data)
    overlay = _overlay(env)
    words = english.EnglishVocabulary(env, overlay, accept_suggested_vocabulary=True)
    numbers = {rule.name: i for i, rule in enumerate(document.rules, 1)}
    checked = render_english(document) == (source, manifest)
    rules, blocks = [], []
    for i, rule in enumerate(document.rules, 1):
        sentence = render_rule_sentence(rule, env, words)
        over = [numbers[name] for name in rule.over]
        header = f"Rule {i}." if not over else (
            f"Rule {i} (exception to rule{'s' if len(over) > 1 else ''} "
            + ", ".join(map(str, over)) + ").")
        blocks.append(header + " " + sentence)
        precedence = (f"Takes precedence over rule{'s' if len(over) > 1 else ''} {_listed(over)}"
                      if over else None)
        rules.append({"number": i, "law": RULE_LAWS[rule.name], "text": sentence,
                      "precedence": precedence, "status": "checked" if checked else "not checked"})
    with _display_parser(env, overlay):
        reread = parse_english(env, "\n".join(blocks))

    def meaning(doc):
        position = {rule.name: i for i, rule in enumerate(doc.rules, 1)}
        return [({k: v for k, v in rule.to_dict()["norm"].items() if k not in ("name", "over")},
                 [position[name] for name in rule.over]) for rule in doc.rules]

    if meaning(reread) != meaning(document):
        raise VEError("The natural view does not read back as the checked rules.")
    return rules


def build():
    conflict = conflict_check()
    return {"format": "ve-web-asimov@1", "quotes": QUOTES, "rules": natural_rules(),
            "document": {"verdict": conflict["verdict"], "targets": conflict["targets"]},
            "groups": GROUPS, "limits": {"note": LIMIT_NOTE, "facts": FACTS_NOTE, "open": OPEN_LIMITS},
            "scenarios": [decide(spec["id"]) for spec in SCENARIOS]}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Regenerate the web app's Asimov section with VE")
    parser.add_argument("--write", action="store_true", help=f"write {OUTPUT.name}")
    args = parser.parse_args(argv)
    text = json.dumps(build(), indent=1, ensure_ascii=False) + "\n"
    if args.write:
        OUTPUT.write_text(text)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
