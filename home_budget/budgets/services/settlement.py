"""
精算計算ロジック

月次の生活費精算を行うための計算を提供する。
"""
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from django.db.models import Sum

from budgets.domain.ratios import calculate_ratios, calculate_shares, format_ratio_percent
from budgets.models import MonthlyBudget
from transactions.models import Transaction


@dataclass
class SettlementResult:
    """精算計算結果"""
    
    # 入力データ
    year_month: str
    user_a_name: str
    user_b_name: str
    income_a: Optional[int]
    income_b: Optional[int]
    
    # 割合
    ratio_a: Optional[Decimal]
    ratio_b: Optional[Decimal]
    
    # 金額
    total: int
    share_a: int
    share_b: int
    paid_a: int
    paid_b: int
    settlement: int  # 正: BがAに払う, 負: AがBに払う
    
    # 表示用
    settlement_text: str
    
    # 警告
    income_missing: bool = False
    payer_missing_count: int = 0
    
    # 件数
    living_cost_count: int = 0
    total_count: int = 0
    
    @property
    def ratio_a_percent(self) -> str:
        """ユーザーAの負担割合（%表示）"""
        return format_ratio_percent(self.ratio_a)

    @property
    def ratio_b_percent(self) -> str:
        """ユーザーBの負担割合（%表示）"""
        return format_ratio_percent(self.ratio_b)


class SettlementCalculator:
    """精算計算クラス"""
    
    def __init__(self, monthly_budget: MonthlyBudget):
        self.monthly_budget = monthly_budget
    
    def calculate(self) -> SettlementResult:
        """精算を計算する"""
        mb = self.monthly_budget
        
        # 基本情報
        user_a_name = mb.user_a.username
        user_b_name = mb.user_b.username
        income_a = int(mb.income_a) if mb.income_a is not None else None
        income_b = int(mb.income_b) if mb.income_b is not None else None
        
        # 収入が未入力かチェック
        income_missing = income_a is None or income_b is None
        
        # 割合計算
        ratio_a, ratio_b = calculate_ratios(income_a, income_b)
        
        # 明細取得
        transactions = Transaction.objects.filter(monthly_budget=mb)
        total_count = transactions.count()
        
        living_cost_transactions = transactions.filter(is_living_cost=True)
        living_cost_count = living_cost_transactions.count()
        
        # 支払者未設定の生活費対象明細をカウント
        payer_missing_count = living_cost_transactions.filter(payer__isnull=True).count()
        
        # 生活費合計
        total = self._calculate_total(living_cost_transactions)
        
        # 負担額
        share_a, share_b = calculate_shares(total, ratio_a, ratio_b)
        
        # 立替額
        paid_a = self._calculate_paid(living_cost_transactions, mb.user_a)
        paid_b = self._calculate_paid(living_cost_transactions, mb.user_b)
        
        # 精算額
        settlement, settlement_text = self._calculate_settlement(
            paid_a, share_a, user_a_name, user_b_name
        )
        
        return SettlementResult(
            year_month=mb.year_month,
            user_a_name=user_a_name,
            user_b_name=user_b_name,
            income_a=income_a,
            income_b=income_b,
            ratio_a=ratio_a,
            ratio_b=ratio_b,
            total=total,
            share_a=share_a,
            share_b=share_b,
            paid_a=paid_a,
            paid_b=paid_b,
            settlement=settlement,
            settlement_text=settlement_text,
            income_missing=income_missing,
            payer_missing_count=payer_missing_count,
            living_cost_count=living_cost_count,
            total_count=total_count,
        )
    
    def _calculate_total(self, transactions) -> int:
        """生活費合計を計算する"""
        result = transactions.aggregate(total=Sum("amount"))
        return int(result["total"] or 0)
    
    def _calculate_paid(self, transactions, user) -> int:
        """立替額を計算する"""
        result = transactions.filter(payer=user).aggregate(total=Sum("amount"))
        return int(result["total"] or 0)
    
    def _calculate_settlement(
        self, paid_a: int, share_a: int, user_a_name: str, user_b_name: str
    ) -> tuple[int, str]:
        """精算額を計算する"""
        # balance_a = paid_a - share_a
        # 正: Aが払いすぎ → BがAに払う
        # 負: Aが不足 → AがBに払う
        settlement = paid_a - share_a
        
        if settlement > 0:
            settlement_text = f"{user_b_name}が{user_a_name}に ¥{settlement:,} 払う"
        elif settlement < 0:
            settlement_text = f"{user_a_name}が{user_b_name}に ¥{-settlement:,} 払う"
        else:
            settlement_text = "精算不要（ちょうど）"
        
        return settlement, settlement_text

