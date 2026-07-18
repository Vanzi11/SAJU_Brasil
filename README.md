# SAJU Brasil

Base técnica para um aplicativo de leitura de Saju (사주, Quatro Pilares do Destino) individual e sinastria (궁합, gunghap), adaptado para usuários no Brasil.

## O que há neste repositório

| Pasta | Conteúdo |
|---|---|
| `fortuneteller/` | Snapshot completo do código-fonte do servidor MCP [hjsh200219/fortuneteller](https://github.com/hjsh200219/fortuneteller) v1.2.0 (licença MIT) — motor de cálculo de Saju |
| `docs/` | Análise técnica, resultados de testes reais e roadmap de adaptação para o Brasil |
| `tests/` | Scripts de teste JSON-RPC usados para validar o servidor |

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

1. **Fuso horário Brasil** — o cálculo assume nascimento na Coreia (UTC+9, longitude vs. 135°E). Precisamos parametrizar timezone + longitude da cidade de nascimento brasileira, incluindo horário de verão histórico. Detalhes em `docs/ROADMAP.md`.
2. **Tradução pt-BR** — as saídas usam termos coreanos (천간/지지/십성 etc.). Criar camada de tradução dos dados estruturados + glossário.
3. **Relatórios via LLM** — o JSON do motor vira prompt para gerar relatórios interpretativos em português.

## Licença

O código em `fortuneteller/` é MIT (© hjsh200219), o que permite uso comercial com atribuição da licença.
