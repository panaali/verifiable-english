| Identifier | Ordered signature | Description | Wording |
|---|---|---|---|
| `person` | Sort | A recorded person. | `person` |
| `service` | Sort | A service recorded in the inventory. | `service` |
| `deployed` | `service` | Recorded as deployed. | `{0} is deployed` |
| `owns` | `person`, `service` | Recorded ownership; person first, service second. | `{0} owns {1}` |

No constants are declared. No lint diagnostic is reported. The stored legend also records the optional negative template for `owns`, absent negative wording for `deployed`, raw declarations, and the naming rules.

<!-- src: paper/generated/worked-example.json, generated from paper/sources/worked-example.env.json. -->
