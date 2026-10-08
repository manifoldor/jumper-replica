# SPDX-License-Identifier: Apache-2.0
# Adapted for the independent Jumper Replica directory and pinned upstream snapshot.
"""Render oriented pilot geometry using the existing depth-buffer renderer."""
from pathlib import Path
import json
import numpy as np
import trimesh
from PIL import Image, ImageDraw
root=Path(__file__).resolve().parents[1]
namespace={'__file__':str(root/'tools/render_reverse_geometry.py'),'__name__':'__main__'}
source=(root/'tools/render_reverse_geometry.py').read_text().split('rows = list')[0]
exec(compile(source,str(root/'tools/render_reverse_geometry.py'),'exec'),namespace)
folder=root/'printing'
sheet=Image.new('RGB',(1800,1300),'white')
for i,path in enumerate(sorted((folder/'oriented_stl').glob('*.stl'))):
    m=trimesh.load_mesh(path)
    colors=np.tile([55,125,190],(len(m.faces),1)); colors[m.face_normals[:,2]<-.707]=[220,95,45]
    panel=namespace['render'](m,colors,namespace['ISO'],path.stem,600)
    sheet.paste(panel,((i%3)*600,(i//3)*650))
sheet.save(folder/'previews/orientations.png')
print('Preview written')
