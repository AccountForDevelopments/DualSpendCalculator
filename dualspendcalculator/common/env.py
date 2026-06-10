"""環境変数文字列の解釈ユーティリティ（副作用なし）"""


def env_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.lower() in ("1", "true", "yes", "on")


def env_str(value: str | None, default: str) -> str:
    return default if value is None else value
