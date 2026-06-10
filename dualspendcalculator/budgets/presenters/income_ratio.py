from budgets.domain.ratios import calculate_ratios, format_ratio_percent
from budgets.models import MonthlyBudget


def _to_income_int(value) -> int | None:
    """DecimalField の収入値を calculate_ratios 用の int に変換する。"""
    if value is None:
        return None
    return int(value)


def build_income_ratio_context(monthly_budget: MonthlyBudget) -> dict[str, str]:
    """月次詳細画面の負担割合表示用 context を組み立てる。"""
    income_a = _to_income_int(monthly_budget.income_a)
    income_b = _to_income_int(monthly_budget.income_b)
    ratio_a, ratio_b = calculate_ratios(income_a, income_b)
    return {
        "ratio_a_percent": format_ratio_percent(ratio_a),
        "ratio_b_percent": format_ratio_percent(ratio_b),
    }
