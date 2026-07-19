# CONTINUIDADE — Leia isto primeiro

Você é a IA que assume a construção da **Saju Brasil** — empresa de relatórios de autoconhecimento baseados no Saju (Quatro Pilares, tradição coreana), vendidos online para o público brasileiro. Este documento transfere todo o contexto da sessão anterior (Claude Fable 5, jul/2026). O dono do projeto é o **Ivã** (trate no masculino; ele é leigo em programação — explique comandos passo a passo, PowerShell no Windows).

## Ordem de leitura obrigatória

1. Este arquivo inteiro.
2. `empresa/EMPRESA.md` → `empresa/GUIA_DE_VOZ.md` → `empresa/DECISOES.md` (D1–D13) → `empresa/PESQUISA_MERCADO.md`
3. `relatorios/prompts/` (os 3 system prompts — ativos centrais)
4. O README.md de cada pasta antes de mexer nela.

## O que já está PRONTO (não refazer)

**Motor de cálculo** (`fortuneteller/`): fork do saju-mcp-server (MIT) com adaptações nossas — nascimentos no Brasil (74 cidades, timezone IANA com horário de verão histórico, correção de longitude; `src/data/brazil_cities.ts` + `src/utils/date.ts`), i18n completo pt-BR (`src/data/i18n/pt_br.ts`). Compilar: `npm install && npm run build`. SEMPRE rodar com `TZ=Asia/Seoul` (o server.mjs já define sozinho). Testes validados: DST, 4 fusos, fronteiras de pilar, regressão coreana.

**Backend** (`app/server.mjs`): rotas /leitura, /sinastria (4 tipos de relação), /diaria, /cidades, /pdf. UI de teste em `app/public/`. Fluxo de produção: motor calcula JSON → prompt → LLM escreve → revisão humana → PDF → e-mail.

**Prompts dos relatórios** (`relatorios/prompts/`): voz aprovada (mulher madura, vivida e acolhedora; honestidade acolhedora; estrutura V3 com frases fixas da casa). O relatório-padrão de qualidade é `relatorios/exemplos/relatorio_iva_premium_demonstracao.md`.

**Dois produtos prontos**: Leitura Individual (R$ 47, entrada) e Leitura Premium (R$ 197) — texto e cálculo 100%; PDF do Premium com visual aprovado (ver abaixo).

## REGRAS INVIOLÁVEIS (a identidade da empresa)

1. **Concordância de gênero** pelo campo `sexo` em TODO texto gerado — revisar cada adjetivo/particípio. Foi falha real de concorrente que revoltou o dono; é a regra nº 1 de todos os prompts.
2. **Fidelidade ao JSON do motor** — nenhum relatório afirma o que não está calculado. Campo ausente = assunto ausente.
3. **Slogan**: "Não é sobre prever sua vida — é sobre entender seus padrões para decidir melhor." + 4 frases-síntese fixas (ver GUIA_DE_VOZ).
4. **Anti-misticismo**: proibido destino escrito, energia cósmica, universo conspira, galáxias/mandalas/tarô/cristais no visual. Saju sempre com orgulho da origem coreana, vocabulário comportamental.
5. **Disclaimer padrão** no fim de todo relatório + tendência (nunca previsão absoluta) + nunca aconselhar começar/terminar relações ou decisões médicas/financeiras.
6. Toda decisão nova → registrar em `empresa/DECISOES.md` com número sequencial.

## TAREFA Nº 1 — CONCLUÍDA (19/07/2026, sessão Claude Fable 5 / Claude Sonnet 5 Cowork)

**Parametrização do gerador de PDF v5** (`app/pdf/premium_v5/build_pdf.py`) feita: agora recebe `python build_pdf.py entrada.json saida.pdf` (mesma interface do v4) e está ligado no endpoint `/pdf` do `server.mjs` (só para `produto === 'premium'` — o essencial continua no v4, ver pendência 1 abaixo). Capítulos narrativos fluem a partir de `dados['relatorio']` (parse de `##`/`###`) com paginação automática de verdade (quebra até no meio de um parágrafo); "Resumo de bolso" e nota final são extraídos do relatório com fallback 100% no JSON do motor; pilares/ciclos continuam data-driven (nunca da prosa do LLM); hanja trocado de CID não-incorporada para TTF embutida (`malgun.ttf`/Droid/Noto, com degradação graciosa se nenhuma existir); reincluídos a frase de reanálise + selo vermelho na última página; título de capítulo nunca vaza a margem (encolhe e cai pra 2 linhas se precisar). Testado com o mapa real do Ivã, um mapa sintético adversarial (hora desconhecida, outro Mestre do Dia, título de capítulo gigante, sem relatório) e fim-a-fim via `/pdf` com o motor real. Detalhes completos em DECISOES.md → D14.

**Limite conhecido, não bloqueante**: se o LLM escrever termos coreanos em **hangul** solto na prosa (ex.: 십성), a fonte precisa ter cobertura de hangul, não só hanja — `malgun.ttf` no Windows cobre os dois; no Linux de teste deste sandbox só havia hanja disponível (Noto Serif/Sans CJK aqui são CFF, que o reportlab não lê — caiu pro Droid, hanja-only). Como D12 já pede hanja nos visuais e não hangul, isso não deveria aparecer na prática, mas fica registrado.

## Demais pendências (ordem sugerida)

1. PDF do produto Essencial no visual v5 (hoje só existe no v4) — o mesmo motor de capítulos dinâmicos de `build_pdf.py` pode ser reaproveitado, só falta a versão mais enxuta do layout.
2. Sinastria: prompt pronto; falta PDF próprio (decisão D11: acentos VERMELHOS amorosa / DOURADOS societária).
3. DIRECAO_DE_ARTE.md — escrever após Ivã aprovar o v5 parametrizado página a página (D13). Com a parametrização pronta, dá pra gerar PDFs de mapas variados pra essa revisão.
4. Pré-lançamento: política de reembolso, LGPD/consentimento no formulário, transparência de IA, meta de validação (ver Pendências em DECISOES.md).
5. EMPRESA.md v1.1 (portfólio atualizado: entrada R$47, sinastria R$49,90, Mapa Completo do Parceiro R$99,90 como bump, Premium R$197, Clube R$27,90 depois).
6. Expandir cidades para base IBGE completa; sorte diária como conteúdo de Instagram.

## Como gerar um relatório hoje (fluxo completo)

```
cd fortuneteller && npm install && npm run build && cd ..
node app/server.mjs          # abre http://localhost:3333
# Windows: pip install reportlab pypdf  (para o PDF)
```
Na UI: aba Leitura → dados + produto → gerar. Sem ANTHROPIC_API_KEY o texto narrativo não sai (aparece o prompt pronto — pode ser colado em qualquer Claude); com a chave, sai automático.

## Estilo de colaboração com o Ivã

Ele decide, você executa e critica com franqueza — ele gosta de discutir antes de executar mudanças grandes e de registrar decisões. Sempre: commits com mensagens claras ao fim de cada rodada (ele roda git no PowerShell — lembre que `&&` não funciona lá; comandos em linhas separadas). Apresente arquivos criados. Não gaste tokens dele com verificações visuais desnecessárias — ele mesmo revisa os PDFs e traz feedback.
