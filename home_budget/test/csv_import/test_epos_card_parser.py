"""EposCardParser / should_skip_row のテスト。"""
import io

from csv_import.services.csv_import_service import CSVImportService
from csv_import.services.epos_card_parser import (
    AMOUNT_COLUMN,
    EposCardParser,
    should_skip_row,
)


def _epos_row(**overrides) -> dict:
    row = {
        "種別（ショッピング、キャッシング、その他）": "ショッピング",
        "ご利用年月日": "2026年5月7日",
        "ご利用場所": "スマ－トイ－エツクス　ジエイア－ルトウカイ",
        "ご利用内容": "－",
        AMOUNT_COLUMN: "8570",
        "支払区分": "1回払い",
        "お支払開始月": "2026年7月",
        "備考": "",
    }
    row.update(overrides)
    return row


class Test_should_skip_row:
    """should_skip_row の検証。"""

    def test_通常行はスキップしない(self):
        assert should_skip_row(_epos_row()) is False

    def test_マイナス金額の取消行はスキップする(self):
        row = _epos_row(**{AMOUNT_COLUMN: "-8570", "備考": "お取消日 2026年5月10日"})

        assert should_skip_row(row) is True

    def test_備考に取消を含む行はスキップする(self):
        row = _epos_row(**{"備考": "お取消日 2026年5月10日"})

        assert should_skip_row(row) is True

    def test_日付が空の行はスキップする(self):
        assert should_skip_row(_epos_row(**{"ご利用年月日": ""})) is True

    def test_注釈行はスキップする(self):
        row = _epos_row(
            **{
                "種別（ショッピング、キャッシング、その他）": "※１　注釈",
                "ご利用年月日": "",
            }
        )

        assert should_skip_row(row) is True


class Test_EposCardParser:
    """EposCardParser の検証。"""

    def test_通常行をパースできる(self):
        parsed = EposCardParser(_epos_row()).parse()

        assert parsed is not None
        assert parsed.amount == 8570
        assert parsed.description == "スマ－トイ－エツクス　ジエイア－ルトウカイ"


class Test_CSVImportService取消行:
    """CSV 取り込み時の取消行スキップの検証。"""

    def test_取消行はエラーではなくスキップされる(self):
        header = (
            "種別（ショッピング、キャッシング、その他）,ご利用年月日,ご利用場所,"
            "ご利用内容,ご利用金額（キャッシングでは元金になります）,支払区分,"
            "お支払開始月,備考\n"
        )
        title = "月別ご利用明細,,,,,,,\n"
        normal = (
            "ショッピング,2026年5月7日,店舗A,－,1000,1回払い,2026年7月,\n"
        )
        cancellation = (
            "ショッピング,2026年5月7日,店舗A,－,-8570,1回払い,2026年7月,"
            "お取消日 2026年5月10日\n"
        )
        csv_bytes = (title + header + normal + cancellation).encode("utf-8")

        class FakeRepo:
            def generate_hash(self, date, description, amount):
                return f"{date}|{description}|{amount}"

            def exists_by_hash(self, import_hash):
                return False

            def create(self, parsed, import_hash):
                pass

        result = CSVImportService(FakeRepo()).import_csv(io.BytesIO(csv_bytes))

        assert result.success_count == 1
        assert result.skip_count == 1
        assert result.error_count == 0
        assert result.errors == []
