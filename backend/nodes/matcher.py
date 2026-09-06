from backend.models import SOP, UserContext, WeatherData


SEVERITY_RANK = {
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
}


def evaluate_condition(
    actual_value,
    operator: str,
    expected_value,
) -> bool:
    """
    Generic condition evaluator.

    This function does not know anything about a specific SOP.
    It simply evaluates:

        actual_value operator expected_value
    """

    if actual_value is None:
        return False

    if operator == ">=":
        return actual_value >= expected_value

    elif operator == ">":
        return actual_value > expected_value

    elif operator == "<=":
        return actual_value <= expected_value

    elif operator == "<":
        return actual_value < expected_value

    elif operator == "==":
        return actual_value == expected_value

    return False


def activity_matches(
    context: UserContext,
    keywords: list[str],
) -> bool:
    """
    Check whether the extracted activity or raw user message
    matches one of the SOP intent keywords.
    """

    if not keywords:
        return True

    activity = (context.activity or "").lower()
    message = context.raw_message.lower()

    for keyword in keywords:
        keyword = keyword.lower()

        if keyword in activity:
            return True

        if keyword in message:
            return True

    return False


def weather_matches(
    weather: WeatherData,
    sop: SOP,
) -> bool:
    """
    Evaluate every weather condition defined in the SOP.
    """

    for field_name, condition in sop.weather_conditions.items():

        actual_value = getattr(
            weather,
            field_name,
            None,
        )

        if not evaluate_condition(
            actual_value,
            condition.operator,
            condition.value,
        ):
            return False

    return True


def find_matching_sops(
    context: UserContext,
    weather: WeatherData,
    sops: dict[str, SOP],
) -> list[SOP]:
    """
    Find every SOP that applies to the current
    user context and live weather data.
    """

    matches = []

    for sop in sops.values():

        intent_ok = activity_matches(
            context,
            sop.intent_keywords,
        )

        weather_ok = weather_matches(
            weather,
            sop,
        )

        if intent_ok and weather_ok:
            matches.append(sop)

    return matches


def select_best_sop(
    matches: list[SOP],
) -> SOP | None:
    """
    Conflict resolution rule:

    1. Higher priority wins.
    2. If priority is the same, higher severity wins.
    """

    if not matches:
        return None

    return max(
        matches,
        key=lambda sop: (
            sop.priority,
            SEVERITY_RANK.get(
                sop.severity.lower(),
                0,
            ),
        ),
    )
    
def match_sop_node(state: dict) -> dict:
    """
    LangGraph node that finds and selects
    the best applicable SOP.
    """

    from backend.loader import load_sops

    context = state["context"]
    weather = state["weather"]

    sops = load_sops()

    matches = find_matching_sops(
        context,
        weather,
        sops,
    )

    selected_sop = select_best_sop(matches)

    return {
        **state,
        "matching_sops": matches,
        "selected_sop": selected_sop,
    }