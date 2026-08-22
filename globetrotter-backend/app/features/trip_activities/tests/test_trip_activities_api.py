import uuid

from fastapi.testclient import TestClient

from app.core.security import create_access_token, hash_password
from app.features.auth.models import User


def test_post_trip_activity_without_token_returns_401(client: TestClient):
    random_trip_id = str(uuid.uuid4())
    random_stop_id = str(uuid.uuid4())
    res = client.post(
        f"/api/trips/{random_trip_id}/stops/{random_stop_id}/activities",
        json={
            "activity_id": str(uuid.uuid4()),
            "scheduled_date": "2026-09-01",
        },
    )
    assert res.status_code == 401


def test_post_trip_activity_unowned_trip_or_mismatched_stop_returns_404(
    client: TestClient, db_session, user_token: str, admin_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    c_res = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "Marseille", "country": "France"},
    )
    c_id = c_res.json()["id"]
    a_res = client.post(
        "/api/activities",
        headers=auth_admin,
        json={
            "city_id": c_id,
            "name": "Boat Tour",
            "type": "sightseeing",
            "cost": 30.0,
        },
    )
    act_id = a_res.json()["id"]

    user2 = User(
        email="user2_ta@globetrotter.com",
        hashed_password=hash_password("Password123!"),
        first_name="User2",
        last_name="TA",
    )
    db_session.add(user2)
    db_session.commit()
    token2 = create_access_token(subject=str(user2.id))
    auth_user2 = {"Authorization": f"Bearer {token2}"}

    trip2 = client.post(
        "/api/trips",
        headers=auth_user2,
        json={
            "name": "User 2 Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    ).json()
    stop2 = client.post(
        f"/api/trips/{trip2['id']}/stops",
        headers=auth_user2,
        json={
            "city_id": c_id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    ).json()

    res1 = client.post(
        f"/api/trips/{trip2['id']}/stops/{stop2['id']}/activities",
        headers=auth_user,
        json={"activity_id": act_id, "scheduled_date": "2026-09-01"},
    )
    assert res1.status_code == 404

    trip1 = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "User 1 Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    ).json()
    client.post(
        f"/api/trips/{trip1['id']}/stops",
        headers=auth_user,
        json={
            "city_id": c_id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    )

    res2 = client.post(
        f"/api/trips/{trip1['id']}/stops/{stop2['id']}/activities",
        headers=auth_user,
        json={"activity_id": act_id, "scheduled_date": "2026-09-01"},
    )
    assert res2.status_code == 404


def test_post_trip_activity_nonexistent_activity_returns_404(
    client: TestClient, admin_token: str, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    c_id = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "Bordeaux", "country": "France"},
    ).json()["id"]
    trip_id = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Bordeaux Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    ).json()["id"]
    stop_id = client.post(
        f"/api/trips/{trip_id}/stops",
        headers=auth_user,
        json={
            "city_id": c_id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    ).json()["id"]

    random_act_id = str(uuid.uuid4())
    res = client.post(
        f"/api/trips/{trip_id}/stops/{stop_id}/activities",
        headers=auth_user,
        json={"activity_id": random_act_id, "scheduled_date": "2026-09-01"},
    )
    assert res.status_code == 404


def test_post_trip_activity_date_outside_stop_range_returns_422(
    client: TestClient, admin_token: str, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    c_id = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "Toulouse", "country": "France"},
    ).json()["id"]
    act_id = client.post(
        "/api/activities",
        headers=auth_admin,
        json={
            "city_id": c_id,
            "name": "Museum Visit",
            "type": "culture",
            "cost": 15.0,
        },
    ).json()["id"]

    trip_id = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Toulouse Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    ).json()["id"]
    stop_id = client.post(
        f"/api/trips/{trip_id}/stops",
        headers=auth_user,
        json={
            "city_id": c_id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    ).json()["id"]

    res = client.post(
        f"/api/trips/{trip_id}/stops/{stop_id}/activities",
        headers=auth_user,
        json={"activity_id": act_id, "scheduled_date": "2026-09-06"},
    )
    assert res.status_code == 422


def test_post_trip_activity_auto_increments_per_day_and_effective_cost(
    client: TestClient, admin_token: str, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    c_id = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "Strasbourg", "country": "France"},
    ).json()["id"]
    a1_id = client.post(
        "/api/activities",
        headers=auth_admin,
        json={
            "city_id": c_id,
            "name": "Cathedral Tour",
            "type": "sightseeing",
            "cost": 10.0,
        },
    ).json()["id"]
    a2_id = client.post(
        "/api/activities",
        headers=auth_admin,
        json={
            "city_id": c_id,
            "name": "Boat Cruise",
            "type": "sightseeing",
            "cost": 25.0,
        },
    ).json()["id"]

    trip_id = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Alsace Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    ).json()["id"]
    stop_id = client.post(
        f"/api/trips/{trip_id}/stops",
        headers=auth_user,
        json={
            "city_id": c_id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    ).json()["id"]

    ta1_res = client.post(
        f"/api/trips/{trip_id}/stops/{stop_id}/activities",
        headers=auth_user,
        json={"activity_id": a1_id, "scheduled_date": "2026-09-01"},
    )
    assert ta1_res.status_code == 201
    ta1 = ta1_res.json()
    assert ta1["order_index"] == 1
    assert float(ta1["effective_cost"]) == 10.0
    assert ta1["activity"]["name"] == "Cathedral Tour"

    ta2_res = client.post(
        f"/api/trips/{trip_id}/stops/{stop_id}/activities",
        headers=auth_user,
        json={
            "activity_id": a2_id,
            "scheduled_date": "2026-09-01",
            "cost_override": 18.0,
        },
    )
    assert ta2_res.status_code == 201
    ta2 = ta2_res.json()
    assert ta2["order_index"] == 2
    assert float(ta2["effective_cost"]) == 18.0
    assert float(ta2["cost_override"]) == 18.0

    ta3_res = client.post(
        f"/api/trips/{trip_id}/stops/{stop_id}/activities",
        headers=auth_user,
        json={"activity_id": a1_id, "scheduled_date": "2026-09-02"},
    )
    assert ta3_res.status_code == 201
    ta3 = ta3_res.json()
    assert ta3["order_index"] == 1

    get_res = client.get(
        f"/api/trips/{trip_id}/stops/{stop_id}/activities", headers=auth_user
    )
    assert get_res.status_code == 200
    grouped = get_res.json()
    assert "2026-09-01" in grouped
    assert "2026-09-02" in grouped
    assert len(grouped["2026-09-01"]) == 2
    assert len(grouped["2026-09-02"]) == 1


def test_reorder_trip_activities_success_and_cross_day_error(
    client: TestClient, admin_token: str, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    c_id = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "Lille", "country": "France"},
    ).json()["id"]
    a1_id = client.post(
        "/api/activities",
        headers=auth_admin,
        json={
            "city_id": c_id,
            "name": "Belfry Visit",
            "type": "sightseeing",
            "cost": 8.0,
        },
    ).json()["id"]
    a2_id = client.post(
        "/api/activities",
        headers=auth_admin,
        json={
            "city_id": c_id,
            "name": "Art Museum",
            "type": "culture",
            "cost": 12.0,
        },
    ).json()["id"]

    trip_id = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Lille Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    ).json()["id"]
    stop_id = client.post(
        f"/api/trips/{trip_id}/stops",
        headers=auth_user,
        json={
            "city_id": c_id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    ).json()["id"]

    ta1_id = client.post(
        f"/api/trips/{trip_id}/stops/{stop_id}/activities",
        headers=auth_user,
        json={"activity_id": a1_id, "scheduled_date": "2026-09-01"},
    ).json()["id"]
    ta2_id = client.post(
        f"/api/trips/{trip_id}/stops/{stop_id}/activities",
        headers=auth_user,
        json={"activity_id": a2_id, "scheduled_date": "2026-09-01"},
    ).json()["id"]

    ta3_id = client.post(
        f"/api/trips/{trip_id}/stops/{stop_id}/activities",
        headers=auth_user,
        json={"activity_id": a1_id, "scheduled_date": "2026-09-02"},
    ).json()["id"]

    bad_reorder = client.patch(
        f"/api/trips/{trip_id}/stops/{stop_id}/activities/reorder",
        headers=auth_user,
        json={"scheduled_date": "2026-09-01", "ordered_ids": [ta1_id, ta3_id]},
    )
    assert bad_reorder.status_code == 422

    valid_reorder = client.patch(
        f"/api/trips/{trip_id}/stops/{stop_id}/activities/reorder",
        headers=auth_user,
        json={"scheduled_date": "2026-09-01", "ordered_ids": [ta2_id, ta1_id]},
    )
    assert valid_reorder.status_code == 200
    reordered_items = valid_reorder.json()
    assert reordered_items[0]["id"] == ta2_id
    assert reordered_items[0]["order_index"] == 1
    assert reordered_items[1]["id"] == ta1_id
    assert reordered_items[1]["order_index"] == 2


def test_delete_trip_activity_preserves_remaining_order_and_grouping(
    client: TestClient, admin_token: str, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    c_id = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "Nantes", "country": "France"},
    ).json()["id"]
    a_id = client.post(
        "/api/activities",
        headers=auth_admin,
        json={
            "city_id": c_id,
            "name": "Castle",
            "type": "sightseeing",
            "cost": 10.0,
        },
    ).json()["id"]

    trip_id = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Nantes Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    ).json()["id"]
    stop_id = client.post(
        f"/api/trips/{trip_id}/stops",
        headers=auth_user,
        json={
            "city_id": c_id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    ).json()["id"]

    ta1_id = client.post(
        f"/api/trips/{trip_id}/stops/{stop_id}/activities",
        headers=auth_user,
        json={"activity_id": a_id, "scheduled_date": "2026-09-01"},
    ).json()["id"]
    ta2_id = client.post(
        f"/api/trips/{trip_id}/stops/{stop_id}/activities",
        headers=auth_user,
        json={"activity_id": a_id, "scheduled_date": "2026-09-01"},
    ).json()["id"]
    ta3_id = client.post(
        f"/api/trips/{trip_id}/stops/{stop_id}/activities",
        headers=auth_user,
        json={"activity_id": a_id, "scheduled_date": "2026-09-01"},
    ).json()["id"]

    del_res = client.delete(
        f"/api/trips/{trip_id}/stops/{stop_id}/activities/{ta2_id}",
        headers=auth_user,
    )
    assert del_res.status_code == 204

    get_res = client.get(
        f"/api/trips/{trip_id}/stops/{stop_id}/activities", headers=auth_user
    )
    assert get_res.status_code == 200
    day1_items = get_res.json()["2026-09-01"]
    assert len(day1_items) == 2
    assert day1_items[0]["id"] == ta1_id
    assert day1_items[0]["order_index"] == 1
    assert day1_items[1]["id"] == ta3_id
    assert day1_items[1]["order_index"] == 3


def test_delete_catalog_activity_with_referencing_trip_activity_returns_409(
    client: TestClient, admin_token: str, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    c_id = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "Rennes", "country": "France"},
    ).json()["id"]
    act_id = client.post(
        "/api/activities",
        headers=auth_admin,
        json={
            "city_id": c_id,
            "name": "Park Walk",
            "type": "other",
            "cost": 0.0,
        },
    ).json()["id"]

    trip_id = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Rennes Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    ).json()["id"]
    stop_id = client.post(
        f"/api/trips/{trip_id}/stops",
        headers=auth_user,
        json={
            "city_id": c_id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    ).json()["id"]

    client.post(
        f"/api/trips/{trip_id}/stops/{stop_id}/activities",
        headers=auth_user,
        json={"activity_id": act_id, "scheduled_date": "2026-09-01"},
    )

    del_act_res = client.delete(f"/api/activities/{act_id}", headers=auth_admin)
    assert del_act_res.status_code == 409
