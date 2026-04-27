# Northern Ireland Political Simulator Prototype (Stage 1)

## What this prototype is
This is a text-based Python prototype of a fictionalised Northern Ireland political ecosystem. You play one actor in a wider system that continues to move whether or not you are central to events.

The game currently models three fictional party machines inspired by familiar NI political types:
- **Unionist Front** (DUP-style unionist logic)
- **People First Movement** (Sinn Féin-style republican logic)
- **Civic Alliance** (Alliance-style cross-community logic)

All politicians and actors are fictional.

## What Stage 1 includes
- Terminal-based playable loop (menu UI).
- Moment-driven timeline (no fixed weekly turn cycle).
- Four time modes:
  - Quiet
  - Formal Session
  - Crisis
  - Campaign
- 30 political moments total:
  - 10 Unionist Front moments
  - 10 People First moments
  - 10 Civic Alliance moments
- Role-limited choices for:
  - Activist
  - Councillor
  - Candidate
  - MLA
  - Adviser
  - Junior Minister
  - Minister
- Core dataclass model for parties, factions, actors, institutions, constituencies, relationships, career state, and the simulation engine.
- Event-driven consequences: variables change because moments occur and decisions are taken.
- Basic career opportunity logic (eligibility rather than forced promotion).
- Relationship scores that influence trust and political positioning.

## What is intentionally not included yet
- No GUI.
- No full UK simulation.
- No Republic of Ireland simulation.
- No passive weekly micro-simulation.
- No real politicians.
- No advanced AI planning, coalition modelling, or deep policy simulation.

## How the political moment system works
The core loop is:

1. A meaningful political moment appears.
2. You pick from responses allowed by your current role.
3. The party machine and wider system reacts.
4. Time jumps to the next meaningful moment (days, weeks, or months depending on time mode).

Quiet periods can jump long stretches. Crisis periods can produce tightly spaced decisions.

## How rank limits actions
Low-rank roles cannot command the whole party. They can influence through:
- branch work
- local pressure
- media briefings
- factional support
- selective leaks

Higher roles unlock broader decisions in Stormont, government departments, and executive contexts.

## Required screens in Stage 1 UI
The terminal menu includes:
1. Main dashboard
2. Player profile
3. Party overview
4. Faction overview
5. Constituency overview
6. Current political moment
7. Decision result (printed after choice)
8. Career opportunities
9. Relationship overview
10. Event log

## Run instructions
From repository root:

```bash
python -m political_sim.main
```

## Tests
Run:

```bash
python -m pytest -q
```

(If `pytest` is not available in your environment, install it or run within your normal dev tooling.)
