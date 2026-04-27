from __future__ import annotations

from typing import Dict, List

from .models import DecisionOption, MomentCategory, PoliticalMoment, Role, TimeSlot, Urgency

ALL_ROLES = [r for r in Role]
LOW_RANK = [Role.ACTIVIST, Role.COUNCILLOR, Role.CANDIDATE]
MID_RANK = [Role.COUNCILLOR, Role.CANDIDATE, Role.MLA, Role.ADVISER]
HIGH_RANK = [Role.MLA, Role.ADVISER, Role.JUNIOR_MINISTER, Role.MINISTER]


def make_options(prefix: str, include_minor: bool = True) -> List[DecisionOption]:
    options = [
        DecisionOption(
            id=f"{prefix}_main_line",
            text="Take the lead and set a disciplined response.",
            required_roles=ALL_ROLES,
            effects_player={"party_trust": 3, "influence": 1},
            effects_party={"party_unity": 2, "media_pressure": -1},
            effects_relationships={"leader": 2},
            consequence_text="Your line is adopted quickly.",
            stamina_cost=12,
            advances_slots=1,
        ),
        DecisionOption(
            id=f"{prefix}_delegate",
            text="Delegate and focus on another pressure point.",
            required_roles=ALL_ROLES,
            effects_player={"stamina": 4, "party_trust": -1},
            effects_party={"party_unity": -1},
            effects_relationships={"faction_rival": 2},
            consequence_text="You conserve energy but lose control of tone.",
            stamina_cost=3,
            advances_slots=1,
        ),
    ]
    if include_minor:
        options.append(
            DecisionOption(
                id=f"{prefix}_minor_call",
                text="Make quick calls to allies (minor action).",
                required_roles=ALL_ROLES,
                effects_player={"faction_support": 1},
                effects_party={},
                consequence_text="Allies are warmed up for later.",
                stamina_cost=4,
                advances_slots=0,
                is_minor_action=True,
            )
        )
    return options


def build_moment_templates() -> List[Dict]:
    return [
        {
            "id": "local_canvass_dispute",
            "title": "Canvassing route dispute",
            "description": "Two branch teams clash over doorstep priorities in your patch.",
            "category": MomentCategory.LOCAL_ISSUE,
            "eligible_roles": LOW_RANK,
            "institution_tags": ["Local Council"],
            "urgency": Urgency.MEDIUM,
        },
        {
            "id": "resident_complaint",
            "title": "Resident complaint spikes online",
            "description": "A local service complaint is gathering traction and needs visible handling.",
            "category": MomentCategory.CONSTITUENCY_WORK,
            "eligible_roles": [Role.COUNCILLOR, Role.MLA],
            "institution_tags": ["Local Council"],
            "urgency": Urgency.HIGH,
        },
        {
            "id": "assembly_whip",
            "title": "Whip instruction before vote",
            "description": "Party managers issue strict attendance and line instructions for a formal vote.",
            "category": MomentCategory.FORMAL_SESSION,
            "eligible_roles": [Role.MLA, Role.JUNIOR_MINISTER, Role.MINISTER],
            "institution_tags": ["Northern Ireland Assembly"],
            "urgency": Urgency.HIGH,
        },
        {
            "id": "hostile_journalist",
            "title": "Hostile journalist requests comment",
            "description": "A broadcaster asks for a rapid response on internal tensions.",
            "category": MomentCategory.MEDIA,
            "eligible_roles": MID_RANK + [Role.JUNIOR_MINISTER, Role.MINISTER],
            "institution_tags": ["Media"],
            "urgency": Urgency.HIGH,
        },
        {
            "id": "department_failure",
            "title": "Department delivery failure",
            "description": "A public service failure requires immediate executive line-setting.",
            "category": MomentCategory.CRISIS,
            "eligible_roles": [Role.ADVISER, Role.JUNIOR_MINISTER, Role.MINISTER],
            "institution_tags": ["Executive Department", "Civil Service"],
            "urgency": Urgency.CRITICAL,
        },
        {
            "id": "faction_call",
            "title": "Late-night faction call",
            "description": "Faction organisers demand clarity before tomorrow's briefing.",
            "category": MomentCategory.BACKROOM_POLITICS,
            "eligible_roles": ALL_ROLES,
            "institution_tags": ["Party Executive"],
            "urgency": Urgency.MEDIUM,
        },
        {
            "id": "campaign_leaflet",
            "title": "Leaflet wording row",
            "description": "Campaign teams dispute wording that could alienate a local bloc.",
            "category": MomentCategory.CAMPAIGN,
            "eligible_roles": LOW_RANK + [Role.MLA],
            "institution_tags": ["Party Executive"],
            "urgency": Urgency.LOW,
        },
        {
            "id": "career_offer",
            "title": "Quiet approach about a promotion track",
            "description": "A senior figure tests whether you would accept a bigger internal role.",
            "category": MomentCategory.CAREER_OPPORTUNITY,
            "eligible_roles": MID_RANK + [Role.JUNIOR_MINISTER],
            "institution_tags": ["Party Executive"],
            "urgency": Urgency.MEDIUM,
        },
    ]


def create_moment_from_template(template: Dict, party_id: str, constituency: str, slot: TimeSlot, day_index: int) -> PoliticalMoment:
    return PoliticalMoment(
        id=f"{template['id']}_{day_index}_{slot.name.lower()}",
        title=template["title"],
        description=template["description"],
        category=template["category"],
        time_slot=slot,
        urgency=template["urgency"],
        eligible_roles=template["eligible_roles"],
        party_tags=[party_id],
        constituency_tags=[constituency],
        institution_tags=template["institution_tags"],
        pressure_requirements={"media_pressure": 40},
        decision_options=make_options(template["id"]),
        ignored_effect="The issue moves without you and may empower a rival.",
        handled_by_system_effect="Another actor handled it first and gains credit.",
        expires_after_slots=2,
        can_escalate=template["urgency"] in [Urgency.HIGH, Urgency.CRITICAL],
        escalation_moment_id="department_failure" if template["id"] != "department_failure" else None,
        consequence_text="The system absorbs your move and continues independently.",
        created_day_index=day_index,
    )
