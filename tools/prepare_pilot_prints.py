# SPDX-License-Identifier: Apache-2.0
# Adapted for the independent Jumper Replica directory and pinned upstream snapshot.
"""Prepare dimension-preserving pilot orientations and sampled normal thickness checks."""
from pathlib import Path
import csv
import hashlib
import json
import numpy as np
import trimesh
from numba import njit

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'geometry/pilot_fit_set'
OUT = ROOT / 'printing'

@njit(cache=True)
def normal_hits(points, normals, triangles):
    result = np.full(len(points), np.nan)
    for i in range(len(points)):
        d = -normals[i]
        o = points[i] + d * 1e-4
        best = 1e30
        for tri in triangles:
            e1 = tri[1] - tri[0]
            e2 = tri[2] - tri[0]
            h = np.cross(d, e2)
            det = np.dot(e1, h)
            if abs(det) < 1e-10:
                continue
            s = o - tri[0]
            u = np.dot(s, h) / det
            if u < -1e-8 or u > 1+1e-8:
                continue
            q = np.cross(s, e1)
            v = np.dot(d, q) / det
            if v < -1e-8 or u+v > 1+1e-8:
                continue
            t = np.dot(e2, q) / det
            if 1e-4 < t < best:
                best = t
        if best < 1e29:
            result[i] = best + 1e-4
    return result


def sample(mesh, count, seed):
    rng = np.random.default_rng(seed)
    ids = rng.choice(len(mesh.faces), count, p=mesh.area_faces/mesh.area)
    uv = rng.random((count, 2))
    s = np.sqrt(uv[:, 0])
    bary = np.column_stack((1-s, s*(1-uv[:, 1]), s*uv[:, 1]))
    points = (mesh.triangles[ids] * bary[:, :, None]).sum(axis=1)
    return ids, points, normal_hits(points, mesh.face_normals[ids], mesh.triangles)


def main():
    for folder in ['oriented_stl', 'wall_samples', 'slicer', 'previews']:
        (OUT/folder).mkdir(parents=True, exist_ok=True)
    # Control: the inward ray must cross a known 2 mm hollow wall, not its 20 mm envelope.
    outer = trimesh.creation.box(extents=[20, 20, 20])
    inner = trimesh.creation.box(extents=[16, 16, 16]); inner.invert()
    control = trimesh.util.concatenate([outer, inner])
    hits = normal_hits(control.triangles_center, control.face_normals, control.triangles)
    assert np.allclose(hits, 2, atol=1e-6), 'Hollow-wall control failed'
    rows = []; choices = []
    for path in sorted(SRC.glob('*.stl')):
        mesh = trimesh.load_mesh(path)
        assert mesh.is_volume, f'Invalid input solid: {path.name}'
        ids, points, hits = sample(mesh, 3000, 20261008)
        with (OUT/'wall_samples'/f'{path.stem}.csv').open('w') as f:
            writer = csv.writer(f); writer.writerow(['source_face', 'x_mm', 'y_mm', 'z_mm', 'normal_distance_mm'])
            writer.writerows([[int(i), *p, float(h)] for i, p, h in zip(ids, points, hits)])
        ups = [('local_z_up', np.array([0.,0.,1.])), ('local_z_down', np.array([0.,0.,-1.]))]
        for k in np.argsort(mesh.facets_area)[-12:]:
            up = -mesh.facets_normal[k]
            if not any(np.dot(up, v) > .99999 for _, v in ups):
                ups.append((f'facet_{k}_down', up))
        candidates = []
        for name, up in ups:
            transform = trimesh.geometry.align_vectors(up, [0,0,1])
            placed = mesh.copy(); placed.apply_transform(transform)
            shift = np.array([-placed.bounds[:,0].mean(), -placed.bounds[:,1].mean(), -placed.bounds[0,2]])
            placed.apply_translation(shift); transform[:3,3] += shift
            contact = (placed.triangles[:,:,2].max(axis=1) <= .21) & (placed.face_normals[:,2] < -.5)
            overhang = (placed.face_normals[:,2] < -np.cos(np.pi/4)) & (placed.triangles_center[:,2] > .4)
            bed_area = float(placed.area_faces[contact].sum())
            down_area = float(placed.area_faces[overhang].sum())
            score = down_area/max(bed_area,1) + placed.extents[2]*.005
            item = dict(part=path.stem, orientation=name, bed_contact_area_mm2=bed_area,
                        downward_area_above_0_4_mm2=down_area, score=float(score),
                        extents_mm=placed.extents.tolist(), transform=transform.tolist())
            candidates.append((score, placed, item))
        candidates.sort(key=lambda x:x[0])
        # The heuristic is a starting orientation; slice support and inspect before printing.
        _, chosen, selection = candidates[0]
        target = OUT/'oriented_stl'/path.name; chosen.export(target)
        back = trimesh.load_mesh(target)
        assert len(back.faces)==len(mesh.faces) and back.is_volume
        assert abs(back.volume/mesh.volume-1) < 1e-5
        row = dict(selection, source_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                   faces=len(mesh.faces), source_volume_mm3=float(mesh.volume),
                   export_volume_relative_error=float(abs(back.volume/mesh.volume-1)),
                   wall_sample_count=len(hits), wall_hits=int(np.isfinite(hits).sum()),
                   normal_distance_percentiles_mm=np.nanpercentile(hits,[0,1,5,50]).tolist(),
                   sampled_area_fraction_under_0_8=float(np.mean(hits<.8)),
                   sampled_area_fraction_under_1_2=float(np.mean(hits<1.2)),
                   fits_220_bed_with_5_mm_margin=bool(np.all(back.extents[:2]<=210)))
        rows.append(row); choices.extend([v for _,_,v in candidates])
        print(path.name, selection['orientation'], np.round(back.extents,2), flush=True)
    (OUT/'geometry_checks.json').write_text(json.dumps(dict(
        method='Area-weighted inward surface-normal ray distance; not global minimum wall thickness.',
        control='24 hollow-cube face-center rays: all 2 mm within 1e-6 mm',
        orientation_method='Rank planar-face orientations by downward area / contact area plus height; tentative.',
        source_commit='61d065219fca767f3142c8f10aff59eae5a5a004', parts=rows),indent=2))
    (OUT/'orientation_candidates.json').write_text(json.dumps(choices,indent=2))

if __name__ == '__main__':
    main()
