from dataclasses import dataclass, field


@dataclass
class ImportResult:
    """CSV取り込み結果"""
    success_count: int = 0
    duplicate_count: int = 0
    skip_count: int = 0
    error_count: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def total_processed(self) -> int:
        return self.success_count + self.duplicate_count + self.skip_count + self.error_count

    def get_message(self) -> str:
        """結果メッセージを生成"""
        messages = []
        if self.success_count > 0:
            messages.append(f"成功: {self.success_count}件")
        if self.duplicate_count > 0:
            messages.append(f"重複スキップ: {self.duplicate_count}件")
        if self.skip_count > 0:
            messages.append(f"除外行スキップ: {self.skip_count}件")
        if self.error_count > 0:
            messages.append(f"エラー: {self.error_count}件")
        return "、".join(messages) if messages else "取り込み対象がありませんでした"
