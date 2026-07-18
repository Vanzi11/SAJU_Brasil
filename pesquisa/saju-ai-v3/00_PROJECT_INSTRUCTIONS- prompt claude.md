# 00_PROJECT_INSTRUCTIONS
## Instruções Globais do Projeto — Saju Platform

---

# CONTEXTO DO PROJETO

Estamos construindo uma plataforma web premium de análise comportamental baseada no Saju/BaZi coreano, potencializada por IA.

O produto será lançado em três fases evolutivas:
- **Fase 1:** Site de vendas com geração de relatório via IA (produto digital)
- **Fase 2:** MicroSaaS com área de membros, pagamento recorrente e leituras adicionais
- **Fase 3:** AI-First OS comportamental — IA conversacional contínua com memória do mapa do usuário

---

# POSICIONAMENTO OFICIAL

O sistema deve ser apresentado como:

**"Sistema Oriental de Análise de Perfil"**
ou
**"Modelo Temporal-Comportamental"**
ou
**"Arquitetura Comportamental Baseada em Ciclos"**

---

# O QUE O PRODUTO É

- Plataforma de autoconhecimento comportamental
- Framework de análise de perfil baseado em padrões orientais
- Sistema de reflexão pessoal orientado por IA
- Modelo interpretativo de padrões humanos

---

# O QUE O PRODUTO NÃO É

- Astrologia mística
- Religião ou prática espiritual
- Oráculo ou adivinhação
- Sistema fatalista ou de previsões absolutas

---

# PILARES DO SISTEMA

## 1. Engine Matemática
Cálculo técnico dos 4 pilares do mapa Saju/BaZi a partir de:
- Nome completo
- Data de nascimento
- Hora de nascimento
- Local de nascimento

## 2. Engine Interpretativa
Tradução psicológica dos padrões energéticos identificados no mapa.

## 3. IA Narrativa
Geração de linguagem humana natural usando Claude API com prompt estruturado.

## 4. UX Comportamental
Experiência emocional premium — o usuário deve sentir sofisticação, clareza e identificação.

---

# FONTES BASE DO SISTEMA

- Di Tian Sui
- Zi Ping Zhen Quan
- Qiong Tong Bao Jian
- Joey Yap BaZi (modernização)
- Zi Wei Dou Shu (camada emocional)
- Big Five, Human Design (UX), Daniel Kahneman, Atomic Habits

---

# REFERÊNCIAS DE DESIGN

- Genera Lab (estrutura de área de membros)
- 16Personalities (clareza e identificação)
- Apple Design (sofisticação visual)
- Headspace / Calm (experiência emocional)
- Notion (organização e elegância)

**Paleta:** tons refinados, dark ou neutro premium. Evitar roxo genérico.
**Tipografia:** display font distinto + body font elegante.
**Tom visual:** analítico, sofisticado, humano — nunca místico ou esotérico.

---

# ARQUITETURA MODULAR (12 módulos)

1. Product Vision ✅
2. Positioning and Philosophy ✅
3. Engine Architecture
4. Five Elements Matrix
5. Ten Gods Matrix
6. Archetypes System
7. AI Decision Tree
8. Interpretation Blocks
9. Master Prompt Agent ✅
10. Report Structure V3
11. UX and Product Experience
12. Business Model and Roadmap

---

# DIRETRIZES GLOBAIS DE LINGUAGEM

A IA deve sempre:
- Soar sofisticada e observacional
- Usar linguagem psicológica e comportamental
- Expressar tendências, nunca certezas absolutas
- Usar estruturas como: "há tendência a…", "frequentemente se manifesta como…"

A IA deve nunca:
- Usar linguagem mística, religiosa ou fatalista
- Fazer previsões absolutas
- Gerar medo, culpa ou manipulação emocional

---

# STACK TÉCNICA PREVISTA

**Fase 1 e 2:**
- **Frontend:** Next.js + Tailwind CSS
- **Backend:** Node.js ou Python
- **Banco de dados:** Supabase
- **Pagamentos:** Stripe ou Mercado Pago
- **IA:** Claude API (claude-sonnet-4-20250514)
- **Cálculo Saju:** biblioteca BaZi em Python/JS
- **Geração de PDF:** biblioteca de exportação estilizada

**Fase 3 (adicional):**
- **Memória conversacional:** Supabase (histórico de chats por usuário)
- **System prompt dinâmico:** mapa Saju completo injetado em cada sessão
- **Agentes especializados:** Claude API com personas distintas por domínio
- **Interface de chat:** componente nativo integrado à plataforma

---

# ARQUIVOS DO PROJETO

| Arquivo | Descrição |
|---|---|
| `00_MASTER_V3_SYSTEM.md` | Arquitetura central do sistema |
| `01_PRODUCT_VISION.md` | Visão estratégica e posicionamento |
| `PROMPT_PROFISSIONAL_SAJU.md` | Prompt operacional de geração de relatório |
| Livros de Saju (PDF) | Base técnica para calibração do sistema |

---

# ROADMAP DE EVOLUÇÃO DO PRODUTO

## Fase 1 — Site (Validação)
**Objetivo:** Validar que pessoas pagam pelo produto antes de construir tudo.

```
Usuário acessa o site
→ Paga pelo relatório
→ Insere dados (nome, data, hora, local)
→ Sistema calcula os 4 pilares do Saju
→ Claude API gera relatório personalizado
→ Usuário acessa o relatório em PDF ou página web
→ Pode comprar leituras adicionais (familiar, sinastria)
```

**Entregável:** Site funcional com pagamento e geração de relatório.

---

## Fase 2 — MicroSaaS (Escala)
**Objetivo:** Transformar o produto em plataforma recorrente.

Adiciona sobre a Fase 1:
- Área de membros com login
- Histórico de todas as leituras do usuário
- Assinatura mensal/anual
- Dashboard com múltiplos mapas (família, equipe)
- Sinastria entre mapas já cadastrados

**Entregável:** Plataforma SaaS com recorrência e retenção.

---

## Fase 3 — AI-First OS Comportamental (Diferenciação)
**Objetivo:** Transformar o relatório estático em um copiloto vivo e conversacional.

O usuário deixa de receber um documento e passa a ter uma **IA que o conhece profundamente** — baseada no seu mapa Saju, memória de interações anteriores e contexto de vida atual.

### O que o AI-First OS faz:

**Memória permanente do mapa**
O mapa Saju do usuário fica sempre no contexto da IA. Ela nunca esquece quem ele é.

**IA conversacional contextualizada**
O usuário pergunta qualquer coisa e recebe respostas filtradas pelo seu perfil comportamental:
- "Devo aceitar essa proposta de trabalho?"
- "Por que eu sempre trava nesse tipo de situação?"
- "Como me comunicar melhor com meu sócio?"

**Agentes especializados**
- Agente de Carreira — decisões profissionais baseadas no mapa
- Agente de Relacionamentos — dinâmicas interpessoais e sinastria
- Agente de Ciclos — momento atual e tendências do período
- Agente de Autoconhecimento — padrões recorrentes e pontos cegos

**Memória de interações**
A IA lembra do que o usuário já compartilhou em conversas anteriores e evolui com ele ao longo do tempo.

### Stack adicional para a Fase 3:
- Claude API com system prompt contendo o mapa Saju completo do usuário
- Banco de memória de conversas (Supabase)
- Interface conversacional integrada à plataforma (chat nativo)
- Agentes especializados por domínio (carreira, relações, ciclos)

---

# MODELO DE NEGÓCIO COMPLETO

| Fase | Produto | Modelo | Preço sugerido |
|---|---|---|---|
| 1 | Leitura Saju Individual | Avulso | R$ 97 – R$ 147 |
| 1 | Leitura Adicional (familiar) | Avulso | R$ 67 – R$ 97 |
| 1 | Sinastria Amorosa | Avulso | R$ 127 – R$ 197 |
| 1 | Sinastria Profissional | Avulso | R$ 127 – R$ 197 |
| 2 | Plano Essencial | Assinatura mensal | R$ 47 – R$ 67/mês |
| 2 | Plano Família | Assinatura mensal | R$ 97 – R$ 127/mês |
| 3 | Plano Copiloto | Assinatura mensal | R$ 147 – R$ 197/mês |
| 3 | Plano Corporativo | Assinatura anual | sob consulta |

---

# OBJETIVO FINAL

Construir um **AI-First OS de inteligência comportamental simbólica** — começando como um simples site de relatórios e evoluindo para um copiloto de autoconhecimento que conhece profundamente cada usuário, baseado em padrões orientais, linguagem moderna, profundidade simbólica e alta escalabilidade.

A visão de longo prazo não é vender um relatório — é ser o sistema que acompanha o usuário em suas decisões de vida.
