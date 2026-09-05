from datetime import datetime, timedelta
from time import sleep
from threading import Lock

import requests

from backend.models import WeatherData


GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
)


# -------------------------------------------------
# API configuration
# -------------------------------------------------

REQUEST_TIMEOUT = 15

MAX_RETRIES = 3

RETRY_BACKOFF_SECONDS = 2


# -------------------------------------------------
# Simple in-memory caches
# -------------------------------------------------

COORDINATE_CACHE: dict[str, dict] = {}

WEATHER_CACHE: dict[
    tuple[float, float, str],
    tuple[datetime, WeatherData]
] = {}

CACHE_DURATION = timedelta(minutes=10)

CACHE_LOCK = Lock()


# -------------------------------------------------
# Shared HTTP session
# -------------------------------------------------

HTTP_SESSION = requests.Session()

HTTP_SESSION.headers.update(
    {
        "User-Agent": (
            "Weather-Advisory-Support-Bot/1.0"
        )
    }
)


# -------------------------------------------------
# Coordinate lookup
# -------------------------------------------------

def get_coordinates(city: str) -> dict | None:
    """
    Convert a city name into latitude and longitude
    using the Open-Meteo Geocoding API.

    Results are cached in memory to avoid repeated
    geocoding requests for the same city.
    """

    normalized_city = city.strip().lower()

    if not normalized_city:
        return None

    with CACHE_LOCK:

        cached = COORDINATE_CACHE.get(
            normalized_city
        )

    if cached:

        print(
            f"[WEATHER CACHE] Using cached "
            f"coordinates for: {city}"
        )

        return cached

    try:

        print(
            f"[WEATHER] Searching coordinates for: "
            f"{city}"
        )

        response = HTTP_SESSION.get(
            GEOCODING_URL,
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=REQUEST_TIMEOUT,
        )

        print(
            "[WEATHER] Geocoding status:",
            response.status_code,
        )

        response.raise_for_status()

        data = response.json()

        results = data.get("results")

        if not results:

            print(
                f"[WEATHER] No coordinates found "
                f"for city: {city}"
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

        with CACHE_LOCK:

            COORDINATE_CACHE[
                normalized_city
            ] = location

        print(
            "[WEATHER] Location found:",
            location,
        )

        return location

    except requests.RequestException as error:

        print(
            f"[WEATHER ERROR] "
            f"Geocoding request failed: {error}"
        )

        return None

    except (
        KeyError,
        ValueError,
    ) as error:

        print(
            f"[WEATHER ERROR] "
            f"Invalid geocoding response: {error}"
        )

        return None


# -------------------------------------------------
# Time handling
# -------------------------------------------------

def normalize_time_reference(
    time_reference: str | None,
) -> str:

    if not time_reference:

        return "now"

    return time_reference.strip().lower()


def get_target_time(
    time_reference: str | None,
) -> datetime:
    """
    Convert supported natural-language time
    references into a target datetime.
    """

    now = datetime.now()

    time_reference = normalize_time_reference(
        time_reference
    )

    print(
        f"[WEATHER] Time reference: "
        f"{time_reference}"
    )

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

    return now


# -------------------------------------------------
# Find closest forecast hour
# -------------------------------------------------

def find_closest_hour_index(
    hourly_times: list[str],
    target_time: datetime,
) -> int:

    if not hourly_times:

        raise ValueError(
            "Hourly weather timestamps are empty."
        )

    parsed_times = [
        datetime.fromisoformat(time_string)
        for time_string in hourly_times
    ]

    closest_index = min(
        range(len(parsed_times)),
        key=lambda index: abs(
            parsed_times[index]
            - target_time
        ),
    )

    print(
        "[WEATHER] Target time:",
        target_time.isoformat(),
    )

    print(
        "[WEATHER] Selected forecast time:",
        parsed_times[
            closest_index
        ].isoformat(),
    )

    return closest_index


# -------------------------------------------------
# Weather API request with retry
# -------------------------------------------------

def fetch_weather_data(
    latitude: float,
    longitude: float,
) -> dict | None:
    """
    Call Open-Meteo with retry and exponential
    backoff when rate-limited.
    """

    params = {
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
    }

    for attempt in range(
        1,
        MAX_RETRIES + 1,
    ):

        try:

            print(
                f"[WEATHER] API request "
                f"attempt {attempt}/"
                f"{MAX_RETRIES}"
            )

            response = HTTP_SESSION.get(
                WEATHER_URL,
                params=params,
                timeout=REQUEST_TIMEOUT,
            )

            print(
                "[WEATHER] Weather API status:",
                response.status_code,
            )

            # Rate limited
            if response.status_code == 429:

                if attempt == MAX_RETRIES:

                    print(
                        "[WEATHER ERROR] "
                        "Rate limit reached after "
                        "all retry attempts."
                    )

                    return None

                retry_after = response.headers.get(
                    "Retry-After"
                )

                if retry_after:

                    try:

                        wait_time = float(
                            retry_after
                        )

                    except ValueError:

                        wait_time = (
                            RETRY_BACKOFF_SECONDS
                            * attempt
                        )

                else:

                    wait_time = (
                        RETRY_BACKOFF_SECONDS
                        * (2 ** (attempt - 1))
                    )

                print(
                    "[WEATHER] Rate limited. "
                    f"Waiting {wait_time} seconds "
                    "before retrying."
                )

                sleep(wait_time)

                continue

            response.raise_for_status()

            return response.json()

        except requests.RequestException as error:

            if attempt == MAX_RETRIES:

                print(
                    f"[WEATHER ERROR] "
                    f"Weather API request failed: "
                    f"{error}"
                )

                return None

            wait_time = (
                RETRY_BACKOFF_SECONDS
                * (2 ** (attempt - 1))
            )

            print(
                f"[WEATHER WARNING] "
                f"Request failed: {error}"
            )

            print(
                f"[WEATHER] Retrying in "
                f"{wait_time} seconds..."
            )

            sleep(wait_time)

    return None


# -------------------------------------------------
# Get weather
# -------------------------------------------------

def get_weather(
    latitude: float,
    longitude: float,
    time_reference: str = "now",
) -> WeatherData | None:
    """
    Fetch hourly weather data and select the
    forecast hour closest to the requested time.

    Results are cached temporarily to reduce
    repeated Open-Meteo API calls.
    """

    normalized_time = normalize_time_reference(
        time_reference
    )

    cache_key = (
        round(latitude, 4),
        round(longitude, 4),
        normalized_time,
    )

    now = datetime.now()

    with CACHE_LOCK:

        cached = WEATHER_CACHE.get(
            cache_key
        )

    if cached:

        cached_time, cached_weather = cached

        if now - cached_time < CACHE_DURATION:

            print(
                "[WEATHER CACHE] Using cached "
                "weather data."
            )

            return cached_weather

    print(
        "[WEATHER] Fetching weather for "
        f"latitude={latitude}, "
        f"longitude={longitude}"
    )

    data = fetch_weather_data(
        latitude,
        longitude,
    )

    if not data:

        return None

    try:

        hourly = data.get("hourly")

        if not hourly:

            print(
                "[WEATHER ERROR] "
                "Hourly weather data is missing."
            )

            return None

        times = hourly.get(
            "time",
            [],
        )

        if not times:

            print(
                "[WEATHER ERROR] "
                "Hourly timestamps are missing."
            )

            return None

        target_time = get_target_time(
            normalized_time
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
                    "[WEATHER ERROR] "
                    f"Missing weather field: "
                    f"{field}"
                )

                return None

            if index >= len(
                hourly[field]
            ):

                print(
                    "[WEATHER ERROR] "
                    f"Index {index} out of range "
                    f"for field: {field}"
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

        with CACHE_LOCK:

            WEATHER_CACHE[
                cache_key
            ] = (
                datetime.now(),
                weather,
            )

        print(
            "[WEATHER] Weather data retrieved:",
            weather,
        )

        return weather

    except (
        KeyError,
        IndexError,
        ValueError,
    ) as error:

        print(
            f"[WEATHER ERROR] "
            f"Weather parsing failed: {error}"
        )

        return None

    except Exception as error:

        print(
            f"[WEATHER ERROR] "
            f"Unexpected error: "
            f"{type(error).__name__}: {error}"
        )

        return None


# -------------------------------------------------
# Complete pipeline
# -------------------------------------------------

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
        Retry if rate-limited
          ↓
        Select requested time
          ↓
        WeatherData
    """

    print(
        "\n========== WEATHER PIPELINE =========="
    )

    print(
        f"[WEATHER] Requested city: {city}"
    )

    print(
        "[WEATHER] Requested time:",
        time_reference,
    )

    coordinates = get_coordinates(
        city
    )

    if not coordinates:

        print(
            "[WEATHER ERROR] "
            "Could not resolve city coordinates."
        )

        return None

    weather = get_weather(
        latitude=coordinates["latitude"],
        longitude=coordinates["longitude"],
        time_reference=time_reference,
    )

    if not weather:

        print(
            "[WEATHER ERROR] "
            "Could not retrieve weather data."
        )

        return None

    result = {

        "location": coordinates,

        "weather": weather,

        "time_reference": time_reference,
    }

    print(
        "[WEATHER] Pipeline completed "
        "successfully."
    )

    print(
        "======================================\n"
    )

    return result