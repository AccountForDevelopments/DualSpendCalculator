"""
明細一括操作サービス

選択した Transaction を対象月の範囲内で一括更新する。
"""
from dataclasses import dataclass
from typing import Literal

from budgets.models import MonthlyBudget

from transactions.models import Transaction

MessageLevel = Literal["warning", "success", "error"]


@dataclass
class BulkActionResult:
    """一括操作の結果（View が messages に反映する）"""

    level: MessageLevel
    message: str
    updated_count: int = 0
    updated_transactions: list[dict] | None = None


class BulkTransactionActionService:
    """明細一括操作を実行するサービス"""

    def apply(
        self,
        monthly_budget: MonthlyBudget,
        action: str | None,
        selected_ids: list[str],
    ) -> BulkActionResult:
        if not selected_ids:
            return BulkActionResult(
                level="warning",
                message="明細を選択してください",
            )

        transactions = Transaction.objects.filter(
            id__in=selected_ids,
            monthly_budget=monthly_budget,
        )
        count = transactions.count()

        if action == "include":
            transactions.update(is_living_cost=True)
            return BulkActionResult(
                level="success",
                message=f"{count}件を生活費に含めました",
                updated_count=count,
            )
        if action == "exclude":
            transactions.update(is_living_cost=False)
            return BulkActionResult(
                level="success",
                message=f"{count}件を生活費から除外しました",
                updated_count=count,
            )
        if action == "payer_a":
            return self._apply_payer_update(
                transactions,
                payer=monthly_budget.user_a,
                username_for_message=monthly_budget.user_a.username,
            )
        if action == "payer_b":
            return self._apply_payer_update(
                transactions,
                payer=monthly_budget.user_b,
                username_for_message=monthly_budget.user_b.username,
            )

        return BulkActionResult(
            level="error",
            message="不正な操作です",
        )

    def _apply_payer_update(
        self,
        transactions,
        *,
        payer,
        username_for_message: str,
    ) -> BulkActionResult:
        """支払者を一括更新し、Ajax 用の更新明細リストを返す。"""
        tx_ids = list(transactions.values_list("id", flat=True))
        count = len(tx_ids)
        transactions.update(payer=payer)
        updated_transactions = [
            {
                "id": tx.id,
                "payer_username": tx.payer.username if tx.payer else None,
            }
            for tx in Transaction.objects.filter(id__in=tx_ids).select_related("payer")
        ]
        return BulkActionResult(
            level="success",
            message=f"{count}件の支払者を{username_for_message}に設定しました",
            updated_count=count,
            updated_transactions=updated_transactions,
        )
