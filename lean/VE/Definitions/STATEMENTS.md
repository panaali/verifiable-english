# Definitions statement review

The current Lean implementation covers a fresh unary predicate whose body is
an existing unary predicate of the same sort. Python accepts acyclic unary and
binary bodies in identity-bound `defined` declarations and elaborates them to
background biconditionals. Lean and Rust explicitly reject these declarations
until their decoders and generalized expansion proofs land.

| Theorem | Statement in plain words |
|---|---|
| `faithful` | The generated biconditional holds exactly when the new and existing predicates agree on every object of their sort. |
| `conservative` | Every admissible input structure has exactly one admissible expansion satisfying that biconditional. |
| `alias_acceptance` | A checked certificate using the definition proves an old-vocabulary conclusion from old-vocabulary premises in every original admissible structure. |

`ve bundle check` replays each lemma's certificate, then admits a citation only
when its conclusion meaning ID is earlier in the same bundle, its environment
identity matches, its labelled hypotheses are on the citing branch, its
transitive leaves are preserved, and shared reading choices agree. Optional
Lean replay batches the certificates in one `route` invocation; the Lean route
currently rejects environments containing `defined` declarations.

The strict parser accepts input-only `define p(x) as (body).`, `(A) iff (B).`,
`every point x that is prime, (B).`, and `no point is prime.` under
`definitions@0`; printing expands these forms into the existing canonical
syntax. `ve definitions --env` previews each definition in natural English,
then checks that the complete English parser finds exactly one reading. The
dedicated English inputs “call a point prime if …” and “by Theorem 3” remain
not yet authorable. `ve assist` does not offer them before its fidelity gate.
N-ary definitions await the gated `nary@0` checker family.
