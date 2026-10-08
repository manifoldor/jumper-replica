# SPDX-License-Identifier: Apache-2.0
# Adapted for the independent Jumper Replica directory and pinned upstream snapshot.
"""Recover reference geometry and assembly from the original visual URDF meshes.

No hole filling, nominal CAD reconstruction, material assignment or fit certification.
Run with trimesh, scipy, numpy, matplotlib and Pillow installed.
"""
from __future__ import annotations

import ast
import collections
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET

import tempfile
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "jumper-replica-matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
import numpy as np
import trimesh
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.getenv("JUMPER_GEOMETRY_DIR", str(ROOT / "geometry")))
URDF = ROOT / "upstream_snapshot/assets/jumper/urdf/jumper/urdf/jumper.urdf"
for folder in ("links_mm", "components_mm", "previews"):
    (OUT / folder).mkdir(parents=True, exist_ok=True)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(name, rows):
    if not rows:
        return
    with (OUT / name).open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def transform(origin):
    t = np.eye(4)
    if origin is not None:
        t[:3, :3] = Rotation.from_euler("xyz", np.fromstring(origin.get("rpy", "0 0 0"), sep=" ")).as_matrix()
        t[:3, 3] = np.fromstring(origin.get("xyz", "0 0 0"), sep=" ") * 1000
    return t


def category(name):
    if name in {"camera_link", "tof_sensor_link", "display_module_link"}:
        return "purchased_module_or_housing_review"
    if name.endswith("forearm_link") or name.endswith("thigh_link"):
        return "aluminium_connector_assembly_review"
    if any(s in name for s in ("pad_", "tip_link", "grip_insert")):
        return "pad_tip_insert_material_review"
    return "structure_or_composite_review"


def export_checked(mesh, path):
    mesh.export(path)
    back = trimesh.load_mesh(path, process=False)
    assert len(back.faces) == len(mesh.faces)
    error = float(np.max(np.abs(back.bounds - mesh.bounds)))
    assert error < 0.0001, (path, error)
    return error


def circular_rims(mesh):
    """Axis-aligned planar sharp closed rims, inward-wall checked; REF only."""
    if len(mesh.faces) < 12:
        return []
    adj = mesh.face_adjacency
    edges = mesh.face_adjacency_edges
    normals = mesh.face_normals
    dot = np.einsum("ij,ij->i", normals[adj[:, 0]], normals[adj[:, 1]])
    sharp = dot < math.cos(math.radians(25))
    result = []
    for w in range(3):
        uv = [a for a in range(3) if a != w]
        levels = collections.defaultdict(list)
        for edge, pair in zip(edges[sharp], adj[sharp]):
            for k in (0, 1):
                if abs(normals[pair[k], w]) > 0.99999:
                    level = round(float(mesh.vertices[edge, w].mean()), 3)
                    levels[level].append((edge, pair[1-k]))
                    break
        for level, items in levels.items():
            neighbors = collections.defaultdict(set)
            for (a, b), _ in items:
                neighbors[int(a)].add(int(b)); neighbors[int(b)].add(int(a))
            unseen = set(neighbors)
            while unseen:
                pending = [min(unseen)]; loop = set()
                while pending:
                    a = pending.pop()
                    if a in loop:
                        continue
                    loop.add(a); pending.extend(neighbors[a] - loop)
                unseen -= loop
                if len(loop) < 12 or any(len(neighbors[a]) != 2 for a in loop):
                    continue
                pts = mesh.vertices[sorted(loop)][:, uv]
                center_u, center_v, c = np.linalg.lstsq(
                    np.column_stack((2 * pts, np.ones(len(pts)))), (pts * pts).sum(1), rcond=None
                )[0]
                rr = c + center_u**2 + center_v**2
                if rr <= 0:
                    continue
                radius = math.sqrt(rr)
                residual = float(np.max(np.abs(np.linalg.norm(pts - [center_u, center_v], axis=1) - radius)))
                if not 0.65 <= radius <= 12 or residual > 0.035:
                    continue
                inward = []
                for (a, b), other in items:
                    if int(a) in loop and int(b) in loop:
                        midpoint = mesh.vertices[[a, b]][:, uv].mean(0)
                        inward.append(float(np.dot(normals[other, uv], midpoint - [center_u, center_v])))
                if not inward or np.mean(inward) > -0.25 * radius:
                    continue
                center = np.zeros(3); center[uv] = [center_u, center_v]; center[w] = level
                result.append({"axis": "xyz"[w], "center_x_mm_REF": float(center[0]),
                               "center_y_mm_REF": float(center[1]), "center_z_mm_REF": float(center[2]),
                               "diameter_mm_REF": 2 * radius, "max_radial_error_mm": residual,
                               "rim_vertices": len(loop), "status": "rim_fit_only_not_hole_type"})
    return result


ISO = np.array([[1 / np.sqrt(2), -1 / np.sqrt(2), 0],
                [1 / np.sqrt(6), 1 / np.sqrt(6), -2 / np.sqrt(6)],
                [1 / np.sqrt(3)] * 3])


def draw(ax, meshes, matrix=ISO, title=""):
    polys = []; colors = []; zs = []
    bounds = []
    light = np.array([0.4, -0.4, 0.8]); light /= np.linalg.norm(light)
    for m, color in meshes:
        v = m.vertices @ matrix.T
        tri = v[m.faces]
        normals = m.face_normals @ matrix.T
        intensity = 0.45 + 0.55 * np.abs(normals @ light)
        polys.append(tri[:, :, :2]); zs.append(tri[:, :, 2].mean(1))
        colors.append(np.clip(np.asarray(color)[None, :] * intensity[:, None], 0, 1))
        bounds.append(v[:, :2])
    p = np.concatenate(polys); z = np.concatenate(zs); c = np.concatenate(colors)
    order = np.argsort(z)
    ax.add_collection(PolyCollection(p[order], facecolors=c[order], edgecolors="none", rasterized=True))
    b = np.concatenate(bounds); lo, hi = b.min(0), b.max(0)
    margin = max(float((hi-lo).max()) * 0.06, 1)
    ax.set_xlim(lo[0]-margin, hi[0]+margin); ax.set_ylim(hi[1]+margin, lo[1]-margin)
    ax.set_aspect("equal"); ax.axis("off"); ax.set_title(title, fontsize=9)


robot = ET.parse(URDF).getroot()
links = {e.get("name"): e for e in robot.findall("link")}
home = None
tree = ast.parse((ROOT / "upstream_snapshot/tasks/jumper/common/constants.py").read_text())
for node in tree.body:
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == "HOME":
        home = ast.literal_eval(node.value)
assert home and len(home) == 22
poses = {"base_link": np.eye(4)}
joints = []; pending = list(robot.findall("joint")); home_limit_violations = []
while pending:
    progressed = False
    for j in pending[:]:
        parent = j.find("parent").get("link"); child = j.find("child").get("link")
        if parent not in poses:
            continue
        origin = transform(j.find("origin")); rotation = np.eye(4)
        axis = np.fromstring(j.find("axis").get("xyz", "0 0 0"), sep=" ") if j.find("axis") is not None else np.zeros(3)
        q = home.get(j.get("name"), 0.0)
        if j.get("type") != "fixed":
            rotation[:3, :3] = Rotation.from_rotvec(axis * q).as_matrix()
        poses[child] = poses[parent] @ origin @ rotation
        limit = j.find("limit")
        if limit is not None:
            if not float(limit.get("lower")) <= q <= float(limit.get("upper")):
                home_limit_violations.append({"joint": j.get("name"), "home_rad": q,
                                              "lower": float(limit.get("lower")), "upper": float(limit.get("upper"))})
        joints.append({"joint": j.get("name"), "type": j.get("type"), "parent": parent, "child": child,
                       "origin_xyz_mm": json.dumps(origin[:3, 3].tolist()),
                       "origin_rpy_rad": j.find("origin").get("rpy", "0 0 0") if j.find("origin") is not None else "0 0 0",
                       "axis": json.dumps(axis.tolist()), "home_rad": q,
                       "lower_rad": limit.get("lower") if limit is not None else "",
                       "upper_rad": limit.get("upper") if limit is not None else ""})
        pending.remove(j); progressed = True
    assert progressed, "Disconnected or cyclic URDF"
assert len(poses) == len(links)

records = []; components = []; holes = []; meshes = {}; split_meshes = {}; candidates = []
assembly = []; max_error = 0.0
for name, link in links.items():
    visual = link.find("visual"); element = visual.find("geometry/mesh")
    src = (URDF.parent / element.get("filename")).resolve()
    m = trimesh.load_mesh(src, process=True)
    scale = np.fromstring(element.get("scale", "1 1 1"), sep=" ") * 1000
    m.vertices *= scale
    parts = sorted(m.split(only_watertight=False, repair=False), key=lambda c: (-len(c.faces), *c.bounds.mean(0)))
    assert sum(len(c.faces) for c in parts) == len(m.faces)
    meshes[name] = m; split_meshes[name] = parts
    error = export_checked(m, OUT / "links_mm" / f"{name}.stl"); max_error = max(max_error, error)
    color = np.fromstring(visual.find("material/color").get("rgba"), sep=" ")[:3]
    world = poses[name] @ transform(visual.find("origin"))
    placed = m.copy(); placed.apply_transform(world)
    assembly.append((placed, color))
    mass = float(link.find("inertial/mass").get("value"))
    records.append({"link": name, "category": category(name), "source": str(src.relative_to(ROOT / "upstream_snapshot")),
                    "source_sha256": sha(src), "triangles": len(m.faces), "components": len(parts),
                    "watertight": bool(m.is_watertight), "winding_consistent": bool(m.is_winding_consistent),
                    "is_volume": bool(m.is_volume), "x_mm_REF": float(m.extents[0]),
                    "y_mm_REF": float(m.extents[1]), "z_mm_REF": float(m.extents[2]),
                    "urdf_mass_kg": mass, "mesh_volume_mm3_if_valid": float(m.volume) if m.is_volume else "",
                    "home_world_matrix_mm": json.dumps(world.tolist()), "export_bounds_error_mm": error})
    for k, c in enumerate(parts, 1):
        cid = f"{name}__C{k:03}"
        # 972-face component repeats throughout joint assemblies. Identity is provisional.
        repeated = len(c.faces) == 972 and abs(c.volume - 10569.66) < 0.2
        if repeated:
            role = "repeated_actuator_or_bearing_reference_not_print"
        elif len(c.faces) < 100:
            role = "small_fragment_or_detail_review"
        elif category(name) == "purchased_module_or_housing_review":
            role = "purchased_module_or_housing_review"
        elif name == "base_link" and k != 1:
            role = "internal_component_identity_review"
        elif category(name) == "aluminium_connector_assembly_review":
            role = "metal_connector_or_cover_review"
        elif c.is_volume:
            role = "closed_geometry_trial_candidate_material_unverified"
        else:
            role = "open_geometry_repair_or_reconstruction_needed"
        path = OUT / "components_mm" / f"{cid}.stl"
        err = export_checked(c, path); max_error = max(max_error, err)
        row = {"id": cid, "link": name, "rank_by_face_count": k, "triangles": len(c.faces),
               "role": role, "watertight": bool(c.is_watertight), "winding_consistent": bool(c.is_winding_consistent),
               "is_volume": bool(c.is_volume), "x_mm_REF": float(c.extents[0]),
               "y_mm_REF": float(c.extents[1]), "z_mm_REF": float(c.extents[2]),
               "signed_volume_mm3": float(c.volume), "center_xyz_mm": json.dumps(c.bounds.mean(0).tolist()),
               "stl": str(path.relative_to(OUT)), "sha256": sha(path), "export_bounds_error_mm": err}
        components.append(row)
        if role == "closed_geometry_trial_candidate_material_unverified":
            candidates.append(row)
        if len(c.faces) >= 100:
            for h in circular_rims(c):
                holes.append({"component": cid, **h})
    print(name, "components", len(parts), "closed solids", sum(c.is_volume for c in parts), flush=True)

write_csv("parts_manifest.csv", records); write_csv("components_manifest.csv", components)
write_csv("trial_candidates.csv", candidates); write_csv("joint_schedule.csv", joints)
write_csv("circular_rim_reference.csv", holes)
assembly_mesh = trimesh.util.concatenate([m for m, _ in assembly])
assembly_mesh.export(OUT / "assembly_home_mm.stl")
scene = trimesh.Scene()
for (name, _), (m, color) in zip(links.items(), assembly):
    m = m.copy(); m.visual.face_colors = np.r_[color * 255, 255].astype(np.uint8)
    scene.add_geometry(m, node_name=name, geom_name=name)
# GLB uses meters; STL outputs above intentionally use millimeters.
scene.apply_transform(np.diag([0.001, 0.001, 0.001, 1]))
scene.export(OUT / "assembly_home.glb")
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, mat, title in zip(axes, (ISO, np.array([[1, 0, 0], [0, -1, 0], [0, 0, 1]]),
                                np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])),
                          ("HOME / isometric", "HOME / top", "HOME / side")):
    draw(ax, assembly, mat, title)
fig.suptitle("Jumper: source visual geometry at named HOME pose / no physical-fit claim")
fig.tight_layout(); fig.savefig(OUT / "previews/assembly_home.png", dpi=150); plt.close(fig)
fig, axes = plt.subplots(9, 5, figsize=(15, 25))
for ax, (name, m) in zip(axes.flat, meshes.items()):
    draw(ax, [(m, [0.75, 0.78, 0.82])], title=f"{name}\n{len(split_meshes[name])} components | {m.extents.round(1)} mm")
for ax in list(axes.flat)[len(meshes):]:
    ax.axis("off")
fig.tight_layout(); fig.savefig(OUT / "previews/link_inventory.png", dpi=110); plt.close(fig)
fig, axes = plt.subplots(4, 5, figsize=(16, 13))
focus = [("base_link", k) for k in range(7)] + [("upper_shell_link", 0)] + [
    (n, k) for n in ("LF_shoulder_link", "LF_forearm_link", "LM_calf_link", "LF_upper_arm_link") for k in range(3)]
for ax, (name, k) in zip(axes.flat, focus):
    c = split_meshes[name][k]
    draw(ax, [(c, [0.76, 0.78, 0.82])], title=f"{name} C{k+1:03}\n{len(c.faces)} faces | solid={c.is_volume}")
fig.tight_layout(); fig.savefig(OUT / "previews/component_focus.png", dpi=140); plt.close(fig)
# Full-resolution source shell views, including its inner surface.
shell = meshes["upper_shell_link"]
fig, axes = plt.subplots(1, 3, figsize=(15, 5))
for ax, mat, title in zip(axes, (ISO, -ISO, np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]])),
                          ("Outer shell", "Reverse isometric", "Underside / mounting features")):
    draw(ax, [(shell, [0.8, 0.18, 0.14])], mat, title)
fig.tight_layout(); fig.savefig(OUT / "previews/upper_shell.png", dpi=160); plt.close(fig)
summary = {"source_commit": "61d065219fca767f3142c8f10aff59eae5a5a004",
           "source_urdf_sha256": sha(URDF), "units": {"stl": "mm", "assembly_glb": "m"},
           "links": len(records), "joints": len(joints), "movable_joints": len(home),
           "total_urdf_mass_kg": sum(r["urdf_mass_kg"] for r in records),
           "components": len(components), "triangles": sum(r["triangles"] for r in records),
           "valid_closed_components": sum(r["is_volume"] for r in components),
           "trial_candidate_components": len(candidates), "fitted_circular_rims": len(holes),
           "component_roles": dict(collections.Counter(r["role"] for r in components)),
           "max_export_bounds_error_mm": max_error,
           "assembly_bounds_mm": assembly_mesh.bounds.tolist(), "assembly_extents_mm": assembly_mesh.extents.tolist(),
           "home_pose_urdf_limit_violations": home_limit_violations,
           "repairs_performed": False, "slicing": "not_tested", "self_intersection": "not_tested",
           "physical_fit": "not_tested", "load_capacity": "not_tested",
           "versions": {"trimesh": trimesh.__version__, "numpy": np.__version__, "matplotlib": matplotlib.__version__}}
(OUT / "validation.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2), flush=True)
