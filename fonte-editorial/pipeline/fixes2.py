# -*- coding: utf-8 -*-
import json, re
doc = json.load(open('doc_fix1.json'))
LOG = json.load(open('log1.json'))
def log(sev, escopo, achado, correcao):
    LOG.append(dict(sev=sev, escopo=escopo, achado=achado, correcao=correcao))

def q(qid):
    for c in doc['chapters']:
        for x in c['quadros']:
            if x['id'] == qid: return x
    for x in doc['fichas']:
        if x['id'] == qid: return x
    raise KeyError(qid)
def sec(qid, prefix):
    for s in q(qid)['sections']:
        if s['header'].startswith(prefix): return s
    raise KeyError(qid+'/'+prefix)
def table(qid, prefix):
    for b in sec(qid, prefix)['blocks']:
        if b['t'] == 'table': return b
    raise KeyError(qid+'/'+prefix)
def set_cell(qid, prefix, key, col, value):
    for r in table(qid, prefix)['rows']:
        if r[0].strip() == key:
            r[col] = value; return
    raise KeyError(f'{qid}/{prefix}/{key}')
def rename_row(qid, prefix, old, new):
    for r in table(qid, prefix)['rows']:
        if r[0].strip() == old:
            r[0] = new; return
    raise KeyError(f'{qid}/{prefix}/{old}')
def callout(qid, titlepart):
    for b in sec(qid,'ALERTAS')['blocks']:
        if b['t']=='callout' and titlepart in b['title']: return b
    raise KeyError(qid+'/'+titlepart)
def hero(qid, label='CONDUTA DE PARTIDA', **kw):
    for f in q(qid)['hero']:
        if f['label'] == label:
            f.update(kw)
            f['value'] = (f.get('title','')+' '+f.get('detail','')).strip()
            return
    raise KeyError(qid+'/'+label)
def sub_all(pattern, repl):
    n = 0
    def fn(o):
        nonlocal n
        if isinstance(o, dict):
            for k,v in o.items():
                if isinstance(v,str):
                    v2 = re.sub(pattern, repl, v)
                    if v2!=v: n+=1; o[k]=v2
                else: fn(v)
        elif isinstance(o,list):
            for i,v in enumerate(o):
                if isinstance(v,str):
                    v2 = re.sub(pattern, repl, v)
                    if v2!=v: n+=1; o[i]=v2
                else: fn(v)
    fn(doc); return n

# =========================================================================
# A1 — VANCOMICINA: alvo de vale 15–20 -> AUC/CIM 400–600
# =========================================================================
c = callout('1.2','VANCOMICINA')
c['title'] = 'ALERTA CRÍTICO · VANCOMICINA: DOSE DE ATAQUE E ALVO DE AUC'
c['body']  = ('Dose de ataque 20–35 mg/kg de peso real (usualmente 25–30 mg/kg no crítico), '
              'teto de 3 g por dose e infusão em pelo menos 60 min por dose de 1 g. '
              'Manutenção 15–20 mg/kg a cada 8–12 h ajustada à função renal. '
              'Alvo: AUC₂₄/CIM 400–600 (consenso ASHP/IDSA/PIDS/SIDP 2020). '
              'O alvo de vale 15–20 mg/L só deve ser usado como substituto quando a AUC não estiver '
              'disponível — associa-se a mais nefrotoxicidade e não é mais o alvo recomendado.')
n = sub_all(r'Ajustar por níveis \(alvo:? 15–20 µg/mL\)',
            'Monitorizar por AUC₂₄/CIM 400–600; vale 15–20 mg/L apenas como substituto quando a AUC não estiver disponível')
n += sub_all(r'Monitorar níveis \(alvo: 15–20 µg/mL\)',
             'Monitorizar por AUC₂₄/CIM 400–600')
set_cell('1.1','ANTIMICROBIANOS','Vancomicina',1,
  'Padrão: ataque 20–35 mg/kg (peso real, teto 3 g); manutenção 15–20 mg/kg a cada 8–12 h '
  'Grave: ataque 25–30 mg/kg; manutenção guiada por AUC₂₄/CIM 400–600 Via: EV')
set_cell('1.2','ANTIMICROBIANOS','Vancomicina',1,
  'Padrão: ataque 20–35 mg/kg (peso real, teto 3 g); manutenção 15–20 mg/kg a cada 8–12 h '
  'Grave: ataque 25–30 mg/kg; manutenção guiada por AUC₂₄/CIM 400–600 Via: EV')
log('A','Livro inteiro (1.1, 1.2 e ficha A18)',
 'Vancomicina com alvo terapêutico declarado como "vale 15–20 µg/mL" e dose de ataque de "25 mg/kg obrigatória", sem teto de dose. O consenso ASHP/IDSA/PIDS/SIDP 2020 abandonou o alvo de vale 15–20 para infecção grave por MRSA justamente pelo excesso de nefrotoxicidade.',
 'Alvo passa a AUC₂₄/CIM 400–600 (preferencial), com o vale 15–20 mg/L apenas como substituto explícito quando a AUC não estiver disponível. Ataque 20–35 mg/kg de peso real (25–30 no crítico), teto de 3 g/dose e tempo mínimo de infusão especificados.')

# =========================================================================
# A2 — critério menor ATS/IDSA: ureia (BUN)
# =========================================================================
n = sub_all(r'ureia ≥20 mg/dL', 'ureia ≥ 43 mg/dL (equivale a BUN ≥ 20 mg/dL)')
n += sub_all(r'ureia ≥20(?! mg)', 'ureia ≥ 43 mg/dL (BUN ≥ 20 mg/dL)')
log('A','1.1 e 1.2 — critérios de UTI',
 'O critério menor de UTI da ATS/IDSA foi transcrito como "ureia ≥ 20 mg/dL". O critério original é BUN ≥ 20 mg/dL, que corresponde a ureia ≈ 43 mg/dL na unidade usada no Brasil — a transcrição literal reduz o limiar em mais da metade.',
 'Passa a "ureia ≥ 43 mg/dL (equivale a BUN ≥ 20 mg/dL)" nos dois quadros.')

# =========================================================================
# A3 — Cefepime: ajuste renal conforme bula
# =========================================================================
CEF = ('>60 mL/min: 2 g 8/8 h; 30–60 mL/min: 2 g 12/12 h; 11–29 mL/min: 2 g 24/24 h; '
       '≤10 mL/min: 1 g 24/24 h (esquema de infecção grave, 2 g 8/8 h)')
n = sub_all(r'>60 mL/min: 2 g 8/8 h; 30–60 mL/min: 2 g 12/12 h; 11–29 mL/min: 1 g 12/12 h; <11 mL/min: 1 g 24/24 h', CEF)
log('A','1.1, 1.2, 7.1 — cefepime',
 'Ajuste renal do cefepime divergente dentro do próprio livro: "11–29 mL/min → 1 g 12/12 h" em 1.1/1.2/7.1 e "2 g 24/24 h" em 1.9. Para o esquema de infecção grave (2 g 8/8 h) a bula prevê 2 g 24/24 h nessa faixa; a redução para 1 g 12/12 h subdosa em infecção grave.',
 'Harmonizado para >60: 2 g 8/8 h · 30–60: 2 g 12/12 h · 11–29: 2 g 24/24 h · ≤10: 1 g 24/24 h.')

# =========================================================================
# A4 — Piperacilina-tazobactam: ajuste renal e teto
# =========================================================================
PT = ('>40 mL/min: 4,5 g 6/6 h; 20–40 mL/min: 3,375 g 6/6 h; <20 mL/min: 2,25 g 6/6 h '
      '(faixas do esquema de pneumonia nosocomial 4,5 g 6/6 h)')
n = sub_all(r'>40 mL/min: 4,5 g 6/6 h; 20–40 mL/min: 2,25 g 6/6 h; <20 mL/min: 2,25 g 8/8 h', PT)
n += sub_all(r'18 g/dia \(pip\)', '16 g/dia de piperacilina (18 g de piperacilina-tazobactam)')
n += sub_all(r'18 g/dia de piperacilina(?! \()', '16 g/dia de piperacilina (18 g de piperacilina-tazobactam)')
log('A','1.1 e 5.3 — piperacilina-tazobactam',
 'Ajuste renal misturava as faixas do esquema de 3,375 g com as do esquema de 4,5 g 6/6 h; e o teto era descrito como "18 g/dia (pip)", quando 18 g é a soma piperacilina+tazobactam (piperacilina = 16 g/dia).',
 'Faixas do esquema de 4,5 g 6/6 h aplicadas de forma coerente e teto corrigido para 16 g/dia de piperacilina.')

# =========================================================================
# A5 — 1.5 hero com dose órfã
# =========================================================================
hero('1.5', title='Ampicilina-sulbactam — se houver pneumonia bacteriana',
     detail='3 g EV 6/6 h. Na aspiração testemunhada sem evolução infecciosa sustentada, suporte e reavaliação em 24–48 h, sem antibiótico automático')
log('A','1.5 — Pneumonia broncoaspirativa',
 'A conduta de partida terminava com uma dose sem fármaco: "…antibiótico conforme evolução e gravidade 3 g EV 6/6 h". Um plantonista lendo apenas o destaque não tem como saber a que droga a dose se refere.',
 'Conduta de partida reescrita com o fármaco explícito (ampicilina-sulbactam 3 g EV 6/6 h) e o ramo de pneumonite química preservado como condição.')

# =========================================================================
# A6 — 3.3 / 3.4 hero ambíguo
# =========================================================================
for qid, nome in (('3.3','Angina de Ludwig'), ('3.4','Infecção cervical profunda')):
    hero(qid, title='Via aérea e controle cirúrgico do foco odontogênico + antimicrobiano',
         detail='Comunitária: ampicilina-sulbactam 3 g EV 6/6 h. Risco de Gram-negativo/assistência à saúde ou sepse: piperacilina-tazobactam 4,5 g EV 6/6 h')
log('A','3.3 e 3.4 — infecções cervicais profundas',
 'A conduta de partida citava ampicilina-sulbactam e terminava com "4,5 g EV 6/6 h", que é a dose da piperacilina-tazobactam. A leitura direta sugere ampicilina-sulbactam 4,5 g 6/6 h, posologia que não existe.',
 'Cada fármaco passa a aparecer com a sua própria dose, separados por cenário (comunitário vs. risco assistencial).')

# =========================================================================
# A7 — 13.5 malária grave
# =========================================================================
hero('13.5', title='Artesunato EV — imediato',
     detail='2,4 mg/kg EV em 0 h, 12 h e 24 h e depois 24/24 h (crianças < 20 kg: 3 mg/kg). Confirmar espécie, peso, gestação e G6PD na tabela oficial do Ministério da Saúde para o esquema oral de continuidade')
hero('13.5','VIA', title='', detail='EV')
log('A','13.5 — Malária grave',
 'Na emergência com maior letalidade do capítulo, a conduta de partida abria com a frase de triagem ("Página de triagem: confirmar espécie…") e a dose de artesunato ficava pendurada no final, sem nome de fármaco; a via aparecia como "Conduta" em vez de EV.',
 'Conduta de partida passa a nomear o artesunato com a dose completa e a via EV; a triagem por espécie/peso/G6PD permanece como condição para o esquema oral de continuidade. Acrescentada a dose pediátrica de 3 mg/kg para < 20 kg.')

# =========================================================================
# A8 — 11.2 gonorreia: alternativa incompleta
# =========================================================================
set_cell('11.2','ANTIMICROBIANOS','Gentamicina',1,
 'Padrão: 240 mg IM dose única SEMPRE associada a azitromicina 2 g VO dose única '
 'Grave: não indicada isoladamente Via: IM')
tb = table('11.2','ALTERNATIVAS')
tb['rows'].append(['Ceftriaxona indisponível ou alergia grave a cefalosporina',
 'Gentamicina + Azitromicina · Gentamicina 240 mg IM dose única + Azitromicina 2 g VO dose única · IM/VO',
 'Dose única',
 'Esquema alternativo do CDC. A gentamicina isolada não é tratamento adequado para gonorreia; a azitromicina 2 g é parte obrigatória do esquema. Programar controle de cura.'])
log('A','11.2 — Gonorreia não complicada',
 'A tabela de ajustes trazia "gentamicina 240 mg IM dose única quando alternativa necessária", sem o parceiro obrigatório. Gentamicina isolada não é esquema aceito para gonorreia e a monoterapia falha com frequência.',
 'A alternativa passa a constar como gentamicina 240 mg IM + azitromicina 2 g VO em dose única, com nota de controle de cura — igual ao que o próprio livro já trazia corretamente em 12.2.')

# =========================================================================
# A9 — 11.3 clamídia: hero contraditório
# =========================================================================
hero('11.3', title='Doxiciclina',
     detail='100 mg VO 12/12 h por 7 dias (adulto não gestante). Gestação ou contraindicação: azitromicina 1 g VO dose única')
hero('11.3','DURAÇÃO', title='', detail='7 dias (doxiciclina) · dose única (azitromicina)')
tb = table('11.3','ESQUEMAS')
tb['rows'].insert(1, ['Gestante ou impossibilidade de doxiciclina',
 'Azitromicina · 1 g VO dose única · VO', 'Dose única',
 'Padrão sindrômico do PCDT brasileiro e opção segura na gestação; realizar controle de cura por NAAT cerca de 4 semanas depois.'])
log('A','11.3 — Clamídia não complicada',
 'A conduta de partida indicava "azitromicina 1 g VO dose única" enquanto o campo de duração do mesmo quadro dizia "7 dias" e a única linha da tabela de esquemas trazia doxiciclina 7 dias. Três informações incompatíveis no mesmo quadro.',
 'Conduta de partida passa a doxiciclina 100 mg 12/12 h por 7 dias no adulto não gestante (preferencial em infecção retal), com azitromicina 1 g dose única explicitada como o ramo de gestação/adesão do PCDT. Duração corrigida em ambos os ramos.')

# =========================================================================
# A10 — 11.6 tricomoníase
# =========================================================================
hero('11.6', title='Metronidazol',
     detail='Mulher: 500 mg VO 12/12 h por 7 dias (preferencial). Homem: 2 g VO dose única')
hero('11.6','DURAÇÃO', title='', detail='7 dias na mulher · dose única no homem')
set_cell('11.6','ESQUEMAS','Tricomoníase — protocolo Brasil/MS',0,'Mulher — esquema preferencial')
tb = table('11.6','ESQUEMAS')
tb['rows'][0][1] = 'Metronidazol · 500 mg VO 12/12 h · VO'
tb['rows'][0][2] = '7 dias'
tb['rows'][0][3] = ('Superior à dose única na mulher (CDC 2021). O PCDT brasileiro admite 2 g em dose única; '
                    'quando a adesão for o fator limitante, registrar a escolha. Tratar parceiros e orientar abstinência.')
tb['rows'].append(['Homem / parceiro','Metronidazol · 2 g VO dose única · VO','Dose única',
                   'Dose única mantém eficácia no homem. Tratar parceiros evita reinfecção.'])
set_cell('11.6','ANTIMICROBIANOS','Metronidazol',1,
 'Padrão: mulher 500 mg VO 12/12 h por 7 dias Grave: homem 2 g VO dose única Via: VO')
log('A','11.6 (e coerência com 10.8) — Tricomoníase',
 'O mesmo livro trazia três versões do esquema: conduta de partida "2 g VO dose única", tabela de ajustes "500 mg 12/12 h por 7 dias em mulheres / 2 g dose única em homens" e, em 10.8, "500 mg 12/12 h por 7 dias" como padrão feminino.',
 'Unificado: mulher 500 mg 12/12 h por 7 dias (preferencial, superior à dose única), homem 2 g dose única; a alternativa do PCDT permanece identificada.')

# =========================================================================
# A11 — 12.5 celulite orbitária: ceftriaxona "12–24 h"
# =========================================================================
n = sub_all(r'Ceftriaxona 2 g EV a cada 12–24 h',
            'Ceftriaxona 2 g EV 24/24 h (2 g 12/12 h apenas se houver extensão intracraniana)')
hero('12.5', title='Vancomicina + Ceftriaxona + Metronidazol',
     detail='Vancomicina EV por peso/AUC + Ceftriaxona 2 g EV 24/24 h + Metronidazol 500 mg EV 8/8 h. Com extensão intracraniana, usar dose meníngea: ceftriaxona 2 g EV 12/12 h')
log('B','12.5 — Celulite orbitária',
 'O quadro prescrevia "ceftriaxona 2 g EV a cada 12–24 h" e, no alerta logo abaixo, instruía explicitamente a NÃO escrever "ceftriaxona 12–24 h" — contradizendo a si mesmo e deixando a dose meníngea indefinida.',
 'Passa a 2 g 24/24 h como padrão, com 2 g 12/12 h reservada e nomeada para extensão intracraniana.')

# =========================================================================
# A12 — 7.1 CIM de penicilina
# =========================================================================
n = sub_all(r'Se pneumococo com CIM de penicilina <0\.1',
            'Se pneumococo com CIM de penicilina ≤ 0,06 µg/mL (ponto de corte meníngeo do CLSI)')
log('A','7.1 — Meningite bacteriana',
 'O descalonamento para penicilina G estava condicionado a "CIM de penicilina < 0.1", que é o ponto de corte não meníngeo. Para meningite, o ponto de corte de sensibilidade do CLSI é ≤ 0,06 µg/mL — a regra antiga autoriza penicilina em cepas que não são sensíveis no LCR.',
 'Critério corrigido para CIM ≤ 0,06 µg/mL, identificado como ponto de corte meníngeo.')

# =========================================================================
# A13 / A14 — 1.3 DPOC: passo a passo incoerente + nomenclatura GOLD
# =========================================================================
tb = table('1.3','CONDUTA PASSO A PASSO')
tb['rows'] = [
 ['1','Exacerbação com purulência de escarro + aumento de dispneia/volume, ou necessidade de ventilação','Indicar antibiótico. Sem esses critérios, tratar como exacerbação não bacteriana.'],
 ['2','Leve/moderada, sem comorbidade descompensada e sem risco de Pseudomonas','Amoxicilina-clavulanato 875/125 mg VO 12/12 h por 5 dias; doxiciclina 100 mg VO 12/12 h é alternativa.'],
 ['3','Grave/internada, sem risco de Pseudomonas','Ceftriaxona 1–2 g EV 24/24 h OU ampicilina-sulbactam 3 g EV 6/6 h; passar para VO assim que estável.'],
 ['4','Risco de Pseudomonas (VEF₁ < 30%, corticoide sistêmico crônico, antibiótico nos últimos 30 dias, bronquiectasias)','Cefepime 2 g EV 8/8 h OU piperacilina-tazobactam 4,5 g EV 6/6 h. Dupla cobertura antipseudomonas só em choque, MDR ou perfil local desfavorável.'],
 ['5','Alergia, falha ou impossibilidade de combinação','Levofloxacino 750 mg VO/EV 24/24 h; atenção a QT, tendinopatia e resistência.'],
 ['6','Reavaliação em 72 h','Melhora: completar 5 dias. Piora: revisar cobertura, pesquisar pneumonia associada e considerar painel viral.'],
]
n = sub_all(r'Leve \(sem comorbidades, GOLD A/B\)', 'Leve (sem comorbidades; GOLD A/B)')
n += sub_all(r'GOLD D \(FEV1 < 30%\)', 'VEF₁ < 30% (GOLD 4) ou exacerbador frequente (grupo E)')
n += sub_all(r'DPOC grave GOLD D, corticoide, prévio abx', 'DPOC com VEF₁ < 30% (GOLD 4), corticoide sistêmico, antibiótico prévio')
n += sub_all(r'GOLD D \(FEV1 < 30%\) • Uso de corticoide sistêmico crônico',
             'VEF₁ < 30% (GOLD 4) ou exacerbador frequente (grupo E) • Uso de corticoide sistêmico crônico')
n += sub_all(r'Risco de Pseudomonas \(GOLD D, corticoide, prévio abx\)',
             'Risco de Pseudomonas (VEF₁ < 30%, corticoide, antibiótico prévio)')
log('A','1.3 — Exacerbação infecciosa de DPOC',
 'A "conduta passo a passo" contradizia a tabela de esquemas do mesmo quadro: indicava levofloxacino como 1ª linha na exacerbação moderada, "cefuroxima + claritromicina" na grave e "pip-tazo + ciprofloxacino" de rotina no risco de Pseudomonas — exatamente o que a tabela de esquemas e os alertas desaconselham.',
 'Passo a passo reescrito para espelhar a tabela de esquemas: amoxicilina-clavulanato como 1ª linha, quinolona reservada a alergia/falha e dupla cobertura antipseudomonas apenas em choque/MDR.')
log('B','1.3 — nomenclatura GOLD',
 'Uso de "GOLD D (FEV1 < 30%)". O grupo D deixou de existir na classificação GOLD desde 2023 (grupos A, B e E) e VEF₁ < 30% é grau espirométrico GOLD 4, não grupo.',
 'Substituído por "VEF₁ < 30% (GOLD 4) ou exacerbador frequente (grupo E)".')

# =========================================================================
# A15 / A16 — linhas trocadas na tabela de stewardship
# =========================================================================
set_cell('1.1','MICROBIOLOGIA','Transição EV → VO',1,
 'Afebril por 24–48 h, hemodinamicamente estável, tolerando dieta e com absorção preservada • '
 'Pneumococo confirmado: amoxicilina 1 g VO 8/8 h • Sem agente identificado: amoxicilina-clavulanato '
 '2 g/125 mg VO 12/12 h • Escolher o oral pelo patógeno, alergia, absorção e apresentação disponível no Brasil')
set_cell('1.1','MICROBIOLOGIA','Descalonamento',1,
 'Após 48–72 h de estabilidade clínica e identificação microbiológica • Reduzir o espectro do esquema empírico amplo • '
 'Com pneumococo ou outro patógeno identificado, estreitar para o agente ativo; não manter automaticamente '
 'ceftriaxona + azitromicina • Retirar cobertura anti-MRSA/antipseudomonas não sustentada por cultura ou fator de risco')
set_cell('1.2','MICROBIOLOGIA','Transição EV → VO',1,
 'Afebril por 24–48 h, sem vasopressor, tolerando dieta e com foco controlado • '
 'Escolher o oral pelo patógeno e sensibilidade • Não transicionar em bacteremia complicada, empiema não drenado ou instabilidade')
set_cell('1.2','MICROBIOLOGIA','Controle de foco',1,
 'Procurar e tratar derrame parapneumônico complicado/empiema, abscesso e obstrução brônquica • '
 'Toracocentese e drenagem quando indicadas • Antibiótico isolado não resolve coleção pleural')
set_cell('7.1','MICROBIOLOGIA','Transição EV → VO',1,
 'Não se aplica: meningite bacteriana é tratada por via endovenosa durante todo o curso. '
 'A alta só ocorre após completar o esquema EV conforme o agente.')
set_cell('7.1','MICROBIOLOGIA','Controle de foco',1,
 'Pesquisar e tratar foco parameníngeo: otite/mastoidite, sinusite, abscesso cerebral, empiema subdural, '
 'endocardite e dispositivo neurocirúrgico • Acionar ORL/neurocirurgia quando houver foco abordável')
log('A','1.1, 1.2 e 7.1 — tabela de stewardship',
 'A linha "Transição EV → VO" estava preenchida com critérios de FALHA TERAPÊUTICA ("ausência de melhora após 48–72 h", "isolamento de patógeno resistente"), e em 1.2 e 7.1 a linha "Controle de foco" trazia conduta de MRSA e o esquema empírico. Lidas de forma literal, essas linhas orientam a passar para via oral justamente no paciente que está falhando.',
 'Conteúdo realocado e reescrito: critérios reais de transição EV→VO, controle de foco pertinente a cada síndrome, e a explicitação de que meningite bacteriana não tem transição oral.')

json.dump(doc, open('doc_fix2.json','w'), ensure_ascii=False, indent=1)
json.dump(LOG, open('log2.json','w'), ensure_ascii=False, indent=1)
print('etapa 2 ok —', len(LOG), 'achados registrados')
