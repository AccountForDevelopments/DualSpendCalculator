"""
家事按分同意書ダウンロードリクエストの検証

PDF 生成前に Transaction ID と対象月の整合性を検証する。
"""
from dataclasses import dataclass

from budgets.models import MonthlyBudget
from transactions.models import Transaction


@dataclass
class AgreementRequestResult:
    """同意書リクエストの検証結果"""

    ok: bool
    message: str = ""
    monthly_budget: MonthlyBudget | None = None
    transaction_ids: list[int] | None = None
    redirect_url_name: str = "budgets:month_list"
    redirect_pk: int | None = None


class AgreementRequestValidator:
    """同意書ダウンロード用 POST パラメータを検証する"""

    def validate(
        self,
        transaction_ids: list[str],
        monthly_budget_id: str | None,
    ) -> AgreementRequestResult:
        if not transaction_ids:
            return AgreementRequestResult(
                ok=False,
                message="選択された請求がありません",
            )

        try:
            transaction_ids_int = [int(tid) for tid in transaction_ids]
        except (ValueError, TypeError):
            return AgreementRequestResult(
                ok=False,
                message="無効な請求IDが含まれています",
            )

        if not monthly_budget_id:
            return AgreementRequestResult(
                ok=False,
                message="対象月が指定されていません",
            )

        try:
            monthly_budget = MonthlyBudget.objects.get(pk=monthly_budget_id)
        except MonthlyBudget.DoesNotExist:
            return AgreementRequestResult(
                ok=False,
                message="対象月が見つかりません",
            )

        monthly_budget_pk = int(monthly_budget_id)
        requested_ids = set(transaction_ids_int)

        all_existing_ids = set(
            Transaction.objects.filter(id__in=transaction_ids_int).values_list(
                "id", flat=True
            )
        )
        if all_existing_ids != requested_ids:
            missing_ids = requested_ids - all_existing_ids
            return AgreementRequestResult(
                ok=False,
                message=(
                    "存在しない請求が含まれています"
                    f"（ID: {', '.join(map(str, missing_ids))}）"
                ),
                redirect_url_name="budgets:month_detail",
                redirect_pk=monthly_budget_pk,
            )

        other_month_transactions = Transaction.objects.filter(
            id__in=transaction_ids_int
        ).exclude(monthly_budget=monthly_budget)

        if other_month_transactions.exists():
            return AgreementRequestResult(
                ok=False,
                message="異なる対象月の請求が含まれています",
                redirect_url_name="budgets:month_detail",
                redirect_pk=monthly_budget_pk,
            )

        return AgreementRequestResult(
            ok=True,
            monthly_budget=monthly_budget,
            transaction_ids=transaction_ids_int,
        )
