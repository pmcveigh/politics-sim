# Northern Ireland Councillor Routine Simulator (MVP)

## Focus
This MVP is councillor-first. You start as a **Councillor**, and gameplay revolves around ordinary political routine rather than random dramatic events.

Core loop:

1. Start day
2. Review inbox and agenda
3. Choose what to handle
4. Decide how to handle it
5. System reacts
6. Unresolved items escalate or are handled by others
7. Time advances
8. Repeat

## Run
```bash
python -m pip install PySide6
python -m political_sim.main
```

## Design principles
- Structured daily agenda with:
  - one routine obligation,
  - one optional opportunity,
  - one possible complication.
- Time slots: Morning, Afternoon, Evening, Late Night.
- Event-driven consequences only (no passive weekly stat drift).
- Choices are about **handling style** (quiet admin, personal ward work, media play, escalation, delay/ignore, etc.).
- Rival councillor can gain from unhandled visible issues.
- Council officers, party group, branch, local media, and residents' relationships matter.

## Career path (still MVP)
Path remains:

**Councillor -> Candidate -> MLA -> Junior Minister**

Assembly selection opportunity appears only when routine-based thresholds are met (reputation, local base, branch support, momentum, and manageable rival threat).

## Included screens
- Dashboard
- Inbox
- Routine (grouped by time slot)
- Party / Factions / Actors / Constituency / Relationships / Career
- Decision Result
- Log
