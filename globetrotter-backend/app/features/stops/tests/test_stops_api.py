import uuid

from fastapi.testclient import TestClient

from app.core.security import create_access_token, hash_password
from app.features.auth.models import User


def test_post_stop_without_token_returns_401(client: TestClient):
    random_trip_id = str(uuid.uuid4())
    res = client.post(
        f"/api/trips/{random_trip_id}/stops",
        json={
            "city_id": str(uuid.uuid4()),
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    )
    assert res.status_code == 401


def test_post_stop_on_another_user_trip_returns_404(
    client: TestClient, db_session, user_token: str, admin_token: str
):
    city_res = client.post(
        "/api/cities",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Lyon", "country": "France"},
    )
    city_id = city_res.json()["id"]

    user2 = User(
        email="user2_stops@globetrotter.com",
        hashed_password=hash_password("Password123!"),
        first_name="User2",
        last_name="Stops",
    )
    db_session.add(user2)
    db_session.commit()
    token2 = create_access_token(subject=str(user2.id))

    trip_res = client.post(
        "/api/trips",
        headers={"Authorization": f"Bearer {token2}"},
        json={
            "name": "User 2 Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    )
    trip_id = trip_res.json()["id"]

    res = client.post(
        f"/api/trips/{trip_id}/stops",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "city_id": city_id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    )
    assert res.status_code == 404


def test_post_stop_nonexistent_city_returns_404(client: TestClient, user_token: str):
    trip_res = client.post(
        "/api/trips",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "name": "My Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    )
    trip_id = trip_res.json()["id"]

    random_city_id = str(uuid.uuid4())
    res = client.post(
        f"/api/trips/{trip_id}/stops",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "city_id": random_city_id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    )
    assert res.status_code == 404


def test_post_stop_end_date_before_start_date_returns_422(
    client: TestClient, admin_token: str, user_token: str
):
    city_res = client.post(
        "/api/cities",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Nice", "country": "France"},
    )
    city_id = city_res.json()["id"]

    trip_res = client.post(
        "/api/trips",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "name": "My Trip 2",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    )
    trip_id = trip_res.json()["id"]

    res = client.post(
        f"/api/trips/{trip_id}/stops",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "city_id": city_id,
            "start_date": "2026-09-05",
            "end_date": "2026-09-01",
        },
    )
    assert res.status_code == 422


def test_post_stop_auto_increments_order_index_and_nested_city(
    client: TestClient, admin_token: str, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    c1_res = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "CityA", "country": "CountryA"},
    )
    c1_id = c1_res.json()["id"]

    c2_res = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "CityB", "country": "CountryB"},
    )
    c2_id = c2_res.json()["id"]

    trip_res = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Multi Stop Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-20",
        },
    )
    trip_id = trip_res.json()["id"]

    s1_res = client.post(
        f"/api/trips/{trip_id}/stops",
        headers=auth_user,
        json={
            "city_id": c1_id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    )
    assert s1_res.status_code == 201
    s1_data = s1_res.json()
    assert s1_data["order_index"] == 1
    assert s1_data["city"]["name"] == "CityA"

    s2_res = client.post(
        f"/api/trips/{trip_id}/stops",
        headers=auth_user,
        json={
            "city_id": c2_id,
            "start_date": "2026-09-06",
            "end_date": "2026-09-10",
        },
    )
    assert s2_res.status_code == 201
    s2_data = s2_res.json()
    assert s2_data["order_index"] == 2
    assert s2_data["city"]["name"] == "CityB"

    list_res = client.get(f"/api/trips/{trip_id}/stops", headers=auth_user)
    assert list_res.status_code == 200
    stops_list = list_res.json()
    assert len(stops_list) == 2
    assert stops_list[0]["order_index"] == 1
    assert stops_list[1]["order_index"] == 2


def test_reorder_stops_succeeds_and_invalid_ids_returns_422(
    client: TestClient, admin_token: str, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    c1_res = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "CityX", "country": "CountryX"},
    )
    c2_res = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "CityY", "country": "CountryY"},
    )
    c1_id, c2_id = c1_res.json()["id"], c2_res.json()["id"]

    trip_res = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Reorder Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-20",
        },
    )
    trip_id = trip_res.json()["id"]

    s1_id = client.post(
        f"/api/trips/{trip_id}/stops",
        headers=auth_user,
        json={
            "city_id": c1_id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    ).json()["id"]

    s2_id = client.post(
        f"/api/trips/{trip_id}/stops",
        headers=auth_user,
        json={
            "city_id": c2_id,
            "start_date": "2026-09-06",
            "end_date": "2026-09-10",
        },
    ).json()["id"]

    bad_reorder = client.patch(
        f"/api/trips/{trip_id}/stops/reorder",
        headers=auth_user,
        json={"ordered_stop_ids": [s1_id]},
    )
    assert bad_reorder.status_code == 422

    valid_reorder = client.patch(
        f"/api/trips/{trip_id}/stops/reorder",
        headers=auth_user,
        json={"ordered_stop_ids": [s2_id, s1_id]},
    )
    assert valid_reorder.status_code == 200
    new_stops = valid_reorder.json()
    assert new_stops[0]["id"] == s2_id
    assert new_stops[0]["order_index"] == 1
    assert new_stops[1]["id"] == s1_id
    assert new_stops[1]["order_index"] == 2


def test_delete_stop_keeps_existing_order_indices(
    client: TestClient, admin_token: str, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    c_res = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "CityZ", "country": "CountryZ"},
    )
    c_id = c_res.json()["id"]

    trip_res = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Delete Stop Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-20",
        },
    )
    trip_id = trip_res.json()["id"]

    s1_id = client.post(
        f"/api/trips/{trip_id}/stops",
        headers=auth_user,
        json={
            "city_id": c_id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    ).json()["id"]

    s2_id = client.post(
        f"/api/trips/{trip_id}/stops",
        headers=auth_user,
        json={
            "city_id": c_id,
            "start_date": "2026-09-06",
            "end_date": "2026-09-10",
        },
    ).json()["id"]

    s3_id = client.post(
        f"/api/trips/{trip_id}/stops",
        headers=auth_user,
        json={
            "city_id": c_id,
            "start_date": "2026-09-11",
            "end_date": "2026-09-15",
        },
    ).json()["id"]

    del_res = client.delete(f"/api/trips/{trip_id}/stops/{s2_id}", headers=auth_user)
    assert del_res.status_code == 204

    list_res = client.get(f"/api/trips/{trip_id}/stops", headers=auth_user)
    assert list_res.status_code == 200
    stops = list_res.json()
    assert len(stops) == 2
    assert stops[0]["id"] == s1_id
    assert stops[0]["order_index"] == 1
    assert stops[1]["id"] == s3_id
    assert stops[1]["order_index"] == 3


def test_delete_city_with_active_stop_returns_409(
    client: TestClient, admin_token: str, user_token: str
):
    auth_user = {"Authorization": f"Bearer {user_token}"}
    auth_admin = {"Authorization": f"Bearer {admin_token}"}

    c_res = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "CityProtected", "country": "CountryP"},
    )
    city_id = c_res.json()["id"]

    trip_res = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Protected City Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-20",
        },
    )
    trip_id = trip_res.json()["id"]

    client.post(
        f"/api/trips/{trip_id}/stops",
        headers=auth_user,
        json={
            "city_id": city_id,
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    )

    del_city_res = client.delete(f"/api/cities/{city_id}", headers=auth_admin)
    assert del_city_res.status_code == 409
