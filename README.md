# SAJU Brasil

Base técnica para um aplicativo de leitura de Saju (사주, Quatro Pilares do Destino) individual e sinastria (궁합, gunghap), adaptado para usuários no Brasil.

## O que há neste repositório

| Pasta | Conteúdo |
|---|---|
| `fortuneteller/` | Motor de cálculo de Saju — base [hjsh200219/fortuneteller](https://github.com/hjsh200219/fortuneteller) v1.2.0 (MIT) + adaptações Brasil (fuso/longitude) + i18n pt-BR |
| `relatorios/` | Camada LLM: prompts pt-BR, pipeline `gerar_prompt.mjs` e relatórios-exemplo |
| `docs/` | Análise técnica, resultados de testes, glossário pt-BR e docs de cada fase |
| `tests/` | Scripts de teste (JSON-RPC, fuso Brasil, tradução) |

## Status da validação (18/07/2026)

O servidor foi instalado e testado com sucesso em Node.js 22. Todas as ferramentas relevantes responderam corretamente: cálculo dos quatro pilares (`analyze_saju`), **sinastria entre duas pessoas** (`check_compatibility`), ciclos de 10 anos (`get_dae_un`), horóscopo diário (`get_daily_fortune`) e análise de amor/carreira/riqueza/saúde. Saídas completas em `docs/RESULTADOS_TESTES.md`.

**Conclusão: o motor cobre leitura individual + sinastria e serve como base do app.** As saídas são JSON estruturado — ideais para alimentar um LLM que gera o relatório final em português.

## Como rodar

```bash
cd fortuneteller
npm install
npm run build
node dist/index.js        # servidor MCP via stdio
# ou: npm run start:http  # modo HTTP (para backend de app)
```

Teste rápido: `node tests/test_mcp.js` (ajuste o caminho `cwd` dentro do script).

## Roadmap de adaptação

1. ~~**Fuso horário Brasil**~~ — ✅ **Concluído (18/07/2026).** Nascimentos em 74 cidades brasileiras com timezone IANA (horário de verão histórico automático) e correção de longitude. Basta passar `birthCity: "São Paulo"` (etc.) nas ferramentas. Detalhes e testes em `docs/FASE1_FUSO_BRASIL.md`. Rodar o servidor com `TZ=Asia/Seoul`.
2. ~~**Tradução pt-BR**~~ — ✅ **Concluído (18/07/2026).** Módulo `src/data/i18n/pt_br.ts` com dicionários completos (troncos, ramos, elementos, dez deuses, 15 sinsal, 14 gyeokguk, 24 termos solares) e `traduzirSaju()` — JSON 100% em português. Ver `docs/FASE2_TRADUCAO.md` e `docs/GLOSSARIO_PT_BR.md`.
3. ~~**Relatórios via LLM**~~ — ✅ **Concluído (18/07/2026).** Pasta `relatorios/`: prompts de leitura individual e sinastria, pipeline `gerar_prompt.mjs` (dados → JSON traduzido → prompt pronto para qualquer API de LLM) e dois relatórios-exemplo reais. Ver `docs/FASE3_RELATORIOS.md`.
4. **Produto (Fase 4)** — backend HTTP (`/leitura`, `/sinastria`, `/diaria`), autocomplete de cidades IBGE, flag "hora desconhecida", UI do app.

## Licença

O código em `fortuneteller/` é MIT (© hjsh200219), o que permite uso comercial com atribuição da licença.
