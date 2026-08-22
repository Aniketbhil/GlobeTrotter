from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.features.activities.models import Activity
from app.features.cities.models import City
from app.scripts.seed_reference_data import seed


def test_list_activities_without_token_returns_401(client: TestClient):
    res = client.get("/api/activities")
    assert res.status_code == 401


def test_create_activity_non_admin_returns_403(
    client: TestClient, user_token: str, admin_token: str
):
    city_res = client.post(
        "/api/cities",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Vienna", "country": "Austria"},
    )
    city_id = city_res.json()["id"]

    res = client.post(
        "/api/activities",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "city_id": city_id,
            "name": "Concert",
            "type": "culture",
            "cost": 50.0,
        },
    )
    assert res.status_code == 403


def test_create_activity_admin_succeeds(client: TestClient, admin_token: str):
    auth_admin_header = {"Authorization": f"Bearer {admin_token}"}

    city_res = client.post(
        "/api/cities",
        headers=auth_admin_header,
        json={"name": "Prague", "country": "Czech Republic"},
    )
    city_id = city_res.json()["id"]

    act_res = client.post(
        "/api/activities",
        headers=auth_admin_header,
        json={
            "city_id": city_id,
            "name": "Castle Tour",
            "type": "sightseeing",
            "cost": 15.0,
            "duration_mins": 120,
            "description": "Historic castle guided tour",
        },
    )
    assert act_res.status_code == 201
    data = act_res.json()
    assert data["name"] == "Castle Tour"
    assert data["type"] == "sightseeing"
    assert data["city_id"] == city_id


def test_list_activities_with_filtering(
    client: TestClient, user_token: str, admin_token: str
):
    auth_user_header = {"Authorization": f"Bearer {user_token}"}
    auth_admin_header = {"Authorization": f"Bearer {admin_token}"}

    city1_res = client.post(
        "/api/cities",
        headers=auth_admin_header,
        json={"name": "Lisbon", "country": "Portugal"},
    )
    city1_id = city1_res.json()["id"]

    city2_res = client.post(
        "/api/cities",
        headers=auth_admin_header,
        json={"name": "Porto", "country": "Portugal"},
    )
    city2_id = city2_res.json()["id"]

    client.post(
        "/api/activities",
        headers=auth_admin_header,
        json={
            "city_id": city1_id,
            "name": "Tram 28 Ride",
            "type": "sightseeing",
            "cost": 5.0,
            "duration_mins": 45,
        },
    )
    client.post(
        "/api/activities",
        headers=auth_admin_header,
        json={
            "city_id": city1_id,
            "name": "Pastel de Nata Class",
            "type": "food",
            "cost": 40.0,
            "duration_mins": 90,
        },
    )
    client.post(
        "/api/activities",
        headers=auth_admin_header,
        json={
            "city_id": city2_id,
            "name": "Port Wine Cellar Tasting",
            "type": "food",
            "cost": 25.0,
            "duration_mins": 60,
        },
    )

    res_city = client.get(
        f"/api/activities?city_id={city1_id}", headers=auth_user_header
    )
    assert res_city.status_code == 200
    assert res_city.json()["total"] == 2

    res_type = client.get("/api/activities?type=food", headers=auth_user_header)
    assert res_type.status_code == 200
    assert res_type.json()["total"] == 2

    res_cost = client.get("/api/activities?max_cost=10.0", headers=auth_user_header)
    assert res_cost.status_code == 200
    assert res_cost.json()["total"] == 1
    assert res_cost.json()["items"][0]["name"] == "Tram 28 Ride"

    res_dur = client.get(
        "/api/activities?max_duration_mins=60", headers=auth_user_header
    )
    assert res_dur.status_code == 200
    assert res_dur.json()["total"] == 2


def test_seed_script_idempotency_in_database(db_session: Session):
    seed(db_session)
    cities_count_1 = db_session.query(City).count()
    activities_count_1 = db_session.query(Activity).count()
    assert cities_count_1 == 25
    assert activities_count_1 == 100

    seed(db_session)
    cities_count_2 = db_session.query(City).count()
    activities_count_2 = db_session.query(Activity).count()
    assert cities_count_2 == 25
    assert activities_count_2 == 100
