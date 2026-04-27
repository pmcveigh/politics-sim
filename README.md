# Northern Ireland Political Simulator Prototype (Stage 1)

## What this prototype is
A text-based Python prototype of a fictionalised Northern Ireland political ecosystem. You are one actor in a system that continues moving with or without your input.

## Stage 1 daily political moments model
- **No weekly turns**.
- Time advances by **time slots** within a day: Morning, Afternoon, Evening, Late Night.
- Decisions advance time by same-day slot progression or into the next day.
- Normal moments never jump multiple days.
- Each day generates a **small agenda (1–3 moments)** to force trade-offs.

## Moment categories
1. Local Issue
2. Party Management
3. Media
4. Formal Session
5. Crisis
6. Campaign
7. Relationship
8. Career Opportunity
9. Constituency Work
10. Backroom Politics

## Core loop
1. Start day and generate agenda.
2. Player responds to a moment (or ignores/defer).
3. System resolves unhandled moments independently.
4. Advance time slot.
5. End day and start next day.

## Features included
- Daily calendar start date: **1 May 2027, Morning**.
- Role-limited moment visibility.
- Urgency, expiry, escalation, and system-handled outcomes for ignored moments.
- Simple stamina mechanic (decision cost affects performance resources).
- Terminal UI with daily agenda, response/ignore flow, time advance, and event log.

## Run
```bash
python -m political_sim.main
```

## Tests
```bash
python -m pytest -q
```
