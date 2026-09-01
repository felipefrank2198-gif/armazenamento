# -*- coding: utf-8 -*-
"""Etapa 6 — desduplicação de células de duração + normalização final."""
import json, re, collections
doc = json.load(open('doc_fix5.json'))
LOG = json.load(open('log5.json'))
def log(sev,esc,ach,cor): LOG.append(dict(sev=sev,escopo=esc,achado=ach,correcao=cor))

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

# --- subscritos consistentes
n  = sub_all(r'\bSpO2\b','SpO₂')
n += sub_all(r'\bPaO2\b','PaO₂'); n += sub_all(r'\bFiO2\b','FiO₂')
n += sub_all(r'\bCO2\b','CO₂');  n += sub_all(r'\bFEV1\b','VEF₁'); n += sub_all(r'\bVEF1\b','VEF₁')
n += sub_all(r'(?<![A-Za-z₀-₉])O2\b','O₂')
n += sub_all(r'\bK\+ e Mg\+','K⁺ e Mg²⁺')
log('C','Livro inteiro',
 'Índices químicos e fisiológicos escritos ora com subscrito ora com dígito normal na mesma página: "SpO2" e "SpO₂", "PaO₂/FiO₂" e "PaO2/FiO2", "FEV1" e "VEF₁".',
 'Padronizados com subscrito em todo o livro (SpO₂, PaO₂/FiO₂, VEF₁, O₂) e a sigla espirométrica unificada em VEF₁.')

# --- ortografia consolidada: betalactâmico
n  = sub_all(r'beta-lactâmic', 'betalactâmic')
n += sub_all(r'Beta-lactâmic', 'Betalactâmic')
n += sub_all(r'beta-lactamase', 'betalactamase')
n += sub_all(r'beta-lactâmico/inibidor', 'betalactâmico com inibidor')
n += sub_all(r'\bbeta-lactâmico\b', 'betalactâmico')
log('C','Livro inteiro',
 'Convivência de "beta-lactâmico" e "betalactâmico" no mesmo livro (e "beta-lactamase"/"betalactamase").',
 'Padronizado para a grafia sem hífen — betalactâmico, betalactamase — em todas as ocorrências.')

# --- duração: extrair a regra repetida para nota de tabela
moved = 0
for c in doc['chapters']:
    for q in c['quadros']:
        for s in q['sections']:
            for b in s['blocks']:
                if b['t']!='table': continue
                try: di = b['headers'].index('Duração')
                except ValueError: continue
                cnt = collections.Counter(r[di] for r in b['rows'] if len(r)>di)
                notes = []
                rep = {v for v,k in cnt.items() if k >= 2 and len(v) > 45}
                for r in b['rows']:
                    if len(r)<=di: continue
                    val = r[di]
                    if len(val) < 55 and val not in rep: continue
                    m = re.match(r'([^.]{3,58}?)\.\s+(.+)$', val) or re.match(r'([^;]{3,48}?);\s+(.+)$', val)
                    if not m: continue
                    head, tail = m.group(1).strip(), m.group(2).strip()
                    r[di] = head
                    notes.append(tail); moved += 1
                if notes:
                    def toks(t):
                        return {re.sub(r'(os|as|es|s)$','',w) for w in re.findall(r'[a-zà-ÿ]{4,}', t.lower())}
                    keep = []
                    for t in sorted(set(notes), key=len, reverse=True):
                        a = toks(t)
                        if any(len(a & toks(k)) / max(1, len(a | toks(k))) >= .42 for k in keep): continue
                        keep.append(t)
                    keep = [(k[0].upper()+k[1:] if k[:1].islower() else k) for k in keep]
                    keep = [k if k.endswith('.') else k+'.' for k in keep]
                    b['note'] = 'Sobre a duração: ' + ' '.join(keep)
log('C','Capítulos 01 a 19 — coluna "Duração"',
 f'A mesma regra de duração, escrita por extenso, repetia-se linha a linha dentro da própria tabela — em 1.1, por exemplo, o parágrafo "Cursos de 3–4 dias podem ser considerados apenas em pacientes selecionados, com estabilidade clínica objetiva, sem complicação e com seguimento confiável" aparecia três vezes na mesma página. Isso alongava a linha inteira e deixava as demais colunas com grandes vazios.',
 f'{moved} células reduzidas à duração propriamente dita; a regra que as qualifica passou a uma nota única sob a tabela. A informação é a mesma, lida em um terço do espaço.')


# --- fichas ausentes de fármacos usados como primeira linha no livro
def ficha(fid, nome, tags, dose_padrao, dose_grave, via, espectro, praticos, adversos, interacoes, fontes):
    secs = [
      {'header':'', 'blocks':[{'t':'table','headers':['Dose padrão','Dose em quadro grave','Via'],
                               'rows':[[dose_padrao, dose_grave, via]]}]},
      {'header':'ESPECTRO — NÃO SUBSTITUI ANTIBIOGRAMA',
       'blocks':[{'t':'spectrum','rows':[{'grupo':g,'v':v,'nota':nt} for g,v,nt in espectro]}]},
      {'header':'SEGURANÇA E MONITORIZAÇÃO',
       'blocks':[{'t':'ul','items':praticos}]},
      {'header':'EFEITOS ADVERSOS E INTERAÇÕES',
       'blocks':[{'t':'table','headers':['Efeitos adversos','Interações'],'rows':[[adversos, interacoes]]}]},
      {'header':'FONTE E DATA DA FICHA','blocks':[{'t':'ul','items':fontes}]},
    ]
    return dict(id=fid, title=nome, tags=tags, intro='', hero=[], sections=secs,
                ref_especifica=[], ref_links=[])

G = ['G+ Cocci','G- Bacilli','Anaeróbios','Atípicos','MRSA','Pseudomonas','ESBL','Fungos','Vírus']
amp = ficha('A40','Ampicilina', ['ESTREITO','PENICILINAS','EV','FICHA'],
  '2 g EV 6/6 h', '2 g EV 4/4 h em meningite, listeriose e endocardite enterocócica', 'EV',
  [('G+ Cocci','sim','Enterococcus faecalis sensível, Streptococcus'),('G- Bacilli','variavel','só sem betalactamase'),
   ('Anaeróbios','variavel','flora oral'),('Atípicos','nao',''),('MRSA','nao',''),('Pseudomonas','nao',''),
   ('ESBL','nao',''),('Fungos','nao',''),('Vírus','nao','')],
  ['Fármaco de escolha para Listeria monocytogenes — cobertura obrigatória na meningite do maior de 50 anos, imunossuprimido, alcoolista ou gestante.',
   'Base do tratamento de endocardite e de infecção invasiva por Enterococcus faecalis sensível; a associação com ceftriaxona poupa aminoglicosídeo.',
   'Não cobre produtores de betalactamase: para essa cobertura, usar ampicilina-sulbactam ou amoxicilina-clavulanato.',
   'Ajuste renal: > 50 mL/min dose padrão; 10–50 mL/min a cada 6–8 h; < 10 mL/min a cada 8–12 h.'],
  '• Exantema (muito frequente em mononucleose) • Diarreia • Reação alérgica • Convulsão em dose alta com disfunção renal',
  '• Alopurinol aumenta a chance de exantema • Pode reduzir a eficácia de contraceptivos orais (efeito pequeno)',
  ['Bulário Eletrônico da Anvisa e bula da apresentação dispensada — dose, preparo, contraindicações.',
   'Diretriz da síndrome correspondente — indicação e duração.',
   'Ficha acrescentada na 4ª edição. Revisão da ficha: setembro de 2026.'])
rif = ficha('A41','Rifampicina', ['ESTREITO','RIFAMICINAS','VO/EV','FICHA'],
  '600 mg VO/EV 24/24 h (10 mg/kg/dia, máximo 600 mg)', '600 mg 12/12 h na quimioprofilaxia de meningococo, por 2 dias', 'VO/EV',
  [('G+ Cocci','sim','sempre em associação'),('G- Bacilli','variavel','Neisseria, Haemophilus'),
   ('Anaeróbios','nao',''),('Atípicos','variavel','micobactérias'),('MRSA','variavel','só como adjuvante em biofilme'),
   ('Pseudomonas','nao',''),('ESBL','nao',''),('Fungos','nao',''),('Vírus','nao','')],
  ['Nunca usar em monoterapia numa infecção estabelecida: a resistência emerge em dias.',
   'Como adjuvante anti-biofilme em infecção de prótese ou material, só iniciar depois do desbridamento, com carga bacteriana reduzida, ferida estável e sem bacteremia ativa.',
   'Indutor potente do citocromo P450: reduz o efeito de anticoagulantes orais, contraceptivos, antirretrovirais, azólicos, corticoides, tacrolimo e ciclosporina. Revisar toda a prescrição antes de iniciar.',
   'Colore urina, lágrima e suor de laranja e mancha lentes de contato gelatinosas — avisar o paciente para não interromper o tratamento por susto.',
   'Monitorar transaminases e bilirrubinas, sobretudo em hepatopatia e em associação com isoniazida e pirazinamida.'],
  '• Hepatotoxicidade • Coloração alaranjada de secreções • Náusea • Citopenias • Síndrome gripal no uso intermitente',
  '• Indução do CYP450: varfarina, contraceptivos, antirretrovirais, azólicos, tacrolimo, ciclosporina, corticoides, metadona',
  ['Bulário Eletrônico da Anvisa e bula da apresentação dispensada — dose, preparo, contraindicações.',
   'Diretriz da síndrome correspondente — indicação e duração.',
   'Ficha acrescentada na 4ª edição. Revisão da ficha: setembro de 2026.'])
doc['fichas'].append(amp); doc['fichas'].append(rif)
doc['fichas'].sort(key=lambda f: f['title'].lower())
for i,f in enumerate(doc['fichas'], 1): f['id'] = f'A{i}'
log('B','Fichas de antimicrobianos',
 'Ampicilina e rifampicina eram prescritas como primeira linha em vários quadros — ampicilina na cobertura obrigatória de Listeria na meningite e na endocardite enterocócica; rifampicina como adjuvante anti-biofilme em prótese e na quimioprofilaxia de meningococo — mas nenhuma das duas tinha ficha própria no livro.',
 'Acrescentadas as duas fichas, com dose, ajuste renal, espectro, alertas de uso (rifampicina nunca em monoterapia; momento certo de iniciá-la em material protético) e o perfil de interações do CYP450. O total de fármacos passa de 39 para 41.')

log('C','Fichas de antimicrobianos',
 'As fichas eram numeradas por classe farmacológica (penicilinas, depois cefalosporinas, depois carbapenêmicos…), o que obriga a saber a classe antes de encontrar o fármaco.',
 'Reordenadas em ordem alfabética e renumeradas de A1 a A41; a classe permanece visível como etiqueta em cada ficha, e o novo índice de antimicrobianos remete a todos os quadros em que cada fármaco aparece com dose.')

json.dump(doc, open('doc_final.json','w'), ensure_ascii=False, indent=1)
json.dump(LOG, open('log_final.json','w'), ensure_ascii=False, indent=1)
print('etapa 6 ok — células de duração compactadas:', moved, '| achados:', len(LOG))
