from collections.abc import Iterable
from dataclasses import dataclass

from budgets.domain.ratios import calculate_ratios, format_ratio_percent
from budgets.models import MonthlyBudget

from .income_ratio import _to_income_int


@dataclass(frozen=True)
class MonthListRow:
    """月次一覧の1行分の表示データ。"""

    monthly_budget: MonthlyBudget
    ratio_a_percent: str
    ratio_b_percent: str


def build_month_list_rows(months: Iterable[MonthlyBudget]) -> list[MonthListRow]:
    """月次一覧画面の行データを組み立てる。"""
    rows: list[MonthListRow] = []
    for monthly_budget in months:
        income_a = _to_income_int(monthly_budget.income_a)
        income_b = _to_income_int(monthly_budget.income_b)
        ratio_a, ratio_b = calculate_ratios(income_a, income_b)
        rows.append(
            MonthListRow(
                monthly_budget=monthly_budget,
                ratio_a_percent=format_ratio_percent(ratio_a),
                ratio_b_percent=format_ratio_percent(ratio_b),
            )
        )
    return rows
