# Wire contracts (`ve/wire_contract`): statement specification for steps S0 to S3

> Status: statement specification, draft 2 (2026-10-02). This is the item-1 statement spec of
> [wire-contract-PLAN.md](wire-contract-PLAN.md) draft 3, which applies the converged design debate
> (`manage-agents/debates/design-wire/{fable,astra}.md`: BUILD with exact edits, S0 to S3 only, S1c moved to S4).
> It covers the authorised steps only: the contract format and tooling (S0), the Python and Lean engines (S1a,
> S1b), the engine corpus and the generic fault generator (S2), and the `soft-norms@0` pilot (S3). The Astra +
> Fable statement review of draft 1 (`manage-agents/debates/wire-spec/{fable,astra}.md`; Sol at xhigh stood in for
> Astra, as `astra.md` records) returned **FIX with exact edits**. Draft 2 applies those edits, in one commit with
> the plan, and changes nothing else; section 13 maps each edit to its change here. By that review S0 to S3 start
> once the edits have landed as listed, with no further review round; an edit that deviates from the list reopens
> the review, and no stage starts earlier. Theorem statements and fixtures are implementation obligations, not
> claims of completed proofs or tests. Nothing was built or run for this draft: the Lean of section 5 has not been
> compiled, the expected records of section 8 were derived by hand, and the `file:line` references were read on
> branch `design/wire` at `f1ccba52` (those added by draft 2 at `0d0a1022`) and must be re-read at each step.
> Nothing here changes a verdict, an identity, a frozen contract, an existing theorem statement or a checker
> function. Section 12 lists where this draft is more exact than the plan or departs from it.

## 0. Scope, one paragraph

Today the order in which a malformed input's faults are reported is whatever order each hand-written validator
happens to run its checks in, and it differs between Python, Lean and Rust (plan section 1). A **wire contract**
is one JSON file per wire unit that lists the unit's validation checks in order, each with a stable code, a
message template and a path. One small generic **engine** per language runs that table and returns the first
failing check. The existing validators keep deciding accept or reject; the engine is consulted only to choose the
diagnostic of a rejection (the **overlay**). S0 to S3 build the format, the Python and Lean engines, the tests,
and one contract, `soft-norms@0`, whose table already exists as soft-norms.md section 8. Rust and every other
unit wait for a separate decision after the continuation gate (section 9).

In this specification: the decisions (1), the definitions (2), the English, one reading per check (3), the
diagnostics (4), the Lean definitions and exact statements (5), the pilot contract (6), generated artefacts and
gates (7), the acceptance fixtures (8), the continuation gate's metrics (9), limits (10), the statement review
checklist (11), the choices this draft resolves (12), and the statement review's edits (13).

## 1. Decisions

| # | Decision | Where |
|---|---|---|
| D1 | One contract file per wire unit; a contract is an ordered list of phases, each an ordered list of checks, groups and includes | 2.2, 2.3 |
| D2 | The reported diagnostic is the first failing instance of the table expanded over the input; the expansion and its order are defined once, for all engines | 2.6 |
| D3 | The Lean engine is the specification: `run` is defined as "the first failing instance", so the plan's two lemmas are immediate, and two more statements say what the plan claims in words (phases are whole-input; the result depends on hooks only where they are reached) | 5 |
| D4 | Every declarative check is total: on a target that is absent it holds; each kind says which present values it rejects | 2.4 |
| D5 | Guards are conjunctions of literals; type forms are not recursive; literals in a contract are scalars. Nothing in a table needs a recursive evaluator | 2.3 |
| D6 | An `include` is resolved to a scope before any engine runs; a view is a total function and is applied during expansion | 2.5, 2.6 |
| D7 | Three outcomes, never merged: a fault (a check was identified), deferred (this language could not evaluate a hook) and residual (no check explains a legacy rejection) | 2.8 |
| D8 | A hook that passes on an inherited decoder's text is marked `inherited`; its text is language-specific until the base contracts exist, and it does not count towards the gate | 2.5, 9 |
| D9 | A contract carries `status`: `shadow` (records computed, nothing public changes) or `public`. S3 ends in shadow with the delta report; the switch is one separate commit | 2.2, 2.8 |
| D10 | The contract decides the diagnostic, never the verdict or an identity; no module on a verdict path imports the engine | 2.8, 7.3 |

## 2. Definitions

### 2.1 Values, the root, pointers and patterns

**Values.** An engine reads restricted JSON values: `null`, a Boolean, an integer from 0 to 2^53 − 1, a string,
an array, or an object with distinct string keys. This is the domain of `ve.wire.validate_json` and
`VE.JsonInput.parse`, plus `null`: the wire readers reject `null`, but it is the value of an absent root member
and occurs in sources built in process. Two values are **equal** when they have the same JSON type and the same
content: arrays elementwise, objects by the same keys with equal values. Values of different types are never
equal (`false` is not `0`). The Python engine reads a tuple as an array, as `ve/softnorms.py:169` does; on any
other value outside the domain (possible only through the in-process API) it evaluates nothing and reports
`clean`.

**The root.** A contract names its input members, for example `"input": ["environment", "norms"]`. The root is
the object with exactly those members. A member that the submitted case lacks has the value `null`, as
`Json.getObjValD` gives. The unit's input adapter (2.5) builds the root from a route case.

**Pointers.** A pointer is a list of reference tokens from the root, written as in RFC 6901 (`~0` for `~`, `~1`
for `/`); the empty pointer `""` is the root. One step from a value `v` by a token `s`:

- if `v` is an object with a member named `s`, that member;
- if `v` is an array and `s` is the decimal numeral of an index below its length (`0`, or digits without a
  leading zero), that element;
- otherwise nothing.

**Patterns.** A pattern is a base and a list of steps; a step is a token or the wildcard `*`.

| Written | Base |
|---|---|
| `/a/*/b` | the root |
| `@`, `@/a/b` | the item of the innermost enclosing group (2.3) |
| `@1/a`, `@2` | the item of the group one level out, two levels out (`@` is `@0`) |

`matches(P)` is the ordered list of pointers and values the pattern reaches. A token step is the pointer step
above. A `*` step on an array takes every element in index order; on an object, every member in Unicode code point
order of the keys; on any other value, nothing. Code point order is the natural order of all three languages
(`VE.Bridge.fields`, Python `sorted`, Rust `BTreeMap`); it is not the UTF-16 order of the canonical serialiser.
The order in which an author wrote the keys never matters. A base `@n` with fewer than `n + 1` enclosing groups
matches nothing.

A pattern without `*` is a **location**. `resolve(L)` is its one match, or **absent**. `concrete(L)` is the
pointer formed from the base and the tokens without looking at the value; it exists whether or not the location
resolves. A pattern cannot address a key literally named `*`; no VE wire format has one.

### 2.2 The files

```
ve/wire_contract/
  contract.schema.json   the shape of the three file kinds below and of the record (lean_service_schema dialect)
  limits.json            {"MAX_RULES": 256, …}: named non-negative integers
  names.json             {"soft_name": {…}, …}: named lexical classes (2.4)
  <unit>.json            one contract, for example soft-norms@0.json
  examples/<unit>/*.json at least two roots that the unit's legacy validator accepts
  contracts.lock         {"<file>": {"revision": n, "sha256": "…"}} for limits.json, names.json and each contract
  engine.py              the Python engine, the overlay and the hook registry
```

A contract has these members, and no others:

| Member | Meaning |
|---|---|
| `contract` | the unit and its wire version, `soft-norms@0` |
| `revision` | a positive integer, increased by every edit of the file |
| `format` | `1`: the format this section defines |
| `status` | `shadow` or `public` (2.8) |
| `input` | the root's member names, in order |
| `adapter` | optional: the name of the input adapter (2.5) |
| `uses` | the other files it reads: `limits`, `names`, and each included contract |
| `codes` | `{CODE: {"class": C, "summary": S}}`; `C` is one of the `VEError` classes of `ve/errors.py` (`InvalidInput`, `SyntaxError`, `UnknownSymbol`, `DuplicateDeclaration`, `UnboundVariable`, `ShadowedVariable`, `TypeMismatch`, `InvalidModel`, `UnsupportedProfile`, `ResourceLimit`) |
| `residual` | the code of the residual record (2.8), declared in `codes` |
| `phases` | an ordered list of `{"name": N, "checks": [entry, …]}` |

A contract, `limits.json` and `names.json` are read with `ve.wire.loads_json`; a file it refuses is `WC01`.
The SHA-256 in the lock is over `ve.wire.canonical_json` of the parsed file. `limits.json` holds every value a
contract names; where `ve/limits.py` has a constant of the same name the two must be equal, and
`tests/test_wire_contract.py` checks it. `ve/limits.py` stays the value the validators read.

### 2.3 Entries, guards and type forms

A phase's `checks` list holds **entries**. An entry is one of:

| Entry | Form |
|---|---|
| check | `{"id", "kind", "at"?, "when"?, "code", "text", "args"?, "says"?, …the kind's parameters}` |
| group | `{"id", "each": pattern, "when"?, "checks": [entry, …]}` |
| include | `{"id", "kind": "include", "contract", "phases": [names], "at"?, "view"?, "says"?, "as"?}` |

- `id`: letters, digits, `.` and `-`, starting with a letter or digit; unique in the contract; never `residual`.
  The ids of checks and of classifier members (2.5) must increase in table order. Ids are compared part by part
  between dots; a part is split into runs of digits and runs of other characters, and runs are compared in turn,
  digits as numbers and the others as strings, a part that is a prefix of another coming first
  (`2.7 < 2.7a < 2.7b < 2.8 < 2.16`, `b1 < b2`). Where a comparison sets a run of digits against a run of other
  characters (`2.a` against `2.7`, `b1` against `1b`), the order is not defined, and the lint refuses a contract
  in which any two of those ids compare so. Group, include and classifier entry ids need only be unique.
- `at`: a location. Its default is `@` inside a group and the root outside one. It is the check's **target**.
- `each`: a pattern. The group's **items** are its matches, in order. Groups nest.
- `when`: a **guard**, a list of literals that must all hold. An entry whose guard does not hold contributes
  nothing. A group's guard is evaluated once, before its items, in the context that encloses the group.
- `says` on an include: the sentence of its view (3.1). It is required when `view` is present and refused
  otherwise: a `view` without `says` is `WC08`, and `says` without a `view` is `WC01`.

| Literal | Holds when |
|---|---|
| `{"present": L}` | `L` resolves |
| `{"absent": L}` | `L` is absent |
| `{"equals": [L, v]}` | `L` resolves to a value equal to `v` |
| `{"differs": [L, v]}` | `L` is absent, or resolves to a value not equal to `v` |
| `{"is": [L, T]}` | `L` resolves to a value of type `T` |
| `{"is_not": [L, T]}` | `L` is absent, or resolves to a value not of type `T` |

A literal value `v` (here and in `const`, `enum`, `item`) is a scalar: a Boolean, an integer or a string; `null`
is written as the type form `"null"`. That is: "`L` is `null`" is `{"is": [L, "null"]}`, "`L` is not `null`" is
`{"is_not": [L, "null"]}`, and a `const` of `null` is a `type` check with `"null"`. An `enum` that would admit
`null` beside other values is the `enum` over the other values under the guard `{"is_not": [L, "null"]}`, with
`L` the check's target. `requires` and `excludes` have no `null` item. Only the literal is excluded: `null`
stays a value an engine reads (2.1) and a type form (below). A `null` literal, if a later unit needs one, is a
change of `format` with its own statement review.

A **type** `T` is one form or a list of forms, any of which may match:

| Form | Matches |
|---|---|
| `"null"`, `"boolean"`, `"integer"`, `"string"`, `"array"`, `"object"` | a value of that JSON type |
| `{"array_of": A}` | an array whose every element has the atomic type `A` |
| `{"tuple": [A1, …, An]}` | an array of exactly `n` elements, element `i` of atomic type `Ai` |

### 2.4 Declarative checks (tier T1)

For every kind in this table: **if the target is absent, the check holds.** Otherwise it fails exactly when the
condition in the second column is true of the target's value `v`. A failing T1 check therefore always has a
present target, and its `path` is the target's pointer.

| Kind and parameters | Fails when | Extra arguments |
|---|---|---|
| `type` (`type`: T) | `v` is not of type `T` | |
| `exact_keys` (`keys`) | `v` is not an object, or its key set is not exactly `keys` | |
| `keys` (`required`, `optional`) | `v` is not an object, or lacks a required key, or has a key in neither list | |
| `const` (`value`) | `v` is not equal to `value` | |
| `enum` (`values`) | `v` is equal to none of `values` | |
| `max_items` (`limit`) | `v` is an array or object with more than `limit` members | `count`, `limit` |
| `max_bytes` (`limit`) | `v` is a string longer than `limit` bytes in UTF-8 | `count`, `limit` |
| `name` (`class`) | `v` is not a string, or is a string outside the class | |
| `name` (`class`, `"on": "key"`) | the last token of the target's pointer is outside the class | |
| `sorted_unique` | `v` is an array of strings that is not in strictly increasing code point order | |
| `unique_so_far` | an earlier item of the innermost group has an equal value at the same location (see below) | |
| `declared_in` (`set`: pattern) | `v` is equal to none of the values that `set` matches | |
| `requires` (`member`: key) | `v` is an object without that key | |
| `requires` (`item`: value) | `v` is an array with no element equal to `item` | |
| `excludes` (`member`: key) | `v` is an object with that key | |
| `excludes` (`item`: value) | `v` is an array with an element equal to `item` | |

One kind has no target and so no absent case:

| Kind and parameters | Fails when | Path | Extra arguments |
|---|---|---|---|
| `max_count` (`of`: pattern, `limit`) | `of` has more than `limit` matches | `concrete(at)` | `count`, `limit` |

- `limit` is a name in `limits.json` or a non-negative integer.
- `"on": "key"` needs a target whose pointer has a last token. On the empty pointer the check is not defined, and
  the lint refuses it wherever the target's pointer can be empty: `at` has no step, and its base is the root, or
  is a group whose `each`, read in the same way, has no step.
- `unique_so_far` is allowed only inside a group and its `at` must be relative to `@`. "The same location" is
  `at` evaluated with the earlier item in place of the current one; an earlier item where it is absent is not
  equal to anything.
- A **lexical class** in `names.json` is an object with any of the members below. A string is in the class when
  every member present is satisfied. A character set is written as single ASCII characters and ranges, `a-z0-9_`.

| Member | Satisfied when |
|---|---|
| `first` (character set) | the string is not empty and its first character is in the set |
| `rest` (character set) | every character after the first is in the set |
| `min_bytes`, `max_bytes` | the UTF-8 length is at least, at most, the number |
| `forbid_prefix` (list) | the string starts with none of them |
| `forbid_infix` (list) | the string contains none of them |
| `enum` (list) | the string is one of them |

### 2.5 Hooks, classifiers, views and adapters (tiers T2 and T3)

These are hand-written per language and registered by name. The contract fixes where they run and what a failure
reports; the code decides only whether the check holds.

| Entry | Contract form | The hand-written part |
|---|---|---|
| hook (T2) | `{"kind": "hook", "hook": NAME, "returns"?: [names], "inherited"?: true}` | a function of the root and the enclosing items that returns `ok` or `fail(args)`, where `args` gives each name in `returns` a JSON value |
| classifier (T3) | `{"kind": "classifier", "classifier": NAME, "emits": [member, …]}`; a member is `{"id", "code", "text", "returns"?, "inherited"?, "says"}` | a function of the root and the enclosing items that returns `ok` or `fail(member id, args)` |
| view | named by an `include`, which carries its `says` (2.3) | a total function from a value to a value |
| adapter | named by the contract | a function from a route case to the root |

Rules, for every language:

1. A hook or classifier reads only its two arguments. It cannot choose a position, a code, a text or a path. The
   `path` of its record is `concrete(at)`.
2. It may assume that every earlier instance (2.6) holds, and is required to agree across languages only on such
   inputs. The engine never calls it otherwise.
3. A classifier is one existing validator with several internal steps. Its `emits` list states the order of those
   steps; the order actually reported is the validator's own and is checked by tests, not by construction. If the
   function names a member that `emits` does not list, the instance holds; the case then shows as a residual.
4. A view is total: it accepts any value and never fails. It is applied when the table is expanded, before any
   check runs, so it may assume nothing.
5. An **inherited** hook or member runs an inherited decoder at its position and passes its text on: its
   `returns` is exactly `["message"]` and its `text` exactly `{message}`. Until the base contracts exist (plan
   S4, S5) that text differs between languages, so comparisons between engines cover every field of such a
   record except `text` and `args`. This is the "coarse `view` hook" of the continuation gate (9).
6. Lean implements every hook, classifier and view of every contract. Python (and later Rust) may lack one; the
   engine then reports `deferred` (2.8).

### 2.6 Expansion: instances and their order

Before any engine runs, each `include` is **resolved**: it is replaced by a **scope** holding the entries of the
named phases of the included contract, in that contract's order. An included phase may itself include; a cycle is
a lint error, and so is an include with a `view` anywhere inside an included phase (views do not nest).

An **instance** is one check, or one classifier entry, placed at one item: it records the phase, the root it
reads, the enclosing items (innermost first), the earlier items of the innermost group, and the scopes around it.
`instances(table, views, root)` is the list built as follows.

- **Table.** The instances of each phase, in phase order.
- **Phase.** The instances of each of its entries, in order.
- **Check or classifier.** One instance if its guard holds, none otherwise.
- **Group.** None if its guard does not hold. Otherwise, for each item in order: the instances of every
  sub-entry, in order, with that item as the innermost one. All of one item's instances come before the next
  item's (item-major). Two groups in sequence over the same pattern give check-major order.
- **Scope.** None if its `at` is absent. Otherwise the instances of its entries, read against a new root: the
  value at `at`, or the view of that value. Inside a scope there are no enclosing items.

The **position** of an instance is the list (phase index, entry index, item index, sub-entry index, item index,
…) down to the check. The instance list is in strictly increasing lexicographic order of position. A fault for
a classifier member has the position of the member's instance followed by the fault's **order key** inside the
set. An order key is a list of numbers, compared like a position, a list that is a prefix of another coming
first. The fault catalogue (8.3) records the key with the fault; where it records none, the key is the one
number that is the member's index in `emits`. Where a validator does not report in the order of `emits`, the
keys of its set are stated where the contract is specified (section 6, `rule_typing`). The fault generator (8.3)
computes expected diagnostics from positions.

**The one order rule.** The engine evaluates the instances in list order and reports the first that does not
hold. Three consequences, all of which soft-norms.md 8 states in words today:

- no check of a phase runs before every check of the earlier phases has held over the whole input;
- inside a group, one item is checked completely before the next;
- a hook is called only when every earlier instance holds.

### 2.7 The record

```json
{"contract": "soft-norms@0", "revision": 1, "check": "2.7a", "phase": "declarations",
 "code": "SOFT_INVALID_NAME", "class": "InvalidInput", "path": "/environment/vocabulary/soft/parties/1",
 "text": "InvalidInput: invalid soft name Q!", "args": {"value": "Q!"}}
```

| Field | Value |
|---|---|
| `contract`, `revision` | of the contract that was run |
| `check` | the check's id, or the classifier member's id. Under scopes, each include id and a `/` come first, outermost first: `3.4/b1` |
| `phase` | the phase of the contract that was run |
| `code` | the check's code; under an include with `as`, the outermost `as` |
| `class` | the class that the contract declaring `code` gives it |
| `path` | the target's pointer in the submitted input; under includes without a view, the include sites come first. Under an include with a view, `path` is that include's site, and the pointer inside the view goes in `args` as `inner_path` |
| `text` | the check's template with its arguments substituted |
| `args` | an object: each placeholder of the template with its rendered string, plus `inner_path` under a view |

**Templates.** A template is ASCII. A placeholder is `{name}` or `{name:renderer}`; `{{` and `}}` are literal
braces. A name may occur more than once in a template, but under one renderer only: `args` holds one string for
each name, so the lint refuses a template that uses one name under two renderers (`{name}` and `{name:raw}` are
the same renderer). A placeholder names one of:

| Argument | Value |
|---|---|
| `value` | the target's value |
| `key` | the last token of the innermost item's pointer; empty outside a group |
| `index` | the position of the innermost item among its group's items, from 0; `0` outside a group |
| `count`, `limit` | for `max_items`, `max_bytes` and `max_count`: the number found and the limit |
| a name in the check's `args` | `"args": {"name": "@1/norm/name"}`: the value at that location |
| a name in `returns` | the value the hook or classifier returned |

**Renderers.** Each is total. An absent value renders as the empty string under every renderer.

| Renderer | Rendering |
|---|---|
| `raw` (the default) | a string as it is, uncut; any other value as `json` |
| `json` | compact JSON: no spaces; object keys in code point order; in strings only `"`, `\` and the characters below U+0020 are escaped (`\"`, `\\`, `\u00xx` in lower case). If the result is longer than 80 bytes in UTF-8, it is cut to the longest prefix of whole characters within 80 bytes and `...` is added |
| `index`, `count` | an integer in decimal; any other value as `json` |
| `list` | an array of strings: sorted by code point and joined by a comma and a space; any other value as `json` |

Records are compared as `ve.wire.canonical_json` bytes.

### 2.8 Outcomes and the overlay

An engine's **outcome** on a root is one of:

| Outcome | Meaning |
|---|---|
| `fault(record)` | the first instance that does not hold is a check this engine evaluated |
| `clean` | every instance holds |
| `deferred(id)` | Python and Rust only: every earlier instance holds, and the instance at `id` needs a hook, classifier or view this language does not have (for a view, `id` is the include's id) |

A fault found before the first deferred instance is final. The Lean engine never defers. A scope whose view
this language lacks cannot be expanded; it contributes one instance in its place, at the scope's position, and
that instance defers.

The **overlay** turns the legacy validator's result and the engine's outcome into what is reported. The legacy
validator's code is not changed and it alone decides accept or reject.

| Legacy validator | Engine | Reported |
|---|---|---|
| accepts | any | nothing. In tests, an outcome other than `clean` from an engine that completes diagnosis is a contract defect (plan C2) |
| rejects with text `m` | `fault(r)` | `r` |
| rejects with text `m` | `clean` | the **residual record**: `check` and `phase` are `residual`, `code` is the contract's `residual` code with its class, `path` is `""`, `text` is `m`, `args` is `{}` |
| rejects with text `m` | `deferred(id)`, and Lean answers | Lean's outcome, read by the two rows above |
| rejects with text `m` | `deferred(id)`, and Lean is not consulted or cannot answer | the **deferred record** `{"contract", "revision", "deferred": id, "text": m}` |

A deferred record has no `check`, `code` or `path`: the engine has not identified the first failing check. It is
counted under the deferred share of its language and never under residual. The residual count is a gated metric
(9); a residual means the contract lacks a check that the legacy validator has.

**Status.** While a contract's `status` is `shadow`, the overlay's result is available to tests and reports only,
and no public output changes. When it is `public`, Python sets `VEError.diagnostic` to the reported record and
`VEError.message` to its `text` (4.2). Changing `status` is a contract edit: it raises the revision and is the
switch commit of plan 5.1, step 6.

### 2.9 What is constructed and what is tested

By construction, given the same contract revision:

- **(A) Expansion.** The instance list is a function of the table, the views and the root (2.6). Two engines
  that implement 2.1 to 2.6 produce the same list.
- **(B) The record, conditional on equal predicate results.** If two engines have the same views, equal on every
  value and not only where a view is reached, and every hook and classifier that is reached returns the same
  result in both, they report the same record: same position, code, path and text. In Lean this is
  `run_congr_reached` (5.3), whose hypothesis on views is equality on every name and value. For Python it is
  evidence from the engine corpus (8.1).

Tested, not constructed:

- whether a hook holds on a given input (per-hook differential tests, 8.3);
- the order inside a classifier set, which is the existing validator's;
- the text of an inherited hook or member, which is the inherited decoder's;
- the fault order of the raw JSON scanners, which is open and outside S0 to S3 (plan question 7).

## 3. English: one reading per check

The contract is data, and people read it in two places: the generated tables in the specs (plan section 3) and,
once a contract is public, the plain-language expectation shown beside a diagnostic. Both use the wordings of
this section. `tools/wire_contract.py` generates them; no wording is typed twice. In S0 to S3 only the generated
spec table of soft-norms.md 8 uses them; no reader-facing surface changes.

### 3.1 Generated wordings

A location is written in code font. An absolute one is written whole: `/environment/profiles`. Inside a group,
an item is named by the id of its group: `@` is "the `g` item", where `g` is the innermost group's id, `@/a/b`
is "the `g` item's `a/b`", and `@1` and `@1/a` name the group one level out in the same way. Below, `W` stands
for the target so written. (Revised after the wire review, Astra B and Fable B5: with "the item" and "the
enclosing item", the sentences of 2.16b and 2.16c were the same words with two different groups.)

| Kind | Wording pattern | The one reading |
|---|---|---|
| `type` | `W, when present, is <type>.` with `<type>` one of `null`, `a Boolean`, `an integer`, `a string`, `an array`, `an object`, `an array of <plural>`, `an array of exactly <n> elements: <type>, …`; alternatives joined by `or` | If there is no value at W the check holds. If there is one, it must have that JSON type. "When present" governs the whole sentence |
| `exact_keys` | `W, when present, is an object with exactly the keys <keys>.` | An object whose key set is that set; a missing or an extra key fails, and so does a value that is not an object |
| `keys` | `W, when present, is an object with the keys <required> and no other key except <optional>.` (`and no other key.` when there is no optional key) | Every required key occurs; every key that occurs is listed. The optional keys may be missing |
| `const` | `W, when present, is <value>.` | Equal in type and content |
| `enum` | `W, when present, is one of <values>.` | Equal to one of them |
| `max_items` | `W, when it is an array or an object, has at most <n> members (<LIMIT>).` | Other values, and no value, hold |
| `max_bytes` | `W, when it is a string, is at most <n> bytes long in UTF-8.` | Bytes, not characters |
| `max_count` | `There are at most <n> values at <pattern> (<LIMIT>).` | The number of matches of the pattern |
| `name` | `W, when present, is a string in the class <class>.` | A value that is not a string fails |
| `name` on key | `The key of W is in the class <class>.` | The key under which W sits in its parent |
| `sorted_unique` | `W, when it is an array of strings, is in strictly increasing code point order.` | Strictly increasing rules out repeats |
| `unique_so_far` | `W, when present, differs from the value at the same place in every earlier `g` item.`, and inside a second group `… item of the same `g1` item.` | Only earlier items are compared, so the second of two equal items fails and the first does not; under an enclosing group, only items of the same enclosing item |
| `declared_in` | `W, when present, equals one of the values at <pattern>.` | The set is read from the input, not from the contract |
| `requires` | `W, when it is an object, has the key <key>.` / `W, when it is an array, contains <value>.` | |
| `excludes` | `W, when it is an object, has no key <key>.` / `W, when it is an array, does not contain <value>.` | |
| guard | `When <literal> and <literal>: ` before the sentence; literals read `<L> is present`, `<L> is absent`, `<L> is <value>`, `<L> is absent or is not <value>`, `<L> is <type>`, `<L> is absent or is not <type>` | When the guard does not hold the check is not run and does not fail |
| group | `Group `g`, when <literals>: its item is each member of <W>, in order; checks <first> to <last> run on one item before the next item.`; `each value at <pattern>` when the pattern has a `*` before its last step; no `when` clause without a guard | Item-major order. "In order" is index order for an array and code point order of keys for an object. The checks named are every check of the group, so the group's end is stated. In the generated table a row inside a group starts with one `·` per enclosing group |
| phase | `**Phase <n>, <name>.** No check of this phase runs unless every check of the earlier phases holds over the whole input.` | |
| include | `The checks of phase <names> of <contract>, in their order, on W` then, with a view, ` as transformed by the view <view>: <says>`, where the `says` sentence closes the sentence, and without a view `.`; then, with `as`, the sentence `They are reported with code <code>.` | Without a view the included checks read the value at W. With a view they read the value that `says` states, and nothing else of W |
| hook, classifier member | the check's `says`, written by hand; inside groups preceded by `For the `g` item of the `g1` item: ` | "The item" in a `says` sentence is the innermost group's item, which the lead names |

A hook, a classifier member and a view have no parameters to generate a sentence from, so the contract carries a
`says` sentence for each, and the lint refuses one without it. A view's sentence is the `says` of the include
that names it (2.3). A `says` sentence states what must hold, in the present tense, with one reading, and its
review is part of the contract's review; for a view, `says` states the value the included checks read.

### 3.2 Wordings this replaces, and why

These are in the specs today or were candidates. Each has two readings, and the generated form has one.

| Wording | Its two readings | Generated instead |
|---|---|---|
| "Each party is a soft name and not repeated." | every name is checked and then every repeat (check-major), or both checks for one party before the next (item-major). The first diagnostic differs when party 1 repeats party 0 and party 2 is malformed | the group sentence of 3.1 with two sub-entries |
| "`decided_by` is a string." | a missing `decided_by` fails, or holds | "…, when present, is a string." |
| "`profiles` is sorted and unique." | sorted by code point, or by UTF-16 unit; they differ outside the BMP | "… is in strictly increasing code point order." |
| "The reported diagnostic is the first failing check in table order; where one check applies to several items, the first failing item." | with two checks over the same items, "table order" and "item order" pull in different directions | the phase and group sentences, which fix it for each group |
| "A hard rule is strict and has no `alterable`." | a rule that is not hard must also be strict, or is not constrained | "When the item's `norm/hard` is `true`: …" |

### 3.3 The three outcomes, in plain words

Any surface that shows an outcome to a person uses these sentences. They contain no notation; a check id is a
name, like a rule name.

| Outcome | Sentence | What it does not say |
|---|---|---|
| fault | `This input is rejected. The first check that fails is <id>: <the check's wording>` | It does not say this is the only fault. Other checks may fail too and are not reported |
| deferred | `This input is rejected. This program cannot tell which check fails first, because it cannot run check <id> itself. The message shown comes from the validator, not from the table.` | It does not say check `<id>` fails |
| residual | `This input is rejected, but no check in the table fails. The message shown comes from the validator, not from the table.` | It does not say the input is valid: the rejection stands |

"First" always means the order of 2.6.

### 3.4 Message templates

A check's `text` is the message that today's validators print (`InvalidInput: invalid soft name Q!`). Revision 1
of a migrated contract keeps today's text wherever the implementations agree on it, so that the delta report is
short. A template is ASCII and uses only the placeholders of 2.7. No string that lands in a generated Lean file
(an id, a code, a class, a phase name, a hook name, a text) may contain, as a whole word, a token that
`lean/audit.py` forbids; the tool imports `FORBIDDEN` from `lean/audit.py` and keeps no list of its own. The
text is not the plain-language expectation: that is the wording of 3.1.

## 4. Diagnostics

### 4.1 The three records

The fault record is in 2.7. The other two, for a contract `demo@0` at revision 1 and a legacy text
`legacy says no`:

```json
{"contract": "demo@0", "revision": 1, "check": "residual", "phase": "residual",
 "code": "DEMO_INVALID_INPUT", "class": "InvalidInput", "path": "", "text": "legacy says no", "args": {}}
```

```json
{"contract": "defer@0", "revision": 1, "deferred": "d2", "text": "legacy says no"}
```

`contract.schema.json` defines all three shapes. A consumer tells them apart by the member `deferred` and by
`check` being `residual`.

### 4.2 Where a record appears

| Place | Shape | In S0 to S3 |
|---|---|---|
| Python, in process | `engine.run(contract, root)` returns `Fault(record)`, `Clean` or `Deferred(id)`; `engine.overlay(contract, legacy_error, outcome, lean=None)` returns a record or `None` | built in S1a |
| Python, public | `VEError.diagnostic`, `None` by default; `VEError.to_dict()` adds the member `diagnostic` only when it is set. `code` keeps its present value in every unit (on the soft route that already is the `SOFT_…` code). When `diagnostic` is set, `message` is the record's `text` | the attribute exists from S1a; it is set only for a contract whose `status` is `public`, and the call that sets it is added by the switch commit, so no output changes during S0 to S3 |
| Lean | `ve_diagnose <unit> [cases.json\|-]` prints one row per case: `{"id": …, "status": "ok", "outcome": "fault", "diagnostic": {…}}` or `{"id": …, "status": "ok", "outcome": "clean"}` | built in S1b |

`ve_diagnose` reads the same case JSON as the unit's route, through `VE.JsonInput.parseCases`. Error rows have
the runners' existing forms: `{"status": "error", "case_index": i, "error": "…"}` for a case that is not
restricted JSON, and `{"id": …, "status": "error", "error": "UnsupportedProfile: case kind <kind> has no wire
contract input"}` for a case whose kind the unit's adapter does not know. Exit status: 0 when every row is `ok`,
1 when a row is an error, 2 for a usage error or an unknown unit (`UnsupportedProfile: no wire contract <unit>`
on standard error). Rows keep `status` within `ok` and `error` so that `ve.backends.lean.run` accepts them
unchanged; the outcome is its own member (12, R8). The legacy runners' rows do not change by a byte.

The assurance manifest gains one operation, `wire.diagnose`: Lean only, no verdict, bound to the executable
`ve_diagnose`. If it is unavailable, the overlay's last row applies: the overlay catches `CheckerUnavailable`
from this one operation and reports the deferred record. The rejection was already decided by the legacy
validator, so an unavailable diagnoser never changes a verdict and never turns a rejection into an operational
failure.

### 4.3 Tool diagnostics

`tools/wire_contract.py --check` validates, lints, regenerates in memory and compares; `--write` writes the
generated files, the lock and the inventory lines of generated modules. It exits 0 or 1 and prints one line per
finding, `<file>: <code>: <detail>`.

| Code | Refuses |
|---|---|
| `WC01` | a file that `ve.wire.loads_json` refuses (2.2; for example a `null`, a negative or fractional number, or a repeated key); a file that does not have the shape of 2.2 to 2.5 (`contract.schema.json`), which includes `says` on an include without a `view` |
| `WC02` | a repeated id; an id with a character outside 2.3 or equal to `residual`; check and member ids that do not increase in table order; two check or member ids whose comparison sets a run of digits against a run of other characters (2.3) |
| `WC03` | a code that is used and not declared, or declared and not used (the `residual` code counts as used); a class outside the list of 2.2 |
| `WC04` | a placeholder that names no argument of 2.7 for that check; an entry of `args` or `returns` that no placeholder uses; an unknown renderer; one argument name under two renderers in one template; an argument location with `*`; a template that is not ASCII or has unbalanced braces |
| `WC05` | an unknown limit or lexical class; a class or character set that 2.4 does not allow (a negative limit is refused by the reader, as `WC01`) |
| `WC06` | `@n` with fewer than `n + 1` enclosing groups; `unique_so_far` outside a group or with an `at` not relative to `@`; an `at` with `*`; `"on": "key"` on a target whose pointer can be empty (2.4); a literal value that is not a scalar |
| `WC07` | a string bound for a generated Lean file that contains a token of `lean/audit.py`'s `FORBIDDEN` as a whole word |
| `WC08` | a hook, a classifier member or an include with a `view`, without `says`; an `inherited` hook or member whose `returns` is not `["message"]` or whose `text` is not `{message}`; a hook or member with no fault in the fault catalogue (8.3) |
| `WC09` | an include of an unknown contract or phase, or of a contract missing from `uses`; an include cycle; an include with a `view` inside an included phase; an `as` code that is not declared |
| `WC10` | a file whose hash differs from the lock; changed content with an unchanged revision; fewer than two examples; an example on which the Python engine does not report `clean` |
| `WC11` | a generated file that differs from regeneration |

A contract whose lock entry does not match is a packaging error: `engine.load` raises `RuntimeError`, which is
neither a `VEError` nor a verdict.

## 5. Lean: definitions and the exact statements

**Namespace as built.** The modules live in `lean/VE/WireContract/` and the namespace is `VE.WireContract`;
wherever sections 5 and 7 write `VE.Contract` (a path, a module, a namespace or a qualified name), the build
reads `VE.WireContract`. The statements of 5.3 are built with the formulas shown, so their qualified names are
`VE.WireContract.run_clean_iff`, `VE.WireContract.run_fault_first`, `VE.WireContract.run_phase_major` and
`VE.WireContract.run_congr_reached` (section 14, C1).

**Files.** `lean/VE/Contract/Table.lean` (the data types; no JSON, no theorems), `Engine.lean` (pointers,
expansion, evaluation, `run`, the theorems), `Diagnose.lean` (the unit registry and the runner),
`Hooks/SoftNorms.lean` and `Hooks/Corpus.lean` (hand-written hooks, views and adapters),
`Tables/SoftNorms.lean` and `Tables/Corpus.lean` (generated, 7.1), `Limits.lean` and `Names.lean` (generated
constants, for hooks and for the LIMITS CONTRACT item), and `lean/DiagnoseMain.lean`, the root of the new
`lean_exe` `ve_diagnose`. **Naming.** No primes, and none of the audit's forbidden words, in comments either.
Field names avoid Lean keywords (`loc` for `at`, `cls` for `class`). The plan's schemata named `holds` and
`diagnosticOf`; here one function `eval` returns the finding of an instance that does not hold, and `Holds` is
defined from it.

### 5.1 Table data

```lean
namespace VE.Contract

abbrev Pointer := List String          -- unescaped RFC 6901 reference tokens, from the root

inductive Step where
  | tok (s : String)
  | star

inductive Base where
  | root
  | item (n : Nat)                     -- the item of the n-th enclosing group; 0 is the innermost

structure Pattern where
  base : Base
  steps : List Step

inductive Value where                  -- a scalar literal of a contract (2.3); it has no `null`
  | bool (b : Bool) | int (n : Nat) | str (s : String)

inductive Atom where
  | null | boolean | integer | string | array | object

inductive TypeForm where
  | atom (a : Atom)
  | arrayOf (a : Atom)
  | tuple (parts : List Atom)

inductive Lit where
  | present (p : Pattern)
  | absent (p : Pattern)
  | equals (p : Pattern) (v : Value)
  | differs (p : Pattern) (v : Value)
  | isType (p : Pattern) (t : List TypeForm)
  | notType (p : Pattern) (t : List TypeForm)

structure NameClass where
  first : Option (List (Nat × Nat))    -- inclusive code point ranges
  rest : Option (List (Nat × Nat))
  minBytes : Option Nat
  maxBytes : Option Nat
  forbidPrefix : List String
  forbidInfix : List String
  oneOf : Option (List String)

inductive Renderer where
  | raw | json | index | count | list

inductive Piece where
  | lit (s : String)
  | arg (name : String) (r : Renderer)

structure Member where                 -- one check of a classifier set (2.5)
  id : String
  code : String
  cls : String
  text : List Piece
  inherited : Bool

inductive Kind where
  | hasType (t : List TypeForm)
  | exactKeys (keys : List String)
  | keys (required optional : List String)
  | const (v : Value)
  | oneOf (vs : List Value)
  | maxItems (limit : Nat)
  | maxBytes (limit : Nat)
  | maxCount (pattern : Pattern) (limit : Nat)
  | name (cls : NameClass) (onKey : Bool)
  | sortedUnique
  | uniqueSoFar
  | declaredIn (set : Pattern)
  | requiresMember (key : String)
  | requiresItem (v : Value)
  | excludesMember (key : String)
  | excludesItem (v : Value)
  | hook (name : String)
  | classifier (name : String) (emits : List Member)

structure Check where
  id : String
  loc : Pattern                        -- `at`
  guard : List Lit                     -- `when`
  kind : Kind
  code : String
  cls : String
  text : List Piece
  args : List (String × Pattern)
  inherited : Bool

inductive Entry where
  | check (c : Check)
  | each (id : String) (over : Pattern) (guard : List Lit) (entries : List Entry)
  | scope (id : String) (loc : Pattern) (view : Option String) (recode : Option (String × String))
      (entries : List Entry)           -- a resolved `include`; `recode` is the `as` code and its class

structure Phase where
  name : String
  entries : List Entry

structure Table where
  contract : String
  revision : Nat
  residual : String × String           -- the residual code and its class
  phases : List Phase

end VE.Contract
```

A generated table has every limit as a numeral, every lexical class and every code's class written out, and every
template already split into pieces, so a table module is self-contained and `run` reads no other data.

### 5.2 The engine

```lean
-- Engine.lean imports VE.Bridge and VE.Contract.Table, and nothing else of VE.
namespace VE.Contract
open Lean

inductive HookResult where
  | ok
  | fail (args : List (String × Json))

inductive ClassifierResult where
  | ok
  | fail (member : String) (args : List (String × Json))

/-- The hand-written predicates of a unit (2.5). Each receives the value its instance reads and the enclosing
    items, innermost first. For a name the unit does not define, `predicate` and `classifier` give `ok` and
    `view` gives the identity. -/
structure Hooks where
  predicate : String → Json → List Pointer → HookResult
  classifier : String → Json → List Pointer → ClassifierResult
  view : String → Json → Json

/-- How pointers under resolved includes map back to the submitted input (2.7). -/
structure Frame where
  ids : List String                    -- include ids, outermost first
  site : Pointer                       -- the sites of the enclosing includes without a view, concatenated
  viewSite : Option Pointer            -- the site of the enclosing include with a view
  recode : Option (String × String)    -- the outermost `as`

def Frame.top : Frame := ⟨[], [], none, none⟩

/-- The frame inside an include whose site is `p`: `ids` gains `id`; the outermost `recode` is kept; with a
    view and no view yet, `viewSite` becomes `site ++ p` and `site` restarts empty; otherwise `site` gains `p`. -/
def Frame.enter (f : Frame) (id : String) (p : Pointer) (view : Option String)
    (recode : Option (String × String)) : Frame

structure Instance where
  phase : String
  check : Check
  root : Json                          -- the input, or the value under a scope
  items : List Pointer                 -- enclosing group items, innermost first
  earlier : List Pointer               -- the earlier items of the innermost group, in order
  frame : Frame

structure Finding where                -- a record (2.7) without `contract` and `revision`
  check : String
  phase : String
  code : String
  cls : String
  path : String
  text : String
  args : List (String × String)

/-- 2.1: every match of a pattern with its pointer, in order; an object's members in the order of
    `VE.Bridge.fields`. -/
def collect (root : Json) (items : List Pointer) (p : Pattern) : List (Pointer × Json)
/-- 2.1: the one match of a pattern without `star`, or `none` when it is absent. -/
def resolve (root : Json) (items : List Pointer) (p : Pattern) : Option (Pointer × Json)
/-- 2.3: every literal of the guard holds. -/
def guardHolds (root : Json) (items : List Pointer) (g : List Lit) : Bool
/-- Each element with the elements before it: `[a, b, c] ↦ [([], a), ([a], b), ([a, b], c)]`. -/
def withEarlier {α : Type} : List α → List (List α × α)

mutual
/-- 2.6: the instances of one entry, in order. -/
def expand (h : Hooks) (phase : String) (root : Json) (items earlier : List Pointer) (frame : Frame) :
    Entry → List Instance
  | .check c =>
    if guardHolds root items c.guard then [⟨phase, c, root, items, earlier, frame⟩] else []
  | .each _ over guard entries =>
    if guardHolds root items guard then
      (withEarlier ((collect root items over).map (·.1))).flatMap fun (before, p) =>
        expandAll h phase root (p :: items) before frame entries
    else []
  | .scope id loc view recode entries =>
    match resolve root items loc with
    | none => []
    | some (p, v) =>
      expandAll h phase (match view with | none => v | some name => h.view name v) [] []
        (frame.enter id p view recode) entries
/-- 2.6: the instances of each entry of a list, in list order. -/
def expandAll (h : Hooks) (phase : String) (root : Json) (items earlier : List Pointer) (frame : Frame) :
    List Entry → List Instance
  | [] => []
  | e :: es =>
    expand h phase root items earlier frame e ++ expandAll h phase root items earlier frame es
end

/-- 2.6: the table expanded over the input. -/
def instances (t : Table) (h : Hooks) (j : Json) : List Instance :=
  t.phases.flatMap fun p => expandAll h p.name j [] [] Frame.top p.entries

/-- 2.4, 2.5, 2.7: `none` when the instance holds, otherwise its finding. For a `hook` or `classifier` it calls
    `h` once; for every other kind it does not use `h`. -/
def eval (h : Hooks) (i : Instance) : Option Finding

def Holds (h : Hooks) (i : Instance) : Prop := eval h i = none

/-- The engine: the finding of the first instance that does not hold. -/
def run (t : Table) (h : Hooks) (j : Json) : Option Finding :=
  (instances t h j).findSome? (eval h)

/-- 2.7: the record of a finding, with the table's `contract` and `revision`. -/
def record (t : Table) (f : Finding) : Json

end VE.Contract
```

`expand` and `expandAll` are written as their defining equations. How Lean is told that they terminate
(structural recursion on the nested type, or a measure) is the builder's choice, and must not change the
equations. `eval` has no body here: its value on each kind is fixed by 2.4, 2.5 and 2.7, and the engine corpus
(8.1) is its acceptance test.

### 5.3 The statements

```lean
namespace VE.Contract
open Lean

/-- The plan's first lemma: the engine reports nothing exactly when every instance holds. -/
theorem run_clean_iff (t : Table) (h : Hooks) (j : Json) :
    run t h j = none ↔ ∀ i ∈ instances t h j, eval h i = none

/-- The plan's second lemma: a reported finding is that of an instance before which every instance holds. -/
theorem run_fault_first (t : Table) (h : Hooks) (j : Json) (d : Finding) :
    run t h j = some d ↔
      ∃ pre i post, instances t h j = pre ++ i :: post ∧ eval h i = some d ∧
        ∀ b ∈ pre, eval h b = none

/-- Phases are whole-input: a later phase is consulted only when the earlier phases report nothing. -/
theorem run_phase_major (t : Table) (ps qs : List Phase) (h : Hooks) (j : Json)
    (ht : t.phases = ps ++ qs) :
    run t h j = (run { t with phases := ps } h j).or (run { t with phases := qs } h j)

/-- Claim (B) of 2.9: two hook sets with the same views, which agree on every instance that is reached,
    give the same result. Hooks after the first instance that does not hold are never consulted. -/
theorem run_congr_reached (t : Table) (h g : Hooks) (j : Json)
    (hv : ∀ name v, h.view name v = g.view name v)
    (hr : ∀ pre i post, instances t h j = pre ++ i :: post →
            (∀ b ∈ pre, eval h b = none) → eval h i = eval g i) :
    run t h j = run t g j

end VE.Contract
```

What these do and do not say:

- They are statements about the Lean engine and any table. They say nothing about Python, about a hook's
  correctness, or about a legacy decoder. No theorem relates a contract to its decoder (plan 3.2); that relation
  is tested in both directions (8.3).
- `run_clean_iff` and `run_fault_first` follow from the definition of `run` by the library facts about
  `List.findSome?`. They are stated because the plan promises them and so that the audit lists them, not because
  they are hard. `run_fault_first` uses a split of the list where the plan wrote an index, which avoids a bound
  proof and says the same.
- `run_phase_major` and `run_congr_reached` are the two sentences of the plan that were prose: "a phase starts
  only when every check of the earlier phases has passed over the whole input", and "by construction,
  conditional on equal predicate results".
- The theorems are optional, as the debate fixed (plan C4). If they are added, each one and every helper
  `theorem` is recorded in `VE/Audit.lean` by lines that are only added, with axioms within `propext`,
  `Classical.choice` and `Quot.sound`. If they are dropped, `VE/Audit.lean` is not touched and the engine corpus
  is the Lean engine's evidence too.

One check at build time, not a theorem: `Hooks/SoftNorms.lean` ends with a `#guard` that every hook, classifier
and view name occurring in `Tables.SoftNorms.table` is one it registers, so a contract that names an unregistered
hook fails `lake build`. `Hooks/Corpus.lean` has the same guard for the corpus tables.

## 6. The pilot contract `soft-norms@0`, revision 1

**Root and entry.** `"input": ["environment", "norms"]`, adapter `soft_source`. For a `soft-elaborate` case the
root's members are the case's; for an `admission` case on the soft path, `norms` is the active norm units that
`VE.Norms.Admission.splitDocument` returns, as `Run.reportedCode` does today (`SoftNorms/Run.lean:344–352`). A
standalone environment is checked with `norms` `[]`. The **legacy validators** are `Wire.decodeSoftSource` in
Lean and `load_soft_document` in Python; neither is edited.

**Limits and classes used.** `limits.json`: `MAX_RULES` 256, `MAX_SOFT_PARTIES` 8, `MAX_SOFT_RANKS` 16,
`MAX_FACTOR_BYTES` 200 (literals in both validators today). `names.json`:

| Class | Definition |
|---|---|
| `soft_name` | `first` `a-z`; `rest` `a-z0-9_`; `max_bytes` 64; `forbid_infix` `__` |
| `not_soft_reserved` | `forbid_prefix` `soft__` |
| `no_double_underscore` | `forbid_infix` `__` |
| `decider` | `min_bytes` 1; `max_bytes` 64 |

**Codes.** The 26 codes of soft-norms.md 8, unchanged. Their classes follow the Python exception classes that
the soft checks raise today. An inherited check's exception keeps whatever class its decoder raises; the record's
`class` is the code's.

| Class | Codes |
|---|---|
| `UnsupportedProfile` | `SOFT_UNSUPPORTED_PROFILE` |
| `ResourceLimit` | `SOFT_RESOURCE_LIMIT` |
| `DuplicateDeclaration` | `SOFT_DUPLICATE_DECLARATION` |
| `UnknownSymbol` | `SOFT_UNKNOWN_PARTY` |
| `InvalidInput` | the other 22; `SOFT_INVALID_INPUT` is the `residual` code |

**The table.** `S` abbreviates `/environment/vocabulary/soft` and `P` abbreviates
`/environment/vocabulary/predicates`. A row "group" opens a group; its sub-entries follow, indented by `·`, until
the next row that is not indented. `{name}` is the argument `"name": "@/norm/name"` (or `@1/norm/name` one group
further in). The texts are those of `Phases.lean` today.

Phase 1, `envelope`:

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 1.1 | `exact_keys` `/environment`: `language`, `profiles`, `spec_revision`, `vocabulary` | `SOFT_INVALID_INPUT` | `InvalidInput: invalid environment envelope` |
| 1.2 | `const` `/environment/language`: `"ve.core@0.2"` | `SOFT_UNSUPPORTED_PROFILE` | `UnsupportedProfile: Unsupported language` |
| 1.3 | `type` `/environment/profiles`: array of strings | `SOFT_UNSUPPORTED_PROFILE` | `UnsupportedProfile: profiles must be a sorted unique array` |
| 1.4 | `const` `/environment/spec_revision`: `"ve-v0.2-expand2-2026-09-25"` | `SOFT_UNSUPPORTED_PROFILE` | `UnsupportedProfile: Unsupported specification revision` |
| 1.5a | `keys` `/environment/vocabulary`: required `sorts`, `predicates`, `constants`; optional `soft` | `SOFT_INVALID_INPUT` | `InvalidInput: invalid vocabulary` |
| 1.5b–d | `type` object at `…/sorts`, `…/predicates`, `…/constants` | as 1.5a | as 1.5a |
| 1.6 | `type` `/norms`: array | `SOFT_INVALID_INPUT` | `InvalidInput: expected an array of norm objects` |
| 1.7 | `max_items` `/norms`: `MAX_RULES` | `SOFT_RESOURCE_LIMIT` | `ResourceLimit: rules` |

Phase 2, `declarations`:

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| | group `P/*` | | |
| · 2.1a | `name` on key: `not_soft_reserved` | `SOFT_INVALID_NAME` | `InvalidInput: invalid soft name {key}` |
| · 2.1b | `name` on key: `no_double_underscore`, when `@/regulated` is present | as 2.1a | as 2.1a |
| | group `P/*` | | |
| · 2.2a | `type` `@/instruction_of`: string | `SOFT_INVALID_INPUT` | `InvalidInput: instruction_of on {key}` |
| · 2.2b | `excludes` `@` member `regulated`, when `@/instruction_of` is present | as 2.2a | as 2.2a |
| · 2.2c | `excludes` `@` member `defined`, same guard | as 2.2a | as 2.2a |
| 2.3 | hook `w1_declarations` at `/environment`, inherited | `SOFT_INVALID_INPUT` | `{message}` |
| 2.4 | `keys` `S`: required `outranking`; optional `parties`, `ranks`, `outranks`, `ties`, `exception_decider` | `SOFT_INVALID_BLOCK` | `InvalidInput: invalid soft block` |
| 2.5 | `type` `S/parties`: array | `SOFT_INVALID_ARRAY` | `InvalidInput: parties must be an array` |
| 2.6 | `max_items` `S/parties`: `MAX_SOFT_PARTIES` | `SOFT_RESOURCE_LIMIT` | `ResourceLimit: parties` |
| | group `S/parties/*` | | |
| · 2.7a | `name`: `soft_name` | `SOFT_INVALID_NAME` | `InvalidInput: invalid soft name {value}` |
| · 2.7b | `unique_so_far` | `SOFT_DUPLICATE_DECLARATION` | `DuplicateDeclaration: party {value}` |
| 2.8a | `type` `S/ranks`: array | `SOFT_INVALID_ARRAY` | `InvalidInput: ranks must be an array` |
| 2.8b | `max_items` `S/ranks`: `MAX_SOFT_RANKS` | `SOFT_RESOURCE_LIMIT` | `ResourceLimit: ranks` |
| | group `S/ranks/*` | | |
| · 2.8c | `name`: `soft_name` | `SOFT_INVALID_NAME` | `InvalidInput: invalid soft name {value}` |
| · 2.8d | `unique_so_far` | `SOFT_DUPLICATE_DECLARATION` | `DuplicateDeclaration: rank {value}` |
| 2.9a | `keys` `S/outranking`: required `mode`; optional `decided_by` | `SOFT_INVALID_OUTRANKING` | `InvalidInput: invalid outranking flag` |
| 2.9b | `enum` `S/outranking/mode`: `"strict"`, `"holistic"` | as 2.9a | as 2.9a |
| 2.10 | `excludes` `S/outranking` member `decided_by`, when `S/outranking/mode` is `"strict"` | `SOFT_STRICT_OUTRANKING_DECIDER` | `InvalidInput: strict outranking has no decider` |
| 2.11 | `type` `S/outranking/decided_by`: string | `SOFT_INVALID_DECIDER` | `InvalidInput: invalid decider for outranking` |
| 2.12 | `requires` `S/outranking` member `decided_by`, when `S/outranking/mode` is `"holistic"` | `SOFT_MISSING_DECIDER` | `MissingExceptionDecider: outranking` |
| 2.13 | `name` `S/outranking/decided_by`: `decider` | `SOFT_INVALID_DECIDER` | `InvalidInput: invalid decider for outranking` |
| 2.14 | `name` `S/exception_decider`: `decider` | `SOFT_INVALID_DECIDER` | `InvalidInput: invalid decider for exception` |
| 2.15 | `type` `S/outranks`: array | `SOFT_INVALID_ARRAY` | `InvalidInput: outranks must be an array` |
| | group `S/outranks/*` | | |
| · 2.16a | `type`: tuple of two strings | `SOFT_INVALID_OUTRANKS_PAIR` | `InvalidInput: invalid outranks pair` |
| · | group `@/*` | | |
| · · 2.16b | `unique_so_far` (the pair's two names differ) | as 2.16a | as 2.16a |
| · 2.16c | `unique_so_far` (the ordered pair is not repeated) | as 2.16a | as 2.16a |
| 2.17a | `type` `S/ties`: array | `SOFT_INVALID_ARRAY` | `InvalidInput: ties must be an array` |
| | group `S/ties/*`: 2.17b, 2.17c, 2.17d, as 2.16a to 2.16c | `SOFT_INVALID_TIES_PAIR` | `InvalidInput: invalid ties pair` |

Phase 3, `profiles`:

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 3.1 | `sorted_unique` `/environment/profiles` | `SOFT_UNSUPPORTED_PROFILE` | `UnsupportedProfile: profiles must be sorted and unique` |
| | group `/environment/profiles/*` | | |
| · 3.2 | hook `profile_registered` | as 3.1 | `UnsupportedProfile: Unsupported profile {value}` |
| 3.3a | `requires` `/environment/profiles` item `"relational-fol@0"` | as 3.1 | `UnsupportedProfile: Missing profile relational-fol@0` |
| 3.3b | `requires` … item `"soft-norms@0"` | as 3.1 | `UnsupportedProfile: soft-norms@0 is required` |
| 3.3c | `requires` … item `"norms@0"` | as 3.1 | `UnsupportedProfile: soft-norms@0 requires norms@0` |
| 3.4a–c | `excludes` … item `"closure@0"`, `"nary@0"`, `"order@0"` | as 3.1 | `UnsupportedProfile: the norms route admits FOL documents only` |
| 3.5a | hook `no_definitions` at `P` | as 3.1 | `UnsupportedProfile: norms route with definitions is not implemented` |
| 3.5b | hook `no_data_flags` at `P` | as 3.1 | `UnsupportedProfile: norms route with data flags is not implemented` |

Phase 4, `rule-fields`. One group over `/norms/*`; every row below is a sub-entry, so each rule is checked
completely before the next. `D` abbreviates the guard "`@/norm/mode` is `"default"`".

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 4.1a | `exact_keys` `@`: `norm` | `SOFT_INVALID_INPUT` | `InvalidInput: expected norm object` |
| 4.1b | `type` `@/norm`: object | as 4.1a | as 4.1a |
| 4.1c | `keys` `@/norm`: required `name`, `predicate`, `sign`, `guard`, `unless`, `over`; optional `mode`, `rank`, `alterable`, `exception`, `hard` | `SOFT_INVALID_INPUT` | `InvalidInput: invalid norm fields` |
| 4.2a | hook `w1_rule_fields` at `@/norm`, inherited | `SOFT_INVALID_INPUT` | `{message}` |
| | group `@/norm/over/*` | | |
| · 4.2b | `unique_so_far` | `SOFT_INVALID_INPUT` | `InvalidInput: duplicate over {value} in rule {name}` |
| 4.3 | `enum` `@/norm/mode`: `"strict"`, `"default"` | `SOFT_INVALID_RULE_FIELDS` | `InvalidInput: invalid mode for rule {name}` |
| 4.4 | `type` `@/norm/rank`: null or string | `SOFT_INVALID_RULE_FIELDS` | `InvalidInput: invalid soft fields for {name}` |
| 4.5a | `type` `@/norm/alterable`: array of strings | `SOFT_INVALID_ALTERABLE` | `InvalidInput: alterable of rule {name} must be sorted and distinct` |
| 4.5b | `sorted_unique` `@/norm/alterable` | as 4.5a | as 4.5a |
| 4.6 | `type` `@/norm/hard`: Boolean | `SOFT_INVALID_RULE_FIELDS` | `InvalidInput: hard of rule {name} must be Boolean` |
| 4.7a | `enum` `@/norm/mode`: `"strict"`, when `@/norm/hard` is `true` | `SOFT_HARD_CONSTRAINT` | `HardConstraintAltered: rule {name}` |
| 4.7b | `max_items` `@/norm/alterable`: 0, same guard | as 4.7a | as 4.7a |
| 4.8 | `type` `@/norm/exception`: null, when `@/norm/mode` is absent or is not `"default"` | `SOFT_STRICT_EXCEPTION` | `InvalidInput: rule {name} is strict and declares an exception` |
| 4.9a | `requires` `@/norm` member `exception`, when D | `SOFT_MISSING_EXCEPTION` | `InvalidInput: rule {name} needs an exception` |
| 4.9b | `keys` `@/norm/exception`: required `sufficient`, `necessary`, `factors`; optional `decided_by`; when D | as 4.9a | as 4.9a |
| 4.10 | `type` `@/norm/exception/decided_by`: null or string, when D | `SOFT_INVALID_DECIDER` | `InvalidInput: invalid decider for rule {name}` |
| 4.11a | `requires` `@/norm/exception` member `decided_by`, when D and `S/exception_decider` is absent | `SOFT_MISSING_DECIDER` | `MissingExceptionDecider: rule {name}` |
| 4.11b | `type` `@/norm/exception/decided_by`: string, same guard | as 4.11a | as 4.11a |
| 4.12 | `name` `@/norm/exception/decided_by`: `decider`, when D and that value is a string | `SOFT_INVALID_DECIDER` | `InvalidInput: invalid decider for rule {name}` |
| 4.13a | `type` `@/norm/exception/sufficient`: array, when D | `SOFT_EXCEPTION_ARRAY` | `InvalidInput: exception sufficient must be an array` |
| | group `@/norm/exception/sufficient/*`, when D | | |
| · 4.13b | hook `fol_formula`, inherited | `SOFT_INVALID_INPUT` | `{message}` |
| 4.13c | `type` `@/norm/exception/necessary`: array, when D | `SOFT_EXCEPTION_ARRAY` | `InvalidInput: exception necessary must be an array` |
| | group `@/norm/exception/necessary/*`, when D | | |
| · 4.13d | hook `fol_formula`, inherited | `SOFT_INVALID_INPUT` | `{message}` |
| 4.14a | `type` `@/norm/exception/factors`: array of strings, when D | `SOFT_INVALID_FACTORS` | `InvalidInput: invalid factors of rule {name}` |
| | group `@/norm/exception/factors/*`, when D | | |
| · 4.14b | `max_bytes`: `MAX_FACTOR_BYTES` | as 4.14a | as 4.14a |

Phase 5, `references`:

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| | group `P/*` | | |
| · 5.1 | `declared_in` `@/instruction_of`: `S/parties/*` | `SOFT_UNKNOWN_PARTY` | `UnknownSymbol: party {value}` |
| | group `S/outranks/*`, then inside it group `@/*` | | |
| · · 5.2a | `declared_in`: `S/ranks/*` | `SOFT_UNKNOWN_RANK` | `UnknownRank: {value}` |
| | group `S/ties/*`, then inside it group `@/*` | | |
| · · 5.2b | `declared_in`: `S/ranks/*` | as 5.2a | as 5.2a |
| | group `/norms/*/norm/name` | | |
| · 5.3 | `unique_so_far` | `SOFT_DUPLICATE_DECLARATION` | `DuplicateDeclaration: rule {value}` |
| | group `/norms/*` (rows 5.4 to 5.9b are its sub-entries) | | |
| · 5.4 | hook `regulated_predicate` at `@/norm/predicate` | `SOFT_INVALID_INPUT` | `UnknownSymbol: regulated predicate {value}` |
| · 5.5 | `declared_in` `@/norm/rank`: `S/ranks/*`, when `@/norm/rank` is a string | `SOFT_UNKNOWN_RANK` | `UnknownRank: rule {name}, {value}` |
| · | group `@/norm/alterable/*` | | |
| · · 5.6 | `declared_in`: `S/parties/*` | `SOFT_UNKNOWN_PARTY` | `UnknownSymbol: party {value}` |
| · 5.7-5.8 | classifier `rule_typing` at `@`, emits: | | |
| · · 5.7 | the rule's guard and carve-outs are typed, within the rule's budget; inherited | `SOFT_INVALID_INPUT` | `{message}` |
| · · 5.8a | each exception condition is typed, within the rule's budget; inherited | `SOFT_INVALID_INPUT` | `{message}` |
| · · 5.8b | no exception condition mentions a regulated, defined or `soft__` predicate | `SOFT_INVALID_EXCEPTION_CONDITION` | `InvalidInput: exception condition of rule {detail}` |
| · | group `@/norm/over/*` | | |
| · · 5.9a | `declared_in`: `/norms/*/norm/name` | `SOFT_INVALID_INPUT` | `UnknownRule: rule {value}` |
| · · 5.9b | hook `over_same_predicate`, returns `rule`, `predicate`, `parent_predicate` | `SOFT_INVALID_INPUT` | `PrecedenceAcrossPredicates: rule {rule} on {predicate}, rule {value} on {parent_predicate}` |

Phase 6, `semantic`:

| Id | Kind, target, guard | Code | Text |
|---|---|---|---|
| 6.1 | hook `outranks_acyclic` at `S/outranks`, returns `detail` | `SOFT_DEPENDENCY_CYCLE` | `DependencyCycle: {detail}` |
| | group `S/ties/*` | | |
| · 6.2 | hook `tie_not_comparable`; arguments `a`: `@/0`, `b`: `@/1` | `SOFT_TIE_AGAINST_ORDER` | `TieAgainstOrder: {a}, {b}` |
| 6.3 | hook `ties_distinct_unordered` at `S/ties` | `SOFT_DUPLICATE_DECLARATION` | `DuplicateDeclaration: tie` |
| 6.4a | hook `decision_names_fit`, returns `name` | `SOFT_RESOURCE_LIMIT` | `ResourceLimit: decision predicate {name}` |
| 6.4b | hook `extended_vocabulary_fits` | `SOFT_RESOURCE_LIMIT` | `ResourceLimit: extended vocabulary` |
| 6.5-6.15 | classifier `soft_semantic`, emits: | | |
| · 6.5a | W1's document node budget on `T` | `SOFT_RESOURCE_LIMIT` | `ResourceLimit: AST exceeds 10,000 nodes` |
| · 6.5b | author precedence is acyclic | `SOFT_DEPENDENCY_CYCLE` | `DependencyCycle: {detail}` |
| · 6.6 | precedence depth at most 16 | `SOFT_RESOURCE_LIMIT` | `ResourceLimit: precedence depth` |
| · 6.7 | the rules of `T` are stratified | `SOFT_DEPENDENCY_CYCLE` | `DependencyCycle: {detail}` |
| · 6.8 | no default rule over a strict rule | `SOFT_OVER_HARD` | `SoftOverHard: {detail}` |
| · 6.9 | derived carve-outs within the limits | `SOFT_RESOURCE_LIMIT` | `ResourceLimit: derived carve-out{detail}` |
| · 6.10a | `T′` is stratified | `SOFT_DEPENDENCY_CYCLE` | `DependencyCycle: {detail}` |
| · 6.10b | `T′` within W1's resource limits; inherited | `SOFT_RESOURCE_LIMIT` | `{message}` |
| · 6.11 | each generated soft premise within the limits | `SOFT_RESOURCE_LIMIT` | `ResourceLimit: generated soft premise` |
| · 6.12 | each generated norm layer within the limits | `SOFT_RESOURCE_LIMIT` | `ResourceLimit: generated norm layer {detail}` |
| · 6.13 | each conflict target within the limits | `SOFT_RESOURCE_LIMIT` | `ResourceLimit: generated conflict target {detail}` |
| · 6.14 | `background′` within one budget | `SOFT_RESOURCE_LIMIT` | `ResourceLimit: generated background` |
| · 6.15 | the layers and `⊤` within one budget | `SOFT_RESOURCE_LIMIT` | `ResourceLimit: generated norm layers` |

**The two classifiers.** Each calls frozen or existing code read-only and maps its failure to a member. The
mapping never reads a name out of a message: it compares a message with a fixed text, or takes what follows a
fixed leading text as `detail`. Names from the input occur only after that leading text, and every earlier check
has held, so input cannot steer the mapping.

- `rule_typing`, for one rule. Lean: `Phases.ruleReferences` on the rule with its exception removed; if that
  fails, member 5.7 with its message. Otherwise `Phases.ruleReferences` on the rule as it is; a failure with code
  `SOFT_INVALID_EXCEPTION_CONDITION` is member 5.8b, any other failure is member 5.8a. Python: the same with
  `_rule_references` and the rule's `conditions` emptied.

  **Order inside the set.** Both validators type the guard and the carve-outs first. They then take the
  exception's conditions one at a time, `sufficient` before `necessary`, and each condition is typed and then
  screened before the next one is read (`Phases.lean:305–313`, `softnorms.py:422–429`). So 5.8a and 5.8b
  alternate condition by condition: a 5.8b fault on an earlier condition comes before a 5.8a fault on a later
  one, and the index in `emits` alone would give the oracle the wrong answer for that pair. In the fault
  catalogue a fault for 5.8a or 5.8b therefore carries the order key of 2.6: (the condition's index, the
  member's index in `emits`), where the conditions of a rule are counted from 0 through `sufficient` and then
  `necessary`, and the members' indices are 1 for 5.8a and 2 for 5.8b. A fault for 5.7 keeps the default key,
  (0), which comes before every key of 5.8a and 5.8b.
- `soft_semantic`. Let `m` be the message with which the legacy validator rejects (`validateSoft`; in Python the
  construction of `SoftNormDocument`). The first rule that applies decides. The table is the Lean classifier,
  with Lean's texts. The Python classifier applies the same rules to the Python validator's exception, with
  three differences that follow from Python's texts:
  - where a rule tests for the leading `ResourceLimit: ` it tests for the exception class `ResourceLimit`;
  - in rules 1 and 2 it tests Python's W1 texts, which have no leading class (`AST exceeds 10,000 nodes`,
    `precedence depth`; `ve/ast.py:212`, `ve/norms.py:252`);
  - before rule 5 it has one more rule: `m` is exactly `ResourceLimit: derived carve-out`: member 6.10b. Python
    gives that text, which names no rule, to a `ResourceLimit` that `SoftenedNormDocument` raises, and that is
    W1's limits on `T′` (`softnorms.py:949–952`). Lean reports the same case from `validateW1 (soften D)`, by
    rule 12. Python's rule 5 is then reached only by a text that goes on to name a rule
    (`ResourceLimit: derived carve-out of rule <name>`), which is the text of 6.9 in both validators.

  That the two classifiers name the same member is tested (tiers 0 and A), not constructed.

| # | Condition | Member |
|---|---|---|
| 1 | W1's check of the base document (`checkW1 D.base`; Python `NormDocument` on the core rules) fails with `m`, and `m` is `ResourceLimit: AST exceeds 10,000 nodes` | 6.5a |
| 2 | the same, and `m` is `ResourceLimit: precedence depth` | 6.6 |
| 3 | the same, and `m` begins `DependencyCycle: `: 6.5b if the author precedence graph is cyclic, otherwise 6.7 | 6.5b, 6.7 |
| 3a | the same, with any other `m` | no member: the classifier returns `ok`, so the rejection shows as a residual (2.8) and is not attributed to `T′` by rules 11 to 13 |
| 4 | `m` begins `SoftOverHard: ` | 6.8 |
| 5 | `m` begins `ResourceLimit: derived carve-out` | 6.9 |
| 6 | `m` begins `ResourceLimit: generated soft premise` | 6.11 |
| 7 | `m` is `ResourceLimit: generated norm layers` | 6.15 |
| 8 | `m` begins `ResourceLimit: generated norm layer ` | 6.12 |
| 9 | `m` begins `ResourceLimit: generated conflict target ` | 6.13 |
| 10 | `m` is `ResourceLimit: generated background` | 6.14 |
| 11 | `m` begins `DependencyCycle: ` | 6.10a |
| 12 | `m` begins `ResourceLimit: ` | 6.10b |
| 13 | anything else | no member, as rule 3a: the classifier returns `ok` and the rejection shows as a residual (revision 3; until revision 2 the fallback member 6.10c, "`T′` passes W1's other checks", which no input was found to reach: W1 on `T′` fails only on its limits, rule 12, or its strata, rule 11) |

**Expected entries of the delta report**, from reading the two validators; none was run. Each is decided at plan
5.1 step 5, not here.

| Check | Python today | Lean today | The contract |
|---|---|---|---|
| 2.7a, 2.8c, a name that is not a string | Python's `str` of the value | compact JSON of the value, whole (`value.compress`, `Phases.lean:89`) | compact JSON of the value, cut at 80 bytes with `...` added (2.7: `raw` renders a value that is not a string as `json`). Python's text changes; Lean's changes where the compact JSON is longer than 80 bytes |
| 4.1c | `InvalidInput: invalid norm fields [<sorted keys>]` | `InvalidInput: invalid norm fields` | Lean's text |
| 6.5a, 6.6 | `AST exceeds 10,000 nodes`, `precedence depth`: W1's Python texts carry the class in the exception, not in the message | `ResourceLimit: AST exceeds 10,000 nodes`, `ResourceLimit: precedence depth` | Lean's texts |
| 6.10b, W1's limits on `T′` | `ResourceLimit: derived carve-out`, which names no rule: `softnorms.py:949–952` rewords the `ResourceLimit` that `SoftenedNormDocument` raises, and W1's own text is lost | W1's own text, from `validateW1 (soften D)` | inherited: each language's text, as in the last row. This is not an entry for 6.9, whose text names the rule in both validators (`ResourceLimit: derived carve-out of rule <name>`) and does not change |
| 6.11 | `ResourceLimit: generated soft premise <label>` | `ResourceLimit: generated soft premise` | Lean's text; Python's label is lost |
| 2.3, 4.2a, 4.13b, 4.13d, 5.7, 5.8a, 6.10b | the inherited decoder's own text | the inherited decoder's own text | each language's text; these stay language-specific until plan S4 and S5 |

**Planned tiers, for the gate of section 9.** A numbered check of soft-norms.md 8 counts by its weakest
sub-entry, in the order T3, inherited hook, T2, T1.

| Tier | Numbered checks | Count |
|---|---|---|
| T1 only | 1.1–1.7; 2.1, 2.2, 2.4–2.17; 3.1, 3.3, 3.4; 4.1, 4.3–4.12, 4.14; 5.1–5.3, 5.5, 5.6 | 43 |
| T2, not inherited | 3.2, 3.5, 5.4, 5.9, 6.1–6.4 | 8 |
| inherited hook | 2.3, 4.2, 4.13 | 3 |
| T3 | 5.7, 5.8, 6.5–6.15 | 13 |

43 + 8 = 51 of 67 against a threshold of 45. This is a count on paper; the gate uses the count of the contract
as built.

## 7. Generated artefacts and gates

### 7.1 Generated Lean

A generated module is exactly:

```lean
/- GENERATED by tools/wire_contract.py from ve/wire_contract/soft-norms@0.json, revision 1,
   sha256 <64 hex digits>; limits <64 hex digits>; names <64 hex digits>. Do not edit. -/
import VE.Contract.Table

namespace VE.Contract.Tables.SoftNorms
def table : VE.Contract.Table :=
  <term>
end VE.Contract.Tables.SoftNorms
```

`<term>` is built only from the constructors of the types of 5.1 (written as anonymous constructors or by name),
list brackets, string literals, numerals, `true`, `false`, `none` and `some`. There is no `theorem`, `instance`,
`macro`, `open`, `#eval` or `#guard`, and no JSON value: `Table.lean` does not mention `Lean.Json`. The header
comment is in the plain layout that `tools/check_lean_imports.py` requires. `Tables/Corpus.lean` holds the three
tables of 8.1 in one namespace each, in the same grammar. `Limits.lean` and `Names.lean` are lists of `def NAME :
Nat := n` and of `NameClass` values, in the same grammar.

### 7.2 Inventory, layers, manifest

- Every new `lean/VE/Contract/**/*.lean` module is added to `VE/Route/frozen-sources.sha256`. `--write` rewrites
  the lines of generated modules; no other tool line changes.
- `tools/layer_policy.py`: the Lean modules fall in layer 2 by the existing rule and `DiagnoseMain` in layer 4;
  `ve.wire_contract` is added to Python layer 1 and `ve.softnorms_contract` to layer 2. `engine.py` imports
  `ve.wire`, `ve.errors` and `ve.limits` only. The pilot's Python hooks, classifiers and adapter live in the new
  profile-layer module `ve/softnorms_contract.py`, which imports `ve.softnorms` read-only and registers them with
  `engine.register`. `ve/softnorms.py` is not edited in S0 to S3.
- Assurance manifest: `Engine.lean`, `Diagnose.lean` and `Hooks/*.lean` read JSON and are classified under
  `other_json` as "diagnostic only: no verdict depends on it"; `DiagnoseMain.lean` is runner glue. Table modules
  handle no JSON and need no entry. The pinned decoder total stays 16,985 lines. One operation is added,
  `wire.diagnose` (4.2).

### 7.3 The import rule

`tools/check_lean_imports.py` gains one rule: a module `VE.Contract.*` may be imported only by a module
`VE.Contract.*`, by `DiagnoseMain`, and by `VE.Audit`. `VE.Audit` imports `VE.Contract.Engine` only, and only if
the theorems of 5.3 are added; `lean/VE.lean` imports `VE.Audit` and nothing imports `VE`, so no executable on a
verdict path links the engine. This rule is what makes "diagnostic only" checkable. The Python side has a
matching test, by a scan of the syntax trees: in S0 to S3 the only modules of `ve/` that import
`ve.wire_contract` are `ve/wire_contract/` itself and `ve/softnorms_contract.py`, nothing in `ve/` imports
`ve.softnorms_contract`, and `engine.run` and `engine.overlay` are called only from `tests/`, `conformance/` and
`tools/`. The one production call site, at the boundary where a rejection is returned, is added by the switch
commit and by nothing earlier.

### 7.4 The gates, as the plan fixes them

The four conservativity gates of plan 5.2 apply to every commit of S0 to S3, as amended by the debate:

- **C1.** No diff in a decoder, canonical serialiser, identity serialisation or digest function.
  `VEError.to_dict()` may gain `diagnostic`; nothing else in it changes.
- **C2.** Legacy verdicts equal their snapshot. Where an implementation supports the unit and completes
  diagnosis, its engine reports `clean` on every accepted input and a fault on every rejected one. Deferred
  outcomes are counted, not compared.
- **C3.** Public diagnostics change only as the delta report lists. In S0 to S3 the pilot stays in `shadow`, so
  the list of public changes is empty.
- **C4.** `lake build`, `lean/audit.py`, `frozen.py` and the manifest test pass. The inventory diff is additions
  and generated rehashes, plus, only if the theorems are added, the reviewed added-lines-only diff of
  `VE/Audit.lean` and its rehash.

`tools/mutation_check.py` gains one injected fault: two rows of a generated table are swapped, and `--check`
must fail.

## 8. Acceptance fixtures for item 1

Deterministic, with expectations written by hand from sections 2 and 6. Each reviewer derives the expectation of
every fixture from those sections before reading the column "Expected". A fixture is green when the Python
engine and `ve_diagnose` both return the expected outcome, as records compared by 2.7.

### 8.1 The engine corpus (`conformance/wire-contract/engine.json`)

Three synthetic contracts in `conformance/wire-contract/contracts/`, with their own `limits` and `names`:
`DEMO_MAX_ITEMS` 3, `DEMO_MAX_TAGS` 4, and the class `word` (`first` `a-z`; `rest` `a-z0-9_`; `max_bytes` 8;
`forbid_infix` `__`).

`inner@0`, revision 1, input `["x", "ys"]`, code `INNER_BAD` (`InvalidInput`, also its residual code), one
phase `body`:

| Id | Entry | Text |
|---|---|---|
| b1 | `type` `/x`: integer | `Inner: x is {value:json}` |
| | group `/ys/*` | |
| · b2 | `type`: string | `Inner: y {index}` |

`demo@0`, revision 1, input `["doc"]`, residual code `DEMO_INVALID_INPUT`. Codes and classes: `DEMO_SHAPE`,
`DEMO_NAME`, `DEMO_SEMANTIC`, `DEMO_INVALID_INPUT` are `InvalidInput`; `DEMO_DUPLICATE` is
`DuplicateDeclaration`; `DEMO_UNKNOWN` is `UnknownSymbol`; `DEMO_LIMIT` is `ResourceLimit`.

| Phase | Id | Entry | Code | Text |
|---|---|---|---|---|
| `shape` | 1.1 | `keys` `/doc`: required `items`, `mode`, `refs`; optional `note`, `owner`, `part`, `seed`, `table` | `DEMO_SHAPE` | `Shape: document` |
| | 1.2 | `type` `/doc/items`: array | `DEMO_SHAPE` | `Shape: items` |
| | 1.3 | `max_items` `/doc/items`: `DEMO_MAX_ITEMS` | `DEMO_LIMIT` | `Limit: {count} items, at most {limit}` |
| | 1.4 | `enum` `/doc/mode`: `"open"`, `"closed"` | `DEMO_SHAPE` | `Shape: mode {value:json}` |
| | 1.5 | `type` `/doc/refs`: array of strings | `DEMO_SHAPE` | `Shape: refs` |
| | 1.6 | `excludes` `/doc` member `note`, when `/doc/mode` is `"closed"` | `DEMO_SHAPE` | `Shape: a closed document has a note` |
| | 1.7 | `requires` `/doc` member `owner`, when `/doc/mode` is `"open"` | `DEMO_SHAPE` | `Shape: an open document has no owner` |
| | 1.8 | `const` `/doc/owner`: `"root"` | `DEMO_SHAPE` | `Shape: owner {value}` |
| | 1.9 | `excludes` `/doc/refs` item `"self"` | `DEMO_SHAPE` | `Shape: refs names self` |
| | 1.10 | `requires` `/doc/refs` item `"a"`, when `/doc/note` is a string | `DEMO_SHAPE` | `Shape: a note needs the ref a` |
| `items` | | group `/doc/items/*` | | |
| | · 2.1a | `exact_keys` `@`: `name`, `tags` | `DEMO_SHAPE` | `Shape: item {index}` |
| | · 2.1b | `name` `@/name`: `word` | `DEMO_NAME` | `Name: {value}` |
| | · 2.1c | `unique_so_far` `@/name` | `DEMO_DUPLICATE` | `Duplicate: {value}` |
| | · 2.1d | `type` `@/tags`: array of strings; argument `name`: `@/name` | `DEMO_SHAPE` | `Shape: tags of {name}` |
| | | group `/doc/items/*` | | |
| | · 2.2a | `sorted_unique` `@/tags`; argument `name`: `@/name` | `DEMO_SHAPE` | `Shape: tags of {name} are not sorted` |
| | · | group `@/tags/*` | | |
| | · · 2.2b | `max_bytes`: 2; argument `name`: `@1/name` | `DEMO_LIMIT` | `Limit: tag {value} of {name}` |
| | | group `/doc/table/*` | | |
| | · 2.3a | `name` on key: `word` | `DEMO_NAME` | `Name: {key}` |
| | · 2.3b | `type`: integer | `DEMO_SHAPE` | `Shape: table entry {key} is {value:json}` |
| `references` | | group `/doc/refs/*` | | |
| | · 3.1 | `declared_in`: `/doc/items/*/name` | `DEMO_UNKNOWN` | `Unknown: {value}` |
| | 3.2 | `max_count` of `/doc/items/*/tags/*`: `DEMO_MAX_TAGS` | `DEMO_LIMIT` | `Limit: {count} tags` |
| | 3.3 | include `inner@0`, phase `body`, at `/doc/part` | | |
| | 3.4 | include `inner@0`, phase `body`, at `/doc`, view `part_view`, with the `says` below, as `DEMO_SEMANTIC` | | |
| `semantic` | 4.1 | hook `no_bad_name`, returns `names` | `DEMO_SEMANTIC` | `Semantic: {names:list}` |
| | 4.3 | classifier `demo_rules`, emits 4.3a (returns `n`) and 4.3b | `DEMO_SEMANTIC` | `Semantic: first {n:count}`; `Semantic: second` |

`defer@0`, revision 1, input `["v", "w", "note"]`, codes `DEFER_SHAPE` and the residual code
`DEFER_INVALID_INPUT` (both `InvalidInput`), two phases, every check with code `DEFER_SHAPE`:

| Phase | Id | Entry | Text |
|---|---|---|---|
| `first` | d1 | `type` `/v`: integer | `Defer: v` |
| `second` | d2 | hook `lean_only` | `Defer: lean only` |
| | d3 | `type` `/w`: integer | `Defer: w` |

The `says` sentences of the corpus contracts, so that the fixture files are determined. Each string is exactly as
shown, backticks included. In the sentence of 3.4, `W` is the letter as written; it stands for the include's
target, as in 3.1, which here is `/doc`.

```json
{"3.4":  "The view gives an object whose only member `x` is the `seed` of W, or 0 when W is not an object with a `seed`.",
 "4.1":  "No value at `/doc/items/*/name` is the string `bad`.",
 "4.3a": "`/doc/refs` does not have exactly 3 elements.",
 "4.3b": "`/doc/refs` does not have exactly 2 elements.",
 "d2":   "`/note` is not the string `lean`."}
```

3.4, 4.1, 4.3a and 4.3b are in `demo@0` and d2 is in `defer@0`. `inner@0` has no hook, classifier or view, and
so no `says`.

The corpus hooks, implemented in `Hooks/Corpus.lean` and in the Python test harness:

| Name | Behaviour |
|---|---|
| `no_bad_name` | let `N` be the values matched by `/doc/items/*/name`; fail with `names` = `N` if `"bad"` is among them; otherwise `ok` |
| `demo_rules` | let `k` be the number of elements of `/doc/refs`; `k` = 3: fail member 4.3a with `n` = 3; `k` = 2: fail member 4.3b; `k` = 4: fail member `4.3z`, which is not declared; otherwise `ok` |
| `part_view` (view) | for an object `d` with a member `seed`: `{"x": seed}`; for any other value: `{"x": 0}` |
| `lean_only` | registered in Lean only: fail if `/note` is `"lean"`; otherwise `ok` |

The base input **B** for `demo@0`:

```json
{"doc": {"items": [{"name": "a", "tags": ["x", "y"]}, {"name": "b", "tags": []}],
         "mode": "open", "owner": "root", "refs": ["a"], "table": {"k": 1},
         "part": {"x": 1, "ys": ["u"]}, "seed": 7}}
```

Each case is B with the change shown; a member named without its owner is a member of `doc`, and "item 0" is
`doc.items[0]`. "Expected" gives `check`, `path` and `text`; the code and class follow from the table, and `args`
from the template.

| Case | Change to B | Expected |
|---|---|---|
| E1 | none | clean |
| E2 | every object's members written in reverse order | clean |
| E3 | `mode` is `"shut"`, and item 0's `name` is `"A!"` | 1.4, `/doc/mode`, `Shape: mode "shut"` (table order beats document order) |
| E4 | `refs` removed | 1.1, `/doc`, `Shape: document` |
| E5 | `doc` gains a member `zzz` with the value `1` | 1.1, `/doc`, `Shape: document` |
| E6 | `doc` is `[]`; and, separately, the case has no `doc` | 1.1, `/doc`, `Shape: document` in both |
| E7 | `items` is `{}` | 1.2, `/doc/items`, `Shape: items` |
| E8 | four valid items `a`, `b`, `c`, `d` | 1.3, `/doc/items`, `Limit: 4 items, at most 3` |
| E9 | `refs` is `["a", 3]` | 1.5, `/doc/refs`, `Shape: refs` |
| E10 | `mode` is `"closed"` and `note` is `"n"` | 1.6, `/doc`, `Shape: a closed document has a note` |
| E11 | `owner` removed | 1.7, `/doc`, `Shape: an open document has no owner` |
| E12 | `owner` is `"admin"` | 1.8, `/doc/owner`, `Shape: owner admin` |
| E13 | `mode` is `"closed"` and `owner` removed | clean (1.7 is guarded out; 1.8 holds on an absent target) |
| E14 | `refs` is `["a", "self"]` | 1.9, `/doc/refs`, `Shape: refs names self` |
| E15 | `note` is `"n"` and `refs` is `["b"]` | 1.10, `/doc/refs`, `Shape: a note needs the ref a` |
| E16 | item 0's `tags` is `[1]`, and item 1's `name` is `"B"` | 2.1d, `/doc/items/0/tags`, `Shape: tags of a` (item-major: item 0 is checked completely first) |
| E17 | item 0's `tags` is `["y", "x"]`, and item 1's `name` is `"a"` | 2.1c, `/doc/items/1/name`, `Duplicate: a` (check-major: the first group covers every item before the second starts) |
| E18 | item 0's `name` is `"A"`, and item 1's `name` is `"B"` | 2.1b, `/doc/items/0/name`, `Name: A` |
| E19 | item 0's `name` is `7`; separately `"a__b"`; separately `"abcdefghi"` | 2.1b, `/doc/items/0/name`, and `Name: 7`, `Name: a__b`, `Name: abcdefghi` |
| E20 | item 1's `tags` is `["long", "ok"]` | 2.2b, `/doc/items/1/tags/0`, `Limit: tag long of b` |
| E21 | `table` is `{"😀": 1, "ｚ": 1}` (U+1F600 and U+FF5A) | 2.3a, `/doc/table/ｚ`, `Name: ｚ` (U+FF5A sorts first by code point; UTF-16 order would put U+1F600 first) |
| E22 | `table` is `{"k": "s"}` | 2.3b, `/doc/table/k`, `Shape: table entry k is "s"` |
| E23 | `table` is `{"k": s}` with `s` a string of 100 letters `a` | 2.3b, `/doc/table/k`, `Shape: table entry k is ` followed by `"`, 79 letters `a` and `...` |
| E24 | `refs` is `["a", "c"]` | 3.1, `/doc/refs/1`, `Unknown: c` |
| E25 | item 0's `tags` is `["a", "b", "c"]` and item 1's is `["d", "e"]` | 3.2, `""`, `Limit: 5 tags` |
| E26 | `part` is `{"x": 1, "ys": ["u", 2]}` | `3.3/b2`, `/doc/part/ys/1`, `Inner: y 1`, code `INNER_BAD` |
| E27 | `seed` is `"s"` | `3.4/b1`, `/doc`, `Inner: x is "s"`, code `DEMO_SEMANTIC`, and `args` has `inner_path` `/x` |
| E28 | items are `z` and `bad`, both with `tags` `[]`; `refs` is `["z"]` | 4.1, `""`, `Semantic: bad, z` |
| E29 | `refs` is `["a", "a", "b"]`; separately `["a", "b"]` | 4.3a, `""`, `Semantic: first 3`; 4.3b, `""`, `Semantic: second` |
| E30 | `refs` is `["a", "a", "b", "b"]` | clean (the classifier names an undeclared member) |
| E31 | `items` is `[]`, `refs` is `[]`, `table` is `{}` | clean |
| E32 | `table`, `part` and `seed` removed | clean |

Cases for `defer@0`, and for the overlay with a legacy text `m`:

| Case | Root | Python engine | Lean engine |
|---|---|---|---|
| E33 | `{"v": "x", "w": "x"}` | fault d1, `/v`, `Defer: v` | the same |
| E34 | `{"v": 1, "w": "x"}` | deferred d2 | fault d3, `/w`, `Defer: w` |
| E35 | `{"v": 1, "w": 2, "note": "lean"}` | deferred d2 | fault d2, `""`, `Defer: lean only` |
| E36 | `{"v": 1, "w": 2}` | deferred d2 | clean |

| Case | Legacy | Engine outcome | Overlay reports |
|---|---|---|---|
| E37 | accepts | clean | nothing |
| E38 | rejects with `m` | E22's fault | E22's record |
| E39 | rejects with `m` | clean on `demo@0` | the residual record of 4.1 with `text` `m` |
| E40 | rejects with `m` | E34 in Python, Lean answers | Lean's record for d3 |
| E41 | rejects with `m` | E36 in Python, Lean answers `clean` | the residual record for `defer@0` |
| E42 | rejects with `m` | E36 in Python, Lean not available | the deferred record of 4.1 |

**Coverage rule.** Beyond these cases the corpus has at least one failing and one holding case for every T1
kind, every literal form, every type form and every renderer, and a case with an absent target for every kind of
the first table of 2.4. The lemma-free evidence for claim (A) is this corpus; it is profile-independent.

### 8.2 Tooling fixtures

| Case | Input | Expected |
|---|---|---|
| L1 | `demo@0` with check 2.1c renamed 2.1a | `WC02` |
| L2 | `demo@0` with rows 1.3 and 1.4 exchanged, ids unchanged | `WC02` |
| L3 | a check whose code is `DEMO_OTHER`, not declared | `WC03` |
| L4 | text `Name: {nome}` on 2.1b | `WC04` |
| L5 | `max_items` with limit `DEMO_NONE` | `WC05` |
| L6 | 2.2b's argument written `@2/name` | `WC06` |
| L7 | a text containing the word `partial`; and one containing `sorry` | `WC07` for both (the second is on the audit's list and was not on the plan's) |
| L8 | hook 4.1 without `says`; and, separately, include 3.4 without `says` | `WC08` for both |
| L9 | include 3.4 moved into `inner@0`'s phase `body` | `WC09` |
| L10 | a changed text with the lock and revision unchanged | `WC10` |
| L11 | a hand edit of `Tables/Corpus.lean`; the mutation of 7.4 | `WC11` |
| L12 | a clean tree | `--check` exits 0 and prints nothing |
| L13 | `--write` after raising a revision | exactly the generated files, the lock and the generated modules' inventory lines change |
| L14 | a module `VE.SoftNorms.Run` importing `VE.Contract.Engine` | `tools/check_lean_imports.py` fails (7.3) |
| L15 | `demo@0` with check 1.8's `const` given the value `null` | `WC01`: `ve.wire.loads_json` refuses the file (2.2) |

### 8.3 The pilot (`soft-norms@0`)

The base is `conformance.soft_norms.multi_fault_base()` (`conformance/soft_norms.py:730`): the soft block
`{"parties": ["p", "q"], "ranks": ["a", "b", "c"], "outranks": [["a", "b"]], "ties": [["b", "c"]], "outranking":
{"mode": "strict"}, "exception_decider": "assistant"}`, the predicates `q` (with `instruction_of` `p`) and `u`,
and four rules: `a0` (default, rank `a`, on `x_required`), `b1` (strict, alterable `p` and `q`, on
`x_permitted`), `c2` (default, rank `b`, over `a0`, an exception without `decided_by`), `d3` (default, on
`x_permitted`). It is one of the contract's two examples; the other is `env()` with no rules. The fault names are
those of `multi_faults()` in the same file.

| Case | Change to the base | Expected `check`, `path`, `text` |
|---|---|---|
| P1 | none; and the second example | clean; both legacy validators accept |
| P2 | `party-name`: parties `["p", "Q!"]` | 2.7a, `/environment/vocabulary/soft/parties/1`, `InvalidInput: invalid soft name Q!` |
| P3 | `party-repeat`: parties `["p", "q", "p"]` | 2.7b, `…/soft/parties/2`, `DuplicateDeclaration: party p` |
| P4 | `language`: `"x"` | 1.2, `/environment/language`, `UnsupportedProfile: Unsupported language` |
| P5 | `parties-shape` (parties `"p"`) with `r3-rank-type` (rule 3's rank `7`) | 2.5, `…/soft/parties`, `InvalidInput: parties must be an array` (phase 2 before phase 4) |
| P6 | `r0-hard-type` (rule 0's `hard` `"yes"`) with `r1-mode` (rule 1's `mode` `"x"`) | 4.6, `/norms/0/norm/hard`, `InvalidInput: hard of rule a0 must be Boolean` (rule 0 before rule 1) |
| P7 | on `env()`: rule `a` default with a factor of 201 bytes, then rule `b` with rank `z` | 4.14b, `/norms/0/norm/exception/factors/0`, `InvalidInput: invalid factors of rule a` (every rule's fields before any cross reference) |
| P8 | `outranks-pair`: `[["a", "b"], ["a", "a"]]` | 2.16b, `…/soft/outranks/1/1`, `InvalidInput: invalid outranks pair` |
| P9 | `ties-pair`: `[["b", "c"], ["b", "c"]]` | 2.17d, `…/soft/ties/1`, `InvalidInput: invalid ties pair` |
| P10 | `holistic-decider`: outranking `{"mode": "holistic"}` | 2.12, `…/soft/outranking`, `MissingExceptionDecider: outranking` |
| P11 | `inherited-decider`: `exception_decider` removed | 4.11a, `/norms/2/norm/exception`, `MissingExceptionDecider: rule c2` |
| P12 | `r1-strict-exception`: rule 1's `exception` `{}` | 4.8, `/norms/1/norm/exception`, `InvalidInput: rule b1 is strict and declares an exception` |
| P13 | `duplicate-rule`: rule 3 named `b1` | 5.3, `/norms/3/norm/name`, `DuplicateDeclaration: rule b1` |
| P14 | `rank-cycle`: outranks `[["a", "b"], ["b", "a"]]` | 6.1, `…/soft/outranks`, `DependencyCycle: a, b` |
| P15 | `soft-over-hard`: rule 3 over `b1` | 6.8, `""`, `SoftOverHard: rule d3 over b1` |
| P16 | `precedence-cycle` (rule 0 over `c2`) with `soft-over-hard` | 6.5b, `""`, `DependencyCycle: a0, c2` (the order inside the classifier set; test-enforced) |
| P17 | `malformed-predicate`: predicate `w` is `false` | 2.3, `/environment`, code `SOFT_INVALID_INPUT`; the text is each language's inherited text and is not compared |

For every case P2 to P17, the record's `code` equals the code the legacy validator reports today in Python
(`VEError.code`) and in Lean (the row's `code`). For a named fault that is the code column of `multi_faults()`;
for a combination it is the code of the fault with the least table position.

**The generic generator** (`conformance/wire_contract.py`, plan 6.2) replaces the generator of
`conformance/soft_norms.py:725–915` and keeps its design. Its acceptance, on `soft-norms@0`:

| Tier | Assertion |
|---|---|
| 0 | every fault of the catalogue, alone, gives its own check as the first diagnostic in Python and in Lean, and both legacy validators reject. The catalogue has every fault of `multi_faults()` and, for each T1 check, the mutations derived from its kind. A fault for a classifier member records its order key (2.6) wherever section 6 states one for its set; otherwise the key is the member's index in `emits` |
| A | all pairs within a phase, a seeded sample of cross-phase pairs and of triples, pairs of one check on two items, all pairs inside each classifier set; only faults with disjoint footprints are combined. Expected: the fault of least position, which inside a classifier set is decided by the order keys (2.6). Python = Lean = expected, on the whole record, except `text` and `args` of inherited records |
| B | seeded stacks of two to five mutations with key order shuffled. The two engines agree, and in each language the engine reports a fault exactly when the legacy validator rejects |
| C | on every case of A and B: gates C1 and C2 |
| coverage | every check is the first diagnostic at least once; every check after the table's first instance is masked by an earlier one at least once (the first instance has no earlier check); every adjacent phase pair occurs; the residual count and the deferred share are reported |

Each T2 hook is also compared between Python and Lean on every Tier 0 to B input at which it is reached. The
existing corpora (the soft conformance fixtures, the stage-0 baseline's rejection cells, the use-case documents)
are replayed in shadow: `clean` on accepted inputs, a fault on rejected ones.

**Allowed coverage gaps.** A check may lack its first-fault or masking witness in one language only for a reason
in this table, stated verbatim as the check's entry of the report's `coverage_unmet_reasons`. Whether a row
applies to a check is judged from the fault catalogue (`conformance/wire_contract_faults.py`), never from the
report; any other entry, and any gap no row covers, fails the coverage row of 9.

| Gap | Language | Applies to | Reason |
|---|---|---|---|
| G1 | Lean | a check every catalogue fault of which only the in-process API can carry (`readers` `python`) | Reached only by an explicit null, which the wire readers refuse before diagnosis: Lean has no witness; Python has its first-fault and masking witnesses. |

### 8.4 Conservativity

- **Z1.** The full existing suite, the conformance reports, `conformance/identity.json`, the frozen baseline and
  every frozen hash are unchanged by each commit of S0 to S3.
- **Z2.** `VEError("x").to_dict()` is `{"code": "InvalidInput", "message": "x"}`, as today; it has a member
  `diagnostic` only after `diagnostic` was set.
- **Z3.** With `soft-norms@0` in `shadow`, every row of `ve_soft_norms_route` and every Python soft exception is
  byte-identical to the pre-step snapshot on the corpora of 8.3.
- **Z4.** `frozen.py` passes; the inventory diff is the additions of 7.2 (and the `VE/Audit.lean` line only if
  the theorems are added).

## 9. The continuation gate: its metrics, exactly

After S3 the DRI reviews one report, `conformance/wire-contract/soft-norms@0-gate.json`, with these numbers:

| Metric | Definition | Required |
|---|---|---|
| residual count | cases of tiers 0, A, B and the replayed corpora in which a legacy validator rejects and that language's engine reports `clean`; per language | 0 |
| Tier 0, Tier A | as 8.3, in Python and in Lean; the expected record is the fault catalogue's on every field, `text` rendered from the contract's template with the catalogue's `args`, and an inherited record's `text` is its language's legacy text | green |
| `n1` | numbered checks of soft-norms.md 8 whose every sub-entry is T1 | reported |
| `n2` | numbered checks whose weakest sub-entry is a T2 hook that is not inherited | reported |
| feasibility | `n1 + n2`, out of 67 | at least 45 |
| deferred share | per language | reported |
| S3-pre | the inherited `norm-defaults@0` difference (`softnorms.py:97` against `Phases.lean:36`) was run with an input that reaches it, the result is recorded in `conformance/wire-contract/s3-pre.md`, and a reachable verdict difference is fixed outside this work | closed |

A numbered check with a member in a classifier set is T3. A numbered check with an inherited hook, or with an
include under a view, is "expressed with a coarse `view` hook" and counts in neither `n1` nor `n2`. The threshold
measures whether the format can express the table; the agreement of T2 hooks remains evidence from tests. If the
gate fails, S2's generic generator is kept over the hand-mirrored tables and the migration stops. S4 onward
needs a separate decision either way.

## 10. Limits, and what is not claimed

1. **No verdict and no identity.** Nothing on a verdict or identity path reads a contract, a table or the
   engine, for existing and for new profiles.
2. **No refinement theorem.** No statement relates a contract to its legacy decoder. "The engine reports a fault
   exactly when the decoder rejects" is tested (8.3), at zero tolerance, on generated and replayed corpora.
3. **The theorems are about the Lean engine.** Python agrees with it on the corpus; that is evidence, not proof.
4. **Hooks are trusted to the extent they are tested.** A T2 hook's truth value, a classifier's member and a
   view's result are hand-written per language.
5. **Inherited texts differ between languages** until the base contracts exist. The record's code, check and
   path agree; its text does not.
6. **One diagnostic.** The engine reports the first failing instance and does not continue.
7. **Entry points outside the pilot.** `decode_rule` on a single norm unit (soft-norms.md 8: 4.1 to 4.14, then
   5.4 to 5.8), the validation of a generated `E′` (`generated=True`, which skips 2.1), and diagnostics raised
   after the table (certificates, witnesses, graphs) keep today's diagnostics.
8. **Rust** has no engine before S4 and does not validate the soft block; the pilot has no Rust column.
9. **Raw JSON faults** (a duplicate key, a depth limit) are reported by the restricted readers before any
   contract runs; their order is open (plan question 7).
10. **Cost.** A rejection costs one engine run in Python and, only when Python defers, one `ve_diagnose` call.
    The pilot's Python hooks are complete, so its expected deferred share in Python is zero.

## 11. Statement review checklist (Astra + Fable, before S0 to S3)

1. **Totality (2.4).** Is every T1 kind defined on every value, and is "an absent target holds" the right
   default? Name a soft-norms check that it gets wrong.
2. **Order (2.6).** Does the expansion give soft-norms.md 8's order in each phase, in particular 4.x item-major,
   5.1 to 5.3 whole-source and 5.4 to 5.9 item-major? Derive E16, E17, P5, P6 and P7 independently.
3. **The pilot table (6).** For each row, do the kind, guard and text reproduce `Phases.lean` and
   `ve/softnorms.py`? Rows worth attacking: 2.2, 2.16, 4.7, 4.8, 4.9, 4.11, 5.5.
4. **The classifiers (6).** Is the decision list for `soft_semantic` exact for both validators, and can any
   input reach a message that it maps to the wrong member? Is `rule_typing`'s two-call scheme exact?
5. **The statements (5.3).** Are `run_fault_first` and `run_congr_reached` the right objects, strong enough and
   not vacuous? Is `run_congr_reached`'s hypothesis satisfiable by two real hook sets?
6. **Records (2.7).** Are `path` under includes, `args`, and the renderers determined for every input, including
   non-string values and long values?
7. **Outcomes (2.8).** Do the overlay's rows cover every combination, and can a deferred outcome ever be
   reported as a residual or the reverse?
8. **Wordings (3).** Does each generated sentence have one reading? Is any rejected wording of 3.2 still in a
   generated form?
9. **Conservativity (7.3, 7.4, 8.4).** Can anything in S0 to S3 change a verdict, an identity or a public byte?
   Is the import rule sufficient?
10. **The gate (9).** Is the classification rule for a numbered check fair, and is the paper count of section 6
    right?

## 12. Choices this draft resolves, and open points

Where the plan gave a schema or left a detail, this draft fixes it. Each is for the statement review to accept
or change; the plan is synchronised afterwards.

| # | Choice | Relative to the plan |
|---|---|---|
| R1 | `run` is defined as the first failing instance, so `run_clean_iff` and `run_fault_first` are immediate; `eval` replaces `holds` and `diagnosticOf`; a list split replaces the index; `run_phase_major` and `run_congr_reached` are added | plan 3.2 gave two schemata and estimated the lemmas as the main uncertainty of S1b; with this definition they are small |
| R2 | Guards are conjunctions of six literal forms; type forms are not recursive; contract literals are scalars: a Boolean, an integer or a string, and never `null` (R16) | plan 2.3 named `when` and `type` without a grammar |
| R3 | An absent target holds, for every T1 kind with a target | not stated in the plan |
| R4 | The kind list is the plan's. `requires` and `excludes` take `member` or `item`; `name` takes `"on": "key"`; a limit may be a numeral | plan 2.3 |
| R5 | Includes are resolved to scopes before any engine runs; views are total and applied at expansion; a viewed include may not sit inside an included phase | plan 2.3 and question 8; the pilot uses no include, because no base contract exists before S4 |
| R6 | `inherited` hooks and members; comparisons exclude their `text` and `args` | plan 5.3's remark that an inherited check is a coarse hook with language-specific text |
| R7 | Classifier members take their detail from the validator's message after a fixed leading text | plan 2.3 said the mapping is hand-written |
| R8 | `ve_diagnose` rows are `status: ok` with a member `outcome` | plan 2.5 wrote `status: "fault" \| "clean"`, which `ve.backends.lean.run`'s row schema would refuse |
| R9 | The import rule also admits `VE.Audit`; `lean/VE.lean` needs no edit | plan 3.1 item 4 named `VE/Contract/*` and `DiagnoseMain.lean` only |
| R10 | `status: shadow \| public` in the contract; S3 ends in shadow with the delta report, and the switch is a separate commit decided with the gate | plan 5.1 steps 4 to 6 |
| R11 | Checks 5.7 and 5.8 are a per-rule classifier set, so T3 has 13 numbered checks, not 11 | plan 5.3 row 1 named 6.5 to 6.15 only |
| R12 | The corpus contracts have generated Lean tables in `Tables/Corpus.lean`; Lean never decodes a contract from JSON | plan 6.1 |
| R13 | Constants such as the specification revision (1.4) are literals in the contract; a new revision of the spec is a contract revision | not stated in the plan |
| R14 | Record `args` hold rendered strings, not JSON values | plan 2.4's example |
| R15 | The pilot's Python hooks live in a new module `ve/softnorms_contract.py`, and in S0 to S3 no production path calls the engine | plan 3 put Python hooks "in the profile modules"; a new module leaves `ve/softnorms.py` without a diff |
| R16 | Contract files, `limits.json` and `names.json` are read with `ve.wire.loads_json`, so a contract has no `null` literal; `null` is tested with the type form | not stated in the plan before its draft 3, which now says it in 2.1 |
| R17 | An include with a `view` carries a `says` sentence, which the generated wording uses and the lint requires | the plan's excerpt in 2.1 had a viewed include without one; plan draft 3 adds it there and in 2.3 |
| R18 | A fault for a classifier member is ordered inside its set by an order key that the fault catalogue records; the index in `emits` is the default. `rule_typing` states its keys | plan 2.2 and 6.2 give the position tuple and "the fault with the least position" only; the order inside a T3 set stays test-enforced, as plan 2.3 says |
| R19 | Claim (B) asks for views that are equal on every value, as `run_congr_reached` does | plan 2.4 (b) says "every predicate reached (a hook, a classifier or a view)"; the plan is not edited for this |

The statement review of draft 1 changed none of R1 to R15 and fixed R16 to R19 (section 13). As that review
asked, the plan's draft 3 is synchronised with R16 and R17 only.

Open, for the review or the build to settle:

1. **`raw` is uncut.** A long name is repeated whole in the text, as today. Cutting it would change today's
   texts. This holds for a string only: a value that is not a string is rendered as `json` and cut, which is
   the Lean delta entry for 2.7a and 2.8c in section 6.
2. **6.11 and 6.9: closed by the statement review.** 6.11's template has no placeholder: the contract takes
   Lean's text, and Python's lost label is an entry of the delta report (section 6). 6.9's text names the rule
   in both validators; Python's text without a rule belongs to 6.10b (section 6, `soft_semantic`).
3. **3.5 as hooks.** "No W3 definition" and "no W5 data flag" could be T1 checks on the raw predicate entries if
   the raw and decoded conditions are shown equal; they are hooks here because that was not checked.
4. **The plain-language sentences of 3.3** have not been shown to a reader. They are fixed here so that every
   surface uses the same words; W8's fidelity gate may change them.
5. **A viewed include's `path`.** It is the include site, as the debate fixed. Whether an IDE can place a
   diagnostic usefully from `inner_path` is not known before S5.

## 13. Statement review response table (draft 2)

Source: `manage-agents/debates/wire-spec/{fable,astra}.md` (Sol at xhigh stood in for Astra in all three rounds,
as `astra.md` records). Verdict: **FIX, by statement edits only**, in one spec and plan commit, after which S0 to
S3 start with no further round if the edits land as listed. The joint position is Fable's round 3, which Astra's
round 3 accepts and which the DRI ruling in `fable.md` adopts: A1 (the `null` literal is removed; Astra's
alternative, a second parser and encoder that admit `null`, is not adopted), A2 as in Fable's round 2, and F1 to
F4 with the four minor edits of Fable's round 1. No frozen validator changes, and this draft changes nothing
else in the design.

| Review edit | Change in this draft |
|---|---|
| A1. A literal is a Boolean, an integer or a string; `null` is written as the type form `"null"`. Only the literal goes: the runtime value `null` and the type form stay (Astra's round 3) | 2.3, the literal sentence and the sentences after it, which also state what replaces an `enum` over `null` and that `requires` and `excludes` have no `null` item (Fable's round 3, point 2; Astra's round 3); 2.1 is unchanged; section 12, R2 and R16 |
| A1. `Value` loses its `null` constructor; `Atom.null` stays | 5.1 |
| A1. "A contract, `limits.json` and `names.json` are read with `ve.wire.loads_json`; a file it refuses is `WC01`." | 2.2; 4.3, `WC01`. As a consequence a negative limit is refused by the reader, so that clause leaves `WC05` |
| A1. Fixture L15: `const` with the value `null` gives `WC01` | 8.2, L15 |
| A1. "A `null` literal, if a later unit needs one, is a change of `format` with its own statement review." | 2.3, last sentence of the literal paragraph |
| A2. The include form gains `"says"?`, required when `view` is present and refused otherwise | 2.3, the entry table and the `says` bullet; 2.5, the view row |
| A2. "For a view, `says` states the value the included checks read" | 3.1, the paragraph after the table |
| A2. The 3.1 include row reads `as transformed by the view <view>: <says>` | 3.1, include row. Because the `says` sentence now closes the sentence, the `as` clause became a sentence of its own, `They are reported with code <code>.` |
| A2. `WC08`: "a hook, a classifier member or an include with a `view`, without `says`" | 4.3, `WC08`; `says` without a `view` is a shape error, `WC01` |
| A2. Corpus 3.4 carries its `says`; 8.1 states the `says` of 4.1, 4.3a, 4.3b and d2 | 8.1, the 3.4 row and the block of `says` sentences. The sentence of 3.4 is the review's; the other four were written for this draft from the hooks' behaviour table |
| A2. L8 adds: include 3.4 without `says` gives `WC08` | 8.2, L8 |
| F1. `soft_semantic`: Python's `ResourceLimit: derived carve-out` without a rule is W1's limits on `T′` (`softnorms.py:949–952`), member 6.10b, not 6.9 | section 6: the third Python difference; the delta table's 6.9 row is replaced by a 6.10b row; section 12, open point 2 |
| F2. 6.11's template is `ResourceLimit: generated soft premise`, without a placeholder (`Soften.lean:650–653`); Python's lost label is a delta entry | section 6: the 6.11 row and the delta table; section 12, open point 2 closed |
| F3. `rule_typing` types and then screens each condition before the next (`Phases.lean:305–313`, `softnorms.py:422–429`); a catalogue fault for a classifier member carries its order key inside the set, defaulting to the index in `emits` | 2.6, the position sentences; section 6, "Order inside the set"; 8.3, tiers 0 and A; section 12, R18 |
| F4. `soft_semantic` rule 3a: a base-W1 failure with any other message names no member and shows as a residual | section 6, rule 3a |
| Minor. `h'` in `run_congr_reached` is renamed `g` | 5.3 |
| Minor. `raw` on a value that is not a string is cut at 80 bytes, and `Phases.lean:89` prints it whole: a Lean delta entry for 2.7a and 2.8c | section 6: the delta table has a column for Lean today; section 12, open point 1 |
| Minor. The lint refuses three cases that were not defined: `"on": "key"` on an empty pointer, one argument name under two renderers, an id comparison of a digit run with a letter run | 2.4 and `WC06`; 2.7 and `WC04`; 2.3 and `WC02` |
| Minor. 2.9 (B) said views "reached"; the theorem needs views equal everywhere | 2.9 (B); section 12, R19 |
| Start of the build: no stage starts before the commit (Fable withdrew "S0, S1a and S1b may start now" in round 2) | the status paragraph |
| Plan wording synchronised with A1 and A2 | plan draft 3: its status paragraph, 2.1 (the reader and the excerpt's include), 2.3 (the `says` of a view) and its section 12 |

## 14. Wire review response (2026-10-02)

Source: `manage-agents/wire-review-astra.final.md` and `manage-agents/reviews/wire-review-fable.md`, both FIX,
on branch `wire/integrate` at `8cb69fda`. Each finding was treated as a class and fixed with a regression test;
the commits are listed in the branch history. The pilot contract is at revision 2.

| Finding | Change |
|---|---|
| Astra A, Fable B4: a viewed include over a nested include gave Python `path` `/doc/part`, `inner_path` `/x` | the Python engine keeps Lean's frame (`Frame.enter`): under a view, `path` is the view's site and `inner_path` the sites inside the view and the local pointer; an inner `as` takes the class of its declaring contract. Corpus contracts `mid@0` and `forms@0` run the case in both engines |
| Fable B2, C: `{{` and `}}` by sentinel characters; the Lean generator ignored them | one template split (`engine.pieces`) for the engine, the Lean generator and the lint |
| Fable A1: Python 6.10c against Lean 3.2 on `norm-defaults@0` | the Python hooks 2.3 and 3.2 use the Lean route's lists, compared with the Lean sources by a test. The registries differ on six profiles; on `rights@0` Python's legacy validator accepts and the Lean route rejects, a legacy verdict difference, so S3-pre (section 9) is open (`conformance/wire-contract/s3-pre.md`) |
| Fable B1: 6.4a names differ | the Python hook goes prefix by prefix, as both legacy validators |
| Fable B3: 6.4a and 6.4b carry an `at` the table of section 6 does not | removed (revision 2); `path` is `""` |
| Astra B, Fable B4: the nested-view lint rule was dead; the WC08 catalogue clause was absent | WC09 searches the included phases, through further includes; WC08 reads the index of the fault catalogue. A member with no known reaching input may be declared unreached with its reason (`conformance/wire_contract_faults.py`, `UNREACHED`: 6.10c); the gate reports it as uncovered. The fixtures L1 to L13 and L15 of 8.2 are now tests |
| Astra B, Fable B5: the flat English table gave 2.16b and 2.16c, and 2.17c and 2.17d, one sentence each; raw `@/*`; vague sentences | 3.1 is revised: items are named by their group's id, a group's sentence names the checks it covers, rows inside a group are marked; the hand-written sentences of 2.3, 3.2, 4.2a, 4.13b, 4.13d, 5.4, 5.7, 5.8a, 5.8b, 5.9b, 6.2, 6.3, 6.4a, 6.4b and 6.15 are made exact |
| Astra B, Fable B6: tiers 0 and A checked codes; the masking oracle read Lean's result; two accepted inputs replayed; feasibility hard-coded; E40, E41 untested; the 8.1 coverage rule unmet | the gate's oracle is the fault catalogue: a hand-written check and path per fault, positions read from the contract, and the record fields `contract` to `path` compared in both engines; Lean's text is compared with the route's for checks that are not inherited. The replay has 1,348 sources. Feasibility is computed. E40 and E41 run against `ve_diagnose`. The corpus gains `mid@0` and `forms@0`, and a test measures the 8.1 coverage rule |
| Astra B: coverage openly unmet | witnesses were found for 6.10a (a holistic collision puts a cycle into `T′`), 5.8a on a later condition and 4.11b (in Python only: a `null` the wire readers refuse). Two gaps remain and are reported with their reasons: 1.1 cannot be masked, because it is the first instance of the table, so the masking clause of 8.3 needs the statement edit "every check after the first instance"; and no input is known that reaches 6.10c, the fallback member of `soft_semantic` |
| Astra C, Fable C: theorems in `VE.WireContract`, the spec says `VE.Contract` | section 5 records the namespace as built and the qualified names; the statements' formulas are those of 5.3 |
| Fable C: `soft_semantic` rule 12 tested a message prefix; adapters differed on a missing `kind` or `norms` | rule 12 tests the class `ResourceLimit`; the Python adapter gives `null` for a missing member and refuses a case without a known kind, as Lean's |

Open for the DRI, then: the `rights@0` legacy verdict difference (S3-pre), the statement edit for 1.1's masking
witness, and whether 6.10c stays a member with no known reaching input. All three are settled in section 15.

## 15. Wire re-check response (2026-10-02)

Source: `manage-agents/wire-looprecheck1.final.md`, FIX, on branch `wire/integrate` at `ff3c92fd`. Each
finding was treated as a class and fixed with a regression test; the commits are listed in the branch
history. The pilot contract is at revision 3. The gate (`soft-norms@0-gate.json`) runs 6,007 cases with no
mismatch and residual 0 in both languages, coverage met, and S3-pre closed; it exits 0.

| Finding | Change |
|---|---|
| A: the `rights@0` legacy verdict difference (Python's soft route accepts, the Lean route rejects at 3.2); S3-pre open | fixed outside the wire work, in Python's soft table, as S3-pre requires: the Lean rights route strips `rights@0` before the soft decoder, so Python's check 3.2 refuses `rights@0` unless its route is the caller (`ve/softnorms.py`, `LAYER_ROUTES`; `RightsEnvironment.LAYERS`), with the Lean route's code and text. Both legacy validators now reject every profile outside the Lean route's registry; tier L adds a whole rights source; `s3-pre.md` records the fix. The code differences on `speech-acts@0` and on `unspecified` under `norm-defaults@0` remain, reported, for plan 5.1 step 5 |
| B: coverage unmet: no first-fault witness for 6.10c, no masking witness for 1.1 and 6.10c | 8.3's masking clause is stated for every check after the table's first instance (1.1 has no earlier check); 6.10c, the fallback member of `soft_semantic` that no input reached, is removed (revision 3): `soft_semantic` rule 13 now names no member, as rule 3a, so such a rejection would show as a residual, which the gate requires to be 0. `UNREACHED` is empty |
| B: tier A had no independent expected `text` or `args` | the catalogue carries hand-written `args` for every fault of a check that is not inherited, with the locations they read in the fault's footprint; the oracle renders the expected `text` from the contract's template itself; an inherited record's `text` must be its language's legacy text, with `args` `{"message": text}`. `record_problems` in the gate holds the comparison |

## 16. Wire re-check 2 response (2026-10-02)

Source: `manage-agents/wire-looprecheck2.final.md`, FIX, on branch `wire/integrate` at `846128ef`. The gate's
report is unchanged: 6,007 cases, no mismatch, residual 0 in both languages, coverage met, feasibility 51 of
67, S3-pre closed; it exits 0.

| Finding | Change |
|---|---|
| B: the gate's exit did not enforce the feasibility threshold of 45 (a report at 44 that matched the stored one passed) | treated as the class "a required row of section 9 the exit does not check": `gate_failures` in the gate lists every unmet row (tier 0 and A mismatches, the residual count of each language, coverage, feasibility, S3-pre) and the gate exits non-zero on any. Feasibility is judged from `n1 + n2` against the section's own 45 of 67, not from the report's `met` or `threshold`, and a report whose `total`, `threshold` or `met` disagrees with them fails |
| C: `record_problems` ignored an unexpected top-level field, so one both engines added passed | every engine record, in every tier (with or without an expected record), must have exactly the members of `$defs/fault` in `contract.schema.json`, which is closed, and `args` must be an object; a test ties the gate's field set to the schema |

## 17. Wire loop final response (2026-10-02)

Sources: `manage-agents/wire-loop.final.md`, FIX, on branch `wire/integrate` at `92199a0d`, and the
orchestrator's `manage-agents/wire-gate-directive.md`. The gate (`soft-norms@0-gate.json`) runs 7,468 cases
(tier 0 165, tier A 4,280, tier B 200, replayed 2,809, legacy differences 14) with no mismatch, residual 0 and
deferred 0 in both languages, coverage met, feasibility 51 of 67 (`n1` 43, `n2` 8), S3-pre closed; it exits 0.

| Finding | Change |
|---|---|
| B: a nonempty `coverage_unmet` passed with `coverage_met` true; B: recorded legacy verdict differences passed with an `s3_pre` of `closed`; C: feasibility counts above the 67 numbered checks passed | treated as the class "a stated summary trusted over its data": `gate_failures` judges coverage from the unmet lists and from the checks without a first or masking witness (a Lean-only gap only where `coverage_unmet_reasons` explains it), S3-pre from `legacy_verdict_differences` (and fails if the legacy-difference tier ran no case), and feasibility from `n1`, `n2`, `coarse` and `t3`, non-negative integers that must partition the 67 numbered checks. Each stated summary (`coverage_met`, `s3_pre`, `total`, `threshold`, `met`, `all_check_count`, `first_check_count`, `masking_not_required`) must also agree with its data, and every tier must have run |
| C: Tier B and replay records accepted a non-string `text` | every member of every engine record, in every tier, has the type `$defs/fault` gives it in `contract.schema.json` (read from the schema; a Boolean is not an integer) |
| Directive: the corpus condition | the gate replays, deduplicated, every `soft-norms@0` input of `tests/test_*contract*` (which include `tests/test_wire_contract*`) and of the soft conformance fixtures: the pairs and triples of `multi_fault_cases()`, P1 to P17, the shadow, probe, S3-pre and admission sources, the acceptance fixtures of soft-norms.md 10 and the Rust fixtures' sources, each built by the code that builds it for its test. `tests/test_wire_gate_corpus.py` reruns the contract tests under a recorder that captures every input sent to either engine or either legacy validator and fails if one is missing from the gate's corpus; 1,442 were missing before |

## 18. Wire2 loop response (2026-10-02)

Sources: `manage-agents/wire2-loop.final.md`, FIX, on branch `wire/integrate` at `03f80e34`, and the
orchestrator's `manage-agents/wire-corpus-directive.md`. The gate (`soft-norms@0-gate.json`) runs 8,576 cases
(tier 0 165, tier A 4,280, tier B 200, replayed 3,917, legacy differences 14) with no mismatch, residual 0 and
deferred 0 in both languages, coverage met, feasibility 51 of 67 (`n1` 43, `n2` 8), S3-pre closed; it exits 0.

| Finding | Change |
|---|---|
| B: the corpus condition was unmet: 56 sources of `expected_rejections()`, 24 of `generated_invalid_exceptions()` and 205 of `near_limit_cases()` were missing, and the corpus test enumerated a subset | treated as the class "an input the tests or the soft conformance module exercise that the gate does not replay". `conformance/soft_norms.py` names what its comparison submits (`exercised_sources()`: the seeded trees `main` examines, 1,000 accepted, `rejected_cases()` and the near-limit cases), and the gate replays all of it. The recorder now also runs the soft tests (`tests/test_soft*`), records the calls the conformance module makes when a test runs it, and sees `SoftNormDocument` over a test's `SoftEnvironment` and the soft route's runner; the 41 test inputs that no generator builds are stored in `soft-norms@0-test-inputs.json` (`--record-test-inputs` rewrites it), and Lean reads none that carries a `null`. A second test calls every public function of the conformance module and fails on any source it yields that the corpus lacks, or on a new function it cannot call |
| B: any entry of `coverage_unmet_reasons` exempted a missing Lean witness | 8.3 now has a table of allowed coverage gaps (G1: Lean, a check every catalogue fault of which only the in-process API can carry). The gate reads the table from this file, judges where a row applies from the fault catalogue, and exempts a gap only under the row's reason verbatim; any other entry fails |
| C: a report with no Lean deferral and `deferred_share.lean` 0.75 passed | the deferred share is judged from the deferred counts: each is a non-negative integer within the cases run, Lean's is 0 (2.8), and each share is its count over the cases. The report counts a deferred outcome under its language's share, never as residual, and a `ve_diagnose` row without an outcome is a mismatch, not a clean outcome |
