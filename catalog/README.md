# Annotation catalog, not a manufacturing BOM

`annotated_groups.json` describes 66 numbered render/annotation groups and links them to canonical source-local geometry. Each entry records geometric state separately from material, process, tolerance and physical-fit status. Manufacturing fields remain unverified.

For C001/C002 component IDs, `geometry_path` selects the original component or the recovered seam solid when available. Whole-link references can still contain several components. `base_link__remaining` is unidentified internal geometry, not a named electronics bill of materials. `assembly/LABELS.md` and its Chinese translation supply the names shown on the poster.

A future manufacturing BOM must identify independent physical part numbers, quantities, material/process, fasteners and revision-compatible purchased items. Do not turn the component, STEP, annotation or detected-cylinder counts into procurement quantities.
