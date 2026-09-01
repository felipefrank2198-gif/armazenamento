import json, re
S=json.load(open('sem.json'))
S=[b for b in S if b['page']>=13]   # skip front matter/TOC

def is_span(b,sz=None,bold=None,c=None):
    return b['type']=='span' and (sz is None or b['sz']==sz) and (bold is None or b['bold']==bold) and (c is None or b['c']==c)

doc={'chapters':[],'fichas':[]}
chap=None; quad=None; sect=None; mode='chapters'
i=0
pend_title=[]
def flush_title():
    global quad,sect
    return

def newsect(name):
    global sect
    sect={'header':name,'blocks':[]}
    quad['sections'].append(sect)

for b in S:
    if is_span(b,21.0,True):
        t=b['t'].strip()
        if t.startswith('Fichas'):
            mode='fichas'; chap=None; quad=None; sect=None
        else:
            m=re.match(r'(\d+)\s+(.*)',t)
            chap={'num':m.group(1),'title':m.group(2),'sub':'','quadros':[]}
            doc['chapters'].append(chap); quad=None; sect=None
        continue
    if is_span(b,15.3,True):
        t=b['t'].strip()
        # continuation of wrapped title?
        if quad is not None and not re.match(r'^([A-Z]?\d+[.]\d+|[A-Z]\d+[.])\s', t) and quad.get('_openTitle'):
            quad['title']+=' '+t; continue
        m=re.match(r'^([A-Z]?[\d.]+)[.]?\s+(.*)$', t)
        qid = m.group(1) if m else ''
        qtitle = m.group(2) if m else t
        quad={'id':qid.rstrip('.'),'title':qtitle,'tags':[],'intro':'','hero':[],'sections':[],'_openTitle':True,'page':b['page']}
        sect=None
        if mode=='fichas': doc['fichas'].append(quad)
        else: chap['quadros'].append(quad)
        continue
    if quad is None:
        # chapter subtitle
        if chap is not None and is_span(b,8.2) and not chap['sub']:
            chap['sub']=b['t'].strip()
        elif mode=='fichas' and is_span(b,8.2):
            doc.setdefault('fichas_intro','')
            doc['fichas_intro']=(doc['fichas_intro']+' '+b['t'].strip()).strip()
        continue
    quad['_openTitle']=False
    if is_span(b,5.8,True,'0xb2545') and not quad['sections'] and not quad['hero']:
        quad['tags'].append(b['t'].strip()); continue
    if is_span(b,8.2) and not quad['sections'] and not quad['hero']:
        quad['intro']=(quad['intro']+' '+b['t'].strip()).strip(); continue
    if b['type']=='hero':
        quad['hero']=b['fields']; continue
    if is_span(b,7.4,True,'0xb7285'):
        newsect(b['t'].strip()); continue
    if sect is None: newsect('')
    if b['type']=='table': sect['blocks'].append({'t':'table','headers':b['headers'],'rows':b['rows']})
    elif b['type']=='callout': sect['blocks'].append({'t':'callout','sev':b['sev'],'title':b['title'],'body':b['body']})
    else:
        bold=b['bold']; txt=b['t'].strip()
        blk=sect['blocks']
        if bold and b['sz']==7.1:
            blk.append({'t':'sub','text':txt})
        elif txt.startswith('•'):
            if blk and blk[-1]['t']=='ul': blk[-1]['items'].append(txt.lstrip('• ').strip())
            else: blk.append({'t':'ul','items':[txt.lstrip('• ').strip()]})
        else:
            if blk and blk[-1]['t']=='ul' and b['sz'] in (7.1,5.8) and not txt.startswith('http'):
                blk[-1]['items'][-1]+=' '+txt
            elif blk and blk[-1]['t']=='p' and blk[-1].get('sz')==b['sz']:
                blk[-1]['text']+=' '+txt
            else:
                blk.append({'t':'p','text':txt,'sz':b['sz'],'c':b['c']})

def clean(o):
    if isinstance(o,dict): return {k:clean(v) for k,v in o.items() if k!='_openTitle'}
    if isinstance(o,list): return [clean(x) for x in o]
    return o
doc=clean(doc)
json.dump(doc,open('doc.json','w'),ensure_ascii=False,indent=1)
print('chapters',len(doc['chapters']),'quadros',sum(len(c['quadros']) for c in doc['chapters']),'fichas',len(doc['fichas']))
for c in doc['chapters']: print(' ',c['num'],c['title'],len(c['quadros']))
