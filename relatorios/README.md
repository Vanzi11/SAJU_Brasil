# relatorios/ — Prompts, exemplos e visuais

- `prompts/` — OS ATIVOS CENTRAIS DA EMPRESA. System prompts que transformam o JSON do motor em relatórios: `leitura_individual.md` (produto R$47), `leitura_premium.md` (R$197), `sinastria.md` (4 tipos de relação). Seguem o GUIA_DE_VOZ (empresa/). Regra nº1 inviolável: concordância de gênero pelo campo `sexo`.
- `exemplos/` — relatórios reais gerados (texto e PDF). `leitura_premium_iva_AMOSTRA_v5_reproduzida.pdf` é o padrão visual APROVADO.
- `visuais/` — protótipos SVG e caderno institucional (texto fixo das páginas de abertura do Premium).
- `gerar_prompt.mjs` — CLI: dados de nascimento → prompt pronto {system,user}.
