from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class PartyType(str, Enum):
    UNIONIST = "unionist"
    REPUBLICAN = "republican"
    CROSS_COMMUNITY = "cross_community"


class Role(str, Enum):
    ACTIVIST = "Activist"
    COUNCILLOR = "Councillor"
    CANDIDATE = "Candidate"
    MLA = "MLA"
    ADVISER = "Adviser"
    JUNIOR_MINISTER = "Junior Minister"
    MINISTER = "Minister"


class InstitutionType(str, Enum):
    LOCAL_COUNCIL = "Local Council"
    ASSEMBLY = "Northern Ireland Assembly"
    EXECUTIVE_DEPARTMENT = "Executive Department"
    PARTY_EXECUTIVE = "Party Executive"
    MEDIA = "Media"
    CIVIL_SERVICE = "Civil Service"


class TimeSlot(str, Enum):
    MORNING = "Morning"
    AFTERNOON = "Afternoon"
    EVENING = "Evening"
    LATE_NIGHT = "Late Night"


class MomentCategory(str, Enum):
    LOCAL_ISSUE = "Local Issue"
    PARTY_MANAGEMENT = "Party Management"
    MEDIA = "Media"
    FORMAL_SESSION = "Formal Session"
    CRISIS = "Crisis"
    CAMPAIGN = "Campaign"
    RELATIONSHIP = "Relationship"
    CAREER_OPPORTUNITY = "Career Opportunity"
    CONSTITUENCY_WORK = "Constituency Work"
    BACKROOM_POLITICS = "Backroom Politics"


class Urgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class GameDate:
    day: int
    month: int
    year: int
    time_slot: TimeSlot

    def label(self) -> str:
        return f"{self.day:02d}/{self.month:02d}/{self.year} ({self.time_slot.value})"


@dataclass
class Faction:
    name: str
    party_id: str
    influence: int = 50
    discipline: int = 50
    loyalty_to_leader: int = 50


@dataclass
class Actor:
    name: str
    party_id: str
    faction: str
    role: Role
    stats: Dict[str, int]


@dataclass
class Party:
    id: str
    name: str
    party_type: PartyType
    leader: str
    factions: List[Faction]
    variables: Dict[str, int]


@dataclass
class Constituency:
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


@dataclass
class Institution:
    name: str
    institution_type: InstitutionType
    legitimacy: int
    pressure: int
    agenda: List[str]
    active_actors: List[str] = field(default_factory=list)


@dataclass
class DecisionOption:
    id: str
    text: str
    required_roles: List[Role]
    effects_player: Dict[str, int]
    effects_party: Dict[str, int]
    effects_relationships: Dict[str, int] = field(default_factory=dict)
    consequence_text: str = ""
    stamina_cost: int = 10
    advances_slots: int = 1
    is_minor_action: bool = False


@dataclass
class PoliticalMoment:
    id: str
    title: str
    description: str
    category: MomentCategory
    time_slot: TimeSlot
    urgency: Urgency
    eligible_roles: List[Role]
    party_tags: List[str]
    constituency_tags: List[str]
    institution_tags: List[str]
    pressure_requirements: Dict[str, int]
    decision_options: List[DecisionOption]
    ignored_effect: str
    handled_by_system_effect: Optional[str]
    expires_after_slots: int
    can_escalate: bool
    escalation_moment_id: Optional[str] = None
    consequence_text: str = ""
    created_day_index: int = 0


@dataclass
class DailyAgenda:
    day_index: int
    moments: List[PoliticalMoment] = field(default_factory=list)


@dataclass
class Relationship:
    target: str
    score: int


@dataclass
class CareerState:
    current_role: Role
    opportunities: List[Role] = field(default_factory=list)
    declined_roles: List[Role] = field(default_factory=list)


@dataclass
class PlayerState:
    name: str
    party_id: str
    constituency: str
    faction: str
    career: CareerState
    reputation: int = 50
    influence: int = 30
    local_base: int = 40
    party_trust: int = 45
    leader_trust: int = 40
    faction_support: int = 50
    media_profile: int = 20
    career_momentum: int = 35
    stamina: int = 100
    enemies: List[str] = field(default_factory=list)
    allies: List[str] = field(default_factory=list)
    relationships: Dict[str, Relationship] = field(default_factory=dict)


@dataclass
class SimulationState:
    day_index: int
    game_date: GameDate
    parties: Dict[str, Party]
    actors: Dict[str, Actor]
    constituencies: Dict[str, Constituency]
    institutions: Dict[str, Institution]
    player: PlayerState
    event_log: List[str] = field(default_factory=list)
    daily_agenda: DailyAgenda = field(default_factory=lambda: DailyAgenda(day_index=0))
