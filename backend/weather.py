from datetime import datetime, timedelta
from time import sleep
from zoneinfo import ZoneInfo

import requests

from backend.models import WeatherData


GEOCODING_URL = (
    "https://geocoding-api.open-meteo.com/v1/search"
)

WEATHER_URL = (
    "https://api.open-meteo.com/v1/forecast"
)


# ============================================================
# CACHE SETTINGS
# ============================================================

COORDINATE_CACHE_TTL = timedelta(hours=24)

WEATHER_CACHE_TTL = timedelta(minutes=10)


# ============================================================
# IN-MEMORY CACHES
# ============================================================

_coordinate_cache: dict = {}

_weather_cache: dict = {}


# ============================================================
# HTTP SESSION
# ============================================================

session = requests.Session()


# ============================================================
# CACHE HELPERS
# ============================================================

def get_cached_value(
    cache: dict,
    key: str,
    ttl: timedelta,
):

    cached = cache.get(key)

    if not cached:
        return None

    value = cached["value"]

    timestamp = cached["timestamp"]

    if datetime.now() - timestamp > ttl:

        del cache[key]

        return None

    return value


def set_cached_value(
    cache: dict,
    key: str,
    value,
):

    cache[key] = {

        "value": value,

        "timestamp": datetime.now(),

    }


# ============================================================
# SAFE API REQUEST WITH RETRY
# ============================================================

def make_request(
    url: str,
    params: dict,
    timeout: int = 15,
    retries: int = 3,
):

    for attempt in range(retries):

        try:

            response = session.get(
                url,
                params=params,
                timeout=timeout,
            )

            print(
                f"[WEATHER] API status code: "
                f"{response.status_code}"
            )

            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            if response.status_code == 200:

                return response

            # ------------------------------------------------
            # RATE LIMITED
            # ------------------------------------------------

            if response.status_code == 429:

                wait_time = 2 ** attempt

                print(
                    "[WEATHER WARNING] "
                    "Rate limited by weather API. "
                    f"Retrying in {wait_time} seconds..."
                )

                sleep(wait_time)

                continue

            # ------------------------------------------------
            # SERVER ERROR
            # ------------------------------------------------

            if 500 <= response.status_code < 600:

                wait_time = 2 ** attempt

                print(
                    "[WEATHER WARNING] "
                    f"Server error {response.status_code}. "
                    f"Retrying in {wait_time} seconds..."
                )

                sleep(wait_time)

                continue

            response.raise_for_status()

        except requests.RequestException as error:

            print(
                "[WEATHER WARNING] "
                f"Request attempt "
                f"{attempt + 1}/{retries} failed: "
                f"{error}"
            )

            if attempt < retries - 1:

                wait_time = 2 ** attempt

                sleep(wait_time)

            else:

                return None

    print(
        "[WEATHER ERROR] "
        "All API retry attempts failed."
    )

    return None


# ============================================================
# GET COORDINATES
# ============================================================

def get_coordinates(
    city: str,
) -> dict | None:

    city_key = city.strip().lower()

    print(
        f"[WEATHER] Searching coordinates for: {city}"
    )

    # --------------------------------------------------------
    # CHECK CACHE
    # --------------------------------------------------------

    cached_location = get_cached_value(
        cache=_coordinate_cache,
        key=city_key,
        ttl=COORDINATE_CACHE_TTL,
    )

    if cached_location:

        print(
            "[WEATHER CACHE] "
            "Using cached coordinates."
        )

        return cached_location

    # --------------------------------------------------------
    # API REQUEST
    # --------------------------------------------------------

    response = make_request(
        url=GEOCODING_URL,
        params={
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json",
        },
    )

    if not response:

        print(
            "[WEATHER ERROR] "
            "Geocoding request failed."
        )

        return None

    try:

        data = response.json()

        results = data.get("results")

        if not results:

            print(
                f"[WEATHER] "
                f"No coordinates found for city: {city}"
            )

            return None

        result = results[0]

        location = {

            "latitude": result["latitude"],

            "longitude": result["longitude"],

            "name": result.get(
                "name",
                city,
            ),

            "country": result.get(
                "country",
            ),

            "timezone": result.get(
                "timezone",
                "UTC",
            ),

        }

        # ----------------------------------------------------
        # SAVE TO CACHE
        # ----------------------------------------------------

        set_cached_value(
            cache=_coordinate_cache,
            key=city_key,
            value=location,
        )

        print(
            "[WEATHER] Location found:",
            location,
        )

        return location

    except (
        ValueError,
        KeyError,
        TypeError,
    ) as error:

        print(
            "[WEATHER ERROR] "
            f"Invalid geocoding response: {error}"
        )

        return None


# ============================================================
# NORMALIZE TIME REFERENCE
# ============================================================

def normalize_time_reference(
    time_reference: str | None,
) -> str:

    if not time_reference:

        return "now"

    return time_reference.strip().lower()


# ============================================================
# GET TARGET TIME
# ============================================================

def get_target_time(
    time_reference: str | None,
    timezone_name: str = "UTC",
) -> datetime:

    time_reference = normalize_time_reference(
        time_reference
    )

    try:

        timezone = ZoneInfo(
            timezone_name
        )

    except Exception:

        timezone = ZoneInfo(
            "UTC"
        )

    # Get current time in the LOCATION'S timezone.
    now = datetime.now(
        timezone
    ).replace(
        tzinfo=None
    )

    print(
        "[WEATHER] "
        f"Time reference: {time_reference}"
    )

    print(
        "[WEATHER] "
        f"Location timezone: {timezone_name}"
    )

    # --------------------------------------------------------
    # TOMORROW
    # --------------------------------------------------------

    if time_reference == "tomorrow":

        target = now + timedelta(
            days=1
        )

        return target.replace(
            hour=12,
            minute=0,
            second=0,
            microsecond=0,
        )

    # --------------------------------------------------------
    # TODAY
    # --------------------------------------------------------

    if time_reference == "today":

        return now.replace(
            hour=12,
            minute=0,
            second=0,
            microsecond=0,
        )

    # --------------------------------------------------------
    # MORNING
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # AFTERNOON
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # EVENING
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # NIGHT
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # NOW
    # --------------------------------------------------------

    return now


# ============================================================
# FIND CLOSEST FORECAST HOUR
# ============================================================

def find_closest_hour_index(
    hourly_times: list[str],
    target_time: datetime,
) -> int:

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

        range(
            len(parsed_times)
        ),

        key=lambda index: abs(

            parsed_times[index]
            -
            target_time

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


# ============================================================
# GET WEATHER
# ============================================================

def get_weather(

    latitude: float,

    longitude: float,

    time_reference: str = "now",

    timezone_name: str = "UTC",

) -> WeatherData | None:

    # --------------------------------------------------------
    # CREATE CACHE KEY
    # --------------------------------------------------------

    cache_key = (
        f"{latitude}:"
        f"{longitude}:"
        f"{normalize_time_reference(time_reference)}:"
        f"{timezone_name}"
    )

    # --------------------------------------------------------
    # CHECK WEATHER CACHE
    # --------------------------------------------------------

    cached_weather = get_cached_value(

        cache=_weather_cache,

        key=cache_key,

        ttl=WEATHER_CACHE_TTL,

    )

    if cached_weather:

        print(
            "[WEATHER CACHE] "
            "Using cached weather data."
        )

        return cached_weather

    print(
        "[WEATHER] Fetching weather for "
        f"latitude={latitude}, "
        f"longitude={longitude}"
    )

    # --------------------------------------------------------
    # WEATHER API REQUEST
    # --------------------------------------------------------

    response = make_request(

        url=WEATHER_URL,

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

    )

    if not response:

        print(
            "[WEATHER ERROR] "
            "Could not retrieve weather data."
        )

        return None

    try:

        data = response.json()

        hourly = data.get(
            "hourly"
        )

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

        # ----------------------------------------------------
        # TARGET TIME
        # ----------------------------------------------------

        target_time = get_target_time(

            time_reference=time_reference,

            timezone_name=timezone_name,

        )

        index = find_closest_hour_index(

            hourly_times=times,

            target_time=target_time,

        )

        # ----------------------------------------------------
        # VALIDATE REQUIRED FIELDS
        # ----------------------------------------------------

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

                    f"Missing weather field: {field}"

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

        # ----------------------------------------------------
        # CREATE WEATHER MODEL
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # PRINT WEATHER RESULT
        # ----------------------------------------------------

        print(
            "\n========== WEATHER RESULT =========="
        )

        print(
            f"[WEATHER] Time reference: "
            f"{time_reference}"
        )

        print(
            f"[WEATHER] Timezone: "
            f"{timezone_name}"
        )

        print(
            f"[WEATHER] Selected hour: "
            f"{times[index]}"
        )

        print(
            "[WEATHER] Values:"
        )

        print(
            f"Temperature: "
            f"{weather.temperature_2m}"
        )

        print(
            f"Wind speed: "
            f"{weather.wind_speed_10m}"
        )

        print(
            f"Precipitation: "
            f"{weather.precipitation}"
        )

        print(
            f"Precipitation probability: "
            f"{weather.precipitation_probability}"
        )

        print(
            f"UV index: "
            f"{weather.uv_index}"
        )

        print(
            f"Weather code: "
            f"{weather.weather_code}"
        )

        print(
            "====================================\n"
        )

        # ----------------------------------------------------
        # SAVE WEATHER TO CACHE
        # ----------------------------------------------------

        set_cached_value(

            cache=_weather_cache,

            key=cache_key,

            value=weather,

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

        TypeError,

    ) as error:

        print(

            "[WEATHER ERROR] "

            f"Weather processing failed: {error}"

        )

        return None

    except Exception as error:

        print(

            "[WEATHER ERROR] "

            f"Unexpected error: "

            f"{type(error).__name__}: {error}"

        )

        return None


# ============================================================
# COMPLETE WEATHER PIPELINE
# ============================================================

def get_live_weather(

    city: str,

    time_reference: str = "now",

) -> dict | None:

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

    # --------------------------------------------------------
    # STEP 1: GET LOCATION
    # --------------------------------------------------------

    coordinates = get_coordinates(
        city
    )

    if not coordinates:

        print(

            "[WEATHER ERROR] "

            "Could not resolve city coordinates."

        )

        return None

    # --------------------------------------------------------
    # STEP 2: GET WEATHER
    # --------------------------------------------------------

    weather = get_weather(

        latitude=coordinates[
            "latitude"
        ],

        longitude=coordinates[
            "longitude"
        ],

        time_reference=time_reference,

        timezone_name=coordinates.get(
            "timezone",
            "UTC",
        ),

    )

    if not weather:

        print(

            "[WEATHER ERROR] "

            "Could not retrieve weather data."

        )

        return None

    # --------------------------------------------------------
    # STEP 3: RETURN RESULT
    # --------------------------------------------------------

    result = {

        "location": coordinates,

        "weather": weather,

        "time_reference": time_reference,

    }

    print(

        "[WEATHER] "

        "Pipeline completed successfully."

    )

    print(

        "======================================\n"

    )

    return result