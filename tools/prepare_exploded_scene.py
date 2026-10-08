# SPDX-License-Identifier: Apache-2.0
# Adapted for the independent Jumper Replica directory and pinned upstream snapshot.
"""Build a complete source-triangle exploded scene using recovered component IDs."""
from pathlib import Path
import csv,json,hashlib
import numpy as np
import trimesh
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'geometry';OUT=ROOT/'assembly'
(OUT/'scene_meshes').mkdir(parents=True,exist_ok=True)
rows=list(csv.DictReader((SRC/'parts_manifest.csv').open(encoding='utf-8-sig')))
components=list(csv.DictReader((SRC/'components_manifest.csv').open(encoding='utf-8-sig')))
by_link={r['link']:[c for c in components if c['link']==r['link']] for r in rows}
names={'base_link':'Lower shell / frame','upper_shell_link':'Upper shell','display_module_link':'Display module','tof_sensor_link':'ToF module','camera_link':'Camera module'}
terms={'shoulder':'Shoulder casing','upper_arm':'Upper-arm casing','forearm':'Forearm connector','palm':'Palm casing','finger':'Moving-finger structure','palm_pad_f':'Palm pad f','palm_pad_b':'Palm pad b','palm_grip_insert':'Palm grip insert','finger_grip_insert':'Finger grip insert','finger_tip':'Finger tip','hip':'Hip casing','thigh':'Thigh connector','calf':'Calf casing','foot_tip':'Foot-tip pad'}
split_terms={'shoulder','upper_arm','forearm','palm','finger','hip','thigh','calf'}
rootdirs={k:np.array(v,dtype=float) for k,v in dict(LF=[.7,.7,0],RF=[.7,-.7,0],LM=[0,1,0],RM=[0,-1,0],LR=[-.7,.7,0],RR=[-.7,-.7,0]).items()}
items=[];total=0
for index,row in enumerate(rows,1):
 link=row['link'];H=np.array(json.loads(row['home_world_matrix_mm']));prefix=link[:2]
 term=link[3:-5] if prefix in rootdirs else ''
 title=names.get(link,f'{prefix} {terms.get(term,term)}')
 if prefix in rootdirs:
  stage={'shoulder':0,'upper_arm':1,'forearm':2,'palm':3,'finger':3,'hip':0,'thigh':1,'calf':2,'foot_tip':3}.get(term,4)
  shift=rootdirs[prefix]*(75+stage*70);shift[2]=-stage*18
 else:shift=np.array([0.,0.,0.])
 comps=by_link[link]
 selected=[1,2,3] if link=='base_link' else [1,2] if term in split_terms else []
 bundles=[]
 if selected:
  majors={}
  for rank in selected:
   c=next(c for c in comps if int(c['rank_by_face_count'])==rank)
   original=SRC/c['stl'];seam=SRC/'seam_recovered_mm'/(c['id']+'.stl')
   mesh=trimesh.load_mesh(seam if seam.exists() else original);majors[rank]=(mesh,c)
  axis=np.array([0.,0.,1.]) if link=='base_link' else majors[2][0].bounds.mean(axis=0)-majors[1][0].bounds.mean(axis=0)
  axis=axis/max(np.linalg.norm(axis),1e-9)
  for rank,(m,c) in majors.items():
   extra=np.array([0.,0.,0.])
   if link=='base_link':extra[2]=[0,75,145][rank-1]
   else:extra=(H[:3,:3]@axis)*(-30 if rank==1 else 30)
   t=title+(' A' if rank==1 else ' B') if link!='base_link' else ['Lower shell / frame','Internal mounting plate','Internal cradle (identity pending)'][rank-1]
   bundles.append((f'{index:02d}{chr(64+rank)}',m,c['id'],t,shift+extra,True,m.is_volume))
  rest=[c for c in comps if int(c['rank_by_face_count']) not in selected]
  if rest:
   m=trimesh.util.concatenate([trimesh.load_mesh(SRC/c['stl']) for c in rest])
   bundles.append((f'{index:02d}R',m,link+'__remaining','Internal components / actuator reference',shift+([0,0,40] if link=='base_link' else np.array([0,0,0])),link=='base_link',False))
 else:
  m=trimesh.load_mesh(SRC/'links_mm'/(link+'.stl'))
  accessories=['palm_pad_f','palm_pad_b','palm_grip_insert','finger_grip_insert','finger_tip']
  if term in accessories:
   center=H[:3,:3]@m.bounds.mean(axis=0)+H[:3,3]
   shift[2]=-120-accessories.index(term)*50-center[2]
  if link=='upper_shell_link':shift=np.array([-180.,-160.,365.])
  if link=='display_module_link':shift=np.array([-180.,-160.,455.])
  if link in ['camera_link','tof_sensor_link']:shift=np.array([115.,-65. if link=='camera_link' else 65.,95.])
  bundles.append((f'{index:02d}',m,link,title,shift,True,m.is_volume))
 assert sum(len(b[1].faces) for b in bundles)==int(row['triangles'])
 for ident,m,source_id,title,delta,label,closed in bundles:
  m.apply_transform(H);assembled_center=m.bounds.mean(axis=0).copy();m.apply_translation(delta)
  path=OUT/'scene_meshes'/(ident+'.stl');m.export(path)
  material='shell'
  if term in ['forearm','thigh']:material='connector'
  if any(w in term for w in ['pad','tip','insert']):material='pad'
  if ident.endswith('R'):material='hardware'
  if link in ['display_module_link','camera_link','tof_sensor_link']:material='module'
  if link=='base_link' and ident.endswith(('B','C')):material='plate'
  items.append(dict(id=ident,source_id=source_id,link=link,name_en=title,mesh=str(path.relative_to(OUT)),triangles=len(m.faces),closed_positive_volume=bool(closed),label=label,material=material,
      assembled_center_mm=assembled_center.tolist(),exploded_center_mm=m.bounds.mean(axis=0).tolist(),explosion_translation_mm=np.asarray(delta).tolist(),home_world_matrix_mm=H.tolist()))
  total+=len(m.faces)
assert total==sum(int(r['triangles']) for r in rows)
manifest=dict(source_commit='61d065219fca767f3142c8f10aff59eae5a5a004',source_links=len(rows),source_triangles=total,render_objects=len(items),labeled_groups=sum(i['label'] for i in items),method='Source HOME matrices plus translations only. Tiny source details remain grouped; no face deletion.',items=items)
(OUT/'scene_manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({k:v for k,v in manifest.items() if k!='items'},indent=2))
