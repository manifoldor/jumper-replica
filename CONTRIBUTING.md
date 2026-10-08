# Contributing

Keep source identifiers, original local coordinate frames and upstream provenance stable. Derived experiments belong in their specific geometry, assembly or printing directory. Source snapshot changes require explicit source-revision records and regenerated evidence. Avoid deleting faces, filling holes or inventing manufacturing details to make a check pass.

For a physical-fit contribution, record printer/nozzle/material/profile, measurements, photos, local edit dimensions, affected source ID and the actual matching hardware revision. Record geometric, slicing, fit and load validation separately. Do not promote a rendering group to a manufactured part number without physical evidence.

Write project code/docs in English, with a corresponding `*.zh.md` translation where provided. Each translation must track the source file's SHA256. Update both before refreshing release hashes. Configure fonts through the documented environment variables rather than bundling system fonts.

```sh
python3 tools/validate_release.py
# After reviewing intentional asset/doc changes:
python3 tools/refresh_manifest.py
python3 tools/validate_release.py
```

The integrity validator detects stale hashes and broken mappings/links. Geometry changes need the relevant conversion/readback checks as well. Add tests only for a real shared failure mode, with controls that can fail. Maintain a clear current-status document and changelog. New contributions to this project use Apache-2.0; retain applicable upstream/third-party notices.
