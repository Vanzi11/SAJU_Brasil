# Resultados dos Testes — 18/07/2026

Ambiente: Node.js v22.22.3, npm 10.9.8, Linux (sandbox). Instalação via `npm install` + `npm run build` (tsc) sem erros. Comunicação via JSON-RPC 2.0/stdio (protocolo MCP 2024-11-05). Scripts em `../tests/`.

Perfis de teste: **P1** masculino, 15/03/1990 10:30 (solar); **P2** feminino, 20/07/1992 14:30 (solar).

## 1. analyze_saju (basic) — P1 ✅

Pilares retornados: ano 경오 (metal/fogo), mês 기묘 (terra/madeira), dia 기묘 (terra/madeira), hora 기사 (terra/fogo). Resposta inclui:

```json
{
  "wuxingCount": {"목":2,"화":2,"토":3,"금":1,"수":0},
  "tenGodsDistribution": {"상관":1,"편관":1,"편인":0.5,"정인":0.5, ...},
  "sinSals": ["do_hwa_sal","yeok_ma_sal"],
  "jiJangGan": {"year":{"primary":{"stem":"정","strength":40}, ...}},
  "dayMasterStrength": {"level":"weak","score":25},
  "gyeokGuk": {"name":"상관격","hanja":"傷官格"},
  "yongSin": {"primaryYongSin":"화","secondaryYongSin":"토"}
}
```

Nota: `birthCity` defaultou para 서울 (Seul) — confirma a limitação de fuso coreano.

## 2. check_compatibility (sinastria) — P1 × P2 ✅

```json
{
  "compatibilityScore": 53,
  "summary": "다소 어려움이 있을 수 있습니다. 서로를 이해하려는 노력이 필요합니다.",
  "strengths": ["지지가 조화로워 편안한 관계를 유지합니다",
                "두 사람 모두 균형잡힌 십성 분포를 가지고 있습니다"],
  "weaknesses": [], "advice": [],
  "elementHarmony": {"harmony": 50, "description": "각자의 특성을 존중하는 것이 중요합니다"}
}
```

Score numérico + harmonia elemental funcionam. `weaknesses`/`advice` vieram vazios neste par — relatório de casal rico precisará da camada LLM sobre os dados brutos dos dois mapas.

## 3. get_dae_un — P1 ✅

Retornou os 10 ciclos completos: 7–16 경진, 17–26 신사, 27–36 임오, 37–46 계미, 47–56 갑신, 57–66 을유, 67–76 병술, 77–86 정해, 87–96 무자, 97–106 기축.

## 4. get_daily_fortune — P1, alvo 18/07/2026 ✅

```json
{"overallLuck":64,"wealthLuck":61,"careerLuck":67,"healthLuck":63,"loveLuck":69,
 "luckyColor":"황색","luckyDirection":"중앙",
 "advice":"오늘은 토 기운이 강한 날입니다. 신중함하게 행동하세요."}
```

## 5. analyze_saju (fortune/love) — P1 ✅

Score 82 com positivos, negativos e conselhos textuais (em coreano) coerentes com o mapa (mestre do dia terra → estabilidade; ausência de 재성 → poucas oportunidades de encontro).

## Veredito

Motor de cálculo sólido e completo para leitura individual e sinastria. Pendências para o produto: fuso/longitude Brasil, tradução pt-BR e camada LLM para relatórios narrativos.
