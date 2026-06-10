"""
家事按分同意書生成ロジック

選択したTransactionのみを対象に、収入比に基づく家事按分を証明するPDF同意書を生成する。
"""
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from django.db.models import Sum
from django.template.loader import render_to_string
from weasyprint import HTML

from budgets.domain.ratios import calculate_ratios, calculate_shares, format_ratio_percent
from budgets.models import MonthlyBudget
from transactions.models import Transaction


@dataclass
class AgreementResult:
    """家事按分同意書計算結果"""
    
    # 入力データ
    year_month: str
    user_a_name: str
    user_b_name: str
    ratio_a: Optional[Decimal]
    ratio_b: Optional[Decimal]
    
    # 金額
    total: int  # 選択したTransactionの合計額
    share_a: int  # ユーザーAの負担額
    share_b: int  # ユーザーBの負担額
    
    # 明細
    transactions: list[Transaction]  # 選択したTransactionのリスト
    
    # 作成日
    created_date: date
    
    @property
    def ratio_a_percent(self) -> str:
        """ユーザーAの負担割合（%表示）"""
        return format_ratio_percent(self.ratio_a)

    @property
    def ratio_b_percent(self) -> str:
        """ユーザーBの負担割合（%表示）"""
        return format_ratio_percent(self.ratio_b)


class AgreementCalculator:
    """家事按分計算クラス
    
    選択したTransactionのみを対象に負担額を計算する。
    """
    
    def __init__(self, monthly_budget: MonthlyBudget):
        self.monthly_budget = monthly_budget
    
    def calculate(self, transaction_ids: list[int]) -> AgreementResult:
        """家事按分を計算する
        
        Args:
            transaction_ids: 選択したTransaction IDのリスト
            
        Returns:
            AgreementResult: 計算結果
        """
        mb = self.monthly_budget
        
        # 基本情報
        user_a_name = mb.user_a.username
        user_b_name = mb.user_b.username
        
        # 選択したTransactionを取得
        transactions = Transaction.objects.filter(
            id__in=transaction_ids,
            monthly_budget=mb
        ).order_by("date", "id")
        
        # 合計額を計算
        total = self._calculate_total(transactions)

        income_a = int(mb.income_a) if mb.income_a is not None else None
        income_b = int(mb.income_b) if mb.income_b is not None else None
        ratio_a, ratio_b = calculate_ratios(income_a, income_b)

        # 負担額を計算
        share_a, share_b = calculate_shares(total, ratio_a, ratio_b)
        
        return AgreementResult(
            year_month=mb.year_month,
            user_a_name=user_a_name,
            user_b_name=user_b_name,
            ratio_a=ratio_a,
            ratio_b=ratio_b,
            total=total,
            share_a=share_a,
            share_b=share_b,
            transactions=list(transactions),
            created_date=date.today(),
        )
    
    def _calculate_total(self, transactions) -> int:
        """選択したTransactionの合計額を計算する"""
        result = transactions.aggregate(total=Sum("amount"))
        return int(result["total"] or 0)


def generate_agreement_pdf(agreement_result: AgreementResult) -> bytes:
    """家事按分同意書PDFを生成する
    
    Args:
        agreement_result: 計算結果
        
    Returns:
        bytes: PDFバイナリ
    """
    # Djangoテンプレートをレンダリング
    html_string = render_to_string(
        "budgets/agreement.html",
        {"result": agreement_result},
    )
    
    # WeasyPrintでPDF生成
    pdf_bytes = HTML(string=html_string).write_pdf()

    return pdf_bytes
