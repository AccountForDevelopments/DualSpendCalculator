from ..forms import CSVUploadForm


def build_csv_upload_section_context() -> dict[str, object]:
    """月次詳細画面の CSV アップロードセクション用 context を組み立てる。

    現状 csv_form は MonthlyBudget に依存しない。将来フォームに月次依存の
    初期値が必要になった場合は monthly_budget 引数を追加する。
    """
    return {"csv_form": CSVUploadForm()}
