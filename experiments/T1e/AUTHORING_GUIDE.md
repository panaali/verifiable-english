# T1e authoring guide (DRAFT, one guide for all three arms)

Adapted from the P3 guide (`experiments/P3-formalisation-tax/AUTHORING_GUIDE.md`), which gave 37/40
first-pass and 8/8 independent-agent sampled agreement. You are the **author**: turn the numbered
prose rules of one access policy into a checkable artefact, so that a checker can decide the claim
"<principal> cannot access <resource>." You are scored by an independent audit: your artefact must
match the prose rule by rule, and it must agree with an independent evaluator of the policy on the
item's own question and on about 100 perturbed fact worlds you do not see. Formalise the **rules**,
not only the answer to this claim.

## What you get

`policy.md` (numbered sections: rules and informational paragraphs), five fact files (`people.csv`,
`teams.yaml`, `roles.json`, `assignments.csv`, `resources.yaml`), `SCHEMA.txt` (how a trusted loader
maps the fact files to relations and tags: you do **not** parse the files yourself), `CLAIM.txt`,
and the template of your arm.

## What you write (every arm)

One artefact file. Inside its policy-rules region, for **every** numbered section, in order:

1. an anchor comment quoting the section verbatim: `<c> §<n>: "<exact sentence>"` (`<c>` is `--` in
   VE, `#` in the script, `%` in Datalog);
2. then either exactly one rule unit for that section, or the line `<c> (informational: no access rule)`
   if the section states no access rule.

A rule unit says when an entity **a** gets the access of an entity **b** it is linked to by one base
relation of the schema: the relation, plus "only if" guards (tag holds) and "unless" guards (tag does
not hold) on a and/or b. An "unless X or Y" clause means neither X nor Y may hold. The access relation
is the union of all rule units; access means one or more steps.

| Arm | File | Rule unit for "Members of a team get its access, unless the team is external." |
|---|---|---|
| VE | `formalisation.vea` | `for every entity x0, (for every entity x1, (if ((x0 member_of x1) and (not (x1 is external))), then (x0 gets_access_of x1))).` |
| Script | `check.py` | `def rule_<n>(a, b):` / `    return rel('member_of', a, b) and (not tag(b, 'external'))` |
| Datalog | `policy.dl` | `access(A, B) :- member_of(A, B), !external(B).` |

Arm specifics:

* **VE.** One statement per rule section, exactly of the form above (strict VE syntax, one line,
  ending with `.`). The trusted checker reads the statements as the only ways to take an access step
  and evaluates `not tc[step](@claimed_principal, @claimed_resource)` on the loaded facts.
  Vocabulary: unary `user group role resource contractor employee suspended external restricted
  privileged temporary confidential public archived`; binary `member_of holds inherits grants
  sponsored_by owns gets_access_of`.
* **Script.** Keep the template's fact helpers (`rel(name, a, b)`, `tag(x, t)`), write one function
  `rule_<n>(a, b)` per rule section returning a Boolean expression, list them in
  `RULES = [...]` after the rules region, and keep or write the closure and query code: the program
  reads the facts JSON on stdin and prints `{"can_access": true|false}` for `FACTS["query"]`. The
  harness executes your program; nobody else checks its closure code.
* **Datalog.** One `access(A, B) :- ...` clause per rule section (negation is `!p(X)`), and the closure
  `reach/2` (one or more `access` steps). The trusted engine evaluates `reach(principal, resource)`.

Check your file (parse, anchors, and the verdict on this item's claim; no expected answer is shown):

```sh
uv run python -m ve_experiments.t1e.run check-artefact --dir <item dir> --arm ve|script|datalog --artefact <file>
```

Iterate as often as the session budget allows; count and report the runs that returned an error.

## Semantics to apply

Closed world: tags and links not in the fact files do not hold. A rule's guards refer to the two linked
entities only ("the member", "the team", "the holder", "the role", "the owner", "the resource", "the
sponsored user", "the sponsoring team", "the inheriting role", "the parent role"). Relation direction
is always from the entity that gains access to the entity whose access it gains (member -> team,
holder -> role, inheriting role -> parent role, role -> granted resource, sponsored user -> sponsoring
team, owner -> resource). Informational sections never change access.
