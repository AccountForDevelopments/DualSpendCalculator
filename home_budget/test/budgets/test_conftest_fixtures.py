"""conftest フィクスチャの注入・動作確認（AC-004）。"""

from decimal import Decimal

import pytest


@pytest.mark.django_db
def test_fixtures_inject_user_a_user_b_monthly_budget(
    user_a,
    user_b,
    monthly_budget,
):
    """user_a, user_b, monthly_budget フィクスチャが注入され、期待どおり取得できる。"""
    assert user_a is not None
    assert user_b is not None
    assert user_a.username != user_b.username

    mb = monthly_budget(user_a, user_b)
    assert mb is not None
    assert mb.user_a_id == user_a.id
    assert mb.user_b_id == user_b.id
    assert mb.year_month == "2026-03"


@pytest.mark.django_db
def test_fixtures_inject_living_cost_transactions(
    user_a,
    user_b,
    monthly_budget,
    living_cost_transactions,
):
    """living_cost_transactions ファクトリで生活費明細が作成され、payer が user_a/user_b のいずれかである。"""
    mb = monthly_budget(user_a, user_b)
    txs = living_cost_transactions(mb, [(Decimal("1000"), user_a), (Decimal("2000"), user_b)])

    assert len(txs) == 2
    assert txs[0].is_living_cost is True
    assert txs[0].payer_id == user_a.id
    assert txs[0].amount == Decimal("1000")
    assert txs[1].is_living_cost is True
    assert txs[1].payer_id == user_b.id
    assert txs[1].amount == Decimal("2000")
