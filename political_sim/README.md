# Councillor Routine-and-Beat Engine (MVP)

The simulation now centres on structured councillor days rather than isolated random incidents.

## Core loop

1. Day template selected.
2. Beats generated into Morning/Afternoon/Evening/Late Night.
3. Active content packs and story arcs inject linked beats.
4. Player picks one main action per slot.
5. Decision consequences update story flags, relationships and ownership.
6. Actor reactions add narrative feedback.
7. Follow-up beats are scheduled for later slots/days.
8. Dashboard cards update and guide next actions.

## Implemented content packs

- Car accident hotspot
- Noise complaint involving resident and business
- Stormont campaign help request

## Dashboard panels

- Today’s Flow
- Casework and Inbox
- Active Local Stories
- Ward Mood
- Party and Branch Pressure
- Relationships
- Career Track
- News and Local Chatter
- Alerts
- Recent Consequence

## Subscreens

- Dashboard
- Inbox / Casework
- Today’s Flow / Routine
- Stories
- Party / Branch
- Factions
- Actors
- Constituency
- Relationships
- Career
- Log
- Decision Result

## Testing

`pytest` covers day templates, slot beats, story flags, follow-ups, ignored rival actions, actor reactions, dashboard flow data, story progression, no passive drift, and career eligibility unlocks.
