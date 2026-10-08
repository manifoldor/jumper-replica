# Assembly reference and fit sequence

Source link names are authoritative. LF/RF are left/right front; LM/RM left/right middle; LR/RR left/right rear. Left/right refer to the robot. Front chains use J0–J4; walking legs use J0–J2. Matching index numbers do not establish matching axis signs or zero offsets.

For component-local homogeneous coordinates `p_mm`, use the row's `home_world_matrix_mm` in `geometry/parts_manifest.csv`: `p_world_mm = H_home @ p_mm`. The exploded presentation adds `explosion_translation_mm` from `assembly/scene_manifest.json`. Do not use the exploded offsets as physical mating transforms. The saved original HOME assembly retains source placement and the unresolved limit discrepancies.

## Digital structure

- Body: lower shell/perimeter frame, internal mounting plate, internal cradle, upper shell and unidentified remaining internals. Display/camera/ToF are module references.
- LF/RF: shoulder, upper arm, forearm, palm and moving finger; pads and grip inserts retain their source f/b suffixes without inventing orientation meanings.
- LM/RM/LR/RR: hip, thigh, calf and foot-tip pad.
- A/B callouts distinguish separated components. They do not automatically imply inner/outer or left/right halves.

The source triangles are sufficient to visualize the chain and measured envelopes. They do not supply all screws, bearings, actuator horns, connector pinouts, cable routing or assembly torque values.

## First physical-fit sequence

Start with the foot-tip sample, then both LF shoulder halves. Record dimensions, support-removal damage, seam closure, post alignment and the clearance to a confirmed real servo/horn. After those pass, test both LM calf halves and the end interfaces. Print the large upper shell last; inspect warping, rib/post integrity and the observed main mounting pattern.

Use `printing/FIT_CHECKLIST.md`; retain measurement photos and measured local corrections. Do not fill functional openings or globally scale the robot to match one tight fit. Select the real material/process for connector loads and compliant pads. Only after measured fits should a single limb undergo travel and load checks; no such checks have yet occurred.
