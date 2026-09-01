# Fonte editorial — Antibioticoterapia no Plantão, 4ª edição

Este diretório contém tudo o que é necessário para gerar novamente o PDF do livro,
sem passar por extração de PDF outra vez. A 5ª edição pode partir daqui.

## O que é cada arquivo

| Arquivo | Para que serve |
|---|---|
| `conteudo.json` | Todo o conteúdo clínico do livro em forma estruturada: 19 capítulos, 162 quadros, 41 fichas, cada bloco identificado por tipo (tabela, alerta, fármaco, espectro). É a fonte da verdade — edite aqui. |
| `achados.json` | Os 44 achados da revisão da 4ª edição, no formato usado pelo relatório. |
| `build_html.py` | Transforma `conteudo.json` no HTML do livro. |
| `build_report.py` | Transforma `achados.json` no PDF do relatório de revisão. |
| `style.css` | Toda a identidade visual: grade, tipografia, cores, tabelas, alertas, capa, sumário e índice. |
| `fonts/` | Source Sans 3 nos pesos usados (SIL Open Font License 1.1). |
| `pipeline/` | Os scripts que reconstruíram o conteúdo a partir do PDF da 3ª edição e aplicaram as correções. Mantidos como registro do que foi feito; não são necessários para gerar novas edições. |

## Como gerar o PDF

```sh
pip install weasyprint
python3 build_html.py     # gera book.html
python3 -c "from weasyprint import HTML; HTML('book.html').write_pdf('book.pdf')"
```

O sumário, os números de página dos capítulos e o índice de antimicrobianos são
calculados automaticamente pelo paginador — não há número de página escrito à mão
em lugar nenhum.

## Como editar o conteúdo

Em `conteudo.json`, cada quadro tem: `id`, `title`, `tags`, `intro`, `hero`
(conduta de partida, via, duração), `sections` e os campos de selo
(`status`, `nivel_evid`, `revisao`, `validacao_nivel`, `ref_especifica`).
Alterar uma dose é alterar a célula correspondente na tabela daquele quadro.

Ao acrescentar uma ficha de antimicrobiano, basta acrescentar o objeto em
`fichas`: a numeração A1…An, a ordem alfabética, a contagem na capa e o índice
remissivo se ajustam sozinhos.
