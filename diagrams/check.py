"""Geometry checker for diagrams/architecture.svg.

Uses the Inter subsets embedded in the SVG to measure every <text> run with the
exact metrics browsers will use, then fails if any text overflows its box, any
line segment crosses any text, or two text runs overlap.

    pip install fonttools brotli && python3 diagrams/check.py diagrams/architecture.svg
"""
import re, sys, io, base64
from fontTools.ttLib import TTFont
SVG=sys.argv[1]
_svg=open(SVG).read()
fonts={}
for m in re.finditer(r"font-weight:(\d+);src:url\(data:font/woff2;base64,([A-Za-z0-9+/=]+)\)",_svg):
    fonts[int(m.group(1))]=TTFont(io.BytesIO(base64.b64decode(m.group(2))))
assert 400 in fonts and 600 in fonts, "embedded Inter 400/600 not found"
def width(txt,size,weight,ls=0):
    f=fonts[weight]; cmap=f.getBestCmap(); hmtx=f['hmtx']; upm=f['head'].unitsPerEm
    w=0
    for ch in txt:
        g=cmap.get(ord(ch)) or cmap.get(ord('x')); w+=hmtx[g][0]
    return w*size/upm + ls*len(txt)
s=open(SVG).read()
cls={'bandt':(13,600,.4,True),'h':(14,600,0,False),'s':(12,400,0,False),'m':(11,400,0,False),'lbl':(11,400,0,False)}
texts=[]
for m in re.finditer(r'<text([^>]*)>(.*?)</text>',s):
    a,t=m.group(1),m.group(2)
    t=t.replace('&amp;','&')
    x=float(re.search(r'x="([\d.]+)"',a).group(1)); y=float(re.search(r'y="([\d.]+)"',a).group(1))
    c=re.search(r'class="(\w+)"',a); 
    if c: size,wt,ls,up=cls[c.group(1)]
    else:
        fs=re.search(r'font-size="([\d.]+)"',a); size=float(fs.group(1)) if fs else 11; wt=600 if 'font-weight="600"' in a else 400; ls=0; up=False
    if up: t=t.upper()
    anc=re.search(r'text-anchor="(\w+)"',a); anc=anc.group(1) if anc else 'start'
    if 'transform' in a: continue
    w=width(t,size,wt,ls)
    x0= x-w/2 if anc=='middle' else (x-w if anc=='end' else x)
    texts.append(dict(t=t,x0=x0,x1=x0+w,y0=y-size*0.75,y1=y+size*0.25,cls=c.group(1) if c else 'raw'))
rects=[]
for m in re.finditer(r'<rect class="box[^"]*" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"',s):
    x,y,w,h=map(float,m.groups()); rects.append((x,y,x+w,y+h))
# cylinder + pill approximations
rects.append((252,580,372,670)); rects.append((120,24,380,64))
PAD=8; bad=0
for t in texts:
    if t['cls'] in ('lbl','bandt','raw'): continue
    cx=(t['x0']+t['x1'])/2; cy=(t['y0']+t['y1'])/2
    box=[r for r in rects if r[0]<=cx<=r[2] and r[1]<=cy<=r[3]]
    if not box: print(f"NOBOX  {t['t']!r}"); bad+=1; continue
    r=box[0]
    if t['x0']<r[0]+PAD or t['x1']>r[2]-PAD:
        print(f"OVERFLOW {t['t']!r}: text {t['x0']:.0f}-{t['x1']:.0f} vs box {r[0]:.0f}-{r[2]:.0f} (need +{max(r[0]+PAD-t['x0'],t['x1']-r[2]+PAD):.0f}px)"); bad+=1
# line segments vs text bboxes
segs=[]
for m in re.finditer(r'<path class="l[d]?" d="([^"]+)"',s):
    pts=re.findall(r'([ML])\s*([\d.]+)\s+([\d.]+)',m.group(1)); pts=[(float(x),float(y)) for _,x,y in pts]
    for a,b in zip(pts,pts[1:]): segs.append((a,b,m.group(1)))
def hit(seg,t,pad=2):
    (x1,y1),(x2,y2),_=seg; X0,X1,Y0,Y1=t['x0']-pad,t['x1']+pad,t['y0']-pad,t['y1']+pad
    if x1==x2: return X0<=x1<=X1 and min(y1,y2)<Y1 and max(y1,y2)>Y0
    if y1==y2: return Y0<=y1<=Y1 and min(x1,x2)<X1 and max(x1,x2)>X0
    return False
for seg in segs:
    for t in texts:
        if hit(seg,t): print(f"LINE-THROUGH-TEXT {t['t']!r} by seg {seg[0]}->{seg[1]}"); bad+=1
# text-vs-text overlap (labels)
for i,a in enumerate(texts):
    for b in texts[i+1:]:
        if a['x0']<b['x1'] and b['x0']<a['x1'] and a['y0']<b['y1'] and b['y0']<a['y1']:
            print(f"TEXT-OVERLAP {a['t']!r} / {b['t']!r}"); bad+=1
print("issues:",bad); sys.exit(1 if bad else 0)
