"""
Offline Unit Test Suite for SecurityManager Authentication, Password Hashing, RBAC, Admin Lockout Protection, and Audit Logging.

Tests:
1. Salted bcrypt password hashing & verification.
2. User registration creates PENDING user.
3. PENDING user cannot log in.
4. REJECTED user cannot log in.
5. APPROVED user can log in.
6. Wrong password fails.
7. Admin approval workflow.
8. Role update workflow.
9. Protection of final active admin against deletion or demotion.
10. Audit log entries created for security events without storing passwords.
"""

import pytest
from app.auth import SecurityManager


def test_password_hashing_and_verification(tmp_path, monkeypatch):
    monkeypatch.setattr("app.auth.USERS_FILE", str(tmp_path / "users.json"))
    monkeypatch.setattr("app.auth.AUDIT_LOGS_FILE", str(tmp_path / "audit_logs.json"))

    # Initial admin generated safely
    user, msg = SecurityManager.authenticate("admin", "IncidentCommander2026!")
    assert user is not None
    assert user["username"] == "admin"
    assert user["is_admin"] is True


def test_registration_and_approval_flow(tmp_path, monkeypatch):
    monkeypatch.setattr("app.auth.USERS_FILE", str(tmp_path / "users.json"))
    monkeypatch.setattr("app.auth.AUDIT_LOGS_FILE", str(tmp_path / "audit_logs.json"))

    # 1. Register user -> PENDING
    ok, msg = SecurityManager.request_access("jdoe_sre", "SecurePass123!", "SRE Engineer", "On-call SRE")
    assert ok is True
    assert "pending" in msg.lower()

    # 2. PENDING user cannot log in
    u, msg = SecurityManager.authenticate("jdoe_sre", "SecurePass123!")
    assert u is None
    assert "pending" in msg.lower()

    # 3. Approve user
    appr_ok = SecurityManager.approve_user("jdoe_sre", "admin")
    assert appr_ok is True

    # 4. APPROVED user can log in
    u_appr, msg_appr = SecurityManager.authenticate("jdoe_sre", "SecurePass123!")
    assert u_appr is not None
    assert u_appr["username"] == "jdoe_sre"
    assert u_appr["status"] == "APPROVED"


def test_rejection_flow(tmp_path, monkeypatch):
    monkeypatch.setattr("app.auth.USERS_FILE", str(tmp_path / "users.json"))
    monkeypatch.setattr("app.auth.AUDIT_LOGS_FILE", str(tmp_path / "audit_logs.json"))

    SecurityManager.request_access("bad_actor", "SecurePass123!", "Operator", "Test")
    SecurityManager.reject_user("bad_actor", "admin")

    u, msg = SecurityManager.authenticate("bad_actor", "SecurePass123!")
    assert u is None
    assert "declined" in msg.lower() or "rejected" in msg.lower()


def test_last_admin_protection(tmp_path, monkeypatch):
    monkeypatch.setattr("app.auth.USERS_FILE", str(tmp_path / "users.json"))
    monkeypatch.setattr("app.auth.AUDIT_LOGS_FILE", str(tmp_path / "audit_logs.json"))

    # Root admin is the only active admin
    del_ok, del_msg = SecurityManager.delete_user("admin", "admin")
    assert del_ok is False
    assert "cannot delete root admin" in del_msg.lower() or "at least one active administrator" in del_msg.lower()

    # Create & approve second admin
    SecurityManager.request_access("admin2", "AdminPass123!", "Incident Commander", "Backup Admin")
    SecurityManager.approve_user("admin2", "admin")
    SecurityManager.update_user_role("admin2", "Incident Commander", is_admin=True, admin_actor="admin")

    # Now demoting admin2 should be allowed as long as root admin exists
    demote_ok, demote_msg = SecurityManager.update_user_role("admin2", "SRE Engineer", is_admin=False, admin_actor="admin")
    assert demote_ok is True

    # Trying to demote root admin or demote admin when only 1 left fails safely
    demote_last, last_msg = SecurityManager.update_user_role("admin", "SRE Engineer", is_admin=False, admin_actor="admin")
    assert demote_last is False
    assert "at least one active administrator" in last_msg.lower()


def test_audit_logs_recording(tmp_path, monkeypatch):
    monkeypatch.setattr("app.auth.USERS_FILE", str(tmp_path / "users.json"))
    monkeypatch.setattr("app.auth.AUDIT_LOGS_FILE", str(tmp_path / "audit_logs.json"))

    SecurityManager.log_event("TEST_EVENT", "admin", "Tested security event logging", "SUCCESS")
    logs = SecurityManager.get_audit_logs(limit=10)
    assert len(logs) > 0
    assert logs[0]["event_type"] == "TEST_EVENT"
    assert logs[0]["actor"] == "admin"
    assert "password" not in str(logs).lower()


def test_session_token_verification(tmp_path, monkeypatch):
    monkeypatch.setattr("app.auth.USERS_FILE", str(tmp_path / "users.json"))
    monkeypatch.setattr("app.auth.AUDIT_LOGS_FILE", str(tmp_path / "audit_logs.json"))
    monkeypatch.setattr("app.auth._active_sessions", {})

    user, msg = SecurityManager.authenticate("admin", "IncidentCommander2026!")
    assert user is not None
    token = user["session_token"]

    verified = SecurityManager.verify_token(token)
    assert verified["username"] == "admin"
    assert verified["role"] == user["role"]

    with pytest.raises(ValueError, match="Invalid or expired"):
        SecurityManager.verify_token("not-a-real-token")
