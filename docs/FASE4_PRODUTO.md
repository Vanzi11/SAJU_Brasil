# Fase 4 concluída — Backend HTTP + UI de teste (18/07/2026)

## O que foi implementado

Pasta `app/` com o backend do produto, **sem nenhuma dependência externa** (Node ≥ 18 puro):

| Rota | Método | Função |
|---|---|---|
| `/` | GET | UI de teste (formulário com abas: leitura, sinastria, diária) |
| `/cidades?q=` | GET | Autocomplete das 74 cidades brasileiras (busca sem acento/caixa) |
| `/leitura` | POST | `{data, hora?, cidade, sexo, gerarRelatorio?}` → leitura traduzida + prompt pronto |
| `/sinastria` | POST | `{pessoa1, pessoa2, gerarRelatorio?}` → dados cruzados + prompt |
| `/diaria` | POST | `{data, hora, cidade, sexo, alvo?}` → scores do dia, cor e direção da sorte em pt-BR |

## Como rodar

```bash
cd fortuneteller && npm install && npm run build && cd ..
node app/server.mjs
# abre http://localhost:3333
```

O servidor define `TZ=Asia/Seoul` internamente (requisito do motor). Porta via `PORT` (padrão 3333).

## Recursos

**Hora desconhecida**: se `hora` for omitida na leitura/sinastria, o cálculo usa 12:00 como referência interna, o **pilar da hora é removido** da resposta (leitura de 3 pilares, prática tradicional) e a flag `horaDesconhecida: true` é incluída — o prompt de LLM automaticamente não menciona o pilar da hora, pois ele não está no JSON.

**Relatório narrativo integrado**: com a variável `ANTHROPIC_API_KEY` definida e `gerarRelatorio: true` no body, o backend chama a API da Anthropic (modelo via `SAJU_LLM_MODEL`, padrão `claude-sonnet-5`) e devolve o relatório pronto no campo `relatorio`. Sem a chave, devolve o `prompt` para o app chamar o LLM que preferir.

## Testes executados (todos ✅)

`/cidades?q=sao` → 6 cidades; `/leitura` sem hora → 3 pilares + flag + 10 ciclos de década; `/sinastria` SP×Manaus → score 53, harmonia 40, prompt completo; `/diaria` → scores + "vermelho"/"sul" traduzidos; `/` → UI servida.

## Novidades no i18n (Fase 4)

`pt_br.ts` ganhou `CORES_PT` (12 cores), `DIRECOES_PT` (5 direções) e `traduzirDiaria()` — a sorte diária agora sai 100% em português (o conselho textual coreano é omitido; pode ser gerado pela camada LLM).

## Pendências para produção

Expandir tabela de cidades para os 5.570 municípios IBGE (estrutura pronta — basta popular `brazil_cities.ts`); rate limiting e autenticação no backend; HTTPS/deploy (o motor já traz `railway.json` e Docker como referência); UI definitiva do app (a atual é painel de teste para desenvolvimento).
