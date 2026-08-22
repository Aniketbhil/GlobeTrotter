import io
from datetime import date

from fastapi.testclient import TestClient

from app.core.security import create_access_token, hash_password
from app.features.auth.models import User
from app.features.trips.service import compute_status


def test_post_trip_without_token_returns_401(client: TestClient):
    res = client.post(
        "/api/trips",
        json={
            "name": "Paris Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-10",
        },
    )
    assert res.status_code == 401


def test_post_trip_end_date_before_start_date_returns_422(
    client: TestClient, user_token: str
):
    res = client.post(
        "/api/trips",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "name": "Invalid Dates Trip",
            "start_date": "2026-09-10",
            "end_date": "2026-09-01",
        },
    )
    assert res.status_code == 422


def test_post_trip_succeeds_and_includes_computed_status(
    client: TestClient, user_token: str
):
    res = client.post(
        "/api/trips",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "name": "Euro Summer",
            "description": "Backpacking Europe",
            "start_date": "2029-06-01",
            "end_date": "2029-06-20",
        },
    )
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Euro Summer"
    assert data["status"] == "upcoming"
    assert data["cover_photo_url"] is None


def test_get_trips_user_isolation(client: TestClient, db_session, user_token: str):
    res1 = client.post(
        "/api/trips",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "name": "User 1 Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    )
    assert res1.status_code == 201

    user2 = User(
        email="user2_trips@globetrotter.com",
        hashed_password=hash_password("Password123!"),
        first_name="User2",
        last_name="Trips",
    )
    db_session.add(user2)
    db_session.commit()
    token2 = create_access_token(subject=str(user2.id))

    res2 = client.post(
        "/api/trips",
        headers={"Authorization": f"Bearer {token2}"},
        json={
            "name": "User 2 Trip",
            "start_date": "2026-10-01",
            "end_date": "2026-10-05",
        },
    )
    assert res2.status_code == 201

    list1 = client.get("/api/trips", headers={"Authorization": f"Bearer {user_token}"})
    assert list1.status_code == 200
    names1 = [t["name"] for t in list1.json()["items"]]
    assert "User 1 Trip" in names1
    assert "User 2 Trip" not in names1

    list2 = client.get("/api/trips", headers={"Authorization": f"Bearer {token2}"})
    assert list2.status_code == 200
    names2 = [t["name"] for t in list2.json()["items"]]
    assert "User 2 Trip" in names2
    assert "User 1 Trip" not in names2


def test_get_trips_grouped_by_status(client: TestClient, user_token: str):
    headers = {"Authorization": f"Bearer {user_token}"}

    client.post(
        "/api/trips",
        headers=headers,
        json={
            "name": "Upcoming Trip",
            "start_date": "2030-01-01",
            "end_date": "2030-01-10",
        },
    )
    client.post(
        "/api/trips",
        headers=headers,
        json={
            "name": "Past Trip",
            "start_date": "2020-01-01",
            "end_date": "2020-01-10",
        },
    )

    res = client.get("/api/trips?group_by=status", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "ongoing" in data
    assert "upcoming" in data
    assert "completed" in data

    upcoming_names = [t["name"] for t in data["upcoming"]]
    completed_names = [t["name"] for t in data["completed"]]
    assert "Upcoming Trip" in upcoming_names
    assert "Past Trip" in completed_names


def test_other_user_trip_returns_404_on_get_patch_delete(
    client: TestClient, db_session, user_token: str
):
    user2 = User(
        email="owner_trip@globetrotter.com",
        hashed_password=hash_password("Password123!"),
        first_name="Owner",
        last_name="User",
    )
    db_session.add(user2)
    db_session.commit()
    token2 = create_access_token(subject=str(user2.id))

    res_create = client.post(
        "/api/trips",
        headers={"Authorization": f"Bearer {token2}"},
        json={
            "name": "Owner Trip",
            "start_date": "2026-09-01",
            "end_date": "2026-09-05",
        },
    )
    trip_id = res_create.json()["id"]

    get_res = client.get(
        f"/api/trips/{trip_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert get_res.status_code == 404

    patch_res = client.patch(
        f"/api/trips/{trip_id}",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"name": "Hacked Trip Name"},
    )
    assert patch_res.status_code == 404

    del_res = client.delete(
        f"/api/trips/{trip_id}",
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert del_res.status_code == 404

    fake_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF"
    file_tuple = ("cover.jpg", io.BytesIO(fake_jpeg), "image/jpeg")
    photo_res = client.post(
        f"/api/trips/{trip_id}/cover-photo",
        headers={"Authorization": f"Bearer {user_token}"},
        files={"file": file_tuple},
    )
    assert photo_res.status_code == 404


def test_upload_cover_photo_succeeds_and_serves(client: TestClient, user_token: str):
    headers = {"Authorization": f"Bearer {user_token}"}

    trip_res = client.post(
        "/api/trips",
        headers=headers,
        json={
            "name": "Cover Photo Trip",
            "start_date": "2027-01-01",
            "end_date": "2027-01-05",
        },
    )
    trip_id = trip_res.json()["id"]

    fake_jpeg = (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb"
    )
    file_tuple = ("cover.jpg", io.BytesIO(fake_jpeg), "image/jpeg")

    up_res = client.post(
        f"/api/trips/{trip_id}/cover-photo",
        headers=headers,
        files={"file": file_tuple},
    )
    assert up_res.status_code == 200
    data = up_res.json()
    assert data["cover_photo_url"] is not None
    assert "/uploads/trip_covers/" in data["cover_photo_url"]

    photo_path = data["cover_photo_url"].replace("http://localhost:8000", "")
    serve_res = client.get(photo_path)
    assert serve_res.status_code == 200
    assert serve_res.content == fake_jpeg


def test_compute_status_unit():
    class DummyTrip:
        def __init__(self, start, end):
            self.start_date = start
            self.end_date = end

    test_today = date(2026, 6, 15)

    ongoing_trip = DummyTrip(date(2026, 6, 10), date(2026, 6, 20))
    assert compute_status(ongoing_trip, today=test_today) == "ongoing"

    upcoming_trip = DummyTrip(date(2026, 7, 1), date(2026, 7, 10))
    assert compute_status(upcoming_trip, today=test_today) == "upcoming"

    completed_trip = DummyTrip(date(2026, 1, 1), date(2026, 1, 10))
    assert compute_status(completed_trip, today=test_today) == "completed"
