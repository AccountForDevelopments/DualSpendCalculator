"""budgets.domain.ratios の単体テスト。"""
from decimal import Decimal

import pytest

from budgets.domain.ratios import calculate_ratios, calculate_shares, format_ratio_percent


class Test_calculate_ratios:
    """calculate_ratios の振る舞いを検証する。"""

    def test_通常の収入比でratio_a_ratio_bが小数4桁で返る(self):
        """
        T-001: 通常の収入比で (ratio_a, ratio_b) が小数4桁の Decimal で返ること
        """
        # Arrange
        income_a = 300000
        income_b = 200000
        expected_ratio_a = Decimal("0.6000")
        expected_ratio_b = Decimal("0.4000")

        # Act
        ratio_a, ratio_b = calculate_ratios(income_a, income_b)

        # Assert
        assert ratio_a == expected_ratio_a
        assert ratio_b == expected_ratio_b

    def test_割り切れない収入比で小数4桁に丸まり合計が1になる(self):
        """
        T-002: 割り切れない収入比で小数4桁に丸まり、ratio_a + ratio_b == 1 であること
        """
        # Arrange
        income_a = 1
        income_b = 3
        four_places = Decimal("0.0001")

        # Act
        ratio_a, ratio_b = calculate_ratios(income_a, income_b)

        # Assert
        assert ratio_a == ratio_a.quantize(four_places)
        assert ratio_b == ratio_b.quantize(four_places)
        assert ratio_a + ratio_b == Decimal("1")

    def test_income_aが0のときratio_aが0_ratio_bが1で返る(self):
        """
        T-003: income_a が 0 のとき (0.0000, 1.0000) が返ること
        """
        # Arrange
        income_a = 0
        income_b = 200000
        expected_ratio_a = Decimal("0.0000")
        expected_ratio_b = Decimal("1.0000")

        # Act
        ratio_a, ratio_b = calculate_ratios(income_a, income_b)

        # Assert
        assert ratio_a == expected_ratio_a
        assert ratio_b == expected_ratio_b

    def test_income_bが0のときratio_aが1_ratio_bが0で返る(self):
        """
        T-004: income_b が 0 のとき (1.0000, 0.0000) が返ること
        """
        # Arrange
        income_a = 300000
        income_b = 0
        expected_ratio_a = Decimal("1.0000")
        expected_ratio_b = Decimal("0.0000")

        # Act
        ratio_a, ratio_b = calculate_ratios(income_a, income_b)

        # Assert
        assert ratio_a == expected_ratio_a
        assert ratio_b == expected_ratio_b

    def test_両方0のときNoneのタプルが返る(self):
        """
        T-005: income_a, income_b が両方 0 のとき (None, None) が返ること
        """
        # Arrange
        income_a = 0
        income_b = 0

        # Act
        ratio_a, ratio_b = calculate_ratios(income_a, income_b)

        # Assert
        assert ratio_a is None
        assert ratio_b is None

    def test_income_aがNoneのときNoneのタプルが返る(self):
        """
        T-006: income_a が None のとき (None, None) が返ること
        """
        # Arrange
        income_a = None
        income_b = 200000

        # Act
        ratio_a, ratio_b = calculate_ratios(income_a, income_b)

        # Assert
        assert ratio_a is None
        assert ratio_b is None

    def test_income_bがNoneのときNoneのタプルが返る(self):
        """
        T-007: income_b が None のとき (None, None) が返ること
        """
        # Arrange
        income_a = 300000
        income_b = None

        # Act
        ratio_a, ratio_b = calculate_ratios(income_a, income_b)

        # Assert
        assert ratio_a is None
        assert ratio_b is None


class Test_calculate_shares:
    """calculate_shares の振る舞いを検証する。"""

    def test_割り切れるtotalとratioでshare_a_share_bが整数で返る(self):
        """
        T-001: 割り切れる total と ratio で (share_a, share_b) が整数で返ること
        """
        # Arrange
        total = 100000
        ratio_a = Decimal("0.6")
        ratio_b = Decimal("0.4")
        expected_share_a = 60000
        expected_share_b = 40000

        # Act
        share_a, share_b = calculate_shares(total, ratio_a, ratio_b)

        # Assert
        assert share_a == expected_share_a
        assert share_b == expected_share_b

    def test_四捨五入が発生するtotalでshare_aが6001で返る(self):
        """
        T-002: 四捨五入が発生する total で share_a が 6001、share_b が 4000 で返ること
        """
        # Arrange
        total = 10001
        ratio_a = Decimal("0.6")
        ratio_b = Decimal("0.4")
        expected_share_a = 6001
        expected_share_b = 4000

        # Act
        share_a, share_b = calculate_shares(total, ratio_a, ratio_b)

        # Assert
        assert share_a == expected_share_a
        assert share_b == expected_share_b

    def test_totalが0のとき0のタプルが返る(self):
        """
        T-003: total が 0 のとき (0, 0) が返ること
        """
        # Arrange
        total = 0
        ratio_a = Decimal("0.6")
        ratio_b = Decimal("0.4")
        expected_share_a = 0
        expected_share_b = 0

        # Act
        share_a, share_b = calculate_shares(total, ratio_a, ratio_b)

        # Assert
        assert share_a == expected_share_a
        assert share_b == expected_share_b

    @pytest.mark.parametrize(
        "ratio_a,ratio_b",
        [
            (None, Decimal("0.4")),
            (Decimal("0.6"), None),
        ],
        ids=["T-004a ratio_aがNone", "T-004b ratio_bがNone"],
    )
    def test_ratio_aまたはratio_bがNoneのとき0のタプルが返る(
        self, ratio_a, ratio_b
    ):
        """
        T-004: ratio_a または ratio_b が None のとき (0, 0) が返ること
        """
        # Arrange
        total = 100000
        expected_share_a = 0
        expected_share_b = 0

        # Act
        share_a, share_b = calculate_shares(total, ratio_a, ratio_b)

        # Assert
        assert share_a == expected_share_a
        assert share_b == expected_share_b


class Test_format_ratio_percent:
    """format_ratio_percent の振る舞いを検証する。"""

    def test_ratioがDecimalのとき60_0パーセント形式で返る(self):
        """
        T-001: ratio が Decimal のとき "60.0%" が返ること
        """
        # Act
        actual = format_ratio_percent(Decimal("0.6"))

        # Assert
        assert actual == "60.0%"

    def test_ratioがNoneのときハイフンが返る(self):
        """
        T-002: ratio が None のとき "-" が返ること
        """
        # Act
        actual = format_ratio_percent(None)

        # Assert
        assert actual == "-"
