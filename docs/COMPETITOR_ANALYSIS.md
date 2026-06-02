# Análise de Concorrentes — Fleet-Orchestration Software para AMRs

> Referência interna. Data: 2026-06-02. Foco: precificação e modelos de software de gestão/orquestração de frota (FMS). Mantido pelo CEO agent.
>
> Legenda de qualidade da fonte: 🟢 fonte direta do fornecedor | 🟡 triangulado (arquivo/imprensa) | 🔴 estimativa de mercado.

## Posicionamento — quem é comparável a nós

Nosso produto é **software puro, agnóstico de hardware, multi-robô**. Comparáveis diretos:
**Meili FMS, InOrbit (Standard) e o Formant histórico.** Os demais ou são bundled com hardware (MiR, OTTO, SEER) ou são RaaS (Locus, 6 River).

## Tabela mestre — precificação dos concorrentes

| Fornecedor / Produto | Categoria | Modelo | Preço público | Software puro? | Notas |
|---|---|---|---|---|---|
| **Meili Robots — Meili FMS** | FMS agnóstico | SaaS por tier + Code License | **€500/mês** sandbox (≤5 robôs, 4–12 meses) 🟢 | ✅ | Produção: sob consulta. Code License = taxa fixa única p/ SIs/OEMs. **Nosso comp mais direto.** |
| **InOrbit** | Robot ops cloud | SaaS por tier (Free/Standard/Enterprise) | **Free: 1 robô, 72h** 🟢; pagos sob consulta | ✅ | Tier grátis construiu o ecossistema (vendors integram SDK de graça). Standard ~$100–300/robô/mês 🔴. |
| **Formant** | Robot ops / agora AI incident mgmt | Platform fee + por device | **Free tier** 🟢; pagos sob consulta | ✅ (era) | Pivotou em 2024–25 p/ semicondutores. Menos concorrência no nosso mercado agora. |
| **MiR Fleet (Mobile Industrial Robots / Teradyne)** | FMS bundled OEM | Licença perpétua + manutenção anual | Sob consulta | ❌ Vendido com robôs MiR | Manutenção estimada $1.000–3.000/robô/ano 🔴. On-prem. |
| **OTTO Fleet Manager (OTTO Motors / Rockwell)** | FMS bundled OEM | RaaS ou capex | Sob consulta | ❌ Vendido com hardware OTTO | Sistema de 5 robôs ~$500k–1M+ capex 🔴. |
| **SYNAOS Intralogistics Platform** | FMS enterprise agnóstico | SaaS enterprise / contrato anual | Sob consulta | ✅ | 50+ installs, base VW/ZF/Schaeffler. Estimativa €2k–10k+/mês 🔴. **Teto enterprise.** |
| **BlueBotics ANT Server** | Navegação OEM + FMS | Licença perpétua por instalação | Sob consulta | ❌ Requer hardware ANT | Tiers Single Vehicle / Fleet. Estimativa €5k–20k perpétua + manutenção 🔴. |
| **Locus Robotics — LocusONE** | AMR de armazém + orquestração | RaaS (HW+SW+serviço) | **~$0,10–0,30/pick** + mínimo mensal 🔴 | ❌ | Software não vendido à parte. Específico de armazém. Reestruturou em 2023. |
| **6 River Systems (agora Ocado OMRS)** | AMR de armazém + software | RaaS | Sob consulta | ❌ | Adquirido pela Ocado. ~$1.500–3.500/robô/mês bundled 🔴. |
| **Open-RMF (Open Source Robotics Alliance)** | Middleware multi-frota open source | Open-core (Apache 2.0) | **Grátis** 🟢 | ✅ | Integração via SI: $50k–300k 🔴. Ameaça só se cliente tem time ROS2 forte. |
| **WAKU Robotics — WAKU Care** | Manutenção/CMMS de AMR | SaaS modular | CI custom a partir de **€12.000/ano** 🟢 | ✅ (manutenção) | Não é orquestrador (não faz dispatch/tráfego). |
| **SEER Robotics — RoboShop / Robokit** | OEM chinês + FMS proprietário | Bundled, licença enterprise | Sob consulta | ❌ Atrelado a hardware SEER | RoboShop = UI de frota deles. Robokit = a API que construímos por cima. |
| **Fox Robotics / Third Wave / ANYbotics** | Hardware-led | Bundle / RaaS | Sob consulta | ❌ | Software não vendido standalone. Fora do nosso escopo direto. |
| **Freedom Robotics** | Observabilidade de frota | SaaS por tier | — | ✅ (era) | **Aparentemente extinto em 2025** (site fora do ar). |
| **Roboligent** | — | — | — | — | **Pivotou p/ robôs humanoides.** Remover do comp set. |

## Modelos de precificação observados no mercado

| # | Modelo | Quem usa | Nota |
|---|--------|----------|------|
| 1 | Por robô/mês (SaaS) | InOrbit, Formant (histórico) | Mais comum em plataformas cloud agnósticas. Descontos de volume >10 robôs. |
| 2 | Flat por site/mês | SYNAOS, enterprise | "Site" = 1 instalação. Negociado por unidade. |
| 3 | Taxa fixa de plataforma (Code License / perpétua) | Meili Code License, BlueBotics | Única ou anual; p/ SIs e operadores que querem self-host. |
| 4 | Sandbox/trial pago | Meili (€500/mês ≤5 robôs) | Reduz risco dos dois lados. Boa alavanca de GTM. |
| 5 | RaaS bundle (HW+SW+serviço) | Locus, OTTO, 6 River | Custo de SW opaco, embutido no fee por robô/pick. |
| 6 | Usage/missão | Locus (per-pick) | Alinha receita ao ROI; risco de fluxo de caixa. |
| 7 | Perpétua bundled + manutenção | MiR Fleet, OTTO | Manutenção ~10–15% do valor da licença/ano. |
| 8 | SaaS em tiers (free→enterprise) | InOrbit, Formant, WAKU | Free tier gera leads + lock-in de ecossistema. |
| 9 | Open-core / freemium | Open-RMF | Monetiza só via serviços/suporte. |
| 10 | Serviços profissionais + integração | Todos enterprise / SIs | Projeto de integração: $20k–150k conforme complexidade. |

## Faixas de preço (síntese)

| Segmento | Frota | Custo SW esperado (USD/mês) |
|---|---|---|
| Piloto / PoC | 1–5 robôs | $300–1.500/mês |
| Pequeno | 5–15 robôs | $1.000–4.000/mês (~$100–300/robô) |
| Mid-market | 15–50 robôs | $3.000–10.000/mês |
| Enterprise / multi-site | 50–200+ robôs | $10.000–50.000+/mês |
| Integração (única) | qualquer | $10.000–80.000 |

**Benchmark por robô:** ~$100–400/robô/mês p/ FMS agnóstico bem-feito (5–30 robôs). Abaixo de $100 = percebido como commodity; acima de $500 = exige ROI muito forte ou hardware bundled.

## Observações estratégicas

1. **Ninguém publica preço** exceto Meili (€500 sandbox) e InOrbit (free tier). Não brigue contra essa norma no enterprise; brigue no piloto/SMB.
2. **Meili FMS é o comp mais direto** (VDA5050, ROS1/2, traffic control). Sandbox €500/5 robôs = nossa âncora de preço de piloto.
3. **InOrbit free tier construiu ecossistema** — considerar free tier específico p/ SEER Robokit.
4. **Formant saiu do mercado** (foco em fabs de semicondutores) → menos concorrência.
5. **Open-RMF** só ameaça com cliente que tem time ROS2 forte — raro na indústria brasileira.
6. **SYNAOS e BlueBotics = teto enterprise** — exigem VDA5050 + OPC UA + canal de SI.
7. **Taxa de integração é real e subcobrada por startups** — $20–60k p/ integração de chão de fábrica é normal. Não dê de graça.
8. **Nenhum FMS nativo brasileiro identificado** → oportunidade green-field; vantagem fiscal local vs. concorrentes estrangeiros (sem IRRF/ISS sobre SaaS importado).

## Lacunas e incertezas

- Sem valores em dólar/euro confirmados p/ InOrbit pago, Formant pago, MiR, OTTO, SYNAOS, BlueBotics (todos "contact sales") — figuras são estimativas.
- Freedom Robotics aparentemente extinto; Roboligent pivotou (remover do comp set).
- SEER RoboShop/Robokit: sistema fechado, sem preço público.
- Locus reestruturou (2023); 6 River agora dentro do Ocado Group.

---

*Fontes: meilirobots.com; web.archive.org (formant.io/pricing, inorbit.ai/pricing 2022–2024); bluebotics.com; synaos.com; ottomotors.com; mobile-industrial-robots.com; open-rmf.org; waku-robotics.com; roboticsandautomationnews.com.*
