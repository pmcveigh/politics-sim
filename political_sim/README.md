# Northern Ireland Councillor Political Simulator (MVP)

## Run
```bash
python -m pip install PySide6
python -m political_sim.main
```

## MVP focus
You play one councillor inside a living local political ecosystem. The simulation is about routine political work:

- resident complaints and casework follow-up,
- officer coordination,
- committee and council business,
- party/branch pressure,
- social media and local press,
- rival councillor competition,
- career progression.

The system continues acting without you: rivals intervene, officers delay, media runs stories, and party actors react.

## Dashboard-led interface
The app launches into a dashboard hub inspired by management-game desk screens. It is the main navigation surface and includes:

1. Today’s Desk
2. Casework Inbox
3. Today’s Routine
4. Ward Mood
5. Party Pressure
6. Relationships
7. Career Track
8. News / Local Chatter
9. Alerts
10. Recent Consequence
11. Active Local Story

Each panel has an **Open** action to jump to Inbox, Routine, Stories, Constituency, Party, Relationships, Career, Decision Result, or Log screens.

## Story arcs (MVP)
A light narrative layer connects decisions across days via persistent `StoryArc` state and memory flags.

Implemented arcs:
- School parking chaos
- Planning objection row
- Missed bins backlash
- Town centre decline

Each arc has stages (initial complaint -> escalation -> resolution/fallout), plus tracked pressure, public visibility, player/rival ownership, and remembered handling style (public vs quiet, rival intervention, officer/media/party dynamics).

## Event-driven consequences
There is no passive weekly drift. Variables move because events happen:

- player decisions,
- ignored issues,
- rival interventions,
- officer responses,
- media coverage,
- party reaction,
- story escalation and outcomes,
- career opportunities.

## Career path
Career track remains:

**Councillor -> Candidate -> MLA -> Junior Minister**

Dashboard and Career screens show progress toward Assembly selection using routine performance, local base, branch support, momentum, and rival pressure.

## Current MVP scope limits
Not yet in scope:
- deep negotiation mini-systems,
- long-term policy drafting,
- election campaign mode,
- advanced AI personalities for all actors,
- polished visual theme.

The current priority is functional desk-style decision flow and narrative continuity.
