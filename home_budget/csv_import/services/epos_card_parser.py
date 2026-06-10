from common.text import parse_amount, parse_date

from ..ports import ParsedTransaction

AMOUNT_COLUMN = "ご利用金額（キャッシングでは元金になります）"
REMARKS_COLUMN = "備考"


def should_skip_row(row: dict) -> bool:
    """除外すべき行かどうかを判定する"""
    date_col = row.get("ご利用年月日", "").strip()
    if not date_col:
        return True

    type_col = row.get("種別（ショッピング、キャッシング、その他）", "").strip()
    if type_col.startswith("（") or type_col.startswith("(") or type_col.startswith("※"):
        return True

    amount = parse_amount(row.get(AMOUNT_COLUMN, ""))
    if amount is not None and amount < 0:
        return True

    remarks = row.get(REMARKS_COLUMN, "").strip()
    if "取消" in remarks:
        return True

    return False


class EposCardParser:
    """エポスカード形式CSVパーサー"""

    REQUIRED_COLUMNS = [
        "ご利用年月日",
        "ご利用場所",
        "ご利用金額（キャッシングでは元金になります）",
    ]

    def __init__(self, row: dict):
        self.row = row

    def parse(self) -> ParsedTransaction | None:
        """行をパースしてトランザクションを返す"""
        date_value = parse_date(self.row.get("ご利用年月日", ""))
        if date_value is None:
            return None

        description = self.row.get("ご利用場所", "").strip()
        if not description:
            return None

        amount = parse_amount(self.row.get(AMOUNT_COLUMN, ""))
        if amount is None or amount <= 0:
            return None

        memo_parts = []
        usage_content = self.row.get("ご利用内容", "").strip()
        if usage_content and usage_content != "－":
            memo_parts.append(usage_content)

        remarks = self.row.get(REMARKS_COLUMN, "").strip()
        if remarks:
            memo_parts.append(remarks)

        memo = " / ".join(memo_parts)

        return ParsedTransaction(
            date=date_value,
            description=description,
            amount=amount,
            memo=memo,
        )
