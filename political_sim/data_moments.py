from __future__ import annotations

from copy import deepcopy
from typing import Dict, List

from .models import Decision, DecisionType, Moment, MomentCategory, PartyType, Role, TimeSlot, Urgency

ALL_ROLES = list(Role)
LOWER_ROLES = [Role.ACTIVIST, Role.COUNCILLOR, Role.CANDIDATE]
SENIOR_ROLES = [Role.MLA, Role.ADVISER, Role.JUNIOR_MINISTER, Role.MINISTER]
MINISTERIAL_ROLES = [Role.JUNIOR_MINISTER, Role.MINISTER]


def _decision(
    decision_id: str,
    label: str,
    description: str,
    roles: List[Role],
    decision_type: DecisionType,
    stamina_cost: int,
    influence_cost: int,
    risk_level: int,
    effects: Dict[str, int],
    consequence: str,
    relationship_effects: Dict[str, int] | None = None,
    career_effects: Dict[str, int] | None = None,
    time_advance: int = 1,
) -> Decision:
    return Decision(
        id=decision_id,
        label=label,
        description=description,
        required_roles=roles,
        decision_type=decision_type,
        influence_cost=influence_cost,
        stamina_cost=stamina_cost,
        risk_level=risk_level,
        effects=effects,
        relationship_effects=relationship_effects or {},
        career_effects=career_effects or {},
        consequence_text=consequence,
        time_advance=time_advance,
    )


def fallback_decisions(prefix: str) -> List[Decision]:
    return [
        _decision(f"{prefix}_quiet", "Stay quiet", "Avoid taking a visible stance.", ALL_ROLES, DecisionType.STAY_QUIET, 2, 0, 25, {"player.party_trust": -1, "player.stamina": 2}, "You stay out of the row and conserve energy."),
        _decision(f"{prefix}_lobby", "Lobby privately", "Phone trusted contacts and shape the tone from the side.", ALL_ROLES, DecisionType.LOBBY, 6, 2, 35, {"player.influence": 1, "player.faction_support": 1}, "Your quiet lobbying shifts a few minds.", {"faction:player_faction": 2}),
        _decision(f"{prefix}_brief", "Brief ally", "Give a friendly actor your preferred line.", ALL_ROLES, DecisionType.BRIEFING, 5, 1, 30, {"player.party_trust": 1, "player.media_profile": 1}, "An ally repeats your line in public."),
        _decision(f"{prefix}_leak", "Leak to friendly contact", "Push selective detail to influence coverage.", ALL_ROLES, DecisionType.LEAK, 8, 3, 55, {"party.media_pressure": -1, "player.reputation": -1, "player.media_profile": 2}, "The leak lands, but people suspect your hand."),
        _decision(f"{prefix}_support", "Support official line", "Back the party position in local conversations.", ALL_ROLES, DecisionType.SUPPORT, 6, 1, 20, {"player.party_trust": 2, "party.party_unity": 1}, "You help keep discipline."),
        _decision(f"{prefix}_oppose", "Oppose official line locally", "Signal disagreement without open rebellion.", LOWER_ROLES + [Role.MLA], DecisionType.OPPOSE, 7, 2, 60, {"player.faction_support": 2, "party.party_unity": -2, "player.party_trust": -2}, "Dissenters applaud you; loyalists do not."),
        _decision(f"{prefix}_constituency", "Focus on constituency work", "Leave the party row and solve local problems.", ALL_ROLES, DecisionType.LOCAL_WORK, 5, 0, 15, {"player.local_base": 2, "constituency.local_issue_pressure": -2}, "Constituents notice practical work.", time_advance=0),
    ]


def _moment_template(
    template_id: str,
    party_type: PartyType,
    title: str,
    description: str,
    category: MomentCategory,
    urgency: Urgency,
    institution_tags: List[str],
    faction_tags: List[str],
    pressure_requirements: Dict[str, int],
    involved_actors: List[str],
    role_decisions: List[Decision],
    ignored_effect: str,
    consequence_summary: str,
    expires_after_slots: int = 2,
    can_escalate: bool = True,
) -> Dict:
    return {
        "id": template_id,
        "party_type": party_type,
        "title": title,
        "description": description,
        "category": category,
        "urgency": urgency,
        "institution_tags": institution_tags,
        "faction_tags": faction_tags,
        "pressure_requirements": pressure_requirements,
        "involved_actors": involved_actors,
        "decision_options": role_decisions + fallback_decisions(template_id),
        "ignored_effect": ignored_effect,
        "consequence_summary": consequence_summary,
        "expires_after_slots": expires_after_slots,
        "can_escalate": can_escalate,
    }


def build_moment_templates() -> List[Dict]:
    moments: List[Dict] = []

    # DUP-style moments
    moments.append(_moment_template("dup_constitutional_pressure", PartyType.DUP_STYLE, "Constitutional pressure spike", "A row over identity symbols and post-Brexit checks fuels internal anger.", MomentCategory.CONSTITUTIONAL, Urgency.HIGH, ["party_executive", "media"], ["Hardline Constitutionalists", "Modernisers"], {"party.custom.constitutional_pressure": 60}, ["udf_leader", "udf_rival"], [
        _decision("dup_constitutional_min_hard", "Take a hard public line", "Frame the issue as a red line in every interview.", MINISTERIAL_ROLES, DecisionType.HARD_LINE, 12, 8, 62, {"party.custom.unionist_credibility": 4, "party.custom.executive_stability": -3, "party.media_pressure": 2}, "Your language satisfies hardliners and alarms pragmatists."),
        _decision("dup_constitutional_min_comp", "Push compromise inside the Executive", "Seek a face-saving adjustment with partners.", MINISTERIAL_ROLES, DecisionType.COMPROMISE, 11, 8, 50, {"party.custom.executive_stability": 4, "party.custom.hardline_pressure": 2, "party.public_trust": 1}, "You lower immediate heat but invite flank criticism."),
        _decision("dup_constitutional_council_echo", "Echo the hard line locally", "Reinforce branch anger in council media.", [Role.COUNCILLOR, Role.CANDIDATE], DecisionType.HARD_LINE, 8, 3, 54, {"player.local_base": 2, "party.custom.hardline_pressure": 2, "party.public_trust": -1}, "The local base cheers your stance."),
        _decision("dup_constitutional_activist_branch", "Push branch pressure", "Organise a branch motion demanding tougher language.", [Role.ACTIVIST], DecisionType.LOBBY, 8, 1, 48, {"player.faction_support": 3, "party.custom.hardline_pressure": 3}, "The motion passes and reaches senior desks."),
    ], "A rival frames your silence as weakness and gains branch credit.", "Unionist credibility and executive stability pull against each other."))

    moments.append(_moment_template("dup_donor_warning", PartyType.DUP_STYLE, "Business donors warn over instability", "A group of donors say repeated crises are hurting investment confidence.", MomentCategory.GOVERNANCE, Urgency.MEDIUM, ["media", "party_executive"], ["Pragmatic Governors", "Hardline Constitutionalists"], {"party.custom.business_confidence": 45}, ["udf_senior_min", "udf_adviser"], [
        _decision("dup_donor_reassure", "Offer a stability briefing", "Promise practical delivery and fewer rows.", SENIOR_ROLES, DecisionType.BRIEFING, 9, 5, 38, {"party.custom.business_confidence": 4, "party.government_credibility": 2, "party.custom.hardline_pressure": 1}, "Donors calm down, though some activists grumble."),
        _decision("dup_donor_attack", "Attack donor meddling", "Say elected politics should not bend to donor pressure.", [Role.MLA, Role.CANDIDATE, Role.COUNCILLOR], DecisionType.HARD_LINE, 7, 3, 58, {"party.activist_morale": 2, "party.custom.business_confidence": -3}, "You excite activists and spook business voices."),
    ], "A rival spokesperson takes the donor call and gains profile.", "Governing credibility is traded against base suspicion."))

    moments.append(_moment_template("dup_selection_fight", PartyType.DUP_STYLE, "Candidate selection fight", "Local organisers back a loyal operator while headquarters wants a polished media performer.", MomentCategory.CANDIDATE_SELECTION, Urgency.HIGH, ["party_executive"], ["Local Bosses", "Modernisers"], {"party.local_machine_strength": 55}, ["udf_officer", "udf_rival"], [
        _decision("dup_selection_local", "Back the loyal organiser", "Argue that turnout machinery matters more than polish.", [Role.COUNCILLOR, Role.ACTIVIST, Role.CANDIDATE], DecisionType.SUPPORT, 8, 4, 45, {"party.local_machine_strength": 3, "party.public_trust": -1, "player.local_base": 2}, "Branch veterans line up behind you."),
        _decision("dup_selection_hq", "Back HQ candidate", "Push for wider appeal and media readiness.", SENIOR_ROLES, DecisionType.COMPROMISE, 9, 5, 50, {"party.public_trust": 2, "party.local_machine_strength": -2, "player.party_trust": 1}, "HQ appreciates the backing; local bosses resent it."),
    ], "The selection closes without you, and your rival claims the winning side.", "Local machine strength clashes with broader appeal."))

    moments.append(_moment_template("dup_social_gaffe", PartyType.DUP_STYLE, "Social conservative media gaffe", "A traditionalist figure makes comments that trigger a hostile media cycle.", MomentCategory.MEDIA, Urgency.HIGH, ["media"], ["Social Conservatives", "Modernisers"], {"party.media_pressure": 55}, ["udf_mla", "udf_adviser"], [
        _decision("dup_gaffe_defend", "Defend the figure", "Say opponents are distorting sincere views.", [Role.ACTIVIST, Role.COUNCILLOR, Role.CANDIDATE], DecisionType.HARD_LINE, 8, 3, 60, {"party.activist_morale": 2, "party.public_trust": -3, "player.media_profile": 1}, "The base rallies while broadcasters push harder."),
        _decision("dup_gaffe_distance", "Distance the party line", "Issue a careful statement and shift to service delivery.", SENIOR_ROLES, DecisionType.DISCIPLINE, 10, 5, 42, {"party.public_trust": 2, "party.party_unity": -1, "party.media_pressure": -1}, "The story cools but internal complaints rise."),
    ], "The local paper runs the story without your quote and frames you as evasive.", "Base loyalty and public trust move in opposite directions."))

    moments.append(_moment_template("dup_delivery_crisis", PartyType.DUP_STYLE, "Stormont delivery crisis", "A department under your party loses control of waiting times.", MomentCategory.DELIVERY, Urgency.CRITICAL, ["executive_department", "civil_service", "media"], ["Pragmatic Governors", "Hardline Constitutionalists"], {"party.government_credibility": 45}, ["udf_senior_min", "udf_adviser"], [
        _decision("dup_delivery_fix", "Own the failure and publish a rescue plan", "Take responsibility and set measurable milestones.", MINISTERIAL_ROLES + [Role.ADVISER], DecisionType.DISCIPLINE, 13, 9, 40, {"party.government_credibility": 4, "party.public_trust": 2, "party.party_unity": -1}, "Civil servants align behind your plan."),
        _decision("dup_delivery_blame", "Blame institutional obstruction", "Argue that blocked structures caused the collapse.", [Role.MLA, Role.COUNCILLOR, Role.CANDIDATE], DecisionType.HARD_LINE, 9, 4, 57, {"party.custom.unionist_credibility": 2, "party.government_credibility": -3, "party.custom.executive_stability": -2}, "Supporters nod, but service users remain furious."),
    ], "Another party actor steps in and appears more competent than you.", "Service delivery pressure competes with the instinct to shift blame."))

    moments.append(_moment_template("dup_westminster_leverage", PartyType.DUP_STYLE, "Westminster leverage opportunity", "A UK minister seeks your party's public backing on a tight vote.", MomentCategory.CONSTITUTIONAL, Urgency.MEDIUM, ["party_executive", "media"], ["Westminster Operators", "Hardline Constitutionalists"], {"party.custom.westminster_leverage": 50}, ["udf_adviser", "udf_leader"], [
        _decision("dup_westminster_extract", "Demand visible concessions", "Set clear asks before any support.", SENIOR_ROLES, DecisionType.LOBBY, 10, 7, 45, {"party.custom.westminster_leverage": 4, "party.custom.unionist_credibility": 2}, "You extract movement, but trust remains thin."),
        _decision("dup_westminster_refuse", "Refuse involvement", "Avoid looking like a junior partner to London.", [Role.MLA, Role.COUNCILLOR, Role.CANDIDATE, Role.ACTIVIST], DecisionType.OPPOSE, 7, 3, 52, {"party.custom.westminster_leverage": -3, "party.custom.hardline_pressure": 2}, "Hardliners are pleased by defiance."),
    ], "A rival negotiates first and claims the Westminster contacts.", "Concessions can be won, but appearing used carries political cost."))

    moments.append(_moment_template("dup_hardline_flank", PartyType.DUP_STYLE, "Hardline flank pressure", "A rival unionist force is polling well on uncompromising rhetoric.", MomentCategory.CAMPAIGN, Urgency.HIGH, ["media", "party_executive"], ["Hardline Constitutionalists", "Modernisers"], {"party.custom.hardline_pressure": 58}, ["udf_rival", "udf_mla"], [
        _decision("dup_flank_match", "Match the rival rhetoric", "Close off defections with sharper messaging.", ALL_ROLES, DecisionType.HARD_LINE, 8, 4, 61, {"party.custom.unionist_credibility": 3, "party.custom.moderate_leakage": 2, "party.public_trust": -1}, "You regain some flank voters and lose moderates."),
        _decision("dup_flank_centre", "Hold a steadier line", "Talk competence and avoid rhetorical escalation.", SENIOR_ROLES + [Role.COUNCILLOR], DecisionType.COMPROMISE, 8, 4, 47, {"party.public_trust": 2, "party.custom.moderate_leakage": -2, "party.custom.hardline_pressure": 2}, "You stabilise the centre and anger hardliners."),
    ], "The rival dominates the narrative and claims authentic conviction.", "Resistance to compromise and moderate leakage are in direct tension."))

    moments.append(_moment_template("dup_loyalist_meeting", PartyType.DUP_STYLE, "Loyalist community meeting", "Local representatives demand stronger language on policing and funding.", MomentCategory.LOCAL, Urgency.MEDIUM, ["local_council", "party_executive"], ["Local Bosses", "Hardline Constitutionalists"], {"constituency.local_issue_pressure": 40}, ["udf_councillor", "udf_mla"], [
        _decision("dup_meeting_attend", "Attend and promise a stronger line", "Offer public backing for tougher demands.", [Role.ACTIVIST, Role.COUNCILLOR, Role.CANDIDATE, Role.MLA], DecisionType.HARD_LINE, 7, 2, 55, {"player.local_base": 3, "party.public_trust": -1, "constituency.local_media_heat": 2}, "You strengthen community links and widen scrutiny."),
        _decision("dup_meeting_lawful", "Emphasise legal pathways", "Advocate calm process and lawful delivery.", SENIOR_ROLES, DecisionType.COMPROMISE, 9, 5, 40, {"party.public_trust": 2, "player.local_base": -1, "party.custom.unionist_credibility": -1}, "Moderates approve while local anger lingers."),
    ], "Local representatives claim you ignored them and brief against you.", "Community ties and wider trust can pull in different directions."))

    moments.append(_moment_template("dup_leadership_briefing", PartyType.DUP_STYLE, "Leadership briefing leak", "Anonymous sources undermine the party leader before a key week.", MomentCategory.FACTIONAL, Urgency.HIGH, ["party_executive", "media"], ["Pragmatic Governors", "Hardline Constitutionalists"], {"party.leader_authority": 50}, ["udf_leader", "udf_rival"], [
        _decision("dup_leader_loyal", "Publicly defend the leader", "Shut down anonymous sniping.", ALL_ROLES, DecisionType.SUPPORT, 8, 3, 34, {"party.leader_authority": 3, "player.leader_trust": 3, "player.faction_support": -1}, "The leader notes your loyalty."),
        _decision("dup_leader_manoeuvre", "Quietly test alternatives", "Sound out whether a future shift is possible.", [Role.MLA, Role.ADVISER, Role.CANDIDATE], DecisionType.CAREER, 9, 5, 67, {"player.career_momentum": 2, "party.party_unity": -3, "player.party_trust": -2}, "You gain whispers of support and attract suspicion."),
    ], "A rival handles the briefing and becomes the new faction favourite.", "Loyalty and ambition are both rewarded, but never at once."))

    moments.append(_moment_template("dup_council_flag", PartyType.DUP_STYLE, "Council flag dispute", "A symbolic vote in council explodes into regional media coverage.", MomentCategory.LOCAL, Urgency.HIGH, ["local_council", "media"], ["Local Bosses", "Modernisers"], {"constituency.local_media_heat": 45}, ["udf_councillor", "udf_adviser"], [
        _decision("dup_flag_mobilise", "Mobilise local supporters", "Turn out branches and dominate the chamber optics.", [Role.ACTIVIST, Role.COUNCILLOR, Role.CANDIDATE], DecisionType.HARD_LINE, 8, 2, 58, {"player.local_base": 3, "party.custom.unionist_credibility": 2, "party.custom.executive_stability": -2}, "You win the room and lose goodwill elsewhere."),
        _decision("dup_flag_deescalate", "Seek a procedural compromise", "Reduce symbolic heat and protect cross-community ties.", [Role.MLA, Role.ADVISER, Role.JUNIOR_MINISTER, Role.MINISTER], DecisionType.COMPROMISE, 9, 5, 42, {"party.custom.executive_stability": 3, "party.custom.unionist_credibility": -1, "party.public_trust": 1}, "The row cools, but some members mutter about retreat."),
    ], "The local paper runs without your perspective and credits your rival.", "Mobilisation energy can damage wider cross-community credibility."))

    # Sinn Féin-style moments
    moments.append(_moment_template("sf_border_poll", PartyType.SINN_FEIN_STYLE, "Border poll pressure builds", "Campaigners demand a sharper unity timetable in every speech.", MomentCategory.CONSTITUTIONAL, Urgency.HIGH, ["party_executive", "media"], ["Republican Old Guard", "Modernising Professionals"], {"party.custom.unity_momentum": 55}, ["pfr_leader", "pfr_mla"], [
        _decision("sf_border_push", "Push a harder unity campaign", "Call for a clear constitutional deadline.", ALL_ROLES, DecisionType.HARD_LINE, 8, 3, 54, {"party.custom.unity_momentum": 4, "party.public_trust": -1, "party.custom.dublin_viability": -1}, "Movement activists celebrate your clarity."),
        _decision("sf_border_reassure", "Pair unity with reassurance", "Stress practical governance alongside constitutional ambition.", SENIOR_ROLES, DecisionType.COMPROMISE, 9, 5, 40, {"party.public_trust": 2, "party.custom.dublin_viability": 2, "party.custom.republican_credibility": -1}, "You broaden appeal and irritate harder voices."),
    ], "Another actor fronts the unity campaign and gains movement credit.", "Unity momentum and reassurance compete for limited political space."))

    moments.append(_moment_template("sf_legacy_headlines", PartyType.SINN_FEIN_STYLE, "Legacy issue returns to headlines", "Hostile interviews reopen unresolved legacy questions.", MomentCategory.MEDIA, Urgency.HIGH, ["media"], ["Republican Old Guard", "Modernising Professionals"], {"party.custom.legacy_pressure": 48}, ["pfr_adviser", "pfr_mla"], [
        _decision("sf_legacy_defend", "Defend movement history forcefully", "Challenge hostile framing and attack selective memory.", [Role.ACTIVIST, Role.COUNCILLOR, Role.MLA], DecisionType.HARD_LINE, 8, 3, 59, {"party.custom.republican_credibility": 3, "party.public_trust": -2, "party.media_pressure": 1}, "Supporters applaud; undecided voters hesitate."),
        _decision("sf_legacy_forward", "Pivot to present delivery", "Acknowledge pain and centre modern governance.", SENIOR_ROLES, DecisionType.DISCIPLINE, 10, 5, 38, {"party.public_trust": 2, "party.government_credibility": 2, "party.custom.republican_credibility": -1}, "Coverage softens, though old guard activists complain."),
    ], "A southern commentator frames your silence as evasive.", "Historic credibility and wider trust pull in different directions."))

    moments.append(_moment_template("sf_dublin_test", PartyType.SINN_FEIN_STYLE, "Dublin government credibility test", "Southern outlets ask if your party is ready for office beyond slogans.", MomentCategory.GOVERNANCE, Urgency.MEDIUM, ["media", "party_executive"], ["Southern Electoral Machine", "Left Social Republicans"], {"party.custom.dublin_viability": 45}, ["pfr_adviser", "pfr_leader"], [
        _decision("sf_dublin_professional", "Run a disciplined policy briefing", "Present costed priorities and governing tone.", SENIOR_ROLES + [Role.CANDIDATE], DecisionType.BRIEFING, 9, 5, 36, {"party.custom.dublin_viability": 4, "party.public_trust": 1}, "Editors call your performance serious."),
        _decision("sf_dublin_attack", "Attack establishment gatekeeping", "Frame the scrutiny as elite panic.", ALL_ROLES, DecisionType.HARD_LINE, 8, 3, 55, {"party.activist_morale": 2, "party.custom.dublin_viability": -2, "party.media_pressure": 2}, "Core supporters love it; sceptics remain unconvinced."),
    ], "A rival spokesperson becomes the default southern media voice.", "Radical edge and governability are difficult to maximise together."))

    moments.append(_moment_template("sf_housing_flash", PartyType.SINN_FEIN_STYLE, "Housing policy flashpoint", "Pressure mounts to choose radical intervention or cautious delivery sequencing.", MomentCategory.DELIVERY, Urgency.CRITICAL, ["assembly", "executive_department"], ["Left Social Republicans", "Governing Pragmatists"], {"constituency.local_issue_pressure": 52}, ["pfr_senior_min", "pfr_councillor"], [
        _decision("sf_housing_radical", "Back radical intervention", "Push rent controls and rapid compulsory powers.", [Role.MLA, Role.JUNIOR_MINISTER, Role.MINISTER, Role.COUNCILLOR], DecisionType.HARD_LINE, 11, 6, 56, {"party.activist_morale": 3, "party.public_trust": -1, "party.government_credibility": -1}, "Activists are energised while implementers warn of chaos."),
        _decision("sf_housing_cautious", "Sequence delivery cautiously", "Prioritise phased build-out and legal resilience.", SENIOR_ROLES, DecisionType.COMPROMISE, 10, 6, 41, {"party.government_credibility": 3, "party.activist_morale": -1, "party.public_trust": 1}, "Delivery teams breathe easier, activists push back."),
    ], "Community anger rises and tomorrow's agenda worsens.", "Left pressure and middle-class reassurance remain in tension."))

    moments.append(_moment_template("sf_activist_controversy", PartyType.SINN_FEIN_STYLE, "Activist controversy", "A local activist creates a social media storm.", MomentCategory.MEDIA, Urgency.MEDIUM, ["media", "party_executive"], ["Northern Community Organisers", "Modernising Professionals"], {"party.media_pressure": 50}, ["pfr_councillor", "pfr_rival"], [
        _decision("sf_activist_protect", "Protect the activist", "Describe criticism as coordinated bad-faith outrage.", [Role.ACTIVIST, Role.COUNCILLOR, Role.CANDIDATE], DecisionType.SUPPORT, 7, 2, 53, {"party.activist_morale": 3, "party.public_trust": -2}, "The base feels defended."),
        _decision("sf_activist_discipline", "Enforce message discipline", "Suspend local media appearances and reset messaging.", SENIOR_ROLES, DecisionType.DISCIPLINE, 9, 5, 39, {"party.public_trust": 2, "party.party_unity": -1, "party.media_pressure": -1}, "The storm weakens, but branch anger grows."),
    ], "A rival handles communications and gains leadership trust.", "Base protection and message discipline cannot both dominate."))

    moments.append(_moment_template("sf_delivery_crisis", PartyType.SINN_FEIN_STYLE, "Stormont delivery crisis", "A departmental backlog undermines claims of competent government.", MomentCategory.DELIVERY, Urgency.CRITICAL, ["executive_department", "civil_service"], ["Governing Pragmatists", "Republican Old Guard"], {"party.government_credibility": 47}, ["pfr_senior_min", "pfr_adviser"], [
        _decision("sf_delivery_own", "Own the failure and fix delivery", "Issue concrete milestones and accountability points.", SENIOR_ROLES, DecisionType.DISCIPLINE, 13, 8, 43, {"party.government_credibility": 4, "party.public_trust": 2, "party.custom.stormont_stability": 2}, "Civil service relationships improve quickly."),
        _decision("sf_delivery_frame", "Frame failure constitutionally", "Argue the constitutional context limits service potential.", [Role.MLA, Role.COUNCILLOR, Role.ACTIVIST], DecisionType.HARD_LINE, 8, 3, 57, {"party.custom.republican_credibility": 2, "party.government_credibility": -3, "party.custom.stormont_stability": -2}, "Movement activists agree, service users do not."),
    ], "Opponents cite your absence as proof of weak governance.", "Competence and constitutional framing tug in opposite directions."))

    moments.append(_moment_template("sf_selection_dispute", PartyType.SINN_FEIN_STYLE, "Candidate selection dispute", "Branch organisers and media strategists clash over the preferred candidate.", MomentCategory.CANDIDATE_SELECTION, Urgency.HIGH, ["party_executive"], ["Northern Community Organisers", "Southern Electoral Machine"], {"party.local_machine_strength": 55}, ["pfr_officer", "pfr_rival"], [
        _decision("sf_selection_branch", "Back the local organiser", "Prioritise branch loyalty and machine discipline.", [Role.ACTIVIST, Role.COUNCILLOR, Role.CANDIDATE], DecisionType.SUPPORT, 8, 3, 42, {"party.local_machine_strength": 3, "party.custom.southern_growth": -1, "player.local_base": 2}, "Local activists reward your loyalty."),
        _decision("sf_selection_media", "Back media-friendly candidate", "Choose expansion potential over machine comfort.", SENIOR_ROLES, DecisionType.COMPROMISE, 9, 5, 48, {"party.custom.southern_growth": 2, "party.local_machine_strength": -2, "player.party_trust": 1}, "Strategists are pleased; branches feel bypassed."),
    ], "The final list is settled without you, strengthening a rival network.", "Branch loyalty and expansion goals conflict."))

    moments.append(_moment_template("sf_soft_challenge", PartyType.SINN_FEIN_STYLE, "Republican credentials challenged", "Rivals claim the party has gone soft on core constitutional goals.", MomentCategory.FACTIONAL, Urgency.MEDIUM, ["media", "party_executive"], ["Republican Old Guard", "Modernising Professionals"], {"party.custom.republican_credibility": 55}, ["pfr_mla", "pfr_rival"], [
        _decision("sf_soft_reassert", "Reassert orthodox credentials", "Adopt sharper language and symbolic signals.", ALL_ROLES, DecisionType.HARD_LINE, 7, 2, 54, {"party.custom.republican_credibility": 3, "party.public_trust": -1, "party.custom.dublin_viability": -1}, "Old guard networks back you."),
        _decision("sf_soft_modern", "Defend a modern governing line", "Insist credibility comes from delivery and seriousness.", SENIOR_ROLES + [Role.COUNCILLOR], DecisionType.COMPROMISE, 8, 4, 45, {"party.government_credibility": 2, "party.custom.dublin_viability": 2, "party.activist_morale": -1}, "You gain moderates and annoy traditionalists."),
    ], "Your rival claims ideological clarity and gains activist attention.", "Old guard expectations and modernising strategy collide."))

    moments.append(_moment_template("sf_southern_scrutiny", PartyType.SINN_FEIN_STYLE, "Southern media scrutiny", "A high-profile southern journalist frames the party as risky and unserious.", MomentCategory.MEDIA, Urgency.HIGH, ["media"], ["Southern Electoral Machine", "Modernising Professionals"], {"party.custom.dublin_viability": 46}, ["pfr_adviser", "pfr_leader"], [
        _decision("sf_scrutiny_attack", "Attack the framing", "Go after the journalist's establishment assumptions.", ALL_ROLES, DecisionType.HARD_LINE, 8, 3, 60, {"party.activist_morale": 2, "party.media_pressure": 2, "party.custom.dublin_viability": -2}, "Supporters praise your aggression."),
        _decision("sf_scrutiny_reassure", "Offer calm reassurance", "Provide detail and tone down confrontation.", SENIOR_ROLES, DecisionType.BRIEFING, 9, 5, 37, {"party.custom.dublin_viability": 3, "party.public_trust": 1, "party.activist_morale": -1}, "The interview lands better than expected."),
    ], "The story runs without your framing and hardens perceptions.", "Attacking establishment media can hurt reassurance efforts."))

    moments.append(_moment_template("sf_leadership_leak", PartyType.SINN_FEIN_STYLE, "Leadership briefing", "Internal doubts about strategy leak before a major conference.", MomentCategory.FACTIONAL, Urgency.HIGH, ["party_executive", "media"], ["Governing Pragmatists", "Republican Old Guard"], {"party.party_unity": 55}, ["pfr_leader", "pfr_rival"], [
        _decision("sf_leak_discipline", "Defend discipline", "Call for unity and condemn anonymous briefing.", ALL_ROLES, DecisionType.DISCIPLINE, 8, 3, 35, {"party.party_unity": 3, "player.party_trust": 2, "player.career_momentum": 1}, "Senior figures notice your discipline."),
        _decision("sf_leak_ambition", "Quietly cultivate dissatisfied figures", "Turn the leak into personal opportunity.", [Role.MLA, Role.ADVISER, Role.CANDIDATE], DecisionType.CAREER, 9, 5, 66, {"player.career_momentum": 3, "party.party_unity": -3, "player.party_trust": -2}, "You build a private network and public suspicion."),
    ], "A rival becomes the organiser of the discontented bloc.", "Discipline and factional ambition reward different behaviours."))

    # Alliance-style moments
    moments.append(_moment_template("all_messaging_test", PartyType.ALLIANCE_STYLE, "Cross-community messaging test", "A divisive story demands a response that is principled yet clear.", MomentCategory.MEDIA, Urgency.HIGH, ["media", "party_executive"], ["Cross-Community Idealists", "Tactical Pragmatists"], {"party.custom.cross_community_credibility": 55}, ["cap_leader", "cap_adviser"], [
        _decision("all_message_principle", "Lead with principle", "State values directly even if some blocs dislike it.", ALL_ROLES, DecisionType.SUPPORT, 8, 3, 45, {"party.custom.cross_community_credibility": 2, "party.custom.both_sides_pressure": 2, "player.media_profile": 1}, "Supporters praise clarity; critics call it naïve."),
        _decision("all_message_precision", "Lead with pragmatic detail", "Use practical framing to avoid symbolic traps.", SENIOR_ROLES + [Role.COUNCILLOR], DecisionType.COMPROMISE, 8, 4, 39, {"party.public_trust": 2, "party.custom.moderate_appeal": 2, "party.custom.liberal_voter_energy": -1}, "Coverage calls you competent but less inspiring."),
    ], "A rival spokesperson defines the narrative first.", "Principle and tactical clarity are hard to balance."))

    moments.append(_moment_template("all_tactical_squeeze", PartyType.ALLIANCE_STYLE, "Tactical vote squeeze", "Bigger parties warn voters not to waste ballots on you.", MomentCategory.CAMPAIGN, Urgency.HIGH, ["media", "party_executive"], ["Tactical Pragmatists", "Cross-Community Idealists"], {"party.custom.tactical_vote_pressure": 50}, ["cap_rival", "cap_leader"], [
        _decision("all_squeeze_counter", "Counter with local delivery record", "Show practical wins to challenge tactical arguments.", ALL_ROLES, DecisionType.LOCAL_WORK, 7, 2, 36, {"party.custom.moderate_appeal": 2, "party.custom.tactical_vote_pressure": -2, "player.local_base": 2}, "Doorstep conversations become more receptive."),
        _decision("all_squeeze_attack", "Attack tactical fearmongering", "Call the squeeze cynical and anti-democratic.", ALL_ROLES, DecisionType.HARD_LINE, 8, 3, 52, {"party.custom.liberal_voter_energy": 2, "party.custom.moderate_appeal": -1, "party.media_pressure": 1}, "You energise activists and unsettle cautious voters."),
    ], "A larger party narrative lands unchallenged in your patch.", "Moderate appeal and pressure from tactical voting remain in tension."))

    moments.append(_moment_template("all_both_sides_attack", PartyType.ALLIANCE_STYLE, "Both sides attack neutrality", "You are accused of helping unionism and nationalism at the same time.", MomentCategory.MEDIA, Urgency.MEDIUM, ["media"], ["Cross-Community Idealists", "Cautious Moderates"], {"party.custom.both_sides_pressure": 55}, ["cap_mla", "cap_adviser"], [
        _decision("all_neutrality_hold", "Hold the cross-community frame", "Refuse binary alignment and repeat core purpose.", ALL_ROLES, DecisionType.SUPPORT, 7, 2, 43, {"party.custom.cross_community_credibility": 3, "party.custom.both_sides_pressure": 1}, "Your base sees consistency."),
        _decision("all_neutrality_pick", "Take a sharper side on this issue", "Prioritise clarity over symmetry.", [Role.MLA, Role.COUNCILLOR, Role.CANDIDATE], DecisionType.HARD_LINE, 8, 3, 58, {"party.custom.liberal_voter_energy": 2, "party.custom.cross_community_credibility": -2}, "The line is clearer, coalition breadth narrows."),
    ], "Commentators say your silence proves evasiveness.", "Identity pressure tests cross-community credibility."))

    moments.append(_moment_template("all_liberal_backlash", PartyType.ALLIANCE_STYLE, "Liberal social issue backlash", "Young activists want a strong progressive stance, while moderate voters look uneasy.", MomentCategory.FACTIONAL, Urgency.MEDIUM, ["party_executive", "media"], ["Young Urban Wing", "Cautious Moderates"], {"party.custom.liberal_voter_energy": 50}, ["cap_rival", "cap_councillor"], [
        _decision("all_liberal_push", "Back a sharper progressive line", "Use direct language and online mobilisation.", ALL_ROLES, DecisionType.HARD_LINE, 8, 3, 55, {"party.custom.liberal_voter_energy": 3, "party.custom.moderate_appeal": -2, "player.media_profile": 1}, "Young activists rally around you."),
        _decision("all_liberal_balance", "Balance tone and timing", "Signal support with less confrontational language.", SENIOR_ROLES + [Role.COUNCILLOR], DecisionType.COMPROMISE, 7, 3, 37, {"party.custom.moderate_appeal": 2, "party.custom.liberal_voter_energy": -1, "party.party_unity": 1}, "The coalition holds, though some activists feel muted."),
    ], "Online activists accuse the party of dithering.", "Liberal energy and moderate caution are both essential and conflicting."))

    moments.append(_moment_template("all_overstretch", PartyType.ALLIANCE_STYLE, "Candidate overstretch in unionist area", "A winnable opening appears but your local machine is thin.", MomentCategory.CAMPAIGN, Urgency.HIGH, ["party_executive", "local_council"], ["Tactical Pragmatists", "Local Government Builders"], {"party.custom.overextension_risk": 40}, ["cap_officer", "cap_rival"], [
        _decision("all_overstretch_push", "Contest aggressively", "Deploy volunteers heavily and chase momentum.", [Role.CANDIDATE, Role.COUNCILLOR, Role.ACTIVIST], DecisionType.CAREER, 10, 4, 57, {"party.election_readiness": 2, "party.custom.overextension_risk": 3, "player.career_momentum": 2}, "You gain visibility and stretch resources."),
        _decision("all_overstretch_target", "Target narrowly", "Limit investment to credible wards and preserve depth.", SENIOR_ROLES + [Role.COUNCILLOR], DecisionType.COMPROMISE, 8, 4, 35, {"party.custom.overextension_risk": -2, "party.election_readiness": 1, "party.custom.moderate_appeal": 1}, "The campaign is tighter and more sustainable."),
    ], "A rival takes the opportunity and claims local initiative.", "Ambition and organisational capacity are in direct competition."))

    moments.append(_moment_template("all_council_delivery", PartyType.ALLIANCE_STYLE, "Council delivery opportunity", "A practical council success could raise credibility if handled well.", MomentCategory.LOCAL, Urgency.MEDIUM, ["local_council", "media"], ["Local Government Builders", "Liberal Professionals"], {"constituency.local_issue_pressure": 35}, ["cap_councillor", "cap_mla"], [
        _decision("all_delivery_quiet", "Deliver quietly", "Prioritise outcomes over headlines.", ALL_ROLES, DecisionType.LOCAL_WORK, 6, 1, 22, {"party.government_credibility": 2, "player.local_base": 2, "party.media_pressure": -1}, "Residents notice competence."),
        _decision("all_delivery_loud", "Turn delivery into a media push", "Use the win for profile-building.", ALL_ROLES, DecisionType.BRIEFING, 8, 3, 44, {"player.media_profile": 3, "party.custom.respectability": 1, "party.media_pressure": 1}, "You gain profile and invite scrutiny."),
    ], "Another councillor presents the success first and takes credit.", "Quiet competence and media attention trade against each other."))

    moments.append(_moment_template("all_media_expectations", PartyType.ALLIANCE_STYLE, "Media praise creates expectations", "Positive coverage now demands consistent high performance.", MomentCategory.MEDIA, Urgency.MEDIUM, ["media"], ["Liberal Professionals", "Cautious Moderates"], {"party.custom.respectability": 58}, ["cap_leader", "cap_adviser"], [
        _decision("all_expectations_manage", "Lower expectations carefully", "Reset tone and stress gradual progress.", SENIOR_ROLES, DecisionType.BRIEFING, 8, 4, 33, {"party.media_pressure": -2, "party.custom.respectability": -1, "party.party_unity": 1}, "You cool pressure but lose some shine."),
        _decision("all_expectations_chase", "Chase the praise cycle", "Accept every appearance and escalate ambition.", ALL_ROLES, DecisionType.CAREER, 10, 5, 59, {"player.media_profile": 3, "party.media_pressure": 2, "party.custom.overextension_risk": 2}, "You become visible and exposed."),
    ], "Press attention moves to a rival who now owns the story.", "Respectability gains can quickly become scrutiny pressure."))

    moments.append(_moment_template("all_young_urban", PartyType.ALLIANCE_STYLE, "Young urban activists demand stronger line", "Younger members push for sharper rhetoric and faster action.", MomentCategory.FACTIONAL, Urgency.HIGH, ["party_executive"], ["Young Urban Wing", "Cautious Moderates"], {"party.custom.liberal_voter_energy": 52}, ["cap_rival", "cap_adviser"], [
        _decision("all_young_meeting", "Attend activists and promise sharper line", "Offer a stronger tone publicly.", [Role.ACTIVIST, Role.COUNCILLOR, Role.CANDIDATE, Role.MLA], DecisionType.HARD_LINE, 9, 3, 55, {"party.custom.liberal_voter_energy": 3, "party.party_unity": -1, "player.faction_support": 2}, "Young activists are energised; moderates worry."),
        _decision("all_young_bridge", "Bridge activists and moderates", "Host a private session to shape a joint message.", SENIOR_ROLES, DecisionType.COMPROMISE, 10, 5, 38, {"party.party_unity": 2, "party.custom.liberal_voter_energy": 1, "party.custom.moderate_appeal": 1}, "The conversation calms internal rows."),
    ], "A rival councillor briefs that you are chasing student politics.", "Youthful energy and broad coalition discipline must be balanced."))

    moments.append(_moment_template("all_exec_dilemma", PartyType.ALLIANCE_STYLE, "Executive participation dilemma", "Entering or staying in government could improve influence but blur identity.", MomentCategory.GOVERNANCE, Urgency.HIGH, ["party_executive", "assembly"], ["Tactical Pragmatists", "Cross-Community Idealists"], {"party.government_credibility": 45}, ["cap_leader", "cap_mla"], [
        _decision("all_exec_join", "Argue for participation", "Influence policy from inside government.", SENIOR_ROLES + [Role.CANDIDATE], DecisionType.COMPROMISE, 9, 5, 47, {"party.government_credibility": 3, "party.custom.cross_community_credibility": -1, "party.custom.respectability": 2}, "You gain leverage and face purity criticism."),
        _decision("all_exec_distance", "Argue for principled distance", "Protect distinct identity by staying outside.", ALL_ROLES, DecisionType.OPPOSE, 7, 2, 46, {"party.custom.cross_community_credibility": 2, "party.government_credibility": -1, "party.activist_morale": 1}, "Your line protects identity but limits formal influence."),
    ], "The party settles its line without you and your influence slips.", "Influence in government and political purity are rarely both maximised."))

    moments.append(_moment_template("all_leadership_row", PartyType.ALLIANCE_STYLE, "Leadership positioning row", "Members disagree whether the party should be technocratic, liberal or insurgent.", MomentCategory.FACTIONAL, Urgency.MEDIUM, ["party_executive", "media"], ["Liberal Professionals", "Tactical Pragmatists", "Young Urban Wing"], {"party.party_unity": 52}, ["cap_leader", "cap_rival"], [
        _decision("all_row_technocratic", "Back technocratic positioning", "Prioritise policy depth and administrative credibility.", SENIOR_ROLES, DecisionType.DISCIPLINE, 8, 4, 33, {"party.custom.respectability": 3, "party.custom.liberal_voter_energy": -1, "party.party_unity": 1}, "Commentators praise seriousness."),
        _decision("all_row_movement", "Back movement energy", "Push a louder reformist identity.", ALL_ROLES, DecisionType.HARD_LINE, 8, 3, 51, {"party.custom.liberal_voter_energy": 3, "party.custom.respectability": -1, "party.party_unity": -1}, "Activists are energised and professionals uneasy."),
    ], "A rival defines the party's future language without you.", "Professionalism and movement energy pull the party in different directions."))

    return moments


def create_moment_from_template(template: Dict, *, day: int, slot: TimeSlot, slot_index: int, party_id: str, constituency_name: str, faction_name: str) -> Moment:
    template_copy = deepcopy(template)
    return Moment(
        id=f"{template_copy['id']}_{day}_{slot_index}",
        title=template_copy["title"],
        description=template_copy["description"],
        party_id=party_id,
        party_type=template_copy["party_type"],
        category=template_copy["category"],
        urgency=template_copy["urgency"],
        time_slot=slot,
        eligible_roles=ALL_ROLES,
        institution_tags=template_copy["institution_tags"],
        constituency_tags=[constituency_name],
        faction_tags=template_copy["faction_tags"] + [faction_name],
        involved_actor_ids=template_copy["involved_actors"],
        pressure_requirements=template_copy["pressure_requirements"],
        decision_options=template_copy["decision_options"],
        ignored_effect=template_copy["ignored_effect"],
        expires_after_slots=template_copy["expires_after_slots"],
        can_escalate=template_copy["can_escalate"],
        escalation_moment_id=None,
        consequence_summary=template_copy["consequence_summary"],
        created_day=day,
        created_slot_index=slot_index,
    )
