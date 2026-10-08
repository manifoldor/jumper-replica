## Change and reason

Explain the problem and resulting behavior. List affected source/component IDs when relevant.

## Evidence

State what was checked and what remains unverified. For physical-fit changes, include printer/profile, measurements, matching hardware revision and photos.

- [ ] Preserve source IDs, scale, coordinate frames and upstream attribution.
- [ ] Update matching Chinese translations and source SHA256 headers where provided.
- [ ] Review intentional changes, refresh the artifact manifest, and run `python3 tools/validate_release.py`.
- [ ] Keep raw G-code, logs, private paths, vendor binaries and credentials out of the commit.

Do not describe mesh closure or slicing success as physical acceptance. See [contributing](../CONTRIBUTING.md).
