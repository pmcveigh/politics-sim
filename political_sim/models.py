from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Dict, List, Optional


class TimeSlot(str, Enum):
    MORNING = "Morning"
    AFTERNOON = "Afternoon"
    EVENING = "Evening"
    LATE_NIGHT = "Late Night"


class BeatType(str, Enum):
    EMAIL_CHECK = "Email Check"
    EMAIL_TRIAGE = "Email Triage"
    PHONE_CALL = "Phone Call"
    RESIDENT_MEETING = "Resident Meeting"
    SITE_VISIT = "Site Visit"
    OFFICER_MEETING = "Officer Meeting"
    MEDIA_REQUEST = "Media Request"
    SOCIAL_MEDIA_POST = "Social Media Post"
    COMMUNITY_EVENT = "Community Event"
    CAMPAIGN_SESSION = "Campaign Session"
    COUNCIL_VOTE = "Council Vote"
    PARTY_STRATEGY_MEETING = "Party Strategy Meeting"
    FALLOUT = "Fallout"


class BeatStatus(str, Enum):
    OPEN = "Open"
    RESOLVED = "Resolved"
    IGNORED = "Ignored"
    TAKEN_BY_RIVAL = "Taken by Rival"


class StoryStatus(str, Enum):
    ACTIVE = "Active"
    RESOLVED = "Resolved"
    FALLOUT = "Fallout"


class Role(str, Enum):
    COUNCILLOR = "Councillor"
    CANDIDATE = "Candidate"
    MLA = "MLA"
    JUNIOR_MINISTER = "Junior Minister"


@dataclass
class GameDate:
    value: date

    def add_days(self, days: int = 1) -> "GameDate":
        from datetime import timedelta

        return GameDate(self.value + timedelta(days=days))


@dataclass
class DayTemplate:
    id: str
    title: str
    slot_beats: Dict[TimeSlot, List[str]]


@dataclass
class DecisionOption:
    id: str
    label: str
    explanation: str
    likely_upside: str
    likely_risk: str
    stamina_cost: int
    influence_cost: int
    effects: Dict[str, int]
    flags_set: List[str] = field(default_factory=list)
    possible_actor_reactions: List[str] = field(default_factory=list)
    next_beats: List[str] = field(default_factory=list)
    consequence_text: str = ""


@dataclass
class ActorReaction:
    actor_id: str
    text: str
    relationship_effects: Dict[str, int] = field(default_factory=dict)


@dataclass
class FollowUp:
    id: str
    story_arc_id: str
    due_date: date
    time_slot: TimeSlot
    beat_id: str


@dataclass
class DailyBeat:
    id: str
    title: str
    description: str
    time_slot: TimeSlot
    beat_type: BeatType
    linked_story_arc_id: Optional[str]
    involved_actor_ids: List[str]
    decision_options: List[DecisionOption]
    ignored_effect: Dict[str, int]
    status: BeatStatus
    urgency: str
    expiry: int
    short_risk_preview: str


@dataclass
class ContentPack:
    id: str
    issue_type: str
    typical_actors: List[str]
    common_risks: List[str]
    common_rewards: List[str]
    possible_beats: List[str]
    likely_followups: List[str]
    suitable_day_templates: List[str]
    tone_text: str


@dataclass
class StoryArc:
    id: str
    title: str
    theme: str
    status: StoryStatus
    current_stage: int
    linked_constituency_id: str
    involved_actor_ids: List[str]
    pressure_level: int
    public_visibility: int
    player_ownership: int
    rival_ownership: int
    flags: Dict[str, bool] = field(default_factory=dict)
    scheduled_followups: List[FollowUp] = field(default_factory=list)
    outcome_tags: List[str] = field(default_factory=list)


@dataclass
class Actor:
    id: str
    name: str
    role: str
    relationship: int


@dataclass
class Party:
    id: str
    name: str


@dataclass
class Faction:
    id: str
    name: str
    pressure: int


@dataclass
class Constituency:
    id: str
    name: str
    flashpoint: str


@dataclass
class Institution:
    id: str
    name: str


@dataclass
class Relationship:
    id: str
    label: str
    score: int


@dataclass
class CareerState:
    current_role: Role = Role.COUNCILLOR
    path: List[Role] = field(default_factory=lambda: [Role.COUNCILLOR, Role.CANDIDATE, Role.MLA, Role.JUNIOR_MINISTER])
    assembly_selection_open: bool = False


@dataclass
class Player:
    id: str
    name: str
    party_id: str
    constituency_id: str
    stamina: int = 80
    influence: int = 25
    reputation: int = 48
    local_base: int = 46
    branch_support: int = 50
    career_momentum: int = 2
    resident_trust: int = 50
    ward_visibility: int = 40
    rival_threat: int = 40


@dataclass
class DailyAgenda:
    date: date
    template_id: str
    beats_by_slot: Dict[TimeSlot, List[str]] = field(default_factory=dict)


@dataclass
class SimulationState:
    game_date: GameDate
    current_slot: TimeSlot
    day_index: int
    player: Player
    party: Party
    factions: Dict[str, Faction]
    constituency: Constituency
    institutions: Dict[str, Institution]
    actors: Dict[str, Actor]
    relationships: Dict[str, Relationship]
    active_story_arcs: Dict[str, StoryArc]
    content_packs: Dict[str, ContentPack]
    day_templates: Dict[str, DayTemplate]
    career: CareerState
    daily_agenda: DailyAgenda
    daily_beats: Dict[str, DailyBeat]
    followups: List[FollowUp] = field(default_factory=list)
    event_log: List[str] = field(default_factory=list)
    recent_consequence: str = ""
    current_result: str = ""
    main_action_taken: bool = False
