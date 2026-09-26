# Data profile stage 1

`data@0` declares binary relations that may be functional, total, or both.
The declarations are part of the environment identity. A functional relation
gives each source at most one target. A total relation gives each source at
least one target. The background generator adds the corresponding first-order
sentences in declaration order. A finite model with a conflicting or missing
target is invalid, with generator `flags`.

`$string` literals are declared constants. Two different declared literals
must denote different elements. This distinctness is an explicit background
premise for every entailment and a finite-model validity condition. Stage 1
permits equality and binary relation slots involving `$string`; it rejects
author-written quantification over `$string` with a stage 2 diagnostic. The
background generator alone may use those binders to express attribute flags.
The strict helper for “the value of this attribute is that value” requires
both flags and elaborates to the binary atom. Set membership is a declared
binary `member(element, collection)` relation, with no extra set axiom.

## Reviewed Lean statements, in plain words

- `functionalPremise_iff`: the generated functionality sentence says exactly
  that true rows with the same source have the same target.
- `totalPremise_iff`: the generated totality sentence says exactly that each
  source has a target in the declared target domain.
- `premises_sat_iff` and `generate_sat_iff`: a structure satisfies the
  generated sentences exactly when it has the declared flag meanings.
- `flags_model_valid`: a finite model that passes the regenerated flag
  sentence check has those meanings.
- `string_encoding_sound`: a checked consequence that includes literal
  distinctness holds in every string-admissible structure. It does not claim
  that every string consequence can be proved by this encoding.
- `fol_data_route_acceptance`: an accepted tableau certificate for the
  regenerated flag and literal background proves its conclusion in every
  admissible structure with those data meanings.
- `closure_data_route_acceptance`: the same claim holds for an accepted
  closure-language certificate after embedding the generated background.
- `fol_data_route_countermodel` and `closure_data_route_countermodel`: a
  checked finite countermodel that satisfies the regenerated flag and literal
  checks refutes the corresponding data consequence.
- `decodeDataModel_valid`: a finite model accepted on the Lean route satisfies
  both literal distinctness and the declared functional and total meanings.

`StringAdmissible` means structural admissibility plus distinct denotations
for different declared string literals. `DataAdmissible` adds the functional
and total meanings from flags. The certificate checks generated background
premises before caller premises. Python and Lean generate the same formulas
on 1,000 deterministic declaration sets; Rust validates the corresponding
finite relation tables. The standard Lean axiom allowlist is unchanged.

## Adapter record boundary

`glob@1`, `prefix@1`, and `regex@1` evaluate every listed input and record
an explicit result or error row. A record binds the domain, each input hash,
the output table hash, the parameters, the Python standard-library version,
and the adapter implementation hash. `ve adapter run --verify` recomputes
the table. The regular-expression dialect is a bounded subset of Python
`re.fullmatch` with no flags: at most one repetition of one atom, no grouped
repetition, alternation combined with repetition, backreferences, or special
groups. Rejected patterns produce explicit error rows. Prefix matching uses
`str.startswith`, and glob uses `fnmatch.fnmatchcase`. The record's
`adapter:<function>@<version>` label is available for citation, but the
document admission and argument checkers do not yet bind a verified record
row to a logical assumption leaf. They do not return proof-level UNKNOWN for
a missing table. The helper lookup returns `None` for a missing table, and
rejects inputs outside the recorded domain.

The Cedar helper keeps a missing attribute distinct from a present false
value as `(defined, value)`, including for `has` on a missing parent. It
compares JSON set values without depending on array order. The Gatekeeper
helper combines verified glob tables for image exemptions; its 20 frozen
string cases pass. These helpers do not yet implement the whole policy flow.

## Remaining integration gates

W3 definitions compose with W5 flags when the flags belong to base binary
predicates: the background order is flags, definitions, then literal
distinctness; finite models supply only base tables and compute defined tables.
The combined Python, Rust and Lean route fixture checks evaluation and
certificate binding. A defined predicate itself cannot carry either flag.
W2 document admission accepts regenerated `background:flags` leaves, while
document admission with W3 definitions remains explicitly deferred.

W4's Lean Core route currently accepts n-ary syntax but its vocabulary decoder
does not accept flagged predicates, defined predicates, or `$string` predicate
slots. Python and Rust handle the corresponding binary data and definition
declarations in an environment that also enables `nary@0`; the three-way
checker contract for those mixed declarations remains open. Lean rejects the
declarations rather than ignoring their generated background. W3's bundle
runtime includes flag premises in certificate binding, but the reviewed
`bundle_sound` theorem still states the definitions-and-literals fragment;
the combined theorem remains open.

The English surface renders and parses `the r of t is v` for a total,
functional attribute as the binary atom, and `the r of t is P` for a unary
target property as an existential witness on a user sort. A non-total
attribute is refused; 1,000 generated value sentences round trip through
the independent English grammar. String-valued target properties still need
stage 2 quantification. The `data@0` order-family combination with flagged
or string-valued relations is gated. Adapter assumption leaves, proof-level
missing-table UNKNOWN, Cedar's 30-item re-rating, its 143-policy run, the
joint 115-decision gate, and the full Gatekeeper policy flow remain. The
Cedar joint gate also requires the W1 norm adapter and W4 n-ary checker.
