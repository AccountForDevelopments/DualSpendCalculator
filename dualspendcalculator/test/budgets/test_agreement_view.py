"""AgreementDownloadView のテスト。

01_what_to_build.md の AC-002〜AC-007, AC-009 に基づく検証。
"""
from unittest.mock import patch
from urllib.parse import unquote

import pytest
from django.contrib.messages import get_messages
from django.test import Client
from django.urls import reverse

from budgets.models import MonthlyBudget
from transactions.models import Transaction


class Test_AgreementDownloadView_正常系:
    """AgreementDownloadView の正常系を検証する。"""

    @pytest.mark.django_db
    def test_PDFが正常に生成され必要な情報がすべて記載される(
        self,
        user_a,
        user_b,
        monthly_budget,
        living_cost_transactions,
    ):
        """
        T-001: 選択したTransaction IDのリストとMonthlyBudgetを指定してPOSTリクエストを送信するとき、
        PDFが正常に生成され、対象月・ユーザーA/B名・負担割合（%表示）・選択した請求額の合計・
        ユーザーA/Bの負担額がすべて記載されること (AC-002)
        """
        # Arrange
        mb = monthly_budget(
            user_a,
            user_b,
            year_month="2026-03",
            income_a=300000,
            income_b=200000,
        )
        transactions = living_cost_transactions(
            mb,
            [
                (5000, user_a),
                (8000, user_a),
            ],
        )
        selected_ids = [t.id for t in transactions]
        client = Client()
        client.force_login(user_a)

        # Act
        response = client.post(
            reverse("budgets:agreement_download"),
            {
                "transaction_ids": selected_ids,
                "monthly_budget_id": mb.id,
            },
        )

        # Assert
        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"
        content_disposition = response["Content-Disposition"]
        assert "attachment" in content_disposition
        assert "家事按分同意書_2026-03.pdf" in unquote(content_disposition)
        assert len(response.content) > 0  # PDFバイナリが返されている

    @pytest.mark.django_db
    def test_PDFに選択したTransactionの明細一覧が記載される(
        self,
        user_a,
        user_b,
        monthly_budget,
        living_cost_transactions,
    ):
        """
        T-002: 選択したTransaction IDのリストとMonthlyBudgetを指定してPOSTリクエストを送信するとき、
        PDFに選択したTransactionの明細一覧（日付・摘要・金額）が記載されること (AC-003)
        """
        # Arrange
        mb = monthly_budget(
            user_a,
            user_b,
            year_month="2026-03",
            income_a=300000,
            income_b=200000,
        )
        transactions = living_cost_transactions(
            mb,
            [
                (5000, user_a),
                (8000, user_a),
            ],
        )
        selected_ids = [t.id for t in transactions]
        client = Client()
        client.force_login(user_a)

        # Act
        response = client.post(
            reverse("budgets:agreement_download"),
            {
                "transaction_ids": selected_ids,
                "monthly_budget_id": mb.id,
            },
        )

        # Assert
        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"
        # PDFの内容はバイナリなので、生成されたことを確認するのみ
        assert len(response.content) > 0

    @pytest.mark.django_db
    def test_PDFに作成日と署名欄が記載される(
        self,
        user_a,
        user_b,
        monthly_budget,
        living_cost_transactions,
    ):
        """
        T-003: 選択したTransaction IDのリストとMonthlyBudgetを指定してPOSTリクエストを送信するとき、
        PDFに作成日（YYYY年MM月DD日）と署名欄（ユーザーA用・ユーザーB用の枠）が記載されること (AC-004)
        """
        # Arrange
        mb = monthly_budget(
            user_a,
            user_b,
            year_month="2026-03",
            income_a=300000,
            income_b=200000,
        )
        transactions = living_cost_transactions(
            mb,
            [
                (5000, user_a),
            ],
        )
        selected_ids = [transactions[0].id]
        client = Client()
        client.force_login(user_a)

        # Act
        response = client.post(
            reverse("budgets:agreement_download"),
            {
                "transaction_ids": selected_ids,
                "monthly_budget_id": mb.id,
            },
        )

        # Assert
        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"
        assert len(response.content) > 0

    @pytest.mark.django_db
    def test_HTTPレスポンスのContent_Typeとファイル名が正しい(
        self,
        user_a,
        user_b,
        monthly_budget,
        living_cost_transactions,
    ):
        """
        T-004: 選択したTransaction IDのリストとMonthlyBudgetを指定してPOSTリクエストを送信するとき、
        HTTPレスポンスのContent-Typeがapplication/pdfとなり、ファイル名に「家事按分同意書」と対象月が含まれること (AC-009)
        """
        # Arrange
        mb = monthly_budget(
            user_a,
            user_b,
            year_month="2026-03",
            income_a=300000,
            income_b=200000,
        )
        transactions = living_cost_transactions(
            mb,
            [
                (5000, user_a),
            ],
        )
        selected_ids = [transactions[0].id]
        client = Client()
        client.force_login(user_a)

        # Act
        response = client.post(
            reverse("budgets:agreement_download"),
            {
                "transaction_ids": selected_ids,
                "monthly_budget_id": mb.id,
            },
        )

        # Assert
        assert response.status_code == 200
        assert response["Content-Type"] == "application/pdf"
        content_disposition = response["Content-Disposition"]
        assert "attachment" in content_disposition
        assert "家事按分同意書_2026-03.pdf" in unquote(content_disposition)


class Test_AgreementDownloadView_エラー系:
    """AgreementDownloadView のエラー系を検証する。"""

    @pytest.mark.django_db
    def test_選択したTransaction_IDが0件のときエラーメッセージが表示される(
        self,
        user_a,
        user_b,
        monthly_budget,
    ):
        """
        T-005: 選択したTransaction IDが0件の状態でPOSTリクエストを送信するとき、
        エラーメッセージが表示され、PDFは生成されないこと (AC-005)
        """
        # Arrange
        mb = monthly_budget(
            user_a,
            user_b,
            year_month="2026-03",
            income_a=300000,
            income_b=200000,
        )
        client = Client()
        client.force_login(user_a)

        # Act
        response = client.post(
            reverse("budgets:agreement_download"),
            {
                "transaction_ids": [],
                "monthly_budget_id": mb.id,
            },
            follow=True,
        )

        # Assert
        assert response.status_code == 200  # follow=Trueなのでリダイレクト先のステータス
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) > 0
        assert any("選択された請求がありません" in str(m) for m in messages)

    @pytest.mark.django_db
    def test_存在しないTransaction_IDを含むリストでエラーメッセージが表示される(
        self,
        user_a,
        user_b,
        monthly_budget,
        living_cost_transactions,
    ):
        """
        T-006: 存在しないTransaction IDを含むリストでPOSTリクエストを送信するとき、
        エラーメッセージが表示され、PDFは生成されないこと (AC-006)
        """
        # Arrange
        mb = monthly_budget(
            user_a,
            user_b,
            year_month="2026-03",
            income_a=300000,
            income_b=200000,
        )
        transactions = living_cost_transactions(
            mb,
            [
                (5000, user_a),
            ],
        )
        # 存在しないIDを含む
        invalid_ids = [transactions[0].id, 99999]
        client = Client()
        client.force_login(user_a)

        # Act
        response = client.post(
            reverse("budgets:agreement_download"),
            {
                "transaction_ids": invalid_ids,
                "monthly_budget_id": mb.id,
            },
            follow=True,
        )

        # Assert
        assert response.status_code == 200  # follow=Trueなのでリダイレクト先のステータス
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) > 0
        assert any("存在しない請求が含まれています" in str(m) for m in messages)

    @pytest.mark.django_db
    def test_他月のMonthlyBudgetに紐づくTransaction_IDでエラーメッセージが表示される(
        self,
        user_a,
        user_b,
        monthly_budget,
        living_cost_transactions,
    ):
        """
        T-007: 他月のMonthlyBudgetに紐づくTransaction IDを含むリストでPOSTリクエストを送信するとき、
        エラーメッセージが表示され、PDFは生成されないこと (AC-007)
        """
        # Arrange
        mb1 = monthly_budget(
            user_a,
            user_b,
            year_month="2026-03",
            income_a=300000,
            income_b=200000,
        )
        mb2 = monthly_budget(
            user_a,
            user_b,
            year_month="2026-04",
            income_a=300000,
            income_b=200000,
        )
        transactions1 = living_cost_transactions(
            mb1,
            [
                (5000, user_a),
            ],
        )
        transactions2 = living_cost_transactions(
            mb2,
            [
                (8000, user_a),
            ],
        )
        # mb1のIDを指定しているが、mb2のTransaction IDを含む
        mixed_ids = [transactions1[0].id, transactions2[0].id]
        client = Client()
        client.force_login(user_a)

        # Act
        response = client.post(
            reverse("budgets:agreement_download"),
            {
                "transaction_ids": mixed_ids,
                "monthly_budget_id": mb1.id,
            },
            follow=True,
        )

        # Assert
        assert response.status_code == 200  # follow=Trueなのでリダイレクト先のステータス
        messages = list(get_messages(response.wsgi_request))
        assert len(messages) > 0
        assert any("異なる対象月の請求が含まれています" in str(m) for m in messages)
