# Project Timeline

> Living log of what was built, decided, and shipped. Maintained by the **CEO agent** — append a new entry at the top whenever meaningful work lands. Newest first.
>
> Entry format:
> ```
> ## YYYY-MM-DD — <short title>
> - **Done:** what was actually completed/shipped
> - **Decided:** key decisions made (and why, one line)
> - **Next:** what comes next
> - **Refs:** commits / files / PRs (optional)
> ```

---

---

## 2026-06-02 — Repo tidy-up (Repo Steward)
- **Done:** Merged `HISTORICO.md` into `TIMELINE.md` (rich history now the "Project history" section below the log) and removed the duplicate. Moved loose strategy docs to `docs/` (ACTION_PLAN, COMPETITOR_ANALYSIS, PRICING_STUDY, Guidelines). Kept `CLAUDE.md` at root (tooling file). Fixed references to moved files.
- **Decided:** `TIMELINE.md` is the single canonical project log; `docs/` holds strategy/analysis docs; tooling files stay at root.
- **Next:** Repo Steward sweeps after future changes so clutter never accumulates.
- **Refs:** `docs/`, `TIMELINE.md`

## 2026-06-02 — Estudo de precificação + análise de concorrentes
- **Done:** Pesquisa de mercado (competitive-analyst + market-specialist). Salvo em `docs/PRICING_STUDY.md` e `docs/COMPETITOR_ANALYSIS.md`.
- **Decided:** Preço = modelo **híbrido** (setup único + por-robô/mês). Piloto: R$12–18k setup + R$1.5–2.5k/mês (≤5 robôs). Escala: R$300–450/robô/mês. Âncora de mercado = Meili FMS €500/mês.
- **Next:** gtm-sales transforma em proposta de piloto; finance monta unit economics; validar preço em discovery real.
- **Refs:** `docs/PRICING_STUDY.md`, `docs/COMPETITOR_ANALYSIS.md`

## 2026-06-02 — AI team + project tracking set up
- **Done:** Built the AI-agent "company" in `.github/agents/` (CEO hub + 10 specialists). Made agents answer-first/concise. CEO became the single point of contact (hub-and-spoke). Added Senior Software Engineer. Started this timeline.
- **Decided:** Talk only to the CEO; it delegates and synthesizes. CEO owns and updates this timeline. Engineers commit to git constantly.
- **Next:** Resolve "app won't open" (suspected `Callbuttons.tsx`); implement real `1007.task` (LM1↔LM2) on dispatch; confirm return-button OPC UA node IDs.
- **Refs:** `.github/agents/`, commit `911ff5e`

<!-- Add new entries ABOVE this line, newest first. -->

---

# Project history (narrative background)

> Folded in from the former HISTORICO.md (rich narrative of how the project evolved). The dated log above is the running record; this section is the deeper background.

# 📜 Histórico do Projeto — da BehaveX à Orquestração de Frota AMR

> Documento vivo. Linha do tempo das features, decisões de arquitetura e marcos do projeto.
> Mantido como memória do que foi construído e por quê. Atualizar a cada marco relevante.
>
> Última atualização: **2026-06-02**

---

## 🧭 Resumo em uma frase

Começou como **BehaveX** — um dashboard React de simulação de enxames (swarm), só frontend com dados mock — e virou um **app desktop de orquestração de frota de AMRs industriais** (Electron + React + backend Flask), integrado a robôs SEER via TCP e a botões de chamada (callbuttons) de chão de fábrica via OPC UA.

---

## 🗓️ Linha do Tempo

### Fase 0 — BehaveX: dashboard de simulação de swarm  _(~abr/2026)_
O ponto de partida. Aplicação **somente frontend**, dados mockados no cliente, sem backend.

- **Stack:** React + TypeScript + Vite + Tailwind v4, tema dark estilo GitHub (`#0d1117` / `#58a6ff`), shadcn/ui (50+ componentes), React Router v7.
- **Marca/identidade:** "AeroNet v2.4.1".
- **Telas:**
  - `/` Dashboard — experimentos recentes, runs ativos, métricas
  - `/experiment/:id` — canvas de simulação com playback (500 steps, 12 agentes)
  - `/comparisons` — visão dupla lado a lado com diff de métricas (divergência destacada nos steps 150–200)
  - `/configs` — config de política de comportamento (URL GitHub, seeds, nº de agentes, densidade de obstáculos)
- **Estado:** simulação via `useState` + `useEffect` (intervalos), engine mock (`useSimEngine`).
- **Backlog documentado:** `docs/ACTION_PLAN.md` (2026-04-25) catalogou **18 itens de UI não implementados** — 11 botões "mortos", 2 interações quebradas (scrubber de timeline, validação de URL), 3 rotas placeholder, 2 implementações mock.
- **Ideia futura (na época):** otimização GPU/ML no Mac (mlx / WebGPU / ONNX) e um backend FastAPI servindo inferência real via WebSocket para substituir o engine mock.

> 🔑 **Decisão de fundação:** todo o estado de simulação era client-side. Isso forçou, mais tarde, a separação clara entre UI e um motor/backend real.

---

### Fase 1 — Aprendendo o robô SEER: protocolo, mapas e visualizadores  _(maio/2026)_
Mergulho no ecossistema **SEER Robotics** (a base dos AMRs). Foco em **entender o protocolo e os mapas** antes de integrar.

- **Protocolo Robokit Netprotocol** estudado e documentado (`context/README.md`): formato de pacote (magic `0x5A`, header 16 bytes big-endian + payload JSON) e portas:
  - `19204` estado/localização/bateria · `19205` controle de movimento/relocalização · `19206` tarefas de navegação · `19210` I/O digital.
- **Scripts de referência** (`context/`): demos de giro, relocalização, leitura de I/O, query de erros, etc. (`rbkDemo*.py`, `rbkApi*.py`).
- **Parser de mapas `.smap`** (formato RoboShop Pro / Protobuf-as-JSON):
  - `ANALISE_REPOSITORIO_SEER.md` — engenharia reversa da estrutura (`header`, `normalPosList`, `normalLineList`, `advancedPointList`, `advancedAreaList`…), descoberta de que os campos são **camelCase** (`minPos`, `maxPos`).
  - `RESUMO_ALTERACOES.md` — carregamento automático do `.smap` local (landmarks, paredes, pontos navegáveis, posição inicial, limites do mapa).
  - `RESUMO_MODO_OFFLINE.md` — **modo offline** nos visualizadores + cadeia de fallback (`.smap` local → robô via API → mapa vazio) e correção de bugs de parsing (JSON compacto em linha única, campos aninhados).
- **Visualizadores Python:** `visualizador_auto.py`, `visualizador_offline.py`, `visualizador_robo.py`, `visualizador_multi_robo.py` — render do mapa + posição do robô (com e sem robô conectado).
- **Mapas reais:** `maps/InnovationBox.smap`, `maps/1007.smap`.

> 🔑 **Aprendizado-chave:** o robô fala TCP + JSON, e os mapas têm tudo que precisamos (landmarks/estações = `advancedPointList`). Dá pra desenvolver **offline** com o `.smap` — isso virou princípio de arquitetura (Sim provider).

---

### Fase 2 — O pivô: de simulação de swarm para orquestração de frota  _(final de maio/2026)_
A BehaveX deixa de ser brinquedo de simulação e vira **plataforma de orquestração de frota AMR** real. O frontend foi reaproveitado; nasce o backend.

- **Nova arquitetura (3 camadas):**
  - **Electron** (`electron/main.ts` + `preload.ts`) — wrapper desktop.
  - **Frontend React** — reescrito para operação de frota.
  - **Backend Flask** (porta `8765`) — REST + **SSE `/events`** (stream ~10 Hz), `fleet.db` (SQLite) para telemetria.
- **Novas telas:** `/` Dashboard (visão da frota), `/field` (mapa/posições ao vivo), `/devices` (inventário de robôs), `/calibration` (+ `/:robotId`, jog manual), `/tasks` (definição/despacho), `/callbuttons` (vínculos OPC UA), `/settings`.
- **Backend modular:**
  - `models.py` — `Robot`, `Station`, `Task`, `MapModel` + máquinas de estado (status do robô e da tarefa).
  - `dispatcher.py` — máquina de estados da frota (asyncio): atribuição do melhor robô ocioso (distância + bateria), travas por estação (1 tarefa por pickup), auto-carga (<25% bateria), coalescência de chamadas.
  - `provider.py` — interface `Provider` + `SimProvider` (move robôs fake rumo ao goal) → **dev 100% offline**.
  - `seer/` — `protocol.py` (codec TCP), `robot_conn.py` (conexão por robô), `provider.py` (`SeerProvider` mapeia estações → landmarks SEER).
  - `db.py` + `telemetry.py` — persistência e captura dupla (JSONL + SQLite) com `run_id`/`cycle_id`/`step`.
  - `smap.py` — parser `.smap` portado para o backend.

> 🔑 **Decisão de arquitetura:** abstração `Provider` (Sim ↔ SEER) — mesma lógica de despacho roda em simulação ou em robô real. Foi o que permitiu evoluir rápido sem hardware na mesa.

---

### Fase 3 — ⚡ O sprint dos Callbuttons  _(quinta 28 e sexta 29/maio/2026)_
**O grande salto.** Em dois dias o projeto saiu de "peças soltas" para um **fluxo ponta-a-ponta funcionando** com botões de chamada de chão de fábrica.

- **Driver OPC UA** (`opcua/callbuttons.py`, lib `asyncua`): assina nós booleanos das estações, detecção de **borda de subida** (False→True = botão pressionado) → `dispatcher.button_pressed(station_id, direction)`, com reconexão (backoff ~10s).
- **Fluxo pareado supplier→consumer:** ex. **Almox → Linha**, com estados de pressão (`idle`/`ready`/`called`/`served`) e direção (`fwd`/`ret`). UI em `Callbuttons.tsx`.
- **Resultado:** apertar o botão físico → backend cria/atribui tarefa → robô (sim ou SEER) é despachado → estado reflete na UI ao vivo via SSE.
- **Marco em git:** commit `ec7357e` "mudanças de hoje" (sex **29/05**) — primeira versão do repositório com a integração funcionando.

> 🏁 **Por que importa:** este é o "momento da verdade" do produto — o gatilho real do operador no chão de fábrica dispara a frota. É a feature que prova o valor (one pilot done well).

---

### Fase 4 — Consolidação "all the features"  _(terça 02/jun/2026 — hoje)_
- **Marco em git:** commit `911ff5e` "Last version with all the features" (**02/06**).
- Estado atual consolidado (ver inventário abaixo). Início de um novo sprint de evolução.
- Onboarding do "time de agentes de IA" (CEO + especialistas) como forma de trabalho.

---

## 🧩 Inventário atual de features  _(snapshot 2026-06-02)_

### Frontend (Electron + React + Vite + Tailwind v4)
| Rota | Tela | Função |
|------|------|--------|
| `/` | Dashboard | Visão geral da frota: robôs ativos, tarefas, alarmes |
| `/field` | Field | Mapa SVG ao vivo, posições dos robôs, criação manual de tarefa |
| `/devices` | Devices | Tabela da frota: IP, status, bateria, posição, tarefa atual |
| `/calibration` | Calibration | Jog manual do robô (frente/trás/giro/stop), por robô |
| `/tasks` | Tasks | Lista de tarefas ativas/histórico com badges de estado |
| `/callbuttons` | Callbuttons | Fluxo pareado de botões (Almox→Linha) via OPC UA |
| `/settings` | Settings | URL do backend, status de conexão, health check |

- Componentes: `Layout` (sidebar, 7 itens), `MapCanvas` (transform metros→pixels, robôs/estações/paredes), kit shadcn/ui (50+).

### Backend (Flask + asyncio + Python)
| Módulo | Função |
|--------|--------|
| `main.py` | Flask :8765, SSE `/events` ~10 Hz, REST (robots/tasks/stations/health, POST callbutton/relocalize) |
| `models.py` | `Robot`/`Station`/`Task`/`MapModel` + máquinas de estado |
| `dispatcher.py` | Despacho da frota: melhor robô ocioso, travas de estação, auto-carga |
| `provider.py` | Interface `Provider` + `SimProvider` (dev offline) |
| `seer/protocol.py` | Codec TCP Netprotocol (ports 19204/19205/19206/19210) |
| `seer/robot_conn.py` · `seer/provider.py` | Conexão por robô + `SeerProvider` (estação→landmark) |
| `opcua/callbuttons.py` | Driver OPC UA, detecção de borda de subida |
| `smap.py` | Parser de mapas `.smap` (SEER) |
| `db.py` · `telemetry.py` | SQLite `fleet.db` + captura dupla (JSONL + SQLite) |
| `soak.py` | Runner de soak test (cycle/step) para fidelidade de dados |

### Plataforma
- **Electron** v33 (build macOS `.dmg`, appId `com.behavex.app`).
- **Mapas:** `maps/InnovationBox.smap`, `maps/1007.smap`.
- **App:** `behavex` v`0.1.0`.

---

## 🧱 Decisões de arquitetura (e como mudaram)

| # | Decisão | Antes | Agora | Por quê |
|---|---------|-------|-------|---------|
| 1 | Origem dos dados | Mock client-side (BehaveX) | Backend Flask + SSE ao vivo | Operação real de frota exige estado de servidor |
| 2 | Abstração de robô | — | Interface `Provider` (Sim ↔ SEER) | Desenvolver e testar sem hardware |
| 3 | Gatilho de tarefa | Botão de UI | **Callbutton físico via OPC UA** | Fluxo real de chão de fábrica |
| 4 | Mapas | Hardcoded/mock | Parser `.smap` real (SEER) | Posições/landmarks reais |
| 5 | Persistência | Nenhuma | SQLite + JSONL firehose | Telemetria e soak tests |
| 6 | Empacotamento | Web only | Electron desktop | Implantação no cliente |

---

## 🗺️ Próximos passos  _(placeholder — sprint em curso)_
> A detalhar com o time. Preencher conforme o sprint avança.

---

## ✏️ A adicionar (pendências de memória)
- [ ] **Rascunhos de arquitetura original** (papel) — o founder vai enviar; documentar como a arquitetura foi pensada vs. como ficou.
- [ ] Datas exatas da Fase 0 (BehaveX) e Fase 1 (pré-git, anteriores a 29/05).
- [ ] Screenshots/GIFs de cada marco (Dashboard BehaveX → Field AMR → Callbuttons).
- [ ] Lista nominal de bugs marcantes resolvidos no sprint dos callbuttons.

---

_Notas: a história anterior a 29/05/2026 é anterior ao git (reconstruída a partir do código, dos docs em `context/` e do `docs/ACTION_PLAN.md`). Datas dessas fases são aproximadas._
