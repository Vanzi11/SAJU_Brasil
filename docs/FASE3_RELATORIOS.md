# Fase 3 concluída — Camada de relatórios via LLM (18/07/2026)

## O que foi implementado

A pasta `relatorios/` contém a camada completa que transforma o JSON determinístico do motor em relatórios narrativos em português:

| Arquivo | Função |
|---|---|
| `relatorios/prompts/leitura_individual.md` | System prompt do relatório individual: papel, regras de fidelidade ao JSON, tom, estrutura em 9 seções, disclaimer fixo |
| `relatorios/prompts/sinastria.md` | System prompt da sinastria: regras de cruzamento dos mapas (ciclos de geração/controle, yongsin recíproco, elementos ausentes × dominantes), tom não-determinista |
| `relatorios/gerar_prompt.mjs` | Pipeline: dados de nascimento → motor (saju + dae-un + compatibilidade) → tradução pt-BR → `{system, user}` pronto para qualquer API de LLM |
| `relatorios/exemplos/relatorio_individual_exemplo.md` | Relatório real gerado a partir do JSON de SP 01/01/1990 12:00 |
| `relatorios/exemplos/relatorio_sinastria_exemplo.md` | Relatório real do par SP × Manaus (score 53) |

## Uso

```bash
cd relatorios
# leitura individual
TZ=Asia/Seoul node gerar_prompt.mjs individual 1990-01-01 12:00 "São Paulo" female

# sinastria
TZ=Asia/Seoul node gerar_prompt.mjs sinastria \
  1990-01-01 12:00 "São Paulo" female \
  1992-07-20 14:30 "Manaus" male
```

A saída é um JSON `{system, user}`. No backend do app:

```js
const { system, user } = JSON.parse(saida);
// Exemplo com a API da Anthropic:
const resposta = await anthropic.messages.create({
  model: 'claude-sonnet-5',
  max_tokens: 4000,
  system,
  messages: [{ role: 'user', content: user }],
});
```

Pré-requisito: `fortuneteller/` compilado (`npm run build`) e processo com `TZ=Asia/Seoul`.

## Decisões de design dos prompts

1. **Fidelidade estrita**: o LLM só pode afirmar o que está no JSON — regra explícita contra alucinação de pilares/estrelas.
2. **Linguagem de tendência**, nunca previsão absoluta; proibição de conselho médico/jurídico/financeiro específico.
3. **Sinastria não-determinista**: score é "termômetro", nunca veredito; proibido aconselhar começar/terminar relações.
4. **Ciclos de geração e controle dos elementos embutidos no prompt** para o LLM cruzar os mapas corretamente (a parte mais rica da sinastria — o motor sozinho entrega só o score).
5. **Disclaimer fixo** obrigatório ao final de todo relatório.

## Nota técnica

O `gerar_prompt.mjs` termina com `process.exit(0)` explícito: o cache do motor (`performance_cache.ts`) registra um `setInterval` sem `unref()` que mantém o processo Node vivo. Correção upstream possível (adicionar `.unref()`), anotada como melhoria futura.

## Próximos passos (Fase 4 — produto)

Backend HTTP com endpoints `/leitura`, `/sinastria`, `/diaria`; cadastro de nascimento com autocomplete de cidades (expandir tabela IBGE); flag "hora desconhecida" (3 pilares); UI.
