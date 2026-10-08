# Local reference toolpaths

Raw G-code and execution logs are not distributed. `tools/slice_pilot_reference.py` regenerates inspection-only paths here; Git and release manifests ignore them. Public slicing counts, estimates and G-code SHA256 digests are in `printing/slicing_checks.json`. Toolpath geometry summaries remain under `printing/`.

Reference outputs use a generic profile and are not bound to an actual printer. Configure the real printer, firmware, filament and start/end routines, then re-slice before printing.
