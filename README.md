# Jumper Replica

[![Integrity checks](https://github.com/manifoldor/jumper-replica/actions/workflows/validate.yml/badge.svg)](https://github.com/manifoldor/jumper-replica/actions/workflows/validate.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)

**English** | [简体中文](README.zh.md)

An independent geometry-recovery and physical-fit reference project for [KingKong Robotics Jumper](https://github.com/KingKongRobotics/jumper), pinned to `61d065219fca767f3142c8f10aff59eae5a5a004`. Current stage: **digital geometry and reference slicing complete; no physical replica built or validated**. Updated 2026-10-08 (Asia/Shanghai).

![Annotated exploded view](assembly/Jumper_Exploded_Preview.png)

## What is ready

- Original-coordinate millimeter geometry: 41 link references, 1,364 connected mesh components, and 13 solids closed by vertex-only seam welding.
- 46 independently validated **faceted** STEP files. These retain triangulated faces rather than original parametric CAD.
- Six pilot fit components with oriented STL, configured 3MF, reference PLA settings and measurement checklists.
- Source HOME assembly GLB/STL, joint schedule, mounting/rim observations, and a 6000 × 4800 annotated exploded poster with 66 callouts and an editable Blender scene.
- A pinned upstream source snapshot, provenance/hashes, reusable scripts and offline integrity validation. The project can be moved away from the original checkout.

Counts describe model representations and rendering groups, not a confirmed manufacturing BOM. The 66 annotations include three module references and an unidentified internal group. Even the remaining 62 groups are not a verified quantity of independent manufactured parts. Geometry closure and successful slicing do not prove physical fit or strength.

## Get the project

```sh
git clone https://github.com/manifoldor/jumper-replica.git
cd jumper-replica
python3 tools/validate_release.py
```

Use GitHub **Code → Download ZIP** for a source archive, or clone to retain revision history. Binary reference geometry is stored directly in Git; Git LFS is not required. For measurements and questions use [support](SUPPORT.md) or [issue templates](https://github.com/manifoldor/jumper-replica/issues/new/choose).

## Start here

| Goal | File / guide |
|---|---|
| See the full structure | [High-resolution poster](assembly/Jumper_Exploded_Annotated.png), [editable SVG](assembly/Jumper_Exploded_Annotated.svg), [Blender scene](assembly/Jumper_Exploded.blend) |
| Understand the latest verified state | [Known information and gaps](docs/KNOWN_INFORMATION.md), [machine-readable status](provenance/project_status.json) |
| Find original-coordinate parts | [Geometry guide](geometry/README.md), [component manifest](geometry/components_manifest.csv), [STEP files](geometry/step_trials/) |
| Understand annotation/source mappings | [Annotation catalog](assembly/LABELS.md), [group catalog](catalog/annotated_groups.json) |
| Print the first fit samples | [Printing guide](printing/README.md), [physical fit checklist](printing/FIT_CHECKLIST.md) |
| Understand source assembly | [Assembly guide](docs/ASSEMBLY.md), [joint schedule](geometry/joint_schedule.csv) |
| Reproduce or verify | [Reproduction](docs/REPRODUCTION.md), [contribution workflow](CONTRIBUTING.md) |
| Review publication scope | [Licensing and provenance](docs/LICENSING.md), [release checklist](docs/RELEASE_CHECKLIST.md) |

```sh
python3 tools/validate_release.py
```

The validator uses the Python standard library; no robot, simulator, slicer, GPU, CAD application or network is required. Install the optional geometry dependencies only when regenerating or deeply inspecting meshes:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements-geometry.txt
```

## Directory map

`upstream_snapshot/`: selected unmodified source files, original meter-scale STL and source provenance. `geometry/`: derived mm geometry and extraction evidence. `assembly/`: original HOME assembly references, exploded render scene and annotations. `printing/`: six fit samples, profiles and slicing evidence. `experiments/reference_gcode/`: guidance for locally generated toolpaths; raw G-code is excluded from publication. `catalog/`: component-group status, not a procurement BOM. `external_references/`: vendor links and measurements, without vendor CAD binaries. `tools/`: independent regeneration/validation scripts. `docs/`: engineering state and workflows. `provenance/`: hashes and source/change records.

The snapshot contains **51 selected files**, not the full training/controller repository. No original firmware, custom PCB, wire harness, complete fastener list, material/tolerance specification or validated whole-robot assembly is supplied here. This project does not claim the vendor's grasp/jump performance.

## License

[Apache-2.0](LICENSE) is explicitly selected for this project's new scripts, documentation, annotations and renders. Derived source geometry retains the upstream attribution in [NOTICE](NOTICE). Upstream materials and external references are distinguished in [licensing details](docs/LICENSING.md). No vendor endorsement is implied. The manufacturer servo STEP is not redistributed because its redistribution terms were not established.
