# SPDX-License-Identifier: Apache-2.0
# Adapted for the independent Jumper Replica directory and pinned upstream snapshot.
"""Render recovered Jumper geometry with Blender Cycles; no geometric reconstruction."""
from pathlib import Path
import json,math,sys
import numpy as np
import struct
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assembly'
manifest=json.loads((OUT/'scene_manifest.json').read_text())
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.render.engine='CYCLES';scene.cycles.samples=48;scene.cycles.use_denoising=True
scene.cycles.max_bounces=6;scene.cycles.transparent_max_bounces=8
scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA';scene.render.film_transparent=True
scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX'
scene.world.color=(.6,.6,.6)
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.8,.85,1,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.18
try:
 prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL';prefs.get_devices()
 for device in prefs.devices:device.use=device.type=='METAL'
 if any(d.type=='METAL' for d in prefs.devices):scene.cycles.device='GPU'
 print('CYCLES DEVICES',[(d.name,d.type,d.use) for d in prefs.devices],flush=True)
except Exception as e:print('CPU fallback',e,flush=True)
colors={'shell':(.42,.008,.013,1),'connector':(.55,.61,.66,1),'pad':(.18,.21,.24,1),'hardware':(.045,.055,.07,1),'module':(.055,.07,.09,1),'plate':(.24,.29,.34,1)}
mats={}
for name,color in colors.items():
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=color;p.inputs['Roughness'].default_value=.36 if name=='shell' else .43;p.inputs['Metallic'].default_value=.7 if name in ['connector','plate'] else .08;mats[name]=m
objects={}
for item in manifest['items']:
 raw=(OUT/item['mesh']).read_bytes();count=struct.unpack_from('<I',raw,80)[0]
 assert len(raw)==84+50*count and count==item['triangles']
 records=np.frombuffer(raw,dtype=np.dtype([('normal','<f4',(3,)),('vertices','<f4',(3,3)),('attribute','<u2')]),offset=84,count=count)
 vertices,inverse=np.unique(records['vertices'].reshape(-1,3),axis=0,return_inverse=True)
 mesh=bpy.data.meshes.new(item['id']);mesh.from_pydata(vertices.tolist(),[],inverse.reshape(-1,3).tolist());mesh.update()
 assert len(mesh.polygons)==item['triangles']
 obj=bpy.data.objects.new(item['id']+'__'+item['source_id'],mesh);scene.collection.objects.link(obj);obj.scale=(.001,)*3
 obj.data.materials.append(mats[item['material']])
 for polygon in obj.data.polygons:polygon.use_smooth=True
 obj.data.set_sharp_from_angle(angle=math.radians(35))
 objects[item['id']]=obj

def light(name,position,power,size,color):
 data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size;data.color=color
 obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj);obj.location=position;obj.rotation_euler=(-obj.location).to_track_quat('-Z','Y').to_euler()
light('Key softbox',(1.2,-1.8,2.4),140,2.0,(1,.94,.88))
light('Fill softbox',(-1.7,-.6,1.5),100,1.8,(.78,.87,1))
light('Rim softbox',(.3,1.8,2),170,1.5,(1,1,1))
cam_data=bpy.data.cameras.new('Engineering orthographic');cam=bpy.data.objects.new('Engineering orthographic',cam_data);scene.collection.objects.link(cam);scene.camera=cam;cam.data.type='ORTHO';cam.data.lens=50

def render(name,selected,width,height,view_direction=(1.3,-1.7,1.9),assembled=False):
 for ident,obj in objects.items():
  obj.hide_render=ident not in selected
  obj.location=Vector(manifest['items'][list(objects).index(ident)]['explosion_translation_mm'])*(-.001 if assembled else 0)
 bpy.context.view_layer.update()
 bounds=[obj.matrix_world@Vector(v) for ident,obj in objects.items() if ident in selected for v in obj.bound_box]
 lo=Vector(tuple(min(v[k] for v in bounds) for k in range(3)));hi=Vector(tuple(max(v[k] for v in bounds) for k in range(3)))
 target=(lo+hi)/2;direction=Vector(view_direction).normalized();cam.location=target+direction*3;cam.rotation_euler=(-direction).to_track_quat('-Z','Y').to_euler()
 bpy.context.view_layer.update()
 inv=cam.matrix_world.inverted();projected=[inv@v for v in bounds];xs=[v.x for v in projected];ys=[v.y for v in projected]
 # Shift to the projected bounds center for stable margins.
 shift=cam.matrix_world.to_quaternion()@Vector(((max(xs)+min(xs))/2,(max(ys)+min(ys))/2,0))
 cam.location+=shift
 cam.data.ortho_scale=max(max(xs)-min(xs),(max(ys)-min(ys))*width/height)*1.16
 scene.render.resolution_x=width;scene.render.resolution_y=height
 scene.render.filepath=str(OUT/(name+'.png'))
 bpy.context.view_layer.update()
 anchors={}
 for item in manifest['items']:
  if item['id'] in selected:
   point=Vector(item['assembled_center_mm'] if assembled else item['exploded_center_mm'])*.001
   uv=world_to_camera_view(scene,cam,point);anchors[item['id']]=[float(uv.x*width),float((1-uv.y)*height)]
 (OUT/(name+'_anchors.json')).write_text(json.dumps(anchors,indent=2))
 print('RENDER START',name,width,height,flush=True);bpy.ops.render.render(write_still=True);print('RENDER DONE',name,flush=True)

(OUT/'render_geometry_checks.json').write_text(json.dumps(dict(source_faces=manifest['source_triangles'],blender_faces=sum(len(o.data.polygons) for o in objects.values()),objects=len(objects),duplicate_faces_preserved=True),indent=2))
all_ids=set(objects)
if '--draft' in sys.argv:
 scene.cycles.samples=12;render('draft',all_ids,1500,1450)
else:
 render('hero',all_ids,3600,3200)
 hero_camera=cam.matrix_world.copy();hero_scale=cam.data.ortho_scale
 render('body_detail',{i['id'] for i in manifest['items'] if i['link'] in ['base_link','upper_shell_link','camera_link','tof_sensor_link','display_module_link']},1450,1050,view_direction=(1.3,-1.6,1.0))
 render('front_detail',{i['id'] for i in manifest['items'] if i['link'].startswith('LF_')},1450,1050,view_direction=(1.7,-1.6,1.4))
 render('leg_detail',{i['id'] for i in manifest['items'] if i['link'].startswith('LM_')},1450,1050,view_direction=(1.7,-1.8,1.6))
 render('assembled',{i['id'] for i in manifest['items']},1450,1050,assembled=True)
 # Save the complete exploded scene with the hero camera.
 for obj in objects.values():obj.location=(0,0,0);obj.hide_render=False
 cam.matrix_world=hero_camera;cam.data.ortho_scale=hero_scale;scene.render.resolution_x=3600;scene.render.resolution_y=3200
 scene.render.filepath='//hero.png'
 for screen in bpy.data.screens:
  for area in screen.areas:
   for space in area.spaces:
    if space.type=='FILE_BROWSER' and space.params:space.params.directory=b'//'
 bpy.context.preferences.filepaths.save_version=0
 bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'Jumper_Exploded.blend'))
