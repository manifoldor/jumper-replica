# SPDX-License-Identifier: Apache-2.0
# Adapted for the independent Jumper Replica directory and pinned upstream snapshot.
"""Convert closed trial geometry to STEP; reject invalid B-reps after readback."""
from pathlib import Path
import csv
import gc
import hashlib
import json
import sys

import numpy as np
import trimesh
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepGProp import BRepGProp
from OCP.BRepBndLib import BRepBndLib
from OCP.GProp import GProp_GProps
from OCP.Bnd import Bnd_Box
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_SOLID

from jumper_faceted_step import FacetedWriter

OUT = Path(__file__).resolve().parents[1] / "geometry"
(OUT / "step_trials").mkdir(exist_ok=True)
rows = list(csv.DictReader((OUT / "trial_candidates.csv").open(encoding="utf-8-sig")))
# Visual inspection identifies the second base component as a structural plate.
# Keep it a reviewed reference rather than silently classifying all internals.
all_rows = list(csv.DictReader((OUT / "components_manifest.csv").open(encoding="utf-8-sig")))
rows += [r for r in all_rows if r["id"] == "base_link__C002"]
seams_only = "--seams-only" in sys.argv
if seams_only:
    recovered = json.loads((OUT / "seam_recovery_validation.json").read_text())
    originals = {r["id"]: r for r in all_rows}
    rows = [{**originals[r["id"]], "stl": r["output"]} for r in recovered
            if r["status"] == "closed_after_vertex_only_weld"]
rows.sort(key=lambda r: int(r["triangles"]))
reports = []
for r in rows:
    source = OUT / r["stl"]
    mesh = trimesh.load_mesh(source, process=True)
    assert mesh.is_volume
    dest = OUT / "step_trials" / (r["id"] + ".step")
    writer = FacetedWriter(); writer.mesh(mesh, r["id"]); writer.write(dest)
    del writer
    reader = STEPControl_Reader()
    status = reader.ReadFile(str(dest))
    if status != IFSelect_RetDone:
        dest.unlink()
        reports.append({"id": r["id"], "status": "read_failed"})
        continue
    reader.TransferRoots(); shape = reader.OneShape()
    exp = TopExp_Explorer(shape, TopAbs_SOLID); count = 0
    while exp.More():
        count += 1; exp.Next()
    props = GProp_GProps(); BRepGProp.VolumeProperties_s(shape, props)
    box = Bnd_Box(); BRepBndLib.Add_s(shape, box, False)
    bounds = np.array([[box.GetXMin(), box.GetYMin(), box.GetZMin()],
                       [box.GetXMax(), box.GetYMax(), box.GetZMax()]])
    error = float(np.max(np.abs(bounds - mesh.bounds)))
    relative = abs(props.Mass() - mesh.volume) / mesh.volume
    valid = bool(BRepCheck_Analyzer(shape).IsValid())
    passed = valid and count == 1 and error < 0.001 and relative < 1e-5
    record = {"id": r["id"], "status": "passed_conversion" if passed else "rejected_conversion",
              "is_valid_brep": valid, "solids": count, "bounds_max_error_mm": error,
              "volume_relative_error": relative, "volume_mm3": props.Mass(),
              "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
              "step_sha256": hashlib.sha256(dest.read_bytes()).hexdigest(),
              "representation": "AP214 FACETED_BREP; planar triangles; no parametric features",
              "physical_fit": "not_tested"}
    reports.append(record)
    if not passed:
        dest.unlink()
    print(record["id"], record["status"], "solids", count, flush=True)
    del reader, shape, mesh; gc.collect()
(OUT / ("step_seam_validation.json" if seams_only else "step_validation.json")).write_text(json.dumps(reports, indent=2) + "\n")
print("STEP accepted", sum(r["status"] == "passed_conversion" for r in reports), "of", len(reports), flush=True)
