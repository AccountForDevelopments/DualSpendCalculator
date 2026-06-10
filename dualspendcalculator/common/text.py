"""
テキスト処理

文字コード判定、日付・金額パースなどのユーティリティを提供する。
"""
import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation


def detect_encoding(file_content: bytes) -> str:
    """
    ファイルの文字コードを自動判定する

    判定順序:
    1. UTF-8 BOMの有無を確認
    2. UTF-8としてデコードを試行
    3. CP932（Shift-JIS）としてデコードを試行

    Args:
        file_content: ファイルのバイナリ内容

    Returns:
        検出された文字コード名（"utf-8-sig", "utf-8", "cp932"）

    Raises:
        ValueError: 文字コードを認識できない場合

    使用例:
        >>> with open("file.csv", "rb") as f:
        ...     encoding = detect_encoding(f.read())
        >>> text = content.decode(encoding)
    """
    if file_content.startswith(b"\xef\xbb\xbf"):
        return "utf-8-sig"

    try:
        file_content.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        pass

    try:
        file_content.decode("cp932")
        return "cp932"
    except UnicodeDecodeError:
        pass

    raise ValueError("ファイルの文字コードを認識できません。CP932またはUTF-8で保存してください")


def parse_date(date_str: str) -> date | None:
    """
    日付文字列をパースする

    対応フォーマット:
    - YYYY年MM月DD日（日本語形式）
    - YYYY-MM-DD（ISO形式）
    - YYYY/MM/DD（スラッシュ区切り）

    Args:
        date_str: 日付文字列

    Returns:
        パース成功時: date オブジェクト
        パース失敗時: None

    使用例:
        >>> parse_date("2025年1月15日")
        datetime.date(2025, 1, 15)
        >>> parse_date("2025-01-15")
        datetime.date(2025, 1, 15)
        >>> parse_date("invalid")
        None
    """
    if not date_str or not date_str.strip():
        return None

    date_str = date_str.strip()

    match = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_str)
    if match:
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            return None

    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        pass

    try:
        return datetime.strptime(date_str, "%Y/%m/%d").date()
    except ValueError:
        pass

    return None


def parse_amount(amount_str: str) -> int | None:
    """
    金額文字列をパースする

    対応パターン:
    - 整数: 1234
    - カンマ区切り: 1,234
    - 引用符付き: "1,234"
    - 小数: 1234.56（整数に丸め）

    Args:
        amount_str: 金額文字列

    Returns:
        パース成功時: 整数の金額
        パース失敗時: None

    使用例:
        >>> parse_amount("1,234")
        1234
        >>> parse_amount('"5,678"')
        5678
        >>> parse_amount("invalid")
        None
    """
    if not amount_str:
        return None

    amount_str = amount_str.strip().strip('"').strip("'")
    amount_str = amount_str.replace(",", "")

    if not amount_str:
        return None

    try:
        return int(Decimal(amount_str))
    except (ValueError, InvalidOperation):
        return None
