# arch-20261109-2 follow-ups

- **arch-layer-legacy-move** (backlog row, post-sprint): move the hand-listed layer exceptions into their modules'
  own first-line declarations (`-- ve-layer: <n> (<reason>)`, `# ve-layer: <n> (<reason>)`) and delete them from
  `tools/layer_policy.py`. Names that would move, counted on this batch's tree: 84 Lean modules that
  `lean_name_layer` names one by one (83 in its set literals, 1 `==` rule; `layer_policy.lean_named()`) and the 97
  names of the `PYTHON` table, 181 in all. The role rules (aggregation targets, entry points, `*.Run`,
  `VE.Route.MeteredRun`, `VE.Service.*`, `ResponseShape*`; `lean_fixed`) and the prefix rules stay in the policy.
  The move must keep `docs/ARCHITECTURE-LAYERS.md`'s table test (`test_documented_python_layers_match_policy`) in
  step: once a Python name moves, that table lists the declared rows too, or the test reads them through
  `layer_policy.python_declarations`.
- **The second conflict cause, not touched here** (PIPELINE-LIMITS L185): whole-file decoder pins of
  `lean/VE/Service/Document.lean` in `ve/assurance-manifest.json`, 4 of the 13 agent syncs since Nov 5.
