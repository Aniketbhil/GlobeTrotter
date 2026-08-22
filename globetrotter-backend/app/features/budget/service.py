from sqlalchemy.orm import Session

from app.core.config import settings
from app.features.budget.models import StopBudgetOverride
from app.features.budget.schemas import (
    BudgetCategoryTotals,
    BudgetResponse,
    DayBudgetEntry,
    StopBudgetBreakdown,
    StopBudgetOverrideUpsert,
)
from app.features.cities.schemas import CityResponse
from app.features.itinerary.service import (
    build_trip_itinerary as build_trip_itinerary_service,
)
from app.features.stops.models import Stop
from app.features.stops.service import list_stops as list_stops_service
from app.features.trip_activities.service import (
    list_trip_activities as list_trip_activities_service,
)
from app.features.trips.models import Trip


def upsert_stop_budget_override(
    db: Session, stop: Stop, data: StopBudgetOverrideUpsert
) -> StopBudgetOverride:
    override = (
        db.query(StopBudgetOverride)
        .filter(StopBudgetOverride.stop_id == stop.id)
        .first()
    )
    if not override:
        override = StopBudgetOverride(stop_id=stop.id)
        db.add(override)

    fields_set = data.model_fields_set
    if "transport_cost_override" in fields_set:
        override.transport_cost_override = data.transport_cost_override
    if "stay_cost_override" in fields_set:
        override.stay_cost_override = data.stay_cost_override

    db.commit()
    db.refresh(override)
    return override


def compute_stop_breakdown(db: Session, stop: Stop) -> StopBudgetBreakdown:
    # nights is computed inclusive of both start and end date
    nights = (stop.end_date - stop.start_date).days + 1

    override = (
        db.query(StopBudgetOverride)
        .filter(StopBudgetOverride.stop_id == stop.id)
        .first()
    )

    # Note: city.cost_index may be null; treat null as 0.0 for formula calculation.
    cost_idx = float(stop.city.cost_index) if stop.city.cost_index is not None else 0.0

    if override and override.transport_cost_override is not None:
        transport_cost = float(override.transport_cost_override)
        transport_is_override = True
    else:
        transport_cost = nights * cost_idx * settings.TRANSPORT_COST_MULTIPLIER
        transport_is_override = False

    if override and override.stay_cost_override is not None:
        stay_cost = float(override.stay_cost_override)
        stay_is_override = True
    else:
        stay_cost = nights * cost_idx * settings.STAY_COST_MULTIPLIER
        stay_is_override = False

    # Assumption: meal cost is computed as nights * MEAL_COST_PER_DAY with no manual override in this pass.
    meal_cost = nights * settings.MEAL_COST_PER_DAY

    stop_acts = list_trip_activities_service(db, stop)
    activity_cost = sum(
        float(a.cost_override if a.cost_override is not None else a.activity.cost)
        for a in stop_acts
    )

    stop_total = transport_cost + stay_cost + meal_cost + activity_cost

    return StopBudgetBreakdown(
        stop_id=stop.id,
        city=CityResponse.model_validate(stop.city),
        nights=nights,
        transport_cost=transport_cost,
        transport_is_override=transport_is_override,
        stay_cost=stay_cost,
        stay_is_override=stay_is_override,
        meal_cost=meal_cost,
        activity_cost=activity_cost,
        stop_total=stop_total,
    )


def build_trip_budget(
    db: Session, trip: Trip, daily_budget_threshold: float | None = None
) -> BudgetResponse:
    stops = list_stops_service(db, trip)
    stop_breakdowns = [compute_stop_breakdown(db, s) for s in stops]

    itinerary = build_trip_itinerary_service(db, trip)
    day_entries: list[DayBudgetEntry] = []
    overbudget_count = 0

    for day_item in itinerary.days:
        act_cost = day_item.day_total_cost
        if daily_budget_threshold is not None:
            is_over = act_cost > daily_budget_threshold
            if is_over:
                overbudget_count += 1
        else:
            is_over = None

        day_entries.append(
            DayBudgetEntry(
                date=day_item.date,
                activity_cost=act_cost,
                is_overbudget=is_over,
            )
        )

    total_transport = sum(b.transport_cost for b in stop_breakdowns)
    total_stay = sum(b.stay_cost for b in stop_breakdowns)
    total_meals = sum(b.meal_cost for b in stop_breakdowns)
    total_activities = sum(b.activity_cost for b in stop_breakdowns)

    category_totals = BudgetCategoryTotals(
        transport=total_transport,
        stay=total_stay,
        meals=total_meals,
        activities=total_activities,
    )
    trip_total = total_transport + total_stay + total_meals + total_activities

    return BudgetResponse(
        trip_id=trip.id,
        trip_name=trip.name,
        stops=stop_breakdowns,
        days=day_entries,
        category_totals=category_totals,
        trip_total_cost=trip_total,
        daily_budget_threshold=daily_budget_threshold,
        overbudget_day_count=overbudget_count,
    )
