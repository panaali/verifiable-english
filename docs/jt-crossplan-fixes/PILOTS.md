# Rebuild reading-set IDs after an environment edit

When a pilot changes its profile list or vocabulary, save the edited `.ve.md`
document and rebuild **every** reading set before loading it:

```sh
uv run --frozen python tools/readings_s1_pilot.py \
  --rebuild-reading-ids edited.ve.md --out rebuilt.ve.md
```

The command recomputes candidate meaning IDs, distinguishing model IDs, and
S1 situation IDs from the environment in the edited document. Sets with a
`companion` keep their companion environment's identities. It carries the
source text through unchanged. If a new constant needs an element in a stored
model, add that element to the model first; the command refuses an invalid
model instead of choosing an element.

To check that a document already has current IDs without writing a file:

```sh
uv run --frozen python tools/readings_s1_pilot.py \
  --rebuild-reading-ids rebuilt.ve.md --check-noop
```

The no-op command exits with an error when any stored reading-set ID would
change. `tests/test_readings_s1_pilot_rebuild.py` checks both the no-op case
and an edited environment.
