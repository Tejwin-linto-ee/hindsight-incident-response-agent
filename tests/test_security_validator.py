"""
Tests for SecurityValidator: strict schema validation, file magic byte inspection, and error masking.
"""

import pytest
from app.security_validator import SecurityValidator


def test_username_validation_valid():
    ok, val = SecurityValidator.validate_username("sre_lead-01")
    assert ok is True
    assert val == "sre_lead-01"


def test_username_validation_invalid_characters():
    ok, msg = SecurityValidator.validate_username("admin<script>alert(1)</script>")
    assert ok is False
    assert "Invalid username format" in msg


def test_username_validation_too_short():
    ok, msg = SecurityValidator.validate_username("ab")
    assert ok is False


def test_password_strength():
    ok, _ = SecurityValidator.validate_password_strength("Short1")
    assert ok is False

    ok_strong, _ = SecurityValidator.validate_password_strength("StrongIncidentPassword2026!")
    assert ok_strong is True


def test_incident_input_strict_validation():
    ok, _ = SecurityValidator.validate_incident_input("Payment gateway returning HTTP 503 errors on checkout.")
    assert ok is True

    # Reject too short
    ok_short, msg = SecurityValidator.validate_incident_input("Hi")
    assert ok_short is False
    assert "too short" in msg


def test_file_upload_valid_log():
    log_content = b"2026-08-16 22:00:00 [ERROR] Connection pool exhausted in database cluster."
    ok, msg, text = SecurityValidator.validate_uploaded_crash_file("crash_report.log", log_content)
    assert ok is True
    assert "Connection pool" in text


def test_file_upload_rejected_extension():
    ok, msg, _ = SecurityValidator.validate_uploaded_crash_file("malicious.exe", b"fake binary payload")
    assert ok is False
    assert "Disallowed file extension" in msg


def test_file_upload_rejected_executable_magic_bytes():
    # Disguised .txt file with Windows PE executable header (MZ)
    fake_exe_as_txt = b"MZ\x90\x00\x03\x00\x00\x00"
    ok, msg, _ = SecurityValidator.validate_uploaded_crash_file("disguised.txt", fake_exe_as_txt)
    assert ok is False
    assert "forbidden binary executable" in msg.lower()


def test_error_masking():
    try:
        raise ValueError("C:\\Users\\secret\\internal\\database.db connection refused")
    except Exception as e:
        masked = SecurityValidator.mask_error_message(e)
        assert "C:\\Users" not in masked
        assert "database.db" not in masked
        assert "ValueError" in masked
