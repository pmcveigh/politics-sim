from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class Role(str, Enum):
    ACTIVIST = "Activist"
    COUNCILLOR = "Councillor"
    CANDIDATE = "Candidate"
    MLA = "MLA"
    ADVISER = "Adviser"
    JUNIOR_MINISTER = "Junior Minister"
    MINISTER = "Minister"


class TimeSlot(str, Enum):
    MORNING = "Morning"
    AFTERNOON = "Afternoon"
    EVENING = "Evening"
    LATE_NIGHT = "Late Night"


class MomentCategory(str, Enum):
    CONSTITUTIONAL = "Constitutional"
    GOVERNANCE = "Governance"
    CANDIDATE_SELECTION = "Candidate Selection"
    MEDIA = "Media"
    DELIVERY = "Service Delivery"
    FACTIONAL = "Factional"
    CAMPAIGN = "Campaign"
    LOCAL = "Local"
    CAREER_OPPORTUNITY = "Career Opportunity"


class Urgency(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class InstitutionType(str, Enum):
    LOCAL_COUNCIL = "Local Council"
    ASSEMBLY = "Northern Ireland Assembly"
    EXECUTIVE_DEPARTMENT = "Executive Department"
    PARTY_EXECUTIVE = "Party Executive"
    MEDIA = "Media"
    CIVIL_SERVICE = "Civil Service"


class PartyType(str, Enum):
    DUP_STYLE = "DUP-style"
    SINN_FEIN_STYLE = "Sinn Féin-style"
    ALLIANCE_STYLE = "Alliance-style"


class DecisionType(str, Enum):
    HARD_LINE = "Hard line"
    COMPROMISE = "Compromise"
    BRIEFING = "Briefing"
    LOBBY = "Lobby"
    LEAK = "Leak"
    LOCAL_WORK = "Local work"
    DISCIPLINE = "Discipline"
    STAY_QUIET = "Stay quiet"
    OPPOSE = "Oppose"
    SUPPORT = "Support"
    CAREER = "Career move"


@dataclass
class Party:
    id: str
    name: str
    party_type: PartyType
    leader_actor_id: str
    in_government: bool
    party_unity: int
    leader_authority: int
    activist_morale: int
    public_trust: int
    media_pressure: int
    scandal_risk: int
    election_readiness: int
    faction_pressure: int
    government_credibility: int
    local_machine_strength: int
    custom_variables: Dict[str, int] = field(default_factory=dict)


@dataclass
class Faction:
    id: str
    name: str
    party_id: str
    strength: int
    loyalty_to_leader: int
    agitation: int
    ideology_tags: List[str]
    preferred_decision_types: List[DecisionType]
    disliked_decision_types: List[DecisionType]


@dataclass
class Actor:
    id: str
    name: str
    role: Role
    party_id: str
    constituency_id: str
    faction_id: str
    reputation: int
    competence: int
    ambition: int
    loyalty_to_party: int
    loyalty_to_leader: int
    faction_loyalty: int
    media_skill: int
    local_machine_strength: int
    ideological_intensity: int
    scandal_risk: int
    stamina: int
    career_momentum: int
    influence: int = 0


@dataclass
class Player:
    actor_id: str
    current_role: Role
    stamina: int
    local_base: int
    party_trust: int
    leader_trust: int
    faction_support: int
    media_profile: int
    career_momentum: int
    allies: List[str] = field(default_factory=list)
    enemies: List[str] = field(default_factory=list)
    career_state: "CareerState" = field(default_factory=lambda: CareerState(current_role=Role.ACTIVIST))
    available_actions: List[str] = field(default_factory=list)


@dataclass
class Constituency:
    id: str
    name: str
    unionist_strength: int
    nationalist_strength: int
    cross_community_strength: int
    working_class_pressure: int
    middle_class_pressure: int
    rural_pressure: int
    urban_pressure: int
    local_issue_pressure: int
    turnout_energy: int
    party_machine_strength: Dict[str, int]
    local_media_heat: int
    current_flashpoint: str


@dataclass
class Institution:
    id: str
    name: str
    institution_type: InstitutionType
    legitimacy: int
    pressure: int
    agenda: List[str]
    active_actor_ids: List[str] = field(default_factory=list)


@dataclass
class Relationship:
    source_id: str
    target_id: str
    score: int
    label: str


@dataclass
class Decision:
    id: str
    label: str
    description: str
    required_roles: List[Role]
    decision_type: DecisionType
    influence_cost: int
    stamina_cost: int
    risk_level: int
    effects: Dict[str, int]
    relationship_effects: Dict[str, int]
    career_effects: Dict[str, int]
    consequence_text: str
    time_advance: int


@dataclass
class Moment:
    id: str
    title: str
    description: str
    party_id: Optional[str]
    party_type: Optional[PartyType]
    category: MomentCategory
    urgency: Urgency
    time_slot: TimeSlot
    eligible_roles: List[Role]
    institution_tags: List[str]
    constituency_tags: List[str]
    faction_tags: List[str]
    involved_actor_ids: List[str]
    pressure_requirements: Dict[str, int]
    decision_options: List[Decision]
    ignored_effect: str
    expires_after_slots: int
    can_escalate: bool
    escalation_moment_id: Optional[str]
    consequence_summary: str
    created_day: int
    created_slot_index: int


@dataclass
class CareerState:
    current_role: Role
    previous_roles: List[Role] = field(default_factory=list)
    reputation: int = 50
    influence: int = 20
    local_base: int = 40
    party_trust: int = 45
    leader_trust: int = 40
    faction_support: int = 45
    media_profile: int = 20
    career_momentum: int = 35
    eligibility_flags: Dict[str, bool] = field(default_factory=dict)
    promotion_offers: List[Role] = field(default_factory=list)
    rivals: List[str] = field(default_factory=list)


@dataclass
class SimulationState:
    day: int
    month: int
    year: int
    slot: TimeSlot
    parties: Dict[str, Party]
    factions: Dict[str, Faction]
    actors: Dict[str, Actor]
    player: Player
    constituencies: Dict[str, Constituency]
    institutions: Dict[str, Institution]
    relationships: Dict[str, Relationship]
    active_moments: List[Moment] = field(default_factory=list)
    event_log: List[str] = field(default_factory=list)

    def date_label(self) -> str:
        return f"{self.day} {self.month_name()} {self.year}, {self.slot.value}"

    def month_name(self) -> str:
        names = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]
        return names[self.month - 1]

