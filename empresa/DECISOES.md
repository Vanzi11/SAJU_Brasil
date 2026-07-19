# Registro de Decisões — Saju Brasil

Decisões tomadas em conjunto (Ivã + Claude). Nada aqui é imutável, mas mudanças devem ser registradas.

## 18/07/2026

**D1. Marca e posicionamento** — Saju explícito e na frente (nome, domínio, comunicação), aproveitando a onda K-culture. A especificação V3 ("Sistema Oriental de Análise de Perfil") NÃO substitui a marca: vira a **voz** dos relatórios — analítica, comportamental, anti-mística, anti-fatalista.

**D2. Voz dos relatórios** — Uma mulher madura, vivida e acolhedora falando com outra mulher: detalhista, gera identificação, acolhe antes de orientar, nomeia bloqueios com cuidado (honestidade acolhedora — nem o tom "sem filtro" agressivo do concorrente, nem gentileza esquecível).

**D3. Concordância de gênero é regra inviolável** — motivada por falha real de concorrente (relatório pago tratou cliente homem no feminino o texto todo). Regra nº 1 de todos os prompts + item obrigatório do checklist de revisão humana.

**D4. Portfólio de lançamento (3 SKUs)** — Leitura Individual R$ 47 (entrada do funil) · Sinastria R$ 49,90 avulsa com campo "tipo de relação" (amorosa/societária/amizade/familiar — 1 SKU, 4 relatórios distintos) · **Mapa Completo do Parceiro** R$ 99,90 (leitura A + leitura B + sinastria; também é o order bump de +R$ 99 no checkout da entrada) · Premium R$ 197 (upsell) · Clube R$ 27,90/mês (fase 2, após base de clientes).

**D5. Funil (Cenário C da pesquisa)** — entrada R$ 47 → bump Mapa Completo → upsell Premium → Clube como destino de recorrência. Sorte diária do motor vira conteúdo gratuito de Instagram (topo de funil).

**D6. Estrutura de relatório** — adotada a Estrutura V3 (10 seções, frases-síntese fixas da casa) + "Resumo de bolso" compartilhável ao final (dor da K-Fã Conectada; marketing orgânico embutido).

**D7. Especificação SAJU AI (91 docs)** — docs de visão/tom/estrutura: absorvidos nos prompts. Docs de engine (13–22): já realizados pelo motor fortuneteller (não construir de novo). Docs de scale-up (RAG, multi-agent, mobile, global): arquivados em `pesquisa/saju-ai-v3/` como visão de futuro — não gastar tempo agora ("antes de sofisticar, simplificar").

**D8. Método declarado** — o produto declara método consistente e reproduzível (motor determinístico, força do mestre por estação/mês). Relatórios de referência do mercado divergem entre si; nossa resposta é transparência metodológica.

## Pendências abertas

- Tipo sanguíneo no Premium: manter como "bônus cultural coreano" rotulado ou trocar por sorte anual mês a mês (tende à troca — mais valor real, já calculado pelo motor).
- Política de reembolso, LGPD e transparência de IA no formulário (obrigatório antes do lançamento).
- Meta de validação concreta (sugestão: X vendas em 60 dias com R$ 500–1.000 de tráfego).
- EMPRESA.md v1.1 consolidando tudo isso.

## 19/07/2026 (madrugada) — Direção de arte

**D9. Direção de arte "Livraria de Seul"** — aplicada primeiro SOMENTE ao Premium (essencial e sinastria herdam depois). Paleta: marfim, roxo profundo, dourado fosco, cinza quente + selo vermelho (dojang 四柱). Moldura finíssima com marcas de canto, pilares como cartas, elementos como círculos de tinta, ilustrações em traço fino por elemento (montanha/bambu/ondas/sol/lua), páginas-respiro com frase única, página final contemplativa fechada no yongsin. Proibições mantidas: nada de galáxia, mandala, cristal, tarô.

**D10. Grid, não caos** — em vez de "nunca repetir layout": 5 templates de página (cheia, dividida, destaque, frase, card) alternados com ritmo. Texturas raster de papel: adiadas (peso de arquivo/risco Canva). Pinceladas reais: futuro investimento em arte comissionada (10 mestres + 5 elementos), pós-validação.

**D11. Sinastria bicolor (futuro)** — identidade por tipo de relação: selo/acentos VERMELHOS para amorosa, DOURADOS para societária/negócios. Registrado para a fase da sinastria.

**D12. Hanja como grafia oficial nos visuais** — caracteres chineses clássicos (甲乙丙…) em vez de hangul nos elementos gráficos: autêntico (carimbos e mapas tradicionais usam hanja) e compatível com as fontes disponíveis.

**D13. Processo visual** — visual primeiro, documentação depois: DIRECAO_DE_ARTE.md será escrita quando o visual for aprovado página a página, para evitar retrabalho.

## 19/07/2026 — PDF v5 parametrizado

**D14. `build_pdf.py` v5 aceita qualquer mapa** — a tarefa nº1 pendente foi concluída: o gerador do Premium (`app/pdf/premium_v5/build_pdf.py`) deixou de ser hard-coded para o mapa do Ivã e passou a receber `entrada.json saida.pdf`, mesma interface do v4. Decisões de parametrização:
- **Capítulos narrativos dinâmicos** — o texto de `relatorio` (escrito pelo LLM a partir de `relatorios/prompts/leitura_premium.md`) é dividido por `##`/`###` em capítulos que fluem com paginação automática (inclusive quebra NO MEIO de um parágrafo se precisar) — o número de páginas do relatório deixou de ser fixo em 18.
- **"Resumo de bolso" e nota final são parseados do relatório** (regex em `**Label:** valor` sob o heading `### ✦ ... 4 linhas`), com fallback 100% derivado do JSON do motor (Mestre do Dia, yongsin, elemento dominante, ciclo atual) quando o relatório ainda não existe ou não segue o padrão — a página de síntese e o disclaimer final nunca ficam vazios.
- **Pilares e ciclos continuam data-driven a partir do JSON do motor** (não do texto livre do LLM), inclusive com 3 colunas quando a hora é desconhecida — mais confiável que tentar extrair datas de prosa.
- **Fonte hanja**: trocada a CID `HeiseiMin-W3` (não embutida) por TTF real, busca por SO (`malgun.ttf` no Windows, `DroidSansFallbackFull`/Noto no Linux — `_cjk_candidates()` em build_pdf.py); se nenhuma for encontrada, os glifos hanja são omitidos (degradação graciosa, nunca quebra o PDF). **Atenção**: no Linux de teste deste sandbox, a Noto Serif/Sans CJK instalada é CFF (PostScript) e o `reportlab` só lê glifos TrueType puros — por isso caiu para o Droid, que cobre hanja mas não hangul. No Windows do Ivã, `malgun.ttf` é TrueType puro e cobre os dois — não deve reproduzir esse limite.
- **Última página**: reincluídos a frase "Recomendamos a reanálise da sua leitura em cerca de um ano." e o selo vermelho 四柱 (tinham sido perdidos na reconstrução do v5).
- **Título de capítulo** com fonte que encolhe automaticamente e cai para 2 linhas se o título do LLM for muito comprido — nunca vaza a margem.
- Testado com o mapa real do Ivã (fidelidade ao v5 original), um mapa sintético (hora desconhecida, outro Mestre do Dia, sem relatório) e via `/pdf` do `server.mjs` fim-a-fim com o motor real.
- `app/server.mjs` agora chama `pdf/premium_v5/build_pdf.py` quando `produto === 'premium'` e mantém `pdf/gerar_pdf.py` (v4) para o essencial.

Pendência que PERMANECE aberta (não fazia parte da tarefa nº1, mas ficou visível): o PDF do produto Essencial ainda não tem visual v5 (item já listado nas "Demais pendências" do CONTINUIDADE.md).

