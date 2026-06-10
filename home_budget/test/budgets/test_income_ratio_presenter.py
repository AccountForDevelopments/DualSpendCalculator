"""build_income_ratio_context のテスト。"""
from decimal import Decimal

import pytest

from budgets.presenters import build_income_ratio_context


class Test_build_income_ratio_context:
    """月次詳細の負担割合 Presenter の検証。"""

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
        context = build_income_ratio_context(mb)

        # Assert
        assert context["ratio_a_percent"] == "60.0%"
        assert context["ratio_b_percent"] == "40.0%"

    @pytest.mark.django_db
    def test_収入未入力のときハイフンが返る(self, user_a, user_b, monthly_budget):
        """
        T-002: 収入が未入力のとき ratio_a_percent / ratio_b_percent が "-" になること
        """
        # Arrange
        mb = monthly_budget(user_a, user_b)

        # Act
        context = build_income_ratio_context(mb)

        # Assert
        assert context["ratio_a_percent"] == "-"
        assert context["ratio_b_percent"] == "-"
