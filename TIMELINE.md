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

## 2026-06-03 — 3D preview reconciled to truth: orphan GLB removed, honest to-scale stand-in
- **Done:** Objectively inspected `public/AMR.glb` with trimesh: **10 parts, 3745 verts / 4536 faces, AABB 0.065 × 0.090 × 0.0285 m** — a thin bracket/fastener sub-assembly, NOT a robot (matches the tiny `AMR.step` AABB; same sub-part). **Verdict: SUB-PART / NOT A ROBOT.** Executed **Case B**: kept the dimensionally-honest to-scale `PlaceholderChassis` as the shipped preview, **`git rm`'d the orphan `public/AMR.glb`**, reduced the `RobotPreview3D` GLB TODO to a one-line "real full-assembly export pending", and reconciled `docs/phase2-3d-preview.md` + this log to state the honest reason (CAD export was a sub-part, not the chassis). typecheck + lint + `tsc && vite build` green; three.js still lazy-split into its own chunk.
- **Decided:** Do NOT fake a robot from a sub-part. The in-app 3D preview is a **to-scale stand-in** (0.85×0.65×0.30 m), not the real robot mesh, until a proper full-assembly STEP/GLB lands from the founder.
- **Refs:** `frontend/app/components/RobotPreview3D.tsx`, `docs/phase2-3d-preview.md` (removed `public/AMR.glb`)

---

## 2026-06-03 — AMR render shipped: to-scale 2D footprint + isolated 3D preview (dims reconciled to W3-600B URDF, 0.85×0.65×0.30)
- **Done:** **Phase 1** — robot renders to real-world scale in Field view. Added data-driven `footprint` field to the Robot model (`types.ts` + `models.py`, serialized into the SSE world payload) with a shared default; `MapCanvas` draws a status-colored rounded-rect at `length·scale × width·scale` rotated by θ (replacing the hardcoded `bodyR=10` circle), heading/label/battery/selection preserved. **Phase 2** — opt-in, isolated 3D preview: lazy-loaded `RobotPreview3D.tsx` (react-three-fiber + drei: orbit, grid, lighting) renders a **to-scale procedural placeholder box** sized from the footprint, with a single marked `TODO(GLB)` swap point. three.js is a separate chunk loaded only on the "3D" toggle (mimics Laser toggle) — zero cost to the initial bundle / 10 Hz SSE path. **Dimensions reconciled:** validated the public **SEER W3-600B** (GilmarCorreia/sim_models) URDF as the authoritative source → **L 0.85 × W 0.65 × H 0.30 m** (lidar-to-lidar length, tray width, tray-raised height; drive-wheel track 0.5575 m), applied across FE/BE/3D (`DEFAULT_FOOTPRINT={0.85,0.65}`, `DEFAULT_HEIGHT_M=0.30`) — supersedes the earlier 0.95×0.65×0.25 guess. typecheck + lint exit 0.
- **Decided:** Use only **derived scalar dimensions** from the W3-600B repo; **do NOT vendor its meshes/STL/GLB** — repo is **GPL-3.0** (copyleft, `package.xml` license=`TODO`), a hard restriction for our proprietary stack. `AMR.step` is only a **sub-component** (~0.065×0.090×0.029 m), not a usable chassis reference — discarded as a scale source. A `public/AMR.glb` was generated from it (cascadio/OCCT) but contained only that sub-part and was **NOT loaded** (placeholder box rendered instead); it has since been **removed as an orphan** (see 2026-06-03 reconcile entry). Any real in-app mesh must come from a license-clean, full-assembly GLB at the marked swap point. 3D stays an isolated opt-in panel, never in the 10 Hz hot path or the 2D source-of-truth map.
- **Next:** Legal to confirm the GPL-3.0 boundary before any asset reuse. Founder: confirm the physical unit is truly a W3-600B so 0.85×0.65×0.30 is final, and provide a proper full-assembly STEP/GLB export. (optional) per-robot footprint from real hardware config. Run full backend `pytest` in a provisioned venv.
- **Refs:** commit `10873ac`; `frontend/app/api/types.ts`, `components/{MapCanvas,RobotPreview3D}.tsx`, `pages/Field.tsx`, `backend/app/models.py`, `docs/phase2-3d-preview.md`; CTO GLB/isolation spec; GilmarCorreia/sim_models (GPL-3.0)

## 2026-06-03 — OPC UA → MQTT migration study (planning only, no change)
- **Done:** CTO produced a decision-grade study on whether to move plant-floor call-button signaling from OPC UA to MQTT. Saved to `docs/OPCUA_VS_MQTT_STUDY.md` (honest protocol comparison for our exact use case, "who produces the signal" analysis, recommendation, high-level migration plan, risks + cheapest experiment, mini-ADR).
- **Decided:** **Stay on OPC UA for the pilot — do not migrate now.** MQTT/Sparkplug is a multi-site/IIoT scale play, not a pilot necessity; migrating now would *add* infra (broker + PLC→MQTT bridge) for zero SLA benefit and re-spend our hardened S2 OPC UA work. Cheap insurance = (later) refactor the button driver behind a `CallButtonProvider` interface (mirror Sim↔SEER) so MQTT is a plug-in if a plant ever requires it. Founder confirmed: no change for now.
- **Next:** Fold ONE question into the plant node-id conversation — "buttons via OPC UA or MQTT/Sparkplug, and who owns the bridge?" Their answer decides everything. Revisit at multi-site scale.
- **Refs:** `docs/OPCUA_VS_MQTT_STUDY.md`, `docs/OPCUA_INTEGRATION.md`, `backend/app/opcua/`

## 2026-06-03 — Project kickoff: to-scale AMR render in Field view (STEP → app)
- **Done:** Recon of the viz stack for the founder's `AMR.step` (Onshape/STEP AP242). Findings: `MapCanvas` is **2D SVG top-down**, robot is a hardcoded `bodyR=10` circle with **no real-world scale**; **no robot-dimension field exists** anywhere (frontend `types.ts`, backend `models.py`/`smap.py`); **no 3D libs** installed. Corrected a wrong assumption: the **scale reference is NOT in the `.smap`** (it only carries map bounds + `resolution` 0.02 m/px) — the true robot footprint comes from the **STEP file's own CAD units** (bounding box).
- **Decided:** Two-track, phased to not disrupt in-flight features. **Track A (offline asset pipeline):** convert `AMR.step` → `AMR.glb` (+ extract true L×W×H) once, commit the lightweight asset; no runtime STEP parser. **Track B (render):** **Phase 1** — data-driven, to-scale **top-down footprint** on the existing SVG map (correct scale, low risk, ships first). **Phase 2** — optional **3D "bonitinho" preview** panel (react-three-fiber + drei) loading the GLB, isolated from the 10Hz SSE hot path. Add a `footprint`/`dimensions` field to the robot model so size is data-driven, not hardcoded.
- **Next:** senior-engineer runs Track A (pipeline + dims) → Phase 1 footprint; cto-architect signs off the GLB pipeline + 3D panel isolation; defer Phase 2 until current feature work lands. Founder: confirm real robot model (length/width/height) so we sanity-check the STEP bbox.
- **Refs:** `AMR.step`, `frontend/app/components/MapCanvas.tsx`, `frontend/app/pages/Field.tsx`, `frontend/app/api/types.ts`, `backend/app/{models,smap}.py`

## 2026-06-03 — Relocalization-assist loop (backend) shipped + full-day plan
- **Done:** Built **Feature 3** (nearest-landmarks API `GET /api/relocalize/suggestions` — robot_id or explicit pose, meters frame, sorted+clamped, proper 4xx/409) and **Feature 4** (dispatcher recovery-alarm enrichment — structured SSE payload `action=RELOCALIZE_ASSIST_V1` with last_pose/reason/suggestions_url/incident_id, **latched** so it fires once per incident and re-arms after recovery). 45 backend tests green (was 36). Frontend `AlarmMsg.payload` typed for the UI engineer. Team planned the full day; marketing delivered full PT-BR landing copy.
- **Decided:** Product name recommendation = **FluxoFleet** (PT/EN-friendly, needs trademark check). Landing = static React/Tailwind route, single CTA "Solicitar piloto", mailto/WhatsApp today. **Defer** handshake floor-proofing (F6) + full runbook (F7) to next week. Landmarks have no theta/name in `.smap` (id/x/y only) — suggestions use lm_id as name, theta null.
- **Next:** Feature 5 — Assist UI panel (consume alarm payload → fetch suggestions → one-click fill X/Y/θ → reuse /relocalize). Then landing page v1. Founder: confirm name + 2 app screenshots + contact email.
- **Refs:** `backend/app/smap.py`, `main.py`, `dispatcher.py`, `models.py`, `frontend/app/api/types.ts`; product day plan + marketing copy

## 2026-06-03 — Repo hygiene: build artifacts untracked + recovered lost files
- **Done:** Fixed `.gitignore` — added a clean `# Build artifacts` block (`dist`, `dist-electron`, `release`) and removed the duplicate stray `dist`. Untracked already-committed artifacts without deleting from disk (`git rm --cached`): `dist-electron` (2 files), `dist` (3 files). Restored `TIMELINE.md`, `CLAUDE.md`, `run-backend.bat` from HEAD — they'd been deleted from the working tree (unstaged, pre-existing; not caused by the artifact untrack). Left unstaged for founder review (not committed).
- **Decided:** Build outputs stay out of version control (regenerated by `npm run build`). Kept `electron/` as a top-level sibling — rejected moving it under `frontend/`: main/preload is the privileged desktop host, not renderer code, and the main/renderer split is a security boundary worth keeping visible. No monorepo tooling (overhead for solo founder mid-pilot).
- **Next:** Optional follow-up hygiene pass for other tracked runtime artifacts (`__pycache__/*.pyc`, `backend/fleet.db`). Founder to confirm before commit.
- **Refs:** `.gitignore`; cto-architect layout review

---

## 2026-06-02 — Timeline consolidated + history rewritten
- **Done:** Snapshotted the previous `TIMELINE.md` into `context/TIMELINE_snapshot_2026-06-02.md` (untouched backup) and rewrote the "Project history" section to be tighter and current — now covering the engineering hardening sprints (S0–S4), the no-hardware pivot (dual-pose sim, preflight), and the laser/LiDAR layer that the old narrative stopped short of.
- **Decided:** Dated log = canonical running record; narrative = concise evolution story. Both live in one file; raw backups go to `context/`.
- **Next:** keep appending dated entries as work lands; refresh the narrative only at major phase boundaries.
- **Refs:** `TIMELINE.md`, `context/TIMELINE_snapshot_2026-06-02.md`

## 2026-06-02 — LiDAR/laser-scan visualization shipped (sim-first)
- **Done:** Reverse-engineered the SEER laser API the founder was missing — `robot_status_laser_req = 1009` on port 19204, response `laser_beams` = list of `[x,y]` points already in **world/map frame** (from netprotocol PDF p.24). Built end-to-end: backend `GET /robots/<id>/laser` pull endpoint (off the 10Hz SSE path, ~2Hz, `step` decimation); `SeerProvider.laser()` for real robot; `SimProvider.laser()` synthesizes a realistic scan via ray-cast against `.smap` walls from est_pose (works fully offline); Field "Laser" toggle + `MapCanvas` renders beams over the map. Deterministic backend test + lint/tsc clean.
- **Decided:** Transport = dedicated pull endpoint polled only while the layer is ON (not in world SSE) to protect the 10Hz loop. Render directly with world→pixel transform (no pose composition) per PDF contract.
- **Next:** Confirm on first real robot that `laser_beams` is truly world-frame `[x,y]` (vs robot-relative/angle-distance) — flagged in code at all 3 sites. Fast-follows available nearly free: 1010 planned-path overlay, 1006 block-point marker.
- **Refs:** commit `8dd8905`; `backend/app/seer/protocol.py`,`robot_conn.py`,`provider.py`, `backend/app/provider.py`, `main.py`, `frontend/app/pages/Field.tsx`, `components/MapCanvas.tsx`

## 2026-06-02 — No-robot pivot: "Pilot Hardening" runs fully in sim
- **Done:** Founder has no physical robot access right now. CTO designed a no-hardware path: turn `SimProvider` into a **dual-pose localization model** (true pose vs estimated pose + confidence decay / loss / mislocalization / relocalize-success-by-proximity) so the recovery FSM and relocalization-assist loop are exercised end-to-end in sim with deterministic tests. Defined the honest "irreducible 60-min on-robot confirmation checklist" (TCP semantics, relocalize tolerances, STOP/RESUME, map alignment, OPC UA node wiring) — everything else ships from sim.
- **Decided:** Build order = preflight config validation → dual-pose sim model → nearest-landmarks API → recovery-alarm enrichment → assist UI → handshake floor-proofing → dry-run runbook. The eventual robot session becomes a *confirmation*, not discovery.
- **Next:** senior-engineer builds steps 1–2 (preflight + sim localization model) first (shippable + tested); then chain the assist API/UI. GTM SOW proceeds in parallel.
- **Refs:** cto-architect design; `backend/app/provider.py`, `dispatcher.py`, `smap.py`

## 2026-06-02 — Next-sprint decision: "Pilot Hardening" (team review)
- **Done:** Full team review (product-manager + domain-expert + gtm-sales). Strong convergence: plumbing is strong, but a real pilot dies on (a) relocalization-assist being only a manual endpoint, not a guided workflow; (b) the 2-button handshake surviving demo but not real shift behavior (timeouts, dedup, deadlocks, "who acts next"); (c) recovery FSM never validated on real SEER signals.
- **Decided:** Next sprint = **Pilot Hardening** (relocalization-assist v1 + handshake floor-proofing + preflight config validation + real-robot dry-run runbook). In parallel, GTM **formalizes the warm site into a paid, time-boxed pilot SOW** with a go/no-go date. The one pilot metric = **on-time delivery SLA to the consumer station**. De-risk first with the cheapest experiment: one real robot, real map, prove pose-frame sanity + relocalize recovery BEFORE building more.
- **Next:** senior-engineer/cto-architect scope Sprint "Pilot Hardening"; gtm-sales drafts 1-page pilot SOW; founder confirms OPC UA node IDs + plant access.
- **Refs:** delegations (PM/domain/GTM), `docs/OPCUA_INTEGRATION.md`

## 2026-06-02 — Sprints 0–4 shipped (engineering)
- **Done:** S0 cleanup (deleted dead swarm/ML UI, live Dashboard). S1 failure-recovery FSM (fixed real bug: failed nav was treated as arrival; re-queue + cooldown + park + alarms, 6 tests). S2 OPC UA hardening (backoff reconnect, per-node subscribe, debounce, seed-on-connect; fixed real node-id-matching bug; mock server + 4 tests + plant checklist). S3 operator completeness (/jog, software STOP-ALL/RESUME, telemetry/history/stats; UI jog d-pad, global STOP button, analytics strip; 10 tests). S4 tooling hygiene (ESLint 9, lint 0 warnings, tsc 0 errors, soak/telemetry committed).
- **Decided:** Software STOP-ALL is explicitly NOT a hardware E-stop (labeled in 3 UI places). Provider abstraction (Sim↔SEER) keeps dispatch logic hardware-agnostic.
- **Next:** validate recovery on real hardware; build relocalization-assist (see entry above).
- **Refs:** commits `0ea0a03`→`27487e2`, `eslint.config.mjs`, `backend/tests/`

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
