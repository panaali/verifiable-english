# AR-21 statements (consolidation step 3a: theorem only)

Plan row 3a (`docs/CONSOLIDATION-PLAN.md` step 3; architecture plan 4.5, AR-21): closure's `replay E a b` on a
certificate equals Core's `replay E a b` on its embedding (`embedClosure`, `embedCert`), for all `a b`; the same for
the trace decoders and for `Steps.closure` against `Steps.core`; the two `checkCertificate`s are not equal, so a
separate corollary states, per accepted version, what AR-22 needs.

All of it is in the new proof module `lean/VE/Closure/CoreEquiv.lean`, namespace `VE.Closure.CoreEquiv`, so
`Tableau.X` is `VE.Closure.Tableau.X` (the closure copy, `lean/VE/TableauExtended*.lean`), `Core.Tableau.X` is
`VE.Core.Tableau.X` and `Formula` is `VE.Closure.Formula`. No existing definition or statement changes.

## The embedding (proof helpers, class P)

`embedClosure` is the existing `VE.Core.embedClosure` (`lean/VE/Core/Conservativity.lean`). The new maps are
constructor for constructor; nothing is dropped or renamed (the version string and ids are copied).

```lean
def embedToken : Tableau.Token → Core.Tableau.Token
  | .constant c => .constant c
  | .witness i => .witness i

mutual
def embedTrace : Tableau.Trace → Core.Tableau.Trace
  | .close => .close
  | .expand rule index parameter children => .expand rule index parameter (embedTraces children)
  | .induct index sort P children => .induct index sort (embedClosure P) (embedTraces children)
def embedTraces : List Tableau.Trace → List Core.Tableau.Trace
  | [] => []
  | t :: ts => embedTrace t :: embedTraces ts
end

def embedCert (c : Tableau.Certificate) : Core.Tableau.Certificate :=
  ⟨c.checker_version, c.environment_id, c.premise_meaning_ids, c.conclusion_meaning_id,
    embedTrace c.trace⟩

def embedSigned (a : Tableau.Signed) : Core.Tableau.Signed :=
  ⟨embedClosure a.formula, a.positive, a.bindings.map embedToken⟩

def embedBranch (b : Tableau.Branch) : Core.Tableau.Branch :=
  ⟨b.formulas.map embedSigned, b.witnesses, b.expanded,
    b.instantiated.map fun p => (p.1, embedToken p.2)⟩
```

## 1. Replay, both flags explicit

**`replay_embed`.** For every environment, both flags, every fuel, branch and trace, closure's replay gives the
same Boolean as Core's replay of the embedded branch and trace.

```lean
theorem replay_embed (E : Environment) (compound induction : Bool) (fuel : Nat)
    (b : Tableau.Branch) (t : Tableau.Trace) :
    Core.Tableau.replay E compound induction fuel (embedBranch b) (embedTrace t) =
      Tableau.replay E compound induction fuel b t
```

**`replay_certificate_embed`.** On a certificate: closure's replay from its initial branch equals Core's replay
of `embedCert c` from the initial branch of the embedded premises and conclusion, for both flags and every fuel.

```lean
theorem replay_certificate_embed (E : Environment) (compound induction : Bool) (fuel : Nat)
    (premises : List Formula) (conclusion : Formula) (c : Tableau.Certificate) :
    Core.Tableau.replay E compound induction fuel
        (Core.Tableau.initial (premises.map embedClosure) (embedClosure conclusion))
        (embedCert c).trace =
      Tableau.replay E compound induction fuel (Tableau.initial premises conclusion) c.trace
```

## 2a. Step counts

**`steps_embed`.** A closure trace and its embedding count the same replay steps, so the step limit refuses the
same certificates.

```lean
theorem steps_embed (t : Tableau.Trace) :
    VE.Route.Steps.core (embedTrace t) = VE.Route.Steps.closure t
```

## 2b. Trace decoders: the equality is false

The plan's statement, `VE.Core.Wire.decodeTrace fuel j = (VE.CertificateWire.decodeClosureTrace fuel j).map
embedTrace` for all `fuel j`, is false, so it is not stated (DRI-RULINGS "never covered": no hypothesis is added
to make it true). Core's invariant decoder (`VE.Core.Bridge.decodeFormula`) has an `atom` case that closure's
(`VE.Closure.Bridge.decodeFormula`) lacks. The mechanised counterexample:

**`decodeTrace_ne_embed`.** There is a fuel and a JSON trace on which Core's decoder does not return the embedding
of closure's answer: the node `{"rule": "closure-induct@1", "at": 0, "sort": "s", "invariant": ["atom", "p",
[["const","a"],["const","a"],["const","a"]]], "children": []}` at fuel 125 decodes in Core and is refused by closure
with `invalid indexed formula`.

```lean
theorem decodeTrace_ne_embed :
    ∃ fuel j, Core.Wire.decodeTrace fuel j ≠
      (VE.CertificateWire.decodeClosureTrace fuel j).map embedTrace
```

Reported for the DRI in REPORT.md: the decoder part stops here.

## 3. The two `checkCertificate`s (corollaries for AR-22)

Their equality is false and is not stated: Core accepts only `ve-tableau-core-checker@1` and runs
`replay E true true`; closure accepts `ve-tableau-closure-checker@0` and `@1` and runs
`replay E true (version == @1)`. What AR-22 needs instead:

**`checkCertificate_eq_core_replay`.** Closure's checker is its own version gate and the well-formedness checks of
the embedded formulas, then Core's replay of the embedded certificate with closure's flag choice.

```lean
theorem checkCertificate_eq_core_replay (E : Environment) (premises : List Formula)
    (conclusion : Formula) (c : Tableau.Certificate) :
    Tableau.checkCertificate E premises conclusion c =
      ((c.checker_version == "ve-tableau-closure-checker@0" ||
          c.checker_version == "ve-tableau-closure-checker@1") &&
        (premises.map embedClosure).all (fun f => f.check E []) &&
        (embedClosure conclusion).check E [] &&
        Core.Tableau.replay E true (c.checker_version == "ve-tableau-closure-checker@1") 125
          (Core.Tableau.initial (premises.map embedClosure) (embedClosure conclusion))
          (embedCert c).trace)
```

**`checkCertificate_v0`.** An `@0` certificate is checked by Core's replay with the induction flag off.

```lean
theorem checkCertificate_v0 (E : Environment) (premises : List Formula)
    (conclusion : Formula) (c : Tableau.Certificate)
    (hv : c.checker_version = "ve-tableau-closure-checker@0") :
    Tableau.checkCertificate E premises conclusion c =
      ((premises.map embedClosure).all (fun f => f.check E []) &&
        (embedClosure conclusion).check E [] &&
        Core.Tableau.replay E true false 125
          (Core.Tableau.initial (premises.map embedClosure) (embedClosure conclusion))
          (embedCert c).trace)
```

**`checkCertificate_v1`.** An `@1` certificate is checked by Core's replay with both flags on, as Core's own
checker runs it.

```lean
theorem checkCertificate_v1 (E : Environment) (premises : List Formula)
    (conclusion : Formula) (c : Tableau.Certificate)
    (hv : c.checker_version = "ve-tableau-closure-checker@1") :
    Tableau.checkCertificate E premises conclusion c =
      ((premises.map embedClosure).all (fun f => f.check E []) &&
        (embedClosure conclusion).check E [] &&
        Core.Tableau.replay E true true 125
          (Core.Tableau.initial (premises.map embedClosure) (embedClosure conclusion))
          (embedCert c).trace)
```

**`checkCertificate_other_version`.** Any other version string is rejected.

```lean
theorem checkCertificate_other_version (E : Environment) (premises : List Formula)
    (conclusion : Formula) (c : Tableau.Certificate)
    (h0 : c.checker_version ≠ "ve-tableau-closure-checker@0")
    (h1 : c.checker_version ≠ "ve-tableau-closure-checker@1") :
    Tableau.checkCertificate E premises conclusion c = false
```

The hypotheses `hv`, `h0`, `h1` select a case of the version gate the checker itself tests; they do not restrict
the equality of statement 1, which holds for all inputs.
