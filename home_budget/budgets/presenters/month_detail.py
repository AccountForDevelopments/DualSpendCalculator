from django.http import QueryDict

from csv_import.presenters import build_csv_upload_section_context
from transactions.presenters import build_transaction_list_section_context

from ..models import MonthlyBudget


def build_month_detail_section_context(
    monthly_budget: MonthlyBudget,
    query_params: QueryDict,
) -> dict[str, object]:
    """月次詳細画面の横断セクション（CSV・明細）用 context を組み立てる。"""
    context: dict[str, object] = {}
    context.update(build_csv_upload_section_context())
    if monthly_budget.transaction_count > 0:
        context.update(
            build_transaction_list_section_context(monthly_budget, query_params)
        )
    return context
