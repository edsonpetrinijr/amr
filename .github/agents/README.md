# AI Agent Roster

Your AI "company". You have **one point of contact: the CEO**. You talk to the CEO, and it
delegates to the right specialist, synthesizes their work, and returns a single clear answer.
You can still call any specialist directly when you want to — but day to day, just talk to the CEO.

Every agent reads `_company-context.md` for shared context.

> Edit `_company-context.md` whenever the venture changes — it is the single source of truth all agents rely on.

## How it works (hub-and-spoke)

```
            you
             |
           [CEO]  <- single point of contact, orchestrates everything
        /    |    \
   engineering  growth  risk/finance ... (specialists below)
```

The CEO triages your ask, routes it to the minimum set of specialists, and hands you back one
answer with next actions. This keeps your attention on one conversation instead of eleven.

## The team

### Talk to this one
| Agent | File | Role |
|-------|------|------|
| **CEO / Co-founder** | `ceo.agent.md` | Your chief of staff + strategist. Orchestrates the team and makes the final call. |

### Specialists the CEO delegates to
| Agent | File | Use it for |
|-------|------|------------|
| **Senior Software Engineer** | `senior-engineer.agent.md` | Hands-on coding, refactoring, debugging, code review, clean code & DSA — knows this codebase |
| **Repo Steward / Organizer** | `repo-steward.agent.md` | Organizes/orchestrates files, dedupes, enforces folder structure, tidies the repo after changes |
| **CTO / Architect** | `cto-architect.agent.md` | Architecture, integrations, big technical bets, system design |
| **Product Manager** | `product-manager.agent.md` | Roadmap, specs/user stories, MVP scope, prioritization |
| **Domain Expert** | `domain-expert.agent.md` | Factory-floor reality checks, operator workflows, edge cases |
| **GTM / Sales** | `gtm-sales.agent.md` | Outreach, discovery, pilot offers, objection handling |
| **Market Specialist** | `market-specialist.agent.md` | TAM/SAM/SOM, ICP, pricing research |
| **Competitive Analyst** | `competitive-analyst.agent.md` | Competitor teardowns, positioning, differentiation |
| **Finance / Fundraising** | `finance.agent.md` | Unit economics, runway, pricing math, fundraising |
| **Marketing / Brand** | `marketing.agent.md` | Positioning, messaging, landing copy, case studies |
| **Legal / Compliance** | `legal-compliance.agent.md` | Safety standards, contracts, IP, liability |

## How to use
1. **Default:** open the CEO agent and tell it what you need — it routes and synthesizes.
2. **Direct:** if you already know who you need (e.g., a quick code fix), pick that specialist from the agent picker.
3. Agents lead with the answer and stay brief (see each file's "Response style" block).

## Notes
- **CTO** and **Senior Engineer** have `edit` + `execute` (they write code and use git). The **Repo Steward** also has `edit` + `execute` (it moves/merges/deletes files via git). The **CEO** has `edit` too, but only for docs (the timeline/context), never the codebase.
- Only the **CEO** has the `agent` tool — it is the one that delegates to the others.
- The CEO maintains **`TIMELINE.md`** (repo root) so you can follow everything that's been done — newest entry on top.
- The engineers **commit to git constantly** — small, frequent, message-scoped commits on `main`.
- These are advisors, not autopilots — they surface decisions; you decide.
