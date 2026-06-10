"""
common アプリ

プロジェクト全体で共有するユーティリティなどを提供する。

このアプリは他のアプリから依存されるが、他のアプリには依存しない。
（安定依存の原則に従い、最も安定したパッケージとして設計）

ディレクトリ構造:
    common/
    ├── env.py          # 環境変数の解釈
    └── text.py         # 文字コード判定・日付・金額パース

使用例:
    from common.text import detect_encoding, parse_date, parse_amount
    from common.env import env_bool, env_str
"""

from .env import env_bool, env_str
from .text import detect_encoding, parse_amount, parse_date

__all__ = [
    "detect_encoding",
    "parse_date",
    "parse_amount",
    "env_bool",
    "env_str",
]
