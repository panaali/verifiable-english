# Directed fixed-rule coverage

The 45 rules absent from the generated G3 stream are each reached by a fresh text. Every row was compared through the Python reader and Lean `english.read`; all verdicts and formulas agree.

| Fixed rule | Environment | Compared text |
|---|---|---|
| `coordination.predicate-and` | `directed-coverage` | Alpha is deployed, reviewed and active. |
| `coordination.predicate-or` | `directed-coverage` | Alpha is deployed, reviewed or active. |
| `coordination.subject-and` | `directed-coverage` | Alpha, beta and gamma are deployed. |
| `coordination.subject-or` | `directed-coverage` | Alpha, beta or gamma is deployed. |
| `declaration.eighth` | `directed-coverage` | For every service, for every second service, for every third service, for every fourth service, for every fifth service, for every sixth service, for every seventh service, for every eighth service, the eighth service is deployed. |
| `declaration.fifth` | `directed-coverage` | For every service, for every second service, for every third service, for every fourth service, for every fifth service, the fifth service is deployed. |
| `declaration.fourth` | `directed-coverage` | For every service, for every second service, for every third service, for every fourth service, the fourth service is deployed. |
| `declaration.seventh` | `directed-coverage` | For every service, for every second service, for every third service, for every fourth service, for every fifth service, for every sixth service, for every seventh service, the seventh service is deployed. |
| `declaration.sixth` | `directed-coverage` | For every service, for every second service, for every third service, for every fourth service, for every fifth service, for every sixth service, the sixth service is deployed. |
| `declaration.third` | `directed-coverage` | For every service, for every second service, for every third service, the third service is deployed. |
| `formula.coordination` | `directed-coverage` | Alpha, beta and gamma are deployed. |
| `formula.natural` | `directed-coverage` | Some service is deployed. |
| `guard-rel.that` | `directed-coverage` | For every service that is deployed and that is reviewed, that service is active. |
| `guard-rel.who` | `directed-coverage` | For every service that is deployed and who is reviewed, that service is active. |
| `listing.all.words` | `directed-coverage` | All of the following hold: first clause: alpha is deployed; end first clause; second clause: beta is reviewed; end second clause. |
| `listing.any.words` | `directed-coverage` | At least one of the following holds: first clause: alpha is deployed; end first clause; second clause: beta is reviewed; end second clause. |
| `listing.both.words` | `directed-coverage` | Both of the following hold: first clause: alpha is deployed; end first clause; second clause: beta is reviewed; end second clause. |
| `listing.if.markers` | `directed-coverage` | If the following holds: (a) alpha is deployed; then the following holds: (b) beta is reviewed. |
| `listing.if.words` | `directed-coverage` | If the following holds: first clause: alpha is deployed; end first clause; second clause: beta is reviewed; end second clause. |
| `marker.hence` | `directed-coverage` | Legacy is deployed. Hence legacy is deployed. |
| `marker.it-follows-that` | `directed-coverage` | Legacy is deployed. It follows that legacy is deployed. |
| `marker.so` | `directed-coverage` | Legacy is deployed. So legacy is deployed. |
| `marker.therefore` | `directed-coverage` | Legacy is deployed. Therefore legacy is deployed. |
| `natural-every.owner` | `directed-coverage` | Every service has an owner. |
| `natural-every.subject` | `directed-coverage` | Every deployed service is reviewed. |
| `natural-no` | `directed-coverage` | No service is deployed. |
| `natural-some` | `directed-coverage` | Some service is deployed. |
| `natural-tail.both` | `directed-coverage` | Every deployed service is reviewed and has an owner. |
| `natural-tail.owner` | `directed-coverage` | Every deployed service has an owner. |
| `natural-tail.relative` | `directed-coverage` | Every deployed service is reviewed. |
| `natural.every` | `directed-coverage` | Every deployed service is reviewed. |
| `natural.no` | `directed-coverage` | No service is deployed. |
| `natural.some` | `directed-coverage` | Some service is deployed. |
| `reach.body.listed` | `closure` | Starting from legacy, legacy is reachable by one or more steps, where a step from a service to a second service satisfies the following: (a) that service is deployed. |
| `sentence.marked` | `directed-coverage` | Legacy is deployed. Therefore legacy is deployed. |
| `some-tail.copula` | `directed-coverage` | Some service is deployed and reviewed. |
| `some-tail.relative` | `directed-coverage` | Some service is deployed. |
| `some-tail.two` | `directed-coverage` | Some service is deployed and is reviewed. |
| `term.it` | `directed-coverage` | Legacy is deployed. It is reviewed. |
| `term.the-eighth` | `directed-coverage` | For every service, for every second service, for every third service, for every fourth service, for every fifth service, for every sixth service, for every seventh service, for every eighth service, the eighth service is deployed. |
| `term.the-fifth` | `directed-coverage` | For every service, for every second service, for every third service, for every fourth service, for every fifth service, the fifth service is deployed. |
| `term.the-fourth` | `directed-coverage` | For every service, for every second service, for every third service, for every fourth service, the fourth service is deployed. |
| `term.the-seventh` | `directed-coverage` | For every service, for every second service, for every third service, for every fourth service, for every fifth service, for every sixth service, for every seventh service, the seventh service is deployed. |
| `term.the-sixth` | `directed-coverage` | For every service, for every second service, for every third service, for every fourth service, for every fifth service, for every sixth service, the sixth service is deployed. |
| `term.the-third` | `directed-coverage` | For every service, for every second service, for every third service, the third service is deployed. |

The complete verdicts, formulas and derivation tags are in `coverage-directed.json`.
