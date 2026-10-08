# SPDX-License-Identifier: Apache-2.0
# Adapted for the independent Jumper Replica directory and pinned upstream snapshot.
"""Embed the complete reference INI using PrusaSlicer's 3MF print-config format."""
from pathlib import Path
import zipfile
ROOT=Path(__file__).resolve().parents[1]
folder=ROOT/'printing/slicer'
config='; Jumper reference study only; actual printer unspecified\n'+''.join('; '+line+'\n' for line in (folder/'reference_fff.ini').read_text().splitlines() if line and not line.startswith('#'))
for path in folder.glob('*.3mf'):
    with zipfile.ZipFile(path) as archive:
        entries={n:archive.read(n) for n in archive.namelist() if n!='Metadata/Slic3r_PE.config'}
    entries['Metadata/Slic3r_PE.config']=config.encode()
    temp=path.with_suffix('.tmp')
    with zipfile.ZipFile(temp,'w',zipfile.ZIP_DEFLATED) as archive:
        for name,data in entries.items():archive.writestr(name,data)
    temp.replace(path)
