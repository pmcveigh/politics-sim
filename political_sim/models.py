from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
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
    CONSTITUENCY_WORK = "Constituency Work"
    FORMAL_SESSION = "Formal Session"
    MEDIA = "Media"
    CAREER_OPPORTUNITY = "Career Opportunity"
    BACKROOM_POLITICS = "Backroom Politics"
    RELATIONSHIP_REACTION = "Relationship/System Reaction"
    CAMPAIGN = "Campaign"
    CRISIS = "Crisis"


class Urgency(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class InstitutionType(str, Enum):
    LOCAL_COUNCIL = "Local Council"
    ASSEMBLY = "Assembly"
    PARTY_HQ = "Party HQ"
    MEDIA = "Media"
    EXECUTIVE = "Executive"


class PartyType(str, Enum):
    UNIONIST = "DUP-style"
    REPUBLICAN = "Sinn Féin-style"
    CROSS_COMMUNITY = "Alliance-style"


class DecisionType(str, Enum):
    PARTY_LINE = "Party Line"
    LOCALIST = "Localist"
    COMPROMISE = "Compromise"
    PROFILE_BUILDING = "Profile Building"
    LOYALIST = "Loyalist"
    FACTIONAL = "Factional"
    CAREER = "Career"
    DEFENSIVE = "Defensive"


@dataclass
class Party:
    id: str
    name: str
    party_type: PartyType
    leader_actor_id: str
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
    custom_variables: Dict[str, int]


@dataclass
class Faction:
    id: str
    party_id: str
    name: str
    strength: int
    loyalty_to_leader: int
    agitation: int
    relationship_with_player: int
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
    influence: int


@dataclass
class Player:
    actor_id: str
    name: str
    role: Role
    party_id: str
    constituency_id: str
    stamina: int
    influence: int
    reputation: int
    local_base: int
    party_trust: int
    leader_trust: int
    media_profile: int
    career_momentum: int


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
    local_media_heat: int
    current_flashpoint: str
    party_machine_strength: Dict[str, int]


@dataclass
class Institution:
    id: str
    name: str
    institution_type: InstitutionType


@dataclass
class Relationship:
    source_id: str
    target_id: str
    label: str
    score: int


@dataclass
class Decision:
    id: str
    label: str
    description: str
    decision_type: DecisionType
    allowed_roles: List[Role]
    effects: Dict[str, int]
    relationship_effects: Dict[str, int]
    career_effects: Dict[str, int]
    result_text: str
    time_advance: int = 1


@dataclass
class Moment:
    id: str
    title: str
    description: str
    category: MomentCategory
    urgency: Urgency
    eligible_roles: List[Role]
    expiry_slots: int
    involved_actor_ids: List[str]
    involved_faction_ids: List[str]
    risk_preview: str
    decision_options: List[Decision]
    ignored_effects: Dict[str, int]
    ignored_relationship_effects: Dict[str, int]
    ignored_text: str
    system_reaction: str


@dataclass
class CareerState:
    current_role: Role
    survived_party_crisis: bool = False
    candidate_selected: bool = False
    became_mla: bool = False
    promotion_offers: List[Role] = field(default_factory=list)
    recent_events: List[str] = field(default_factory=list)


@dataclass
class SimulationState:
    current_date: date
    time_slot: TimeSlot
    parties: Dict[str, Party]
    factions: Dict[str, Faction]
    actors: Dict[str, Actor]
    player: Player
    constituencies: Dict[str, Constituency]
    institutions: Dict[str, Institution]
    relationships: Dict[str, Relationship]
    career: CareerState
    active_moments: List[Moment]
    current_result: Optional[str] = None
    event_log: List[str] = field(default_factory=list)

    def datetime_label(self) -> str:
        return f"{self.current_date.isoformat()} {self.time_slot.value}"
