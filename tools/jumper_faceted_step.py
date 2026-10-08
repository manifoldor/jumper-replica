# SPDX-License-Identifier: Apache-2.0
# Adapted for the independent Jumper Replica directory and pinned upstream snapshot.
# Adapted from the prior Microduck faceted reference converter.
"""Compact AP214 faceted B-rep serialization, geometry preserved verbatim."""
from pathlib import Path
class FacetedWriter:
    def __init__(self):
        self.lines=[]
        self.app=self.add("APPLICATION_CONTEXT('core data for automotive mechanical design processes')")
        self.add(f"APPLICATION_PROTOCOL_DEFINITION('international standard','automotive_design',2000,#{self.app})")
        self.pc=self.add(f"PRODUCT_CONTEXT('',#{self.app},'mechanical')")
        self.dc=self.add(f"PRODUCT_DEFINITION_CONTEXT('part definition',#{self.app},'design')")
        mm=self.add('(LENGTH_UNIT() NAMED_UNIT(*) SI_UNIT(.MILLI.,.METRE.))')
        rad=self.add('(NAMED_UNIT(*) PLANE_ANGLE_UNIT() SI_UNIT($,.RADIAN.))')
        sr=self.add('(NAMED_UNIT(*) SI_UNIT($,.STERADIAN.) SOLID_ANGLE_UNIT())')
        tol=self.add(f"UNCERTAINTY_MEASURE_WITH_UNIT(LENGTH_MEASURE(1.E-07),#{mm},'distance_accuracy_value','conversion tolerance')")
        self.context=self.add(f"(GEOMETRIC_REPRESENTATION_CONTEXT(3) GLOBAL_UNCERTAINTY_ASSIGNED_CONTEXT((#{tol})) GLOBAL_UNIT_ASSIGNED_CONTEXT((#{mm},#{rad},#{sr})) REPRESENTATION_CONTEXT('','3D millimetres'))")
        point=self.point([0.,0.,0.]);z=self.add("DIRECTION('',(0.,0.,1.))");x=self.add("DIRECTION('',(1.,0.,0.))")
        self.axis=self.add(f"AXIS2_PLACEMENT_3D('',#{point},#{z},#{x})")
    def add(self,s):
        self.lines.append(f'#{len(self.lines)+1}={s};\n');return len(self.lines)
    def point(self,p):
        nums=[]
        for value in p:
            s=format(float(value),'.15g').upper()
            if '.' not in s and 'E' not in s:s+='.'
            nums.append(s)
        return self.add("CARTESIAN_POINT('',("+','.join(nums)+'))')
    def mesh(self,mesh,name):
        vertices=[self.point(v) for v in mesh.vertices];faces=[]
        for j,f in enumerate(mesh.faces):
            loop=self.add("POLY_LOOP('',("+','.join('#'+str(vertices[int(i)]) for i in f)+'))')
            bound=self.add(f"FACE_OUTER_BOUND('',#{loop},.T.)")
            n=mesh.face_normals[j]
            normal=self.add("DIRECTION('',("+','.join(str(float(i)) for i in n)+'))')
            direction=mesh.vertices[f[1]]-mesh.vertices[f[0]]
            import numpy as np
            direction/=np.linalg.norm(direction)
            ref=self.add("DIRECTION('',("+','.join(str(float(i)) for i in direction)+'))')
            placement=self.add(f"AXIS2_PLACEMENT_3D('',#{vertices[int(f[0])]},#{normal},#{ref})")
            plane=self.add(f"PLANE('',#{placement})")
            faces.append(self.add(f"FACE_SURFACE('',(#{bound}),#{plane},.T.)"))
        shell=self.add("CLOSED_SHELL('',("+','.join('#'+str(i) for i in faces)+'))')
        solid=self.add(f"FACETED_BREP('{name}',#{shell})")
        product=self.add(f"PRODUCT('{name}','{name}','Mesh-derived reference', (#{self.pc}))")
        formation=self.add(f"PRODUCT_DEFINITION_FORMATION('','',#{product})")
        definition=self.add(f"PRODUCT_DEFINITION('design','',#{formation},#{self.dc})")
        pds=self.add(f"PRODUCT_DEFINITION_SHAPE('','',#{definition})")
        rep=self.add(f"FACETED_BREP_SHAPE_REPRESENTATION('{name}',(#{self.axis},#{solid}),#{self.context})")
        self.add(f'SHAPE_DEFINITION_REPRESENTATION(#{pds},#{rep})')
        self.add(f"PRODUCT_RELATED_PRODUCT_CATEGORY('part',$,(#{product}))")
    def write(self,path):
        header="""ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('Jumper mesh-derived faceted solid reference'),'2;1');
FILE_NAME('Jumper','2026-10-08T00:00:00',(''),(''),'Jumper faceted B-rep converter','', '');
FILE_SCHEMA(('AUTOMOTIVE_DESIGN { 1 0 10303 214 1 1 1 1 }'));
ENDSEC;
DATA;
"""
        Path(path).write_text(header+''.join(self.lines)+'ENDSEC;\nEND-ISO-10303-21;\n')
