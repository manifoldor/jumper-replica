# Geometry inventory

All derived STL/STEP here use millimeters; `assembly_home.glb` uses meters. Original upstream meshes remain meter-scale in `../upstream_snapshot/`. Component coordinates are the source link's coordinates, not bed placement.

- `links_mm/`: 41 full visual links; many contain composite assemblies.
- `components_mm/`: 1,364 edge-connected source mesh components, with face counts preserved. Many are small details; no manufacturing count follows from this number.
- `seam_recovered_mm/`: 13 closed solids from vertex merging only; no face filling/deletion.
- `step_trials/`: 46 valid AP214 faceted B-reps (33 original candidates/reviewed plate + 13 recovered solids). Valid conversion is not manufacturing approval.
- `pilot_fit_set/`: six selected originals for the first fit experiments.
- `parts_manifest.csv`: source hashes, dimensions, masses and HOME world matrices.
- `components_manifest.csv`: component roles/states, bounds, source-local file paths and hashes.
- `trial_candidates.csv`: 32 closed source candidates; their canonical files are under `components_mm/`.
- `joint_schedule.csv`: all 40 source joints, HOME values, axes and limits.
- `circular_rim_reference.csv`: 741 observed circular rims, not unique holes or threads.
- `upper_shell_mounting_reference.json`: source-local mounting observations, including the approximately 70 × 135 mm main pattern.

Original visual extraction, vertex-only seam recovery and STEP conversion reports are retained separately. The extraction report's unsliced state is historical; six later reference slices are documented under `../printing/`. Still-open major source geometry remains visibly identified in `../catalog/annotated_groups.json`.

The full-link and full-assembly STL are inspection references. Print individual selected components after checking material/process and the actual machine; printing a composite link can enclose a servo reference or unrelated internals.
