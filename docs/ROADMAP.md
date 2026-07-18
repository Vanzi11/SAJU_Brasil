# Roadmap — Adaptação para o Brasil

## Fase 1 — Fuso horário e hora solar verdadeira (crítico)

O Saju é calculado sobre a **hora solar verdadeira** do local de nascimento. Hoje o código assume Coreia. O que muda:

### 1.1 Parser de hora civil
`parseBirthDateTimeKorea` (em `fortuneteller/src/utils/date.ts`) interpreta a hora como KST (UTC+9, sem DST). Substituir por parser que aceita timezone IANA (ex.: `America/Sao_Paulo`, `America/Manaus`, `America/Fortaleza`) usando `date-fns-tz` (o projeto já usa date-fns).

**Atenção ao horário de verão histórico brasileiro**: quem nasceu entre outubro e fevereiro em anos com DST (praticamente todos até 2019) tem 1h de diferença na hora civil. A base IANA já contém esse histórico — basta usar a timezone certa por UF/ano.

### 1.2 Tabela de longitudes brasileiras
Replicar `src/data/longitude_table.ts` com cidades brasileiras. Correção: `offset_min = (longitude_local − meridiano_do_fuso) × 4 min/grau`. Exemplos (fuso UTC−3, meridiano −45°):

| Cidade | Longitude | Correção |
|---|---|---|
| São Paulo | −46,63° | −6,5 min |
| Rio de Janeiro | −43,17° | +7,3 min |
| Brasília | −47,88° | −11,5 min |
| Fortaleza | −38,54° | +25,8 min |
| Manaus (UTC−4, mer. −60°) | −60,02° | −0,1 min |
| Rio Branco (UTC−5, mer. −75°) | −67,81° | +28,8 min |

Fonte sugerida: coordenadas de municípios do IBGE (5.570 municípios, dados públicos).

### 1.3 Equação do tempo (opcional, refinamento)
O original usa só longitude. Para precisão máxima somar a equação do tempo (±16 min conforme a época do ano). Relevante porque o pilar da hora muda a cada 2h — nascimentos perto da fronteira entre ramos (ex.: 10:59/11:01) podem mudar de pilar.

### 1.4 Validação
Casos de teste: nascimento em DST vs. fora; fronteiras de ramo horário; os 4 fusos brasileiros; comparação com manseryeok de referência.

## Fase 2 — Tradução pt-BR

1. **Dados estruturais** (determinístico, sem LLM): mapear 천간→troncos celestes, 지지→ramos terrestres, 오행→cinco elementos (목/화/토/금/수 → Madeira/Fogo/Terra/Metal/Água), 십성→dez deuses, 신살 (15), 격국, nomes dos 24 termos solares. Criar `src/data/i18n/pt-BR.ts`.
2. **Textos interpretativos**: os templates em coreano dentro de `src/lib/` (fortune.ts, compatibility.ts etc.) podem ser (a) traduzidos template a template, ou (b) ignorados — usando só o JSON estruturado e deixando o texto para o LLM. **Recomendação: (b)** — menos trabalho e relatórios melhores.
3. **Glossário do app**: decidir termos de produto (ex.: manter "Saju" e "Dae-un" como marca, ou "Quatro Pilares"/"ciclo de década").

## Fase 3 — Camada de relatórios (LLM)

- Prompt de leitura individual: recebe o JSON do `analyze_saju` + `get_dae_un` e gera relatório narrativo em pt-BR (personalidade, carreira, amor, ciclos).
- Prompt de sinastria: recebe os dois mapas completos + `check_compatibility` e gera relatório de casal (o score sozinho é raso — os dois JSONs completos dão material para análise elemento a elemento).
- Definir tom do produto e disclaimers (entretenimento/autoconhecimento; não é aconselhamento médico/financeiro).

## Fase 4 — Produto

- Backend: extrair `src/lib/` como pacote próprio ou usar modo HTTP como microserviço.
- API do app: endpoints `/leitura`, `/sinastria`, `/diaria`.
- Cadastro de nascimento: data, hora, cidade (autocomplete IBGE), flag "hora desconhecida" (calcular com 3 pilares).
