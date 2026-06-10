"""TransactionEditForm のテスト。"""
import pytest

from transactions.forms import TransactionEditForm
from transactions.models import Transaction


class Test_TransactionEditForm:
    """明細編集フォームの検証。"""

    @pytest.mark.django_db
    def test_支払者を設定すると生活費フラグがTrueになる(
        self, user_a, user_b, monthly_budget, living_cost_transactions
    ):
        # Arrange
        mb = monthly_budget(user_a, user_b)
        txs = living_cost_transactions(mb, [(5000, None)])
        Transaction.objects.filter(pk=txs[0].pk).update(
            is_living_cost=False, payer=None
        )
        tx = txs[0]

        # Act
        form = TransactionEditForm(
            data={"payer": user_a.id, "category": "", "memo": ""},
            instance=tx,
            monthly_budget=mb,
        )
        assert form.is_valid()
        saved = form.save()

        # Assert
        saved.refresh_from_db()
        assert saved.payer_id == user_a.id
        assert saved.is_living_cost is True

    @pytest.mark.django_db
    def test_支払者を空にすると生活費フラグがFalseになる(
        self, user_a, user_b, monthly_budget, living_cost_transactions
    ):
        # Arrange
        mb = monthly_budget(user_a, user_b)
        txs = living_cost_transactions(mb, [(5000, user_a)])
        tx = txs[0]

        # Act
        form = TransactionEditForm(
            data={"payer": "", "category": "", "memo": ""},
            instance=tx,
            monthly_budget=mb,
        )
        assert form.is_valid()
        saved = form.save()

        # Assert
        saved.refresh_from_db()
        assert saved.payer_id is None
        assert saved.is_living_cost is False
