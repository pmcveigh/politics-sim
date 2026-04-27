from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Dict, List, Optional


class Role(str, Enum):
    COUNCILLOR = "Councillor"
    CANDIDATE = "Candidate"
    MLA = "MLA"
    JUNIOR_MINISTER = "Junior Minister"


class TimeSlot(str, Enum):
    MORNING = "Morning"
    AFTERNOON = "Afternoon"
    EVENING = "Evening"
    LATE_NIGHT = "Late Night"


class RoutineCategory(str, Enum):
    CASEWORK = "Casework"
    COUNCIL_BUSINESS = "Council Business"
    COMMITTEE_WORK = "Committee Work"
    OFFICER_FOLLOW_UP = "Officer Follow-Up"
    PARTY_GROUP = "Party Group"
    BRANCH_POLITICS = "Branch Politics"
    COMMUNITY_EVENT = "Community Event"
    WARD_VISIBILITY = "Ward Visibility"
    LOCAL_MEDIA = "Local Media"
    SOCIAL_MEDIA = "Social Media"
    RIVAL_ACTIVITY = "Rival Activity"
    PERSONAL_CAPACITY = "Personal Capacity"
    CAREER_POSITIONING = "Career Positioning"


class MomentCategory(str, Enum):
    ROUTINE = "Routine"
    ESCALATION = "Escalation"
    CAREER = "Career"
    REACTION = "Reaction"


class StoryStatus(str, Enum):
    ACTIVE = "Active"
    RESOLVED = "Resolved"
    FALLOUT = "Fallout"


class Urgency(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class InstitutionType(str, Enum):
    LOCAL_COUNCIL = "Local Council"
    PARTY = "Party"
    MEDIA = "Media"
    COMMUNITY = "Community"


class PartyType(str, Enum):
    UNIONIST = "Unionist"
    REPUBLICAN = "Republican"
    CROSS_COMMUNITY = "Cross-Community"


class DecisionType(str, Enum):
    HANDLE = "Handle"
    POSITION = "Position"
    ESCALATE = "Escalate"
    IGNORE = "Ignore"


class HandlingStyle(str, Enum):
    QUIET_ADMIN = "Quiet Administrative"
    PERSONAL_WARD_WORK = "Personal Ward Work"
    PUBLIC_CAMPAIGNING = "Public Campaigning"
    PARTY_ESCALATION = "Party Escalation"
    CROSS_PARTY_DEAL = "Cross-Party Deal"
    MEDIA_PLAY = "Media Play"
    DELAY_IGNORE = "Delay / Ignore"
    HONEST_REFUSAL = "Honest Refusal"


class ItemStatus(str, Enum):
    OPEN = "Open"
    HANDLED = "Handled"
    EXPIRED = "Expired"
    TAKEN_BY_OTHERS = "Taken by Others"


@dataclass
class Party:
    id: str
    name: str
    party_type: PartyType


@dataclass
class Faction:
    id: str
    party_id: str
    name: str
    pressure: int


@dataclass
class Actor:
    id: str
    name: str
    role: Role
    party_id: str


@dataclass
class Player:
    actor_id: str
    name: str
    role: Role
    party_id: str
    constituency_id: str
    reputation: int
    influence: int
    stamina: int
    casework_backlog: int
    resident_trust: int
    local_media_profile: int
    branch_support: int
    party_group_trust: int
    officer_relationship: int
    rival_threat: int
    social_media_volatility: int
    ward_visibility: int
    committee_credibility: int
    local_issue_pressure: int
    career_momentum: int
    local_base: int


@dataclass
class Constituency:
    id: str
    name: str
    local_issue_pressure: int
    local_media_heat: int
    turnout_energy: int
    working_class_pressure: int
    middle_class_pressure: int
    rural_pressure: int
    urban_pressure: int
    current_flashpoint: str
    resident_satisfaction: int
    council_service_pressure: int
    party_machine_strength: Dict[str, int]


@dataclass
class Institution:
    id: str
    name: str
    institution_type: InstitutionType


@dataclass
class Relationship:
    id: str
    label: str
    score: int


@dataclass
class Decision:
    id: str
    label: str
    decision_type: DecisionType
    handling_style: HandlingStyle
    allowed_roles: List[Role]
    stamina_cost: int
    is_minor: bool
    effects: Dict[str, int]
    relationship_effects: Dict[str, int]
    result_text: str
    likely_upside: str = ""
    likely_risk: str = ""
    influence_cost: int = 0
    affected_groups: List[str] = field(default_factory=list)


@dataclass
class RoutineItem:
    id: str
    title: str
    description: str
    category: RoutineCategory
    time_slot: TimeSlot
    urgency: Urgency
    workload_cost: int
    stamina_cost: int
    influence_cost: int
    expires_after_slots: int
    involved_actor_ids: List[str]
    involved_relationships: List[str]
    linked_constituency_id: str
    possible_decisions: List[Decision]
    ignored_effect: Dict[str, int]
    escalation: str
    status: ItemStatus = ItemStatus.OPEN
    slots_remaining: int = 1
    story_arc_id: Optional[str] = None


@dataclass
class StoryArc:
    id: str
    title: str
    theme: str
    status: StoryStatus
    current_stage: int
    linked_constituency_id: str
    involved_actor_ids: List[str]
    involved_relationships: List[str]
    pressure_level: int
    public_visibility: int
    player_ownership: int
    rival_ownership: int
    next_possible_moments: List[str]
    outcome_tags: List[str]
    memory: Dict[str, bool] = field(default_factory=dict)


@dataclass
class Moment:
    id: str
    title: str
    description: str
    category: MomentCategory
    source_item_id: Optional[str]


@dataclass
class CareerState:
    current_role: Role
    path_target: Role = Role.MLA
    assembly_selection_open: bool = False


@dataclass
class DailyAgenda:
    date: date
    day_name: str
    routine_obligation_id: str
    opportunity_id: str
    complication_id: str
    items_by_slot: Dict[TimeSlot, List[str]] = field(default_factory=dict)


@dataclass
class SimulationState:
    current_date: date
    time_slot: TimeSlot
    day_index: int
    parties: Dict[str, Party]
    factions: Dict[str, Faction]
    actors: Dict[str, Actor]
    player: Player
    constituencies: Dict[str, Constituency]
    institutions: Dict[str, Institution]
    relationships: Dict[str, Relationship]
    career: CareerState
    routine_items: List[RoutineItem]
    moments: List[Moment]
    daily_agenda: DailyAgenda
    event_log: List[str]
    active_story_arcs: List[StoryArc] = field(default_factory=list)
    current_result: str = ""
    recent_consequence: str = ""
    main_actions_used: int = 0
    minor_actions_used: int = 0

    def datetime_label(self) -> str:
        return f"{self.current_date.isoformat()} ({self.current_date.strftime('%A')}) - {self.time_slot.value}"
