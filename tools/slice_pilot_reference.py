# SPDX-License-Identifier: Apache-2.0
# Adapted for the independent Jumper Replica directory and pinned upstream snapshot.
"""Reference-only FFF slices; no real printer has been selected."""
from pathlib import Path
import subprocess
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'printing'
BIN = Path(sys.argv[1])
CONFIG = OUT/'slicer/reference_fff.ini'
OVERRIDES = '''# Reference geometry study only. Bind actual printer before printing.
bed_shape = 0x0,220x0,220x220,0x220
max_print_height = 250
nozzle_diameter = 0.4
filament_diameter = 1.75
filament_density = 1.24
filament_type = PLA
layer_height = 0.2
first_layer_height = 0.2
perimeters = 3
top_solid_layers = 5
bottom_solid_layers = 5
fill_density = 15%
fill_pattern = gyroid
perimeter_generator = arachne
support_material = 1
support_material_auto = 1
support_material_style = snug
support_material_threshold = 45
support_material_contact_distance = 0.2
support_material_xy_spacing = 0.3
brim_width = 5
skirts = 0
temperature = 205
first_layer_temperature = 205
bed_temperature = 60
first_layer_bed_temperature = 60
perimeter_speed = 40
external_perimeter_speed = 25
infill_speed = 50
solid_infill_speed = 40
top_solid_infill_speed = 30
support_material_speed = 40
bridge_speed = 25
first_layer_speed = 20
travel_speed = 120
retract_length = 0.8
retract_speed = 30
gcode_flavor = marlin2
start_gcode = ; REFERENCE ONLY: actual machine start code is intentionally unspecified
end_gcode = ; REFERENCE ONLY: actual machine end code is intentionally unspecified
'''

def main():
    overrides = OUT/'slicer/reference_overrides.ini'; overrides.write_text(OVERRIDES)
    base = [str(BIN), '--datadir', str(Path(__import__('tempfile').gettempdir())/'jumper-replica-prusa-data'), '--threads', '4']
    saved = subprocess.run(base+['--load',str(overrides),'--save',str(CONFIG)],capture_output=True,text=True)
    (OUT/'slicer/config_export.log').write_text(saved.stdout+saved.stderr)
    saved.check_returncode()
    results=[]
    for stl in sorted((OUT/'oriented_stl').glob('*.stl')):
        name=stl.stem; print('Slicing '+name,flush=True)
        gcode=ROOT/'experiments/reference_gcode'/f'{name}.REFERENCE_ONLY.gcode'
        gcode.parent.mkdir(parents=True,exist_ok=True)
        project=OUT/'slicer'/f'{name}.3mf'
        run=subprocess.run(base+['--load',str(CONFIG),'--center','110,110','--export-gcode','--output',str(gcode),str(stl)],capture_output=True,text=True)
        (OUT/'slicer'/f'{name}.log').write_text(run.stdout+run.stderr)
        # Export the editable project separately from the G-code output.
        export=subprocess.run(base+['--load',str(CONFIG),'--center','110,110','--export-3mf','--output',str(project),str(stl)],capture_output=True,text=True)
        (OUT/'slicer'/f'{name}.project.log').write_text(export.stdout+export.stderr)
        result=dict(part=name,returncode=run.returncode,project_returncode=export.returncode)
        if run.returncode==0 and gcode.exists():
            data=gcode.read_text()
            result['layer_changes']=data.count(';LAYER_CHANGE')
            result['extruding_moves']=len(re.findall(r'^G1 .*\bE[-\d.]',data,re.M))
            result['support_sections']=data.count(';TYPE:Support material')
            result['estimates']=[line[2:] for line in data.splitlines() if line.startswith(('; filament used','; estimated printing time','; total filament'))]
            result['bytes']=gcode.stat().st_size
            result['gcode_sha256']=__import__('hashlib').sha256(gcode.read_bytes()).hexdigest()
            assert result['layer_changes']>0 and result['extruding_moves']>0
        results.append(result)
        print(json.dumps(result),flush=True)
    (OUT/'slicing_checks.json').write_text(json.dumps(dict(slicer_version='PrusaSlicer 2.9.6',dmg_sha256='94fd7b8a9f87c9631e1c71739b15b184fc5f4c0ceabd69072f1c78f229a4fe40',
        status='Reference only; actual hardware and start/end code unspecified',raw_toolpaths_in_public_package=False,results=results),indent=2))
    assert all(r['returncode']==0 and r['project_returncode']==0 for r in results)

if __name__=='__main__':
    main()
