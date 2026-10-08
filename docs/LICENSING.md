# Licensing and source provenance

The top-level Apache-2.0 license is explicitly selected for new Jumper Replica scripts, documentation, annotations and render outputs. This is a project license decision, not an assumption that generated outputs automatically inherit an upstream license.

The selected upstream repository states Apache-2.0 for maintainer-owned materials and preserves third-party terms. Unmodified selected files retain their exact hashes and notices in `upstream_snapshot/`; every source entry is linked to its pinned commit in `upstream_snapshot/source_manifest.json`. No separate license override was found in the selected robot mesh/URDF snapshot. Derived geometry retains the applicable repository attribution and a prominent modification record in `NOTICE` and `provenance/artifact_manifest.json`.

Change operations include connected-component extraction, meters-to-millimeters conversion, vertex-only welding, faceted STEP conversion, rigid print orientations, explosion translations and annotated rendering. This is not original manufacturer CAD. The complete upstream NOTICE is archived as a source record; training dependency notices do not imply those libraries are included here.

The manufacturer's TS20 STEP was downloaded for a separate dimensional investigation. Its redistribution terms were not established. The public preparation excludes that binary and retains only `external_references/TS20-50-TS20-100.json`: URL, checksum and measured bounds. No vendor CAD is substituted into this project's scene. The separate jumper-design LFS CAD archive was not fetched and is not redistributed.

Blender, PrusaSlicer, Python packages, system fonts, firmware images and third-party binaries are not bundled. Dependency version declarations link users to their own installations; each dependency retains its license. Generated images contain rendered text, not font files. No manufacturer endorsement, trademark permission, original manufacturing approval or hardware certification is asserted.
