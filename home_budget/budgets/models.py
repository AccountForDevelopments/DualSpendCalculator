from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models


class MonthlyBudget(models.Model):
    """月次予算管理モデル"""
    
    year_month = models.CharField(
        max_length=7,
        unique=True,
        verbose_name="対象月",
        help_text="YYYY-MM形式"
    )
    user_a = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="budget_as_a",
        verbose_name="ユーザーA"
    )
    user_b = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="budget_as_b",
        verbose_name="ユーザーB"
    )
    income_a = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name="ユーザーA月収"
    )
    income_b = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name="ユーザーB月収"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "月次予算"
        verbose_name_plural = "月次予算"
        ordering = ["-year_month"]

    def __str__(self):
        return f"{self.year_month}"

    @property
    def has_income(self) -> bool:
        """収入が入力されているか"""
        return self.income_a is not None and self.income_b is not None

    @property
    def transaction_count(self) -> int:
        """取り込み済み明細件数"""
        return self.transactions.count()

    @property
    def living_cost_count(self) -> int:
        """生活費対象明細件数"""
        return self.transactions.filter(is_living_cost=True).count()

    @property
    def total_living_cost(self) -> Decimal:
        """生活費合計"""
        from django.db.models import Sum
        result = self.transactions.filter(is_living_cost=True).aggregate(
            total=Sum("amount")
        )
        return result["total"] or Decimal("0")

