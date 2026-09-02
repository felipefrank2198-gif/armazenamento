import json, re

doc = json.load(open('doc_final.json'))
LOG = json.load(open('log_final.json'))

def log(sev, esc, ach, cor):
    LOG.append(dict(sev=sev, escopo=esc, achado=ach, correcao=cor))

def sub_all(pat, rep, count=[0]):
    s = json.dumps(doc, ensure_ascii=False)
    new_s, n = re.subn(pat, rep, s)
    count[0] += n
    return new_s, n

s = json.dumps(doc, ensure_ascii=False)

# 1) DISP note: cefpodoxima IS available (Orelox 100/200mg comprimido, uso adulto);
#    cefixima NOT registered for human use in Brazil.
old_disp = ("No Brasil, a cefalosporina oral de alternativa mais disponível é a cefuroxima axetil "
            "(comprimido de 250 e 500 mg e suspensão). O cefdinir existe apenas como suspensão oral "
            "pediátrica; cefpodoxima e cefixima têm disponibilidade variável e podem não ser encontradas. "
            "Confirmar no formulário local antes de prescrever.")
new_disp = ("No Brasil, a cefalosporina oral de alternativa mais disponível é a cefuroxima axetil "
            "(comprimido de 250 e 500 mg e suspensão). O cefdinir existe apenas como suspensão oral "
            "pediátrica. A cefpodoxima está disponível como Orelox comprimido de 100 e 200 mg, mas apenas "
            "para uso adulto — não há suspensão pediátrica registrada no Brasil. A cefixima não tem "
            "registro para uso humano no país e não deve ser prescrita aqui.")
n1 = s.count(old_disp)
s = s.replace(old_disp, new_disp)

old_disp2 = ("A cefalosporina oral de alternativa com apresentação mais estável no Brasil é a cefuroxima "
             "axetil. O cefdinir existe aqui apenas como suspensão oral pediátrica; cefpodoxima e cefixima "
             "têm disponibilidade variável. Priorizar amoxicilina ou amoxicilina-clavulanato e escolher a "
             "alternativa pelo tipo de alergia e pelo formulário do serviço.")
new_disp2 = ("A cefalosporina oral de alternativa com apresentação mais estável no Brasil é a cefuroxima "
             "axetil. O cefdinir existe aqui apenas como suspensão oral pediátrica. A cefpodoxima (Orelox "
             "100/200 mg comprimido) só serve para adulto, sem suspensão pediátrica registrada; a cefixima "
             "não tem registro para uso humano no Brasil. Priorizar amoxicilina ou amoxicilina-clavulanato "
             "e escolher a alternativa pelo tipo de alergia e pelo formulário do serviço.")
n2 = s.count(old_disp2)
s = s.replace(old_disp2, new_disp2)

log("B", "Múltiplos capítulos (11.1, 14.1, 14.2, 14.3, 14.5)",
    "Nota de disponibilidade descrevia cefpodoxima e cefixima igualmente como 'disponibilidade variável'.",
    f"Cefpodoxima tem registro humano no Brasil (Orelox, comprimido 100/200 mg, uso adulto, sem suspensão "
    f"pediátrica); cefixima não tem registro para uso humano no país. Nota reescrita para distinguir as duas "
    f"({n1+n2} ocorrências).")

doc = json.loads(s)

def q(qid):
    for ch in doc.get('chapters', []):
        for quad in ch.get('quadros', []):
            if quad.get('id') == qid:
                return quad
        for fic in ch.get('fichas', []):
            if fic.get('id') == qid:
                return fic
    for fic in doc.get('fichas', []):
        if fic.get('id') == qid:
            return fic
    return None

def sec(qid, prefix):
    quad = q(qid)
    if not quad:
        return None
    for s_ in quad.get('sections', []):
        if s_.get('header', '').startswith(prefix):
            return s_
    return None

def table(qid, prefix):
    s_ = sec(qid, prefix)
    if not s_:
        return None
    for b in s_.get('blocks', []):
        if b.get('t') == 'table':
            return b
    return None

# 2) Quadro 14.5 — ITU pediátrica: cefixima usada como alternativa oral. Trocar por cefuroxima axetil.
quad = q('14.5')
if quad:
    for h in quad.get('hero', []):
        if 'Cefixima' in h.get('value', '') or 'Cefixima' in h.get('title', ''):
            h['value'] = h['value'].replace(
                'Ceftriaxona ou Cefalexina/Cefixima conforme gravidade',
                'Ceftriaxona ou Cefalexina/Cefuroxima axetil conforme gravidade')
            h['title'] = h['title'].replace(
                'Ceftriaxona ou Cefalexina/Cefixima conforme gravidade',
                'Ceftriaxona ou Cefalexina/Cefuroxima axetil conforme gravidade')

    tb = table('14.5', 'ESQUEMAS TERAPÊUTICOS')
    if tb:
        for row in tb['rows']:
            if row and 'Cefixima' in row[1]:
                row[1] = ("Cefalexina ou Cefuroxima axetil · Cefalexina 50–100 mg/kg/dia VO 6/6 h ou "
                           "cefuroxima axetil 20–30 mg/kg/dia VO 12/12 h · VO")
                row[3] = ("Escolher conforme o padrão local e o antibiograma prévio. A cefixima não tem "
                           "registro para uso humano no Brasil; cefalexina e cefuroxima axetil são as "
                           "opções orais disponíveis aqui.")

log("A", "14.5 ITU Febril pediátrica",
    "Conduta oral de manutenção citava cefixima 8 mg/kg/dia, sem registro para uso humano no Brasil.",
    "Substituída por cefuroxima axetil 20–30 mg/kg/dia VO 12/12h como segunda opção junto à cefalexina, "
    "ambas com apresentação pediátrica disponível no país.")

# 3) Quadro de uretrite/gonorreia — cefixima como alternativa à ceftriaxona.
found_gono = False
for ch in doc.get('chapters', []):
    for quad2 in ch.get('quadros', []) + ch.get('fichas', []):
        for s_ in quad2.get('sections', []):
            if s_.get('header', '').startswith('ALTERNATIVAS E ALERGIA'):
                for b in s_.get('blocks', []):
                    if b.get('t') == 'table':
                        for row in b['rows']:
                            if row and 'Cefixima 800 mg' in row[1]:
                                found_gono = True
                                row[1] = ("Cefixima 800 mg VO dose única + doxiciclina 100 mg VO 12/12 h "
                                           "por 7 dias se clamídia não excluída · Reservada a onde a "
                                           "cefixima for obtida por importação/manipulação — não tem "
                                           "registro para uso humano no Brasil · VO")
                                row[3] = ("A cefixima não é comercializada no Brasil. Diante de gonococo "
                                           "e ceftriaxona indisponível, priorize obter/transferir ceftriaxona "
                                           "em vez de contar com esta alternativa; não há substituto oral "
                                           "nacional equivalente validado pelo PCDT.")
if found_gono:
    log("A", "Uretrite/cervicite — alergia e ceftriaxona indisponível",
        "Cefixima listada como alternativa oral prática à ceftriaxona para gonorreia; não tem registro para uso humano no Brasil.",
        "Ressalva reescrita deixando explícito que a cefixima não é comercializada no país e que a conduta "
        "correta é priorizar obter ceftriaxona, não substituir por um fármaco indisponível.")

# 4) Front-matter reference table row.
json.dump(doc, open('doc_final.json', 'w'), ensure_ascii=False, indent=1)
json.dump(LOG, open('log_final.json', 'w'), ensure_ascii=False, indent=1)
print('n1', n1, 'n2', n2, 'gono found', found_gono)
print('achados totais', len(LOG))
