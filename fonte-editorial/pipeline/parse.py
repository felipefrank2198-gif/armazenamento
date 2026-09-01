import pymupdf, json, re, collections

SRC='/home/user/armazenamento/Antibioticoterapia_no_Plantao_Edicao_3_1_Revisada_Compacta.pdf'
d=pymupdf.open(SRC)

HDR_Y=40; FTR_Y=805
F_HEADER=(0.929,0.949,0.965)
F_ZEBRA=(0.965,0.973,0.98)
F_WHITE=(1.0,1.0,1.0)
CALLOUT={(0.933,0.961,0.984):'info',(1.0,0.969,0.902):'atencao',(1.0,0.945,0.945):'critico'}
HERO=(0.043,0.145,0.271)
CHIPS={(0.902,0.965,0.969),(0.925,0.992,0.961),(0.929,0.949,0.965)}

def rr(f): return tuple(round(x,3) for x in f)

pages=[]
for pno,p in enumerate(d, start=1):
    spans=[]
    for b in p.get_text('dict')['blocks']:
        if b['type']!=0: continue
        for l in b['lines']:
            for s in l['spans']:
                y=s['bbox'][1]
                if y<HDR_Y or y>FTR_Y: continue
                t=s['text']
                if not t.strip(): continue
                spans.append(dict(x0=s['bbox'][0],y0=s['bbox'][1],x1=s['bbox'][2],y1=s['bbox'][3],
                                  f=s['font'],sz=round(s['size'],1),c=hex(s['color']),t=t))
    rects=[]
    for dr in p.get_drawings():
        if not dr['fill']: continue
        r=dr['rect']
        if r.y1<HDR_Y or r.y0>FTR_Y: continue
        rects.append(dict(fill=rr(dr['fill']), x0=r.x0,y0=r.y0,x1=r.x1,y1=r.y1))
    pages.append(dict(n=pno,spans=spans,rects=rects))

json.dump(pages, open('raw.json','w'))
print('pages',len(pages),'spans',sum(len(p['spans']) for p in pages))
