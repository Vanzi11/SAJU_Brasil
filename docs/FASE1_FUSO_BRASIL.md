# Fase 1 concluída — Fuso horário Brasil (18/07/2026)

## O que foi implementado

Nascimentos em cidades brasileiras agora são calculados corretamente, mantendo o fluxo coreano 100% intacto (regressão testada).

### Arquivos modificados/criados

| Arquivo | Mudança |
|---|---|
| `fortuneteller/src/data/brazil_cities.ts` | **Novo.** 74 cidades (27 capitais + grandes cidades + Fernando de Noronha) com longitude e timezone IANA. Busca tolerante a acentos/caixa ("Sao Paulo" = "São Paulo") |
| `fortuneteller/src/utils/date.ts` | Nova função `getAdjustedBirthInstantBrazilForSaju`; `getAdjustedBirthInstantForSaju` roteia cidades brasileiras automaticamente |
| `fortuneteller/src/data/longitude_table.ts` | `resolveBirthCityForSaju` reconhece cidades brasileiras (antes caía no default Seul) |
| `fortuneteller/src/schemas/index.ts` | Descrição do campo `birthCity` atualizada |
| `tests/test_brasil.mjs` | Suíte de validação Brasil |

### Como funciona

1. A hora civil de nascimento é interpretada na timezone IANA da cidade (ex.: `America/Sao_Paulo`). **O horário de verão histórico brasileiro (1931–2019) é aplicado automaticamente** pela base IANA — quem nasceu em DST tem a 1h descontada sem configuração extra.
2. O instante UTC é convertido em hora solar média local: `UTC + longitude × 4 min/grau`.
3. Os dígitos resultantes são re-ancorados em `Asia/Seoul`, porque todo o pipeline de pilares do motor lê o instante renderizado em KST. Assim dia e hora extraídos são exatamente a hora solar verdadeira do local brasileiro.

Convenção adotada: o pilar do dia usa a **data solar local do nascimento** (escola do meridiano local), não a data coreana.

## Testes executados (todos ✅)

| Caso | Resultado |
|---|---|
| A. SP 01/01/1990 12:00 (horário de verão, UTC−2) | solar 10:53 ✓ |
| B. SP 15/03/1990 12:00 (sem DST, UTC−3) | solar 11:53 ✓ (A vs B = exatamente 1h → DST comprovado) |
| C. Manaus 01/07/1995 06:00 (UTC−4, sobre o meridiano −60°) | solar 06:00 ✓ |
| D. Rio Branco 01/07/2000 12:00 (UTC−5) | solar 12:29 ✓ |
| E. Fortaleza 01/07/2000 12:00 (UTC−3) | solar 12:26 ✓ |
| F. Fronteira de ramo: SP 11:05 civil → solar 10:58 | pilar da hora 사 (09–11h) ✓ — sem correção seria 오 |
| G. Regressão fluxo coreano (Seul default) | pilares idênticos aos originais ✓ |
| H. Nome sem acento "Sao Paulo" | resolvido para "São Paulo" ✓ |
| E2E via MCP: `analyze_saju` com birthCity São Paulo; sinastria SP×Manaus | ✓ |
| Suíte upstream (`npm test`) | 120/124 — as 4 falhas são pré-existentes do projeto original (verificadas no código intocado) |

## Requisito operacional

Rodar o servidor com `TZ=Asia/Seoul` (o código upstream de pilar do ano/mês usa getters dependentes do fuso do processo). Em produção: `TZ=Asia/Seoul node dist/index.js`.

## Limitações conhecidas

1. Se os dígitos re-ancorados caírem exatamente numa lacuna de DST **coreano** (1948–60, 1987–88), há deslocamento de 1h — janela de poucos minutos por ano nesses períodos, risco desprezível.
2. Hora solar **média** (sem equação do tempo, ±16 min) — mesma aproximação usada pelo motor original para a Coreia. Refinamento opcional na Fase 1.3 do roadmap.
3. 74 cidades cadastradas; expandir com a base IBGE completa (5.570 municípios) quando o app tiver cadastro por autocomplete.
