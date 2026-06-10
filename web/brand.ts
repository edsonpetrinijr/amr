// Single source of truth for marketing-page identity.
// Swap the product name, contact email or WhatsApp link here and every
// landing-page reference updates. Keep this file dependency-free.

export const BRAND = "FluxoFleet"

// Category + elevator copy — aligned with docs/POSITIONING.md.
export const TAGLINE = "Orchestration Engine para AMRs industriais"
export const ELEVATOR =
  "FluxoFleet é o motor de orquestração que coordena frotas de AMRs industriais " +
  "com confirmação física e recuperação automática de falhas — sem parar a linha."

export const CONTACT_EMAIL = "piloto@fluxofleet.com"

// Leave empty to hide the WhatsApp CTA. Set to a full https://wa.me/... URL to show it.
export const WHATSAPP_URL = ""

// Pre-filled mailto used by every "Solicitar piloto" button.
export const PILOT_MAILTO =
  `mailto:${CONTACT_EMAIL}` +
  `?subject=${encodeURIComponent(`Solicitar piloto ${BRAND}`)}`
