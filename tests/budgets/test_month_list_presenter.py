"""build_month_list_rows のテスト。"""
from decimal import Decimal

import pytest

from budgets.presenters import build_month_list_rows


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
