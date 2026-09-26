# Gatekeeper image exemption fragment

The `is_exempt` helper checks image names against complete, recomputed glob
tables. This request lists the exact images whose matches may be cited. An
unlisted image is rejected; a missing table produces UNKNOWN.

```sh
uv run python -m ve adapter run usecases/gatekeeper-exemption/request.json
```

Save the result as a record and run `uv run python -m ve adapter run --verify
RECORD.json` before citing the labelled adapter premise. This example covers
the string exemption operation, not the full Gatekeeper policy template.
