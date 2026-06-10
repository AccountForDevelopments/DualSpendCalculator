"""build_csv_upload_section_context のテスト。"""
from csv_import.forms import CSVUploadForm
from csv_import.presenters import build_csv_upload_section_context


class Test_build_csv_upload_section_context:
    """CSV アップロードセクション Presenter の検証。"""

    def test_csv_formキーがCSVUploadFormインスタンスである(self):
        context = build_csv_upload_section_context()

        assert "csv_form" in context
        assert isinstance(context["csv_form"], CSVUploadForm)
