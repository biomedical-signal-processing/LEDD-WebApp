"""Pure calculation rules for Levodopa Equivalent Daily Dose (LEDD).

This module deliberately has no Streamlit dependency. Conversion rules can
therefore be reviewed and tested without launching the user interface.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence


# Multipliers are based on the publication cited in the application footer.
# Safinamide is handled separately because its contribution is fixed per day.
LEDD_CONVERSIONS = {
    "Levodopa": 1,
    "Levodopa CR": 0.75,
    "Levodopa ER": 0.5,
    "Duodopa": 1.11,
    "Entacapone": 0.33,
    "Tolcapone": 0.5,
    "Opicapone": 0.5,
    "Selegiline oral": 10,
    "Selegiline sublingual": 80,
    "Rasagiline": 100,
    "Apomorphine": 10,
    "Piribedil": 1,
    "Pramipexole": 100,
    "Ropinirole": 20,
    "Rotigotine": 30,
    "Amantadine": 1,
}

# The order here defines the four positions in strings such as ``1-0-1-0``.
SCHEDULE_TIMES = ["Morning", "Noon", "Evening", "Night"]

# Categories drive both the UI ingredient display and the result breakdown.
CATEGORIES = {
    "L-Dopa": ["Levodopa", "Levodopa CR", "Levodopa ER", "Duodopa"],
    "COMT inhibitors": ["Entacapone", "Opicapone", "Tolcapone"],
    "MAO-B inhibitors": [
        "Selegiline oral",
        "Selegiline sublingual",
        "Rasagiline",
        "Safinamide",
    ],
    "Dopamine Agonists": [
        "Rotigotine",
        "Ropinirole",
        "Pramipexole",
        "Piribedil",
        "Apomorphine",
    ],
    "Other": ["Amantadine"],
}


def get_category(ingredient: str) -> str:
    """Return the reporting category for an active ingredient."""
    for category, ingredients in CATEGORIES.items():
        if ingredient in ingredients:
            return category
    return "Unknown"


def ingredient_ledd(ingredient: str, amount_mg: float, daily_dose: float) -> float:
    """Calculate LEDD for one ingredient.

    Safinamide contributes a fixed 100 mg LEDD when taken, independently of the
    marketed 50 mg or 100 mg strength, as documented by the calculator's source.
    """
    if ingredient == "Safinamide":
        return 100.0 if daily_dose > 0 else 0.0

    # Ingredients without a conversion factor are adjuncts (for example,
    # carbidopa) and intentionally contribute zero to the LEDD result.
    factor = LEDD_CONVERSIONS.get(ingredient)
    return daily_dose * amount_mg * factor if factor is not None else 0.0


def compute_ledd(
    medication_list: Sequence[tuple[str, str]],
    medication_data: Mapping[str, Mapping[str, float]],
) -> tuple[float, set[str], dict[str, float]]:
    """Calculate total and per-category LEDD for selected medications.

    Args:
        medication_list: ``(product name, schedule)`` pairs. A schedule contains
            four hyphen-separated unit counts in ``SCHEDULE_TIMES`` order.
        medication_data: Product names mapped to ingredient strengths in mg.

    Returns:
        The total LEDD, the set of contributing categories, and a category-to-
        LEDD mapping.

    Raises:
        ValueError: If a schedule does not contain exactly four values.
    """
    total_ledd = 0.0
    used_categories: set[str] = set()
    category_ledd: defaultdict[str, float] = defaultdict(float)

    for name, schedule in medication_list:
        # Sum all four administrations to obtain units taken per day.
        schedule_counts = [float(value) for value in schedule.split("-")]
        if len(schedule_counts) != len(SCHEDULE_TIMES):
            raise ValueError("A medication schedule must contain four values.")
        daily_dose = sum(schedule_counts)
        # Calculate each active ingredient independently because combination
        # products may contain both contributing and non-contributing compounds.
        for ingredient, amount_mg in medication_data.get(name, {}).items():
            ledd = ingredient_ledd(ingredient, amount_mg, daily_dose)
            if ledd == 0:
                continue
            total_ledd += ledd
            category = get_category(ingredient)
            category_ledd[category] += ledd
            used_categories.add(category)

    # Expose a regular dict rather than leaking the internal defaultdict API.
    return total_ledd, used_categories, dict(category_ledd)
