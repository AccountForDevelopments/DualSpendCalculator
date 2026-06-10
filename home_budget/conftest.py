"""pytest フィクスチャ: User / MonthlyBudget / Transaction のテスト用データ生成。

利用するテストには @pytest.mark.django_db を付与すること。
"""

import uuid
from decimal import Decimal
from datetime import datetime

import pytest
from django.contrib.auth.models import User

from budgets.models import MonthlyBudget
from transactions.models import Transaction


@pytest.fixture(scope="function")
def _user_pair():
    """2 名の User をまとめて作成し (user_a, user_b) を返す。"""
    suffix = uuid.uuid4().hex[:8]
    user_a = User.objects.create(username=f"user_a_{suffix}")
    user_b = User.objects.create(username=f"user_b_{suffix}")
    return (user_a, user_b)


@pytest.fixture(scope="function")
def user_a(_user_pair):
    """精算の「ユーザーA」となる User インスタンス。"""
    return _user_pair[0]


@pytest.fixture(scope="function")
def user_b(_user_pair):
    """精算の「ユーザーB」となる User インスタンス。"""
    return _user_pair[1]


@pytest.fixture(scope="function")
def _user_pair_ab():
    """05_calculation_rules の計算例用。username が "A" と "B" の 2 名の User をまとめて作成し (user_a, user_b) を返す。"""
    user_a = User.objects.create(username="A")
    user_b = User.objects.create(username="B")
    return (user_a, user_b)


@pytest.fixture(scope="function")
def user_a_ab(_user_pair_ab):
    """精算の「ユーザーA」となる User（username="A"）。T-001 の settlement_text リテラル検証用。"""
    return _user_pair_ab[0]


@pytest.fixture(scope="function")
def user_b_ab(_user_pair_ab):
    """精算の「ユーザーB」となる User（username="B"）。T-001 の settlement_text リテラル検証用。"""
    return _user_pair_ab[1]


@pytest.fixture(scope="function")
def monthly_budget():
    """user_a, user_b に紐づく MonthlyBudget を 1 件作成するファクトリを返す。

    返り値は callable。呼び出し例:
        mb = monthly_budget(user_a, user_b)
        mb = monthly_budget(user_a, user_b, year_month="2026-04", income_a=Decimal("300000"), income_b=Decimal("200000"))
    """
    def _create(
        user_a,
        user_b,
        year_month="2026-03",
        income_a=None,
        income_b=None,
    ):
        kwargs = {
            "year_month": year_month,
            "user_a": user_a,
            "user_b": user_b,
        }
        if income_a is not None:
            kwargs["income_a"] = income_a
        if income_b is not None:
            kwargs["income_b"] = income_b
        return MonthlyBudget.objects.create(**kwargs)

    return _create


@pytest.fixture(scope="function")
def living_cost_transactions():
    """指定した MonthlyBudget に紐づく is_living_cost=True の Transaction を複数件作成するファクトリを返す。

    返り値は callable。呼び出し例:
        txs = living_cost_transactions(monthly_budget, [(Decimal("1000"), user_a), (Decimal("2000"), user_b)])
        txs = living_cost_transactions(monthly_budget, [(Decimal("1000"), None), (Decimal("2000"), user_a)])  # payer=None 可
    items: (amount, payer) のリスト。amount は Decimal または int。payer は User または None（支払者未設定）。
    """
    def _create(monthly_budget, items):
        year_month = monthly_budget.year_month
        base_date = datetime.strptime(f"{year_month}-01", "%Y-%m-%d").date()
        created = []
        for i, (amount, payer) in enumerate(items):
            amount = Decimal(amount) if not isinstance(amount, Decimal) else amount
            date = base_date
            description = f"fixture-{i}"
            import_hash = Transaction.generate_import_hash(date, description, amount)
            tx = Transaction.objects.create(
                monthly_budget=monthly_budget,
                date=date,
                description=description,
                amount=amount,
                is_living_cost=True,
                payer=payer,
                import_hash=import_hash,
            )
            created.append(tx)
        return created

    return _create
