# -*- coding: utf-8 -*-
import json, re
doc = json.load(open('doc_fix2.json'))
LOG = json.load(open('log2.json'))
def log(sev, escopo, achado, correcao): LOG.append(dict(sev=sev, escopo=escopo, achado=achado, correcao=correcao))
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
def set_cell(qid,p,key,col,val):
    for r in table(qid,p)['rows']:
        if r[0].strip()==key: r[col]=val; return
    raise KeyError(f'{qid}/{p}/{key}')
def add_callout(qid, sev, title, body, pos=None):
    s = sec(qid,'ALERTAS')
    c = {'t':'callout','sev':sev,'title':title,'body':body}
    s['blocks'].insert(0 if pos is None else pos, c)
def sub_all(pat, rep):
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

# A17 — duração cUTI (IDSA 2025)
DUR = ('7 dias na resposta favorável com foco controlado (5–7 dias se fluoroquinolona), contados a partir da '
       'primeira terapia ativa; 10–14 dias apenas em bacteremia complicada, abscesso, prostatite, obstrução não '
       'resolvida ou resposta lenta')
for qid, keys in (('5.1',['Pielonefrite sem choque e baixo risco de ESBL/Pseudomonas',
                          'Sepse, internação recente, sonda/nefrostomia, manipulação urológica ou risco de Pseudomonas',
                          'ESBL prévio/provável, choque séptico ou falha a cefalosporina']),
                  ('5.3',['Sem sepse, baixo risco de ESBL/Pseudomonas',
                          'Sepse, sonda, manipulação urológica, hospitalização recente ou risco de Pseudomonas',
                          'Choque, ESBL prévio/provável ou falha a cefalosporina'])):
    for k in keys:
        try: set_cell(qid,'ESQUEMAS',k,2,DUR)
        except KeyError: pass
log('B','5.1 e 5.3 — duração da ITU alta/complicada',
 'O campo de duração do quadro trazia a regra da diretriz IDSA 2025 (5–7 dias com fluoroquinolona, 7 dias com não fluoroquinolona), mas as linhas da tabela de esquemas mantinham "7–10 dias" e "7–14 dias" da prática antiga. O médico lia duas durações diferentes no mesmo quadro.',
 'Tabela harmonizada com a diretriz de 2025: 7 dias na resposta favorável com foco controlado, contados da primeira terapia ativa, e 10–14 dias reservados às exceções nomeadas.')

# A18 — mupirocina via
set_cell('14.7','ESQUEMAS','Poucas lesões, localizado',1,'Mupirocina tópica · Aplicar 2–3×/dia sobre as lesões · Tópica')
set_cell('14.7','ANTIMICROBIANOS','Mupirocina',1,'Padrão: aplicar 2–3×/dia por 5 dias Grave: não aplicável Via: tópica')
set_cell('14.7','ANTIMICROBIANOS','Mupirocina',2,'Uso tópico: sem ajuste renal')
log('A','14.7 — Impetigo pediátrico',
 'A mupirocina, de uso tópico, estava rotulada com via "VO" na tabela de esquemas e na de ajustes, acompanhada de uma nota interna de desenvolvimento publicada no livro.',
 'Via corrigida para tópica nos dois pontos e nota interna removida.')

# A22 — aztreonam padronizado
n = sub_all(r'Aztreonam 2 g EV 6/6 h', 'Aztreonam 2 g EV 8/8 h')
n += sub_all(r'aztreonam 2 g EV 6/6 h', 'aztreonam 2 g EV 8/8 h')
n += sub_all(r'Padrão: 1–2 g EV 8/8 h Grave: 2 g EV 6/6 h se grave/Pseudomonas',
             'Padrão: 2 g EV 8/8 h Grave: 2 g EV 6/6 h apenas em Pseudomonas grave (teto de 8 g/dia)')
log('B','1.2, 3.3, 19.3, 19.7 — aztreonam',
 'A mesma indicação aparecia ora como 2 g EV 6/6 h, ora 8/8 h, sem critério explícito. 2 g 6/6 h corresponde ao teto de 8 g/dia.',
 'Padronizado em 2 g EV 8/8 h, com 6/6 h reservado e nomeado para Pseudomonas grave, com o teto de 8 g/dia explícito.')

# A19 — TB meníngea: esquema brasileiro
set_cell('7.6','ESQUEMAS','Suspeita alta ou confirmada',1,
 'RHZE + corticoide · Fase intensiva: 2 meses de rifampicina + isoniazida + pirazinamida + etambutol em '
 'comprimido combinado por faixa de peso (MS). Manutenção: 10 meses de rifampicina + isoniazida. '
 'Associar piridoxina 50 mg/dia com a isoniazida · VO')
set_cell('7.6','ESQUEMAS','Suspeita alta ou confirmada',2,
 '12 meses no total (2 RHZE + 10 RH), conforme o Ministério da Saúde para a forma meningoencefálica')
set_cell('7.6','ESQUEMAS','Rebaixamento, hidrocefalia, AVC ou hipertensão intracraniana',1,
 'RHZE + Dexametasona · RHZE por faixa de peso + dexametasona EV/VO nas primeiras 4–8 semanas, '
 'com desmame gradual conforme resposta neurológica · VO/EV')
set_cell('7.6','ESQUEMAS','Rebaixamento, hidrocefalia, AVC ou hipertensão intracraniana',2,
 '12 meses no total (2 RHZE + 10 RH); corticoide por 4–8 semanas com desmame')
for f in q('7.6')['hero']:
    if f['label']=='DURAÇÃO': f['title']=''; f['detail']='12 meses (2 RHZE + 10 RH) — esquema meningoencefálico do Ministério da Saúde'; f['value']=f['detail']
log('B','7.6 — Meningite tuberculosa',
 'A duração aparecia como "9–12 meses ou conforme protocolo" e o esquema apenas como "doses por peso conforme protocolo de TB", sem indicar qual é o esquema brasileiro para a forma meningoencefálica.',
 'Explicitado o esquema do Ministério da Saúde: 2 meses de RHZE + 10 meses de RH (12 meses no total), com piridoxina associada à isoniazida e corticoide por 4–8 semanas com desmame.')

# A20 — IGHAT no tétano instalado
set_cell('13.8','ESQUEMAS','Neutralização de toxina não ligada',1,
 'Imunoglobulina humana antitetânica (IGHAT) · 3.000–6.000 UI IM no tétano instalado, em dose única, '
 'aplicada em massa muscular diferente da vacina. Na profilaxia após ferimento a dose é 250–500 UI. '
 'Onde só houver soro antitetânico heterólogo (SAT), seguir a dose e o teste de sensibilidade do protocolo · IM')
log('A','13.8 — Tétano acidental instalado',
 'A imunoglobulina antitetânica constava apenas como "dose única conforme protocolo oficial/local", sem número. Em uma emergência de UTI, o guia deixava a dose da terapia específica em aberto.',
 'Doses explicitadas: 3.000–6.000 UI IM no tétano instalado e 250–500 UI na profilaxia, com a ressalva do SAT heterólogo.')

# A21 — neurotoxoplasmose: manutenção
tb = table('7.5','ESQUEMAS')
tb['rows'].append(['Manutenção (profilaxia secundária) após a indução',
 'Pirimetamina + Sulfadiazina + Ácido folínico · Pirimetamina 25–50 mg VO/dia + Sulfadiazina 2–4 g VO/dia '
 'divididos em 2–4 tomadas + Ácido folínico 10–25 mg VO/dia · VO',
 'Até CD4 > 200 células/mm³ por mais de 6 meses em terapia antirretroviral, com melhora clínica e radiológica',
 'Manter a profilaxia secundária enquanto persistir a imunossupressão. A alternativa com clindamicina não protege contra pneumocistose: manter profilaxia específica.'])
log('B','7.5 — Neurotoxoplasmose',
 'O esquema de indução terminava com "≥6 semanas, depois manutenção", sem informar as doses da manutenção nem o critério para suspendê-la.',
 'Acrescentada a linha de manutenção com doses (pirimetamina 25–50 mg/dia + sulfadiazina 2–4 g/dia + ácido folínico) e o critério de suspensão (CD4 > 200 por mais de 6 meses em TARV).')

# A23 — sífilis: neurossífilis + Jarisch-Herxheimer
tb = table('11.4','ESQUEMAS')
tb['rows'].append(['Neurossífilis, sífilis ocular ou ótica',
 'Penicilina G cristalina · 18–24 milhões UI/dia EV, em 3–4 milhões UI a cada 4 h ou em infusão contínua · EV',
 '10–14 dias',
 'Ramo distinto: não tratar com penicilina benzatina. Avaliar punção lombar, oftalmologia/otorrinolaringologia e seguimento sorológico. Alguns protocolos acrescentam benzatina 2,4 milhões UI semanal por 3 semanas ao final.'])
add_callout('11.4','atencao','ATENÇÃO · REAÇÃO DE JARISCH-HERXHEIMER',
 'Febre, calafrios, mialgia e piora transitória das lesões nas primeiras 24 h após a primeira dose de penicilina. '
 'É esperada, sobretudo na sífilis recente, e não caracteriza alergia — não suspender o tratamento. '
 'Orientar antitérmico e observação. Na gestante pode desencadear contrações e alterações do batimento cardíaco fetal: '
 'orientar procurar assistência obstétrica se isso ocorrer.')
log('B','11.4 — Sífilis adquirida',
 'O quadro remetia a neurossífilis/sífilis ocular como "outro ramo", mas o livro não trazia em nenhum lugar o esquema correspondente; e não havia menção à reação de Jarisch-Herxheimer, que é a intercorrência mais comum após a primeira dose e é rotineiramente confundida com alergia.',
 'Acrescentado o esquema de neurossífilis (penicilina G cristalina 18–24 milhões UI/dia por 10–14 dias) e um alerta sobre a reação de Jarisch-Herxheimer, com a ressalva obstétrica.')

# 2.1 — febre reumática e escore nomeado
add_callout('2.1','info','INFORMAÇÃO · POR QUE TRATAR: PREVENÇÃO DE FEBRE REUMÁTICA',
 'O ganho sintomático do antibiótico na faringite estreptocócica é pequeno (cerca de um dia). '
 'A razão principal para tratar é prevenir febre reumática aguda — desfecho ainda relevante no Brasil — '
 'e complicações supurativas. Isso justifica completar os 10 dias de betalactâmico oral, e não encurtar o curso.')
n = sub_all(r'Quando não houver sinais virais claros, usar escore e teste rápido/cultura conforme disponibilidade\.',
            'Quando não houver sinais virais claros, aplicar o escore de Centor/McIsaac e o teste rápido ou cultura conforme disponibilidade.')
log('B','2.1 — Faringoamigdalite estreptocócica',
 'O quadro citava genericamente "usar escore" sem nomeá-lo e não explicitava a razão de tratar (prevenção de febre reumática), que é o que sustenta o curso de 10 dias em vez de um curso curto.',
 'Escore de Centor/McIsaac nomeado e acrescentado alerta explicando o objetivo do tratamento e por que a duração de 10 dias não deve ser encurtada.')

# terminologia SMX-TMP
n = sub_all(r'\b160/800 mg\b','800/160 mg')
n += sub_all(r'SMX-TMP 1–2 DS VO 12/12 h','SMX-TMP 800/160 mg (1 comprimido) VO 12/12 h; 2 comprimidos em adulto de grande porte conforme protocolo')
n += sub_all(r'1 comprimido DS VO 12/12 h','800/160 mg (1 comprimido) VO 12/12 h')
n += sub_all(r'Trimetoprima-Sulfametoxazol','Sulfametoxazol-trimetoprima')
log('C','Livro inteiro — sulfametoxazol-trimetoprima',
 'A mesma droga aparecia como "800/160 mg", "160/800 mg", "1 comprimido DS" e "1–2 DS" — sendo "DS" (double strength) nomenclatura norte-americana sem correspondência na apresentação brasileira.',
 'Padronizado para "800/160 mg (1 comprimido)" em todo o livro, com a ordem sulfametoxazol/trimetoprima constante.')

json.dump(doc, open('doc_fix3.json','w'), ensure_ascii=False, indent=1)
json.dump(LOG, open('log3.json','w'), ensure_ascii=False, indent=1)
print('etapa 3 ok —', len(LOG), 'achados')
