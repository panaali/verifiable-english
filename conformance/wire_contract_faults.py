"""Additional single-check witnesses derived from soft-norms wire table kinds."""

from conformance.soft_norms import (multi_fault_base, norm, soft4_aggregate_reproducers,
                                   soft4_reproducers, soft3_reproducers)


def derived_faults():
    """(check, environment, norms) with the check as the first fault."""
    def make(check, change):
        environment, norms = multi_fault_base()
        root = {"environment": environment, "norms": norms}
        change(root)
        return check, root["environment"], root["norms"]
    def set_at(path, value):
        def change(root):
            target = root
            for step in path[:-1]:
                target = target[step]
            target[path[-1]] = value
        return change
    E = ("environment",)
    V = E + ("vocabulary",)
    S = V + ("soft",)
    P = V + ("predicates",)
    N = ("norms",)
    changes = [
        ("1.1", lambda r: r["environment"].update(extra=1)),
        ("1.5b", set_at(V + ("sorts",), [])),
        ("1.5c", set_at(V + ("predicates",), [])),
        ("1.5d", set_at(V + ("constants",), [])),
        ("1.6", set_at(("norms",), {})),
        ("1.7", lambda r: r["norms"].extend([r["norms"][0]] * 257)),
        ("2.1b", lambda r: r["environment"]["vocabulary"]["predicates"].update({
            "a__b": r["environment"]["vocabulary"]["predicates"]["x_required"]})),
        ("2.2b", lambda r: r["environment"]["vocabulary"]["predicates"]["q"].update(
            regulated=r["environment"]["vocabulary"]["predicates"]["x_required"]["regulated"])),
        ("2.2c", lambda r: r["environment"]["vocabulary"]["predicates"]["q"].update(defined=["top"])),
        ("2.6", set_at(S + ("parties",), [f"p{i}" for i in range(9)])),
        ("2.8a", set_at(S + ("ranks",), "a")),
        ("2.8b", set_at(S + ("ranks",), [f"r{i}" for i in range(17)])),
        ("2.8c", set_at(S + ("ranks",), ["a", "Bad!"])),
        ("2.9a", set_at(S + ("outranking",), {"mode": "strict", "extra": 1})),
        ("2.11", set_at(S + ("outranking",), {"mode": "holistic", "decided_by": 7})),
        ("2.13", set_at(S + ("outranking",), {"mode": "holistic", "decided_by": ""})),
        ("2.15", set_at(S + ("outranks",), "a")),
        ("2.16a", set_at(S + ("outranks",), [["a"]])),
        ("2.16c", set_at(S + ("outranks",), [["a", "b"], ["a", "b"]])),
        ("2.17a", set_at(S + ("ties",), "a")),
        ("2.17b", set_at(S + ("ties",), [["b"]])),
        ("2.17c", set_at(S + ("ties",), [["b", "b"]])),
        ("3.3a", lambda r: r["environment"].update(profiles=[
            p for p in r["environment"]["profiles"] if p != "relational-fol@0"])),
        ("3.3b", lambda r: r["environment"].update(profiles=[
            p for p in r["environment"]["profiles"] if p != "soft-norms@0"])),
        ("3.4b", lambda r: r["environment"].update(profiles=sorted(
            r["environment"]["profiles"] + ["nary@0"]))),
        ("3.4c", lambda r: r["environment"].update(profiles=sorted(
            r["environment"]["profiles"] + ["order@0"]))),
        ("3.5a", lambda r: (
            r["environment"].update(profiles=sorted(r["environment"]["profiles"] + ["definitions@0"])),
            r["environment"]["vocabulary"]["predicates"]["u"].update(
                defined={"arguments": ["assistant"], "body": ["top"]}))),
        ("3.5b", lambda r: (
            r["environment"].update(profiles=sorted(r["environment"]["profiles"] + ["data@0"])),
            r["environment"]["vocabulary"]["predicates"]["u"].update(
                arguments=["assistant", "assistant"], functional=True))),
        ("4.1a", lambda r: r["norms"][0].update(extra=1)),
        ("4.1b", set_at(N + (0, "norm"), 7)),
        ("4.5a", set_at(N + (1, "norm", "alterable"), "p")),
        ("4.7b", lambda r: r["norms"][1]["norm"].update(hard=True)),
        ("4.9a", lambda r: r["norms"][0]["norm"].pop("exception")),
        ("4.13c", set_at(N + (0, "norm", "exception", "necessary"), "x")),
        ("4.13d", set_at(N + (0, "norm", "exception", "necessary"), [["bad"]])),
        ("4.14a", set_at(N + (0, "norm", "exception", "factors"), [1])),
        ("5.9b", lambda r: r["norms"][3]["norm"].update(over=["a0"])),
        ("6.4b", lambda r: r["environment"]["vocabulary"]["predicates"].update({
            f"z{i}": {"arguments": ["assistant"], "description": "z"} for i in range(248)})),
        ("6.6", lambda r: r["norms"].extend(
            norm(f"z{i}", "x_required", True, over=[f"z{i - 1}"] if i else [])
            for i in range(20))),
    ]
    examples = [make(check, change) for check, change in changes]
    wanted = {"soft4-target-doubling-11": "6.13",
              "soft4-background-premise-nodes-9996": "6.14",
              "soft4-layers-strict-guard-4981": "6.15"}
    for name, environment, norms, _ in (*soft4_aggregate_reproducers(),
                                         *list(soft4_reproducers())[:3]):
        if name in wanted:
            examples.append((wanted[name], environment, norms))
    for name, environment, norms, _ in soft3_reproducers():
        if name == "soft3-rule-nodes-before-exception-condition":
            examples.append(("5.8a", environment, norms))
            break
    environment, _ = multi_fault_base()
    examples.append(("6.7", environment, [
        norm("ra", "x_required", True, guard=["unary", "x_permitted", ["var", 0]]),
        norm("rb", "x_permitted", True, guard=["unary", "x_required", ["var", 0]])]))
    return examples
