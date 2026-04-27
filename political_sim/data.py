from __future__ import annotations

from typing import Dict, List

from .models import (
    Actor,
    Constituency,
    Decision,
    DecisionType,
    Faction,
    Institution,
    InstitutionType,
    Moment,
    MomentCategory,
    Party,
    PartyType,
    Relationship,
    Role,
    Urgency,
)


def _decision(
    id_: str,
    label: str,
    text: str,
    allowed: List[Role],
    d_type: DecisionType,
    effects: Dict[str, int],
    rel: Dict[str, int],
    career: Dict[str, int],
) -> Decision:
    return Decision(id=id_, label=label, description=text, decision_type=d_type, allowed_roles=allowed, effects=effects, relationship_effects=rel, career_effects=career, result_text=text)


def build_parties() -> Dict[str, Party]:
    return {
        "udp": Party("udp", "Union Democratic Party", PartyType.UNIONIST, "udp_leader", 62, 65, 58, 47, 55, 41, 56, 52, 48, 60, {
            "unionist_credibility": 64, "hardline_pressure": 55, "moderate_leakage": 38, "westminster_leverage": 50,
            "executive_stability": 44, "business_confidence": 49, "constitutional_pressure": 61,
        }),
        "rup": Party("rup", "Republican Unity Party", PartyType.REPUBLICAN, "rup_leader", 63, 66, 61, 50, 53, 40, 57, 50, 49, 62, {
            "republican_credibility": 67, "unity_momentum": 57, "northern_machine_strength": 62, "southern_growth": 56,
            "dublin_viability": 48, "legacy_pressure": 54, "stormont_stability": 45,
        }),
        "cap": Party("cap", "Civic Alliance Party", PartyType.CROSS_COMMUNITY, "cap_leader", 58, 59, 60, 56, 46, 34, 55, 47, 54, 52, {
            "cross_community_credibility": 66, "moderate_appeal": 60, "liberal_voter_energy": 58, "tactical_vote_pressure": 51,
            "both_sides_pressure": 49, "respectability": 62, "overextension_risk": 45,
        }),
    }


def build_constituencies() -> Dict[str, Constituency]:
    return {
        "east_belfast": Constituency("east_belfast", "East Belfast", 60, 17, 23, 54, 58, 20, 80, 49, 57, 53, "Bonfire route dispute", {"udp": 68, "rup": 25, "cap": 48}),
        "north_down": Constituency("north_down", "North Down", 37, 14, 49, 38, 71, 30, 70, 45, 62, 42, "Harbour redevelopment", {"udp": 46, "rup": 18, "cap": 64}),
        "fermanagh_south_tyrone": Constituency("fermanagh_south_tyrone", "Fermanagh and South Tyrone", 39, 43, 18, 64, 33, 72, 28, 57, 61, 48, "Cross-border farm grants", {"udp": 41, "rup": 63, "cap": 27}),
        "west_belfast": Constituency("west_belfast", "West Belfast", 11, 73, 16, 69, 36, 12, 86, 56, 54, 61, "Housing repair backlog", {"udp": 15, "rup": 74, "cap": 20}),
        "lagan_valley": Constituency("lagan_valley", "Lagan Valley", 56, 22, 22, 42, 61, 36, 59, 44, 59, 46, "Road safety complaints", {"udp": 59, "rup": 30, "cap": 39}),
    }


def build_factions() -> Dict[str, Faction]:
    factions = [
        ("udp_hardline", "udp", "Hardline Constitutionalists"), ("udp_governors", "udp", "Pragmatic Governors"), ("udp_social", "udp", "Social Conservatives"),
        ("udp_westminster", "udp", "Westminster Operators"), ("udp_bosses", "udp", "Local Bosses"), ("udp_modernisers", "udp", "Modernisers"),
        ("rup_old_guard", "rup", "Republican Old Guard"), ("rup_pragmatists", "rup", "Governing Pragmatists"), ("rup_left", "rup", "Left Social Republicans"),
        ("rup_southern", "rup", "Southern Electoral Machine"), ("rup_northern", "rup", "Northern Community Organisers"), ("rup_professional", "rup", "Modernising Professionals"),
        ("cap_liberal", "cap", "Liberal Professionals"), ("cap_local", "cap", "Local Government Builders"), ("cap_idealists", "cap", "Cross-Community Idealists"),
        ("cap_tactical", "cap", "Tactical Pragmatists"), ("cap_young", "cap", "Young Urban Wing"), ("cap_cautious", "cap", "Cautious Moderates"),
    ]
    out: Dict[str, Faction] = {}
    for fid, pid, name in factions:
        out[fid] = Faction(fid, pid, name, 50, 50, 42, 48, [DecisionType.COMPROMISE], [DecisionType.HARD_LINE if hasattr(DecisionType, 'HARD_LINE') else DecisionType.FACTIONAL])
    return out


def build_actors() -> Dict[str, Actor]:
    template = [
        ("leader", Role.MINISTER), ("senior", Role.MINISTER), ("mla", Role.MLA), ("councillor", Role.COUNCILLOR),
        ("adviser", Role.ADVISER), ("officer", Role.ADVISER), ("rival", Role.COUNCILLOR),
    ]
    parties = [("udp", "Union"), ("rup", "Republican"), ("cap", "Civic")]
    out: Dict[str, Actor] = {}
    for pid, stem in parties:
        for idx, (suffix, role) in enumerate(template, start=1):
            actor_id = f"{pid}_{suffix}"
            out[actor_id] = Actor(actor_id, f"{stem} {suffix.title()} {idx}", role, pid, "north_down", f"{pid}_{'local' if pid == 'cap' else 'governors' if pid == 'udp' else 'pragmatists'}", 45 + idx * 3, 45 + idx * 2, 40 + idx * 5, 55, 54, 50, 48, 45, 52, 38, 72, 35, 25 + idx * 4)
    return out


def build_institutions() -> Dict[str, Institution]:
    return {
        "council": Institution("council", "Council Chamber", InstitutionType.LOCAL_COUNCIL),
        "assembly": Institution("assembly", "Stormont Assembly", InstitutionType.ASSEMBLY),
        "hq": Institution("hq", "Party HQ", InstitutionType.PARTY_HQ),
        "media": Institution("media", "Local Media", InstitutionType.MEDIA),
    }


def build_relationships(player_id: str, player_party: str) -> Dict[str, Relationship]:
    return {
        "leader": Relationship(player_id, f"{player_party}_leader", "Party leader", 52),
        "local_branch": Relationship(player_id, f"branch_{player_party}", "Local branch", 51),
        "local_media": Relationship(player_id, "media_pool", "Local media", 48),
    }


def build_moments() -> List[Moment]:
    councillor_roles = [Role.COUNCILLOR]
    cand_roles = [Role.COUNCILLOR, Role.CANDIDATE]
    mla_roles = [Role.MLA]
    return [
        Moment("local_planning_row", "Local planning row", "A redevelopment plan has split residents and party organisers.", MomentCategory.CONSTITUENCY_WORK, Urgency.MEDIUM, councillor_roles, 2, [], [], "Local popularity vs party line.", [
            _decision("plan_party_line", "Back party line", "You defend the party's preferred scheme.", councillor_roles, DecisionType.PARTY_LINE, {"party.party_unity": 3, "player.local_base": -2, "constituency.local_issue_pressure": 2}, {"local_branch": 2}, {"career_momentum": 1}),
            _decision("plan_local", "Back residents", "You publicly side with residents against HQ pressure.", councillor_roles, DecisionType.LOCALIST, {"player.reputation": 3, "player.local_base": 4, "party.party_unity": -3}, {"leader": -3, "local_media": 2}, {"career_momentum": 1}),
            _decision("plan_compromise", "Broker compromise", "You secure amendments and calm the row.", councillor_roles, DecisionType.COMPROMISE, {"party.party_unity": 2, "player.reputation": 2, "constituency.local_media_heat": -2}, {"local_branch": 3}, {"career_momentum": 2}),
            _decision("plan_absent", "Stay absent", "You avoid blame but lose initiative.", councillor_roles, DecisionType.DEFENSIVE, {"player.reputation": -2, "player.stamina": 3}, {"local_branch": -2}, {"career_momentum": -1}),
        ], {"constituency.local_issue_pressure": 3, "player.local_base": -2, "rival.reputation": 2}, {"local_branch": -1}, "Rival councillor takes the lead on local anger.", "Your rival appears as the practical voice."),
        Moment("council_rebellion", "Council rebellion", "Councillors threaten to break whip over a rates vote.", MomentCategory.FORMAL_SESSION, Urgency.HIGH, councillor_roles, 1, [], [], "Discipline vs local credibility.", [
            _decision("rebellion_whip", "Enforce whip", "You push discipline and stop defections.", councillor_roles, DecisionType.PARTY_LINE, {"party.party_unity": 4, "player.local_base": -2}, {"leader": 3}, {"career_momentum": 1}),
            _decision("rebellion_rebels", "Side with rebels", "You join dissenters and attack HQ handling.", councillor_roles, DecisionType.FACTIONAL, {"party.party_unity": -4, "player.reputation": 3}, {"leader": -4, "local_branch": 2}, {"career_momentum": 1}),
            _decision("rebellion_compromise", "Broker compromise", "You reduce the rebellion without humiliation.", councillor_roles, DecisionType.COMPROMISE, {"party.party_unity": 2, "player.reputation": 2, "player.stamina": -8}, {"local_branch": 3, "leader": 1}, {"career_momentum": 2}),
            _decision("rebellion_absent", "Miss the vote", "You avoid direct blame and look weak.", councillor_roles, DecisionType.DEFENSIVE, {"player.reputation": -3, "party.party_unity": -1}, {"leader": -2}, {"career_momentum": -1}),
        ], {"party.party_unity": -4, "party.local_machine_strength": -2, "rival.reputation": 3}, {"leader": -2}, "Rebels claim your silence was consent.", "A rival briefs that you are unreliable in crunch votes."),
        Moment("local_media_interview", "Local media interview", "A regional outlet offers you a live interview slot.", MomentCategory.MEDIA, Urgency.MEDIUM, cand_roles, 2, [], [], "Profile boost vs gaffe risk.", [
            _decision("media_safe", "Play it safe", "You stick to disciplined lines.", cand_roles, DecisionType.DEFENSIVE, {"player.media_profile": 1, "party.media_pressure": -1}, {"local_media": 1}, {"career_momentum": 1}),
            _decision("media_bold", "Go bold", "You make a sharp argument to stand out.", cand_roles, DecisionType.PROFILE_BUILDING, {"player.media_profile": 3, "player.reputation": 1, "party.scandal_risk": 2}, {"local_media": 2, "leader": -1}, {"career_momentum": 2}),
        ], {"player.media_profile": -1, "constituency.local_media_heat": 1, "rival.reputation": 2}, {"local_media": -1}, "Rival councillor takes your interview slot.", "The rival's profile grows from your absence."),
        Moment("candidate_selection_opening", "Candidate selection opening", "A shortlist opens for an Assembly seat.", MomentCategory.CAREER_OPPORTUNITY, Urgency.HIGH, councillor_roles, 2, [], [], "Branch support vs HQ preference.", [
            _decision("selection_branch", "Build branch coalition", "You spend influence on local endorsements.", councillor_roles, DecisionType.CAREER, {"player.local_base": 3, "player.influence": -4}, {"local_branch": 4}, {"career_momentum": 2}),
            _decision("selection_hq", "Court party HQ", "You focus on leadership backing.", councillor_roles, DecisionType.LOYALIST, {"player.party_trust": 3, "player.influence": -3}, {"leader": 3, "local_branch": -2}, {"career_momentum": 1}),
        ], {"player.career_momentum": -1, "rival.reputation": 3}, {"local_branch": -2}, "Your rival secures early signatures.", "HQ hears your name less often."),
        Moment("faction_dinner", "Faction dinner invitation", "A faction invites you to a private dinner briefing.", MomentCategory.BACKROOM_POLITICS, Urgency.MEDIUM, [Role.COUNCILLOR, Role.MLA], 1, [], [], "Build faction links vs alienate others.", [
            _decision("dinner_attend", "Attend dinner", "You build links with that faction.", [Role.COUNCILLOR, Role.MLA], DecisionType.FACTIONAL, {"player.influence": 2}, {"leader": -1}, {"career_momentum": 1}),
            _decision("dinner_decline", "Decline politely", "You avoid internal labels.", [Role.COUNCILLOR, Role.MLA], DecisionType.DEFENSIVE, {"player.reputation": 1}, {"leader": 0}, {"career_momentum": 0}),
        ], {"rival.influence": 2}, {"leader": -1}, "Rival builds faction backing while you stay outside.", "Faction whispers now include your rival, not you."),
        Moment("rival_handles_issue", "Rival councillor handles issue", "A neglected constituency complaint is resolved by a rival.", MomentCategory.RELATIONSHIP_REACTION, Urgency.LOW, councillor_roles, 1, [], [], "Ignored moments can empower rivals.", [
            _decision("rival_counter", "Re-engage fast", "You meet residents and recover some ground.", councillor_roles, DecisionType.LOCALIST, {"player.local_base": 2, "rival.reputation": -1}, {"local_branch": 1}, {"career_momentum": 1}),
            _decision("rival_ignore", "Let it pass", "You accept short-term loss.", councillor_roles, DecisionType.DEFENSIVE, {"player.local_base": -2, "rival.reputation": 1}, {"local_branch": -1}, {"career_momentum": -1}),
        ], {"rival.reputation": 2, "player.local_base": -2}, {"local_branch": -1}, "Rival becomes branch go-to fixer.", "System rewards visible doers."),
        Moment("assembly_campaign_launch", "Assembly campaign launch", "Your campaign message must be locked in.", MomentCategory.CAMPAIGN, Urgency.HIGH, [Role.CANDIDATE], 1, [], [], "Broad appeal vs activist energy.", [
            _decision("campaign_broad", "Broad appeal launch", "Centrist messaging to widen support.", [Role.CANDIDATE], DecisionType.COMPROMISE, {"party.public_trust": 2, "player.reputation": 2}, {"local_media": 1}, {"career_momentum": 1}),
            _decision("campaign_base", "Base mobilisation launch", "Sharper message to energise activists.", [Role.CANDIDATE], DecisionType.PROFILE_BUILDING, {"party.activist_morale": 3, "party.public_trust": -1, "player.reputation": 2}, {"local_branch": 2}, {"career_momentum": 2}),
        ], {"player.reputation": -2, "rival.reputation": 2}, {"local_media": -1}, "Rival campaign defines the opening frame.", "You enter the race on the back foot."),
        Moment("debate_night", "Debate night pressure", "Debate prep team asks whether to stay cautious or attack.", MomentCategory.CAMPAIGN, Urgency.HIGH, [Role.CANDIDATE], 1, [], [], "Safe answers vs bold statement.", [
            _decision("debate_safe", "Safe discipline", "Avoid errors and stay message-tight.", [Role.CANDIDATE], DecisionType.DEFENSIVE, {"party.scandal_risk": -2, "player.media_profile": 1}, {"leader": 1}, {"career_momentum": 1}),
            _decision("debate_bold", "Bold intervention", "Take a risk to dominate coverage.", [Role.CANDIDATE], DecisionType.PROFILE_BUILDING, {"player.media_profile": 3, "party.scandal_risk": 2}, {"local_media": 2}, {"career_momentum": 2}),
        ], {"player.media_profile": -1, "rival.reputation": 2}, {"leader": -1}, "Opponent dominates headlines.", "Missed spotlight hurts momentum."),
        Moment("election_result", "Election result", "Result night determines whether you reach the Assembly.", MomentCategory.CAREER_OPPORTUNITY, Urgency.CRITICAL, [Role.CANDIDATE], 1, [], [], "Win seat, narrow loss, or list role.", [
            _decision("result_claim", "Claim mandate", "You present the result as legitimacy for bigger role.", [Role.CANDIDATE], DecisionType.CAREER, {"player.reputation": 4, "player.party_trust": 2}, {"leader": 1}, {"career_momentum": 3}),
        ], {"player.reputation": -2}, {"leader": -1}, "Party lists move without your input.", "Narrative control goes elsewhere."),
        Moment("first_assembly_vote", "First Assembly vote", "Whips demand support on a difficult vote.", MomentCategory.FORMAL_SESSION, Urgency.HIGH, mla_roles, 1, [], [], "Follow whip vs independent profile.", [
            _decision("vote_whip", "Follow whip", "You reinforce trust with leadership.", mla_roles, DecisionType.LOYALIST, {"player.leader_trust": 3, "party.party_unity": 2}, {"leader": 3}, {"career_momentum": 1}),
            _decision("vote_independent", "Signal independence", "You dissent carefully to build identity.", mla_roles, DecisionType.LOCALIST, {"player.reputation": 2, "player.leader_trust": -3, "party.party_unity": -2}, {"local_media": 1}, {"career_momentum": 1}),
        ], {"player.leader_trust": -2, "rival.influence": 2}, {"leader": -2}, "Whips note your absence.", "Trust falls in private tallies."),
        Moment("party_crisis_briefing", "Party crisis briefing", "A scandal puts leadership under intense pressure.", MomentCategory.CRISIS, Urgency.CRITICAL, [Role.MLA, Role.ADVISER, Role.JUNIOR_MINISTER], 1, [], [], "Defend leader, stay quiet, or brief faction.", [
            _decision("crisis_defend", "Defend leader", "You front the media and hold the line.", [Role.MLA, Role.ADVISER, Role.JUNIOR_MINISTER], DecisionType.LOYALIST, {"player.leader_trust": 4, "party.government_credibility": 1, "player.stamina": -6}, {"leader": 4}, {"career_momentum": 1}),
            _decision("crisis_quiet", "Stay quiet", "You avoid direct ownership of the row.", [Role.MLA, Role.ADVISER, Role.JUNIOR_MINISTER], DecisionType.DEFENSIVE, {"player.reputation": -1}, {"leader": -2}, {"career_momentum": -1}),
            _decision("crisis_brief", "Brief your faction", "You protect faction interests over public discipline.", [Role.MLA, Role.ADVISER, Role.JUNIOR_MINISTER], DecisionType.FACTIONAL, {"party.party_unity": -3, "player.influence": 2}, {"leader": -4}, {"career_momentum": 1}),
        ], {"player.leader_trust": -3, "party.faction_pressure": 2}, {"leader": -3}, "Leadership marks you as unreliable under fire.", "Rivals frame themselves as steadier hands."),
        Moment("junior_minister_offer", "Junior minister offer", "Leadership considers you for a junior ministry.", MomentCategory.CAREER_OPPORTUNITY, Urgency.HIGH, [Role.MLA], 2, [], [], "Take office and lose freedom, or stay independent.", [
            _decision("offer_accept", "Accept office", "You gain formal power with tighter discipline.", [Role.MLA], DecisionType.CAREER, {"player.influence": 6, "player.party_trust": 3, "player.reputation": 2}, {"leader": 3}, {"career_momentum": 2}),
            _decision("offer_decline", "Decline and stay independent", "You keep freedom but risk leadership trust.", [Role.MLA], DecisionType.DEFENSIVE, {"player.reputation": 1, "player.leader_trust": -3}, {"leader": -3}, {"career_momentum": 1}),
        ], {"player.leader_trust": -2}, {"leader": -2}, "Leadership looks elsewhere for loyal ministers.", "A rival gets fast-tracked into office."),
    ]
