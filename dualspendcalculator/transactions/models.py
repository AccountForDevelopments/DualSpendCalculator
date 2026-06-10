import hashlib

from django.contrib.auth.models import User
from django.db import models

from budgets.models import MonthlyBudget


class TransactionQuerySet(models.QuerySet):
    """取引明細の検索クエリセット"""

    def for_monthly_budget(self, monthly_budget: MonthlyBudget):
        """月次詳細画面用: 対象月の明細を新しい順で返す。"""
        return self.filter(monthly_budget=monthly_budget).order_by("-date", "-id")

    def by_month_detail_filters(self, cleaned_data: dict):
        """月次詳細のフィルタ条件を適用する（検証済み cleaned_data のみ渡す）。"""
        queryset = self
        is_living_cost = cleaned_data.get("is_living_cost")
        if is_living_cost == "true":
            queryset = queryset.filter(is_living_cost=True)
        elif is_living_cost == "false":
            queryset = queryset.filter(is_living_cost=False)

        payer = cleaned_data.get("payer")
        if payer == "unset":
            queryset = queryset.filter(payer__isnull=True)
        elif payer:
            queryset = queryset.filter(payer_id=payer)

        category = cleaned_data.get("category")
        if category:
            queryset = queryset.filter(category=category)

        amount_min = cleaned_data.get("amount_min")
        if amount_min is not None:
            queryset = queryset.filter(amount__gte=amount_min)

        amount_max = cleaned_data.get("amount_max")
        if amount_max is not None:
            queryset = queryset.filter(amount__lte=amount_max)

        return queryset


class Transaction(models.Model):
    """取引明細モデル"""
    
    CATEGORY_CHOICES = [
        ("food", "食費"),
        ("daily", "日用品"),
        ("utility", "光熱費"),
        ("rent", "家賃"),
        ("other", "その他"),
    ]

    monthly_budget = models.ForeignKey(
        MonthlyBudget,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="対象月"
    )
    date = models.DateField(verbose_name="取引日")
    description = models.CharField(max_length=255, verbose_name="摘要")
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        verbose_name="金額"
    )
    is_living_cost = models.BooleanField(
        default=False,
        verbose_name="生活費対象"
    )
    payer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paid_transactions",
        verbose_name="支払者"
    )
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        null=True,
        blank=True,
        verbose_name="カテゴリ"
    )
    memo = models.TextField(blank=True, default="", verbose_name="メモ")
    import_hash = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="インポートハッシュ"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    objects = TransactionQuerySet.as_manager()

    class Meta:
        verbose_name = "取引明細"
        verbose_name_plural = "取引明細"
        ordering = ["-date", "-id"]
        indexes = [
            models.Index(fields=["monthly_budget"]),
            models.Index(fields=["is_living_cost"]),
            models.Index(fields=["payer"]),
            models.Index(fields=["date"]),
        ]

    def __str__(self):
        return f"{self.date} {self.description} ¥{self.amount:,}"

    @staticmethod
    def generate_import_hash(date, description: str, amount) -> str:
        """重複判定用ハッシュを生成"""
        hash_source = f"{date.isoformat()}|{description}|{amount}"
        return hashlib.sha256(hash_source.encode()).hexdigest()

