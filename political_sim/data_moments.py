from __future__ import annotations

from typing import List

from .models import DecisionOption, PoliticalMoment, Role, TimeMode


ROLE_SETS = {
    "low": [Role.ACTIVIST, Role.COUNCILLOR, Role.CANDIDATE],
    "mid": [Role.COUNCILLOR, Role.CANDIDATE, Role.MLA, Role.ADVISER],
    "high": [Role.MLA, Role.ADVISER, Role.JUNIOR_MINISTER, Role.MINISTER],
    "all": [
        Role.ACTIVIST,
        Role.COUNCILLOR,
        Role.CANDIDATE,
        Role.MLA,
        Role.ADVISER,
        Role.JUNIOR_MINISTER,
        Role.MINISTER,
    ],
}


def _options(prefix: str) -> List[DecisionOption]:
    return [
        DecisionOption(
            id=f"{prefix}_discipline",
            text="Stick to the party line and keep discipline.",
            required_roles=ROLE_SETS["all"],
            effects_player={"party_trust": 4, "leader_trust": 4, "influence": 1, "media_profile": -1},
            effects_party={"party_unity": 3, "public_trust": 1},
            effects_relationships={"leader": 5, "faction_rival": -2},
            consequence_text="You reinforced discipline and avoided a split headline.",
        ),
        DecisionOption(
            id=f"{prefix}_pivot",
            text="Push a pragmatic compromise to steady the situation.",
            required_roles=[Role.COUNCILLOR, Role.CANDIDATE, Role.MLA, Role.ADVISER, Role.JUNIOR_MINISTER, Role.MINISTER],
            effects_player={"reputation": 2, "influence": 2, "party_trust": -1, "media_profile": 2},
            effects_party={"government_credibility": 2, "party_unity": -1, "media_pressure": -1},
            effects_relationships={"moderates": 4, "hardliners": -3},
            consequence_text="You sold a compromise, gaining profile but irritating purists.",
            delayed_effect_note="A future leadership briefing may revisit your compromise.",
        ),
        DecisionOption(
            id=f"{prefix}_leak",
            text="Brief allies off-record and leak pressure upwards.",
            required_roles=[Role.ACTIVIST, Role.COUNCILLOR, Role.CANDIDATE, Role.ADVISER, Role.MLA],
            effects_player={"influence": 3, "party_trust": -4, "leader_trust": -3, "career_momentum": 1},
            effects_party={"media_pressure": 3, "faction_pressure": 2, "scandal_risk": 2},
            effects_relationships={"leader": -5, "media": 3},
            consequence_text="The leak landed. You matter more, but trust has thinned.",
            delayed_effect_note="Enemies may brief against you in a later crisis.",
        ),
    ]


def create_moments() -> List[PoliticalMoment]:
    dup_titles = [
        "Constitutional pressure spike",
        "Business donors warn over instability",
        "Candidate selection fight",
        "Media gaffe from social conservative figure",
        "Stormont delivery crisis",
        "Westminster leverage opportunity",
        "Hardline flank pressure",
        "Local loyalist community meeting",
        "Leadership briefing on discipline",
        "Council flag dispute",
    ]
    sf_titles = [
        "Border poll pressure builds",
        "Legacy issue returns to headlines",
        "Dublin credibility test",
        "Housing policy flashpoint",
        "Activist controversy",
        "Stormont delivery crunch",
        "Candidate selection dispute",
        "Republican credentials challenged",
        "Southern media scrutiny",
        "Leadership strategy briefing",
    ]
    al_titles = [
        "Cross-community messaging test",
        "Tactical vote squeeze",
        "Both sides attack neutrality",
        "Liberal social issue backlash",
        "Candidate overstretch in unionist area",
        "Council delivery opportunity",
        "Media praise raises expectations",
        "Young urban wing demands stronger line",
        "Executive participation dilemma",
        "Leadership positioning row",
    ]

    moments: List[PoliticalMoment] = []
    for idx, title in enumerate(dup_titles, start=1):
        mode = [TimeMode.CRISIS, TimeMode.FORMAL_SESSION, TimeMode.QUIET, TimeMode.CAMPAIGN][idx % 4]
        moments.append(
            PoliticalMoment(
                id=f"dup_{idx}",
                title=title,
                description=f"Unionist Front confronts: {title.lower()}. You are one actor, not the commanding centre.",
                time_mode=mode,
                eligible_roles=ROLE_SETS["all"],
                target_party_id="unionist_front",
                affected_variables=["party_unity", "constitutional_pressure", "media_pressure"],
                decision_options=_options(f"dup_{idx}"),
                consequence_text="Party actors react to your move and continue manoeuvring without waiting on you.",
                relationship_effects="Leader trust and factional support can shift.",
                career_effects="Solid handling can unlock candidate or committee pathways.",
                delayed_effects="Leaked or compromised choices may resurface in later briefings.",
            )
        )
    for idx, title in enumerate(sf_titles, start=1):
        mode = [TimeMode.QUIET, TimeMode.CRISIS, TimeMode.FORMAL_SESSION, TimeMode.CAMPAIGN][idx % 4]
        moments.append(
            PoliticalMoment(
                id=f"sf_{idx}",
                title=title,
                description=f"People First Movement faces: {title.lower()}. Internal factions expect different responses.",
                time_mode=mode,
                eligible_roles=ROLE_SETS["all"],
                target_party_id="people_first",
                affected_variables=["party_unity", "legacy_pressure", "stormont_stability"],
                decision_options=_options(f"sf_{idx}"),
                consequence_text="Your action nudges the machine, then organisers, media, and rivals carry on.",
                relationship_effects="Old-guard and pragmatist links can diverge.",
                career_effects="Momentum can open advisory or ministerial eligibility later.",
                delayed_effects="Legacy and media choices may return during campaign mode.",
            )
        )
    for idx, title in enumerate(al_titles, start=1):
        mode = [TimeMode.FORMAL_SESSION, TimeMode.QUIET, TimeMode.CAMPAIGN, TimeMode.CRISIS][idx % 4]
        moments.append(
            PoliticalMoment(
                id=f"all_{idx}",
                title=title,
                description=f"Civic Alliance is tested by: {title.lower()}. Balancing both sides remains difficult.",
                time_mode=mode,
                eligible_roles=ROLE_SETS["all"],
                target_party_id="civic_alliance",
                affected_variables=["cross_community_credibility", "both_sides_pressure", "tactical_vote_pressure"],
                decision_options=_options(f"all_{idx}"),
                consequence_text="You influence tone and positioning, but party dynamics continue independently.",
                relationship_effects="Idealists and pragmatists remember your line.",
                career_effects="Strong performance can create candidacy or committee opportunities.",
                delayed_effects="Overextension and expectations can trigger later crisis moments.",
            )
        )
    return moments
