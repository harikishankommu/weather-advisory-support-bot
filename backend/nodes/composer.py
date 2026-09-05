def compose_response_node(state: dict) -> dict:
    """
    Create a final response grounded only in:

    1. Selected SOP
    2. Retrieved weather data
    """

    selected_sop = state["selected_sop"]
    weather = state["weather"]
    context = state["context"]
    location = state["location_data"]

    reply = f"""
Weather Advisory

Location: {location["name"]}
Time: {context.time_reference}

Selected SOP: {selected_sop.id}
Severity: {selected_sop.severity.upper()}

Weather conditions:
- Temperature: {weather.temperature_2m} °C
- Wind speed: {weather.wind_speed_10m} km/h
- Precipitation: {weather.precipitation} mm
- Precipitation probability: {weather.precipitation_probability}%
- UV index: {weather.uv_index}

Guidance:
{selected_sop.guidance}
""".strip()

    return {
        **state,
        "reply": reply,
    }