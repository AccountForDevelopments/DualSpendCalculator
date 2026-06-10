"""build_month_list_rows / build_month_list_column_labels のテスト。"""
from decimal import Decimal

import pytest

from budgets.presenters import build_month_list_column_labels, build_month_list_rows


class Test_build_month_list_column_labels:
    """月次一覧列見出し Presenter の検証。"""

    @pytest.mark.django_db
    def test_列見出しにユーザー名が含まれる(self, user_a, user_b, monthly_budget):
        # Arrange
        mb = monthly_budget(user_a, user_b)

        # Act
        labels = build_month_list_column_labels(mb)

        # Assert
        assert labels.user_a_income == f"{user_a.username} 収入"
        assert labels.user_b_income == f"{user_b.username} 収入"
        assert labels.user_a_ratio == f"{user_a.username} 割合"
        assert labels.user_b_ratio == f"{user_b.username} 割合"

    def test_月次が0件のときフォールバックラベルが返る(self):
        # Act
        labels = build_month_list_column_labels(None)

        # Assert
        assert labels.user_a_income == "収入A"
        assert labels.user_b_income == "収入B"
        assert labels.user_a_ratio == "割合A"
        assert labels.user_b_ratio == "割合B"


class Test_build_month_list_rows:
    """月次一覧 Presenter の検証。"""

    @pytest.mark.django_db
    def test_収入ありのとき割合がパーセント形式で返る(self, user_a, user_b, monthly_budget):
        """
        T-001: 収入が入力済みのとき ratio_a_percent / ratio_b_percent が "60.0%" / "40.0%" になること
        """
        # Arrange
        mb = monthly_budget(
            user_a,
            user_b,
            income_a=Decimal("300000"),
            income_b=Decimal("200000"),
        )

        # Act
        rows = build_month_list_rows([mb])

        # Assert
        assert len(rows) == 1
        assert rows[0].monthly_budget == mb
        assert rows[0].ratio_a_percent == "60.0%"
        assert rows[0].ratio_b_percent == "40.0%"

    @pytest.mark.django_db
    def test_収入未入力のときハイフンが返る(self, user_a, user_b, monthly_budget):
        """
        T-002: 収入が未入力のとき ratio_a_percent / ratio_b_percent が "-" になること
        """
        # Arrange
        mb = monthly_budget(user_a, user_b)

        # Act
        rows = build_month_list_rows([mb])

        # Assert
        assert len(rows) == 1
        assert rows[0].ratio_a_percent == "-"
        assert rows[0].ratio_b_percent == "-"
