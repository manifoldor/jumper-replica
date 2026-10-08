# SPDX-License-Identifier: Apache-2.0
# Adapted for the independent Jumper Replica directory and pinned upstream snapshot.
"""Full-triangle orthographic CPU previews with a per-pixel depth buffer."""
import csv
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import numpy as np
import trimesh
from PIL import Image, ImageDraw
from numba import njit

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "geometry"


@njit(cache=True)
def raster(v, f, c, n, size):
    z = np.full((size, size), -1e30)
    rgb = np.full((size, size, 3), 250, dtype=np.uint8)
    light = np.array([0.3, -0.4, 0.866])
    for i in range(len(f)):
        a, b, d = v[f[i, 0]], v[f[i, 1]], v[f[i, 2]]
        den = (b[1]-d[1])*(a[0]-d[0])+(d[0]-b[0])*(a[1]-d[1])
        if abs(den) < 1e-10:
            continue
        xmin = max(0, int(np.floor(min(a[0], b[0], d[0]))))
        xmax = min(size-1, int(np.ceil(max(a[0], b[0], d[0]))))
        ymin = max(0, int(np.floor(min(a[1], b[1], d[1]))))
        ymax = min(size-1, int(np.ceil(max(a[1], b[1], d[1]))))
        shade = 0.35+0.65*abs(np.dot(n[i], light))
        for y in range(ymin, ymax+1):
            for x in range(xmin, xmax+1):
                u = ((b[1]-d[1])*(x-d[0])+(d[0]-b[0])*(y-d[1]))/den
                w = ((d[1]-a[1])*(x-d[0])+(a[0]-d[0])*(y-d[1]))/den
                t = 1-u-w
                if min(u,w,t) >= -1e-7:
                    depth = u*a[2]+w*b[2]+t*d[2]
                    if depth > z[y,x]:
                        z[y,x] = depth
                        for j in range(3):
                            rgb[y,x,j] = int(max(0,min(255,c[i,j]*shade)))
    return rgb


def render(mesh, colors, matrix, title, size=800):
    v = mesh.vertices @ matrix.T
    normals = mesh.face_normals @ matrix.T
    lo = v[:,:2].min(0); hi = v[:,:2].max(0)
    factor = (size-80)/max(hi-lo)
    v[:,:2] = (v[:,:2]-(lo+hi)/2)*factor+size/2
    im = Image.fromarray(raster(v, mesh.faces, colors, normals, size))
    panel = Image.new("RGB", (size, size+50), "white");panel.paste(im,(0,50))
    ImageDraw.Draw(panel).text((15,15),title,fill="black")
    return panel


ISO = np.array([[1/np.sqrt(2),-1/np.sqrt(2),0],
                [1/np.sqrt(6),1/np.sqrt(6),-2/np.sqrt(6)],
                [1/np.sqrt(3)]*3])
rows = list(csv.DictReader((OUT/"parts_manifest.csv").open(encoding="utf-8-sig")))
urdf = ET.parse(ROOT/"upstream_snapshot/assets/jumper/urdf/jumper/urdf/jumper.urdf").getroot()
materials = {e.get("name"):np.fromstring(e.find("visual/material/color").get("rgba"),sep=" ")[:3]*255 for e in urdf.findall("link")}
placed=[];colors=[]
for r in rows:
    m=trimesh.load_mesh(OUT/"links_mm"/(r["link"]+".stl"));m.apply_transform(np.array(json.loads(r["home_world_matrix_mm"])))
    placed.append(m); colors.append(np.tile(materials[r["link"]],(len(m.faces),1)))
assembled=trimesh.util.concatenate(placed); colors=np.concatenate(colors)
views=[(ISO,"HOME / isometric"),(np.array([[1,0,0],[0,-1,0],[0,0,1]]),"HOME / top"),
       (np.array([[1,0,0],[0,0,-1],[0,1,0]]),"HOME / side")]
panels=[render(assembled,colors,mat,title) for mat,title in views]
sheet=Image.new("RGB",(2400,900),"white")
for i,p in enumerate(panels):sheet.paste(p,(800*i,50))
ImageDraw.Draw(sheet).text((15,15),"Jumper full source triangles / depth-buffer preview / named HOME geometry; URDF limit conflicts recorded separately",fill="black")
sheet.save(OUT/"previews/assembly_home.png")
shell=trimesh.load_mesh(OUT/"links_mm/upper_shell_link.stl")
panels=[render(shell,np.tile([200,55,45],(len(shell.faces),1)),mat,title) for mat,title in
        [(ISO,"Upper shell / outer"),(-ISO,"Upper shell / reverse"),(np.array([[1,0,0],[0,-1,0],[0,0,-1]]),"Upper shell / underside")]]
sheet=Image.new("RGB",(2400,850),"white")
for i,p in enumerate(panels):sheet.paste(p,(800*i,0))
sheet.save(OUT/"previews/upper_shell.png")
print("Depth-buffer assembly and shell previews written")
