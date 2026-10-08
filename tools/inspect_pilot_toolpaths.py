# SPDX-License-Identifier: Apache-2.0
# Adapted for the independent Jumper Replica directory and pinned upstream snapshot.
"""Check reference toolpath bounds and plot extrusion volume by height and feature."""
from pathlib import Path
import re
import json
import zipfile
import collections
import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'printing'
reports=[]
fig,axes=plt.subplots(2,3,figsize=(15,8),constrained_layout=True)
for ax,path in zip(axes.flat,sorted((ROOT/'experiments/reference_gcode').glob('*.gcode'))):
    pos=dict(X=0.,Y=0.,Z=0.,E=0.); kind='Custom'; debt=0.; groups=collections.defaultdict(lambda:[0.,0.]); xyz=[]; counts=collections.Counter()
    for line in path.read_text().splitlines():
        if line.startswith(';TYPE:'):
            kind=line[6:]
        code=line.split(';')[0]
        if code.startswith('G92 '):
            for key,value in re.findall(r'([XYZE])([-+\d.]+)',code):pos[key]=float(value)
        elif code.startswith(('G0 ','G1 ')):
            old=pos.copy();fields=dict((k,float(v)) for k,v in re.findall(r'([XYZE])([-+\d.]+)',code));pos.update(fields)
            delta=pos['E']-old['E']
            if delta<0:debt-=delta
            else:
                deposit=max(0,delta-debt);debt=max(0,debt-delta)
                if deposit>1e-7 and ('X' in fields or 'Y' in fields):
                    xyz.extend([[old[k] for k in 'XYZ'],[pos[k] for k in 'XYZ']]);counts[kind]+=1
                    groups[round(pos['Z'],3)][int(kind.startswith('Support'))]+=deposit*math.pi*(1.75/2)**2
    bounds=np.array([np.min(xyz,axis=0),np.max(xyz,axis=0)])
    assert bounds[0,0]>=0 and bounds[0,1]>=0 and bounds[1,0]<=220 and bounds[1,1]<=220 and bounds[1,2]<=250
    layers=sorted(groups);vols=np.array([groups[z] for z in layers]);ax.plot(layers,vols[:,0],label='Model + brim');ax.plot(layers,vols[:,1],label='Support');ax.set_title(path.name.split('.REFERENCE')[0],fontsize=10);ax.set_xlabel('Z (mm)');ax.set_ylabel('Deposited volume / height (mm3)');ax.legend(fontsize=8)
    project=OUT/'slicer'/(path.name.split('.REFERENCE')[0]+'.3mf')
    with zipfile.ZipFile(project) as z:
        assert z.testzip() is None
        assert any(n.endswith('.model') for n in z.namelist())
        assert 'Metadata/Slic3r_PE.config' in z.namelist()
        config=z.read('Metadata/Slic3r_PE.config').decode()
        assert 'layer_height = 0.2' in config and 'nozzle_diameter = 0.4' in config
    reports.append(dict(part=path.name.split('.REFERENCE')[0],extruding_path_bounds_mm=bounds.tolist(),feature_move_counts=dict(counts),deposited_volume_mm3=dict(model_and_brim=float(vols[:,0].sum()),support=float(vols[:,1].sum())),project_crc_and_embedded_config_valid=True))
fig.savefig(OUT/'previews/extrusion_by_height.png',dpi=150)
(OUT/'toolpath_checks.json').write_text(json.dumps(dict(method='Absolute E tracking, G92 handling and retract debt; travel excluded. Includes brim in model volume.',results=reports),indent=2))
print(json.dumps(reports,indent=2))
