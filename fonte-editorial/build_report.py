# -*- coding: utf-8 -*-
import json, html, collections
E = lambda s: html.escape(s or '')
L = json.load(open('log_final.json'))
SEV = {'A':('A','Risco de conduta','crit'),
       'B':('B','Diretriz / consistência','att'),
       'C':('C','Editorial e tipográfico','ed')}
order = {'A':0,'B':1,'C':2}
L = sorted(L, key=lambda x: order[x['sev']])
cnt = collections.Counter(x['sev'] for x in L)

rows=[]
n=0
for x in L:
    n+=1
    code, lbl, cls = SEV[x['sev']]
    rows.append(f'''<tr class="{cls}">
<td class="num">{n}</td>
<td class="sev"><span class="badge {cls}">{code}</span></td>
<td class="esc">{E(x['escopo'])}</td>
<td class="ach">{E(x['achado'])}</td>
<td class="cor">{E(x['correcao'])}</td></tr>''')

HTML=f'''<!DOCTYPE html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Relatório de revisão — ATB PRO 4ª edição</title>
<style>
@font-face{{font-family:Source;src:url(fonts/SourceSans3-400.ttf);font-weight:400}}
@font-face{{font-family:Source;src:url(fonts/SourceSans3-600.ttf);font-weight:600}}
@font-face{{font-family:Source;src:url(fonts/SourceSans3-700.ttf);font-weight:700}}
@font-face{{font-family:Source;src:url(fonts/SourceSans3-400-Italic.ttf);font-weight:400;font-style:italic}}
:root{{--ink:#15202b;--ink2:#3d4a58;--ink3:#69757f;--navy:#0b2545;--teal:#0a6a76;
       --rule:#dde3e8;--rule2:#eef2f5;--red:#a01b23;--redbg:#fcf0f0;--amber:#a15c00;--amberbg:#fdf6e7}}
@page{{size:A4 landscape; margin:14mm 13mm 13mm;
 @bottom-left{{content:"Relatório de revisão clínica e editorial · ATB PRO 4ª edição"; font-family:Source; font-size:6.4pt; color:var(--ink3); vertical-align:top; padding-top:3mm}}
 @bottom-right{{content:counter(page); font-family:Source; font-size:7.6pt; font-weight:600; color:var(--navy); vertical-align:top; padding-top:3mm}}}}
@page cover{{margin:0; @bottom-left{{content:none}} @bottom-right{{content:none}}}}
html{{font-family:Source; font-size:9pt; color:var(--ink); font-variant-numeric:tabular-nums}}
body{{margin:0}}
.cv{{page:cover; background:var(--navy); color:#fff; width:297mm; height:210mm; position:relative; break-after:page}}
.cv .b{{position:absolute; left:24mm; top:52mm; right:24mm}}
.cv .k{{font-size:7.6pt; font-weight:700; letter-spacing:.24em; text-transform:uppercase; color:#8fc7d0}}
.cv h1{{font-size:36pt; font-weight:700; line-height:1.05; margin:8mm 0 0; letter-spacing:-.015em}}
.cv .s{{font-size:11.5pt; color:#c8d8e6; margin-top:6mm; max-width:180mm; line-height:1.45}}
.cv .st{{position:absolute; left:24mm; right:24mm; bottom:34mm; display:flex;
        border-top:.6pt solid rgba(255,255,255,.3); border-bottom:.6pt solid rgba(255,255,255,.3)}}
.cv .st div{{flex:1; padding:6mm 0 6mm 7mm; border-left:.6pt solid rgba(255,255,255,.3)}}
.cv .st div:first-child{{border-left:0; padding-left:0}}
.cv .st b{{display:block; font-size:22pt; font-weight:700; line-height:1}}
.cv .st span{{font-size:8pt; color:#9fbdd4}}
.cv .f{{position:absolute; left:24mm; bottom:16mm; font-size:9pt; color:#9fbdd4}}
h2{{font-size:16pt; color:var(--navy); margin:0 0 2mm; letter-spacing:-.01em}}
.lead{{font-size:9pt; color:var(--ink2); line-height:1.5; max-width:230mm; margin-bottom:5mm}}
.leg{{display:flex; gap:5mm; margin-bottom:5mm; font-size:8pt}}
.leg div{{flex:1; border-left:2.4pt solid; padding:2mm 0 2mm 3mm; line-height:1.4}}
.leg .crit{{border-color:var(--red)}} .leg .att{{border-color:#e6b64d}} .leg .ed{{border-color:var(--teal)}}
.leg b{{display:block; color:var(--navy)}}
table{{width:100%; border-collapse:collapse; font-size:7.7pt; line-height:1.4}}
thead{{display:table-header-group}}
th{{text-align:left; font-size:6.5pt; font-weight:700; letter-spacing:.1em; text-transform:uppercase;
   color:var(--ink3); padding:0 3mm 1.4mm 0; border-bottom:.7pt solid var(--navy)}}
td{{vertical-align:top; padding:2.2mm 3mm 2.2mm 0; border-bottom:.5pt solid var(--rule2)}}
td:last-child, th:last-child{{padding-right:0}}
tr.crit td{{background:var(--redbg)}}
tr.att td{{background:var(--amberbg)}}
.num{{color:var(--ink3); font-weight:600}}
.badge{{display:inline-block; font-size:7pt; font-weight:700; width:5mm; text-align:center;
        padding:.6mm 0; border-radius:.8mm; color:#fff}}
.badge.crit{{background:var(--red)}} .badge.att{{background:var(--amber)}} .badge.ed{{background:var(--teal)}}
.esc{{font-weight:600; color:var(--navy)}}
</style></head><body>
<div class="cv"><div class="b">
<div class="k">Documento de apoio · não integra o livro</div>
<h1>Relatório de revisão clínica<br>e editorial</h1>
<div class="s">Tudo o que mudou entre a 3ª edição (3.1, revisão de 15/08/2026) e a 4ª edição de
<i>Antibioticoterapia no Plantão</i>. Cada linha traz o achado como estava e a correção como ficou,
para validação item a item antes da publicação.</div></div>
<div class="st">
 <div><b>{cnt['A']}</b><span>achados com risco de conduta</span></div>
 <div><b>{cnt['B']}</b><span>divergências de diretriz e consistência</span></div>
 <div><b>{cnt['C']}</b><span>correções editoriais e tipográficas</span></div>
 <div><b>{len(L)}</b><span>achados no total</span></div></div>
<div class="f">Dr. Felipe Frank Pinto · setembro de 2026</div></div>

<h2>Achados e correções</h2>
<p class="lead">Ordenado por severidade. As linhas em vermelho são as que, lidas literalmente por um plantonista,
poderiam levar a uma conduta errada; as em âmbar são divergências em relação à diretriz vigente ou
contradições internas; as demais são editoriais. Nenhuma conduta clínica foi alterada sem que a
justificativa esteja registrada aqui.</p>
<div class="leg">
<div class="crit"><b>A · Risco de conduta</b>Dose, unidade, via, alvo terapêutico ou critério que, seguido como está escrito, muda o tratamento.</div>
<div class="att"><b>B · Diretriz e consistência</b>Discordância em relação à diretriz vigente, contradição entre dois pontos do próprio livro ou lacuna de conteúdo.</div>
<div class="ed"><b>C · Editorial e tipográfico</b>Ortografia, terminologia, repetição, resíduo de sistema e estrutura de página.</div>
</div>
<table>
<col style="width:4%"><col style="width:4%"><col style="width:16%"><col style="width:38%"><col style="width:38%">
<thead><tr><th>#</th><th>Sev.</th><th>Onde</th><th>O que estava</th><th>O que ficou</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table>
</body></html>'''
open('report.html','w').write(HTML)
print('relatório ok —', len(L), 'achados')
