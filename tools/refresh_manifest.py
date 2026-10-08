# SPDX-License-Identifier: Apache-2.0
"""Refresh hashes after reviewing intentional project changes."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
EXCLUDED={'provenance/artifact_manifest.json','provenance/release_validation.json'}
IGNORED={'.git','__pycache__','.venv','venv','cache','.pytest_cache','artifacts'}

def files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and not any(v in IGNORED for v in p.relative_to(ROOT).parts) and p.relative_to(ROOT).as_posix() not in EXCLUDED and not p.name.endswith(('.blend1','.blend2','.pyc','.tmp','.gcode','.log')))

def sha(path):
    value=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):value.update(chunk)
    return value.hexdigest()

if __name__=='__main__':
    rows=[]
    for p in files():
        rel=p.relative_to(ROOT).as_posix()
        provenance='unmodified_upstream_snapshot' if rel.startswith('upstream_snapshot/') and rel!='upstream_snapshot/source_manifest.json' else 'upstream_derived_geometry' if rel.startswith('geometry/') and p.suffix in {'.stl','.step','.glb'} else 'project_contribution_or_evidence'
        rows.append(dict(path=rel,bytes=p.stat().st_size,sha256=sha(p),provenance=provenance))
    target=ROOT/'provenance/artifact_manifest.json'
    target.write_text(json.dumps(dict(schema_version=1,license='Apache-2.0; upstream notices and external-reference distinctions apply',excluded_volatile_files=sorted(EXCLUDED),files=rows),indent=2)+'\n')
    print(f'Manifest refreshed: {len(rows)} files / {sum(r["bytes"] for r in rows)} bytes')
