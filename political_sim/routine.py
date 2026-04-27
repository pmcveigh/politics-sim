from __future__ import annotations

from dataclasses import replace
from datetime import date
from typing import Dict, List

from .data import clone_decisions, routine_templates
from .models import DailyAgenda, RoutineItem, TimeSlot, Urgency


WEEKDAY_BIAS: Dict[int, Dict[str, List[str]]] = {
    0: {"obligation": ["casework_school_parking", "officer_followup_bins"], "opportunity": ["media_quote"], "complication": ["committee_vote_rates"]},
    1: {"obligation": ["committee_vote_rates", "officer_followup_bins"], "opportunity": ["media_quote"], "complication": ["casework_school_parking"]},
    2: {"obligation": ["committee_vote_rates"], "opportunity": ["residents_association_meeting"], "complication": ["media_quote"]},
    3: {"obligation": ["casework_school_parking"], "opportunity": ["residents_association_meeting"], "complication": ["officer_followup_bins"]},
    4: {"obligation": ["officer_followup_bins"], "opportunity": ["media_quote"], "complication": ["casework_school_parking"]},
    5: {"obligation": ["casework_school_parking"], "opportunity": ["residents_association_meeting"], "complication": ["media_quote"]},
    6: {"obligation": ["officer_followup_bins"], "opportunity": ["residents_association_meeting"], "complication": ["casework_school_parking"]},
}

SLOT_LAYOUT = {
    "obligation": TimeSlot.MORNING,
    "opportunity": TimeSlot.AFTERNOON,
    "complication": TimeSlot.EVENING,
}


def build_daily_routine(current_date: date, day_index: int, constituency_id: str) -> tuple[DailyAgenda, List[RoutineItem]]:
    templates = {t["id"]: t for t in routine_templates()}
    bias = WEEKDAY_BIAS[current_date.weekday()]

    rotation = day_index % len(bias["obligation"])
    obligation_id = bias["obligation"][rotation]
    opportunity_id = bias["opportunity"][day_index % len(bias["opportunity"])]
    complication_id = bias["complication"][day_index % len(bias["complication"])]

    def mk(item_id: str, slot: TimeSlot, urgency: Urgency, ttl: int) -> RoutineItem:
        t = templates[item_id]
        return RoutineItem(
            id=f"{item_id}_{day_index}_{slot.name.lower()}",
            title=t["title"],
            description=t["description"],
            category=t["category"],
            time_slot=slot,
            urgency=urgency,
            workload_cost=1,
            stamina_cost=4,
            influence_cost=0,
            expires_after_slots=ttl,
            involved_actor_ids=[],
            involved_relationships=[],
            linked_constituency_id=constituency_id,
            possible_decisions=clone_decisions(t["decisions"]),
            ignored_effect=dict(t["ignored"]),
            escalation=t["escalation"],
            slots_remaining=ttl,
        )

    items = [
        mk(obligation_id, SLOT_LAYOUT["obligation"], Urgency.HIGH, 2),
        mk(opportunity_id, SLOT_LAYOUT["opportunity"], Urgency.MEDIUM, 2),
        mk(complication_id, SLOT_LAYOUT["complication"], Urgency.HIGH, 1),
    ]

    agenda = DailyAgenda(
        date=current_date,
        day_name=current_date.strftime("%A"),
        routine_obligation_id=items[0].id,
        opportunity_id=items[1].id,
        complication_id=items[2].id,
        items_by_slot={
            TimeSlot.MORNING: [items[0].id],
            TimeSlot.AFTERNOON: [items[1].id],
            TimeSlot.EVENING: [items[2].id],
            TimeSlot.LATE_NIGHT: [],
        },
    )
    return agenda, items
