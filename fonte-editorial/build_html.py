# -*- coding: utf-8 -*-
import json, re, html, collections, unicodedata
doc = json.load(open('doc_final.json'))
import re as _re
def _upd(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if isinstance(v,str): o[k]=_re.sub(r'Revisão da ficha: 15/08/2026\.',
                'Conteúdo clínico revisto em 15/08/2026; revisão clínica e editorial da 4ª edição em setembro de 2026.', v)
            else: _upd(v)
    elif isinstance(o,list):
        for i,v in enumerate(o):
            if isinstance(v,str): o[i]=_re.sub(r'Revisão da ficha: 15/08/2026\.',
                'Conteúdo clínico revisto em 15/08/2026; revisão clínica e editorial da 4ª edição em setembro de 2026.', v)
            else: _upd(v)
_upd(doc)
E = lambda s: html.escape(s or '')

EDICAO = '4ª edição · revisão de setembro de 2026'
AUTOR  = 'Dr. Felipe Frank Pinto'

def bullets(txt):
    """Converte 'a • b • c' em linhas."""
    parts = [p.strip() for p in re.split(r'\s*•\s*', txt) if p.strip()]
    if len(parts) <= 1: return E(txt)
    return ''.join(f'<span class="bul">{E(p)}</span>' for p in parts)

def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode()
    return re.sub(r'[^a-zA-Z0-9]+','-',s).strip('-').lower()

# ------------------------------------------------------------------ blocos
REL_COL = {'AGENTES E CONTEXTO'}
def render_table(b, header):
    h = b['headers']; rr = b['rows']
    ncol = len(h)
    # larguras por tipo de seção
    W = {
      'AGENTES E CONTEXTO':        ['30%','13%','57%'],
      'ESQUEMAS TERAPÊUTICOS':     ['24%','32%','18%','26%'],
      'ALTERNATIVAS E ALERGIA':    ['24%','32%','18%','26%'],
      'QUANDO AMPLIAR COBERTURA':  ['13%','50%','37%'],
      'CONDUTA PASSO A PASSO':     ['6%','30%','64%'],
      'CRITÉRIOS':                 ['16%','84%'],
      'MICROBIOLOGIA, CONTROLE DE FOCO E STEWARDSHIP': ['17%','83%'],
      '':                          ['32%','44%','24%'],
      'EFEITOS ADVERSOS E INTERAÇÕES': ['50%','50%'],
    }
    widths = W.get(header)
    if not widths or len(widths)!=ncol:
        widths = ['22%'] + [f'{78/max(1,ncol-1):.0f}%']*(ncol-1)
    cols = ''.join(f'<col style="width:{w}">' for w in widths)
    th = ''.join(f'<th>{E(x)}</th>' for x in h)
    body=[]
    for r in rr:
        tds=[]
        for i,cell in enumerate(r):
            cls=''
            if i==0 and header not in ('', 'EFEITOS ADVERSOS E INTERAÇÕES'):
                cls = ' class="step"' if header=='CONDUTA PASSO A PASSO' else ' class="k"'
            if header=='AGENTES E CONTEXTO' and i==1:
                tds.append(f'<td><span class="rel">{E(cell)}</span></td>'); continue
            tds.append(f'<td{cls}>{bullets(cell)}</td>')
        body.append('<tr>'+''.join(tds)+'</tr>')
    note = f'<div class="tnote">{bullets(b["note"])}</div>' if b.get('note') else ''
    return f'<table class="t">{cols}<thead><tr>{th}</tr></thead><tbody>{"".join(body)}</tbody></table>{note}'

SEV_LBL = {'info':'Informação','atencao':'Atenção','critico':'Alerta crítico'}
def render_callout(b):
    sev = b['sev']
    t = re.sub(r'^(INFORMAÇÃO|ATENÇÃO|ALERTA CRÍTICO)\s*·\s*','',b['title']).strip()
    t = t[:1].upper()+t[1:] if t.isupper() and len(t)>28 else t
    return (f'<div class="alert {sev}"><span class="tagx">{SEV_LBL[sev]}</span>'
            f'<div class="at">{E(t)}</div><div class="ab">{bullets(b["body"])}</div></div>')

GEST_LBL = {'aceito':'Gestação: uso aceito','ressalva':'Gestação: com ressalva','evitar':'Gestação: evitar'}
def render_drugs(b):
    rows=[]
    for d in b['rows']:
        gs = f'<span class="gs {d["gest"]}">{GEST_LBL[d["gest"]]}</span>' if d.get('gest') else ''
        via = f'<span class="via">{E(d["via"])}</span>' if d.get('via') else ''
        dose = f'<b>{E(d["padrao"])}</b>'
        if d.get('grave'): dose += f'<br><span class="lab">Grave</span> {E(d["grave"])}'
        notas=[]
        if d.get('teto'): notas.append(f'<span class="lab">Teto</span> {E(d["teto"])}')
        if d.get('hep'):  notas.append(f'<span class="lab">Hepático</span> {E(d["hep"])}')
        if d.get('nota'): notas.append(E(d['nota']))
        rows.append('<tr>'
          f'<td><span class="nm">{E(d["nome"])}</span>{via}{gs}</td>'
          f'<td>{dose}</td>'
          f'<td>{bullets(d.get("renal",""))}</td>'
          f'<td>{"<br>".join(notas)}</td></tr>')
    return ('<table class="dr"><col style="width:22%"><col style="width:30%">'
            '<col style="width:26%"><col style="width:22%">'
            '<thead><tr><th>Fármaco</th><th>Dose</th><th>Função renal</th><th>Observações</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>')

SPEC_LBL={'sim':'cobre','variavel':'depende','nao':'não cobre'}
def render_spectrum(b):
    cells=[]; notes=[]
    for r in b['rows']:
        bg = ' sim-bg' if r['v']=='sim' else (' var-bg' if r['v']=='variavel' else '')
        cells.append(f'<div class="{bg.strip()}"><span class="g">{E(r["grupo"])}</span>'
                     f'<span class="v {r["v"]}">{SPEC_LBL[r["v"]]}</span></div>')
        if r['nota']: notes.append(f'{E(r["grupo"])}: {E(r["nota"])}')
    out = f'<div class="spec">{"".join(cells)}</div>'
    if notes: out += f'<div class="specnotes">{" · ".join(notes)}</div>'
    return out

def render_blocks(sec):
    out=[]
    for b in sec['blocks']:
        if   b['t']=='table':    out.append(render_table(b, sec['header']))
        elif b['t']=='callout':  out.append(render_callout(b))
        elif b['t']=='drugs':    out.append(render_drugs(b))
        elif b['t']=='spectrum': out.append(render_spectrum(b))
        elif b['t']=='ul':
            items=''.join(f'<li>{E(i)}</li>' for i in b['items'] if i.strip())
            if items: out.append(f'<div class="check"><ul>{items}</ul></div>')
        elif b['t']=='sub':      pass
        elif b['t']=='p':
            if b.get('text','').strip(): out.append(f'<p style="font-size:8pt;line-height:1.45">{E(b["text"])}</p>')
    return ''.join(out)

# ------------------------------------------------------------------ quadro
SEC_TITLE = {
 'AGENTES E CONTEXTO':'Agentes e contexto',
 'ESQUEMAS TERAPÊUTICOS':'Esquemas terapêuticos',
 'ALTERNATIVAS E ALERGIA':'Alternativas e alergia',
 'QUANDO AMPLIAR COBERTURA':'Quando ampliar a cobertura',
 'ALERTAS DE SEGURANÇA':'Alertas de segurança',
 'CONDUTA PASSO A PASSO':'Conduta passo a passo',
 'CRITÉRIOS':'Critérios',
 'MICROBIOLOGIA, CONTROLE DE FOCO E STEWARDSHIP':'Microbiologia, controle de foco e stewardship',
 'ANTIMICROBIANOS E AJUSTES':'Antimicrobianos e ajustes',
 'VALIDAÇÃO INSTITUCIONAL':'Validação institucional',
 'ESPECTRO — NÃO SUBSTITUI ANTIBIOGRAMA':'Espectro — não substitui antibiograma',
 'SEGURANÇA E MONITORIZAÇÃO':'Segurança e monitorização',
 'EFEITOS ADVERSOS E INTERAÇÕES':'Efeitos adversos e interações',
 'FONTE E DATA DA FICHA':'Fonte e data da ficha',
}
CRIT_TAGS = {'CRITICA','GRAVE'}
def render_quadro(q, kind='quadro'):
    chips=''.join(
      f'<span class="chip {"crit" if t in CRIT_TAGS else "sev"}">{E(t.replace("CRITICA","CRÍTICA").replace("PEDIATRICO","PEDIÁTRICO"))}</span>'
      for t in q['tags'])
    st=[]
    if q.get('status'):  st.append(f'<b>{E(q["status"])}</b>')
    if q.get('nivel_evid'): st.append(E(q['nivel_evid']))
    if q.get('revisao'): st.append('revisão '+E('/'.join(reversed(q['revisao'].split('-')))))
    if q.get('validacao_nivel'): st.append(f'validação institucional <b>{E(q["validacao_nivel"])}</b>')
    status = f'<div class="status">{" · ".join(st)}</div>' if st else ''
    hero = {f['label']: f for f in q['hero']}
    hc = hero.get('CONDUTA DE PARTIDA', {})
    hv = hero.get('VIA', {}); hd = hero.get('DURAÇÃO', {})
    herohtml = (f'<div class="hero"><div class="main">'
        f'<div class="lbl">Conduta de partida</div>'
        f'<div class="drug">{E(hc.get("title") or hc.get("value",""))}</div>'
        + (f'<div class="dose">{E(hc.get("detail",""))}</div>' if hc.get('detail') else '')
        + '</div><div class="side">'
        + (f'<div><div class="lbl">Via</div><div class="val big">{E(hv.get("detail") or hv.get("value",""))}</div></div>' if hv else '')
        + (f'<div><div class="lbl">Duração</div><div class="val">{E(hd.get("detail") or hd.get("value",""))}</div></div>' if hd else '')
        + '</div></div>') if hero else ''
    secs=[]
    for s in q['sections']:
        inner = render_blocks(s)
        if not inner.strip(): continue
        title = SEC_TITLE.get(s['header'], s['header'].capitalize())
        xref = ''
        if s['header'].startswith('ALTERNATIVAS'):
            xref = ('<div class="xref">Classifique a reação antes de substituir o betalactâmico — '
                    'ver “Alergia a betalactâmico” na abertura e o quadro 19.7.</div>')
        secs.append(f'<div class="sec"><h4>{E(title)}</h4>{xref}{inner}</div>')
    refs=''
    if q.get('ref_especifica') or q.get('ref_links'):
        items=''.join(f'<div>{E(r)}</div>' for r in q.get('ref_especifica',[]))
        links=''.join(f'<div><a href="{E(l)}">{E(l)}</a></div>' for l in q.get('ref_links',[]))
        refs=f'<div class="refs"><span class="lab">Referência do quadro</span>{items}{links}</div>'
    top = (f'<div class="qtop"><div class="hd"><div class="id">{E(q["id"])}</div><h3>{E(q["title"])}</h3>'
           f'<div class="chips">{chips}</div>{status}</div>'
           + (f'<p class="intro">{E(q["intro"])}</p>' if q.get('intro') else '')
           + herohtml + '</div>')
    return (f'<section class="{kind}" id="q-{slug(q["id"])}">' + top + ''.join(secs) + refs + '</section>')

# ------------------------------------------------------------------ pré-textuais
nq = sum(len(c['quadros']) for c in doc['chapters'])
nf = len(doc['fichas'])
cover = f'''<div class="cover"><div class="rule"></div><div class="inner">
<div class="eyebrow">Guia clínico de bolso</div>
<h1><span>Antibioticoterapia</span><span>no Plantão</span></h1>
<div class="sub">Decisão antimicrobiana à beira do leito: síndrome por síndrome, com dose, via, duração, critérios de gravidade e plano de descalonamento.</div>
</div>
<div class="stats">
 <div class="stat"><b>{nq}</b><span>quadros clínicos</span></div>
 <div class="stat"><b>{len(doc["chapters"])}</b><span>sistemas</span></div>
 <div class="stat"><b>{nf}</b><span>antimicrobianos</span></div>
</div>
<div class="foot"><div class="aut">{AUTOR}</div><div class="ed">{EDICAO}</div></div></div>'''

AVISO = '''<section class="front">
<div class="kicker">Leia antes de usar</div>
<h2>Aviso clínico e médico-legal</h2>
<p class="lead">Este guia é ferramenta de apoio à decisão dirigida a profissionais de saúde. Não é prescrição
automática nem protocolo institucional, e não substitui exame presencial, julgamento clínico, bula,
CCIH, infectologia ou a microbiologia do seu serviço.</p>

<h3>Antes de prescrever — em todos os quadros</h3>
<ul>
<li>Confirme diagnóstico, gravidade, alergias e o tipo de reação prévia.</li>
<li>Confirme peso atual, função renal e hepática, gestação e lactação, e interações.</li>
<li>Colha culturas quando mudarem a conduta, sem atrasar terapia tempo-dependente.</li>
<li>Considere controle de foco, epidemiologia local, resistência e disponibilidade institucional.</li>
<li>Reavalie em 24–72 h para descalonar, trocar a via e limitar a duração.</li>
</ul>
<p style="color:#69757f;font-size:8pt">Este bloco vale para todos os quadros do livro e por isso não é repetido em cada página.</p>

<h3>Política editorial</h3>
<p>Brasil e SUS como padrão; alternativas internacionais aparecem explicitamente identificadas.
Cada quadro exibe, no cabeçalho, um selo com o nível da sua referência:</p>
<table class="defs">
<tr><td class="k">Verificado</td><td>Há diretriz dedicada àquela síndrome, identificada na própria página.</td></tr>
<tr><td class="k">Revisão parcial</td><td>Há diretriz pertinente, mas parte das doses ou durações vem de fonte farmacêutica ou de prática consolidada.</td></tr>
<tr><td class="k">Bibliografia de capítulo</td><td>Não há diretriz dedicada ao tema; a conduta é sustentada pela bibliografia do capítulo e por prática consolidada. Doses exigem validação institucional.</td></tr>
</table>
<p>A bibliografia de capítulo, consolidada e sem repetições, fecha cada capítulo. A bibliografia de capítulo
não deve ser lida como validação individual de cada dose.</p>
<p>A data que aparece no selo de cada quadro é a da última verificação clínica registrada para aquele tópico.
Sobre ela, esta 4ª edição aplicou uma revisão clínica e editorial transversal, síndrome por síndrome,
concluída em setembro de 2026 — o que mudou está documentado no relatório de revisão que acompanha esta edição.</p>
<p style="margin-top:4mm;color:#69757f;font-size:8pt">O selo <b>validação institucional</b> indica o quanto aquela conduta depende do
protocolo, do antibiograma e da disponibilidade do seu serviço: <b>dispensável</b>, <b>recomendada</b> ou <b>obrigatória</b>.</p>
</section>'''

COMO = '''<section class="front">
<div class="kicker">Como ler</div>
<h2>A anatomia de um quadro</h2>
<p class="lead">Todos os quadros clínicos seguem a mesma sequência. Ela foi desenhada para que a
primeira decisão esteja sempre no alto da página e o refinamento venha depois.</p>
<table class="defs">
<tr><td class="k">Conduta de partida</td><td>O bloco escuro no alto da página. Fármaco, dose, via e duração para o cenário mais frequente. É ponto de partida, não dispensa a leitura dos critérios e alertas.</td></tr>
<tr><td class="k">Agentes e contexto</td><td>Patógenos prováveis e o que torna cada um mais provável naquele paciente.</td></tr>
<tr><td class="k">Esquemas terapêuticos</td><td>Dose, via, duração e observações, organizados por gravidade e por risco de resistência.</td></tr>
<tr><td class="k">Alternativas e alergia</td><td>Separa alergia verdadeira, intolerância, reação tardia grave e necessidade de especialista.</td></tr>
<tr><td class="k">Quando ampliar a cobertura</td><td>Critérios objetivos para acrescentar MRSA, Pseudomonas, ESBL ou anaeróbios — e apenas eles.</td></tr>
<tr><td class="k">Alertas de segurança</td><td>Três níveis. <b>Informação</b>: contexto útil. <b>Atenção</b>: erro frequente. <b>Alerta crítico</b>: erro que muda desfecho.</td></tr>
<tr><td class="k">Conduta passo a passo</td><td>A sequência operacional, do reconhecimento à reavaliação.</td></tr>
<tr><td class="k">Critérios</td><td>Internação, UTI, gravidade e falha terapêutica.</td></tr>
<tr><td class="k">Microbiologia e stewardship</td><td>Culturas, controle de foco, marco da duração, descalonamento e transição EV → VO.</td></tr>
<tr><td class="k">Antimicrobianos e ajustes</td><td>Dose padrão e de gravidade, ajuste renal, teto, ajuste hepático e monitorização. O selo ao lado do fármaco resume gestação e lactação.</td></tr>
</table>
<h3>Selos de gestação e lactação</h3>
<table class="defs">
<tr><td class="k"><span class="gs aceito" style="font-family:Source">Gestação: uso aceito</span></td><td>Experiência clínica geralmente favorável quando há indicação. Considerar idade gestacional, função orgânica e foco; em lactação, avaliar o lactente.</td></tr>
<tr><td class="k"><span class="gs ressalva" style="font-family:Source">Gestação: com ressalva</span></td><td>Uso possível dentro de um recorte específico, com a restrição indicada no próprio quadro.</td></tr>
<tr><td class="k"><span class="gs evitar" style="font-family:Source">Gestação: evitar</span></td><td>Escolher alternativa específica para o foco; usar apenas se o benefício superar claramente o risco e não houver opção adequada.</td></tr>
</table>
</section>'''

ALERGIA = '''<section class="front">
<div class="kicker">Página de consulta rápida</div>
<h2>Alergia a betalactâmico em uma página</h2>
<p class="lead">Rotular um paciente como alérgico à penicilina sem classificar a reação leva a esquemas
inferiores, mais tóxicos e mais caros. Esta página vale para todos os quadros do livro; o quadro 19.7
traz a versão operacional para o plantão.</p>
<h3>Primeiro: que reação foi essa?</h3>
<table class="defs">
<tr><td class="k">Efeito adverso ou intolerância</td><td>Náusea, diarreia, cefaleia. Não é alergia. O betalactâmico de escolha pode ser mantido.</td></tr>
<tr><td class="k">Reação tardia leve</td><td>Exantema maculopapular após dias, sem sinais sistêmicos. Baixo risco de reação imediata; cefalosporina de cadeia lateral distinta costuma ser segura.</td></tr>
<tr><td class="k">Reação imediata (IgE)</td><td>Urticária, angioedema, broncoespasmo, hipotensão em minutos a poucas horas. Evitar o fármaco implicado; escolher por cadeia lateral ou considerar dessensibilização em infecção crítica.</td></tr>
<tr><td class="k">Reação cutânea grave tardia</td><td>SSJ/NET, DRESS, PEGA, nefrite intersticial, citopenia. Contraindica a classe implicada. Não fazer teste ou desafio no pronto-socorro.</td></tr>
</table>
<h3>Depois: o que isso muda</h3>
<ul>
<li>A reatividade cruzada entre penicilinas e cefalosporinas depende sobretudo da <b>cadeia lateral</b>, não do anel betalactâmico. Cefalosporinas de cadeia lateral distinta são frequentemente seguras mesmo com história de reação imediata a penicilina.</li>
<li>Carbapenêmicos têm reatividade cruzada baixa com penicilinas.</li>
<li>Aztreonam não tem reatividade cruzada relevante com penicilinas e cefalosporinas — exceto ceftazidima, com quem compartilha cadeia lateral.</li>
<li>Em infecção grave na qual o betalactâmico é claramente superior, a dessensibilização é uma opção real e deve ser discutida em vez de aceitar um esquema inferior.</li>
<li>Registre no prontuário <b>qual</b> fármaco, <b>quanto tempo</b> depois e <b>quais</b> sintomas. Um rótulo sem descrição perpetua o erro por anos.</li>
</ul>
</section>'''


APRESENTACOES = """<section class="front" id="f-apresentacoes">
<div class="kicker">Antes de prescrever</div>
<h2>Apresentações disponíveis no Brasil</h2>
<p class="lead">Uma dose correta pela diretriz pode não existir na farmácia. As diretrizes que sustentam este
livro são majoritariamente norte-americanas e europeias, e várias apresentações que elas usam não têm
registro no Brasil. Esta página reúne os pontos em que a diferença muda a prescrição.</p>

<h3>Onde a apresentação brasileira muda a receita</h3>
<table class="defs">
<tr><td class="k">Amoxicilina</td><td>Cápsula de 500 mg e comprimido de 875 mg. <b>Não há apresentação de 1 g</b>: a dose de 1 g VO 8/8 h da pneumonia comunitária corresponde a duas cápsulas de 500 mg.</td></tr>
<tr><td class="k">Amoxicilina + clavulanato</td><td>Comprimidos de 500/125 mg e 875/125 mg; suspensões de 250/62,5 e 400/57 mg por 5 mL; injetável de 1000/200 mg. <b>A apresentação de liberação prolongada 2000/125 mg (XR) não existe no Brasil.</b> Quando for necessária maior exposição à amoxicilina, associar amoxicilina isolada em vez de aumentar o clavulanato.</td></tr>
<tr><td class="k">Amoxicilina + clavulanato em pediatria</td><td>A dose alta das diretrizes norte-americanas (90 mg/kg/dia de amoxicilina com 6,4 mg/kg/dia de clavulanato) depende da suspensão 600/42,9 mg por 5 mL, proporção 14:1, que não existe aqui. Com a suspensão brasileira (400/57 mg por 5 mL, proporção 7:1), dar até 70 mg/kg/dia por ela e completar com amoxicilina isolada, mantendo o clavulanato em até 10 mg/kg/dia.</td></tr>
<tr><td class="k">Penicilina V</td><td>Comprimido de 500.000 UI (≈ 312 mg) e solução oral de 80.000 UI/mL. <b>Não há comprimido rotulado em miligramas</b>: prescrever em unidades internacionais.</td></tr>
<tr><td class="k">Oxacilina</td><td>Apenas apresentação injetável. Para cobertura antiestafilocócica oral, a opção é cefalexina.</td></tr>
<tr><td class="k">Cefdinir</td><td>Disponível apenas como suspensão oral pediátrica. Não há cápsula para adulto.</td></tr>
<tr><td class="k">Cefpodoxima e cefixima</td><td>Disponibilidade variável. Não contar com elas como plano B sem confirmar no formulário do serviço.</td></tr>
<tr><td class="k">Colírios e pomadas oftálmicas</td><td>As opções com registro nacional são tobramicina 0,3% (colírio e pomada), ciprofloxacino 0,3%, azitromicina 1,5% e as associações oxitetraciclina + polimixina B e neomicina + polimixina B + bacitracina.</td></tr>
</table>

<h3>Citadas na literatura internacional, sem equivalente no Brasil</h3>
<ul>
<li><b>Amoxicilina-clavulanato 2000/125 mg (XR)</b> — usar 875/125 mg 12/12 h, ou 500/125 mg 8/8 h, associando amoxicilina isolada quando for preciso elevar a amoxicilina.</li>
<li><b>Suspensão pediátrica 600/42,9 mg por 5 mL (14:1)</b> — usar a suspensão 400/57 mg por 5 mL e completar com amoxicilina isolada.</li>
<li><b>Dicloxacilina</b> — usar cefalexina por via oral; oxacilina apenas endovenosa.</li>
<li><b>Colírio de polimixina B + trimetoprima</b> — usar tobramicina, ciprofloxacino ou azitromicina colírio.</li>
<li><b>Pomada oftálmica de eritromicina e de bacitracina isolada</b> — usar tobramicina pomada ou as associações disponíveis.</li>
</ul>

<h3>Antimicrobianos de reserva: registro não é o mesmo que disponibilidade</h3>
<p>Ceftazidima-avibactam, ceftolozano-tazobactam, meropenem-vaborbactam, imipenem-relebactam, cefiderocol,
sulbactam-durlobactam, aztreonam-avibactam, fidaxomicina e bezlotoxumabe aparecem nos capítulos hospitalares
como as opções corretas para os respectivos mecanismos de resistência. Nem todos estão registrados no país,
e mesmo os registrados podem não estar padronizados no seu serviço. Antes de contar com qualquer um deles,
confirme com a farmácia clínica e a CCIH — os quadros correspondentes trazem o esquema alternativo para quando
o preferencial não estiver disponível.</p>

<p style="margin-top:5mm;color:#69757f;font-size:8pt">Apresentações e marcas mudam. Esta página reflete a
verificação feita para a 4ª edição; diante de dúvida, confirmar na bula da apresentação efetivamente dispensada
e no formulário da instituição.</p>
</section>"""

# --------------------------------------------------------------- sumário
toc=['<section class="toc front"><div class="kicker">Conteúdo</div><h2>Sumário</h2>']
toc.append('<div class="c"><span class="n"></span><span class="t">Páginas de abertura</span>'
           '<span class="dots"></span><span class="p"></span></div>')
for lbl, hid in (('Aviso clínico e médico-legal','f-aviso'),('A anatomia de um quadro','f-como'),
                 ('Apresentações disponíveis no Brasil','f-apresentacoes'),
                 ('Alergia a betalactâmico em uma página','f-alergia')):
    toc.append(f'<div class="q"><span class="n"></span><span class="t">{lbl}</span>'
               f'<span class="dots"></span><span class="p"><a href="#{hid}"></a></span></div>')
for c in doc['chapters']:
    toc.append(f'<div class="c"><span class="n">{E(c["num"])}</span><span class="t">{E(c["title"])}</span>'
               f'<span class="dots"></span><span class="p"><a href="#c-{c["num"]}"></a></span></div>')
    for q in c['quadros']:
        toc.append(f'<div class="q"><span class="n">{E(q["id"])}</span><span class="t">{E(q["title"])}</span>'
                   f'<span class="dots"></span><span class="p"><a href="#q-{slug(q["id"])}"></a></span></div>')
toc.append('<div class="c"><span class="n"></span><span class="t">Fichas de antimicrobianos</span>'
           '<span class="dots"></span><span class="p"><a href="#fichas"></a></span></div>')
toc.append('<div class="c"><span class="n"></span><span class="t">Índice de antimicrobianos</span>'
           '<span class="dots"></span><span class="p"><a href="#indice"></a></span></div>')
toc.append('</section>')

# --------------------------------------------------------------- corpo
body=[]
for c in doc['chapters']:
    qlist=''.join(
      f'<div><b>{E(q["id"])}</b><span class="tt">{E(q["title"])}</span>'
      f'<span class="pp"><a href="#q-{slug(q["id"])}"></a></span></div>' for q in c['quadros'])
    nota = f'<div class="note">{E(c["nota"])}</div>' if c.get('nota') else ''
    body.append(f'<section class="chapter" id="c-{c["num"]}"><div class="wrap">'
                f'<div class="eyeb">Capítulo</div>'
                f'<div class="num">{E(c["num"])}</div><h2>{E(c["title"])}</h2>'
                f'<div class="meta">{len(c["quadros"])} quadros clínicos neste sistema</div>'
                f'{nota}<div class="qlist">{qlist}</div></div></section>')
    for q in c['quadros']:
        body.append(render_quadro(q))
    if c.get('bibliografia'):
        items=''.join(f'<li>{E(r)}</li>' for r in c['bibliografia'])
        body.append(f'<div class="chapbib"><span class="lab">Bibliografia do capítulo {E(c["num"])} — {E(c["title"])}</span>'
                    f'<ul>{items}</ul></div>')

fichas_intro = doc.get('fichas_intro','')
body.append(f'<section class="chapter" id="fichas"><div class="wrap"><div class="num">A</div>'
            f'<h2>Fichas de antimicrobianos</h2><div class="meta">{nf} fármacos</div>'
            f'<div class="note">{E(fichas_intro)}</div></div></section>')
for q in doc['fichas']:
    body.append(render_quadro(q, kind='quadro ficha'))

# --------------------------------------------------------------- índice
idx = collections.defaultdict(set)
NOISE = {'conduta','procedimento','conforme','não','sem','individualizar','padrão','grave','via','dose'}
BLOCK = {'nao se aplica','sem antibiotico','sem antibiotico inicial','sem antibiotico por marcador isolado',
         'conduta dirigida','estrategia de descalonamento','conforme foco','sem antibiotico automatico',
         'sem antibiotico se estavel','observacao ativa','medidas locais','higiene palpebral',
         'controle local odontologico','incisao e drenagem','drenagem','antibiotico conforme foco'}
ALIAS = {'penicilina g benzatina':'Penicilina benzatina','penicilina benzatina':'Penicilina benzatina',
         'piperacilina + tazobactam':'Piperacilina-tazobactam','piperacilina tazobactam':'Piperacilina-tazobactam',
         'piperacilina-tazobactam':'Piperacilina-tazobactam',
         'smx tmp':'Sulfametoxazol-trimetoprima','tmp smx':'Sulfametoxazol-trimetoprima',
         'sulfametoxazol trimetoprim':'Sulfametoxazol-trimetoprima',
         'sulfametoxazol-trimetoprima':'Sulfametoxazol-trimetoprima',
         'sulfametoxazol trimetoprima':'Sulfametoxazol-trimetoprima',
         'vancomicina vo':'Vancomicina (via oral, para C. difficile)',
         'amoxicilina + clavulanato':'Amoxicilina-clavulanato','amoxicilina clavulanato':'Amoxicilina-clavulanato',
         'amoxicilina-clavulanato':'Amoxicilina-clavulanato',
         'ampicilina + sulbactam':'Ampicilina-sulbactam','ampicilina sulbactam':'Ampicilina-sulbactam',
         'ampicilina-sulbactam':'Ampicilina-sulbactam',
         'ceftazidima avibactam':'Ceftazidima-avibactam','ceftazidima-avibactam':'Ceftazidima-avibactam',
         'trimetoprima sulfametoxazol':'Sulfametoxazol-trimetoprima'}
for c in doc['chapters']:
    for q in c['quadros']:
        for s in q['sections']:
            for b in s['blocks']:
                if b['t']=='drugs':
                    for d in b['rows']:
                        nm = re.split(r'\s+(?:em|dose|conforme)\b', d['nome'])[0].strip(' .')
                        if nm and nm.lower() not in NOISE and len(nm)>3:
                            idx[nm].add((q['id'], slug(q['id'])))
for f in doc['fichas']:
    nm = re.sub(r'^[A-Z]\d+\.\s*','',f['title']).strip()
    idx.setdefault(nm, set())
    idx[nm].add(('ficha', slug(f['id'])))
def norm(s): return unicodedata.normalize('NFKD', s.lower()).encode('ascii','ignore').decode()
merged = {}
for k, v in idx.items():
    key = re.sub(r'\s+',' ', norm(k).replace('-',' ').replace('+',' ')).strip()
    if key in BLOCK or key.startswith('sem antibiotico') or key.startswith('conduta'): continue
    name = ALIAS.get(key, k)
    key2 = re.sub(r'\s+',' ', norm(name).replace('-',' ').replace('+',' ')).strip()
    merged.setdefault(key2, [name, set()])
    merged[key2][1] |= v
entries=[]
for key in sorted(merged):
    name, refs = merged[key]
    def sk(r):
        try: return (0,)+tuple(int(x) for x in r[0].split('.'))
        except: return (1,0,0)
    links=' · '.join(f'<a href="#q-{s}">{E(i)}&nbsp;p.&nbsp;</a>' if i!='ficha'
                     else f'<a href="#q-{s}">ficha&nbsp;p.&nbsp;</a>'
                     for i,s in sorted(refs, key=sk))
    entries.append(f'<div class="e"><b>{E(name)}</b><span>{links}</span></div>')
body.append('<section class="index" id="indice"><div class="kicker">Consulta por fármaco</div>'
            '<h2>Índice de antimicrobianos</h2>'
            '<p class="lead">Onde cada antimicrobiano aparece com dose e ajuste. O número é o do quadro; '
            'em seguida, a página.</p>'
            f'<div class="cols">{"".join(entries)}</div></section>')

HTML = f'''<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Antibioticoterapia no Plantão — {EDICAO}</title>
<link rel="stylesheet" href="style.css"></head><body>
{cover}
{AVISO.replace('<section class="front">','<section class="front" id="f-aviso">')}
<div class="pagebreak"></div>
{COMO.replace('<section class="front">','<section class="front" id="f-como">')}
<div class="pagebreak"></div>
{APRESENTACOES}
<div class="pagebreak"></div>
{ALERGIA.replace('<section class="front">','<section class="front" id="f-alergia">')}
<div class="pagebreak"></div>
{''.join(toc)}
{''.join(body)}
</body></html>'''
open('book.html','w').write(HTML)
print('html ok', len(HTML), 'bytes ·', nq, 'quadros ·', nf, 'fichas ·', len(entries), 'entradas de índice')
