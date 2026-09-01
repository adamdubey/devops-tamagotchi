# 🐣 DevOps Tamagotchi

> A tiny virtual production server kept alive entirely by GitHub Actions.

<p align="center">
  <img src="./assets/dashboard.svg?v=20260901152502974655" width="720" alt="DevOps Tamagotchi dashboard">
</p>

## What is this?

DevOps Tamagotchi is a tiny simulated production environment living inside a GitHub repository.

Every hour, GitHub Actions:

- 🩺 performs a health check
- 📊 generates fake CPU and memory telemetry
- 🎲 decides whether production is healthy, degraded, or on fire
- 💾 persists its current state
- 🎨 regenerates the dashboard above
- 🤖 commits the updated state back to the repository

You can also manually poke production using the **😈 Poke Prod** workflow.

Available chaos controls:

- 💥 `incident` — cause a generic production incident
- 🔥 `cpu` — saturate CPU
- 🧠 `memory` — simulate a memory leak
- 💚 `heal` — resolve the active incident
- 🍪 `feed` — give the server a snack

No server.

Just GitHub Actions keeping a fake server emotionally stable.

## Architecture

```text
                    GitHub Actions
                          │
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼
      🐣 Health Check           😈 Poke Prod
              │                       │
              │                 ┌─────┴─────┐
              │                 │           │
              ▼                 ▼           ▼
        tamagotchi.py      poke_prod.py   chaos
              │                 │
              └────────┬────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
          state.json      incidents.json
              │
              ▼
        dashboard.svg
              │
              ▼
           README
```


## Incident lifecycle & Possible States

**State Meaning:**
- 🟢 Healthy	prod is vibing
- 🟡 Degraded	prod feels suspicious
- 🔴 Incident	somebody wake up on-call

```
🟢 HEALTHY
     │
     │ 😈 poke prod
     ▼
🔴 INCIDENT
     │
     │ incident timer running
     │
     │ 💚 heal
     ▼
🟢 HEALTHY
     │
     ├── Last MTTR
     └── Average MTTR
```

## Built with

- GitHub Actions
- Python
- SVG
- cron
- persistent JSON state
- incident tracking
- MTTR calculation
- questionable production decisions
