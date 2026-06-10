"""
精算サービス

budgets アプリのビジネスロジックを提供する。
"""
from .agreement_request import AgreementRequestResult, AgreementRequestValidator
from .settlement import SettlementCalculator, SettlementResult

__all__ = [
    "SettlementCalculator",
    "SettlementResult",
    "AgreementCalculator",
    "AgreementResult",
    "generate_agreement_pdf",
    "AgreementRequestResult",
    "AgreementRequestValidator",
]

_LAZY_AGREEMENT_EXPORTS = frozenset(
    {"AgreementCalculator", "AgreementResult", "generate_agreement_pdf"}
)


def __getattr__(name: str):
    if name in _LAZY_AGREEMENT_EXPORTS:
        from . import agreement

        return getattr(agreement, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
