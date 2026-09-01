import json, re, collections
blocks=json.load(open('blocks.json'))
F_HEADER=[0.929,0.949,0.965]

def celltext(ss):
    if not ss: return ''
    ss=sorted(ss,key=lambda s:(round(s['y0'],1), s['x0']))
    lines=[]; cur=[]; cy=None
    for s in ss:
        if cy is None or abs(s['y0']-cy)<2.0:
            cur.append(s); cy=s['y0'] if cy is None else cy
        else:
            lines.append(cur); cur=[s]; cy=s['y0']
    if cur: lines.append(cur)
    out=[]
    for ln in lines:
        out.append(''.join(x['t'] for x in sorted(ln,key=lambda z:z['x0'])).strip())
    txt=''
    for i,l in enumerate(out):
        if not txt: txt=l
        elif txt.endswith('-') and not txt.endswith(' -'): txt=txt[:-1]+l
        else: txt=txt+' '+l
    return re.sub(r'\s+',' ',txt).strip()

def parse_table(b):
    rects=b['rects']; spans=b['spans']
    hdr=rects[0]
    hs=[s for s in spans if hdr['y0']-1<=(s['y0']+s['y1'])/2<=hdr['y1']+1]
    cols=sorted({round(s['x0'],0) for s in hs})
    # merge near-duplicate col positions
    merged=[]
    for c in cols:
        if merged and c-merged[-1]<6: continue
        merged.append(c)
    cols=merged
    if not cols: cols=[51.0]
    def colidx(x):
        best=0
        for i,c in enumerate(cols):
            if x>=c-3: best=i
        return best
    headers=['']*len(cols)
    for s in hs: headers[colidx(s['x0'])]=(headers[colidx(s['x0'])]+s['t']).strip()
    rows=[]
    for r in rects[1:]:
        rs=[s for s in spans if r['y0']-1<=(s['y0']+s['y1'])/2<=r['y1']+1]
        if not rs: continue
        cells=[[] for _ in cols]
        for s in rs: cells[colidx(s['x0'])].append(s)
        rows.append([celltext(c) for c in cells])
    return dict(headers=headers, rows=rows)

def parse_callout(b):
    ss=sorted(b['spans'],key=lambda s:(round(s['y0'],1),s['x0']))
    if not ss: return None
    title=''; body=[]
    first_y=ss[0]['y0']
    tspans=[s for s in ss if abs(s['y0']-first_y)<2]
    title=''.join(s['t'] for s in tspans).strip()
    rest=[s for s in ss if abs(s['y0']-first_y)>=2]
    body=celltext(rest)
    fill=tuple(b['rects'][0]['fill'])
    sev={ (0.933,0.961,0.984):'info',(1.0,0.969,0.902):'atencao',(1.0,0.945,0.945):'critico'}.get(tuple(round(x,3) for x in fill),'info')
    return dict(sev=sev,title=title,body=body)

def parse_hero(b):
    ss=b['spans']
    out={}
    # label spans are bold small light-blue 0x9fd5e0
    labels=[s for s in ss if s['c']=='0x9fd5e0']
    labels.sort(key=lambda s:(s['x0'],s['y0']))
    # group by column x
    colx=sorted({round(s['x0'],0) for s in labels})
    if not colx: return [dict(label='', value=celltext(ss))]
    groups=collections.defaultdict(list)
    for s in ss:
        cx=min(colx,key=lambda c: abs(s['x0']-c) if s['x0']>=c-4 else 1e9)
        groups[cx].append(s)
    fields=[]
    for cx in colx:
        col=sorted(groups[cx],key=lambda s:s['y0'])
        cur=None
        for s in col:
            if s['c']=='0x9fd5e0':
                if cur: fields.append(cur)
                cur=dict(label=s['t'].strip(),spans=[])
            elif cur is not None: cur['spans'].append(s)
        if cur: fields.append(cur)
    out=[]
    for f in fields:
        big=[x for x in f['spans'] if x['sz']>=12]
        small=[x for x in f['spans'] if x['sz']<12]
        out.append(dict(label=f['label'], value=celltext(f['spans']),
                        title=celltext(big), detail=celltext(small)))
    return out

out=[]
for b in blocks:
    if b['kind']=='table': out.append(dict(page=b['page'],y=b['y'],type='table',**parse_table(b)))
    elif b['kind']=='callout':
        c=parse_callout(b)
        if c: out.append(dict(page=b['page'],y=b['y'],type='callout',**c))
    elif b['kind']=='hero': out.append(dict(page=b['page'],y=b['y'],type='hero',fields=parse_hero(b)))
    else:
        s=b['spans'][0]
        out.append(dict(page=b['page'],y=b['y'],type='span',sz=s['sz'],c=s['c'],bold='Bold' in s['f'],t=s['t']))
json.dump(out,open('sem.json','w'),ensure_ascii=False)
print(len(out))
