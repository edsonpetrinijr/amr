# Daily logs

One Markdown file per day: `AAAA-MM-DD.md` (ex.: `2026-06-08.md`). Newest day is whatever date it is today.

Each daily file has two parts:

1. **`## Resumo do dia`** — no topo, pra você bater o olho rápido e confirmar:
   - **Aconteceu:** o que de fato rolou no dia (1–4 linhas).
   - **Decidido:** decisões-chave (e o porquê, em uma linha).
   - **Próximo:** o que fica pendente pra amanhã.
2. **`## Log`** — cronológico, com **horário estimado** por ação:
   - `- HH:MM — o que foi feito (refs/commits)`
   - Os horários são estimativas (reconstruídos dos timestamps dos commits + memória do dia). Não precisam ser exatos.

A [`TIMELINE.md`](../../TIMELINE.md) na raiz é o **índice** desses arquivos (uma linha por dia + link). A narrativa de fundo do projeto vive em [`PROJECT_HISTORY.md`](../PROJECT_HISTORY.md).

Quem mantém: o **CEO agent** — a rotina `/end-of-day-routine` cria/atualiza o arquivo do dia e a linha no índice; a `/morning-routine` lê os últimos.

---

## Template

```markdown
# AAAA-MM-DD

## Resumo do dia
- **Aconteceu:** 
- **Decidido:** 
- **Próximo:** 

## Log
- 09:15 — 
- 11:40 — 
- 16:20 — 
```
