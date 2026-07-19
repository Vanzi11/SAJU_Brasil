# app/ — Backend e geração de PDF

- `server.mjs` — backend HTTP sem dependências (Node ≥18). Rotas: `/` (UI), `/cidades`, `/leitura`, `/sinastria`, `/diaria`, `/pdf`. Rodar: `node app/server.mjs` (define TZ=Asia/Seoul internamente). Com `ANTHROPIC_API_KEY` + `gerarRelatorio:true`, gera o relatório narrativo via API.
- `public/index.html` — painel de teste (3 abas, autocomplete de cidades, botão Baixar PDF).
- `pdf/gerar_pdf.py` — gerador de PDF v4 (paramétrico, funciona para QUALQUER cliente; visual anterior). Requer `pip install reportlab pypdf`.
- `pdf/premium_v5/` — gerador do VISUAL APROVADO (v5, "livro de Seul", 18 págs), vindo do Lovable/Gemini. **Ainda hard-coded para o mapa do Ivã** — a tarefa nº 1 da próxima sessão é parametrizá-lo (ver CONTINUIDADE.md).
