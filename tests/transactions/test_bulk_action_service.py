"""BulkTransactionActionService のテスト。"""
import pytest

from transactions.models import Transaction
from transactions.services import BulkTransactionActionService


class Test_BulkTransactionActionService:
    """明細一括操作サービスの検証。"""

    @pytest.mark.django_db
    def test_選択が0件のときwarningを返す(
        self, user_a, user_b, monthly_budget
    ):
        mb = monthly_budget(user_a, user_b)
        result = BulkTransactionActionService().apply(mb, "exclude", [])

        assert result.level == "warning"
        assert result.message == "明細を選択してください"
        assert result.updated_count == 0

    @pytest.mark.django_db
    def test_不正なactionのときerrorを返す(
        self, user_a, user_b, monthly_budget, living_cost_transactions
    ):
        mb = monthly_budget(user_a, user_b)
        txs = living_cost_transactions(mb, [(5000, user_a)])
        result = BulkTransactionActionService().apply(
            mb, "invalid", [str(txs[0].id)]
        )

        assert result.level == "error"
        assert result.message == "不正な操作です"

    @pytest.mark.django_db
    def test_excludeで生活費フラグと支払者がクリアされる(
        self, user_a, user_b, monthly_budget, living_cost_transactions
    ):
        mb = monthly_budget(user_a, user_b)
        txs = living_cost_transactions(mb, [(5000, user_a)])

        result = BulkTransactionActionService().apply(
            mb, "exclude", [str(txs[0].id)]
        )

        assert result.level == "success"
        assert result.updated_count == 1
        assert "生活費から除外しました" in result.message
        txs[0].refresh_from_db()
        assert txs[0].is_living_cost is False
        assert txs[0].payer_id is None
        assert result.updated_transactions is not None
        assert result.updated_transactions[0]["id"] == txs[0].id
        assert result.updated_transactions[0]["payer_username"] is None

    @pytest.mark.django_db
    def test_payer_aで支払者と生活費フラグが設定される(
        self, user_a, user_b, monthly_budget, living_cost_transactions
    ):
        mb = monthly_budget(user_a, user_b)
        txs = living_cost_transactions(mb, [(5000, user_b)])
        Transaction.objects.filter(pk=txs[0].pk).update(
            is_living_cost=False, payer=None
        )

        result = BulkTransactionActionService().apply(
            mb, "payer_a", [str(txs[0].id)]
        )

        assert result.level == "success"
        assert result.updated_count == 1
        assert user_a.username in result.message
        assert "生活費に含め" in result.message
        txs[0].refresh_from_db()
        assert txs[0].payer_id == user_a.id
        assert txs[0].is_living_cost is True

    @pytest.mark.django_db
    def test_payer_aでupdated_transactionsが返る(
        self, user_a, user_b, monthly_budget, living_cost_transactions
    ):
        mb = monthly_budget(user_a, user_b)
        txs = living_cost_transactions(mb, [(5000, None), (3000, user_b)])

        result = BulkTransactionActionService().apply(
            mb, "payer_a", [str(txs[0].id), str(txs[1].id)]
        )

        assert result.updated_transactions is not None
        assert len(result.updated_transactions) == 2
        updated_by_id = {item["id"]: item["payer_username"] for item in result.updated_transactions}
        assert updated_by_id[txs[0].id] == user_a.username
        assert updated_by_id[txs[1].id] == user_a.username
