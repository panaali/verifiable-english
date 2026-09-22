# Feasibility check: original obfuscated physics arguments

Assessment date: 2026-09-22. This is a source inspection and a small Lean experiment,
not a complete formalization or a measured estimate of full development cost.

## Completed follow-up

[Package 3b: ICEBERG](iceberg/README.md) now supplies a direct conditional root
proof, explicit physical-model checklist, rational approximation contract, serial
whole-project build, qualitative VE skeleton, and measured phase cost ledger.
The feasibility-only assessment below is retained as the original starting point.

## Outcome

The mathematical cores of the iceberg and wrapping-ball examples look suitable for
a bounded formalization project. The train example needs a modeling decision that
can change which answer is correct. The inspected examples do not establish that
mandatory proofs would be unaffordable; they also do not establish that translating
entire adversarial transcripts would be cheap.

The experiment contains 11 checked declarations in `Feasibility.lean`. A local
Lean 4.24.0 invocation took 3.115 seconds including startup, imports, elaboration,
tactics, and kernel checking. All declarations depend only on `propext`,
`Classical.choice`, and `Quot.sound`; no `sorryAx` or additional axioms appear.
See `verification.json` for the command and output. This timing is a single local
measurement, not an authoring-time estimate or a representative benchmark.

**Scope:** rational algebra and explicit conditional models. There is no VE parser,
real-valued calculus, physical-model validation, empirical measurement, or proof of
all transcript nodes here. Model equations remain explicit premises.

## Sources actually inspected

The [Barnes–Christiano report](https://www.alignmentforum.org/posts/PJLABqQ962hZEqhdB/debate-update-obfuscated-arguments-problem)
links three dishonest argument trees. The pages return essentially no text through
the web reader, but their public interactive browser views still loaded. All three
rendered trees were read, together with the wrapping-ball root debate page:

- [Icebergs](https://meteor-debate.herokuapp.com/tree_view/pn5YDndA9fwosKwuZ/0): air,
  water, and metal inclusions in floating ice; the displayed branch introduces oil
  and compares displaced and melted volumes.
- [Train](https://meteor-debate.herokuapp.com/tree_view/QWGyt7pnKgZSGKR93/0): switching
  to a smaller circular track, with no friction. The displayed answers distinguish
  approximate constancy with possible slowdown from exact constancy.
- [Wrapping ball](https://meteor-debate.herokuapp.com/tree_view/RE3JNqDBxt9tQoJgB/0):
  a point mass on a string wrapping around a stopped pole, neglecting gravity.
  The dishonest branch compares with a scenario including gravity.

These are the displayed partial argument trees, not recovered exports of every
experiment or a complete audit of all hidden notes. Probability estimates and
phrases such as “no important difference” are not silently converted into exact
theorems in this experiment.

## 1. Icebergs: inexpensive algebra, explicit approximation boundary

Let rho be water density, b the initial displaced volume, a the final occupied
volume contributed by the melted composite object, m the ice mass, c the inclusion
mass, and V the inclusion's final contribution to occupied volume. With air
buoyancy neglected, the model equations are:

```text
rho * b = m + c
rho * a = m + rho * V
therefore rho * (a - b) = rho * V - c
```

The first theorem checks this identity. Further theorems use units with water
density numerically one and establish:

- A water inclusion gives zero change.
- A massless air inclusion that escapes gives zero change.
- A sinking inclusion denser than water gives a decrease.
- Retaining positive bubble mass while still neglecting air buoyancy changes the
  result to a decrease. Thus “approximately unchanged” needs an explicit tolerance
  and error analysis to become a quantitative result about the original problem.

These are idealized occupied-volume statements. Relating occupied volume to water
height requires tub geometry, no spill for the considered branch, and final
equilibrium. Distinguishing the water/oil interface from the upper surface of a
floating oil layer is also necessary when assessing the oil detour.

There is a useful local sign check: tree node 14 writes the change as final minus
initial volume, while node 12 associates a negative displaced-minus-melted
difference with a decrease. If those terms are the same before/after quantities,
the latter sign means an increase. `iceberg_sign_check` checks the arithmetic;
it does not resolve the source's physical vocabulary for the author.

Assessment: a good first pilot once the idealizations and output tolerance are
agreed. Extending rational algebra to real arithmetic is routine in principle, but
has not been compiled in this experiment. Deriving hydrostatics from deeper fluid
mechanics, or proving a quantitative air-buoyancy approximation bound, is additional
work and should not be included in a cheap estimate without testing it.

## 2. Train: model choice is the central obstacle

The displayed inference from absence of an opposing force to constant speed is
insufficient on its own: a forward force does positive work. A concrete rational
counterexample checks that logical gap. It is not a physically realizable
counterexample satisfying every premise about the original frictionless track.

For a point particle, unchanged kinetic energy and unchanged nonzero mass imply
unchanged squared speed; this is also checked. To infer unchanged speed requires
its nonnegativity, and to establish unchanged energy requires the no-work dynamics.

For a reduced rigid-body model, center speed v need not stay fixed when total
kinetic energy stays fixed:

```text
2K = (mass + rotationalInertia / radius^2) * v^2
```

The checked endpoint witness uses mass = inertia = 1, radii 2 and 1, and squared
speeds 1 and 5/8. Both endpoints have the same total kinetic energy. This is an
algebraic witness to the importance of rotational energy, not a proof that a
particular train and transition geometry realize the trajectory.

Assessment: the arithmetic is cheap. A faithful model of a finite train, its
contacts, transition geometry, and the meaning of “speed” is a larger task.
Approving a point-particle model could certify the exact-constancy answer while
discarding the finite-size effect the displayed honest answer leaves room for.
The sources inspected do not specify enough to claim a completed physical audit.

## 3. Wrapping ball: a short route avoids the gravity detour

Here is an independent ideal-model derivation, rather than a translation of every
branch of the adversarial argument. Work on a smooth taut-string interval after
wrapping starts and before contact/singularity. The pole is a stationary circle,
the string is massless and inextensible, and tension is the only force on the ball.

Let u and t be radial and tangent unit vectors at the contact point. Write
q = R*u + s*t and s = L - R*theta. Differentiation gives:

```text
qdot = thetaDot * (R*t - R*t - s*u) = -s*thetaDot*u
force = -T*t
force dot qdot = 0
```

The checked algebraic lemma establishes this last identity given the displayed
velocity expression and radial/tangent orthogonality. The real calculus linking
that expression to q has not been formalized here. With Newton's equation and the
work–energy theorem, zero power yields constant kinetic energy and speed.

A second checked identity gives torque about the pole center as -R*T. Thus zero
power does not imply zero torque. Any angular-momentum argument must identify its
system boundary; conservation for a larger system does not automatically give
conservation for the ball alone.

Assessment: a plausible small real-calculus development, with substantial standard
mathematics available. Mathlib's [mean-value and constant-derivative results](https://leanprover-community.github.io/mathlib4_docs/Mathlib/Analysis/Calculus/MeanValue.html)
support the final constancy step. [Physlib](https://github.com/leanprover-community/physlib)
contains mechanics formalizations, but no claim is made that it already includes
this problem. Full string-contact dynamics and the initial braking transient were
not checked here. “There is no important difference” between gravity and
gravity-free cases needs replacement by an explicit proposition to be assessed.

## What this says about cost and VE

Three different tasks must be kept separate:

1. Checking the short mathematical consequences of a fixed ideal model: demonstrated
   at small scale here.
2. Supplying a complete proof of the intended answer from a reviewed physical model:
   plausible for iceberg and ball, but neither completion time nor cost is measured.
3. Faithfully translating every branch and probabilistic qualification in the
   original debates: not demonstrated and not needed if a fresh short certificate
   can establish the original root claim.

No defensible dollar estimate or full-project person-day estimate follows from
this probe. The strongest next experiment is one completed iceberg formalization,
with independent review of its assumptions and a stated error tolerance, followed
by the wrapping ball. Track model-review time separately from proof-authoring and
checking time. The train should test resistance to approving an oversimplified
model rather than merely act as an easy constant-speed exercise.

The current VE v0 cannot express this arithmetic and calculus directly. The checked
file uses Lean alone. A VE extension or an audited interface to mathematical
definitions is a separate project cost. The original design documents were not
modified by this investigation.
