"""BulkActionView のテスト。"""
import pytest
from django.contrib.messages import get_messages
from django.test import Client
from django.urls import reverse


class Test_BulkActionView:
    """一括操作ビューの検証。"""

    @pytest.mark.django_db
    def test_Ajaxでpayer_aのときJSONが返る(
        self, user_a, user_b, monthly_budget, living_cost_transactions
    ):
        # Arrange
        mb = monthly_budget(user_a, user_b)
        txs = living_cost_transactions(mb, [(5000, None)])
        client = Client()
        client.force_login(user_a)
        url = reverse("transactions:bulk_action", kwargs={"pk": mb.pk})

        # Act
        response = client.post(
            url,
            {"action": "payer_a", "selected": [str(txs[0].id)]},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == "success"
        assert data["updated_count"] == 1
        assert data["updated"][0]["id"] == txs[0].id
        assert data["updated"][0]["payer_username"] == user_a.username

    @pytest.mark.django_db
    def test_Ajaxで選択0件のときwarningのJSONが返る(
        self, user_a, user_b, monthly_budget
    ):
        # Arrange
        mb = monthly_budget(user_a, user_b)
        client = Client()
        client.force_login(user_a)
        url = reverse("transactions:bulk_action", kwargs={"pk": mb.pk})

        # Act
        response = client.post(
            url,
            {"action": "payer_a", "selected": []},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["level"] == "warning"
        assert data["message"] == "明細を選択してください"

    @pytest.mark.django_db
    def test_通常POSTのときリダイレクトとメッセージが返る(
        self, user_a, user_b, monthly_budget, living_cost_transactions
    ):
        # Arrange
        mb = monthly_budget(user_a, user_b)
        txs = living_cost_transactions(mb, [(5000, None)])
        client = Client()
        client.force_login(user_a)
        url = reverse("transactions:bulk_action", kwargs={"pk": mb.pk})

        # Act
        response = client.post(
            url,
            {"action": "include", "selected": [str(txs[0].id)]},
        )

        # Assert
        assert response.status_code == 302
        assert response.url == reverse("budgets:month_detail", kwargs={"pk": mb.pk})
        messages = list(get_messages(response.wsgi_request))
        assert any("生活費に含めました" in str(m) for m in messages)
