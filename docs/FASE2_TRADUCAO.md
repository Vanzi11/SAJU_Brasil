# Fase 2 concluída — Tradução pt-BR (18/07/2026)

## O que foi implementado

Novo módulo `fortuneteller/src/data/i18n/pt_br.ts` com a tradução determinística de todo o vocabulário estrutural do motor, mais a função `traduzirSaju()` que converte o JSON do `analyze_saju` em uma estrutura 100% em português, pronta para exibir no app ou alimentar o LLM de relatórios.

### Dicionários exportados

`TRONCOS_PT` (10 troncos celestes com hanja, romanização, elemento, polaridade), `RAMOS_PT` (12 ramos com animal do zodíaco e horário), `ELEMENTOS_PT` (cinco elementos), `DEZ_DEUSES_PT` (com essência de cada um), `SINSAL_PT` (15 estrelas com significado), `GYEOKGUK_PT` (14 padrões), `TERMOS_SOLARES_PT` (24 termos), `NIVEL_FORCA_PT`, além de `formatarPilarPt()` e `traduzirSaju()`.

### Exemplo de saída de `traduzirSaju()`

```json
{
  "pilares": { "dia": { "ganji": "병인", "tronco": "Byeong (丙) — Fogo Yang",
                         "ramo": "In (寅) — Tigre, Madeira" } },
  "mestreDoDia": "Byeong (丙) — Fogo Yang",
  "elementos": { "contagem": { "Madeira": 1, "Fogo": 4, "Terra": 1, "Metal": 0, "Água": 2 },
                 "dominantes": ["Fogo"], "fracos": ["Metal"] },
  "sinsal": [{ "nome": "Cavalo das Estações", "hanja": "驛馬殺",
               "significado": "Viagens, mudanças, vida em movimento" }],
  "padraoDeVida": { "nome": "Padrão do Oficial Direto", "essencia": "retidão, senso de dever" },
  "yongsin": { "elementoPrincipal": "Madeira", "elementoSecundario": "Fogo" }
}
```

## Decisão de arquitetura

Conforme o roadmap, os **textos interpretativos longos em coreano NÃO foram traduzidos** (frases de resumo, conselhos etc.). Eles são descartados na tradução; a camada LLM (Fase 3) gera o relatório em português diretamente do JSON estruturado — resultado melhor e sem manutenção de centenas de templates.

## Validação

Teste com perfil brasileiro real (SP, 01/01/1990 12:00): varredura automática confirmou **zero caracteres coreanos** na saída traduzida (exceto o campo `ganji`, mantido de propósito como identificador tradicional). Script: `tests/test_ptbr.mjs`.

## Uso no app

```js
import { calculateSaju } from '.../dist/lib/saju.js';
import { traduzirSaju } from '.../dist/data/i18n/pt_br.js';

const saju = calculateSaju('1990-01-01', '12:00', 'solar', false, 'female', 'São Paulo');
const leitura = traduzirSaju(saju); // pronto para UI ou prompt de LLM
```

Referência humana dos termos: `docs/GLOSSARIO_PT_BR.md`.
