from __future__ import annotations

import hashlib
import importlib
import secrets
from functools import lru_cache


@lru_cache(maxsize=1)
def _password_hasher():
    try:
        module = importlib.import_module("argon2")
    except Exception:
        return None

    return module.PasswordHasher()


def _pbkdf2_hash(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120000)
    return f"pbkdf2_sha256${salt}${derived.hex()}"


def hash_password(password: str) -> str:
    hasher = _password_hasher()
    if hasher is None:
        return _pbkdf2_hash(password)
    return hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    if password_hash.startswith("pbkdf2_sha256$"):
        try:
            _, salt, digest = password_hash.split("$", 2)
        except ValueError:
            return False
        return _pbkdf2_hash(password, salt) == f"pbkdf2_sha256${salt}${digest}"

    hasher = _password_hasher()
    if hasher is None:
        return False
    try:
        return hasher.verify(password_hash, password)
    except Exception:
        return False


def make_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
