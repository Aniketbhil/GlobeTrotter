import uuid

from fastapi.testclient import TestClient

from app.core.security import create_access_token, hash_password
from app.features.auth.models import User


def test_get_budget_without_token_returns_401(client: TestClient):
    random_trip_id = str(uuid.uuid4())
    res = client.get(f"/api/trips/{random_trip_id}/budget")
    assert res.status_code == 401


def test_get_budget_unowned_trip_returns_404(
    client: TestClient, db_session, user_token: str
):
    user2 = User(
        email="user2_budget@globetrotter.com",
        hashed_password=hash_password("Password123!"),
        first_name="User2",
        last_name="Budget",
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
        f"/api/trips/{trip2['id']}/budget",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res.status_code == 404


def test_put_budget_override_without_token_returns_401(client: TestClient):
    random_trip_id = str(uuid.uuid4())
    random_stop_id = str(uuid.uuid4())
    res = client.put(
        f"/api/trips/{random_trip_id}/stops/{random_stop_id}/budget-override",
        json={"transport_cost_override": 100.0},
    )
    assert res.status_code == 401


def test_put_budget_override_mismatched_stop_returns_404(
    client: TestClient, admin_token: str, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    c_id = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "CityB1", "country": "CountryB1"},
    ).json()["id"]

    trip1 = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Trip 1",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    ).json()
    trip2 = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Trip 2",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    ).json()

    stop2 = client.post(
        f"/api/trips/{trip2['id']}/stops",
        headers=auth_user,
        json={
            "city_id": c_id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    ).json()

    # Attempt to put override on trip1 with stop2 (which belongs to trip2) -> 404
    res = client.put(
        f"/api/trips/{trip1['id']}/stops/{stop2['id']}/budget-override",
        headers=auth_user,
        json={"transport_cost_override": 150.0},
    )
    assert res.status_code == 404


def test_formula_driven_budget_and_nights_calculation(
    client: TestClient, admin_token: str, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    # City with cost_index 10.0
    c_res = client.post(
        "/api/cities",
        headers=auth_admin,
        json={
            "name": "FormulaCity",
            "country": "FormulaCountry",
            "cost_index": 10.0,
        },
    )
    city = c_res.json()

    trip = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Formula Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    ).json()

    # Stop: Sept 1 to Sept 5 (5 nights inclusive)
    stop = client.post(
        f"/api/trips/{trip['id']}/stops",
        headers=auth_user,
        json={
            "city_id": city["id"],
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    ).json()

    res = client.get(f"/api/trips/{trip['id']}/budget", headers=auth_user)
    assert res.status_code == 200
    data = res.json()

    assert len(data["stops"]) == 1
    stop_b = data["stops"][0]
    assert stop_b["stop_id"] == stop["id"]
    assert stop_b["nights"] == 5

    # Formula costs:
    # transport = 5 nights * 10.0 cost_index * 15.0 = 750.0
    # stay = 5 nights * 10.0 cost_index * 25.0 = 1250.0
    # meals = 5 nights * 30.0 = 150.0
    assert stop_b["transport_cost"] == 750.0
    assert stop_b["transport_is_override"] is False
    assert stop_b["stay_cost"] == 1250.0
    assert stop_b["stay_is_override"] is False
    assert stop_b["meal_cost"] == 150.0
    assert stop_b["activity_cost"] == 0.0
    assert stop_b["stop_total"] == 750.0 + 1250.0 + 150.0 + 0.0

    # Category totals
    cat = data["category_totals"]
    assert cat["transport"] == 750.0
    assert cat["stay"] == 1250.0
    assert cat["meals"] == 150.0
    assert cat["activities"] == 0.0
    assert data["trip_total_cost"] == 2150.0

    # No threshold -> is_overbudget is null
    assert data["daily_budget_threshold"] is None
    assert data["overbudget_day_count"] == 0
    for day in data["days"]:
        assert day["is_overbudget"] is None


def test_partial_override_and_reverting_override_to_null(
    client: TestClient, admin_token: str, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    c_id = client.post(
        "/api/cities",
        headers=auth_admin,
        json={
            "name": "OverrideCity",
            "country": "OverrideCountry",
            "cost_index": 5.0,
        },
    ).json()["id"]

    trip = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Override Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-03",
        },
    ).json()

    stop = client.post(
        f"/api/trips/{trip['id']}/stops",
        headers=auth_user,
        json={
            "city_id": c_id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-03",
        },
    ).json()

    # Step 1: PUT override setting ONLY transport_cost_override = 500.0
    put1 = client.put(
        f"/api/trips/{trip['id']}/stops/{stop['id']}/budget-override",
        headers=auth_user,
        json={"transport_cost_override": 500.0},
    )
    assert put1.status_code == 200
    assert put1.json()["transport_cost_override"] == 500.0

    get1 = client.get(f"/api/trips/{trip['id']}/budget", headers=auth_user).json()
    stop_b1 = get1["stops"][0]
    assert stop_b1["transport_cost"] == 500.0
    assert stop_b1["transport_is_override"] is True
    # Stay remains formula: 3 nights * 5.0 * 25.0 = 375.0
    assert stop_b1["stay_cost"] == 375.0
    assert stop_b1["stay_is_override"] is False

    # Step 2: PUT override setting stay_cost_override = 800.0 (transport untouched)
    put2 = client.put(
        f"/api/trips/{trip['id']}/stops/{stop['id']}/budget-override",
        headers=auth_user,
        json={"stay_cost_override": 800.0},
    )
    assert put2.status_code == 200

    get2 = client.get(f"/api/trips/{trip['id']}/budget", headers=auth_user).json()
    stop_b2 = get2["stops"][0]
    assert stop_b2["transport_cost"] == 500.0
    assert stop_b2["transport_is_override"] is True
    assert stop_b2["stay_cost"] == 800.0
    assert stop_b2["stay_is_override"] is True

    # Step 3: PUT override explicitly setting transport_cost_override = null (reverts to formula)
    put3 = client.put(
        f"/api/trips/{trip['id']}/stops/{stop['id']}/budget-override",
        headers=auth_user,
        json={"transport_cost_override": None},
    )
    assert put3.status_code == 200

    get3 = client.get(f"/api/trips/{trip['id']}/budget", headers=auth_user).json()
    stop_b3 = get3["stops"][0]
    # Transport formula: 3 nights * 5.0 * 15.0 = 225.0
    assert stop_b3["transport_cost"] == 225.0
    assert stop_b3["transport_is_override"] is False
    assert stop_b3["stay_cost"] == 800.0
    assert stop_b3["stay_is_override"] is True


def test_daily_budget_threshold_and_overbudget_day_count(
    client: TestClient, admin_token: str, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    c_id = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "ThreshCity", "country": "ThreshCountry"},
    ).json()["id"]
    a1_id = client.post(
        "/api/activities",
        headers=auth_admin,
        json={
            "city_id": c_id,
            "name": "Big Activity",
            "type": "sightseeing",
            "cost": 100.0,
        },
    ).json()["id"]
    a2_id = client.post(
        "/api/activities",
        headers=auth_admin,
        json={
            "city_id": c_id,
            "name": "Small Activity",
            "type": "food",
            "cost": 20.0,
        },
    ).json()["id"]

    trip = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Threshold Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-03",
        },
    ).json()

    stop = client.post(
        f"/api/trips/{trip['id']}/stops",
        headers=auth_user,
        json={
            "city_id": c_id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-03",
        },
    ).json()

    # Day 1 (Sept 1): 100.0
    client.post(
        f"/api/trips/{trip['id']}/stops/{stop['id']}/activities",
        headers=auth_user,
        json={"activity_id": a1_id, "scheduled_date": "2026-09-01"},
    )
    # Day 2 (Sept 2): 20.0
    client.post(
        f"/api/trips/{trip['id']}/stops/{stop['id']}/activities",
        headers=auth_user,
        json={"activity_id": a2_id, "scheduled_date": "2026-09-02"},
    )

    # GET Budget with daily_budget_threshold = 50.0
    res = client.get(
        f"/api/trips/{trip['id']}/budget?daily_budget_threshold=50.0",
        headers=auth_user,
    )
    assert res.status_code == 200
    data = res.json()

    assert data["daily_budget_threshold"] == 50.0
    assert data["overbudget_day_count"] == 1

    days = data["days"]
    assert days[0]["date"] == "2026-09-01"
    assert days[0]["activity_cost"] == 100.0
    assert days[0]["is_overbudget"] is True

    assert days[1]["date"] == "2026-09-02"
    assert days[1]["activity_cost"] == 20.0
    assert days[1]["is_overbudget"] is False

    assert days[2]["date"] == "2026-09-03"
    assert days[2]["activity_cost"] == 0.0
    assert days[2]["is_overbudget"] is False
