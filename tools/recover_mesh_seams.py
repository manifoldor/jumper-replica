# SPDX-License-Identifier: Apache-2.0
# Adapted for the independent Jumper Replica directory and pinned upstream snapshot.
"""Try vertex-only seam welding; no face deletion, hole filling or remeshing."""
import csv
import hashlib
import json
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial import cKDTree

OUT = Path(__file__).resolve().parents[1] / "geometry"
(OUT / "seam_recovered_mm").mkdir(exist_ok=True)
rows = list(csv.DictReader((OUT / "components_manifest.csv").open(encoding="utf-8-sig")))
reports = []
for r in rows:
    if r["is_volume"] == "True" or int(r["triangles"]) < 100:
        continue
    if r["role"] == "purchased_module_or_housing_review":
        continue
    original = trimesh.load_mesh(OUT / r["stl"], process=True)
    result = {"id": r["id"], "original_role": r["role"], "status": "still_open_no_reconstruction",
              "original_faces": len(original.faces), "original_sha256": hashlib.sha256((OUT/r["stl"]).read_bytes()).hexdigest()}
    for digits in (4, 3):
        m = original.copy(); m.merge_vertices(digits_vertex=digits)
        assert len(m.faces) == len(original.faces)
        shift = float(cKDTree(m.vertices).query(original.vertices)[0].max())
        if m.is_volume and shift <= 0.001:
            path = OUT / "seam_recovered_mm" / (r["id"] + ".stl")
            m.export(path)
            back = trimesh.load_mesh(path, process=True)
            assert back.is_volume and len(back.faces) == len(original.faces)
            result.update(status="closed_after_vertex_only_weld", grid_decimal_digits_mm=digits,
                          max_vertex_displacement_mm=shift, faces_unchanged=True,
                          bounds_max_error_mm=float(np.max(np.abs(back.bounds-original.bounds))),
                          output=str(path.relative_to(OUT)), output_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                          hole_filling=False, face_deletion=False, physical_fit="not_tested")
            break
    reports.append(result)
    print(r["id"], result["status"], flush=True)
(OUT / "seam_recovery_validation.json").write_text(json.dumps(reports, indent=2) + "\n")
print("Recovered", sum(r["status"] == "closed_after_vertex_only_weld" for r in reports), "of", len(reports))
