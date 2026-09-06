import re

from backend.models import UserContext


# ============================================================
# ACTIVITY PATTERNS
# ============================================================

ACTIVITY_PATTERNS = {
    "cycling": [
        "cycling",
        "cycle",
        "bike ride",
        "bicycle",
        "biking",
        "ride my bike",
    ],

    "running": [
        "running",
        "run",
        "jogging",
        "jog",
    ],

    "walking": [
        "walking",
        "walk",
        "go for a walk",
    ],

    "outdoor_exercise": [
        "exercise",
        "workout",
        "work out",
        "outdoor workout",
    ],

    "travel": [
        "travel",
        "commute",
        "journey",
        "trip",
        "driving",
        "drive",
        "ride",
    ],

    "picnic": [
        "picnic",
        "outing",
        "outdoor lunch",
        "family outing",
    ],

    "outdoor_event": [
        "outdoor event",
        "concert",
        "festival",
        "function",
        "gathering",
    ],

    "dog_walk": [
        "walk my dog",
        "walk the dog",
        "take my dog out",
    ],
}


# ============================================================
# VULNERABLE GROUP PATTERNS
# ============================================================

VULNERABLE_GROUP_PATTERNS = {
    "child": [
        "child",
        "children",
        "kid",
        "kids",
        "toddler",
        "baby",
    ],

    "elderly": [
        "elderly",
        "senior",
        "older adult",
        "old person",
        "grandfather",
        "grandmother",
    ],

    "pet": [
        "pet",
        "dog",
        "puppy",
        "cat",
    ],
}


# ============================================================
# TIME PATTERNS
#
# Longer phrases must come before shorter phrases.
# ============================================================

TIME_PATTERNS = [
    "this morning",
    "this afternoon",
    "this evening",
    "tonight",
    "tomorrow",
    "today",
    "now",
]


# ============================================================
# EXTRACT ACTIVITY
# ============================================================

def extract_activity(
    message: str,
) -> str | None:
    """
    Extract a normalized activity from the user's message.
    """

    message_lower = message.lower()

    for activity, patterns in ACTIVITY_PATTERNS.items():

        for pattern in patterns:

            pattern_regex = (
                r"\b"
                + re.escape(pattern.lower())
                + r"\b"
            )

            if re.search(
                pattern_regex,
                message_lower,
            ):

                return activity

    return None


# ============================================================
# EXTRACT VULNERABLE GROUP
# ============================================================

def extract_vulnerable_group(
    message: str,
) -> str | None:
    """
    Detect vulnerable groups such as children,
    elderly people, or pets.
    """

    message_lower = message.lower()

    for group, patterns in (
        VULNERABLE_GROUP_PATTERNS.items()
    ):

        for pattern in patterns:

            pattern_regex = (
                r"\b"
                + re.escape(pattern.lower())
                + r"\b"
            )

            if re.search(
                pattern_regex,
                message_lower,
            ):

                return group

    return None


# ============================================================
# EXTRACT TIME
# ============================================================

def extract_time(
    message: str,
) -> str | None:
    """
    Extract a supported time reference.

    Returns None when the user does not specify
    a time explicitly.
    """

    message_lower = message.lower()

    for time_value in TIME_PATTERNS:

        pattern_regex = (
            r"\b"
            + re.escape(time_value)
            + r"\b"
        )

        if re.search(
            pattern_regex,
            message_lower,
        ):

            return time_value

    return None


# ============================================================
# EXTRACT LOCATION
# ============================================================

def extract_location(
    message: str,
) -> str | None:
    """
    Extract a location from phrases such as:

        in Hyderabad
        at Bhopal
        near Delhi

    The extraction stops before common time words
    and question boundaries.
    """

    patterns = [
        r"\bin\s+([A-Z][a-zA-Z\s-]*?)(?=\s+(?:today|tomorrow|this morning|this afternoon|this evening|tonight|now)\b|[?.!,]|$)",
        r"\bat\s+([A-Z][a-zA-Z\s-]*?)(?=\s+(?:today|tomorrow|this morning|this afternoon|this evening|tonight|now)\b|[?.!,]|$)",
        r"\bnear\s+([A-Z][a-zA-Z\s-]*?)(?=\s+(?:today|tomorrow|this morning|this afternoon|this evening|tonight|now)\b|[?.!,]|$)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            message,
            flags=re.IGNORECASE,
        )

        if match:

            location = match.group(1).strip()

            if location:

                return location

    return None


# ============================================================
# PROCESS INTAKE
# ============================================================

def process_intake(
    message: str,
    previous_context: UserContext | None = None,
) -> UserContext:
    """
    Convert a natural-language user message
    into structured UserContext.

    Missing information can be inherited from
    the previous conversation context.

    Explicitly supplied information in the new
    message always overrides previous context.
    """

    # --------------------------------------------------------
    # Extract information from the current message
    # --------------------------------------------------------

    activity = extract_activity(
        message
    )

    location = extract_location(
        message
    )

    time_reference = extract_time(
        message
    )

    vulnerable_group = extract_vulnerable_group(
        message
    )

    # --------------------------------------------------------
    # SESSION MEMORY FALLBACK
    # --------------------------------------------------------

    if previous_context:

        # Activity inheritance
        if not activity:

            activity = (
                previous_context.activity
            )

        # Location inheritance
        if not location:

            location = (
                previous_context.location
            )

        # Vulnerable group inheritance
        if not vulnerable_group:

            vulnerable_group = (
                previous_context.vulnerable_group
            )

        # Time inheritance
        #
        # Only inherit previous time if the new
        # message does not explicitly specify one.
        if not time_reference:

            time_reference = (
                previous_context.time_reference
                or "now"
            )

    # --------------------------------------------------------
    # DEFAULT TIME
    # --------------------------------------------------------

    if not time_reference:

        time_reference = "now"

    # --------------------------------------------------------
    # DEBUG OUTPUT
    # --------------------------------------------------------

    print(
        "\n========== INTAKE =========="
    )

    print(
        "[INTAKE] Message:",
        message,
    )

    print(
        "[INTAKE] Activity:",
        activity,
    )

    print(
        "[INTAKE] Location:",
        location,
    )

    print(
        "[INTAKE] Time reference:",
        time_reference,
    )

    print(
        "[INTAKE] Vulnerable group:",
        vulnerable_group,
    )

    print(
        "============================\n"
    )

    return UserContext(
        activity=activity,
        location=location,
        time_reference=time_reference,
        vulnerable_group=vulnerable_group,
        raw_message=message,
    )