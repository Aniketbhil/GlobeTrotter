import io
import uuid

from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.features.auth.schemas import UserUpdate
from app.features.stops.models import Stop
from app.features.trip_activities.models import TripActivity
from app.features.trips.models import Trip


def test_signup_all_fields_succeeds(client: TestClient):
    payload = {
        "email": "explorer@globetrotter.com",
        "password": "Password123!",
        "first_name": "Jane",
        "last_name": "Doe",
        "phone_number": "+1234567890",
        "city": "Paris",
        "country": "France",
        "additional_info": "Avid traveler & photographer",
        "photo_url": "https://example.com/avatar.jpg",
    }
    response = client.post("/api/auth/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "explorer@globetrotter.com"
    assert data["first_name"] == "Jane"
    assert data["last_name"] == "Doe"
    assert data["phone_number"] == "+1234567890"
    assert data["city"] == "Paris"
    assert data["country"] == "France"
    assert data["additional_info"] == "Avid traveler & photographer"
    assert data["photo_url"] == "https://example.com/avatar.jpg"
    assert data["language"] == "en"
    assert data["is_admin"] is False
    assert "hashed_password" not in data


def test_signup_duplicate_email_fails(client: TestClient):
    payload = {
        "email": "duplicate@globetrotter.com",
        "password": "Password123!",
        "first_name": "Alice",
        "last_name": "Smith",
    }
    res1 = client.post("/api/auth/signup", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/api/auth/signup", json=payload)
    assert res2.status_code == 409


def test_signup_omitting_optional_fields_succeeds(client: TestClient):
    payload = {
        "email": "minimal@globetrotter.com",
        "password": "Password123!",
        "first_name": "Bob",
        "last_name": "Jones",
    }
    response = client.post("/api/auth/signup", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "minimal@globetrotter.com"
    assert data["phone_number"] is None
    assert data["city"] is None
    assert data["country"] is None
    assert data["additional_info"] is None
    assert data["photo_url"] is None


def test_login_correct_credentials_returns_jwt(client: TestClient):
    signup_payload = {
        "email": "user@globetrotter.com",
        "password": "Password123!",
        "first_name": "Charlie",
        "last_name": "Brown",
    }
    client.post("/api/auth/signup", json=signup_payload)

    login_data = {
        "username": "user@globetrotter.com",
        "password": "Password123!",
    }
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


def test_login_wrong_password_returns_401(client: TestClient):
    signup_payload = {
        "email": "user2@globetrotter.com",
        "password": "Password123!",
        "first_name": "Charlie",
        "last_name": "Brown",
    }
    client.post("/api/auth/signup", json=signup_payload)

    login_data = {
        "username": "user2@globetrotter.com",
        "password": "WrongPassword!",
    }
    response = client.post("/api/auth/login", data=login_data)
    assert response.status_code == 401


def test_get_me_without_token_returns_401(client: TestClient):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_get_me_with_valid_token_returns_user_profile(client: TestClient):
    signup_payload = {
        "email": "me@globetrotter.com",
        "password": "Password123!",
        "first_name": "Diana",
        "last_name": "Prince",
        "city": "Themyscira",
        "country": "Greece",
    }
    signup_res = client.post("/api/auth/signup", json=signup_payload)
    assert signup_res.status_code == 201

    login_data = {
        "username": "me@globetrotter.com",
        "password": "Password123!",
    }
    login_res = client.post("/api/auth/login", data=login_data)
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    user_data = me_res.json()
    assert user_data["email"] == "me@globetrotter.com"
    assert user_data["first_name"] == "Diana"
    assert user_data["last_name"] == "Prince"
    assert user_data["city"] == "Themyscira"
    assert user_data["country"] == "Greece"


def test_forgot_and_reset_password_flow(client: TestClient):
    signup_payload = {
        "email": "reset@globetrotter.com",
        "password": "OldPassword123!",
        "first_name": "Eve",
        "last_name": "Adams",
    }
    signup_res = client.post("/api/auth/signup", json=signup_payload)
    user_id = signup_res.json()["id"]

    forgot_res = client.post(
        "/api/auth/forgot-password", json={"email": "reset@globetrotter.com"}
    )
    assert forgot_res.status_code == 200

    reset_token = create_access_token(
        subject=user_id,
        expires_minutes=15,
        additional_claims={"purpose": "reset"},
    )
    reset_res = client.post(
        "/api/auth/reset-password",
        json={"token": reset_token, "new_password": "NewPassword123!"},
    )
    assert reset_res.status_code == 200

    login_res = client.post(
        "/api/auth/login",
        data={
            "username": "reset@globetrotter.com",
            "password": "NewPassword123!",
        },
    )
    assert login_res.status_code == 200


# --- PART A TESTS ---


def test_signup_with_phone_and_login_with_phone(client: TestClient):
    signup_payload = {
        "email": "phoneuser@globetrotter.com",
        "password": "Password123!",
        "first_name": "Phone",
        "last_name": "User",
        "phone_number": "+19876543210",
    }
    res = client.post("/api/auth/signup", json=signup_payload)
    assert res.status_code == 201

    login_res = client.post(
        "/api/auth/login",
        data={"username": "+19876543210", "password": "Password123!"},
    )
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data


def test_signup_duplicate_phone_number_fails(client: TestClient):
    payload1 = {
        "email": "userA@globetrotter.com",
        "password": "Password123!",
        "first_name": "User",
        "last_name": "A",
        "phone_number": "+15550001111",
    }
    client.post("/api/auth/signup", json=payload1)

    payload2 = {
        "email": "userB@globetrotter.com",
        "password": "Password123!",
        "first_name": "User",
        "last_name": "B",
        "phone_number": "+15550001111",
    }
    res2 = client.post("/api/auth/signup", json=payload2)
    assert res2.status_code == 409


def test_login_unrecognized_phone_returns_401(client: TestClient):
    res = client.post(
        "/api/auth/login",
        data={"username": "+9999999999", "password": "Password123!"},
    )
    assert res.status_code == 401
    assert res.json()["detail"] == "Incorrect email or password"


# --- PART B TESTS ---


def test_upload_valid_photo_succeeds_and_serves(client: TestClient):
    signup_payload = {
        "email": "photouser@globetrotter.com",
        "password": "Password123!",
        "first_name": "Photo",
        "last_name": "User",
    }
    client.post("/api/auth/signup", json=signup_payload)

    login_res = client.post(
        "/api/auth/login",
        data={
            "username": "photouser@globetrotter.com",
            "password": "Password123!",
        },
    )
    token = login_res.json()["access_token"]

    fake_jpeg = (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xff\xdb"
    )
    file_tuple = ("profile.jpg", io.BytesIO(fake_jpeg), "image/jpeg")

    upload_res = client.post(
        "/api/auth/me/photo",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": file_tuple},
    )
    assert upload_res.status_code == 200
    user_data = upload_res.json()
    assert user_data["photo_url"] is not None
    assert "/uploads/photos/" in user_data["photo_url"]

    photo_path = user_data["photo_url"].replace("http://localhost:8000", "")
    serve_res = client.get(photo_path)
    assert serve_res.status_code == 200
    assert serve_res.content == fake_jpeg


def test_upload_disallowed_content_type_fails(client: TestClient):
    signup_payload = {
        "email": "pdfuser@globetrotter.com",
        "password": "Password123!",
        "first_name": "Pdf",
        "last_name": "User",
    }
    client.post("/api/auth/signup", json=signup_payload)
    login_res = client.post(
        "/api/auth/login",
        data={
            "username": "pdfuser@globetrotter.com",
            "password": "Password123!",
        },
    )
    token = login_res.json()["access_token"]

    fake_pdf = b"%PDF-1.4 ..."
    file_tuple = ("doc.pdf", io.BytesIO(fake_pdf), "application/pdf")

    res = client.post(
        "/api/auth/me/photo",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": file_tuple},
    )
    assert res.status_code == 400


def test_upload_file_exceeding_max_size_fails(client: TestClient):
    signup_payload = {
        "email": "largeuser@globetrotter.com",
        "password": "Password123!",
        "first_name": "Large",
        "last_name": "User",
    }
    client.post("/api/auth/signup", json=signup_payload)
    login_res = client.post(
        "/api/auth/login",
        data={
            "username": "largeuser@globetrotter.com",
            "password": "Password123!",
        },
    )
    token = login_res.json()["access_token"]

    large_bytes = b"x" * (6 * 1024 * 1024)
    file_tuple = ("large.jpg", io.BytesIO(large_bytes), "image/jpeg")

    res = client.post(
        "/api/auth/me/photo",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": file_tuple},
    )
    assert res.status_code == 413


def test_upload_photo_without_auth_fails(client: TestClient):
    fake_jpeg = b"fake image bytes"
    file_tuple = ("profile.jpg", io.BytesIO(fake_jpeg), "image/jpeg")

    res = client.post("/api/auth/me/photo", files={"file": file_tuple})
    assert res.status_code == 401


def test_delete_photo_when_exists_removes_file(client: TestClient):
    signup_payload = {
        "email": "deluser@globetrotter.com",
        "password": "Password123!",
        "first_name": "Delete",
        "last_name": "User",
    }
    client.post("/api/auth/signup", json=signup_payload)
    login_res = client.post(
        "/api/auth/login",
        data={
            "username": "deluser@globetrotter.com",
            "password": "Password123!",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    fake_png = b"\x89PNG\r\n\x1a\n"
    file_tuple = ("avatar.png", io.BytesIO(fake_png), "image/png")

    up_res = client.post(
        "/api/auth/me/photo", headers=headers, files={"file": file_tuple}
    )
    assert up_res.status_code == 200
    photo_url = up_res.json()["photo_url"]
    photo_path = photo_url.replace("http://localhost:8000", "")

    del_res = client.delete("/api/auth/me/photo", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["photo_url"] is None

    serve_res = client.get(photo_path)
    assert serve_res.status_code == 404


def test_delete_photo_when_none_exists(client: TestClient):
    signup_payload = {
        "email": "nophotouser@globetrotter.com",
        "password": "Password123!",
        "first_name": "NoPhoto",
        "last_name": "User",
    }
    client.post("/api/auth/signup", json=signup_payload)
    login_res = client.post(
        "/api/auth/login",
        data={
            "username": "nophotouser@globetrotter.com",
            "password": "Password123!",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    del_res = client.delete("/api/auth/me/photo", headers=headers)
    assert del_res.status_code == 200
    assert del_res.json()["photo_url"] is None


# --- PROFILE UPDATE & ACCOUNT DELETION TESTS ---


def test_patch_me_without_token_returns_401(client: TestClient):
    res = client.patch("/api/auth/me", json={"first_name": "NewName"})
    assert res.status_code == 401


def test_patch_me_partial_update_first_name(client: TestClient):
    signup_payload = {
        "email": "patchuser@globetrotter.com",
        "password": "Password123!",
        "first_name": "OldFirst",
        "last_name": "OldLast",
        "city": "OldCity",
    }
    client.post("/api/auth/signup", json=signup_payload)
    login_res = client.post(
        "/api/auth/login",
        data={
            "username": "patchuser@globetrotter.com",
            "password": "Password123!",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    patch_res = client.patch(
        "/api/auth/me", headers=headers, json={"first_name": "NewFirst"}
    )
    assert patch_res.status_code == 200
    data = patch_res.json()
    assert data["first_name"] == "NewFirst"
    assert data["last_name"] == "OldLast"
    assert data["city"] == "OldCity"


def test_patch_me_duplicate_phone_number_conflict(client: TestClient):
    client.post(
        "/api/auth/signup",
        json={
            "email": "phone1@globetrotter.com",
            "password": "Password123!",
            "first_name": "User",
            "last_name": "One",
            "phone_number": "+1111111111",
        },
    )
    client.post(
        "/api/auth/signup",
        json={
            "email": "phone2@globetrotter.com",
            "password": "Password123!",
            "first_name": "User",
            "last_name": "Two",
        },
    )
    login_res = client.post(
        "/api/auth/login",
        data={
            "username": "phone2@globetrotter.com",
            "password": "Password123!",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.patch(
        "/api/auth/me", headers=headers, json={"phone_number": "+1111111111"}
    )
    assert res.status_code == 409


def test_patch_me_own_phone_number_unchanged_succeeds(client: TestClient):
    client.post(
        "/api/auth/signup",
        json={
            "email": "ownphone@globetrotter.com",
            "password": "Password123!",
            "first_name": "Own",
            "last_name": "Phone",
            "phone_number": "+1222222222",
        },
    )
    login_res = client.post(
        "/api/auth/login",
        data={
            "username": "ownphone@globetrotter.com",
            "password": "Password123!",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.patch(
        "/api/auth/me",
        headers=headers,
        json={"phone_number": "+1222222222", "first_name": "UpdatedOwn"},
    )
    assert res.status_code == 200
    assert res.json()["first_name"] == "UpdatedOwn"
    assert res.json()["phone_number"] == "+1222222222"


def test_patch_me_disallowed_fields_ignored_by_schema(client: TestClient):
    assert "email" not in UserUpdate.model_fields
    assert "password" not in UserUpdate.model_fields
    assert "is_admin" not in UserUpdate.model_fields
    assert "photo_url" not in UserUpdate.model_fields

    client.post(
        "/api/auth/signup",
        json={
            "email": "disallowed@globetrotter.com",
            "password": "Password123!",
            "first_name": "Disallowed",
            "last_name": "User",
        },
    )
    login_res = client.post(
        "/api/auth/login",
        data={
            "username": "disallowed@globetrotter.com",
            "password": "Password123!",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.patch(
        "/api/auth/me",
        headers=headers,
        json={
            "email": "hacked@globetrotter.com",
            "is_admin": True,
            "photo_url": "https://hacked.com/pic.jpg",
            "first_name": "AllowedName",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == "disallowed@globetrotter.com"
    assert data["is_admin"] is False
    assert data["photo_url"] is None
    assert data["first_name"] == "AllowedName"


def test_delete_me_without_token_returns_401(client: TestClient):
    res = client.delete("/api/auth/me")
    assert res.status_code == 401


def test_delete_me_authenticated_user_succeeds(client: TestClient):
    client.post(
        "/api/auth/signup",
        json={
            "email": "deleteaccount@globetrotter.com",
            "password": "Password123!",
            "first_name": "Del",
            "last_name": "Account",
        },
    )
    login_res = client.post(
        "/api/auth/login",
        data={
            "username": "deleteaccount@globetrotter.com",
            "password": "Password123!",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    del_res = client.delete("/api/auth/me", headers=headers)
    assert del_res.status_code == 204

    # Subsequent GET /api/auth/me fails 401
    me_res = client.get("/api/auth/me", headers=headers)
    assert me_res.status_code == 401


def test_delete_me_cascades_trips_stops_and_activities(
    client: TestClient, db_session, admin_token: str
):
    auth_admin = {"Authorization": f"Bearer {admin_token}"}
    c_id = client.post(
        "/api/cities",
        headers=auth_admin,
        json={"name": "CascadeCity", "country": "CascadeCountry"},
    ).json()["id"]
    act_id = client.post(
        "/api/activities",
        headers=auth_admin,
        json={
            "city_id": c_id,
            "name": "CascadeAct",
            "type": "sightseeing",
            "cost": 10.0,
        },
    ).json()["id"]

    # User creates trip -> stop -> trip_activity
    client.post(
        "/api/auth/signup",
        json={
            "email": "cascadeuser@globetrotter.com",
            "password": "Password123!",
            "first_name": "Cascade",
            "last_name": "User",
        },
    )
    login_res = client.post(
        "/api/auth/login",
        data={
            "username": "cascadeuser@globetrotter.com",
            "password": "Password123!",
        },
    )
    token = login_res.json()["access_token"]
    auth_user = {"Authorization": f"Bearer {token}"}

    trip = client.post(
        "/api/trips",
        headers=auth_user,
        json={
            "name": "Cascade Trip",
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
        json={"activity_id": act_id, "scheduled_date": "2026-09-01"},
    )

    # Delete user account
    del_res = client.delete("/api/auth/me", headers=auth_user)
    assert del_res.status_code == 204

    # Verify directly in DB that trip, stop, trip_activity are gone
    trip_uuid = uuid.UUID(trip["id"])
    stop_uuid = uuid.UUID(stop["id"])
    assert db_session.query(Trip).filter(Trip.id == trip_uuid).first() is None
    assert db_session.query(Stop).filter(Stop.id == stop_uuid).first() is None
    assert (
        db_session.query(TripActivity).filter(TripActivity.stop_id == stop_uuid).first()
        is None
    )


def test_delete_me_removes_profile_photo_file(client: TestClient):
    client.post(
        "/api/auth/signup",
        json={
            "email": "delphotouser@globetrotter.com",
            "password": "Password123!",
            "first_name": "DelPhoto",
            "last_name": "User",
        },
    )
    login_res = client.post(
        "/api/auth/login",
        data={
            "username": "delphotouser@globetrotter.com",
            "password": "Password123!",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    fake_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF"
    file_tuple = ("profile.jpg", io.BytesIO(fake_jpeg), "image/jpeg")

    up_res = client.post(
        "/api/auth/me/photo", headers=headers, files={"file": file_tuple}
    )
    photo_url = up_res.json()["photo_url"]
    photo_path = photo_url.replace("http://localhost:8000", "")

    # Delete user account
    del_res = client.delete("/api/auth/me", headers=headers)
    assert del_res.status_code == 204

    # Photo file is removed from disk (GET returns 404)
    serve_res = client.get(photo_path)
    assert serve_res.status_code == 404
