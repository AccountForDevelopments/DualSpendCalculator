"""AgreementCalculator の単体テスト。

01_what_to_build.md の AC-001, AC-008 に基づく検証。
"""
from datetime import date
from decimal import Decimal, ROUND_HALF_UP

import pytest

from budgets.services.agreement import AgreementCalculator, AgreementResult
from transactions.models import Transaction


class Test_AgreementCalculator_calculate:
    """AgreementCalculator.calculate() の振る舞いを検証する。"""

    @pytest.mark.django_db
    def test_選択したTransactionの合計と負担額が正しく計算される(
        self,
        user_a,
        user_b,
        monthly_budget,
        living_cost_transactions,
    ):
        """
        T-001: 選択したTransaction IDのリストとMonthlyBudgetを指定してcalculate()を実行するとき、
        選択したTransactionのamountの合計が計算され、calculate_ratios を使用して
        share_a/share_bが正しく計算されること (AC-001)
        """
        # Arrange
        mb = monthly_budget(
            user_a,
            user_b,
            year_month="2026-03",
            income_a=Decimal("300000"),
            income_b=Decimal("200000"),
        )
        transactions = living_cost_transactions(
            mb,
            [
                (Decimal("5000"), user_a),
                (Decimal("8000"), user_a),
                (Decimal("3000"), user_b),
                (Decimal("4000"), user_b),
            ],
        )
        # 最初の2件のみを選択
        selected_ids = [transactions[0].id, transactions[1].id]
        expected_total = 5000 + 8000  # 13000
        # ratio_a = 0.6, ratio_b = 0.4 で計算（四捨五入）
        expected_share_a = int((Decimal(expected_total) * Decimal("0.6000")).quantize(Decimal("1"), ROUND_HALF_UP))  # 7800
        expected_share_b = int((Decimal(expected_total) * Decimal("0.4000")).quantize(Decimal("1"), ROUND_HALF_UP))  # 5200

        # Act
        result = AgreementCalculator(mb).calculate(selected_ids)

        # Assert
        assert result.total == expected_total
        assert result.share_a == expected_share_a
        assert result.share_b == expected_share_b
        assert result.year_month == "2026-03"
        assert result.user_a_name == user_a.username
        assert result.user_b_name == user_b.username
        assert len(result.transactions) == 2
        assert result.transactions[0].id == transactions[0].id
        assert result.transactions[1].id == transactions[1].id

    @pytest.mark.django_db
    def test_income_aまたはincome_bがNoneのとき負担額が0で計算される(
        self,
        user_a,
        user_b,
        monthly_budget,
        living_cost_transactions,
    ):
        """
        T-002: MonthlyBudgetのincome_aまたはincome_bがNoneの状態でcalculate()を実行するとき、
        ratio_a/ratio_bがNoneとなり、負担額は0として計算されること (AC-008)
        """
        # Arrange
        mb = monthly_budget(
            user_a,
            user_b,
            year_month="2026-03",
            income_a=None,
            income_b=Decimal("200000"),
        )
        transactions = living_cost_transactions(
            mb,
            [
                (Decimal("10000"), user_a),
            ],
        )
        selected_ids = [transactions[0].id]

        # Act
        result = AgreementCalculator(mb).calculate(selected_ids)

        # Assert
        assert result.ratio_a is None
        assert result.ratio_b is None
        assert result.share_a == 0
        assert result.share_b == 0
        assert result.total == 10000
        assert result.ratio_a_percent == "-"
        assert result.ratio_b_percent == "-"

    @pytest.mark.django_db
    def test_四捨五入が発生する負担額が正しく計算される(
        self,
        user_a,
        user_b,
        monthly_budget,
        living_cost_transactions,
    ):
        """
        T-003: 四捨五入が発生する合計額で負担額が正しく計算されること
        """
        # Arrange
        mb = monthly_budget(
            user_a,
            user_b,
            year_month="2026-03",
            income_a=Decimal("300000"),
            income_b=Decimal("200000"),
        )
        transactions = living_cost_transactions(
            mb,
            [
                (Decimal("10001"), user_a),  # 合計10001、ratio_a=0.6 → 6000.6 → 6001（四捨五入）
            ],
        )
        selected_ids = [transactions[0].id]
        expected_share_a = 6001
        expected_share_b = 4000

        # Act
        result = AgreementCalculator(mb).calculate(selected_ids)

        # Assert
        assert result.share_a == expected_share_a
        assert result.share_b == expected_share_b


class Test_AgreementResult_ratio_percent:
    """AgreementResult.ratio_a_percent / ratio_b_percent の振る舞いを検証する。"""

    def test_ratio_aがDecimalのとき60_0パーセント形式で返る(self):
        """
        T-004: ratio_a が Decimal のとき "60.0%" が返ること
        """
        # Arrange
        result = AgreementResult(
            year_month="2026-03",
            user_a_name="userA",
            user_b_name="userB",
            ratio_a=Decimal("0.6"),
            ratio_b=Decimal("0.4"),
            total=10000,
            share_a=6000,
            share_b=4000,
            transactions=[],
            created_date=date.today(),
        )

        # Act
        actual = result.ratio_a_percent

        # Assert
        assert actual == "60.0%"

    def test_ratio_aがNoneのときハイフンが返る(self):
        """
        T-005: ratio_a が None のとき "-" が返ること
        """
        # Arrange
        result = AgreementResult(
            year_month="2026-03",
            user_a_name="userA",
            user_b_name="userB",
            ratio_a=None,
            ratio_b=None,
            total=10000,
            share_a=0,
            share_b=0,
            transactions=[],
            created_date=date.today(),
        )

        # Act
        actual = result.ratio_a_percent

        # Assert
        assert actual == "-"

    def test_ratio_bがDecimalのとき40_0パーセント形式で返る(self):
        """
        T-006: ratio_b が Decimal のとき "40.0%" が返ること
        """
        # Arrange
        result = AgreementResult(
            year_month="2026-03",
            user_a_name="userA",
            user_b_name="userB",
            ratio_a=Decimal("0.6"),
            ratio_b=Decimal("0.4"),
            total=10000,
            share_a=6000,
            share_b=4000,
            transactions=[],
            created_date=date.today(),
        )

        # Act
        actual = result.ratio_b_percent

        # Assert
        assert actual == "40.0%"

    def test_ratio_bがNoneのときハイフンが返る(self):
        """
        T-007: ratio_b が None のとき "-" が返ること
        """
        # Arrange
        result = AgreementResult(
            year_month="2026-03",
            user_a_name="userA",
            user_b_name="userB",
            ratio_a=None,
            ratio_b=None,
            total=10000,
            share_a=0,
            share_b=0,
            transactions=[],
            created_date=date.today(),
        )

        # Act
        actual = result.ratio_b_percent

        # Assert
        assert actual == "-"
