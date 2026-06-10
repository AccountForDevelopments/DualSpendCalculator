"""build_transaction_list_section_context のテスト。"""
import pytest
from django.http import QueryDict

from transactions.models import Transaction
from transactions.presenters import build_transaction_list_section_context
from transactions.presenters.transaction_list_section import PAGE_SIZE


class Test_build_transaction_list_section_context:
    """明細一覧セクション Presenter の検証。"""

    @pytest.mark.django_db
    def test_明細なしのとき空の一覧と1ページ目を返す(
        self, user_a, user_b, monthly_budget
    ):
        mb = monthly_budget(user_a, user_b)
        context = build_transaction_list_section_context(mb, QueryDict())

        assert len(context["transactions"]) == 0
        assert context["page_obj"].number == 1
        assert context["page_obj"].paginator.count == 0
        assert "filter_form" in context
        assert context["filter_params"] == ""

    @pytest.mark.django_db
    def test_is_living_cost_trueで生活費対象のみ返る(
        self, user_a, user_b, monthly_budget, living_cost_transactions
    ):
        mb = monthly_budget(user_a, user_b)
        living_cost_transactions(mb, [(5000, user_a)])
        tx = living_cost_transactions(mb, [(3000, user_b)])[0]
        Transaction.objects.filter(pk=tx.pk).update(is_living_cost=False)

        context = build_transaction_list_section_context(
            mb,
            QueryDict("is_living_cost=true"),
        )

        assert len(context["transactions"]) == 1
        assert context["transactions"][0].is_living_cost is True

    @pytest.mark.django_db
    def test_page2で2ページ目のobject_listを返す(
        self, user_a, user_b, monthly_budget, living_cost_transactions
    ):
        mb = monthly_budget(user_a, user_b)
        amounts = [(1000 + i, user_a) for i in range(PAGE_SIZE + 1)]
        living_cost_transactions(mb, amounts)

        context = build_transaction_list_section_context(
            mb,
            QueryDict("page=2"),
        )

        assert context["page_obj"].number == 2
        assert len(context["transactions"]) == 1

    @pytest.mark.django_db
    def test_filter_paramsにpageキーが含まれない(
        self, user_a, user_b, monthly_budget, living_cost_transactions
    ):
        mb = monthly_budget(user_a, user_b)
        living_cost_transactions(mb, [(5000, user_a)])

        context = build_transaction_list_section_context(
            mb,
            QueryDict("page=1&is_living_cost=true&category=food"),
        )

        assert "page=" not in context["filter_params"]
        assert "is_living_cost=true" in context["filter_params"]
        assert "category=food" in context["filter_params"]
