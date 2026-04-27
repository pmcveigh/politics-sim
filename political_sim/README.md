# Northern Ireland Political Simulator - MVP-of-the-MVP

## What this prototype is
A compact, event-driven desktop prototype built with **Python + PySide6**. You play one actor inside a live political machine. Politics moves with or without you.

## Install
```bash
python -m pip install PySide6
```

## Run
```bash
python -m political_sim.main
```

## Stage 1 includes
- GUI with persistent layout:
  - Left nav: Dashboard, Inbox, Party, Factions, Actors, Constituency, Relationships, Career, Log.
  - Top bar: date, time slot, player identity and core stats.
  - Main panel: selected screen.
  - Right panel: context summary and warnings.
- Default start:
  - Fictional player.
  - **Councillor**.
  - **Civic Alliance Party**.
  - **North Down**.
- Event-driven time slots: Morning, Afternoon, Evening, Late Night.
- 12 core political moments for the intended path:
  - Councillor -> Candidate -> MLA -> crisis survivor -> junior minister offer.
- Role-limited decisions (invalid decisions hidden).
- Ignore handling with independent system reactions and rival gains.
- Decision Result view with visible consequences.
- Chronological event log.

## Intentionally not included
- Full UK simulation.
- Full election model.
- Real politicians.
- Passive weekly stat drift.
- Database/save system.

## Event-driven consequences
Variables change only when moments are handled or ignored. The simulation does **not** apply passive weekly stat decay.

## Career path logic
Progression is gated by thresholds and events.
- Candidate selection checks reputation, local base, branch relationship and momentum.
- MLA status is triggered through election result moments.
- Junior minister is an offer moment and can be accepted or declined.

## The player is a cog in a system
Ignoring moments can help rivals, reduce trust, and trigger consequences. The machine keeps moving whether you intervene or not.
