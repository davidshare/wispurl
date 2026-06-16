from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, VerifyMismatchError

from app.config import AuthSettings
from app.errors.exceptions import WeakPasswordError

COMMON_PASSWORDS = {
    "password",
    "password123",
    "qwerty12345",
    "letmein12345",
    "admin1234567",
    "welcome12345",
}

DUMMY_PASSWORD_HASH = (
    "$argon2id$v=19$m=19456,t=2,p=1$"  # noqa: S105
    "zYjaB/kheUcdZWrFVIp2gg$h56Laz2bhS8rrbJf0FsVbo1C8B190JAIQBO+5vHVa1E"
)


def build_password_hasher(settings: AuthSettings) -> PasswordHasher:
    return PasswordHasher(
        time_cost=settings.argon2_time_cost,
        memory_cost=settings.argon2_memory_cost,
        parallelism=settings.argon2_parallelism,
    )


def validate_password_policy(password: str, settings: AuthSettings) -> None:
    if len(password) < settings.password_min_length:
        raise WeakPasswordError
    if len(password) > settings.password_max_length:
        raise WeakPasswordError
    if password.strip() != password:
        raise WeakPasswordError
    if password.casefold() in COMMON_PASSWORDS:
        raise WeakPasswordError


def hash_password(password: str, settings: AuthSettings) -> str:
    validate_password_policy(password, settings)
    return build_password_hasher(settings).hash(password)


def verify_password(
    password: str,
    hashed_password: str,
    settings: AuthSettings,
) -> bool:
    try:
        return bool(build_password_hasher(settings).verify(hashed_password, password))
    except (VerifyMismatchError, VerificationError):
        return False


def password_needs_rehash(hashed_password: str, settings: AuthSettings) -> bool:
    return build_password_hasher(settings).check_needs_rehash(hashed_password)


def run_dummy_verify(password: str, settings: AuthSettings) -> None:
    verify_password(password, DUMMY_PASSWORD_HASH, settings)
