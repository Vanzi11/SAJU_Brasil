# Textos do lançamento manual — página de obrigado + e-mail de coleta de dados

> Deriva de `empresa/GUIA_DE_VOZ.md` (slogan, vocabulário permitido/proibido, regras invioláveis). Cobre a Etapa 2 do fluxo descrito em `docs/FASE4B_LANCAMENTO_MANUAL_VALIDACAO.md`. Textos prontos pra colar na página de "obrigado" da Hotmart/Kiwify e no e-mail de acompanhamento.

## 1. Página de obrigado (redirecionamento pós-compra, configurável sem código na Hotmart/Kiwify)

```
Recebemos sua compra! 🌿

Seu Saju está a um passo de ficar pronto. Precisamos só de alguns
dados de nascimento pra calcular seu mapa com precisão.

Em instantes você recebe um e-mail com o que precisamos —
confira também a caixa de spam, pra não perder o prazo.

Prazo de entrega: até [X] dias úteis após o envio dos seus dados.

Dúvidas? Responda o e-mail de confirmação ou fale com a gente
no WhatsApp: [número]

"Não é sobre prever sua vida — é sobre entender seus
padrões para decidir melhor."
```

## 2. E-mail — pedido de dados (produto individual: Essencial ou Premium)

```
Assunto: Só falta isso pro seu Saju ficar pronto ✦

Oi, [nome]!

Que bom te ter por aqui. Seu [Plano Essencial / Plano Premium]
está reservado — agora precisamos dos seus dados de nascimento
pra calcular seu mapa com exatidão. O Saju é sensível a detalhe:
até a cidade certa muda o resultado.

Responda este e-mail com:

• Nome completo
• Data de nascimento (dia/mês/ano)
• Horário de nascimento (se não souber, tudo bem — o cálculo
  se ajusta, só perde uma camada de detalhe)
• Cidade e estado de nascimento
• Sexo (usamos pra ajustar a linguagem do relatório certinho)

Ao enviar esses dados, você concorda que vamos usá-los
exclusivamente para gerar o seu relatório, com apoio de
inteligência artificial na escrita do texto interpretativo
— o cálculo do mapa em si é determinístico, não gerado por IA.
Seus dados não são compartilhados com terceiros nem usados
para nenhum outro fim.

Assim que recebermos, seu relatório chega em até [X] dias úteis.

Até já,
[assinatura / nome do negócio]

"Não é sobre prever sua vida — é sobre entender seus
padrões para decidir melhor."
```

## 3. E-mail — pedido de dados (Sinastria Amorosa ou Societária)

```
Assunto: Só falta isso pra sua Sinastria ficar pronta ✦

Oi, [nome]!

Sua [Sinastria Amorosa / Sinastria Societária & Parcerias]
está reservada. Pra cruzar os dois mapas com exatidão, precisamos
dos dados de nascimento das duas pessoas envolvidas.

Responda este e-mail com:

Pessoa 1
• Nome completo
• Data de nascimento (dia/mês/ano)
• Horário de nascimento (se não souber, tudo bem)
• Cidade e estado de nascimento
• Sexo

Pessoa 2
• (os mesmos 5 dados acima)

Ao enviar esses dados, vocês concordam com o uso deles
exclusivamente para gerar o relatório de sinastria, com apoio
de inteligência artificial na escrita do texto interpretativo
— o cálculo dos mapas é determinístico, não gerado por IA.
Os dados não são compartilhados com terceiros.

Assim que recebermos, o relatório chega em até [X] dias úteis.

Até já,
[assinatura / nome do negócio]

"Não é sobre prever sua vida — é sobre entender seus
padrões para decidir melhor."
```

## Notas de implementação

- **[X] dias úteis**: defina um prazo real que você consegue cumprir no fluxo manual (digitar dados → gerar → revisar → enviar). Melhor prometer 3 dias e entregar em 1 do que o contrário.
- **Consentimento LGPD**: o parágrafo "Ao enviar esses dados..." cobre a pendência de transparência de IA + uso de dados registrada em `DECISOES.md`. Quando a Fase 5 (formulário automático) entrar em produção, esse texto vira um checkbox obrigatório em vez de um parágrafo de e-mail — mas o conteúdo jurídico é o mesmo, só muda o formato.
- **"Sexo" no formulário**: crítico — é o campo que evita o erro de concordância de gênero (regra inviolável nº 1 do `GUIA_DE_VOZ.md`). Não deixar como campo opcional.
- Nenhum vocabulário proibido usado (sem "destino", "universo", "energia cósmica" etc.) — revisar contra `GUIA_DE_VOZ.md` se o texto for alterado depois.
