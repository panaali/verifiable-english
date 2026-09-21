# claims.ve statement map

These are the two premises the claim graph found **both sides implicitly
share** (see claim-graph.md, "shared deductive core"). They are not a
formalisation of the whole article; they are the shared skeleton extracted
from the argument structure.

| # | Represents |
|---|---|
| 1 | The Citizenship Clause's own conditional structure ("born ... and subject to the jurisdiction thereof ... are citizens"), read by both Krikorian/Cooper and Mayes/Newman as: born-in-US + subject-to-jurisdiction implies citizen. Neither side disputes this rule; they dispute the extension of `subject_to_jurisdiction`. |
| 2 | The rule both sides accept as the settled holding of *United States v. Wong Kim Ark* (1898): a child with a non-citizen parent permanently domiciled in the U.S. (but ineligible for naturalization) is subject to the jurisdiction of the United States. Mayes cites this case as "settled law for 127 years"; Cooper's rebuttal targets its *scope* (see claim-graph.md, Claim F2), not this narrow holding itself. |

Everything else in the debate — the contested extension of `subject_to_jurisdiction`
for undocumented/temporary-visitor parents, the historical-intent dispute, the
scale/incentive argument, the administrability argument, and the moral/values
claims — is **not** put into this checked document; see claim-graph.md for why
(most of it is not first-order-formalisable content at all: empirical
predictions, historical-authority weighing, and values). The rival,
mutually-contradictory extension premises that each side would need to add to
reach their conclusion are kept as separate files in `countermodel/`, precisely
because they cannot jointly hold in one non-vacuous checked document without
begging the question against one side.
