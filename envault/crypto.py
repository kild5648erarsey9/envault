"""Cryptographic utilities for encrypting and decrypting secrets."""

import base64
import os
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet


SALT_SIZE = 16
ITERATIONS = 390_000


def derive_key(password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
    )
    raw_key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(raw_key)


def encrypt(plaintext: str, password: str) -> str:
    """Encrypt plaintext using a password. Returns a base64-encoded token."""
    salt = os.urandom(SALT_SIZE)
    key = derive_key(password, salt)
    f = Fernet(key)
    token = f.encrypt(plaintext.encode())
    # Prepend salt to the token so it can be used during decryption
    combined = base64.urlsafe_b64encode(salt + base64.urlsafe_b64decode(token))
    return combined.decode()


def decrypt(encoded: str, password: str) -> str:
    """Decrypt an encoded secret using a password."""
    raw = base64.urlsafe_b64decode(encoded.encode())
    salt = raw[:SALT_SIZE]
    token = base64.urlsafe_b64encode(raw[SALT_SIZE:])
    key = derive_key(password, salt)
    f = Fernet(key)
    return f.decrypt(token).decode()
