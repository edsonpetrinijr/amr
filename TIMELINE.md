# Project Timeline — índice de logs diários

> Cada dia tem seu próprio arquivo em [`docs/log/`](docs/log/) com **Resumo do dia** (Aconteceu / Decidido / Próximo) no topo e um **Log** cronológico com horário estimado por ação. Newest first.
>
> Mantido pelo **CEO agent**: a rotina de fim de dia cria/atualiza o arquivo do dia; a de manhã lê os últimos. Narrativa de fundo em [`docs/PROJECT_HISTORY.md`](docs/PROJECT_HISTORY.md).

| Dia | Resumo |
|-----|--------|
| [`2026-06-11`](docs/log/2026-06-11.md) | Retomada da PoC na `feat/poc-conversor-torque-sim` + hardening de producao (gates de simulacao em backend/frontend) + filtro de mapa para ocultar callbuttons sem landmark (remove ruido como Linha A/B/C). Validacao tecnica: backend **83 passed** + `test_devices_api` **17 passed**, frontend `typecheck` + `lint` OK. Merge iniciado com seguranca via worktree (`main` fast-forward da branch PoC) e limpeza estrutural do repo (artefatos de build removidos + backlog consolidado). Dois commits locais prontos para PR split (funcional + cleanup). |
| [`2026-06-10`](docs/log/2026-06-10.md) | PoC Conversor de Torque (sim + dual-AMR), branch `feat/poc-conversor-torque-sim`. **Build de empresa:** `docs/POSITIONING.md` (5 Pilares + afiação competitiva), landing reformada nível-empresa, deck `docs/DECK_PILOTO.md`. Wedge = "missões multi-robô interdependentes c/ confirmação física". |
| [`2026-06-09`](docs/log/2026-06-09.md) | Reunião DOS (tablet substitui etiquetas): extrair info p/ alimentar o AMR numa célula dedicada sempre-AMR; DOS = muitas sprints → **estratégia de desacoplar e depender o mínimo do DOS** (usar o feed já achado). **Célula-piloto escolhida por dados (TRANVR2): BT30CS principal / BT09TC backup** — validar fisicamente c/ Cleber/Douglas/Fábio. M4 Boot destravado: trick-m4-6.13.4 + JDK 17 instalados manualmente (proxy CAT). |
| [`2026-06-08`](docs/log/2026-06-08.md) | Feed de pedidos da CAT decodificado + fontes reais (txt/Oracle) achadas; alinhamento Zampim; MVP da linha de montagem; polimento pré-demo (pt-BR + branding). |
| [`2026-06-03`](docs/log/2026-06-03.md) | Dia cheio: render AMR (2D/3D), modelo W3 colorido, seletor de mapa, devices/callbuttons, relocalização-assist; rename desktop/server; visita de campo. |
| [`2026-06-02`](docs/log/2026-06-02.md) | Time de agentes de IA montado + timeline iniciada; Sprints 0–4 + LiDAR; pivô "sem robô" (Pilot Hardening); estudo de preço/concorrentes. |

<!-- Novos dias entram no TOPO da tabela. Crie o arquivo docs/log/AAAA-MM-DD.md e adicione a linha aqui. -->
