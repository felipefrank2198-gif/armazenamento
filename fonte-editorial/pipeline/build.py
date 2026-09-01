import json, re, collections
pages=json.load(open('raw.json'))

F_HEADER=(0.929,0.949,0.965); F_ZEBRA=(0.965,0.973,0.98); F_WHITE=(1.0,1.0,1.0)
CALLOUT={(0.933,0.961,0.984):'info',(1.0,0.969,0.902):'atencao',(1.0,0.945,0.945):'critico'}
HERO=(0.043,0.145,0.271)
ROWFILLS={F_HEADER,F_ZEBRA,F_WHITE}

def tup(f): return tuple(f)

blocks=[]   # flat stream of blocks in reading order
for pg in pages:
    n=pg['n']; spans=pg['spans']; rects=[dict(r, fill=tup(r['fill'])) for r in pg['rects']]
    wide=[r for r in rects if (r['x1']-r['x0'])>300]
    # regions
    regions=[]
    for r in wide:
        if r['fill'] in ROWFILLS: regions.append(('row',r))
        elif r['fill'] in CALLOUT: regions.append(('callout',r))
        elif r['fill']==HERO: regions.append(('hero',r))
    regions.sort(key=lambda z:(z[1]['y0'], z[1]['x0']))
    # merge rows into tables
    merged=[]; i=0
    while i<len(regions):
        kind,r=regions[i]
        if kind=='row':
            grp=[r]; j=i+1
            while j<len(regions) and regions[j][0]=='row' and regions[j][1]['y0']-grp[-1]['y1']<1.5:
                grp.append(regions[j][1]); j+=1
            merged.append(('table',grp)); i=j
        else:
            merged.append((kind,[r])); i+=1
    used=[False]*len(spans)
    def inside(s,r,pad=1.0):
        cy=(s['y0']+s['y1'])/2
        return r['x0']-pad<=s['x0']<=r['x1']+pad and r['y0']-pad<=cy<=r['y1']+pad
    items=[]
    for kind,grp in merged:
        y0=min(r['y0'] for r in grp); y1=max(r['y1'] for r in grp)
        sel=[k for k,s in enumerate(spans) if not used[k] and any(inside(s,r) for r in grp)]
        for k in sel: used[k]=True
        items.append((y0,kind,grp,[spans[k] for k in sel]))
    for k,s in enumerate(spans):
        if not used[k]: items.append((s['y0'],'span',None,[s]))
    items.sort(key=lambda z:z[0])
    for y0,kind,grp,ss in items:
        blocks.append(dict(page=n,y=y0,kind=kind,rects=grp,spans=ss))

json.dump(blocks, open('blocks.json','w'))
c=collections.Counter(b['kind'] for b in blocks)
print(c)
