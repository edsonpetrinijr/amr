# Estudo de Precificação — Software de Orquestração de Frota AMR

> Referência interna. Data: 2026-06-02. Mantido pelo CEO agent.
> Produto: control-plane agnóstico de hardware para frotas de AMRs (Electron+React / Python+Flask), integrando SEER Robokit, OPC UA e RoboShop. Caso piloto: entrega de peças com handshake de 2 botões (supplier→consumer).

## Decisão (TL;DR)

**Modelo HÍBRIDO — taxa de setup única + assinatura recorrente por robô/mês.**

| Fase | Estrutura | BRL | USD |
|------|-----------|-----|-----|
| **Piloto** | Setup único (até 5 robôs, 1 site) | R$12.000–18.000 | $2.500–4.000 |
| **Piloto** | SaaS mensal (trial 3 meses) | R$1.500–2.500/mês | $300–500/mês |
| **Escala** | Por robô/mês (anual) | R$300–450/robô/mês | $200–400/robô/mês |

Setup creditado na conversão para plano anual. Mire na banda **"mid"**.

## Por quê

- **Concorrentes diretos (software puro, agnóstico):** Meili FMS ancora em **€500/mês** (sandbox ≤5 robôs ≈ R$3.000); InOrbit/Formant usam tier grátis + enterprise "sob consulta". Faixa observável: **$100–400/robô/mês**.
- **Ninguém publica preço enterprise** ("contact sales"). Vantagem: publicar um SKU de piloto barato para aquisição e negociar o resto.
- **Valor criado:** frota de 5 robôs gera **R$157k–480k/ano** (≈2 FTEs liberados R$107k + throughput + downtime evitado). Capturar 5–10% = R$650–4.000/mês → corredor de preço.
- **Ancoragem de hardware:** software de frota ≈ **15–25% do capex/ano**. AMR ~$30k → **$375–500/robô/mês**.
- **Vantagem Brasil:** SaaS estrangeiro sofre retenção de 17–30% (IRRF+ISS). Empresa local elimina isso. Nenhum FMS nativo brasileiro identificado → campo aberto.

## Modelos avaliados (ranking para solo founder)

| # | Modelo | Veredito |
|---|--------|----------|
| 🥇 | Setup + por-robô/mês (híbrido) | **Recomendado p/ escala** — caixa imediato + ARR que cresce com a frota |
| 🥈 | Setup + flat por site | **Melhor p/ piloto** — fácil de aprovar, sem contar robôs |
| 🥉 | Só por-robô/mês | Sem caixa upfront; deixa dinheiro na mesa |
| 4 | Licença única + manutenção | Ruim p/ ARR; difícil cobrar manutenção no Brasil |
| 5 | ROI-based (% das economias) | Inviável operacionalmente solo; disputas garantidas |
| 6 | RaaS bundled (HW+SW+serviço) | Exige capital p/ comprar hardware — não agora |
| 7 | Por missão/entrega | Receita imprevisível; difícil instrumentar — só como add-on |

## Faixas de WTP por tamanho de frota (BRL/mês)

| Frota | Conservador | **Alvo (mid)** | Agressivo |
|-------|-------------|----------------|-----------|
| 2–3 robôs | R$1.200–2.000 | R$2.000–3.500 | R$4.000–6.000 |
| 5–10 robôs | R$3.000–5.000 | R$5.000–9.000 | R$10k–18k |
| 10–20 robôs | R$6.000–10k | R$10k–18k | R$20k–40k |

## Estrutura de piloto recomendada

```
Onboarding/Integração (única):   R$12.000–18.000
  Inclui: site survey, config OPC UA dos botões, upload de mapa
  RoboShop, integração SEER Robokit, onboarding de 4 semanas
SaaS de piloto (trial 3 meses):  R$1.500–2.500/mês (até 5 robôs, 1 site)
Conversão pós-piloto:            taxa de setup creditada no Ano 1
  Plano anual: R$24.000–36.000/ano (R$2.000–3.000/mês)
```
- Setup cobre ~40–80h de integração (~R$150/h) e cria comprometimento.
- SaaS de piloto fica abaixo do limite de aprovação discricionária do gerente de planta (POs < R$5k/mês).
- Trial de 3 meses: longo o suficiente p/ medir ROI, curto o suficiente p/ criar urgência.

**Medir no piloto:** entregas/hora, utilização %, horas-FTE em coordenação manual (baseline vs. 30/60/90 dias) → vira case study e justifica preço de escala.

## Trade-off aceito

Taxa de setup cria atrito com pilotos sensíveis a custo. Aceito de propósito: financia runway sem diluição, gera comprometimento do cliente, e o crédito na conversão neutraliza a objeção "já paguei pelo setup".

## Kill criteria

- 2+ pilotos recusarem o setup mesmo com crédito → migrar para "só por-robô, sem setup".
- Integradores exigirem margem que inviabilize venda direta → modelo de licença wholesale via canal.
- WTP real medido < R$1.500/mês → reposicionar como add-on, não plataforma.

## Premissas

- Câmbio R$5,50/USD; €1 ≈ R$6,00 (mid-2025).
- Multiplicador de encargos sociais BR ≈ 1,80× sobre salário bruto.
- Custo de AMR: $25k–60k. Operador BR fully-loaded ≈ R$53,5k/ano.
- Preços enterprise dos concorrentes são estimativas (todos "contact sales"). Ver `COMPETITOR_ANALYSIS.md`.
