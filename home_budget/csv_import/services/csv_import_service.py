"""
CSV取り込みサービス

依存性逆転の原則（DIP）に基づき、具体的なモデルに依存しない設計。
TransactionRepository を通じてストレージにアクセスする。
"""
import csv
import io
from typing import BinaryIO

from common.text import detect_encoding

from ..ports import TransactionRepository
from .epos_card_parser import EposCardParser, should_skip_row
from .import_result import ImportResult


class CSVImportService:
    """CSV取り込みサービス

    TransactionRepository を注入することで、任意のストレージに対応可能。

    使用例（HomeBudgetApp）:
        from csv_import.adapters import DjangoTransactionRepository

        repository = DjangoTransactionRepository(monthly_budget)
        service = CSVImportService(repository)
        result = service.import_csv(file)
    """

    def __init__(self, repository: TransactionRepository):
        """
        サービスを初期化する

        Args:
            repository: トランザクションリポジトリ（Protocol を満たす任意の実装）
        """
        self.repository = repository

    def import_csv(self, file: BinaryIO) -> ImportResult:
        """
        CSVファイルを取り込む

        Args:
            file: アップロードされたファイルオブジェクト

        Returns:
            ImportResult: 取り込み結果
        """
        result = ImportResult()

        file_content = file.read()

        if not file_content:
            result.errors.append("ファイルが空です")
            return result

        try:
            encoding = detect_encoding(file_content)
        except ValueError as e:
            result.errors.append(str(e))
            return result

        try:
            text_content = file_content.decode(encoding)
        except UnicodeDecodeError as e:
            result.errors.append(f"ファイルのデコードに失敗しました: {e}")
            return result

        lines = text_content.splitlines()

        if len(lines) < 2:
            result.errors.append("ヘッダー行が見つかりません")
            return result

        reader = csv.DictReader(io.StringIO("\n".join(lines[1:])))

        if reader.fieldnames is None:
            result.errors.append("CSVのヘッダーを読み取れませんでした")
            return result

        missing_columns = [
            col for col in EposCardParser.REQUIRED_COLUMNS if col not in reader.fieldnames
        ]

        if missing_columns:
            result.errors.append(f"必須列（{'/'.join(missing_columns)}）が見つかりません")
            return result

        for row_num, row in enumerate(reader, start=3):
            if should_skip_row(row):
                result.skip_count += 1
                continue

            parser = EposCardParser(row)
            parsed = parser.parse()

            if parsed is None:
                result.error_count += 1
                result.errors.append(f"行{row_num}: パースに失敗しました")
                continue

            import_hash = self.repository.generate_hash(
                parsed.date,
                parsed.description,
                parsed.amount,
            )

            if self.repository.exists_by_hash(import_hash):
                result.duplicate_count += 1
                continue

            try:
                self.repository.create(parsed, import_hash)
                result.success_count += 1
            except Exception as e:
                result.error_count += 1
                result.errors.append(f"行{row_num}: 保存に失敗しました - {e}")

        return result
