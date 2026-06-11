# FluxoFleet — Positioning & Messaging Foundation

> Documento-fonte para landing page, deck, e materiais de vendas. Idioma primário: PT-BR.
> Estágio: pré-receita, primeiro piloto em andamento (planta automotiva). **Não inventar logos, métricas ou clientes.** O piloto é a máquina de prova.

---

## 1. Categoria & Posicionamento (one-line)

> **Nota de afiação (validação competitiva, 2026-06-10):** "Orchestration Engine" é linguagem genérica (Meili/InOrbit/OEMs já usam "orchestration") e os "5 Pilares" são IP do Roboteon/MHI. Por isso: usamos os 5 Pilares como **dispositivo de narrativa/educação**, não como reivindicação de categoria, e ancoramos o pitch na única coisa que só nós demonstramos — **missão multi-robô coreografada com confirmação física e auto-recuperação**. Ver Seção 9.

**Wedge (reivindicação central, ownável):** *O control-plane que coordena **missões inteiras de fluxo de material** — tarefas interdependentes entre vários robôs como uma única missão recuperável — não robôs soltos.*

**Categoria (contexto, não bandeira):** camada de software (control-plane) de orquestração para frotas de AMRs industriais, que roda **por cima** dos robôs, independente do fabricante. Os **5 Pilares de Software** (Integração, Sincronização, Orquestração, Otimização, Simulação) do MHI/Roboteon são nosso mapa de produto e ferramenta de honestidade (vivo vs. roadmap vs. norte) — não nossa categoria proprietária.

**Statement de posicionamento:**

> Para **gestores de planta e engenharia de processo** que precisam de **entrega de peças confiável entre estações sem parar a linha**, o **FluxoFleet** é um **motor de orquestração de AMRs** que coordena a frota com **confirmação física e recuperação automática de falhas**. Diferente do software embarcado do fabricante ou de FMS estrangeiros, somos **agnósticos de hardware, feitos para a realidade do chão de fábrica brasileiro**, e orquestramos **múltiplos AMRs em paralelo** numa mesma missão.

**English one-liner:**
> FluxoFleet is the hardware-agnostic orchestration engine for industrial AMR fleets — coordinating multiple robots with physical handshake confirmation and automatic fault recovery, so the line never stops.

---

## 2. Hierarquia de Mensagem

**Mensagem central (headline):**
> **Orquestre AMRs com confirmação física e recuperação automática — sem parar a linha.**

**Subhead:**
> FluxoFleet é o control-plane da sua frota AMR: roda sobre os robôs que você já tem (SEER), dispara entregas por botão físico, coordena múltiplos robôs em paralelo e recupera falhas sozinho.

**3 pilares de sustentação** (mapeados aos 5 pilares MHI):

| Pilar de mensagem | Pilar MHI | O que diz | Prova (piloto) |
|---|---|---|---|
| **1. Conecta no que você já tem** | Integração | Sem trocar robôs ou refazer o chão. Entra por cima. | Integração viva com SEER Robokit (TCP), botões físicos via OPC UA, mapas `.smap`/RoboShop, telemetria em tempo real. |
| **2. Confirma antes de mover** | Sincronização | Nada despacha sem o destino confirmar. Handshake físico de 2 botões. | Pickup único (BTLOG1) → 3 pontos-de-uso distintos (FLBT10TC1/2/3); despacho só após confirmação física. |
| **3. Coordena a frota, não só um robô** | Orquestração | Múltiplos AMRs numa mesma missão, em paralelo, com fila, requeue e alarmes. | **Despacho dual-AMR:** um robô leva o rack cheio, outro busca o vazio em paralelo. Recuperação automática com assistência de relocalização. |

*Otimização e Simulação entram como visão (norte) — ver Seção 3.*

---

## 3. A Narrativa dos 5 Pilares

A história de produto que conta de onde viemos e para onde vamos. **Honesta sobre o que está vivo vs. roadmap.**

| Pilar | Status | O que significa no FluxoFleet |
|---|---|---|
| **1. Integração** | ✅ **Vivo** | Conexão com SEER (TCP), OPC UA (botões físicos), mapas RoboShop. Agnóstico de hardware por design. |
| **2. Sincronização** | ✅ **Vivo** | Handshake físico de 2 etapas; despacha só quando origem e destino confirmam. Estados sincronizados em tempo real. |
| **3. Orquestração** | ✅ **Vivo — nosso núcleo** | Despacho dual-AMR coordenado, fila, requeue automático, alarmes, stop-all por software, jog manual. **É aqui que ganhamos.** |
| **4. Otimização** | 🟡 **Roadmap** | Roteamento e sequenciamento por dados de throughput/gargalo. Hoje coletamos o histórico (tempo por rota, taxa de falha) que alimenta isso. |
| **5. Simulação / Digital Twin** | 🔭 **Norte (visão)** | Gêmeo digital do fluxo de materiais: simular layouts, dimensionar frota e validar mudanças antes de tocar a planta. Nossa estrela-guia de longo prazo. |

**Como contar:** "Os 5 pilares descrevem o software completo de execução robótica. O FluxoFleet já é forte nos três pilares de fundação — Integração, Sincronização e Orquestração — que são o que faz a linha rodar hoje. O histórico que coletamos é a base da Otimização. E o destino é o Digital Twin: simular antes de mover um único robô."

---

## 4. Audiência & Mensagem por Persona

| Persona | Dor central | Mensagem-chave |
|---|---|---|
| **Gestor de planta** (econômico/operacional) | Parada de linha = dinheiro perdido | "Menos paradas por falha de entrega. O FluxoFleet recupera sozinho e mantém a linha andando." |
| **Engenheiro de processo/industrial** | Precisa de previsibilidade e dados para melhorar o fluxo | "Cada entrega vira dado: tempo por rota, gargalo por estação e turno. Decida com histórico, não com achismo." |
| **Líder de manutenção/operação** | Falhas viram improviso manual | "Fila, reenvio automático, alarmes e stop-all. Quando algo falha, você tem controle e visibilidade — não pânico." |
| **Comprador econômico** (decisor/financeiro) | Risco de lock-in e ROI incerto | "Roda sobre os robôs que você já tem — sem trocar frota. Setup previsível + assinatura por robô. Comece com um piloto." |

---

## 5. Diferenciação

**vs. (a) software embarcado do fabricante do robô (MiR, OTTO, etc.)**
- **Agnóstico de hardware:** orquestramos a frota independente da marca — sem lock-in num único OEM.
- **Orquestração multi-robô real:** o software do OEM gerencia *os robôs dele*; nós coordenamos uma missão entre vários robôs (dual-AMR) com handshake físico.

**vs. (b) FMS estrangeiros (Meili, InOrbit, Formant)**
- **Brasil-first:** suporte, implantação e contrato na realidade local — fuso, idioma, faturamento em R$, presença no piloto.
- **Confiabilidade por handshake físico:** confirmação de 2 botões reduz despacho indevido — pensado para o chão de fábrica, não só dashboard remoto.
- **Foco em execução, não telemetria:** alguns players estrangeiros são observabilidade/teleoperação; nós orquestramos a tarefa de ponta a ponta.

**Pílula de diferenciação (uma linha):**
> Agnóstico de hardware, Brasil-first, com handshake físico e orquestração dual-AMR — o control-plane que entra por cima do que você já tem.

---

## 6. Boilerplate & Elevator Pitches

**1 frase (PT-BR):**
> FluxoFleet é o motor de orquestração que coordena frotas de AMRs industriais com confirmação física e recuperação automática de falhas — sem parar a linha.

**1 frase (EN):**
> FluxoFleet is the hardware-agnostic orchestration engine for industrial AMR fleets — physical handshake, automatic fault recovery, no line stoppage.

**1 parágrafo (boilerplate PT-BR):**
> FluxoFleet é uma camada de software de orquestração (control-plane) para frotas de robôs móveis autônomos (AMRs) em fábricas. Roda por cima dos robôs que a planta já tem — integrando-se a SEER (TCP), botões físicos via OPC UA e mapas RoboShop — para coordenar a entrega de peças entre estações com confirmação física de 2 etapas, despacho de múltiplos robôs em paralelo e recuperação automática de falhas. Agnóstico de hardware e feito para a realidade industrial brasileira, o FluxoFleet transforma cada entrega em dado rastreável, dando à operação previsibilidade sem trocar a frota. Atualmente em piloto numa planta do setor automotivo.

**Pitch verbal (~30s):**
> "Robô de fábrica é fácil de comprar e difícil de orquestrar. Quando a entrega falha, a linha para e vira operação manual. O FluxoFleet é a camada de software que roda por cima dos robôs que você já tem: a chamada vem de um botão físico, nada despacha sem o destino confirmar, e a gente coordena vários robôs na mesma missão — um leva o rack cheio, outro busca o vazio. Se algo falha, recupera sozinho. Estamos rodando o primeiro piloto numa planta automotiva. É hardware-agnóstico, é Brasil-first, e começa com um piloto curto."

---

## 7. Prova & Credibilidade

**O que podemos afirmar com verdade hoje (estágio piloto):**
- ✅ Integrações reais e funcionais: SEER (TCP), OPC UA, mapas `.smap`/RoboShop, telemetria ao vivo.
- ✅ Caso de uso real em piloto: entrega de sub-montagem de conversor de torque — 3 part numbers, pickup único → 3 pontos-de-uso distintos.
- ✅ Diferencial técnico demonstrável: despacho **dual-AMR** em paralelo + handshake físico de 2 botões.
- ✅ Controles de segurança e operação: stop-all por software, jog manual, fila/requeue/alarmes, assistência de relocalização.

**Como falar de resultados sem inventar métrica:**
- Use **claims direcionais**, não números fabricados: "menos paradas por falha de entrega", "menos caminhada de operador", "mais previsibilidade".
- Posicione o **piloto como a máquina de prova**: "Estamos medindo tempo por rota, taxa de falha e gargalos no piloto atual — números reais virão do cliente real."
- **Nunca** prometa % de uptime, ROI em meses, ou economia em R$ até ter dado do piloto.
- Quando o piloto fechar: capturar **1 estudo de caso + 1 referência nomeada** (com permissão) — é o ativo de credibilidade nº 1.

**Próximos ativos de prova a coletar:**
1. Métricas baseline vs. pós-FluxoFleet do piloto (com consentimento de divulgação).
2. Citação/depoimento do gestor de planta do piloto.
3. Vídeo curto do dual-AMR em operação real.
4. Logo do cliente (somente com autorização formal).

---

## 8. Punch-list: Landing Page (`web/LandingPage.tsx`)

Para ler como empresa, não como PoC:

**Tom & categoria**
- [ ] Adicionar **kicker de categoria** acima do H1: "Orchestration Engine para AMRs industriais" — ancorar na categoria, não só no benefício.
- [ ] Subhead do hero: mencionar **dual-AMR / multi-robô** explicitamente (é o diferencial e não aparece no hero atual).

**Seções faltando**
- [ ] **Os 5 Pilares** — seção nova com a tabela vivo/roadmap/norte (Seção 3). Mostra visão de categoria + honestidade técnica.
- [ ] **Diferenciação** explícita: bloco "Por que não o software do fabricante" e "Por que não FMS estrangeiro" (Seção 5). Hoje os diferenciais estão genéricos.
- [ ] **Prova / piloto** — uma faixa "Em piloto numa planta automotiva" com o caso de uso real (torque-converter, 3 pontos-de-uso). Concreto vence adjetivo.
- [ ] **Personas/ROI** — micro-seção "Para quem" com a mensagem por persona (Seção 4).

**Prova social (sem inventar)**
- [ ] **Não** colocar logos falsos. Usar placeholder honesto: "Primeiro piloto em andamento — referências em breve" em vez de carrossel de logos vazio.
- [ ] Substituir claims vagos por **claims direcionais rotulados** como expectativa do piloto, não fato consumado.

**Consistência de voz**
- [ ] Padronizar para tom técnico/plano: cortar qualquer adjetivo de hype; toda afirmação ou tem prova ou é rotulada como visão/roadmap.
- [ ] Glossário rápido (tooltip ou rodapé): AMR, control-plane, handshake — comprador industrial valoriza clareza sobre jargão.

## 9. Afiação competitiva — o que mudar (2026-06-10)

Síntese do stress-test do `competitive-analyst` contra Meili / InOrbit / Formant / OEMs. Três correções de alto impacto:

**(1) Demover "Orchestration Engine" de categoria → para dispositivo de narrativa.**
"Orchestration" é a palavra mais saturada do setor e os 5 Pilares são IP do Roboteon. Quem buscar o termo cai no Roboteon, não em nós. Mantemos os 5 Pilares como ferramenta de educação/honestidade; a reivindicação central passa a ser o **wedge** (Seção 1).

**(2) Reposicionar dual-AMR: de "coordena vários robôs" (table stakes) → "coreografa tarefas interdependentes numa única missão" (o wedge real).**
Todo FMS sério coordena múltiplos robôs — dizer isso nos iguala a todos. O diferencial verdadeiro é a **semântica de workflow**: uma missão que acopla dois robôs a tarefas complementares e dependentes (cheio sai + vazio volta, em paralelo, com gate de handshake físico). A maioria dos FMS despacha tarefas *independentes* e resolve conflito por regra de tráfego — não modelam "estas duas tarefas são uma troca coreografada".
> **A validar:** confirmar no sandbox do Meili que eles não suportam missões pareadas/dependentes antes de gravar este claim num slide de venda. (Confiança média.)

**(3) Brasil-first: tornar estrutural, não sentimental.**
"Falamos português" não é defensável (um FMS estrangeiro localiza em um trimestre). O que é sticky: **economia local** (sem IRRF/ISS sobre SaaS importado — *confirmar com finance antes de escrever*), **presença física no piloto**, e **relações de integração/SI no chão** que um estrangeiro não absorve lucrativamente no nosso tamanho de frota.

**Handshake físico — moldar como postura de confiabilidade, não como "um botão".**
Qualquer concorrente faz um botão OPC UA num sprint. O defensável é o **gate de confirmação física**: nada despacha sem origem E destino confirmarem — sem despacho fantasma, operador no loop, auto-recuperação quando falha. Frame: *"feito para o chão, não para o dashboard."*

**Maior vulnerabilidade (e antídoto).**
Ataque do concorrente: *"é um piloto único pré-receita que faz 3 de 5 pilares e admite que Otimização/Simulação são roadmap; nós já fazemos tudo em dezenas de sites."* Nossa própria grade de maturidade entrega esse enquadramento.
→ **Antídoto:** em deal competitivo, **não liderar pela grade dos 5 Pilares**. Liderar pelo resultado de missão (linha não para, recupera sozinha — provado numa planta automotiva ao vivo). Transformar maturidade em foco: *"Otimização/Simulação é onde plataformas genéricas prometem slideware; nós entregamos os três pilares que mantêm sua linha rodando hoje, e o dado que coletamos agora é o que torna a otimização real."* E virar a amplitude deles em lock-in (vêm amarrados ao hardware/nuvem deles; nós rodamos no que você já tem).

**Recomendação nº 1 (maior impacto):** re-ancorar todo o pitch da categoria genérica para a **única capacidade que só nós demonstramos** — missões multi-robô interdependentes com confirmação física e auto-recuperação. Tudo o mais (agnóstico de hardware, Brasil-first, handshake) vira *razão-para-acreditar* dessa única reivindicação, em vez de uma lista de cinco diferenciais co-iguais (uma lista de cinco lê como "nenhum forte").
