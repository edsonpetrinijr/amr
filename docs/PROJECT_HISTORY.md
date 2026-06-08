# Histórico do Projeto — narrativa de fundo

> Movido para fora da `TIMELINE.md` (que agora é um índice de logs diários em `docs/log/`).
> Esta é a história mais profunda de como o projeto evoluiu — atualizar só em marcos relevantes.

---

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

### Fase 4 — Consolidação "all the features"  _(terça 02/jun/2026)_
- **Marco em git:** commit `911ff5e` "Last version with all the features".
- Estado consolidado: 7 telas + backend modular + Sim/SEER + OPC UA + telemetria.
- Onboarding do "time de agentes de IA" (CEO + especialistas) como forma de trabalho — CEO é o ponto único de contato e mantém esta timeline.

---

### Fase 5 — Endurecimento de engenharia (Sprints 0–4)  _(02/jun/2026)_
De "tudo funciona na demo" para "aguenta turno real". Cinco sprints encadeados:

- **S0 — Limpeza:** removidas as telas/ML mortas da era BehaveX (swarm, ws-bridge); Dashboard ligado a dados ao vivo; `CLAUDE.md` reescrito.
- **S1 — Recuperação de falhas (FSM):** corrigido bug real — navegação falha era tratada como chegada. Agora há re-fila, cooldown, park, offline/stuck/bateria e alarmes (6 testes). `arrived()` ⇒ só `TASK_FINISHED`.
- **S2 — Endurecimento OPC UA:** reconexão com backoff, subscribe por nó, debounce, seed na conexão; corrigido bug real de match de node-id. Mock server + 4 testes + checklist de planta.
- **S3 — Completude do operador:** `/jog`, STOP-ALL/RESUME por software, telemetria/histórico/stats; UI com d-pad de jog, botão global STOP e faixa de analytics (10 testes).
- **S4 — Higiene de tooling:** ESLint 9 (0 warnings), `tsc` (0 erros), soak runner + telemetria firehose commitados.

> 🔑 **Decisão:** STOP-ALL de software **não** é E-stop de hardware (rotulado em 3 lugares da UI). A abstração `Provider` mantém o despacho agnóstico de hardware.

---

### Fase 6 — Pilot Hardening sem hardware  _(02/jun/2026 — hoje)_
Founder sem acesso a robô físico no momento → estratégia de provar tudo em simulação, deixando a sessão no robô como **confirmação**, não descoberta.

- **Preflight + readiness:** validação de config na subida + `/health` reporta prontidão.
- **Modelo de dupla pose no `SimProvider`:** pose verdadeira vs. pose estimada + confiança (decay/perda/mislocalização/relocalize por proximidade) → o FSM de recuperação e o loop de relocalização-assist rodam ponta-a-ponta em sim, com testes determinísticos.
- **Camada LiDAR/laser:** engenharia reversa da API SEER (`1009` na 19204, `laser_beams` = `[x,y]` em frame do mapa). Endpoint pull `GET /robots/<id>/laser` (~2Hz, fora do SSE 10Hz), `SimProvider.laser()` via ray-cast contra paredes do `.smap` (offline) e `SeerProvider.laser()` para robô real; toggle "Laser" no Field renderiza os feixes.

> 🔑 **Decisão estratégica (revisão de time):** próximo foco = **Pilot Hardening** (relocalização-assist guiada + handshake à prova de turno + preflight + runbook de dry-run no robô). GTM formaliza o site morno num **piloto pago time-boxed**; métrica única = **SLA de entrega on-time na estação de consumo**.

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
| `main.py` | Flask :8765, SSE `/events` ~10 Hz, REST (robots/tasks/stations, `/health` readiness, POST callbutton/relocalize, `/robots/<id>/laser`, `/jog`, STOP-ALL/RESUME) |
| `models.py` | `Robot`/`Station`/`Task`/`MapModel` + máquinas de estado + campos de recuperação |
| `dispatcher.py` | Despacho da frota: melhor robô ocioso, travas de estação, auto-carga, recuperação de falhas (re-fila/cooldown/park) |
| `provider.py` | Interface `Provider` + `SimProvider` (dev offline, dupla pose + laser sintético) |
| `seer/protocol.py` | Codec TCP Netprotocol (ports 19204/19205/19206/19210) + laser `1009` |
| `seer/robot_conn.py` · `seer/provider.py` | Conexão por robô + `SeerProvider` (estação→landmark, laser real) |
| `opcua/callbuttons.py` | Driver OPC UA, detecção de borda de subida (backoff, debounce) |
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
| 7 | Validação sem robô | Só na demo/robô | Sim de dupla pose + testes determinísticos | Provar FSM/relocalização offline; robô vira confirmação |

---

## 🗺️ Próximos passos  _(sprint "Pilot Hardening")_
- Relocalização-assist v1: de endpoint manual para **workflow guiado** (nearest-landmarks API + UI de assist).
- Handshake do callbutton à prova de turno: timeouts, dedup, deadlocks, "quem age a seguir".
- Confirmar no **primeiro robô real**: frame do `laser_beams` ([x,y] mundo vs. relativo), tolerâncias de relocalização, STOP/RESUME, alinhamento de mapa, node IDs OPC UA (≈60 min de checklist).
- GTM: fechar o site morno como **piloto pago time-boxed** com data de go/no-go.

---

## ✏️ A adicionar (pendências de memória)
- [ ] **Rascunhos de arquitetura original** (papel) — o founder vai enviar; documentar como foi pensada vs. como ficou.
- [ ] Datas exatas da Fase 0 (BehaveX) e Fase 1 (pré-git, anteriores a 29/05).
- [ ] Screenshots/GIFs de cada marco (Dashboard BehaveX → Field AMR → Callbuttons → Laser).
- [ ] Lista nominal de bugs marcantes resolvidos no sprint dos callbuttons.

---

_Notas: a história anterior a 29/05/2026 é anterior ao git (reconstruída a partir do código, dos docs em `context/` e do `docs/ACTION_PLAN.md`). Datas dessas fases são aproximadas._
