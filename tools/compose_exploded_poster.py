# SPDX-License-Identifier: Apache-2.0
# Adapted for the independent Jumper Replica directory and pinned upstream snapshot.
"""Compose a high-resolution engineering poster with editable SVG annotations."""
from pathlib import Path
import json,base64,html,os
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'assembly'
W,H=6000,4800
CHINESE=os.getenv('JUMPER_CJK_FONT','/System/Library/Fonts/STHeiti Medium.ttc');SANS=os.getenv('JUMPER_SANS_FONT','/System/Library/Fonts/Helvetica.ttc');MONO=os.getenv('JUMPER_MONO_FONT','/System/Library/Fonts/SFNSMono.ttf')

def table(path):
 rows=[]
 for line in path.read_text().splitlines():
  if line.startswith('|') and not line.startswith(('|---','| ID','| Key')):
   rows.append([v.strip().strip('`') for v in line.strip('|').split('|')])
 return rows
texts=dict(table(OUT/'FIGURE_TEXT.zh.md'));labels={r[0]:(r[1],r[2]) for r in table(OUT/'LABELS.zh.md')}
manifest=json.loads((OUT/'scene_manifest.json').read_text());anchors=json.loads((OUT/'hero_anchors.json').read_text())
image=Image.new('RGB',(W,H),(250,251,253));draw=ImageDraw.Draw(image)
svg=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',f'<rect width="{W}" height="{H}" fill="#fafbfd"/>']

def rect(box,fill,outline=None,radius=0,width=1):
 if radius:draw.rounded_rectangle(box,radius,fill=fill,outline=outline,width=width)
 else:draw.rectangle(box,fill=fill,outline=outline,width=width)
 x,y,x2,y2=box;svg.append(f'<rect x="{x}" y="{y}" width="{x2-x}" height="{y2-y}" rx="{radius}" fill="{fill or "none"}" stroke="{outline or "none"}" stroke-width="{width}"/>')

def text(x,y,value,size=36,color='#263341',font=CHINESE):
 f=ImageFont.truetype(font,size);draw.text((x,y),value,font=f,fill=color)
 family='STHeiti, PingFang SC, Noto Sans CJK SC, sans-serif' if font==CHINESE else 'Helvetica, Arial, sans-serif' if font==SANS else 'SFMono, Consolas, monospace'
 svg.append(f'<text x="{x}" y="{y+size*.86}" font-family="{family}" font-size="{size}" fill="{color}">{html.escape(value)}</text>')

def line(points,color='#c1c8d0',width=2,dashed=False):
 if dashed:
  for a,b in zip(points,points[1:]):
   a=np.array(a,dtype=float);b=np.array(b,dtype=float);length=np.linalg.norm(b-a)
   for t in np.arange(0,length,22):
    p=a+(b-a)*t/max(length,1);q=a+(b-a)*min(t+11,length)/max(length,1);draw.line([tuple(p),tuple(q)],fill=color,width=width)
 else:draw.line(points,fill=color,width=width,joint='curve')
 svg.append('<polyline points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in points)+f'" fill="none" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="11 11"' if dashed else '')+'/>')

def circle(x,y,r,fill,outline=None,width=1):
 draw.ellipse((x-r,y-r,x+r,y+r),fill=fill,outline=outline,width=width)
 svg.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{outline or "none"}" stroke-width="{width}"/>')

def place(path,x,y,width=None,height=None):
 im=Image.open(path).convert('RGBA')
 if width is None:width,height=im.size
 else:im=im.resize((width,height),Image.Resampling.LANCZOS)
 image.paste(im,(x,y),im)
 data=base64.b64encode(path.read_bytes()).decode()
 svg.append(f'<image x="{x}" y="{y}" width="{width}" height="{height}" href="data:image/png;base64,{data}"/>')

# Editorial header with ample space and one strong color accent.
rect((100,105,120,327),'#bc2e38')
text(155,80,'JUMPER',148,'#202b36',SANS);text(950,145,texts['title'],86)
text(160,292,texts['subtitle'],39,'#687684')
text(4420,133,'MECHANICAL ASSEMBLY',35,'#485866',SANS)
text(4420,190,'SOURCE-BASED EXPLODED STUDY',26,'#84919d',SANS)
text(4420,245,'61d0652  /  OCT 2026',26,'#84919d',MONO)
line([(100,375),(5900,375)],'#d7dce2',2)
text(160,410,texts['groups']+'  ·  '+texts['links']+'  ·  '+texts['faces'],29,'#667581')
# Quiet background registration marks stay behind the geometry.
for x,y in [(2100,1000),(3900,1000),(2100,2900),(3900,2900)]:
 line([(x-20,y),(x+20,y)],'#e6ebef',2);line([(x,y-20),(x,y+20)],'#e6ebef',2)
place(OUT/'hero.png',1200,450,3600,3200)
# Balanced annotation banks; sorting by screen height avoids label-to-label crossings.
items=[i for i in manifest['items'] if i['label']]
items.sort(key=lambda i:anchors[i['id']][0]);left=items[:len(items)//2];right=items[len(items)//2:]
annotation_layout=[]
for side,bank in [('left',left),('right',right)]:
 bank.sort(key=lambda i:anchors[i['id']][1]);ymin,ymax,gap=590,3420,80
 desired=[450+anchors[i['id']][1]-28 for i in bank]
 ys=[]
 for y in desired:ys.append(max(ymin,y,ys[-1]+gap if ys else ymin))
 if ys[-1]>ymax:
  ys[-1]=ymax
  for k in range(len(ys)-2,-1,-1):ys[k]=min(ys[k],ys[k+1]-gap)
 assert ys[0]>=ymin and ys[-1]<=ymax
 for item,y in zip(bank,ys):
  ident=item['id'];source,name=labels[ident];x=140 if side=='left' else 4990;ax=1200+anchors[ident][0];ay=450+anchors[ident][1]
  endpoint=1130 if side=='left' else 4870
  elbow=1160 if side=='left' else 4840
  color='#bc2e38' if item['material']=='shell' else '#687b8e'
  line([(endpoint,y+24),(elbow,y+24),(ax,ay)],'#adb9c4',2)
  circle(ax,ay,5,'#fafbfd',color,2)
  rect((x,y+2,x+74,y+49),'#ffffff','#d1d9e0',9,2)
  text(x+8,y+8,ident,28,color,MONO)
  text(x+90,y+1,name,35)
  text(x+90,y+45,source,21,'#82909d',MONO)
  annotation_layout.append(dict(id=ident,source_id=source,label=name,bank=side,anchor=[ax,ay],label_top_left=[x,y]))
# Four inspection cards preserve the link between the exploded and assembled robot.
line([(100,3575),(5900,3575)],'#d7dce2',2)
cards=[('body_detail','body','A  /  BODY'),('front_detail','front','B  /  LF'),('leg_detail','leg','C  /  LM'),('assembled','assembled','D  /  HOME')]
for j,(file,key,english) in enumerate(cards):
 x=100+j*1470;y=3630
 rect((x,y,x+1390,y+950),'#ffffff','#dce2e8',24,2)
 text(x+35,y+26,english,25,'#b0323d',SANS);text(x+35,y+69,texts[key],43)
 place(OUT/(file+'.png'),x+25,y+133,1340,790)
 if file!='assembled':
  points=json.loads((OUT/(file+'_anchors.json')).read_text());taken=[]
  for ident,p in points.items():
   if ident not in labels:continue
   px=x+25+p[0]*1340/1450;py=y+133+p[1]*790/1050
   # Only compact IDs in detail panels; full names are in the main callouts.
   tx=px+10;ty=py-20
   for _ in range(20):
    if not any(abs(tx-a)<75 and abs(ty-b)<30 for a,b in taken):break
    ty+=30
   ty=min(y+908,max(y+142,ty));tx=min(x+1295,max(x+35,tx));taken.append((tx,ty))
   line([(px,py),(tx,ty+12)],'#b7c2cc',1);rect((tx-3,ty-1,tx+69,ty+28),'#ffffff',None,5);text(tx,ty,ident,23,'#4c6277',MONO)
text(120,4620,texts['footnote'],30,'#617180')
text(120,4670,texts['status'],29,'#7c8792')
text(4100,4642,'CYCLES / TRUE SOURCE MESH',25,'#7c8792',SANS)
text(4100,4688,'66 CALLOUTS · RIGID EXPANSION',25,'#7c8792',SANS)
svg.append('</svg>')
image.save(OUT/'Jumper_Exploded_Annotated.png',dpi=(300,300))
(OUT/'Jumper_Exploded_Annotated.svg').write_text('\n'.join(svg))
(OUT/'annotation_layout.json').write_text(json.dumps(annotation_layout,ensure_ascii=True,indent=2))
assert len(annotation_layout)==66 and len(set(a['id'] for a in annotation_layout))==66
preview=image.copy();preview.thumbnail((2400,1920));preview.save(OUT/'Jumper_Exploded_Preview.png')
print('Poster composed: 6000 x 4800, 66 unique bilingual source-mapped callouts')
