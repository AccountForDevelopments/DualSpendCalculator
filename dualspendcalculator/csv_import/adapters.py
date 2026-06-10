"""
アダプター実装（csv_import）

ポートの具体的な実装を提供する。
ここでDjango ORMへの依存が発生するが、services.pyはこれに依存しない。

設計原則:
- ポートとアダプター: 外部連携の具体実装を分離
- 依存性の局所化: ORMへの依存をこのファイルに閉じ込める
"""
from datetime import date

from budgets.models import MonthlyBudget
from transactions.models import Transaction

from .ports import ParsedTransaction, TransactionRepository


class DjangoTransactionRepository:
    """Django ORMを使用したTransactionRepository実装
    
    このクラスは TransactionRepository Protocol を満たす。
    Django ORM固有の実装をカプセル化し、services.pyからは抽象として扱われる。
    
    使用例:
        repository = DjangoTransactionRepository(monthly_budget)
        importer = CSVImportService(repository)
        result = importer.import_csv(file)
    """
    
    def __init__(self, monthly_budget: MonthlyBudget):
        """
        リポジトリを初期化する
        
        Args:
            monthly_budget: 紐付ける月次予算
        """
        self.monthly_budget = monthly_budget
    
    def exists_by_hash(self, import_hash: str) -> bool:
        """インポートハッシュで重複チェック"""
        return Transaction.objects.filter(import_hash=import_hash).exists()
    
    def create(self, data: ParsedTransaction, import_hash: str) -> None:
        """トランザクションを作成"""
        Transaction.objects.create(
            monthly_budget=self.monthly_budget,
            date=data.date,
            description=data.description,
            amount=data.amount,
            memo=data.memo,
            import_hash=import_hash,
        )
    
    def generate_hash(self, date: date, description: str, amount: int) -> str:
        """インポートハッシュを生成"""
        return Transaction.generate_import_hash(date, description, amount)


# Type check: DjangoTransactionRepository は TransactionRepository を満たす
def _type_check() -> None:
    """型チェック用のヘルパー（実行時には呼ばれない）"""
    repo: TransactionRepository = DjangoTransactionRepository(None)  # type: ignore
    assert isinstance(repo, TransactionRepository)

