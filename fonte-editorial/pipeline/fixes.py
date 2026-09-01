# -*- coding: utf-8 -*-
"""Correções clínicas e editoriais ATB PRO 3.1 -> 4.0"""
import json, re, copy, sys

doc = json.load(open('doc.json'))
LOG = []

def log(sev, escopo, achado, correcao):
    LOG.append(dict(sev=sev, escopo=escopo, achado=achado, correcao=correcao))

# ---------------------------------------------------------------- utilidades
def walk_strings(obj, fn, path=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str): obj[k] = fn(v)
            else: walk_strings(v, fn, path+(k,))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            if isinstance(v, str): obj[i] = fn(v)
            else: walk_strings(v, fn, path+(i,))

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

def rows(qid, prefix):
    for b in sec(qid, prefix)['blocks']:
        if b['t'] == 'table': return b['rows'], b['headers']
    raise KeyError(qid+'/'+prefix+'/table')

def set_row(qid, prefix, key, col, value):
    rr, _ = rows(qid, prefix)
    for r in rr:
        if r[0].strip() == key:
            r[col] = value; return True
    raise KeyError(f'{qid}/{prefix}/{key}')

def set_hero(qid, label, **kw):
    for f in q(qid)['hero']:
        if f['label'] == label:
            f.update(kw)
            f['value'] = (f.get('title','') + ' ' + f.get('detail','')).strip()
            return True
    raise KeyError(qid+'/'+label)

# ==========================================================================
# 1. QUEBRAS DE PALAVRA (artefato tipográfico da edição 3.1)
# ==========================================================================
BREAKS = [
    ("Piperacilina-Tazobac tam","Piperacilina-Tazobactam"),
    ("Piperacilina-tazobact am","Piperacilina-tazobactam"),
    ("Amoxicilina-Clavulan ato","Amoxicilina-Clavulanato"),
    ("Amoxicilina-clavulan ato","Amoxicilina-clavulanato"),
    ("Ampicilina-Sulbacta m","Ampicilina-Sulbactam"),
    ("Ampicilina-sulbacta m","Ampicilina-sulbactam"),
    ("Ceftazidima-avibacta m","Ceftazidima-avibactam"),
    ("Ceftolozano-tazobac tam","Ceftolozano-tazobactam"),
    ("Sulbactam-durlobact am","Sulbactam-durlobactam"),
    ("Sulfametoxazol-Trim etoprim","Sulfametoxazol-Trimetoprim"),
    ("Sulfametoxazol-Trimetoprim a","Sulfametoxazol-Trimetoprima"),
    ("Ciprofloxacino/ofloxa cino","Ciprofloxacino/ofloxacino"),
    ("Rifampicina/Isoniazi da/Pirazinamida/Eta mbutol","Rifampicina/Isoniazida/Pirazinamida/Etambutol"),
    ("Ceftazidima/Cefepim e","Ceftazidima/Cefepime"),
    ("Vancomicina + Cefta zidima/Tobramicina","Vancomicina + Ceftazidima/Tobramicina"),
    ("a minoglicosídeo/vancomicina/aciclovi r","aminoglicosídeo/vancomicina/aciclovir"),
    ("individualizar se pne umonia/bronquiectas ia","individualizar se pneumonia/bronquiectasia"),
    ("contrain dicação/intolerância","contraindicação/intolerância"),
    ("Moderada/grave/c rônica","Moderada/grave/crônica"),
    ("Clássico/monomic robiano","Clássico/monomicrobiano"),
    ("Abdominal/perine al/ginecológica","Abdominal/perineal/ginecológica"),
    ("homens mais velh os/instrumentaçã o","homens mais velhos/instrumentação"),
    ("foco portal/polimi crobiano","foco portal/polimicrobiano"),
    ("focal/rebaixamento/papiledema/imu nossupressão","focal/rebaixamento/papiledema/imunossupressão"),
    ("sinusal/otogênico/odo ntogênico","sinusal/otogênico/odontogênico"),
    ("Pós-neurocirurgia/hospital ar","Pós-neurocirurgia/hospitalar"),
    ("cefalospori na/beta-lactâmico","cefalosporina/beta-lactâmico"),
    ("bacteremia/endoc ardite","bacteremia/endocardite"),
    ("M etronidazol/clindami cina","Metronidazol/clindamicina"),
    ("etronidazol/clindami cina","etronidazol/clindamicina"),
    ("per sistência/recorrên cia","persistência/recorrência"),
    ("persis tência/recorrência","persistência/recorrência"),
    ("crônica/o dontogênica","crônica/odontogênica"),
    ("escolares/adolesc entes","escolares/adolescentes"),
    ("pele/osso/pneumo nia","pele/osso/pneumonia"),
    ("urinário/abdomina l","urinário/abdominal"),
    ("cateter/TPN/abdo minal","cateter/TPN/abdominal"),
    ("limpa/ortopédica/c ardiovascular","limpa/ortopédica/cardiovascular"),
    ("abdominal/urinário/pul monar","abdominal/urinário/pulmonar"),
    ("tempo-dependent e","tempo-dependente"),
    ("as plenia/alcoolismo/ cirrose","asplenia/alcoolismo/cirrose"),
    ("sinusite crônica/o dontogênica","sinusite crônica/odontogênica"),
    ("possível em saúde /imunossupressão","possível em contexto assistencial/imunossupressão"),
    ("doxiciclina + m etronidazol/clindami cina","doxiciclina + metronidazol/clindamicina"),
    ("NITROFURÂNICOS/FOSFOM","NITROFURÂNICOS/FOSFOMICINA"),
    ("Nitrofurantoí na","Nitrofurantoína"),
    ("adultos/não gestantes","adultos/não gestantes"),
    ("Piperacilina + Tazobac tam","Piperacilina + Tazobactam"),
]
cnt_breaks = 0
def fix_breaks(s):
    global cnt_breaks
    for a, b in BREAKS:
        if a in s:
            cnt_breaks += s.count(a); s = s.replace(a, b)
    return s
walk_strings(doc, fix_breaks)
log('C', 'Livro inteiro',
    'Palavras partidas ao meio, sem hífen, nas colunas estreitas ("Piperacilina-Tazobac tam", "individualizar se pne umonia/bronquiectas ia", "a minoglicosídeo/vancomicina/aciclovi r").',
    f'{cnt_breaks} ocorrências reconstituídas; nova composição usa hifenização pt-BR e larguras de coluna calculadas, eliminando a causa.')

# tags quebradas das fichas A31/A32
for fid in ('A31','A32'):
    t = q(fid)['tags']
    q(fid)['tags'] = [x for x in t if x != 'ICINA']
log('C','Fichas A31 e A32',
    'O rótulo "NITROFURÂNICOS/FOSFOMICINA" aparecia partido em dois chips ("NITROFURÂNICOS/FOSFOM" + "ICINA").',
    'Rótulo reconstituído em um único chip.')

# ==========================================================================
# 2. ORTOGRAFIA / ACENTUAÇÃO
# ==========================================================================
SPELL = [
    (r'otorréia','otorreia'), (r'Otorréia','Otorreia'),
    (r'\bpos-neurocirurgia\b','pós-neurocirurgia'),
    (r'\bpos-exposicao\b','pós-exposição'),
    (r'\bprimario\b','primário'), (r'\bprimarios\b','primários'),
    (r'\bnefromostomia\b','nefrostomia'),
    (r'\bcristaluria\b','cristalúria'),
    (r'\bDisturbio eletrolitico\b','Distúrbio eletrolítico'),
    (r'\bobstruida\b','obstruída'),
    (r'\bserotoninergicas\b','serotoninérgicas'),
    (r'\bestacionaria\b','estacionária'),
    (r'\bproteinas\b','proteínas'),
    (r'\bempiricos\b','empíricos'),
    (r'\banti-pseudomonica\b','antipseudomônica'),
    (r'\banfilaxia\b','anafilaxia'),
    (r'\btecnica\b','técnica'),
    (r'pH < 7\.35','pH < 7,35'),
    (r'\bChlamydophila pneumoniae\b','Chlamydia pneumoniae'),
]
cnt_spell = 0
def fix_spell(s):
    global cnt_spell
    for a,b in SPELL:
        s2 = re.sub(a,b,s)
        if s2 != s: cnt_spell += 1
        s = s2
    return s
walk_strings(doc, fix_spell)
log('C','Livro inteiro',
    'Grafias fora do Acordo Ortográfico e acentos ausentes: "otorréia" (12×), "pos-neurocirurgia", "primario", "nefromostomia", "cristaluria", "obstruida", "anfilaxia", "pH < 7.35", entre outras.',
    'Corrigidas; separador decimal padronizado em vírgula.')

# "e" no lugar de "é"
ACC = [
 ("5 DIAS E SUFICIENTE","5 DIAS É SUFICIENTE"),
 ("CULTURA DE ESCARRO E CHAVE","CULTURA DE ESCARRO É CHAVE"),
 ("o tratamento definitivo e controle de fonte","o tratamento definitivo é o controle de fonte"),
 ("Cobertura anaerobicida e mais relevante","Cobertura anaerobicida é mais relevante"),
 ("o tratamento central e drenagem/desobstrução biliar","o tratamento central é a drenagem/desobstrução biliar"),
 ("Drenagem biliar e pilar do tratamento","Drenagem biliar é pilar do tratamento"),
 ("o ponto decisivo e controle cirúrgico/intervencional de fonte","o ponto decisivo é o controle cirúrgico/intervencional da fonte"),
 ("A maioria das gastroenterites agudas e viral/autolimitada","A maioria das gastroenterites agudas é viral/autolimitada"),
 ("A prioridade e hidratação e reconhecimento de gravidade","A prioridade é hidratação e reconhecimento de gravidade"),
 ("A prioridade absoluta e reidratação agressiva","A prioridade absoluta é a reidratação agressiva"),
 ("Hidratação e tratamento principal","Hidratação é o tratamento principal"),
 ("quando a suspeita e alta","quando a suspeita é alta"),
 ("Infecção de via biliar obstruída","Infecção de via biliar obstruída"),
]
cnt_acc = 0
def fix_acc(s):
    global cnt_acc
    for a,b in ACC:
        if a in s: cnt_acc += 1; s = s.replace(a,b)
    return s
walk_strings(doc, fix_acc)
log('C','Capítulos 01, 06, 07',
    'Verbo "é" grafado como conjunção "e", invertendo o sentido de 11 frases ("o tratamento definitivo e controle de fonte", "A prioridade e hidratação", "5 DIAS E SUFICIENTE").',
    'Frases corrigidas.')

# ==========================================================================
# 3. TERMINOLOGIA (resíduos da versão em aplicativo)
# ==========================================================================
TERM = [
 (r'\bO app não substitui\b','Este guia não substitui'),
 (r'Via real é tópica cutânea; mantido como VO por limitação atual do schema\.',''),
 (r'\bRevisão do card\b','Revisão da ficha'),
 (r'Não usar o card combinado como prescrição única','Não usar este quadro como prescrição única'),
 (r'Nunca tratar o neonato por este card','Nunca tratar o neonato por este quadro'),
 (r'\busar módulo Sepse\b','ver o capítulo 16 — Sepse'),
 (r'\bUsar módulo específico\b','Usar o quadro específico do foco'),
 (r'\busar módulo específico\b','usar o quadro específico do foco'),
 (r'\bEscolher no módulo específico\b','Escolher no quadro específico'),
 (r'\bEscolher esquema do módulo específico\b','Escolher o esquema do quadro específico'),
 (r'\bmódulo Sepse/Hospitalares\b','capítulos 16 e 18'),
 (r'\bCMI\b','CIM'), (r'\bMIC\b','CIM'),
]
cnt_term = 0
def fix_term(s):
    global cnt_term
    for a,b in TERM:
        s2 = re.sub(a,b,s)
        if s2 != s: cnt_term += 1
        s = s2
    return s
walk_strings(doc, fix_term)
log('C','Capítulos 14, 16, 19 e fichas',
    'Terminologia de aplicativo remanescente no livro: "o app", "card", "módulo", "schema" — inclusive uma nota interna de desenvolvimento publicada em 14.7 ("mantido como VO por limitação atual do schema").',
    'Substituída por terminologia editorial (quadro, ficha, capítulo); nota interna removida. "MIC/CMI" unificados em "CIM".')

json.dump(doc, open('doc_fix1.json','w'), ensure_ascii=False, indent=1)
json.dump(LOG, open('log1.json','w'), ensure_ascii=False, indent=1)
print('etapa 1 ok — quebras:',cnt_breaks,'ortografia:',cnt_spell,'acentos-é:',cnt_acc,'termos:',cnt_term)
