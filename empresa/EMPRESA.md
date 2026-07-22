# BITNA SAJU
> Documento de Contexto da Empresa
> Versão 1.0
---
# Visão Geral
A Bitna Saju é uma empresa digital AI First dedicada à divulgação e comercialização de produtos baseados no Saju (Quatro Pilares do Destino), adaptados para o público brasileiro.
O objetivo inicial da empresa é validar rapidamente a aceitação do mercado utilizando produtos digitais de baixo custo, operação enxuta e forte automação por Inteligência Artificial.
A empresa não pretende iniciar com uma estrutura complexa, área de membros robusta ou grande equipe.
A prioridade é:
- validar demanda;
- gerar vendas;
- aprender com clientes reais;
- evoluir os produtos continuamente.
---
# Modelo de Negócio
Empresa extremamente enxuta.
Estrutura inicial:
Instagram → Conteúdo → Anúncios → Landing Page → Hotmart ou Kiwify → Pagamento → Formulário → IA gera relatório → Revisão humana → Envio por e-mail
Todo o processo deve ser simples, rápido e escalável.
---
# Posicionamento
A empresa NÃO vende astrologia como entretenimento.
A empresa vende ferramentas de autoconhecimento e análise de relacionamentos utilizando o sistema oriental Saju.
O foco da comunicação deve ser sempre prático.
Exemplos:
- compreender sua personalidade
- entender seus talentos
- analisar compatibilidade
- refletir sobre carreira
- compreender padrões pessoais
Evitar linguagem excessivamente mística.
---
# Público-alvo
Baseado em pesquisa sintética.
Principal público:
- mulheres
- 18–34 anos
- classes C1/C2
- Sudeste
- interesse por cultura coreana
- interesse por desenvolvimento pessoal
- consumidoras digitais
Dores principais:
- relacionamentos
- carreira
- ansiedade sobre decisões
- autoconhecimento
- compatibilidade amorosa
---
# Produtos
> v1.1 (21/07/2026) — 4 tipos de produto travados (nome + diferenciais). **Preços não fechados** — valores de D4 (DECISOES.md) seguem como referência de funil até nova decisão. Ver D22 para o registro desta atualização.

## 🌿 Plano Essencial
Para quem quer começar a jornada de autoconhecimento coreano.
- Relatório Personalizado em PDF
- Análise do Elemento Mestre & Dinâmica Yin-Yang
- Visão Geral de Carreira e Talentos Naturais
- Resumo de Compatibilidade & Amor

*Implementação: `app/pdf/gerar_pdf.py` + `relatorios/prompts/leitura_individual.md` (produto "essencial" no backend).*

## ⭐ Plano Premium
A imersão completa no seu mapa de vida e destino.
- Relatório Completo e Aprofundado em PDF
  - Visão Aprofundada de Carreira e Talentos Naturais
  - Visão Aprofundada de Compatibilidade & Amor
- Tudo do Plano Essencial +
- Análise detalhada dos 4 Pilares (Ano, Mês, Dia, Hora)
- Mapa dos Cinco Elementos: seu equilíbrio e excessos energéticos
- Guia de Ciclos de Vida: como navegar pelos seus momentos de sorte e desafios
- Conselhos Práticos: cores, elementos e hábitos para harmonizar sua energia

*Implementação: `app/pdf/premium_v5/build_pdf.py` + `relatorios/prompts/leitura_premium.md` (produto "premium" no backend).*

## 💞 Sinastria Amorosa (Saju de Casal)
Para casais, encontros recentes ou para entender a química com o crush.
- Relatório Especial de Compatibilidade em PDF
- Cruzamento de Elementos: como o Elemento Mestre de cada um reage ao outro (complemento, atrito ou paixão)
- Dinâmica da Relativização: onde a relação flui naturalmente e onde podem surgir faíscas/desentendimentos
- Linguagens da Conexão: como cada um expressa afeto e segurança segundo o Saju
- Conselhos do Saju: dicas práticas para harmonizar as energias do casal e cultivar um relacionamento duradouro

## 🤝 Sinastria Societária & Parcerias
Para sócios, parceiros de negócios, projetos em equipe ou amigos próximos.
- Relatório Estratégico de Parceria em PDF
- Mapeamento de Talentos Complementares: quem é melhor na visão/estratégia e quem brilha na execução/operação
- Pontos de Tensão nos Negócios: mapeamento de possíveis divergências em momentos de estresse ou tomada de decisão
- Prosperidade Combinada: como a junção dos elementos dos dois atrai ou bloqueia oportunidades financeiras
- Guia de Comunicação Eficiente: como alinhar expectativas e potencializar a tomada de decisão em conjunto

*Implementação (Amorosa e Societária): mesmo motor + mesmo prompt-base `relatorios/prompts/sinastria.md`, diferenciados pelo campo `tipoRelacao`. É 1 SKU técnico com 2 posicionamentos de produto distintos — não duplicar engine/prompt (ver D4, D22). PDF próprio de sinastria ainda pendente (ver CONTINUIDADE.md).*

## Clube Saju — R$ 27,90/mês (fase 2)
Horóscopo coreano mensal, conteúdos exclusivos, comunidade, descontos, novas leituras, sinastrias promocionais. Inicialmente conceito — não construir agora.
---
# Estratégia Comercial
Funil: Instagram → Conteúdo → Venda → Entrega → Relacionamento → Recorrência
---
# Tecnologia
AI First. IA para: geração dos relatórios, revisão, atendimento, conteúdo, marketing, copywriting, pesquisa, SEO, automações.
Humano: revisão, decisões, melhoria contínua, estratégia.
---
# Presença Digital
Domínio: a definir — bitnasaju.com.br (ou equivalente) precisa ter disponibilidade confirmada antes do registro (ver D23)
Canais iniciais: site institucional, Instagram.
Futuro: Clube Saju, área de membros.
---
# Filosofia da Empresa
Antes de automatizar, validar. Antes de escalar, vender. Antes de sofisticar, simplificar.
Toda decisão prioriza velocidade de implementação, aprendizado com clientes reais e melhoria contínua.
O objetivo da primeira fase não é construir uma plataforma, mas validar um modelo de negócio sustentável.
