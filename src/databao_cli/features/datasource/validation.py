"""Validation rules for datasource names.

These rules are shared between the CLI workflow and the Streamlit UI so
that users get the same feedback regardless of how they create a
datasource.
"""

import re

# Allowed segment characters: alphanumeric, hyphens, underscores, dots.
# Must start and end with an alphanumeric character.
_VALID_SEGMENT_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9._-]*[a-zA-Z0-9])?$")

MAX_DATASOURCE_NAME_LENGTH = 255


def validate_datasource_name(name: str) -> str | None:
    """Return an error message if *name* is invalid, or ``None`` if it is OK.

    Datasource names may contain forward-slash separators to organise
    datasources into folders (e.g. ``resources/my_db``).  Each segment
    between slashes is validated individually.

    Rules per segment:
    * Must not be empty or whitespace-only.
    * Must only contain letters, digits, hyphens, underscores, and dots.
    * Must start and end with a letter or digit.

    Overall rules:
    * Total length must not exceed 255 characters.
    * Must not contain spaces.
    """
    if not name or not name.strip():
        return "Datasource name must not be empty."

    if len(name) > MAX_DATASOURCE_NAME_LENGTH:
        return f"Datasource name must be at most {MAX_DATASOURCE_NAME_LENGTH} characters."

    if " " in name:
        return "Datasource name must not contain spaces."

    segments = name.split("/")
    for segment in segments:
        if not segment:
            return "Datasource name must not contain empty path segments (double slashes)."
        if not _VALID_SEGMENT_RE.match(segment):
            return (
                "Datasource name may only contain letters, digits, hyphens, "
                "underscores, and dots, and each segment must start and end "
                "with a letter or digit."
            )

    return None
