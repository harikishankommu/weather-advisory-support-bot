def missing_location_node(state: dict) -> dict:
    """
    Used when no location is available.
    """

    return {
        **state,
        "reply": (
            "I need a location to check live weather conditions. "
            "Please tell me the city or location you are asking about."
        ),
    }


def weather_error_node(state: dict) -> dict:
    """
    Used when geocoding or weather retrieval fails.
    """

    return {
        **state,
        "reply": (
            "I couldn't retrieve live weather data for this location, "
            "so I can't provide a weather-grounded advisory right now."
        ),
    }


def no_guidance_node(state: dict) -> dict:
    """
    Used when weather data is available but no SOP applies.
    """

    return {
        **state,
        "reply": (
            "I found the weather data, but I don't have a specific "
            "SOP that applies to this situation. "
            "I can't provide a policy-grounded advisory."
        ),
    }