# PROTOCOLO DE SESSÃO — obrigatório para toda IA que trabalhar neste repositório

Regra de ouro: **se não está no repositório, não aconteceu.** Conversas são efêmeras; o repositório é a memória da empresa. Cada falha listada aqui já ocorreu de verdade — o protocolo existe para que não ocorra de novo.

## Ao ABRIR a sessão

1. Ler `CONTINUIDADE.md` inteiro e seguir sua ordem de leitura.
2. Rodar `git status` e `git log --oneline -5`: se houver mudanças não commitadas ou commits com mensagem vazia/estranha, avisar o Ivã ANTES de começar trabalho novo.
3. Conferir se as "Demais pendências" do CONTINUIDADE.md batem com o último bloco do DECISOES.md — se algo já foi concluído e não está marcado, corrigir na hora.

## Durante a sessão

4. **Decisão tomada = D# registrado imediatamente** em `empresa/DECISOES.md` (número sequencial, data, contexto, o que muda). Não acumular para o fim — sessões são interrompidas sem aviso (limite de tokens, quedas). *Falha real: a sessão Fable quase perdeu D9–D13 por registrar em lote.*
5. Toda amostra de PDF/relatório gerada vai para `relatorios/exemplos/` com nome descritivo (`produto_pessoa_ano_AMOSTRA_vN`), nunca só em /tmp. *Falha real: o script original do v5 foi perdido porque só existia no sandbox efêmero do Lovable.*
6. Criou pasta ou arquivo importante? Atualizar o `README.md` da pasta no mesmo turno.
7. Mudou layout/gerador? Testar com **dados reais e texto de tamanho de produção** antes de dar por pronto (lição do D18 — fixtures curtos escondem bugs).

## Ao ENCERRAR a sessão (checklist de saída — executar SEMPRE que o Ivã sinalizar pausa/fim, ou a cada entrega grande)

8. `DECISOES.md` atualizado? (checar contra o que foi feito na conversa)
9. `CONTINUIDADE.md`: pendências concluídas marcadas com ✅ e D#? Novas pendências adicionadas? Alguma seção envelheceu ("Tarefa nº1", contagem de decisões, status dos produtos)?
10. **Bloco de commit pronto para o Ivã copiar**, sempre neste formato (PowerShell — uma linha por comando, nunca `&&`, mensagem já escrita entre aspas):

```powershell
git add .
git commit -m "mensagem descritiva do que foi feito nesta rodada"
git push
```

*Falha real: 3 commits entraram no histórico com a mensagem "0" porque o bloco não foi entregue pronto.*

## Auditoria periódica (a cada 3–4 sessões)

11. Uma sessão dedica 15 minutos a: ler o transcript das sessões recentes (`session_info`), cruzar com DECISOES.md/CONTINUIDADE.md, corrigir drifts, verificar `git log` e `.gitignore`. Registrar a auditoria como D#.

## O que NUNCA fazer

- Reverter decisão registrada sem novo D# explicando o porquê.
- Editar `empresa/GUIA_DE_VOZ.md` ou os prompts de `relatorios/prompts/` sem discussão prévia com o Ivã — são os ativos centrais.
- Deixar segredo (API key, token, senha) em qualquer arquivo do repositório.
- Commitar `node_modules/`, `dist/`, `.claude/`, caches (o `.gitignore` cobre — não remover entradas).
