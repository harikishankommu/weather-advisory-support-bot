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

        user_ok = user_conditions_match(
            context,
            sop,
        )

        if intent_ok and weather_ok and user_ok:
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
    from backend.loader import load_sops

    context = state["context"]
    weather = state["weather"]

    print("\n========== SOP MATCHER ==========")

    print("[MATCHER] Context:")
    print(context)

    print("[MATCHER] Weather:")
    print(weather)

    sops = load_sops()

    print("[MATCHER] Loaded SOPs:")
    print(list(sops.keys()))

    matches = find_matching_sops(
        context,
        weather,
        sops,
    )

    print("[MATCHER] Matching SOPs:")

    for sop in matches:
        print(
            f"- {sop.id} | "
            f"severity={sop.severity} | "
            f"priority={sop.priority}"
        )

    selected_sop = select_best_sop(matches)

    print("[MATCHER] Selected SOP:")

    if selected_sop:
        print(selected_sop.id)
    else:
        print("None")

    print("=================================\n")

    return {
        **state,
        "matching_sops": matches,
        "selected_sop": selected_sop,
    }

def user_conditions_match(
    context: UserContext,
    sop: SOP,
) -> bool:
    """
    Check whether the user context satisfies
    the user_conditions defined in the SOP.
    """

    if not sop.user_conditions:
        return True

    for field_name, expected_value in sop.user_conditions.items():

        actual_value = getattr(
            context,
            field_name,
            None,
        )

        if actual_value is None:
            return False

        if isinstance(expected_value, list):

            if actual_value not in expected_value:
                return False

        else:

            if actual_value != expected_value:
                return False

    return True