# VE v0: Relational Claim Language

**Status:** Proposed specification, September 20, 2026. The definitions below are design notation, not compiled Lean code or completed proofs. This document owns v0 syntax and semantics; see the [architecture](../architecture-and-design.md) for purpose and the [verification contract](verification-contract.md) for guarantees.

## Semantic profile and environment

The only admitted profile is `relational-fol@0`, using `ve.core@0`. A document consists of closed first-order formulas interpreted over a typed relational structure. The profile supports two distinct judgments: evaluating claims in a supplied finite structure, and certifying that a conclusion follows from explicit premises in every admissible structure. The [debate protocol](debate-protocol.md) defines the latter's claim and certificate bindings. Neither judgment supplies evidence that the vocabulary or premises accurately describe the world, nor issues commands or permissions.

The environment `E` contains the language/profile identifiers, specification revision, and complete local vocabulary `Σ`. Its artifact identifier binds all these fields together. `Σ` declares:

- a finite set of sort identifiers;
- unary predicate identifiers with one argument sort;
- binary predicate identifiers with an ordered pair of argument sorts;
- constant identifiers with their sorts;
- a human-readable description for each declaration, shown during confirmation.

Predicate symbols have no hidden definitions or inference rules. A supplied model determines their extensions. Descriptions explain the intended modeling convention; checking the types does not prove those descriptions correspond to real-world concepts. Changing a description changes the vocabulary package identity and invalidates prior human confirmation.

No remote lookup, implicit import, subtyping, overloaded symbol, inferred sort, recursive definition, or executable vocabulary entry is allowed. Unknown language/profile versions are errors. Schema and model validation are part of the checking boundary, not preprocessing that may silently repair inputs.

This fragment supports the first experiments on requirement reinterpretation and inconsistent meanings across argument branches. Task selection must establish which requirements and deductions it can express without turning difficult checks into opaque agent-supplied predicates. Arithmetic and claims about textual formatting need specified extensions or input adapters; a predicate named `uses_decimals` does not implement either check. The [architecture](../architecture-and-design.md#language-choices) explains the tradeoffs.

The environment wire shape is shown below using the worked example's vocabulary. All displayed fields are required, including empty maps; unknown fields are rejected. Sort entries contain only `description`; predicate entries contain `arguments` (an ordered array of one or two declared sorts) and `description`; constant entries contain `sort` and `description`. Descriptions are nonempty Unicode strings. The specification revision must identify an immutable revision supported by the checker; a matching language name alone is insufficient. This draft identifier is illustrative, not an implemented release.

```json
{
  "language": "ve.core@0",
  "profile": "relational-fol@0",
  "spec_revision": "ve-v0-draft-2026-09-20",
  "vocabulary": {
    "sorts": {
      "person": {"description": "A person recorded in the inventory."},
      "service": {"description": "A service recorded in the inventory."}
    },
    "predicates": {
      "deployed": {"arguments": ["service"], "description": "Recorded as deployed in this inventory."},
      "owns": {"arguments": ["person", "service"], "description": "The person is recorded as an owner of the service."},
      "reviewed": {"arguments": ["service"], "description": "Recorded as reviewed in this inventory."}
    },
    "constants": {}
  }
}
```

## Surface grammar

Identifiers match `[a-z][a-z0-9_]*`. Semantic syntax is ASCII, case-sensitive, and uses the literal spaces and punctuation below. Each statement ends with a period and LF, including the last. No comments, tabs, CRLF, or alternate Unicode punctuation are accepted by the strict parser. An authoring tool may propose a rewrite, retaining the original prose separately.

These restrictions bound the first parser/proof experiment; they are not required by the concept of unambiguous language. Their usability, including newline and identifier friction, is unmeasured. A future relaxation must update the lexical specification and source-correspondence obligations rather than silently normalizing input at the checking boundary.

In this EBNF, quoted strings are literal bytes, `LF` is one newline, commas between productions mean concatenation, and braces mean repetition. `sort`, `unary`, `binary`, and `constant` must resolve to the corresponding vocabulary category. `variable` is an explicit binder name.

```ebnf
document  = statement, LF, { statement, LF } ;
statement = formula, "." ;
formula   = "true"
          | "false"
          | term, " is ", unary
          | term, " ", binary, " ", term
          | term, " equals ", term
          | "not (", formula, ")"
          | "(", formula, ") and (", formula, ")"
          | "(", formula, ") or (", formula, ")"
          | "if (", formula, "), then (", formula, ")"
          | "for every ", sort, " ", variable, ", (", formula, ")"
          | "there exists ", sort, " ", variable, ", (", formula, ")" ;
term      = variable | "@", constant ;
```

Reserved identifiers are `true`, `false`, `is`, `equals`, `not`, `and`, `or`, `if`, `then`, `for`, `every`, `there`, `exists`, `believes`, `must`, and `eventually`. Schema symbol identifiers are pairwise distinct across categories, cannot be reserved, and cannot match `x[0-9]+`, which is reserved for generated binder names. Variables cannot equal schema identifiers or reserved words. A binder cannot shadow an active binder. Free variables are rejected. Sibling scopes may reuse a binder name.

The grammar deliberately has no implicit precedence or extra grouping production: parentheses belong to the displayed constructs. Unary/binary predicate arity is fixed by the schema. Invalid input must fail with a location and diagnostic; never reinterpret an unknown construct as a different valid one. An implementation must prove grammar uniqueness rather than rely solely on deterministic parser execution.

## Typed abstract syntax and binding

Let `Γ` be the ordered stack of bound-variable sorts, nearest binder first. The following constructors are a typed design, with equality and argument-sort evidence implicit in the notation:

```text
Term(Σ, Γ, s) =
    Var(i)                 where Γ[i] = s
  | Const(c)               where Σ.constants[c] = s

Formula(Σ, Γ) =
    Top | Bottom
  | Unary(p, t)            where p : s and t : Term(Σ, Γ, s)
  | Binary(r, t, u)        where r : (s1, s2), t : Term(Σ, Γ, s1),
                                u : Term(Σ, Γ, s2)
  | Eq(t, u)               where t and u have the same sort
  | Not(a) | And(a, b) | Or(a, b) | Implies(a, b)
  | Forall(s, body)        where body : Formula(Σ, s :: Γ)
  | Exists(s, body)        where body : Formula(Σ, s :: Γ)

Document(Σ) = nonempty ordered list of Formula(Σ, [])
```

Binder indices count outward from zero; source variable names and source spans are retained only in separate diagnostic metadata. Parsing is responsible for resolving names to indices without capture. Thus alpha-renaming produces the same semantic AST. Equality is equality of elements of the same declared sort, not string similarity or an implicit relation between different sorts.

The typed notation specifies admissible semantic objects, not a mandatory implementation representation. The formalization may use intrinsically typed constructors or raw constructors with a proved well-formedness predicate. Choose after a representative nested-binding parser/printer proof; either choice must expose the same indexed wire AST and denotation. Runtime data structures may differ again, subject to correspondence. Source names remain available for diagnostics in every representation.

For example, `for every service s, (there exists person p, (p owns s)).` has AST:

```text
Forall(service, Exists(person, Binary(owns, Var(0), Var(1))))
```

Under the two binders, `Γ = [person, service]`; reversing the relation's arguments is a type error. No pronouns, implied quantifiers, higher-order arguments, function symbols, or embedded Lean source occur in v0.

## Structures and denotation

An admissible structure `S` assigns a domain `D_s` to each declared sort, a correctly sorted domain element to each constant, and a relation of the declared sorts to each predicate. Domains may be finite or infinite, and empty if no constant requires an inhabitant. There is no unique-name assumption. A valuation `ρ` assigns a correctly sorted element to each bound variable. Variables and constants denote their assigned elements; atomic predicates denote membership in the assigned relations.

The formula clauses are:

```text
⟦Top⟧ = True                        ⟦Bottom⟧ = False
⟦Eq(t,u)⟧ = (⟦t⟧ = ⟦u⟧)          ⟦Not(a)⟧ = ¬⟦a⟧
⟦And(a,b)⟧ = ⟦a⟧ ∧ ⟦b⟧           ⟦Or(a,b)⟧ = ⟦a⟧ ∨ ⟦b⟧
⟦Implies(a,b)⟧ = ⟦a⟧ → ⟦b⟧
⟦Forall(s,a)⟧(ρ) = ∀ d ∈ D_s, ⟦a⟧(d :: ρ)
⟦Exists(s,a)⟧(ρ) = ∃ d ∈ D_s, ⟦a⟧(d :: ρ)
⟦document⟧ = conjunction of its closed statements, evaluated at ρ = []
```

Write `Denote(E,A,S)` for this interpretation. For a finite list of closed premises `Δ` and closed conclusion `C`, all under `E`, logical consequence means:

```text
Entails(E, Δ, C) := ∀ admissible S,
  (∀ A ∈ Δ, Denote(E,A,S)) → Denote(E,C,S)
```

This quantifies over all admissible structures, not just examples submitted during a debate. Universal statements over empty domains and implications with false antecedents are true. Nonemptiness or existence needed by an argument must be expressed as premises; the checker may not infer it from a sort name or an illustrative example.

## Finite models and evaluation

A valid model `M` supplies a finite enumeration `D_s` for each declared sort, an element of `D_s` for each constant of sort `s`, and a finite set of tuples for each predicate, matching its declared arity and sorts. Every declared sort, constant, and predicate must have an entry, even when its domain or relation is empty. Unknown entries, duplicate entries, dangling entities, and wrong-sort tuples are errors.

An entity is identified by `(sort, local_id)`; identical strings in different sorts do not make equal entities. Local IDs use the identifier character pattern, but may equal reserved words or schema names because they occur only as model data. Constants may denote the same entity; no unique-name assumption is inferred. Domains may be empty if no declared constant requires an inhabitant. The inventory includes `complete: true`: the submitter explicitly attests that it is the complete finite structure to be evaluated. This is a data-model assertion, not a checker guarantee of completeness about reality.

The model has exactly four required fields: `complete` (the literal Boolean `true`), `domains` (sort-to-array-of-local-IDs map), `constants` (constant-to-local-ID map), and `relations` (predicate-to-array-of-tuples map). Tuple entries are local-ID strings whose sorts come from the predicate signature. Unknown fields are errors; no defaults are inserted. Duplicate JSON object keys must be detected before a decoder can overwrite them.

Within that supplied structure, a tuple absent from a declared relation is false. A missing relation entry is an invalid model, not an empty relation. This distinction prevents a partial submission from silently being evaluated as a complete model.

Every valid finite `M` determines an admissible structure, written `asStructure(M)`. Use the same denotation above; abbreviate `Denote(E,A,asStructure(M))` as `Denote(E,A,M)`. All predicate membership and equality tests are decidable on these finite structures. This permits a terminating recursive Boolean evaluator with a proposed theorem equating its result to denotation.

A finite model satisfying every premise and falsifying the conclusion is a counterexample to `Entails(E,Δ,C)`. One model satisfying the conclusion does not prove entailment. Failure to find a finite counterexample also does not prove entailment. No complete decision procedure or terminating proof search for unrestricted first-order consequence is promised.

Universal quantification over an empty domain is true; existential quantification is false. Material implication with a false antecedent is true. These are deliberate profile rules. A user who needs a nonempty set of deployed services must state that constraint explicitly. UI diagnostics should surface vacuous satisfaction rather than disguise it as evidence of a deployed service.

Closed-world evaluation applies only within the complete submitted model. An empirical premise with no evidence remains unresolved in the debate; it does not acquire a false value from omission. The finite-model wire format represents examples and countermodels, not an incomplete knowledge base.

## Canonical representation and identity

`print_E` emits the exact surface grammar, naming binders `x0`, `x1`, … in preorder, resetting the counter at each statement. Names are globally fresh within a statement. Statement order and all logical constructors remain unchanged. Every well-typed closed AST has one proposed rendering; bound source names do not form part of semantic identity.

Generated names make identity independent of the author's choices, but `x0` and `x1` are harder to read than `s` and `p`, and reviewers see the canonical text. Whether to show reviewers the author's binder names, which a debater could choose to mislead, or names derived from the sort, such as `service1`, is open and should be settled in the inspection pilot. Identity would be computed from the indexed AST in either case.

`parse_E` accepts the strict grammar with any permitted binder names. `canonical_E(s)` additionally requires `print_E(parse_E(s)) = s`. Both ordinary binder names and canonical binder names may denote accepted VE; only the latter are canonical bytes. Do not silently modify the submitted source or claim its bytes were already canonical.

The only normalization in v0 is binder naming and fixed serialization. It does not reorder conjunctions, expand vocabulary definitions, identify synonyms, or solve logical equivalence. Its idempotence follows from the parser/printer contract once proved, not from a semantic-equivalence oracle.

For interchange, AST constructors use tagged JSON arrays: `["top"]`, `["bottom"]`, `["var", index]`, `["const", id]`, `["unary", id, term]`, `["binary", id, term, term]`, `["eq", term, term]`, `["not", formula]`, binary connective tags `and`, `or`, `implies`, and binder tags `["forall", sort, body]` / `["exists", sort, body]`. A document is an ordered array of formula arrays. Reject unknown tags, incorrect arity, and invalid indices before constructing the typed AST.

Use SHA-256 over domain-separated UTF-8 [JCS serialization](https://www.rfc-editor.org/rfc/rfc8785) for portable artifact identifiers. v0 JSON admits strings, booleans, arrays, objects, and bounded nonnegative integer indices; duplicate object keys and strings that violate JCS's Unicode requirements are rejected. Map keys follow JCS ordering. Model domain arrays and relation tuple sets are sorted lexicographically by their ASCII identifiers, comparing tuples component by component; duplicates are **rejected** before serialization. Arrays representing formula order, predicate argument sorts, or tuple argument order are never sorted. JSON formatting and set enumeration order do not affect semantic identity; original submitted bytes may be retained separately for transport provenance.

The identity preimages are:

```text
source_id = SHA256("ve-source-v0\n" || exact_source_bytes)
environment_id = SHA256("ve-environment-v0\n" || JCS(E))
meaning_id = SHA256("ve-meaning-v0\n" || JCS({environment_id, ast}))
model_id = SHA256("ve-model-v0\n" || JCS({environment_id, model}))
```

Digest fields encode the 32-byte result as 64 lowercase hexadecimal characters. `E` includes the schema package itself, not only a mutable URL. Its own digest is not a field within its preimage. Explanations, proof records, and signatures are outside the semantic AST and carry these identifiers separately. Byte-equal preimages are authoritative when available; hash equality is a practical identifier under the stated collision-resistance assumption, not a theorem of semantic equivalence. Signed transport and key management are outside v0.

## Worked example

This vocabulary uses `person` and `service`; unary `deployed` and `reviewed` take a service; binary `owns` takes a person and a service. No constants are declared. The descriptions mean records of these facts within the supplied inventory.

The three requirements, written in accepted but not canonically renamed VE, are:

```text
there exists service s, (s is deployed).
for every service s, (if (s is deployed), then (there exists person p, (p owns s))).
for every service s, (if (s is deployed), then (s is reviewed)).
```

Canonical text:

```text
there exists service x0, (x0 is deployed).
for every service x0, (if (x0 is deployed), then (there exists person x1, (x1 owns x0))).
for every service x0, (if (x0 is deployed), then (x0 is reviewed)).
```

A model payload, shown before canonical key ordering:

```json
{
  "complete": true,
  "domains": {"person": ["alice"], "service": ["api"]},
  "constants": {},
  "relations": {
    "deployed": [["api"]],
    "reviewed": [["api"]],
    "owns": [["alice", "api"]]
  }
}
```

All three constraints are satisfied in this model. Replacing `reviewed` with `[]` violates statement 3 at `s = api`. Replacing `owns` with `[]` violates statement 2 at `s = api`, with no person satisfying the inner existential. Deleting the `reviewed` key is an invalid-model error. An empty service domain, with correspondingly empty relation tables, violates statement 1 even though statements 2 and 3 are vacuously true.

These are hand-specified expected outcomes for the future conformance suite. They are not claims that a VE executable or proof checker has run.

## Rejection and resource behavior

Required diagnostic classes are `SyntaxError`, `UnknownSymbol`, `DuplicateDeclaration`, `UnboundVariable`, `ShadowedVariable`, `TypeMismatch`, `InvalidModel`, `UnsupportedProfile`, and `ResourceLimit`. Retain source spans separately from semantic nodes.

The proposed runtime envelope is at most 64 KiB of VE text, 64 formula nesting levels, 10,000 AST nodes, 32 sorts, 256 predicate symbols, 1,000 entities per sort, and 100,000 relation tuples total. Runtime identifiers (including model local IDs) are limited to 64 ASCII bytes; apply these limits and bounded integer checks before allocation. Input packages are capped at 16 MiB. These are initial engineering limits, not mathematical expressiveness claims; the unbudgeted reference definitions are separate from these runtime caps.

Finite quantifier evaluation can still be expensive. A budgeted evaluator returns `Satisfied`, `Violated`, or `ResourceLimit`; a budget exhaustion is never a negative result. Permit at most 1,000,000 formula-node evaluations per request initially, with host cancellation as a separate operational outcome. The logical reference evaluator is total; completeness claims for the deployed evaluator must be conditional on sufficient resources. Resource errors must not be reported as ambiguity, unprovability, or mistranslation.
