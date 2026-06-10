"""
text モジュール

テキスト処理に関するユーティリティを提供する。

含まれる機能:
- encoding: 文字コード判定
- parsing: 日付・金額パース
"""
from .encoding import detect_encoding
from .parsing import parse_date, parse_amount

__all__ = [
    "detect_encoding",
    "parse_date",
    "parse_amount",
]

