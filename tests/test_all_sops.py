from backend.models import WeatherData, UserContext
from backend.loader import load_sops
from backend.nodes.matcher import (
    find_matching_sops,
    select_best_sop,
)


# Load all SOPs
sops = load_sops()


# ------------------------------------------------------------
# DEFAULT SAFE WEATHER
# ------------------------------------------------------------

SAFE_WEATHER = {
    "temperature_2m": 25.0,
    "wind_speed_10m": 5.0,
    "precipitation": 0.0,
    "precipitation_probability": 10.0,
    "uv_index": 2.0,
    "weather_code": 0,
}


def run_test(
    test_name: str,
    expected_sop: str,
    activity: str | None,
    vulnerable_group: str | None,
    raw_message: str,
    weather_overrides: dict,
):
    print("\n" + "=" * 70)
    print(f"TEST: {test_name}")
    print(f"Expected SOP: {expected_sop}")

    # Create controlled weather
    weather_values = SAFE_WEATHER.copy()
    weather_values.update(weather_overrides)

    weather = WeatherData(**weather_values)

    # Create user context
    context = UserContext(
        activity=activity,
        location="Test City",
        time_reference="today",
        vulnerable_group=vulnerable_group,
        raw_message=raw_message,
    )

    # Find matching SOPs
    matches = find_matching_sops(
        context=context,
        weather=weather,
        sops=sops,
    )

    # Select best SOP
    selected = select_best_sop(matches)

    print(f"Activity: {activity}")
    print(f"Vulnerable Group: {vulnerable_group}")
    print(f"Message: {raw_message}")

    print("\nWeather:")
    print(weather)

    print("\nMatched SOPs:")

    if matches:
        for sop in matches:
            print(
                f"- {sop.id} | "
                f"severity={sop.severity} | "
                f"priority={sop.priority}"
            )
    else:
        print("No SOP matched.")

    print("\nSelected SOP:")

    if selected:
        print(selected.id)
    else:
        print("None")

    # Result
    if selected and selected.id == expected_sop:
        print("\nRESULT: PASS")
    else:
        print("\nRESULT: FAIL")


# ============================================================
# WX-001 — Severe Rainfall Override
# ============================================================

run_test(
    test_name="WX-001 Severe Rainfall Override",
    expected_sop="WX-001",
    activity="cycling",
    vulnerable_group=None,
    raw_message="Is it safe to go cycling outside today?",
    weather_overrides={
        "precipitation": 10.0,
    },
)


# ============================================================
# EX-001 — Extreme Heat
# ============================================================

run_test(
    test_name="EX-001 Extreme Heat Exercise",
    expected_sop="EX-001",
    activity="running",
    vulnerable_group=None,
    raw_message="Is it safe to go running today?",
    weather_overrides={
        "temperature_2m": 40.0,
    },
)


# ============================================================
# EX-002 — High UV
# ============================================================

run_test(
    test_name="EX-002 High UV Exposure",
    expected_sop="EX-002",
    activity="cycling",
    vulnerable_group=None,
    raw_message="Can I go cycling outside today?",
    weather_overrides={
        "uv_index": 8.0,
    },
)


# ============================================================
# EX-003 — Strong Wind Cycling
# ============================================================

run_test(
    test_name="EX-003 Strong Wind Cycling",
    expected_sop="EX-003",
    activity="cycling",
    vulnerable_group=None,
    raw_message="Can I go cycling today?",
    weather_overrides={
        "wind_speed_10m": 40.0,
    },
)


# ============================================================
# EX-004 — Rain During Exercise
# ============================================================

run_test(
    test_name="EX-004 Rain During Exercise",
    expected_sop="EX-004",
    activity="running",
    vulnerable_group=None,
    raw_message="Can I go running outside today?",
    weather_overrides={
        "precipitation": 2.0,
    },
)


# ============================================================
# TR-001 — High Rain Probability During Travel
# ============================================================

run_test(
    test_name="TR-001 Rain Risk During Travel",
    expected_sop="TR-001",
    activity="travel",
    vulnerable_group=None,
    raw_message="Is it safe to travel today?",
    weather_overrides={
        "precipitation_probability": 70.0,
    },
)


# ============================================================
# TR-002 — Strong Wind During Travel
# ============================================================

run_test(
    test_name="TR-002 Strong Wind During Travel",
    expected_sop="TR-002",
    activity="motorcycle",
    vulnerable_group=None,
    raw_message="Can I travel by motorcycle today?",
    weather_overrides={
        "wind_speed_10m": 50.0,
    },
)


# ============================================================
# TR-003 — Picnic During Rain
# ============================================================

run_test(
    test_name="TR-003 Picnic During Rain",
    expected_sop="TR-003",
    activity="picnic",
    vulnerable_group=None,
    raw_message="Is today good for a picnic?",
    weather_overrides={
        "precipitation": 1.0,
    },
)


# ============================================================
# TR-004 — Outdoor Event Strong Wind
# ============================================================

run_test(
    test_name="TR-004 Outdoor Event Strong Wind",
    expected_sop="TR-004",
    activity="event",
    vulnerable_group=None,
    raw_message="Is it safe to attend an outdoor event?",
    weather_overrides={
        "wind_speed_10m": 35.0,
    },
)


# ============================================================
# VG-001 — Child in Extreme Heat
# ============================================================

run_test(
    test_name="VG-001 Child in Extreme Heat",
    expected_sop="VG-001",
    activity="walking",
    vulnerable_group="child",
    raw_message="Can my child go outside today?",
    weather_overrides={
        "temperature_2m": 38.0,
    },
)


# ============================================================
# VG-002 — Elderly Person in Extreme Heat
# ============================================================

run_test(
    test_name="VG-002 Elderly Person in Extreme Heat",
    expected_sop="VG-002",
    activity="walking",
    vulnerable_group="elderly",
    raw_message="Can my grandmother go outside today?",
    weather_overrides={
        "temperature_2m": 38.0,
    },
)


# ============================================================
# VG-003 — Pet in Extreme Heat
# ============================================================

run_test(
    test_name="VG-003 Pet in Extreme Heat",
    expected_sop="VG-003",
    activity="walking",
    vulnerable_group="pet",
    raw_message="Is it okay to take my dog for a walk today?",
    weather_overrides={
        "temperature_2m": 35.0,
    },
)


# ============================================================
# VG-004 — Vulnerable Group in Heavy Rain
# ============================================================

run_test(
    test_name="VG-004 Vulnerable Group in Heavy Rain",
    expected_sop="VG-004",
    activity="walking",
    vulnerable_group="elderly",
    raw_message="Can my elderly grandmother go outside today?",
    weather_overrides={
        "precipitation": 5.0,
    },
)