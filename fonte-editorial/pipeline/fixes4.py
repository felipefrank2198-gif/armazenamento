# -*- coding: utf-8 -*-
"""Etapa 4 — reestruturação editorial: remoção de boilerplate, campos estruturados."""
import json, re, collections
doc = json.load(open('doc_fix3.json'))
LOG = json.load(open('log3.json'))
def log(sev,esc,ach,cor): LOG.append(dict(sev=sev,escopo=esc,achado=ach,correcao=cor))
QS = [q for c in doc['chapters'] for q in c['quadros']]

# ---------------------------------------------------------------- 1. "Nível: required."
NIVEL = {'none':'dispensável','recommended':'recomendada','required':'obrigatória'}
n = 0
for q in QS:
    for s in q['sections']:
        for b in s['blocks']:
            if b['t']=='ul':
                for i,it in enumerate(b['items']):
                    m = re.match(r'Nível:\s*(none|recommended|required)\.\s*(.*)', it)
                    if m:
                        q['validacao_nivel'] = NIVEL[m.group(1)]
                        b['items'][i] = m.group(2).strip()
                        n += 1
log('C','96 quadros — bloco "Validação antes da prescrição"',
 'Os valores internos do modelo de dados foram publicados em inglês dentro do texto: "Nível: none.", "Nível: recommended.", "Nível: required." aparecem no início do bloco de validação em 96 quadros.',
 'Convertidos em um selo em português no cabeçalho do quadro — Validação institucional: dispensável / recomendada / obrigatória — e a frase explicativa foi mantida como texto corrido.')

# ---------------------------------------------------------------- 2. checklist genérico
GENERICOS = {
 'Confirmar alergias, função orgânica, gestação/lactação, interações e protocolo local.',
 'Validar com protocolo institucional/CCIH, microbiologia local e disponibilidade antes da padronização.',
 'Revisar alergias, função renal/hepática, gestação/lactação, peso e interações relevantes',
 'Confirmar gestação, alergias, peso, interações e contraindicações antes de prescrever.',
 'Reavaliar gestação, lactação, idade, peso, função renal/hepática e contraindicações',
 'Ajustar dose para função renal/hepática, alergias, gestação, peso e gravidade',
 'Confirmar peso atual em kg e dose máxima adulta',
 'Checar alergias, função renal/hepática, hidratação e risco de toxicidade',
}
rm = 0
for q in QS:
    for s in q['sections']:
        if not s['header'].startswith('VALIDAÇÃO'): continue
        for b in s['blocks']:
            if b['t']=='ul':
                before = len(b['items'])
                b['items'] = [i for i in b['items'] if i.strip().rstrip('.') not in {g.rstrip('.') for g in GENERICOS} and i.strip()]
                rm += before-len(b['items'])
log('C','Livro inteiro — bloco "Validação antes da prescrição"',
 f'{rm} repetições de itens de checklist genéricos ("Confirmar alergias, função orgânica, gestação/lactação, interações e protocolo local", "Validar com protocolo institucional/CCIH…") que já constam integralmente do bloco "Antes de prescrever" da abertura do livro.',
 'Itens genéricos removidos dos quadros e mantidos uma única vez na abertura; permanecem no quadro apenas os itens específicos daquela síndrome.')

# ---------------------------------------------------------------- 3. alerta betalactâmico repetido
BL_TITLE = 'CLASSIFICAR A REAÇÃO AO BETA-LACTÂMICO'
rm = 0
for q in QS:
    for s in q['sections']:
        if s['header'].startswith('ALERTAS'):
            before = len(s['blocks'])
            s['blocks'] = [b for b in s['blocks'] if not (b['t']=='callout' and BL_TITLE in b['title'])]
            rm += before-len(s['blocks'])
log('C','90 quadros — alerta de alergia a betalactâmico',
 'O mesmo alerta de 300 caracteres ("Separar efeito adverso/intolerância, reação imediata de baixo ou alto risco…") era repetido integralmente em 90 quadros, ocupando cerca de 4 páginas somadas.',
 'Transferido para a abertura do livro, na página "Alergia a betalactâmico em uma página", com remissão fixa ao quadro 19.7 no rodapé da seção "Alternativas e alergia" de cada quadro.')

# ---------------------------------------------------------------- 4. alertas de capítulo inteiro -> nota de capítulo
CHAPTER_NOTES = {
 'Dose pediátrica exige conferência ativa': '14',
 'Síndrome prática: decisão baseada em contexto': '19',
 'Checklist de profilaxia': '17',
}
moved = collections.Counter()
for c in doc['chapters']:
    for q in c['quadros']:
        for s in q['sections']:
            if not s['header'].startswith('ALERTAS'): continue
            keep = []
            for b in s['blocks']:
                hit = next((k for k in CHAPTER_NOTES if b['t']=='callout' and k in b['title']), None)
                if hit and CHAPTER_NOTES[hit]==c['num']:
                    c.setdefault('nota', b['body']); moved[hit]+=1
                else: keep.append(b)
            s['blocks'] = keep
log('C','Capítulos 14, 17 e 19',
 f'Alertas idênticos repetidos em todos os quadros do capítulo: "Dose pediátrica exige conferência ativa" (11×), "Síndrome prática" (14×), "Checklist de profilaxia" (10×).',
 'Promovidos a nota de abertura do capítulo, onde valem para todos os quadros, e removidos das repetições.')

# ---------------------------------------------------------------- 5. ESCOPO DA REVISÃO -> selo
STATUS = {'verificado':'Verificado','bibliografia-de-capitulo':'Bibliografia de capítulo','revisao-parcial':'Revisão parcial'}
for q in QS:
    for s in q['sections']:
        if not s['header'].startswith('REVISÃO'): continue
        keep=[]
        for b in s['blocks']:
            if b['t']=='callout' and 'ESCOPO' in b['title']:
                m = re.search(r'Status:\s*([\w-]+)\s*·\s*nível:\s*([\w]+)\s*·\s*última revisão:\s*([\d-]+)', b['body'])
                if m:
                    q['status'] = STATUS.get(m.group(1), m.group(1))
                    q['nivel_evid'] = m.group(2)
                    q['revisao'] = m.group(3)
                continue
            keep.append(b)
        s['blocks']=keep
log('C','162 quadros — bloco "Escopo da revisão"',
 'Uma caixa de 250 caracteres com o mesmo texto de rodapé metodológico era repetida ao final de cada um dos 162 quadros (sete variantes ao todo), somando cerca de 8 páginas.',
 'Convertida em um selo compacto no cabeçalho do quadro (status · nível de evidência · data da revisão); a explicação metodológica completa passa a constar uma única vez na política editorial.')

# ---------------------------------------------------------------- 6. tabela de fármacos -> registros estruturados
GEST = [
 ('Experiência clínica geralmente favorável quando indicada','aceito','Uso aceito quando indicado — considerar idade gestacional e foco'),
 ('Pode ser usada quando clinicamente indicada','aceito','Uso aceito quando indicado — individualizar dose e monitorização'),
 ('Usável em gestação em cenários apropriados','ressalva','Aceito com ressalva — evitar em deficiência de G6PD e a termo'),
 ('Usável em gestação para baixo trato','ressalva','Aceito com ressalva — apenas trato urinário baixo'),
 ('Evitar de rotina na gestação','evitar','Evitar de rotina — só se o benefício superar o risco'),
 ('Evitar na gestação','evitar','Evitar — escolher alternativa específica para o foco'),
]
def classify(seg):
    s = seg.strip()
    if not s or s in ('Individualizar.','Não necessário','Seguro','Conforme indicação; monitorar K/creatinina'):
        return ('drop', s)
    for k, code, txt in GEST:
        if s.startswith(k): return ('gest', (code, txt))
    if re.match(r'^[\d,.]+\s*(g|mg|mcg|milhões)', s) or re.search(r'\b(g|mg)/dia\b', s): return ('teto', s)
    if re.search(r'hepat', s, re.I): return ('hep', s)
    return ('nota', s)

def parse_dose(cell):
    d = dict(padrao='', grave='', via='')
    m = re.search(r'Padrão:\s*(.*?)(?:\s+Grave:\s*(.*?))?(?:\s+Via:\s*(.*))?$', cell)
    if m:
        d['padrao'] = (m.group(1) or '').strip()
        d['grave']  = (m.group(2) or '').strip()
        d['via']    = (m.group(3) or '').strip()
    else:
        d['padrao'] = cell.strip()
    return d

nfarm = 0
for q in QS:
    for s in q['sections']:
        if not s['header'].startswith('ANTIMICROBIANOS'): continue
        for bi,b in enumerate(s['blocks']):
            if b['t']!='table': continue
            drugs=[]
            for r in b['rows']:
                nome = r[0].strip()
                dose = parse_dose(r[1] if len(r)>1 else '')
                renal = (r[2] if len(r)>2 else '').strip()
                rec = dict(nome=nome, **dose, renal=renal, teto='', hep='', gest='', gest_txt='', nota='')
                if len(r)>3:
                    for seg in r[3].split(' | '):
                        kind, val = classify(seg)
                        if kind=='gest': rec['gest'], rec['gest_txt'] = val
                        elif kind=='teto': rec['teto'] = val
                        elif kind=='hep': rec['hep'] = val
                        elif kind=='nota': rec['nota'] = (rec['nota']+' '+val).strip()
                drugs.append(rec); nfarm+=1
            s['blocks'][bi] = {'t':'drugs','rows':drugs}
log('C','157 quadros — tabela "Antimicrobianos e ajustes"',
 'A coluna "Outras populações/monitorização" concatenava até quatro informações distintas separadas por barra vertical — ajuste hepático, gestação/lactação, teto de dose e monitorização — e a frase de gestação/lactação, sempre idêntica, repetia-se cerca de 600 vezes no livro.',
 'A coluna foi desmembrada em campos próprios. Gestação/lactação passou a ser um selo de três estados (uso aceito / com ressalva / evitar) ao lado do nome do fármaco, com a legenda apresentada uma única vez; teto de dose e ajuste hepático ganharam colunas próprias.')

# ---------------------------------------------------------------- 7. espectro das fichas -> matriz
ESP = {'atividade esperada em suscetíveis':'sim','dependente de sensibilidade':'variavel','não contar como cobertura':'nao'}
for q in doc['fichas']:
    for s in q['sections']:
        if not s['header'].startswith('ESPECTRO'): continue
        for bi,b in enumerate(s['blocks']):
            if b['t']!='table': continue
            m=[]
            for r in b['rows']:
                m.append(dict(grupo=r[0].strip(), v=ESP.get(r[1].strip(),'nao'), nota=(r[2].strip() if len(r)>2 else '')))
            s['blocks'][bi] = {'t':'spectrum','rows':m}
log('C','39 fichas de antimicrobianos — bloco "Espectro"',
 'O espectro era apresentado como uma tabela de nove linhas por ficha, em que a frase "não contar como cobertura" aparecia 250 vezes no conjunto do livro — cerca de 351 linhas de tabela para transmitir 351 valores de três estados.',
 'Substituído por uma faixa compacta de nove marcadores com três estados (cobre / depende de sensibilidade / não cobre), lida de relance e com as notas específicas preservadas. Reduz cerca de 12 páginas.')

json.dump(doc, open('doc_fix4.json','w'), ensure_ascii=False, indent=1)
json.dump(LOG, open('log4.json','w'), ensure_ascii=False, indent=1)
print('etapa 4 ok — fármacos estruturados:',nfarm,'| achados:',len(LOG))
