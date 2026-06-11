# FluxoFleet AMR (CAT) — Action Plan de Execucao (MVP Interno)

Gerado em: 2026-06-11  
Janela alvo: ate 2026-06-29  
Escopo: MVP interno da celula de sub-montagem de conversor de torque

---

## 1. Objetivo de entrega

Entregar v1 operacional na celula piloto com:

1. 3 destinos ativos (FLBT10TC1/2/3) em 1 turno completo (4h -> 8h).
2. Sem intervencao humana fisica para manter fluxo.
3. Defesa do Risco A (localizacao) com Camadas 0, 1 e 3 ativas.
4. Operacao self-service para itens criticos da matriz (2, 3 e 4).

---

## 2. Gates de aceite

### Gate A (v1 entregue)

1. Taxa de intervencao humana fisica = 0% (binario).
2. Taxa de missao completa >= 95%.
3. MTBI com tendencia crescente entre turnos.
4. Camadas 0, 1 e 3 validadas em simulacao de falha controlada.

### Gate B (v1.1)

1. Camada 2 de auto-recuperacao assistida por landmarks.
2. SLO mais fino por celula/turno.
3. Relatorio de desempenho por rota com comparativo historico.

---

## 3. Squads paralelos

### SQ1 — Localizacao e Resiliencia (Risco A)

Escopo:
1. Camada 0: deteccao `LOCALIZATION_LOST`.
2. Camada 1: auto-recuperacao silenciosa com timeout.
3. Camada 3: escalacao com payload para runbook.

Done:
1. Eventos padronizados emitidos e persistidos.
2. Recovery automatico com limite de tentativas.
3. Escalacao acionavel no desktop.

### SQ2 — Orquestracao e Relatorio v1

Escopo:
1. KPI de missao completa.
2. KPI de intervencao fisica.
3. KPI de MTBI.

Done:
1. Endpoint e painel do relatorio v1 com os 3 numeros.
2. Criterios de contabilizacao auditaveis.

### SQ3 — Self-service Operacional

Escopo:
1. Upload/configuracao de mapa.
2. Vinculo callbutton -> estacao -> direcao.
3. Configuracao/comissionamento de robo por UI.

Done:
1. Fluxo completo por UI sem edicao manual de arquivo.
2. Validacao de entrada e feedback de erro claro.

### SQ4 — Integracoes de chao (OPC UA/IO)

Escopo:
1. Estabilidade de leitura/escrita OPC UA.
2. Idempotencia de acionamentos.
3. Observabilidade de falhas de integracao.

Done:
1. Retentativas seguras e sem duplicar missao.
2. Eventos de falha de integracao com causa rastreavel.

### SQ5 — QA de Confiabilidade + Runbook

Escopo:
1. Teste de falha controlada para localizacao.
2. Soak 4h e 8h.
3. Validacao do runbook com Adilson e Zampin.

Done:
1. Relatorio de validacao por turno.
2. Evidencia de go/no-go por Gate A.

---

## 4. Branch strategy

Padrao:

`squad/v1/<squad>-<tema>-w<semana>`

Branches iniciais:

1. `squad/v1/sq1-localizacao-resiliencia-w1`
2. `squad/v1/sq2-orquestracao-relatorio-w1`
3. `squad/v1/sq3-selfservice-ui-w1`
4. `squad/v1/sq4-opcua-integracao-w1`
5. `squad/v1/sq5-qa-runbook-w1`
6. `release/v1-cat-interno` (branch de integracao)

Regra de merge:

1. PR pequeno por feature.
2. Rebase diario em `release/v1-cat-interno`.
3. Sem merge direto em `main` antes do Gate A.

---

## 5. Sprint plan (3 sprints rapidas)

### Sprint 1 (dias 1-6): Fundacao e contratos

Objetivo:
1. Fechar contratos de evento, estado e dados do relatorio.
2. Entregar self-service minimo utilizavel.

Entregaveis:
1. Eventos de localizacao e schema de incidente.
2. UI de mapa/callbutton/robo com validacoes minimas.
3. Baseline de KPI v1 no dashboard.

Aceite sprint:
1. Deteccao de perda de localizacao em menos de 5s no teste controlado.
2. Configuracao completa da celula pela UI sem edicao manual.

### Sprint 2 (dias 7-12): Resiliencia ativa

Objetivo:
1. Fechar Camada 1.
2. Estabilizar orquestracao com falhas de integracao.

Entregaveis:
1. Recovery automatico com max tentativas e timeout.
2. Escalonamento automatico para operador quando recovery falhar.
3. Soak 4h com coleta de KPI.

Aceite sprint:
1. Missao completa >= 92% em 4h.
2. Nenhum deadlock de state machine em falha induzida.

### Sprint 3 (dias 13-18): Hardening e Gate A

Objetivo:
1. Fechar Camada 3 + runbook validado.
2. Validar turno completo.

Entregaveis:
1. Runbook final homologado.
2. Soak 8h com relatorio final.
3. Dossie de decisao para Marcus.

Aceite sprint:
1. Intervencao fisica = 0%.
2. Missao completa >= 95%.
3. MTBI em tendencia de alta.

---

## 6. Backlog por prioridade

### P0 (bloqueia Gate A)

1. Risco A Camadas 0/1/3.
2. Relatorio v1 com 3 numeros.
3. Self-service dos itens 2/3/4 da matriz.
4. Runbook validado e testado em falha controlada.

### P1 (fortalece v1)

1. Alarmes com contexto de ultima pose e landmark sugerido.
2. Auditoria de alteracao de configuracao por usuario/hora.
3. Painel de saude de integracao OPC UA.

### P2 (v1.1)

1. Camada 2 assistida por landmarks.
2. SLO por estacao/takt.
3. Heuristicas de prevencao (telemetria de recorrencia).

---

## 7. Sequencia de integracao (ordem de merge)

1. SQ3 (contratos de configuracao e self-service base).
2. SQ1 Camada 0 (com feature flag ativa so na celula piloto).
3. SQ4 integracao OPC UA estabilizada.
4. SQ1 Camada 1 + SQ2 KPI v1.
5. SQ1 Camada 3 + SQ5 validacao/runbook.
6. Soak final na `release/v1-cat-interno`.
7. Promocao para `main` apos Gate A.

---

## 8. Checklist pre-promocao para main

1. Gate A aprovado com evidencia.
2. Soak 8h sem intervencao fisica.
3. Fluxo dual-AMR sem regressao funcional.
4. Self-service operacional validado por Adilson/Zampin/Victor.
5. Runbook testado em 1 falha controlada realistica.
6. Plano de rollback pronto e testado.
7. Aprovação final: Edson + Adilson + Zampin + Marcus.

---

## 9. Cadencia de execucao

1. Daily de 15 min por squad.
2. Daily de integracao cross-squad (10 min).
3. Review tecnica dia sim/dia nao na branch `release/v1-cat-interno`.
4. Go/no-go semanal com base em KPI e risco A.

---

## 10. Proximas 48 horas

1. Criar branches de sprint 1 para os 5 squads.
2. Abrir PRs iniciais so com contratos/flags/test harness.
3. Definir owner de cada KPI do relatorio v1.
4. Congelar escopo de Gate A (sem novos itens fora P0).
5. Agendar simulacao de falha controlada para validacao do runbook.
