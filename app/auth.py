import os
import json
import secrets
from datetime import datetime
from typing import Dict, Any, Optional, List
import bcrypt

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
USERS_FILE = os.path.join(DATA_DIR, "users.json")
AUDIT_LOGS_FILE = os.path.join(DATA_DIR, "audit_logs.json")

# In-memory session store: token -> authenticated user context
_active_sessions: Dict[str, Dict[str, Any]] = {}


class SecurityManager:
    """
    Enterprise Security, RBAC, Approval Workflow & Access Audit Manager.
    - Salted bcrypt password hashing
    - Account approval workflow (PENDING / APPROVED / REJECTED)
    - Admin privilege checks & user lifecycle management (Approve, Reject, Delete, Role Change)
    - Full security audit logging (Logins, Failed attempts, Registrations, Approvals, Invocations)
    """

    @classmethod
    def _now_iso(cls) -> str:
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    @classmethod
    def _load_users(cls) -> Dict[str, Any]:
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(USERS_FILE):
            default_salt = bcrypt.gensalt()
            admin_password = os.getenv("ADMIN_PASSWORD", "IncidentCommander2026!")
            default_hash = bcrypt.hashpw(admin_password.encode('utf-8'), default_salt).decode('utf-8')
            users = {
                "admin": {
                    "username": "admin",
                    "role": "Admin / Incident Commander",
                    "status": "APPROVED",  # Default admin is auto-approved
                    "is_admin": True,
                    "password_hash": default_hash,
                    "created_at": cls._now_iso(),
                    "last_login": None,
                    "approved_by": "SYSTEM"
                }
            }
            with open(USERS_FILE, "w", encoding="utf-8") as f:
                json.dump(users, f, indent=2)
            return users

        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    @classmethod
    def _save_users(cls, users: Dict[str, Any]) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=2)

    # ─────────────────────────────────────────────────────────────
    #  AUDIT LOGGING
    # ─────────────────────────────────────────────────────────────

    @classmethod
    def log_event(cls, event_type: str, actor: str, details: str, status: str = "SUCCESS") -> None:
        """Record a timestamped security or operational audit event."""
        os.makedirs(DATA_DIR, exist_ok=True)
        logs = []
        if os.path.exists(AUDIT_LOGS_FILE):
            try:
                with open(AUDIT_LOGS_FILE, "r", encoding="utf-8") as f:
                    logs = json.load(f)
            except Exception:
                logs = []

        entry = {
            "timestamp": cls._now_iso(),
            "event_type": event_type,  # e.g., AUTH_LOGIN, USER_REGISTER, USER_APPROVED, INCIDENT_INVESTIGATED
            "actor": actor,
            "status": status,          # SUCCESS, FAILED, BLOCKED, PENDING
            "details": details
        }
        # Keep last 500 entries (prepend newest)
        logs.insert(0, entry)
        logs = logs[:500]

        with open(AUDIT_LOGS_FILE, "w", encoding="utf-8") as f:
            json.dump(logs, f, indent=2)

    @classmethod
    def get_audit_logs(cls, limit: int = 50) -> List[Dict[str, Any]]:
        if not os.path.exists(AUDIT_LOGS_FILE):
            return []
        try:
            with open(AUDIT_LOGS_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
                return logs[:limit]
        except Exception:
            return []

    # ─────────────────────────────────────────────────────────────
    #  AUTHENTICATION & REGISTRATION
    # ─────────────────────────────────────────────────────────────

    @classmethod
    def authenticate(cls, username: str, password: str) -> tuple[Optional[Dict[str, Any]], str]:
        """
        Returns (user_dict, message)
        User dict is None if authentication fails or account is pending approval.
        """
        users = cls._load_users()
        u_key = username.strip().lower()
        user = users.get(u_key)

        if not user:
            cls.log_event("AUTH_LOGIN", username, "Attempted login for nonexistent username", "FAILED")
            return None, "Invalid username or password."

        # Check password hash
        try:
            if not bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
                cls.log_event("AUTH_LOGIN", username, "Invalid password attempt", "FAILED")
                return None, "Invalid username or password."
        except Exception:
            return None, "Authentication error during password verification."

        # Check Approval Status
        status = user.get("status", "APPROVED")
        if status == "PENDING":
            cls.log_event("AUTH_LOGIN", username, "Pending user attempted sign-in", "BLOCKED")
            return None, "Account is pending Admin approval. Please contact an administrator."
        elif status == "REJECTED":
            cls.log_event("AUTH_LOGIN", username, "Rejected user attempted sign-in", "BLOCKED")
            return None, "Your access request was declined by the administrator."

        # Update last login & log
        user["last_login"] = cls._now_iso()
        users[u_key] = user
        cls._save_users(users)

        cls.log_event("AUTH_LOGIN", username, f"Successful login ({user.get('role', 'Operator')})", "SUCCESS")

        session_token = secrets.token_hex(32)
        user_dict = {
            "username": user["username"],
            "role": user.get("role", "SRE Engineer"),
            "is_admin": user.get("is_admin", False) or u_key == "admin",
            "session_token": session_token,
            "tenant_id": user.get("tenant_id", "default"),
            "status": status,
        }
        cls._register_session(session_token, user_dict)
        return user_dict, "SUCCESS"

    @classmethod
    def _register_session(cls, token: str, user: Dict[str, Any]) -> None:
        """Store an authenticated session token for subsequent API requests."""
        _active_sessions[token] = {
            "username": user["username"],
            "role": user.get("role", "SRE Engineer"),
            "tenant_id": user.get("tenant_id", "default"),
            "is_admin": user.get("is_admin", False),
        }

    @classmethod
    def verify_token(cls, token: str) -> Dict[str, Any]:
        """Validate a bearer token and return the associated user context."""
        if not token:
            raise ValueError("Missing authentication token")
        session = _active_sessions.get(token)
        if not session:
            raise ValueError("Invalid or expired authentication token")
        return session

    @classmethod
    def request_access(cls, username: str, password: str, role: str = "SRE Engineer", reason: str = "") -> tuple[bool, str]:
        """User registers for access, placing them in PENDING status for Admin confirmation."""
        users = cls._load_users()
        u_key = username.strip().lower()

        if u_key in users:
            return False, "Username is already taken."

        salt = bcrypt.gensalt()
        pw_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

        users[u_key] = {
            "username": u_key,
            "role": role,
            "status": "PENDING",  # Requires Admin Approval!
            "is_admin": False,
            "password_hash": pw_hash,
            "reason": reason,
            "created_at": cls._now_iso(),
            "last_login": None,
            "approved_by": None
        }
        cls._save_users(users)
        cls.log_event("USER_REGISTER", u_key, f"New registration request for role '{role}'. Reason: {reason}", "PENDING")
        return True, "Registration submitted! Your account is pending administrator confirmation."

    # ─────────────────────────────────────────────────────────────
    #  ADMIN USER MANAGEMENT
    # ─────────────────────────────────────────────────────────────

    @classmethod
    def list_users(cls) -> List[Dict[str, Any]]:
        users = cls._load_users()
        user_list = []
        for u in users.values():
            safe_u = {k: v for k, v in u.items() if k != "password_hash"}
            user_list.append(safe_u)
        return sorted(user_list, key=lambda x: x.get("created_at", ""), reverse=True)

    @classmethod
    def approve_user(cls, username: str, admin_actor: str) -> bool:
        users = cls._load_users()
        u_key = username.strip().lower()
        if u_key not in users:
            return False
        users[u_key]["status"] = "APPROVED"
        users[u_key]["approved_by"] = admin_actor
        cls._save_users(users)
        cls.log_event("USER_APPROVED", admin_actor, f"Approved user '{u_key}' for platform access", "SUCCESS")
        return True

    @classmethod
    def reject_user(cls, username: str, admin_actor: str) -> bool:
        users = cls._load_users()
        u_key = username.strip().lower()
        if u_key not in users or u_key == "admin":
            return False
        users[u_key]["status"] = "REJECTED"
        users[u_key]["approved_by"] = f"REJECTED_BY_{admin_actor}"
        cls._save_users(users)
        cls.log_event("USER_REJECTED", admin_actor, f"Rejected access for user '{u_key}'", "SUCCESS")
        return True

    @classmethod
    def _count_active_admins(cls, users: Dict[str, Any]) -> int:
        count = 0
        for u in users.values():
            if u.get("status") == "APPROVED" and u.get("is_admin", False):
                count += 1
        return count

    @classmethod
    def delete_user(cls, username: str, admin_actor: str) -> tuple[bool, str]:
        users = cls._load_users()
        u_key = username.strip().lower()
        if u_key not in users:
            return False, "User does not exist."
        if u_key == "admin":
            return False, "Cannot delete root admin account."

        if users[u_key].get("is_admin", False) and users[u_key].get("status") == "APPROVED":
            if cls._count_active_admins(users) <= 1:
                return False, "At least one active administrator must remain."

        del users[u_key]
        cls._save_users(users)
        cls.log_event("USER_DELETED", admin_actor, f"Deleted user account '{u_key}'", "SUCCESS")
        return True, "User account deleted."

    @classmethod
    def update_user_role(cls, username: str, new_role: str, is_admin: bool, admin_actor: str) -> tuple[bool, str]:
        users = cls._load_users()
        u_key = username.strip().lower()
        if u_key not in users:
            return False, "User does not exist."

        current_is_admin = users[u_key].get("is_admin", False)
        current_status = users[u_key].get("status")

        # Protecting last admin demotion
        if current_is_admin and not is_admin and current_status == "APPROVED":
            if cls._count_active_admins(users) <= 1:
                return False, "At least one active administrator must remain."

        users[u_key]["role"] = new_role
        if u_key != "admin":  # Root admin remains admin always
            users[u_key]["is_admin"] = is_admin
        else:
            users[u_key]["is_admin"] = True

        cls._save_users(users)
        cls.log_event("USER_ROLE_UPDATED", admin_actor, f"Updated '{u_key}' role to '{new_role}' (admin={users[u_key]['is_admin']})", "SUCCESS")
        return True, "User role updated successfully."
