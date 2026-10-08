# SPDX-License-Identifier: Apache-2.0
"""Offline validation of release integrity, provenance and model mappings."""
from pathlib import Path
import ast,csv,json,re,struct,sys,zipfile,xml.etree.ElementTree as ET
from urllib.parse import unquote
from refresh_manifest import ROOT,files,sha


def read(path):return json.loads((ROOT/path).read_text(encoding='utf-8'))
def csv_rows(path):return list(csv.DictReader((ROOT/path).open(encoding='utf-8-sig')))
def require(condition,message):
    if not condition:raise ValueError(message)

def triangles(path):
    with path.open('rb') as f:header=f.read(84)
    require(len(header)==84,f'Invalid STL header: {path}')
    count=struct.unpack_from('<I',header,80)[0]
    require(path.stat().st_size==84+50*count,f'STL length mismatch: {path}')
    return count

def main():
    manifest=read('provenance/artifact_manifest.json');rows=manifest['files'];known={r['path'] for r in rows};current={p.relative_to(ROOT).as_posix() for p in files()}
    require(known==current,'File inventory differs from reviewed artifact manifest; review changes before refreshing')
    for r in rows:
        p=ROOT/r['path'];require(p.stat().st_size==r['bytes'] and sha(p)==r['sha256'],f'Artifact checksum mismatch: {r["path"]}')
    source=read('upstream_snapshot/source_manifest.json')
    require(source['commit']=='61d065219fca767f3142c8f10aff59eae5a5a004','Unexpected upstream pin')
    for r in source['files']:require(sha(ROOT/'upstream_snapshot'/r['path'])==r['sha256'],f'Upstream source changed: {r["path"]}')
    parts=csv_rows('geometry/parts_manifest.csv');components=csv_rows('geometry/components_manifest.csv');by_id={r['id']:r for r in components}
    require(len(parts)==41 and len(components)==1364,'Unexpected geometry inventory')
    total=0
    for r in parts:
        require(sha(ROOT/'upstream_snapshot'/r['source'])==r['source_sha256'],f'Source mapping/hash mismatch: {r["link"]}')
        n=triangles(ROOT/'geometry/links_mm'/(r['link']+'.stl'));require(n==int(r['triangles']),'Link face mismatch');total+=n
    require(total==430915,'Source triangle total changed')
    for r in components:
        p=ROOT/'geometry'/r['stl'];require(sha(p)==r['sha256'] and triangles(p)==int(r['triangles']),f'Component mismatch: {r["id"]}')
    require(sum(int(r['triangles']) for r in components)==total,'Component split lost/added triangles')
    for link in parts:require(sum(int(r['triangles']) for r in components if r['link']==link['link'])==int(link['triangles']),f'Link split mismatch: {link["link"]}')
    recoveries=read('geometry/seam_recovery_validation.json');closed=[r for r in recoveries if r['status']=='closed_after_vertex_only_weld']
    require(len(closed)==13,'Recovery count differs')
    for r in closed:
        p=ROOT/'geometry'/r['output'];require(sha(p)==r['output_sha256'] and triangles(p)==r['original_faces'],f'Recovered geometry mismatch: {r["id"]}')
        require(not r['hole_filling'] and not r['face_deletion'],'Unexpected destructive seam operation')
    step_reports=read('geometry/step_validation.json')+read('geometry/step_seam_validation.json')
    require(len(step_reports)==46 and len(list((ROOT/'geometry/step_trials').glob('*.step')))==46,'STEP inventory differs')
    for r in step_reports:
        require(r['status']=='passed_conversion' and r['is_valid_brep'] and r['solids']==1,f'STEP conversion not accepted: {r["id"]}')
        p=ROOT/'geometry/step_trials'/(r['id']+'.step');require(sha(p)==r['step_sha256'],f'STEP hash mismatch: {r["id"]}')
        stl=ROOT/'geometry/seam_recovered_mm'/(r['id']+'.stl') if (ROOT/'geometry/seam_recovered_mm'/(r['id']+'.stl')).exists() else ROOT/'geometry'/by_id[r['id']]['stl']
        require(sha(stl)==r['source_sha256'],f'STEP input mapping changed: {r["id"]}')
    slices=read('printing/slicing_checks.json')['results'];require(len(slices)==6 and all(r['returncode']==r['project_returncode']==0 and r['extruding_moves']>0 for r in slices),'Incomplete reference slicing evidence')
    for r in slices:
        require(re.fullmatch(r'[0-9a-f]{64}',r['gcode_sha256']) and r['bytes']>0 and r['layer_changes']>0,f'Incomplete archived toolpath evidence: {r["part"]}')
        gcode=ROOT/'experiments/reference_gcode'/(r['part']+'.REFERENCE_ONLY.gcode')
        if gcode.exists():require(sha(gcode)==r['gcode_sha256'],f'Local reference toolpath hash differs: {r["part"]}')
        project=ROOT/'printing/slicer'/(r['part']+'.3mf')
        with zipfile.ZipFile(project) as z:
            require(z.testzip() is None,f'3MF CRC failure: {project.name}')
            config=z.read('Metadata/Slic3r_PE.config').decode();require('layer_height = 0.2' in config and 'nozzle_diameter = 0.4' in config,'3MF profile mismatch')
    scene=read('assembly/scene_manifest.json');layout=read('assembly/annotation_layout.json');catalog=read('catalog/annotated_groups.json')
    intended={i['id'] for i in scene['items'] if i['label']}
    require(len(intended)==66 and intended=={i['id'] for i in layout}=={i['annotation_id'] for i in catalog},'Annotation/catalog mapping differs')
    require(len(scene['items'])==88 and sum(triangles(ROOT/'assembly'/i['mesh']) for i in scene['items'])==430915,'Exploded geometry differs')
    for r in catalog:require((ROOT/r['geometry_path']).exists(),f'Catalog source missing: {r["source_id"]}')
    require(read('assembly/render_geometry_checks.json')['blender_faces']==430915 and read('assembly/blend_readback_validation.json')['faces']==430915,'Blender evidence incomplete')
    for p in (ROOT/'tools').glob('*.py'):ast.parse(p.read_text(encoding='utf-8'))
    translations=0;link_count=0
    for p in ROOT.rglob('*.md'):
        if 'upstream_snapshot' in p.parts:continue
        text=p.read_text(encoding='utf-8')
        if p.name.endswith('.zh.md'):
            source_path=p.with_name(p.name.replace('.zh.md','.md'));require(source_path.exists() and f'tracks: {source_path.name} @ sha256:{sha(source_path)}' in text,f'Stale translation: {p.relative_to(ROOT)}');translations+=1
        text=re.sub(r'```.*?```','',text,flags=re.S)
        for target in re.findall(r'\[[^\]]*\]\(([^)]+)\)',text):
            if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:',target) or target.startswith('#'):continue
            target=unquote(target.split('#')[0].split(' "')[0].strip('<>'))
            require((p.parent/target).exists(),f'Broken local link: {p.relative_to(ROOT)} -> {target}');link_count+=1
    forbidden=[p for p in files() if p.name in {'.env','id_rsa','id_ed25519'} or p.suffix in {'.dmg','.ttf','.ttc','.otf'} or (p.parent==ROOT/'external_references' and p.suffix in {'.step','.stp'})]
    require(not forbidden,'Excluded vendor/binary/font/credential files present')
    privacy_patterns=[rb'/(?:Users|home)/[^/\s"<>]+',rb'/private/(?:tmp|var)/',rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',rb'gh[pousr]_[A-Za-z0-9]{20,}',rb'github_pat_[A-Za-z0-9_]{20,}',rb'AKIA[A-Z0-9]{16}',rb'sk-proj-[A-Za-z0-9_-]{20,}']
    for p in files():
        payloads=[p.read_bytes()]
        if p.suffix=='.3mf':
            with zipfile.ZipFile(p) as z:payloads.extend(z.read(n) for n in z.namelist())
        require(not any(re.search(pattern,payload) for pattern in privacy_patterns for payload in payloads),f'Private path/credential marker in release file: {p.relative_to(ROOT)}')
    largest=max(rows,key=lambda r:r['bytes']);require(largest['bytes']<100*1024*1024,'Single file exceeds ordinary GitHub file limit; review hosting strategy')
    status=read('provenance/project_status.json');require(status['physical_fit']=='not_tested' and status['complete_manufacturing_bom']=='not_available','Unexpected manufacturing readiness claim')
    report=dict(status='passed_integrity_and_provenance',artifact_files=len(rows),artifact_bytes=sum(r['bytes'] for r in rows),source_files=len(source['files']),source_commit=source['commit'],links=41,components=1364,source_triangles=430915,validated_step_records=46,configured_3mf=6,annotation_groups=66,translation_pairs=translations,local_links_checked=link_count,largest_file=largest,physical_validation='not_performed',note='STEP validity evidence is hash-verified from earlier CAD-kernel runs; raw reference toolpaths are excluded, with slicing results and digests retained')
    (ROOT/'provenance/release_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))

if __name__=='__main__':
    try:main()
    except (ValueError,AssertionError,FileNotFoundError,KeyError,zipfile.BadZipFile) as e:
        print(f'VALIDATION FAILED: {e}',file=sys.stderr);sys.exit(1)
