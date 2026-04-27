# Northern Ireland Political Simulator: Councillor Routine and Story Beat Engine

**Document status:** Stage 1 technical design  
**Target repository location:** `docs/councillor_routine_beat_engine.md`  
**Primary implementation target:** Python with PySide6  
**Game mode covered:** Councillor-focused MVP  
**Document purpose:** Define the routine-driven daily simulation, story beat engine, dashboard-first interface, and event-driven consequence system for the first playable version.

## 1. Design Intent

The simulator should not feel like a random political incident generator. It should feel like the daily professional routine of a Northern Ireland councillor who is trying to do the job, build a local base, avoid political traps, manage rivals, keep party relationships alive, and gradually become credible enough for Assembly selection.

The player is not the centre of the political world. The player is one actor within a wider system. The system moves around them. Council officers respond or delay. Rivals claim credit. Local journalists frame stories. Residents post online. Party group figures apply pressure. Branch members notice attendance and loyalty. Factions observe whether the player is useful, principled, ambitious, reckless or unreliable.

The first playable slice should not attempt to simulate all of Northern Ireland politics. It should simulate a believable councillor day with enough continuity that a local issue can become a small story over several days.

The core feeling should be:

> I have a busy day. I cannot do everything. Every choice affects residents, party colleagues, officers, rivals, media and my future career.

## 2. Primary MVP Goal

The MVP should prove this career loop:

1. Start as a councillor.
2. Handle ordinary ward work.
3. Build resident trust and local visibility.
4. Develop branch and faction support.
5. Compete with a local rival.
6. Become credible for Assembly candidate selection.
7. Win or secure entry into the Assembly path.
8. Survive an early party crisis.
9. Become eligible for a junior ministerial offer later.

The first implementation should focus mostly on stages 1 to 6. Later stages can be represented by lightweight career opportunity moments.

## 3. Non-goals for This Stage

The following are deliberately out of scope:

- Full UK simulation.
- Full Republic of Ireland simulation.
- Real politicians.
- Full election modelling.
- Database persistence.
- Complex procedural narrative generation.
- A grand strategy map.
- Hour-by-hour realism.
- Passive weekly stat drift.
- Omnipotent player control.
- A command line interface as the main UI.

The MVP should be a compact PySide6 desktop application with a dashboard-first management interface.

## 4. Core Simulation Principle

Do not generate disconnected events. Generate structured days made from linked beats.

The core daily loop is:

1. Start day.
2. Player checks dashboard.
3. Inbox and agenda are populated.
4. Player chooses which item to handle.
5. Player chooses how to handle it.
6. System reacts.
7. Story memory is updated.
8. Time advances by one slot.
9. Unhandled items may expire, escalate or be handled by another actor.
10. Day continues until the end-of-day review.

Time advances by time slot, not by week.

The time slots are:

- Morning
- Afternoon
- Evening
- Late Night

The normal game should never jump forward by more than one day. A day should feel politically active and operationally busy.

## 5. Natural Councillor Day Structure

A councillor day should usually be built from the following components:

- Email and casework triage.
- Resident complaints.
- Phone calls from residents, officers, journalists or party figures.
- Site visits.
- Meetings with council officers.
- Community events.
- Local media interactions.
- Social media decisions.
- Party group or branch activity.
- Committee or council business.
- Rival councillor activity.
- End-of-day fallout and inbox review.

The simulation should not rigidly force the same sequence every day. It should use day templates that make the routine feel coherent.

## 6. Example Daily Loops

### 6.1 Local Incident Day

1. Check emails.
2. Triage emails and respond as appropriate.
3. Phone call reports a car accident at a known hotspot.
4. Player decides how to proceed.
5. Player may go to the scene.
6. Player may speak to crash victims or residents.
7. Player may speak to media.
8. Player may post on social media.
9. Player returns to base.
10. Meeting with council officers about an urban renewal project.
11. Council meeting.
12. Vote on three minor issues.
13. Check emails.
14. End day.

### 6.2 Campaign Support Day

1. Phone call asks for help campaigning in the Stormont election.
2. Player promises, refuses or negotiates support.
3. Meeting with council officers on a new digital project.
4. Community charity event.
5. Player speaks to media at the event.
6. Player checks emails.
7. Player triages and responds.
8. Evening campaign session.
9. Doorstep challenges create political choices.
10. Branch and party campaign organisers react.

### 6.3 Routine Political Positioning Day

1. Check emails.
2. Triage and respond.
3. Plan leaflet drop for council elections.
4. Arrange supporters.
5. Meet constituent with ongoing noise complaint.
6. Speak to business owner about the complaint.
7. Interview with local newspaper about flags and band parades.
8. Meeting with local party strategy team.
9. Late social media and branch reaction.

These examples are not fixed scripts. They are reference patterns for how the generator should assemble believable days.

## 7. Beat-Based Architecture

The simulation should be built from four main layers:

1. Day templates.
2. Story beats.
3. Content packs.
4. Memory and follow-up rules.

### 7.1 Day Templates

A day template gives the rough shape of the day.

Examples:

- Admin-heavy day.
- Crisis-interrupt day.
- Council-meeting day.
- Campaign-heavy day.
- Community-visibility day.
- Media-heavy day.
- Committee-and-officer day.

A day template should define likely beat slots and probabilities, not fixed content.

Example template:

| Slot | Beat role | Notes |
|---|---|---|
| Morning | Inbox triage | Standard start to day |
| Morning | Trigger | Phone call or urgent complaint |
| Afternoon | Field action | Site visit, officer call or resident meeting |
| Afternoon | Scheduled work | Officer meeting or committee preparation |
| Evening | Formal or public activity | Council meeting, party group, community event |
| Late Night | Fallout | Social media, rival post, journalist follow-up |

### 7.2 Story Beats

A beat is one playable scene or decision point.

Beat examples:

- Check emails.
- Triage issue.
- Receive phone call.
- Visit site.
- Meet resident.
- Meet business owner.
- Speak to council officer.
- Attend community event.
- Speak to media.
- Post on social media.
- Attend council meeting.
- Vote on local issue.
- Join campaign session.
- Handle doorstep challenge.
- Read late-night fallout.

A beat should usually contain:

- Short narrative description.
- Who is involved.
- Why it matters.
- Available handling options.
- Likely upside.
- Likely risk.
- Costs.
- Consequences.
- Follow-up hooks.

### 7.3 Content Packs

A content pack provides the subject matter. It fills day templates and beats with local political material.

Initial content packs should include:

- Car accident hotspot.
- School parking chaos.
- Noise complaint between resident and business owner.
- Flags and band parades question.
- Urban renewal project.
- Missed bins backlash.
- Planning objection row.
- Antisocial behaviour spike.
- Town centre decline.
- Digital council project.
- Charity/community event.
- Stormont campaign help request.

Each content pack defines:

- Issue title.
- Issue type.
- Main stakeholders.
- Relevant institutions.
- Potential beats.
- Risks.
- Rewards.
- Likely media framing.
- Likely social media reaction.
- Follow-up possibilities.
- Resolution conditions.

### 7.4 Memory and Follow-up Rules

The game should remember what the player did.

Memory flags should be simple booleans, counters or tags. They should not become an over-complex scripting language.

Example flags for a car accident hotspot:

- `visited_scene`
- `contacted_psni`
- `contacted_roads_officer`
- `spoke_to_victims`
- `gave_media_quote`
- `posted_before_facts`
- `promised_action`
- `blamed_council`
- `rival_intervened`
- `resident_expectations_high`
- `officer_annoyed`
- `local_media_engaged`

Follow-up beats then check these flags.

Example:

- If `posted_before_facts` is true, a journalist may later ask whether the player checked the facts before making a public claim.
- If `contacted_roads_officer` is false, the officer may be irritated when the issue reaches media before the department was contacted.
- If `rival_intervened` is true, the rival may claim they secured officer attention.
- If `spoke_to_victims` is true and handled respectfully, resident trust may rise even if the problem is not solved.

## 8. Core Data Model

### 8.1 GameDate

Tracks the current game date and time slot.

Fields:

- `day`
- `month`
- `year`
- `weekday`
- `time_slot`

### 8.2 TimeSlot

Enum:

- `MORNING`
- `AFTERNOON`
- `EVENING`
- `LATE_NIGHT`

### 8.3 DayTemplate

Defines a daily structure.

Fields:

- `id`
- `name`
- `description`
- `weekday_bias`
- `required_beat_types`
- `optional_beat_types`
- `complication_chance`
- `allowed_content_tags`

### 8.4 DailyBeat

A playable scene or decision point.

Fields:

- `id`
- `title`
- `description`
- `beat_type`
- `time_slot`
- `urgency`
- `status`
- `linked_story_arc_id`
- `involved_actor_ids`
- `involved_relationships`
- `decision_options`
- `ignored_effect`
- `expiry_slot`
- `minor_action_allowed`

### 8.5 ContentPack

Defines issue-specific content.

Fields:

- `id`
- `title`
- `issue_type`
- `summary`
- `stakeholders`
- `institutions`
- `risk_tags`
- `reward_tags`
- `possible_opening_beats`
- `possible_followup_beats`
- `resolution_beats`
- `media_angles`
- `social_media_angles`

### 8.6 StoryArc

Tracks a developing local issue.

Fields:

- `id`
- `title`
- `theme`
- `status`
- `current_stage`
- `max_stage`
- `linked_constituency_id`
- `involved_actor_ids`
- `involved_relationships`
- `pressure_level`
- `public_visibility`
- `player_ownership`
- `rival_ownership`
- `resident_confidence`
- `officer_confidence`
- `party_concern`
- `flags`
- `scheduled_followups`
- `outcome_tags`

### 8.7 DecisionOption

A choice available to the player.

Fields:

- `id`
- `label`
- `description`
- `handling_style`
- `required_role`
- `stamina_cost`
- `influence_cost`
- `risk_level`
- `likely_upside`
- `likely_risk`
- `effects`
- `flags_set`
- `flags_cleared`
- `actor_reactions`
- `followup_rules`
- `result_text`

### 8.8 ActorReaction

A short system response from a simulated actor.

Fields:

- `actor_id`
- `reaction_text`
- `relationship_effects`
- `variable_effects`
- `possible_followup_beat`
- `visibility`

### 8.9 Player

Represents the player as an actor with career-specific state.

Fields:

- `actor_id`
- `name`
- `role`
- `party_id`
- `constituency_id`
- `stamina`
- `influence`
- `reputation`
- `local_base`
- `resident_trust`
- `branch_support`
- `party_group_trust`
- `officer_relationship`
- `media_profile`
- `social_media_volatility`
- `rival_threat`
- `career_momentum`

### 8.10 CareerState

Tracks progression.

Fields:

- `current_role`
- `target_role`
- `previous_roles`
- `selection_eligibility`
- `committee_credibility`
- `branch_support`
- `faction_support`
- `leader_trust`
- `promotion_offers`
- `career_flags`
- `rivals`

### 8.11 SimulationState

Top-level state object.

Fields:

- `date`
- `player`
- `parties`
- `factions`
- `actors`
- `constituencies`
- `institutions`
- `relationships`
- `active_story_arcs`
- `today_beats`
- `event_log`
- `recent_consequence`

## 9. Handling Styles

Choices should not be generic. Most beats should offer different ways to deal with the same issue.

Handling styles:

- Quiet Administrative
- Personal Ward Work
- Public Campaigning
- Party Escalation
- Cross-Party Deal
- Media Play
- Delay or Ignore
- Honest Refusal
- Delegation
- Confrontational Challenge

### 9.1 Quiet Administrative

Example: forward the complaint to the relevant officer and ask for an update.

Benefits:

- Low risk.
- Good for officer relationship.
- Keeps expectations controlled.

Drawbacks:

- Low public credit.
- Residents may feel ignored if response is slow.
- Rival can still appear more active.

### 9.2 Personal Ward Work

Example: visit site, meet residents, take photographs, listen directly.

Benefits:

- Strong resident trust.
- Strong ward visibility.
- Good for local base.

Drawbacks:

- High stamina cost.
- Raises expectations.
- Can be inefficient if overused.

### 9.3 Public Campaigning

Example: post publicly or call for urgent action.

Benefits:

- Raises visibility.
- Pressures institutions.
- Useful if issue has stalled.

Drawbacks:

- Can annoy officers.
- Can increase social media volatility.
- Can look opportunistic.

### 9.4 Party Escalation

Example: ask MLA, MP or party group leader to intervene.

Benefits:

- Can get faster response.
- Builds party links if aligned with priorities.

Drawbacks:

- Costs influence.
- Makes issue more partisan.
- May reduce image of independence.

### 9.5 Cross-Party Deal

Example: work with rival or opposing councillor to solve practical issue.

Benefits:

- Improves committee credibility.
- Can solve issue efficiently.
- Good for non-sectarian or practical image.

Drawbacks:

- Party group may dislike freelancing.
- Rival may share credit.
- Factions may see it as softness.

### 9.6 Media Play

Example: give interview or feed line to local paper.

Benefits:

- Raises media profile.
- Can shape narrative.
- Useful for career progression.

Drawbacks:

- Gaffe risk.
- Hostile framing risk.
- Party discipline risk.

### 9.7 Honest Refusal

Example: tell resident the council cannot do what they want.

Benefits:

- Builds long-term credibility.
- Improves officer trust.
- Avoids false promises.

Drawbacks:

- Immediate resident dissatisfaction.
- Rival can promise easier answers.

## 10. Action Economy

Each time slot allows:

- One main action.
- One minor action if stamina permits.

Main actions include:

- Site visit.
- Council meeting.
- Committee meeting.
- Community event.
- Media interview.
- Major resident meeting.
- Campaign session.
- Party strategy meeting.

Minor actions include:

- Send officer email.
- Phone resident.
- Post factual update.
- Call ally.
- Read papers.
- Check rival activity.
- Reply to journalist with holding line.

This creates pressure without requiring overwhelming detail.

## 11. Stamina and Capacity

Stamina represents time, energy and attention.

Low stamina should:

- Increase gaffe risk.
- Reduce relationship gains.
- Reduce media performance.
- Increase chance of poor judgement.
- Make late-night fallout more dangerous.
- Make the player more likely to miss details.

Stamina should recover partially overnight, but not always fully. A punishing week of public issues and meetings should leave the player more fragile.

## 12. Story Arcs for the First Vertical Slice

The first vertical slice should implement three detailed story chains and one lighter optional chain.

### 12.1 Car Accident Hotspot

Theme: road safety, visible local incident, media pressure, emotional residents.

Opening beats:

- Phone call from resident.
- Email from residents' association.
- Local journalist asks for comment.

Possible beats:

- Attend scene.
- Speak to victims or residents.
- Contact PSNI or roads officer.
- Post public statement.
- Request traffic-calming review.
- Attend residents' meeting.
- Rival proposes council motion.

Key risks:

- Looking opportunistic.
- Promising powers the council does not have.
- Annoying officers by going public too early.
- Rival claiming action.

Key rewards:

- Resident trust.
- Media profile.
- Ownership of road safety issue.
- Career momentum if handled maturely.

Example stages:

1. Incident reported.
2. Public and officer response.
3. Council or committee follow-up.
4. Resolution, ongoing pressure or backlash.

### 12.2 Noise Complaint and Business Owner Dispute

Theme: resident welfare versus local business interests.

Opening beats:

- Resident email about late-night noise.
- Phone call from business owner.
- Social media thread about nuisance.

Possible beats:

- Meet resident.
- Meet business owner.
- Ask council enforcement officer for advice.
- Broker informal agreement.
- Go public.
- Support formal complaint.
- Attend community mediation.

Key risks:

- Alienating business group.
- Failing vulnerable residents.
- Being accused of anti-business politics.
- Becoming trapped in a neighbour dispute.

Key rewards:

- Resident trust.
- Business relationship if handled fairly.
- Officer respect for careful process.
- Committee credibility.

Example stages:

1. Initial complaint.
2. Two-sided dispute.
3. Mediation, enforcement or escalation.
4. Settlement or public row.

### 12.3 Stormont Campaign Help Request

Theme: party loyalty, career ambition, stamina trade-off.

Opening beats:

- Party organiser calls asking for help.
- Candidate asks for evening canvassing support.
- Branch chair asks for leaflet drop planning.

Possible beats:

- Promise to help.
- Refuse due to council workload.
- Negotiate limited support.
- Join canvassing session.
- Handle doorstep challenge.
- Speak to campaign team.
- Debrief with branch.

Key risks:

- Neglecting council work.
- Damaging branch relationship.
- Being seen as ambitious rather than useful.
- Doorstep encounter goes badly.

Key rewards:

- Branch support.
- Faction support.
- Candidate selection credibility.
- Party group trust.

Example stages:

1. Request for help.
2. Practical campaign activity.
3. Doorstep challenge or campaign incident.
4. Branch reaction and career effect.

### 12.4 Flags and Band Parades Interview

Theme: sensitive identity issue, local media, party line, cross-community pressure.

Opening beats:

- Local paper asks for interview.
- Party group sends suggested line.
- Residents' group complains about disruption.

Possible beats:

- Follow party line.
- Give careful balanced answer.
- Refuse interview.
- Make strong public statement.
- Consult community groups first.
- Ask senior colleague to handle it.

Key risks:

- Angering base.
- Angering moderates.
- Looking evasive.
- Creating social media pile-on.

Key rewards:

- Media profile.
- Cross-community credibility.
- Faction support if aligned.
- Party trust if disciplined.

## 13. Dynamic Actor Reactions

After important actions, the system should generate one or more short reactions.

Actors who can react:

- Resident.
- Residents' association chair.
- Business owner.
- Council officer.
- Local journalist.
- Rival councillor.
- Party group leader.
- Branch organiser.
- Faction contact.
- Campaign organiser.
- Community worker.

Reactions should be descriptive and mechanically meaningful.

Examples:

- The roads officer replies quickly because your relationship is good.
- The journalist frames your answer fairly, but trims your caveat.
- Your rival posts from the same site and implies they were first to act.
- The branch organiser notes that you showed up when asked.
- The business owner says privately that you are grandstanding.
- A parent thanks you, but asks when something will actually change.
- Party group warns you not to freelance on sensitive issues.
- Residents' association invites you to a follow-up meeting.

## 14. Follow-up Generation

The follow-up generator should inspect active story arcs and memory flags.

For each unresolved story arc, it should decide whether to schedule:

- Officer response.
- Resident follow-up.
- Rival action.
- Media follow-up.
- Social media fallout.
- Party group intervention.
- Committee item.
- Council vote.
- Community meeting.
- Quiet resolution.

The follow-up generator should not flood the player. A day should still have a manageable agenda.

## 15. Dashboard-First Interface

The dashboard should be the main screen and main navigation hub.

It should feel like a management desk, closer in spirit to older Football Manager hub screens than to a random event popup.

### 15.1 Dashboard Goals

The dashboard should answer these questions immediately:

- What time is it?
- What kind of day is this?
- What must I deal with now?
- What is urgent?
- What is being ignored?
- Who is annoyed?
- What story is developing?
- What is my rival doing?
- Am I progressing toward Assembly selection?
- What happened after my last decision?

### 15.2 Dashboard Panels

Suggested panels:

1. Today’s Flow.
2. Inbox and Casework.
3. Active Local Story.
4. Ward Mood.
5. Party Pressure.
6. Rival Watch.
7. Relationships at Risk.
8. Career Track.
9. Local Chatter.
10. Recent Consequence.

### 15.3 Today’s Flow Panel

Displays the timeline of the day.

Example:

| Time | Item | Status |
|---|---|---|
| 09:00 | Email triage and casework | Pending |
| 10:20 | Phone call: accident at junction | Urgent |
| 12:00 | Media request from local paper | Waiting |
| 14:00 | Urban renewal officer meeting | Scheduled |
| 18:30 | Council meeting | Scheduled |
| 21:15 | Late inbox and social media check | Later |

The player should be able to click an item to open its decision screen.

### 15.4 Active Local Story Panel

Shows one or two active arcs.

Fields:

- Story title.
- Stage.
- Pressure level.
- Public visibility.
- Player ownership.
- Rival ownership.
- Next expected beat.

Example:

**Car Accident Hotspot**  
Stage 2: Pressure on officers  
Pressure: High  
Visibility: Medium  
Player ownership: 42  
Rival ownership: 18  
Next: Roads officer reply expected by tomorrow.

### 15.5 Career Track Panel

Shows progress toward the next step.

For councillor to Assembly selection:

- Reputation.
- Local base.
- Branch support.
- Career momentum.
- Rival threat.
- Faction support.

The panel should show the next likely opportunity and what is holding the player back.

### 15.6 Recent Consequence Panel

Shows the latest outcome.

Example:

**Residents saw you at the school gates**  
Resident trust +4. Ward visibility +3. Rival threat +1.  
Next suggested action: chase the roads officer before tomorrow evening.

## 16. Subscreens

The dashboard should be the main navigation surface, but subscreens are still useful.

Screens:

- Dashboard.
- Inbox.
- Day Flow.
- Stories.
- Party.
- Factions.
- Actors.
- Constituency.
- Relationships.
- Career.
- Log.
- Decision Result.

### 16.1 Inbox Screen

Grouped by:

- New.
- Urgent.
- Waiting on officer.
- Awaiting player response.
- Escalated.
- Resolved.

Each item should show:

- Issue.
- Sender.
- Urgency.
- Expiry.
- Current risk.
- Linked story.
- Handling options.

### 16.2 Day Flow Screen

Shows the full timeline by time slot.

The player can select a beat and see:

- Description.
- Involved people.
- Available decisions.
- What happens if ignored.

### 16.3 Stories Screen

Shows active story arcs and their remembered state.

Do not expose raw flags by default. Convert them to readable phrases.

Example:

- You visited the scene personally.
- Officers have not yet been contacted.
- Residents expect visible action.
- Rival has not intervened yet.
- Media interest is rising.

### 16.4 Decision Screen

Each decision card should show:

- Label.
- Description.
- Likely upside.
- Likely risk.
- Stamina cost.
- Influence cost.
- Affected groups.

Do not hide all consequences, but do not reveal exact numbers for everything if it feels too mechanical. The MVP can show exact numbers in result panels for clarity.

### 16.5 Decision Result Screen

The result should be descriptive and concise.

Sections:

- Headline.
- Narrative result.
- Key changes.
- Actor reactions.
- Story progression.
- Follow-up created.
- Time advanced.

## 17. Event-Driven Consequences

There must be no passive weekly drift.

Variables should change only because something happened:

- Player handled a beat.
- Player ignored a beat.
- Rival handled a beat.
- Officer responded.
- Journalist published.
- Resident group reacted.
- Party group intervened.
- Story arc escalated.
- Career opportunity was triggered.

This is critical for player comprehension. The player should understand why the state changed.

## 18. Ignoring and Deferment

Ignoring is a real choice, not just failure.

Reasons to ignore:

- Save stamina.
- Avoid a trap.
- Prioritise more important issue.
- Let officer process work.
- Avoid media escalation.
- Keep out of faction fight.

Possible ignored outcomes:

- Expires harmlessly.
- Resident trust falls.
- Rival intervenes.
- Officer handles quietly.
- Journalist publishes without comment.
- Branch complains.
- Issue escalates tomorrow.
- Social media grows hostile.

Ignored outcomes should be visible in the log and dashboard.

## 19. Rival System

The MVP should include one main rival councillor.

The rival should:

- Claim credit for ignored visible issues.
- Brief against the player.
- Attend events the player misses.
- Compete for Assembly selection.
- Gain from player overreach.
- Occasionally cooperate if relationship is tolerable.

Rival variables:

- reputation.
- local visibility.
- branch support.
- relationship with player.
- ambition.
- current narrative.

Rival actions should not happen every time. They should be frequent enough to create pressure.

## 20. Career Progression

Career progression must be driven by routine performance, not arbitrary points.

Assembly selection eligibility should consider:

- Reputation.
- Local base.
- Branch support.
- Career momentum.
- Faction support.
- Rival threat.
- Media profile.
- Record of handled local stories.

Good casework matters. Good media matters. Party loyalty matters. Handling local stories well should make the player feel politically real.

### 20.1 Candidate Selection Trigger

When thresholds are reached, the system should create a story beat:

**Assembly Selection Opening**

Choices:

- Formally seek selection.
- Privately test support.
- Ask faction contact for backing.
- Defer and build local base.
- Undermine rival quietly.

This should not be automatic promotion.

## 21. Initial Implementation Plan

### Step 1: Build Core Models

Implement:

- GameDate.
- TimeSlot.
- DayTemplate.
- DailyBeat.
- ContentPack.
- StoryArc.
- DecisionOption.
- ActorReaction.
- Player.
- CareerState.
- SimulationState.

### Step 2: Build Day Generator

Generate one day at a time.

Inputs:

- Weekday.
- Active story arcs.
- Player role.
- Current pressures.
- Scheduled obligations.

Outputs:

- List of DailyBeat objects grouped by time slot.

### Step 3: Build Three Story Chains

Implement:

- Car accident hotspot.
- Noise complaint and business owner dispute.
- Stormont campaign help request.

Each chain should have at least three stages and remembered flags.

### Step 4: Build Decision Application

When the player chooses a decision:

- Apply effects.
- Set flags.
- Create reactions.
- Update story stage.
- Schedule follow-up.
- Advance time.
- Write log entry.

### Step 5: Build Ignored Item Processing

When time advances:

- Check expired beats.
- Apply ignored effects.
- Give rival a chance to act.
- Schedule escalations.
- Write log entries.

### Step 6: Build Dashboard UI

Make the dashboard functional first.

Required cards:

- Today’s Flow.
- Active Local Story.
- Inbox.
- Ward Mood.
- Rival Watch.
- Career Track.
- Recent Consequence.

### Step 7: Build Decision and Result UI

The player must be able to:

- Open a beat.
- Read context.
- Compare choices.
- Choose one.
- See a descriptive result.
- Return to dashboard.

### Step 8: Add Tests

Test:

- Day generation.
- Story arc progression.
- Decision effect application.
- Ignored item processing.
- Rival intervention.
- Career eligibility.
- Dashboard state summaries.

## 22. Example Beat Definition

Example object shape in Python-like pseudocode:

```python
DailyBeat(
    id="car_crash_phone_call_stage_1",
    title="Phone call: accident at Ballyholme junction",
    description=(
        "A residents' association contact rings to say there has been another "
        "collision at a junction they have complained about before. They say "
        "people are shaken and a local paper may already be asking questions."
    ),
    beat_type=BeatType.PHONE_CALL,
    time_slot=TimeSlot.MORNING,
    urgency=Urgency.HIGH,
    linked_story_arc_id="car_accident_hotspot",
    decision_options=[
        "go_to_scene",
        "contact_officer_first",
        "post_publicly_now",
        "delegate_to_colleague",
        "log_for_later",
    ],
    ignored_effect="rival_may_attend_scene",
    expiry_slot=TimeSlot.AFTERNOON,
)
```

## 23. Example Decision Definition

```python
DecisionOption(
    id="go_to_scene",
    label="Go to the scene personally",
    description=(
        "Leave your planned admin block and go to the junction. Speak to "
        "residents, check the road layout and gather details before deciding "
        "whether to go public."
    ),
    handling_style=HandlingStyle.PERSONAL_WARD_WORK,
    stamina_cost=14,
    influence_cost=0,
    likely_upside="Residents feel listened to and you gain ownership of the issue.",
    likely_risk="You lose time and raise expectations for quick action.",
    effects={
        "player.resident_trust": +4,
        "player.ward_visibility": +3,
        "story.player_ownership": +8,
        "story.pressure_level": +1,
    },
    flags_set=["visited_scene", "resident_expectations_high"],
    actor_reactions=["resident_thanks_player", "rival_watches_issue"],
    result_text="You spend forty minutes at the junction speaking to residents."
)
```

## 24. Example Result

Headline:

**Residents see you at the junction**

Narrative:

You leave the morning inbox half-finished and head to the accident hotspot. The residents are shaken but appreciative. One parent says this is the first time an elected representative has actually stood there and watched the traffic pattern. You avoid blaming anyone yet, but promise to chase the roads officer before the end of the day.

Key changes:

- Resident Trust +4
- Ward Visibility +3
- Casework Backlog +1
- Stamina -14
- Story Ownership +8
- Resident Expectations +1

System reaction:

Your rival does not intervene yet, but a branch member messages to ask whether you are turning this into a campaign issue.

Story progression:

Car Accident Hotspot moves to Stage 2: Pressure on officers.

Follow-up created:

Roads officer follow-up is added to Afternoon.

## 25. README Notes for the Repository

The repository should include a README section explaining that this is not yet a full political simulator. It is a councillor routine prototype. The design goal is to prove that politics can feel natural through daily work, story memory and actor reactions.

Suggested README wording:

> This prototype focuses on the daily life of a councillor. The player handles emails, resident complaints, local incidents, officer meetings, council business, community events, local media and party pressure. The game does not use passive weekly drift. Things change because the player acts, ignores something, or another actor moves first.

## 26. Acceptance Criteria

The implementation is acceptable when:

- The app launches into a dashboard.
- The dashboard shows a believable day timeline.
- The player can check inbox-style issues.
- The player can respond to a phone call or local issue.
- Each issue has multiple handling styles.
- Choices produce descriptive outcomes.
- Story arcs remember previous choices.
- Follow-up beats appear on later slots or later days.
- Ignoring visible issues can help the rival.
- Council officers, residents, journalists and party figures can react.
- Career progress toward Assembly selection is visible.
- The interface feels like a working political desk, not a random event feed.

## 27. Final Design Summary

The game should be made from:

- Templates that shape the day.
- Beats that create playable scenes.
- Content packs that provide local political issues.
- Decisions that define how the player handles problems.
- Memory flags that preserve continuity.
- Actor reactions that create drama.
- Follow-ups that make stories evolve.
- A dashboard that makes the work readable at a glance.

In short:

> Templates create the day. Beats create the scenes. Choices create consequences. Memory creates continuity. Actors create politics. Follow-ups create story.
