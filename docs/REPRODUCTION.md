# Independent reproduction

The bundled selected snapshot is sufficient for these geometry scripts. They do not import the training package or depend on the original checkout's location. Python 3.12 with `requirements-geometry.txt` matches the analysis environment. The offline release validator requires only Python's standard library.

```sh
python3 tools/validate_release.py
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-geometry.txt
.venv/bin/python tools/reverse_engineer_jumper.py
.venv/bin/python tools/recover_mesh_seams.py
.venv/bin/python tools/reverse_engineer_step.py
.venv/bin/python tools/reverse_engineer_step.py --seams-only
.venv/bin/python tools/render_reverse_geometry.py
```

The validator leaves reference assets unchanged and writes a validation report. Regeneration commands write their named output directories and replace derived artifacts. Use a copy or Git branch for experiments. `JUMPER_GEOMETRY_DIR=/tmp/jumper-probe` isolates the extraction script's output for comparing it to the included immutable snapshot. STEP readback requires OpenCascade, already pinned in the optional requirements.

## Pilot preparation and slicing

```sh
.venv/bin/python tools/prepare_pilot_prints.py
.venv/bin/python tools/slice_pilot_reference.py /path/to/PrusaSlicer
.venv/bin/python tools/embed_pilot_configs.py
.venv/bin/python tools/validate_pilot_projects.py
.venv/bin/python tools/inspect_pilot_toolpaths.py
.venv/bin/python tools/render_pilot_prints.py
```

Reference slicer version: PrusaSlicer 2.9.6. The script accepts the executable path rather than installing or bundling a slicer. It writes editable projects under `printing/slicer/` and inspection-only G-code under `experiments/reference_gcode/`. Raw G-code and execution logs are local outputs ignored by Git and release manifests. The public package retains slicing evidence and digests. The standard profile is generic, with intentionally unspecified machine start/end code.

## Exploded scene and annotation

```sh
.venv/bin/python tools/prepare_exploded_scene.py
/path/to/Blender --background --factory-startup --python tools/render_exploded_blender.py
.venv/bin/python tools/compose_exploded_poster.py
```

Reference renderer: Blender 4.5.9 LTS / Cycles / 48 samples, tested with Apple M4 Metal GPU. CPU fallback is available; exact pixels are not promised across render backends. `-- --draft` selects the short draft render. `.blend` output stores a relative render path; no external textures are required.

The compositor uses the bilingual Markdown catalogs and macOS fonts by default. On other platforms set `JUMPER_CJK_FONT`, `JUMPER_SANS_FONT`, and `JUMPER_MONO_FONT` to fonts you are permitted to use; font files are not redistributed. For a writable plotting cache, set `MPLCONFIGDIR` and `XDG_CACHE_HOME` if required by the environment.

Upstream snapshot files must never be silently edited. Changing source revision requires updating source hashes, geometry evidence, catalogs and documentation together. Regenerated files invalidate the existing artifact manifest; run `tools/refresh_manifest.py` after reviewing changes, then run `tools/validate_release.py` again. A passed manifest check is not a substitute for geometric/physical validation.
