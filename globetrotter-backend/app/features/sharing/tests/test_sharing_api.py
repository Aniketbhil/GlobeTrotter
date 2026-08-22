import uuid

from fastapi.testclient import TestClient

from app.core.security import create_access_token, hash_password
from app.features.auth.models import User


def test_publish_trip_without_token_returns_401(client: TestClient):
    random_id = str(uuid.uuid4())
    res = client.post(f"/api/trips/{random_id}/share")
    assert res.status_code == 401


def test_publish_trip_unowned_trip_returns_404(
    client: TestClient, db_session, user_token: str
):
    user2 = User(
        email="user2_share@globetrotter.com",
        hashed_password=hash_password("Password123!"),
        first_name="User2",
        last_name="Share",
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

    res = client.post(
        f"/api/trips/{trip2['id']}/share",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res.status_code == 404


def test_publish_unpublish_republish_cycle_reuses_slug(
    client: TestClient, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    trip = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Share Cycle Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    ).json()

    # Publish
    pub_res = client.post(f"/api/trips/{trip['id']}/share", headers=auth_user)
    assert pub_res.status_code == 200
    pub_data = pub_res.json()
    slug = pub_data["slug"]
    assert pub_data["is_public"] is True
    assert f"/api/public/itinerary/{slug}" in pub_data["share_url"]

    # Public GET (no auth header) succeeds
    public_res = client.get(f"/api/public/itinerary/{slug}")
    assert public_res.status_code == 200

    # Unpublish
    unpub_res = client.delete(f"/api/trips/{trip['id']}/share", headers=auth_user)
    assert unpub_res.status_code == 200
    assert unpub_res.json()["is_public"] is False

    # Public GET now 404
    public_res_after_unpub = client.get(f"/api/public/itinerary/{slug}")
    assert public_res_after_unpub.status_code == 404

    # Republish -> same slug reused!
    repub_res = client.post(f"/api/trips/{trip['id']}/share", headers=auth_user)
    assert repub_res.status_code == 200
    assert repub_res.json()["slug"] == slug
    assert repub_res.json()["is_public"] is True


def test_get_public_itinerary_never_published_slug_returns_404(
    client: TestClient,
):
    res = client.get("/api/public/itinerary/nonexistent-slug-123")
    assert res.status_code == 404


def test_public_itinerary_payload_contains_no_sensitive_fields(
    client: TestClient, admin_token: str, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    c_id = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "PublicCity", "country": "PublicCountry"},
    ).json()["id"]
    act_id = client.post(
        "/api/activities",
        headers=auth_admin,
        json={
            "city_id": c_id,
            "name": "Public Activity",
            "type": "sightseeing",
            "cost": 50.0,
        },
    ).json()["id"]

    trip = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Private Budget Trip",
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
            "budget_estimate": 500.0,
        },
    ).json()

    client.post(
        f"/api/trips/{trip['id']}/stops/{stop['id']}/activities",
        headers=auth_user,
        json={
            "activity_id": act_id,
            "scheduled_date": "2026-09-01",
            "cost_override": 45.0,
        },
    )

    # Share trip
    pub_data = client.post(f"/api/trips/{trip['id']}/share", headers=auth_user).json()
    slug = pub_data["slug"]

    # Public GET without token
    res = client.get(f"/api/public/itinerary/{slug}")
    assert res.status_code == 200
    payload = res.json()

    # Check top-level: NO trip_id, user_id, costs
    assert "trip_id" not in payload
    assert "user_id" not in payload
    assert "owner" not in payload
    assert "cost" not in payload
    assert payload["trip_name"] == "Private Budget Trip"

    # Check stop: NO budget_estimate
    assert len(payload["stops"]) == 1
    stop_data = payload["stops"][0]
    assert "budget_estimate" not in stop_data

    # Check activity: NO cost, cost_override, effective_cost
    assert len(stop_data["activities"]) == 1
    act_data = stop_data["activities"][0]
    assert "cost" not in act_data
    assert "cost_override" not in act_data
    assert "effective_cost" not in act_data
    assert act_data["name"] == "Public Activity"


def test_copy_public_itinerary_without_token_returns_401(client: TestClient):
    res = client.post("/api/public/itinerary/some-slug/copy")
    assert res.status_code == 401


def test_copy_public_itinerary_unpublished_slug_returns_404(
    client: TestClient, user_token: str
):
    res = client.post(
        "/api/public/itinerary/nonexistent-slug/copy",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res.status_code == 404


def test_copy_public_itinerary_succeeds(
    client: TestClient, db_session, admin_token: str, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    c_id = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "CopyCity", "country": "CopyCountry"},
    ).json()["id"]
    act_id = client.post(
        "/api/activities",
        headers=auth_admin,
        json={
            "city_id": c_id,
            "name": "Copy Activity",
            "type": "culture",
            "cost": 20.0,
        },
    ).json()["id"]

    # Original owner creates trip, stop, activity
    source_trip = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Original Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    ).json()

    stop = client.post(
        f"/api/trips/{source_trip['id']}/stops",
        headers=auth_user,
        json={
            "city_id": c_id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
            "budget_estimate": 300.0,
        },
    ).json()

    client.post(
        f"/api/trips/{source_trip['id']}/stops/{stop['id']}/activities",
        headers=auth_user,
        json={
            "activity_id": act_id,
            "scheduled_date": "2026-09-01",
            "cost_override": 15.0,
        },
    )

    # Share source trip
    share_data = client.post(
        f"/api/trips/{source_trip['id']}/share", headers=auth_user
    ).json()
    slug = share_data["slug"]

    # Copier user
    copier = User(
        email="copier@globetrotter.com",
        hashed_password=hash_password("Password123!"),
        first_name="Copier",
        last_name="User",
    )
    db_session.add(copier)
    db_session.commit()
    copier_token = create_access_token(subject=str(copier.id))
    auth_copier = {"Authorization": f"Bearer {copier_token}"}

    # Copier copies trip with default name
    copy_res1 = client.post(
        f"/api/public/itinerary/{slug}/copy",
        headers=auth_copier,
        json={},
    )
    assert copy_res1.status_code == 201
    copied1 = copy_res1.json()
    assert copied1["name"] == "Copy of Original Trip"

    # Copier copies trip with custom name
    copy_res2 = client.post(
        f"/api/public/itinerary/{slug}/copy",
        headers=auth_copier,
        json={"name": "My Custom Copied Trip"},
    )
    assert copy_res2.status_code == 201
    copied2 = copy_res2.json()
    assert copied2["name"] == "My Custom Copied Trip"

    # Verify copied trip 2 stops & activities:
    copied2_stops = client.get(
        f"/api/trips/{copied2['id']}/stops", headers=auth_copier
    ).json()
    assert len(copied2_stops) == 1
    copied2_stop = copied2_stops[0]
    # budget_estimate is NOT copied (None)
    assert copied2_stop["budget_estimate"] is None

    copied2_acts = client.get(
        f"/api/trips/{copied2['id']}/stops/{copied2_stop['id']}/activities",
        headers=auth_copier,
    ).json()
    day1_acts = copied2_acts["2026-09-01"]
    assert len(day1_acts) == 1
    # cost_override is NOT copied (None), effective_cost defaults to base 20.0
    assert day1_acts[0]["cost_override"] is None
    assert float(day1_acts[0]["effective_cost"]) == 20.0

    # Source trip remains completely unchanged
    source_stops_check = client.get(
        f"/api/trips/{source_trip['id']}/stops", headers=auth_user
    ).json()
    assert len(source_stops_check) == 1
    assert float(source_stops_check[0]["budget_estimate"]) == 300.0
