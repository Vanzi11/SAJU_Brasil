# Fase 5 (plano) — Automação de vendas: webhook → formulário → geração → aprovação → envio

> Status: **plano, não implementado**. Hospedagem 24h ainda não decidida (Ivã optou por não tratar isso agora — o desenho abaixo não muda se rodar local ou hospedado). Plataforma de venda (Hotmart/Kiwify/ambas) também em aberto — o desenho suporta qualquer uma, ver seção "Webhook".

## Objetivo

Cliente compra → recebe pedido pra fornecer dados de nascimento → sistema gera leitura + PDF sozinho (reaproveitando `/leitura`, `/sinastria`, `/pdf` já prontos e testados) → Ivã recebe e-mail com o PDF pra revisar → Ivã aprova com 1 clique → cliente recebe o PDF final por e-mail. Nenhuma peça nova toca no motor de cálculo, no prompt ou no gerador de PDF — só orquestra o que já existe.

## Modelo de dados novo: `pedido`

Guardado como JSON por enquanto (sem banco novo — mesma filosofia zero-dependência do `server.mjs`). Um arquivo por pedido em `app/pedidos/{id}.json`, ou um único `app/pedidos.json` como índice — decidir no momento da implementação conforme volume.

```
{
  id: string (uuid),
  plataforma: "hotmart" | "kiwify",
  produto: "essencial" | "premium" | "sinastria_amorosa" | "sinastria_societaria",
  emailCliente: string,
  nomeCliente: string,
  status: "aguardando_dados" | "aguardando_geracao" | "aguardando_aprovacao" | "aprovado" | "enviado" | "erro",
  dadosNascimento: { data, hora?, cidade, sexo } | null,
  pessoa2?: { nome, data, hora?, cidade, sexo } | null,   // só sinastria
  tipoRelacao?: "amorosa" | "societaria",                  // só sinastria
  relatorioTexto: string | null,
  pdfPath: string | null,
  tokenFormulario: string,   // link pro cliente preencher nascimento
  tokenAprovacao: string,    // link pro Ivã aprovar
  criadoEm: timestamp,
  expiraEm: timestamp        // tokens expiram (ex: 15 dias)
}
```

## Rotas novas (somam às já existentes: `/`, `/cidades`, `/leitura`, `/sinastria`, `/diaria`, `/pdf`)

| Rota | Método | Função |
|---|---|---|
| `/webhook/hotmart` | POST | Recebe aviso de compra da Hotmart. Valida assinatura (`hottok`). Cria `pedido` com status `aguardando_dados`. Envia e-mail ao cliente com link do formulário. |
| `/webhook/kiwify` | POST | Mesma função, adaptador pro formato da Kiwify. |
| `/pedidos/:token/formulario` | GET | Serve a página HTML de coleta de nascimento (campos condicionais se for sinastria). |
| `/pedidos/:token/dados` | POST | Recebe os dados preenchidos. Muda status pra `aguardando_geracao` e **dispara a geração na hora** (chama internamente a mesma lógica de `/leitura` ou `/sinastria` com `gerarRelatorio:true`, depois `/pdf`). Ao terminar: status `aguardando_aprovacao`, e-mail pra Ivã com PDF anexado + link de aprovação. |
| `/pedidos/:id/aprovar` | GET | Link clicável no e-mail do Ivã. Valida `tokenAprovacao`. Muda status pra `aprovado`, dispara e-mail final ao cliente com o PDF, muda status pra `enviado`. |
| `/pedidos/:id/status` | GET (opcional) | Painel simples pra Ivã ver pedidos pendentes, sem precisar vasculhar e-mail. |

## Peça que falta e precisa de escolha: envio de e-mail

O `server.mjs` hoje não manda e-mail nenhum. Três opções, todas viáveis sem inflar dependências:

1. **Resend** (API HTTP simples, `fetch` puro, sem SDK) — recomendo por ser o mais simples de integrar mantendo "zero dependência de pacote".
2. **SendGrid** — similar, mais estabelecido, plano grátis menor.
3. **SMTP de um Gmail/Workspace** — exige a lib `nodemailer` (única dependência nova do projeto). Mais familiar, mas menos escalável se o volume crescer.

Isso fica como pendência de decisão — não bloqueia o resto do desenho, só a etapa final de implementação do envio.

## Segurança (não pular)

- **Assinatura do webhook**: Hotmart manda um `hottok` no payload, Kiwify tem verificação própria por token de conta — validar sempre, senão qualquer um pode fabricar um "pedido pago" falso e gerar relatório de graça.
- **Tokens de formulário e aprovação**: gerados aleatórios (ex: `crypto.randomUUID()`), de uso único, com expiração (ex: 15 dias) — evita que um link vazado gere problema depois.
- **Rate limit** no `/webhook` e no `/pedidos/:token/dados` — já estava listado como pendência geral do backend (`FASE4_PRODUTO.md`), fica ainda mais importante com rota pública.

## Ordem de construção sugerida

1. **Fila de pedidos + formulário de nascimento** (funciona standalone, sem webhook — dá pra testar criando pedido manualmente)
2. **Geração automática ao submeter o formulário** (conecta o formulário ao que já existe: `/leitura`/`/sinastria` + `/pdf`)
3. **E-mail de aprovação pro Ivã + rota de aprovar**
4. **Webhook real da Hotmart/Kiwify** (só entra depois dos passos 1–3 estarem testados manualmente — é a peça mais fácil de testar por último, porque dá pra simular "pedido criado" na mão)
5. **Envio final ao cliente**
6. **Hospedagem 24h** (fica por último de propósito — só importa quando o resto já está validado local)

## Não muda em nada

Prompts (`leitura_individual.md`, `leitura_premium.md`, `sinastria.md`), motor de cálculo, geradores de PDF (`gerar_pdf.py`, `build_pdf.py`) — zero alteração. Essa fase só adiciona orquestração em volta do que já é aprovado e testado.
