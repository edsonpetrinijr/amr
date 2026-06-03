import React from "react"
import {
  ArrowRight, CheckCircle2, ShieldCheck, Workflow, Plug, History,
  AlertTriangle, OctagonX, Hand, MapPin, Radio, MonitorPlay,
  Image as ImageIcon, Film,
} from "lucide-react"
import { BRAND, CONTACT_EMAIL, WHATSAPP_URL, PILOT_MAILTO } from "./brand"

// ─────────────────────────────────────────────────────────────────────────────
// Marketing landing page (v1) — standalone public route, no operator chrome.
// Palette mirrors the operator app (GitHub-dark): bg #0d1117, panels #161b22,
// borders #30363d, text #c9d1d9 / headings #e6edf3 / muted #8b949e, accent
// blue #58a6ff, primary green #238636. All brand copy reads from brand.ts.
// ─────────────────────────────────────────────────────────────────────────────

const NAV = [
  { label: "Como funciona", href: "#como-funciona" },
  { label: "Integrações", href: "#integracoes" },
  { label: "Segurança", href: "#seguranca" },
  { label: "Piloto", href: "#piloto" },
  { label: "FAQ", href: "#faq" },
]

/** Primary CTA — opens a pre-filled email. Repeated 2–3x down the page. */
function CtaButton({
  label,
  className = "",
}: {
  label: string
  className?: string
}) {
  return (
    <a
      href={PILOT_MAILTO}
      className={
        "inline-flex items-center justify-center gap-2 rounded-md bg-[#238636] px-5 py-3 " +
        "text-sm font-semibold text-white transition-colors hover:bg-[#2ea043] " +
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#2ea043] " +
        className
      }
    >
      {label}
      <ArrowRight className="h-4 w-4" />
    </a>
  )
}

function Section({
  id,
  children,
  className = "",
}: {
  id?: string
  children: React.ReactNode
  className?: string
}) {
  return (
    <section id={id} className={"mx-auto w-full max-w-6xl px-5 py-16 sm:px-8 md:py-24 " + className}>
      {children}
    </section>
  )
}

function SectionTitle({ kicker, title, sub }: { kicker?: string; title: string; sub?: string }) {
  return (
    <div className="mb-10 max-w-3xl">
      {kicker && (
        <p className="mb-2 text-sm font-semibold uppercase tracking-wide text-[#58a6ff]">{kicker}</p>
      )}
      <h2 className="text-2xl font-semibold leading-tight text-[#e6edf3] md:text-3xl">{title}</h2>
      {sub && <p className="mt-3 text-base text-[#8b949e] md:text-lg">{sub}</p>}
    </div>
  )
}

function BulletList({ items }: { items: string[] }) {
  return (
    <ul className="space-y-3">
      {items.map((it) => (
        <li key={it} className="flex items-start gap-3 text-[#c9d1d9]">
          <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-[#3fb950]" />
          <span>{it}</span>
        </li>
      ))}
    </ul>
  )
}

// ── Header ───────────────────────────────────────────────────────────────────
function Header() {
  return (
    <header className="sticky top-0 z-50 border-b border-[#30363d] bg-[#0d1117]/90 backdrop-blur">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between px-5 py-3 sm:px-8">
        <a href="#top" className="text-lg font-semibold tracking-tight text-[#e6edf3]">
          {BRAND}
        </a>
        <nav className="hidden items-center gap-6 md:flex">
          {NAV.map((n) => (
            <a
              key={n.href}
              href={n.href}
              className="text-sm text-[#8b949e] transition-colors hover:text-[#c9d1d9]"
            >
              {n.label}
            </a>
          ))}
        </nav>
        <CtaButton label="Solicitar piloto" className="px-4 py-2" />
      </div>
    </header>
  )
}

// ── Hero ─────────────────────────────────────────────────────────────────────
function Hero() {
  return (
    <Section className="pt-16 md:pt-20">
      <div className="max-w-3xl">
        <h1 className="text-3xl font-bold leading-tight text-[#e6edf3] sm:text-4xl md:text-5xl">
          Orquestre AMRs com confirmação física e recuperação automática — sem parar a linha.
        </h1>
        <p className="mt-5 text-lg text-[#8b949e]">
          {BRAND} é a camada de orquestração sobre seus robôs (SEER) para entrega de peças entre
          estações com handshake de 2 etapas, telemetria ao vivo e controles de segurança.
        </p>

        <div className="mt-8 grid gap-3 sm:grid-cols-3">
          {[
            "Menos paradas por falha de entrega",
            "Menos caminhada de operador",
            "Mais previsibilidade (tempos, histórico, gargalos)",
          ].map((b) => (
            <div
              key={b}
              className="flex items-start gap-2 rounded-lg border border-[#30363d] bg-[#161b22] p-4 text-sm text-[#c9d1d9]"
            >
              <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-[#3fb950]" />
              {b}
            </div>
          ))}
        </div>

        <div className="mt-8 flex flex-wrap items-center gap-4">
          <CtaButton label="Solicitar piloto (20 min)" />
          <a
            href="#como-funciona"
            className="inline-flex items-center gap-2 text-sm font-medium text-[#58a6ff] hover:underline"
          >
            Ver como funciona <ArrowRight className="h-4 w-4" />
          </a>
        </div>

        <p className="mt-4 text-xs text-[#6e7681]">
          Integra com SEER (TCP) · OPC UA (botões físicos) · mapas .smap · telemetria em tempo real
        </p>
      </div>
    </Section>
  )
}

// ── Problem ──────────────────────────────────────────────────────────────────
function Problem() {
  return (
    <div className="border-y border-[#30363d] bg-[#0b0f14]">
      <Section>
        <SectionTitle
          kicker="O problema"
          title="Quando o robô vira 'mais um sistema', a linha paga a conta."
        />
        <div className="grid gap-4 md:grid-cols-2">
          {[
            "Chamadas sem confirmação geram viagem errada e retrabalho",
            "Falhas sem fila, sem reenvio e sem rastreio claro",
            "Em plantas grandes, a relocalização falha e a operação vira manual",
            "Segurança operacional vira improviso",
          ].map((p) => (
            <div
              key={p}
              className="flex items-start gap-3 rounded-lg border border-[#30363d] bg-[#161b22] p-5 text-[#c9d1d9]"
            >
              <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-[#d29922]" />
              <span>{p}</span>
            </div>
          ))}
        </div>
      </Section>
    </div>
  )
}

// ── Solution ─────────────────────────────────────────────────────────────────
function Solution() {
  return (
    <Section>
      <SectionTitle
        kicker="A solução"
        title="FluxoFleet é o control-plane da sua frota AMR."
        sub="Sem trocar seus robôs, você ganha entrega entre estações com regras, confirmação e recuperação."
      />
      <div className="rounded-xl border border-[#30363d] bg-[#161b22] p-6 md:p-8">
        <BulletList
          items={[
            "Chamadas por botões físicos (OPC UA)",
            "Confirmação em 2 etapas antes do despacho",
            "Fila, requeue automático e alarmes",
            "Stop-all por software, jog manual e operação assistida",
            "Telemetria ao vivo + histórico",
          ]}
        />
      </div>
    </Section>
  )
}

// ── How it works ─────────────────────────────────────────────────────────────
const STEPS = [
  {
    icon: Hand,
    title: "Chamada no supplier (botão físico)",
    body: "O operador solicita a entrega; entra na fila com timestamp.",
  },
  {
    icon: CheckCircle2,
    title: "Confirmação no consumer (botão físico)",
    body: "Só despacha quando o destino confirma que pode receber.",
  },
  {
    icon: Radio,
    title: "Despacho do AMR (SEER via TCP)",
    body: "O robô recebe a missão com status em tempo real.",
  },
  {
    icon: AlertTriangle,
    title: "Acompanhamento e exceções",
    body: "Se falhar: alarme, requeue e recuperação (inclui assistência de relocalização).",
  },
  {
    icon: History,
    title: "Histórico para melhoria contínua",
    body: "Tempo por rota, taxa de falhas, gargalos por estação/turno.",
  },
]

function HowItWorks() {
  return (
    <div id="como-funciona" className="border-y border-[#30363d] bg-[#0b0f14]">
      <Section>
        <SectionTitle kicker="Como funciona" title="Da chamada no botão ao histórico — em 5 passos." />
        <ol className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {STEPS.map((s, i) => (
            <li
              key={s.title}
              className="rounded-lg border border-[#30363d] bg-[#161b22] p-5"
            >
              <div className="mb-3 flex items-center gap-3">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-[#1f6feb] text-sm font-bold text-white">
                  {i + 1}
                </span>
                <s.icon className="h-5 w-5 text-[#58a6ff]" />
              </div>
              <h3 className="font-semibold text-[#e6edf3]">{s.title}</h3>
              <p className="mt-1.5 text-sm text-[#8b949e]">{s.body}</p>
            </li>
          ))}
        </ol>
      </Section>
    </div>
  )
}

// ── Differentiators (also the "Segurança" anchor target) ─────────────────────
function Differentiators() {
  return (
    <Section id="seguranca">
      <SectionTitle
        kicker="Diferenciais"
        title="Projetado para fábrica: UX, segurança e integração."
      />
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {[
          { icon: Hand, text: "Handshake físico (2 botões) reduz despacho indevido" },
          { icon: MapPin, text: "Operação robusta em mapa grande com assistência de relocalização" },
          { icon: History, text: "Recuperação de falhas: fila, reenvio, alarmes, visibilidade" },
          { icon: OctagonX, text: "Controle operacional: stop-all, jog manual, intervenção guiada" },
          { icon: Radio, text: "Rastreabilidade: telemetria ao vivo + histórico" },
          { icon: Workflow, text: "Não é robô, é camada de orquestração — entra por cima do que você já tem" },
        ].map((d) => (
          <div key={d.text} className="rounded-lg border border-[#30363d] bg-[#161b22] p-5">
            <d.icon className="mb-3 h-5 w-5 text-[#58a6ff]" />
            <p className="text-[#c9d1d9]">{d.text}</p>
          </div>
        ))}
      </div>
    </Section>
  )
}

// ── Integrations ─────────────────────────────────────────────────────────────
function Integrations() {
  return (
    <div id="integracoes" className="border-y border-[#30363d] bg-[#0b0f14]">
      <Section>
        <SectionTitle
          kicker="Integrações"
          title="Integra com o que já existe no seu chão."
        />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[
            "SEER AMRs (TCP)",
            "OPC UA (botões/IO)",
            "Mapas RoboShop .smap",
            "Desktop (Electron) + painel web (React)",
            "Backend Python/Flask com telemetria (SSE)",
          ].map((item) => (
            <div
              key={item}
              className="flex items-center gap-3 rounded-lg border border-[#30363d] bg-[#161b22] p-4 text-[#c9d1d9]"
            >
              <Plug className="h-5 w-5 shrink-0 text-[#58a6ff]" />
              {item}
            </div>
          ))}
        </div>
        <p className="mt-5 max-w-2xl text-sm text-[#8b949e]">
          Não usa SEER? Ainda vale conversar — o modelo é control-plane e pode ser adaptado por
          integração.
        </p>
      </Section>
    </div>
  )
}

// ── Product / screenshot placeholders ────────────────────────────────────────
function Placeholder({
  icon: Icon,
  label,
  className = "",
}: {
  icon: React.ComponentType<{ className?: string }>
  label: string
  className?: string
}) {
  return (
    <div
      className={
        "flex flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed " +
        "border-[#30363d] bg-[#0d1117] p-8 text-center text-[#6e7681] " +
        className
      }
    >
      <Icon className="h-8 w-8" />
      <span className="text-xs uppercase tracking-wide">{label}</span>
    </div>
  )
}

function Product() {
  return (
    <Section>
      <SectionTitle
        kicker="Produto"
        title="O operador enxerga o que está acontecendo — agora."
      />
      <div className="grid gap-6 lg:grid-cols-2">
        <figure className="space-y-3">
          <Placeholder icon={ImageIcon} label="Screenshot — mapa da planta" className="h-56" />
          <figcaption className="text-sm text-[#8b949e]">
            Mapa da planta com status da missão e fila por estação.
          </figcaption>
        </figure>
        <figure className="space-y-3">
          <Placeholder icon={ImageIcon} label="Screenshot — analytics" className="h-56" />
          <figcaption className="text-sm text-[#8b949e]">
            Chamadas, confirmações, falhas e tempos — por turno e por rota.
          </figcaption>
        </figure>
        <figure className="space-y-3 lg:col-span-2">
          <Placeholder icon={Film} label="Vídeo / GIF — fluxo completo" className="h-64" />
          <figcaption className="text-sm text-[#8b949e]">
            Chamada no botão → confirmação → despacho → acompanhamento.
          </figcaption>
        </figure>
      </div>
    </Section>
  )
}

// ── Pilot ────────────────────────────────────────────────────────────────────
function Pilot() {
  return (
    <div id="piloto" className="border-y border-[#30363d] bg-[#0b0f14]">
      <Section>
        <SectionTitle
          kicker="Piloto"
          title="Piloto pago, rápido e com critério de sucesso."
        />
        <div className="grid gap-6 md:grid-cols-2">
          <div className="rounded-xl border border-[#30363d] bg-[#161b22] p-6">
            <h3 className="mb-4 font-semibold text-[#e6edf3]">O que entra</h3>
            <BulletList
              items={[
                "Integração com até 5 robôs (SEER)",
                "2–6 estações (supplier/consumer) com botões OPC UA",
                "Fila, confirmação, alarmes e stop-all",
                "Painel com telemetria ao vivo + histórico",
              ]}
            />
          </div>
          <div className="rounded-xl border border-[#30363d] bg-[#161b22] p-6">
            <h3 className="mb-4 font-semibold text-[#e6edf3]">O que você recebe</h3>
            <BulletList
              items={[
                "Relatório com tempos, taxa de falhas, causas e recomendações",
                "Plano de escala (R$/robô/mês) e próximos pontos de integração",
              ]}
            />
          </div>
        </div>
        <div className="mt-8">
          <CtaButton label="Solicitar piloto (20 min)" />
        </div>
      </Section>
    </div>
  )
}

// ── FAQ ──────────────────────────────────────────────────────────────────────
const FAQ = [
  {
    q: "Isso substitui WMS/MES?",
    a: "Não. É a camada de orquestração da frota e do fluxo de chamadas/entregas no chão.",
  },
  {
    q: "Preciso trocar meus robôs?",
    a: "Não. Opera por cima da frota existente (primeiro suporte: SEER).",
  },
  {
    q: "E se o robô travar / perder posição?",
    a: "Trabalhamos com fila, alarmes e recuperação, incluindo assistência de relocalização.",
  },
  {
    q: "Tem stop-all?",
    a: "Sim, parada geral por software para controle operacional.",
  },
  {
    q: "Vocês instalam botões?",
    a: "Integramos via OPC UA; a instalação física pode ser feita pela manutenção local com nossa especificação.",
  },
  {
    q: "Como é o comercial?",
    a: "Começamos com piloto pago e, validando os critérios, seguimos para mensalidade por robô.",
  },
]

function Faq() {
  return (
    <Section id="faq">
      <SectionTitle kicker="FAQ" title="Perguntas frequentes" />
      <div className="space-y-3">
        {FAQ.map((f) => (
          <details
            key={f.q}
            className="group rounded-lg border border-[#30363d] bg-[#161b22] p-5 [&_summary]:cursor-pointer"
          >
            <summary className="flex items-center justify-between font-medium text-[#e6edf3] marker:content-none">
              {f.q}
              <ArrowRight className="h-4 w-4 shrink-0 text-[#8b949e] transition-transform group-open:rotate-90" />
            </summary>
            <p className="mt-3 text-sm text-[#8b949e]">{f.a}</p>
          </details>
        ))}
      </div>
    </Section>
  )
}

// ── Final CTA / lead capture ─────────────────────────────────────────────────
function FinalCta() {
  return (
    <div className="border-y border-[#30363d] bg-[#0b0f14]">
      <Section className="text-center">
        <ShieldCheck className="mx-auto mb-4 h-10 w-10 text-[#3fb950]" />
        <h2 className="mx-auto max-w-2xl text-2xl font-semibold text-[#e6edf3] md:text-3xl">
          Pronto para orquestrar sua frota com confirmação física e recuperação automática?
        </h2>
        <p className="mx-auto mt-3 max-w-xl text-[#8b949e]">
          Conversa de 20 minutos para desenhar o piloto na sua planta.
        </p>
        <div className="mt-8 flex flex-wrap items-center justify-center gap-4">
          <CtaButton label="Solicitar piloto (20 min)" />
          {WHATSAPP_URL && (
            <a
              href={WHATSAPP_URL}
              className="inline-flex items-center justify-center gap-2 rounded-md border border-[#30363d] bg-transparent px-5 py-3 text-sm font-semibold text-[#c9d1d9] transition-colors hover:bg-[#21262d]"
            >
              Falar no WhatsApp
            </a>
          )}
        </div>
      </Section>
    </div>
  )
}

// ── Footer ───────────────────────────────────────────────────────────────────
function Footer() {
  return (
    <footer className="bg-[#0d1117]">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-2 px-5 py-10 text-sm text-[#8b949e] sm:px-8">
        <div className="flex items-center gap-2 font-medium text-[#c9d1d9]">
          <MonitorPlay className="h-4 w-4 text-[#58a6ff]" />
          {BRAND} — Orquestração de AMRs para chão de fábrica
        </div>
        <div>Brasil</div>
        <a href={`mailto:${CONTACT_EMAIL}`} className="text-[#58a6ff] hover:underline">
          {CONTACT_EMAIL}
        </a>
        <div className="mt-2 text-[#6e7681]">© 2026</div>
      </div>
    </footer>
  )
}

// ── Page ─────────────────────────────────────────────────────────────────────
export function LandingPage() {
  return (
    <div id="top" className="min-h-screen w-full bg-[#0d1117] font-sans text-[#c9d1d9]">
      <Header />
      <main>
        <Hero />
        <Problem />
        <Solution />
        <HowItWorks />
        <Differentiators />
        <Integrations />
        <Product />
        <Pilot />
        <Faq />
        <FinalCta />
      </main>
      <Footer />
    </div>
  )
}
