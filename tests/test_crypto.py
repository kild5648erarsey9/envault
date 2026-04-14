"""Tests for the crypto module."""

import pytest
from envault.crypto import encrypt, decrypt


PASSWORD = "super-secret-master-password"


def test_encrypt_returns_string():
    token = encrypt("hello", PASSWORD)
    assert isinstance(token, str)
    assert len(token) > 0


def test_decrypt_roundtrip():
    plaintext = "my_api_key_value"
    token = encrypt(plaintext, PASSWORD)
    result = decrypt(token, PASSWORD)
    assert result == plaintext


def test_different_encryptions_produce_different_tokens():
    token1 = encrypt("same", PASSWORD)
    token2 = encrypt("same", PASSWORD)
    # Each call uses a fresh random salt, so tokens must differ
    assert token1 != token2


def test_decrypt_with_wrong_password_raises():
    token = encrypt("secret", PASSWORD)
    with pytest.raises(Exception):
        decrypt(token, "wrong-password")


def test_empty_string_roundtrip():
    token = encrypt("", PASSWORD)
    assert decrypt(token, PASSWORD) == ""


def test_unicode_roundtrip():
    plaintext = "pässwörد 🔑"
    token = encrypt(plaintext, PASSWORD)
    assert decrypt(token, PASSWORD) == plaintext
