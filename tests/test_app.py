"""End-to-end smoke test for the Streamlit interface."""

import unittest
from pathlib import Path

from streamlit.testing.v1 import AppTest


def button_with_label(app: AppTest, label: str):
    """Find a rendered Streamlit button by its user-facing label."""
    return next(button for button in app.button if button.label == label)


class AppSmokeTests(unittest.TestCase):
    """Exercise the primary workflow through Streamlit's test harness."""

    def test_calculation_and_exports_render_without_errors(self):
        """A known medication should calculate and render without UI errors."""
        app_path = Path(__file__).resolve().parents[1] / "app.py"

        # Launch the UI and verify its essential initial controls.
        app = AppTest.from_file(app_path).run(timeout=20)
        self.assertFalse(app.exception)
        self.assertEqual(app.selectbox[0].options, ["Switzerland"])
        self.assertTrue(
            any(button.label == "Exit Calculator" for button in app.button)
        )

        # Simulate adding one morning dose and requesting the calculation.
        app.selectbox[1].select("Madopar 125 mg").run(timeout=20)
        app.number_input(key="schedule_Morning").set_value(1.0)
        button_with_label(app, "Add Medication to List").click().run(timeout=20)
        button_with_label(app, "Compute LEDD").click().run(timeout=20)

        # The known 100 mg levodopa dose is a compact regression check for both
        # the UI-to-core handoff and the rendered result.
        self.assertFalse(app.exception)
        self.assertTrue(
            any("Total LEDD: **100.00 mg**" in item.value for item in app.success)
        )


if __name__ == "__main__":
    unittest.main()
