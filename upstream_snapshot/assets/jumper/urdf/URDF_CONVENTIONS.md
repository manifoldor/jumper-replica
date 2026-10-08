# Jumper URDF conventions

These conventions record the decisions accepted for this robot. Apply them to future exports and edits in this directory. The latest explicit user request takes precedence. Historical primitive, convex-decomposition and decimation experiments are not the default specification.

## 1. Canonical deliverable

The reference model is jumper/urdf/jumper.urdf relative to this document.

    urdf/
      AGENTS.md
      URDF_CONVENTIONS.md
      jumper/
        urdf/
          jumper.urdf
        meshes/
          visual/
            base_link.stl
            LF_shoulder_link.stl
            ...
      jumper.zip                 # optional distributable archive

Robot identifier and release folder: jumper. Product display name: Jumper. Do not use crab as the robot/product identifier. Deliver the complete robot, not an isolated shell or link, unless that is the requested task.

Keep the package small. Do not add audit reports, generation scripts, test outputs, duplicate meshes, ROS scaffolding or experimental variants to the distributable unless required by the requested workflow. Do not add release.json.

## 2. English names and stable identifiers

Use English ASCII filenames and identifiers: no Chinese names, pinyin or transliterations such as shexiangtou/shangke. Preserve these case-sensitive position prefixes:

| Prefix | Position |
|---|---|
| LF | Left front |
| RF | Right front |
| LM | Left middle |
| RM | Right middle |
| LR | Left rear |
| RR | Right rear |

Left/right refer to the robot, not the viewer. Retain LF/RF rather than silently changing to FL/FR. After the prefix, use lowercase English words separated by underscores for semantic names; movable joints use uppercase J followed by a zero-based index.

- Links end in _link; joints end in _joint.
- Visual mesh filenames match their link names, including case: LF_forearm_link.stl.
- Body links: base_link, upper_shell_link, display_module_link, camera_link, tof_sensor_link.
- Front-limb terminology: shoulder, upper_arm, forearm, palm, finger.
- Walking-leg terminology: hip, thigh, calf, foot. The current separate foot-tip pads retain foot_tip_link and fixed foot_tip_joint; use foot_link for a complete foot assembly in future designs.
- Preserve existing accessory identifiers: palm_pad_f, palm_pad_b, finger_tip, finger_grip_insert, palm_grip_insert. Do not silently expand or reinterpret their suffixes.
- Movable joints use <PREFIX>_J<index>_joint, starting at J0 independently for each limb and proceeding from the body toward the end effector. Example: LF_J1_joint drives LF_upper_arm_link.
- LF/RF use J0 through J4; LM/RM/LR/RR use J0 through J2. Fixed joints retain semantic names and do not consume an index. Links and mesh filenames retain semantic part names.
- Numbering is stable and does not depend on XML order. Matching indices in corresponding left/right limbs do not imply equal axis directions or angle signs.

| Index | LF / RF function | LM / RM / LR / RR function |
|---|---|---|
| J0 | Shoulder yaw | Hip yaw |
| J1 | Shoulder pitch | Hip flexion, driving thigh |
| J2 | Elbow | Knee flexion, driving calf |
| J3 | Wrist | Not present |
| J4 | Gripper opening/closing, driving finger | Not present |

- Preserve existing names and control ordering when re-exporting the same mechanism. New mechanisms may add meaningful names; do not rename established identifiers for cosmetic consistency.

The exact current joint-to-link mapping is recorded below. It overrides guessed names.

## 3. Revision metadata

Keep revision information only in an XML comment immediately after the declaration in jumper.urdf. Carry forward the existing values unless a revision change is requested or justified by the actual new design.

    <?xml version='1.0' encoding='utf-8'?>
    <!--
      model_revision: MODEL_REVISION
      ros_package_version: PACKAGE_VERSION
      Revision metadata only; robot names and mesh paths remain version-independent.
    -->
    <robot name="jumper">

Do not insert revision numbers, dates or suffixes such as v2 into the package folder, archive name, URDF filename, robot identifier, link/joint identifiers or mesh paths. Do not use nonstandard robot attributes to store versions. The package-version comment alone does not create a ROS package.

## 4. Mesh paths and collision policy

The current accepted package uses the ORIGINAL visual STL for both visual and collision geometry. Each current link has one visual and one collision element sharing the same mesh filename, origin and scale.

    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <mesh filename="../meshes/visual/LF_palm_link.stl"/>
      </geometry>
    </visual>
    <collision name="LF_palm_link_collision">
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <mesh filename="../meshes/visual/LF_palm_link.stl"/>
      </geometry>
    </collision>

This example uses identity origin; preserve the actual visual transform for each link, including nonidentity origins and scale when present.

Do not automatically replace collisions with primitives, decimated meshes or convex decomposition. Do not recreate a separate meshes/collision directory or impose the abandoned five-primitives/500-face trial budgets. Geometry redesign requires an actual task requesting it.

Use portable paths relative to the URDF location. No machine-specific absolute paths or broken package:// references in the standalone package. Preserve STL coordinates and units; STL itself does not declare units. Do not double-apply millimetre-to-metre conversion.

A mesh reference does not guarantee concave triangle-by-triangle collision. In MuJoCo, ordinary mesh colliders are treated as convex hulls; openings may be filled. Preserve this known behavior in documentation and do not claim precise concave contact or resolve it silently.

## 5. Geometry and physical properties

Use metres, kilograms, radians and kg*m^2. Preserve actual CAD/link frames, joint origins, axes, signs, limits and inertial origins. Establish directions from model data; do not infer a local axis from a screenshot or replace it using PCA.

Naming, packaging and appearance-only edits must not alter physical parameters. Current reference values:

| Quantity | Current value |
|---|---:|
| Base mass | 0.886006064277726 kg |
| Display module mass | 0.0228872961815731 kg |
| Total modeled mass | 2.5429618067892991 kg |
| Links / joints / movable joints | 41 / 40 / 22 |

These are this model's baseline, not mandatory values for a genuinely changed robot. Do not switch back to the abandoned 1.209 kg base value. Do not recompute mass or inertia from simplified collision geometry without an explicit modeling task. Distinguish estimated properties from measured or CAD-derived properties.

Retain the current MuJoCo compiler settings: balanceinertia=false, discardvisual=false, strippath=false. Do not silently repair or rebalance invalid inertias; diagnose their source. A future intentionally different export target may need different compatibility settings, which must be stated.

## 6. Appearance

| Parts | RGBA |
|---|---|
| Base/lower shell, display, camera, ToF housing | 0 0 0 1 |
| Red upper shell and red limb covers | 0.85 0.08 0.05 1 |
| LF/RF forearm and LM/RM/LR/RR thigh connectors | 0.68 0.70 0.72 1 |
| Existing pads, grip inserts and tips | 0.816 0.820 0.804 1 |

The six connectors represent natural anodized aluminium using a simple silver color; this is not a calibrated physically based material. Preserve per-link colors unless appearance changes are requested.

## 7. Optional camera and motor configuration

If camera/ or motor/ files are supplied, preserve them as supporting configuration. YAML files are not automatically consumed by URDF. Identify the loader/controller/plugin before claiming they affect simulation.

Update configuration link references when naming changes: camera_link is canonical, not shexiangtou_link. Preserve units and explicit uncalibrated/unknown/null fields. Do not treat a header-only measurement CSV as real samples or blindly apply motor data to fixed joints. Match actuator assignments to the actual movable joints. Do not add a runtime or sensor plugin solely because configuration files exist.

## 8. Generation and verification workflow

1. Read this document and the current reference URDF before generating.
2. Preserve unrelated user changes. Experiments use an independent directory; never replace the reference with an unaccepted trial.
3. Validate XML, unique names, connected parent/child links, resource paths and joint ordering. Compare unchanged physical properties against the starting model.
4. For the current shared-STL policy, verify visual/collision paths, origins and scales match. Check exported mesh payloads if a task should preserve geometry.
5. Verify a representative loader can open the packaged model. Geometry or frame edits also need relevant visual and contact checks; a comment-only edit needs XML/semantic verification, not a dynamics test.
6. Treat raw zero pose carefully: it is outside some current joint limits. Use named, reproducible poses when comparing contact behavior.
7. Report exactly what was checked. Successful loading is not collision equivalence, dynamics validation, sensor calibration or physical-fit certification.
8. Keep reports and temporary tools outside the distributable. When packaging is requested, export jumper.zip and verify archive contents and relative references.

Use focused reads and concise reports. Reuse valid checks. Delegate suitable independent work to a lighter model when it saves cost; do not multiply agents for trivial edits.

## 9. Current joint-to-link mapping

Root link: base_link. Rows are in current URDF joint order.

| Joint | Type | Parent link | Child link |
|---|---|---|---|
| upper_shell_joint | fixed | base_link | upper_shell_link |
| display_module_joint | fixed | base_link | display_module_link |
| tof_sensor_joint | fixed | base_link | tof_sensor_link |
| camera_joint | fixed | base_link | camera_link |
| LF_J0_joint | revolute | base_link | LF_shoulder_link |
| LF_J1_joint | revolute | LF_shoulder_link | LF_upper_arm_link |
| LF_J2_joint | revolute | LF_upper_arm_link | LF_forearm_link |
| LF_J3_joint | revolute | LF_forearm_link | LF_palm_link |
| LF_palm_pad_f_joint | fixed | LF_palm_link | LF_palm_pad_f_link |
| LF_palm_pad_b_joint | fixed | LF_palm_link | LF_palm_pad_b_link |
| LF_J4_joint | revolute | LF_palm_link | LF_finger_link |
| LF_finger_tip_joint | fixed | LF_finger_link | LF_finger_tip_link |
| LF_finger_grip_insert_joint | fixed | LF_finger_link | LF_finger_grip_insert_link |
| LF_palm_grip_insert_joint | fixed | LF_palm_link | LF_palm_grip_insert_link |
| RF_J0_joint | revolute | base_link | RF_shoulder_link |
| RF_J1_joint | revolute | RF_shoulder_link | RF_upper_arm_link |
| RF_J2_joint | revolute | RF_upper_arm_link | RF_forearm_link |
| RF_J3_joint | revolute | RF_forearm_link | RF_palm_link |
| RF_palm_pad_f_joint | fixed | RF_palm_link | RF_palm_pad_f_link |
| RF_palm_pad_b_joint | fixed | RF_palm_link | RF_palm_pad_b_link |
| RF_palm_grip_insert_joint | fixed | RF_palm_link | RF_palm_grip_insert_link |
| RF_J4_joint | revolute | RF_palm_link | RF_finger_link |
| RF_finger_grip_insert_joint | fixed | RF_finger_link | RF_finger_grip_insert_link |
| RF_finger_tip_joint | fixed | RF_finger_link | RF_finger_tip_link |
| LM_J0_joint | revolute | base_link | LM_hip_link |
| LM_J1_joint | revolute | LM_hip_link | LM_thigh_link |
| LM_J2_joint | revolute | LM_thigh_link | LM_calf_link |
| LM_foot_tip_joint | fixed | LM_calf_link | LM_foot_tip_link |
| RM_J0_joint | revolute | base_link | RM_hip_link |
| RM_J1_joint | revolute | RM_hip_link | RM_thigh_link |
| RM_J2_joint | revolute | RM_thigh_link | RM_calf_link |
| RM_foot_tip_joint | fixed | RM_calf_link | RM_foot_tip_link |
| LR_J0_joint | revolute | base_link | LR_hip_link |
| LR_J1_joint | revolute | LR_hip_link | LR_thigh_link |
| LR_J2_joint | revolute | LR_thigh_link | LR_calf_link |
| LR_foot_tip_joint | fixed | LR_calf_link | LR_foot_tip_link |
| RR_J0_joint | revolute | base_link | RR_hip_link |
| RR_J1_joint | revolute | RR_hip_link | RR_thigh_link |
| RR_J2_joint | revolute | RR_thigh_link | RR_calf_link |
| RR_foot_tip_joint | fixed | RR_calf_link | RR_foot_tip_link |

## 10. Current movable-joint order

This is the current URDF declaration order. Downstream controllers must bind names explicitly or verify that their expected ordering matches.

1. LF_J0_joint
2. LF_J1_joint
3. LF_J2_joint
4. LF_J3_joint
5. LF_J4_joint
6. RF_J0_joint
7. RF_J1_joint
8. RF_J2_joint
9. RF_J3_joint
10. RF_J4_joint
11. LM_J0_joint
12. LM_J1_joint
13. LM_J2_joint
14. RM_J0_joint
15. RM_J1_joint
16. RM_J2_joint
17. LR_J0_joint
18. LR_J1_joint
19. LR_J2_joint
20. RR_J0_joint
21. RR_J1_joint
22. RR_J2_joint
