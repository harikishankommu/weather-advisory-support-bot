from typing import TypedDict, Optional

from langgraph.graph import StateGraph, START, END

from backend.models import UserContext, WeatherData, SOP
from backend.nodes.intake import process_intake
from backend.nodes.weather_node import fetch_weather_node
from backend.nodes.matcher import match_sop_node
from backend.nodes.composer import compose_response_node
from backend.nodes.fallback import (
    missing_location_node,
    weather_error_node,
    no_guidance_node,
)


class WeatherBotState(TypedDict, total=False):
    message: str
    session_id: str

    context: UserContext
    weather: WeatherData
    location_data: dict

    matching_sops: list[SOP]
    selected_sop: Optional[SOP]

    error: Optional[str]
    reply: str


def intake_node(state: WeatherBotState) -> dict:
    """
    Convert the user's natural-language message
    into structured context while preserving
    previous session context.
    """

    from backend.memory import session_memory

    session_id = state.get("session_id", "default")

    previous_context = session_memory.get_context(
        session_id
    )

    context = process_intake(
        state["message"],
        previous_context,
    )

    session_memory.update_context(
        session_id,
        context,
    )

    return {
        "context": context
    }
    
    
def route_after_intake(
    state: WeatherBotState,
) -> str:
    """
    Decide whether we have enough information
    to fetch weather.
    """

    context = state["context"]

    if not context.location:
        return "missing_location"

    return "weather"


def route_after_weather(
    state: WeatherBotState,
) -> str:
    """
    Decide whether weather retrieval succeeded.
    """

    if state.get("error"):
        return "weather_error"

    return "matcher"


def route_after_matcher(
    state: WeatherBotState,
) -> str:
    """
    Decide whether any SOP applies.
    """

    if not state.get("selected_sop"):
        return "no_guidance"

    return "composer"


def build_graph():
    """
    Build the Weather Advisory Support Bot graph.
    """

    builder = StateGraph(WeatherBotState)

    # Add nodes
    builder.add_node("intake", intake_node)

    builder.add_node(
        "weather",
        fetch_weather_node,
    )

    builder.add_node(
        "matcher",
        match_sop_node,
    )

    builder.add_node(
        "composer",
        compose_response_node,
    )

    builder.add_node(
        "missing_location",
        missing_location_node,
    )

    builder.add_node(
        "weather_error",
        weather_error_node,
    )

    builder.add_node(
        "no_guidance",
        no_guidance_node,
    )

    # Start
    builder.add_edge(
        START,
        "intake",
    )

    # After intake
    builder.add_conditional_edges(
        "intake",
        route_after_intake,
        {
            "missing_location": "missing_location",
            "weather": "weather",
        },
    )

    # After weather
    builder.add_conditional_edges(
        "weather",
        route_after_weather,
        {
            "weather_error": "weather_error",
            "matcher": "matcher",
        },
    )

    # After matcher
    builder.add_conditional_edges(
        "matcher",
        route_after_matcher,
        {
            "no_guidance": "no_guidance",
            "composer": "composer",
        },
    )

    # End branches
    builder.add_edge(
        "composer",
        END,
    )

    builder.add_edge(
        "missing_location",
        END,
    )

    builder.add_edge(
        "weather_error",
        END,
    )

    builder.add_edge(
        "no_guidance",
        END,
    )

    return builder.compile()


# Create the compiled graph
weather_bot_graph = build_graph()