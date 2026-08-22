import uuid

from fastapi.testclient import TestClient

from app.core.security import create_access_token, hash_password
from app.features.auth.models import User


def test_get_itinerary_without_token_returns_401(client: TestClient):
    random_trip_id = str(uuid.uuid4())
    res = client.get(f"/api/trips/{random_trip_id}/itinerary")
    assert res.status_code == 401


def test_get_itinerary_unowned_trip_returns_404(
    client: TestClient, db_session, user_token: str
):
    user2 = User(
        email="user2_itin@globetrotter.com",
        hashed_password=hash_password("Password123!"),
        first_name="User2",
        last_name="Itin",
    )
    db_session.add(user2)
    db_session.commit()
    token2 = create_access_token(subject=str(user2.id))

    trip2 = client.post(
        "/api/trips",
        headers={"Authorization": f"Bearer {token2}"},
        json={
            "name": "User 2 Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    ).json()

    res = client.get(
        f"/api/trips/{trip2['id']}/itinerary",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res.status_code == 404


def test_get_itinerary_trip_with_no_stops_returns_empty_days(
    client: TestClient, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    trip = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Empty Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    ).json()

    res = client.get(f"/api/trips/{trip['id']}/itinerary", headers=auth_user)
    assert res.status_code == 200
    data = res.json()
    assert data["trip_id"] == trip["id"]
    assert data["days"] == []
    assert data["trip_total_cost"] == 0.0


def test_get_itinerary_multi_stop_and_activity_costs(
    client: TestClient, admin_token: str, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    c1 = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "ParisItin", "country": "France"},
    ).json()
    c2 = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "RomeItin", "country": "Italy"},
    ).json()

    a1 = client.post(
        "/api/activities",
        headers=auth_admin,
        json={
            "city_id": c1["id"],
            "name": "Eiffel Tower",
            "type": "sightseeing",
            "cost": 30.0,
        },
    ).json()
    a2 = client.post(
        "/api/activities",
        headers=auth_admin,
        json={
            "city_id": c1["id"],
            "name": "Louvre",
            "type": "culture",
            "cost": 20.0,
        },
    ).json()

    trip = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Europe Grand Tour",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    ).json()

    # Stop 1: Paris, Sept 1-3 (3 days)
    stop1 = client.post(
        f"/api/trips/{trip['id']}/stops",
        headers=auth_user,
        json={
            "city_id": c1["id"],
            "start_date": "2026-09-01",
            "end_date": "2026-09-03",
        },
    ).json()

    # Stop 2: Rome, Sept 4-5 (2 days)
    client.post(
        f"/api/trips/{trip['id']}/stops",
        headers=auth_user,
        json={
            "city_id": c2["id"],
            "start_date": "2026-09-04",
            "end_date": "2026-09-05",
        },
    )

    # Schedule activities on Stop 1 Day 1 (Sept 1): Eiffel Tower (30.0) + Louvre (override 25.0)
    client.post(
        f"/api/trips/{trip['id']}/stops/{stop1['id']}/activities",
        headers=auth_user,
        json={"activity_id": a1["id"], "scheduled_date": "2026-09-01"},
    )
    client.post(
        f"/api/trips/{trip['id']}/stops/{stop1['id']}/activities",
        headers=auth_user,
        json={
            "activity_id": a2["id"],
            "scheduled_date": "2026-09-01",
            "cost_override": 25.0,
        },
    )

    # GET Itinerary
    res = client.get(f"/api/trips/{trip['id']}/itinerary", headers=auth_user)
    assert res.status_code == 200
    data = res.json()

    # Total 5 days (3 for Paris, 2 for Rome)
    assert len(data["days"]) == 5

    # Day 1 (Sept 1): 2 activities, day_total_cost = 30 + 25 = 55.0
    day1 = data["days"][0]
    assert day1["date"] == "2026-09-01"
    assert day1["city"]["name"] == "ParisItin"
    assert len(day1["activities"]) == 2
    assert day1["day_total_cost"] == 55.0

    # Day 2 (Sept 2): 0 activities, day_total_cost = 0.0
    day2 = data["days"][1]
    assert day2["date"] == "2026-09-02"
    assert len(day2["activities"]) == 0
    assert day2["day_total_cost"] == 0.0

    # Stop 2 Day 1 (Sept 4): Rome city nested
    day4 = data["days"][3]
    assert day4["date"] == "2026-09-04"
    assert day4["city"]["name"] == "RomeItin"

    assert data["trip_total_cost"] == 55.0


def test_get_calendar_without_token_returns_401(client: TestClient):
    res = client.get("/api/trips/calendar?year=2026&month=9")
    assert res.status_code == 401


def test_get_calendar_user_isolation(client: TestClient, db_session, user_token: str):
    auth_user = {"Authorization": f"Bearer {user_token}"}

    client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "User 1 Sept Trip",
            "start_date": "2026-09-10",
            "end_date": "2026-09-15",
        },
    )

    user2 = User(
        email="user2_cal@globetrotter.com",
        hashed_password=hash_password("Password123!"),
        first_name="User2",
        last_name="Cal",
    )
    db_session.add(user2)
    db_session.commit()
    token2 = create_access_token(subject=str(user2.id))

    client.post(
        "/api/trips",
        headers={"Authorization": f"Bearer {token2}"},
        json={
            "name": "User 2 Sept Trip",
            "start_date": "2026-09-12",
            "end_date": "2026-09-18",
        },
    )

    res = client.get("/api/trips/calendar?year=2026&month=9", headers=auth_user)
    assert res.status_code == 200
    names = [t["name"] for t in res.json()["trips"]]
    assert "User 1 Sept Trip" in names
    assert "User 2 Sept Trip" not in names


def test_get_calendar_boundary_overlap_and_out_of_month(
    client: TestClient, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}

    # Trip 1: starts Aug 25, ends Sept 5 (starts before Sept, ends inside Sept)
    client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Overlap Start Trip",
            "start_date": "2026-08-25",
            "end_date": "2026-09-05",
        },
    )

    # Trip 2: starts Sept 25, ends Oct 5 (starts inside Sept, ends after Sept)
    client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Overlap End Trip",
            "start_date": "2026-09-25",
            "end_date": "2026-10-05",
        },
    )

    # Trip 3: starts Nov 1, ends Nov 10 (entirely outside Sept)
    client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Outside Trip",
            "start_date": "2026-11-01",
            "end_date": "2026-11-10",
        },
    )

    res = client.get("/api/trips/calendar?year=2026&month=9", headers=auth_user)
    assert res.status_code == 200
    trips = res.json()["trips"]
    names = [t["name"] for t in trips]
    assert "Overlap Start Trip" in names
    assert "Overlap End Trip" in names
    assert "Outside Trip" not in names


def test_get_calendar_invalid_month_returns_422(client: TestClient, user_token: str):
    res = client.get(
        "/api/trips/calendar?year=2026&month=13",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res.status_code == 422
