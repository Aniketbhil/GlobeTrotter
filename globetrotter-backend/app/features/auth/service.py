import logging
import uuid

from fastapi import UploadFile
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.common.exceptions import (
    BadRequestError,
    ConflictError,
    NotFoundError,
    UnauthorizedError,
)
from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.core.storage import StorageBackend
from app.features.auth.models import User
from app.features.auth.schemas import SignupRequest

logger = logging.getLogger(__name__)


def ensure_env_admin_account(db: Session) -> None:
    if not settings.ADMIN_EMAIL or not settings.ADMIN_PASSWORD:
        return

    admin_email = settings.ADMIN_EMAIL.strip()
    admin_password = settings.ADMIN_PASSWORD.strip()

    user = db.query(User).filter(func.lower(User.email) == admin_email.lower()).first()
    if not user:
        user = User(
            email=admin_email,
            hashed_password=hash_password(admin_password),
            first_name="Admin",
            last_name="System",
            is_admin=True,
        )
        db.add(user)
    else:
        user.is_admin = True
        user.hashed_password = hash_password(admin_password)

    db.commit()


def signup_user(db: Session, data: SignupRequest) -> User:
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise ConflictError(f"User with email '{data.email}' already exists")

    if data.phone_number:
        existing_phone = (
            db.query(User).filter(User.phone_number == data.phone_number).first()
        )
        if existing_phone:
            raise ConflictError("Phone number already registered")

    hashed_pw = hash_password(data.password)
    user = User(
        email=data.email,
        hashed_password=hashed_pw,
        first_name=data.first_name,
        last_name=data.last_name,
        phone_number=data.phone_number,
        city=data.city,
        country=data.country,
        additional_info=data.additional_info,
        photo_url=data.photo_url,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, identifier: str, password: str) -> User:
    if "@" in identifier:
        user = db.query(User).filter(User.email == identifier).first()
    else:
        user = db.query(User).filter(User.phone_number == identifier).first()

    if not user or not verify_password(password, user.hashed_password):
        raise UnauthorizedError("Incorrect email or password")
    return user


def generate_reset_token(db: Session, email: str) -> str:
    user = db.query(User).filter(User.email == email).first()
    if not user:
        token = create_access_token(
            subject=str(uuid.uuid4()),
            expires_minutes=15,
            additional_claims={"purpose": "reset"},
        )
        logger.info("Password reset requested for non-existent email: %s", email)
        return token

    token = create_access_token(
        subject=str(user.id),
        expires_minutes=15,
        additional_claims={"purpose": "reset"},
    )
    # TODO: Send email with reset token in production
    print(f"[RESET TOKEN STUB] Password reset token for {email}: {token}")
    logger.info("[RESET TOKEN STUB] Password reset token generated for %s", email)
    return token


def reset_password(db: Session, token: str, new_password: str) -> None:
    try:
        payload = decode_access_token(token)
    except Exception as e:
        raise UnauthorizedError("Invalid or expired reset token") from e

    if payload.get("purpose") != "reset":
        raise BadRequestError("Invalid token purpose")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError("Invalid token subject")

    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError as e:
        raise BadRequestError("Invalid user ID in token") from e

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("User not found")

    user.hashed_password = hash_password(new_password)
    db.commit()


async def update_user_photo(
    db: Session, user: User, storage: StorageBackend, file: UploadFile
) -> User:
    relative_path = await storage.save(file, subfolder="photos")
    public_url = storage.url_for(relative_path)

    if user.photo_url:
        try:
            storage.delete(user.photo_url)
        except Exception as e:  # noqa: BLE001
            logger.warning("Could not delete old user photo: %s", e)

    user.photo_url = public_url
    db.commit()
    db.refresh(user)
    return user


def delete_user_photo(db: Session, user: User, storage: StorageBackend) -> User:
    if user.photo_url:
        try:
            storage.delete(user.photo_url)
        except Exception as e:  # noqa: BLE001
            logger.warning("Could not delete user photo: %s", e)
        user.photo_url = None
        db.commit()
        db.refresh(user)
    return user
