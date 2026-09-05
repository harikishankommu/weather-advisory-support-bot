from backend.weather import get_live_weather


def fetch_weather_node(state: dict) -> dict:
    """
    Fetch live weather using the location extracted
    during the intake step.
    """

    context = state["context"]

    if not context.location:
        return {
            **state,
            "error": "missing_location",
        }

    result = get_live_weather(
        context.location,
        context.time_reference,
    )

    if not result:
        return {
            **state,
            "error": "weather_fetch_failed",
        }

    return {
        **state,
        "location_data": result["location"],
        "weather": result["weather"],
        "error": None,
    }