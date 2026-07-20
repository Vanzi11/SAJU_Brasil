# Saju Brasil — Leitura Premium — PDF generator (v5)

Gerador em Python/reportlab do visual "livro de arte de Seul" (D9): relatório
A4 editorial, capa com hanja fantasma, pilares como cartas, elementos como
círculos de tinta, capítulos narrativos com paginação automática e selo
vermelho (dojang).

## Requisitos

- Python 3.9+
- `pip install reportlab pillow`
  (Pillow é opcional em tempo de execução — só é usada para tingir os ícones
  raster dos animais/elementos em `assets/icons/`; sem ela, o gerador cai de
  volta pros ícones vetoriais desenhados à mão)

## Uso

    python build_pdf.py entrada.json saida.pdf

`entrada.json` segue a mesma interface do gerador v4 (`app/pdf/gerar_pdf.py`):

```json
{
  "produto": "premium",
  "nome": "Ivã",
  "idadeAproximada": 43,
  "leitura": { "...saída de traduzirSaju() + ciclosDeDecada..." },
  "relatorio": "markdown escrito pelo LLM a partir de relatorios/prompts/leitura_premium.md, ou null"
}
```

Ligado no endpoint `POST /pdf` do `app/server.mjs` quando `produto === 'premium'`.

## Arquivos

    build_pdf.py                                   # gerador (arquivo único)
    data/relatorio_iva_premium_demonstracao.md      # relatório de referência (Ivã) — bom fixture de teste
    fonts/InstrumentSerif-Regular.ttf
    fonts/InstrumentSerif-Italic.ttf
    fonts/CrimsonPro-Regular.ttf
    fonts/CrimsonPro-Italic.ttf
    fonts/Inter-Regular.ttf
    fonts/Inter-Italic.ttf

## Como funciona a paginação dinâmica

- Páginas fixas/estruturais (capa, colofão, introdução, método, pilares, elementos,
  respiro do Mestre do Dia): 1 página cada, com dados do JSON do motor.
- `dados['relatorio']` é dividido em capítulos por `##` (e `###` para o "Resumo de
  bolso"). Cada capítulo flui com paginação automática — inclusive quebra NO MEIO
  de um parágrafo se o texto for maior que uma página — então o relatório NÃO tem
  mais um número fixo de páginas (o v5 original tinha exatamente 18).
- A seção com heading contendo "ciclo"/"década"/"tempo" dispara também a página de
  linha do tempo dedicada (dados de `leitura.ciclosDeDecada`, não da prosa).
- O heading `### ✦ ... 4 linhas` (ou similar) é extraído com regex `**Label:**
  valor` para a página de síntese; se não existir (relatório ainda não gerado, ou
  formato diferente), a síntese cai para um fallback 100% derivado do JSON do motor.
- Hanja usa uma fonte TTF embutida de verdade (nunca a CID `HeiseiMin-W3`, que não
  embute no PDF) — busca em `_cjk_candidates()`: `malgun.ttf` no Windows,
  `DroidSansFallbackFull`/Noto no Linux. Se nada for encontrado, os glifos hanja
  são simplesmente omitidos (degradação graciosa).

## Testar sem o servidor

Use `data/relatorio_iva_premium_demonstracao.md` (texto real do Ivã) para montar um
`entrada.json` de teste rápido — é o melhor fixture porque exercita todos os
padrões de heading (`##`, `### ✦ 4 linhas`, nota final) que o parser espera.

## Notas

- Paleta, fontes e constantes de layout ficam no topo de `build_pdf.py`.
- Fontes: Instrument Serif e Crimson Pro são OFL, Inter é OFL — ver licenças no
  Google Fonts.
