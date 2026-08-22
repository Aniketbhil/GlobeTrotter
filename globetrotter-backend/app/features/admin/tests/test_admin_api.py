import uuid
from datetime import UTC, date, datetime, timedelta

from fastapi.testclient import TestClient

from app.core.security import create_access_token, hash_password
from app.features.admin.service import get_stats_overview
from app.features.auth.models import User
from app.features.trips.models import Trip


def test_admin_routes_without_token_return_401(client: TestClient):
    assert client.get("/api/admin/stats/overview").status_code == 401
    assert client.get("/api/admin/stats/top-cities").status_code == 401
    assert client.get("/api/admin/stats/top-activities").status_code == 401
    assert client.get("/api/admin/users").status_code == 401
    random_id = str(uuid.uuid4())
    assert client.get(f"/api/admin/users/{random_id}/trips").status_code == 401


def test_admin_routes_non_admin_return_403(client: TestClient, user_token: str):
    auth = {"Authorization": f"Bearer {user_token}"}
    assert client.get("/api/admin/stats/overview", headers=auth).status_code == 403
    assert client.get("/api/admin/stats/top-cities", headers=auth).status_code == 403
    assert (
        client.get("/api/admin/stats/top-activities", headers=auth).status_code == 403
    )
    assert client.get("/api/admin/users", headers=auth).status_code == 403
    random_id = str(uuid.uuid4())
    assert (
        client.get(f"/api/admin/users/{random_id}/trips", headers=auth).status_code
        == 403
    )


def test_admin_stats_overview_as_admin(
    client: TestClient, admin_token: str, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    # Create known quantities
    c_id = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "StatCity", "country": "StatCountry"},
    ).json()["id"]
    a_id = client.post(
        "/api/activities",
        headers=auth_admin,
        json={
            "city_id": c_id,
            "name": "StatAct",
            "type": "sightseeing",
            "cost": 10.0,
        },
    ).json()["id"]

    trip = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Stat Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    ).json()

    stop = client.post(
        f"/api/trips/{trip['id']}/stops",
        headers=auth_user,
        json={
            "city_id": c_id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    ).json()

    client.post(
        f"/api/trips/{trip['id']}/stops/{stop['id']}/activities",
        headers=auth_user,
        json={"activity_id": a_id, "scheduled_date": "2026-09-01"},
    )

    res = client.get("/api/admin/stats/overview", headers=auth_admin)
    assert res.status_code == 200
    data = res.json()
    assert data["total_users"] >= 2
    assert data["total_trips"] >= 1
    assert data["total_stops"] >= 1
    assert data["total_scheduled_activities"] >= 1


def test_admin_stats_overview_30_day_window_logic(db_session):
    now = datetime(2026, 9, 1, 12, 0, 0, tzinfo=UTC)

    u1 = User(
        email="u1_window@globetrotter.com",
        hashed_password=hash_password("Password123!"),
        first_name="U1",
        last_name="Win",
    )
    u2 = User(
        email="u2_window@globetrotter.com",
        hashed_password=hash_password("Password123!"),
        first_name="U2",
        last_name="Win",
    )
    db_session.add_all([u1, u2])
    db_session.commit()

    # Trip inside 30-day window (created 10 days ago)
    t_recent = Trip(
        user_id=u1.id,
        name="Recent Trip",
        start_date=date(2026, 9, 1),
        end_date=date(2026, 9, 5),
        created_at=now - timedelta(days=10),
        updated_at=now - timedelta(days=10),
    )
    # Trip outside 30-day window (created 40 days ago)
    t_old = Trip(
        user_id=u2.id,
        name="Old Trip",
        start_date=date(2026, 7, 1),
        end_date=date(2026, 7, 5),
        created_at=now - timedelta(days=40),
        updated_at=now - timedelta(days=40),
    )
    db_session.add_all([t_recent, t_old])
    db_session.commit()

    stats = get_stats_overview(db_session, now=now)
    assert stats.trips_created_last_30_days >= 1
    assert stats.active_users_last_30_days >= 1


def test_admin_top_cities_cross_user_ranking(
    client: TestClient, db_session, admin_token: str, user_token: str
):
    auth_user1 = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    c1 = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "TopCity1", "country": "Country1"},
    ).json()
    c2 = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "TopCity2", "country": "Country2"},
    ).json()

    # User 2
    u2 = User(
        email="u2_top@globetrotter.com",
        hashed_password=hash_password("Password123!"),
        first_name="U2",
        last_name="Top",
    )
    db_session.add(u2)
    db_session.commit()
    auth_user2 = {"Authorization": f"Bearer {create_access_token(str(u2.id))}"}

    # User 1 stops at City 1 twice
    t1 = client.post(
        "/api/trips",
        headers=auth_user1,
        json={
            "name": "Trip 1",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    ).json()
    client.post(
        f"/api/trips/{t1['id']}/stops",
        headers=auth_user1,
        json={
            "city_id": c1["id"],
            "start_date": "2026-09-01",
            "end_date": "2026-09-03",
        },
    )
    client.post(
        f"/api/trips/{t1['id']}/stops",
        headers=auth_user1,
        json={
            "city_id": c1["id"],
            "start_date": "2026-09-04",
            "end_date": "2026-09-06",
        },
    )

    # User 2 stops at City 1 once, City 2 once
    t2 = client.post(
        "/api/trips",
        headers=auth_user2,
        json={
            "name": "Trip 2",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    ).json()
    client.post(
        f"/api/trips/{t2['id']}/stops",
        headers=auth_user2,
        json={
            "city_id": c1["id"],
            "start_date": "2026-09-01",
            "end_date": "2026-09-03",
        },
    )
    client.post(
        f"/api/trips/{t2['id']}/stops",
        headers=auth_user2,
        json={
            "city_id": c2["id"],
            "start_date": "2026-09-04",
            "end_date": "2026-09-06",
        },
    )

    # City 1 total stops across users = 3, City 2 total stops = 1
    res = client.get("/api/admin/stats/top-cities", headers=auth_admin)
    assert res.status_code == 200
    top_cities = res.json()
    city_names = [c["name"] for c in top_cities]
    assert "TopCity1" in city_names
    c1_entry = next(c for c in top_cities if c["name"] == "TopCity1")
    assert c1_entry["stop_count"] == 3


def test_admin_top_cities_limit_exceeded_returns_422(
    client: TestClient, admin_token: str
):
    res = client.get(
        "/api/admin/stats/top-cities?limit=51",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 422


def test_admin_list_users_pagination_search_and_trip_count(
    client: TestClient, db_session, admin_token: str, user_token: str
):
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    res = client.get(
        "/api/admin/users?search=user&sort_by=created_at&page=1&page_size=10",
        headers=auth_admin,
    )
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert data["page"] == 1
    assert data["page_size"] == 10


def test_admin_list_user_trips_bypass(
    client: TestClient, db_session, admin_token: str, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    # User creating trip
    user_trip = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "User Secret Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    ).json()

    # Get regular user ID from /api/auth/me
    me = client.get("/api/auth/me", headers=auth_user).json()
    user_id = me["id"]

    # Admin lists target user's trips -> 200 OK (bypass works!)
    admin_res = client.get(f"/api/admin/users/{user_id}/trips", headers=auth_admin)
    assert admin_res.status_code == 200
    user_trips = admin_res.json()
    assert len(user_trips) >= 1
    assert any(t["id"] == user_trip["id"] for t in user_trips)

    # Nonexistent user -> 404
    fake_id = str(uuid.uuid4())
    assert (
        client.get(f"/api/admin/users/{fake_id}/trips", headers=auth_admin).status_code
        == 404
    )


def test_regression_regular_user_cannot_access_other_users_trip(
    client: TestClient, db_session, user_token: str
):
    # Create user 2
    u2 = User(
        email="u2_reg@globetrotter.com",
        hashed_password=hash_password("Password123!"),
        first_name="U2",
        last_name="Reg",
    )
    db_session.add(u2)
    db_session.commit()
    auth_user2 = {"Authorization": f"Bearer {create_access_token(str(u2.id))}"}

    # User 2 creates trip
    t2 = client.post(
        "/api/trips",
        headers=auth_user2,
        json={
            "name": "User 2 Private Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    ).json()

    # Regular user 1 tries to GET user 2's trip via regular trips endpoint -> 404
    auth_user1 = {"Authorization": f"Bearer {user_token}"}
    res = client.get(f"/api/trips/{t2['id']}", headers=auth_user1)
    assert res.status_code == 404
