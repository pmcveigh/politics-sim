# political-sim

Routine-and-beat councillor prototype built with Python and PySide6.

## Run

```bash
python -m political_sim.main
```

## What this stage implements

- A dashboard-led vertical slice.
- Day templates (admin, crisis, campaign, council, community).
- Daily beats grouped into Morning, Afternoon, Evening and Late Night.
- Three playable story chains:
  - Car accident hotspot
  - Noise complaint (resident and business)
  - Stormont campaign help request
- Decision options with explanatory upside/risk/costs.
- Story memory flags and stage progression.
- Actor reactions and relationship movement.
- Follow-up scheduling for later days.
- System independence when beats are ignored (rival/officer/media movement).
- Career path scaffold: Councillor -> Candidate -> MLA -> Junior Minister.

## Scope

This is not a full UK simulator or election simulator. It is an MVP proving that councillor routine can feel dynamic and interactive without random isolated events.
