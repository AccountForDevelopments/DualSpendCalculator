"""
負担割合・負担額のドメインロジック

収入比に基づく負担割合と、合計額に対する負担額の計算を提供する。
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


def calculate_ratios(
    income_a: Optional[int], income_b: Optional[int]
) -> tuple[Optional[Decimal], Optional[Decimal]]:
    """収入比から負担割合を計算する（小数4桁）。"""
    if income_a is None or income_b is None:
        return None, None

    total_income = income_a + income_b
    if total_income == 0:
        return None, None

    ratio_a = (Decimal(income_a) / Decimal(total_income)).quantize(
        Decimal("0.0001")
    )
    ratio_b = (Decimal(income_b) / Decimal(total_income)).quantize(
        Decimal("0.0001")
    )

    return ratio_a, ratio_b


def calculate_shares(
    total: int, ratio_a: Optional[Decimal], ratio_b: Optional[Decimal]
) -> tuple[int, int]:
    """負担割合に基づき負担額を計算する（端数は四捨五入）。"""
    if ratio_a is None or ratio_b is None:
        return 0, 0

    share_a = int(
        (Decimal(total) * ratio_a).quantize(Decimal("1"), ROUND_HALF_UP)
    )
    share_b = int(
        (Decimal(total) * ratio_b).quantize(Decimal("1"), ROUND_HALF_UP)
    )

    return share_a, share_b


def format_ratio_percent(ratio: Optional[Decimal]) -> str:
    """負担割合をパーセント表示用文字列に変換する。"""
    if ratio is None:
        return "-"
    return f"{ratio * 100:.1f}%"
