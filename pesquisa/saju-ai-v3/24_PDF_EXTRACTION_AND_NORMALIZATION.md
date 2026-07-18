# 24_PDF_EXTRACTION_AND_NORMALIZATION
## Sistema de Extração, Limpeza e Normalização de PDFs
## For SAJU AI V3

---

# 1. VISÃO GERAL

A qualidade do conhecimento da IA depende:
# diretamente da qualidade dos dados processados.

PDFs ruins geram:
- embeddings ruins,
- retrieval ruim,
- interpretações inconsistentes,
- hallucinations.

---

# 2. OBJETIVO

Criar:
- pipeline limpo,
- extração consistente,
- padronização semântica,
- base textual confiável.

---

# 3. REGRA CENTRAL

O sistema NÃO deve:
- jogar PDFs diretamente no RAG.

Antes disso:
os documentos devem:
# ser normalizados.

---

# 4. PIPELINE IDEAL

O fluxo correto:

```text
PDF
→ OCR
→ Cleaning
→ Normalization
→ Semantic Structuring
→ Chunking
→ Embedding
→ RAG
```

---

# 5. TIPOS DE PDF

A pipeline deve detectar:

| Type | Action |
|---|---|
| Native PDF | Direct extraction |
| OCR PDF | OCR correction |
| Scanned Image PDF | Full OCR |
| Mixed PDF | Hybrid extraction |

---

# 6. OCR QUALITY RULE

OCR ruim:
# destrói significado técnico.

Especialmente em:
- chinês,
- coreano,
- termos metafísicos.

---

# 7. OCR RECOMENDADO

Sugestões:
- PaddleOCR
- Tesseract customizado
- ABBYY
- OCR multilíngue

---

# 8. LÍNGUAS DO PROJETO

O sistema deve suportar:
- inglês,
- chinês,
- coreano,
- português.

---

# 9. NORMALIZAÇÃO DE TERMOS

O sistema deve padronizar:
# nomenclaturas.

---

# 10. EXEMPLO

Todos devem virar:
```text
Seven Killings
```

Mesmo se o PDF usar:
- 7K
- Qi Sha
- Seven Killings Star
- 七杀

---

# 11. PADRONIZAÇÃO OBRIGATÓRIA

Termos obrigatórios:

| Canonical Term | Variations |
|---|---|
| Day Master | Day Stem / Self |
| Useful God | Yong Shen / 用神 |
| Resource | 印 |
| Companion | 比劫 |
| Output | 食伤 |

---

# 12. REMOÇÃO DE RUÍDO

A pipeline deve remover:
- headers,
- footers,
- page numbers,
- watermark,
- OCR garbage,
- linhas quebradas.

---

# 13. DETECÇÃO DE ESTRUTURA

O parser deve identificar:
- capítulos,
- subtítulos,
- tabelas,
- listas,
- exemplos,
- fórmulas.

---

# 14. METADATA EXTRACTION

Cada documento deve gerar metadata:

```json
{
  "source": "Zi Ping Zhen Quan",
  "author": "Traditional",
  "language": "Chinese",
  "topic": "Useful God",
  "difficulty": "Advanced"
}
```

---

# 15. SEMANTIC SEGMENTATION

O texto deve ser dividido:
# semanticamente.

E NÃO:
- por página,
- por tamanho bruto,
- aleatoriamente.

---

# 16. IDEAL SEGMENTATION

Cada chunk deve conter:
- uma regra,
- um conceito,
- uma explicação completa.

---

# 17. EXEMPLOS DE CHUNKS

## Correto:
- “Rooting in Winter charts”
- “Strong Fire Useful God logic”

---

## Errado:
- metade de uma explicação,
- texto quebrado sem contexto.

---

# 18. DUPLICATE DETECTION

A pipeline deve detectar:
- chunks repetidos,
- regras duplicadas,
- exemplos redundantes.

---

# 19. VERSION CONTROL

Cada documento deve possuir:
- versão,
- data,
- origem,
- nível de confiança.

---

# 20. SOURCE HIERARCHY

A prioridade deve ser:

```text
Core Classical Texts
>
Validated Modern Sources
>
Interpretative Material
>
Community Content
```

---

# 21. TRANSLATION LAYER

Traduções devem:
- preservar significado técnico,
- preservar lógica estrutural,
- evitar simplificação exagerada.

---

# 22. MULTI-LANGUAGE MAPPING

O sistema deve mapear:

| Chinese | English | Portuguese |
|---|---|---|
| 用神 | Useful God | Deus Útil |
| 七杀 | Seven Killings | Sete Assassinatos |
| 比肩 | Friend | Companheiro |

---

# 23. GLOSSARY SYSTEM

Criar:
# glossário centralizado.

Isso evita:
- inconsistência terminológica,
- retrieval incorreto,
- embeddings confusos.

---

# 24. TAGGING SYSTEM

Cada chunk deve receber:
- tags estruturais,
- tags psicológicas,
- tags narrativas.

---

# 25. EXEMPLO DE TAGS

```json
{
  "topic": "Seven Killings",
  "layer": "Psychological",
  "traits": [
    "pressure",
    "competitiveness",
    "leadership"
  ]
}
```

---

# 26. QUALITY VALIDATION

Antes do embedding:
o sistema deve validar:
- OCR quality,
- semantic integrity,
- translation consistency,
- duplicate score.

---

# 27. EMBEDDING PREPARATION

Chunks devem:
- ser pequenos,
- semanticamente claros,
- altamente específicos.

---

# 28. PDF WARNING

PDFs metafísicos frequentemente possuem:
- traduções ruins,
- OCR ruim,
- terminologia inconsistente.

A pipeline deve tratar isso:
# agressivamente.

---

# 29. FUTURE DATABASE STRUCTURE

Idealmente:
o sistema deve armazenar:

| Layer | Function |
|---|---|
| Raw Text | original |
| Clean Text | normalizado |
| Semantic Chunk | retrieval |
| Embedding | busca vetorial |
| Tags | taxonomia |

---

# 30. AI INTERPRETATION RULE

A IA deve:
- preferir chunks confiáveis,
- priorizar fontes clássicas,
- evitar retrieval ambíguo.

---

# 31. FINAL PRINCIPLE

A qualidade da IA NÃO depende apenas:
do modelo.

Ela depende:
# da qualidade estrutural do conhecimento processado.

PDFs bem normalizados:
- aumentam coerência,
- reduzem hallucinations,
- melhoram profundidade,
- criam consistência interpretativa.
