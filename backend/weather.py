from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import requests

from backend.models import WeatherData


GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def get_coordinates(city: str) -> dict | None:
    """
    Convert a city name into latitude and longitude
    using the Open-Meteo Geocoding API.
    """

    try:

        print(
            f"[WEATHER] Searching coordinates for: {city}",
            flush=True,
        )

        response = requests.get(
            GEOCODING_URL,
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=15,
        )

        print(
            f"[WEATHER] Geocoding status: {response.status_code}",
            flush=True,
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results")

        if not results:

            print(
                f"[WEATHER ERROR] No coordinates found for: {city}",
                flush=True,
            )

            return None

        result = results[0]

        location = {
            "latitude": result["latitude"],
            "longitude": result["longitude"],
            "name": result.get("name", city),
            "country": result.get("country"),
            "timezone": result.get("timezone"),
        }

        print(
            f"[WEATHER] Location found: {location}",
            flush=True,
        )

        return location

    except requests.RequestException as error:

        print(
            f"[WEATHER ERROR] Geocoding request failed: {error}",
            flush=True,
        )

        return None

    except (KeyError, ValueError) as error:

        print(
            f"[WEATHER ERROR] Invalid geocoding response: {error}",
            flush=True,
        )

        return None


def normalize_time_reference(
    time_reference: str | None,
) -> str:
    """
    Normalize the extracted time reference.
    """

    if not time_reference:
        return "now"

    return time_reference.strip().lower()


def get_target_time(
    time_reference: str | None,
    timezone_name: str | None = None,
) -> datetime:
    """
    Convert a natural-language time reference
    into a target datetime.

    The returned datetime is converted to a naive
    local datetime because Open-Meteo hourly timestamps
    are returned as local timestamps.
    """

    time_reference = normalize_time_reference(
        time_reference
    )

    try:

        if timezone_name:

            now = datetime.now(
                ZoneInfo(timezone_name)
            )

        else:

            now = datetime.now()

    except Exception:

        now = datetime.now()

    # Convert timezone-aware datetime into naive local time
    now = now.replace(
        tzinfo=None
    )

    print(
        f"[WEATHER] Time reference: {time_reference}",
        flush=True,
    )

    print(
        f"[WEATHER] Local target timezone: {timezone_name}",
        flush=True,
    )

    # Tomorrow

    if time_reference == "tomorrow":

        target = now + timedelta(days=1)

        return target.replace(
            hour=12,
            minute=0,
            second=0,
            microsecond=0,
        )

    # Today

    if time_reference == "today":

        return now.replace(
            hour=12,
            minute=0,
            second=0,
            microsecond=0,
        )

    # Morning

    if time_reference in [
        "morning",
        "this morning",
    ]:

        return now.replace(
            hour=9,
            minute=0,
            second=0,
            microsecond=0,
        )

    # Afternoon

    if time_reference in [
        "afternoon",
        "this afternoon",
    ]:

        return now.replace(
            hour=15,
            minute=0,
            second=0,
            microsecond=0,
        )

    # Evening

    if time_reference in [
        "evening",
        "this evening",
    ]:

        return now.replace(
            hour=18,
            minute=0,
            second=0,
            microsecond=0,
        )

    # Night

    if time_reference in [
        "night",
        "tonight",
        "this night",
    ]:

        return now.replace(
            hour=21,
            minute=0,
            second=0,
            microsecond=0,
        )

    # Default: current local time

    return now


def find_closest_hour_index(
    hourly_times: list[str],
    target_time: datetime,
) -> int:
    """
    Find the Open-Meteo forecast hour closest
    to the requested target time.
    """

    if not hourly_times:

        raise ValueError(
            "Hourly weather timestamps are empty."
        )

    parsed_times = []

    for time_string in hourly_times:

        parsed_time = datetime.fromisoformat(
            time_string
        )

        parsed_times.append(
            parsed_time
        )

    closest_index = min(
        range(len(parsed_times)),
        key=lambda index: abs(
            parsed_times[index] - target_time
        ),
    )

    print(
        f"[WEATHER] Target time: {target_time.isoformat()}",
        flush=True,
    )

    print(
        "[WEATHER] Selected forecast time: "
        f"{parsed_times[closest_index].isoformat()}",
        flush=True,
    )

    return closest_index


def get_weather(
    latitude: float,
    longitude: float,
    time_reference: str = "now",
    timezone_name: str | None = None,
) -> WeatherData | None:
    """
    Fetch hourly weather data from Open-Meteo
    and select the hour closest to the requested time.
    """

    try:

        print(
            "[WEATHER] Fetching weather for "
            f"latitude={latitude}, "
            f"longitude={longitude}",
            flush=True,
        )

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
            timeout=15,
        )

        print(
            f"[WEATHER] Weather API status: {response.status_code}",
            flush=True,
        )

        response.raise_for_status()

        data = response.json()

        # Log API error if Open-Meteo returns one

        if "error" in data:

            print(
                f"[WEATHER ERROR] Open-Meteo error: {data}",
                flush=True,
            )

            return None

        hourly = data.get("hourly")

        if not hourly:

            print(
                "[WEATHER ERROR] Hourly weather data is missing.",
                flush=True,
            )

            print(
                f"[WEATHER ERROR] Response: {data}",
                flush=True,
            )

            return None

        times = hourly.get(
            "time",
            [],
        )

        if not times:

            print(
                "[WEATHER ERROR] Hourly timestamps are missing.",
                flush=True,
            )

            return None

        # Prefer the timezone returned by Open-Meteo

        api_timezone = data.get(
            "timezone",
            timezone_name,
        )

        target_time = get_target_time(
            time_reference,
            api_timezone,
        )

        index = find_closest_hour_index(
            times,
            target_time,
        )

        required_fields = [
            "temperature_2m",
            "wind_speed_10m",
            "precipitation",
            "precipitation_probability",
            "uv_index",
            "weather_code",
        ]

        for field in required_fields:

            if field not in hourly:

                print(
                    f"[WEATHER ERROR] Missing field: {field}",
                    flush=True,
                )

                return None

            if index >= len(hourly[field]):

                print(
                    f"[WEATHER ERROR] Index out of range "
                    f"for field: {field}",
                    flush=True,
                )

                return None

        weather = WeatherData(

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

        print(
            f"[WEATHER] Weather data retrieved: {weather}",
            flush=True,
        )

        return weather

    except requests.Timeout as error:

        print(
            f"[WEATHER ERROR] Weather request timed out: {error}",
            flush=True,
        )

        return None

    except requests.RequestException as error:

        print(
            f"[WEATHER ERROR] Weather API request failed: {error}",
            flush=True,
        )

        return None

    except KeyError as error:

        print(
            f"[WEATHER ERROR] Missing weather key: {error}",
            flush=True,
        )

        return None

    except IndexError as error:

        print(
            f"[WEATHER ERROR] Weather index error: {error}",
            flush=True,
        )

        return None

    except ValueError as error:

        print(
            f"[WEATHER ERROR] Weather value error: {error}",
            flush=True,
        )

        return None

    except Exception as error:

        print(
            "[WEATHER ERROR] Unexpected error: "
            f"{type(error).__name__}: {error}",
            flush=True,
        )

        return None


def get_live_weather(
    city: str,
    time_reference: str = "now",
) -> dict | None:
    """
    Complete live weather pipeline.

        City
          ↓
        Geocoding
          ↓
        Latitude / Longitude
          ↓
        Open-Meteo Forecast
          ↓
        Select requested time
          ↓
        WeatherData
    """

    print(
        "\n========== WEATHER PIPELINE ==========",
        flush=True,
    )

    print(
        f"[WEATHER] Requested city: {city}",
        flush=True,
    )

    print(
        f"[WEATHER] Requested time: {time_reference}",
        flush=True,
    )

    coordinates = get_coordinates(
        city
    )

    if not coordinates:

        print(
            "[WEATHER ERROR] Could not resolve city coordinates.",
            flush=True,
        )

        return None

    weather = get_weather(
        latitude=coordinates["latitude"],
        longitude=coordinates["longitude"],
        time_reference=time_reference,
        timezone_name=coordinates.get("timezone"),
    )

    if not weather:

        print(
            "[WEATHER ERROR] Could not retrieve weather data.",
            flush=True,
        )

        return None

    result = {

        "location": coordinates,

        "weather": weather,

        "time_reference": time_reference,
    }

    print(
        "[WEATHER] Pipeline completed successfully.",
        flush=True,
    )

    print(
        "======================================\n",
        flush=True,
    )

    return result