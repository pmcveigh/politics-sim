from __future__ import annotations

from typing import Dict, List

from .models import (
    Actor,
    BeatType,
    Constituency,
    ContentPack,
    DayTemplate,
    DecisionOption,
    Faction,
    Institution,
    Party,
    Relationship,
    TimeSlot,
)


def build_party() -> Party:
    return Party(id="civic", name="Civic Alliance Party")


def build_factions() -> Dict[str, Faction]:
    return {
        "localists": Faction("localists", "Ward Localists", 52),
        "organisers": Faction("organisers", "Branch Organisers", 48),
    }


def build_constituency() -> Constituency:
    return Constituency(id="harbour", name="Harbour and Lough", flashpoint="Road safety near the old junction")


def build_institutions() -> Dict[str, Institution]:
    return {
        "council": Institution("council", "Borough Council"),
        "branch": Institution("branch", "Local Branch"),
    }


def build_actors() -> Dict[str, Actor]:
    return {
        "rival": Actor("rival", "Jordan Keenan", "Rival Councillor", 40),
        "officer": Actor("officer", "Sam O'Neill", "Council Officer", 50),
        "journalist": Actor("journalist", "Aisling Ward", "Local Journalist", 50),
        "party_figure": Actor("party_figure", "Riley Porter", "Party Group Organiser", 50),
        "residents_contact": Actor("residents_contact", "Moira Boyd", "Residents' Association Contact", 52),
    }


def build_relationships() -> Dict[str, Relationship]:
    return {
        "rival": Relationship("rival", "Main Rival Councillor", 38),
        "officer": Relationship("officer", "Roads and Neighbourhood Officer", 49),
        "journalist": Relationship("journalist", "Local Journalist", 50),
        "party_figure": Relationship("party_figure", "Party Group Organiser", 50),
        "residents_contact": Relationship("residents_contact", "Residents' Association", 53),
    }


def build_day_templates() -> Dict[str, DayTemplate]:
    return {
        "admin": DayTemplate("admin", "Admin-heavy day", {
            TimeSlot.MORNING: ["email_check", "email_triage"],
            TimeSlot.AFTERNOON: ["officer_meeting", "resident_meeting"],
            TimeSlot.EVENING: ["party_strategy_meeting"],
            TimeSlot.LATE_NIGHT: ["fallout"],
        }),
        "crisis": DayTemplate("crisis", "Crisis-interrupt day", {
            TimeSlot.MORNING: ["email_check", "phone_call"],
            TimeSlot.AFTERNOON: ["site_visit", "officer_meeting"],
            TimeSlot.EVENING: ["media_request", "council_vote"],
            TimeSlot.LATE_NIGHT: ["fallout"],
        }),
        "campaign": DayTemplate("campaign", "Campaign day", {
            TimeSlot.MORNING: ["party_strategy_meeting", "campaign_session"],
            TimeSlot.AFTERNOON: ["email_triage", "officer_meeting"],
            TimeSlot.EVENING: ["campaign_session", "resident_meeting"],
            TimeSlot.LATE_NIGHT: ["fallout"],
        }),
        "council": DayTemplate("council", "Council day", {
            TimeSlot.MORNING: ["email_check", "officer_meeting"],
            TimeSlot.AFTERNOON: ["council_vote"],
            TimeSlot.EVENING: ["media_request", "social_media_post"],
            TimeSlot.LATE_NIGHT: ["fallout"],
        }),
        "community": DayTemplate("community", "Community day", {
            TimeSlot.MORNING: ["email_check"],
            TimeSlot.AFTERNOON: ["community_event", "media_request"],
            TimeSlot.EVENING: ["resident_meeting", "social_media_post"],
            TimeSlot.LATE_NIGHT: ["fallout"],
        }),
    }


def build_content_packs() -> Dict[str, ContentPack]:
    return {
        "car_accident": ContentPack(
            id="car_accident",
            issue_type="Car accident hotspot",
            typical_actors=["officer", "journalist", "residents_contact", "rival"],
            common_risks=["Going public before facts", "Rival steals ownership"],
            common_rewards=["Residents feel heard", "Officer confidence improves"],
            possible_beats=["phone_call", "site_visit", "media_request"],
            likely_followups=["officer_meeting", "resident_meeting", "council_vote"],
            suitable_day_templates=["crisis", "council"],
            tone_text="A serious local safety issue with emotional resident pressure.",
        ),
        "noise_complaint": ContentPack(
            id="noise_complaint",
            issue_type="Noise complaint",
            typical_actors=["residents_contact", "officer", "rival", "journalist"],
            common_risks=["Appearing one-sided", "Business backlash"],
            common_rewards=["Balanced mediation", "Trust from both sides"],
            possible_beats=["resident_meeting", "officer_meeting", "media_request"],
            likely_followups=["social_media_post", "resident_meeting"],
            suitable_day_templates=["admin", "community"],
            tone_text="A personal dispute that can become public quickly.",
        ),
        "campaign_help": ContentPack(
            id="campaign_help",
            issue_type="Campaign help request",
            typical_actors=["party_figure", "rival", "residents_contact"],
            common_risks=["Neglecting ward issues", "Branch doubts reliability"],
            common_rewards=["Branch approval", "Candidate support"],
            possible_beats=["party_strategy_meeting", "campaign_session", "resident_meeting"],
            likely_followups=["campaign_session", "fallout"],
            suitable_day_templates=["campaign"],
            tone_text="Party pressure collides with local councillor duties.",
        ),
    }


def decision_library() -> Dict[str, List[DecisionOption]]:
    return {
        "car_phone_call": [
            DecisionOption("go_scene", "Go to the scene personally", "Attend immediately and speak with residents.", "Higher resident trust and visibility.", "Stamina drain and media pressure.", 12, 1, {"player.resident_trust": 4, "player.ward_visibility": 3}, ["visited_scene"], ["residents_contact"], ["site_visit"], "You arrive quickly and residents note that you turned up in person."),
            DecisionOption("call_officer_first", "Call the roads officer and PSNI contact first", "Seek facts before public comment.", "Safer information and better officer trust.", "Slower visible response.", 5, 1, {"relationship.officer": 3, "player.resident_trust": 1}, ["contacted_officer_first"], ["officer"], ["officer_meeting"], "You gather the collision history and request a technical update."),
            DecisionOption("post_immediately", "Issue a public statement immediately", "Publish before full facts are known.", "Visibility surge and online engagement.", "Accusations of opportunism.", 4, 2, {"player.ward_visibility": 5, "relationship.officer": -2, "relationship.journalist": -1}, ["posted_before_facts", "gave_media_quote"], ["journalist"], ["media_request"], "Your post spreads quickly, but questions about accuracy follow."),
            DecisionOption("log_later", "Log it for later and continue planned work", "Keep routine commitments first.", "Preserves stamina for the day.", "Rival may intervene and gain credit.", 0, 0, {"player.stamina": 2, "player.rival_threat": 4}, [], ["rival"], [], "You defer the issue and trust routine channels to hold for now."),
        ],
        "noise_meeting": [
            DecisionOption("meet_resident", "Meet the resident first", "Hear immediate impact in person.", "Resident trust improves.", "Business owner may feel blamed.", 8, 1, {"relationship.residents_contact": 2, "player.resident_trust": 3}, ["met_resident"], [], ["officer_meeting"], "The resident describes sleepless nights and asks for urgent action."),
            DecisionOption("hear_both", "Arrange both sides and hear both", "Bring resident and business owner to the same table.", "Balanced credibility.", "Takes longer and may frustrate both sides.", 10, 2, {"player.reputation": 2, "relationship.officer": 1}, ["met_resident", "met_business_owner", "heard_both_sides"], [], ["media_request"], "The meeting is tense but you avoid taking a public side too early."),
            DecisionOption("blame_business", "Blame the business publicly", "Take a hard public line.", "Short-term applause from angry residents.", "Business and officer backlash.", 5, 2, {"relationship.residents_contact": 1, "relationship.officer": -2}, ["blamed_business_publicly"], ["journalist"], ["social_media_post"], "Your comments spread online and the dispute becomes political."),
        ],
        "campaign_request": [
            DecisionOption("promise_help", "Promise evening campaign help", "Commit to canvassing support.", "Branch sees loyalty and effort.", "Ward casework may slip.", 9, 2, {"relationship.party_figure": 3, "player.career_momentum": 2}, ["promised_to_help", "helped_candidate"], ["party_figure"], ["campaign_session"], "The organiser thanks you and books you onto a tough evening patch."),
            DecisionOption("decline_help", "Decline and prioritise ward duties", "Protect local routine commitments.", "Residents appreciate focus.", "Branch may mark you unreliable.", 2, 0, {"player.resident_trust": 2, "relationship.party_figure": -2}, [], ["party_figure"], ["resident_meeting"], "You keep your ward diary intact but party murmurs begin."),
        ],
    }


def beat_type_from_id(beat_id: str) -> BeatType:
    mapping = {
        "email_check": BeatType.EMAIL_CHECK,
        "email_triage": BeatType.EMAIL_TRIAGE,
        "phone_call": BeatType.PHONE_CALL,
        "resident_meeting": BeatType.RESIDENT_MEETING,
        "site_visit": BeatType.SITE_VISIT,
        "officer_meeting": BeatType.OFFICER_MEETING,
        "media_request": BeatType.MEDIA_REQUEST,
        "social_media_post": BeatType.SOCIAL_MEDIA_POST,
        "community_event": BeatType.COMMUNITY_EVENT,
        "campaign_session": BeatType.CAMPAIGN_SESSION,
        "council_vote": BeatType.COUNCIL_VOTE,
        "party_strategy_meeting": BeatType.PARTY_STRATEGY_MEETING,
        "fallout": BeatType.FALLOUT,
    }
    return mapping[beat_id]
