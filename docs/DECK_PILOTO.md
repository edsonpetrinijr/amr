# FluxoFleet — Deck do Piloto
### Apresentação para Marcus · Planta automotiva (CAT) · Estágio piloto
> Idioma: PT-BR. Sem métricas fabricadas, sem logos falsos. O piloto é a máquina de prova.

---

## Slide 1 — Abertura
**Mensagem:** Robô de fábrica é fácil de comprar e difícil de orquestrar.
- Título de capa: *FluxoFleet — orquestração de AMRs, sem parar a linha.*
- Subtítulo: "O que mostramos hoje está rodando no piloto desta planta."
- Cue: logo FluxoFleet + nome do piloto (torque-converter). Sem stock art.

---

## Slide 2 — O problema no chão de fábrica
**Mensagem:** Quando a entrega de peça falha, a linha para e vira improviso manual.
- Entrega entre estações depende de timing — atrasou, a estação fica sem peça.
- Robô parado por falha sem recuperação = operador empurrando rack na mão.
- Cada parada é dinheiro, e a causa raiz some sem registro.
- Cue: foto/diagrama da célula real — pickup BTLOG1 alimentando FLBT10TC1/2/3.

---

## Slide 3 — Por que o problema persiste
**Mensagem:** A planta tem robôs, mas não tem quem coordene a frota.
- Software do OEM gerencia *os robôs dele*, um a um — não a missão.
- FMS estrangeiro: caro, remoto, fuso e idioma errados, sem presença no chão.
- Resultado: ilhas de automação que não conversam e falham em silêncio.
- Cue: ícone "control-plane faltando" entre robôs e linha.

---

## Slide 4 — A solução: missões multi-robô coordenadas
**Mensagem:** O FluxoFleet é a camada de software que coordena missões inteiras de fluxo de material — não robôs soltos — por cima dos robôs que você já tem.
- Control-plane agnóstico de hardware — entra sem trocar frota nem refazer o chão.
- A chamada vem de botão físico; nada despacha sem o destino confirmar.
- Coordena tarefas interdependentes na mesma missão e recupera falhas sozinho.
- Cue: diagrama de camadas — robôs (SEER) → FluxoFleet → operação.

---

## Slide 5 — Os 5 Pilares (narrativa — vivo / roadmap / norte)
**Mensagem:** Já somos fortes nos três pilares que mantêm a linha rodando; o resto é caminho declarado.
> Usar como educação/honestidade — não liderar um pitch competitivo por aqui.
- ✅ **Integração** — SEER (TCP), OPC UA (botões), mapas RoboShop. *Vivo.*
- ✅ **Sincronização** — handshake físico de 2 etapas. *Vivo.*
- ✅ **Orquestração** — despacho dual-AMR, fila, requeue, alarmes. *Vivo — nosso núcleo.*
- 🟡 **Otimização** — roteamento por dados. *Roadmap (já coletamos o histórico).*
- 🔭 **Simulação / Digital Twin** — simular antes de mover um robô. *Norte / visão.*
- Cue: tabela com selos de status. Marcus precisa ver a honra da fronteira vivo↔visão.

---

## Slide 6 — O caso de uso do piloto
**Mensagem:** Sub-montagem de conversor de torque — real, em operação aqui.
- 3 part numbers, pickup único (BTLOG1) → 3 pontos-de-uso distintos (FLBT10TC1/2/3).
- Disparo por botão físico na estação que precisa da peça.
- Telemetria ao vivo de cada missão e cada robô.
- Cue: mapa da célula com a rota real destacada.

---

## Slide 7 — DEMO AO VIVO (centro do deck)
**Mensagem:** Veja a missão coreografada — cheio vai, vazio volta — com handshake físico, agora.
**Roteiro do que mostrar na tela, em ordem:**
1. **Chamada:** operador aperta o botão físico em FLBT10TC1 → missão aparece na fila do dashboard.
2. **Handshake:** confirmação de 2 botões (origem + destino) antes de qualquer movimento — mostrar o estado mudar para "confirmado".
3. **Missão dual-AMR:** AMR-A pega o rack cheio no BTLOG1; **em paralelo e dependente** AMR-B vai buscar o rack vazio. Apontar que é UMA missão com duas tarefas acopladas, não dois jobs soltos.
4. **Telemetria:** posição, estado e tempo de rota em tempo real na tela.
5. **Recuperação de falha:** (se seguro) induzir/mostrar um fault → requeue automático + assistência de relocalização, sem operador empurrando rack.
6. **Controle:** demonstrar stop-all por software e jog manual.
- Cue: tela cheia do dashboard ao vivo. Plano B: vídeo curto gravado da mesma célula caso a rede falhe.

---

## Slide 8 — O que torna isto difícil (e nosso)
**Mensagem:** Missão única com tarefas interdependentes + confirmação física é o diferencial real — não "coordenar vários robôs" (isso todo FMS faz).
- Coreografar duas tarefas dependentes numa missão (cheio vai, vazio volta) — não dois jobs independentes resolvidos por regra de tráfego.
- Despacho só passa quando origem E destino confirmam fisicamente — sem despacho fantasma.
- Recuperação automática com relocalização: falha vira evento gerenciado, não pânico.
- Cue: antes/depois — "improviso manual" vs. "missão orquestrada".

---

## Slide 9 — Diferenciação
**Mensagem:** Missão multi-robô coreografada + agnóstico de hardware + Brasil-first (estrutural).
- **vs. software do OEM (MiR, OTTO):** sem lock-in; coordenamos a missão entre marcas, não só os robôs de um fabricante.
- **vs. FMS estrangeiro (Meili, InOrbit, Formant):** economia local (sem drag de imposto sobre SaaS importado), contrato em R$, presença física no piloto, suporte de integração no chão — coisas que um FMS estrangeiro não cobre lucrativamente no seu tamanho de frota.
- **Coordenação:** tarefas interdependentes numa missão, com handshake físico — não só telemetria/teleoperação.
- Cue: tabela de 3 colunas — OEM / FMS estrangeiro / FluxoFleet.

---

## Slide 10 — O que medimos no piloto
**Mensagem:** Cada entrega vira dado — números reais virão deste piloto, não de marketing.
- **Tempo por rota** — baseline vs. orquestrado.
- **Taxa de falha de entrega** e tempo de recuperação.
- **Gargalos** por estação e por turno.
- Claim direcional, honesto: "Esperamos menos paradas por falha e menos caminhada de operador — vamos medir aqui." Sem % nem R$ inventados.
- Cue: painel de métricas com campos preenchidos como "em coleta".

---

## Slide 11 — Como o piloto avança
**Mensagem:** Da célula única à frota — caminho incremental e de baixo risco.
- Hoje: 3 part numbers, 1 célula, dual-AMR + handshake vivos.
- Próximo: mais part numbers / próxima célula sobre a mesma base.
- Dados do piloto alimentam o pilar de Otimização (roteamento por throughput).
- Cue: timeline simples (agora → expansão → otimização → digital twin).

---

## Slide 12 — O pedido (next step)
**Mensagem:** Marcus, vamos formalizar o sucesso e definir a próxima célula.
- **1. Critérios de sucesso do piloto** acordados por escrito (tempo de rota, taxa de falha alvo, janela de avaliação).
- **2. Expandir o escopo:** de 3 para N part numbers / próxima célula de sub-montagem.
- **3. Permissão de prova:** capturar métricas baseline, 1 depoimento e vídeo do dual-AMR (com autorização) — para sustentar o caso interno.
- Cue: caixa de decisão com as 3 opções; um dono e uma data ao lado de cada.

---

## Slide 13 — Quem somos (boilerplate)
**Mensagem:** O control-plane da sua frota AMR.
- "FluxoFleet é uma camada de software de orquestração (control-plane) para frotas de AMRs em fábricas — integra SEER, OPC UA e mapas RoboShop, coordena entrega entre estações com handshake físico, despacho multi-robô em paralelo e recuperação automática de falhas. Agnóstico de hardware e Brasil-first. Atualmente em piloto numa planta do setor automotivo."
- Cue: contato + nome do champion (Marcus) como ponto de continuidade.
