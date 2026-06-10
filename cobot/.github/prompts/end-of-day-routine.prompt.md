---
description: "End-of-day routine: review what got done today, write it to today's daily log (docs/log/), update the index, tidy & push everything, and tee up tomorrow. Run each evening."
name: "End-of-Day Routine"
agent: "ceo"
argument-hint: "Optional: notes on what you worked on today."
---
You are running the founder's **end-of-day routine**. Be the CEO/chief-of-staff: capture the day, keep the house in order, and set up tomorrow. Lead with the summary; keep it tight.

Do this, in order:

1. **See what changed.** Run `git --no-pager log --since="6am" --date=format:'%H:%M' --pretty='%ad  %s'` to get today's commits **with their times** (these are your estimated timestamps for the log), and `git --no-pager status --short` for uncommitted work. Check whether today's daily log already exists (`docs/log/<today>.md`) so you append instead of duplicating. Use the founder's notes above if provided.
2. **Write today's daily log.** Create or update `docs/log/<today>.md` (`AAAA-MM-DD.md`) — see `docs/log/README.md` for the format. It has two parts:
   - **`## Resumo do dia`** at the top — **Aconteceu / Decidido / Próximo**, short and factual. This is what the founder reads to confirm the day at a glance.
   - **`## Log`** — chronological lines `- HH:MM — what was done (refs/commits)`. Use the commit times from step 1 as the estimated times; add non-commit events (meetings, field visits, decisions) at their approximate time too. Only log meaningful actions. Append to the existing Log if the file already exists; keep it in time order.
3. **Update the index.** In `TIMELINE.md` (the index table at repo root), add a row for today at the TOP of the table — `| [\`<today>\`](docs/log/<today>.md) | <one-line summary> |` — or refresh today's summary if the row already exists. Don't paste the full detail here; the index is one line per day.
4. **Tidy & commit the house.** If today created clutter, duplicate docs, or stray files, delegate to `repo-steward` to organize. Commit any meaningful uncommitted work that's in a good state, with clear scoped messages (note: never commit secrets, `fleet.db`, `__pycache__`, or generated files — leave those unstaged).
5. **Push everything.** Push the day's commits to the remote so nothing is left only on this machine: `git push`. If the branch has no upstream yet, set it with `git push -u origin <branch>`. Confirm the push succeeded (or report clearly if it failed, e.g. auth or conflicts) — don't silently skip it.
6. **Tee up tomorrow.** List the top 1–3 things to pick up next, so the morning routine has a clean starting point. Mirror these into the daily log's **Próximo**.

Keep the whole thing short. The deliverable is today's `docs/log/<today>.md` (Resumo + timestamped Log) + the index row in `TIMELINE.md`, everything committed and **pushed**, plus a clear handoff to tomorrow.

## Output Format
- **Today in review**: a few bullets.
- **Daily log updated**: confirm `docs/log/<today>.md` (show the Resumo do dia you wrote).
- **Housekeeping**: what was tidied/committed, or "nothing needed".
- **Pushed**: confirm `git push` succeeded (branch + commits pushed), or report the failure.
- **Tomorrow's pickup**: 1–3 items.
