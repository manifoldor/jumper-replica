# Assembly and exploded rendering

[Poster](Jumper_Exploded_Annotated.png) · [editable SVG](Jumper_Exploded_Annotated.svg) · [Blender scene](Jumper_Exploded.blend) · [labels](LABELS.md)

The poster is 6000 × 4800 with 66 callouts, three detailed inspection panels and an assembled HOME reference. The scene has 88 mesh objects and exactly 430,915 faces, including duplicate source faces. This is an assembly illustration rather than validated manufacturing instructions.

`scene_manifest.json` records original HOME matrices and every explosion translation. `scene_meshes/` are exploded millimeter STL. Blender scales each object by 0.001 to meters. Only translations are added for explosion; upper shell/display lateral offsets expose the rear structure, and gripper accessories are spread vertically for readability. Distances are illustrative, not assembly tolerances.

`annotation_layout.json` maps all 66 unique labels to source IDs and screen positions. Geometry/render/Blender-readback reports document their checks. Source actuator references are retained; external servo CAD is not substituted. Red/silver/dark materials are render styling, not physical material specifications.

The original assembled reference is `../geometry/assembly_home.glb` (meters) or `../geometry/assembly_home_mm.stl` (millimeters). See [assembly guide](../docs/ASSEMBLY.md) for joint and coordinate conventions.
