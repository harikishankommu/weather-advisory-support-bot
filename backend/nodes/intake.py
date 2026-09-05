import re

from backend.models import UserContext


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


TIME_PATTERNS = [
    "today",
    "tomorrow",
    "this morning",
    "this afternoon",
    "this evening",
    "tonight",
    "now",
]


def extract_activity(message: str) -> str | None:
    """
    Extract a normalized activity from the user's message.
    """

    message_lower = message.lower()

    for activity, patterns in ACTIVITY_PATTERNS.items():

        for pattern in patterns:

            if pattern in message_lower:
                return activity

    return None


def extract_vulnerable_group(
    message: str,
) -> str | None:
    """
    Detect vulnerable groups such as children,
    elderly people, or pets.
    """

    message_lower = message.lower()

    for group, patterns in VULNERABLE_GROUP_PATTERNS.items():

        for pattern in patterns:

            if pattern in message_lower:
                return group

    return None


def extract_time(
    message: str,
) -> str:
    """
    Extract a basic time reference.
    """

    message_lower = message.lower()

    for time_value in TIME_PATTERNS:

        if time_value in message_lower:
            return time_value

    return "now"


def extract_location(
    message: str,
) -> str | None:
    """
    Simple location extraction.

    Looks for phrases such as:

    in Hyderabad
    at Bhopal
    near Delhi
    """

    patterns = [
        r"\bin\s+([A-Z][a-zA-Z\s]+)",
        r"\bat\s+([A-Z][a-zA-Z\s]+)",
        r"\bnear\s+([A-Z][a-zA-Z\s]+)",
    ]

    for pattern in patterns:

        match = re.search(pattern, message)

        if match:

            location = match.group(1).strip()

            # Remove common time words if captured
            for time_value in TIME_PATTERNS:

                location = re.sub(
                    rf"\b{time_value}\b",
                    "",
                    location,
                    flags=re.IGNORECASE,
                ).strip()

            return location

    return None


def process_intake(
    message: str,
    previous_context: UserContext | None = None,
) -> UserContext:
    """
    Convert a natural language user message
    into structured UserContext.

    Missing values can be inherited from the
    previous conversation context.
    """

    activity = extract_activity(message)

    location = extract_location(message)

    time_reference = extract_time(message)

    vulnerable_group = extract_vulnerable_group(
        message
    )

    # Session memory fallback
    if previous_context:

        if not activity:
            activity = previous_context.activity

        if not location:
            location = previous_context.location

        if not vulnerable_group:
            vulnerable_group = (
                previous_context.vulnerable_group
            )

    return UserContext(
        activity=activity,
        location=location,
        time_reference=time_reference,
        vulnerable_group=vulnerable_group,
        raw_message=message,
    )