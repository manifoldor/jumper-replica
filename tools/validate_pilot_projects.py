# SPDX-License-Identifier: Apache-2.0
# Adapted for the independent Jumper Replica directory and pinned upstream snapshot.
"""Compare exported 3MF geometry with the oriented source STLs."""
from pathlib import Path
import json,zipfile,xml.etree.ElementTree as ET
import numpy as np
import trimesh
out=Path(__file__).resolve().parents[1]/'printing'
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
results=[]
for p in (out/'slicer').glob('*.3mf'):
 with zipfile.ZipFile(p) as z:
  xml=ET.fromstring(z.read('3D/3dmodel.model'))
  assert xml.get('unit')=='millimeter'
  vs=xml.findall('.//m:vertex',ns);fs=xml.findall('.//m:triangle',ns)
  verts=np.array([[float(v.get(k)) for k in 'xyz'] for v in vs]);faces=np.array([[int(f.get(k)) for k in ['v1','v2','v3']] for f in fs])
  m=trimesh.Trimesh(verts,faces,process=False);s=trimesh.load_mesh(out/'oriented_stl'/(p.stem+'.stl'))
  assert len(m.faces)==len(s.faces)
  err=float(max(abs(m.extents-s.extents)));verr=abs(m.volume/s.volume-1)
  assert err<1e-4 and verr<1e-5
  repairs=ET.fromstring(z.read('Metadata/Slic3r_PE_model.config')).findall('.//mesh')
  results.append(dict(part=p.stem,faces=len(m.faces),bbox_error_mm=err,volume_relative_error=verr,slicer_mesh_repair_statistics=[e.attrib for e in repairs]))
(out/'project_geometry_checks.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
