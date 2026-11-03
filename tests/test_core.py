"""Unit tests for the independently testable LEDD calculation rules."""

import unittest

from ledd_calculator.core import compute_ledd, ingredient_ledd


class IngredientLeddTests(unittest.TestCase):
    """Verify conversion behavior for individual active ingredients."""

    def test_standard_conversion_uses_amount_and_daily_dose(self):
        """Standard factors multiply strength by units taken per day."""
        self.assertEqual(ingredient_ledd("Levodopa", 100, 2.5), 250)

    def test_safinamide_is_fixed_for_both_market_strengths(self):
        """Safinamide contributes 100 mg regardless of tablet strength."""
        self.assertEqual(ingredient_ledd("Safinamide", 50, 1), 100)
        self.assertEqual(ingredient_ledd("Safinamide", 100, 1), 100)

    def test_unknown_ingredient_is_not_counted(self):
        """Adjunct ingredients without a conversion factor contribute zero."""
        self.assertEqual(ingredient_ledd("Carbidopa", 25, 3), 0)


class ComputeLeddTests(unittest.TestCase):
    """Verify aggregation across products, schedules, and categories."""

    def test_example_calculation_and_categories(self):
        """Multiple products should produce the expected total and breakdown."""
        # Carbidopa is deliberately present to confirm that adjunct ingredients
        # do not alter the result.
        medication_data = {
            "Levodopa 100": {"Levodopa": 100, "Carbidopa": 25},
            "Rasagiline 1": {"Rasagiline": 1},
        }
        medications = [
            ("Levodopa 100", "1-0.5-1-0"),
            ("Rasagiline 1", "1-0-0-0"),
        ]

        total, categories, breakdown = compute_ledd(medications, medication_data)

        # 250 mg levodopa plus 100 mg rasagiline equals 350 mg total LEDD.
        self.assertEqual(total, 350)
        self.assertEqual(categories, {"L-Dopa", "MAO-B inhibitors"})
        self.assertEqual(breakdown, {"L-Dopa": 250, "MAO-B inhibitors": 100})

    def test_schedule_requires_four_values(self):
        """Malformed schedules should fail instead of being silently accepted."""
        with self.assertRaisesRegex(ValueError, "four values"):
            compute_ledd([("Example", "1-0")], {"Example": {"Levodopa": 100}})


if __name__ == "__main__":
    unittest.main()
