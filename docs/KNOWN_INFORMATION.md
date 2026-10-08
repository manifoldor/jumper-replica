# Known information and unresolved work

Current state: 2026-10-08, combining extraction, STEP readback, six reference slices and rendering. Earlier `geometry/validation.json` is the extraction-stage evidence: its `slicing: not_tested` applies to that stage. The current aggregate is `provenance/project_status.json`, supported by `printing/slicing_checks.json`. No physical print occurred.

| Evidence | Confirmed digitally | Still unresolved |
|---|---|---|
| Source model | 41 links, 40 joints, 22 movable joints; two five-joint front manipulators and four three-joint walking legs | Exact hardware revision and zero conventions |
| Extraction | 430,915 triangles; 1,364 edge-connected components; 75 original closed components | Tiny fragments/composites are not physical parts |
| Trial selection | 32 original closed trial candidates | Material and manufacturing suitability unverified |
| Seam recovery | 13 solids closed by vertex merging alone; maximum vertex movement under 0.000018 mm | 26 of the 39 reviewed substantial open components remain open; no holes filled |
| STEP | 46 valid single-solid faceted STEP conversions; maximum bounds error about 1e-7 mm | Native sketches, analytic surfaces, tolerances and manufacturing features not recovered |
| Rim fitting | 741 circular rim observations with coordinates and residuals | Not 741 holes, not thread specifications; observations can be repeated/nested |
| Six fit samples | All slices contain extrusion paths and fit the generic 220 × 220 × 250 mm reference volume, including support/brim | Actual printer, shrinkage, support removal and physical fit |
| Wall sampling | 3,000 area-weighted inward normal rays per sample; shoulder/calf P05 approximately 0.8 mm | Not a global minimum wall-thickness certification or strength test |
| Rendering | 88 objects, 66 annotated groups; all source triangles retained | Illustration grouping is not a manufacturing BOM |

## Discrepancies to preserve

- `RF_J4_joint`: HOME 0.0 rad, URDF lower limit 0.1 rad.
- `LM_J0_joint`: HOME 0.0012 rad, URDF lower limit +0.75 rad; the copied simulation XML uses -0.75 rad. The source limits are not edited.
- Summed URDF mass is 2.542962 kg. Upstream hardware documentation lists 1.8 kg and an engineering prototype of 2.8 kg. These describe differing evidence/revisions; no mass target is assumed.
- Source HOME envelope is approximately 368.536 × 415.265 × 178.371 mm, not maximum swept workspace. Published product dimensions are 400 × 400 × 200 mm.
- 21 repeated cylindrical actuator references were detected, while the mechanism has 22 movable joints. This is a geometry-detection count, not a servo purchase quantity.
- Six forearm/thigh connector assemblies have an anodized-aluminium description in the source conventions. Subpart material cannot be inferred from assembly color. Foot/pad compliance remains unknown.

## Hardware and control boundaries

The upstream specification names RK3576, 4 GB RAM, 64 GB storage, a 25.2 V / 3000 mAh removable Li-ion battery, 22 tactile servos and the listed sensors/displays/audio. Those are product/source descriptions, not a complete purchasing or wiring plan. The camera lists 5 MP alongside an OV16880 reference; board/module identity must be confirmed rather than inferring interchangeable components from the sensor family.

`upstream_snapshot/assets/jumper/motor/motor_config.yaml` leaves vendor, part number and firmware unset. Servo ratio assignments, horn/mounting interfaces, bus topology, connectors and firmware versions need confirmation. The external TS20 CAD is an independent dimensional reference, not a verified replacement for every source actuator.

The original deployment documentation defines DDS interfaces but relies on motor-controller and IMU services outside the reviewed checkout. Real-board NPU execution and the motor-bus control loop were explicitly unvalidated in the reviewed source. This repository does not supply missing low-level drivers, OS images, PCB schematics, power distribution or harness fabrication data.

## Next milestones

1. Bind an actual printer, print foot/shoulder samples and record measured interfaces.
2. Confirm a real actuator revision/horn and build one limb with the required connector process.
3. Resolve open geometry and validate fasteners, travel, support access and loaded interfaces.
4. Establish a measured procurement BOM, electrical architecture and lower-level bus services.
5. Calibrate joint order/zeros, inertia/friction and timing before whole-robot motion evaluation.
