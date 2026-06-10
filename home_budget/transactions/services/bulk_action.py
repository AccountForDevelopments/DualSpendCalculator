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
            transactions.update(payer=monthly_budget.user_a)
            return BulkActionResult(
                level="success",
                message=f"{count}件の支払者を{monthly_budget.user_a.username}に設定しました",
                updated_count=count,
            )
        if action == "payer_b":
            transactions.update(payer=monthly_budget.user_b)
            return BulkActionResult(
                level="success",
                message=f"{count}件の支払者を{monthly_budget.user_b.username}に設定しました",
                updated_count=count,
            )

        return BulkActionResult(
            level="error",
            message="不正な操作です",
        )
