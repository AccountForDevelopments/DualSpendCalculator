"""SettlementCalculator の単体テスト。

05_calculation_rules の負担割合・制約・エッジケースに基づく検証。
"""
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from budgets.services.settlement import SettlementCalculator, SettlementResult


def _default_settlement_result_kwargs():
    """ratio_a_percent / ratio_b_percent の検証に不要な必須フィールドをダミーで埋めた辞書を返す。"""
    return {
        "year_month": "2026-01",
        "user_a_name": "A",
        "user_b_name": "B",
        "income_a": 0,
        "income_b": 0,
        "total": 0,
        "share_a": 0,
        "share_b": 0,
        "paid_a": 0,
        "paid_b": 0,
        "settlement": 0,
        "settlement_text": "精算不要",
    }


class Test_SettlementResult_ratio_a_percent:
    """SettlementResult.ratio_a_percent の振る舞いを検証する。"""

    def test_ratio_aがDecimalのとき60_0パーセント形式で返る(self):
        """
        T-001: ratio_a が Decimal のとき "60.0%" が返ること (AC-001)
        """
        # Arrange
        kwargs = {
            **_default_settlement_result_kwargs(),
            "ratio_a": Decimal("0.6"),
            "ratio_b": Decimal("0.4"),
        }
        result = SettlementResult(**kwargs)

        # Act
        actual = result.ratio_a_percent

        # Assert
        assert actual == "60.0%"

    def test_ratio_aがNoneのときハイフンが返る(self):
        """
        T-002: ratio_a が None のとき "-" が返ること (AC-002)
        """
        # Arrange
        kwargs = {
            **_default_settlement_result_kwargs(),
            "ratio_a": None,
            "ratio_b": Decimal("0.4"),
        }
        result = SettlementResult(**kwargs)

        # Act
        actual = result.ratio_a_percent

        # Assert
        assert actual == "-"


class Test_SettlementResult_ratio_b_percent:
    """SettlementResult.ratio_b_percent の振る舞いを検証する。"""

    def test_ratio_bがDecimalのとき40_0パーセント形式で返る(self):
        """
        T-003: ratio_b が Decimal のとき "40.0%" が返ること (AC-003)
        """
        # Arrange
        kwargs = {
            **_default_settlement_result_kwargs(),
            "ratio_a": Decimal("0.6"),
            "ratio_b": Decimal("0.4"),
        }
        result = SettlementResult(**kwargs)

        # Act
        actual = result.ratio_b_percent

        # Assert
        assert actual == "40.0%"

    def test_ratio_bがNoneのときハイフンが返る(self):
        """
        T-004: ratio_b が None のとき "-" が返ること (AC-004)
        """
        # Arrange
        kwargs = {
            **_default_settlement_result_kwargs(),
            "ratio_a": Decimal("0.6"),
            "ratio_b": None,
        }
        result = SettlementResult(**kwargs)

        # Act
        actual = result.ratio_b_percent

        # Assert
        assert actual == "-"


class Test__calculate_settlement:
    """_calculate_settlement の振る舞いを検証する。"""

    @pytest.fixture
    def calculator(self):
        """DB を使わない単体テスト用に、monthly_budget をモックした SettlementCalculator を返す。"""
        mock_mb = MagicMock()
        return SettlementCalculator(mock_mb)

    def test_paid_aがshare_aより大きいとき正のsettlementとBがAに払う文言が返る(
        self, calculator
    ):
        """
        T-001: paid_a > share_a のとき正の settlement と「BがAに」文言・金額が返ること (AC-001)
        """
        # Arrange
        paid_a = 13000
        share_a = 12000
        user_a_name = "userA"
        user_b_name = "userB"
        expected_settlement = 1000

        # Act
        settlement, settlement_text = calculator._calculate_settlement(
            paid_a, share_a, user_a_name, user_b_name
        )

        # Assert
        assert settlement == expected_settlement
        assert "userBがuserAに" in settlement_text
        assert "1,000" in settlement_text

    def test_paid_aがshare_aより小さいとき負のsettlementとAがBに払う文言が返る(
        self, calculator
    ):
        """
        T-002: paid_a < share_a のとき負の settlement と「AがBに」文言・金額が返ること (AC-002)
        """
        # Arrange
        paid_a = 5000
        share_a = 12000
        user_a_name = "userA"
        user_b_name = "userB"
        expected_settlement = -7000

        # Act
        settlement, settlement_text = calculator._calculate_settlement(
            paid_a, share_a, user_a_name, user_b_name
        )

        # Assert
        assert settlement == expected_settlement
        assert "userAがuserBに" in settlement_text
        assert "7,000" in settlement_text

    def test_paid_aとshare_aが等しいとき0と精算不要文言が返る(self, calculator):
        """
        T-003: paid_a == share_a のとき settlement が 0 で「精算不要（ちょうど）」が返ること (AC-003)
        """
        # Arrange
        paid_a = 12000
        share_a = 12000
        user_a_name = "userA"
        user_b_name = "userB"
        expected_settlement = 0
        expected_settlement_text = "精算不要（ちょうど）"

        # Act
        settlement, settlement_text = calculator._calculate_settlement(
            paid_a, share_a, user_a_name, user_b_name
        )

        # Assert
        assert settlement == expected_settlement
        assert settlement_text == expected_settlement_text


class Test_calculate_統合:
    """calculate() の統合テスト。DB 上の MonthlyBudget と Transaction で精算結果を検証する。"""

    @pytest.mark.django_db
    def test_05計算例と一致する精算結果が返る(
        self,
        user_a_ab,
        user_b_ab,
        monthly_budget,
        living_cost_transactions,
    ):
        """
        T-001: 05_calculation_rules の計算例と一致し、settlement_text に「BがAに」「1,000」が含まれること (AC-001)
        """
        # Arrange
        mb = monthly_budget(
            user_a_ab,
            user_b_ab,
            year_month="2025-12",
            income_a=Decimal("300000"),
            income_b=Decimal("200000"),
        )
        living_cost_transactions(
            mb,
            [
                (Decimal("5000"), user_a_ab),
                (Decimal("8000"), user_a_ab),
                (Decimal("3000"), user_b_ab),
                (Decimal("4000"), user_b_ab),
            ],
        )

        # Act
        result = SettlementCalculator(mb).calculate()

        # Assert
        assert result.total == 20000
        assert result.share_a == 12000
        assert result.share_b == 8000
        assert result.paid_a == 13000
        assert result.paid_b == 7000
        assert result.settlement == 1000
        assert "BがAに" in result.settlement_text
        assert "1,000" in result.settlement_text

    @pytest.mark.django_db
    def test_収入未入力のときincome_missingがTrueでratio_shareが0またはNone(
        self,
        user_a,
        user_b,
        monthly_budget,
    ):
        """
        T-002: income_a が None のとき income_missing が True、ratio/share が None/0 であること (AC-002)
        """
        # Arrange
        mb = monthly_budget(user_a, user_b, income_a=None, income_b=Decimal("200000"))

        # Act
        result = SettlementCalculator(mb).calculate()

        # Assert
        assert result.income_missing is True
        assert result.ratio_a is None
        assert result.ratio_b is None
        assert result.share_a == 0
        assert result.share_b == 0

    @pytest.mark.django_db
    def test_支払者未設定の生活費明細があるときpayer_missing_countが件数と一致(
        self,
        user_a,
        user_b,
        monthly_budget,
        living_cost_transactions,
    ):
        """
        T-003: 支払者未設定の生活費明細が 2 件のとき payer_missing_count が 2 であること (AC-003)
        """
        # Arrange
        mb = monthly_budget(
            user_a,
            user_b,
            income_a=Decimal("300000"),
            income_b=Decimal("200000"),
        )
        living_cost_transactions(
            mb,
            [
                (Decimal("1000"), None),
                (Decimal("2000"), None),
                (Decimal("3000"), user_a),
            ],
        )

        # Act
        result = SettlementCalculator(mb).calculate()

        # Assert
        assert result.payer_missing_count == 2

    @pytest.mark.django_db
    def test_生活費対象が0件のときtotal0で精算不要(
        self,
        user_a,
        user_b,
        monthly_budget,
    ):
        """
        T-004: 生活費対象が 0 件のとき total=0, settlement=0, settlement_text が「精算不要（ちょうど）」であること (AC-004)
        """
        # Arrange
        mb = monthly_budget(
            user_a,
            user_b,
            income_a=Decimal("300000"),
            income_b=Decimal("200000"),
        )

        # Act
        result = SettlementCalculator(mb).calculate()

        # Assert
        assert result.total == 0
        assert result.settlement == 0
        assert result.settlement_text == "精算不要（ちょうど）"

    @pytest.mark.django_db
    def test_全明細が同一支払者のときpaid_aが合計と一致し精算額が正しく計算される(
        self,
        user_a,
        user_b,
        monthly_budget,
        living_cost_transactions,
    ):
        """
        T-005: 生活費対象の明細がすべて user_a の支払いのとき、paid_a が合計・paid_b=0、精算額・文言が正しいこと (AC-005)
        """
        # Arrange: 合計 20000、負担 6:4 → share_a=12000, share_b=8000, settlement = paid_a - share_a = 8000
        mb = monthly_budget(
            user_a,
            user_b,
            income_a=Decimal("300000"),
            income_b=Decimal("200000"),
        )
        living_cost_transactions(mb, [(Decimal("20000"), user_a)])

        # Act
        result = SettlementCalculator(mb).calculate()

        # Assert
        expected_total = 20000
        expected_share_a = 12000
        expected_paid_a = 20000
        expected_settlement = expected_paid_a - expected_share_a  # 8000
        assert result.total == expected_total
        assert result.paid_a == expected_paid_a
        assert result.paid_b == 0
        assert result.settlement == expected_settlement
        assert "8,000" in result.settlement_text
        assert result.user_b_name in result.settlement_text and result.user_a_name in result.settlement_text
