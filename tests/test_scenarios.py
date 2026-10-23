import importlib.util
import unittest
from pathlib import Path

SCENARIOS_PATH = (
    Path(__file__).parents[1] / "custom_components" / "comfoclime" / "scenarios.py"
)
SCENARIOS_SPEC = importlib.util.spec_from_file_location(
    "comfoclime_scenarios", SCENARIOS_PATH
)
SCENARIOS_MODULE = importlib.util.module_from_spec(SCENARIOS_SPEC)
SCENARIOS_SPEC.loader.exec_module(SCENARIOS_MODULE)


class ScenarioTests(unittest.TestCase):
    def test_scenario_confirmation_helper_exists(self):
        self.assertTrue(
            SCENARIOS_MODULE.scenario_update_confirmed(
                4, {"scenario": 4, "scenarioTimeLeft": 10}
            ),
        )

    def test_scenario_confirmation_rejects_ignored_or_expired_update(self):
        self.assertFalse(
            SCENARIOS_MODULE.scenario_update_confirmed(
                7, {"scenario": 5, "scenarioTimeLeft": 300}
            )
        )
        self.assertFalse(
            SCENARIOS_MODULE.scenario_update_confirmed(
                7, {"scenario": 7, "scenarioTimeLeft": 0}
            )
        )


if __name__ == "__main__":
    unittest.main()
