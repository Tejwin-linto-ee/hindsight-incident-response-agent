"""
Enterprise Security Validator & File Inspector.
Provides strict schema validation (type, length, regex format),
magic bytes content-based file inspection, and structured exception masking.
"""

import os
import re
from typing import Any, Dict, Optional, Tuple


class SecurityValidator:
    """
    Zero-Trust Strict Input Validator & File Content Inspector.
    Rejects invalid inputs instead of only escaping.
    """

    # Strict regex schemas
    USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_\-\.]{3,32}$")
    ROLE_REGEX = re.compile(r"^[a-zA-Z0-9\s\-_/]{3,50}$")
    INCIDENT_TEXT_REGEX = re.compile(r"^[\w\s\.,;:!\?\-\(\)\[\]\{\}\'\"/\\+=@#\$%\^&\*~`\n\r\t]{5,10000}$", re.UNICODE)

    MAX_FILE_SIZE_BYTES = 2 * 1024 * 1024  # 2MB

    # Executable byte signatures to reject
    DISALLOWED_MAGIC_BYTES = [
        b"MZ",           # Windows PE executable / DLL
        b"\x7fELF",      # Linux ELF binary
        b"\xca\xfe\xba\xbe", # Mach-O or Java Class
        b"<?php",        # PHP script
        b"#!",           # Unix shebang executable
        b"<script",      # HTML/JS payload
    ]

    ALLOWED_MIME_EXTENSIONS = {".log", ".txt", ".json", ".csv"}

    @classmethod
    def validate_username(cls, username: str) -> Tuple[bool, str]:
        if not isinstance(username, str):
            return False, "Username must be a string."
        clean = username.strip()
        if not cls.USERNAME_REGEX.match(clean):
            return False, "Invalid username format: Must be 3-32 alphanumeric characters (dashes, underscores, dots allowed)."
        return True, clean

    @classmethod
    def validate_password_strength(cls, password: str) -> Tuple[bool, str]:
        if not isinstance(password, str):
            return False, "Password must be a string."
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        if len(password) > 128:
            return False, "Password exceeds maximum length of 128 characters."
        return True, password

    @classmethod
    def validate_incident_input(cls, text: str, field_name: str = "Incident description") -> Tuple[bool, str]:
        if not isinstance(text, str):
            return False, f"{field_name} must be text."
        clean = text.strip()
        if len(clean) < 5:
            return False, f"{field_name} is too short (minimum 5 characters required)."
        if len(clean) > 10000:
            return False, f"{field_name} exceeds maximum allowed size of 10,000 characters."
        if not cls.INCIDENT_TEXT_REGEX.match(clean):
            return False, f"{field_name} contains unprintable or disallowed binary control characters."
        return True, clean

    @classmethod
    def validate_uploaded_crash_file(cls, filename: str, file_bytes: bytes) -> Tuple[bool, str, str]:
        """
        Validates uploaded crash log files by:
        1. Checking extension against whitelist
        2. Enforcing max 2MB size limit
        3. Scanning binary magic bytes for executable or script signatures (rejecting if detected)
        4. Decoding UTF-8 text safely
        """
        if not filename or not file_bytes:
            return False, "Uploaded file is empty or missing name.", ""

        ext = os.path.splitext(filename)[1].lower()
        if ext not in cls.ALLOWED_MIME_EXTENSIONS:
            return False, f"Disallowed file extension '{ext}'. Only .log, .txt, .json, and .csv are permitted.", ""

        if len(file_bytes) > cls.MAX_FILE_SIZE_BYTES:
            return False, f"File size ({len(file_bytes)} bytes) exceeds maximum 2MB limit.", ""

        # Content inspection: Reject executable and script signatures
        file_header = file_bytes[:32]
        for bad_magic in cls.DISALLOWED_MAGIC_BYTES:
            if bad_magic.lower() in file_header.lower():
                return False, "Security violation: Uploaded file contains forbidden binary executable or script signatures.", ""

        try:
            decoded_text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            try:
                decoded_text = file_bytes.decode("latin-1")
            except Exception:
                return False, "File encoding invalid: Unable to parse as text.", ""

        return True, "File passed strict security validation.", decoded_text

    @classmethod
    def mask_error_message(cls, exc: Exception, generic_msg: str = "An internal processing error occurred.") -> str:
        """
        Returns a sanitized user-facing error message without leaking stack traces or paths.
        """
        # Return clean user message without filesystem paths or DB internals
        return f"{generic_msg} (Error Reference: {type(exc).__name__})"
