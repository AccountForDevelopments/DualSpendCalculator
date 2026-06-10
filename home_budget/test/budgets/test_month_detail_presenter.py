"""build_month_detail_section_context のテスト。"""
import pytest
from django.http import QueryDict

from budgets.presenters import build_month_detail_section_context
from csv_import.forms import CSVUploadForm


class Test_build_month_detail_section_context:
    """月次詳細 Facade Presenter の検証。"""

    @pytest.mark.django_db
    def test_明細0件のときcsv_formのみを返す(
        self, user_a, user_b, monthly_budget
    ):
        mb = monthly_budget(user_a, user_b)
        context = build_month_detail_section_context(mb, QueryDict())

        assert "csv_form" in context
        assert isinstance(context["csv_form"], CSVUploadForm)
        assert "filter_form" not in context
        assert "transactions" not in context
        assert "page_obj" not in context
        assert "filter_params" not in context

    @pytest.mark.django_db
    def test_明細ありのときcsv_formと明細系4キーを返す(
        self, user_a, user_b, monthly_budget, living_cost_transactions
    ):
        mb = monthly_budget(user_a, user_b)
        living_cost_transactions(mb, [(5000, user_a)])

        context = build_month_detail_section_context(mb, QueryDict())

        assert "csv_form" in context
        assert "filter_form" in context
        assert "transactions" in context
        assert "page_obj" in context
        assert "filter_params" in context
        assert len(context["transactions"]) == 1
