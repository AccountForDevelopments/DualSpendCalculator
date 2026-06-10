"""
ポート定義（csv_import）

依存性逆転の原則（DIP）に基づき、具体的なモデルへの依存を抽象化する。
このモジュールは「何ができるべきか」を定義し、「どう実現するか」は adapters.py に委ねる。

設計原則:
- DIP: 上位モジュールは下位モジュールに依存しない。両者は抽象に依存する。
- ポートとアダプター: 外部連携のインターフェースを分離
"""
from abc import ABC, abstractmethod
from datetime import date
from typing import Protocol, runtime_checkable

# libs/csv_parser から汎用データクラスをインポート
# 注意: 本番では libs をインストールするか、sys.path に追加する必要がある
try:
    from csv_parser import ParsedTransaction
except ImportError:
    # フォールバック: ローカル定義
    from dataclasses import dataclass
    
    @dataclass
    class ParsedTransaction:
        """パース済みトランザクション"""
        date: date
        description: str
        amount: int
        memo: str = ""


@runtime_checkable
class TransactionRepository(Protocol):
    """トランザクションリポジトリのインターフェース
    
    このProtocolを実装することで、任意のストレージ（Django ORM、SQLAlchemy、
    ファイルなど）に対応可能。
    
    使用例:
        class DjangoTransactionRepository:
            def exists_by_hash(self, import_hash: str) -> bool:
                return Transaction.objects.filter(import_hash=import_hash).exists()
            # ...他のメソッド
    """
    
    def exists_by_hash(self, import_hash: str) -> bool:
        """インポートハッシュで重複チェック
        
        Args:
            import_hash: 重複チェック用のハッシュ値
            
        Returns:
            既に存在する場合はTrue
        """
        ...
    
    def create(self, data: ParsedTransaction, import_hash: str) -> None:
        """トランザクションを作成
        
        Args:
            data: パース済みトランザクションデータ
            import_hash: インポートハッシュ
        """
        ...
    
    def generate_hash(self, date: date, description: str, amount: int) -> str:
        """インポートハッシュを生成
        
        Args:
            date: 日付
            description: 摘要
            amount: 金額
            
        Returns:
            ハッシュ文字列
        """
        ...

