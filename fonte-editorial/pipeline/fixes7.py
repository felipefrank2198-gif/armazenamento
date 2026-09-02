# -*- coding: utf-8 -*-
"""Etapa 7 — apresentações realmente disponíveis no Brasil."""
import json, re
doc = json.load(open('doc_final.json'))
LOG = json.load(open('log_final.json'))
def log(sev,esc,ach,cor): LOG.append(dict(sev=sev,escopo=esc,achado=ach,correcao=cor))

def sub_all(pat, rep, count=[0]):
    n=0
    def fn(o):
        nonlocal n
        it = o.items() if isinstance(o,dict) else enumerate(o)
        for k,v in list(it):
            if isinstance(v,str):
                v2=re.sub(pat,rep,v)
                if v2!=v: n+=1; o[k]=v2
            elif isinstance(v,(dict,list)): fn(v)
    fn(doc); return n
def q(qid):
    for c in doc['chapters']:
        for x in c['quadros']:
            if x['id']==qid: return x
    for x in doc['fichas']:
        if x['id']==qid: return x
    raise KeyError(qid)
def sec(qid,p):
    for s in q(qid)['sections']:
        if s['header'].startswith(p): return s
    raise KeyError(qid+p)
def table(qid,p):
    for b in sec(qid,p)['blocks']:
        if b['t']=='table': return b
    raise KeyError(qid+p)
def row(qid,p,key):
    for r in table(qid,p)['rows']:
        if r[0].strip()==key: return r
    raise KeyError(f'{qid}/{p}/{key}')
def drug(qid,name):
    for s in q(qid)['sections']:
        for b in s['blocks']:
            if b['t']=='drugs':
                for d in b['rows']:
                    if d['nome'].strip()==name: return d
    raise KeyError(f'{qid}/{name}')
def add_callout(qid, sev, title, body, pos=0):
    sec(qid,'ALERTAS')['blocks'].insert(pos, {'t':'callout','sev':sev,'title':title,'body':body})

# =====================================================================
# 1. AMOXICILINA-CLAVULANATO 2 g/125 mg (XR) — não existe no Brasil
# =====================================================================
ALTA = ('875/125 mg VO 12/12 h; quando for necessária maior exposição à amoxicilina, '
        'associar amoxicilina isolada 500–875 mg VO 12/12 h em vez de aumentar o clavulanato')
n  = sub_all(r'2 g/125 mg VO 12/12 h \(XR, quando disponível\)', ALTA)
n += sub_all(r'2 g/125 mg VO 12/12 h \(XR\)', ALTA)
n += sub_all(r'Amox\+Clav XR 2 g/125 mg VO 12/12 h por 7 dias, se disponível\.',
             'Amoxicilina-clavulanato 875/125 mg VO 12/12 h por 7 dias, associando amoxicilina isolada 875 mg VO 12/12 h '
             'quando houver risco de pneumococo com sensibilidade reduzida.')
n += sub_all(r'875/125 mg VO 12/12 h ou 2 g/125 mg VO 12/12 h',
             '875/125 mg VO 12/12 h ou 500/125 mg VO 8/8 h')
n += sub_all(r'amoxicilina-clavulanato 2 g/125 mg VO 12/12 h', 'amoxicilina-clavulanato 875/125 mg VO 12/12 h')
n += sub_all(r'Grave: 2 g/125 mg VO 12/12 h(?! \()', 'Grave: ' + ALTA)
n += sub_all(r'\(XR\)', '')
n += sub_all(r'2 g/125 mg', '875/125 mg')
r = row('1.1','ALTERNATIVAS','Falha com amoxicilina')
r[3] = ('Provavelmente H. influenzae ou MSSA produtor de betalactamase. No Brasil não há a apresentação de '
        '2000/125 mg (XR): as apresentações orais são 500/125 mg e 875/125 mg.')
log('A','1.1, 1.3, 1.4, 1.5 e 1.6 — amoxicilina-clavulanato',
 'O livro prescrevia amoxicilina-clavulanato "2 g/125 mg VO 12/12 h (XR)" em treze pontos, inclusive como esquema de '
 'transição oral da pneumonia e como dose alta da sinusite. Essa apresentação de liberação prolongada não tem registro '
 'no Brasil: as apresentações orais disponíveis são 500/125 mg e 875/125 mg, e as suspensões 250/62,5 e 400/57 mg por 5 mL.',
 'Substituída pela posologia possível no Brasil: 875/125 mg VO 12/12 h (ou 500/125 mg VO 8/8 h). Onde a intenção era '
 'aumentar a exposição à amoxicilina, o esquema passa a associar amoxicilina isolada 500–875 mg VO 12/12 h, sem elevar '
 'o clavulanato — que é o fator limitante de tolerância.')

# =====================================================================
# 2. AMOXICILINA-CLAVULANATO PEDIÁTRICO — teto do clavulanato
# =====================================================================
r = row('14.2','ESQUEMAS','Amoxicilina nos últimos 30 dias, conjuntivite purulenta ou falha inicial')
r[1] = ('Amoxicilina + Clavulanato · até 70 mg/kg/dia de amoxicilina VO 12/12 h (suspensão 400/57 mg/5 mL); '
        'completar com amoxicilina isolada para atingir 80–90 mg/kg/dia · VO')
r[3] = ('Escolha quando houver maior chance de H. influenzae/Moraxella produtores de betalactamase. '
        'No Brasil não existe a suspensão 14:1 (600/42,9 mg/5 mL): com a suspensão 400/57 mg/5 mL, 90 mg/kg/dia de '
        'amoxicilina levaria o clavulanato a ~12,8 mg/kg/dia. Manter o clavulanato em até 10 mg/kg/dia e completar a '
        'amoxicilina com o produto isolado.')
d = drug('14.2','Amoxicilina + Clavulanato')
d['padrao'] = 'até 70 mg/kg/dia de amoxicilina VO 12/12 h (suspensão 400/57 mg/5 mL)'
d['grave']  = 'completar com amoxicilina isolada até 80–90 mg/kg/dia, mantendo o clavulanato em até 10 mg/kg/dia'
r = row('14.3','ESQUEMAS','Sinusite bacteriana persistente, grave ou com piora bifásica')
r[1] = ('Amoxicilina ± Clavulanato · 45 mg/kg/dia de amoxicilina VO 12/12 h; se risco de resistência ou gravidade, '
        '80–90 mg/kg/dia — com a suspensão brasileira 400/57 mg/5 mL, dar até 70 mg/kg/dia pelo clavulanato e '
        'completar com amoxicilina isolada · VO')
d = drug('14.3','Amoxicilina + Clavulanato')
d['padrao'] = '45 mg/kg/dia de amoxicilina VO 12/12 h'
d['grave']  = ('80–90 mg/kg/dia de amoxicilina: até 70 mg/kg/dia pela suspensão 400/57 mg/5 mL e o restante com '
               'amoxicilina isolada, mantendo o clavulanato em até 10 mg/kg/dia')
add_callout('14.2','atencao','ATENÇÃO · DOSE ALTA DE AMOXICILINA-CLAVULANATO NO BRASIL',
 'A dose alta descrita nas diretrizes norte-americanas (90 mg/kg/dia de amoxicilina com 6,4 mg/kg/dia de clavulanato) '
 'depende da suspensão 600/42,9 mg/5 mL, na proporção 14:1, que não existe no Brasil. Com a suspensão disponível aqui '
 '(400/57 mg/5 mL, proporção 7:1), 90 mg/kg/dia de amoxicilina levariam o clavulanato a cerca de 12,8 mg/kg/dia, acima '
 'do que se tolera. A forma correta de chegar a 80–90 mg/kg/dia é dar até 70 mg/kg/dia pela suspensão combinada e '
 'completar com amoxicilina isolada.')
log('A','14.2 e 14.3 — amoxicilina-clavulanato em pediatria',
 'Os quadros prescreviam "90 mg/kg/dia de amoxicilina" na forma de amoxicilina-clavulanato. Essa dose vem das diretrizes '
 'norte-americanas e pressupõe a suspensão 600/42,9 mg/5 mL (proporção 14:1), que não é comercializada no Brasil. Com a '
 'suspensão brasileira (400/57 mg/5 mL, proporção 7:1), a mesma dose de amoxicilina leva o clavulanato a cerca de '
 '12,8 mg/kg/dia — acima do limite de tolerância e causa previsível de diarreia e abandono do tratamento.',
 'Os esquemas passam a limitar a suspensão combinada a 70 mg/kg/dia de amoxicilina e a completar com amoxicilina isolada '
 'até 80–90 mg/kg/dia, mantendo o clavulanato em até 10 mg/kg/dia. Acrescentado alerta explicando a diferença entre as '
 'apresentações brasileira e norte-americana.')

# =====================================================================
# 3. PENICILINA V — no Brasil o comprimido é de 500.000 UI
# =====================================================================
n = sub_all(r'penicilina V 500 mg VO 12/12 h por 10 dias',
            'penicilina V (fenoximetilpenicilina) 500.000 UI VO 6/6 h a 8/8 h por 10 dias')
n += sub_all(r'Penicilina V 500 mg VO 6/6 h', 'Penicilina V 500.000 UI VO 6/6 h')
n += sub_all(r'Penicilina V ou Amoxicilina · Penicilina V 500\.000 UI VO 6/6 h',
             'Penicilina V ou Amoxicilina · Penicilina V (fenoximetilpenicilina) 500.000 UI VO 6/6 h')
r = row('4.1','ESQUEMAS','Erisipela clássica estreptocócica')
r[3] = ('Boa opção quando o quadro é tipicamente estreptocócico, sem purulência. No Brasil a penicilina V é '
        'apresentada em comprimido de 500.000 UI (≈ 312 mg) e em solução oral de 80.000 UI/mL — não há comprimido '
        'expresso em miligramas.')
log('B','2.1 e 4.1 — penicilina V',
 'A dose era escrita como "penicilina V 500 mg", que é a forma norte-americana. No Brasil a fenoximetilpenicilina é '
 'apresentada em comprimido de 500.000 UI (≈ 312 mg) e em solução oral de 80.000 UI/mL; não existe comprimido rotulado '
 'em miligramas, o que torna a prescrição não executável na farmácia.',
 'Posologia reescrita na unidade da apresentação brasileira: 500.000 UI VO 6/6 h a 8/8 h, com a equivalência em '
 'miligramas indicada uma vez.')

# =====================================================================
# 4. AMOXICILINA 1 g — não há apresentação de 1 g no Brasil
# =====================================================================
d = drug('1.1','Amoxicilina')
d['nota'] = ((d.get('nota','')+' ') if d.get('nota') else '') + \
  'No Brasil não há apresentação de 1 g: a dose de 1 g corresponde a duas cápsulas de 500 mg. As apresentações orais são cápsula de 500 mg e comprimido de 875 mg.'
log('B','1.1 e demais quadros que usam amoxicilina 1 g',
 'A conduta de partida da pneumonia comunitária é amoxicilina 1 g VO 8/8 h — dose correta pela diretriz, mas sem '
 'apresentação correspondente no Brasil, onde existem cápsula de 500 mg e comprimido de 875 mg.',
 'Acrescentada a nota de que 1 g corresponde a duas cápsulas de 500 mg, para que a prescrição seja executável. '
 'A dose recomendada não foi alterada.')

# =====================================================================
# 5. COLÍRIO E POMADA OFTÁLMICA — apresentações inexistentes no Brasil
# =====================================================================
r = row('12.1','ESQUEMAS','Conjuntivite bacteriana provável, sem sinais de alarme')
r[1] = ('Tobramicina 0,3% colírio · 1 gota no olho acometido 4/4 h a 6/6 h · Tópica')
r[3] = ('Alternativas com apresentação brasileira: ciprofloxacino 0,3% colírio, azitromicina 1,5% colírio, '
        'ou pomada de oxitetraciclina + polimixina B / neomicina + polimixina B + bacitracina. '
        'Reavaliar se não melhorar em 48–72 h ou se surgirem sinais de alarme.')
d = drug('12.1','Polimixina B + Trimetoprima colírio')
d['nome'] = 'Tobramicina colírio 0,3%'
d['padrao'] = '1 gota 4/4 h a 6/6 h por 5–7 dias'
d['grave'] = 'Não indicada para ceratite/úlcera — nesses casos, quinolona tópica em dose intensiva por oftalmologia'
for f in q('12.1')['hero']:
    if f['label']=='CONDUTA DE PARTIDA':
        f['title'] = 'Higiene e observação na maioria; colírio antibiótico quando bacteriana provável'
        f['detail'] = ('Tobramicina 0,3% colírio, 1 gota 4/4 h a 6/6 h; quinolona tópica se usuário de lente de contato '
                       'sem ceratite aparente')
        f['value'] = f['title']+' '+f['detail']
r = row('12.9','ESQUEMAS','Blefarite anterior bacteriana ou secreção na margem palpebral')
r[1] = ('Tobramicina 0,3% pomada oftálmica · Aplicar na margem palpebral 1–2×/dia · Tópica')
r[3] = ('No Brasil não há pomada oftálmica de eritromicina nem de bacitracina isolada. As opções com apresentação '
        'nacional são tobramicina 0,3% pomada e as associações oxitetraciclina + polimixina B ou '
        'neomicina + polimixina B + bacitracina.')
d = drug('12.9','Eritromicina pomada oftálmica')
d['nome'] = 'Tobramicina pomada oftálmica 0,3%'
d['padrao'] = 'Aplicar na margem palpebral 1–2×/dia por 7–10 dias'
log('A','12.1 e 12.9 — apresentações oftálmicas',
 'A conjuntivite bacteriana tinha como conduta de partida "polimixina B/trimetoprima colírio" e a blefarite, '
 '"eritromicina ou bacitracina pomada oftálmica". Nenhuma das três apresentações é comercializada no Brasil: '
 'são produtos norte-americanos (Polytrim, eritromicina oftálmica, bacitracina oftálmica isolada).',
 'Substituídas pelas apresentações com registro nacional: tobramicina 0,3% colírio e pomada, com ciprofloxacino, '
 'azitromicina colírio e as associações oxitetraciclina + polimixina B e neomicina + polimixina B + bacitracina '
 'listadas como alternativas.')

# =====================================================================
# 6. DICLOXACILINA — sem apresentação no Brasil
# =====================================================================
n = sub_all(r'Cefalexina ou Oxacilina/Dicloxacilina', 'Cefalexina; oxacilina EV se internação')
log('C','10.6 — mastite puerperal',
 'A conduta de partida citava "Cefalexina ou Oxacilina/Dicloxacilina". A dicloxacilina não é comercializada no Brasil '
 'e a oxacilina existe apenas como apresentação injetável — nenhuma das duas serve para o tratamento oral que o quadro '
 'descreve.',
 'Conduta reescrita como cefalexina por via oral, com oxacilina endovenosa nomeada apenas para o cenário de internação.')

# =====================================================================
# 7. CEFALOSPORINAS ORAIS DE ALTERNATIVA — disponibilidade real
# =====================================================================
DISP = ('No Brasil, a cefalosporina oral de alternativa mais disponível é a cefuroxima axetil (comprimido de 250 e 500 mg '
        'e suspensão). O cefdinir existe apenas como suspensão oral pediátrica; cefpodoxima e cefixima têm disponibilidade '
        'variável e podem não ser encontradas. Confirmar no formulário local antes de prescrever.')
for qid, key in (('14.1','Alergia não anafilática a penicilina'),
                 ('14.2','Alergia não grave a penicilina'),
                 ('14.3','Alergia não grave a penicilina')):
    r = row(qid,'ALTERNATIVAS',key)
    r[1] = re.sub(r'^Cefdinir ou Cefuroxima · Cefdinir 14 mg/kg/dia VO 1–2x/dia; Cefuroxima 30 mg/kg/dia VO 12/12 h',
                  'Cefuroxima axetil ou Cefdinir · Cefuroxima axetil 30 mg/kg/dia VO 12/12 h; cefdinir 14 mg/kg/dia VO 1–2×/dia', r[1])
    r[1] = re.sub(r'^Cefuroxima axetil ou Cefdinir · Cefuroxima 30 mg/kg/dia VO 12/12 h ou Cefdinir 14 mg/kg/dia VO 1–2x/dia',
                  'Cefuroxima axetil ou Cefdinir · Cefuroxima axetil 30 mg/kg/dia VO 12/12 h; cefdinir 14 mg/kg/dia VO 1–2×/dia', r[1])
    r[1] = re.sub(r'^Cefdinir, Cefuroxima ou Cefpodoxima · Cefdinir 14 mg/kg/dia VO 1–2x/dia',
                  'Cefuroxima axetil ou Cefdinir · Cefuroxima axetil 30 mg/kg/dia VO 12/12 h; cefdinir 14 mg/kg/dia VO 1–2×/dia', r[1])
    r[3] = DISP
n = sub_all(r'Não apresentar cefdinir ou outras formulações pouco disponíveis como alternativa universal\. '
            r'Priorizar amoxicilina/amoxicilina-clavulanato e escolher alternativa por tipo de alergia e formulário local\.',
 'A cefalosporina oral de alternativa com apresentação mais estável no Brasil é a cefuroxima axetil. O cefdinir existe '
 'aqui apenas como suspensão oral pediátrica; cefpodoxima e cefixima têm disponibilidade variável. Priorizar '
 'amoxicilina ou amoxicilina-clavulanato e escolher a alternativa pelo tipo de alergia e pelo formulário do serviço.')
r = row('14.5','ESQUEMAS','Criança estável, aceitando VO, sem toxemia')
r[3] = ('Escolher conforme o padrão local e o antibiograma prévio. A cefixima tem disponibilidade variável no Brasil; '
        'cefalexina e cefuroxima axetil são as opções orais mais constantes.')
r = row('11.1','ALTERNATIVAS','Ceftriaxona indisponível para gonococo não complicado')
r[3] = ('Alternativa inferior; evitar como solução de rotina para gonorreia faríngea quando houver ceftriaxona. '
        'A cefixima tem disponibilidade variável no Brasil — confirmar antes de contar com ela como plano B.')
log('B','11.1, 14.1, 14.2, 14.3 e 14.5 — cefalosporinas orais de alternativa',
 'As alternativas para alergia não grave a penicilina abriam com cefdinir e cefpodoxima, e a ITU febril e a gonorreia '
 'ofereciam cefixima sem ressalva. No Brasil o cefdinir existe apenas como suspensão oral pediátrica (não há cápsula '
 'para adulto) e cefpodoxima e cefixima têm disponibilidade variável; o alerta que já existia dizia genericamente para '
 'não usar cefdinir, o que também não é exato.',
 'A cefuroxima axetil — a de apresentação mais estável no país — passou a encabeçar as alternativas, com cefdinir '
 'mantido em seguida e a ressalva de disponibilidade escrita de forma precisa em cada quadro.')

json.dump(doc, open('doc_final.json','w'), ensure_ascii=False, indent=1)
json.dump(LOG, open('log_final.json','w'), ensure_ascii=False, indent=1)
print('etapa 7 ok —', len(LOG), 'achados no total')
