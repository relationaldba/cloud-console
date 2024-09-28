import bcrypt


def hash_password(plain_password: str):
    """Hash a password using bcrypt"""

    password_bytes = plain_password.encode(encoding="utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=password_bytes, salt=salt)
    return hashed_password.decode(encoding="utf-8")


def verify_password(plain_password: str, hashed_password: str):
    """Verify if the supplied plain text password matches the hashed password"""

    password_bytes = plain_password.encode("utf-8")
    hash_bytes = hashed_password.encode(encoding="utf-8")
    return bcrypt.checkpw(password=password_bytes, hashed_password=hash_bytes)
