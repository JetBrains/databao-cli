"""Validation rules for datasource fields.

These rules are shared between the CLI workflow and the Streamlit UI so
that users get the same feedback regardless of how they create a
datasource.
"""

import ipaddress
import re

# The agent requires source names to match this pattern so they can be
# used unquoted in SQL queries.  See databao-agent domain.py.
_SOURCE_NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

# Folder segments in the datasource path are more permissive — they only
# need to be valid filesystem names.
_FOLDER_SEGMENT_RE = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$")

MAX_DATASOURCE_NAME_LENGTH = 255

MIN_PORT = 1
MAX_PORT = 65535

# Hostname: RFC 952 / RFC 1123 — labels separated by dots.
_HOSTNAME_RE = re.compile(r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$")


def validate_datasource_name(name: str) -> str | None:
    """Return an error message if *name* is invalid, or ``None`` if it is OK.

    Datasource names may contain forward-slash separators to organise
    datasources into folders (e.g. ``resources/my_db``).  Folder segments
    are validated as filesystem-safe names.  The final segment (the actual
    source name) must match the agent's ``^[A-Za-z][A-Za-z0-9_]*$``
    pattern so it can be used unquoted in SQL queries.
    """
    if not name or not name.strip():
        return "Datasource name must not be empty."

    if len(name) > MAX_DATASOURCE_NAME_LENGTH:
        return f"Datasource name must be at most {MAX_DATASOURCE_NAME_LENGTH} characters."

    if re.search(r"\s", name):
        return "Datasource name must not contain whitespace."

    segments = name.split("/")
    for segment in segments:
        if not segment:
            return "Datasource name must not contain empty path segments (double slashes)."

    # Validate folder segments (all but the last).
    for segment in segments[:-1]:
        if not _FOLDER_SEGMENT_RE.match(segment):
            return (
                f"Folder segment '{segment}' may only contain letters, digits, "
                "hyphens, underscores, and dots, and must start and end with "
                "a letter or digit."
            )

    # Validate the source name (last segment) against the agent's pattern.
    source_name = segments[-1]
    if not _SOURCE_NAME_RE.match(source_name):
        return "Datasource name must start with a letter and contain only letters, digits, and underscores."

    return None


def validate_port(value: str) -> str | None:
    """Return an error message if *value* is not a valid port number."""
    try:
        port = int(value)
    except ValueError:
        return "Port must be a number."
    if port < MIN_PORT or port > MAX_PORT:
        return f"Port must be between {MIN_PORT} and {MAX_PORT}."
    return None


def validate_hostname(value: str) -> str | None:
    """Return an error message if *value* is not a valid hostname or IP."""
    value = value.strip()
    if not value:
        return "Hostname must not be empty."
    # Allow localhost and IP addresses as-is.
    if value == "localhost" or _is_ip_address(value):
        return None
    if len(value) > 253:
        return "Hostname must not exceed 253 characters."
    if not _HOSTNAME_RE.match(value):
        return "Hostname contains invalid characters."
    return None


def _is_ip_address(value: str) -> bool:
    """Return True if *value* is a valid IPv4 or IPv6 address."""
    # Strip brackets for bracketed IPv6 (e.g. [::1]).
    stripped = value.strip("[]")
    try:
        ipaddress.ip_address(stripped)
        return True
    except ValueError:
        return False
