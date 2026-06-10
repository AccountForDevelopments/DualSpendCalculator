"""AgreementRequestValidator のテスト。"""
import pytest

from budgets.services import AgreementRequestValidator


class Test_AgreementRequestValidator:
    """同意書リクエスト検証の検証。"""

    @pytest.mark.django_db
    def test_transaction_idsが空のとき失敗する(
        self, user_a, user_b, monthly_budget
    ):
        mb = monthly_budget(user_a, user_b)
        result = AgreementRequestValidator().validate([], str(mb.id))

        assert result.ok is False
        assert result.message == "選択された請求がありません"
        assert result.redirect_url_name == "budgets:month_list"

    @pytest.mark.django_db
    def test_存在しないTransaction_IDを含むとき失敗する(
        self, user_a, user_b, monthly_budget, living_cost_transactions
    ):
        mb = monthly_budget(user_a, user_b)
        txs = living_cost_transactions(mb, [(5000, user_a)])
        result = AgreementRequestValidator().validate(
            [str(txs[0].id), "99999"], str(mb.id)
        )

        assert result.ok is False
        assert "存在しない請求が含まれています" in result.message
        assert result.redirect_url_name == "budgets:month_detail"
        assert result.redirect_pk == mb.id

    @pytest.mark.django_db
    def test_他月のTransaction_IDを含むとき失敗する(
        self, user_a, user_b, monthly_budget, living_cost_transactions
    ):
        mb1 = monthly_budget(user_a, user_b, year_month="2026-03")
        mb2 = monthly_budget(user_a, user_b, year_month="2026-04")
        txs1 = living_cost_transactions(mb1, [(5000, user_a)])
        txs2 = living_cost_transactions(mb2, [(8000, user_a)])

        result = AgreementRequestValidator().validate(
            [str(txs1[0].id), str(txs2[0].id)], str(mb1.id)
        )

        assert result.ok is False
        assert result.message == "異なる対象月の請求が含まれています"
        assert result.redirect_url_name == "budgets:month_detail"
        assert result.redirect_pk == mb1.id

    @pytest.mark.django_db
    def test_正常なリクエストのとき成功する(
        self, user_a, user_b, monthly_budget, living_cost_transactions
    ):
        mb = monthly_budget(user_a, user_b)
        txs = living_cost_transactions(mb, [(5000, user_a), (8000, user_a)])
        ids = [str(t.id) for t in txs]

        result = AgreementRequestValidator().validate(ids, str(mb.id))

        assert result.ok is True
        assert result.monthly_budget == mb
        assert result.transaction_ids == [t.id for t in txs]
