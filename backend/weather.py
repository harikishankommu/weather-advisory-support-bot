from datetime import datetime, timedelta

import requests

from backend.models import WeatherData


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def get_coordinates(city: str) -> dict | None:
    """
    Convert a city name into latitude and longitude.
    """

    try:
        response = requests.get(
            GEOCODING_URL,
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("results"):
            return None

        result = data["results"][0]

        return {
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "name": result.get("name"),
            "country": result.get("country"),
        }

    except requests.RequestException:
        return None


def get_target_time(
    time_reference: str,
) -> datetime:
    """
    Convert a simple natural-language time reference
    into a target datetime.
    """

    now = datetime.now()

    time_reference = (
        time_reference or "now"
    ).lower()

    if time_reference == "tomorrow":

        target = now + timedelta(days=1)

        return target.replace(
            hour=12,
            minute=0,
            second=0,
            microsecond=0,
        )

    if time_reference == "today":

        return now.replace(
            hour=12,
            minute=0,
            second=0,
            microsecond=0,
        )

    if time_reference == "this morning":

        return now.replace(
            hour=9,
            minute=0,
            second=0,
            microsecond=0,
        )

    if time_reference == "this afternoon":

        return now.replace(
            hour=15,
            minute=0,
            second=0,
            microsecond=0,
        )

    if time_reference == "this evening":

        return now.replace(
            hour=18,
            minute=0,
            second=0,
            microsecond=0,
        )

    if time_reference == "tonight":

        return now.replace(
            hour=21,
            minute=0,
            second=0,
            microsecond=0,
        )

    return now


def find_closest_hour_index(
    hourly_times: list[str],
    target_time: datetime,
) -> int:
    """
    Find the forecast hour closest to the requested time.
    """

    parsed_times = [
        datetime.fromisoformat(time)
        for time in hourly_times
    ]

    closest_index = min(
        range(len(parsed_times)),
        key=lambda index: abs(
            parsed_times[index] - target_time
        ),
    )

    return closest_index


def get_weather(
    latitude: float,
    longitude: float,
    time_reference: str = "now",
) -> WeatherData | None:
    """
    Fetch weather forecast and select the hour
    closest to the requested time.
    """

    try:

        response = requests.get(
            WEATHER_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "hourly": (
                    "temperature_2m,"
                    "wind_speed_10m,"
                    "precipitation,"
                    "precipitation_probability,"
                    "uv_index,"
                    "weather_code"
                ),
                "forecast_days": 3,
                "timezone": "auto",
            },
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        hourly = data.get("hourly")

        if not hourly:
            return None

        target_time = get_target_time(
            time_reference
        )

        times = hourly.get("time", [])

        if not times:
            return None

        index = find_closest_hour_index(
            times,
            target_time,
        )

        return WeatherData(
            temperature_2m=hourly[
                "temperature_2m"
            ][index],

            wind_speed_10m=hourly[
                "wind_speed_10m"
            ][index],

            precipitation=hourly[
                "precipitation"
            ][index],

            precipitation_probability=hourly[
                "precipitation_probability"
            ][index],

            uv_index=hourly[
                "uv_index"
            ][index],

            weather_code=hourly[
                "weather_code"
            ][index],
        )

    except (
        requests.RequestException,
        KeyError,
        IndexError,
        ValueError,
    ):
        return None


def get_live_weather(
    city: str,
    time_reference: str = "now",
) -> dict | None:
    """
    Complete weather pipeline.

    City
        ↓
    Coordinates
        ↓
    Forecast
        ↓
    Requested time
    """

    coordinates = get_coordinates(city)

    if not coordinates:
        return None

    weather = get_weather(
        coordinates["latitude"],
        coordinates["longitude"],
        time_reference,
    )

    if not weather:
        return None

    return {
        "location": coordinates,
        "weather": weather,
        "time_reference": time_reference,
    }