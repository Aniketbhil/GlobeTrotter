import uuid

from fastapi.testclient import TestClient


def test_list_cities_without_token_returns_401(client: TestClient):
    res = client.get("/api/cities")
    assert res.status_code == 401


def test_list_cities_with_valid_token_and_filtering(
    client: TestClient, user_token: str, admin_token: str
):
    auth_user_header = {"Authorization": f"Bearer {user_token}"}
    auth_admin_header = {"Authorization": f"Bearer {admin_token}"}

    client.post(
        "/api/cities",
        headers=auth_admin_header,
        json={
            "name": "Paris",
            "country": "France",
            "region": "Europe",
            "cost_index": 85.5,
            "popularity_score": 98,
        },
    )
    client.post(
        "/api/cities",
        headers=auth_admin_header,
        json={
            "name": "Rome",
            "country": "Italy",
            "region": "Europe",
            "cost_index": 75.0,
            "popularity_score": 95,
        },
    )
    client.post(
        "/api/cities",
        headers=auth_admin_header,
        json={
            "name": "Tokyo",
            "country": "Japan",
            "region": "Asia",
            "cost_index": 80.0,
            "popularity_score": 99,
        },
    )

    # List all
    res = client.get("/api/cities", headers=auth_user_header)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 3

    # Filter search
    res_search = client.get("/api/cities?search=par", headers=auth_user_header)
    assert res_search.status_code == 200
    assert res_search.json()["total"] == 1
    assert res_search.json()["items"][0]["name"] == "Paris"

    # Filter country
    res_country = client.get("/api/cities?country=Italy", headers=auth_user_header)
    assert res_country.status_code == 200
    assert res_country.json()["total"] == 1
    assert res_country.json()["items"][0]["name"] == "Rome"

    # Filter region
    res_region = client.get("/api/cities?region=Asia", headers=auth_user_header)
    assert res_region.status_code == 200
    assert res_region.json()["total"] == 1
    assert res_region.json()["items"][0]["name"] == "Tokyo"

    # Sort by cost_index
    res_sort = client.get("/api/cities?sort_by=cost_index", headers=auth_user_header)
    assert res_sort.status_code == 200
    names = [c["name"] for c in res_sort.json()["items"]]
    assert names == ["Rome", "Tokyo", "Paris"]


def test_get_city_nonexistent_returns_404(client: TestClient, user_token: str):
    random_id = str(uuid.uuid4())
    res = client.get(
        f"/api/cities/{random_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert res.status_code == 404


def test_create_city_non_admin_returns_403(client: TestClient, user_token: str):
    res = client.post(
        "/api/cities",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "Berlin", "country": "Germany"},
    )
    assert res.status_code == 403


def test_create_city_admin_succeeds(client: TestClient, admin_token: str):
    res = client.post(
        "/api/cities",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "name": "Madrid",
            "country": "Spain",
            "region": "Europe",
            "cost_index": 68.0,
            "popularity_score": 90,
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Madrid"
    assert data["country"] == "Spain"


def test_delete_city_with_referencing_activities_returns_409(
    client: TestClient, admin_token: str
):
    auth_admin_header = {"Authorization": f"Bearer {admin_token}"}

    # Create city
    city_res = client.post(
        "/api/cities",
        headers=auth_admin_header,
        json={"name": "Athens", "country": "Greece"},
    )
    assert city_res.status_code == 201
    city_id = city_res.json()["id"]

    # Create activity for city
    act_res = client.post(
        "/api/activities",
        headers=auth_admin_header,
        json={
            "city_id": city_id,
            "name": "Acropolis Tour",
            "type": "sightseeing",
            "cost": 20.0,
        },
    )
    assert act_res.status_code == 201

    # Attempt to delete city
    del_res = client.delete(f"/api/cities/{city_id}", headers=auth_admin_header)
    assert del_res.status_code == 409
