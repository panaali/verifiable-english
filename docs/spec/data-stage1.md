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
the table. The regular-expression dialect is Python `re.fullmatch` with no
flags; prefix matching uses `str.startswith`, and glob uses
`fnmatch.fnmatchcase`. Adapter truth enters a policy proof only as a labelled
premise, `adapter:<function>@<version>`; the logical checker does not prove
the host string computation. A missing table yields UNKNOWN, and an input
outside the recorded domain is rejected.

The Cedar helper keeps a missing attribute distinct from a present false
value as `(defined, value)`. The Gatekeeper helper combines verified glob
tables for image exemptions. These helpers are independent of the unfinished
policy and English integrations.

## Remaining integration gates

The `data@0` order-family combination with flagged or string-valued
relations is gated. Natural definite-description parsing and rendering,
the 1,000 English round trips, full Cedar and Gatekeeper corpus runs, and
automatic adapter assumption leaves remain to be integrated. Cedar's joint
115-decision gate requires the W1 norm adapter and W4 n-ary checker.
