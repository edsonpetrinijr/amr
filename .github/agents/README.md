# AI Agent Roster

Your AI "company". You have **one point of contact: the CEO**. You talk to the CEO, and it
delegates to the right specialist, synthesizes their work, and returns a single clear answer.
You can still call any specialist directly when you want to — but day to day, just talk to the CEO.

Every agent reads `_company-context.md` for shared context.

> Edit `_company-context.md` whenever the venture changes — it is the single source of truth all agents rely on.

## How it works (hub-and-spoke + a parallel engineering pod)

```
                    you
                     |
                   [CEO]                 <- single point of contact, orchestrates everything
          /          |          \
   [eng-lead]     growth      strategy / risk / finance ...
    /   |   \                  (specialists below)
front  back  integration       <- engineers run IN PARALLEL, each in its own folders
   \   |   /
 senior-engineer (glue + review)
```

The CEO triages your ask and routes it. For engineering, it hands the work to the **Engineering
Lead**, which **splits it by domain and runs several engineers at the same time**, then integrates —
so building is fast and parallel instead of one-at-a-time.

## The team

### Talk to this one
| Agent | File | Role |
|-------|------|------|
| **CEO / Co-founder** | `ceo.agent.md` | Your chief of staff + strategist. Orchestrates everyone and makes the final call. |

### Engineering pod (runs in parallel)
| Agent | File | Use it for |
|-------|------|------------|
| **Engineering Lead** | `eng-lead.agent.md` | Splits a build/fix into independent streams and runs the engineers **in parallel**, then integrates |
| **Frontend Engineer** | `frontend-engineer.agent.md` | `frontend/` + `electron/` — React/TS/Vite/Tailwind UI, desktop shell |
| **Backend Engineer** | `backend-engineer.agent.md` | `backend/app/` core — Flask, SSE, dispatcher, models, provider, db |
| **Integration Engineer** | `integration-engineer.agent.md` | SEER TCP (`seer/`), OPC UA (`opcua/`), `.smap`/`.task`, maps |
| **Senior Software Engineer** | `senior-engineer.agent.md` | Cross-cutting glue, code review, integrating the parallel pieces; small single-domain fixes |

> **Parallel-safe by design:** each engineer edits a disjoint set of folders, so multiple instances
> work at once without colliding. The Engineering Lead partitions the work and defines the seams.

### Other specialists the CEO delegates to
| Agent | File | Use it for |
|-------|------|------------|
| **CTO / Architect** | `cto-architect.agent.md` | Architecture, integrations, big technical bets, system design |
| **Product Manager** | `product-manager.agent.md` | Roadmap, specs/user stories, MVP scope, prioritization |
| **Domain Expert** | `domain-expert.agent.md` | Factory-floor reality checks, operator workflows, edge cases |
| **GTM / Sales** | `gtm-sales.agent.md` | Outreach, discovery, pilot offers, objection handling |
| **Market Specialist** | `market-specialist.agent.md` | TAM/SAM/SOM, ICP, pricing research |
| **Competitive Analyst** | `competitive-analyst.agent.md` | Competitor teardowns, positioning, differentiation |
| **Finance / Fundraising** | `finance.agent.md` | Unit economics, runway, pricing math, fundraising |
| **Marketing / Brand** | `marketing.agent.md` | Positioning, messaging, landing copy, case studies |
| **Legal / Compliance** | `legal-compliance.agent.md` | Safety standards, contracts, IP, liability |
| **Idea Strategist / Incubator** | `idea-strategist.agent.md` | Matures & pressure-tests raw ideas, validates with specialists, prototypes in `idea/<slug>` branches |
| **Repo Steward / Organizer** | `repo-steward.agent.md` | Organizes files, dedupes, enforces structure, tidies the repo after changes |

## Daily routines (slash commands)
Run these from chat as prompts (type `/` in the chat box). Both run as the CEO.
- **`/morning-routine`** — start of day: catch up via the recent daily logs in `docs/log/` + git log, orient, surface the backlog, and agree on ONE focus. Read-only.
- **`/end-of-day-routine`** — end of day: review what got done, write today's `docs/log/AAAA-MM-DD.md` (Resumo do dia + timestamped Log) and update the `TIMELINE.md` index, tidy via `repo-steward`, commit and **push** everything, and tee up tomorrow.

Prompt files live in `.github/prompts/`.

## How to use
1. **Default:** open the CEO agent and tell it what you need — it routes and synthesizes.
2. **Build something:** the CEO routes it to `eng-lead`, which runs engineers in parallel. (You can also open `eng-lead` directly.)
3. **Direct:** for a tiny fix, pick the specific engineer from the agent picker.
4. Agents lead with the answer and stay brief (see each file's "Response style" block).

## Notes
- **Engineers** (`eng-lead`'s pod) and **CTO** have `edit` + `execute` (write code, use git). **Repo Steward** has them too (moves/merges files via git). **CEO** has `edit` for docs only (timeline/context), never the codebase.
- The **`agent`** tool (delegation) is held by the **CEO** (delegates to everyone) and the **Engineering Lead** (delegates to the engineer pod).
- The CEO maintains the project log as **one file per day in `docs/log/`**, indexed by **`TIMELINE.md`** (repo root) — each day has a quick **Resumo** + a timestamped **Log**, newest day on top.
- The engineers **commit to git constantly** — small, frequent, scoped commits on `main`, each in its own lane.
- These are advisors/doers, not autopilots — they surface decisions; you decide.