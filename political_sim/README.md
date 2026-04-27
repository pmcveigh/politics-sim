# Northern Ireland Political Simulator (Stage 1 terminal prototype)

## What this prototype is
This is a terminal-playable political simulator set in a fictional Northern Ireland ecosystem. You are not the centre of the world: you are one actor in a living system where rivals, factions, journalists and institutions keep moving with or without your intervention.

## How to run
```bash
python -m political_sim.main
```

## Daily political moment system
- Time is tracked in four daily slots: **Morning**, **Afternoon**, **Evening**, **Late Night**.
- At the start of each day, the engine creates **1 to 3 political moments** based on party pressure, faction agitation, constituency context, role access and institutional context.
- Core loop:
  1. View agenda.
  2. Pick a moment to handle (or ignore/defer).
  3. Choose a role-limited decision.
  4. System reacts, time advances, unhandled moments evolve.
- Normal flow never jumps by more than one day.

## Parties included (loaded into one shared engine)
- **Unionist Democratic Front** (DUP-style)
- **People First Republican Movement** (Sinn Féin-style)
- **Civic Alliance Party** (Alliance-style)

The same simulation engine handles all party types via data models and party variables.

## Playable roles
- Activist
- Councillor
- Candidate
- MLA
- Adviser
- Junior Minister
- Minister

Each role has different authority and available actions. Lower roles can influence, lobby, leak, campaign and build relationships, but cannot command whole-party strategy.

## What is included in Stage 1
- Complete dataclass-based model for parties, factions, actors, player, institutions, constituencies, relationships, moments and decisions.
- 30 party-specific political moments (10 per party style).
- Daily agenda UI with urgency, expiry, involved actors/factions and risk hints.
- Role-limited decisions plus fallback influence options.
- Ignored/deferred moments continue through system reactions and expiry logic.
- Career momentum and career opportunity offers (no automatic promotion).
- Event log and quick state inspection menus.

## What is not included yet
- GUI.
- Save/load system.
- Deep economic model.
- Multi-party coalition negotiation gameplay beyond the prototype abstraction.
- Full AI planning for every actor.

## Why the player is a cog, not a controller
The engine resolves unhandled moments, allows rivals to gain credit, escalates unresolved issues, and generates system reactions from leaders, factions, media and opposing parties. You influence outcomes from your role, but you do not command the system.
