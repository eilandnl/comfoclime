"""Supported ComfoClime dashboard scenarios."""

SCENARIO_VALUES = {
    "cooking": 4,
    "party": 5,
    "holiday": 7,
    "scenario_boost": 8,
}

SCENARIO_DEFAULT_DURATIONS_MINUTES = {
    "cooking": 30,
    "party": 30,
    "holiday": 24 * 60,
    "scenario_boost": 30,
}


def scenario_update_confirmed(expected_scenario, dashboard):
    """Return whether the dashboard confirms the requested active scenario."""
    if dashboard is None or dashboard.get("scenario") != expected_scenario:
        return False

    remaining = dashboard.get("scenarioTimeLeft")
    return (
        isinstance(remaining, (int, float))
        and not isinstance(remaining, bool)
        and remaining > 0
    )
