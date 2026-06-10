from django.core.paginator import Paginator
from django.http import QueryDict

from budgets.models import MonthlyBudget

from ..forms import TransactionFilterForm
from ..models import Transaction

PAGE_SIZE = 50


def build_transaction_list_section_context(
    monthly_budget: MonthlyBudget,
    query_params: QueryDict,
) -> dict[str, object]:
    """月次詳細画面の明細一覧セクション用 context を組み立てる。"""
    filter_form = TransactionFilterForm(
        query_params,
        monthly_budget=monthly_budget,
    )
    queryset = Transaction.objects.for_monthly_budget(monthly_budget)
    if filter_form.is_valid():
        queryset = queryset.by_month_detail_filters(filter_form.cleaned_data)

    paginator = Paginator(queryset, PAGE_SIZE)
    page_obj = paginator.get_page(query_params.get("page"))

    params = query_params.copy()
    if "page" in params:
        del params["page"]

    return {
        "filter_form": filter_form,
        "transactions": page_obj.object_list,
        "page_obj": page_obj,
        "filter_params": params.urlencode(),
    }
