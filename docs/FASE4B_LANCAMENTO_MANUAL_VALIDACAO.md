# Lançamento manual — validar antes de automatizar

> Status: plano. Objetivo: vender de verdade com o mínimo de trabalho novo, usando só o que já está pronto e testado. A automação completa (`docs/FASE5_AUTOMACAO_VENDAS.md`) só entra depois de validar que o produto vende.

## A ideia central

Tudo que falta pra Fase 5 (webhook, fila, formulário automático, e-mail, aprovação) resolve um problema que você **ainda não tem**: volume. Com poucas vendas por semana, um humano (você) no meio do processo não é gargalo — é controle de qualidade de graça, que resolve exatamente o medo que você levantou lá atrás (leitura ou PDF perdendo qualidade). Automatizar cedo demais trocaria essa revisão manual por confiança cega no sistema, sem necessidade.

## O que já está pronto e não precisa de nada novo

- Motor de cálculo, prompts (Essencial, Premium), geração de PDF — tudo testado
- Painel local (`localhost:3333`, rodando com `node app/server.mjs`) — já tem formulário de entrada com autocomplete de cidade, já gera relatório + PDF na hora

Ou seja: **você já consegue gerar um relatório de qualidade hoje, sem escrever nada.** O que falta é só a ponte entre "cliente pagou" e "você digita os dados dele no painel".

## Escopo do lançamento manual (produtos)

Lançar com **Essencial e Premium primeiro** — são os dois já completos de ponta a ponta. Sinastria (Amorosa/Societária) entra depois, porque falta o PDF próprio dela (só o prompt está pronto — ver pendência em `DECISOES.md`). Isso reduz o trabalho de lançamento pela metade sem abrir mão de nada que já funciona.

## Fluxo operacional manual (sem código novo)

```
1. Cliente compra pelo link de checkout da Hotmart/Kiwify
   (link de pagamento simples — não precisa de webhook nem integração)
        ↓
2. Página de "obrigado" da própria Hotmart/Kiwify (configurável sem código)
   pede pro cliente mandar os dados de nascimento por e-mail ou WhatsApp
   (nome, data, hora ou "não sei", cidade, e para sinastria: dados da 2ª pessoa)
        ↓
3. Você recebe os dados e digita no painel local (localhost:3333)
        ↓
4. Servidor gera o relatório + PDF automaticamente (isso já é automático hoje)
        ↓
5. Você lê o PDF gerado — é o seu controle de qualidade manual
        ↓
6. Você manda o PDF por e-mail pro cliente
```

O único trabalho manual de verdade é os passos 2, 3, 5 e 6 — e são rápidos (minutos por pedido).

## O que precisa ser decidido antes de abrir a venda (não é código, é negócio)

Essas pendências já estavam registradas em `DECISOES.md` e são o bloqueio real pro lançamento, não a automação:

1. **Preço** (mesmo que provisório — dá pra ajustar depois de validar)
2. **Texto de consentimento LGPD e transparência de uso de IA** — precisa aparecer onde o cliente manda os dados (e-mail/WhatsApp/formulário simples), mesmo sem ser um formulário formal ainda
3. **Política de reembolso** — uma frase clara na página de vendas já resolve
4. Decisão do "bônus tipo sanguíneo" no Premium (manter ou trocar por sorte anual) — não bloqueia lançamento, mas define o conteúdo final do PDF Premium

## Critério pra saber quando migrar pra automação (Fase 5)

Definir um gatilho objetivo evita duas armadilhas: automatizar cedo demais (gastando esforço em algo sem tração) ou tarde demais (você virando gargalo). Sugestão de gatilho — qualquer um destes:

- Volume: mais de N pedidos/semana tornando o processo manual cansativo (ex.: N = 5–10, ajuste conforme sua rotina)
- Tempo: mais de X minutos/dia dedicados só à parte operacional (digitar dados, mandar e-mail)
- Validação de mercado atingida: a "meta de validação concreta" já pendente em `DECISOES.md` (ex.: X vendas em 60 dias)

Quando qualquer um bater, `docs/FASE5_AUTOMACAO_VENDAS.md` já está pronto pra sair do papel — nenhum retrabalho, só seguir a ordem de construção que já está lá.

## Resumo da sequência completa

```
Agora → Fechar as 3-4 decisões de negócio acima (rápido)
      → Configurar link de checkout + página de obrigado na Hotmart/Kiwify (sem código)
      → Vender Essencial e Premium manualmente
      → PDF de Sinastria fica pronto em paralelo (dev, quando der)
      → Adicionar Sinastria ao catálogo manual
      → Bater o gatilho de volume/tempo/validação
      → Migrar pra Fase 5 (automação completa, plano já pronto)
```
