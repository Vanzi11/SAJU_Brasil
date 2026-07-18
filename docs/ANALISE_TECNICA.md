# Análise Técnica — Servidor Saju MCP (fortuneteller v1.2.0)

## Visão geral

Servidor MCP em TypeScript/Node.js (≥18) que calcula Saju de forma **determinística** — sem depender de LLM para a matemática. É exatamente o que um app de leitura precisa: o LLM alucina cálculos calendáricos; este motor não.

- Repositório: https://github.com/hjsh200219/fortuneteller
- npm: `@hoshin/saju-mcp-server` | Licença: MIT
- Modos de execução: stdio (MCP), HTTP (`npm run start:http`, pronto p/ Railway), Smithery, Docker

## As 7 ferramentas

1. **`analyze_saju`** — pilares (ano/mês/dia/hora), oito caracteres, contagem dos cinco elementos, dez deuses (십성), sinsal, jijanggan com pesos sazonais, força do mestre do dia, gyeokguk (padrão de vida), yongsin (elemento de equilíbrio). Tipos: `basic`, `fortune` (geral/carreira/riqueza/saúde/amor), `yongsin`, `school_compare` (5 escolas), `yongsin_method`.
2. **`check_compatibility`** — sinastria: score 0-100, harmonia elemental, pontos fortes/fracos, conselhos.
3. **`convert_calendar`** — solar ↔ lunar 1900–2200, com mês intercalar (윤달). Tabelas locais, sem API externa.
4. **`get_daily_fortune`** — scores diários (geral/riqueza/carreira/saúde/amor), cor e direção da sorte, conselho.
5. **`get_dae_un`** — ciclos de 10 anos (대운) por idade, com stem/branch e elementos.
6. **`get_fortune_by_period`** — sorte anual (세운), mensal (월운), horária (시운), multi-ano.
7. **`manage_settings`** — pesos entre escolas interpretativas (Ziping, Ditiansui, Qiongtong Baojian, moderna, sinsal).

## Ativos de dados críticos (o que não podemos perder)

- `src/data/solar_terms_*.ts` — 24 termos solares de **1900 a 2200** (essencial: o pilar do mês depende do termo solar, não do mês civil)
- `src/data/lunar_table.ts` + `manselyeok_table.ts` — tabelas manseryeok/lunares locais
- `src/data/heavenly_stems.ts`, `earthly_branches.ts`, `wuxing.ts` — dados fundamentais com jijanggan e relações
- `src/data/longitude_table.ts` — 229 cidades coreanas (modelo a replicar com cidades brasileiras)
- `src/lib/` — toda a lógica: saju.ts, compatibility.ts, dae_un.ts, yong_sin.ts, ten_gods.ts, sin_sal.ts, gyeok_guk.ts, day_master_strength.ts etc.

## Arquitetura do cálculo de hora (ponto-chave para o Brasil)

Em `src/utils/date.ts`:

```
getAdjustedBirthInstantForSaju(solarDate, birthTime, birthCity)
  = parseBirthDateTimeKorea(...)                 // interpreta hora como KST (UTC+9)
  + getLongitudeOffsetMinutesForSaju(birthCity)  // corrige vs. meridiano 135°E
```

Ou seja: hora civil → hora solar verdadeira via longitude. A constante legada `TRUE_SOLAR_TIME_ADJUSTMENT = -30` existe mas o fluxo atual usa a tabela de longitude. **A adaptação Brasil troca essas duas peças** (parser de timezone + tabela de longitudes) sem tocar no núcleo do cálculo.

## Limitações identificadas

1. **Coreia hard-coded**: parser assume KST; `birthCity` só aceita cidades coreanas (default 서울/Seul).
2. **Saídas em coreano**: labels e textos interpretativos (ex.: "상관격", "다소 어려움이 있을 수 있습니다").
3. Textos interpretativos são templates relativamente curtos — para relatórios ricos, usar o JSON como insumo de um LLM, não o texto pronto.
4. Sinastria retorna `weaknesses`/`advice` às vezes vazios (visto no teste) — a profundidade do relatório de casal virá da camada LLM.

## Recomendação de arquitetura para o app

Não usar o protocolo MCP em produção. Usar `src/lib/` como biblioteca Node diretamente (ou o modo HTTP como microserviço de cálculo). Fluxo: dados de nascimento → motor (JSON determinístico) → LLM com prompt em pt-BR → relatório final. O MCP fica útil para prototipagem no Claude Desktop.
