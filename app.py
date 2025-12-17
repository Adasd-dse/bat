import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

from analysis import (
    ForecastResult,
    ProfitRow,
    ScenarioAdjustments,
    analyze_financials,
    evaluate_scenario,
    forecast_profits,
    load_financials,
    summarize_financials,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Aplicatie pentru analiza si prognoza a activitatilor economice ale "
            "unei companii de printare 3D, cu scopul de a maximiza profitul."
        )
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Calea catre fisierul CSV cu date financiare (luna,revenue,variable_costs,fixed_costs,print_volume)",
    )
    parser.add_argument(
        "--forecast-months",
        type=int,
        default=3,
        help="Numarul de luni pe care sa se faca prognoza profitului (default: 3)",
    )
    parser.add_argument(
        "--price-adjust",
        type=float,
        default=0.0,
        help="Ajustare procentuala a veniturilor (ex: 0.05 pentru +5% fata de datele istorice)",
    )
    parser.add_argument(
        "--variable-cost-adjust",
        type=float,
        default=0.0,
        help="Ajustare procentuala a costurilor variabile (ex: -0.03 pentru reducere de 3%)",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        help="Daca este setat, salveaza sumarul si prognoza in fisier JSON pentru raportare.",
    )
    return parser


def format_currency(value: float) -> str:
    return f"{value:,.2f}".replace(",", " ")


def print_analysis(
    rows: List[ProfitRow],
    summary: Dict[str, float],
    forecast: ForecastResult,
    adjustments: ScenarioAdjustments,
) -> None:
    print("\n== Rezultate curente ==")
    for row in rows:
        print(
            f"{row['month']:<10} Venituri: {format_currency(row['revenue'])} | "
            f"Costuri variabile: {format_currency(row['variable_costs'])} | "
            f"Costuri fixe: {format_currency(row['fixed_costs'])} | "
            f"Profit: {format_currency(row['profit'])} | Marja: {row['profit_margin']*100:.1f}%"
        )

    print("\n== Sumar ==")
    print(f"Profit total: {format_currency(summary['total_profit'])}")
    print(f"Profit mediu: {format_currency(summary['average_profit'])}")
    print(f"Marja medie: {summary['average_margin']*100:.2f}%")
    print(f"Crestere profit lunara (estimata): {summary['profit_trend']*100:.2f}%")

    print("\n== Prognoza profit ==")
    for month, profit in forecast.projected_profits:
        print(f"{month:<10} Profit prognozat: {format_currency(profit)}")
    print(f"Profit prognozat mediu: {format_currency(forecast.average_projected_profit)}")

    print("\n== Scenariu ajustat ==")
    print(
        f"Ajustare pret: {adjustments.price_adjust*100:.1f}% | "
        f"Ajustare costuri variabile: {adjustments.variable_cost_adjust*100:.1f}%"
    )
    print(f"Profit ajustat (mediu): {format_currency(adjustments.adjusted_average_profit)}")
    print(f"Punct de break-even estimat: {format_currency(adjustments.break_even_revenue)}")



def save_json(
    path: Path,
    rows: List[ProfitRow],
    summary: Dict[str, float],
    forecast: ForecastResult,
    adjustments: ScenarioAdjustments,
) -> None:
    payload = {
        "rows": rows,
        "summary": summary,
        "forecast": {
            "projected_profits": forecast.projected_profits,
            "average_projected_profit": forecast.average_projected_profit,
            "slope": forecast.slope,
        },
        "scenario": adjustments._asdict(),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    print(f"Raport salvat in {path}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    data = load_financials(args.file)
    rows = analyze_financials(data)
    summary = summarize_financials(rows)
    forecast = forecast_profits(rows, args.forecast_months)
    scenario = ScenarioAdjustments(
        price_adjust=args.price_adjust,
        variable_cost_adjust=args.variable_cost_adjust,
        adjusted_average_profit=0.0,
        break_even_revenue=0.0,
    )
    scenario = evaluate_scenario(rows, scenario)

    print_analysis(rows, summary, forecast, scenario)

    if args.output_json:
        save_json(args.output_json, rows, summary, forecast, scenario)


if __name__ == "__main__":
    main()
