import csv
from collections import namedtuple
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

ProfitRow = Dict[str, float]
ForecastResult = namedtuple(
    "ForecastResult", ["projected_profits", "average_projected_profit", "slope"]
)
ScenarioAdjustments = namedtuple(
    "ScenarioAdjustments",
    ["price_adjust", "variable_cost_adjust", "adjusted_average_profit", "break_even_revenue"],
)


MONTH_LABELS = [
    "Ianuarie",
    "Februarie",
    "Martie",
    "Aprilie",
    "Mai",
    "Iunie",
    "Iulie",
    "August",
    "Septembrie",
    "Octombrie",
    "Noiembrie",
    "Decembrie",
]


def load_financials(path: Path) -> List[Dict[str, float]]:
    """Incarca date financiare din CSV.

    CSV trebuie sa contina headerul: month,revenue,variable_costs,fixed_costs,print_volume
    """
    rows: List[Dict[str, float]] = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"month", "revenue", "variable_costs", "fixed_costs", "print_volume"}
        if set(reader.fieldnames or []) != required:
            missing = required - set(reader.fieldnames or [])
            raise ValueError(
                f"CSV invalid. Lipsesc coloanele: {', '.join(sorted(missing))}."
            )
        for raw in reader:
            rows.append(
                {
                    "month": raw["month"],
                    "revenue": float(raw["revenue"]),
                    "variable_costs": float(raw["variable_costs"]),
                    "fixed_costs": float(raw["fixed_costs"]),
                    "print_volume": float(raw["print_volume"]),
                }
            )
    return rows


def analyze_financials(data: Iterable[Dict[str, float]]) -> List[ProfitRow]:
    rows: List[ProfitRow] = []
    for entry in data:
        profit = entry["revenue"] - entry["variable_costs"] - entry["fixed_costs"]
        margin = profit / entry["revenue"] if entry["revenue"] else 0.0
        rows.append({**entry, "profit": profit, "profit_margin": margin})
    return rows


def _linear_regression(points: List[Tuple[float, float]]) -> Tuple[float, float]:
    """Calculeaza panta si intersectia pentru regresie liniara simpli."""
    n = len(points)
    if n == 0:
        return 0.0, 0.0
    sum_x = sum(p[0] for p in points)
    sum_y = sum(p[1] for p in points)
    sum_xy = sum(p[0] * p[1] for p in points)
    sum_x2 = sum(p[0] ** 2 for p in points)

    denominator = n * sum_x2 - sum_x ** 2
    if denominator == 0:
        return 0.0, sum_y / n if n else 0.0
    slope = (n * sum_xy - sum_x * sum_y) / denominator
    intercept = (sum_y - slope * sum_x) / n
    return slope, intercept


def forecast_profits(rows: List[ProfitRow], months: int) -> ForecastResult:
    profits = [row["profit"] for row in rows]
    points = list(enumerate(profits))
    slope, intercept = _linear_regression(points)

    projected: List[Tuple[str, float]] = []
    start_index = len(profits)
    for i in range(months):
        idx = start_index + i
        month_label = MONTH_LABELS[idx % 12] + f" {2024 + idx // 12}"
        predicted = intercept + slope * idx
        projected.append((month_label, max(predicted, 0.0)))

    average_future_profit = sum(p for _, p in projected) / months if months else 0.0
    return ForecastResult(projected, average_future_profit, slope)


def _trend_percentage(profits: List[float]) -> float:
    if len(profits) < 2:
        return 0.0
    initial, final = profits[0], profits[-1]
    if initial == 0:
        return 0.0
    return (final - initial) / abs(initial)


def summarize_financials(rows: List[ProfitRow]) -> Dict[str, float]:
    profits = [row["profit"] for row in rows]
    total_profit = sum(profits)
    average_profit = total_profit / len(profits) if profits else 0.0
    average_margin = (
        sum(row["profit_margin"] for row in rows) / len(rows) if rows else 0.0
    )
    trend = _trend_percentage(profits)

    return {
        "total_profit": total_profit,
        "average_profit": average_profit,
        "average_margin": average_margin,
        "profit_trend": trend,
    }


def evaluate_scenario(
    rows: List[ProfitRow], adjustments: ScenarioAdjustments
) -> ScenarioAdjustments:
    adjusted_revenue = [row["revenue"] * (1 + adjustments.price_adjust) for row in rows]
    adjusted_variable = [
        row["variable_costs"] * (1 + adjustments.variable_cost_adjust) for row in rows
    ]
    adjusted_profits = [
        r - v - row["fixed_costs"]
        for r, v, row in zip(adjusted_revenue, adjusted_variable, rows)
    ]
    contribution_margins = [
        (r - v) / row["print_volume"] if row["print_volume"] else 0.0
        for r, v, row in zip(adjusted_revenue, adjusted_variable, rows)
    ]
    avg_contribution = (
        sum(contribution_margins) / len(contribution_margins) if contribution_margins else 0.0
    )
    avg_fixed = sum(row["fixed_costs"] for row in rows) / len(rows) if rows else 0.0
    break_even_revenue = avg_fixed / avg_contribution if avg_contribution else 0.0

    average_profit = sum(adjusted_profits) / len(adjusted_profits) if adjusted_profits else 0.0

    return adjustments._replace(
        adjusted_average_profit=average_profit,
        break_even_revenue=break_even_revenue,
    )
